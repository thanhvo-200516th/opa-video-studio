# kb-remotion-vietnamese-reel-expert — toàn văn tài liệu của nguồn `remotion-vietnamese-reel-expert`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/remotion-vietnamese-reel-expert/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: remotion-vietnamese-reel-expert/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `remotion-vietnamese-reel-expert`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Vietnamese 3-second hook patterns + VN typography scale/line-height rules for 9:16 reels
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Media Super Powers/.claude/skills/remotion-vietnamese-reel-expert`
> **Khi dùng trên máy Linux này:**
> - Windows path E:/Vibe Coding/.../tiktok-ai-news-factory/assets/remotion-template/... (template not imported): remove
> - generalize or label the @ainius.net brand identity as an example
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: remotion-vietnamese-reel-expert
description: Expert in creating high-quality vertical Vietnamese reels (1080x1920) using Remotion for @ainius.net AI news channel. Specializes in 4 content pillars (Breaking/Explainer/Tool Review/Industry Signal), 5 hook patterns, 7-12 slide structure, cream background + red coral accent brand identity, Be Vietnam Pro typography, persistent progress bar + slide counter + "A\\" logo watermark, karaoke captions, browser mockups. Use this skill whenever user mentions reel, TikTok, Instagram Reel, AI news Vietnamese, @ainius.net, Vietnamese short video, or uploads video reference. Always combine with remotion-best-practices skill.
tags: remotion, vietnamese, reel, vertical-video, karaoke, ainius, ai-news
---

# Remotion Vietnamese Reel Expert

Hub skill for producing @ainius.net AI news reels in Vietnamese.

## Khi cần quyết định pillar và editorial calendar
Load [./references/ai-news-pillars.md](./references/ai-news-pillars.md).

## Khi viết hook slide đầu tiên
**BẮT BUỘC** load [./references/hook-patterns.md](./references/hook-patterns.md) trước khi code slide 01. Hook phải kết thúc voiceover trước frame 75 (2.5s @ 30fps).

## Cho mọi component visual
Load [./references/channel-identity.md](./references/channel-identity.md) để có color tokens, typography scale, và 13 signature của kênh.

## Cấu trúc MainVideo

GlobalOverlay (progress bar + slide counter + logo) **PHẢI** nằm NGOÀI `<Series>`, nếu không sẽ bị shift theo Sequence local frame.

## Implementation reference

Brand profile `AINIUS_STYLE` tại `E:/Vibe Coding/Media Super Powers/skills/tiktok-ai-news-factory/assets/remotion-template/src/styling/profiles/ainius.ts`.

Demo composition `AiniusClaudeOpus47Video` registered in Root.tsx.

<!-- ===== /file: remotion-vietnamese-reel-expert/MODULE.md ===== -->

<!-- ===== file: remotion-vietnamese-reel-expert/references/ai-news-pillars.md ===== -->

# AI News Content Pillars

> **Khi nào load file này:** user muốn tạo video mới, cần quyết định video thuộc loại nào, hoặc cần script cho kênh tin tức AI tiếng Việt.

## Tổng quan 4 Pillar

Kênh AI news tiếng Việt cần chính xác **4 content pillars**, tỷ lệ phân bổ cố định:

```
Breaking AI News     ████████████████        40%
Explainer            ████████████            30%
Tool Review & Demo   ████████                20%
Industry Signal      ████                    10%
```

Quy tắc: **không dưới 3 pillar, không quá 5 pillar.** Ít hơn → kênh quá niche. Nhiều hơn → khán giả confused về identity.

---

## Pillar 1: Breaking AI News (40% lịch)

**Mục đích:** Giữ audience cảm thấy "kênh này luôn biết tin mới nhất". Đây là pillar thu hút follow mới nhanh nhất.

**Đặc trưng:**
- Thời lượng 30-60 giây
- 5-7 slide
- Hook: stat punch hoặc bold claim
- Tốc độ voiceover 1.05-1.1x (tạo urgency)
- Tông giọng: báo chí khẩn cấp

**Chủ đề mẫu đã verify:**
- Model mới ra mắt: "Claude Opus 4.7 vừa ra mắt", "GPT-5.4 benchmark mới"
- Feature mới: "Claude Code giờ có Computer Use", "Grok Imagine video-to-video"
- Deal/acquisition: "Anthropic đầu tư $X vào Y", "OpenAI mua startup Z"
- Leak/announcement: "Roadmap OpenAI vừa lộ", "Gemini 3.1 sắp ra"

**Checklist khi làm video pillar này:**
- [ ] Có ít nhất 1 con số cụ thể (giá, benchmark, %, date)
- [ ] Có ít nhất 1 nguồn verify (Anthropic blog, VentureBeat, TechCrunch)
- [ ] Published trong vòng 24-48h kể từ event (sau đó giảm hiệu quả >70%)
- [ ] CTA: "Follow để không bỏ lỡ", "Notification ON"
- [ ] Hashtag breaking: #AInews #TechNews + tên model

**Hook pattern phù hợp nhất:** Stat punch, Bold claim (xem hook-patterns.md)

**Tốc độ xuất bản:** 1-2 video/tuần, tối đa 3 nếu có nhiều event.

---

## Pillar 2: Explainer (30% lịch)

**Mục đích:** Xây dựng authority và save rate. Save rate cao → algorithm boost lâu dài.

**Đặc trưng:**
- Thời lượng 60-120 giây
- 8-10 slide
- Hook: curiosity gap hoặc bold question
- Tốc độ voiceover 1.0x (giảng giải điềm tĩnh)
- Tông giọng: giáo viên thân thiện

**Chủ đề mẫu:**
- Concept: "Agent AI là gì?", "RAG hoạt động ra sao?", "Vector DB 1 phút"
- Kỹ thuật: "Token vs context window", "Fine-tune vs prompt engineering"
- Workflow: "Cách prompt Claude hiệu quả", "5 sai lầm khi dùng ChatGPT"
- Ecosystem: "MCP là gì?", "Computer use protocol giải thích"

**Checklist:**
- [ ] Có **analogy Việt Nam** (phở, cà phê sữa đá, grab, bộ đội, trường đại học...)
- [ ] Có ít nhất 1 SVG diagram tự vẽ với `stroke-dashoffset` animation
- [ ] Có slide "misconception" — chỉ ra điều mọi người hiểu sai
- [ ] Có takeaway 1 câu ở slide cuối để dễ save
- [ ] KHÔNG dùng thuật ngữ tiếng Anh nếu có từ Việt tương đương

**Giữ nguyên tiếng Anh:** tên model (Claude, GPT, Gemini), tên công ty (OpenAI, Anthropic), tên technical term chuẩn (transformer, embedding, token).

**Tốc độ xuất bản:** 1 video/tuần. Có thể tổ chức thành series (AI 101 tập 1, 2, 3...).

---

## Pillar 3: Tool Review & Demo (20% lịch)

**Mục đích:** Monetization pipeline. Đây là pillar tạo affiliate revenue cao nhất.

**Đặc trưng:**
- Thời lượng 60-180 giây
- 8-12 slide
- Hook: bold question, direct comparison
- Screen recording thật (không mô phỏng)
- Cursor animation + typing animation

**Chủ đề mẫu:**
- Comparison: "Claude Code vs Cursor", "ElevenLabs vs OpenAI TTS"
- Deep dive: "Dùng Claude Code 30 ngày — kinh nghiệm", "Top 10 prompt thiết kế"
- Pricing breakdown: "Claude plan nào đáng tiền?", "API cost so sánh"
- Workflow: "Cách tôi build video bằng Remotion + Claude"

**Checklist:**
- [ ] Dùng TOOL THẬT, quay màn hình thật (audience phát hiện fake ngay)
- [ ] Có Pros VÀ Cons (trung thực tăng credibility → tăng affiliate conversion)
- [ ] Có pricing card cụ thể với plan khuyến nghị
- [ ] CTA affiliate link rõ ràng (disclosure: "link ở bio có affiliate")
- [ ] Screen recording 1920×1080 scale vào BrowserMockup

**Tốc độ xuất bản:** 2-3 video/tháng. Không làm quá thường xuyên vì cần deep-dive thật.

---

## Pillar 4: Industry Signal (10% lịch)

**Mục đích:** Tạo tranh luận → comment rate cao → algorithm boost. Pillar này ít nhất về số lượng nhưng cao nhất về engagement per video.

**Đặc trưng:**
- Thời lượng 45-75 giây
- 6-8 slide
- Hook: stat punch
- Tông giọng: analyst Bloomberg, không giật gân
- **BẮT BUỘC** có counter-argument (để tăng credibility)

**Chủ đề mẫu:**
- Stock movement: "Figma -6% sau Claude Design", "NVIDIA +$200B sau GTC"
- Leadership move: "CEO X rời Google", "Y vừa join OpenAI"
- M&A: "Adobe mua startup Z", "Microsoft thoái vốn khỏi W"
- Regulation: "EU AI Act ảnh hưởng gì đến Claude?"

**Checklist:**
- [ ] Số liệu có timestamp và nguồn (cổ phiếu, ngày, tweet link)
- [ ] Tông voice **không superlative** ("siêu", "cực", "đỉnh" — CẤM)
- [ ] Có slide counter-argument ("nhưng cũng có người cho rằng...")
- [ ] CTA: "Comment ý kiến của bạn" (không phải "Follow")
- [ ] Prepare 3 comment mồi thảo luận sẵn, pin trong 30 phút đầu

**Tốc độ xuất bản:** 1-2 video/tháng. Chỉ làm khi CÓ event thật, không fabricate.

---

## Matrix phân bổ pillar theo tuần (70/30 planned-reactive)

```
Tuần chuẩn — 4 video:
  Thứ 2:   Breaking AI News   (planned, có thể thay = breaking thật)
  Thứ 4:   Explainer          (planned, từ backlog 8 tập)
  Thứ 6:   Tool Review        (nếu có sẵn) hoặc Breaking
  Chủ nhật: Industry Signal  (chỉ khi có event) hoặc Breaking

