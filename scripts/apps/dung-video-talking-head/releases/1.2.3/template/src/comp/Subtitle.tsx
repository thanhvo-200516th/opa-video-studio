import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { BLOCKS, Block, SAFE, Word } from "../data/script";
import { C, FONT, FPS, HERO_SCRIPT_FONT, NAMED } from "../theme";
import { EASE, fitSize, wordCap } from "../anim";
import { ADV, INK } from "../ink";

// Mốc hiện (show), mốc tắt (out) và số frame thoát (exit_f: 6 thường, 2 khi chuyển
// nhanh để từ cuối kịp đọc — R30) do picture_lock tính sẵn (lead, giữ, đồng bộ đỉnh
// tiếng) — ở đây chỉ còn độ dài animation hiện chữ.
const REVEAL = 9;    // frame để một từ hiện xong (đạt 90 % ở frame 5 = sync_frame.block)

// Block đặt đáy ở SAFE.sub_bottom_px; dòng cuối chừa thêm phần nét chữ thò dưới
// đáy dòng (em của dòng) để đáy nét chữ nằm ở y 1436 mà không ra ngoài hộp — B14
// đo nét chữ, không đo hiệu ứng (Ruling R26). Đo trên font hiện tại với dấu nặng
// và g j p q y ỵ, mọi cỡ fitSize cho ra: hero script (BeVietnamPro Black Italic,
// lineHeight 1,02) thò tới 0,121 em; dòng nhỏ (BeVietnamPro, 1,24) chạm đáy dòng;
// hero stomp/quote (DTPhudu hoa) còn cách đáy ≥ 0,05 em. Phần dư ~0,02–0,04 em
// cho làm tròn điểm ảnh. Đổi font thì đo lại (check_text_safe sẽ báo).
const DESC = { small: 0.04, script: 0.14, stomp: 0 } as const;

// D2 (1.1.1, R64): lề sơn của span gradient. background-clip:text chỉ tô bên trong hộp của span, mà
// nét BeVietnamPro Black Italic thò ra ngoài hộp (ư +0,154 em, phải Ế 0,226, trái j 0,124, trên Ẳ
// 0,239) ⇒ canary "tính từ" hiện thành "tính tù". padding bốn phía + margin ngang âm bằng nhau: vùng
// tô rộng ra, bố cục không đổi. = rules text.glyph_pad_em (test ghim).
const GLYPH_PAD_EM = 0.3;

// Cỡ chữ theo độ dài dòng (anim.fitSize) của từng face: [cỡ gốc, số ký tự lý tưởng, cỡ nhỏ nhất] —
// keep() dùng chung cỡ nhỏ nhất. Cỡ gốc script 149 (1.1.0: 150): có phần đệm nét chữ, hero ≤ 8 ký tự
// (TIERS text.hero_one_row_chars) phải một hàng — «làm NHÓM» ở 150 rộng ≈ 801 px > sub_max_w.
const FIT = { script: [149, 15, 88], stomp: [176, 12, 98], small: [54, 24, 38] } as const;
type Face = keyof typeof FIT;

/**
 * D2 (b, R65): phần nét chữ thò khỏi hộp chữ (em) của ký tự đầu (l) và cuối (r) của từ — bảng
 * src/ink.ts sinh từ font (tools/make_ink_table.py); tra NFC, chữ HOA với stomp. Dòng nhỏ
 * (BeVietnamPro Medium đứng, thò ≤ 0,037 em ≈ 2 px) không đệm.
 */
const inkOf = (face: Face, t: string) => {
  if (face === "small") return { l: 0, r: 0 };
  const s = (face === "stomp" ? t.toUpperCase() : t).normalize("NFC");
  return { l: INK[face].l[s[0]] ?? 0, r: INK[face].r[s[s.length - 1]] ?? 0 };
};
const padEm = (face: Face, s: string) => {
  const k = inkOf(face, s);
  return k.l + k.r;
};

