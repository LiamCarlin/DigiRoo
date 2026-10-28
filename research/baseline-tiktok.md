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

## All 30 posts (local pull, 2026-10-27)

Pulled on a laptop with `bash tools/pull_instagram.sh https://www.tiktok.com/@digiroocase 30` (yt-dlp 2026.10.26, Chrome cookies): 25 videos + 5 photo posts. Raw files and `posts.csv` are in `media/raw/digiroocase/` (not committed, 75 MB). Every video has a teardown stub with frames in `research/teardowns/<date>-<id>/`. The 8 hand-filled teardowns from the cloud pull stay in `research/teardowns/<id>/`. Numbers for the 10 posts above haven't moved.

**Account totals:** 9,350 views · 176 likes (matches the profile) · 6 comments · 20 shares · 7 saves. **Median 210 views, mean 312.** 3 of 30 cleared 600; 1 cleared 1,000. Photo posts median 320 vs videos 199.

| Period | Posts | Median views | Likes |
|---|---|---|---|
| 2023-09-29 → 10-05 (launch batch, one a day) | 7 | 22 | 7 |
| 2025-06 → 2025-12 | 16 | 214 | 123 |
| 2026 | 7 | 320 | 46 |

### The 20 posts the embed didn't show
| Date | Views | Likes | Com | Shares | Saves | Sec | Type | What it is | Format |
|---|---|---|---|---|---|---|---|---|---|
| 2025-11-25 | 477 | 9 | 0 | 0 | 0 | 8 | video | Trade-show booth pan, "Working to preserve little spines everywhere!" | 08 |
| 2025-11-15 | 287 | 9 | 2 | 2 | 0 | 7 | video | Antonia on a panel stage: "What I'd tell you to limit… as a PIMU-certified advocate" | 08 |
| 2025-11-12 | 343 | 13 | 0 | 1 | 1 | 7 | video | Antonia walks a hotel lobby with the box; caption "SIT UP STRAIGHT… this one's for you" | 01 / 08 |
| 2025-11-11 | 228 | 2 | 0 | 0 | 1 | 9 | video | Girl at a Christmas-tree table with the purple unit, "Just 4 weeks until school's out" | 10 |
| 2025-11-10 | 150 | 1 | 0 | 0 | 0 | – | photo | Stance carousel: "Banning devices is pointless" + her family's rules | 15? |
| 2025-11-07 | **2,184** | 4 | 0 | 1 | 0 | – | photo | Stance carousel: "Screentime is NOT a bad choice… it's a PERSONAL choice" | 15? |
| 2025-11-06 | 39 | 1 | 0 | 1 | 0 | 119 | video | Duet with Dr. Ryan Hanstad on kids' posture | 05 |
| 2025-11-05 | 360 | 8 | 0 | 0 | 0 | – | photo | #phototrend carousel: "You've seen kids hunched over their screens" | – |
| 2025-11-05 | 199 | 18 | 0 | 2 | 0 | 64 | video | Antonia to camera: "Parents of tech savvy kids need to hear this" | 07 |
| 2025-11-05 | 30 | 2 | 0 | 1 | 0 | 15 | video | "6-7" trend: boy snaps a flimsy rival case | 11 / 12 |
| 2025-10-30 | 153 | 4 | 1 | 0 | 0 | 5 | video | Customer photo collage (Ava + pink unit) | 13 |
| 2025-10-15 | 51 | 1 | 0 | 0 | 0 | 27 | video | Graphic: "Struggling to balance screen time? You're not alone" + 3 habits | – |
| 2025-06-04 | 200 | 10 | 1 | 0 | 0 | 21 | video | Product on stand, typed text "As a mom, here's why I'm loving the DigiRoo" | 02 |
| 2023-10-05 | 27 | 0 | 0 | 0 | 0 | 32 | video | "Mama Approved!": girl on the floor with the unit | 06 |
| 2023-10-04 | 11 | 0 | 0 | 0 | 0 | 22 | video | "Posture with generic (or no) tablet case": girl hunched on couch | 02 |
| 2023-10-03 | 32 | 0 | 0 | 1 | 0 | 32 | video | Boy slumped at desk, "Back to school doesn't have to mean back or neck pain!" | 02 |
| 2023-10-02 | 12 | 0 | 0 | 0 | 0 | 34 | video | Boy on couch, "Did you know… 20% of people suffer from tech neck" | 05 |
| 2023-10-01 | 14 | 2 | 0 | 1 | 0 | 58 | video | "Hey mamas, if your kids are anything like mine": girl on the floor | 06 |
| 2023-09-30 | 22 | 2 | 0 | 0 | 0 | 10 | video | Girl swaps out a generic case, "Goodbye generic iPad cases" | 04 |
| 2023-09-29 | 893 | 3 | 0 | 4 | 0 | 37 | video | Animated "Meet DigiRoo" launch intro | – |

### What the full history adds
1. **Her best post ever is a no-product stance carousel.** "Screentime is NOT a bad choice" did 2,184 views, 3.5× the next best. It got reach without engagement (4 likes, 0 comments), and a similar carousel three days later did 150, so it's one hit, not yet a pattern. With photo posts at a median of 320 against 199 for videos, this overturns "retire static graphics on TikTok" above. Keep one stance carousel a week and test two more before deciding. Candidate **format 15: stance carousel** (pillar A).
2. **The 2023 launch batch went nowhere.** Seven polished kid-plus-text clips ran on seven straight days. Apart from the animated intro (893), each got 11–32 views. Posting generic product clips every day built nothing. Since then her posts have a median about 10× higher.
3. **Antonia on camera earns likes.** Her talking head has the best like rate of any video with 100+ views: 9% (18 on 199), against 6.6% for the sunset. The lobby walk (13 likes) and the panel clip (2 comments, 2 shares) come next. Pillar E and format 07 are under-used.
4. **Long, borrowed authority doesn't travel.** The Dr. Hanstad duet (119 s) did 39 views and the Maine News segment (118 s) did 219, about median. The chiro angle works when it's short and in her own voice (World Spine Day, 620).
5. **A trend sound alone didn't help.** The "6-7" post did 30 views. Format 11 needs a real slouch-to-lift reveal, not just the sound.
6. **Asking for comments isn't enough.** "Tag a Mom friend in the comments" got 0. There are 6 comments across 30 posts. Prompts need a question parents want to answer (e.g. "What's your family's one screen rule?").
7. **More claims to retire (§5):** "Avoid tech-neck with Digiroo!", "Back to school doesn't have to mean back or neck pain!", an unsourced "20% of people suffer from tech neck", "preventing Tech Neck", "prevents kids from hunching over", "reducing neck strain", "Tech Neck be gone!". These are old posts, so leave them up but don't reuse the lines.

## Instagram
@kidsdigitalwellness is still not pulled. The cloud run hit a login wall and HTTP 429 rate limits. A local run on 2026-10-27 read Chrome's logged-in cookies fine but failed for a different reason: yt-dlp marks its Instagram *profile* extractor as broken ("Unable to extract data"), so it can't list the account's posts at all. Nothing was spoofed or bypassed. `research/baseline-instagram.md` waits on a working way to list the posts. yt-dlp's single-post Instagram extractor is not marked broken, so a list of post URLs is the likely route (untested).
