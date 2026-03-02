import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="AVINASH SEN VOICE STUDIO", page_icon="💎", layout="wide")

# --- 2. 3D CYBER-GOLD THEME ---
if 'theme' not in st.session_state:
    st.session_state.theme = "Cyber 3D Gold 🧊"

def apply_theme(theme_choice):
    if theme_choice == "Cyber 3D Gold 🧊":
        bg = "radial-gradient(circle at center, #0f172a 0%, #020617 100%)"
        accent = "#fbbf24"; card = "rgba(30, 41, 59, 0.75)"; text = "#f8fafc"
    elif theme_choice == "Anime Pastel 🌸":
        bg = "linear-gradient(135deg, #fce4ec 0%, #e1f5fe 100%)"
        accent = "#f06292"; card = "rgba(255, 255, 255, 0.8)"; text = "#4a148c"
    else: # Minimalist Pro
        bg = "#f8fafc"; accent = "#1e40af"; card = "#ffffff"; text = "#1e293b"

    st.markdown(f"""
    <style>
    .main {{ background: {bg}; color: {text}; font-family: 'Inter', sans-serif; }}
    div[data-testid="column"] > div {{
        background: {card} !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 2.5rem !important;
        box-shadow: 15px 15px 45px rgba(0,0,0,0.6);
    }}
    h1, h2, h3 {{ color: {accent}; text-transform: uppercase; letter-spacing: 2px; font-weight: 900; }}
    .stButton>button {{
        width: 100%; background: linear-gradient(135deg, {accent} 0%, #f59e0b 100%);
        color: #000 !important; font-weight: 800; border-radius: 12px; height: 60px;
        box-shadow: 0 5px 0 rgba(0,0,0,0.3); border: none; transition: 0.1s;
    }}
    .stButton>button:active {{ transform: translateY(4px); }}
    .stTextArea textarea {{ background: #000 !important; color: {accent} !important; border-radius: 15px !important; border: 1px solid {accent}44 !important; }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# --- 3. STUDIO ENGINE ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

kokoro = load_engine()

# --- 4. LAYOUT ---
st.title("💎 AVINASH SEN VOICE STUDIO")
st.caption("ULTIMATE 3D PRODUCTION • v13.0")

l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("🛡️ GUARDIAN")
    # THE FIX: I converted your link to a Direct Image URL that Streamlit can read
    gojo_img = "https://rukminim2.flixcart.com/image/850/1000/xif0q/poster/v/k/c/medium-satoru-gojo-jujutsu-kaisen-wall-poster-paper-print-original-imaggfayj6qyzg9z.jpeg"
    st.image(gojo_img, caption="SATORU GOJO", use_container_width=True)
    
    st.session_state.theme = st.selectbox("ACTIVE THEME", ["Cyber 3D Gold 🧊", "Anime Pastel 🌸", "Minimalist Pro 💼"])
    
    VOICES = {
        "am_onyx": "🌑 Onyx (Deep)", "af_sky": "🎭 Sky (Energetic)", 
        "af_bella": "🎙️ Bella (News)", "am_adam": "🎬 Adam (Movie)",
        "af_heart": "💖 Heart (Soft)", "am_fenrir": "🐺 Fenrir (Gravelly)",
        "am_michael": "👨‍🏫 Michael (Pro)", "af_sarah": "✨ Sarah (Gentle)"
    }
    
    mode = st.radio("VOICE ARCHITECTURE", ["Solo", "Fusion (Mix)"])
    if mode == "Solo":
        v_id = st.selectbox("IDENTITY", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    else:
        v1 = st.selectbox("Base Soul", list(VOICES.keys()), index=0) # Onyx
        v2 = st.selectbox("Target Soul", list(VOICES.keys()), index=1) # Sky
        mix = st.slider("Mix Ratio", 0.0, 1.0, 0.75)
    
    speed = st.slider("TEMPO", 0.5, 2.0, 1.0)

with m:
    st.subheader("📝 SCRIPT")
    text = st.text_area("", placeholder="Command me, Master Avinash...", height=420, label_visibility="collapsed")
    if st.button("🚀 INITIATE RENDER"):
        if text.strip() and kokoro:
            with st.spinner("SYNETHESIZING..."):
                if mode == "Solo":
                    samples, sr = kokoro.create(text, voice=v_id, speed=speed, lang="en-us")
                else:
                    s1, s2 = kokoro.get_voice_style(v1), kokoro.get_voice_style(v2)
                    blend = (s1 * (1 - mix)) + (s2 * mix)
                    samples, sr = kokoro.create(text, voice=blend, speed=speed, lang="en-us")
                
                buf = io.BytesIO()
                sf.write(buf, samples, sr, format='WAV')
                st.session_state.out = (buf.getvalue(), len(samples)/sr, text)

with r:
    st.subheader("🎧 MONITOR")
    if 'out' in st.session_state:
        aud, dur, original_text = st.session_state.out
        st.audio(aud, format="audio/wav")
        st.success(f"ONLINE | {dur:.2f}s")
        st.download_button("📥 WAV MASTER", aud, "master.wav")
        
        # SRT GENERATION
        srt = f"1\n00:00:00,000 --> 00:00:{int(dur):02},000\n{original_text}"
        st.download_button("📜 SRT SUBS", srt, "subs.srt")
    else:
        st.info("AWAITING SIGNAL...")

    st.markdown("### 📊 BEST MIX")
    st.info("**Gojo:** Onyx (0.7) + Sky (0.3)")