const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a: string, b: string, t: number) => {
  const [r1, g1, b1] = hex(a);
  const [r2, g2, b2] = hex(b);
  const f = (x: number, y: number) => Math.round(x + (y - x) * t);
  return `rgb(${f(r1, r2)},${f(g1, g2)},${f(b1, b2)})`;
};

// Dải màu chạy suốt cả dòng: mỗi từ lấy một lát của cùng một gradient,
// nên các từ nối lại vẫn đọc ra một chuyển màu liên tục (không cần đo chữ).
const RAMP = ["#fbf9ff", "#d7ccff", "#b3a4ff"];
const rampAt = (t: number) => {
  const k = Math.min(0.999, Math.max(0, t)) * (RAMP.length - 1);
  const i = Math.floor(k);
  return mix(RAMP[i], RAMP[i + 1], k - i);
};

const wordP = (frame: number, w: Word) =>
  EASE.outCubic(Math.min(1, Math.max(0, (frame - w.show * FPS) / REVEAL)));

type LineKind = "small" | "hero";

const Line: React.FC<{
  words: Word[];
  frame: number;
  size: number;
  kind: LineKind;
  block: Block;
  last: boolean;
  probe: boolean;
}> = ({ words, frame, size, kind, block, last, probe }) => {
  const hero = kind === "hero";
  // R209 (1.2.0, lô b03 video 6/12): dòng CUỐI của thẻ rơi từ trên xuống (dy âm) — trượt từ dưới lên thì chữ và quầng nhoè
  // chui qua đáy vùng an toàn vài khung (text_safe bắt khi khung dò trùng lúc từ đang hiện). |dy| ≥ blur nên không bao giờ lòi đáy.
  const dy = (hero ? 40 : 24) * (last ? -1 : 1);
  const n = words.length;

  const font =
    !hero
      ? FONT.body
      : block.style === "script"
      ? HERO_SCRIPT_FONT
      : FONT.displayBlack;

  const stomp = hero && block.style !== "script";
  const solid = stomp ? NAMED[block.color ?? "ink"] : null;
  const face: Face = !hero ? "small" : stomp ? "stomp" : "script";
  const gap = hero ? "0.24em" : "0.3em";

  return (
    <div
      style={{
        display: "flex",
        flexWrap: hero && block.hero_row ? "nowrap" : "wrap",
        justifyContent: "center",
        alignItems: "baseline",
        columnGap: gap,
        rowGap: hero ? "0.02em" : "0.06em",
        maxWidth: SAFE.sub_max_w,
        paddingBottom: last ? `${DESC[face]}em` : 0,
        fontFamily: font,
        fontSize: size,
        lineHeight: hero ? 1.02 : 1.24,
        fontWeight: hero ? 900 : 500,
        fontStyle: hero && block.style === "script" ? "italic" : "normal",
        textTransform: stomp ? "uppercase" : "none",
        letterSpacing: hero ? "-0.015em" : "0",
      }}
    >
      {groupsOf(words).map((g) => (
        // P5: nhóm glue không xuống dòng giữa các từ của nó (dải màu gradient vẫn theo từng từ)
        <span key={g[0]} style={{ display: "inline-flex", flexWrap: "nowrap", alignItems: "baseline", columnGap: gap }}>
          {g.map((i) => cell(words[i], i))}
        </span>
      ))}
    </div>
  );

  function cell(w: Word, i: number) {
    // D2: ô từ — cả chỗ giữ khi chưa hiện và quầng — chứa trọn nét chữ thò ra; bố cục dòng
    // không đổi khi từ hiện
    const ink = inkOf(face, w.t);
    const inkPad = face === "small" ? {} : { paddingLeft: `${ink.l}em`, paddingRight: `${ink.r}em` };
    const p = wordP(frame, w);
    if (p <= 0) return <span key={i} style={{ ...inkPad, opacity: 0 }}>{w.t}</span>;

    const accent = hero && block.accent === i;
    const color = solid
      ? solid
      : accent
      ? C.heroC
      : hero
      ? undefined
      : C.ink;

    const grad =
      hero && !solid && !accent
        ? `linear-gradient(100deg, ${rampAt(i / Math.max(n, 1))}, ${rampAt(
            (i + 1) / Math.max(n, 1)
          )})`
        : undefined;

    // probe bỏ drop-shadow (R26); blur hiện chữ vẫn đo — chữ lên hình đúng như vậy (R29)
    const common: React.CSSProperties = {
      display: "inline-block",
      ...inkPad,
      opacity: p,
      transform: `translateY(${(1 - p) * dy}px)`,
      filter: `blur(${(1 - p) * (hero ? 12 : 8)}px)${
        hero && !probe ? " drop-shadow(0 8px 22px rgba(0,0,0,.8))" : ""
      }`,
    };

    return (
      <span key={i} style={{ position: "relative", ...common }}>
        {/* quầng sáng phía sau — bản sao nhoè của chính chữ đó */}
        {hero && !probe ? (
          <span
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              ...inkPad,
              color: solid ?? "#8f7dff",
              filter: "blur(22px)",
              opacity: 0.7 * p,
              pointerEvents: "none",
            }}
          >
            {w.t}
          </span>
        ) : null}
        <span
          style={{
            position: "relative",
            color: grad ? "transparent" : color,
            backgroundImage: grad,
            WebkitBackgroundClip: grad ? "text" : undefined,
            backgroundClip: grad ? ("text" as const) : undefined,
            padding: grad ? `${GLYPH_PAD_EM}em` : undefined,
            margin: grad ? `0 -${GLYPH_PAD_EM}em` : undefined,
            textShadow: grad || probe
              ? "none"
              : hero
              ? "0 8px 34px rgba(0,0,0,.6), 0 2px 6px rgba(0,0,0,.5)"
              : "0 3px 16px rgba(0,0,0,.75), 0 1px 3px rgba(0,0,0,.6)",
          }}
        >
          {w.t}
        </span>
      </span>
    );
  }
};

