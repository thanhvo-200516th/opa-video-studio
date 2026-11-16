"""Tự kiểm offline (không mạng, không CLIP): chọn clip, ngưỡng Muse, scenes.json, tên file, chọn bản tải, chuẩn hoá xoá metadata.

    ~/.venvs/footage/bin/python selftest.py      → in từng mục OK / LỖI, thoát 1 nếu có lỗi
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import footage  # noqa: E402
import media  # noqa: E402
import sources  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(f"[{'OK' if cond else 'LỖI':4}] {name}  {detail if not cond else ''}")
    if not cond:
        fails.append(name)


def c(src, i, score, w=1080, h=1920, dur=10.0):
    return {"source": src, "id": str(i), "title": f"t{i}", "w": w, "h": h, "duration": dur, "score": score, "files": []}


# chọn: cộng hướng khung + kho, hạ clip ngắn, bỏ trùng, lấy 3
picks = footage.select([c("pexels", 1, 0.30, 1920, 1080), c("pexels", 1, 0.30), c("local", "a", 0.295), c("pixabay", 2, 0.31, dur=2),
                        c("mixkit", 3, 0.20), c("pexels", 4, 0.29)], "portrait", 3)
check("chọn: thứ tự theo điểm đã cộng / trừ", [p["id"] for p in picks] == ["a", "1", "4"], [p["id"] for p in picks])
check("chọn: không trùng", len({(p["source"], p["id"]) for p in picks}) == len(picks))
again = footage.select([c("local", "a", 0.30), c("mixkit", 5, 0.29)], "portrait", 3, used={("local", "a")})
check("chọn: clip đã dùng cho cảnh trước bị hạ", again[0]["id"] == "5", [p["id"] for p in again])
check("Muse: điểm thấp → tạo", footage.need_muse([{"rank_score": 0.2}], "auto") and footage.need_muse([{"rank_score": 0.25}], "auto"))
check("Muse: điểm đủ → không tạo", not footage.need_muse([{"rank_score": 0.3}], "auto"))
check("Muse: never / always", not footage.need_muse([], "never") and footage.need_muse([{"rank_score": 0.9}], "always"))

# scenes.json
with tempfile.TemporaryDirectory() as td:
    p = Path(td, "s.json")
    p.write_text(json.dumps({"project": "X", "scenes": [{"id": 1, "query": "q"}, {"id": 2}]}))
    try:
        footage.load_scenes(p)
        check("scenes.json thiếu query → báo lỗi", False)
    except SystemExit as e:
        check("scenes.json thiếu query → báo lỗi", "cảnh 2" in str(e))
    p.write_text(json.dumps({"project": "X", "scenes": [{"query": "q"}]}))
    cfg = footage.load_scenes(p)
    check("scenes.json mặc định id + orientation", cfg["scenes"][0]["id"] == 1 and cfg["orientation"] == "portrait")

# tên file, chọn bản tải, tag Mixkit
check("slug tiếng Việt", media.slug("Người xem đang ở mức nào?") == "Nguoi_Xem_Dang_O_Muc_Nao", media.slug("Người xem đang ở mức nào?"))
urls = sources.best_file([(3840, 2160, "4k"), (1280, 720, "720"), (1920, 1080, "1080"), (640, 360, "360")])
check("bản tải: 1080 trước, 4K sau cùng", urls[0] == "1080" and urls[-1] == "4k", urls)
check("tag Mixkit bỏ từ chung", sources.mixkit_tags("a bored man in front of a laptop computer") == ["bored", "laptop"],
      sources.mixkit_tags("a bored man in front of a laptop computer"))
try:
    media.http_get("http://127.0.0.1:9/x?key=secret", timeout=1, tries=1)
except RuntimeError as e:
    check("URL có key không lộ trong lỗi", "secret" not in str(e), str(e))

# khung cảnh từ lời bóc / kịch bản
import draft  # noqa: E402
import review  # noqa: E402
segs = [{"start": 1.8, "end": 5.6, "text": "a"}, {"start": 5.6, "end": 8.0, "text": "b"}, {"start": 8.0, "end": 9.1, "text": "c"},
        {"start": 9.1, "end": 16.0, "text": "d"}, {"start": 16.0, "end": 17.0, "text": "e"}]
sc = draft.from_segments(segs)
check("draft lời bóc: gộp câu thành cảnh ≥ 4 s, ≤ 8,5 s", [x["t"] for x in sc] == [[1.8, 8.0], [8.0, 16.0], [16.0, 17.0]],
      [x["t"] for x in sc])
sc = draft.from_segments([{"start": 0, "end": 2, "text": "Thứ nhất, người xem"}, {"start": 2, "end": 4, "text": "Thứ hai, lỗi sai"},
                          {"start": 4, "end": 5, "text": "Bước 3 là quay"}])
check("draft: mỗi ý liệt kê một cảnh", len(sc) == 3, [x["text"] for x in sc])
tx = draft.from_text("# Tiêu đề\n" + " ".join(f"Câu số {i} có năm sáu bảy chữ." for i in range(8)))
check("draft kịch bản: bỏ tiêu đề, 15–35 chữ / cảnh", len(tx) == 4 and "Tiêu đề" not in tx[0]["text"] and all(15 <= len(x["text"].split()) <= 35 for x in tx[:-1]),
      [len(x["text"].split()) for x in tx])
with tempfile.TemporaryDirectory() as td:
    base = Path(td, "_Tim_Footage", "P")
    base.mkdir(parents=True)
    clip = Path(td, "Stock", "FTG_A_1.mp4")
    pk = {"project": "P<x>", "scenes": [{"id": 1, "t": [1, 2], "text": "Lời <b>", "query": "q", "status": "ok", "chosen": 0, "errors": [],
                                          "picks": [{"source": "mixkit", "path": str(clip), "rank_score": 0.3, "w": 1, "h": 2, "duration": 4}]}]}
    page = review._html(pk, base)
    check("trang duyệt: video đường dẫn tương đối + escape HTML",
          'src="../../Stock/FTG_A_1.mp4"' in page and "Lời &lt;b&gt;" in page and "P&lt;x&gt;" in page, page[-400:])

# cảnh "both" → cảnh video + cảnh ảnh dùng chung ảnh Muse; kiểm "seconds"
with tempfile.TemporaryDirectory() as td:
    p = Path(td, "s.json")
    p.write_text(json.dumps({"project": "X", "scenes": [{"id": 3, "query": "q", "kind": "both", "muse_prompt": "m"},
                                                         {"id": 4, "query": "q", "kind": "image"}]}))
    sc = footage.load_scenes(p)["scenes"]
    check("kind both → 2 cảnh (video + ảnh), cùng base_id",
          [(x["id"], x["kind"], x.get("base_id")) for x in sc] == [(3, "video", 3), ("3-anh", "image", 3), (4, "image", None)],
          [(x["id"], x["kind"], x.get("base_id")) for x in sc])
    import fetch  # noqa: E402
    check("Muse cảnh both dùng chung tên ảnh", fetch.muse_base("P", sc[0]) == fetch.muse_base("P", sc[1]))
    p.write_text(json.dumps({"project": "X", "scenes": [{"query": "q", "kind": "gif", "seconds": 700}]}))
    try:
        footage.load_scenes(p)
        check("kind / seconds sai → báo lỗi", False)
    except SystemExit as e:
        check("kind / seconds sai → báo lỗi", "kind" in str(e) and "seconds" in str(e), str(e))

# ảnh Pexels / Pixabay (dữ liệu mẫu theo tài liệu API — chưa chạy thật vì máy chưa có key)
_orig = media.http_json
media.http_json = lambda url, headers=None: ({"photos": [{"id": 7, "width": 3000, "height": 4500, "url": "https://pexels/p/7",
                                                          "alt": "man with paper", "photographer": "A",
                                                          "src": {"original": "https://img/7.jpeg", "medium": "https://img/7m"}}]}
                                             if "pexels" in url else
                                             {"hits": [{"id": 9, "pageURL": "https://pixabay/9", "tags": "desk, laptop",
                                                        "webformatURL": "https://pb/9w", "largeImageURL": "https://pb/9L",
                                                        "imageWidth": 1280, "imageHeight": 1920, "user": "B"}]})
px, pb = sources.pexels_photos("man", "portrait", "k"), sources.pixabay_photos("desk", "portrait", "k")
media.http_json = _orig
check("ảnh Pexels: ứng viên ảnh, bản tải giới hạn cạnh 2560",
      px[0]["type"] == "image" and px[0]["files"][0][2].endswith("h=2560") and px[0]["thumb"] == "https://img/7m", px)
check("ảnh Pixabay: ứng viên ảnh, largeImageURL", pb[0]["type"] == "image" and pb[0]["files"][0][2] == "https://pb/9L", pb)

# kho: lọc theo loại (không cần CLIP)
import numpy as np  # noqa: E402
from library import Library  # noqa: E402
with tempfile.TemporaryDirectory() as td:
    lib = Library(Path(td))
    lib.files = [{"path": "/a/v_1.mp4", "type": "video", "w": 1, "h": 2, "duration": 5}, {"path": "/a/i_2.jpg", "type": "image", "w": 1, "h": 2,
                 "duration": 0}, {"path": "/a/old_3.mp4", "w": 2, "h": 1, "duration": 5}]
    lib.emb = np.eye(3, 512, dtype=np.float32)
    lib.owner = np.array([0, 1, 2])
    q = np.eye(1, 512, dtype=np.float32)
    check("kho: tìm ảnh chỉ ra ảnh", [x["id"] for x in lib.search(q, 5, "image")] == ["i_2"])
    check("kho: tìm video ra video (kể cả mục cũ chưa có type)", sorted(x["id"] for x in lib.search(q, 5, "video")) == ["old_3", "v_1"])
    for rel in ("A/clip_1.mp4", "A/x_doan/doan01_8s.mp4", "A/x_doan/doan01_cuoi.png", "_Tim_Footage/P/sheet.jpg", "A/b.mp4.part"):
        (Path(td) / rel).parent.mkdir(parents=True, exist_ok=True)
        (Path(td) / rel).write_bytes(b"x")
    check("kho: bỏ đoạn trung gian _doan/, kết quả dự án, file đang tải", [x.name for x in lib.scan()] == ["clip_1.mp4"],
          [x.name for x in lib.scan()])

# ảnh: xoá EXIF + giới hạn cạnh; ảnh động zoom chậm
from PIL import Image  # noqa: E402
with tempfile.TemporaryDirectory() as td:
    src, out, mp4 = Path(td, "in.jpg"), Path(td, "out.jpg"), Path(td, "dong.mp4")
    ex = Image.Exif()
    ex[0x0131] = "Muse prompt bi_mat"                  # Software
    Image.new("RGB", (4000, 6000), (200, 100, 50)).save(src, exif=ex)
    media.normalize_image(src, out)
    with Image.open(out) as im:
        check("ảnh: cạnh dài ≤ 2560, không EXIF", max(im.size) == 2560 and not im.getexif() and b"bi_mat" not in out.read_bytes(),
              (im.size, dict(im.getexif())))
    media.ken_burns(out, mp4, seconds=2)
    d = json.loads(subprocess.run([media.FFPROBE, "-v", "error", "-count_frames", "-show_entries",
                                   "stream=codec_type,width,height,nb_read_frames,r_frame_rate", "-of", "json", str(mp4)],
                                  capture_output=True, text=True).stdout)["streams"]
    check("ảnh động: 1080×1920, 30fps, 60 khung / 2 s, không tiếng",
          len(d) == 1 and (d[0]["width"], d[0]["height"], d[0]["r_frame_rate"], d[0]["nb_read_frames"]) == (1080, 1920, "30/1", "60"), d)

# clip dài: chia đoạn, khung cuối, nối chuyển mờ
import chain  # noqa: E402
check("chia đoạn: 30 s → 4×8 s, 60 s → 8×8 s, 12 s → 2×7 s, seg ngoài 5–10 bị kẹp",
      chain.plan_segments(30) == [8] * 4 and chain.plan_segments(60) == [8] * 8 and chain.plan_segments(12) == [7, 7]
      and chain.plan_segments(20, seg=15) == [7, 7, 7] and chain.plan_segments(11, seg=5) == [5, 5, 5],
      [chain.plan_segments(30), chain.plan_segments(60), chain.plan_segments(12), chain.plan_segments(20, seg=15), chain.plan_segments(11, seg=5)])
check("chia đoạn đủ dài sau khi trừ phần chuyển mờ", all(sum(chain.plan_segments(t)) - 0.2 * (len(chain.plan_segments(t)) - 1) >= t
                                                         for t in (11, 13, 17, 25, 31, 45, 59, 90)))
with tempfile.TemporaryDirectory() as td:
    parts = []
    for i, col in enumerate(("red", "green", "blue")):
        f = Path(td, f"p{i}.mp4")
        subprocess.run([media.FFMPEG, "-v", "error", "-f", "lavfi", "-i", f"color={col}:s=704x1248:d=2:r=30", "-f", "lavfi", "-i",
                        "sine=d=2", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(f)], check=True)
        parts.append(f)
    png = media.last_frame(parts[2], Path(td, "cuoi.png"))
    with Image.open(png) as im:
        r, g, b = im.convert("RGB").getpixel((10, 10))
    check("khung cuối: đúng khung của đoạn (xanh dương)", b > 200 and r < 40 and g < 40, (r, g, b))
    check("lệch mối nối: hai khung giống nhau ≈ 0", chain.seam_diff(png, parts[2]) < 2, chain.seam_diff(png, parts[2]))
    out = media.concat_xfade(parts, Path(td, "noi.mp4"), 0.2, 5.0)
    d = json.loads(subprocess.run([media.FFPROBE, "-v", "error", "-count_frames", "-show_entries",
                                   "stream=codec_type,width,height,nb_read_frames:format=duration", "-of", "json", str(out)],
                                  capture_output=True, text=True).stdout)
    st = d["streams"]
    check("nối chuyển mờ: 5,0 s · 150 khung · không tiếng · giữ cỡ đoạn đầu",
          len(st) == 1 and st[0]["nb_read_frames"] == "150" and (st[0]["width"], st[0]["height"]) == (704, 1248), d)
    mid = media.frame(out, 2.0 - 0.1, 64).getpixel((5, 5))
    check("nối chuyển mờ: giữa mối nối là pha trộn (không cắt cứng)", mid[0] > 20 and mid[1] > 20, mid)

# đoạn nối: trùng đoạn trước / không bám khung đầu → tạo lại, giữ bản khớp nhất (Muse giả lập)
import shutil  # noqa: E402
import muse  # noqa: E402
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    clips = {}
    for col in ("blue", "red"):
        clips[col] = td / f"{col}.mp4"
        subprocess.run([media.FFMPEG, "-v", "error", "-f", "lavfi", "-i", f"color={col}:s=160x284:d=1:r=30", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", str(clips[col])], check=True)
    blue_png = media.last_frame(clips["blue"], td / "blue.png")
    seq = [clips["blue"], clips["red"], clips["blue"]]          # lần 1 trùng đoạn trước, lần 2 lệch khung, lần 3 đạt
    calls = []
    _real = muse.generate_video
    def fake(text, frame_in, out, seconds=5, attempt=0, **k):
        calls.append(attempt)
        shutil.copy(seq[attempt], out)
        if attempt == 2:                                       # bản đạt: cùng màu nhưng khác byte với đoạn trước
            subprocess.run([media.FFMPEG, "-v", "error", "-y", "-i", str(seq[attempt]), "-c:v", "libx264", "-crf", "30", str(out)], check=True)
        return out
    muse.generate_video = fake
    try:
        diff, n = chain._segment("t", blue_png, td / "doan02_8s.mp4", 8, {chain._md5(clips["blue"])}, lambda *a: None)
    finally:
        muse.generate_video = _real
    check("đoạn nối: trùng → tạo lại, lệch → tạo lại, giữ bản đạt", calls == [0, 1, 2] and n == 3 and diff < 5
          and (td / "doan02_8s.mp4").exists() and not list(td.glob("doan02_8s_thu*.mp4")), (calls, n, diff))

# chuẩn hoá: bỏ tiếng, xoá metadata, H.264
with tempfile.TemporaryDirectory() as td:
    src, out = Path(td, "in.mov"), Path(td, "out.mp4")
    subprocess.run([media.FFMPEG, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=3840x2160:d=1:r=25", "-f", "lavfi", "-i",
                    "sine=d=1", "-shortest", "-metadata", "title=bi_mat", "-metadata", "comment=prompt AI", "-c:v", "libx264",
                    "-c:a", "aac", str(src)], check=True)
    media.normalize(src, out)
    tags = subprocess.run([media.FFPROBE, "-v", "error", "-show_entries", "format_tags:stream_tags:stream=codec_name,height,r_frame_rate",
                           "-of", "json", str(out)], capture_output=True, text=True).stdout
    d = json.loads(tags)
    st = d["streams"]
    check("chuẩn hoá: chỉ còn hình H.264, 1080p, 30fps",
          len(st) == 1 and st[0]["codec_name"] == "h264" and st[0]["height"] == 1080 and st[0]["r_frame_rate"] == "30/1", st)
    raw = out.read_bytes()
    check("chuẩn hoá: xoá metadata + dấu phần mềm", "bi_mat" not in tags and "prompt" not in tags and "encoder" not in tags.lower()
          and b"x264" not in raw and b"Lav" not in raw, tags[:300])

print(f"\n{'ĐẠT' if not fails else 'LỖI: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
