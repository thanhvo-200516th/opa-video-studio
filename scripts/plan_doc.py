#!/usr/bin/env python3
"""plan_doc — tài liệu kế hoạch dựng theo từng nhịp (beat) cho người duyệt TRƯỚC khi dựng (SKILL §3, giữa bước 6 và 7).

    plan_doc.py build  <W> [--manifest <V>/00_storyboard_manifest.json] --out <W>/edit_plan.html
        Đọc <W>/words_tl.json (build_spec_q.py ghi, kể cả khi KEY_SPECS còn trống) + manifest (nếu có: ranh giới cảnh, B-roll).
        Chia nhịp ở cuối câu / ranh giới cảnh (mục tiêu 3–6 s), ghi <W>/plan_draft.json và MỘT file HTML (CSS/JS inline, chạy offline).
        Mỗi nhịp có 3 phương án A (giữ mặt + chữ chính) · B (chữ chính kiểu nhấn khác) · C (cắt sang B-roll / đồ hoạ).
        Badge «Gợi ý» chỉ là gợi ý của `suggest()` — KHÔNG tự chọn thay người dùng.
    plan_doc.py export <file-tải-về.json> <W>
        Kiểm tra file người dùng tải từ HTML («Xuất JSON») rồi ghi <W>/plan_export.json.
        build_spec_q.py đọc file này để sinh KEY_SPECS khi KEY_SPECS trống (`key_specs_from_export`).

Lược đồ plan_export.json: {"version": 1, "beats": [{beat, t0, t1, scene, phrase,
    choice: {ref, kind: stay|keyword|broll|gfx, scene_type: aroll|overlay|cutaway} | null,
    key: {lead, text, script, phrase, palette} | null, note, broll_note | null}]}  (choice null = chưa chọn → bỏ qua).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import zlib
from pathlib import Path

PALETTE = ("gold", "red", "cyan", "mint")                      # xoay như KEY_SPECS cột 6
KINDS = ("stay", "keyword", "broll", "gfx")
SCENE_TYPES = ("aroll", "overlay", "cutaway")
BEAT_MIN_S, BEAT_MAX_S, BEAT_CLAUSE_S, BEAT_TAIL_S = 3.0, 6.0, 4.5, 1.5   # mục tiêu 3–6 s/nhịp; nhịp cụt < 1,5 s gộp vào nhịp trước
SENTENCE_END, CLAUSE_END = (".", "?", "!", "…"), (",", ";", ":")
OPTION_OF = {"stay": "A", "close": "B", "show": "C"}           # nhãn suggest() → phương án gợi ý

STOP = {"và", "là", "của", "có", "cho", "với", "một", "những", "các", "này", "đó", "thì", "mà", "để", "không", "được", "ở", "trong",
        "rất", "cũng", "như", "khi", "nếu", "vì", "nên", "đã", "sẽ", "đang", "cái", "ra", "vào", "lại", "còn", "mình", "tôi", "anh",
        "em", "bạn", "nó", "ta", "rồi", "đây", "kia", "nhưng", "hay", "hoặc", "thế", "mới", "chỉ", "từ", "về", "theo", "bị", "hơn"}

# ---- A3: phân loại nhịp (khoá luật D16: khái niệm mới → giữ mặt; mô tả → cho xem; cảm xúc / kết → mặt cận) ----
INTRO_CUES = ("gọi là", "khái niệm", "nghĩa là", "tức là", "định nghĩa", "kiểu", "loại", "thứ nhất", "đầu tiên", "mô hình", "nguyên tắc",
              "bí quyết", "quy tắc", "phương pháp")
EMOTION_CUES = ("hạnh phúc", "yêu", "buồn", "đau", "khóc", "cô đơn", "nỗi", "hy vọng", "trân trọng", "nhớ", "sợ", "cảm ơn", "cuối cùng",
                "tự do", "ý nghĩa", "cuộc đời", "cuộc sống", "mãi mãi", "tin rằng", "xin", "hãy")
SHOW_CUES = ("người", "ông", "bà", "cô", "chị", "chú", "bác", "thành phố", "nước", "làng", "quê", "bức", "tranh", "ảnh", "hình",
             "căn", "ngôi", "chiếc", "cuốn", "quyển", "triệu", "tỷ", "nghìn", "trăm", "phần trăm", "mét", "màu", "con đường", "tòa", "toà")


def norm(s: str) -> str:
    return re.sub(r"[^\w\s]", "", unicodedata.normalize("NFC", s).lower()).strip()


def _has(text: str, cues: tuple[str, ...]) -> str | None:
    """Cụm đầu tiên trong `cues` xuất hiện nguyên từ (không dính vào âm tiết khác) trong `text`."""
    low = unicodedata.normalize("NFC", text).lower()
    return next((c for c in cues if re.search(rf"(?<!\w){re.escape(c)}(?!\w)", low)), None)


def _mid_sentence_proper_noun(text: str) -> str | None:
    """Từ viết hoa giữa câu (tên người / địa danh) → nhịp đang tả người / nơi."""
    toks = text.split()
    return next((t for k, t in enumerate(toks[1:], 1) if t[:1].isupper() and not toks[k - 1].endswith(SENTENCE_END)), None)


def explain(beat_text: str, is_new_item: bool, is_last: bool) -> tuple[str, str]:
    """(nhãn, lý do) — nhãn = 'stay' (giữ mặt) | 'show' (cho xem) | 'close' (mặt cận / chữ nhấn). Thứ tự ưu tiên cố định, dễ giải thích:
    nhịp cuối → close · giới thiệu khái niệm / kiểu mới → stay · câu cảm xúc → close · tả số / người / vật / nơi → show · còn lại → stay."""
    if is_last:
        return "close", "nhịp cuối: kết bằng mặt"
    if is_new_item:
        return "stay", "mục mới: giữ mặt để giới thiệu"
    if (c := _has(beat_text, INTRO_CUES)):
        return "stay", f"giới thiệu khái niệm («{c}»): giữ mặt"
    if (c := _has(beat_text, EMOTION_CUES)):
        return "close", f"câu cảm xúc («{c}»): mặt cận"
    if re.search(r"\d", beat_text):
        return "show", "có số liệu: cho xem"
    if (c := _has(beat_text, SHOW_CUES) or _mid_sentence_proper_noun(beat_text)):
        return "show", f"tả người / vật / nơi («{c}»): cho xem"
    return "stay", "không có dấu hiệu cần minh hoạ: giữ mặt"


def suggest(beat_text: str, is_new_item: bool, is_last: bool) -> str:
    """'stay' | 'show' | 'close' — chỉ làm gợi ý, không bao giờ tự chọn."""
    return explain(beat_text, is_new_item, is_last)[0]


# ---- đọc dữ liệu ----
def load_words(w: Path) -> list[tuple[str, float, float]]:
    f = w / "words_tl.json"
    if not f.is_file():
        raise SystemExit(f"Không thấy {f}: chạy build_spec_q.py (KEY_SPECS trống cũng được) để ghi words_tl.json")
    words = [(str(t), float(s), float(e)) for t, s, e in json.loads(f.read_text(encoding="utf-8"))]
    if not words:
        raise SystemExit(f"{f} rỗng")
    return words


def load_scenes(manifest: Path | None, n_words: int) -> list[dict]:
    """[{scene, first, last, type, video, role}] theo thứ tự manifest; token = display_text.split() (khớp words_tl). Không có / lệch → 1 cảnh."""
    whole = [{"scene": 0, "first": 0, "last": n_words - 1, "type": "a-roll", "video": None, "role": None}]
    if manifest is None:
        return whole
    segs = json.loads(manifest.read_text(encoding="utf-8")).get("segments", [])
    out, k = [], 0
    for i, s in enumerate(segs):
        n = len((s.get("display_text") or "").split())
        out.append({"scene": i, "first": k, "last": k + n - 1, "type": s.get("type", "a-roll"),
                    "video": (s.get("files") or {}).get("video_file"), "role": s.get("role_id")})
        k += n
    if k != n_words or any(o["last"] < o["first"] for o in out):
        print(f"[cảnh báo] số từ manifest ({k}) ≠ words_tl ({n_words}): bỏ qua ranh giới cảnh của manifest", file=sys.stderr)
        return whole
    return out


# ---- chia nhịp ----
def _scene_of(i: int, scenes: list[dict]) -> dict:
    return next(s for s in scenes if s["first"] <= i <= s["last"])


def split_beats(words: list[tuple[str, float, float]], scenes: list[dict]) -> list[tuple[int, int]]:
    """[(từ đầu, từ cuối)] chỉ số trong words. Đóng nhịp ở: ranh giới cảnh · cuối câu khi đã ≥ 3 s · dấu phẩy khi ≥ 4,5 s · quá 6 s."""
    starts = {s["first"] for s in scenes}
    spans, a = [], 0
    for i, (tok, _, _) in enumerate(words):
        if i == len(words) - 1 or (i + 1) in starts:
            close = True
        else:
            dur = words[i + 1][1] - words[a][1]
            close = (tok.endswith(SENTENCE_END) and dur >= BEAT_MIN_S) or (tok.endswith(CLAUSE_END) and dur >= BEAT_CLAUSE_S) or dur >= BEAT_MAX_S
        if close:
            spans.append((a, i))
            a = i + 1
    merged: list[tuple[int, int]] = []
    for a, b in spans:                                   # nhịp cụt gộp vào nhịp trước nếu cùng cảnh và không vượt quá lố
        dur = words[b][2] - words[a][1]
        if merged and dur < BEAT_TAIL_S and _scene_of(a, scenes) is _scene_of(merged[-1][0], scenes) \
                and words[b][2] - words[merged[-1][0]][1] <= BEAT_MAX_S + BEAT_TAIL_S:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


# ---- chữ chính mặc định ----
def _runs(toks: list[str]) -> list[tuple[int, int]]:
    """Các đoạn liên tiếp không phải từ phụ (STOP), không vắt qua dấu câu — ứng viên chữ chính."""
    out, a = [], None
    for i, t in enumerate(toks):
        if norm(t) in STOP or not norm(t):
            if a is not None:
                out.append((a, i - 1))
            a = None
            continue
        a = i if a is None else a
        if t.endswith(SENTENCE_END + CLAUSE_END):
            out.append((a, i))
            a = None
    return out + ([(a, len(toks) - 1)] if a is not None else [])


def pick_key(toks: list[str], which: str, pal: str) -> dict:
    """Chữ chính mặc định, LẤY TỪ LỜI (B10). which='tail' = đoạn từ nội dung cuối nhịp; 'long' = đoạn dài nhất (hoà → đoạn đầu)."""
    runs = _runs(toks) or [(len(toks) - 1, len(toks) - 1)]
    a, b = runs[-1] if which == "tail" else max(runs, key=lambda r: (r[1] - r[0], -r[0]))
    a = max(a, b - 2)                                    # tối đa 3 từ
    seg = toks[a:b + 1]
    return {"lead": " ".join(toks[max(0, a - 2):a]) or None, "text": " ".join(re.sub(r"[^\w\s]", "", t) for t in seg).upper(),
            "script": None, "phrase": " ".join(norm(t) for t in seg), "palette": pal}


# ---- dựng nhịp + phương án ----
def build_options(i: int, toks: list[str], scene: dict) -> list[dict]:
    pal = lambda off: PALETTE[(i + off) % 4]                               # noqa: E731  (A/B liền nhau không trùng màu)
    c_cut = scene["type"] == "b-roll"
    return [
        {"id": "A", "kind": "stay", "scene_type": "aroll", "ref": "stay", "title": "Giữ mặt + chữ chính",
         "desc": "Người nói giữ nguyên, chữ chính lấy từ lời hiện ở dưới / giữa khung.", "key": pick_key(toks, "tail", pal(0))},
        {"id": "B", "kind": "keyword", "scene_type": "overlay", "ref": "key-accent", "title": "Chữ chính kiểu nhấn khác",
         "desc": "Nhấn cụm khác trong câu (đoạn dài nhất), có thể thêm chữ viết tay / trích dẫn ngắn.", "key": pick_key(toks, "long", pal(2))},
        {"id": "C", "kind": "broll" if c_cut else "gfx", "scene_type": "cutaway", "ref": scene["video"] or "gfx",
         "title": "Cắt sang B-roll" if c_cut else "Cắt sang đồ hoạ / B-roll mới",
         "desc": (f"Cảnh B-roll đã có trong manifest ({scene['video']}), giọng chạy tiếp." if c_cut else
                  "Cắt sang minh hoạ: ghi vào «Ghi chú B-roll / đồ hoạ» thứ cần thấy (đồ hoạ chưa có bộ sinh → vào danh sách chưa hỗ trợ)."),
         "key": None},
    ]


def build_draft(words: list[tuple[str, float, float]], scenes: list[dict], name: str = "") -> dict:
    spans = split_beats(words, scenes)
    beats = []
    for n, (a, b) in enumerate(spans):
        toks = [w[0] for w in words[a:b + 1]]
        text = " ".join(toks)
        sc = _scene_of(a, scenes)
        t0 = 0.0 if n == 0 else round(words[a][1], 3)
        t1 = round(words[spans[n + 1][0]][1], 3) if n + 1 < len(spans) else round(words[b][2], 3)
        intro = n == 0 or bool(re.match(r"\s*(thứ\s+\w+|đầu tiên|tiếp theo|loại|kiểu)\b", text.lower()))
        label, why = explain(text, intro, n == len(spans) - 1)
        if sc["type"] == "b-roll" and label != "show":
            label, why = "show", "manifest đã đặt B-roll cho đoạn này"
        beats.append({"beat": n + 1, "t0": t0, "t1": t1, "scene": sc["scene"], "text": text,
                      "words": [[t, round(s, 3), round(e, 3)] for t, s, e in words[a:b + 1]],
                      "suggest": OPTION_OF[label], "suggest_why": why, "options": build_options(n, toks, sc)})
    pid = f"{name}-{len(beats)}-{zlib.crc32(' '.join(w[0] for w in words).encode()) % 100000}"
    return {"version": 1, "id": pid, "name": name, "duration": beats[-1]["t1"], "beats": beats}


# ---- HTML (một file, offline) ----
HTML = r"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8"><title>Kế hoạch dựng — __TITLE__</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--aroll:#9aa0a6;--overlay:#8ec5ff;--cutaway:#1a4fa0;--ink:#1d2129;--line:#d8dce3}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,sans-serif;color:var(--ink);background:#f4f5f8}
header{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);padding:12px 20px}
h1{margin:0 0 4px;font-size:18px}.meta{color:#5b6270;font-size:13px}
#tl{display:flex;height:26px;margin:10px 0 4px;border-radius:5px;overflow:hidden;border:1px solid var(--line)}
#tl a{display:block;background:repeating-linear-gradient(45deg,#fff,#fff 4px,#eceef2 4px,#eceef2 8px);border-right:1px solid #fff;cursor:pointer}
#tl a.aroll{background:var(--aroll)}#tl a.overlay{background:var(--overlay)}#tl a.cutaway{background:var(--cutaway)}
.legend span{display:inline-block;margin-right:14px;font-size:12px}.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:4px;vertical-align:-1px}
.bar{margin-top:8px}button{font:inherit;padding:6px 12px;border:1px solid #b5bbc6;background:#fff;border-radius:6px;cursor:pointer}
button.pri{background:#123ce8;color:#fff;border-color:#123ce8}button:hover{filter:brightness(.96)}
main{max-width:1100px;margin:16px auto;padding:0 14px}
.beat{background:#fff;border:1px solid var(--line);border-radius:10px;margin-bottom:16px;padding:14px}
.beat h2{margin:0 0 6px;font-size:15px}.beat h2 small{color:#5b6270;font-weight:400}
.top{display:grid;grid-template-columns:1fr 1fr;gap:12px}.script{background:#f7f8fa;border-radius:6px;padding:8px 10px}
textarea,input[type=text]{width:100%;font:inherit;padding:5px 7px;border:1px solid #c5cad3;border-radius:5px}textarea{min-height:58px;resize:vertical}
.opts{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}
.opt{border:2px solid var(--line);border-radius:8px;padding:10px;display:flex;flex-direction:column;gap:6px}
.opt.chosen{border-color:#123ce8;background:#f1f4ff}.opt h3{margin:0;font-size:14px}
.tag{font-size:11px;padding:1px 7px;border-radius:9px;color:#fff;display:inline-block}.tag.aroll{background:var(--aroll)}.tag.overlay{background:#3a8fe0}.tag.cutaway{background:var(--cutaway)}
.pick{background:#ffd23f;color:#3b2e00;font-size:11px;font-weight:600;padding:1px 7px;border-radius:9px;margin-left:6px}
.opt label{font-size:12px;color:#5b6270}.opt small{color:#5b6270}
@media(max-width:800px){.top,.opts{grid-template-columns:1fr}}
</style></head><body>
<header><h1>Kế hoạch dựng — __TITLE__</h1>
<div class="meta" id="meta"></div><div id="tl"></div>
<div class="legend"><span><i style="background:var(--aroll)"></i>Giữ mặt</span><span><i style="background:var(--overlay)"></i>Lớp phủ</span>
<span><i style="background:var(--cutaway)"></i>Cắt sang</span><span><i style="background:#fff;border:1px solid #bbb"></i>Chưa chọn</span></div>
<div class="bar"><button class="pri" id="bExport">Xuất JSON</button> <button id="bCopy">Copy Plan</button> <span class="meta" id="msg"></span></div></header>
<main id="main"></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent),KEY='opa_plan_'+D.id;
const S=JSON.parse(localStorage.getItem(KEY)||'{"choice":{},"note":{},"edit":{},"broll":{}}');
const TYPE={aroll:'Giữ mặt',overlay:'Lớp phủ',cutaway:'Cắt sang'};
const save=()=>localStorage.setItem(KEY,JSON.stringify(S));
const fmt=t=>Math.floor(t/60)+':'+(t%60).toFixed(1).padStart(4,'0');
const el=(tag,cls,html)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.textContent=html;return e};
const keyOf=(b,o)=>{if(!o.key)return null;const e=(S.edit[b.beat]||{})[o.id]||{};return{lead:(e.lead!==undefined?e.lead:o.key.lead)||null,
 text:e.text!==undefined?e.text:o.key.text,script:(e.script!==undefined?e.script:o.key.script)||null,phrase:e.phrase!==undefined?e.phrase:o.key.phrase,palette:o.key.palette}};
function field(b,o,f,label){const w=el('div'),l=el('label',null,label),i=el('input');i.type='text';
 const k=keyOf(b,o);i.value=k[f]||'';i.oninput=()=>{((S.edit[b.beat]=S.edit[b.beat]||{})[o.id]=S.edit[b.beat][o.id]||{})[f]=i.value;save()};w.append(l,i);return w}
function timeline(){const t=document.getElementById('tl');t.textContent='';D.beats.forEach(b=>{const a=el('a'),c=S.choice[b.beat];
 a.style.width=(100*(b.t1-b.t0)/D.duration)+'%';if(c)a.className=b.options.find(o=>o.id===c).scene_type;
 a.title='Nhịp '+b.beat+' · '+fmt(b.t0)+'–'+fmt(b.t1);a.onclick=()=>document.getElementById('b'+b.beat).scrollIntoView({behavior:'smooth'});t.append(a)});
 const n=D.beats.filter(b=>S.choice[b.beat]).length;document.getElementById('meta').textContent=D.beats.length+' nhịp · '+D.duration.toFixed(1)+' s · đã chọn '+n+'/'+D.beats.length}
function render(){const m=document.getElementById('main');m.textContent='';D.beats.forEach(b=>{
 const card=el('section','beat');card.id='b'+b.beat;
 const h=el('h2',null,'Nhịp '+b.beat+' · '+fmt(b.t0)+' – '+fmt(b.t1));h.append(el('small',null,' ('+(b.t1-b.t0).toFixed(1)+' s · cảnh '+(b.scene+1)+')'));card.append(h);
 const top=el('div','top'),nw=el('div');nw.append(el('label',null,'Ghi chú của bạn'));const ta=el('textarea');ta.value=S.note[b.beat]||'';
 ta.oninput=()=>{S.note[b.beat]=ta.value;save()};nw.append(ta);const sc=el('div','script');sc.append(el('b',null,'Lời: '),document.createTextNode(b.text));top.append(nw,sc);card.append(top);
 const g=el('div','opts');b.options.forEach(o=>{const c=el('div','opt'+(S.choice[b.beat]===o.id?' chosen':''));
  const hd=el('h3',null,o.id+' · '+o.title);if(b.suggest===o.id){const p=el('span','pick','Gợi ý');p.title=b.suggest_why;hd.append(p)}c.append(hd);
  c.append(el('span','tag '+o.scene_type,TYPE[o.scene_type]),el('small',null,o.desc),el('small',null,'Ref: '+o.ref));
  if(o.key){c.append(field(b,o,'text','Chữ chính (lấy từ lời)'),field(b,o,'phrase','Cụm trong lời (mốc giờ)'),field(b,o,'lead','Từ dẫn (tuỳ chọn)'));
   if(o.id==='B')c.append(field(b,o,'script','Chữ viết tay / trích dẫn (≤ 2 từ, tuỳ chọn)'))}
  else{const w=el('div');w.append(el('label',null,'Ghi chú B-roll / đồ hoạ'));const t2=el('textarea');t2.value=S.broll[b.beat]||'';t2.oninput=()=>{S.broll[b.beat]=t2.value;save()};w.append(t2);c.append(w)}
  const bt=el('button',S.choice[b.beat]===o.id?'pri':'',S.choice[b.beat]===o.id?'✓ Đã chọn':'Chọn phương án này');
  bt.onclick=()=>{if(S.choice[b.beat]===o.id)delete S.choice[b.beat];else S.choice[b.beat]=o.id;save();render()};c.append(bt);g.append(c)});
 card.append(g);m.append(card)});timeline()}
function plan(){return{version:1,source:'edit_plan.html',plan_id:D.id,beats:D.beats.map(b=>{const id=S.choice[b.beat],o=b.options.find(x=>x.id===id);
 const k=o?keyOf(b,o):null;return{beat:b.beat,t0:b.t0,t1:b.t1,scene:b.scene,phrase:k?k.phrase:'',
 choice:o?{ref:o.ref,kind:o.kind,scene_type:o.scene_type}:null,key:k,note:S.note[b.beat]||'',broll_note:o&&!o.key?(S.broll[b.beat]||''):null}})}}
function say(t){document.getElementById('msg').textContent=t}
document.getElementById('bExport').onclick=()=>{const a=el('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(plan(),null,1)],{type:'application/json'}));
 a.download='plan_export.json';a.click();say('Đã tải plan_export.json — chạy: plan_doc.py export plan_export.json <thư mục work>')};
document.getElementById('bCopy').onclick=()=>{const txt=plan().beats.map(p=>{const b=D.beats[p.beat-1],o=p.choice?b.options.find(x=>x.ref===p.choice.ref&&x.kind===p.choice.kind):null;
 return 'Nhịp '+p.beat+' ['+fmt(p.t0)+'–'+fmt(p.t1)+'] '+(o?o.id+' '+o.title+(p.key?' «'+p.key.text+'»':''):'(chưa chọn)')+(p.note?' — '+p.note:'')+(p.broll_note?' — B-roll: '+p.broll_note:'')}).join('\n');
 const ok=()=>say('Đã copy plan');if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(txt).then(ok,()=>say('Không copy được'));
 else{const t=el('textarea');t.value=txt;document.body.append(t);t.select();try{document.execCommand('copy');ok()}catch(e){say('Không copy được')}t.remove()}};
render();
</script></body></html>
"""


