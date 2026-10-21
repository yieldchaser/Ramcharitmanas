# -*- coding: utf-8 -*-
"""Render Music-Tracklist-001-<max>.txt as a print-quality A4 PDF.

Why a browser: the list mixes Devanagari and Latin text, and Chrome is the only
renderer on this machine that shapes Devanagari correctly *and* embeds the font.
WeasyPrint is installed but its Pango DLLs are missing, so it cannot run here.

  1. parses the committed .txt (rows + group ranges)
  2. builds a print-only HTML page (repeating table head, no screen chrome)
  3. Chrome headless --print-to-pdf  -> temp PDF
  4. PyMuPDF stamps "page N of M" in the footer, which CSS cannot do in Chrome
  5. writes Music-Tracklist-001-<max>.pdf next to the .txt

Usage:  python tools/pendrive/make_pdf.py
"""
import glob, html, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "ytdl")


def parse_txt(path):
    txt = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n")
    rows, groups, in_groups = [], [], False
    for line in txt.split("\n"):
        r = re.match(r"^(\d{3}) \|\s*([\d:]+) \| (.*)$", line)
        if r:
            n, dur, text = int(r.group(1)), r.group(2), r.group(3).rstrip()
            title, _, artist = text.partition("  -  ")
            rows.append((n, dur, title.strip(), artist.strip()))
            in_groups = False
            continue
        if line.startswith("GROUPS"):
            in_groups = True
            continue
        g = re.match(r"^\s{4,}(\d{3})(?:-(\d{3}))?\s{3}(\S.*)$", line)
        if in_groups and g:
            a = int(g.group(1))
            groups.append((a, int(g.group(2) or a), g.group(3).strip()))
        elif in_groups and line.strip() == "":
            in_groups = False
    return rows, groups


def build_html(rows, groups, maxn, src):
    def rgb(a, b):
        return f"{a:03d}" if a == b else f"{a:03d}–{b:03d}"

    group_of = {}
    for a, b, g in groups:
        for n in range(a, b + 1):
            group_of[n] = g

    body, last = [], None
    for n, dur, title, artist in rows:
        g = group_of.get(n, "")
        if g != last:
            body.append(f'<tr class="grp"><td colspan="3">{html.escape(g)}</td></tr>')
            last = g
        a = f'<span class="ar">{html.escape(artist)}</span>' if artist else ""
        body.append(f'<tr><td class="n">{n:03d}</td><td class="d">{html.escape(dur)}</td>'
                    f'<td>{html.escape(title)}{a}</td></tr>')

    idx = "".join(f"<tr><td class='rn'>{rgb(a, b)}</td><td>{html.escape(g)}</td></tr>"
                  for a, b, g in groups)

    return f"""<!doctype html>
<html lang="hi"><head><meta charset="utf-8">
<title>Pendrive Track List 001–{maxn}</title>
<style>
  @page {{ size: A4; margin: 14mm 12mm 16mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Segoe UI", "Nirmala UI", sans-serif; font-size: 9.4pt;
          color: #111; margin: 0; }}
  h1 {{ font-size: 20pt; margin: 0 0 2mm; color: #7a1f1f; letter-spacing: .2px; }}
  .sub {{ font-size: 10pt; color: #444; margin: 0 0 1mm; }}
  .rule {{ height: 2.2pt; background: #7a1f1f; margin: 3mm 0 4mm; }}
  .how {{ border: .7pt solid #d8cfbe; background: #faf7f0; border-radius: 2mm;
          padding: 3mm 4mm; font-size: 8.9pt; line-height: 1.45; margin: 0 0 4mm; }}
  .how b {{ color: #7a1f1f; }}
  .cap {{ font-size: 7.8pt; text-transform: uppercase; letter-spacing: .8px;
          color: #5a3a12; margin: 0 0 1.5mm; }}
  .idx {{ width: 100%; border-collapse: collapse; font-size: 8.6pt;
          margin: 0 0 5mm; }}
  .idx td {{ padding: .8mm 2mm; border-bottom: .4pt solid #eee; }}
  .idx td.rn {{ font-variant-numeric: tabular-nums; font-weight: 600;
                color: #7a1f1f; white-space: nowrap; width: 22mm; }}
  table.main {{ width: 100%; border-collapse: collapse; font-size: 9.2pt; }}
  table.main thead th {{ text-align: left; font-size: 8.2pt; text-transform: uppercase;
      letter-spacing: .4px; color: #5a3a12; border-bottom: 1.2pt solid #7a1f1f;
      padding: 1.6mm 2mm; }}
  table.main thead {{ display: table-header-group; }}
  table.main tr {{ break-inside: avoid; }}
  table.main td {{ padding: 1.35mm 2mm; border-bottom: .4pt solid #e6e0d2;
      vertical-align: top; }}
  table.main td.n {{ font-weight: 700; color: #7a1f1f; width: 14mm;
      font-variant-numeric: tabular-nums; white-space: nowrap; }}
  table.main td.d {{ width: 18mm; color: #555; font-variant-numeric: tabular-nums;
      white-space: nowrap; }}
  table.main tr:nth-child(even) td {{ background: #fbf9f4; }}
  tr.grp td {{ background: #efe6d3 !important; font-weight: 700; color: #5a3a12;
      font-size: 9.6pt; padding: 2.2mm 2mm 1.6mm; border-bottom: .7pt solid #d8c9a8;
      break-after: avoid; }}
  .ar {{ color: #6b6b6b; }}
  .ar:before {{ content: " — "; }}
  .nw {{ white-space: nowrap; }}
  .foot {{ margin-top: 5mm; font-size: 8pt; color: #666; border-top: .5pt solid #ddd;
           padding-top: 2mm; }}
</style></head><body>
<h1>Pendrive Track List — 001 to {maxn}</h1>
<p class="sub">{maxn} tracks · one flat <code>Music</code> folder on the pendrive · C-28 music speaker</p>
<div class="rule"></div>

<div class="how">
  <b>To play a song by number:</b> press <b>MODE</b> until <b>USB</b> lights on the display,
  then type the three-digit number on the remote (<b class="nw">0 2 5</b>) — press the digits quickly,
  within about a second, or they register as separate jumps. If the player ignores the
  leading zero, type <b>25</b>. A song also plays from the list by using <b>«</b> / <b>»</b>
  to step one track at a time.
  <br><b>Note:</b> 156 old recordings carried no title inside the file; they are listed as
  <i>Untitled recording</i> with their exact length so they can be recognised by duration.
</div>

<div class="cap">Groups</div>
<table class="idx">{idx}</table>

<table class="main">
  <thead><tr><th>No.</th><th>Length</th><th>Track</th></tr></thead>
  <tbody>
{''.join(body)}
  </tbody>
</table>
<div class="foot">Numbers are zero-padded to three digits and the file order matches the
numbers, so the number on the remote is the number in this list. Album tag on every file
is <i>Bhakti Collection</i>; the group name appears in the file name.</div>
</body></html>"""


