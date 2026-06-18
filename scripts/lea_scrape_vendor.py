#!/usr/bin/env python3
"""Scrape LEA Professional product renders from leaprofessional.com and mirror
them into the repo so Framer can fetch them, then the gallery goes in
LEA_Images.csv (galleries only, like MAG/Garvan).

LEA amps are rack units with a small set of studio renders per model, named
`/wp-content/uploads/2022/08/<MODEL>_Connect_Series_LEA_Professional_<view>_NOSHADOW.png`
(view in Front/Back/FrontBack; casing varies — CS168D uses FRONT/BACK/FRONT-BACK).
CS1504 and the half-rack models use one-off filenames. Many of our 20 catalog
slugs share one chassis render (the ADSP / Dante / Government / CDS variants of a
power class are the same box), so renders are stored once in Assets/lea/_renders/
and referenced by every slug that uses them.

Output: images in Assets/lea/_renders/, manifest scripts/lea_scrape_manifest.json.
"""
import os, ssl, json, urllib.request, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERS = os.path.join(REPO, "Assets", "lea", "_renders")
UP = "https://leaprofessional.com/wp-content/uploads/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# our 20 catalog slugs -> chassis render token (the box that's photographed)
CHASSIS = {
    "cs352-adsp": "CS352", "cs354-adsp": "CS354", "cs702-adsp": "CS702", "cs704-adsp": "CS704",
    "cs352d-adsp": "CS352D", "cs354d-adsp": "CS354D", "cs702d-adsp": "CS702D", "cs704d-adsp": "CS704D",
    "cs704d-g": "CS704D", "cds354": "CS354D", "cds704": "CS704D",
    "cs354": "CS354", "cs704": "CS704", "cs352d": "CS352D", "cs702d": "CS702D", "cs168d": "CS168D",
}
# slugs whose renders are one-off filenames (relpaths under wp-content/uploads/)
SPECIAL = {
    "cs1504":   ["2024/07/1504-front.png", "2022/06/Front-_-Back_1504D.png"],
    "cs1504-g": ["2024/07/1504-front.png", "2022/06/Front-_-Back_1504D.png"],
    "cs64d":    ["2025/04/Half-Rack-Front.png"],
    "cs124":    ["2025/04/Half-Rack-Front.png"],
}
VIEWS = ["Front", "Back", "FrontBack", "FRONT", "BACK", "FRONT-BACK"]

def head_ok(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
            return r.status == 200
    except Exception:
        return False

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
        return r.read()

def magic_ok(d):
    return d[:2] == b"\xff\xd8" or d[:8] == b"\x89PNG\r\n\x1a\n"

def token_renders(tok):
    """Relpaths (under uploads/) of the existing NOSHADOW renders for a token."""
    out, seen = [], set()
    for v in VIEWS:
        rel = f"2022/08/{tok}_Connect_Series_LEA_Professional_{v}_NOSHADOW.png"
        key = v.lower().replace("-", "")
        if key in seen:
            continue
        if head_ok(UP + urllib.parse.quote(rel)):
            seen.add(key); out.append(rel)
    return out

def download(rel):
    """Download uploads/<rel> into Assets/lea/_renders/, return repo relpath."""
    dest = os.path.join(RENDERS, os.path.basename(rel))
    if not os.path.exists(dest):
        d = fetch(UP + urllib.parse.quote(rel))
        if not magic_ok(d):
            print(f"  !! not image: {rel}"); return None
        os.makedirs(RENDERS, exist_ok=True)
        open(dest, "wb").write(d)
    return os.path.relpath(dest, REPO)

def main():
    os.makedirs(RENDERS, exist_ok=True)
    # resolve render relpaths per token once
    tok_cache = {}
    manifest = {}
    for slug in list(CHASSIS) + list(SPECIAL):
        rels = SPECIAL.get(slug)
        if rels is None:
            tok = CHASSIS[slug]
            if tok not in tok_cache:
                tok_cache[tok] = token_renders(tok)
            rels = tok_cache[tok]
        saved = []
        for rel in rels:
            try:
                p = download(rel)
            except Exception as e:
                print(f"  !! {slug} {rel[-30:]}: {str(e)[:40]}"); continue
            if p:
                saved.append(p)
        manifest[slug] = sorted(dict.fromkeys(saved))
        print(f"{slug:14} {CHASSIS.get(slug,'(special)'):8} imgs={len(saved)}")
    json.dump(manifest, open(os.path.join(REPO, "scripts", "lea_scrape_manifest.json"), "w"), indent=1)
    tot = len(set(p for v in manifest.values() for p in v))
    print(f"\n{len(manifest)} slugs | {tot} distinct render files | "
          f"{sum(1 for v in manifest.values() if v)} with images")
    print("empty:", [s for s, v in manifest.items() if not v])

if __name__ == "__main__":
    main()
