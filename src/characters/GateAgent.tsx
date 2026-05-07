import React from "react";

export type GateAgentProps = {
  scale?: number;
  x?: number;
  y?: number;
  mouthOpen?: number;
  browAngle?: number;
  armUp?: number;
};

/**
 * Generic adult NPC in airline uniform. Used as the foil for The Rock when
 * the script's `participants` includes "other" in airport-style settings.
 */
export const GateAgent: React.FC<GateAgentProps> = ({
  scale = 1,
  x = 0,
  y = 0,
  mouthOpen = 0,
  browAngle = 0,
  armUp = 0,
}) => {
  const mo = Math.max(0, Math.min(1, mouthOpen));
  const armRotate = armUp * 70;

  return (
    <svg
      viewBox="0 0 200 380"
      width={200 * scale}
      height={380 * scale}
      style={{ position: "absolute", left: x, top: y, overflow: "visible" }}
    >
      <ellipse cx="100" cy="370" rx="65" ry="6" fill="rgba(0,0,0,0.25)" />

      {/* uniform jacket: navy with gold trim */}
      <rect x="56" y="170" width="88" height="130" rx="14" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="56" y="170" width="88" height="14" fill="#caa44a" />
      <rect x="96" y="184" width="8" height="116" fill="#caa44a" />
      <rect x="64" y="190" width="10" height="6" fill="#caa44a" rx="1" />
      <rect x="64" y="200" width="10" height="6" fill="#caa44a" rx="1" />

      {/* slacks */}
      <rect x="68" y="300" width="26" height="68" rx="6" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="106" y="300" width="26" height="68" rx="6" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />

      {/* arms */}
      <g transform={`rotate(${armRotate} 60 188)`}>
        <rect x="36" y="180" width="26" height="86" rx="10" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
        <circle cx="48" cy="270" r="12" fill="#d8b48a" stroke="#1a1a1e" strokeWidth="3" />
      </g>
      <rect x="138" y="180" width="26" height="86" rx="10" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
      <circle cx="150" cy="270" r="12" fill="#d8b48a" stroke="#1a1a1e" strokeWidth="3" />

      {/* head + cap */}
      <circle cx="100" cy="110" r="56" fill="#d8b48a" stroke="#1a1a1e" strokeWidth="3" />
      <path
        d="M 42 90 Q 50 50 100 50 Q 150 50 158 90 L 158 102 Q 100 86 42 102 Z"
        fill="#1f2d4a"
        stroke="#1a1a1e"
        strokeWidth="3"
      />
      <rect x="48" y="98" width="104" height="8" fill="#caa44a" />

      {/* brows */}
      <g transform={`rotate(${browAngle} 80 96)`}>
        <rect x="68" y="93" width="22" height="5" rx="2" fill="#1a1a1e" />
      </g>
      <g transform={`rotate(${-browAngle} 120 96)`}>
        <rect x="110" y="93" width="22" height="5" rx="2" fill="#1a1a1e" />
      </g>

      {/* eyes */}
      <circle cx="80" cy="115" r="5" fill="#1a1a1e" />
      <circle cx="120" cy="115" r="5" fill="#1a1a1e" />

      {/* mustache (subtle) */}
      <rect x="86" y="138" width="28" height="4" rx="2" fill="#5a3a1e" />

      {/* mouth */}
      <ellipse cx="100" cy={148 + mo * 4} rx={6 + mo * 6} ry={1.5 + mo * 8} fill="#1a1a1e" />
      {mo > 0.4 && <ellipse cx="100" cy={150 + mo * 4} rx={3 + mo * 3} ry={mo * 4} fill="#a83a4a" />}

      {/* name tag */}
      <rect x="76" y="234" width="48" height="14" rx="2" fill="#fff" stroke="#1a1a1e" strokeWidth="2" />
      <line x1="80" y1="241" x2="120" y2="241" stroke="#1a1a1e" strokeWidth="1" />
    </svg>
  );
};
