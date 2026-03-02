import streamlit as st
from kokoro_onnx import Kokoro
import soundfile as sf
import os
import numpy as np
from pydub import AudioSegment
from huggingface_hub import hf_hub_download

# Setup
st.set_page_config(page_title="Pro YT Voice Studio", layout="wide")
st.title("🎙️ Pro YouTube Voice Studio (v1.0)")

@st.cache_resource
def load_tts():
    # CLOUD FIX: This downloads the 310MB model directly to the server 
    # instead of uploading it through GitHub.
    model_path = hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="kokoro-v1.0.onnx")
    # We still keep voices-v1.0.bin in your GitHub folder (it's small)
    return Kokoro(model_path, "voices-v1.0.bin")

def apply_bass_boost(audio_path, gain_db=6):
    """Processes the WAV file to add depth and bass"""
    audio = AudioSegment.from_wav(audio_path)
    # Low-pass filter targets the 'chest' frequencies for that radio sound
    bass = audio.low_pass_filter(500).apply_gain(gain_db)
    final_audio = audio.overlay(bass)
    final_audio.export(audio_path, format="wav")

try:
    tts = load_tts()
    all_voices = tts.get_voices()

    # --- SIDEBAR: VOICE CONTROLS ---
    st.sidebar.header("🎛️ Voice Engineering")
    
    # 1. Primary Voice
    main_voice = st.sidebar.selectbox("Base Voice", all_voices, index=0, 
                                     help="The main personality of your voice.")
    
    # 2. Voice Blending
    enable_blend = st.sidebar.checkbox("Enable Voice Blending (Unique Voice)")
    ratio = 0.5
    if enable_blend:
        blend_voice = st.sidebar.selectbox("Secondary Voice to Mix", all_voices, index=1)
        ratio = st.sidebar.slider("Mix Ratio (Left = Base, Right = Mix)", 0.0, 1.0, 0.5)

    # 3. Audio Effects (Bass Boost!)
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔊 Audio Effects")
    speed = st.sidebar.slider("Speaking Speed", 0.5, 2.0, 1.0)
    bass_boost = st.sidebar.slider("Bass Boost (Depth)", 0, 15, 6)
    
    # --- MAIN AREA: RECOMMENDATIONS ---
    col1, col2 = st.columns([2, 1])

    with col2:
        st.info("💡 **2026 Hindi Guide (v1.0)**")
        st.markdown("""
        - **Male (Deep):** `hm_omega` (Use Bass 8)
        - **Male (Smooth):** `hm_psi` (Use Bass 5)
        - **Female (Pro):** `hf_alpha` (Use Bass 2)
        - **Female (Soft):** `hf_beta` (Use Bass 2)
        
        **English Favorites:**
        - `af_heart` (Storytelling)
        - `af_bella` (Energetic Top 10)
        """)

    with col1:
        text = st.text_area("YouTube Script:", height=300, placeholder="Paste your script here...")

        if st.button("🚀 Generate Pro Voiceover"):
            if text:
                with st.spinner("Processing High-Quality Audio..."):
                    # Step 1: Handle Blending Logic
                    if enable_blend:
                        v1 = tts.get_voice_style(main_voice)
                        v2 = tts.get_voice_style(blend_voice)
                        mixed_style = v1 * (1 - ratio) + v2 * ratio
                        samples, sample_rate = tts.create(text, voice=mixed_style, speed=speed)
                    else:
                        samples, sample_rate = tts.create(text, voice=main_voice, speed=speed)
                    
                    # Step 2: Save Temporary File
                    temp_file = "yt_output.wav"
                    sf.write(temp_file, samples, sample_rate)
                    
                    # Step 3: Apply Bass Boost if selected
                    if bass_boost > 0:
                        apply_bass_boost(temp_file, gain_db=bass_boost)
                    
                    # Step 4: Display Results
                    st.audio(temp_file)
                    st.success(f"Voiceover Ready with {bass_boost}dB Bass Boost!")
                    
                    with open(temp_file, "rb") as f:
                        st.download_button("📥 Download Final Voiceover", f, file_name="yt_final_voice.wav")
            else:
                st.warning("Please enter your script.")

except Exception as e:
    st.error(f"Setup Error: {e}")