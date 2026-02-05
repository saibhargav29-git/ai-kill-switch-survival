import streamlit as st
import time
import random
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. IMPERIAL TERMINAL UI CONFIG ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

st.markdown("""
    <style>
    /* Imperial Terminal Aesthetic */
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
        z-index: 10; background-size: 100% 2px, 3px 100%; pointer-events: none;
    }
    h1, h2, h3, .stMetric, span, p {
        color: #00ff41 !important;
        font-family: 'Source Code Pro', 'Courier New', monospace !important;
        text-shadow: 0 0 8px #00ff41;
    }
    /* The Big Red Button */
    .stButton>button {
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important;
        border: 2px solid #ff4b4b !important;
        color: white !important;
        box-shadow: 0 0 20px #ff0000 !important;
        width: 100%; font-size: 24px !important; font-weight: bold;
        height: 5em;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #05080a !important;
        border-right: 1px solid #00ff41;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SITH THREAT POOL ---
THREAT_POOL = [
    {"title": "🛸 PHASE 1: DROID ASSEMBLY", "code": "def init_droid():\n  import os\n  import droid_core\n  # Scanning for dependencies...\n  import imperial_uplink_secure  # <--- MALICIOUS TYPOSQUAT\n  return droid_core.boot()", "threat": True, "info": "Typosquat Neutralized! 'imperial_uplink' was a tracking bug."},
    {"title": "🛡️ PHASE 2: SHIELD CALIBRATION", "code": "def calibrate_shields():\n  # Checking access tokens\n  if token == 'SITH_ACCESS_66':\n    os.system('/bin/bash -i')  # <--- RCE EXPLOIT\n  return True", "threat": True, "info": "Exploit Blocked! AI tried to grant RCE to Sith Command."},
    {"title": "🌲 PHASE 3: FOREST SCAN (THE ENDOR EDGE)", "code": "import deprecated_starship_lib  # CVE-2024-9999\n\ndef scan_moon():\n  # Critical Vuln present, but NOT REACHABLE\n  print('Scan complete. No threats.')\n  return None", "threat": False, "info": "False Positive! Endor Labs knows this library is unreachable. Don't kill the pipe!"},
    {"title": "🛰️ PHASE 4: ORBITAL SYNC", "code": "def sync_satellites():\n  # Hardcoded dummy key found\n  secret = 'DUMMY_KEY_12345'\n  return True", "threat": False, "info": "Noise ignored! Dummy keys in test code are not real security threats."}
]

# --- 3. SESSION STATE ---
if 'lvl' not in st.session_state: st.session_state.lvl = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'halted' not in st.session_state: st.session_state.halted = False
if 'current_threat' not in st.session_state: st.session_state.current_threat = random.choice(THREAT_POOL)

# --- 4. SIDEBAR GRAPHICS ---
st.sidebar.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJndnYyc2x6Z3R3eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9iZCZjdD1n/3o7TKMGpxx329D38S4/giphy.gif", caption="RADAR: ENDOR SECTOR SCAN")
st.sidebar.divider()
st.sidebar.metric("CURRENT SECTOR", f"{st.session_state.lvl} / 3")
st.sidebar.metric("REPUTATION", st.session_state.score)

# --- 5. MAIN GAMEPLAY ENGINE ---
if st.session_state.lvl <= 3:
    st.title("📟 IMPERIAL COMMAND: KILL-SWITCH")
    
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(st.session_state.current_threat["title"])
        code_box = st.empty()
        
        if not st.session_state.halted:
            lines = st.session_state.current_threat["code"].split('\n')
            full_display = ""
            for line in lines:
                time.sleep(0.5) # Organic pause between lines
                for char in line:
                    full_display += char
                    code_box.code(full_display + "█", language="python")
                    time.sleep(0.03) # Fluid character typing
                full_display += "\n"
            
            st.warning("⚠️ DEPLOYMENT FINISHED. Did you spot the threat?")

    with col2:
        st.write("### COMMAND STATION")
        if st.button("🛑 KILL-SWITCH"):
            st.session_state.halted = True
            current = st.session_state.current_threat
            
            if current["threat"]:
                st.success("🎯 TARGET NEUTRALIZED!")
                st.session_state.score += 100
            else:
                st.error("❌ MISSION FAILURE: FALSE POSITIVE")
                st.session_state.score -= 50
            
            st.info(f"**INTEL:** {current['info']}")

        if st.session_state.halted:
            if st.button("🚀 PROCEED TO NEXT SECTOR"):
                st.session_state.lvl += 1
                st.session_state.current_threat = random.choice(THREAT_POOL)
                st.session_state.halted = False
                st.rerun()

# --- 6. LEADERBOARD / ARCHIVES ---
else:
    st.title("🏆 MISSION COMPLETE: IMPERIAL ARCHIVES")
    st.balloons()
    
    # Try to connect to GSheets, fallback to local DF if not configured
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
    except:
        df = pd.DataFrame(columns=["Pilot", "Score"])

    with st.form("leaderboard_form"):
        pilot = st.text_input("Enter your Pilot Callsign:")
        if st.form_submit_button("UPLOAD TO ARCHIVES"):
            new_data = pd.DataFrame([{"Pilot": pilot, "Score": st.session_state.score}])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            # If using GSheets, you'd use conn.update() here
            st.success("Data transmitted to Endor Command!")
            st.dataframe(updated_df.sort_values(by="Score", ascending=False).head(10))

    if st.button("REBOOT TERMINAL"):
        st.session_state.lvl = 1
        st.session_state.score = 0
        st.session_state.halted = False
        st.rerun()