Khi có event thật:
  - Breaking news hot → swap slot thứ 2 hoặc thứ 6
  - Industry signal → swap slot chủ nhật
  - Explainer giữ nguyên (nền tảng authority lâu dài)
```

## Quy tắc chọn pillar khi có topic mới

Dùng decision tree này:

```
Topic mới → Hỏi:
│
├─ Đây có phải event xảy ra trong 48h qua?
│   YES → Breaking AI News
│   NO → tiếp
│
├─ Đây là so sánh/demo tool cụ thể?
│   YES → Tool Review
│   NO → tiếp
│
├─ Đây có phải stock/leadership/M&A move?
│   YES → Industry Signal
│   NO → tiếp
│
└─ Đây là khái niệm cần giải thích?
    YES → Explainer
    NO → Topic không phù hợp với kênh, skip.
```

## Anti-patterns — pillar KHÔNG nên có

- **"Drama AI"**: soi mói nội bộ công ty, tố cáo, tin đồn → mất credibility dài hạn
- **"Motivation AI"**: "AI sẽ thay đổi đời bạn" generic → không có takeaway
- **"Listicle AI"**: "Top 10 tool AI năm 2026" → bị thay thế dễ dàng, không unique
- **"Reaction AI"**: xem tweet người khác rồi react → không có value-add

Nếu topic không vào được 1 trong 4 pillar trên → **không làm**, giữ consistency kênh.

<!-- ===== /file: remotion-vietnamese-reel-expert/references/ai-news-pillars.md ===== -->

<!-- ===== file: remotion-vietnamese-reel-expert/references/channel-identity.md ===== -->

# Channel Identity — Visual & Tone Spec cho @ainius.net

> **Khi nào load file này:** trước khi code bất kỳ component nào. Đây là file nền tảng xác định "kênh này trông như thế nào".

## Nguyên tắc vàng

**Audience phải nhận ra kênh trong 1 giây** khi scroll — không cần đọc watermark. Đạt được bằng 13 signature dưới đây.

## 13 Signature Element

| # | Element | Specification |
|---|---------|---------------|
| 1 | Tỷ lệ & format | 1080×1920 portrait, 30fps, H.264 |
| 2 | Progress bar đỏ | Top, 4px, `#E63946`, fill 0→100% toàn video, zIndex 200 |
| 3 | Slide counter | Góc top-left 40,40; format `XX/NN`; 28px weight 500; opacity 0.45 |
| 4 | Logo watermark | Góc top-right 40,40; box 72×72px `#111`; chữ "A\\" trắng 36px weight 700 |
| 5 | Nền | Base `#F5F0EA` + radial tint `rgba(230,57,70,0.04)` từ 4 góc |
| 6 | Typography headline | 72-130px, weight 700-800, `#111`, letter-spacing -0.03em |
| 7 | Accent color | `#E63946` (đỏ coral) — dùng cho từ nhấn, số âm, link |
| 8 | Accent bars | 2 thanh dọc 3px × 400px `#E63946` 2 bên headline quan trọng |
| 9 | Label kicker | 24-28px weight 500, letter-spacing 0.2em, opacity 0.5 |
| 10 | Karaoke caption | y=1400-1600; 42-46px weight 700; bg `rgba(0,0,0,0.5)`; active word `#E63946` |
| 11 | Browser mockup | Border 3px gradient đỏ + 3 dot macOS + badge `#111` "Anthropic Labs" |
| 12 | Screen recording | Nhúng trong BrowserMockup bằng `<OffthreadVideo>` muted |
| 13 | Data viz | Bar chart horizontal; pill shape `borderRadius: 999`; `tabular-nums` |

