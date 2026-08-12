"""
Local, offline TTS via Piper (https://github.com/rhasspy/piper).

Piper is a small, fast neural TTS that runs entirely on CPU with no
network calls. Install with `pip install piper-tts` and download a
voice (.onnx + .onnx.json) from the piper releases page, then set
PIPER_MODEL_PATH in config.py.
"""
import subprocess
import wave
from pathlib import Path

from . import config


def synthesize(text: str, out_wav: Path) -> float:
    """
    Render `text` to `out_wav` using the piper CLI. Returns duration in seconds.
    """
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        config.PIPER_BIN,
        "--model", config.PIPER_MODEL_PATH,
        "--output_file", str(out_wav),
    ]
    proc = subprocess.run(
        cmd, input=text.encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"piper failed (code {proc.returncode}):\n{proc.stderr.decode(errors='ignore')}"
        )

    with wave.open(str(out_wav), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    return duration


if __name__ == "__main__":
    import sys
    dur = synthesize(" ".join(sys.argv[1:]) or "This is a test.", Path("/tmp/test.wav"))
    print(f"Wrote /tmp/test.wav, duration={dur:.2f}s")
