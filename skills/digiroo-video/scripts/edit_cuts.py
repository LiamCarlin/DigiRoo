#!/usr/bin/env python3
"""
edit_cuts.py — Antonia's raw phone clips + a post card → one finished, checked 9:16 cut.

    python3 edit_cuts.py --edit media/week-02/edits/w46-mon-couch-every-night.json
    python3 edit_cuts.py --card media/week-02/post-cards/w46-mon-couch-every-night.md \
                         --clips media/raw/week-02/w46-mon-couch-every-night --out media/cuts/w46-mon-couch-every-night.mp4

What it does, in order
  1. picks the best take when a shot has several (whisper match score, else the last take)
  2. trims each clip: to the spoken line (whisper or adaptive speech detection), around the stand-pop
     ("lift": strongest burst of motion in a static take), or to the seconds you give
  3. tightens talking clips: cuts pauses longer than max_pause, alternating a 1.1x punch-in to hide each jump
  4. normalises picture (1080x1920, 30 fps, iPhone HDR → SDR, mild grade) and sound (voice chain, per-clip level)
  5. draws every word with Pillow (persistent title, captions, overlays, end card) and composites it, so no
     libass/drawtext build of ffmpeg is needed
  6. mixes voice-over, a music bed ducked under the voice (with a dip just before the lift) and sound effects,
     then one static gain to -14 LUFS with a limiter so peaks stay under -1 dBTP after AAC
  7. exports <out>.mp4 + .srt + .edit.json + .cover.jpg and runs qc.py on the result

Nothing in media/raw is ever written to. Whisper (faster-whisper) is optional; without it captions are timed
to the detected speech in each clip, which is close enough to post.

edit.json — every key is optional except "clips"
{
  "output": "media/cuts/w46-mon-couch-every-night.mp4",
  "recipe": "slouch-to-lift",            # slouch-to-lift | talking-head | voiceover | text-story (sets defaults)
  "length_target": [18, 26],             # this week's band from trends.md; qc.py warns outside it (rule 5 still applies)
  "title": "every night, same couch, same slouch (mom + inventor)",   # frame one, upper third, whole video
  "title_until": "first_cut",            # or seconds: end the title early when it would mislabel a later shot or cover a face
  "end_card": {"question": "what's your house rule?", "save": "save this for the next iPad session",
               "brand": "DigiRoo · link in bio", "seconds": 3, "style": "freeze"},   # or false
  "caption": {"words_per_cue": 3, "size": 80},
  "music": {"file": "bed.m4a", "under_voice_db": 12, "dip_before_lift": true},     # licensed or her own
  "sfx": [{"file": "click.wav", "at": "lift", "gain_db": -6}],
  "intro": "clinic-intro.mov",           # prepended untouched (affiliate pack: the clinic's 5-s selfie line)
  "vo": "vo.m4a", "vo_text": "...",      # voice memo laid over muted clips; clips follow the voice
  "clips": [
    {"file": "IMG_0412.MOV", "trim": "lift", "lift": {"before": 3.5, "after": 4.5}},   # + "at": 8.1 when the auto pop is wrong
    {"takes": ["IMG_0415.MOV", "IMG_0416.MOV"], "text": "That's it. That's the whole fix.", "tighten": true},
    {"file": "IMG_0418.MOV", "trim": [0.5, 4.0], "mute": true, "overlay": "eye level, no nagging", "push": 1.05}
  ]
}
Per clip: "trim" = "auto" | "lift" | [start, end] | null · "text" = what is said (script line) · "overlay" = on-screen
line for a clip with no speech · "mute" · "tighten" · "max_pause" (0.4) · "punch" (1.0, 1.1 or "auto") ·
"push" (slow push-in, ≤1.08) · "focus" [x, y] crop centre 0–1 · "fit" "crop" | "blur" (landscape footage) ·
"clean": false (UGC with music already under the voice: level it, skip the denoiser; don't tighten it either, the music would jump) ·
"captions": false (her line is already on screen as the title; keeps the voice processing, skips the captions).
"lift": {"before", "after", "at"} · "at" = the second the stand goes up in the raw clip, when the auto pop is wrong.
"music": {"file", "license", "source", "start", "under_voice_db", "dip_before_lift", "carve"} · license + source are required by qc.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dvlib as L
from dvlib import W, H, FPS, run

RECIPES = {
    "slouch-to-lift": {"first_trim": "lift", "end_card": True},
    "talking-head": {"tighten": True, "punch": "auto"},
    "voiceover": {"mute": True},
    "text-story": {"mute": False},
}
# Where each kind of text sits and how it looks. "classic" is the original DigiRoo look (heavy white Poppins with a
# black outline). "native" follows what the niche's top videos actually use (references/edit-style.md): TikTok Sans at
# medium weight, hooks and callouts on rounded boxes, captions with the spoken word on a yellow box.
STYLES = {
    "classic": {
        "label": {"top": 300, "max_w": 700, "size": 44, "kw": dict(style="box", fill="white", box="indigo", upper=True)},
        "title": {"top": 300, "max_w": 960, "size": 84, "small": 76},
        "note": {"top": 600, "max_w": 860, "size": 60},
        "cap": {"bottom": 1340, "max_w": 760, "size": 80, "chars": 28, "per_cue": 3},
        "over": {"bottom": 1340, "max_w": 760, "size": 80},
        "over_hi": {"bottom": 1150, "max_w": 760, "size": 72},
    },
    "native": {
        "label": {"top": 300, "max_w": 760, "size": 40, "kw": dict(weight=800, family="tiktok", style="box", fill="white", box="indigo", upper=True)},
        "title": {"top": 300, "max_w": 740, "size": 54, "small": 50, "kw": dict(weight=600, family="tiktok", style="box", fill="ink", box="white")},
        "note": {"top": 560, "max_w": 740, "size": 42, "kw": dict(weight=600, family="tiktok", style="box", fill="white", box="ink")},
        "cap": {"bottom": 1240, "max_w": 740, "size": 58, "kw": dict(weight=700, family="tiktok", style="soft", stroke=4), "highlight": ("yellow", "ink"),
                "chars": 22, "per_cue": 3},
        "over": {"bottom": 1240, "max_w": 760, "size": 54, "kw": dict(weight=700, family="tiktok", style="box", fill="ink", box="yellow")},
        "over_hi": {"bottom": 1060, "max_w": 760, "size": 50, "kw": dict(weight=700, family="tiktok", style="box", fill="ink", box="yellow")},
    },
}
SLOTS = {k: dict(v) for k, v in STYLES["native"].items()}
LOG = {"decisions": [], "warnings": []}

def decide(msg): LOG["decisions"].append(msg); print("DECISION: " + msg)
def warn(msg): LOG["warnings"].append(msg); print("WARNING: " + msg, file=sys.stderr)


# ---------- 1. transcription and takes ----------
def transcribe(path, model_name="base"):
    """[{'w','s','e'}] word dicts in source seconds, or None when faster-whisper isn't installed."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        model = transcribe.__dict__.setdefault(model_name, WhisperModel(model_name, device="cpu", compute_type="int8"))
        segs, _ = model.transcribe(path, word_timestamps=True, vad_filter=True, language="en")
        return [{"w": w.word.strip(), "s": float(w.start), "e": float(w.end)} for seg in segs for w in (seg.words or [])]
    except Exception as e:  # model download blocked, etc.
        warn(f"whisper unavailable ({e.__class__.__name__}); captions follow detected speech instead")
        return None

def join_tokens(words):
    """Whisper splits some words into tokens ("built" + "-in", "Mm" + "-hmm"); a caption shows them as one word."""
    out = []
    for w in words or []:
        t = w["w"]
        if out and len(t) > 1 and (t[0] in "-'’" or t.lower() == "n't"):
            out[-1] = {"w": out[-1]["w"] + t, "s": out[-1]["s"], "e": w["e"]}
        else:
            out.append(dict(w))
    return out

def norm(s):
    return re.sub(r"[^a-z0-9' ]", "", s.lower()).split()

