#!/usr/bin/env python3
"""Mirror LEA spec-sheet PDFs into the repo so Framer's Specsheet field can use
them (it only accepts raw.githubusercontent / framerusercontent URLs, not LEA's
gated /download/ pages).

LEA serves datasheets through WordPress Download Manager: a /download/<slug>/
page exposes a `?wpdmdl=<id>` link that returns the PDF directly. Each catalogue
model is resolved to its spec-sheet slug (model-specific where one exists, the
shared Connect-Series sheet otherwise), the PDF is downloaded once per slug into
Assets/lea/_datasheets/, and slug->pdf is written to
scripts/lea_datasheets_manifest.json.
"""
import os, re, ssl, sys, json, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lea_catalog import catalog

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS = os.path.join(REPO, "Assets", "lea", "_datasheets")
BASE = "https://leaprofessional.com/download/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# spec-sheet download slugs that exist on leaprofessional.com (harvested from the
# series pages); used to pick the most specific real sheet per model.
VALID = {
    "1504-g-spec-sheet", "1504d-g-spec-sheet", "354-g-spec-sheet", "354d-g-spec-sheet",
    "702-g-spec-sheet", "704-g-spec-sheet", "704d-g-spec-sheet",
    "cds-352-spec-sheet", "cds-354-spec-sheet", "cds-702-spec-sheet", "cds-704-spec-sheet",
    "spec-sheet-cds-1504", "cinema-digital-series-spec-sheet",
    "spec-sheet-1504", "spec-sheet-1504d", "spec-sheet-164d", "spec-sheet-168d",
    "spec-sheet-3004", "spec-sheet-3004d", "spec-sheet-84d",
    "spec-sheet-352-adsp", "spec-sheet-352d-adsp", "spec-sheet-354-adsp", "spec-sheet-354d-adsp",
    "spec-sheet-702-adsp", "spec-sheet-702d-adsp", "spec-sheet-704-adsp", "spec-sheet-704d-adsp",
    "spec-sheet-352d", "spec-sheet-354d", "spec-sheet-702d", "spec-sheet-704d",
    "spec-sheet-dante-connect-series", "spec-sheet-dante-connect-adsp",
    "spec-sheet-network-connect-adsp",
}
FAMILY = "spec-sheet-dante-connect-series"   # broadest Connect-Series sheet

def slug_for(m):
    num, d = m["num"], ("d" if m["dante"] else "")
    if m["cinema"]:
        cands = [f"cds-{num}-spec-sheet", "spec-sheet-cds-1504", "cinema-digital-series-spec-sheet"]
    elif m["gov"]:
        cands = [f"{num}{d}-g-spec-sheet"]
    elif m["adsp"]:
        cands = [f"spec-sheet-{num}{d}-adsp",
                 "spec-sheet-dante-connect-adsp" if m["dante"] else "spec-sheet-network-connect-adsp"]
    else:
        cands = [f"spec-sheet-{num}{d}", f"spec-sheet-{num}"]
    for c in cands:
        if c in VALID:
            return c
    return FAMILY

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")

def wpdmdl_id(slug):
    html = get(BASE + slug + "/")
    m = re.search(r"wpdmdl=(\d+)", html)
    return m.group(1) if m else None

def fetch_pdf(slug):
    dest = os.path.join(DS, slug + ".pdf")
    if os.path.exists(dest):
        return os.path.relpath(dest, REPO)
    wid = wpdmdl_id(slug)
    if not wid:
        print(f"  !! no wpdmdl for {slug}"); return None
    data = get(f"{BASE}{slug}/?wpdmdl={wid}", binary=True)
    if data[:4] != b"%PDF":
        print(f"  !! not a PDF: {slug} (wpdmdl={wid})"); return None
    os.makedirs(DS, exist_ok=True)
    open(dest, "wb").write(data)
    return os.path.relpath(dest, REPO)

def main():
    os.makedirs(DS, exist_ok=True)
    pdf_cache, manifest = {}, {}
    for m in catalog():
        slug = slug_for(m)
        if slug not in pdf_cache:
            try:
                pdf_cache[slug] = fetch_pdf(slug)
            except Exception as e:
                print(f"  !! {slug}: {str(e)[:50]}"); pdf_cache[slug] = None
        rel = pdf_cache[slug]
        manifest[m["slug"]] = rel
        print(f"{m['slug']:14} -> {slug:34} {'OK' if rel else 'FAIL'}")
    json.dump(manifest, open(os.path.join(REPO, "scripts", "lea_datasheets_manifest.json"), "w"), indent=1)
    have = sum(1 for v in manifest.values() if v)
    print(f"\n{have}/{len(manifest)} models have a datasheet | "
          f"{len(set(v for v in pdf_cache.values() if v))} distinct PDFs")
    print("missing:", [s for s, v in manifest.items() if not v])

if __name__ == "__main__":
    main()
