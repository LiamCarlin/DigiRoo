---
name: affiliate-outreach
description: Run DigiRoo's clinician affiliate outreach — pick the next 10 pediatric chiropractors/physios by fit score from the target list, draft a personalised Instagram DM and email for each (every reference checked on the clinic's own page), present them for approval, log to the tracker, generate day-5 follow-ups, onboard clinics that say yes, and work out monthly commissions. Never sends or pays on its own. Use when Antonia says "do outreach", "next 10 clinics", "follow-ups", "who's due", "onboard <clinic>", "add this clinic", or "commissions".
---

# affiliate-outreach

**Promise:** 10 personalised, approvable messages in one pass; the tracker always knows who's drafted, who's next and who's due a follow-up. Antonia (or Claude in Chrome with her go) sends.

## Read first
- `DIGIROO-brief.md` §3 P2 (clinician persona), §5 (claims), §12 (commission/discount).
- `affiliates/clinician-list.csv` (targets; columns: clinic, clinician_name, role, city, state_or_country, website, instagram_handle, ig_followers, tiktok_handle, email, phone, specialty_tags, posts_content, fit_score, source_url, notes).
- `affiliates/tracker.csv` (every clinic drafted or contacted; columns: date, clinic, clinician_name, channel, handle_or_email, status, next_action_date, reply_summary, code, notes). Statuses: `drafted` → `approved` → `sent` → `followed_up` / `replied` → `onboarded` / `closed-no-reply` / `declined`.
- `templates/outreach-dm.md`, `templates/outreach-email.md`, `templates/affiliate-one-pager.md`.

## Modes

### "do outreach" / "next 10"
0. **Drafts waiting?** If `tracker.csv` has rows with status `drafted` or `approved`, show those first ("10 drafts from 4 Nov are waiting: approve, change or drop?") and pick no new clinics until she answers, unless she says "new ones anyway". Their messages are in the latest `affiliates/outreach-batch-NN.md`.
1. **Pick 10**: rows in `clinician-list.csv` whose clinic isn't in `tracker.csv` under any status (if two list rows share a clinic name, tell them apart by the tracker's handle_or_email), sorted by fit_score desc, then rows with an Instagram handle first (DM beats email), then Bermuda before US unless she says a metro. Skip anything with `notes` containing "closed" or "verify".
2. **Check and personalise**: for each, find one specific thing to reference, and **open the page it's on** (WebFetch, or Claude in Chrome if that's blocked). The thing must be in the page's own text: a search snippet, page tag or meta description isn't enough (a snippet once credited a clinic with a tech-neck post it never wrote). Put a quote of 15 words or fewer in the table so Antonia can see it's real.
   - Start from `notes`/`source_url`; if thin, one WebSearch for `"<clinic>" <city> blog OR instagram posture kids`.
   - Instagram-only clinic whose posts can't be read: reference their specialty and city honestly ("a pediatric PT practice for Westchester families") and mark ⚠️ "look at their latest post before sending".
   - Never invent a post.
   - While on their site, fill any blank `clinician_name`, `instagram_handle` and `email` in `clinician-list.csv`, and add `contact form <url>` and `checked YYYY-MM-DD` to `notes`. Correct a wrong note rather than leaving it.
3. **Draft** from the templates, on the best channel the clinic has: Instagram DM, then email, then their website's contact form (paste the email version and give her the form URL).
   - **DM:** 60 words or fewer, no link, one specific reference, ends with the free-unit offer and a soft question.
   - **Email:** subject + body, with `affiliates/one-pager.pdf` attached.
   - Keep the brief §4 voice and zero medical claims. Run a word count, don't eyeball it.
4. **Save and log**: write the batch to `affiliates/outreach-batch-NN.md` (next number) and add each clinic to `tracker.csv` now, status `drafted`, next_action_date blank. Logging at draft time is what stops a second run from drafting the same clinics, or messaging a clinic she already contacted without telling Claude.
5. **Present all 10** in one table: clinic · clinician · channel · the message · the checked reference with its quote · fit score. Ask once: "Approve all, or tell me which to change."
6. On approval, set status `approved`. When she confirms they were sent (or Claude in Chrome sends with her go), set `sent` with next_action_date = send date + 5.
7. **Hand back** the approved messages as a copy-paste block per channel (DMs grouped, emails grouped, contact forms with their URLs).

