"""
dvlib.py — shared helpers for the digiroo-video scripts (edit_cuts.py, check_clips.py, qc.py).

Only needs ffmpeg/ffprobe on PATH and Pillow. Works with a minimal ffmpeg build (no libass, no
drawtext, no zscale): every piece of text is drawn with Pillow and composited with `overlay`.

Numbers in here come from the source skills credited in references/sources.md:
safe zone and type sizes (take-one vertical.md / words.md), loudness and voice chain (take-one audio.md,
earshot sound-design.md), export flags (argo export.ts), visual-event detector (earshot video.py).
"""
import json, math, os, re, shlex, subprocess, sys

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "fonts"))

# 9:16 safe zone for TikTok + Reels at 1080x1920 (take-one vertical.md:21,41,98)
SAFE = {"x0": 56, "x1": 940, "y0": 285, "y1": 1480, "rail_x": 940, "rail_y": 880}
# loudness target for the finished cut (take-one audio.md:17, earshot sound-design.md:55-57)
LUFS, TP = -14.0, -1.5
# voice chain: take-one vo.py:140, plus a light FFT denoise for living-room hum (not in the sources)
VOICE_CHAIN = ("highpass=f=85,afftdn=nf=-30,"
               "equalizer=f=3200:t=q:w=1.1:g=2,equalizer=f=230:t=q:w=1.0:g=-1.5,"
               "acompressor=threshold=-24dB:ratio=3:attack=6:release=110:makeup=2")
# export: argo export.ts:696-750 (x264 aq + bt709 tags kill banding; libx264, not VideoToolbox)
X264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
        "-x264-params", "aq-mode=3:aq-strength=0.8:deblock=1,1:colorprim=bt709:transfer=bt709:colormatrix=bt709",
        "-colorspace:v", "bt709", "-color_primaries:v", "bt709", "-color_trc:v", "bt709", "-color_range", "tv",
        "-r", str(FPS)]
AAC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
BANNED = ["elevate", "elevates", "elevating", "game-changer", "game changer", "revolutionary", "unlock", "seamless",
          "effortlessly", "must-have", "guaranteed", "cure", "cures", "fix your posture", "fixes posture",
          "fixes tech neck", "corrects", "prevents", "prevent tech neck", "medical", "treatment", "treats",
          "therapy", "clinically", "doctor-recommended", "doctor recommended"]


try:
    import PIL  # noqa: F401  (all text, end cards and sheets are drawn with Pillow)
except ImportError:
    raise SystemExit("Pillow is missing. On a Mac: brew install pillow (elsewhere: pip install pillow)")


# ---------- running things ----------
def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.stderr.write("FAILED: " + " ".join(shlex.quote(str(c)) for c in cmd) + "\n" + p.stderr[-3000:] + "\n")
        raise SystemExit(1)
    return p

def has_filter(name, _cache={}):
    if not _cache:
        out = run(["ffmpeg", "-hide_banner", "-filters"], check=False).stdout
        _cache.update({l.split()[1]: True for l in out.splitlines()[8:] if len(l.split()) > 2})
    return name in _cache


# ---------- probing ----------
def probe(path):
    """Return the facts the scripts care about, with rotation already applied to width/height."""
    d = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path]).stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = int(float((v.get("tags") or {}).get("rotate", rot)))
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den or 0) else 0.0
    trc = v.get("color_transfer", "") or ""
    return {
        "path": path, "w": w, "h": h, "fps": round(fps, 2), "rotation": rot,
        "duration": float(d.get("format", {}).get("duration") or v.get("duration") or 0),
        "vcodec": v.get("codec_name", ""), "pix_fmt": v.get("pix_fmt", ""),
        "hdr": trc in ("arib-std-b67", "smpte2084"), "transfer": trc,
        "primaries": v.get("color_primaries", ""),
        "has_audio": a is not None, "acodec": (a or {}).get("codec_name", ""),
        "size_mb": round(os.path.getsize(path) / 1e6, 1),
    }

