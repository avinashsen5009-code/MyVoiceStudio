import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- 1. CORE STUDIO CONFIGURATION ---
st.set_page_config(page_title="AVINASH SEN VOICE STUDIO", page_icon="💎", layout="wide")

# --- 2. THEME ENGINE: CYBER-GOLD 3D ---
st.markdown("""
    <style>
    /* Professional Deep Dark Background */
    .main { 
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* 3D Glassmorphism Panel Styling */
    div[data-testid="column"] > div {
        background: rgba(30, 41, 59, 0.45) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 2.5rem !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
        margin-bottom: 1.5rem;
    }

    /* Luminous Gold Typography */
    h1, h2, h3 { 
        color: #fbbf24; 
        text-transform: uppercase; 
        letter-spacing: 3px; 
        font-weight: 900;
        border-bottom: 2px solid rgba(251, 191, 36, 0.2);
        padding-bottom: 10px;
    }

    /* Professional 3D Tactical Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: #020617 !important;
        font-weight: 800;
        border-radius: 12px;
        border: none;
        height: 60px;
        box-shadow: 0 5px 0 #b45309, 0 12px 20px rgba(245, 158, 11, 0.3);
        transition: all 0.1s ease;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        transform: translateY(2px);
        box-shadow: 0 3px 0 #b45309, 0 8px 15px rgba(245, 158, 11, 0.4);
    }
    .stButton>button:active {
        transform: translateY(5px);
        box-shadow: 0 0px 0 #b45309;
    }

    /* Blackbox Script Input */
    .stTextArea textarea { 
        background-color: #020617 !important; 
        color: #fbbf24 !important; 
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        padding: 15px !important;
    }
    
    /* Smooth Transitions */
    .stAudio { border-radius: 50px; overflow: hidden; background: #fbbf24; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STABLE AI ENGINE LOADER ---
@st.cache_resource(show_spinner=False)
def load_studio_engine():
    try:
        m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
        v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
        return Kokoro(m, v)
    except Exception as e:
        st.error(f"SYSTEM OFFLINE: {e}")
        return None

kokoro = load_studio_engine()

# --- 4. SRT GENERATOR UTILITY ---
def generate_srt(text, dur):
    words = text.split(); srt = ""
    if not words: return ""
    step = dur / len(words)
    for i, w in enumerate(words):
        f = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},000"
        srt += f"{i+1}\n{f(i*step)} --> {f((i+1)*step)}\n{w}\n\n"
    return srt

# --- 5. APP LAYOUT ---
st.title("💎 AVINASH SEN VOICE STUDIO")
st.caption("DOMAIN EXPANSION: PROFESSIONAL AI VOICE SYNTHESIS v6.5")

col_ctrl, col_main, col_mon = st.columns([1, 1.3, 1])

# --- SIDEBAR & CONTROL PANEL ---
with col_ctrl:
    st.subheader("⚙️ CORE CONTROLS")
    
    # 3D GOJO CHARACTER IMAGE
    # Using a high-quality static URL for Gojo to ensure he appears instantly
    st.image("https://raw.githubusercontent.com/leonelhs/kokoro-thewh1teagle/main/media/gojo_monitor_v1.png", 
             caption="SATORU GOJO | STUDIO GUARDIAN", use_container_width=True)
    
    st.markdown("---")
    VOICES = {
        "GOJO_MODE": "🌌 GOJO (UNLIMITED VOID)",
        "am_fenrir": "🐺 FENRIR (DEEP GRAVEL)",
        "af_sky": "🎭 SKY (ANIME ENERGY)",
        "af_bella": "🎙️ BELLA (BUSINESS PRO)",
        "am_onyx": "🌑 ONYX (CINEMATIC DARK)",
        "af_heart": "💖 HEART (SOFT/KIND)"
    }
    
    v_choice = st.selectbox("VOICE IDENTITY", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    speed = st.slider("SPEECH TEMPO", 0.5, 2.0, 1.05)
    
    if st.button("🔄 REBOOT ENGINE"):
        st.cache_resource.clear()
        st.rerun()

# --- MAIN SCRIPTING CONSOLE ---
with col_main:
    st.subheader("📝 SCRIPT MASTER")
    text_input = st.text_area("Dialogue", placeholder="What is your command, Master Avinash?", height=420, label_visibility="collapsed")
    
    if st.button("⚡ INITIATE MASTER SYNTHESIS"):
        if text_input.strip() and kokoro:
            try:
                with st.spinner("EXPANDING DOMAIN..."):
                    ts = int(time.time())
                    
                    # Logic for Gojo Mode (The Infinity Blend)
                    if v_choice == "GOJO_MODE":
                        s1 = kokoro.get_voice_style("am_onyx")
                        s2 = kokoro.get_voice_style("af_sky")
                        mixed = (s1 * 0.70) + (s2 * 0.30)
                        samples, sample_rate = kokoro.create(text_input, voice=mixed, speed=speed, lang="en-us")
                    else:
                        samples, sample_rate = kokoro.create(text_input, voice=v_choice, speed=speed, lang="en-us")
                    
                    buf = io.BytesIO()
                    sf.write(buf, samples, sample_rate, format='WAV')
                    
                    # Store in Session State to prevent "No key" error
                    st.session_state.final_audio = buf.getvalue()
                    st.session_state.final_vname = v_choice
                    st.session_state.final_dur = len(samples)/sample_rate
                    st.session_state.final_srt = generate_srt(text_input, st.session_state.final_dur)
                    st.session_state.ts = ts
            except Exception as e:
                st.error(f"ENGINE ERROR: {e}")

# --- PRODUCTION MONITOR ---
with col_mon:
    st.subheader("🎧 MONITOR")
    if 'final_audio' in st.session_state:
        st.markdown(f"**STATUS:** ONLINE")
        st.markdown(f"**IDENTITY:** {st.session_state.final_vname}")
        
        # Audio Player with no 'key' argument to avoid Streamlit errors
        st.audio(st.session_state.final_audio, format="audio/wav")
        st.info(f"DURATION: {st.session_state.final_dur:.2f}s")
        
        st.markdown("### 📥 EXPORT HUB")
        d1, d2 = st.columns(2)
        d1.download_button("WAV MASTER 📥", st.session_state.final_audio, f"master_{st.session_state.ts}.wav")
        d2.download_button("SRT SUBS 📜", st.session_state.final_srt, f"subs_{st.session_state.ts}.srt")
    else:
        st.info("SYSTEM IDLE: AWAITING SIGNAL")

# --- SESSION LOGS ---
st.markdown("---")
st.caption(f"© 2026 AVINASH SEN | MASTER PRODUCTION ENVIRONMENT")