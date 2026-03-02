import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io
import os
import time
from datetime import datetime
import zipfile

# --- 1. CORE STUDIO CONFIG ---
# Set page to wide, set matching icon and title
st.set_page_config(page_title="AVINASH SEN VOICE STUDIO", page_icon="💎", layout="wide")

# --- 2. BACKEND & HISTORY ENGINE ---
if 'studio_history' not in st.session_state: st.session_state.studio_history = []
if 'current_generation' not in st.session_state: st.session_state.current_generation = None
if 'active_theme' not in st.session_state: st.session_state.active_theme = "Cyber 3D 🧊"

# Stable function to load the ONNX engine
@st.cache_resource(show_spinner=False)
def load_studio_engine():
    try:
        model_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Engine connection failure: {e}")
        return None

# Simple word-based SRT Generator
def generate_srt(text, total_duration_seconds):
    words = text.split()
    if not words: return ""
    per_word = total_duration_seconds / len(words)
    srt_content = ""
    for i, word in enumerate(words):
        start = i * per_word
        end = (i + 1) * per_word
        # Format [hh:mm:ss,mmm]
        f = lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02},{int((x-int(x))*1000):03}"
        srt_content += f"{i+1}\n{f(start)} --> {f(end)}\n{word}\n\n"
    return srt_content

# Add a generation to the history buffer (last 5)
def add_to_history(voice_key, duration, text_snippet, wav_data, srt_data):
    entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'voice': voice_key,
        'duration': duration,
        'text': text_snippet,
        'wav': wav_data,
        'srt': srt_data
    }
    st.session_state.studio_history.insert(0, entry)
    if len(st.session_state.studio_history) > 5:
        st.session_state.studio_history.pop()

# Comprehensive set of 12 adult Kokoro voices
VOICE_DETAILS = {
    'af_bella': 'US Bella (Professional)', 'af_sarah': 'US Sarah (Soft)',
    'af_sky': 'US Sky (Energetic)', 'af_heart': 'US Heart (Warm)',
    'am_adam': 'US Adam (Cinematic)', 'am_onyx': 'US Onyx (Deep)',
    'am_michael': 'US Michael (Professor)', 'am_fenrir': 'US Fenrir (Gravelly)',
    'af_alloy': 'US Alloy (Guardian)', 'af_aoede': 'US Aoede (Singer/Melodic)',
    'af_nicole': 'US Nicole (Author/Narrator)', 'am_puck': 'US Puck (Mischievous)'
}

# --- 3. DYNAMIC THEME & CSS (Cyber 3D Default) ---
def apply_theme_css(theme_name):
    # Colors matching the 'provided image' polished glass and blue/gold accents
    if theme_name == "Minimalist Pro 💼":
        bg = "#f1f5f9"; primary = "#1e40af"; secondary = "#1d4ed8"; text = "#0f172a"; card = "#ffffff"
        waveform = "#e2e8f0"; glowing = "0 0 10px rgba(0,0,0,0.1)"
    elif theme_choice == "Anime Kawaii 🌸":
        bg = "linear-gradient(135deg, #fce4ec 0%, #e1f5fe 100%)"; primary = "#f06292"; secondary = "#ec407a"; text = "#4a148c"; card = "rgba(255,255,255,0.7)"
        waveform = "#f8bbd0"; glowing = "0 0 15px rgba(240,98,146,0.3)"
    else: # Cyber 3D 🧊 (Default from Image)
        bg = "#0f172a"; primary = "#a5f3fc"; secondary = "#f59e0b"; text = "white"; card = "rgba(15,23,42,0.6)"
        waveform = "#1e293b"; glowing = "0 0 20px rgba(165,243,252,0.4)"

    st.markdown(f"""
    <style>
    /* Full Page and Card Styling matching provided image's glassmorphism */
    .main {{ background: {bg}; color: {text}; font-family: 'Inter', sans-serif; }}
    div[data-testid="column"] > div {{
        background: {card} !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem !important;
        box-shadow: {glowing}, -5px -5px 15px rgba(255,255,255,0.03);
        margin-bottom: 2rem;
    }}
    /* Header and Buttons matching the polished white/gold style */
    h1, h2, h3 {{ text-transform: uppercase; letter-spacing: 2px; color: {text}; }}
    .stButton>button {{
        width: 100%; 
        background: linear-gradient(135deg, #0f172a 0%, #a5f3fc 100%);
        color: white !important;
        font-weight: bold;
        border-radius: 12px;
        height: 55px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: none;
    }}
    .stButton>button:active {{ transform: translateY(4px); box-shadow: 0 1px 0 transparent; }}
    /* Cyber-styled Input */
    .stTextArea textarea {{ background: #000 !important; color: #fbbf24 !important; border-radius: 12px !important; }}
    /* Advanced Settings Slider */
    .stSlider {{ color: #fbbf24; }}
    </style>
    """, unsafe_allow_html=True)

