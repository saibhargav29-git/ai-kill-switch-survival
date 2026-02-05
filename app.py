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
    except:
        return [{"title": "SYSTEM ERROR", "threat": True, "bad_line": 0, "info": "YAML Missing", "code": "import os\nos.system('malicious')"}]

# Initialize Session States
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

# Determine background color based on game state
bg_color = "#05080a"
if st.session_state.panic: bg_color = "#440000"
elif st.session_state.status == "success": bg_color = "#0a1f0a"
elif st.session_state.status == "fail": bg_color = "#2b0505"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: 0.5s; }}
    h1, h2, h3, p, .stMetric {{ color: #00ff41 !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ 
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important; 
        color: white !important; width: 100%; height: 6em; font-weight: bold; 
        border: 3px solid #ff4b4b !important; box-shadow: 0 0 20px #ff0000;
        font-size: 22px !important;
    }}
    .certificate-box {{ border: 5px double #00ff41; padding: 40px; background-color: #0a140a; text-align: center; border-radius: 15px; box-shadow: 0 0 40px #00ff41; margin: 20px auto; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. UPDATED CALLBACKS (Real-Time Aware) ---
def handle_kill_switch():
    st.session_state.halted = True
    challenge = st.session_state.current_threat
    
    # Check if a threat exists AND if it has been typed yet
    # 'bad_line' should be the index (0-based) of the malicious line in your YAML
    has_threat_appeared = challenge.get("threat") and st.session_state.current_line_idx >= challenge.get("bad_line", 99)

    if has_threat_appeared:
        st.session_state.score += 100
        st.session_state.status = "success"
    elif challenge.get("threat") and not has_threat_appeared:
        # User hit it too early! It's a threat but hasn't "attacked" yet
        st.session_state.score -= 25
        st.session_state.status = "fail"
        st.session_state.info_override = "TOO EARLY! The threat hadn't manifested yet."
    else:
        # False alarm on a safe file
        st.session_state.score -= 50
        st.session_state.status = "fail"
        st.session_state.info_override = "FALSE ALARM! This system was clean."

def next_sector_reset():
    st.session_state.lvl += 1
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)
    st.session_state.halted = False
    st.session_state.panic = False
    st.session_state.status = "active"
    st.session_state.current_line_idx = 0
    if 'info_override' in st.session_state: del st.session_state.info_override

# --- 4. GAME INTERFACE ---
st.markdown('<div style="text-align:center; color:#00ff41; font-weight:bold;">🛡️ ENDOR LABS | RSA 2026</div>', unsafe_allow_html=True)

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
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector_reset)

    with col1:
        st.subheader(st.session_state.current_threat['title'])
        code_box = st.empty()
        
        if not st.session_state.halted and not st.session_state.panic:
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            for idx, line in enumerate(lines):
                if st.session_state.halted: break
                st.session_state.current_line_idx = idx # Track current progress
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
            code_box.code(st.session_state.current_threat["code"], language="python")
            if st.session_state.status == "success":
                st.success(st.session_state.current_threat["info"])
            else:
                msg = getattr(st.session_state, 'info_override', "SYSTEM COMPROMISED")
                st.error(msg)

else:
    # --- 5. CERTIFICATE & LEADERBOARD ---
    st.markdown('<div style="text-align:center;"><img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueXF4ZzR6ZzR6ZzR6ZzR6ZzR6ZzR6ZzR6ZzR6ZzR6ZzR6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif" width="300"></div>', unsafe_allow_html=True)
    
    # Force a connection refresh
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        if not st.session_state.db_updated:
            df = conn.read(worksheet="Sheet1", ttl=0)
            new_row = pd.DataFrame([{"Pilot": st.session_state.pilot_name, "Score": st.session_state.score}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.session_state.db_updated = True
        
        # Display Leaderboard
        st.markdown("### 🏆 GALACTIC TOP 5")
        lb_df = conn.read(worksheet="Sheet1", ttl=0)
        lb_df['Score'] = pd.to_numeric(lb_df['Score'])
        st.table(lb_df.sort_values(by="Score", ascending=False).head(5))
    except Exception as e:
        st.error(f"Comms Jammed: {e}")

    if st.button("REBOOT"): st.session_state.clear(); st.rerun()

# --- 6. ADMIN ---
with st.expander("🛠️ Admin"):
    admin_pass = st.text_input("Password", type="password")
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "endor2026"):
        st.session_state.typing_speed = st.slider("Speed", 0.01, 0.20, st.session_state.typing_speed)
        if st.button("Reset Leaderboard"):
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(worksheet="Sheet1", data=pd.DataFrame(columns=["Pilot", "Score"]))
            st.rerun()
