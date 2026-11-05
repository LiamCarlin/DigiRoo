#!/usr/bin/env python3
"""
qc.py — measure a finished cut before anyone sees it ("the user should never be the first viewer").

    python3 qc.py media/cuts/w46-mon-couch-every-night.mp4
    python3 qc.py media/cuts/w46-mon-couch-every-night.mp4 --reference saved-reel.mp4

Reads <cut>.edit.json (written by edit_cuts.py) when it exists. Writes, next to the cut:
  <cut>.qc.md / .qc.json   every check with PASS / WARN / FAIL and the number behind it
  <cut>.sheet.jpg          24 frames from the exported file, with timestamps
  <cut>.hook.jpg           0–3 s every 0.5 s: the muted test (is the point clear with the sound off?)
  <cut>.stills.jpg         4 stills: frame one, the lift, the after-hold, the end card (each must work as a poster)
  <cut>.safezone.jpg       a captioned frame with the TikTok/Reels UI zones shaded red
  <cut>.vs-reference.jpg   (with --reference) the two contact sheets side by side
Exit code 1 if anything FAILs. Every number in the report comes from a command that ran (earshot process.md:133).
"""
import argparse, json, os, re, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dvlib as L
from dvlib import W, H, FPS, SAFE, run


def atoms(path):
    order = []
    with open(path, "rb") as f:
        while len(order) < 12:
            hdr = f.read(8)
            if len(hdr) < 8: break
            size, kind = struct.unpack(">I4s", hdr)
            order.append(kind.decode("latin-1"))
            if size == 1: size = struct.unpack(">Q", f.read(8))[0]; f.seek(size - 16, 1)
            elif size == 0: break
            else: f.seek(size - 8, 1)
    return order

def frame_stats(path, t=0.0):
    from PIL import Image, ImageStat
    f = L.grab(path, t, path + f".f{t:.2f}.png")
    if not f: return None
    st = ImageStat.Stat(Image.open(f).convert("L")); os.remove(f)
    return round(st.mean[0], 1), round(st.stddev[0], 1)

def diffs(path):
    """Frame-to-frame mean abs difference (0–255) at full frame rate on a 96x54 grey copy (huashu qa.js, video-director qa_video.py)."""
    return [(t, v * 255) for t, v in L.motion_series(path, fps=FPS)]

def glitches(series, declared, hold_from):
    vals = [v for _, v in series]; out = {"cuts": [], "flashes": [], "frozen": [], "undeclared": []}
    for i in range(1, len(vals) - 1):
        lo, hi = max(0, i - 15), min(len(vals), i + 16)
        med = L._median(vals[lo:hi])
        t = series[i][0]
        if vals[i] > 14 and vals[i] > 4 * (med + 0.5):
            out["cuts"].append(round(t, 2))
            if not any(abs(t - c) <= 2.0 / FPS for c in declared):
                out["undeclared"].append(round(t, 2))
        # a flash: one odd frame — big change in and straight back out, with calm frames either side
        hi = max(6, 4 * med)
        if 1 < i < len(vals) - 2 and vals[i] > hi and vals[i + 1] > hi and abs(vals[i] - vals[i + 1]) < 0.35 * vals[i] \
                and vals[i - 1] < hi / 3 and vals[i + 2] < hi / 3 and not any(abs(t - c) <= 2.0 / FPS for c in declared):
            out["flashes"].append(round(t, 2))
    run_start = None
    for t, v in series:
        if v < 0.25 and t < hold_from:
            run_start = t if run_start is None else run_start
        else:
            if run_start is not None and t - run_start >= 1.0: out["frozen"].append([round(run_start, 2), round(t, 2)])
            run_start = None
    return out

def beats(path):
    """Beat table for comparing against a reference (reanimate's analysis loop, adapted to footage)."""
    s = diffs(path); info = L.probe(path)
    g = glitches(s, [], info["duration"] + 1)
    burst = L.find_lift(path)
    cuts = []  # a dissolve or whip in someone else's reel spans a few frames: count it once
    for i, c in enumerate(g["cuts"]):
        if not i or c - g["cuts"][i - 1] > 3.5 / FPS: cuts.append(c)
    shots = [0.0] + cuts + [info["duration"]]
    return {"duration": round(info["duration"], 2), "cuts": cuts,
            "shot_lengths": [round(b - a, 2) for a, b in zip(shots, shots[1:])],
            "biggest_move": round(burst[1], 2) if burst else None, "loudness": L.loudness(path)}

