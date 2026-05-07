"""Thin ElevenLabs client used by Agent 3 (Production).

Handles two endpoints:
- POST /v1/text-to-speech/{voice_id}     (dialogue VO)
- POST /v1/sound-generation              (SFX from text description)

Stays dependency-light (urllib only) so the pipeline doesn't drag in another
HTTP library or async runtime. Calls are sequential by design — for an entire
30-second short this is ~14 calls × 2-4s each, which is acceptable; parallelize
later if cycle time matters.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


class ElevenLabsError(RuntimeError):
    pass


@dataclass
class ElevenLabsClient:
    api_key: Optional[str] = None
    timeout_seconds: int = 120

    def __post_init__(self) -> None:
        if not self.api_key:
            # Treat empty-string env vars as missing.
            self.api_key = os.environ.get("ELEVENLABS_API_KEY") or None
        if not self.api_key:
            raise ElevenLabsError(
                "ELEVENLABS_API_KEY not set. Add it to pipeline/.env or export it."
            )

    # ---------- TTS ---------- #

    def synthesize_speech(
        self,
        *,
        text: str,
        voice_id: str,
        out_path: Path,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: Optional[Dict[str, Any]] = None,
        output_format: str = "mp3_44100_128",
        skip_if_exists: bool = True,
    ) -> Path:
        if skip_if_exists and out_path.exists() and out_path.stat().st_size > 4000:
            return out_path
        body = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings or {
                "stability": 0.4,
                "similarity_boost": 0.78,
                "style": 0.55,
                "use_speaker_boost": True,
            },
        }
        url = f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}?output_format={output_format}"
        data = self._post(url, body)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        return out_path

    # ---------- SFX ---------- #

    def synthesize_sfx(
        self,
        *,
        description: str,
        duration_seconds: float,
        out_path: Path,
        prompt_influence: float = 0.5,
        skip_if_exists: bool = True,
    ) -> Path:
        if skip_if_exists and out_path.exists() and out_path.stat().st_size > 4000:
            return out_path
        # API supports 0.5-22 seconds.
        clamped = max(0.5, min(22.0, duration_seconds))
        body = {
            "text": description,
            "duration_seconds": clamped,
            "prompt_influence": prompt_influence,
        }
        url = f"{ELEVENLABS_BASE}/sound-generation"
        data = self._post(url, body)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        return out_path

    # ---------- internals ---------- #

    def _post(self, url: str, body: Dict[str, Any]) -> bytes:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "xi-api-key": self.api_key or "",
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            detail = e.read()[:500].decode("utf-8", errors="replace")
            raise ElevenLabsError(f"HTTP {e.code} from ElevenLabs: {detail}") from e
        except urllib.error.URLError as e:
            raise ElevenLabsError(f"Network error talking to ElevenLabs: {e}") from e
