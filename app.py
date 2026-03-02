import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="Avinash Sen Voice Studio", page_icon="💎", layout="wide")

# --- THEME ENGINE (Cyber 3D Gold & Gojo Integration) ---
def apply_premium_theme():
    # Primary Colors: Deep Space Blue, White, Luminous Gold
    primary = "#1e40af" # Deep Blue
    gold = "#facc15" # Luminous Gold
    bg = "#0f172a" # Deep Space BG
    card = "#1e293b" # Semi-Transparent Panel BG
    text = "#f8fafc" # Clean White

    st.markdown(f"""
    <style>
    /* Dark Deep Space Background */
    .main {{ 
        background-color: {bg}; 
        color: {text}; 
        font-family: 'Inter', sans-serif;
        background-image: radial-gradient(circle at 10% 20%, rgba(30, 64, 175, 0.1) 0%, rgba(15, 23, 42, 1) 90%);
    }}
    
    /* 3D Glassmorphism Panels (Studio Control, Monitor) */
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {{
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        padding: 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
    }}

    /* Luminous Gold "Generate" Button (3D Effect) */
    .stButton>button {{
        width: 100%; 
        background: linear-gradient(135deg, #f59e0b 0%, {gold} 100%);
        color: #0f172a !important; 
        font-weight: 800; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        border-radius: 12px; 
        border: none; 
        height: 55px;
        box-shadow: 0 0 15px rgba(250, 204, 21, 0.4);
        transition: 0.2s ease-in-out;
    }}
    .stButton>button:hover {{
        box-shadow: 0 0 25px rgba(250, 204, 21, 0.6);
        transform: scale(1.02);
    }}
    .stButton>button:active {{ 
        transform: translateY(3px) scale(0.98); 
    }}
    
    /* Input Areas & Selectboxes (Cyber style) */
    .stTextArea textarea {{ 
        background-color: {card} !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        color: {gold} !important; 
        border-radius: 12px !important;
        font-family: 'Courier New', monospace;
    }}
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {card} !important;
        color: {text} !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Global Text Styling */
    h1, h2, h3, .stCaption {{ color: {text}; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }}
    
    /* Gojo Character Overlay */
    #gojo-monitor {{
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 300px;
        opacity: 0.8;
        z-index: 1000;
        pointer-events: none;
    }}
    </style>
    
    <div id="gojo-monitor">
        <img src="https://raw.githubusercontent.com/leonelhs/kokoro-thewh1teagle/main/media/gojo_monitor_v1.png" alt="Gojo Monitor">
    </div>
    """, unsafe_allow_html=True)

# Apply Theme immediately
apply_premium_theme()

# --- ENGINE LOADER (Stable) ---
@st.cache_resource(show_spinner=False)
def load_kokoro():
    try:
        model_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Engine connection failure: {e}")
        return None

# Initialize History
if 'history' not in st.session_state: st.session_state.history = []

def get_srt(text, dur):
    words = text.split(); srt = ""
    if not words: return ""
    step = dur / len(words)
    for i, w in enumerate(words):
        s, e = i * step, (i+1) * step
        f = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},{int((x-int(x))*1000):03}"
        srt += f"{i+1}\n{f(s)} --> {f(e)}\n{w}\n\n"
    return srt

# --- SIDEBAR: STUDIO CONTROLS ---
with st.sidebar:
    st.markdown("### 💎 STUDIO CONTROL PANEL")
    
    st.selectbox("ENVIRONMENT THEME", ["Cyber 3D Gold 🧊", "Minimalist Pro 💼", "Anime Kawaii 🌸"])
    
    if st.button("🔄 FORCE REBOOT ENGINE"):
        st.cache_resource.clear()
        st.rerun()
    
    st.markdown("---")
    st.header("🎭 VOICE DIRECTORY")
    
    VOICES = {
        "af_bella": "🎙️ Bella (Professional)", "af_sarah": "✨ Sarah (Soft)", "af_heart": "💖 Heart (Warm)", 
        "af_sky": "🎭 Sky (Energetic)", "am_adam": "🎬 Adam (Movie)", "am_onyx": "🌑 Onyx (Deep)", 
        "am_michael": "👨‍🏫 Michael (Professor)", "am_fenrir": "🐺 Fenrir (Gravelly)"
    }
    
    mode = st.radio("PROCESSING MODE", ["Solo Persona", "Vocal Fusion (Mix)"])
    if mode == "Solo Persona":
        v_choice = st.selectbox("ACTIVE CHARACTER", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    else:
        v1 = st.selectbox("Base Soul", list(VOICES.keys()), index=0)
        v2 = st.selectbox("Target Soul", list(VOICES.keys()), index=3)
        ratio = st.slider("Mix Balance", 0.0, 1.0, 0.5)

    speed = st.slider("SPEECH TEMPO", 0.5, 2.0, 1.0)

# Load engine
kokoro = load_kokoro()

# --- MAIN STUDIO ---
st.title("💎 AVINASH SEN VOICE STUDIO")
st.caption("PROFESSIONAL AI VOICE SYNTHESIS v5.1")

l, r = st.columns([1, 1])

with l:
    st.markdown("### 📝 SCRIPT MASTER & GENERATION")
    text_input = st.text_area("Dialogue", placeholder="Enter final dialogue here, Master Avinash. The spirits await...", height=320, label_visibility="collapsed")
    if st.button("⚡ GENERATE MASTER AUDIO"):
        if text_input.strip() and kokoro:
            try:
                with st.spinner("Synthesizing vectors..."):
                    if mode == "Solo Persona":
                        samples, sample_rate = kokoro.create(text_input, voice=v_choice, speed=speed, lang="en-us")
                        v_name = v_choice
                    else:
                        s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(v2)
                        blend = (s1 * (1 - ratio)) + (s2 * ratio)
                        samples, sample_rate = kokoro.create(text_input, voice=blend, speed=speed, lang="en-us")
                        v_name = f"Fusion({v1}/{v2})"

                    buf = io.BytesIO()
                    sf.write(buf, samples, sample_rate, format='WAV')
                    
                    st.session_state.current_audio_data = buf.getvalue()
                    st.session_state.current_srt = get_srt(text_input, len(samples)/sample_rate)
                    st.session_state.current_vname = v_name
                    
                    # History
                    st.session_state.history.insert(0, {"v": v_name, "a": buf.getvalue(), "t": text_input[:30]})
            except Exception as e:
                st.error(f"Critical error: {e}")

with r:
    st.markdown("### 🎧 PRODUCTION MONITOR & OUTPUT")
    if 'current_audio_data' in st.session_state:
        st.audio(st.session_state.current_audio_data, format="audio/wav")
        st.info(f"Identity: {st.session_state.current_vname}")
        
        st.markdown("### 📥 DOWNLOAD CENTER")
        d1, d2 = st.columns(2)
        d1.download_button("WAV MASTER 📥", st.session_state.current_audio_data, "master_export.wav")
        d2.download_button("SRT SUBTITLES 📜", st.session_state.current_srt, "subtitles.srt")
    else:
        st.info("Awaiting input to begin rendering.")

# --- HISTORY ---
st.markdown("---")
st.markdown("### 🕒 SESSION LOGS")
if st.session_state.history:
    for i, item in enumerate(st.session_state.history[:3]):
        with st.expander(f"Rec: {item['v']} | {item['t']}..."):
            st.audio(item['a'], format="audio/wav")