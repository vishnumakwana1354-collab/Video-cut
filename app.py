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

# Safe multi-version import for MoviePy (v1.x & v2.x compatible)
VideoFileClip = None
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
except ImportError:
    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        try:
            import moviepy as mp
            VideoFileClip = mp.VideoFileClip
        except ImportError:
            # Auto install moviepy if completely missing
            install_package("moviepy", ["--break-system-packages"])
            try:
                from moviepy.video.io.VideoFileClip import VideoFileClip
            except ImportError:
                import moviepy as mp
                VideoFileClip = mp.VideoFileClip

# Page configuration
st.set_page_config(
    page_title="JGV Video Splitter (Python)",
    page_icon="✂️",
    layout="centered"
)

# Language Dictionary
translations = {
    "gu": {
        "title": "JGV વીડિયો સ્પ્લિટ એપ",
        "subtitle": "તમારા વીડિયોના નાના ટુકડા સરળતાથી કરો",
        "upload_label": "વીડિયો ફાઈલ અહીં અપલોડ કરો:",
        "split_method": "સ્પ્લિટ રીત પસંદ કરો:",
        "opt_duration": "ચોક્કસ સમયગાળા મુજબ (By Duration)",
        "opt_parts": "સરખા ભાગોની સંખ્યા મુજબ (By Equal Parts)",
        "opt_range": "કસ્ટમ સમયગાળો (Custom Range)",
        "duration_label": "દરેક ક્લિપનો સમયગાળો (સેકન્ડમાં):",
        "parts_label": "કેટલા ભાગ કરવા છે?:",
        "start_label": "શરૂઆતનો સમય (સેકન્ડ):",
        "end_label": "અંતનો સમય (સેકન્ડ):",
        "btn_start": "વીડિયો પ્રોસેસ શરૂ કરો ✂️",
        "success": "તમારો વીડિયો સફળતાપૂર્વક સ્પ્લિટ થઈ ગયો છે!",
        "download": "ડાઉનલોડ કરો",
        "error": "ભૂલ આવી:"
    },
    "en": {
        "title": "JGV Video Splitter App",
        "subtitle": "Split your videos easily into smaller clips",
        "upload_label": "Upload Video File:",
        "split_method": "Select Split Method:",
        "opt_duration": "By Duration (in seconds)",
        "opt_parts": "By Equal Parts",
        "opt_range": "Custom Range",
        "duration_label": "Clip Duration (seconds):",
        "parts_label": "Number of Parts:",
        "start_label": "Start Time (seconds):",
        "end_label": "End Time (seconds):",
        "btn_start": "Start Processing ✂️",
        "success": "Video successfully split!",
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

# File Uploader
uploaded_file = st.file_uploader(t["upload_label"], type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    # Save uploaded file to temp file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    try:
        # Load video using safe clip reader
        clip = VideoFileClip(video_path)
        total_duration = clip.duration

        st.video(video_path)
        st.info(f"⏱️ વીડિયોનો કુલ સમયગાળો (Total Duration): **{round(total_duration, 2)} સેકન્ડ**")

        # Split Method Options
        method = st.selectbox(
            t["split_method"],
            [t["opt_duration"], t["opt_parts"], t["opt_range"]]
        )

        segments = []

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

        # Process Button
        if st.button(t["btn_start"], type="primary"):
            st.markdown("### ⚙️ પ્રોસેસ ચાલુ છે...")
            progress_bar = st.progress(0)

            out_files = []
            
            for index, (start_time, end_time) in enumerate(segments):
                # Compatible subclip method call for both MoviePy v1 & v2
                if hasattr(clip, 'subclip'):
                    sub_clip = clip.subclip(start_time, end_time)
                elif hasattr(clip, 'subclipped'):
                    sub_clip = clip.subclipped(start_time, end_time)
                else:
                    sub_clip = clip.subclip(start_time, end_time)

                out_path = f"clip_{index + 1}.mp4"
                
                # Fast video export using moviepy
                sub_clip.write_videofile(
                    out_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    logger=None
                )
                out_files.append((out_path, index + 1))
                progress_bar.progress((index + 1) / len(segments))

            st.success(t["success"])

            # Display generated clips and download buttons
            for out_path, num in out_files:
                with open(out_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Clip {num} {t['download']}",
                        data=f,
                        file_name=f"clip_{num}.mp4",
                        mime="video/mp4"
                    )
                # Cleanup temp file
                if os.path.exists(out_path):
                    os.remove(out_path)

        clip.close()

    except Exception as e:
        st.error(f"{t['error']} {str(e)}")

    finally:
        # Cleanup input file
        if os.path.exists(video_path):
            os.remove(video_path)
