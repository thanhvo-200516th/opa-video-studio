"""faster-whisper large-v3 (cached on this machine, CPU int8): word timestamps for a Vietnamese voice track.

  ffmpeg -i source.mp4 -vn -ac 1 -ar 16000 raw16k.wav
  PYTHONIOENCODING=utf-8 python transcribe.py raw16k.wav whisper_raw.json
Output: [{"win", "start", "end", "text", "words": [{"w", "s", "e", "p"}]}]. "win" is the start of the
30 s decoding window; repeated or merged sentences show up near window changes (check them with retx.py).
About 4-5 min for 131 s of audio.
"""
import json, sys
from faster_whisper import WhisperModel

src, dst = sys.argv[1], sys.argv[2]
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, info = model.transcribe(src, language="vi", word_timestamps=True, vad_filter=False, beam_size=5)
out = []
for s in segments:
    out.append({"win": round(s.seek * 0.01, 2), "start": s.start, "end": s.end, "text": s.text,
                "words": [{"w": w.word, "s": w.start, "e": w.end, "p": w.probability} for w in s.words]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text}", flush=True)
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE", flush=True)
