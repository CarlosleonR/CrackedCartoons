import React from "react";
import { AbsoluteFill } from "remotion";

export const AirportBackground: React.FC = () => {
  return (
    <AbsoluteFill>
      <svg
        viewBox="0 0 1080 1920"
        width={1080}
        height={1920}
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <linearGradient id="apt-floor" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#c4c8cf" />
            <stop offset="100%" stopColor="#7e8593" />
          </linearGradient>
          <linearGradient id="apt-wall" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#5a6f8e" />
            <stop offset="100%" stopColor="#2e3b54" />
          </linearGradient>
          <linearGradient id="apt-window" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#a8c5e0" />
            <stop offset="100%" stopColor="#dae5ef" />
          </linearGradient>
        </defs>

        <rect x="0" y="0" width="1080" height="1080" fill="url(#apt-wall)" />

        <rect x="60" y="220" width="280" height="600" fill="url(#apt-window)" rx="8" />
        <rect x="400" y="220" width="280" height="600" fill="url(#apt-window)" rx="8" />
        <rect x="740" y="220" width="280" height="600" fill="url(#apt-window)" rx="8" />
        <line x1="200" y1="220" x2="200" y2="820" stroke="#1a1a1e" strokeWidth="6" />
        <line x1="540" y1="220" x2="540" y2="820" stroke="#1a1a1e" strokeWidth="6" />
        <line x1="880" y1="220" x2="880" y2="820" stroke="#1a1a1e" strokeWidth="6" />

        <g transform="translate(120, 380)">
          <rect width="200" height="80" rx="10" fill="#fff" stroke="#1a1a1e" strokeWidth="6" />
          <line x1="20" y1="22" x2="20" y2="58" stroke="#1a1a1e" strokeWidth="4" />
          <rect x="40" y="20" width="60" height="14" fill="#1a1a1e" />
          <rect x="40" y="40" width="100" height="10" fill="#1a1a1e" opacity="0.7" />
          <rect x="40" y="55" width="80" height="8" fill="#1a1a1e" opacity="0.5" />
        </g>

        <rect x="0" y="900" width="1080" height="60" fill="#1a1a1e" />
        <rect x="0" y="960" width="1080" height="60" fill="#f5d35a" />
        <text
          x="540" y="1003"
          textAnchor="middle"
          fontFamily="ui-rounded, system-ui, sans-serif"
          fontSize="42"
          fontWeight="900"
          fill="#1a1a1e"
        >
          NOW BOARDING — GATE 7
        </text>

        <rect x="0" y="1020" width="1080" height="900" fill="url(#apt-floor)" />

        <g stroke="#1a1a1e" strokeWidth="6" fill="none" opacity="0.55">
          <line x1="120" y1="1140" x2="960" y2="1140" />
          <line x1="120" y1="1140" x2="120" y2="1840" />
          <line x1="960" y1="1140" x2="960" y2="1840" />
          <line x1="120" y1="1840" x2="960" y2="1840" />
        </g>
        <g stroke="#1a1a1e" strokeWidth="4" strokeDasharray="14 10" opacity="0.7">
          <line x1="120" y1="1280" x2="960" y2="1280" />
          <line x1="120" y1="1420" x2="960" y2="1420" />
          <line x1="120" y1="1560" x2="960" y2="1560" />
          <line x1="120" y1="1700" x2="960" y2="1700" />
        </g>
        <g fontFamily="ui-rounded, system-ui, sans-serif" fontSize="46" fontWeight="900" fill="#1a1a1e" opacity="0.5">
          <text x="540" y="1220" textAnchor="middle">GROUP 1</text>
          <text x="540" y="1360" textAnchor="middle">GROUP 2</text>
          <text x="540" y="1500" textAnchor="middle">GROUP 3</text>
          <text x="540" y="1640" textAnchor="middle">GROUP 4</text>
          <text x="540" y="1780" textAnchor="middle">GROUP 5</text>
        </g>
      </svg>
    </AbsoluteFill>
  );
};
