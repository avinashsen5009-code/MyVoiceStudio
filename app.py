import streamlit as st
import subprocess
import whisper
import os
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. SETTINGS & HELPERS ---
st.set_page_config(page_title="Elite Production Studio", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

def format_timestamp(seconds):
    """Helper for SRT timestamps"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{msecs:03d}"

# --- 2. LOAD AI ENGINES ---
@st.cache_resource
def init_tools():
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. VOICE LIBRARY ---
voice_library = {
    "af_heart": "Soft & Emotional (Best for Anime)",
    "af_bella": "Clear & Professional (Best for Explainers)",
    "am_adam": "Deep & Serious (Best for Motivation)",
    "am_michael": "Energetic (Best for Tech)",
    "bf_emma": "Warm & Friendly (Best for Vlogs)",
    "bm_george": "Cinematic (Best for Trailers)"
}

st.sidebar.title("🎙️ Voice Settings")
for v_id, desc in voice_library.items():
    st.sidebar.caption(f"- **{v_id}**: {desc}")

# --- 4. MAIN INTERFACE ---
st.title("🎬 The Ultimate Studio")

tab_creator, tab_history = st.tabs(["⚡ Creation Dashboard", "📜 History"])

with tab_creator:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Audio & SRT Generator")
        txt = st.text_area("Script", "Welcome to the studio. Let's create something viral.")
        
        v1 = st.selectbox("Primary Voice", list(voice_library.keys()))
        use_fusion = st.checkbox("Enable Voice Fusion")
        
        if use_fusion:
            v2 = st.selectbox("Fusion Partner", list(voice_library.keys()), index=1)
            ratio = st.slider("Mix Ratio (0=Primary, 100=Partner)", 0, 100, 50) / 100
        
        if st.button("Generate Audio & SRT"):
            with st.spinner("Creating Unique Voice..."):
                if use_fusion:
                    # CORRECT FUSION LOGIC: Get styles and blend them
                    s1 = kokoro.get_voice_style(v1)
                    s2 = kokoro.get_voice_style(v2)
                    blended = s1 * (1 - ratio) + s2 * ratio
                    samples, sr = kokoro.create(txt, voice=blended, speed=1.0)
                else:
                    samples, sr = kokoro.create(txt, voice=v1, speed=1.0)
                
                sf.write("studio_audio.wav", samples, sr)
            
            with st.spinner("Writing Subtitles..."):
                result = whisper_engine.transcribe("studio_audio.wav")
                srt_content = ""
                for i, seg in enumerate(result['segments'], 1):
                    s, e = format_timestamp(seg['start']), format_timestamp(seg['end'])
                    srt_content += f"{i}\n{s} --> {e}\n{seg['text'].strip()}\n\n"
                
                with open("subtitles.srt", "w") as f: f.write(srt_content)
            
            st.session_state.history.append({"text": txt[:30], "voice": v1 + (" (Fusion)" if use_fusion else "")})
            st.audio("studio_audio.wav")
            st.download_button("Download SRT", open("subtitles.srt", "rb"), "subtitles.srt")

    with col2:
        st.subheader("2. Video Merger")
        video_file = st.file_uploader("Upload MP4", type=["mp4"])
        
        if video_file and st.button("Render Final Video"):
            if not os.path.exists("subtitles.srt"):
                st.error("Generate Audio/SRT first!")
            else:
                with st.spinner("Burning Captions..."):
                    with open("in.mp4", "wb") as f: f.write(video_file.getbuffer())
                    
                    # FFmpeg Command
                    cmd = [
                        "ffmpeg", "-y", "-i", "in.mp4", "-i", "studio_audio.wav",
                        "-vf", "subtitles=subtitles.srt:force_style='Fontsize=20,PrimaryColour=&H0000FFFF'",
                        "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "out.mp4"
                    ]
                    subprocess.run(cmd, capture_output=True)
                    st.video("out.mp4")

with tab_history:
    for item in reversed(st.session_state.history):
        st.write(f"✅ {item['voice']}: {item['text']}...")