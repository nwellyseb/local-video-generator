"""
Runs the full pipeline: prompt -> script -> per-beat TTS -> caption timing
-> rendered frames -> final mp4 (via moviepy, which shells out to ffmpeg).
"""
import shutil
from pathlib import Path

import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, concatenate_audioclips

from . import config, script_gen, tts, captions, visuals


def build_video(prompt: str, out_name: str = "output.mp4", num_beats: int = 6) -> Path:
    if config.WORKDIR.exists():
        shutil.rmtree(config.WORKDIR)
    config.WORKDIR.mkdir(parents=True)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/4] Generating script...")
    script = script_gen.generate_script(prompt, num_beats=num_beats)
    title = script["title"]
    beats = script["beats"]
    print(f"  Title: {title}  ({len(beats)} beats)")

    video_clips = []
    audio_clips = []

    for i, beat in enumerate(beats):
        print(f"[2/4] Beat {i+1}/{len(beats)}: synthesizing narration...")
        wav_path = config.WORKDIR / f"beat_{i:02d}.wav"
        duration = tts.synthesize(beat["narration"], wav_path)

        print(f"[3/4] Beat {i+1}/{len(beats)}: aligning captions...")
        chunks = captions.get_caption_chunks(wav_path, beat["caption"], duration)
        if not chunks:
            chunks = [captions.CaptionChunk(beat["caption"], 0.0, duration)]

        show_title = (i == 0)  # title bar only on the very first beat, like the reference
        for chunk in chunks:
            frame = visuals.render_frame(title, chunk.text, beat["scene"], show_title)
            frame_arr = np.array(frame)
            clip_dur = max(0.3, chunk.end - chunk.start)
            video_clips.append(ImageClip(frame_arr).set_duration(clip_dur))

        audio_clips.append(AudioFileClip(str(wav_path)))

    print("[4/4] Assembling final video...")
    final_video = concatenate_videoclips(video_clips, method="compose")
    final_audio = concatenate_audioclips(audio_clips)
    final_video = final_video.set_audio(final_audio).set_duration(final_audio.duration)
    final_video = final_video.set_fps(config.FPS)

    out_path = config.OUTPUT_DIR / out_name
    final_video.write_videofile(
        str(out_path), fps=config.FPS, codec="libx264", audio_codec="aac",
        preset="medium", threads=4,
    )
    return out_path
