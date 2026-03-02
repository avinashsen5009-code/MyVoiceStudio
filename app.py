import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- 1. CORE SYSTEM & ERROR HANDLING ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

# Initializing Session States to prevent "Variable Not Found" errors
if 'history' not in st.session_state: st.session_state.history = []
if 'theme' not in st.session_state: st.session_state.theme = "Cyber 3D Gold 🧊"
if 'last_audio' not in st.session_state: st.session_state.last_audio = None

# --- 2. 3D NEUMORPHIC UI ENGINE ---
def apply_3d_ui(theme):
    if theme == "Cyber 3D Gold 🧊":
        bg, acc, card, txt = "#0f172a", "#fbbf24", "rgba(30, 41, 59, 0.8)", "#f8fafc"
    elif theme == "Anime Pastel 🌸":
        bg, acc, card, txt = "#fff5f7", "#f06292", "rgba(255, 255, 255, 0.9)", "#4a148c"
    else: # Minimalist Pro
        bg, acc, card, txt = "#f8fafc", "#1e40af", "#ffffff", "#1e293b"
    
    st.markdown(f"""
    <style>
    .main {{ background: {bg}; color: {txt}; }}
    /* 3D Glass Cards */
    div[data-testid="column"] > div {{
        background: {card} !important; backdrop-filter: blur(15px);
        border-radius: 20px; padding: 25px; border: 1px solid {acc}33;
        box-shadow: 12px 12px 35px rgba(0,0,0,0.5); margin-bottom: 20px;
    }}
    /* Pro Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {acc}, #f59e0b); color: black !important;
        font-weight: 900; border-radius: 12px; height: 60px; border: none; width: 100%;
        box-shadow: 0 4px 15px {acc}44; transition: 0.2s;
    }}
    .stButton>button:active {{ transform: scale(0.98); }}
    /* Cyber Input */
    .stTextArea textarea {{ background: #000 !important; color: {acc} !important; border: 1px solid {acc} !important; }}
    </style>
    """, unsafe_allow_html=True)

apply_3d_ui(st.session_state.theme)

# --- 3. FAIL-SAFE ENGINE LOADER ---
@st.cache_resource(show_spinner=False)
def get_engine():
    try:
        m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
        v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
        return Kokoro(m, v)
    except Exception as e:
        st.error(f"Engine Connection Failed: {e}")
        return None

# --- 4. PRODUCTION FEATURES ---
def generate_srt(text, dur):
    words = text.split()
    if not words: return ""
    time_per_word = dur / len(words)
    srt_lines = []
    for i, word in enumerate(words):
        start = i * time_per_word
        end = (i + 1) * time_per_word
        fmt = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},000"
        srt_lines.append(f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{word}\n")
    return "\n".join(srt_lines)

# --- 5. TRIPLE MONITOR INTERFACE ---
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("🛡️ GUARDIAN")
    # FAIL-SAFE IMAGE: Works if local file exists, otherwise provides a button
    try:
        st.image("gojo.jpg", use_container_width=True)
    except:
        uploaded_file = st.file_uploader("🖼️ Upload Gojo Image", type=['jpg','png','jpeg'])
        if uploaded_file: st.image(uploaded_file, use_container_width=True)
        else: st.warning("Please place 'gojo.jpg' in the folder or upload one.")

    st.session_state.theme = st.selectbox("ACTIVE THEME", ["Cyber 3D Gold 🧊", "Anime Pastel 🌸", "Minimalist Pro 💼"])
    
    st.markdown("---")
    # Feature: 12+ Professional Voices
    VOICES = {
        "am_onyx": "🌑 Onyx (Deep)", "af_sky": "🎭 Sky (Anime)", 
        "af_bella": "🎙️ Bella (News)", "am_adam": "🎬 Adam (Movie)",
        "am_michael": "👨‍🏫 Michael (Pro)", "am_fenrir": "🐺 Fenrir (Villain)",
        "af_heart": "💖 Heart (Soft)", "af_sarah": "✨ Sarah (Gentle)",
        "af_nicole": "📖 Nicole (Narrator)", "af_aoede": "🎶 Aoede (Melodic)",
        "am_puck": "⚡ Puck (Fast)", "af_alloy": "🛡️ Alloy (Guardian)"
    }
    
    # Feature: Gojo Fusion Mix
    mode = st.radio("SYNTHESIS MODE", ["Standard", "Gojo Fusion (Pro Mix)"])
    v_id = st.selectbox("VOICE IDENTITY", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    speed = st.slider("SPEECH TEMPO", 0.5, 2.0, 1.0)

with m:
    st.subheader("📝 SCRIPT MASTER")
    script = st.text_area("", placeholder="Command me, Master Avinash...", height=400, label_visibility="collapsed")
    
    if st.button("🚀 INITIATE QUANTUM RENDER"):
        if script.strip():
            engine = get_engine()
            if engine:
                with st.spinner("SYNETHESIZING VOID..."):
                    # Feature: Gojo Fusion Logic (0.75 mix)
                    if mode == "Gojo Fusion (Pro Mix)":
                        s1 = engine.get_voice_style("am_onyx")
                        s2 = engine.get_voice_style("af_sky")
                        blend = (s1 * 0.75) + (s2 * 0.25)
                        samples, sr = engine.create(script, voice=blend, speed=speed, lang="en-us")
                    else:
                        samples, sr = engine.create(script, voice=v_id, speed=speed, lang="en-us")
                    
                    # Convert to Audio Data
                    buf = io.BytesIO()
                    sf.write(buf, samples, sr, format='WAV')
                    audio_bytes = buf.getvalue()
                    duration = len(samples)/sr
                    
                    # Store in Session State
                    st.session_state.last_audio = {
                        "wav": audio_bytes,
                        "srt": generate_srt(script, duration),
                        "dur": duration,
                        "text": script[:30] + "..."
                    }
                    # Feature: History Log
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M"), "script": script[:20]+"..."})

with r:
    st.subheader("🎧 MONITOR")
    if st.session_state.last_audio:
        curr = st.session_state.last_audio
        st.audio(curr['wav'], format="audio/wav")
        st.success(f"ONLINE | {curr['dur']:.2f}s")
        
        # Feature: One-Click Master Export
        st.download_button("📥 WAV MASTER", curr['wav'], f"voice_{int(time.time())}.wav")
        # Feature: Pro SRT Export
        st.download_button("📜 SRT SUBS", curr['srt'], f"subs_{int(time.time())}.srt")
    else:
        st.info("Awaiting Signal...")

    st.subheader("🕒 HISTORY")
    for item in st.session_state.history[-5:]:
        st.caption(f"✅ {item['time']} - {item['script']}")