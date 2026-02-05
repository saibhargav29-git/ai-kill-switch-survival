import streamlit as st
import time

# 1. Setup Page Vibe
st.set_page_config(page_title="AI Bullshit Detector", layout="wide")
st.title("🎯 AI Bullshit Detector: Man vs. Machine")

# 2. Define the "Attacks" (The Level Data)
levels = [
    {"code": "import requests\nimport fast-api-secure # MALICIOUS PACKAGE!", "is_bug": True, "type": "Hallucination"},
    {"code": "def process(user_input):\n    eval(user_input) # REACHABLE VULN!", "is_bug": True, "type": "Reachable"},
    {"code": "import yaml\n# Vulnerable lib imported but NEVER used.\ndef hello():\n    print('Safe')", "is_bug": False, "type": "Unreachable (Noise)"}
]

# 3. Game State
if 'level' not in st.session_state:
    st.session_state.level = 0
    st.session_state.score = 0

# 4. The "AI Typing" Simulation
def type_code(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.1)

# 5. UI Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live AI Code Stream...")
    if st.button("START LEVEL"):
        st.write_stream(type_code(levels[st.session_state.level]["code"]))

with col2:
    st.subheader("The Buzzer")
    if st.button("🚨 SLAM BUZZER", use_container_width=True):
        current_lvl = levels[st.session_state.level]
        if current_lvl["is_bug"]:
            st.success(f"CORRECT! You caught a {current_lvl['type']}!")
            st.session_state.score += 100
        else:
            st.error("WRONG! That's unreachable noise. Endor Labs would have ignored this.")
            st.session_state.score -= 50
        
        if st.session_state.level < len(levels) - 1:
            st.session_state.level += 1
