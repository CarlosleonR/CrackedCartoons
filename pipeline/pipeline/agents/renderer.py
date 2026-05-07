"""Wrapper around `npx remotion render`.

The Remotion project lives in shorts-series/ (one level above this pipeline/).
This wrapper just shells out — no Node/JS state in Python.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


REMOTION_PROJECT = Path(__file__).resolve().parents[3]  # shorts-series/


@dataclass
class RenderResult:
    composition_id: str
    output_path: Path
    duration_seconds: Optional[float]
    stderr_tail: str


class Renderer:
    def __init__(self, project_dir: Path = REMOTION_PROJECT) -> None:
        if not (project_dir / "remotion.config.ts").exists():
            raise RuntimeError(
                f"Not a Remotion project: {project_dir} (no remotion.config.ts)"
            )
        if shutil.which("npx") is None:
            raise RuntimeError("`npx` not on PATH. Install Node.")
        self.project_dir = project_dir

    def render(
        self,
        *,
        composition_id: str,
        out_path: Path,
        props: Optional[Dict[str, Any]] = None,
        scale: Optional[float] = None,
        overwrite: bool = True,
        log_stream: bool = True,
    ) -> RenderResult:
        out_path = out_path.resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = ["npx", "remotion", "render", composition_id, str(out_path)]
        if props:
            cmd += ["--props", json.dumps(props)]
        if scale is not None:
            cmd += [f"--scale={scale}"]
        if overwrite:
            cmd += ["--overwrite"]

        proc = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "")[-2000:]
            raise RuntimeError(
                f"remotion render failed (exit {proc.returncode}):\n{tail}"
            )

        return RenderResult(
            composition_id=composition_id,
            output_path=out_path,
            duration_seconds=None,
            stderr_tail=(proc.stderr or "")[-500:],
        )

    def render_still(
        self,
        *,
        composition_id: str,
        out_path: Path,
        frame: int = 0,
        props: Optional[Dict[str, Any]] = None,
        scale: Optional[float] = None,
    ) -> Path:
        out_path = out_path.resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "npx", "remotion", "still", composition_id, str(out_path),
            f"--frame={frame}",
        ]
        if props:
            cmd += ["--props", json.dumps(props)]
        if scale is not None:
            cmd += [f"--scale={scale}"]

        proc = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "")[-2000:]
            raise RuntimeError(
                f"remotion still failed (exit {proc.returncode}):\n{tail}"
            )
        return out_path
