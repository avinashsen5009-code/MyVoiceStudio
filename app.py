import streamlit as st
import subprocess
import whisper
import os
import random
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. CORE ENGINE ---
st.set_page_config(page_title="Avinash Sen: Reality Studio", layout="wide")

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

@st.cache_resource
def init_tools():
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 2. THE REALISM CONTROLS ---
st.sidebar.title("🧬 Neural Humanizer")

# Native Hindi/Hinglish Models
hindi_models = {"hm_omega": "Deep Male", "hm_psi": "Soft Male", "hf_alpha": "Clear Female", "hf_beta": "Warm Female"}
base_v = st.sidebar.selectbox("Base Human Model", list(hindi_models.keys()))

# THE REALISM SLIDERS
st.sidebar.subheader("🎚️ ElevenLabs Simulation")
emotion_depth = st.sidebar.slider("Emotional Pitch (Non-Robot)", 0.0, 0.20, 0.05, help="Higher = less robotic, more 'swing' in voice.")
breath_pause = st.sidebar.slider("Natural Breath Gaps", 0.1, 1.0, 0.4)
v_speed = st.sidebar.slider("Speech Speed", 0.8, 1.3, 1.05)

# CAPTION STYLE
st.sidebar.subheader("✍️ Caption Design")
t_color = st.sidebar.color_picker("Text Color", "#00FF00")
t_size = st.sidebar.slider("Font Size", 20, 100, 65)

# --- 3. MAIN DASHBOARD ---
st.title("🎙️ Avinash Sen Elite Studio")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Realistic Scripting")
    # PRO TIP: Use commas and dots for 'ElevenLabs' style pauses
    raw_script = st.text_area("Script (Hindi/Hinglish):", 
        "Suno... kya tumne kabhi socha hai? Ki sach kya hai. Yeh duniya... bohot ajeeb hai doston.")
    
    cap_lang = st.radio("Translate Captions?", ["No (Hinglish)", "Yes (English)"], horizontal=True)

    if st.button("🔥 Generate Realistic Voice"):
        with st.spinner("Processing Human Phonetics..."):
            # GET STYLE
            style = kokoro.get_voice_style(base_v)
            
            # THE SECRET SAUCE: Dynamic DNA
            # Instead of a fixed voice, we add 'Vocal Shimmer'
            vocal_shimmer = np.random.normal(0, emotion_depth, style.shape).astype(np.float32)
            humanized_style = style + vocal_shimmer
            
            # GENERATE WITH GAPS
            samples, sr = kokoro.create(raw_script, voice=humanized_style, speed=v_speed)
            sf.write("speech.wav", samples, sr)
            
        with st.spinner("Analyzing Voice for Typo Captions..."):
            task = "translate" if cap_lang == "Yes (English)" else "transcribe"
            result = whisper_engine.transcribe("speech.wav", task=task, word_timestamps=True)
            
            # ASS HEADER (Typo Style)
            ass_h = f"[Script Info]\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            ass_lines = []
            for seg in result['segments']:
                for word in seg['words']:
                    s, e = word['start'], word['end']
                    t_in = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}"
                    t_out = f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                    
                    # TYPO LOGIC: Words pop and bounce
                    clean_w = word['word'].strip().upper()
                    # Random jitter for position so it feels high-energy
                    x, y = random.randint(300, 340), random.randint(170, 190)
                    ass_lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{\\pos({x},{y})\\t(0,100,\\fscx130\\fscy130)\\t(100,200,\\fscx100\\fscy100)}}{clean_w}")

            with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_h + "\n".join(ass_lines))
            st.audio("speech.wav")
            st.success("Voice is now Humanized & Unique.")

with col2:
    st.subheader("2. Final Video")
    bg_vid = st.file_uploader("Upload Background", type=["mp4"])
    if bg_vid and st.button("🎥 Render Viral Edit"):
        with st.spinner("Merging..."):
            with open("bg.mp4", "wb") as f: f.write(bg_vid.getbuffer())
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "speech.wav", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "final.mp4"]
            subprocess.run(cmd)
            st.video("final.mp4")
            with open("final.mp4", "rb") as f: st.download_button("📥 Download", f, "viral_video.mp4")