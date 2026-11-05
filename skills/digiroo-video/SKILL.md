---
name: digiroo-video
description: DigiRoo's one video skill, from phone to post. Turns the week's post cards into a single coached shoot (phone settings, light, framing, sound, how to direct her daughter), checks clips the moment they land and says keep or reshoot, cuts each post into a finished, captioned 9:16 video (title in frame one, stand-pop found automatically, end card with a question, music ducked under her voice, -14 LUFS), and checks every cut with numbers and frame sheets before Antonia sees it. Once a week it measures what's breaking out in the niche (length, cuts, hooks, shared sounds) and sets that week's targets. Falls back to a CapCut cut sheet when code can't run. Use when she says "shoot day", "what do I film", "how do I film this", "check my clips", "cut the week", "edit these", "make the video", "make it like this reel", "what's trending", uploads clips, or gives notes on a cut.
---

# digiroo-video

**Promise:** Antonia films from one card, drops the clips, and gets back videos that are ready to post. She learns nothing new. Each step is one sentence from her. Every other decision gets made, written down, and can be overturned in one reply. She is never the first person to watch a cut.

## The four moves

| Move | She says | Claude does | She gets | Gate before it reaches her |
|---|---|---|---|---|
| 1 · Shoot card | "shoot day" | Groups every shot of the week into one session and writes the coaching into it | `media/<week>/shoot-card.md` | ≤90 min in total, kid ≤20 min, phone only |
| 2 · Coach | "how do I film the car one?" or "first time filming" | Sends the pocket card for that setup | A 6–8 line message | Nothing she'd need to look up |
| 3 · Check | uploads clips, or "check my clips" | Runs `check_clips.py` on the folder | A keep/redo table with the reason and the fix | No "redo" left while the kid is still there |
| 4 · Cut | "cut the week" / "edit these" | Writes edit.json, runs `edit_cuts.py`, then `qc.py`, then looks at the frames and fixes once | mp4 + srt + cover per post | QC has no FAIL and every eye-check scores ≥8 |
| (notes) | "slower", "different music", "lose the second line" | Changes only that, re-cuts as `-v2`, saves the note | `<post-id>-v2.mp4` | Same gate |
| (weekly) Trends | "what's trending", or Monday's review | Measures the niche's newest videos (or reels she saved) with `trends.py` | `trends.md`: this week's length band, pop timing, hook frames, shared sounds | Rules beat trends; a trend that breaks one is reported, not adopted |

Run the moves in order when she says "do the whole week's video". Each move also works on its own.

## Read first (every run)
1. `references/video-rules.md` — the ten rules every cut must pass. The default shot is the **slouch-to-lift in one take**.
2. `video-notes.md` at the repo root, if it exists. It holds her taste and her filming notes, in her words, with dates. Apply them. If one contradicts the video rules, follow the rules and ask her once.
   `trends.md` at the repo root, if today is on or before its "good until" date: this week's length band and pop timing. Order of authority: video rules, then her notes, then trends. A stale note is ignored and named as stale.
3. `DIGIROO-brief.md` §4 (voice), §5 (claims), §12 (settings). From the content-week skill: the week's post cards in `media/<week>/post-cards/`.
4. Then only what the move needs:
   - Moves 1–3: `references/filming-guide.md`.
   - Move 4: `references/edit-craft.md`, `references/edit-style.md` (the native look and its evidence) and `references/qc-and-review.md`.
   - `references/sources.md` only if someone asks where a technique came from.

## Move 1 — Shoot card ("shoot day")
1. **Pull every shot** from every card: post id, shot, framing, what happens, who's in it (kid / Antonia / hands), location, props, seconds, and the line to say.
2. **Collapse to one-takes.** Every slouch-to-lift post becomes one continuous take: slouch → pop → upright, with her off-camera line if the card has one. The editor finds the pop. Posts that reuse Monday's footage say so and need no new shot. If the current `trends.md` band starts above 15 s, add her selfie line to those posts (the one-take alone runs 11–15 s, and holds are never padded).
3. **Group** by location, then by talent, then by setup:
   - Hands-only and Antonia-only blocks go first.
   - Kid blocks go last and stay short (20-minute attention budget).
   - Start where the light is best at her shoot time. Car and outdoor blocks go last.