def duration(path):
    return probe(path)["duration"]


# ---------- picture analysis ----------
def motion_series(path, start=None, end=None, fps=15, changed_px=False, top=None):
    """Mean absolute frame difference per frame on a tiny grey copy (earshot video.py:47-84).
    Returns [(t, diff_0_to_1)]. With changed_px=True, returns the fraction of pixels that moved > 4/255
    instead (take-one gate.mjs:22-31), which is what the dead-air check needs. top=0.2 measures only the top fifth
    of the picture (the wall behind her head), where camera shake shows and a wriggling kid doesn't."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start: cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", path]
    if end: cmd += ["-t", f"{end - (start or 0):.3f}"]
    vf = f"fps={fps}," + (f"crop=iw:ih*{top}:0:0," if top else "") + "scale=96:54:flags=area,format=gray,tblend=all_mode=difference"
    if changed_px:
        vf += ",lutyuv=y='if(gt(val,4),255,0)'"
    vf += ",signalstats,metadata=print:key=lavfi.signalstats.YAVG"
    p = run(cmd + ["-an", "-vf", vf, "-f", "null", "-"], check=False)
    out, t = [], None
    for line in p.stderr.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m: t = float(m.group(1)); continue
        m = re.search(r"signalstats\.YAVG=([\d.]+)", line)
        if m and t is not None:
            out.append(((start or 0) + t, float(m.group(1)) / 255.0)); t = None
    return out

def _median(xs):
    s = sorted(xs); n = len(s)
    return 0.0 if not n else (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2)

def motion_events(series, fps=15):
    """Local maxima above 1.2 % and > 4x the 1-second median (+0.004), or >= 15 %; >= 0.12 s apart
    (earshot video.py:6-10)."""
    vals = [v for _, v in series]; ev = []; half = fps // 2
    for i in range(1, len(vals) - 1):
        if not (vals[i] >= vals[i - 1] and vals[i] >= vals[i + 1]):
            continue
        med = _median(vals[max(0, i - half): i + half + 1])
        if (vals[i] > 0.012 and vals[i] > 4 * med + 0.004) or vals[i] >= 0.15:
            if not ev or series[i][0] - ev[-1][0] >= 0.12:
                ev.append((series[i][0], vals[i]))
            elif vals[i] > ev[-1][1]:
                ev[-1] = (series[i][0], vals[i])
    return ev

_BURSTS = {}
def lift_bursts(path, fps=15, share=0.4):
    """Every clear burst of motion in a static take, strongest first: [(start, peak, end, strength)] in seconds.
    A burst counts when its 0.5 s average clears max(0.008, 2.5x the take's median) and `share` of the strongest;
    peaks closer than 1 s are one burst. In a skit the strongest burst is often NOT the stand-pop: a parent walking
    in close to the lens or a kid flailing moves more pixels than a stand rising (seen on real footage, 2026-11)."""
    key = (path, fps)
    if key not in _BURSTS:
        s = motion_series(path, fps=fps)
        if len(s) < fps * 2:
            _BURSTS[key] = ([], [], 0.0)
        else:
            win = max(3, fps // 2)  # 0.5 s moving average
            vals = [v for _, v in s]
            sm = [sum(vals[max(0, i - win // 2): i + win // 2 + 1]) / len(vals[max(0, i - win // 2): i + win // 2 + 1]) for i in range(len(vals))]
            _BURSTS[key] = (s, sm, _median(sm))
    s, sm, base = _BURSTS[key]
    if not sm:
        return []
    floor = max(0.008, base * 2.5)
    if max(sm) < floor:
        return []
    need = max(floor, share * max(sm))
    peaks = []
    for i in range(len(sm)):
        if sm[i] < need or (i and sm[i] < sm[i - 1]) or (i < len(sm) - 1 and sm[i] < sm[i + 1]):
            continue
        if peaks and s[i][0] - s[peaks[-1]][0] < 1.0:
            if sm[i] > sm[peaks[-1]]: peaks[-1] = i
        else:
            peaks.append(i)
    out = []
    for pk in peaks:
        thr = base + 0.3 * (sm[pk] - base)
        a = pk
        while a > 0 and sm[a - 1] > thr: a -= 1
        b = pk
        while b < len(sm) - 1 and sm[b + 1] > thr: b += 1
        out.append((s[a][0], s[pk][0], s[b][0], sm[pk]))
    return sorted(out, key=lambda x: -x[3])

def find_lift(path, fps=15, at=None):
    """The stand-pop: the strongest sustained burst of motion in a static, side-on take.
    `at` (seconds into the clip, from her note or from a reviewer who looked at the frames) picks the burst nearest
    that moment instead; with no burst within 1.5 s it trusts the number and keeps a short span around it.
    Returns (start, peak, end) of the burst in seconds, or None when the take has no clear burst."""
    if at is not None:
        near = [x for x in lift_bursts(path, fps, share=0.0) if abs(x[1] - float(at)) <= 1.5]
        if near:
            a, pk, b, _ = min(near, key=lambda x: abs(x[1] - float(at)))
            return a, pk, b
        at = float(at)
        return max(0.0, at - 0.3), at, at + 0.5
    bursts = lift_bursts(path, fps)
    return bursts[0][:3] if bursts else None

def brightness(path, fps=2):
    """Mean luma (0-255) sampled twice a second, plus 10th/90th percentile, on an 8-bit grey copy."""
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf",
             f"fps={fps},scale=160:-2,format=gray,signalstats,metadata=print", "-f", "null", "-"], check=False)
    avg = [float(x) for x in re.findall(r"signalstats\.YAVG=([\d.]+)", p.stderr)]
    low = [float(x) for x in re.findall(r"signalstats\.YLOW=([\d.]+)", p.stderr)]
    high = [float(x) for x in re.findall(r"signalstats\.YHIGH=([\d.]+)", p.stderr)]
    if not avg:
        return None
    return {"mean": round(sum(avg) / len(avg), 1), "low": round(_median(low), 1), "high": round(_median(high), 1)}


# ---------- sound analysis ----------
def loudness(path, start=None, dur=None):
    """Integrated LUFS, true peak (dBTP) and loudness range via ebur128 (optionally for one stretch)."""
    span = (["-ss", f"{start:.3f}"] if start else []) + (["-t", f"{dur:.3f}"] if dur else [])
    p = run(["ffmpeg", "-hide_banner", "-nostats", *span, "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], check=False)
    tail = p.stderr[p.stderr.rfind("Summary:"):] if "Summary:" in p.stderr else ""
    def grab(pat):
        m = re.search(pat, tail, re.S)
        return float(m.group(1)) if m else None
    return {"lufs": grab(r"I:\s+(-?[\d.]+) LUFS"), "lra": grab(r"LRA:\s+(-?[\d.]+) LU"),
            "tp": grab(r"True peak:.*?Peak:\s+(-?[\d.]+|-inf) dBFS")}

def gain_to(path, target, start=None, dur=None, most=20.0):
    """Static gain (dB) that brings a stretch to `target` LUFS. Static, not loudnorm's dynamic mode, which lifts the
    room hiss between lines; quiet stays quiet and the final two-pass loudnorm sets the overall level."""
    m = loudness(path, start, dur)["lufs"]
    return 0.0 if m is None or m < -70 else max(-most, min(most, target - m))

def level_series(path, start=None, end=None, win=0.05, pre=None):
    """RMS level (dBFS) per 50 ms window, using astats; no numpy needed. `pre` is an optional filter run first
    (e.g. a band-pass to measure only the speech band)."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start: cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", path]
    if end: cmd += ["-t", f"{end - (start or 0):.3f}"]
    n = int(16000 * win)
    p = run(cmd + ["-vn", "-af", (pre + "," if pre else "") + f"aformat=channel_layouts=mono,aresample=16000,asetnsamples=n={n}:p=0,"
                   "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level", "-f", "null", "-"], check=False)
    lv = []
    for x in re.findall(r"RMS_level=(-?[\d.]+|-inf)", p.stderr):
        lv.append(-120.0 if x == "-inf" else float(x))
    return [((start or 0) + i * win, v) for i, v in enumerate(lv)]

