"""Kiểm SFX khớp MỌI nhịp hình (v2.8): chuyển cảnh · chữ vào · punch nỗi đau · SFX mở đầu. Đo HÌNH chuyển cảnh trên bản
xuất thật, đo TIẾNG từ chính file SFX mà spec dùng.

    python3 qa_sync.py SPEC.craft.json PROJECT.fcproj OUT_DIR [t1 t2 …] [--keep]   # t = giây điểm cắt
    (không đưa t → mốc đầu các clip V1 trừ clip đầu; --keep = giữ clip đo; PROJECT chỉ giữ để tương thích — không còn cần)
    → một bảng cho mỗi loại nhịp (cắt · chữ · punch · mở đầu), mỗi dòng: mốc hình · SFX khớp (rãnh · at · tên) · tiếng bắt
      đầu · tiếng to nhất · lệch · dời đề xuất; tổng mỗi loại.
    → ghi OUT_DIR/sfx_shifts.json (chỉ các clip LỆCH: beat, clip hình, rãnh, at, src, shift) + in lệnh sửa:
      python3 sfx_shift.py SPEC OUT_DIR/sfx_shifts.json SPEC_MOI.craft.json → dựng lại (fc_build_fast) rồi chạy lại qa_sync.

Luật từng loại nhịp (ĐẠT khi):
1. Cắt (chuyển cảnh, V1): |đỉnh tiếng − khung hình đổi mạnh nhất| ≤ 0,05 s + 1 khung; tiếng bắt đầu không sớm hơn hình
   bắt đầu đổi > 0,1 s (rules-details SKILL §7.4; kb-master-video-edit « Đồng bộ SFX với chuyển cảnh »).
2. Chữ vào (key_hit / pen / type / pop / word_click …): mốc hình = KHUNG ĐẦU TIÊN chữ nhìn thấy, đọc từ keyframe vào của clip
   chữ trong spec (opacity > 0 và crop phải < 100 %; lớp chữ nằm trong spec nên không cần xuất hình). Tiếng rơi 0–0,08 s
   SAU mốc đó (± 1 khung): key_hit đo ĐỈNH (« từ khoá to rơi xuống », motion_fx.keyword_tpl đặt đỉnh đúng `at` của chữ),
   loại còn lại đo lúc TIẾNG BẮT ĐẦU (tiếng gõ / nét bút kéo dài). Nguồn: kb-master-video-edit › sfx-hmc quy luật 1
   « chữ tiêu đề xuất hiện thì luôn có SFX, đúng khung hình chữ hiện » + « chữ hiện trước lời 25 ms, sớm 0–80 ms ».
   SFX gắn với lớp chữ theo chữ trong « » của tên SFX (từ khoá ưu tiên lớp « Từ khoá · … »), gần nhất trong 1,5 s.
3. Punch nỗi đau (E1): cú phóng = đoạn keyframe `motion.scale` tăng ≥ 6 điểm trong ≤ 0,4 s tới ≥ 112 % (trên trần 110 %
   của zoom chậm C4; chỉ clip hình, không tính lớp chữ); mốc hình = GIỮA đoạn phóng
   (lúc hình đổi mạnh nhất, cùng luật với cắt). SFX « nhấn nỗi đau » gần nhất trong 0,6 s: |đỉnh − giữa| ≤ 0,05 s + 1 khung.
   Zoom chậm C4 (đoạn dài) không có SFX nên không đo; punch không có SFX nhấn ghi « KHÔNG SFX » (không phải lỗi).
4. Mở đầu (F1): tiếng bắt đầu nghe thấy ở khung 0–1 (≤ 1 khung).

LỆCH có chặn giao không? KHÔNG — qa_sync là báo cáo (cổng G5 chỉ chặn spec_lint / scene_check / edit_rules). Chỉ CHẶN
(thoát 1) khi tiếng SỚM hơn hình > 0,1 s ở bất kỳ loại nhịp nào; lệch nhẹ hơn thoát 0, vẫn nên sửa.

Cách đo chuyển cảnh (v2.6, sau chạy thử OPA05: 5/13 lệch giả hoặc không rõ nguyên nhân):
- Hình: clip video 270×480 KHÔNG chữ / không tiếng dựng từ spec (chữ vào/ra làm nhiễu độ sáng + chuyển động). Khung đổi
  mạnh nhất = trọng tâm các khung ≥ 80 % mức đổi lớn nhất quanh điểm cắt (zoom + punch có hai đỉnh hai bên điểm cắt: lấy giữa,
  không lấy bên cao hơn một chút).
- Tiếng: giải mã đúng đoạn [in, in+dur] của từng SFX trong spec, nhân gain_db, lấy đỉnh. Chỉ SFX chuyển cảnh mới gắn với điểm
  cắt (SFX chữ / nhấn nỗi đau / mở đầu có loại nhịp riêng). Chỉ 1 phiên FilmCraft ẩn; ~25 s cho video 52 s; chữ / punch / mở
  đầu đo từ spec nên thêm < 5 s.
Clip đo QA không phải bản giao (A1), xoá sau khi đo.
"""
import json
import re
import shlex
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import numpy as np

