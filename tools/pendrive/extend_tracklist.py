# -*- coding: utf-8 -*-
"""Extend the pendrive track list after new numbered tracks are added.

The list is normally produced by `make_tracklist.py`, which needs `plan.json`
(a Temp intermediate). Once the drive is authoritative this script rebuilds both
formats straight from `D:\\Music`, so appending 400, 401, ... never means re-running
the whole rebuild kit:

  1. reads the current committed list (001-<old>) and keeps its rows verbatim
  2. reads the new numbers off the drive (title, artist, length)
  3. writes Music-Tracklist-001-<new>.txt + .html, removes the old pair
  4. renames the HTML search box / headers to the new maximum

Usage:  python tools/pendrive/extend_tracklist.py "Vivah Gari Geet"
"""
import os, re, sys, html, glob

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from mutagen.mp3 import MP3

ROOT = r"D:\Music"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def hms(sec):
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def drive_rows():
    """{n: (filename, title, artist, duration)} straight off the pendrive."""
    out = {}
    for f in os.listdir(ROOT):
        if not f.lower().endswith(".mp3"):
            continue
        m = re.match(r"^(\d{3}) - ", f)
        if not m:
            continue
        n = int(m.group(1))
        st = MP3(os.path.join(ROOT, f))
        t = st.tags or {}
        title = str(t.get("TIT2", "")).strip() or os.path.splitext(f)[0][6:]
        title = re.sub(r"^\d{3}\s*-\s*", "", title)
        artist = str(t.get("TPE1", "")).strip()
        out[n] = (f, title, artist, st.info.length)
    return out


def parse_txt(path):
    """Rows and group blocks from the committed list."""
    rows, groups, maxn = [], [], 0
    txt = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n")
    for line in txt.split("\n"):
        r = re.match(r"^(\d{3}) \|\s*([\d:]+) \| (.*)$", line)
        if r:
            rows.append((int(r.group(1)), r.group(2), r.group(3).rstrip()))
            maxn = max(maxn, int(r.group(1)))
            continue
        g = re.match(r"^\s{4,}(\d{3})(?:-(\d{3}))?\s{3}(\S.*)$", line)
        if g and "|" not in line and not line.strip().startswith(("1.", "2.", "3.")):
            a = int(g.group(1)); b = int(g.group(2) or a)
            groups.append([a, b, g.group(3).strip()])
    return rows, groups, maxn


def range_line(a, b):
    return f"{a:03d}" if a == b else f"{a:03d}-{b:03d}"


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "New Downloads"
    old = sorted(glob.glob(os.path.join(REPO, "Music-Tracklist-001-*.txt")))
    old = [p for p in old if not p.endswith(".html")]
    if not old:
        sys.exit("no existing Music-Tracklist-001-*.txt to extend")
    old_txt = old[-1]
    rows, groups, old_max = parse_txt(old_txt)

    d = drive_rows()
    new_max = max(d)
    missing = [n for n in range(1, new_max + 1) if n not in d]
    if missing:
        sys.exit(f"drive is missing numbers: {missing[:10]}")
    if new_max <= old_max:
        print(f"nothing to add (drive max {new_max}, list max {old_max})")
        return
    rows = [r for r in rows if r[0] <= old_max]

    def row_text(title, artist):
        t = "Untitled recording" if title.lower().startswith("untitled") else title
        a = "" if artist in ("", "Various Artists") else f"  -  {artist}"
        return f"{t}{a}"

    extra = []
    for n in range(old_max + 1, new_max + 1):
        _, title, artist, dur = d[n]
        extra.append((n, hms(dur), row_text(title, artist)))

    groups = [g for g in groups if g[1] <= old_max]
    groups.append([old_max + 1, new_max, group])

    title_line = f"PENDRIVE TRACK LIST  -  {new_max} TRACKS  -  NUMBERS 001 TO {new_max}"
    header = [
        title_line,
        "=" * len(title_line),
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
    header += [f"  {range_line(a, b):>11}   {g}" for a, b, g in groups]
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

    lines, last = [], None
    for n, h, text in rows + extra:
        g = next(g for a, b, g in groups if a <= n <= b)
        if g != last:
            lines += ["", f"--- {g} ---"]
            last = g
        lines.append(f"{n:03d} | {h:>8} | {text}")

    new_txt = old_txt.replace(f"001-{old_max:03d}.txt", f"001-{new_max:03d}.txt")
    if new_txt == old_txt:
        new_txt = os.path.join(REPO, f"Music-Tracklist-001-{new_max:03d}.txt")
    with open(new_txt, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("\r\n".join(header + lines) + "\r\n")

    # ---------------- HTML ----------------
    all_rows = rows + extra
    trs, last = [], None
    for n, h, text in all_rows:
        g = next(g for a, b, g in groups if a <= n <= b)
        if g != last:
            trs.append(f'<tr class="grp"><td colspan="3">{html.escape(g)}</td></tr>')
            last = g
        title, _, artist = text.partition("  -  ")
        a_html = f' <span class="a">— {html.escape(artist)}</span>' if artist else ""
        trs.append(f'<tr><td class="n">{n:03d}</td><td class="t">{html.escape(h)}</td>'
                   f'<td>{html.escape(title)}{a_html}</td></tr>')

    groups_html = "".join(f"<li><b>{range_line(a, b)}</b> — {html.escape(g)}</li>"
                          for a, b, g in groups)
    html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pendrive Track List 001-{new_max}</title>
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
<header><h1>Pendrive track list — {new_max} tracks</h1>
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
    new_html = new_txt[:-4] + ".html"
    with open(new_html, "w", encoding="utf-8") as fh:
        fh.write(html_doc)

    for stale in glob.glob(os.path.join(REPO, f"Music-Tracklist-001-{old_max:03d}.*")):
        if os.path.abspath(stale) not in (os.path.abspath(new_txt), os.path.abspath(new_html)):
            os.remove(stale)
            print("removed old", os.path.basename(stale))
    print("wrote", os.path.basename(new_txt), os.path.getsize(new_txt), "bytes")
    print("wrote", os.path.basename(new_html), os.path.getsize(new_html), "bytes")
    print(f"rows: {len(all_rows)} | added {old_max + 1}-{new_max} as '{group}'")


if __name__ == "__main__":
    main()
