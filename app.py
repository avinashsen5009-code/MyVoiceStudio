import streamlit as st
import subprocess
import whisper
import os
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. SETTINGS & HELPERS ---
st.set_page_config(page_title="Avinash Sen Studio V4", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

def format_timestamp(seconds):
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

# --- 3. SIDEBAR: CAPTION DESIGNER ---
st.sidebar.title("🎨 Caption Designer")
cap_color = st.sidebar.color_picker("Text Color", "#FFFF00") # Default Yellow
cap_outline = st.sidebar.color_picker("Outline Color", "#000000") # Default Black
cap_size = st.sidebar.slider("Font Size", 10, 72, 28)
cap_pos = st.sidebar.slider("Vertical Position (Margin)", 0, 100, 10) # Distance from bottom

# Convert Hex to FFmpeg BGR format
def hex_to_ffmpeg(hex_color):
    hex_color = hex_color.lstrip('#')
    # FFmpeg uses &HBBGGRR format
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

ffmpeg_color = hex_to_ffmpeg(cap_color)
ffmpeg_outline = hex_to_ffmpeg(cap_outline)

# --- 4. MAIN INTERFACE ---
st.title("🎬 Avinash Sen Pro Studio")

tab_creator, tab_history = st.tabs(["⚡ Creation Dashboard", "📜 History"])

with tab_creator:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Audio & SRT Generator")
        txt = st.text_area("Script", "Enter your viral script here...")
        
        voices = ["af_heart", "af_bella", "am_adam", "am_michael", "bf_emma", "bm_george"]
        v1 = st.selectbox("Primary Voice", voices)
        use_fusion = st.checkbox("Enable Voice Fusion")
        
        if use_fusion:
            v2 = st.selectbox("Fusion Partner", voices, index=1)
            ratio = st.slider("Mix Ratio", 0, 100, 50) / 100
        
        if st.button("Generate Audio & SRT"):
            with st.spinner("Synthesizing..."):
                if use_fusion:
                    s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(v2)
                    blended = s1 * (1 - ratio) + s2 * ratio
                    samples, sr = kokoro.create(txt, voice=blended, speed=1.0)
                else:
                    samples, sr = kokoro.create(txt, voice=v1, speed=1.0)
                sf.write("studio_audio.wav", samples, sr)
            
            with st.spinner("Transcribing..."):
                result = whisper_engine.transcribe("studio_audio.wav")
                srt_content = ""
                for i, seg in enumerate(result['segments'], 1):
                    s, e = format_timestamp(seg['start']), format_timestamp(seg['end'])
                    srt_content += f"{i}\n{s} --> {e}\n{seg['text'].strip()}\n\n"
                with open("subtitles.srt", "w", encoding="utf-8") as f: f.write(srt_content)
            
            st.audio("studio_audio.wav")
            st.success("✅ Ready for Video!")

    with col2:
        st.subheader("2. Video Render")
        video_file = st.file_uploader("Upload Background MP4", type=["mp4"])
        
        if video_file and st.button("Render Final Video"):
            if not os.path.exists("subtitles.srt"):
                st.error("Generate Audio first!")
            else:
                with st.spinner("Burning Dynamic Captions..."):
                    with open("in.mp4", "wb") as f: f.write(video_file.getbuffer())
                    
                    # DYNAMIC FONT STYLE STRING
                    style = f"Fontname=Arial,Fontsize={cap_size},PrimaryColour={ffmpeg_color},OutlineColour={ffmpeg_outline},BorderStyle=1,Outline=2,Alignment=2,MarginV={cap_pos}"
                    
                    cmd = [
                        "ffmpeg", "-y", "-i", "in.mp4", "-i", "studio_audio.wav",
                        "-vf", f"subtitles=subtitles.srt:force_style='{style}'",
                        "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "out.mp4"
                    ]
                    subprocess.run(cmd, capture_output=True)
                    st.video("out.mp4")
                    with open("out.mp4", "rb") as f:
                        st.download_button("📥 Download Final Video", f, "final_video.mp4")

with tab_history:
    st.write(st.session_state.history)