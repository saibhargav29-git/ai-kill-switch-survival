import streamlit as st
import time
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. SESSION STATE MANAGEMENT ---
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'panic' not in st.session_state: st.session_state.panic = False
if 'pilot_name' not in st.session_state: st.session_state.pilot_name = ""
if 'uploaded' not in st.session_state: st.session_state.uploaded = False

# --- 2. THE SITH THREAT POOL ---
THREAT_POOL = [
    {"title": "🛸 PHASE 1: DROID ASSEMBLY", "code": "def init_droid():\n  import os\n  import droid_core\n  # Scanning for dependencies...\n  import imperial_uplink_secure  # <--- MALICIOUS TYPOSQUAT\n  return droid_core.boot()", "threat": True, "info": "Typosquat Neutralized! 'imperial_uplink' was a tracking bug."},
    {"title": "🛡️ PHASE 2: SHIELD CALIBRATION", "code": "def calibrate_shields():\n  # Checking access tokens\n  if token == 'SITH_ACCESS_66':\n    os.system('/bin/bash -i')  # <--- RCE EXPLOIT\n  return True", "threat": True, "info": "Exploit Blocked! AI tried to grant RCE to Sith Command."},
    {"title": "🌲 PHASE 3: FOREST SCAN (THE ENDOR EDGE)", "code": "import deprecated_starship_lib  # CVE-2024-9999\n\ndef scan_moon():\n  # Critical Vuln present, but NOT REACHABLE\n  print('Scan complete. No threats.')\n  return None", "threat": False, "info": "False Positive! Endor Labs knows this library is unreachable. Don't kill the pipe!"},
    {"title": "🛰️ PHASE 4: ORBITAL SYNC", "code": "def sync_satellites():\n  # Hardcoded dummy key found\n  secret = 'DUMMY_KEY_12345'\n  return True", "threat": False, "info": "Noise ignored! Dummy keys in test code are not real security threats."}
]

if 'current_threat' not in st.session_state:
    st.session_state.current_threat = THREAT_POOL[0]

# --- 3. UI CONFIG & STAR WARS CSS ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

# Dynamic Theme Switching
bg_color = "#05080a"
text_color = "#00ff41"
if st.session_state.panic:
    bg_color = "#330000"
    text_color = "#ff0000"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: background-color 0.5s ease; }}
    h1, h2, h3, p, .stMetric, .pilot-text {{ color: {text_color} !important; font-family: 'Courier New', monospace !important; }}
    .stButton>button {{ background: #8b0000 !important; color: white !important; width: 100%; height: 4em; font-weight: bold; border: 2px solid #ff0000; box-shadow: 0 0 15px #ff0000; }}
    .pilot-display {{ font-size: 20px; border-bottom: 2px solid {text_color}; padding-bottom: 10px; margin-bottom: 20px; text-transform: uppercase; font-weight: bold; }}
    .panic-text {{ color: #ff0000; font-weight: bold; font-size: 24px; text-align: center; animation: blink 0.5s infinite; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    .certificate-box {{ border: 5px double #00ff41; padding: 30px; background-color: #0a140a; text-align: center; border-radius: 15px; box-shadow: 0 0 30px #00ff41; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC CALLBACKS ---
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

# --- 5. APP FLOW ---

# STEP A: Pilot Identification
if not st.session_state.pilot_name:
    st.title("📟 IMPERIAL COMMAND: LOGIN")
    st.sidebar.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJndnYyc2x6Z3R3eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxx329D38S4/giphy.gif")
    with st.form("login"):
        name = st.text_input("Enter Pilot Callsign:")
        if st.form_submit_button("INITIATE MISSION"):
            if name:
                st.session_state.pilot_name = name
                st.rerun()

# STEP B: Active Mission (Levels 1-4)
elif st.session_state.lvl <= 4:
    st.title("📟 IMPERIAL COMMAND TERMINAL")
    st.markdown(f'<div class="pilot-display">ACTIVE PILOT: {st.session_state.pilot_name}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(st.session_state.current_threat["title"])
        code_box = st.empty()
        
        if not st.session_state.halted:
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            for line in lines:
                if st.session_state.halted: break
                time.sleep(0.4) # Wait before new line
                for char in line:
                    if st.session_state.halted: break
                    full_text += char
                    code_box.code(full_text + "█", language="python")
                    time.sleep(0.02)
                full_text += "\n"
            
            # Trigger Panic if finished and not killed
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
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector)

# STEP C: Mission Summary & Certificate
else:
    st.title("🏆 MISSION COMPLETE")
    st.balloons()

    st.markdown(f"""
    <div class="certificate-box">
        <h1 style="color: #00ff41;">CERTIFICATE OF MERIT</h1>
        <p style="color: #00ff41;">This document certifies that</p>
        <h2 style="color: #ffffff; font-size: 40px;">{st.session_state.pilot_name}</h2>
        <p style="color: #00ff41;">has successfully protected the Endor Pipeline</p>
        <hr style="border: 1px solid #00ff41; width: 50%;">
        <p style="color: #00ff41; font-size: 24px;">FINAL SCORE: <b>{st.session_state.score}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Global Leaderboard Logic
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        if not st.session_state.uploaded:
            existing = conn.read(ttl=0)
            new_row = pd.DataFrame([{"Pilot": st.session_state.pilot_name, "Score": st.session_state.score}])
            conn.update(data=pd.concat([existing, new_row]))
            st.session_state.uploaded = True
        
        st.subheader("🌌 GLOBAL LEADERBOARD")
        st.table(conn.read(ttl=0).sort_values(by="Score", ascending=False).head(10))
    except:
        st.warning("Archives currently offline. Score not saved to cloud.")

    if st.button("REBOOT FOR NEXT PILOT"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
