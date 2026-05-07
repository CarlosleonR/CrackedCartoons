import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { Child } from "../characters/Child";
import { Sandwich } from "../scene/Sandwich";
import { PicnicBackground } from "../scene/PicnicBackground";
import { SpeechBubble } from "../scene/SpeechBubble";
import { easeOut, lipFlap } from "./SceneTimingHelpers";
import type { DialogueLine } from "./types";

type Props = {
  participants?: string[];
  setting?: string;
};

export const DialogueExchangeScene: React.FC<{
  props: Props;
  duration: number;
  voiceover: DialogueLine[];
  sceneStartFrame: number;
}> = ({ voiceover, sceneStartFrame }) => {
  const frame = useCurrentFrame();
  const absFrame = sceneStartFrame + frame;

  const childIn = interpolate(frame, [0, 18], [400, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
  const rockBob = Math.sin(frame * 0.22) * 6;

  // Active line: whichever line covers absFrame.
  const activeLine = voiceover.find(
    (l) => absFrame >= l.start_frame && absFrame < l.start_frame + l.estimated_duration_frames
  );

  const flapAmt = lipFlap(frame, 0.9);
  const isRockTalking = activeLine?.speaker === "rock";
  const isKidTalking = activeLine?.speaker === "kid";

  const rockMouthOpen = isRockTalking ? 0.7 * flapAmt : 0.05;
  const rockBrow = isRockTalking ? 26 : 16;
  const rockCurve = isRockTalking ? -0.55 : -0.4;

  const kidMouthOpen = isKidTalking ? 0.85 * flapAmt : 0.05;
  const kidBrow = isKidTalking ? 30 : 6;
  const kidArm = isKidTalking ? 0.85 : 0;

  // Bubble pop-in / pop-out tied to the active line's window.
  let bubbleScale = 0;
  if (activeLine) {
    const localStart = activeLine.start_frame - sceneStartFrame;
    const localEnd = localStart + activeLine.estimated_duration_frames;
    const popIn = interpolate(frame, [localStart, localStart + 8], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut });
    const popOut = interpolate(frame, [localEnd - 6, localEnd], [1, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
    bubbleScale = popIn * popOut;
  }

  const bubbleText = activeLine?.on_screen_text ?? activeLine?.text ?? "";
  const bubbleX = isRockTalking ? 40 : 500;
  const bubbleY = isRockTalking ? 880 : 660;

  return (
    <AbsoluteFill>
      <PicnicBackground />
      <Sandwich variant="classic" x={420} y={1500} scale={1.0} rotate={-2} />

      <TheRock
        x={80}
        y={1180 + rockBob}
        scale={2.4}
        browAngle={rockBrow}
        mouthCurve={rockCurve}
        mouthOpen={rockMouthOpen}
        pupilX={isKidTalking ? -0.3 : 0}
        pupilY={-0.1}
      />

      <Child
        x={620 + childIn}
        y={970}
        scale={1.6}
        mouthOpen={kidMouthOpen}
        browAngle={kidBrow}
        armUp={kidArm}
      />

      {bubbleText && (
        <div style={{ transform: `scale(${bubbleScale})`, transformOrigin: "center center" }}>
          <SpeechBubble
            text={bubbleText}
            x={bubbleX}
            y={bubbleY}
            width={560}
            tailDirection="down"
            fontSize={58}
          />
        </div>
      )}
    </AbsoluteFill>
  );
};
