import streamlit as st
import whisper
import random
import subprocess
import gc
from kokoro import KPipeline
from pydub import AudioSegment
import soundfile as sf
import numpy as np

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Avinash: Neural Fusion Studio", layout="wide")

@st.cache_resource
def load_assets():
    return KPipeline(lang_code='a'), whisper.load_model("tiny")

pipe, whisper_model = load_assets()

# --- 2. THE FUSION ENGINE ---
def mix_voices(text, v1, v2, blend):
    gen1 = pipe(text, voice=v1, speed=1.1)
    gen2 = pipe(text, voice=v2, speed=1.0)
    a1 = np.concatenate([audio for _, _, audio in gen1])
    a2 = np.concatenate([audio for _, _, audio in gen2])
    mixed = (a1 * (1 - blend)) + (a2 * blend)
    sf.write('fused.wav', mixed, 24000)
    return AudioSegment.from_wav("fused.wav")

# --- 3. UI & RENDER ---
st.title("🎬 Master Fusion Studio")
with st.sidebar:
    ratio = st.selectbox("Resolution", ["9:16 (Portrait)", "16:9 (Landscape)"])
    v1 = st.selectbox("Voice A", ["af_bella", "af_nicole"], index=0)
    v2 = st.selectbox("Voice B", ["am_michael", "bf_emma"], index=1)
    blend = st.slider("Voice Fusion Blend", 0.0, 1.0, 0.5)
    chaos = st.slider("Typography Chaos", 10, 120, 60)
    script = st.text_area("Script", "Your vision is your reality.")

if st.button("🚀 RENDER PROJECT"):
    dims = "1080:1920" if "9:16" in ratio else "1920:1080"
    
    # Process Voice
    audio = mix_voices(script, v1, v2, blend)
    audio.export("temp.mp3", format="mp3")
    
    # Process Captions
    result = whisper_model.transcribe("temp.mp3", word_timestamps=True)
    
    ass_lines = []
    for seg in result['segments']:
        for word in seg['words']:
            x = random.randint(300, 700)
            y = random.randint(300, 700)
            rot = random.randint(-chaos, chaos)
            # Dynamic Kinetic Tags
            anim = f"{{\\an5\\frz{rot}\\move({x},{y},{x},{y-50})\\t(0,100,\\fscx160\\fscy160)}}"
            ts = f"{int(word['start']//3600):02}:{int((word['start']%3600)//60):02}:{word['start']%60:05.2f}"
            ass_lines.append(f"Dialogue: 0,{ts},{ts},Default,,0,0,0,,{anim}{word['word'].upper()}")

    # Save Subtitles
    with open("subs.ass", "w") as f:
        f.write("[Script Info]\nPlayResX: 1920\nPlayResY: 1080\n[V4+ Styles]\nStyle: Default,Impact,100,&H00FFFFFF,&H00000000,&H80000000,1,5,3,5,10\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ass_lines))

    # FFmpeg Render
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x00FF00:s={dims.replace(':', 'x')}:r=30", "-i", "temp.mp3", "-vf", f"ass=subs.ass,scale={dims}", "-c:v", "libx264", "-shortest", "final.mp4"])
    
    st.video("final.mp4")
    with open("final.mp4", "rb") as f:
        st.download_button("📥 Download Green Screen", f, "final_studio_render.mp4")
    gc.collect()