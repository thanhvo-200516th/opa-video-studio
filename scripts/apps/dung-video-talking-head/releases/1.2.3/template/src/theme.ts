import { FPS as LOCK_FPS, DURATION_F } from "./data/script";
export const FPS = LOCK_FPS;
export const W = 1080;
export const H = 1920;
export const DUR = DURATION_F;

export const sec = (t: number) => Math.round(t * FPS);

export const C = {
  ink: "#ffffff",
  dim: "rgba(255,255,255,0.86)",
  heroA: "#b9a6ff", // tím sáng
  heroB: "#7c6cf5", // tím đậm
  heroC: "#5ec8ff", // xanh cyan (điểm nhấn)
  warn: "#ff5d73",
  gold: "#ffcf6b",
  shadow: "0 6px 30px rgba(0,0,0,0.55), 0 2px 8px rgba(0,0,0,0.45)",
};

/** Tên màu dùng trong edit.json → mã màu. */
export const NAMED = { warn: C.warn, gold: C.gold, ink: C.ink } as const;

export const FONT = {
  body: "'BeVietnamPro', system-ui, sans-serif",
  bodyBold: "'BeVietnamProBold', system-ui, sans-serif",
  black: "'BeVietnamProBlack', system-ui, sans-serif",
  display: "'DTPhudu', system-ui, sans-serif",
  displayBlack: "'DTPhuduBlack', system-ui, sans-serif",
  bebas: "'BebasNeueVN', Impact, sans-serif",
  script: "'Merolat', cursive",
  script2: "'HeyMonday', cursive",
  heroAlt: "'BeVietnamProBlackItalic', system-ui, sans-serif",
};

/**
 * Font của dòng hero kiểu "script".
 * FONT.script  = Merolat — didone nghiêng mảnh, gần bản tham chiếu nhất.
 * FONT.heroAlt = Be Vietnam Pro Black Italic — đậm, dễ đọc hơn trên nền rối.
 * Đổi một dòng này là đổi toàn bộ phim.
 */
export const HERO_SCRIPT_FONT = FONT.heroAlt;
