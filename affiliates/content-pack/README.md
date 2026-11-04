# Affiliate content pack — what every clinic gets

Three ready-to-post videos (plus captions), a printable parent handout and a code card. Personalised per clinic in about two minutes by `affiliate-outreach` → "onboard <clinic>", which fills the placeholders below and writes the clinic's folder to `affiliates/onboarded/<clinic-slug>/`.

| Placeholder | Example |
|---|---|
| `{{CLINIC}}` | Advanced Chiropractic Wellness Center |
| `{{CLINICIAN}}` | Dr. Nicole Harford |
| `{{HANDLE}}` | @advancedchiropracticbermuda |
| `{{CODE}}` | DRHARFORD10 |
| `{{CITY}}` | Hamilton, Bermuda |

## The three posts (format 14, clinic-voiced, no claims)
| # | Post | Length | Clinic films | Job |
|---|---|---|---|---|
| 1 | [Eyes up, not screen down](post-01-eyes-up.md) | 20 s | nothing (optional 5-s intro) | the tip; keyword-rich (tech neck, screen time, kids posture) |
| 2 | [Before / after, side profile](post-02-before-after.md) | 10 s | nothing | the proof; loops, works muted |
| 3 | [Will my kid actually use it?](post-03-will-they-use-it.md) | 25 s | nothing (optional 5-s intro) | the objection; day-1 vs week-2 |

Each post ships two ways:
- **As-is:** finished mp4 with Antonia's voice and the clinic's handle + code on the end card. The clinic posts it and adds one line of caption.
- **Clinic intro:** the clinic records a 5-second selfie line (given on each card), sends it over, and `edit-cuts` splices it in front. Same cut, their face first.

All three are cut from the Week 01 shoot (Mon shots 1/3/4 and Tue lines), so no extra filming by Antonia. Edit configs are in `edits/`.

## Print pieces
- [Parent handout](parent-handout.md) → `parent-handout.pdf` (A4/Letter, one page, clinic name in the footer)
- [Code card](code-card.md) → `code-card.pdf` (business-card size, 10 per sheet)

Regenerate the PDFs after filling placeholders: `python3 affiliates/content-pack/build_pdfs.py affiliates/onboarded/<clinic-slug>/`.

## Rules baked in
- No "prevents / treats / fixes / doctor-recommended". Habit and comfort language only (brief §5).
- Every video and the handout say "not medical advice" once, small.
- Clinician-voiced lines are flagged **[REVIEW: clinician]** and the clinic approves their own intro.
- The clinic's code is on screen in every video (end card) and on the handout and card, so attribution is clean.

## Monthly loop
Day 1 of each month: a fourth post (new format from the library), their numbers (orders with their code, commission), and a thank-you. Logged in `affiliates/tracker.csv`.
