import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io

st.set_page_config(page_title="Kokoro TTS Studio", page_icon="🎙️")

st.title("🎙️ Kokoro TTS Studio v1.9")
st.write("Professional AI Voice Generation")

@st.cache_resource
def load_kokoro():
    try:
        # 2026 Updated Paths: Looking in the 'onnx' subfolder of the community repo
        # This repo is the current standard for Streamlit deployments
        REPO_ID = "onnx-community/Kokoro-82M-v1.0-ONNX"
        
        model_path = hf_hub_download(repo_id=REPO_ID, filename="onnx/model.onnx")
        voices_path = hf_hub_download(repo_id=REPO_ID, filename="voices.bin")
        
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Download Error: {e}")
        st.info("The AI model files were moved. Trying an alternative repo...")
        return None

kokoro = load_kokoro()

if kokoro:
    with st.sidebar:
        st.header("Voice Settings")
        voice_list = list(kokoro.get_voices())
        selected_voice = st.selectbox("Choose Voice:", voice_list, index=0)
        speed = st.slider("Speech Speed:", 0.5, 2.0, 1.0)

    text = st.text_area("Input Text:", placeholder="Type your script here...", height=200)

    if st.button("Generate Audio", type="primary"):
        if not text.strip():
            st.warning("Please enter text!")
        else:
            try:
                with st.spinner("Creating voiceover..."):
                    samples, sample_rate = kokoro.create(
                        text, 
                        voice=selected_voice, 
                        speed=speed, 
                        lang="en-us"
                    )
                    
                    audio_buffer = io.BytesIO()
                    sf.write(audio_buffer, samples, sample_rate, format='WAV')
                    
                    st.audio(audio_buffer.getvalue())
                    st.download_button(
                        label="💾 Download WAV",
                        data=audio_buffer.getvalue(),
                        file_name=f"kokoro_{selected_voice}.wav",
                        mime="audio/wav"
                    )
            except Exception as e:
                st.error(f"Generation Error: {e}")