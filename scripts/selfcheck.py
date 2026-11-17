#!/usr/bin/env python3
"""selfcheck — kiểm skill opa-video-studio chạy được trọn gói trên máy này (không cần skill nào khác).

    python3 selfcheck.py [--quick]        # --quick: bỏ phần chạy thử npx (chậm)

Kiểm: (1) file tham chiếu trong SKILL.md có thật; (2) công cụ trong scripts/apps/ (craft-handoff, facecammaxxing,
motion-sfx-audio-mastering, video-use, video-understand, …) có đủ file lõi; (3) công cụ dòng lệnh, venv Whisper, font,
template FilmCraft, USB; (4) chạy thử nhẹ từng script (py_compile + --help / status). Không ghi gì ra ngoài thư mục tạm.
Thoát 0 = không có LỖI (CẢNH BÁO vẫn cho qua).
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "scripts" / "apps"
HOME = Path.home()
VENV = HOME / ".venvs" / "video-skills" / "bin" / "python"
results: list[tuple[str, str, str]] = []          # (mức, mục, chi tiết)


def note(level: str, item: str, detail: str = "") -> None:
    results.append((level, item, detail))


def check_apps() -> None:
    """Mọi công cụ lõi vendored trong scripts/apps/ có thật (thay cho kiểm skill anh em)."""
    core = ["craft-handoff/tools/fc_build.py", "craft-handoff/tools/craftctl.py", "craft-handoff/tools/fc_export.py",
            "talking-head-premiere/scripts/audit_sfx.py", "dviet-viral-text-audio-edit/scripts/clean_and_master_voice.py",
            "motion-sfx-audio-mastering/scripts/master.py", "motion-sfx-audio-mastering/scripts/audio/qa_audio.py",
            "facecammaxxing/scripts/fcm.py", "ae-script-builder/templates/du-an-ae/tools/ec.py",
            "ae-script-builder/templates/du-an-ae/build/lib.jsx", "ae-template-customizer/scripts/parse_aep_timings.py",
            "video-use/helpers/transcribe.py", "video-understand/scripts/understand_video.py",
            "auto-footage/scripts/footage.py", "auto-footage/scripts/selftest.py",
            "strip-media-metadata/scripts/strip_metadata.py", "hyperframes-audio/scripts/carve.mjs",
            "video-style-trainer/scripts/style_trainer.py",
            "dung-video-talking-head/releases/1.2.3/scripts/stage.py",
            "dung-video-talking-head/releases/1.2.3/scripts/make_cards.py"]
    for rel in core:
        note("OK" if (APPS / rel).is_file() else "LỖI", f"scripts/apps/{rel}")
    nested = [str(p) for p in ROOT.rglob("SKILL.md") if p != ROOT / "SKILL.md"]
    note("LỖI" if nested else "OK", "không có SKILL.md lồng nhau", "; ".join(nested[:3]))


def check_files() -> None:
    if not (ROOT / "SKILL.md").is_file():
        note("CẢNH BÁO", "SKILL.md", "chưa có")
        return
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for rel in sorted(set(re.findall(r"`((?:references|scripts)/[A-Za-z0-9_./-]+\.(?:md|json|py))`", text))):
        note("OK" if (ROOT / rel).is_file() else "LỖI", f"file {rel}")


def check_tools() -> None:
    for b in ("ffmpeg", "ffprobe", "uvx", "rvm-matte", "deep-filter", "clearvoice-enhance", "resemble-enhance",
              "audio-separator", "auto-editor", "ffmpeg-normalize", "pycaps", "filmcraft", "effectcraft", "npx", "node"):
        p = shutil.which(b) or (str(HOME / ".local/bin" / b) if (HOME / ".local/bin" / b).exists() else None)
        note("OK" if p else "LỖI", f"lệnh {b}", p or "không tìm thấy")
    r = subprocess.run([str(VENV), "-c", "import faster_whisper, PIL, numpy"], capture_output=True, text=True)
    note("OK" if r.returncode == 0 else "LỖI", "venv video-skills (faster-whisper, PIL)", r.stderr[-200:])
    cache = glob.glob(str(HOME / ".cache/huggingface/hub/models--mobiuslabsgmbh--faster-whisper-large-v3-turbo"))
    note("OK" if cache else "CẢNH BÁO", "model Whisper large-v3-turbo trong cache", "" if cache else "lần đầu sẽ tải")
    fonts = subprocess.run(["fc-list", ":", "family", "style"], capture_output=True, text=True).stdout
    for fam, style in (("SF Pro Display", "Medium"), ("SF Pro Display", "Semibold"), ("SF Pro Display", "Heavy"),
                       ("SF Pro Display", "Heavy Italic"), ("Playfair Display", "Bold Italic"), ("Great Vibes", "Regular"),
                       ("Montserrat", "Black"), ("Bebas Neue", "Regular")):
        ok = any(fam in l and style in l for l in fonts.splitlines())
        note("OK" if ok else "LỖI", f"font {fam} {style}")
    tpl = sorted(glob.glob(str(HOME / ".local/share/filmcraft/Graphics Templates/dviet-v2-*.fcgt")))
    note("OK" if len(tpl) == 6 else "CẢNH BÁO", "6 template FilmCraft [DViet v2]", f"có {len(tpl)}")
    usb = Path("/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/AI Video/prompts/MASTER_VIDEO_EDITOR_VI.md")
    note("OK" if usb.exists() else "CẢNH BÁO", "USB Over Powers (playbook HyperFrames, kho SFX lớn)", "" if usb.exists() else "chưa cắm — loại B/C/D thiếu playbook")
    tnedit = os.environ.get("TNEDIT_DIR", str(HOME / "Thanh/Media/TNEDIT"))
    for d in (f"{tnedit}/02_SFX/Thu_Vien_SFX_PR", f"{tnedit}/08_Nhac_Nen/BGM_Thu_Vien_PR", f"{tnedit}/01_Font/Google_Fonts_PR",
              f"{tnedit}/02_SFX/sfx hmc"):
        n = len(os.listdir(d)) if os.path.isdir(d) else 0     # kho media riêng của máy gốc — máy khác không có thì chỉ cảnh báo
        note("OK" if n else "CẢNH BÁO", f"kho {d}", f"{n} file" if n else "không có (kho media riêng; đặt kho của bạn rồi sửa đường dẫn)")


def run(cmd: list[str], timeout: int = 90, cwd: str | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, (r.stdout + r.stderr)[-300:]
    except (subprocess.TimeoutExpired, OSError) as e:
        return 99, str(e)


def check_text_fx(tmp: Path) -> None:
    """24 hiệu ứng chữ sinh được spec hợp lệ (mốc ≥ 0, thời lượng > 0) và trang xem trước khớp snippets.json."""
    out = tmp / "snip" / "s.json"
    out.parent.mkdir()
    code, msg = run([str(VENV), str(ROOT / "scripts/text_fx_demo.py"), "--snippets", str(out)])
    if code != 0:
        note("LỖI", "text_fx 24 hiệu ứng", msg.strip()[-150:])
        return
    snip = json.loads(out.read_text(encoding="utf-8"))
    bad = [f"{k}: {c.get('name')} at={c['at']:.3f}" for k, v in snip.items() for tr in v["tracks"] for c in tr["clips"]
           if c["at"] < 0 or c["dur"] <= 0]
    note("OK" if len(snip) == 24 and not bad else "LỖI", "text_fx 24 hiệu ứng sinh spec hợp lệ", "; ".join(bad[:3]) or f"{len(snip)} hiệu ứng")
    shipped = json.loads((ROOT / "assets/text-fx/snippets.json").read_text(encoding="utf-8"))
    strip = lambda d: re.sub(r'"/[^"]*/([^"/]+\.png)"', r'"\1"', json.dumps(d, sort_keys=True, ensure_ascii=False))  # noqa: E731
    stale = [k for k in snip if strip(snip[k]) != strip(shipped.get(k))]
    note("OK" if not stale else "CẢNH BÁO", "assets/text-fx/snippets.json khớp thư viện",
         f"cũ: {', '.join(stale)} — chạy text_fx_demo.py --snippets" if stale else "")
    html = (ROOT / "assets/text-fx/preview/XEM_TRUOC_24_HIEU_UNG.html").read_text(encoding="utf-8")
    ok = ("const SNIP = " + json.dumps(shipped, ensure_ascii=False) + ";") in html
    note("OK" if ok else "CẢNH BÁO", "trang xem trước 24 hiệu ứng khớp snippets.json", "" if ok else "cập nhật const SNIP")
    probe_sfx = tmp / "pop.wav"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=880:d=0.3", str(probe_sfx)])
    code, msg = run([str(VENV), str(ROOT / "scripts/build_kit.py"), "sfx", str(probe_sfx)])
    note("OK" if code == 0 else "LỖI", "build_kit.py đo SFX", msg.strip()[-120:])
    check_silence_cut(tmp)
    check_silence_onset(tmp)
    check_motion_fx(tmp)


def check_motion_fx(tmp: Path) -> None:
    """Motion FX: mọi hàm sinh clip hợp lệ, cue có trong sfx_catalog, sfx_auto ra clip có file thật."""
    code = r"""
