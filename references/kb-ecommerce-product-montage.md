# kb-ecommerce-product-montage — toàn văn tài liệu của nguồn `ecommerce-product-montage`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/ecommerce-product-montage/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: ecommerce-product-montage/MODULE.md ===== -->

<!-- master-video-edit: mô-đun nhập 2026-10-29 -->
> **Mô-đun `ecommerce-product-montage`** của `master-video-edit` — kiến thức tham khảo (không chạy công cụ trong file nếu chưa có).
> Thêm gì: Sales spine (hook-pain-demo-proof-CTA), material roles, proof placement for selling reels
> Nguồn (USB): `/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/output/research-integration-20261002/sources/openchatcut/src/agent/skills/ecommerce-product-montage`
> **Khi dùng trên máy Linux này:**
> - repoint sibling refs (product-ad-video-script, beat-sync-montage, multi-clips-to-reels)
> Công cụ OpenChatCut nhắc trong file (nếu có) chỉ dùng được khi app OpenChatCut mở, qua MCP `openchatcut`; không có thì làm bằng ffmpeg / faster-whisper / FilmCraft.

---
name: ecommerce-product-montage
description: |
  Assemble product footage, UGC, and b-roll into a conversion-oriented montage with a hook → pain → demo → proof → CTA rhythm.
  Use for 带货混剪, 产品混剪, 商品短视频, 种草视频, ecommerce montage, product reel, UGC cutdown, or when the user wants selling footage cut into a short that converts.
---

# Ecommerce Product Montage

Use this workflow when the goal is a short that *sells*, not just one that looks
good. The failure mode to avoid is a pretty montage with no sales spine: strong
footage, pleasant cuts, and zero reason for the viewer to act.

This workflow decides **structure and sequencing** for selling footage. It does
not write the ad copy — when the hook, angles, or CTA text are not given, hand
off to `product-ad-video-script` for the script, then come back here to assemble.
It does not re-explain music tooling — for beat-driven placement use
`beat-sync-montage` or `music-intelligence`.

This is a OpenChatCut-native workflow. Use the current project, source assets,
asset-frame inspection, AV/script context, and OpenChatCut editing tools.

## When to switch workflows

- No script yet, only a product/offer → `product-ad-video-script` first, return here to cut.
- Music should drive the cut placement → `beat-sync-montage` (and `music-intelligence` for tools).
- Many clips, no selling intent, just the strongest cut → `multi-clips-to-reels`.
- N distinct selling variants from one pool → `batch-montage-variants`, using this workflow per cut.

## Workflow

1. Fix the one job the edit must do: which objection it dissolves or which action it drives (save, tap, buy, follow). If the brief names none, propose one and confirm.
2. Inventory the material by sales role, not by file: hero demo, UGC reaction, proof (review/result), context b-roll, price/offer card. See [references/material-roles.md](references/material-roles.md). Footage that fills no role is parked, not force-inserted.
3. Lay the sales spine before cutting: hook (0–3s, the open loop) → pain/context → demo → proof → CTA. See [references/sales-spine.md](references/sales-spine.md). Every beat maps to a spine position; a clip with no spine position is cut.
4. Lead with the hook from a real moment, not a title card. The first three seconds either open a loop ("you are doing X wrong") or show the payoff; a logo sting as opener loses the scroll.
5. Place the demo where the viewer is curious, not where the script says "demo." Demo proves the hook; if the hook is a result, demo the path to it.
6. Insert proof as a pattern interrupt, not a block. One real review line or result frame beats a stacked proof montage. See [references/proof-placement.md](references/proof-placement.md).
7. Hold the CTA long enough to read. Price, offer, and the exact action each get a legible beat; a CTA flashed for one cut is a CTA nobody acts on.
8. Keep claims grounded. Do not manufacture prices, guarantees, medical, or earnings claims the assets do not support. Pull offer text from the product page or user notes; if absent, ask.
9. QA by the spine, not by the cut list: can a cold viewer state the offer and the action after watching once? If not, the edit sells nothing.
10. Report the spine coverage and any role with no usable footage, so a thin section is flagged before shipping.