---

## Color Tokens (đầy đủ)

```css
/* Primary palette */
--bg-primary: #F5F0EA;           /* Nền chính kem */
--bg-tint-red: rgba(230,57,70,0.04); /* Tint radial 4 góc */
--bg-overlay-dark: rgba(0,0,0,0.5);  /* Overlay caption */

--text-primary: #111111;         /* Text đen đậm */
--text-muted: rgba(17,17,17,0.6); /* Text phụ */
--text-faint: rgba(17,17,17,0.45); /* Counter, kicker */

/* Accent đỏ coral — identity của kênh */
--accent-primary: #E63946;       /* Đỏ chính */
--accent-muted: rgba(230,57,70,0.12); /* Bar background */
--accent-tint: rgba(230,57,70,0.3);   /* Shadow/glow nhẹ */

/* Semantic (dùng trong data viz) */
--success: #22c55e;              /* Số dương, tăng */
--danger: #E63946;               /* Số âm, giảm */
--warning: #f59e0b;              /* Gold accent khi cần */

/* Mockup */
--mockup-bg: #1a1a1a;            /* Browser inside bg */
--mockup-border: #E63946;        /* Browser border đỏ */
--mockup-badge: #111;            /* Badge "Anthropic Labs" */
```

---

## Typography Scale (Vietnamese-optimized)

