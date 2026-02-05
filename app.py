import streamlit as st
import time

# --- THEME & CONFIG ---
st.set_page_config(page_title="AI Kill-Switch Challenge", layout="wide")

# Custom CSS for "Hacker House" Vibe
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; color: #00ff00; }
    .stButton>button { background-color: #ff4b4b; color: white; height: 5em; width: 100%; font-size: 20px; font-weight: bold; border-radius: 10px; }
    .status-box { padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- GAME DATA (The 3 Levels) ---
LEVELS = [
    {
        "title": "Level 1: The Shadow Dependency",
        "code": "import os\nimport requests\n# AI suggests a new security helper\nimport fast-api-secure-helper  # <--- MALICIOUS TYPOSQUAT",
        "is_threat": True,
        "type": "Typosquat",
        "explanation": "That package doesn't exist. It's a typosquatting attack!"
    },
    {
        "title": "Level 2: The Logic Bomb",
        "code": "def auth_user(username, password):\n    if username == 'endor_admin_backdoor':\n        return True # <--- UNAUTHORIZED ACCESS",
        "is_threat": True,
        "type": "Exploit",
        "explanation": "The AI added a hardcoded backdoor!"
    },
    {
        "title": "Level 3: The Endor Edge (Reachability)",
        "code": "import old_lib_v1 # Vulnerable but NOT USED\n\ndef main():\n    print('Hello World')\n    # The vulnerable function in old_lib is never called.",
        "is_threat": False,
        "type": "Noise",
        "explanation": "This is a False Positive! The vulnerability is unreachable. Hitting the switch caused $50k in downtime."
    }
]

# --- SESSION STATE ---
if 'lvl' not in st.session_state: st.session_state.lvl = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'game_active' not in st.session_state: st.session_state.game_active = False

# --- UI LAYOUT ---
st.title("🚨 AI Kill-Switch Challenge")
st.write(f"**Score:** {st.session_state.score} | **Current Phase:** {st.session_state.lvl + 1}/3")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 Live Production Pipeline")
    if st.button("▶️ DEPLOY TO PROD", key="start_btn"):
        st.session_state.game_active = True
        
    code_placeholder = st.empty()
    
    if st.session_state.game_active:
        full_code = LEVELS[st.session_state.lvl]["code"]
        current_display = ""
        for char in full_code:
            current_display += char
            code_placeholder.code(current_display, language="python")
            time.sleep(0.04) # Speed of the "AI Agent"
        st.warning("⚠️ Code Deployed! Did you miss the threat?")
        st.session_state.game_active = False

with col2:
    st.subheader("⌨️ Command Station")
    # THE BIG RED BUTTON
    if st.button("🛑 EMERGENCY STOP (KILL-SWITCH)", key="kill_btn"):
        current_data = LEVELS[st.session_state.lvl]
        
        if current_data["is_threat"]:
            st.success(f"✅ GREAT CATCH! Stopped a {current_data['type']} attack.")
            st.session_state.score += 100
        else:
            st.error("❌ FALSE ALARM! That bug was unreachable. You halted production for no reason.")
            st.session_state.score -= 50
        
        st.info(f"**The Endor Truth:** {current_data['explanation']}")
        
        if st.session_state.lvl < 2:
            if st.button("Next Level"):
                st.session_state.lvl += 1
                st.rerun()
        else:
            st.balloons()
            st.write("### Game Over! Show this to the Endor Labs Team for your Swag!")
