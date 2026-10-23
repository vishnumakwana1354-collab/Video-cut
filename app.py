import sys
import subprocess
import os
import tempfile
import math

# Auto install required packages automatically if missing
def install_package(package, flags=None):
    cmd = [sys.executable, "-m", "pip", "install", package]
    if flags:
        cmd.extend(flags)
    try:
        subprocess.check_call(cmd)
    except Exception as e:
        pass

# Ensure streamlit is installed
try:
    import streamlit as st
except ImportError:
    install_package("streamlit", ["--break-system-packages"])
    import streamlit as st

# Safe multi-version import for MoviePy & AudioFileClip
VideoFileClip = None
AudioFileClip = None
vfx = None

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, vfx
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        import moviepy.video.fx.all as vfx
    except ImportError:
        install_package("moviepy", ["--break-system-packages"])
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, vfx
        except ImportError:
            import moviepy as mp
            VideoFileClip = mp.VideoFileClip
            AudioFileClip = mp.AudioFileClip

# Page configuration
st.set_page_config(
    page_title="JGV Studio Video Editor & Splitter",
    page_icon="🎬",
    layout="centered"
)

# Language Dictionary
translations = {
    "gu": {
        "title": "JGV વીડિયો એડિટર અને સ્પ્લિટ ઓલ-ઈન-વન એપ 🎬",
        "subtitle": "વીડિયો કટ કરો, સ્પીડ બદલો, ઓડિયો ઉમેરો/હટાવો અને સરળતાથી ડાઉનલોડ કરો",
        "upload_label": "૧. મુખ્ય વીડિયો ફાઈલ અપલોડ કરો:",
        "audio_upload_label": "નવું સંગીત/ઓડિયો અપલોડ કરો (MP3 / WAV):",
        "tool_selection": "તમારું ટૂલ પસંદ કરો:",
        "opt_split": "✂️ વીડિયો સ્પ્લિટ (તુકડા કરવા)",
        "opt_audio": "🎵 ઓડિયો સેટિંગ્સ (સંગીત એડ / રીમુવ કરવું)",
        "opt_speed": "⚡ વીડિયો સ્પીડ (ફાસ્ટ / સ્લો કરવું)",
        "split_method": "સ્પ્લિટ પદ્ધતિ પસંદ કરો:",
        "opt_duration": "ચોક્કસ સમયગાળા મુજબ (By Duration)",
        "opt_parts": "સરખા ભાગોની સંખ્યા મુજબ (By Equal Parts)",
        "opt_range": "કસ્ટમ સમયગાળો (Custom Range)",
        "duration_label": "દરેક ક્લિપનો સમયગાળો (સેકન્ડમાં):",
        "parts_label": "કેટલા ભાગ કરવા છે?:",
        "start_label": "શરૂઆતનો સમય (સેકન્ડ):",
        "end_label": "અંતનો સમય (સેકન્ડ):",
        "audio_action": "ઓડિયો વિકલ્પ પસંદ કરો:",
        "audio_mute": "મૂળ સંગીત/ઓડિયો દુર કરવો (Mute Audio)",
        "audio_replace": "નવું સંગીત/ઓડિયો ઉમેરવો (Add/Replace Music)",
        "speed_label": "વીડિયો સ્પીડ પસંદ કરો (1.0x સાધારણ સ્પીડ છે):",
        "btn_start": "પ્રોસેસ શરૂ કરો 🚀",
        "success": "પ્રોસેસ સફળતાપૂર્વક પૂર્ણ થઈ છે!",
        "download_all": "📥 બધા વીડિયો એકસાથે ડાઉનલોડ કરો",
        "download": "ડાઉનલોડ",
        "error": "ભૂલ આવી:"
    },
    "en": {
        "title": "JGV Video Editor & Splitter All-in-One 🎬",
        "subtitle": "Split videos, change speed, add/remove music, and download easily",
        "upload_label": "1. Upload Main Video File:",
        "audio_upload_label": "Upload New Audio/Music (MP3 / WAV):",
        "tool_selection": "Select Your Tool:",
        "opt_split": "✂️ Video Splitter",
        "opt_audio": "🎵 Audio Settings (Add/Remove Music)",
        "opt_speed": "⚡ Video Speed (Fast / Slow)",
        "split_method": "Select Split Method:",
        "opt_duration": "By Duration (in seconds)",
        "opt_parts": "By Equal Parts",
        "opt_range": "Custom Range",
        "duration_label": "Clip Duration (seconds):",
        "parts_label": "Number of Parts:",
        "start_label": "Start Time (seconds):",
        "end_label": "End Time (seconds):",
        "audio_action": "Select Audio Option:",
        "audio_mute": "Remove original music/audio (Mute)",
        "audio_replace": "Add/Replace new background music",
        "speed_label": "Select Video Speed Multiplier (1.0x is Normal):",
        "btn_start": "Start Processing 🚀",
        "success": "Processing completed successfully!",
        "download_all": "📥 Download All Clips",
        "download": "Download",
        "error": "Error occurred:"
    }
}

# Language selection state
if "lang" not in st.session_state:
    st.session_state["lang"] = "gu"

col_title, col_lang = st.columns([4, 1])

