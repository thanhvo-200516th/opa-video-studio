#!/usr/bin/env python3
"""Căn lại mốc từng từ theo GIỌNG THẬT (luật B16, người dùng chốt 2026-11-11: chữ và giọng phải khớp nhân vật).

Lỗi đo 2026-11-11: transcript giọng B-roll do HeyGen trả (`engine: heygen-voice`) có mốc dồn cục — vd OPA01 02_voice-b-roll-1:
từ 15–27 cùng 5,63 s → 14–18 chữ phụ đề bật ra cùng lúc, lệch giọng. Sửa: Whisper nghe lại file giọng lấy mốc thật, giữ
NGUYÊN chữ kịch bản (đúng chính tả), ghép từng từ vào mốc Whisper; từ không khớp nội suy giữa hai mốc kề.

    python retime_voice.py "<thư mục video>" [--all]      # chỉ sửa transcript hỏng (hoặc mọi transcript với --all)
    from retime_voice import broken, retime
Bản gốc lưu ở transcripts/_goc_truoc_can_lai/.
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "apps/video-use/helpers"))
from vn_numbers import expand_tokens  # noqa: E402

COLLAPSE_RUN = 3            # ≥ 3 từ liền cùng mốc bắt đầu = dồn cục
BURST_N, BURST_S = 6, 0.3   # ≥ 6 từ bắt đầu trong 0,3 s = dồn cục


def _norm(t: str) -> str:
    return re.sub(r"[^\w]", "", t.lower())


def _dur(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def words(d: dict) -> list[dict]:
    return [w for w in d.get("words", []) if w.get("type", "word") == "word" and w.get("text", "").strip()]


def broken(d: dict) -> str | None:
    """Lý do transcript bị dồn mốc, hoặc None nếu ổn."""
    ws = words(d)
    run = best = 1
    for a, b in zip(ws, ws[1:]):
        run = run + 1 if abs(b["start"] - a["start"]) < 1e-3 else 1
        best = max(best, run)
    if best >= COLLAPSE_RUN:
        return f"{best} từ liền cùng một mốc"
    starts = [w["start"] for w in ws]
    for i in range(len(starts) - BURST_N + 1):
        if starts[i + BURST_N - 1] - starts[i] <= BURST_S:
            return f"{BURST_N} từ bắt đầu trong {BURST_S} s ở {starts[i]:.2f} s"
    return None


def retime(tr_path: Path, audio: Path) -> dict:
    """Giữ chữ của transcript, lấy mốc từ Whisper nghe `audio`. Trả transcript mới (chưa ghi)."""
    from transcribe import call_whisper            # scripts/apps/video-use/helpers: faster-whisper GPU, rơi về CPU
    d = json.loads(tr_path.read_text(encoding="utf-8"))
    script = words(d)
    wh = words(call_whisper(audio, language="vi"))
    # so trên dạng đọc số thành chữ để «90%» khớp «chín mươi phần trăm»; mỗi token mở rộng nhớ chỉ số từ gốc
    def flat(ws):
        toks, owner = [], []
        for i, w in enumerate(ws):
            for t in expand_tokens([w["text"].strip(".,!?;:\"'").lower()]):
                toks.append(_norm(t)); owner.append(i)
        return toks, owner
    st, so = flat(script)
    wt, wo = flat(wh)
    times: dict[int, list[float]] = {}
    for blk in difflib.SequenceMatcher(None, st, wt, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            si, wi = so[blk.a + k], wo[blk.b + k]
            t = times.setdefault(si, [wh[wi]["start"], wh[wi]["end"]])
            t[0], t[1] = min(t[0], wh[wi]["start"]), max(t[1], wh[wi]["end"])
    end_all = _dur(audio) or (wh[-1]["end"] if wh else 0.0)
    anchors = sorted(times)
    out = []
    for i, w in enumerate(script):
        if i in times:
            s, e = times[i]
        else:                                          # nội suy giữa mốc khớp trước / sau
            prev = max((a for a in anchors if a < i), default=None)
            nxt = min((a for a in anchors if a > i), default=None)
            t0 = times[prev][1] if prev is not None else 0.0
            t1 = times[nxt][0] if nxt is not None else end_all
            gap_n = (nxt if nxt is not None else len(script)) - (prev if prev is not None else -1)
            k = i - (prev if prev is not None else -1)
            s = t0 + (t1 - t0) * (k - 1) / gap_n
            e = t0 + (t1 - t0) * k / gap_n
        out.append({**w, "start": round(s, 3), "end": round(max(e, s + 0.04), 3), "type": "word"})
    for a, b in zip(out, out[1:]):                     # mốc tăng dần, không chồng
        if b["start"] < a["start"]:
            b["start"] = a["start"]
        if a["end"] > b["start"]:
            a["end"] = max(a["start"] + 0.02, b["start"])
    matched = len(times) / max(1, len(script))
    return {**{k: v for k, v in d.items() if k != "words"}, "words": out,
            "engine": f"{d.get('engine', '?')}+whisper-retime", "retime_match": round(matched, 3)}


def audio_for(tr: Path, video_dir: Path) -> Path | None:
    stem = tr.stem
    for ext in (".mp3", ".wav", ".mp4", ".m4a"):
        p = video_dir / (stem + ext)
        if p.exists():
            return p
    return None


def fix_dir(video_dir: Path, force: bool = False) -> list[dict]:
    res = []
    tdir = video_dir / "transcripts"
    for tr in sorted(tdir.glob("*.json")):
        if tr.name.endswith(".whisper.json"):
            continue
        d = json.loads(tr.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or "words" not in d:
            continue
        why = broken(d)
        if not (why or force):
            continue
        audio = audio_for(tr, video_dir)
        if not audio:
            res.append({"file": tr.name, "status": "không thấy file giọng", "why": why})
            continue
        new = retime(tr, audio)
        bak = tdir / "_goc_truoc_can_lai" / tr.name
        if not bak.exists():
            bak.parent.mkdir(exist_ok=True)
            shutil.copy2(tr, bak)
        tr.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
        res.append({"file": tr.name, "status": "đã căn lại", "why": why, "match": new["retime_match"],
                    "after": broken(new)})
    return res


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    for r in fix_dir(Path(sys.argv[1]), "--all" in sys.argv):
        print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
