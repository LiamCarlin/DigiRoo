#!/usr/bin/env python3
"""
ingest_videos.py — build teardown material for the format library.

    python3 tools/ingest_videos.py --urls urls.txt --out research/teardowns
    python3 tools/ingest_videos.py --files media/raw/ugc/*.mp4 --out research/teardowns
    python3 tools/ingest_videos.py --urls urls.txt --out research/teardowns --no-whisper

For each video:
  1. download with yt-dlp (public TikTok / Instagram / YouTube Shorts) + metadata (views, likes, date, caption, hashtags)
     — or take local files (Drive clips)
  2. transcript with faster-whisper (optional)
  3. scene cuts with ffmpeg scenedetect + frame grabs at 0 s / 1.5 s / 3 s and at each cut
  4. write <out>/<id>/meta.json, transcript.txt, cuts.txt, frames/*.jpg and a teardown.md stub
     (hook type, beat map, shot list, why it works, how DigiRoo would use it) for Claude to fill in.

Note: TikTok/Instagram downloads are blocked from the Claude cloud sandbox. Run this on a laptop,
or paste a screen recording / the saved reel's mp4 into --files instead.
"""
import argparse, json, os, re, subprocess, sys, shutil

def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.stderr.write(p.stderr[-2000:] + "\n"); raise SystemExit(1)
    return p

def download(url, out):
    os.makedirs(out, exist_ok=True)
    p = run(["yt-dlp", "--no-playlist", "-o", os.path.join(out, "%(id)s.%(ext)s"), "--write-info-json", "-f", "mp4/best", url], check=False)
    if p.returncode != 0:
        sys.stderr.write(f"download failed for {url}: {p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ''}\n"); return None
    vids = [f for f in os.listdir(out) if f.endswith(".mp4")]
    infos = [f for f in os.listdir(out) if f.endswith(".info.json")]
    meta = {}
    if infos:
        d = json.load(open(os.path.join(out, infos[0])))
        meta = {k: d.get(k) for k in ("id", "title", "description", "uploader", "view_count", "like_count", "comment_count", "repost_count", "upload_date", "duration", "webpage_url")}
        meta["hashtags"] = re.findall(r"#\w+", d.get("description") or "")
    return (os.path.join(out, vids[0]) if vids else None), meta

def transcript(path):
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel("base", device="cpu", compute_type="int8")
        segs, _ = m.transcribe(path, language="en")
        return "\n".join(f"[{s.start:05.1f}] {s.text.strip()}" for s in segs)
    except Exception as e:
        return f"(no transcript: {e.__class__.__name__})"

def scene_cuts(path, thresh=0.3):
    p = run(["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{thresh})',showinfo", "-f", "null", "-"], check=False)
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", p.stderr)]

def frames(path, out, times):
    os.makedirs(out, exist_ok=True)
    for t in times:
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", "scale=360:-1", os.path.join(out, f"t{t:05.1f}.jpg")], check=False)

STUB = """# Teardown — {id}

**Source:** {url} · **Views:** {views} · **Likes:** {likes} · **Posted:** {date} · **Length:** {dur}s
**Caption:** {caption}
**Hashtags:** {tags}

## Hook type (first 3 s)
(problem callout · POV · result-first · credential · demo cold-open · pattern interrupt · …) — and the exact first line

## Beat map
| t | beat | what happens on screen | spoken |
|---|---|---|---|
{beats}

## Shot list
(framing, camera motion, location per beat)

## On-screen text pattern
## Audio bed
## Why it works (3 mechanisms)
## How DigiRoo would use it
## Do-not-copy
creator's face/name/catchphrase/licensed audio
"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--urls"); ap.add_argument("--files", nargs="*"); ap.add_argument("--out", default="research/teardowns"); ap.add_argument("--no-whisper", action="store_true")
    a = ap.parse_args(); items = []
    if a.urls:
        items += [("url", u.strip()) for u in open(a.urls) if u.strip() and not u.startswith("#")]
    if a.files:
        items += [("file", f) for f in a.files]
    if not items: ap.error("give --urls file or --files ...")
    for kind, src in items:
        vid_id = re.sub(r"[^A-Za-z0-9]+", "-", os.path.splitext(os.path.basename(src))[0])[:40] if kind == "file" else re.sub(r"[^A-Za-z0-9]+", "-", src.split("?")[0].rstrip("/").split("/")[-1])[:40]
        d = os.path.join(a.out, vid_id); os.makedirs(d, exist_ok=True)
        if kind == "url":
            res = download(src, d)
            if not res or not res[0]: continue
            path, meta = res
        else:
            path = os.path.join(d, os.path.basename(src)); shutil.copy(src, path); meta = {"webpage_url": src}
        meta["duration"] = meta.get("duration") or float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path]).stdout.strip() or 0)
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=2)
        tr = "(skipped)" if a.no_whisper else transcript(path); open(os.path.join(d, "transcript.txt"), "w").write(tr)
        cuts = scene_cuts(path); open(os.path.join(d, "cuts.txt"), "w").write("\n".join(f"{c:.2f}" for c in cuts))
        frames(path, os.path.join(d, "frames"), sorted(set([0, 1.5, 3] + [round(c, 1) for c in cuts[:10]])))
        beats = "\n".join(f"| {c:.1f} | | | |" for c in [0.0] + cuts[:8])
        open(os.path.join(d, "teardown.md"), "w").write(STUB.format(id=vid_id, url=meta.get("webpage_url", src), views=meta.get("view_count", "?"), likes=meta.get("like_count", "?"),
            date=meta.get("upload_date", "?"), dur=round(float(meta.get("duration") or 0), 1), caption=(meta.get("description") or "")[:200], tags=" ".join(meta.get("hashtags", [])), beats=beats))
        print(f"{vid_id}: {len(cuts)} cuts, {round(float(meta.get('duration') or 0),1)}s → {d}")

if __name__ == "__main__":
    main()
