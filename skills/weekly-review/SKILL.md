---
name: weekly-review
description: Turn last week's TikTok/Instagram/Facebook numbers (screenshots, CSV, or Metricool export) and Antonia's gut notes into a short review — what worked, what didn't and why, affiliate funnel, three concrete changes — appended to lessons-learned.md so next week's plan uses them. Use when she says "review the week", "how did we do", "the 2 L's", pastes insights screenshots, or on Monday before content-week.
---

# weekly-review (the 2 L's: what we Learned, what we'll do with it)

**Promise:** 10 minutes of her time (screenshots + 3 gut notes) → one page she can skim, and `content-week` automatically gets smarter.

## Read first
- `DIGIROO-brief.md` §12 (`view_jail_threshold`, cadence).
- `media/<week>/weekly-calendar.md` (what was posted, when, which format/pillar/hook).
- `lessons-learned.md` (previous entries, running hypotheses H1–H4).
- `affiliates/tracker.csv` (funnel: "contacted" counts `sent` and later, not `drafted` or `approved`); sales from orders on clinic codes in the Sales by discount screenshot.

## Inputs
Ask for exactly these screenshots (or a CSV / Metricool export, or she types the numbers):
- **TikTok Studio**, one per post: open the post's analytics (the screen with views, average watch time and "watched full video"), plus the Overview for the week's follower change.
- **Instagram**, one per Reel: the Reel → View insights.
- **Shopify**: Analytics → Reports → **Sales by discount** (last 7 days), and the Analytics overview (sessions, orders).
- Her gut notes: "what felt good / what felt like a chore / what people said".

If a number is missing, leave the cell blank; don't estimate. Average watch time and retention only exist in those screenshots, so without them say the hook calls are a guess.

If she sends nothing, public TikTok counts (views, likes, comments, shares, saves, post time) can be pulled on a laptop with `yt-dlp --skip-download --playlist-end 10 --print "%(timestamp)s|%(view_count)s|%(like_count)s|%(comment_count)s|%(repost_count)s|%(save_count)s|%(title).60s" https://www.tiktok.com/@digiroocase`. Retention and followers stay blank.

## Steps
0. **Find the week's posts.** Calendar rows marked `scheduled` or `posted` that went live, plus anything she posted outside the calendar.
   - **Nothing went out:** say so in one line and stop, offering `schedule the week`. Don't review a different week as if it were this one.
   - **Posts outside the calendar:** get pillar, format and hook type from `research/teardowns/<id>/teardown.md` if one exists, or from the post's first 3 seconds. Mark them `unplanned` in the table.
1. **Per-post table:** post id · platform · views · retention/avg watch · likes · comments · shares · saves · profile visits · link clicks (if known) · pillar · format · hook type · posted time.
2. **Headline numbers:** median views per platform vs. `view_jail_threshold` (600); % of posts above it; total saves+shares (the shareability signal); follower delta; Shopify orders + code uses; affiliate funnel (contacted / replied / onboarded / posted / sales).
3. **Top 2 / bottom 2** with the *why*, chosen from: hook (first 1.5 s), format, pillar, length, time slot, sound, caption first line, kid on camera or not. Be specific: "the side-profile before/after at 19:40 got 3× the shares of the talking-head at 11:30."
4. **Hypothesis check:** update H1–H4 status (supported / not yet / contradicted) with one line of evidence each.
5. **Three changes for next week.** Concrete and small: "lead with the side profile in every A post", "move the education post to Tuesday 19:30", "retry format 04 with the pink unit". These become constraints in the next `content-week` run.
6. **Objections & comments log:** copy any recurring question/objection into the `Objections` section (feeds format 12).
7. **Append** to `lessons-learned.md` using the entry template below. Never edit old entries.
8. Tell her in 5 lines: median views, best post and why, worst post and why, the three changes, and "say `plan my week` when you're ready."

## Entry template (append to lessons-learned.md)
```
## Week of YYYY-MM-DD (reviewed YYYY-MM-DD)
**Posted:** n TikTok / n Reels / n FB · **Median views:** TT x · IG y · **Above 600:** k/n · **Saves+shares:** s · **Followers:** +f (TT) +g (IG) · **Orders:** o (codes: …)
| Post | Plat | Views | Ret | Likes | Com | Shares | Saves | Pillar | Format | Hook type | Time |
|…|
**Top 2 & why:** …
**Bottom 2 & why:** …
**Affiliate funnel:** contacted a · replied b · onboarded c · posted d · sales e
**Hypotheses:** H1 … · H2 … · H3 … · H4 …
**Three changes for next week:**
1. …
2. …
3. …
**Objections / comments heard:** …
**Antonia's gut:** …
```
