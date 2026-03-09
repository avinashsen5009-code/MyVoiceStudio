import streamlit as st
import numpy as np
import soundfile as sf
import gc
from kokoro import KPipeline
from pydub import AudioSegment

st.set_page_config(page_title="Neural Voice Studio", layout="centered")

# --- 1. OPTIMIZED ENGINE (Only loads once) ---
@st.cache_resource
def get_neural_pipe():
    return KPipeline(lang_code='a')

pipe = get_neural_pipe()

# --- 2. THE VOICE FUSION ENGINE ---
def generate_fused_voice(text, v1, v2, blend):
    # Generate two voices
    gen1 = pipe(text, voice=v1, speed=1.0)
    gen2 = pipe(text, voice=v2, speed=1.0)
    
    # Convert to array
    a1 = np.concatenate([audio for _, _, audio in gen1])
    a2 = np.concatenate([audio for _, _, audio in gen2])
    
    # Broadcast/Length fix
    min_len = min(len(a1), len(a2))
    mixed = (a1[:min_len] * (1-blend)) + (a2[:min_len] * blend)
    
    sf.write('output.wav', mixed, 24000)
    return 'output.wav'

# --- 3. UI ---
st.title("🎙️ Neural Voice Studio")
script = st.text_area("Your Script:", "Success is built on consistency.")
v1 = st.selectbox("Voice 1", ["af_bella", "af_nicole", "am_michael"])
v2 = st.selectbox("Voice 2", ["bf_emma", "am_adam", "af_sky"])
blend = st.slider("Voice Fusion Blend", 0.0, 1.0, 0.5)

if st.button("🚀 Generate Voice"):
    with st.spinner("Synthesizing..."):
        file_path = generate_fused_voice(script, v1, v2, blend)
        st.audio(file_path)
        with open(file_path, "rb") as f:
            st.download_button("📥 Download Voice", f, "fused_voice.wav")
    gc.collect()