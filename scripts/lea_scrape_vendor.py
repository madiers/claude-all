#!/usr/bin/env python3
"""Scrape LEA Professional product renders for the WHOLE catalogue
(scripts/lea_catalog.py) from leaprofessional.com and mirror them into
Assets/lea/_renders/, then record slug -> [image relpaths] in
scripts/lea_scrape_manifest.json.

Renders live at
/wp-content/uploads/2022/08/<TOKEN>_Connect_Series_LEA_Professional_<view>_NOSHADOW.png
(view in Front/Back/FrontBack; casing varies). CS1504 and the half-rack models
use one-off filenames (declared as 'special' in the catalogue). Many catalogue
slugs share one chassis render (ADSP / Dante / Government / CDS variants of a
power class are the same box), so renders are stored once and referenced by each.
"""
import os, sys, ssl, json, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lea_catalog import catalog

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERS = os.path.join(REPO, "Assets", "lea", "_renders")
UP = "https://leaprofessional.com/wp-content/uploads/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
VIEWS = ["Front", "Back", "FrontBack", "FRONT", "BACK", "FRONT-BACK"]

# one-off renders that don't follow the /2022/08/<TOKEN>_..._NOSHADOW pattern
SPECIAL_SRC = {
    "Assets/lea/_renders/1504-front.png": "2024/07/1504-front.png",
    "Assets/lea/_renders/Front-_-Back_1504D.png": "2022/06/Front-_-Back_1504D.png",
    "Assets/lea/_renders/Half-Rack-Front.png": "2025/04/Half-Rack-Front.png",
    "Assets/lea/_renders/CS3004-Front.png": "2025/01/CS3004-Front.png",
    "Assets/lea/_renders/CS3004-Front-and-Back.png": "2025/01/CS3004-Front-and-Back.png",
    "Assets/lea/_renders/CS3004-back-panel.png": "2025/01/CS3004-back-panel.png",
    "Assets/lea/_renders/CS3004D-Front-and-Back.png": "2025/01/CS3004D-Front-and-Back.png",
    "Assets/lea/_renders/CS3004D-back.png": "2025/01/CS3004D-back.png",
}

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

def download(rel, dest):
    if not os.path.exists(dest):
        d = fetch(UP + urllib.parse.quote(rel))
        if not magic_ok(d):
            print(f"  !! not image: {rel}"); return False
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(d)
    return True

def token_renders(tok):
    """repo relpaths for the existing NOSHADOW renders of a token."""
    out, seen = [], set()
    for v in VIEWS:
        key = v.lower().replace("-", "")
        if key in seen:
            continue
        rel = f"2022/08/{tok}_Connect_Series_LEA_Professional_{v}_NOSHADOW.png"
        if head_ok(UP + urllib.parse.quote(rel)):
            dest = os.path.join(RENDERS, os.path.basename(rel))
            if download(rel, dest):
                seen.add(key); out.append(os.path.relpath(dest, REPO))
    return out

def main():
    os.makedirs(RENDERS, exist_ok=True)
    tok_cache = {}
    manifest = {}
    for m in catalog():
        kind, val = m["render"]
        if kind == "special":
            rels = []
            for relpath in val:
                src = SPECIAL_SRC.get(relpath)
                dest = os.path.join(REPO, relpath)
                if src and download(src, dest):
                    rels.append(relpath)
                elif os.path.exists(dest):
                    rels.append(relpath)
        else:  # token
            if val not in tok_cache:
                tok_cache[val] = token_renders(val)
            rels = list(tok_cache[val])
        manifest[m["slug"]] = sorted(dict.fromkeys(rels))
        print(f"{m['slug']:14} {str(val)[:22]:22} imgs={len(manifest[m['slug']])}")
    json.dump(manifest, open(os.path.join(REPO, "scripts", "lea_scrape_manifest.json"), "w"), indent=1)
    tot = len(set(p for v in manifest.values() for p in v))
    empty = [s for s, v in manifest.items() if not v]
    print(f"\n{len(manifest)} slugs | {tot} distinct render files | empty: {empty}")

if __name__ == "__main__":
    main()
