import streamlit as st
import whisper
import moviepy as mp
import subprocess
import os
import re
import numpy as np
import io
import soundfile as sf
from datetime import timedelta
from huggingface_hub import hf_hub_download

# --- 1. STUDIO ENGINE CONFIG ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

if 'last_audio' not in st.session_state: st.session_state.last_audio = None
if 'final_video' not in st.session_state: st.session_state.final_video = None

def apply_studio_css():
    acc = st.session_state.get('cap_color', "#EAB308")
    st.markdown(f"""
    <style>
    .stApp {{ background-color: #020617; color: white; }}
    div[data-testid="column"] > div {{
        background: rgba(15, 23, 42, 0.95); border-radius: 15px; 
        padding: 25px; border: 1px solid {acc}44; box-shadow: 0 8px 32px rgba(0,0,0,0.8);
    }}
    .stButton>button {{ background: {acc} !important; color: black; font-weight: 900; border: none; height: 3em; }}
    .stDownloadButton>button {{ background: transparent !important; color: {acc} !important; border: 1px solid {acc} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. AI HELPERS ---
@st.cache_resource
def load_whisper(): return whisper.load_model("base")

def to_ass_color(hex_color):
    # Converts #RRGGBB to &H00BBGGRR& (ASS format)
    return f"&H00{hex_color[5:7]}{hex_color[3:5]}{hex_color[1:3]}&"

# --- 3. THE STUDIO INTERFACE ---
apply_studio_css()
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("🎨 TYPOGRAPHY CONSOLE")
    cap_color = st.color_picker("Text Primary Color", "#EAB308", key="cap_color")
    out_color = st.color_picker("Outline/Glow Color", "#000000")
    cap_size = st.slider("Font Size", 10, 100, 32)
    font_style = st.selectbox("Font Family", ["Impact", "Arial Black", "Verdana", "Courier New"])
    v_pos = st.slider("Vertical Position (Bottom to Top)", 10, 300, 50)
    
    st.markdown("---")
    st.subheader("🎙️ VOICE DOWNLOADS")
    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio['wav'], format='audio/wav')
        st.download_button("📥 DOWNLOAD RAW VOICE (.WAV)", st.session_state.last_audio['wav'], "studio_voice.wav")
    else:
        st.caption("No voice generated yet.")

with m:
    st.subheader("🎥 PRODUCTION HUB")
    tab1, tab2 = st.tabs(["AI Voice & Captions", "Auto-Caption Uploaded Video"])
    
    with tab1:
        script = st.text_area("Script", placeholder="Type what you want the AI to say...", height=200)
        col1, col2 = st.columns(2)
        with col1: v_id = st.selectbox("Base Soul", ["am_onyx", "af_sky", "am_adam", "af_bella"])
        with col2: speed = st.slider("Tempo", 0.5, 2.0, 1.0)
        
        bg_vid = st.file_uploader("Upload Background MP4 (Optional)", type=['mp4'])
        
        if st.button("🚀 RENDER VOICE + CAPTIONS"):
            from kokoro_onnx import Kokoro # Imported here to keep it clean
            m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
            v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
            engine = Kokoro(m_path, v_path)
            
            # Generate Audio
            samples, sr = engine.create(script, voice=v_id, speed=speed, lang="en-us")
            buf = io.BytesIO(); sf.write(buf, samples, sr, format='WAV')
            st.session_state.last_audio = {"wav": buf.getvalue(), "text": script, "dur": len(samples)/sr}
            st.rerun()

    with tab2:
        raw_vid = st.file_uploader("Upload Video to Detect Speech", type=['mp4', 'mov'])
        if st.button("🪄 AUTO-DETECT & CAPTION"):
            if raw_vid:
                with st.spinner("Analyzing Speech..."):
                    with open("in.mp4", "wb") as f: f.write(raw_vid.read())
                    model = load_whisper()
                    res = model.transcribe("in.mp4")
                    
                    # Create ASS Subtitle file with custom style
                    ass_header = f"""[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Shadow, Alignment, MarginV
Style: Default,{font_style},{cap_size},{to_ass_color(cap_color)},{to_ass_color(out_color)},1,2,1,2,{v_pos}
[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
                    events = ""
                    for seg in res['segments']:
                        events += f"Dialogue: 0,{timedelta(seconds=seg['start'])},{timedelta(seconds=seg['end'])},Default,,0,0,0,,{seg['text'].upper()}\n"
                    
                    with open("subs.ass", "w") as f: f.write(ass_header + events)
                    subprocess.run(f'ffmpeg -y -i in.mp4 -vf "ass=subs.ass" output.mp4', shell=True)
                    with open("output.mp4", "rb") as f: st.session_state.final_video = f.read()
                    st.success("Video Synced!")

with r:
    st.subheader("📺 STUDIO MONITOR")
    if st.session_state.final_video:
        st.video(st.session_state.final_video)
        st.download_button("📥 DOWNLOAD MASTER MP4", st.session_state.final_video, "avinash_studio_pro.mp4")
    else:
        st.info("Rendered video will appear here.")
    
    st.markdown("---")
    st.subheader("📜 PROJECT SRT")
    if st.session_state.last_audio:
        st.caption("SRT generated from Voice Studio is ready.")
        # Logic to convert last_audio text to SRT would go here