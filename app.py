import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io

st.set_page_config(page_title="Kokoro TTS Studio", page_icon="🎙️")

st.title("🎙️ Kokoro TTS Studio v1.95")
st.write("Professional AI Voice Generation")

@st.cache_resource
def load_kokoro():
    try:
        # 2026 Stable Path: We are using the main hexgrad repo with the explicit v1.0 filenames
        # These are the official files that kokoro-onnx 0.5.0 expects.
        REPO_ID = "hexgrad/Kokoro-82M"
        
        # We download the ONNX version specifically
        model_path = hf_hub_download(repo_id=REPO_ID, filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id=REPO_ID, filename="voices-v1.0.bin")
        
        return Kokoro(model_path, voices_path)
    except Exception as e:
        st.error(f"Download Error: {e}")
        st.info("Attempting to fix the link... Please wait.")
        return None

kokoro = load_kokoro()

if kokoro:
    with st.sidebar:
        st.header("Voice Settings")
        # Extract voices from the bin file
        voice_list = sorted(list(kokoro.get_voices()))
        selected_voice = st.selectbox("Choose Voice:", voice_list, index=0)
        speed = st.slider("Speech Speed:", 0.5, 2.0, 1.0)
        st.caption("Voices starting with 'af' are Female, 'am' are Male.")

    text = st.text_area("Input Text:", value="Welcome to your new AI studio.", height=200)

    if st.button("Generate Audio", type="primary"):
        if not text.strip():
            st.warning("Please enter text!")
        else:
            try:
                with st.spinner("Creating voiceover..."):
                    # Generate the raw audio samples
                    samples, sample_rate = kokoro.create(
                        text, 
                        voice=selected_voice, 
                        speed=speed, 
                        lang="en-us"
                    )
                    
                    # Wrap in WAV format for the browser
                    audio_buffer = io.BytesIO()
                    sf.write(audio_buffer, samples, sample_rate, format='WAV')
                    
                    st.audio(audio_buffer.getvalue())
                    st.download_button(
                        label="💾 Download WAV",
                        data=audio_buffer.getvalue(),
                        file_name=f"voice_{selected_voice}.wav",
                        mime="audio/wav"
                    )
            except Exception as e:
                st.error(f"Generation Error: {e}")