import streamlit as st
import subprocess
import whisper
import os
import random
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. SETTINGS & HELPERS ---
st.set_page_config(page_title="Avinash Sen: Ultra Studio", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

def hex_to_ass(hex_color):
    """Converts #RRGGBB to ASS &HBBGGRR"""
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

# --- 2. LOAD AI ENGINES ---
@st.cache_resource
def init_tools():
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. SIDEBAR: VOICE & CAPTION PRO ---
st.sidebar.title("🧬 Voice DNA & Style")

# Anti-Reuse Settings
st.sidebar.subheader("Algorithm Protection")
dna_jitter = st.sidebar.slider("DNA Randomization (Anti-Reuse)", 0.0, 0.1, 0.02, help="Adds tiny variations so the voice is never flagged as 'Reused Content'")
speed_jitter = st.sidebar.slider("Speed Variation", 0.8, 1.5, 1.1)

# Caption Styles
st.sidebar.subheader("Caption Visuals")
anim_style = st.sidebar.selectbox("Animation Style", ["Random Jump", "Center Shake", "Zoom In", "Static Bottom"])
t_color = st.sidebar.color_picker("Text Color", "#D4AF37") # Gold
t_size = st.sidebar.slider("Font Size", 20, 100, 55)

# --- 4. MAIN INTERFACE ---
st.title("🎬 Avinash Sen Ultra Studio")

tab_creator, tab_history = st.tabs(["🚀 Viral Engine", "📜 Work Log"])

with tab_creator:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Script & Fusion")
        txt = st.text_area("What's the story?", "They told me I couldn't do it. So I did it twice.")
        
        # Expanded Voice List
        voices = ["af_heart", "af_bella", "af_nicole", "af_sky", "am_adam", "am_michael", "bf_emma", "bm_george", "bm_lewis"]
        v1 = st.selectbox("Primary Voice", voices)
        use_fusion = st.checkbox("Enable Fusion (Unique Blend)")
        v2 = st.selectbox("Partner Voice", voices, index=1) if use_fusion else v1
        mix = st.sidebar.slider("Fusion Mix %", 0, 100, 50) / 100

        if st.button("🔥 Generate Unique Audio"):
            with st.spinner("Blending Neural DNA..."):
                # FIX: Explicitly handle the voice style arrays
                s1 = kokoro.get_voice_style(v1)
                s2 = kokoro.get_voice_style(v2)
                
                # The Fusion Formula
                blended = (s1 * (1 - mix)) + (s2 * mix)
                
                # Add Anti-Reuse Jitter
                noise = np.random.uniform(-dna_jitter, dna_jitter, blended.shape).astype(np.float32)
                unique_voice = blended + noise
                
                samples, sr = kokoro.create(txt, voice=unique_voice, speed=speed_jitter)
                sf.write("unique_audio.wav", samples, sr)
                
            with st.spinner("Creating Word-Level Animation..."):
                result = whisper_engine.transcribe("unique_audio.wav", word_timestamps=True)
                
                # ASS Header
                ass_header = f"[Script Info]\nScriptType: v4.00+\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                
                ass_lines = []
                for seg in result['segments']:
                    for word in seg['words']:
                        s, e = word['start'], word['end']
                        t_in = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}"
                        t_out = f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                        
                        # Animation Logic
                        clean_word = word['word'].strip().upper()
                        if anim_style == "Random Jump":
                            pos = f"\\pos({random.randint(150,490)},{random.randint(100,260)})"
                        elif anim_style == "Center Shake":
                            pos = f"\\pos({320+random.randint(-10,10)},{180+random.randint(-10,10)})"
                        elif anim_style == "Zoom In":
                            pos = f"\\pos(320,180)\\fscx150\\fscy150\\t(0,100,\\fscx100,\\fscy100)"
                        else:
                            pos = f"\\pos(320,300)"
                            
                        ass_lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{{pos}}}{clean_word}")

                with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_header + "\n".join(ass_lines))
                
                st.session_state.history.append(f"Voice: {v1}+{v2} | Text: {txt[:40]}...")
                st.audio("unique_audio.wav")
                st.success("DNA Generated. Ready to Render.")

    with col2:
        st.subheader("2. Final Rendering")
        video_file = st.file_uploader("Upload Video Background", type=["mp4"])
        if video_file and st.button("🎥 Render for YouTube/Reels"):
            with st.spinner("Hardcoding DNA & Animations..."):
                with open("bg.mp4", "wb") as f: f.write(video_file.getbuffer())
                cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "unique_audio.wav", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "viral.mp4"]
                subprocess.run(cmd)
                st.video("viral.mp4")
                with open("viral.mp4", "rb") as f: st.download_button("📥 Download Viral Video", f, "viral_video.mp4")

with tab_history:
    st.subheader("Session Downloads")
    full_log = "\n".join(st.session_state.history)
    st.text_area("History Summary", full_log, height=200)
    st.download_button("💾 Download History .txt", full_log, "studio_history.txt")