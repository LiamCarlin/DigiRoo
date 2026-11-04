#!/usr/bin/env python3
"""
trends.py — the weekly trend check: what is working in the niche right now, measured, and what to change.

    python3 trends.py research/trends/2026-11-04                                  # a pull from tools/tiktok_public_pull.py
    python3 trends.py research/trends/2026-11-04 --own research/own-posts.csv --out trends.md
    python3 trends.py saved-reels/                                                # any folder of reels she saved

Reads <folder>/videos.csv when it's there (plays, saves, shares, sound, date, hashtags; the mp4 in its `file`
column). Otherwise it measures every video file in the folder, with no stats.
Each video gets the same beat table as `qc.py --reference`: length, cuts, shot lengths, when the biggest move
lands, loudness. Breakouts are the top third by plays against their own account's median, so a small
account's outlier counts as much as a big account's. Writes:
  trends.md               the note: breakouts vs. the rest vs. our rules vs. her own posts, sounds and hashtags
                          used by 2+ accounts, caption openers, and this week's targets
  <folder>/trends.json    the same targets, for edit.json (length_target, lift before) and content-week
  <folder>/hooks.jpg      frame one and 1.5 s of every breakout, for the eye check (title? problem first? who?)
Rules beat trends: targets are clipped to video-rules.md, and a trend that breaks a rule is reported, not adopted.
--own takes her own numbers (research/own-posts.csv from weekly-review, or research/baseline-tiktok/posts.csv):
columns seconds and views, optionally avg_watch (seconds) and date.
"""
import argparse, csv, datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dvlib as L
import qc

RULE_LEN = (10, 30)          # video-rules rule 5 (product and how-to)
RULE_CUTS = 3                # rule 3
LIFT_BEFORE = (2.5, 4.5)     # enough slouch to read the title, never so much they scroll
VIDEO_EXT = (".mp4", ".mov", ".m4v")
OPENERS = [("replying to a comment", r"^(replying to|reply to|answering)\b|@\w+.*\?$"), ("pov", r"^pov\b"),
           ("how to", r"\bhow (to|i)\b"), ("question", r"\?"), ("number", r"^\d+|\b\d+ (ways|things|signs|tips|mistakes)\b"),
           ("stop / don't", r"^(stop|don'?t|never)\b"), ("parent voice", r"\b(mom|mum|dad|parent|toddler|my (son|daughter|kid))\b")]


def num(v):
    try: return float(str(v).replace(",", ""))
    except (TypeError, ValueError): return None

def med(xs):
    xs = [x for x in xs if x is not None]
    return round(L._median(xs), 1) if xs else None

def quart(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    i = (len(xs) - 1) * q; lo = int(i); hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)

def pct(n, d):
    return f"{round(100 * n / d)}%" if d else "—"

def show(path):
    r = os.path.relpath(path)
    return os.path.abspath(path) if r.startswith("..") else r

def resolve(path, folder):
    for p in (path, os.path.join(folder, path), os.path.join(folder, os.path.basename(path))):
        if p and os.path.isfile(p): return p
    return None

def load(folder):
    csv_path = os.path.join(folder, "videos.csv")
    if os.path.exists(csv_path):
        rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
        for r in rows:
            r["plays"] = num(r.get("views")) or num(r.get("plays_embed"))
            r["path"] = resolve(r.get("file") or "", folder)
        return rows, True
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(VIDEO_EXT))
    return [{"handle": "", "id": os.path.splitext(f)[0], "plays": None, "path": os.path.join(folder, f)} for f in files], False

def opener(caption):
    first = re.split(r"(?<=[.!?])\s|#", (caption or "").strip(), maxsplit=1)[0].strip().lower()
    for name, rx in OPENERS:
        if re.search(rx, first): return name
    return "statement"

def is_original(r):
    s = (r.get("sound") or "").lower()
    return str(r.get("sound_original")).lower() == "true" or s.startswith("original sound") or s in ("", "original")

