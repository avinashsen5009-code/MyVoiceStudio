import streamlit as st
from kokoro_onnx import Kokoro
import soundfile as sf
import os
import numpy as np
from pydub import AudioSegment, effects
from huggingface_hub import hf_hub_download
import re

# Page Config
st.set_page_config(page_title="Pro YT Voice Studio", layout="wide")
st.title("🎙️ Pro YouTube Voice Studio (v1.6 Final)")

@st.cache_resource
def load_tts_engine():
    model_path = hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-v1.0-ONNX", 
        filename="onnx/model.onnx"
    )
    # Ensure voices-v1.0.bin is in your main GitHub folder
    return Kokoro(model_path, "voices-v1.0.bin")

def master_audio(path, bass_db=6):
    audio = AudioSegment.from_wav(path)
    audio = effects.normalize(audio)
    if bass_db > 0:
        # High-end mastering: targets the deep chest frequencies
        bass = audio.low_pass_filter(250).apply_gain(bass_db)
        audio = audio.overlay(bass)
    audio = effects.normalize(audio, headroom=0.1)
    audio.export(path, format="wav")

try:
    # Initialize Engine
    tts = load_tts_engine()
    voice_list = sorted(tts.get_voices())

    # Sidebar
    st.sidebar.header("🎛️ Studio Controls")
    selected_voice = st.sidebar.selectbox("Select Voice", voice_list, index=0)
    
    st.sidebar.markdown("---")
    val_speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0, step=0.1)
    val_bass = st.sidebar.slider("Studio Bass", 0, 15, 8)
    
    # Main
    user_text = st.text_area("Your Script:", height=250, placeholder="Enter text here...")

    if st.button("🚀 Generate Audio"):
        if user_text.strip():
            with st.spinner("🎙️ Processing..."):
                # --- THE HARD-CODED FIX ---
                # 1. Get the raw style vector from the .bin file
                # 2. Force it to float32 using np.asarray
                # 3. Use np.ascontiguousarray to ensure ONNX can read the memory
                raw_style = tts.get_voice_style(selected_voice)
                safe_style = np.ascontiguousarray(np.asarray(raw_style, dtype=np.float32))

                # Split text into sentences to avoid memory errors
                segments = re.split(r'([।\.!\?\n])', user_text)
                audio_chunks = []

                for part in segments:
                    if part.strip():
                        # We pass the 'safe_style' vector instead of the voice name
                        samples, sample_rate = tts.create(
                            part, 
                            voice=safe_style, 
                            speed=float(val_speed)
                        )
                        audio_chunks.append(samples)
                
                if audio_chunks:
                    final_samples = np.concatenate(audio_chunks)
                    temp_out = "master_out.wav"
                    sf.write(temp_out, final_samples, sample_rate)
                    
                    # Apply Studio Mastering
                    master_audio(temp_out, bass_db=val_bass)
                    
                    st.audio(temp_out)
                    with open(temp_out, "rb") as f:
                        st.download_button("📥 Download Voiceover", f, file_name="pro_voice.wav")
                    st.success("✅ Voice Generated Successfully!")
        else:
            st.warning("Please type something first.")

except Exception as e:
    st.error(f"❌ System Error: {str(e)}")
    st.info("Check if voices-v1.0.bin is uploaded to your GitHub repository.")