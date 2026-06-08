#!/usr/bin/env python3
"""Copy + web-optimize Garvan website photos from the external Drive gallery into
Assets/garvan-acoustics/<slug>/, and emit a per-slug manifest (images + datasheet)
for batch-CSV construction.

- Source:  ../Garvan Products/By Product/<slug>/<slug>_NN.{jpg,png,...}
- Dest:    Assets/garvan-acoustics/<slug>/<same-name>   (resized to <=1600px via sips)
- Skips PDFs (datasheet already mirrored in Assets); records existing PDF name.
"""
import os, subprocess, json, sys, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ROOT = os.path.normpath(os.path.join(REPO, "..", "Garvan Products", "By Product"))
DEST_ROOT = os.path.join(REPO, "Assets", "garvan-acoustics")

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAXPX = 1600

def is_image(name):
    return os.path.splitext(name)[1].lower() in IMG_EXT and not name.startswith(".")

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

def sort_key(name):
    # natural-ish: _01, _02 ... then the rest
    base = os.path.splitext(name)[0]
    digits = "".join(ch for ch in base.split("_")[-1] if ch.isdigit())
    return (0, int(digits)) if digits else (1, name.lower())

def main():
    slugs = sorted(d for d in os.listdir(SRC_ROOT)
                   if os.path.isdir(os.path.join(SRC_ROOT, d)) and not d.startswith("."))
    manifest = {}
    total_copied = 0
    for slug in slugs:
        sdir = os.path.join(SRC_ROOT, slug)
        ddir = os.path.join(DEST_ROOT, slug)
        os.makedirs(ddir, exist_ok=True)
        imgs = sorted([f for f in os.listdir(sdir) if is_image(f)], key=sort_key)
        copied = []
        for f in imgs:
            src = os.path.join(sdir, f)
            dst = os.path.join(ddir, f)
            ext = os.path.splitext(f)[1].lower()
            w, h = dims(src)
            if max(w, h) > MAXPX:
                # genuinely large: downscale (re-encode jpgs at q80)
                cmd = ["sips", "-Z", str(MAXPX)]
                if ext in (".jpg", ".jpeg"):
                    cmd += ["-s", "format", "jpeg", "-s", "formatOptions", "80"]
                cmd += [src, "--out", dst]
                r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                ok = r.returncode == 0 and os.path.exists(dst)
                if not ok:
                    print(f"  !! sips failed {slug}/{f}: {r.stderr.decode()[:80]}", file=sys.stderr)
            else:
                # already web-sized: copy bytes unchanged
                shutil.copy2(src, dst)
                ok = os.path.exists(dst)
            if ok:
                copied.append(f)
                total_copied += 1
        # existing datasheet PDF already in Assets (mirrored previously)
        pdfs = sorted([f for f in os.listdir(ddir) if f.lower().endswith(".pdf")]) if os.path.isdir(ddir) else []
        # existing pdfthumb png (from prior commit) if present and no real photos
        manifest[slug] = {"images": copied, "pdfs": pdfs}
        print(f"{slug:18} imgs={len(copied):2}  pdf={pdfs[:1]}")
    with open(os.path.join(REPO, "scripts", "garvan_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    print(f"\nTOTAL images copied/optimized: {total_copied} across {len(slugs)} slugs")

if __name__ == "__main__":
    main()
