import streamlit as st
import time
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. SESSION STATE ---
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'panic' not in st.session_state: st.session_state.panic = False
if 'pilot_name' not in st.session_state: st.session_state.pilot_name = ""
if 'status' not in st.session_state: st.session_state.status = "active"
if 'typed_history' not in st.session_state: st.session_state.typed_history = ""

# --- 2. THREAT DATABASE ---
THREAT_POOL = [
    {"title": "🛸 PHASE 1: DROID ASSEMBLY", "code": "def init_droid():\n  import os\n  import droid_core\n  import imperial_uplink_secure  # <--- SUSPICIOUS!\n  return droid_core.boot()", "threat": True, "info": "TYPOSQUAT NEUTRALIZED!"},
    {"title": "🛡️ PHASE 2: SHIELD CONTROL", "code": "if token == 'SITH_66':\n  os.system('/bin/bash')  # <--- RCE EXPLOIT!\ncalibrate_shields()", "threat": True, "info": "RCE EXPLOIT BLOCKED!"},
    {"title": "📦 PHASE 3: SUPPLY CHAIN", "code": "import endor_labs_internal\n# Shadowing internal package...\nimport mal_pkg_shadow  # <--- MALICIOUS\nprint('Syncing...')", "threat": True, "info": "SUPPLY CHAIN ATTACK STOPPED!"},
    {"title": "🌲 PHASE 4: FOREST SCAN", "code": "import deprecated_lib  # CVE-2024\ndef scan():\n  # UNREACHABLE VULN\n  return None", "threat": False, "info": "FALSE POSITIVE! (Endor Edge)"}
]

if 'current_threat' not in st.session_state:
    st.session_state.current_threat = THREAT_POOL[0]

# --- 3. UI CONFIG ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

# Theme color logic
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
    /* Pulsing Kill Switch */
    .stButton>button {{ 
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important; 
        color: white !important; width: 100%; height: 6em; font-weight: bold; 
        border: 3px solid #ff4b4b !important; box-shadow: 0 0 20px #ff0000;
        font-size: 22px !important;
    }}
    .panic-text {{ color: #ff0000; font-weight: bold; font-size: 24px; animation: blink 0.5s infinite; text-align: center; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
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
    st.session_state.typed_history = ""

# --- 5. MAIN LOGIC ---
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
    st.write(f"PILOT: {st.session_state.pilot_name.upper()}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {st.session_state.current_threat['title']}")
        code_box = st.empty()
        
        # ACTIVE TYPING (Only if not stopped and not in panic)
        if not st.session_state.halted and not st.session_state.panic:
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            for line in lines:
                if st.session_state.halted: break # Exit loop immediately if button clicked
                time.sleep(0.4)
                for char in line:
                    if st.session_state.halted: break
                    full_text += char
                    code_box.code(full_text + "█", language="python")
                    time.sleep(0.01) # Faster character typing for responsiveness
                full_text += "\n"
            
            # If typing finishes naturally
            if not st.session_state.halted:
                st.session_state.typed_history = full_text
                st.session_state.panic = True
                st.rerun()
        
        else:
            # Result Display
            display_text = st.session_state.typed_history if st.session_state.typed_history else st.session_state.current_threat["code"]
            code_box.code(display_text, language="python")
            if st.session_state.status == "success":
                st.success(f"🎯 NEUTRALIZED: {st.session_state.current_threat['info']}")
            elif st.session_state.status == "fail":
                st.error(f"❌ MISFIRE: {st.session_state.current_threat['info']}")

    with col2:
        st.metric("SECTOR", f"{st.session_state.lvl}/{len(THREAT_POOL)}")
        st.metric("REPUTATION", st.session_state.score)
        st.divider()
        
        # The Kill-Switch is visible and clickable the entire time!
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
            if st.session_state.panic:
                st.markdown('<p class="panic-text">🚨 DEPLOYMENT IMMINENT! 🚨</p>', unsafe_allow_html=True)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector)
