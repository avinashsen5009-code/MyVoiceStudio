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

# --- CONFIG ---
st.set_page_config(page_title="Avinash: Neural Fusion Studio", layout="wide")

@st.cache_resource
def load_models():
    return KPipeline(lang_code='a'), whisper.load_model("tiny")

neural_pipeline, whisper_engine = load_models()

# --- THE AMBIENCE BLENDER (Anti-Copyright) ---
def add_ambience(audio_path, intensity):
    audio = AudioSegment.from_file(audio_path)
    # Generate 1 second of white noise (very quiet)
    noise = AudioSegment.white_noise().apply_gain(-40)
    # Loop noise to match length
    noise = noise * (len(audio) // 1000 + 1)
    return audio.overlay(noise[:len(audio)], gain_during_overlay=intensity)

# --- SIDEBAR UI ---
st.sidebar.title("🧬 Neural Fusion Control")
script = st.sidebar.text_area("Your Script:", "The world is changing. Are you ready to lead?")
fusion_depth = st.sidebar.slider("Fusion Ambience (Anti-Copyright)", -50, -20, -35)
chaos_level = st.sidebar.slider("Kinetic Chaos Level", 10, 200, 80)

# --- RENDER ENGINE ---
if st.button("🚀 EXECUTE NEURAL CHAOS"):
    with st.spinner("1/3: Neural Speech Synthesis..."):
        # Kokoro Neural Generation
        generator = neural_pipeline(script, voice="af_bella", speed=1.1)
        for _, _, audio in generator:
            sf.write('raw.wav', audio, 24000)
        
        # Apply Fusion
        final_audio = add_ambience('raw.wav', fusion_depth)
        final_audio.export("final.mp3", format="mp3")

    with st.spinner("2/3: Generating Kinetic Typography..."):
        result = whisper_engine.transcribe("final.mp3", word_timestamps=True, fp16=False)
        
        # ASS Generation with Chaos
        ass_lines = []
        for word_data in [w for s in result['segments'] for w in s['words']]:
            text = word_data['word'].strip().upper()
            start, end = word_data['start'], word_data['end']
            
            # Kinetic Chaos Logic: Words jump randomly
            x = random.randint(150, 490)
            y = random.randint(100, 260)
            
            # Rotation and movement based on Chaos Level
            rot = random.randint(-chaos_level//4, chaos_level//4)
            anim = f"{{\\an5\\frz{rot}\\move({x},{y},{x},{y-20})\\t(0,100,\\fscx150\\fscy150)}}"
            
            ts, te = f"{int(start//3600)}:{int((start%3600)//60):02}:{start%60:05.2f}", f"{int(end//3600)}:{int((end%3600)//60):02}:{end%60:05.2f}"
            ass_lines.append(f"Dialogue: 0,{ts},{te},Default,,0,0,0,,{anim}{text}")

        with open("green.ass", "w") as f:
            f.write("[Script Info]\nPlayResX: 640\nPlayResY: 360\n[V4+ Styles]\nStyle: Default,Arial Black,90,&H00FFFFFF,&H00000000,&H80000000,1,4,3,5,10\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ass_lines))

    with st.spinner("3/3: Rendering..."):
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x00FF00:s=640x360:r=30:d=120", "-i", "final.mp3", "-vf", "ass=green.ass", "-c:v", "libx264", "-shortest", "final.mp4"])
        st.video("final.mp4")