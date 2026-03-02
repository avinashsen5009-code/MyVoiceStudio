import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- 1. CORE SYSTEM CONFIG ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

# --- 2. THEME ENGINE (Feature: 3D Neumorphic & Theme Switcher) ---
if 'theme' not in st.session_state: st.session_state.theme = "Cyber 3D Gold 🧊"
if 'history' not in st.session_state: st.session_state.history = []

def apply_ui(theme):
    if theme == "Cyber 3D Gold 🧊":
        bg, acc, card = "#0f172a", "#fbbf24", "rgba(30, 41, 59, 0.8)"
    elif theme == "Anime Pastel 🌸":
        bg, acc, card = "#fff5f7", "#f06292", "rgba(255, 255, 255, 0.9)"
    else:
        bg, acc, card = "#f8fafc", "#1e40af", "#ffffff"
    
    st.markdown(f"""
    <style>
    .main {{ background: {bg}; color: white; font-family: 'Inter'; }}
    div[data-testid="column"] > div {{
        background: {card} !important; backdrop-filter: blur(15px);
        border-radius: 25px; padding: 30px; border: 1px solid {acc}33;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.5); margin-bottom: 20px;
    }}
    .stButton>button {{
        background: linear-gradient(90deg, {acc}, #f59e0b); color: black !important;
        font-weight: 900; border-radius: 12px; height: 60px; border: none; width: 100%;
    }}
    .stTextArea textarea {{ background: #000 !important; color: {acc} !important; border-radius: 15px; }}
    </style>
    """, unsafe_allow_html=True)

apply_ui(st.session_state.theme)

# --- 3. AI ENGINE (Feature: Quantum Rendering) ---
@st.cache_resource
def load_engine():
    try:
        m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
        v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
        return Kokoro(m, v)
    except Exception as e:
        st.error(f"Engine Error: {e}")
        return None

kokoro = load_engine()

# --- 4. TRIPLE MONITOR LAYOUT ---
l, m, r = st.columns([1, 1.5, 1])

with l:
    st.subheader("🛡️ GUARDIAN")
    # Feature: Local Image Integration
    img_file = st.file_uploader("Upload Gojo Image", type=['jpg','png','jpeg'])
    if img_file: st.image(img_file, use_container_width=True)
    else: st.info("Upload Gojo image to see him!")
    
    st.session_state.theme = st.selectbox("THEME", ["Cyber 3D Gold 🧊", "Anime Pastel 🌸", "Minimalist Pro 💼"])
    
    # Feature: 12+ Voices
    VOICES = {"am_onyx":"Onyx (Deep)","af_sky":"Sky (Anime)","am_adam":"Adam (Movie)","am_fenrir":"Fenrir (Gravelly)","af_heart":"Heart (Soft)","am_michael":"Michael (Pro)"}
    
    # Feature: Gojo Fusion Mixing
    mode = st.radio("MODE", ["Solo", "Gojo Fusion (0.75)"])
    v_id = st.selectbox("VOICE", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    speed = st.slider("SPEED", 0.5, 2.0, 1.0)

with m:
    st.subheader("📝 SCRIPT MASTER")
    text = st.text_area("", placeholder="Speak your command...", height=400)
    
    if st.button("🚀 INITIATE GENERATION"):
        if text.strip() and kokoro:
            with st.spinner("Synthesizing..."):
                # Fusion Logic
                if mode == "Gojo Fusion (0.75)":
                    s1, s2 = kokoro.get_voice_style("am_onyx"), kokoro.get_voice_style("af_sky")
                    style = (s1 * 0.7) + (s2 * 0.3)
                    samples, sr = kokoro.create(text, voice=style, speed=speed, lang="en-us")
                else:
                    samples, sr = kokoro.create(text, voice=v_id, speed=speed, lang="en-us")
                
                # Audio Export (Feature #10)
                buf = io.BytesIO()
                sf.write(buf, samples, sr, format='WAV')
                dur = len(samples)/sr
                
                # SRT Generation (Feature #6)
                srt = f"1\n00:00:00,000 --> 00:00:{int(dur):02},000\n{text}"
                
                st.session_state.current = {"wav": buf.getvalue(), "srt": srt, "dur": dur}
                st.session_state.history.append({"text": text[:20], "time": datetime.now().strftime("%H:%M")})

with r:
    st.subheader("🎧 MONITOR")
    if 'current' in st.session_state:
        st.audio(st.session_state.current['wav'])
        st.success(f"Duration: {st.session_state.current['dur']:.2f}s")
        st.download_button("📥 DOWNLOAD WAV", st.session_state.current['wav'], "master.wav")
        st.download_button("📜 DOWNLOAD SRT", st.session_state.current['srt'], "subs.srt")
    
    st.subheader("🕒 HISTORY")
    for h in st.session_state.history[-5:]:
        st.caption(f"✅ {h['time']} - {h['text']}...")