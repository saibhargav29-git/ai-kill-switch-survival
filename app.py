import streamlit as st
import time

# --- STAR WARS / ENDOR THEME UI ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        background-color: #05080a;
        color: #00ff41; /* Matrix/Hacker Green */
        font-family: 'Source Code Pro', monospace;
    }
    .stButton>button {
        background: linear-gradient(145deg, #ff0000, #8b0000);
        color: white;
        border: 2px solid #550000;
        height: 4em;
        width: 100%;
        font-size: 24px;
        font-weight: bold;
        text-shadow: 2px 2px #000;
        box-shadow: 0 0 15px #ff0000;
    }
    .stButton>button:hover {
        background: #ff4b4b;
        box-shadow: 0 0 25px #ff0000;
    }
    .terminal-output {
        background-color: #000;
        border: 1px solid #00ff41;
        padding: 20px;
        border-radius: 5px;
        box-shadow: inset 0 0 10px #00ff41;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCI-FI LEVEL DATA ---
LEVELS = [
    {
        "title": "🛸 PHASE 1: DROID ASSEMBLY LINE",
        "code": "def assemble_droid(unit_id):\n    import sys\n    import droid_control_v2\n    # AI suggesting a suspicious dependency\n    import imperial_uplink_secure  # <--- MALICIOUS TYPOSQUAT\n    droid_control_v2.init(unit_id)\n    print('Droid online...')",
        "is_threat": True,
        "type": "Typosquat",
        "explanation": "'imperial_uplink_secure' is a malicious package designed to hijack droid units!"
    },
    {
        "title": "🛡️ PHASE 2: SHIELD GENERATOR CALIBRATION",
        "code": "def adjust_shields(power_level):\n    if power_level > 9000:\n        # AI added a secret backdoor access\n        if request.headers.get('Secret-Sith-Token'):\n            return os.system('/bin/sh') # <--- RCE EXPLOIT\n    return True",
        "is_threat": True,
        "type": "Exploit",
        "explanation": "The AI added a Remote Code Execution (RCE) backdoor for Sith Command!"
    },
    {
        "title": "🌲 PHASE 3: ENDOR ARCHIVE SCAN (THE REACHABILITY TEST)",
        "code": "import deprecated_starship_lib  # CVE-2024-9999 (CRITICAL)\n\ndef scan_forest_moon():\n    # This function is safe.\n    # deprecated_starship_lib is never actually called.\n    print('No Ewoks detected.')\n    return None",
        "is_threat": False,
        "type": "Noise",
        "explanation": "FALSE ALARM! 'deprecated_starship_lib' is vulnerable but UNREACHABLE. You halted the scan for no reason. Endor Labs would have ignored this noise."
    }
]

# --- GAME STATE ---
if 'lvl' not in st.session_state: st.session_state.lvl = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'game_active' not in st.session_state: st.session_state.game_active = False

# --- UI HEADER ---
st.title("📟 ENDOR KILL-SWITCH: SURVIVAL CHALLENGE")
cols = st.columns(4)
cols[0].metric("LEVEL", f"{st.session_state.lvl + 1} / 3")
cols[1].metric("SCORE", st.session_state.score)
cols[2].text("PIPELINE STATUS:")
if st.session_state.game_active:
    cols[2].warning("RUNNING...")
else:
    cols[2].success("HALTED")

# --- GAMEPLAY ---
col_main, col_btn = st.columns([3, 1])

with col_main:
    st.subheader(LEVELS[st.session_state.lvl]["title"])
    placeholder = st.empty()
    
    if not st.session_state.game_active:
        if st.button("🚀 INITIATE DEPLOYMENT"):
            st.session_state.game_active = True
            st.rerun()

    if st.session_state.game_active:
        full_code = LEVELS[st.session_state.lvl]["code"]
        lines = full_code.split('\n')
        displayed_code = ""
        for line in lines:
            displayed_code += line + "\n"
            placeholder.code(displayed_code, language="python")
            time.sleep(0.4) # Adjust speed here
        
        st.error("⚠️ DEPLOYMENT COMPLETE. System Compromised?")
        st.session_state.game_active = False

with col_btn:
    st.write("### COMMAND")
    if st.button("🚨 KILL-SWITCH"):
        current = LEVELS[st.session_state.lvl]
        if current["is_threat"]:
            st.success("🔥 THREAT NEUTRALIZED!")
            st.session_state.score += 100
        else:
            st.error("❌ MISSION FAILURE")
            st.write("You killed the process for a False Positive.")
            st.session_state.score -= 50
        
        st.write(f"**INTEL:** {current['explanation']}")
        
        if st.session_state.lvl < 2:
            if st.button("PROCEED TO NEXT SECTOR"):
                st.session_state.lvl += 1
                st.session_state.game_active = False
                st.rerun()
        else:
            st.balloons()
            st.write("## 🎉 CHALLENGE COMPLETE")
            if st.button("RESTART MISSION"):
                st.session_state.lvl = 0
                st.session_state.score = 0
                st.rerun()
