# Edit style — the "native" look, and the evidence for it

This file was written 2026-11-04, after the Babson team's notes on six test cuts: "too plain, just text", "the text is too bold", "doesn't make sense". It records what top videos in the niche and in competitors' ads actually do on screen, then the spec that `edit_cuts.py` implements as `"style": "native"`. The default is now native. `"style": "classic"` keeps the original look.

**Evidence tags:**
- **P** = guidance the platform published.
- **M** = measured study (the sample is named).
- **O** = our own frame-by-frame reading.
- **V** = vendor or agency blog (weak).

Most of the M figures come from studies the platforms ran or paid for, and several are a few years old.

## What the niche does (O)

**Our 30 top niche TikToks** (`research/segment/montage/`, 4M–18.5M views):
- **Text is small and light.** It's TikTok's own text at medium weight with a soft shadow, about 45–60 px at 1080 wide.
  - @drjoshpt, @kelseymcdonald.pt and @katie.blake.fit all do this.
  - None use heavy outlined 84 px type.
- **Hooks often sit on a box.**
  - @kidsonlychiropractic (13.2M) uses a white box with black text.
  - @pedsdoctalk uses a red rounded "Pediatrician Reacts:" pill.
- **Captions run a few words at a time.** @pedsdoctalk puts the spoken word on a white box.
- **Graphics point at the thing.**
  - The 18.5M neck-hump video draws red lines along the neck angle.
  - Its follow-up puts the before and after photos side by side.
- **Something changes every 2–3 s:** comment-reply cards, picture-in-picture, or B-roll.

**Seven live Meta ads** (Yoto ×2, Pinwheel ×2, Bark ×3; Meta Ad Library, US, active, 2026-11-04):
- **Hook text sits on frame 0 and is gone by 4–6 s.**
- **Yoto tells the story in native boxes.** It uses orange and white boxes, one per shot.
- **Bark uses word-by-word captions** with one keyword in a colour.
- **Pinwheel uses small plain captions**, with doorstep/unboxing cutaways.
- **None had a designed end card.** Several end on the product in hand.
- **Kids'-case competitors had no active US video ads** under keyword search: OtterBox Kids, Speck, Cooper and Fire Kids.

## What the platforms and studies say

| Technique | Evidence | Source |
|---|---|---|
| State the proposition in the first 3 s; 90 % of ad-recall impact lands in the first 6 s | P | TikTok creative best practices; TikTok Creative Codes (2023) |
| Text in the first 7 s: +43 % conversions | M (TikTok) | socialmediatoday.com/news/tiktok-shares-best-practice-tips-for-driving-conversion-with-your-ads/610952 |
| Brand plus message within 5 s: 1.7× more likely to drive strong purchase intent; branding repeated through the ad beats a single end-frame logo | M (Meta × Toluna, about 100 ads) | tolunacorporate.com/what-makes-short-form-video-ads-work-meta-toluna-study |
| Logo visible in the scene: +182 % brand awareness; logo overlays reduced the lift; creator-led ads got +39 % attention | M (System1 × TikTok, 887 ads) | chiefmarketer.com/system1-tiktok-study-branding-elements-and-creator-led-content-improve-short-form-video-ads |
| Voice-over at 4+ words/s converted 19 % better; on-screen text at 5–10 words/s had higher view rates | M (VidMob, 1,400 TikTok ads) | socialmediatoday.com/news/new-study-outlines-key-considerations-for-tiktok-promotions-and-ad-campaign/589041 |
| Variety of scenes: +38 % conversion; captions that state the offer: +80 % | M (TikTok) | as above (610952) |
| "Go lo-fi", use TikTok text overlays, quick scene changes, sound on | P | ads.tiktok.com/business/library/Creative_Codes_May_2023.pdf |
| Reels: keep text out of the top 14 %, the bottom 35 % and 6 % at each side | P | facebook.com/business/ads-guide/update/image/instagram-reels |
| Music or VO: up to 13 % more incremental conversions | P (Meta) | socialmediatoday.com/news/meta-shares-tips-on-reels-hooks-creative-diversification-in-ads-and-threa/808182 |
| Word-highlight captions add 18–34 % watch time | V (no method) | treat as unproven |
| TikTok Sans is the platform's own UI font, open source (SIL OFL) | — | developers.tiktok.com/blog/tiktok-sans-open-source |

