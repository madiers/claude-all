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
import csv, json, os, urllib.parse, html as _html

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(REPO, "Products_Famer_latest_6-56pm.csv")
G_MAN = json.load(open(os.path.join(REPO, "scripts", "garvan_manifest.json")))
F_RES = json.load(open(os.path.join(REPO, "scripts", "research_fasttel.json")))
F_MAN = json.load(open(os.path.join(REPO, "scripts", "fasttel_manifest.json")))

BRANCH = "claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}/"
PCOLS = ['Slug', ':draft', 'Title', 'Sub Title', 'Product Description',
         'Technical Table', 'Brand', 'Product Categories', 'Product Tags', 'Specsheet']
# Image CSV carries Title + Product Description because Framer's CSV importer
# refuses to map an update unless the required "Product Description" field is
# present ("Map the required field 'Product Description'"). Values are the same
# cleaned copy as the products CSV, so re-importing images is non-destructive.
ICOLS = ['Slug', 'Title', 'Product Description', 'Thumbnail', 'Thumbnail:alt', 'Gallery']

def raw_url(path):
    return RAW + urllib.parse.quote(path)

def hosted(u):
    u = (u or "").strip()
    return u.startswith("https://framerusercontent.com/") or u.startswith("https://raw.githubusercontent.com/")

def tech_table(pairs):
    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in pairs if v)
    return ("<table><tbody><tr><th>Specification</th><th>Value</th></tr>"
            + rows + "</tbody></table>")

# ---- Wix Ricos JSON -> clean HTML --------------------------------------------
# Several Garvan products were migrated from Wix with raw Ricos document JSON
# ({"nodes":[...]}) sitting in the Product Description cell (often wrapped in a
# single <p>). Framer renders that as literal JSON. Convert it to plain HTML.
def _esc(t):
    return _html.escape(t or "", quote=False)

def _inline(tn):
    td = tn.get("textData", {}) or {}
    s = _esc(td.get("text", "").replace("\r", "")).replace("\n", "<br>")
    bold = ital = und = False
    link = None
    for d in td.get("decorations", []) or []:
        ty = d.get("type")
        if ty == "BOLD": bold = True
        elif ty == "ITALIC": ital = True
        elif ty == "UNDERLINE": und = True
        elif ty == "LINK": link = ((d.get("linkData", {}) or {}).get("link", {}) or {}).get("url")
    if und: s = f"<u>{s}</u>"
    if ital: s = f"<em>{s}</em>"
    if bold: s = f"<strong>{s}</strong>"
    if link: s = f'<a href="{_esc(link)}">{s}</a>'
    return s

def _inline_children(node):
    s = "".join(_inline(c) for c in node.get("nodes", []) if c.get("type") == "TEXT").strip()
    while s.startswith("<br>"): s = s[4:].strip()
    while s.endswith("<br>"): s = s[:-4].strip()
    return s

def _para(p):
    return _inline_children(p) if p.get("type") == "PARAGRAPH" else ""

def _render_ricos(nodes):
    out = []
    for n in nodes:
        t = n.get("type")
        if t == "PARAGRAPH":
            inner = _inline_children(n)
            if inner: out.append(f"<p>{inner}</p>")
        elif t == "HEADING":
            lvl = max(2, min(6, int((n.get("headingData", {}) or {}).get("level", 3))))
            inner = _inline_children(n)
            if inner: out.append(f"<h{lvl}>{inner}</h{lvl}>")
        elif t in ("BULLETED_LIST", "ORDERED_LIST"):
            tag = "ul" if t == "BULLETED_LIST" else "ol"
            items = []
            for li in n.get("nodes", []):
                if li.get("type") != "LIST_ITEM": continue
                txt = " ".join(filter(None, (_para(p) for p in li.get("nodes", []))))
                if txt: items.append(f"<li>{txt}</li>")
            if items: out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
        elif t == "TABLE":
            rws = []
            for r in n.get("nodes", []):
                if r.get("type") != "TABLE_ROW": continue
                cells = ["<td>" + " ".join(filter(None, (_para(p) for p in c.get("nodes", [])))) + "</td>"
                         for c in r.get("nodes", []) if c.get("type") == "TABLE_CELL"]
                if cells: rws.append("<tr>" + "".join(cells) + "</tr>")
            if rws: out.append("<figure><table><tbody>" + "".join(rws) + "</tbody></table></figure>")
        # IMAGE / other node types: skipped (Wix media ids aren't usable URLs)
    return "".join(out)

def ricos_to_html(desc):
    s = (desc or "").strip()
    cand = s
    if cand.startswith("<p>") and cand.endswith("</p>"):
        cand = cand[3:-4].strip()
    if not (cand.startswith("{") and '"nodes"' in cand):
        return desc                      # already clean HTML — leave untouched
    try:
        data = json.loads(cand)
    except Exception:
        return desc
    return _render_ricos(data.get("nodes", [])) or desc

# ---------------- Garvan ----------------
# Garvan products that exist in the export with an EMPTY Brand (so the brand
# filter skipped them) — the SA/SN/WA CinemAtelier, LOTO & CORO lines. They
# carry raw Ricos JSON descriptions. Pull them in, brand + clean them.
ORPHAN_GARVAN = ["sa111", "sa117", "sa214", "sa225", "sa314", "sa317", "sa320",
                 "sn117", "snw23m", "atelier", "wa120", "wa420", "wae121", "wn120"]
ACOUSTIC_SLUGS = {"cinematelier", "atelier", "acoustic-parquet", "microbaffle",
                  "quadra", "sound-quadra", "surface"}
def garvan_type_tags(slug, title, sub, desc):
    text = f"{title} {sub} {desc}".lower()
    # NB: Garvan's marketing voice calls its 360° speakers "diffusers" ("marine
    # outdoor diffusers", "the other diffusers in the collection") — so the bare
    # words "diffuser"/"absorber" are NOT acoustic markers here. Require the
    # acoustic/sound qualifier to catch real acoustic-treatment panels only.
    is_acoustic = (slug in ACOUSTIC_SLUGS or (slug.startswith("ka") and slug.endswith("h"))
                   or any(w in text for w in ("acoustic panel", "sound panel", "parquet",
                          "baffle", "acoustic treatment", "sound-absorbing", "sound absorbing",
                          "acoustic absorber", "sound absorber", "acoustic diffuser",
                          "sound diffuser")))
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
    by_slug = {r["Slug"]: r for r in live}
    g = {s: r for s, r in by_slug.items() if r.get("Brand") == "garvan-acoustics"}
    # Pull in the SA/SN/WA orphans that ship with an EMPTY Brand (so the brand
    # filter skipped them, leaving their raw Ricos-JSON descriptions live).
    for slug in ORPHAN_GARVAN:
        if slug in by_slug and slug not in g:
            g[slug] = by_slug[slug]
    prods, imgs = [], []
    for slug in sorted(g):
        b = g[slug]
        title = (b.get("Title") or slug).strip()
        sub = (b.get("Sub Title") or "").strip()
        desc = ricos_to_html((b.get("Product Description") or "").strip())
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
        imgs.append({"Slug": slug, "Title": title, "Product Description": desc,
                     "Thumbnail": thumb, "Thumbnail:alt": alt[:160], "Gallery": gallery})
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
        imgs.append({"Slug": slug, "Title": title, "Product Description": desc,
                     "Thumbnail": thumb, "Thumbnail:alt": alt[:160], "Gallery": gallery})
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
