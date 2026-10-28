---
name: content-week
description: Turn Antonia's brain dump (or nothing at all) into a complete 5–7 post week for DigiRoo — one post card per post with hook, script, shot list, captions, hashtags and CTA, plus a weekly calendar. Use when she says "plan my week", "content week", pastes a brain dump or voice-note transcript, shares reel links, or just asks "what should I post this week".
---

# content-week

**Promise:** 20-minute brain dump in → a week she could hand to a stranger to film. Runs in one pass. Asks at most 2 questions, and only if the answer changes the plan.

## Read first (every run)
1. `DIGIROO-brief.md` — pillars (§6), voice (§4), claims (§5), hook/CTA/hashtag banks (§7–9), settings (§12).
2. `format-library.md` — pick formats; open the chosen `formats/*.md` for the skeletons.
3. `lessons-learned.md` — last entry's "3 changes for next week" are hard constraints this week.
4. `research/awareness-calendar.md` — any hook inside the week ±3 days.
5. `media/raw/` listing (if present) — which clips already exist; prefer posts that can be cut from them.

## Inputs (all optional)
- **Brain dump:** free text, voice-note transcript, bullet list. Can be 1 line.
- **Reel links:** saved reels she wants to recreate (if `tools/ingest_videos.py` can't run, ask her for a one-line description of the reel and treat it as a format request).
- **Clips:** list of files in `media/raw/<week>/`.
- **Week start date:** default next Monday.

If there's no brain dump: propose from pillars + calendar hooks + the two best-performing formats in `lessons-learned.md`. Say so in the output.

## The 2 permitted questions (only if needed)
- "Kid on camera this week, yes or no?" (changes 2–3 formats)
- "Any product news (sale, new colour, press) to lead with?"
Otherwise assume brief defaults and go.

## Steps
1. **Parse ideas.** Split the brain dump into ideas. For each, tag the pillar (A–E) and the closest format (by hook type). Keep her words; they're the hooks.
2. **Calendar check.** Add one D-pillar post if an awareness day or season lands in the week. Mention the date in the hook.
3. **Balance to the default mix:** 2×A, 1×B, 1×C, 1×D (+ optional E on Saturday). If her ideas overflow a pillar, keep the best, park the rest in `media/<week>/parked-ideas.md`.
4. **Apply lessons.** If `lessons-learned.md` says a format/hook/time underperformed, don't use it. If it says something won, include one variation.
5. **Write each post card** using `templates/post-card.md`. Every card must have:
   - Hook: spoken + on-screen text + first visual, ≤1.5 s. Pull from §7 or write a new one in the same register.
   - Script: 20–35 s, ≤85 spoken words, spoken English, says "DigiRoo" once and ≥2 keywords from brief §10.
   - Shot list: 3–5 shots, phone only, framing + what happens + seconds. A stranger could film it.
   - On-screen text lines, in order.
   - Captions: TikTok (first line ≤150 chars, 3–5 hashtags), IG (longer, 5–8 hashtags), FB (plain).
   - Hashtags from the bank (§9) + up to 3 niche/seasonal.
   - CTA from §8 (rotate; never repeat within the week).
   - Review flag if the post quotes/voices a clinician or states a number.
6. **Claims pass.** Re-read every script against brief §5. Rewrite anything that promises an outcome into habit/comfort language.
7. **Write `media/<week>/weekly-calendar.md`** from `templates/weekly-calendar.md`: day, time (spread inside the posting window, alternate midday/evening), platforms, pillar, format, hook, card link, status `scripted`.
8. **Hand off:** tell her (a) what's in the week in 5 lines, (b) which posts need the kid, (c) "say `shoot day` and I'll group the shots into one session."

## Output files
```
media/<week>/weekly-calendar.md
media/<week>/post-cards/<week>-<dd>-<slug>.md   (5–7 files)
media/<week>/parked-ideas.md                     (if any)
```
Post id format: `w{ISO week}-{mon|tue|...}-{slug}` e.g. `w45-mon-pov-couch`.

## Acceptance
- Runs from a 5-line brain dump without follow-up questions.
- No banned words (brief §4), no outcome claims (brief §5).
- Every card's shot list is filmable with a phone in ≤15 min.
- Calendar has a time for every post inside the window in brief §12.

## Tone of the output to Antonia
Short, warm, no jargon. Lead with the calendar table, then "open any card to film it."
