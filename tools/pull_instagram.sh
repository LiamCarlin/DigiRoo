#!/usr/bin/env bash
# Pull Antonia's recent Instagram/TikTok posts (with her approval) into media/raw/<account>/
# and build teardown stubs for the format library. Run on a laptop (Instagram/TikTok are
# blocked from the Claude cloud sandbox).
#
#   bash tools/pull_instagram.sh https://www.instagram.com/kidsdigitalwellness/ 20
#   bash tools/pull_instagram.sh https://www.tiktok.com/@digiroocase 20
#
# Instagram usually needs a logged-in session: log into instagram.com in Chrome first, then
# the script passes --cookies-from-browser chrome. Change BROWSER if you use another one.
set -euo pipefail
URL="${1:?profile url}"; N="${2:-20}"; BROWSER="${BROWSER:-chrome}"
ACC=$(echo "$URL" | sed -E 's#https?://(www\.)?##; s#/$##; s#.*/@?##')
OUT="media/raw/$ACC"; mkdir -p "$OUT"
command -v yt-dlp >/dev/null || pip3 install -q yt-dlp
echo "→ downloading last $N posts from $URL into $OUT"
yt-dlp --cookies-from-browser "$BROWSER" --playlist-end "$N" -f "mp4/best" \
  --write-info-json --no-write-playlist-metafiles \
  -o "$OUT/%(upload_date)s_%(id)s.%(ext)s" "$URL" || {
  echo "!! download failed. If Instagram says login required, make sure you're logged in on $BROWSER."; exit 1; }
# metadata table: date, id, views, likes, comments, duration, caption
python3 - "$OUT" <<'PY'
import json, glob, os, sys, csv
out = sys.argv[1]; rows = []
for f in sorted(glob.glob(os.path.join(out, "*.info.json"))):
    d = json.load(open(f))
    rows.append([d.get("upload_date"), d.get("id"), d.get("view_count"), d.get("like_count"), d.get("comment_count"),
                 round(float(d.get("duration") or 0), 1), (d.get("description") or "").replace("\n", " ")[:200], d.get("webpage_url")])
with open(os.path.join(out, "posts.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["date", "id", "views", "likes", "comments", "seconds", "caption", "url"]); w.writerows(rows)
print(f"{len(rows)} posts → {out}/posts.csv")
PY
echo "→ building teardown stubs (no whisper; drop --no-whisper to transcribe)"
python3 tools/ingest_videos.py --files "$OUT"/*.mp4 --out research/teardowns --no-whisper
echo "done. Next: paste research/teardowns/*/teardown.md into Claude with 'tear these down for the format library'."
