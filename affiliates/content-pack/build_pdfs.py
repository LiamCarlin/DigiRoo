#!/usr/bin/env python3
"""Fill placeholders and render the parent handout + code card to PDF with headless Chromium.

    python3 affiliates/content-pack/build_pdfs.py affiliates/onboarded/advanced-chiropractic/   # expects clinic.json there
    python3 affiliates/content-pack/build_pdfs.py --sample                                       # sample clinic, writes next to this file
"""
import json, os, re, subprocess, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = {"CLINIC": "Sample Family Chiropractic", "CLINICIAN": "Dr. Sam Example", "HANDLE": "@sampleclinic",
          "CODE": "DRSAMPLE10", "CITY": "Hamilton, Bermuda"}  # fictional; real clinics get their own folder

CSS = """<style>
@page { size: Letter; margin: 18mm; }
body { font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; color: #1c2130; line-height: 1.45; font-size: 12.5pt; }
h1 { font-size: 22pt; margin: 0 0 4px; color: #1f3c88; } h2 { font-size: 13.5pt; margin: 14px 0 2px; color: #1f3c88; }
p { margin: 4px 0 8px; } .sub { color: #555; font-style: italic; font-size: 10.5pt; }
.pick { background: #eef3ff; border-left: 5px solid #1f3c88; padding: 10px 14px; margin-top: 16px; border-radius: 4px; }
.foot { margin-top: 14px; font-size: 10pt; color: #555; border-top: 1px solid #ddd; padding-top: 6px; }
.cards { display: grid; grid-template-columns: repeat(2, 85.6mm); gap: 6mm; }
.card { width: 85.6mm; height: 54mm; border: 1px dashed #aaa; border-radius: 3mm; padding: 6mm; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; }
.card.front { background: #1f3c88; color: white; } .card b.big { font-size: 15pt; } .card .code { font-size: 17pt; font-weight: 700; letter-spacing: 1px; }
.card small { font-size: 8.5pt; opacity: .8; }
</style>"""

def fill(text, ctx):
    ctx = dict(ctx); ctx.setdefault("CITY_TAG", re.sub(r"[^a-z]", "", ctx.get("CITY", "").split(",")[0].lower()))
    return re.sub(r"\{\{(\w+)\}\}", lambda m: ctx.get(m.group(1), m.group(0)), text)

def md_to_html(md):
    out = []
    for line in md.splitlines():
        if line.startswith("# "): out.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "): out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("*") and line.endswith("*") and not line.startswith("**"): out.append(f"<p class='sub'>{line.strip('*')}</p>")
        elif line.strip() == "---": out.append("<div class='pick'>")
        elif line.strip(): out.append(f"<p>{re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)}</p>")
    h = "\n".join(out)
    if "<div class='pick'>" in h:
        parts = h.split("<div class='pick'>"); tail = parts[1].rsplit("<p>", 1)
        h = parts[0] + "<div class='pick'>" + tail[0] + "</div><p class='foot'>" + tail[1]
    return h

def render(html_body, out_pdf):
    html_path = out_pdf[:-4] + ".html"
    open(html_path, "w", encoding="utf-8").write(f"<!doctype html><html><head><meta charset='utf-8'>{CSS}</head><body>{html_body}</body></html>")
    js = f"""const {{ chromium }} = require('playwright');(async()=>{{const b=await chromium.launch({{args:['--no-sandbox']}});const p=await b.newPage();
await p.goto('file://{html_path}');await p.pdf({{path:'{out_pdf}',format:'Letter',printBackground:true}});await b.close();}})();"""
    subprocess.run(["node", "-e", js], check=True)
    return out_pdf

def main():
    if "--sample" in sys.argv:
        ctx, out = SAMPLE, HERE
    else:
        d = sys.argv[1]; ctx = json.load(open(os.path.join(d, "clinic.json"))); out = d
    handout = md_to_html(fill(open(os.path.join(HERE, "parent-handout.md"), encoding="utf-8").read(), ctx))
    render(handout, os.path.join(out, "parent-handout.pdf"))
    e = {k: html.escape(v) for k, v in fill(json.dumps(ctx), ctx) and ctx.items()}
    card = f"""<div class='cards'>""" + "".join(f"""
<div class='card front'><b class='big'>Screen Time, Elevated.</b><span>DigiRoo: the kids' iPad case that lifts the screen to eye level.</span><span class='code'>10% off · {e['CODE']}</span><small>kidsdigitalwellness.com</small></div>
<div class='card'><b>Recommended by {e['CLINIC']}</b><span>{e['CLINICIAN']} · {e['HANDLE']}</span><span>Eyes up, not screen down. 👀</span><small>not medical advice</small></div>""" for _ in range(4)) + "</div>"
    render(card, os.path.join(out, "code-card.pdf"))
    print("wrote", os.path.join(out, "parent-handout.pdf"), "and", os.path.join(out, "code-card.pdf"))

if __name__ == "__main__":
    main()
