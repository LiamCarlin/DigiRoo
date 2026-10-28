# Demo cut (pipeline proof)

`demo-cut.mp4` was produced by `skills/edit-cuts/edit_cuts.py` from three synthetic test clips (colour bars + tone, different aspect ratios) using the Monday post card's script, because Antonia's Drive clips could not be pulled into the build sandbox (see README → "Getting her Drive clips in").

What it proves, frame by frame:
- `frame-hook.png` — hook banner on top for the first 2 s, clip auto-cropped from 16:9/portrait to 1080×1920.
- `frame-overlay.png` — mid-screen on-screen text from the card (yellow) + bottom captions above the TikTok UI safe zone.
- `frame-captions.png` — captions on a muted B-roll clip, script-timed (no Whisper in the sandbox); `.srt` exported alongside.
- Leading/trailing silence trimmed on clips 1–2 (silence mode); manual trim on clip 3; end card appended.

Re-run: `python3 skills/edit-cuts/edit_cuts.py --edit media/week-01/demo-cut/edit.json --no-whisper` (paths inside `edit.json` are relative to the scratch folder it was made in; point `file` at any three clips to reproduce).
