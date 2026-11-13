import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";
import { FPS } from "../theme";
import { EASE } from "../anim";
import { DURATION_S, SHOTS } from "../data/script";

/**
 * Camera 2.5D trên một cú quay tĩnh: mỗi "shot" là một cỡ cảnh khác nhau
 * (cắt cứng ở đầu shot) cộng một chuyển động chậm bên trong shot —
 * không khung hình nào đứng yên, và cắt cỡ cảnh tạo cảm giác nhiều máy.
 */
const END = DURATION_S;

export const Footage: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;

  let i = 0;
  for (let k = 0; k < SHOTS.length; k++) if (t >= SHOTS[k].t) i = k;
  const shot = SHOTS[i];
  const next = SHOTS[i + 1]?.t ?? END;

  const p = Math.min(1, Math.max(0, (t - shot.t) / (next - shot.t)));
  const scale = shot.s0 + (shot.s1 - shot.s0) * EASE.inOut(p);

  // Dịch khung bị chặn bởi phần dư sau khi phóng, tránh lòi mép đen.
  const slack = (scale - 1) / 2;
  const clamp = (v: number) => Math.max(-slack, Math.min(slack, v));
  const x = clamp(shot.x ?? 0) * 100;
  const y = clamp(shot.y ?? 0) * 100;

  // Nhịp cắt: 4 frame đầu shot nảy nhẹ + mờ 1 nhịp, đọc ra "cú cắt" chứ không phải "zoom".
  // P7 (1.1.1): không mờ dần từ đen — frame 0 đã thấy người nói, sắc nét.
  const cutF = i > 0 ? frame - shot.t * FPS : -1; // R24: shot 0 là khung mở, không nảy/mờ
  const kick = cutF >= 0 && cutF < 5 ? (1 - cutF / 5) * 0.018 : 0;
  const cutBlur = cutF >= 0 && cutF < 3 ? (1 - cutF / 3) * 5 : 0;

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <AbsoluteFill
        style={{
          transform: `translate(${x}%, ${y}%) scale(${scale + kick})`,
          transformOrigin: "50% 32%",
          filter: `blur(${cutBlur}px) saturate(1.06) contrast(1.06) brightness(${1 + kick * 2})`,
        }}
      >
        <OffthreadVideo
          src={staticFile("master.mp4")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          pauseWhenBuffering
          muted
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
