import streamlit as st
import time
import yaml
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_lottie import st_lottie
import requests

# --- 1. CORE LOGIC & DATA ---
def load_lottieurl(url: str):
    """Safe loader for Lottie animations to prevent app crashes"""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Reliable Star Wars Lottie URLs
# BB-8 (Success) and Darth Vader/Stormtrooper themed (Fail)
lottie_success = load_lottieurl("https://assets8.lottiefiles.com/private_files/lf30_ig9hzpnd.json") 
lottie_fail = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_6sxyjyjj.json")

def load_challenges():
    try:
        with open("challenges.yaml", 'r') as f:
            return yaml.load(f, Loader=yaml.SafeLoader)['challenges']
    except:
        return [{"title": "CORE REPL", "threat": True, "bad_line": 0, "info": "YAML Missing", "code": "import os\nos.system('malicious')"}]

if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'panic' not in st.session_state: st.session_state.panic = False
if 'pilot_name' not in st.session_state: st.session_state.pilot_name = ""
if 'status' not in st.session_state: st.session_state.status = "active"
if 'db_updated' not in st.session_state: st.session_state.db_updated = False
if 'typing_speed' not in st.session_state: st.session_state.typing_speed = 0.08
if 'current_line_idx' not in st.session_state: st.session_state.current_line_idx = 0

if 'challenge_pool' not in st.session_state:
    st.session_state.challenge_pool = load_challenges()

if 'current_threat' not in st.session_state:
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)

# --- 2. THEME & CSS ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

bg_color = "#05080a"
sector_text_color = "#00ff41"

threat_is_live = (st.session_state.current_threat.get("threat") and 
                  st.session_state.current_line_idx >= st.session_state.current_threat.get("bad_line", 0))

if st.session_state.panic: bg_color = "#440000"
elif st.session_state.status == "success": bg_color = "#0a1f0a"
elif st.session_state.status == "fail": bg_color = "#2b0505"