4. **Time it:**

   | Item | Minutes |
   |---|---|
   | Each one-take (with one retake) | 3 |
   | Each talking line (two takes) | 3 |
   | Each hands-only shot | 2 |
   | Each change of location | +5 |
   | Setup | +10 |
   | B-roll | +10 |

   Over 90 minutes, move the lowest-priority post (pillar D or E first) to next week and recompute.
5. **Write the card** from `templates/shoot-card.md`:
   - The "Phone setup" box goes at the top **only on her first shoot**, or if a clip check found a settings problem. After that, use the one-line reminder.
   - Each block gets: the setup in one line, the "good looks like" line, what to say, the kid direction, and any filming note from `video-notes.md` that applies.
6. **Tell her** the total minutes, which block needs her daughter, and the one thing to do first (charge the phone, wipe the lens, Do Not Disturb on). End with: "When you're done, drop the clips here and say **check my clips** before she runs off."

## Move 2 — Coach ("how do I film…")
Answer from `references/filming-guide.md` with the **pocket card** for that setup: 6–8 short lines she can read on her phone while filming. Lead with where the phone goes, then light, what she does, what to say, and when to stop. Add nothing she didn't ask about.

If it's her first shoot, send the 5-line phone setup once and say it's a one-time thing.

## Move 3 — Check the clips ("check my clips", or whenever clips arrive)
1. Put the clips in `media/raw/<week>/<post-id>/`, one folder per post. In a chat, use the uploaded files where they are. **Never rename, move or re-encode a raw clip.**
2. Run `python3 <this skill>/scripts/check_clips.py <folder>`. For the slouch-to-lift take, add `--kind slouch-to-lift`; it finds the stand-pop and checks there is enough slouch before and upright after.
3. Look at `clips-check.jpg`, which shows the first, middle and last frame of every clip. Judge what the numbers can't:
   - Is she side-on?
   - Are her whole head and the iPad in frame?
   - Is the top quarter free for the title?
   - For a talking head: are the eyes about 40% down, with headroom?
   - Is anything private in shot (school logo, house number, her name on a cup)?
4. Reply with the table, cut down to **clip · keep/redo · the fix in plain words**. Put the redo items first. Example: "IMG_0413: too dark. Open the curtain behind the phone and do it once more (2 min)."
5. If a problem has now shown up twice, append one dated line under **Filming notes** in `video-notes.md`. Create the file from `templates/video-notes.md` if it doesn't exist. Example: "2026-11-11: car clips dark at 5 pm. Film the car block before 4."

## Move 4 — Cut ("cut the week", "edit these", "make the video")
**Can code run?**
- Yes: `ffmpeg` and `python3` with Pillow are available. Use **Mode A**.
- No: use **Mode B**, the cut sheet.
- Whisper (`faster-whisper`) is optional. Without it, captions are timed to the detected speech, which is close enough to post. With it, captions are word-exact and best-take picking compares the takes against the script.

### Mode A — automatic
1. **Write `media/<week>/edits/<post-id>.json`.** Shortcut: `python3 <this skill>/scripts/edit_cuts.py --card <post card> --clips <folder> --out media/cuts/<post-id>.mp4` builds one from the card. Then tighten it by hand using the patterns in `references/edit-craft.md`:
   - `recipe`
   - `title`: frame one, a full sentence a parent would say (≤12 words), off by about 4 s (`title_until`); `label`: the credential or format pill ("mom review", "before")
   - the native extras (edit-style.md): `tags` (BEFORE/AFTER), callouts with a `point` arrow, `zooms` on the beat, `sfx` (`builtin:pop` …, at most 2), `end_card.style` `live` or `split`
   - per clip: `text` (the line as spoken), `trim` (`"lift"` for the one-take)
   - `overlays` with `"at": "lift"` / `"after"`
   - `end_card.question`
   - `length_target` and `lift.before` from a current `trends.md` (edit-craft §1, "This week's band")
   - optional `music`, which must be licensed or her own, with `license` and `source` recorded; vet it with `scripts/vet_music.py` first (see edit-craft → Sound)
   - for a slouch-to-lift take, check the pop: the editor names any other motion it saw; if the pop still shows the wrong moment, set `lift.at`
   - every key is optional except `clips`
