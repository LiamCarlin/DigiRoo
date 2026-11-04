#!/usr/bin/env python3
"""
package_skills.py — sync shared files and rebuild dist/ (skill zips + Project knowledge).

    python3 tools/package_skills.py

1. Copies the canonical video rules (skills/digiroo-video/references/video-rules.md) into
   skills/content-week/references/ and dist/project-knowledge/, and the shoot-card template into templates/,
   so each uploaded skill zip is self-contained.
2. Rebuilds dist/project-knowledge/templates-all.md from templates/*.md and refreshes the instruction,
   rules, notes and trends files there.
3. Zips every skills/<name>/ into dist/skills/<name>.zip and removes zips of skills that no longer exist.
Run it after changing anything under skills/ or templates/.
"""
import os, shutil, zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
J = lambda *p: os.path.join(ROOT, *p)
RULES = J("skills", "digiroo-video", "references", "video-rules.md")
SYNCED = "<!-- synced copy of skills/digiroo-video/references/video-rules.md by tools/package_skills.py; edit that file -->\n"

def sync():
    rules = open(RULES, encoding="utf-8").read()
    for dst in (J("skills", "content-week", "references", "video-rules.md"), J("dist", "project-knowledge", "video-rules.md")):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "w", encoding="utf-8").write(SYNCED + rules)
    shutil.copyfile(J("skills", "digiroo-video", "templates", "shoot-card.md"), J("templates", "shoot-card.md"))
    parts = []
    for name in sorted(os.listdir(J("templates"))):
        if name.endswith(".md"):
            parts.append(f"\n\n---\n# templates/{name}\n\n" + open(J("templates", name), encoding="utf-8").read())
    open(J("dist", "project-knowledge", "templates-all.md"), "w", encoding="utf-8").write("".join(parts))
    for f in ("project-instructions.md", "video-notes.md", "trends.md", "format-library.md"):
        if os.path.exists(J(f)):
            shutil.copyfile(J(f), J("dist", "project-knowledge", f))

def zip_skills():
    out = J("dist", "skills"); os.makedirs(out, exist_ok=True)
    names = sorted(n for n in os.listdir(J("skills")) if os.path.exists(J("skills", n, "SKILL.md")))
    for z in os.listdir(out):
        if z.endswith(".zip") and z[:-4] not in names:
            os.remove(os.path.join(out, z)); print(f"removed dist/skills/{z} (skill no longer exists)")
    for n in names:
        path = os.path.join(out, n + ".zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for base, dirs, files in os.walk(J("skills", n)):
                dirs[:] = sorted(d for d in dirs if d != "__pycache__")
                for f in sorted(files):
                    if f == ".DS_Store" or f.endswith(".pyc"):
                        continue
                    full = os.path.join(base, f)
                    z.write(full, os.path.relpath(full, J("skills")))
        print(f"dist/skills/{n}.zip  {os.path.getsize(path) // 1024} KB")

if __name__ == "__main__":
    sync()
    zip_skills()
