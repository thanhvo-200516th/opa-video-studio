"""Áp luật dựng mới (2026-10-31) lên một timeline spec đã có, ghi ra spec bản mới.

- Mọi điểm cắt (A-roll liền nhau, cảnh chèn vào/ra) có chuyển cảnh 2D, kèm whoosh khi chưa có SFX gần đó.
- Hiệu ứng 3D chỉ dùng đúng 4 lần: 2 chữ + 2 cảnh chèn, ngay lúc xuất hiện. Mọi 3D khác bị gỡ.
- Mọi SFX thay bằng file trong /home/vmiz/Thanh/Media/TNEDIT/02_SFX/sfx hmc (căn đỉnh tiếng vào đúng khoảnh khắc cũ).
- Đường dẫn tài nguyên trỏ về TNEDIT khi có bản ở đó (theo bảng đối chiếu 2026-10-30).

Chạy: ~/.venvs/video-skills/bin/python remix_rules.py IN.craft.json OUT.craft.json "Tên sequence"
rồi dựng: scripts/apps/craft-handoff/tools/fc_build.py OUT.craft.json <project>.fcproj (xem references/pipelines.md GĐ4).
Số đo SFX lưu tạm ở ~/.cache/master-video-edit/sfx_measure_cache.json.
"""
import csv
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

MEDIA = Path("/home/vmiz/Thanh/Media")
TNE = MEDIA / "TNEDIT"
HMC = MEDIA / "sfx hmc"
CACHE = Path.home() / ".cache/master-video-edit/sfx_measure_cache.json"
THREE_D_TR = {"spin_3d", "spinback_3d", "roll_3d", "cube_spin", "flip_over", "flip_motion", "fold_motion", "page_turn", "page_peel"}
THREE_D_FX = {"rotate_3d", "basic_3d"}
OVERLAY_WORDS = ("chuyển cảnh", "vệt sáng", "flash", "tối", "dải", "tách nền", "vignette")

# Chuyển cảnh cho điểm cắt (khung ở 25 fps) và SFX đi kèm
CUT_TR = [("zoom_blur", 5, "whoosh_fast"), ("whip", 6, "whoosh_fast"), ("flash", 3, "whoosh_flash"),
          ("cross_zoom", 6, "whoosh_fast"), ("glitch", 5, "glitch"), ("directional_blur_transition", 6, "swish_short"),
          ("light_leak", 8, "whoosh_flash"), ("blur_dissolve", 6, "swish_short"), ("chroma_leak", 6, "whoosh_flash")]
CARD_IN = [("pop_motion", 8), ("travel_motion", 8), ("pull_motion", 8), ("spring_motion", 9), ("slide", 7)]
CARD_OUT = [("zoom_blur", 5), ("blur_dissolve", 6), ("directional_blur_transition", 6), ("cross_zoom", 5)]