2. **Run** `python3 <this skill>/scripts/edit_cuts.py --edit media/<week>/edits/<post-id>.json`. Add `--no-whisper` if the model can't download. In a chat sandbox, write the output to the sandbox and send her the files.
3. **Read what it printed.**
   - Every `DECISION:` line, such as which take it used or where the stand-pop is, goes into your note to her.
   - Every `WARNING:` either gets fixed now or stated plainly.
4. **QC runs on its own** and writes `<post-id>.qc.md` and four images. Follow `references/qc-and-review.md`:
   - **Numbers:** fix every FAIL.
   - **Pictures:** open `hook.jpg`, `stills.jpg`, `safezone.jpg` and `sheet.jpg`, and score hook, readability, visible change, rhythm and sound from 1–10. Take 2 points off your own scores.
   - **Fixes:** if any score is under 8, make **one** fix round from the fix table, re-run, and re-check. Then deliver, saying what's still weak. Never loosen a check to pass.
   - **Fresh reviewer:** in Claude Code, a fresh subagent given only the images, the qc.md and the card can do the scoring ("default to reject").
5. **Deliver** `media/cuts/<post-id>.mp4` + `.srt` + `.cover.jpg`, and update the calendar row to `cut`. The note to her, per post:
   - one line on what it is and its length
   - the QC verdict
   - the decisions she can overturn ("used take 2; the music dips just before the pop")
   - what wasn't checked (for example "not watched on a phone yet"; "add the in-app sound when you post")

   Then: "Say **schedule the week** when you're happy."

### Mode B — cut sheet for CapCut (when code can't run)
Write `media/<week>/cut-sheets/<post-id>.md`:
```
# Cut sheet — <post-id>   (1080×1920, 30 fps, CapCut)
Clip | Use from–to | Spoken line (caption) | On-screen text | Notes
IMG_0412 | 0:02.0–0:11.8 | "That's it. That's the whole fix." (at 0:07.6) | TITLE all the way: every night, same couch, same slouch (mom + inventor) · "watch her neck" 0:03.5–0:05.7 | one take, no cuts
End | 3 s | — | what's the one thing you say every night? / save this for tonight / DigiRoo · link in bio | freeze last frame, darken 50%
Text: white, bold, thin black outline, one style. Title top third, captions lower-middle, nothing in the bottom fifth or under the right-hand buttons.
Captions: CapCut auto-captions ON, 2–4 words per line, same white style. Export 1080p, 30 fps, "Smart HDR" off.
```
Timestamps come from her note ("the pop is about 6 seconds in"), or by asking her for the second the stand goes up. That is the only question allowed.

### Notes on a cut ("make it…")
- Fold her note in and re-cut as `-v2`. Change only that place and that time. If a note is ambiguous, take the sensible reading and say which one you took.
- Never come back with a new round of options.
- Append the note to `video-notes.md` under **Taste**, dated and in her words.
- One note is about one video. Make it a standing rule only if she says "always" or it repeats.

## "Make it like this" (she shares a reel she likes)
1. Get the file. `tools/ingest_videos.py` downloads public links on a laptop; otherwise ask for a screen recording.
2. After cutting ours, run `python3 <this skill>/scripts/qc.py <our cut> --reference <their file>`. It compares length, cut times, shot lengths, the biggest move and loudness, and writes a side-by-side sheet.
3. Borrow the **timing and structure** only, never their footage, music or words. If their rhythm breaks a video rule (for example 8 cuts in 18 s), keep the rule and tell her why in one line.

