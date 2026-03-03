import streamlit as st
import asyncio
import edge_tts
import whisper
import os
import random
import subprocess
import soundfile as sf
from datetime import timedelta

# --- 1. SETUP & UTILS ---
st.set_page_config(page_title="Avinash Sen: Neural Studio", layout="wide")

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_engine = load_whisper()

# --- 2. SIDEBAR: NEURAL VOICE SELECTION ---
st.sidebar.title("🎙️ Microsoft Neural Voices")
st.sidebar.info("These voices use Deep Learning for 99% human realism.")

# The best Hindi Neural Voices available
voices_dict = {
    "hi-IN-MadhurNeural": "Madhur (Deep Male - Best for Sigma/News)",
    "hi-IN-SwararaNeural": "Swarara (Smooth Female - Best for Vlogs)",
    "en-IN-PrabhatNeural": "Prabhat (Indian English Male)",
    "en-IN-NeerjaNeural": "Neerja (Indian English Female)"
}

selected_voice = st.sidebar.selectbox("Select Native Voice", list(voices_dict.keys()), format_func=lambda x: voices_dict[x])
v_pitch = st.sidebar.slider("Voice Pitch", -20, 20, 0)
v_rate = st.sidebar.slider("Speech Speed %", -20, 20, 0)

# Caption Customization (Restored)
st.sidebar.subheader("🎨 Caption Style")
t_color = st.sidebar.color_picker("Text Color", "#FFD700") # Gold
t_size = st.sidebar.slider("Font Size", 20, 100, 50)
cap_task = st.sidebar.selectbox("Caption Language", ["English Translation", "Original Hindi/Hinglish"])

# --- 3. THE GENERATOR FUNCTION ---
async def generate_voice(text, voice, pitch, rate):
    # Adjusting pitch/rate for Edge-TTS format
    p_str = f"{pitch:+}Hz"
    r_str = f"{rate:+}%"
    communicate = edge_tts.Communicate(text, voice, pitch=p_str, rate=r_str)
    await communicate.save("speech.mp3")

# --- 4. MAIN INTERFACE ---
st.title("🎬 High-End Hindi Video Studio")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Script (Type in Hindi or Hinglish)")
    script = st.text_area("Your Script:", "Namaste doston! Aaj hum AI ki duniya mein ek naya kadam uthayenge. Kya aap taiyaar hain?")
    
    if st.button("🎙️ Generate Human Voice"):
        with st.spinner("Synthesizing Neural Speech..."):
            asyncio.run(generate_voice(script, selected_voice, v_pitch, v_rate))
            st.audio("speech.mp3")
            
        with st.spinner("Creating Dynamic Typo Captions..."):
            # Whisper Transcribe/Translate
            task = "translate" if cap_task == "English Translation" else "transcribe"
            result = whisper_engine.transcribe("speech.mp3", task=task, word_timestamps=True)
            
            # ASS Header
            ass_h = f"[Script Info]\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            lines = []
            for seg in result['segments']:
                for word in seg['words']:
                    s, e = word['start'], word['end']
                    t_in = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}"
                    t_out = f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                    
                    # TYPO ANIMATION
                    clean_w = word['word'].strip().upper()
                    x, y = 320 + random.randint(-15, 15), 180 + random.randint(-10, 10)
                    # Flash & Zoom effect
                    lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{\\pos({x},{y})\\t(0,100,\\fscx125\\fscy125)\\t(100,200,\\fscx100\\fscy100)}}{clean_w}")

            with open("typo.ass", "w", encoding="utf-8") as f:
                f.write(ass_h + "\n".join(lines))
            st.success("Audio & Subtitles Ready!")

with col2:
    st.subheader("2. Video Rendering")
    bg_video = st.file_uploader("Upload Background", type=["mp4"])
    if bg_video and st.button("🎥 Render Final Viral Video"):
        with st.spinner("Merging Audio + Dynamic Captions..."):
            with open("bg.mp4", "wb") as f: f.write(bg_video.getbuffer())
            # FFmpeg: High Quality Render
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "speech.mp3", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "output.mp4"]
            subprocess.run(cmd)
            st.video("output.mp4")
            with open("output.mp4", "rb") as f:
                st.download_button("📥 Download MP4", f, "final_hindi_reel.mp4")