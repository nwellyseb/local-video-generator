# Local Video Generator

Turns a text prompt into a short "fact/story" video — title card, simple
flat-shape scenes (stick figure, tree, laptop, etc.), synced captions, and
narration — entirely offline, no API keys.

Pipeline: **Ollama** (script) → **Piper** (narration) → **faster-whisper**
(caption timing) → **Pillow** (frames) → **MoviePy/ffmpeg** (final mp4).

## 1. Install system dependencies

```bash
# ffmpeg (required by moviepy)
sudo apt install ffmpeg        # Debian/Ubuntu
brew install ffmpeg            # macOS

# Ollama (local LLM) - https://ollama.com
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1           # or any model you prefer, update config.py to match
ollama serve                   # leave running in a terminal (or it runs as a service)
```

## 2. Install Python dependencies

```bash
cd video_gen
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## 3. Get a Piper voice

Download a voice model (`.onnx` + `.onnx.json`) from the
[Piper releases page](https://github.com/rhasspy/piper/releases) or
[Hugging Face piper-voices repo](https://huggingface.co/rhasspy/piper-voices),
e.g. `en_US-lessac-medium`. Put both files in `~/piper_voices/` (or wherever
you like) and update `PIPER_MODEL_PATH` in `video_gen/config.py`.

Also make sure the `piper` binary is on your PATH (it's installed by
`pip install piper-tts`, or grab a standalone binary from the same releases
page).

## 4. Point to a bold TTF font

`config.py` defaults to DejaVuSans-Bold, common on Linux. If it's missing,
either `sudo apt install fonts-dejavu` or point `FONT_TITLE`/`FONT_CAPTION`
at any bold `.ttf` you have.

## 5. Generate a video

```bash
python -m video_gen "the hidden effects of learning chess" --beats 6
```

Output lands in `~/video_gen_output/output.mp4`. Intermediate per-beat
audio/frames are in `~/video_gen_work/` (wiped and rebuilt each run).

## Tuning

- `config.py` — colors, canvas size, font sizes, caption chunk length, which
  Ollama/Whisper model to use.
- `visuals.py` — `SCENE_DRAWERS` dict maps scene keywords to drawing
  functions. Add your own (e.g. `draw_rocket`, `draw_house`) and add the
  keyword to `script_gen.SCENE_VOCAB` so the LLM can pick it.
- First run of faster-whisper downloads model weights once (needs internet
  that one time); after that it's fully cached and offline.

## Known limitations / next steps

- Per-beat video duration is derived from Whisper's word timestamps, which
  can drift slightly from the raw TTS audio length on very short beats —
  the final video duration is snapped to match total audio, but a beat's
  visuals could occasionally be a few hundred ms off from its audio.
- Scene selection is a single keyword per beat (no multi-object scenes or
  transitions/animation within a beat — icons are static, matching the
  reference style, not animated).
- No background music track — easy to add via `moviepy`'s
  `CompositeAudioClip` if you want it.
