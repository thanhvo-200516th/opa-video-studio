"""Soát chữ hiển thị từ build/_report.json (textDump do main.jsx xuất).

Luật (EDITORIAL_RULES.md + BRAND-SPEC):
1. Mọi dòng hiển thị bắt đầu bằng chữ hoa; dòng mở bằng số/dấu câu thì chữ cái đầu tiên sau đó viết hoa.
2. Cỡ chữ ≥ 28 px.
3. Font chỉ trong bộ đã duyệt; Fraunces chỉ ở comp cụm nhấn (TXT_*_NHAN); không có font thay thế.
4. Mục song song (cùng tiền tố comp, khác số thứ tự) dùng cùng font và cỡ.
Chạy: python -I tools/qa_chu.py  → in bảng và mã thoát 1 nếu có lỗi.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1] / "build" / "_report.json"
FONTS = {"BeVietnamPro-ExtraBold", "BeVietnamPro-SemiBold", "BeVietnamPro-Bold", "BeVietnamPro-Medium", "FrauncesOPA-ExtraBoldItalic"}
ACCENT = "FrauncesOPA-ExtraBoldItalic"
# URL / tên miền giữ chữ thường như tên file (luật Minh chốt 2026-10-08 cho tên file hiện trên hình).
URL = re.compile(r"^(https?://)?[a-z0-9-]+(\.[a-z0-9-]+)+(/\S*)?$")


def first_letter(line: str):
    m = re.search(r"[^\W\d_]", line)
    return m.group(0) if m else None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    rep = json.loads(REPORT.read_text(encoding="utf-8"))
    errs, rows = [], rep.get("textDump", [])
    groups = defaultdict(set)
    for t in rows:
        where = f"{t['comp']}/{t['layer']}"
        for line in re.split(r"[\r\n]+", t["text"]):
            ch = first_letter(line)
            if ch and not ch.isupper() and not URL.match(line.strip()):
                errs.append(f"viết hoa: {where}: '{line}'")
        if t["size"] < 28:
            errs.append(f"cỡ chữ {t['size']} < 28: {where}")
        if t["font"] not in FONTS:
            errs.append(f"font ngoài bộ: {t['font']} ở {where}")
        if t.get("substitute"):
            errs.append(f"font thay thế: {where}")
        if t["font"] == ACCENT and "_NHAN" not in t["comp"]:
            errs.append(f"Fraunces ngoài cụm nhấn: {where}")
        m = re.match(r"(TXT_S\d_(?:Y|TINH_NANG_))\d+$", t["comp"])
        if m:
            groups[m.group(1)].add((t["font"], round(t["size"], 1)))
    for g, styles in groups.items():
        if len(styles) > 1:
            errs.append(f"mục song song {g}* khác kiểu: {sorted(styles)}")
    print(f"{len(rows)} layer chữ · {sum(len(re.split(r'[\r\n]+', t['text'])) for t in rows)} dòng · nhóm song song: {dict((k, sorted(v)) for k, v in groups.items())}")
    for t in rows:
        print(f"  {t['comp']:28s} {t['font']:30s} {t['size']:6.1f}  {t['text'][:60]!r}")
    for e in errs:
        print("LỖI", e)
    print("KẾT QUẢ:", "đạt" if not errs else f"{len(errs)} lỗi")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
