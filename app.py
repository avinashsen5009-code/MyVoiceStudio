import streamlit as st
import asyncio
import edge_tts
import whisper
import os
import random
import subprocess
import numpy as np

# --- 1. CORE SETUP ---
st.set_page_config(page_title="Avinash Sen: Reality Studio v17", layout="wide")

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_engine = load_whisper()

# --- 2. SIDEBAR: THE REALISM ENGINE ---
st.sidebar.title("🎙️ Human Voice Lab")
st.sidebar.info("This engine uses Neural Prosody to avoid the robotic 'flat' sound.")

# High-Quality Native Hindi Models
hindi_voices = {
    "hi-IN-MadhurNeural": "Madhur (Deep Male - Studio Quality)",
    "hi-IN-SwararaNeural": "Swarara (Smooth Female - Natural Flow)"
}

selected_voice = st.sidebar.selectbox("Base Voice Model", list(hindi_voices.keys()), format_func=lambda x: hindi_voices[x])

# HUMANIZERS
st.sidebar.subheader("🧬 Vocal DNA")
v_pitch = st.sidebar.slider("Vocal Depth (Pitch)", -10, 10, -2)
v_speed = st.sidebar.slider("Speech Energy", 0.9, 1.2, 1.05)
v_volume = st.sidebar.slider("Gain (Mic Intensity)", 0, 10, 5)

# CAPTION STYLE (Restored & Enhanced)
st.sidebar.subheader("🎨 Caption Style")
t_color = st.sidebar.color_picker("Text Color", "#FFCC00") 
t_size = st.sidebar.slider("Font Size", 30, 90, 60)
cap_lang = st.sidebar.selectbox("Subtitle Type", ["English Translation", "Hinglish / Hindi"])

# --- 3. THE "REAL-VOICE" ENGINE ---
async def generate_pro_voice(text, voice, pitch, rate):
    # We use SSML to force natural human breathing patterns
    p_str = f"{pitch:+}Hz"
    r_str = f"{(rate-1)*100:+}%"
    
    # Adding 'Breaths' (silence) at commas and periods
    processed_text = text.replace(".", '<break time="700ms"/>').replace(",", '<break time="300ms"/>')
    
    ssml = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='hi-IN'>
        <voice name='{voice}'>
            <prosody pitch='{p_str}' rate='{r_str}'>
                {processed_text}
            </prosody>
        </voice>
    </speak>
    """
    communicate = edge_tts.Communicate(ssml, voice)
    await communicate.save("raw_speech.mp3")
    
    # Use FFmpeg to add 'Studio Compression' (Makes it sound expensive)
    # This removes the 'tinny' robot sound
    cmd = ["ffmpeg", "-y", "-i", "raw_speech.mp3", "-af", "highpass=f=200,lowpass=f=3000,volume=1.5", "final_speech.mp3"]
    subprocess.run(cmd)

# --- 4. MAIN INTERFACE ---
st.title("🎬 Avinash Sen: Ultra-Realistic Studio")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Enter Your Script")
    # PRO TIP: Use Devanagari (Hindi letters) for the most realistic Indian accent
    script = st.text_area("Write here:", "Namaste doston. Aaj main aapko dikhaunga... ki asli AI voice kaisi hoti hai.")
    
    if st.button("🔥 Generate Human Speech"):
        with st.spinner("Processing Studio Audio..."):
            asyncio.run(generate_pro_voice(script, selected_voice, v_pitch, v_speed))
            st.audio("final_speech.mp3")
            
        with st.spinner("Creating Typo Captions..."):
            task = "translate" if cap_lang == "English Translation" else "transcribe"
            result = whisper_engine.transcribe("final_speech.mp3", task=task, word_timestamps=True)
            
            # ASS Formatting
            ass_h = f"[Script Info]\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            lines = []
            for seg in result['segments']:
                for word in seg['words']:
                    s, e = word['start'], word['end']
                    t_in = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}"
                    t_out = f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                    
                    # TYPO: Random position + Bounce
                    clean_w = word['word'].strip().upper()
                    x, y = 320 + random.randint(-10, 10), 180 + random.randint(-10, 10)
                    lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{\\pos({x},{y})\\t(0,100,\\fscx130\\fscy130)\\t(100,200,\\fscx100\\fscy100)}}{clean_w}")

            with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_h + "\n".join(lines))
            st.success("Humanized Audio & Captions Ready!")

with col2:
    st.subheader("2. Video Render")
    bg_video = st.file_uploader("Upload Clip", type=["mp4"])
    if bg_video and st.button("🎥 Render Final Video"):
        with st.spinner("Hardcoding DNA..."):
            with open("bg.mp4", "wb") as f: f.write(bg_video.getbuffer())
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "final_speech.mp3", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "output.mp4"]
            subprocess.run(cmd)
            st.video("output.mp4")