#!/usr/bin/env python3
"""Build Garvan rows for the combined import batch CSV.

Non-destructive upsert: each row is pre-filled from the live Framer export so no
existing field is cleared, then Thumbnail / Gallery / Specsheet are overlaid with
raw.githubusercontent URLs pointing at Assets/garvan-acoustics/<slug>/.
"""
import csv, json, os, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(REPO, "Products_Famer_latest_6-56pm.csv")
MANIFEST = os.path.join(REPO, "scripts", "garvan_manifest.json")
OUT = os.path.join(REPO, "batch_2026-06-08.csv")

BRANCH = "claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}/"
COLS = ['Slug', ':draft', 'Title', 'Sub Title', 'Product Description', 'Technical Table',
        'Thumbnail', 'Thumbnail:alt', 'Brand', 'Product Categories', 'Product Tags',
        'Specsheet', 'Gallery']

def raw_url(slug, fname):
    path = f"Assets/garvan-acoustics/{slug}/{fname}"
    return RAW + urllib.parse.quote(path)  # quote keeps '/', encodes spaces etc.

def is_hosted(u):
    u = (u or "").strip()
    return u.startswith("https://framerusercontent.com/") or u.startswith("https://raw.githubusercontent.com/")

def pick_datasheet(pdfs, slug):
    if not pdfs:
        return None
    # prefer a model datasheet over generic brochures
    pref = [p for p in pdfs if "datasheet" in p.lower()]
    if pref:
        return pref[0]
    pref = [p for p in pdfs if slug.replace("-", "") in p.lower().replace("-", "").replace("_", "")]
    return (pref or pdfs)[0]

def main():
    manifest = json.load(open(MANIFEST))
    live = list(csv.DictReader(open(LIVE, newline="", encoding="utf-8")))
    by_slug = {r["Slug"]: r for r in live if r.get("Brand") == "garvan-acoustics"}

    rows = []
    stats = {"thumb_set": 0, "gallery_set": 0, "spec_set": 0, "no_images": []}
    for slug in sorted(by_slug):
        base = by_slug[slug]
        row = {c: (base.get(c, "") or "") for c in COLS}
        row["Slug"] = slug
        row["Brand"] = "garvan-acoustics"
        m = manifest.get(slug, {"images": [], "pdfs": []})
        imgs = m["images"]
        # Gallery = every optimized photo (manifest order: _01, _02, ...)
        if imgs:
            row["Gallery"] = ", ".join(raw_url(slug, f) for f in imgs)
            stats["gallery_set"] += 1
            # Thumbnail: fill only when missing/unhosted — respect already-curated thumbs
            if not is_hosted(row.get("Thumbnail")):
                row["Thumbnail"] = raw_url(slug, imgs[0])
                stats["thumb_set"] += 1
                if not (row.get("Thumbnail:alt") or "").strip():
                    row["Thumbnail:alt"] = f"{row.get('Title') or slug} — Garvan Acoustics"
        else:
            stats["no_images"].append(slug)
            # keep whatever thumbnail the live export already had
        # Specsheet: keep existing hosted; else use mirrored datasheet PDF
        if not is_hosted(row.get("Specsheet")):
            ds = pick_datasheet(m["pdfs"], slug)
            if ds:
                row["Specsheet"] = raw_url(slug, ds)
                stats["spec_set"] += 1
        rows.append(row)

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {len(rows)} garvan rows -> {os.path.basename(OUT)}")
    print(f"  thumbnails set from gallery: {stats['thumb_set']}")
    print(f"  galleries set:              {stats['gallery_set']}")
    print(f"  specsheets newly set:       {stats['spec_set']}")
    print(f"  no images (thumb untouched): {stats['no_images']}")

if __name__ == "__main__":
    main()
