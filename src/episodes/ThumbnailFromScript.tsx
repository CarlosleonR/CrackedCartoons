/**
 * Generic thumbnail renderer driven by a `ThumbnailSpec` (see
 * pipeline/schemas/publish.py). One layout enum branches the visual.
 */
import React from "react";
import { AbsoluteFill } from "remotion";
import { TheRock } from "../characters/TheRock";
import { Sandwich } from "../scene/Sandwich";

export type ThumbnailMood = "angry" | "smug" | "shocked" | "indignant" | "deadpan";
export type ThumbnailLayout =
  | "rock_left_object_right"
  | "rock_center_score_overlay"
  | "rock_only_big_text";

export type ThumbnailSpecJSON = {
  background_color: string;
  accent_color: string;
  episode_badge: string;
  headline: string;
  callout?: string | null;
  score?: string | null;
  footer: string;
  mood: ThumbnailMood;
  layout: ThumbnailLayout;
};

export type ThumbnailFromScriptProps = {
  spec: ThumbnailSpecJSON | null;
};

const MOOD_TO_FACE: Record<
  ThumbnailMood,
  { brow: number; curve: number; mouthOpen: number; pupilX: number; pupilY: number }
> = {
  angry:     { brow: 28, curve: -0.55, mouthOpen: 0.5, pupilX: 0.6, pupilY: -0.2 },
  smug:      { brow: 6,  curve: 0.2,   mouthOpen: 0.0, pupilX: -0.2, pupilY: 0 },
  shocked:   { brow: -8, curve: 0.0,   mouthOpen: 0.7, pupilX: 0,    pupilY: -0.4 },
  indignant: { brow: 22, curve: -0.4,  mouthOpen: 0.4, pupilX: 0.4,  pupilY: -0.1 },
  deadpan:   { brow: 0,  curve: 0,     mouthOpen: 0,   pupilX: 0,    pupilY: 0 },
};

const Stripes: React.FC<{ accent: string }> = ({ accent }) => (
  <svg
    viewBox="0 0 1080 1920"
    width={1080}
    height={1920}
    style={{ position: "absolute", inset: 0 }}
  >
    <g opacity="0.15" stroke={accent} strokeWidth="14" fill="none">
      <line x1="-200" y1="200" x2="1280" y2="900" />
      <line x1="-200" y1="500" x2="1280" y2="1200" />
      <line x1="-200" y1="800" x2="1280" y2="1500" />
    </g>
  </svg>
);

const Badge: React.FC<{ text: string }> = ({ text }) => (
  <div
    style={{
      position: "absolute", top: 80, left: 0, right: 0, textAlign: "center",
      fontFamily: "ui-rounded, system-ui, sans-serif",
    }}
  >
    <div
      style={{
        display: "inline-block", padding: "14px 32px",
        background: "#1a1a1e", color: "#f5d35a",
        fontSize: 56, fontWeight: 900, letterSpacing: 2,
        transform: "rotate(-3deg)",
        border: "5px solid #1a1a1e",
        boxShadow: "10px 10px 0 #d94a3a",
      }}
    >
      {text}
    </div>
  </div>
);

const Headline: React.FC<{ text: string; accent: string; top: number; size?: number }> = ({
  text, accent, top, size = 200,
}) => (
  <div
    style={{
      position: "absolute", top, left: 0, right: 0, textAlign: "center",
      fontFamily: "ui-rounded, system-ui, sans-serif",
      fontSize: size, fontWeight: 900, color: "#1a1a1e",
      lineHeight: 0.92, letterSpacing: -8,
      textShadow: `12px 12px 0 ${accent}`,
      whiteSpace: "pre-line",
    }}
  >
    {text}
  </div>
);

const Callout: React.FC<{ text: string; right: number; top: number }> = ({ text, right, top }) => (
  <div
    style={{
      position: "absolute", right, top,
      fontFamily: "ui-rounded, system-ui, sans-serif",
      fontSize: 64, fontWeight: 900, color: "#1a1a1e",
      background: "#fff", padding: "10px 20px",
      border: "5px solid #1a1a1e",
      transform: "rotate(4deg)",
      boxShadow: "6px 6px 0 #1a1a1e",
    }}
  >
    {text}
  </div>
);