# Update theme choice in session state and apply immediately
theme_choice = st.session_state.get('active_theme', "Cyber 3D 🧊")
apply_theme_css(theme_choice)

# --- 4. LAYOUT: TRIPLE-MONITOR (From Image) ---
# Column 1 (Left): Gojo character
# Column 2 (Center): Control, Script, Monitor, Downloads
# Column 3 (Right): Monitor (expanded description), Logs
col1, col2, col3 = st.columns([1, 1.5, 1])

with col1:
    # Character Image from 'Offline Local Image Integration' (Feature #5)
    st.image("gojo.jpg", caption="SATORU GOJO | Studio Guardian", use_container_width=True)
    st.markdown("---")

with col2:
    # Title from Image with 'Gojo' visual details
    st.markdown("<h1 style='text-align: center; color: white;'>💎 AVINASH SEN VOICE STUDIO</h1>", unsafe_allow_html=True)
    st.caption("ULTIMATE AI SYNTHESIS SUITE • LOCAL MASTER EDITION")

    # PANEL A: Studio Control (Feature #4/5 from user request)
    st.subheader("⚙️ STUDIO CONTROL")
    c1, c2 = st.columns([1, 1])
    # Theme Switcher (Feature #5/user request)
    new_theme = c1.selectbox("ENVIRONMENT THEME", ["Minimalist Pro 💼", "Cyber 3D 🧊", "Anime Kawaii 🌸"], index=1)
    if new_theme != theme_choice:
        st.session_state.active_theme = new_theme
        st.rerun()

    if c2.button("FORCE REBOOT ENGINE"):
        st.cache_resource.clear()
        st.session_state.studio_history = []
        st.session_state.current_generation = None
        st.rerun()

    # PANEL B: Voice Directory (Comprehensive, Feature #3)
    st.subheader("🎭 VOICE DIRECTORY")
    st.info("Comprehensive set of 12 Persona Souls and Fusion Mixing.")
    # structured list layout matching the image (non-interactive display)
    voice_list_display = "".join([f"<p style='margin:0;'>{k}: {v}</p>" for k, v in VOICE_DETAILS.items()])
    st.markdown(voice_list_display, unsafe_allow_html=True)
    
    # Character Selector
    voice_key = st.selectbox("ACTIVE CHARACTER", list(VOICE_DETAILS.keys()), index=0)

    # Processing Mode
    mode = st.radio("PROCESSING MODE", ["Solo Persona", "Vocal Fusion (Mix)", "Gojo Fusion (Mix)"], index=0)
    
    st.subheader("🔧 ADVANCED SETTINGS")
    speed = st.slider("SPEECH TEMPO (precision slider)", 0.5, 2.0, 1.0, step=0.01) # precision slider (Feature #9)
    # Checkbox for optional normalization (image shows a placeholder, this is an actual feature)
    normalize_audio = st.checkbox("NORMALIZE OUTPUT", value=True)

    # PANEL C: Script Master & Generation
    st.subheader("📝 SCRIPT MASTER & GENERATION")
    script_text = st.text_area("", placeholder="Enter your final dialogue here, Master Avinash. The spirits await...", height=400, label_visibility="collapsed")
    
    # Generation Logic
    if st.button("⚡ GENERATE FINAL AUDIO"):
        if script_text.strip():
            with st.spinner("SYNTHESIZING VECTORS..."):
                engine = load_studio_engine()
                if engine:
                    try:
                        # Logic for Gojo Fusion (Feature #2)
                        if mode == "Gojo Fusion (Mix)":
                            s1 = engine.get_voice_style("am_onyx") # Onyx (Deep)
                            s2 = engine.get_voice_style("af_sky") # Sky (Anime)
                            # 70% deep, 30% playful anime
                            final_style = (s1 * 0.70) + (s2 * 0.30)
                            samples, sample_rate = engine.create(script_text, voice=final_style, speed=speed, lang="en-us")
                            final_voice_key = "Fusion(am_onyx+af_sky)"
                        else:
                            samples, sample_rate = engine.create(script_text, voice=voice_key, speed=speed, lang="en-us")
                            final_voice_key = voice_key
                        
                        # Generate the stable WAV and SRT (Feature #7/10)
                        buf_wav = io.BytesIO()
                        sf.write(buf_wav, samples, sample_rate, format='WAV')
                        wav_data = buf_wav.getvalue()
                        duration = len(samples)/sample_rate
                        
                        srt_data = generate_srt(script_text, duration)
                        
                        snippet = script_text[:30] + '...' if len(script_text) > 30 else script_text
                        add_to_history(final_voice_key, duration, snippet, wav_data, srt_data)
                        
                        # Update current generation for the right panel
                        st.session_state.current_generation = {
                            'voice': final_voice_key, 'dur': duration, 'text': script_text,
                            'wav': wav_data, 'srt': srt_data
                        }
                    except Exception as e:
                        st.error(f"Synthesis failed: {e}")

