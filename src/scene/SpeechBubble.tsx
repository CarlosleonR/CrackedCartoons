import React from "react";

export type SpeechBubbleProps = {
  text: string;
  x: number;
  y: number;
  width?: number;
  scale?: number;
  tailDirection?: "left" | "right" | "down";
  fontSize?: number;
  rotate?: number;
};

export const SpeechBubble: React.FC<SpeechBubbleProps> = ({
  text,
  x,
  y,
  width = 520,
  scale = 1,
  tailDirection = "left",
  fontSize = 56,
  rotate = 0,
}) => {
  const lines = text.split("\n");
  const lineHeight = fontSize * 1.15;
  const padY = 32;
  const height = padY * 2 + lineHeight * lines.length;

  const tail =
    tailDirection === "left"
      ? `M 60 ${height - 10} L 20 ${height + 50} L 110 ${height - 10} Z`
      : tailDirection === "right"
      ? `M ${width - 60} ${height - 10} L ${width - 20} ${height + 50} L ${width - 110} ${height - 10} Z`
      : `M ${width / 2 - 30} ${height - 10} L ${width / 2} ${height + 50} L ${width / 2 + 30} ${height - 10} Z`;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `scale(${scale}) rotate(${rotate}deg)`,
        transformOrigin: "top left",
      }}
    >
      <svg width={width} height={height + 60} style={{ overflow: "visible" }}>
        <rect
          x="0"
          y="0"
          width={width}
          height={height}
          rx="36"
          fill="#fff"
          stroke="#1a1a1e"
          strokeWidth="6"
        />
        <path d={tail} fill="#fff" stroke="#1a1a1e" strokeWidth="6" strokeLinejoin="round" />
        {lines.map((line, i) => (
          <text
            key={i}
            x={width / 2}
            y={padY + lineHeight * (i + 0.8)}
            textAnchor="middle"
            fontSize={fontSize}
            fontWeight="800"
            fill="#1a1a1e"
            fontFamily="ui-rounded, system-ui, -apple-system, 'Helvetica Neue', sans-serif"
          >
            {line}
          </text>
        ))}
      </svg>
    </div>
  );
};
