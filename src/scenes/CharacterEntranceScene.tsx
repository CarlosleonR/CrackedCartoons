import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { Sandwich, SandwichVariant } from "../scene/Sandwich";
import { renderBackground } from "./registry";
import { easeOut } from "./SceneTimingHelpers";

type Props = {
  character?: string;
  entrance_direction?: "left" | "right" | "top";
  on_screen_label?: string;
  background_props?: string[];
  setting?: string;
};

const SANDWICH_KEYS: Record<string, SandwichVariant> = {
  sandwich_classic: "classic",
  sandwich_tall: "tall",
  sandwich_weird: "weird",
};

export const CharacterEntranceScene: React.FC<{
  props: Props;
  duration: number;
}> = ({ props, duration }) => {
  const frame = useCurrentFrame();
  const dir = props.entrance_direction ?? "right";

  const enterFromX = dir === "right" ? 1400 : dir === "left" ? -400 : 540;
  const enterFromY = dir === "top" ? -400 : 1100;
  const restY = 1100;

  const x = interpolate(frame, [0, 50], [enterFromX, 540], {
    extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut,
  });
  const y = interpolate(frame, [0, 50], [enterFromY, restY], {
    extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut,
  });
  const rot = interpolate(frame, [0, 50], [-720, 0], {
    extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut,
  });
  const settle = Math.sin(Math.max(0, frame - 50) * 0.4) * Math.max(0, 1 - (frame - 50) / 30) * 22;
  const labelIn = interpolate(frame, [60, 78], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const labelOut = interpolate(frame, [duration - 12, duration], [1, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const sandwiches = (props.background_props ?? [])
    .map((k) => SANDWICH_KEYS[k])
    .filter(Boolean) as SandwichVariant[];

  const setting = props.setting ?? "picnic";

  return (
    <AbsoluteFill>
      {renderBackground(setting)}
      {setting === "picnic" && sandwiches[0] && <Sandwich variant={sandwiches[0]} x={140} y={1380} scale={1.4} rotate={-4} />}
      {setting === "picnic" && sandwiches[1] && <Sandwich variant={sandwiches[1]} x={460} y={1340} scale={1.4} rotate={2} />}
      {setting === "picnic" && sandwiches[2] && <Sandwich variant={sandwiches[2]} x={740} y={1380} scale={1.4} rotate={-1} />}

      <TheRock x={x - 220} y={y + settle} scale={3.2} bodyRotate={rot} browAngle={14} mouthCurve={-0.3} mouthOpen={0.1} />

      {props.on_screen_label && (
        <div
          style={{
            position: "absolute", top: 200, left: 0, right: 0, textAlign: "center",
            opacity: labelIn * labelOut,
            fontFamily: "ui-rounded, system-ui, sans-serif",
            fontSize: 92, fontWeight: 900, color: "#fff",
            letterSpacing: -2, textShadow: "6px 6px 0 #1a1a1e",
          }}
        >
          {props.on_screen_label.toUpperCase()}
        </div>
      )}
    </AbsoluteFill>
  );
};
