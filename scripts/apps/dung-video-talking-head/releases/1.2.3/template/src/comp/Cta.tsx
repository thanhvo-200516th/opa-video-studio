import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { CTA, SAFE } from "../data/script";
import { C, FONT, FPS } from "../theme";
import { EASE, bebasEm } from "../anim";

const POP = 12; // frame pill bật lên (outBack, đạt 90 % ở frame 4 = sync_frame.cta_pill)
// Phụ đề chiếm đáy hộp chữ suốt câu CTA nên pill ở phần trên hộp (top ≥
// SAFE.text_y_min), đúng chỗ Task 11 đặt — duyệt hình R1 có thể dời (Ruling R26).
// 40 px dưới mép trên hộp: pill phồng khi bật (outBack tới ×1,08) vẫn trong hộp.
const TOP = 40;
const SIZE = { emoji: 44, label: 40, keyword: 52 }; // cỡ chữ gốc (1.0.0)

// B2: pill rộng ≤ SAFE.sub_max_w cả lúc bật (đỉnh outBack ×1,084) lẫn nhịp (×1,015). Phần cố
// định (đệm 2×40, viền 2×2, hai khoảng 18) giữ nguyên; chữ co cùng tỉ lệ theo bề rộng ước —
// emoji 1,3 em (đo bằng render), nhãn BeVietnamPro 500 ≤ 0,82 em/ký tự (như dòng nhỏ của
// Subtitle.tsx), từ khoá Bebas (anim.bebasEm) cộng letterSpacing 0,1 em mỗi ký tự; test_picture
// render kiểm. validate_edit chặn nhãn/từ khoá dài quá text.cta_*_max_chars nên chữ không co
// quá nhỏ.
const MAX_SCALE = 1.084 * 1.015;
const FIXED = 2 * 40 + 2 * 2 + 2 * 18;
const textScale = (label: string, keyword: string) =>
  Math.min(
    1,
    (SAFE.sub_max_w / MAX_SCALE - FIXED) /
      (1.3 * SIZE.emoji + 0.82 * label.length * SIZE.label + (bebasEm(keyword) + 0.1 * keyword.length) * SIZE.keyword)
  );

/** probe: bỏ bóng đổ và backdrop-filter; giữ nền, viền và chữ của pill (R26). */
export const Cta: React.FC<{ probe?: boolean }> = ({ probe = false }) => {
  const frame = useCurrentFrame();
  if (!CTA || frame < CTA.show * FPS) return null;

  const p = EASE.outBack(Math.min(1, (frame - CTA.show * FPS) / POP));
  const pulse = 1 + Math.sin((frame / FPS) * 6) * 0.015;
  const k = textScale(CTA.label, CTA.keyword);

  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: SAFE.text_y_min + TOP }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 18,
          padding: "20px 40px",
          borderRadius: 999,
          background: "rgba(255,207,107,0.14)",
          border: `2px solid ${C.gold}`,
          backdropFilter: probe ? "none" : "blur(16px)",
          opacity: Math.min(1, p),
          transform: `translateY(${(1 - p) * 40}px) scale(${p * pulse})`,
          boxShadow: probe ? "none" : "0 18px 60px rgba(0,0,0,.45)",
        }}
      >
        <span style={{ fontSize: SIZE.emoji * k }}>👇</span>
        <span style={{ fontFamily: FONT.body, fontWeight: 500, fontSize: SIZE.label * k, color: "#fff",
                       whiteSpace: "nowrap" }}>
          {CTA.label}
        </span>
        <span
          style={{
            fontFamily: FONT.bebas,
            fontSize: SIZE.keyword * k,
            whiteSpace: "nowrap",
            letterSpacing: "0.1em",
            color: C.gold,
          }}
        >
          {CTA.keyword}
        </span>
      </div>
    </AbsoluteFill>
  );
};
