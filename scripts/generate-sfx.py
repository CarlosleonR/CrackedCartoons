#!/usr/bin/env python3
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
OUT_DIR = ROOT / "public" / "sfx"
OUT_DIR.mkdir(parents=True, exist_ok=True)

api_key = None
for line in ENV_PATH.read_text().splitlines():
    if line.startswith("ELEVENLABS_API_KEY="):
        api_key = line.split("=", 1)[1].strip()
if not api_key:
    sys.exit("Missing ELEVENLABS_API_KEY")

SFX = [
    ("title_impact.mp3",   "cartoon punchy whoosh impact, brassy stinger, short 1 second", 1.0, 0.4),
    ("rock_arrival.mp3",   "heavy boulder rolling on dirt, comedic cartoon rumble, ending in a thud", 2.5, 0.45),
    ("stamp_ding.mp3",     "rubber stamp slam followed by a tiny metallic ding, judge gavel feel", 1.0, 0.5),
    ("record_scratch.mp3", "vinyl record scratch, sudden stop, comedic", 1.0, 0.5),
    ("sad_trombone.mp3",   "classic sad trombone wah-wah-wah-waaah, comedic failure sound", 2.5, 0.55),
    ("kid_gasp.mp3",       "small child gasp, short, surprised", 0.7, 0.4),
]

for filename, text, duration, prompt_influence in SFX:
    out_path = OUT_DIR / filename
    if out_path.exists() and out_path.stat().st_size > 4000:
        print(f"-- skip (exists): {filename}")
        continue
    body = json.dumps({
        "text": text,
        "duration_seconds": duration,
        "prompt_influence": prompt_influence,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/sound-generation",
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        out_path.write_bytes(data)
        print(f">> {filename}  ({len(data)} bytes)")
    except urllib.error.HTTPError as e:
        print(f"!! {filename} FAILED ({e.code}): {e.read()[:300]}")
        sys.exit(1)

print("\nDone.")
for p in sorted(OUT_DIR.glob("*.mp3")):
    print(f"  {p.name}: {p.stat().st_size} bytes")
