import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { Sandwich, SandwichVariant } from "../scene/Sandwich";
import { SpeechBubble } from "../scene/SpeechBubble";
import { renderBackground } from "./registry";
import { easeOut, lipFlap } from "./SceneTimingHelpers";
import type { DialogueLine } from "./types";

type Props = {
  subject?: string;
  subject_variant?: string;
  score?: string;
  hero_shot_text?: string;
  setting?: string;
};

const VARIANT_KEYS: Record<string, SandwichVariant> = {
  classic: "classic",
  tall: "tall",
  weird: "weird",
};

export const RatingBeatScene: React.FC<{
  props: Props;
  duration: number;
  voiceover: DialogueLine[];
  sceneStartFrame: number;
}> = ({ props, voiceover, sceneStartFrame }) => {
  const frame = useCurrentFrame();
  const variant = VARIANT_KEYS[props.subject_variant ?? "classic"] ?? "classic";
  const score = props.score ?? "0/10";

  const sandwichScale = interpolate(frame, [0, 14, 22], [0.4, 2.6, 2.4], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const sandwichY = interpolate(frame, [0, 14], [1200, 720], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const shake = Math.sin(frame * 0.9) * (frame > 30 && frame < 60 ? 8 : 0);

  // Pull the active line (if any) from voiceover relevant to this scene.
  const absFrame = sceneStartFrame + frame;
  const activeLine = voiceover.find(
    (l) => absFrame >= l.start_frame && absFrame < l.start_frame + l.estimated_duration_frames
  );

  const bubbleIn = interpolate(frame, [18, 30], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const bubbleOut = interpolate(frame, [78, 88], [1, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const bubbleScale = bubbleIn * bubbleOut;

  const scoreIn = interpolate(frame, [56, 68, 80], [0, 1.25, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const scoreOut = interpolate(frame, [82, 90], [1, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const mouthOpen = lipFlap(frame, 0.7);
  const rockBob = Math.sin(frame * 0.25) * 8;
  const bubbleText = activeLine?.on_screen_text ?? activeLine?.text ?? "";

  return (
    <AbsoluteFill>
      {renderBackground(props.setting ?? "picnic")}

      <div style={{ transform: `translate(${shake}px, 0)` }}>
        <Sandwich variant={variant} x={540 - 200} y={sandwichY} scale={sandwichScale} />
      </div>

      <TheRock
        x={120}
        y={1280 + rockBob}
        scale={2.4}
        browAngle={26}
        mouthCurve={-0.5}
        mouthOpen={frame > 18 && frame < 80 ? mouthOpen : 0.05}
        pupilX={0.5}
        pupilY={-0.3}
      />

      {bubbleText && (
        <div style={{ transform: `scale(${bubbleScale})`, transformOrigin: "left top" }}>
          <SpeechBubble
            text={bubbleText}
            x={360}
            y={1180}
            width={620}
            tailDirection="left"
            fontSize={52}
          />
        </div>
      )}

      <div
        style={{
          position: "absolute",
          left: 0, right: 0, top: 320,
          textAlign: "center",
          opacity: scoreOut,
          transform: `scale(${scoreIn})`,
          fontFamily: "ui-rounded, system-ui, sans-serif",
          fontSize: 180, fontWeight: 900, color: "#d94a3a",
          letterSpacing: -6, textShadow: "10px 10px 0 #1a1a1e",
        }}
      >
        {score}
      </div>
    </AbsoluteFill>
  );
};