Font stack:
```
font-family: "Be Vietnam Pro", "Segoe UI", system-ui, -apple-system, sans-serif;
```

### Scale chuẩn

| Token | Size | Weight | Letter-spacing | Line-height | Dùng cho |
|-------|------|--------|----------------|-------------|----------|
| `--h1-hero` | 130px | 800 | -0.035em | 1.05 | Hook slide, big statement |
| `--h1` | 110px | 700-800 | -0.03em | 1.1 | Headline main |
| `--h2` | 72px | 700 | -0.02em | 1.15 | Subheadline |
| `--h3` | 52px | 600 | 0 | 1.2 | Card title |
| `--body` | 42px | 500 | 0 | 1.35 | Body text |
| `--caption` | 36px | 500 | 0 | 1.4 | Caption area |
| `--label-kicker` | 28px | 500 | 0.2em | 1.0 | "ANTHROPIC" style label |
| `--counter` | 28px | 500 | 0.08em | 1.0 | Slide counter "XX/NN" |
| `--source` | 20px | 400 | 0 | 1.4 | Footnote source |

### Quy tắc đặc biệt cho tiếng Việt

**Line-height TỐI THIỂU:**
- Headline (80px+): `1.05` → dưới mức này dấu thanh `ấ`, `ệ`, `ớ` sẽ chồng lên dòng trên
- Body (40-50px): `1.35` → dưới mức này dấu sẽ đè lên nhau giữa các từ
- **KHÔNG BAO GIỜ** dùng line-height < 1.0

**Font weight:**
- Dùng 400, 500, 600, 700, 800 — **TRÁNH** 900 (nét dày gây vỡ pixel trên Vietnamese diacritics)
- Khi cần "ultra bold", dùng 800 + letter-spacing âm thêm 0.01em

**Dấu gạch ngang:**
- Số âm: ký tự `−` (U+2212 Minus Sign) — KHÔNG phải `-` hyphen
- Em-dash trong câu: `—` (U+2014) — KHÔNG phải `--` double hyphen
- Khoảng cách: `từ — từ` (có space 2 bên) cho em-dash

**Sentence case:**
- Headline tiếng Việt **KHÔNG** Title Case ("Claude Opus 4.7 Vừa Ra Mắt" → SAI)
- Dùng sentence case thuần ("Claude Opus 4.7 vừa ra mắt" → ĐÚNG)
- Ngoại lệ: tên riêng (Claude, Anthropic, GitHub, Copilot...)

---

## Safe Zone (bắt buộc)

```
┌─────────────────────────────────────┐  ← 150px top (status bar, search)
│                                     │
│   [NỘI DUNG CHÍNH]                  │
│   1080 - 60*2 = 960px width usable  │
│                                     │
│   60px ◄───────────────────► 60px   │
│                                     │
│                                     │
│                                     │
└─────────────────────────────────────┘  ← 170px bottom (nav, swipe UI)

Vùng an toàn: 960 × 1600 px
```

**Không bao giờ** đặt text quan trọng ngoài vùng này. Platform UI sẽ che mất ở preview iOS/Android.

---

## Component Structure bắt buộc

### MainVideo.tsx pattern

