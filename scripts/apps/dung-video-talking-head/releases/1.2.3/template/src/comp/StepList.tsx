import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { SAFE, STEPS } from "../data/script";
import { C, FONT, FPS } from "../theme";
import { EASE } from "../anim";

const ENTER = 10; // frame thẻ trượt vào (đạt 90 % ở frame 6 = sync_frame.card)
const ITEM = 9;   // frame một mục hiện xong (đạt 90 % ở frame 5 = sync_frame.item)
const OUT = 8;

/**
 * Bảng 4 mục dựng dần theo lời nói: mục mới sáng, mục cũ lùi về 50% —
 * đổi nhịp so với subtitle 3 tầng để đoạn liệt kê không đọc như slide.
 * Thẻ (tính cả viền) rộng SAFE.sub_max_w, đáy ở SAFE.sub_bottom_px — nằm trong
 * hộp chữ (B14). probe: bỏ bóng đổ, backdrop-filter, bóng chữ; giữ nền, viền thẻ
 * và chữ (Ruling R26) — blur chuyển động vẫn đo (Ruling R29).
 */
export const StepList: React.FC<{ probe?: boolean }> = ({ probe = false }) => {
  const frame = useCurrentFrame();
  if (!STEPS) return null;
  const { in: IN_AT, out: OUT_AT, items, title } = STEPS;
  if (frame < IN_AT * FPS || frame > OUT_AT * FPS + OUT) return null;

  const enter = EASE.outCubic(Math.min(1, (frame - IN_AT * FPS) / ENTER));
  const q = Math.min(1, Math.max(0, (frame - OUT_AT * FPS) / OUT));
  const last = items.reduce((acc, s, i) => (frame >= s.show * FPS ? i : acc), -1);

  return (
    <AbsoluteFill
      style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: SAFE.sub_bottom_px }}
    >
      <div
        style={{
          width: SAFE.sub_max_w,
          boxSizing: "border-box",
          padding: "34px 40px 40px",
          borderRadius: 34,
          background: "rgba(10,10,16,0.56)",
          border: "1px solid rgba(255,255,255,0.14)",
          backdropFilter: probe ? "none" : "blur(22px)",
          boxShadow: probe ? "none" : "0 30px 90px rgba(0,0,0,.5)",
          opacity: enter * (1 - q),
          transform: `translateY(${(1 - enter) * 36 - 26 * q}px) scale(${0.97 + enter * 0.03})`,
          filter: `blur(${(1 - enter) * 8 + q * 8}px)`,
        }}
      >
        <div
          style={{
            fontFamily: FONT.bebas,
            fontSize: 34,
            letterSpacing: "0.16em",
            color: C.gold,
            marginBottom: 22,
          }}
        >
          {title}
        </div>

        {items.map((s, i) => {
          const p = EASE.outCubic(
            Math.min(1, Math.max(0, (frame - s.show * FPS) / ITEM))
          );
          const active = i === last;
          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 22,
                padding: "12px 0",
                opacity: p * (active ? 1 : 0.46),
                transform: `translateX(${(1 - p) * 46}px)`,
                filter: `blur(${(1 - p) * 9}px)`,
                transition: "none",
              }}
            >
              <span
                style={{
                  fontFamily: FONT.bebas,
                  fontSize: 54,
                  color: active ? C.gold : "rgba(255,255,255,.6)",
                  minWidth: 62,
                }}
              >
                0{i + 1}
              </span>
              <span
                style={{
                  fontFamily: FONT.display,
                  fontWeight: 700,
                  fontSize: 58,
                  color: "#fff",
                  lineHeight: 1.1,
                  textShadow: probe ? "none" : "0 4px 20px rgba(0,0,0,.6)",
                }}
              >
                {s.label}
              </span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
