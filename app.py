import streamlit as st
import time
import yaml
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. CORE LOGIC ---
def load_challenges():
    try:
        with open("challenges.yaml", 'r') as f:
            return yaml.load(f, Loader=yaml.SafeLoader)['challenges']
    except Exception as e:
        return [{"title": "SYSTEM ERROR", "threat": False, "info": "YAML Missing", "code": "print('Check challenges.yaml')"}]

# Initialize Session States
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'panic' not in st.session_state: st.session_state.panic = False
if 'pilot_name' not in st.session_state: st.session_state.pilot_name = ""
if 'status' not in st.session_state: st.session_state.status = "active"
if 'db_updated' not in st.session_state: st.session_state.db_updated = False
if 'typing_speed' not in st.session_state: st.session_state.typing_speed = 0.08

if 'challenge_pool' not in st.session_state:
    st.session_state.challenge_pool = load_challenges()

if 'current_threat' not in st.session_state:
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)

# --- 2. THEME & CSS ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

bg_color = "#05080a"
text_color = "#00ff41"
if st.session_state.panic:
    bg_color = "#440000"
    text_color = "#ff4b4b"
elif st.session_state.status == "success":
    bg_color = "#0a1f0a"
elif st.session_state.status == "fail":
    bg_color = "#2b0505"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: 0.8s ease-in-out; }}
    h1, h2, h3, p, .stMetric {{ color: {text_color} !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ 
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important; 
        color: white !important; width: 100%; height: 6em; font-weight: bold; 
        border: 3px solid #ff4b4b !important; box-shadow: 0 0 20px #ff0000;
        font-size: 22px !important;
    }}
    .certificate-box {{ border: 5px double #00ff41; padding: 40px; background-color: #0a140a; text-align: center; border-radius: 15px; box-shadow: 0 0 40px #00ff41; margin: 20px auto; }}
    .force-text {{ font-style: italic; color: #fff; text-shadow: 0 0 10px #00ff41; font-size: 1.5em; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. UPDATED CALLBACKS (State Cleaning) ---
def handle_kill_switch():
    st.session_state.halted = True
    st.session_state.panic = False
    if st.session_state.current_threat["threat"]:
        st.session_state.score += 100
        st.session_state.status = "success"
    else:
        st.session_state.score -= 50
        st.session_state.status = "fail"

def next_sector_reset():
    # EXPLICITLY CLEAR OLD DATA
    st.session_state.lvl += 1
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)
    st.session_state.halted = False
    st.session_state.panic = False
    st.session_state.status = "active"

# --- 4. GAME INTERFACE ---
st.markdown('<div style="text-align:center; letter-spacing: 5px; color:#00ff41; font-weight:bold;">🛡️ ENDOR LABS | RSA 2026</div>', unsafe_allow_html=True)

if not st.session_state.pilot_name:
    st.title("📟 IMPERIAL COMMAND: LOGIN")
    with st.form("login"):
        name = st.text_input("Enter Pilot Callsign:")
        if st.form_submit_button("INITIATE MISSION"):
            if name: 
                st.session_state.pilot_name = name
                st.rerun()

elif st.session_state.lvl <= 5:
    st.title("📟 IMPERIAL COMMAND TERMINAL")
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.metric("SECTOR", f"{st.session_state.lvl}/5")
        st.metric("REPUTATION", st.session_state.score)
        st.divider()
        # THE BUTTON IS NOW ALWAYS HERE (Not waiting for loop)
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch, key="ks_btn")
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector_reset, key="next_btn")

    with col1:
        st.markdown(f"### {st.session_state.current_threat['title']}")
        code_box = st.empty()
        status_box = st.empty() # Placeholder for results to prevent ghosting
        
        if not st.session_state.halted and not st.session_state.panic:
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            for line in lines:
                if st.session_state.halted: break
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
            # INTERFACE AFTER BUTTON CLICK OR PANIC
            code_box.code(st.session_state.current_threat["code"], language="python")
            
            if st.session_state.status == "success":
                status_box.success(f"🎯 NEUTRALIZED: {st.session_state.current_threat['info']}")
                st.markdown('<p class="force-text">The Force is strong with this pilot!</p>', unsafe_allow_html=True)
            elif st.session_state.status == "fail":
                status_box.error("❌ MISFIRE! You disabled a safe system.")
            elif st.session_state.panic:
                status_box.warning("⚠️ DEPLOYMENT FINISHED. Did you spot the threat?")

else:
    # --- 5. CERTIFICATE (Perserved) ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    if not st.session_state.db_updated:
        try:
            df = conn.read(worksheet="Sheet1", ttl=0)
            new_row = pd.DataFrame([{"Pilot": st.session_state.pilot_name, "Score": st.session_state.score}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.session_state.db_updated = True
        except: pass

    st.balloons()
    rank = "JEDI MASTER" if st.session_state.score >= 400 else "REBEL AGENT"
    st.markdown(f"""
        <div class="certificate-box">
            <h1>CERTIFICATE OF MERIT</h1>
            <h2>{st.session_state.pilot_name.upper()}</h2>
            <p class="force-text">"The Force is strong with this pilot."</p>
            <hr style="border: 1px solid #00ff41;">
            <h3>RANK: {rank}</h3>
            <h3>FINAL REPUTATION: {st.session_state.score}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🏆 TOP ACE PILOTS")
    try:
        leaderboard = conn.read(worksheet="Sheet1", ttl=0)
        st.table(leaderboard.sort_values(by="Score", ascending=False).head(5))
    except: st.info("Leaderboard syncing...")

    if st.button("REBOOT FOR NEXT PILOT"):
        st.session_state.clear()
        st.rerun()

# --- 6. ADMIN ---
with st.expander("🛠️ System Admin"):
    admin_pass = st.text_input("Admin Override:", type="password")
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "endor2026"):
        new_speed = st.slider("Adjust Typing Speed:", 0.01, 0.20, st.session_state.typing_speed)
        if st.button("Save Speed"):
            st.session_state.typing_speed = new_speed
        if st.button("🚨 RESET LEADERBOARD"):
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(worksheet="Sheet1", data=pd.DataFrame(columns=["Pilot", "Score"]))
