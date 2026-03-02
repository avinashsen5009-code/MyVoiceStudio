import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import time
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="Avinash Sen Voice Studio", page_icon="🌸", layout="wide")

# ✨ ANIME THEME CSS ✨
st.markdown("""
    <style>
    /* Anime Pastel Background */
    .main { 
        background: linear-gradient(135deg, #fce4ec 0%, #e1f5fe 100%); 
        color: #4a148c; 
    }
    
    /* Sidebar: Soft Blue */
    div[data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.6) !important; 
        backdrop-filter: blur(15px);
        border-right: 3px solid #f06292; 
    }
    
    /* Text Area: Kawaii Style */
    .stTextArea textarea { 
        background-color: rgba(255, 255, 255, 0.8) !important; 
        color: #1a237e !important; 
        border: 2px solid #ce93d8 !important; 
        border-radius: 15px !important;
    }
    
    /* Buttons: Vibrant Pink to Purple */
    .stButton>button {
        width: 100%; 
        background: linear-gradient(90deg, #f06292, #ba68c8);
        color: white; 
        font-weight: bold; 
        border-radius: 20px; 
        border: none;
        box-shadow: 0 4px 10px rgba(240, 98, 146, 0.3);
        height: 50px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(240, 98, 146, 0.5);
    }
    
    /* History Cards */
    .history-card { 
        background: rgba(255, 255, 255, 0.7); 
        border-left: 8px solid #f06292; 
        padding: 15px; 
        margin: 10px 0; 
        border-radius: 12px;
        color: #4a148c;
    }
    
    h1, h2, h3 { font-family: 'Comic Sans MS', cursive, sans-serif; color: #ad1457; }
    </style>
    """, unsafe_allow_html=True)

# --- STABLE ENGINE LOADER ---
@st.cache_resource(show_spinner=False)
def load_kokoro(version_tag):
    REPO_ID = "leonelhs/kokoro-thewh1teagle"
    try:
        model_path = hf_hub_download(repo_id=REPO_ID, filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id=REPO_ID, filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Oh no! The engine is shy: {e}")
        return None

# --- SIDEBAR: ANIME CONTROLS ---
with st.sidebar:
    st.title("🌸 STUDIO SETTINGS")
    if st.button("✨ Reset Magic Engine"):
        st.cache_resource.clear()
        st.rerun()
    
    st.markdown("---")
    st.header("🎭 Choose Persona")
    
    VOICES = {
        "af_bella": "🎙️ Bella (Professional)",
        "af_sarah": "✨ Sarah (Friendly)",
        "af_nicole": "📖 Nicole (Soft Narrator)",
        "af_sky": "🎭 Sky (High Energy/Anime)",
        "am_adam": "🎬 Adam (Movie Trailer)",
        "am_onyx": "🌑 Onyx (Deep/Cool)",
        "am_michael": "👨‍🏫 Michael (Professor)",
        "am_puck": "⚡ Puck (Hyper/Excited)"
    }
    
    mode = st.radio("Voice Mode", ["Single Character", "Fusion Mix"], index=0)
    
    if mode == "Single Character":
        v_choice = st.selectbox("Active Character", list(VOICES.keys()), format_func=lambda x: VOICES[x])
    else:
        v1 = st.selectbox("Base Soul", list(VOICES.keys()), index=0)
        v2 = st.selectbox("Fusion Soul", list(VOICES.keys()), index=3) # Default Sky for anime feel
        mix_ratio = st.slider("Fusion Balance", 0.0, 1.0, 0.5)

    speed = st.slider("Speech Flow", 0.5, 2.0, 1.0)
    st.caption("Lower = Dramatic. Higher = Fast Paced!")

# Initialize Engine
kokoro = load_kokoro(st.session_state.get('engine_ver', 1.0))

if 'history' not in st.session_state:
    st.session_state.history = []

# --- SRT GENERATOR ---
def generate_srt(text, duration):
    words = text.split()
    if not words: return ""
    avg_word_dur = duration / len(words)
    srt_content = ""
    for i, word in enumerate(words):
        start = i * avg_word_dur
        end = (i + 1) * avg_word_dur
        def fmt(s):
            m, s = divmod(s, 60); h, m = divmod(m, 60)
            return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s-int(s))*1000):03}"
        srt_content += f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{word}\n\n"
    return srt_content

# --- MAIN DASHBOARD ---
st.title("✨ AVINASH SEN VOICE STUDIO")
st.write("Crafting beautiful anime-style voices with high-fidelity AI.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 SCRIPT SCROLL")
    text_input = st.text_area("", placeholder="Enter your dialogue here, senpai...", height=300, label_visibility="collapsed")
    gen_btn = st.button("🌟 GENERATE VOICE")

with col2:
    st.markdown("### 🎧 AUDIO PREVIEW")
    if gen_btn and text_input.strip():
        try:
            with st.spinner("Summoning voice spirits..."):
                ts = int(time.time()) # Unique key to fix the "no change" bug
                
                if mode == "Single Character":
                    samples, sample_rate = kokoro.create(text_input, voice=v_choice, speed=speed, lang="en-us")
                    display_voice = v_choice
                else:
                    s1 = kokoro.get_voice_style(v1)
                    s2 = kokoro.get_voice_style(v2)
                    blended = (s1 * (1 - mix_ratio)) + (s2 * mix_ratio)
                    samples, sample_rate = kokoro.create(text_input, voice=blended, speed=speed, lang="en-us")
                    display_voice = f"Fusion ({v1}/{v2})"

                buf = io.BytesIO()
                sf.write(buf, samples, sample_rate, format='WAV')
                audio_bytes = buf.getvalue()
                duration = len(samples) / sample_rate
                srt_data = generate_srt(text_input, duration)

                # Unique Audio Player to force voice change
                st.audio(audio_bytes, format="audio/wav", key=f"audio_{ts}")
                
                st.success(f"Synthesis Complete! ({duration:.2f}s)")
                
                # Anime Styled Downloads
                d_col1, d_col2 = st.columns(2)
                d_col1.download_button("🎀 Save Audio", audio_bytes, f"avinash_voice_{ts}.wav", "audio/wav")
                d_col2.download_button("📝 Get Subtitles", srt_data, f"subs_{ts}.srt", "text/plain")

                # Session History
                st.session_state.history.insert(0, {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "voice": display_voice,
                    "text": text_input[:50] + "...",
                    "audio": audio_bytes,
                    "key": ts,
                    "srt": srt_data
                })
        except Exception as e:
            st.error(f"Something went wrong: {e}")
    else:
        st.info("Ready for your script! Type something and press the button.")

# --- PRODUCTION LOGS ---
st.markdown("---")
st.subheader("🕒 RECENT CREATIONS")
if st.session_state.history:
    for item in st.session_state.history[:5]:
        with st.container():
            st.markdown(f'<div class="history-card"><b>{item["time"]} | {item["voice"]}</b><br>{item["text"]}</div>', unsafe_allow_html=True)
            h_col1, h_col2 = st.columns([2, 1])
            with h_col1: st.audio(item["audio"], key=f"hist_{item['key']}")
            with h_col2: st.download_button("SRT", item['srt'], f"srt_{item['key']}.srt", key=f"dl_{item['key']}")
else:
    st.caption("Your production logs will appear here.")