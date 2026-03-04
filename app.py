import streamlit as st
import whisper
import os
import random
import subprocess
from pydub import AudioSegment

# --- 1. CORE SETUP ---
st.set_page_config(page_title="Avinash Sen: Pro-Editor", layout="wide")

@st.cache_resource
def load_whisper():
    # 'small' is the sweet spot for Hindi accuracy vs speed
    return whisper.load_model("small") 

whisper_engine = load_whisper()

# --- 2. SIDEBAR: FULL DESIGN CONTROL ---
st.sidebar.title("🎨 Design & Typography")

# Font Selection (Make sure these are installed on your system/server)
font_choice = st.sidebar.selectbox("Select Font Style", ["Arial Black", "Impact", "Verdana", "Courier New"])

# Color & Size
f_size = st.sidebar.slider("Font Size", 30, 120, 70)
primary_color = st.sidebar.color_picker("Text Color", "#FFFF00") # Bright Yellow
outline_color = st.sidebar.color_picker("Outline Color", "#000000")

# Logic Controls
st.sidebar.subheader("🕹️ Layout Engine")
v_align = st.sidebar.selectbox("Placement", ["Dynamic Chaos", "Strict Center", "Top/Bottom Toggle"])
mode = st.sidebar.radio("Content Language:", ["Native Hindi", "English Translation"])
margin = st.sidebar.slider("Safe Margin (Stay away from edges)", 50, 200, 100)

# --- 3. THE STUDIO INTERFACE ---
st.title("🎬 Viral Hindi Caption Studio")

uploaded_file = st.file_uploader("Upload MP4 Video", type=["mp4"])

if uploaded_file:
    with open("input.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🔥 Generate Pro-Captions"):
        with st.spinner("AI analyzing speech patterns..."):
            
            # 1. WHISPER ENGINE
            task_type = "translate" if mode == "English Translation" else "transcribe"
            result = whisper_engine.transcribe("input.mp4", task=task_type, word_timestamps=True)
            
            # 2. AUDIO MIXER
            subprocess.run(["ffmpeg", "-y", "-i", "input.mp4", "-q:a", "0", "-map", "a", "audio.wav"])
            main_audio = AudioSegment.from_wav("audio.wav")
            pop_sfx = None
            if os.path.exists("pop.wav"):
                try: pop_sfx = AudioSegment.from_file("pop.wav")
                except: pass

            # 3. ADVANCED SUBTITLE STYLING
            # Using \an5 for Center-Center Anchor (Best for Pop effects)
            ass_header = f"""[Script Info]
PlayResX: 640
PlayResY: 360

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV
Style: Default,{font_choice},{f_size},{hex_to_ass(primary_color)},{hex_to_ass(outline_color)},1,4,5,20
"""
            def hex_to_ass(hex_c):
                hex_c = hex_c.lstrip('#')
                return f"&H00{hex_c[4:6]}{hex_c[2:4]}{hex_c[0:2]}"

            events_header = "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            lines = []
            for seg in result['segments']:
                for word in seg['words']:
                    start, end = word['start'], word['end']
                    text = word['word'].strip().upper()
                    
                    # --- SMART SAFE POSITIONING ---
                    if v_align == "Dynamic Chaos":
                        # We keep X and Y strictly within the center box
                        x = random.randint(margin, 640 - margin)
                        y = random.randint(margin, 360 - margin)
                    elif v_align == "Strict Center":
                        x, y = 320, 180
                    else:
                        x, y = 320, random.choice([margin, 360 - margin])

                    # THE ANIMATION: Pop + Hover Drift
                    # \an5 = Center Anchor
                    # \pos(x,y) = Spawn point
                    # \move(x,y, x, y-30) = Float upwards
                    anim = f"{{\\an5\\pos({x},{y})\\move({x},{y},{x},{y-30})\\t(0,100,\\fscx140\\fscy140)\\t(100,200,\\fscx100\\fscy100)}}"
                    
                    ts = f"{int(start//3600)}:{int((start%3600)//60):02}:{start%60:05.2f}"
                    te = f"{int(end//3600)}:{int((end%3600)//60):02}:{end%60:05.2f}"
                    
                    lines.append(f"Dialogue: 0,{ts},{te},Default,,0,0,0,,{anim}{text}")
                    
                    if pop_sfx:
                        main_audio = main_audio.overlay(pop_sfx, position=int(start*1000))

            # 4. FINAL RENDER
            main_audio.export("final_audio.wav", format="wav")
            with open("subs.ass", "w", encoding="utf-8") as f:
                f.write(ass_header + events_header + "\n".join(lines))
            
            # Using high-quality libx264 encoding
            subprocess.run([
                "ffmpeg", "-y", "-i", "input.mp4", "-i", "final_audio.wav", 
                "-vf", "ass=subs.ass", "-c:v", "libx264", "-crf", "18", 
                "-c:a", "aac", "-map", "0:v", "-map", "1:a", "-shortest", "final.mp4"
            ])
            
            st.success("✅ Studio Render Complete!")
            st.video("final.mp4")
            with open("final.mp4", "rb") as f:
                st.download_button("📥 Download Viral Edit", f, "viral_reel.mp4")