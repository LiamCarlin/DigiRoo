#!/usr/bin/env python3
"""
edit_cuts.py — raw phone clips + a post card → one captioned 9:16 cut.

    python3 edit_cuts.py --edit media/week-01/edits/w45-mon-pov-couch.json
    python3 edit_cuts.py --card media/week-01/post-cards/w45-mon-pov-couch.md \
                         --clips media/raw/week-01/mon --out media/cuts/w45-mon-pov-couch.mp4

Pipeline
  1. (optional) transcribe each clip with faster-whisper → word timestamps
  2. trim each clip to its spoken segment (whisper) or to non-silent audio (ffmpeg silencedetect)
  3. normalise to 1080x1920 30fps, concatenate in shot-list order
  4. burn captions (word-timed if whisper, script-timed otherwise), big sans, safe zone
  5. hook text on top for the first 2 s, optional end card
  6. export <out>.mp4 + <out>.srt + <out>.edit.json (what was done)

Whisper is optional. With --no-whisper (or when faster_whisper/model download isn't available)
the script still produces a finished cut using script-timed captions; that is the mode
used for the Friday demo in the sandbox. On a Mac with faster-whisper installed, word-level
timing kicks in automatically.

edit.json schema
{
  "output": "media/cuts/w45-mon-pov-couch.mp4",
  "hook": "POV: you look over and see this",        # top overlay, first 2 s (optional)
  "end_card": {"line1": "Screen Time, Elevated.", "line2": "DigiRoo · link in bio", "seconds": 2.5},
  "caption": {"words_per_cue": 3, "uppercase": false, "size": 72, "margin_v": 430},
  "music": {"file": "bed.mp3", "volume": 0.15},     # optional
  "clips": [
    {"file": "IMG_0001.MOV", "text": "Every parent has seen this.", "trim": "auto"},
    {"file": "IMG_0002.MOV", "text": "", "trim": [0.5, 4.0], "overlay": "and now I don't have to say sit up"},
    {"file": "IMG_0003.MOV", "text": "DigiRoo. It's in my bio.", "trim": "auto", "mute": true}
  ]
}
"text"  = what is said in that clip (from the post card script). Used for caption timing when
          whisper isn't available, and to pick the right spoken segment when it is.
"trim"  = "auto" (speech/silence based), [start, end] seconds, or null (keep all).
"overlay" = on-screen text line for that clip (mid-screen), from the post card.
"""
import argparse, json, os, re, shlex, subprocess, sys, tempfile, shutil
from difflib import SequenceMatcher

W, H, FPS = 1080, 1920, 30
FONT_CANDIDATES = ["Poppins", "Montserrat", "Inter", "Liberation Sans", "DejaVu Sans"]

# ---------- helpers ----------
def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.stderr.write("FAILED: " + " ".join(shlex.quote(c) for c in cmd) + "\n" + p.stderr[-3000:] + "\n")
        raise SystemExit(1)
    return p

def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path]).stdout.strip() or 0)

