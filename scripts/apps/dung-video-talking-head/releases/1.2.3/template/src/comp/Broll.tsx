import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import { EASE } from "../anim";
import { BROLL, type Broll as Slot } from "../data/script";

/**
 * B-roll cắt cảnh toàn màn hình (spec 1.2.0 §8, B08 full, B10 cắt cứng): mỗi slot một Sequence phủ kín khung,
 * vẽ giữa Footage và Grade (B13). Ảnh tĩnh đẩy scale push[0] → push[1] suốt slot (B09) + nảy vào settle_f frame
 * đầu (như kick cú cắt của Footage). Clip: phát nguyên, không đẩy. Mọi trị số đến từ khoá hình (rules.json).
 */
const Still: React.FC<{ b: Slot }> = ({ b }) => {
  const f = useCurrentFrame(); // đếm từ đầu Sequence
  const n = b.f_out - b.f_in;
  const p = n > 1 ? Math.min(1, f / (n - 1)) : 1;
  const settle = f < b.settle_f ? (1 - f / b.settle_f) * b.settle_amp : 0;
  const scale = b.push[0] + (b.push[1] - b.push[0]) * EASE.inOut(p) + settle;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${scale})` }}>
        <Img src={staticFile(b.file)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Clip: React.FC<{ b: Slot }> = ({ b }) => (
  <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
    <OffthreadVideo src={staticFile(b.file)} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
  </AbsoluteFill>
);

export const Broll: React.FC = () => (
  <>
    {BROLL.map((b) => (
      <Sequence key={b.id} from={b.f_in} durationInFrames={b.f_out - b.f_in} premountFor={30}>
        {b.media === "clip" ? <Clip b={b} /> : <Still b={b} />}
      </Sequence>
    ))}
  </>
);
