# Filming guide — how Antonia films a DigiRoo video on her phone

Claude reads this file. Antonia never has to. Send her the **pocket card** for whatever she's about to film: short lines she can read on her phone mid-shoot. The detail underneath is for answering "why?" and for fixing what `check_clips.py` finds.

The whole system rests on one idea: **one kid, one place, one still phone, one continuous take.** The 12.8M-view video in the niche has zero cuts. It's also the easiest thing to film, because the editor finds the moment the stand pops up by itself.

---

## 0. Phone setup — once, ever (5 lines)
Send this on her first shoot, or when a clip check finds a settings problem. iPhone: **Settings → Camera**.
1. **Record Video → 1080p HD at 30 fps.**
   - Clips stay small enough to send.
   - TikTok and Reels play at 1080 anyway.
   - Use 4K at 30 only if Liam's Mac does the cutting and she wants room to crop.
2. **Record Video → HDR Video: off.** HDR clips look washed-out grey once they're edited and posted. The editor converts them, but off is truer.
3. **Record Video → Lock White Balance: on**, plus **Lock Camera: on**, so colours and lenses don't shift mid-take.
4. **Grid: on.** The top line marks where the title will sit.
5. **Settings → Voice Memos → Audio Quality: Lossless**, for voice-overs.

Before every shoot: Do Not Disturb on (a call ruins a take), at least 5 GB free, lens wiped on a T-shirt.

Android: the same settings live under Camera → ⚙ (1080p 30 fps, HDR/"HDR10+ video" off, grid on).

---

## 1. Pocket cards (send the one that fits)

### A · The slouch-to-lift, one take (the default; most posts)
```
📱 Phone UPRIGHT, leaning on a mug, side-on to her, at her head height. 1x lens, no zoom.
☀️ Window behind the PHONE, not behind her. Lamp on after 4pm.
🖐 Tap her face on screen, hold till "AE/AF LOCK". Don't touch the phone again.
⏺ Record, then wait: let her sink into her show, 5+ seconds of slouch (count "1 Mississippi"…).
⬆️ Your hand comes in from the side, pops the stand up, out again. Don't block her face.
⏳ 5+ seconds of her upright. Say your line off-camera if the card has one. 3 more seconds. Stop.
🔁 Do it twice. Takes are free; the editor picks the better one.
```
**Good looks like:** her whole head to her lap and the iPad in frame, side-on. Empty wall or ceiling across the top quarter. The same framing before and after, because the phone never moved.

### B · Talking to camera (Antonia)
```
📱 Front camera, phone at YOUR eye level (stack of books), arm's length away.
👀 Eyes on the top grid line or a little under it, so there's room above your head for the title.
☀️ Face the window. Plain wall behind you, 1–2 m back if you can.
🔇 TV, dishwasher, fan, AC off. Doors shut.
🗣 First word is the hook, no "Hi, I'm Antonia". Look at the LENS, not your face.
🔁 Say each line twice with a breath between. Fluff a word? Keep rolling, start the sentence again.
⏹ Count 2 seconds after the last word, then stop.
```
**Good looks like:** you fill about the middle third of the frame, with the top of your head around a quarter of the way down. Lively, about 20% more energy than feels natural.

### C · Voice-over (voice memo)
```
🚗 Parked car, engine off, windows up. Or a closet full of clothes.
📱 Voice Memos, phone 20 cm from your mouth, slightly to the side (no puffs).
🗣 Read the card's script once through, pause, then once more. Smile while you talk; it carries.
⏹ Send the memo with the clips.
```

### D · Car (format 12, how-to in the car)
```
🅿️ Parked. Never film while driving.
📱 Phone braced on the front headrest or passenger seat, upright, pointing back at her, at her head height.
☀️ Sunshade on her window; no direct sun on her face. Film before 4pm in winter.
⏺ One take: iPad flat on her lap → stand up on her knees → screen at eye level → 5 s upright.
```

### E · Hands and product (no kid needed)
```
📱 Phone upright, propped, 30–40 cm away. Plain table, window light from the side.
🖐 Move slowly, then HOLD the end position for 2 seconds.
🔍 Want a close-up? Film it as its own clip with the phone closer. Never zoom later.
🧽 Wipe the case first. Both colours if the card says so.
```

### F · B-roll (10 minutes, any shoot)
```
1. Hands raising the stand, 3 heights, slow (hold each 2 s).
2. Her slouched → her upright, same angle, 5 s each (the one-take covers this).
3. Close-ups: hinge, handle, colour.
4. Founder: packing an order, the 2020 sketch, a Bermuda view.
```

---

## 2. Why each instruction is there (for answering "why?")

