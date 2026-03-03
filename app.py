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
st.set_page_config(page_title="Avinash Sen: Native Hindi Studio", layout="wide")

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

# --- 2. LOAD NATIVE HINDI ENGINES ---
@st.cache_resource
def init_tools():
    # Loading the Hindi-capable ONNX model
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. SIDEBAR: CUSTOMIZATION ---
st.sidebar.title("💎 Professional Controls")

# Native Hindi Voice Selection
st.sidebar.subheader("🎙️ Hindi Voice DNA")
# 'hf' = Hindi Female, 'hm' = Hindi Male
hindi_voices = {
    "hf_alpha": "Hindi Female (Sweet/Clear)",
    "hf_beta": "Hindi Female (Professional)",
    "hm_omega": "Hindi Male (Deep/Sigma)",
    "hm_psi": "Hindi Male (Energetic)"
}
v1 = st.sidebar.selectbox("Primary Hindi Voice", list(hindi_voices.keys()))
use_fusion = st.sidebar.checkbox("Enable Voice Fusion", value=True)
v2 = st.sidebar.selectbox("Fusion Partner", list(hindi_voices.keys()), index=1) if use_fusion else v1
mix_ratio = st.sidebar.slider("Fusion Mix %", 0, 100, 50) / 100
jitter = st.sidebar.slider("Anti-Reuse (Human Variation)", 0.01, 0.08, 0.03)

# Caption Styling
st.sidebar.subheader("✍️ Caption Designer")
cap_mode = st.sidebar.selectbox("Caption Content", ["English Translation", "Hindi (Devanagari)"])
t_color = st.sidebar.color_picker("Text Color", "#00F2FF") # Neon Cyan
t_size = st.sidebar.slider("Font Size", 30, 90, 55)
anim_style = st.sidebar.selectbox("Animation Style", ["Dynamic Typo", "Center Pop", "Static"])

# --- 4. MAIN INTERFACE ---
st.title("🎬 Native Hindi Viral Studio")
st.info("💡 **Realistic Hindi:** You can now type in **Hindi (नमस्ते)** or **Hinglish (Namaste)**. The 'h' models will handle both with a natural Indian accent.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Script Input")
    txt = st.text_area("Write your script here:", "नमस्ते दोस्तों, आज हम देखेंगे कि एआई की मदद से वीडियो कैसे बनाते हैं।")
    
    if st.button("🚀 Generate Human Hindi Audio"):
        with st.spinner("Synthesizing Native Speech..."):
            # Fusion Logic
            s1 = kokoro.get_voice_style(v1)
            s2 = kokoro.get_voice_style(v2)
            blended = (s1 * (1 - mix_ratio)) + (s2 * mix_ratio)
            
            # Anti-Reuse DNA Jitter
            noise = np.random.uniform(-jitter, jitter, blended.shape).astype(np.float32)
            samples, sr = kokoro.create(txt, voice=blended + noise, speed=1.0)
            sf.write("hindi_audio.wav", samples, sr)
            
        with st.spinner("Creating Translated Captions..."):
            # Whisper Task
            task = "translate" if cap_mode == "English Translation" else "transcribe"
            result = whisper_engine.transcribe("hindi_audio.wav", task=task, word_timestamps=True)
            
            # ASS Formatting
            font = "Arial" if cap_mode == "English Translation" else "Nirmala UI"
            ass_header = f"[Script Info]\nScriptType: v4.00+\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,{font},{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            ass_lines = []
            for seg in result['segments']:
                for word in seg['words']:
                    s, e = word['start'], word['end']
                    t_in = f"{int(s//3600):01}:{int((s%3600)//60):02}:{s%60:05.2f}"
                    t_out = f"{int(e//3600):01}:{int((e%3600)//60):02}:{e%60:05.2f}"
                    
                    clean_w = word['word'].strip().upper()
                    if anim_style == "Dynamic Typo":
                        pos = f"\\pos({random.randint(200,440)},{random.randint(120,240)})\\t(0,100,\\fscx120\\fscy120)\\t(100,200,\\fscx100,\\fscy100)"
                    elif anim_style == "Center Pop":
                        pos = f"\\pos(320,180)\\t(0,100,\\fscx140\\fscy140)\\t(100,200,\\fscx100,\\fscy100)"
                    else:
                        pos = f"\\pos(320,300)"
                        
                    ass_lines.append(f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{{pos}}}{clean_w}")

            with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_header + "\n".join(ass_lines))
            st.audio("hindi_audio.wav")
            st.success("✅ Native Hindi Audio Ready!")

with col2:
    st.subheader("2. Video Rendering")
    video_file = st.file_uploader("Upload BG Video", type=["mp4"])
    if video_file and st.button("🎥 Render Final Video"):
        with st.spinner("Burning Captions..."):
            with open("bg.mp4", "wb") as f: f.write(video_file.getbuffer())
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "hindi_audio.wav", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "viral.mp4"]
            subprocess.run(cmd)
            st.video("viral.mp4")
            with open("viral.mp4", "rb") as f: st.download_button("📥 Download MP4", f, "viral_hindi.mp4")