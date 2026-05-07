# Cracked Cartoons

Automated YouTube Shorts pipeline. The character is **The Rock** — a literal rock with a face who has confidently wrong opinions about things he has no business having opinions about.

## Layout

```
shorts-series/
├── src/                      Remotion (React/TypeScript) — animation
│   ├── characters/           SVG characters (TheRock, Child)
│   ├── scene/                Scene props (Sandwich, PicnicBackground, SpeechBubble)
│   ├── scenes/               Reusable scene renderers per SceneType
│   └── episodes/             EpisodeFromScript (generic) + Episode01 + thumbnails
├── public/
│   ├── scripts/              EpisodeScript JSONs consumed by EpisodeFromScript
│   ├── thumbnails/           ThumbnailSpec JSONs consumed by ThumbnailFromScript
│   ├── audio/                Generated TTS clips (per episode)
│   └── sfx/                  Generated sound-effect clips
├── pipeline/                 Python — the 6-agent automation pipeline
│   ├── pipeline/agents/      idea_scout, writer, production, quality_check,
│   │                         publisher, analyst (+ supporting clients)
│   ├── pipeline/schemas/     Pydantic schemas (Concept, EpisodeScript,
│   │                         PublishMetadata, ThumbnailSpec, IdeaBatch,
│   │                         AnalystOutput, QualityReport, ...)
│   ├── pipeline/prompts/     Stable system prompts (cached via Anthropic
│   │                         prompt caching)
│   ├── examples/             Example concepts
│   └── tests/                Offline tests (no API spend)
└── README.md
```

## The 6-agent pipeline

| # | Agent | Role |
|---|-------|------|
| 1 | Idea Scout | Reddit + manual seeds → Claude → top 3 episode concepts |
| 2 | Writer | Concept + accumulated KnowledgeNotes → structured EpisodeScript |
| 3 | Production | EpisodeScript → ElevenLabs TTS + SFX → `npx remotion render` → MP4 |
| 4 | Quality Check | Deterministic gate: duration drift, audio file integrity, optional frame sampling |
| 5 | Publisher | Claude → title/description/tags + ThumbnailSpec → render thumbnail → upload via YouTube Data API v3, optionally scheduled (next Thu/Fri/Sat/Sun 14:00 local) |
| 6 | Analyst | YouTube metrics + comments → EpisodeReport → durable KnowledgeNotes that flow back into Agent 2 |

## Running locally

See [pipeline/README.md](pipeline/README.md) for setup and per-agent CLIs.

```bash
cd pipeline
source .venv/bin/activate
python -m pipeline.agents.writer     examples/concept_episode02.json out/ep02-script.json
python -m pipeline.agents.production out/ep02-script.json --scale=0.5
python -m pipeline.agents.publisher  out/ep02-script.json --qc --schedule --upload
```

Built on top of [Remotion](https://www.remotion.dev/), [ElevenLabs](https://elevenlabs.io/), and the [Anthropic Claude API](https://docs.anthropic.com/).
