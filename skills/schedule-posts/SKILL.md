---
name: schedule-posts
description: Push the week's finished posts into the free native schedulers — Meta Business Suite (Instagram Reels + Facebook) and TikTok Studio — through Claude in Chrome, with hashtags inserted as real entities and times spread inside Antonia's window; optionally Metricool or Buffer instead. Presents the full queue and never clicks the final Schedule button without her explicit "go". Use when she says "schedule the week", "queue these", "post these", or after edit-cuts delivers the cuts.
---

# schedule-posts

**Promise:** the queue is built, shown to her, and scheduled only after she says go. Nothing is ever published immediately.

## Read first
- `DIGIROO-brief.md` §12: `scheduler`, `posting_window_local`, `timezone`, `cross_post`, handles.
- `media/<week>/weekly-calendar.md` (times, platforms, card links, status).
- Each post card's caption blocks (TikTok / IG / FB) and the exported `media/cuts/<post-id>.mp4`.

## Inputs
- Week folder. Optional: "only TikTok", "only IG", a date range.

## Step 0 — Preflight (no browser yet)
1. List every post with status `cut`: file exists, duration ≤ 60 s (Reels/TikTok sweet spot), 9:16, size < 287 MB (TikTok web) / < 1 GB (MBS).
2. Build the time grid: run `python3 skills/schedule-posts/schedule_grid.py --calendar media/<week>/weekly-calendar.md` (wraps the tiktok-bulk-scheduler grid logic: spreads inside the window, 5-minute snaps, skips <20 min from now, refuses >10 days ahead on TikTok). Alternate midday/evening slots across the week; IG + FB at the same time as TikTok unless she says otherwise.
3. **Show the queue table**: day, time ET, platform, first caption line, file, hashtags. Ask once: "Reply **go** to schedule all, or tell me what to change."

Stop here until she answers. If the TikTok account is not a Business/Creator account with Studio scheduling available, say so and offer: (a) schedule IG+FB now and give her a TikTok posting checklist with times, or (b) draft on TikTok Studio instead.

## Step 1 — Meta Business Suite (IG Reels + Facebook)
Load Chrome tools once (ToolSearch `select:` the claude-in-chrome tab/navigate/computer/read_page/find/file_upload/javascript tools). Then, per post:
1. Open `https://business.facebook.com/latest/reels_composer` (or Planner → Create Reel) for the Kids Digital Wellness page with Instagram connected. Read the page/IG handle off the screen and state it back before uploading anything.
2. Upload `media/cuts/<post-id>.mp4`. Wait for the preview.
3. Toggle **Facebook + Instagram** placements on (per `cross_post`).
4. Paste the IG caption; MBS accepts pasted hashtags as real entities, but verify they render blue in the preview.
5. Cover: let MBS pick, unless the card specifies a cover frame (then scrub to it).
6. **Schedule** → set date + time from the grid → re-read the fields → click Schedule. Screenshot the confirmation.
7. Update the calendar row: status `scheduled`, add `MBS ✓ <time>`.

## Step 2 — TikTok Studio
Per post, on `https://www.tiktok.com/tiktokstudio/upload`:
1. Upload the file; wait for the thumbnail. Confirm the handle on screen is `@digiroocase`.
2. Clear the pre-filled caption. **Type** the TikTok caption body (don't paste).
3. Insert each hashtag via the `#` autocomplete dropdown, one at a time, and verify with the DOM check in `references/hashtag-entities.md` (copied from tiktok-bulk-scheduler). Dead hashtags get redone before moving on.
4. Leave disclosures, privacy, duet/stitch at defaults. Never toggle AI-content or branded-content on her behalf.
5. "When to post" → Schedule → date + time from the grid → re-read both fields → Schedule. Screenshot.
6. Update the calendar row: `TT ✓ <time>`.

If any step fails twice: stop, leave the rest untouched, report what's queued and where it broke. Captcha or login wall → hand to Antonia.

## Step 3 — Verify
- MBS: Planner view for the week; TikTok: Studio → Posts → Scheduled. Read back every post (date, time, first caption line). Fix mismatches.
- Write the final table into `media/<week>/weekly-calendar.md` and tell her where to edit/delete anything (Planner / TikTok Studio → Scheduled).

## Optional path — Metricool or Buffer
If `scheduler: metricool` (free plan: 1 brand, TikTok + IG + FB, calendar view): open `https://app.metricool.com/planning`, create post → select the three networks → upload → paste per-network captions (Metricool lets you customise each) → set time → Schedule. Same go-rule, same verification. Buffer: `https://publish.buffer.com`, same flow (free plan 3 channels, 10 posts per channel queued).

## Hard rules
- Never publish "now". Every post is scheduled or drafted.
- Never schedule without an explicit "go" from Antonia (or Liam in testing, on a test account).
- No raw URLs in TikTok captions; "link in bio" only. FB captions may include the store link.
- No two captions in one week share the same first line or CTA.
- Confirm the account handle out loud before the first upload on each platform.
