#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
OUT_DIR = ROOT / "public" / "audio"
OUT_DIR.mkdir(parents=True, exist_ok=True)

api_key = None
for line in ENV_PATH.read_text().splitlines():
    if line.startswith("ELEVENLABS_API_KEY="):
        api_key = line.split("=", 1)[1].strip()
if not api_key:
    sys.exit("Missing ELEVENLABS_API_KEY")

ROCK = "0MSJor2XYiJo1Dad2OYK"
KID = "cgSgspJ2msm6clMCkdW9"
MODEL = "eleven_multilingual_v2"

LINES = [
    ("rock_aioli.mp3",        ROCK, "No aioli? Disgrace.",            0.32, 0.7),
    ("rock_too_tall.mp3",     ROCK, "Too tall. Unhinged.",            0.32, 0.7),
    ("rock_what_is_this.mp3", ROCK, "What is this? Get it away.",     0.30, 0.75),
    ("kid_my_sandwich.mp3",   KID,  "Hey! That's MY sandwich!",       0.28, 0.8),
    ("rock_bad_taste.mp3",    ROCK, "Then you have bad taste.",       0.35, 0.65),
    ("kid_youre_a_rock.mp3",  KID,  "You're a rock!",                 0.28, 0.8),
    ("rock_connoisseur.mp3",  ROCK, "I am a connoisseur.",            0.4,  0.6),
    ("kid_no_mouths.mp3",     KID,  "Rocks don't have mouths.",       0.45, 0.4),
    ("rock_outro_mutter.mp3", ROCK, "And another thing... warm lettuce. WARM lettuce. The bread-to-filling ratio is criminal. Mayonnaise is a scam.", 0.5, 0.5),
]

for filename, voice, text, stability, style in LINES:
    out_path = OUT_DIR / filename
    if out_path.exists() and out_path.stat().st_size > 4000:
        print(f"-- skip (exists): {filename}")
        continue
    body = json.dumps({
        "text": text,
        "model_id": MODEL,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": 0.78,
            "style": style,
            "use_speaker_boost": True,
        },
    }).encode("utf-8")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        out_path.write_bytes(data)
        print(f">> {filename}  ({len(data)} bytes)")
    except urllib.error.HTTPError as e:
        print(f"!! {filename} FAILED ({e.code}): {e.read()[:300]}")
        sys.exit(1)

print("\nDone.")
for p in sorted(OUT_DIR.glob("*.mp3")):
    print(f"  {p.name}: {p.stat().st_size} bytes")