TOOLS = Path(__file__).resolve().parents[1] / "scripts/apps/craft-handoff/tools"
if not TOOLS.is_dir():
    TOOLS = Path(__file__).resolve().parent / "apps" / "craft-handoff" / "tools"
sys.path.insert(0, str(TOOLS))

PEAK_TOL = 0.05            # s, cộng 1 khung
EARLY_START = 0.1          # s: tiếng bắt đầu sớm hơn hình quá mức này → LỆCH
BLOCK_EARLY = 0.1          # s: đỉnh tiếng sớm hơn hình quá mức này → CHẶN
WIN_BEFORE, WIN_AFTER = 0.45, 0.4
HOP = 240 / 48000          # 5 ms
SHIFTS_FILE = "sfx_shifts.json"
TEXT_KINDS = ("key_hit", "type", "untype", "pen", "sparkle", "word_click", "bar_click", "grid_click", "pop", "data_beep", "highlighter")
PEAK_KINDS = ("key_hit",)  # đo ĐỈNH tiếng; loại chữ khác đo lúc tiếng bắt đầu
TEXT_LATE = 0.08           # s: tiếng rơi 0 … +0,08 s sau khung chữ đầu tiên nhìn thấy
TEXT_AIM = 0.04            # s: dời tới giữa cửa sổ 0–0,08
PAIR_MAX = 1.5             # s: SFX chữ chỉ gắn với lớp chữ trong khoảng này
PUNCH_RISE, PUNCH_SPAN, PUNCH_PAIR, PUNCH_MIN = 6.0, 0.4, 0.6, 112.0   # điểm scale, s, s, scale (trên trần zoom chậm 110)
BEAT_TITLES = {"cut": "Chuyển cảnh", "text": "Chữ vào", "punch": "Punch nỗi đau", "open": "SFX mở đầu"}


def cut_times(spec: dict) -> list[float]:
    """Mốc cắt tự động: đầu các clip V1 (track video đầu tiên) trừ clip đầu."""
    v1 = next(t for t in spec["tracks"] if t.get("type") == "video")
    return sorted({round(c["at"], 3) for c in v1["clips"] if c["at"] > 0.05})


def beat_of(name: str) -> str:
    """Loại nhịp của một SFX theo tên « SFX <kind> · … »: open | pain | text | cut (chuyển cảnh, kể cả tiếng có sẵn của overlay)."""
    n = unicodedata.normalize("NFC", name or "").lower()
    kind = n.removeprefix("sfx").split("·")[0].strip()
    if "mở đầu" in n:
        return "open"
    if "nhấn nỗi đau" in n:
        return "pain"
    return "text" if kind in TEXT_KINDS or "từ khoá" in n else "cut"


def sfx_events(spec: dict, beats: tuple | None = ("cut",)) -> list[dict]:
    """SFX trong spec (track âm tên có « SFX ») thuộc các loại nhịp `beats` (None = tất cả; mặc định chỉ chuyển cảnh):
    track, at, in, dur, src, name, gain_db, beat."""
    out = []
    for t in spec["tracks"]:
        if t.get("type") != "audio" or "SFX" not in t.get("name", ""):
            continue
        for c in t["clips"]:
            b = beat_of(c.get("name", ""))
            if beats is None or b in beats:
                out.append({"track": t["name"], "at": float(c["at"]), "in": float(c.get("in", 0)),
                            "dur": float(c["dur"]), "src": c["src"], "name": c.get("name", ""),
                            "gain_db": c.get("gain_db"), "beat": b})
    return out


