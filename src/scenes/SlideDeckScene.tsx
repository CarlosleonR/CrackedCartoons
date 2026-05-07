import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { DaveFromHR } from "../characters/DaveFromHR";
import { renderBackground } from "./registry";
import { easeOut, lipFlap } from "./SceneTimingHelpers";
import type { DialogueLine } from "./types";

type Props = {
  setting?: string;
  slide_number?: number;
  slide_count?: number | string;
  slide_title?: string;
  slide_subtitle?: string;
};

/**
 * Dave's projector + slide. The slide IS the visual; Dave stands beside it
 * with a remote, mouth flapping if he's currently speaking. Setting can be
 * anything — the joke works because Dave is in the WRONG setting and is
 * presenting anyway.
 */
export const SlideDeckScene: React.FC<{
  props: Props;
  duration: number;
  voiceover: DialogueLine[];
  sceneStartFrame: number;
}> = ({ props, voiceover, sceneStartFrame }) => {
  const frame = useCurrentFrame();
  const setting = props.setting ?? "gladiator_arena";
  const slideNumber = props.slide_number ?? 1;
  const slideCount = props.slide_count ?? "47";
  const slideTitle = props.slide_title ?? "WORKPLACE EXPECTATIONS";
  const slideSubtitle = props.slide_subtitle;

  const slidePop = interpolate(frame, [0, 12], [0.7, 1], {
    extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut,
  });

  const absFrame = sceneStartFrame + frame;
  const activeLine = voiceover.find(
    (l) => absFrame >= l.start_frame && absFrame < l.start_frame + l.estimated_duration_frames,
  );
  const isDaveSpeaking = activeLine?.speaker === "dave";
  const daveMouth = isDaveSpeaking ? 0.7 * lipFlap(frame, 0.85) : 0.05;

  return (
    <AbsoluteFill>
      {renderBackground(setting)}

      {/* Tilted projection screen — the slide */}
      <div
        style={{
          position: "absolute",
          top: 220,
          left: 90,
          right: 90,
          padding: "70px 50px",
          background: "#fff",
          border: "10px solid #1a1a1e",
          borderRadius: 16,
          transform: `scale(${slidePop})`,
          transformOrigin: "center top",
          boxShadow: "16px 16px 0 #1a1a1e",
          fontFamily: "ui-rounded, system-ui, sans-serif",
          textAlign: "left",
        }}
      >
        <div style={{ fontSize: 38, fontWeight: 800, color: "#7e8593", letterSpacing: 1 }}>
          SLIDE {slideNumber} of {slideCount}
        </div>
        <div style={{ height: 8, background: "#caa44a", margin: "20px 0 36px" }} />
        <div
          style={{
            fontSize: 100,
            fontWeight: 900,
            color: "#1a1a1e",
            letterSpacing: -3,
            lineHeight: 1.0,
          }}
        >
          {slideTitle.toUpperCase()}
        </div>
        {slideSubtitle && (
          <div
            style={{
              fontSize: 44,
              fontWeight: 700,
              color: "#1a1a1e",
              opacity: 0.7,
              marginTop: 28,
            }}
          >
            {slideSubtitle}
          </div>
        )}
      </div>

      {/* Dave to the side with a remote */}
      <DaveFromHR
        x={780}
        y={1240}
        scale={1.7}
        mouthOpen={daveMouth}
        browAngle={4}
        armUp={0.6}
      />
    </AbsoluteFill>
  );
};
