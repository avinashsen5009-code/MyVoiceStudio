import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import re
import time
from datetime import datetime

# --- 1. CORE CONFIG & THEME ENGINE ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

# Initialize Session States
if 'history' not in st.session_state: st.session_state.history = []
if 'last_audio' not in st.session_state: st.session_state.last_audio = None
if 'active_theme' not in st.session_state: st.session_state.active_theme = "Cyber 3D Gold 🧊"

def apply_custom_theme():
    theme = st.session_state.active_theme
    if theme == "Cyber 3D Gold 🧊":
        bg, acc, card, txt = "#0f172a", "#fbbf24", "rgba(30, 41, 59, 0.8)", "#f8fafc"
    elif theme == "Anime Pastel 🌸":
        bg, acc, card, txt = "#fff5f7", "#f06292", "rgba(255, 255, 255, 0.9)", "#4a148c"
    else: # Minimalist Pro
        bg, acc, card, txt = "#f8fafc", "#1e40af", "#ffffff", "#1e293b"
    
    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: {txt}; }}
    [data-testid="stVerticalBlock"] > div:has(div.stColumn) > div {{
        background: {card} !important; backdrop-filter: blur(15px);
        border-radius: 20px; padding: 25px; border: 1px solid {acc}33;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.4);
    }}
    .stButton>button {{
        background: linear-gradient(135deg, {acc}, #f59e0b) !important; color: black !important;
        font-weight: 900; border-radius: 12px; height: 55px; border: none !important; width: 100%;
    }}
    .stTextArea textarea {{ background: #000 !important; color: {acc} !important; border: 1px solid {acc}33 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FAIL-SAFE ENGINE & UTILS ---
@st.cache_resource(show_spinner=False)
def load_kokoro_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

def clean_script_pro(text):
    text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    return " ".join(text.split())

def create_pro_srt(text, duration):
    words = text.split()
    if not words: return ""
    per_word = duration / len(words)
    srt_content = ""
    for i, word in enumerate(words):
        start, end = i * per_word, (i + 1) * per_word
        ts = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        srt_content += f"{i+1}\n{ts(start)} --> {ts(end)}\n{word}\n\n"
    return srt_content

# --- 3. UI LAYOUT ---
apply_custom_theme()
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("🛡️ STUDIO CONTROL")
    # Theme Selection with Callback for Instant Change
    st.selectbox("🎨 ENVIRONMENT", ["Cyber 3D Gold 🧊", "Anime Pastel 🌸", "Minimalist Pro 💼"], 
                 key="active_theme")
    
    try:
        st.image("gojo.jpg", use_container_width=True)
    except:
        uploaded = st.file_uploader("Upload Profile", type=['jpg','png'])
        if uploaded: st.image(uploaded, use_container_width=True)

    st.markdown("---")
    VOICES = {"am_onyx": "🌑 Onyx (Deep)", "af_sky": "🎭 Sky (Anime)", "af_bella": "🎙️ Bella", "am_adam": "🎬 Adam", "am_fenrir": "🐺 Fenrir", "am_michael": "👨‍🏫 Michael"}
    
    # Fusion Logic
    mode = st.radio("ARCHITECTURE", ["Solo Identity", "Fusion (Gojo Mix)"])
    if mode == "Fusion (Gojo Mix)":
        v1, v2, mix_ratio = "am_onyx", "af_sky", 0.75
        st.info("Gojo Mode: 75% Onyx / 25% Sky")
    else:
        v_id = st.selectbox("VOICE", list(VOICES.keys()), format_func=lambda x: VOICES[x])
        mix_ratio = 1.0

    speed = st.slider("TEMPO", 0.5, 2.0, 1.05)

with m:
    st.subheader("📝 PRODUCTION SCRIPT")
    raw_script = st.text_area("", placeholder="Enter your script...", height=400, label_visibility="collapsed")
    
    if st.button("🚀 RENDER MASTER"):
        if raw_script.strip():
            engine = load_kokoro_engine()
            clean_text = clean_script_pro(raw_script)
            
            with st.spinner("Synthesizing..."):
                try:
                    # THE FIX: Fetch and Shape Voice Styles Correctely
                    if mode == "Fusion (Gojo Mix)":
                        s1, s2 = engine.get_voice_style("am_onyx"), engine.get_voice_style("af_sky")
                        style = (s1 * 0.75) + (s2 * 0.25)
                    else:
                        style = engine.get_voice_style(v_id)
                    
                    # ERROR-FREE SHAPING: Ensures NumPy shape is always (1, 512)
                    style = np.atleast_2d(style)
                    
                    samples, sr = engine.create(clean_text, voice=style, speed=speed, lang="en-us")
                    
                    # Export
                    buf = io.BytesIO()
                    sf.write(buf, samples, sr, format='WAV')
                    duration = len(samples) / sr
                    
                    st.session_state.last_audio = {
                        "wav": buf.getvalue(),
                        "srt": create_pro_srt(clean_text, duration),
                        "dur": duration
                    }
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M"), "text": clean_text[:20]})
                except Exception as e:
                    st.error(f"Engine Error: {e}")

with r:
    st.subheader("🎧 MONITOR")
    if st.session_state.last_audio:
        aud = st.session_state.last_audio
        st.audio(aud['wav'])
        st.download_button("📥 DOWNLOAD WAV", aud['wav'], "master.wav")
        st.download_button("📜 DOWNLOAD SRT", aud['srt'], "subs.srt")
        st.success(f"DUR: {aud['dur']:.2f}s")
    else:
        st.info("Idle...")

    st.subheader("🕒 LOGS")
    for h in st.session_state.history[-5:]:
        st.caption(f"✅ {h['time']} - {h['text']}...")