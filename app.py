import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
import math
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="NEON KOKORO V4", page_icon="🌌", layout="wide")

# Futuristic Cyberpunk CSS
st.markdown("""
    <style>
    .main { background-color: #060606; color: #e0e0e0; }
    div[data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 1px solid #00f2fe; }
    .stTextArea textarea { background-color: #1a1a1a !important; color: #00f2fe !important; border: 1px solid #333 !important; }
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #00f2fe, #4facfe);
        color: black; font-weight: bold; border-radius: 5px; border: none;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
    }
    .history-card { background: #111; border-left: 5px solid #00f2fe; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- STABLE ENGINE LOADER ---
@st.cache_resource
def load_kokoro():
    REPO_ID = "leonelhs/kokoro-thewh1teagle"
    try:
        model_path = hf_hub_download(repo_id=REPO_ID, filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id=REPO_ID, filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Engine Failure: {e}")
        return None

kokoro = load_kokoro()

# --- UTILITY: SRT GENERATOR ---
def generate_srt(text, duration):
    words = text.split()
    if not words: return ""
    
    avg_word_dur = duration / len(words)
    srt_content = ""
    
    for i, word in enumerate(words):
        start_time = i * avg_word_dur
        end_time = (i + 1) * avg_word_dur
        
        def format_time(seconds):
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            msecs = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02}:{mins:02}:{secs:02},{msecs:03}"
        
        srt_content += f"{i+1}\n{format_time(start_time)} --> {format_time(end_time)}\n{word}\n\n"
    return srt_content

# --- INITIALIZE SESSION ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- VOICE DIRECTORY ---
VOICES = {
    "af_bella": "🎙️ News/Business (Female)",
    "af_sarah": "✨ Friendly/Podcast (Female)",
    "am_adam": "🎬 Movie Trailer (Male)",
    "am_onyx": "🌑 Dark/Authoritative (Male)",
    "af_sky": "🎭 Energetic/Anime (Female)",
    "am_michael": "👨‍🏫 Educational (Male)"
}

# --- MAIN INTERFACE ---
st.title("🌌 NEON KOKORO STUDIO v4.0")
st.write("Next-Gen Voice Synthesis with Auto-Subtitles")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("🎛️ Control Panel")
    mode = st.tabs(["Single Mode", "Hybrid (Mix) Mode"])
    
    with mode[0]:
        v_choice = st.selectbox("Select Personality", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    
    with mode[1]:
        v1 = st.selectbox("Base Voice", list(VOICES.keys()), index=0, key="v1")
        v2 = st.selectbox("Target Voice", list(VOICES.keys()), index=2, key="v2")
        mix_ratio = st.slider("Mix Ratio", 0.0, 1.0, 0.5)

    speed = st.slider("Flow Speed", 0.5, 2.0, 1.0)
    text_input = st.text_area("📜 Script", placeholder="Enter your script here...", height=250)
    
    gen_btn = st.button("🚀 INITIATE SYNTHESIS")

with col2:
    st.header("⚡ Output Console")
    if gen_btn and text_input.strip():
        try:
            with st.spinner("Rendering quantum audio..."):
                # Synthesis Logic
                if "Single" in str(mode):
                    samples, sample_rate = kokoro.create(text_input, voice=v_choice, speed=speed, lang="en-us")
                    final_voice = v_choice
                else:
                    s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(v2)
                    mixed = (s1 * (1 - mix_ratio)) + (s2 * mix_ratio)
                    samples, sample_rate = kokoro.create(text_input, voice=mixed, speed=speed, lang="en-us")
                    final_voice = f"Mix({v1}/{v2})"

                # Audio Export
                buf = io.BytesIO()
                sf.write(buf, samples, sample_rate, format='WAV')
                audio_data = buf.getvalue()
                duration = len(samples) / sample_rate

                # SRT Export
                srt_data = generate_srt(text_input, duration)

                # UI Display
                st.audio(audio_data)
                st.success(f"Generated {duration:.2f}s of audio")
                
                # Downloads
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button("📥 Download WAV", audio_data, "voice.wav", "audio/wav")
                with dl2:
                    st.download_button("📥 Download SRT", srt_data, "subtitles.srt", "text/plain")

                # History Save
                st.session_state.history.insert(0, {
                    "time": datetime.now().strftime("%H:%M"),
                    "voice": final_voice,
                    "text": text_input[:40] + "...",
                    "audio": audio_data,
                    "srt": srt_data
                })
        except Exception as e:
            st.error(f"Critical System Error: {e}")
    else:
        st.info("System Ready. Awaiting Script Input...")

# --- HISTORY SECTION ---
st.markdown("---")
st.subheader("🕒 Production History")
if st.session_state.history:
    for i, item in enumerate(st.session_state.history[:5]):
        with st.container():
            st.markdown(f"""<div class="history-card"><b>{item['time']} | {item['voice']}</b><br>{item['text']}</div>""", unsafe_allow_html=True)
            h_col1, h_col2 = st.columns([2, 1])
            with h_col1: st.audio(item['audio'])
            with h_col2: st.download_button("Get SRT", item['srt'], f"subs_{i}.srt", key=f"srt_{i}")
else:
    st.caption("History will appear here after your first generation.")