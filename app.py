import streamlit as st
import moviepy as mp
import whisper  # This requires 'pip install openai-whisper'
import os
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="Avinash Sen Studio V2", layout="wide")

# Theme Switcher
st.sidebar.title("🎨 Studio Settings")
theme_choice = st.sidebar.selectbox("Choose Theme", ["Gold Elite", "Cyberpunk", "Ghost"])

# Custom CSS for Theme
if theme_choice == "Gold Elite":
    st.markdown("<style>.stApp {background-color: #000; color: #D4AF37;}</style>", unsafe_allow_html=True)

# --- 2. VOICE FUSION ENGINE ---
@st.cache_resource
def init_tools():
    # Downloads the AI Voice models
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. THE STUDIO TABS ---
tab_audio, tab_video, tab_srt = st.tabs(["🎵 Audio Studio", "🎥 Video Captions", "📄 SRT Generator"])

with tab_audio:
    st.subheader("Voice Fusion & Solo Audio")
    voice_list = ["af_heart", "af_bella", "am_adam", "am_michael", "bf_emma", "bm_george"]
    
    col1, col2 = st.columns(2)
    with col1:
        v1 = st.selectbox("Primary Voice", voice_list)
        speed = st.slider("Speech Speed", 0.5, 2.0, 1.0)
    with col2:
        use_fusion = st.checkbox("Enable Voice Fusion")
        v2 = st.selectbox("Fusion Partner", voice_list, index=1) if use_fusion else None

    txt = st.text_area("Enter Script", "Welcome to the elite studio.")
    
    if st.button("Generate MP3"):
        # Logic to create audio
        samples, sr = kokoro.create(txt, voice=v1, speed=speed)
        sf.write("studio_audio.wav", samples, sr)
        st.audio("studio_audio.wav")
        st.download_button("Download Audio", open("studio_audio.wav", "rb"), "voiceover.mp3")

with tab_srt:
    st.subheader("Extract Subtitles (SRT)")
    up_audio = st.file_uploader("Upload Audio for SRT", type=["wav", "mp3"])
    if up_audio and st.button("Generate SRT"):
        with open("temp.wav", "wb") as f: f.write(up_audio.getbuffer())
        result = whisper_engine.transcribe("temp.wav")
        # Simple SRT formatting logic
        st.code(result["text"]) 
        st.success("SRT Content Generated above!")

# --- 4. YOUTUBE SUGGESTIONS ---
st.sidebar.markdown("---")
st.sidebar.subheader("🚀 YT Growth Tool")
topic = st.sidebar.text_input("Topic", "Gojo Motivation")
if st.sidebar.button("Get Viral Title"):
    st.sidebar.write(f"🏆 Title: Why {topic} will SHOCK you in 2026")