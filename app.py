import streamlit as st
import asyncio
import edge_tts
import whisper
import os
import random
import subprocess

# --- 1. SETUP ---
st.set_page_config(page_title="Avinash Sen: Ultra Real Studio", layout="wide")

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_engine = load_whisper()

# --- 2. SIDEBAR: THE REALISM DIALS ---
st.sidebar.title("🧬 ElevenLabs Mode")
st.sidebar.warning("Using SSML Injection for Human Emotions")

voices_dict = {
    "hi-IN-MadhurNeural": "Deep Male (Sigma/Boss)",
    "hi-IN-SwararaNeural": "Smooth Female (Vlog/Story)"
}

selected_voice = st.sidebar.selectbox("Voice Model", list(voices_dict.keys()), format_func=lambda x: voices_dict[x])
emotion_level = st.sidebar.slider("Emotional Range (Pitch)", 0, 50, 25)
pause_duration = st.sidebar.slider("Breath Gap (ms)", 100, 800, 400)

# Caption Customization
st.sidebar.subheader("🎨 Typo Style")
t_color = st.sidebar.color_picker("Text Color", "#00FF00") # Neon Green
t_size = st.sidebar.slider("Font Size", 30, 100, 60)

# --- 3. THE "HUMANIZER" ENGINE (SSML) ---
async def generate_human_voice(text, voice, emotion, gap):
    # This turns plain text into 'Emotional SSML'
    # It adds a pitch contour and a 'breath' pause after every comma/period
    ssml = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='hi-IN'>
        <voice name='{voice}'>
            <prosody pitch='+{emotion}Hz' rate='+5%' contour='(0%,+0%) (25%,+15%) (50%,-10%) (100%,+0%)'>
                {text.replace(',', f'<break time="{gap}ms"/>').replace('.', f'<break time="{gap+200}ms"/>')}
            </prosody>
        </voice>
    </speak>
    """
    communicate = edge_tts.Communicate(ssml, voice)
    await communicate.save("speech.mp3")

# --- 4. MAIN INTERFACE ---
st.title("🎙️ Avinash Sen: Reality Engine")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Script (Hindi/Hinglish)")
    script = st.text_area("Your Script:", "Doston... kya aapne kabhi socha hai? Ki AI ek insaan ki tarah kaise bol sakta hai. Yeh kamaal hai.")
    
    cap_lang = st.radio("Caption Language", ["English (Translated)", "Hinglish (Original)"], horizontal=True)

    if st.button("🔥 Generate Non-Robotic Voice"):
        with st.spinner("Injecting Vocal Shimmer & Breaths..."):
            asyncio.run(generate_human_voice(script, selected_voice, emotion_level, pause_duration))
            st.audio("speech.mp3")
            
        with st.spinner("Creating High-Energy Typo..."):
            task = "translate" if cap_lang == "English (Translated)" else "transcribe"
            result = whisper_engine.transcribe("speech.mp3", task=task, word_timestamps=True)
            
            ass_h = f"[Script Info]\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            lines = []
            for seg in result['segments']:
                for word in seg['words']:
                    s, e = word['start'], word['end']
                    t_in, t_out = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}", f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                    
                    # TYPO: Dynamic Bounce & Random Position
                    clean_w = word['word'].strip().upper()
                    x, y = 320 + random.randint(-20, 20), 180 + random.randint(-15, 15)
                    lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{\\pos({x},{y})\\t(0,100,\\fscx140\\fscy140)\\t(100,200,\\fscx100\\fscy100)}}{clean_w}")

            with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_h + "\n".join(lines))
            st.success("Humanized Audio & Typo Ready!")

with col2:
    st.subheader("2. Final Render")
    bg_video = st.file_uploader("Upload Video", type=["mp4"])
    if bg_video and st.button("🎥 Render Viral Reel"):
        with st.spinner("Merging..."):
            with open("bg.mp4", "wb") as f: f.write(bg_video.getbuffer())
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "speech.mp3", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "output.mp4"]
            subprocess.run(cmd)
            st.video("output.mp4")