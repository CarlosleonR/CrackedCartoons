import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { easeOut } from "./SceneTimingHelpers";

type Props = {
  episode_number?: string;
  headline?: string;
  subtitle?: string;
};

export const TitleCardScene: React.FC<{ props: Props }> = ({ props }) => {
  const frame = useCurrentFrame();
  const headline = (props.headline || "THE ROCK").toUpperCase();
  const episodeNumber = props.episode_number || "Ep. 1";
  const subtitle = props.subtitle || "";

  const flash = interpolate(frame, [0, 4], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const titleY = interpolate(frame, [4, 18], [-200, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const titleScale = interpolate(frame, [10, 22, 28], [1, 1.08, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const subOpacity = interpolate(frame, [22, 32], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const rockX = interpolate(frame, [40, 64], [1300, 540], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const rockBob = Math.sin((frame - 40) * 0.4) * 8;
  const rockRot = interpolate(frame, [40, 64], [-120, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });

  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a1e" }}>
      <AbsoluteFill style={{ opacity: flash, backgroundColor: "#f5d35a" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            transform: `translateY(${titleY}px) scale(${titleScale})`,
            textAlign: "center",
            fontFamily: "ui-rounded, system-ui, sans-serif",
          }}
        >
          <div
            style={{
              fontSize: 140, fontWeight: 900, color: "#1a1a1e",
              lineHeight: 1, letterSpacing: -4,
              textShadow: "8px 8px 0 #d94a3a",
            }}
          >
            {headline}
          </div>
          {subtitle && (
            <div style={{ opacity: subOpacity, fontSize: 56, fontWeight: 700, color: "#1a1a1e", marginTop: 38 }}>
              {episodeNumber} — {subtitle}
            </div>
          )}
        </div>
        <div style={{ height: 60 }} />
        <div style={{ position: "relative", width: 1080, height: 600 }}>
          <TheRock
            x={rockX - 200}
            y={140 + rockBob}
            scale={2.4}
            bodyRotate={rockRot}
            browAngle={20}
            mouthCurve={-0.4}
            mouthOpen={0.05}
            pupilX={0.2}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