def locate(script, words, pad=0.15):
    """Best-matching run of transcribed words for a script line → (start, end, span, score) or None."""
    if not words or not script:
        return None
    target = norm(script); toks = [(norm(w["w"]) or [""])[0] for w in words]
    best, bi, bj = 0.0, 0, len(words); n = len(target)
    for i in range(len(toks)):
        for j in range(i + max(1, n // 2), min(len(toks), i + n * 2) + 1):
            r = SequenceMatcher(None, target, toks[i:j]).ratio()
            if r > best:
                best, bi, bj = r, i, j
    if best < 0.45:
        return None
    span = words[bi:bj]
    return max(span[0]["s"] - pad, 0), span[-1]["e"] + pad, span, best

def pick_take(takes, text, get_words):
    """Highest script-match score wins; ties go to the shorter delivery. No transcript → last take."""
    scored = []
    for t in takes:
        loc = locate(text, get_words(t)) if text else None
        if loc:
            scored.append((loc[3], -(loc[1] - loc[0]), t))
    if scored:
        scored.sort(reverse=True)
        decide(f"take {os.path.basename(scored[0][2])} of {len(takes)} (script match {scored[0][0]:.2f})")
        return scored[0][2]
    decide(f"take {os.path.basename(takes[-1])} of {len(takes)}: the last take, no transcript to compare")
    return takes[-1]


# ---------- 2. trimming ----------
def lift_span(src, info, before, after, at=None):
    found = L.find_lift(src, at=at)
    if not found:
        warn(f"{os.path.basename(src)}: no clear stand-pop found; trimmed to speech/whole clip instead")
        return None
    a, pk, b = found
    s, e = max(0.0, a - before), min(info["duration"], b + after)
    how = f"set by lift.at {float(at):.1f}s" if at is not None else "strongest motion"
    decide(f"{os.path.basename(src)}: stand-pop at {pk:.1f}s ({how}); kept {s:.1f}-{e:.1f}s ({before}s slouch before, {after}s upright after)")
    others = [x[1] for x in L.lift_bursts(src) if abs(x[1] - pk) > 1.0]
    if others and at is None:  # a parent walking in or a kid flailing can out-move the stand: say so, so the eye check looks
        decide(f"{os.path.basename(src)}: other motion at {', '.join(f'{t:.1f}s' for t in others)}; if stills.jpg shows the wrong "
               f"moment at the pop, set \"lift\": {{\"at\": <seconds into the raw clip>}}")
    return s, e, pk

def speech_trim(src, info, text, words):
    if words and text:
        loc = locate(text, words)
        if loc:
            return loc[0], min(loc[1], info["duration"]), "whisper"
    spans = L.speech_spans(src) if info["has_audio"] else []
    if spans:
        return max(0.0, spans[0][0] - 0.15), min(info["duration"], spans[-1][1] + 0.25), "speech"
    return 0.0, info["duration"], "whole"

def tighten(s, e, words, src, max_pause):
    """Cut pauses longer than max_pause inside [s, e]. Returns kept sub-spans in source seconds."""
    if words:
        inside = [w for w in words if w["s"] >= s - 0.05 and w["e"] <= e + 0.05]
        gaps = [(a["e"], b["s"]) for a, b in zip(inside, inside[1:]) if b["s"] - a["e"] > max_pause]
        pad = 0.08
    else:
        sp = L.speech_spans(src, s, e)
        gaps = [(a[1], b[0]) for a, b in zip(sp, sp[1:]) if b[0] - a[1] > max_pause]
        pad = 0.10
    keep, cur = [], s
    for g0, g1 in gaps:
        keep.append((cur, g0 + pad)); cur = g1 - pad
    keep.append((cur, e))
    return [(a, b) for a, b in keep if b - a > 0.15]


# ---------- 3–4. picture and sound per part ----------
def vfilter(info, clip, punch=1.0, push=None, frames=0):
    f = []
    if info["hdr"]:
        if L.has_filter("zscale"):
            f.append("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
        else:
            f.append("colorspace=all=bt709:iall=bt2020:itrc=bt2020-10:format=yuv420p:fast=0,eq=contrast=1.05:saturation=1.08")
    fx, fy = (clip.get("focus") or [0.5, 0.42])[:2]
    if clip.get("fit") == "blur" and info["w"] > info["h"]:
        f.append(f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=20:5[bg];"
                 f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
    else:
        f.append(f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy}")
    if punch and punch > 1.001:
        cw, ch = int(W / punch) // 2 * 2, int(H / punch) // 2 * 2
        f.append(f"crop={cw}:{ch}:({W}-{cw})*{fx}:({H}-{ch})*{fy},scale={W}:{H}:flags=lanczos")
    if push and push > 1.001 and frames > 1:
        f.append(f"scale={W*2}:{H*2}:flags=lanczos,zoompan=z='1+({push}-1)*on/{frames}':"
                 f"x='iw/2-(iw/zoom/2)':y='ih*{fy}-(ih/zoom*{fy})':d=1:s={W}x{H}:fps={FPS}")
    if clip.get("look", "natural") == "natural":
        g = clip.get("_lift_gamma", 0.98)  # dark living-room clips get a gentle, measured lift; never a filter look
        f.append(f"eq=contrast=1.04:saturation=1.06:gamma={g:.2f},unsharp=5:5:0.35:5:5:0")
    f.append(f"fps={FPS},setsar=1,format=yuv420p")
    return ",".join(f)

def encode_part(src, dst, s, e, info, clip, punch=1.0, voice=True, hold=0.0):
    dur = max(round((e - s) * FPS), 6) / FPS; hold = round(hold * FPS) / FPS  # whole frames: no A/V drift across parts
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{s:.3f}", "-t", f"{dur:.3f}", "-i", src]
    vf = vfilter(info, clip, punch, clip.get("push"), int(round(dur * FPS)))
    if hold > 0:
        vf += f",tpad=stop_mode=clone:stop_duration={hold:.3f}"
    if clip.get("mute") or not info["has_audio"]:
        cmd += ["-f", "lavfi", "-t", f"{dur + hold:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a"]
    else:
        g = L.gain_to(src, -18.0 if voice else -26.0, s, dur)
        if voice and clip.get("clean") is False:  # UGC with music baked under the voice: the denoiser would smear the music
            chain = f"highpass=f=60,volume={g:.1f}dB"
        else:
            chain = (f"volume={g:.1f}dB," + L.VOICE_CHAIN) if voice else f"highpass=f=60,volume={g:.1f}dB"
        chain += ",alimiter=limit=0.89:level=false,aresample=48000,aformat=channel_layouts=stereo"
        chain += f",afade=t=in:d=0.008,afade=t=out:st={max(dur - 0.03, 0):.3f}:d=0.03"
        if hold > 0:
            chain += f",apad=pad_dur={hold:.3f}"
        cmd += ["-filter_complex", f"[0:v]{vf}[v];[0:a]{chain}[a]", "-map", "[v]", "-map", "[a]"]
    cmd += ["-t", f"{dur + hold:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", dst]
    run(cmd)
    return L.duration(dst)


# ---------- 5. text ----------
WEAK = {"a", "an", "the", "i", "i'm", "my", "his", "her", "their", "our", "your", "of", "to", "for", "and", "or", "but",
        "in", "on", "at", "with", "that", "so", "if", "as", "while", "when", "he", "she", "we", "it's", "is", "was", "rid", "get"}
CLINGS = {"it", "them", "him", "up", "down", "out", "off", "rid", "of", "itself", "himself", "herself", "than", "too"}  # belong to the word before

def chunk(words_txt, per_cue=3, max_chars=None):
    """Cues of 2–5 words that break at a phrase end (explainroo captions.js: ≤28 characters, break at a sentence
    end or pause). A phrase too long for one cue is split into even pieces, so no word is left on its own."""
    max_chars = max_chars or SLOTS["cap"].get("chars", 28)
    most = per_cue + 1 if max_chars < 28 else per_cue + 2  # native captions: 1-4 words on one line
    phrases, cur = [], []
    for w in words_txt:
        cur.append(w)
        if re.search(r"[.!?,;:]$", w):
            phrases.append(cur); cur = []
    if cur: phrases.append(cur)
    def weak_end(g):
        return not re.search(r"[.!?,;:]$", g[-1]) and g[-1].lower() in WEAK
    def split(ph):
        """Best split of a long phrase into 1-5-word cues ≤ max_chars: cues near per_cue + 0.5 words, no cue ending
        on "the" / "I" / "of" unless nothing else fits, no lone words (a small dynamic programme; phrases are short)."""
        best = [(0.0, [])] + [(float("inf"), None)] * len(ph)
        for j in range(1, len(ph) + 1):
            for k in range(1, min(most, j) + 1):
                g = ph[j - k:j]
                if k > 1 and len(" ".join(g)) > max_chars:
                    continue
                c = (best[j - k][0] + (k - per_cue - 0.5) ** 2 + (8 if j < len(ph) and weak_end(g) else 0) + (6 if k == 1 else 0)
                     + (12 if j - k > 0 and g[0].lower().strip(",.") in CLINGS else 0))
                if c < best[j][0]:
                    best[j] = (c, best[j - k][1] + [g])
        return best[len(ph)][1]
    groups = []
    for ph in phrases:
        if len(ph) <= most and len(" ".join(ph)) <= max_chars:
            groups.append(ph)
        else:
            groups += split(ph)
    out = []
    for g in groups:  # fold a lone word into its neighbour when the pair still fits
        if out and len(g) == 1 and len(out[-1]) < per_cue + 2 and len(" ".join(out[-1] + g)) <= max_chars:
            out[-1] = out[-1] + g
        else:
            out.append(g)
    return [g for g in out if g]

def clean_cue(ws):
    return L.burnable(" ".join(ws))  # the full stop comes off after merging (merge_flashes needs to see sentence ends)

def cues_from_words(words, per_cue):
    out = []
    for g in chunk([w["w"] for w in words], per_cue):
        sel, words = words[:len(g)], words[len(g):]
        out.append([sel[0]["s"], sel[-1]["e"] + 0.05, clean_cue(g), [(w["s"], w["e"]) for w in sel]])
    return out

def cues_over_spans(text, spans, per_cue):
    """No transcript: share the line's word groups across the detected speech, by length."""
    groups = chunk(text.split(), per_cue)
    if not groups or not spans:
        return []
    total = sum(b - a for a, b in spans); weights = [sum(len(w) for w in g) + 1 for g in groups]; wt = sum(weights)
    def at(x):
        for a, b in spans:
            if x <= b - a: return a + x
            x -= b - a
        return spans[-1][1]
    out, acc = [], 0.0
    for g, w in zip(groups, weights):
        share = total * w / wt
        a0, a1 = at(acc), at(acc + share); n = len(g)  # no transcript: the words share the cue evenly
        out.append([a0, a1, clean_cue(g), [(a0 + k * (a1 - a0) / n, a0 + (k + 1) * (a1 - a0) / n) for k in range(n)]]); acc += share
    return out

def merge_flashes(cues, min_dur=None, max_words=None, max_chars=None):
    """A fast talker (4+ words/s) turns 3-word cues into 0.3 s flashes nobody can read. Fold a cue shorter than
    min_dur into the neighbour it belongs with (the next one, unless it ends a phrase) while the pair still fits two
    caption lines. The words still land with her voice; there are just fewer, longer reads."""
    native = SLOTS["cap"].get("chars", 28) < 28  # one-line captions: fast is fine (VidMob, 1,400 TikTok ads), flashes aren't
    min_dur = min_dur or (0.45 if native else 0.7); max_words = max_words or (4 if native else 5)
    max_chars = max_chars or (SLOTS["cap"].get("chars", 28) + 4 if native else 32)
    cues = [list(c) for c in sorted(cues)]
    i = 0
    while i < len(cues):
        c = cues[i]
        if c[1] - c[0] < min_dur:
            for j in ((i - 1, i + 1) if re.search(r"[,.!?;:]$", c[2]) else (i + 1, i - 1)):
                if not 0 <= j < len(cues):
                    continue
                a, b = sorted((i, j)); txt = cues[a][2] + " " + cues[b][2]
                if re.search(r"[.!?]$", cues[a][2]):
                    continue  # never glue two sentences into one caption
                if len(txt.split()) <= max_words and len(txt) <= max_chars and cues[b][0] - cues[a][1] < 0.6:
                    cues[a] = [cues[a][0], cues[b][1], txt] + ([cues[a][3] + cues[b][3]] if len(cues[a]) > 3 and len(cues[b]) > 3 else [])
                    del cues[b]
                    i = max(a - 1, 0); break
            else:
                i += 1
            continue
        i += 1
    return cues

def settle_cues(cues, min_len=0.6):
    """Minimum time on screen (explainroo/video-director hold rules); stretch into the gap after, never overlap."""
    cues = sorted(cues)
    for i, c in enumerate(cues):
        nxt = cues[i + 1][0] if i + 1 < len(cues) else c[1] + 1.0
        want = max(min_len, 0.4 + 0.2 * len(c[2].split()))
        c[1] = min(max(c[1], c[0] + want), nxt - 0.02) if nxt > c[0] else c[1]
    return [c for c in cues if c[1] - c[0] > 0.1 and c[2]]

def place(img, slot, cfg_size=None):
    sl = SLOTS[slot]
    x = (W - img.width) // 2
    y = sl["top"] if "top" in sl else sl["bottom"] - img.height
    return x, y

def render_text_track(events, total, tmp):
    """events: dicts {slot, text, s, e, enter, kw, hl, point}. Renders one full-frame RGBA PNG per distinct on-screen state
    and returns an ffconcat list. Entering text eases in (captions 4 frames, everything else 8); text on screen at t=0
    never animates, so frame one is finished (video-director: 'Frame 0 is a finished composition'). A title shown
    with a label pill sits just under it. A callout with a "point" gets an arrow to that spot (fractions of the frame)."""
    from PIL import Image
    blocks, boxes, made = {}, [], {}
    for i, ev in enumerate(events):
        sl = SLOTS[ev["slot"]]; size = ev.get("size", sl["size"])
        kw = dict(sl.get("kw", {})); kw.update(ev.get("kw") or {})
        if ev.get("hl") is not None and sl.get("highlight"):
            kw["highlight"] = (ev["hl"],) + tuple(sl["highlight"])
        img, nlines = L.text_block(ev["text"], size, sl["max_w"], **kw)
        if ev["slot"] == "title" and nlines > 4:
            size = sl.get("small", size - 6); img, nlines = L.text_block(ev["text"], size, sl["max_w"], **kw)
            warn(f"title runs past 4 lines; set at {size} px. Aim for 6-12 words.")
        made[i] = (img, nlines, size)
    for i, ev in enumerate(events):
        img, nlines, size = made[i]; x, y = place(img, ev["slot"])
        if ev.get("top") is not None:
            y = int(ev["top"])
        elif ev["slot"] == "title":
            labs = [made[j][0] for j, e2 in enumerate(events) if e2["slot"] == "label" and e2["s"] < ev["e"] and ev["s"] < e2["e"]]
            if labs:
                y = SLOTS["label"]["top"] + max(l.height for l in labs) - 48 + 10
        if ev["slot"] == "note":
            tis = [blocks[j] for j, e2 in enumerate(events[:i]) if e2["slot"] == "title" and e2["s"] < ev["e"] and ev["s"] < e2["e"] and j in blocks]
            if tis:
                y = max(t[2] + t[0].height for t in tis) - 48 + 6
        pt = ev.get("point")
        blocks[i] = (img, x, y, (pt[0] * W, pt[1] * H) if pt else None)
        if ev.get("sub"):
            continue  # one caption, many highlight states: QC sees the caption once
        boxes.append({"slot": ev["slot"], "text": ev["text"], "s": round(ev["s"], 2), "e": round(ev.get("cue_e", ev["e"]), 2),
                      "size": size, "lines": nlines, "box": [x + 24, y + 24, x + img.width - 24, y + img.height - 24]})
    nf = int(round(total * FPS)); fe = [(int(round(ev["s"] * FPS)), int(round(ev["e"] * FPS)), ev.get("enter", 4 if ev["slot"] == "cap" else 8)) for ev in events]
    states, cache, seq = [], {}, 0
    for f in range(nf):
        key = tuple((i, min(f - s, n) if n else n) for i, (s, e, n) in enumerate(fe) if s <= f < e)
        if states and states[-1][0] == key:
            states[-1][2] += 1
        else:
            states.append([key, f, 1])
    lines = ["ffconcat version 1.0"]
    for key, f0, count in states:
        if key not in cache:
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for i, step in key:
                img, x, y, pt = blocks[i]; n = fe[i][2]; p = 1.0
                if n and step < n:  # arrive from 95 % scale with opacity, ease-out, no overshoot (rossark SKILL.md:68,293)
                    p = 1 - (1 - (step + 1) / (n + 1)) ** 3; sc = 0.95 + 0.05 * p
                    im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.LANCZOS)
                    im.putalpha(im.split()[3].point(lambda v: int(v * p)))
                    canvas.alpha_composite(im, (x + (img.width - im.width) // 2, y + (img.height - im.height) // 2))
                else:
                    canvas.alpha_composite(img, (x, y))
                if pt:
                    above = pt[1] < y + img.height / 2
                    L.draw_arrow(canvas, (x + img.width / 2, (y + 22) if above else (y + img.height - 22)), pt, alpha=p)
            fp = os.path.join(tmp, f"txt{seq:04d}.png"); canvas.save(fp); cache[key] = fp; seq += 1
        lines += [f"file '{cache[key]}'", f"duration {count / FPS:.6f}"]
    lines.append(f"file '{cache[states[-1][0]]}'")
    path = os.path.join(tmp, "text.ffconcat"); open(path, "w").write("\n".join(lines) + "\n")
    return path, boxes

def end_card_part(last_part, dst, card, tmp, body=None, style="classic"):
    """The last 3-3.5 s. "freeze" (classic): the last frame blurred and darkened, question + save line + brand.
    "brand": the same backdrop in the native style: the question on a white box, the save line, the DigiRoo wordmark.
    "split": before and after side by side (frames from the body at before_at / after_at), question on top,
    save line and wordmark under: the transformation is the last thing on screen, not a blur."""
    from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
    secs = float(card.get("seconds", 3.0))
    q = L.burnable(card.get("question") or card.get("line1") or "")
    sv = L.burnable(card.get("save") or "")
    br = L.burnable(card.get("brand") or card.get("line2") or "DigiRoo · link in bio")
    kind = card.get("style", "freeze")
    def backdrop(path, t, dim):
        f = L.grab(path, t, os.path.join(tmp, f"bg{t:.2f}.png"))
        im = Image.open(f).convert("RGB").resize((W, H))
        return ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(14))).enhance(dim).convert("RGBA"), Image.open(f).convert("RGB").resize((W, H))
    last_t = max(L.duration(last_part) - 0.05, 0) if last_part else 0
    if kind == "freeze" or style == "classic":
        if last_part:
            bg, _ = backdrop(last_part, last_t, 0.5)
        else:
            bg = Image.new("RGBA", (W, H), (20, 24, 38, 255))
        y = int(H * 0.36)
        for text, size in ((q, 84), (sv, 60), (br, 52)):
            if not text: continue
            img, _ = L.text_block(text, size, 860)
            bg.alpha_composite(img, ((W - img.width) // 2, y)); y += img.height + 20
    else:
        nat = dict(family="tiktok")
        bg, _ = backdrop(body if (kind == "split" and body) else last_part, card.get("after_at", last_t) if (kind == "split" and body) else last_t, 0.38)
        qi, _ = L.text_block(q, 60, 900, weight=600, style="box", fill="ink", box="white", **nat) if q else (None, 0)
        si, _ = L.text_block(sv, 46, 860, weight=600, style="soft", **nat) if sv else (None, 0)
        wm = L.wordmark(76)
        li, _ = L.text_block("link in bio", 40, 600, weight=600, style="soft", **nat)
        y = 300
        if qi: bg.alpha_composite(qi, ((W - qi.width) // 2, y)); y += qi.height - 20
        foot = (si.height - 30 if si else 0) + wm.height + li.height - 10
        if kind == "split" and body:
            # moving split: the before clip on top, the after clip below, both playing (a freeze stops the scroll)
            return split_card(body, dst, card, q, sv, br, secs, tmp)
        else:
            y = max(y, 820)
        if si: bg.alpha_composite(si, ((W - si.width) // 2, y)); y += si.height - 30
        bg.alpha_composite(wm, ((W - wm.width) // 2, y + 6)); y += wm.height + 4
        bg.alpha_composite(li, ((W - li.width) // 2, y - 10))
    png = os.path.join(tmp, "endcard.png"); bg.convert("RGB").save(png)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-i", png, "-f", "lavfi", "-i",
         "anullsrc=channel_layout=stereo:sample_rate=48000", "-t", f"{secs:.3f}", "-vf", f"fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-r", str(FPS), "-c:a", "pcm_s16le", "-shortest", dst])
    return L.duration(dst)

def split_card(body, dst, card, q, sv, br, secs, tmp):
    """Before (top) and after (bottom) play together for `secs`, each a 1080x960 band centred on the kid, with the
    question on top, BEFORE/AFTER pills on the seam and the save line under. Live footage to the last frame."""
    from PIL import Image
    nat = dict(family="tiktok")
    bd = L.duration(body)
    ba = max(0.0, min(float(card.get("before_at", 0.3)), bd - secs))
    aa = max(secs, min(float(card.get("after_at", bd)), bd)) - secs
    fy = (card.get("focus") or [0.5, 0.5])[1]
    cy = int(min(max(fy * H - 480, 0), H - 960)) // 2 * 2
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    qi, _ = L.text_block(q, 54, 860, weight=600, style="box", fill="ink", box="white", **nat) if q else (None, 0)
    if qi: ov.alpha_composite(qi, ((W - qi.width) // 2, 290))
    for txt, col, yy in (("before", "indigo", 960 - 92), ("after", "orange", 960 + 14)):
        ti, _ = L.text_block(txt, 40, 400, weight=800, style="box", fill="white", box=col, upper=True, **nat)
        ov.alpha_composite(ti, (60, yy))
    line = "\n".join(x for x in (sv, br) if x)
    if line:
        si, _ = L.text_block(line, 44, 860, weight=600, style="soft", **nat)
        ov.alpha_composite(si, ((W - si.width) // 2, 1240 - si.height))
    png = os.path.join(tmp, "split_overlay.png"); ov.save(png)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", body, "-loop", "1", "-i", png,
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-filter_complex",
         f"[0:v]trim=start={ba:.3f}:duration={secs:.3f},setpts=PTS-STARTPTS,crop={W}:960:0:{cy}[a];"
         f"[0:v]trim=start={aa:.3f}:duration={secs:.3f},setpts=PTS-STARTPTS,crop={W}:960:0:{cy}[b];"
         f"[a][b]vstack=2[s];[s][1:v]overlay=0:0:shortest=1,fps={FPS},format=yuv420p[v]",
         "-map", "[v]", "-map", "2:a", "-t", f"{secs:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
         "-r", str(FPS), "-c:a", "pcm_s16le", dst])
    return L.duration(dst)

def write_srt(cues, path):
    def t(x):
        x = max(x, 0); ms = int(round((x - int(x)) * 1000)); x = int(x)
        return f"{x//3600:02d}:{x%3600//60:02d}:{x%60:02d},{ms:03d}"
    with open(path, "w", encoding="utf-8") as f:
        for i, c in enumerate(cues, 1):
            f.write(f"{i}\n{t(c[0])} --> {t(c[1])}\n{c[2]}\n\n")


# ---------- post card → edit.json ----------
def clip_order(files, card_txt):
    """Shot order: the card's 'clips:' line if it names the files, else iPhone numbering / recording time."""
    m = re.search(r"clips:\s*([^·\n]+)", card_txt)
    named = [c.strip().split(" ")[0] for c in m.group(1).split(",")] if m else []
    base = {os.path.basename(f): f for f in files}
    if named and all(n in base for n in named):
        return [base[n] for n in named] + [f for f in files if os.path.basename(f) not in named]
    def key(f):
        num = re.search(r"(\d{3,})", os.path.basename(f))
        tag = run(["ffprobe", "-v", "error", "-show_entries", "format_tags=creation_time", "-of", "csv=p=0", f], check=False).stdout.strip()
        return (tag or "", int(num.group(1)) if num else 0, f)
    return sorted(files, key=key)

def card_to_edit(card_path, clips_dir, out):
    txt = open(card_path, encoding="utf-8").read()
    m = re.search(r"## Script.*?```\n(.*?)```", txt, re.S)
    lines = []
    for l in (m.group(1) if m else "").splitlines():
        l = re.sub(r"\([^)]*\)|\[[^\]]*\]", "", l).strip().strip("'\"‘’“”").strip()
        if l: lines.append(l)
    title = (re.search(r"\*\*(?:Title[^*]*|On screen):\*\*\s*`(.*?)`", txt) or [None, ""])[1]
    overlays = re.findall(r"^\d+\. `(.*?)`", txt, re.M)
    question, save = "", "save this for the next iPad session"
    if overlays and "?" in overlays[-1]:
        q = overlays.pop(); question = L.burnable(q.split("?")[0]) + "?"
        save = L.burnable(q.split("?", 1)[1]) or save
    files = clip_order([os.path.join(clips_dir, f) for f in os.listdir(clips_dir) if f.lower().endswith((".mp4", ".mov", ".m4v"))], txt)
    recipe = "slouch-to-lift" if re.search(r"slouch-to-lift", txt, re.I) else None
    clips = [{"file": f, "text": lines[i] if i < len(lines) else "", "trim": "auto",
              "overlay": overlays[i] if i < len(overlays) else ""} for i, f in enumerate(files)]
    if recipe and len(files) == 1:  # one take: the line is spoken in it, overlays sit either side of the pop
        clips[0].update({"trim": "lift", "text": " ".join(lines), "overlay": "",
                         "overlays": [{"text": t, "at": at} for t, at in zip(overlays, ("lift", "after"))]})
    elif recipe and len(files) >= 3:  # before / lift / after as separate clips (same framing, phone untouched)
        names = [os.path.basename(f).lower() for f in files]
        li = next((k for k, n in enumerate(names) if "lift" in n or "pop" in n), 1)
        for k, c in enumerate(clips):
            c["text"], c["overlay"] = "", overlays[k - 1] if 0 < k <= len(overlays) else ""
            c["trim"] = {"last": 3.5} if k < li else ("lift" if k == li else {"first": 5.0})
            if k == li: c["lift"] = {"before": 0.6, "after": 1.2}
        clips[-1]["text"] = " ".join(lines)  # her off-camera line is in the after shot; the upright hold stays 5 s
    decide(f"edit built from {os.path.basename(card_path)}: {len(clips)} clip(s) in shot order, recipe {recipe or 'none'}")
    return {"output": out, "recipe": recipe, "title": title,
            "end_card": {"question": question, "save": save, "brand": "DigiRoo · link in bio"}, "clips": clips}


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--edit"); ap.add_argument("--card"); ap.add_argument("--clips"); ap.add_argument("--out")
    ap.add_argument("--no-whisper", action="store_true"); ap.add_argument("--whisper-model", default="base")
    ap.add_argument("--transcripts", help="dir of precomputed <clipname>.words.json (skips whisper)")
    ap.add_argument("--no-qc", action="store_true"); ap.add_argument("--keep", action="store_true", help="keep the working folder (debugging)")
    a = ap.parse_args()
    if a.edit:
        cfg = json.load(open(a.edit)); base = os.path.dirname(os.path.abspath(a.edit))
    elif a.card and a.clips:
        cfg = card_to_edit(a.card, a.clips, a.out or "cut.mp4"); base = os.getcwd()
    else:
        ap.error("give --edit edit.json, or --card card.md --clips dir --out file.mp4")
    for k in ("ffmpeg", "ffprobe"):
        if not shutil.which(k):
            raise SystemExit(f"{k} not found. On a Mac: brew install ffmpeg")
    def rel(p): return p if os.path.isabs(p) else os.path.join(base, p)
    out = rel(cfg.get("output") or a.out or "cut.mp4"); os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    recipe = RECIPES.get(cfg.get("recipe") or "", {})
    per_cue_cfg = cfg.get("caption", {}).get("words_per_cue")
    style = cfg.get("style", "native")
    if style not in STYLES:
        raise SystemExit(f"unknown style '{style}': use one of {', '.join(STYLES)}")
    SLOTS.clear(); SLOTS.update({k: dict(v) for k, v in STYLES[style].items()})
    SLOTS["cap"]["size"] = int(cfg.get("caption", {}).get("size", SLOTS["cap"]["size"]))
    if cfg.get("title_top"):  # faces in the top third: the hook, its label and the close's question move down together
        d_top = int(cfg["title_top"]) - SLOTS["title"]["top"]
        for k in ("title", "label", "note"):
            SLOTS[k]["top"] += d_top
            if SLOTS[k]["top"] > 600:  # low enough to sit beside the like/comment rail: wrap narrower
                SLOTS[k]["max_w"] = min(SLOTS[k]["max_w"], 720)
    per_cue = int(per_cue_cfg or SLOTS["cap"].get("per_cue", 3))
    tmp = tempfile.mkdtemp(prefix="cuts_")

    words_cache = {}
    def get_words(src):
        if src in words_cache: return words_cache[src]
        w = None
        if a.transcripts:
            tp = os.path.join(a.transcripts, os.path.basename(src) + ".words.json")
            w = json.load(open(tp)) if os.path.exists(tp) else None
        elif not a.no_whisper:
            w = transcribe(src, a.whisper_model)
        words_cache[src] = join_tokens(w) if w else w; return words_cache[src]

    clips = [dict(c) for c in cfg["clips"]]
    if cfg.get("intro"):
        clips = [{"file": cfg["intro"], "text": cfg.get("intro_text", ""), "trim": "auto", "_intro": True, "look": "none"}] + clips
    title = L.burnable(cfg.get("title") or cfg.get("hook") or "")
    if not cfg.get("title") and cfg.get("hook"):
        decide("hook used as the persistent title (video-rules rule 1)")

    # voice-over: clips follow the voice (video-director: picture follows voice)
    vo = rel(cfg["vo"]) if cfg.get("vo") else None
    vo_words, vo_spans, vo_targets = None, [], None
    if vo:
        for c in clips:
            if not c.get("_intro"): c.setdefault("mute", True)
        vo_info = L.probe(vo); vo_words = get_words(vo); vo_spans = L.speech_spans(vo)
        texts = [c.get("text", "") for c in clips if not c.get("_intro")]
        if all(texts):
            starts = []
            if vo_words:
                rest = vo_words
                for t in texts:
                    loc = locate(t, rest)
                    starts.append(loc[0] if loc else None)
                    if loc: rest = [w for w in rest if w["s"] >= loc[1] - 0.2]
            if not vo_words or None in starts:
                counts = [len(t.split()) for t in texts]; tot = sum(counts); speech = sum(b - a for a, b in vo_spans) or vo_info["duration"]
                spans = vo_spans or [(0, vo_info["duration"])]; acc = 0.0; starts = []
                for cnt in counts:
                    x = acc
                    for s0, s1 in spans:
                        if x <= s1 - s0: starts.append(s0 + x); break
                        x -= s1 - s0
                    else: starts.append(spans[-1][1])
                    acc += speech * cnt / tot
            ends = [max(s - 0.3, 0) for s in starts[1:]] + [vo_info["duration"] + 0.4]
            begins = [0.0] + ends[:-1]
            vo_targets = [max(e - b, 0.8) for b, e in zip(begins, ends)]
            decide("each clip runs for its line of the voice-over; the cut lands ~0.3 s before the next line")

    parts, cuts, cues, events, clip_log, overlays = [], [], [], [], [], []
    offset, intro_dur, lift_at, vi = 0.0, 0.0, None, 0
    for i, clip in enumerate(clips):
        for k, v in recipe.items():
            if k in ("tighten", "punch", "mute"): clip.setdefault(k, v)
        if recipe.get("first_trim") and "trim" not in clip and len(cfg["clips"]) == 1 and not clip.get("_intro"):
            clip["trim"] = recipe["first_trim"]  # a one-take: find the pop
        takes = [rel(t) for t in (clip.get("takes") or [clip["file"]])]
        for t in takes:
            if not os.path.exists(t): raise SystemExit(f"missing clip: {t}")
        text = (clip.get("text") or "").strip()
        src = takes[0] if len(takes) == 1 else pick_take(takes, text, get_words)
        info = L.probe(src); name = os.path.basename(src)
        if min(info["w"], info["h"]) < 1080: warn(f"{name}: {info['w']}x{info['h']} is below 1080 wide; it will look soft (film 1080p or 4K)")
        if info["w"] > info["h"]: warn(f"{name}: filmed sideways; cropped to vertical (film the phone upright next time)")
        if info["hdr"]: decide(f"{name}: iPhone HDR clip converted to standard colour (turn HDR Video off in Camera settings)")
        br = L.brightness(src) if clip.get("look", "natural") == "natural" else None
        if br and br["mean"] < 80 and not info["hdr"]:
            clip["_lift_gamma"] = min(1.35, 1.0 + (90 - br["mean"]) / 120)
            decide(f"{name}: dark clip (brightness {br['mean']}), lifted gamma to {clip['_lift_gamma']:.2f}; more window light next time")
        speaks = bool(text) and not clip.get("mute") and info["has_audio"]
        words = get_words(src) if speaks else None
        trim = clip.get("trim", "auto"); mode, pk = "manual", None
        if isinstance(trim, list):
            s, e = float(trim[0]), min(float(trim[1]), info["duration"])
        elif isinstance(trim, dict):  # {"first": 5} or {"last": 3.5}: the opening / closing seconds of a no-speech shot
            if "last" in trim: s, e = max(0.0, info["duration"] - float(trim["last"]) - 0.2), info["duration"] - 0.2
            else: s, e = 0.2, min(info["duration"], 0.2 + float(trim.get("first", info["duration"])))
            mode = "manual"
        elif trim == "lift":
            lp = clip.get("lift", {})
            got = lift_span(src, info, float(lp.get("before", 3.5)), float(lp.get("after", 4.5)), lp.get("at"))
            if got: s, e, pk = got; mode = "lift"
            else: s, e, mode = speech_trim(src, info, text, words)
        elif trim == "auto" and speaks:
            s, e, mode = speech_trim(src, info, text, words)
        else:
            s, e, mode = 0.0, info["duration"], "whole"
        hold = 0.0
        if vo_targets and not clip.get("_intro"):
            want = vo_targets[vi]; vi += 1
            if e - s > want: e = s + want
            else: hold = want - (e - s)
        spans = tighten(s, e, words, src, float(clip.get("max_pause", 0.4))) if (clip.get("tighten") and speaks) else [(s, e)]
        if len(spans) > 1: decide(f"{name}: cut {len(spans) - 1} pause(s) longer than {clip.get('max_pause', 0.4)} s")
        clip_start = offset; heard = []
        for k, (a0, a1) in enumerate(spans):
            punch = clip.get("punch", 1.0)
            if punch == "auto": punch = 1.1 if (len(spans) > 1 and k % 2 == 1) else 1.0
            dst = os.path.join(tmp, f"p{len(parts):03d}.mkv")
            d = encode_part(src, dst, a0, a1, info, clip, float(punch or 1.0), voice=bool(text), hold=hold if k == len(spans) - 1 else 0.0)
            if parts: cuts.append(round(offset, 3))
            parts.append(dst)
            if words:
                for w in words:
                    if a0 <= (w["s"] + w["e"]) / 2 <= a1:
                        heard.append({"w": w["w"], "s": offset + max(w["s"] - a0, 0), "e": offset + min(w["e"] - a0, d)})
            elif speaks:  # timed from the raw clip: the voice chain lifts room noise, the original doesn't
                heard += [(offset + x0 - a0, offset + x1 - a0) for x0, x1 in L.speech_spans(src, a0, a1)]
            offset += d
        cd = offset - clip_start
        if pk is not None: lift_at = clip_start + (pk - s)
        if clip.get("_intro"): intro_dur = cd
        # captions for this clip
        if speaks and not vo and clip.get("captions", True):  # "captions": false when the title already shows the line
            if words:
                cues += cues_from_words(heard, per_cue)
            else:
                cues += cues_over_spans(text, heard or [(clip_start + 0.1, offset - 0.1)], per_cue)
        ov = L.burnable(clip.get("overlay") or "")
        if ov:
            overlays.append({"name": name, "text": ov, "s": clip_start, "e": offset, "with_caps": clip.get("overlay_with_captions"),
                             "point": clip.get("overlay_point")})
        lift_out = clip_start + (pk - s) if pk is not None else None
        for o in clip.get("overlays") or []:  # timed overlays inside one take: "lift" | "after" | "before" | seconds
            at, txt = o.get("at", "after"), L.burnable(o.get("text", ""))
            if not txt: continue
            if at == "lift" and lift_out: w0, w1 = lift_out - 1.6, lift_out + 0.6
            elif at == "after" and lift_out: w0, w1 = lift_out + 0.8, offset
            elif at == "before": w0, w1 = clip_start + 0.6, (lift_out - 0.2 if lift_out else offset)
            elif isinstance(at, (int, float)):  # + 0.15 s: placement keeps 0.05 s clear at each end, so size for that
                w0 = clip_start + at; w1 = w0 + (float(o["dur"]) + 0.1 if o.get("dur") else max(1.5, 1.0 + 0.3 * len(txt.split())) + 0.15)
            else: warn(f"{name}: overlay '{txt}' at '{at}' skipped (no stand-pop found)"); continue
            overlays.append({"name": name, "text": txt, "s": max(w0, clip_start), "e": min(w1, offset), "with_caps": o.get("with_captions"),
                             "point": o.get("point")})
        clip_log.append({"clip": name, "trim_mode": mode, "start": round(s, 2), "end": round(e, 2), "parts": len(spans),
                         "out_start": round(clip_start, 2), "duration": round(cd, 2), "lift_at": round(lift_at, 2) if pk is not None else None})

    # voice-over captions
    if vo:
        vo_at = intro_dur
        if vo_words:
            cues += [[c[0] + vo_at, c[1] + vo_at, c[2], [(a + vo_at, b + vo_at) for a, b in c[3]]] for c in cues_from_words(vo_words, per_cue)]
        else:
            text = cfg.get("vo_text") or " ".join(c.get("text", "") for c in clips if not c.get("_intro"))
            cues += cues_over_spans(text, [(a0 + vo_at, a1 + vo_at) for a0, a1 in vo_spans] or [(vo_at, offset)], per_cue)

    body_end = offset
    def when(v):
        """A moment in the cut: seconds, "lift", "lift+0.6", "end", "first_cut", "title" (0). None if it can't be placed."""
        if v is None: return None
        if isinstance(v, (int, float)): return float(v)
        m = re.match(r"^(lift|end|first_cut|title)\s*([+-]\s*[\d.]+)?$", str(v).strip())
        if not m: raise SystemExit(f"can't read the moment '{v}': use seconds, lift, lift+0.6, end or first_cut")
        base = {"lift": lift_at, "end": body_end, "title": intro_dur,
                "first_cut": next((c for c in cuts if c > intro_dur + 0.5), body_end)}[m.group(1)]
        return None if base is None else base + float((m.group(2) or "0").replace(" ", ""))
    ec = cfg.get("end_card", recipe.get("end_card", True))
    live_close = None
    if ec and isinstance(ec, dict) and ec.get("style") == "live":
        live_close = ec; ec = None  # end on live footage (research: none of the niche's ads freeze; a lone logo frame underperforms)
    if ec:
        ec = ec if isinstance(ec, dict) else {}
        if not (ec.get("question") or ec.get("line1")):
            warn("end card has no question; video-rules rule 8 wants a save/share line and a question")
        dst = os.path.join(tmp, "end.mkv"); cuts.append(round(offset, 3))
        ec.setdefault("style", "freeze" if style == "classic" else "brand")
        body = None
        if ec["style"] == "split":
            bl = os.path.join(tmp, "body.txt"); open(bl, "w").write("".join(f"file '{q}'\n" for q in parts))
            body = os.path.join(tmp, "body.mkv")
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", bl, "-c", "copy", body])
            for k in ("before_at", "after_at"):
                v = ec.get(k)
                ec[k] = (lift_at - 1.0 if lift_at else 0.3) if v is None and k == "before_at" else (body_end - 0.3 if v is None else when(v))
        offset += end_card_part(parts[-1] if parts else None, dst, ec, tmp, body=body, style=style); parts.append(dst)
    total = offset

    n0 = len(cues); cues = merge_flashes(cues)
    if len(cues) < n0: decide(f"folded {n0 - len(cues)} caption flash(es) under 0.7 s into their neighbours (fast speech)")
    # land just ahead of the word; no full stop at the end of an on-screen line (take-one words.md:23)
    cues = settle_cues([[max(c[0] - 0.08, 0), c[1], c[2].rstrip(".")] + c[3:] for c in cues if c[0] < body_end])
    if title:
        t_end = body_end
        tu = cfg.get("title_until")  # multi-shot cuts: a "before" title ("same slouch") must not label the after shot
        if tu == "first_cut":
            t_end = next((c for c in cuts if c > intro_dur + 0.5), body_end)
        elif isinstance(tu, (int, float)):
            t_end = min(body_end, intro_dur + float(tu))
        if t_end < body_end:
            decide(f"title off at {t_end:.1f}s (title_until {tu}); captions and overlays carry the rest")
        events.insert(0, {"slot": "title", "text": title, "s": intro_dur, "e": t_end, "enter": 0 if intro_dur == 0 else 8})
        lab = cfg.get("label")  # a small pill over the title: the credential or the format ("mom review", "before")
        if lab:
            lab = lab if isinstance(lab, dict) else {"text": lab}
            events.insert(1, {"slot": "label", "text": L.burnable(lab["text"]), "s": intro_dur, "e": t_end, "enter": 0 if intro_dur == 0 else 8,
                              "kw": {"box": lab["color"]} if lab.get("color") else {}})
    if live_close:
        ls = max(intro_dur, body_end - float(live_close.get("seconds", 3.0)))
        q = L.burnable(live_close.get("question") or "")
        if not q: warn("live close has no question; video-rules rule 8 wants a save/share line and a question")
        events.append({"slot": "title", "text": q, "s": ls, "e": body_end, "kw": {}, **({"top": live_close["top"]} if live_close.get("top") else {})})
        sv = L.burnable("\n".join(x for x in (live_close.get("save"), live_close.get("brand", "DigiRoo · link in bio")) if x))
        if sv: events.append({"slot": "note", "text": sv, "s": ls + 0.3, "e": body_end})
        decide(f"live close: the question goes over the last {body_end - ls:.1f}s of footage, no end card")
    for tg in cfg.get("tags") or []:  # timed pills in the label slot: "after" once the stand is up
        t0, t1 = when(tg.get("from", 0)), when(tg.get("to", "end"))
        if t0 is None or t1 is None:
            warn(f"tag '{tg.get('text')}' skipped: its moment can't be placed (no stand-pop?)"); continue
        events.append({"slot": "label", "text": L.burnable(tg["text"]), "s": max(0.0, t0), "e": min(body_end, t1),
                       "kw": {"box": tg.get("color", "orange")}, **({"top": tg["top"]} if tg.get("top") else {})})
    # frame one is the cover: a caption already on screen at 0 s arrives finished, like the title
    karaoke = bool(SLOTS["cap"].get("highlight")) and cfg.get("caption", {}).get("highlight", True)
    cap_end = body_end
    if live_close and not live_close.get("keep_captions"):
        cap_end = max(intro_dur, body_end - float(live_close.get("seconds", 3.0)))  # the question is the only read at the end
    for c in cues:
        if c[0] >= cap_end - 0.15:
            continue
        cs, ce, ct = c[0], min(c[1], cap_end), c[2]
        first = {"enter": 0} if cs < 1.0 / FPS else {}
        ws = c[3] if len(c) > 3 else None
        if karaoke and ws and len(ws) == len(ct.split()):  # the spoken word sits on a yellow box as she says it
            for k, (w0, w1) in enumerate(ws):
                ks = cs if k == 0 else max(cs, w0 - 0.04)
                ke = ce if k == len(ws) - 1 else max(ks + 0.04, ws[k + 1][0] - 0.04)
                events.append({"slot": "cap", "text": ct, "s": ks, "e": min(ke, ce), "hl": k, "cue_e": ce,
                               **(first if k == 0 else {"enter": 0, "sub": True})})
        else:
            events.append({"slot": "cap", "text": ct, "s": cs, "e": ce, **first})
    # overlays go only where no caption is showing: one read at a time, never text over text
    for ov in overlays:
        need = max(1.5, 1.0 + 0.3 * len(ov["text"].split()))
        if ov["with_caps"]:
            events.append({"slot": "over_hi", "text": ov["text"], "s": ov["s"] + 0.05, "e": ov["e"] - 0.05, "point": ov.get("point")}); continue
        busy = sorted((max(c[0], ov["s"]), min(c[1], ov["e"])) for c in cues if c[1] > ov["s"] and c[0] < ov["e"])
        free, cur = [], ov["s"] + 0.05
        for b0, b1 in busy:
            if b0 - cur > 0: free.append((cur, b0 - 0.1))
            cur = max(cur, b1 + 0.1)
        free.append((cur, ov["e"] - 0.05))
        best = max(free, key=lambda f: f[1] - f[0])
        if best[1] - best[0] >= need:
            events.append({"slot": "over", "text": ov["text"], "s": best[0], "e": best[1], "point": ov.get("point")})
        elif not busy:
            events.append({"slot": "over", "text": ov["text"], "s": best[0], "e": best[1], "point": ov.get("point")})
            warn(f"{ov['name']}: overlay '{ov['text']}' is on for {best[1] - best[0]:.1f}s; it needs {need:.1f}s to be read")
        else:
            decide(f"{ov['name']}: overlay '{ov['text']}' left off because captions fill that clip (one text system)")

    lst = os.path.join(tmp, "parts.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    joined = os.path.join(tmp, "joined.mkv")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    track, boxes = render_text_track(events, total, tmp)

    # ---- 6. mix ----
    ins = ["-i", joined, "-f", "concat", "-safe", "0", "-i", track]; n_in = 2
    zs, fxs, fys = [], [], []
    for z in cfg.get("zooms") or []:  # a quick punch-in on the beat: ease in 0.18 s, hold, ease out 0.25 s
        za = when(z.get("at"))  # (not "a": that's the command line)
        if za is None: warn(f"zoom at '{z.get('at')}' skipped: no stand-pop found"); continue
        zd = float(z.get("dur", 1.4)); sc = min(float(z.get("scale", 1.1)), 1.15); zb = za + zd
        fx, fy = (z.get("focus") or [0.5, 0.42])[:2]
        T = f"(in/{FPS})"
        zs.append(f"{sc - 1:.3f}*clip(({T}-{za:.3f})/0.18,0,1)*clip(({zb:.3f}-{T})/0.25,0,1)")
        fxs.append((za, zb, fx)); fys.append((za, zb, fy))
        decide(f"punch-in {sc:.2f}x at {za:.1f}s for {zd:.1f}s")
    vin = "[0:v]"
    if zs:
        def pick(vals, default):
            e = str(default)
            for z0, z1, v in reversed(vals):
                e = f"if(between(in/{FPS},{z0 - 0.3:.3f},{z1 + 0.3:.3f}),{v},{e})"
            return e
        zoom = "1+" + "+".join(zs)
        fc0 = (f"[0:v]zoompan=z='{zoom}':x='(iw-iw/zoom)*{pick(fxs, 0.5)}':y='(ih-ih/zoom)*{pick(fys, 0.42)}'"
               f":d=1:s={W}x{H}:fps={FPS},setsar=1[vz]")
        vin = "[vz]"
    fc = ["[1:v]format=rgba[t]", f"{vin}[t]overlay=0:0:format=auto,format=yuv420p[v]"]
    if zs:
        fc.insert(0, fc0)
    voice = ["[0:a]"]
    # voice-over and music are rendered through their chains first: loudnorm's 3 s lookahead gets dropped at
    # end-of-stream when it sits inside the big video+audio graph (seen with ffmpeg 9), so it never goes in there
    def prerender(src, chain, dst, pre=()):
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *pre, "-i", src, "-vn", "-af", chain + ",aresample=48000",
             "-ac", "2", "-c:a", "pcm_s16le", dst]); return dst
    if vo:
        vo_wav = prerender(vo, f"volume={L.gain_to(vo, -18.0):.1f}dB," + L.VOICE_CHAIN + ",alimiter=limit=0.89:level=false", os.path.join(tmp, "vo.wav"))
        ins += ["-i", vo_wav]; d_ms = int(intro_dur * 1000)
        fc.append(f"[{n_in}:a]adelay={d_ms}|{d_ms}[vo]"); n_in += 1
        voice.append("[vo]")
    fc.insert(2, f"[0:a]apad=whole_dur={total:.3f}[base]"); voice[0] = "[base]"
    fc.append(("".join(voice) + f"amix=inputs={len(voice)}:duration=first:normalize=0," if len(voice) > 1 else "[base]") + "asplit=3[voice][key][vstem]")
    bus = ["[voice]"]
    mu = cfg.get("music")
    stems = None
    if mu and mu.get("file"):
        under = float(mu.get("under_voice_db", 12))
        talks = bool(vo) or any((c.get("text") or "").strip() and not c.get("mute") for c in clips)
        # carve a little room for her voice: the bed loses 4 dB around 2.5 kHz, where consonants live (earshot mixing)
        carve = ",equalizer=f=2500:t=q:w=1.0:g=-4" if talks and mu.get("carve", True) else ""
        m_at = float(mu.get("start", 0.0))  # skip a track's intro: "start": 6.5
        mu_wav = prerender(rel(mu["file"]), f"atrim=0:{total:.3f},volume={L.gain_to(rel(mu['file']), -18 - under, m_at or None, total):.1f}dB{carve}",
                           os.path.join(tmp, "music.wav"), pre=(("-ss", f"{m_at:.3f}") if m_at else ()) + ("-stream_loop", "-1", "-t", f"{total + 1:.3f}"))
        if not (mu.get("license") and mu.get("source")):
            warn("music has no licence recorded: add \"license\" and \"source\" (the track's own page) to edit.json; QC fails it until then")
        ins += ["-i", mu_wav]
        m = f"[{n_in}:a]aformat=channel_layouts=stereo,atrim=0:{total:.3f}"
        if lift_at and mu.get("dip_before_lift", True):  # earshot: pull the bed down 0.3–0.5 s before the hit, back on the hit
            m += f",volume='if(between(t,{lift_at - 0.45:.3f},{lift_at:.3f}),0.35,1)':eval=frame"
            decide(f"music dips for 0.45 s before the stand-pop at {lift_at:.1f}s")
        m += f",afade=t=out:st={max(total - 1.5, 0):.3f}:d=1.5[mraw]"
        fc.append(m); n_in += 1
        fc.append("[mraw][key]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=280:makeup=1,asplit=2[music][mstem]")
        bus.append("[music]")
        # stems for the balance check (qc: "music under voice", "music in the gaps"): measured, not guessed
        stems = (os.path.join(tmp, "stem_voice.wav"), os.path.join(tmp, "stem_music.wav"))
    else:
        fc.append("[key]anullsink"); fc.append("[vstem]anullsink")
    sfx_log = []
    for k, sfx in enumerate(cfg.get("sfx") or []):
        at = when(sfx.get("at", 0))
        if at is None: warn("sfx at 'lift' skipped: no stand-pop found"); continue
        sfx_log.append({"sound": os.path.basename(sfx["file"]).replace("builtin:", ""), "at": round(at, 2), "gain_db": sfx.get("gain_db", -6)})
        f_sfx = sfx["file"]
        f_sfx = L.make_sfx(f_sfx[8:], os.path.join(tmp, f"sfx{k}.wav")) if f_sfx.startswith("builtin:") else rel(f_sfx)
        ins += ["-i", f_sfx]; ms = int(max(at + float(sfx.get("offset", 0)), 0) * 1000)
        fc.append(f"[{n_in}:a]aresample=48000,aformat=channel_layouts=stereo,volume={float(sfx.get('gain_db', -6))}dB,adelay={ms}|{ms}[sfx{k}]")
        bus.append(f"[sfx{k}]"); n_in += 1
    fc.append("".join(bus) + f"amix=inputs={len(bus)}:duration=first:normalize=0,atrim=0:{total:.3f}[a]" if len(bus) > 1 else "[voice]atrim=0:" + f"{total:.3f}[a]")
    mixed = os.path.join(tmp, "mixed.mkv")
    if a.keep: open(os.path.join(tmp, "mix.txt"), "w").write(" ".join(ins) + "\n" + ";\n".join(fc) + "\n")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + ins + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
         "-t", f"{total:.3f}"] + L.X264 + ["-c:a", "pcm_s16le", "-ar", "48000", mixed]
        + ([a for st, lab in zip(stems, ("[vstem]", "[mstem]")) for a in ("-map", lab, "-t", f"{total:.3f}", "-c:a", "pcm_s16le", "-ar", "48000", st)] if stems else []))
    balance = L.mix_balance(stems[0], stems[1], body_end, [(c[0], c[1]) for c in cues]) if stems else None
    if balance:
        decide("music balance: " + ", ".join(f"{k} {v}" for k, v in balance.items()))

    # ---- loudness: one measured static gain + a limiter at -2 dBFS so AAC still lands under -1 dBTP (earshot master.py).
    # Not dynamic loudnorm: it falls back to pumping whenever a transient (the stand's click) would overshoot.
    target = float(cfg.get("loudness", L.LUFS))
    meas = L.loudness(mixed)["lufs"]
    af = []
    def master(limit):
        gain, chain = target - meas, None
        for _ in range(4):  # the limiter eats a little level on peaky mixes; measure and correct (audio only, fast)
            chain = f"volume={gain:.2f}dB,alimiter=limit={limit}:attack=4:release=60:level=false,aresample=48000"
            probe_wav = os.path.join(tmp, "master.wav")
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", mixed, "-vn", "-af", chain, "-c:a", "pcm_s16le", probe_wav])
            got = L.loudness(probe_wav)["lufs"]
            if got is None or abs(got - target) <= 0.3: break
            gain += min(target - got, 4.0)
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", mixed, "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-af", chain] + L.AAC +
            ["-video_track_timescale", "90000", "-movflags", "+faststart", out])
        return L.loudness(out)
    if meas is not None and meas > -60:
        got = master(0.79)
        if got["tp"] is not None and got["tp"] > -1.0:  # AAC overshoot on a peaky mix: one retry with 1 dB more headroom
            decide(f"true peak {got['tp']} dBTP after AAC; re-mastered with the limiter at -3 dBFS")
            got = master(0.70)
        if got["lufs"] is not None and abs(got["lufs"] - target) > 1.0:
            warn(f"master reached {got['lufs']} LUFS, not {target}: the mix is too peaky or too quiet to lift cleanly; add a sound plan (a bed)")
    else:
        warn("the cut is silent or near-silent; loudness not set")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", mixed, "-map", "0:v", "-map", "0:a", "-c:v", "copy"] + L.AAC +
            ["-video_track_timescale", "90000", "-movflags", "+faststart", out])

    stem = os.path.splitext(out)[0]
    srt = stem + ".srt"; write_srt(cues, srt)
    L.grab(out, 0.0, stem + ".cover.jpg")
    log = {"output": out, "duration_sec": round(total, 2), "body_end": round(body_end, 2), "title": title,
           "recipe": cfg.get("recipe"), "style": style, "sfx": sfx_log, "length_target": cfg.get("length_target"), "clips": clip_log, "cuts": cuts, "lift_at": round(lift_at, 2) if lift_at else None,
           "captions": len(cues), "text": boxes, "end_question": ((ec or {}).get("question") or (ec or {}).get("line1")) if ec else ((live_close or {}).get("question")), "music": bool(mu and mu.get("file")), "vo": bool(vo),
           "music_info": ({"file": os.path.basename(mu["file"]), "license": mu.get("license"), "source": mu.get("source"),
                           "under_voice_db": mu.get("under_voice_db", 12), "balance": balance} if mu and mu.get("file") else None),
           "decisions": LOG["decisions"], "warnings": LOG["warnings"]}
    json.dump(log, open(stem + ".edit.json", "w"), indent=2)
    if a.keep: print("working files kept in " + tmp)
    else: shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({k: log[k] for k in ("output", "duration_sec", "cuts", "lift_at", "captions")}, indent=2))
    if not a.no_qc:
        import qc
        qc.run_qc(out, log)

if __name__ == "__main__":
    main()
