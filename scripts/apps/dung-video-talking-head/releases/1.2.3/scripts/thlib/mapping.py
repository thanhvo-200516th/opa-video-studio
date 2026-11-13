"""thlib.mapping — ghép mp4 HeyGen với mục VIDEO SCRIPT v3 theo nội dung
(spec §6.1), dùng trong `intake.py` (P0). Chỉ đọc: không sửa file video, không
ghi vào folder video.
"""

from __future__ import annotations

from pathlib import Path

from . import textnorm

# Ngưỡng khớp title trước khi so thêm nội dung (title+body) — §6.1 điểm 2:
# "so tiêu đề + lời (không so số)".
_TITLE_MATCH_THRESHOLD = 0.5


def _tokens(text: str) -> list[str]:
    return textnorm.norm(text)


def _sim(a: str, b: str) -> float:
    return textnorm.similarity(_tokens(a), _tokens(b))


def _title_overlap(a_title: str, b_title: str) -> float:
    """Độ chồng token tiêu đề, không quan tâm thứ tự chữ: |A∩B| / min(|A|,|B|).
    Ba file (v3, đạo diễn, phân loại) diễn đạt cùng một tiêu đề khác thứ tự
    chữ (vd "lời thoại AI nghe như quảng cáo" ↔ "AI giả vì lời thoại như
    brochure"), nên so theo tập token ổn định hơn `textnorm.similarity`
    (SequenceMatcher — nhạy thứ tự, hợp để so cả đoạn kịch bản dài hơn)."""
    a, b = set(_tokens(a_title)), set(_tokens(b_title))
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def list_videos(vid_root) -> list[dict]:
    """Liệt kê video theo số mục: folder `<n>/<n>.mp4` hoặc file lẻ `<n>.mp4`
    ngay tại gốc (không có folder). Bỏ qua mọi entry không phải số thuần
    (A_Minh_*, B1..B19, Video_avatar*, ...). Sắp theo n tăng dần."""
    vid_root = Path(vid_root)
    videos: list[dict] = []
    for p in vid_root.iterdir():
        if p.is_dir() and p.name.isdigit():
            mp4 = p / f"{p.name}.mp4"
            if mp4.exists():
                videos.append({"n": int(p.name), "source": mp4, "loose": False})
        elif p.is_file() and p.suffix.lower() == ".mp4" and p.stem.isdigit():
            videos.append({"n": int(p.stem), "source": p, "loose": True})
    videos.sort(key=lambda v: v["n"])
    return videos


def match_clip(heard_text: str, sections: dict[int, dict]) -> dict:
    """So `heard_text` (whisper `mapping.clip_s` giây đầu) với 60 mục v3 theo
    token đã chuẩn hoá — cùng cách tính với `audit/scan_all.py` nhưng dùng
    `thlib.textnorm`. Trả về mục giống nhất, mục nhì, và điểm giống khối
    APPLY CUSTOM MOTION cao nhất (để phát hiện dán nhầm). Giữ nguyên
    `heard_text` trong kết quả (khoá "heard") để `classify` xác nhận điều
    kiện placeholder ở spec §6.1 điểm 3 (mục v3 có placeholder VÀ whisper
    nghe thấy chính từ đó) mà không phải đổi chữ ký `classify`."""
    heard_tokens = _tokens(heard_text)
    n_tok = max(len(heard_tokens), 1)

    scores = sorted(
        (
            (textnorm.similarity(heard_tokens, _tokens(sec["script"])[: n_tok + 10]), n)
            for n, sec in sections.items()
        ),
        key=lambda t: (-t[0], t[1]),
    )
    best_score, best_n = scores[0]
    second_score, second_n = scores[1]

    motion_scores = [
        textnorm.similarity(heard_tokens, _tokens(sec["motion"])[: n_tok + 10])
        for sec in sections.values()
        if sec.get("motion")
    ]
    motion_score = max(motion_scores) if motion_scores else 0.0

    return {
        "v3": best_n,
        "score": best_score,
        "second": second_n,
        "second_score": second_score,
        "motion_score": motion_score,
        "heard": heard_text,
    }


