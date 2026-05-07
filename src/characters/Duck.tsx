import React from "react";

export type DuckProps = {
  scale?: number;
  x?: number;
  y?: number;
  mouthOpen?: number;
  browAngle?: number;
  armUp?: number;
};

/**
 * The Duck. A duck convinced he is a person. Wears a navy suit jacket, white
 * shirt, red tie. Holds his clipboard with confidence. Body language is
 * 100% professional human; it just happens that he is a duck.
 */
export const Duck: React.FC<DuckProps> = ({
  scale = 1,
  x = 0,
  y = 0,
  mouthOpen = 0,
  browAngle = 0,
  armUp = 0,
}) => {
  const mo = Math.max(0, Math.min(1, mouthOpen));
  const armRotate = armUp * 50;

  return (
    <svg
      viewBox="0 0 200 380"
      width={200 * scale}
      height={380 * scale}
      style={{ position: "absolute", left: x, top: y, overflow: "visible" }}
    >
      <ellipse cx="100" cy="370" rx="60" ry="6" fill="rgba(0,0,0,0.25)" />

      {/* navy suit jacket */}
      <rect x="56" y="170" width="88" height="130" rx="14" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
      {/* white shirt triangle */}
      <path d="M 88 170 L 100 220 L 112 170 Z" fill="#fff" stroke="#1a1a1e" strokeWidth="2" />
      {/* red tie */}
      <path d="M 96 178 L 104 178 L 106 200 L 100 240 L 94 200 Z" fill="#c44a3a" stroke="#1a1a1e" strokeWidth="2" />
      {/* tiny knot */}
      <rect x="96" y="172" width="8" height="6" fill="#a83a2a" stroke="#1a1a1e" strokeWidth="1" />
      {/* navy slacks */}
      <rect x="68" y="300" width="26" height="68" rx="6" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="106" y="300" width="26" height="68" rx="6" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />

      {/* arms with white feathered hands (small) */}
      <g transform={`rotate(${armRotate} 60 188)`}>
        <rect x="36" y="180" width="26" height="86" rx="10" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
        <ellipse cx="49" cy="272" rx="13" ry="11" fill="#fff8d2" stroke="#1a1a1e" strokeWidth="2" />
      </g>
      <rect x="138" y="180" width="26" height="86" rx="10" fill="#1f2d4a" stroke="#1a1a1e" strokeWidth="3" />
      <ellipse cx="151" cy="272" rx="13" ry="11" fill="#fff8d2" stroke="#1a1a1e" strokeWidth="2" />

      {/* DUCK HEAD — white feathered, a bit tall, with a cheek tuft */}
      <ellipse cx="100" cy="108" rx="60" ry="56" fill="#ffffff" stroke="#1a1a1e" strokeWidth="3" />
      {/* feather tuft on top */}
      <path d="M 100 50 Q 88 36 80 48 Q 96 50 100 62 Q 104 50 120 48 Q 112 36 100 50 Z"
            fill="#ffffff" stroke="#1a1a1e" strokeWidth="2" />

      {/* duck bill — orange */}
      <ellipse
        cx="100"
        cy={142 + mo * 3}
        rx={28}
        ry={8 + mo * 4}
        fill="#ff8a3a"
        stroke="#1a1a1e"
        strokeWidth="2.5"
      />
      {/* nostril dots on the bill */}
      <circle cx="92" cy={138 + mo * 3} r="1.5" fill="#1a1a1e" />
      <circle cx="108" cy={138 + mo * 3} r="1.5" fill="#1a1a1e" />
      {mo > 0.3 && (
        // open-bill — show pink interior
        <ellipse cx="100" cy={144 + mo * 3} rx={16} ry={mo * 4} fill="#ffa6c1" />
      )}

      {/* black bead eyes */}
      <circle cx="80" cy="98" r="6" fill="#1a1a1e" />
      <circle cx="120" cy="98" r="6" fill="#1a1a1e" />
      <circle cx="82" cy="96" r="2" fill="#fff" />
      <circle cx="122" cy="96" r="2" fill="#fff" />

      {/* eyebrow-like feather tufts (suggest expression even though ducks don't have brows) */}
      <g transform={`rotate(${browAngle} 80 84)`}>
        <path d="M 70 80 Q 80 76 92 82" stroke="#1a1a1e" strokeWidth="2.5" fill="none" />
      </g>
      <g transform={`rotate(${-browAngle} 120 84)`}>
        <path d="M 108 82 Q 120 76 130 80" stroke="#1a1a1e" strokeWidth="2.5" fill="none" />
      </g>
    </svg>
  );
};
