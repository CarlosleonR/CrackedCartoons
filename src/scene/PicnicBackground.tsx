import React from "react";
import { AbsoluteFill } from "remotion";

export const PicnicBackground: React.FC = () => {
  return (
    <AbsoluteFill>
      <svg
        viewBox="0 0 1080 1920"
        width={1080}
        height={1920}
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#9bd6ee" />
            <stop offset="100%" stopColor="#e8f3d2" />
          </linearGradient>
          <linearGradient id="grass" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#7ec04a" />
            <stop offset="100%" stopColor="#4a8a32" />
          </linearGradient>
          <pattern id="check" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
            <rect width="80" height="80" fill="#f5e8d8" />
            <rect width="40" height="40" fill="#d94a3a" />
            <rect x="40" y="40" width="40" height="40" fill="#d94a3a" />
          </pattern>
        </defs>

        <rect x="0" y="0" width="1080" height="1100" fill="url(#sky)" />
        <circle cx="180" cy="240" r="60" fill="#fff" opacity="0.85" />
        <circle cx="240" cy="220" r="70" fill="#fff" opacity="0.85" />
        <circle cx="900" cy="320" r="55" fill="#fff" opacity="0.85" />
        <circle cx="950" cy="300" r="50" fill="#fff" opacity="0.85" />

        <ellipse cx="200" cy="1100" rx="220" ry="160" fill="#3a7a2a" opacity="0.7" />
        <rect x="180" y="900" width="40" height="200" fill="#5a3a1e" />
        <ellipse cx="880" cy="1100" rx="200" ry="150" fill="#3a7a2a" opacity="0.7" />
        <rect x="860" y="920" width="36" height="180" fill="#5a3a1e" />

        <rect x="0" y="1080" width="1080" height="840" fill="url(#grass)" />

        <g transform="translate(540 1500) rotate(-3)">
          <rect x="-540" y="-180" width="1080" height="360" fill="url(#check)" opacity="0.95" />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
