#!/usr/bin/env python3
"""Build MAG_Images.csv — galleries ONLY for every MAG-Audio product.

User request (2026-06-18): "only galleries for all MAG products we have, change
nothing. Only galleries, no thumbnails." So the CSV carries just:
    Slug, Product Description, Gallery
Product Description is copied verbatim from the live export (Framer's importer
requires that field to be mapped; copying it back changes nothing). No
Thumbnail column, no other fields.

Gallery images come from the repo's MAG image cache,
`MAG/cache/catalog/<series>/...-1000x1000.jpg`, served over raw.githubusercontent.

Mapping (slug -> images):
- The 56 products already mapped in batch_2026-05-26_magaudio.csv are reused
  VERBATIM (those galleries are hand-curated, incl. group/accessory shots that
  no token rule would find).
- The rest are matched by bounded model-code token on the filename, with a
  base-model fallback for variants that share a base cabinet's photos
  (air-82-ip -> AIR-82, sting-8-114 -> STING-8, ...). An IP/non-IP consistency
  filter keeps `sub-15` and `sub-15-ip` from stealing each other's shots.
Products with no matching image are emitted with an empty Gallery and listed.
"""
import csv, os, re, json, urllib.parse, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(REPO, "Products_18-June-2026.csv")
BATCH = os.path.join(REPO, "batch_2026-05-26_magaudio.csv")
CACHE = os.path.join(REPO, "MAG", "cache", "catalog")
BRANCH = "claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}/"

def raw_url(relpath):
    return RAW + urllib.parse.quote(relpath)

# ---- image inventory (relpath from repo root) ----
IMAGES = []
for root, _, files in os.walk(CACHE):
    for f in files:
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            IMAGES.append(os.path.relpath(os.path.join(root, f), REPO))
def nfn(relpath):
    return re.sub(r"[^A-Z0-9]+", "-", os.path.basename(relpath).upper()).strip("-")
NF = {p: nfn(p) for p in IMAGES}

def bounded(tok, nf):
    return re.search(r"(?:^|-)" + re.escape(tok) + r"(?:-|$)", nf) is not None
def has_ip(nf):
    return bounded("IP", nf)

# Aliases / base-model tokens for variants whose photos live under another code.
ALIAS = {
    "sting-8-74": ["STING-8", "ST8"], "sting-8-114": ["STING-8", "ST8"],
    "sting-8-ip-74": ["STING-8", "ST8"], "sting-8-ip-114": ["STING-8", "ST8"],
    "sub-28a": ["SUB-28-A", "SUB-28A", "SUB-28"], "sub-28": ["SUB-28-A", "SUB-28"],
    "sub-28-ip": ["SUB-28-A", "SUB-28"],
    "s218": ["S-218", "S218"],
    "air-s26": ["AIR-S26A", "AIR-S26"],
}

def tokens_for(slug):
    """Ordered candidate tokens: the slug's own code first (so a variant that
    WAS photographed — e.g. cue-li — wins on its own token), then base-model
    fallbacks for variants that share a base cabinet's photos."""
    cand = [slug.upper()] + ALIAS.get(slug, [])
    # Build base models by peeling variant markers off the tail, smallest edit
    # first: -ip (weatherised), then a trailing active/install/transformer/
    # powered letter glued to the size number (nx-15a, air-c5t, focus-5p).
    seen = {slug}
    frontier = [slug]
    for _ in range(3):
        nxt = []
        for s in frontier:
            for b in (re.sub(r"-ip(-\d+)?$", "", s),          # air-82-ip -> air-82
                      re.sub(r"(?<=\d)[aitp]$", "", s)):       # nx-15a -> nx-15
                if b != s and b not in seen:
                    seen.add(b); nxt.append(b); cand.append(b.upper())
        frontier = nxt
    return list(dict.fromkeys(cand))

def match_slug(slug):
    slug_ip = bounded("IP", slug.upper())
    for tok in tokens_for(slug):
        hits = [p for p in IMAGES if bounded(tok, NF[p])]
        # IP consistency: a non-IP slug shouldn't grab IP-only shots and v.v.,
        # but only filter when it doesn't empty the result.
        consistent = [p for p in hits if has_ip(NF[p]) == slug_ip]
        chosen = consistent if consistent else hits
        if chosen:
            return sorted(chosen, key=lambda p: os.path.basename(p).lower())
    return []

def main():
    rows = list(csv.DictReader(open(EXPORT, newline="", encoding="utf-8")))
    mag = [r for r in rows if r.get("Brand") == "mag-audio"]
    # reuse curated galleries verbatim (keyed by slug) ----
    batch = {r["Slug"]: r.get("Gallery", "").strip()
             for r in csv.DictReader(open(BATCH, newline="", encoding="utf-8"))
             if r.get("Gallery", "").strip()}
    # authoritative slug -> [image relpaths] for products scraped from the vendor
    mpath = os.path.join(REPO, "scripts", "mag_scrape_manifest.json")
    scraped = json.load(open(mpath)) if os.path.exists(mpath) else {}
    out, empties, report = [], [], []
    for r in mag:
        slug = r["Slug"]
        # Prefer whichever of the full vendor scrape / curated May batch carries
        # MORE images (the batch keeps a couple of hand-picked group shots the
        # product page lacks; the scrape is otherwise the complete gallery).
        batch_g = batch.get(slug, "")
        nb = len([u for u in batch_g.split(",") if u.strip()])
        scrape_list = scraped.get(slug, [])
        ns = len(scrape_list)
        if ns or nb:
            if ns >= nb:
                gallery, src = ",".join(raw_url(p) for p in scrape_list), f"scrape:{ns}"
            else:
                gallery, src = batch_g, f"batch:{nb}"
        else:
            files = match_slug(slug)
            gallery = ",".join(raw_url(p) for p in files)
            src = f"match:{len(files)}"
        n = len([u for u in gallery.split(",") if u.strip()])
        report.append((slug, src, n))
        if n == 0:
            # No images for this product — omit the row entirely so importing
            # can't blank an existing gallery ("change nothing").
            empties.append(slug)
            continue
        out.append({"Slug": slug,
                    "Product Description": r.get("Product Description", ""),
                    "Gallery": gallery})
    with open(os.path.join(REPO, "MAG_Images.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Slug", "Product Description", "Gallery"])
        w.writeheader(); w.writerows(out)
    scr = sum(1 for s, src, n in report if src.startswith("scrape") and n)
    bat = sum(1 for s, src, n in report if src.startswith("batch") and n)
    mat = sum(1 for s, src, n in report if src.startswith("match") and n)
    print(f"MAG_Images.csv: {len(out)} rows with galleries "
          f"({scr} from vendor scrape, {bat} from May batch, {mat} token-matched)  "
          f"| {len(empties)} omitted | {sum(n for _,_,n in report)} images")
    if "--report" in sys.argv:
        for slug, src, n in report:
            print(f"  {slug:30} {src:10} imgs={n}")
    print("\nNO IMAGES (", len(empties), "):", empties)

if __name__ == "__main__":
    main()
