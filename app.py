import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io

st.set_page_config(page_title="Kokoro TTS Studio", page_icon="🎙️")

st.title("🎙️ Kokoro TTS Studio v1.8")
st.write("Generating high-quality AI voices directly from the cloud.")

# 1. Download Model & Voices from the official Hexgrad repo
@st.cache_resource
def load_kokoro():
    # Using the official repo to avoid 404 Entry Not Found errors
    model_path = hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="kokoro-v1.0.onnx")
    voices_path = hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="voices-v1.0.bin")
    return Kokoro(model_path, voices_path)

try:
    kokoro = load_kokoro()
    
    # 2. User Input
    text = st.text_area("Enter your script:", "Hello! My name is Kokoro. I am a high-quality AI voice.")
    
    # Get available voices
    voice_list = list(kokoro.get_voices())
    selected_voice = st.selectbox("Select a Voice:", voice_list)
    
    speed = st.slider("Speech Speed:", 0.5, 2.0, 1.0)

    if st.button("Generate Speech"):
        with st.spinner("Generating audio..."):
            # Generate the audio samples
            samples, sample_rate = kokoro.create(
                text, 
                voice=selected_voice, 
                speed=speed, 
                lang="en-us"
            )
            
            # Convert to 16-bit PCM for better compatibility
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, samples, sample_rate, format='WAV')
            
            st.audio(audio_buffer.getvalue())
            st.success("Audio Generated!")
            
            st.download_button(
                label="Download Audio (.wav)",
                data=audio_buffer.getvalue(),
                file_name="ai_voiceover.wav",
                mime="audio/wav"
            )

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Tip: If you see a 404 error, the Hugging Face repo might be temporarily down.")