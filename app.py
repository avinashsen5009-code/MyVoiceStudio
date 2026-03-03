import streamlit as st
import subprocess
import whisper
import os
import random
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. HELPERS & CONFIG ---
st.set_page_config(page_title="Avinash Sen: Translator Studio", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{msecs:03d}"

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

# --- 2. LOAD AI ENGINES ---
@st.cache_resource
def init_tools():
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    # Using 'base' model for fast translation
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. SIDEBAR: TYPO & VOICE STYLING ---
st.sidebar.title("🎨 Style & DNA")
t_color = st.sidebar.color_picker("Caption Color", "#D4AF37") # Gold
t_size = st.sidebar.slider("Font Size", 20, 100, 50)
jitter = st.sidebar.slider("Voice Jitter (Anti-Reuse)", 0.01, 0.10, 0.03)

# --- 4. MAIN INTERFACE ---
st.title("🎬 Hindi Speech ➔ English Typo")
st.info("💡 **Rule for Clarity:** Write Hindi words in English letters (e.g., 'Namaste' instead of 'नमस्ते').")

tab_creator, tab_history = st.tabs(["🚀 Creation Dashboard", "📜 Work Log"])

with tab_creator:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Audio Generation")
        # Example Script: "Doston, aaj hum baat karenge AI ke baare mein. It's truly amazing!"
        txt = st.text_area("Script (Hinglish)", "Doston, kya aap jaante hain ki AI kaise kaam karta hai? Let's find out.")
        
        voices = ["af_heart", "af_bella", "af_sky", "am_adam", "am_michael", "bf_emma", "bm_george"]
        v1 = st.selectbox("Primary Voice", voices)
        use_fusion = st.checkbox("Enable Fusion (Unique Blend)")
        v2 = st.selectbox("Partner Voice", voices, index=1) if use_fusion else v1
        
        if st.button("🎙️ Generate Voice & Translate"):
            with st.spinner("Blending Unique Voice..."):
                s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(v2)
                # Mathematical Fusion + Neural Jitter
                blended = (s1 * 0.5) + (s2 * 0.5)
                unique_dna = blended + np.random.uniform(-jitter, jitter, blended.shape).astype(np.float32)
                
                samples, sr = kokoro.create(txt, voice=unique_dna, speed=1.1)
                sf.write("speech.wav", samples, sr)
            
            with st.spinner("Translating Speech to English Captions..."):
                # TASK="TRANSLATE" turns Hindi speech into English text
                result = whisper_engine.transcribe("speech.wav", task="translate", word_timestamps=True)
                
                ass_header = f"[Script Info]\nScriptType: v4.00+\nPlayResX: 640\nPlayResY: 360\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV\nStyle: Default,Arial,{t_size},{hex_to_ass(t_color)},&H00000000,1,3,2,20\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                
                ass_lines = []
                for seg in result['segments']:
                    for word in seg['words']:
                        s, e = word['start'], word['end']
                        t_in, t_out = format_timestamp(s)[3:], format_timestamp(e)[3:] # ASS format uses shorter timestamps
                        
                        # Typo: Random Jumping Position
                        x, y = random.randint(150, 490), random.randint(100, 260)
                        clean_w = word['word'].strip().upper()
                        
                        ass_lines.append(f"Dialogue: 0,0:{t_in},0:{t_out},Default,,0,0,0,,{{\\pos({x},{y})\\t(0,100,\\fscx120\\fscy120)\\t(100,200,\\fscx100,\\fscy100)}}{clean_w}")

                with open("typo.ass", "w", encoding="utf-8") as f: f.write(ass_header + "\n".join(ass_lines))
                st.audio("speech.wav")
                st.success("✅ Audio & Translated Typo Script Ready!")

    with col2:
        st.subheader("2. Final Render")
        video_file = st.file_uploader("Background Video", type=["mp4"])
        if video_file and st.button("🎥 Render English Captions"):
            with open("bg.mp4", "wb") as f: f.write(video_file.getbuffer())
            # FFmpeg: Merging audio and burning the translated ASS file
            cmd = ["ffmpeg", "-y", "-i", "bg.mp4", "-i", "speech.wav", "-vf", "ass=typo.ass", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "final.mp4"]
            subprocess.run(cmd)
            st.video("final.mp4")
            with open("final.mp4", "rb") as f: st.download_button("📥 Download Viral Edit", f, "final_video.mp4")

with tab_history:
    st.write("Session History will appear here...")