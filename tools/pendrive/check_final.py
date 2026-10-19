# -*- coding: utf-8 -*-
"""Verify the generated 001-399 tracklist against plan.json."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

plan = json.load(open(r"C:\Users\Dell\AppData\Local\Temp\ytdl\plan.json", encoding="utf-8"))
by = {p["n"]: p for p in plan}
TXT = r"C:\Users\Dell\Github\Ramcharitmanas\Music-Tracklist-001-399.txt"
txt = open(TXT, encoding="utf-8-sig").read().splitlines()

rows = {}
for L in txt:
    m = re.match(r"^(\d{3}) \|\s*([\d:]+)\s*\| (.+)$", L)
    if not m:
        continue
    n = int(m.group(1))
    parts = [int(x) for x in m.group(2).split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
    rows[n] = (sec, m.group(3))

print("rows parsed:", len(rows))
print("numbers 1..399 complete:", sorted(rows) == list(range(1, 400)))
missing = [n for n in range(1, 400) if n not in rows]
print("missing:", missing[:10])

diffs = []
for n, (sec, rest) in rows.items():
    d = abs(sec - by[n]["dur"])
    if d > 2:
        diffs.append((n, sec, round(by[n]["dur"], 1), rest[:50]))
print("duration mismatches >2s:", len(diffs))
for x in diffs[:10]:
    print("  ", x)

bad = []
for n, (sec, rest) in rows.items():
    t = by[n]["title"]
    if t.startswith("Untitled"):
        if not rest.startswith("Untitled recording"):
            bad.append((n, rest[:40]))
    elif not rest.startswith(t[:20]):
        bad.append((n, rest[:45], t[:45]))
print("title mismatches:", len(bad))
for x in bad[:8]:
    print("  ", x)

print("total hours in list:", round(sum(v[0] for v in rows.values()) / 3600, 1))
