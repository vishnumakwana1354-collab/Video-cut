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

# Safe multi-version import for MoviePy
VideoFileClip = None
AudioFileClip = None
vfx = None
afx = None

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, vfx, afx
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        import moviepy.video.fx.all as vfx
        import moviepy.audio.fx.all as afx
    except ImportError:
        install_package("moviepy", ["--break-system-packages"])
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, vfx, afx
        except ImportError:
            import moviepy as mp
            VideoFileClip = mp.VideoFileClip
            AudioFileClip = mp.AudioFileClip

# Page configuration
st.set_page_config(
    page_title="JGV ShotCut Pro Video Studio & Splitter",
    page_icon="🎬",
    layout="wide"
)

# Language Dictionary
translations = {
    "gu": {
        "title": "JGV ShotCut પ્રો વીડિયો એડિટર અને સ્પ્લિટ ઓલ-ઈન-વન એપ 🎬",
        "subtitle": "વીડિયો સ્પ્લિટ, સ્પીડ કંટ્રોલ, ઓડિયો ઉમેરવો/હટાવવો, રિવર્સ, ક્રોપ અને ઈન્સ્ટન્ટ ડાઉનલોડ કરો",
        "upload_label": "૧. મુખ્ય વીડિયો ફાઈલ અપલોડ કરો (Upload Main Video):",
        "audio_upload_label": "નવું સંગીત/ઓડિયો ઉમેરો (MP3 / WAV / M4A):",
        "tool_selection": "ટૂલ પસંદ કરો (Select Editing Tool):",
        "opt_split": "✂️ વીડિયો સ્પ્લિટ અને કટર (Video Splitter)",
        "opt_audio": "🎵 ઓડિયો મ્યુઝિક સેટિંગ્સ (Audio / Music Tools)",
        "opt_speed": "⚡ સ્પીડ અને સ્લો મોશન (Speed & Slow-Mo)",
        "opt_reverse": "🔄 રિવર્સ વીડિયો (Play Video in Reverse)",
        "opt_crop": "📐 ક્રોપ અને રેશિયો (Crop & Aspect Ratio)",
        "opt_extract": "🔊 વીડિયોમાંથી ઓડિયો અલગ કરો (Extract MP3)",
        "split_method": "સ્પ્લિટ પદ્ધતિ પસંદ કરો:",
        "opt_duration": "ચોક્કસ સમયગાળા મુજબ (By Duration)",
        "opt_parts": "સરખા ભાગોની સંખ્યા મુજબ (By Equal Parts)",
        "opt_range": "કસ્ટમ સમયગાળો (Custom Range)",
        "duration_label": "દરેક ક્લિપનો સમયગાળો (સેકન્ડમાં):",
        "parts_label": "કેટલા ભાગ કરવા છે?:",
        "start_label": "શરૂઆતનો સમય (સેકન્ડ):",
        "end_label": "અંતનો સમય (સેકન્ડ):",
        "audio_action": "ઓડિયો વિકલ્પ પસંદ કરો:",
        "audio_mute": "મૂળ સંગીત દુર કરવું (Mute Original Audio)",
        "audio_replace": "નવું સંગીત ઉમેરવું (Add/Replace Music)",
        "speed_label": "વીડિયો સ્પીડ પસંદ કરો (1.0x સામાન્ય છે, 0.5x સ્લો મોશન, 2.0x ફાસ્ટ):",
        "ratio_label": "એસ્પેક્ટ રેશિયો પસંદ કરો (For IG, YouTube, TikTok):",
        "btn_start": "પ્રોસેસ શરૂ કરો (Start Processing) 🚀",
        "success": "પ્રોસેસ સફળતાપૂર્વક પૂર્ણ થઈ છે!",
        "download": "ડાઉનલોડ કરો (Download)",
        "error": "ભૂલ આવી:"
    },
    "en": {
        "title": "JGV ShotCut Pro Video Studio & Splitter 🎬",
        "subtitle": "Pro All-in-One Editor: Split, Change Speed, Add/Remove Audio, Reverse, Crop & Instant Download",
        "upload_label": "1. Upload Main Video File:",
        "audio_upload_label": "Upload New Audio/Music (MP3 / WAV / M4A):",
        "tool_selection": "Select Editing Tool:",
        "opt_split": "✂️ Video Splitter & Cutter",
        "opt_audio": "🎵 Audio / Music Editor",
        "opt_speed": "⚡ Video Speed (Fast & Slow Motion)",
        "opt_reverse": "🔄 Video Reverser",
        "opt_crop": "📐 Crop & Aspect Ratio (IG, Shorts, Reels)",
        "opt_extract": "🔊 Extract MP3 Audio from Video",
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
        "speed_label": "Select Video Speed (1.0x Normal, 0.5x Slo-Mo, 2.0x Fast):",
        "ratio_label": "Select Aspect Ratio:",
        "btn_start": "Start Processing 🚀",
        "success": "Processing completed successfully!",
        "download": "Download",
        "error": "Error occurred:"
    }
}