import json, sys
sys.path.insert(0, sys.argv[1] + '/scripts')
import os
import motion_fx as M
from motion_fx import MotionFX
from cut_plan import OPTIONS
from sfx_auto import plan_sfx, CATALOG
fx = MotionFX(gfx_dir=sys.argv[2], key_y=500, cap_y=1440)
fx.keyword_tpl('Đừng bắt', 'Kịch bản', 'chung chung', 0.0, 1.6)
fx.caption2('Nếu bạn không', 'muốn cầm tờ', 1.6, 1.4)
fx.collage([('AI chỉ làm', 3.0, 'mx_heavy', 84), ('phần thô', 3.4, 'brush', 170)], end=4.2)
fx.word_pop([('một', 4.2), ('hai', 4.4), ('ba', 4.6)], 5.2)
fx.label_quote('Nguyên tắc', 4.2, 1.0)
fx.asset_3d('/dev/null', 4.5, 1.8, pos=(760, 560), scale=38.0, anim='float', cue='pop')
fx.strip_reveal('/dev/null', 2.0, 6.0); fx.grid_reveal('/dev/null', 2.0, 7.0); fx.leak_overlay(8.0)
fx.cut_burst([('/dev/null', 0.0)] * 4, 8.5)
v = {'src': '/dev/null', 'at': 6.0, 'dur': 2.0}; fx.join(v, 'flash')
for i, kd in enumerate(['flash_burst', 'film_burn', 'light_leak', 'glitch', 'film_roll']): fx.transition(10.0 + i, kd, clip_after={'at': 10.0 + i})
for i, kd in enumerate(sorted(M.COMBO_KINDS)):
    fx.cut_fx(16.0 + i, kd, {'src': '/dev/null', 'at': 16.0 + i, 'dur': 1.0}, clip_before={'src': '/dev/null', 'at': 15.0 + i, 'in': 2.0, 'dur': 1.0})
