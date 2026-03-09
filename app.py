import streamlit as st
import whisper
import os
import random
import subprocess
import gc
from gtts import gTTS
from pydub import AudioSegment

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="Avinash: Voice Fusion Studio", layout="wide")

@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny") 

whisper_engine = load_whisper()

def hex_to_ass(hex_c):
    hex_c = hex_c.lstrip('#')
    return f"&H00{hex_c[4:6]}{hex_c[2:4]}{hex_c[0:2]}"

# --- 1. VOICE PRESETS (The "Soul") ---
VOICE_PRESETS = {
    "🔥 The Motivator (US)": {"tld": "us", "speed": 1.15, "pitch": 1.05},
    "🇬🇧 The Storyteller (UK)": {"tld": "uk", "speed": 1.0, "pitch": 0.95},
    "⚡ Hyper Growth (AU)": {"tld": "com.au", "speed": 1.3, "pitch": 1.1},
    "🎙️ Midnight Late Night (CA)": {"tld": "ca", "speed": 0.9, "pitch": 0.85}
}

# --- 2. CAPTION PRESETS (The "Look") ---
CAPTION_PRESETS = {
    "👑 Hormozi Viral": {
        "font": "Arial Black", "size": 95, "color": "#FFFF00", 
        "pop": 160, "layout": "Center", "shake": True
    },
    "🌪️ Kinetic Chaos": {
        "font": "Impact", "size": 110, "color": "#00F2FF", 
        "pop": 185, "layout": "Random", "shake": True
    },
    "🌑 Cyberpunk Glow": {
        "font": "Courier New", "size": 85, "color": "#FF00FF", 
        "pop": 130, "layout": "Lower Third", "shake": False
    },
    "💎 Minimal Lux": {
        "font": "Verdana", "size": 70, "color": "#FFFFFF", 
        "pop": 115, "layout": "Center", "shake": False
    }
}

st.sidebar.title("🧬 Voice Fusion & Presets")

with st.sidebar:
    v_mode = st.selectbox("Select Voice Personality", list(VOICE_PRESETS.keys()))
    c_mode = st.selectbox("Select Visual Preset", list(CAPTION_PRESETS.keys()))
    fusion_strength = st.slider("Fusion Anti-Copyright Strength", 0.0, 1.0, 0.5)
    script = st.text_area("Your Script:", "Don't let your dreams be dreams. Just do it.")

st.title("🎬 Master Fusion Studio")

if st.button("🚀 EXECUTE UNIQUE RENDER"):
    if script:
        try:
            v_cfg = VOICE_PRESETS[v_mode]
            c_cfg = CAPTION_PRESETS[c_mode]

            with st.spinner("Applying Voice Fusion..."):
                # Generate Base
                tts = gTTS(text=script, lang='en', tld=v_cfg['tld'])
                tts.save("base.mp3")
                
                # Fusion Engine (Anti-Copyright)
                sound = AudioSegment.from_mp3("base.mp3")
                
                # 1. Pitch Shift & Speed
                new_sample_rate = int(sound.frame_rate * (v_cfg['pitch'] + (fusion_strength * 0.05)))
                fused_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
                fused_sound = fused_sound.set_frame_rate(44100)
                
                if v_cfg['speed'] != 1.0:
                    fused_sound = fused_sound.speedup(playback_speed=v_cfg['speed'])
                
                fused_sound.export("final_audio.mp3", format="mp3")
                duration = len(fused_sound) / 1000.0

            with st.spinner("Syncing Dynamic Captions..."):
                gc.collect()
                result = whisper_engine.transcribe("final_audio.mp3", word_timestamps=True, fp16=False)
                
                ass_header = f"""[Script Info]
PlayResX: 640
PlayResY: 360
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, ShadowColour, BorderStyle, Outline, Shadow, Alignment, MarginV
Style: Default,{c_cfg['font']},{c_cfg['size']},{hex_to_ass(c_cfg['color'])},&H00000000,&H80000000,1,4,3,5,10
"""
                events = "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                lines = []
                
                for word_data in [w for s in result['segments'] for w in s['words']]:
                    text = word_data['word'].strip().upper()
                    start, end = word_data['start'], word_data['end']
                    
                    # Position Logic
                    if c_cfg['layout'] == "Random":
                        x, y = random.randint(150, 490), random.randint(100, 260)
                    elif c_cfg['layout'] == "Lower Third":
                        x, y = 320, 280
                    else: x, y = 320, 180

                    # Shake & Pop Logic
                    shake = f"\\t(0,50,\\move({x},{y},{x+2},{y+2}))\\t(50,100,\\move({x+2},{y+2},{x},{y}))" if c_cfg['shake'] else ""
                    anim = f"{{\\an5\\move({x},{y},{x},{y-20}){shake}\\t(0,100,\\fscx{c_cfg['pop']}\\fscy{c_cfg['pop']})\\t(100,200,\\fscx100\\fscy100)}}"
                    
                    ts, te = f"{int(start//3600)}:{int((start%3600)//60):02}:{start%60:05.2f}", f"{int(end//3600)}:{int((end%3600)//60):02}:{end%60:05.2f}"
                    lines.append(f"Dialogue: 0,{ts},{te},Default,,0,0,0,,{anim}{text}")

                with open("green.ass", "w") as f: f.write(ass_header + events + "\n".join(lines))

            with st.spinner("Final Master Rendering..."):
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x00FF00:s=640x360:r=30:d=120",
                    "-i", "final_audio.mp3", "-vf", "ass=green.ass", "-c:v", "libx264", 
                    "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-shortest", "output.mp4"
                ])

            st.video("output.mp4")
            st.download_button("📥 Download Unique Green Screen", open("output.mp4", "rb"), "fusion_export.mp4")

        except Exception as e: st.error(f"Error: {e}")
        finally: gc.collect()