def render_html(draft: dict) -> str:
    data = json.dumps(draft, ensure_ascii=False).replace("</", "<\\/")
    return HTML.replace("__TITLE__", draft["name"] or "video").replace("__DATA__", data)


def cmd_build(w: Path, manifest: Path | None, out: Path) -> int:
    words = load_words(w)
    draft = build_draft(words, load_scenes(manifest, len(words)), name=w.resolve().parent.name)
    (w / "plan_draft.json").write_text(json.dumps(draft, ensure_ascii=False, indent=1), encoding="utf-8")
    out.write_text(render_html(draft), encoding="utf-8")
    print(f"Đã ghi {w / 'plan_draft.json'} và {out}: {len(draft['beats'])} nhịp · {draft['duration']:.1f} s. "
          f"Mở {out.name} bằng trình duyệt, chọn từng nhịp, bấm «Xuất JSON», rồi: plan_doc.py export <file tải về> {w}")
    return 0


# ---- export: kiểm tra + ghi plan_export.json ----
def find_phrase(words: list[tuple[str, float, float]], phrase: str, t0: float, t1: float) -> float | None:
    """Giờ bắt đầu của cụm (so khớp norm, liên tiếp) có từ đầu nằm trong [t0, t1); None nếu không có."""
    ptoks = norm(phrase).split()
    n = len(ptoks)
    for i in range(len(words) - n + 1):
        if t0 - 1e-3 <= words[i][1] < t1 + 1e-3 and [norm(words[j][0]) for j in range(i, i + n)] == ptoks:
            return words[i][1]
    return None


