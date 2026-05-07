import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { renderBackground, renderProtagonist, Character } from "./registry";
import { easeOut } from "./SceneTimingHelpers";
import type { DialogueLine } from "./types";

type Props = {
  setting?: string;
  protagonist?: Character | string;     // who is on screen (usually Gerald)
  event_text?: string;                  // big diegetic event label, e.g. "METEOR"
  caption?: string;                     // small descriptive overlay, e.g. "(he keeps pumping gas)"
  protagonist_x?: number;
  protagonist_y?: number;
  protagonist_scale?: number;
};

/**
 * Silent storytelling scene. Used by Gerald episodes (Format 2: The Silent
 * Witness). No speech bubbles, no scores — just the character existing in
 * the setting while the world does something around them.
 *
 * `event_text` is rendered as a large diegetic label (the visual event the
 * character is failing to react to). `caption` is a smaller deadpan overlay.
 */
export const VisualBeatScene: React.FC<{
  props: Props;
  duration: number;
  voiceover: DialogueLine[];
  sceneStartFrame: number;
}> = ({ props }) => {
  const frame = useCurrentFrame();

  const setting = props.setting ?? "park";
  const protagonist: Character = (props.protagonist as Character) ?? "gerald";

  const eventScale = interpolate(frame, [0, 14], [0.4, 1.0], {
    extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut,
  });
  const captionOpacity = interpolate(frame, [22, 36], [0, 1], {
    extrapolateRight: "clamp", extrapolateLeft: "clamp",
  });

  return (
    <AbsoluteFill>
      {renderBackground(setting)}

      {/* Big event label — visual storytelling carries the joke */}
      {props.event_text && (
        <div
          style={{
            position: "absolute",
            top: 380,
            left: 0,
            right: 0,
            textAlign: "center",
            transform: `scale(${eventScale})`,
            transformOrigin: "center top",
            fontFamily: "ui-rounded, system-ui, sans-serif",
            fontSize: 160,
            fontWeight: 900,
            color: "#1a1a1e",
            letterSpacing: -6,
            textShadow: "10px 10px 0 #d94a3a",
            whiteSpace: "pre-line",
          }}
        >
          {props.event_text.toUpperCase()}
        </div>
      )}

      {/* Protagonist — usually Gerald, doing nothing */}
      <div style={{ position: "absolute", left: 0, top: 0, right: 0, bottom: 0 }}>
        {renderProtagonist(protagonist, {
          x: props.protagonist_x ?? 380,
          y: props.protagonist_y ?? 1180,
          scale: props.protagonist_scale ?? 1.6,
          mouthOpen: 0,
          browAngle: 0,
          armUp: 0,
        })}
      </div>

      {/* Deadpan caption */}
      {props.caption && (
        <div
          style={{
            position: "absolute",
            bottom: 80,
            left: 60,
            right: 60,
            textAlign: "center",
            opacity: captionOpacity,
            fontFamily: "ui-rounded, system-ui, sans-serif",
            fontSize: 56,
            fontWeight: 800,
            color: "#1a1a1e",
            background: "#fff",
            border: "5px solid #1a1a1e",
            borderRadius: 14,
            padding: "18px 28px",
            boxShadow: "8px 8px 0 #1a1a1e",
          }}
        >
          {props.caption}
        </div>
      )}
    </AbsoluteFill>
  );
};
