#!/usr/bin/env python3
"""Scrape each MAG product's FULL 1000x1000 gallery from mag-audio.com (OpenCart)
and mirror the images into MAG/cache/catalog/<series>/ so Framer can fetch them
over raw.githubusercontent.

Covers ALL MAG products (Brand=mag-audio in the export), not just the empty ones
— the repo cache previously held only a single image for several series (CUE,
FLY-R, AIR-CX...), so those galleries looked sparse next to the website.

Each product PAGE exposes its own gallery as
`/image/cache/catalog/<series>/<file>-1000x1000.jpg`; related products show only
as small thumbs, so the 1000x1000 set on a page is that product's own gallery.
Product URLs are resolved from mag-audio.com/sitemap.xml (slug == last path
segment, preferring the live page over /archive-audio/...). Because some
filenames carry no clean model token (LAIR-620001, VerA-M-BK-*), the slug ->
[image relpaths] mapping is recorded authoritatively in
scripts/mag_scrape_manifest.json. Then re-run scripts/build_mag_images.py.
"""
import os, re, ssl, csv, json, urllib.request, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(REPO, "Products_18-June-2026.csv")
BASE = "https://mag-audio.com/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# slugs whose page can't be resolved by exact last-segment match
SPECIAL = {
    "air-c24-installation-speaker": ["products-by-series/air-c-series/air-c24"],
    "cl-s": ["accessories/mounting-hardware/cl-s12",
             "accessories/mounting-hardware/cl-s15",
             "accessories/mounting-hardware/cl-s18"],
}
CACHE_RE = re.compile(r"image/cache/catalog/[^\"'\s)]+?-1000x1000\.(?:jpg|jpeg|png|JPG|JPEG|PNG)")

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")

def magic_ok(d):
    return d[:2] == b"\xff\xd8" or d[:8] == b"\x89PNG\r\n\x1a\n"

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def resolve_pages():
    """slug -> [vendor page path(s)] from the sitemap (+ SPECIAL overrides)."""
    sm = get(BASE + "sitemap.xml")
    urls = re.findall(r"<loc>(https://mag-audio\.com/[^<]+)</loc>", sm)
    prod = [u for u in urls if u.count("/") >= 4]
    seg = [(u, norm(u.rstrip("/").split("/")[-1])) for u in prod]
    slugs = [r["Slug"] for r in csv.DictReader(open(EXPORT, newline="", encoding="utf-8"))
             if r.get("Brand") == "mag-audio"]
    pages = {}
    for s in slugs:
        if s in SPECIAL:
            pages[s] = SPECIAL[s]; continue
        ns = norm(s)
        hits = [u for u, sn in seg if sn == ns]
        if hits:
            nonarch = [u for u in hits if "/archive" not in u]
            chosen = (nonarch or hits)[0]
            pages[s] = [chosen.split("mag-audio.com/", 1)[1]]
    return pages

def scrape_page(path):
    """Return list of (encoded_relpath) for the 1000x1000 cache images on a page."""
    try:
        html = get(BASE + path)
    except Exception as e:
        print(f"  !! page {path[-34:]}: {str(e)[:40]}"); return []
    return sorted(set(CACHE_RE.findall(html)))

def main():
    pages = resolve_pages()
    manifest = {}
    for slug, paths in pages.items():
        rels = []
        for p in paths:
            for rel_enc in scrape_page(p):
                rel = urllib.parse.unquote(rel_enc)
                dest = os.path.join(REPO, "MAG", "cache", "catalog",
                                    rel.split("image/cache/catalog/", 1)[1])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                if not os.path.exists(dest):
                    try:
                        d = get(BASE + rel_enc, binary=True)
                    except Exception as e:
                        print(f"  !! img {rel[-34:]}: {str(e)[:40]}"); continue
                    if not magic_ok(d):
                        print(f"  !! not image {rel[-34:]}"); continue
                    open(dest, "wb").write(d)
                rels.append(os.path.relpath(dest, REPO))
        rels = sorted(dict.fromkeys(rels), key=lambda r: os.path.basename(r).lower())
        manifest[slug] = rels
        print(f"{slug:30} imgs={len(rels)}")
    json.dump(manifest, open(os.path.join(REPO, "scripts", "mag_scrape_manifest.json"), "w"), indent=1)
    tot = sum(len(v) for v in manifest.values())
    empty = [s for s, v in manifest.items() if not v]
    print(f"\nresolved {len(manifest)} products | {tot} images | "
          f"{sum(1 for v in manifest.values() if v)} with images")
    print("no images / unresolved:", empty)

if __name__ == "__main__":
    main()
