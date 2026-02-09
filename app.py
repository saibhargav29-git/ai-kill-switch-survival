import streamlit as st
import time
import yaml
import random
import pandas as pd
import base64
from supabase import create_client, Client

# --- 1. DATABASE SETUP (SUPABASE) ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- 2. CORE LOGIC & DATA ---
def load_challenges():
    try:
        with open("challenges.yaml", 'r') as f:
            return yaml.load(f, Loader=yaml.SafeLoader)['challenges']
    except Exception:
        return [{"title": "SYSTEM ERROR", "threat": True, "bad_line": 0, "info": "YAML Missing", "code": "import os\nos.system('malicious')"}]

# Initialize Session States
state_defaults = {
    'lvl': 1, 'score': 0, 'halted': False, 'panic': False, 
    'pilot_name': "", 'status': "active", 'db_updated': False, 
    'typing_speed': 0.08, 'current_line_idx': 0, 'music_on': True
}
for key, val in state_defaults.items():
    if key not in st.session_state: st.session_state[key] = val

if 'challenge_pool' not in st.session_state:
    st.session_state.challenge_pool = load_challenges()

# Ensure we have a starting threat
if 'current_threat' not in st.session_state:
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)

# --- 3. THEME & AUDIO FX ---
st.set_page_config(page_title="Endor Kill-Switch", layout="wide")

