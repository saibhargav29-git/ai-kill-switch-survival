import streamlit as st
import time
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. SESSION STATE INITIALIZATION ---
# Using session_state to ensure we don't lose progress during reruns
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'panic' not in st.session_state: st.session_state.panic = False
if 'pilot_name' not in st.session_state: st.session_state.pilot_name = ""
if 'status' not in st.session_state: st.session_state.status = "active"

# --- 2. THE THREAT DATABASE ---
THREAT_POOL = [
    {"title": "🛸 PHASE 1: DROID ASSEMBLY", "code": "import os\nimport droid_core\nimport imperial_uplink_secure # <--- TYPOSQUAT\ndroid_core.boot()", "threat": True, "info": "TYPOSQUAT NEUTRALIZED!"},
    {"title": "🛡️ PHASE 2: SHIELD CONTROL", "code": "if token == 'SITH_66':\n  os.system('/bin/bash') # <--- RCE EXPLOIT\ncalibrate()", "threat": True, "info": "RCE EXPLOIT BLOCKED!"},
    {"title": "📦 PHASE 3: SUPPLY CHAIN", "code": "import endor_internal_lib # Shadow attack\n# Checking versioning...\nprint('Syncing...')", "threat": True, "info": "SUPPLY CHAIN ATTACK STOPPED!"},
    {"title": "🌲 PHASE 4: FOREST SCAN", "code": "import deprecated_lib # CVE-2024\ndef scan():\n  # UNREACHABLE VULN\n  return None", "threat": False, "info": "FALSE POSITIVE! (Endor Edge)"}
]

# Lock the current threat so it doesn't change during reruns
if 'current_threat' not in st.session_state:
    st.session_state.current_threat = THREAT_POOL[0]

# --- 3. DYNAMIC UI STYLING ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

# Theme logic based on game state
bg_color = "#05080a"
text_color = "#00ff41"
if st.session_state.status == "fail" or st.session_state.panic:
    bg_color = "#330000"
    text_color = "#ff4b4b"
elif st.session_state.status == "success":
    bg_color = "#0a1f0a"
    text_color = "#00ff41"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: 0.5s; }}
    h1, h2, h3, p, .stMetric {{ color: {text_color} !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ background: #8b0000 !important; color: white !important; width: 100%; height: 5em; font-weight: bold; border: 2px solid #ff0000; box-shadow: 0 0 15px #ff0000; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    .panic-text {{ color: #ff0000; font-weight: bold; font-size: 24px; animation: blink 0.5s infinite; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CALLBACKS (Ensuring smooth state transitions) ---
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

# --- 5. APP FLOW ---
# LOGIN
if not st.session_state.pilot_name:
    st.title("📟 IMPERIAL COMMAND: LOGIN")
    with st.form("login"):
        name = st.text_input("Enter Pilot Callsign:")
        if st.form_submit_button("INITIATE MISSION"):
            if name: 
                st.session_state.pilot_name = name
                st.rerun()

# MISSION SCREEN
elif st.session_state.lvl <= len(THREAT_POOL):
    st.title("📟 IMPERIAL COMMAND TERMINAL")
    st.write(f"PILOT: {st.session_state.pilot_name.upper()}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {st.session_state.current_threat['title']}")
        code_box = st.empty()
        
        # TYPING ENGINE: This loop only runs when NOT halted
        if not st.session_state.halted:
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            for i, line in enumerate(lines):
                if st.session_state.halted: break
                time.sleep(0.5)
                for char in line:
                    if st.session_state.halted: break
                    full_text += char
                    code_box.code(full_text + "█", language="python")
                    time.sleep(0.02)
                full_text += "\n"
            
            # If we reach the end without a kill-switch, trigger PANIC
            if not st.session_state.halted and not st.session_state.panic:
                st.session_state.panic = True
                st.rerun() # Refresh to trigger the red background and stop the typing loop
        else:
            # Show static code and result
            code_box.code(st.session_state.current_threat["code"], language="python")
            if st.session_state.status == "success":
                st.success(f"🎯 {st.session_state.current_threat['info']}")
            else:
                st.error(f"❌ {st.session_state.current_threat['info']}")

    with col2:
        st.metric("SECTOR", f"{st.session_state.lvl}/{len(THREAT_POOL)}")
        st.metric("REPUTATION", st.session_state.score)
        st.divider()
        
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
            if st.session_state.panic:
                st.markdown('<p class="panic-text">🚨 DEPLOYMENT IMMINENT! 🚨</p>', unsafe_allow_html=True)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector)

# FINAL SCREEN
else:
    st.title("🏆 MISSION COMPLETE")
    st.markdown(f"### {st.session_state.pilot_name.upper()}, you saved the sector.")
    st.metric("FINAL REPUTATION", st.session_state.score)
    if st.button("REBOOT SYSTEM"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
