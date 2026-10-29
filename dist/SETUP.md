# DigiRoo Content Studio — setup in 5 minutes (for Liam, then for Antonia)

## A. The Claude Project (works on any paid plan)
1. claude.ai → Projects → **New project** → name it **DigiRoo Content Studio**.
2. **Instructions** → paste the whole of `project-knowledge/project-instructions.md`.
3. **Knowledge** → upload every file in `project-knowledge/` (11 files, ~250 KB):
   `DIGIROO-brief.md`, `format-library.md`, `formats-all.md`, `video-rules.md`, `lessons-learned.md`, `templates-all.md`, `awareness-calendar.md`, `week-01-calendar-and-shoot.md`, `week-01-post-cards.md`, `questions-for-antonia.md`, `project-instructions.md`.
4. Open a chat in the Project and type: **plan my week** followed by two lines of brain dump. You should get a calendar table and seven post cards without being asked anything.

## B. The skills (optional; needs code execution on)
Settings → Capabilities → turn on **Code execution**. Then Settings → Capabilities → **Skills** → **Upload skill** → each zip in `skills/` (six uploads). After that, the same commands work in any chat, not only inside the Project, and `edit-cuts` can run its Python when clips are attached.
If "Upload skill" isn't available on the plan, skip this: the Project instructions carry the same steps.

## C. On a Mac, for the video pipeline (Liam now; Antonia later if she wants)
```
brew install ffmpeg
pip3 install faster-whisper pillow
git clone https://github.com/LiamCarlin/DigiRoo ~/digiroo
```
Then `python3 skills/edit-cuts/edit_cuts.py --edit media/week-01/edits/<post-id>.json` after clips are in `media/raw/week-01/<post-id>/`.

## D. The five sentences Antonia says each week
`plan my week` · `shoot day` · `cut the week` · `schedule the week` (then **go**) · `review the week` — plus `do outreach` on Fridays.

## E. Before Friday's demo, check
- [ ] Project answers `plan my week` with a calendar in under two minutes
- [ ] `media/week-01/post-cards/` open as readable cards (show Monday)
- [ ] A cut from the couch shoot plays (or the demo cut in `media/week-01/demo-cut/` as the pipeline proof)
- [ ] `affiliates/outreach-batch-01.md` and the content pack PDFs open
- [ ] Screen recording done (script in `docs-demo-script.md`)
