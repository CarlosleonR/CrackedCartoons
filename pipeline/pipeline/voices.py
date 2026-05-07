"""ElevenLabs voice and model config.

Override any of these with environment variables in pipeline/.env to swap
voices without code changes.
"""
from __future__ import annotations
import os
from typing import Dict

from pipeline.schemas import Speaker


# Custom (paid-plan-friendly) voices in your account. Default to your
# "ROCK" voice and to Jessica for the kid (since the public-library
# "Grimey" voice requires a paid ElevenLabs subscription).
_DEFAULTS = {
    Speaker.rock:     "0MSJor2XYiJo1Dad2OYK",   # ROCK (custom)
    Speaker.kid:      "cgSgspJ2msm6clMCkdW9",   # Jessica (default voice)
    Speaker.narrator: "nPczCjzI2devNBz1zQrb",   # Brian (default voice)
    Speaker.other:    "nPczCjzI2devNBz1zQrb",   # Brian fallback
}

_ENV_KEY = {
    Speaker.rock:     "ELEVENLABS_VOICE_ROCK",
    Speaker.kid:      "ELEVENLABS_VOICE_KID",
    Speaker.narrator: "ELEVENLABS_VOICE_NARRATOR",
    Speaker.other:    "ELEVENLABS_VOICE_OTHER",
}


def voice_id(speaker: Speaker) -> str:
    return os.environ.get(_ENV_KEY[speaker], _DEFAULTS[speaker])


def all_voices() -> Dict[Speaker, str]:
    return {s: voice_id(s) for s in Speaker}


# Per-speaker voice settings tuning. The Rock benefits from lower stability
# (more emotional range) and higher style (exaggeration); narrator is steadier.
VOICE_SETTINGS = {
    Speaker.rock:     {"stability": 0.32, "similarity_boost": 0.78, "style": 0.7,  "use_speaker_boost": True},
    Speaker.kid:      {"stability": 0.30, "similarity_boost": 0.78, "style": 0.75, "use_speaker_boost": True},
    Speaker.narrator: {"stability": 0.55, "similarity_boost": 0.78, "style": 0.3,  "use_speaker_boost": True},
    Speaker.other:    {"stability": 0.45, "similarity_boost": 0.78, "style": 0.4,  "use_speaker_boost": True},
}

TTS_MODEL = "eleven_multilingual_v2"
