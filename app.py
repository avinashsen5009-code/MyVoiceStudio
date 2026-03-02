import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- 1. SETTINGS & TRIPLE-MONITOR CONFIG ---
st.set_page_config(page_title="AVINASH SEN VOICE STUDIO", page_icon="💎", layout="wide")

# --- 2. DYNAMIC THEME SWITCHER (FEATURE #5) ---
if 'theme' not in st.session_state:
    st.session_state.theme = "Cyber 3D Gold 🧊"

def apply_theme(theme_choice):
    if theme_choice == "Cyber 3D Gold 🧊":
        bg = "radial-gradient(circle at center, #0f172a 0%, #020617 100%)"
        accent = "#fbbf24"; card = "rgba(30, 41, 59, 0.75)"; text = "#f8fafc"
    elif theme_choice == "Anime Pastel 🌸":
        bg = "linear-gradient(135deg, #fce4ec 0%, #e1f5fe 100%)"
        accent = "#f06292"; card = "rgba(255, 255, 255, 0.8)"; text = "#4a148c"
    else: # Minimalist Pro
        bg = "#f8fafc"; accent = "#1e40af"; card = "#ffffff"; text = "#1e293b"

    # FEATURE #2: 3D NEUMORPHIC UI CSS
    st.markdown(f"""
    <style>
    .main {{ background: {bg}; color: {text}; font-family: 'Inter', sans-serif; }}
    div[data-testid="column"] > div {{
        background: {card} !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px !important;
        padding: 2.5rem !important;
        box-shadow: 20px 20px 60px rgba(0,0,0,0.5), -5px -5px 20px rgba(255,255,255,0.05);
        margin-bottom: 2rem;
    }}
    h1, h2, h3 {{ color: {accent}; text-transform: uppercase; letter-spacing: 3px; font-weight: 900; }}
    .stButton>button {{
        width: 100%; background: linear-gradient(135deg, {accent} 0%, #f59e0b 100%);
        color: #000 !important; font-weight: 900; border-radius: 15px; height: 65px;
        box-shadow: 0 6px 0 rgba(0,0,0,0.3); border: none; transition: 0.1s;
    }}
    .stButton>button:active {{ transform: translateY(4px); box-shadow: 0 1px 0 transparent; }}
    .stTextArea textarea {{ background: #000 !important; color: {accent} !important; border-radius: 15px !important; border: 2px solid {accent}44 !important; font-size: 1.1rem; }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# --- 3. QUANTUM RENDER ENGINE (FEATURE #8) ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

# FEATURE #6: PRO SRT GENERATOR
def create_srt(text, duration):
    words = text.split()
    if not words: return ""
    per_word = duration / len(words)
    srt_content = ""
    for i, word in enumerate(words):
        start = i * per_word
        end = (i + 1) * per_word
        fmt = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},000"
        srt_content += f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{word}\n\n"
    return srt_content

kokoro = load_engine()

# --- 4. TRIPLE-MONITOR LAYOUT (FEATURE #4) ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1])

# --- MONITOR 1: CONTROLS ---
with col_left:
    st.subheader("🛡️ STUDIO CONTROL")
    
    # FEATURE #3: LOCAL IMAGE INTEGRATION
    try:
        st.image("gojo.jpg", use_container_width=True)
    except:
        st.warning("Place 'gojo.jpg' in the folder to see Gojo!")
        st.image("https://raw.githubusercontent.com/leonelhs/kokoro-thewh1teagle/main/media/gojo_monitor_v1.png", use_container_width=True)

    st.session_state.theme = st.selectbox("ENVIRONMENT", ["Cyber 3D Gold 🧊", "Anime Pastel 🌸", "Minimalist Pro 💼"])
    
    # FEATURE #7: 12+ HIGH-FIDELITY VOICES
    VOICES = {
        "am_onyx": "🌑 Onyx (Deep/Gojo)", "af_sky": "🎭 Sky (Anime/Edge)", 
        "af_bella": "🎙️ Bella (Professional)", "am_adam": "🎬 Adam (Movie)",
        "af_heart": "💖 Heart (Soft)", "am_fenrir": "🐺 Fenrir (Gravelly)",
        "am_michael": "👨‍🏫 Michael (Narrator)", "af_sarah": "✨ Sarah (Gentle)",
        "af_nicole": "📖 Nicole", "af_aoede": "🎶 Aoede", "am_puck": "⚡ Puck", "af_alloy": "🛡️ Alloy"
    }

    # FEATURE #1: GOJO FUSION ENGINE
    mode = st.radio("VOICE ARCHITECTURE", ["Standard Persona", "Gojo Fusion Mix"])
    if mode == "Standard Persona":
        v_id = st.selectbox("IDENTITY", list(VOICES.keys()), format_func=lambda x: VOICES[x])
        speed = st.slider("TEMPO CONTROL", 0.5, 2.0, 1.0) # FEATURE #9
    else:
        st.info("Mixing Onyx (Base) + Sky (Target) at 0.75 for Gojo")
        v1 = "am_onyx"; v2 = "af_sky"
        mix_ratio = st.slider("Fusion Ratio", 0.0, 1.0, 0.75)
        speed = st.slider("TEMPO CONTROL", 0.5, 2.0, 1.05)

# --- MONITOR 2: SCRIPTING ---
with col_mid:
    st.subheader("📝 SCRIPTING CONSOLE")
    script_text = st.text_area("", placeholder="Enter your script, Master Avinash...", height=480, label_visibility="collapsed")
    
    if st.button("🚀 INITIATE DOMAIN EXPANSION"):
        if script_text.strip() and kokoro:
            start_time = time.time()
            with st.spinner("QUANTUM RENDERING..."):
                if mode == "Standard Persona":
                    samples, sr = kokoro.create(script_text, voice=v_id, speed=speed, lang="en-us")
                else:
                    s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(v2)
                    blend = (s1 * (1 - mix_ratio)) + (s2 * mix_ratio)
                    samples, sr = kokoro.create(script_text, voice=blend, speed=speed, lang="en-us")
                
                buf = io.BytesIO()
                sf.write(buf, samples, sr, format='WAV')
                render_time = time.time() - start_time
                st.session_state.prod = (buf.getvalue(), len(samples)/sr, script_text, render_time)

# --- MONITOR 3: PRODUCTION ---
with col_right:
    st.subheader("🎧 MONITOR")
    if 'prod' in st.session_state:
        aud, dur, txt, r_time = st.session_state.prod
        st.audio(aud, format="audio/wav")
        st.success(f"RENDERED IN {r_time:.2f}s")
        st.info(f"DURATION: {dur:.2f}s")
        
        # FEATURE #10: ONE-CLICK MASTER EXPORT
        st.markdown("### 📥 EXPORT HUB")
        st.download_button("WAV MASTER 📥", aud, f"master_{int(time.time())}.wav")
        
        # FEATURE #6: SRT DOWNLOAD
        srt_data = create_srt(txt, dur)
        st.download_button("SRT SUBS 📜", srt_data, f"subs_{int(time.time())}.srt")
    else:
        st.info("SYSTEM IDLE: AWAITING SIGNAL")

    st.markdown("---")
    st.markdown("### 📊 STUDIO LOG")
    st.caption(f"Session Active: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("Engine: Kokoro ONNX v1.0")