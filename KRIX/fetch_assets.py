#!/usr/bin/env python3
"""
Localize Krix assets into the repo (run in a NETWORK-ENABLED environment).

Why: Framer's CSV import fails to fetch some Krix-hosted PDFs/images, and the
build sandbox has no outbound network. This script downloads every referenced
asset, removes backgrounds from opaque images, saves PNGs, commits them to the
repo, and rewrites the CSV Specsheet/Thumbnail columns to raw.githubusercontent
URLs (which Framer fetches reliably).

PREREQUISITES (network-enabled host):
    pip install requests rembg pillow
    # rembg downloads a model on first run.

USAGE:
    python3 KRIX/fetch_assets.py            # download, process, rewrite CSVs
    python3 KRIX/fetch_assets.py --commit   # also git add/commit/push

It is idempotent: existing files in KRIX/assets/ are reused, not re-downloaded.
Every step is wrapped so one failure does not abort the run; a summary prints
at the end listing what succeeded and what still needs manual attention.
"""
import csv, os, re, sys, subprocess, urllib.parse

REPO = "madiers/claude-all"
BRANCH = "claude/blissful-cori-JY3Gi"
ROOT = os.path.dirname(os.path.abspath(__file__))            # .../KRIX
ASSETS = os.path.join(ROOT, "assets")
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/KRIX/assets/"
CSVS = [os.path.join(ROOT, "Krix_Site_Enrichment.csv"),
        os.path.join(ROOT, "Krix_Draft_Additions.csv")]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# Product page per slug for image scraping. Fallback = /product/<slug>.
PAGE_OVERRIDES = {
    "holographix": "https://www.krix.com.au/product/holographix",
    "hemispherix-sps": "https://www.krix.com.au/product/ic-35s",
    "ic-80-(stratospherix-as)": "https://www.krix.com.au/product/ic-80",
    "kx-4010": "https://www.krix.com.au/commercial-cinema/kx-4010",
    "kx-4210": "https://www.krix.com.au/commercial-cinema/kx-4210",
    "kx-4240": "https://www.krix.com.au/commercial-cinema/kx-4240",
    "kx-4605": "https://www.krix.com.au/commercial-cinema/kx-4605",
    "kx-4610": "https://www.krix.com.au/commercial-cinema/kx-4610",
    "kx-4610s": "https://www.krix.com.au/commercial-cinema/kx-4610s",
    "kx-5910": "https://www.krix.com.au/commercial-cinema/kx-5910",
    "kx-5720": "https://www.krix.com.au/commercial-cinema/kx-5720",
    "kx-1155": "https://www.krix.com.au/commercial-cinema/kx-1155",
    "kx-1470": "https://www.krix.com.au/commercial-cinema/kx-1470",
}

def page_url(slug):
    return PAGE_OVERRIDES.get(slug, f"https://www.krix.com.au/product/{slug}")

def _requests():
    import requests
    return requests

def download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    r = _requests().get(url, headers=UA, timeout=60)
    r.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(r.content)
    return True

def find_main_image(page):
    """Return a best-guess product image URL from a Krix product page."""
    r = _requests().get(page, headers=UA, timeout=60)
    r.raise_for_status()
    html = r.text
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', html, re.I)
    if m:
        return m.group(1)
    # fallback: any Webflow CDN raster image on the page
    imgs = re.findall(r'https://[^"\']+\.(?:png|jpg|jpeg|webp)', html, re.I)
    imgs = [u for u in imgs if "website-files.com" in u or "krix" in u]
    return imgs[0] if imgs else None

def is_opaque(path):
    """True if image has no usable alpha transparency (so BG removal is wanted)."""
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    alpha = im.getchannel("A")
    return alpha.getextrema()[0] == 255  # min alpha 255 => fully opaque

def remove_bg(src, dst):
    from rembg import remove
    from PIL import Image
    with open(src, "rb") as f:
        out = remove(f.read())
    with open(dst, "wb") as f:
        f.write(out)
    Image.open(dst).save(dst)  # normalize

def localize_pdfs(rows, ix, log):
    si = ix.get("Specsheet")
    if si is None:
        return
    for r in rows[1:]:
        url = r[si].strip()
        if not url or "raw.githubusercontent.com" in url or "framerusercontent.com" in url:
            continue
        slug = r[ix["Slug"]]
        dest = os.path.join(ASSETS, f"{slug}_datasheet.pdf")
        try:
            download(url, dest)
            r[si] = RAW + urllib.parse.quote(f"{slug}_datasheet.pdf")
            log.append(f"PDF  ok   {slug}")
        except Exception as e:
            log.append(f"PDF  FAIL {slug}: {e}")

def localize_images(rows, ix, log, drafts):
    ti, ai = ix.get("Thumbnail"), ix.get("Thumbnail:alt")
    for r in rows[1:]:
        slug = r[ix["Slug"]]
        if not drafts and r[ti].strip():      # existing row already has an image
            continue
        dest_png = os.path.join(ASSETS, f"{slug}.png")
        if os.path.exists(dest_png):
            r[ti] = RAW + urllib.parse.quote(f"{slug}.png"); continue
        try:
            img_url = find_main_image(page_url(slug))
            if not img_url:
                log.append(f"IMG  FAIL {slug}: no image found on page"); continue
            ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1].lower() or ".jpg"
            raw = os.path.join(ASSETS, f"_{slug}_src{ext}")
            download(img_url, raw)
            try:
                if ext == ".png" and not is_opaque(raw):
                    os.replace(raw, dest_png)           # already transparent PNG
                else:
                    remove_bg(raw, dest_png)            # remove background -> PNG
                    os.remove(raw)
            except Exception as e:
                # fall back to the raw image (still localized) if BG removal fails
                os.replace(raw, dest_png); log.append(f"IMG  warn {slug}: bg-removal skipped ({e})")
            r[ti] = RAW + urllib.parse.quote(f"{slug}.png")
            if ai is not None and not r[ai].strip():
                r[ai] = r[ix["Title"]]
            log.append(f"IMG  ok   {slug}")
        except Exception as e:
            log.append(f"IMG  FAIL {slug}: {e}")

def main():
    csv.field_size_limit(10**8)
    os.makedirs(ASSETS, exist_ok=True)
    log = []
    for path in CSVS:
        rows = list(csv.reader(open(path, newline="", encoding="utf-8")))
        ix = {c: i for i, c in enumerate(rows[0])}
        drafts = "Draft" in os.path.basename(path)
        localize_pdfs(rows, ix, log)
        localize_images(rows, ix, log, drafts)
        csv.writer(open(path, "w", newline="", encoding="utf-8")).writerows(rows)
    print("\n".join(log))
    print(f"\nDONE: {sum('ok' in l for l in log)} ok, "
          f"{sum('FAIL' in l for l in log)} failed, "
          f"{sum('warn' in l for l in log)} warnings")
    if "--commit" in sys.argv:
        subprocess.run(["git", "add", "KRIX"], check=True)
        subprocess.run(["git", "commit", "-m",
                        "Localize Krix images/PDFs into repo and repoint CSV URLs"], check=True)
        subprocess.run(["git", "push", "-u", "origin", BRANCH], check=True)

if __name__ == "__main__":
    main()