with col_lang:
    if st.button("EN / GU"):
        st.session_state["lang"] = "en" if st.session_state["lang"] == "gu" else "gu"

t = translations[st.session_state["lang"]]

with col_title:
    st.title(t["title"])
    st.caption(t["subtitle"])

st.markdown("---")

# Main Video Upload
uploaded_file = st.file_uploader(t["upload_label"], type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    try:
        clip = VideoFileClip(video_path)
        total_duration = clip.duration

        st.video(video_path)
        st.info(f"⏱️ વીડિયોનો સમયગાળો (Duration): **{round(total_duration, 2)} સેકન્ડ**")

        # Feature selection
        tool = st.radio(t["tool_selection"], [t["opt_split"], t["opt_audio"], t["opt_speed"]])

        segments = []
        audio_file_path = None
        speed_factor = 1.0
        mode = "split"

        if tool == t["opt_split"]:
            mode = "split"
            method = st.selectbox(
                t["split_method"],
                [t["opt_duration"], t["opt_parts"], t["opt_range"]]
            )

            if method == t["opt_duration"]:
                seg_dur = st.number_input(t["duration_label"], min_value=1.0, value=60.0, step=1.0)
                count = math.ceil(total_duration / seg_dur)
                for i in range(count):
                    s = i * seg_dur
                    e = min((i + 1) * seg_dur, total_duration)
                    segments.append((s, e))

            elif method == t["opt_parts"]:
                parts_num = st.number_input(t["parts_label"], min_value=2, value=2, step=1)
                seg_dur = total_duration / parts_num
                for i in range(parts_num):
                    s = i * seg_dur
                    e = (i + 1) * seg_dur
                    segments.append((s, e))

            elif method == t["opt_range"]:
                col1, col2 = st.columns(2)
                with col1:
                    start_t = st.number_input(t["start_label"], min_value=0.0, max_value=float(total_duration), value=0.0)
                with col2:
                    end_t = st.number_input(t["end_label"], min_value=0.0, max_value=float(total_duration), value=min(10.0, float(total_duration)))
                
                if start_t < end_t:
                    segments.append((start_t, end_t))
                else:
                    st.error("અંતનો સમય શરૂઆતના સમય કરતા વધારે હોવો જોઈએ.")

        elif tool == t["opt_audio"]:
            mode = "audio"
            audio_opt = st.radio(t["audio_action"], [t["audio_mute"], t["audio_replace"]])
            if audio_opt == t["audio_replace"]:
                audio_upload = st.file_uploader(t["audio_upload_label"], type=["mp3", "wav", "m4a", "aac"])
                if audio_upload is not None:
                    afile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    afile.write(audio_upload.read())
                    audio_file_path = afile.name

        elif tool == t["opt_speed"]:
            mode = "speed"
            speed_factor = st.slider(t["speed_label"], min_value=0.25, max_value=3.0, value=1.5, step=0.25)

        # Process Button
        if st.button(t["btn_start"], type="primary"):
            st.markdown("### ⚙️ પ્રોસેસ ચાલુ છે...")
            progress_bar = st.progress(0)
            generated_clips = []

            if mode == "split":
                for index, (start_time, end_time) in enumerate(segments):
                    if hasattr(clip, 'subclip'):
                        sub_clip = clip.subclip(start_time, end_time)
                    else:
                        sub_clip = clip.subclipped(start_time, end_time)

                    out_path = f"clip_{index + 1}.mp4"
                    sub_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                    generated_clips.append(out_path)
                    progress_bar.progress((index + 1) / len(segments))

            elif mode == "audio":
                out_path = "edited_audio_video.mp4"
                if audio_opt == t["audio_mute"]:
                    edited_clip = clip.without_audio() if hasattr(clip, 'without_audio') else clip.set_audio(None)
                else:
                    if audio_file_path:
                        new_audio = AudioFileClip(audio_file_path)
                        edited_clip = clip.set_audio(new_audio)
                    else:
                        edited_clip = clip

                edited_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                generated_clips.append(out_path)
                progress_bar.progress(1.0)

            elif mode == "speed":
                out_path = f"speed_{speed_factor}x_video.mp4"
                if vfx and hasattr(vfx, 'speedx'):
                    edited_clip = vfx.speedx(clip, speed_factor)
                elif hasattr(clip, 'fx'):
                    edited_clip = clip.fx(vfx.speedx, speed_factor)
                else:
                    edited_clip = clip

                edited_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                generated_clips.append(out_path)
                progress_bar.progress(1.0)

            st.success(t["success"])

            # Automatic / Instant Download Buttons
            st.markdown("### 📥 ડાઉનલોડ સેક્શન")
            for idx, out_file in enumerate(generated_clips):
                with open(out_file, "rb") as file_data:
                    st.download_button(
                        label=f"⬇️ ડાઉનલોડ કરો ({os.path.basename(out_file)})",
                        data=file_data,
                        file_name=os.path.basename(out_file),
                        mime="video/mp4",
                        key=f"dl_{idx}"
                    )
                if os.path.exists(out_file):
                    os.remove(out_file)

        clip.close()

    except Exception as e:
        st.error(f"{t['error']} {str(e)}")

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