## Trends ("what's trending", and every Monday with the review)
The fixed rules come from a one-off study of 30 niche videos. This move keeps them current: once a week, measure what's breaking out now and turn it into targets for the week's cards and cuts.
1. **Get the videos.**
   - **On a Mac** (Liam, or Claude Code), from the repo root:
     `python3 tools/tiktok_public_pull.py --handles-file research/trend-accounts.txt --out research/trends/<date> --media media/raw/trends/<date> --download 3 --since-days 21`
     It reads public pages only: each account's 10 newest videos with play counts (pinned old hits are dropped by date), then the top 3 per account from the last 21 days (stats, mp4, frames). About 5 minutes. TikTok blocks the chat sandbox, so this half only runs on a laptop.
   - **In a chat:** ask her for 3–6 reels she saved this week (screen recordings are fine). Put them in one folder. With no play counts they count as references, not breakouts.
2. **Measure:** `python3 <this skill>/scripts/trends.py <folder> --own research/own-posts.csv --out trends.md`. For each video it measures length, cuts, when the biggest move lands, loudness, sound, caption opener and hashtags. Breakouts are the top third by plays against their own account's median. It writes `trends.md`, `<folder>/trends.json` and `<folder>/hooks.jpg`. With `--own`, her own posts by length band (and watch-through, once weekly-review logs it) narrow the length band too.
3. **Look:** open `hooks.jpg` (frame one and 1.5 s of every breakout) and fill the two Eye check lines in `trends.md`: what's on screen at 0 s, whether there's a title, the best hook's shape in one line, and anything that breaks a rule.
4. **Tell her in 3 lines:** the length band, the hook shape worth borrowing, and the sound ("original" unless a shared sound fits a text-narrated post). Then: "`plan my week` will use it."
5. **Limits.**
   - The band only ever narrows rule 5. Breakouts with 8 cuts don't change rule 3.
   - Shared sounds are a note for post time: in-app, Commercial Music Library only, never downloaded.
   - Their footage, words and music are never used, only timing and shape.
   - The note is good for 7 days. Hashtag pages need a login, so the check follows the accounts in `research/trend-accounts.txt`; add a creator she watches there.

## Hard rules
- **Raw footage is never modified.** Work on copies; outputs go to `media/cuts/`.
- **Her daughter's privacy:**
  - First name never on screen or in captions.
  - No school logos, uniforms, house numbers, street signs, or anything that places her.
  - Everyday clothes only, never bath or bed.
  - Face optional: a side-on slouch from behind the shoulder works without it.
  - If she says "no face", every card respects it.
- **Claims:** captions and overlays say only what's on the card, and QC fails banned words (brief §4/§5). A clinician-voiced line keeps its `[REVIEW: clinician]` flag through to delivery.
- **Sound licensing:**
  - Export with her voice and the room's real sound (the stand's click is the best sound effect there is).
  - Music only if she owns it or it's CC0 / Mixkit / Pixabay with the licence read on the item's own page.
  - Trending sounds get added in-app at post time, from the Commercial Music Library on a business account.
- **Evidence:** every number told to her comes from a command that ran. Don't say "sounds good" without the loudness reading behind it.
- **Never post, schedule or send.** That is `schedule-posts`, and only after her "go".

## Files
```
scripts/edit_cuts.py     raw clips + edit.json (or a post card) → finished cut, then QC
scripts/check_clips.py   keep/redo for raw clips, with plain-English fixes
scripts/qc.py            numbers + frame sheets for a finished cut; --reference to compare timing
scripts/trends.py        the weekly trend check: niche videos (or saved reels) → trends.md with this week's targets
scripts/vet_music.py     check a music track before it goes under a cut: level, voice-range busyness, intro, singing
scripts/dvlib.py         shared helpers (probe, motion, speech, loudness, text drawing)
references/              video-rules · filming-guide · edit-craft · qc-and-review · sources
templates/               shoot-card.md · edit.json · video-notes.md · trends.md
fonts/                   TikTok Sans (native style) and Poppins (classic), both SIL OFL 1.1, so text looks the same on a Mac and in the sandbox
```
Setup on a Mac (once): `brew install ffmpeg pillow` (Homebrew's Python refuses `pip3 install`). Optional, for word-exact captions: faster-whisper in a virtual environment (`dist/SETUP.md` §C). In a chat sandbox, `pip install pillow` if it's missing. The scripts need no libass, drawtext or zscale; all the text is drawn with Pillow.
