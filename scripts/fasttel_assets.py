#!/usr/bin/env python3
"""Download Fasttel product images (and the shared FT600 family datasheet) into
Assets/fasttel/<slug>/, web-optimize, and emit scripts/fasttel_manifest.json.

Sources are shop.fasttel.com (/web/image/...image_1024 -> usually webp) and
static.wixstatic.com base media URLs (original res -> may need downscale).
"""
import os, json, subprocess, urllib.request, ssl

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(REPO, "scripts", "research_fasttel.json")
DEST = os.path.join(REPO, "Assets", "fasttel")
SHARED = os.path.join(DEST, "_shared")
MAXPX = 1600
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
        return r.read()

def ext_of(data):
    if data[:2] == b"\xff\xd8": return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n": return ".png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return ".webp"
    if data[:4] == b"%PDF": return ".pdf"
    if data[:6] in (b"GIF87a", b"GIF89a"): return ".gif"
    return None

def dims(path):
    try:
        out = subprocess.check_output(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                                      stderr=subprocess.DEVNULL).decode()
        w = h = 0
        for line in out.splitlines():
            if "pixelWidth:" in line: w = int(line.split(":")[1])
            if "pixelHeight:" in line: h = int(line.split(":")[1])
        return w, h
    except Exception:
        return 0, 0

def optimize(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".webp":
        return  # already <=1024 from Odoo
    w, h = dims(path)
    if max(w, h) > MAXPX:
        cmd = ["sips", "-Z", str(MAXPX)]
        if ext in (".jpg", ".jpeg"):
            cmd += ["-s", "format", "jpeg", "-s", "formatOptions", "80"]
        cmd += [path, "--out", path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    data = json.load(open(RESEARCH))
    fam_url = data["ft600_family_datasheet"]
    products = data["products"]
    os.makedirs(SHARED, exist_ok=True)

    # shared FT600 family datasheet (once)
    fam_path = os.path.join(SHARED, "ft600_family_datasheet.pdf")
    fam_rel = "Assets/fasttel/_shared/ft600_family_datasheet.pdf"
    if not os.path.exists(fam_path):
        try:
            d = fetch(fam_url)
            if d[:4] == b"%PDF":
                open(fam_path, "wb").write(d)
                print("shared FT600 datasheet saved", len(d), "bytes")
            else:
                print("!! FT600 family url not a PDF")
        except Exception as e:
            print("!! family datasheet failed:", e)

    manifest = {}
    for p in products:
        slug = p["slug"]
        ddir = os.path.join(DEST, slug)
        os.makedirs(ddir, exist_ok=True)
        imgs = []
        for i, url in enumerate(p.get("image_urls", []), 1):
            try:
                d = fetch(url)
            except Exception as e:
                print(f"  !! {slug} img{i} fetch failed: {str(e)[:60]}")
                continue
            ext = ext_of(d)
            if ext is None or ext == ".pdf":
                print(f"  !! {slug} img{i} not an image ({url[:50]})")
                continue
            fn = f"{slug}_{i:02d}{ext}"
            fp = os.path.join(ddir, fn)
            open(fp, "wb").write(d)
            optimize(fp)
            imgs.append(fn)
        # datasheet resolution
        ds = None
        own = os.path.join(ddir, f"{slug}_datasheet.pdf")
        if os.path.exists(own):
            ds = f"Assets/fasttel/{slug}/{slug}_datasheet.pdf"
        elif p.get("datasheet_url") == "ft600_family" and os.path.exists(fam_path):
            ds = fam_rel
        manifest[slug] = {"images": imgs, "datasheet": ds}
        print(f"{slug:16} imgs={len(imgs)} ds={'Y' if ds else '-'}")

    json.dump(manifest, open(os.path.join(REPO, "scripts", "fasttel_manifest.json"), "w"), indent=1)
    tot = sum(len(v["images"]) for v in manifest.values())
    print(f"\nTOTAL fasttel images: {tot} across {len(manifest)} slugs")

if __name__ == "__main__":
    main()
