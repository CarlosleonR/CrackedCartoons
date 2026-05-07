// TypeScript mirrors of pipeline/schemas/script.py.
// Hand-maintained; if you change the Pydantic schema, update here too.

export type Speaker = "rock" | "kid" | "narrator" | "other";
export type Emotion =
  | "smug" | "angry" | "indignant" | "confused" | "deadpan"
  | "shocked" | "excited" | "sad" | "hostile";

export type SceneType =
  | "title_card"
  | "character_entrance"
  | "rating_beat"
  | "dialogue_exchange"
  | "reaction_beat"
  | "montage"
  | "outro";

export type DialogueLine = {
  speaker: Speaker;
  text: string;
  on_screen_text?: string | null;
  emotion?: Emotion | null;
  start_frame: number;
  estimated_duration_frames: number;
  scene_id: string;
  /** Filled in by ProductionAgent before writing public/scripts/<id>.json */
  audio_src?: string;
};

export type SFXCue = {
  description: string;
  start_frame: number;
  duration_seconds: number;
  volume: number;
  scene_id: string;
  reuse_key?: string | null;
  audio_src?: string;
};

export type Scene = {
  id: string;
  type: SceneType;
  start_frame: number;
  duration_frames: number;
  description: string;
  props: Record<string, unknown>;
  visual_notes?: string | null;
};

export type EpisodeScriptJSON = {
  episode_id: string;
  title: string;
  logline: string;
  fps: number;
  width: number;
  height: number;
  total_frames: number;
  structure: string;
  scenes: Scene[];
  voiceover: DialogueLine[];
  sfx: SFXCue[];
  thumbnail_concept: string;
};
