#!/usr/bin/env python3
"""
check_clips.py — look at Antonia's raw clips the moment they land and say, in plain words, keep or reshoot.
Run it while the kid is still around, so a dark or sideways take costs two minutes, not a week.

    python3 check_clips.py media/raw/week-02/w46-mon-couch-every-night
    python3 check_clips.py IMG_0412.MOV IMG_0413.MOV --kind slouch-to-lift

Writes <folder>/clips-check.md (the table) and <folder>/clips-check.jpg (first / middle / last frame of each clip,
for Claude to judge framing: side-on, head in frame, room at the top for the title). Never modifies a clip.
--kind slouch-to-lift also looks for the stand-pop and says whether there's enough slouch before and upright after.
"""
import argparse, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dvlib as L

VIDEO = (".mov", ".mp4", ".m4v")

def check(path, kind=None):
    info = L.probe(path); name = os.path.basename(path)
    notes, verdict = [], "keep"
    def fix(level, msg):
        nonlocal verdict
        notes.append(msg)
        if level == "redo": verdict = "redo"
        elif level == "warn" and verdict == "keep": verdict = "keep (see note)"
    if info["w"] > info["h"]:
        fix("redo", "filmed sideways: hold the phone upright (portrait)")
    if min(info["w"], info["h"]) < 1080:
        fix("warn", f"{min(info['w'], info['h'])}p is soft: Camera settings → Record Video → 1080p HD at 30 fps")
    if info["hdr"]:
        fix("warn", "HDR is on: fine, I convert it, but turning off Settings → Camera → Record Video → HDR Video keeps colours truer")
    if info["fps"] and not (23 <= info["fps"] <= 31 or 59 <= info["fps"] <= 61):
        fix("warn", f"{info['fps']} fps: use 30 fps")
    if info["duration"] < 2.5:
        fix("redo", f"only {info['duration']:.1f}s: keep rolling 3 s before and after the action")
    br = L.brightness(path)
    if br:
        if br["mean"] < 45:
            fix("redo", f"too dark (brightness {br['mean']}): face a window or switch on a lamp beside the phone")
        elif br["mean"] < 70:
            fix("warn", f"a bit dark (brightness {br['mean']}): open the curtains or move closer to the window")
        if br["high"] >= 250 and br["mean"] > 170:
            fix("warn", "bright patches blown out: don't film with a window behind her; tap her face to set exposure")
    speech = L.speech_spans(path) if info["has_audio"] else []
    ld = L.loudness(path) if info["has_audio"] else {"lufs": None, "tp": None}
    if speech:
        lv = sorted(v for _, v in L.level_series(path))
        floor = lv[int(len(lv) * 0.10)] if lv else -90
        if ld["lufs"] is not None and ld["lufs"] < -38:
            fix("warn", f"voice is quiet ({ld['lufs']} LUFS): film closer, about an arm's length, or record the line as a voice memo")
        if ld["tp"] is not None and ld["tp"] > -0.5:
            fix("warn", "sound distorts: too close to the mic, wind, or shouting")
        if floor > -45:
            fix("warn", f"noisy room (background {floor:.0f} dB): TV, fan, dishwasher or AC off for talking takes")
    motion = L.motion_series(path, fps=10, top=0.2)
    vals = sorted(v for _, v in motion)
    still = L._median(vals) * 255 if vals else 0  # background movement = the camera moving, not the kid
    if still > 3.0:
        fix("warn", f"the camera moves (steadiness {still:.1f}): lean the phone on a mug or against a book, and don't touch it")
    lift = None
    if kind == "slouch-to-lift":
        lift = L.find_lift(path)
        if not lift:
            fix("redo", "no stand-pop found: one take, phone still, slouch → pop the stand → upright")
        else:
            a, pk, b = lift
            others = [x[1] for x in L.lift_bursts(path) if abs(x[1] - pk) > 1.0]
            if others:  # a parent walking in or a kid flailing can out-move the stand; the pop frame in the sheet settles it
                notes.append(f"pop read at {pk:.1f}s, other movement at {', '.join(f'{t:.1f}s' for t in others)}: check the "
                             f"'pop' frame in clips-check.jpg; if it isn't the stand going up, the edit takes lift.at <second>")
            if a < 3.0: fix("warn", f"only {a:.1f}s of slouch before the pop: let her settle into her show for 5+ s first")
            if info["duration"] - b < 4.0: fix("warn", f"only {info['duration'] - b:.1f}s upright after: keep rolling 5+ s after the pop")
    if info["size_mb"] > 30:
        notes.append(f"{info['size_mb']} MB: may be too big to attach in a chat; AirDrop it to the Mac or put it in the Drive folder")
    return {"clip": name, "verdict": verdict, "duration": round(info["duration"], 1), "size": f"{info['w']}x{info['h']}",
            "fps": info["fps"], "hdr": info["hdr"], "brightness": br["mean"] if br else None,
            "voice": bool(speech), "lufs": ld["lufs"], "steadiness": round(still, 1),
            "lift": [round(x, 1) for x in lift] if lift else None, "notes": notes}

