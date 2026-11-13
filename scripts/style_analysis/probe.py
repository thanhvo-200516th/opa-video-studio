"""Đo mỗi video: thông số, điểm cắt cảnh (scdet), loudness EBU R128. Ghi metrics/<id>.json"""
import json, os, re, subprocess, sys, statistics
vid_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
FF = "/home/vmiz/.local/bin/ffmpeg"
def run(args):
    return subprocess.run(args, capture_output=True, text=True).stderr
for f in sorted(os.listdir(vid_dir)):
    if not f.endswith(".mp4"): continue
    vid = f[:-4]; p = os.path.join(vid_dir, f)
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p], capture_output=True, text=True).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    dur = float(pr["format"]["duration"])
    err = run([FF, "-hide_banner", "-i", p, "-vf", "scale=270:480,scdet=threshold=10", "-an", "-f", "null", "-"])
    cuts = [float(t) for t in re.findall(r"lavfi\.scd\.time:\s*([\d.]+)", err)]
    scores = [float(s) for s in re.findall(r"lavfi\.scd\.score:\s*([\d.]+)", err)]
    bounds = [0.0] + cuts + [dur]
    shots = [round(b - a, 3) for a, b in zip(bounds, bounds[1:]) if b - a > 0.04]
    lo = run([FF, "-hide_banner", "-i", p, "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"])
    I = re.findall(r"I:\s*(-?[\d.]+) LUFS", lo); LRA = re.findall(r"LRA:\s*([\d.]+) LU", lo); TP = re.findall(r"Peak:\s*(-?[\d.]+) dBFS", lo)
    m = {"id": vid, "duration": round(dur, 2), "w": v["width"], "h": v["height"], "fps": v.get("avg_frame_rate"),
         "cuts": [round(c, 2) for c in cuts], "cut_scores": scores, "n_shots": len(shots),
         "shot_median": round(statistics.median(shots), 2) if shots else None, "shot_mean": round(statistics.mean(shots), 2) if shots else None,
         "shot_min": min(shots) if shots else None, "shot_max": max(shots) if shots else None,
         "cuts_per_10s": round(len(cuts) / dur * 10, 2),
         "lufs_I": float(I[-1]) if I else None, "LRA": float(LRA[-1]) if LRA else None, "true_peak": float(TP[-1]) if TP else None}
    json.dump(m, open(os.path.join(out_dir, vid + ".json"), "w"), ensure_ascii=False, indent=1)
    print(vid, m["duration"], "s", m["n_shots"], "shots, median", m["shot_median"], "s,", m["lufs_I"], "LUFS")
