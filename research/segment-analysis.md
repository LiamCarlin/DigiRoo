# Segment analysis — what performs in DigiRoo's niche, from the videos themselves

**Pulled 2026-10-28** with `tools/tiktok_public_pull.py` from TikTok's public profile, embed and video pages (no login, plain requests). 18 accounts, 128 videos listed, the top 3 per account by plays downloaded (30 videos), frames and stats in `research/segment/`. Instagram can't be read anonymously, so this is TikTok only; the same creators cross-post.

Accounts: pediatric chiro (@kidsonlychiropractic), pediatric PTs (@ptandparenthood, @theptmama, @kelseymcdonald.pt, @develobaby, @just4kidsphysio), pediatrician (@pedsdoctalk), adult posture/PT (@drrodpt, @drjoshpt, @dr.dan_dpt, @katie.blake.fit, @thejointchiro), parenting (@biglittlefeelings, @drbeckyatgoodinside, @kayla23ma), mom-tech (@momtestedfinds), screen-time (@thescreentimeconsultant), kids-case incumbent (@otterbox). Seven accounts returned no videos from the embed endpoint (noted in `videos.csv`), so this is a sample, not a census.

## The 30 downloaded videos, ranked
| Account | Followers | Views | Likes | Comments | Shares (rate) | Saves (rate) | Sec | Sound | Caption |
|---|---|---|---|---|---|---|---|---|---|
| @katie.blake.fit | 121,900 | 18,500,000 | 1,400,000 | 2,955 | 133,500 (0.7%) | 1,105,175 (6.0%) | 36 | original | Replying to @Sasstoid   How to fix your neck hump #neckhump #neckhumpf |
| @kidsonlychiropractic | 133,200 | 13,200,000 | 1,200,000 | 7,666 | 36,100 (0.3%) | 42,706 (0.3%) | 42 | Sunbleach | BABY WHO HAS CRIED SINCE BIRTH FINALLY CALMS after a gentle pediactic  |
| @drjoshpt | 415,800 | 12,800,000 | 487,000 | 2,751 | 48,500 (0.4%) | 161,594 (1.3%) | 32 | original | Self Pop Your Low Back Easily #backpain #wfh #physicaltherapy |
| @kidsonlychiropractic | 133,200 | 6,200,000 | 424,400 | 1,239 | 5,082 (0.1%) | 12,367 (0.2%) | 63 | Yellow - Acoustic | Newborn finds relief after 7 hours of non-stop crying. A certified ped |
| @katie.blake.fit | 121,900 | 6,000,000 | 513,100 | 974 | 30,400 (0.5%) | 359,310 (6.0%) | 75 | original | How to fix tech neck #neckhump #neckhumpfix #neckhumpexercises #neckhu |
| @kidsonlychiropractic | 133,200 | 4,800,000 | 163,800 | 1,034 | 5,851 (0.1%) | 6,093 (0.1%) | 61 | River's Lullaby | Little Millie had a crazy blowout after her first adjustment, now she  |
| @kelseymcdonald.pt | 49,200 | 3,100,000 | 205,500 | 324 | 57,600 (1.9%) | 31,473 (1.0%) | 10 | original | One of my favorite tricks for babies who are learning to walk… a hula  |
| @drjoshpt | 415,800 | 2,800,000 | 132,600 | 1,098 | 27,400 (1.0%) | 70,002 (2.5%) | 61 | original | This One Muscle Fixes 80% of Low Back Tightness #backpain #golflife #p |
| @kayla23ma | 47,200 | 2,500,000 | 44,900 | 1,308 | 1,590 (0.1%) | 2,828 (0.1%) | 104 | original | #dutchoven #cleaning #cleantok #bakingsoda #cleanwithme  |
| @biglittlefeelings | 103,100 | 1,200,000 | 79,300 | 466 | 5,087 (0.4%) | 9,743 (0.8%) | 101 | original | It’s dinnertime, everyone’s exhausted, and your kid’s still using the  |
| @biglittlefeelings | 103,100 | 1,000,000 | 53,200 | 724 | 14,900 (1.5%) | 15,953 (1.6%) | 96 | original | There’s no denying it: seeing your toddler hit can be REALLY scary/tri |
| @biglittlefeelings | 103,100 | 769,900 | 83,800 | 468 | 6,111 (0.8%) | 4,491 (0.6%) | 57 | original | The goal here is to make them feel loved, seen and secure ❤️ #mindfulp |
| @kelseymcdonald.pt | 49,200 | 644,400 | 55,100 | 326 | 9,836 (1.5%) | 15,645 (2.4%) | 45 | original | Your baby’s hips are still forming — literally made of mostly cartilag |
| @momtestedfinds | 598 | 327,500 | 4,362 | 217 | 658 (0.2%) | 2,130 (0.7%) | 74 | original | When iPads are set up as Kids iPads, Apple blocks apps by age rating—e |
| @momtestedfinds | 598 | 168,900 | 1,276 | 17 | 264 (0.2%) | 746 (0.4%) | 27 | original | If your text messages are showing up on your child’s iPad, it’s usuall |
| @momtestedfinds | 598 | 138,900 | 2,265 | 56 | 517 (0.4%) | 1,634 (1.2%) | 137 | original | Setting up a kid’s iPad from scratch the RIGHT way 👧📱 I created a chil |
| @kayla23ma | 47,200 | 47,300 | 679 | 27 | 4 (0.0%) | 11 (0.0%) | 97 | original | Halloween party prep! 🎃 |
| @drjoshpt | 415,800 | 38,400 | 1,739 | 14 | 247 (0.6%) | 1,427 (3.7%) | 10 | original | Do this 20x a day to get stronger hips #beginnerworkout #beginnerexerc |
| @pedsdoctalk | 339,000 | 19,300 | 301 | 12 | 162 (0.8%) | 108 (0.6%) | 240 | original | Why does your toddler swing back the second you take something away? T |
| @theptmama | 129,100 | 8,421 | 43 | 1 | 7 (0.1%) | 14 (0.2%) | 54 | original | Cute AND functional?! 👟😍 These STQ Kids sneakers have that trendy look |
| @ptandparenthood | 57,000 | 2,566 | 83 | 2 | 3 (0.1%) | 41 (1.6%) | 85 | Glitter glitter /  | It’s time for another toy rotation! These are for my 18 month old but  |
| @thescreentimeconsultant | 15 | 1,941 | 109 | 0 | 8 (0.4%) | 1 (0.1%) | 5 | original | Lets set a good example parents 🫣 #techintentional #parenting #safescr |
| @kayla23ma | 47,200 | 1,784 | 38 | 0 | 3 (0.2%) | 10 (0.6%) | 39 | Spooky, Scary Skel | Pumpkin painting contest for work… I went with Cat in the Hat 🎨🙀 |
| @ptandparenthood | 57,000 | 1,496 | 49 | 3 | 0 (0.0%) | 11 (0.7%) | 56 | [Kirarin] Cute gli | A weekly toy rotation haul for my 18 month old!  I try to do a good mi |
| @theptmama | 129,100 | 1,344 | 24 | 7 | 1 (0.1%) | 2 (0.1%) | 14 | Halloween (Trap Re | The real Halloween horror story 🎃💀 Just a pediatric PT looking for fle |
| @ptandparenthood | 57,000 | 1,334 | 69 | 1 | 7 (0.5%) | 14 (1.0%) | 36 | original | Toddler Pumpkin Play- Part 1, Gross Motor Edition  Easy ways to help a |
| @thescreentimeconsultant | 15 | 1,173 | 44 | 18 | 1 (0.1%) | 2 (0.2%) | 33 | original | When you were a kid and you were bored 🥱 what did your parents say? 🌲  |
| @pedsdoctalk | 339,000 | 1,029 | 52 | 5 | 7 (0.7%) | 1 (0.1%) | 16 | original | IB: @lizzypalios How many times have I thought, "Can anybody read the  |
| @thescreentimeconsultant | 15 | 896 | 28 | 3 | 0 (0.0%) | 0 (0.0%) | 21 | original | I hear this all the time: “My kid needs a phone to navigate safely in  |
| @pedsdoctalk | 339,000 | 834 | 67 | 2 | 3 (0.4%) | 12 (1.4%) | 159 | original | Stitch with: @lyssa.hamblin on IG  Your kid just pointed at someone in |

## What the top videos do (from the frames)

**1. @katie.blake.fit, 18.5M, "How to fix your neck hump", 36 s, 4 cuts.** Frame one is a side-profile before/after photo of her own neck with red lines on the angle. Then one stretch, demonstrated, with plain white captions lower-middle. 1.1M saves (6% of viewers). It's a "Replying to @…" video. No speech until the end: the pictures and text carry it. Her 6M follow-up is the same video with a disclaimer slide ("I am not a professional…").

**2. @kidsonlychiropractic, 13.2M / 6.2M / 4.8M, crying baby → calm, 42–63 s, 3 cuts.** Phone footage in the clinic, text narration in a white box mid-screen ("BABY WHO HAS CRIED SINCE BIRTH FINALLY CALMS"), a soft trending sound, no voice-over. Credential inline ("CACCP certified pediatric chiropractor"). 7.6K comments: transformation plus controversy.

**3. @drjoshpt, 12.8M, "Self Pop Low Back EASILY", 32 s, zero cuts.** One static shot, title in the corner from frame one, then the move. 161K saves. His 2.8M "This muscle fixes 80% of back pain" is the same recipe with him to camera first. His 10-second "POV: you started doing this move 20x/side daily…" keeps the whole caption on screen the entire time, zero cuts.

**4. @kelseymcdonald.pt, 3.1M, hula-hoop walking trick, 10 s, zero cuts.** Title top-centre from frame one: "parenting hack for helping babies walk (from a pediatric PT + mom of 2)". Mom, baby, one trick, one shot. 57K shares, the highest share rate in the set (1.9%). Her 644K hips video: talking head with a pelvis model and the baby in a carrier, title top-left with "from a pediatric physical therapist".

**5. @biglittlefeelings, 1.2M / 1.0M / 770K, 57–101 s, 5 cuts.** Static title at the top for the whole video ("How to Get Your Toddler to Listen the First Time"), white wall, scripted talking head with jump cuts, one on-screen note card. The only long format that works, and it's a script, not a vlog.

**6. @momtestedfinds, 598 followers, 327K / 169K / 139K.** Screen recordings of iPad settings, opened on a comment card ("I don't like that you can't download certain apps…"), SEO captions ("Setting up a kid's iPad from scratch the RIGHT way"). A 600-follower account getting 300K views on a search-shaped tutorial.

**7. @thescreentimeconsultant, 15 followers.** Her 5-second kid skit ("When your mom tells you to get off your screen but she is always scrolling her phone") did 1,941 views; her 21–33 s talking-to-camera posts did 896 and 1,173. Smallest account in the set, same lesson: relatable kid moment beats explaining.

**Where Antonia's posts sit.** Her best recent product post (World Spine Day, 620 TT / 679 IG) breaks rules 1, 2 and 5: a slow walk-in, no title until later, 55 s. Her best-liked clips are the ones that accidentally follow the rules: "3 ages, 1 case" (574) opens on a toddler already using the case; "Your son needs this iPad case" (521) has a title in frame one. Nothing she has posted shows the slouch first.

## The rules (full version in `skills/content-week/references/video-rules.md`)
1. Title on screen in frame one, with a credential.
2. Problem before product: hunched kid, side-on, first.
3. One kid, one place, one static phone, ≤3 cuts.
4. Before → lift → after in the same framing.
5. 10–30 s unless it's a scripted explainer.
6. One text system, plain white, lower-middle.
7. Credentials only if true; no claim words.
8. Earn a save or share, then ask a question.
9. Original sound for how-to; trending sound only under text-narrated transformations.
10. Reply to comments with videos.

## What this changes in the system
- `content-week` now writes every card to the slouch-to-lift recipe or a listed exception (07 scripted explainer, 15 carousel, 16 collab) and refuses a card that fails the checklist.
- `shoot-day` adds "phone leaning on a mug at the kid's head height, side-on" as the default setup and shoots before/after in one go.
- `edit-cuts` prints the pre-publish checklist and defaults to plain white lower-middle captions; the yellow mid-screen overlay and the top banner are gone except for the persistent title.
- Format 13 (re-cutting old captioned posts) is demoted to "only with raw, uncaptioned clips".
- Formats 01, 02, 03, 07 get proof links from this set.

## Hypotheses to test in Weeks 01–03 (feeds weekly-review)
- H5 A 15–20 s slouch-to-lift with a title in frame one beats her 210 median by 3× (target ≥600) on the first post.
- H6 "Save this" + question CTA lifts saves+shares per view above 1% (her current: 0.1%).
- H7 A search-shaped how-to ("how to set up an iPad so your kid doesn't slouch", momtestedfinds style) outperforms a lifestyle post on views within 7 days.

## Caveats
Embed pages return a mixed set of recent and popular videos per account, not a true top-N; several big accounts returned nothing. View counts are TikTok's public counts on the day. No transcripts (no Whisper in the sandbox); spoken content inferred from captions and frames.
