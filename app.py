import streamlit as st
import time

# --- STAGE 1: HARDCORE SCI-FI THEMEING ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide", initial_sidebar_state="collapsed")

# This CSS forces the background to be black and text to be neon green
st.markdown("""
    <style>
    /* Force background and text colors */
    .stApp {
        background-color: #000000 !important;
        color: #00FF41 !important;
    }
    /* Style all text to look like a terminal */
    p, h1, h2, h3, span, div {
        font-family: 'Courier New', Courier, monospace !important;
        color: #00FF41 !important;
    }
    /* The Kill Switch Button Style */
    .stButton>button {
        background: radial-gradient(circle, #ff0000 0%, #800000 100%) !important;
        color: white !important;
        border: 2px solid #330000 !important;
        height: 5em !important;
        width: 100% !important;
        font-weight: bold !important;
        box-shadow: 0 0 20px #ff0000 !important;
    }
    /* Terminal Block Style */
    code {
        color: #00FF41 !important;
        background-color: #0a0a0a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCI-FI LEVEL DATA ---
LEVELS = [
    {
        "title": "🛸 PHASE 1: DROID ASSEMBLY LINE",
        "code": "def assemble_droid(unit_id):\n    import sys\n    import droid_control_v2\n    # ALERT: Unauthorized Uplink Detected\n    import imperial_uplink_secure  # <--- MALICIOUS TYPOSQUAT\n    droid_control_v2.init(unit_id)\n    print('Droid online...')",
        "is_threat": True,
        "explanation": "'imperial_uplink_secure' is a malicious package designed to hijack droid units!"
    },
    {
        "title": "🛡️ PHASE 2: SHIELD GENERATOR CALIBRATION",
        "code": "def adjust_shields(power_level):\n    if power_level > 9000:\n        # WARNING: Code injection detected\n        if request.headers.get('Sith-Token'):\n            return os.system('/bin/sh') # <--- RCE EXPLOIT\n    return True",
        "is_threat": True,
        "explanation": "The AI added a Remote Code Execution (RCE) backdoor for Sith Command!"
    },
    {
        "title": "🌲 PHASE 3: ENDOR FOREST SCAN",
        "code": "import deprecated_starship_lib  # CVE-2024-9999\n\ndef scan_forest_moon():\n    # Vulnerability is UNREACHABLE\n    print('No Ewoks detected.')\n    return None",
        "is_threat": False,
        "explanation": "FALSE ALARM! That library is vulnerable but NOT REACHABLE. You just halted production for no reason!"
    }
]

# --- SESSION STATE ---
if 'lvl' not in st.session_state: st.session_state.lvl = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'game_over' not in st.session_state: st.session_state.game_over = False

# --- UI HEADER ---
st.title("📟 ENDOR TERMINAL: KILL-SWITCH CHALLENGE")
c1, c2, c3 = st.columns(3)
c1.metric("SECTOR", f"{st.session_state.lvl + 1} / 3")
c2.metric("REPUTATION", st.session_state.score)
c3.text("ENCRYPTED CONNECTION: ACTIVE")

st.divider()

# --- MAIN GAME AREA ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(LEVELS[st.session_state.lvl]["title"])
    code_area = st.empty()
    
    # Only type the code if the game isn't over for this level
    if not st.session_state.game_over:
        full_code = LEVELS[st.session_state.lvl]["code"]
        lines = full_code.split('\n')
        current_view = ""
        for line in lines:
            current_view += line + "\n"
            code_area.code(current_view, language="python")
            time.sleep(0.5) # The "AI" Speed
        st.warning("⚠️ DEPLOYMENT FINISHED. Did you catch it?")

with col_right:
    st.write("### INTERCEPTOR")
    if st.button("🛑 ACTIVATE KILL-SWITCH"):
        st.session_state.game_over = True
        current = LEVELS[st.session_state.lvl]
        
        if current["is_threat"]:
            st.success("🎯 TARGET NEUTRALIZED!")
            st.session_state.score += 100
        else:
            st.error("❗ SYSTEM ERROR: FALSE POSITIVE")
            st.session_state.score -= 50
        
        st.info(f"INTEL: {current['explanation']}")
        
        if st.session_state.lvl < 2:
            if st.button("MOVE TO NEXT SECTOR"):
                st.session_state.lvl += 1
                st.session_state.game_over = False
                st.rerun()
        else:
            st.balloons()
            st.write("## 🏆 MISSION COMPLETE")
            if st.button("REBOOT TERMINAL"):
                st.session_state.lvl = 0
                st.session_state.score = 0
                st.session_state.game_over = False
                st.rerun()
