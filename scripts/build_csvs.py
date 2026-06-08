#!/usr/bin/env python3
"""Build the 4 import CSVs (per user request, 2026-06-08):

  Garvan_Products.csv  Fasttel_Products.csv   product data, NO image columns:
      Slug, :draft, Title, Sub Title, Product Description, Technical Table,
      Brand, Product Categories, Product Tags, Specsheet
  Garvan_Images.csv    Fasttel_Images.csv     slug -> image mapping:
      Slug, Thumbnail, Thumbnail:alt, Gallery

Rules honored:
- Product Categories / Tags use ONLY values already present in the live export
  ("the ones you saw there"): categories audio / cinema,audio; tags speaker,
  subwoofer, amplifier, acoustic-sound-panels, outdoor, door-phone, touch-panel,
  faceplates, install-kit, controller, ...  No new slugs are invented.
- Every product gets a Technical Table (a simple Model/Brand/Type one for Garvan
  where the catalog has no spec data; a full spec table for Fasttel).
- Every image row gets a Thumbnail:alt.
"""
import csv, json, os, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(REPO, "Products_Famer_latest_6-56pm.csv")
G_MAN = json.load(open(os.path.join(REPO, "scripts", "garvan_manifest.json")))
F_RES = json.load(open(os.path.join(REPO, "scripts", "research_fasttel.json")))
F_MAN = json.load(open(os.path.join(REPO, "scripts", "fasttel_manifest.json")))

BRANCH = "claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}/"
PCOLS = ['Slug', ':draft', 'Title', 'Sub Title', 'Product Description',
         'Technical Table', 'Brand', 'Product Categories', 'Product Tags', 'Specsheet']
ICOLS = ['Slug', 'Thumbnail', 'Thumbnail:alt', 'Gallery']

def raw_url(path):
    return RAW + urllib.parse.quote(path)

def hosted(u):
    u = (u or "").strip()
    return u.startswith("https://framerusercontent.com/") or u.startswith("https://raw.githubusercontent.com/")

def tech_table(pairs):
    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in pairs if v)
    return ("<table><tbody><tr><th>Specification</th><th>Value</th></tr>"
            + rows + "</tbody></table>")

# ---------------- Garvan ----------------
ACOUSTIC_SLUGS = {"cinematelier", "atelier", "acoustic-parquet", "microbaffle",
                  "quadra", "sound-quadra", "surface"}
def garvan_type_tags(slug, title, sub, desc):
    text = f"{title} {sub} {desc}".lower()
    is_acoustic = (slug in ACOUSTIC_SLUGS or (slug.startswith("ka") and slug.endswith("h"))
                   or any(w in text for w in ("acoustic panel", "sound panel", "absorber",
                          "diffuser", "parquet", "baffle", "acoustic treatment")))
    if is_acoustic:
        return "cinema,audio", "acoustic-sound-panels", "Acoustic panel"
    if "subwoofer" in text or "sub-woofer" in text:
        tag, typ = "subwoofer", "Subwoofer"
    elif "amplifier" in text or "amplifiers" in text:
        tag, typ = "amplifier", "Amplifier"
    else:
        tag, typ = "speaker", "Loudspeaker"
    if any(w in text for w in ("outdoor", "weather", "garden", "marine", "all-weather", "alfresco")):
        tag = tag + ",outdoor"
        typ = typ + " (outdoor)"
    return "audio", tag, typ

def pick_datasheet(pdfs, slug):
    if not pdfs: return None
    pref = [p for p in pdfs if "datasheet" in p.lower()]
    if pref: return pref[0]
    key = slug.replace("-", "").replace("_", "")
    pref = [p for p in pdfs if key in p.lower().replace("-", "").replace("_", "")]
    return (pref or pdfs)[0]

