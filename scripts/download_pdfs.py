#!/usr/bin/env python3
"""Download every vendor Specsheet PDF referenced in research_mag.json /
research_krix.json into the repo, organized so each PDF lives next to its
product's image folder under "NEW Product Pics/".

After download, the Specsheet column in batch_2026-05-29.csv can be rewritten
to point at raw.githubusercontent.com instead of the vendor URL.
"""
import json, os, urllib.parse, urllib.request, ssl, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# Map slug -> local image folder (parent we'll save the PDF into).
# These mirror the folders left in "NEW Product Pics/" after cleanup.
SLUG_FOLDER = {
    # MAG accessories (10)
    "cl-s":      "NEW Product Pics/AIR series/Accessories/CL-S",
    "lair-122":  "NEW Product Pics/AIR series/Accessories/LAIR-122",
    "lair-152":  "NEW Product Pics/AIR series/Accessories/LAIR-152",
    "lair-62":   "NEW Product Pics/AIR series/Accessories/LAIR-62",
    "lair-82":   "NEW Product Pics/AIR series/Accessories/LAIR-82",
    "lls":       "NEW Product Pics/AIR series/Accessories/LLS Render",
    "air-cl":    "NEW Product Pics/AIR-C series/Accessories/AIR-CL",
    "air-cs":    "NEW Product Pics/AIR-C series/Accessories/AIR-CS",
    "h-air-12":  "NEW Product Pics/AIR-C series/Accessories-Air-Cx/H-AIR-12",
    "v-air-12":  "NEW Product Pics/AIR-C series/Accessories-Air-Cx/V-AIR-12",
    # Krix cinema
    "ka-1100":             "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Amplifiers/KA-1100",
    "megaphonix-in-room":  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Freestanding/Megaphonix In-Room",
    "megaphonix-in-wall":  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/In-wall/Megaphonix In-Wall",
    "phonix-in-wall":      "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/In-wall/Phonix In-Wall",
    "as-315":              "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/AS-315",
    "mx-20-mk2":           "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-20 Mk2",
    "mx-30i":              "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-30i",
    "mx-40i":              "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-40i",
    "mxi-118":             "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MXi-118",
    "megaphonix":          "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/Megaphonix",
    "owx-50":              "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/OWX-50",
    "owx-55":              "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/OWX-55",
    "phonix":              "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/Phonix",
    "phonix-45":           "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/Phonix 45",
    "phonix-flat":         "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/Phonix Flat",
    "megacyclonix":        "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Subwoofer/Megacyclonix",
    "ucx-218":             "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Subwoofer/UCX-218",
    # Krix HE
    "banana-plugs":        "NEW Product Pics/KRIX Home Entertainment Product Images/Accessories/Banana Plugs",
    "seismix-transmitter": "NEW Product Pics/KRIX Home Entertainment Product Images/Accessories/Seismix Transmitter",
    "acoustix-mk2":        "NEW Product Pics/KRIX Home Entertainment Product Images/Bookshelf/Acoustix Mk2",
    "equinox-mk5":         "NEW Product Pics/KRIX Home Entertainment Product Images/Bookshelf/Equinox Mk5",
    "graphix-mk2":         "NEW Product Pics/KRIX Home Entertainment Product Images/Centre Channel/Graphix Mk2",
    "sonix-mk3":           "NEW Product Pics/KRIX Home Entertainment Product Images/Centre Channel/Sonix Mk3",
    "holographix":         "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/Holographix",
    "ic-20":               "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/IC-20",
    "ic-30":               "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/IC-30",
    "ic-32":               "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/IC-32",
    "ic-50":               "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/IC-50",
    "ic-52":               "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/IC-52",
    "ic-80":               "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/IC-80",
    "iw-50":               "NEW Product Pics/KRIX Home Entertainment Product Images/In-Wall/IW-50",
    "aquatix":             "NEW Product Pics/KRIX Home Entertainment Product Images/Outdoor/Aquatix",
    "tropix":              "NEW Product Pics/KRIX Home Entertainment Product Images/Outdoor/Tropix",
    "dynamix-mk4":         "NEW Product Pics/KRIX Home Entertainment Product Images/Surround/Dynamix Mk4",
}

def load(p):
    with open(p) as f: return json.load(f)

products = load('scripts/research_mag.json') + load('scripts/research_krix.json')

ctx = ssl.create_default_context()
ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

# Track mapping: slug -> local repo-relative pdf path (or "" if no pdf)
result = {}
fails = []
for p in products:
    slug = p['slug']
    url  = p.get('specsheet_url', '').strip()
    if not url:
        result[slug] = ""
        continue
    folder = SLUG_FOLDER.get(slug)
    if not folder:
        print(f"!! unknown folder for slug {slug}", file=sys.stderr)
        fails.append((slug, "no folder mapping"))
        continue
    os.makedirs(folder, exist_ok=True)
    # Compose a clean filename: slug + .pdf, plus a "_datasheet" suffix
    # so files sort distinctly from images.
    fname = f"{slug}_datasheet.pdf"
    out = os.path.join(folder, fname)
    if os.path.exists(out) and os.path.getsize(out) > 1024:
        print(f"   skip (exists): {out}")
        result[slug] = out
        continue
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            data = r.read()
        if len(data) < 1024 or not data[:4] == b"%PDF":
            raise RuntimeError(f"not a PDF (first bytes: {data[:8]!r}, size {len(data)})")
        with open(out, 'wb') as f:
            f.write(data)
        print(f"OK {len(data)//1024:>5} KB  {slug:<22}  {url[:80]}")
        result[slug] = out
        time.sleep(0.3)
    except Exception as e:
        print(f"FAIL {slug:<22}  {type(e).__name__}: {e}  ({url})")
        fails.append((slug, str(e)))
        result[slug] = ""

# Save mapping for the rewrite step
with open('scripts/pdf_paths.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"\nDownloaded PDFs for {sum(1 for v in result.values() if v)} / {len(products)} products")
if fails:
    print(f"Failures ({len(fails)}):")
    for s, e in fails: print(f"  {s}: {e}")