# Language selection state
if "lang" not in st.session_state:
    st.session_state["lang"] = "gu"

col_title, col_lang = st.columns([5, 1])

with col_lang:
    if st.button("🌐 EN / GU"):
        st.session_state["lang"] = "en" if st.session_state["lang"] == "gu" else "gu"

t = translations[st.session_state["lang"]]

with col_title:
    st.title(t["title"])
    st.caption(t["subtitle"])

st.markdown("---")

# Main Video Upload
uploaded_file = st.file_uploader(t["upload_label"], type=["mp4", "mov", "avi", "mkv", "webm"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    try:
        clip = VideoFileClip(video_path)
        total_duration = clip.duration

        col_preview, col_info = st.columns([2, 1])
        with col_preview:
            st.video(video_path)
        with col_info:
            st.info(f"⏱️ **સમયગાળો (Duration):** {round(total_duration, 2)} સેકન્ડ")
            st.info(f"📐 **રિઝોલ્યુશન (Resolution):** {clip.w} x {clip.h} px")
            st.info(f"🔊 **ઓડિયો સ્ત્રોત:** {'હા (Audio Present)' if clip.audio else 'ના (Muted)'}")

        st.markdown("---")

        # Feature selection
        tool = st.radio(
            t["tool_selection"],
            [
                t["opt_split"],
                t["opt_audio"],
                t["opt_speed"],
                t["opt_reverse"],
                t["opt_crop"],
                t["opt_extract"]
            ],
            horizontal=True
        )

        segments = []
        audio_file_path = None
        speed_factor = 1.0
        aspect_ratio = "Original"

        # 1. SPLIT TOOL
        if tool == t["opt_split"]:
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

        # 2. AUDIO TOOL
        elif tool == t["opt_audio"]:
            audio_opt = st.radio(t["audio_action"], [t["audio_mute"], t["audio_replace"]])
            if audio_opt == t["audio_replace"]:
                audio_upload = st.file_uploader(t["audio_upload_label"], type=["mp3", "wav", "m4a", "aac"])
                if audio_upload is not None:
                    afile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    afile.write(audio_upload.read())
                    audio_file_path = afile.name

        # 3. SPEED TOOL
        elif tool == t["opt_speed"]:
            speed_factor = st.slider(t["speed_label"], min_value=0.25, max_value=3.0, value=1.5, step=0.25)

        # 4. CROP TOOL
        elif tool == t["opt_crop"]:
            aspect_ratio = st.selectbox(
                t["ratio_label"],
                ["Original", "9:16 (Instagram Reels / TikTok)", "16:9 (YouTube Landscape)", "1:1 (Instagram Post)"]
            )

        # Process Button
        if st.button(t["btn_start"], type="primary"):
            st.markdown("### ⚙️ પ્રોસેસ ચાલુ છે (Processing Video)...")
            progress_bar = st.progress(0)
            generated_clips = []

            # 1. SPLIT PROCESSING
            if tool == t["opt_split"]:
                for index, (start_time, end_time) in enumerate(segments):
                    if hasattr(clip, 'subclip'):
                        sub_clip = clip.subclip(start_time, end_time)
                    else:
                        sub_clip = clip.subclipped(start_time, end_time)

                    out_path = f"split_clip_{index + 1}.mp4"
                    sub_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                    generated_clips.append((out_path, "video/mp4"))
                    progress_bar.progress((index + 1) / len(segments))

            # 2. AUDIO PROCESSING
            elif tool == t["opt_audio"]:
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
                generated_clips.append((out_path, "video/mp4"))
                progress_bar.progress(1.0)

            # 3. SPEED PROCESSING
            elif tool == t["opt_speed"]:
                out_path = f"speed_{speed_factor}x_video.mp4"
                if vfx and hasattr(vfx, 'speedx'):
                    edited_clip = vfx.speedx(clip, speed_factor)
                elif hasattr(clip, 'fx'):
                    edited_clip = clip.fx(vfx.speedx, speed_factor)
                else:
                    edited_clip = clip

                edited_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                generated_clips.append((out_path, "video/mp4"))
                progress_bar.progress(1.0)

            # 4. REVERSE PROCESSING
            elif tool == t["opt_reverse"]:
                out_path = "reversed_video.mp4"
                if vfx and hasattr(vfx, 'time_mirror'):
                    edited_clip = vfx.time_mirror(clip)
                elif hasattr(clip, 'fx'):
                    edited_clip = clip.fx(vfx.time_mirror)
                else:
                    edited_clip = clip

                edited_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                generated_clips.append((out_path, "video/mp4"))
                progress_bar.progress(1.0)

            # 5. CROP PROCESSING
            elif tool == t["opt_crop"]:
                out_path = "cropped_video.mp4"
                w, h = clip.w, clip.h

                if aspect_ratio == "9:16 (Instagram Reels / TikTok)":
                    target_w = int(h * (9 / 16))
                    edited_clip = clip.crop(x_center=w / 2, width=min(w, target_w))
                elif aspect_ratio == "16:9 (YouTube Landscape)":
                    target_h = int(w * (9 / 16))
                    edited_clip = clip.crop(y_center=h / 2, height=min(h, target_h))
                elif aspect_ratio == "1:1 (Instagram Post)":
                    min_dim = min(w, h)
                    edited_clip = clip.crop(x_center=w / 2, y_center=h / 2, width=min_dim, height=min_dim)
                else:
                    edited_clip = clip

                edited_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                generated_clips.append((out_path, "video/mp4"))
                progress_bar.progress(1.0)

            # 6. AUDIO EXTRACTION (MP3)
            elif tool == t["opt_extract"]:
                out_path = "extracted_audio.mp3"
                if clip.audio:
                    clip.audio.write_audiofile(out_path, logger=None)
                    generated_clips.append((out_path, "audio/mp3"))
                    progress_bar.progress(1.0)
                else:
                    st.error("આ વીડિયોમાં ઓડિયો નથી!")

            st.success(t["success"])

            # Automatic / Instant Download Section
            st.markdown("### 📥 ડાઉનલોડ સેક્શન (Instant Download)")
            for idx, (out_file, mime_type) in enumerate(generated_clips):
                if os.path.exists(out_file):
                    with open(out_file, "rb") as file_data:
                        st.download_button(
                            label=f"⬇️ ડાઉનલોડ કરો: {os.path.basename(out_file)} ✅",
                            data=file_data,
                            file_name=os.path.basename(out_file),
                            mime=mime_type,
                            key=f"dl_{idx}"
                        )
                    os.remove(out_file)

        clip.close()

    except Exception as e:
        st.error(f"{t['error']} {str(e)}")

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
