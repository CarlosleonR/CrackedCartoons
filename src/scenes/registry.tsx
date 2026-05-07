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

export const renderNpc = (
  speaker: Speaker,
  setting: string | undefined,
  p: NpcRendererProps,
): React.ReactNode => {
  // The kid is the kid wherever we are.
  if (speaker === "kid") {
    const kp: ChildProps = {
      x: p.x, y: p.y, scale: p.scale,
      mouthOpen: p.mouthOpen, browAngle: p.browAngle, armUp: p.armUp,
    };
    return <Child {...kp} />;
  }
  // Generic NPC: pick by setting.
  if (setting === "airport") {
    const ga: GateAgentProps = {
      x: p.x, y: p.y, scale: p.scale,
      mouthOpen: p.mouthOpen, browAngle: p.browAngle, armUp: p.armUp,
    };
    return <GateAgent {...ga} />;
  }
  // Fallback: use the kid as a stand-in. (The vision-QC step will flag this
  // and prompt the human to add a purpose-built NPC.)
  const kp: ChildProps = {
    x: p.x, y: p.y, scale: p.scale,
    mouthOpen: p.mouthOpen, browAngle: p.browAngle, armUp: p.armUp,
  };
  return <Child {...kp} />;
};
