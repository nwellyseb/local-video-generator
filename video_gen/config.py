"""
Central config. Tweak paths/models here.
"""
from pathlib import Path

# --- Video canvas ---
WIDTH = 1080
HEIGHT = 1920
FPS = 30

# --- Colors (RGB) ---
COLOR_BG = (169, 167, 163)          # gray body background
COLOR_TITLE_BG = (10, 10, 10)       # black title bar
COLOR_TITLE_TEXT = (222, 222, 222)  # off-white title text
COLOR_CAPTION_BG = (15, 15, 15)     # black caption box
COLOR_CAPTION_TEXT = (255, 255, 255)
COLOR_GROUND = (130, 128, 124)      # ground line strip
COLOR_FIGURE = (30, 30, 30)         # stick figure lines
COLOR_SKIN = (196, 184, 168)

TITLE_BAR_HEIGHT = 230
GROUND_Y = HEIGHT - 420             # where the "floor" sits
CAPTION_BOX_MARGIN = 40
CAPTION_BOX_HEIGHT = 220

# --- Fonts ---
# Point these at TTF files you have locally. DejaVuSans-Bold ships with
# most Linux systems / matplotlib installs. Swap for any bold TTF you like.
FONT_TITLE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_CAPTION = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TITLE_FONT_SIZE = 58
CAPTION_FONT_SIZE = 44

# --- Ollama (local LLM for script generation) ---
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1"  # change to whatever model you've pulled

# --- Piper (local TTS) ---
# Download a voice from https://github.com/rhasspy/piper/releases (a .onnx + .onnx.json pair)
PIPER_MODEL_PATH = "/Users/nwell/Downloads/video_gen/en_US-lessac-medium.onnx"
PIPER_BIN = "piper"  # assumes `piper` is on PATH; point to full path otherwise

# --- faster-whisper (local caption timing) ---
WHISPER_MODEL_SIZE = "base.en"  # tiny.en/base.en/small.en - bigger = more accurate, slower
WHISPER_DEVICE = "cpu"          # set to "cuda" if you have a GPU + CUDA toolkit

# --- Output ---
WORKDIR = Path.home() / "video_gen_work"
OUTPUT_DIR = Path.home() / "video_gen_output"

# --- Caption chunking ---
MAX_WORDS_PER_CAPTION = 8
