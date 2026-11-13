"""Bảng cue âm thanh theo từng chuyển động: chọn SFX từ kho, đặt mức theo độ to đo được, sinh dữ liệu cho AE.

Mức: mỗi cue có độ to tức thời đích M (LUFS, cửa sổ 400 ms, BS.1770) trong bản trộn; gain = M đích − M đo của file
(đo sau khi chuyển WAV, giải mã 2 kênh như AE phát). Thang mức đặt quanh giọng đọc tương lai ở −16 LUFS:
- nhạc nền: tích hợp −31 LUFS (15 LU dưới giọng, chuẩn nền 1.2.3 Minh duyệt);
- tiếng nhỏ (đồng hồ, gõ phím): −32 … −37; sự kiện giao diện: −27 … −33; chuyển cảnh: −25 … −27; logo: −24,5.
Mọi SFX thấp hơn giọng ít nhất 8 LU; đỉnh âm căn vào khoảnh khắc hình (đo đỉnh từng file, không căn đầu file).

Đầu ra:
- assets/sfx/<tên>.wav: file đã chọn, chuyển WAV 48 kHz (AE không đọc OGG; MP3 lệch giờ vì độ trễ bộ mã)
- build/data/am_thanh_cues.jsxinc: OPA.SFX_CUES, OPA.SFX_PEAK, OPA.MUSIC cho build/scenes/am_thanh.jsx
- audio/BANG-CUE-AM-THANH.md: bảng cue đọc được (cảnh, khung, chuyển động, âm, mức, lý do)
- có file giọng đọc: assets/voice/giong-doc-<tên>.wav và OPA.VOICE (gain để giọng ở −16,3 LUFS khi phát; SFX + nhạc
  cộng thêm ~0,3 LU nên bản trộn ra −16); bảng cue thêm cột "Lời" (cue rơi lúc đang nói hay khoảng nghỉ) và "Dưới giọng"
Chạy: python -I tools/am_thanh_cues.py "<thư mục kho sfx>" ["<file giọng đọc>"]
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import lfilter, resample_poly

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phan_tich_sfx import K1, K2, SR, decode, measure  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SFX_DIR, MUSIC = ROOT / "assets" / "sfx", ROOT / "assets" / "music" / "nhac-nen-opa-agent.wav"
OUT_JSX, OUT_MD = ROOT / "build" / "data" / "am_thanh_cues.jsxinc", ROOT / "audio" / "BANG-CUE-AM-THANH.md"
MUSIC_LUFS = -31.0     # 15 LU dưới giọng −16 LUFS
VOICE_DIR, VOICE_LUFS = ROOT / "assets" / "voice", -16.3
SPEECH_DB = -38.0      # RMS 10 ms của file giọng trên mức này = đang nói
# Trần đỉnh thật mỗi cue: âm cực ngắn (click, pop) có M thấp mà đỉnh cao; trùng đỉnh giọng thì đẩy bản trộn quá −2 dBTP
# (bài học B8 trong master prompt). gain = min(đạt M đích, không vượt trần đỉnh).
TP_CAP = -12.0
OPA_KIT = "opa-sonic-logo-c.wav"   # logo âm thanh OPA (V2/V3), giữ để nhận diện thương hiệu

# Tên ngắn → file trong kho (đường dẫn tương đối kho), hoặc file OPA có sẵn trong assets/sfx.
SND = {
    "tick": "04-ui-tech-hud/ui-tick-crisp-A6.wav", "tock": "04-ui-tech-hud/ui-tick-crisp-E6.wav",
    "popA": "03-pops-snaps-elastic/pop-bubble-low-A4.wav", "popC": "03-pops-snaps-elastic/pop-bubble-mid-C#5.wav",
    "popE": "03-pops-snaps-elastic/pop-bubble-high-E5.wav", "accent": "04-ui-tech-hud/ui-swish-accent-tick.wav",
    "ping": "04-ui-tech-hud/ui-soft-ping-night.wav",
    "alert": "04-ui-tech-hud/ui-alert-soft-low.wav", "sent": "04-ui-tech-hud/ui-card-snap-dock.wav",
    "type": "04-ui-tech-hud/uisfx-minimal-typing.mp3", "click": "04-ui-tech-hud/kenney-mouseclick1.wav",
    "press": "04-ui-tech-hud/uisfx-minimal-press.mp3", "release": "packs/uisfx-themes/minimal/release.mp3", "windup": "01-whooshes-transitions/whoosh-deep-windup.wav",
    "thump": "02-impacts-hits/thump-body-punch.wav", "swell": "05-risers-builders/swell-tonal-brass-1.0s.wav",
    "expand": "01-whooshes-transitions/uisfx-glass-expand.mp3", "catch": "03-pops-snaps-elastic/catch-bright-ring.wav",
    "marimba": "04-ui-tech-hud/ui-wood-marimba-tick.wav",
    "bell": "04-ui-tech-hud/ui-chime-question-bell.wav", "toggle": "04-ui-tech-hud/uisfx-minimal-toggle-on.mp3",
    "collapse": "01-whooshes-transitions/uisfx-glass-collapse.mp3", "airy": "01-whooshes-transitions/whoosh-light-airy.wav",
    "success": "04-ui-tech-hud/uisfx-minimal-success.mp3", "whoosh": "01-whooshes-transitions/whoosh-cut-medium.wav",
    "logo": OPA_KIT, "bounce": "03-pops-snaps-elastic/catch-bounce-dry.wav",
}
# Dịch cao độ (cent) để hợp giọng La trưởng của nhạc (Q5 đo b17): success là G–B–D → +200 thành A–C#–E (hợp âm chủ);
# glass expand/collapse là G–B–E cao 43–47 cent → +155 thành A–C#–F#. Dịch bằng đổi tốc độ phát: âm ngắn lại theo tỉ lệ.
SHIFT = {"success": 200, "expand": 155, "collapse": 155}


def cues() -> list[tuple]:
    """(cảnh, khung master của ĐỈNH âm, âm, M đích, tên layer AE (không dấu), chuyển động, lý do)."""
    c = []
    # Cảnh 1 · hook: đồng hồ tích tắc 0,5 s (bỏ khung 0, 30 vì trùng tin nhắn 2, 29), 6 tin nhắn bật theo hợp âm La.
    for f in range(15, 136, 15):
        if f == 30:
            continue
        k = "tick" if f % 30 == 0 else "tock"
        c.append((1, f, k, -32, f"Dong ho {'tich' if k == 'tick' else 'tac'} {f}", "Đồng hồ nảy mỗi 0,5 s",
                  "Tích A6 / tắc E6 xen kẽ, ngang nền nhạc: nhịp thời gian trôi, không đè lời"))
    for i, (f, k) in enumerate(zip((2, 12, 21, 29, 36, 42), ("popA", "popC", "popE") * 2)):
        c.append((1, f, k, -28 + min(i, 3) * 0.5, f"Tin nhan bat {i + 1}", f"Tin nhắn {i + 1} bật lò xo",
                  "Pop A4–C#5–E5 đi lên theo hợp âm La trưởng của nhạc: dồn dập mà vẫn hợp giọng"))
    c.append((1, 79, "accent", -32, "Khoi nhan quet (Moi ngay)", "Khối nhấn trắng quét \"Mỗi ngày?\"",
              "Swish ngắn đúng nhịp quét 8 khung; nằm dưới câu 1 nên hạ còn −32; cùng âm, cùng mức khối nhấn cảnh 3"))
    # Cảnh 2 · nỗi đau: tin mới (cách một), trả lời lặp, cảnh báo, phiếu POS, chip, gõ phím, bấm lưu, Bò lao vào.
    for i, f in enumerate((170, 188, 212, 236, 262, 284, 306, 334, 354, 372)):
        c.append((2, f + 1, "ping", -29.5, f"Tin moi {i + 1}", "Tin khách mới trượt vào hộp thư",
                  "Ping A3 trầm \"night\" cho cảnh đêm; lấy tin cách một để mỗi âm cách ≥ 0,5 s"))
    for i, f in enumerate((176, 248, 320)):
        c.append((2, f, "alert", -28.5, f"Canh bao {i + 1}", f"Icon \"!\" của gạch đầu dòng {i + 1} bật",
                  "Cảnh báo mềm (Rê5, trong giọng La); ba mục song song cùng một âm, cùng mức"))
    for i, f in enumerate((252, 274, 296)):
        c.append((2, f, "sent", -32, f"Tra loi lap {i + 1}", f"Câu trả lời y hệt lần {i + 1} gửi đi",
                  "Cùng một tiếng \"snap\" mỗi lần: nghe ra sự lặp; lần 4 (316) bỏ vì trùng cảnh báo 3 và phiếu POS"))
    for i, f in enumerate((346, 349, 352, 367, 370, 376)):
        c.append((2, f, "type", -34 - (i % 2), f"Go phim {i + 1}", "Vạch gõ dài ra trong ô",
                  "Gõ phím rất nhỏ, xen mức ±1 dB; cách ping tin mới (355, 373) ít nhất 3 khung"))
    c.append((2, 381, "press", -29.5, "Bam luu (than)", "Con trỏ bấm lưu: lớp thân",
              "Press của bộ minimal (đỉnh không nhọn nên đứng trên nhạc mà vẫn dưới trần đỉnh)"))
    c.append((2, 381, "click", -46, "Bam luu (tach)", "Con trỏ bấm lưu: lớp tách",
              "Click chuột Kenney cùng khung, nhập với lớp thân thành một cú bấm; trùng âm /s/ của \"sẽ\" nên rất nhỏ (Q5 v10)"))
    c.append((2, 385, "release", -32.5, "Bam luu (nha)", "Con trỏ nhả", "Release của bộ minimal, nhỏ hơn lúc bấm"))
    c.append((2, 388, "windup", -31, "Bo OPA lao vao", "Bò trắng lao vào từ phải",
              "Whoosh trầm, đỉnh lúc Bò vừa lọt vào hình và nhanh nhất; nằm dưới \"mệt mỏi như thế nào\" nên hạ còn −31"))
    c.append((2, 393, "thump", -28, "Dia sang bat", "Đĩa sáng bật sau lưng Bò, Bò hoá xanh",
              "Tiếng thịch thân trầm cho cú va: rơi đúng khoảng lặng của nhạc"))
    c.append((2, 404, "swell", -28, "Swell sang ngay", "Đĩa nở phủ kín khung (393–404)",
              "Swell hợp âm (giọng La) dâng tới khung trắng cuối, nhạc đáp cảnh 3 ngay sau; dưới chữ cuối câu 2 nên −28"))
    # Cảnh 3 · giải pháp.
    c.append((3, 415, "expand", -28, "Bang OPA mo", "Bảng OPA Agent mở bằng mask",
              "Expand mềm, đỉnh lúc mask mở nhanh nhất; dịch +155 cent về La–Đô♯–Fa♯ cho hợp giọng"))
    c.append((3, 436, "accent", -32, "Khoi nhan quet (1 ket noi)", "Khối nhấn xanh quét \"Chỉ 1 kết nối —\"",
              "Cùng âm, cùng mức khối nhấn cảnh 1; rơi vào khoảng nghỉ 14,46–14,75 s"))
    c.append((3, 441, "catch", -28.5, "Bo dap dau bang", "Bò đáp vào đầu bảng, màu xanh lan ra",
              "\"Catch\" sáng E5: Bò về đúng chỗ"))
    c.append((3, 457, "bell", -27, "Ket noi Pancake POS", "Chip \"Pancake POS\" cắm vào, vòng tỏa",
              "Chuông hai tông sáng (E6–A5) = đã kết nối; âm dày, đỉnh thấp nên nổi trên nhạc thân đầy mà không vượt "
              "trần đỉnh (tiếng chốt khóa bị trần giữ, chìm dưới nhạc 3,8 LU); cách tick tính năng 1 sáu khung"))
    for i, f in enumerate((451, 479, 507, 535, 563)):
        c.append((3, f, "marimba", -28, f"Tinh nang {i + 1}", f"Icon tính năng {i + 1} bật",
                  "Marimba A5 ấm, hợp giọng; năm mục song song cùng âm, cùng mức"))
    c.append((3, 574, "toggle", -29.5, "Nut gat tiep quan", "Nút gạt chạy từ Bò sang nhân viên",
              "Toggle-on lúc nút gạt gần tới đích (đã đi 77 % ở 574)"))
    c.append((3, 639, "collapse", -34, "Cot chu thu R6", "Cột chữ thu R6, bảng hoá xanh",
              "Collapse mềm cùng cú thu đầu của R6, dịch +155 cent như expand; nằm dưới chữ \"OPA Agent\" cuối câu 3 "
              "nên hạ còn −34"))
    c.append((3, 669, "airy", -29, "Nhan vat troi len", "Chủ shop trồi lên trong khung xanh",
              "Whoosh nhẹ đi lên, đỉnh trong khoảng nghỉ 22,19–22,62 s, trước câu 4 hơn 0,3 s (âm nhiều 2–8 kHz)"))
    # Cảnh 4 · giải phóng: chỉ 3 dấu tích và cú nở khung, giữ cảnh thư thả.
    for i, f in enumerate((674, 722, 768)):
        c.append((4, f, "success", -29, f"Dau tich {i + 1}", f"Icon tích mục {i + 1} bật",
                  "Chuông \"xong\" ba nốt đi lên, dịch +2 cung thành La–Đô♯–Mi (hợp âm chủ của nhạc); nốt cuối, cũng là "
                  "đỉnh, rơi đúng lúc icon tích bật; ba mục cùng âm, cùng mức"))
    c.append((4, 898, "whoosh", -26, "Khung xanh no tran", "Khung xanh nở tràn khung sang cảnh 5",
              "Whoosh đỉnh trước cắt 0,03 s (luật whoosh vào cảnh mới)"))
    # Cảnh 5 · CTA.
    c.append((5, 904, "logo", -27, "Sonic logo OPA", "Bò hiện, vòng tỏa đầu tiên",
              "Logo âm thanh OPA (giọng La, đã dùng ở V2/V3); đỉnh trong khoảng nghỉ trước \"OPA Agent\" câu 5 (30,33 s), "
              "đuôi nằm dưới lời nên −27"))
    c.append((5, 966, "bounce", -29, "Nut CTA bat", "Nút URL bật lò xo", "Bounce A4: về chủ âm, kết ý"))
    c.append((5, 1025, "press", -28.5, "Bam nut CTA (than)", "Con trỏ bấm nút CTA: lớp thân",
              "Cùng cú bấm cảnh 2, to hơn 1 dB vì là hành động chốt"))
    c.append((5, 1025, "click", -29, "Bam nut CTA (tach)", "Con trỏ bấm nút CTA: lớp tách", "Lớp tách sáng như cảnh 2"))
    c.append((5, 1030, "release", -31.5, "Bam nut CTA (nha)", "Con trỏ nhả", "Release của bộ minimal"))
    return c


def convert(lib: Path, key: str) -> Path:
    """Chép file của âm vào assets/sfx dạng WAV 48 kHz (giữ số kênh). File OPA có sẵn thì dùng luôn."""
    rel = SND[key]
    if rel == OPA_KIT:
        return SFX_DIR / OPA_KIT
    cents = SHIFT.get(key, 0)
    dst = SFX_DIR / (Path(rel).stem + (f"+{cents}c" if cents else "") + ".wav")
    if not dst.exists():
        af = f"aresample=48000,asetrate={48000 * 2 ** (cents / 1200):.3f},aresample=48000" if cents else "aresample=48000"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(lib / rel), "-af", af, "-c:a", "pcm_s24le", str(dst)],
                       check=True)
    return dst


def music_gain() -> tuple[float, float]:
    """Độ to nhạc như khi AE phát (file mono ra cả 2 kênh nguyên mức, to hơn số đo trên file 3 LU)."""
    i_lufs = measure(MUSIC, MUSIC.parent)["i_lufs"]
    return i_lufs, round(MUSIC_LUFS - i_lufs, 2)


def sfx_stem(rows: list, peaks: dict) -> np.ndarray:
    """Dựng lại stem SFX đúng như AE đặt (bắt đầu = khung/30 − giây tới đỉnh, nhân gain), 2 kênh, dài 36,5 s."""
    n = int(36.5 * SR)
    st, cache = np.zeros((n, 2)), {}
    for r in rows:
        if r["wav"] not in cache:
            cache[r["wav"]] = decode(SFX_DIR / r["wav"])
        x = cache[r["wav"]] * 10 ** (r["gain"] / 20)
        s0 = int(round((r["frame"] / 30 - peaks[r["wav"]]) * SR))
        a, b = max(s0, 0), min(s0 + len(x), n)
        st[a:b] += x[a - s0:b - s0]
    return st


def window_tp(st: np.ndarray, t: float, half: float = 0.04) -> float:
    """Đỉnh thật (×4) của stem trong ±half giây quanh t."""
    seg = st[max(0, int((t - half) * SR)):int((t + half) * SR)]
    pk = max(float(np.abs(resample_poly(seg[:, c], 4, 1)).max()) for c in range(2)) if len(seg) else 0.0
    return 20 * np.log10(pk + 1e-12)


def cap_stacked(rows: list, peaks: dict) -> list[str]:
    """Âm chồng nhau (hai lớp cùng khung, đuôi âm trước) có thể vượt trần dù từng cue đã dưới trần (Q5 đo b17):
    đo đỉnh thật trên stem quanh từng cue, cue nào vượt thì hạ mọi cue cùng khung đúng phần vượt; lặp tới khi đạt."""
    lowered = []
    for _ in range(4):
        st = sfx_stem(rows, peaks)
        over = {}
        for r in rows:
            excess = window_tp(st, r["frame"] / 30) - TP_CAP
            if excess > 0.05:
                over[r["frame"]] = max(over.get(r["frame"], 0.0), excess)
        if not over:
            break
        for r in rows:
            if r["frame"] in over:
                r["gain"] = round(r["gain"] - over[r["frame"]] - 0.05, 1)
                lowered.append(r["label"])
    st = sfx_stem(rows, peaks)
    for r in rows:
        r["tp"] = round(window_tp(st, r["frame"] / 30), 1)
    return sorted(set(lowered))


def voice_prep(src: Path) -> tuple[Path, float, float]:
    """Chép giọng đọc vào assets/voice dạng WAV 48 kHz (MP3 lệch giờ trong AE vì độ trễ bộ mã); gain để về VOICE_LUFS."""
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    dst = VOICE_DIR / f"giong-doc-{src.stem}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ar", "48000", "-c:a", "pcm_s24le", str(dst)], check=True)
    i_lufs = measure(dst, dst.parent)["i_lufs"]
    return dst, i_lufs, round(VOICE_LUFS - i_lufs, 2)


def speaking(path: Path):
    """Hàm t → True khi giọng đang nói tại t (RMS 10 ms của file gốc trên SPEECH_DB)."""
    x = decode(path).mean(axis=1)
    w = int(0.01 * SR)
    n = len(x) // w
    rms = 20 * np.log10(np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(axis=1)) + 1e-9)
    return lambda t: bool(rms[min(max(int(t / 0.01), 0), n - 1)] > SPEECH_DB)


def music_momentary(gain_db: float, path: Path = MUSIC):
    """Hàm t (giây) → độ to tức thời 400 ms của file (mặc định nhạc nền, đã nhân gain) quanh t."""
    y = lfilter(*K2, lfilter(*K1, decode(path) * 10 ** (gain_db / 20), axis=0), axis=0)
    p = np.cumsum(np.vstack([np.zeros((1, 2)), y ** 2]), axis=0)
    n4 = int(0.4 * SR)

    def at(t: float) -> float:
        a = max(0, int(t * SR) - n4 // 2)
        b = min(len(y), a + n4)
        return float(-0.691 + 10 * np.log10(max(((p[b] - p[a]) / (b - a)).sum(), 1e-20)))
    return at


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    lib = Path(sys.argv[1])
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    meas = {}
    for key in SND:
        path = convert(lib, key)
        meas[key] = {**measure(path, path.parent), "wav": path.name}
    i_music, g_music = music_gain()
    music_at = music_momentary(g_music)
    rows, capped = [], []
    for scene, frame, key, target, label, motion, why in sorted(cues(), key=lambda r: r[1]):
        m = meas[key]
        gain = round(min(target - m["m_max"], TP_CAP - m["tp_dbtp"]), 1)
        if target - m["m_max"] > gain:
            capped.append(label)
        rows.append({"scene": scene, "frame": frame, "key": key, "wav": m["wav"], "target": target, "gain": gain,
                     "m_file": m["m_max"], "label": label, "motion": motion, "why": why})
    peaks = {m["wav"]: m["peak_s"] for m in meas.values()}
    stacked = cap_stacked(rows, peaks)
    voice = None
    if len(sys.argv) > 2:
        v_path, v_i, v_gain = voice_prep(Path(sys.argv[2]))
        voice = {"file": v_path.name, "src": Path(sys.argv[2]).name, "i": v_i, "gain": v_gain}
        vo_at, talk = music_momentary(v_gain, v_path), speaking(v_path)
    for r in rows:
        r["m"] = round(r["m_file"] + r["gain"], 1)
        r["over"] = round(r["m"] - music_at(r["frame"] / 30), 1)
        if voice:
            t = r["frame"] / 30
            r["talk"] = talk(t)
            r["under"] = round(vo_at(t) - r["m"], 1) if r["talk"] else None
    OUT_JSX.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSX.write_text(
        "// Sinh bởi tools/am_thanh_cues.py — không sửa tay. [file, khung master của ĐỈNH âm, gain dB, tên layer]\n"
        f"OPA.SFX_PEAK = {json.dumps(peaks, ensure_ascii=True)};\n"
        f"OPA.SFX_CUES = {json.dumps([[r['wav'], r['frame'], r['gain'], r['label']] for r in rows], ensure_ascii=True)};\n"
        f"OPA.MUSIC = {json.dumps({'file': MUSIC.name, 'gain': g_music}, ensure_ascii=True)};\n"
        f"OPA.VOICE = {json.dumps({'file': voice['file'], 'gain': voice['gain']} if voice else None, ensure_ascii=True)};\n",
        encoding="utf-8")
    write_md(rows, lib, i_music, g_music, voice)
    print(f"OK {len(rows)} cue · {len(peaks)} file âm · nhạc {i_music} LUFS → gain {g_music} dB")
    if voice:
        close = [f"{r['label']} {r['under']:.1f}" for r in rows if r["under"] is not None and r["under"] < 10]
        print(f"Giọng {voice['src']}: {voice['i']} LUFS → gain {voice['gain']:+.2f} dB → {VOICE_LUFS} LUFS · "
              f"{sum(1 for r in rows if r['talk'])} cue rơi lúc đang nói · dưới giọng < 10 LU:", ", ".join(close) or "không có")
    print(f"Hạ theo trần đỉnh {TP_CAP:g} dBTP ({len(capped)} cue):", ", ".join(capped))
    print("Hạ thêm vì âm chồng nhau vượt trần:", ", ".join(stacked) or "không có")
    print(f"Stem SFX dựng lại: đỉnh thật lớn nhất quanh các cue {max(r['tp'] for r in rows):.1f} dBTP")
    low = [f"{r['label']} {r['over']:+.1f}" for r in rows if r["over"] < -2]
    print("Thấp hơn nhạc quá 2 LU (theo cửa sổ 400 ms):", ", ".join(low) or "không có")


LEVELS = [
    "## Thang mức (research decibel, 22/10/2026)", "",
    "| Lớp | Mức trong bản trộn | Căn cứ |", "|---|---|---|",
    "| Giọng đọc | −16,3 LUFS trong bản trộn (bản giao chuẩn hoá −16 LUFS, đỉnh thật ≤ −2 dBTP) | Chuẩn Minh chốt; AES TD1008: nhạc −16, lời −18 LUFS; "
    "YouTube chuẩn hoá về khoảng −14 LUFS và không kéo bản nhỏ lên |",
    "| Nhạc nền | −31 LUFS tích hợp (15 LU dưới giọng), dải độ to ≤ 5 LU | Quy trình nền 1.2.3 Minh duyệt (giọng luôn cao hơn nền "
    "≥ 10 LU); hướng dẫn trộn phổ biến: nhạc dưới lời 15–25 dB; WCAG 1.4.7 (AAA): nền dưới lời ≥ 20 dB |",
    "| SFX chuyển cảnh, logo | M −24,5 … −27 | Rơi vào khoảng nghỉ giữa các câu; vẫn dưới giọng ≥ 8 LU |",
    "| SFX sự kiện giao diện | M −27 … −31 | Nhô trên nền nhạc tại chỗ 0–4 LU |",
    "| Tiếng nhỏ (đồng hồ, gõ phím, click) | M −33 … −38 | Âm cực ngắn, sáng: nghe rõ dù M thấp |",
    "| Mỗi cue | Đỉnh thật ≤ −12 dBTP | Âm trùng đỉnh giọng đẩy bản trộn quá trần (bài học B8 trong master prompt) |",
    "| Cả bản ngắn (nội dung quảng cáo) | Độ to ngắn hạn 3 s không vượt mức tích hợp quá 5 LU; đỉnh thật ≤ −1 dBTP | "
    "EBU R 128 s1 (nội dung ngắn); đo theo ITU-R BS.1770 / EBU Tech 3341 |", "",
    "Nguồn: [EBU R 128 s1](https://tech.ebu.ch/docs/r/r128s1.pdf) · [EBU R 128](https://en.wikipedia.org/wiki/EBU_R_128) · "
    "[AES TD1008 (Production Advice)](https://productionadvice.co.uk/td1008/) · "
    "[Telos: loudness cho streaming](https://docs.telosalliance.com/docs/understanding-loudness-for-streaming-audio) · "
    "[WCAG 1.4.7](https://www.disabilityworld.org/toolkit/standards/wcag/1-4-7-low-or-no-background-audio/) · "
    "[Vidpros: nhạc nền quá to](https://vidpros.com/fix-background-music-too-loud-video/).", "",
]
SKIPPED = [
    "## Chuyển động cố ý không gắn âm", "",
    "- Chữ vào/ra (R1–R6): lời đọc sẽ đọc đúng chữ đó, thêm âm sẽ che lời.",
    "- Điện thoại rung lần 7–11 (56–112): nhịp 14 khung lệch nhịp đồng hồ 15 khung, chồng lên nhau thành lộn xộn dưới lời "
    "cảnh 1; sáu lần rung đầu trùng tin nhắn bật nên đã có âm.",
    "- Tin mới thứ 2, 4, 6 (178, 200, 224) và chấm đỏ, \"99+\" nảy: cách tin trước dưới 0,5 s (nghe thành tiếng đúp), "
    "đã có ping của tin kề.",
    "- Trả lời lặp lần 4 (316): trùng cảnh báo 3 và phiếu POS mở.",
    "- Rung quá tải (375–389): nhạc dâng hats và whoosh Bò lao vào đảm nhận.",
    "- Hàng minh họa cảnh 3 (hộp kho, tích, vạch quét, giỏ hàng, người) và chuông 24H: lời cảnh 3 dày, tick tính năng đã "
    "đánh dấu từng hàng.",
    "- Tích bay lên cảnh 4 (684–814), hơi cà phê, Bò thở, nút CTA thở: chuyển động nền liên tục, giữ cảnh 4 thư thả.",
    "- Vòng tỏa thứ hai (916) và con trỏ CTA đi vào (992–1022): logo âm thanh đã phủ; chỉ gắn âm lúc bấm.",
    "- Riser vào màn trắng (4,9 s) và tiếng giấy phiếu POS (10,77 s): bỏ khi lồng giọng 23/10. Riser nằm đè \"tưởng tượng\" "
    "đầu câu 2, tiếng giấy đè đúng chữ \"size\"; cả hai nhiều năng lượng 2–8 kHz, che phụ âm.",
    "- Chip số điện thoại, địa chỉ bay vào ô (338–348, 358–368): bỏ sau rà chéo v10, vì tiếng swish đè đầu âm tiết \"rồi\", "
    "\"từng\" lúc lời đang đọc đúng \"nhập tay từng đơn hàng\"; dời đi thì chỉ cách ping tin mới 1 khung.", "",
]


def vn(x: float, spec: str) -> str:
    """Số kiểu Việt: dấu phẩy thập phân, dấu trừ thật."""
    return format(x, spec).replace(".", ",").replace("-", "−")


def write_md(rows: list, lib: Path, i_music: float, g_music: float, voice: dict | None) -> None:
    scenes = {1: "Cảnh 1 · Hook (0–5 s)", 2: "Cảnh 2 · Nỗi đau (5–13,5 s)", 3: "Cảnh 3 · Giải pháp (13,5–22 s)",
              4: "Cảnh 4 · Giải phóng (22–30 s)", 5: "Cảnh 5 · CTA (30–36 s)"}
    lines = ["# Bảng cue âm thanh — OPA Agent × Pancake", "",
             "Sinh bởi `tools/am_thanh_cues.py` (không sửa tay; sửa cue trong file đó rồi chạy lại và dựng lại AE).",
             f"Kho SFX: `{lib}` (CC0 / MIT). Logo âm thanh: bộ âm OPA. Nhạc nền: tự tổng hợp (`tools/audio/score_agent.py`).",
             "", "**Cột:** khung = khung master (30 fps) mà **đỉnh** âm rơi vào; M đích = độ to tức thời 400 ms muốn có trong "
             f"bản trộn (LUFS); M = độ to thực sau gain (thấp hơn đích khi bị trần đỉnh thật {vn(TP_CAP, 'g')} dBTP giữ lại: "
             "âm cực ngắn, đỉnh nhọn); gain = chỉnh trên layer AE; TP = đỉnh thật của toàn bộ SFX trong ±40 ms quanh đỉnh cue "
             "(dựng lại stem, đã tính các âm chồng nhau; vượt trần thì cả nhóm cùng khung bị hạ).", "",
             f"**Nhạc nền:** `{MUSIC.name}` · đo {vn(i_music, 'g')} LUFS → gain {vn(g_music, '+.2f')} dB → tích hợp "
             f"{vn(MUSIC_LUFS, 'g')} LUFS (15 LU dưới giọng −16 LUFS). Cột **Nhô** = M của cue trừ độ to tức thời của nhạc "
             "quanh khung đó (âm ngắn, sáng vẫn nghe rõ khi Nhô hơi âm vì thang 400 ms tính thấp âm cực ngắn).", ""]
    if voice:
        lines += [f"**Giọng đọc:** `{voice['src']}` → `assets/voice/{voice['file']}` · đo {vn(voice['i'], 'g')} LUFS → gain "
                  f"{vn(voice['gain'], '+.2f')} dB → {vn(VOICE_LUFS, 'g')} LUFS. Cột **Lời** = cue rơi lúc đang nói hay khoảng "
                  "nghỉ; **Dưới giọng** = độ to tức thời của giọng trừ M của cue (chỉ tính lúc đang nói).", ""]
    lines += LEVELS
    for s in sorted(scenes):
        lines += [f"## {scenes[s]}", "",
                  "| Giây | Khung | Chuyển động | Âm (file trong kho) | M đích | M | Nhô | " + ("Lời | Dưới giọng | " if voice else "")
                  + "Gain | TP | Lý do |",
                  "|---:|---:|---|---|---:|---:|---:|" + ("---|---:|" if voice else "") + "---:|---:|---|"]
        for r in (r for r in rows if r["scene"] == s):
            shift = f" (+{SHIFT[r['key']]} cent)" if r["key"] in SHIFT else ""
            talk = ""
            if voice:
                talk = ("đang nói | " + vn(r["under"], ".1f") + " | ") if r["talk"] else "nghỉ | — | "
            lines.append(f"| {vn(r['frame'] / 30, '.2f')} | {r['frame']} | {r['motion']} | `{SND[r['key']]}`{shift} | "
                         f"{vn(r['target'], 'g')} | {vn(r['m'], 'g')} | {vn(r['over'], '+.1f')} | {talk}{vn(r['gain'], '+.1f')} | "
                         f"{vn(r['tp'], 'g')} | {r['why']} |")
        lines.append("")
    lines += SKIPPED
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
