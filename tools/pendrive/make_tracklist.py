# -*- coding: utf-8 -*-
"""Generate the 001-399 pendrive track list (TXT + printable HTML)."""
import os, sys, json, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from mutagen.mp3 import MP3

OUT = r"D:\Music"
PLAN = r"C:\Users\Dell\AppData\Local\Temp\ytdl\plan.json"
REPO = r"C:\Users\Dell\Github\Ramcharitmanas"
plan = json.load(open(PLAN, encoding="utf-8"))
by_n = {p["n"]: p for p in plan}

def hms(sec):
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

rows = []
for n in range(1, 400):
    p = by_n[n]
    f = p["file"]
    path = os.path.join(OUT, f)
    dur = MP3(path).info.length
    rows.append({"n": n, "file": f, "title": p["title"], "artist": p["artist"],
                 "group": p["group"], "dur": dur, "hms": hms(dur)})

# group ranges
ranges = []
for r in rows:
    if ranges and ranges[-1][2] == r["group"]:
        ranges[-1][1] = r["n"]
    else:
        ranges.append([r["n"], r["n"], r["group"]])
range_line = lambda a, b: f"{a:03d}" if a == b else f"{a:03d}-{b:03d}"

header = [
    "PENDRIVE TRACK LIST  -  399 TRACKS  -  NUMBERS 001 TO 399",
    "==========================================================",
    "",
    "Every file is a real MP3, named with its number, and stored in the",
    "'Music' folder on the pen drive.  The number in this list is the",
    "number the player shows.",
    "",
    "TO PLAY A SONG BY NUMBER",
    "  1. Press MODE until USB (or SD) is selected.",
    "  2. Type the three-digit number on the remote, e.g. 0 2 5.",
    "  3. Press the play button (or wait for the player to jump).",
    "  If the player ignores the leading zero, type 25 instead of 025.",
    "",
    "GROUPS",
]
for a, b, g in ranges:
    header.append(f"  {range_line(a,b):>11}   {g}")
header += [
    "",
    "NOTE: 156 old recordings had no song name inside the file.  They are",
    "listed as 'Untitled recording' with their exact length, so the person",
    "helping can recognise them by duration.  The number still works.",
    "",
    "",
    "NO. | LENGTH   | TRACK",
    "----+----------+--------------------------------------------------------",
]

lines = []
last_group = None
for r in rows:
    if r["group"] != last_group:
        lines.append("")
        lines.append(f"--- {r['group']} ---")
        last_group = r["group"]
    name = r["title"]
    if name.startswith("Untitled"):
        name = "Untitled recording"
    artist = "" if r["artist"] in ("Various Artists", "") else f"  -  {r['artist']}"
    lines.append(f"{r['n']:03d} | {r['hms']:>8} | {name}{artist}")

text = "\r\n".join(header + lines) + "\r\n"

# Repo only - the pendrive holds nothing but the Music folder.
for dest in [os.path.join(REPO, "Music-Tracklist-001-399.txt")]:
    with open(dest, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write(text)
    print("wrote", dest, os.path.getsize(dest), "bytes")

# ---------------- HTML ----------------
trs = []
last_group = None
for r in rows:
    if r["group"] != last_group:
        trs.append(f'<tr class="grp"><td colspan="3">{html.escape(r["group"])}</td></tr>')
        last_group = r["group"]
    name = "Untitled recording" if r["title"].startswith("Untitled") else r["title"]
    artist = "" if r["artist"] in ("Various Artists", "") else f' <span class="a">— {html.escape(r["artist"])}</span>'
    trs.append(f'<tr><td class="n">{r["n"]:03d}</td><td class="t">{html.escape(r["hms"])}</td>'
               f'<td>{html.escape(name)}{artist}</td></tr>')

groups_html = "".join(f"<li><b>{range_line(a,b)}</b> — {html.escape(g)}</li>" for a, b, g in ranges)
html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pendrive Track List 001-399</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:0;background:#faf7f0;color:#1d1d1d}}
header{{position:sticky;top:0;background:#7a1f1f;color:#fff;padding:14px 18px;z-index:2}}
h1{{margin:0;font-size:20px}} header p{{margin:6px 0 10px;font-size:14px;opacity:.95}}
input{{width:100%;box-sizing:border-box;font-size:18px;padding:10px 12px;border-radius:8px;border:0}}
main{{max-width:900px;margin:0 auto;padding:16px}}
table{{width:100%;border-collapse:collapse;font-size:16px}}
th,td{{padding:7px 8px;border-bottom:1px solid #e3dccd;vertical-align:top}}
td.n{{font-weight:700;white-space:nowrap;font-variant-numeric:tabular-nums;color:#7a1f1f}}
td.t{{white-space:nowrap;color:#555;font-variant-numeric:tabular-nums}}
tr.grp td{{background:#efe6d3;font-weight:700;color:#5a3a12;padding:10px 8px}}
.a{{color:#666}} .note{{background:#fff;border:1px solid #e3dccd;border-radius:8px;padding:12px;margin:14px 0;font-size:14px;line-height:1.5}}
ul{{columns:2;font-size:14px}} @media(max-width:600px){{ul{{columns:1}}}}
</style></head><body>
<header><h1>Pendrive track list — 399 tracks</h1>
<p>Type the 3-digit number on the remote, e.g. 0 2 5, then play.</p>
<input id="q" placeholder="Search a number or a name…" autocomplete="off"></header>
<main>
<div class="note"><b>How to play:</b> press MODE until USB is selected, type the three-digit number (025), then press play.
If the player ignores the leading zero, type 25. 156 old recordings have no embedded title; they are listed as
<i>Untitled recording</i> with their exact length so they can be recognised by duration.</div>
<ul>{groups_html}</ul>
<table id="t"><thead><tr><th>No.</th><th>Length</th><th>Track</th></tr></thead>
<tbody>{''.join(trs)}</tbody></table>
</main>
<script>
const q=document.getElementById('q'),rows=[...document.querySelectorAll('#t tbody tr')];
q.addEventListener('input',()=>{{const v=q.value.trim().toLowerCase();
rows.forEach(r=>{{r.style.display=!v||r.textContent.toLowerCase().includes(v)?'':'none';}});}});
</script></body></html>"""
for dest in [os.path.join(REPO, "Music-Tracklist-001-399.html")]:
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(html_doc)
    print("wrote", dest, os.path.getsize(dest), "bytes")
