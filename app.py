import streamlit as st
import time
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. SESSION STATE (The Brain) ---
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'panic' not in st.session_state: st.session_state.panic = False

# --- 2. DATA POOL ---
THREAT_POOL = [
    {"title": "🛸 PHASE 1: DROID ASSEMBLY", "code": "import droid_v2\nimport imperial_uplink_secure # <--- TYPOSQUAT", "threat": True, "info": "Typosquat Neutralized!"},
    {"title": "🛡️ PHASE 2: SHIELD CONTROL", "code": "if token == 'SITH_66':\n  os.system('/bin/bash') # <--- RCE EXPLOIT", "threat": True, "info": "RCE Exploit Blocked!"},
    {"title": "🌲 PHASE 3: FOREST SCAN", "code": "import deprecated_lib # CVE-2024\ndef scan():\n  # Vulnerability is UNREACHABLE", "threat": False, "info": "False Positive! (The Endor Edge)"},
    {"title": "🛰️ PHASE 4: ORBITAL SYNC", "code": "def sync():\n  key = 'DUMMY_KEY_12345'\n  return True", "threat": False, "info": "Noise ignored!"}
]

# Ensure the threat is persistent
if 'current_threat' not in st.session_state:
    st.session_state.current_threat = THREAT_POOL[0]

# --- 3. UI CONFIG & CSS ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

# Panic Colors
bg_color = "#05080a"
text_color = "#00ff41"
if st.session_state.panic:
    bg_color = "#330000"
    text_color = "#ff0000"

st.markdown(f"""<style>
    .stApp {{ background-color: {bg_color} !important; transition: 0.5s; }}
    h1, h2, h3, p, .stMetric {{ color: {text_color} !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ background: #8b0000 !important; color: white !important; width: 100%; height: 4em; font-weight: bold; border: 2px solid #ff0000; box-shadow: 0 0 15px #ff0000; }}
    .panic-text {{ color: #ff0000; font-weight: bold; font-size: 24px; text-align: center; animation: blink 0.5s infinite; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
</style>""", unsafe_allow_html=True)

# --- 4. CALLBACKS (Preventing the Loop) ---
def handle_kill_switch():
    st.session_state.halted = True
    st.session_state.panic = False
    if st.session_state.current_threat["threat"]:
        st.session_state.score += 100
    else:
        st.session_state.score -= 50

def next_sector():
    st.session_state.lvl += 1
    if st.session_state.lvl <= 4:
        st.session_state.current_threat = THREAT_POOL[st.session_state.lvl - 1]
    st.session_state.halted = False
    st.session_state.panic = False

# --- 5. MAIN GAME LOGIC ---
if st.session_state.lvl <= 4:
    st.title("📟 IMPERIAL COMMAND TERMINAL")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(st.session_state.current_threat["title"])
        code_box = st.empty()
        
        # Only type if NOT halted
        if not st.session_state.halted:
            full_text = ""
            for line in st.session_state.current_threat["code"].split('\n'):
                if st.session_state.halted: break
                time.sleep(0.4)
                for char in line:
                    if st.session_state.halted: break
                    full_text += char
                    code_box.code(full_text + "█", language="python")
                    time.sleep(0.02)
                full_text += "\n"
            
            # Switch to Panic Mode if finished and not stopped
            if not st.session_state.halted:
                st.session_state.panic = True
                st.markdown('<p class="panic-text">🚨 CRITICAL: AI DEPLOYMENT IMMINENT! 🚨</p>', unsafe_allow_html=True)
                st.button("🛑 KILL-SWITCH (PANIC OVERRIDE)", on_click=handle_kill_switch)
        else:
            code_box.code(st.session_state.current_threat["code"], language="python")
            st.info(f"**INTEL:** {st.session_state.current_threat['info']}")

    with col2:
        st.metric("SECTOR", f"{st.session_state.lvl}/4")
        st.metric("REPUTATION", st.session_state.score)
        st.divider()
        
        # Kill switch is only visible if not halted
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector)

else:
    st.title("🏆 MISSION COMPLETE")
    st.balloons()
    if st.button("REBOOT SYSTEM"):
        st.session_state.lvl = 1
        st.session_state.score = 0
        st.session_state.halted = False
        st.session_state.panic = False
        st.session_state.current_threat = THREAT_POOL[0]
        st.rerun()
