export const EASE = {
  outCubic: (t: number) => 1 - Math.pow(1 - t, 3),
  inCubic: (t: number) => t * t * t,
  inOut: (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outBack: (t: number) => 1 + 2.2 * Math.pow(t - 1, 3) + 1.4 * Math.pow(t - 1, 2),
};

export const lerp = (p: number, a: number, b: number) => a + (p - 0) * (b - a);

/** Cỡ chữ co lại theo độ dài chuỗi để không tràn khung. */
export const fitSize = (text: string, base: number, idealChars: number, min: number) =>
  Math.max(min, Math.min(base, (base * idealChars) / Math.max(text.length, 1)));

/**
 * Bề rộng ước (em) của một chuỗi Bebas Neue VN — trần em của từng nhóm ký tự, advance đo
 * bằng fontTools trên PS-Bebas-Neue-Regular-V1.1.otf: dấu cách 0,16; I i . , : ; ! ' ≤ 0,21;
 * M W m w % @ ≤ 0,59; chữ và số khác ≤ 0,43 (có dấu tiếng Việt cũng vậy). Đổi font thì đo lại
 * (test_picture render kiểm). Tít hook (B1) và từ khoá CTA (B2) dùng.
 */
export const bebasEm = (text: string) =>
  [...text].reduce(
    (em, ch) => em + (ch === " " ? 0.16 : "Ii.,:;!'".includes(ch) ? 0.21 : "MWmw%@".includes(ch) ? 0.59 : 0.43),
    0
  );

/**
 * B2: cỡ ≤ `size` sao cho từ dài nhất (một từ không xuống dòng được) rộng ≤ `maxW`, biết mỗi
 * ký tự rộng tối đa `em` em — trần em/ký tự của font, hiệu chỉnh bằng render (Subtitle.tsx).
 * `extraEm` (D2, 1.1.1): phần đệm nét chữ của ô từ (l + r lớn nhất, src/ink.ts) cộng thêm.
 */
export const wordCap = (words: string[], size: number, em: number, maxW: number, extraEm = 0) =>
  Math.min(size, maxW / (em * Math.max(1, ...words.map((w) => w.length)) + extraEm));

/** Nhiễu tất định (mulberry32) – dùng cho grain/jitter, không đổi giữa các lần render. */
export const rand = (seed: number) => {
  let t = (seed + 0x6d2b79f5) >>> 0;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
