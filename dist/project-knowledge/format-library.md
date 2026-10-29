# Format library — DigiRoo

Pick one per post. Each file has a script skeleton, shot list and the pillar it serves. Add your own proof links (saved reels) under 'Proof' in each file.

| # | Format | Pillar | Length | Use when |
|---|---|---|---|---|
| 01 | [POV: mom spots the slouch](formats/01-pov-slouch-spot.md) | A | 12–20 s | You have a kid, a couch and 10 minutes. The reliable weekly banker. |
| 02 | [Before/after in 7 seconds](formats/02-before-after-7s.md) | C | 7–12 s | You need a quick product post and have 2 clips. Great for Stories and ads later. |
| 03 | [Chiropractor explains tech neck in 20 s](formats/03-chiro-explains-20s.md) | B | 20–30 s | Pillar B week; you have a clinician quote (or an affiliate willing to be on camera / voice note). |
| 04 | [Unboxing with a kid](formats/04-unboxing-with-kid.md) | C | 25–40 s | You have a sealed unit and a kid who'll react. Also the easiest UGC brief for affiliates and customers. |
| 05 | [Stitch / react to the stat](formats/05-stitch-the-stat.md) | B | 15–25 s | A news clip, study or creator video about kids' screen time or tech neck is circulating. |
| 06 | [Day in the life: screen time edition](formats/06-day-in-the-life-screen-time.md) | A | 25–40 s | You want a low-pressure lifestyle post from B-roll you already shot. |
| 07 | [Three things I didn't know until I became a mom](formats/07-three-things-i-didnt-know.md) | A | 25–35 s | You have talking-head energy and no kid available. |
| 08 | [Why I made this (founder story)](formats/08-founder-why-i-made-this.md) | E | 30–45 s | Trust-building, new-follower weeks, Bermuda press moments, awards anniversaries. |
| 09 | [25 positions in 15 seconds](formats/09-25-positions-15s.md) | C | 12–18 s | Hands-only day; no talent needed. Good for a trending sound. |
| 10 | [Awareness-day hook (World Spine Day etc.)](formats/10-calendar-hook.md) | D | 15–30 s | An awareness day or season is within 3 days: World Spine Day (Oct 16), back-to-school, Screen-Free Week, gift guides, road-trip season. |
| 11 | [Trending sound + slouch-to-lift reveal](formats/11-trend-sound-reveal.md) | D | 7–15 s | A sound is trending with a 'transition' or 'reveal' beat and you have 10 minutes. |
| 12 | ['But will my kid actually use it?' (objection kill)](formats/12-objection-kill.md) | C | 20–30 s | Comments or DMs raise the same doubt (durability, will they use it, does it fit, is it worth $50). |
| 13 | [UGC re-cut (from the Drive folder)](formats/13-ugc-recut.md) | C | 15–30 s | Only with raw, uncaptioned clips (customer/influencer originals). Never re-cut an already-captioned post. |
| 14 | [Clinic post (for affiliates to repost)](formats/14-affiliate-clinic-post.md) | B | 15–25 s | Building the affiliate content pack; clinic-voiced, parent-friendly, no claims. |
| 15 | [Stance carousel (opinion, photo post)](formats/15-stance-carousel.md) | A | 5–7 slides | You have a parenting opinion you'd defend at dinner and no kid to film. Her best TikTok ever (2,184 views) was one. Still testing. |
| 16 | [Collab reel (co-posted with a partner)](formats/16-collab-reel.md) | D | 15–45 s | A school, clinic, event partner or parent creator will co-post. Her two biggest Instagram reels (84K, 24.5K) were collabs. One a month. |

## Pillar coverage
- A lifestyle: 01, 06, 07, 15
- B education: 03, 05, 14
- C demo/UGC: 02, 04, 09, 12, 13
- D hook/trend: 10, 11, 16
- E founder: 08

Baselines behind 15 and 16: `research/baseline-tiktok.md`, `research/baseline-instagram.md`. Teardowns of all her own videos are in `research/teardowns/`.

## Every post passes the video rules
`skills/content-week/references/video-rules.md`: title in frame one, problem before product, one kid/one place/≤3 cuts, before→lift→after in one framing, 10–30 s, one text system. Format 13 (re-cut) only with raw, uncaptioned clips.

## Rotation rule
Don't repeat a format within 2 weeks except 01 (the banker). `content-week` checks `lessons-learned.md` and prefers formats that beat the view-jail threshold last time.

## Adding a format
Run `tools/ingest_videos.py` on a saved reel, read the teardown, and if it's a new mechanism, copy any file here as a template and number it 15+.
