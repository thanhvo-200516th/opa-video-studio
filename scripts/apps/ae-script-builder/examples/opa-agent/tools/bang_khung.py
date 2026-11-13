"""Sinh bảng thời gian chữ (khung master) từ báo cáo dựng build/_report.json và chèn vào KHUNG-DUNG.md.

Khung trong Text comp là khung cục bộ; cộng offset của TITLE trong Scene và của Scene trong Master
(đúng quy tắc của mẫu: "Keyframe local của pre-comp phải đổi về timeline Scene/Master").
Chạy: python -I tools/bang_khung.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "build" / "_report.json"
DOC = ROOT / "KHUNG-DUNG.md"
MASTER = "OPA_AGENT_MASTER_16x9"
RECIPE = {"R1": "R1 theo từ", "R2": "R2 theo dòng", "R3": "R3 theo ký tự", "R4": "R4 hai pha", "R5": "R5 dòng từ phải"}


def fmt(f):
    return "—" if f is None else f"f{f} ({f / 30:.2f} s)".replace(".", ",")


def offset(comp: str, placements: list) -> int:
    total, cur, guard = 0, comp, 0
    while cur != MASTER and guard < 10:
        hit = next((p for p in placements if p["child"] == cur), None)
        if hit is None:
            return total
        total += hit["start"]
        cur = hit["parent"]
        guard += 1
    return total


def main() -> None:
    rep = json.loads(REPORT.read_text(encoding="utf-8"))
    pl = rep.get("placements", [])
    rows = ["| Text comp | Công thức | Cỡ chữ | Bắt đầu vào | Hiện đủ | Bắt đầu ra | Hết |", "|---|---|---:|---|---|---|---|"]
    for t in rep["texts"]:
        comp = t["layer"].split("/")[0]
        off = offset(comp, pl)
        sh = lambda v: None if v is None else int(round(v + off))
        rows.append(f"| {comp} | {RECIPE.get(t['recipe'], t['recipe'])} | {t['em']:g} px | {fmt(sh(t['inAt']))} | {fmt(sh(t['full']))} | "
                    f"{fmt(sh(t['outAt'])) if t['outAt'] is not None else 'theo chuyển cảnh'} | {fmt(sh(t['outEnd']))} |")
    sfx = ["| Âm | Đỉnh (khung master) | Mức |", "|---|---|---:|"]
    for name, frame, db in rep.get("sfx", []):
        sfx.append(f"| {name} | {fmt(frame)} | {db:g} dB |")
    block = ("<!-- BANG-TU-DONG:BAT-DAU (sinh bởi tools/bang_khung.py từ build/_report.json, không sửa tay) -->\n"
             "### Bảng thời gian chữ theo khung master\n\n" + "\n".join(rows) +
             f"\n\nBản dựng: {len(rep.get('comps', []))} comp, {rep.get('expressionCount')} expression, "
             f"lỗi expression: {len(rep.get('expressionErrors') or [])}, lỗi dựng: {len(rep.get('errors') or [])}.\n\n"
             "### SFX theo chuyển động (chưa có giọng đọc; bảng đầy đủ kèm lý do: `audio/BANG-CUE-AM-THANH.md`)\n\n" + "\n".join(sfx) + "\n<!-- BANG-TU-DONG:KET-THUC -->")
    doc = DOC.read_text(encoding="utf-8")
    doc = re.sub(r"<!-- BANG-TU-DONG:BAT-DAU.*?BANG-TU-DONG:KET-THUC -->", lambda m: block, doc, flags=re.S)
    DOC.write_text(doc, encoding="utf-8")
    print(f"OK: {len(rows) - 2} dòng chữ, {len(sfx) - 2} SFX")


if __name__ == "__main__":
    main()
