import streamlit as st
import subprocess
import whisper
import os
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro
import json

# --- 1. SETTINGS & HISTORY SETUP ---
st.set_page_config(page_title="Elite Production Studio", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. LOAD AI ENGINES ---
@st.cache_resource
def init_tools():
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. VOICE LIBRARY & SUGGESTIONS ---
voice_library = {
    "af_heart": "Soft & Emotional (Best for Anime/Stories)",
    "af_bella": "Clear & Professional (Best for Explainers)",
    "am_adam": "Deep & Serious (Best for Motivation/Sigma)",
    "am_michael": "Energetic & Fast (Best for Tech/Gaming)",
    "bf_emma": "Warm & Friendly (Best for Vlogs)",
    "bm_george": "Gravelly & Cinematic (Best for Trailers)"
}

st.sidebar.title("🎙️ Voice Settings")
st.sidebar.markdown("**Voice Suggestions:**")
for v_id, desc in voice_library.items():
    st.sidebar.caption(f"- **{v_id}**: {desc}")

# --- 4. MAIN INTERFACE ---
st.title("🎬 The Ultimate Studio")

tab_creator, tab_history = st.tabs(["⚡ Creation Dashboard (Audio + SRT + Video)", "📜 Generation History"])

with tab_creator:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Generate Audio & SRT")
        txt = st.text_area("Script", "Domain Expansion: Infinite Void. Welcome to the elite level.")
        
        v1 = st.selectbox("Primary Voice", list(voice_library.keys()))
        use_fusion = st.checkbox("Enable Voice Fusion (Mix 2 Voices)")
        v2 = st.selectbox("Fusion Partner", list(voice_library.keys()), index=1) if use_fusion else None
        blend_ratio = st.slider("Fusion Mix (0 = Primary, 100 = Partner)", 0, 100, 50) if use_fusion else 0
        
        if st.button("Generate Audio & SRT"):
            with st.spinner("Recording Voice..."):
                # Kokoro Voice Fusion Logic
                if use_fusion:
                    voice1_data = kokoro.get_voice(v1)
                    voice2_data = kokoro.get_voice(v2)
                    # Blend the neural embeddings
                    blended_voice = (voice1_data * (1 - (blend_ratio/100))) + (voice2_data * (blend_ratio/100))
                    samples, sr = kokoro.create(txt, voice=blended_voice, speed=1.0)
                else:
                    samples, sr = kokoro.create(txt, voice=v1, speed=1.0)
                
                sf.write("studio_audio.wav", samples, sr)
            
            with st.spinner("Writing SRT File..."):
                result = whisper_engine.transcribe("studio_audio.wav")
                
                # Format into standard SRT
                srt_content = ""
                for i, segment in enumerate(result['segments'], start=1):
                    start = format_timestamp(segment['start'])
                    end = format_timestamp(segment['end'])
                    srt_content += f"{i}\n{start} --> {end}\n{segment['text'].strip()}\n\n"
                
                with open("subtitles.srt", "w") as f:
                    f.write(srt_content)
                
                st.session_state.history.append({"text": txt[:30]+"...", "voice": v1 + (" (Fusion)" if use_fusion else "")})
                
                st.success("✅ Audio and SRT Generated!")
                st.audio("studio_audio.wav")
                st.download_button("📥 Download MP3", open("studio_audio.wav", "rb"), "voiceover.wav")
                st.download_button("📥 Download SRT", open("subtitles.srt", "rb"), "subtitles.srt")

    with col2:
        st.subheader("2. Video Caption Burner")
        st.info("Upload a video to burn the recently generated Audio & SRT directly into it.")
        video_file = st.file_uploader("Upload Background Video", type=["mp4"])
        
        if video_file and st.button("Render Final Video"):
            if not os.path.exists("subtitles.srt") or not os.path.exists("studio_audio.wav"):
                st.error("Please generate the Audio & SRT on the left side first!")
            else:
                with st.spinner("Burning Captions via FFmpeg Engine..."):
                    with open("input_video.mp4", "wb") as f: f.write(video_file.getbuffer())
                    
                    # FFmpeg command to merge video, new audio, and burn SRT
                    # Escaping the SRT path is required for FFmpeg video filters
                    cmd = [
                        "ffmpeg", "-y", 
                        "-i", "input_video.mp4", 
                        "-i", "studio_audio.wav",
                        "-vf", "subtitles=subtitles.srt:force_style='Fontname=Arial,Fontsize=24,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1'",
                        "-c:v", "libx264", 
                        "-c:a", "aac", 
                        "-map", "0:v:0", "-map", "1:a:0", "-shortest", 
                        "final_output.mp4"
                    ]
                    
                    try:
                        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        st.success("🎬 Video Rendered Successfully!")
                        st.video("final_output.mp4")
                        with open("final_output.mp4", "rb") as file:
                            st.download_button("📥 Download Final MP4", file, "viral_video.mp4")
                    except subprocess.CalledProcessError as e:
                        st.error("FFmpeg Error. Ensure FFmpeg is installed correctly.")
                        st.code(e.stderr.decode("utf-8"))

with tab_history:
    st.subheader("Generation Log")
    if not st.session_state.history:
        st.write("No audio generated yet during this session.")
    else:
        for idx, item in enumerate(reversed(st.session_state.history)):
            st.write(f"**{idx+1}.** {item['text']} | *Voice: {item['voice']}*")

# Helper function for SRT timestamps
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{msecs:03d}"