def classify(video: dict, match: dict, sections: dict[int, dict], R) -> dict:
    """Phân loại một video theo spec §6.1 điểm 3, dùng ngưỡng `mapping.*`
    của `R` (thlib.rules.Rules). `video` chỉ cần khoá "n" (số folder);
    `match` phải đến từ `match_clip` (dùng khoá "heard" của nó cho điều
    kiện placeholder)."""
    n = video["n"]
    v3 = match["v3"]

    if v3 != n:
        return {"status": "needs_input", "reasons": [f"SỐ LỆCH: giống mục {v3:02d}"]}

    # Spec §6.1 điểm 3 / brief: mục v3 còn placeholder [IN HOA] CHƯA điền VÀ
    # whisper nghe thấy chính từ đó (placeholder đã lowercase, bỏ ngoặc,
    # xuất hiện trong heard text) -> HeyGen đọc nguyên placeholder, phải
    # render lại (fix ở nguồn: điền placeholder trong v3 rồi render lại —
    # spec §7.1/§7.2). Chỉ có placeholder cấu trúc mà lời đọc vẫn nghe tự
    # nhiên (video 32: "[CÔNG CỤ]" -> "công cụ") thì không tự động rơi vào
    # nhánh này — PREP ghi CONCERN, user quyết (spec §7.1).
    placeholders = sections.get(v3, {}).get("placeholders") or []
    if placeholders:
        heard_lower = match.get("heard", "").lower()
        placeholder_words = [p.strip("[]").lower() for p in placeholders]
        if any(word in heard_lower for word in placeholder_words):
            return {"status": "needs_rerender", "reasons": ["placeholder"]}

    min_score = R.get("mapping.min_score")
    if match["motion_score"] > match["score"] or match["score"] < min_score:
        return {"status": "needs_rerender", "reasons": ["motion"]}

    min_margin = R.get("mapping.min_margin")
    if match["score"] - match["second_score"] < min_margin:
        return {"status": "needs_input", "reasons": ["margin"]}

    return {"status": "ok", "reasons": []}


def match_director(section: dict, director: dict[int, dict]) -> int | None:
    """Ghép một mục v3 với dòng kịch bản đạo diễn theo tiêu đề + lời (không so
    số — spec §6.1 điểm 2). Ứng viên phải đạt ngưỡng tiêu đề trước, sau đó
    chọn ứng viên có độ khớp tiêu đề+lời cao nhất."""
    best_n, best_score = None, -1.0
    for n, d in director.items():
        if _title_overlap(section["title"], d["title"]) < _TITLE_MATCH_THRESHOLD:
            continue
        combined = _text_sim(section, d)
        if combined > best_score:
            best_score, best_n = combined, n
    return best_n


def _text_sim(section: dict, d: dict) -> float:
    """Độ khớp tiêu đề + lời giữa mục v3 và một dòng đạo diễn."""
    return _sim(f"{section['title']} {section.get('script', '')}", f"{d['title']} {d.get('body', '')}")


def hint_scores(section: dict, director_row: dict | None, eval_row: dict | None) -> dict:
    """Điểm của hai gợi ý đã ghép (Ruling R14 — PREP-SHEET in cạnh tiêu đề để thấy gợi ý sai):
    {"director_title", "director_text", "eval_title"} — đúng các số match_director /
    match_eval dùng để chọn; dòng nào không có thì None."""
    return {
        "director_title": _title_overlap(section["title"], director_row["title"]) if director_row else None,
        "director_text": _text_sim(section, director_row) if director_row else None,
        "eval_title": _title_overlap(section["title"], eval_row["title"]) if eval_row else None,
    }


def match_eval(section: dict, director_row: int | None, eval_rows: list[dict]) -> int | None:
    """Ghép mục v3 với dòng phân loại HYBRID/talking-head. File phân loại
    đánh số theo file đạo diễn (lệch v3, spec §6.0) nên tra thẳng bằng
    `director_row` rồi xác nhận lại bằng độ khớp tiêu đề, thay vì so tiêu đề
    lại từ đầu trên cả 60 dòng."""
    if director_row is None:
        return None
    row = next((r for r in eval_rows if r["row"] == director_row), None)
    if row is None:
        return None
    if _title_overlap(section["title"], row["title"]) >= _TITLE_MATCH_THRESHOLD:
        return director_row
    return None
