import streamlit as st
import whisper
import os
import random
import subprocess
import gc
from pydub import AudioSegment

# --- 1. SETUP ---
st.set_page_config(page_title="Avinash: Stable Studio", layout="wide")

@st.cache_resource
def load_whisper():
    # 'tiny' is mandatory for Streamlit Cloud stability
    return whisper.load_model("tiny") 

whisper_engine = load_whisper()

# --- 2. DEFINE THE UPLOADER FIRST ---
st.title("⚡ Pro Green Screen Studio")
uploaded_audio = st.file_uploader("Upload Audio (MP3/WAV)", type=["mp3", "wav", "m4a"])

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎛️ Design Controls")
    f_size = st.slider("Font Size", 30, 150, 90)
    color_choice = st.color_picker("Text Color", "#FFFF00")
    mode = st.selectbox("Language", ["Hindi", "English Translation"])

def hex_to_ass(hex_c):
    hex_c = hex_c.lstrip('#')
    return f"&H00{hex_c[4:6]}{hex_c[2:4]}{hex_c[0:2]}"

# --- 4. THE LOGIC CHECK (This is where the NameError was) ---
if uploaded_audio is not None:
    # Save the file immediately
    with open("temp_audio.mp3", "wb") as f:
        f.write(uploaded_audio.getbuffer())

    if st.button("🚀 GENERATE GREEN SCREEN"):
        try:
            with st.spinner("Processing..."):
                gc.collect()
                
                # Run Whisper with CPU-safe settings
                task = "translate" if mode == "English Translation" else "transcribe"
                result = whisper_engine.transcribe(
                    "temp_audio.mp3", 
                    task=task, 
                    word_timestamps=True,
                    fp16=False
                )
                
                # --- ASS SCRIPT GENERATION ---
                ass_header = f"""[Script Info]
PlayResX: 640
PlayResY: 360
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, ShadowColour, BorderStyle, Outline, Shadow, Alignment, MarginV
Style: Default,Arial,{f_size},{hex_to_ass(color_choice)},&H00000000,&H80000000,1,4,2,5,20
"""
                events = "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                
                lines = []
                for seg in result['segments']:
                    for word in seg['words']:
                        start, end = word['start'], word['end']
                        text = word['word'].strip().upper()
                        x, y = random.randint(100, 540), random.randint(100, 260)
                        anim = f"{{\\an5\\move({x},{y},{x},{y-40})\\t(0,100,\\fscx140\\fscy140)\\t(100,200,\\fscx100\\fscy100)}}"
                        ts, te = f"{int(start//3600)}:{int((start%3600)//60):02}:{start%60:05.2f}", f"{int(end//3600)}:{int((end%3600)//60):02}:{end%60:05.2f}"
                        lines.append(f"Dialogue: 0,{ts},{te},Default,,0,0,0,,{anim}{text}")

                with open("green.ass", "w", encoding="utf-8") as f:
                    f.write(ass_header + events + "\n".join(lines))

                # --- FFMPEG RENDER ---
                subprocess.run([
                    "ffmpeg", "-y", 
                    "-f", "lavfi", "-i", "color=c=0x00FF00:s=640x360:r=30:d=120", 
                    "-i", "temp_audio.mp3", 
                    "-vf", "ass=green.ass", 
                    "-c:v", "libx264", "-preset", "ultrafast", 
                    "-pix_fmt", "yuv420p", "-shortest", "green_output.mp4"
                ])
                
                st.video("green_output.mp4")
                
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            gc.collect()
else:
    st.info("Please upload an audio file to start.")