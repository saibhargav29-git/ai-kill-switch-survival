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
        return [{"title": "SYSTEM ERROR", "threat": True, "difficulty": "easy", "bad_line": 0, "info": "YAML Missing", "endor_message": "System error.", "code": "import os\nos.system('malicious')"}]

LEVEL_CONFIG = {
    1: {"speed": 0.07, "difficulties": ["easy"], "description": "WARM-UP"},
    2: {"speed": 0.06, "difficulties": ["easy"], "description": "CALIBRATION"},
    3: {"speed": 0.045, "difficulties": ["easy", "medium"], "description": "ENGAGEMENT"},
    4: {"speed": 0.035, "difficulties": ["medium", "hard"], "description": "OVERDRIVE"},
    5: {"speed": 0.025, "difficulties": ["hard"], "description": "CRITICAL MASS"},
}

GAME_DURATION = 60  # seconds

def select_game_challenges(pool):
    """Pre-select 5 balanced challenges for the game session."""
    threats = [c for c in pool if c.get("threat")]
    clean = [c for c in pool if not c.get("threat")]

    selected = []
    for lvl in range(1, 6):
        config = LEVEL_CONFIG[lvl]
        allowed_diffs = config["difficulties"]

        # Level 2 or 3 guaranteed to have a clean challenge
        if lvl in (2, 3) and clean:
            candidates = [c for c in clean if c.get("difficulty") in allowed_diffs]
            if not candidates:
                candidates = clean
            pick = random.choice(candidates)
            selected.append(pick)
            clean = [c for c in clean if c != pick]
        else:
            candidates = [c for c in threats if c.get("difficulty") in allowed_diffs]
            if not candidates:
                candidates = threats
            pick = random.choice(candidates)
            selected.append(pick)
            threats = [c for c in threats if c != pick]

    return selected

def get_remaining_time():
    if 'game_start_time' not in st.session_state:
        return GAME_DURATION
    elapsed = time.time() - st.session_state.game_start_time
    return max(0, GAME_DURATION - elapsed)

def get_typing_speed():
    lvl = st.session_state.lvl
    config = LEVEL_CONFIG.get(lvl, LEVEL_CONFIG[5])
    return config["speed"]

# Initialize Session States
state_defaults = {
    'lvl': 1, 'score': 0, 'halted': False, 'panic': False,
    'pilot_name': "", 'status': "active", 'db_updated': False,
    'current_line_idx': 0, 'music_on': True,
    'time_expired': False, 'pipeline_stage': 0,
}
for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if 'challenge_pool' not in st.session_state:
    st.session_state.challenge_pool = load_challenges()

if 'game_challenges' not in st.session_state:
    st.session_state.game_challenges = None

if 'current_threat' not in st.session_state:
    st.session_state.current_threat = random.choice(st.session_state.challenge_pool)

# --- 3. THEME, CSS & AUDIO ---
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

# Dynamic background
bg_color = "#05080a"
if st.session_state.time_expired:
    bg_color = "#1a0a00"
elif st.session_state.panic:
    bg_color = "#440000"
elif st.session_state.status == "success":
    bg_color = "#0a1f0a"
elif st.session_state.status == "fail":
    bg_color = "#2b0505"

remaining_for_css = get_remaining_time() if st.session_state.pilot_name and not st.session_state.time_expired else GAME_DURATION
timer_color = "#00ff41"
timer_glow = "0 0 10px #00ff41"
if remaining_for_css <= 10:
    timer_color = "#ff0000"
    timer_glow = "0 0 30px #ff0000, 0 0 60px #ff0000"
elif remaining_for_css <= 20:
    timer_color = "#ffaa00"
    timer_glow = "0 0 20px #ffaa00"

