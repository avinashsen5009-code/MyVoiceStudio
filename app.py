import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import re
from datetime import datetime

# --- 1. PERFECTED OBSIDIAN GOLD THEME ---
st.set_page_config(page_title="AVINASH SEN STUDIO", layout="wide", page_icon="💎")

if 'history' not in st.session_state: st.session_state.history = []
if 'last_audio' not in st.session_state: st.session_state.last_audio = None

def apply_perfect_theme(theme):
    if theme == "Obsidian Gold 🏆":
        # Deepest Midnight and True Gold
        bg, acc, card, txt = "#020617", "#EAB308", "rgba(15, 23, 42, 0.98)", "#F8FAFC"
    elif theme == "Cyber Blue 🧊":
        bg, acc, card, txt = "#0F172A", "#38BDF8", "rgba(30, 41, 59, 0.9)", "#F1F5F9"
    else: # Studio White
        bg, acc, card, txt = "#FFFFFF", "#2563EB", "#F1F5F9", "#0F172A"
    
    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: {txt}; }}
    /* Card Styling: Glassmorphism */
    div[data-testid="column"] > div {{
        background: {card} !important; backdrop-filter: blur(30px);
        border-radius: 12px; padding: 25px; border: 1px solid {acc}22;
        box-shadow: 0 15px 60px rgba(0,0,0,0.9); margin-bottom: 20px;
    }}
    /* Gold Buttons */
    .stButton>button {{
        background: {acc} !important; color: #000 !important;
        font-weight: 800; border-radius: 6px; height: 50px;
        border: none !important; width: 100%; text-transform: uppercase;
        box-shadow: 0 0 15px {acc}33; transition: 0.3s;
    }}
    .stButton>button:hover {{ box-shadow: 0 0 25px {acc}66; transform: translateY(-2px); }}
    /* Text Inputs */
    .stTextArea textarea {{ 
        background: #000 !important; color: {acc} !important; 
        border: 1px solid {acc}44 !important; font-size: 16px;
    }}
    /* Headers */
    h1, h2, h3 {{ color: {acc}; font-weight: 800; letter-spacing: -1px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE & LOGIC ---
@st.cache_resource(show_spinner=False)
def load_engine():
    m = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m, v)

def clean_script(text):
    return " ".join(re.sub(r'\[.*?\]|\(.*?\)', '', text).split())

def make_srt(text, dur):
    words = text.split(); step = dur/len(words) if words else 0
    srt = ""
    for i, w in enumerate(words):
        s, e = i*step, (i+1)*step
        ts = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        srt += f"{i+1}\n{ts(s)} --> {ts(e)}\n{w}\n\n"
    return srt

# --- 3. THE STUDIO ---
l, m, r = st.columns([1, 1.4, 1])

with l:
    st.subheader("⚙️ CONTROL PANEL")
    t_choice = st.selectbox("ACTIVE THEME", ["Obsidian Gold 🏆", "Cyber Blue 🧊", "Studio White 💼"])
    apply_perfect_theme(t_choice)
    
    try:
        st.image("gojo.jpg", use_container_width=True)
    except:
        st.caption("Add gojo.jpg to folder for avatar.")

    st.markdown("---")
    VOICES = {
        "am_onyx": "🌑 Onyx (Deep)", "af_sky": "🎭 Sky (Anime)", 
        "am_adam": "🎬 Adam (Cinema)", "am_fenrir": "🐺 Fenrir (Gravel)",
        "af_bella": "🎙️ Bella (Pro)", "am_michael": "👨‍🏫 Michael (Clear)"
    }
    
    # RESTORED: Mode Selection (Single vs Fusion)
    arch_mode = st.radio("VOICE MODE", ["Solo Voice", "Fusion Mix"])
    
    if arch_mode == "Solo Voice":
        v_primary = st.selectbox("SELECT VOICE", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    else:
        v_primary = st.selectbox("BASE VOICE", list(VOICES.keys()), index=0, format_func=lambda x: VOICES[x])
        v_secondary = st.selectbox("FUSION FLAVOR", list(VOICES.keys()), index=1, format_func=lambda x: VOICES[x])
        fusion_val = st.slider("MIX RATIO", 0.0, 1.0, 0.70)
    
    speed = st.slider("TEMPO", 0.5, 2.0, 1.05)

with m:
    st.subheader("📝 YOUTUBE SCRIPT")
    raw_script = st.text_area("", placeholder="Paste script here...", height=430, label_visibility="collapsed")
    
    if st.button("🚀 RENDER FINAL AUDIO"):
        if raw_script.strip():
            engine = load_engine()
            clean_txt = clean_script(raw_script)
            
            with st.spinner("Processing Void..."):
                try:
                    if arch_mode == "Solo Voice":
                        style = engine.get_voice_style(v_primary)
                    else:
                        s1, s2 = engine.get_voice_style(v_primary), engine.get_voice_style(v_secondary)
                        style = (s1 * fusion_val) + (s2 * (1.0 - fusion_val))
                    
                    style = np.atleast_2d(style)
                    samples, sr = engine.create(clean_txt, voice=style, speed=speed, lang="en-us")
                    
                    buf = io.BytesIO(); sf.write(buf, samples, sr, format='WAV')
                    dur = len(samples)/sr
                    st.session_state.last_audio = {"wav": buf.getvalue(), "srt": make_srt(clean_txt, dur), "dur": dur}
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M"), "text": clean_txt[:20]})
                except Exception as e:
                    st.error(f"Render Error: {e}")

with r:
    st.subheader("🎧 MONITOR")
    if st.session_state.last_audio:
        aud = st.session_state.last_audio
        st.audio(aud['wav'])
        st.download_button("📥 WAV MASTER", aud['wav'], "yt_master.wav")
        st.download_button("📜 SRT SUBS", aud['srt'], "yt_subs.srt")
        st.success(f"DUR: {aud['dur']:.2f}s")
    else:
        st.info("Awaiting Signal...")

    st.subheader("🕒 HISTORY")
    for h in st.session_state.history[-5:]:
        st.caption(f"✅ {h['time']} - {h['text']}...")