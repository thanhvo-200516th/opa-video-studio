#!/usr/bin/env python3
"""v2.6 QA tools: contact_sheet --out ↔ fc_fast_qa --times-file, qa_sync (đo SFX từ spec + hình tổng hợp), sfx_shift,
audit_sfx --out. Không mở FilmCraft. Chạy: ~/.venvs/video-skills/bin/python tests/test_qa_tools.py"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import fc_fast_qa  # noqa: E402
import qa_sync  # noqa: E402
import sfx_shift  # noqa: E402

fails: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"[{'OK' if ok else 'LỖI'}] {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *[str(a) for a in args]], capture_output=True, text=True)


def make_wav(path: Path, peak_at: float, dur: float = 1.5) -> None:
    """WAV 48 kHz: nền rất nhỏ, một cú nổ 40 ms tại peak_at."""
    t = np.arange(int(dur * 48000)) / 48000
    x = 0.001 * np.sin(2 * np.pi * 300 * t)
    m = (t >= peak_at) & (t < peak_at + 0.04)
    x[m] = 0.8 * np.sin(2 * np.pi * 800 * t[m])
    pcm = (x * 32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "48000", "-ac", "1", "-i", "-", str(path)],
                   input=pcm, check=True)


def make_spec(d: Path) -> dict:
    sfx = []
    for i, (name, at, peak_in) in enumerate((("SFX whoosh · chuyển cảnh zoom", 2.0, 0.30),     # đỉnh 2,30 = điểm cắt 2,3
                                             ("SFX shutter · chuyển cảnh shutter", 4.0, 0.60))):  # đỉnh 4,60, cắt 4,5 → trễ 0,1
        w = d / f"s{i}.wav"
        make_wav(w, peak_in)
        sfx.append({"src": str(w), "at": at, "in": 0.0, "dur": 1.2, "name": name})
    key = d / "k.wav"
    make_wav(key, 0.1)
    sfx.append({"src": str(key), "at": 2.25, "in": 0.0, "dur": 0.5, "name": "SFX key_hit · từ khoá «ÔM HẾT»"})  # to nhưng là chữ
    return {"name": "t", "duration": 8.0, "fps": 30,
            "tracks": [{"type": "video", "name": "V1", "clips": [{"at": 0.0, "dur": 2.3, "src": "a"}, {"at": 2.3, "dur": 2.2, "src": "b"},
                                                                  {"at": 4.5, "dur": 3.5, "src": "c"}]},
                       {"type": "audio", "name": "A2 SFX (mở đầu)", "clips": sfx}]}


def test_times_file(d: Path) -> None:
    spec = {"duration": 10.0, "tracks": [{"type": "video", "clips": [{"at": 0.0, "dur": 5}, {"at": 5.0, "dur": 5}]}]}
    sp = d / "s.craft.json"
    sp.write_text(json.dumps(spec))
    tf = d / "sub" / "times.txt"
    r = run(SCRIPTS / "contact_sheet.py", "times", sp, "--full", "--out", tf)
    stdout_times = run(SCRIPTS / "contact_sheet.py", "times", sp, "--full").stdout.split()
    check(r.returncode == 0 and tf.is_file(), "contact_sheet times --out ghi tệp", r.stderr)
    got = fc_fast_qa.read_times_file(tf)
    check(got == [float(x) for x in stdout_times] and len(got) >= 3, "times-file = đúng các mốc in ra", f"{got} vs {stdout_times}")
    tf.write_text("0.5,\n1.25  2.0\n")
    check(fc_fast_qa.read_times_file(tf) == [0.5, 1.25, 2.0], "times-file: xuống dòng / dấu phẩy / nhiều khoảng trắng")
    tf.write_text("0.5 abc")
    try:
        fc_fast_qa.read_times_file(tf)
        check(False, "times-file: chữ không phải số phải báo lỗi")
    except ValueError as e:
        check("abc" in str(e), "times-file: chữ không phải số → ValueError nêu tên mã")
    h = run(SCRIPTS / "fc_fast_qa.py", "--help").stdout
    check("--times-file" in h, "fc_fast_qa --help có --times-file")


def test_qa_sync_core(d: Path) -> None:
    spec = make_spec(d)
    ev = qa_sync.sfx_events(spec)
    check(len(ev) == 2 and all("key_hit" not in e["name"] for e in ev), "sfx_events bỏ SFX chữ (key_hit)", str(ev))
    profiles = [(e, qa_sync.sfx_profile(e)) for e in ev]
    check(all(p for _, p in profiles), "sfx_profile giải mã được")
    check(abs(profiles[0][1]["a_peak"] - 2.30) <= 0.02 and abs(profiles[1][1]["a_peak"] - 4.60) <= 0.02, "đỉnh tiếng = at + vị trí đỉnh trong file",
          str([p["a_peak"] for _, p in profiles]))
    hit = qa_sync.pick_sfx(profiles, 2.3)
    check(hit is not None and hit[0]["name"].endswith("zoom"), "điểm cắt 2,3 gắn whoosh, không gắn tiếng nhấn chữ to hơn")
    # hình tổng hợp: nháy sáng đúng giây 2,3 và 4,5
    fps = 30.0
    lum = np.full(240, 80.0)
    mot = np.zeros(240)
    for t in (2.3, 4.5):
        lum[int(round(t * fps))] = 200.0
        mot[int(round(t * fps))] = 40.0
    v_start, v_peak = qa_sync.video_change(lum, mot, 2.3, fps)
    check(abs(v_peak - 2.3) <= 1 / fps, "video_change: đỉnh hình tại nháy sáng", f"{v_peak}")
    # hai đỉnh đối xứng quanh điểm cắt (zoom + punch) → giữa, không phải bên cao hơn một chút
    mot2 = np.zeros(240)
    mot2[int(round(2.2 * fps))], mot2[int(round(2.4 * fps))] = 22.2, 20.9
    _, vp2 = qa_sync.video_change(np.full(240, 80.0), mot2, 2.3, fps)
    check(abs(vp2 - 2.3) <= 0.02, "video_change: hai đỉnh hai bên → lấy giữa", f"{vp2}")
    rows = []
    for cut in (2.3, 4.5):
        _, vp = qa_sync.video_change(lum, mot, cut, fps)
        e, p = qa_sync.pick_sfx(profiles, cut)
        rows.append({"cut": cut, "v_peak": vp, "event": e, "audio": p, **qa_sync.judge(0, vp, p, fps)})
    check(rows[0]["status"] == "ĐẠT" and rows[0]["shift"] is None, "cắt 2,3: ĐẠT", str(rows[0]["status"]))
    check(rows[1]["status"] == "LỆCH" and not rows[1]["block"] and -0.12 <= rows[1]["shift"] <= -0.08,
          "cắt 4,5: tiếng trễ 0,1 s → LỆCH, KHÔNG chặn, dời −0,1", str((rows[1]["status"], rows[1]["shift"])))
    early = qa_sync.judge(0, 5.0, {"a_peak": 4.8, "a_start": 4.7, "level": -6}, fps)
    check(early["block"] and early["shift"] == 0.2, "tiếng đỉnh sớm hơn hình 0,2 s → CHẶN, dời +0,2")
    check(qa_sync.judge(0, 5, None, fps)["status"] == "KHÔNG SFX", "không có SFX gần → KHÔNG SFX, không phải LỆCH")
    sh = qa_sync.shifts_of(rows)
    check(len(sh) == 1 and sh[0]["track"] == "A2 SFX (mở đầu)" and sh[0]["at"] == 4.0, "shifts_of chỉ ghi clip LỆCH", str(sh))


def test_sfx_shift(d: Path) -> None:
    spec = make_spec(d)
    sp, shp, out = d / "a.craft.json", d / "sh.json", d / "b.craft.json"
    sp.write_text(json.dumps(spec))
    shifts = [{"track": "A2 SFX (mở đầu)", "at": 4.0, "name": "x", "src": spec["tracks"][1]["clips"][1]["src"], "shift": -0.1}]
    shp.write_text(json.dumps(shifts))
    r = run(SCRIPTS / "sfx_shift.py", sp, shp, out)
    new = json.loads(out.read_text())
    moved = new["tracks"][1]["clips"][1]
    check(r.returncode == 0 and abs(moved["at"] - 3.9) < 1e-6, "sfx_shift dời at −0,1", r.stdout + r.stderr)
    check(json.loads(sp.read_text()) == spec, "sfx_shift không sửa spec gốc")
    check(new["tracks"][1]["clips"][0] == spec["tracks"][1]["clips"][0], "clip khác giữ nguyên")
    clamp, _, _ = sfx_shift.apply_shifts(spec, [dict(shifts[0], shift=-9.0)])
    check(clamp["tracks"][1]["clips"][1]["at"] == 0.0, "kẹp không trước 0 s")
    bad = [dict(shifts[0], at=7.7)]
    shp.write_text(json.dumps(bad))
    r2 = run(SCRIPTS / "sfx_shift.py", sp, shp, out)
    check(r2.returncode == 1 and "không khớp" in r2.stdout, "mục không khớp → thoát 1 + nêu rõ")
    check(run(SCRIPTS / "sfx_shift.py", sp, shp, sp).returncode == 2, "tệp ra trùng spec gốc → từ chối")


def test_audit_out(d: Path) -> None:
    src = d / "t.wav"
    make_wav(src, 0.1)
    TICKS = 254_016_000_000
    seq = {"audio_tracks": [{"name": "SFX", "items": [{"item": 1, "start": 0, "duration": TICKS, "source_in": 0}]}],
           "video_tracks": [{"items": [{"start": 0, "duration": 3 * TICKS}]}]}
    proj = {"project": {"items": {"1": {"kind": {"Media": {"media": {"File": {"path": str(src)}}}}},
                                  "2": {"kind": {"Sequence": seq}}}}}
    pd = d / "proj"
    pd.mkdir()
    (pd / "p.fcproj").write_text(json.dumps(proj))
    r = run(SCRIPTS / "audit_sfx.py", pd / "p.fcproj")
    check(r.returncode == 0 and (pd / "qa" / "audit_sfx.json").is_file() and (pd / "qa" / "sfx_manifest.json").is_file(),
          "audit_sfx mặc định ghi vào qa/ cạnh project", r.stdout[-300:] + r.stderr[-300:])
    check("/tmp/" not in r.stdout.replace(str(d), ""), "audit_sfx không in đường dẫn /tmp")
    o = d / "elsewhere"
    r = run(SCRIPTS / "audit_sfx.py", pd / "p.fcproj", "--out", o)
    check(r.returncode == 0 and (o / "audit_sfx.json").is_file(), "audit_sfx --out DIR", r.stderr[-300:])
    check('"repeated_takes": []' in r.stdout, "vẫn in repeated_takes", r.stdout[-300:])


with tempfile.TemporaryDirectory() as t:
    base = Path(t)
    for fn in (test_times_file, test_qa_sync_core, test_sfx_shift, test_audit_out):
        sub = base / fn.__name__
        sub.mkdir()
        fn(sub)

print("\nTẤT CẢ ĐẠT" if not fails else f"\n{len(fails)} LỖI: {fails}")
sys.exit(1 if fails else 0)