def render(html_path, pdf_path):
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
           f"--print-to-pdf={pdf_path}", "file:///" + html_path.replace("\\", "/")]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if not os.path.exists(pdf_path):
        raise RuntimeError("chrome produced no PDF:\n" + (p.stderr or "")[-600:])
    return pdf_path


def stamp(pdf_path, label):
    # Helvetica is a WinAnsi font: keep the stamped text pure ASCII or dashes and
    # middle dots come out as mojibake (en dash printed as '\u00b7' on the first run).
    import pymupdf
    doc = pymupdf.open(pdf_path)
    total = doc.page_count
    for i, page in enumerate(doc, 1):
        txt = f"{label}   |   page {i} of {total}"
        size = 7.6
        w = pymupdf.get_text_length(txt, fontname="helv", fontsize=size)
        page.insert_text(((page.rect.width - w) / 2, page.rect.height - 20),
                         txt, fontsize=size, fontname="helv", color=(0.42, 0.42, 0.42))
    doc.set_metadata({"title": f"Pendrive Track List 001-{label[-3:]}",
                      "subject": "C-28 music speaker track list",
                      "author": "Ramcharitmanas repo",
                      "keywords": "pendrive, mp3, tracklist, C-28"})
    doc.saveIncr()
    doc.close()


def main():
    src = sorted(p for p in glob.glob(os.path.join(REPO, "Music-Tracklist-001-*.txt")))
    if not src:
        sys.exit("no Music-Tracklist-001-*.txt found")
    src = src[-1]
    rows, groups = parse_txt(src)
    maxn = max(r[0] for r in rows)
    if len(rows) != maxn:
        sys.exit(f"row count {len(rows)} does not match max number {maxn}")
    os.makedirs(WORK, exist_ok=True)
    html_path = os.path.join(WORK, "tracklist-print.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(build_html(rows, groups, maxn, src))
    out = os.path.join(REPO, f"Music-Tracklist-001-{maxn:03d}.pdf")
    render(html_path, out)
    stamp(out, f"Pendrive track list 001-{maxn}")
    import pymupdf
    d = pymupdf.open(out)
    print(f"wrote {os.path.basename(out)}  ({os.path.getsize(out) / 1024:.0f} KB, "
          f"{d.page_count} pages, {len(rows)} rows, {len(groups)} groups)")
    d.close()


if __name__ == "__main__":
    main()
