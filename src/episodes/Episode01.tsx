import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  Easing,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { TheRock } from "../characters/TheRock";
import { Child } from "../characters/Child";
import { Sandwich } from "../scene/Sandwich";
import { PicnicBackground } from "../scene/PicnicBackground";
import { SpeechBubble } from "../scene/SpeechBubble";

const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();

  const bgFlash = interpolate(frame, [0, 4], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const titleY = interpolate(frame, [4, 18], [-200, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const titleScale = interpolate(frame, [10, 22, 28], [1, 1.08, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const subtitleOpacity = interpolate(frame, [22, 32], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const rockX = interpolate(frame, [40, 64], [1300, 540], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const rockBob = Math.sin((frame - 40) * 0.4) * 8;
  const rockRot = interpolate(frame, [40, 64], [-120, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const fadeOut = interpolate(frame, [78, 90], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const browWiggle = Math.sin((frame - 64) * 0.5) * 8;

  return (
    <AbsoluteFill style={{ opacity: fadeOut, backgroundColor: "#1a1a1e" }}>
      <AbsoluteFill style={{ opacity: bgFlash, backgroundColor: "#f5d35a" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            transform: `translateY(${titleY}px) scale(${titleScale})`,
            textAlign: "center",
            fontFamily: "ui-rounded, system-ui, -apple-system, sans-serif",
          }}
        >
          <div
            style={{
              fontSize: 140,
              fontWeight: 900,
              color: "#1a1a1e",
              lineHeight: 1,
              letterSpacing: -4,
              textShadow: "8px 8px 0 #d94a3a",
            }}
          >
            THE ROCK
          </div>
          <div
            style={{
              fontSize: 96,
              fontWeight: 900,
              color: "#1a1a1e",
              lineHeight: 1,
              letterSpacing: -3,
              marginTop: 14,
            }}
          >
            HAS THOUGHTS
          </div>
          <div
            style={{
              opacity: subtitleOpacity,
              fontSize: 56,
              fontWeight: 700,
              color: "#1a1a1e",
              marginTop: 38,
            }}
          >
            Ep. 1 — The Picnic
          </div>
        </div>
        <div style={{ height: 60 }} />
        <div style={{ position: "relative", width: 1080, height: 600 }}>
          <TheRock
            x={rockX - 200}
            y={140 + rockBob}
            scale={2.4}
            bodyRotate={rockRot}
            browAngle={20 + browWiggle}
            mouthCurve={-0.4}
            mouthOpen={0.05}
            pupilX={0.2}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

type RockArrivalProps = { totalFrames: number };
const RockArrival: React.FC<RockArrivalProps> = ({ totalFrames }) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [0, 50], [1400, 540], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const rot = interpolate(frame, [0, 50], [-720, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const settle = Math.sin(Math.max(0, frame - 50) * 0.4) * Math.max(0, 1 - (frame - 50) / 30) * 22;
  const labelIn = interpolate(frame, [60, 78], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const labelOut = interpolate(frame, [totalFrames - 12, totalFrames], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <AbsoluteFill>
      <PicnicBackground />
      <Sandwich variant="classic" x={140} y={1380} scale={1.4} rotate={-4} />
      <Sandwich variant="tall" x={460} y={1340} scale={1.4} rotate={2} />
      <Sandwich variant="weird" x={740} y={1380} scale={1.4} rotate={-1} />

      <TheRock
        x={enter - 220}
        y={1100 + settle}
        scale={3.2}
        bodyRotate={rot}
        browAngle={14}
        mouthCurve={-0.3}
        mouthOpen={0.1}
      />

      <div
        style={{
          position: "absolute",
          top: 200,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: labelIn * labelOut,
          fontFamily: "ui-rounded, system-ui, sans-serif",
          fontSize: 92,
          fontWeight: 900,
          color: "#fff",
          letterSpacing: -2,
          textShadow: "6px 6px 0 #1a1a1e",
        }}
      >
        UNINVITED
      </div>
    </AbsoluteFill>
  );
};

type RatingBeatProps = {
  variant: "classic" | "tall" | "weird";
  quote: string;
  score: string;
};

const RatingBeat: React.FC<RatingBeatProps> = ({ variant, quote, score }) => {
  const frame = useCurrentFrame();

  const sandwichScale = interpolate(frame, [0, 14, 22], [0.4, 2.6, 2.4], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const sandwichY = interpolate(frame, [0, 14], [1200, 720], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const shake = Math.sin(frame * 0.9) * (frame > 30 && frame < 60 ? 8 : 0);

  const bubbleIn = interpolate(frame, [18, 30], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const bubbleOut = interpolate(frame, [78, 88], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const bubbleScale = bubbleIn * bubbleOut;

  const scoreIn = interpolate(frame, [56, 68, 80], [0, 1.25, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const scoreOut = interpolate(frame, [82, 90], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  const mouthOpen = (Math.sin(frame * 0.7) + 1) / 2;
  const rockBob = Math.sin(frame * 0.25) * 8;

  return (
    <AbsoluteFill>
      <PicnicBackground />

      <div style={{ transform: `translate(${shake}px, 0)` }}>
        <Sandwich variant={variant} x={540 - 200} y={sandwichY} scale={sandwichScale} />
      </div>

      <TheRock
        x={120}
        y={1280 + rockBob}
        scale={2.4}
        browAngle={26}
        mouthCurve={-0.5}
        mouthOpen={frame > 18 && frame < 80 ? mouthOpen : 0.05}
        pupilX={0.5}
        pupilY={-0.3}
      />

      <div style={{ transform: `scale(${bubbleScale})`, transformOrigin: "left top" }}>
        <SpeechBubble
          text={quote}
          x={360}
          y={1180}
          width={620}
          tailDirection="left"
          fontSize={52}
        />
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 320,
          textAlign: "center",
          opacity: scoreOut,
          transform: `scale(${scoreIn})`,
          fontFamily: "ui-rounded, system-ui, sans-serif",
          fontSize: 180,
          fontWeight: 900,
          color: "#d94a3a",
          letterSpacing: -6,
          textShadow: "10px 10px 0 #1a1a1e",
        }}
      >
        {score}
      </div>
    </AbsoluteFill>
  );
};

const ChildArgument: React.FC = () => {
  const frame = useCurrentFrame();

  const rockBob = Math.sin(frame * 0.22) * 6;
  const childIn = interpolate(frame, [0, 18], [400, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });

  type Beat = {
    start: number;
    end: number;
    speaker: "child" | "rock";
    text: string;
    childMouth?: number;
    childBrow?: number;
    childArm?: number;
    rockMouth?: number;
    rockBrow?: number;
    rockCurve?: number;
    bubbleSide?: "left" | "right";
  };

  const beats: Beat[] = [
    {
      start: 14,
      end: 70,
      speaker: "child",
      text: "THAT'S MY\nSANDWICH!!",
      childMouth: 0.9,
      childBrow: 30,
      childArm: 1,
      bubbleSide: "right",
    },
    {
      start: 78,
      end: 144,
      speaker: "rock",
      text: "THEN YOU HAVE\nBAD TASTE.",
      rockMouth: 0.85,
      rockBrow: 28,
      rockCurve: -0.6,
      bubbleSide: "left",
    },
    {
      start: 152,
      end: 210,
      speaker: "child",
      text: "YOU'RE\nA ROCK!!",
      childMouth: 0.95,
      childBrow: 36,
      childArm: 0.9,
      bubbleSide: "right",
    },
    {
      start: 218,
      end: 280,
      speaker: "rock",
      text: "I AM A\nCONNOISSEUR.",
      rockMouth: 0.7,
      rockBrow: 18,
      rockCurve: -0.2,
      bubbleSide: "left",
    },
    {
      start: 290,
      end: 330,
      speaker: "child",
      text: "ROCKS DON'T\nHAVE MOUTHS.",
      childMouth: 0.6,
      childBrow: 4,
      childArm: 0.1,
      bubbleSide: "right",
    },
  ];

  const activeBeat = beats.find((b) => frame >= b.start && frame <= b.end);
  const lastFinishedBeat = [...beats].reverse().find((b) => frame > b.end);

  const lipFlap = (Math.sin(frame * 0.9) + 1) / 2;
  const dotsFrame = Math.max(0, frame - 330);
  const showRockShock = frame > 330;
  const dotCount = Math.min(3, Math.floor(dotsFrame / 14));

  let rockMouthVal = 0.05;
  let rockBrowVal = 16;
  let rockCurveVal = -0.4;
  let rockEyeX = 0;
  let rockPupilTwitch = 0;
  let childMouthVal = 0;
  let childBrowVal = 4;
  let childArmVal = 0;

  if (activeBeat?.speaker === "rock") {
    rockMouthVal = (activeBeat.rockMouth ?? 0.6) * lipFlap;
    rockBrowVal = activeBeat.rockBrow ?? 16;
    rockCurveVal = activeBeat.rockCurve ?? -0.4;
  } else if (lastFinishedBeat?.speaker === "rock") {
    rockBrowVal = lastFinishedBeat.rockBrow ?? 16;
    rockCurveVal = lastFinishedBeat.rockCurve ?? -0.4;
  }
  if (activeBeat?.speaker === "child") {
    childMouthVal = (activeBeat.childMouth ?? 0.6) * lipFlap;
    childBrowVal = activeBeat.childBrow ?? 4;
    childArmVal = activeBeat.childArm ?? 0;
    rockEyeX = -0.3;
  }
  if (showRockShock) {
    rockBrowVal = -8;
    rockCurveVal = 0;
    rockMouthVal = 0;
    rockPupilTwitch = Math.sin(dotsFrame * 0.6) * 0.4;
    rockEyeX = rockPupilTwitch;
  }

  const bubble = activeBeat ? (
    <SpeechBubble
      text={activeBeat.text}
      x={activeBeat.bubbleSide === "left" ? 40 : 500}
      y={activeBeat.bubbleSide === "left" ? 880 : 660}
      width={560}
      tailDirection="down"
      fontSize={58}
    />
  ) : null;

  const bubbleEnterScale = activeBeat
    ? interpolate(frame, [activeBeat.start, activeBeat.start + 8], [0, 1], {
        extrapolateRight: "clamp",
        extrapolateLeft: "clamp",
        easing: easeOut,
      })
    : 0;
  const bubbleExitScale = activeBeat
    ? interpolate(frame, [activeBeat.end - 6, activeBeat.end], [1, 0], {
        extrapolateRight: "clamp",
        extrapolateLeft: "clamp",
      })
    : 0;

  return (
    <AbsoluteFill>
      <PicnicBackground />
      <Sandwich variant="classic" x={420} y={1500} scale={1.0} rotate={-2} />

      <TheRock
        x={80}
        y={1180 + rockBob}
        scale={2.4}
        browAngle={rockBrowVal}
        mouthCurve={rockCurveVal}
        mouthOpen={rockMouthVal}
        pupilX={rockEyeX}
        pupilY={showRockShock ? 0.4 : -0.1}
      />

      <Child
        x={620 + childIn}
        y={970}
        scale={1.6}
        mouthOpen={childMouthVal}
        browAngle={childBrowVal}
        armUp={childArmVal}
      />

      <div
        style={{
          transform: `scale(${bubbleEnterScale * bubbleExitScale})`,
          transformOrigin: "center center",
        }}
      >
        {bubble}
      </div>

      {showRockShock && (
        <div
          style={{
            position: "absolute",
            left: 200,
            top: 1090,
            fontFamily: "ui-rounded, system-ui, sans-serif",
            fontSize: 96,
            fontWeight: 900,
            color: "#1a1a1e",
            letterSpacing: 8,
          }}
        >
          {".".repeat(dotCount)}
        </div>
      )}
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const frame = useCurrentFrame();

  const flash = interpolate(frame, [0, 6], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const cardY = interpolate(frame, [4, 22], [-300, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const cardScale = interpolate(frame, [18, 30, 38], [1, 1.12, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeInOut,
  });
  const subIn = interpolate(frame, [38, 54], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const tagIn = interpolate(frame, [70, 90], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: easeOut,
  });
  const rockShake = Math.sin(frame * 0.4) * 4;

  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a1e" }}>
      <AbsoluteFill style={{ opacity: flash, backgroundColor: "#f5d35a" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            transform: `translateY(${cardY}px) scale(${cardScale})`,
            textAlign: "center",
            fontFamily: "ui-rounded, system-ui, sans-serif",
          }}
        >
          <div
            style={{
              fontSize: 200,
              fontWeight: 900,
              color: "#1a1a1e",
              lineHeight: 0.9,
              letterSpacing: -8,
              textShadow: "10px 10px 0 #d94a3a",
            }}
          >
            NOBODY
          </div>
          <div
            style={{
              fontSize: 200,
              fontWeight: 900,
              color: "#1a1a1e",
              lineHeight: 0.9,
              letterSpacing: -8,
              marginTop: 10,
              textShadow: "10px 10px 0 #d94a3a",
            }}
          >
            WON.
          </div>
          <div
            style={{
              opacity: subIn,
              fontSize: 56,
              fontWeight: 800,
              color: "#1a1a1e",
              marginTop: 60,
            }}
          >
            (the rock is still talking)
          </div>
        </div>

        <div style={{ height: 80 }} />
        <div style={{ position: "relative", width: 1080, height: 280 }}>
          <TheRock
            x={420 + rockShake}
            y={20}
            scale={1.6}
            browAngle={22}
            mouthCurve={-0.5}
            mouthOpen={(Math.sin(frame * 0.8) + 1) / 2 * 0.6}
          />
        </div>

        <div
          style={{
            opacity: tagIn,
            fontSize: 48,
            fontWeight: 800,
            color: "#1a1a1e",
            fontFamily: "ui-rounded, system-ui, sans-serif",
            marginTop: 40,
          }}
        >
          subscribe for more bad opinions
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

type AudioClip = { from: number; file: string; volume?: number };

const VO_CLIPS: AudioClip[] = [
  { from: 198, file: "audio/rock_aioli.mp3" },
  { from: 288, file: "audio/rock_too_tall.mp3" },
  { from: 378, file: "audio/rock_what_is_this.mp3" },
  { from: 464, file: "audio/kid_my_sandwich.mp3" },
  { from: 528, file: "audio/rock_bad_taste.mp3" },
  { from: 602, file: "audio/kid_youre_a_rock.mp3" },
  { from: 668, file: "audio/rock_connoisseur.mp3" },
  { from: 740, file: "audio/kid_no_mouths.mp3" },
];

const SFX_CLIPS: AudioClip[] = [
  { from: 4,   file: "sfx/title_impact.mp3",   volume: 0.7 },
  { from: 90,  file: "sfx/rock_arrival.mp3",   volume: 0.55 },
  { from: 232, file: "sfx/stamp_ding.mp3",     volume: 0.6 },
  { from: 322, file: "sfx/stamp_ding.mp3",     volume: 0.6 },
  { from: 412, file: "sfx/stamp_ding.mp3",     volume: 0.6 },
  { from: 452, file: "sfx/kid_gasp.mp3",       volume: 0.5 },
  { from: 778, file: "sfx/record_scratch.mp3", volume: 0.65 },
  { from: 800, file: "sfx/sad_trombone.mp3",   volume: 0.55 },
];

export const Episode01: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#9bd6ee" }}>
      <Sequence durationInFrames={90} layout="none">
        <TitleCard />
      </Sequence>
      <Sequence from={90} durationInFrames={90} layout="none">
        <RockArrival totalFrames={90} />
      </Sequence>
      <Sequence from={180} durationInFrames={90} layout="none">
        <RatingBeat
          variant="classic"
          quote={"NO AIOLI?\nDISGRACE."}
          score="0/10"
        />
      </Sequence>
      <Sequence from={270} durationInFrames={90} layout="none">
        <RatingBeat
          variant="tall"
          quote={"TOO TALL.\nUNHINGED."}
          score="2/10"
        />
      </Sequence>
      <Sequence from={360} durationInFrames={90} layout="none">
        <RatingBeat
          variant="weird"
          quote={"WHAT IS THIS?\nGET IT AWAY."}
          score="-3/10"
        />
      </Sequence>
      <Sequence from={450} durationInFrames={330} layout="none">
        <ChildArgument />
      </Sequence>
      <Sequence from={780} durationInFrames={120} layout="none">
        <Outro />
      </Sequence>

      {VO_CLIPS.map((clip) => (
        <Sequence key={clip.file} from={clip.from} layout="none">
          <Audio src={staticFile(clip.file)} volume={clip.volume ?? 1} />
        </Sequence>
      ))}
      {SFX_CLIPS.map((clip, i) => (
        <Sequence key={`${clip.file}-${i}`} from={clip.from} layout="none">
          <Audio src={staticFile(clip.file)} volume={clip.volume ?? 0.6} />
        </Sequence>
      ))}

      <Sequence from={812} layout="none">
        <DistantRockRant />
      </Sequence>
    </AbsoluteFill>
  );
};

const DistantRockRant: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fadeIn = interpolate(frame, [0, fps * 0.5], [0, 0.22], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  return (
    <Audio
      src={staticFile("audio/rock_outro_mutter.mp3")}
      volume={fadeIn}
      playbackRate={0.92}
      startFrom={Math.round(fps * 1.2)}
    />
  );
};
