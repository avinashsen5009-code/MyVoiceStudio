import streamlit as st
import whisper
import os
import random
import subprocess
from pydub import AudioSegment

# --- 1. SETUP ---
st.set_page_config(page_title="Avinash Sen: Fast Chaos", layout="wide")

# FASTER MODEL: Changed 'base' to 'tiny' for speed
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny") 

whisper_engine = load_whisper()

# --- 2. THE ERROR-PROOF SFX ENGINE ---
def get_sfx():
    try:
        if os.path.exists("pop.wav"):
            return AudioSegment.from_file("pop.wav") # Safer than .from_wav
    except Exception:
        return None
    return None

# --- 3. THE STUDIO ---
st.title("🌪️ Fast Hindi Caption Studio")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Video", type=["mp4"])
    # Keywords to trigger Pop Sound
    power_words = st.text_input("Highlight Keywords (Comma separated):", "PAISA, GOAL, SUCCESS, ZINDAGI")

if uploaded_file:
    if st.button("🚀 Start Fast Process"):
        with st.spinner("Processing..."):
            # Save Temp Video
            with open("input.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 1. Faster Transcription
            result = whisper_engine.transcribe("input.mp4", word_timestamps=True)
            
            # 2. SFX Logic (Error Proof)
            pop_sfx = get_sfx()
            subprocess.run(["ffmpeg", "-y", "-i", "input.mp4", "-q:a", "0", "-map", "a", "audio.wav"])
            main_audio = AudioSegment.from_wav("audio.wav")
            
            # 3. Build Animated Captions (Chaos Mode)
            ass_header = "[Script Info]\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,50,&H00FFFFFF,&H00000000,1,2,2,20\nStyle: High,Arial,65,&H0000FFFF,&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            lines = []
            highlights = [w.strip().upper() for w in power_words.split(",")]

            for seg in result['segments']:
                for word in seg['words']:
                    start, end = word['start'], word['end']
                    clean_w = word['word'].strip().upper()
                    
                    # Timing for SFX
                    if any(h in clean_w for h in highlights) and pop_sfx:
                        main_audio = main_audio.overlay(pop_sfx, position=int(start*1000))
                        style = "High"
                    else:
                        style = "Default"

                    # THE VISUAL CHAOS (Random + Pop + Hover)
                    x, y = random.randint(100, 540), random.randint(80, 280)
                    # \move makes it hover, \t makes it pop
                    anim = f"{{\\move({x},{y},{x},{y-30})\\t(0,100,\\fscx150\\fscy150)\\t(100,200,\\fscx100\\fscy100)}}"
                    
                    t_s = f"{int(start//3600)}:{int((start%3600)//60):02}:{start%60:05.2f}"
                    t_e = f"{int(end//3600)}:{int((end%3600)//60):02}:{end%60:05.2f}"
                    lines.append(f"Dialogue: 0,{t_s},{t_e},{style},,0,0,0,,{anim}{clean_w}")

            # 4. Final Export
            main_audio.export("final_audio.wav", format="wav")
            with open("sub.ass", "w") as f: f.write(ass_header + "\n".join(lines))
            
            subprocess.run(["ffmpeg", "-y", "-i", "input.mp4", "-i", "final_audio.wav", "-vf", "ass=sub.ass", "-map", "0:v", "-map", "1:a", "-shortest", "out.mp4"])
            
            st.video("out.mp4")