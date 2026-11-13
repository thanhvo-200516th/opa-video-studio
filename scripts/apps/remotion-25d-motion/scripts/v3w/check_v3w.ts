// tools/v3w/check_v3w.ts — kiểm số của V3 (thuần, không render):
//   1) ≤ 9 chữ mỗi frame (gồm nhãn UI); 2) thời gian đứng đọc (nhóm lời, nhãn bước đủ chữ ≥ 0,4 s, tiêu đề tài liệu, chữ
//   outro); 3) chặng camera (dời góc khung, vọt, nhảy vận tốc ở khóa); 4) camera không khựng (frame < 15 px/s mỗi ô 2 s);
//   5) Bò cách mép khung ≥ 65 px khi có mặt; kính không chạm Bò; 6) tờ tài liệu phủ kín khung khi lớp nền xanh tắt.
// Chạy:  node node_modules/tsx/dist/cli.mjs tools/v3w/check_v3w.ts [--json out.json]
// Exit:  0 đạt, 1 có mục trượt.
import { writeFileSync } from "node:fs";
import { mascotExtentPx } from "../../src/fx/mascotAnchor";
import { camLegs, legsReport } from "../../src/v2w/core/camLegs";
import { project } from "../../src/v2w/core/camera";
import { camAt, camSpeed } from "../../src/v2w/core/camTrack";
import { BO_MAIN, HOP, boMainPoseAt } from "../../src/v3w/bo";
import { MAIN_LEGS, MAIN_TRACK, OUTRO_LEGS, OUTRO_TRACK } from "../../src/v3w/camera";
import { V3_COPY } from "../../src/v3w/copy";
import { HUD_GROUPS } from "../../src/v3w/groups";
import { BO_MARGIN, LENS, STEP_COUNT } from "../../src/v3w/layout";
import { titleGlyph } from "../../src/v3w/scenes/docState";
import { PAGE_COVERS } from "../../src/v3w/scenes/MainWorld";
import { pageAt } from "../../src/v3w/scenes/docState";
import { subGlyph } from "../../src/v3w/scenes/outroText";
import { labelInLens, lensAt } from "../../src/v3w/scenes/rowState";
import { V3 } from "../../src/v3w/timing";
import { v3WordCount, v3WordsAt } from "../../src/v3w/words";

const fails: string[] = [];
const FPS = V3.FPS;
const FRAMES = V3.TOTAL * FPS;
const ts = (from: number, to: number): number[] => {
  const out: number[] = [];
  for (let f = Math.ceil(from * FPS); f < to * FPS; f++) out.push(f / FPS);
  return out;
};
/** Đoạn liên tục dài nhất (giây) mà pred đúng trong [from; to). */
const longestRun = (from: number, to: number, pred: (t: number) => boolean): { len: number; at: number } => {
  let best = { len: 0, at: from };
  let start = -1;
  ts(from, to + 1 / FPS).forEach((t) => {
    if (pred(t) && t < to) { if (start < 0) start = t; } else if (start >= 0) {
      if (t - start > best.len) best = { len: t - start, at: start };
      start = -1;
    }
  });
  return best;
};

// 1) ≤ 9 chữ
let maxWords = 0;
let maxAt = 0;
for (let f = 0; f < FRAMES; f++) {
  const t = f / FPS;
  const n = v3WordCount(t);
  if (n > maxWords) { maxWords = n; maxAt = t; }
  if (n > 9) fails.push(`${t.toFixed(3)} s: ${n} chữ (${v3WordsAt(t).filter((w) => w.visible >= 0.5).map((w) => w.text).join(" ")})`);
}
console.log(`1) chữ trên khung: tối đa ${maxWords} ở ${maxAt.toFixed(3)} s → ${maxWords <= 9 ? "ĐẠT" : "TRƯỢT"}`);