## Plan Format

- The one job this edit does
- Material inventory by role, with what is missing
- Spine map: timestamp → spine position → which clip → why it earns that slot
- Hook type (open loop / payoff) and the moment used
- Proof placement and the interrupt it creates
- CTA beats: price, offer, action, each with duration
- Risks: ungrounded claims, thin demo, CTA too short, hook that does not land

## Rules

- **Spine over polish.** A serviceable cut in the right spine position beats a beautiful cut that breaks the argument.
- **Hook is a moment, not a card.** Open on footage that creates tension or shows the result; title cards come later if at all.
- **One job per edit.** An edit trying to handle every objection handles none. Pick the one that converts this audience.
- **Proof interrupts, it does not pile.** One credible proof point lands harder than five weak ones.
- **CTA must be legible.** Price, offer, and action each get a readable beat; never flash the CTA.
- **Claims stay grounded.** No invented price, guarantee, medical, or earnings claim. Ask when the asset is silent.
- **Park, do not force.** Footage that fits no spine position weakens the edit; leave it out and say so.

<!-- ===== /file: ecommerce-product-montage/MODULE.md ===== -->

<!-- ===== file: ecommerce-product-montage/references/material-roles.md ===== -->

# Material Roles for Product Montage

Sort footage by the job it does in the sale, not by which file it came from. A
clip that is gorgeous but fills no role is dead weight in a selling edit.

## The five roles

| Role | What it carries | Weak when |
|---|---|---|
| Hero demo | The product doing the thing it is sold for | Staged, over-lit, obviously a commercial |
| UGC reaction | A real person's genuine response | Scripted, reads as an actor reading lines |
| Proof | Review line, result, before/after, stat | Fabricated, unreadable, piled without a beat |
| Context b-roll | Setting, lifestyle, the world the product lives in | Decorative only, no link to the argument |
| Offer card | Price, discount, the exact action to take | Flashed, buried, contradicts the spoken CTA |

A finished montage needs at least hero demo + one proof + an offer card. UGC and
context are what lift it from ad to story.

## Inventory before planning

For each source asset, tag it with the role(s) it can serve and the strength:

```
asset          role                strength   note
clip_04.mp4     hero demo           strong     real unboxing, natural light
ugc_02.mp4      ugc reaction        medium     genuine laugh, but audio low
review_01.png   proof               strong     verbatim 5-star, on-brand
broll_11.mp4    context b-roll      weak       pretty but unrelated to hook
```

Strength is a judgment, not a file property — the same clip can be strong in one
role and useless in another.

## Parking, not forcing

Footage that fits no spine position is parked, not inserted to fill time. Common
cases:

- B-roll with no link to the argument → cut or move to a separate mood cut.
- A second proof point when one already landed → hold for a variant, do not stack.
- Hero demo that is clearly staged → use as context, not as the proof of the hook.

Parking keeps the spine tight. A 20-second edit with every role covered beats a
40-second edit padded with pretty irrelevance.

## Capacity check

If the pool has no usable proof or no offer text, say so before cutting. An edit
with hook + demo but no proof and no CTA is a teaser, not a product montage — the
user should decide whether that is the intent.

<!-- ===== /file: ecommerce-product-montage/references/material-roles.md ===== -->

<!-- ===== file: ecommerce-product-montage/references/proof-placement.md ===== -->

# Proof Placement

Proof is what turns a nice demo into something the viewer believes. The mistake
is to pile proof into a block — five weak claims read as a commercial break. One
credible proof point, placed as an interrupt, lands harder.

## Proof as a pattern interrupt

A selling montage builds rhythm: hook, pain, demo. Proof should *break* that
rhythm with a jolt of reality — a real voice, a real number, a real before/after.

