"""Bộ nghe A/B của phim 3D "Thủ môn" (G6) cho Minh — CHƯA NGHE BẰNG TAI.

python -X utf8 tools/audio/score_thumon_ab.py
  → film3d/films/thu-mon/out/g6-am/ab/<nhóm>-<A|B|C>.{mp4,wav} + danh-sach.md + ab.json
Ba nhóm, mỗi nhóm 3 phương án, mỗi phương án một đoạn 3,5–3,8 s cắt từ cả phim:
  (a) a-dap      tiếng Bò đáp (4,40–7,90 s: nhảy cao 10 cm, xoay, đáp, hứng sau lưng)
  (b) b-mep-ban  cú hứng ở mép bàn (8,00–11,50 s: lấy đà, lao 8,42, hứng 8,97, chênh vênh, khựng, lùi về)
  (c) c-tick     tiếng tick hứng (3,00–6,80 s: năm lần hứng đầu)
Cách dựng giống hệt bản chính (cùng nhạc, cùng mọi cue khác), chỉ đổi variant / bật-tắt cue của nhóm; master bằng đúng
chuỗi master.apply_chain với G của master chính (so sánh công bằng ở cùng mức nghe). MP4: đoạn hình có giờ phim
(thu-mon-G2-timecode.mp4) mã hóa lại x264 crf 18, âm AAC 320k như quy ước mux. WAV: 48 kHz 24-bit mono, fade 10 ms hai đầu.
Exit 0 = đạt, 1 = ffmpeg lỗi, 2 = thiếu đầu vào (chạy score_thumon_build.py trước).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import dsp  # noqa: E402
import master as mst  # noqa: E402
import score_thumon_build as B  # noqa: E402
import score_thumon_cues as C  # noqa: E402
import score_thumon_meas as M  # noqa: E402
import score_thumon_music as music_mod  # noqa: E402
import score_thumon_sfx as SFX  # noqa: E402

EARS = "CHƯA NGHE BẰNG TAI"
FADE_S = 0.01


def _lands(sheet: dict, style: str) -> dict:
    return {e["id"]: {"variant": f"{e['variant'].split('/')[0]}/{style}"} for e in sheet["events"] if e["kind"] == "land"}


def _catches(sheet: dict, style: str) -> dict:
    return {e["id"]: {"variant": f"{e['variant']}/{style}"} for e in sheet["events"] if e["kind"] == "catch"}


GROUPS = {
    "a-dap": {"title": "(a) Tiếng Bò đáp", "span": (4.40, 7.90), "probe": "land-3", "variants": {
        "A": ("Thân trầm 110 → 55 Hz + \"tok\" sừng khô 40 ms (đang dùng trong bản chính)", lambda s: _lands(s, "A")),
        "B": ("Thân nặng hơn 100 → 50 Hz, ngân dài ×1,3, không tok, click nhẹ: êm và \"nặng ký\" hơn",
              lambda s: _lands(s, "B")),
        "C": ("\"Gỗ đặc\": thân 130 → 65 Hz ngắn ×0,6 + tiếng gõ gỗ 640 Hz: khô, gọn, ít trầm",
              lambda s: _lands(s, "C"))}},
    "b-mep-ban": {"title": "(b) Cú hứng ở mép bàn (lao 8,42 s, hứng 8,97 s)", "span": (8.00, 11.50), "probe": "save-b7",
                  "variants": {
        "A": ("Thock nặng 160 → 80 Hz + chuông quãng 5 E5–B5 tắt 0,32 s; trượt nốt tới mép bàn (đang dùng)",
              lambda s: {}),
        "B": ("Cú húc như V2: impact accent + sub-drop 0,6 s, sừng rung tắt 3 nhịp — to và \"điện ảnh\" hơn",
              lambda s: {"save-b7": {"variant": "B"}}),
        "C": ("Tối giản: một tick sáng E6 ngân 0,18 s, bỏ tiếng trượt mép bàn — nhẹ, không phô",
              lambda s: {"save-b7": {"variant": "C"}, "slide-lunge": {"sound": False}})}},
    "c-tick": {"title": "(c) Tiếng tick hứng", "span": (3.00, 6.80), "probe": "catch-b4", "variants": {
        "A": ("Tick khô, mỗi lần một nốt leo A4 → C5 → D5 → E5 → G5 (đang dùng)", lambda s: {}),
        "B": ("Tick + tiếng \"tock\" rỗng của lòng O (380 → 330 Hz): thật hơn, có thân", lambda s: _catches(s, "B")),
        "C": ("Một cao độ A4 cho mọi lần (khác seed, mức): bình tĩnh, ít \"nhạc game\"", lambda s: _catches(s, "C"))}},
}


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("không thấy ffmpeg trên PATH")
    return exe


def write_wav24(path: Path, x: np.ndarray) -> None:
    """PCM 24-bit mono 48 kHz (đóng gói 3 byte mỗi mẫu bằng module wave)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    y = np.round(np.clip(np.asarray(x, dtype=np.float64), -1.0, 1.0 - 2 ** -23) * 2 ** 23).astype("<i4")
    raw = y.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(3)
        w.setframerate(dsp.SR)
        w.writeframes(raw)


def excerpt(x: np.ndarray, span: tuple[float, float]) -> np.ndarray:
    a, b = (int(round(t * dsp.SR)) for t in span)
    return dsp.fade_edges(x[a:b], FADE_S * 1000, FADE_S * 1000)