def _power_mean(dbs):
    dbs = [d for d in dbs if d > -110]
    return round(10 * math.log10(sum(10 ** (d / 10) for d in dbs) / len(dbs)), 1) if dbs else None

SPEECH_BAND = "highpass=f=1000,lowpass=f=4000"
def mix_balance(voice_wav, music_wav, body_end=None, talk_spans=None):
    """How the music bed sits against her voice, from the two stems the editor writes (before the master gain,
    which moves both equally). Talking windows come from `talk_spans` (the cut's caption timings) when given; an
    empty list means nobody talks, so a kid's groan or the stand's click is never mistaken for a voice. Without it,
    talking windows are 50 ms frames where the voice stem is within 20 dB of its own 95th percentile. Returns:
      speech_band_margin_db  voice minus music in the 1-4 kHz band while she talks (intelligibility; ≥15 is clear)
      gaps_under_voice_db    how far the bed sits under her talking level when she isn't talking (8-24 = audible, not loud)
      talk_share             share of the body where someone is talking
    The margin is None when nobody talks (a text-story cut): then the bed IS the sound and loudness alone judges it."""
    end = body_end
    v = [x for x in level_series(voice_wav, end=end)]
    m = [x for x in level_series(music_wav, end=end)]
    vb = level_series(voice_wav, end=end, pre=SPEECH_BAND)
    mb = level_series(music_wav, end=end, pre=SPEECH_BAND)
    n = min(len(v), len(m), len(vb), len(mb))
    if not n:
        return None
    vals = sorted(x[1] for x in v[:n])
    p95 = vals[min(n - 1, int(n * 0.95))]
    if talk_spans is not None:
        talk = [i for i in range(n) if any(a <= v[i][0] <= b for a, b in talk_spans)]
    else:
        talk = [i for i in range(n) if v[i][1] > max(p95 - 20, -50) and p95 > -45]
    quiet = [i for i in range(n) if i not in set(talk)]
    out = {"talk_share": round(len(talk) / n, 2)}
    if len(talk) >= 10:  # half a second of talking at least
        out["speech_band_margin_db"] = round(_power_mean([vb[i][1] for i in talk]) - _power_mean([mb[i][1] for i in talk]), 1)
        voice_lvl = _power_mean([v[i][1] for i in talk]); bed = _power_mean([m[i][1] for i in quiet]) if quiet else None
        out["gaps_under_voice_db"] = round(voice_lvl - bed, 1) if bed is not None else None
    else:
        out["speech_band_margin_db"] = None; out["gaps_under_voice_db"] = None
    out["music_level_db"] = _power_mean([x[1] for x in m[:n]])
    return out