const text = (ws: Word[]) => ws.map((w) => w.t).join(" ");

// B2: dòng chỉ xuống dòng giữa các từ, nên cỡ còn bị chặn bởi từ dài nhất (anim.wordCap): trần
// em mỗi ký tự = em/ký tự lớn nhất trên mọi từ của 60 kịch bản kênh, advance đo bằng fontTools
// (dòng nhỏ BeVietnamPro 500: "mâm" 0,815; hero script BeVietnamPro Black Italic: "mâm" 0,828,
// "WORKFLOW" 0,818; hero stomp/quote DTPhudu Black in hoa: "MỞ" 0,655) — nét chữ nghiêng vẫn hẹp
// hơn advance; test_picture render kiểm các từ xấu nhất. Đổi font thì đo lại.
const WORD_EM = { small: 0.82, script: 0.83, stomp: 0.66 } as const;

// P5 (1.1.1): nhóm chỉ số từ của một dòng — từ mang glue dính với từ ngay sau (không xuống dòng).
function groupsOf(ws: Word[]): number[][] {
  const out: number[][] = [];
  ws.forEach((_, i) => (i > 0 && ws[i - 1].glue ? out[out.length - 1].push(i) : out.push([i])));
  return out;
}
const unit = (ws: Word[], g: number[]) => g.map((i) => ws[i].t).join(" ");

// P5: nhóm glue ở cỡ nhỏ nhất của face vẫn rộng quá sub_max_w (trần WORD_EM mỗi ký tự + phần nét
// thò) thì nhả glue của nhóm đó — glue không bao giờ làm tràn hộp.
const keep = (ws: Word[], face: Face): Word[] => {
  const wide = groupsOf(ws).filter((g) => {
    const s = unit(ws, g);
    return (s.length * WORD_EM[face] + padEm(face, s)) * FIT[face][2] > SAFE.sub_max_w;
  });
  const drop = new Set(wide.flat());
  return ws.map((w, i) => (drop.has(i) ? { ...w, glue: false } : w));
};

