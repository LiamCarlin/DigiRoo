# Video rules — what the winning videos in DigiRoo's niche actually do

Derived from 30 top-performing TikToks across 18 pediatric-chiro, pediatric-PT, posture and parenting accounts (frames, cut counts, speech timing and public stats; `research/segment-analysis.md`), plus Antonia's own 50 posts. Every post card from `content-week`, every shoot card and every cut from `digiroo-video` must pass this checklist. If a card can't pass, change the card, not the rule.

## The ten rules

1. **Title on screen in frame one.** The hook is a written line visible before anything moves: a promise or a transformation, 6–12 words, plus who's saying it. "How to fix the iPad slouch (from a mom who invented a case for it)." Spoken hooks come second; in the 18.5M and 12.8M videos nobody speaks for the first 5+ seconds, the title does the work.
2. **Show the problem before the product.** Frame one is the hunched kid, side-on, head down. The 18.5M neck-hump video opens on a before/after profile photo; the 13.2M chiro video opens on the crying baby. A product in frame one is an ad and gets scrolled.
3. **One kid, one place, one static phone.** The 12.8M, 3.1M and 38K videos have zero cuts. Keep cuts to three or fewer; never stitch different kids, rooms or years together. Lean the phone on something; no handheld pans.
4. **Transformation in one framing.** Before (slouch) → the lift → after (upright) from the same side-on angle, so the neck angle change is undeniable. "Watch her neck" beats any claim.
5. **10–30 seconds for product and how-to.** Only scripted talking-head explainers (format 07) and tutorials run longer. Her own best recent post (620) was 55 s; cut to 25.
6. **One text system, native to the platform.** TikTok Sans at medium weight, never heavy:
   - a hook sentence on white rounded boxes, with a small brand-colour label pill, gone by about 4 s;
   - one-line captions with the spoken word on a yellow box;
   - yellow callouts with an arrow to the thing.
   Captions and callouts stay above the Reels UI (y < 1250). Never put text over text, and never put a banner over burned-in captions. The spec and its evidence (the niche's top videos and competitors' live ads) are in `edit-style.md`, replacing the 2026-10-28 "plain white, persistent title" version after the team found that look too plain and too bold.
7. **Credential or honesty line, inline, true.** "from a pediatric PT + mom of 2", "CACCP certified pediatric chiropractor", "mom + inventor". Only what's real (brief §5): no "doctor-recommended", no stats without a named source.
8. **Earn a save or a share, then ask for a comment.** How-tos get saved (6% of viewers saved the neck-hump video), hacks get shared (1.9% shared the hula-hoop trick), transformations get comments. Every video ends with "save this for the next iPad session" or "send this to a parent" **and** a question parents want to answer.
9. **Sound: original for how-to, trending only for text-narrated transformations.** The text-narrated baby videos ride a soft trending sound; the how-tos are original sound. Never a loud trend sound under a spoken explanation.
10. **Reply to comments with videos.** The 18.5M video is "Replying to @…"; the 327K iPad tutorial opens on a comment card. Once a post gets a question, the answer is next week's post (format 12).

## Don'ts (all seen in her own posts or in Wednesday v1)
- Montage of unrelated clips as a "demo".
- Product, box or logo in frame one.
- Re-cutting old posts that already carry burned-in captions.
- Two caption systems on screen (hers plus ours).
- Heavy outlined text, or a title left on screen over the payoff.
- Static graphic or flyer as a video post on TikTok (fine as a carousel, see format 15).
- Spoken intro before the title ("Hi, I'm Antonia…" as frame one). Her best-liked talking head still opened with a slow walk-in.
- Anything under 1080×1920 or upscaled from 720p.

## Shot recipe that satisfies rules 1–6: the "slouch-to-lift", filmed as ONE take
The phone leans on a mug, side-on, at the kid's head height, and nobody touches it. Press record and let her sink into her show. Pop the stand, let her sit upright, say the line off-camera, stop. The editor (`digiroo-video`) finds the pop on its own and trims around it. Zero cuts, the same framing guaranteed, nothing to line up.

| Beat | What's on screen | Framing | Seconds | Text |
|---|---|---|---|---|
| Slouch | kid hunched over the iPad flat on lap/couch | side-on, phone on a mug at her head height | 3.5 | TITLE (stays) |
| Pop | hand pops the DigiRoo stand up, screen rises, she sits up | same take | ~1 | "watch her neck" |
| Upright | kid upright, watching; Antonia's one line off-camera | same take | 4.5–5.5 | caption of the line |
| (optional) Selfie | Antonia, one line | selfie, eye level | 4–5 | caption of the line |
| End frame | the last frame frozen and darkened | — | 3 | question + "save this…" |

Total 11–20 s, 0–1 cuts, one kid, one place. Filming coaching: `filming-guide.md` card A.

## Pre-publish checklist (`qc.py` measures what it can; the rest is the eye check in `qc-and-review.md`)
- [ ] Title readable in frame one, 6–12 words, credential included
- [ ] Problem visible before the product
- [ ] ≤3 cuts, one subject, one setting
- [ ] Same framing for before and after
- [ ] 10–30 s (or scripted format 07/tutorial)
- [ ] One text style, nothing over burned-in captions
- [ ] No claim words (brief §5)
- [ ] Ends with save/share line + a question
- [ ] 1080×1920 source, not upscaled
