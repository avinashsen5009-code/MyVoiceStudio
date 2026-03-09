import streamlit as st
import whisper
import random
import subprocess
import gc
from kokoro import KPipeline
from pydub import AudioSegment
import soundfile as sf
import numpy as np

# --- 1. MEMORY-OPTIMIZED ENGINE ---
@st.cache_resource
def load_ai_engines():
    # Pre-loading models into cache to prevent 'Loading' loops
    pipe = KPipeline(lang_code='a')
    model = whisper.load_model("tiny")
    return pipe, model

pipe, whisper_model = load_ai_engines()

# --- 2. THE FUSION ENGINE ---
def mix_voices(text, v1, v2, blend):
    gen1 = pipe(text, voice=v1, speed=1.1)
    gen2 = pipe(text, voice=v2, speed=1.0)
    a1 = np.concatenate([audio for _, _, audio in gen1])
    a2 = np.concatenate([audio for _, _, audio in gen2])
    mixed = (a1 * (1 - blend)) + (a2 * blend)
    sf.write('fused.wav', mixed, 24000)
    return AudioSegment.from_wav("fused.wav")

# --- 3. UI & RENDER LOGIC ---
st.title("🎬 Neural Fusion Studio")

with st.sidebar:
    ratio = st.selectbox("Aspect Ratio", ["9:16 (Vertical)", "16:9 (Horizontal)"])
    v1 = st.selectbox("Voice A", ["af_bella", "af_nicole"])
    v2 = st.selectbox("Voice B", ["am_michael", "bf_emma"])
    blend = st.slider("Voice Mix", 0.0, 1.0, 0.5)
    chaos = st.slider("Typo Chaos", 10, 150, 80)
    script = st.text_area("Your Script", "Success is built on consistency.")

if st.button("🚀 GENERATE MASTER"):
    dims = "1080x1920" if "9:16" in ratio else "1920x1080"
    
    with st.spinner("Synthesizing Neural Speech..."):
        audio = mix_voices(script, v1, v2, blend)
        audio.export("temp.mp3", format="mp3")
        duration = len(audio) / 1000.0

    with st.spinner("Generating Kinetic Typography..."):
        result = whisper_model.transcribe("temp.mp3", word_timestamps=True)
        ass_lines = []
        for seg in result['segments']:
            for word in seg['words']:
                x = random.randint(200, 800)
                y = random.randint(200, 800)
                rot = random.randint(-chaos, chaos)
                anim = f"{{\\an5\\frz{rot}\\move({x},{y},{x},{y-50})\\t(0,100,\\fscx160\\fscy160)}}"
                ts = f"{int(word['start']//3600):02}:{int((word['start']%3600)//60):02}:{word['start']%60:05.2f}"
                ass_lines.append(f"Dialogue: 0,{ts},{ts},Default,,0,0,0,,{anim}{word['word'].upper()}")

        with open("subs.ass", "w") as f:
            f.write("[Script Info]\nPlayResX: 1920\nPlayResY: 1080\n[V4+ Styles]\nStyle: Default,Impact,100,&H00FFFFFF,&H00000000,&H80000000,1,5,3,5,10\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ass_lines))

    with st.spinner("Rendering Video..."):
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x00FF00:s={dims}:r=30:d={duration}", "-i", "temp.mp3", "-vf", f"ass=subs.ass,scale={dims}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", "output.mp4"])
        
    st.video("output.mp4")
    with open("output.mp4", "rb") as f:
        st.download_button("📥 Download Green Screen", f, "output.mp4")
    
    gc.collect() # Force free up RAM