# luật màu vòng 9: chữ key luôn phát sáng (vàng / trắng siêu nhẹ), không hồng / cam / xanh lá trong vòng, màu buộc dùng phải phát sáng
glow = lambda c: next((e['params'] for e in c.get('effects', []) if e['effect'] == 'wonder_glow'), None)
g_gold = glow(fx.keyword_tpl(None, 'Vàng', None, 30.0, 2.0, palette='gold')[0])
g_red = glow(fx.keyword_tpl(None, 'Đỏ', None, 32.0, 2.0, palette='red')[0])
g_col = glow(fx.collage([('a', 34.0, 'mx_heavy', 84), ('b', 34.2, 'brush', 170)], end=35.0)[-1])
g_lime = glow(fx.caption2('màu', 'xanh lá', 36.0, 1.0, color=M.PALETTES['lime']['cap'])[1])
cap = fx.caption2('Nếu bạn không', 'muốn cầm tờ giấy', 38.0, 1.5)       # dòng 2 vàng viết tay mảnh, trong vùng phụ đề
cap_ok = cap[1]['_role'] == 'thin_script' and cap[1]['size'] > cap[0]['size'] and cap[1]['position'][1] + fx.ink_bottom('thin_script', cap[1]['size'], cap[1]['text']) <= 1440 + 200
# lần 11: font phụ đề phân tầng theo đoạn 3–5 nhịp; trong 5 nhịp liên tiếp ≤ 3 cụm viết tay; ≥ 3 kiểu xuất hiện
n0 = len(fx.cap_style_log)
long = [(f'từ{i}' + ('.' if i % 7 == 6 else ''), 40.0 + i * 0.45) for i in range(84)]
fx.captions2(long, 40.0 + 84 * 0.45)
seq = [k for _, k in fx.cap_style_log[n0:]]
cap_ok = cap_ok and len(set(seq)) >= 3 and all(seq[i:i + 5].count('script') <= 3 for i in range(len(seq)))
# lần 12: kiểu vào đa dạng, không lặp liền nhau; phụ đề không cam / hồng
for g in ('cap', 'key'):
    es = [e for _, gg, e in fx.entrance_log if gg == g]
    cap_ok = cap_ok and len(set(es)) >= min(5, len(es)) and all(a != b for a, b in zip(es, es[1:]))
