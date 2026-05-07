/**
 * Setting -> Background and Speaker -> Character lookup.
 *
 * Scenes branch on `props.setting` and `props.participants` from the
 * EpisodeScript, so the same DialogueExchangeScene can render a picnic OR
 * an airport scene depending on what Agent 2 wrote into the script.
 *
 * Adding a new setting:
 *   1. Build src/scene/<Name>Background.tsx
 *   2. Add an entry below
 *   3. Add the string to the system prompt's allowed setting list
 *      (pipeline/pipeline/prompts/writer_system.md, scene type catalog)
 */
import React from "react";
import { PicnicBackground } from "../scene/PicnicBackground";
import { AirportBackground } from "../scene/AirportBackground";
import { Child, ChildProps } from "../characters/Child";
import { GateAgent, GateAgentProps } from "../characters/GateAgent";
import { Gerald, GeraldProps } from "../characters/Gerald";
import { DaveFromHR, DaveFromHRProps } from "../characters/DaveFromHR";
import { Duck, DuckProps } from "../characters/Duck";
import type { Speaker } from "./types";

export type Setting = "picnic" | "airport" | "office" | "cafe" | "park" | "auto";

export const BACKGROUND_REGISTRY: Record<Setting, React.FC> = {
  picnic: PicnicBackground,
  airport: AirportBackground,
  // Stubs that fall back to picnic until purpose-built. Listed explicitly so
  // the writer can request them and we get a known visual rather than a
  // crash; the QC-vision step will then flag the mismatch as a setting drift.
  office: PicnicBackground,
  cafe: PicnicBackground,
  park: PicnicBackground,
  auto: PicnicBackground,
};

export const renderBackground = (setting?: string): React.ReactNode => {
  const key = (setting as Setting) ?? "picnic";
  const Component = BACKGROUND_REGISTRY[key] ?? PicnicBackground;
  return <Component />;
};

/** Non-rock NPC component for a given speaker + setting context. */
export type NpcRendererProps = {
  x: number;
  y: number;
  scale: number;
  mouthOpen: number;
  browAngle: number;
  armUp: number;
};

/* ---------- Rating-beat subjects ---------- */

export type SubjectKind = "sandwich" | "text" | "auto";

export type SubjectRendererProps = {
  variant: string;          // e.g. "tall" sandwich variant; or "GROUP 4" text label
  scale: number;
  x: number;
  y: number;
  rotate: number;
  shake: number;
  setting: string;
};

export const renderSubject = (
  kind: SubjectKind | string | undefined,
  p: SubjectRendererProps,
): React.ReactNode => {
  // Text-card subject — large headline banner. Used when the rating target
  // isn't a thing we have an SVG for (boarding group, tier name, etc).
  // Centered horizontally on the 1080 canvas; vertical position follows p.y.
  if (kind === "text") {
    return (
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: p.y + 120,                 // a bit lower than sandwich y so it doesn't fight the score
          textAlign: "center",
          transform: `translateX(${p.shake}px) rotate(${p.rotate}deg) scale(${p.scale / 2.4})`,
          transformOrigin: "center top",
          fontFamily: "ui-rounded, system-ui, sans-serif",
          pointerEvents: "none",
        }}
      >
        <div
          style={{
            display: "inline-block",
            padding: "28px 56px",
            background: "#fff",
            border: "8px solid #1a1a1e",
            borderRadius: 24,
            boxShadow: "10px 10px 0 #1a1a1e",
            fontSize: 120,
            fontWeight: 900,
            color: "#1a1a1e",
            letterSpacing: -4,
            whiteSpace: "nowrap",
          }}
        >
          {p.variant.toUpperCase()}
        </div>
      </div>
    );
  }

  // Default: sandwich (legacy / picnic episodes).
  // Lazily import to avoid hard cycle.
  const { Sandwich } = require("../scene/Sandwich") as typeof import("../scene/Sandwich");
  const sw = (["classic", "tall", "weird"].includes(p.variant) ? p.variant : "classic") as
    "classic" | "tall" | "weird";
  return (
    <Sandwich
      variant={sw}
      x={p.x + p.shake}
      y={p.y}
      scale={p.scale}
      rotate={p.rotate}
    />
  );
};

export const renderNpc = (
  speaker: Speaker,
  setting: string | undefined,
  p: NpcRendererProps,
): React.ReactNode => {
  const common = {
    x: p.x, y: p.y, scale: p.scale,
    mouthOpen: p.mouthOpen, browAngle: p.browAngle, armUp: p.armUp,
  };

  // Speaker-pinned characters take priority over setting-based fallbacks.
  if (speaker === "kid")    return <Child       {...(common as ChildProps)} />;
  if (speaker === "gerald") return <Gerald      {...(common as GeraldProps)} />;
  if (speaker === "dave")   return <DaveFromHR  {...(common as DaveFromHRProps)} />;
  if (speaker === "duck")   return <Duck        {...(common as DuckProps)} />;

  // Generic "other" NPC: pick by setting.
  if (setting === "airport") return <GateAgent {...(common as GateAgentProps)} />;

  // Fallback: kid stand-in. Vision-QC will flag for the human to add a real NPC.
  return <Child {...(common as ChildProps)} />;
};

/* ---------- Protagonist (the episode's lead) ---------- */

export type Character = "the_rock" | "gerald" | "dave_from_hr" | "the_duck";

export const renderProtagonist = (
  character: Character | string | undefined,
  p: NpcRendererProps,
): React.ReactNode => {
  // The Rock is rendered separately by scene components (he has bespoke
  // mouth/curve/pupil props); this helper covers the *other* leads.
  const common = {
    x: p.x, y: p.y, scale: p.scale,
    mouthOpen: p.mouthOpen, browAngle: p.browAngle, armUp: p.armUp,
  };
  if (character === "gerald")        return <Gerald     {...(common as GeraldProps)} />;
  if (character === "dave_from_hr")  return <DaveFromHR {...(common as DaveFromHRProps)} />;
  if (character === "the_duck")      return <Duck       {...(common as DuckProps)} />;
  return null; // the_rock and unrecognized values: caller renders separately
};
