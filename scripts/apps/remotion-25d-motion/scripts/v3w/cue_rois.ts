// tools/v3w/cue_rois.ts — vùng đo (ROI, px màn 1920×1080) và cách đo đỉnh thị giác quanh từng cue của V3, tính từ mã cảnh
// (vị trí thế giới chiếu qua camera thật). tools/v3w/cue_visual.py đọc JSON này, giải mã MP4 và tìm frame đỉnh.
//   rise: frame màu `color` tăng nhanh nhất (diện tích nở/quét) · max / min: frame nhiều / ít màu nhất · bump: đỉnh bướu sau
//   khi trừ xu hướng tuyến tính (thở phì chồng lên nhịp thở idle) · onset: frame đầu có
//   màu vượt ngưỡng · drop: frame đầu màu dưới ngưỡng · diff: frame thay đổi mạnh nhất (khóa chữ + đập camera).
//   norm: chia số điểm cho s₁² của camera (bỏ phần đổi cỡ do zoom). Cue không đo được trên hình (chồng lớp trắng trên trắng)
//   thì tính đỉnh giải tích từ mã (analytic).
// Chạy:  node node_modules/tsx/dist/cli.mjs tools/v3w/cue_rois.ts <out.json>
import { writeFileSync } from "node:fs";
import { mascotExtentPx } from "../../src/fx/mascotAnchor";
import { project, s1Of } from "../../src/v2w/core/camera";
import { CamTrack, camAt } from "../../src/v2w/core/camTrack";
import { SP, springAt } from "../../src/v2w/core/spring";
import type { Pt } from "../../src/v2w/core/time";
import { BO_MAIN, boMainPoseAt } from "../../src/v3w/bo";
import { MAIN_TRACK, OUTRO_TRACK } from "../../src/v3w/camera";
import { G_PLAN, G_Q, G_RO, OUTRO_TEXT } from "../../src/v3w/groups";
import { CARD, LEAK_STEPS, numCenter, slotOf } from "../../src/v3w/layout";
import { CARD_LOOK } from "../../src/v3w/ui/StepCard";
import { ejectAt } from "../../src/v3w/scenes/rowState";
import { V3 } from "../../src/v3w/timing";

type Roi = { cue: string; t: number; kind: "rise" | "max" | "min" | "bump" | "onset" | "drop" | "diff"; color: string;
  box: number[]; win: [number, number]; norm?: { from: number; s: number[] }; accept?: [number, number] };
type Analytic = { cue: string; t: number; peak: number; note: string; info?: boolean };

const box = (track: CamTrack, t: number, pts: Pt[], pad = 0): number[] => {
  const cam = camAt(t, track);
  const p = pts.map((q) => project(cam, 1, q));
  return [Math.min(...p.map((q) => q[0])) - pad, Math.min(...p.map((q) => q[1])) - pad, Math.max(...p.map((q) => q[0])) + pad,
    Math.max(...p.map((q) => q[1])) + pad];
};
const around = (track: CamTrack, t: number, c: Pt, hw: number, hh: number): number[] =>
  box(track, t, [[c[0] - hw, c[1] - hh], [c[0] + hw, c[1] + hh]]);
const sAt = (track: CamTrack, from: number, to: number): { from: number; s: number[] } => {
  const s: number[] = [];
  for (let f = Math.round(from * 60); f <= Math.round(to * 60); f++) s.push(s1Of(camAt(f / 60, track)));
  return { from: Math.round(from * 60), s };
};
const hud = (g: typeof G_Q, line0: number, lines: number, w: number): number[] =>
  [g.slot.left - 20, g.slot.top + line0 * 1.32 * g.slot.size - 0.1 * g.slot.size, g.slot.left + w,
    g.slot.top + (line0 + lines) * 1.32 * g.slot.size + 0.2 * g.slot.size];

