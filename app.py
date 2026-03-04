import streamlit as st
import whisper
import os
import random
import subprocess
import gc  # Garbage collection to prevent crashes
from pydub import AudioSegment

st.set_page_config(page_title="Avinash: Stable Studio", layout="wide")

# --- MEMORY EFFICIENT LOADING ---
@st.cache_resource
def load_whisper():
    # 'tiny' is 4x lighter than 'base'. For 40s+ on Streamlit Cloud, 
    # 'tiny' is the ONLY way to prevent the RuntimeError.
    return whisper.load_model("tiny") 

whisper_engine = load_whisper()

# ... (UI and Sidebar code remains the same) ...

if uploaded_audio:
    with open("temp_audio.mp3", "wb") as f:
        f.write(uploaded_audio.getbuffer())

    if st.button("🚀 GENERATE CAPTIONS"):
        try:
            with st.spinner("AI is thinking (Memory Optimized)..."):
                
                # 1. FORCE CLEANUP
                gc.collect() 
                
                # 2. RUN WHISPER
                task = "translate" if mode == "English Translation" else "transcribe"
                # Added fp16=False because Streamlit Cloud doesn't have GPUs
                result = whisper_engine.transcribe(
                    "temp_audio.mp3", 
                    task=task, 
                    word_timestamps=True,
                    fp16=False 
                )
                
                # ... (ASS Script Generation logic) ...
                
                # 3. FFMPEG RENDER
                # We use a lower resolution (480x270) to save more memory
                subprocess.run([
                    "ffmpeg", "-y", 
                    "-f", "lavfi", "-i", "color=c=0x00FF00:s=480x270:r=30:d=120", 
                    "-i", "temp_audio.mp3", 
                    "-vf", "ass=green.ass", 
                    "-c:v", "libx264", "-preset", "ultrafast", 
                    "-pix_fmt", "yuv420p", "-shortest", "green_output.mp4"
                ])
                
                st.video("green_output.mp4")
                
        except Exception as e:
            st.error(f"The audio was too heavy for the free server. Try a 20-second clip or check the logs.")
            st.write(e)
        finally:
            gc.collect() # Final cleanup