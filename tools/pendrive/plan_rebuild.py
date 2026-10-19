# -*- coding: utf-8 -*-
import os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"D:\Music"
probe = json.load(open('probe_tags.json', encoding='utf-8'))
def num_of(f):
    return int(re.match(r'^(\d+)', f).group(1))
by_num = {num_of(f): f for f in probe}
assert len(by_num) == 399, len(by_num)

GROUPS = {'Chaiti','Kajri','Jhumar','Hori','Phag','Rajan Ji Maharaj','Rambhadracharya',
          'Ramnandacharya','Swami Raghvacharya','Madhushala'}
JUNK = re.compile(r'^(untitled|track\s*\d+|audio|mp3|song|unknown|na|n/?a)$', re.I)

def clean_title(s):
    if not s: return ''
    s = str(s)
    s = s.replace('\x00','')
    s = re.sub(r'[|｜]', ' - ', s)
    s = re.sub(r'\(\s*raag\.?fm\s*\)', '', s, flags=re.I)
    s = re.sub(r'raag\.?fm', '', s, flags=re.I)
    s = re.sub(r'(\s*-\s*)+', ' - ', s)
    s = re.sub(r'[<>:"/\?*]', ' ', s)
    s = re.sub(r'[\x00-\x1f\x7f]', ' ', s)
    s = re.sub(r'[\U00010000-\U0010ffff]', '', s)   # emoji / non-BMP
    s = re.sub(r'\s+', ' ', s).strip(' .-')
    return s

rows = []
for n in range(1, 400):
    f = by_num[n]
    stem = os.path.splitext(f)[0]
    p = probe[f]
    tags = p['tags']
    t = clean_title(tags.get('title',''))
    if not t or JUNK.match(t):
        t = ''
    rest = re.sub(r'^\d+\s*[-–]?\s*', '', stem).strip()
    group = 'Old Collection'
    if n >= 278 and ' - ' in rest:
        tail = rest.rsplit(' - ',1)[1].strip()
        if tail in GROUPS:
            group = tail
            rest = rest.rsplit(' - ',1)[0].strip()
        else:
            group = 'New Downloads'
    elif n >= 278:
        group = 'New Downloads'
    if not t:
        t = rest if rest and not JUNK.match(rest) else ''
    title = t or 'Untitled'
    if not t:
        d = p['dur']; title = f"Untitled ({d//60}m{d%60:02d}s)"
    title = title[:80].strip(' .-')
    fname = f"{n:03d} - {title}.mp3"
    artist = clean_title(tags.get('artist','')) or 'Various Artists'
    rows.append((n, fname, title, artist, group, p['dur'], p['codec']))

# checks
names = [r[1] for r in rows]
print("rows:", len(rows), "| unique filenames:", len(set(names)))
bad = [x for x in names if len(x) > 120]
print("names >120 chars:", len(bad), bad[:3])
print("untitled:", sum(1 for r in rows if r[2].startswith('Untitled')))
print("transcodes:", sum(1 for r in rows if r[6] != 'mp3'))
print("\n--- first 20 ---")
for r in rows[:20]: print(r[0], '|', r[1], '|', r[6], '|', r[4])
print("\n--- 270-285 ---")
for r in rows[269:285]: print(r[0], '|', r[1], '|', r[6], '|', r[4])
print("\n--- last 5 ---")
for r in rows[-5:]: print(r[0], '|', r[1], '|', r[6], '|', r[4])
json.dump([{'n':n,'file':f,'title':t,'artist':a,'group':g,'dur':d,'codec':c} for n,f,t,a,g,d,c in rows],
          open('plan.json','w',encoding='utf-8'), ensure_ascii=False, indent=0)