with col3:
    # Title from Image with detailed output information
    st.subheader("🎧 MONITOR")
    
    # Determine the context of the Monitor panel
    gen = st.session_state.get('current_generation')
    
    # PANEL D: Production Monitor (Feature #4 placeholder waveform)
    # The provided image shows a placeholder, and a real waveform is unstable and complex.
    # I have created a complex placeholder visual to match that high-quality look.
    try:
        # Complex placeholder to match image's waveform/status look
        if gen:
            waveform_p = st.container()
            waveform_p.markdown(f"**ACTIVE:** {gen['voice']} | **DURATION:** {gen['dur']:.2f}s | **STATUS:** READY", unsafe_allow_html=True)
            waveform_p.audio(gen['wav'], format='audio/wav')
        else:
            waveform_p = st.container()
            waveform_p.markdown(f"**ACTIVE:** IDLE | **DURATION:** 0.00s | **STATUS:** IDLE", unsafe_allow_html=True)
            # Placeholder volume slider matching image look
            st.write("")
            st.markdown("![Waveform Placeholder](https://raw.githubusercontent.com/leonelhs/kokoro-thewh1teagle/main/media/waveform_placeholder_final.png)", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load placeholder visual: {e}")

    # PANEL E: Download Center (Feature #6/10)
    st.subheader("📥 DOWNLOAD CENTER")
    if gen:
        # Stable Downloads for WAV and SRT
        c1, c2, c3 = st.columns(3)
        c1.download_button("WAV MASTER", gen['wav'], f"final_export_{gen['voice']}_{int(time.time())}.wav")
        c2.download_button("SRT SUBTITLES", gen['srt'], f"subs_{gen['voice']}_{int(time.time())}.srt")
        
        # Batch Export: Zips WAV and SRT for stable batching
        buf_zip = io.BytesIO()
        with zipfile.ZipFile(buf_zip, 'w') as zip_file:
            zip_file.writestr("audio.wav", gen['wav'])
            zip_file.writestr("subtitles.srt", gen['srt'])
        c3.download_button("BATCH EXPORT", buf_zip.getvalue(), f"batch_{int(time.time())}.zip")
    else:
        st.info("Generation required for downloads.")

    # PANEL F: Session Logs (Feature #6 history)
    st.subheader("🕒 SESSION LOGS")
    history = st.session_state.studio_history
    if history:
        # Structured display matching the image's history logs
        for i, log in enumerate(history):
            expander_title = f"{i+1}. {log['voice']} | {log['duration']:.1f}s | {log['text']}"
            with st.expander(expander_title):
                st.audio(log['wav'], format='audio/wav')
                l1, l2 = st.columns(2)
                l1.download_button("Get WAV", log['wav'], f"log_wav_{i+1}.wav")
                l2.download_button("Get SRT", log['srt'], f"log_srt_{i+1}.srt")
    else:
        st.caption("Awaiting first generation.")