def validate_export(data: dict, words: list[tuple[str, float, float]]) -> list[str]:
    errs = []
    beats = data.get("beats") if isinstance(data, dict) else None
    if not isinstance(beats, list) or not beats:
        return ["thiếu danh sách 'beats'"]
    for b in beats:
        tag = f"nhịp {b.get('beat')}"
        if not (isinstance(b.get("t0"), (int, float)) and isinstance(b.get("t1"), (int, float)) and b["t0"] < b["t1"]):
            errs.append(f"{tag}: t0/t1 không hợp lệ")
            continue
        ch, key = b.get("choice"), b.get("key")
        if ch is None:
            continue
        if ch.get("kind") not in KINDS or ch.get("scene_type") not in SCENE_TYPES:
            errs.append(f"{tag}: choice.kind/scene_type không hợp lệ ({ch})")
        if key is None:
            continue
        if ch.get("kind") not in ("stay", "keyword"):
            errs.append(f"{tag}: chỉ stay/keyword mới có chữ chính")
        if not str(key.get("text") or "").strip():
            errs.append(f"{tag}: chữ chính trống")
        if key.get("palette") not in PALETTE:
            errs.append(f"{tag}: palette «{key.get('palette')}» không thuộc {PALETTE}")
        if find_phrase(words, str(key.get("phrase") or ""), b["t0"], b["t1"]) is None:
            errs.append(f"{tag}: cụm «{key.get('phrase')}» không có trong lời của nhịp (B10: chữ lấy từ lời)")
    return errs


