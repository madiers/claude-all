#!/usr/bin/env python3
"""Aggregate 14 brand audit JSONs into a single Framer-import batch CSV.

Reads:
  scripts/audit_results/<brand>.json  (per-brand agent output, varying key conventions)

Writes:
  batch_2026-05-29_enrichment.csv     (upsert + new rows for all 14 brands)
  scripts/asset_urls.json             (vendor asset URLs to mirror into the repo)
  scripts/unfindable_report.md        (manual checklist of skipped items)
"""
import csv, json, os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# Canonical Framer column order
HEADER = [
    "Slug", ":draft", "Title", "Sub Title", "Product Description",
    "Technical Table", "Thumbnail", "Thumbnail:alt",
    "Brand", "Product Categories", "Product Tags", "Specsheet", "Gallery",
]

# Key normalization: lowercase + strip whitespace+punct -> canonical Framer column name
KEY_MAP = {
    "slug": "Slug",
    "title": "Title",
    "sub_title": "Sub Title", "subtitle": "Sub Title", "sub title": "Sub Title",
    "product_description": "Product Description", "description": "Product Description",
    "technical_table": "Technical Table",
    "thumbnail": "Thumbnail", "thumbnail_url": "Thumbnail",
    "thumbnail_vendor_url": "Thumbnail", "thumbnailurl": "Thumbnail",
    "brand": "Brand",
    "product_categories": "Product Categories", "categories": "Product Categories",
    "product_tags": "Product Tags", "tags": "Product Tags",
    "specsheet": "Specsheet", "specsheet_url": "Specsheet",
    "specsheet_vendor_url": "Specsheet",
    "gallery": "Gallery", "gallery_urls": "Gallery",
    "gallery_vendor_urls": "Gallery",
}

def normalize_key(k):
    """Lowercase + remove non-alnum, look up in KEY_MAP. Returns None for unknown keys."""
    nk = "".join(c if c.isalnum() else "_" for c in k.lower()).strip("_")
    # collapse underscores
    while "__" in nk: nk = nk.replace("__", "_")
    # try canonical
    if k in HEADER: return k
    if nk in KEY_MAP: return KEY_MAP[nk]
    # try with spaces
    if k.lower() in KEY_MAP: return KEY_MAP[k.lower()]
    return None

def normalize_entry(entry):
    """Convert any agent's dict to canonical Framer keys."""
    out = {}
    for k, v in entry.items():
        if v is None or v == "" or v == []:
            continue
        ck = normalize_key(k)
        if not ck:
            # Unknown field; ignore (likely metadata like 'source_url', 'updates_applied', 'notes')
            continue
        if ck == "Gallery" and isinstance(v, list):
            v = ", ".join(str(x) for x in v if x)
        out[ck] = str(v).strip() if not isinstance(v, str) else v.strip()
    return out

# ============================================================
rows_by_slug = {}   # slug -> normalized row dict
unfindable = []     # list of {brand, slug, fields, note}
asset_urls = defaultdict(dict)   # brand -> { slug: {Thumbnail: url, Specsheet: url, Gallery: [url,...]}}
audit_summary = {}