// B2 + D2 + P5: cỡ còn bị chặn bởi đơn vị không xuống dòng dài nhất (từ, hay nhóm glue), cộng phần
// đệm nét chữ lớn nhất của các đơn vị.
const capped = (ws: Word[], face: Face, size: number) => {
  const units = groupsOf(ws).map((g) => unit(ws, g));
  return wordCap(units, size, WORD_EM[face], SAFE.sub_max_w, Math.max(...units.map((s) => padEm(face, s))));
};
// R124: bề rộng (em ở cỡ 1) của hero dựng MỘT hàng (hero_row) đúng như Line dàn: advance thật từng ký tự
// (ink.ts ADV; ký tự không có trong bảng lấy trần WORD_EM) + letter-spacing hero mỗi ký tự + đệm nét hai
// mép mỗi từ (ô từ) + khoảng cách từ. = letterSpacing / gap của dòng hero trong Line (test ghim).
const HERO_LS_EM = -0.015;
const HERO_GAP_EM = 0.24;
const HERO_ROW_FIT = 0.95;   // R209: chừa 5 % — quầng nhoè 12 px lúc hiện + advance đo hụt vài % (lô b03 video 6: 810/800 px)
const rowEm = (ws: Word[], face: "script" | "stomp") =>
  ws.reduce((sum, w) => {
    const s = (face === "stomp" ? w.t.toUpperCase() : w.t).normalize("NFC");
    return sum + [...s].reduce((acc, c) => acc + (ADV[face][c] ?? WORD_EM[face]) + HERO_LS_EM, 0) + padEm(face, w.t);
  }, 0) + HERO_GAP_EM * Math.max(0, ws.length - 1);
const smallSize = (ws: Word[]) => {
  const [base, ideal, min] = FIT.small;
  return capped(ws, "small", fitSize(text(ws), base, ideal, min));
};

export const Subtitle: React.FC<{ probe?: boolean }> = ({ probe = false }) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: SAFE.sub_bottom_px,
        textAlign: "center",
      }}
    >
      {BLOCKS.map((b) => {
        const outAt = b.out;
        const inAt = Math.min(...b.top.concat(b.hero, b.bottom).map((w) => w.show));

        if (frame < inAt * FPS - 2 || frame > outAt * FPS + b.exit_f) return null;

        const q = Math.min(1, Math.max(0, (frame - outAt * FPS) / b.exit_f));
        const heroTxt = text(b.hero);
        const quoted =
          b.style === "quote"
            ? b.hero.map((w, i) => ({
                ...w,
                t: (i === 0 ? "“" : "") + w.t + (i === b.hero.length - 1 ? "”" : ""),
              }))
            : b.hero;
        const heroFace: Face = b.style === "script" ? "script" : "stomp";
        const heroWords = keep(quoted, heroFace);
        const [base, ideal, min] = FIT[heroFace];
        const fitted = capped(heroWords, heroFace, fitSize(heroTxt, base, ideal, min));
        const heroSize = b.hero_row ? Math.min(fitted, (HERO_ROW_FIT * SAFE.sub_max_w) / rowEm(heroWords, heroFace as "script" | "stomp")) : fitted;
        const top = keep(b.top, "small");
        const bottom = keep(b.bottom, "small");

        return (
          <div
            key={b.id}
            style={{
              position: "absolute",
              bottom: SAFE.sub_bottom_px,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 10,
              opacity: 1 - q,
              transform: `translateY(${-20 * EASE.inCubic(q)}px)`,
              filter: `blur(${6 * q}px)`,
            }}
          >
            {top.length ? (
              <Line
                words={top}
                frame={frame}
                size={smallSize(top)}
                kind="small"
                block={b}
                last={false}
                probe={probe}
              />
            ) : null}

            <Line
              words={heroWords}
              frame={frame}
              size={heroSize}
              kind="hero"
              block={b}
              last={!bottom.length}
              probe={probe}
            />

            {bottom.length ? (
              <Line
                words={bottom}
                frame={frame}
                size={smallSize(bottom)}
                kind="small"
                block={b}
                last
                probe={probe}
              />
            ) : null}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
