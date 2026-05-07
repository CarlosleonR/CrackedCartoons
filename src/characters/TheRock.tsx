import React from "react";

export type RockProps = {
  mouthOpen?: number;
  mouthCurve?: number;
  browAngle?: number;
  pupilX?: number;
  pupilY?: number;
  bodyRotate?: number;
  scale?: number;
  x?: number;
  y?: number;
};

export const TheRock: React.FC<RockProps> = ({
  mouthOpen = 0,
  mouthCurve = 0,
  browAngle = 0,
  pupilX = 0,
  pupilY = 0,
  bodyRotate = 0,
  scale = 1,
  x = 0,
  y = 0,
}) => {
  const mo = Math.max(0, Math.min(1, mouthOpen));
  const mc = Math.max(-1, Math.min(1, mouthCurve));
  const px = Math.max(-1, Math.min(1, pupilX));
  const py = Math.max(-1, Math.min(1, pupilY));

  const mouthCx = 100;
  const mouthCy = 132;
  const mouthRx = 22;
  const mouthRyMax = 18;
  const mouthRy = 1.5 + mo * mouthRyMax;

  const curveLift = -mc * 8;
  const mouthPath = `
    M ${mouthCx - mouthRx} ${mouthCy + curveLift}
    Q ${mouthCx} ${mouthCy + mouthRy * 1.2 - curveLift * 2}
      ${mouthCx + mouthRx} ${mouthCy + curveLift}
    Q ${mouthCx} ${mouthCy - mouthRy * 0.6 - curveLift * 2}
      ${mouthCx - mouthRx} ${mouthCy + curveLift}
    Z
  `;

  const browLeftAngle = browAngle;
  const browRightAngle = -browAngle;

  const pupilOffsetX = px * 4;
  const pupilOffsetY = py * 3;

  return (
    <svg
      viewBox="0 0 200 200"
      width={200 * scale}
      height={200 * scale}
      style={{
        position: "absolute",
        left: x,
        top: y,
        overflow: "visible",
        transform: `rotate(${bodyRotate}deg)`,
        transformOrigin: "center",
      }}
    >
      <ellipse cx="100" cy="178" rx="70" ry="8" fill="rgba(0,0,0,0.25)" />

      <g>
        <path
          d="
            M 30 110
            C 22 80, 38 50, 65 42
            C 85 36, 105 38, 130 46
            C 158 56, 178 80, 172 110
            C 168 138, 150 162, 120 168
            C 85 174, 50 162, 36 142
            C 28 130, 26 120, 30 110 Z
          "
          fill="#7a7a82"
          stroke="#3d3d44"
          strokeWidth="3"
          strokeLinejoin="round"
        />

        <path
          d="M 50 70 Q 60 65 75 70"
          stroke="#5a5a62"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
        />
        <path
          d="M 130 60 Q 145 58 155 68"
          stroke="#5a5a62"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
        />
        <circle cx="58" cy="148" r="3" fill="#5a5a62" />
        <circle cx="148" cy="138" r="2.5" fill="#5a5a62" />
        <circle cx="120" cy="158" r="2" fill="#5a5a62" />

        <ellipse cx="60" cy="100" rx="14" ry="11" fill="#fafafa" stroke="#2a2a2e" strokeWidth="2" />
        <ellipse cx="140" cy="100" rx="14" ry="11" fill="#fafafa" stroke="#2a2a2e" strokeWidth="2" />
        <circle cx={60 + pupilOffsetX} cy={100 + pupilOffsetY} r="5" fill="#1a1a1e" />
        <circle cx={140 + pupilOffsetX} cy={100 + pupilOffsetY} r="5" fill="#1a1a1e" />
        <circle cx={61 + pupilOffsetX} cy={98 + pupilOffsetY} r="1.5" fill="#fff" />
        <circle cx={141 + pupilOffsetX} cy={98 + pupilOffsetY} r="1.5" fill="#fff" />

        <g transform={`rotate(${browLeftAngle} 60 80)`}>
          <rect x="44" y="78" width="32" height="6" rx="3" fill="#2a2a2e" />
        </g>
        <g transform={`rotate(${browRightAngle} 140 80)`}>
          <rect x="124" y="78" width="32" height="6" rx="3" fill="#2a2a2e" />
        </g>

        <path d={mouthPath} fill="#1a1a1e" stroke="#1a1a1e" strokeWidth="2" strokeLinejoin="round" />
        {mo > 0.3 && (
          <ellipse
            cx={mouthCx}
            cy={mouthCy + mouthRy * 0.4}
            rx={mouthRx * 0.55}
            ry={mouthRy * 0.5}
            fill="#a83a4a"
          />
        )}
      </g>
    </svg>
  );
};
