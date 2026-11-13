#!/usr/bin/env python3
"""Lint cấm cho mã hình V2 (KH §3.10, TK §6, NC §4.4).

Chạy:  python tools/qa/lint_forbidden.py [đường dẫn…]   (mặc định src/videos/V2 src/fx src/ui)
Luật (chỉ xét phần mã, đã bỏ chú thích // và /* */; chú thích không vẽ ra hình):
  hieu-ung   gradient, shadow, backdrop, blur(, filter:/=, Math.random, interpolateColors, CameraMotionBlur, useState(
  hex        mã màu hex ngoài src/brand/tokens.ts
  frame-tran from={số…}, durationInFrames={số…}
  ten-cam    Zalo, Messenger, Facebook, "bạn"
  chu-viet   chữ tiếng Việt có dấu trong .tsx dưới src/videos/V2 và src/ui (lời phải ở copy.ts/screenText.ts)
Dòng có `// qa-allow: <lý do>` được bỏ qua.
In `file:dòng: luật`; exit 1 khi có vi phạm, 2 khi đường dẫn không tồn tại.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATHS = ("src/videos/V2", "src/fx", "src/ui")
EXTS = {".ts", ".tsx"}
TOKENS_FILE = (ROOT / "src/brand/tokens.ts").resolve()
VI_SCOPES = ("/src/videos/V2/", "/src/ui/")
_VI_LOWER = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VI_RE = re.compile(f"[{_VI_LOWER}{_VI_LOWER.upper()}]")
ALLOW_RE = re.compile(r"qa-allow:\s*\S")
RULES: tuple[tuple[str, re.Pattern], ...] = (
    ("hieu-ung", re.compile(r"gradient|box-?[sS]hadow|drop-?[sS]hadow|backdrop|blur\(|\bfilter\s*[:=]"
                            r"|Math\.random|interpolateColors|CameraMotionBlur|useState\(")),
    ("hex", re.compile(r"(?<![\w.&])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")),
    ("frame-tran", re.compile(r"(?:\bfrom|durationInFrames)=\{\d")),
    ("ten-cam", re.compile(r"Zalo|Messenger|Facebook|\bbạn\b", re.IGNORECASE)),
)


def split_code(text: str) -> list[tuple[str, str]]:
    """Tách từng dòng thành (mã, chú thích). Chuỗi giữ trong phần mã."""
    lines: list[tuple[str, str]] = []
    code: list[str] = []
    note: list[str] = []
    state = "code"  # code | line | block | ' | " | `
    i = 0
    while i < len(text):
        ch, nxt = text[i], text[i + 1 : i + 2]
        if ch == "\n":
            lines.append(("".join(code), "".join(note)))
            code, note = [], []
            if state in ("line", "'", '"'):
                state = "code"
            i += 1
            continue
        if state == "code":
            if ch == "/" and nxt == "/":
                state, i = "line", i + 2
                continue
            if ch == "/" and nxt == "*":
                state, i = "block", i + 2
                continue
            if ch in "'\"`":
                state = ch
            code.append(ch)
        elif state in ("line", "block"):
            if state == "block" and ch == "*" and nxt == "/":
                state, i = "code", i + 2
                continue
            note.append(ch)
        else:  # trong chuỗi
            code.append(ch)
            if ch == "\\" and nxt and nxt != "\n":
                code.append(nxt)
                i += 2
                continue
            if ch == state:
                state = "code"
        i += 1
    lines.append(("".join(code), "".join(note)))
    return lines


def lint_file(path: Path) -> list[tuple[int, str, str]]:
    """Trả về [(dòng, luật, đoạn khớp)]."""
    resolved = path.resolve()
    posix = "/" + resolved.as_posix().lstrip("/")
    vi_scope = path.suffix == ".tsx" and any(s in posix for s in VI_SCOPES)
    is_tokens = resolved == TOKENS_FILE
    out = []
    text = path.read_text(encoding="utf-8")
    for no, (code, note) in enumerate(split_code(text), start=1):
        if ALLOW_RE.search(note):
            continue
        for name, rx in RULES:
            if name == "hex" and is_tokens:
                continue
            m = rx.search(code)
            if m:
                out.append((no, name, m.group(0)))
        if vi_scope:
            m = VI_RE.search(code)
            if m:
                out.append((no, "chu-viet", m.group(0)))
    return out


def collect(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix in EXTS and f.is_file())
        elif p.suffix in EXTS:
            files.append(p)
    return files


def show(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    paths = [Path(a) for a in sys.argv[1:]] or [ROOT / p for p in DEFAULT_PATHS]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print(f"Không có đường dẫn: {', '.join(missing)}", file=sys.stderr)
        return 2
    files = collect(paths)
    total = 0
    for f in files:
        for no, rule, hit in lint_file(f):
            print(f"{show(f)}:{no}: {rule} ({hit})")
            total += 1
    print(f"TỔNG: {len(files)} file, {total} vi phạm")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
