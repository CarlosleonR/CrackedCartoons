import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { PicnicBackground } from "../scene/PicnicBackground";

type Props = {
  cut_count?: number;
  cut_description?: string;
};

/**
 * Quick-cut montage placeholder. Each "cut" is a 1/N slice of the duration
 * with a different background tint and a shaking Rock. Replace with bespoke
 * cuts once a montage actually needs them.
 */
export const MontageScene: React.FC<{ props: Props; duration: number }> = ({ props, duration }) => {
  const frame = useCurrentFrame();
  const cuts = Math.max(1, props.cut_count ?? 3);
  const cutLen = Math.floor(duration / cuts);
  const cutIdx = Math.min(cuts - 1, Math.floor(frame / cutLen));
  const tint = ["#9bd6ee", "#f5d35a", "#d94a3a", "#7ec04a", "#9b6cc4"][cutIdx % 5];

  return (
    <AbsoluteFill style={{ backgroundColor: tint }}>
      <PicnicBackground />
      <TheRock
        x={420 + Math.sin(frame * 0.9) * 12}
        y={1100}
        scale={3.0}
        browAngle={26}
        mouthCurve={-0.55}
        mouthOpen={(Math.sin(frame * 1.1) + 1) / 2 * 0.6}
      />
      {props.cut_description && (
        <div
          style={{
            position: "absolute", top: 220, left: 0, right: 0, textAlign: "center",
            fontFamily: "ui-rounded, system-ui, sans-serif",
            fontSize: 78, fontWeight: 900, color: "#1a1a1e",
            letterSpacing: -2, textShadow: "6px 6px 0 #fff",
          }}
        >
          {props.cut_description.toUpperCase()}
        </div>
      )}
    </AbsoluteFill>
  );
};
