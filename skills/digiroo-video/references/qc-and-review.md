# QC and review — nobody sees a cut until it has been measured and looked at

Three layers, in this order [video-director quality.md:3-6]:
1. **Numbers**: `qc.py`, run automatically at the end of `edit_cuts.py`.
2. **Pictures**: four images, looked at by Claude.
3. **A critic**: scores, the three weakest moments, one fix round.

"The user should never be the first viewer" [video-director quality.md:65]. Every number in the note to Antonia comes from a command that ran [earshot process.md:133]. Say what wasn't checked.

## 1. What `qc.py` measures

| Check | PASS when | Fails/warns because | Source |
|---|---|---|---|
| size | exactly 1080×1920 | platform re-scales soften the picture | video-director graders |
| frame rate / codec | 30 fps, h264 yuv420p, AAC | compatibility | argo export |
| fast start | `moov` before `mdat` | plays while it uploads or streams | earshot mux |
| length | 10–30 s (talking head ≤60) | video-rules 5 | segment analysis |
| loudness | −14 LUFS ±1, on the delivered MP4 | platform normalisation; too quiet loses the scroll | take-one, earshot, video-director |
| true peak | ≤ −1 dBTP after AAC | AAC overshoot clips | earshot |
| dead air | no silence ≥1 s before the end card | dead second = scroll (fine if the in-app sound covers it) | video-director craft.md:81 |
| frame one | mean ≥8 and sd ≥6 (of 255) | a black or flat first frame is a dead cover | video-director qa:417 |
| black frames | none (blackdetect 0.1 s) | glitch | explainroo qa |
| flash frames | none | single-frame flash = a bad splice | video-director qa:122 |
| frozen picture | no ≥1 s stretch with <0.25/255 change before the end card | dead air, or a dropped clip | huashu qa.js, video-director qa:144 |
| unplanned jumps | every hard change is within 2 frames of a planned cut | a hand moving fast can trip this; look before you act | video-director qa:130 |
| opening moves | some motion ≥1.5/255 in the first 5 s | a static opening reads as a photo | huashu qa.js |
| title in frame one | the title is on screen at 0.0 s | video-rules 1 (the affiliate intro is the one allowed WARN) | segment analysis |
| title size | ≥84 px, ≤4 lines | readable as a thumbnail | video-director, take-one |
| safe zone | every text box inside x 56–940 (beside the rail) and y 285–1480 | TikTok/Reels buttons and caption bar | take-one vertical.md |
| text size | nothing under 70 px | readable at phone width | take-one words.md:38 |
| words per caption | ≤5 | one glance | take-one, explainroo |
| caption speed | ≤3.5 words/s | readable on mute | video-director |
| overlay hold | ≥ max(1.5 s, 1 s + 0.3 s a word) | readable on mute | video-director craft.md:51 |
| text over text | no two text boxes overlap in time and space | one read at a time | video-rules 6 |
| claim words | none of the banned words | brief §4/§5 | brief |
| cuts between shots | ≤3 | video-rules 3 | segment analysis |
| lift found | the slouch-to-lift recipe found the stand-pop | the transformation is the video | video-rules 4 |
| ends on a question | the end card question has "?" | video-rules 8 | segment analysis |

FAIL means fix before she sees it. WARN means fix it, or tell her in one line why it stays. **Never loosen a threshold to pass** [earshot fixer.md:46]. A deliberate exception gets written into the delivery note as `qa_ok: <reason>` so the next round doesn't re-argue it.

## 2. The four images (Claude opens every one)

| File | Question to answer |
|---|---|
| `<id>.hook.jpg` (0–3 s every 0.5 s) | **The muted test.** With no sound, do these frames say what this is and why to keep watching? Title readable at thumbnail size, slouch visible? |
| `<id>.stills.jpg` (frame one, the pop, the upright hold, the end card) | Would each work as a poster [huashu director.md]? Is the problem shown before the product? Is the change in her neck obvious between still 1 and still 3? |
| `<id>.safezone.jpg` | Is any word under the red zones? Is any text on her face or on the hand doing the action? |
| `<id>.sheet.jpg` (24 frames) | One kid, one place; same framing before and after; nothing jarring; a held moment doesn't feel dead. |

Then score each 1–10:
- **hook** (first 2 s, muted)
- **readable at phone size**
- **the change is visible**
- **rhythm** (nothing rushed, nothing dead)
- **sound** (from the loudness reading plus what's in the mix)

Take **2 points** off your own scores, because makers grade about two points high [take-one concept-check.md:55]. Ship at **8+ on every line**. Name the **three weakest moments with timestamps** [take-one quality-checklist.md, huashu SKILL.md:67].

### The fresh critic (Claude Code; optional in a chat)
Spawn a subagent with only the four images, `qc.md`, and the post card. Brief:
> You are a demanding short-form editor for a parenting brand. Default to reject. From the frames alone, say in one sentence what this video is about. Score hook, readability at phone width, visible change, rhythm and sound 1–10, and list at most 5 issues ranked P0–P2, each with a timestamp and the exact fix. Do not suggest new concepts, music or footage that doesn't exist. Answer in under 300 words; end with PASS or RETURN.

Its scores run 0.5–1.5 above the maker's [take-one reviewer-brief.md:48]. Fold its P0/P1 issues in.

## 3. One fix round, then deliver
"One fix round, then one re-check. Unbounded loops make different things worse" [video-director quality.md:203]. Fix shots that scored ≤7 and leave anything scoring 9+ alone.

| Symptom | Change in edit.json |
|---|---|
| Hook unclear muted | Rewrite `title` (6–12 words: the promise + who's saying it); make sure the slouch is visible in frame one (`lift.before` up, or `focus` the crop) |
| Pop is too early or too late | `lift.before` / `lift.after`; the pop should sit 25–60% in |
| Feels slow after the pop | `lift.after` down to 4; drop an overlay |
| Feels rushed | `lift.after` up; `end_card.seconds` 3.5; fewer overlays |
| Captions too fast | `caption.words_per_cue` 2; or tighten less (`max_pause` 0.6) so the words breathe |
| Text over her face | `focus` y down (0.5–0.55) to move her lower; or a shorter title (fewer lines) |
| Overlay dropped | Shorten it to 2–4 words, or move it (`"at": "before"`) |
| Jump cuts too visible | `"punch": "auto"` (alternating 1.1×); or `max_pause` 0.6 |
| Dark | Nothing in the edit beyond the auto-lift. Ask for a reshoot with the window behind the phone. |
| Loudness off | Re-run; if it's still off, the mix is nearly silent, so add a sound plan |
| Silence ≥1 s | Fine if she's adding the in-app sound (say so); otherwise a licensed bed or `sfx` on the pop |
| Undeclared jump | Look at the sheet at that timestamp. A fast hand is fine; a glitch means re-cut that clip with a manual `trim`. |

## 4. The delivery note (per post, ≤6 lines)
```
w46-mon-couch-every-night — 12.8 s, one take, ready. QC: PASS (−14.2 LUFS, all text inside the safe zone).
Decisions you can overturn: used your second take; the stand pops at 3.8 s; "eye level" left off (captions were on screen).
Not checked: watched on a real phone. When you post, add a soft trending sound in-app (TikTok Commercial Music Library).
Files: media/cuts/w46-mon-couch-every-night.mp4 (+ .srt, .cover.jpg)
```
If she replies with a note, re-cut as `-v2`, change only that, and log it in `video-notes.md` under **Taste**.