```tsx
export const MainVideo: React.FC<{totalSlides: number}> = ({totalSlides}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Xác định slide hiện tại từ frame
  const currentSlide = useMemo(() => calculateCurrentSlide(frame), [frame]);

  return (
    <AbsoluteFill style={{ 
      backgroundColor: 'var(--bg-primary)',
      fontFamily: '"Be Vietnam Pro", "Segoe UI", sans-serif'
    }}>
      {/* Background radial tint */}
      <RadialTintBackground />

      {/* SCENES PHẢI NẰM TRONG SERIES/SEQUENCE */}
      <Series>
        <Series.Sequence durationInFrames={90}>
          <Scene01Hook />
        </Series.Sequence>
        {/* ... các scene khác ... */}
      </Series>

      {/* GLOBAL OVERLAY NẰM NGOÀI SERIES — luôn hiện */}
      <GlobalOverlay 
        currentSlide={currentSlide} 
        totalSlides={totalSlides} 
      />
    </AbsoluteFill>
  );
};
```

**QUY TẮC TUYỆT ĐỐI:** `<GlobalOverlay />` **LUÔN** nằm NGOÀI `<Series>`, nếu không progress bar + counter sẽ bị shift theo Sequence local frame.

### GlobalOverlay spec

```tsx
const GlobalOverlay: React.FC<Props> = ({ currentSlide, totalSlides }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  
  const progress = interpolate(
    frame, [0, durationInFrames - 1], [0, 100],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  return (
    <>
      {/* Progress bar */}
      <div style={{
        position: 'absolute', top: 0, left: 0,
        height: 4, width: `${progress}%`,
        backgroundColor: '#E63946',
        zIndex: 200,
      }} />

      {/* Slide counter */}
      <div style={{
        position: 'absolute', top: 40, left: 60,
        fontSize: 28, fontWeight: 500,
        letterSpacing: '0.08em',
        color: 'rgba(17,17,17,0.45)',
        fontVariantNumeric: 'tabular-nums',
        zIndex: 200,
      }}>
        {String(currentSlide).padStart(2, '0')} / {String(totalSlides).padStart(2, '0')}
      </div>

      {/* Logo watermark */}
      <div style={{
        position: 'absolute', top: 40, right: 60,
        width: 72, height: 72,
        backgroundColor: '#111',
        borderRadius: 12,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 200,
      }}>
        <span style={{
          color: '#F5F0EA', fontSize: 36, fontWeight: 700,
        }}>A\\</span>
      </div>
    </>
  );
};
```

---

## Tông giọng (Voice & Tone)

### Tông base — áp dụng mọi pillar
- **Trực tiếp, không vòng vo** — câu ngắn, động từ chủ động
- **Tự tin nhưng không khoe khoang** — số liệu cụ thể > superlative
- **Thân thiện nhưng chuyên nghiệp** — xưng "bạn" chứ không "các bạn thân mến"

### Tông điều chỉnh theo pillar

| Pillar | Tông đặc trưng | Ví dụ |
|--------|----------------|-------|
| Breaking | Khẩn cấp, báo chí | "Vừa xảy ra", "Ngay hôm nay", "Đừng bỏ lỡ" |
| Explainer | Giáo viên thân thiện | "Hãy hình dung", "Giống như", "Đơn giản là" |
| Tool Review | Chuyên gia thực dụng | "Tôi đã dùng 30 ngày", "Đây là sự thật", "Đáng tiền hay không" |
| Industry Signal | Analyst Bloomberg | "Tín hiệu cho thấy", "Dữ liệu cho biết", "Cần lưu ý" |

### Từ cấm trong mọi video
- Từ superlative rẻ tiền: "siêu", "cực", "đỉnh", "đỉnh cao", "xịn xò"
- Câu mở bị nhàm: "Chào các bạn", "Welcome back", "Hôm nay mình sẽ..."
- Filler: "Thật ra", "Nói chung", "Nói thẳng ra thì"
- Tiếng lóng TikTok generic: "không phải dạng vừa", "đỉnh nóc", "kịch trần"

### Từ ưu tiên dùng
- Động từ mạnh: "ra mắt", "công bố", "rung chuyển", "đánh bại", "thay đổi cuộc chơi"
- Indicator: "cụ thể là", "theo [nguồn]", "dữ liệu cho thấy", "tính đến [ngày]"
- Engagement: "bạn nghĩ sao?", "comment ý kiến", "save lại", "share cho bạn bè"

---

## Animation Signatures

### Entrance defaults
```tsx
const entrance = spring({ 
  frame, fps, 
  config: { damping: 200 }  // Default: smooth, no bounce
});
```

### Entrance variants
```tsx
// Snappy (for stat numbers)
const snappy = spring({ frame, fps, config: { damping: 14, stiffness: 120 }});

// Bouncy (for CTA button only)
const bouncy = spring({ frame, fps, config: { damping: 8 }});

// Hero pop (for hook slide only)
const hero = spring({ frame, fps, config: { damping: 12, stiffness: 100 }});
```

