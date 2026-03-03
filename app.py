import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import re
import time
from datetime import datetime

# --- 1. STUDIO UI & DYNAMIC THEME ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

if 'active_theme' not in st.session_state: st.session_state.active_theme = "Obsidian Gold 🏆"
if 'last_audio' not in st.session_state: st.session_state.last_audio = None

def apply_studio_css():
    theme = st.session_state.active_theme
    if theme == "Obsidian Gold 🏆":
        bg, acc, card, txt = "#020617", "#EAB308", "rgba(15, 23, 42, 0.98)", "#F8FAFC"
    elif theme == "Cyber Blue 🧊":
        bg, acc, card, txt = "#0F172A", "#38BDF8", "rgba(30, 41, 59, 0.9)", "#F1F5F9"
    else: 
        bg, acc, card, txt = "#FFFFFF", "#2563EB", "#F1F5F9", "#0F172A"
    
    st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{ background-color: {bg} !important; color: {txt} !important; }}
    div[data-testid="column"] > div {{
        background: {card} !important; border-radius: 20px; padding: 25px; 
        border: 1px solid {acc}33; box-shadow: 0 0 30px {acc}11;
    }}
    .stButton>button {{
        background: {acc} !important; color: #000 !important; font-weight: 900;
        border-radius: 10px; border: none; transition: 0.3s;
    }}
    /* DYNAMIC CAPTION BOX */
    .caption-box {{
        background: rgba(0,0,0,0.8); border: 2px solid {acc};
        border-radius: 15px; padding: 20px; text-align: center;
        min-height: 100px; display: flex; align-items: center; justify-content: center;
        font-size: 24px; font-weight: 800; color: #fff; margin-top: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
    .highlight {{ color: {acc}; text-transform: uppercase; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ENGINE ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

def clean_txt(t): return " ".join(re.sub(r'\[.*?\]|\(.*?\)', '', t).split())

# --- 3. STUDIO LAYOUT ---
apply_studio_css()
l, m, r = st.columns([1, 1.4, 1])

VOICES = {"am_onyx": "🌑 Onyx", "af_sky": "🎭 Sky", "am_adam": "🎬 Adam", "am_fenrir": "🐺 Fenrir", "af_bella": "🎙️ Bella", "am_michael": "👨‍🏫 Michael"}

with l:
    st.subheader("⚙️ CONTROL")
    st.selectbox("THEME", ["Obsidian Gold 🏆", "Cyber Blue 🧊", "Studio White 💼"], key="active_theme")
    arch = st.radio("ARCHITECTURE", ["Solo", "Fusion"], key="arch_mode")
    
    if st.session_state.arch_mode == "Solo":
        v_solo = st.selectbox("VOICE", list(VOICES.keys()), format_func=lambda x: VOICES[x], key="v_solo")
    else:
        v_b = st.selectbox("BASE", list(VOICES.keys()), index=0, key="v_b")
        v_f = st.selectbox("FLAVOR", list(VOICES.keys()), index=1, key="v_f")
        ratio = st.slider("RATIO", 0.0, 1.0, 0.75, key="mix")
    
    speed = st.slider("TEMPO", 0.5, 2.0, 1.05)

with m:
    st.subheader("📝 PRODUCTION")
    script = st.text_area("", placeholder="Paste script...", height=350, label_visibility="collapsed")
    
    if st.button("🚀 RENDER & SYNC"):
        if script.strip():
            engine = load_engine()
            text = clean_txt(script)
            with st.spinner("Processing..."):
                try:
                    if st.session_state.arch_mode == "Solo":
                        style = np.atleast_2d(engine.get_voice_style(st.session_state.v_solo))
                    else:
                        s1, s2 = engine.get_voice_style(st.session_state.v_b), engine.get_voice_style(st.session_state.v_f)
                        style = np.atleast_2d((s1 * st.session_state.mix) + (s2 * (1.0 - st.session_state.mix)))
                    
                    samples, sr = engine.create(text, voice=style, speed=speed, lang="en-us")
                    buf = io.BytesIO(); sf.write(buf, samples, sr, format='WAV')
                    st.session_state.last_audio = {"wav": buf.getvalue(), "text": text, "dur": len(samples)/sr}
                except Exception as e: st.error(f"Error: {e}")

    # --- DYNAMIC CAPTION PREVIEW ---
    if st.session_state.last_audio:
        st.markdown("### 📺 DYNAMIC PREVIEW")
        cap_placeholder = st.empty()
        words = st.session_state.last_audio["text"].split()
        
        if st.button("▶️ PLAY WITH CAPTIONS"):
            st.audio(st.session_state.last_audio["wav"])
            start_time = time.time()
            total_dur = st.session_state.last_audio["dur"]
            time_per_word = total_dur / len(words)
            
            for i, word in enumerate(words):
                # Highlight logic
                display_text = " ".join([f'<span class="highlight">{w}</span>' if idx == i else w for idx, w in enumerate(words[max(0, i-3):i+4])])
                cap_placeholder.markdown(f'<div class="caption-box">... {display_text} ...</div>', unsafe_allow_html=True)
                time.sleep(time_per_word)
            cap_placeholder.markdown('<div class="caption-box">FINISHED</div>', unsafe_allow_html=True)

with r:
    st.subheader("🎧 MONITOR")
    if st.session_state.last_audio:
        aud = st.session_state.last_audio
        st.audio(aud['wav'])
        st.download_button("📥 WAV MASTER", aud['wav'], "master.wav")
        # Generate SRT for download
        per_w = aud['dur']/len(words)
        srt = ""
        for i, w in enumerate(words):
            s, e = i*per_w, (i+1)*per_w
            ts = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},000"
            srt += f"{i+1}\n{ts(s)} --> {ts(e)}\n{w}\n\n"
        st.download_button("📜 DOWNLOAD SRT", srt, "subs.srt")
    else:
        st.info("Render a script to see dynamic captions.")