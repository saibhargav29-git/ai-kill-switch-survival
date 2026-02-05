import streamlit as st
import time
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. IMPERIAL TERMINAL UI ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #05080a !important;
        background-image: radial-gradient(circle, #0a1f0a 1%, #05080a 100%);
        color: #00ff41 !important;
    }
    /* CRT Scanline Effect */
    .stApp::before {
        content: " "; display: block; position: absolute; top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
        z-index: 2; background-size: 100% 2px, 3px 100%; pointer-events: none;
    }
    h1, h2, h3, .stMetric, span, p {
        color: #00ff41 !important;
        font-family: 'Courier New', Courier, monospace !important;
        text-shadow: 0 0 8px #00ff41;
    }
    .stButton>button {
        background: #8b0000 !important;
        border: 2px solid #ff0000 !important;
        color: white !important;
        box-shadow: 0 0 15px #ff0000 !important;
        width: 100%; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA POOL ---
THREAT_POOL = [
    {"title": "🛸 DROID ASSEMBLY", "code": "import sys\nimport droid_v2\nimport imperial_uplink_secure # <--- TYPOSQUAT", "threat": True, "info": "Typosquat! 'imperial_uplink' is a tracking bug."},
    {"title": "🛡️ SHIELD CONTROL", "code": "def calibrate(p):\n  if header == 'Sith-Token':\n    os.system('/bin/sh') # <--- RCE", "threat": True, "info": "Exploit! AI added a backdoor for Sith Command."},
    {"title": "🌲 FOREST SCAN", "code": "import old_lib_v1 # CVE-2024\ndef scan():\n  # Vulnerability is UNREACHABLE\n  print('Safe')", "threat": False, "info": "Noise! Library is vulnerable but NOT REACHABLE."},
    {"title": "🛰️ ORBITAL SYNC", "code": "def sync():\n  # Static analysis noise\n  x = 'hardcoded_dummy_key'\n  return True", "threat": False, "info": "False Positive! Dummy keys are not real secrets."}
]

# --- 3. STATE MGMT ---
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'current_threat' not in st.session_state: st.session_state.current_threat = random.choice(THREAT_POOL)

# --- 4. GAMEPLAY ---
if st.session_state.lvl <= 3:
    st.title("📟 IMPERIAL TERMINAL: SECTOR CONTROL")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(st.session_state.current_threat["title"])
        code_box = st.empty()
        if not st.session_state.halted:
            lines = st.session_state.current_threat["code"].split('\n')
            full_text = ""
            for line in lines:
                full_text += line + "\n"
                code_box.code(full_text, language="python")
                time.sleep(0.4)
            st.warning("⚠️ DEPLOYMENT FINISHED. REACT NOW!")

    with col2:
        st.write("### COMMANDS")
        if st.button("🛑 EMERGENCY KILL-SWITCH"):
            st.session_state.halted = True
            if st.session_state.current_threat["threat"]:
                st.success("🎯 TARGET NEUTRALIZED")
                st.session_state.score += 100
            else:
                st.error("❌ REPUTATION LOSS: FALSE ALARM")
                st.session_state.score -= 50
            st.info(st.session_state.current_threat["info"])

        if st.session_state.halted:
            if st.button("🚀 NEXT SECTOR"):
                st.session_state.lvl += 1
                st.session_state.current_threat = random.choice(THREAT_POOL)
                st.session_state.halted = False
                st.rerun()
    
    st.divider()
    st.metric("SCORE / REPUTATION", st.session_state.score)

# --- 5. GLOBAL LEADERBOARD (POST-MISSION) ---
else:
    st.title("🏆 MISSION COMPLETE: IMPERIAL ARCHIVES")
    st.balloons()
    
    # Connection to Google Sheets
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn.read(ttl=0)
    except:
        existing_data = pd.DataFrame(columns=["Pilot", "Score"])

    with st.form("archive_form"):
        name = st.text_input("Enter Pilot Callsign:")
        if st.form_submit_button("UPLOAD DATA"):
            new_row = pd.DataFrame([{"Pilot": name, "Score": st.session_state.score}])
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Data transmitted to Endor Command!")

    st.subheader("🌌 TOP GUARDIANS OF ENDOR")
    st.dataframe(existing_data.sort_values(by="Score", ascending=False).head(10), use_container_width=True)
    
    if st.button("REBOOT SYSTEM"):
        st.session_state.lvl = 1
        st.session_state.score = 0
        st.rerun()
