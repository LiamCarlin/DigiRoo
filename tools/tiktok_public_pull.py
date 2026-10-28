#!/usr/bin/env python3
"""
tiktok_public_pull.py — study what works in a niche using only TikTok's public pages.

    python3 tools/tiktok_public_pull.py --handles kidsonlychiropractic pedsdoctalk --out research/segment --download 3

For each handle: the public profile page (follower/video counts) and the public profile
embed (/embed/@handle: the 10 most recent videos with play counts and direct video URLs).
Then, for the top N by plays, the public video page (likes, comments, shares, saves,
duration, sound, hashtags), the mp4, a 6-frame contact sheet, and a teardown stub.
Plain curl, no login, no spoofing, 2 s between requests. Public data only.
"""
import argparse, csv, json, os, re, subprocess, sys, time, datetime

UA_NOTE = "plain curl default"
def get(url, out):
    r = subprocess.run(["curl", "-g", "-sS", "-L", "--max-time", "40", "-o", out, "-w", "%{http_code}", url], capture_output=True, text=True)
    time.sleep(2)
    return r.stdout.strip()

def json_blobs(html):
    out = []
    for b in re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.S):
        try: out.append(json.loads(b))
        except Exception: pass
    return out

def rehydration(html):
    m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1)).get("__DEFAULT_SCOPE__", {}) if m else {}

def walk(o, pred, acc):
    if isinstance(o, dict):
        if pred(o): acc.append(o)
        for v in o.values(): walk(v, pred, acc)
    elif isinstance(o, list):
        for v in o: walk(v, pred, acc)
    return acc

def profile(handle, tmp):
    code = get(f"https://www.tiktok.com/@{handle}", f"{tmp}/{handle}.profile.html")
    if code != "200": return {}
    d = rehydration(open(f"{tmp}/{handle}.profile.html", encoding="utf-8", errors="ignore").read())
    u = d.get("webapp.user-detail", {}).get("userInfo", {})
    return {"handle": handle, "nickname": u.get("user", {}).get("nickname"), "bio": u.get("user", {}).get("signature"), **{k: u.get("stats", {}).get(k) for k in ("followerCount", "heartCount", "videoCount")}}

def embed_items(handle, tmp):
    code = get(f"https://www.tiktok.com/embed/@{handle}", f"{tmp}/{handle}.embed.html")
    if code != "200": return []
    items = []
    for b in json_blobs(open(f"{tmp}/{handle}.embed.html", encoding="utf-8", errors="ignore").read()):
        walk(b, lambda o: "playAddr" in o and "id" in o, items)
    seen, out = set(), []
    for i in items:
        if i["id"] in seen: continue
        seen.add(i["id"]); out.append({"id": i["id"], "desc": i.get("desc"), "play": i.get("playCount"), "playAddr": i.get("playAddr"), "cover": i.get("coverUrl") or i.get("originCoverUrl")})
    return out

def video_stats(handle, vid, tmp):
    code = get(f"https://www.tiktok.com/@{handle}/video/{vid}", f"{tmp}/{vid}.html")
    if code != "200": return {}
    it = rehydration(open(f"{tmp}/{vid}.html", encoding="utf-8", errors="ignore").read()).get("webapp.video-detail", {}).get("itemInfo", {}).get("itemStruct", {})
    if not it: return {}
    s = it.get("statsV2") or it.get("stats") or {}
    return {"date": datetime.datetime.fromtimestamp(int(it.get("createTime", 0)), datetime.UTC).strftime("%Y-%m-%d"),
            "views": int(s.get("playCount", 0)), "likes": int(s.get("diggCount", 0)), "comments": int(s.get("commentCount", 0)), "shares": int(s.get("shareCount", 0)), "saves": int(s.get("collectCount", 0) or 0),
            "seconds": (it.get("video") or {}).get("duration"), "sound": (it.get("music") or {}).get("title"), "sound_original": (it.get("music") or {}).get("original"),
            "hashtags": " ".join("#" + c["hashtagName"] for c in it.get("textExtra", []) if c.get("hashtagName")), "caption": (it.get("desc") or "").replace("\n", " "),
            "is_photo": bool(it.get("imagePost"))}

def contact_sheet(mp4, out_jpg):
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout.strip() or 0)
    step = max(d / 5, 0.5)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", mp4, "-vf", f"select='eq(n,0)+gte(t-prev_selected_t,{step})',scale=270:-1,tile=6x1", "-frames:v", "1", out_jpg], capture_output=True)
    return d

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--handles", nargs="+", required=True); ap.add_argument("--out", default="research/segment")
    ap.add_argument("--download", type=int, default=0, help="download the top N videos per handle by plays"); ap.add_argument("--media", default="media/raw/segment")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); os.makedirs(f"{a.out}/montage", exist_ok=True); tmp = f"{a.out}/.pages"; os.makedirs(tmp, exist_ok=True)
    rows, profiles = [], []
    for h in a.handles:
        p = profile(h, tmp); items = embed_items(h, tmp)
        print(f"@{h}: followers={p.get('followerCount')} videos={p.get('videoCount')} embed_items={len(items)}", flush=True)
        if p: profiles.append(p)
        items.sort(key=lambda i: -(i.get("play") or 0))
        for rank, i in enumerate(items):
            row = {"handle": h, "followers": p.get("followerCount"), "id": i["id"], "plays_embed": i.get("play"), "url": f"https://www.tiktok.com/@{h}/video/{i['id']}", "desc": (i.get("desc") or "")[:200]}
            if rank < a.download and i.get("playAddr"):
                row.update(video_stats(h, i["id"], tmp))
                mdir = f"{a.media}/{h}"; os.makedirs(mdir, exist_ok=True); mp4 = f"{mdir}/{i['id']}.mp4"
                if not os.path.exists(mp4): get(i["playAddr"], mp4)
                if os.path.getsize(mp4) > 10000:
                    row["seconds"] = row.get("seconds") or round(contact_sheet(mp4, f"{a.out}/montage/{h}_{i['id']}.jpg"), 1)
                    contact_sheet(mp4, f"{a.out}/montage/{h}_{i['id']}.jpg"); row["file"] = mp4
                else:
                    os.remove(mp4); row["file"] = ""
            rows.append(row)
    keys = ["handle", "followers", "id", "plays_embed", "views", "likes", "comments", "shares", "saves", "seconds", "sound", "sound_original", "is_photo", "date", "hashtags", "caption", "desc", "url", "file"]
    with open(f"{a.out}/videos.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    json.dump(profiles, open(f"{a.out}/profiles.json", "w"), indent=1)
    print(f"{len(rows)} videos listed, {sum(1 for r in rows if r.get('file'))} downloaded → {a.out}/videos.csv")

if __name__ == "__main__":
    main()
