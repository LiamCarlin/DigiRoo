---
name: affiliate-outreach
description: Run DigiRoo's clinician affiliate outreach — pick the next 10 pediatric chiropractors/physios by fit score from the target list, draft a personalised Instagram DM and email for each, present them for approval, log to the tracker, and generate day-5 follow-ups. Never sends on its own. Use when Antonia says "do outreach", "next 10 clinics", "follow-ups", "who's due", or "add this clinic".
---

# affiliate-outreach

**Promise:** 10 personalised, approvable messages in one pass; the tracker always knows who's next and who's due a follow-up. Antonia (or Claude in Chrome with her go) sends.

## Read first
- `DIGIROO-brief.md` §3 P2 (clinician persona), §5 (claims), §12 (commission/discount).
- `affiliates/clinician-list.csv` (targets; columns: clinic, clinician_name, role, city, state_or_country, website, instagram_handle, ig_followers, tiktok_handle, email, phone, specialty_tags, posts_content, fit_score, source_url, notes).
- `affiliates/tracker.csv` (what's been sent; columns: date, clinic, clinician_name, channel, handle_or_email, status, next_action_date, reply_summary, code, notes).
- `templates/outreach-dm.md`, `templates/outreach-email.md`, `templates/affiliate-one-pager.md`.

## Modes

### "do outreach" / "next 10"
1. **Pick 10**: rows in `clinician-list.csv` not yet in `tracker.csv`, sorted by fit_score desc, then rows with an Instagram handle first (DM beats email), then Bermuda before US unless she says a metro. Skip anything with `notes` containing "closed" or "verify".
2. **Personalise**: for each, find one specific thing to reference. Use the `notes`/`source_url` from the list; if thin, run one WebSearch for `"<clinic>" <city> instagram OR blog posture kids` and quote a real post/page title. If nothing specific exists, reference their specialty tag and city honestly ("your pediatric focus in Tampa"), never invent a post.
3. **Draft** from the templates: IG DM (≤60 words, no link, one specific reference, ends with the free-unit offer and a soft question) and the email variant (subject + body, one-pager attached/linked). Keep brief §4 voice, zero medical claims.
4. **Present all 10** in one table: clinic · clinician · channel · the DM text · the one specific reference used · fit score. Ask once: "Approve all, or tell me which to change."
5. On approval, **log** each to `tracker.csv` with status `drafted`, `next_action_date` = today + 5. When she confirms they were sent (or Claude in Chrome sends with her go), update status to `sent`.
6. **Hand back** the approved messages as a copy-paste block per channel (DMs grouped, emails grouped).

### "follow-ups" / "who's due"
- Rows with status `sent` and `next_action_date` ≤ today and no reply → draft the day-5 follow-up (≤40 words) from the template; present; on approval set status `followed_up`, next_action_date +7. After a second no-reply, set `closed-no-reply`.
- Rows with status `replied` → summarise the reply, propose the next step (send one-pager / ask address / create code), draft it.

### "onboard <clinic>"
1. Create the code name (`DR<LASTNAME>10`), note it in `tracker.csv` (`code`), and write the Shopify discount instructions (10% off, no minimum, one code per clinic) for her to create (or do it via `shopify-admin` with her go).
2. Make the clinic's folder `affiliates/onboarded/<clinic-slug>/` with `clinic.json` (`CLINIC`, `CLINICIAN`, `HANDLE`, `CODE`, `CITY`).
3. Fill the pack: copy `affiliates/content-pack/post-0{1,2,3}-*.md` and `edits/*.json` into the folder with the placeholders replaced; run `python3 affiliates/content-pack/build_pdfs.py affiliates/onboarded/<clinic-slug>/` for the handout and code card; run `edit-cuts` on the three edit files (add `"intro"` if the clinic sent a selfie line) to produce the three mp4s.
4. Draft the "welcome + content pack" message from `templates/outreach-dm.md` (the "if they reply yes" block), attach the three videos, the handout PDF, the code card PDF and the captions. Flag the two clinician-voiced intros **[REVIEW: clinician]** for Antonia and the clinic.
5. Log `onboarded` in `tracker.csv` with the date; set `next_action_date` to the 1st of next month for the monthly loop (new post + their numbers + thanks).

### "add this clinic"
- Append a row to `clinician-list.csv` with whatever she gives; fill fit_score by the rubric in `affiliates/list-sources.md`.

## Weekly cadence (feeds weekly-review)
Mon: next 10 · Wed: follow-ups · Fri: onboard anyone who said yes. Report funnel counts (contacted / replied / onboarded / posted / sales) in `weekly-review`.

## Rules
- Nothing is sent without Antonia's explicit approval, each batch.
- No "doctor-recommended", no medical claims, no fake familiarity ("loved your work!" without a specific).
- Max 10 new DMs per day from one IG account to stay well under spam heuristics; space sends ≥5 minutes apart if Claude in Chrome sends.
- Never DM the same clinic twice before the follow-up window; dedupe on clinic + city.