_LEVELS = {}
def speech_spans(path, start=None, end=None, below_p95_db=30.0, merge_gap=0.12, min_len=0.12):
    """Where someone is talking, in source seconds: 50 ms windows above a threshold set from the WHOLE clip —
    the higher of (95th percentile - 30 dB), take-one vo.py:32-42, and 45 % of the way from the room's floor to
    the voice, so a phone take with TV hiss 25 dB under the voice still reads the hiss as silence.
    Pass start/end to get only the spans inside that window. Returns [(start, end)]."""
    if path not in _LEVELS:
        _LEVELS[path] = level_series(path)
    lv = _LEVELS[path]
    if not lv:
        return []
    vals = sorted(v for _, v in lv)
    p95 = vals[min(len(vals) - 1, int(len(vals) * 0.95))]
    floor = vals[int(len(vals) * 0.10)]
    if p95 - floor < 12:          # no contrast between voice and room: treat as no speech
        return []
    thr = max(p95 - below_p95_db, floor + 0.45 * (p95 - floor))
    lo, hi = (start or 0.0), (end if end is not None else lv[-1][0] + 1)
    spans = []
    for t, v in lv:
        if t < lo or t > hi or v <= thr:
            continue
        if spans and t - spans[-1][1] <= merge_gap:
            spans[-1][1] = t + 0.05
        else:
            spans.append([t, t + 0.05])
    return [(round(a, 3), round(min(b, hi), 3)) for a, b in spans if b - a >= min_len]


