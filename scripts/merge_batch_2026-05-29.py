#!/usr/bin/env python3
"""Merge skeleton CSV with research JSON into the final Framer batch CSV.

Reads:
  batch_2026-05-29_skeleton.csv      (slug, brand, thumbnail/gallery URLs)
  scripts/research_mag.json
  scripts/research_krix.json

Writes:
  batch_2026-05-29.csv               (final Framer-ready file)
"""
import csv, json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

research = {}
for src in ['scripts/research_mag.json', 'scripts/research_krix.json']:
    with open(src) as f:
        for entry in json.load(f):
            research[entry['slug']] = entry

with open('batch_2026-05-29_skeleton.csv') as f:
    rows = list(csv.reader(f))
header = rows[0]
ci = {name: i for i, name in enumerate(header)}

out_rows = [header]
missing = []
for r in rows[1:]:
    slug = r[ci['Slug']]
    if slug == 'arts':
        continue
    rd = research.get(slug)
    if not rd:
        missing.append(slug)
        out_rows.append(r)
        continue
    r[ci['Title']] = rd.get('title', r[ci['Title']])
    r[ci['Sub Title']] = rd.get('sub_title', r[ci['Sub Title']])
    r[ci['Product Description']] = rd.get('description', '')
    r[ci['Technical Table']] = rd.get('technical_table', '')
    r[ci['Product Categories']] = rd.get('product_categories', '')
    r[ci['Product Tags']] = rd.get('product_tags', '')
    r[ci['Specsheet']] = rd.get('specsheet_url', '')
    r[ci['Thumbnail:alt']] = rd.get('title', r[ci['Thumbnail:alt']])
    out_rows.append(r)

with open('batch_2026-05-29.csv', 'w', newline='') as f:
    csv.writer(f).writerows(out_rows)

print(f"Wrote batch_2026-05-29.csv with {len(out_rows)-1} rows")
if missing:
    print(f"!! Missing research for: {missing}")

# Validation
with open('batch_2026-05-29.csv') as f:
    final = list(csv.reader(f))
slugs = [r[0] for r in final[1:]]
print(f"\nValidation:")
print(f"  rows (excl header): {len(final)-1}")
print(f"  distinct slugs:     {len(set(slugs))}")
print(f"  duplicate slugs:    {[s for s, c in Counter(slugs).items() if c > 1]}")
for col in ['Product Description', 'Technical Table', 'Thumbnail', 'Brand']:
    empties = [r[0] for r in final[1:] if not r[ci[col]]]
    print(f"  empty {col}: {len(empties)} {empties[:5]}")
entities = [r[0] for r in final[1:] if '&lt;' in r[ci['Product Description']]]
print(f"  rows with &lt; in description: {len(entities)} {entities}")
print(f"  brand counts: {Counter(r[ci['Brand']] for r in final[1:])}")
print(f"  specsheet present: {sum(1 for r in final[1:] if r[ci['Specsheet']])}/{len(final)-1}")
print(f"  category counts: {Counter(r[ci['Product Categories']] for r in final[1:])}")
