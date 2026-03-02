import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="Avinash Sen Voice Studio", page_icon="🎙️", layout="wide")

# --- THEME ENGINE (3D & Professional) ---
def apply_theme(theme_name):
    if "Anime" in theme_name:
        primary = "#f06292"; bg = "linear-gradient(135deg, #fce4ec 0%, #e1f5fe 100%)"; card = "rgba(255,255,255,0.8)"; text = "#4a148c"
    elif "Cyber" in theme_name:
        primary = "#00f2fe"; bg = "#0a0f1e"; card = "#161e31"; text = "#00f2fe"
    else: # Minimalist Pro
        primary = "#1e40af"; bg = "#f1f5f9"; card = "#ffffff"; text = "#0f172a"

    st.markdown(f"""
    <style>
    .main {{ background: {bg}; color: {text}; }}
    
    /* 3D Professional Card Effect */
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {{
        background: {card} !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        box-shadow: 8px 8px 16px rgba(0,0,0,0.1), -4px -4px 12px rgba(255,255,255,0.5) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        margin-bottom: 1rem;
    }}

    /* 3D Tactile Button */
    .stButton>button {{
        width: 100%; background: {primary}; color: white;
        border-radius: 10px; border: none; height: 50px;
        font-weight: bold; text-transform: uppercase;
        box-shadow: 0 6px 0 rgba(0,0,0,0.2); transition: 0.1s;
    }}
    .stButton>button:active {{ transform: translateY(3px); box-shadow: 0 2px 0 rgba(0,0,0,0.2); }}
    
    .stTextArea textarea {{ border-radius: 10px !important; border: 1px solid {primary}44 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE LOADER ---
@st.cache_resource(show_spinner=False)
def load_kokoro():
    try:
        model_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Engine connection lost: {e}")
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ STUDIO SETTINGS")
    theme_choice = st.selectbox("Current Environment", ["Minimalist Pro 💼", "Anime Kawaii 🌸", "Cyber 3D 🧊"])
    apply_theme(theme_choice)
    
    st.markdown("---")
    st.header("🎭 VOICE DIRECTORY")
    
    VOICES = {
        "af_bella": "🎙️ Bella (News)", "af_sarah": "✨ Sarah (Soft)", "af_nicole": "📖 Nicole (Narrator)",
        "af_sky": "🎭 Sky (Energetic)", "af_heart": "💖 Heart (Warm)", "af_alloy": "🛡️ Alloy (Neutral)",
        "am_adam": "🎬 Adam (Movie)", "am_onyx": "🌑 Onyx (Deep)", "am_michael": "👨‍🏫 Michael (Professor)",
        "am_puck": "⚡ Puck (Hyper)", "am_fenrir": "🐺 Fenrir (Gravelly)"
    }
    
    mode = st.radio("Processing Mode", ["Solo Persona", "Vocal Fusion (Mix)"])
    if mode == "Solo Persona":
        v_choice = st.selectbox("Active Character", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    else:
        v1 = st.selectbox("Base Soul", list(VOICES.keys()), index=0)
        v2 = st.selectbox("Target Soul", list(VOICES.keys()), index=3)
        ratio = st.slider("Mix Balance", 0.0, 1.0, 0.5)

    speed = st.slider("Speech Tempo", 0.5, 2.0, 1.0)

# --- LOGIC HELPERS ---
kokoro = load_kokoro()
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

# --- MAIN STUDIO ---
st.title("💎 AVINASH SEN VOICE STUDIO")

l, r = st.columns([1, 1])

with l:
    st.subheader("📝 Script Console")
    text_input = st.text_area("Dialogue", placeholder="Enter script...", height=300, label_visibility="collapsed")
    if st.button("🚀 GENERATE MASTER AUDIO"):
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
                    
                    # Update Session State
                    st.session_state.current_audio_data = buf.getvalue()
                    st.session_state.current_srt = get_srt(text_input, len(samples)/sample_rate)
                    st.session_state.current_vname = v_name
                    
                    # History
                    st.session_state.history.insert(0, {"v": v_name, "a": buf.getvalue(), "t": text_input[:30]})
            except Exception as e:
                st.error(f"Error: {e}")

with r:
    st.subheader("🎧 Production Monitor")
    if 'current_audio_data' in st.session_state:
        # Standard audio player without the 'key' argument to prevent the error
        st.audio(st.session_state.current_audio_data, format="audio/wav")
        st.caption(f"Active Identity: {st.session_state.current_vname}")
        
        d1, d2 = st.columns(2)
        d1.download_button("📥 Download WAV", st.session_state.current_audio_data, "voice_export.wav")
        d2.download_button("📜 Get SRT", st.session_state.current_srt, "subtitles.srt")
    else:
        st.info("System Ready. Waiting for script synthesis...")

# --- HISTORY ---
st.markdown("---")
st.subheader("🕒 Session Logs")
if st.session_state.history:
    for i, item in enumerate(st.session_state.history[:3]):
        with st.expander(f"Record {i+1}: {item['v']} | {item['t']}..."):
            st.audio(item['a'], format="audio/wav")