### Stagger pattern
- Related items (icon grid, bullet list): stagger 10-12 frames
- Scene transitions: fade 12 frames (TransitionSeries)
- Bar chart bars: stagger 10 frames, each animates 30 frames

### Forbidden animations
- Linear fade (dùng spring, không CSS `transition`)
- Rotation >45° (làm khán giả "say")
- Bouncy text (chỉ dùng cho CTA button)
- Auto-scroll (reel là vertical một frame, không scroll)

---

## Ending CTA Pattern

Slide cuối bắt buộc có **1 trong 3 CTA patterns**:

### CTA Pattern A — Follow
```
Visual: Logo A\\ lớn giữa + URL "ainius.net" dưới
Text: "Follow để không bỏ lỡ"
Duration: 6-8 giây
Animation: Scale pop-in + infinite slow pulse loop
```

### CTA Pattern B — Save
```
Visual: Icon save big + text "Save lại video này"
Text: "Phần 2 sẽ có trong tuần tới"
Duration: 6-8 giây
Animation: Save icon spring scale + bookmark pulse
```

### CTA Pattern C — Comment
```
Visual: Speech bubble icon + câu hỏi cụ thể
Text: "[Câu hỏi trực tiếp cho audience]"
Duration: 6-10 giây
Animation: Bubble float gentle + typing dots
```

Pillar mapping:
- Breaking → Pattern A (Follow)
- Explainer → Pattern B (Save)
- Tool Review → Pattern A + affiliate link
- Industry Signal → Pattern C (Comment)

---

## Font loading strategy

Vì Be Vietnam Pro là Google Font, cần load trước khi render:

```tsx
// In Composition root
import { loadFont } from "@remotion/google-fonts/BeVietnamPro";

const { fontFamily, waitUntilDone } = loadFont("normal", {
  weights: ["400", "500", "600", "700", "800"],
  subsets: ["vietnamese", "latin"],
});

// Use delayRender to wait
const handle = delayRender();
waitUntilDone().then(() => continueRender(handle));
```

Fallback khi không có mạng: `"Segoe UI"` (Windows), `"-apple-system"` (macOS/iOS).

---

## Consistency Audit — mỗi 10 video

Sau mỗi 10 video publish, audit:

- [ ] Progress bar có ở 10/10 video?
- [ ] Counter format `XX/NN` nhất quán?
- [ ] Logo watermark kích thước + vị trí giống?
- [ ] Background color đúng `#F5F0EA` (không drift)?
- [ ] Accent đỏ `#E63946` xuất hiện ≥3 lần mỗi video?
- [ ] Không video nào dùng font khác Be Vietnam Pro?
- [ ] Không slide nào có line-height < 1.1?

Nếu có drift, cập nhật skill file này + rebuild các video gần đây.

<!-- ===== /file: remotion-vietnamese-reel-expert/references/channel-identity.md ===== -->

<!-- ===== file: remotion-vietnamese-reel-expert/references/hook-patterns.md ===== -->

# Hook Patterns — Khoa học 3 giây đầu cho reel tiếng Việt

> **Khi nào load file này:** khi viết slide 01 (hook) cho bất kỳ video nào. Bắt buộc đọc trước khi code slide đầu tiên.

## Hệ số retention bắt buộc

Theo nghiên cứu 2026 (OpusClip, Paddy Galloway 3.3B Shorts study, Vugola):

- **Drop rate 3s đầu:** nếu >35%, video coi như hỏng
- **3s retention target:** >65% cho video bình thường, >75% cho video muốn viral
- **Swiped Away ratio:** <40% — trên đó là hook thất bại hoàn toàn

Nếu Whisper transcribe xong mà voiceover không kết thúc message chính trước frame 75 (2.5s @ 30fps) → **rewrite hook**, không compromise.

## Công thức tổng quát

```
Hook Strength = [Pattern Break] + [Emotional Trigger] + [Curiosity Gap]
```

Hook phải **phát hết trong 2-2.5 giây**, chừa 0.5s buffer trước mốc 3s. Frame window: 0-75.

---

## Pattern 1: Bold Claim Shock

**Cơ chế tâm lý:** Cognitive dissonance — khán giả không thể để yên một statement mạnh. Não phải verify.

**Pillar phù hợp:** Breaking AI News, Tool Review

**Template Việt:**
- "X vừa **[động từ mạnh]** Y."
- "**Không ai** ngờ [điều bất ngờ] lại thành **sự thật**."
- "**Đây là dấu chấm hết** cho [thứ quen thuộc]."

