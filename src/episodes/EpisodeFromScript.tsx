/**
 * Generic episode renderer. Reads `EpisodeScript` JSON from public/scripts/<id>.json
 * (resolved by `calculateMetadata` in Root.tsx) and dispatches each scene to its
 * corresponding component in src/scenes/. Audio cues are mounted at the top
 * level using their absolute frame numbers.
 *
 * Adding a new SceneType:
 *   1. Add the type to src/scenes/types.ts and pipeline/schemas/script.py.
 *   2. Build a new component in src/scenes/ that takes
 *        ({ props, duration, voiceover?, sceneStartFrame? })
 *   3. Register it in SCENE_REGISTRY below.
 */
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";

import type {
  EpisodeScriptJSON,
  Scene,
  DialogueLine,
  SceneType,
} from "../scenes/types";
import { TitleCardScene } from "../scenes/TitleCardScene";
import { CharacterEntranceScene } from "../scenes/CharacterEntranceScene";
import { RatingBeatScene } from "../scenes/RatingBeatScene";
import { DialogueExchangeScene } from "../scenes/DialogueExchangeScene";
import { ReactionBeatScene } from "../scenes/ReactionBeatScene";
import { OutroScene } from "../scenes/OutroScene";
import { MontageScene } from "../scenes/MontageScene";
import { VisualBeatScene } from "../scenes/VisualBeatScene";
import { SlideDeckScene } from "../scenes/SlideDeckScene";

const SCENE_REGISTRY: Record<SceneType, React.FC<any>> = {
  title_card:        TitleCardScene,
  character_entrance: CharacterEntranceScene,
  rating_beat:       RatingBeatScene,
  dialogue_exchange: DialogueExchangeScene,
  reaction_beat:     ReactionBeatScene,
  outro:             OutroScene,
  montage:           MontageScene,
  visual_beat:       VisualBeatScene,
  slide_deck:        SlideDeckScene,
};

const renderScene = (scene: Scene, voiceover: DialogueLine[]): React.ReactNode => {
  const Component = SCENE_REGISTRY[scene.type];
  if (!Component) {
    return (
      <AbsoluteFill style={{ backgroundColor: "#222", color: "#fff", padding: 40 }}>
        Unknown scene type: {scene.type}
      </AbsoluteFill>
    );
  }
  // Filter voiceover lines that fall inside this scene.
  const sceneVO = voiceover.filter((l) => l.scene_id === scene.id);
  return (
    <Component
      props={scene.props}
      duration={scene.duration_frames}
      voiceover={sceneVO}
      sceneStartFrame={scene.start_frame}
    />
  );
};

export type EpisodeFromScriptProps = {
  script: EpisodeScriptJSON | null;
};

export const EpisodeFromScript: React.FC<EpisodeFromScriptProps> = ({ script }) => {
  if (!script) {
    return (
      <AbsoluteFill style={{ backgroundColor: "#1a1a1e", color: "#f5d35a", padding: 60 }}>
        <div style={{ fontSize: 64, fontFamily: "ui-rounded, system-ui, sans-serif" }}>
          No script loaded.
          <br />
          Render with --props='{`{"scriptId":"Ep01-..."}`}'
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "#9bd6ee" }}>
      {script.scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.start_frame}
          durationInFrames={scene.duration_frames}
          layout="none"
        >
          {renderScene(scene, script.voiceover)}
        </Sequence>
      ))}

      {script.voiceover.map((line, i) =>
        line.audio_src ? (
          <Sequence key={`vo-${i}`} from={line.start_frame} layout="none">
            <Audio src={staticFile(line.audio_src)} volume={1} />
          </Sequence>
        ) : null
      )}

      {script.sfx.map((cue, i) =>
        cue.audio_src ? (
          <Sequence key={`sfx-${i}`} from={cue.start_frame} layout="none">
            <Audio src={staticFile(cue.audio_src)} volume={cue.volume ?? 0.6} />
          </Sequence>
        ) : null
      )}
    </AbsoluteFill>
  );
};