### "follow-ups" / "who's due"
- Rows with status `sent` and `next_action_date` ≤ today and no reply → draft the day-5 follow-up (≤40 words) from the template; present; on approval set status `followed_up`, next_action_date +7. After a second no-reply, set `closed-no-reply`.
- Rows with status `replied` → summarise the reply, propose the next step (send one-pager / ask address / create code), draft it.

### "onboard <clinic>"
1. Create the code name (`DR<LASTNAME>10`, clinic name if no clinician), note it in `tracker.csv` (`code`), and write the Shopify discount steps for her to follow (Discounts → Create discount → Amount off order → code → 10%, no minimum, one code per clinic), or do it via `shopify-admin` with her go.
2. Make the clinic's folder `affiliates/onboarded/<clinic-slug>/` with `clinic.json` (`CLINIC`, `CLINICIAN`, `HANDLE`, `CODE`, `CITY`).
3. Fill the pack: copy `affiliates/content-pack/post-0{1,2,3}-*.md` and `edits/*.json` into the folder with the placeholders replaced; run `python3 affiliates/content-pack/build_pdfs.py affiliates/onboarded/<clinic-slug>/` for the handout and code card; run `edit-cuts` on the three edit files (add `"intro"` if the clinic sent a selfie line) to produce the three mp4s.
4. Draft the "welcome + content pack" message from `templates/outreach-dm.md` (the "if they reply yes" block), attach the three videos, the handout PDF, the code card PDF and the captions, and email `affiliates/one-pager.pdf` if they haven't had it. That PDF is made once from `templates/affiliate-one-pager.md`, and only after the contact email in it is confirmed (brief §11 #17). Flag the two clinician-voiced intros **[REVIEW: clinician]** for Antonia and the clinic.
5. Log `onboarded` in `tracker.csv` with the date; set `next_action_date` to the 1st of next month for the monthly loop (`commissions` below: new post + their numbers + thanks).

### "add this clinic"
- Append a row to `clinician-list.csv` with whatever she gives; fill fit_score by the rubric in `affiliates/list-sources.md`.

### "commissions" (first Monday of the month)
1. Ask for Shopify → Analytics → Reports → **Sales by discount** for last month (screenshot or CSV).
2. For every code in `tracker.csv`: orders, sales after the discount (before tax and shipping), commission = `affiliate_commission_pct` (brief §12) × those sales. Codes with no orders still get a row.
3. Write `affiliates/commissions-YYYY-MM.csv` (month, code, clinic, orders, sales, commission, paid). Leave `paid` blank.
4. Draft each clinic's monthly note (what the one-pager promises: orders with their code, their commission, and the month's fourth post from the content pack's monthly loop, `affiliates/content-pack/README.md`). Present them with the total owed.
5. Antonia pays and sends; Claude never moves money. When she confirms, fill `paid` with the date.
6. The month's order total is the "sales" number in `weekly-review`'s affiliate funnel.

## Weekly cadence (feeds weekly-review)
Mon: next 10 · Wed: follow-ups · Fri: onboard anyone who said yes · first Monday of the month: commissions. Report funnel counts (contacted / replied / onboarded / posted / sales) in `weekly-review`.

## Rules
- Nothing is sent without Antonia's explicit approval, each batch.
- No "doctor-recommended", no medical claims, no fake familiarity ("loved your work!" without a specific).
- Max 10 new DMs per day from one IG account to stay well under spam heuristics; space sends ≥5 minutes apart if Claude in Chrome sends.
- Never DM the same clinic twice before the follow-up window; dedupe on clinic + city.
- The CSV is the source of truth. After editing `clinician-list.csv`, remind Liam the Google Sheet mirror (`affiliates/list-sources.md`) is behind.
