import streamlit as st
import time
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. SESSION STATE ---
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'panic' not in st.session_state: st.session_state.panic = False
if 'pilot_name' not in st.session_state: st.session_state.pilot_name = ""
if 'status' not in st.session_state: st.session_state.status = "active" # active, success, fail

# --- 2. DIVERSE THREAT POOL ---
THREAT_POOL = [
    {"title": "🛸 PHASE 1: DROID ASSEMBLY", "code": "import os\nimport droid_core\nimport imperial_uplink_secure # <--- TYPOSQUAT\ndroid_core.boot()", "threat": True, "info": "TYPOSQUAT! 'imperial_uplink' was a tracker."},
    {"title": "🛡️ PHASE 2: SHIELD CONTROL", "code": "def calibrate(token):\n  if token == 'SITH_66':\n    os.system('/bin/bash') # <--- RCE EXPLOIT\n  return True", "threat": True, "info": "RCE EXPLOIT! Backdoor found in shield logic."},
    {"title": "📦 PHASE 3: SUPPLY CHAIN", "code": "import endor_labs_internal # <--- DEPENDENCY CONFUSION\n# Internal package shadow attack\nprint('Update complete')", "threat": True, "info": "DEPENDENCY CONFUSION! Malicious public package hijacked internal name."},
    {"title": "🌲 PHASE 4: FOREST SCAN (THE ENDOR EDGE)", "code": "import deprecated_starship_lib # CVE-2024\ndef scan():\n  # Vuln present but NOT REACHABLE\n  return None", "threat": False, "info": "FALSE POSITIVE! Endor Labs knows this is unreachable. Pipe is safe!"},
    {"title": "🛰️ PHASE 5: ORBITAL SYNC", "code": "def sync():\n  # Hardcoded dummy key\n  secret = 'DUMMY_KEY_12345'\n  return True", "threat": False, "info": "NOISE! Dummy keys in test code are not threats."}
]

if 'current_threat' not in st.session_state:
    st.session_state.current_threat = THREAT_POOL[0]

# --- 3. UI THEMING ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

# Theme logic
bg_color = "#05080a"
text_color = "#00ff41" # Neon Green
if st.session_state.panic:
    bg_color = "#330000"
    text_color = "#ff4b4b"
elif st.session_state.status == "success":
    bg_color = "#0a1f0a"
    text_color = "#00ff41"
elif st.session_state.status == "fail":
    bg_color = "#2b0505"
    text_color = "#ff4b4b"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: 0.5s ease; }}
    h1, h2, h3, p, .stMetric {{ color: {text_color} !important; font-family: 'Courier New', monospace; text-shadow: 0 0 10px {text_color}; }}
    .stButton>button {{ background: #8b0000 !important; color: white !important; width: 100%; height: 5em; font-weight: bold; border: 2px solid #ff0000; box-shadow: 0 0 15px #ff0000; font-size: 20px; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    .panic-text {{ color: #ff0000; font-weight: bold; font-size: 24px; animation: blink 0.5s infinite; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CALLBACKS ---
def handle_kill_switch():
    st.session_state.halted = True
    st.session_state.panic = False
    if st.session_state.current_threat["threat"]:
        st.session_state.score += 100
        st.session_state.status = "success"
    else:
        st.session_state.score -= 50
        st.session_state.status = "fail"

def next_sector():
    st.session_state.lvl += 1
    if st.session_state.lvl <= len(THREAT_POOL):
        st.session_state.current_threat = THREAT_POOL[st.session_state.lvl - 1]
    st.session_state.halted = False
    st.session_state.panic = False
    st.session_state.status = "active"

# --- 5. GAME INTERFACE ---
if not st.session_state.pilot_name:
    st.title("📟 IMPERIAL COMMAND: LOGIN")
    with st.form("login"):
        name = st.text_input("Enter Pilot Callsign:")
        if st.form_submit_button("INITIATE MISSION"):
            if name: 
                st.session_state.pilot_name = name
                st.rerun()

elif st.session_state.lvl <= len(THREAT_POOL):
    st.title("📟 IMPERIAL COMMAND TERMINAL")
    st.subheader(f"ACTIVE PILOT: {st.session_state.pilot_name.upper()}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {st.session_state.current_threat['title']}")
        code_box = st.empty()
        
        if not st.session_state.halted:
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            for line in lines:
                if st.session_state.halted: break
                time.sleep(0.3)
                for char in line:
                    if st.session_state.halted: break
                    full_text += char
                    code_box.code(full_text + "█", language="python")
                    time.sleep(0.01)
                full_text += "\n"
            
            if not st.session_state.halted:
                st.session_state.panic = True
                st.markdown('<p class="panic-text">🚨 CRITICAL: MALICIOUS DEPLOYMENT IMMINENT! 🚨</p>', unsafe_allow_html=True)
                st.rerun()
        else:
            # Highlight result
            code_box.code(st.session_state.current_threat["code"], language="python")
            if st.session_state.status == "success":
                st.success(f"🎯 NEUTRALIZED: {st.session_state.current_threat['info']}")
            else:
                st.error(f"❌ ERROR: {st.session_state.current_threat['info']}")

    with col2:
        st.metric("SECTOR", f"{st.session_state.lvl}/{len(THREAT_POOL)}")
        st.metric("REPUTATION", st.session_state.score)
        st.divider()
        
        # Kill switch is NEVER disabled now!
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector)

else:
    st.title("🏆 MISSION COMPLETE")
    st.balloons()
    st.markdown(f"""<div style="border:5px double #00ff41; padding:20px; text-align:center;">
        <h2>CERTIFICATE OF MERIT</h2>
        <h1>{st.session_state.pilot_name.upper()}</h1>
        <p>FINAL SCORE: {st.session_state.score}</p>
    </div>""", unsafe_allow_html=True)
    if st.button("REBOOT SYSTEM"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