POOLS = {
    "whoosh_fast": ["01_vut_gio_chuyen_canh/vut_gio_chuyen_canh_nhanh_01.wav", "01_vut_gio_chuyen_canh/vut_gio_chuyen_canh_nhanh_02.mp3",
                    "01_vut_gio_chuyen_canh/vut_gio_chuyen_canh_nhanh_03.wav", "01_vut_gio_chuyen_canh/vut_lia_may_nhanh_01.wav",
                    "01_vut_gio_chuyen_canh/vut_lia_may_nhanh_02.wav"],
    "whoosh_flash": ["01_vut_gio_chuyen_canh/vut_gio_kem_chop_sang_01.wav", "01_vut_gio_chuyen_canh/vut_gio_kem_chop_sang_02.wav",
                     "01_vut_gio_chuyen_canh/vut_gio_kem_chop_sang_03.wav", "07_may_anh_chop_sang/man_trap_may_anh_01.mp3"],
    "swish_short": ["01_vut_gio_chuyen_canh/vut_ngan_khung_truot_vao_01.wav", "01_vut_gio_chuyen_canh/vut_ngan_khung_truot_vao_02.wav",
                    "01_vut_gio_chuyen_canh/vut_ngan_doi_chu_01.mp3", "01_vut_gio_chuyen_canh/vut_ngan_doi_chu_02.wav"],
    "riser": ["02_tu_luc_cao_trao/tieng_on_tu_luc_ngan_01.wav", "02_tu_luc_cao_trao/tieng_on_tu_luc_ngan_02.mp3",
              "02_tu_luc_cao_trao/tieng_dien_tu_vut_len_01.mp3", "02_tu_luc_cao_trao/tieng_dien_tu_vut_len_02.wav",
              "02_tu_luc_cao_trao/tieng_on_quet_01.mp3"],
    "impact": ["03_bum_va_cham/bum_tram_chuyen_canh_01.mp3", "03_bum_va_cham/bum_tram_chuyen_canh_02.wav",
               "03_bum_va_cham/va_cham_bat_logo_02.wav", "03_bum_va_cham/rung_tram_am_i_01.mp3", "03_bum_va_cham/rung_tram_am_i_02.mp3"],
    "pop": ["04_ting_chuong/bup_ting_hien_the_01.wav", "04_ting_chuong/bup_ting_hien_the_02.wav", "04_ting_chuong/bup_ting_hien_the_03.mp3",
            "04_ting_chuong/bup_tram_hien_khung_01.wav", "04_ting_chuong/bup_tram_hien_khung_02.wav", "05_go_chu/bip_tung_ky_tu_02.wav"],
    "ding": ["04_ting_chuong/ting_ngan_dai_01.mp3", "04_ting_chuong/ting_ngan_dai_02.wav", "04_ting_chuong/chuong_lap_lanh_01.wav",
             "04_ting_chuong/chuong_lap_lanh_02.mp3", "04_ting_chuong/ting_chuong_kim_loai_01.wav", "04_ting_chuong/ting_chuong_kim_loai_02.wav",
             "04_ting_chuong/lap_lanh_anh_sang_01.wav", "04_ting_chuong/lap_lanh_anh_sang_02.wav", "03_bum_va_cham/va_cham_bat_logo_01.wav"],
    "typing": ["05_go_chu/go_chu_ky_thuat_so_01.wav", "05_go_chu/go_chu_ky_thuat_so_02.mp3", "05_go_chu/bip_tung_ky_tu_01.wav",
               "05_go_chu/go_ban_phim_that_01.wav", "05_go_chu/go_ban_phim_that_02.mp3", "08_dac_biet/bip_cong_nghe_giam_dan_01.wav"],
    "glitch": ["06_nhieu_ky_thuat_so/nhieu_ky_thuat_so_chuyen_canh_01.mp3", "06_nhieu_ky_thuat_so/nhieu_ky_thuat_so_chuyen_canh_02.wav",
               "06_nhieu_ky_thuat_so/tach_nhieu_gat_01.mp3", "06_nhieu_ky_thuat_so/tach_nhieu_gat_02.mp3"],
    "camera": ["07_may_anh_chop_sang/man_trap_may_anh_01.mp3", "07_may_anh_chop_sang/man_trap_may_anh_02.wav"],
    "film": ["07_may_anh_chop_sang/may_chieu_phim_cu_01.wav", "07_may_anh_chop_sang/may_chieu_phim_cu_02.wav",
             "08_dac_biet/bip_cong_nghe_giam_dan_02.wav"],
    "money": ["08_dac_biet/may_tinh_tien_ting_01.mp3", "08_dac_biet/may_tinh_tien_ting_02.mp3", "08_dac_biet/tieng_xu_thang_giai_01.wav"],
}
RULES = [("glitch", ("glitch", "static", "vhs", "scratch", "noise", "tach")), ("camera", ("shutter", "camera", "photo", "snap")),
         ("money", ("cash", "coin", "money", "register", "ka-ching", "kaching")), ("film", ("clock", "tick", "film", "projector", "reel")),
         ("impact", ("heartbeat", "impact", "boom", "hit", "kick", "drum", "bass", "thud", "punch", "slam")),
         ("riser", ("riser", "rise", "swell", "sweep", "build")), ("typing", ("typing", "keyboard", "type", "text", "data", "counter", "click", "ui_")),
         ("pop", ("pop", "bubble", "blip")), ("ding", ("ding", "bell", "chime", "notif", "sparkle", "tada", "success", "magic", "positive")),
         ("swish_short", ("paper", "page", "tear", "swipe", "slide", "whip")),
         ("whoosh_flash", ("flash", "leak", "cinematic", "laser", "long")), ("whoosh_fast", ("whoosh", "swoosh", "transition", "chuyen", "woosh", "air"))]


