import streamlit as st
from kokoro_onnx import Kokoro
import soundfile as sf
import os
import numpy as np
from pydub import AudioSegment, effects
from huggingface_hub import hf_hub_download
import re

# 1. Setup Page
st.set_page_config(page_title="Pro YT Voice Studio", layout="wide")
st.title("🎙️ Pro YouTube Voice Studio (v1.2 Stable)")

@st.cache_resource
def load_tts():
    # Downloads the high-speed optimized model for 2026
    model_path = hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-v1.0-ONNX", 
        filename="onnx/model.onnx"
    )
    # Ensure voices-v1.0.bin is in your GitHub folder
    return Kokoro(model_path, "voices-v1.0.bin")

def apply_studio_mastering(audio_path, bass_gain=6):
    """Professional Audio Mastering: Normalization + Bass Boost"""
    audio = AudioSegment.from_wav(audio_path)
    audio = effects.normalize(audio)
    
    if bass_gain > 0:
        # Boosts warm frequencies (below 250Hz) for that radio/podcast feel
        bass = audio.low_pass_filter(250).apply_gain(bass_gain)
        audio = audio.overlay(bass)
    
    # Final Peak Limiter to prevent mobile speaker distortion
    audio = effects.normalize(audio, headroom=0.1)
    audio.export(audio_path, format="wav")

try:
    tts = load_tts()
    all_voices = sorted(tts.get_voices())

    # --- SIDEBAR: VOICE CONTROLS ---
    st.sidebar.header("🎛️ Voice Engineering")
    main_voice = st.sidebar.selectbox(
        "Base Voice", 
        all_voices, 
        index=all_voices.index("hm_omega") if "hm_omega" in all_voices else 0
    )
    
    enable_blend = st.sidebar.checkbox("AI Voice Blending")
    ratio = 0.5
    if enable_blend:
        blend_voice = st.sidebar.selectbox("Secondary Voice", all_voices, index=1)
        ratio = st.sidebar.slider("Mix Ratio", 0.0, 1.0, 0.5)

    st.sidebar.markdown("---")
    speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0, step=0.1)
    bass_boost = st.sidebar.slider("Studio Bass (dB)", 0, 15, 6)
    
    # --- MAIN INTERFACE ---
    text = st.text_area("YouTube Script:", height=300, placeholder="Paste your Hindi or English script here...")

    if st.button("🚀 Generate Ultra-HD Voiceover"):
        if not text.strip():
            st.warning("Please enter your script.")
        else:
            with st.spinner("🎙️ Mastering Audio..."):
                # A. Split text by punctuation to prevent memory crashes on mobile
                chunks = re.split(r'([।\.!\?\n])', text)
                full_audio = []
                
                # B. THE CRITICAL FIX: Force all voice data to Float32 immediately
                # This prevents the "Unexpected input data type" (int32) error.
                if enable_blend:
                    v1 = tts.get_voice_style(main_voice).astype(np.float32)
                    v2 = tts.get_voice_style(blend_voice).astype(np.float32)
                    # Use float() on ratio to ensure decimal math
                    style = (v1 * (1.0 - float(ratio)) + v2 * float(ratio)).astype(np.float32)
                else:
                    style = tts.get_voice_style(main_voice).astype(np.float32)

                # C. Process each text segment
                for i in range(0, len(chunks)-1, 2):
                    segment = chunks[i] + (chunks[i+1] if i+1 < len(chunks) else "")
                    if segment.strip():
                        # Force speed to float to satisfy the ONNX engine
                        samples, sample_rate = tts.create(segment, voice=style, speed=float(speed))
                        full_audio.append(samples)
                
                # Fallback for short texts without punctuation marks
                if not full_audio and text.strip():
                    samples, sample_rate = tts.create(text, voice=style, speed=float(speed))
                    full_audio = [samples]

                if full_audio:
                    # D. Assemble and Master
                    final_data = np.concatenate(full_audio)
                    output_name = "final_master.wav"
                    sf.write(output_name, final_data, sample_rate)
                    
                    # Apply final Bass and Volume leveling
                    apply_studio_mastering(output_name, bass_gain=bass_boost)
                    
                    # E. Output for Mobile
                    st.audio(output_name)
                    with open(output_name, "rb") as f:
                        st.download_button("📥 Download Final Voiceover", f, file_name="pro_voiceover.wav")
                    st.success("✅ Success: Tensor Verified and Audio Mastered!")

except Exception as e:
    # Captures and displays any remaining errors for easy fixing
    st.error(f"⚠️ System Alert: {str(e)}")