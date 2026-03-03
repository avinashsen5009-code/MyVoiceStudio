import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import re
from datetime import datetime

# --- 1. THEME ENGINE (FULL OVERRIDE) ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

if 'active_theme' not in st.session_state: st.session_state.active_theme = "Obsidian Gold 🏆"
if 'history' not in st.session_state: st.session_state.history = []
if 'last_audio' not in st.session_state: st.session_state.last_audio = None

def apply_full_theme():
    theme = st.session_state.active_theme
    if theme == "Obsidian Gold 🏆":
        bg, acc, card, txt = "#020617", "#EAB308", "rgba(15, 23, 42, 0.95)", "#F8FAFC"
    elif theme == "Cyber Blue 🧊":
        bg, acc, card, txt = "#0F172A", "#38BDF8", "rgba(30, 41, 59, 0.9)", "#F1F5F9"
    else: 
        bg, acc, card, txt = "#FFFFFF", "#2563EB", "#F1F5F9", "#0F172A"
    
    st.markdown(f"""
    <style>
    /* Full Page Override */
    .stApp, [data-testid="stAppViewContainer"] {{ background-color: {bg} !important; color: {txt} !important; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 1px solid {acc}22; }}
    
    /* Column Cards */
    div[data-testid="column"] > div {{
        background: {card} !important; backdrop-filter: blur(20px);
        border-radius: 15px; padding: 25px; border: 1px solid {acc}33;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }}
    
    /* Global Text & Buttons */
    h1, h2, h3, p, span, label {{ color: {txt} !important; }}
    .stButton>button {{
        background: {acc} !important; color: #000 !important;
        font-weight: 800; border-radius: 8px; border: none !important;
    }}
    .stTextArea textarea {{ background: #000 !important; color: {acc} !important; border: 1px solid {acc}44 !important; }}
    
    /* Fix for Selectbox/Radio labels */
    div[data-baseweb="select"] > div {{ background-color: #000 !important; color: {txt} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FAIL-SAFE ENGINE ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

def clean_script(text):
    return " ".join(re.sub(r'\[.*?\]|\(.*?\)', '', text).split())

def make_srt(text, dur):
    words = text.split(); step = dur/len(words) if words else 0
    srt = ""
    for i, w in enumerate(words):
        s, e = i*step, (i+1)*step
        ts = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        srt += f"{i+1}\n{ts(s)} --> {ts(e)}\n{w}\n\n"
    return srt

# --- 3. THE STUDIO INTERFACE ---
apply_full_theme()
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("⚙️ SETTINGS")
    # Theme with instant refresh
    st.selectbox("THEME", ["Obsidian Gold 🏆", "Cyber Blue 🧊", "Studio White 💼"], 
                 key="active_theme")
    
    try:
        st.image("gojo.jpg", use_container_width=True)
    except:
        st.caption("Gojo Image Missing")

    st.markdown("---")
    VOICES = {"am_onyx": "🌑 Onyx (Deep)", "af_sky": "🎭 Sky (Anime)", "am_adam": "🎬 Adam", "am_fenrir": "🐺 Fenrir", "af_bella": "🎙️ Bella", "am_michael": "👨‍🏫 Michael"}
    
    # Mode selection with instant refresh
    arch = st.radio("VOICE ARCHITECTURE", ["Solo Identity", "Fusion Mix"], key="arch_mode")
    
    if st.session_state.arch_mode == "Solo Identity":
        v_main = st.selectbox("SELECT VOICE", list(VOICES.keys()), format_func=lambda x: VOICES[x], key="v_solo")
    else:
        v_base = st.selectbox("BASE SOUL", list(VOICES.keys()), index=0, format_func=lambda x: VOICES[x], key="v_base")
        v_flavor = st.selectbox("FLAVOR SOUL", list(VOICES.keys()), index=1, format_func=lambda x: VOICES[x], key="v_flavor")
        f_ratio = st.slider("FUSION RATIO", 0.0, 1.0, 0.75, key="mix_val")

    speed = st.slider("TEMPO", 0.5, 2.0, 1.05)

with m:
    st.subheader("📝 PRODUCTION")
    script = st.text_area("", placeholder="Enter your script...", height=440, label_visibility="collapsed")
    
    if st.button("🚀 RENDER FINAL"):
        if script.strip():
            engine = load_engine()
            txt = clean_script(script)
            with st.spinner("Synthesizing..."):
                try:
                    if st.session_state.arch_mode == "Solo Identity":
                        style = engine.get_voice_style(st.session_state.v_solo)
                    else:
                        s1 = engine.get_voice_style(st.session_state.v_base)
                        s2 = engine.get_voice_style(st.session_state.v_flavor)
                        style = (s1 * st.session_state.mix_val) + (s2 * (1.0 - st.session_state.mix_val))
                    
                    style = np.atleast_2d(style)
                    samples, sr = engine.create(txt, voice=style, speed=speed, lang="en-us")
                    
                    buf = io.BytesIO(); sf.write(buf, samples, sr, format='WAV')
                    st.session_state.last_audio = {"wav": buf.getvalue(), "srt": make_srt(txt, len(samples)/sr), "dur": len(samples)/sr}
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M"), "text": txt[:20]})
                except Exception as e:
                    st.error(f"Error: {e}")

with r:
    st.subheader("🎧 MONITOR")
    if st.session_state.last_audio:
        aud = st.session_state.last_audio
        st.audio(aud['wav'])
        st.download_button("📥 WAV", aud['wav'], "master.wav")
        st.download_button("📜 SRT", aud['srt'], "subs.srt")
        st.success(f"READY | {aud['dur']:.2f}s")
    else:
        st.info("Idle...")

    st.subheader("🕒 LOGS")
    for h in st.session_state.history[-5:]:
        st.caption(f"✅ {h['time']} - {h['text']}...")