cap_ok = cap_ok and not set(M.CAPTION_ROTATION) & {'fire', 'coral', 'pink', 'violet'} and 'violet' in M.CAP_GLOW_REQUIRED
# lần 16: chữ khớp giọng — mốc từ đầu sau lặng kéo về chỗ tiếng thật; dòng 2 chỉ hiện khi bắt đầu được nói
import subprocess
from build_kit import refine_words
wav = sys.argv[2] + '/rw.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-t', '1', '-i', 'anullsrc=r=16000:cl=mono', '-f', 'lavfi', '-t', '1',
                '-i', 'sine=f=300:sample_rate=16000', '-filter_complex', '[0][1]concat=n=2:v=0:a=1', wav], check=True)
rw = refine_words([{'text': 'a', 'start': 0.75, 'end': 1.4}], wav)
c2 = fx.caption2('Nhiều editor mới', 'khi edit video', 60.0, 2.0, entrance='type', word_times=([0.05, 0.35, 0.65], [0.95, 1.15, 1.4]))
cap_ok = cap_ok and abs(rw[0]['start'] - 1.0) < 0.05 and abs(c2[1]['at'] - 60.9) < 0.04
# lần 19: chữ chính sau người — track matte đảo trên ảnh từ khoá, lớp người khớp motion / src của V1
blk = fx.keyword_tpl('dẫn', 'Sau đầu', None, 70.0, 2.0, palette='gold', y=400, size=218)
v1s = [{'src': '/dev/null', 'at': 69.0, 'in': 10.0, 'dur': 1.5, 'motion': {'scale': 150}},
       {'src': '/dev/null', 'at': 70.5, 'in': 20.0, 'dur': 3.0, 'motion': {'scale': [[0, 150], [3.0, 160]]}}]
mts = fx.behind_person(blk, v1s, '/dev/null')
tmk = [c for c in blk if any(e['effect'] == 'track_matte' and e['params']['reverse'] for e in c.get('effects', []))]
cap_ok = cap_ok and len(mts) == 2 and abs(mts[0]['in'] - 11.0) < 1e-3 and len(tmk) >= 1 and all(c.get('_role') != 'mx_med' for c in tmk)
cap_ok = cap_ok and M.KEY_KINDS_PER_VIDEO[0] <= len(fx.key_kinds) <= M.KEY_KINDS_PER_VIDEO[1] and set(M.CAP_ENTRANCES) == {'type', 'glow_rise', 'blur', 'flicker', 'font_flip', 'word'}
color_err = [n for n, ok in [('gold_soft', g_gold and g_gold['intensity'][0][1] <= 60), ('red_glow', g_red and g_red['intensity'][0][1] >= 150),
                             ('collage_glow', g_col), ('lime_forced_glow', g_lime),
                             ('rotation', not set(M.DEFAULT_ROTATION) & M.GLOW_REQUIRED), ('cap_script', cap_ok)] if not ok]