def play_audio(file_name, loop=True):
    if st.session_state.music_on:
        try:
            with open(file_name, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                loop_attr = "loop" if loop else ""
                audio_html = f"""
                    <audio autoplay {loop_attr} id="bg-music">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                    <script>
                        var audio = window.parent.document.getElementById("bg-music");
                        if (audio) {{ audio.volume = 0.3; audio.play(); }}
                    </script>
                """
                st.components.v1.html(audio_html, height=0)
        except Exception:
            pass 

bg_color = "#05080a"
if st.session_state.panic: bg_color = "#440000"
elif st.session_state.status == "success": bg_color = "#0a1f0a"
elif st.session_state.status == "fail": bg_color = "#2b0505"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: 0.5s; }}
    h1, h2, h3, p, .stMetric {{ color: #00ff41 !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ 
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important; 
        color: white !important; width: 100%; height: 5em; font-weight: bold; 
        border: 3px solid #ff4b4b !important; box-shadow: 0 0 20px #ff0000;
        font-size: 20px !important;
    }}
    .certificate-box {{ border: 5px double #00ff41; padding: 40px; background-color: #0a140a; text-align: center; border-radius: 15px; box-shadow: 0 0 40px #00ff41; margin: 20px auto; }}
    .imperial-box {{ border: 5px solid #ff0000; padding: 40px; background-color: #1a0000; text-align: center; border-radius: 5px; box-shadow: 0 0 40px #ff0000; margin: 20px auto; }}
    </style>
    """, unsafe_allow_html=True)

if st.session_state.pilot_name:
    if st.session_state.lvl > 5 and st.session_state.score >= 100:
        play_audio("star_wars_theme.mp3", loop=False)
    elif st.session_state.lvl <= 5:
        play_audio("imperial_march.mp3", loop=True)

def show_galactic_fx(is_success):
    if is_success:
        st.markdown('<div style="font-size: 50px; text-align: center; margin: 10px;">✨ 🛸 ✨ 🌟 🌌 ⚔️ 🌌 🌟 🛸 ✨</div>', unsafe_allow_html=True)
        st.markdown('<div style="background-color:#00ff41; color:black; padding:10px; text-align:center; font-weight:bold; border-radius:5px;">MISSION ACCOMPLISHED ... SECTOR SECURED ... THE FORCE IS STRONG WITH YOU</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 50px; text-align: center; margin: 10px;">🚨 🛰️ 🚨 💥 🌑 💥 🛰️ 🚨</div>', unsafe_allow_html=True)
        st.markdown('<div style="background-color:#ff0000; color:white; padding:10px; text-align:center; font-weight:bold; border-radius:5px;">SYSTEM BREACH ... IMPERIAL FORCES OVERRUNNING SECTOR ... MISSION FAILED</div>', unsafe_allow_html=True)

# --- 4. CALLBACKS ---
def handle_kill_switch():
    st.session_state.halted = True
    challenge = st.session_state.current_threat
    has_threat_appeared = challenge.get("threat") and st.session_state.current_line_idx >= challenge.get("bad_line", 0)

    if has_threat_appeared:
        st.session_state.score += 100
        st.session_state.status = "success"
    elif challenge.get("threat") and not has_threat_appeared:
        st.session_state.score -= 25
        st.session_state.status = "fail"
        st.session_state.info_override = "TOO EARLY! The malicious code hadn't manifested yet."
    else:
        st.session_state.score -= 50
        st.session_state.status = "fail"
        st.session_state.info_override = "FALSE ALARM! This system was clean."

def next_sector_reset():
    st.session_state.lvl += 1
    # FIX: Explicitly pick a NEW random challenge for the next level
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)
    st.session_state.halted = False
    st.session_state.panic = False
    st.session_state.status = "active"
    st.session_state.current_line_idx = 0
    if 'info_override' in st.session_state: del st.session_state.info_override

# --- 5. GAME INTERFACE ---
st.markdown('<div style="text-align:center; color:#00ff41; font-weight:bold; letter-spacing:3px;">🛡️ ENDOR LABS | RSA 2026</div>', unsafe_allow_html=True)

if not st.session_state.pilot_name:
    st.title("📟 LOGIN: PILOT CALLSIGN")
    with st.form("login"):
        name = st.text_input("Enter Callsign:")
        if st.form_submit_button("INITIATE"):
            if name: 
                st.session_state.pilot_name = name
                # Ensure the very first level has a random threat
                st.session_state.current_threat = random.choice(st.session_state.challenge_pool)
                st.rerun()

elif st.session_state.lvl <= 5:
    col1, col2 = st.columns([3, 1])
    with col2:
        st.metric("SCORE", st.session_state.score)
        st.metric("SECTOR", f"{st.session_state.lvl}/5")
        st.divider()
        if not st.session_state.halted:
            st.button("🛑 KILL-SWITCH", on_click=handle_kill_switch)
        else:
            st.button("🚀 NEXT SECTOR", on_click=next_sector_reset)

    with col1:
        st.subheader(st.session_state.current_threat['title'])
        timer_bar = st.empty()
        code_box = st.empty()
        feedback_area = st.empty() 
        
        if not st.session_state.halted and not st.session_state.panic:
            feedback_area.empty()
            full_text = ""
            lines = st.session_state.current_threat["code"].split('\n')
            total_lines = len(lines)
            
            for idx, line in enumerate(lines):
                if st.session_state.halted: break
                st.session_state.current_line_idx = idx 
                timer_bar.progress((idx + 1) / total_lines, text=f"SCANNING LINE {idx+1}/{total_lines}")
                
                for char in line:
                    if st.session_state.halted: break
                    full_text += char
                    code_box.code(full_text + "█", language="python")
                    time.sleep(st.session_state.typing_speed)
                full_text += "\n"
                time.sleep(st.session_state.typing_speed * 2)
            
            if not st.session_state.halted:
                st.session_state.panic = True
                st.rerun()
        else:
            timer_bar.empty()
            code_box.code(st.session_state.current_threat["code"], language="python")
            with feedback_area:
                if st.session_state.status == "success":
                    st.success(st.session_state.current_threat["info"])
                else:
                    msg = st.session_state.get('info_override', "SYSTEM COMPROMISED!")
                    st.error(msg)

else:
    # --- 6. CONDITIONAL FINALE & DB UPDATE ---
    if not st.session_state.db_updated:
        try:
            supabase.table("leaderboard").insert({
                "pilot": st.session_state.pilot_name, 
                "score": st.session_state.score
            }).execute()
            st.session_state.db_updated = True
        except Exception as e:
            st.error("DATABASE SYNC FAILED.")

    show_galactic_fx(st.session_state.score >= 100)

    if st.session_state.score < 100:
        st.markdown(f'<div class="imperial-box"><h1 style="color:#ff0000;">IMPERIAL OCCUPATION</h1><h2 style="color:white;">{st.session_state.pilot_name.upper()}</h2><hr style="border: 1px solid #ff0000;"><h3 style="color:white;">FINAL SCORE: {st.session_state.score}</h3></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="certificate-box"><h1>REPUBLIC COMMENDATION</h1><h2>{st.session_state.pilot_name.upper()}</h2><hr style="border: 1px solid #00ff41;"><h3 style="color:white;">FINAL SCORE: {st.session_state.score}</h3></div>', unsafe_allow_html=True)
    
    st.markdown("### 🏆 GALACTIC TOP ACE PILOTS")
    try:
        response = supabase.table("leaderboard").select("pilot, score").order("score", desc=True).limit(5).execute()
        if response.data:
            lb_df = pd.DataFrame(response.data)
            st.table(lb_df[['pilot', 'score']])
    except Exception:
        st.error("Comms Jammed.")

    if st.button("REBOOT FOR NEXT PILOT"):
        st.session_state.clear()
        st.rerun()

# --- 8. SYSTEM ADMIN ---
st.divider()
with st.expander("🛠️ System Admin"):
    admin_pass = st.text_input("Admin Override:", type="password")
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "endor2026"):
        st.success("Authenticated")
        st.session_state.music_on = st.checkbox("Music On/Off", value=st.session_state.music_on)
        new_speed = st.slider("Adjust Typing Speed:", 0.01, 0.20, st.session_state.typing_speed)
        if st.button("Save Settings"):
            st.session_state.typing_speed = new_speed
            st.rerun()
