import "./index.css";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { Episode01 } from "./episodes/Episode01";
import { Thumbnail01 } from "./episodes/Thumbnail01";
import {
  EpisodeFromScript,
  EpisodeFromScriptProps,
} from "./episodes/EpisodeFromScript";
import {
  ThumbnailFromScript,
  ThumbnailFromScriptProps,
  ThumbnailSpecJSON,
} from "./episodes/ThumbnailFromScript";
import type { EpisodeScriptJSON } from "./scenes/types";

const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1920;
const DURATION_SECONDS = 30;

type EpisodeRenderProps = EpisodeFromScriptProps & { scriptId?: string };

const calculateEpisodeMetadata: CalculateMetadataFunction<EpisodeRenderProps> = async ({
  props,
}) => {
  const scriptId = props.scriptId;
  if (!scriptId) {
    return {
      durationInFrames: 1,
      props: { ...props, script: null },
    };
  }
  const url = staticFile(`scripts/${scriptId}.json`);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch ${url}: ${res.status}`);
  }
  const script = (await res.json()) as EpisodeScriptJSON;
  return {
    durationInFrames: script.total_frames,
    fps: script.fps,
    width: script.width,
    height: script.height,
    props: { ...props, script },
  };
};

type ThumbnailRenderProps = ThumbnailFromScriptProps & { thumbnailId?: string };

const calculateThumbnailMetadata: CalculateMetadataFunction<ThumbnailRenderProps> = async ({
  props,
}) => {
  const id = props.thumbnailId;
  if (!id) {
    return { durationInFrames: 1, props: { ...props, spec: null } };
  }
  const url = staticFile(`thumbnails/${id}.json`);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  const spec = (await res.json()) as ThumbnailSpecJSON;
  return { durationInFrames: 1, props: { ...props, spec } };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Generic, script-driven composition used by Agent 3 (Production). */}
      <Composition
        id="Episode"
        component={EpisodeFromScript}
        durationInFrames={1}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{ scriptId: "Ep01-PicnicSandwiches", script: null } as EpisodeRenderProps}
        calculateMetadata={calculateEpisodeMetadata}
      />

      {/* Generic, spec-driven thumbnail used by Agent 5 (Publisher). */}
      <Composition
        id="Thumbnail"
        component={ThumbnailFromScript}
        durationInFrames={1}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{ thumbnailId: "Ep01-PicnicSandwiches", spec: null } as ThumbnailRenderProps}
        calculateMetadata={calculateThumbnailMetadata}
      />

      {/* Original hand-built Ep1 — kept as a regression reference. */}
      <Composition
        id="Ep01-PicnicSandwiches"
        component={Episode01}
        durationInFrames={DURATION_SECONDS * FPS}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ep01-Thumbnail"
        component={Thumbnail01}
        durationInFrames={1}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
