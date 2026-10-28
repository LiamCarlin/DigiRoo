# TikTok baseline — @digiroocase (pulled 2026-10-28, with Antonia's approval)

Source: TikTok's public profile and embed pages plus each video's public page. Videos are in `media/raw/tiktok-digiroocase/` (not committed, 15 MB), covers, carousel images and 6-frame contact sheets in `research/baseline-tiktok/`, per-video frame grabs and teardown stubs in `research/teardowns/`.

## Account
| Followers | Following | Total likes | Videos | Bio |
|---|---|---|---|---|
| 42 | 135 | 176 | 30 | "The first ergonomic case invented by a Mom to prevent Tech Neck. Digital Wellness tips for parents raising tech savvy kids. Collaborations welcomed" |

Bio note: "prevent Tech Neck" is a claim the brief avoids (§5). Suggest: "The kids' iPad case that lifts the screen to eye level. Screen Time, Elevated." (flag for Antonia).

## Last 10 posts (the embed exposes 10 of 30)
| Date | Views | Likes | Com | Shares | Saves | Sec | Type | What it is | Hook / first frame |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-21 | 160 | 4 | 0 | 0 | 1 | 21 | video | Fast montage of kids using DigiRoo in 6+ settings (field, kitchen, homework, screenshot of a parent's story) | "DIGIROO in action" text; opens on a sideline shot, no face, no spoken hook |
| 2026-10-17 | **620** | 15 | 0 | 2 | 0 | 55 | video | Antonia to camera for World Spine Day: chiro stat, product, boy at table | Living-room wide shot, Antonia walks in; hook arrives late |
| 2026-10-05 | 320 | 1 | 0 | 0 | 0 | – | photo (2) | Carousel: "Our head goes where our eyes go. Raise the screen." | Static graphic |
| 2026-10-03 | 521 | 8 | 0 | 2 | 2 | 19 | video | UGC-style: boy opens box, "Your son needs this iPad case!", height-adjustable demo, "share this with every Boy-Mom" | Text hook in frame 1, kid + product immediately |
| 2026-09-24 | **574** | 3 | 0 | 2 | 0 | 39 | video | "3 ages, 1 case": toddler, 8-year-old, baby all using it; "even baby J can handle them" | Toddler with pink unit in frame 1 |
| 2026-05-06 | 219 | 6 | 0 | 0 | 2 | 119 | video | Maine News TV segment with a chiropractor | TV news framing, 2 minutes long |
| 2026-04-22 | 289 | 9 | 0 | 0 | 0 | 18 | video | Digicel co-branded "day in the life" (Sarah): laptop, car, homework with DigiRoo, router, couch | "HI, MY NAME IS SARAH" red caps |
| 2025-12-23 | 228 | 2 | 0 | 0 | 0 | – | photo (1) | Holiday graphic: ergonomic posture + age-appropriate content | Static |
| 2025-12-03 | **561** | 37 | 2 | 0 | 0 | 8 | video | Bermuda sunset with a December affirmation list (no product) | Sunset + text |
| 2025-12-01 | 146 | 2 | 0 | 0 | 0 | 10 | video | "Tech savvy kids deserve the best ergonomic iPad case" | Product text |

**Median views: 305.** Mean 364. Above 600: 1 of 10. Comments: 2 total (both on the sunset post). Shares: 6 total. Saves: 5 total. Cadence: 5 posts in the last 5 weeks after a 4-month gap (May → Sept), which is the "bursty" pattern she described.

## What the numbers say
1. **Kids on screen in frame one wins.** The two best product posts (574, 521) open on a child using the case within the first second. The montage that opened on a sideline wide shot (160) and the product-text post (146) are the bottom two.
2. **The chiro angle works even with a slow hook.** World Spine Day is her best product post (620, 15 likes, 2 shares) despite a 55-second runtime and a hook that arrives after a walk-in. Cut to 25 seconds with the stat spoken in the first 1.5 seconds and it should clear 1,000. This is exactly Tuesday's post card.
3. **Her best-liked post has no product.** The Bermuda sunset affirmation (37 likes, 2 comments) is personal and local. Pillar E (founder / Bermuda) earns its Saturday slot.
4. **Nobody comments.** 2 comments across 10 posts: captions never ask a question. Every Week 01 card now ends with a comment prompt or "send this to…".
5. **Nothing is a trend or a sound play.** Sounds are generic instrumentals. One trend-sound post per week (format 11) is a cheap test.
6. **Captions already use #screentimeelevated and #worldspineday**, so the hashtag bank matches her habit. Add the clinician set (#pediatricchiropractor, #kidsposture) which she hasn't used.
7. **Claims to tidy up:** bio says "prevent Tech Neck"; the box says "the only kids tablet case designed to support positive posture" (fine); "reduces Tech Neck" appears in the homework caption. Flagged in the brief.

## Format mapping (what she already makes → library)
| Her post | Library format | Keep / change |
|---|---|---|
| 3 ages, 1 case | 06 day-in-the-life variant | Keep; add a spoken hook "three kids, one case, zero sit-ups" |
| Your son needs this iPad case | 04 unboxing with a kid | Keep; it's the UGC brief for affiliates |
| World Spine Day chiro stat | 03 chiro explains / 10 calendar hook | Cut to 25 s, stat first |
| DigiRoo in action montage | 06 day-in-the-life | Open on the strongest kid clip, not the sideline |
| Maine News segment | 05 stitch-the-stat | Re-cut the best 20 s with a text hook; 2 minutes is too long for TikTok |
| Sunset affirmation | 08 founder / Bermuda | Keep monthly, add one line of product |
| Static graphics | – | Retire on TikTok; keep for IG carousels/stories |

## Instagram
@kidsdigitalwellness could not be pulled: Instagram serves a login wall to anonymous requests and rate-limits yt-dlp (HTTP 429). It needs a logged-in session, which means running `tools/pull_instagram.sh` on a laptop where Instagram is signed in. Nothing here was spoofed or bypassed.
