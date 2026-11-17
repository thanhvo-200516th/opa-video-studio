#!/usr/bin/env python3
"""env_status — kiểm tra các công cụ lõi trong scripts/apps/ và kho tài nguyên trên máy.

    python3 env_status.py
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SKILL_ROOT = Path(__file__).resolve().parents[1]
APPS = SKILL_ROOT / "scripts" / "apps"
VENV_PY = HOME / ".venvs" / "video-skills" / "bin" / "python"
FCM_PY = APPS / "facecammaxxing" / ".venv" / "bin" / "python"
FFMPEG = HOME / ".local" / "bin" / "ffmpeg"
TNEDIT = HOME / "Thanh" / "Media" / "TNEDIT"

USER_FONTS = HOME / ".local" / "share" / "fonts"        # nơi FilmCraft / text_fx tìm font (không cần sudo)
INTER_FONTS = ("Inter-ExtraBold.ttf", "Inter-Medium.ttf")   # hồ sơ minimal-edu (assets/fonts); FilmCraft không đọc thẳng từ thư mục skill


def missing_inter_fonts(dest: Path = USER_FONTS) -> list[str]:
    """Bản tĩnh Inter của hồ sơ minimal-edu chưa có trong thư mục font người dùng (bản biến thiên Inter-Variable.ttf không đủ ExtraBold)."""
    return [f for f in INTER_FONTS if not (dest / f).is_file()]


def install_inter_fonts(dest: Path = USER_FONTS, refresh: bool = True) -> list[str]:
    """Chép các file Inter còn thiếu từ assets/fonts vào thư mục font người dùng rồi fc-cache; trả danh sách đã chép. Không sudo."""
    todo = missing_inter_fonts(dest)
    if todo:
        dest.mkdir(parents=True, exist_ok=True)
        for f in todo:
            shutil.copy2(SKILL_ROOT / "assets" / "fonts" / f, dest / f)
        if refresh and shutil.which("fc-cache"):
            subprocess.run(["fc-cache", "-f", str(dest)], check=False, capture_output=True)
    return todo


MODULES = {
    "script-aroll-broll-analyzer": {
        "dir": SKILL_ROOT / "scripts",
        "key_script": SKILL_ROOT / "scripts" / "analyze_and_scaffold.py",
        "role": "Phân tích kịch bản A-Roll / B-Roll linh hoạt, chuẩn hóa TTS, khóa rule B-Roll (không voice, không text) & đóng gói Thư mục con đánh số + Báo cáo 10 bước",
    },
    "talking-head-premiere": {
        "dir": APPS / "talking-head-premiere",
        "key_script": APPS / "talking-head-premiere" / "scripts" / "audit_sfx.py",
        "role": "Dựng Talking Head trên FilmCraft (.fcproj) / Premiere (.prproj), icon bám lời, caption động, zoom nhấn ý",
    },
    "dviet-viral-text-audio-edit": {
        "dir": APPS / "dviet-viral-text-audio-edit",
        "key_script": APPS / "dviet-viral-text-audio-edit" / "scripts" / "clean_and_master_voice.py",
        "role": "Chữ nghệ thuật 2 tầng @__dviet (Calligraphy + Sans) & Lọc ồn giọng nói AI mã nguồn mở (-14 LUFS)",
    },
    "facecammaxxing": {
        "dir": APPS / "facecammaxxing",
        "key_script": APPS / "facecammaxxing" / "scripts" / "fcm.py",
        "role": "22 hiệu ứng 3D, biểu đồ & chữ sau đầu người nói (Remotion + GSAP + Three.js + Blender)",
    },
    "ae-script-builder": {
        "dir": APPS / "ae-script-builder",
        "key_script": APPS / "ae-script-builder" / "templates" / "du-an-ae" / "build" / "lib.jsx",
        "role": "Dựng mới dự án After Effects / EffectCraft bằng mã .jsx, 10 quy tắc chữ tiếng Việt (R1–R10) & QA khung chết",
    },
    "ae-template-customizer": {
        "dir": APPS / "ae-template-customizer",
        "key_script": APPS / "ae-template-customizer" / "scripts" / "parse_aep_timings.py",
        "role": "Phân tích & tùy biến sâu template .aep thương mại, thay nhân vật/UI/chữ tiếng Việt & gắn SFX theo keyframe",
    },
    "motion-sfx-audio-mastering": {
        "dir": APPS / "motion-sfx-audio-mastering",
        "key_script": APPS / "motion-sfx-audio-mastering" / "scripts" / "master.py",
        "role": "Thiết kế âm thanh từ kho 2.990+ SFX, đồng bộ cao độ La trưởng, QA âm thanh & Mastering EBU R128",
    },
}


def cmd_status(_args):
    print("=" * 78)
    print("🎬 OPA-VIDEO-STUDIO — KIỂM TRA HỆ SINH THÁI 7 MÔ-ĐUN & TÀI NGUYÊN")
    print("=" * 78)
    all_ok = True
    for idx, (name, info) in enumerate(MODULES.items(), 1):
        script_ok = info["key_script"].exists()
        dir_ok = info["dir"].exists()
        status = "✅ SẴN SÀNG" if (dir_ok and script_ok) else "❌ THIẾU FILE"
        if not (dir_ok and script_ok):
            all_ok = False
        print(f"  [{idx}] {name:<28} : {status}")
        print(f"      ├─ Vai trò : {info['role']}")
        print(f"      └─ Lõi     : {info['key_script']}")

    print("-" * 78)
    print("📦 KHO TÀI NGUYÊN & CÔNG CỤ TRÊN MÁY:")
    checks = [
        ("Python Video Venv", VENV_PY),
        ("Python Facecam Venv", FCM_PY),
        ("FFmpeg 8.1", FFMPEG),
        ("EffectCraft 0.17", HOME / ".local" / "bin" / "effectcraft"),
        ("DeepFilterNet3 CLI", HOME / ".local" / "bin" / "deep-filter"),
        ("ClearerVoice CLI", HOME / ".local" / "bin" / "clearvoice-enhance"),
        ("RobustVideoMatting CLI", HOME / ".local" / "bin" / "rvm-matte"),
        ("Kho SFX Talking Head (86 WAV)", TNEDIT / "02_SFX" / "Thu_Vien_SFX_PR"),
        ("Kho Assets Pro (Icons/Cards/Halos)", TNEDIT / "07_Assets"),
        ("Kho Font Tiếng Việt & Calligraphy", TNEDIT / "01_Font"),
        ("Kho Nhạc Nền (BGM)", TNEDIT / "08_Nhac_Nen" / "BGM_Thu_Vien_PR"),
    ]
    for label, path in checks:
        ok = path.exists()
        print(f"  • {label:<36}: {'✅ Có' if ok else '⚠️ Chưa thấy'} ({path})")
    miss = missing_inter_fonts()
    print(f"  • {'Font Inter (hồ sơ minimal-edu)':<36}: " + ("✅ Có" if not miss else f"⚠️ Thiếu {', '.join(miss)} — chạy: python3 env_status.py --install-fonts"))

    print("=" * 78)
    if all_ok:
        print("🚀 KẾT LUẬN: Toàn bộ 7 mô-đun trong 'opa-video-studio' đã kết nối và sẵn sàng!")
    return 0 if all_ok else 1


def main():
    parser = argparse.ArgumentParser(description="Kiểm tra trạng thái 7 mô-đun trong scripts/apps/ & kho tài nguyên")
    parser.add_argument("--install-fonts", action="store_true", help="chép Inter-ExtraBold / Inter-Medium (assets/fonts) vào ~/.local/share/fonts + fc-cache (hồ sơ minimal-edu)")
    args = parser.parse_args()
    if args.install_fonts:
        done = install_inter_fonts()
        print("Đã cài: " + ", ".join(done) if done else "Font Inter đã đủ, không cần cài.")
        return
    sys.exit(cmd_status(args))


if __name__ == "__main__":
    main()
