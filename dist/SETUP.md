# DigiRoo Content Studio — setup in 5 minutes (for Liam, then for Antonia)

## A. The Claude Project (works on any paid plan)
1. claude.ai → Projects → **New project** → name it **DigiRoo Content Studio**.
2. **Instructions** → paste the whole of `project-knowledge/project-instructions.md`.
3. **Knowledge** → upload every file in `project-knowledge/` (13 files, ~260 KB):
   `DIGIROO-brief.md`, `format-library.md`, `formats-all.md`, `video-rules.md`, `video-notes.md`, `trends.md`, `lessons-learned.md`, `templates-all.md`, `awareness-calendar.md`, `week-01-calendar-and-shoot.md`, `week-01-post-cards.md`, `questions-for-antonia.md`, `project-instructions.md`.
   Already set up? Replace `project-instructions.md` (paste it into Instructions again), `video-rules.md` and `templates-all.md`, and add `video-notes.md` and `trends.md`.
   **Every Monday** after the trend pull (C below), replace `trends.md`; it goes stale after 7 days.
4. Open a chat in the Project and type: **plan my week** followed by two lines of brain dump. You should get a calendar table and seven post cards without being asked anything.

## B. The skills (optional; needs code execution on)
Settings → Capabilities → turn on **Code execution**. Then Settings → Capabilities → **Skills** → **Upload skill** → each zip in `skills/` (five uploads: `content-week`, `digiroo-video`, `schedule-posts`, `weekly-review`, `affiliate-outreach`). After that, the same commands work in any chat, not only inside the Project, and `digiroo-video` can check and cut clips when they're attached.
**Already uploaded the old ones?** Delete `edit-cuts` and `shoot-day` first (`digiroo-video` replaces both; two skills answering "cut the week" fight), then re-upload `content-week`, `schedule-posts` and `affiliate-outreach`, which point at the new skill.
If "Upload skill" isn't available on the plan, skip this: the Project instructions carry the same steps.

## C. On a Mac, for the video pipeline (Liam now; Antonia later if she wants)
```
brew install ffmpeg
pip3 install pillow
pip3 install faster-whisper      # optional: word-exact captions and best-take picking
git clone https://github.com/LiamCarlin/DigiRoo ~/digiroo
```
The plain Homebrew ffmpeg is enough. The scripts draw all text with Pillow, so they need no libass, drawtext or zscale.
- Check clips: `python3 skills/digiroo-video/scripts/check_clips.py media/raw/week-02/<post-id> --kind slouch-to-lift`
- Cut: `python3 skills/digiroo-video/scripts/edit_cuts.py --edit media/week-02/edits/<post-id>.json` (or `--card <post card> --clips <folder> --out media/cuts/<post-id>.mp4`)
- QC on its own: `python3 skills/digiroo-video/scripts/qc.py media/cuts/<post-id>.mp4 [--reference saved-reel.mp4]`
- Trend check, Mondays (~5 min, public pages only):
  `python3 tools/tiktok_public_pull.py --handles-file research/trend-accounts.txt --out research/trends/<date> --media media/raw/trends/<date> --download 3 --since-days 21`
  `python3 skills/digiroo-video/scripts/trends.py research/trends/<date> --own research/own-posts.csv --out trends.md`
  then `python3 tools/package_skills.py` and replace `trends.md` in the Project.
- After editing anything in `skills/` or `templates/`: `python3 tools/package_skills.py` rebuilds these zips and the knowledge files.

## D. The five sentences Antonia says each week
`plan my week` · `shoot day` · `check my clips` · `cut the week` · `schedule the week` (then **go**) · `review the week` — plus `do outreach` on Fridays and `what's trending` on Mondays. Any time: `how do I film this?`

## E. Before Friday's demo, check
- [ ] Project answers `plan my week` with a calendar in under two minutes
- [ ] `media/week-01/post-cards/` open as readable cards (show Monday)
- [ ] A cut from the couch shoot plays (or the demo cut in `media/week-01/demo-cut/` as the pipeline proof)
- [ ] `affiliates/outreach-batch-01.md` and the content pack PDFs open
- [ ] Screen recording done (script in `docs-demo-script.md`)
