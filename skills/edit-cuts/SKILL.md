---
name: edit-cuts
description: Turn the week's raw phone clips plus a post card into a finished, captioned 9:16 video (hook text on top, word-timed captions, end card) ready to schedule — or, when the Python pipeline can't run, a CapCut/Canva-ready cut sheet with timestamps and caption text. Use when Antonia says "cut the week", "edit these", "make the videos", "caption this", or uploads clips after a shoot.
---

# edit-cuts

**Promise:** raw clips in → post-ready mp4 + .srt per post, no timeline editing by her. Two modes; always deliver one of them.

## Read first
- `skills/content-week/references/video-rules.md` → the script prints the pre-publish checklist; a cut that fails it goes back to the card, not to the queue. Defaults: persistent `title` in the upper third, plain white lower-middle captions, no overlay over burned-in text.
- The post card(s) for the week (`media/<week>/post-cards/*.md`): script lines, on-screen text, hook, shot order, "Edit notes".
- `DIGIROO-brief.md` §4 (voice) for any caption rewording, §5 (claims).
- Clips: `media/raw/<week>/<post-id>/` (one folder per post; file order = shot order), or whatever she uploaded.

## Mode A — automatic (`edit_cuts.py`)
Runs anywhere with ffmpeg + Python 3.10+. Whisper (faster-whisper) is optional and improves caption timing; without it the script still ships a finished cut with script-timed captions.

1. **Map clips to shots.** List the clip files in order; pair each with the matching script line and on-screen text from the card. If the count doesn't match, pair by watching the first frame (`ffmpeg -ss 1 -frames:v 1`) and ask one question only if it's genuinely ambiguous.
2. **Write `media/<week>/edits/<post-id>.json`** in the schema at the top of `edit_cuts.py`:
   - `hook` = the card's on-screen hook text.
   - per clip: `text` = that shot's spoken line; `overlay` = that shot's on-screen text; `trim` = `"auto"` (default), `[start,end]` if she said "use 0:04–0:09", or `null` for B-roll; `mute: true` for B-roll under VO.
   - `end_card` default on; `music` only if she dropped a bed file.
   - `vo` = a separately recorded voice memo (m4a) to lay over muted clips; `intro` = a clip to prepend untouched (used by the affiliate pack for the clinic's 5-second selfie line; the hook banner then starts after it).
3. **Run:** `python3 skills/edit-cuts/edit_cuts.py --edit media/<week>/edits/<post-id>.json`
   - Whisper present → each clip is trimmed to the spoken segment that matches its script line, captions are word-timed.
   - Whisper absent/blocked → `--no-whisper` behaviour: leading/trailing silence trimmed, captions spread across the clip by word length. Still post-ready.
   - A precomputed transcript (`--transcripts dir/` with `<clip>.words.json`) also works; useful when Liam runs Whisper once on his Mac.
4. **QC** (report honestly):
   - Hook visible in the first 2 s, above the safe zone; captions clear of the bottom 430 px (TikTok UI).
   - Total ≤ 45 s unless the card says otherwise; no dead air > 0.7 s.
   - Audio levels consistent (loudnorm is applied per clip).
   - Product name appears on screen at least once (end card does this).
   - Grab 3 frames (start, middle, end) and look at them.
5. **Deliver:** `media/cuts/<post-id>.mp4` + `.srt` + `.edit.json`. Update the calendar row status to `cut`. Send the files to her.

Setup on a Mac (once): `brew install ffmpeg && pip3 install faster-whisper pillow` (the Whisper model downloads on first run, ~150 MB for `base`).

## Mode B — cut sheet for CapCut / Canva (when A can't run)
Produce `media/<week>/cut-sheets/<post-id>.md`:
```
# Cut sheet — <post-id>   (CapCut template: "DigiRoo captions")
Clip | Use from–to | Spoken line (type as caption) | On-screen text | Notes
IMG_0231 | 0:01.2–0:04.8 | Every parent has seen this. | POV: you look over and see this | hook text top, 2 s
IMG_0232 | 0:00.5–0:04.5 | So the screen comes up instead. | and now I don't have to say sit up | yellow mid text
IMG_0233 | 0:00.5–0:03.5 | DigiRoo. It's in my bio. | — | mute, VO over
End card | 2.5 s | — | Screen Time, Elevated. / DigiRoo · link in bio | saved Canva end card
Captions: Auto-captions ON, style "DigiRoo captions" (white, bold, outline, bottom-safe). Export 1080×1920, 30 fps.
```
Timestamps come from `silence_trim` logic (listen for the start/end of speech) or her note. One saved CapCut template + this sheet = 5 minutes per post.

## Rules
- Never modify files in `media/raw/`; work on copies/exports only.
- Captions are the script as spoken; if Whisper hears something different, trust the audio, but keep the on-screen text from the card.
- No claims added in captions beyond what's on the card.
- If a clip is unusable (shaky, no audio), say which and offer the B-roll substitute from the shoot card, don't silently drop it.
