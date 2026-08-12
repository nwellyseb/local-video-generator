"""
Turns a user prompt into a structured video script using a local Ollama model.

Output schema:
{
  "title": "THE HIDDEN EFFECTS OF LEARNING CHESS",
  "beats": [
    {"narration": "...", "caption": "...", "scene": ["figure", "tree", "book"]},
    ...
  ]
}

`narration` is what gets spoken by TTS. `caption` is what's shown on screen
(usually the same text, but you can shorten it for readability). `scene` is
a list of keywords picked from a fixed vocabulary the renderer understands
(see visuals.SCENE_DRAWERS) - as many as make sense for that beat (usually
1-4). The renderer lays them all out automatically.
"""
import json
import re
import requests

from . import config

SCENE_VOCAB = [
    "figure", "tree", "laptop", "book", "brain", "clock",
    "heart", "lightbulb", "phone", "chessboard", "money", "generic",
]

MAX_SCENE_ICONS = 5  # sanity ceiling so a scene never gets absurdly crowded

SYSTEM_PROMPT = f"""You write short-form "fact/story" video scripts, 5-8 beats.
Each beat has: narration (one spoken sentence), caption (<=12 words shown
on screen), and scene (a list of keywords from this exact vocabulary:
{", ".join(SCENE_VOCAB)}).

Vary the length of the scene list across beats - do not use the same count
every time. Mix short beats (1 keyword) with fuller ones (3-4 keywords).
Only include keywords that genuinely relate to that beat's sentence. Max
{MAX_SCENE_ICONS} keywords per beat.

Output a single JSON object with this shape, and nothing else:
{{"title": "SHORT UPPERCASE TITLE", "beats": [{{"narration": "...", "caption": "...", "scene": ["keyword1", "keyword2"]}}]}}
"""


def _extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output:\n{text}")
    return json.loads(text[start:end + 1])


def _sanitize_scene(raw) -> list[str]:
    """Normalize whatever the model gave us into a list of valid keywords."""
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return ["generic"]
    cleaned = [s for s in raw if isinstance(s, str) and s in SCENE_VOCAB]
    cleaned = list(dict.fromkeys(cleaned))[:MAX_SCENE_ICONS]  # dedupe, cap
    return cleaned or ["generic"]


def _enforce_count_variation(beats: list[dict]) -> None:
    """
    Safety net: local LLMs often ignore "vary the count" instructions and
    default to the same number every beat. This forces real variation by
    capping each beat's icon count against a rotating target pattern -
    it only trims (never invents irrelevant icons), so beats where the
    model gave more icons than the target get trimmed down, guaranteeing
    the sequence isn't flat.
    """
    target_pattern = [1, 3, 2, 4, 1, 2, 3, 1]
    for i, beat in enumerate(beats):
        target = target_pattern[i % len(target_pattern)]
        if len(beat["scene"]) > target:
            beat["scene"] = beat["scene"][:target]


def generate_script(prompt: str, num_beats: int = 6) -> dict:
    """Call local Ollama, return parsed {title, beats} dict."""
    user_msg = f'Topic: "{prompt}". Write exactly {num_beats} beats.'
    resp = requests.post(
        config.OLLAMA_URL,
        json={
            "model": config.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "stream": False,
            "format": "json",  # forces Ollama to constrain output to valid JSON syntax
            "options": {"temperature": 0.9},
        },
        timeout=180,
    )
    resp.raise_for_status()
    content = resp.json()["message"]["content"]

    try:
        data = _extract_json(content)
    except (ValueError, json.JSONDecodeError) as e:
        raise RuntimeError(
            f"Model did not return parseable JSON even in JSON mode. "
            f"Raw output was:\n{content}"
        ) from e

    # Validate / sanitize
    if "title" not in data or "beats" not in data:
        raise ValueError(f"Malformed script JSON (missing title/beats): {data}")
    for beat in data["beats"]:
        beat["scene"] = _sanitize_scene(beat.get("scene"))
        beat.setdefault("caption", beat.get("narration", "")[:60])
    _enforce_count_variation(data["beats"])
    return data


if __name__ == "__main__":
    import sys
    script = generate_script(" ".join(sys.argv[1:]) or "the hidden effects of learning chess")
    print(json.dumps(script, indent=2))