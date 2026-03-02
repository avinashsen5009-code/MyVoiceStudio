import streamlit as st
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download
import soundfile as sf
import os
import io

st.set_page_config(page_title="Kokoro TTS Studio", page_icon="🎙️")

st.title("🎙️ Kokoro TTS Studio v2.1")
st.write("Professional AI Voice Generation")

@st.cache_resource
def load_kokoro():
    # Primary Repo (Proven stable for 2026 Streamlit/Spaces)
    REPO_ID = "leonelhs/kokoro-thewh1teagle"
    
    try:
        # Download verified files
        model_path = hf_hub_download(repo_id=REPO_ID, filename="kokoro-v1.0.onnx")
        voices_path = hf_hub_download(repo_id=REPO_ID, filename="voices-v1.0.bin")
        return Kokoro(model_path, voices_path)
        
    except Exception as e:
        st.error(f"Hugging Face Hub Error: {e}")
        st.info("🔄 Hub is unstable. Switching to Direct GitHub Download...")
        
        # FAIL-SAFE: Direct Download from GitHub Releases
        import urllib.request
        
        MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
        VOICE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
        
        try:
            # Download to local cache if they don't exist
            if not os.path.exists("kokoro-v1.0.onnx"):
                urllib.request.urlretrieve(MODEL_URL, "kokoro-v1.0.onnx")
            if not os.path.exists("voices-v1.0.bin"):
                urllib.request.urlretrieve(VOICE_URL, "voices-v1.0.bin")
            
            return Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
        except Exception as github_e:
            st.error(f"Critical System Failure: {github_e}")
            return None

kokoro = load_kokoro()

if kokoro:
    with st.sidebar:
        st.header("Voice Settings")
        voice_list = sorted(list(kokoro.get_voices()))
        selected_voice = st.selectbox("Choose Voice:", voice_list, index=0)
        speed = st.slider("Speech Speed:", 0.5, 2.0, 1.0)
        st.markdown("---")
        st.caption("v2.1 - Enhanced Reliability")

    text = st.text_area("Input Text:", value="The system is fully operational.", height=200)

    if st.button("Generate Audio", type="primary"):
        if not text.strip():
            st.warning("Please enter text!")
        else:
            try:
                with st.spinner("✨ Creating high-fidelity audio..."):
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
                        file_name=f"{selected_voice}_studio.wav",
                        mime="audio/wav"
                    )
            except Exception as e:
                st.error(f"Generation Error: {e}")
else:
    st.warning("⚠️ Model failed to load. Please check your internet connection and refresh.")