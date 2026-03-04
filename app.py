import streamlit as st
import whisper
import os
import random
import subprocess
from pydub import AudioSegment

# --- 1. CORE STUDIO CONFIG ---
st.set_page_config(page_title="Avinash Sen: Chaos Captions", layout="wide")

def hex_to_ass(hex_color):
    """Converts #RRGGBB to ASS format &HBBGGRR"""
    hex_color = hex_color.lstrip('#')
    return f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_engine = load_whisper()

# --- 2. SIDEBAR: CHAOS & POWER SETTINGS ---
st.sidebar.title("💎 Viral Chaos Engine")

# Standard Styling
font_size = st.sidebar.slider("Font Size", 30, 100, 65)
main_color = st.sidebar.color_picker("Normal Text Color", "#FFFFFF") 

# Highlight Styling
st.sidebar.subheader("🔥 Power Word Highlight")
highlight_color = st.sidebar.color_picker("Highlight Color", "#FF0055") # Neon Pink/Red
power_words = st.sidebar.text_area("Keywords to Highlight (Comma separated):", 
                                   "PAISA, GOAL, SUCCESS, ZINDAGI, WIN, AI, DOSTON")

st.sidebar.subheader("🔊 Sound Effects")
use_sfx = st.sidebar.checkbox("Play 'Pop' sound on Highlights", value=True)

# --- 3. THE PROCESSING LOGIC ---
st.title("🌪️ Random Hover & Pop Studio")
st.info("Words will appear randomly anywhere, Pop in size, and Hover upwards!")

uploaded_file = st.file_uploader("Upload your MP4", type=["mp4"])

if uploaded_file:
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.video("temp_video.mp4")

    if st.button("✨ Generate Viral Chaos Captions"):
        with st.spinner("AI is listening to your Hindi audio..."):
            result = whisper_engine.transcribe("temp_video.mp4", word_timestamps=True)
            
            # Extract main audio for SFX mixing
            subprocess.run(["ffmpeg", "-y", "-i", "temp_video.mp4", "-q:a", "0", "-map", "a", "main_audio.wav"])
            main_audio = AudioSegment.from_wav("main_audio.wav")
            
            # Load the SFX (You need a pop.wav file in your folder)
            if use_sfx and os.path.exists("pop.wav"):
                pop_sfx = AudioSegment.from_wav("pop.wav")
            else:
                pop_sfx = None
            
        with st.spinner("Building Random Position & Hover Layers..."):
            ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 640
PlayResY: 360

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Alignment, MarginV
Style: Default,Arial,{font_size},{hex_to_ass(main_color)},&H00000000,1,2,2,20
Style: Highlight,Impact,{font_size + 15},{hex_to_ass(highlight_color)},&H00000000,1,3,2,20
"""
            events_header = "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            
            ass_lines = []
            highlight_list = [w.strip().upper() for w in power_words.split(",")]

            for segment in result['segments']:
                for word in segment['words']:
                    start, end = word['start'], word['end']
                    clean_w = word['word'].strip().upper().replace('.', '').replace(',', '')
                    
                    def format_time(t):
                        return f"{int(t//3600):01}:{int((t%3600)//60):02}:{t%60:05.2f}"

                    t_s, t_e = format_time(start), format_time(end)
                    
                    # Highlight & SFX Logic
                    is_highlight = any(hw in clean_w for hw in highlight_list)
                    current_style = "Highlight" if is_highlight else "Default"
                    
                    if is_highlight and pop_sfx:
                        # Overlay the pop sound at the exact millisecond the word appears
                        insert_pos = int(start * 1000) 
                        main_audio = main_audio.overlay(pop_sfx, position=insert_pos)

                    # --- THE VISUAL MAGIC ---
                    # 1. Random Anywhere: x from 100 to 540, y from 50 to 300 (Keeps it on screen)
                    x = random.randint(100, 540)
                    y = random.randint(50, 300)
                    
                    # 2. Pop & Hover: 
                    # \move(x,y, x,y-20) makes it float up slowly.
                    # \t(...) makes it pop big then shrink.
                    animation = f"{{\\move({x},{y},{x},{y-25})\\t(0,80,\\fscx160\\fscy160)\\t(80,200,\\fscx100\\fscy100)}}"
                    
                    ass_lines.append(f"Dialogue: 0,{t_s},{t_e},{current_style},,0,0,0,,{animation}{clean_w}")

            # Export Mixed Audio and ASS
            main_audio.export("mixed_audio.wav", format="wav")
            with open("viral.ass", "w", encoding="utf-8") as f:
                f.write(ass_header + events_header + "\n".join(ass_lines))

        with st.spinner("Burning Chaos Effects into Video..."):
            output_name = "output_chaos.mp4"
            # FFmpeg merges the NEW mixed audio + video + ASS subtitles
            subprocess.run([
                "ffmpeg", "-y", "-i", "temp_video.mp4", "-i", "mixed_audio.wav",
                "-vf", "ass=viral.ass", "-c:v", "libx264", "-c:a", "aac", 
                "-map", "0:v:0", "-map", "1:a:0", output_name
            ])
            
            st.success("✅ Random Hover, Pops, and Sound Effects Synced!")
            st.video(output_name)
            with open(output_name, "rb") as f:
                st.download_button("📥 Download Chaos Edit", f, "chaos_edit.mp4")