def cmd_export(src: Path, w: Path) -> int:
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"Không đọc được {src}: {e}")
    errs = validate_export(data, load_words(w))
    if errs:
        raise SystemExit("plan_export không hợp lệ:\n  " + "\n  ".join(errs))
    out = w / "plan_export.json"
    out.write_text(json.dumps({"version": 1, "beats": data["beats"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    chosen = [b for b in data["beats"] if b.get("choice")]
    print(f"Đã ghi {out}: {len(chosen)}/{len(data['beats'])} nhịp đã chọn · {sum(1 for b in chosen if b.get('key'))} khối chữ chính")
    return 0


def key_specs_from_export(export: dict, words: list[tuple[str, float, float]], scene_at) -> tuple[list[tuple], list[str]]:
    """Từ plan_export.json → (hàng KEY_SPECS, ghi chú chưa hỗ trợ). Hàng = (cảnh, từ dẫn, CHỮ CHÍNH, chữ viết tay, cụm trong lời, bảng màu)
    — đúng định dạng build_spec_q.py; `scene_at(giờ)` → chỉ số cảnh chứa cụm. Nhịp kind broll/gfx không có chữ chính → báo, không im lặng bỏ."""
    rows, unsupported = [], []
    for b in sorted(export.get("beats", []), key=lambda x: x["t0"]):
        ch, key = b.get("choice"), b.get("key")
        if ch and ch.get("kind") in ("broll", "gfx"):
            unsupported.append(f"nhịp {b['beat']} ({ch['kind']}): {b.get('broll_note') or 'không ghi chú'}")
        if not (ch and key):
            continue
        t = find_phrase(words, key["phrase"], b["t0"], b["t1"])
        if t is None:
            raise SystemExit(f"plan_export: không thấy cụm «{key['phrase']}» (nhịp {b['beat']}) trong words_tl.json — chạy lại plan_doc.py export")
        rows.append((t, (scene_at(t), key.get("lead") or None, key["text"], key.get("script") or None, key["phrase"], key["palette"])))
    return [r for _, r in sorted(rows, key=lambda x: x[0])], unsupported


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="words_tl.json → plan_draft.json + edit_plan.html")
    b.add_argument("work", type=Path)
    b.add_argument("--manifest", type=Path)
    b.add_argument("--out", type=Path)
    e = sub.add_parser("export", help="kiểm tra file tải từ HTML → plan_export.json")
    e.add_argument("file", type=Path)
    e.add_argument("work", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "build":
        return cmd_build(a.work, a.manifest, a.out or a.work / "edit_plan.html")
    return cmd_export(a.file, a.work)


if __name__ == "__main__":
    sys.exit(main())
