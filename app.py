import streamlit as st
from kokoro_onnx import Kokoro
import soundfile as sf
import os
import numpy as np
from pydub import AudioSegment, effects
from huggingface_hub import hf_hub_download
import re
import gc

# 1. Force Streamlit to clear its memory on every refresh
st.cache_resource.clear()
gc.collect()

# 2. Page Configuration
st.set_page_config(page_title="Pro YT Voice Studio", layout="wide")
st.title("🎙️ Pro YouTube Voice Studio (v1.3 Final)")

@st.cache_resource
def load_tts():
    # Downloads the official 2026 optimized model
    model_path = hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-v1.0-ONNX", 
        filename="onnx/model.onnx"
    )
    return Kokoro(model_path, "voices-v1.0.bin")

def apply_studio_mastering(audio_path, bass_gain=6):
    """Professional Audio Mastering for High-Quality YouTube Audio"""
    audio = AudioSegment.from_wav(audio_path)
    audio = effects.normalize(audio)
    
    if bass_gain > 0:
        # Precision Bass: Targets 'chest' frequencies for that deep radio sound
        bass = audio.low_pass_filter(250).apply_gain(bass_gain)
        audio = audio.overlay(bass)
    
    # Final limiter to prevent distortion on mobile speakers
    audio = effects.normalize(audio, headroom=0.1)
    audio.export(audio_path, format="wav")

try:
    tts = load_tts()
    all_voices = sorted(tts.get_voices())

    # --- SIDEBAR: CONTROLS ---
    st.sidebar.header("🎛️ Voice Engineering")
    main_voice = st.sidebar.selectbox("Base Voice", all_voices, 
                                     index=all_voices.index("hm_omega") if "hm_omega" in all_voices else 0)
    
    enable_blend = st.sidebar.checkbox("AI Voice Blending")
    ratio = 0.5
    if enable_blend:
        blend_voice = st.sidebar.selectbox("Secondary Voice", all_voices, index=1)
        ratio = st.sidebar.slider("Mix Ratio", 0.0, 1.0, 0.5)

    st.sidebar.markdown("---")
    speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0, step=0.1)
    bass_boost = st.sidebar.slider("Studio Bass (dB)", 0, 15, 6)
    
    # --- MAIN INTERFACE ---
    text = st.text_area("YouTube Script:", height=300, placeholder="Paste Hindi or English script here...")

    if st.button("🚀 Generate Ultra-HD Voiceover"):
        if not text.strip():
            st.warning("Please enter your script.")
        else:
            with st.spinner("🎙️ AI is processing... (Tensor Verified)"):
                # A. TEXT SPLITTING: Prevents memory crashes
                chunks = re.split(r'([।\.!\?\n])', text)
                full_audio = []
                
                # B. THE ULTIMATE TENSOR FIX: 
                # We convert every single component to float32 separately
                v_base = tts.get_voice_style(main_voice).astype(np.float32)
                
                if enable_blend:
                    v_mix = tts.get_voice_style(blend_voice).astype(np.float32)
                    # Force math to stay in float32
                    style = (v_base * (1.0 - float(ratio)) + v_mix * float(ratio)).astype(np.float32)
                else:
                    style = v_base.astype(np.float32)

                # C. GENERATION LOOP
                for i in range(0, len(chunks)-1, 2):
                    segment = chunks[i] + (chunks[i+1] if i+1 < len(chunks) else "")
                    if segment.strip():
                        # Force speed to float to satisfy ONNX engine
                        samples, sample_rate = tts.create(segment, voice=style, speed=float(speed))
                        full_audio.append(samples)
                
                # Fallback for texts without punctuation
                if not full_audio and text.strip():
                    samples, sample_rate = tts.create(text, voice=style, speed=float(speed))
                    full_audio = [samples]

                if full_audio:
                    final_data = np.concatenate(full_audio)
                    output_name = "final_master.wav"
                    sf.write(output_name, final_data, sample_rate)
                    
                    # Apply final Mastering
                    apply_studio_mastering(output_name, bass_gain=bass_boost)
                    
                    st.audio(output_name)
                    with open(output_name, "rb") as f:
                        st.download_button("📥 Download Final Voiceover", f, file_name="pro_voiceover.wav")
                    st.success("✅ Success: Audio Mastered!")

except Exception as e:
    st.error(f"⚠️ System Alert: {str(e)}")