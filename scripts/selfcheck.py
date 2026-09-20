#!/usr/bin/env python3
"""Static self-check for the HyperFrames slideshow deck:
1. island JSON parses; slide sceneIds resolve to real data-composition-id scenes
2. fragment times fall within each slide's [start, end]
3. wrapper island is in sync with the composition island
4. hotspot targets resolve to slideSequences ids; branch scenes not in main line
5. no time overlap between main-line slides
6. inline <script> bodies pass `node --check`
"""
import json
import re
import subprocess
import sys
import tempfile
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(ROOT, "..", "composition", "index.html")
WRAP = os.path.join(ROOT, "..", "index.html")

ISLAND_RE = re.compile(
    r'<script type="application/hyperframes-slideshow\+json">(.*?)</script>', re.S
)
SCENE_RE = re.compile(
    r'data-composition-id="([^"]+)"\s+data-start="(\d+)"\s+data-duration="(\d+)"'
)

errors = []
warns = []


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


comp_html = load(COMP)
wrap_html = load(WRAP)

comp_islands = ISLAND_RE.findall(comp_html)
wrap_islands = ISLAND_RE.findall(wrap_html)
if len(comp_islands) != 1:
    errors.append(f"composition island count = {len(comp_islands)}, expected 1")
if len(wrap_islands) != 1:
    errors.append(f"wrapper island count = {len(wrap_islands)}, expected 1")

comp_island = json.loads(comp_islands[0])
wrap_island = json.loads(wrap_islands[0])

if comp_island != wrap_island:
    errors.append("wrapper island is OUT OF SYNC with composition island")

# scenes declared in composition (skip the root wrapper)
scenes = {}
for cid, start, dur in SCENE_RE.findall(comp_html):
    if cid == "root":
        continue
    scenes[cid] = (int(start), int(dur))

print(f"scenes declared: {len(scenes)}")
for cid, (s, d) in scenes.items():
    print(f"  {cid:14s} start={s:3d} duration={d}")

main_slides = comp_island.get("slides", [])
seqs = comp_island.get("slideSequences", [])
seq_ids = {s["id"] for s in seqs}
branch_scene_ids = {sl["sceneId"] for sq in seqs for sl in sq["slides"]}

# 1. sceneId resolution
for sl in main_slides:
    sid = sl["sceneId"]
    if sid not in scenes:
        errors.append(f"main slide sceneId '{sid}' has no matching scene")
for sq in seqs:
    for sl in sq["slides"]:
        if sl["sceneId"] not in scenes:
            errors.append(f"branch slide sceneId '{sl['sceneId']}' has no matching scene")

# 2. fragments within [start, end]
for sl in main_slides:
    sid = sl["sceneId"]
    if sid not in scenes:
        continue
    start, dur = scenes[sid]
    end = start + dur
    for t in sl.get("fragments", []):
        if t < start or t > end:
            errors.append(f"fragment {t} of '{sid}' outside [{start},{end}]")
for sq in seqs:
    for sl in sq["slides"]:
        sid = sl["sceneId"]
        if sid not in scenes:
            continue
        start, dur = scenes[sid]
        end = start + dur
        for t in sl.get("fragments", []):
            if t < start or t > end:
                errors.append(f"branch fragment {t} of '{sid}' outside [{start},{end}]")

# 3. hotspot targets
for sl in main_slides:
    for h in sl.get("hotspots", []):
        if h["target"] not in seq_ids:
            errors.append(f"hotspot '{h['id']}' targets unknown sequence '{h['target']}'")
        for k in ("x", "y", "w", "h"):
            v = h.get("region", {}).get(k)
            if v is not None and not (0 <= v <= 100):
                errors.append(f"hotspot '{h['id']}' region {k}={v} outside 0-100")

# 4. branch scenes must not appear in main line
main_ids = {sl["sceneId"] for sl in main_slides}
overlap = main_ids & branch_scene_ids
if overlap:
    errors.append(f"branch scenes also in main line: {sorted(overlap)}")

# 5. main-line time overlap
ranges = sorted((scenes[sid] if sid in scenes else None, sid) for sid in main_ids)
prev_end = -1
prev_sid = None
ordered = []
for sl in main_slides:
    sid = sl["sceneId"]
    if sid in scenes:
        ordered.append((scenes[sid][0], scenes[sid][0] + scenes[sid][1], sid))
ordered.sort()
for s, e, sid in ordered:
    if s < prev_end:
        errors.append(f"main-line slide '{sid}' overlaps '{prev_sid}'")
    prev_end, prev_sid = e, sid

# 6. total root duration covers all scenes
max_end = max(s + d for s, d in scenes.values())
m = re.search(r'data-composition-id="root"[^>]*data-duration="(\d+)"', comp_html)
root_dur = int(m.group(1)) if m else -1
if root_dur < max_end:
    errors.append(f"root duration {root_dur} < last scene end {max_end}")

# 7. node --check on every inline script (skip src= and json islands)
SCRIPT_RE = re.compile(r"<script(?![^>]*\bsrc=)(?![^>]*type=\"application/hyperframes-slideshow\+json\")(?![^>]*type=\"application/json\")([^>]*)>(.*?)</script>", re.S)
tmp = tempfile.mkdtemp()
n = 0
for path in (COMP, WRAP):
    html = load(path)
    for attrs, body in SCRIPT_RE.findall(html):
        if not body.strip():
            continue
        n += 1
        f = os.path.join(tmp, f"inline_{n}.js")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(body)
        r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"node --check failed for inline script #{n} in {os.path.basename(os.path.dirname(path))}/{os.path.basename(path)}:\n{r.stderr.strip()}")

# 8. every .frag element in composition has an island fragment entry (won't show otherwise)
frag_els = set(re.findall(r'class="[^"]*\bfrag\b[^"]*"[^>]*id="([^"]+)"', comp_html))
frag_els |= set(re.findall(r'id="([^"]+)"[^>]*class="[^"]*\bfrag\b', comp_html))
island_frag_els = set()
for sl in main_slides:
    for t in sl.get("fragments", []):
        island_frag_els.add(t)
# map: find ids whose FRAGMENTS table references them
fr_table = re.findall(r'\{ t: ([\d.]+), el: "([^"]+)" \}', comp_html)
table_ids = {eid for _, eid in fr_table}
island_times = sorted(float(t) for sl in main_slides for t in sl.get("fragments", []))
table_times = sorted(float(t) for t, _ in fr_table)
if island_times != table_times:
    errors.append(f"FRAGMENTS table times {table_times} != island times {island_times}")
missing_reveal = frag_els - table_ids
if missing_reveal:
    errors.append(f".frag elements without root-timeline reveal: {sorted(missing_reveal)}")
extra = table_ids - frag_els
if extra:
    warns.append(f"FRAGMENTS table references non-.frag ids: {sorted(extra)}")

# 9. images referenced exist
for img in set(re.findall(r'src="\.\./assets/([^"]+)"', comp_html)):
    p = os.path.join(ROOT, "..", "assets", img)
    if not os.path.isfile(p):
        errors.append(f"missing asset: assets/{img}")

print()
for w in warns:
    print("WARN:", w)
if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("ALL CHECKS PASSED "
      f"({len(main_slides)} main slides, {len(seqs)} sequences, "
      f"{sum(len(s.get('fragments', [])) for s in main_slides)} fragments, "
      f"{n} inline scripts node-checked)")
