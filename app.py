import streamlit as st
import subprocess
import whisper
import os
import random
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. SETTINGS & HELPERS ---
st.set_page_config(page_title="Avinash Sen Typo Studio", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

def hex_to_ass(hex_color):
    """Converts #RRGGBB to ASS &HAABBGGRR (Alpha-Blue-Green-Red)"""
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

# --- 2. LOAD AI ENGINES (With Word Timestamps) ---
@st.cache_resource
def init_tools():
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. SIDEBAR: TYPO DESIGNER ---
st.sidebar.title("⚡ Typo Designer")
t_color = st.sidebar.color_picker("Word Color", "#FFFF00")
t_size = st.sidebar.slider("Font Size", 20, 80, 45)
intensity = st.sidebar.slider("Movement Intensity", 0, 100, 50)

# --- 4. MAIN INTERFACE ---
st.title("🎬 High-Energy Typo Studio")

tab_creator, tab_history = st.tabs(["🚀 Create Viral Video", "📜 History Log"])

with tab_creator:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Voice & Script")
        txt = st.text_area("Script", "This is how you dominate the algorithm with moving text.")
        
        voices = ["af_heart", "af_bella", "am_adam", "am_michael", "bf_emma", "bm_george"]
        v1 = st.selectbox("Main Voice", voices)
        use_fusion = st.checkbox("Enable Fusion")
        
        if st.button("Generate Audio & Typo Data"):
            with st.spinner("Synthesizing..."):
                if use_fusion:
                    s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(voices[1])
                    blended = s1 * 0.5 + s2 * 0.5
                    samples, sr = kokoro.create(txt, voice=blended, speed=1.1)
                else:
                    samples, sr = kokoro.create(txt, voice=v1, speed=1.1)
                sf.write("audio.wav", samples, sr)
            
            with st.spinner("Analyzing Word Timestamps..."):
                # We use word_timestamps=True for the "Typo" effect
                result = whisper_engine.transcribe("audio.wav", word_timestamps=True)
                
                # CREATE THE .ASS FILE (Advanced Subtitles)
                ass_header = f"""[Script Info]\nScriptType: v4.00+\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,2,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
                
                ass_lines = []
                for segment in result['segments']:
                    for word in segment['words']:
                        start = word['start']
                        end = word['end']
                        # RANDOM POSITION LOGIC (The "Typo" Effect)
                        # We change X and Y based on intensity
                        rand_x = 320 + random.randint(-intensity*2, intensity*2)
                        rand_y = 180 + random.randint(-intensity, intensity)
                        
                        time_s = f"{int(start//3600):01}:{int((start%3600)//60):02}:{start%60:05.2f}"
                        time_e = f"{int(end//3600):01}:{int((end%3600)//60):02}:{end%60:05.2f}"
                        
                        ass_lines.append(f"Dialogue: 0,{time_s},{time_e},Default,,0,0,0,,{{\\pos({rand_x},{rand_y})}}{word['word'].strip().upper()}")
                
                with open("typo.ass", "w", encoding="utf-8") as f:
                    f.write(ass_header + "\n".join(ass_lines))
                
                st.session_state.history.append({"script": txt, "voice": v1})
                st.audio("audio.wav")
                st.success("✅ Typo Script Ready!")

    with col2:
        st.subheader("2. Video Render")
        video_file = st.file_uploader("Upload Background", type=["mp4"])
        
        if video_file and st.button("Render Dynamic Video"):
            with st.spinner("Generating Animation..."):
                with open("bg.mp4", "wb") as f: f.write(video_file.getbuffer())
                
                # FFmpeg command using the .ass file instead of .srt
                cmd = [
                    "ffmpeg", "-y", "-i", "bg.mp4", "-i", "audio.wav",
                    "-vf", "ass=typo.ass",
                    "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "output.mp4"
                ]
                subprocess.run(cmd)
                st.video("output.mp4")
                with open("output.mp4", "rb") as f:
                    st.download_button("📥 Download Result", f, "typo_video.mp4")

with tab_history:
    st.subheader("Session History")
    history_str = ""
    for entry in st.session_state.history:
        log = f"Voice: {entry['voice']} | Script: {entry['script']}\n"
        st.text(log)
        history_str += log
    
    if history_str:
        st.download_button("💾 Download Full History (.txt)", history_str, "studio_history.txt")