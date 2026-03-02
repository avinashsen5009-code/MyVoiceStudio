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
    .main { 
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="column"] > div {
        background: rgba(30, 41, 59, 0.45) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 2.5rem !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
        margin-bottom: 1.5rem;
    }
    h1, h2, h3 { 
        color: #fbbf24; 
        text-transform: uppercase; 
        letter-spacing: 3px; 
        font-weight: 900;
        border-bottom: 2px solid rgba(251, 191, 36, 0.2);
    }
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
    }
    .stButton>button:active {
        transform: translateY(4px);
        box-shadow: 0 0px 0 #b45309;
    }
    .stTextArea textarea { 
        background-color: #020617 !important; 
        color: #fbbf24 !important; 
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ENGINE LOADER ---
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

# --- 4. APP LAYOUT ---
st.title("💎 AVINASH SEN VOICE STUDIO")
st.caption("DOMAIN EXPANSION: PROFESSIONAL AI VOICE SYNTHESIS v7.0")

col_ctrl, col_main, col_mon = st.columns([1, 1.3, 1])

with col_ctrl:
    st.subheader("⚙️ CORE CONTROLS")
    
    # PASTE YOUR GOOGLE IMAGE LINK HERE
    # I've put a reliable Gojo link below as a default
    gojo_url = "https://pin.it/fZ6SoZr4s"
    st.image(gojo_url, caption="SATORU GOJO | THE STRONGEST", use_container_width=True)
    
    st.markdown("---")
    VOICES = {
        "GOJO_MODE": "🌌 GOJO (UNLIMITED VOID)",
        "am_fenrir": "🐺 FENRIR (DEEP GRAVEL)",
        "af_sky": "🎭 SKY (ANIME ENERGY)",
        "af_bella": "🎙️ BELLA (BUSINESS PRO)",
        "am_onyx": "🌑 ONYX (CINEMATIC DARK)"
    }
    
    v_choice = st.selectbox("VOICE IDENTITY", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    speed = st.slider("SPEECH TEMPO", 0.5, 2.0, 1.05)
    
    if st.button("🔄 REBOOT ENGINE"):
        st.cache_resource.clear()
        st.rerun()

with col_main:
    st.subheader("📝 SCRIPT MASTER")
    text_input = st.text_area("Dialogue", placeholder="What is your command, Master Avinash?", height=420, label_visibility="collapsed")
    
    if st.button("⚡ INITIATE MASTER SYNTHESIS"):
        if text_input.strip() and kokoro:
            with st.spinner("EXPANDING DOMAIN..."):
                if v_choice == "GOJO_MODE":
                    s1 = kokoro.get_voice_style("am_onyx")
                    s2 = kokoro.get_voice_style("af_sky")
                    mixed = (s1 * 0.70) + (s2 * 0.30)
                    samples, sample_rate = kokoro.create(text_input, voice=mixed, speed=speed, lang="en-us")
                else:
                    samples, sample_rate = kokoro.create(text_input, voice=v_choice, speed=speed, lang="en-us")
                
                buf = io.BytesIO()
                sf.write(buf, samples, sample_rate, format='WAV')
                st.session_state.final_audio = buf.getvalue()
                st.session_state.vname = v_choice

with col_mon:
    st.subheader("🎧 MONITOR")
    if 'final_audio' in st.session_state:
        st.success(f"IDENTITY: {st.session_state.vname}")
        st.audio(st.session_state.final_audio, format="audio/wav")
        st.download_button("WAV MASTER 📥", st.session_state.final_audio, f"master.wav")
    else:
        st.info("AWAITING SIGNAL")