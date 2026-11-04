# Trends — checked 2026-11-04, good until 2026-11-11

`digiroo-video` and `content-week` read this before shoot cards and cuts. Order of authority: the video rules, then her notes in `video-notes.md`, then this note. After 2026-11-11 it's stale: say so and run the check again (`trends.py`, see the skill's Trends move).

**Sample:** 67 videos listed from 8 accounts · 23 measured · window: posted since 2026-10-14 (21 days) · breakouts = top third by plays against their own account's median
**Source:** `research/trends/2026-11-04` · frames: `research/trends/2026-11-04/hooks.jpg`

## What the breakouts did
| | breakouts | the rest | our rule |
|---|---|---|---|
| videos | 8 | 15 | |
| length (median) | 115.9 s | 62.6 s | 10–30 s |
| length (middle half) | 69–154 s | 30–82 s | |
| cuts (median) | 16.0 | 5 | ≤3 |
| zero-cut videos | 12% | 20% | the one-take |
| first cut at | 7.2 s | 3.5 s | |
| biggest move at (first 10 s) | 2.6 s (n=1) | 5.2 s (n=6) | the pop at ~3.5 s |
| loudness | -30.0 LUFS | -16.4 LUFS | -14 LUFS (the apps even playback out; ours stays put) |
| original sound | 100% | 80% | original for how-to (rule 9) |
| saves / views | 1% | 3% | |
| shares / views | 0% | 1% | |

## The breakouts
| account | × own median | plays | length | cuts | move at | sound | caption opens |
|---|---|---|---|---|---|---|---|
| @pedsdoctalk | ×1313.8 | 946600 | 240 s | 23 | 146.07 | original | Why does your toddler swing back the second you take somethi |
| @kidsonlychiropractic | ×44.8 | 770900 | 135 s | 15 | 2.6 | original | 🩷See this heartfelt video about baby who only takes a few mi |
| @kayla23ma | ×39.0 | 55200 | 97 s | 17 | 18.6 | original | Halloween party prep! 🎃 |
| @kidsonlychiropractic | ×8.5 | 146400 | 186 s | 17 | 91.33 | original | 💙 do you notice your baby being really tense in their body,  |
| @drjoshpt | ×6.2 | 72400 | 59 s | 2 | 28.8 | original | These strength exercises will change your life! #strength #l |
| @theptmama | ×6.0 | 3392 | 72 s | 7 | 72.33 | original | DAY 1/30 🎄 A Toy A Day with a Pediatric PT! We’re bringing b |
| @drjoshpt | ×4.8 | 55800 | 39 s | 0 | — | original | Do This Every Morning Before Your Coffee #beginnerexercise # |
| @kidsonlychiropractic | ×4.8 | 82300 | 144 s | 18 | 12.2 | original | ⭐️See How Dr. Roller helps this baby after her parents broug |

## Sounds used by 2+ accounts
- none shared this week (everyone's on their own or original sound)

## Hashtags used by 2+ accounts
- none shared this week

## How the captions open
| opener | breakouts | the rest |
|---|---|---|
| statement | 6 | 12 |
| question | 2 | 0 |
| parent voice | 0 | 1 |
| how to | 0 | 1 |
| number | 0 | 1 |

## Her own posts by length (8 posts, median 405 views)
| length | posts | median views | median watch-through |
|---|---|---|---|
| ≤15 s | 2 | 353.5 | — |
| 16–30 s | 3 | 289.0 | — |
| 31–45 s | 1 | 574.0 | — |
| 46 s + | 2 | 419.5 | — |

## This week's targets (copy into edit.json and the post cards)
- **Length:** 10–30 s → `"length_target": [10, 30]` in edit.json. Why: rule 5: 10–30 s; niche breakouts' middle half (69–154 s) barely overlaps 10–30 s, so not adopted.
- **Slouch before the pop:** 3.5 s → `"lift": {"before": 3.5}`. Why: fewer than 3 breakouts have a big move in their first 10 s, so the default stands.
- **Cuts:** breakouts median 16.0; ours stay ≤3, one take where we can.
- **Sound:** original sound; nothing shared enough to chase.

## Eye check (Claude, from research/trends/2026-11-04/hooks.jpg; fill in, then keep or drop)
- Title in frame one? Problem before product? Who is on screen at 0 s? One line on the best hook and how DigiRoo would borrow its shape: 3 of the 8 open on a written title with the credential in it: @pedsdoctalk ("Pediatrician Reacts: …", red box), @theptmama ("Day 1 of Christmas Gift Ideas for Your Kids", from a pediatric PT) and @drjoshpt ("Do This Every Morning While Your Coffee Brews"). The two clinic videos open on the baby already in the room with small word-by-word captions and no title. @kayla23ma is a selfie to camera. **Borrow two shapes.** First, the routine anchor plus credential ("every morning while your coffee brews"), e.g. "do this before every iPad session (mom + inventor)". Second, the seasonal series: @theptmama started a 30-day Christmas gift series this week, so gift season is open. One D-pillar card can be "the gift for the kid who's always on the iPad (mom + inventor)".
- Anything here that breaks a video rule (and so isn't adopted): length (69–154 s) and cuts (median 16) break rules 3 and 5. The reaction format plays someone else's clip inset, which is not our footage; use it only as a reply-to-comment (rule 10) over her own clip. None of the clinic videos have a title in frame one, so we keep rule 1.