def classify(path: str) -> str:
    p = Path(path)
    for text in (p.stem.lower(), str(p.parent).lower()):
        for cat, words in RULES:
            if any(w in text for w in words):
                return cat
    return "swish_short"


_cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}


def measure(path: str) -> dict:
    """Mức đỉnh (dBFS), thời điểm đỉnh và độ dài của một file âm thanh."""
    if path not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        a = np.abs(np.frombuffer(raw, dtype=np.float32))
        i = int(a.argmax())
        _cache[path] = {"peak_db": round(float(20 * np.log10(max(float(a[i]), 1e-6))), 2), "peak_t": round(i / 16000, 3), "dur": round(len(a) / 16000, 3)}
    return _cache[path]


def load_path_map() -> dict:
    """Đường dẫn cũ (PR/, Heygen/…) → bản trong TNEDIT, chỉ khi file đích có thật (cột trong bảng vẫn ghi tiền tố cũ "Tài Nguyên Edit/")."""
    m = {}
    with open(TNE / "99_Nhat_Ky_Sap_Xep/bang_doi_chieu_2026-10-30.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            src, dst = row["nguon"], row["dich_trong_Tai_Nguyen_Edit"]
            kept = row["ghi_chu_hoac_trung_voi"]
            for cand in (dst, kept):
                if not cand:
                    continue
                full = TNE / cand.removeprefix("Tài Nguyên Edit/")
                if full.is_file():
                    m[str(MEDIA / src)] = str(full)
                    break
    return m


def first_val(v, default=0.0):
    return (v[0][1] if v and isinstance(v[0], list) else v) if isinstance(v, list) else (default if v is None else v)


def frames(n: int, fps: float) -> int:
    return max(2, round(n * fps / 25))


def is_card(c: dict) -> bool:
    return any(e["effect"] == "rounded_crop" for e in c.get("effects", []))


def main(inp: str, out: str, name: str) -> None:
    spec = json.loads(Path(inp).read_text())
    fps, total = spec["fps"], spec.get("duration") or 0
    spec["name"] = name
    pmap, remapped = load_path_map(), 0
    for t in spec["tracks"]:
        t["name"] = t["name"].replace(" 3D", "").replace("3D ", "")
        for c in t["clips"]:
            if c.get("src") in pmap:
                c["src"], remapped = pmap[c["src"]], remapped + 1

    # 1. Gỡ mọi 3D cũ
    stripped = 0
    for t in spec["tracks"]:
        for c in t["clips"]:
            before = len(c.get("effects", []))
            if "effects" in c:
                c["effects"] = [e for e in c["effects"] if e["effect"] not in THREE_D_FX]
            stripped += before - len(c.get("effects", []))
            for k in ("transition_in", "transition_out"):
                if c.get(k, {}).get("effect") in THREE_D_TR:
                    del c[k]
                    stripped += 1

    vtracks = [t for t in spec["tracks"] if t["type"] == "video"]
    v1 = vtracks[0]["clips"]
    broll = [t for t in vtracks[1:] if t["clips"] and all(c.get("src", "").lower().endswith((".mp4", ".mov")) for c in t["clips"])
             and not any(w in t["name"].lower() for w in OVERLAY_WORDS)]
    texts = [t for t in spec["tracks"] if t["type"] == "text"]

    # 2. Chọn đúng 4 lần 3D: 2 chữ + 2 cảnh chèn, rải đều video
    def nearest(cands, frac):
        return min(cands, key=lambda c: abs(c["at"] - frac * total)) if cands else None
    big = [c for t in texts if "lớn" in t["name"].lower() or "tiêu đề" in t["name"].lower() for c in t["clips"] if c["dur"] >= 0.8]
    accent = [c for t in texts if "nhấn" in t["name"].lower() for c in t["clips"] if c["dur"] >= 0.8]
    cards = [c for t in broll for c in t["clips"] if is_card(c)] or [c for t in broll for c in t["clips"]]
    picks = [("text", min(big or accent, key=lambda c: c["at"])), ("text", nearest(accent or big, 0.55)),
             ("broll", nearest(cards, 0.30)), ("broll", nearest(cards, 0.78))]
    seen, three_d = set(), []
    for kind, c in picks:
        if c is None or id(c) in seen:
            raise SystemExit(f"không chọn được đủ 4 điểm 3D ({kind})")
        seen.add(id(c))
        if kind == "text":
            fx = {"effect": "rotate_3d", "params": {"rot_y": [[0, 75], [0.32, 0, "easeIn"]], "rot_x": [[0, -12], [0.32, 0, "easeIn"]], "perspective": 55}}
        else:
            fx = {"effect": "rotate_3d", "params": {"rot_y": [[0, -80], [0.42, 0, "easeIn"]], "rot_x": [[0, 18], [0.42, 0, "easeIn"]], "perspective": 60}}
            c.pop("transition_in", None)          # 3D là cách cảnh chèn xuất hiện
        c.setdefault("effects", []).append(fx)
        three_d.append((kind, round(c["at"], 2), c.get("text") or Path(c["src"]).stem))

    # 3. Chuyển cảnh ở mọi điểm cắt
    cuts = []                                    # (thời điểm, loại SFX)
    cyc = itertools.cycle(CUT_TR)
    for a, b in zip(v1, v1[1:]):
        if abs(a["at"] + a["dur"] - b["at"]) < 0.02:
            eff, n, sfxcat = next(cyc)
            b["transition_in"] = {"effect": eff, "frames": frames(n, fps)}
            cuts.append((b["at"], sfxcat))
    cin, cout = itertools.cycle(CARD_IN), itertools.cycle(CARD_OUT)
    for t in broll:
        cl = sorted(t["clips"], key=lambda c: c["at"])
        for i, c in enumerate(cl):
            adj_prev = i > 0 and abs(cl[i - 1]["at"] + cl[i - 1]["dur"] - c["at"]) < 0.02
            adj_next = i + 1 < len(cl) and abs(c["at"] + c["dur"] - cl[i + 1]["at"]) < 0.02
            card = is_card(c)
            if id(c) not in seen and "transition_in" not in c:
                if card:
                    eff, n = next(cin)
                else:
                    eff, n, sfxcat = next(cyc)
                    cuts.append((c["at"], sfxcat))
                c["transition_in"] = {"effect": eff, "frames": frames(n, fps)}
            if not adj_next and "transition_out" not in c:
                if card:
                    eff, n = next(cout)
                else:
                    eff, n, sfxcat = next(cyc)
                    cuts.append((c["at"] + c["dur"], sfxcat))
                c["transition_out"] = {"effect": eff, "frames": frames(n, fps)}
            del adj_prev

    # 4. SFX → sfx hmc, giữ khoảnh khắc đỉnh tiếng và mức đỉnh của bản đã duyệt
    atracks = [t for t in spec["tracks"] if t["type"] == "audio"]
    voice = [t for t in atracks if "giọng" in t["name"].lower()]
    music = [t for t in atracks if "nhạc" in t["name"].lower()]
    sfx_tracks = [t for t in atracks if t not in voice and t not in music]
    used, last_t, events = Counter(), {}, []

    def pick(cat: str, moment: float) -> str:
        pool = [str(HMC / f) for f in POOLS[cat]]
        pool.sort(key=lambda p: (used[p], -(moment - last_t.get(p, -99))))
        p = next((p for p in pool if moment - last_t.get(p, -99) > 6), pool[0])
        used[p] += 1
        last_t[p] = moment
        return p

    old = sorted((c for t in sfx_tracks for c in t["clips"]), key=lambda c: c["at"])
    for c in old:
        m = measure(c["src"])
        moment = c["at"] + m["peak_t"] - c.get("in", 0)
        level = m["peak_db"] + first_val(c.get("gain_db"), 0)
        events.append((moment, classify(c["src"]), level, c.get("name", "")))
    moments = [e[0] for e in events]
    added = 0
    for at, cat in cuts:
        if not any(abs(at - mm) < 0.3 for mm in moments):
            events.append((at - 0.02, cat, -17.0 if cat != "glitch" else -20.0, "chuyển cảnh"))
            moments.append(at)
            added += 1
    lanes, new_clips = [], []
    for moment, cat, level, label in sorted(events):
        p = pick(cat, moment)
        m = measure(p)
        at = round(max(0.0, moment - m["peak_t"]), 3)
        dur = round(min(m["dur"], total - at), 3)
        if dur <= 0.05:
            continue
        clip = {"src": p, "at": at, "dur": dur, "gain_db": round(max(-30, min(8, level - m["peak_db"])), 1),
                "name": f"{Path(p).stem} · {label}"[:60]}
        lane = next((i for i, end in enumerate(lanes) if end <= at - 0.001), None)
        if lane is None:
            lanes.append(0)
            new_clips.append([])
            lane = len(lanes) - 1
        lanes[lane] = at + dur
        new_clips[lane].append(clip)
    new_sfx = [{"type": "audio", "name": f"A SFX HMC {i + 1}", "clips": cl} for i, cl in enumerate(new_clips)]
    others = [t for t in spec["tracks"] if t["type"] != "audio"]
    spec["tracks"] = others + voice + new_sfx + music

    # 5. Kiểm luật
    n3d = sum(1 for t in spec["tracks"] for c in t["clips"]
              if any(e["effect"] in THREE_D_FX for e in c.get("effects", []))
              or any(c.get(k, {}).get("effect") in THREE_D_TR for k in ("transition_in", "transition_out")))
    assert n3d == 4, n3d
    missing = [a["at"] + a["dur"] for a, b in zip(v1, v1[1:]) if abs(a["at"] + a["dur"] - b["at"]) < 0.02 and "transition_in" not in b]
    assert not missing, missing
    assert all(str(HMC) in c["src"] for t in new_sfx for c in t["clips"])
    spec.setdefault("notes", []).append(
        "Bản 2026-10-31: mọi điểm cắt có chuyển cảnh; 3D đúng 4 lần (2 chữ, 2 cảnh chèn) lúc xuất hiện; "
        "toàn bộ SFX lấy từ /home/vmiz/Thanh/Media/TNEDIT/02_SFX/sfx hmc; tài nguyên trỏ về TNEDIT. Chưa xuất MP4.")
    Path(out).write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(_cache, ensure_ascii=False))
    ntr = sum(1 for t in spec["tracks"] for c in t["clips"] for k in ("transition_in", "transition_out") if k in c)
    print(json.dumps({"out": out, "remapped_paths": remapped, "removed_3d": stripped, "three_d": three_d,
                      "transitions": ntr, "v1_cuts": len(v1) - 1, "sfx": sum(len(c) for c in new_clips),
                      "sfx_added_for_cuts": added, "sfx_tracks": len(new_clips),
                      "distinct_sfx_files": len(used), "max_reuse": used.most_common(1)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
