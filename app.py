import streamlit as st
import whisper
import os
import random
import subprocess

# --- 1. CORE SETUP ---
st.set_page_config(page_title="Avinash: Green Screen Studio", layout="wide")

@st.cache_resource
def load_whisper():
    # 'tiny' or 'base' are ultra-fast for just audio processing
    return whisper.load_model("base") 

whisper_engine = load_whisper()

# --- 2. THE CONTROL MATRIX ---
st.sidebar.title("🟢 Green Screen Controls")

with st.sidebar.expander("🎨 Multi-Color Engine", expanded=True):
    font_choice = st.selectbox("Font Style", ["Impact", "Arial Black", "Verdana"])
    f_size = st.slider("Text Size", 30, 150, 90)
    
    # Parametric Palette
    c1 = st.color_picker("Color 1", "#FFFF00") # Yellow
    c2 = st.color_picker("Color 2", "#00F2FF") # Cyan
    c3 = st.color_picker("Color 3", "#FFFFFF") # White
    color_speed = st.slider("Color Change Speed", 1, 5, 1)

with st.sidebar.expander("🎭 Animation & Placement", expanded=True):
    pop_int = st.slider("Pop Intensity", 100, 200, 150)
    hover_dist = st.slider("Drift (Upwards)", 0, 100, 40)
    layout = st.radio("Position", ["Center", "Lower Third", "Chaos"])
    mode = st.selectbox("Language", ["Hindi", "English Translation"])

# --- 3. THE FAST ENGINE ---
st.title("⚡ Ultra-Fast Green Screen Captions")
st.markdown("Upload **Audio Only** to generate a transparent-ready caption video.")

def hex_to_ass(hex_c):
    hex_c = hex_c.lstrip('#')
    return f"&H00{hex_c[4:6]}{hex_c[2:4]}{hex_c[0:2]}"

uploaded_audio = st.file_uploader("Upload Audio (MP3/WAV)", type=["mp3", "wav", "m4a"])

if uploaded_audio:
    with open("temp_audio.mp3", "wb") as f:
        f.write(uploaded_audio.getbuffer())

    if st.button("🚀 GENERATE GREEN SCREEN"):
        with st.spinner("Processing Audio..."):
            
            # 1. WHISPER (Audio only is much faster)
            task = "translate" if mode == "English Translation" else "transcribe"
            result = whisper_engine.transcribe("temp_audio.mp3", task=task, word_timestamps=True)
            
            # 2. ASS SCRIPT
            custom_colors = [hex_to_ass(c1), hex_to_ass(c2), hex_to_ass(c3)]
            ass_header = f"""[Script Info]
PlayResX: 640
PlayResY: 360
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, ShadowColour, BorderStyle, Outline, Shadow, Alignment, MarginV
Style: Default,{font_choice},{f_size},&H00FFFFFF,&H00000000,&H80000000,1,4,2,5,20
"""
            events = "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            lines = []
            word_count = 0
            for seg in result['segments']:
                for word in seg['words']:
                    start, end = word['start'], word['end']
                    text = word['word'].strip().upper()
                    
                    # Color Mapping
                    color = custom_colors[(word_count // color_speed) % len(custom_colors)]
                    word_count += 1

                    # Position Logic
                    if layout == "Chaos":
                        x, y = random.randint(100, 540), random.randint(100, 260)
                    elif layout == "Lower Third":
                        x, y = 320, 280
                    else: x, y = 320, 180

                    anim = f"{{\\an5\\c{color}\\move({x},{y},{x},{y-hover_dist})\\t(0,100,\\fscx{pop_int}\\fscy{pop_int})\\t(100,200,\\fscx100\\fscy100)}}"
                    ts, te = f"{int(start//3600)}:{int((start%3600)//60):02}:{start%60:05.2f}", f"{int(end//3600)}:{int((end%3600)//60):02}:{end%60:05.2f}"
                    lines.append(f"Dialogue: 0,{ts},{te},Default,,0,0,0,,{anim}{text}")

            with open("green.ass", "w", encoding="utf-8") as f: f.write(ass_header + events + "\n".join(lines))

            # 3. FFMPEG GHOST RENDER (Creates Green Screen Video)
            # We create a 640x360 green background and burn the subtitles on it
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x00FF00:s=640x360:d=5", 
                "-i", "temp_audio.mp3", "-vf", "ass=green.ass", "-c:v", "libx264", 
                "-shortest", "-pix_fmt", "yuv420p", "green_output.mp4"
            ])
            
            st.video("green_output.mp4")
            st.download_button("📥 Download Green Screen", open("green_output.mp4", "rb"), "green_captions.mp4")