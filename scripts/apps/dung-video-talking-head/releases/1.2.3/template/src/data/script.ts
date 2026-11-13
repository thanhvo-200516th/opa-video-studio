// GIỮ CHỖ — BUILD sinh bản thật từ picture_lock.json (thlib.picture.write_script_ts).
export type Word = { t: string; show: number; display_shift_s?: number; glue?: boolean };
export type Block = {
  id: string;
  style: "script" | "stomp" | "quote";
  color: "warn" | "gold" | "ink" | null;
  accent: number | null;
  synced: boolean;
  out: number;
  exit_f: number;
  hero_row?: boolean;
  top: Word[]; hero: Word[]; bottom: Word[];
};
export type Steps = { title: string; in: number; out: number; items: { label: string; show: number }[] };
export type Shot = { t: number; s0: number; s1: number; x?: number; y?: number };
export type Hook = { text: string; color: "warn" | "gold" | "ink"; land: number; out: number; end: number };
export type Cta = { label: string; keyword: string; show: number };
export type Safe = {
  text_x_min: number; text_x_max: number; text_y_min: number; text_y_max: number;
  sub_bottom_px: number; sub_max_w: number; subject_y_min: number; subject_y_max: number;
};
export type Broll = { id: string; f_in: number; f_out: number; file: string; media: "still" | "clip"; push: [number, number]; settle_f: number; settle_amp: number };

export const FPS = 30;
export const DURATION_F = 300;
export const DURATION_S = 10;
export const HOOK: Hook | null = null;
export const BLOCKS: Block[] = [];
export const STEPS: Steps | null = null;
export const SHOTS: Shot[] = [{ t: 0, s0: 1, s1: 1.04 }];
export const CTA: Cta | null = null;
export const SAFE: Safe = {
  text_x_min: 140, text_x_max: 940, text_y_min: 270, text_y_max: 1436,
  sub_bottom_px: 484, sub_max_w: 800, subject_y_min: 270, subject_y_max: 1080,
};
export const BROLL: Broll[] = [];
