import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- 1. CORE STUDIO CONFIGURATION ---
st.set_page_config(page_title="AVINASH SEN VOICE STUDIO", page_icon="💎", layout="wide")

# --- 2. DYNAMIC THEME ENGINE (3D NEUMORPHIC) ---
if 'theme' not in st.session_state:
    st.session_state.theme = "Cyber 3D Gold 🧊"

def apply_theme(theme_choice):
    if theme_choice == "Cyber 3D Gold 🧊":
        bg = "radial-gradient(circle at center, #0f172a 0%, #020617 100%)"
        accent = "#fbbf24"; card = "rgba(30, 41, 59, 0.7)"; text = "#f8fafc"
    elif theme_choice == "Anime Pastel 🌸":
        bg = "linear-gradient(135deg, #fce4ec 0%, #e1f5fe 100%)"
        accent = "#f06292"; card = "rgba(255, 255, 255, 0.8)"; text = "#4a148c"
    else: # Minimalist Pro
        bg = "#f8fafc"; accent = "#1e40af"; card = "#ffffff"; text = "#1e293b"

    st.markdown(f"""
    <style>
    .main {{ background: {bg}; color: {text}; font-family: 'Inter', sans-serif; }}
    div[data-testid="column"] > div {{
        background: {card} !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 1.5rem;
    }}
    h1, h2, h3 {{ color: {accent}; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }}
    .stButton>button {{
        width: 100%; background: linear-gradient(135deg, {accent} 0%, #f59e0b 100%);
        color: #000 !important; font-weight: 800; border-radius: 12px; height: 55px;
        box-shadow: 0 4px 0 rgba(0,0,0,0.3); transition: 0.1s; border: none;
    }}
    .stButton>button:active {{ transform: translateY(4px); box-shadow: 0 0px 0 transparent; }}
    .stTextArea textarea {{ background: #000 !important; color: {accent} !important; border-radius: 12px !important; border: 1px solid {accent}33 !important; }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# --- 3. ENGINE & SRT UTILITIES ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

def generate_srt(text, dur):
    words = text.split(); srt = ""
    if not words: return ""
    step = dur / len(words)
    for i, w in enumerate(words):
        s, e = i * step, (i+1) * step
        f = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},000"
        srt += f"{i+1}\n{f(s)} --> {f(e)}\n{w}\n\n"
    return srt

kokoro = load_engine()

# --- 4. PRODUCTION LAYOUT ---
st.title("💎 AVINASH SEN VOICE STUDIO")
st.caption("DOMAIN EXPANSION • MASTER PRODUCTION SUITE v9.0")

l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("🛡️ GUARDIAN")
    # YOUR GOJO IMAGE LINK (Direct Proxy for Google Shared Link)
    gojo_url = "https://share.google/images/liqR9LBTTIuszTpXt"
    st.image(gojo_url, caption="SATORU GOJO | THE STRONGEST", use_container_width=True)
    
    st.session_state.theme = st.selectbox("ACTIVE THEME", ["Cyber 3D Gold 🧊", "Anime Pastel 🌸", "Minimalist Pro 💼"])
    
    VOICES = {
        "af_bella": "🎙️ Bella (Pro)", "af_sarah": "✨ Sarah (Soft)", "af_sky": "🎭 Sky (Anime)",
        "af_heart": "💖 Heart (Kind)", "am_adam": "🎬 Adam (Movie)", "am_onyx": "🌑 Onyx (Deep)",
        "am_michael": "👨‍🏫 Michael (Pro)", "am_fenrir": "🐺 Fenrir (Gravelly)"
    }
    
    mode = st.radio("SYNTHESIS MODE", ["Solo Persona", "Vocal Fusion (Mix)"])
    if mode == "Solo Persona":
        v_id = st.selectbox("IDENTITY", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    else:
        v1 = st.selectbox("Base Soul", list(VOICES.keys()), index=5) # Onyx
        v2 = st.selectbox("Target Soul", list(VOICES.keys()), index=2) # Sky
        ratio = st.slider("Mix Ratio", 0.0, 1.0, 0.7)
    
    speed = st.slider("TEMPO CONTROL", 0.5, 2.0, 1.0)

with m:
    st.subheader("📜 SCRIPT MASTER")
    text = st.text_area("", placeholder="Speak your truth, Master Avinash...", height=400, label_visibility="collapsed")
    
    if st.button("🚀 INITIATE QUANTUM RENDER"):
        if text.strip() and kokoro:
            with st.spinner("EXPANDING VOID..."):
                if mode == "Solo Persona":
                    samples, sr = kokoro.create(text, voice=v_id, speed=speed, lang="en-us")
                    vn = v_id
                else:
                    s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(v2)
                    blend = (s1 * (1 - ratio)) + (s2 * ratio)
                    samples, sr = kokoro.create(text, voice=blend, speed=speed, lang="en-us")
                    vn = f"Fusion({v1}/{v2})"
                
                buf = io.BytesIO()
                sf.write(buf, samples, sr, format='WAV')
                st.session_state.prod = (buf.getvalue(), vn, len(samples)/sr, generate_srt(text, len(samples)/sr))

with r:
    st.subheader("🎧 MONITOR")
    if 'prod' in st.session_state:
        aud, vn, dur, srt = st.session_state.prod
        st.audio(aud, format="audio/wav")
        st.success(f"ONLINE | {vn} | {dur:.2f}s")
        st.download_button("📥 WAV MASTER", aud, f"master_{int(time.time())}.wav")
        st.download_button("📜 SRT SUBS", srt, f"subs_{int(time.time())}.srt")
    else:
        st.info("AWAITING SIGNAL...")

    st.markdown("### 📊 PRO MIX GUIDE")
    st.table({
        "Output Goal": ["Gojo", "News Anchor", "Narrator", "Protagonist"],
        "Mix / Voice": ["Onyx 70% + Sky 30%", "Bella 100%", "Michael 100%", "Sky 100%"],
        "Tempo": ["1.05x", "1.0x", "0.9x", "1.1x"]
    })