if threat_is_live and not st.session_state.halted:
    sector_text_color = "#ff0000; text-shadow: 0 0 15px #ff0000;"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: 0.5s; }}
    h1, h2, h3, p, .stMetric {{ color: #00ff41 !important; font-family: 'Courier New', monospace; }}
    .sector-header {{ color: {sector_text_color}; font-size: 2rem; font-weight: bold; margin-bottom: 10px; }}
    .stButton>button {{ 
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important; 
        color: white !important; width: 100%; height: 6em; font-weight: bold; 
        border: 3px solid #ff4b4b !important; box-shadow: 0 0 20px #ff0000;
        font-size: 22px !important;
    }}
    .certificate-box {{ border: 5px double #00ff41; padding: 40px; background-color: #0a140a; text-align: center; border-radius: 15px; box-shadow: 0 0 40px #00ff41; margin: 20px auto; }}
    .imperial-box {{ border: 5px solid #ff0000; padding: 40px; background-color: #1a0000; text-align: center; border-radius: 5px; box-shadow: 0 0 40px #ff0000; margin: 20px auto; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CALLBACKS ---
def handle_kill_switch():
    st.session_state.halted = True
    challenge = st.session_state.current_threat
    if threat_is_live:
        st.session_state.score += 100
        st.session_state.status = "success"
    else:
        st.session_state.score -= 50
        st.session_state.status = "fail"
        st.session_state.info_override = "FALSE ALARM! System was clean."

def next_sector_reset():
    st.session_state.lvl += 1
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)
    st.session_state.halted = False
    st.session_state.panic = False
    st.session_state.status = "active"
    st.session_state.current_line_idx = 0
    if 'info_override' in st.session_state: del st.session_state.info_override

# --- 4. GAME INTERFACE ---
st.markdown('<div style="text-align:center; color:#00ff41; font-weight:bold; letter-spacing:3px;">🛡️ ENDOR LABS | RSA 2026</div>', unsafe_allow_html=True)

if not st.session_state.pilot_name:
    st.title("📟 LOGIN: PILOT CALLSIGN")
    with st.form("login"):
        name = st.text_input("Enter Callsign:")
        if st.form_submit_button("INITIATE"):
            if name: st.session_state.pilot_name = name; st.rerun()

elif st.session_state.lvl <= 5:
    col1, col2 = st.columns([3, 1])
    with col2:
        st.metric("SCORE", st.session_state.score)
        st.metric("SECTOR", f"{st.session_state.lvl}/5")
        st.divider()
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector_reset)

    with col1:
        # CLEAN SECTOR HEADER - Fixed "Sector: Sector:" issue
        clean_title = st.session_state.current_threat.get('title', 'Unknown Sector').replace("SECTOR:", "").strip()
        st.markdown(f'<div class="sector-header">📡 SECTOR: {clean_title}</div>', unsafe_allow_html=True)
        
        timer_bar = st.empty()
        code_box = st.empty()
        
        if not st.session_state.halted and not st.session_state.panic:
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            total_lines = len(lines)
            
            for idx, line in enumerate(lines):
                if st.session_state.halted: break
                st.session_state.current_line_idx = idx 
                
                timer_bar.progress((idx + 1) / total_lines, text=f"SCANNING: Line {idx+1}/{total_lines}")
                
                # Dynamic re-run to trigger the Red Glowing Title if we hit the bad line
                if st.session_state.current_threat.get("threat") and idx == st.session_state.current_threat.get("bad_line"):
                    st.rerun()

                for char in line:
                    if st.session_state.halted: break
                    full_text += char
                    code_box.code(full_text + "█", language="python")
                    time.sleep(st.session_state.typing_speed)
                full_text += "\n"
                time.sleep(st.session_state.typing_speed * 2)
            
            if not st.session_state.halted:
                st.session_state.panic = True
                st.rerun()
        else:
            timer_bar.empty()
            code_box.code(st.session_state.current_threat["code"], language="python")
            if st.session_state.status == "success":
                st.success(st.session_state.current_threat["info"])
            else:
                msg = st.session_state.get('info_override', "SYSTEM COMPROMISED!")
                st.error(msg)

else:
    # --- 5. FINALE ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    if not st.session_state.db_updated:
        try:
            df = conn.read(worksheet="Sheet1", ttl=0)
            new_row = pd.DataFrame([{"Pilot": st.session_state.pilot_name, "Score": st.session_state.score}])
            conn.update(worksheet="Sheet1", data=pd.concat([df, new_row], ignore_index=True))
            st.session_state.db_updated = True
        except: pass

    # Score < 100 is Imperial Defeat
    if st.session_state.score < 100:
        if lottie_fail: st_lottie(lottie_fail, height=300, key="vader_final")
        else: st.image("https://media.giphy.com/media/106H6aMvHlSk5G/giphy.gif") # Fallback
        
        st.markdown(f'<div class="imperial-box"><h1>IMPERIAL OCCUPATION</h1><h2>{st.session_state.pilot_name.upper()}</h2><p>"You have failed me for the last time."</p><h3 style="color:white;">FINAL SCORE: {st.session_state.score}</h3></div>', unsafe_allow_html=True)
    else:
        if lottie_success: st_lottie(lottie_success, height=300, key="bb8_final")
        else: st.image("https://media.giphy.com/media/8hMD9YakVza3452Spu/giphy.gif") # Fallback
        
        st.markdown(f'<div class="certificate-box"><h1>REPUBLIC COMMENDATION</h1><h2>{st.session_state.pilot_name.upper()}</h2><p>"The Force is strong with you."</p><h3 style="color:white;">FINAL SCORE: {st.session_state.score}</h3></div>', unsafe_allow_html=True)
    
    st.markdown("### 🏆 GALACTIC TOP ACE PILOTS")
    try:
        lb_df = conn.read(worksheet="Sheet1", ttl=0)
        lb_df = lb_df.dropna(subset=['Pilot', 'Score'])
        lb_df['Score'] = pd.to_numeric(lb_df['Score'], errors='coerce')
        st.table(lb_df.sort_values(by="Score", ascending=False).head(5))
    except: st.error("Comms Jammed.")

    if st.button("REBOOT FOR NEXT PILOT"):
        st.session_state.clear()
        st.rerun()

# --- 6. SYSTEM ADMIN ---
st.divider()
with st.expander("🛠️ System Admin"):
    admin_pass = st.text_input("Admin Override:", type="password")
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "endor2026"):
        st.success("Authenticated")
        new_speed = st.slider("Adjust Typing Speed:", 0.01, 0.20, st.session_state.typing_speed)
        if st.button("Save Speed Settings"):
            st.session_state.typing_speed = new_speed
            st.rerun() 
        if st.button("🚨 RESET LEADERBOARD"):
            try:
                conn.update(worksheet="Sheet1", data=pd.DataFrame(columns=["Pilot", "Score"]))
                st.rerun()
            except: st.error("Reset Failed.")
