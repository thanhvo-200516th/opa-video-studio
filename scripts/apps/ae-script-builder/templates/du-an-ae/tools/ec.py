"""Gói build/ thành một file .jsx chạy được trong EffectCraft (Linux), thay cho tools/ae.py (After Effects, Windows).

EffectCraft chạy ExtendScript theo mô hình đối tượng của After Effects nhưng không mở được .aep: đoạn đầu bundle
cho app.open(.aep / file chưa có) tạo project mới và cho project.save() lưu ra .ecproj.

  python tools/ec.py [project/<tên>.ecproj]
Sau đó trong EffectCraft: File > Scripts > Run Script File… → build/_bundle_ec.jsx
(cần bật Settings > Scripting > Allow Scripts to Write Files để ghi .ecproj và build/_report.json).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
BUNDLE_ORDER = ["lib.jsx", "data/*.jsxinc", "scenes/*.jsx", "main.jsx"]

SHIM = """// ===== EffectCraft: .aep -> project mới, lưu .ecproj =====
(function () {
  var open0 = app.open, save0 = Project.prototype.save;
  app.open = function (f) {
    var s = String(f && f.fsName ? f.fsName : f);
    if (/\\.aep$/i.test(s) || !new File(s).exists) return app.newProject();
    return open0.call(app, f);
  };
  Project.prototype.save = function (file) {
    return save0.call(this, file || (this.file ? undefined : new File(OPA_ARGS.target)));
  };
})();
"""


def bundle(target: Path) -> Path:
    report = BUILD / "_report.json"
    args = f"var OPA_ARGS = {{target: '{target.as_posix()}', report: '{report.as_posix()}', sfx: '{(ROOT / 'assets' / 'sfx').as_posix()}'}};\n"
    parts = [args, SHIM]
    for pat in BUNDLE_ORDER:
        files = sorted(BUILD.glob(pat)) if "*" in pat else [BUILD / pat]
        for f in files:
            parts.append(f"// ===== {f.relative_to(BUILD).as_posix()} =====\n" + f.read_text(encoding="utf-8"))
    out = BUILD / "_bundle_ec.jsx"
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


if __name__ == "__main__":
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "project" / f"{ROOT.name}.ecproj"
    target.parent.mkdir(parents=True, exist_ok=True)
    (BUILD / "_report.json").unlink(missing_ok=True)
    print(bundle(target))
