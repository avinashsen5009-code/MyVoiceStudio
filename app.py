import streamlit as st
import whisper
import os
import random
import subprocess
import gc
from kokoro import KPipeline
from pydub import AudioSegment
import soundfile as sf
import numpy as np

# --- 1. CORE ENGINE ---
st.set_page_config(page_title="Avinash Master Studio", layout="wide")

@st.cache_resource
def get_engines():
    # KPipeline is the neural engine for realistic speech
    return KPipeline(lang_code='a'), whisper.load_model("tiny")

neural_pipe, whisper_model = get_engines()

# --- 2. THE VOICE MIXER ---
def generate_fused_audio(text, v1, v2, blend):
    # Generates two voices and blends them to create a unique sound (Anti-Copyright)
    gen1 = neural_pipe(text, voice=v1, speed=1.1)
    gen2 = neural_pipe(text, voice=v2, speed=1.0)
    
    # Extract audio data and mix
    a1 = np.concatenate([audio for _, _, audio in gen1])
    a2 = np.concatenate([audio for _, _, audio in gen2])
    
    # Blend voices
    mixed = (a1 * (1 - blend)) + (a2 * blend)
    sf.write('mixed.wav', mixed, 24000)
    return AudioSegment.from_wav("mixed.wav")

# --- 3. UI ---
st.title("🎬 Kinetic Chaos Studio")
with st.sidebar:
    ratio = st.selectbox("Resolution", ["9:16 (TikTok)", "16:9 (YouTube)"])
    v1 = st.selectbox("Voice 1", ["af_bella", "af_nicole"], index=0)
    v2 = st.selectbox("Voice 2", ["am_michael", "bf_emma"], index=1)
    blend = st.slider("Voice Mix Blend", 0.0, 1.0, 0.5)
    chaos = st.slider("Typography Chaos", 10, 150, 80)
    script = st.text_area("Your Script", "Success is not just about luck, it is about consistency.")

if st.button("🚀 RENDER PROJECT"):
    # Render Logic
    res = "9:16" if ratio == "9:16 (TikTok)" else "16:9"
    dims = "1080x1920" if res == "9:16" else "1920x1080"
    
    with st.spinner("Mixing Neural Voices..."):
        audio = generate_fused_audio(script, v1, v2, blend)
        audio.export("final.mp3", format="mp3")
        duration = len(audio) / 1000.0

    with st.spinner("Generating Kinetic Chaos..."):
        # Whisper for timing
        trans = whisper_model.transcribe("final.mp3", word_timestamps=True)
        
        # Build ASS for Green Screen
        ass_lines = []
        for seg in trans['segments']:
            for word in seg['words']:
                text = word['word'].strip().upper()
                x = random.randint(200, 800) if res == "16:9" else random.randint(100, 900)
                y = random.randint(200, 800)
                
                # Pop Animation + Chaos
                anim = f"{{\\an5\\frz{random.randint(-chaos, chaos)}\\move({x},{y},{x},{y-50})\\t(0,100,\\fscx160\\fscy160)}}"
                ts = f"{int(word['start']//3600)}:{int((word['start']%3600)//60):02}:{word['start']%60:05.2f}"
                te = f"{int(word['end']//3600)}:{int((word['end']%3600)//60):02}:{word['end']%60:05.2f}"
                ass_lines.append(f"Dialogue: 0,{ts},{te},Default,,0,0,0,,{anim}{text}")

        with open("gs.ass", "w") as f:
            f.write("[Script Info]\nPlayResX: 1920\nPlayResY: 1080\n[V4+ Styles]\nStyle: Default,Impact,120,&H0000FFFF,&H00000000,&H80000000,1,5,3,5,10\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ass_lines))

    # Render Final
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x00FF00:s={dims}:r=30:d={duration}", "-i", "final.mp3", "-vf", "ass=gs.ass", "-c:v", "libx264", "-shortest", "output.mp4"])
    st.video("output.mp4")