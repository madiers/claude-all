#!/usr/bin/env python3
"""Mirror every vendor-hosted asset (Thumbnail / Specsheet / Gallery URLs) referenced
in scripts/asset_urls.json into the repo under Assets/<brand>/<slug>/...

Builds scripts/asset_local_paths.json mapping vendor URL -> repo-relative local path.
Used by rewrite_batch_csv.py to produce the final batch CSV with
raw.githubusercontent.com URLs.

Run repeatedly — skips files that already exist with non-zero size and a sane header
(PDF magic bytes for PDFs, image magic for images).
"""
import json, os, sys, time, urllib.parse, urllib.request, ssl, mimetypes
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
os.makedirs('Assets', exist_ok=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
CTX = ssl.create_default_context()

def safe_name(s):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:200]

def derive_ext(url, content_type=None, default=""):
    p = urllib.parse.urlparse(url)
    base = os.path.basename(p.path)
    if "." in base:
        ext = "." + base.rsplit(".",1)[1].split("?")[0].lower()
        if 1 < len(ext) <= 6: return ext
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or default
        return ext
    return default

PDF_MAGIC = b"%PDF"
IMG_MAGICS = [b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"RIFF", b"<?xml", b"<svg",
              b"\x00\x00\x00", b"BM"]  # png, jpg, gif, webp, svg, mp4ish, bmp

def is_valid(kind, data):
    if not data or len(data) < 100: return False
    if kind == "Specsheet": return data[:4] == PDF_MAGIC
    if kind in ("Thumbnail","Gallery"):
        return any(data.startswith(m) for m in IMG_MAGICS) or b"<svg" in data[:200] or b"<?xml" in data[:200]
    return True

def skip_url(url):
    if not url or not url.startswith("http"): return ("not-http", url)
    host = urllib.parse.urlparse(url).netloc.lower()
    # Dropbox folder URLs aren't direct files
    if "dropbox.com/scl/fo/" in url: return ("dropbox-folder", url)
    # LEA gated download pages aren't direct PDFs (often render an HTML page)
    if "leaprofessional.com/download/" in url: return ("lea-gated", url)
    return None

def download(url, out, kind, timeout=30, attempts=2):
    if os.path.exists(out) and os.path.getsize(out) > 1024:
        # Already there; trust it
        return ("skip-exists", os.path.getsize(out))
    sk = skip_url(url)
    if sk: return sk
    last_err = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                ct = r.headers.get("Content-Type","")
                data = r.read()
            if not is_valid(kind, data):
                last_err = f"invalid-content kind={kind} bytes={len(data)} ct={ct} starts={data[:8]!r}"
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "wb") as f: f.write(data)
            return ("ok", len(data))
        except HTTPError as e:
            last_err = f"http-{e.code}"
        except (URLError, TimeoutError, ConnectionError, OSError) as e:
            last_err = f"{type(e).__name__}: {e}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
    return ("fail", last_err)

def task(brand, slug, kind, url, idx=None):
    """Return (job_key, status, info, local_path)."""
    ext = derive_ext(url, default=".bin")
    # Conservative ext fallbacks
    if kind == "Specsheet" and ext not in (".pdf",): ext = ".pdf"
    if kind in ("Thumbnail","Gallery") and ext == ".bin": ext = ".jpg"

    if kind == "Specsheet":
        name = f"{slug}_datasheet.pdf"
    elif kind == "Thumbnail":
        name = f"{slug}_main{ext}"
    else:
        name = f"{slug}_gallery_{idx}{ext}"
    out = f"Assets/{safe_name(brand)}/{safe_name(slug)}/{safe_name(name)}"
    status, info = download(url, out, kind)
    key = f"{brand}|{slug}|{kind}|{idx if idx is not None else ''}"
    return (key, status, info, out, url)

def main():
    asset_urls = json.load(open("scripts/asset_urls.json"))
    jobs = []
    for brand, slugs in asset_urls.items():
        for slug, assets in slugs.items():
            if "Thumbnail" in assets:
                jobs.append((brand, slug, "Thumbnail", assets["Thumbnail"], None))
            if "Specsheet" in assets:
                jobs.append((brand, slug, "Specsheet", assets["Specsheet"], None))
            if "Gallery" in assets and isinstance(assets["Gallery"], list):
                for i, u in enumerate(assets["Gallery"][:8], start=1):  # cap gallery at 8
                    jobs.append((brand, slug, "Gallery", u, i))

    print(f"Mirror plan: {len(jobs)} downloads")

    stats = {"ok":0,"skip-exists":0,"fail":0,"dropbox-folder":0,"lea-gated":0,"not-http":0}
    failures = []
    url_to_path = {}  # vendor URL -> local path

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(task, *j) for j in jobs]
        for i, fut in enumerate(as_completed(futures)):
            try:
                key, status, info, out, url = fut.result()
            except Exception as e:
                print(f"  EXC: {e}", file=sys.stderr)
                stats["fail"] += 1
                continue
            stats[status] = stats.get(status, 0) + 1
            if status == "ok" or status == "skip-exists":
                url_to_path[url] = out
            else:
                failures.append((status, info, url))
            if (i+1) % 50 == 0 or i+1 == len(jobs):
                print(f"  [{i+1}/{len(jobs)}]  ok={stats.get('ok',0)} skip={stats.get('skip-exists',0)} "
                      f"dropbox={stats.get('dropbox-folder',0)} lea={stats.get('lea-gated',0)} "
                      f"not-http={stats.get('not-http',0)} fail={stats.get('fail',0)}",
                      flush=True)

    print(f"\nDone. Stats: {stats}")
    print(f"Total local files mapped: {len(url_to_path)}")
    print(f"Failures: {len(failures)} (sample 10:)")
    for s, info, u in failures[:10]:
        print(f"  [{s}] {info}  {u[:120]}")

    with open("scripts/asset_local_paths.json","w") as f:
        json.dump(url_to_path, f, indent=2, sort_keys=True)
    with open("scripts/mirror_failures.json","w") as f:
        json.dump(
            [{"status":s,"info":str(i),"url":u} for s,i,u in failures],
            f, indent=2, sort_keys=True)
    print(f"\nWrote scripts/asset_local_paths.json + scripts/mirror_failures.json")

if __name__ == "__main__":
    main()
