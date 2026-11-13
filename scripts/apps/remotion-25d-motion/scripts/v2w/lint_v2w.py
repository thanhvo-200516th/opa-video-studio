#!/usr/bin/env python3
"""Lint luật code của bản 16:9 (NN §8.3, §8.6) cho src/v2w. Bỏ chú thích trước khi xét (dùng split_code của lint V2).

Chạy:  python tools/v2w/lint_v2w.py [đường dẫn…]   (mặc định src/v2w)
Luật:
  hieu-ung   gradient, shadow, backdrop, will-change, CSS 3D (perspective, translateZ, rotateX/Y, preserve-3d),
             interpolateColors, Math.random, Date, useRef, useState(, @remotion/motion-blur, CameraMotionBlur
  blur       filter / feGaussianBlur / blur( ngoài core/blur.tsx
  mau        mã màu hex, rgb(, rgba(, hsl( (màu chỉ lấy từ COLORS)
  chu-viet   chữ tiếng Việt có dấu trong mã (lời chỉ ở copy.ts/screenText.ts); dòng có `Error(` được bỏ qua
  sequence   <Sequence, <Series (bật tắt bằng điều kiện t)
  lam-tron   Math.floor / Math.round (thời gian không được làm tròn; framesOf dùng qa-allow)
  frame-tran from={số…}, durationInFrames={số…}
  ten-cam    Zalo, Messenger, Facebook, "bạn"
  dai        file ≥ 300 dòng
Dòng có `// qa-allow: <lý do>` được bỏ qua. Exit 1 khi có vi phạm, 2 khi đường dẫn không tồn tại.
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("lint_forbidden", ROOT / "tools/qa/lint_forbidden.py")
assert _spec and _spec.loader
_lf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lf)
split_code, VI_RE, ALLOW_RE = _lf.split_code, _lf.VI_RE, _lf.ALLOW_RE

DEFAULT = ROOT / "src/v2w"
BLUR_FILE = (ROOT / "src/v2w/core/blur.tsx").resolve()
MAX_LINES = 300
RULES: tuple[tuple[str, re.Pattern], ...] = (
    ("hieu-ung", re.compile(r"gradient|box-?[sS]hadow|drop-?[sS]hadow|text-?[sS]hadow|backdrop|will-?[cC]hange|perspective"
                            r"|translateZ|rotate[XY]\(|preserve-3d|interpolateColors|Math\.random|\bDate\b|useRef\b"
                            r"|useState\(|@remotion/motion-blur|CameraMotionBlur")),
    ("mau", re.compile(r"(?<![\w.&])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b|\brgba?\(|\bhsla?\(")),
    ("sequence", re.compile(r"<Sequence\b|<Series\b")),
    ("lam-tron", re.compile(r"Math\.(floor|round)\b")),
    ("frame-tran", re.compile(r"(?:\bfrom|durationInFrames)=\{\d")),
    ("ten-cam", re.compile(r"Zalo|Messenger|Facebook|\bbạn\b", re.IGNORECASE)),
)
BLUR_RE = re.compile(r"\bfilter\s*[:=]|feGaussianBlur|blur\(")


def lint_file(path: Path) -> list[tuple[int, str, str]]:
    text = path.read_text(encoding="utf-8")
    out: list[tuple[int, str, str]] = []
    lines = split_code(text)
    if len(text.splitlines()) >= MAX_LINES:
        out.append((len(lines), "dai", f"{len(text.splitlines())} dòng"))
    is_blur = path.resolve() == BLUR_FILE
    for no, (code, note) in enumerate(lines, start=1):
        if ALLOW_RE.search(note):
            continue
        for name, rx in RULES:
            m = rx.search(code)
            if m:
                out.append((no, name, m.group(0)))
        if not is_blur:
            m = BLUR_RE.search(code)
            if m:
                out.append((no, "blur", m.group(0)))
        if "Error(" not in code:
            m = VI_RE.search(code)
            if m:
                out.append((no, "chu-viet", m.group(0)))
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    paths = [Path(a) for a in sys.argv[1:]] or [DEFAULT]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print(f"Không có đường dẫn: {', '.join(missing)}", file=sys.stderr)
        return 2
    files = [f for p in paths for f in (sorted(p.rglob("*")) if p.is_dir() else [p]) if f.suffix in {".ts", ".tsx"}]
    total = 0
    for f in files:
        for no, rule, hit in lint_file(f):
            print(f"{f.resolve().relative_to(ROOT).as_posix()}:{no}: {rule} ({hit})")
            total += 1
    print(f"TỔNG: {len(files)} file, {total} vi phạm")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
