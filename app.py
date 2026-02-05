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
    .stApp {{ background-color: {bg_color} !important; transition: 0.5s; }}
    h1, h2, h3, p, .stMetric {{ color: {text_color} !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ 
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important; 
        color: white !important; width: 100%; height: 6em; font-weight: bold; 
        border: 3px solid #ff4b4b !important; box-shadow: 0 0 20px #ff0000;
        font-size: 22px !important;
    }}
    .certificate-box {{ border: 5px double #00ff41; padding: 40px; background-color: #0a140a; text-align: center; border-radius: 15px; box-shadow: 0 0 40px #00ff41; margin: 50px auto; max-width: 800px; }}
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

# --- 5. APP FLOW ---
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
        
        # Only type if the user hasn't hit the switch and we aren't already in panic
        if not st.session_state.halted and not st.session_state.panic:
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
            
            # If the loop finished naturally, trigger panic once
            if not st.session_state.halted:
                st.session_state.panic = True
                st.rerun()
        else:
            code_box.code(st.session_state.current_threat["code"], language="python")
            if st.session_state.status == "success":
                st.success(f"🎯 NEUTRALIZED: {st.session_state.current_threat['info']}")
            elif st.session_state.status == "fail":
                st.error(f"❌ MISFIRE: {st.session_state.current_threat['info']}")
            elif st.session_state.panic:
                st.warning("⚠️ DEPLOYMENT FINISHED. Did you spot the threat?")

    with col2:
        st.metric("SECTOR", f"{st.session_state.lvl}/{len(THREAT_POOL)}")
        st.metric("REPUTATION", st.session_state.score)
        st.divider()
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector)

else:
    st.balloons()
    st.markdown(f'<div class="certificate-box"><h1>CERTIFICATE OF MERIT</h1><h2>{st.session_state.pilot_name.upper()}</h2><hr><h3>FINAL REPUTATION: {st.session_state.score}</h3></div>', unsafe_allow_html=True)
    if st.button("REBOOT FOR NEXT PILOT"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
