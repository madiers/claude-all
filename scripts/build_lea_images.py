#!/usr/bin/env python3
"""Build LEA_Images.csv — galleries only for every LEA product (same shape as
MAG_Images.csv): Slug, Product Description (copied verbatim from the export so
Framer's required-field mapping is satisfied without changing anything), Gallery.

Gallery images are the LEA Professional product renders scraped by
scripts/lea_scrape_vendor.py into Assets/lea/_renders/ and recorded in
scripts/lea_scrape_manifest.json. Served over raw.githubusercontent.
"""
import csv, os, json, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(REPO, "Products_18_june_MAG_Updated.csv")
MAN = json.load(open(os.path.join(REPO, "scripts", "lea_scrape_manifest.json")))
BRANCH = "claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}/"

def raw_url(p):
    return RAW + urllib.parse.quote(p)

def main():
    rows = [r for r in csv.DictReader(open(EXPORT, newline="", encoding="utf-8"))
            if r.get("Brand") == "lea"]
    out, empty = [], []
    for r in rows:
        slug = r["Slug"]
        imgs = MAN.get(slug, [])
        if not imgs:
            empty.append(slug); continue
        out.append({"Slug": slug,
                    "Product Description": r.get("Product Description", ""),
                    "Gallery": ",".join(raw_url(p) for p in imgs)})
    with open(os.path.join(REPO, "LEA_Images.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Slug", "Product Description", "Gallery"])
        w.writeheader(); w.writerows(out)
    print(f"LEA_Images.csv: {len(out)}/{len(rows)} products with galleries | "
          f"{sum(len(r['Gallery'].split(',')) for r in out)} image refs")
    if empty:
        print("no images:", empty)

if __name__ == "__main__":
    main()