def has_audio(path):
    return bool(run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", path]).stdout.strip())

def pick_font():
    for name in FONT_CANDIDATES:
        out = subprocess.run(["fc-match", name], capture_output=True, text=True).stdout
        if name.split()[0].lower() in out.lower():
            return name
    return "DejaVu Sans"

def ass_t(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def srt_t(t):
    t = max(t, 0); ms = int(round((t - int(t)) * 1000)); t = int(t)
    return f"{t//3600:02d}:{t%3600//60:02d}:{t%60:02d},{ms:03d}"

def esc(s):
    return s.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")

# ---------- step 1: transcription ----------
def transcribe(path, model_name="base"):
    """Return list of {'w','s','e'} word dicts, or None if whisper unavailable."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        segs, _ = model.transcribe(path, word_timestamps=True, vad_filter=True, language="en")
        words = []
        for seg in segs:
            for w in (seg.words or []):
                words.append({"w": w.word.strip(), "s": float(w.start), "e": float(w.end)})
        return words
    except Exception as e:  # model download blocked, etc.
        sys.stderr.write(f"[whisper unavailable: {e.__class__.__name__}] falling back to script-timed captions\n")
        return None

def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).split()

def locate_script_in_words(script, words, pad=0.25):
    """Find the span of transcribed words that best matches the script line. Returns (start, end, matched_words)."""
    if not words:
        return None
    target = norm(script)
    toks = [norm(w["w"])[0] if norm(w["w"]) else "" for w in words]
    best, best_i, best_j = 0.0, 0, len(words)
    n = len(target)
    for i in range(len(toks)):
        for j in range(i + max(1, n // 2), min(len(toks), i + n * 2) + 1):
            r = SequenceMatcher(None, target, toks[i:j]).ratio()
            if r > best:
                best, best_i, best_j = r, i, j
    if best < 0.45:
        return None
    span = words[best_i:best_j]
    return max(span[0]["s"] - pad, 0), span[-1]["e"] + pad, span

# ---------- step 2: trimming ----------
def silence_trim(path, noise="-30dB", min_sil=0.35, pad=0.2):
    """Trim leading/trailing silence using ffmpeg silencedetect. Returns (start, end)."""
    dur = duration(path)
    if not has_audio(path):
        return 0.0, dur
    p = run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=noise={noise}:d={min_sil}", "-f", "null", "-"], check=False)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    s, e = 0.0, dur
    if starts and starts[0] < 0.05 and ends:          # leading silence
        s = ends[0]
    if starts and (len(ends) < len(starts) or ends[-1] >= dur - 0.15) and starts[-1] > s:  # trailing silence runs to EOF
        e = starts[-1]
    s = max(s - pad, 0); e = min(e + pad, dur)
    if e - s < 0.8:
        return 0.0, dur
    return s, e

# ---------- step 3: normalise ----------
def normalise(src, dst, start=None, end=None, mute=False):
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    if start: cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", src]
    if end: cmd += ["-to", f"{max(end - (start or 0), 0.3):.3f}"]
    if mute or not has_audio(src):
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-shortest", "-map", "0:v:0", "-map", "1:a:0"]
    else:
        cmd += ["-map", "0:v:0", "-map", "0:a:0", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11"]
    cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", dst]
    run(cmd)
    return duration(dst)

def end_card(dst, line1, line2, seconds):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H), (20, 24, 38))
    d = ImageDraw.Draw(img)
    fp = subprocess.run(["fc-match", "-f", "%{file}", pick_font() + ":bold"], capture_output=True, text=True).stdout.strip()
    f1 = ImageFont.truetype(fp, 96); f2 = ImageFont.truetype(fp, 56)
    for txt, f, y in ((line1, f1, H * 0.42), (line2, f2, H * 0.52)):
        bw = d.textlength(txt, font=f)
        d.text(((W - bw) / 2, y), txt, font=f, fill=(255, 255, 255))
    png = dst + ".png"; img.save(png)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-i", png,
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-t", str(seconds),
         "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest", dst])
    return seconds

# ---------- step 4: captions ----------
def cues_from_words(words, offset, per_cue):
    out = []
    for i in range(0, len(words), per_cue):
        grp = words[i:i + per_cue]
        out.append((offset + grp[0]["s"], offset + grp[-1]["e"] + 0.05, " ".join(w["w"] for w in grp)))
    return out

def cues_from_text(text, offset, dur, per_cue):
    words = text.split()
    if not words: return []
    groups = [words[i:i + per_cue] for i in range(0, len(words), per_cue)]
    weights = [sum(len(w) for w in g) for g in groups]; tot = sum(weights)
    lead = min(0.15, dur * 0.05); usable = max(dur - lead - 0.05, 0.4); t = offset + lead; out = []
    for g, wgt in zip(groups, weights):
        seg = usable * wgt / tot
        out.append((t, t + seg, " ".join(g))); t += seg
    return out

def build_ass(cues, overlays, hook, cfg, total):
    font = pick_font(); size = int(cfg.get("size", 72)); mv = int(cfg.get("margin_v", 430)); up = cfg.get("uppercase", False)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,1,2,80,80,{mv},1
Style: Hook,{font},{int(size*1.15)},&H00FFFFFF,&H000000FF,&H00000000,&H9A000000,-1,0,0,0,100,100,0,0,3,10,0,8,70,70,300,1
Style: Over,{font},{int(size*0.95)},&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,1,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if hook:
        ev.append(f"Dialogue: 1,{ass_t(0)},{ass_t(min(2.2, total))},Hook,,0,0,0,,{{\\fad(0,150)}}{esc(hook.upper() if up else hook)}")
    for s, e, txt in overlays:
        ev.append(f"Dialogue: 1,{ass_t(s)},{ass_t(e)},Over,,0,0,0,,{{\\fad(120,120)}}{esc(txt)}")
    for s, e, txt in cues:
        ev.append(f"Dialogue: 0,{ass_t(s)},{ass_t(e)},Cap,,0,0,0,,{{\\fad(40,40)}}{esc(txt.upper() if up else txt)}")
    return head + "\n".join(ev) + "\n"

def write_srt(cues, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (s, e, t) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_t(s)} --> {srt_t(e)}\n{t}\n\n")

# ---------- post card → edit.json ----------
def card_to_edit(card_path, clips_dir, out):
    txt = open(card_path, encoding="utf-8").read()
    m = re.search(r"## Script.*?```\n(.*?)```", txt, re.S)
    script_lines = [l.strip().strip("'\"") for l in (m.group(1) if m else "").splitlines() if l.strip() and not l.strip().startswith("[") and not l.strip().startswith("(")]
    hook = (re.search(r"\*\*On screen:\*\* `(.*?)`", txt) or [None, ""])[1]
    overlays = re.findall(r"^\d+\. `(.*?)`", txt, re.M)
    files = sorted(f for f in os.listdir(clips_dir) if f.lower().endswith((".mp4", ".mov", ".m4v")))
    clips = []
    for i, f in enumerate(files):
        clips.append({"file": os.path.join(clips_dir, f), "text": script_lines[i] if i < len(script_lines) else "",
                      "trim": "auto", "overlay": overlays[i] if i < len(overlays) else ""})
    return {"output": out, "hook": hook, "end_card": {"line1": "Screen Time, Elevated.", "line2": "DigiRoo · link in bio", "seconds": 2.5},
            "caption": {"words_per_cue": 3}, "clips": clips}

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--edit"); ap.add_argument("--card"); ap.add_argument("--clips"); ap.add_argument("--out")
    ap.add_argument("--no-whisper", action="store_true"); ap.add_argument("--whisper-model", default="base")
    ap.add_argument("--transcripts", help="dir of precomputed <clipname>.words.json (skips whisper)")
    a = ap.parse_args()
    if a.edit:
        cfg = json.load(open(a.edit)); base = os.path.dirname(os.path.abspath(a.edit))
    elif a.card and a.clips:
        cfg = card_to_edit(a.card, a.clips, a.out or "cut.mp4"); base = os.getcwd()
    else:
        ap.error("give --edit edit.json or --card card.md --clips dir --out file.mp4")
    out = cfg.get("output", a.out or "cut.mp4")
    if not os.path.isabs(out): out = os.path.join(base, out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="cuts_"); parts = []; cues = []; overlays = []; offset = 0.0; log = []
    per_cue = int(cfg.get("caption", {}).get("words_per_cue", 3))

    for i, clip in enumerate(cfg["clips"]):
        src = clip["file"] if os.path.isabs(clip["file"]) else os.path.join(base, clip["file"])
        if not os.path.exists(src): raise SystemExit(f"missing clip: {src}")
        text = (clip.get("text") or "").strip(); trim = clip.get("trim", "auto"); words = None; mode = "keep"
        if a.transcripts:
            tp = os.path.join(a.transcripts, os.path.basename(src) + ".words.json")
            if os.path.exists(tp): words = json.load(open(tp))
        elif not a.no_whisper and not clip.get("mute"):
            words = transcribe(src, a.whisper_model)
        start = end = None
        if isinstance(trim, list):
            start, end = trim; mode = "manual"
        elif trim == "auto":
            loc = locate_script_in_words(text, words) if (words and text) else None
            if loc:
                start, end, span = loc; mode = "whisper"
                words = [{"w": w["w"], "s": w["s"] - start, "e": w["e"] - start} for w in span]
            else:
                start, end = silence_trim(src); mode = "silence"
        dst = os.path.join(tmp, f"c{i:02d}.mp4")
        d = normalise(src, dst, start, end, mute=clip.get("mute", False))
        if text:
            cues += cues_from_words(words, offset, per_cue) if mode == "whisper" else cues_from_text(text, offset, d, per_cue)
        if clip.get("overlay"):
            overlays.append((offset + 0.1, offset + d - 0.1, clip["overlay"]))
        log.append({"clip": os.path.basename(src), "trim_mode": mode, "start": round(start or 0, 2), "end": round(end or 0, 2), "duration": round(d, 2)})
        parts.append(dst); offset += d

    ec = cfg.get("end_card")
    if ec:
        dst = os.path.join(tmp, "end.mp4"); offset += end_card(dst, ec.get("line1", "Screen Time, Elevated."), ec.get("line2", "DigiRoo · link in bio"), float(ec.get("seconds", 2.5))); parts.append(dst)
    total = offset

    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    ass = os.path.join(tmp, "caps.ass"); open(ass, "w", encoding="utf-8").write(build_ass(cues, overlays, cfg.get("hook"), cfg.get("caption", {}), total))

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", joined]
    music = cfg.get("music")
    if music and music.get("file"):
        mp = music["file"] if os.path.isabs(music["file"]) else os.path.join(base, music["file"])
        cmd += ["-stream_loop", "-1", "-i", mp, "-filter_complex",
                f"[0:v]ass={shlex.quote(ass)}[v];[1:a]volume={music.get('volume', 0.15)}[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
                "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-vf", f"ass={shlex.quote(ass)}"]
    cmd += ["-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
    run(cmd)
    srt = os.path.splitext(out)[0] + ".srt"; write_srt(cues, srt)
    json.dump({"output": out, "duration_sec": round(total, 2), "clips": log, "captions": len(cues), "hook": cfg.get("hook")},
              open(os.path.splitext(out)[0] + ".edit.json", "w"), indent=2)
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"output": out, "srt": srt, "duration_sec": round(total, 2), "clips": log, "captions": len(cues)}, indent=2))

if __name__ == "__main__":
    main()
