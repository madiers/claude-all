#!/usr/bin/env python3
"""Pick the right Thumbnail + Gallery images for each Garvan product.

Two problems this fixes (reported 2026-06-08):
  1. Galleries were assigned at the *product-line* level — e.g. every
     CinemAtelier panel (ka313h, ka316h, ...) pulled the shared
     `cinematelier__cinematelier_*` set, so ka313h's gallery showed every
     other model in the line. Each product must show ONLY its own images.
  2. Thumbnails were lifestyle/in-situ photos. The client wants the clean
     white-background / no-background product render as the thumbnail.

Approach: for each slug, look only at images whose filename belongs to that
slug (`<slug>_*`, never the `*__*` shared-line dumps), drop datasheet page
renders (`_pdfthumb`) and PDFs, then rank by background cleanliness using
`sips` (a transparent-alpha cutout or an all-white-corner frame = clean).

  Gallery   = the slug's own images, clean renders first.
  Thumbnail = the cleanest render (alpha cutout / white bg), else the first
              own image (no clean render exists locally for that slug).

Emits scripts/garvan_image_pick.json -> { slug: {thumbnail, gallery: [...],
clean: bool} }.  build_csvs.py reads this instead of the old line-level
manifest, so the CSV build stays fast and deterministic.

Slugs with NO own images (only shared-line dumps locally — the AT amplifier
and KR/KW Aria series) are emitted with empty gallery and flagged in
`needs_vendor_images`; those need per-product photos scraped from
garvanacoustic.com.
"""
import os, sys, json, struct, subprocess, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(REPO, "Assets", "garvan-acoustics")
OUT = os.path.join(REPO, "scripts", "garvan_image_pick.json")

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")

def is_img(f):
    return os.path.splitext(f)[1].lower() in IMG_EXT

def is_own(slug, f):
    """True if file belongs to this slug (not a `line__*` shared dump)."""
    if "__" in f:
        return False
    key = slug.replace("-", "").replace("_", "")
    return f.lower().replace("-", "").replace("_", "").startswith(key)

def is_excluded(f):
    n = f.lower()
    return "pdfthumb" in n or "datasheet" in n or n.endswith(".pdf")

def has_alpha(path):
    try:
        out = subprocess.check_output(["sips", "-g", "hasAlpha", path],
                                      stderr=subprocess.DEVNULL).decode()
        return "yes" in out
    except Exception:
        return False

def corner_colors(path, n=24):
    """Return the 4 corner RGB tuples of the image downsampled to n x n via a
    BMP round-trip (no PIL available)."""
    td = tempfile.mkdtemp()
    bmp = os.path.join(td, "t.bmp")
    try:
        r = subprocess.run(["sips", "-s", "format", "bmp", "-z", str(n), str(n),
                            path, "--out", bmp],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0 or not os.path.exists(bmp):
            return None
        data = open(bmp, "rb").read()
        off = struct.unpack_from("<I", data, 10)[0]
        w = struct.unpack_from("<i", data, 18)[0]
        h = struct.unpack_from("<i", data, 22)[0]
        bpp = struct.unpack_from("<H", data, 28)[0]
        nb = bpp // 8
        row = ((w * nb + 3) // 4) * 4
        H = abs(h)
        def px(x, y):
            yy = (H - 1 - y) if h > 0 else y
            i = off + yy * row + x * nb
            return (data[i + 2], data[i + 1], data[i])   # BMP is BGR
        return [px(0, 0), px(w - 1, 0), px(0, H - 1), px(w - 1, H - 1)]
    finally:
        try:
            os.remove(bmp); os.rmdir(td)
        except Exception:
            pass

def is_clean_bg(path):
    """Clean = transparent cutout OR all four corners near-white."""
    if has_alpha(path):
        return True
    cs = corner_colors(path)
    if not cs:
        return False
    return all(all(ch >= 225 for ch in c) for c in cs)

def rank(f):
    n = f.lower()
    if "main" in n:
        return 0
    if "gallery" in n:
        return 1
    return 2

def main():
    pick = {}
    needs = []
    slugs = sorted(d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, d)))
    for slug in slugs:
        d = os.path.join(BASE, slug)
        files = [f for f in sorted(os.listdir(d))
                 if is_img(f) and is_own(slug, f) and not is_excluded(f)]
        clean = {f: is_clean_bg(os.path.join(d, f)) for f in files}
        # gallery: own images, clean renders first (main, gallery, other),
        # then the rest (lifestyle photos of the same product) by name.
        ordered = sorted(files, key=lambda f: (0 if clean[f] else 1, rank(f), f.lower()))
        clean_imgs = [f for f in ordered if clean[f]]
        thumb = clean_imgs[0] if clean_imgs else (ordered[0] if ordered else None)
        pick[slug] = {
            "thumbnail": thumb,
            "gallery": ordered,
            "has_clean": bool(clean_imgs),
        }
        if not ordered:
            needs.append(slug)
        sys.stdout.write(
            f"{slug:16} own={len(ordered):2} clean={len(clean_imgs):2} "
            f"thumb={'CLEAN ' if clean_imgs else 'photo ' if ordered else 'NONE  '}"
            f"{thumb or ''}\n")
    json.dump({"pick": pick, "needs_vendor_images": needs},
              open(OUT, "w"), indent=1)
    print(f"\nwrote {OUT}")
    print(f"slugs with own images: {sum(1 for v in pick.values() if v['gallery'])}")
    print(f"slugs with a CLEAN thumbnail: {sum(1 for v in pick.values() if v['has_clean'])}")
    print(f"slugs needing vendor per-product images ({len(needs)}): {needs}")

if __name__ == "__main__":
    main()
