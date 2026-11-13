import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { Fonts } from "../fonts";
import { Footage } from "./Footage";
import { Broll } from "./Broll";
import { Grade } from "./Grade";
import { StepList } from "./StepList";
import { Subtitle } from "./Subtitle";
import { Cta } from "./Cta";
import { Hook } from "./Hook";

/**
 * Remotion chỉ render hình: tiếng (giọng + SFX + nhạc nền) trộn sẵn trên trục
 * vo-clean thành public/mix.wav và ghép bằng ffmpeg. <Audio> ở đây chỉ để nghe
 * khi xem Studio — bản render thật chạy với --muted.
 */
export const Main: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Fonts />
    <Footage />
    <Broll />
    <Grade />
    <StepList />
    <Subtitle />
    <Hook />
    <Cta />
    <Audio src={staticFile("mix.wav")} />
  </AbsoluteFill>
);

/**
 * Prop của TextOnly. probe = true: mọi lớp chữ tắt hiệu ứng mềm — quầng (bản sao
 * nhoè), drop/text-shadow, box-shadow, backdrop-filter và blur chuyển động — chỉ
 * còn nét chữ và nền/viền thẻ, pill (vị trí, độ mờ giữ nguyên). check_text_safe
 * đo đúng phần đó (Ruling R26). hook = false: không vẽ tít hook (ảnh dò che mặt của
 * cổng face_safe — tít hook toàn khung ≤ 1,5 s được miễn, spec 1.1.1 §7.4).
 */
export type TextOnlyProps = { probe: boolean; hook?: boolean };

/** Chỉ các lớp chữ, không nền — check_text_safe render PNG trong suốt của nó (B14). */
export const TextOnly: React.FC<TextOnlyProps> = ({ probe, hook }) => (
  <AbsoluteFill>
    <Fonts />
    <StepList probe={probe} />
    <Subtitle probe={probe} />
    {hook !== false ? <Hook probe={probe} /> : null}
    <Cta probe={probe} />
  </AbsoluteFill>
);
