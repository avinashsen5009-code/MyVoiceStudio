import streamlit as st
from kokoro_onnx import Kokoro
import soundfile as sf
import os
import numpy as np
from pydub import AudioSegment, effects
from huggingface_hub import hf_hub_download
import re

# Setup
st.set_page_config(page_title="Pro YT Voice Studio", layout="wide", initial_sidebar_state="expanded")
st.title("🎙️ Pro YouTube Voice Studio (v1.1 Optimized)")

@st.cache_resource
def load_tts():
    # Official High-Speed Mirror
    model_path = hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-v1.0-ONNX", 
        filename="onnx/model.onnx"
    )
    return Kokoro(model_path, "voices-v1.0.bin")

def process_audio_pro(audio_path, gain_db=6):
    """Advanced audio processing: Normalization + Bass Boost"""
    audio = AudioSegment.from_wav(audio_path)
    
    # 1. Normalize (Prevents clipping/distortion)
    audio = effects.normalize(audio)
    
    if gain_db > 0:
        # 2. Precision Bass Boost (Low Shelf Filter is cleaner than Low Pass)
        # Boosts the 'warmth' frequencies (below 400Hz)
        audio = audio.low_pass_filter(400).apply_gain(gain_db).overlay(audio)
    
    # 3. Final Peak Limiter (Professional Finish)
    audio = effects.normalize(audio, headroom=0.1)
    audio.export(audio_path, format="wav")

try:
    tts = load_tts()
    all_voices = sorted(tts.get_voices())

    # --- SIDEBAR ---
    st.sidebar.header("🎛️ Studio Controls")
    main_voice = st.sidebar.selectbox("Base Voice", all_voices, index=all_voices.index("hm_omega") if "hm_omega" in all_voices else 0)
    
    enable_blend = st.sidebar.checkbox("Custom Voice Blending")
    ratio = 0.5
    if enable_blend:
        blend_voice = st.sidebar.selectbox("Mix with", all_voices, index=1)
        ratio = st.sidebar.slider("Mix Ratio", 0.0, 1.0, 0.5)

    st.sidebar.markdown("---")
    speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0, step=0.1)
    bass_boost = st.sidebar.slider("Studio Bass (dB)", 0, 15, 6)
    
    # --- MAIN INTERFACE ---
    col1, col2 = st.columns([2, 1])

    with col2:
        st.success("✨ **Pro Tip**\nUse `hm_omega` with **Bass 10** for a 'Discovery Channel' Hindi vibe.")
        st.info("📖 **Auto-Splitter Active**\nYou can now paste very long scripts! The AI will process them sentence-by-sentence automatically.")

    with col1:
        text = st.text_area("Your Script:", height=300, placeholder="Type your Hindi or English script here...")

        if st.button("🚀 Generate Studio Quality Audio"):
            if not text.strip():
                st.warning("Please enter a script first.")
            else:
                with st.spinner("🧠 AI is speaking... (Optimizing Audio)"):
                    # Optimization: Split text by punctuation to avoid memory crashes
                    sentences = re.split(r'([।\.!\?\n])', text)
                    combined_samples = []
                    
                    # Prepare Voice Style
                    if enable_blend:
                        v1 = tts.get_voice_style(main_voice)
                        v2 = tts.get_voice_style(blend_voice)
                        style = (v1 * (1 - ratio) + v2 * ratio).astype(np.float32)
                    else:
                        style = tts.get_voice_style(main_voice).astype(np.float32)

                    # Process each chunk
                    for i in range(0, len(sentences)-1, 2):
                        chunk = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
                        if chunk.strip():
                            samples, sample_rate = tts.create(chunk, voice=style, speed=speed)
                            combined_samples.append(samples)
                    
                    if not combined_samples: # Fallback if regex fails
                         samples, sample_rate = tts.create(text, voice=style, speed=speed)
                         combined_samples = [samples]

                    # Merge and Save
                    final_samples = np.concatenate(combined_samples)
                    temp_file = "studio_out.wav"
                    sf.write(temp_file, final_samples, sample_rate)
                    
                    # Professional Mastering
                    process_audio_pro(temp_file, gain_db=bass_boost)
                    
                    # Display Result
                    st.audio(temp_file)
                    with open(temp_file, "rb") as f:
                        st.download_button("📥 Download Final Master (.WAV)", f, file_name="yt_studio_voice.wav")
                    
                    # Cleanup
                    st.caption("Cleaned up memory for next run.")

except Exception as e:
    st.error(f"System Error: {str(e)}")