const rois: Roi[] = [
  { cue: "tick-accent-1", t: V3.ACCENT_1, kind: "rise", color: "white", box: hud(G_Q, 1, 1, 980), win: [1.35, 1.75] },
  { cue: "tick-accent-2", t: V3.ACCENT_2, kind: "rise", color: "white", box: hud(G_RO, 1, 1, 560), win: [7.85, 8.25] },
  { cue: "tick-accent-3", t: V3.ACCENT_3, kind: "rise", color: "blue", box: hud(G_PLAN, 1, 2, 690), win: [13.85, 14.25] },
  ...LEAK_STEPS.map((i, k): Roi => {
    const t = k === 0 ? V3.ALERT_1 : V3.ALERT_2;
    return { cue: k === 0 ? "blip-alert-1" : "blip-alert-2", t, kind: "onset", color: "red",
      box: around(MAIN_TRACK, t, slotOf(i), CARD.w / 2 + 30, CARD.h / 2 + 30), win: [t - 0.15, t + 0.2] };
  }),
  // thở phì: diện tích ĐÁY chữ U của Bò (38 % dưới — hạt bay lên từ khe trán không vào vùng) chia s₁² — đỉnh phồng
  (() => {
    const e = mascotExtentPx(BO_MAIN, boMainPoseAt(V3.SNORT));
    // khoảng nhận [0; +3] f60 = "đỉnh phồng trùng 8,75–8,80" (lead chốt sau rà chéo Q5-V3)
    return { cue: "snort", t: V3.SNORT, kind: "bump" as const, color: "white", accept: [0, 3] as [number, number],
      box: box(MAIN_TRACK, V3.SNORT, [[e.minX, e.minY + 0.62 * (e.maxY - e.minY)], [e.maxX, e.maxY]], 30), win: [8.62, 8.9] as [number, number],
      norm: sAt(MAIN_TRACK, 8.62, 8.9) };
  })(),
  ...LEAK_STEPS.map((i, k): Roi => {
    const s = slotOf(i);
    const c: Pt = [s[0] + CARD.w / 2 - CARD_LOOK.chipInset, s[1] - CARD.h / 2 + CARD_LOOK.chipInset];
    return { cue: `tick-fix#${k + 1}`, t: V3.FIX, kind: "rise", color: "blue", box: around(MAIN_TRACK, V3.FIX, c, 60, 60),
      win: [8.85, 9.2] };
  }),
  { cue: "whoosh-gather/paper", t: V3.DOC, kind: "min", color: "white",
    box: box(MAIN_TRACK, V3.DOC, [[slotOf(0)[0] - CARD.w, slotOf(0)[1] - CARD.h], [slotOf(4)[0] + CARD.w, slotOf(4)[1] + CARD.h]]),
    win: [9.85, 10.15] },
  ...V3.NUMS.map((t, k): Roi => ({ cue: `tick-num-${k + 1}`, t, kind: "rise", color: "blue",
    box: around(MAIN_TRACK, t, numCenter(k), 88, 88), win: [t - 0.2, t + 0.25] })),
  { cue: "whoosh-dive", t: V3.DIVE, kind: "drop", color: "white", box: [0, 0, 1920, 1080], win: [14.85, 15.1] },
  { cue: "hit-logo", t: V3.LOGO, kind: "diff", color: "white",
    box: box(OUTRO_TRACK, V3.LOGO, [[OUTRO_TEXT.title.left, OUTRO_TEXT.title.top - 30],
      [OUTRO_TEXT.title.left + 780, OUTRO_TEXT.title.top + 200]]), win: [15.35, 15.65] },
  { cue: "tick-cta", t: V3.CTA_LOCK, kind: "max", color: "white",
    box: box(OUTRO_TRACK, V3.CTA_LOCK, [[OUTRO_TEXT.cta.left - 80, OUTRO_TEXT.cta.centerY - 200],
      [OUTRO_TEXT.cta.left + 1000, OUTRO_TEXT.cta.centerY + 200]]), win: [17.55, 18.1], norm: sAt(OUTRO_TRACK, 17.55, 18.1) },
];

/** Đỉnh giải tích của khối i (khối trắng trên Bò trắng, không đo được bằng màu): frame tốc độ nở lớn nhất, quét 0–0,35 s
 *  sau lúc khối hiện (rà chéo vòng 2: quét 0–98 ms trước đây cắt mất đỉnh diện tích ≈ 128 ms của lò xo MORPH).
 *  edge: tốc độ lớn lên của CẠNH khối, d(scale)/dt — cách đo của V2, dùng làm chuẩn khớp;
 *  area: tốc độ tăng DIỆN TÍCH, d(scale²)/dt — chỉ báo. */
const growPeak = (i: number, pow: 1 | 2): number => {
  const sc = (tt: number): number => (0.12 + 0.88 * springAt(tt, ejectAt(i), SP.MORPH)) ** pow;
  let best = { v: -1, t: 0 };
  for (let f = 0; f < 3500; f++) {
    const t = ejectAt(i) + f / 10000;
    const v = sc(t + 5e-5) - sc(t - 5e-5);
    if (v > best.v) best = { v, t };
  }
  return best.t;
};
const analytic: Analytic[] = [
  ...V3.EJECT.map((t, i): Analytic => ({ cue: `tick-eject-${i + 1}`, t, peak: growPeak(i, 1),
    note: "cạnh khối lớn nhanh nhất, d(scale)/dt (cách V2; giải tích từ mã)" })),
  ...V3.EJECT.map((t, i): Analytic => ({ cue: `tick-eject-${i + 1} (diện tích)`, t, peak: growPeak(i, 2), info: true,
    note: "diện tích khối tăng nhanh nhất, d(scale²)/dt (chỉ báo)" })),
  { cue: "chime-hoi", t: V3.TILT, peak: V3.TILT, note: "Bò bắt đầu nghiêng đầu (spring MORPH khởi đúng mốc)" },
];

const out = process.argv[2];
if (!out) throw new Error("cue_rois: thiếu đường dẫn JSON đầu ra");
writeFileSync(out, JSON.stringify({ rois, analytic }, null, 2), "utf-8");
console.log(`cue_rois: ${rois.length} ROI, ${analytic.length} giải tích → ${out}`);