# ---------- fonts and text ----------
def font_path(weight=800):
    for f in (f"Poppins-{weight}.woff", "Poppins-800.woff", "Poppins-700.woff"):
        p = os.path.join(FONT_DIR, f)
        if os.path.exists(p):
            return p
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(p):
            return p
    raise SystemExit("no font found: keep skills/digiroo-video/fonts/ next to scripts/")

_EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]")
def burnable(text):
    """Burned-in text uses Poppins, which has no emoji. Emoji stay in the post caption, not the picture."""
    return re.sub(r"[ \t]{2,}", " ", _EMOJI.sub("", text or "")).strip()

def wrap(text, font, max_w):
    """Greedy word wrap; a "\n" in the text forces a line break."""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            trial = (cur + " " + w).strip()
            if font.getlength(trial) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
    return lines

# Brand colours, sampled from the DigiRoo box and logo (2026-11-04): the letters of "DigiRoo" use all five.
BRAND = {"orange": (238, 106, 47), "yellow": (246, 194, 62), "green": (125, 187, 66), "teal": (47, 163, 160),
         "indigo": (52, 53, 143), "ink": (22, 22, 28), "white": (255, 255, 255)}
TIKTOK_FONT = os.path.join(FONT_DIR, "TikTokSans-VF.ttf")

def get_font(weight=800, size=60, family="poppins"):
    """family "tiktok" = TikTok Sans (SIL OFL 1.1, the platform's own UI font, variable weight 300-900): on-screen text
    then looks native, the way the niche's top videos do. Falls back to Poppins when the file isn't there."""
    from PIL import ImageFont
    if family == "tiktok" and os.path.exists(TIKTOK_FONT):
        f = ImageFont.truetype(TIKTOK_FONT, size)
        try:
            f.set_variation_by_axes([36, 100, max(300, min(900, weight)), 0])  # optical size, width, weight, slant
        except Exception:
            pass
        return f
    return ImageFont.truetype(font_path(weight if weight >= 700 else 700), size)

def _rgb(c):
    return BRAND.get(c, c) if isinstance(c, str) else tuple(c)