for fname in sorted(os.listdir('scripts/audit_results')):
    brand = fname.replace('.json','')
    d = json.load(open(f'scripts/audit_results/{fname}'))
    upd_count = new_count = 0

    # Existing updates - Brand stays unchanged (would be ignored anyway by Framer if blank)
    for raw in d.get('existing_updates', []):
        e = normalize_entry(raw)
        slug = e.get('Slug')
        if not slug: continue
        # Always include brand for safety on upsert
        e.setdefault('Brand', brand)
        # Don't include :draft for updates (Framer keeps existing value if blank)
        # Capture asset URLs for the mirror step
        au = asset_urls[brand].setdefault(slug, {})
        if 'Thumbnail' in e: au['Thumbnail'] = e['Thumbnail']
        if 'Specsheet' in e: au['Specsheet'] = e['Specsheet']
        if 'Gallery' in e:
            au['Gallery'] = [u.strip() for u in e['Gallery'].split(',') if u.strip()]
        rows_by_slug[slug] = e
        upd_count += 1

    # New products - need :draft=true and full content
    for raw in d.get('new_products', []):
        e = normalize_entry(raw)
        slug = e.get('Slug')
        if not slug: continue
        e['Brand'] = brand          # force brand correctness
        e[':draft'] = 'true'
        au = asset_urls[brand].setdefault(slug, {})
        if 'Thumbnail' in e: au['Thumbnail'] = e['Thumbnail']
        if 'Specsheet' in e: au['Specsheet'] = e['Specsheet']
        if 'Gallery' in e:
            au['Gallery'] = [u.strip() for u in e['Gallery'].split(',') if u.strip()]
        rows_by_slug[slug] = e
        new_count += 1

    # Unfindable -> manual checklist
    for u in d.get('unfindable', []):
        unfindable.append({
            'brand': brand,
            'slug': u.get('slug',''),
            'fields': u.get('fields', []),
            'note': u.get('note', ''),
        })

    audit_summary[brand] = (upd_count, new_count, len(d.get('unfindable',[])))

# ============================================================
# Write the enrichment CSV
out_csv = 'batch_2026-05-29_enrichment.csv'
with open(out_csv, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(HEADER)
    for slug in sorted(rows_by_slug):
        e = rows_by_slug[slug]
        row = [e.get(h, '') for h in HEADER]
        w.writerow(row)

# ============================================================
# Write asset URL map for the next (mirror) step
with open('scripts/asset_urls.json', 'w') as f:
    json.dump(asset_urls, f, indent=2, sort_keys=True)

# ============================================================
# Write unfindable report
with open('scripts/unfindable_report.md', 'w') as f:
    f.write("# Unfindable items — manual handling needed\n\n")
    f.write(f"Total: {len(unfindable)} items across {len({u['brand'] for u in unfindable})} brands\n\n")
    by_brand = defaultdict(list)
    for u in unfindable: by_brand[u['brand']].append(u)
    for brand in sorted(by_brand):
        f.write(f"## {brand}\n\n")
        f.write("| Slug | Missing fields | Note |\n|---|---|---|\n")
        for u in by_brand[brand]:
            fields = ", ".join(u['fields']) if u['fields'] else "(unknown)"
            note = u['note'].replace('|','\\|').replace('\n',' ')
            f.write(f"| `{u['slug']}` | {fields} | {note} |\n")
        f.write("\n")

# ============================================================
print(f"=== AGGREGATION SUMMARY ===\n")
print(f"{'BRAND':<22} {'UPDATES':>8} {'NEW':>5} {'UNFIND':>7}")
total_u = total_n = total_unf = 0
for b in sorted(audit_summary):
    u, n, unf = audit_summary[b]
    print(f"{b:<22} {u:>8} {n:>5} {unf:>7}")
    total_u += u; total_n += n; total_unf += unf
print(f"{'TOTAL':<22} {total_u:>8} {total_n:>5} {total_unf:>7}")
print()
print(f"Wrote {out_csv} with {len(rows_by_slug)} rows")
print(f"Wrote scripts/asset_urls.json")
print(f"Wrote scripts/unfindable_report.md")

# Validation
with open(out_csv) as f: rows = list(csv.reader(f))
print(f"\nCSV validation:")
print(f"  total rows (excl hdr): {len(rows)-1}")
print(f"  brands represented: {len(set(r[8] for r in rows[1:] if r[8]))}")
specsheet_filled = sum(1 for r in rows[1:] if r[11])
thumb_filled = sum(1 for r in rows[1:] if r[6])
print(f"  with Specsheet: {specsheet_filled}")
print(f"  with Thumbnail: {thumb_filled}")
draft_count = sum(1 for r in rows[1:] if r[1] == 'true')
print(f"  :draft=true (new products): {draft_count}")
print(f"  :draft empty (updates):     {len(rows)-1-draft_count}")