**Not found:** rigorous data on how many SFX to use, on punch-ins, on split-screens, or on end card vs. no end card. Those parts of the spec are craft judgement and should be A/B tested.

## The spec (`"style": "native"`)

| Element | Look | Where | edit.json |
|---|---|---|---|
| Hook | TikTok Sans SemiBold 54 px, ink on white rounded boxes (one per line), a full first-person sentence of up to 12 words | top, y 300 | `title`, `title_until` (about 4 s, or `"first_cut"`) |
| Label pill | TikTok Sans ExtraBold 40 px, upper case, white on a brand colour | over the hook | `label`: `"mom review"`, `"before"`, `"gift idea"` … with `color` |
| Tags | same pill, timed | label slot | `tags: [{"text": "after", "from": "lift+0.8"}]` |
| Captions | TikTok Sans Bold 58 px, white, 4 px outline, soft shadow, one line, 1–4 words (≤ 22 characters); the spoken word on a yellow box | bottom at y 1240 (clear of the Reels UI) | automatic from Whisper; `caption.highlight: false` turns the box off |
| Callout | ink on a yellow box, with an arrow to the thing | over the captions | `overlays: [{"text", "at", "dur", "point": [x, y]}]` (point = fraction of the frame); `"with_captions": true` lifts it above the captions |
| Punch-in | 1.08–1.12×, in over 0.18 s, out over 0.25 s, on a beat | — | `zooms: [{"at", "scale", "dur", "focus"}]` |
| SFX | synthesised pop / whoosh / ding / tick (no licence needed), at most 2 per video, 9–18 dB under | — | `sfx: [{"file": "builtin:pop", "at": "lift", "gain_db": -10}]` |
| Close | **live**: the question on a white box and the save line over the last 2–3 s of footage, no freeze. **split**: before (top) and after (bottom) play together for 2–3 s, with pills | — | `end_card: {"style": "live" \| "split" \| "brand" \| "freeze", …}` |
| Brand | in the footage (the case, the box) and in her voice; no logo bug. The `wordmark()` pill exists for tests only | — | — |

**Brand colours,** sampled from the box: orange (238,106,47), yellow (246,194,62), green (125,187,66), teal (47,163,160), indigo (52,53,143), ink (22,22,28).

## Recipes

- **VO testimonial (20–35 s):**
  - label `mom review` and a hook written from her best line;
  - captions run from 0 s;
  - a callout plus a punch-in on the key line ("It was his neck");
  - keep her spoken CTA, ideally over the product in hand;
  - live close with the question.
- **Silent before/after (10–20 s):**
  - label `before` plus a POV hook on the slouch;
  - one short callout per shot;
  - tag `after` on the upright shot, with a ding;
  - a moving split close, if the footage has 2 s of clean "before".
- **Skit (one take, 15–20 s):**
  - label `before` plus a POV hook, gone by about 4.5 s;
  - "watch her neck" callout with an arrow at the pop;
  - pop SFX and a 1.12× punch-in on the pop;
  - tag `after` with a ding;
  - moving split close.

## QC under the native style

- **Title:** ≥ 52 px.
- **Text:** ≥ 38 px.
- **Captions:** ≤ 4 words.
- **Caption speed:** ≤ 7 words/s. Captions follow her voice; VidMob found fast text did fine.
- **Safe zone:** x 65–940, y 285–1250.

Everything else is unchanged.

## A/B tests worth running (when posting starts)

1. Live close vs. moving split vs. a 1.5 s packshot.
2. Karaoke yellow box vs. a single brand-coloured keyword.
3. With vs. without SFX.
4. Hook variants: "POV:" vs. a question vs. her own line.
