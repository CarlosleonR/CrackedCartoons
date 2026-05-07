import { Easing } from "remotion";
import type { DialogueLine } from "./types";

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

/** Convert an absolute episode frame into a scene-relative frame. */
export const toSceneFrame = (absoluteFrame: number, sceneStartFrame: number): number => {
  return absoluteFrame - sceneStartFrame;
};

/** True iff the given absolute frame is within [line.start, line.start+dur). */
export const isLineActive = (line: DialogueLine, absoluteFrame: number): boolean => {
  return (
    absoluteFrame >= line.start_frame &&
    absoluteFrame < line.start_frame + line.estimated_duration_frames
  );
};

/** Lip-flap amplitude 0..1 driven by sin so mouths move during VO. */
export const lipFlap = (frame: number, rate = 0.85): number => {
  return (Math.sin(frame * rate) + 1) / 2;
};