def mux_excerpt(video: Path, wav: Path, span: tuple[float, float], out: Path, title: str) -> None:
    a, b = span
    cmd = [_ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i",
           str(video), "-i", str(wav), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc",
           "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "320k", "-aac_pns", "0", "-ac", "2", "-shortest",
           "-metadata", f"title={title}", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg A/B lỗi ({r.returncode}): {r.stderr.strip()[-600:]}")


def render_variant(sheet: dict, music: np.ndarray, overrides: dict, gain_db: float, tmp: Path) -> np.ndarray:
    stems, _ = B.render_stems(sheet, music, overrides)
    mix_wav, out_wav = tmp / "ab-mix.wav", tmp / "ab-master.wav"
    dsp.write_wav_f32(mix_wav, stems["mix"])
    mst.apply_chain(mix_wav, out_wav, gain_db, B.LIMIT)
    return dsp.read_wav(out_wav)


def probe_clip(sheet: dict, overrides: dict, cid: str) -> dict:
    ev = next(e for e in B.with_overrides(sheet, overrides)["events"] if e["id"] == cid)
    return M.describe(SFX.render_cue(ev, sheet["id"]).x)


def write_index(info: dict, path: Path) -> None:
    lines = [f"# Bộ nghe A/B phim 3D \"Thủ môn\" (G6) — {EARS}", "",
             "Mở từng MP4 (có giờ phim ở góc), nghe trên loa điện thoại rồi tai nghe. Ba phương án trong một nhóm chỉ khác "
             "đúng tiếng được hỏi; nhạc và mọi tiếng khác giống hệt bản chính, cùng mức master.", "",
             "Số đo (của tiếng đại diện): trọng tâm phổ (Hz, thấp = trầm), thời gian tắt −40 dB (ms), crest (dB, cao = gai).",
             ""]
    for g, d in info.items():
        span = "–".join(f"{t:.2f}".replace(".", ",") for t in d["span"])
        lines += [f"## {d['title']}", "", f"Đoạn {span} s · tiếng đại diện `{d['probe']}`", "",
                  "| Phương án | File | Mô tả | Trọng tâm (Hz) | Tắt −40 dB (ms) | Crest (dB) |", "|---|---|---|---|---|---|"]
        for k, v in d["variants"].items():
            p = v["probe"]
            lines.append(f"| {k} | `ab/{v['mp4']}` | {v['desc']} | {p['trong_tam_hz']} | {p['tat_40db_ms']} | "
                         f"{p['crest_db']} |")
        lines.append("")
    lines += ["Câu hỏi: mỗi nhóm chọn A, B hay C (hoặc \"không cái nào\" + vì sao). Bản chính đang dùng phương án A."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


VIDEO_BAN1 = C.FILM / "out" / "g2-duyet" / "thu-mon-G2-timecode.mp4"


def run() -> int:
    rec = B.load_build()
    sheet = B.require_fresh_cues()                 # cue sheet đúng events.json / timeline.js hiện tại
    ids = {e["id"] for e in sheet["events"]}
    missing = sorted({d["probe"] for d in GROUPS.values()} - ids)
    if missing:
        raise B.InputError(f"bộ A/B này dành cho bản 1 (Minh đã chọn phương án A ở G6); cue sheet hiện tại thiếu {missing}")
    B.require_same_md5(rec)                        # master (lấy G) đúng bản dựng từ cue sheet này
    gain = float(rec["master"]["gain_db"])
    video = VIDEO_BAN1
    if not video.is_file():
        raise B.InputError(f"thiếu bản hình {video}")
    out_dir = B.PATHS["ab"]
    out_dir.mkdir(parents=True, exist_ok=True)
    music = music_mod.render_music(sheet)
    with tempfile.TemporaryDirectory(prefix="thumon-ab-") as tmp:
        info = {g: render_group(sheet, music, g, d, gain, video, Path(tmp)) for g, d in GROUPS.items()}
    (out_dir / "ab.json").write_text(json.dumps({"nghe": EARS, "gain_db": gain, "video": B.rel(video), "groups": info},
                                                ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_index(info, out_dir / "danh-sach.md")
    print(f"→ {out_dir / 'danh-sach.md'} · {EARS}")
    return 0


def render_group(sheet: dict, music: np.ndarray, g: str, d: dict, gain: float, video: Path, tmp: Path) -> dict:
    """Ba phương án của một nhóm: WAV 24-bit + MP4 có giờ phim + số đo tiếng đại diện. File trung gian ở tmp."""
    out_dir = B.PATHS["ab"]
    info = {"title": d["title"], "span": d["span"], "probe": d["probe"], "variants": {}}
    for k, (desc, make) in d["variants"].items():
        ov = make(sheet)
        x = excerpt(render_variant(sheet, music, ov, gain, tmp), d["span"])
        wav, mp4 = out_dir / f"{g}-{k}.wav", out_dir / f"{g}-{k}.mp4"
        write_wav24(wav, x)
        mux_excerpt(video, wav, d["span"], mp4, f"Thủ môn G6 A/B {g}-{k} — {EARS}")
        info["variants"][k] = {"desc": desc, "overrides": ov, "wav": wav.name, "mp4": mp4.name,
                               "probe": probe_clip(sheet, ov, d["probe"]), "md5_wav": B.md5(wav)}
        print(f"{g}-{k}: {mp4.name} · {desc}")
    return info


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        return run()
    except (B.InputError, C.InputError, ValueError) as e:
        print(f"LỖI: {e}")
        return 2
    except (RuntimeError, OSError) as e:
        print(f"LỖI: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
