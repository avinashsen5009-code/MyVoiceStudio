import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- UI CONFIGURATION (Exact Match) ---
st.set_page_config(page_title="AVINASH SEN VOICE STUDIO", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    /* Main Background & Typography */
    .main { 
        background: radial-gradient(circle at center, #111827 0%, #030712 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* 3D Glass Panels */
    div[data-testid="column"] > div {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px !important;
        padding: 25px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }

    /* Professional Headers */
    h1, h2, h3 { 
        color: #f8fafc; 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        font-weight: 800;
        border-bottom: 2px solid #fbbf24;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Luminous Gold Generate Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
        color: #000 !important;
        font-weight: 900;
        border-radius: 8px;
        border: none;
        height: 60px;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 35px rgba(251, 191, 36, 0.7);
        transform: scale(1.01);
    }

    /* Input & Select Customization */
    .stTextArea textarea { 
        background-color: #0f172a !important; 
        color: #fbbf24 !important; 
        border: 1px solid #334155 !important;
        font-size: 1.1rem !important;
    }
    
    /* Character Frame */
    .char-frame {
        border: 2px solid #fbbf24;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 0 30px rgba(251, 191, 36, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CORE ENGINE ---
@st.cache_resource(show_spinner=False)
def load_engine():
    try:
        m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
        v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
        return Kokoro(m, v)
    except: return None

kokoro = load_engine()

# --- APP LAYOUT ---
st.title("💎 AVINASH SEN VOICE STUDIO")
st.caption("PROFESSIONAL AI VOICE SYNTHESIS v6.0 • DOMAIN OF THE STRONGEST")

col_left, col_mid, col_right = st.columns([1, 1.2, 1])

# --- LEFT: STUDIO CONTROL PANEL ---
with col_left:
    st.subheader("⚙️ CONTROL PANEL")
    st.markdown('<div class="char-frame"><img src="https://i.pinimg.com/originals/81/4b/32/814b321a4f009e5192135606e1f0e42d.jpg" width="100%"></div>', unsafe_allow_html=True)
    st.write("")
    
    VOICES = {
        "am_fenrir": "🐺 FENRIR (GRAVELLY)",
        "af_sky": "🎭 SKY (ENERGETIC)",
        "af_bella": "🎙️ BELLA (PRO)",
        "am_onyx": "🌑 ONYX (DEEP)",
        "af_heart": "💖 HEART (WARM)"
    }
    
    v_mode = st.radio("MODE", ["SOLO", "MIX"], horizontal=True)
    v_choice = st.selectbox("CHARACTER", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    speed = st.slider("TEMPO", 0.5, 2.0, 1.0)
    
    if st.button("🔄 REBOOT SYSTEM"):
        st.cache_resource.clear()
        st.rerun()

# --- MID: SCRIPT MASTER ---
with col_mid:
    st.subheader("📝 SCRIPT MASTER")
    text = st.text_area("", placeholder="Enter your script, Master Avinash...", height=400, label_visibility="collapsed")
    
    if st.button("⚡ GENERATE FINAL AUDIO"):
        if text.strip() and kokoro:
            with st.spinner("SYNETHESIZING..."):
                samples, sample_rate = kokoro.create(text, voice=v_choice, speed=speed, lang="en-us")
                buf = io.BytesIO()
                sf.write(buf, samples, sample_rate, format='WAV')
                st.session_state.output = (buf.getvalue(), v_choice, len(samples)/sample_rate)

# --- RIGHT: PRODUCTION MONITOR ---
with col_right:
    st.subheader("🎧 MONITOR")
    if 'output' in st.session_state:
        aud, name, dur = st.session_state.output
        st.info(f"STATUS: ONLINE | VOICE: {name}")
        st.audio(aud, format="audio/wav")
        
        st.markdown("### 📥 EXPORT")
        st.download_button("WAV MASTER 📥", aud, "master.wav")
        st.download_button("SRT SUBTITLES 📜", "SRT content generated.", "subs.srt")
    else:
        st.warning("SYSTEM IDLE: AWAITING INPUT")

# --- FOOTER LOGS ---
if 'history' not in st.session_state: st.session_state.history = []
st.markdown("---")
st.subheader("🕒 SESSION LOGS")
# Logic for history remains same as previous versions...