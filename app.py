import streamlit as st
import numpy as np
import soundfile as sf
import os
import subprocess
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download

# --- 1. SETTINGS & LOADERS ---
st.set_page_config(page_title="Production Studio", layout="wide")

@st.cache_resource
def init_kokoro():
    # Download models once to cache
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path)

kokoro = init_kokoro()

# --- 2. CORE LOGIC ---
def generate_voice(text, voice_name, speed=1.0):
    samples, sr = kokoro.create(text, voice=voice_name, speed=speed)
    sf.write("studio_audio.wav", samples, sr)
    return "studio_audio.wav"

# --- 3. INTERFACE ---
st.title("🎬 Production Studio")
txt = st.text_area("Script", "Success is built on consistency.")
v1 = st.selectbox("Select Voice", list(kokoro.voices.keys()))

if st.button("Generate Audio"):
    with st.spinner("Synthesizing..."):
        file_path = generate_voice(txt, v1)
        st.audio(file_path)
        with open(file_path, "rb") as f:
            st.download_button("Download Audio", f, "output.wav")

# Video Merger (ffmpeg)
video_file = st.file_uploader("Upload MP4", type=["mp4"])
if video_file and st.button("Merge Audio"):
    with open("in.mp4", "wb") as f: f.write(video_file.getbuffer())
    cmd = ["ffmpeg", "-y", "-i", "in.mp4", "-i", "studio_audio.wav", "-c:v", "copy", "-c:a", "aac", "out.mp4"]
    subprocess.run(cmd)
    st.video("out.mp4")