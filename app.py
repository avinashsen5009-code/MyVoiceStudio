import streamlit as st
import whisper
import os
import random
import subprocess

# --- 1. STUDIO CONFIG ---
st.set_page_config(page_title="Avinash Sen: Caption Master", layout="wide")

def hex_to_ass(hex_color):
    """Converts #RRGGBB to ASS &HBBGGRR"""
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_engine = load_whisper()

# --- 2. SIDEBAR: FULL CUSTOMIZATION ---
st.sidebar.title("🎨 Caption Customizer")

# Font & Color
font_size = st.sidebar.slider("Font Size", 20, 100, 55)
text_color = st.sidebar.color_picker("Text Color", "#FFCC00") # Viral Yellow
outline_color = st.sidebar.color_picker("Outline Color", "#000000")

# Effects & Animations
st.sidebar.subheader("✨ Effects")
effect_type = st.sidebar.selectbox("Animation Style", [
    "Dynamic Pop (Viral)", 
    "Center Pulse (Clean)", 
    "Bottom Slide (Modern)"
])

# Translation
target_lang = st.sidebar.radio("Subtitle Content", ["Hindi (Original)", "English (Translate)"])

# --- 3. MAIN DASHBOARD ---
st.title("🎥 Auto-Dynamic Caption Studio")
st.info("Upload your Hindi video. I will detect the speech and sync the captions perfectly.")

uploaded_video = st.file_uploader("Upload MP4 Video", type=["mp4", "mov", "avi"])

if uploaded_video:
    # Save video locally
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_video.getbuffer())
    
    st.video("input_video.mp4")

    if st.button("🔥 Generate Dynamic Captions"):
        with st.spinner("Step 1: Listening to Hindi Speech..."):
            # Detect and Transcribe/Translate
            task = "translate" if target_lang == "English (Translate)" else "transcribe"
            result = whisper_engine.transcribe("input_video.mp4", task=task, word_timestamps=True)
        
        with st.spinner("Step 2: Designing Dynamic Effects..."):
            # ASS File Header (The styling engine)
            ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 640
PlayResY: 360

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV
Style: Default,Arial,{font_size},{hex_to_ass(text_color)},{hex_to_ass(outline_color)},1,2,2,20
"""
            events_header = "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            ass_lines = []
            for segment in result['segments']:
                for word in segment['words']:
                    start = word['start']
                    end = word['end']
                    
                    # Convert time to ASS format (0:00:00.00)
                    def format_time(t):
                        hours = int(t // 3600)
                        minutes = int((t % 3600) // 60)
                        seconds = t % 60
                        return f"{hours:01}:{minutes:02}:{seconds:05.2f}"

                    t_start = format_time(start)
                    t_end = format_time(end)
                    clean_word = word['word'].strip().upper()

                    # Apply Selected Animation Effect
                    if effect_type == "Dynamic Pop (Viral)":
                        # Random position jitter + Zoom
                        x, y = 320 + random.randint(-15, 15), 180 + random.randint(-10, 10)
                        effect_code = f"{{\\pos({x},{y})\\t(0,100,\\fscx130\\fscy130)\\t(100,200,\\fscx100\\fscy100)}}"
                    elif effect_type == "Center Pulse (Clean)":
                        effect_code = f"{{\\pos(320,180)\\t(0,100,\\fscx140\\fscy140)\\t(100,200,\\fscx100\\fscy100)}}"
                    else: # Bottom Slide
                        effect_code = f"{{\\pos(320,300)\\move(320,320,320,300,0,100)}}"

                    ass_lines.append(f"Dialogue: 0,{t_start},{t_end},Default,,0,0,0,,{effect_code}{clean_word}")

            # Write the Caption File
            with open("captions.ass", "w", encoding="utf-8") as f:
                f.write(ass_header + events_header + "\n".join(ass_lines))

        with st.spinner("Step 3: Rendering Final Video..."):
            # Use FFmpeg to burn subtitles into the video
            output_file = "final_viral_video.mp4"
            render_cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-vf", "ass=captions.ass",
                "-c:a", "copy", output_file
            ]
            subprocess.run(render_cmd)
            
            st.success("✅ Perfectly Synced!")
            st.video(output_file)
            
            with open(output_file, "rb") as f:
                st.download_button("📥 Download Viral Video", f, "viral_captions.mp4")