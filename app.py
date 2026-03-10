import streamlit as st
import subprocess
import whisper
import os
import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro
import re

st.set_page_config(page_title="Avinash Sen Ultra Studio", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

# ---------------------------
# HELPERS
# ---------------------------

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

def clean_word(word):
    word = re.sub(r'[^\w\s]', '', word)
    return word.upper()

def normalize_audio(samples):
    samples = np.array(samples)

    if samples.ndim > 1:
        samples = samples.mean(axis=1)

    samples = samples / np.max(np.abs(samples))

    return samples


emoji_map = {
    "MONEY":"💰",
    "SUCCESS":"🚀",
    "POWER":"⚡",
    "BRAIN":"🧠",
    "FOCUS":"🎯",
    "WIN":"🏆",
    "FAIL":"💀",
    "LIFE":"🌍",
    "TIME":"⏳"
}

highlight_words = [
    "MONEY","SUCCESS","POWER","FOCUS","WIN","FAIL","BRAIN"
]

# ---------------------------
# LOAD MODELS
# ---------------------------

@st.cache_resource
def init_tools():

    model_path = hf_hub_download(
        repo_id="leonelhs/kokoro-thewh1teagle",
        filename="kokoro-v1.0.onnx"
    )

    voice_path = hf_hub_download(
        repo_id="leonelhs/kokoro-thewh1teagle",
        filename="voices-v1.0.bin"
    )

    kokoro = Kokoro(model_path, voice_path)

    whisper_model = whisper.load_model("small")

    return kokoro, whisper_model


kokoro, whisper_engine = init_tools()

# ---------------------------
# SIDEBAR
# ---------------------------

st.sidebar.title("🧬 Voice DNA")

dna_jitter = st.sidebar.slider("DNA Randomization",0.0,0.1,0.02)
speed_jitter = st.sidebar.slider("Speed Variation",0.8,1.5,1.1)

st.sidebar.title("Caption Style")

anim_style = st.sidebar.selectbox(
    "Caption Preset",
    [
        "Dynamic Word",
        "Story Blocks",
        "Bottom Clean",
        "Emoji Pop",
        "Hormozi",
        "MrBeast Pop",
        "Iman Clean",
        "Cinematic Blocks"
    ]
)

t_color1 = st.sidebar.color_picker("Caption Color 1","#D4AF37")
t_color2 = st.sidebar.color_picker("Caption Color 2","#FF4C4C")
t_color3 = st.sidebar.color_picker("Caption Color 3","#4CFFB5")

t_size = st.sidebar.slider("Font Size",20,100,55)

# ---------------------------
# UI
# ---------------------------

st.title("🎬 Avinash Sen Ultra Studio")

tab_creator, tab_history = st.tabs(["🚀 Viral Engine","📜 Work Log"])

with tab_creator:

    col1,col2 = st.columns([1,1])

    with col1:

        txt = st.text_area(
            "What's the story?",
            "They told me I couldn't do it. So I did it twice."
        )

        voices = [
            "af_heart","af_bella","af_nicole","af_sky",
            "am_adam","am_michael",
            "bf_emma","bm_george","bm_lewis"
        ]

        v1 = st.selectbox("Primary Voice",voices)

        use_fusion = st.checkbox("Enable Fusion")

        v2 = st.selectbox("Partner Voice",voices,index=1) if use_fusion else v1

        mix = st.sidebar.slider("Fusion Mix %",0,100,50)/100

        if st.button("🔥 Generate Unique Audio"):

            with st.spinner("Generating voice..."):

                s1 = kokoro.get_voice_style(v1)
                s2 = kokoro.get_voice_style(v2)

                blended = (s1*(1-mix)) + (s2*mix)

                noise = np.random.uniform(
                    -dna_jitter,dna_jitter,blended.shape
                ).astype(np.float32)

                unique_voice = blended + noise

                samples,sr = kokoro.create(
                    txt,
                    voice=unique_voice,
                    speed=speed_jitter
                )

                samples = normalize_audio(samples)

                audio_path="unique_audio.wav"

                sf.write(audio_path,samples,sr,format="WAV",subtype="PCM_16")

                if not os.path.exists(audio_path) or os.path.getsize(audio_path)<1000:
                    st.error("Audio generation failed.")
                    st.stop()

            with st.spinner("Generating captions..."):

                result = whisper_engine.transcribe(
                    audio_path,
                    word_timestamps=True,
                    fp16=False
                )

                words=[]

                for seg in result["segments"]:
                    for w in seg["words"]:
                        words.append(w)

                ass_header=f"""
[Script Info]
ScriptType: v4.00+
PlayResX:1080
PlayResY:1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BorderStyle,Outline,Alignment,MarginV
Style: Default,Arial,{t_size},&H00FFFFFF,&H00000000,1,4,2,40

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

                ass_lines=[]

                colors=[t_color1,t_color2,t_color3]

                i=0

                while i < len(words):

                    if anim_style=="Cinematic Blocks":

                        chunk=words[i:i+3]

                        start=chunk[0]["start"]
                        end=chunk[-1]["end"]+0.2

                        t_in=f"{int(start//3600)}:{int((start%3600)//60):02}:{start%60:05.2f}"
                        t_out=f"{int(end//3600)}:{int((end%3600)//60):02}:{end%60:05.2f}"

                        text_words=[]

                        for w in chunk:

                            cw=clean_word(w["word"])

                            if cw in highlight_words:
                                cw=f"{{\\c&H0000FFFF}}{cw}"

                            text_words.append(cw)

                        text=" ".join(text_words)

                        pos="\\pos(540,960)"

                        ass_lines.append(
                            f"Dialogue:0,{t_in},{t_out},Default,,0,0,0,,{{{pos}}}{text}"
                        )

                        i+=3
                        continue

                    word=words[i]

                    s=word["start"]
                    e=word["end"]+0.15

                    t_in=f"{int(s//3600)}:{int((s%3600)//60):02}:{s%60:05.2f}"
                    t_out=f"{int(e//3600)}:{int((e%3600)//60):02}:{e%60:05.2f}"

                    clean=clean_word(word["word"])

                    color=hex_to_ass(colors[i%3])

                    emoji=""
                    if clean in emoji_map:
                        emoji=" "+emoji_map[clean]

                    if anim_style=="Dynamic Word":
                        pos="\\pos(250,950)" if i%2==0 else "\\pos(830,950)"
                        text=f"{{\\c{color}}}{clean}{emoji}"

                    elif anim_style=="Story Blocks":
                        pos="\\pos(250,850)" if i%2==0 else "\\pos(830,850)"
                        text=f"{{\\c{color}}}{clean}{emoji}"

                    elif anim_style=="Bottom Clean":
                        pos="\\pos(540,1700)"
                        text=clean

                    elif anim_style=="Emoji Pop":
                        pos="\\pos(540,960)"
                        text=f"{{\\fscx130\\fscy130}}{clean}{emoji}"

                    elif anim_style=="Hormozi":
                        pos="\\pos(540,960)"
                        text=f"{{\\b1}}{clean}"

                    elif anim_style=="MrBeast Pop":
                        pos="\\pos(540,960)"
                        text=f"{{\\fscx160\\fscy160\\t(0,120,\\fscx100,\\fscy100)}}{clean}"

                    elif anim_style=="Iman Clean":
                        pos="\\pos(540,1650)"
                        text=clean

                    ass_lines.append(
                        f"Dialogue:0,{t_in},{t_out},Default,,0,0,0,,{{{pos}}}{text}"
                    )

                    i+=1

                with open("typo.ass","w",encoding="utf-8") as f:
                    f.write(ass_header+"\n".join(ass_lines))

            st.audio(audio_path)

            st.session_state.history.append(txt[:50])

            st.success("Audio + captions generated.")

    with col2:

        video_file=st.file_uploader("Upload background video",type=["mp4"])

        if video_file and st.button("🎥 Render Video"):

            with open("bg.mp4","wb") as f:
                f.write(video_file.getbuffer())

            cmd=[
                "ffmpeg",
                "-y",
                "-i","bg.mp4",
                "-i","unique_audio.wav",
                "-vf","ass=typo.ass",
                "-c:v","libx264",
                "-c:a","aac",
                "-shortest",
                "viral.mp4"
            ]

            subprocess.run(cmd)

            st.video("viral.mp4")

            with open("viral.mp4","rb") as f:
                st.download_button("Download Video",f,"viral_video.mp4")

with tab_history:

    full_log="\n".join(st.session_state.history)

    st.text_area("History",full_log,height=200)

    st.download_button("Download Log",full_log,"studio_history.txt")