"""Render mot kich ban TikTok thanh video talking head tren HeyGen.

Preset da chot: ban B — photo avatar "AHuy - Golf Cart CEO" + voice clone AHuy.

Cach dung:
    set HEYGEN_KEY=<api key>          (PowerShell: $env:HEYGEN_KEY="<api key>")
    python render.py 5                 -> chi in loi thoai da lam sach, KHONG ton credit
    python render.py 5 --yes           -> render that su va tai video ve folder nay

Luon chay lan 1 khong co --yes de doc lai loi thoai truoc. Bo lam sach ben duoi
chi xu ly markdown; so lieu, ky tu % va tu khoa viet lien van phai tu sua tay.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request

# Console Windows mac dinh la cp1252, khong in duoc tieng Viet co dau.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "kich-ban-30-bai.json")
BASE = "https://api.heygen.com"

# --- Preset ban B (da chot 26/10/2026) ---------------------------------------
AVATAR_ID = "761364fad106369de1c3ada3994aee9c"   # look "AHuy - Golf Cart CEO"
VOICE_ID = "09bed03ed2984542836268ac73ffc18c"    # voice clone AHuy (Vietnamese, nam)
ASPECT_RATIO = "9:16"
RESOLUTION = "1080p"
FIT = "cover"
EXPRESSIVENESS = "medium"
MOTION_PROMPT = (
    "A composed business executive speaking directly to camera: natural head turns, "
    "steady eye contact, calm confident posture, subtle shoulder and torso movement "
    "in time with speech."
)


def call(method, path, payload=None):
    key = os.environ.get("HEYGEN_KEY")
    if not key:
        sys.exit("Thieu bien moi truong HEYGEN_KEY.")
    headers = {"X-Api-Key": key}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")


def clean(text):
    """Bo markdown khoi loi thoai de TTS khong doc ra ky tu thua."""
    text = text.replace("$\\rightarrow$", ",").replace("\\n", "\n")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)      # **dam**
    text = re.sub(r"\*(.+?)\*", r"\1", text)          # *nghieng*
    text = re.sub(r"`(.+?)`", r"\1", text)            # `code`
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.M)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def warnings(text, keyword):
    out = []
    if "%" in text:
        out.append("Co ky tu '%' — nen viet thanh chu (vd '90%' -> 'chin muoi phan tram').")
    if keyword and keyword in text:
        out.append(f"Tu khoa '{keyword}' viet lien se bi danh van — tach thanh tung tu.")
    if re.search(r"\d", text):
        out.append("Co chu so — nghe lai xem giong doc co doc dung khong.")
    return out


def build_vo(entry):
    parts = [clean(scene["vo"]) for scene in entry["scenes"]]
    return "\n\n".join(p for p in parts if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("num", type=int, help="So thu tu kich ban, 1-30")
    ap.add_argument("--yes", action="store_true", help="Render that su (ton credit)")
    ap.add_argument("--text", help="Duong dan file .txt loi thoai da sua tay")
    args = ap.parse_args()

    data = json.load(open(SCRIPTS, encoding="utf-8"))
    entry = next((x for x in data if x["order"] == args.num), None)
    if entry is None:
        sys.exit(f"Khong tim thay kich ban so {args.num}.")

    if args.text:
        vo = open(args.text, encoding="utf-8").read().strip()
    else:
        vo = build_vo(entry)

    slug = (entry.get("keyword") or f"bai{args.num:02d}").lower()
    stem = f"bai{args.num:02d}-{slug}"

    print(f"=== Bai #{args.num:02d} | {entry['funnel']} | {entry['day']} ===")
    print(entry["title"])
    print(f"Tu khoa comment: {entry.get('keyword')}")
    print(f"Do dai loi thoai: {len(vo)} ky tu\n")
    print(vo)
    print()
    for w in warnings(vo, entry.get("keyword")):
        print("  [!] " + w)

    if not args.yes:
        print(f"\nChua render. Sua loi thoai thi luu ra {stem}-loi-thoai.txt roi chay:")
        print(f"    python render.py {args.num} --text {stem}-loi-thoai.txt --yes")
        return

    res = call("POST", "/v3/videos", {
        "type": "avatar",
        "title": f"Bai{args.num:02d} {entry['title'][:60]}",
        "avatar_id": AVATAR_ID,
        "voice_id": VOICE_ID,
        "script": vo,
        "aspect_ratio": ASPECT_RATIO,
        "resolution": RESOLUTION,
        "fit": FIT,
        "expressiveness": EXPRESSIVENESS,
        "motion_prompt": MOTION_PROMPT,
    })
    vid = res["data"]["video_id"]
    print(f"\nDa gui render: {vid}")

    for i in range(120):
        d = call("GET", "/v3/videos/" + vid).get("data", {})
        st = d.get("status")
        print(f"  [{i * 20}s] {st}", flush=True)
        if st == "completed":
            dest = os.path.join(HERE, stem + ".mp4")
            urllib.request.urlretrieve(d["video_url"], dest)
            size = os.path.getsize(dest) / 1024 / 1024
            print(f"\nXONG: {dest} ({size:.1f} MB, {d.get('duration')}s)")
            open(os.path.join(HERE, stem + "-loi-thoai.txt"), "w", encoding="utf-8").write(vo)
            return
        if st == "failed":
            sys.exit("Render that bai: " + json.dumps(d, ensure_ascii=False))
        time.sleep(20)
    sys.exit("Qua lau, van dang render. Kiem tra tren heygen.com.")


if __name__ == "__main__":
    main()