def build_garvan():
    live = list(csv.DictReader(open(LIVE, newline="", encoding="utf-8")))
    g = {r["Slug"]: r for r in live if r.get("Brand") == "garvan-acoustics"}
    prods, imgs = [], []
    for slug in sorted(g):
        b = g[slug]
        title = (b.get("Title") or slug).strip()
        sub = (b.get("Sub Title") or "").strip()
        desc = (b.get("Product Description") or "").strip()
        cat, tags, typ = garvan_type_tags(slug, title, sub, desc)
        m = G_MAN.get(slug, {"images": [], "pdfs": []})
        # Specsheet: keep hosted, else mirrored datasheet
        spec = b.get("Specsheet", "") if hosted(b.get("Specsheet")) else ""
        if not spec:
            ds = pick_datasheet(m["pdfs"], slug)
            if ds: spec = raw_url(f"Assets/garvan-acoustics/{slug}/{ds}")
        prods.append({
            "Slug": slug, ":draft": b.get(":draft", "false") or "false",
            "Title": title, "Sub Title": sub, "Product Description": desc,
            "Technical Table": tech_table([("Model", title), ("Brand", "Garvan Acoustics"),
                                           ("Type", typ)]),
            "Brand": "garvan-acoustics", "Product Categories": cat,
            "Product Tags": tags, "Specsheet": spec,
        })
        # image row
        photos = m["images"]
        if photos:
            thumb = raw_url(f"Assets/garvan-acoustics/{slug}/{photos[0]}")
            gallery = ", ".join(raw_url(f"Assets/garvan-acoustics/{slug}/{f}") for f in photos)
        else:
            thumb = b.get("Thumbnail", "") if hosted(b.get("Thumbnail")) else ""
            gallery = ""
        alt = " ".join((sub or f"{title} — Garvan Acoustics").split())
        imgs.append({"Slug": slug, "Thumbnail": thumb, "Thumbnail:alt": alt[:160], "Gallery": gallery})
    return prods, imgs

# ---------------- Fasttel ----------------
def build_fasttel():
    live = list(csv.DictReader(open(LIVE, newline="", encoding="utf-8")))
    flive = {r["Slug"]: r for r in live if r.get("Brand") == "fasttel"}
    live_slugs = set(flive)
    prods, imgs = [], []
    for p in F_RES["products"]:
        slug = p["slug"]
        is_new = slug not in live_slugs
        b = flive.get(slug, {})
        # non-destructive: prefer live copy for existing rows
        title = (b.get("Title") or p["title"]).strip()
        sub = (b.get("Sub Title") or p["sub_title"]).strip()
        desc = (b.get("Product Description") or p["description"]).strip()
        # category: restrict to values present in the live export (audio / cinema,audio)
        cat = "audio"
        # tags: research (already filtered to the live vocab); keep live door-phone if present
        tags = list(dict.fromkeys(p.get("tags", [])))
        if not tags:
            tags = ["door-phone"]
        man = F_MAN.get(slug, {"images": [], "datasheet": None})
        spec = raw_url(man["datasheet"]) if man.get("datasheet") else (b.get("Specsheet", "") if hosted(b.get("Specsheet")) else "")
        prods.append({
            "Slug": slug, ":draft": "true" if is_new else "false",
            "Title": title, "Sub Title": sub, "Product Description": desc,
            "Technical Table": tech_table([(s["label"], s["value"]) for s in p.get("specs", [])]
                                          or [("Brand", "Fasttel"), ("Model", title)]),
            "Brand": "fasttel", "Product Categories": cat,
            "Product Tags": ",".join(tags), "Specsheet": spec,
        })
        photos = man["images"]
        if photos:
            thumb = raw_url(f"Assets/fasttel/{slug}/{photos[0]}")
            gallery = ", ".join(raw_url(f"Assets/fasttel/{slug}/{f}") for f in photos)
        else:
            thumb = b.get("Thumbnail", "") if hosted(b.get("Thumbnail")) else ""
            gallery = ""
        alt = " ".join(f"{title} — {sub}".split()) if sub else f"{title} — Fasttel"
        imgs.append({"Slug": slug, "Thumbnail": thumb, "Thumbnail:alt": alt[:160], "Gallery": gallery})
    return prods, imgs

def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    print(f"  {os.path.basename(path):22} {len(rows):3} rows")

def main():
    gp, gi = build_garvan()
    fp, fi = build_fasttel()
    print("written:")
    write_csv(os.path.join(REPO, "Garvan_Products.csv"), PCOLS, gp)
    write_csv(os.path.join(REPO, "Garvan_Images.csv"), ICOLS, gi)
    write_csv(os.path.join(REPO, "Fasttel_Products.csv"), PCOLS, fp)
    write_csv(os.path.join(REPO, "Fasttel_Images.csv"), ICOLS, fi)
    # quick coverage stats
    print("\nGarvan: cats", {r['Product Categories'] for r in gp},
          "| imgrows w/thumb:", sum(1 for r in gi if r['Thumbnail']))
    print("Fasttel: drafts", sum(1 for r in fp if r[':draft']=='true'),
          "live", sum(1 for r in fp if r[':draft']=='false'),
          "| imgrows w/thumb:", sum(1 for r in fi if r['Thumbnail']),
          "| specsheets:", sum(1 for r in fp if r['Specsheet']))

if __name__ == "__main__":
    main()
