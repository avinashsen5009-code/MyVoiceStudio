import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import numpy as np
import io

st.set_page_config(page_title="Kokoro TTS Studio", page_icon="🎙️")

st.title("🎙️ Kokoro TTS Studio v2.0")
st.write("Professional AI Voice Generation")

@st.cache_resource
def load_kokoro():
    # Attempt 1: Official Hexgrad Repo (Preferred)
    try:
        model_path = hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
    except Exception:
        # Attempt 2: Community Mirror (Fallback)
        try:
            st.info("🔄 Official repo busy, switching to backup server...")
            model_path = hf_hub_download(repo_id="onnx-community/Kokoro-82M-ONNX", filename="onnx/model.onnx")
            voices_path = hf_hub_download(repo_id="onnx-community/Kokoro-82M-ONNX", filename="voices.bin")
            return Kokoro(model_path, voices_path)
        except Exception as e:
            st.error(f"Critical Connection Error: {e}")
            return None

kokoro = load_kokoro()

if kokoro:
    with st.sidebar:
        st.header("Voice Settings")
        voice_list = sorted(list(kokoro.get_voices()))
        selected_voice = st.selectbox("Choose Voice:", voice_list, index=0)
        speed = st.slider("Speech Speed:", 0.5, 2.0, 1.0)
        st.markdown("---")
        st.caption("v2.0 - Stabilized for Python 3.12")

    text = st.text_area("Input Text:", value="The system is now online and ready to generate.", height=200)

    if st.button("Generate Audio", type="primary"):
        if not text.strip():
            st.warning("Please enter text!")
        else:
            try:
                with st.spinner("✨ Synthesizing..."):
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
                        file_name=f"{selected_voice}_voiceover.wav",
                        mime="audio/wav"
                    )
            except Exception as e:
                st.error(f"Generation Error: {e}")