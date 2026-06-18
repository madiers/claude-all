#!/usr/bin/env python3
"""Scrape the 1000x1000 product-gallery images from mag-audio.com (OpenCart) for
the MAG products that had no images in the repo, and mirror them into
MAG/cache/catalog/<series>/ so Framer can fetch them over raw.githubusercontent.

Each product page exposes its own gallery as
`/image/cache/catalog/<series>/<file>-1000x1000.jpg`; related products show only
as small thumbs, so the 1000x1000 set on a page is that product's own gallery.
Because some filenames don't carry a clean model token (LAIR-620001, VerA-M-...),
we record an authoritative slug -> [image relpaths] manifest here rather than
re-deriving the mapping from filenames later.

Output: images under MAG/cache/catalog/..., manifest scripts/mag_scrape_manifest.json.
Then re-run scripts/build_mag_images.py.
"""
import os, re, ssl, json, urllib.request, urllib.parse, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://mag-audio.com/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# slug -> vendor page path(s) (resolved from mag-audio.com/sitemap.xml)
PAGES = {
    "vera-m-wh": ["products-by-series/vera-series/vera-m-wh"],
    "vera-m": ["products-by-series/vera-series/vera-m"],
    "fly-sub-18": ["products-by-series/fly-series/fly-sub-18"],
    "fly-sub-12l": ["products-by-series/fly-series/fly-sub-12l"],
    "fly-sub-15": ["products-by-series/fly-series/fly-sub-15"],
    "fd-s15": ["products-by-series/field-series/fd-s15"],
    "fd-52": ["products-by-series/field-series/fd-52"],
    "sting-6q": ["products-by-series/sting-series/sting-6-q"],
    "sting-6qi": ["products-by-series/sting-series/sting-6qi"],
    "cluster-q": ["products-by-series/cluster-series/cluster-q"],
    "cluster-q-ip": ["products-by-series/cluster-series/cluster-q-ip"],
    "cluster-q8": ["products-by-series/cluster-series/cluster-q8"],
    "cluster-q8-ip": ["products-by-series/cluster-series/cluster-q8-ip"],
    "air-62": ["products-by-series/air-series/air-62"],
    "air-c4t": ["products-by-series/air-c-series/air-c4t"],
    "air-c4": ["products-by-series/air-c-series/air-c4"],
    "air-c24-installation-speaker": ["products-by-series/air-c-series/air-c24"],
    "air-s18": ["products-by-series/air-series/air-s18"],
    "air-s18-ip": ["products-by-series/air-series/air-s18-ip"],
    "air-s12": ["products-by-series/air-series/air-s12"],
    "air-s12-ip": ["products-by-series/air-series/air-s12-ip"],
    "nx-12a": ["archive-audio/nx-series/nx-12a"],
    "nx-12i": ["archive-audio/nx-series/nx-12i"],
    "nx-12-ip": ["archive-audio/nx-series/nx12-ip"],
    "wasp-8": ["products-by-series/wasp-series/wasp8"],
    "wasp-s15": ["products-by-series/wasp-series/wasp-s15"],
    "wasp-s18": ["products-by-series/wasp-series/wasp-s18"],
    "cl-s": ["accessories/mounting-hardware/cl-s12",
             "accessories/mounting-hardware/cl-s15",
             "accessories/mounting-hardware/cl-s18"],
    "lair-122": ["accessories/mounting-hardware/lair122"],
    "lair-152": ["accessories/mounting-hardware/lair152"],
    "lair-62": ["accessories/mounting-hardware/lair62"],
    "lair-82": ["accessories/mounting-hardware/lair82"],
    "lls": ["accessories/mounting-hardware/lls"],
    "air-cl": ["accessories/mounting-hardware/air-cl"],
    "air-cs": ["accessories/mounting-hardware/air-cs"],
    "h-air-12": ["accessories/mounting-hardware/h-air-12"],
    "v-air-12": ["accessories/mounting-hardware/v-air-12"],
    "nd-10a": ["products-by-series/nd-series/nd-10a"],
    "nd-12a": ["products-by-series/nd-series/nd-12a"],
    "war-6": ["amplification/amplifier-racks/war-6"],
    "war-8": ["amplification/amplifier-racks/war-8"],
}

CACHE_RE = re.compile(r"image/cache/catalog/[^\"'\s)]+?-1000x1000\.(?:jpg|jpeg|png|JPG|JPEG|PNG)")

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")

def magic_ok(d):
    return d[:2] == b"\xff\xd8" or d[:8] == b"\x89PNG\r\n\x1a\n"

def main():
    manifest = {}
    for slug, paths in PAGES.items():
        rels = []
        for p in paths:
            try:
                html = get(BASE + p)
            except Exception as e:
                print(f"{slug:30} !! page {p[-30:]}: {str(e)[:40]}"); continue
            for m in sorted(set(CACHE_RE.findall(html))):
                rel_enc = m                              # vendor relpath (may have %20)
                rel = urllib.parse.unquote(rel_enc)      # decoded local path
                dest = os.path.join(REPO, "MAG", "cache", "catalog",
                                    rel.split("image/cache/catalog/", 1)[1])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                if not os.path.exists(dest):
                    try:
                        d = get(BASE + rel_enc, binary=True)
                    except Exception as e:
                        print(f"{slug:30} !! img {rel[-30:]}: {str(e)[:40]}"); continue
                    if not magic_ok(d):
                        print(f"{slug:30} !! not an image: {rel[-30:]}"); continue
                    open(dest, "wb").write(d)
                rels.append(os.path.relpath(dest, REPO))
        # de-dup, stable order
        rels = sorted(dict.fromkeys(rels), key=lambda r: os.path.basename(r).lower())
        manifest[slug] = rels
        print(f"{slug:30} imgs={len(rels)}")
    json.dump(manifest, open(os.path.join(REPO, "scripts", "mag_scrape_manifest.json"), "w"), indent=1)
    tot = sum(len(v) for v in manifest.values())
    empty = [s for s, v in manifest.items() if not v]
    print(f"\nTOTAL images: {tot}  | products with images: {sum(1 for v in manifest.values() if v)}/{len(manifest)}")
    print("still empty:", empty)

if __name__ == "__main__":
    main()
