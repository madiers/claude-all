#!/usr/bin/env python3
"""Rewrite batch_2026-05-29_enrichment.csv:
- Replace vendor Specsheet / Thumbnail / Gallery URLs with raw.githubusercontent.com
  URLs to the mirrored copies under Assets/<brand>/<slug>/.
- Drop URLs that didn't successfully mirror (so Framer doesn't store a 404).
"""
import csv, os, urllib.parse, glob, mimetypes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BRANCH = "claude/blissful-cori-JY3Gi"
BASE = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}"

def raw_url(rel):
    return BASE + "/" + urllib.parse.quote(rel, safe="/")

def safe(s):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:200]

def find_local(brand, slug, kind, idx=None):
    """Return repo-relative path of the mirrored file if it exists, else None."""
    folder = f"Assets/{safe(brand)}/{safe(slug)}"
    if not os.path.isdir(folder):
        return None
    if kind == "Specsheet":
        p = f"{folder}/{safe(slug)}_datasheet.pdf"
        return p if os.path.isfile(p) and os.path.getsize(p) > 1024 else None
    if kind == "Thumbnail":
        for ext in (".jpg",".jpeg",".png",".webp",".gif",".svg",".bin"):
            p = f"{folder}/{safe(slug)}_main{ext}"
            if os.path.isfile(p) and os.path.getsize(p) > 100: return p
        return None
    if kind == "Gallery":
        for ext in (".jpg",".jpeg",".png",".webp",".gif",".svg",".bin"):
            p = f"{folder}/{safe(slug)}_gallery_{idx}{ext}"
            if os.path.isfile(p) and os.path.getsize(p) > 100: return p
        return None
    return None

with open("batch_2026-05-29_enrichment.csv") as f:
    rows = list(csv.reader(f))
hdr = rows[0]
ci = {h: i for i, h in enumerate(hdr)}

stats = {"spec_rewritten":0,"spec_dropped":0,"spec_unchanged":0,
         "thumb_rewritten":0,"thumb_dropped":0,"thumb_unchanged":0,
         "gallery_urls_rewritten":0,"gallery_urls_dropped":0,"gallery_rows_changed":0}

for r in rows[1:]:
    slug  = r[ci["Slug"]]
    brand = r[ci["Brand"]]

    # Specsheet
    spec = r[ci["Specsheet"]]
    if spec:
        local = find_local(brand, slug, "Specsheet")
        if local:
            r[ci["Specsheet"]] = raw_url(local)
            stats["spec_rewritten"] += 1
        else:
            r[ci["Specsheet"]] = ""
            stats["spec_dropped"] += 1
    else:
        stats["spec_unchanged"] += 1

    # Thumbnail
    thumb = r[ci["Thumbnail"]]
    if thumb:
        local = find_local(brand, slug, "Thumbnail")
        if local:
            r[ci["Thumbnail"]] = raw_url(local)
            stats["thumb_rewritten"] += 1
        else:
            r[ci["Thumbnail"]] = ""
            stats["thumb_dropped"] += 1
    else:
        stats["thumb_unchanged"] += 1

    # Gallery (comma-separated)
    gallery = r[ci["Gallery"]]
    if gallery:
        urls = [u.strip() for u in gallery.split(",") if u.strip()]
        new = []
        for idx, _u in enumerate(urls, start=1):
            local = find_local(brand, slug, "Gallery", idx)
            if local:
                new.append(raw_url(local))
                stats["gallery_urls_rewritten"] += 1
            else:
                stats["gallery_urls_dropped"] += 1
        if new != urls:
            r[ci["Gallery"]] = ", ".join(new)
            stats["gallery_rows_changed"] += 1

with open("batch_2026-05-29_enrichment.csv","w",newline="") as f:
    csv.writer(f).writerows(rows)

print("Rewrite stats:")
for k, v in sorted(stats.items()):
    print(f"  {k:<28} {v}")

# Validation
with open("batch_2026-05-29_enrichment.csv") as f:
    rows2 = list(csv.reader(f))
spec_g  = sum(1 for r in rows2[1:] if "raw.githubusercontent.com" in r[ci["Specsheet"]])
spec_v  = sum(1 for r in rows2[1:] if r[ci["Specsheet"]] and "raw.githubusercontent.com" not in r[ci["Specsheet"]])
thumb_g = sum(1 for r in rows2[1:] if "raw.githubusercontent.com" in r[ci["Thumbnail"]])
thumb_v = sum(1 for r in rows2[1:] if r[ci["Thumbnail"]] and "raw.githubusercontent.com" not in r[ci["Thumbnail"]])
print(f"\nFinal CSV state:")
print(f"  Specsheet:  github={spec_g}  vendor-left={spec_v}  blank={len(rows2)-1-spec_g-spec_v}")
print(f"  Thumbnail:  github={thumb_g}  vendor-left={thumb_v}  blank={len(rows2)-1-thumb_g-thumb_v}")