// 2) đứng đọc
HUD_GROUPS.forEach(({ group: g }) => {
  const read = g.exit - g.enter;
  console.log(`2) ${g.lines.map((l) => l.text).join(" / ")}: ${g.enter.toFixed(2)} → ${g.exit.toFixed(2)} (${read.toFixed(2)} s)`);
  if (read < 1.5) fails.push(`nhóm ${g.id} chỉ ${read.toFixed(2)} s`);
});
for (let i = 0; i < STEP_COUNT; i++) {
  const r = longestRun(4.5, 10, (t) => labelInLens(i, t));
  console.log(`2) nhãn "${V3_COPY.steps[i]}": đủ chữ liên tục dài nhất ${r.len.toFixed(2)} s từ ${r.at.toFixed(2)}`);
  if (r.len < 0.4) fails.push(`nhãn ${V3_COPY.steps[i]} chỉ ${r.len.toFixed(2)} s`);
}
const alertLabel = (i: number, t: number): boolean => labelInLens(i, t);
console.log(`2) kính trên Tin nhắn lúc 7,00: ${alertLabel(1, V3.ALERT_1)}; trên Chăm sóc lúc 7,50: ${alertLabel(4, V3.ALERT_2)}`);
if (!alertLabel(1, V3.ALERT_1) || !alertLabel(4, V3.ALERT_2)) fails.push("kính không đứng trên khối đúng blip");
/** Đứng đọc CHẶT (cách đo của rà chéo): mọi chữ yên (|y| ≤ 0,8 % chiều cao mask, hiện đủ) — từ lúc chữ cuối yên tới lúc
 *  chữ đầu nhấc. */
const still = (g: { y: number; opacity: number }): boolean => Math.abs(g.y) <= 0.008 && g.opacity >= 0.99;
const title = longestRun(10, 12.5, (t) => Array.from({ length: 8 }, (_, k) => titleGlyph(k, t)).every(still));
console.log(`2) tiêu đề tài liệu đứng đọc chặt ${title.len.toFixed(2)} s từ ${title.at.toFixed(2)}`);
if (title.len < 1.5) fails.push(`tiêu đề tài liệu chỉ ${title.len.toFixed(2)} s`);
const sub = longestRun(15.2, 17.6, (t) => [0, 1, 2].every((k) => still(subGlyph(k, t))));
console.log(`2) "Cho doanh nghiệp" đứng đọc chặt ${sub.len.toFixed(2)} s từ ${sub.at.toFixed(2)}`);
if (sub.len < 1.5) fails.push(`"Cho doanh nghiệp" chỉ ${sub.len.toFixed(2)} s`);
const titleOut = ts(11.9, 12.4).filter((t) => Array.from({ length: 8 }, (_, k) => titleGlyph(k, t)).some((g) => g.visible > 0.02));
console.log(`2) tiêu đề còn hiện tới ${titleOut.length ? titleOut[titleOut.length - 1].toFixed(3) : "—"} s (cần rút xong ≤ 12,10)`);

// 3) chặng camera
const report = (name: string, keys: ReturnType<typeof camLegs>): void => {
  const r = legsReport(keys);
  r.legs.forEach((l) => console.log(`3) ${name} ${l.from.toFixed(2)}→${l.to.toFixed(2)}: góc ${l.cornerPx.toFixed(0)} px · vọt `
    + `${l.overshootPx.toFixed(1)} · tốc độ ${l.minSpeed.toFixed(0)}–${l.peakSpeed.toFixed(0)} px/s`));
  console.log(`3) ${name}: nhảy vận tốc max ${r.maxJump.toFixed(2)} px/f60, vọt max ${r.maxOvershootPx.toFixed(1)} px`);
  if (r.maxJump > 2) fails.push(`${name}: nhảy vận tốc ${r.maxJump.toFixed(2)} px/f60 ở khóa`);
};
report("CHÍNH", camLegs(MAIN_LEGS));
report("OUTRO", camLegs(OUTRO_LEGS));

// 4) camera không khựng (chỉ báo; chỉ số thật đo trên MP4)
for (let w = 0; w < V3.TOTAL; w += 2) {
  const slow = ts(w, w + 2).filter((t) => camSpeed(t, t < V3.DIVE ? MAIN_TRACK : OUTRO_TRACK) < 0.25).length;
  console.log(`4) ô [${w}; ${w + 2}): ${slow} frame camera < 15 px/s`);
}

