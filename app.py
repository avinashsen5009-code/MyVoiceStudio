import streamlit as st
import os
import random
import subprocess
from openai import OpenAI
import whisper

# --- 1. PRO SETUP ---
st.set_page_config(page_title="Avinash Sen: 100% Human Studio", layout="wide")

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

# --- 2. SIDEBAR: THE ELITE CONTROLS ---
st.sidebar.title("💎 Elite Human Engine")
api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")

# These models are trained on real human speech samples
voice_options = {
    "echo": "Deep Male (Smooth/Calm)",
    "onyx": "Deep Male (Powerful/Sigma)",
    "shimmer": "Clear Female (Energetic)",
    "nova": "Warm Female (Professional)"
}

selected_voice = st.sidebar.selectbox("Select Actor Voice", list(voice_options.keys()), format_func=lambda x: voice_options[x])

st.sidebar.subheader("🎨 Caption Designer")
t_color = st.sidebar.color_picker("Text Color", "#00F2FF") # Neon Cyan
t_size = st.sidebar.slider("Font Size", 30, 100, 60)
cap_lang = st.sidebar.selectbox("Subtitle Language", ["English (Translated)", "Original (Hinglish/Hindi)"])

# --- 3. THE "HUMAN" PERFORMANCE ENGINE ---
def generate_elite_voice(api_key, text, voice):
    client = OpenAI(api_key=api_key)
    # Using 'tts-1-hd' for the highest possible bitrate/realism
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text
    )
    response.stream_to_file("speech.mp3")

# --- 4. MAIN INTERFACE ---
st.title("🎙️ Avinash Sen: 100% Reality Studio")
st.warning("🚀 This engine uses HD Neural models for zero robotic sound.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Script (Hindi/Hinglish)")
    script = st.text_area("Script:", "Doston... aaj main aapko ek aisi baat batane wala hoon, jo aapki zindagi badal degi. Believe me.")
    
    if st.button("🔥 Generate 100% Human Voice"):
        if not api_key:
            st.error("Please enter your OpenAI API Key in the sidebar!")
        else:
            with st.spinner("Recording 'Real' Performance..."):
                generate_elite_voice(api_key, script, selected_voice)
                st.audio("speech.mp3")
                
            with st.spinner("Processing Viral Captions..."):
                model = whisper.load_model("base")
                task = "translate" if cap_lang == "English (Translated)" else "transcribe"
                result = model.transcribe("speech.mp3", task=task, word_timestamps=True)
                
                ass_h = f"[Script Info]\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                
                lines = []
                for seg in result['segments']:
                    for word in seg['words']:
                        s, e = word['start'], word['end']
                        t_in = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}"
                        t_out = f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                        
                        clean_w = word['word'].strip().upper()
                        x, y = 320 + random.randint(-15, 15), 180 + random.randint(-10, 10)
                        lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{\\pos({x},{y})\\t(0,100,\\fscx135\\fscy135)\\t(100,200,\\fscx100\\fscy100)}}{clean_w}")

                with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_h + "\n".join(lines))
                st.success("Human Performance Captured!")

with col2:
    st.subheader("2. Final Rendering")
    video_file = st.file_uploader("Background Clip", type=["mp4"])
    if video_file and st.button("🎥 Render Final Viral Video"):
        with st.spinner("Burning DNA & Subtitles..."):
            with open("bg.mp4", "wb") as f: f.write(video_file.getbuffer())
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "speech.mp3", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "output.mp4"]
            subprocess.run(cmd)
            st.video("output.mp4")