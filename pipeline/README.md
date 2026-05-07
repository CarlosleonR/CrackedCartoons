# Cracked Cartoons — Pipeline

Multi-agent system that automates the YouTube Shorts series end-to-end.

## Status

| # | Agent | Status |
|---|-------|--------|
| 1 | Idea Scout | **built** |
| 2 | Writer | **built** (reads from KnowledgeBase) |
| 3 | Production | **built** |
| 4 | Quality Check | **built** |
| 5 | Publisher | **built** (with scheduler) |
| 6 | Analyst | **built** (writes to KnowledgeBase) |

## Setup

```bash
cd pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # then fill in ANTHROPIC_API_KEY
```

## Agent 2 — Writer

Takes a `Concept` (premise / conflict / punchline) and emits an `EpisodeScript`
JSON whose scene types map 1:1 to Remotion components in
`shorts-series/src/episodes/`.

### Run

```bash
# stdout
python -m pipeline.agents.writer examples/concept_episode02.json

# write to file
python -m pipeline.agents.writer examples/concept_episode02.json out/ep02.json
```

### Architecture

- **Structured output via tool use**, not regex. The `submit_episode_script`
  tool's `input_schema` is the JSON schema of `EpisodeScript`, and
  `tool_choice` forces the model to call it. Pydantic re-validates after
  the call — including timing constraints (scene durations sum to total_frames,
  audio cues reference real scene ids).

- **Prompt caching**. The system prompt (~3KB) and the tool definition
  (~5KB JSON schema) are marked `cache_control: ephemeral`. Only the user
  message (the concept, ≤500 tokens) varies per episode. Expect cache reads
  on the second call onward; observe via `cache_read_input_tokens` in the
  `[writer]` log line.

- **Pure function**. `WriterAgent.write(concept) -> WriterResult` has no
  side effects. CrewAI orchestration can wrap it as a `Tool` later.

### Schema

See [`schemas/script.py`](schemas/script.py). Key constraints enforced:

- `episode_id` matches `^Ep\d{2,3}-[A-Za-z0-9-]+$`.
- Scenes are contiguous: `start_frame` of scene N+1 == `start_frame + duration_frames` of scene N.
- Sum of scene durations == `total_frames`.
- Every voiceover/SFX cue references an existing `scene_id` and starts before `total_frames`.

### Tests

```bash
pytest tests/
```

All 14 tests run offline (no API). They guard schema regressions, catch the
most common LLM failure modes (off-by-one timing, dangling refs), and verify
SFX dedup and audio file layout in the production agent.

## Agent 3 — Production

Takes the `EpisodeScript` JSON and produces a rendered MP4. Pipeline:

1. ElevenLabs TTS for every voiceover line (`pipeline/voices.py` maps speaker → voice ID; override via env vars).
2. ElevenLabs SFX for every cue, deduped by `reuse_key` so e.g. three rating beats share one `stamp_ding.mp3`.
3. Writes `public/scripts/<episode_id>.json` with `audio_src` populated on each line/cue.
4. `npx remotion render Episode --props='{"scriptId":"..."}'` — the generic `Episode` composition (in `src/episodes/EpisodeFromScript.tsx`) reads the script and dispatches scenes via the registry in `src/scenes/`.

### Run

```bash
# end-to-end, requires ELEVENLABS_API_KEY in .env
python -m pipeline.agents.production /path/to/script.json

# audio + script.json only, skip the render
python -m pipeline.agents.production /path/to/script.json --skip-render

# fast preview render
python -m pipeline.agents.production /path/to/script.json --scale=0.5
```

### Architecture choice: generic composition, not codegen

Each new episode is a script JSON + audio assets, not a new `.tsx` file.
This avoids hand-written codegen and keeps the React surface stable. Adding
a new scene type means adding a component in `src/scenes/` and registering
it in `src/episodes/EpisodeFromScript.tsx`'s `SCENE_REGISTRY`.
