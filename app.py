import streamlit as st
from kokoro_onnx import Kokoro
import soundfile as sf
import os
import numpy as np
from pydub import AudioSegment, effects
from huggingface_hub import hf_hub_download
import re

# 1. Page Config
st.set_page_config(page_title="Pro YT Voice Studio", layout="wide")
st.title("🎙️ Pro YouTube Voice Studio (v1.4 Final Fix)")

@st.cache_resource
def load_tts_safe():
    """Loads the model and forces it into the correct memory state"""
    model_path = hf_hub_download(
        repo_id="onnx-community/Kokoro-82M-v1.0-ONNX", 
        filename="onnx/model.onnx"
    )
    return Kokoro(model_path, "voices-v1.0.bin")

def master_audio(path, bass=6):
    """Adds the professional YouTube 'Thump' to the voice"""
    audio = AudioSegment.from_wav(path)
    audio = effects.normalize(audio)
    if bass > 0:
        # Deepens the voice for that 'News' or 'Facts' channel feel
        low_end = audio.low_pass_filter(300).apply_gain(bass)
        audio = audio.overlay(low_end)
    audio = effects.normalize(audio, headroom=0.1)
    audio.export(path, format="wav")

try:
    kokoro = load_tts_safe()
    voices = sorted(kokoro.get_voices())

    # --- SIDEBAR ---
    st.sidebar.header("🎛️ Audio Settings")
    main_v = st.sidebar.selectbox("Base Voice", voices, index=voices.index("hm_omega") if "hm_omega" in voices else 0)
    
    do_mix = st.sidebar.checkbox("Mix Two Voices")
    mix_ratio = 0.5
    if do_mix:
        other_v = st.sidebar.selectbox("Mix Voice", voices, index=1)
        mix_ratio = st.sidebar.slider("Mix Balance", 0.0, 1.0, 0.5)

    st.sidebar.markdown("---")
    user_speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0, step=0.1)
    user_bass = st.sidebar.slider("Studio Bass", 0, 15, 8)
    
    # --- MAIN ---
    script = st.text_area("Your Script:", height=250, placeholder="Paste Hindi/English here...")

    if st.button("🚀 Generate Studio Audio"):
        if not script.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("🎙️ AI is rendering..."):
                # A. Prepare the Voice Style - FORCING FLOAT32 HERE
                # This is where the int32 error usually lives
                raw_style = kokoro.get_voice_style(main_v)
                
                if do_mix:
                    raw_style2 = kokoro.get_voice_style(other_v)
                    # Force both to float32 BEFORE math
                    s1 = raw_style.astype(np.float32)
                    s2 = raw_style2.astype(np.float32)
                    final_style = (s1 * (1.0 - float(mix_ratio)) + s2 * float(mix_ratio)).astype(np.float32)
                else:
                    final_style = raw_style.astype(np.float32)

                # B. Split Text by Punctuation
                parts = re.split(r'([।\.!\?\n])', script)
                combined = []

                for i in range(0, len(parts)-1, 2):
                    txt = parts[i] + (parts[i+1] if i+1 < len(parts) else "")
                    if txt.strip():
                        # C. Force EVERYTHING in the create call to be Float
                        samples, sr = kokoro.create(
                            txt, 
                            voice=final_style, 
                            speed=float(user_speed)
                        )
                        combined.append(samples)
                
                if not combined:
                    samples, sr = kokoro.create(script, voice=final_style, speed=float(user_speed))
                    combined = [samples]

                # D. Save and Master
                audio_data = np.concatenate(combined)
                sf.write("out.wav", audio_data, sr)
                master_audio("out.wav", bass=user_bass)
                
                st.audio("out.wav")
                with open("out.wav", "rb") as f:
                    st.download_button("📥 Download Voiceover", f, file_name="pro_yt_voice.wav")

except Exception as e:
    # If it fails, we show the exact mathematical type it received
    st.error(f"System Error: {str(e)}")