known = set(M.TRANS) | M.COMBO_KINDS | set(M.JOINS) | {'zoom + punch'}
opt_err = sorted({o for opts in OPTIONS.values() for o in opts} - known)
cat = json.load(open(CATALOG)); roots = cat.get('roots', {})
res = lambda f: roots[f.split(':', 1)[0]] + '/' + f.split(':', 1)[1] if f.split(':', 1)[0] in roots else f
files = [f for k in cat['kinds'].values() for f in k.get('files', [])] + [f for p in cat.get('opening', {}).get('pairs', []) for f in p]
missing = sorted(f for f in files if f.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac', '.aif', '.aiff')) and not os.path.exists(res(f)))
clicks = [f for k in ('grid_click', 'bar_click') for f in cat['kinds'][k]['files']]   # lần 10; word_click cố ý gom mọi file click (lần 15)
missing += ['click dùng chung: ' + f for f in sorted({f for f in clicks if clicks.count(f) > 1})]
missing += [f'{k} < 8 file' for k in ('grid_click', 'bar_click', 'word_click') if len(cat['kinds'][k]['files']) < 8]
missing += [f'font {r}' for r, (_, _, fp) in M.FONTS.items() if not os.path.exists(fp)]   # mọi font Motion FX đã cài
bad = [c.get('name') for _, c in fx.items if c['at'] < 0 or c['dur'] <= 0]
kinds = set(json.load(open(CATALOG))['kinds'])
unknown = sorted({q['kind'] for q in fx.cues if not q.get('src')} - kinds)   # cue có src = tiếng có sẵn của overlay
words = [('a', 0.0, 0.3)]
sfx = plan_sfx(fx.cues, words, 10.0, 'selfcheck')
print(len(fx.items), len(sfx), color_err, opt_err, missing[:3], bad, unknown)
"""
    code_rc, msg = run([str(VENV), "-c", code, str(ROOT), str(tmp / "mfx")])
    ok = code_rc == 0 and msg.strip().endswith("[] [] [] [] []")
    note("OK" if ok else "LỖI", "motion_fx + sfx_auto + cut_plan: clip, phát sáng, chuyển cảnh, file SFX hợp lệ", msg.strip()[-200:])


def check_silence_cut(tmp: Path) -> None:
    """Âm dựng sẵn: lời 1 s · lặng 1 s · tiếng thở 0,2 s (không có chữ) · lặng 1 s · lời 1,5 s · lặng 96 s · lời 1 s (sau giây 99)."""
    wav = tmp / "giong.wav"
    parts = [("sine=f=300:d=1", 1), ("anullsrc=r=48000:cl=mono", 1), ("sine=f=500:d=0.2", 0.2), ("anullsrc=r=48000:cl=mono", 1),
             ("sine=f=300:d=1.5", 1.5), ("anullsrc=r=48000:cl=mono", 96), ("sine=f=300:d=1", 1)]
    args = sum((["-f", "lavfi", "-t", str(d), "-i", src] for src, d in parts), [])
    graph = "".join(f"[{i}]aresample=48000,aformat=channel_layouts=mono[a{i}];" for i in range(len(parts)))
    graph += "".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]"
    run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", graph, "-map", "[o]", str(wav)], timeout=60)
    words = tmp / "loi.json"
    words.write_text(json.dumps([{"text": "một", "start": 0.1, "end": 0.9}, {"text": "hai", "start": 3.3, "end": 4.6},
                                 {"text": "ba", "start": 100.8, "end": 101.6}]))
    code, msg = run([str(VENV), str(ROOT / "scripts/silence_cut.py"), str(wav), "--words", str(words), "-o", str(tmp / "doan.json")])
    segs = json.loads((tmp / "doan.json").read_text())["segments"] if code == 0 else []
    ok = len(segs) == 3 and segs[0][0] == 0.0 and abs(segs[1][0] - 3.13) < 0.07 and 101.5 < segs[2][1] <= 101.71   # ≤ độ dài file
    note("OK" if ok else "LỖI", "silence_cut.py cắt khoảng lặng (bỏ tiếng thở, file > 99 s, đoạn cuối ≤ độ dài file)",
         str(segs) if not ok else f"{len(segs)} đoạn")


def check_silence_onset(tmp: Path) -> None:
    """Lặng đầu video (THCN 05): Whisper đặt chữ đầu sớm 0,45 s → đoạn đầu phải vào ở tiếng thật, không ở mốc Whisper;
    chữ đầu nói nhỏ (−40 dB, dưới ngưỡng −35) vẫn được giữ; fit_words dời chữ đầu về đầu đoạn."""
    def wav(name: str, parts: list[tuple[str, float]]) -> Path:
        out = tmp / name
        args = sum((["-f", "lavfi", "-t", str(d), "-i", src] for src, d in parts), [])
        graph = "".join(f"[{i}]aresample=48000,aformat=channel_layouts=mono[a{i}];" for i in range(len(parts)))
        graph += "".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]"
        run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", graph, "-map", "[o]", str(out)], timeout=60)
        return out
    som = wav("som.wav", [("anullsrc=r=48000:cl=mono", 1), ("sine=f=300:d=1", 1)])
    nho = wav("nho.wav", [("anullsrc=r=48000:cl=mono", 0.6), ("sine=f=300:d=0.4,volume=-22dB", 0.4), ("sine=f=300:d=1", 1)])
    dau = wav("dau.wav", [("anullsrc=r=48000:cl=mono", 0.28), ("sine=f=300:d=1.5", 1.5)])       # lặng đầu TTS / HeyGen 0,28 s < 0,3 s
    code = f"""import sys; sys.path.insert(0, {str(ROOT / 'scripts')!r})
from silence_cut import fit_words, speech_segments
w = [{{"text": "là", "start": 0.55, "end": 1.2}}]
a = speech_segments({str(som)!r}, w); b = speech_segments({str(nho)!r}, [{{"text": "nhỏ", "start": 0.6, "end": 1.3}}])
c = speech_segments({str(dau)!r}, [{{"text": "một", "start": 0.0, "end": 1.2}}])
print(a[0][0], b[0][0], fit_words(w, a)[0]["start"], c[0][0])"""
    rc, out = run([str(VENV), "-c", code])
    try:
        a0, b0, w0, c0 = map(float, out.split()[-4:])
        ok = rc == 0 and abs(a0 - 0.93) < 0.04 and abs(b0 - 0.53) < 0.04 and w0 == a0 and 0.15 <= c0 <= 0.25
    except ValueError:
        ok = False
    note("OK" if ok else "LỖI", "silence_cut.py không để lặng đầu video khi Whisper đặt chữ đầu sớm", out[-160:] if not ok else
         f"vào {a0:.2f} s (Whisper 0,55) · chữ nhỏ giữ từ {b0:.2f} s · lặng đầu 0,28 s → vào {c0:.2f} s")


def check_aroll_broll_scaffold(tmp: Path) -> None:
    """Kiểm analyze_and_scaffold.py: chuẩn hóa TTS, tạo Thư mục con đánh số và xuất Báo cáo 10 bước."""
    sample_json = tmp / "sample_kb.json"
    out_dir = tmp / "kb_out"
    sample_json.write_text(
        json.dumps(
            {
                "scripts": [
                    {
                        "script_id": "KB01",
                        "slug": "KB01_Mau_Test",
                        "title": "Test 4% Token & 15 triệu/tháng",
                        "segments": [
                            {
                                "type": "a-roll",
                                "time_range": "00s - 04s",
                                "duration_sec": 4.0,
                                "display_text": "Làm 1 video tốn 4% token!",
                                "visual_direction": "A-Roll tại bàn làm việc.",
                            },
                            {
                                "type": "b-roll",
                                "time_range": "04s - 09s",
                                "duration_sec": 5.0,
                                "display_text": "Tiết kiệm 15 triệu/tháng.",
                                "visual_direction": "Cảnh trám quay màn hình.",
                            },
                        ],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    code, msg = run([str(VENV), str(ROOT / "scripts/analyze_and_scaffold.py"), "from-json", str(sample_json), "--out-dir", str(out_dir)])
    report_ok = (out_dir / "00_BAO_CAO_PHAN_TICH_AROLL_BROLL.md").is_file() and (out_dir / "KB01_Mau_Test" / "00_storyboard_manifest.json").is_file()
    note("OK" if code == 0 and report_ok else "LỖI", "analyze_and_scaffold.py đóng gói Thư mục con & xuất Báo cáo 10 bước",
         "00_BAO_CAO_PHAN_TICH_AROLL_BROLL.md + KB01_Mau_Test" if (code == 0 and report_ok) else msg.strip()[-140:])


def check_edit_rules(tmp: Path) -> None:
    """Luật 2026-11-06 (edit_rules.py): từ điển nỗi đau, zoom keyframe, bộ kiểm chạy trên spec dựng sẵn có lỗi cố ý."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import edit_rules as E
    import importlib
    importlib.reload(E)
    pain = E.find_pain_in_text("Mình thất bại vì mất khách, không biết bắt đầu")
    k = E.zoom_keys(9.0, [2.4, 6.1])
    zoom_ok = all(100 <= v <= 118 for _, v, _ in k) and all(b[0] > a[0] for a, b in zip(k, k[1:])) and max(v for _, v, _ in k) == 118
    spec = {"fps": 30, "duration": 10, "tracks": [
        {"type": "video", "name": "V1 A-roll", "clips": [{"at": 0, "dur": 5, "name": "a"}, {"at": 5, "dur": 5, "name": "b"}]},
        {"type": "text", "name": "FX · text_low 1", "clips": [
            {"at": 0, "dur": 1, "text": "cam", "color": "#FF7A1A", "font": "A"},
            {"at": 1, "dur": 1, "text": "tim", "color": "#D6CCFF", "font": "B", "effects": [{"effect": "wonder_glow", "params": {}}]}]}]}
    r = {x["rule"]: x["status"] for x in E.audit_spec(spec, [("thất", 1.0), ("bại", 1.3)])}
    caught = (r.get("Font 4-6 mỗi video") == "LỖI" and r.get("Chữ phụ: không cam / hồng / tím / đỏ trừ khi phát sáng") == "LỖI"
              and r.get("Mọi điểm cắt có chuyển cảnh") == "LỖI" and r.get("Zoom in / out ở đoạn nói dài") == "CẢNH BÁO"
              and r.get("Nhiều B-roll / footage") == "CẢNH BÁO" and r.get("Từ khoá nỗi đau được nhấn") == "CẢNH BÁO")
    M = importlib.import_module("motion_fx")
    join_ok = {"flicker", "shutter"} <= set(M.JOINS) and "violet" not in M.CAPTION_ROTATION
    note("OK" if pain and zoom_ok and caught and join_ok else "LỖI", "edit_rules.py: nỗi đau · zoom · bộ kiểm 8 luật · flicker / shutter",
         f"pain={pain} zoom_ok={zoom_ok} caught={caught} join_ok={join_ok} {r}" if not (pain and zoom_ok and caught and join_ok) else f"{len(pain)} cụm nỗi đau · {len(k)} khoá zoom")


def check_scripts(quick: bool) -> None:
    scripts = ROOT / "scripts"
    pys = [*(scripts / n for n in ("analyze_and_scaffold.py", "env_status.py", "prep_video.py", "matte.py", "facecam.py",
                                   "audit_sfx.py", "limit_master.py", "master_audio.py", "normalize_tts.py",
                                   "dviet_text.py", "build_dviet_templates.py", "muse_gen.py", "text_fx.py", "fx_gfx.py",
                                   "text_fx_demo.py", "build_kit.py", "qa_frames.py", "qa_audio.py", "silence_cut.py",
                                   "edit_rules.py", "speed_media.py", "transcribe.py", "flow_3d_assets.py")),
           *(scripts / "style_analysis").glob("*.py"),
           *(APPS / r for r in ("craft-handoff/tools/fc_build.py", "craft-handoff/tools/craftctl.py",
                                "talking-head-premiere/scripts/audit_sfx.py",
                                "dviet-viral-text-audio-edit/scripts/clean_and_master_voice.py",
                                "motion-sfx-audio-mastering/scripts/master.py", "motion-sfx-audio-mastering/scripts/transcribe.py",
                                "facecammaxxing/scripts/fcm.py", "ae-script-builder/templates/du-an-ae/tools/ec.py"))]
    bad = []
    for p in pys:
        if not p.is_file():
            note("LỖI", f"script {p}", "không có")
            continue
        try:
            compile(p.read_text(encoding="utf-8"), str(p), "exec")      # chỉ kiểm cú pháp, không ghi .pyc
        except SyntaxError as e:
            bad.append(f"{p.name}: {str(e)[:120]}")
    note("LỖI" if bad else "OK", f"biên dịch {len(pys)} script Python", "; ".join(bad[:3]))
    shells = [f for f in ROOT.rglob("*.sh") if "node_modules" not in f.parts]
    bad_sh = [f.name for f in shells if subprocess.run(["bash", "-n", str(f)], capture_output=True).returncode]
    note("LỖI" if bad_sh else "OK", f"cú pháp {len(shells)} script shell", "; ".join(bad_sh[:3]))
    crlf = [str(f.relative_to(ROOT)) for f in ROOT.rglob("*") if f.is_file() and "node_modules" not in f.parts and "apps" not in f.parts      # apps/ là bản chép nguyên gốc, chỉ đọc
            and f.suffix in (".sh", ".py", ".mjs", ".js") and (lambda b: b"\r\n" in b and (f.suffix == ".sh" or b[:2] == b"#!"))(f.read_bytes())]
    note("LỖI" if crlf else "OK", "script chạy trực tiếp không dùng xuống dòng Windows (CRLF)", "; ".join(crlf[:3]))
    code, out = run([str(VENV), str(ROOT / "scripts/env_status.py")])
    note("OK" if code == 0 and "❌" not in out else "LỖI", "env_status.py", out.strip().splitlines()[-1] if out.strip() else "")
    with tempfile.TemporaryDirectory() as t:
        ev = Path(t, "ev.json")
        ev.write_text(json.dumps({"events": [{"role": "number", "num": "3", "noun": "Điều", "context": "nên biết", "at": 0, "dur": 2},
                                             {"role": "pair", "small": "Ví dụ", "big": "Kiểm tra", "at": 2, "dur": 1}]}, ensure_ascii=False))
        code, out = run([str(VENV), str(ROOT / "scripts/dviet_text.py"), str(ev), "-o", str(Path(t, "o.json"))])
        note("OK" if code == 0 else "LỖI", "dviet_text.py sinh chữ", out.strip()[-150:])
        check_text_fx(Path(t))
        check_aroll_broll_scaffold(Path(t))
        check_edit_rules(Path(t))
    fcm_py = APPS / "facecammaxxing/.venv/bin/python"
    for label, cmd in (("craft-handoff fc_build --help", ["python3", str(APPS / "craft-handoff/tools/fc_build.py"), "--help"]),
                       ("facecammaxxing fcm.py --help", [str(fcm_py if fcm_py.exists() else VENV), str(APPS / "facecammaxxing/scripts/fcm.py"), "--help"]),
                       ("motion-sfx master.py --help", [str(VENV), str(APPS / "motion-sfx-audio-mastering/scripts/master.py"), "--help"]),
                       ("video-understand --help", [str(VENV), str(APPS / "video-understand/scripts/understand_video.py"), "--help"]),
                       ("video-use transcribe --help", [str(VENV), str(APPS / "video-use/helpers/transcribe.py"), "--help"]),
                       ("yt-dlp (uvx)", ["uvx", "--from", "yt-dlp", "--with", "curl_cffi", "yt-dlp", "--version"])):
        code, out = run(cmd, timeout=120)
        note("OK" if code == 0 else "LỖI", label, out.strip().splitlines()[-1][:120] if out.strip() else "")
    code, out = run(["curl", "-sS", "-m", "5", "http://127.0.0.1:18610/readyz"])   # Muse (muse2api): dịch vụ có thể đang tắt
    note("OK" if code == 0 and '"ready":true' in out else "CẢNH BÁO", "Muse /readyz (ảnh/clip B-roll)", out.strip()[:120])
    if not quick:
        code, out = run(["npx", "--yes", "hyperframes", "--version"], timeout=180, cwd=tempfile.gettempdir())
        note("OK" if code == 0 else "CẢNH BÁO", "HyperFrames CLI (npx)", out.strip().splitlines()[-1][:80] if out.strip() else "")


def main() -> int:
    quick = "--quick" in sys.argv
    print(f"opa-video-studio selfcheck — skill tại {ROOT}, công cụ tại {APPS}\n")
    check_apps(); check_files(); check_tools(); check_scripts(quick)
    width = max(len(i) for _, i, _ in results)
    for lv in ("LỖI", "CẢNH BÁO", "OK"):
        for level, item, detail in results:
            if level == lv:
                print(f"[{level:8}] {item:<{width}}  {detail}")
    n = {lv: sum(1 for r in results if r[0] == lv) for lv in ("OK", "CẢNH BÁO", "LỖI")}
    print(f"\nTổng: {n['OK']} OK · {n['CẢNH BÁO']} cảnh báo · {n['LỖI']} lỗi")
    return 1 if n["LỖI"] else 0


if __name__ == "__main__":
    sys.exit(main())