// 5) Bò cách mép, kính không chạm Bò
const boBox = (t: number): { x0: number; y0: number; x1: number; y1: number } => {
  const e = mascotExtentPx(BO_MAIN, boMainPoseAt(t));
  const cam = camAt(t, MAIN_TRACK);
  const pts = [[e.minX, e.minY], [e.maxX, e.minY], [e.minX, e.maxY], [e.maxX, e.maxY]].map((p) => project(cam, 1, p as [number, number]));
  return { x0: Math.min(...pts.map((p) => p[0])), y0: Math.min(...pts.map((p) => p[1])),
    x1: Math.max(...pts.map((p) => p[0])), y1: Math.max(...pts.map((p) => p[1])) };
};
let minMargin = { m: Infinity, t: 0 };
const marginBad: number[] = [];
ts(0, HOP.dipAt).filter((t) => t < 3.5 || t >= 4.9).forEach((t) => {
  const b = boBox(t);
  const m = Math.min(b.x0, b.y0, 1920 - b.x1, 1080 - b.y1);
  if (m < minMargin.m) minMargin = { m, t };
  if (m < BO_MARGIN) marginBad.push(t);
});
console.log(`5) Bò cách mép nhỏ nhất ${minMargin.m.toFixed(0)} px ở ${minMargin.t.toFixed(3)} s; dưới ${BO_MARGIN} px: ${marginBad.length} frame`
  + (marginBad.length ? ` (${marginBad[0].toFixed(2)}–${marginBad[marginBad.length - 1].toFixed(2)})` : ""));
if (marginBad.length) fails.push(`Bò sát mép ${marginBad.length} frame`);
let lensGap = { g: Infinity, t: 0 };
ts(4.6, 9.5).forEach((t) => {
  const { c, k } = lensAt(t);
  if (k < 0.05) return;
  const cam = camAt(t, MAIN_TRACK);
  const lc = project(cam, 1, c);
  const r = LENS.r * k * (cam.zoom / (1 - cam.z));
  const b = boBox(t);
  const dx = Math.max(b.x0 - lc[0], 0, lc[0] - b.x1);
  const dy = Math.max(b.y0 - lc[1], 0, lc[1] - b.y1);
  const g = Math.hypot(dx, dy) - r;
  if (g < lensGap.g) lensGap = { g, t };
});
console.log(`5) khe kính – khung bao Bò nhỏ nhất ${lensGap.g.toFixed(0)} px ở ${lensGap.t.toFixed(3)} s (khung bao: chỉ báo)`);

// 6) tờ tài liệu phủ kín khung khi lớp nền xanh tắt
const pageGaps = ts(PAGE_COVERS.from, V3.DIVE).filter((t) => {
  const p = pageAt(t);
  if (!p) return true;
  const cam = camAt(t, MAIN_TRACK);
  const a = project(cam, 1, [p.x0 + p.r, p.y0 + p.r]);
  const b = project(cam, 1, [p.x1 - p.r, p.y1 - p.r]);
  return !(a[0] <= -4 && a[1] <= -4 && b[0] >= 1924 && b[1] >= 1084);
});
console.log(`6) tờ tài liệu không phủ kín khung: ${pageGaps.length} frame trong [${PAGE_COVERS.from}; ${V3.DIVE})`);
if (pageGaps.length) fails.push(`tờ không phủ kín ${pageGaps.length} frame (đầu ${pageGaps[0].toFixed(3)})`);

const json = process.argv.indexOf("--json");
if (json > 0) writeFileSync(process.argv[json + 1], JSON.stringify({ maxWords, maxAt, title, sub, minMargin, lensGap, fails }, null, 2),
  "utf-8");
fails.forEach((f) => console.log(`  TRƯỢT ${f}`));
console.log(fails.length ? `TRƯỢT (${fails.length})` : "ĐẠT");
process.exit(fails.length ? 1 : 0);
