import React from "react";
import { AbsoluteFill } from "remotion";
import { TheRock } from "../characters/TheRock";
import { Sandwich } from "../scene/Sandwich";

export const Thumbnail01: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(circle at 30% 25%, #ffe066 0%, #f5b73a 65%, #d98b1f 100%)",
      }}
    >
      <svg
        viewBox="0 0 1080 1920"
        width={1080}
        height={1920}
        style={{ position: "absolute", inset: 0 }}
      >
        <g opacity="0.16" stroke="#1a1a1e" strokeWidth="14" fill="none">
          <line x1="-200" y1="200" x2="1280" y2="900" />
          <line x1="-200" y1="500" x2="1280" y2="1200" />
          <line x1="-200" y1="800" x2="1280" y2="1500" />
        </g>
      </svg>

      <div
        style={{
          position: "absolute",
          top: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: "ui-rounded, system-ui, sans-serif",
        }}
      >
        <div
          style={{
            display: "inline-block",
            padding: "14px 32px",
            background: "#1a1a1e",
            color: "#f5d35a",
            fontSize: 56,
            fontWeight: 900,
            letterSpacing: 2,
            transform: "rotate(-3deg)",
            border: "5px solid #1a1a1e",
            boxShadow: "10px 10px 0 #d94a3a",
          }}
        >
          EP. 1
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          top: 220,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: "ui-rounded, system-ui, sans-serif",
          fontSize: 200,
          fontWeight: 900,
          color: "#1a1a1e",
          lineHeight: 0.94,
          letterSpacing: -8,
          textShadow: "12px 12px 0 #d94a3a",
        }}
      >
        NOBODY
        <br />
        ASKED.
      </div>

      <div
        style={{
          position: "absolute",
          right: 80,
          top: 760,
          fontFamily: "ui-rounded, system-ui, sans-serif",
          fontSize: 64,
          fontWeight: 900,
          color: "#1a1a1e",
          background: "#fff",
          padding: "10px 20px",
          border: "5px solid #1a1a1e",
          transform: "rotate(4deg)",
          boxShadow: "6px 6px 0 #1a1a1e",
        }}
      >
        ← rates your sandwich
      </div>

      <div style={{ position: "absolute", left: 40, top: 980 }}>
        <TheRock
          scale={3.4}
          browAngle={28}
          mouthCurve={-0.55}
          mouthOpen={0.5}
          pupilX={0.6}
          pupilY={-0.15}
        />
      </div>

      <div style={{ position: "absolute", right: 60, top: 1200 }}>
        <div style={{ position: "relative", width: 440, height: 440 }}>
          <Sandwich variant="tall" scale={2.2} rotate={-4} />
          <div
            style={{
              position: "absolute",
              left: 80,
              top: -90,
              transform: "rotate(14deg)",
              fontFamily: "ui-rounded, system-ui, sans-serif",
              fontSize: 150,
              fontWeight: 900,
              color: "#d94a3a",
              letterSpacing: -4,
              WebkitTextStroke: "8px #1a1a1e",
              filter: "drop-shadow(6px 6px 0 #1a1a1e)",
            }}
          >
            0/10
          </div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 70,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: "ui-rounded, system-ui, sans-serif",
          fontSize: 52,
          fontWeight: 800,
          color: "#1a1a1e",
          letterSpacing: 1,
        }}
      >
        the rock has thoughts
      </div>
    </AbsoluteFill>
  );
};
