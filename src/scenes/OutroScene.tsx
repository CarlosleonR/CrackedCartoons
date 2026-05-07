import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { easeInOut, easeOut } from "./SceneTimingHelpers";

type Props = {
  big_text?: string;
  subtitle?: string;
  tag?: string;
};

export const OutroScene: React.FC<{ props: Props }> = ({ props }) => {
  const frame = useCurrentFrame();
  const bigText = (props.big_text ?? "NOBODY WON.").toUpperCase().split("\n");

  const flash = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const cardY = interpolate(frame, [4, 22], [-300, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const cardScale = interpolate(frame, [18, 30, 38], [1, 1.12, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeInOut });
  const subIn = interpolate(frame, [38, 54], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const tagIn = interpolate(frame, [70, 90], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const rockShake = Math.sin(frame * 0.4) * 4;

  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a1e" }}>
      <AbsoluteFill style={{ opacity: flash, backgroundColor: "#f5d35a" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            transform: `translateY(${cardY}px) scale(${cardScale})`,
            textAlign: "center",
            fontFamily: "ui-rounded, system-ui, sans-serif",
          }}
        >
          {bigText.map((line, i) => (
            <div
              key={i}
              style={{
                fontSize: 200, fontWeight: 900, color: "#1a1a1e",
                lineHeight: 0.9, letterSpacing: -8,
                marginTop: i === 0 ? 0 : 10,
                textShadow: "10px 10px 0 #d94a3a",
              }}
            >
              {line}
            </div>
          ))}
          {props.subtitle && (
            <div style={{ opacity: subIn, fontSize: 56, fontWeight: 800, color: "#1a1a1e", marginTop: 60 }}>
              {props.subtitle}
            </div>
          )}
        </div>

        <div style={{ height: 80 }} />
        <div style={{ position: "relative", width: 1080, height: 280 }}>
          <TheRock
            x={420 + rockShake}
            y={20}
            scale={1.6}
            browAngle={22}
            mouthCurve={-0.5}
            mouthOpen={(Math.sin(frame * 0.8) + 1) / 2 * 0.6}
          />
        </div>

        {props.tag && (
          <div
            style={{
              opacity: tagIn,
              fontSize: 48, fontWeight: 800, color: "#1a1a1e",
              fontFamily: "ui-rounded, system-ui, sans-serif",
              marginTop: 40,
            }}
          >
            {props.tag}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
