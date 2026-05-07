"""Agent 3 — Production.

Pipeline:
  EpisodeScript JSON
    -> ElevenLabs TTS for every voiceover line
    -> ElevenLabs SFX for every unique cue (deduped via reuse_key)
    -> writes the script + audio paths into shorts-series/public/scripts/
    -> calls `npx remotion render Episode --props='{"scriptId":"..."}'`
    -> returns the path to the rendered MP4.

The generic Remotion composition `Episode` (see src/episodes/EpisodeFromScript.tsx)
fetches the script JSON and renders all scenes + audio cues.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

from pipeline.agents.elevenlabs_client import ElevenLabsClient
from pipeline.agents.renderer import REMOTION_PROJECT, Renderer
from pipeline.schemas import DialogueLine, EpisodeScript, SFXCue, Speaker
from pipeline.voices import TTS_MODEL, VOICE_SETTINGS, voice_id


@dataclass
class ProductionResult:
    script: EpisodeScript
    rendered_mp4: Path
    voiceover_files: Dict[str, Path]  # line key -> mp3 path
    sfx_files: Dict[str, Path]        # cue key -> mp3 path
    script_json_path: Path


def _slug(text: str, max_len: int = 28) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return text[:max_len] or "x"


def _line_basename(line: DialogueLine, idx: int) -> str:
    return f"{idx:02d}_{line.speaker.value}_{_slug(line.text)}.mp3"


def _sfx_basename(cue: SFXCue, idx: int) -> str:
    if cue.reuse_key:
        return f"{cue.reuse_key}.mp3"
    h = hashlib.sha1(cue.description.encode()).hexdigest()[:8]
    return f"{idx:02d}_{_slug(cue.description)}_{h}.mp3"


@dataclass
class ProductionAgent:
    """Stateful only over file paths; the heavy work happens in components."""

    public_dir: Path = field(default_factory=lambda: REMOTION_PROJECT / "public")
    out_dir: Path = field(default_factory=lambda: REMOTION_PROJECT / "out")
    scripts_subdir: str = "scripts"
    audio_subdir: str = "audio"
    sfx_subdir: str = "sfx"
    elevenlabs: Optional[ElevenLabsClient] = None
    renderer: Optional[Renderer] = None

    def __post_init__(self) -> None:
        self.elevenlabs = self.elevenlabs or ElevenLabsClient()
        self.renderer = self.renderer or Renderer()

    # ---------- public API ---------- #

    def produce(
        self,
        script: EpisodeScript,
        *,
        render_scale: Optional[float] = None,
        skip_render: bool = False,
    ) -> ProductionResult:
        episode_id = script.episode_id

        vo_files = self._synthesize_voiceover(script, episode_id)
        sfx_files = self._synthesize_sfx(script, episode_id)
        script_json_path = self._write_script_json(script, vo_files, sfx_files)

        mp4_path = self.out_dir / f"{episode_id}.mp4"
        if skip_render:
            return ProductionResult(
                script=script,
                rendered_mp4=mp4_path,  # not actually written
                voiceover_files=vo_files,
                sfx_files=sfx_files,
                script_json_path=script_json_path,
            )

        self.renderer.render(  # type: ignore[union-attr]
            composition_id="Episode",
            out_path=mp4_path,
            props={"scriptId": episode_id},
            scale=render_scale,
        )
        return ProductionResult(
            script=script,
            rendered_mp4=mp4_path,
            voiceover_files=vo_files,
            sfx_files=sfx_files,
            script_json_path=script_json_path,
        )

    # ---------- audio synthesis ---------- #

    def _synthesize_voiceover(
        self, script: EpisodeScript, episode_id: str
    ) -> Dict[str, Path]:
        out = {}
        ep_dir = self.public_dir / self.audio_subdir / episode_id
        for i, line in enumerate(script.voiceover):
            key = self._line_key(i, line)
            target = ep_dir / _line_basename(line, i)
            self.elevenlabs.synthesize_speech(  # type: ignore[union-attr]
                text=line.text,
                voice_id=voice_id(line.speaker),
                voice_settings=VOICE_SETTINGS[line.speaker],
                model_id=TTS_MODEL,
                out_path=target,
            )
            out[key] = target
        return out

    def _synthesize_sfx(
        self, script: EpisodeScript, episode_id: str
    ) -> Dict[str, Path]:
        out = {}
        ep_dir = self.public_dir / self.sfx_subdir / episode_id
        # Dedup by reuse_key. If absent, every cue is unique.
        seen_files: Dict[str, Path] = {}
        for i, cue in enumerate(script.sfx):
            basename = _sfx_basename(cue, i)
            target = ep_dir / basename
            cache_key = cue.reuse_key or f"_{i}"
            if cache_key in seen_files:
                target = seen_files[cache_key]
            else:
                self.elevenlabs.synthesize_sfx(  # type: ignore[union-attr]
                    description=cue.description,
                    duration_seconds=cue.duration_seconds,
                    out_path=target,
                )
                seen_files[cache_key] = target
            out[self._cue_key(i, cue)] = target
        return out

    # ---------- script.json for the generic composition ---------- #

    def _write_script_json(
        self,
        script: EpisodeScript,
        vo_files: Dict[str, Path],
        sfx_files: Dict[str, Path],
    ) -> Path:
        public_root = self.public_dir
        scripts_dir = public_root / self.scripts_subdir
        scripts_dir.mkdir(parents=True, exist_ok=True)

        # Build a render-ready payload: same shape as EpisodeScript, plus
        # `audio_src` fields on each line/cue pointing at the staticFile path.
        payload = script.model_dump(mode="json")
        for i, (line, line_data) in enumerate(zip(script.voiceover, payload["voiceover"])):
            key = self._line_key(i, line)
            line_data["audio_src"] = self._public_relpath(vo_files[key])
        for i, (cue, cue_data) in enumerate(zip(script.sfx, payload["sfx"])):
            key = self._cue_key(i, cue)
            cue_data["audio_src"] = self._public_relpath(sfx_files[key])

        out_path = scripts_dir / f"{script.episode_id}.json"
        out_path.write_text(json.dumps(payload, indent=2))
        return out_path

    # ---------- helpers ---------- #

    def _public_relpath(self, p: Path) -> str:
        """staticFile() arguments are relative to public/. Return that suffix."""
        return str(p.resolve().relative_to(self.public_dir.resolve()))

    @staticmethod
    def _line_key(idx: int, line: DialogueLine) -> str:
        return f"vo:{idx}:{line.scene_id}:{line.start_frame}"

    @staticmethod
    def _cue_key(idx: int, cue: SFXCue) -> str:
        return f"sfx:{idx}:{cue.scene_id}:{cue.start_frame}"


# ---------- CLI ---------- #

def main() -> None:
    """Usage: python -m pipeline.agents.production <script.json> [--skip-render] [--scale=0.5]"""
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)

    args = sys.argv[1:]
    if not args:
        print(
            "usage: python -m pipeline.agents.production <script.json> "
            "[--skip-render] [--scale=N]",
            file=sys.stderr,
        )
        sys.exit(2)

    script_path = Path(args[0])
    skip_render = "--skip-render" in args
    scale: Optional[float] = None
    for a in args:
        if a.startswith("--scale="):
            scale = float(a.split("=", 1)[1])

    script = EpisodeScript.model_validate_json(script_path.read_text())
    agent = ProductionAgent()
    result = agent.produce(script, render_scale=scale, skip_render=skip_render)

    print(json.dumps({
        "episode_id": result.script.episode_id,
        "script_json": str(result.script_json_path),
        "rendered_mp4": str(result.rendered_mp4) if not skip_render else None,
        "voiceover_count": len(result.voiceover_files),
        "sfx_count": len(set(result.sfx_files.values())),
    }, indent=2))


if __name__ == "__main__":
    main()
