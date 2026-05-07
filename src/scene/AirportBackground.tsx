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

        <rect x="60" y="220" width="280" height="540" fill="url(#apt-window)" rx="8" />
        <rect x="400" y="220" width="280" height="540" fill="url(#apt-window)" rx="8" />
        <rect x="740" y="220" width="280" height="540" fill="url(#apt-window)" rx="8" />
        <line x1="200" y1="220" x2="200" y2="760" stroke="#1a1a1e" strokeWidth="6" />
        <line x1="540" y1="220" x2="540" y2="760" stroke="#1a1a1e" strokeWidth="6" />
        <line x1="880" y1="220" x2="880" y2="760" stroke="#1a1a1e" strokeWidth="6" />

        {/* Tarmac visible through the windows */}
        <rect x="60" y="600" width="960" height="160" fill="#3d3d44" opacity="0.55" />

        {/* Plane #1 — center window, tail visible */}
        <g transform="translate(480, 470)">
          <ellipse cx="0" cy="120" rx="180" ry="14" fill="#1a1a1e" opacity="0.25" />
          <path d="M -160 100 Q -180 80, -150 70 L 150 70 Q 180 80, 170 100 L 150 110 Q 0 120, -150 110 Z"
                fill="#fff" stroke="#1a1a1e" strokeWidth="3" />
          <rect x="-90" y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="-70" y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="-50" y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="-30" y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="-10" y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="10"  y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="30"  y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="50"  y="80" width="6" height="6" fill="#a8c5e0" />
          <rect x="70"  y="80" width="6" height="6" fill="#a8c5e0" />
          <path d="M 130 70 L 165 30 L 175 30 L 155 70 Z" fill="#fff" stroke="#1a1a1e" strokeWidth="3" />
          <path d="M -160 100 Q -190 90, -200 130 L -160 130 Z" fill="#caa44a" stroke="#1a1a1e" strokeWidth="2" />
          <path d="M 160 100 Q 190 90, 200 130 L 160 130 Z" fill="#caa44a" stroke="#1a1a1e" strokeWidth="2" />
        </g>

        {/* Plane #2 — distant in right window */}
        <g transform="translate(880, 540) scale(0.55)">
          <path d="M -120 100 Q -140 88, -110 78 L 110 78 Q 140 88, 130 100 L -110 100 Z"
                fill="#fff" stroke="#1a1a1e" strokeWidth="3" opacity="0.85" />
          <path d="M 110 78 L 140 50 L 148 50 L 130 78 Z" fill="#fff" stroke="#1a1a1e" strokeWidth="3" opacity="0.85" />
        </g>

        {/* Departures sign on the wall */}
        <g transform="translate(120, 100)">
          <rect width="320" height="92" rx="8" fill="#1a1a1e" stroke="#caa44a" strokeWidth="3" />
          <text x="160" y="42" textAnchor="middle" fontFamily="ui-rounded, system-ui, sans-serif"
                fontSize="24" fontWeight="700" fill="#caa44a">DEPARTURES</text>
          <line x1="14" y1="50" x2="306" y2="50" stroke="#caa44a" strokeWidth="1" />
          <text x="22"  y="74" fontFamily="monospace" fontSize="18" fontWeight="700" fill="#f5d35a">JFK 14:20  ON TIME</text>
        </g>

        {/* Terminal banner sign hanging from ceiling — TERMINAL B with arrow */}
        <g transform="translate(640, 90)">
          <rect width="380" height="100" rx="6" fill="#caa44a" stroke="#1a1a1e" strokeWidth="4" />
          <text x="120" y="68" textAnchor="middle" fontFamily="ui-rounded, system-ui, sans-serif"
                fontSize="48" fontWeight="900" fill="#1a1a1e">TERMINAL B</text>
          <path d="M 280 50 L 340 50 L 340 36 L 360 60 L 340 84 L 340 70 L 280 70 Z"
                fill="#1a1a1e" />
        </g>

        {/* Gate counter / podium with screen */}
        <g transform="translate(60, 760)">
          <rect width="380" height="120" rx="6" fill="#caa44a" stroke="#1a1a1e" strokeWidth="4" />
          <rect x="14" y="14" width="160" height="80" rx="4" fill="#1a1a1e" />
          <text x="94" y="48" textAnchor="middle" fontFamily="monospace" fontSize="14" fontWeight="700" fill="#7eff7e">GATE  B7</text>
          <text x="94" y="68" textAnchor="middle" fontFamily="monospace" fontSize="13" fontWeight="700" fill="#7eff7e">BOARDING</text>
          <text x="94" y="84" textAnchor="middle" fontFamily="monospace" fontSize="13" fontWeight="700" fill="#7eff7e">GROUP 4</text>
          <rect x="200" y="20" width="160" height="20" rx="2" fill="#1a1a1e" opacity="0.4" />
          <rect x="200" y="48" width="120" height="14" rx="2" fill="#1a1a1e" opacity="0.4" />
          <rect x="200" y="68" width="140" height="14" rx="2" fill="#1a1a1e" opacity="0.4" />
        </g>

        {/* Jetway / boarding bridge entrance — right side */}
        <g transform="translate(720, 760)">
          <rect width="300" height="120" rx="6" fill="#7e8593" stroke="#1a1a1e" strokeWidth="4" />
          <rect x="20" y="20" width="80" height="80" rx="4" fill="#caa44a" stroke="#1a1a1e" strokeWidth="3" />
          <path d="M 60 30 L 60 90 M 40 60 L 80 60" stroke="#1a1a1e" strokeWidth="3" fill="none" />
          <text x="200" y="58" textAnchor="middle" fontFamily="ui-rounded, system-ui, sans-serif"
                fontSize="34" fontWeight="900" fill="#1a1a1e">JETWAY</text>
          <text x="200" y="92" textAnchor="middle" fontFamily="ui-rounded, system-ui, sans-serif"
                fontSize="22" fontWeight="700" fill="#1a1a1e" opacity="0.7">→ to plane</text>
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
          NOW BOARDING — GATE B7
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

        {/* Passenger queue between the gate counter (x<440) and the jetway (x>720) */}
        <g opacity="0.55">
          <Passenger x={470} y={830} skin="#e6c39b" shirt="#3aa67a" />
          <Passenger x={510} y={840} skin="#c69a6a" shirt="#c44a3a" rolling />
          <Passenger x={555} y={835} skin="#f0d4b0" shirt="#3a4ac4" />
          <Passenger x={600} y={845} skin="#a87c4e" shirt="#caa44a" rolling />
          <Passenger x={650} y={840} skin="#e6c39b" shirt="#7e8593" />
          <Passenger x={695} y={835} skin="#d8b48a" shirt="#5a6f8e" />
        </g>

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

const SmallRock: React.FC<{ cx: number; cy: number; r: number }> = ({ cx, cy, r }) => (
  <g>
    <ellipse cx={cx} cy={cy + r * 0.7} rx={r * 1.1} ry={r * 0.25} fill="rgba(0,0,0,0.25)" />
    <circle cx={cx} cy={cy} r={r} fill="#7a7a82" stroke="#3d3d44" strokeWidth="2" />
    <circle cx={cx - r * 0.35} cy={cy - r * 0.25} r={r * 0.18} fill="#5a5a62" opacity="0.6" />
  </g>
);
