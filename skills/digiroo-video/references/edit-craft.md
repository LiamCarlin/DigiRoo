# Edit craft — how a DigiRoo cut is put together

Read this before writing an edit.json. `edit_cuts.py` already enforces most of these numbers, so this file explains what each key does and which recipe to reach for. The source of each number is in brackets; `sources.md` has the links.

## 1. The shape of a DigiRoo video

**The slouch-to-lift arc.** A stable state for about 25% of the running time, the disturbance for about 45%, then settle and hold for about 30% [video-director craft.md]. In seconds:

| Beat | Length | What happens |
|---|---|---|
| Slouch | 3.5 s | Title on, problem visible. "Hold the before long enough to understand the pain" [huashu formats]. |
| Pop | ~1 s | The hand comes in and the screen rises. Fast action. |
| Upright | 4.5–5.5 s | Her line off-camera; the hold. Slow meaning ("fast actions, slow meanings", take-one timing.md). |
| End frame | 3 s | Question + save line. The CTA is never the shortest hold [take-one]. |

Total is 11–15 s. Add a 4–5 s selfie line and it's 15–20 s. That sits inside rule 5 (10–30 s).

**This week's band.** When `trends.md` is current (today is on or before its "good until" date), copy its length band into edit.json as `"length_target"` and its slouch-before into `lift.before`. `qc.py` then warns when a cut lands outside the band. Reach the band with content (the selfie line, the card's second clip), never by stretching holds or adding cuts. A band only ever narrows rule 5; for a scripted talking head, leave `length_target` out. A stale `trends.md` is ignored and named as stale in the note to her.

**Hero placement.** The pop sits 25–60% in. The loudest moment is the pop or her line, never the end card [video-director, earshot].

**Something new every 2–4 s.** Never a fully dead second outside a designed hold [video-director craft.md:81]. In a one-take, the overlay ("watch her neck") and the captions supply the new thing. Don't add cuts for that.

**Cuts.**
- At most 3 between shots (rule 3).
- Jump cuts inside one talking take don't count. They're hidden with an alternating 1.1× punch-in.
- Cut on movement, at peak velocity. Never cut on a still frame; enter the next shot already moving [video-director, huashu].
- No crossfades, wipes or blur-ins [video-director quality.md, huashu techniques.md].

**Shorter isn't better.** A 28 s cut scored the same as 20 s, and the note on the shorter one was "too fast" [take-one launch-film.md]. Don't trim holds to win seconds.

## 2. Words on screen

**The default is now `"style": "native"`. Its spec, sizes and evidence are in `edit-style.md`.** The table below is the original `"classic"` look, which is still available.