def sheet_strip(path, out, times, width=270, cols=None):
    from PIL import Image, ImageDraw, ImageFont
    tiles = []
    for i, t in enumerate(times):
        f = L.grab(path, t, out + f".{i}.jpg", width)
        if f: tiles.append((t, Image.open(f).convert("RGB"))); os.remove(f)
    if not tiles: return None
    cols = cols or len(tiles); rows = (len(tiles) + cols - 1) // cols; tw, th = tiles[0][1].size
    im = Image.new("RGB", (cols * (tw + 4) + 4, rows * (th + 4) + 4), (24, 24, 24))
    font = ImageFont.truetype(L.font_path(700), max(14, width // 12))
    for i, (t, tile) in enumerate(tiles):
        x, y = 4 + (i % cols) * (tw + 4), 4 + (i // cols) * (th + 4)
        im.paste(tile, (x, y)); ImageDraw.Draw(im).text((x + 6, y + 4), f"{t:.1f}s", font=font, fill=(255, 230, 0), stroke_width=2, stroke_fill=(0, 0, 0))
    im.save(out, quality=88); return out

def run_qc(path, log=None, reference=None):
    stem = os.path.splitext(path)[0]
    if log is None and os.path.exists(stem + ".edit.json"):
        log = json.load(open(stem + ".edit.json"))
    log = log or {}
    info = L.probe(path); checks = []
    def add(name, status, value, rule):
        checks.append({"check": name, "status": status, "value": value, "rule": rule})

    # --- file ---
    ok = (info["w"], info["h"]) == (W, H)
    add("size", "PASS" if ok else "FAIL", f"{info['w']}x{info['h']}", "exactly 1080x1920")
    add("frame rate", "PASS" if abs(info["fps"] - FPS) < 0.1 else "WARN", info["fps"], "30 fps")
    add("codec", "PASS" if info["vcodec"] == "h264" and info["pix_fmt"] == "yuv420p" and info["acodec"] == "aac" else "FAIL",
        f"{info['vcodec']}/{info['pix_fmt']}/{info['acodec']}", "h264 yuv420p + aac")
    order = atoms(path)
    fast = "moov" in order and ("mdat" not in order or order.index("moov") < order.index("mdat"))
    add("fast start", "PASS" if fast else "WARN", " > ".join(order[:4]), "moov before mdat, so it plays while uploading")
    dur = info["duration"]; long_ok = log.get("recipe") in ("talking-head",)
    add("length", "PASS" if 10 <= dur <= (60 if long_ok else 30.5) else "WARN", f"{dur:.1f}s", "10–30 s (scripted talking head up to 60)")
    lt = log.get("length_target")
    if lt and len(lt) == 2:
        add("length vs. this week", "PASS" if lt[0] - 0.5 <= dur <= lt[1] + 0.5 else "WARN", f"{dur:.1f}s", f"{lt[0]}–{lt[1]} s (trends.md)")

    # --- sound ---
    ld = L.loudness(path)
    if ld["lufs"] is None or ld["lufs"] < -60:
        add("loudness", "WARN", "silent", "-14 LUFS ±1 (a silent cut needs a sound plan: her voice, the real click, or a bed)")
    else:
        add("loudness", "PASS" if abs(ld["lufs"] - L.LUFS) <= 1.0 else "WARN", f"{ld['lufs']} LUFS", "-14 LUFS ±1, measured after AAC")
        add("true peak", "PASS" if ld["tp"] is not None and ld["tp"] <= -1.0 else "WARN", f"{ld['tp']} dBTP", "≤ -1 dBTP")
    mi = log.get("music_info")
    if mi:  # the music verification step: licensed, and never over her voice
        add("music licence", "PASS" if mi.get("license") and mi.get("source") else "FAIL",
            f"{mi.get('license') or 'none'} · {mi.get('source') or 'no source page'}",
            "licence + the track's own page recorded in edit.json (CC0 / Mixkit / Pixabay, read that session)")
        bal = mi.get("balance") or {}
        mg = bal.get("speech_band_margin_db")
        if mg is not None:
            add("music under voice", "PASS" if mg >= 15 else ("WARN" if mg >= 10 else "FAIL"), f"{mg} dB under her voice (1-4 kHz, while talking)",
                "her words stay clear: the bed sits ≥15 dB under the voice in the speech band (raise under_voice_db)")
            gp = bal.get("gaps_under_voice_db")
            if gp is not None:
                add("music in the gaps", "PASS" if 8 <= gp <= 24 else "WARN", f"{gp} dB under her talking level",
                    "between lines the bed is heard but never louder than 8 dB under her voice (8-24 dB)")
        else:
            lvl = bal.get("music_level_db")
            add("music present", "PASS" if lvl is not None and lvl > -45 else "WARN", f"{lvl} dBFS before the master" if lvl is not None else "silent",
                "no one talks, so the bed carries the cut: it must be there and the master must reach -14 LUFS")
    if log.get("sfx"):
        n = len(log["sfx"])
        add("sound effects", "PASS" if n <= 2 else "WARN", ", ".join(f"{x['sound']} at {x['at']}s ({x['gain_db']} dB)" for x in log["sfx"]),
            "at most 2, under the voice (edit-style.md)")
    body_end = log.get("body_end", dur)
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-t", f"{body_end:.2f}", "-vn", "-af", "silencedetect=n=-50dB:d=1.0", "-f", "null", "-"], check=False)
    sil = [round(float(x), 2) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    if ld["lufs"] is not None and ld["lufs"] > -60:
        add("dead air", "PASS" if not sil else "WARN", sil or "none", "no silence ≥1 s before the end card (fine if she adds the in-app sound)")

    # --- picture ---
    fs = frame_stats(path, 0.0)
    add("frame one", "PASS" if fs and fs[0] >= 8 and fs[1] >= 6 else "FAIL", f"mean {fs[0]} sd {fs[1]}" if fs else "unreadable",
        "frame 0 is a finished picture, not black or flat")
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf", "blackdetect=d=0.1:pix_th=0.10", "-f", "null", "-"], check=False)
    blacks = re.findall(r"black_start:([\d.]+)", p.stderr)
    add("black frames", "PASS" if not blacks else "FAIL", blacks or "none", "no black frames")
    series = diffs(path)
    g = glitches(series, log.get("cuts", []), body_end)
    add("flash frames", "PASS" if not g["flashes"] else "FAIL", g["flashes"] or "none", "no single-frame flashes")
    add("frozen picture", "PASS" if not g["frozen"] else "WARN", g["frozen"] or "none", "nothing frozen ≥1 s before the end card (designed holds excepted)")
    add("unplanned jumps", "PASS" if not g["undeclared"] else "WARN", g["undeclared"] or "none", "every hard picture change is a planned cut (a fast hand can trip this; look)")
    early = [v for t, v in series if t < 5]
    add("opening moves", "PASS" if early and max(early) >= 1.5 else "WARN", f"peak {max(early):.1f}" if early else "-", "something moves in the first 5 s")

    # --- words on screen ---
    boxes = log.get("text", [])
    title = next((b for b in boxes if b["slot"] == "title"), None)
    add("title in frame one", "PASS" if title and title["s"] <= 0.04 else ("WARN" if title else "FAIL"),
        title["text"] if title else "no title", "video-rules 1: the title is on screen at 0.0 s")
    if title:
        native = log.get("style", "classic") == "native"  # native: TikTok Sans on a box, sized like the niche's own text
        tmin = 52 if native else 84
        add("title size", "PASS" if title["size"] >= tmin and title["lines"] <= 4 else "WARN", f"{title['size']} px, {title['lines']} lines",
            f"≥{tmin} px, ≤4 lines ({'native style: TikTok-size text on a box, references/edit-style.md' if native else 'video-director, take-one'})")
        n = len(title["text"].split())
        add("title length", "PASS" if 5 <= n <= 13 else "WARN", f"{n} words", "6–12 words + credential")
    nat = log.get("style") == "native"
    sx0, sy1 = (65, 1250) if nat else (SAFE["x0"], SAFE["y1"])  # native also clears Reels: 6 % sides, bottom 35 % (Meta ads guide)
    bad = []
    for b in boxes:
        x0, y0, x1, y1 = b["box"]
        right = SAFE["rail_x"] if y1 > SAFE["rail_y"] else W - sx0
        if x0 < sx0 or x1 > right or y0 < SAFE["y0"] or y1 > sy1:
            bad.append(f"{b['text'][:24]}… {b['box']}")
    add("safe zone", "PASS" if not bad else "FAIL", bad or "all text inside",
        f"x {sx0}–940 beside the button rail, y {SAFE['y0']}–{sy1}" + (" (TikTok + Reels)" if nat else ""))
    floor = 38 if log.get("style") == "native" else 70  # native labels are 40 px pills; captions 60 px
    small = [f"{b['text'][:20]} {b['size']}px" for b in boxes if b["size"] < floor]
    add("text size", "PASS" if not small else "WARN", small or f"all ≥{floor} px", f"nothing that must be read under {floor} px")
    caps = [b for b in boxes if b["slot"] == "cap"]
    wmax, rate = (4, 7.0) if nat else (5, 3.6)
    long_cues = [c["text"] for c in caps if len(c["text"].split()) > wmax]
    add("words per caption", "PASS" if not long_cues else "WARN", long_cues or f"{len(caps)} cues ≤{wmax} words",
        "1–4 words, one line (native)" if nat else "2–5 words a cue")
    fast = [f"{c['text']} ({len(c['text'].split()) / max(c['e'] - c['s'], 0.01):.1f}/s)" for c in caps
            if len(c["text"].split()) / max(c["e"] - c["s"], 0.01) > rate]
    add("caption speed", "PASS" if not fast else "WARN", fast[:4] or f"all ≤{rate:g} words/s",
        "≤7 words/s: synced to her voice; fast text did better in VidMob's 1,400 TikTok ads (references/edit-style.md)" if nat
        else "captions read at ≤3.5 words a second (video-director)")
    still = [b for b in boxes if b["slot"].startswith("over")]
    short = [b["text"] for b in still if (b["e"] - b["s"]) < max(1.5, 1.0 + 0.3 * len(b["text"].split())) - 0.05]
    if still:
        add("overlay hold", "PASS" if not short else "WARN", short or "all held long enough", "on screen ≥ max(1.5 s, 1 s + 0.3 s a word)")
    clash = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a["s"] < b["e"] and b["s"] < a["e"] and not (a["box"][2] < b["box"][0] or b["box"][2] < a["box"][0] or a["box"][3] < b["box"][1] or b["box"][3] < a["box"][1]):
                clash.append(f"'{a['text'][:16]}' × '{b['text'][:16]}'")
    add("text over text", "PASS" if not clash else "FAIL", clash or "none", "one read at a time, never text over text")
    said = " ".join(b["text"].lower() for b in boxes)
    hits = [w for w in L.BANNED if re.search(r"\b" + re.escape(w) + r"\b", said)]
    add("claim words", "PASS" if not hits else "FAIL", hits or "none", "brief §4 banned words / §5 claims")

    # --- the recipe ---
    shots = [c for c in log.get("clips", []) if not c.get("clip", "").startswith("clinic")]
    if shots:
        add("cuts between shots", "PASS" if len(shots) - 1 <= 3 else "WARN", f"{len(shots)} shots", "video-rules 3: ≤3 cuts, one kid, one place")
    if log.get("recipe") == "slouch-to-lift":
        la, be = log.get("lift_at"), log.get("body_end") or dur
        pos = la / be if la and be else None
        add("lift found", "PASS" if la and 0.25 <= pos <= 0.6 else "WARN", f"{la}s ({pos:.0%} in)" if la else "not found",
            "the stand-pop sits 25–60 % in, after a slouch you can see (check the pop still: is it the stand?)")
    if log:
        q = log.get("end_question") or next((b["text"] for b in reversed(boxes) if "?" in b["text"]), None)
        add("ends on a question", "PASS" if q and "?" in q else "WARN", q or "no question", "video-rules 8: save/share line + a question")

    # --- pictures to look at ---
    out = {}
    out["sheet"] = L.contact_sheet(path, stem + ".sheet.jpg")
    out["hook"] = sheet_strip(path, stem + ".hook.jpg", [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], width=240)
    lift = log.get("lift_at") or dur * 0.4
    still_t = [0.0, lift, min(body_end - 0.5, lift + 2.5), min(dur - 0.3, body_end + 1.0)]
    out["stills"] = sheet_strip(path, stem + ".stills.jpg", still_t, width=360)
    capt = next((c for c in caps if c["e"] - c["s"] > 0.5), None)
    f = L.grab(path, (capt["s"] + capt["e"]) / 2 if capt else min(1.0, dur / 2), stem + ".sz.png")
    if f: out["safezone"] = L.safe_zone_preview(f, stem + ".safezone.jpg"); os.remove(f)

    ref = None
    if reference:
        ours, theirs = beats(path), beats(reference)
        ref = {"ours": ours, "reference": theirs}
        rs = L.contact_sheet(reference, stem + ".ref-sheet.jpg")
        if rs and out["sheet"]:
            from PIL import Image
            a, b = Image.open(out["sheet"]), Image.open(rs)
            im = Image.new("RGB", (a.width + b.width + 12, max(a.height, b.height)), (0, 0, 0))
            im.paste(a, (0, 0)); im.paste(b, (a.width + 12, 0)); im.save(stem + ".vs-reference.jpg", quality=85)
            os.remove(rs); out["vs_reference"] = stem + ".vs-reference.jpg"

    fails = [c for c in checks if c["status"] == "FAIL"]; warns = [c for c in checks if c["status"] == "WARN"]
    verdict = "FAIL" if fails else ("PASS with notes" if warns else "PASS")
    md = [f"# QC — {os.path.basename(path)}", "", f"**{verdict}** · {dur:.1f}s · {ld['lufs']} LUFS · {len(log.get('cuts', []))} cuts · "
          f"{len(caps)} captions", "", "| Check | Result | Measured | Rule |", "|---|---|---|---|"]
    for c in checks:
        v = c["value"] if isinstance(c["value"], str) else json.dumps(c["value"])
        md.append(f"| {c['check']} | {c['status']} | {v[:90]} | {c['rule']} |")
    md += ["", "## Look at these before saying it's done",
           f"- `{os.path.basename(out.get('hook') or '')}`: with the sound off, does 0–3 s say what this is and why to keep watching?",
           f"- `{os.path.basename(out.get('stills') or '')}`: would each still work as a poster? Is the slouch visible before the product?",
           f"- `{os.path.basename(out.get('safezone') or '')}`: no word under the red zones.",
           f"- `{os.path.basename(out.get('sheet') or '')}`: one kid, one place; same framing before and after; nothing jarring.",
           "- Score 1–10: hook, readable at phone size, the change is visible, rhythm, sound. Ship at 8+ on every line; "
           "take 2 points off your own scores (makers grade high). Name the three weakest moments with timestamps."]
    if log.get("decisions"):
        md += ["", "## Decisions made for her (she can overturn any in one reply)"] + [f"- {d}" for d in log["decisions"]]
    if log.get("warnings"):
        md += ["", "## Warnings from the cut"] + [f"- {w}" for w in log["warnings"]]
    if ref:
        md += ["", "## Against the reference", "| | ours | reference |", "|---|---|---|"]
        for k in ("duration", "cuts", "shot_lengths", "biggest_move"):
            md.append(f"| {k} | {ref['ours'][k]} | {ref['reference'][k]} |")
        md.append(f"| loudness | {ref['ours']['loudness']['lufs']} | {ref['reference']['loudness']['lufs']} |")
    open(stem + ".qc.md", "w").write("\n".join(md) + "\n")
    json.dump({"verdict": verdict, "checks": checks, "files": out, "reference": ref}, open(stem + ".qc.json", "w"), indent=2)
    print("\n".join(md[:len(checks) + 6]))
    print(f"\nQC: {verdict} — {stem}.qc.md")
    return verdict

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cut"); ap.add_argument("--reference")
    a = ap.parse_args()
    sys.exit(1 if run_qc(a.cut, reference=a.reference) == "FAIL" else 0)
