import React from "react";

export type SandwichVariant = "classic" | "tall" | "weird";

export type SandwichProps = {
  variant?: SandwichVariant;
  scale?: number;
  x?: number;
  y?: number;
  rotate?: number;
  opacity?: number;
};

export const Sandwich: React.FC<SandwichProps> = ({
  variant = "classic",
  scale = 1,
  x = 0,
  y = 0,
  rotate = 0,
  opacity = 1,
}) => {
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
        opacity,
        transform: `rotate(${rotate}deg)`,
        transformOrigin: "center",
      }}
    >
      {variant === "classic" && (
        <g>
          <ellipse cx="100" cy="172" rx="70" ry="6" fill="rgba(0,0,0,0.2)" />
          <path
            d="M 30 110 Q 100 90 170 110 L 170 130 Q 100 145 30 130 Z"
            fill="#e8c184"
            stroke="#7a5a2a"
            strokeWidth="3"
          />
          <rect x="32" y="125" width="136" height="8" fill="#5fa84a" rx="2" />
          <rect x="32" y="133" width="136" height="6" fill="#d96a55" rx="2" />
          <rect x="32" y="139" width="136" height="6" fill="#f5d35a" rx="2" />
          <path
            d="M 30 145 Q 100 130 170 145 L 170 165 Q 100 180 30 165 Z"
            fill="#e8c184"
            stroke="#7a5a2a"
            strokeWidth="3"
          />
        </g>
      )}
      {variant === "tall" && (
        <g>
          <ellipse cx="100" cy="180" rx="60" ry="5" fill="rgba(0,0,0,0.2)" />
          <path
            d="M 45 60 Q 100 45 155 60 L 155 78 Q 100 90 45 78 Z"
            fill="#e8c184"
            stroke="#7a5a2a"
            strokeWidth="3"
          />
          <rect x="48" y="76" width="104" height="8" fill="#5fa84a" rx="2" />
          <rect x="48" y="84" width="104" height="10" fill="#c44a3a" rx="2" />
          <rect x="48" y="94" width="104" height="6" fill="#fff7c2" rx="2" />
          <rect x="48" y="100" width="104" height="10" fill="#e07a4a" rx="2" />
          <rect x="48" y="110" width="104" height="6" fill="#5fa84a" rx="2" />
          <rect x="48" y="116" width="104" height="10" fill="#c44a3a" rx="2" />
          <rect x="48" y="126" width="104" height="6" fill="#fff7c2" rx="2" />
          <path
            d="M 45 130 Q 100 118 155 130 L 155 150 Q 100 165 45 150 Z"
            fill="#e8c184"
            stroke="#7a5a2a"
            strokeWidth="3"
          />
        </g>
      )}
      {variant === "weird" && (
        <g>
          <ellipse cx="100" cy="172" rx="70" ry="6" fill="rgba(0,0,0,0.2)" />
          <path
            d="M 28 105 Q 100 82 172 110 L 170 130 Q 100 148 28 128 Z"
            fill="#f0d4a4"
            stroke="#a07a3a"
            strokeWidth="3"
          />
          <rect x="32" y="124" width="136" height="6" fill="#9b6cc4" rx="2" />
          <path
            d="M 35 130 Q 100 142 165 130 L 165 138 Q 100 150 35 138 Z"
            fill="#7ad4a8"
          />
          <circle cx="60" cy="135" r="4" fill="#3a5a3a" />
          <circle cx="100" cy="138" r="5" fill="#3a5a3a" />
          <circle cx="140" cy="135" r="4" fill="#3a5a3a" />
          <path
            d="M 28 142 Q 100 128 172 145 L 170 165 Q 100 180 28 162 Z"
            fill="#f0d4a4"
            stroke="#a07a3a"
            strokeWidth="3"
          />
          <text x="100" y="60" textAnchor="middle" fontSize="22" fill="#8a4ac4" fontWeight="700">
            ???
          </text>
        </g>
      )}
    </svg>
  );
};
