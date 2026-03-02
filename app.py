import streamlit as st
from kokoro_onnx import Kokoro
import soundfile as sf
import numpy as np
from pydub import AudioSegment, effects
from huggingface_hub import hf_hub_download
import re
import os

st.set_page_config(page_title="Pro YT Voice Studio", layout="wide")
st.title("🎙️ Pro YouTube Voice Studio (v1.8 Cloud-Sync)")

@st.cache_resource
def load_full_engine():
    # 1. Download Model
    model_path = hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-v1.0-ONNX", 
        filename="onnx/model.onnx"
    )
    # 2. Download Voices (This ensures you have the correct .bin file)
    voices_path = hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-v1.0-ONNX", 
        filename="voices-v1.0.bin"
    )
    return Kokoro(model_path, voices_path)

def master_audio(path, bass_db=8):
    audio = AudioSegment.from_wav(path)
    audio = effects.normalize(audio)
    if bass_db > 0:
        # Professional Bass-Boost for that "Big YouTuber" voice
        bass = audio.low_pass_filter(250).apply_gain(bass_db)
        audio = audio.overlay(bass)
    audio = effects.normalize(audio, headroom=0.1)
    audio.export(path, format="wav")

try:
    # Initialize from Cloud
    tts = load_full_engine()
    voice_list = sorted(tts.get_voices())

    st.sidebar.header("🎛️ Studio Controls")
    sel_voice = st.sidebar.selectbox("Voice", voice_list, index=0)
    val_speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0, step=0.1)
    val_bass = st.sidebar.slider("Studio Bass", 0, 15, 8)
    
    user_text = st.text_area("Script:", height=250, placeholder="Paste your script here...")

    if st.button("🚀 Generate Studio Audio"):
        if user_text.strip():
            with st.spinner("🎙️ Rendering Pro Audio..."):
                # FORCE FLOAT32: This prevents the 'int32' error from coming back
                raw_style = tts.get_voice_style(sel_voice)
                safe_style = np.array(raw_style, dtype=np.float32)

                segments = re.split(r'([।\.!\?\n])', user_text)
                audio_chunks = []

                for part in segments:
                    if part.strip():
                        # We pass the float32 array directly to the engine
                        samples, sr = tts.create(
                            part, 
                            voice=safe_style, 
                            speed=float(val_speed)
                        )
                        audio_chunks.append(samples)
                
                if audio_chunks:
                    final_data = np.concatenate(audio_chunks)
                    sf.write("out.wav", final_data, sr)
                    master_audio("out.wav", val_bass)
                    
                    st.audio("out.wav")
                    with open("out.wav", "rb") as f:
                        st.download_button("📥 Download Voiceover", f, file_name="yt_master.wav")
                    st.success("✅ Mastered Successfully!")
        else:
            st.warning("Please enter text.")

except Exception as e:
    st.error(f"⚠️ System Error: {str(e)}")
    st.info("Tip: If the app hangs, click 'Manage App' -> 'Reboot' to refresh the engine.")