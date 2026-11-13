import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { FONT, FPS, NAMED } from "../theme";
import { HOOK, SAFE } from "../data/script";
import { EASE, bebasEm } from "../anim";

const BASE = 460;  // cỡ tít tối đa (1.0.0)
const PUSH = 0.05; // đẩy nhẹ 5 % giữa land và out

/**
 * B1: cỡ tít co theo bề rộng chữ để lúc đẩy lớn nhất (×(1 + PUSH) ở frame out — check_text_safe
 * dò cả frame đó) chữ vẫn rộng ≤ SAFE.sub_max_w; tít ngắn (vd "20") giữ BASE.
 */
const hookSize = (text: string) => Math.min(BASE, SAFE.sub_max_w / ((1 + PUSH) * bebasEm(text)));

/**
 * Cú mở: con số chiếm gần hết khung, giữ một nhịp rồi thu nhỏ + nhoè
 * rơi xuống chỗ dòng phụ — bàn giao cho subtitle thay vì cắt phụt.
 * probe: bỏ quầng sáng và bóng chữ, chỉ còn nét chữ (Ruling R26) — blur chuyển
 * động vẫn đo (Ruling R29).
 */
export const Hook: React.FC<{ probe?: boolean }> = ({ probe = false }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!HOOK || t > HOOK.end) return null;
  const { land: HOLD, out: OUT, end: END, text } = HOOK;
  const IN = 0;
  const color = NAMED[HOOK.color];

  const enter = EASE.outCubic(Math.min(1, (t - IN) / (HOLD - IN)));
  const push = EASE.inOut(Math.min(1, Math.max(0, (t - HOLD) / (OUT - HOLD))));
  const exit = EASE.inCubic(Math.min(1, Math.max(0, (t - OUT) / (END - OUT))));

  const scale = (1.34 - 0.34 * enter) * (1 + push * PUSH) * (1 - exit * 0.42);

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingBottom: 240 }}>
      <div
        style={{
          position: "relative",
          fontFamily: FONT.bebas,
          fontSize: hookSize(text),
          whiteSpace: "nowrap",
          lineHeight: 0.86,
          color,
          opacity: enter * (1 - exit),
          transform: `translateY(${(1 - enter) * 60 + exit * 420}px) scale(${scale})`,
          filter: `blur(${(1 - enter) * 26 + exit * 16}px)`,
          textShadow: probe ? "none" : "0 20px 90px rgba(0,0,0,.7)",
        }}
      >
        {probe ? null : (
          <span
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              color,
              filter: "blur(52px)",
              opacity: 0.75,
            }}
          >
            {text}
          </span>
        )}
        <span style={{ position: "relative" }}>{text}</span>
      </div>
    </AbsoluteFill>
  );
};
