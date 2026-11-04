# DigiRoo Content Studio — how to run your week

Everything runs inside Claude. Five sentences, one shoot, posts scheduled.

## Your week (about 2 hours total)

| When | Say to Claude | What you get |
|---|---|---|
| **Monday, 20 min** | `plan my week` + a brain dump (type it, or paste a voice-note transcript) | A calendar for the week and one card per post: hook, script, 3–5 phone shots, captions, hashtags. |
| **Monday, 1 min** | `shoot day` | One filming list, grouped so you set up once, with how to film each shot. Says exactly when you need your daughter. |
| **Tue or Wed, 60–90 min** | *(film with your phone from the shoot card)* | Raw clips. Most posts are **one take**: slouch, pop the stand, upright. Ask `how do I film this?` any time. |
| **Right after, 2 min** | `check my clips` + the clips | Keep or redo for each clip, with the fix in plain words, while your daughter's still around. |
| **Wed, 5 min** | `cut the week` | Finished, captioned, checked 9:16 videos for every post (or a CapCut cut sheet if you'd rather assemble). Reply with notes and you get a v2. |
| **Wed, 5 min** | `schedule the week` → read the queue → reply **go** | Posts scheduled in Meta Business Suite (Reels + Facebook) and TikTok Studio. Nothing posts until you say go. |
| **Friday, 10 min** | `do outreach` → approve the 10 messages → send | Ten personalised clinic DMs/emails, logged, with follow-ups drafted on day 5. |
| **Next Monday, 10 min** | screenshots of TikTok Studio + IG Insights + Shopify, then `review the week` | What worked, what didn't, three changes. Next week's plan already knows them. |
| **Monday, with the review** | `what's trending` (or attach 3–6 reels you saved) | What's breaking out in the niche this week, measured: the length to aim for, the hook shape worth borrowing, any sound shared by several accounts. `plan my week` and `cut the week` use it. |

If you have no ideas on a Monday, just say `plan my week`. Claude proposes from the pillars and the calendar.

## Rules the system follows
- No medical claims. Habit and comfort language only. Anything that quotes a clinician is flagged for you to check.
- Nothing posts, schedules or sends without your explicit **go**.
- Your raw footage is never modified.
- You're never the first person to watch a cut: every video is measured and looked at before it reaches you.
- Your daughter's first name, school or street never appear on screen.

## Where things live
```
DIGIROO-brief.md        who we are, who we talk to, what we can say, hashtags   ← update when something changes
format-library.md       16 short-form formats (formats/ has the scripts)
lessons-learned.md      what worked, week by week (Claude appends; you read)
video-notes.md          your taste in edits + filming notes (Claude adds a line when you give a note)
trends.md               this week's trend check: length band, hooks, shared sounds (refreshed Mondays, good for 7 days)
media/week-NN/          calendar, post cards, shoot card, cuts for each week
affiliates/             clinic list (127, mirrored to Google Sheet: https://docs.google.com/spreadsheets/d/19PT0OrWsCpwaCnSpZxLmAhDeJtkuu9f-kQtF4aKJs2w), tracker, templates, one-pager, content-pack (3 videos + handout + code card per clinic)
skills/                 plan (content-week) · video (digiroo-video: shoot, coach, check, cut, trends) · schedule · review · affiliate outreach
research/               competitors, benchmarks, awareness calendar, personas, metrics; trend-accounts.txt (who the trend check follows), own-posts.csv (your posts' length + watch time), trends/ (each week's pull)
```

## Setup (once, with Liam)
1. **Claude Project** "DigiRoo Content Studio": paste `project-instructions.md` as the instructions; upload `DIGIROO-brief.md`, `format-library.md`, `formats/`, `lessons-learned.md`, `templates/`, the current week's folder.
2. **Skills:** upload each folder in `skills/` as a zip under Settings → Capabilities → Skills (needs code execution on; available on Pro per Anthropic's help centre, confirm on her account). If skills aren't available on her plan, the Project instructions alone run the same steps.
3. **Clips in:** either add the shared Drive folder to *My Drive* (right-click → "Add shortcut to Drive") so Claude's Drive connector can see it, or AirDrop clips into `media/raw/week-NN/<post-id>/`.
4. **Video cutting:** on a Mac, `brew install ffmpeg pillow` (Homebrew's Python refuses `pip3 install`; word-exact captions need faster-whisper in a virtual environment, see `dist/SETUP.md`). Without this, `cut the week` gives a CapCut cut sheet instead. The same Mac runs the Monday trend pull (TikTok blocks Claude's chat sandbox); after it, replace `trends.md` in the Project knowledge.
5. **Phone, once:** Settings → Camera → Record Video → 1080p HD at 30 fps, HDR Video off, Lock White Balance on; Camera → Grid on. Instagram → Settings → Data usage and media quality → Upload at highest quality on.
6. **Scheduling:** TikTok account switched to a Business/Creator account (for TikTok Studio scheduling, up to 10 days ahead). Meta Business Suite already connected to the Facebook page + Instagram. Claude in Chrome installed.
7. **Affiliate codes:** one Shopify discount code per clinic, 10% off, named `DR<LASTNAME>10`.

## Questions we still need from you
See `DIGIROO-brief.md` §11. Until you answer, the defaults there are in use.
