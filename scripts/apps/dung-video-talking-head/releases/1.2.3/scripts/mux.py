"""mux.py — ghép hình và tiếng của BUILD (S25, S18); ghi out/QA.json.

Dùng: PYTHONIOENCODING=utf-8 python mux.py <project_dir>

Remotion chỉ render hình (out/_video.mp4, render_video.py --muted); tiếng là các mix đã
chuẩn hoá trên trục vo-clean. Mỗi bản xuất ghép bằng
  ffmpeg -i out/_video.mp4 -i <wav> -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k
         -ar 48000 -af apad -t <duration_f/fps> <mp4>
  (P8, spec 1.1.1 §9.5: duration_f = round(t_end·fps) có thể dài hơn tiếng tới nửa frame — video
  16: 1330,56 ⇒ 1331 f; -shortest của 1.1.0 cắt mất frame hình cuối. Tiếng đệm im tới đúng
  duration_f/fps của picture_lock.json, hình giữ đủ duration_f frame — L11 đếm lại.)
  - out/final.mp4        ← public/mix.wav
  - out/final-nobgm.mp4  ← public/mix-nobgm.wav
  - out/final-social.mp4 ← public/mix.wav lossless (có bed nếu có — Ruling R35, không lấy tiếng
    AAC của final.mp4: thế hệ AAC thứ hai vọt TP thất thường +0,1…+3,2 dB) qua vòng dùng chung
    mix.loudnorm_encoded: loudnorm 2 lượt tuyến tính về loudness.social_lufs, limiter true-peak
    4× trần đầu TP đích − 0,5 dB (file tạm out/_social.wav), ghép như trên, TP đo trên bản đã mã
    hoá như L11; còn vượt thì hạ trần phần vượt + 0,1 dB rồi làm lại, tối đa loud.TP_TRIES lần.
    Lần cuối vẫn vượt: giữ bản đó, ghi QA — cổng hỏng là L11.
final / final-nobgm: vòng R35 đã chạy ở cổng mix của BUILD (mã hoá thử, cùng bộ mã) — bản ghi
của nó đọc từ out/mix_loudness.json.
QA.json (chỉ đo và ghi — cổng là L11 của lint sau mux):
  - xcorr_ms: độ trễ tiếng final.mp4 so với mix.wav (ms, dương = final trễ);
  - cues: mỗi cue của out/sfx_plan.json — đoạn mẫu [start_s, end_s) của nó trên
    public/sfx_stem.wav tìm lại trên tiếng final.mp4 trong ±12 f quanh chỗ đã xếp;
    offset_f dương = final trễ;
  - outputs: mỗi bản xuất — loudness BS.1770 hai kênh (R10), true peak (đo trên bản đã mã
    hoá), độ dài, attempts (số lần của vòng R35), ceiling_dbtp (trần limiter lần cuối).
Thoát mã 1 khi thiếu file vào hoặc ffmpeg lỗi.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from thlib import audio as A
from thlib import mix, rules
from thlib.loud import AAC_ARGS, ffmpeg

FINALS = ("final.mp4", "final-nobgm.mp4", "final-social.mp4")
SEARCH_F = 12          # tìm lại cue trên final trong ±12 f quanh chỗ plan xếp
_ENCODE = ["-c:v", "copy", *AAC_ARGS]


def mux_one(video: Path, wav: Path, out: Path, dur_s: float) -> Path:
    """Hình của `video` (copy) + tiếng `wav` (AAC 192k 48 kHz, đệm im — apad) -> `out`, dài đúng
    `dur_s` = duration_f/fps của khoá hình (P8: không -shortest). Trả `out`."""
    ffmpeg(["-y", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a", *_ENCODE,
            "-af", "apad", "-t", f"{dur_s:.6f}", str(out)])
    return out


def make_social(mix_wav: Path, video: Path, out: Path, loud: dict, dur_s: float) -> dict:
    """final-social.mp4 (R35): `mix_wav` qua vòng dùng chung mix.loudnorm_encoded về
    loudness.social_lufs (encode = ghép với hình `video` như final, dài `dur_s`). Lần cuối vẫn
    vượt TP: giữ bản đó để L11 FAIL. Trả bản ghi vòng {"attempts", "ceiling_dbtp"}."""
    wav = out.with_name("_social.wav")
    try:
        got = mix.loudnorm_encoded(mix_wav, wav, loud["social_lufs"], loud["tp_dbtp"],
                                   lambda w: mux_one(video, w, out, dur_s))
    except mix.TruePeakError as exc:
        print(f"CẢNH BÁO: {exc} — L11 sẽ FAIL")
        got = exc.record
    finally:
        wav.unlink(missing_ok=True)
    return {"attempts": got["attempts"], "ceiling_dbtp": got["ceiling_dbtp"]}


def cue_offset_f(stem: np.ndarray, track: np.ndarray, cue: dict, fps: int) -> float:
    """Độ lệch (frame) của cue trên `track`: đoạn [start_s, end_s) của nó trên stem, tìm
    trong ±SEARCH_F frame quanh start_s bằng tương quan chéo; dương = track trễ."""
    a, b = int(round(cue["start_s"] * A.SR)), int(round(cue["end_s"] * A.SR))
    w = int(round(SEARCH_F * A.SR / fps))
    lo = max(0, a - w)
    k = A.match_at(track[lo: b + w], stem[a:b])     # R217: chuẩn hoá — thô bị giọng to kéo lệch
    return (lo + k - a) * fps / A.SR


def _output(x: np.ndarray) -> dict:
    """Loudness BS.1770 hai kênh (R10), true peak lớn nhất các kênh, độ dài."""
    return {"lufs": round(A.integrated_lufs(x), 2),
            "tp_dbtp": round(max(A.true_peak_db(x[:, ch]) for ch in range(x.shape[1])), 2),
            "duration_s": round(len(x) / A.SR, 4)}


def qa(project: Path, R, loops: dict) -> dict:
    """Số đo QA của ba bản xuất đã ghép (dạng QA.json); `loops` = bản ghi vòng R35 của từng bản
    xuất ({"attempts", "ceiling_dbtp"}), nối vào outputs."""
    out, pub = project / "out", project / "public"
    finals = {name: A.decode(out / name) for name in FINALS}
    final = finals["final.mp4"].mean(axis=1)
    stem = A.decode_mono(pub / "sfx_stem.wav")
    plan = json.loads((out / "sfx_plan.json").read_text(encoding="utf-8"))
    return {
        "xcorr_ms": round(A.xcorr_lag_ms(A.decode(pub / "mix.wav").mean(axis=1), final), 3),
        "cues": [{"id": c["id"], "role": c["role"], "frame": c["frame"],
                  "offset_f": round(cue_offset_f(stem, final, c, R.get("fps")), 3)} for c in plan["cues"]],
        "outputs": {name: {**_output(x), **loops[name]} for name, x in finals.items()},
    }


def run(project: Path) -> dict:
    """Ghép ba bản xuất của `project`, trả QA (chưa ghi file)."""
    R = rules.load(project=project)
    out, pub = project / "out", project / "public"
    video, record, lock = out / "_video.mp4", out / "mix_loudness.json", project / "picture_lock.json"
    for need in (video, pub / "mix.wav", pub / "mix-nobgm.wav", pub / "sfx_stem.wav", out / "sfx_plan.json",
                 record, lock):
        if not need.is_file():
            raise FileNotFoundError(2, "không có file", str(need))
    mixes = json.loads(record.read_text(encoding="utf-8"))
    picture_lock = json.loads(lock.read_text(encoding="utf-8"))
    dur_s = picture_lock["duration_f"] / picture_lock["fps"]
    mux_one(video, pub / "mix.wav", out / "final.mp4", dur_s)
    mux_one(video, pub / "mix-nobgm.wav", out / "final-nobgm.mp4", dur_s)
    social = make_social(pub / "mix.wav", video, out / "final-social.mp4", R.get("loudness"), dur_s)
    return qa(project, R, {"final.mp4": mixes["mix.wav"], "final-nobgm.mp4": mixes["mix-nobgm.wav"],
                           "final-social.mp4": social})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ghép hình + tiếng ra 3 bản xuất, đo QA (S25, S18)")
    ap.add_argument("project",
                    help="Thư mục dự án edit-r<ver> (đã render out/_video.mp4, có public/mix*.wav)")
    project = Path(ap.parse_args(argv).project)
    try:
        result = run(project)
    except FileNotFoundError as exc:
        print(f"FAIL: thiếu file đầu vào của mux: {exc.filename or exc}")
        return 1
    except RuntimeError as exc:
        print(f"FAIL: {exc}")
        return 1
    path = project / "out" / "QA.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for name, got in result["outputs"].items():
        print("%-17s %6.2f LUFS  TP %6.2f dBTP  %.3f s  lần %d, trần limiter %.2f dBTP"
              % (name, got["lufs"], got["tp_dbtp"], got["duration_s"], got["attempts"], got["ceiling_dbtp"]))
    print("xcorr(mix.wav, final.mp4) %+.3f ms" % result["xcorr_ms"])
    for c in result["cues"]:
        print("cue %-16s f%-5d lệch trên final %+.2f f" % (c["id"], c["frame"], c["offset_f"]))
    print("KẾT QUẢ: đã ghép %s, đã ghi %s" % (", ".join(FINALS), path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