**Ví dụ cụ thể:**
- "Anthropic vừa **thả bom**." (Video #01)
- "Claude vừa **nuốt chửng** Figma trong 1 ngày."
- "Đây là **dấu chấm hết** cho designer không biết AI."
- "$5 — mức giá **đánh bại** toàn bộ frontier."

**Do:**
- Dùng động từ mạnh ("thả bom", "nuốt chửng", "đánh bại", "xoá sổ")
- Tên riêng cụ thể ở vị trí subject (Anthropic, Claude, GPT-5.4)
- Highlight 1-2 từ quan trọng bằng màu #E63946

**Don't:**
- "X có thể sẽ Y" → từ "có thể" giết hook
- "Có lẽ X là điều bạn cần biết" → weak
- Dùng quá nhiều superlative ("siêu to khổng lồ") → rẻ tiền

---

## Pattern 2: Curiosity Gap

**Cơ chế tâm lý:** Thông tin incomplete tạo "itch" phải gãi — não không chịu được gap.

**Pillar phù hợp:** Explainer, Tool Review

**Template Việt:**
- "[Topic quen thuộc]. Nhưng **ít ai thực sự hiểu** Y."
- "3 thứ X làm được mà Y **chưa bao giờ** làm nổi."
- "**Điều ít ai biết** về [thứ gì đó]."
- "Tại sao [người] lại **[hành động bất ngờ]**?"

**Ví dụ cụ thể:**
- "Agent AI là gì **thực sự?**" (Video #02)
- "3 thứ Claude làm được mà Figma AI **chưa bao giờ** làm nổi..."
- "Tại sao CPO Anthropic lại **rời hội đồng Figma**?"
- "**Điều ít ai biết** về Claude Opus 4.7..."

**Do:**
- Gợi ý có information gap mà khán giả đang thiếu
- Dùng từ "thực sự", "chưa ai biết", "bí mật"
- Hình thức câu hỏi mở (không trả lời được bằng yes/no)

**Don't:**
- "Click để biết..." → clickbait trắng trợn, thuật toán phạt
- Curiosity gap không có payoff → audience mất niềm tin sau 2-3 video
- Quá mơ hồ ("Điều này sẽ làm bạn bất ngờ") → generic

**Quy tắc vàng:** Phải **thực sự giải đáp** gap đó trong video. Không giải đáp = mất credibility vĩnh viễn.

---

## Pattern 3: Bold Question

**Cơ chế tâm lý:** Câu hỏi trực tiếp kích hoạt phản xạ trả lời. Audience suy nghĩ câu trả lời → đã stop scroll.

**Pillar phù hợp:** Tool Review, Explainer

**Template Việt:**
- "Bạn vẫn còn **[hành động outdated]** trong 2026?"
- "Đây có phải là **dấu chấm hết** cho [thứ gì đó]?"
- "Tại sao [nhóm người] chuyển hết sang **[công cụ mới]**?"
- "[Câu hỏi so sánh] — bạn chọn cái nào?"

**Ví dụ cụ thể:**
- "Bạn vẫn còn vẽ mockup **tay** trong 2026?"
- "Đây có phải là **dấu chấm hết** cho Canva?"
- "Tại sao developer chuyển hết sang **Claude Code**?"
- "Figma hay Claude? — bạn chọn cái nào?"

**Do:**
- Câu hỏi đánh vào pain point / status quo của audience
- Kết hợp với ảnh nhân vật biểu cảm (confused, surprised)
- Dùng từ "vẫn còn" để tạo áp lực "mình outdated?"

**Don't:**
- Câu hỏi yes/no dễ trả lời "không" → audience scroll
- Câu hỏi quá rộng ("AI là gì?") → không có tension

---

## Pattern 4: Stat Punch

**Cơ chế tâm lý:** Con số cụ thể kích hoạt pattern-matching của não. Ba con số liên tiếp → não force search cho story.

**Pillar phù hợp:** Industry Signal, Breaking AI News

**Template Việt:**
- "[Số 1]. [Số 2]. [Số 3]. **Trong [khung thời gian ngắn].**"
- "[Con số to bự] — mức [adjective] **chưa từng thấy**."
- "[Số người] **đang [hành động]** sau công bố này."
- "$[X] — đánh bại toàn bộ [ngành]."

**Ví dụ cụ thể:**
- "Figma **−6%**. Wix **−4.7%**. GoDaddy **−3%**. Trong 3 ngày." (Video #03)
- "**$5.00** — mức giá đánh bại toàn bộ frontier."
- "**100.000 designer** đang lo lắng sau công bố này."
- "**2 tỷ USD** bay hơi trong 1 ngày."

**Do:**
- Dùng `tabular-nums` font-variant để số căn đều
- Dùng ký tự `−` (U+2212) thay `-` hyphen
- Stagger 3 con số xuống dưới, mỗi số spring riêng
- Màu #E63946 cho số âm, #22c55e cho số dương

**Don't:**
- Số quá general (">50% người dùng") → không specific
- Số không có timestamp → audience không biết tươi hay cũ
- Làm tròn quá nhiều (~40%) → mất credibility

---

## Pattern 5: Pattern Interrupt

**Cơ chế tâm lý:** Phá vỡ expectation scroll pattern. Khán giả đang quen thấy A, B, C → bạn show X, họ dừng lại.

**Pillar phù hợp:** Mọi pillar (đặc biệt hiệu quả với audience đã follow kênh)

**Template Việt:**
- "**Dừng scroll.** [Lý do urgent]."
- "Nếu bạn là [nghề], **xem xong hãy [hành động]**."
- "**[Ảnh shock]** + [câu caption ngắn]"

**Ví dụ cụ thể:**
- "**Dừng scroll.** Điều này sẽ thay đổi cách bạn làm việc."
- "Nếu bạn là designer, **xem xong hãy inbox cho tôi**."
- "[Ảnh CEO mặt nghiêm trọng] **Ba dòng tweet vừa làm Figma mất 6%.**"
- "**Đọc 10 giây này** rồi quyết định có nên nghỉ việc hay không."

**Do:**
- Kết hợp visual + text (đừng chỉ text)
- Tạo feeling "cá nhân gửi cho bạn"
- Direct address: "bạn", "các bạn designer", "nếu bạn dùng X"

**Don't:**
- Lạm dụng "dừng scroll" → khán giả thấy nhàm sau 3 video
- Pattern interrupt không liên quan đến content → bait-and-switch

---

## Hook Checklist (BẮT BUỘC trước khi approve script)

Trước khi code slide 01, verify tất cả:

- [ ] Hook kết thúc voiceover trước frame 75 (2.5s @ 30fps)
- [ ] Chứa ít nhất 1 trong 5 pattern ở trên
- [ ] Có visual element không chỉ text (cursor, ảnh, icon, bar chart...)
- [ ] **Không có greeting** ("Chào các bạn", "Hôm nay", "Welcome back")
- [ ] **Không có logo intro** (logo chỉ ở góc watermark, không full-screen)
- [ ] Nếu có caption, chữ đầu phải hiện trong frame 1-10
- [ ] Entrance animation dùng `spring({ damping: 12-14 })` — không linear
- [ ] Hook có ít nhất 1 từ màu #E63946 để tạo focal point
- [ ] Audience không phải "suy nghĩ" mới hiểu — phải "cảm" ngay

## A/B test framework

Để tối ưu hook cho audience của bạn cụ thể, làm 3 bước:

1. **Publish 2 version** của cùng 1 topic, chỉ khác hook pattern
   - Ví dụ: Version A dùng Bold Claim, Version B dùng Stat Punch
2. **Đo 3s retention sau 48h** (TikTok Analytics / YT Studio)
3. **Clone winner pattern** cho 5 video tiếp theo, so sánh trung bình

Sau 10 video có data, bạn sẽ biết audience của mình phản ứng mạnh nhất với pattern nào.

## Common mistakes khi viết hook tiếng Việt

1. **Dịch word-by-word từ prompt tiếng Anh**: "Here's why..." → "Đây là lý do tại sao..." (quá dài và formal)
2. **Lạm dụng dấu ba chấm**: "Và rồi..." → tạo cảm giác chưa chắc chắn
3. **Dùng tiếng Anh không cần thiết**: "Update mới nhất về AI" → dùng "Tin mới về AI" mạnh hơn
4. **Câu hỏi tu từ quá dài**: "Bạn có bao giờ tự hỏi làm thế nào mà..." → cắt thành "Làm thế nào X?"
5. **Đặt tên riêng ở cuối câu**: "Một model AI vừa ra mắt — **Claude Opus 4.7**" → đặt tên riêng ĐẦU câu để nhận ra ngay

## Hook failure modes — debug nhanh

| Triệu chứng | Chẩn đoán | Fix |
|-------------|-----------|-----|
| 3s retention 30-40% | Hook chậm, quá dài | Cắt câu xuống <8 từ |
| 3s retention 40-55% | Hook không có emotional trigger | Thêm động từ mạnh hoặc số sốc |
| 3s retention 55-65% | Hook OK nhưng thiếu unique | Thêm 1 từ highlight đỏ hoặc visual cue |
| 3s retention >65% nhưng drop 5-7s | Hook tốt, nội dung body không deliver | Giữ hook, rewrite slide 2-3 |
| Retention đều tốt nhưng share <0.5% | Thiếu takeaway quote-worthy | Thêm slide quote card cuối |

<!-- ===== /file: remotion-vietnamese-reel-expert/references/hook-patterns.md ===== -->