| Element | Rule | Source |
|---|---|---|
| Title | Frame one, finished. Never fades in at 0 s, because frame one is also the cover (a caption on screen at 0 s doesn't fade in either). On multi-shot cuts, `"title_until": "first_cut"` keeps a "before" title off the after shot and off faces. | video-director S:155, explainroo A:777 |
| Title copy | 6–12 words + the credential ("(mom + inventor)") | video-rules 1 |
| Title size and length | 84 px, up to 4 lines. "The headline gets a second line, not a smaller size." Only past 4 lines does it drop to 76. | video-director ≥84 px by 3 s; take-one vertical.md:39 |
| Title position | Top at y 300. Inside the 4:5 feed-preview crop (y ≥ 285) and the IG grid's middle 3:4. | take-one vertical.md:41,76 |
| Captions | 2–5 words. Break at a phrase end, ≤28 characters, no full stop on screen, never end a cue on "the", "I", "of" (the editor picks the split). A line already on screen as the title gets `"captions": false`. | take-one words.md:22-23, explainroo captions.js |
| Caption position | Lower-middle; block bottom at y 1340, width ≤760 px centred, clear of the button rail (x > 940 below y 880) | take-one, explainroo safe areas |
| Caption timing | Lands 0.08 s ahead of the word and eases in over 4 frames. ≤3.5 words/s. | huashu craft.md:33, video-director |
| Overlays | Same style, same slot as captions, only where no caption is showing. Never the same words as the captions. Held for max(1.5 s, 1 s + 0.3 s a word). | explainroo A:774, video-director craft.md:51 |
| Density | About one extra text element every 4 s at most; "most sentences get nothing" | huashu talking-head.md:45 |
| Style | One system: white Poppins ExtraBold, thin dark outline, soft drop shadow. No second colour, no boxes, no emoji burned in (emoji live in the post caption). | video-rules 6 |
| Motion | Arrives from 95% scale with opacity on an ease-out, 133–267 ms. No bounce, never from scale 0, nothing under 100 ms (it flickers at 30 fps). | rossark SKILL.md:44,68,293 |

**Timed overlays inside one take.** `"overlays": [{"text": "watch her neck", "at": "lift"}, {"text": "eye level. no nagging.", "at": "after"}]`.
- `lift` = 1.6 s before the pop until 0.6 s after it.
- `after` = from 0.8 s after the pop to the end of the clip.
- `before` = the slouch.
- A number = seconds into the clip.

The editor moves each overlay into the longest caption-free gap. If no gap is long enough, it drops the overlay and says so, rather than putting text over text.

## 3. Picture

- **Let the footage lead.** The "natural" look is contrast 1.04, saturation 1.06, gamma 0.98 and a light unsharp after scaling. Every clip gets the same treatment, because mismatched grading breaks a film [huashu photo-led.md]. No LUT looks, no filters. Brand colour stays off the footage [huashu colour.md].
- **Dark clips** get a measured gamma lift up to 1.35, and the editor logs a decision. Very dark (<45) is a reshoot, not a fix.
- **iPhone HDR (HLG)** is converted to standard colour: zscale tone-map when the build has it, otherwise a BT.2020→709 `colorspace` conversion. The real fix is HDR Video off on the phone.
- **Zoom.**
  - Punch-in 1.1× on alternate jump cuts. Warn at >1.12×, never ≥1.2× on 1080 footage [take-one pipeline.md:81].
  - `push` (a slow push-in) ≤1.08, only on holds longer than 3 s. Not on everything: "Ken Burns on everything" is a cheap tell [huashu photo-led.md].
- **Sideways footage** gets cropped to 9:16 with `focus` [x, y], or `"fit": "blur"` to letterbox it over a blurred copy. Either way it's second-best [argo roadmap]; tell her to film upright.
- **Never upscale more than 1.5×** [video-director]. Under 1080 wide, QC warns.

## 4. Sound

| Layer | Treatment | Source |
|---|---|---|
| Her voice (on-camera or off) | `highpass 85 Hz → light FFT denoise → +2 dB at 3.2 kHz, −1.5 dB at 230 Hz → compressor 3:1 at −24 dB`, static gain to −18 LUFS, limiter | take-one vo.py:140 |
| Room sound on no-speech clips | static gain to −26 LUFS. Stays quiet, and keeps the real stand click. | earshot "every sound has a visible cause" |
| Voice-over memo | same voice chain; pre-rendered, then placed after any intro; clips follow its lines (the cut lands ~0.3 s before the next line) | video-director sound.md:86 |
| Music bed | static gain to 12 LU under the voice (`under_voice_db`); sidechain-ducked under her voice (ratio 6, attack 40 ms, release 280 ms); dips −9 dB for 0.45 s just before the pop, back on the pop; 1.5 s fade at the end | huashu sound.md:134; take-one audio.md; earshot SKILL.md:187 |
| Sound effects | `sfx: [{"file", "at": "lift", "gain_db": -8}]`, at most 2 a video, never on a hard cut, never on a key word; placed by the sound's peak | earshot sound-design.md; video-director sound.md:115 |
| Master | one measured static gain to −14 LUFS + a limiter at −2 dBFS so it reads ≤ −1 dBTP after AAC; measured again on the MP4 | take-one, earshot, video-director |

Why static gain, not loudnorm: dynamic loudnorm lifts the hiss between lines and pumps around transients like the stand's click. Its 3 s lookahead also got dropped at the end of a stream inside a big ffmpeg 9 graph, which silenced the last seconds of a voice-over in testing.

**Music: where it comes from.**
- Her own, or CC0 / Mixkit / Pixabay, with the licence read on the item's own page that session. No NC or ND, nothing "free with credit on social", no rips [earshot licences.md].
- **The default is no music in the export.** For text-narrated transformations she adds a soft trending sound in-app at post time, from the Commercial Music Library because DigiRoo is a business account (video-rules 9).
- How-tos and talking heads keep original sound.
- If a bed is used: calm acoustic or folk at 80–110 BPM, warm and family. No techno, trap, or drums under a voice [huashu music.md].
- **Vet it first:** `python3 <this skill>/scripts/vet_music.py bed.mp3` reports length, level swings, how busy the track is in the 1–4 kHz voice range, how long its intro takes (`"start"`), and whether Whisper hears singing in it (a sung bed never goes under a voice).
- **Record the licence in edit.json:** `"music": {"file", "license", "source", "start", "under_voice_db"}`. `qc.py` fails a bed with no licence and source, and measures the bed against her voice on separate stems (`music under voice`, `music in the gaps`). Under a voice the bed also loses 4 dB around 2.5 kHz (`"carve": false` turns that off).
- On Pixabay, skip tracks with the "Content ID Registered" badge: they can be auto-claimed or muted on Reels even when used legally. Mixkit's free licence forbids Content ID registration.
- **UGC that already has music under the voice** (the gaps between her words sit within ~15 dB of her voice): add no bed, set `"clean": false` (level it, skip the denoiser, which smears music), and don't `tighten` it (every cut makes the music jump). The creator's track is unlicensed for the brand until the creator names it; ask, or ask for the clean voice-over.

**Silence.**
- With the sound off, the video must still make sense; that's the hook-sheet test.
- With the sound on, there's no dead second outside the end card. QC flags silence ≥1 s, which is fine if she's adding the in-app sound.

## 5. The end frame
- Freeze of the last frame, blurred and darkened to 50%.
- Three lines: **the question** (84 px), **the save/share line** (60 px), **"DigiRoo · link in bio"** (52 px).
- 3 s by default.
- The title is gone by then: one read at a time.
- Rule 8: every video ends with a save/share line **and** a question parents want to answer.

## 6. Recipes → edit.json

**Slouch-to-lift, one take (format 01, most A/C/D posts)**
```json
{"recipe": "slouch-to-lift", "title": "every night, same couch, same slouch (mom + inventor)",
 "end_card": {"question": "what's the one thing you say every night?", "save": "save this for tonight"},
 "clips": [{"file": "IMG_0412.MOV", "text": "That's it. That's the whole fix.",
            "lift": {"before": 3.5, "after": 5.0},
            "overlays": [{"text": "watch her neck", "at": "lift"}]}]}
```

**Slouch-to-lift + Antonia's selfie line (15–20 s)**: the one-take, then `{"file": "IMG_0420.MOV", "text": "<her line>", "tighten": true}`. That's 1 cut.

**Before/after in 7 s (format 02, text-story)**: two takes in the same framing, `"mute": true`, an `overlay` each, `"recipe": "text-story"`. No speech, so it needs a sound plan: the real click as an `sfx`, a licensed bed, or in-app sound.

**Talking head (formats 03, 07, 08)**
```json
{"recipe": "talking-head", "title": "it's not how long. it's how low. (mom + inventor)",
 "clips": [{"takes": ["IMG_0501.MOV", "IMG_0502.MOV"], "text": "<line 1 as spoken>"},
           {"takes": ["IMG_0503.MOV", "IMG_0504.MOV"], "text": "<line 2>"}]}
```
- `tighten` cuts pauses longer than 0.4 s and alternates 1.1× punch-ins on the jumps.
- The best take wins on its script-match score, with ties going to the tighter delivery.
- Write `text` as it is **spoken**; Whisper mishears names otherwise [huashu talking-head.md:30].

**Voice-over how-to (format 12: car, setup)**: `"recipe": "voiceover"`, `"vo": "memo.m4a"`, muted clips each with the `text` of its line. The clips run as long as their lines, and captions come from the memo.

**Collab / clinic intro (format 16, affiliate pack)**
- `"intro": "clinic-selfie.mov"`, `"intro_text": "<their line>"`. The intro is prepended untouched and the title starts after it. That's the one allowed exception to the frame-one title rule; QC shows it as WARN.
- Clinician lines keep `[REVIEW: clinician]`.

**UGC recut (format 13)**: only raw, uncaptioned clips (no text over burned-in text). Creator permission is logged in `media/raw/permissions.md`.

## 7. Picking, trimming, tightening
| `trim` value | What the editor does |
|---|---|
| `"lift"` | Finds the strongest sustained burst of motion in a still take: frame difference on a 96×54 grey copy with a 0.5 s average, the window above 30% of the peak [earshot video.py]. Keeps `before` seconds of slouch and `after` seconds upright. If no clear burst, it falls back to the speech span and warns. |
| `"auto"` | With Whisper, the span of words that best matches `text`. Without it, from the first to the last detected speech: 50 ms windows above max(p95 − 30 dB, 45% of the way from the room floor to the voice) [take-one vo.py:32-42]. |
| `[start, end]` | Her note ("use 0:04–0:09"). |
| `null` | Keep everything. |

Captions without Whisper are spread across the detected speech by word length. Whisper makes them word-exact. Phrase-level timing is good enough for 2–5-word cues.

## 8. Posting it at full quality (tell her once; `schedule-posts` checks it)
- **Instagram:** Settings → *Data usage and media quality* → **Upload at highest quality: on**. Otherwise IG may lower quality on a weak connection.
- **TikTok:** upload from TikTok Studio on the web, or turn on the high-quality upload option in the app. Its wording moves between versions; check it on her phone once.
- Upload **our clean MP4** to each platform. Never re-post a TikTok download to IG; the watermark gets it buried.
- Leave the platforms' auto-captions **off**, since ours are burned in. Use our `.srt` only where a platform takes a caption file and shows it as an optional track.
- Cover: frame one, the title over the slouch, already inside IG's 3:4 grid crop.
