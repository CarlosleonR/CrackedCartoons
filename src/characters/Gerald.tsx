import React from "react";

export type GeraldProps = {
  scale?: number;
  x?: number;
  y?: number;
  /** Gerald has zero reactions. These props mostly do nothing — included so
   *  the registry can call him with the same shape as other NPCs. */
  mouthOpen?: number;
  browAngle?: number;
  armUp?: number;
};

/**
 * Extremely normal-looking guy. Beige sweater, brown pants, neutral face that
 * never changes regardless of what's happening around him. Comedy comes from
 * his complete lack of reaction.
 */
export const Gerald: React.FC<GeraldProps> = ({
  scale = 1,
  x = 0,
  y = 0,
}) => {
  return (
    <svg
      viewBox="0 0 200 380"
      width={200 * scale}
      height={380 * scale}
      style={{ position: "absolute", left: x, top: y, overflow: "visible" }}
    >
      <ellipse cx="100" cy="370" rx="60" ry="6" fill="rgba(0,0,0,0.25)" />

      {/* beige sweater — non-descript */}
      <rect x="58" y="170" width="84" height="130" rx="14" fill="#c9b58a" stroke="#1a1a1e" strokeWidth="3" />
      {/* khaki pants */}
      <rect x="68" y="300" width="26" height="68" rx="6" fill="#a8915a" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="106" y="300" width="26" height="68" rx="6" fill="#a8915a" stroke="#1a1a1e" strokeWidth="3" />

      {/* arms — always at his sides */}
      <rect x="36" y="180" width="26" height="86" rx="10" fill="#c9b58a" stroke="#1a1a1e" strokeWidth="3" />
      <circle cx="49" cy="270" r="12" fill="#e6c39b" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="138" y="180" width="26" height="86" rx="10" fill="#c9b58a" stroke="#1a1a1e" strokeWidth="3" />
      <circle cx="151" cy="270" r="12" fill="#e6c39b" stroke="#1a1a1e" strokeWidth="3" />

      {/* head + plain brown hair */}
      <circle cx="100" cy="110" r="56" fill="#e6c39b" stroke="#1a1a1e" strokeWidth="3" />
      <path
        d="M 46 80 Q 60 50 100 50 Q 140 50 154 80 Q 154 65 130 60 Q 100 52 70 60 Q 46 65 46 80 Z"
        fill="#5a3a1e"
        stroke="#1a1a1e"
        strokeWidth="2"
      />

      {/* perfectly horizontal eyebrows — no emotion */}
      <rect x="68" y="93" width="22" height="4" rx="1" fill="#1a1a1e" />
      <rect x="110" y="93" width="22" height="4" rx="1" fill="#1a1a1e" />

      {/* dot eyes */}
      <circle cx="80" cy="115" r="4" fill="#1a1a1e" />
      <circle cx="120" cy="115" r="4" fill="#1a1a1e" />

      {/* small flat mouth — never moves */}
      <line x1="92" y1="142" x2="108" y2="142" stroke="#1a1a1e" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
};
