# LEGACY (2026-11-04, THCN 03): ví dụ cũ chạy trọn Motion FX trên media riêng của THCN 03 — CHỈ để tham khảo cách gọi MotionFX.
# Video mới dùng assets/motion-fx/build_spec_q.py (đọc speed_plan.json, chữ theo kịch bản, V1/A1 khớp, không dải tối dưới).
"""Demo Motion FX (2026-11-04): 5 câu đầu THCN 03 dựng lại bằng scripts/motion_fx.py + scripts/sfx_auto.py.

Chữ, chuyển cảnh, SFX theo các reel mẫu đã phân tích (Newbie Edit, 1cho.mejia, Fauzaib, Lens Distortions).
Project THCN 03 gốc không bị đụng: chỉ đọc A-roll, giọng đã lọc và mốc lời.
Chạy: OPA_SKILL_DIR=<thư mục skill> ~/.venvs/video-skills/bin/python example_build_spec.py  → demo.craft.json (rồi fc_build → Demo_MotionFX.fcproj)
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(os.environ.get("OPA_SKILL_DIR") or Path(__file__).resolve().parents[2])   # assets/motion-fx/ → thư mục skill
sys.path.insert(0, str(SKILL / "scripts"))
from build_kit import align_words, pack  # noqa: E402
from cut_plan import Cut, plan_cuts, plan_table  # noqa: E402
from motion_fx import MotionFX  # noqa: E402
from sfx_auto import duck, plan_sfx  # noqa: E402

W = Path(__file__).resolve().parent
ROOT = W.parent
SRC = Path("/home/vmiz/Thanh/Media/TNEDIT/09_Du_An/THCN/Video03_Mau")
TN = Path("/home/vmiz/Thanh/Media/TNEDIT")
AROLL = SRC / "media/THCN03_F1C4_h264.mp4"
VOICE = next((SRC / "work/prep").glob("*_voice_clean_14lufs.wav"))
WORDS = json.loads((SRC / "work/prep/words_prompted.json").read_text())
MK = TN / "06_B-Roll/Stock_Theo_Chu_De_Mixkit"
MUSIC = TN / "08_Nhac_Nen/BGM_Thu_Vien_PR/BGM_Tech_Electronic_Trap_Electro_Vibes_126.mp3"
SHADE_TOP = TN / "07_Assets/Gradient_Vignette_9x16/top_shade_dark_text_zone_1080x1920.png"
FPS, ACCENT, FACE = 30, "#1ECCFC", (600, 920)
KEY_Y, CAP_Y = 500, 1440

SEG = [(3.45, 7.99, "push"), (11.40, 19.36, "flat"), (23.55, 24.58, "punch"), (25.90, 29.62, "push"), (32.70, 36.92, "flat")]
SEG = [(round(a * FPS) / FPS, round(b * FPS) / FPS, z) for a, b, z in SEG]
T0, _t = [], 0.0
for _a, _b, _ in SEG:
    T0.append(_t)
    _t += _b - _a
END = _t
CAPTIONS = [
    "Đừng bắt AI viết kịch bản chung chung nữa, nếu bạn không muốn cầm tờ giấy lên mà chẳng biết quay cảnh gì.",
    "Sau nửa năm đưa AI vào quy trình làm video, thì mình đưa ra một nguyên tắc, đó là AI chỉ làm phần thô, "
    "còn con người sẽ là người check và duyệt cuối cùng.",
    "Mỗi khi bí",
    "ý tưởng, mình sử dụng AI chạy theo 3 điều kiện này. Một,",
    "người xem đang ở mức nào. Hai, là những lỗi sai gì nhìn thấy được bằng mắt trên màn hình.",
]


def tl(i: int, src: float) -> float:
    a, b, _ = SEG[i]
    return T0[i] + min(max(src, a), b) - a


def seg_end(i: int) -> float:
    return T0[i] + SEG[i][1] - SEG[i][0]


def timed_words() -> list[list[tuple]]:
    """Mỗi câu: [(chữ theo kịch bản, start, end)] trên timeline (mốc từ Whisper, chữ từ kịch bản)."""
    out = []
    for i, text in enumerate(CAPTIONS):
        a, b, _ = SEG[i]
        cands = [w for w in WORDS if a - 0.1 <= w["start"] < b]
        toks = text.split()
        times = align_words(toks, cands)
        row = []
        for tok, t in zip(toks, times):
            s = tl(i, t)
            if row:
                s = max(s, row[-1][1])
            nxt = next((w["end"] for w in cands if abs(w["start"] - t) < 0.02), t + 0.25)
            row.append((tok, s, tl(i, nxt)))
        out.append(row)
    return out


def at(row: list, word: str, k: int = 0) -> float:
    """Mốc của lần thứ k từ `word` trong câu (so không phân biệt hoa thường, bỏ dấu câu)."""
    hits = [s for w, s, _ in row if re.sub(r"[,.?!]", "", w).lower() == word.lower()]
    return hits[k]


def zoom_motion(kind: str, dur: float) -> dict | None:
    if kind == "flat":
        return None
    return {"anchor": list(FACE), "position": list(FACE),
            "scale": [[0, 100], [dur, 109]] if kind == "push" else 112}


def broll_scale(path: Path) -> float:
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", str(path)],
                                   capture_output=True, text=True, check=True).stdout.strip().split(","))
    return round(max(1080 / w, 1920 / h) / (1080 / w) * 100, 2)   # media mặc định vừa bề ngang khung


def music_gain(target_lufs: float = -22.5) -> float:          # ~7 dB dưới giọng (mẫu Newbie ~4, @__dviet 6–7)
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(MUSIC), "-t", "60", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return round(target_lufs - float(re.findall(r"I:\s*(-?[\d.]+) LUFS", e)[-1]), 1)


def main() -> None:
    rows = timed_words()
    words_tl = [w for r in rows for w in r]
    skip = [(0.0, rows[0][9][1] - 0.05), (rows[3][6][1] - 0.05, seg_end(3))]   # phụ đề nhường đúng các từ đã có trong từ khoá
    v1, a1 = [], []
    for i, (a, b, zoom) in enumerate(SEG):
        c = {"src": str(AROLL), "at": T0[i], "in": a, "dur": b - a, "audio": False, "name": f"A-roll {i + 1}"}
        if (mo := zoom_motion(zoom, b - a)) is not None:
            c["motion"] = mo
        v1.append(c)
        a1.append({"src": str(VOICE), "at": T0[i], "in": a, "dur": b - a, "name": f"Giọng {i + 1}", "gain_db": -2.4})

    fx = MotionFX(gfx_dir=ROOT / "media/gfx", fps=FPS, accent=ACCENT, key_y=KEY_Y, cap_y=CAP_Y)   # vòng màu mặc định: vàng chủ đạo
    r0, r1, r2, r3, r4 = rows
    idea = MK / "FTG_Idea_Brainstorm_Brainstorming_36908.mp4"
    IDEA_IN, IDEA_DUR = 2.0, 1.5
    last = lambda r, n=4: " ".join(w for w, _, _ in r[-n:])        # noqa: E731
    first = lambda r, n=4: " ".join(w for w, _, _ in r[:n])        # noqa: E731

    # ---------- 1. Phân tích điểm cắt TRƯỚC khi chọn chuyển cảnh ----------
    cuts = [Cut(T0[1], (str(AROLL), SEG[0][1] - 1 / FPS), (str(AROLL), SEG[1][0]), before=last(r0), after=first(r1)),
            Cut(T0[2], (str(AROLL), SEG[1][1] - 1 / FPS), (str(AROLL), SEG[2][0]), before=last(r1), after=first(r2)),
            Cut(T0[3], (str(AROLL), SEG[2][1] - 1 / FPS), (str(idea), IDEA_IN), b_kind="broll", before=last(r2, 3),
                after="[B-roll ý tưởng] " + first(r3, 2)),
            Cut(T0[3] + IDEA_DUR, (str(idea), IDEA_IN + IDEA_DUR - 1 / FPS), (str(AROLL), SEG[3][0] + IDEA_DUR),
                a_kind="broll", before="[B-roll ý tưởng]", after="mình sử dụng AI"),
            Cut(T0[4], (str(AROLL), SEG[3][1] - 1 / FPS), (str(AROLL), SEG[4][0]), before=last(r3), after=first(r4),
                section=True)]
    plan = plan_cuts(cuts)
    (W / "transition_plan.md").write_text("# Phân tích điểm cắt → chuyển cảnh\n\n" + plan_table(plan) + "\n")
    print(plan_table(plan))

    # ---------- 2. Áp chuyển cảnh theo bảng (overlay TNEDIT: khung sáng nhất trúng điểm cắt) ----------
    punch = {i: (v1[i].get("motion") or {}).get("scale") for i in range(len(v1))}
    OVERLAY_KINDS = {"flash_burst", "film_burn", "light_leak", "film_roll", "glitch"}
    used: dict = {}
    broll_clip = None
    for c in plan:
        j = c.info["join"]
        if c.b_kind == "broll":
            mo = {"scale": broll_scale(idea)}
            reveal, ov = j.split(" + ")
            (fx.grid_reveal if reveal == "grid_reveal" else fx.strip_reveal)(str(idea), IDEA_IN, c.t, motion=mo)
            broll_clip = fx.image(str(idea), c.t, IDEA_DUR, lane="gfx_under", name="B-roll · ý tưởng")
            broll_clip.update({"in": IDEA_IN, "audio": False, "motion": mo})
            fx.transition(c.t, ov, clip_after=broll_clip, variant=used.get(ov, 0))
            used[ov] = used.get(ov, 0) + 1
            v1[T0.index(c.t)]["transition_in"] = {"effect": "cross_dissolve", "frames": 2}   # điểm cắt V1 dưới B-roll
            continue
        if c.a_kind == "broll":                                      # ra B-roll: B-roll kết thúc đúng c.t
            if j in OVERLAY_KINDS:
                fx.transition(c.t, j, variant=used.get(j, 0))
            else:
                broll_clip["transition_out"] = {"effect": "zoom_blur", "frames": 5}
                fx.cues.append({"t": c.t, "kind": "whoosh", "why": "B-roll ra (zoom blur)"})
            used[j] = used.get(j, 0) + 1
            continue
        i = T0.index(c.t)
        if j == "zoom + punch":                                   # đổi khung 100 ↔ 112% để jump cut có nghĩa
            prev = punch.get(i - 1)
            v1[i]["motion"] = {"anchor": list(FACE), "position": list(FACE), "scale": 100 if prev not in (None, 100) else 112}
            fx.join(v1[i], "zoom")
        else:                                                     # overlay TNEDIT · ghép sáng tạo · chuyển cảnh FilmCraft
            fx.cut_fx(c.t, j, v1[i], variant=used.get(j, 0), clip_before=v1[i - 1])
        used[j] = used.get(j, 0) + 1

    # ---------- 3. Chữ (mỗi khối một bảng màu) ----------
    t_hook = at(r0, "muốn") + 0.1                     # từ khoá hook giữ ~2,2 s (1,6 s bị chê nhanh)
    fx.keyword_tpl("Đừng bắt AI viết", "Kịch bản", "chung chung", at=0.0, dur=t_hook, palette="gold")
    fx.label_quote("Nguyên tắc", at(r1, "nguyên"), at(r1, "còn") - at(r1, "nguyên"))
    t_kw = at(r1, "người") + 0.05                     # "phần thô" giữ ~0,8 s rồi nhường chỗ cho từ khoá
    fx.collage([("AI chỉ làm", at(r1, "AI", 1), "mx_heavy", 84), ("phần thô", at(r1, "phần"), "brush", 170)],
               end=t_kw + 0.2, y=470, palette="mint")
    fx.keyword_tpl("còn", "Con người", "check và duyệt", at=t_kw, dur=seg_end(1) - t_kw, palette="red")
    fx.keyword_tpl("chạy theo", "3 điều kiện", "này", at=at(r3, "chạy"), dur=seg_end(3) - at(r3, "chạy"), palette="violet")
    fx.label_quote("Điều kiện 1", T0[4], at(r4, "Hai") - T0[4])
    fx.label_quote("Điều kiện 2", at(r4, "Hai"), seg_end(4) - at(r4, "Hai"))
    # Cao trào: chuỗi cắt nhanh B-roll màn hình (vào B-roll khác cảnh → hợp với cắt nhanh), kết bằng flash thật
    shots = [(MK / f, s) for f, s in [("FTG_Video_Editing_cursor_working_on_video_editing_software_close_up_50605.mp4", 1.0),
                                       ("FTG_Video_Editing_computer_screen_view_of_video_editing_software_50610.mp4", 2.0),
                                       ("FTG_Video_Editing_Young_Man_Working_On_Video_Editing_23145.mp4", 3.0),
                                       ("FTG_Video_Editing_youtube_editing_on_a_workstation_41274.mp4", 1.5),
                                       ("FTG_Video_Editing_Boy_Editing_A_Video_On_A_Computer_44071.mp4", 2.5)]]
    burst, t_end = fx.cut_burst([(str(p), s) for p, s in shots], at(r4, "những"), first=0.42, last=0.17)
    for c in burst:
        c["motion"] = {"scale": broll_scale(Path(c["src"]))}
    t_pop = at(r4, "nhìn")
    pop_words = [(w.rstrip("."), s) for w, s, _ in r4 if s >= t_pop - 1e-3]
    fx.word_pop(pop_words, END, y=CAP_Y)
    skip.append((t_pop - 0.05, END))

    # Phụ đề 2 dòng cho mọi câu (không tick), tránh khoảng word_pop
    for i, r in enumerate(rows):
        fx.captions2([(w, s) for w, s, _ in r], seg_end(i), skip=skip, y=CAP_Y)
    print("kiểu phụ đề theo đoạn:", fx.cap_style_log)

    sfx = plan_sfx(fx.cues, words_tl, END, name="Demo_MotionFX_THCN03", gain_offset=-0.5)
    sfx_tracks = pack(sfx, 6)
    g = music_gain()
    t_trans = [c.t for c in plan] + [t_end]                 # nhạc hạ 5 dB quanh mỗi chuyển cảnh để SFX nổi lên
    music = [{"src": str(MUSIC), "at": 0.0, "in": 0.0, "dur": END, "name": "Nhạc nền Trap Electro Vibes (hạ ở chuyển cảnh)",
              "gain_db": duck(g, t_trans, END)}]
    spec = {"name": "Demo Motion FX · THCN 03 (5 câu đầu)", "width": 1080, "height": 1920, "fps": FPS, "duration": END,
            "tracks": [{"type": "video", "name": "V1 A-roll", "clips": v1},
                       {"type": "video", "name": "V2 Dải tối vùng chữ trên",
                        "clips": [{"src": str(SHADE_TOP), "at": 0.0, "dur": END, "name": "Dải tối trên"}]},
                       *fx.tracks("FX · "),
                       {"type": "audio", "name": "A1 Giọng (đã lọc)", "clips": a1},
                       *[{"type": "audio", "name": f"A{n + 2} SFX{' (mở đầu)' if n == 0 else ''}", "clips": t}
                         for n, t in enumerate(sfx_tracks)],
                       {"type": "audio", "name": "Nhạc nền", "clips": music}],
            "markers": [{"at": 0.0, "name": "SFX MỞ ĐẦU", "comment": "sfx_auto chọn theo tên video"}]
            + [{"at": T0[i], "name": f"Câu {i + 1}", "comment": ""} for i in range(1, len(SEG))],
            "notes": ["Demo motion_fx + sfx_auto 2026-11-04. Không xuất MP4 — người dùng tự duyệt."]}
    (W / "demo.craft.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    kinds = {}
    for q in fx.cues:
        kinds[q["kind"]] = kinds.get(q["kind"], 0) + 1
    print(f"dài {END:.2f}s · {sum(len(t['clips']) for t in fx.tracks())} clip FX · {len(sfx)} SFX / {len(sfx_tracks)} track · "
          f"nhạc {g} dB · cue {kinds}")


if __name__ == "__main__":
    main()
