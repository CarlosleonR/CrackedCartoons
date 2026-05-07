import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { Child } from "../characters/Child";
import { Sandwich } from "../scene/Sandwich";
import { PicnicBackground } from "../scene/PicnicBackground";
import type { Emotion } from "./types";

type Props = {
  character?: "rock" | "kid";
  expression?: Emotion;
  dots?: number;
};

const EXPRESSION_TO_FACE: Record<Emotion, { brow: number; curve: number; pupilTwitch: boolean }> = {
  smug:      { brow: 8,  curve: 0.2,  pupilTwitch: false },
  angry:     { brow: 28, curve: -0.7, pupilTwitch: false },
  indignant: { brow: 22, curve: -0.5, pupilTwitch: false },
  confused: { brow: -4, curve: -0.1, pupilTwitch: true  },
  deadpan:   { brow: 0,  curve: 0,    pupilTwitch: false },
  shocked:   { brow: -8, curve: 0,    pupilTwitch: true  },
  excited:   { brow: -2, curve: 0.5,  pupilTwitch: false },
  sad:       { brow: -12, curve: -0.3, pupilTwitch: false },
  hostile:   { brow: 30, curve: -0.8, pupilTwitch: false },
};

export const ReactionBeatScene: React.FC<{ props: Props; duration: number }> = ({ props, duration }) => {
  const frame = useCurrentFrame();
  const expr = EXPRESSION_TO_FACE[props.expression ?? "shocked"];
  const dotCount = Math.min(props.dots ?? 3, Math.floor(frame / 14));
  const twitch = expr.pupilTwitch ? Math.sin(frame * 0.6) * 0.4 : 0;
  const fadeIn = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const character = props.character ?? "rock";

  return (
    <AbsoluteFill style={{ opacity: fadeIn }}>
      <PicnicBackground />
      <Sandwich variant="classic" x={420} y={1500} scale={1.0} rotate={-2} />

      {character === "rock" ? (
        <TheRock
          x={80}
          y={1180}
          scale={2.4}
          browAngle={expr.brow}
          mouthCurve={expr.curve}
          mouthOpen={0}
          pupilX={twitch}
          pupilY={0.4}
        />
      ) : (
        <Child x={620} y={970} scale={1.6} mouthOpen={0} browAngle={expr.brow} armUp={0} />
      )}

      {dotCount > 0 && (
        <div
          style={{
            position: "absolute",
            left: character === "rock" ? 200 : 720,
            top: 1090,
            fontFamily: "ui-rounded, system-ui, sans-serif",
            fontSize: 96, fontWeight: 900, color: "#1a1a1e", letterSpacing: 8,
          }}
        >
          {".".repeat(dotCount)}
        </div>
      )}
    </AbsoluteFill>
  );
};
