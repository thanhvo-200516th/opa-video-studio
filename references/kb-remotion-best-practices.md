# kb-remotion-best-practices — toàn văn tài liệu của nguồn `remotion-best-practices`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/remotion-best-practices/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: remotion-best-practices/SKILL.md ===== -->

---
name: remotion-best-practices
description: Router for all Remotion skills
version: 4.0.539
---

## Preserve user changes

Users may make edits in the code outside of the conversation.

If you detect a surprising change made in the meanwhile, don't overwrite it, assume it was intentional or ask for confirmation.

## Creating a video

If the user asks to make, create, or build a new video or composition, load [Create a new Remotion video](./remotion-create/REFERENCE.md), whether or not a Remotion project already exists.

## New project setup

If no Remotion project currently exists, load [Create a new Remotion project](./remotion-create/REFERENCE.md)

## React Markup Best Practices

If you are writing Remotion React Markup, load [Remotion Markup Best Practices](./remotion-markup/REFERENCE.md)

## Maps

For static maps, animated routes and markers, geographic explainers, Mapbox, MapLibre, MapTiler, GeoJSON, or 3D geographic flyovers, load [Remotion Maps](./remotion-maps/REFERENCE.md).

## Multimedia

For achieving multimedia tasks in the browser, such as trimming, cropping videos, or getting metadata from them, load [Remotion Multimedia](./remotion-multimedia/REFERENCE.md)

## Improving Interactivity

By structuring the Remotion markup well, we can allow users to interactively change things in the Studio and write back to code. If relevant: [Interactivity Best Practices](./remotion-interactivity/REFERENCE.md)

## Open the preview

If the user asks to "make" a video, "create" a video, etc.
Don't render the video by default unless they are very explicit. They want to instead see an interactive preview.
As soon as the project can run, start Studio and open the preview in the browser before building or editing the composition. Keep it open while you work so the user can watch progress and steer.

### If you are using Cursor

Run Studio without `--no-open` so it opens the browser automatically:

```bash
npx remotion studio
```

### If you are using another agent client with an in-app browser

You can use the command above to let Studio open the browser, or run:

```bash
npx remotion studio --no-open
```

This will start a long-running process and print the server URL for the preview.  
If the server is already started, it will print the URL.
If you use `--no-open`, open the exact printed URL in the in-app browser and verify that Studio loads. Once a composition exists, verify that its video preview loads. If you cannot open it there, run Studio without `--no-open`.
You can visit a specific composition by navigating to `/[composition-id]`, for example `http://localhost:3000/MapAnimation`.

:::note
The Studio supports WebMCP tools.
:::

### If you do not have an in-app browser

This will open the Studio in the browser or refocus it if it is already open.

```bash
npx remotion studio
```

### More options

To launch a project in Remotion Studio, open its exact local URL, or configure Studio CLI flags, load [Remotion Studio](./remotion-studio/REFERENCE.md).

## Render the video

Only render if the user is very explicit in asking for it.  
E.g. "Render the video", "Export", "Give me the MP4".

The preview also has a more intuitive rendering interface, so consider using it instead of the command line for rendering.

```
npx remotion render
```

For more options, see [Rendering](./remotion-render/REFERENCE.md).

For advanced rendering beyond simple `npx remotion render`, see: [Rendering Best Practices](./remotion-render/REFERENCE.md)

## Captions

When working with Captions, load [Remotion Captions](./remotion-captions/REFERENCE.md).

## Creating a SaaS, automation or application

Use the [Remotion SaaS skill](./remotion-saas/REFERENCE.md) for knowledge about Remotion-powered SaaS apps, such as `<Player>`, rendering on Lambda, Vercel, Cloudflare, via Express.js, client-side rendering, or for finding the right SaaS template.

## Looking up Remotion APIs and documentation

To find and read current Remotion documentation, load [Remotion Docs](./remotion-docs/REFERENCE.md).

## Upgrading

To upgrade Remotion, related packages, compatible Mediabunny packages, and installed Remotion Agent Skills, load [Remotion Upgrade](./remotion-upgrade/REFERENCE.md).

<!-- craft-handoff:start -->
## Mở và sửa tiếp trong FilmCraft / EffectCraft

Khi user muốn sửa tiếp trong FilmCraft hoặc EffectCraft, không giao một MP4 phẳng: viết timeline spec rồi dùng skill `craft-handoff` dựng project gốc (`.fcproj` / `.ecproj`) có đủ track, clip, keyframe, chữ, effect và SFX. Với skill này: mỗi `<Sequence>` / phần tử thành một clip: `<Video>`/`<Audio>`/`<Img>` đặt file gốc kèm in/dur, phần vẽ bằng React render ProRes 4444 nền trong suốt. Chi tiết: `craft-handoff/references/skills-map.md`.
<!-- craft-handoff:end -->

<!-- ===== /file: remotion-best-practices/SKILL.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-captions/REFERENCE.md ===== -->

---
name: remotion-captions
description: Transcribing, displaying and animating captions
version: 4.0.539
---

All captions must be processed in JSON. The captions must use the [`Caption`](https://www.remotion.dev/docs/captions/caption.md) type which is the following:

```ts
import type { Caption } from "@remotion/captions";
```

This is the definition:

```ts
type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
  pageBreakAfter?: boolean;
};
```

## Generating captions

To transcribe video and audio files to generate captions, load the [transcribe-captions.md](transcribe-captions.md) file for more instructions.

## Displaying captions

To display captions in your video, load the [display-captions.md](display-captions.md) file for more instructions.

## Importing captions

To import captions from a .srt file, load the [import-srt-captions.md](import-srt-captions.md) file for more instructions.

## Post-creation

After you're done, load this skill: [Remotion Best Practices](../SKILL.md)

If not alreay done, open the Remotion Studio, unless instructed otherwise.

<!-- ===== /file: remotion-best-practices/remotion-captions/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-captions/display-captions.md ===== -->

---
name: display-captions
description: Displaying captions in Remotion using the Basic Captions element
metadata:
  tags: captions, subtitles, display, element
---

# Displaying captions in Remotion

This guide explains how to display captions in Remotion, assuming you already have captions in the [`Caption`](https://www.remotion.dev/docs/captions/caption.md) format.

## Prerequisites

Read [Transcribing audio](transcribe-captions.md) for how to generate captions.

First, the [`@remotion/captions`](https://www.remotion.dev/docs/captions.md) package needs to be installed.
If it is not installed, use the following command:

```bash
npx remotion add @remotion/captions # If project uses npm
bunx remotion add @remotion/captions # If project uses bun
yarn remotion add @remotion/captions # If project uses yarn
pnpm exec remotion add @remotion/captions # If project uses pnpm
```

## Adding the Basic Captions element

Use the [Basic Captions](https://www.remotion.dev/elements/captions/basic-captions) element to display captions.

Alternatives are available at [Remotion Captions Elements](https://www.remotion.dev/elements/captions), but use Basic Captions unless there are more precise specifications.

Fetch its source code from https://www.remotion.dev/elements/captions/basic-captions.md and copy the `basic-captions.tsx` file into the project unchanged.

## Displaying captions alongside video content

Keep each clip's video and captions inside the same `<Sequence>` or `<TransitionSeries.Sequence>`.
Put the clip's `trimBefore`, `durationInFrames`, and `playbackRate` on that shared parent so trimming or changing the speed affects both.  
For independently positioned clips, put `from` on the shared `<Sequence>` too.

Give every captioned clip its own group and inline caption array; do not combine captions from multiple clips into one overlay outside the scene timeline.  
Moving, reordering, trimming, or deleting the group then affects its video and captions together.

Putting captions inside a scene is insufficient if `trimBefore` or `playbackRate` is still applied only to `<Video>`: its sibling captions do not inherit those props. Apply them to the shared parent instead.

The Caption editor writes back to the array literal on the selected `<BasicCaptions>` source node, so inline the captions directly in its `captions` prop.  
Passing a variable or component prop such as `captions={captions}` leaves no source array for the editor to update.  
If the captions were transcribed to a JSON file, copy its contents into the prop.

Give the caption area a width and position it over the video. In this
1920px-wide composition, the 900px caption area is centered by translating it
`(1920 - 900) / 2 = 510` pixels from the left:

```tsx title="src/MyComposition.tsx"
import { Video } from "@remotion/media";
import { TransitionSeries } from "@remotion/transitions";
import { staticFile, useVideoConfig } from "remotion";
import { BasicCaptions } from "./basic-captions";

export const MyComposition: React.FC = () => {
  const { fps } = useVideoConfig();

  return (
    <TransitionSeries>
      <TransitionSeries.Sequence
        name="Opening"
        trimBefore={4 * fps}
        durationInFrames={20 * fps}
      >
        <Video
          name="Opening footage"
          src={staticFile("opening.mp4")}
          objectFit="cover"
          style={{ width: "100%", height: "100%" }}
        />
        <BasicCaptions
          name="Opening captions"
          width={900}
          style={{
            position: "absolute",
            bottom: 120,
            translate: "510px 0px",
          }}
          captions={[
            {
              text: "Hello",
              startMs: 5000,
              endMs: 5400,
              timestampMs: 5200,
              confidence: null,
            },
            {
              text: " world",
              startMs: 5400,
              endMs: 5900,
              timestampMs: 5650,
              confidence: null,
            },
          ]}
        />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence
        name="Next clip"
        trimBefore={1 * fps}
        durationInFrames={5 * fps}
      >
        <Video
          name="Next footage"
          src={staticFile("next.mp4")}
          objectFit="cover"
          style={{ width: "100%", height: "100%" }}
        />
        <BasicCaptions
          name="Next captions"
          width={900}
          style={{
            position: "absolute",
            bottom: 120,
            translate: "510px 0px",
          }}
          captions={[
            {
              text: "Next",
              startMs: 2000,
              endMs: 2400,
              timestampMs: 2200,
              confidence: null,
            },
            {
              text: " clip",
              startMs: 2400,
              endMs: 2900,
              timestampMs: 2650,
              confidence: null,
            },
          ]}
        />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
```

```tsx title="src/Root.tsx"
import { Composition } from "remotion";
import { MyComposition } from "./MyComposition";

export const RemotionRoot = () => {
  return (
    <Composition
      id="MyComposition"
      component={MyComposition}
      durationInFrames={750}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

To change a captioned clip's speed, set `playbackRate` on its shared sequence.
`durationInFrames` selects a range of source frames; the group occupies `durationInFrames / playbackRate` frames in its parent timeline.
Update the composition duration when changing the total timeline length.

If a caption has `pageBreakAfter: true`, the current page ends after that caption and the next caption starts a new page.

## White-space preservation

The captions are whitespace sensitive. You should include spaces in the `text` field before each word.

<!-- ===== /file: remotion-best-practices/remotion-captions/display-captions.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-captions/import-srt-captions.md ===== -->

---
name: import-srt-captions
description: Importing .srt subtitle files into Remotion using @remotion/captions
metadata:
  tags: captions, subtitles, srt, import, parse
---

# Importing .srt subtitles into Remotion

If you have an existing `.srt` subtitle file, you can import it into Remotion using `parseSrt()` from `@remotion/captions`.

If you don't have a .srt file, read [Transcribing audio](transcribe-captions.md) for how to generate captions instead.

## Prerequisites

First, the @remotion/captions package needs to be installed.
If it is not installed, use the following command:

```bash
npx remotion add @remotion/captions # If project uses npm
bunx remotion add @remotion/captions # If project uses bun
yarn remotion add @remotion/captions # If project uses yarn
pnpm exec remotion add @remotion/captions # If project uses pnpm
```

## Reading an .srt file

Use `staticFile()` to reference an `.srt` file in your `public` folder, then fetch and parse it:

```tsx
import { useState, useEffect, useCallback } from "react";
import { staticFile, useDelayRender } from "remotion";
import { parseSrt } from "@remotion/captions";
import type { Caption } from "@remotion/captions";

export const MyComponent: React.FC = () => {
  const [captions, setCaptions] = useState<Caption[] | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const fetchCaptions = useCallback(async () => {
    try {
      const response = await fetch(staticFile("subtitles.srt"));
      const text = await response.text();
      const { captions: parsed } = parseSrt({ input: text });
      setCaptions(parsed);
      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [continueRender, cancelRender, handle]);

  useEffect(() => {
    fetchCaptions();
  }, [fetchCaptions]);

  if (!captions) {
    return null;
  }

  return (
    <>
      {/* Use captions here */}
    </>
  );
};
```

Remote URLs are also supported - you can `fetch()` a remote file via URL instead of using `staticFile()`.

## Using imported captions

Once parsed, the captions are in the `Caption` format and can be used with all `@remotion/captions` utilities.

<!-- ===== /file: remotion-best-practices/remotion-captions/import-srt-captions.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-captions/transcribe-captions.md ===== -->

# Transcribing audio

To transcribe audio to generate captions in Remotion, use the [`transcribe()`](https://www.remotion.dev/docs/whisper-webgpu/transcribe.md) function from the [`@remotion/whisper-webgpu`](https://www.remotion.dev/docs/whisper-webgpu.md) package.
It runs Whisper locally on the GPU and works in both Node.js and the browser.

## Prerequisites

Install the required packages if they are not installed:

```bash
npx remotion add @remotion/whisper-webgpu @huggingface/transformers mediabunny @mediabunny/server # If project uses npm
bunx remotion add @remotion/whisper-webgpu @huggingface/transformers mediabunny @mediabunny/server # If project uses bun
yarn remotion add @remotion/whisper-webgpu @huggingface/transformers mediabunny @mediabunny/server # If project uses yarn
pnpm exec remotion add @remotion/whisper-webgpu @huggingface/transformers mediabunny @mediabunny/server # If project uses pnpm
```

A compatible GPU is required. ONNX Runtime does not work on Linux arm64.

## Transcribing

Make a Node.js script that decodes the audio to a 16kHz mono waveform, downloads a model, and transcribes it.

```ts
import { registerMediabunnyServer } from "@mediabunny/server";
import {
  WHISPER_WEBGPU_SAMPLE_RATE,
  canUseWhisperWebGpu,
  downloadWhisperModel,
  loadWhisperModel,
  toCaptions,
  transcribe,
} from "@remotion/whisper-webgpu";
import {
  ALL_FORMATS,
  Conversion,
  FilePathSource,
  Input,
  NullTarget,
  Output,
  WavOutputFormat,
} from "mediabunny";
import { writeFile } from "node:fs/promises";

registerMediabunnyServer();

const support = await canUseWhisperWebGpu();
if (!support.supported) {
  throw new Error(support.detailedReason);
}

type WaveformChunk = {
  startFrame: number;
  waveform: Float32Array;
};
const chunks: WaveformChunk[] = [];

using input = new Input({
  formats: ALL_FORMATS,
  source: new FilePathSource("public/video123.mp4"),
});
const audioTrack = await input.getPrimaryAudioTrack();
if (audioTrack === null) {
  throw new Error("The media does not contain an audio track.");
}

const conversion = await Conversion.init({
  input,
  output: new Output({
    format: new WavOutputFormat(),
    target: new NullTarget(),
  }),
  video: { discard: true },
  audio: (track) => {
    if (track.id !== audioTrack.id) {
      return { discard: true };
    }

    return {
      codec: "pcm-f32",
      forceTranscode: true,
      numberOfChannels: 1,
      sampleFormat: "f32",
      sampleRate: WHISPER_WEBGPU_SAMPLE_RATE,
      process: (sample) => {
        const waveform = new Float32Array(
          sample.allocationSize({ format: "f32", planeIndex: 0 }) /
            Float32Array.BYTES_PER_ELEMENT,
        );
        sample.copyTo(waveform, { format: "f32", planeIndex: 0 });
        chunks.push({
          startFrame: Math.round(sample.timestamp * WHISPER_WEBGPU_SAMPLE_RATE),
          waveform,
        });
        return sample;
      },
    };
  },
});

if (!conversion.isValid) {
  throw new Error("The audio track cannot be decoded.");
}

await conversion.execute();

const waveformLength = chunks.reduce(
  (max, chunk) => Math.max(max, chunk.startFrame + chunk.waveform.length),
  0,
);
const channelWaveform = new Float32Array(waveformLength);
for (const chunk of chunks) {
  const destinationStart = Math.max(0, chunk.startFrame);
  const sourceStart = Math.max(0, -chunk.startFrame);
  const availableLength = Math.min(
    chunk.waveform.length - sourceStart,
    channelWaveform.length - destinationStart,
  );

  if (availableLength > 0) {
    channelWaveform.set(
      chunk.waveform.subarray(sourceStart, sourceStart + availableLength),
      destinationStart,
    );
  }
}

const model = "small.en";
await downloadWhisperModel({ model });
await using modelHandle = await loadWhisperModel({ model });
const transcription = await transcribe({ channelWaveform, model });
const { captions } = toCaptions({ whisperWebGpuOutput: transcription });

// Write it to a file so the captions can be inlined into the Remotion code
await writeFile("captions123.json", JSON.stringify(captions, null, 2));
```

## Choosing a model

`small.en` is the recommended default for English.  
For other languages, use a multilingual model such as `small` and pass the `language` option to `transcribe()` - automatic language detection is not supported.  
See [`getAvailableModels()`](https://www.remotion.dev/docs/whisper-webgpu/get-available-models.md) for all models.

## Transcribing in the browser

In the browser, use [`resampleTo16Khz()`](https://www.remotion.dev/docs/whisper-webgpu/resample-to-16khz.md) to get the waveform from a `File` instead of using Mediabunny:

```ts
import {
  downloadWhisperModel,
  resampleTo16Khz,
  toCaptions,
  transcribe,
} from "@remotion/whisper-webgpu";

export const transcribeFile = async (file: File) => {
  await downloadWhisperModel({ model: "small.en" });
  const channelWaveform = await resampleTo16Khz({ file });
  const transcription = await transcribe({
    channelWaveform,
    model: "small.en",
  });

  const { captions } = toCaptions({ whisperWebGpuOutput: transcription });
  return captions;
};
```

Transcribe each original source video or audio file individually.  
Keep the resulting caption timestamps relative to the beginning of that source file, including portions currently trimmed out of the edit.  
Do not add composition offsets or flatten multiple transcripts into composition-wide timestamps.

See [Displaying captions](display-captions.md) for how to display the captions in Remotion.

<!-- ===== /file: remotion-best-practices/remotion-captions/transcribe-captions.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-create/REFERENCE.md ===== -->

---
name: remotion-create
description: Create a new Remotion video
version: 4.0.539
---

These are instructions for making a new Remotion project and composition.  
If this is not the next task, see [Remotion Best Practices](../SKILL.md)

## Scaffold a project

If a project already exists, skip this.
Ensure Node.js and Git is installed, and the current folder is appropriate for starting a new project.

Inspect the current folder, including hidden files, before choosing where to scaffold.

### Empty folder

If it is empty, or contains only disposable operating-system metadata such as `.DS_Store`, create the project directly in the current folder.
Remove only those disposable metadata files first, since `create-video` rejects non-empty folders.
Do not treat all hidden files as disposable: files such as `.env` and directories such as `.git` are meaningful contents.

Scaffold in existing folder:

```bash
npx create-video@latest --yes --blank --no-tailwind .
npm i
```

### Non-empty folder

If the current folder contains meaningful contents and no project already exists, scaffold into a new subfolder.
Replace `my-video` with a suitable project name.

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
cd my-video
npm i
```

## Open the preview before building the video

As soon as the project can run, open [Remotion Studio](../remotion-studio/REFERENCE.md) in the browser before writing or changing the composition. For a new project, do this immediately after scaffolding and installing dependencies. For an existing project, do it before editing the video. Keep Studio running while you work so the user can see changes as they appear and steer the result.

## Designing a video

Keep the scaffold and add React Markup.
Follow [Remotion React Markup Best Practices](../remotion-markup/REFERENCE.md) and [Video Layout Rules](video-layout.md) for video-first layout and text sizing guidance.

Before writing the root that registers `<Composition>` or `<Still>` elements,
follow [Compositions and stills](../remotion-markup/compositions.md).

## Is this a timeline of clips?

If the video arranges multiple video or audio clips on a timeline, follow
[Video editing](../remotion-markup/video-editing.md) before writing the
timeline. Give every clip that should be edited independently its own authored
JSX node.

## Is this a multi-scene video?

If this is a video with multiple subsequent scenes, follow guidance at [Multi-scene videos](../remotion-markup/multi-scene-video.md).

## Interactivity Best Practices

By structuring the React Markup following [Remotion Interactivity Best Practices](../remotion-interactivity/REFERENCE.md), you allow the user to make edits in the Studio which write back to code.

## TailwindCSS

If Tailwind is requested, see [tailwind.md](tailwind.md) for using TailwindCSS in Remotion.

## Follow-up

The video creation process has finished.
For follow-up prompts, use [Remotion Best Practices](../SKILL.md)

<!-- ===== /file: remotion-best-practices/remotion-create/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-create/tailwind.md ===== -->

---
name: tailwind
description: Using TailwindCSS in Remotion.
metadata:
---

You can and should use TailwindCSS in Remotion, if TailwindCSS is installed in the project.

Don't use `transition-*` or `animate-*` classes - always animate using the `useCurrentFrame()` hook.

Tailwind must be installed and enabled first in a Remotion project - see https://www.remotion.dev/docs/tailwind.

<!-- ===== /file: remotion-best-practices/remotion-create/tailwind.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-create/video-layout.md ===== -->

You are designing a video, not a webpage.

- Decide what the viewer should notice first in each scene. Build the frame around that one thing.
- Keep important content inside a generous safe area. For 1080px-wide videos, keep key text at least 80px from the sides and 100px from the top and bottom.
- Do not add redundant elements.
- For 1080px-wide compositions, use these rough minimums:
  - Main headline: 84px
  - Important supporting text: 44px
- Scale those values with the composition width.

<!-- ===== /file: remotion-best-practices/remotion-create/video-layout.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-docs/REFERENCE.md ===== -->

---
name: remotion-docs
description: Search Remotion documentation
version: 4.0.539
---

This skill teaches you how to discover and read current Remotion documentation.
If this is not relevant, load [Remotion Best Practices](../SKILL.md) instead.

## Searching the docs

Use the Algolia search API to find relevant documentation pages:

```
POST https://plsduol1ca-dsn.algolia.net/1/indexes/*/queries?x-algolia-api-key=3e42dbd4f895fe93ff5cf40d860c4a85&x-algolia-application-id=PLSDUOL1CA
Content-Type: application/x-www-form-urlencoded

{
  "requests": [
    {
      "query": "<your search query>",
      "indexName": "remotion",
      "params": "attributesToRetrieve=[\"hierarchy.lvl0\",\"hierarchy.lvl1\",\"hierarchy.lvl2\",\"url\"]&hitsPerPage=10"
    }
  ]
}
```

Each hit contains a `url` field pointing to the documentation page.

## Fetching a page as Markdown

Append `.md` to any Remotion docs URL to retrieve its Markdown source (saves tokens):

```
https://www.remotion.dev/docs/use-video-config.md
https://www.remotion.dev/docs/sequence.md
https://www.remotion.dev/docs/lambda/rendermediaonlambda.md
```

## Workflow

1. Search Algolia for the concept or API you need.
2. Pick the most relevant URL(s) from the results.
3. Fetch each URL with the `.md` suffix.
4. Implement using the current documentation rather than memorized API knowledge.

<!-- ===== /file: remotion-best-practices/remotion-docs/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-interactivity/REFERENCE.md ===== -->

---
name: remotion-interactivity
description: Structure Remotion markup for interactivity
version: 4.0.539
---

Studio edits the JSX nodes that create timeline items. Structure the code around
what the user should be able to select, move, trim, or style independently.
Keep editable values inline on each instance.

Before writing a scene or refactoring its layers, read
[editable timeline structure](timeline-structure.md). It covers editing units,
tracks, shared timing, plain layout containers, and a complete component-to-root
example. For a timeline built from footage, also read
[editable video timelines](../remotion-markup/video-editing.md).

Use [connected compositions](../remotion-markup/connected-compositions.md) when
a scene or reusable group needs its own timeline. Validate both its standalone
view and the full parent timeline; a connection alone does not guarantee fewer
visible rows.

## Choose schema fields

Each key in the schema is a prop that Studio can read and edit at the call site.
Props that are not in the schema still work, but are not editable in Studio.
Keys may use dot notation, such as `style.color`.

| Type                                                                         | Use for                                                      | Keyframable   |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------ | ------------- |
| `string`                                                                     | Strings, such as a title, prompt, or code snippet            | No            |
| `number`                                                                     | Numbers, with optional `min`, `max`, `step`, `integer`       | Yes           |
| `boolean`                                                                    | On/off switches                                              | Yes (hold)    |
| `color`                                                                      | CSS color strings                                            | Yes           |
| `enum`                                                                       | A choice between `variants`, each with its own nested schema | Opt-in (hold) |
| `array`                                                                      | Lists of numbers, colors, enums and more                     | No            |
| `asset`                                                                      | Media sources, with optional `assetType`                     | No            |
| `font-family`                                                                | CSS font family                                              | No            |
| `font-weight`                                                                | Font weight                                                  | Yes           |
| `translate`, `scale`, `rotation-css`, `rotation-degrees`, `transform-origin` | Transforms                                                   | Yes           |
| `uv-coordinate`                                                              | A normalized `[x, y]` point on the element                   | Yes           |
| `svg-path`                                                                   | SVG path data                                                | Yes           |
| `remotion-captions`                                                          | `Caption[]` data                                             | No            |
| `hidden`                                                                     | A value kept out of the controls                             | —             |

Every field needs a `default` and should have a `description`, which Studio shows as the label.
Set `keyframable: false` to show a static control.

Expose content and per-instance appearance, such as the text and an accent color.
Do not add fields for `style.translate`, `style.scale`, `style.rotate`, `style.transformOrigin` and `style.opacity`: `Interactive.create()` adds them automatically.

To make CSS properties of the root editable per instance, spread the built-in schema fragments:

```tsx
const cardSchema = {
  ...Interactive.textSchema, // style.color, style.fontSize, style.fontWeight, ...
  ...Interactive.backgroundSchema, // style.backgroundColor
  ...Interactive.borderRadiusSchema, // style.borderRadius, ...
} as const satisfies InteractivitySchema;
```

Also available: `Interactive.borderSchema`, and `Interactive.captionsSchema` for components that accept captions.
For components that accept `React.ReactNode` children, add `...Interactive.childrenSchema`.
It provides controls for children content and may evolve to support richer content.
Currently, it uses a string field labeled "Text" with a default of `''`.
If a component requires string-only children, declare an explicit `children` field with `type: 'string'` instead.
`Interactive.textSchema` controls typography styles; `childrenSchema` controls content.
The children fragment is not included in `baseSchema` or automatically added to custom components.
Nested markup and computed children are currently read-only.
`text-content` is a deprecated alias for the `string` field type.
See [`InteractivitySchema`](https://www.remotion.dev/docs/interactivity-schema) for all options.

## Make an HTML element interactive using `Interactive`

Every HTML and SVG element (except `<Img>`, it already is interactive) such as `<div>` can be turned interactive using `Interactive`:

```tsx title="Interactive elements"
<Interactive.Div
  name="Greeting card"
  style={{fontSize: 80, padding: 24}}
>
  Hello
</Interactive.Div>
```

Use this for text or graphics that need independent controls. Keep layout-only
containers and decorative internals as plain HTML; an interactive component
already provides controls for its root.

## Prefer inline text

If text is fixed and only used once, write it directly inside the interactive element instead of extracting it into a constant.

```tsx title="Inline text"
// 👍 Fixed copy stays editable
<Interactive.Div name="Title">
  Remotion Best Practices
</Interactive.Div>
```

Use a prop or variable only when the text is dynamic or reused.

## Give interactive elements a descriptive name

Add a `name` prop to elements to make them easily identifyable.
Avoid computed names, hardcode them.

```tsx title="Interactive names"
<>
  <Interactive.Div name="Hero title" style={{fontSize: 80}}>
    Launch day
  </Interactive.Div>
  <Img name="Avatar" src="https://remotion.media/image.jpeg" />
  <Video name="Background" src="https://remotion.media/video.mp4" />
  <Interactive.Div name="Title">
    Launch day
  </Interactive.Div>
</>
```

## Keep all CSS styles inline

The best way is to just pass a plain object to `style` - no referring to constants, no object spreading, no math.

```tsx title="Interactive example"
<Interactive.Div
  style={{
    fontSize: 80,
    color: 'red',
  }}
>
  Hello World!
</Interactive.Div>
```

```tsx title="❌ Bad for interactivity"
const baseStyle = useMemo(() => {
  return {
    fontSize: 12 // ❌ Non-inline styles are not supported
  }
}, []);

<Interactive.Div
  style={{
    ...baseStyle, // ❌ Spreading is not supported
    color: RED, // ❌ Referring to constants is not supported
    scale: frame * 10 // ❌ Math is not supported
  }}
>
  Hello World!
</Interactive.Div>
```

## Animate using `interpolate()`

Write animations as inline `interpolate()` calls on the property that changes.  
The output range, easing, extrapolation and `output` property should use hardcoded values.

The input range may additionally use `durationInFrames`, `fps`, `width` and `height` destructured directly from `useVideoConfig()`. Bare identifiers such as `durationInFrames`, multiplication with a number such as `2 * fps` or `fps * 2`, and subtraction of a number such as `durationInFrames - 1` are supported.

```tsx title="Inline values"
const {fps, durationInFrames} = useVideoConfig();

// 👍 Inline values can be standardized and keyframed
<Interactive.Div
  name="Product card"
  style={{
    color: 'white',
    fontSize: 80,
    scale: interpolate(frame, [0, fps], [0, 1], {
      easing: Easing.spring({damping: 200}),
      output: 'perceptual-scale',
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp'
    }),
    rotate: interpolate(frame, [0, 1 * fps], ['0deg', '20deg'], {
      easing: Easing.spring({damping: 200}),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp'
    }),
    translate: interpolate(
      frame,
      [durationInFrames - 30, durationInFrames],
      ['0px 0px', '0px 120px'],
      {
        easing: Easing.spring({damping: 200}),
        output: 'perceptual-scale',
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp'
      }
    ),
  }}
/>
```

```tsx title="❌ Bad interactivity"
const translateY = interpolate(frame, [0, 30], [0, 120]); // ❌ Math should be directly in the markup

<Interactive.Div
  name="Product card"
  style={{
    translate: translateY, // ❌ Only inline interpolate() calls are supported,
    rotate: interpolate(frame, [start, start + 10], [0, Math.PI]), // ❌ Cannot use math with arbitrary variables, cannot use constants
    scale: interpolate(anyVariable, [0, 30], [0, 1]) // ❌ Can only interpret the `frame` variable.
  }}
/>
```

## Keep SVG paths editable with `Interactive.Path`

Use `<Interactive.Path>` from `remotion` instead of `<path>` inside an SVG to make the path visually editable.

Install `@remotion/paths` for path interpolation and Studio path keyframes:

```sh
bunx remotion add @remotion/paths
```

If the geometry is meant to be static, put the path string directly in the `d` prop. Do not extract it into a constant.

```tsx title="Editable static path"
import {Interactive} from 'remotion';

<Interactive.Svg width={300} height={300} viewBox="0 0 300 300">
  <Interactive.Path
    name="Triangle"
    d="M 40 40 L 260 40 L 150 260 Z"
    fill="#0b84f3"
  />
</Interactive.Svg>
```

### Morph paths using inline `interpolatePaths()`

Use `interpolatePaths()` from `@remotion/paths` directly in `d`.  
It accepts a frame, an input range, an equally sized array of path strings, and options for easing, extrapolation, and posterization.
Keep the output paths, ranges, and options inline, following the same input-range rules as `interpolate()` above.  
Do not use `interpolatePath()` API or extract the interpolated result into a variable when the path keyframes should remain editable in Studio.

```tsx title="Editable path keyframes"
import {interpolatePaths} from '@remotion/paths';
import {Easing, Interactive, useCurrentFrame} from 'remotion';

export const MorphingPath = () => {
  const frame = useCurrentFrame();

  return (
    <Interactive.Svg width={300} height={300} viewBox="0 0 300 300">
      <Interactive.Path
        name="Morphing triangle"
        d={interpolatePaths(
          frame,
          [0, 30, 60],
          [
            'M 40 40 L 260 40 L 150 260 Z',
            'M 40 150 L 150 40 L 260 150 Z',
            'M 40 260 L 150 40 L 260 260 Z',
          ],
          {
            easing: Easing.bezier(0.42, 0, 0.58, 1),
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          },
        )}
        fill="#0b84f3"
      />
    </Interactive.Svg>
  );
};
```

Studio can edit the path at the current frame, add or move keyframes, and adjust their easing.  
Use `strokeDasharray` and `strokeDashoffset` to evolve paths.

## Use `scale`, `translate`, `rotate` CSS properties

Avoid the `transform` CSS property.  
If possible, use `scale`, `rotate` and `translate` instead because only they are interactively editable.

## Keep composition metadata inline

When scaffolding a composition, use a JSX string literal for `id`, keep `width`, `height`, `fps`, `durationInFrames` and `defaultProps` inline and make no type assertions.

The Props editor can save visual edits back to your code when `defaultProps` is an inline object literal on `<Composition>` or `<Still>`.

```tsx
// 👍 Static values are in <Composition>, dynamic values are in calculateMetadata()
const calculateMetadata = useMemo(async () => {
  const dimensions = await getDimensions(); // just an example
  return {width: dimensions.width, height: dimensions.height};
});

<Composition
  id="my-video"
  component={MyComponent}
  durationInFrames={150}
  fps={30}
  calculateMetadata={calculateMetadata}
  defaultProps={{title: 'Hello', color: '#0b84ff'}}
/>
```

```tsx title="Negative examples"
const defaultProps = {title: 'Hello', color: '#0b84ff'}; // ❌ Don't extract defaultProps, must be inline
const calculateMetadata = useMemo(() => {
  // ❌ Unnecessary because no calculation is being done,
  return {durationInFrames: 150, fps: 30, width: 1920, height: 1080};
});

<Composition
  id="my-video"
  component={MyComponent}
  calculateMetadata={calculateMetadata}
  defaultProps={{
    title: 'Hello',
  } as Props} // ❌ Don't have type assertions, instead type MyComponent correctly
/>
```

Use only `calculateMetadata()` for the part of the metadata that is dynamic.

## Effects should be inline too

Keep effect arrays and parameters inline so their shape and keyframes remain editable. See [Inline effects](./inline-effects.md) for examples.

## Making your own component interactive

To make a custom userland component interactive, use:
[Make a component interactive](https://www.remotion.dev/docs/studio/make-component-interactive.md)

## Video editing

If a Remotion component mainly consists of video and audio clips, see [Video editing](../remotion-markup/video-editing.md) for best practices on how to structure Remotion markup so the clips are interactively editable in the timeline.

<!-- ===== /file: remotion-best-practices/remotion-interactivity/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-interactivity/inline-effects.md ===== -->

## Effects should be inline too

The effects array should not be computed.
The same rules for setting keyframes as `interpolate()` apply too here: All values should also be hardcoded: Input range, output range, easing, extrapolation, `output` property.

```tsx title="Effects"
// 👍 Parameters are inline and the array shape is stable
<CanvasImage
  src={src}
  width={1280}
  height={720}
  effects={[
    radialProgressiveBlur({
      center: [0.5, 0.5],
      width: 1.2,
      height: 0.8,
      start: 0.2,
      disabled: true,
      rotation: interpolate(frame, [0, 120], [0, 180]),
    }),
  ]}
/>

const center = [0.5, 0.5] as const;
const rotation = frame * 1.5;

<CanvasImage
  src={src}
  width={1280}
  height={720}
  // ❌ Conditional effect is not animateable
  effects={enabled ? [
    radialProgressiveBlur({
      // ❌ Not inline
      center,
      rotation,
    }),
  ] : []}
/>
```

Render separate elements if one version should have effects and another should not.

<!-- ===== /file: remotion-best-practices/remotion-interactivity/inline-effects.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-interactivity/timeline-structure.md ===== -->

# Editable timeline structure

Choose what the user should be able to move, trim, style, duplicate, or delete
together before adding timeline items. A scene, a captioned shot, a summary
card, or a sticker with its entrance sound can each be one editable unit.
Use plain HTML for the layout and decoration inside that unit. Add an
`Interactive` element when it needs independent selection or controls.

Write each independently editable instance as its own JSX node, with a literal
name and inline timing and appearance props. Reuse the component implementation
for repeated cards or stickers, but keep their instances separate. Use loops for
output intentionally controlled as one template, such as particles or chart
bars, rather than independently editable clips.

## Choose how items share time

| Editing behavior                                                 | Structure                                                           |
| ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| Items have independent start times and do not overlap            | A named `Track`, with timing on each item                           |
| Consecutive clips should stay adjacent when one changes duration | `TransitionSeries`, with timing on each `TransitionSeries.Sequence` |
| Several layers must move, trim, or change speed together         | One timed component or `Sequence` containing those layers           |

A track is useful for scenes, music segments, cutaways, stickers, or sound
effects. Group non-overlapping siblings by role instead of giving every item
its own row. Items that remain visible together need separate tracks or a
component that contains their shared layout. Staggered entrances do not make
overlapping cards suitable for one track.

Put timing directly on components that accept it. Avoid a `Sequence` around a
single timing-capable child just to name or register it. Keep wrappers that
provide shared timing, dimensions, or `TransitionSeries` behavior. Use
`layout="none"` on a `Sequence` when it should not introduce a layout element.

For captioned footage and overlays spanning cuts, read
[editable video timelines](../remotion-markup/video-editing.md).

## Give substantial groups their own timelines

Create a connected composition when a scene or reusable element benefits from
being edited on its own. Export it with `Interactive.create()` and register the
same reference with `Composition`.

- Use `layout: 'absolute-fill'` for a scene. Return a fragment and put its
  background and alignment styles on the instance; the managed root applies them.
- Use `layout: 'none'` for a bounded element. Forward `style` to its plain root.
  The component already owns a timeline item, so the root does not need another
  `Interactive.Div` for the same controls.

Connection enables drill-down and shared implementation. It does not guarantee
fewer rows in the parent: Studio can display connected children inside a series.
Choose useful editing boundaries, then inspect the actual parent timeline.
Do not add wrapper components or hide editable content just to alter row counts.

## Complete example

The title is one editable element. Its scene has a connected timeline, while
independently timed scenes and music segments each share a named track.

```tsx title="Title.tsx"
import type React from 'react';
import {Interactive} from 'remotion';

const TitleInner = ({
  children,
  style,
}: {
  readonly children: React.ReactNode;
  readonly style: React.CSSProperties;
}) => <h1 style={{margin: 0, ...style}}>{children}</h1>;

export const Title = Interactive.create({
  Component: TitleInner,
  layout: 'none',
  schema: {
    ...Interactive.textSchema,
    ...Interactive.childrenSchema,
  },
});
```

```tsx title="Chapter.tsx"
import {Interactive} from 'remotion';
import {Title} from './Title';

const ChapterInner = ({title}: {readonly title: string}) => (
  <>
    <Title
      name="Chapter title"
      style={{fontFamily: 'Arial, sans-serif', fontSize: 96, color: 'white'}}
    >
      {title}
    </Title>
  </>
);

export const Chapter = Interactive.create({
  Component: ChapterInner,
  layout: 'absolute-fill',
  schema: {
    ...Interactive.backgroundSchema,
    title: {type: 'string', default: '', description: 'Title'},
  },
});
```

```tsx title="MyVideo.tsx"
import {Audio} from '@remotion/media';
import {staticFile, Track, useVideoConfig} from 'remotion';
import {Chapter} from './Chapter';

export const MyVideo = () => {
  const {fps} = useVideoConfig();
  return (
    <>
      <Track name="Chapters">
        <Chapter
          name="Opening"
          durationInFrames={3 * fps}
          title="Introduction"
          style={{
            backgroundColor: '#111111',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        />
        <Chapter
          name="Feature"
          from={3 * fps}
          durationInFrames={4 * fps}
          title="New features"
          style={{
            backgroundColor: '#243b53',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        />
      </Track>
      <Track name="Music">
        <Audio
          name="Opening music"
          src={staticFile('music.mp3')}
          durationInFrames={2 * fps}
        />
        <Audio
          name="Closing music"
          src={staticFile('music.mp3')}
          from={4 * fps}
          trimBefore={10 * fps}
          durationInFrames={3 * fps}
        />
      </Track>
    </>
  );
};
```

```tsx title="Root.tsx"
import {Composition, Folder} from 'remotion';
import {Chapter} from './Chapter';
import {MyVideo} from './MyVideo';
import {Title} from './Title';

export const RemotionRoot = () => (
  <>
    <Composition
      id="MyVideo"
      component={MyVideo}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={210}
    />
    <Folder name="Scenes">
      <Composition
        id="Chapter"
        component={Chapter}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={90}
        defaultProps={{
          title: 'Introduction',
          style: {
            backgroundColor: '#111111',
            justifyContent: 'center',
            alignItems: 'center',
          },
        }}
      />
    </Folder>
    <Folder name="Elements">
      <Composition
        id="Title"
        component={Title}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={90}
        defaultProps={{
          children: 'Introduction',
          style: {
            fontFamily: 'Arial, sans-serif',
            fontSize: 96,
            color: 'white',
          },
        }}
      />
    </Folder>
  </>
);
```

Keep metadata and defaults inline on each registration. See
[connected compositions](../remotion-markup/connected-compositions.md) for
extracting existing groups and checking both the parent and standalone views.

<!-- ===== /file: remotion-best-practices/remotion-interactivity/timeline-structure.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/REFERENCE.md ===== -->

---
name: remotion-maps
description: Remotion Map animation knowledge
version: 4.0.539
---

# Remotion Maps

Choose exactly one technique from the intended shot, then load only that technique's `TECHNIQUE.md`.
Every technique directory is self-contained and may be removed without breaking the others.

## [Static map](techniques/static-map/TECHNIQUE.md)

- Requires you grab a satellite image and mount it in a `<Img>` tag, and animate on top

## [Mapbox](techniques/mapbox/TECHNIQUE.md)

- Requires a Mapbox key
- Nicer styles by default
- Map can display a round globe when zoomed out
- Includes nice 3D buildings such as the Eiffel tower

## [MapLibre](techniques/maplibre/TECHNIQUE.md)

- Requires no API key, fully free
- Does not include 3D building

## [MapTiler](techniques/maptiler/TECHNIQUE.md)

- Uses MapTiler
- Annotations can be drawn on top of geographic features: borders, rivers, labels

## [CesiumJS](techniques/cesium/TECHNIQUE.md)

- Flythroughs through terrain and mountains
- "Flight simulator" perspective

<!-- ===== /file: remotion-best-practices/remotion-maps/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/cesium/TECHNIQUE.md ===== -->

# CesiumJS — 3D flyovers in Remotion

Instructions for achieving map animations with "flight-simulator" perspective in Remotion.

## Modes

| Mode        | Data                                                  | Use for                                                |
| ----------- | ----------------------------------------------------- | ------------------------------------------------------ |
| `landscape` | MapTiler `terrain-quantized-mesh-v2` + `satellite-v2` | Mountains, gorges, rivers, coastlines and rural routes |
| `city`      | Google Photorealistic 3D Tiles                        | Cities, architecture and recognizable landmarks        |

Do not use footprint extrusions for city flyovers. They produce crude building blocks rather than
textured architecture.

## Credentials

For `landscape`, set:

```text
REMOTION_MAPTILER_KEY=...
```

Create a MapTiler key at https://cloud.maptiler.com/account/keys/.

For `city`, set:

```text
REMOTION_GOOGLE_MAPS_API_KEY=...
```

Create a billing-enabled Google Map Tiles API key by following
https://developers.google.com/maps/documentation/tile/get-api-key. Enable the **Map Tiles API** and
restrict the key to that API. Ensure its application restriction permits local headless Remotion
requests.

## Build the flight

1. Copy `assets/CesiumFlythrough.tsx`, a path JSON and `assets/example-Root.tsx` into the Remotion
   project, or import the component directly.
2. Supply the camera route as `[longitude, latitude][]`. Use only meaningful control points; do not hand-author dozens of tiny corrections.
3. Leave `pathSmoothingPasses={3}` initially. The component applies repeated Chaikin corner cutting, turning straight-then-corner input into a continuous swerve. Increase to `4` for a softer route or reduce to `2` when the camera must follow a tight corridor.
4. Set absolute camera altitudes for the location. City cameras normally fly lower than landscape
   cameras.
5. Render a middle-frame still before rendering the full video.

```tsx
<CesiumFlythrough
  mode="city"
  path={cameraPath}
  pathSmoothingPasses={3}
  altitudeStart={700}
  altitudeEnd={500}
  lookAheadKm={0.7}
  travelKm={4.5}
/>
```

## Camera behavior

Walk the smoothed curve by arc length for constant ground speed. Aim at a real point farther along
the curve rather than its next vertex. Derive roll from the change in look-ahead bearing so the
camera banks into a turn instead of twitching left and right.

For landscape routes, `scripts/prep-cesium-path.mjs` also clips, resamples, smooths and dampens a
GeoJSON centerline before the component applies its final curve smoothing.


## Mechanics

- Set `viewer.useDefaultRenderLoop = false`.
- Call `viewer.render()`, never `scene.render()`, while settling.
- Use `preserveDrawingBuffer: true`.
- Gate initialization and every frame with `delayRender`.
- Drive camera animation from `useCurrentFrame()`; do not use CSS transitions or browser-timed animation.
- Settle landscapes on `globe.tilesLoaded` and cities on `tileset.tilesLoaded`.
- Keep all provider attribution visible.
- Record the source and effective date of custom or disputed geography.
- Inspect rendered pixels, not only Studio playback, at every required aspect ratio.
- Read `references/3d-flyover-architecture.md` for camera math, `references/3d-data-sources.md` for provider details, and `references/3d-troubleshooting.md` for blank, coarse, unauthorized or timed-out renders.

## Files

- `assets/CesiumFlythrough.tsx` — reusable two-mode component.
- `assets/flight-path.ts` — dependency-free Chaikin route smoothing.
- `assets/example-Root.tsx` — landscape and city compositions.
- `assets/cesium-path.json` — sample landscape route.
- `assets/city-path.json` — sample city route.
- `assets/sample-river.geojson` — sample path-preparation input.
- `scripts/prep-cesium-path.mjs` — dependency-free landscape route preparation.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/cesium/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/cesium/references/3d-data-sources.md ===== -->

# Flyover data sources

## Landscape

Use MapTiler for both layers:

- `terrain-quantized-mesh-v2`: elevation encoded as Cesium quantized-mesh terrain.
- `satellite-v2`: raster satellite imagery draped on that mesh.

CesiumJS renders the layers; it does not supply the data. Set `REMOTION_MAPTILER_KEY`.

Create a key:

- https://cloud.maptiler.com/account/keys/

Official documentation:

- https://docs.maptiler.com/cesium/
- https://docs.maptiler.com/schema-raster/terrain-3d/

## City

Use Google Photorealistic 3D Tiles. Google supplies one high-resolution 3D mesh already textured
with imagery. Disable the Cesium globe and do not add MapTiler terrain or satellite beneath it. Set
`REMOTION_GOOGLE_MAPS_API_KEY`.

Create and configure a key:

- https://developers.google.com/maps/documentation/tile/get-api-key

Enable the Map Tiles API in a billing-enabled Google Cloud project and restrict the key to that API.
The application restriction must permit the local headless Remotion request.

Official documentation:

- https://developers.google.com/maps/documentation/tile/3d-tiles
- https://developers.google.com/maps/documentation/tile/policies

## Why not extruded buildings

OSM-, Overture- and vector-tile building products primarily provide footprints, approximate heights
and optional roof attributes. They are useful for analytical or stylized maps, but they do not
provide the textured architecture required for a cinematic city flyover.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/cesium/references/3d-data-sources.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/cesium/references/3d-flyover-architecture.md ===== -->

# 3D Flyover — architecture reference

Deep detail behind `TECHNIQUE.md`: provider loading, the camera-path pipeline, per-frame camera math, and
the proven terrain values. Both landscape and city modes have been forward-tested through Remotion.

## 1. Provider initialization

Create the Viewer with `baseLayer: false`, UI widgets disabled, and
`contextOptions.webgl.preserveDrawingBuffer: true`. Never hide the credit display.

### Landscape

Add MapTiler `satellite-v2` with `UrlTemplateImageryProvider`, then load
`terrain-quantized-mesh-v2` with `CesiumTerrainProvider.fromUrl({requestVertexNormals: true})`.
MapTiler supplies both datasets; no Cesium ion token is required.

### City

Do not add MapTiler. Hide the globe, then add:

```ts
viewer.scene.globe.show = false;
const tileset = await Cesium.Cesium3DTileset.fromUrl(
  `https://tile.googleapis.com/v1/3dtiles/root.json?key=${GOOGLE_KEY}`,
  {showCreditsOnScreen: true, maximumScreenSpaceError: 4},
);
viewer.scene.primitives.add(tileset);
```

Lower `maximumScreenSpaceError` improves refinement at substantial download/render cost. Start at
`4` for a hero landmark and `6–8` for wider urban shots. Enforce the Google 30-second promotional
video ceiling in the component.

Load Cesium from the CDN after setting `window.CESIUM_BASE_URL`; the tested version is `1.143`.

## 2. The camera path — structure & generation

Four properties matter, in order:

1. **Continuous curvature** — the camera must flow through curves, never "fly straight, snap to a new
   heading, fly straight." The component applies three passes of **Chaikin corner cutting** to every
   supplied path. Each pass replaces a segment with quarter and three-quarter points, rounding a
   corner into a curve. Three passes are the default; four is softer, two is tighter.
2. **Constant ground speed** — precompute cumulative distance along the rounded curve and interpolate
   by arc length. Do not animate by source-point index; unequal source spacing creates speed bumps.
3. **Minimized amplitude** — for detailed landscape centerlines, dampen the prepared path toward its
   straight start→end chord by a fixed fraction `DAMP` (0 = dead straight, 1 = full river). This is
   the single swerve-amplitude knob.
4. **Enough length** — `PATHKM ≥ TRAVEL_KM + 2·LOOK_AHEAD_KM` so the look-ahead aim never clamps.

`../scripts/prep-cesium-path.mjs` does: clip a window of the source centerline → resample to even
arc-length spacing (0.1 km) → moving-average smooth (±2.8 km window, 2 passes) → dampen toward the chord
(`DAMP=0.45`). Validate with the heading-delta probe it prints — deltas should be small and change
_gradually_ (water-wars: `3,0,-1,-3,-4,1,7,9,5,-5,-12,-7,…`). Big jumps = corners = bad.

The component then applies Chaikin smoothing to this prepared route, or directly to a short
hand-authored city route. Keep city control points sparse and intentional; smoothing cannot rescue a
zig-zagging route that crosses the subject repeatedly.

**Source data:** OSM via Overpass (~0.3 km vertex spacing) — Natural Earth is too coarse for inner
gorges. overpass-api.de is often busy → mirror `overpass.kumi.systems`.

## 3. Camera animation per frame (position, heading, pitch, bank)

Walk the path by **arc length** (precompute cumulative distances once). Every frame:

- **Position** = the point at `dCam` km along the path, altitude `lerp(ALT_START, ALT_END, prog)`.
- **Heading** = bearing from the camera point to a **real point `LOOK_AHEAD_KM` further along the same
  path**. A far aim averages wiggle → smooth heading; on a curved path it leads into the bend, so the
  heading turns gently with the path. (A local-tangent aim spins the camera at every kink — don't.)
- **Pitch** = constant. We keep a MapLibre-style param `PITCH_FROM_NADIR` (90 = horizon), then convert:
  **Cesium pitch = `-(90 - PITCH_FROM_NADIR)`** (Cesium: 0 = horizon, -90 = straight down). 76° → -14°.
- **Bank (roll)** = lean _into_ the turn — the helicopter tell. Measure turn rate as the bearing change
  between `aim` and a point `2·LOOK_AHEAD_KM` ahead; `roll = clamp(dH · BANK_GAIN, ±MAX_BANK)`. Because
  the path is smooth, `dH` changes gradually → the bank eases in and out, never jerks.

```ts
const setCamera = (C, viewer, prog) => {
  const dCam = Math.min(TRAVEL_KM, PATHKM - LOOK_AHEAD_KM * 2) * prog;
  const cam  = alongPath(dCam);                    // arc-length point
  const aim  = alongPath(dCam + LOOK_AHEAD_KM);     // heading target (real point on the path)
  const aim2 = alongPath(dCam + LOOK_AHEAD_KM * 2); // turn-rate probe → bank
  const heading = bearing(cam, aim);
  let dH = bearing(aim, aim2) - heading; while (dH > Math.PI) dH -= 2*Math.PI; while (dH < -Math.PI) dH += 2*Math.PI;
  viewer.camera.setView({
    destination: C.Cartesian3.fromDegrees(cam[0], cam[1], lerp(ALT_START, ALT_END, prog)),
    orientation: { heading, pitch: C.Math.toRadians(-(90 - PITCH_FROM_NADIR)), roll: clamp(dH * BANK_GAIN, -MAX_BANK, MAX_BANK) },
  });
};
```

> **Cesium vs MapLibre conventions (gotcha):** Cesium heading is radians, 0 = north, clockwise. Pitch
> 0 = horizon, negative = down (MapLibre is the inverse). Roll positive = bank right; tune the sign by eye.

## 4. The feel — proven water-wars values

| Param                    | Value                  | Meaning                                                                              |
| ------------------------ | ---------------------- | ------------------------------------------------------------------------------------ |
| `TRAVEL_KM`              | 13                     | How far the camera travels. **Speed = `TRAVEL_KM / durationSeconds`.**               |
| duration                 | 24 s (720 f @30)       | 13 km / 24 s ≈ **0.54 km/s** — a slow, peaceful glide. 8 s felt "extremely rushed".  |
| `ALT_START → ALT_END`    | 4600 → 4300 m ASL      | Absolute (terrain-independent). Inside the corridor walls → fly _through_, not over. |
| `LOOK_AHEAD_KM`          | 1.5                    | Heading smoothness vs responsiveness.                                                |
| `PITCH_FROM_NADIR`       | 76°                    | Stare-ahead down the corridor (90 = level). → Cesium -14°.                           |
| `MAX_BANK` / `BANK_GAIN` | 0.13 rad (~7.5°) / 0.6 | Helicopter lean into turns.                                                          |
| `verticalExaggeration`   | 1.1                    | Subtle terrain drama.                                                                |
| `DAMP` (prep)            | 0.45                   | Swerve amount: higher = weavier, lower = straighter.                                 |

**A slow camera renders fast.** At 0.54 km/s the camera moves ~18 m/frame, so tiles stay cached and each
`settle()` returns almost immediately; the 720-frame render completed in one pass (no chunk-rendering).

## 5. The complete component

The full, runnable component is `../assets/CesiumFlythrough.tsx` — read it directly. Its shape:

- `loadCesium()` — inject `CESIUM_BASE_URL` + the CDN `Cesium.js`, resolve when loaded.
- init effect — build the Viewer (§1), `setCamera(…, 0)`, `await settle(viewer)`, `continueRender`.
- `settle(viewer)` — loop `viewer.render()` until `globe.tilesLoaded` for landscapes or
  `tileset.tilesLoaded` for cities is stable for ~8 ticks (cap ~600).
- per-frame effect — `delayRender({timeoutInMilliseconds: 60000})` → `setCamera(prog)` → `settle()` → `continueRender`.

## 6. Render

```bash
bunx remotion still   src/index.ts <Comp> out.png --frame=N --gl=angle --timeout=180000   # validate framing/bank first
bunx remotion render  src/index.ts <Comp> out.mp4  --gl=angle --concurrency=1 --timeout=180000
```

`--gl=angle` is mandatory. Use `--concurrency=1`; `settle()` already serializes tile loading.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/cesium/references/3d-flyover-architecture.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/cesium/references/3d-troubleshooting.md ===== -->

# 3D Flyover — troubleshooting

## The headless dead-end (why we render through Remotion)

Cesium's globe **will not draw in a standalone headless Playwright/Chromium** harness. Verified on
Apple M4 (ANGLE Metal active, WebGL working): the skybox/stars render, but the globe surface produces
**zero draw commands** (`scene.frameState.commandList.length === 0`), `globe.tilesLoaded` never goes
true, and frames come back as the black starfield. No network failures; `sampleTerrainMostDetailed`
succeeds (terrain data is reachable). Dead-ends tried, all failed:

- default render loop, manual `scene.render()`, manual `viewer.render()`, headed mode (context-destroyed).

**What works:** render Cesium **through Remotion** — same headless Chrome, but driven by Remotion's frame
loop with these four non-negotiables:

1. `useDefaultRenderLoop = false` — drive frames by hand.
2. Per frame call **`viewer.render()`**, NOT `scene.render()`. `viewer.render()` does the full frame
   (`initializeFrame` → tile streaming → render); `scene.render()` skips frame-init, so tiles never
   advance and the globe never appears. **This is the single most important line.**
3. `contextOptions: { webgl: { preserveDrawingBuffer: true } }` so Remotion's screenshot captures pixels.
4. Gate init + every frame with `delayRender(…, {timeoutInMilliseconds})` — tile loading can exceed Remotion's
   default; use 60–120 s.

The standalone `flythrough.html` / `render.mjs` / `probe.mjs` from the original spike are kept only as the
record of this dead-end. The canonical render path is the Remotion component
(`../assets/CesiumFlythrough.tsx`).

## Symptom → fix

| Symptom                                                   | Cause                                                                                                         | Fix                                                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Frames are black with stars                               | Globe not drawing (headless Playwright, or `scene.render()` used)                                             | Render through Remotion; use `viewer.render()`; `useDefaultRenderLoop=false`.                       |
| Screenshots blank/transparent                             | No `preserveDrawingBuffer`                                                                                    | `contextOptions:{ webgl:{ preserveDrawingBuffer:true } }`.                                          |
| "delayRender timed out"                                   | Cold tiles exceed the default                                                                                 | `delayRender(…, {timeoutInMilliseconds: 120000})` + `--timeout=180000`.                             |
| Globe is a dark/navy sphere                               | Imagery layer didn't attach                                                                                   | `baseLayer:false` then `viewer.imageryLayers.addImageryProvider(...)`.                              |
| High-pitch frame shows a void/starfield above the horizon | No atmosphere                                                                                                 | `viewer.scene.skyAtmosphere.show = true`.                                                           |
| 403 on tiles in headless                                  | Domain-locked MapTiler key                                                                                    | Use an **unrestricted** key.                                                                        |
| Google root tileset returns 403                           | Map Tiles API disabled, billing absent, wrong key, or application restriction blocks local headless rendering | Enable Map Tiles API and billing; restrict the key to that API while allowing the Remotion request. |
| Google scene shows a duplicate/competing surface          | MapTiler or the Cesium globe is still enabled                                                                 | Do not add MapTiler; set `viewer.scene.globe.show=false`.                                           |
| Google mesh remains coarse                                | Screen-space error is too high or the capture starts before refinement                                        | Lower `maximumScreenSpaceError`; settle on `tileset.tilesLoaded`.                                   |
| WebGL unavailable / software renderer                     | Missing GL flag                                                                                               | Render with `--gl=angle`.                                                                           |
| Camera looks at sky / ground, not terrain                 | Pitch sign / convention                                                                                       | Cesium pitch 0 = horizon, negative = down (inverse of MapLibre); `-(90 - PITCH_FROM_NADIR)`.        |
| Aim/turn-probe clamps near the end                        | Path too short                                                                                                | `PATHKM ≥ TRAVEL_KM + 2·LOOK_AHEAD_KM`; raise `WINDOW_KM` in prep.                                  |
| Path feels like straight-then-corner                      | Douglas-Peucker simplification                                                                                | Use resample → moving-average smooth (see architecture §2), not `turf.simplify`.                    |
| Camera bumps left and right instead of swerving           | Sparse route vertices are still being followed as straight segments                                           | Keep `pathSmoothingPasses={3}`; use sparse intentional control points and arc-length movement.      |

## Gotchas checklist

- **`viewer.render()`, never `scene.render()`** per frame. The single biggest trap.
- Cesium loads from **CDN**; set `window.CESIUM_BASE_URL` _before_ injecting the script.
- `preserveDrawingBuffer: true` or screenshots are blank.
- `delayRender` uses `timeoutInMilliseconds`; set it to at least 60,000.
- Terrain: `baseLayer:false`, then add MapTiler imagery.
- Google: no MapTiler, hide the globe, retain `showCreditsOnScreen:true`.
- Always `skyAtmosphere.show = true`.
- Validate the path's heading-delta probe and render one **still** (framing + bank) before the full mp4.
- Cesium pitch/roll conventions are inverted vs MapLibre.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/cesium/references/3d-troubleshooting.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/mapbox/TECHNIQUE.md ===== -->

---
name: maps-mapbox
description: Make deterministic Remotion 2D map animations with Mapbox GL JS and Turf. Use when the user chooses Mapbox for animated routes, map markers, labels, camera movement, or Mapbox styles.
metadata:
  tags: map, map animation, mapbox, turf, geojson, route animation
---

Use Mapbox GL JS for rendering maps in Remotion when the user wants Mapbox styles or higher-fidelity map visuals and has a Mapbox access token. Use Turf for geospatial operations such as great-circle routes, distances, slicing lines, and positions along routes.

Use this technique only when the user has a Mapbox access token and wants Mapbox styles or data.

## Core rules

- Prefer `@turf/turf` for geospatial work. Do not hand-roll distance, great-circle, route slicing, or coordinate interpolation unless the user explicitly needs a custom non-geodesic effect.
- Use GeoJSON sources and Mapbox layers for lines, markers, and labels. Avoid DOM `Marker` elements unless the user specifically asks for HTML markers.
- Keep the live map camera static by default. Before moving it on every frame, read [moving-map stability](references/render-stability.md). Prefer a fixed map plate for satellite imagery, hillshade, or a modest 2D reframe.
- Use a live per-frame camera only after rendering a short MP4 and checking for shimmer. This 2D technique does not provide genuine terrain, pitch, bearing, or banking.
- Disable non-deterministic map behavior: `interactive: false`, `fadeDuration: 0`.
- Drive animation from `useCurrentFrame()`; do not use CSS transitions or browser-timed animation.
- Use `delayRender()` / `continueRender()` around map loading and per-frame map updates.
- Set `preserveDrawingBuffer: true` and render WebGL with `bunx remotion ... --gl=angle`.
- Before continuing the initial render, add sources/layers, apply the frame-0 camera with `jumpTo()` or `setFreeCameraOptions()`, then wait for `idle`.
- Do not add a `mapInstance.remove()` cleanup function; it can interfere with Remotion's render lifecycle.
- Use Mapbox style URLs such as `mapbox://styles/mapbox/standard` or a user-provided custom style.
- Do not install `@types/mapbox-gl`; Mapbox GL JS ships its own types.
- Keep required provider attribution visible and verify current provider terms before rendering.
- Record the source and effective date of custom or disputed geography.
- Inspect rendered pixels, not only Studio playback, at every required aspect ratio.

Coordinates in Mapbox, Turf, and GeoJSON are `[longitude, latitude]`.

```ts
const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];
```

## Prerequisites

Install Mapbox GL JS and Turf with the project's package manager.

```bash
npm i mapbox-gl @turf/turf
```

```bash
bun i mapbox-gl @turf/turf
```

```bash
yarn add mapbox-gl @turf/turf
```

```bash
pnpm i mapbox-gl @turf/turf
```

Import the Mapbox CSS once in the component or an app-level stylesheet:

```ts
import 'mapbox-gl/dist/mapbox-gl.css';
```

Mapbox requires a public access token. Prefer passing it as an input prop or reading it from an environment variable that is available to the bundled Remotion code.

```ts
const mapboxAccessToken = process.env.REMOTION_MAPBOX_TOKEN;

if (!mapboxAccessToken) {
	throw new Error('Set REMOTION_MAPBOX_TOKEN to render Mapbox maps.');
}
```

## Basic map example

```tsx
import {useEffect, useRef, useState} from 'react';
import {useDelayRender, useVideoConfig} from 'remotion';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];

const mapboxAccessToken = process.env.REMOTION_MAPBOX_TOKEN;

if (!mapboxAccessToken) {
	throw new Error('Set REMOTION_MAPBOX_TOKEN to render Mapbox maps.');
}

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const {delayRender, continueRender} = useDelayRender();
	const {width, height} = useVideoConfig();
	const [loadingHandle] = useState(() => delayRender('Loading Mapbox map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		const mapInstance = new mapboxgl.Map({
			accessToken: mapboxAccessToken,
			container: containerRef.current,
			style: 'mapbox://styles/mapbox/standard',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.jumpTo({center: zurich, zoom: 7});
			mapInstance.once('idle', () => {
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	return (
		<>
			<div ref={containerRef} style={{width, height, position: 'absolute'}} />
		</>
	);
};
```

Animated examples should keep the loaded map in React state and skip per-frame updates until that state is set.

## Animated flight route example

This example shows the recommended pattern for route animations:

- Turf creates the route and markers.
- Turf slices the route for line reveal animation.
- Mapbox renders the route with GeoJSON sources and layers.
- The camera uses `jumpTo()` with animated center, zoom, bearing, and pitch.
- Frame 0 is prepared before `continueRender()`.

```tsx
import * as turf from '@turf/turf';
import {useEffect, useRef, useState} from 'react';
import {
	AbsoluteFill,
	Easing,
	interpolate,
	useCurrentFrame,
	useDelayRender,
	useVideoConfig,
} from 'remotion';
import mapboxgl, {type GeoJSONSource, type Map} from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];

const mapboxAccessToken = process.env.REMOTION_MAPBOX_TOKEN;

if (!mapboxAccessToken) {
	throw new Error('Set REMOTION_MAPBOX_TOKEN to render Mapbox maps.');
}

const greatCircleLine = (from: [number, number], to: [number, number]) => {
	const route = turf.greatCircle(from, to, {npoints: 100});

	if (route.geometry.type === 'LineString') {
		return turf.lineString(route.geometry.coordinates);
	}

	// Great-circle routes crossing the antimeridian can become MultiLineString.
	// Keep the example valid by choosing the longest segment.
	const longestSegment = route.geometry.coordinates.reduce((longest, segment) => {
		return segment.length > longest.length ? segment : longest;
	});

	return turf.lineString(longestSegment);
};

const targetRoute = greatCircleLine(zurich, newYork);
const targetRouteDistance = turf.length(targetRoute);

const cityMarkers = turf.featureCollection([
	turf.point(zurich, {name: 'Zurich'}),
	turf.point(newYork, {name: 'New York'}),
]);

const clampProgress = (progress: number) => Math.min(1, Math.max(0, progress));

const distanceAlong = (totalDistance: number, progress: number) => {
	// Keep the route non-empty at progress 0; Turf can error on zero-length slices.
	return Math.max(0.001, totalDistance * clampProgress(progress));
};

const getPartialTargetRoute = (progress: number) => {
	return turf.lineSliceAlong(
		targetRoute,
		0,
		distanceAlong(targetRouteDistance, progress),
	);
};

const getCameraOptions = (progress: number) => {
	const target = turf.along(
		targetRoute,
		distanceAlong(targetRouteDistance, progress),
	).geometry.coordinates as [number, number];

	return {
		center: target,
		zoom: interpolate(progress, [0, 0.5, 1], [7, 2.4, 8], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		}),
		bearing: interpolate(progress, [0, 1], [-20, 35], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
		}),
		pitch: interpolate(progress, [0, 0.25, 0.75, 1], [25, 55, 55, 30], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		}),
	};
};

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const frame = useCurrentFrame();
	const {delayRender, continueRender} = useDelayRender();
	const {durationInFrames, height, width} = useVideoConfig();
	const [map, setMap] = useState<Map | null>(null);
	const [loadingHandle] = useState(() => delayRender('Loading Mapbox map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		const mapInstance = new mapboxgl.Map({
			accessToken: mapboxAccessToken,
			container: containerRef.current,
			style: 'mapbox://styles/mapbox/standard',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.addSource('trace', {
				type: 'geojson',
				data: getPartialTargetRoute(0),
			});

			mapInstance.addLayer({
				id: 'trace-line',
				type: 'line',
				source: 'trace',
				layout: {
					'line-cap': 'round',
					'line-join': 'round',
				},
				paint: {
					'line-color': '#111111',
					'line-width': 7,
				},
			});

			mapInstance.addSource('city-markers', {
				type: 'geojson',
				data: cityMarkers,
			});

			mapInstance.addLayer({
				id: 'city-marker-dots',
				type: 'circle',
				source: 'city-markers',
				paint: {
					'circle-color': '#f03b20',
					'circle-radius': 12,
					'circle-stroke-color': '#ffffff',
					'circle-stroke-width': 4,
				},
			});

			mapInstance.addLayer({
				id: 'city-marker-labels',
				type: 'symbol',
				source: 'city-markers',
				layout: {
					'text-allow-overlap': true,
					'text-anchor': 'top',
					'text-field': ['get', 'name'],
					'text-offset': [0, 0.9],
					'text-size': 28,
				},
				paint: {
					'text-color': '#111111',
					'text-halo-color': '#ffffff',
					'text-halo-width': 3,
				},
			});

			mapInstance.jumpTo(getCameraOptions(0));
			mapInstance.once('idle', () => {
				setMap(mapInstance);
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	useEffect(() => {
		if (!map) {
			return;
		}

		const handle = delayRender('Rendering Mapbox frame');
		const timelineProgress = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
		});
		const travelProgress = interpolate(timelineProgress, [0.2, 0.82], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		});
		const trace = map.getSource('trace') as GeoJSONSource | undefined;

		trace?.setData(getPartialTargetRoute(travelProgress));
		map.jumpTo(getCameraOptions(travelProgress));

		map.once('idle', () => continueRender(handle));
		// Force an idle event even if the camera parameters are unchanged from the previous frame.
		map.triggerRepaint();
	}, [continueRender, delayRender, durationInFrames, frame, map]);

	return (
		<AbsoluteFill style={{backgroundColor: '#e8eef3'}}>
			<div ref={containerRef} style={{height, position: 'absolute', width}} />
		</AbsoluteFill>
	);
};
```

## Camera guidance

For a validated live-camera route animation, animate `center`, `zoom`, `bearing`, and `pitch` with `jumpTo()`:

```ts
map.jumpTo({
	center,
	zoom,
	bearing,
	pitch,
});
```

Keep route progress and camera progress separate if the camera needs to lead, lag, zoom out, or zoom back in. For cinematic 3D camera moves, load the 3D flyover branch from the parent skill.

## Lines

Use GeoJSON sources for lines. Unless the user asks, do not add glow effects or extra decorative points.

For geodesic flight routes, use Turf:

```ts
const line = greatCircleLine(start, end);
const distance = turf.length(line);
const partialLine = turf.lineSliceAlong(
	line,
	0,
	// Keep the route non-empty at progress 0.
	Math.max(0.001, distance * progress),
);
```

For a visually straight line on the map, use a simple GeoJSON `LineString` between the two points instead of `greatCircle()`.

## Markers and labels

Use map-native GeoJSON layers for markers and labels:

```tsx
mapInstance.addSource('markers', {
	type: 'geojson',
	data: turf.featureCollection([
		turf.point([-118.2437, 34.0522], {name: 'Los Angeles'}),
	]),
});

mapInstance.addLayer({
	id: 'marker-dots',
	type: 'circle',
	source: 'markers',
	paint: {
		'circle-color': '#f03b20',
		'circle-radius': 12,
		'circle-stroke-color': '#ffffff',
		'circle-stroke-width': 4,
	},
});

mapInstance.addLayer({
	id: 'marker-labels',
	type: 'symbol',
	source: 'markers',
	layout: {
		'text-allow-overlap': true,
		'text-anchor': 'top',
		'text-field': ['get', 'name'],
		'text-offset': [0, 0.9],
		'text-size': 28,
	},
	paint: {
		'text-color': '#111111',
		'text-halo-color': '#ffffff',
		'text-halo-width': 3,
	},
});
```

Make marker sizes and label font sizes large enough for the composition resolution.

## Styles

Default to Mapbox Standard:

```ts
style: 'mapbox://styles/mapbox/standard'
```

If the user requests another style, use any valid Mapbox style URL.

## Rendering

For WebGL map renders, prefer single concurrency and ANGLE:

```bash
bunx remotion render [composition-id] out/video.mp4 --gl=angle --concurrency=1
```

Use the equivalent package runner for the project. In npm projects, use `npx`; in Bun projects, use `bunx`.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/mapbox/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/mapbox/references/render-stability.md ===== -->

# Moving Map Render Stability

Read this reference before building a moving 2D MapTiler scene or diagnosing a wavering Remotion render.

## Symptom and cause

If basemap detail shimmers or jitters during a pan/zoom, the likely cause is per-frame `map.jumpTo()`.
Headless MapTiler capture can resample both vector hillshade and satellite imagery differently frame to
frame. Tile retries, easing changes, and label changes do not solve that renderer effect.

## Required pattern: fixed map plate

For any 2D pan/zoom:

1. Render the MapTiler canvas once at the largest required zoom in an oversized container. Size it from the camera route and keep each dimension below the browser's reliable WebGL render-buffer limit (commonly 4096 px). Do **not** blindly use 3×: a 1920×1080 composition becomes 5760 px wide and Chromium may silently downsample it, causing visible pixelation during the CSS zoom.
2. Keep the map's camera static.
3. For each frame, calculate the approved target centre/zoom, then move the canvas with CSS `translate` + `scale`.
4. Apply the same transform to every projected HTML overlay.
5. Continue to animate GeoJSON data and paint properties imperatively; only the renderer camera is frozen.

Keep pitch and bearing constant. Use a 3D engine such as Cesium for genuine changing pitch/bearing or a terrain flythrough.

```ts
const baseZoom = Math.max(start.zoom, end.zoom);
const map = new maptilersdk.Map({
  container,
  style,
  center: end.center,
  zoom: baseZoom,
  pitch: end.pitch ?? 0,
  bearing: end.bearing ?? 0,
  interactive: false,
  fadeDuration: 0,
  canvasContextAttributes: {preserveDrawingBuffer: true},
});

// Per Remotion frame. `camera` is the approved centre/zoom interpolation.
const projected = map.project(camera.center);
const scale = 2 ** (camera.zoom - baseZoom);
const plate = {
  transform: `translate(${width / 2 - projected.x * scale}px, ${height / 2 - projected.y * scale}px) scale(${scale})`,
  transformOrigin: "0 0",
};

// Convert label projection with exactly the same plate transform.
const labelX = labelPoint.x * scale + width / 2 - projected.x * scale;
const labelY = labelPoint.y * scale + height / 2 - projected.y * scale;
```

### Plate sizing and sharpness

- Render at the maximum zoom reached by **any** camera waypoint, including intermediate or hold cameras. The CSS scale should never exceed `1`; otherwise the plate is being enlarged.
- Centre the frozen map on the midpoint of the camera route's geographic extent, not automatically on the final camera. This minimizes required overscan.
- Keep the largest canvas dimension at or below 4096 px unless the actual render environment has been tested with a larger `MAX_RENDERBUFFER_SIZE`.
- For 1920×1080, a 3840×2160 plate is a safe default. For 1080×1920, use approximately 2700×3840 when the route needs extra horizontal pan room.
- If the route cannot fit within that plate at the required zoom, split the shot into two fixed plates with a deliberate editorial transition. Do not trade sharpness for one enormous canvas.
- Distinguish failure modes: repeating shimmer means the live renderer is moving; steadily soft tiles during a CSS push means the fixed plate is underspecified, internally downsampled, or being scaled above `1`.

## Verification

- Render a short MP4, not only a Studio preview.
- Inspect static terrain texture and satellite detail while the camera moves.
- If any underlying map detail wavers, use the fixed map plate. Do not approve it as a minor preview artefact.
- Render WebGL with `--gl=angle`, `preserveDrawingBuffer:true`, and conservative concurrency (`1`) while validating.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/mapbox/references/render-stability.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/maplibre/TECHNIQUE.md ===== -->

---
name: maps-maplibre
description: Make deterministic Remotion 2D map animations with MapLibre GL JS and Turf. Use when the user chooses MapLibre for animated routes, map markers, labels, and camera movement.
metadata:
  tags: map, map animation, maplibre, turf, geojson, route animation
---

Use MapLibre GL JS for rendering maps in Remotion. Use Turf for geospatial operations such as great-circle routes, distances, slicing lines, and positions along routes.

## Core rules

- Prefer `@turf/turf` for geospatial work. Do not hand-roll distance, great-circle, route slicing, or coordinate interpolation unless the user explicitly needs a custom non-geodesic effect.
- Use GeoJSON sources and MapLibre layers for lines, markers, and labels. Avoid DOM `Marker` elements unless the user specifically asks for HTML markers.
- Keep the live map camera static by default. Before moving it on every frame, read [moving-map stability](references/render-stability.md). Prefer a fixed map plate for satellite imagery, hillshade, or a modest 2D reframe.
- Use a live per-frame camera only after rendering a short MP4 and checking for shimmer. This 2D technique does not provide genuine terrain, pitch, bearing, or banking.
- Disable non-deterministic map behavior: `interactive: false`, `fadeDuration: 0`.
- Drive animation from `useCurrentFrame()`; do not use CSS transitions or browser-timed animation.
- Use `delayRender()` / `continueRender()` around map loading and per-frame map updates.
- Set `preserveDrawingBuffer: true` and render WebGL with `bunx remotion ... --gl=angle`.
- Before continuing the initial render, add sources/layers, apply the frame-0 camera with `jumpTo()`, then wait for `idle`.
- Do not add a `mapInstance.remove()` cleanup function; it can interfere with Remotion's render lifecycle.
- Use standard MapLibre style JSON URLs and layer/source APIs.
- Do not install `@types/maplibre-gl`; MapLibre ships its own types.
- Keep required provider attribution visible and verify the current terms of the chosen style and tile providers before rendering.
- Record the source and effective date of custom or disputed geography.
- Inspect rendered pixels, not only Studio playback, at every required aspect ratio.

Coordinates in MapLibre, Turf, and GeoJSON are `[longitude, latitude]`.

```ts
const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];
```

## Prerequisites

Install MapLibre and Turf with the project's package manager.

```bash
npm i maplibre-gl @turf/turf
```

```bash
bun i maplibre-gl @turf/turf
```

```bash
yarn add maplibre-gl @turf/turf
```

```bash
pnpm i maplibre-gl @turf/turf
```

Import the MapLibre CSS once in the component or an app-level stylesheet:

```ts
import 'maplibre-gl/dist/maplibre-gl.css';
```

## Basic map example

```tsx
import {useEffect, useRef, useState} from 'react';
import {useDelayRender, useVideoConfig} from 'remotion';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const {delayRender, continueRender} = useDelayRender();
	const {width, height} = useVideoConfig();
	const [loadingHandle] = useState(() => delayRender('Loading map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		maplibregl.setWorkerUrl(
			URL.createObjectURL(
				new Blob(
					[`import "https://unpkg.com/maplibre-gl@${maplibregl.getVersion()}/dist/maplibre-gl-worker.mjs";`],
					{type: 'text/javascript'},
				),
			),
		);

		const mapInstance = new maplibregl.Map({
			container: containerRef.current,
			style: 'https://demotiles.maplibre.org/style.json',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.jumpTo({center: zurich, zoom: 7});
			mapInstance.once('idle', () => {
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	return (
		<>
			<div ref={containerRef} style={{width, height, position: 'absolute'}} />
		</>
	);
};
```

Animated examples should keep the loaded map in React state and skip per-frame updates until that state is set.

## Animated flight route example

This example shows the recommended pattern for route animations:

- Turf creates the route and markers.
- Turf slices the route for line reveal animation.
- The camera has a separate route from the target route.
- MapLibre's `calculateCameraOptionsFromTo()` is used for camera movement.
- Frame 0 is prepared before `continueRender()`.

```tsx
import * as turf from '@turf/turf';
import {useEffect, useRef, useState} from 'react';
import {
	AbsoluteFill,
	Easing,
	interpolate,
	useCurrentFrame,
	useDelayRender,
	useVideoConfig,
} from 'remotion';
import * as maplibregl from 'maplibre-gl';
import {type GeoJSONSource, type Map} from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];

const greatCircleLine = (from: [number, number], to: [number, number]) => {
	const route = turf.greatCircle(from, to, {npoints: 100});

	if (route.geometry.type === 'LineString') {
		return turf.lineString(route.geometry.coordinates);
	}

	// Great-circle routes crossing the antimeridian can become MultiLineString.
	// Keep the example valid by choosing the longest segment.
	const longestSegment = route.geometry.coordinates.reduce((longest, segment) => {
		return segment.length > longest.length ? segment : longest;
	});

	return turf.lineString(longestSegment);
};

const targetRoute = greatCircleLine(zurich, newYork);
const targetRouteDistance = turf.length(targetRoute);

const cameraRoute = greatCircleLine(zurich, newYork);
const cameraRouteDistance = turf.length(cameraRoute);

const cityMarkers = turf.featureCollection([
	turf.point(zurich, {name: 'Zurich'}),
	turf.point(newYork, {name: 'New York'}),
]);

const clampProgress = (progress: number) => Math.min(1, Math.max(0, progress));

const distanceAlong = (totalDistance: number, progress: number) => {
	// Keep the route non-empty at progress 0; Turf can error on zero-length slices.
	return Math.max(0.001, totalDistance * clampProgress(progress));
};

const getPartialTargetRoute = (progress: number) => {
	return turf.lineSliceAlong(
		targetRoute,
		0,
		distanceAlong(targetRouteDistance, progress),
	);
};

const getCameraOptions = (
	map: Map,
	progress: number,
	cameraAltitudeMeters: number,
	cameraLatitudeOffset: number,
) => {
	const target = turf.along(
		targetRoute,
		distanceAlong(targetRouteDistance, progress),
	).geometry.coordinates;
	const camera = turf.along(
		cameraRoute,
		distanceAlong(cameraRouteDistance, progress),
	).geometry.coordinates;

	return map.calculateCameraOptionsFromTo(
		new maplibregl.LngLat(camera[0], camera[1] - cameraLatitudeOffset),
		cameraAltitudeMeters,
		new maplibregl.LngLat(target[0], target[1]),
	);
};

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const frame = useCurrentFrame();
	const {delayRender, continueRender} = useDelayRender();
	const {durationInFrames, height, width} = useVideoConfig();
	const [map, setMap] = useState<Map | null>(null);
	const [loadingHandle] = useState(() => delayRender('Loading MapLibre map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		maplibregl.setWorkerUrl(
			URL.createObjectURL(
				new Blob(
					[`import "https://unpkg.com/maplibre-gl@${maplibregl.getVersion()}/dist/maplibre-gl-worker.mjs";`],
					{type: 'text/javascript'},
				),
			),
		);

		const mapInstance = new maplibregl.Map({
			container: containerRef.current,
			style: 'https://demotiles.maplibre.org/style.json',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.addSource('trace', {
				type: 'geojson',
				data: getPartialTargetRoute(0),
			});

			mapInstance.addLayer({
				id: 'trace-line',
				type: 'line',
				source: 'trace',
				layout: {
					'line-cap': 'round',
					'line-join': 'round',
				},
				paint: {
					'line-color': '#111111',
					'line-width': 7,
				},
			});

			mapInstance.addSource('city-markers', {
				type: 'geojson',
				data: cityMarkers,
			});

			mapInstance.addLayer({
				id: 'city-marker-dots',
				type: 'circle',
				source: 'city-markers',
				paint: {
					'circle-color': '#f03b20',
					'circle-radius': 12,
					'circle-stroke-color': '#ffffff',
					'circle-stroke-width': 4,
				},
			});

			mapInstance.addLayer({
				id: 'city-marker-labels',
				type: 'symbol',
				source: 'city-markers',
				layout: {
					'text-allow-overlap': true,
					'text-anchor': 'top',
					'text-field': ['get', 'name'],
					'text-offset': [0, 0.9],
					'text-size': 28,
				},
				paint: {
					'text-color': '#111111',
					'text-halo-color': '#ffffff',
					'text-halo-width': 3,
				},
			});

			mapInstance.jumpTo(getCameraOptions(mapInstance, 0, 180000, 1.1));
			mapInstance.once('idle', () => {
				setMap(mapInstance);
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	useEffect(() => {
		if (!map) {
			return;
		}

		const handle = delayRender('Rendering MapLibre frame');
		const timelineProgress = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
		});
		const travelProgress = interpolate(timelineProgress, [0.2, 0.82], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		});
		const cameraAltitudeMeters = interpolate(
			timelineProgress,
			[0, 0.28, 0.74, 1],
			[180000, 2200000, 2200000, 180000],
			{
				extrapolateLeft: 'clamp',
				extrapolateRight: 'clamp',
				easing: Easing.bezier(0.645, 0.045, 0.355, 1),
			},
		);
		const cameraLatitudeOffset = interpolate(
			timelineProgress,
			[0, 0.28, 0.74, 1],
			[1.1, 8, 8, 1.1],
			{
				extrapolateLeft: 'clamp',
				extrapolateRight: 'clamp',
				easing: Easing.bezier(0.645, 0.045, 0.355, 1),
			},
		);
		const trace = map.getSource('trace') as GeoJSONSource | undefined;

		trace?.setData(getPartialTargetRoute(travelProgress));
		map.jumpTo(
			getCameraOptions(
				map,
				travelProgress,
				cameraAltitudeMeters,
				cameraLatitudeOffset,
			),
		);

		map.once('idle', () => continueRender(handle));
		// Force an idle event even if the camera parameters are unchanged from the previous frame.
		map.triggerRepaint();
	}, [continueRender, delayRender, durationInFrames, frame, map]);

	return (
		<AbsoluteFill style={{backgroundColor: '#e8eef3'}}>
			<div ref={containerRef} style={{height, position: 'absolute', width}} />
		</AbsoluteFill>
	);
};
```

## Camera guidance

Use MapLibre's camera helper for camera movement:

```ts
map.calculateCameraOptionsFromTo(cameraLngLat, cameraAltitudeMeters, targetLngLat);
```

A good pattern is to keep two concepts separate:

- `targetRoute`: where the animated line is and where the camera looks.
- `cameraRoute`: where the camera moves.

Then use Turf to read positions from both routes for the same progress value:

```ts
const target = turf.along(targetRoute, targetDistance * progress).geometry.coordinates;
const camera = turf.along(cameraRoute, cameraDistance * progress).geometry.coordinates;

map.jumpTo(
	map.calculateCameraOptionsFromTo(
		new maplibregl.LngLat(camera[0], camera[1]),
		cameraAltitudeMeters,
		new maplibregl.LngLat(target[0], target[1]),
	),
);
```

For zoom-out / travel / zoom-in animations, animate travel progress separately from camera altitude. Camera altitude is measured in meters. This avoids heavy custom camera math.

## Lines

Use GeoJSON sources for lines. Unless the user asks, do not add glow effects or extra decorative points.

For geodesic flight routes, use Turf:

```ts
const line = greatCircleLine(start, end);
const distance = turf.length(line);
const partialLine = turf.lineSliceAlong(
	line,
	0,
	// Keep the route non-empty at progress 0.
	Math.max(0.001, distance * progress),
);
```

For a visually straight line on the map, use a simple GeoJSON `LineString` between the two points instead of `greatCircle()`.

## Markers and labels

Use map-native GeoJSON layers for markers and labels:

```tsx
mapInstance.addSource('markers', {
	type: 'geojson',
	data: turf.featureCollection([
		turf.point([-118.2437, 34.0522], {name: 'Los Angeles'}),
	]),
});

mapInstance.addLayer({
	id: 'marker-dots',
	type: 'circle',
	source: 'markers',
	paint: {
		'circle-color': '#f03b20',
		'circle-radius': 12,
		'circle-stroke-color': '#ffffff',
		'circle-stroke-width': 4,
	},
});

mapInstance.addLayer({
	id: 'marker-labels',
	type: 'symbol',
	source: 'markers',
	layout: {
		'text-allow-overlap': true,
		'text-anchor': 'top',
		'text-field': ['get', 'name'],
		'text-offset': [0, 0.9],
		'text-size': 28,
	},
	paint: {
		'text-color': '#111111',
		'text-halo-color': '#ffffff',
		'text-halo-width': 3,
	},
});
```

Make marker sizes and label font sizes large enough for the composition resolution.

## Styles

Default to the stock MapLibre demo style:

```ts
style: 'https://demotiles.maplibre.org/style.json'
```

If the user requests another style, use any valid MapLibre style JSON URL.

## Rendering

For WebGL map renders, prefer single concurrency and ANGLE:

```bash
bunx remotion render [composition-id] out/video.mp4 --gl=angle --concurrency=1
```

Use the equivalent package runner for the project. In npm projects, use `npx`; in Bun projects, use `bunx`.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/maplibre/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/maplibre/references/render-stability.md ===== -->

# Moving Map Render Stability

Read this reference before building a moving 2D MapTiler scene or diagnosing a wavering Remotion render.

## Symptom and cause

If basemap detail shimmers or jitters during a pan/zoom, the likely cause is per-frame `map.jumpTo()`.
Headless MapTiler capture can resample both vector hillshade and satellite imagery differently frame to
frame. Tile retries, easing changes, and label changes do not solve that renderer effect.

## Required pattern: fixed map plate

For any 2D pan/zoom:

1. Render the MapTiler canvas once at the largest required zoom in an oversized container. Size it from the camera route and keep each dimension below the browser's reliable WebGL render-buffer limit (commonly 4096 px). Do **not** blindly use 3×: a 1920×1080 composition becomes 5760 px wide and Chromium may silently downsample it, causing visible pixelation during the CSS zoom.
2. Keep the map's camera static.
3. For each frame, calculate the approved target centre/zoom, then move the canvas with CSS `translate` + `scale`.
4. Apply the same transform to every projected HTML overlay.
5. Continue to animate GeoJSON data and paint properties imperatively; only the renderer camera is frozen.

Keep pitch and bearing constant. Use a 3D engine such as Cesium for genuine changing pitch/bearing or a terrain flythrough.

```ts
const baseZoom = Math.max(start.zoom, end.zoom);
const map = new maptilersdk.Map({
  container,
  style,
  center: end.center,
  zoom: baseZoom,
  pitch: end.pitch ?? 0,
  bearing: end.bearing ?? 0,
  interactive: false,
  fadeDuration: 0,
  canvasContextAttributes: {preserveDrawingBuffer: true},
});

// Per Remotion frame. `camera` is the approved centre/zoom interpolation.
const projected = map.project(camera.center);
const scale = 2 ** (camera.zoom - baseZoom);
const plate = {
  transform: `translate(${width / 2 - projected.x * scale}px, ${height / 2 - projected.y * scale}px) scale(${scale})`,
  transformOrigin: "0 0",
};

// Convert label projection with exactly the same plate transform.
const labelX = labelPoint.x * scale + width / 2 - projected.x * scale;
const labelY = labelPoint.y * scale + height / 2 - projected.y * scale;
```

### Plate sizing and sharpness

- Render at the maximum zoom reached by **any** camera waypoint, including intermediate or hold cameras. The CSS scale should never exceed `1`; otherwise the plate is being enlarged.
- Centre the frozen map on the midpoint of the camera route's geographic extent, not automatically on the final camera. This minimizes required overscan.
- Keep the largest canvas dimension at or below 4096 px unless the actual render environment has been tested with a larger `MAX_RENDERBUFFER_SIZE`.
- For 1920×1080, a 3840×2160 plate is a safe default. For 1080×1920, use approximately 2700×3840 when the route needs extra horizontal pan room.
- If the route cannot fit within that plate at the required zoom, split the shot into two fixed plates with a deliberate editorial transition. Do not trade sharpness for one enormous canvas.
- Distinguish failure modes: repeating shimmer means the live renderer is moving; steadily soft tiles during a CSS push means the fixed plate is underspecified, internally downsampled, or being scaled above `1`.

## Verification

- Render a short MP4, not only a Studio preview.
- Inspect static terrain texture and satellite detail while the camera moves.
- If any underlying map detail wavers, use the fixed map plate. Do not approve it as a minor preview artefact.
- Render WebGL with `--gl=angle`, `preserveDrawingBuffer:true`, and conservative concurrency (`1`) while validating.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/maplibre/references/render-stability.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/maptiler/TECHNIQUE.md ===== -->

# MapTiler maps in Remotion

MapTiler is a good solution for map animations where geographics features should be drawn as annotations on top of the map: Country borders, rivers, labels for POIs.

## MapTiler SDK (`@maptiler/sdk`)

Draw the basemap plus MapTiler Planet vector layers and custom GeoJSON into a WebGL canvas. Default styled-vector starting point: `MapStyle.BASIC`; satellite is an equally valid choice.

## Remotion

Imperatively update `setData`/`setPaintProperty`.

Use `jumpTo` only for a static shot, or a fixed map plate for any pan/zoom.
Gate with [`delayRender`](https://www.remotion.dev/docs/delay-render.md) until `map.once('idle')`.

Use `preserveDrawingBuffer:true`.

Render labels as positioned [`<Interactive.Div>`](https://www.remotion.dev/docs/interactive.md) elements.

Env `REMOTION_MAPTILER_KEY` (unrestricted). Init the map once (ref guard); update imperatively per frame.

When constructing MapLibre/MapTiler layer objects, omit optional properties that are absent.  
In particular, use `...(layer.filter ? {filter: layer.filter} : {})`; do not pass `filter: undefined`. An undefined filter can suppress the layer while separately created halo or border layers continue rendering, producing missing country fills and dark marker halos with no coloured cores.

Drive animation from `useCurrentFrame()` rather than CSS transitions or browser timers.  

## Choose the source for each map element

Do not begin by manufacturing GeoJSON. First check whether MapTiler Planet already exposes the element as filtered vector data.

### MapTiler vector

Use it when the feature exists in a provider `source-layer`, its attributes support an exact filter, and provider geometry is editorially acceptable.

### Hybrid

Use it when ordinary geographic context can come from MapTiler while the claim depends on custom
evidence.

Animate each layer according to its source and meaning.

MapTiler vector features remain split across tiles. Do not use them for a semantic start-to-end line draw; extract, verify, order, and bake that element to GeoJSON first. Read **`references/map-data-sources.md`** and reuse **`assets/MapTilerVectorElement.ts`** for provider-layer setup and per-frame paint updates.

## Motion stability

**Do not call `map.jumpTo()` on every Remotion frame when the camera moves.** In headless capture it can make both MapTiler hillshade **and satellite imagery** shimmer/jitter, even when the source tiles load correctly. This is renderer resampling, not a data, network, or label problem.

For the implementation, read **`references/render-stability.md`** before building or debugging any moving map. It contains the fixed-map-plate recipe, diagnostics, and render checks.

- Use the live MapTiler camera only for a static shot.
- Keep pitch and bearing constant for a fixed plate. This technique does not implement a genuine changing 3D camera.
- Verify the moving preview and a short rendered MP4 before approving a beat. If any basemap detail wavers, switch to the fixed-plate pattern; do not try to solve it with tile retries or camera easing.

## Drawing rivers

Use `turf.lineSliceAlong(line, 0, lineKm*reveal)` to draw rivers.

## Source selection

Use MapTiler vector layers for suitable provider features and custom GeoJSON for story-specific or ordered geometry. If the beat needs country-entry triggers or a progressive line draw, run `scripts/prep-geo.mjs` to bake `country-meta.json`, `borders.geojson`, and the ordered line. Details → `references/map-data-sources.md` and `references/map-geo-prep.md`.

## Keep it minmal

Strip clutter on `load`: remove `symbol` layers (place labels) and `/other border/i` (admin-1 inner borders); hide the logo via CSS. Keep country + disputed borders.

## Files

Use as reference:

- `assets/RiverReveal.tsx` — the main component.
- `assets/MapTilerVectorElement.ts` — filtered MapTiler Planet elements.
- `assets/CountryLabel.tsx` — reusable example label.
- `assets/tokens.ts` — example palette and durations.
- `assets/example-Root.tsx` — minimal composition scaffold.
- `assets/sample-data/` — example route and generated country metadata.
- `scripts/prep-geo.mjs` — geo pipeline.
- `references/map-explainer-architecture.md` — timing model and implementation.
- `references/map-data-sources.md` — provider vector versus custom GeoJSON selection.
- `references/map-geo-prep.md` — basemap stripping and geo preparation.
- `references/render-stability.md` — camera motion and stable headless renders.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/maptiler/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/maptiler/references/map-data-sources.md ===== -->

# Map element data sources

Choose the source independently for every story element. A single map can—and often should—mix
provider vectors with custom geodata.

## Decision rule

Use a MapTiler Planet vector layer when the feature already exists there, its attributes support an
editorially precise filter, and provider geometry is acceptable for the claim. Use custom GeoJSON when
the feature is absent, proposed, historical, disputed, corrected, privately sourced, or needs ordered
geometry for a deterministic draw.

| Requirement                                                                 | MapTiler vector layer | Custom GeoJSON                              |
| --------------------------------------------------------------------------- | --------------------- | ------------------------------------------- |
| Roads, waterways, water, boundaries, land cover, or other standard context  | Prefer                | Use only when provider data is insufficient |
| Basemap-consistent geometry without a duplicate local dataset               | Prefer                | No                                          |
| Proposed, historical, classified, corrected, or production-specific element | No                    | Prefer                                      |
| Fade, colour, width, radius, blur, or fill-opacity animation                | Yes                   | Yes                                         |
| Feature-state highlight when a stable feature ID exists                     | Yes                   | Yes                                         |
| Deterministic source-to-end line draw or perimeter draw                     | Bake first            | Prefer                                      |
| Geometry editing, morphing, clipping, or exact sequencing                   | No                    | Prefer                                      |

Provider alignment is not proof of correctness. Inspect the attributes and geometry against the
editorial source before presenting a provider feature as evidence.

## MapTiler vector mode

MapTiler Planet is a vector tile source. Add it once, then build story layers with a
`source-layer` and an exact attribute filter. Read the current MapTiler Planet schema before choosing
layer names or fields.

Common layer categories include `waterway`, `water`, `transportation`, `boundary`, `landcover`, and
`poi`; availability, fields, and zoom ranges vary by schema version.

```ts
import {addMapTilerVectorElement, setVectorElementPaint} from "./MapTilerVectorElement";

addMapTilerVectorElement(map, process.env.REMOTION_MAPTILER_KEY!, {
  id: "story-river",
  sourceLayer: "waterway",
  type: "line",
  filter: [
    "all",
    ["==", ["get", "class"], "river"],
    ["==", ["coalesce", ["get", "name_en"], ["get", "name"]], "Yarlung Tsangpo"],
  ],
  layout: {"line-cap": "round", "line-join": "round"},
  paint: {
    "line-color": "#E8F7FF",
    "line-width": 3,
    "line-opacity": 0,
  },
});

setVectorElementPaint(map, "story-river", {
  "line-opacity": reveal,
  "line-width": 2 + reveal * 2,
});
```

Animate provider features by changing paint properties from the Remotion frame: opacity, colour,
width, blur, fill opacity, circle radius, or symbol opacity. Use feature state only when the source
provides stable IDs and the selection remains deterministic across tiles.

Do not treat a tiled line as one ordered path. Vector tiles split features at tile boundaries, so a
source-to-mouth or start-to-end draw has no reliable global order. If that motion carries meaning,
extract and verify the complete feature, order it once, save it as GeoJSON, and use the custom mode.

## Custom geodata mode

Use the bundled `../assets/RiverReveal.tsx` and `../scripts/prep-geo.mjs` pattern for custom GeoJSON. This mode owns
the exact geometry and can slice it by distance, calculate entry triggers, draw complete borders, and
produce deterministic sequences.

Custom mode is mandatory when:

- the feature is not in the provider dataset;
- the story uses a proposed route, planned tunnel, historical boundary, disputed interpretation, or
  non-public dataset;
- provider geometry was editorially corrected;
- motion must travel through the geometry in a verified order;
- a complete off-screen boundary matters and a viewport query would silently crop it.

## Hybrid mode

Use provider vectors for ordinary contextual features and custom GeoJSON for the specific claim. For
example: MapTiler waterways and roads as aligned context; a custom proposed tunnel, dam site, disputed
boundary, or verified evacuation area as the highlighted evidence.

Keep provider and custom layers visually distinct when they carry different evidentiary weight. Record
the source and effective date of every custom layer in the production notes.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/maptiler/references/map-data-sources.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/maptiler/references/map-explainer-architecture.md ===== -->

# Map Explainer — architecture reference

Deep detail behind `TECHNIQUE.md`: the timing model, the river reveal + electric head, the per-country
sequence, and label projection. The supplied values are examples, not a production style system.
The custom-geometry example is `../assets/RiverReveal.tsx` +
`../assets/CountryLabel.tsx` +
`../assets/tokens.ts`. Provider-vector setup is in
`../assets/MapTilerVectorElement.ts`; choose between
the two modes with `data-sources.md`.

## 1. The render harness (per frame)

Init the MapTiler map once (ref guard). On `load`: strip clutter (see `geo-prep.md`), add sources/layers,
wait for `once('idle') → continueRender`. Per frame:

```
delayRender → setData/setPaintProperty → map.once('idle', continueRender) → triggerRepaint
```

`preserveDrawingBuffer:true` so Remotion's screenshot captures the canvas. Render `--gl=angle`.
For an animated camera, read `render-stability.md`: the MapTiler renderer remains static and a CSS plate
transform supplies the camera choreography.

## 2. Timing model — time-based; beat length derived from the sequences

Everything keys off **seconds** (`t = frame / fps`), not reveal-units. The river draws over a window;
each country **triggers when the river reaches it** and runs a fixed sequence. The beat is exactly as
long as the sequences need.

```ts
const RIVER_START = 0.3, RIVER_END = 8.0;            // river draws over this window
const BORDER_S = 2.5, FILL_S = 1.0, LABEL_S = 0.7;   // per-country sequence (constant durations)
const trigger = (c) => RIVER_START + META[c].stop * (RIVER_END - RIVER_START);  // river-arrival time
// beat length = max over c of (trigger(c) + BORDER_S + FILL_S + LABEL_S) + tail
const reveal = interpolate(t, [RIVER_START, RIVER_END], [0,1], { ...clamp, easing: Easing.bezier(0.645, 0.045, 0.355, 1) });
```

**Constant durations matter:** drive the border draw by _time since trigger_, not a slice of the reveal —
otherwise complex or long borders flash by in a fraction of a second.

## 3. Provider-vector animation

MapTiler Planet elements can be animated directly in place. Filter an exact `source-layer` feature,
initialize its paint in the hidden or neutral state, then update paint properties from the Remotion frame.
This works for line, fill, circle, and symbol layers without copying provider geometry into the project.

Do not assume tiled geometry has a global order. Provider features are split at tile boundaries: opacity,
colour, width, blur, radius, fill, and feature-state changes are reliable; semantic start-to-end line
draws are not. Bake ordered GeoJSON when the direction of the draw carries meaning.

## 4. Custom line animation — reveal + electric draw-head

The "electricity" is a **white-hot head** leading the draw — the last few % of the drawn line in its own
bright + glow layers, faded out once the river completes.

```ts
const riverDrawnKm = lineKm * reveal;
map.getSource("river").setData(turf.lineSliceAlong(line, 0, Math.max(0.001, riverDrawnKm)));
const headKm = lineKm * 0.03;
map.getSource("river-head").setData(turf.lineSliceAlong(line, Math.max(0, riverDrawnKm - headKm), Math.max(0.001, riverDrawnKm)));
let headFade = 0;
if (reveal > 0.002 && reveal < 0.999) headFade = 1;
else if (reveal >= 0.999) headFade = 1 - clamp01((t - RIVER_END) / 0.5);  // fade out at the mouth
map.setPaintProperty("river-headglow", "line-opacity", 0.85 * headFade);
map.setPaintProperty("river-head", "line-opacity", headFade);
```

Layers, bottom→top: `river-glow` (electric blue `#49C6FF`, w11, op0.32, blur6) → `river-line`
(icy core `#E8F7FF`, w3) → `river-headglow` (`rgba(120,225,255,.95)`, w16, blur9) → `river-head`
(white `#FFFFFF`, w4.5). **No dark casing** — the bright icy core reads over every fill on its own.

## 5. Country animation — border draws → fill blooms → label rises

Triggered by river arrival, each country runs three sequential phases. The border is a **darker shade**
of the country colour (the electricity is on the river, not here).

```ts
const lt = t - trigger(c);                                   // local seconds since trigger
// 1) complete source border draws on over a constant BORDER_S, multi-segment-safe
const bp = interpolate(clamp01(lt / BORDER_S), [0,1], [0,1], { easing: Easing.bezier(0.645, 0.045, 0.355, 1) });
map.getSource(`trail-${c}`).setData(sliceBorder(DRAW[c], 0, DRAW[c].total * bp));   // COUNTRY_DARK line
// 2) fill blooms in (opacity overshoots, then settles) after the border completes
const fp = clamp01((lt - BORDER_S) / FILL_S);
const fo = interpolate(fp, [0, 0.6, 1], [0, FILL_OPACITY * 1.25, FILL_OPACITY], { ...clamp, easing: Easing.bezier(0.3333333333333333, 1, 0.6666666666666666, 1) });
map.setPaintProperty(`fill-${c}`, "fill-opacity", fp <= 0 ? 0 : fo);
// 3) label rises in after the fill
const lp = clamp01((lt - BORDER_S - FILL_S) / LABEL_S);
```

`sliceBorder(d, fromKm, toKm)` reveals a portion of a complete (possibly multi-segment) border as a
MultiLineString, slicing each segment by cumulative length — no joins across gaps and no viewport crop:

```ts
const sliceBorder = (d, fromKm, toKm) => {
  const out = [];
  for (let i = 0; i < d.segLines.length; i++) {
    const start = d.cum[i], end = start + d.segLen[i];
    const a = Math.max(fromKm, start), b = Math.min(toKm, end);
    if (b - a <= 0.0008) continue;
    out.push(turf.lineSliceAlong(d.segLines[i], a - start, b - start).geometry.coordinates);
  }
  return { type:"Feature", properties:{}, geometry:{ type:"MultiLineString", coordinates: out } };
};
```

Choose fill, border, and river colours in the production's local token file. The bundled token values are
examples only; do not carry a source project's palette into another production.

## 6. Labels — HTML overlay, projected each frame

Labels are React, not map symbols (full typography control). `CountryLabel` is an example accent-rule,
rise-and-fade treatment; select the typeface and final values in the production.
Positioned by projecting the anchor to screen pixels **every frame**, stored in state:

```ts
const p = map.project(META[c].anchor);   // lngLat → screen px (respects the live camera)
pos[c] = { x: p.x, y: p.y, reveal: lp };
setLabels(pos);                          // re-render the overlay; effect deps exclude `labels`
```

`CountryLabel` shows the mechanics: uppercase region name, short accent divider, rise/fade entrance,
and `pointerEvents:none`. Select font, weight, size, spacing, contrast, and colour from the production's
own type and palette system.

## 7. Camera — fixed map plate for any movement

Read `render-stability.md`. Do not use per-frame `map.jumpTo()` for a moving 2D shot; it can shimmer in
headless renders even on satellite imagery. Interpolate the intended camera for the CSS plate transform,
while keeping the MapTiler renderer static.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/maptiler/references/map-explainer-architecture.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/maptiler/references/map-geo-prep.md ===== -->

# Map Explainer — basemap & geo prep

How the basemap is cleaned and how `../scripts/prep-geo.mjs` bakes the per-country data the component reads.

## Basemap styling — strip the clutter

On `load`, remove the basemap's labels and inner admin borders so only your geography reads:

```ts
for (const l of m.getStyle().layers as any[])
  if (l.type === "symbol" || /other border/i.test(l.id)) m.removeLayer(l.id);
```

- `type === "symbol"` → every place/water/road **label** (the "MapTiler labels"). Gone.
- Inner admin-border layer IDs vary by style. Inspect the loaded style, remove state/province/district
  layers as needed, and retain only the context borders the production requires.
- Logo/attribution: `maptilerLogo:false` + `attributionControl:false` aren't always enough — also hide
  via CSS in the component:
  ```tsx
  <style>
    {`
      .maplibregl-ctrl-bottom-left,
      .maplibregl-ctrl-bottom-right,
      .maplibregl-ctrl-attrib,
      .maptiler-logo {
        display: none !important;
      }
    `}
  </style>
  ```

## `../scripts/prep-geo.mjs` → outputs

Reads a routed river GeoJSON + country polygon GeoJSONs; writes:

- **River line** — simplified for a smooth draw. For a braided river, route one source→mouth path through
  the network first: greedy endpoint-chaining bounces between parallel channels. → `src/geo/river-flow.json`.
- **`public/geo/borders.geojson`** — each country's polygon tagged `{country: name}` (one source,
  filtered per country for the fills).
- **`src/geo/country-meta.json`** — per country `{ stop, anchor, border }`.

### `stop` — when a country lights up

Walk the river points; first point inside a country (`turf.booleanPointInPolygon`) = the arc-length
fraction where the river **enters** it. Drives the trigger time. The headwaters country = 0.

### `anchor` — label centre via pole of inaccessibility

The most-interior point of the country (clipped to a per-country **story bbox** so a big country
centres in the relevant region, not its far bulge), then a small operator **nudge**. Pole = grid-sample
inside the polygon, keep the point with max distance to the boundary. **Centroids get pulled to edges —
don't use them.**

```js
const pole = (poly) => {
  const bb = turf.bbox(poly), edge = turf.polygonToLine(poly), N = 46;
  let best = null, bestD = -1;
  for (let i = 0; i <= N; i++) for (let j = 0; j <= N; j++) {
    const p = turf.point([bb[0]+(bb[2]-bb[0])*i/N, bb[1]+(bb[3]-bb[1])*j/N]);
    if (!turf.booleanPointInPolygon(p, poly)) continue;
    const d = turf.pointToLineDistance(p, edge);
    if (d > bestD) { bestD = d; best = p.geometry.coordinates; }
  }
  return best;
};
const ANCHOR_BBOX = { china:[82,27,96,32], india:[76,14,99,31], bangladesh:[86,20,93,27] };  // story regions
const NUDGE = { china:[0,0.6], india:[-1.0,0], bangladesh:[0,-0.6] };                          // operator-directed
```

### `border` — complete source geometry

Preserve every exterior ring from the named country source. Never clip a country or bilateral border to
the framed bbox and never discard an off-screen segment: the geometry may leave the frame naturally.
The renderer handles a MultiLineString by cumulative length, so it remains one timed reveal without
inventing joins across gaps.

## Tuning the geo prep for a new scenario

| Want                              | Knob                                                                 |
| --------------------------------- | -------------------------------------------------------------------- |
| Which countries                   | the country list in `prep-geo.mjs` (+ supply their polygon GeoJSONs) |
| Label centred in the right region | `ANCHOR_BBOX[country]` (the story bbox)                              |
| Nudge a label                     | `NUDGE[country]` (lng, lat offset)                                   |
| What border is drawn              | the complete named source geometry; never the visible extent         |
| When each lights up               | derived from `stop` — depends on the river geometry                  |

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/maptiler/references/map-geo-prep.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/maptiler/references/render-stability.md ===== -->

# Moving Map Render Stability

Read this reference before building a moving 2D MapTiler scene or diagnosing a wavering Remotion render.

## Symptom and cause

If basemap detail shimmers or jitters during a pan/zoom, the likely cause is per-frame `map.jumpTo()`.
Headless MapTiler capture can resample both vector hillshade and satellite imagery differently frame to
frame. Tile retries, easing changes, and label changes do not solve that renderer effect.

## Required pattern: fixed map plate

For any 2D pan/zoom:

1. Render the MapTiler canvas once at the largest required zoom in an oversized container. Size it from the camera route and keep each dimension below the browser's reliable WebGL render-buffer limit (commonly 4096 px). Do **not** blindly use 3×: a 1920×1080 composition becomes 5760 px wide and Chromium may silently downsample it, causing visible pixelation during the CSS zoom.
2. Keep the map's camera static.
3. For each frame, calculate the approved target centre/zoom, then move the canvas with CSS `translate` + `scale`.
4. Apply the same transform to every projected HTML overlay.
5. Continue to animate GeoJSON data and paint properties imperatively; only the renderer camera is frozen.

Keep pitch and bearing constant. Use a 3D engine such as Cesium for genuine changing pitch/bearing or a terrain flythrough.

```ts
const baseZoom = Math.max(start.zoom, end.zoom);
const map = new maptilersdk.Map({
  container,
  style,
  center: end.center,
  zoom: baseZoom,
  pitch: end.pitch ?? 0,
  bearing: end.bearing ?? 0,
  interactive: false,
  fadeDuration: 0,
  canvasContextAttributes: {preserveDrawingBuffer: true},
});

// Per Remotion frame. `camera` is the approved centre/zoom interpolation.
const projected = map.project(camera.center);
const scale = 2 ** (camera.zoom - baseZoom);
const plate = {
  transform: `translate(${width / 2 - projected.x * scale}px, ${height / 2 - projected.y * scale}px) scale(${scale})`,
  transformOrigin: "0 0",
};

// Convert label projection with exactly the same plate transform.
const labelX = labelPoint.x * scale + width / 2 - projected.x * scale;
const labelY = labelPoint.y * scale + height / 2 - projected.y * scale;
```

### Plate sizing and sharpness

- Render at the maximum zoom reached by **any** camera waypoint, including intermediate or hold cameras. The CSS scale should never exceed `1`; otherwise the plate is being enlarged.
- Centre the frozen map on the midpoint of the camera route's geographic extent, not automatically on the final camera. This minimizes required overscan.
- Keep the largest canvas dimension at or below 4096 px unless the actual render environment has been tested with a larger `MAX_RENDERBUFFER_SIZE`.
- For 1920×1080, a 3840×2160 plate is a safe default. For 1080×1920, use approximately 2700×3840 when the route needs extra horizontal pan room.
- If the route cannot fit within that plate at the required zoom, split the shot into two fixed plates with a deliberate editorial transition. Do not trade sharpness for one enormous canvas.
- Distinguish failure modes: repeating shimmer means the live renderer is moving; steadily soft tiles during a CSS push means the fixed plate is underspecified, internally downsampled, or being scaled above `1`.

## Verification

- Render a short MP4, not only a Studio preview.
- Inspect static terrain texture and satellite detail while the camera moves.
- If any underlying map detail wavers, use the fixed map plate. Do not approve it as a minor preview artefact.
- Render WebGL with `--gl=angle`, `preserveDrawingBuffer:true`, and conservative concurrency (`1`) while validating.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/maptiler/references/render-stability.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-maps/techniques/static-map/TECHNIQUE.md ===== -->

---
name: remotion-maps-static
description: Create a deterministic static locator map in Remotion when neither the camera nor geographic data animates.
---

# Static map

Use a static image when the map only provides location context. This is the smallest, fastest, and
most deterministic map technique.

## Build

1. Export or request a map image at the composition's final aspect ratio and at least its rendered
   pixel dimensions.
2. Store the image in the Remotion project's `public/` directory.
3. Render it with `CanvasImage` and `staticFile()`.
4. Add labels or markers as ordinary Remotion elements if they remain fixed.

```tsx
import React from 'react';
import {AbsoluteFill, CanvasImage, staticFile} from 'remotion';

export const StaticMap: React.FC = () => {
	return (
	  <>
  		<CanvasImage
  			src={staticFile('locator-map.png')}
  			style={{width: '100%', height: '100%', objectFit: 'cover'}}
  		/>
		</>
	);
};
```

## Overlays and Interactivity

Follow [Remotion Interactivity](../../../remotion-interactivity/REFERENCE.md) best practices and [Remotion Markup Best practices](../../../remotion-markup/REFERENCE.md) for elements.

<!-- ===== /file: remotion-best-practices/remotion-maps/techniques/static-map/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/3d.md ===== -->

---
name: 3d
description: 3D content in Remotion using Three.js and React Three Fiber.
metadata:
  tags: 3d, three, threejs
---

# Using Three.js and React Three Fiber in Remotion

Follow React Three Fiber and Three.js best practices.  
Only the following Remotion-specific rules need to be followed:

## Prerequisites

First, the `@remotion/three` package needs to be installed.  
If it is not, use the following command:

```bash
npx remotion add @remotion/three # If project uses npm
bunx remotion add @remotion/three # If project uses bun
yarn remotion add @remotion/three # If project uses yarn
pnpm exec remotion add @remotion/three # If project uses pnpm
```

## Using ThreeCanvas

You MUST wrap 3D content in `<ThreeCanvas>` and include proper lighting.  
`<ThreeCanvas>` MUST have a `width` and `height` prop.

```tsx
import { ThreeCanvas } from "@remotion/three";
import { useVideoConfig } from "remotion";

const { width, height } = useVideoConfig();

<ThreeCanvas width={width} height={height}>
  <ambientLight intensity={0.4} />
  <directionalLight position={[5, 5, 5]} intensity={0.8} />
  <mesh>
    <sphereGeometry args={[1, 32, 32]} />
    <meshStandardMaterial color="red" />
  </mesh>
</ThreeCanvas>;
```

## No animations not driven by `useCurrentFrame()`

Shaders, models etc MUST NOT animate by themselves.  
No animations are allowed unless they are driven by `useCurrentFrame()`.  
Otherwise, it will cause flickering during rendering.

Using `useFrame()` from `@react-three/fiber` is forbidden.

## Animate using `useCurrentFrame()`

Use `useCurrentFrame()` to perform animations.

```tsx
const frame = useCurrentFrame();
const rotationY = frame * 0.02;

<mesh rotation={[0, rotationY, 0]}>
  <boxGeometry args={[2, 2, 2]} />
  <meshStandardMaterial color="#4a9eff" />
</mesh>;
```

## Using `<Sequence>` inside `<ThreeCanvas>`

The `layout` prop of any `<Sequence>` inside a `<ThreeCanvas>` must be set to `none`.

```tsx
import { Sequence } from "remotion";
import { ThreeCanvas } from "@remotion/three";

const { width, height } = useVideoConfig();

<ThreeCanvas width={width} height={height}>
  <Sequence layout="none">
    <mesh>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#4a9eff" />
    </mesh>
  </Sequence>
</ThreeCanvas>;
```

<!-- ===== /file: remotion-best-practices/remotion-markup/3d.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/REFERENCE.md ===== -->

---
name: remotion-markup
description: Content, animation and effects best practices
version: 4.0.539
---

This is guidance for writing Remotion React Markup.
If this is not relevant, load [Remotion Best Practices](../SKILL.md) instead.

## Preserve user changes

Users may make edits in the code outside of the conversation.

If you detect a surprising change made in the meanwhile, don't overwrite it, assume it was intentional or ask for confirmation.

## General rules

Keep `useCurrentFrame()` in the smallest component that needs it. Extract
frame-dependent audio volume, titles, and overlays into their own components
instead of subscribing the whole composition or scene; otherwise unrelated
descendants re-render on every frame. Preserve the existing frame coordinates
when extracting across timing boundaries, and keep editable interpolations
inline on the item's props.

Inside a composition or scene component, get `fps` from `useVideoConfig()` for
all seconds-to-frames calculations, including timing props such as `from`,
`trimBefore` and `durationInFrames`. Keeping the expression on
the JSX node, such as `trimBefore={4 * fps}`, lets Studio edit the timing and
keeps it correct if the composition frame rate changes.

Drive animations using `useCurrentFrame()` and `interpolate()`.  
CSS `transition` or `animation` will not render correctly, they need to refactored.  
Tailwind animation class will not render correctly, they need to be refactored.

Use `Easing.bezier()` and `Easing.spring()` to customize timing.

Before choosing the markup hierarchy, read
[editable timeline structure](../remotion-interactivity/timeline-structure.md).
Choose editing units first, then the tracks or shared timing boundaries they
need. It includes a complete example with interactive components and their
registrations. For source-editable styles, schemas, and keyframes, see
[Remotion Interactivity](../remotion-interactivity/REFERENCE.md).

```tsx
import { useCurrentFrame, useVideoConfig, Easing, interpolate, Interactive } from "remotion";

export const FadeIn = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <Interactive.Div
      name="Title"
      style={{
        opacity: interpolate(frame, [0, 2 * fps], [0, 1], {
          extrapolateRight: "clamp",
          extrapolateLeft: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }),
      }}
    >
      Hello World!
    </Interactive.Div>
  );
};
```

Keep the `interpolate()` call inline in the `style` prop.
Use `scale`, `translate`, `rotate` CSS properties over `transform`.

```tsx
// 👍 Inline editable keyframes and transform shorthands
style={{
  scale: interpolate(frame, [0, 100], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.spring({damping: 200}),
    output: 'perceptual-scale' // For `scale` animations, use "output: 'perceptual-scale'"
  }),
  translate: interpolate(frame, [0, 100], ["0px 0px", "100px 100px"], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.spring({damping: 200}),
  }),
  rotate: interpolate(frame, [0, 100], ["20deg", "90deg"], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.spring({damping: 200}),
  }),
}}

// 👎 Non-inline values and transform strings become harder to edit in Studio
const scale = interpolate(frame, [0, 100], [0, 1]);

style={{
  transform: `scale(${scale})`,
}}
```

## Assets

Place assets in the `public/` folder at your project root.
Use `staticFile()` to reference files from the `public/` folder.

## Media components

Add video and audio using `<Video>` and `<Audio>` from `@remotion/media`.  
Add images using the `<CanvasImage>` component.
Add animated GIFs, APNG, WebP or AVIF images using `<AnimatedImage>`, use `@remotion/gif` if not using Chrome.
Use `staticFile()` for files in `public/` or pass a remote URL directly:

```tsx
import { Audio, Video } from "@remotion/media";
import { staticFile, CanvasImage, AnimatedImage } from "remotion";

export const MyComposition = () => {
  return (
    <>
      <Video src={staticFile("video.mp4")} style={{ opacity: 0.5 }} />
      <Audio src={staticFile("audio.mp3")} />
      <CanvasImage
        src={staticFile("logo.png")}
        style={{ width: 100, height: 100 }}
      />
      <Video src="https://remotion.media/video.mp4" />
      <AnimatedImage src={staticFile('nyancat.gif')} />
    </>
  );
};
```

If the composition is primarily a timeline of video or audio clips, read
[video-editing.md](video-editing.md) before choosing its source structure.

## Delaying, trimming

Use [sequencing](sequencing.md) to choose the timing boundary and
[timing props](timing-props.md) for the supported props and order of operations.

## Maps

See [Remotion Maps](./remotion-maps/REFERENCE.md) if wanting to include maps in the video.

## Text highlights and annotations

See [text-highlights.md](text-highlights.md) for text highlights (highlight markers), circles, underlines, strike-throughs, crossed-off text, boxes.

## Multi-scene videos

See [multi-scene-video.md](multi-scene-video.md) if planning to make a video with multiple subsequent scenes.

## Connected compositions

Read [connected compositions](connected-compositions.md) when a scene or group
needs its own editable timeline, or when handling a Studio pre-compose request.
It covers extraction, registration, inherited styles, and verification in both
the parent and standalone views.

## Voiceover

See [voiceover.md](voiceover.md) for adding an AI-generated voiceover to Remotion compositions using ElevenLabs TTS.

## Embedding Videos

See [embedding-videos.md](embedding-videos.md) for advanced knowledge about embedding videos - trimming, volume, speed, looping, pitch.

## Embedding Audio

See [audio.md](audio.md) for advanced audio features like trimming, volume, speed, pitch.

## Cropping

See [cropping.md](cropping.md) if needing to crop the visible rectangle of a component.

## Transitions

See [transitions.md](transitions.md) for scene transition patterns.

## Motion blur

When adding motion blur or a movement trail, read [motion-blur.md](motion-blur.md) for the preferred HTML-in-canvas approach, preview requirements, and alternatives.

## Visual and pixel effects

When adding a visual effect, first identify the element or group it should affect.
If the target component supports `effects` and a built-in effect below matches the
request, prefer that effect over a CSS approximation. For example, apply
`vignette()` directly to a `<Video>`'s `effects` prop when the vignette should
affect that video.

These components accept `effects` directly:

| Import from        | Components                                                                                                                    |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `remotion`         | `<Img>`, `<CanvasImage>`, `<AnimatedImage>`, `<Solid>`, `<HtmlInCanvas>`                                                      |
| `@remotion/media`  | `<Video>`                                                                                                                     |
| `@remotion/gif`    | `<Gif>`                                                                                                                       |
| `@remotion/rive`   | `<RemotionRiveCanvas>`                                                                                                        |
| `@remotion/shapes` | `<Arrow>`, `<Callout>`, `<Circle>`, `<Ellipse>`, `<Heart>`, `<Pie>`, `<Polygon>`, `<Rect>`, `<Spark>`, `<Star>`, `<Triangle>` |

Ordinary HTML elements, `<Interactive.*>` DOM wrappers, `<AbsoluteFill>`, and
`<Sequence>` do not accept `effects` directly. To apply effects to their content,
wrap them in `<HtmlInCanvas>` and put the `effects` prop on the wrapper.

For other elements, prefer regular HTML and CSS where suitable. Consider wrapping
a group in [`<HtmlInCanvas>`](html-in-canvas.md) when post-processing the whole
group is appropriate and the environment supports it.

Read [effects.md](effects.md) before applying an effect for imports, parameters,
and setup. It also covers reusable custom effects with `createEffect()` when no
built-in effect matches.

### Available effects

Built-in effects from `@remotion/effects`:

- Color and tone: `brightness()`, `colorCorrection()`, `colorKey()`, `contrast()`, `curves()`, `duotone()`, `exposure()`, `grayscale()`, `hue()`, `invert()`, `levels()`, `linearGradient()`, `linearGradientTint()`, `lut()`, `saturation()`, `shadowsHighlights()`, `thermalVision()`, `tint()`, `vibrance()`, `whiteBalance()`.
- Blur and trails: `blur()`, `lightTrail()`, `linearProgressiveBlur()`, `radialProgressiveBlur()`, `regionBlur()`, `zoomBlur()`.
- Lighting: `dropShadow()`, `longShadows()`, `glow()`, `lightLeak()`, `shine()`, `starburst()`, `vignette()`.
- Distortion and transforms: `barrelDistortion()`, `chromaticAberration()`, `cornerPin()`, `fisheye()`, `mirror()`, `noiseDisplacement()`, `scale()`, `skew()`, `tile()`, `uvTranslate()`, `wave()`, `xyTranslate()`.
- Textures and patterns: `burlap()`, `checkerboard()`, `contourLines()`, `dotGrid()`, `emboss()`, `flannel()`, `gridlines()`, `halftone()`, `halftoneLinearGradient()`, `lines()`, `liquidContours()`, `noise()`, `paper()`, `pattern()`, `rings()`, `scanlines()`, `speckle()`, `tvSignalOff()`, `waves()`, `whiteNoise()`, `zigzag()`.
- Edges: `outline()`, `roughenEdges()`, `shrinkwrap()`, `tear()`.
- Pixelation and transitions: `evolve()`, `linearProgressivePixelate()`, `pixelate()`, `pixelDissolve()`, `radialProgressivePixelate()`, `venetianBlinds()`.

## Color correction

Read [color-correction.md](color-correction.md) for primary adjustments with
`colorCorrection()`, tonal mapping with `levels()` or `curves()`, their Studio
editors, and 3D `.cube` color grades with `lut()`.

## 3D content

See [./3d.md](./3d.md) for 3D content in Remotion using Three.js and React Three Fiber.

## Sound effects

When needing to use sound effects, load the [./sfx.md](./sfx.md) file for more information.

## Audio visualization

When needing to visualize audio (spectrum bars, waveforms, bass-reactive effects), load the [./audio-visualization.md](./audio-visualization.md) file for more information.

## Maps

For static maps, animated routes and markers, geographic explainers, Mapbox, MapLibre, MapTiler, GeoJSON, or 3D geographic flyovers, load [Remotion Maps](./remotion-maps/REFERENCE.md).

## Captions

When dealing with captions or subtitles, load the [Remotion Captions](../remotion-captions/REFERENCE.md) skill for more information.

## Arabic and right-to-left text

For Arabic, Persian, Urdu or Hebrew text, read [arabic-text.md](arabic-text.md): set the base direction, animate by word, and split letters only in a way that keeps them joined.

## Google Fonts

Is the recommended way to load fonts in Remotion. See [google-fonts.md](google-fonts.md) for how to load Google Fonts.

## Local fonts

See [local-fonts.md](local-fonts.md) for how to load local fonts.

## GIFs

See [gifs.md](gifs.md) for how to display GIFs synchronized with Remotion's timeline.

## Advanced Images

See [images.md](images.md) for sizing and positioning images, dynamic image paths, and getting image dimensions.

## Lottie animations

See [lottie.md](lottie.md) for embedding Lottie animations in Remotion.

## Timing

See [timing.md](timing.md) for more timing techniques for `interpolate()`.

## Parameterized videos

See [parameters.md](parameters.md) for making a composition parametrizable by adding a Zod schema.

## Measuring DOM nodes

See [measuring-dom-nodes.md](measuring-dom-nodes.md) for measuring DOM element dimensions in Remotion.

## Measuring text

See [measuring-text.md](measuring-text.md) for measuring text dimensions, fitting text to containers, and checking overflow.

## Using FFmpeg

For some video operations, such as trimming videos or detecting silence, FFmpeg should be used. Load the [./ffmpeg.md](./ffmpeg.md) file for more information.

## Silence detection

When needing to detect and trim silent segments from video or audio files, load the [./silence-detection.md](./silence-detection.md) file.

## Dynamic duration, dimensions and data

See [calculate-metadata.md](calculate-metadata.md) for dynamically set composition duration, dimensions, and props.

## Compositions and stills

Before registering `<Composition>` or `<Still>` elements, read [compositions.md](compositions.md) for source-editable registrations, folders, default props and nesting. For Studio navigation into a scene's own timeline, use [connected compositions](connected-compositions.md).

## Advanced sequencing

See [sequencing.md](sequencing.md) for more sequencing patterns - delay, trim, limit duration of items.

## Install modules

Use `npx remotion add` to add new packages with the right version:

```
npx remotion add @remotion/media
```

This goes for `@remotion/*` packages, `mediabunny`, `@mediabunny/*`, `zod`, and `@huggingface/transformers`.

## Visual checks

Open the [Remotion Studio](../remotion-studio/REFERENCE.md) to check visual changes.
When changing timeline structure, inspect the full composition as well as any
connected components; verify the visible layers, cut timing, and synchronized
content.

You can also use [Rendering](../remotion-render/REFERENCE.md) to inspect one or several frames as images.

<!-- ===== /file: remotion-best-practices/remotion-markup/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/arabic-text.md ===== -->

---
name: arabic-text
description: Arabic, Persian, Urdu and Hebrew text - base direction, word and letter animation that keeps Arabic letters joined, fonts.
metadata:
  tags: arabic, rtl, persian, urdu, hebrew, typography, text-animation, captions
---

# Arabic and right-to-left text

## Set the base direction

Put `dir="rtl"` and `lang` on the element that holds right-to-left text.

Words or letters wrapped in `display: inline-block` (needed for `translate`, `scale`, `rotate`) are neutral to the bidi algorithm. Without a base direction the line defaults to LTR, so the words are placed left to right and the sentence reads backwards, even though every word looks correct. This is the usual failure of word-by-word captions and karaoke highlights.

When the language comes from props, decide the direction from the words. Count words rather than reading the first letter, because Arabic captions often start with a Latin brand name:

```tsx
const RTL = /[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]/;
const isRtl = (words: string[]) =>
  words.filter((w) => RTL.test(w)).length > words.length / 2;

<div dir={isRtl(words) ? 'rtl' : 'ltr'}>{/* word spans */}</div>
```

## Animate words, not letters

Arabic letters change shape depending on their neighbours. `text.split('')`, `[...text]` or `Array.from(text)` put each letter in its own box, and a letter in an `inline-block` is shaped alone, so the word falls apart into isolated letters.

Prefer word-level or line-level animation for Arabic. Split on spaces, give the container `dir="rtl"`, animate each word.

## Per-letter animation, if it is needed

Split into units that the browser can still join:

- keep harakat (vowel marks) in the same unit as their letter
- keep lam + alef (`لا`, `لأ`, `لإ`, `لآ`) as one unit, it is a ligature
- keep runs of digits and Latin as one unit, or an RTL line reverses them
- add a zero-width joiner (`\u200D`) on each side of a unit that connects to its neighbour, so each unit is drawn in its connected form

```tsx
const ZWJ = '\u200D';
const RIGHT_JOINING = /[\u0622-\u0625\u0627\u0629\u062F-\u0632\u0648\u0671-\u0673\u0675-\u0677\u0688-\u0699\u06C0\u06C3-\u06CB\u06CD\u06CF\u06D2\u06D3\u06D5]/;
const LETTER = /[\u0620-\u064A\u066E-\u06D3\u06D5\u06FA-\u06FC\u06FF]/;
const LTR_RUN = /^[0-9\u0660-\u0669\u06F0-\u06F9A-Za-z\u066B\u066C.,:%]+$/;
const MARK = /[\u064B-\u065F\u0670\u06D6-\u06ED]/;
const MARKS = /[\u064B-\u065F\u0670\u06D6-\u06ED\u200D]/g;
const first = (u: string) => u.replace(MARKS, '')[0] ?? '';
const last = (u: string) => u.replace(MARKS, '').slice(-1);
const joinsPrev = (u: string) => LETTER.test(first(u)) && first(u) !== '\u0621';
const joinsNext = (u: string) =>
  LETTER.test(last(u)) && last(u) !== '\u0621' && !RIGHT_JOINING.test(last(u));

export const splitArabicLetters = (text: string): string[] => {
  const g: string[] = [];
  for (const ch of text) {
    if (MARK.test(ch) && g.length > 0) g[g.length - 1] += ch;
    else g.push(ch);
  }
  const units: string[] = [];
  for (let i = 0; i < g.length; i++) {
    if (LTR_RUN.test(g[i])) {
      let run = g[i];
      while (g[i + 1] && LTR_RUN.test(g[i + 1])) run += g[++i];
      units.push(run);
    } else if (first(g[i]) === '\u0644' && /[\u0622\u0623\u0625\u0627]/.test(first(g[i + 1] ?? ''))) {
      units.push(g[i] + g[++i]);
    } else {
      units.push(g[i]);
    }
  }
  return units.map((u, i) => {
    const before = i > 0 && joinsNext(units[i - 1]) && joinsPrev(u) ? ZWJ : '';
    const after = i < units.length - 1 && joinsNext(u) && joinsPrev(units[i + 1]) ? ZWJ : '';
    return before + u + after;
  });
};
```

Render the units in a container with `dir="rtl"`, one `inline-block` span per unit, and animate the spans as usual. In Remotion's Chrome renders the letters join exactly as in the unsplit word.

## Fonts

Load an Arabic font explicitly, for example `@remotion/google-fonts/NotoSansArabic`, `IBMPlexSansArabic`, `Cairo` or `Tajawal`. See [google-fonts.md](google-fonts.md). A Latin-only font falls back to whatever Arabic font the render machine has.

Avoid `letterSpacing` and `textTransform` on Arabic text.

The ZWJ technique needs care outside Chrome: Safari draws a ZWJ-padded letter in a fallback font when the font has no U+200D glyph, so the same composition shown in the `<Player>` on an iPhone can mix two typefaces inside a word. Alexandria (as served by Google Fonts), IBM Plex Sans Arabic, Cairo and Tajawal have no U+200D glyph; Noto Sans Arabic and Noto Naskh Arabic do. Video renders are not affected.

<!-- ===== /file: remotion-best-practices/remotion-markup/arabic-text.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/audio-visualization.md ===== -->

---
name: audio-visualization
description: Audio visualization patterns - spectrum bars, waveforms, bass-reactive effects
metadata:
  tags: audio, visualization, spectrum, waveform, bass, music, audiogram, frequency
---

# Audio Visualization in Remotion

## Prerequisites

```bash
npx remotion add @remotion/media-utils
```

## Loading Audio Data

Use `useWindowedAudioData()` (https://www.remotion.dev/docs/use-windowed-audio-data) to load audio data:

```tsx
import { useWindowedAudioData } from "@remotion/media-utils";
import { staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const { audioData, dataOffsetInSeconds } = useWindowedAudioData({
  src: staticFile("podcast.wav"),
  frame,
  fps,
  windowInSeconds: 30,
});
```

## Spectrum Bar Visualization

Use `visualizeAudio()` (https://www.remotion.dev/docs/visualize-audio) to get frequency data for bar charts:

```tsx
import { useWindowedAudioData, visualizeAudio } from "@remotion/media-utils";
import { staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const { audioData, dataOffsetInSeconds } = useWindowedAudioData({
  src: staticFile("music.mp3"),
  frame,
  fps,
  windowInSeconds: 30,
});

if (!audioData) {
  return null;
}

const frequencies = visualizeAudio({
  fps,
  frame,
  audioData,
  numberOfSamples: 256,
  optimizeFor: "speed",
  dataOffsetInSeconds,
});

return (
  <div style={{ display: "flex", alignItems: "flex-end", height: 200 }}>
    {frequencies.map((v, i) => (
      <div
        key={i}
        style={{
          flex: 1,
          height: `${v * 100}%`,
          backgroundColor: "#0b84f3",
          margin: "0 1px",
        }}
      />
    ))}
  </div>
);
```

- `numberOfSamples` must be power of 2 (32, 64, 128, 256, 512, 1024)
- Values range 0-1; left of array = bass, right = highs
- Use `optimizeFor: "speed"` for Lambda or high sample counts

**Important:** When passing `audioData` to child components, also pass the `frame` from the parent. Do not call `useCurrentFrame()` in each child - this causes discontinuous visualization when children are inside `<Sequence>` with offsets.

## Waveform Visualization

Use `visualizeAudioWaveform()` (https://www.remotion.dev/docs/media-utils/visualize-audio-waveform) with `createSmoothSvgPath()` (https://www.remotion.dev/docs/media-utils/create-smooth-svg-path) for oscilloscope-style displays:

```tsx
import {
  createSmoothSvgPath,
  useWindowedAudioData,
  visualizeAudioWaveform,
} from "@remotion/media-utils";
import { staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { width, fps } = useVideoConfig();
const HEIGHT = 200;

const { audioData, dataOffsetInSeconds } = useWindowedAudioData({
  src: staticFile("voice.wav"),
  frame,
  fps,
  windowInSeconds: 30,
});

if (!audioData) {
  return null;
}

const waveform = visualizeAudioWaveform({
  fps,
  frame,
  audioData,
  numberOfSamples: 256,
  windowInSeconds: 0.5,
  dataOffsetInSeconds,
});

const path = createSmoothSvgPath({
  points: waveform.map((y, i) => ({
    x: (i / (waveform.length - 1)) * width,
    y: HEIGHT / 2 + (y * HEIGHT) / 2,
  })),
});

return (
  <svg width={width} height={HEIGHT}>
    <path d={path} fill="none" stroke="#0b84f3" strokeWidth={2} />
  </svg>
);
```

## Bass-Reactive Effects

Extract low frequencies for beat-reactive animations:

```tsx
const frequencies = visualizeAudio({
  fps,
  frame,
  audioData,
  numberOfSamples: 128,
  optimizeFor: "speed",
  dataOffsetInSeconds,
});

const lowFrequencies = frequencies.slice(0, 32);
const bassIntensity =
  lowFrequencies.reduce((sum, v) => sum + v, 0) / lowFrequencies.length;

const scale = 1 + bassIntensity * 0.5;
const opacity = Math.min(0.6, bassIntensity * 0.8);
```

## Volume-Based Waveform

Use `getWaveformPortion()` (https://www.remotion.dev/docs/get-waveform-portion) when you need simplified volume data instead of frequency spectrum:

```tsx
import { getWaveformPortion } from "@remotion/media-utils";
import { useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const currentTimeInSeconds = frame / fps;

const waveform = getWaveformPortion({
  audioData,
  startTimeInSeconds: currentTimeInSeconds,
  durationInSeconds: 5,
  numberOfSamples: 50,
});

// Returns array of { index, amplitude } objects (amplitude: 0-1)
waveform.map((bar) => (
  <div key={bar.index} style={{ height: bar.amplitude * 100 }} />
));
```

## Postprocessing

Low frequencies naturally dominate. Apply logarithmic scaling for visual balance:

```tsx
const minDb = -100;
const maxDb = -30;

const scaled = frequencies.map((value) => {
  const db = 20 * Math.log10(value);
  return (db - minDb) / (maxDb - minDb);
});
```

<!-- ===== /file: remotion-best-practices/remotion-markup/audio-visualization.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/audio.md ===== -->

---
name: audio
description: Using audio and sound in Remotion - importing, trimming, volume, speed, pitch
metadata:
  tags: audio, media, trim, volume, speed, loop, pitch, mute, sound, sfx
---

# Using audio in Remotion

## Prerequisites

First, the @remotion/media package needs to be installed.
If it is not installed, use the following command:

```bash
npx remotion add @remotion/media
```

## Importing Audio

Use `<Audio>` from `@remotion/media` to add audio to your composition.

```tsx
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";

export const MyComposition = () => {
  return <Audio src={staticFile("audio.mp3")} />;
};
```

Remote URLs are also supported:

```tsx
import { Audio } from "@remotion/media";

<Audio src="https://remotion.media/audio.mp3" />
```

By default, audio plays from the start, at full volume and full length.
Multiple audio tracks can be layered by adding multiple `<Audio>` components.

## Trimming

Use `trimBefore` to skip the beginning of the audio and `durationInFrames` to end it early. Values are in frames.

```tsx
import { Audio } from "@remotion/media";

const { fps } = useVideoConfig();

return (
  <Audio
    src={staticFile("audio.mp3")}
    trimBefore={2 * fps} // Skip the first 2 seconds
    durationInFrames={8 * fps} // Play 8 seconds, until the 10 second mark
  />
);
```

The audio still starts playing at the beginning of the composition - only the specified portion is played.

## Delaying

Set `from` directly on `<Audio>` to delay when it starts:

```tsx
import { staticFile, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";

const { fps } = useVideoConfig();

return (
  <Audio from={fps} src={staticFile("audio.mp3")} />
);
```

The audio will start playing after 1 second.

## Volume

Set a static volume (0 to 1):

```tsx
import { Audio } from "@remotion/media";

<Audio src={staticFile("audio.mp3")} volume={0.5} />
```

Use `useCurrentFrame()` and `interpolate()` for keyframed volume:

```tsx
import { Audio } from "@remotion/media";
import { interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

return (
  <Audio
    src={staticFile("audio.mp3")}
    volume={interpolate(frame, [0, 1 * fps], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })}
  />
);
```

With Studio interactivity enabled, these keyframes can be edited and are shown as a volume curve in the timeline.

## Muting

Use `muted` to silence the audio. It can be set dynamically:

```tsx
import { Audio } from "@remotion/media";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

return (
  <Audio
    src={staticFile("audio.mp3")}
    muted={frame >= 2 * fps && frame <= 4 * fps} // Mute between 2s and 4s
  />
);
```

## Speed

Use `playbackRate` to change the playback speed:

```tsx
import { Audio } from "@remotion/media";

// 2x speed
<Audio src={staticFile("audio.mp3")} playbackRate={2} />
// Half speed
<Audio src={staticFile("audio.mp3")} playbackRate={0.5} />
```

Reverse playback is not supported.

## Looping

Use `loop` to loop the audio indefinitely:

```tsx
import { Audio } from "@remotion/media";

<Audio src={staticFile("audio.mp3")} loop />
```

Put `name`, `from`, `loop`, and `volume` directly on `<Audio>`.

```tsx
import { Audio } from "@remotion/media";
import { interpolate, staticFile, useCurrentFrame } from "remotion";

const frame = useCurrentFrame();

<Audio
  src={staticFile("audio.mp3")}
  loop
  volume={interpolate(frame, [0, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  })}
/>
```

## Pitch

Use `toneFrequency` to adjust the pitch without affecting speed. Values range from 0.01 to 2:

```tsx
import { Audio } from "@remotion/media";

<Audio
  src={staticFile("audio.mp3")}
  toneFrequency={1.5} // Higher pitch
/>
<Audio
  src={staticFile("audio.mp3")}
  toneFrequency={0.8} // Lower pitch
/>
```

Pitch shifting only works during server-side rendering, not in the Remotion Studio preview or in the `<Player />`.

<!-- ===== /file: remotion-best-practices/remotion-markup/audio.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/calculate-metadata.md ===== -->

---
name: calculate-metadata
description: Dynamically set composition duration, dimensions, and props
metadata:
  tags: calculateMetadata, duration, dimensions, props, dynamic
---

# Using calculateMetadata

Use `calculateMetadata` on a `<Composition>` to dynamically set duration, dimensions, and transform props before rendering.
Use it when metadata depends on input props, fetched data, or asset metadata.
For static dimensions, duration, FPS, and initial props, inline the values on `<Composition>` instead.

```tsx
<Composition
  id="MyComp"
  component={MyComponent}
  durationInFrames={300}
  fps={30}
  width={1920}
  height={1080}
  defaultProps={{ videoSrc: "https://remotion.media/video.mp4" }}
  calculateMetadata={calculateMetadata}
/>
```

## Setting duration based on a video

Use the [`getVideoDuration`](../remotion-multimedia/get-video-duration.md) and [`getVideoDimensions`](../remotion-multimedia/get-video-dimensions.md) skills to get the video duration and dimensions:

```tsx
import { CalculateMetadataFunction } from "remotion";
import { getVideoDuration } from "./get-video-duration";

const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  const durationInSeconds = await getVideoDuration(props.videoSrc);

  return {
    durationInFrames: Math.ceil(durationInSeconds * 30),
  };
};
```

## Matching dimensions of a video

Use the [`getVideoDimensions`](../remotion-multimedia/get-video-dimensions.md) skill to get the video dimensions:

```tsx
import { CalculateMetadataFunction } from "remotion";
import { getVideoDuration } from "./get-video-duration";
import { getVideoDimensions } from "./get-video-dimensions";

const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  const dimensions = await getVideoDimensions(props.videoSrc);

  return {
    width: dimensions.width,
    height: dimensions.height,
  };
};
```

## Setting duration based on multiple videos

```tsx
const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  const metadataPromises = props.videos.map((video) =>
    getVideoDuration(video.src),
  );
  const allMetadata = await Promise.all(metadataPromises);

  const totalDuration = allMetadata.reduce(
    (sum, durationInSeconds) => sum + durationInSeconds,
    0,
  );

  return {
    durationInFrames: Math.ceil(totalDuration * 30),
  };
};
```

## Setting a default outName

Set the default output filename based on props:

```tsx
const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  return {
    defaultOutName: `video-${props.id}`, // .mp4 is added automatically
  };
};
```

## Transforming props

Fetch data or transform props before rendering:

```tsx
const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
  abortSignal,
}) => {
  const response = await fetch(props.dataUrl, { signal: abortSignal });
  const data = await response.json();

  return {
    props: {
      ...props,
      fetchedData: data,
    },
  };
};
```

The `abortSignal` cancels stale requests when props change in the Studio.

## Return value

All fields are optional. Returned values override the `<Composition>` props:

- `durationInFrames`: Number of frames
- `width`: Composition width in pixels
- `height`: Composition height in pixels
- `fps`: Frames per second
- `props`: Transformed props passed to the component
- `defaultOutName`: Default output filename
- `defaultCodec`: Default codec for rendering

<!-- ===== /file: remotion-best-practices/remotion-markup/calculate-metadata.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/color-correction.md ===== -->

---
name: color-correction
description: Correct exposure, white balance, and tone with primary adjustments, Levels, Curves, and 3D Cube LUTs.
metadata:
  tags: color-correction, color-grading, levels, curves, lut, cube, exposure, white-balance
---

# Color correction

Apply color adjustments through the `effects` prop of `<Video>` from `@remotion/media`, or other supported components.  
See [effects.md](effects.md) for more context on effects.

## Primary adjustments

Prefer [`colorCorrection()`](https://www.remotion.dev/docs/effects/color-correction) when combining adjustments.  
It performs them in one WebGL pass and exposes controls in the Studio.

| Control                 | Meaning and range                                                         | Neutral value |
| ----------------------- | ------------------------------------------------------------------------- | ------------- |
| `exposure`              | Stops, from `-5` to `5`; positive values brighten                         | `0`           |
| `temperature`           | From `-1` (cooler) to `1` (warmer)                                        | `0`           |
| `tint`                  | From `-1` (greener) to `1` (more magenta)                                 | `0`           |
| `shadows`, `highlights` | From `-1` to `1`; negative values darken, positive values lift the region | `0`           |
| `blacks`, `whites`      | From `-1` to `1`; target narrower regions near black and white            | `0`           |
| `contrast`              | Non-negative multiplier around `pivot` (`0` to `1`, default `0.5`)        | `1`           |
| `saturation`            | Non-negative multiplier; `0` is grayscale                                 | `1`           |
| `vibrance`              | From `-1` to `1`; positive values emphasize muted colors                  | `0`           |

```tsx
import {colorCorrection} from '@remotion/effects/color-correction';
import {Video} from '@remotion/media';
import {staticFile} from 'remotion';

export const CorrectedVideo = () => {
  return (
    <Video
      src={staticFile('footage.mp4')}
      effects={[
        colorCorrection({
          exposure: 0.25,
          temperature: 0.1,
          tint: -0.03,
          shadows: 0.15,
          highlights: -0.1,
          contrast: 1.1,
          saturation: 1.05,
          vibrance: 0.15,
        }),
      ]}
    />
  );
};
```

Internally, `colorCorrection()` applies exposure, white balance, tonal regions,
contrast, saturation, then vibrance. Omitted controls use their neutral values.
Keep everything inline on the target's `effects` prop.

Standalone effects are also available when a different order or an additional
adjustment is needed: `exposure()`, `whiteBalance()`, `shadowsHighlights()`,
`contrast()`, `saturation()`, and `vibrance()`. See [effects](effects.md)

## Levels and Curves

Use [`levels()`](https://www.remotion.dev/docs/effects/levels) to set input black
and white points, adjust midtones with gamma, or limit the output range.
`blackPoint` and `whitePoint` are normalized from `0` to `1`, default to `0` and
`1`, and require `blackPoint < whitePoint`. `gamma` ranges from `0.01` to `10`,
defaults to `1`, and values above `1` brighten midtones. `outputBlack` and
`outputWhite` range from `0` to `1` and default to `0` and `1`; reversing them
inverts the output.

Use [`curves()`](https://www.remotion.dev/docs/effects/curves) for an S-curve or
other adjustments that need multiple input/output control points. Supply `2` to
`32` `[input, output]` pairs with both coordinates in `0` to `1` and strictly
increasing input values. Outputs may increase or decrease. The default
`[[0, 0], [1, 1]]` leaves the image unchanged. Values outside the first and last
input points use the nearest endpoint's output.

Curves uses `interpolation: 'smooth'` by default, connecting points without
overshooting their output values. Use `'linear'` for straight segments.
`amount` blends with the original image from `0` to `1` (default `1`).

Both effects default to `channel: 'rgb'`. Set `'red'`, `'green'`, or `'blue'` to
adjust one channel, and stack separate effect calls for different channel
adjustments. Both preserve alpha. Curves, the Levels channel/output controls,
and their graphical Studio editors are available from Remotion `4.0.537`.

Keep the effect calls and point arrays inline so Studio can edit them:

```tsx
import {curves} from '@remotion/effects/curves';
import {levels} from '@remotion/effects/levels';
import {Video} from '@remotion/media';
import {staticFile} from 'remotion';

export const ToneAdjustedVideo = () => {
  return (
    <Video
      src={staticFile('footage.mp4')}
      effects={[
        levels({
          blackPoint: 0.03,
          whitePoint: 0.95,
          gamma: 1.1,
          outputBlack: 0.02,
          outputWhite: 0.98,
        }),
        curves({
          channel: 'red',
          points: [[0, 0], [0.5, 0.55], [1, 1]],
          amount: 0.8,
        }),
      ]}
    />
  );
};
```

Effects run in array order: this example adjusts the RGB levels, then lifts
red midtones. Place primary adjustments before `lut()` when the LUT should
receive the corrected footage.

## LUTs and combining effects

A LUT (lookup table) maps input RGB colors to output colors. Use
[`lut()`](https://www.remotion.dev/docs/effects/lut) to apply a 3D `.cube` LUT.  
Its `content` parameter takes the complete file contents as a string.

This example uses a small warm LUT inline:

```tsx
import {colorCorrection} from '@remotion/effects/color-correction';
import {lut} from '@remotion/effects/lut';
import {Video} from '@remotion/media';
import {staticFile} from 'remotion';

export const GradedVideo = () => {
  return (
    <Video
      src={staticFile('footage.mp4')}
      effects={[
        colorCorrection({exposure: 0.25, contrast: 1.1}),
        lut({
          content: `TITLE "Warm"
LUT_3D_SIZE 2
0 0 0
1 0.1 0
0 0.9 0.1
1 0.9 0.1
0 0.1 0.8
1 0.2 0.7
0 0.9 0.8
1 0.9 0.8`,
        }),
      ]}
    />
  );
};
```

### Supported format and limitations

- Only 3D `.cube` LUTs are supported. `LUT_3D_SIZE` must be an integer from `2`
  to `256`, followed by exactly `size ** 3` RGB rows. 1D LUTs are unsupported.
- Optional `TITLE`, `DOMAIN_MIN`, `DOMAIN_MAX`, blank lines, and `#` comments are
  supported. Other LUT formats need conversion before use.
- `lut()` has no `src` or strength/amount parameter. Use `disabled: true` to
  bypass it.

## Studio workflow

Select the layer and open its effect in the inspector. Levels shows an input
histogram with black, gamma, and white input handles plus output endpoints.
Curves shows an input histogram behind the graph: add or drag points, edit
their numeric coordinates, remove points, or reset the curve. The histogram
shows pixels entering that effect, including adjustments earlier in the stack.

Levels numeric controls and Curves `amount` can be keyframed in Studio.
Curves points are not keyframable in Studio. To animate them, derive `points`
from `useCurrentFrame()` in code, keeping input values strictly increasing on
every frame. Computed point arrays display as read-only in the graph.

Put `.cube` files in `public/` to preview them in the Assets panel.  
The user can drag a 3D `.cube` file from the computer or Assets panel onto a
video in the canvas or timeline to apply the LUT effect.

## See also

- [Color correction documentation](https://www.remotion.dev/docs/color-correction)

<!-- ===== /file: remotion-best-practices/remotion-markup/color-correction.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/compositions.md ===== -->

---
name: compositions
description: Defining compositions, stills, folders, default props and dynamic metadata
metadata:
  tags: composition, still, folder, props, metadata
---

A `<Composition>` defines the component, width, height, fps and duration of a renderable video.

## Source-editable registrations

Give each composition or still that should be edited independently in the
Studio its own authored JSX node. Use a JSX string literal for `id`, and keep
its metadata and editable default values directly on that node.

Programmatic registration is suitable when the generated compositions are
intentionally controlled as one source template and do not need to be
reordered, duplicated, deleted or edited individually in the Studio.

```tsx title="src/MyComposition.tsx"
type Props = {
  readonly title: string;
};

export const MyComposition = ({title}: Props) => <h1>{title}</h1>;
```

```tsx title="src/Root.tsx"
import {Composition} from 'remotion';
import {MyComposition} from './MyComposition';

export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="Launch"
        component={MyComposition}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{title: 'Launch'}}
      />
      <Composition
        id="Recap"
        component={MyComposition}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{title: 'Recap'}}
      />
    </>
  );
};
```

Both registrations can reuse the same component. Keeping them as separate JSX
nodes gives each one its own source-editing target.

## Default Props and scaffold metadata

Pass `defaultProps` to provide initial values for your component.  
Values must be JSON-serializable (`Date`, `Map`, `Set`, and `staticFile()` are supported).
Use `defaultProps` for composition-wide values that should be visible and editable before the video renders.

Keep data owned by a child editor on that child's JSX node. For example,
captions that should remain editable in the Caption editor belong as an inline
array on `<BasicCaptions>`, not in composition `defaultProps` or a component
prop. See [Displaying captions](../remotion-captions/display-captions.md).

For Studio editing, keep `defaultProps` as an inline object literal on `<Composition>` or `<Still>`.
Keep values that should be written back directly in the object instead of deriving them from a loop variable.
Do not store it in a variable, import it, spread it, create it with a helper, or wrap it in `satisfies`.
Use `type` declarations for props rather than `interface` to ensure `defaultProps` type safety.

```tsx title="src/Root.tsx"
import {Composition} from 'remotion';
import {MyComposition} from './MyComposition';

const defaultProps = { title: "Hello World" };

export const RemotionRoot = () => {
  return (
    <>
      {/* 👍 Inline metadata and defaults */}
      <Composition
        id="MyComposition"
        component={MyComposition}
        durationInFrames={100}
        fps={30}
        width={1080}
        height={1080}
        defaultProps={{ title: "Hello World" }}
      />

      {/* 👎 Hidden defaults cannot be saved back by Studio */}
      <Composition
        id="OtherComposition"
        component={MyComposition}
        durationInFrames={100}
        fps={30}
        width={1080}
        height={1080}
        defaultProps={defaultProps}
      />
    </>
  );
};
```

## Folders

Use `<Folder>` to organize compositions in the sidebar.  
Folder names can only contain letters, numbers, and hyphens.

```tsx title="src/Root.tsx"
import { Composition, Folder } from "remotion";

export const RemotionRoot = () => {
  return (
    <>
      <Folder name="Marketing">
        <Composition id="Promo" /* ... */ />
        <Composition id="Ad" /* ... */ />
      </Folder>
      <Folder name="Social">
        <Folder name="Instagram">
          <Composition id="Story" /* ... */ />
          <Composition id="Reel" /* ... */ />
        </Folder>
      </Folder>
    </>
  );
};
```

## Stills

Use `<Still>` for single-frame images. It does not require `durationInFrames` or `fps`.

```tsx title="src/Root.tsx"
import { Still } from "remotion";
import { Thumbnail } from "./Thumbnail";

export const RemotionRoot = () => {
  return (
    <Still
      id="Thumbnail"
      component={Thumbnail}
      width={1280}
      height={720}
    />
  );
};
```

## Dynamic duration, width, and height

Use [`calculateMetadata`](./calculate-metadata.md) to make dimensions, duration, or props dynamic based on input props, fetched data, or asset metadata.

## Nesting compositions within another

To render a composition's component inside another composition, use `<Sequence>` with `width` and `height` when the nested content needs its own dimensions.

When the nested scene should have its own editable Studio timeline, use the [connected composition structure](connected-compositions.md).

```tsx
<>
  <Video src="https://remotion.media/video.mp4" />
  <Sequence
    width={1920}
    height={1080}
  >
    <OverlayComponent />
  </Sequence>
</>
```

<!-- ===== /file: remotion-best-practices/remotion-markup/compositions.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/connected-compositions.md ===== -->

# Connected compositions

A connected composition lets the user open a scene or element in its own
Studio timeline while editing the implementation used by the parent video.
Use it for a substantial scene, a reusable card, or a group that should move
and be edited together, such as a sticker with its sound or a summary graphic.
A layout container or decorative detail usually belongs inside that group as
plain HTML.

## Create the connection

1. Export the component with `Interactive.create()`. Use `layout: 'absolute-fill'`
   for a scene or `layout: 'none'` for a bounded element.
2. Render that exported component in the parent, with its instance props inline.
   Put timing directly on it, or on the shared `Sequence` or
   `TransitionSeries.Sequence` that governs its layers.
3. Register the exact same exported reference in `<Composition component={...}>`.
   Give the registration a unique literal ID, inline metadata, and representative
   inline `defaultProps`. Registering an inner component or an inline wrapper
   does not connect the instance the user sees.

Follow the [complete timeline example](../remotion-interactivity/timeline-structure.md)
for the component definitions, parent, and registrations.

Each independently editable instance still needs its own JSX node. Reuse a
component for repeated units rather than copying its implementation or generating
all instances from one `.map()` call. Keep editor-owned data at its editable
source: caption arrays belong inline on the caption component, not behind a
prop of a generic shot component.

## Make the component independent of its parent

The parent is not mounted when the standalone composition opens. Load fonts
inside the component or a shared imported module, and keep required typography
there. Supply representative content, background, and alignment in the
registration's defaults. Those defaults do not automatically apply to parent
instances or copy their props.

Match the parent's fps and dimensions unless a difference is intentional.
Preserve the source-time offset as well as the duration when the component's
captions or overlays read original-media frames. The instance's placement in
the parent timeline does not usually belong in its standalone defaults.

## Extract an existing group

For a pre-compose request, move the selected markup into a named component and
register it. If the selection already has a meaningful timing wrapper, keep
that wrapper and its props in place and extract its contents. Preserve trim,
speed, stacking order, inherited styles, and the duration needed by sound tails.
A new component file without its registration does not complete the connection.

## Verify both views

Open the full composition and the standalone composition. Check that the group
looks and sounds the same, that its timeline has useful editing units, and that
double-clicking the parent instance opens the intended composition. For a
refactor, compare representative frames and check cut boundaries, captions,
entrance animations, and audio tails.

Connected compositions provide editing boundaries, not a promise to collapse
all their rows. Studio's compact-series view can expose connected children.
Inspect the full-video timeline as well as the standalone view before claiming
that an extraction reduced clutter. Treat row expansion or unused vertical
space as a layout issue when the markup already expresses the correct groups;
avoid extra wrappers or hidden editable layers solely to force a compact view.

<!-- ===== /file: remotion-best-practices/remotion-markup/connected-compositions.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/cropping.md ===== -->

# Cropping

Preferably, the `cropLeft`, `cropRight`, `cropTop` and `cropBottom` props are used to crop content.
It allows for interactively dragging the components and adapting the outlines in the canvas to the crop.

The following components support `crop*` props:

- `<Sequence>` from `remotion`, when `layout="absolute-fill"`
- `<Interactive.*>` HTML and SVG elements from `remotion`
- Custom components made with `Interactive.create()` from `remotion`, using a managed `layout: 'absolute-fill'` root or forwarding `style` to their own visual root
- `<CanvasImage>` from `remotion`
- `<Img>` from `remotion`
- `<AnimatedImage>` from `remotion`
- `<HtmlInCanvas>` from `remotion`
- `<Solid>` from `remotion`
- `<Video>` from `@remotion/media`
- `<Gif>` from `@remotion/gif`
- `<RemotionRiveCanvas>` from `@remotion/rive`

Crop values are ratios between `0` and `1`.
A value of `0` applies no crop on that edge.
A value of `1` is a full crop.
Keep [Interactivity Best Practices](../remotion-interactivity/REFERENCE.md) also for cropping, to keep it editable and keyframable.

```tsx
<CanvasImage
  src={staticFile("photo.png")}
  cropLeft={interpolate(frame, [0, 30], [0, 0.25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  })}
  cropBottom={0.1}
/>
```

Do not use `clipPath` together with crop props.

<!-- ===== /file: remotion-best-practices/remotion-markup/cropping.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/effects.md ===== -->

---
name: effects
description: Canvas/WebGL visual effects for Remotion using effects arrays and createEffect().
metadata:
  tags: effects, visual-effects, webgl, canvas, video, create-effect
---

Read this guidance when adding an effect to a component that supports `effects`,
or when considering canvas post-processing or a reusable custom effect.

Docs: https://www.remotion.dev/docs/effects
Custom effect docs: https://www.remotion.dev/docs/create-effect

For exposure, white balance, Levels, Curves, and LUTs, read
[color-correction.md](color-correction.md).

## Usage

Install the package that provides the chosen effect:

```bash
npx remotion add @remotion/effects
```

Effects are functions passed to the `effects` prop of supported components.

These components accept `effects` directly:

| Import from        | Components                                                                                                                    |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `remotion`         | `<Img>`, `<CanvasImage>`, `<AnimatedImage>`, `<Solid>`, `<HtmlInCanvas>`                                                      |
| `@remotion/media`  | `<Video>`                                                                                                                     |
| `@remotion/gif`    | `<Gif>`                                                                                                                       |
| `@remotion/rive`   | `<RemotionRiveCanvas>`                                                                                                        |
| `@remotion/shapes` | `<Arrow>`, `<Callout>`, `<Circle>`, `<Ellipse>`, `<Heart>`, `<Pie>`, `<Polygon>`, `<Rect>`, `<Spark>`, `<Star>`, `<Triangle>` |

Ordinary HTML elements, `<Interactive.*>` DOM wrappers, `<AbsoluteFill>`, and
`<Sequence>` do not accept `effects` directly. To apply effects to their content,
wrap them in `<HtmlInCanvas>` and put the `effects` prop on the wrapper.

For example, apply an effect directly to a video:

```tsx
import {Video} from '@remotion/media';
import {blur} from '@remotion/effects/blur';

<Video
  src="https://remotion.media/video.mp4"
  effects={[blur({radius: 8})]}
/>;
```

Use the effect docs for exact props and imports. Most `@remotion/effects` imports use `@remotion/effects/<effect-slug>`; `uvTranslate()` and `xyTranslate()` use `@remotion/effects/translate`.

Most effects use WebGL2; `cylinder()`, `sphere()`, and `pageTurn()` use WebGPU. During renders, enable WebGL and WebGPU with:

```ts
import {Config} from '@remotion/cli/config';

Config.setChromiumOpenGlRenderer('angle');
```

## Available effects

Built-in effects from `@remotion/effects`:

- Color and tone: `brightness()`, `colorCorrection()`, `colorKey()`, `contrast()`, `curves()`, `duotone()`, `exposure()`, `grayscale()`, `hue()`, `invert()`, `levels()`, `linearGradient()`, `linearGradientTint()`, `lut()`, `saturation()`, `shadowsHighlights()`, `thermalVision()`, `tint()`, `vibrance()`, `whiteBalance()`.
- Blur and trails: `blur()`, `lightTrail()`, `linearProgressiveBlur()`, `radialProgressiveBlur()`, `regionBlur()`, `zoomBlur()`.
- Lighting: `dropShadow()`, `longShadows()`, `glow()`, `lightLeak()`, `shine()`, `starburst()`, `vignette()`.
- Distortion and transforms: `barrelDistortion()`, `chromaticAberration()`, `cornerPin()`, `fisheye()`, `mirror()`, `noiseDisplacement()`, `scale()`, `skew()`, `tile()`, `uvTranslate()`, `wave()`, `xyTranslate()`.
- Textures and patterns: `burlap()`, `checkerboard()`, `contourLines()`, `dotGrid()`, `emboss()`, `flannel()`, `gridlines()`, `halftone()`, `halftoneLinearGradient()`, `lines()`, `liquidContours()`, `noise()`, `paper()`, `pattern()`, `rings()`, `scanlines()`, `speckle()`, `tvSignalOff()`, `waves()`, `whiteNoise()`, `zigzag()`.
- Edges: `outline()`, `roughenEdges()`, `shrinkwrap()`, `tear()`.
- Pixelation and transitions: `evolve()`, `linearProgressivePixelate()`, `pixelate()`, `pixelDissolve()`, `radialProgressivePixelate()`, `venetianBlinds()`.

Example:

```tsx
import {Video} from '@remotion/media';
import {brightness} from '@remotion/effects/brightness';

<Video
  src="https://remotion.media/video.mp4"
  effects={[brightness({})]}
/>;
```

## Custom effects

Use `createEffect()` from `remotion` when the user wants a reusable effect factory that works in the same `effects` array as `@remotion/effects`.

Prefer a custom effect over `<HtmlInCanvas onPaint>` when the transformation should be reusable, parameterized, editable in Studio, or stackable with other effects.

For quick project-specific effects, keep the effect next to the composition, for example `src/effects/palette-map.ts`. For library effects intended for `@remotion/effects`, follow the repository's `add-effect` skill instead.

`createEffect()` expects:

- `type`: stable reverse-DNS identifier, for example `com.example.paletteMap`.
- `label`: Studio label, commonly `paletteMap()`.
- `documentationLink`: URL or `null`.
- `backend`: `"2d"`, `"webgl2"` or `"webgpu"`.
- `calculateKey(params)`: stable string containing every resolved parameter that changes output.
- `setup(target)`: create reusable backend state, or return `null`.
- `apply({source, target, width, height, params, state, flipSourceY})`: draw the transformed result into `target`.
- `cleanup(state)`: free resources created by `setup()`.
- `schema`: an `InteractivitySchema` for Studio controls. `disabled` is added automatically.
- `validateParams(params)`: throw on missing or invalid values.

Use `backend: "2d"` for simple pixel, filter, drawImage, or image-data effects. Use WebGL2 only when shader math or GPU performance is needed; during renders, enable WebGL as shown above.

```ts
import {createEffect, type InteractivitySchema} from 'remotion';

type MyEffectParams = {
  readonly amount?: number;
};

const myEffectSchema = {
  amount: {
    type: 'number',
    min: 0,
    max: 1,
    step: 0.01,
    default: 1,
    description: 'Amount',
  },
} as const satisfies InteractivitySchema;

const resolve = (params: MyEffectParams) => ({
  amount: params.amount ?? 1,
});

export const myEffect = createEffect<MyEffectParams, null>({
  type: 'com.example.myEffect',
  label: 'myEffect()',
  documentationLink: null,
  backend: '2d',
  calculateKey: (params) => {
    const {amount} = resolve(params);
    return `my-effect-${amount}`;
  },
  setup: () => null,
  apply: ({source, target, width, height, params}) => {
    const ctx = target.getContext('2d');
    if (!ctx) {
      throw new Error('Could not get a 2D context for myEffect().');
    }

    const {amount} = resolve(params);

    ctx.clearRect(0, 0, width, height);
    ctx.filter = `opacity(${amount * 100}%)`;
    ctx.drawImage(source, 0, 0, width, height);
    ctx.filter = 'none';
  },
  cleanup: () => undefined,
  schema: myEffectSchema,
  validateParams: ({amount = 1}) => {
    if (typeof amount !== 'number' || !Number.isFinite(amount) || amount < 0 || amount > 1) {
      throw new TypeError('amount must be a number between 0 and 1');
    }
  },
});
```

For a WebGL2 effect, compile/link shaders in `setup()`, keep the program, fullscreen quad, texture, and uniform locations in state, upload `source` in `apply()`, and free GPU resources in `cleanup()`. Minimal shape:

```ts
import {createEffect, type InteractivitySchema} from 'remotion';

type RgbShiftParams = {
  readonly amount?: number;
};

type RgbShiftState = {
  readonly gl: WebGL2RenderingContext;
  readonly program: WebGLProgram;
  readonly vao: WebGLVertexArrayObject;
  readonly vbo: WebGLBuffer;
  readonly texture: WebGLTexture;
  readonly uSource: WebGLUniformLocation | null;
  readonly uOffset: WebGLUniformLocation | null;
};

const rgbShiftSchema = {
  amount: {
    type: 'number',
    min: 0,
    max: 80,
    step: 1,
    default: 12,
    description: 'Amount',
  },
} as const satisfies InteractivitySchema;

export const rgbShift = createEffect<RgbShiftParams, RgbShiftState>({
  type: 'com.example.rgbShift',
  label: 'rgbShift()',
  documentationLink: null,
  backend: 'webgl2',
  calculateKey: ({amount = 12}) => `rgb-shift-${amount}`,
  setup: (target) => {
    const gl = target.getContext('webgl2', {
      premultipliedAlpha: true,
      alpha: true,
      preserveDrawingBuffer: true,
    });
    if (!gl) {
      throw new Error('Could not get a WebGL2 context for rgbShift().');
    }

    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);

    // Compile/link shaders, create a fullscreen quad VAO/VBO, create a
    // CLAMP_TO_EDGE RGBA texture, and get uSource/uOffset uniform locations.
    return createRgbShiftState(gl);
  },
  apply: ({source, width, height, params, state, flipSourceY}) => {
    const amount = params.amount ?? 12;
    const {gl} = state;

    gl.viewport(0, 0, width, height);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, flipSourceY);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, state.texture);
    gl.texImage2D(
      gl.TEXTURE_2D,
      0,
      gl.RGBA,
      gl.RGBA,
      gl.UNSIGNED_BYTE,
      source as TexImageSource,
    );

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.useProgram(state.program);
    if (state.uSource) gl.uniform1i(state.uSource, 0);
    if (state.uOffset) gl.uniform2f(state.uOffset, amount / width, 0);
    gl.bindVertexArray(state.vao);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  },
  cleanup: ({gl, program, vao, vbo, texture}) => {
    gl.deleteTexture(texture);
    gl.deleteBuffer(vbo);
    gl.deleteProgram(program);
    gl.deleteVertexArray(vao);
  },
  schema: rgbShiftSchema,
  validateParams: ({amount = 12}) => {
    if (typeof amount !== 'number' || !Number.isFinite(amount) || amount < 0 || amount > 80) {
      throw new TypeError('amount must be a number between 0 and 80');
    }
  },
});
```

For a complete 2D and WebGL2 pair, see `packages/example/src/EffectsTestbed/sample-posterize-2d.ts` and `packages/example/src/EffectsTestbed/sample-rgb-shift-webgl.ts`.

Use the returned factory in an `effects` array:

```tsx
import {CanvasImage, staticFile} from 'remotion';
import {myEffect} from './effects/my-effect';

export const MyComp: React.FC = () => {
  return (
    <CanvasImage
      src={staticFile('image.png')}
      effects={[myEffect({amount: 0.8})]}
    />
  );
};
```

When generating a custom effect, also:

- Include `disabled?: boolean` only through the returned factory; do not add it to the custom params type or schema.
- Validate required parameters at factory-call time with `validateParams`.
- Include all defaults in both `schema` and the `resolve()` helper.
- Reset mutable 2D context state such as `filter`, `globalAlpha`, transforms, and compositing after drawing.
- Preserve alpha unless the requested effect intentionally changes transparency.

<!-- ===== /file: remotion-best-practices/remotion-markup/effects.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/embedding-videos.md ===== -->

---
name: embedding-videos
description: Embedding videos in Remotion - trimming, volume, speed, looping, pitch
metadata:
  tags: video, media, trim, volume, speed, loop, pitch
---

# Using videos in Remotion

## Prerequisites

First, the @remotion/media package needs to be installed.  
If it is not, use the following command:

```bash
npx remotion add @remotion/media # If project uses npm
bunx remotion add @remotion/media # If project uses bun
yarn remotion add @remotion/media # If project uses yarn
pnpm exec remotion add @remotion/media # If project uses pnpm
```

Use `<Video>` from `@remotion/media` to embed videos into your composition.

```tsx
import { Video } from "@remotion/media";
import { staticFile } from "remotion";

export const MyComposition = () => {
  return <Video src={staticFile("video.mp4")} />;
};
```

Remote URLs are also supported:

```tsx
<Video src="https://remotion.media/video.mp4" />
```

## Trimming

Use `trimBefore` to skip the beginning of the video and `durationInFrames` to end it early. Values are in frames.

```tsx
const { fps } = useVideoConfig();

return (
  <Video
    src={staticFile("video.mp4")}
    trimBefore={2 * fps} // Skip the first 2 seconds
    durationInFrames={8 * fps} // Play 8 seconds, until the 10 second mark
  />
);
```

## Delaying

Set `from` directly on `<Video>` to delay when it appears:

```tsx
import { staticFile, useVideoConfig } from "remotion";
import { Video } from "@remotion/media";

const { fps } = useVideoConfig();

return (
  <Video from={fps} src={staticFile("video.mp4")} />
);
```

The video will appear after 1 second.

## Sizing and Position

Use the `style` prop to control size and position:

```tsx
<Video
  src={staticFile("video.mp4")}
  style={{
    width: 500,
    height: 300,
    position: "absolute",
    top: 100,
    left: 50,
  }}
  objectFit="cover"
/>
```

## Volume

Set a static volume (0 to 1):

```tsx
<Video src={staticFile("video.mp4")} volume={0.5} />
```

Use `useCurrentFrame()` and `interpolate()` for keyframed volume:

```tsx
import { Video } from "@remotion/media";
import { interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

return (
  <Video
    src={staticFile("video.mp4")}
    volume={interpolate(frame, [0, 1 * fps], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })}
  />
);
```

With Studio interactivity enabled, these keyframes can be edited and are shown as a volume curve in the timeline.

Use `muted` to silence the video entirely:

```tsx
<Video src={staticFile("video.mp4")} muted />
```

## Speed

Use `playbackRate` to change the playback speed:

```tsx
// 2x speed
<Video src={staticFile("video.mp4")} playbackRate={2} />
// Half speed
<Video src={staticFile("video.mp4")} playbackRate={0.5} />
```

Reverse playback is not supported.

## Looping

Use `loop` to loop the video indefinitely:

```tsx
<Video src={staticFile("video.mp4")} loop />
```

```tsx
import { Video } from "@remotion/media";
import { interpolate, staticFile, useCurrentFrame } from "remotion";

const frame = useCurrentFrame();

<Video
  src={staticFile("video.mp4")}
  loop
  volume={interpolate(frame, [0, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  })}
/>
```

## Pitch

Use `toneFrequency` to adjust the pitch without affecting speed. Values range from 0.01 to 2:

```tsx
<Video
  src={staticFile("video.mp4")}
  toneFrequency={1.5} // Higher pitch
/>
<Video
  src={staticFile("video.mp4")}
  toneFrequency={0.8} // Lower pitch
/>
```

Pitch shifting only works during server-side rendering, not in the Remotion Studio preview or in the `<Player />`.

<!-- ===== /file: remotion-best-practices/remotion-markup/embedding-videos.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/ffmpeg.md ===== -->

---
name: ffmpeg
description: Using FFmpeg and FFprobe in Remotion
metadata:
  tags: ffmpeg, ffprobe, video, trimming
---

## FFmpeg in Remotion

`ffmpeg` and `ffprobe` do not need to be installed. They are available via the `npx remotion ffmpeg` and `npx remotion ffprobe`:

```bash
npx remotion ffmpeg -i input.mp4 output.mp3
npx remotion ffprobe input.mp4
```

### Trimming videos

You have 2 options for trimming videos:

1. **Preferred**: Use the `trimBefore` and `durationInFrames` props of the `<Video>` component. This is non-destructive, requires no re-encoding, and you can change the trim at any time.

```tsx
import {Video} from '@remotion/media';

<Video
  src={staticFile('video.mp4')}
  trimBefore={5 * fps}
  durationInFrames={5 * fps}
/>;
```

2. Use the FFmpeg command line. You MUST re-encode the video to avoid frozen frames at the start of the video. Only use this if you need a standalone trimmed file (e.g. for upload or external use).

```bash
# Re-encodes from the exact frame
npx remotion ffmpeg -ss 00:00:05 -i public/input.mp4 -to 00:00:10 -c:v libx264 -c:a aac public/output.mp4
```

<!-- ===== /file: remotion-best-practices/remotion-markup/ffmpeg.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/gifs.md ===== -->

---
name: gif
description: Displaying GIFs, APNG, AVIF and WebP in Remotion
metadata:
  tags: gif, animation, images, animated, apng, avif, webp
---

# Using Animated images in Remotion

## Basic usage

Use `<AnimatedImage>` to display a GIF, APNG, AVIF or WebP image synchronized with Remotion's timeline:

```tsx
import { AnimatedImage, staticFile } from "remotion";

export const MyComposition = () => {
  return (
    <AnimatedImage
      src={staticFile("animation.gif")}
      width={500}
      height={500}
    />
  );
};
```

Remote URLs are also supported (must have CORS enabled):

```tsx
<AnimatedImage
  src="https://example.com/animation.gif"
  width={500}
  height={500}
/>
```

## Sizing and fit

Control how the image fills its container with the `fit` prop:

```tsx
// Stretch to fill (default)
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={300}
  fit="fill"
/>

// Maintain aspect ratio, fit inside container
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={300}
  fit="contain"
/>

// Fill container, crop if needed
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={300}
  fit="cover"
/>
```

## Playback speed

Use `playbackRate` to control the animation speed:

```tsx
// 2x speed
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={500}
  playbackRate={2}
/>
// Half speed
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={500}
  playbackRate={0.5}
/>
```

## Looping behavior

Control what happens when the animation finishes:

```tsx
// Loop indefinitely (default)
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={500}
  loopBehavior="loop"
/>

// Play once, show final frame
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={500}
  loopBehavior="pause-after-finish"
/>

// Play once, then clear canvas
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={500}
  loopBehavior="clear-after-finish"
/>
```

## Styling

Use the `style` prop for additional CSS (use `width` and `height` props for sizing):

```tsx
<AnimatedImage
  src={staticFile("animation.gif")}
  width={500}
  height={500}
  style={{
    borderRadius: 20,
    position: "absolute",
    top: 100,
    left: 50,
  }}
/>
```

## Getting GIF duration

Use `getGifDurationInSeconds()` from `@remotion/gif` to get the duration of a GIF.

```bash
npx remotion add @remotion/gif
```

```tsx
import { getGifDurationInSeconds } from "@remotion/gif";
import { staticFile } from "remotion";

const duration = await getGifDurationInSeconds(staticFile("animation.gif"));
console.log(duration); // e.g. 2.5
```

This is useful for setting the composition duration to match the GIF:

```tsx
import { getGifDurationInSeconds } from "@remotion/gif";
import { staticFile, CalculateMetadataFunction } from "remotion";

const calculateMetadata: CalculateMetadataFunction = async () => {
  const duration = await getGifDurationInSeconds(staticFile("animation.gif"));
  return {
    durationInFrames: Math.ceil(duration * 30),
  };
};
```

## Alternative

If `<AnimatedImage>` does not work (only supported in Chrome and Firefox), you can use `<Gif>` from `@remotion/gif` instead.

```bash
npx remotion add @remotion/gif # If project uses npm
bunx remotion add @remotion/gif # If project uses bun
yarn remotion add @remotion/gif # If project uses yarn
pnpm exec remotion add @remotion/gif # If project uses pnpm
```

```tsx
import { Gif } from "@remotion/gif";
import { staticFile } from "remotion";

export const MyComposition = () => {
  return <Gif src={staticFile("animation.gif")} width={500} height={500} />;
};
```

The `<Gif>` component has the same props as `<AnimatedImage>` but only supports GIF files.

<!-- ===== /file: remotion-best-practices/remotion-markup/gifs.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/google-fonts.md ===== -->

---
name: fonts
description: Loading Google Fonts and local fonts in Remotion
metadata:
  tags: fonts, google-fonts, typography, text
---

# Using fonts in Remotion

## Google Fonts with @remotion/google-fonts

The recommended way to use Google Fonts. It's type-safe and automatically blocks rendering until the font is ready.

### Prerequisites

First, the @remotion/google-fonts package needs to be installed.
If it is not installed, use the following command:

```bash
npx remotion add @remotion/google-fonts # If project uses npm
bunx remotion add @remotion/google-fonts # If project uses bun
yarn remotion add @remotion/google-fonts # If project uses yarn
pnpm exec remotion add @remotion/google-fonts # If project uses pnpm
```

```tsx
import { loadFont } from "@remotion/google-fonts/Lobster";

const { fontFamily } = loadFont();

export const MyComposition = () => {
  return (
    <div style={{ fontFamily }}>
      Hello World
    </div>
  );
};
```

Preferrably, specify only needed weights and subsets to reduce file size:

```tsx
import { loadFont } from "@remotion/google-fonts/Roboto";

const { fontFamily } = loadFont("normal", {
  weights: ["400", "700"],
  subsets: ["latin"],
});
```

## Using in components

Call `loadFont()` at the top level of your component or in a separate file that's imported early:

```tsx
import { loadFont } from "@remotion/google-fonts/Montserrat";

const { fontFamily } = loadFont("normal", {
  weights: ["400", "700"],
  subsets: ["latin"],
});

export const Title: React.FC<{ text: string }> = ({ text }) => {
  return (
    <h1
      style={{
        fontFamily,
        fontSize: 80,
        fontWeight: "bold",
      }}
    >
      {text}
    </h1>
  );
};
```

<!-- ===== /file: remotion-best-practices/remotion-markup/google-fonts.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/html-in-canvas.md ===== -->

# Using `<HtmlInCanvas>` in Remotion

Renders children into a `<canvas>` so you can post-process them with the Canvas 2D API or WebGL.

Only works in Chrome 149+ with the `chrome://flags/#canvas-draw-element` flag enabled.  
Give the user a notice.

## Nesting

Nest `<HtmlInCanvas>` components only when `HtmlInCanvas.isNestingSupported()` returns `true` (Chrome 157.0.8080.0 or newer with HTML-in-canvas enabled). Older browsers reject nesting.

## Enabling WebGL during renders

If you make use of WebGL during renders, you need to enable it:

From the CLI:

```bash
npx remotion render --gl=angle
```

Set it as the default for Studio and CLI (advised):

```ts
import { Config } from "@remotion/cli/config";

Config.setChromiumOpenGlRenderer("angle");
```

## Basic usage

By default, draws to canvas with no effect applied:

```tsx
import { HtmlInCanvas } from "remotion";

export const MyComp = () => {
  return (
    <HtmlInCanvas width={1280} height={720}>
      <div style={{ fontSize: 80 }}>
        Hello
      </div>
    </HtmlInCanvas>
  );
};
```

## 2D effect with `onPaint`

`onPaint` runs whenever the content updates. Call `ctx.drawElementImage(elementImage, 0, 0)` to draw the captured DOM.

```tsx
import {
  AbsoluteFill,
  HtmlInCanvas,
  type HtmlInCanvasOnPaint,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { useCallback } from "react";

export const Blur = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  const onPaint: HtmlInCanvasOnPaint = useCallback(
    ({ canvas, elementImage }) => {
      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("Failed to acquire 2D context");

      const blurPx = 4 + 18 * (0.5 + 0.5 * Math.sin((frame / fps) * Math.PI));

      ctx.reset();
      ctx.filter = `blur(${blurPx}px)`;
      ctx.drawElementImage(elementImage, 0, 0);
    },
    [frame, fps],
  );

  return (
    <HtmlInCanvas width={width} height={height} onPaint={onPaint}>
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          fontSize: 120,
        }}
      >
        <h1>
          Hello
        </h1>
      </AbsoluteFill>
    </HtmlInCanvas>
  );
};
```

## WebGL effects

For WebGL, set up the context, program, and texture in `onInit` and return a cleanup function. Allocate the texture with `gl.texImage2D(..., null)` when `elementImage` changes size. Inside `onPaint`, upload with `gl.texElementSubImage2D(gl.TEXTURE_2D, 0, 0, 0, elementImage)` and draw. Older Chromium versions only expose `gl.texElementImage2D()`; use it when the new method is absent.

For a fully working minimal example, see https://github.com/remotion-dev/remotion/blob/main/packages/docs/components/demos/HtmlInCanvasDocsDemoWebGL.tsx.

## Async `onPaint`

`onPaint` may be `async`. Remotion holds the frame open via `delayRender()` until the promise resolves. Useful for multi-pass effects with `createImageBitmap`.

<!-- ===== /file: remotion-best-practices/remotion-markup/html-in-canvas.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/images.md ===== -->

## Sizing and positioning

Use the `style` prop to control size and position:

```tsx
<Img
  src={staticFile("photo.png")}
  style={{
    width: 500,
    height: 300,
    position: "absolute",
    top: 100,
    left: 50,
    objectFit: "cover",
  }}
/>
```

## Dynamic image paths

Use template literals for dynamic file references:

```tsx
import { Img, staticFile, useCurrentFrame } from "remotion";

const frame = useCurrentFrame();

// Image sequence
<Img src={staticFile(`frames/frame${frame}.png`)} />

// Selecting based on props
<Img src={staticFile(`avatars/${props.userId}.png`)} />

// Conditional images
<Img
  src={staticFile(`icons/${isActive ? "active" : "inactive"}.svg`)}
/>
```

This pattern is useful for:

- Image sequences (frame-by-frame animations)
- User-specific avatars or profile images
- Theme-based icons
- State-dependent graphics

## Getting image dimensions

Use `getImageDimensions()` from `@remotion/media-utils` to get the dimensions of an image:

```tsx
import { getImageDimensions } from "@remotion/media-utils";
import { staticFile } from "remotion";

const { width, height } = await getImageDimensions(staticFile("photo.png"));
```

This is useful for calculating aspect ratios or sizing compositions:

```tsx
import { getImageDimensions } from "@remotion/media-utils";
import { staticFile, CalculateMetadataFunction } from "remotion";

const calculateMetadata: CalculateMetadataFunction = async () => {
  const { width, height } = await getImageDimensions(staticFile("photo.png"));
  return {
    width,
    height,
  };
};
```

<!-- ===== /file: remotion-best-practices/remotion-markup/images.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/light-leaks.md ===== -->

---
name: light-leaks
description: Light leak overlay effects for Remotion using lightLeak() from @remotion/effects.
metadata:
  tags: light-leaks, overlays, effects, transitions
---

## Light Leaks

This only works from Remotion 4.0.500 and up. Use `npx remotion versions` to check your Remotion version and `npx remotion upgrade` to upgrade your Remotion version.

Apply `lightLeak()` from `@remotion/effects/light-leak` to a canvas-based component such as `<Solid>`. Animate `progress` from `0` to `1`; the light leak reveals during the first half and retracts during the second half.

Typically use it inside a `<TransitionSeries.Overlay>` to play over the cut point between two scenes. See the **transitions** rule for `<TransitionSeries>` and overlay usage.

## Prerequisites

```bash
npx remotion add @remotion/effects
```

## Light leak overlay component

Keep the `progress` calculation inline so it is editable in Remotion Studio:

```tsx
import {lightLeak} from '@remotion/effects/light-leak';
import {interpolate, Solid, useCurrentFrame, useVideoConfig} from 'remotion';

const LightLeakOverlay: React.FC<{
  seed?: number;
  hueShift?: number;
}> = ({seed = 0, hueShift = 0}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, height, width} = useVideoConfig();

  return (
    <Solid
      width={width}
      height={height}
      effects={[
        lightLeak({
          seed,
          hueShift,
          progress: interpolate(frame, [0, durationInFrames - 1], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }),
      ]}
    />
  );
};
```

## Basic usage with TransitionSeries

```tsx
import {TransitionSeries} from '@remotion/transitions';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={60}>
    <SceneA />
  </TransitionSeries.Sequence>
  <TransitionSeries.Overlay durationInFrames={30}>
    <LightLeakOverlay />
  </TransitionSeries.Overlay>
  <TransitionSeries.Sequence durationInFrames={60}>
    <SceneB />
  </TransitionSeries.Sequence>
</TransitionSeries>;
```

## Options

- `progress?` — controls the evolve/retract phase from `0` to `1`. Effects do not animate on their own, so drive it with `useCurrentFrame()` and `interpolate()`. Default: `0.5`.
- `seed?` — determines the shape of the light leak pattern. Different seeds produce different patterns. Default: `0`.
- `hueShift?` — rotates the hue in degrees (`0`–`360`). Default: `0` (yellow-to-orange). `120` = green, `240` = blue.
- `disabled?` — skips the effect when `true`. Default: `false`.

## Customizing the look

```tsx
// Blue-tinted light leak with a different pattern
<LightLeakOverlay seed={5} hueShift={240} />;

// Green-tinted light leak
<LightLeakOverlay seed={2} hueShift={120} />;
```

## Standalone usage

The overlay component can also be used outside of `<TransitionSeries>` as a decorative layer in any composition:

```tsx
const MyComp: React.FC = () => (
  <>
    <MyContent />
    <LightLeakOverlay seed={3} />
  </>
);
```

`lightLeak()` uses WebGL2. Enable WebGL during rendering with `Config.setChromiumOpenGlRenderer("angle")`.

<!-- ===== /file: remotion-best-practices/remotion-markup/light-leaks.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/local-fonts.md ===== -->

For local font files, use the `@remotion/fonts` package.

### Prerequisites

First, install @remotion/fonts:

```bash
npx remotion add @remotion/fonts # If project uses npm
bunx remotion add @remotion/fonts # If project uses bun
yarn remotion add @remotion/fonts # If project uses yarn
pnpm exec remotion add @remotion/fonts # If project uses pnpm
```

### Loading a local font

Place your font file in the `public/` folder and use `loadFont()`:

```tsx
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

await loadFont({
  family: "MyFont",
  url: staticFile("MyFont-Regular.woff2"),
});

export const MyComposition = () => {
  return (
    <div style={{ fontFamily: "MyFont" }}>
      Hello World
    </div>
  );
};
```

### Loading multiple weights

Load each weight separately with the same family name:

```tsx
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

await Promise.all([
  loadFont({
    family: "Inter",
    url: staticFile("Inter-Regular.woff2"),
    weight: "400",
  }),
  loadFont({
    family: "Inter",
    url: staticFile("Inter-Bold.woff2"),
    weight: "700",
  }),
]);
```

### Available options

```tsx
loadFont({
  family: "MyFont", // Required: name to use in CSS
  url: staticFile("font.woff2"), // Required: font file URL
  format: "woff2", // Optional: auto-detected from extension
  weight: "400", // Optional: font weight
  style: "normal", // Optional: normal or italic
  display: "block", // Optional: font-display behavior
});
```

<!-- ===== /file: remotion-best-practices/remotion-markup/local-fonts.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/lottie.md ===== -->

---
name: lottie
description: Embedding Lottie animations in Remotion.
metadata:
  category: Animation
---

# Using Lottie Animations in Remotion

## Prerequisites

First, the @remotion/lottie package needs to be installed.  
If it is not, use the following command:

```bash
npx remotion add @remotion/lottie # If project uses npm
bunx remotion add @remotion/lottie # If project uses bun
yarn remotion add @remotion/lottie # If project uses yarn
pnpm exec remotion add @remotion/lottie # If project uses pnpm
```

## Displaying a Lottie file

To import a Lottie animation:

- Fetch the Lottie asset
- Wrap the loading process in `delayRender()` and `continueRender()`
- Save the animation data in a state
- Render the Lottie animation using the `Lottie` component from the `@remotion/lottie` package

```tsx
import { Lottie, LottieAnimationData } from "@remotion/lottie";
import { useEffect, useState } from "react";
import { cancelRender, continueRender, delayRender } from "remotion";

export const MyAnimation = () => {
  const [handle] = useState(() => delayRender("Loading Lottie animation"));

  const [animationData, setAnimationData] =
    useState<LottieAnimationData | null>(null);

  useEffect(() => {
    fetch("https://assets4.lottiefiles.com/packages/lf20_zyquagfl.json")
      .then((data) => data.json())
      .then((json) => {
        setAnimationData(json);
        continueRender(handle);
      })
      .catch((err) => {
        cancelRender(err);
      });
  }, [handle]);

  if (!animationData) {
    return null;
  }

  return <Lottie animationData={animationData} />;
};
```

## Styling and animating

Lottie supports the `style` prop to allow styles and animations:

```tsx
return (
  <Lottie
    animationData={animationData}
    style={{ width: 400, height: 400 }}
  />
);
```

<!-- ===== /file: remotion-best-practices/remotion-markup/lottie.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/measuring-dom-nodes.md ===== -->

---
name: measuring-dom-nodes
description: Measuring DOM element dimensions in Remotion
metadata:
  tags: measure, layout, dimensions, getBoundingClientRect, scale
---

# Measuring DOM nodes in Remotion

Remotion applies a `scale()` transform to the video container, which affects values from `getBoundingClientRect()`. Use `useCurrentScale()` to get correct measurements.

## Measuring element dimensions

```tsx
import { useCurrentScale } from "remotion";
import { useRef, useEffect, useState } from "react";

export const MyComponent = () => {
  const ref = useRef<HTMLDivElement>(null);
  const scale = useCurrentScale();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    setDimensions({
      width: rect.width / scale,
      height: rect.height / scale,
    });
  }, [scale]);

  return (
    <div ref={ref}>
      Content to measure
    </div>
  );
};
```

<!-- ===== /file: remotion-best-practices/remotion-markup/measuring-dom-nodes.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/measuring-text.md ===== -->

---
name: measuring-text
description: Measuring text dimensions, fitting text to containers, and checking overflow
metadata:
  tags: measure, text, layout, dimensions, fitText, fillTextBox
---

# Measuring text in Remotion

## Prerequisites

Install @remotion/layout-utils if it is not already installed:

```bash
npx remotion add @remotion/layout-utils
```

## Measuring text dimensions

Use `measureText()` to calculate the width and height of text:

```tsx
import { measureText } from "@remotion/layout-utils";

const { width, height } = measureText({
  text: "Hello World",
  fontFamily: "Arial",
  fontSize: 32,
  fontWeight: "bold",
});
```

Results are cached - duplicate calls return the cached result.

## Fitting text to a width

Use `fitText()` to find the optimal font size for a container:

```tsx
import { fitText } from "@remotion/layout-utils";

const { fontSize } = fitText({
  text: "Hello World",
  withinWidth: 600,
  fontFamily: "Inter",
  fontWeight: "bold",
});

return (
  <div
    style={{
      fontSize: Math.min(fontSize, 80), // Cap at 80px
      fontFamily: "Inter",
      fontWeight: "bold",
    }}
  >
    Hello World
  </div>
);
```

## Checking text overflow

Use `fillTextBox()` to check if text exceeds a box:

```tsx
import { fillTextBox } from "@remotion/layout-utils";

const box = fillTextBox({ maxBoxWidth: 400, maxLines: 3 });

const words = ["Hello", "World", "This", "is", "a", "test"];
for (const word of words) {
  const { exceedsBox } = box.add({
    text: word + " ",
    fontFamily: "Arial",
    fontSize: 24,
  });
  if (exceedsBox) {
    // Text would overflow, handle accordingly
    break;
  }
}
```

## Best practices

**Load fonts first:** Only call measurement functions after fonts are loaded.

```tsx
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily, waitUntilDone } = loadFont("normal", {
  weights: ["400"],
  subsets: ["latin"],
});

waitUntilDone().then(() => {
  // Now safe to measure
  const { width } = measureText({
    text: "Hello",
    fontFamily,
    fontSize: 32,
  });
});
```

**Use validateFontIsLoaded:** Catch font loading issues early:

```tsx
measureText({
  text: "Hello",
  fontFamily: "MyCustomFont",
  fontSize: 32,
  validateFontIsLoaded: true, // Throws if font not loaded
});
```

**Match font properties:** Use the same properties for measurement and rendering:

```tsx
const fontStyle = {
  fontFamily: "Inter",
  fontSize: 32,
  fontWeight: "bold" as const,
  letterSpacing: "0.5px",
};

const { width } = measureText({
  text: "Hello",
  ...fontStyle,
});

return (
  <div style={fontStyle}>
    Hello
  </div>
);
```

**Avoid padding and border:** Use `outline` instead of `border` to prevent layout differences:

```tsx
<div style={{ outline: "2px solid red" }}>
  Text
</div>
```

<!-- ===== /file: remotion-best-practices/remotion-markup/measuring-text.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/motion-blur.md ===== -->

# Motion blur

Use `@remotion/motion-blur` for frame-driven motion blur.  
Install it with `npx remotion add @remotion/motion-blur`.

`<HtmlInCanvasMotionBlur>` is the state of the art in Remotion for blurring animated HTML. It captures the content at fractional frames and averages its pixels in a canvas.

## `<HtmlInCanvasMotionBlur>`

Available from Remotion 4.0.529.  
Supply the canvas `width` and `height`, usually from `useVideoConfig()`.  
`shutterAngle` defaults to `180` and accepts `0` to `360`.
`0` disables blur. `samples` defaults to `8` and must be an integer from `1` to `64`. More samples can smooth the blur but increase preview and render cost.

Call `useCurrentFrame()` inside the child component so each sample receives its own frame.

```tsx
import {
  HtmlInCanvasMotionBlur,
} from '@remotion/motion-blur';
import {useCurrentFrame, useVideoConfig} from 'remotion';

const MovingBox = () => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        position: 'absolute',
        left: frame * 10,
        top: 200,
        width: 120,
        height: 120,
        backgroundColor: '#ff6b6b',
      }}
    />
  );
};

export const HtmlInCanvasBlur = () => {
  const {width, height} = useVideoConfig();

  return (
    <HtmlInCanvasMotionBlur
      width={width}
      height={height}
      samples={8}
      shutterAngle={180}
    >
      <MovingBox />
    </HtmlInCanvasMotionBlur>
  );
};
```

For live preview, enable HTML-in-canvas in Chrome 149 or later with `chrome://flags/#canvas-draw-element`.  
No configuration for rendering is necessary.

Nest `<HtmlInCanvas>` or `<HtmlInCanvasMotionBlur>` components only when `HtmlInCanvas.isNestingSupported()` returns `true` (Chrome 157.0.8080.0 or newer with HTML-in-canvas enabled).

If HTML-in-canvas is unavailable, see the [motion blur guide](https://www.remotion.dev/docs/motion-blur) for other options. See the [`<HtmlInCanvasMotionBlur>` reference](https://www.remotion.dev/docs/motion-blur/html-in-canvas-motion-blur) for API details.

<!-- ===== /file: remotion-best-practices/remotion-markup/motion-blur.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/multi-scene-video.md ===== -->

# Multi-scene videos

Give each substantial scene its own component and connect it when it benefits
from an independent editing timeline. Keep each instance's name, timing, and
props inline in the parent.

Choose the parent structure from the editing behavior:

- For independent scene start times, use a named `Track` with explicit `from`
  and `durationInFrames` on each scene. Its items must not overlap.
- For scenes that should remain adjacent as their durations change, use
  `TransitionSeries`. Keep each scene inside its own
  `TransitionSeries.Sequence`, with duration and source trim on that boundary.
  Add transitions when needed and account for their overlaps in the total
  composition duration.

Follow [editable timeline structure](../remotion-interactivity/timeline-structure.md)
for a complete scene, parent, and registration example. See
[transitions](transitions.md) for transition timing and presentations, and
[connected compositions](connected-compositions.md) for extraction and
verification in the full video.

<!-- ===== /file: remotion-best-practices/remotion-markup/multi-scene-video.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/parameters.md ===== -->

---
name: parameters
description: Make a video parametrizable by adding a Zod schema
metadata:
  tags: parameters, zod, schema
---

To make a video parametrizable, a Zod schema can be added to a composition.

First, `zod` must be installed .

Search the project for lockfiles and run the correct command depending on the package manager:

If `package-lock.json` is found, use the following command:

```bash
npm i zod
```

If `bun.lockb` is found, use the following command:

```bash
bun i zod
```

If `yarn.lock` is found, use the following command:

```bash
yarn add zod
```

If `pnpm-lock.yaml` is found, use the following command:

```bash
pnpm i zod
```

Then, a Zod schema can be defined alongside the component:

```tsx title="src/MyComposition.tsx"
import { z } from "zod";

export const MyCompositionSchema = z.object({
  title: z.string(),
});

const MyComponent: React.FC<z.infer<typeof MyCompositionSchema>> = () => {
  return (
    <div>
      <h1>
        {props.title}
      </h1>
    </div>
  );
};
```

In the root file, the schema can be passed to the composition:

```tsx title="src/Root.tsx"
import { Composition } from "remotion";
import { MycComponent, MyCompositionSchema } from "./MyComposition";

export const RemotionRoot = () => {
  return (
    <Composition
      id="MyComposition"
      component={MyComponent}
      durationInFrames={100}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ title: "Hello World" }}
      schema={MyCompositionSchema}
    />
  );
};
```

Now, the user can edit the parameter visually in the sidebar.

All schemas that are supported by Zod are supported by Remotion.

Remotion requires that the top-level type is a z.object(), because the collection of props of a React component is always an object.

## Color picker

For adding a color picker, use `zColor()` from `@remotion/zod-types`.

If it is not installed, use the following command:

```bash
npx remotion add @remotion/zod-types # If project uses npm
bunx remotion add @remotion/zod-types # If project uses bun
yarn remotion add @remotion/zod-types # If project uses yarn
pnpm exec remotion add @remotion/zod-types # If project uses pnpm
```

Then import `zColor` from `@remotion/zod-types`:

```tsx
import { zColor } from "@remotion/zod-types";
```

Then use it in the schema:

```tsx
export const MyCompositionSchema = z.object({
  color: zColor(),
});
```

<!-- ===== /file: remotion-best-practices/remotion-markup/parameters.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/REFERENCE.md ===== -->

---
name: remotion-maps
description: Remotion Map animation knowledge
version: 4.0.539
---

# Remotion Maps

Choose exactly one technique from the intended shot, then load only that technique's `TECHNIQUE.md`.
Every technique directory is self-contained and may be removed without breaking the others.

## [Static map](techniques/static-map/TECHNIQUE.md)

- Requires you grab a satellite image and mount it in a `<Img>` tag, and animate on top

## [Mapbox](techniques/mapbox/TECHNIQUE.md)

- Requires a Mapbox key
- Nicer styles by default
- Map can display a round globe when zoomed out
- Includes nice 3D buildings such as the Eiffel tower

## [MapLibre](techniques/maplibre/TECHNIQUE.md)

- Requires no API key, fully free
- Does not include 3D building

## [MapTiler](techniques/maptiler/TECHNIQUE.md)

- Uses MapTiler
- Annotations can be drawn on top of geographic features: borders, rivers, labels

## [CesiumJS](techniques/cesium/TECHNIQUE.md)

- Flythroughs through terrain and mountains
- "Flight simulator" perspective

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/TECHNIQUE.md ===== -->

# CesiumJS — 3D flyovers in Remotion

Instructions for achieving map animations with "flight-simulator" perspective in Remotion.

## Modes

| Mode        | Data                                                  | Use for                                                |
| ----------- | ----------------------------------------------------- | ------------------------------------------------------ |
| `landscape` | MapTiler `terrain-quantized-mesh-v2` + `satellite-v2` | Mountains, gorges, rivers, coastlines and rural routes |
| `city`      | Google Photorealistic 3D Tiles                        | Cities, architecture and recognizable landmarks        |

Do not use footprint extrusions for city flyovers. They produce crude building blocks rather than
textured architecture.

## Credentials

For `landscape`, set:

```text
REMOTION_MAPTILER_KEY=...
```

Create a MapTiler key at https://cloud.maptiler.com/account/keys/.

For `city`, set:

```text
REMOTION_GOOGLE_MAPS_API_KEY=...
```

Create a billing-enabled Google Map Tiles API key by following
https://developers.google.com/maps/documentation/tile/get-api-key. Enable the **Map Tiles API** and
restrict the key to that API. Ensure its application restriction permits local headless Remotion
requests.

## Build the flight

1. Copy `assets/CesiumFlythrough.tsx`, a path JSON and `assets/example-Root.tsx` into the Remotion
   project, or import the component directly.
2. Supply the camera route as `[longitude, latitude][]`. Use only meaningful control points; do not hand-author dozens of tiny corrections.
3. Leave `pathSmoothingPasses={3}` initially. The component applies repeated Chaikin corner cutting, turning straight-then-corner input into a continuous swerve. Increase to `4` for a softer route or reduce to `2` when the camera must follow a tight corridor.
4. Set absolute camera altitudes for the location. City cameras normally fly lower than landscape
   cameras.
5. Render a middle-frame still before rendering the full video.

```tsx
<CesiumFlythrough
  mode="city"
  path={cameraPath}
  pathSmoothingPasses={3}
  altitudeStart={700}
  altitudeEnd={500}
  lookAheadKm={0.7}
  travelKm={4.5}
/>
```

## Camera behavior

Walk the smoothed curve by arc length for constant ground speed. Aim at a real point farther along
the curve rather than its next vertex. Derive roll from the change in look-ahead bearing so the
camera banks into a turn instead of twitching left and right.

For landscape routes, `scripts/prep-cesium-path.mjs` also clips, resamples, smooths and dampens a
GeoJSON centerline before the component applies its final curve smoothing.


## Mechanics

- Set `viewer.useDefaultRenderLoop = false`.
- Call `viewer.render()`, never `scene.render()`, while settling.
- Use `preserveDrawingBuffer: true`.
- Gate initialization and every frame with `delayRender`.
- Drive camera animation from `useCurrentFrame()`; do not use CSS transitions or browser-timed animation.
- Settle landscapes on `globe.tilesLoaded` and cities on `tileset.tilesLoaded`.
- Keep all provider attribution visible.
- Record the source and effective date of custom or disputed geography.
- Inspect rendered pixels, not only Studio playback, at every required aspect ratio.
- Read `references/3d-flyover-architecture.md` for camera math, `references/3d-data-sources.md` for provider details, and `references/3d-troubleshooting.md` for blank, coarse, unauthorized or timed-out renders.

## Files

- `assets/CesiumFlythrough.tsx` — reusable two-mode component.
- `assets/flight-path.ts` — dependency-free Chaikin route smoothing.
- `assets/example-Root.tsx` — landscape and city compositions.
- `assets/cesium-path.json` — sample landscape route.
- `assets/city-path.json` — sample city route.
- `assets/sample-river.geojson` — sample path-preparation input.
- `scripts/prep-cesium-path.mjs` — dependency-free landscape route preparation.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-data-sources.md ===== -->

# Flyover data sources

## Landscape

Use MapTiler for both layers:

- `terrain-quantized-mesh-v2`: elevation encoded as Cesium quantized-mesh terrain.
- `satellite-v2`: raster satellite imagery draped on that mesh.

CesiumJS renders the layers; it does not supply the data. Set `REMOTION_MAPTILER_KEY`.

Create a key:

- https://cloud.maptiler.com/account/keys/

Official documentation:

- https://docs.maptiler.com/cesium/
- https://docs.maptiler.com/schema-raster/terrain-3d/

## City

Use Google Photorealistic 3D Tiles. Google supplies one high-resolution 3D mesh already textured
with imagery. Disable the Cesium globe and do not add MapTiler terrain or satellite beneath it. Set
`REMOTION_GOOGLE_MAPS_API_KEY`.

Create and configure a key:

- https://developers.google.com/maps/documentation/tile/get-api-key

Enable the Map Tiles API in a billing-enabled Google Cloud project and restrict the key to that API.
The application restriction must permit the local headless Remotion request.

Official documentation:

- https://developers.google.com/maps/documentation/tile/3d-tiles
- https://developers.google.com/maps/documentation/tile/policies

## Why not extruded buildings

OSM-, Overture- and vector-tile building products primarily provide footprints, approximate heights
and optional roof attributes. They are useful for analytical or stylized maps, but they do not
provide the textured architecture required for a cinematic city flyover.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-data-sources.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-flyover-architecture.md ===== -->

# 3D Flyover — architecture reference

Deep detail behind `TECHNIQUE.md`: provider loading, the camera-path pipeline, per-frame camera math, and
the proven terrain values. Both landscape and city modes have been forward-tested through Remotion.

## 1. Provider initialization

Create the Viewer with `baseLayer: false`, UI widgets disabled, and
`contextOptions.webgl.preserveDrawingBuffer: true`. Never hide the credit display.

### Landscape

Add MapTiler `satellite-v2` with `UrlTemplateImageryProvider`, then load
`terrain-quantized-mesh-v2` with `CesiumTerrainProvider.fromUrl({requestVertexNormals: true})`.
MapTiler supplies both datasets; no Cesium ion token is required.

### City

Do not add MapTiler. Hide the globe, then add:

```ts
viewer.scene.globe.show = false;
const tileset = await Cesium.Cesium3DTileset.fromUrl(
  `https://tile.googleapis.com/v1/3dtiles/root.json?key=${GOOGLE_KEY}`,
  {showCreditsOnScreen: true, maximumScreenSpaceError: 4},
);
viewer.scene.primitives.add(tileset);
```

Lower `maximumScreenSpaceError` improves refinement at substantial download/render cost. Start at
`4` for a hero landmark and `6–8` for wider urban shots. Enforce the Google 30-second promotional
video ceiling in the component.

Load Cesium from the CDN after setting `window.CESIUM_BASE_URL`; the tested version is `1.143`.

## 2. The camera path — structure & generation

Four properties matter, in order:

1. **Continuous curvature** — the camera must flow through curves, never "fly straight, snap to a new
   heading, fly straight." The component applies three passes of **Chaikin corner cutting** to every
   supplied path. Each pass replaces a segment with quarter and three-quarter points, rounding a
   corner into a curve. Three passes are the default; four is softer, two is tighter.
2. **Constant ground speed** — precompute cumulative distance along the rounded curve and interpolate
   by arc length. Do not animate by source-point index; unequal source spacing creates speed bumps.
3. **Minimized amplitude** — for detailed landscape centerlines, dampen the prepared path toward its
   straight start→end chord by a fixed fraction `DAMP` (0 = dead straight, 1 = full river). This is
   the single swerve-amplitude knob.
4. **Enough length** — `PATHKM ≥ TRAVEL_KM + 2·LOOK_AHEAD_KM` so the look-ahead aim never clamps.

`../scripts/prep-cesium-path.mjs` does: clip a window of the source centerline → resample to even
arc-length spacing (0.1 km) → moving-average smooth (±2.8 km window, 2 passes) → dampen toward the chord
(`DAMP=0.45`). Validate with the heading-delta probe it prints — deltas should be small and change
_gradually_ (water-wars: `3,0,-1,-3,-4,1,7,9,5,-5,-12,-7,…`). Big jumps = corners = bad.

The component then applies Chaikin smoothing to this prepared route, or directly to a short
hand-authored city route. Keep city control points sparse and intentional; smoothing cannot rescue a
zig-zagging route that crosses the subject repeatedly.

**Source data:** OSM via Overpass (~0.3 km vertex spacing) — Natural Earth is too coarse for inner
gorges. overpass-api.de is often busy → mirror `overpass.kumi.systems`.

## 3. Camera animation per frame (position, heading, pitch, bank)

Walk the path by **arc length** (precompute cumulative distances once). Every frame:

- **Position** = the point at `dCam` km along the path, altitude `lerp(ALT_START, ALT_END, prog)`.
- **Heading** = bearing from the camera point to a **real point `LOOK_AHEAD_KM` further along the same
  path**. A far aim averages wiggle → smooth heading; on a curved path it leads into the bend, so the
  heading turns gently with the path. (A local-tangent aim spins the camera at every kink — don't.)
- **Pitch** = constant. We keep a MapLibre-style param `PITCH_FROM_NADIR` (90 = horizon), then convert:
  **Cesium pitch = `-(90 - PITCH_FROM_NADIR)`** (Cesium: 0 = horizon, -90 = straight down). 76° → -14°.
- **Bank (roll)** = lean _into_ the turn — the helicopter tell. Measure turn rate as the bearing change
  between `aim` and a point `2·LOOK_AHEAD_KM` ahead; `roll = clamp(dH · BANK_GAIN, ±MAX_BANK)`. Because
  the path is smooth, `dH` changes gradually → the bank eases in and out, never jerks.

```ts
const setCamera = (C, viewer, prog) => {
  const dCam = Math.min(TRAVEL_KM, PATHKM - LOOK_AHEAD_KM * 2) * prog;
  const cam  = alongPath(dCam);                    // arc-length point
  const aim  = alongPath(dCam + LOOK_AHEAD_KM);     // heading target (real point on the path)
  const aim2 = alongPath(dCam + LOOK_AHEAD_KM * 2); // turn-rate probe → bank
  const heading = bearing(cam, aim);
  let dH = bearing(aim, aim2) - heading; while (dH > Math.PI) dH -= 2*Math.PI; while (dH < -Math.PI) dH += 2*Math.PI;
  viewer.camera.setView({
    destination: C.Cartesian3.fromDegrees(cam[0], cam[1], lerp(ALT_START, ALT_END, prog)),
    orientation: { heading, pitch: C.Math.toRadians(-(90 - PITCH_FROM_NADIR)), roll: clamp(dH * BANK_GAIN, -MAX_BANK, MAX_BANK) },
  });
};
```

> **Cesium vs MapLibre conventions (gotcha):** Cesium heading is radians, 0 = north, clockwise. Pitch
> 0 = horizon, negative = down (MapLibre is the inverse). Roll positive = bank right; tune the sign by eye.

## 4. The feel — proven water-wars values

| Param                    | Value                  | Meaning                                                                              |
| ------------------------ | ---------------------- | ------------------------------------------------------------------------------------ |
| `TRAVEL_KM`              | 13                     | How far the camera travels. **Speed = `TRAVEL_KM / durationSeconds`.**               |
| duration                 | 24 s (720 f @30)       | 13 km / 24 s ≈ **0.54 km/s** — a slow, peaceful glide. 8 s felt "extremely rushed".  |
| `ALT_START → ALT_END`    | 4600 → 4300 m ASL      | Absolute (terrain-independent). Inside the corridor walls → fly _through_, not over. |
| `LOOK_AHEAD_KM`          | 1.5                    | Heading smoothness vs responsiveness.                                                |
| `PITCH_FROM_NADIR`       | 76°                    | Stare-ahead down the corridor (90 = level). → Cesium -14°.                           |
| `MAX_BANK` / `BANK_GAIN` | 0.13 rad (~7.5°) / 0.6 | Helicopter lean into turns.                                                          |
| `verticalExaggeration`   | 1.1                    | Subtle terrain drama.                                                                |
| `DAMP` (prep)            | 0.45                   | Swerve amount: higher = weavier, lower = straighter.                                 |

**A slow camera renders fast.** At 0.54 km/s the camera moves ~18 m/frame, so tiles stay cached and each
`settle()` returns almost immediately; the 720-frame render completed in one pass (no chunk-rendering).

## 5. The complete component

The full, runnable component is `../assets/CesiumFlythrough.tsx` — read it directly. Its shape:

- `loadCesium()` — inject `CESIUM_BASE_URL` + the CDN `Cesium.js`, resolve when loaded.
- init effect — build the Viewer (§1), `setCamera(…, 0)`, `await settle(viewer)`, `continueRender`.
- `settle(viewer)` — loop `viewer.render()` until `globe.tilesLoaded` for landscapes or
  `tileset.tilesLoaded` for cities is stable for ~8 ticks (cap ~600).
- per-frame effect — `delayRender({timeoutInMilliseconds: 60000})` → `setCamera(prog)` → `settle()` → `continueRender`.

## 6. Render

```bash
bunx remotion still   src/index.ts <Comp> out.png --frame=N --gl=angle --timeout=180000   # validate framing/bank first
bunx remotion render  src/index.ts <Comp> out.mp4  --gl=angle --concurrency=1 --timeout=180000
```

`--gl=angle` is mandatory. Use `--concurrency=1`; `settle()` already serializes tile loading.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-flyover-architecture.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-troubleshooting.md ===== -->

# 3D Flyover — troubleshooting

## The headless dead-end (why we render through Remotion)

Cesium's globe **will not draw in a standalone headless Playwright/Chromium** harness. Verified on
Apple M4 (ANGLE Metal active, WebGL working): the skybox/stars render, but the globe surface produces
**zero draw commands** (`scene.frameState.commandList.length === 0`), `globe.tilesLoaded` never goes
true, and frames come back as the black starfield. No network failures; `sampleTerrainMostDetailed`
succeeds (terrain data is reachable). Dead-ends tried, all failed:

- default render loop, manual `scene.render()`, manual `viewer.render()`, headed mode (context-destroyed).

**What works:** render Cesium **through Remotion** — same headless Chrome, but driven by Remotion's frame
loop with these four non-negotiables:

1. `useDefaultRenderLoop = false` — drive frames by hand.
2. Per frame call **`viewer.render()`**, NOT `scene.render()`. `viewer.render()` does the full frame
   (`initializeFrame` → tile streaming → render); `scene.render()` skips frame-init, so tiles never
   advance and the globe never appears. **This is the single most important line.**
3. `contextOptions: { webgl: { preserveDrawingBuffer: true } }` so Remotion's screenshot captures pixels.
4. Gate init + every frame with `delayRender(…, {timeoutInMilliseconds})` — tile loading can exceed Remotion's
   default; use 60–120 s.

The standalone `flythrough.html` / `render.mjs` / `probe.mjs` from the original spike are kept only as the
record of this dead-end. The canonical render path is the Remotion component
(`../assets/CesiumFlythrough.tsx`).

## Symptom → fix

| Symptom                                                   | Cause                                                                                                         | Fix                                                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Frames are black with stars                               | Globe not drawing (headless Playwright, or `scene.render()` used)                                             | Render through Remotion; use `viewer.render()`; `useDefaultRenderLoop=false`.                       |
| Screenshots blank/transparent                             | No `preserveDrawingBuffer`                                                                                    | `contextOptions:{ webgl:{ preserveDrawingBuffer:true } }`.                                          |
| "delayRender timed out"                                   | Cold tiles exceed the default                                                                                 | `delayRender(…, {timeoutInMilliseconds: 120000})` + `--timeout=180000`.                             |
| Globe is a dark/navy sphere                               | Imagery layer didn't attach                                                                                   | `baseLayer:false` then `viewer.imageryLayers.addImageryProvider(...)`.                              |
| High-pitch frame shows a void/starfield above the horizon | No atmosphere                                                                                                 | `viewer.scene.skyAtmosphere.show = true`.                                                           |
| 403 on tiles in headless                                  | Domain-locked MapTiler key                                                                                    | Use an **unrestricted** key.                                                                        |
| Google root tileset returns 403                           | Map Tiles API disabled, billing absent, wrong key, or application restriction blocks local headless rendering | Enable Map Tiles API and billing; restrict the key to that API while allowing the Remotion request. |
| Google scene shows a duplicate/competing surface          | MapTiler or the Cesium globe is still enabled                                                                 | Do not add MapTiler; set `viewer.scene.globe.show=false`.                                           |
| Google mesh remains coarse                                | Screen-space error is too high or the capture starts before refinement                                        | Lower `maximumScreenSpaceError`; settle on `tileset.tilesLoaded`.                                   |
| WebGL unavailable / software renderer                     | Missing GL flag                                                                                               | Render with `--gl=angle`.                                                                           |
| Camera looks at sky / ground, not terrain                 | Pitch sign / convention                                                                                       | Cesium pitch 0 = horizon, negative = down (inverse of MapLibre); `-(90 - PITCH_FROM_NADIR)`.        |
| Aim/turn-probe clamps near the end                        | Path too short                                                                                                | `PATHKM ≥ TRAVEL_KM + 2·LOOK_AHEAD_KM`; raise `WINDOW_KM` in prep.                                  |
| Path feels like straight-then-corner                      | Douglas-Peucker simplification                                                                                | Use resample → moving-average smooth (see architecture §2), not `turf.simplify`.                    |
| Camera bumps left and right instead of swerving           | Sparse route vertices are still being followed as straight segments                                           | Keep `pathSmoothingPasses={3}`; use sparse intentional control points and arc-length movement.      |

## Gotchas checklist

- **`viewer.render()`, never `scene.render()`** per frame. The single biggest trap.
- Cesium loads from **CDN**; set `window.CESIUM_BASE_URL` _before_ injecting the script.
- `preserveDrawingBuffer: true` or screenshots are blank.
- `delayRender` uses `timeoutInMilliseconds`; set it to at least 60,000.
- Terrain: `baseLayer:false`, then add MapTiler imagery.
- Google: no MapTiler, hide the globe, retain `showCreditsOnScreen:true`.
- Always `skyAtmosphere.show = true`.
- Validate the path's heading-delta probe and render one **still** (framing + bank) before the full mp4.
- Cesium pitch/roll conventions are inverted vs MapLibre.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-troubleshooting.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/mapbox/TECHNIQUE.md ===== -->

---
name: maps-mapbox
description: Make deterministic Remotion 2D map animations with Mapbox GL JS and Turf. Use when the user chooses Mapbox for animated routes, map markers, labels, camera movement, or Mapbox styles.
metadata:
  tags: map, map animation, mapbox, turf, geojson, route animation
---

Use Mapbox GL JS for rendering maps in Remotion when the user wants Mapbox styles or higher-fidelity map visuals and has a Mapbox access token. Use Turf for geospatial operations such as great-circle routes, distances, slicing lines, and positions along routes.

Use this technique only when the user has a Mapbox access token and wants Mapbox styles or data.

## Core rules

- Prefer `@turf/turf` for geospatial work. Do not hand-roll distance, great-circle, route slicing, or coordinate interpolation unless the user explicitly needs a custom non-geodesic effect.
- Use GeoJSON sources and Mapbox layers for lines, markers, and labels. Avoid DOM `Marker` elements unless the user specifically asks for HTML markers.
- Keep the live map camera static by default. Before moving it on every frame, read [moving-map stability](references/render-stability.md). Prefer a fixed map plate for satellite imagery, hillshade, or a modest 2D reframe.
- Use a live per-frame camera only after rendering a short MP4 and checking for shimmer. This 2D technique does not provide genuine terrain, pitch, bearing, or banking.
- Disable non-deterministic map behavior: `interactive: false`, `fadeDuration: 0`.
- Drive animation from `useCurrentFrame()`; do not use CSS transitions or browser-timed animation.
- Use `delayRender()` / `continueRender()` around map loading and per-frame map updates.
- Set `preserveDrawingBuffer: true` and render WebGL with `bunx remotion ... --gl=angle`.
- Before continuing the initial render, add sources/layers, apply the frame-0 camera with `jumpTo()` or `setFreeCameraOptions()`, then wait for `idle`.
- Do not add a `mapInstance.remove()` cleanup function; it can interfere with Remotion's render lifecycle.
- Use Mapbox style URLs such as `mapbox://styles/mapbox/standard` or a user-provided custom style.
- Do not install `@types/mapbox-gl`; Mapbox GL JS ships its own types.
- Keep required provider attribution visible and verify current provider terms before rendering.
- Record the source and effective date of custom or disputed geography.
- Inspect rendered pixels, not only Studio playback, at every required aspect ratio.

Coordinates in Mapbox, Turf, and GeoJSON are `[longitude, latitude]`.

```ts
const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];
```

## Prerequisites

Install Mapbox GL JS and Turf with the project's package manager.

```bash
npm i mapbox-gl @turf/turf
```

```bash
bun i mapbox-gl @turf/turf
```

```bash
yarn add mapbox-gl @turf/turf
```

```bash
pnpm i mapbox-gl @turf/turf
```

Import the Mapbox CSS once in the component or an app-level stylesheet:

```ts
import 'mapbox-gl/dist/mapbox-gl.css';
```

Mapbox requires a public access token. Prefer passing it as an input prop or reading it from an environment variable that is available to the bundled Remotion code.

```ts
const mapboxAccessToken = process.env.REMOTION_MAPBOX_TOKEN;

if (!mapboxAccessToken) {
	throw new Error('Set REMOTION_MAPBOX_TOKEN to render Mapbox maps.');
}
```

## Basic map example

```tsx
import {useEffect, useRef, useState} from 'react';
import {useDelayRender, useVideoConfig} from 'remotion';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];

const mapboxAccessToken = process.env.REMOTION_MAPBOX_TOKEN;

if (!mapboxAccessToken) {
	throw new Error('Set REMOTION_MAPBOX_TOKEN to render Mapbox maps.');
}

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const {delayRender, continueRender} = useDelayRender();
	const {width, height} = useVideoConfig();
	const [loadingHandle] = useState(() => delayRender('Loading Mapbox map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		const mapInstance = new mapboxgl.Map({
			accessToken: mapboxAccessToken,
			container: containerRef.current,
			style: 'mapbox://styles/mapbox/standard',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.jumpTo({center: zurich, zoom: 7});
			mapInstance.once('idle', () => {
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	return (
		<>
			<div ref={containerRef} style={{width, height, position: 'absolute'}} />
		</>
	);
};
```

Animated examples should keep the loaded map in React state and skip per-frame updates until that state is set.

## Animated flight route example

This example shows the recommended pattern for route animations:

- Turf creates the route and markers.
- Turf slices the route for line reveal animation.
- Mapbox renders the route with GeoJSON sources and layers.
- The camera uses `jumpTo()` with animated center, zoom, bearing, and pitch.
- Frame 0 is prepared before `continueRender()`.

```tsx
import * as turf from '@turf/turf';
import {useEffect, useRef, useState} from 'react';
import {
	AbsoluteFill,
	Easing,
	interpolate,
	useCurrentFrame,
	useDelayRender,
	useVideoConfig,
} from 'remotion';
import mapboxgl, {type GeoJSONSource, type Map} from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];

const mapboxAccessToken = process.env.REMOTION_MAPBOX_TOKEN;

if (!mapboxAccessToken) {
	throw new Error('Set REMOTION_MAPBOX_TOKEN to render Mapbox maps.');
}

const greatCircleLine = (from: [number, number], to: [number, number]) => {
	const route = turf.greatCircle(from, to, {npoints: 100});

	if (route.geometry.type === 'LineString') {
		return turf.lineString(route.geometry.coordinates);
	}

	// Great-circle routes crossing the antimeridian can become MultiLineString.
	// Keep the example valid by choosing the longest segment.
	const longestSegment = route.geometry.coordinates.reduce((longest, segment) => {
		return segment.length > longest.length ? segment : longest;
	});

	return turf.lineString(longestSegment);
};

const targetRoute = greatCircleLine(zurich, newYork);
const targetRouteDistance = turf.length(targetRoute);

const cityMarkers = turf.featureCollection([
	turf.point(zurich, {name: 'Zurich'}),
	turf.point(newYork, {name: 'New York'}),
]);

const clampProgress = (progress: number) => Math.min(1, Math.max(0, progress));

const distanceAlong = (totalDistance: number, progress: number) => {
	// Keep the route non-empty at progress 0; Turf can error on zero-length slices.
	return Math.max(0.001, totalDistance * clampProgress(progress));
};

const getPartialTargetRoute = (progress: number) => {
	return turf.lineSliceAlong(
		targetRoute,
		0,
		distanceAlong(targetRouteDistance, progress),
	);
};

const getCameraOptions = (progress: number) => {
	const target = turf.along(
		targetRoute,
		distanceAlong(targetRouteDistance, progress),
	).geometry.coordinates as [number, number];

	return {
		center: target,
		zoom: interpolate(progress, [0, 0.5, 1], [7, 2.4, 8], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		}),
		bearing: interpolate(progress, [0, 1], [-20, 35], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
		}),
		pitch: interpolate(progress, [0, 0.25, 0.75, 1], [25, 55, 55, 30], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		}),
	};
};

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const frame = useCurrentFrame();
	const {delayRender, continueRender} = useDelayRender();
	const {durationInFrames, height, width} = useVideoConfig();
	const [map, setMap] = useState<Map | null>(null);
	const [loadingHandle] = useState(() => delayRender('Loading Mapbox map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		const mapInstance = new mapboxgl.Map({
			accessToken: mapboxAccessToken,
			container: containerRef.current,
			style: 'mapbox://styles/mapbox/standard',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.addSource('trace', {
				type: 'geojson',
				data: getPartialTargetRoute(0),
			});

			mapInstance.addLayer({
				id: 'trace-line',
				type: 'line',
				source: 'trace',
				layout: {
					'line-cap': 'round',
					'line-join': 'round',
				},
				paint: {
					'line-color': '#111111',
					'line-width': 7,
				},
			});

			mapInstance.addSource('city-markers', {
				type: 'geojson',
				data: cityMarkers,
			});

			mapInstance.addLayer({
				id: 'city-marker-dots',
				type: 'circle',
				source: 'city-markers',
				paint: {
					'circle-color': '#f03b20',
					'circle-radius': 12,
					'circle-stroke-color': '#ffffff',
					'circle-stroke-width': 4,
				},
			});

			mapInstance.addLayer({
				id: 'city-marker-labels',
				type: 'symbol',
				source: 'city-markers',
				layout: {
					'text-allow-overlap': true,
					'text-anchor': 'top',
					'text-field': ['get', 'name'],
					'text-offset': [0, 0.9],
					'text-size': 28,
				},
				paint: {
					'text-color': '#111111',
					'text-halo-color': '#ffffff',
					'text-halo-width': 3,
				},
			});

			mapInstance.jumpTo(getCameraOptions(0));
			mapInstance.once('idle', () => {
				setMap(mapInstance);
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	useEffect(() => {
		if (!map) {
			return;
		}

		const handle = delayRender('Rendering Mapbox frame');
		const timelineProgress = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
		});
		const travelProgress = interpolate(timelineProgress, [0.2, 0.82], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		});
		const trace = map.getSource('trace') as GeoJSONSource | undefined;

		trace?.setData(getPartialTargetRoute(travelProgress));
		map.jumpTo(getCameraOptions(travelProgress));

		map.once('idle', () => continueRender(handle));
		// Force an idle event even if the camera parameters are unchanged from the previous frame.
		map.triggerRepaint();
	}, [continueRender, delayRender, durationInFrames, frame, map]);

	return (
		<AbsoluteFill style={{backgroundColor: '#e8eef3'}}>
			<div ref={containerRef} style={{height, position: 'absolute', width}} />
		</AbsoluteFill>
	);
};
```

## Camera guidance

For a validated live-camera route animation, animate `center`, `zoom`, `bearing`, and `pitch` with `jumpTo()`:

```ts
map.jumpTo({
	center,
	zoom,
	bearing,
	pitch,
});
```

Keep route progress and camera progress separate if the camera needs to lead, lag, zoom out, or zoom back in. For cinematic 3D camera moves, load the 3D flyover branch from the parent skill.

## Lines

Use GeoJSON sources for lines. Unless the user asks, do not add glow effects or extra decorative points.

For geodesic flight routes, use Turf:

```ts
const line = greatCircleLine(start, end);
const distance = turf.length(line);
const partialLine = turf.lineSliceAlong(
	line,
	0,
	// Keep the route non-empty at progress 0.
	Math.max(0.001, distance * progress),
);
```

For a visually straight line on the map, use a simple GeoJSON `LineString` between the two points instead of `greatCircle()`.

## Markers and labels

Use map-native GeoJSON layers for markers and labels:

```tsx
mapInstance.addSource('markers', {
	type: 'geojson',
	data: turf.featureCollection([
		turf.point([-118.2437, 34.0522], {name: 'Los Angeles'}),
	]),
});

mapInstance.addLayer({
	id: 'marker-dots',
	type: 'circle',
	source: 'markers',
	paint: {
		'circle-color': '#f03b20',
		'circle-radius': 12,
		'circle-stroke-color': '#ffffff',
		'circle-stroke-width': 4,
	},
});

mapInstance.addLayer({
	id: 'marker-labels',
	type: 'symbol',
	source: 'markers',
	layout: {
		'text-allow-overlap': true,
		'text-anchor': 'top',
		'text-field': ['get', 'name'],
		'text-offset': [0, 0.9],
		'text-size': 28,
	},
	paint: {
		'text-color': '#111111',
		'text-halo-color': '#ffffff',
		'text-halo-width': 3,
	},
});
```

Make marker sizes and label font sizes large enough for the composition resolution.

## Styles

Default to Mapbox Standard:

```ts
style: 'mapbox://styles/mapbox/standard'
```

If the user requests another style, use any valid Mapbox style URL.

## Rendering

For WebGL map renders, prefer single concurrency and ANGLE:

```bash
bunx remotion render [composition-id] out/video.mp4 --gl=angle --concurrency=1
```

Use the equivalent package runner for the project. In npm projects, use `npx`; in Bun projects, use `bunx`.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/mapbox/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/mapbox/references/render-stability.md ===== -->

# Moving Map Render Stability

Read this reference before building a moving 2D MapTiler scene or diagnosing a wavering Remotion render.

## Symptom and cause

If basemap detail shimmers or jitters during a pan/zoom, the likely cause is per-frame `map.jumpTo()`.
Headless MapTiler capture can resample both vector hillshade and satellite imagery differently frame to
frame. Tile retries, easing changes, and label changes do not solve that renderer effect.

## Required pattern: fixed map plate

For any 2D pan/zoom:

1. Render the MapTiler canvas once at the largest required zoom in an oversized container. Size it from the camera route and keep each dimension below the browser's reliable WebGL render-buffer limit (commonly 4096 px). Do **not** blindly use 3×: a 1920×1080 composition becomes 5760 px wide and Chromium may silently downsample it, causing visible pixelation during the CSS zoom.
2. Keep the map's camera static.
3. For each frame, calculate the approved target centre/zoom, then move the canvas with CSS `translate` + `scale`.
4. Apply the same transform to every projected HTML overlay.
5. Continue to animate GeoJSON data and paint properties imperatively; only the renderer camera is frozen.

Keep pitch and bearing constant. Use a 3D engine such as Cesium for genuine changing pitch/bearing or a terrain flythrough.

```ts
const baseZoom = Math.max(start.zoom, end.zoom);
const map = new maptilersdk.Map({
  container,
  style,
  center: end.center,
  zoom: baseZoom,
  pitch: end.pitch ?? 0,
  bearing: end.bearing ?? 0,
  interactive: false,
  fadeDuration: 0,
  canvasContextAttributes: {preserveDrawingBuffer: true},
});

// Per Remotion frame. `camera` is the approved centre/zoom interpolation.
const projected = map.project(camera.center);
const scale = 2 ** (camera.zoom - baseZoom);
const plate = {
  transform: `translate(${width / 2 - projected.x * scale}px, ${height / 2 - projected.y * scale}px) scale(${scale})`,
  transformOrigin: "0 0",
};

// Convert label projection with exactly the same plate transform.
const labelX = labelPoint.x * scale + width / 2 - projected.x * scale;
const labelY = labelPoint.y * scale + height / 2 - projected.y * scale;
```

### Plate sizing and sharpness

- Render at the maximum zoom reached by **any** camera waypoint, including intermediate or hold cameras. The CSS scale should never exceed `1`; otherwise the plate is being enlarged.
- Centre the frozen map on the midpoint of the camera route's geographic extent, not automatically on the final camera. This minimizes required overscan.
- Keep the largest canvas dimension at or below 4096 px unless the actual render environment has been tested with a larger `MAX_RENDERBUFFER_SIZE`.
- For 1920×1080, a 3840×2160 plate is a safe default. For 1080×1920, use approximately 2700×3840 when the route needs extra horizontal pan room.
- If the route cannot fit within that plate at the required zoom, split the shot into two fixed plates with a deliberate editorial transition. Do not trade sharpness for one enormous canvas.
- Distinguish failure modes: repeating shimmer means the live renderer is moving; steadily soft tiles during a CSS push means the fixed plate is underspecified, internally downsampled, or being scaled above `1`.

## Verification

- Render a short MP4, not only a Studio preview.
- Inspect static terrain texture and satellite detail while the camera moves.
- If any underlying map detail wavers, use the fixed map plate. Do not approve it as a minor preview artefact.
- Render WebGL with `--gl=angle`, `preserveDrawingBuffer:true`, and conservative concurrency (`1`) while validating.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/mapbox/references/render-stability.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maplibre/TECHNIQUE.md ===== -->

---
name: maps-maplibre
description: Make deterministic Remotion 2D map animations with MapLibre GL JS and Turf. Use when the user chooses MapLibre for animated routes, map markers, labels, and camera movement.
metadata:
  tags: map, map animation, maplibre, turf, geojson, route animation
---

Use MapLibre GL JS for rendering maps in Remotion. Use Turf for geospatial operations such as great-circle routes, distances, slicing lines, and positions along routes.

## Core rules

- Prefer `@turf/turf` for geospatial work. Do not hand-roll distance, great-circle, route slicing, or coordinate interpolation unless the user explicitly needs a custom non-geodesic effect.
- Use GeoJSON sources and MapLibre layers for lines, markers, and labels. Avoid DOM `Marker` elements unless the user specifically asks for HTML markers.
- Keep the live map camera static by default. Before moving it on every frame, read [moving-map stability](references/render-stability.md). Prefer a fixed map plate for satellite imagery, hillshade, or a modest 2D reframe.
- Use a live per-frame camera only after rendering a short MP4 and checking for shimmer. This 2D technique does not provide genuine terrain, pitch, bearing, or banking.
- Disable non-deterministic map behavior: `interactive: false`, `fadeDuration: 0`.
- Drive animation from `useCurrentFrame()`; do not use CSS transitions or browser-timed animation.
- Use `delayRender()` / `continueRender()` around map loading and per-frame map updates.
- Set `preserveDrawingBuffer: true` and render WebGL with `bunx remotion ... --gl=angle`.
- Before continuing the initial render, add sources/layers, apply the frame-0 camera with `jumpTo()`, then wait for `idle`.
- Do not add a `mapInstance.remove()` cleanup function; it can interfere with Remotion's render lifecycle.
- Use standard MapLibre style JSON URLs and layer/source APIs.
- Do not install `@types/maplibre-gl`; MapLibre ships its own types.
- Keep required provider attribution visible and verify the current terms of the chosen style and tile providers before rendering.
- Record the source and effective date of custom or disputed geography.
- Inspect rendered pixels, not only Studio playback, at every required aspect ratio.

Coordinates in MapLibre, Turf, and GeoJSON are `[longitude, latitude]`.

```ts
const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];
```

## Prerequisites

Install MapLibre and Turf with the project's package manager.

```bash
npm i maplibre-gl @turf/turf
```

```bash
bun i maplibre-gl @turf/turf
```

```bash
yarn add maplibre-gl @turf/turf
```

```bash
pnpm i maplibre-gl @turf/turf
```

Import the MapLibre CSS once in the component or an app-level stylesheet:

```ts
import 'maplibre-gl/dist/maplibre-gl.css';
```

## Basic map example

```tsx
import {useEffect, useRef, useState} from 'react';
import {useDelayRender, useVideoConfig} from 'remotion';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const {delayRender, continueRender} = useDelayRender();
	const {width, height} = useVideoConfig();
	const [loadingHandle] = useState(() => delayRender('Loading map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		maplibregl.setWorkerUrl(
			URL.createObjectURL(
				new Blob(
					[`import "https://unpkg.com/maplibre-gl@${maplibregl.getVersion()}/dist/maplibre-gl-worker.mjs";`],
					{type: 'text/javascript'},
				),
			),
		);

		const mapInstance = new maplibregl.Map({
			container: containerRef.current,
			style: 'https://demotiles.maplibre.org/style.json',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.jumpTo({center: zurich, zoom: 7});
			mapInstance.once('idle', () => {
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	return (
		<>
			<div ref={containerRef} style={{width, height, position: 'absolute'}} />
		</>
	);
};
```

Animated examples should keep the loaded map in React state and skip per-frame updates until that state is set.

## Animated flight route example

This example shows the recommended pattern for route animations:

- Turf creates the route and markers.
- Turf slices the route for line reveal animation.
- The camera has a separate route from the target route.
- MapLibre's `calculateCameraOptionsFromTo()` is used for camera movement.
- Frame 0 is prepared before `continueRender()`.

```tsx
import * as turf from '@turf/turf';
import {useEffect, useRef, useState} from 'react';
import {
	AbsoluteFill,
	Easing,
	interpolate,
	useCurrentFrame,
	useDelayRender,
	useVideoConfig,
} from 'remotion';
import * as maplibregl from 'maplibre-gl';
import {type GeoJSONSource, type Map} from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const zurich: [number, number] = [8.5417, 47.3769];
const newYork: [number, number] = [-74.006, 40.7128];

const greatCircleLine = (from: [number, number], to: [number, number]) => {
	const route = turf.greatCircle(from, to, {npoints: 100});

	if (route.geometry.type === 'LineString') {
		return turf.lineString(route.geometry.coordinates);
	}

	// Great-circle routes crossing the antimeridian can become MultiLineString.
	// Keep the example valid by choosing the longest segment.
	const longestSegment = route.geometry.coordinates.reduce((longest, segment) => {
		return segment.length > longest.length ? segment : longest;
	});

	return turf.lineString(longestSegment);
};

const targetRoute = greatCircleLine(zurich, newYork);
const targetRouteDistance = turf.length(targetRoute);

const cameraRoute = greatCircleLine(zurich, newYork);
const cameraRouteDistance = turf.length(cameraRoute);

const cityMarkers = turf.featureCollection([
	turf.point(zurich, {name: 'Zurich'}),
	turf.point(newYork, {name: 'New York'}),
]);

const clampProgress = (progress: number) => Math.min(1, Math.max(0, progress));

const distanceAlong = (totalDistance: number, progress: number) => {
	// Keep the route non-empty at progress 0; Turf can error on zero-length slices.
	return Math.max(0.001, totalDistance * clampProgress(progress));
};

const getPartialTargetRoute = (progress: number) => {
	return turf.lineSliceAlong(
		targetRoute,
		0,
		distanceAlong(targetRouteDistance, progress),
	);
};

const getCameraOptions = (
	map: Map,
	progress: number,
	cameraAltitudeMeters: number,
	cameraLatitudeOffset: number,
) => {
	const target = turf.along(
		targetRoute,
		distanceAlong(targetRouteDistance, progress),
	).geometry.coordinates;
	const camera = turf.along(
		cameraRoute,
		distanceAlong(cameraRouteDistance, progress),
	).geometry.coordinates;

	return map.calculateCameraOptionsFromTo(
		new maplibregl.LngLat(camera[0], camera[1] - cameraLatitudeOffset),
		cameraAltitudeMeters,
		new maplibregl.LngLat(target[0], target[1]),
	);
};

export const MyComposition = () => {
	const containerRef = useRef<HTMLDivElement>(null);
	const frame = useCurrentFrame();
	const {delayRender, continueRender} = useDelayRender();
	const {durationInFrames, height, width} = useVideoConfig();
	const [map, setMap] = useState<Map | null>(null);
	const [loadingHandle] = useState(() => delayRender('Loading MapLibre map'));

	useEffect(() => {
		if (!containerRef.current) {
			return;
		}

		maplibregl.setWorkerUrl(
			URL.createObjectURL(
				new Blob(
					[`import "https://unpkg.com/maplibre-gl@${maplibregl.getVersion()}/dist/maplibre-gl-worker.mjs";`],
					{type: 'text/javascript'},
				),
			),
		);

		const mapInstance = new maplibregl.Map({
			container: containerRef.current,
			style: 'https://demotiles.maplibre.org/style.json',
			center: zurich,
			zoom: 7,
			interactive: false,
			attributionControl: false,
			fadeDuration: 0,
			canvasContextAttributes: {
				preserveDrawingBuffer: true,
			},
		});

		mapInstance.on('load', () => {
			mapInstance.addSource('trace', {
				type: 'geojson',
				data: getPartialTargetRoute(0),
			});

			mapInstance.addLayer({
				id: 'trace-line',
				type: 'line',
				source: 'trace',
				layout: {
					'line-cap': 'round',
					'line-join': 'round',
				},
				paint: {
					'line-color': '#111111',
					'line-width': 7,
				},
			});

			mapInstance.addSource('city-markers', {
				type: 'geojson',
				data: cityMarkers,
			});

			mapInstance.addLayer({
				id: 'city-marker-dots',
				type: 'circle',
				source: 'city-markers',
				paint: {
					'circle-color': '#f03b20',
					'circle-radius': 12,
					'circle-stroke-color': '#ffffff',
					'circle-stroke-width': 4,
				},
			});

			mapInstance.addLayer({
				id: 'city-marker-labels',
				type: 'symbol',
				source: 'city-markers',
				layout: {
					'text-allow-overlap': true,
					'text-anchor': 'top',
					'text-field': ['get', 'name'],
					'text-offset': [0, 0.9],
					'text-size': 28,
				},
				paint: {
					'text-color': '#111111',
					'text-halo-color': '#ffffff',
					'text-halo-width': 3,
				},
			});

			mapInstance.jumpTo(getCameraOptions(mapInstance, 0, 180000, 1.1));
			mapInstance.once('idle', () => {
				setMap(mapInstance);
				continueRender(loadingHandle);
			});
		});
	}, [continueRender, loadingHandle]);

	useEffect(() => {
		if (!map) {
			return;
		}

		const handle = delayRender('Rendering MapLibre frame');
		const timelineProgress = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
		});
		const travelProgress = interpolate(timelineProgress, [0.2, 0.82], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: Easing.bezier(0.645, 0.045, 0.355, 1),
		});
		const cameraAltitudeMeters = interpolate(
			timelineProgress,
			[0, 0.28, 0.74, 1],
			[180000, 2200000, 2200000, 180000],
			{
				extrapolateLeft: 'clamp',
				extrapolateRight: 'clamp',
				easing: Easing.bezier(0.645, 0.045, 0.355, 1),
			},
		);
		const cameraLatitudeOffset = interpolate(
			timelineProgress,
			[0, 0.28, 0.74, 1],
			[1.1, 8, 8, 1.1],
			{
				extrapolateLeft: 'clamp',
				extrapolateRight: 'clamp',
				easing: Easing.bezier(0.645, 0.045, 0.355, 1),
			},
		);
		const trace = map.getSource('trace') as GeoJSONSource | undefined;

		trace?.setData(getPartialTargetRoute(travelProgress));
		map.jumpTo(
			getCameraOptions(
				map,
				travelProgress,
				cameraAltitudeMeters,
				cameraLatitudeOffset,
			),
		);

		map.once('idle', () => continueRender(handle));
		// Force an idle event even if the camera parameters are unchanged from the previous frame.
		map.triggerRepaint();
	}, [continueRender, delayRender, durationInFrames, frame, map]);

	return (
		<AbsoluteFill style={{backgroundColor: '#e8eef3'}}>
			<div ref={containerRef} style={{height, position: 'absolute', width}} />
		</AbsoluteFill>
	);
};
```

## Camera guidance

Use MapLibre's camera helper for camera movement:

```ts
map.calculateCameraOptionsFromTo(cameraLngLat, cameraAltitudeMeters, targetLngLat);
```

A good pattern is to keep two concepts separate:

- `targetRoute`: where the animated line is and where the camera looks.
- `cameraRoute`: where the camera moves.

Then use Turf to read positions from both routes for the same progress value:

```ts
const target = turf.along(targetRoute, targetDistance * progress).geometry.coordinates;
const camera = turf.along(cameraRoute, cameraDistance * progress).geometry.coordinates;

map.jumpTo(
	map.calculateCameraOptionsFromTo(
		new maplibregl.LngLat(camera[0], camera[1]),
		cameraAltitudeMeters,
		new maplibregl.LngLat(target[0], target[1]),
	),
);
```

For zoom-out / travel / zoom-in animations, animate travel progress separately from camera altitude. Camera altitude is measured in meters. This avoids heavy custom camera math.

## Lines

Use GeoJSON sources for lines. Unless the user asks, do not add glow effects or extra decorative points.

For geodesic flight routes, use Turf:

```ts
const line = greatCircleLine(start, end);
const distance = turf.length(line);
const partialLine = turf.lineSliceAlong(
	line,
	0,
	// Keep the route non-empty at progress 0.
	Math.max(0.001, distance * progress),
);
```

For a visually straight line on the map, use a simple GeoJSON `LineString` between the two points instead of `greatCircle()`.

## Markers and labels

Use map-native GeoJSON layers for markers and labels:

```tsx
mapInstance.addSource('markers', {
	type: 'geojson',
	data: turf.featureCollection([
		turf.point([-118.2437, 34.0522], {name: 'Los Angeles'}),
	]),
});

mapInstance.addLayer({
	id: 'marker-dots',
	type: 'circle',
	source: 'markers',
	paint: {
		'circle-color': '#f03b20',
		'circle-radius': 12,
		'circle-stroke-color': '#ffffff',
		'circle-stroke-width': 4,
	},
});

mapInstance.addLayer({
	id: 'marker-labels',
	type: 'symbol',
	source: 'markers',
	layout: {
		'text-allow-overlap': true,
		'text-anchor': 'top',
		'text-field': ['get', 'name'],
		'text-offset': [0, 0.9],
		'text-size': 28,
	},
	paint: {
		'text-color': '#111111',
		'text-halo-color': '#ffffff',
		'text-halo-width': 3,
	},
});
```

Make marker sizes and label font sizes large enough for the composition resolution.

## Styles

Default to the stock MapLibre demo style:

```ts
style: 'https://demotiles.maplibre.org/style.json'
```

If the user requests another style, use any valid MapLibre style JSON URL.

## Rendering

For WebGL map renders, prefer single concurrency and ANGLE:

```bash
bunx remotion render [composition-id] out/video.mp4 --gl=angle --concurrency=1
```

Use the equivalent package runner for the project. In npm projects, use `npx`; in Bun projects, use `bunx`.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maplibre/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maplibre/references/render-stability.md ===== -->

# Moving Map Render Stability

Read this reference before building a moving 2D MapTiler scene or diagnosing a wavering Remotion render.

## Symptom and cause

If basemap detail shimmers or jitters during a pan/zoom, the likely cause is per-frame `map.jumpTo()`.
Headless MapTiler capture can resample both vector hillshade and satellite imagery differently frame to
frame. Tile retries, easing changes, and label changes do not solve that renderer effect.

## Required pattern: fixed map plate

For any 2D pan/zoom:

1. Render the MapTiler canvas once at the largest required zoom in an oversized container. Size it from the camera route and keep each dimension below the browser's reliable WebGL render-buffer limit (commonly 4096 px). Do **not** blindly use 3×: a 1920×1080 composition becomes 5760 px wide and Chromium may silently downsample it, causing visible pixelation during the CSS zoom.
2. Keep the map's camera static.
3. For each frame, calculate the approved target centre/zoom, then move the canvas with CSS `translate` + `scale`.
4. Apply the same transform to every projected HTML overlay.
5. Continue to animate GeoJSON data and paint properties imperatively; only the renderer camera is frozen.

Keep pitch and bearing constant. Use a 3D engine such as Cesium for genuine changing pitch/bearing or a terrain flythrough.

```ts
const baseZoom = Math.max(start.zoom, end.zoom);
const map = new maptilersdk.Map({
  container,
  style,
  center: end.center,
  zoom: baseZoom,
  pitch: end.pitch ?? 0,
  bearing: end.bearing ?? 0,
  interactive: false,
  fadeDuration: 0,
  canvasContextAttributes: {preserveDrawingBuffer: true},
});

// Per Remotion frame. `camera` is the approved centre/zoom interpolation.
const projected = map.project(camera.center);
const scale = 2 ** (camera.zoom - baseZoom);
const plate = {
  transform: `translate(${width / 2 - projected.x * scale}px, ${height / 2 - projected.y * scale}px) scale(${scale})`,
  transformOrigin: "0 0",
};

// Convert label projection with exactly the same plate transform.
const labelX = labelPoint.x * scale + width / 2 - projected.x * scale;
const labelY = labelPoint.y * scale + height / 2 - projected.y * scale;
```

### Plate sizing and sharpness

- Render at the maximum zoom reached by **any** camera waypoint, including intermediate or hold cameras. The CSS scale should never exceed `1`; otherwise the plate is being enlarged.
- Centre the frozen map on the midpoint of the camera route's geographic extent, not automatically on the final camera. This minimizes required overscan.
- Keep the largest canvas dimension at or below 4096 px unless the actual render environment has been tested with a larger `MAX_RENDERBUFFER_SIZE`.
- For 1920×1080, a 3840×2160 plate is a safe default. For 1080×1920, use approximately 2700×3840 when the route needs extra horizontal pan room.
- If the route cannot fit within that plate at the required zoom, split the shot into two fixed plates with a deliberate editorial transition. Do not trade sharpness for one enormous canvas.
- Distinguish failure modes: repeating shimmer means the live renderer is moving; steadily soft tiles during a CSS push means the fixed plate is underspecified, internally downsampled, or being scaled above `1`.

## Verification

- Render a short MP4, not only a Studio preview.
- Inspect static terrain texture and satellite detail while the camera moves.
- If any underlying map detail wavers, use the fixed map plate. Do not approve it as a minor preview artefact.
- Render WebGL with `--gl=angle`, `preserveDrawingBuffer:true`, and conservative concurrency (`1`) while validating.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maplibre/references/render-stability.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/TECHNIQUE.md ===== -->

# MapTiler maps in Remotion

MapTiler is a good solution for map animations where geographics features should be drawn as annotations on top of the map: Country borders, rivers, labels for POIs.

## MapTiler SDK (`@maptiler/sdk`)

Draw the basemap plus MapTiler Planet vector layers and custom GeoJSON into a WebGL canvas. Default styled-vector starting point: `MapStyle.BASIC`; satellite is an equally valid choice.

## Remotion

Imperatively update `setData`/`setPaintProperty`.

Use `jumpTo` only for a static shot, or a fixed map plate for any pan/zoom.
Gate with [`delayRender`](https://www.remotion.dev/docs/delay-render.md) until `map.once('idle')`.

Use `preserveDrawingBuffer:true`.

Render labels as positioned [`<Interactive.Div>`](https://www.remotion.dev/docs/interactive.md) elements.

Env `REMOTION_MAPTILER_KEY` (unrestricted). Init the map once (ref guard); update imperatively per frame.

When constructing MapLibre/MapTiler layer objects, omit optional properties that are absent.  
In particular, use `...(layer.filter ? {filter: layer.filter} : {})`; do not pass `filter: undefined`. An undefined filter can suppress the layer while separately created halo or border layers continue rendering, producing missing country fills and dark marker halos with no coloured cores.

Drive animation from `useCurrentFrame()` rather than CSS transitions or browser timers.  

## Choose the source for each map element

Do not begin by manufacturing GeoJSON. First check whether MapTiler Planet already exposes the element as filtered vector data.

### MapTiler vector

Use it when the feature exists in a provider `source-layer`, its attributes support an exact filter, and provider geometry is editorially acceptable.

### Hybrid

Use it when ordinary geographic context can come from MapTiler while the claim depends on custom
evidence.

Animate each layer according to its source and meaning.

MapTiler vector features remain split across tiles. Do not use them for a semantic start-to-end line draw; extract, verify, order, and bake that element to GeoJSON first. Read **`references/map-data-sources.md`** and reuse **`assets/MapTilerVectorElement.ts`** for provider-layer setup and per-frame paint updates.

## Motion stability

**Do not call `map.jumpTo()` on every Remotion frame when the camera moves.** In headless capture it can make both MapTiler hillshade **and satellite imagery** shimmer/jitter, even when the source tiles load correctly. This is renderer resampling, not a data, network, or label problem.

For the implementation, read **`references/render-stability.md`** before building or debugging any moving map. It contains the fixed-map-plate recipe, diagnostics, and render checks.

- Use the live MapTiler camera only for a static shot.
- Keep pitch and bearing constant for a fixed plate. This technique does not implement a genuine changing 3D camera.
- Verify the moving preview and a short rendered MP4 before approving a beat. If any basemap detail wavers, switch to the fixed-plate pattern; do not try to solve it with tile retries or camera easing.

## Drawing rivers

Use `turf.lineSliceAlong(line, 0, lineKm*reveal)` to draw rivers.

## Source selection

Use MapTiler vector layers for suitable provider features and custom GeoJSON for story-specific or ordered geometry. If the beat needs country-entry triggers or a progressive line draw, run `scripts/prep-geo.mjs` to bake `country-meta.json`, `borders.geojson`, and the ordered line. Details → `references/map-data-sources.md` and `references/map-geo-prep.md`.

## Keep it minmal

Strip clutter on `load`: remove `symbol` layers (place labels) and `/other border/i` (admin-1 inner borders); hide the logo via CSS. Keep country + disputed borders.

## Files

Use as reference:

- `assets/RiverReveal.tsx` — the main component.
- `assets/MapTilerVectorElement.ts` — filtered MapTiler Planet elements.
- `assets/CountryLabel.tsx` — reusable example label.
- `assets/tokens.ts` — example palette and durations.
- `assets/example-Root.tsx` — minimal composition scaffold.
- `assets/sample-data/` — example route and generated country metadata.
- `scripts/prep-geo.mjs` — geo pipeline.
- `references/map-explainer-architecture.md` — timing model and implementation.
- `references/map-data-sources.md` — provider vector versus custom GeoJSON selection.
- `references/map-geo-prep.md` — basemap stripping and geo preparation.
- `references/render-stability.md` — camera motion and stable headless renders.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-data-sources.md ===== -->

# Map element data sources

Choose the source independently for every story element. A single map can—and often should—mix
provider vectors with custom geodata.

## Decision rule

Use a MapTiler Planet vector layer when the feature already exists there, its attributes support an
editorially precise filter, and provider geometry is acceptable for the claim. Use custom GeoJSON when
the feature is absent, proposed, historical, disputed, corrected, privately sourced, or needs ordered
geometry for a deterministic draw.

| Requirement                                                                 | MapTiler vector layer | Custom GeoJSON                              |
| --------------------------------------------------------------------------- | --------------------- | ------------------------------------------- |
| Roads, waterways, water, boundaries, land cover, or other standard context  | Prefer                | Use only when provider data is insufficient |
| Basemap-consistent geometry without a duplicate local dataset               | Prefer                | No                                          |
| Proposed, historical, classified, corrected, or production-specific element | No                    | Prefer                                      |
| Fade, colour, width, radius, blur, or fill-opacity animation                | Yes                   | Yes                                         |
| Feature-state highlight when a stable feature ID exists                     | Yes                   | Yes                                         |
| Deterministic source-to-end line draw or perimeter draw                     | Bake first            | Prefer                                      |
| Geometry editing, morphing, clipping, or exact sequencing                   | No                    | Prefer                                      |

Provider alignment is not proof of correctness. Inspect the attributes and geometry against the
editorial source before presenting a provider feature as evidence.

## MapTiler vector mode

MapTiler Planet is a vector tile source. Add it once, then build story layers with a
`source-layer` and an exact attribute filter. Read the current MapTiler Planet schema before choosing
layer names or fields.

Common layer categories include `waterway`, `water`, `transportation`, `boundary`, `landcover`, and
`poi`; availability, fields, and zoom ranges vary by schema version.

```ts
import {addMapTilerVectorElement, setVectorElementPaint} from "./MapTilerVectorElement";

addMapTilerVectorElement(map, process.env.REMOTION_MAPTILER_KEY!, {
  id: "story-river",
  sourceLayer: "waterway",
  type: "line",
  filter: [
    "all",
    ["==", ["get", "class"], "river"],
    ["==", ["coalesce", ["get", "name_en"], ["get", "name"]], "Yarlung Tsangpo"],
  ],
  layout: {"line-cap": "round", "line-join": "round"},
  paint: {
    "line-color": "#E8F7FF",
    "line-width": 3,
    "line-opacity": 0,
  },
});

setVectorElementPaint(map, "story-river", {
  "line-opacity": reveal,
  "line-width": 2 + reveal * 2,
});
```

Animate provider features by changing paint properties from the Remotion frame: opacity, colour,
width, blur, fill opacity, circle radius, or symbol opacity. Use feature state only when the source
provides stable IDs and the selection remains deterministic across tiles.

Do not treat a tiled line as one ordered path. Vector tiles split features at tile boundaries, so a
source-to-mouth or start-to-end draw has no reliable global order. If that motion carries meaning,
extract and verify the complete feature, order it once, save it as GeoJSON, and use the custom mode.

## Custom geodata mode

Use the bundled `../assets/RiverReveal.tsx` and `../scripts/prep-geo.mjs` pattern for custom GeoJSON. This mode owns
the exact geometry and can slice it by distance, calculate entry triggers, draw complete borders, and
produce deterministic sequences.

Custom mode is mandatory when:

- the feature is not in the provider dataset;
- the story uses a proposed route, planned tunnel, historical boundary, disputed interpretation, or
  non-public dataset;
- provider geometry was editorially corrected;
- motion must travel through the geometry in a verified order;
- a complete off-screen boundary matters and a viewport query would silently crop it.

## Hybrid mode

Use provider vectors for ordinary contextual features and custom GeoJSON for the specific claim. For
example: MapTiler waterways and roads as aligned context; a custom proposed tunnel, dam site, disputed
boundary, or verified evacuation area as the highlighted evidence.

Keep provider and custom layers visually distinct when they carry different evidentiary weight. Record
the source and effective date of every custom layer in the production notes.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-data-sources.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-explainer-architecture.md ===== -->

# Map Explainer — architecture reference

Deep detail behind `TECHNIQUE.md`: the timing model, the river reveal + electric head, the per-country
sequence, and label projection. The supplied values are examples, not a production style system.
The custom-geometry example is `../assets/RiverReveal.tsx` +
`../assets/CountryLabel.tsx` +
`../assets/tokens.ts`. Provider-vector setup is in
`../assets/MapTilerVectorElement.ts`; choose between
the two modes with `data-sources.md`.

## 1. The render harness (per frame)

Init the MapTiler map once (ref guard). On `load`: strip clutter (see `geo-prep.md`), add sources/layers,
wait for `once('idle') → continueRender`. Per frame:

```
delayRender → setData/setPaintProperty → map.once('idle', continueRender) → triggerRepaint
```

`preserveDrawingBuffer:true` so Remotion's screenshot captures the canvas. Render `--gl=angle`.
For an animated camera, read `render-stability.md`: the MapTiler renderer remains static and a CSS plate
transform supplies the camera choreography.

## 2. Timing model — time-based; beat length derived from the sequences

Everything keys off **seconds** (`t = frame / fps`), not reveal-units. The river draws over a window;
each country **triggers when the river reaches it** and runs a fixed sequence. The beat is exactly as
long as the sequences need.

```ts
const RIVER_START = 0.3, RIVER_END = 8.0;            // river draws over this window
const BORDER_S = 2.5, FILL_S = 1.0, LABEL_S = 0.7;   // per-country sequence (constant durations)
const trigger = (c) => RIVER_START + META[c].stop * (RIVER_END - RIVER_START);  // river-arrival time
// beat length = max over c of (trigger(c) + BORDER_S + FILL_S + LABEL_S) + tail
const reveal = interpolate(t, [RIVER_START, RIVER_END], [0,1], { ...clamp, easing: Easing.bezier(0.645, 0.045, 0.355, 1) });
```

**Constant durations matter:** drive the border draw by _time since trigger_, not a slice of the reveal —
otherwise complex or long borders flash by in a fraction of a second.

## 3. Provider-vector animation

MapTiler Planet elements can be animated directly in place. Filter an exact `source-layer` feature,
initialize its paint in the hidden or neutral state, then update paint properties from the Remotion frame.
This works for line, fill, circle, and symbol layers without copying provider geometry into the project.

Do not assume tiled geometry has a global order. Provider features are split at tile boundaries: opacity,
colour, width, blur, radius, fill, and feature-state changes are reliable; semantic start-to-end line
draws are not. Bake ordered GeoJSON when the direction of the draw carries meaning.

## 4. Custom line animation — reveal + electric draw-head

The "electricity" is a **white-hot head** leading the draw — the last few % of the drawn line in its own
bright + glow layers, faded out once the river completes.

```ts
const riverDrawnKm = lineKm * reveal;
map.getSource("river").setData(turf.lineSliceAlong(line, 0, Math.max(0.001, riverDrawnKm)));
const headKm = lineKm * 0.03;
map.getSource("river-head").setData(turf.lineSliceAlong(line, Math.max(0, riverDrawnKm - headKm), Math.max(0.001, riverDrawnKm)));
let headFade = 0;
if (reveal > 0.002 && reveal < 0.999) headFade = 1;
else if (reveal >= 0.999) headFade = 1 - clamp01((t - RIVER_END) / 0.5);  // fade out at the mouth
map.setPaintProperty("river-headglow", "line-opacity", 0.85 * headFade);
map.setPaintProperty("river-head", "line-opacity", headFade);
```

Layers, bottom→top: `river-glow` (electric blue `#49C6FF`, w11, op0.32, blur6) → `river-line`
(icy core `#E8F7FF`, w3) → `river-headglow` (`rgba(120,225,255,.95)`, w16, blur9) → `river-head`
(white `#FFFFFF`, w4.5). **No dark casing** — the bright icy core reads over every fill on its own.

## 5. Country animation — border draws → fill blooms → label rises

Triggered by river arrival, each country runs three sequential phases. The border is a **darker shade**
of the country colour (the electricity is on the river, not here).

```ts
const lt = t - trigger(c);                                   // local seconds since trigger
// 1) complete source border draws on over a constant BORDER_S, multi-segment-safe
const bp = interpolate(clamp01(lt / BORDER_S), [0,1], [0,1], { easing: Easing.bezier(0.645, 0.045, 0.355, 1) });
map.getSource(`trail-${c}`).setData(sliceBorder(DRAW[c], 0, DRAW[c].total * bp));   // COUNTRY_DARK line
// 2) fill blooms in (opacity overshoots, then settles) after the border completes
const fp = clamp01((lt - BORDER_S) / FILL_S);
const fo = interpolate(fp, [0, 0.6, 1], [0, FILL_OPACITY * 1.25, FILL_OPACITY], { ...clamp, easing: Easing.bezier(0.3333333333333333, 1, 0.6666666666666666, 1) });
map.setPaintProperty(`fill-${c}`, "fill-opacity", fp <= 0 ? 0 : fo);
// 3) label rises in after the fill
const lp = clamp01((lt - BORDER_S - FILL_S) / LABEL_S);
```

`sliceBorder(d, fromKm, toKm)` reveals a portion of a complete (possibly multi-segment) border as a
MultiLineString, slicing each segment by cumulative length — no joins across gaps and no viewport crop:

```ts
const sliceBorder = (d, fromKm, toKm) => {
  const out = [];
  for (let i = 0; i < d.segLines.length; i++) {
    const start = d.cum[i], end = start + d.segLen[i];
    const a = Math.max(fromKm, start), b = Math.min(toKm, end);
    if (b - a <= 0.0008) continue;
    out.push(turf.lineSliceAlong(d.segLines[i], a - start, b - start).geometry.coordinates);
  }
  return { type:"Feature", properties:{}, geometry:{ type:"MultiLineString", coordinates: out } };
};
```

Choose fill, border, and river colours in the production's local token file. The bundled token values are
examples only; do not carry a source project's palette into another production.

## 6. Labels — HTML overlay, projected each frame

Labels are React, not map symbols (full typography control). `CountryLabel` is an example accent-rule,
rise-and-fade treatment; select the typeface and final values in the production.
Positioned by projecting the anchor to screen pixels **every frame**, stored in state:

```ts
const p = map.project(META[c].anchor);   // lngLat → screen px (respects the live camera)
pos[c] = { x: p.x, y: p.y, reveal: lp };
setLabels(pos);                          // re-render the overlay; effect deps exclude `labels`
```

`CountryLabel` shows the mechanics: uppercase region name, short accent divider, rise/fade entrance,
and `pointerEvents:none`. Select font, weight, size, spacing, contrast, and colour from the production's
own type and palette system.

## 7. Camera — fixed map plate for any movement

Read `render-stability.md`. Do not use per-frame `map.jumpTo()` for a moving 2D shot; it can shimmer in
headless renders even on satellite imagery. Interpolate the intended camera for the CSS plate transform,
while keeping the MapTiler renderer static.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-explainer-architecture.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-geo-prep.md ===== -->

# Map Explainer — basemap & geo prep

How the basemap is cleaned and how `../scripts/prep-geo.mjs` bakes the per-country data the component reads.

## Basemap styling — strip the clutter

On `load`, remove the basemap's labels and inner admin borders so only your geography reads:

```ts
for (const l of m.getStyle().layers as any[])
  if (l.type === "symbol" || /other border/i.test(l.id)) m.removeLayer(l.id);
```

- `type === "symbol"` → every place/water/road **label** (the "MapTiler labels"). Gone.
- Inner admin-border layer IDs vary by style. Inspect the loaded style, remove state/province/district
  layers as needed, and retain only the context borders the production requires.
- Logo/attribution: `maptilerLogo:false` + `attributionControl:false` aren't always enough — also hide
  via CSS in the component:
  ```tsx
  <style>
    {`
      .maplibregl-ctrl-bottom-left,
      .maplibregl-ctrl-bottom-right,
      .maplibregl-ctrl-attrib,
      .maptiler-logo {
        display: none !important;
      }
    `}
  </style>
  ```

## `../scripts/prep-geo.mjs` → outputs

Reads a routed river GeoJSON + country polygon GeoJSONs; writes:

- **River line** — simplified for a smooth draw. For a braided river, route one source→mouth path through
  the network first: greedy endpoint-chaining bounces between parallel channels. → `src/geo/river-flow.json`.
- **`public/geo/borders.geojson`** — each country's polygon tagged `{country: name}` (one source,
  filtered per country for the fills).
- **`src/geo/country-meta.json`** — per country `{ stop, anchor, border }`.

### `stop` — when a country lights up

Walk the river points; first point inside a country (`turf.booleanPointInPolygon`) = the arc-length
fraction where the river **enters** it. Drives the trigger time. The headwaters country = 0.

### `anchor` — label centre via pole of inaccessibility

The most-interior point of the country (clipped to a per-country **story bbox** so a big country
centres in the relevant region, not its far bulge), then a small operator **nudge**. Pole = grid-sample
inside the polygon, keep the point with max distance to the boundary. **Centroids get pulled to edges —
don't use them.**

```js
const pole = (poly) => {
  const bb = turf.bbox(poly), edge = turf.polygonToLine(poly), N = 46;
  let best = null, bestD = -1;
  for (let i = 0; i <= N; i++) for (let j = 0; j <= N; j++) {
    const p = turf.point([bb[0]+(bb[2]-bb[0])*i/N, bb[1]+(bb[3]-bb[1])*j/N]);
    if (!turf.booleanPointInPolygon(p, poly)) continue;
    const d = turf.pointToLineDistance(p, edge);
    if (d > bestD) { bestD = d; best = p.geometry.coordinates; }
  }
  return best;
};
const ANCHOR_BBOX = { china:[82,27,96,32], india:[76,14,99,31], bangladesh:[86,20,93,27] };  // story regions
const NUDGE = { china:[0,0.6], india:[-1.0,0], bangladesh:[0,-0.6] };                          // operator-directed
```

### `border` — complete source geometry

Preserve every exterior ring from the named country source. Never clip a country or bilateral border to
the framed bbox and never discard an off-screen segment: the geometry may leave the frame naturally.
The renderer handles a MultiLineString by cumulative length, so it remains one timed reveal without
inventing joins across gaps.

## Tuning the geo prep for a new scenario

| Want                              | Knob                                                                 |
| --------------------------------- | -------------------------------------------------------------------- |
| Which countries                   | the country list in `prep-geo.mjs` (+ supply their polygon GeoJSONs) |
| Label centred in the right region | `ANCHOR_BBOX[country]` (the story bbox)                              |
| Nudge a label                     | `NUDGE[country]` (lng, lat offset)                                   |
| What border is drawn              | the complete named source geometry; never the visible extent         |
| When each lights up               | derived from `stop` — depends on the river geometry                  |

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-geo-prep.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/render-stability.md ===== -->

# Moving Map Render Stability

Read this reference before building a moving 2D MapTiler scene or diagnosing a wavering Remotion render.

## Symptom and cause

If basemap detail shimmers or jitters during a pan/zoom, the likely cause is per-frame `map.jumpTo()`.
Headless MapTiler capture can resample both vector hillshade and satellite imagery differently frame to
frame. Tile retries, easing changes, and label changes do not solve that renderer effect.

## Required pattern: fixed map plate

For any 2D pan/zoom:

1. Render the MapTiler canvas once at the largest required zoom in an oversized container. Size it from the camera route and keep each dimension below the browser's reliable WebGL render-buffer limit (commonly 4096 px). Do **not** blindly use 3×: a 1920×1080 composition becomes 5760 px wide and Chromium may silently downsample it, causing visible pixelation during the CSS zoom.
2. Keep the map's camera static.
3. For each frame, calculate the approved target centre/zoom, then move the canvas with CSS `translate` + `scale`.
4. Apply the same transform to every projected HTML overlay.
5. Continue to animate GeoJSON data and paint properties imperatively; only the renderer camera is frozen.

Keep pitch and bearing constant. Use a 3D engine such as Cesium for genuine changing pitch/bearing or a terrain flythrough.

```ts
const baseZoom = Math.max(start.zoom, end.zoom);
const map = new maptilersdk.Map({
  container,
  style,
  center: end.center,
  zoom: baseZoom,
  pitch: end.pitch ?? 0,
  bearing: end.bearing ?? 0,
  interactive: false,
  fadeDuration: 0,
  canvasContextAttributes: {preserveDrawingBuffer: true},
});

// Per Remotion frame. `camera` is the approved centre/zoom interpolation.
const projected = map.project(camera.center);
const scale = 2 ** (camera.zoom - baseZoom);
const plate = {
  transform: `translate(${width / 2 - projected.x * scale}px, ${height / 2 - projected.y * scale}px) scale(${scale})`,
  transformOrigin: "0 0",
};

// Convert label projection with exactly the same plate transform.
const labelX = labelPoint.x * scale + width / 2 - projected.x * scale;
const labelY = labelPoint.y * scale + height / 2 - projected.y * scale;
```

### Plate sizing and sharpness

- Render at the maximum zoom reached by **any** camera waypoint, including intermediate or hold cameras. The CSS scale should never exceed `1`; otherwise the plate is being enlarged.
- Centre the frozen map on the midpoint of the camera route's geographic extent, not automatically on the final camera. This minimizes required overscan.
- Keep the largest canvas dimension at or below 4096 px unless the actual render environment has been tested with a larger `MAX_RENDERBUFFER_SIZE`.
- For 1920×1080, a 3840×2160 plate is a safe default. For 1080×1920, use approximately 2700×3840 when the route needs extra horizontal pan room.
- If the route cannot fit within that plate at the required zoom, split the shot into two fixed plates with a deliberate editorial transition. Do not trade sharpness for one enormous canvas.
- Distinguish failure modes: repeating shimmer means the live renderer is moving; steadily soft tiles during a CSS push means the fixed plate is underspecified, internally downsampled, or being scaled above `1`.

## Verification

- Render a short MP4, not only a Studio preview.
- Inspect static terrain texture and satellite detail while the camera moves.
- If any underlying map detail wavers, use the fixed map plate. Do not approve it as a minor preview artefact.
- Render WebGL with `--gl=angle`, `preserveDrawingBuffer:true`, and conservative concurrency (`1`) while validating.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/render-stability.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/remotion-maps/techniques/static-map/TECHNIQUE.md ===== -->

---
name: remotion-maps-static
description: Create a deterministic static locator map in Remotion when neither the camera nor geographic data animates.
---

# Static map

Use a static image when the map only provides location context. This is the smallest, fastest, and
most deterministic map technique.

## Build

1. Export or request a map image at the composition's final aspect ratio and at least its rendered
   pixel dimensions.
2. Store the image in the Remotion project's `public/` directory.
3. Render it with `CanvasImage` and `staticFile()`.
4. Add labels or markers as ordinary Remotion elements if they remain fixed.

```tsx
import React from 'react';
import {AbsoluteFill, CanvasImage, staticFile} from 'remotion';

export const StaticMap: React.FC = () => {
	return (
	  <>
  		<CanvasImage
  			src={staticFile('locator-map.png')}
  			style={{width: '100%', height: '100%', objectFit: 'cover'}}
  		/>
		</>
	);
};
```

## Overlays and Interactivity

Follow [Remotion Interactivity](../../../../remotion-interactivity/REFERENCE.md) best practices and [Remotion Markup Best practices](../../../REFERENCE.md) for elements.

<!-- ===== /file: remotion-best-practices/remotion-markup/remotion-maps/techniques/static-map/TECHNIQUE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/sequencing.md ===== -->

---
name: sequencing
description: Sequencing patterns for Remotion - delay, trim, limit duration of items
metadata:
  tags: sequence, series, timing, delay, trim
---

# Choose the timing boundary

Put timing props directly on a built-in interactive component or one made with
`Interactive.create()` when that item should be edited independently. Set audio
timing and volume on `Audio` from `@remotion/media`.

Use a shared `Sequence` when several layers must inherit the same trim, speed,
or start time, when overriding dimensions for descendants, or when the child
does not accept timing props. Choose `layout="none"` if the group should not
add a layout element; otherwise its absolute-fill layout also positions the
contents.

Use `Track` for non-overlapping items with independent positions and
`TransitionSeries` for consecutive items that should shift together when a
duration changes. Keep the series' own sequence boundaries, including when a
child already accepts timing props.

Follow [editable timeline structure](../remotion-interactivity/timeline-structure.md)
for grouping and examples. See [timing props](timing-props.md) for how `from`,
`trimBefore`, duration, speed, and looping combine, and
[editable video timelines](video-editing.md) for synchronized footage and captions.

<!-- ===== /file: remotion-best-practices/remotion-markup/sequencing.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/sfx.md ===== -->

---
name: sfx
description: Including sound effects
metadata:
  tags: sfx, sound, effect, audio
---

To include a sound effect, use `<Audio>` from `@remotion/media`:

```tsx
import { Audio } from "@remotion/media";

<Audio src={"https://remotion.media/whoosh.wav"} />;
```

The following sound effects are available:

- `https://remotion.media/whoosh.wav`
- `https://remotion.media/whip.wav`
- `https://remotion.media/page-turn.wav`
- `https://remotion.media/switch.wav`
- `https://remotion.media/mouse-click.wav`
- `https://remotion.media/shutter-modern.wav`
- `https://remotion.media/shutter-old.wav`
- `https://remotion.media/ding.wav`
- `https://remotion.media/bruh.wav`
- `https://remotion.media/vine-boom.wav`
- `https://remotion.media/windows-xp-error.wav`
- `https://remotion.media/fah.wav`
- `https://remotion.media/spongebob-fail.wav`
- `https://remotion.media/omg-hell-nah.wav`
- `https://remotion.media/price-is-right-fail.wav`
- `https://remotion.media/romance-meme.wav`
- `https://remotion.media/bone-crack.wav`
- `https://remotion.media/anime-wow.wav`
- `https://remotion.media/yippee.wav`
- `https://remotion.media/loading-lag.wav`
- `https://remotion.media/wilhelm-scream.wav`
- `https://remotion.media/mac-quack.wav`
- `https://remotion.media/skedaddle.wav`
- `https://remotion.media/snapchat-notification.wav`
- `https://remotion.media/nelly-ahh.wav`
- `https://remotion.media/sanctuary-guardian-what.wav`
- `https://remotion.media/minecraft-hurt.wav`
- `https://remotion.media/oh-my-god-vine.wav`
- `https://remotion.media/illuminati-confirmed.wav`
- `https://remotion.media/dramatic-boomer.wav`
- `https://remotion.media/triggered.wav`
- `https://remotion.media/record-scratch.wav`

For more sound effects, search the internet. A good resource is https://github.com/kapishdima/soundcn/tree/main/assets.

<!-- ===== /file: remotion-best-practices/remotion-markup/sfx.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/silence-detection.md ===== -->

---
name: silence-detection
description: Adaptive silence detection for video/audio files using FFmpeg loudnorm and silencedetect
metadata:
  tags: silence, detection, trimming, ffmpeg, loudnorm, audio
---

# Adaptive Silence Detection

Detect silent segments in video or audio files.

Requires FFmpeg — see [ffmpeg.md](./ffmpeg.md) for how to invoke it in Remotion projects.

## Step 1: Measure loudness with `loudnorm`

Use the `loudnorm` filter in JSON mode to get the EBU R128 integrated loudness and gating threshold for each file:

```bash
npx remotion ffmpeg -i public/video.mov -map 0:a -af loudnorm=print_format=json -f null /dev/null
```

As output you will get:
- `input_i`: Integrated loudness (dB) — the overall perceived volume
- `input_thresh`: EBU R128 gating threshold (dB) — the level below which audio is considered too quiet to count toward loudness measurement

## Step 2: Detect silences using adaptive threshold

Pass the `input_thresh` value from step 1 as the `noise` parameter to `silencedetect`:

```bash
npx remotion ffmpeg -i public/video.mov -map 0:a -af "silencedetect=noise=${THRESH}dB:d=0.5" -f null /dev/null
```

Parameters:
- `noise`: The threshold below which audio is considered silent. Use `input_thresh` from step 1.
- `d`: Minimum silence duration in seconds. `0.5` is a good default.

## Interpreting the output

The filter outputs pairs of `silence_start` and `silence_end` timestamps:

```
[silencedetect] silence_start: 0
[silencedetect] silence_end: 2.241021 | silence_duration: 2.241021
[silencedetect] silence_start: 38.77425
[silencedetect] silence_end: 39.619604 | silence_duration: 0.845354
```

## Identifying leading and trailing silence

- **Leading silence**: Consecutive silence segments starting at or near 0. If the first `silence_start` is > 0.5s, there is no leading silence.
- **Trailing silence**: The last silence segment that extends to (or near) the end of the file. Compare the last `silence_end` with the file's total duration.

When multiple silences are nearly contiguous at the start or end (gap < 0.2s), treat them as a single leading/trailing silence block.

## Using with Remotion's `<Video>` component

Apply the detected trim points using `trimBefore` and `durationInFrames` (values are in frames):

```tsx
import { Video } from "@remotion/media";
import { staticFile, useVideoConfig } from "remotion";

const { fps } = useVideoConfig();

<Video
  src={staticFile("video.mov")}
  trimBefore={Math.floor(leadingEnd * fps)}
  durationInFrames={Math.ceil(trailingStart * fps) - Math.floor(leadingEnd * fps)}
/>
```

<!-- ===== /file: remotion-best-practices/remotion-markup/silence-detection.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/text-highlights.md ===== -->

---
name: text-highlights
description: Animated text highlights and hand-drawn annotations using @remotion/rough-notation.
metadata:
  tags: text, highlights, annotations, circles, rough-notation
---

# Text highlights

Use `@remotion/rough-notation` to draw animated annotations around or behind text. It supports highlights, circles, underlines, strike-throughs, crossed-off text, boxes, and brackets.

Docs: https://www.remotion.dev/docs/text-highlights

Install the package using the same Remotion version as the project:

```bash
bunx remotion add @remotion/rough-notation
```

Choose the component that describes the annotation: `<Highlight>`, `<Circle>`, `<Underline>`, `<StrikeThrough>`, `<CrossedOff>`, `<Box>`, or `<Bracket>`. The component determines both the annotation style and whether it renders behind or on top of the text.

Drive `progress` from `useCurrentFrame()` so the annotation is deterministic and synchronized with the video:

```tsx
import {Circle, Highlight} from '@remotion/rough-notation';
import {interpolate, useCurrentFrame} from 'remotion';

export const TextAnnotations: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <div style={{fontSize: 80}}>
      This is{' '}
      <Highlight
        color="rgba(255, 236, 79, 0.62)"
        progress={interpolate(frame, [15, 40], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })}
      >
        important
      </Highlight>
      , and this is{' '}
      <Circle color="#2563eb" progress={interpolate(frame, [15, 40], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })}>
        connected
      </Circle>
      .
    </div>
  );
};
```

Keep `progress` inline, hardcoded and use `interpolate` for maximum [Studio interactivity](../remotion-interactivity/REFERENCE.md).

<!-- ===== /file: remotion-best-practices/remotion-markup/text-highlights.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/timing-props.md ===== -->

## Delaying, trimming

In the component that renders these items, get `const {fps} = useVideoConfig()`.
Use this `fps` for seconds-to-frames expressions on the JSX node, rather than
a fixed FPS constant.

The following timing props are supported by built-in components (`<AbsoluteFill>`, `<Interactive.*>`, `<Img>`, `<AnimatedImage>`, `<CanvasImage>`, `<HtmlInCanvas>`, `<Solid>`, `<Sequence>`, `<Track>` from `remotion`, `<Video>` and `<Audio>` from `@remotion/media`, `<Gif>`, and more).
Custom components made with `Interactive.create()` accept them too, see [Prefer interactive components with their own timelines](../remotion-interactivity/REFERENCE.md#prefer-interactive-components-with-their-own-timelines).

### `from`

When the item starts appearing in the timeline.
Its children start at frame `0` when it appears.

```tsx
<Img from={1 * fps} {/* ... */}/>
<Video from={1 * fps} {/* ... */}/>
<Interactive.Div from={1 * fps} {/* ... */}/>
<LowerThird from={1 * fps} {/* ... */}/>
```

### `trimBefore`

Sets the first frame of the item's own timeline:

```tsx
// Trim away first 2 seconds of footage
<Video trimBefore={2 * fps} {/* ... */} />

// `useCurrentFrame()` of the children starts at `10 * fps`
<Interactive.Div trimBefore={10 * fps} {/* ... */} />
```

### `durationInFrames`

How many frames of the item's own timeline are shown, starting at `trimBefore`.
Use it to end media early instead of cutting the file:

```tsx
// Play the footage from second 2 to second 5
<Video trimBefore={2 * fps} durationInFrames={3 * fps} {/* ... */} />
<Img durationInFrames={20 * fps} {/* ... */}/>
<LowerThird durationInFrames={5 * fps} {/* ... */}/>
```

### `playbackRate`

Changes the speed of the item.
Children calling `useCurrentFrame()` advance `playbackRate` frames per frame of the parent.
The item occupies `durationInFrames / playbackRate` frames in its parent timeline.

```tsx
// 2x speed
<Video playbackRate={2} {/* ... */} />
<LowerThird playbackRate={0.5} durationInFrames={2 * fps} {/* ... */} />
```

### `loop`

Repeats the range selected by `trimBefore` and `durationInFrames` until the parent ends.
`<Video>`, `<Audio>`, `<Gif>` and `<AnimatedImage>` may omit `durationInFrames`; the media's own duration after `trimBefore` then defines the loop range.
Other items need `durationInFrames` to define the loop range:

```tsx
<Video loop {/* ... */} />
<Interactive.Div durationInFrames={2 * fps} loop {/* ... */} />
```

Put timing and volume directly on `<Audio>`.

`<Img>`, `<CanvasImage>`, `<Solid>` and shapes do not support `loop` because their output does not change over time.

### Order of operations

1. `from` positions the item in its parent timeline.
2. `trimBefore` sets the first frame of the item's own timeline.
3. `durationInFrames` selects the range of the item's own timeline.
4. `playbackRate` stretches or compresses the selected range.
5. `loop` repeats the selected range until the parent ends.

Children calling `useCurrentFrame()` get `trimBefore + (frame - from) * playbackRate`.

See [Timing and trimming](https://www.remotion.dev/docs/timing) for more details.

### Fallback

If a component does not support these props, wrap it in `<Sequence>` from `remotion`, which has them.

- `layout="absolute-fill"` makes the Sequence behave like AbsoluteFill
- `layout="none"` is "headless" mode, no wrapper element is used.

<!-- ===== /file: remotion-best-practices/remotion-markup/timing-props.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/timing.md ===== -->

Drive motion with `interpolate()` over an explicit frame range. 
To customize timing, use **`Easing.bezier`** or `Easing.spring`.

A simple linear interpolation is done using the `interpolate` function.

```ts title="Going from 0 to 1 over 0.3 seconds"
import { interpolate } from "remotion";

const opacity = interpolate(frame, [0, 0.3 * fps], [0, 1]);
```

By default, the values are not clamped, so the value can go outside the range [0, 1].  
Here is how they can be clamped:

```ts title="Going from 0 to 1 over 0.3 seconds with extrapolation"
const opacity = interpolate(frame, [0, 0.3 * fps], [0, 1], {
  extrapolateRight: "clamp",
  extrapolateLeft: "clamp",
});
```

## Studio-editable animation patterns

When an animation should be editable in Remotion Studio, keep the `interpolate()` call directly in the `style` prop and prefer individual CSS transform properties:

```tsx
// 👍 Inline editable keyframes and transform shorthands
style={{
  scale: interpolate(frame, [0, 100], [0, 1]),
  translate: interpolate(frame, [0, 100], ["0px 0px", "100px 100px"]),
  rotate: interpolate(frame, [0, 100], ["20deg", "90deg"]),
}}

// 👎 Hidden values and transform strings become computed in Studio
const translateY = interpolate(frame, [0, 100], [0, 120]);
const rotation = interpolate(frame, [0, 100], [0, 20]);

style={{
  transform: `translateY(${translateY}px) rotate(${rotation}deg)`,
}}
```

Use `transform` strings only when individual CSS transform properties do not cover the effect, such as `skew()`, `perspective()`, or order-sensitive multi-transform chains.

## Spring easing

A nice push movement with no bounce:

```ts
import { interpolate, Easing } from "remotion";

const opacity = interpolate(frame, [0, 0.3 * fps], [0, 1], {
  easing: Easing.spring({damping: 200}),
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

## Bézier easing

Pass values like you would to a CSS cubic-bezier function.

```ts
import { interpolate, Easing } from "remotion";

const opacity = interpolate(frame, [0, 0.3 * fps], [0, 1], {
  easing: Easing.bezier(0.16, 1, 0.3, 1),
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

## Animating scale

When animating scale, if the output is linear, the perceived scale would be smaller the larger the scale gets.  
Use this option to compensate:

```ts
const scale = interpolate(frame, [0, 0.3 * fps], [0, 1], {
  easing: Easing.bezier(0.16, 1, 0.3, 1),
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  output: 'perceptual-scale' // <- Add this to scale animations
});
```

## Multiple keyframes

Add as many keyframes as you want. For multiple easings, pass an array with `n - 1` items:

```ts
const scale = interpolate(frame, [0, 1 * fps, 9 * fps, 10 * fps], [0, 1, 1, 0], {
  easing: [Easing.bezier(0.16, 1, 0.3, 1), Easing.linear, Easing.spring({damping: 200})],
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  output: 'perceptual-scale' // <- Add this to scale animations
});
```

## Posterization

You can intentionally reduce the frame rate for artistic reason. Use if it makes sense.

```ts
const scale = interpolate(frame, [0, 1 * fps], [0, 1], {
  easing: Easing.bezier(0.16, 1, 0.3, 1),
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  posterize: 3 // Only every 3rd frame is sampled
});
```

<!-- ===== /file: remotion-best-practices/remotion-markup/timing.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/transitions.md ===== -->

---
name: transitions
description: Scene transitions and overlays for Remotion using TransitionSeries.
metadata:
  tags: transitions, overlays, fade, slide, wipe, scenes
---

## TransitionSeries

`<TransitionSeries>` arranges scenes and supports two ways to enhance the cut point between them:

- **Transitions** (`<TransitionSeries.Transition>`) — crossfade, slide, wipe, etc. between two scenes. Shortens the timeline because both scenes play simultaneously during the transition.
- **Overlays** (`<TransitionSeries.Overlay>`) — render an effect (e.g. a light leak) on top of the cut point without shortening the timeline.

For a multi-scene timeline, keep the outer `<TransitionSeries>` visible in the
timeline. Studio favors the active scene sequence when the two have the same
full-frame canvas outline.

Children are absolutely positioned.

## Prerequisites

```bash
bunx remotion add @remotion/transitions
```

## Transition example

Use the connected `Chapter` scene from the
[composition example](../remotion-interactivity/timeline-structure.md).

```tsx title="TransitionVideo.tsx"
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {Chapter} from './Chapter';

export const TransitionVideo = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence name="Opening" durationInFrames={60}>
      <Chapter title="Introduction" style={{backgroundColor: '#111111'}} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition
      presentation={fade()}
      timing={linearTiming({durationInFrames: 15})}
    />
    <TransitionSeries.Sequence name="Feature" durationInFrames={60}>
      <Chapter title="New features" style={{backgroundColor: '#243b53'}} />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
```

## Custom presentation

```tsx title="SlideInPresentation.tsx"
import type {TransitionPresentationComponentProps} from '@remotion/transitions';

export const SlideInPresentation = ({
  children,
  presentationDirection,
  presentationProgress,
}: TransitionPresentationComponentProps<Record<string, never>>) => {
  if (presentationDirection === 'exiting') {
    return <>{children}</>;
  }

  return (
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          translate: `${(1 - presentationProgress) * 100}% 0`,
        }}
      >
        {children}
      </div>
    </div>
  );
};
```

Use it in place of `fade()` in `TransitionVideo.tsx`:

```tsx
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {SlideInPresentation} from './SlideInPresentation';

<TransitionSeries.Transition
  presentation={{component: SlideInPresentation, props: {}}}
  timing={linearTiming({durationInFrames: 15})}
/>;
```

## Overlay example

```tsx title="LightLeakOverlay.tsx"
import {lightLeak} from '@remotion/effects/light-leak';
import type {CSSProperties} from 'react';
import {Interactive, interpolate, Solid, useCurrentFrame, useVideoConfig} from 'remotion';

const LightLeakOverlayInner = ({style}: {readonly style?: CSSProperties}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, height, width} = useVideoConfig();

  return (
    <Solid
      width={width}
      height={height}
      style={style}
      effects={[
        lightLeak({
          progress: interpolate(frame, [0, durationInFrames - 1], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }),
      ]}
    />
  );
};

export const LightLeakOverlay = Interactive.create({
  Component: LightLeakOverlayInner,
  layout: 'none',
});
```

```tsx title="OverlayVideo.tsx"
import {TransitionSeries} from '@remotion/transitions';
import {Chapter} from './Chapter';
import {LightLeakOverlay} from './LightLeakOverlay';

export const OverlayVideo = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence name="Opening" durationInFrames={60}>
      <Chapter title="Introduction" style={{backgroundColor: '#111111'}} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Overlay durationInFrames={20}>
      <LightLeakOverlay name="Light leak" />
    </TransitionSeries.Overlay>
    <TransitionSeries.Sequence name="Feature" durationInFrames={60}>
      <Chapter title="New features" style={{backgroundColor: '#243b53'}} />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
```

## Mixing transitions and overlays

Separate overlays and transitions with a scene.

```tsx title="MixedVideo.tsx"
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {Chapter} from './Chapter';
import {LightLeakOverlay} from './LightLeakOverlay';

export const MixedVideo = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence name="Opening" durationInFrames={60}>
      <Chapter title="Introduction" style={{backgroundColor: '#111111'}} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Overlay durationInFrames={30}>
      <LightLeakOverlay name="Light leak" />
    </TransitionSeries.Overlay>
    <TransitionSeries.Sequence name="Feature" durationInFrames={60}>
      <Chapter title="New features" style={{backgroundColor: '#243b53'}} />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition
      presentation={fade()}
      timing={linearTiming({durationInFrames: 15})}
    />
    <TransitionSeries.Sequence name="Closing" durationInFrames={60}>
      <Chapter title="Thank you" style={{backgroundColor: '#382345'}} />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
```

## Transition props

`<TransitionSeries.Transition>` requires:

- `presentation` — the visual effect (e.g. `fade()`, `slide()`, `wipe()`).
- `timing` — controls speed and easing (e.g. `linearTiming()`, `springTiming()`).

## Overlay props

`<TransitionSeries.Overlay>` accepts:

- `durationInFrames` — how long the overlay is visible (positive integer).
- `offset?` — shifts the overlay relative to the cut point center. Positive = later, negative = earlier. Default: `0`.

## Available transition types

Import transitions from their respective modules:

```tsx
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { flip } from "@remotion/transitions/flip";
import { clockWipe } from "@remotion/transitions/clock-wipe";
```

## Slide transition with direction

```tsx
import {TransitionSeries, linearTiming} from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";

<TransitionSeries.Transition
  presentation={slide({ direction: "from-left" })}
  timing={linearTiming({ durationInFrames: 20 })}
/>;
```

Directions: `"from-left"`, `"from-right"`, `"from-top"`, `"from-bottom"`

## Timing options

```tsx
import { linearTiming, springTiming } from "@remotion/transitions";

// Linear timing - constant speed
linearTiming({ durationInFrames: 20 });

// Spring timing - organic motion
springTiming({ config: { damping: 200 }, durationInFrames: 25 });
```

## Duration calculation

Transitions overlap adjacent scenes, so the total composition length is **shorter** than the sum of all sequence durations. Overlays do **not** affect the total duration.

For example, with two 60-frame sequences and a 15-frame transition:

- Without transitions: `60 + 60 = 120` frames
- With transition: `60 + 60 - 15 = 105` frames

Adding an overlay between two other sequences does not change the total.

### Getting the duration of a transition

Use the `getDurationInFrames()` method on the timing object:

```tsx
import { linearTiming, springTiming } from "@remotion/transitions";

const linearDuration = linearTiming({
  durationInFrames: 20,
}).getDurationInFrames({ fps: 30 });
// Returns 20

const springDuration = springTiming({
  config: { damping: 200 },
}).getDurationInFrames({ fps: 30 });
// Returns calculated duration based on spring physics
```

For `springTiming` without an explicit `durationInFrames`, the duration depends on `fps` because it calculates when the spring animation settles.

### Calculating total composition duration

```tsx
import { linearTiming } from "@remotion/transitions";

const scene1Duration = 60;
const scene2Duration = 60;
const scene3Duration = 60;

const timing1 = linearTiming({ durationInFrames: 15 });
const timing2 = linearTiming({ durationInFrames: 20 });

const transition1Duration = timing1.getDurationInFrames({ fps: 30 });
const transition2Duration = timing2.getDurationInFrames({ fps: 30 });

const totalDuration =
  scene1Duration +
  scene2Duration +
  scene3Duration -
  transition1Duration -
  transition2Duration;
// 60 + 60 + 60 - 15 - 20 = 145 frames
```

<!-- ===== /file: remotion-best-practices/remotion-markup/transitions.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/video-editing.md ===== -->

# Editable video timelines

Structure the timeline around the things the user edits together: a captioned
shot, a set of cutaways, or an independently timed music segment. Write every
independently editable clip as its own JSX node with inline names and props.
Use the [timeline structure guide](../remotion-interactivity/timeline-structure.md)
for choosing tracks, timing groups, and connected compositions.

## Choose the cut behavior

Use a named `Track` for non-overlapping clips with independent start times. Keep
`from`, `trimBefore`, `durationInFrames`, and `playbackRate` on each clip. Moving
or resizing one clip then leaves the other start times unchanged.

Use `TransitionSeries` when consecutive clips should remain adjacent. Put
`durationInFrames` on each `TransitionSeries.Sequence`; the series calculates
start times and repositions later clips after a duration change. It also handles
overlapping transitions. Preserve these specialized boundaries when refactoring.

Get `fps` from `useVideoConfig()` for seconds-to-frames expressions, and keep
them on the JSX node, such as `trimBefore={4 * fps}`. Literal frame counts are
appropriate when the edit is already specified in frames.

## Keep synchronized layers on one clock

Put a shot's video, captions, and source-synchronized overlays under one timing
boundary. Apply `trimBefore`, `durationInFrames`, and `playbackRate` to that
boundary once. For an independently placed group, also set its `from`.

A `Sequence` is useful here because moving, trimming, retiming, or deleting the
group affects all its layers. For consecutive shots, use the existing
`TransitionSeries.Sequence` for the same purpose:

```tsx
import {Video} from '@remotion/media';
import {TransitionSeries} from '@remotion/transitions';
import {staticFile, useVideoConfig} from 'remotion';
import {BasicCaptions} from './basic-captions';

export const Interview = () => {
  const {fps} = useVideoConfig();
  return (
    <TransitionSeries name="Interview shots">
      <TransitionSeries.Sequence
        name="Opening"
        trimBefore={4 * fps}
        durationInFrames={3 * fps}
      >
        <Video name="Opening footage" src={staticFile('interview.mp4')} />
        <BasicCaptions
          name="Opening captions"
          width={900}
          style={{position: 'absolute', bottom: 80, translate: '510px 0px'}}
          captions={[
            {
              text: 'Hello',
              startMs: 4500,
              endMs: 4900,
              timestampMs: 4700,
              confidence: null,
            },
            {
              text: ' world',
              startMs: 4900,
              endMs: 5400,
              timestampMs: 5150,
              confidence: null,
            },
          ]}
        />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence
        name="Next shot"
        trimBefore={10 * fps}
        durationInFrames={2 * fps}
      >
        <Video name="Next footage" src={staticFile('interview.mp4')} />
        <BasicCaptions
          name="Next captions"
          width={900}
          style={{position: 'absolute', bottom: 80, translate: '510px 0px'}}
          captions={[
            {
              text: 'Next',
              startMs: 10500,
              endMs: 11000,
              timestampMs: 10750,
              confidence: null,
            },
          ]}
        />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
```

Each caption array stays inline on its own caption node, with timestamps relative
to the original media file. Passing the array through a generic shot prop removes
the source array the Caption editor needs. See
[displaying captions](../remotion-captions/display-captions.md#displaying-captions-alongside-video-content)
for the caption component and setup.

## Place overlays at the scope they span

Keep a source-synchronized HUD inside its shot. Put a sticker that continues
across several cuts in the enclosing scene, so the end of the first cut does
not unmount it. Use that scene's frame coordinates for its timing.

Within a shot or scene, put successive cutaways on a named `Cutaways` track.
Keep simultaneous visuals on separate tracks. If cutaways cover a speaking
video, retain the underlying speech or deliberately separate its audio; removing
an obscured video can also remove the voice.

Group a sticker or other visual with its accompanying sound when they should
move or be deleted together. Keep their local offsets inside the group. Give
both the visual and sound their intended durations so the group neither cuts
off a sound tail nor extends the visual to cover that tail.

## Put music segments on a shared track

Music clips with gaps or adjacent boundaries can share one named track. They
remain separately editable, including their source trims and volume envelopes:

See the [complete timeline example](../remotion-interactivity/timeline-structure.md)
for a music track alongside scene tracks.

Check natural audio durations as well as explicit bounds before putting sounds
on a track. An item may end exactly where the next begins, but overlapping tails
need separate tracks. Do not shorten sounds just to make them fit.

## Preserve the edit when restructuring

Keep source trims, cut lengths, playback rates, caption arrays, volume envelopes,
and stacking order unchanged unless the user requested an edit. Moving content
under a new timing boundary can change the frame returned by `useCurrentFrame()`;
preserve the source clock or adjust local offsets deliberately.

Verify the full composition and any connected views, rather than judging the
result only from a standalone scene. Check visual output and audio around cuts,
overlay boundaries, and sound tails. Grouping the timeline should preserve the
existing edit while making its controls easier to use.

<!-- ===== /file: remotion-best-practices/remotion-markup/video-editing.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-markup/voiceover.md ===== -->

---
name: voiceover
description: Adding AI-generated voiceover to Remotion compositions using TTS
metadata:
  tags: voiceover, audio, elevenlabs, tts, speech, calculateMetadata, dynamic duration
---

# Adding AI voiceover to a Remotion composition

Use ElevenLabs TTS to generate speech audio per scene, then use [`calculateMetadata`](./calculate-metadata.md) to dynamically size the composition to match the audio.

## Prerequisites

By default this guide uses **ElevenLabs** as the TTS provider (`ELEVENLABS_API_KEY` environment variable). Users may substitute any TTS service that can produce an audio file.

If the user has not specified a TTS provider, recommend ElevenLabs and ask for their API key.

Ensure the environment variable is available when running the generation script:

```bash
node --strip-types generate-voiceover.ts
```

## Generating audio with ElevenLabs

Create a script that reads the config, calls the ElevenLabs API for each scene, and writes MP3 files to the `public/` directory so Remotion can access them via `staticFile()`.

The core API call for a single scene:

```ts title="generate-voiceover.ts"
const response = await fetch(
  `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
  {
    method: "POST",
    headers: {
      "xi-api-key": process.env.ELEVENLABS_API_KEY!,
      "Content-Type": "application/json",
      Accept: "audio/mpeg",
    },
    body: JSON.stringify({
      text: "Welcome to the show.",
      model_id: "eleven_multilingual_v2",
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.3,
      },
    }),
  },
);

const audioBuffer = Buffer.from(await response.arrayBuffer());
writeFileSync(`public/voiceover/${compositionId}/${scene.id}.mp3`, audioBuffer);
```

## Dynamic composition duration with calculateMetadata

Use [`calculateMetadata`](./calculate-metadata.md) to measure the [audio durations](../remotion-multimedia/get-audio-duration.md) and set the composition length accordingly.

```tsx
import { CalculateMetadataFunction, staticFile } from "remotion";
import { getAudioDuration } from "./get-audio-duration";

// Match the fps on this composition's <Composition> registration.
const compositionFps = 30;

const SCENE_AUDIO_FILES = [
  "voiceover/my-comp/scene-01-intro.mp3",
  "voiceover/my-comp/scene-02-main.mp3",
  "voiceover/my-comp/scene-03-outro.mp3",
];

export const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  const durations = await Promise.all(
    SCENE_AUDIO_FILES.map((file) => getAudioDuration(staticFile(file))),
  );

  const sceneDurations = durations.map((durationInSeconds) => {
    return durationInSeconds * compositionFps;
  });

  return {
    durationInFrames: Math.ceil(sceneDurations.reduce((sum, d) => sum + d, 0)),
  };
};
```

The computed `sceneDurations` are passed into the component via a `voiceover` prop so the component knows how long each scene should be.
`calculateMetadata` runs outside the composition component, so it cannot call
`useVideoConfig()`. Inside the component, use `const {fps} = useVideoConfig()`
for timing props instead of reusing `compositionFps`.

If the composition uses [`<TransitionSeries>`](./transitions.md), subtract the overlap from total duration: [./transitions.md#calculating-total-composition-duration](./transitions.md#calculating-total-composition-duration)

## Rendering audio in the component

See [audio.md](./audio.md) for more information on how to render audio in the component.

## Delaying audio start

See [audio.md#delaying](./audio.md#delaying) for more information on how to delay the audio start.

<!-- ===== /file: remotion-best-practices/remotion-markup/voiceover.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-multimedia/REFERENCE.md ===== -->

---
name: remotion-multimedia
description: Interacting with Mediabunny
version: 4.0.539
---

Mediabunny is a multimedia library for dealing with audio and video in the browser.
Here is a compact overview of its capabilities: https://mediabunny.dev/llms.txt

## Getting audio duration

See [get-audio-duration.md](get-audio-duration.md) for getting the duration of an audio file in seconds with Mediabunny.

## Getting video dimensions

See [get-video-dimensions.md](get-video-dimensions.md) for getting the width and height of a video file with Mediabunny.

## Getting video duration

See [get-video-duration.md](get-video-duration.md) for getting the duration of a video file in seconds with Mediabunny.

<!-- ===== /file: remotion-best-practices/remotion-multimedia/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-multimedia/get-audio-duration.md ===== -->

---
name: get-audio-duration
description: Getting the duration of an audio file in seconds with Mediabunny
metadata:
  tags: duration, audio, length, time, seconds, mp3, wav
---

# Getting audio duration with Mediabunny

Mediabunny can extract the duration of an audio file. It works in browser, Node.js, and Bun environments.

## Getting audio duration

```tsx title="get-audio-duration.ts"
import { Input, ALL_FORMATS, UrlSource } from "mediabunny";

export const getAudioDuration = async (src: string) => {
  const input = new Input({
    formats: ALL_FORMATS,
    source: new UrlSource(src),
  });

  const durationInSeconds = await input.computeDuration();
  return durationInSeconds;
};
```

## Usage

```tsx
const duration = await getAudioDuration("https://remotion.media/audio.mp3");
console.log(duration); // e.g. 180.5 (seconds)
```

## Using with staticFile in Remotion

Make sure to wrap the file path in `staticFile()`:

```tsx
import { staticFile } from "remotion";

const duration = await getAudioDuration(staticFile("audio.mp3"));
```

## In Node.js and Bun

Use `FilePathSource` instead of `UrlSource` to read a file from disk:

```tsx
import { Input, ALL_FORMATS, FilePathSource } from "mediabunny";

const input = new Input({
  formats: ALL_FORMATS,
  source: new FilePathSource("audio.mp3"),
});

const durationInSeconds = await input.computeDuration();
input.dispose(); // Closes the file handle
```

For a `File` from a file input or drag and drop, use `new BlobSource(file)` instead.

<!-- ===== /file: remotion-best-practices/remotion-multimedia/get-audio-duration.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-multimedia/get-video-dimensions.md ===== -->

---
name: get-video-dimensions
description: Getting the width and height of a video file with Mediabunny
metadata:
  tags: dimensions, width, height, resolution, size, video
---

# Getting video dimensions with Mediabunny

Mediabunny can extract the width and height of a video file. It works in browser, Node.js, and Bun environments.

## Getting video dimensions

```tsx
import { Input, ALL_FORMATS, UrlSource } from "mediabunny";

export const getVideoDimensions = async (src: string) => {
  const input = new Input({
    formats: ALL_FORMATS,
    source: new UrlSource(src),
  });

  const videoTrack = await input.getPrimaryVideoTrack();
  if (!videoTrack) {
    throw new Error("No video track found");
  }

  return {
    width: videoTrack.displayWidth,
    height: videoTrack.displayHeight,
  };
};
```

## Usage

```tsx
const dimensions = await getVideoDimensions("https://remotion.media/video.mp4");
console.log(dimensions.width); // e.g. 1920
console.log(dimensions.height); // e.g. 1080
```

## Using with local files

For a `File` from a file input or drag and drop, use `BlobSource` instead of `UrlSource`:

```tsx
import { Input, ALL_FORMATS, BlobSource } from "mediabunny";

const input = new Input({
  formats: ALL_FORMATS,
  source: new BlobSource(file), // File object from input or drag-drop
});

const videoTrack = await input.getPrimaryVideoTrack();
if (!videoTrack) {
  throw new Error("No video track found");
}

const width = videoTrack.displayWidth;
const height = videoTrack.displayHeight;
```

In Node.js and Bun, use `new FilePathSource(path)` to read a file from disk, and call `input.dispose()` when done.

## Using with staticFile in Remotion

```tsx
import { staticFile } from "remotion";

const dimensions = await getVideoDimensions(staticFile("video.mp4"));
```

<!-- ===== /file: remotion-best-practices/remotion-multimedia/get-video-dimensions.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-multimedia/get-video-duration.md ===== -->

---
name: get-video-duration
description: Getting the duration of a video file in seconds with Mediabunny
metadata:
  tags: duration, video, length, time, seconds
---

# Getting video duration with Mediabunny

Mediabunny can extract the duration of a video file. It works in browser, Node.js, and Bun environments.

## Getting video duration

```tsx
import { Input, ALL_FORMATS, UrlSource } from "mediabunny";

export const getVideoDuration = async (src: string) => {
  const input = new Input({
    formats: ALL_FORMATS,
    source: new UrlSource(src),
  });

  const durationInSeconds = await input.computeDuration();
  return durationInSeconds;
};
```

## Usage

```tsx
const duration = await getVideoDuration("https://remotion.media/video.mp4");
console.log(duration); // e.g. 10.5 (seconds)
```

## Video files from the public/ directory

Make sure to wrap the file path in `staticFile()`:

```tsx
import { staticFile } from "remotion";

const duration = await getVideoDuration(staticFile("video.mp4"));
```

## In Node.js and Bun

Use `FilePathSource` instead of `UrlSource` to read a file from disk:

```tsx
import { Input, ALL_FORMATS, FilePathSource } from "mediabunny";

const input = new Input({
  formats: ALL_FORMATS,
  source: new FilePathSource("video.mp4"),
});

const durationInSeconds = await input.computeDuration();
input.dispose(); // Closes the file handle
```

For a `File` from a file input or drag and drop, use `new BlobSource(file)` instead.

<!-- ===== /file: remotion-best-practices/remotion-multimedia/get-video-duration.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-render/REFERENCE.md ===== -->

---
name: remotion-render
description: Export a Remotion video
version: 4.0.539
---

## General rendering strategy

Render a video using:

```
npx remotion render
```

Full list of options: https://www.remotion.dev/docs/cli/render.md

Render a still using:

```
npx remotion still
```

Full list of options: https://www.remotion.dev/docs/cli/still.md

To render several frames as images in one call, use `render --frames`:

```
npx remotion render [composition-id] out/frames --frames=0,30,90 --image-format=png
```

See https://www.remotion.dev/docs/cli/render.md#--frames for more options.

## Transparent videos

See [Transparent videos](./transparent-videos.md) for rendering out a video with transparency.

<!-- ===== /file: remotion-best-practices/remotion-render/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-render/transparent-videos.md ===== -->

---
name: transparent-videos
description: Rendering transparent videos in Remotion
metadata:
  tags: transparent, alpha, codec, vp9, prores, webm
---

# Rendering Transparent Videos

Remotion can render transparent videos in two ways: as a ProRes video or as a WebM video.

## Transparent ProRes

Ideal for when importing into video editing software.

**CLI:**

```bash
npx remotion render --image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444 MyComp out.mov
```

**Default in Studio** (restart Studio after changing):

```ts
// remotion.config.ts
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("png");
Config.setPixelFormat("yuva444p10le");
Config.setCodec("prores");
Config.setProResProfile("4444");
```

**Setting it as the default export settings for a composition** (using `calculateMetadata`):

```tsx
import { CalculateMetadataFunction } from "remotion";

const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  return {
    defaultCodec: "prores",
    defaultVideoImageFormat: "png",
    defaultPixelFormat: "yuva444p10le",
    defaultProResProfile: "4444",
  };
};

<Composition
  id="my-video"
  component={MyVideo}
  durationInFrames={150}
  fps={30}
  width={1920}
  height={1080}
  calculateMetadata={calculateMetadata}
/>;
```

## Transparent WebM (VP9)

Ideal for when playing in a browser.

**CLI:**

```bash
npx remotion render --image-format=png --pixel-format=yuva420p --codec=vp9 MyComp out.webm
```

**Default in Studio** (restart Studio after changing):

```ts
// remotion.config.ts
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("png");
Config.setPixelFormat("yuva420p");
Config.setCodec("vp9");
```

**Setting it as the default export settings for a composition** (using `calculateMetadata`):

```tsx
import { CalculateMetadataFunction } from "remotion";

const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  return {
    defaultCodec: "vp8",
    defaultVideoImageFormat: "png",
    defaultPixelFormat: "yuva420p",
  };
};

<Composition
  id="my-video"
  component={MyVideo}
  durationInFrames={150}
  fps={30}
  width={1920}
  height={1080}
  calculateMetadata={calculateMetadata}
/>;
```

<!-- ===== /file: remotion-best-practices/remotion-render/transparent-videos.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-saas/REFERENCE.md ===== -->

---
name: remotion-saas
description: Build an app with Remotion
version: 4.0.539
---

One can build apps with Remotion.  
It is possible to have a simple form and hook it up to a render, or have a complex video editor.

## Choosing a template or a framework

We have several templates for SaaS which can be cloned or used as a reference.
See [Choosing a framework](framework.md) for help choosing a template or framework.

## The `<Player>`

This component allows embedding a Remotion preview in a React app. See [Player](player.md) for more information about the Player.

## Rendering

There are client-side and server-side rendering options available. See [Rendering](rendering.md) for advice on how to choose, and about the Lambda, Vercel, Node.js and Cloudflare options.

## With Vue

See https://www.remotion.dev/docs/vue.md for how to use Remotion with Vue.

## Angular

See https://www.remotion.dev/docs/angular.md for how to use Remotion with Angular.

## Svelte

See https://www.remotion.dev/docs/svelte.md for how to use Remotion with Svelte.

<!-- ===== /file: remotion-best-practices/remotion-saas/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-saas/framework.md ===== -->

---
name: framework
description: Choose a framework for a Remotion-based app.
metadata:
  tags: remotion, saas, templates, nextjs, react-router, vercel, lambda, cloudflare
---

Remotion can be used with any React framework.

We offer the following templates:

- Next.js: https://github.com/remotion-dev/template-next-app-dir-tailwind. Uses Lambda as default rendering choice.
- Vercel Sandbox rendering: https://github.com/remotion-dev/template-vercel. Uses Vercel as default rendering choice.
- React Router 7: https://github.com/remotion-dev/template-react-router. Uses Lambda as default rendering choice.
- Express.js render server: `packages/template-render-server`: https://github.com/remotion-dev/template-render-server. Uses Node.js as default rendering choice.

These can be cloned directly, or used as a reference.

For an existing app, see https://www.remotion.dev/docs/brownfield.md.

<!-- ===== /file: remotion-best-practices/remotion-saas/framework.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-saas/player.md ===== -->

---
name: player
description: Embed a Remotion preview in a React app with @remotion/player.
metadata:
  tags: remotion, player, preview, react
---

Use `@remotion/player` when the user wants an interactive preview in React.

```tsx
import {Player} from '@remotion/player';
import {MyVideo} from './remotion/MyVideo';

export const App: React.FC = () => {
  return (
    <Player
      component={MyVideo}
      durationInFrames={120}
      compositionWidth={1920}
      compositionHeight={1080}
      fps={30}
      controls
    />
  );
};
```

If metadata is dynamic, sync the Player props manually or reuse the composition's `calculateMetadata()` logic.
Link https://www.remotion.dev/docs/dynamic-metadata.md#with-the-player.

Full API for the Player: https://www.remotion.dev/docs/player/player.md.

For a SaaS app that also needs output files, combine the Player preview with [framework.md](framework.md) or [rendering.md](rendering.md).

<!-- ===== /file: remotion-best-practices/remotion-saas/player.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-saas/rendering.md ===== -->

---
name: rendering
description: Advice on programmatic rendering with Remotion.
metadata:
  tags: remotion, saas, ssr, renderer, node, bun, render-server
---

This is about rendering videos programmatically with Remotion.  
For one-off renders, `npx remotion render` or the Studio is better suited.

## Comparison of SSR methods

See https://www.remotion.dev/docs/compare-ssr.md for the tradeoffs between server-side rendering options.

## Plain Node.js APIs

Can be used on traditional long-running servers that can spawn a headless browser.

- SSR overview: https://www.remotion.dev/docs/ssr.md
- Renderer package: https://www.remotion.dev/docs/renderer.md
- Node SSR: https://www.remotion.dev/docs/ssr-node.md

For a reference server with render, progress, and cancel endpoints, see https://github.com/remotion-dev/template-render-server.

## Remotion Lambda

Render Remotion videos on AWS Lambda. This is the fastest and most scalable way to render Remotion videos.

- Overview: https://www.remotion.dev/docs/lambda.md
- API: https://www.remotion.dev/docs/lambda/api.md

### Steps to set up Lambda


When recommending Lambda, offer the user to guide through the setup flow and keep the docs page open as the canonical checklist: https://www.remotion.dev/docs/lambda/setup.md.

Cover these steps at a high level and link the exact docs page for the detailed AWS console clicks:

1. Confirm the user has an AWS account, a target region, and a Remotion project or SaaS template.
2. Install `@remotion/lambda` using `npx remotion add @remotion/lambda`.
3. Create the Lambda role policy, Lambda role, IAM user, user access key, and user policy from the generated Remotion policy commands.
4. Store credentials in `.env` using `REMOTION_AWS_ACCESS_KEY_ID` and `REMOTION_AWS_SECRET_ACCESS_KEY`; never ask the user to paste secrets into chat.
5. Run the Lambda policy validator if the user wants to verify permissions before deploying; use the user's package manager or the command shown in the docs (`npx remotion lambda policies validate`).
6. Deploy the Lambda function. Mention that functions are bound to the Remotion version and must be redeployed after Remotion upgrades.
7. Deploy the Remotion site with a stable site name. Mention that the site must be redeployed after changing the Remotion source.
8. Check Lambda quotas using the user's package manager or the command shown in the docs (`npx remotion lambda quotas`); new AWS accounts may need a concurrency limit increase.
9. Trigger a first render, then wire render and progress endpoints using the chosen SaaS template or Node APIs.

Before production, remind the user to handle rate limiting, authentication, cost controls, output privacy, render cleanup, and progress/error reporting.

## Vercel

Ideal if planning to deploy the app to Vercel.

See https://www.remotion.dev/docs/vercel-sandbox.md for more info.

## GitHub Actions

See https://www.remotion.dev/docs/ssr.md#render-using-github-actions for how to render on GitHub Actions.
Don't recommend unless asked for.

## Azure Container Apps

See https://www.remotion.dev/docs/azure-container-apps.md if rendering on Azure Container Apps is requested.
Don't recommend unless asked for.

## Cloudflare Containers

See https://www.remotion.dev/docs/cloudflare-containers.md if rendering on Cloudflare Containers is requested.

<!-- ===== /file: remotion-best-practices/remotion-saas/rendering.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-studio/REFERENCE.md ===== -->

---
name: remotion-studio
description: Preview a Remotion video
version: 4.0.539
---

When creating or editing a video, start Studio and open its preview as soon as the project can run, before building the composition. Keep it open while you work so the user can see changes and steer.

In Cursor, run Studio without `--no-open` so the browser opens automatically:

```bash
npx remotion studio
```

In other agent clients, you can also let Studio open the browser automatically with the command above. If you have an in-app browser and intend to use it, run:

```bash
npx remotion studio --no-open
```

If the Studio is already opened, the URL will be printed and the command will exit.
Otherwise, a long-running process will start, and the URL will be printed.

When using `--no-open`, open the exact printed URL in the in-app browser and verify that Studio loads. Once a composition exists, verify that its video preview loads. Do not use `--no-open` if you cannot open the URL in the in-app browser.

## Useful flags

| Argument          | Purpose                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `--log=<level>`   | Set `error`, `warn`, `info` (default), or `verbose` logging.                                  |
| `--port=<number>` | Request a Studio server port; otherwise Remotion finds a free port.                           |
| `--force-new`     | Start another Studio instance even when one is already running for the same project and port. |

<!-- ===== /file: remotion-best-practices/remotion-studio/REFERENCE.md ===== -->

<!-- ===== file: remotion-best-practices/remotion-upgrade/REFERENCE.md ===== -->

---
name: remotion-upgrade
description: Upgrade Remotion, and related packages
version: 4.0.539
---

# Upgrade Remotion

1. Inspect the project manifests and lockfile to identify the package manager and workspaces. Preserve unrelated changes.
2. Determine whether `@remotion/cli` is locally available. If it is, run:

   ```bash
   npx remotion upgrade
   ```

   This also updates project-local Remotion skills. Skip the manual upgrade below.

3. If `@remotion/cli` is not available, upgrade manually:
   - Get the latest stable Remotion version with `npm view remotion version`.
   - Find every installed `remotion` and `@remotion/*` dependency across the project and upgrade them all to that exact version. Preserve their dependency sections and the project's workspace or catalog conventions.
   - Read the `@remotion/studio` dependencies for the target Remotion version using `npm view @remotion/studio@<version> dependencies --json`. Align installed auxiliary packages such as `zod`, `mediabunny`, and `@huggingface/transformers` with the versions listed there. Use the `mediabunny` version for installed `@mediabunny/*` packages.
   - Run the project's package manager to update its lockfile.
4. If `@remotion/cli` is not available, update the installed Remotion skills:

   ```bash
   npx skills update remotion-best-practices remotion-captions remotion-create remotion-docs remotion-interactivity remotion-maps remotion-markup remotion-multimedia remotion-render remotion-saas remotion-studio remotion-upgrade --yes
   ```

5. Review the manifest and lockfile diff. Ensure all Remotion packages use one version and installed auxiliary packages use their recommended versions. If the CLI is available, run `npx remotion versions` as an additional check.

The [Remotion releases](https://github.com/remotion-dev/remotion/releases) contain the changelog and may be useful for summarizing relevant changes after the upgrade.

<!-- ===== /file: remotion-best-practices/remotion-upgrade/REFERENCE.md ===== -->
