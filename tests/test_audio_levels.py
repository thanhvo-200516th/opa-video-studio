#!/usr/bin/env python3
"""Kiểm audio_levels.py trên âm thanh tổng hợp. Chạy: ~/.venvs/video-skills/bin/python tests/test_audio_levels.py"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import numpy as np  # noqa: E402
from audio_levels import SR, apply_gain, decode, load_rules, measure  # noqa: E402

TOOL = ROOT / "scripts" / "audio_levels.py"
DUR = 12.0


def ff(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def make_sources(d: Path) -> dict[str, Path]:
    """Giọng (hai đoạn, SFX đặt vào khoảng lặng giữa chúng để đỉnh không cộng dồn) = nhiễu băng hẹp điều biên (đỉnh − LUFS ≈ 12 dB như tiếng nói), nhạc = nhiễu hồng, SFX = tiếng chuông ngắn."""
    src = {"voice": d / "voice.wav", "bgm": d / "bgm.wav", "sfx": d / "sfx.wav"}
    ff("-f", "lavfi", "-i", "anoisesrc=d=14:c=white:r=48000:seed=7:a=0.5",
       "-af", "lowpass=f=3500,highpass=f=120,tremolo=f=4:d=0.6,volume=-9dB", str(src["voice"]))
    ff("-f", "lavfi", "-i", "anoisesrc=d=14:c=pink:r=48000:seed=3:a=0.3", "-af", "lowpass=f=6000", str(src["bgm"]))
    ff("-f", "lavfi", "-i", "sine=f=1000:d=0.6:r=48000", "-af", "afade=t=out:st=0.2:d=0.4,volume=-3dB", str(src["sfx"]))
    return src


def clip(src: Path, at: float, dur: float, name: str, **extra) -> dict:
    return {"src": str(src), "at": at, "in": 0.0, "dur": dur, "name": name, **extra}


def make_spec(d: Path, src: dict[str, Path]) -> Path:
    spec = {"name": "T", "fps": 30, "width": 108, "height": 192, "duration": DUR, "tracks": [
        {"type": "video", "name": "V1", "clips": []},
        {"type": "audio", "name": "A1 Giọng", "clips": [clip(src["voice"], 0.0, 5.0, "Giọng 1"),
                                                         {**clip(src["voice"], 7.0, 5.0, "Giọng 2"), "in": 6.0}]},
        {"type": "audio", "name": "A2 SFX", "clips": [clip(src["sfx"], 5.2, 0.6, "SFX A · bell", tier="A"),
                                                       clip(src["sfx"], 6.2, 0.6, "SFX · bell")]},
        {"type": "audio", "name": "Nhạc nền", "clips": [clip(src["bgm"], 0.0, DUR, "Nhạc nền")]},
    ]}
    p = d / "t.craft.json"
    p.write_text(json.dumps(spec, ensure_ascii=False))
    return p


def render_stem(clips: list[dict], out: Path, extra_db: float = 0.0) -> None:
    """Trộn các clip của một track theo at / in / dur / gain_db thành một stem dài DUR."""
    parts, labels = [], []
    for i, c in enumerate(clips):
        ms = int(c["at"] * 1000)
        parts.append(f"[{i}:a]atrim={c['in']}:{c['in'] + c['dur']},asetpts=PTS-STARTPTS,volume={c['gain_db'] + extra_db}dB,"
                     f"adelay={ms}:all=1,apad=whole_dur={DUR}[a{i}]")
        labels.append(f"[a{i}]")
    parts.append("".join(labels) + f"amix=inputs={len(clips)}:normalize=0:duration=longest,atrim=0:{DUR}[o]")
    ins = [x for c in clips for x in ("-i", c["src"])]
    ff(*ins, "-filter_complex", ";".join(parts), "-map", "[o]", "-ar", "48000", str(out))


def mix_master(stems: list[Path], out: Path) -> None:
    ff(*[x for s in stems for x in ("-i", str(s))], "-filter_complex",
       f"amix=inputs={len(stems)}:normalize=0:duration=longest", "-ar", "48000", str(out))


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)


def stems_of(spec: dict, d: Path, bgm_extra_db: float = 0.0) -> dict[str, Path]:
    by = {"voice": 1, "sfx": 2, "bgm": 3}
    out = {}
    for k, i in by.items():
        out[k] = d / f"{k}_stem.wav"
        render_stem(spec["tracks"][i]["clips"], out[k], bgm_extra_db if k == "bgm" else 0.0)
    return out


def statuses(r: subprocess.CompletedProcess) -> dict[str, str]:
    rows = json.loads(r.stdout[r.stdout.index("[\n"):])
    return {x["id"]: x["status"] for x in rows}


def read(path: Path) -> np.ndarray:
    return decode(path, 0.0, 1e6)


def peak_db(x: np.ndarray) -> float:
    return 20 * math.log10(float(np.abs(x).max()))


def rms_db(x: np.ndarray, a: float, b: float) -> float:
    seg = x[int(a * SR):int(b * SR)]
    return 10 * math.log10(float((seg ** 2).mean()) + 1e-20)


def in_rng(v: float, rule: dict) -> bool:
    return rule["min"] <= v <= rule["max"]


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=codec_name,sample_rate,channels:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    return {**j["streams"][0], "duration": float(j["format"]["duration"])}


def test_stems(d: Path, src: dict[str, Path], leveled: dict, rules: dict, master: Path) -> None:
    spec_p = d / "leveled.craft.json"
    out = d / "stems"
    r = run("stems", str(spec_p), str(out))
    assert r.returncode == 0, r.stderr + r.stdout
    assert "xấp xỉ" in r.stdout, r.stdout
    for k in ("voice", "bgm", "sfx"):
        info = probe(out / f"{k}.wav")
        assert (info["codec_name"], info["sample_rate"], info["channels"]) == ("pcm_f32le", "48000", 2), info
        assert abs(info["duration"] - DUR) < 0.01, (k, info)
    # đỉnh voice / sfx / bgm = bản tham chiếu dựng bằng bộ lọc ffmpeg (render_stem); --bgm-chain (HPF + EQ + fade) hạ nhạc
    ref = {}
    for k, i in (("voice", 1), ("sfx", 2), ("bgm", 3)):
        ref[k] = d / f"ref_{k}.wav"
        render_stem(leveled["tracks"][i]["clips"], ref[k])
    for k in ("voice", "sfx", "bgm"):
        a, b = measure(out / f"{k}.wav")["peak"], measure(ref[k])["peak"]
        assert abs(a - b) < 0.1, (k, a, b)
    ref_lufs = measure(ref["bgm"])["lufs"] + 3.01       # nguồn mono đọc thấp hơn hai kênh giống hệt 3 LU
    assert abs(measure(out / "bgm.wav")["lufs"] - ref_lufs) < 0.15, (measure(out / "bgm.wav"), ref_lufs)
    r = run("stems", str(spec_p), str(d / "stems_chain"), "--bgm-chain")
    assert r.returncode == 0, r.stderr
    chained = measure(d / "stems_chain" / "bgm.wav")["lufs"]
    assert ref_lufs - 5.0 < chained < ref_lufs - 0.2, (chained, ref_lufs)
    # check --stems = ba cờ --voice/--bgm/--sfx
    r = run("check", str(master), "--stems", str(out))
    assert r.returncode == 0 and set(statuses(r).values()) == {"PASS"}, r.stdout + r.stderr
    print("stems: 48 kHz stereo float32 dài đúng spec; đỉnh = tham chiếu; check --stems đạt")


def test_keyframe_speed(d: Path, src: dict[str, Path]) -> None:
    tone = d / "tone.wav"
    ff("-f", "lavfi", "-i", "sine=f=1000:d=4:r=48000", str(tone))
    spec = {"name": "K", "duration": 8.0, "tracks": [
        {"type": "audio", "name": "A1 Giọng", "clips": [
            {"src": str(tone), "at": 0.0, "in": 0.0, "dur": 4.0, "name": "Giọng k",
             "gain_db": [[0, -30], [1, -30], [2, -10], [4, -10]]},
            {"src": str(tone), "at": 5.0, "in": 0.0, "dur": 2.0, "name": "Giọng tốc độ", "speed": 2.0, "gain_db": -6.0}]},
    ]}
    p = d / "k.craft.json"
    p.write_text(json.dumps(spec))
    r = run("stems", str(p), str(d / "kst"))
    assert r.returncode == 0, r.stderr + r.stdout
    v = read(d / "kst" / "voice.wav")
    assert abs(len(v) / SR - 8.0) < 0.01, len(v)
    lo, mid, hi = rms_db(v[:, 0], 0.2, 0.8), rms_db(v[:, 0], 1.45, 1.55), rms_db(v[:, 0], 2.5, 3.5)
    assert abs((hi - lo) - 20.0) < 0.5 and abs((mid - lo) - 10.0) < 1.0, (lo, mid, hi)   # nội suy tuyến tính theo dB
    # speed 2: 4 s nguồn → 2 s trên timeline, im lặng sau đó
    on, off = rms_db(v[:, 0], 5.2, 6.8), rms_db(v[:, 0], 7.1, 7.9)
    assert on > -30 and off < -80, (on, off)
    # atempo giữ cao độ: tần số vẫn ~ 1 kHz
    seg = v[int(5.2 * SR):int(6.8 * SR), 0]
    f = np.argmax(np.abs(np.fft.rfft(seg))) * SR / len(seg)
    assert abs(f - 1000) < 15, f
    print("stems: gain_db dạng khoá nội suy theo dB; speed → atempo (đúng thời lượng, giữ cao độ)")


def test_overlap(d: Path, src: dict[str, Path], rules: dict) -> None:
    bell = src["sfx"]
    spec = {"name": "O", "duration": DUR, "tracks": [
        {"type": "audio", "name": "A2 SFX", "clips": [
            clip(bell, 5.00, 0.6, "SFX · chuông 1", tier="B"), clip(bell, 5.05, 0.6, "SFX · chuông 2", tier="B"),
            clip(bell, 9.0, 0.6, "SFX · chuông 3", tier="B")]},
    ]}
    p = d / "o.craft.json"
    p.write_text(json.dumps(spec))
    r = run("plan", str(p), "-o", str(d / "o.levels.craft.json"))
    assert r.returncode == 0, r.stderr + r.stdout
    out = json.loads((d / "o.levels.craft.json").read_text())
    assert all("tier" not in c for c in out["tracks"][0]["clips"]), "đầu ra không được còn khoá tier"
    rep = json.loads(r.stdout[r.stdout.index("{\n"):])
    assert rep["dropped_tier"] == 3 and rep["clips"][0]["tier"] == "B", rep           # bản ghi tier nằm ở báo cáo
    red = [c["overlap_reduction_db"] for c in rep["clips"]]
    assert red[0] == red[1] < -2.0 and red[2] == 0, red                                 # hai chuông chồng bị hạ, chuông lẻ giữ
    g = [c["gain_db"] for c in out["tracks"][0]["clips"]]
    assert abs(g[2] - (rules["sfx_peak_dbfs"]["tier"]["B"] - measure(bell, 0.0, 0.6)["peak"])) < 0.05, g
    assert abs(g[0] - g[2] - red[0]) < 0.05, (g, red)
    r = run("stems", str(d / "o.levels.craft.json"), str(d / "ost"))
    assert r.returncode == 0, r.stderr
    pk = measure(d / "ost" / "sfx.wav")["peak"]
    assert in_rng(pk, rules["sfx_peak_dbfs"]), pk
    print(f"plan: hai chuông chồng 50 ms hạ {red[0]} dB → sfx_peak {pk:.1f} dBFS trong khoảng luật; chuông lẻ giữ gain; không còn tier")


def main() -> None:
    rules = load_rules()
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        src = make_sources(d)
        spec_in = make_spec(d, src)
        before = spec_in.read_text()

        # --- plan ---
        out = d / "leveled.craft.json"
        r = run("plan", str(spec_in), "-o", str(out))
        assert r.returncode == 0, r.stderr + r.stdout
        assert spec_in.read_text() == before, "plan không được sửa spec gốc"
        leveled = json.loads(out.read_text())
        v, sfx, bgm = (leveled["tracks"][i]["clips"] for i in (1, 2, 3))
        pk = lambda c: measure(c["src"], c["in"], c["dur"])["peak"] + c["gain_db"]  # noqa: E731
        for vc in v:
            assert abs(pk(vc) - rules["voice_peak_dbfs"]["target"]) < 0.3, pk(vc)
        assert abs(pk(sfx[0]) - rules["sfx_peak_dbfs"]["tier"]["A"]) < 0.3, pk(sfx[0])      # có tier A
        assert abs(pk(sfx[1]) - rules["sfx_peak_dbfs"]["target"]) < 0.3, pk(sfx[1])         # không tier → target
        print("plan: đỉnh giọng / SFX tier / SFX mặc định về đúng đích")

        # --- mix + check PASS ---
        stems = stems_of(leveled, d)
        master = d / "master.wav"
        mix_master(list(stems.values()), master)
        flags = ["--voice", str(stems["voice"]), "--bgm", str(stems["bgm"]), "--sfx", str(stems["sfx"])]
        r = run("check", str(master), *flags)
        print(r.stdout.split("[\n")[0], end="")
        assert r.returncode == 0, r.stdout + r.stderr
        st = statuses(r)
        assert set(st.values()) == {"PASS"}, st

        # check chỉ có bản mix: các luật cần stem phải SKIP, không FAIL
        r = run("check", str(master))
        st = statuses(r)
        assert st["voice_peak"] == st["bgm_below_voice"] == st["speech_floor"] == "SKIP", st
        assert r.returncode == 2 and "CHƯA KIỂM" in r.stdout, (r.returncode, r.stdout)      # có SKIP → không được coi là đạt
        r = run("check", str(master), "--allow-skip")
        assert r.returncode == 0, r.stdout + r.stderr
        print("check: bản mix chuẩn → PASS, thiếu stem → SKIP, exit 2 (--allow-skip → 0)")

        test_stems(d, src, leveled, rules, master)
        test_keyframe_speed(d, src)
        test_overlap(d, src, rules)

        # --- nhạc quá to → FAIL ---
        loud = stems_of(leveled, d, bgm_extra_db=14.0)
        loud_master = d / "master_loud.wav"
        mix_master(list(loud.values()), loud_master)
        r = run("check", str(loud_master), "--voice", str(loud["voice"]), "--bgm", str(loud["bgm"]), "--sfx", str(loud["sfx"]))
        st = statuses(r)
        assert r.returncode == 1 and st["bgm_below_voice"] == "FAIL" and st["speech_floor"] == "FAIL", (r.returncode, st)
        print("check: nhạc to hơn 14 dB → FAIL (bgm_below_voice, speech_floor)")

        # --- gain_db dạng khoá: giữ hình dạng, khoá lớn nhất = gain tính được ---
        c = {"gain_db": [[0, -3.0], [1, -3.0], [1.5, -40]]}
        apply_gain(c, -9.0)
        assert c["gain_db"] == [[0, -9.0], [1, -9.0], [1.5, -46.0]], c

        # --- rules.json thiếu khoá → dừng, nói rõ khoá nào ---
        bad = json.loads((ROOT / "rules.json").read_text(encoding="utf-8"))
        del bad["params"]["audio"]["master_lufs"]["tol_lu"]
        bad_rules = d / "bad_rules.json"
        bad_rules.write_text(json.dumps(bad))
        for args in (("plan", str(spec_in), "-o", str(d / "x.json")), ("check", str(master))):
            r = run(*args, "--rules", str(bad_rules))
            assert r.returncode != 0 and "master_lufs.tol_lu" in r.stderr, (args[0], r.returncode, r.stderr)
        assert not (d / "x.json").exists()
        print("thiếu khoá rules.json → dừng, không có số mặc định")
    print("TẤT CẢ ĐẠT")


if __name__ == "__main__":
    main()
