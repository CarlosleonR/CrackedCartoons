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

        {/* Distant passenger queue silhouettes — far back, behind the action */}
        <g opacity="0.55">
          {/* a row of small passengers along the back wall */}
          <Passenger x={140} y={840} skin="#e6c39b" shirt="#3aa67a" />
          <Passenger x={210} y={830} skin="#c69a6a" shirt="#c44a3a" rolling />
          <Passenger x={280} y={845} skin="#f0d4b0" shirt="#3a4ac4" />
          <Passenger x={350} y={835} skin="#a87c4e" shirt="#caa44a" rolling />
          <Passenger x={420} y={840} skin="#e6c39b" shirt="#7e8593" />
          <Passenger x={770} y={835} skin="#d8b48a" shirt="#5a6f8e" rolling />
          <Passenger x={840} y={840} skin="#c69a6a" shirt="#9b6cc4" />
          <Passenger x={910} y={830} skin="#f0d4b0" shirt="#3aa67a" />
        </g>

        {/* A few rolling suitcases sitting at the gate */}
        <Suitcase x={70} y={870} hue="#3a4ac4" />
        <Suitcase x={970} y={865} hue="#c44a3a" />

        {/* "Other rocks behind them" — small grey rocks scattered along the floor */}
        <SmallRock cx={260} cy={1860} r={22} />
        <SmallRock cx={760} cy={1850} r={18} />
        <SmallRock cx={870} cy={1870} r={28} />
      </svg>
    </AbsoluteFill>
  );
};

/* ---------- helper sub-components inside the SVG ---------- */

const Passenger: React.FC<{ x: number; y: number; skin: string; shirt: string; rolling?: boolean }> = ({
  x, y, skin, shirt, rolling,
}) => (
  <g transform={`translate(${x} ${y})`}>
    {/* head */}
    <circle cx="0" cy="0" r="11" fill={skin} stroke="#1a1a1e" strokeWidth="1.5" />
    {/* torso */}
    <rect x="-12" y="11" width="24" height="34" rx="4" fill={shirt} stroke="#1a1a1e" strokeWidth="1.5" />
    {/* legs */}
    <rect x="-10" y="44" width="8" height="20" rx="2" fill="#2e3b54" />
    <rect x="2" y="44" width="8" height="20" rx="2" fill="#2e3b54" />
    {rolling && (
      <>
        {/* pull-handle */}
        <line x1="14" y1="22" x2="22" y2="32" stroke="#1a1a1e" strokeWidth="2" />
        {/* small suitcase */}
        <rect x="20" y="32" width="14" height="22" rx="2" fill="#caa44a" stroke="#1a1a1e" strokeWidth="1.5" />
      </>
    )}
  </g>
);

const Suitcase: React.FC<{ x: number; y: number; hue: string }> = ({ x, y, hue }) => (
  <g transform={`translate(${x} ${y})`} opacity="0.85">
    <rect x="0" y="0" width="38" height="56" rx="5" fill={hue} stroke="#1a1a1e" strokeWidth="3" />
    <rect x="14" y="-10" width="10" height="14" fill="#1a1a1e" />
    <line x1="0" y1="20" x2="38" y2="20" stroke="#1a1a1e" strokeWidth="2" />
    <circle cx="6" cy="56" r="3" fill="#1a1a1e" />
    <circle cx="32" cy="56" r="3" fill="#1a1a1e" />
  </g>
);

const SmallRock: React.FC<{ cx: number; cy: number; r: number }> = ({ cx, cy, r }) => (
  <g>
    <ellipse cx={cx} cy={cy + r * 0.7} rx={r * 1.1} ry={r * 0.25} fill="rgba(0,0,0,0.25)" />
    <circle cx={cx} cy={cy} r={r} fill="#7a7a82" stroke="#3d3d44" strokeWidth="2" />
    <circle cx={cx - r * 0.35} cy={cy - r * 0.25} r={r * 0.18} fill="#5a5a62" opacity="0.6" />
  </g>
);
