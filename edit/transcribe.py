from faster_whisper import WhisperModel
import json
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = m.transcribe("edit/audio.wav", word_timestamps=True, vad_filter=True)
out=[]
lines=[]
for s in segs:
    words=[{"w":w.word,"s":round(w.start,2),"e":round(w.end,2)} for w in (s.words or [])]
    out.append({"start":round(s.start,2),"end":round(s.end,2),"text":s.text.strip(),"words":words})
    lines.append(f"[{s.start:7.2f} - {s.end:7.2f}] {s.text.strip()}")
json.dump(out, open("edit/transcript.json","w"), indent=1)
open("edit/transcript.txt","w").write("\n".join(lines))
print(f"segments: {len(out)}  duration≈{out[-1]['end'] if out else 0:.1f}s")
print("\n".join(lines))
