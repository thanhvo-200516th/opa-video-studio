"""Bộ nghe thử cho cổng H1 (KH §3.9 "CLI âm", TK §10): 22 WAV + phổ PNG + index.md trong out/audio-kit/.

Chạy tại gốc dự án: python tools/audio/preview_kit.py   (npm run audio:kit)
Exit 0 = ghi đủ 22 WAV; 2 = thiếu/hỏng cues.json. WAV PCM 16-bit mono 48 kHz (phát được trên điện thoại).
Clip SFX đệm 0,2 s lặng trước, 0,3 s sau; nhạc 30 s giữ nguyên độ dài.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from scipy.io import wavfile  # noqa: E402

import dsp  # noqa: E402
import score_v2  # noqa: E402
import score_v2_sched  # noqa: E402
import sonic_logo  # noqa: E402
import synth  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SHEET_ID = "v2-khong-bo-sot-khach"
OUT = ROOT / "out" / "audio-kit"
PRE_S, POST_S = 0.2, 0.3
EXPECTED = 22


@dataclass(frozen=True)
class KitItem:
    name: str     # tên file, không đuôi
    group: str
    desc: str
    x: np.ndarray
    source: str   # cue / seed
    pad: bool = True


def load_sheet(path: Path) -> dict:
    """Đọc cues.json; thiếu file hoặc sai schema → ValueError."""
    if not path.is_file():
        raise ValueError(f"thiếu {path}")
    sheet = json.loads(path.read_text(encoding="utf-8"))
    if sheet.get("schema") != 2 or sheet.get("id") != SHEET_ID:
        raise ValueError(f"{path}: schema/id không đúng (cần schema 2, id {SHEET_ID})")
    return sheet


def _cue(sheet: dict, cid: str, variant: str | None = None) -> tuple[np.ndarray, str]:
    ev = next((e for e in sheet["events"] if e["id"] == cid), None)
    if ev is None:
        raise ValueError(f"sheet thiếu cue {cid}")
    if variant is not None:
        ev = {**ev, "variant": variant}
    span = f"[{ev['f'] - ev['durF']:g}, {ev['f']:g})" if ev.get("anchor") == "end" and "durF" in ev else f"f{ev['f']:g}"
    src = f"cue {cid} {span}" + (f", biến thể {variant}" if variant else "") + f", seed {sheet['id']}:{cid}"
    return synth.render_cue(ev, sheet["id"]).x, src


def _fundamental(x: np.ndarray, lo: float = 150.0, hi: float = 450.0) -> float:
    p = np.abs(np.fft.rfft(x * np.hanning(len(x)), 1 << 17))
    f = np.fft.rfftfreq(1 << 17, 1 / dsp.SR)
    m = (f >= lo) & (f <= hi)
    return float(f[m][np.argmax(p[m])])


def _pings(sheet: dict) -> dict[str, tuple[np.ndarray, str]]:
    """Ping A3 và E4: ưu tiên seed của cue trong phim, thiếu thì dò seed audio-kit:ping:k."""
    found: dict[str, tuple[np.ndarray, str]] = {}
    cands = [(e["id"], None) for e in sheet["events"] if e["kind"] == "ping"] + [(None, k) for k in range(64)]
    for cid, k in cands:
        if cid is not None:
            x, src = _cue(sheet, cid)
        else:
            seed = f"audio-kit:ping:{k}"
            x, src = synth.ping(seed).x, f"seed {seed} (không có trong phim)"
        note = min(("A3", "E4"), key=lambda nm: abs(_fundamental(x) - dsp.hz(nm)))
        found.setdefault(note, (x, src))
        if len(found) == 2:
            return found
    raise ValueError("không tìm được seed cho cả ping A3 và E4")


def build_items(sheet: dict) -> list[KitItem]:
    sid = sheet["id"]
    items: list[KitItem] = []

    def add(name, group, desc, cid, variant=None):
        x, src = _cue(sheet, cid, variant)
        items.append(KitItem(name, group, desc, x, src))

    add("impact-accent", "hit", "HIT #1 (accent)", "hit-accent")
    add("impact-logo", "hit", "HIT #2 (logo)", "hit-logo")
    add("subdrop-accent", "sub-drop", "sub-drop #1", "subdrop-accent")
    add("subdrop-logo", "sub-drop", "sub-drop #2", "subdrop-logo")
    add("whoosh-cut-light", "whoosh", "cắt đêm → sáng", "whoosh-day")
    add("whoosh-cut", "whoosh", "cắt sang KK 6", "whoosh-thesis")
    add("whoosh-windup", "whoosh", "whoosh lấy đà — chỉ bản A/B (Điểm quyết 6)", "whoosh-charge")
    add("riser", "riser", "riser trước khoảng lặng", "riser")
    add("tick-ui-e6", "tick UI", "tick UI E6 (bản chính)", "tick-reply-1")
    add("tick-ui-cs7", "tick UI", "tick UI C#7 (phương án)", "tick-reply-1", "C#7")
    add("tick-catch-a4", "tick catch", "tick catch A4 (bản chính)", "tick-catch-1")
    add("tick-catch-e5", "tick catch", "tick catch E5 (phương án)", "tick-catch-1", "E5")
    for note, (x, src) in sorted(_pings(sheet).items()):
        items.append(KitItem(f"ping-{note.lower()}", "ping", f"ping {note}", x, src))
    add("thump", "thump", "mõm chạm (có / không?)", "thump")
    add("snort", "snort", "snort sau reveal", "snort")
    add("swell", "swell", "swell đảo vào Outro", "swell")
    for v in ("a", "c"):
        clip = sonic_logo.sonic_logo(v, f"{sid}:sonic-logo")
        items.append(KitItem(f"sonic-logo-{v}", "sonic logo", f"sonic logo ({v}) riêng", clip.x,
                             f"sonic_logo('{v}'), seed {sid}:sonic-logo"))
    for v in ("a", "c"):
        items.append(KitItem(f"opa-sonic-logo-{v}", "sonic logo", f"hit + sub + sonic logo ({v}) theo gainDb cue",
                             sonic_logo.logo_stem(v, sheet), f"logo_stem('{v}')"))
    items.append(KitItem("music-30s", "nhạc", "nhạc 30 s (stem nhạc, chưa SFX, chưa master)",
                         score_v2.render_music(sheet), "render_music, seed v2-music", pad=False))
    return items


def _write_wav(path: Path, x: np.ndarray) -> None:
    peak = float(np.max(np.abs(x)))
    if not np.isfinite(peak) or peak > 1.0:
        raise ValueError(f"{path.name}: đỉnh {peak} vượt 1 hoặc không hữu hạn")
    wavfile.write(str(path), dsp.SR, np.round(x * 32767).astype(np.int16))


def _write_png(path: Path, x: np.ndarray, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = np.arange(len(x)) / dsp.SR
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 4.5), sharex=True)
    a1.plot(t, x, linewidth=0.5)
    a1.set_ylim(-1, 1)
    a1.set_title(title, fontsize=9)
    with np.errstate(divide="ignore"):   # đoạn đệm lặng cho log10(0); ô đó vẽ màu nền
        a2.specgram(x, NFFT=1024, Fs=dsp.SR, noverlap=768, cmap="magma")
    a2.set_ylim(0, 12000)
    a2.set_xlabel("giây")
    a2.set_ylabel("Hz")
    fig.tight_layout()
    fig.savefig(str(path), dpi=100)
    plt.close(fig)


def _index(rows: list[str], sheet: dict) -> str:
    tl = score_v2_sched.timeline(sheet)
    fps = float(sheet["fps"])
    head = [
        "# Bộ nghe thử âm V2 (out/audio-kit)", "",
        "**CHƯA NGHE BẰNG TAI.** Tự tổng hợp 100 % (tools/audio/*.py, seed cố định); không file âm ngoài.",
        "Sinh bằng `npm run audio:kit` (`python tools/audio/preview_kit.py`). WAV PCM 16-bit mono 48 kHz.",
        "Clip SFX: đỉnh −1 dBFS, đệm 0,2 s trước và 0,3 s sau. Nhạc 30 s: stem nhạc, phần thân ≈ −20 LUFS, chưa master.",
        "Bản A/B trong phim (whoosh lấy đà, hit logo −3 dB, sonic logo c, pad đuôi) do gói E ghi ở"
        " `out/v2-khong-bo-sot-khach/audio-ab/`.", "",
        "| File | Nhóm | Nội dung | Dài (s) | Momentary max (LUFS) | Nguồn |", "|---|---|---|---|---|---|",
    ]
    tail = [
        "", "## Cần nghe (loa điện thoại + tai nghe, TK §10, Điểm quyết 6)", "",
        "- Điểm quyết 6: lao trong im lặng hay thêm `whoosh-windup`; hit logo −6 dB hay −3 dB (bản A/B của E);"
        " `opa-sonic-logo-a` hay `opa-sonic-logo-c`.",
        "- tick UI: `tick-ui-e6` hay `tick-ui-cs7`.",
        "- tick catch: `tick-catch-a4` hay `tick-catch-e5`.",
        "- ping (`ping-a3`, `ping-e4`): có giống âm báo ứng dụng không.",
        "- thump: giữ hay bỏ.",
        f"- `music-30s`: motif ô 2 (E5–A4–C5) có nghe ra không; band rút ở {tl.drop / fps:.2f} s;"
        f" lặng {tl.cut / fps:.2f}–{tl.hit / fps:.2f} s; dừng đúng {tl.stop / fps:.2f} s.",
    ]
    return "\n".join(head + rows + tail) + "\n"


def main() -> int:
    try:
        sheet = load_sheet(ROOT / "src" / "audio" / "cues" / f"{SHEET_ID}.json")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"LỖI: {e}")
        return 2
    items = build_items(sheet)
    if len(items) != EXPECTED or len({it.name for it in items}) != EXPECTED:
        raise ValueError(f"bộ nghe có {len(items)} mục, cần {EXPECTED} tên khác nhau")
    png_dir = OUT / "png"
    png_dir.mkdir(parents=True, exist_ok=True)
    keep = {it.name for it in items}
    for old in list(OUT.glob("*.wav")) + list(png_dir.glob("*.png")):   # bỏ file cũ không còn trong danh sách
        if old.stem not in keep:
            old.unlink()
    rows = []
    for it in items:
        x = it.x
        if it.pad:
            x = np.concatenate([np.zeros(int(PRE_S * dsp.SR)), x, np.zeros(int(POST_S * dsp.SR))])
        _write_wav(OUT / f"{it.name}.wav", x)
        _write_png(png_dir / f"{it.name}.png", x, f"{it.name}: {it.desc}")
        mm = dsp.momentary_max(it.x)
        rows.append(f"| [{it.name}.wav]({it.name}.wav) · [phổ](png/{it.name}.png) | {it.group} | {it.desc} | "
                    f"{len(x) / dsp.SR:.2f} | {mm:.1f} | {it.source} |")
        print(f"OK {it.name}.wav  {len(x) / dsp.SR:.2f} s  momentary max {mm:.1f} LUFS")
    (OUT / "index.md").write_text(_index(rows, sheet), encoding="utf-8")
    n = len(list(OUT.glob("*.wav")))
    print(f"TỔNG: {n} WAV, index.md → {OUT}")
    return 0 if n == EXPECTED else 1


if __name__ == "__main__":
    sys.exit(main())
