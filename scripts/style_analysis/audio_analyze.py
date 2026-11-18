"""Đo âm thanh từ stem đã tách: mức nhạc/SFX so với giọng, nhạc có chạy suốt không, duck khi nói,
mật độ tiếng nhấn (transient) và tỷ lệ điểm cắt cảnh có tiếng nhấn. Ghi audio_metrics/<id>.json"""
import json, os, re, shutil, subprocess, sys, glob, random
import numpy as np
S = sys.argv[1]; out = os.path.join(S, "audio_metrics"); os.makedirs(out, exist_ok=True)
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
def load(p, sr=16000):
    pcm = subprocess.run([FF, "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
def lufs(p):
    e = subprocess.run([FF, "-hide_banner", "-i", p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s*(-?[\d.]+) LUFS", e); return float(m[-1]) if m else None
def env_db(x, sr, win=0.02, hop=0.01):
    w, h = int(sr * win), int(sr * hop); n = max(1, (len(x) - w) // h)
    fr = np.lib.stride_tricks.sliding_window_view(x, w)[::h][:n]
    return 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-9)
def onsets(db, hop=0.01, rise=8.0, floor=-38.0, look=30, gap=0.12):
    t = []; last = -1
    for i in range(look, len(db)):
        base = np.median(db[i - look:i])
        if db[i] > floor and db[i] - base > rise and (last < 0 or (i - last) * hop > gap):
            t.append(i * hop); last = i
    return t
sr = 16000
for vfile in sorted(glob.glob(os.path.join(S, "videos", "*.mp4"))):
    vid = os.path.basename(vfile)[:-4]
    voc = glob.glob(os.path.join(S, "stems", f"{vid}_(Vocals)*.wav")); ins = glob.glob(os.path.join(S, "stems", f"{vid}_(Instrumental)*.wav"))
    if not voc or not ins: print(vid, "missing stems"); continue
    v, m = load(voc[0], sr), load(ins[0], sr); n = min(len(v), len(m)); v, m = v[:n], m[:n]
    vdb, mdb = env_db(v, sr), env_db(m, sr)
    speaking = vdb > (np.percentile(vdb, 95) - 25)
    music_on = mdb > -50
    k = min(len(speaking), len(mdb))
    duck = float(np.median(mdb[:k][~speaking[:k]]) - np.median(mdb[:k][speaking[:k]])) if (~speaking[:k]).sum() > 50 and speaking[:k].sum() > 50 else None
    ons = onsets(mdb)
    met = json.load(open(os.path.join(S, "metrics", vid + ".json")))
    cuts = met["cuts"]; dur = n / sr
    def hit(ts, a=-0.15, b=0.10): return sum(any(a <= o - c <= b for o in ons) for c in ts)
    rnd = [random.uniform(0.5, dur - 0.5) for _ in range(400)]
    res = {"id": vid, "lufs_vocals": lufs(voc[0]), "lufs_music_sfx": lufs(ins[0]),
           "music_present_pct": round(100 * float(music_on.mean()), 1), "music_drop_when_speaking_db": round(duck, 1) if duck is not None else None,
           "transients": len(ons), "transients_per_min": round(len(ons) / dur * 60, 1), "transient_times": [round(o, 2) for o in ons],
           "cuts": len(cuts), "cuts_with_transient": hit(cuts), "cuts_with_transient_pct": round(100 * hit(cuts) / len(cuts), 1) if cuts else None,
           "random_baseline_pct": round(100 * hit(rnd) / len(rnd), 1)}
    res["music_vs_voice_db"] = round(res["lufs_music_sfx"] - res["lufs_vocals"], 1) if res["lufs_music_sfx"] is not None and res["lufs_vocals"] is not None else None
    json.dump(res, open(os.path.join(out, vid + ".json"), "w"), indent=1)
    print(vid, {k: res[k] for k in ("lufs_vocals", "lufs_music_sfx", "music_vs_voice_db", "music_present_pct", "music_drop_when_speaking_db", "transients_per_min", "cuts_with_transient_pct", "random_baseline_pct")})