def _gain_curve(gain, n: int) -> np.ndarray:
    """gain_db (số hoặc [[giây, dB]…]) → dB mỗi bước 5 ms."""
    if gain is None:
        return np.zeros(n)
    if isinstance(gain, (int, float)):
        return np.full(n, float(gain))
    ks = sorted((float(k[0]), float(k[1])) for k in gain)
    return np.interp(np.arange(n) * HOP, [k[0] for k in ks], [k[1] for k in ks])


def sfx_profile(ev: dict) -> dict | None:
    """Đỉnh / lúc bắt đầu nghe thấy của một SFX (giây trên timeline) + mức đỉnh dB; None nếu không giải mã được."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ev['in']:.4f}", "-t", f"{ev['dur']:.4f}", "-i", ev["src"],
                        "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True)
    x = np.frombuffer(p.stdout, np.int16).astype(np.float32) / 32768 if p.returncode == 0 else np.zeros(0, np.float32)
    if len(x) < 240:
        return None
    n = len(x) // 240
    env = 10 * np.log10((x[:n * 240].reshape(n, 240) ** 2).mean(1) + 1e-12) + _gain_curve(ev["gain_db"], n)
    peak_db = float(env.max())
    i_peak = int(np.argmax(env))
    i_start = next(i for i, v in enumerate(env) if v > peak_db - 24)
    return {"a_peak": ev["at"] + i_peak * HOP, "a_start": ev["at"] + i_start * HOP, "level": peak_db}


def pick_sfx(profiles: list[tuple[dict, dict]], cut: float) -> tuple[dict, dict] | None:
    """SFX chuyển cảnh gắn với điểm cắt: đỉnh nằm trong cửa sổ quanh điểm cắt, mức đỉnh cao nhất."""
    near = [(e, p) for e, p in profiles if cut - WIN_BEFORE <= p["a_peak"] <= cut + WIN_AFTER]
    return max(near, key=lambda ep: ep[1]["level"]) if near else None


def build_video_only(spec_path: Path, out: Path) -> tuple[Path, Path]:
    """Spec không chữ, không tiếng → fc_build → xuất h264 270×480 (1 phiên FilmCraft ẩn)."""
    from craftctl import Craft
    s = json.loads(spec_path.read_text(encoding="utf-8"))
    s["tracks"] = [t for t in s["tracks"] if t["type"] == "video" and not t.get("name", "").startswith("text_img")]
    s["name"] = s.get("name", "") + " · chỉ hình (QA)"
    sp, pj, mp4 = out / "video_only.craft.json", out / "video_only.fcproj", out / "video_lowres.mp4"
    sp.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "fc_build.py"), str(sp), str(pj), "--frames", "0"], check=True,
                   capture_output=True)
    with tempfile.TemporaryDirectory() as wd, Craft("filmcraft", Path(wd)) as fc:
        fc.cmd("file.open", {"path": str(pj)})
        fc.cmd("file.exportMedia", {"path": str(mp4), "format": "h264", "scale": 0.25, "audio": False, "crf": 30,
                                    "wait": True})
    return pj, mp4


def video_signal(mp4: Path) -> tuple[np.ndarray, np.ndarray]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=54:96,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 96, 54).astype(np.float32)
    return a.mean(axis=(1, 2)), np.r_[0, np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))]


def video_change(lum: np.ndarray, mot: np.ndarray, cut: float, fps: float) -> tuple[float, float]:
    """(hình bắt đầu đổi, khung đổi mạnh nhất = trọng tâm các khung ≥ 80 % mức đổi lớn nhất) quanh điểm cắt."""
    f0, f1 = max(0, int(round((cut - WIN_BEFORE) * fps))), min(len(lum), int(round((cut + WIN_AFTER) * fps)))
    change = np.abs(lum[f0:f1] - np.median(lum[f0:f0 + 4])) + 2 * mot[f0:f1]
    v_start = next((f0 + i for i, v in enumerate(change) if v > 10), f0) / fps
    top = np.flatnonzero(change >= 0.8 * change.max())
    v_peak = float(np.average(f0 + top, weights=change[top])) / fps
    return v_start, v_peak


def _verdict(ok: bool, block: bool, shift: float, trim: float = 0.0) -> dict:
    return {"status": "ĐẠT" if ok else "LỆCH", "ok": ok, "block": block, "shift": None if ok or trim else round(shift, 3),
            "trim": round(trim, 3) if trim and not ok else None}


def judge(v_start: float, v_peak: float, p: dict | None, fps: float) -> dict:
    """Cắt: đỉnh khớp ± 0,05 s + 1 khung và tiếng không bắt đầu sớm hơn hình > 0,1 s. Đỉnh đã khớp mà chỉ phần dạo đầu của file
    nghe thấy sớm → không dời được: `trim` = số giây cắt đầu file (at và in cùng + trim, đỉnh giữ nguyên)."""
    if p is None:
        return {"status": "KHÔNG SFX", "ok": True, "block": False, "shift": None, "trim": None}
    d = p["a_peak"] - v_peak
    peak_ok = abs(d) <= PEAK_TOL + 1 / fps
    start_deficit = (v_start - EARLY_START) - p["a_start"]
    return _verdict(peak_ok and start_deficit <= 0, d < -BLOCK_EARLY, -d, start_deficit if peak_ok and start_deficit > 0 else 0.0)


def judge_text(t_vis: float, p: dict, peak: bool, fps: float) -> dict:
    """Chữ vào: tiếng (đỉnh nếu `peak`, không thì lúc bắt đầu) rơi 0 … +0,08 s sau khung chữ đầu tiên nhìn thấy (± 1 khung)."""
    d = (p["a_peak"] if peak else p["a_start"]) - t_vis
    return _verdict(-1 / fps <= d <= TEXT_LATE + 1 / fps, d < -BLOCK_EARLY, TEXT_AIM - d)


def judge_punch(t0: float, t1: float, p: dict, fps: float) -> dict:
    """Punch: đỉnh tiếng ở giữa đoạn phóng [t0, t1] (± 0,05 s + 1 khung); chặn khi tiếng sớm hơn đoạn phóng > 0,1 s."""
    d = p["a_peak"] - (t0 + t1) / 2
    return _verdict(abs(d) <= PEAK_TOL + 1 / fps, p["a_peak"] < t0 - BLOCK_EARLY, -d)


def judge_open(p: dict, at: float, fps: float) -> dict:
    """Mở đầu: tiếng bắt đầu nghe thấy ở khung 0–1."""
    return _verdict(p["a_start"] <= 1 / fps + 1e-3, False, -p["a_start"])


def measure(spec: dict, mp4: Path, cuts: list[float], fps: float = 30.0) -> list[dict]:
    lum, mot = video_signal(mp4)
    profiles = [(e, p) for e in sfx_events(spec) if (p := sfx_profile(e))]
    rows = []
    for cut in cuts:
        v_start, v_peak = video_change(lum, mot, cut, fps)
        hit = pick_sfx(profiles, cut)
        ev, p = hit if hit else (None, None)
        rows.append({"beat": "cut", "cut": cut, "v_start": v_start, "v_peak": v_peak, "ref": v_peak, "clip": f"V1 @ {cut:.2f}",
                     "event": ev, "audio": p, "d": p["a_peak"] - v_peak if p else None, **judge(v_start, v_peak, p, fps)})
    return rows


# ---------------------------------------------------------------- nhịp chữ / punch / mở đầu (đo từ spec)
def _norm(x: str) -> str:
    return unicodedata.normalize("NFC", x or "").casefold()


def _first_where(keys: list, ok) -> float | None:
    """Giây (tương đối clip) hình bắt đầu thoả `ok(giá trị)`: nếu khoảng trước đó nội suy thì tính từ keyframe đứng trước
    (đoạn dốc bắt đầu), nếu `hold` thì tại chính keyframe này. None khi không bao giờ thoả."""
    for i, k in enumerate(keys):
        if ok(float(k[1])):
            if i == 0:
                return 0.0
            prev = keys[i - 1]
            return float(k[0]) if len(prev) > 2 and prev[2] == "hold" else float(prev[0])
    return None


def visible_start(clip: dict) -> float:
    """Giây (tương đối clip) khung đầu tiên chữ nhìn thấy: opacity > 0 và crop phải < 100 % (mặc định 0 s)."""
    t = 0.0
    op = clip.get("opacity")
    if isinstance(op, list) and op:
        t = max(t, _first_where(op, lambda v: v > 0) or 0.0)
    for fx in clip.get("effects", []):
        right = fx.get("params", {}).get("right") if fx.get("effect") == "crop" else None
        if isinstance(right, list) and right:
            t = max(t, _first_where(right, lambda v: v < 99.5) or 0.0)
    return t


def text_layers(spec: dict) -> list[dict]:
    """Mọi lớp chữ (track type text hoặc text_img): tên, chữ chuẩn hoá để tìm, mốc khung đầu tiên nhìn thấy (timeline)."""
    out = []
    for t in spec["tracks"]:
        if t.get("type") == "text" or t.get("name", "").startswith("text_img"):
            for c in t["clips"]:
                out.append({"clip": c.get("name", ""), "hay": _norm(f"{c.get('text', '')} {c.get('name', '')}"),
                            "t_vis": float(c["at"]) + visible_start(c), "key": c.get("name", "").startswith("Từ khoá")})
    return out


def punch_beats(spec: dict) -> list[dict]:
    """Cú phóng (E1) trên các clip video: keyframe `motion.scale` tăng ≥ 6 điểm trong ≤ 0,4 s. t0, t1 = đầu, cuối đoạn phóng."""
    out = []
    for t in spec["tracks"]:
        for c in t["clips"] if t.get("type") == "video" and not t.get("name", "").startswith("text_img") else []:
            sc = c.get("motion", {}).get("scale")
            if not isinstance(sc, list) or len(sc) < 2:
                continue
            for a, b in zip(sc, sc[1:]):
                if float(b[1]) - float(a[1]) >= PUNCH_RISE and float(b[1]) >= PUNCH_MIN and 0 < float(b[0]) - float(a[0]) <= PUNCH_SPAN:
                    out.append({"clip": c.get("name", ""), "t0": c["at"] + float(a[0]), "t1": c["at"] + float(b[0])})
    return sorted(out, key=lambda x: x["t0"])


def _pair_text(ev: dict, p: dict, layers: list[dict], peak: bool) -> dict | None:
    """Lớp chữ của SFX chữ: chữ trong « » của tên SFX có trong lớp (từ khoá ưu tiên lớp « Từ khoá »), gần nhất trong PAIR_MAX."""
    a = p["a_peak"] if peak else p["a_start"]
    m = re.search(r"«([^»]*)»?", ev["name"])
    tok = _norm(m.group(1)).strip(" …") if m else ""
    cands = [l for l in layers if tok in l["hay"]] if tok else layers
    if "key_hit" in ev["name"] and any(l["key"] for l in cands):
        cands = [l for l in cands if l["key"]]
    cands = [l for l in cands if abs(l["t_vis"] - a) <= (PAIR_MAX if tok else 0.5)]
    return min(cands, key=lambda l: abs(l["t_vis"] - a)) if cands else None


def _beat_row(beat: str, ev: dict | None, p: dict | None, clip: str, ref: float | None, verdict: dict, peak: bool = True) -> dict:
    d = p["a_peak" if peak else "a_start"] - ref if p and ref is not None else None
    return {"beat": beat, "clip": clip, "ref": ref, "event": ev, "audio": p, "d": d, **verdict}


def measure_beats(spec: dict, fps: float = 30.0) -> list[dict]:
    """Hàng đo cho SFX chữ vào, nhấn nỗi đau (punch) và mở đầu; punch không có SFX nhấn cũng có một hàng « KHÔNG SFX »."""
    layers, punches = text_layers(spec), punch_beats(spec)
    rows, used = [], set()
    for ev in sfx_events(spec, ("open", "text", "pain")):
        p = sfx_profile(ev)
        if p is None:
            continue
        if ev["beat"] == "open":
            rows.append(_beat_row("open", ev, p, "khung 0–1", 0.0, judge_open(p, ev["at"], fps), peak=False))
        elif ev["beat"] == "text":
            peak = any(k in ev["name"] for k in PEAK_KINDS)
            lay = _pair_text(ev, p, layers, peak)
            if lay is None:
                rows.append(_beat_row("text", ev, p, "—", None, {"status": "KHÔNG MỐC", "ok": True, "block": False, "shift": None, "trim": None}))
            else:
                rows.append(_beat_row("text", ev, p, lay["clip"], lay["t_vis"], judge_text(lay["t_vis"], p, peak, fps), peak))
        else:
            near = [(i, b) for i, b in enumerate(punches) if abs((b["t0"] + b["t1"]) / 2 - p["a_peak"]) <= PUNCH_PAIR]
            if not near:
                rows.append(_beat_row("punch", ev, p, "—", None, {"status": "KHÔNG MỐC", "ok": True, "block": False, "shift": None, "trim": None}))
                continue
            i, b = min(near, key=lambda ib: abs((ib[1]["t0"] + ib[1]["t1"]) / 2 - p["a_peak"]))
            used.add(i)
            rows.append(_beat_row("punch", ev, p, b["clip"], (b["t0"] + b["t1"]) / 2, judge_punch(b["t0"], b["t1"], p, fps)))
    for i, b in enumerate(punches):
        if i not in used:
            rows.append(_beat_row("punch", None, None, b["clip"], (b["t0"] + b["t1"]) / 2,
                                  {"status": "KHÔNG SFX", "ok": True, "block": False, "shift": None, "trim": None}))
    return rows


def shifts_of(rows: list[dict]) -> list[dict]:
    """Danh sách sửa cho sfx_shift.py: chỉ clip LỆCH; shift > 0 = dời muộn hơn (giây); hoặc trim = cắt bớt đầu file (giây)."""
    return [{"beat": r.get("beat", "cut"), "clip": r.get("clip", ""), "track": r["event"]["track"],
             "at": round(r["event"]["at"], 3), "name": r["event"]["name"], "src": r["event"]["src"],
             **({"shift": r["shift"]} if r["shift"] is not None else {"trim": r["trim"]})}
            for r in rows if r.get("shift") is not None or r.get("trim")]


def _who(ev: dict | None) -> str:
    return f"{ev['track'].split()[0]} · {ev['at']:.2f} · {ev['name'].replace('SFX ', '')[:34]}" if ev else "—"


def _cut_table(rows: list[dict]) -> None:
    print("| Điểm cắt | Hình bắt đầu | Hình mạnh nhất | SFX khớp (rãnh · at · tên) | Tiếng bắt đầu | Tiếng to nhất | Lệch đỉnh | Dời | |")
    print("|---:|---:|---:|---|---:|---:|---:|---:|---|")
    for r in rows:
        p = r["audio"]
        if p:
            cols = f"{p['a_start']:.2f} ({p['a_start'] - r['v_start']:+.2f}) | {p['a_peak']:.2f} | {p['a_peak'] - r['v_peak']:+.2f}"
        else:
            cols = "— | — | —"
        shift = f"{r['shift']:+.2f}" if r["shift"] is not None else f"cắt {r['trim']:.2f}" if r.get("trim") else ""
        print(f"| {r['cut']:.2f} | {r['v_start']:.2f} | {r['v_peak']:.2f} | {_who(r['event'])} | {cols} | {shift} | "
              f"{r['status']}{' · CHẶN' if r['block'] else ''} |")


def _beat_table(rows: list[dict]) -> None:
    print("| Mốc hình | Clip hình | SFX khớp (rãnh · at · tên) | Tiếng bắt đầu | Tiếng to nhất | Lệch | Dời | |")
    print("|---:|---|---|---:|---:|---:|---:|---|")
    for r in rows:
        p = r["audio"]
        ref = f"{r['ref']:.2f}" if r["ref"] is not None else "—"
        cols = f"{p['a_start']:.2f} | {p['a_peak']:.2f}" if p else "— | —"
        d = f"{r['d']:+.2f}" if r["d"] is not None else "—"
        shift = f"{r['shift']:+.2f}" if r["shift"] is not None else f"cắt {r['trim']:.2f}" if r.get("trim") else ""
        print(f"| {ref} | {r['clip'][:34]} | {_who(r['event'])} | {cols} | {d} | {shift} | "
              f"{r['status']}{' · CHẶN' if r['block'] else ''} |")


def count_by_beat(rows: list[dict]) -> dict[str, dict[str, int]]:
    """{loại nhịp: {n, ĐẠT, LỆCH, CHẶN, khác}} — « khác » = KHÔNG SFX / KHÔNG MỐC."""
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        c = out.setdefault(r.get("beat", "cut"), {"n": 0, "ĐẠT": 0, "LỆCH": 0, "CHẶN": 0, "khác": 0})
        c["n"] += 1
        c["ĐẠT" if r["status"] == "ĐẠT" else "LỆCH" if r["status"] == "LỆCH" else "khác"] += 1
        c["CHẶN"] += bool(r["block"])
    return out


def print_report(rows: list[dict], spec_path: Path, shifts_path: Path) -> None:
    for beat, title in BEAT_TITLES.items():
        part = [r for r in rows if r.get("beat", "cut") == beat]
        if part:
            print(f"\n### {title}")
            (_cut_table if beat == "cut" else _beat_table)(part)
    print("\n| Loại nhịp | Đo | ĐẠT | LỆCH | CHẶN | Không SFX / không mốc |\n|---|---:|---:|---:|---:|---:|")
    for beat, c in count_by_beat(rows).items():
        print(f"| {BEAT_TITLES[beat]} | {c['n']} | {c['ĐẠT']} | {c['LỆCH']} | {c['CHẶN']} | {c['khác']} |")
    bad = [r for r in rows if not r["ok"]]
    blocked = [r for r in rows if r["block"]]
    print(f"\nTổng: {len(rows) - len(bad)}/{len(rows)} ĐẠT · {len(bad)} LỆCH · {len(blocked)} CHẶN (tiếng sớm hơn hình > {BLOCK_EARLY:g} s).")
    if blocked:
        print("→ CHẶN: sửa trước khi giao (rules-details SKILL §7.4).")
    elif bad:
        print("→ LỆCH nhưng KHÔNG chặn giao (qa_sync là báo cáo; cổng G5 chỉ chặn spec_lint / scene_check / edit_rules).")
    if bad:
        new_spec = spec_path.with_name(spec_path.name.replace(".craft.json", ".shifted.craft.json"))
        cmd = " ".join(shlex.quote(str(x)) for x in
                       ("python3", Path(__file__).with_name("sfx_shift.py"), spec_path, shifts_path, new_spec))
        print(f"Cột « Dời » = số giây dời SFX (+ muộn hơn; « cắt x » = bỏ x giây đầu file, đỉnh giữ nguyên). Sửa: {cmd}  → fc_build_fast bản mới → chạy lại qa_sync.")


def main() -> int:
    keep = "--keep" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--keep"]
    if len(args) < 3:
        sys.exit(__doc__)
    spec_path, out = Path(args[0]).resolve(), Path(args[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    cuts = [float(t) for t in args[3:]] or cut_times(spec)
    pj, mp4 = build_video_only(spec_path, out)
    fps = float(spec.get("fps", 30))
    rows = measure(spec, mp4, cuts, fps) + measure_beats(spec, fps)
    if not keep:                                             # clip đo không phải bản giao: xoá sau khi đo
        for f in (mp4, pj, out / "video_only.craft.json"):
            f.unlink(missing_ok=True)
    shifts_path = out / SHIFTS_FILE
    shifts_path.write_text(json.dumps(shifts_of(rows), ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "qa_sync_summary.json").write_text(json.dumps(count_by_beat(rows), ensure_ascii=False, indent=1), encoding="utf-8")
    print_report(rows, spec_path, shifts_path)
    return 1 if any(r["block"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
