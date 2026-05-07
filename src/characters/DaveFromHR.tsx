import React from "react";

export type DaveFromHRProps = {
  scale?: number;
  x?: number;
  y?: number;
  mouthOpen?: number;
  browAngle?: number;
  armUp?: number;
};

/**
 * Dave from HR. Polo shirt with a lanyard. Slightly receding hairline. Always
 * mid-sentence. The lanyard is the visual anchor — it's how you know it's Dave.
 */
export const DaveFromHR: React.FC<DaveFromHRProps> = ({
  scale = 1,
  x = 0,
  y = 0,
  mouthOpen = 0,
  browAngle = 0,
  armUp = 0,
}) => {
  const mo = Math.max(0, Math.min(1, mouthOpen));
  const armRotate = armUp * 60;

  return (
    <svg
      viewBox="0 0 200 380"
      width={200 * scale}
      height={380 * scale}
      style={{ position: "absolute", left: x, top: y, overflow: "visible" }}
    >
      <ellipse cx="100" cy="370" rx="62" ry="6" fill="rgba(0,0,0,0.25)" />

      {/* light-blue polo */}
      <rect x="56" y="170" width="88" height="130" rx="14" fill="#a8c5e0" stroke="#1a1a1e" strokeWidth="3" />
      {/* polo collar */}
      <path d="M 80 170 L 100 188 L 120 170 L 120 184 L 100 200 L 80 184 Z" fill="#fff" stroke="#1a1a1e" strokeWidth="2" />
      {/* lanyard — bright orange strap with badge */}
      <path d="M 88 170 Q 100 200 100 215" stroke="#ff8a3a" strokeWidth="4" fill="none" />
      <path d="M 112 170 Q 100 200 100 215" stroke="#ff8a3a" strokeWidth="4" fill="none" />
      <rect x="84" y="215" width="32" height="42" rx="3" fill="#fff" stroke="#1a1a1e" strokeWidth="2" />
      <line x1="88" y1="225" x2="112" y2="225" stroke="#1a1a1e" strokeWidth="1" />
      <line x1="88" y1="232" x2="108" y2="232" stroke="#1a1a1e" strokeWidth="1" opacity="0.6" />
      <line x1="88" y1="238" x2="106" y2="238" stroke="#1a1a1e" strokeWidth="1" opacity="0.6" />
      {/* khaki pants */}
      <rect x="68" y="300" width="26" height="68" rx="6" fill="#caa44a" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="106" y="300" width="26" height="68" rx="6" fill="#caa44a" stroke="#1a1a1e" strokeWidth="3" />

      {/* gesturing left arm */}
      <g transform={`rotate(${armRotate} 60 188)`}>
        <rect x="36" y="180" width="26" height="86" rx="10" fill="#a8c5e0" stroke="#1a1a1e" strokeWidth="3" />
        <circle cx="49" cy="270" r="12" fill="#e6c39b" stroke="#1a1a1e" strokeWidth="3" />
        {/* index-finger gesture when arm is up */}
        {armUp > 0.4 && <line x1="58" y1="270" x2="78" y2="262" stroke="#1a1a1e" strokeWidth="3" strokeLinecap="round" />}
      </g>
      <rect x="138" y="180" width="26" height="86" rx="10" fill="#a8c5e0" stroke="#1a1a1e" strokeWidth="3" />
      <circle cx="151" cy="270" r="12" fill="#e6c39b" stroke="#1a1a1e" strokeWidth="3" />

      {/* head + receding hair */}
      <circle cx="100" cy="110" r="56" fill="#e6c39b" stroke="#1a1a1e" strokeWidth="3" />
      <path
        d="M 50 88 Q 70 60 100 62 Q 130 60 150 88 Q 138 76 122 78 Q 100 80 78 78 Q 62 76 50 88 Z"
        fill="#7a5a3a"
        stroke="#1a1a1e"
        strokeWidth="2"
      />

      {/* glasses — Dave has wireframes */}
      <circle cx="80" cy="115" r="13" fill="none" stroke="#1a1a1e" strokeWidth="2.5" />
      <circle cx="120" cy="115" r="13" fill="none" stroke="#1a1a1e" strokeWidth="2.5" />
      <line x1="93" y1="115" x2="107" y2="115" stroke="#1a1a1e" strokeWidth="2.5" />
      {/* eyes inside glasses */}
      <circle cx="80" cy="115" r="3" fill="#1a1a1e" />
      <circle cx="120" cy="115" r="3" fill="#1a1a1e" />

      {/* brows above glasses */}
      <g transform={`rotate(${browAngle} 80 96)`}>
        <rect x="68" y="92" width="22" height="4" rx="1" fill="#1a1a1e" />
      </g>
      <g transform={`rotate(${-browAngle} 120 96)`}>
        <rect x="110" y="92" width="22" height="4" rx="1" fill="#1a1a1e" />
      </g>

      {/* mouth — mid-explanation by default */}
      <ellipse cx="100" cy={146 + mo * 4} rx={6 + mo * 6} ry={1.5 + mo * 7} fill="#1a1a1e" />
    </svg>
  );
};