def strip(paths, out, pops=None):
    """First, middle and last frame of each clip; slouch-to-lift clips get a fourth frame at the detected pop,
    so a wrong pop (a parent walking in, a kid waving) is caught by eye before the cut."""
    from PIL import Image, ImageDraw, ImageFont
    rows, pops = [], pops or {}
    for p in paths:
        d = L.duration(p); ims = []
        times = [(0.3, ""), (d / 2, ""), (max(d - 0.3, 0), "")]
        if pops.get(p) is not None: times.insert(2, (pops[p], f"pop {pops[p]:.1f}s"))
        for t, label in times:
            f = L.grab(p, t, out + ".tmp.jpg", 200)
            if f: ims.append((Image.open(f).convert("RGB"), label)); os.remove(f)
        if ims: rows.append((os.path.basename(p), ims))
    if not rows: return None
    tw, th = rows[0][1][0][0].size; lab = 34; cols = max(len(r[1]) for r in rows)
    im = Image.new("RGB", (cols * (tw + 4) + 4, len(rows) * (th + lab + 4) + 4), (24, 24, 24))
    font = ImageFont.truetype(L.font_path(700), 22); d = ImageDraw.Draw(im)
    for r, (name, ims) in enumerate(rows):
        y = 4 + r * (th + lab + 4); d.text((8, y + 4), name, font=font, fill=(255, 230, 0))
        for c, (tile, label) in enumerate(ims):
            x = 4 + c * (tw + 4); im.paste(tile.resize((tw, th)), (x, y + lab))
            if label: d.text((x + 6, y + lab + 6), label, font=font, fill=(255, 230, 0), stroke_width=2, stroke_fill=(0, 0, 0))
    im.save(out, quality=85); return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+"); ap.add_argument("--kind", help="slouch-to-lift: also find the stand-pop")
    a = ap.parse_args()
    files = []
    for p in a.paths:
        files += sorted(f for f in glob.glob(os.path.join(p, "*")) if f.lower().endswith(VIDEO)) if os.path.isdir(p) else [p]
    if not files: raise SystemExit("no clips found")
    res = [check(f, a.kind) for f in files]
    folder = a.paths[0] if os.path.isdir(a.paths[0]) else os.path.dirname(os.path.abspath(files[0]))
    md = ["| Clip | Verdict | Length | Size | Light | Voice | Steady | Notes |", "|---|---|---|---|---|---|---|---|"]
    for r in res:
        voice = f"{r['lufs']} LUFS" if r["voice"] else "—"
        md.append(f"| {r['clip']} | **{r['verdict']}** | {r['duration']}s | {r['size']}{' HDR' if r['hdr'] else ''} | {r['brightness']} | {voice} | "
                  f"{r['steadiness']} | {'; '.join(r['notes']) or 'good'} |")
    redo = [r["clip"] for r in res if r["verdict"] == "redo"]
    head = f"{len(res)} clips: {len(res) - len(redo)} good" + (f", {len(redo)} to redo ({', '.join(redo)})" if redo else "")
    sheet = strip(files, os.path.join(folder, "clips-check.jpg"), {f: r["lift"][1] for f, r in zip(files, res) if r["lift"]})
    open(os.path.join(folder, "clips-check.md"), "w").write(f"# Clip check\n\n{head}\n\n" + "\n".join(md) + "\n")
    print(head); print("\n".join(md))
    if sheet: print(f"\nframes: {sheet}")
    json.dump(res, open(os.path.join(folder, "clips-check.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