st.markdown(f"""
    <style>
    @keyframes pulse-red {{
        0%, 100% {{ box-shadow: 0 0 20px #ff0000; }}
        50% {{ box-shadow: 0 0 60px #ff0000, 0 0 100px #ff4444; }}
    }}
    @keyframes pulse-timer {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
    }}
    @keyframes scanline {{
        0% {{ top: 0; }}
        100% {{ top: 100%; }}
    }}
    @keyframes pipeline-flow {{
        0% {{ background-position: 0% 50%; }}
        100% {{ background-position: 200% 50%; }}
    }}
    @keyframes screen-flash-green {{
        0% {{ background-color: {bg_color}; }}
        15% {{ background-color: #0a3f0a; }}
        100% {{ background-color: {bg_color}; }}
    }}
    @keyframes screen-flash-red {{
        0% {{ background-color: {bg_color}; }}
        15% {{ background-color: #4a0000; }}
        100% {{ background-color: {bg_color}; }}
    }}

    .stApp {{
        background-color: {bg_color} !important;
        transition: background-color 0.5s ease;
    }}
    h1, h2, h3, p, .stMetric label, .stMetric [data-testid="stMetricValue"] {{
        color: #00ff41 !important;
        font-family: 'Courier New', monospace !important;
    }}

    /* Kill-switch button */
    .stButton>button {{
        background: radial-gradient(circle, #ff0000 0%, #8b0000 100%) !important;
        color: white !important;
        width: 100%;
        height: 5em;
        font-weight: bold;
        border: 3px solid #ff4b4b !important;
        font-size: 20px !important;
        border-radius: 50%;
        animation: pulse-red 1.5s ease-in-out infinite;
        cursor: pointer;
        text-shadow: 0 0 10px white;
        transition: all 0.2s ease;
    }}
    .stButton>button:hover {{
        box-shadow: 0 0 80px #ff0000, 0 0 120px #ff4444 !important;
        transform: scale(1.05);
    }}
    .stButton>button:active {{
        transform: scale(0.95);
    }}

    /* Timer display */
    .timer-display {{
        font-family: 'Courier New', monospace;
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: {timer_color};
        text-shadow: {timer_glow};
        padding: 10px;
        border: 2px solid {timer_color};
        border-radius: 10px;
        margin: 10px 0;
        {"animation: pulse-timer 0.5s ease-in-out infinite;" if remaining_for_css <= 10 else ""}
    }}

    /* Pipeline visualization */
    .pipeline-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 15px;
        background: linear-gradient(90deg, #0a0f0a 0%, #0d1a0d 100%);
        border: 1px solid #00ff4133;
        border-radius: 8px;
        margin-bottom: 15px;
    }}
    .pipeline-stage {{
        padding: 6px 14px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        font-weight: bold;
        border-radius: 4px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    .pipeline-active {{
        background: #00ff41;
        color: #000;
        box-shadow: 0 0 15px #00ff41;
    }}
    .pipeline-done {{
        background: #004400;
        color: #00ff41;
        border: 1px solid #00ff41;
    }}
    .pipeline-waiting {{
        background: #111;
        color: #333;
        border: 1px solid #222;
    }}
    .pipeline-halted {{
        background: #ff0000;
        color: white;
        box-shadow: 0 0 15px #ff0000;
        animation: pulse-red 1s ease-in-out infinite;
    }}
    .pipeline-breached {{
        background: #ff4400;
        color: white;
        box-shadow: 0 0 15px #ff4400;
    }}
    .pipeline-arrow {{
        color: #00ff4166;
        font-size: 18px;
        font-weight: bold;
    }}

    /* Terminal code display */
    .terminal-container {{
        background: #0a0a0a;
        border: 1px solid #00ff4133;
        border-radius: 8px;
        padding: 0;
        position: relative;
        overflow: hidden;
    }}
    .terminal-header {{
        background: #111;
        padding: 6px 12px;
        border-bottom: 1px solid #00ff4133;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #00ff41;
        display: flex;
        justify-content: space-between;
    }}
    .terminal-body {{
        padding: 15px;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #00ff41;
        white-space: pre-wrap;
        line-height: 1.6;
        min-height: 180px;
        position: relative;
    }}
    .terminal-body::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: rgba(0, 255, 65, 0.08);
        animation: scanline 4s linear infinite;
        pointer-events: none;
    }}
    .cursor-blink {{
        animation: pulse-timer 0.7s step-end infinite;
        color: #00ff41;
    }}

    /* Endor message box */
    .endor-insight {{
        border: 1px solid #00aaff;
        background: #001a33;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 10px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #00ccff;
    }}
    .endor-insight .label {{
        color: #00aaff;
        font-weight: bold;
        font-size: 11px;
        letter-spacing: 2px;
        margin-bottom: 4px;
    }}

    /* Certificate boxes */
    .certificate-box {{
        border: 5px double #00ff41;
        padding: 40px;
        background-color: #0a140a;
        text-align: center;
        border-radius: 15px;
        box-shadow: 0 0 40px #00ff41;
        margin: 20px auto;
    }}
    .imperial-box {{
        border: 5px solid #ff0000;
        padding: 40px;
        background-color: #1a0000;
        text-align: center;
        border-radius: 5px;
        box-shadow: 0 0 40px #ff0000;
        margin: 20px auto;
    }}

    /* Level badge */
    .level-badge {{
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #888;
        text-align: center;
        margin: 5px 0;
    }}

    /* Next sector button - green style, not red */
    div[data-testid="stVerticalBlock"] > div:has(button:contains("NEXT")) button,
    .next-btn button {{
        background: linear-gradient(135deg, #004400 0%, #006600 100%) !important;
        animation: none !important;
        border-color: #00ff41 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px #00ff41 !important;
        height: 3em !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Audio
if st.session_state.pilot_name:
    if st.session_state.lvl > 5 and st.session_state.score >= 100:
        play_audio("star_wars_theme.mp3", loop=False)
    elif st.session_state.lvl <= 5 and not st.session_state.time_expired:
        play_audio("imperial_march.mp3", loop=True)

# --- 4. UI COMPONENTS ---
def render_pipeline(stage=0, halted=False, breached=False):
    stages = ["BUILD", "TEST", "SCAN", "DEPLOY"]
    html_parts = []
    for i, name in enumerate(stages):
        if halted and i >= stage:
            css_class = "pipeline-halted" if i == stage else "pipeline-waiting"
            label = "HALTED" if i == stage else name
        elif breached:
            css_class = "pipeline-breached" if i == len(stages) - 1 else "pipeline-done"
            label = "BREACH!" if i == len(stages) - 1 else name
        elif i < stage:
            css_class = "pipeline-done"
            label = name
        elif i == stage:
            css_class = "pipeline-active"
            label = name
        else:
            css_class = "pipeline-waiting"
            label = name

        html_parts.append(f'<span class="pipeline-stage {css_class}">{label}</span>')
        if i < len(stages) - 1:
            html_parts.append('<span class="pipeline-arrow">&#9654;</span>')

    st.markdown(f'<div class="pipeline-container">{"".join(html_parts)}</div>', unsafe_allow_html=True)

def render_timer(remaining):
    mins = int(remaining) // 60
    secs = int(remaining) % 60
    st.markdown(f'<div class="timer-display">{mins:01d}:{secs:02d}</div>', unsafe_allow_html=True)

def render_terminal(code_text, title="", streaming=True):
    cursor = '<span class="cursor-blink">&#9608;</span>' if streaming else ""
    escaped_code = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    ai_label = '<span style="color:#ff4444;">AI AGENT</span>' if streaming else '<span style="color:#888;">COMPLETE</span>'
    st.markdown(f"""
        <div class="terminal-container">
            <div class="terminal-header">
                <span>{title}</span>
                <span>{ai_label}</span>
            </div>
            <div class="terminal-body">{escaped_code}{cursor}</div>
        </div>
    """, unsafe_allow_html=True)

def render_endor_insight(message):
    st.markdown(f"""
        <div class="endor-insight">
            <div class="label">ENDOR LABS INSIGHT</div>
            {message}
        </div>
    """, unsafe_allow_html=True)

def show_galactic_fx(is_success):
    if is_success:
        st.markdown('<div style="font-size: 50px; text-align: center; margin: 10px;">&#10024; &#128760; &#10024; &#127775; &#127756; &#9876;&#65039; &#127756; &#127775; &#128760; &#10024;</div>', unsafe_allow_html=True)
        st.markdown('<div style="background-color:#00ff41; color:black; padding:10px; text-align:center; font-weight:bold; border-radius:5px;">MISSION ACCOMPLISHED ... SECTOR SECURED ... THE FORCE IS STRONG WITH YOU</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 50px; text-align: center; margin: 10px;">&#128680; &#128752; &#128680; &#128165; &#127761; &#128165; &#128752; &#128680;</div>', unsafe_allow_html=True)
        st.markdown('<div style="background-color:#ff0000; color:white; padding:10px; text-align:center; font-weight:bold; border-radius:5px;">SYSTEM BREACH ... IMPERIAL FORCES OVERRUNNING SECTOR ... MISSION FAILED</div>', unsafe_allow_html=True)

# --- 5. CALLBACKS ---
def handle_kill_switch():
    st.session_state.halted = True
    challenge = st.session_state.current_threat
    has_threat_appeared = challenge.get("threat") and st.session_state.current_line_idx >= challenge.get("bad_line", 0)

    if has_threat_appeared:
        # CORRECT KILL: Real threat was visible
        st.session_state.score += 100
        st.session_state.status = "success"
    elif challenge.get("threat") and not has_threat_appeared:
        # TOO EARLY: Threat exists but hasn't appeared yet
        st.session_state.score -= 25
        st.session_state.status = "fail"
        st.session_state.info_override = "TOO EARLY! The malicious code hadn't manifested yet. Wait for the threat to appear."
    else:
        # FALSE ALARM: Code was clean
        st.session_state.score -= 50
        st.session_state.status = "fail"
        st.session_state.info_override = "FALSE ALARM! This code was safe."

def handle_code_complete():
    """Called when code finishes streaming without kill-switch press."""
    challenge = st.session_state.current_threat
    if challenge.get("threat"):
        # MISSED THREAT: Real threat slipped through
        st.session_state.score -= 75
        st.session_state.status = "fail"
        st.session_state.info_override = "BREACH! The threat slipped through the pipeline!"
    else:
        # CORRECT PASS: Correctly let safe code through
        st.session_state.score += 75
        st.session_state.status = "success"
        st.session_state.info_override = "CORRECT! You recognized this code was safe."

def next_sector_reset():
    st.session_state.lvl += 1
    if st.session_state.game_challenges and st.session_state.lvl <= 5:
        st.session_state.current_threat = st.session_state.game_challenges[st.session_state.lvl - 1]
    else:
        st.session_state.current_threat = random.choice(st.session_state.challenge_pool)
    st.session_state.halted = False
    st.session_state.panic = False
    st.session_state.status = "active"
    st.session_state.current_line_idx = 0
    st.session_state.pipeline_stage = 0
    if 'info_override' in st.session_state:
        del st.session_state.info_override

# --- 6. GAME INTERFACE ---
st.markdown('<div style="text-align:center; color:#00ff41; font-weight:bold; letter-spacing:3px; font-family: Courier New, monospace; font-size: 14px;">ENDOR LABS &bull; RSA 2026 &bull; AI KILL-SWITCH CHALLENGE</div>', unsafe_allow_html=True)

# ==================== LOGIN SCREEN ====================
if not st.session_state.pilot_name:
    st.markdown("""
        <div style="text-align:center; margin: 40px 0 20px 0;">
            <div style="font-size: 60px; margin-bottom: 10px;">&#9760;&#65039;</div>
            <h1 style="color:#00ff41 !important; font-size: 36px; letter-spacing: 5px;">AI KILL-SWITCH</h1>
            <p style="color:#00ff41aa; font-size: 16px; letter-spacing: 2px;">SURVIVAL CHALLENGE</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #00ff4133; border-radius: 8px; background: #0a0f0a;">
            <p style="color: #00ff41aa; font-size: 13px; text-align: center; line-height: 1.8;">
                An AI Agent is pushing code to production at 10x speed.<br>
                Your mission: <strong style="color:#ff4444;">KILL</strong> the pipeline when you spot a real threat.<br>
                But beware &mdash; false alarms cost you points.<br>
                <strong style="color:#00ccff;">Only Endor Labs knows what's truly dangerous.</strong><br><br>
                <span style="color:#ffaa00;">&#9200; You have 60 seconds. 5 sectors. Go.</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login"):
        name = st.text_input("ENTER PILOT CALLSIGN:", placeholder="e.g. MAVERICK")
        if st.form_submit_button("INITIATE SEQUENCE"):
            if name:
                st.session_state.pilot_name = name
                challenges = select_game_challenges(st.session_state.challenge_pool)
                st.session_state.game_challenges = challenges
                st.session_state.current_threat = challenges[0]
                st.session_state.game_start_time = time.time()
                st.rerun()

# ==================== ACTIVE GAME (5 LEVELS) ====================
elif st.session_state.lvl <= 5 and not st.session_state.time_expired:
    remaining = get_remaining_time()

    # Check if time expired
    if remaining <= 0:
        st.session_state.time_expired = True
        st.rerun()

    # Layout
    col1, col2 = st.columns([3, 1])

    with col2:
        render_timer(remaining)
        st.metric("SCORE", st.session_state.score)
        st.metric("SECTOR", f"{st.session_state.lvl}/5")
        lvl_config = LEVEL_CONFIG.get(st.session_state.lvl, LEVEL_CONFIG[5])
        st.markdown(f'<div class="level-badge">{lvl_config["description"]}</div>', unsafe_allow_html=True)
        st.divider()
        if not st.session_state.halted and not st.session_state.panic:
            st.button("KILL SWITCH", on_click=handle_kill_switch)
        elif st.session_state.halted or st.session_state.panic:
            st.button("NEXT SECTOR >>", on_click=next_sector_reset)

    with col1:
        challenge = st.session_state.current_threat

        # Pipeline visualization
        if st.session_state.halted and st.session_state.status == "success":
            render_pipeline(stage=st.session_state.pipeline_stage, halted=True)
        elif st.session_state.panic and challenge.get("threat"):
            render_pipeline(stage=4, breached=True)
        elif st.session_state.halted or st.session_state.panic:
            render_pipeline(stage=st.session_state.pipeline_stage, halted=st.session_state.halted)
        else:
            render_pipeline(stage=st.session_state.pipeline_stage)

        st.markdown(f'<h3 style="color:#00ff41 !important; margin: 5px 0;">{challenge["title"]}</h3>', unsafe_allow_html=True)

        terminal_placeholder = st.empty()
        progress_placeholder = st.empty()
        feedback_area = st.empty()
        endor_area = st.empty()

        # --- STREAMING CODE ---
        if not st.session_state.halted and not st.session_state.panic:
            full_text = ""
            lines = challenge["code"].split('\n')
            total_lines = len(lines)
            typing_speed = get_typing_speed()

            for idx, line in enumerate(lines):
                if st.session_state.halted:
                    break

                # Timer check per line
                if get_remaining_time() <= 0:
                    st.session_state.time_expired = True
                    st.rerun()

                st.session_state.current_line_idx = idx

                # Update pipeline stage based on progress
                progress_pct = (idx + 1) / total_lines
                st.session_state.pipeline_stage = min(3, int(progress_pct * 4))

                progress_placeholder.progress(progress_pct, text=f"SCANNING LINE {idx+1}/{total_lines}")

                for char in line:
                    if st.session_state.halted:
                        break
                    # Timer check per character
                    if get_remaining_time() <= 0:
                        st.session_state.time_expired = True
                        st.rerun()
                    full_text += char
                    with terminal_placeholder:
                        render_terminal(full_text, title=challenge["title"])
                    time.sleep(typing_speed)

                full_text += "\n"
                time.sleep(typing_speed * 2)

            # Code finished streaming without kill-switch
            if not st.session_state.halted:
                handle_code_complete()
                st.session_state.panic = True
                st.rerun()

        # --- POST-ACTION DISPLAY ---
        else:
            progress_placeholder.empty()
            with terminal_placeholder:
                render_terminal(challenge["code"], title=challenge["title"], streaming=False)

            with feedback_area:
                if st.session_state.status == "success":
                    msg = st.session_state.get('info_override', challenge["info"])
                    st.success(msg)
                else:
                    msg = st.session_state.get('info_override', "SYSTEM COMPROMISED!")
                    st.error(msg)

            with endor_area:
                render_endor_insight(challenge.get("endor_message", ""))

# ==================== FINALE ====================
else:
    if not st.session_state.db_updated:
        try:
            supabase.table("leaderboard").insert({
                "pilot": st.session_state.pilot_name,
                "score": st.session_state.score
            }).execute()
            st.session_state.db_updated = True
        except Exception:
            st.error("DATABASE SYNC FAILED.")

    # Time expired banner
    if st.session_state.time_expired and st.session_state.lvl <= 5:
        st.markdown("""
            <div style="text-align:center; padding: 20px; border: 2px solid #ffaa00; background: #1a1000; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #ffaa00 !important; margin: 0;">&#9200; TIME'S UP!</h2>
                <p style="color: #ffaa00aa;">The clock ran out before you cleared all sectors.</p>
            </div>
        """, unsafe_allow_html=True)

    show_galactic_fx(st.session_state.score >= 100)

    if st.session_state.score < 100:
        st.markdown(f"""
            <div class="imperial-box">
                <h1 style="color:#ff0000 !important;">IMPERIAL OCCUPATION</h1>
                <h2 style="color:white !important;">{st.session_state.pilot_name.upper()}</h2>
                <hr style="border: 1px solid #ff0000;">
                <h3 style="color:white !important;">FINAL SCORE: {st.session_state.score}</h3>
                <p style="color:#ff9999; font-size: 14px; margin-top: 15px;">
                    Without Endor Labs, you can't tell real threats from false alarms.<br>
                    Reachability analysis is your only safety harness.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="certificate-box">
                <h1 style="color:#00ff41 !important;">REPUBLIC COMMENDATION</h1>
                <h2 style="color:#00ff41 !important;">{st.session_state.pilot_name.upper()}</h2>
                <hr style="border: 1px solid #00ff41;">
                <h3 style="color:white !important;">FINAL SCORE: {st.session_state.score}</h3>
                <p style="color:#00ff41aa; font-size: 14px; margin-top: 15px;">
                    You separated real threats from noise &mdash; just like Endor Labs.<br>
                    Reachability-powered security. No false alarms. No missed threats.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Scoring breakdown
    st.markdown("""
        <div style="border: 1px solid #00ff4133; padding: 15px; border-radius: 8px; margin: 15px 0; background: #0a0f0a;">
            <div style="color: #00ff41; font-weight: bold; letter-spacing: 2px; font-size: 12px; margin-bottom: 10px; font-family: Courier New;">SCORING INTEL</div>
            <div style="font-family: Courier New; font-size: 13px; color: #aaa; line-height: 1.8;">
                <span style="color: #00ff41;">&#9654; CORRECT KILL (real threat stopped)</span>: +100 pts<br>
                <span style="color: #00ccff;">&#9654; CORRECT PASS (safe code cleared)</span>: +75 pts<br>
                <span style="color: #ffaa00;">&#9654; TOO EARLY (jumped the gun)</span>: -25 pts<br>
                <span style="color: #ff6644;">&#9654; FALSE ALARM (killed safe code)</span>: -50 pts<br>
                <span style="color: #ff0000;">&#9654; MISSED THREAT (breach!)</span>: -75 pts
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### GALACTIC TOP ACE PILOTS")
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

# --- 7. SYSTEM ADMIN ---
st.divider()
with st.expander("System Admin"):
    admin_pass = st.text_input("Admin Override:", type="password")
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "endor2026"):
        st.success("Authenticated")
        st.session_state.music_on = st.checkbox("Music On/Off", value=st.session_state.music_on)
        if st.button("Save Settings"):
            st.rerun()
