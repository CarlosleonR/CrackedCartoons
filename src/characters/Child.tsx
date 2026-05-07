import React from "react";

export type ChildProps = {
  scale?: number;
  x?: number;
  y?: number;
  mouthOpen?: number;
  browAngle?: number;
  armUp?: number;
};

export const Child: React.FC<ChildProps> = ({
  scale = 1,
  x = 0,
  y = 0,
  mouthOpen = 0,
  browAngle = 0,
  armUp = 0,
}) => {
  const mo = Math.max(0, Math.min(1, mouthOpen));
  const armRotate = armUp * 135;

  return (
    <svg
      viewBox="0 0 200 360"
      width={200 * scale}
      height={360 * scale}
      style={{
        position: "absolute",
        left: x,
        top: y,
        overflow: "visible",
      }}
    >
      <ellipse cx="100" cy="350" rx="60" ry="6" fill="rgba(0,0,0,0.2)" />

      <rect x="60" y="160" width="80" height="120" rx="14" fill="#e54f3a" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="74" y="280" width="22" height="60" rx="6" fill="#3a4ac4" stroke="#1a1a1e" strokeWidth="3" />
      <rect x="104" y="280" width="22" height="60" rx="6" fill="#3a4ac4" stroke="#1a1a1e" strokeWidth="3" />

      <g transform={`rotate(${armRotate} 65 180)`}>
        <rect x="38" y="170" width="28" height="80" rx="10" fill="#e54f3a" stroke="#1a1a1e" strokeWidth="3" />
        <circle cx="48" cy="252" r="12" fill="#f5c89a" stroke="#1a1a1e" strokeWidth="3" />
      </g>
      <rect x="134" y="170" width="28" height="80" rx="10" fill="#e54f3a" stroke="#1a1a1e" strokeWidth="3" />
      <circle cx="148" cy="252" r="12" fill="#f5c89a" stroke="#1a1a1e" strokeWidth="3" />

      <circle cx="100" cy="100" r="58" fill="#f5c89a" stroke="#1a1a1e" strokeWidth="3" />
      <path
        d="M 50 70 Q 60 30 100 35 Q 140 30 150 70 Q 150 60 130 60 Q 100 50 70 60 Q 50 60 50 70 Z"
        fill="#5a3a1e"
        stroke="#1a1a1e"
        strokeWidth="2"
      />

      <g transform={`rotate(${-browAngle} 80 90)`}>
        <rect x="68" y="86" width="22" height="5" rx="2" fill="#1a1a1e" />
      </g>
      <g transform={`rotate(${browAngle} 120 90)`}>
        <rect x="110" y="86" width="22" height="5" rx="2" fill="#1a1a1e" />
      </g>

      <circle cx="80" cy="105" r="5" fill="#1a1a1e" />
      <circle cx="120" cy="105" r="5" fill="#1a1a1e" />
      <circle cx="81" cy="103" r="1.5" fill="#fff" />
      <circle cx="121" cy="103" r="1.5" fill="#fff" />

      <ellipse cx="100" cy={130 + mo * 4} rx={6 + mo * 8} ry={2 + mo * 10} fill="#1a1a1e" />
      {mo > 0.4 && <ellipse cx="100" cy={132 + mo * 4} rx={3 + mo * 4} ry={mo * 5} fill="#a83a4a" />}
    </svg>
  );
};
