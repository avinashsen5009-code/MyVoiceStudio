import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io

# Page Setup
st.set_page_config(page_title="Kokoro TTS Studio", page_icon="🎙️")

st.title("🎙️ Kokoro TTS Studio v1.8")
st.write("Professional AI Voice Generation")

# 1. Error-Proof Model Loading
@st.cache_resource
def load_kokoro():
    try:
        # Using the official 2026 stable repository
        model_path = hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Failed to connect to AI Servers: {e}")
        return None

kokoro = load_kokoro()

if kokoro:
    # 2. Sidebar Settings
    with st.sidebar:
        st.header("Voice Settings")
        voice_list = list(kokoro.get_voices())
        selected_voice = st.selectbox("Choose Voice:", voice_list, index=0)
        speed = st.slider("Speech Speed:", 0.5, 2.0, 1.0)
        st.info("Tip: 'af_bella' and 'am_adam' are great for YouTube.")

    # 3. Text Input
    text = st.text_area("Input Text:", placeholder="Enter the script for your video here...", height=200)

    if st.button("Generate Audio", type="primary"):
        if not text.strip():
            st.warning("Please enter some text first!")
        else:
            try:
                with st.spinner("Processing..."):
                    # Generate samples
                    samples, sample_rate = kokoro.create(
                        text, 
                        voice=selected_voice, 
                        speed=speed, 
                        lang="en-us"
                    )
                    
                    # Convert to high-quality WAV buffer
                    audio_buffer = io.BytesIO()
                    sf.write(audio_buffer, samples, sample_rate, format='WAV')
                    
                    # Output
                    st.audio(audio_buffer.getvalue())
                    
                    st.download_button(
                        label="💾 Download Voiceover",
                        data=audio_buffer.getvalue(),
                        file_name=f"kokoro_{selected_voice}.wav",
                        mime="audio/wav"
                    )
            except Exception as e:
                st.error(f"Generation Error: {e}")
                st.info("Try shortening the text if the error persists.")