### Framing (9:16)
- **Upright.** The phone must be vertical. Sideways footage cropped to 9:16 loses two-thirds of the picture and looks soft. `check_clips.py` says *redo*.
- **Side-on, at her head height.** The neck angle is the whole story, and from the side "watch her neck" proves itself. A phone above her looks down and hides the hunch. A mug on the coffee table is usually the right height.
- **Top quarter empty.** The title sits from about 300 px down to 700 px. Text sitting on her face breaks the frame (never put text on a face; take-one).
- **Not under the right edge or the bottom fifth.** TikTok and Reels put the like/comment buttons down the right side from about mid-height, and the caption and handle at the bottom. The text safe zone is x 56–940, y 285–1480 on a 1080×1920 frame.
- **1× lens, no zoom.** 0.5× bends faces. Digital zoom gets soft, and the editor never pushes past 1.1×.
- **Talking head: eyes about 40% down.** That leaves headroom for the persistent title above her head. In a tight selfie the title lands on her forehead.

### Light
- **Window behind the phone.** Light falls on her face. A window behind her turns her into a silhouette and blows out the sky; `check_clips.py` flags that as *blown out*.
- **One kind of light.** Daylight plus a warm ceiling bulb makes her face two colours. Daylight alone, or lamps alone after dark.
- **Lock exposure (AE/AF lock).** Otherwise the picture brightens and darkens as her hand comes into frame, and the before and after won't match.
- **Dark clips.** The editor lifts a dark clip a little (`gamma` up to 1.35) but can't invent light. Brightness under 45 is a redo.

### Sound
- **Talking takes need quiet.** Phone mics pick up the room. TV, dishwasher, AC and fans all compete with her voice. `check_clips.py` measures the background, and anything above −45 dB gets "noisy room".
- **The slouch take is different.** The show playing softly is real and fine. The editor keeps the room sound low, and her off-camera line gets cleaned up and lifted.
- **Arm's length or a voice memo.** Quieter than −38 LUFS on a talking line reads as "too far".
- **No music while filming.** It can't be removed later and it's a licensing problem. Music gets added in the app at post time.
- **The stand's click is gold.** It's the one real sound that proves the moment. The pop in the one-take catches it; don't talk over it.

### Takes
- **Roll early, stop late.** 5 s of slouch before and 5 s upright after gives the editor room. `check_clips.py` warns when either side is under 3–4 s.
- **Twice.** With Whisper, the editor scores each take against the script and keeps the best. Without it, it keeps the last one.
- **Don't trim on the phone.** Trimming is the editor's job. Don't rename or edit clips either. Send the originals.

### Directing her daughter (the most important section)
- **Never ask her to slouch.** A posed slouch looks fake, and kids overdo it. Start recording 20–30 seconds into her show and the real slouch arrives on its own.
- **Never ask her to look at the camera.** "Caught, not posed. Nobody looking at the lens" (take-one). If she notices the phone, keep rolling; she'll forget it in half a minute.
- **Give her a task, not a pose.** "Show me the part where…", "What's happening now?" Then the lift is just Mum adjusting the iPad, which is the truth.
- **20-minute budget.** Kid blocks go last and stay short. Stop before she's bored; a bored kid looks bored on camera.
- **She can say no.** No take is worth a fight, and her mood shows on camera. Reward after, not during.
- **Privacy (always):**
  - First name never said on camera or shown.
  - No school uniform or logo, no house number, street sign or car plate.
  - Everyday clothes only, never in the bath or in bed.
  - Face optional: from behind the shoulder, side-on still shows the neck.

### Continuity
- **One outfit per day of posts.** Change only her top for posts meant to look like a different day (the shoot card says which).
- **The same unit colour within a post.** Both colours go in B-roll.
- **Same couch, same blanket.** Repeating the setting week to week is a feature: viewers recognise the setup.

---

## 3. After filming
1. **Send the clips:** AirDrop to the Mac into `media/raw/<week>/<post-id>/`, put them in the shared Drive folder, or attach them in the chat.
   - Clips over about 30 MB may not attach in a chat. AirDrop or Drive those.
   - 1080p clips under 20 s are normally fine.
2. **Say "check my clips"** while her daughter is still around. A redo costs two minutes now and a week later.
3. **Don't edit, trim, rename or filter anything.**

---

## 4. Troubleshooting (what `check_clips.py` says → what to tell her)

| It says | Why | Tell her |
|---|---|---|
| filmed sideways | phone held landscape | "Hold the phone upright; one more take." |
| too dark / a bit dark | brightness <45 / <70 | "Open the curtain behind the phone or switch on a lamp beside it." |
| blown out | window behind her | "Turn so the window is behind the phone." |
| HDR is on | Camera setting | "Settings → Camera → Record Video → HDR Video off. This clip's fine, I converted it." |
| below 1080 | camera set to 720p | "Settings → Camera → Record Video → 1080p HD at 30 fps." |
| camera moves | handheld or bumped | "Lean it on a mug or a book and don't touch it once it's recording." |
| voice is quiet | too far from the mic | "Closer: arm's length. Or record the line as a voice memo." |
| noisy room | TV/AC/dishwasher | "TV and AC off for the talking bits." |
| no stand-pop found | the take has no clear lift, or the phone moved | "One take: slouch, pop the stand, upright, and keep the phone still." |
| only Xs of slouch / upright | started late or stopped early | "Roll 5 seconds before you pop it and 5 after." |
| only Xs long | stopped too fast | "Keep rolling 3 seconds before and after." |
| too big to attach | long or 4K clip | "AirDrop it to the Mac or drop it in the Drive folder." |
