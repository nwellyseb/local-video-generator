"""
Gets word-level timestamps from a generated narration WAV using
faster-whisper (fully local, runs on CPU), then groups words into
short caption chunks for on-screen display.

Install: pip install faster-whisper
(first run downloads the whisper model weights once, then it's cached
 locally and works offline after that)
"""
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel

from . import config

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type="int8",
        )
    return _model


@dataclass
class CaptionChunk:
    text: str
    start: float
    end: float


def get_caption_chunks(wav_path: Path, fallback_text: str, fallback_duration: float) -> list[CaptionChunk]:
    """
    Transcribe wav_path and return a list of CaptionChunk with real timestamps.
    Falls back to evenly-spaced chunks of `fallback_text` if whisper produces
    nothing usable (e.g. very short clips).
    """
    model = _get_model()
    segments, _info = model.transcribe(str(wav_path), word_timestamps=True)

    words = []
    for seg in segments:
        if seg.words:
            words.extend(seg.words)

    if not words:
        return _even_fallback(fallback_text, fallback_duration)

    chunks = []
    buf, buf_start = [], None
    for w in words:
        if buf_start is None:
            buf_start = w.start
        buf.append(w.word.strip())
        if len(buf) >= config.MAX_WORDS_PER_CAPTION:
            chunks.append(CaptionChunk(" ".join(buf).strip(), buf_start, w.end))
            buf, buf_start = [], None
    if buf:
        chunks.append(CaptionChunk(" ".join(buf).strip(), buf_start, words[-1].end))
    return chunks


def _even_fallback(text: str, duration: float) -> list[CaptionChunk]:
    words = text.split()
    if not words:
        return [CaptionChunk("", 0.0, duration)]
    n_chunks = max(1, len(words) // config.MAX_WORDS_PER_CAPTION + 1)
    per = duration / n_chunks
    chunks = []
    for i in range(n_chunks):
        w = words[i * config.MAX_WORDS_PER_CAPTION:(i + 1) * config.MAX_WORDS_PER_CAPTION]
        if not w:
            continue
        chunks.append(CaptionChunk(" ".join(w), i * per, (i + 1) * per))
    return chunks