- Insert proof right after the demo peak, while belief is lowest and curiosity is highest.
- Use a hard cut or a distinct audio bed so the proof reads as "and here is the evidence," not "and now more footage."
- One proof point per edit unless the brief is explicitly comparison/long-form.

## What counts as proof

| Type | Strong | Weak |
|---|---|---|
| Review line | Verbatim, on-brand, specific | "great product" generic, or fabricated |
| Result | Before/after frame, measurable | Vague "it works" with no visual |
| Stat | Sourced, legible on screen | Unsourced number flashed past |
| UGC reaction | Genuine, spontaneous | Clearly read from a script |

## Grounding rules

- No invented price, guarantee, medical, or earnings claim. Pull offer and proof
  text from the product page, user notes, or visible assets.
- If the asset is silent on a claim the edit implies, ask — do not fill the gap
  with a plausible number. A wrong claim in a shipped montage is a trust loss, not
  a trim.
- Attribute proof to its source when the format allows (e.g., a review handle),
  so it reads as real rather than as copywritten.

## Capacity and variants

If the pool has several strong proof points, do not stack them in one edit —
distribute them across variants (see `batch-montage-variants`). Each variant leads
with a different proof, which is also how you A/B test what actually converts.

## Red flags

- Proof is a block of three-plus clips with no interrupt between them.
- The only proof is generic praise with no specifics.
- The CTA contradicts the proof (proof says "results vary," CTA says "guaranteed").
- Offer text appears nowhere on screen, only in spoken audio no one replays.

<!-- ===== /file: ecommerce-product-montage/references/proof-placement.md ===== -->

<!-- ===== file: ecommerce-product-montage/references/sales-spine.md ===== -->

# Sales Spine

The spine is the argument the edit makes. Cut to the spine, not to the clock.
Every clip earns its slot by advancing one position; a clip that advances none
is removed.

## The five positions

| Position | Job | Time budget | What lands it |
|---|---|---|---|
| Hook | Open a loop or show the payoff | 0–3s | A real moment of tension or result, not a logo |
| Pain / context | Why this matters | 3–8s | The problem the product resolves, felt not stated |
| Demo | Prove the hook | 8–18s | The product doing the thing, natural and legible |
| Proof | Make it believable | 18–24s | One real review/result, placed as an interrupt |
| CTA | Drive the action | 24–30s | Price, offer, and the exact action, each readable |

Budgets are starting points for a ~30s short; stretch or compress by platform,
but never let the CTA fall below ~3 readable seconds.

## Hook first, always

The hook is position one and the only non-negotiable open. Two working shapes:

- **Open loop:** "you are doing X wrong" / "stop buying Y" — tension the rest of the edit resolves.
- **Payoff:** show the result in frame one, then demo the path to it.

A logo sting or a slow establishing shot as the opener forfeits the scroll. If
the only strong opener is the demo, lead with a one-beat result slice and return
to the full demo in position three.

## Demo proves the hook

If the hook is a result, the demo is the path to that result — sequence them so
the viewer connects "I saw the payoff" to "here is how." If the hook is a problem,
the demo is the relief. Either way the demo is not a separate chapter; it is the
answer to whatever the hook asked.

## CTA must be legible

The CTA is three sub-beats, not one:

1. **Price** — the number, on screen long enough to read (≥1.5s).
2. **Offer** — the discount, bundle, or urgency, distinct from the price.
3. **Action** — the exact verb: "tap", "save", "follow", named once and held.

Flashing the CTA for a single cut is the most common reason a good edit converts
nothing. Hold it.

## One job per edit

Pick the single objection or action the edit serves. An edit that tries to handle
price, quality, and social proof simultaneously handles none — it reads as a
brochure. State the one job in the plan; if a clip serves a different job, it
belongs in a variant, not this cut.

<!-- ===== /file: ecommerce-product-montage/references/sales-spine.md ===== -->