def text_block(text, size, max_w, weight=800, stroke=None, shadow=True, line_gap=0.12, family="poppins", style="outline",
               fill="white", box="white", highlight=None, upper=False):
    """One block of centred text. Returns an RGBA image cropped to the text plus its shadow, and the line count.
    style "outline": white text, dark outline, drop shadow (the original DigiRoo look).
          "soft":    white text, thin outline, soft shadow (TikTok's default text; captions).
          "box":     text on a rounded box per line, the TikTok "background" text style (hooks, labels, callouts).
    highlight=(word index, box colour, text colour): that word sits on its own small box (the spoken word, karaoke-style)."""
    from PIL import Image, ImageDraw, ImageFilter
    if upper:
        text = text.upper()
    fill, box = _rgb(fill), _rgb(box)
    font = get_font(weight, size, family)
    lines = wrap(text, font, max_w)
    asc, desc = font.getmetrics(); lh = asc + desc
    if style == "outline":
        stroke = stroke if stroke is not None else max(3, size // 14)
    elif style == "soft":
        stroke = stroke if stroke is not None else max(2, size // 26)
    else:
        stroke = 0
    padx, pady = (int(size * 0.42), int(size * 0.14)) if style == "box" else (0, 0)
    gap = int(size * line_gap) if style != "box" else -int(size * 0.06)  # box lines touch, like TikTok's
    widths = [font.getlength(l) for l in lines]
    hp = int(size * 0.16) if highlight else 0
    tw = int(max(widths)) + 2 * stroke + 2 * padx + 2 * hp
    row_h = lh + 2 * pady
    th = row_h * len(lines) + gap * (len(lines) - 1) + 2 * stroke
    pad = 24
    img = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = pad + stroke; wi = 0; space = font.getlength(" ")
    for l, w in zip(lines, widths):
        x0 = pad + (tw - (w + 2 * padx)) / 2
        if style == "box":
            d.rounded_rectangle([x0, y, x0 + w + 2 * padx, y + row_h], int(size * 0.3), fill=box + (255,))
        tx = x0 + padx
        for wd in l.split(" "):
            ww = font.getlength(wd)
            if highlight and wi == highlight[0]:
                tx += hp  # the box gets its own room; it never eats the space before or after the word
                d.rounded_rectangle([tx - hp, y + pady + int(lh * 0.04), tx + ww + hp, y + pady + lh - int(lh * 0.04)],
                                    int(size * 0.22), fill=_rgb(highlight[1]) + (255,))
                d.text((tx, y + pady), wd, font=font, fill=_rgb(highlight[2]) + (255,))
                tx += hp
            else:
                d.text((tx, y + pady), wd, font=font, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            tx += ww + space; wi += 1
        y += row_h + gap
    if shadow:
        a, blur = {"outline": (0.55, max(4, size // 12)), "soft": (0.6, max(5, size // 9)), "box": (0.22, max(6, size // 7))}[style]
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(img.split()[3].point(lambda v: int(v * a)))
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
        base = Image.new("RGBA", img.size, (0, 0, 0, 0))
        base.alpha_composite(sh, (0, max(2, size // 20)))
        base.alpha_composite(img)
        img = base
    return img, len(lines)

def wordmark(size=110):
    """"DigiRoo" in the logo's letter colours (D orange, i yellow, g green, i teal, R indigo, oo orange) on a white pill.
    Drawn, not copied: the brand's own name in its own colours."""
    from PIL import Image, ImageDraw
    font = get_font(900, size, "tiktok")
    cols = ["orange", "yellow", "green", "teal", "indigo", "orange", "orange"]
    word = "DigiRoo"; w = sum(font.getlength(c) for c in word); asc, desc = font.getmetrics()
    padx, pady = int(size * 0.45), int(size * 0.2)
    img = Image.new("RGBA", (int(w) + 2 * padx, asc + desc + 2 * pady), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], int(img.height / 2), fill=(255, 255, 255, 255))
    x = padx
    for ch, c in zip(word, cols):
        d.text((x, pady), ch, font=font, fill=BRAND[c] + (255,)); x += font.getlength(ch)
    return img

def draw_arrow(canvas, start, end, colour="yellow", width=12, alpha=1.0):
    """A plain arrow from a callout box to the thing it names (the red lines on the 18.5M neck video do this job)."""
    from PIL import Image, ImageDraw
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    (x0, y0), (x1, y1) = start, end
    ang = math.atan2(y1 - y0, x1 - x0); head = width * 3.2
    bx, by = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
    pts = [(x1, y1), (bx - head * 0.6 * math.sin(ang), by + head * 0.6 * math.cos(ang)),
           (bx + head * 0.6 * math.sin(ang), by - head * 0.6 * math.cos(ang))]
    for wdt, col in ((width + 6, (0, 0, 0, 150)), (width, _rgb(colour) + (255,))):
        d.line([(x0, y0), (bx, by)], fill=col, width=wdt)
    d.polygon(pts, fill=_rgb(colour) + (255,), outline=(0, 0, 0, 150))
    if alpha < 1:
        layer.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    canvas.alpha_composite(layer)

SFX = {  # synthesised, so there's nothing to license: short, soft, under the voice
    "pop":    "aevalsrc='0.6*sin(2*PI*(380+2600*t)*t)*exp(-38*t)':s=48000:d=0.18",
    "whoosh": "anoisesrc=color=pink:amplitude=0.5:d=0.45:r=48000,bandpass=f=1400:width_type=o:w=1.6,afade=t=in:d=0.28,afade=t=out:st=0.28:d=0.17",
    "ding":   "aevalsrc='0.45*sin(2*PI*1568*t)*exp(-5*t)+0.2*sin(2*PI*3136*t)*exp(-8*t)':s=48000:d=0.9",
    "tick":   "aevalsrc='0.5*sin(2*PI*2200*t)*exp(-90*t)':s=48000:d=0.06",
}
def make_sfx(name, out):
    if name not in SFX:
        raise SystemExit(f"unknown built-in sound '{name}': use one of {', '.join(SFX)}")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", SFX[name], "-ac", "2", "-c:a", "pcm_s16le", out])
    return out


# ---------- frames and sheets ----------
def grab(path, t, out, width=None):
    vf = ["-vf", f"scale={width}:-2"] if width else []
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{max(t, 0):.3f}", "-i", path,
         "-frames:v", "1"] + vf + ["-q:v", "3", out], check=False)
    return out if os.path.exists(out) else None

def contact_sheet(path, out, n=24, cols=6, width=270, label=True):
    """n evenly spaced frames in a grid with timestamps, from the exported file itself (take-one vertical.md:32)."""
    from PIL import Image, ImageDraw, ImageFont
    dur = duration(path); tmp = out + ".d"; os.makedirs(tmp, exist_ok=True)
    tiles = []
    for i in range(n):
        t = dur * (i + 0.5) / n
        f = grab(path, t, os.path.join(tmp, f"{i:02d}.jpg"), width)
        if f: tiles.append((t, Image.open(f).convert("RGB")))
    if not tiles:
        return None
    tw, th = tiles[0][1].size; rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 4, rows * th + (rows + 1) * 4), (24, 24, 24))
    font = ImageFont.truetype(font_path(700), max(14, width // 12))
    for i, (t, im) in enumerate(tiles):
        x = 4 + (i % cols) * (tw + 4); y = 4 + (i // cols) * (th + 4)
        sheet.paste(im, (x, y))
        if label:
            ImageDraw.Draw(sheet).text((x + 6, y + 4), f"{t:.1f}s", font=font, fill=(255, 230, 0), stroke_width=2, stroke_fill=(0, 0, 0))
    sheet.save(out, quality=88)
    for f in os.listdir(tmp): os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    return out

def safe_zone_preview(frame_path, out):
    """Draw where TikTok/Reels UI sits over a frame, so text placement can be checked by eye."""
    from PIL import Image, ImageDraw
    im = Image.open(frame_path).convert("RGBA").resize((W, H))
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    red = (255, 40, 40, 90)
    d.rectangle([0, 0, W, SAFE["y0"]], fill=red)                       # top tabs + feed-preview crop
    d.rectangle([0, SAFE["y1"], W, H], fill=red)                       # caption, handle, sound row
    d.rectangle([SAFE["rail_x"], SAFE["rail_y"], W, SAFE["y1"]], fill=red)  # like/comment/share rail
    d.rectangle([0, SAFE["y0"], SAFE["x0"], SAFE["y1"]], fill=red)
    im.alpha_composite(ov); im.convert("RGB").save(out, quality=88)
    return out
