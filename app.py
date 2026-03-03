import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import re
from datetime import datetime

# --- 1. OBSIDIAN GOLD THEME ENGINE ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

if 'history' not in st.session_state: st.session_state.history = []
if 'last_audio' not in st.session_state: st.session_state.last_audio = None

def apply_studio_theme(theme):
    if theme == "Obsidian Gold 🏆":
        bg, acc, card, txt = "#0a0f1e", "#f59e0b", "rgba(15, 23, 42, 0.95)", "#f8fafc"
    elif theme == "Cyber Blue 🧊":
        bg, acc, card, txt = "#0f172a", "#38bdf8", "rgba(30, 41, 59, 0.8)", "#f1f5f9"
    else: # Minimalist White
        bg, acc, card, txt = "#ffffff", "#2563eb", "#f1f5f9", "#0f172a"
    
    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: {txt}; }}
    div[data-testid="column"] > div {{
        background: {card} !important; backdrop-filter: blur(25px);
        border-radius: 15px; padding: 25px; border: 1px solid {acc}44;
        box-shadow: 0 10px 50px rgba(0,0,0,0.8); margin-bottom: 20px;
    }}
    .stButton>button {{
        background: linear-gradient(135deg, {acc}, #b45309) !important;
        color: #000 !important; font-weight: 900; border-radius: 8px;
        height: 55px; border: none !important; width: 100%;
        text-transform: uppercase; letter-spacing: 2px;
    }}
    .stTextArea textarea {{ 
        background: #000 !important; color: {acc} !important; 
        border: 1px solid {acc}66 !important; font-size: 17px;
    }}
    h1, h2, h3 {{ color: {acc}; text-transform: uppercase; font-weight: 900; }}
    /* Custom Slider Color */
    .stSlider > div [data-baseweb="slider"] > div > div {{ background: {acc} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FAIL-SAFE CORE ENGINE ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

def clean_script(text):
    return " ".join(re.sub(r'\[.*?\]|\(.*?\)', '', text).split())

def make_srt(text, dur):
    words = text.split()
    if not words: return ""
    step = dur / len(words)
    srt = ""
    for i, w in enumerate(words):
        s, e = i * step, (i + 1) * step
        ts = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        srt += f"{i+1}\n{ts(s)} --> {ts(e)}\n{w}\n\n"
    return srt

# --- 3. UI LAYOUT ---
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("⚙️ CORE ENGINE")
    t_choice = st.selectbox("THEME", ["Obsidian Gold 🏆", "Cyber Blue 🧊", "Minimalist White 💼"])
    apply_studio_theme(t_choice)
    
    try:
        st.image("gojo.jpg", use_container_width=True)
    except:
        st.info("Place gojo.jpg in folder for avatar display.")

    st.markdown("---")
    VOICES = {
        "am_onyx": "🌑 Onyx (Deep)", "af_sky": "🎭 Sky (Anime)", 
        "am_adam": "🎬 Adam (Cinema)", "am_fenrir": "🐺 Fenrir (Gravel)",
        "af_bella": "🎙️ Bella (Smooth)", "am_michael": "👨‍🏫 Michael (Clear)",
        "af_sarah": "✨ Sarah (Soft)", "af_nicole": "📖 Nicole (Narrator)"
    }
    
    st.write("**QUANTUM FUSION SETUP**")
    v_primary = st.selectbox("PRIMARY SOUL (Base)", list(VOICES.keys()), index=0, format_func=lambda x: VOICES[x])
    v_secondary = st.selectbox("SECONDARY SOUL (Flavor)", list(VOICES.keys()), index=1, format_func=lambda x: VOICES[x])
    
    # THE ADJUSTABLE FUSION SLIDER
    fusion_val = st.slider("FUSION RATIO", 0.0, 1.0, 0.70, help="1.0 = Pure Primary | 0.0 = Pure Secondary")
    st.caption(f"Mix: {int(fusion_val*100)}% {VOICES[v_primary].split()[1]} / {int((1-fusion_val)*100)}% {VOICES[v_secondary].split()[1]}")
    
    speed = st.slider("TEMPO (Speed)", 0.5, 2.0, 1.05)

with m:
    st.subheader("📝 PRODUCTION SCRIPT")
    raw_script = st.text_area("", placeholder="Enter script here...", height=420, label_visibility="collapsed")
    
    if st.button("🚀 RENDER QUANTUM AUDIO"):
        if raw_script.strip():
            engine = load_engine()
            clean_txt = clean_script(raw_script)
            
            with st.spinner("SYNETHESIZING VOID..."):
                try:
                    # FETCH STYLES
                    s1 = engine.get_voice_style(v_primary)
                    s2 = engine.get_voice_style(v_secondary)
                    
                    # PRECISION FUSION MATH
                    style = (s1 * fusion_val) + (s2 * (1.0 - fusion_val))
                    style = np.atleast_2d(style)
                    
                    samples, sr = engine.create(clean_txt, voice=style, speed=speed, lang="en-us")
                    
                    buf = io.BytesIO()
                    sf.write(buf, samples, sr, format='WAV')
                    dur = len(samples) / sr
                    
                    st.session_state.last_audio = {
                        "wav": buf.getvalue(),
                        "srt": make_srt(clean_txt, dur),
                        "dur": dur
                    }
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M"), "text": clean_txt[:20]})
                except Exception as e:
                    st.error(f"Render Failed: {e}")

with r:
    st.subheader("🎧 MASTER MONITOR")
    if st.session_state.last_audio:
        aud = st.session_state.last_audio
        st.audio(aud['wav'])
        st.success(f"ONLINE | {aud['dur']:.2f}s")
        st.download_button("📥 DOWNLOAD WAV", aud['wav'], "master.wav")
        st.download_button("📜 DOWNLOAD SRT", aud['srt'], "subs.srt")
    else:
        st.info("Awaiting Input...")

    st.subheader("🕒 RECENT LOGS")
    for h in st.session_state.history[-5:]:
        st.caption(f"✅ {h['time']} - {h['text']}...")