import streamlit as st
import subprocess
import whisper
import os
import random
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. CONFIG & HELPERS ---
st.set_page_config(page_title="Avinash Sen: Master Studio", layout="wide")

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

# --- 3. SIDEBAR: FULL CUSTOMIZATION ---
st.sidebar.title("🎨 Studio Controls")

# Voice & Fusion
st.sidebar.subheader("🎙️ Voice DNA")
voices = ["af_heart", "af_bella", "af_sky", "am_adam", "am_michael", "bf_emma", "bm_george"]
v1 = st.sidebar.selectbox("Primary Voice", voices)
use_fusion = st.sidebar.checkbox("Enable Voice Fusion", value=True)
v2 = st.sidebar.selectbox("Fusion Partner", voices, index=1) if use_fusion else v1
mix_ratio = st.sidebar.slider("Fusion Mix %", 0, 100, 50) / 100
jitter = st.sidebar.slider("Anti-Reuse (DNA Jitter)", 0.0, 0.1, 0.02)

# Caption Styling
st.sidebar.subheader("✍️ Caption Style")
cap_lang = st.sidebar.selectbox("Caption Language", ["English (Translated)", "Hinglish (Original)"])
t_color = st.sidebar.color_picker("Text Color", "#D4AF37") # Gold
t_size = st.sidebar.slider("Font Size", 20, 100, 50)
anim_type = st.sidebar.selectbox("Animation", ["Pop & Jump", "Center Pulse", "Static"])

# --- 4. MAIN INTERFACE ---
st.title("🎬 Ultra Viral Studio")
st.warning("⚠️ For clear Hindi speech, please type your script in English letters (e.g., 'Doston' instead of 'दोस्तों').")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Script Input")
    txt = st.text_area("Hinglish Script:", "Doston, aaj main aapko batane wala hoon ek kamaal ki AI trick. Let's go!")
    
    if st.button("🔥 Generate Unique Audio & Captions"):
        with st.spinner("Synthesizing Voice..."):
            # FIXED FUSION LOGIC
            s1 = kokoro.get_voice_style(v1)
            s2 = kokoro.get_voice_style(v2)
            blended = (s1 * (1 - mix_ratio)) + (s2 * mix_ratio)
            
            # Apply Anti-Reuse Jitter
            noise = np.random.uniform(-jitter, jitter, blended.shape).astype(np.float32)
            final_voice = blended + noise
            
            samples, sr = kokoro.create(txt, voice=final_voice, speed=1.1)
            sf.write("speech.wav", samples, sr)
            
        with st.spinner("Processing Typo Animations..."):
            # Translation Task
            task_type = "translate" if cap_lang == "English (Translated)" else "transcribe"
            result = whisper_engine.transcribe("speech.wav", task=task_type, word_timestamps=True)
            
            # ASS Formatting
            ass_header = f"[Script Info]\nScriptType: v4.00+\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            ass_lines = []
            for seg in result['segments']:
                for word in seg['words']:
                    s, e = word['start'], word['end']
                    t_in = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}"
                    t_out = f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                    
                    # Style Logic
                    clean_w = word['word'].strip().upper()
                    if anim_type == "Pop & Jump":
                        pos = f"\\pos({random.randint(150,490)},{random.randint(100,260)})\\t(0,100,\\fscx120\\fscy120)\\t(100,200,\\fscx100,\\fscy100)"
                    elif anim_type == "Center Pulse":
                        pos = f"\\pos(320,180)\\t(0,100,\\fscx130\\fscy130)\\t(100,200,\\fscx100,\\fscy100)"
                    else:
                        pos = f"\\pos(320,300)"
                        
                    ass_lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{{pos}}}{clean_w}")

            with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_header + "\n".join(ass_lines))
            st.audio("speech.wav")
            st.success("✅ Audio & Translated Script Ready!")

with col2:
    st.subheader("2. Final Video Render")
    video_file = st.file_uploader("Upload Background", type=["mp4"])
    if video_file and st.button("🎥 Render Viral Video"):
        with st.spinner("Merging Audio + Dynamic Captions..."):
            with open("bg.mp4", "wb") as f: f.write(video_file.getbuffer())
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "speech.wav", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "viral.mp4"]
            subprocess.run(cmd)
            st.video("viral.mp4")
            with open("viral.mp4", "rb") as f: st.download_button("📥 Download Result", f, "viral_final.mp4")

# --- 5. HISTORY ---
st.markdown("---")
if st.button("💾 Save to History"):
    st.session_state.history.append(f"Script: {txt[:50]}...")
    st.success("Saved!")