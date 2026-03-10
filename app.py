import streamlit as st
import subprocess
import whisper
import os
import random
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro

# --- 1. SETTINGS & HELPERS ---
st.set_page_config(page_title="Avinash Sen: Ultra Studio", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

def hex_to_ass(hex_color):
    """Converts #RRGGBB to ASS &HBBGGRR"""
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

emoji_map = {
    "money":"💰",
    "success":"🚀",
    "power":"⚡",
    "brain":"🧠",
    "focus":"🎯",
    "win":"🏆",
    "fail":"💀",
    "life":"🌍",
    "time":"⏳",
    "danger":"⚠️"
}

# --- 2. LOAD AI ENGINES ---
@st.cache_resource
def init_tools():
    m_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="kokoro-v1.0.onnx")
    v_path = hf_hub_download(repo_id="leonelhs/kokoro-thewh1teagle", filename="voices-v1.0.bin")
    return Kokoro(m_path, v_path), whisper.load_model("base")

kokoro, whisper_engine = init_tools()

# --- 3. SIDEBAR: VOICE & CAPTION PRO ---
st.sidebar.title("🧬 Voice DNA & Style")

# Anti-Reuse Settings
st.sidebar.subheader("Algorithm Protection")
dna_jitter = st.sidebar.slider("DNA Randomization (Anti-Reuse)", 0.0, 0.1, 0.02)
speed_jitter = st.sidebar.slider("Speed Variation", 0.8, 1.5, 1.1)

# Caption Styles
st.sidebar.subheader("Caption Visuals")

anim_style = st.sidebar.selectbox(
    "Caption Preset",
    [
        "Dynamic Word",
        "Story Blocks",
        "Bottom Clean",
        "Emoji Pop",
        "Hormozi",
        "MrBeast Pop",
        "Iman Clean"
    ]
)

t_color1 = st.sidebar.color_picker("Caption Color 1", "#D4AF37")
t_color2 = st.sidebar.color_picker("Caption Color 2", "#FF4C4C")
t_color3 = st.sidebar.color_picker("Caption Color 3", "#4CFFB5")

t_size = st.sidebar.slider("Font Size", 20, 100, 55)

# --- 4. MAIN INTERFACE ---
st.title("🎬 Avinash Sen Ultra Studio")

tab_creator, tab_history = st.tabs(["🚀 Viral Engine", "📜 Work Log"])

with tab_creator:

    col1, col2 = st.columns([1, 1])

    with col1:

        st.subheader("1. Script & Fusion")

        txt = st.text_area(
            "What's the story?",
            "They told me I couldn't do it. So I did it twice."
        )

        voices = [
            "af_heart","af_bella","af_nicole","af_sky",
            "am_adam","am_michael",
            "bf_emma","bm_george","bm_lewis"
        ]

        v1 = st.selectbox("Primary Voice", voices)

        use_fusion = st.checkbox("Enable Fusion (Unique Blend)")
        v2 = st.selectbox("Partner Voice", voices, index=1) if use_fusion else v1

        mix = st.sidebar.slider("Fusion Mix %", 0, 100, 50) / 100

        if st.button("🔥 Generate Unique Audio"):

            with st.spinner("Blending Neural DNA..."):

                s1 = kokoro.get_voice_style(v1)
                s2 = kokoro.get_voice_style(v2)

                blended = (s1 * (1 - mix)) + (s2 * mix)

                noise = np.random.uniform(-dna_jitter, dna_jitter, blended.shape).astype(np.float32)

                unique_voice = blended + noise

                samples, sr = kokoro.create(txt, voice=unique_voice, speed=speed_jitter)

                sf.write("unique_audio.wav", samples, sr)
    with st.spinner("Creating Word-Level Animation..."):

          result = whisper_engine.transcribe("unique_audio.wav", word_timestamps=True)

    colors = [t_color1, t_color2, t_color3]

    ass_header = f"""
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV
Style: Default,Arial,{t_size},&H00FFFFFF,&H00000000,1,3,2,40

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_lines = []
    word_counter = 0

    for seg in result['segments']:

        for word in seg['words']:

            s = word['start']
            e = word['end']

            t_in = f"{int(s//3600)}:{int((s%3600)//60):02}:{s%60:05.2f}"
            t_out = f"{int(e//3600)}:{int((e%3600)//60):02}:{e%60:05.2f}"

            clean_word = word['word'].strip().upper()

            color = hex_to_ass(colors[word_counter % 3])

            emoji = ""
            if clean_word.lower() in emoji_map:
                emoji = " " + emoji_map[clean_word.lower()]

            # Dynamic Word (Left / Right)
            if anim_style == "Dynamic Word":

                pos = "\\pos(250,950)" if word_counter % 2 == 0 else "\\pos(830,950)"

                text = f"{{\\c{color}}}{clean_word}{emoji}"

            # Story Blocks (same but slightly higher)
            elif anim_style == "Story Blocks":

                pos = "\\pos(250,850)" if word_counter % 2 == 0 else "\\pos(830,850)"

                text = f"{{\\c{color}}}{clean_word}{emoji}"

            # Bottom Clean
            elif anim_style == "Bottom Clean":

                pos = "\\pos(540,1700)"
                text = f"{clean_word}"

            # Emoji Pop
            elif anim_style == "Emoji Pop":

                pos = "\\pos(540,960)"
                text = f"{{\\fscx130\\fscy130}}{clean_word}{emoji}"

            # Hormozi Style
            elif anim_style == "Hormozi":

                pos = "\\pos(540,960)"

                if len(clean_word) > 5:
                    text = f"{{\\c&H0000FF00\\b1}}{clean_word}"
                else:
                    text = clean_word

            # MrBeast Pop
            elif anim_style == "MrBeast Pop":

                pos = "\\pos(540,960)"
                text = f"{{\\fscx160\\fscy160\\t(0,120,\\fscx100,\\fscy100)}}{clean_word}"

            # Iman Clean
            elif anim_style == "Iman Clean":

                pos = "\\pos(540,1650)"
                text = clean_word

            ass_lines.append(
                f"Dialogue: 0,{t_in},{t_out},Default,,0,0,0,,{{{pos}}}{text}"
            )

            word_counter += 1

    # save ASS subtitle file
with open("typo.ass", "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(ass_lines))

# update Streamlit UI after file is written
st.session_state.history.append(f"Voice: {v1}+{v2} | Text: {txt[:40]}...")

st.audio("unique_audio.wav")

st.success("DNA Generated. Ready to Render.")

with col2:

        st.subheader("2. Final Rendering")

        video_file = st.file_uploader("Upload Video Background", type=["mp4"])

        if video_file and st.button("🎥 Render for YouTube/Reels"):

            with st.spinner("Hardcoding DNA & Animations..."):

                with open("bg.mp4", "wb") as f:
                    f.write(video_file.getbuffer())

                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i","bg.mp4",
                    "-i","unique_audio.wav",
                    "-vf","ass=typo.ass",
                    "-c:v","libx264",
                    "-c:a","aac",
                    "-map","0:v:0",
                    "-map","1:a:0",
                    "-shortest",
                    "viral.mp4"
                ]

                subprocess.run(cmd)

                st.video("viral.mp4")

                with open("viral.mp4", "rb") as f:

                    st.download_button(
                        "📥 Download Viral Video",
                        f,
                        "viral_video.mp4"
                    )

with tab_history:

    st.subheader("Session Downloads")

    full_log = "\n".join(st.session_state.history)

    st.text_area("History Summary", full_log, height=200)

    st.download_button(
        "💾 Download History .txt",
        full_log,
        "studio_history.txt"
    )