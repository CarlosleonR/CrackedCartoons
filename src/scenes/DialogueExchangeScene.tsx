import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { TheRock } from "../characters/TheRock";
import { Sandwich } from "../scene/Sandwich";
import { SpeechBubble } from "../scene/SpeechBubble";
import { easeOut, lipFlap } from "./SceneTimingHelpers";
import { renderBackground, renderNpc } from "./registry";
import type { DialogueLine, Speaker } from "./types";

type Props = {
  participants?: Speaker[];
  setting?: string;
};

export const DialogueExchangeScene: React.FC<{
  props: Props;
  duration: number;
  voiceover: DialogueLine[];
  sceneStartFrame: number;
}> = ({ props, voiceover, sceneStartFrame }) => {
  const frame = useCurrentFrame();
  const absFrame = sceneStartFrame + frame;

  const setting = props.setting ?? "picnic";
  const participants = props.participants ?? ["rock", "kid"];
  const npcSpeaker: Speaker =
    (participants.find((p) => p !== "rock") as Speaker) ?? "other";

  const npcSlideIn = interpolate(frame, [0, 18], [400, 0], {
    extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut,
  });
  const rockBob = Math.sin(frame * 0.22) * 6;

  const activeLine = voiceover.find(
    (l) =>
      absFrame >= l.start_frame &&
      absFrame < l.start_frame + l.estimated_duration_frames,
  );

  const flapAmt = lipFlap(frame, 0.9);
  const isRockTalking = activeLine?.speaker === "rock";
  const isNpcTalking = activeLine && activeLine.speaker !== "rock";

  const rockMouthOpen = isRockTalking ? 0.7 * flapAmt : 0.05;
  const rockBrow = isRockTalking ? 26 : 16;
  const rockCurve = isRockTalking ? -0.55 : -0.4;

  const npcMouthOpen = isNpcTalking ? 0.85 * flapAmt : 0.05;
  const npcBrow = isNpcTalking ? 30 : 6;
  const npcArm = isNpcTalking ? 0.8 : 0;

  let bubbleScale = 0;
  if (activeLine) {
    const localStart = activeLine.start_frame - sceneStartFrame;
    const localEnd = localStart + activeLine.estimated_duration_frames;
    const popIn = interpolate(frame, [localStart, localStart + 8], [0, 1], {
      extrapolateRight: "clamp", extrapolateLeft: "clamp", easing: easeOut,
    });
    const popOut = interpolate(frame, [localEnd - 6, localEnd], [1, 0], {
      extrapolateRight: "clamp", extrapolateLeft: "clamp",
    });
    bubbleScale = popIn * popOut;
  }

  const bubbleText = activeLine?.on_screen_text ?? activeLine?.text ?? "";
  const bubbleX = isRockTalking ? 40 : 500;
  const bubbleY = isRockTalking ? 880 : 660;

  return (
    <AbsoluteFill>
      {renderBackground(setting)}

      {/* Picnic-only foreground prop. Don't litter airports with sandwiches. */}
      {setting === "picnic" && (
        <Sandwich variant="classic" x={420} y={1500} scale={1.0} rotate={-2} />
      )}

      <TheRock
        x={80}
        y={1180 + rockBob}
        scale={2.4}
        browAngle={rockBrow}
        mouthCurve={rockCurve}
        mouthOpen={rockMouthOpen}
        pupilX={isNpcTalking ? -0.3 : 0}
        pupilY={-0.1}
      />

      {renderNpc(npcSpeaker, setting, {
        x: 620 + npcSlideIn,
        y: 970,
        scale: 1.6,
        mouthOpen: npcMouthOpen,
        browAngle: npcBrow,
        armUp: npcArm,
      })}

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
