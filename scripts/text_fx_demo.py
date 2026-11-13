"""Dựng một timeline FilmCraft chạy lần lượt 24 hiệu ứng (mỗi cái ~2,3 s) trên A-roll có sẵn để kiểm tra bằng mắt,
và/hoặc xuất đoạn spec của từng hiệu ứng (đặt ở giây 0) cho nút copy của trang xem trước.

    python text_fx_demo.py --aroll a.mp4:1.4:9.5 b.mp4:6.2:21.8 ... --out DIR [--matte] [--build]
    python text_fx_demo.py --snippets snippets.json

--aroll: danh sách file:in:out (giây) ghép nối thành V1. --matte: tạo lớp người tách nền cho B12 (rvm-matte, GPU).
--build: gọi scripts/apps/craft-handoff/tools/fc_build.py ra DIR/demo.fcproj. Chạy bằng ~/.venvs/video-skills/bin/python.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from text_fx import FX  # noqa: E402

FC_BUILD = Path(__file__).resolve().parents[1] / "scripts/apps/craft-handoff/tools/fc_build.py"
CARD_SRC = "/home/vmiz/Thanh/Media/TNEDIT/06_B-Roll/Stock_Theo_Chu_De_Mixkit/FTG_Video_Editing_editing_a_video_on_an_audiovisual_workstation_41276.mp4"
SLOT = 2.3


def effects(fx: FX, t0, matte: str | None) -> dict:
    """24 hiệu ứng; t0(i) = giây bắt đầu ô thứ i. Trả {mã: (tên, lời gọi)}."""
    calls = {}

    def reg(code, name, call):
        calls[code] = (name, call)

    t = t0(0); reg("B1", "Cặp lớn–nhỏ", f"fx.pair('có chủ đích', 'để dựng', at={t:.2f}, dur=2.1)"); fx.pair("có chủ đích", "để dựng", at=t, dur=2.1)
    t = t0(1); reg("B2", "Từ lớn thay trên chữ nhỏ", f"fx.swap_big('không cần', [('máy xịn', {t:.2f}), ('đèn đẹp', {t + .7:.2f}), ('kịch bản dài', {t + 1.4:.2f})], end={t + 2.1:.2f})")
    fx.swap_big("không cần", [("máy xịn", t), ("đèn đẹp", t + .7), ("kịch bản dài", t + 1.4)], end=t + 2.1)
    t = t0(2); reg("B3", "Chồng 3 tầng", f"fx.stack3('cách', 'dựng', 'có chủ đích', at={t:.2f}, dur=2.1)"); fx.stack3("cách", "dựng", "có chủ đích", at=t, dur=2.1)
    t = t0(3); reg("B4", "Chồng mà dễ đọc (crop feather)", f"fx.stack3('cách', 'dựng', 'có chủ đích', at={t:.2f}, dur=2.1, readable=True)")
    fx.stack3("cách", "dựng", "có chủ đích", at=t, dur=2.1, readable=True)
    t = t0(4); reg("B5", "Viết tay phát sáng chéo", f"k = fx.text('set up', {t:.2f}, 2.1, 'sans', 140); fx.blur_in(k); fx.script_accent('chuyên nghiệp', {t + .5:.2f}, 1.6, over=k)")
    k = fx.text("set up", t, 2.1, "sans", 140, case=False); fx.blur_in(k); fx.script_accent("chuyên nghiệp", t + .5, 1.6, over=k)
    t = t0(5); reg("B6", "Viết tay thay từ", f"fx.script_swap('hành trình', [('videographer', {t:.2f}), ('editor', {t + 1.1:.2f})], end={t + 2.1:.2f})")
    fx.script_swap("hành trình", [("videographer", t), ("editor", t + 1.1)], end=t + 2.1)
    t = t0(6); reg("B7", "Số khổng lồ + bookmark", f"fx.number_hook('3', 'hiệu ứng', at={t:.2f}, dur=2.1, small_words=[('nên', {t + .5:.2f}), ('lưu', {t + .7:.2f}), ('ngay', {t + .9:.2f})], bookmark_at={t + 1.3:.2f})")
    fx.number_hook("3", "hiệu ứng", at=t, dur=2.1, small_words=[("nên", t + .5), ("lưu", t + .7), ("ngay", t + .9)], bookmark_at=t + 1.3)
    t = t0(7); reg("B8", "Trượt lên mượt", f"fx.slide_up_text('dựng mượt', {t:.2f}, 2.1)"); fx.slide_up_text("dựng mượt", t, 2.1)
    t = t0(8); reg("B9", "Giả 3D xoay", f"fx.swing3d('giả 3D', {t:.2f}, 2.1)"); fx.swing3d("giả 3D", t, 2.1)
    t = t0(9); reg("B10", "Trượt xuống nhoè", f"fx.slide_down_text('kỹ năng', {t:.2f}, 2.1, y=330)"); fx.slide_down_text("kỹ năng", t, 2.1, y=330)
    t = t0(10)
    words = [("mỗi", t), ("vết", t + .3), ("cắt", t + .55), ("đều", t + .8), ("có", t + 1.1), ("lý", t + 1.3), ("do", t + 1.45)]
    reg("B11", "Phụ đề từng chữ", f"fx.word_captions({[(w, round(x, 2)) for w, x in words]}, end={t + 2.1:.2f}, mode='color')")
    fx.word_captions(words, end=t + 2.1, mode="color")
    t = t0(11)
    if matte:
        reg("B12", "Chữ sau đầu", f"fx.behind_head('EDIT', {t:.2f}, 2.1, matte_src='<người_alpha.mov>', head_top=900, halo='#B05FFD')")
        fx.behind_head("EDIT", t, 2.1, matte_src=matte, head_top=900, halo="#B05FFD")
    t = t0(12); reg("B13", "Chữ gắn tường", f"fx.wall_text('CLONE', 'effect', {t:.2f}, 2.1)"); fx.wall_text("CLONE", "effect", t, 2.1)
    t = t0(13); reg("B14", "Nghiêng theo vật + tràn khung", f"fx.tilt_text('người xem', {t:.2f}, 0.9, x=620, y=960); fx.punch_overflow('motion', {t + 1:.2f}, 1.1, punch_at={t + 1.6:.2f}, small='tạo ra')")
    fx.tilt_text("người xem", t, 0.9, x=620, y=960); fx.punch_overflow("motion", t + 1, 1.1, punch_at=t + 1.6, small="tạo ra")
    t = t0(14); reg("B15", "Phát sáng 2", f"fx.glow_text('glow text', {t:.2f}, 2.1)"); fx.glow_text("glow text", t, 2.1)
    t = t0(15); reg("B16", "Chữ mờ ảo", f"fx.dreamy_blur('mờ ảo', {t:.2f}, 2.1)"); fx.dreamy_blur("mờ ảo", t, 2.1)
    t = t0(16); reg("B17", "Blend Overlay", f"fx.overlay_text('blendmode', {t:.2f}, 2.1, y=1500)"); fx.overlay_text("blendmode", t, 2.1, y=1500)
    t = t0(17); reg("B18", "Chữ gradient", f"fx.gradient_word('tẻ nhạt', {t:.2f}, 2.1, ['#E83CC8', '#7A3CF0', '#E02828'])")
    fx.gradient_word("tẻ nhạt", t, 2.1, ["#E83CC8", "#7A3CF0", "#E02828"])
    t = t0(18); reg("B19", "Gõ chữ trong khung chọn", f"fx.typed_box('Cảm ơn', {t:.2f}, 2.1, under='hẹn gặp lại.')"); fx.typed_box("Cảm ơn", t, 2.1, under="hẹn gặp lại.")
    t = t0(19); reg("B20", "Pill kính lộ dần", f"fx.glass_pill('về cách dùng & ý nghĩa', {t:.2f}, 2.1)"); fx.glass_pill("về cách dùng & ý nghĩa", t, 2.1)
    t = t0(20); reg("B21", "Thẻ UI + nhãn", f"fx.ui_card('<clip.mp4>', {t:.2f}, 2.1, src_in=3, label='clip chủ thể')")
    fx.ui_card(CARD_SRC, t, 2.1, src_in=3, label="clip chủ thể")
    t = t0(21); reg("B22", "CTA Lưu lại", f"fx.cta_save({t:.2f}, 2.1, tail=[('để', {t + .6:.2f}), ('xem', {t + .75:.2f}), ('khi cần', {t + .9:.2f})], click_at={t + .7:.2f})")
    fx.cta_save(t, 2.1, tail=[("để", t + .6), ("xem", t + .75), ("khi cần", t + .9)], click_at=t + .7)
    t = t0(22); reg("B23", "Chữ diễn: gạch / đổi font / chớp / cong",
                    f"fx.strike_word('làm thủ công', {t:.2f}, 0.55, strike_at={t + .2:.2f}, small='không cần'); fx.font_flip('fonts', {t + .55:.2f}, step=0.12); fx.flicker_text('FLICKER', {t + 1.15:.2f}, 0.5); fx.curved_caption('cũng như truy cập kho tài nguyên', {t + 1.65:.2f}, 0.6)")
    fx.strike_word("làm thủ công", t, 0.55, strike_at=t + .2, small="không cần")
    fx.font_flip("fonts", t + .55, step=0.12)
    fx.flicker_text("FLICKER", t + 1.15, 0.5)
    fx.curved_caption("cũng như truy cập kho tài nguyên", t + 1.65, 0.6)
    t = t0(23); reg("B24", "Bố cục quay màn hình", f"fx.tutorial_layout('bước một', {t:.2f}, 2.1, captions=[('chọn layer dưới rồi bấm', {t + .3:.2f})], keywords=[('ALT+G', {t + .9:.2f})])")
    fx.tutorial_layout("bước một", t, 2.1, captions=[("chọn layer dưới rồi bấm", t + .3)], keywords=[("ALT+G", t + .9)])
    return calls


def snippets(path: Path, gfx: Path) -> None:
    """Mỗi hiệu ứng chạy riêng ở giây 0 → {mã: {name, call, tracks}} để dán vào spec."""
    out = {}
    probe = FX(gfx_dir=gfx)
    calls = effects(probe, lambda i: 0.0, matte="<người_alpha.mov>")
    for code, (name, call) in calls.items():
        fx = FX(gfx_dir=gfx)
        exec(call, {"fx": fx})
        out[code] = {"name": name, "python": call, "tracks": fx.tracks()}
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{len(out)} đoạn → {path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aroll", nargs="*", default=[])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--matte", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--snippets", type=Path)
    a = ap.parse_args()
    if a.snippets:
        snippets(a.snippets, a.snippets.parent / "gfx")
        return
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    segs = [(p, float(i), float(o)) for p, i, o in (s.rsplit(":", 2) for s in a.aroll)]
    v1, t = [], 0.0
    for p, i, o in segs:
        v1.append({"src": p, "at": t, "in": i, "dur": o - i, "audio": False, "name": Path(p).stem})
        t += o - i
    total = min(t, 24 * SLOT)
    t0 = lambda i: i * SLOT + 0.1  # noqa: E731
    matte = None
    if a.matte:                                   # lớp người cho đúng đoạn A-roll ở ô B12
        st = t0(11)
        for c in v1:
            if c["at"] <= st < c["at"] + c["dur"]:
                src_t = c["in"] + st - c["at"]
                clip = out / "b12_aroll.mp4"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{src_t:.3f}", "-t", "2.3", "-i", c["src"], "-an",
                                "-c:v", "libx264", "-crf", "14", str(clip)], check=True)
                matte = str(out / "b12_person_alpha.mov")
                subprocess.run([str(Path.home() / ".local/bin/rvm-matte"), str(clip), matte, "0.25"], check=True)
    fx = FX(gfx_dir=out / "gfx")
    calls = effects(fx, t0, matte)
    markers = [{"at": t0(i), "name": f"{code} · {calls[code][0]}", "comment": calls[code][1]}
               for i, code in enumerate([f"B{n}" for n in range(1, 25)]) if code in calls]
    spec = {"name": "text_fx demo 24 hiệu ứng (master-video-edit)", "width": 1080, "height": 1920, "fps": fx.fps, "duration": total,
            "tracks": [{"type": "video", "name": "V1 A-roll", "clips": v1}, *fx.tracks()], "markers": markers}
    (out / "demo.craft.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    print(f"spec: {out / 'demo.craft.json'} · {sum(len(t['clips']) for t in spec['tracks'])} clip · {len(spec['tracks'])} track")
    if a.build:
        subprocess.run([sys.executable, str(FC_BUILD), str(out / "demo.craft.json"), str(out / "demo.fcproj"),
                        "--report", str(out / "demo.report.json"), "--frames", "0"], check=True)


if __name__ == "__main__":
    main()