def own_posts(path):
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        s, v = num(r.get("seconds")), num(r.get("views"))
        if s and v is not None:
            w = num(r.get("avg_watch")) or num(r.get("avg_watch_s"))
            rows.append({"seconds": s, "views": v, "watch": (w / s) if w else None, "date": r.get("date", "")})
    bands = [("≤15 s", 0, 15), ("16–30 s", 15, 30), ("31–45 s", 30, 45), ("46 s +", 45, 10 ** 6)]
    out = []
    for name, lo, hi in bands:
        b = [r for r in rows if lo < r["seconds"] <= hi]
        out.append({"band": name, "lo": max(lo, 1), "hi": hi, "posts": len(b), "views": med([r["views"] for r in b]),
                    "watch": med([100 * r["watch"] for r in b if r["watch"]])})
    return rows, out

def hooks_sheet(rows, out, width=216):
    from PIL import Image, ImageDraw, ImageFont
    cols = []
    for r in rows[:12]:
        tiles = []
        for i, t in enumerate((0.2, 1.5)):
            f = L.grab(r["path"], t, out + f".{r['id']}.{i}.jpg", width)
            if f: tiles.append(Image.open(f).convert("RGB")); os.remove(f)
        if tiles: cols.append((r, tiles))
    if not cols: return None
    tw, th = cols[0][1][0].size; lab = 34
    im = Image.new("RGB", (len(cols) * (tw + 4) + 4, lab + 2 * (th + 4) + 4), (24, 24, 24))
    d = ImageDraw.Draw(im); font = ImageFont.truetype(L.font_path(700), 15)
    for c, (r, tiles) in enumerate(cols):
        x = 4 + c * (tw + 4)
        name = ("@" + r["handle"]) if r.get("handle") else r["id"][:18]
        d.text((x + 2, 4), name[:22], font=font, fill=(255, 230, 0))
        d.text((x + 2, 19), (f"×{r['ratio']:.1f} · " if r.get("ratio") else "") + f"{r['beats']['duration']:.0f}s", font=font, fill=(220, 220, 220))
        for i, tile in enumerate(tiles):
            im.paste(tile, (x, lab + i * (th + 4)))
    im.save(out, quality=86); return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder"); ap.add_argument("--own", help="her own posts CSV (seconds, views, optional avg_watch, date)")
    ap.add_argument("--days", type=int, default=21, help="count videos posted in the last N days as this week's sample")
    ap.add_argument("--out", default="trends.md"); ap.add_argument("--today", help="YYYY-MM-DD (default: today)")
    a = ap.parse_args()
    today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
    rows, has_stats = load(a.folder)
    if not rows: raise SystemExit(f"no videos.csv and no video files in {a.folder}")

    # the window: this month's videos when there are enough measured ones, else everything (and say so)
    since = (today - datetime.timedelta(days=a.days)).isoformat()
    dated = [r for r in rows if r.get("date")]
    recent = [r for r in dated if r["date"] >= since]
    if dated and len([r for r in recent if r.get("path")]) >= 6:
        pool, window = recent, f"posted since {since} ({a.days} days)"
    else:
        pool = rows
        window = (f"all dates (only {len([r for r in recent if r.get('path')])} measured videos since {since}, fewer than 6)"
                  if dated else "no dates in the sample")
    stats_pool = [r for r in pool if r.get("date")] or pool
    measured_pool = [r for r in pool if r.get("path")]

    # breakout ratio: plays against the account's own median within the window
    by_handle = {}
    for r in pool:
        if r.get("plays") is not None: by_handle.setdefault(r.get("handle", ""), []).append(r["plays"])
    for r in pool:
        base = L._median(by_handle[r.get("handle", "")]) if by_handle.get(r.get("handle", "")) else None
        r["ratio"] = (r["plays"] / base) if r.get("plays") is not None and base else None

    for r in measured_pool:
        try:
            r["beats"] = qc.beats(r["path"]); b = r["beats"]
            b["first_cut"] = b["cuts"][0] if b["cuts"] else None
            print(f"measured {r.get('handle') or ''} {r['id']}: {b['duration']:.1f}s, {len(b['cuts'])} cuts, move at {b['biggest_move']}", flush=True)
        except (SystemExit, Exception) as e:
            print(f"skipped {r['path']}: {e}", file=sys.stderr)
    measured = [r for r in measured_pool if r.get("beats")]
    if not measured: raise SystemExit("no video could be measured")

    ranked = sorted(measured, key=lambda r: -(r.get("ratio") or 0))
    if any(r.get("ratio") for r in measured):
        k = max(1, round(len(ranked) / 3)); breakouts, rest = ranked[:k], ranked[k:]
    else:
        breakouts, rest = measured, []

    def summary(group):
        if not group: return None
        bs = [r["beats"] for r in group]
        moves = [b["biggest_move"] for b in bs if b["biggest_move"] is not None and b["biggest_move"] <= 10]
        views = [r for r in group if num(r.get("views"))]
        return {"n": len(group), "length": med([b["duration"] for b in bs]),
                "length_mid": [round(quart([b["duration"] for b in bs], .25)), round(quart([b["duration"] for b in bs], .75))],
                "cuts": med([len(b["cuts"]) for b in bs]), "zero_cut": pct(sum(1 for b in bs if not b["cuts"]), len(bs)),
                "first_cut": med([b["first_cut"] for b in bs]), "move": med(moves), "move_n": len(moves),
                "lufs": med([b["loudness"]["lufs"] for b in bs if b["loudness"]["lufs"] is not None and b["loudness"]["lufs"] > -60]),
                "original": pct(sum(1 for r in group if is_original(r)), len(group)) if has_stats else "—",
                "saves": pct(sum(num(r.get("saves")) or 0 for r in views), sum(num(r["views"]) for r in views)) if views else "—",
                "shares": pct(sum(num(r.get("shares")) or 0 for r in views), sum(num(r["views"]) for r in views)) if views else "—"}
    top, others = summary(breakouts), summary(rest)
    ranked_by_plays = any(r.get("ratio") for r in measured)
    B = "breakouts" if ranked_by_plays else "saved reels"

    # sounds and hashtags that 2+ accounts used in the window
    def shared(split):
        seen = {}
        for r in stats_pool:
            for v in split(r):
                if v: seen.setdefault(v, set()).add(r.get("handle", ""))
        return sorted(((v, len(h)) for v, h in seen.items() if len(h) >= 2), key=lambda x: -x[1])
    sounds = shared(lambda r: [] if is_original(r) else [(r.get("sound") or "").strip()])
    tags = shared(lambda r: sorted(set(t.lower() for t in re.findall(r"#\w+", r.get("hashtags") or r.get("caption") or r.get("desc") or ""))))
    open_b = {}
    for grp, label in ((breakouts, "b"), (rest, "r")):
        for r in grp:
            if r.get("caption") or r.get("desc"):
                o = opener(r.get("caption") or r.get("desc")); open_b.setdefault(o, {"b": 0, "r": 0})[label] += 1

    # her own posts, by length band
    own_rows, bands = own_posts(a.own) if a.own else ([], [])
    own_med = med([r["views"] for r in own_rows])
    best = None
    for b in bands:
        if b["posts"] >= 3 and b["views"] and own_med and b["views"] >= 1.25 * own_med and (not best or b["views"] > best["views"]):
            best = b

    # targets: start from the rule, narrow by her own best band (her viewers first), then by the niche; never leave the rule
    target, why = list(RULE_LEN), [f"rule 5: {RULE_LEN[0]}–{RULE_LEN[1]} s"]
    cands = []
    if best: cands.append((f"her own best length ({best['band']}, median {best['views']:.0f} views vs {own_med:.0f} overall)", best["lo"], min(best["hi"], 60)))
    if top and len(breakouts) >= 3:
        lo, hi = top["length_mid"]; cands.append((f"{'niche breakouts' if ranked_by_plays else 'the saved reels'}' middle half ({lo}–{hi} s)", lo, hi))
    for name, lo, hi in cands:
        n_lo, n_hi = max(target[0], lo), min(target[1], hi)
        if n_hi - n_lo >= 4: target = [round(n_lo), round(n_hi)]; why.append(name)
        else: why.append(f"{name} barely overlaps {target[0]}–{target[1]} s, so not adopted")
    lift_before, lift_why = 3.5, "fewer than 3 breakouts have a big move in their first 10 s, so the default stands"
    if top and top["move"] is not None and top["move_n"] >= 3:
        lift_before = round(min(max(top["move"], LIFT_BEFORE[0]), LIFT_BEFORE[1]), 1)
        lift_why = f"{top['move_n']} breakouts' biggest move lands at a median {top['move']} s; kept within {LIFT_BEFORE[0]}–{LIFT_BEFORE[1]} s so the title can be read"

    folder_rel = show(a.folder)
    hooks = hooks_sheet(breakouts, os.path.join(a.folder, "hooks.jpg"))
    valid = (today + datetime.timedelta(days=7)).isoformat()
    accounts = sorted(set(r.get("handle") for r in rows if r.get("handle")))
    targets = {"checked": today.isoformat(), "valid_until": valid, "source": folder_rel, "window": window,
               "length_target": target, "length_why": why, "lift_before": lift_before, "lift_why": lift_why,
               "breakouts": [{"handle": r.get("handle"), "id": r["id"], "ratio": round(r["ratio"], 1) if r.get("ratio") else None,
                              "url": r.get("url"), **{k: r["beats"][k] for k in ("duration", "cuts", "biggest_move")}} for r in breakouts],
               "shared_sounds": sounds[:8], "shared_hashtags": tags[:12], "summary": {"breakouts": top, "rest": others}}
    json.dump(targets, open(os.path.join(a.folder, "trends.json"), "w"), indent=2, ensure_ascii=False)

    def cell(s, k): return "—" if not s or s.get(k) is None else s[k]
    md = [f"# Trends — checked {today.isoformat()}, good until {valid}",
          "",
          f"`digiroo-video` and `content-week` read this before shoot cards and cuts. Order of authority: the video rules, then her notes in `video-notes.md`, then this note. "
          f"After {valid} it's stale: say so and run the check again (`trends.py`, see the skill's Trends move).",
          "",
          f"**Sample:** {len(rows)} videos listed from {len(accounts) or 'saved'} {'accounts' if accounts else 'reels'} · {len(measured)} measured · window: {window} · "
          + ("breakouts = top third by plays against their own account's median" if ranked_by_plays else "no play counts, so every reel counts as a reference"),
          f"**Source:** `{folder_rel}` · frames: `{show(hooks) if hooks else 'none'}`",
          "",
          f"## What the {B} did",
          f"| | {B} | the rest | our rule |",
          "|---|---|---|---|",
          f"| videos | {cell(top, 'n')} | {cell(others, 'n')} | |",
          f"| length (median) | {cell(top, 'length')} s | {cell(others, 'length')} s | {RULE_LEN[0]}–{RULE_LEN[1]} s |",
          f"| length (middle half) | {'–'.join(map(str, top['length_mid'])) if top else '—'} s | {'–'.join(map(str, others['length_mid'])) if others else '—'} s | |",
          f"| cuts (median) | {cell(top, 'cuts')} | {cell(others, 'cuts')} | ≤{RULE_CUTS} |",
          f"| zero-cut videos | {cell(top, 'zero_cut')} | {cell(others, 'zero_cut')} | the one-take |",
          f"| first cut at | {cell(top, 'first_cut')} s | {cell(others, 'first_cut')} s | |",
          f"| biggest move at (first 10 s) | {cell(top, 'move')} s (n={cell(top, 'move_n')}) | {cell(others, 'move')} s (n={cell(others, 'move_n')}) | the pop at ~3.5 s |",
          f"| loudness | {cell(top, 'lufs')} LUFS | {cell(others, 'lufs')} LUFS | -14 LUFS (the apps even playback out; ours stays put) |",
          f"| original sound | {cell(top, 'original')} | {cell(others, 'original')} | original for how-to (rule 9) |",
          f"| saves / views | {cell(top, 'saves')} | {cell(others, 'saves')} | |",
          f"| shares / views | {cell(top, 'shares')} | {cell(others, 'shares')} | |",
          "",
          f"## The {B}"]
    md += ["| account | × own median | plays | length | cuts | move at | sound | caption opens |", "|---|---|---|---|---|---|---|---|"]
    for r in breakouts:
        b = r["beats"]
        md.append(f"| {('@' + r['handle']) if r.get('handle') else r['id']} | {('×%.1f' % r['ratio']) if r.get('ratio') else '—'} | "
                  f"{int(r['plays']) if r.get('plays') else '—'} | {b['duration']:.0f} s | {len(b['cuts'])} | {b['biggest_move'] if b['biggest_move'] is not None else '—'} | "
                  f"{'original' if is_original(r) else (r.get('sound') or '—')[:30]} | {(r.get('caption') or r.get('desc') or '')[:60].replace('|', '/')} |")
    md += ["", "## Sounds used by 2+ accounts"]
    md += [f"- {s} ({n} accounts). Business accounts can only use it if it's in the Commercial Music Library: search it in-app at post time; if it isn't there, keep original sound." for s, n in sounds[:8]] or ["- none shared this week (everyone's on their own or original sound)"]
    md += ["", "## Hashtags used by 2+ accounts"]
    md += [" ".join(f"{t} ({n})" for t, n in tags[:12])] if tags else ["- none shared this week"]
    if open_b:
        md += ["", "## How the captions open", "| opener | breakouts | the rest |", "|---|---|---|"]
        md += [f"| {o} | {c['b']} | {c['r']} |" for o, c in sorted(open_b.items(), key=lambda x: -x[1]["b"])]
    if bands:
        md += ["", f"## Her own posts by length ({len(own_rows)} posts, median {own_med:.0f} views)",
               "| length | posts | median views | median watch-through |", "|---|---|---|---|"]
        md += [f"| {b['band']} | {b['posts']} | {b['views'] if b['views'] is not None else '—'} | {str(b['watch']) + '%' if b['watch'] is not None else '—'} |" for b in bands]
    md += ["", "## This week's targets (copy into edit.json and the post cards)",
           f"- **Length:** {target[0]}–{target[1]} s → `\"length_target\": [{target[0]}, {target[1]}]` in edit.json. Why: " + "; ".join(why) + ".",
           f"- **Slouch before the pop:** {lift_before} s → `\"lift\": {{\"before\": {lift_before}}}`. Why: {lift_why}.",
           f"- **Cuts:** {B} median {cell(top, 'cuts')}; ours stay ≤{RULE_CUTS}, one take where we can.",
           "- **Sound:** " + (f"{sounds[0][0]} is shared by {sounds[0][1]} accounts; only for a text-narrated transformation, only from the Commercial Music Library, added in-app." if sounds else "original sound; nothing shared enough to chase."),
           "",
           f"## Eye check (Claude, from {show(hooks) if hooks else 'the frames'}; fill in, then keep or drop)",
           "- Title in frame one? Problem before product? Who is on screen at 0 s? One line on the best hook and how DigiRoo would borrow its shape:",
           "- Anything here that breaks a video rule (and so isn't adopted):",
           ""]
    open(a.out, "w", encoding="utf-8").write("\n".join(md))
    print(f"wrote {show(a.out)}, {os.path.join(folder_rel, 'trends.json')}" + (f", {show(hooks)}" if hooks else ""))
    print(f"length target {target[0]}–{target[1]} s · lift before {lift_before} s · {len(breakouts)} {B} of {len(measured)} measured")

if __name__ == "__main__":
    main()
