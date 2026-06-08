#!/usr/bin/env python3
"""Scrape per-product images from garvanacoustic.com (WordPress) for the Garvan
products that had no own images locally — so each product shows ITS OWN photos
instead of a shared product-line gallery (reported 2026-06-08).

The vendor pages are server-rendered HTML; per-model images are named with the
model code (e.g. SA520.png, Garvan-amplifiers-AT432-A.png, sa117.png). We match
strictly on the model-code token so we never pull a sibling model's image (the
sa117 page also carries SA115 shots, etc.). WordPress size variants
(-300x78, -1536x400 ...) are collapsed to the original upload.

Only the products with genuinely distinct vendor images are listed here. The
Aria soundbar modules (kr/kw 4-digit) are custom-length variants of one product
with no dedicated render, `ara` has no product page, and at232-a / at260-a have
only a generic amplifier photo — those are left for a manual decision.

Saves to Assets/garvan-acoustics/<slug>/<slug>_v<NN>.<ext>, web-optimized.
Re-run scripts/garvan_pick_images.py + scripts/build_csvs.py afterwards.
"""
import os, re, ssl, json, subprocess, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(REPO, "Assets", "garvan-acoustics")
MAXPX = 1600
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

V = "https://www.garvanacoustic.com/en/product/"
CINEMATELIER = V + "acoustic-sound-panels-cinematelier/"
AMP = V + "amplifiers/"

# slug -> (page_url, [include tokens (lowercased)], [exclude tokens])
PAGES = {
    "sa117":        (V + "sa117/",                        ["sa117"],           []),
    "sa225":        (V + "outdoor-speaker-sa225/",        ["sa225"],           []),
    "sn117":        (V + "outdoor-loudspeakers-sn117/",   ["sn117"],           []),
    "wn120":        (V + "wn120/",                        ["wn120", "sn120"],  []),
    "atelier":      (V + "sound-absorbing-panels-atelier/", ["atelier"],       ["cinematelier"]),
    "surface":      (V + "sound-absorbing-panel-surface/", ["surface"],        []),
    "sound-quadra": (V + "tile-loudspeaker-quadra/",      ["quadra"],          []),
    "sa520":        (CINEMATELIER,                        ["sa520"],           []),
    "wa220":        (CINEMATELIER,                        ["wa220"],           ["wa220h"]),
    "sa111":        (CINEMATELIER,                        ["sa111"],           []),
    "sa214":        (CINEMATELIER,                        ["sa214"],           []),
    "sa314":        (CINEMATELIER,                        ["sa314"],           []),
    "sa317":        (CINEMATELIER,                        ["sa317"],           []),
    "sa320":        (CINEMATELIER,                        ["sa320"],           []),
    "wae121":       (V + "active-subwoofer-wae121/",      ["wae121"],          ["wae121p"]),
    "at432-a":      (AMP,                                 ["at432-a"],         []),
    "at432-d":      (AMP,                                 ["at432-d"],         []),
    "at460-a":      (AMP,                                 ["at460-a"],         []),
    "at460-d":      (AMP,                                 ["at460-d"],         []),
    "at440":        (AMP,                                 ["at440"],           []),
    "at2404-a":     (AMP,                                 ["at2404-a"],        []),
    "at4804-a":     (AMP,                                 ["at4804-a"],        []),
}

# never want site chrome / decorative assets
GLOBAL_EXCLUDE = ("logo", "made-in-italy", "favicon", "bg_garvan", "garvan_logo",
                  "icon", "placeholder")
SIZEVAR = re.compile(r"-\d+x\d+(?=\.\w+$)")
IMG_RE = re.compile(r"wp-content/uploads/20\d{2}/\d{2}/[^\"' )]+?\.(?:png|jpg|jpeg)", re.I)

def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")

def ext_of(d):
    if d[:2] == b"\xff\xd8": return ".jpg"
    if d[:8] == b"\x89PNG\r\n\x1a\n": return ".png"
    if d[:4] == b"RIFF" and d[8:12] == b"WEBP": return ".webp"
    return None

def dims(path):
    try:
        out = subprocess.check_output(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                                      stderr=subprocess.DEVNULL).decode()
        w = h = 0
        for ln in out.splitlines():
            if "pixelWidth:" in ln: w = int(ln.split(":")[1])
            if "pixelHeight:" in ln: h = int(ln.split(":")[1])
        return w, h
    except Exception:
        return 0, 0

def optimize(path):
    ext = os.path.splitext(path)[1].lower()
    w, h = dims(path)
    if max(w, h) > MAXPX:
        cmd = ["sips", "-Z", str(MAXPX)]
        if ext in (".jpg", ".jpeg"):
            cmd += ["-s", "format", "jpeg", "-s", "formatOptions", "82"]
        cmd += [path, "--out", path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def candidates(html, includes, excludes):
    out = []
    seen = set()
    for m in IMG_RE.finditer(html):
        rel = m.group(0)
        low = rel.lower()
        if any(x in low for x in GLOBAL_EXCLUDE): continue
        if any(x in low for x in excludes): continue
        if not any(tok in low for tok in includes): continue
        base = SIZEVAR.sub("", rel)              # collapse to original upload
        if base in seen: continue
        seen.add(base)
        out.append("https://www.garvanacoustic.com/" + base)
    return out

def main():
    report = {}
    for slug, (url, inc, exc) in PAGES.items():
        try:
            html = fetch(url)
        except Exception as e:
            print(f"{slug:14} !! page fetch failed: {str(e)[:60]}")
            report[slug] = {"error": "page fetch failed"}
            continue
        urls = candidates(html, inc, exc)
        ddir = os.path.join(DEST, slug)
        os.makedirs(ddir, exist_ok=True)
        saved = []
        for i, u in enumerate(urls, 1):
            try:
                d = fetch(u, binary=True)
            except Exception as e:
                print(f"{slug:14} !! img fetch failed {u[-40:]}: {str(e)[:40]}")
                continue
            ext = ext_of(d)
            if not ext:
                print(f"{slug:14} !! not an image: {u[-40:]}")
                continue
            fn = f"{slug}_v{i:02d}{ext}"
            fp = os.path.join(ddir, fn)
            open(fp, "wb").write(d)
            optimize(fp)
            saved.append(fn)
        report[slug] = {"page": url, "found": len(urls), "saved": saved}
        print(f"{slug:14} found={len(urls):2} saved={len(saved):2}  {saved}")
    json.dump(report, open(os.path.join(REPO, "scripts", "garvan_scrape_report.json"), "w"), indent=1)
    print("\nTOTAL images:", sum(len(v.get("saved", [])) for v in report.values()))

if __name__ == "__main__":
    main()
