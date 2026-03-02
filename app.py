import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import io
import re
import time
from datetime import datetime

# --- 1. CORE SYSTEM ---
st.set_page_config(page_title="VOICE STUDIO", layout="wide", page_icon="💎")

if 'history' not in st.session_state: st.session_state.history = []
if 'last_audio' not in st.session_state: st.session_state.last_audio = None
# Initialize theme state before anything loads
if 'theme' not in st.session_state: st.session_state.theme = "Cyber 3D Gold 🧊"

# --- 2. SCRIPT CLEANER ---
def clean_script(text):
    cleaned = re.sub(r'\[.*?\]', '', text)
    cleaned = re.sub(r'\(.*?\)', '', cleaned)
    return " ".join(cleaned.split())

# --- 3. INSTANT THEME ENGINE ---
# Applied at the very top so changes reflect immediately
def apply_theme():
    theme = st.session_state.theme
    if theme == "Cyber 3D Gold 🧊":
        bg, acc, card, txt = "#0f172a", "#fbbf24", "rgba(30, 41, 59, 0.8)", "#f8fafc"
    elif theme == "Anime Pastel 🌸":
        bg, acc, card, txt = "#fff5f7", "#f06292", "rgba(255, 255, 255, 0.9)", "#4a148c"
    else: 
        bg, acc, card, txt = "#f8fafc", "#1e40af", "#ffffff", "#1e293b"
    
    st.markdown(f"""
    <style>
    .main {{ background: {bg}; color: {txt}; }}
    div[data-testid="column"] > div {{
        background: {card} !important; backdrop-filter: blur(15px);
        border-radius: 20px; padding: 25px; border: 1px solid {acc}33;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.5);
    }}
    .stButton>button {{
        background: linear-gradient(135deg, {acc}, #f59e0b); color: black !important;
        font-weight: 900; border-radius: 12px; height: 60px; border: none; width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- 4. ENGINE LOADER ---
@st.cache_resource(show_spinner=False)
def get_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

# --- 5. STUDIO INTERFACE ---
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("🛡️ STUDIO CONTROL")
    
    # THEME FIX: key="theme" links directly to session_state
    st.selectbox("🎨 ACTIVE THEME", 
                 ["Cyber 3D Gold 🧊", "Anime Pastel 🌸", "Minimalist Pro 💼"], 
                 key="theme")
    
    try:
        st.image("gojo.jpg", use_container_width=True)
    except:
        uploaded = st.file_uploader("Upload Profile Image", type=['jpg','png'])
        if uploaded: st.image(uploaded, use_container_width=True)
    
    st.markdown("---")
    VOICES = {
        "am_onyx": "🌑 Onyx (Deep)", "af_sky": "🎭 Sky (Anime)", 
        "af_bella": "🎙️ Bella (Pro)", "am_adam": "🎬 Adam (Movie)",
        "am_fenrir": "🐺 Fenrir (Gravelly)", "am_michael": "👨‍🏫 Michael (Tech)"
    }
    
    # MIXING FIX: Restored full custom voice fusion
    mode = st.radio("VOICE ARCHITECTURE", ["Solo Identity", "Custom Mix (Fusion)"])
    if mode == "Custom Mix (Fusion)":
        v1 = st.selectbox("Base Voice", list(VOICES.keys()), index=0, format_func=lambda x: VOICES[x])
        v2 = st.selectbox("Target Voice", list(VOICES.keys()), index=1, format_func=lambda x: VOICES[x])
        mix_ratio = st.slider("Base Ratio (%)", 0.0, 1.0, 0.75)
    else:
        v_id = st.selectbox("SELECT VOICE", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    
    speed = st.slider("TEMPO", 0.5, 2.0, 1.05)
    do_clean = st.checkbox("Clean Script (Auto-remove [Brackets])", value=True)

with m:
    st.subheader("📝 YOUTUBE PRODUCTION")
    script = st.text_area("", placeholder="Paste your script here...", height=400, label_visibility="collapsed")
    
    if st.button("🚀 RENDER MASTER AUDIO"):
        if script.strip():
            engine = get_engine()
            final_text = clean_script(script) if do_clean else script
            
            with st.spinner("Synthesizing Clean Audio..."):
                # Apply custom mix logic
                if mode == "Custom Mix (Fusion)":
                    s1, s2 = engine.get_voice_style(v1), engine.get_voice_style(v2)
                    blend = (s1 * mix_ratio) + (s2 * (1.0 - mix_ratio))
                    samples, sr = engine.create(final_text, voice=blend, speed=speed, lang="en-us")
                else:
                    samples, sr = engine.create(final_text, voice=v_id, speed=speed, lang="en-us")
                
                buf = io.BytesIO(); sf.write(buf, samples, sr, format='WAV')
                dur = len(samples)/sr
                
                # Pro word-based SRT
                words = final_text.split()
                step = dur/len(words) if words else 0
                srt = ""
                for i, w in enumerate(words):
                    s, e = i*step, (i+1)*step
                    f = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},000"
                    srt += f"{i+1}\n{f(s)} --> {f(e)}\n{w}\n\n"
                
                st.session_state.last_audio = {"wav": buf.getvalue(), "srt": srt, "dur": dur}
                st.session_state.history.append({"time": datetime.now().strftime("%H:%M"), "text": final_text[:20]})

with r:
    st.subheader("🎧 MONITOR")
    if st.session_state.last_audio:
        curr = st.session_state.last_audio
        st.audio(curr['wav'], format="audio/wav")
        st.success(f"Rendering Complete | {curr['dur']:.2f}s")
        st.download_button("📥 DOWNLOAD WAV", curr['wav'], "yt_master.wav")
        st.download_button("📜 DOWNLOAD SRT", curr['srt'], "yt_subs.srt")
    else:
        st.info("Awaiting script input...")

    st.markdown("---")
    st.subheader("🕒 HISTORY")
    for h in st.session_state.history[-5:]:
        st.caption(f"✅ {h['time']} - {h['text']}...")