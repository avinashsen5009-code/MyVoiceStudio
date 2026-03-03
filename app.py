import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import re
import os
import subprocess
from datetime import datetime

# --- 1. STUDIO UI & THEME ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

if 'active_theme' not in st.session_state: st.session_state.active_theme = "Obsidian Gold 🏆"
if 'last_audio' not in st.session_state: st.session_state.last_audio = None

def apply_studio_css():
    theme = st.session_state.active_theme
    bg, acc = ("#020617", "#EAB308") if theme == "Obsidian Gold 🏆" else ("#0F172A", "#38BDF8")
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; color: #F8FAFC !important; }}
    div[data-testid="column"] > div {{
        background: rgba(15, 23, 42, 0.95) !important; border-radius: 20px; 
        padding: 25px; border: 1px solid {acc}33;
    }}
    .stButton>button {{
        background: {acc} !important; color: #000 !important; font-weight: 900;
        border-radius: 10px; width: 100%; border: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE UTILS ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

def make_srt(text, dur):
    words = text.split(); step = dur/len(words) if words else 0
    srt = ""
    for i, w in enumerate(words):
        s, e = i*step, (i+1)*step
        ts = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        srt += f"{i+1}\n{ts(s)} --> {ts(e)}\n{w}\n\n"
    return srt

# --- 3. THE STUDIO INTERFACE ---
apply_studio_css()
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("⚙️ SETTINGS")
    st.selectbox("THEME", ["Obsidian Gold 🏆", "Cyber Blue 🧊"], key="active_theme")
    
    VOICES = {"am_onyx": "🌑 Onyx", "af_sky": "🎭 Sky", "am_adam": "🎬 Adam", "am_fenrir": "🐺 Fenrir"}
    arch = st.radio("VOICE MODE", ["Solo", "Fusion Mix"], key="arch_mode")
    
    if st.session_state.arch_mode == "Solo":
        v_solo = st.selectbox("VOICE", list(VOICES.keys()), format_func=lambda x: VOICES[x], key="v_solo")
    else:
        v_b = st.selectbox("BASE", list(VOICES.keys()), index=0, key="v_b")
        v_f = st.selectbox("FLAVOR", list(VOICES.keys()), index=1, key="v_f")
        ratio = st.slider("RATIO", 0.0, 1.0, 0.75, key="mix")
    
    speed = st.slider("TEMPO", 0.5, 2.0, 1.05)

with m:
    st.subheader("📝 PRODUCTION")
    script = st.text_area("Script", height=300, label_visibility="collapsed")
    
    # VIDEO UPLOADER FOR CAPTION BURNING
    bg_video = st.file_uploader("📂 Upload Background Video (MP4)", type=['mp4'])
    
    if st.button("🚀 GENERATE VIDEO WITH CAPTIONS"):
        if script.strip() and bg_video:
            engine = load_engine()
            text = " ".join(re.sub(r'\[.*?\]|\(.*?\)', '', script).split())
            
            with st.spinner("Processing... This may take a minute."):
                # 1. Generate Audio
                if st.session_state.arch_mode == "Solo":
                    style = np.atleast_2d(engine.get_voice_style(st.session_state.v_solo))
                else:
                    s1, s2 = engine.get_voice_style(st.session_state.v_b), engine.get_voice_style(st.session_state.v_f)
                    style = np.atleast_2d((s1 * st.session_state.mix) + (s2 * (1.0 - st.session_state.mix)))
                
                samples, sr = engine.create(text, voice=style, speed=speed, lang="en-us")
                
                # 2. Save Temporary Files
                sf.write("temp_audio.wav", samples, sr)
                srt_content = make_srt(text, len(samples)/sr)
                with open("temp_subs.srt", "w") as f: f.write(srt_content)
                with open("temp_video.mp4", "wb") as f: f.write(bg_video.read())
                
                # 3. FFMPEG Command: Merging Audio + Video + Burning Subtitles
                # 'force_style' sets the Font, Size, and Color (Yellow/Gold)
                cmd = (
                    f'ffmpeg -y -i temp_video.mp4 -i temp_audio.wav '
                    f'-vf "subtitles=temp_subs.srt:force_style=\'FontSize=20,PrimaryColour=&H00FFFF&,Alignment=2\'" '
                    f'-map 0:v -map 1:a -c:v libx264 -shortest out_video.mp4'
                )
                
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    with open("out_video.mp4", "rb") as f:
                        st.session_state.final_video = f.read()
                    st.success("Video Rendered Successfully!")
                except Exception as e:
                    st.error(f"FFMPEG Error: {e}. Ensure FFmpeg is installed.")

with r:
    st.subheader("🎬 FINAL OUTPUT")
    if 'final_video' in st.session_state:
        st.video(st.session_state.final_video)
        st.download_button("📥 DOWNLOAD CAPTIONED VIDEO", st.session_state.final_video, "yt_final.mp4")
    else:
        st.info("Upload a video and render a script to see results.")