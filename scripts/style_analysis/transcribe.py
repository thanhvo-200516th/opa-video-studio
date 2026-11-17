"""Bóc lời tiếng Việt kèm mốc từng từ (faster-whisper large-v3-turbo). transcripts/<id>.json + .txt"""
import os, shutil, sys, json, glob, subprocess
import numpy as np
from faster_whisper import WhisperModel
vid_dir, out_dir = sys.argv[1], sys.argv[2]; os.makedirs(out_dir, exist_ok=True)
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
try:
    model = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cuda", compute_type="int8_float16"); dev = "cuda"
except Exception as e:
    print("cuda fail:", e); model = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8"); dev = "cpu"
print("device", dev)
for f in sorted(glob.glob(os.path.join(vid_dir, "*.mp4"))):
    vid = os.path.basename(f)[:-4]
    if os.path.exists(os.path.join(out_dir, vid + ".json")): continue
    pcm = subprocess.run([FF, '-v', 'error', '-i', f, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    segs, info = model.transcribe(audio, language="vi", word_timestamps=True, vad_filter=True, beam_size=5)
    out = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
            "words": [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]} for s in segs]
    json.dump(out, open(os.path.join(out_dir, vid + ".json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(out_dir, vid + ".txt"), "w").write("\n".join(f"[{s['start']:6.2f}-{s['end']:6.2f}] {s['text']}" for s in out))
    print(vid, len(out), "segments")