const ScoreStamp: React.FC<{
  text: string; left?: number; right?: number; top: number; rotate?: number; size?: number;
}> = ({ text, left, right, top, rotate = -18, size = 150 }) => (
  <div
    style={{
      position: "absolute", left, right, top,
      transform: `rotate(${rotate}deg)`,
      fontFamily: "ui-rounded, system-ui, sans-serif",
      fontSize: size, fontWeight: 900,
      color: "#d94a3a", letterSpacing: -4,
      WebkitTextStroke: "8px #1a1a1e",
      filter: "drop-shadow(6px 6px 0 #1a1a1e)",
    }}
  >
    {text}
  </div>
);

const Footer: React.FC<{ text: string }> = ({ text }) => (
  <div
    style={{
      position: "absolute", bottom: 70, left: 0, right: 0, textAlign: "center",
      fontFamily: "ui-rounded, system-ui, sans-serif",
      fontSize: 52, fontWeight: 800, color: "#1a1a1e", letterSpacing: 1,
    }}
  >
    {text}
  </div>
);

export const ThumbnailFromScript: React.FC<ThumbnailFromScriptProps> = ({ spec }) => {
  if (!spec) {
    return (
      <AbsoluteFill style={{ backgroundColor: "#1a1a1e", color: "#f5d35a", padding: 60 }}>
        <div style={{ fontSize: 64, fontFamily: "ui-rounded, system-ui, sans-serif" }}>
          No thumbnail spec.
          <br />
          Render with --props='{`{"specSource":"Ep01-..."}`}'
        </div>
      </AbsoluteFill>
    );
  }
  const face = MOOD_TO_FACE[spec.mood];

  const bg = `radial-gradient(circle at 30% 25%, ${spec.background_color} 0%, ${spec.background_color} 65%, #00000022 100%)`;

  if (spec.layout === "rock_only_big_text") {
    return (
      <AbsoluteFill style={{ background: bg }}>
        <Stripes accent={spec.accent_color} />
        <Badge text={spec.episode_badge} />
        <Headline text={spec.headline} accent={spec.accent_color} top={260} size={220} />
        <div style={{ position: "absolute", left: 380, top: 1240 }}>
          <TheRock scale={3.0} {...face} />
        </div>
        {spec.callout && <Callout text={spec.callout} right={80} top={1180} />}
        <Footer text={spec.footer} />
      </AbsoluteFill>
    );
  }

  if (spec.layout === "rock_center_score_overlay") {
    return (
      <AbsoluteFill style={{ background: bg }}>
        <Stripes accent={spec.accent_color} />
        <Badge text={spec.episode_badge} />
        <Headline text={spec.headline} accent={spec.accent_color} top={220} />
        <div style={{ position: "absolute", left: 280, top: 1080 }}>
          <TheRock scale={3.6} {...face} />
        </div>
        {spec.score && (
          <ScoreStamp text={spec.score} right={120} top={1080} rotate={14} size={180} />
        )}
        <Footer text={spec.footer} />
      </AbsoluteFill>
    );
  }

  // default: rock_left_object_right
  return (
    <AbsoluteFill style={{ background: bg }}>
      <Stripes accent={spec.accent_color} />
      <Badge text={spec.episode_badge} />
      <Headline text={spec.headline} accent={spec.accent_color} top={220} />
      {spec.callout && <Callout text={spec.callout} right={80} top={760} />}
      <div style={{ position: "absolute", left: 40, top: 980 }}>
        <TheRock scale={3.4} {...face} />
      </div>
      <div style={{ position: "absolute", right: 60, top: 1200 }}>
        <div style={{ position: "relative", width: 440, height: 440 }}>
          <Sandwich variant="tall" scale={2.2} rotate={-4} />
          {spec.score && (
            <ScoreStamp text={spec.score} left={80} top={-90} rotate={14} size={150} />
          )}
        </div>
      </div>
      <Footer text={spec.footer} />
    </AbsoluteFill>
  );
};
