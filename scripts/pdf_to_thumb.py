#!/usr/bin/env python3
"""For every row in batch_2026-05-29_enrichment.csv that has a Specsheet PDF
but no Thumbnail, render page 1 of the PDF as a PNG and use that as the
Thumbnail. Uses macOS's built-in `sips` so no extra dependencies.
"""
import csv, os, subprocess, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BRANCH = "claude/blissful-cori-JY3Gi"
BASE = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}"
def raw_url(rel): return BASE + "/" + urllib.parse.quote(rel, safe="/")

def safe(s):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:200]

def pdf_to_png(pdf_path, png_path):
    """Render page 1 of the PDF to a PNG using sips. Returns True on success."""
    try:
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        # sips renders the first page automatically when input is a PDF
        result = subprocess.run(
            ["sips", "-s", "format", "png", pdf_path, "--out", png_path],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return False
        return os.path.exists(png_path) and os.path.getsize(png_path) > 1024
    except Exception:
        return False

with open("batch_2026-05-29_enrichment.csv") as f:
    rows = list(csv.reader(f))
hdr = rows[0]
ci = {h: i for i, h in enumerate(hdr)}

candidates = []
for r in rows[1:]:
    if r[ci["Specsheet"]] and not r[ci["Thumbnail"]]:
        candidates.append(r)
print(f"Found {len(candidates)} rows with Specsheet but no Thumbnail")

ok = fail = skip = 0
for r in candidates:
    slug  = r[ci["Slug"]]
    brand = r[ci["Brand"]]
    pdf_local = f"Assets/{safe(brand)}/{safe(slug)}/{safe(slug)}_datasheet.pdf"
    png_local = f"Assets/{safe(brand)}/{safe(slug)}/{safe(slug)}_pdfthumb.png"
    if not os.path.isfile(pdf_local):
        print(f"  SKIP no local pdf: {pdf_local}")
        skip += 1
        continue
    if os.path.isfile(png_local) and os.path.getsize(png_local) > 1024:
        # Already rendered in a previous run
        r[ci["Thumbnail"]] = raw_url(png_local)
        ok += 1
        continue
    if pdf_to_png(pdf_local, png_local):
        r[ci["Thumbnail"]] = raw_url(png_local)
        ok += 1
        if ok % 20 == 0:
            print(f"  rendered {ok}/{len(candidates)}")
    else:
        print(f"  FAIL render: {pdf_local}")
        fail += 1

with open("batch_2026-05-29_enrichment.csv", "w", newline="") as f:
    csv.writer(f).writerows(rows)

print(f"\nDone. ok={ok}  fail={fail}  skip={skip}")
# Final state check
with open("batch_2026-05-29_enrichment.csv") as f:
    rows2 = list(csv.reader(f))
blank_thumb = sum(1 for r in rows2[1:] if not r[ci["Thumbnail"]])
print(f"\nFinal CSV: {len(rows2)-1} rows, {blank_thumb} still blank Thumbnail")
