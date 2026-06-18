#!/usr/bin/env python3
"""Build the LEA split import: LEA_Products.csv (full product rows, with
thumbnails) + LEA_Images.csv (galleries only). Covers the WHOLE catalogue
(scripts/lea_catalog.py): the 20 products already in Framer are emitted
VERBATIM from the export (their thumbnails are left exactly as-is), and the ~26
missing models get full generated rows + the vendor render as their thumbnail.

Content for new rows is derived from LEA's model numbering (watts = num[:-1]*10,
channels = num[-1], 2 ohm = half power) and the per-series feature set, matching
the phrasing of the LEA rows already in the CMS. Images come from
Assets/lea/_renders/ (scripts/lea_scrape_vendor.py) over raw.githubusercontent.
"""
import os, sys, csv, json, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lea_catalog import catalog

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(REPO, "Products_18_june_MAG_Updated.csv")
MAN = json.load(open(os.path.join(REPO, "scripts", "lea_scrape_manifest.json")))
DSMAN = json.load(open(os.path.join(REPO, "scripts", "lea_datasheets_manifest.json")))
BRANCH = "claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/madiers/claude-all/{BRANCH}/"
PCOLS = ["Slug", ":draft", "Title", "Sub Title", "Product Description", "Technical Table",
         "Thumbnail", "Thumbnail:alt", "Brand", "Product Categories", "Product Tags", "Specsheet"]
ICOLS = ["Slug", "Product Description", "Gallery"]

def raw_url(p):
    return RAW + urllib.parse.quote(p)

def p2ohm(w):
    # LEA's high-power models hold full power at 2 ohm; smaller ones halve it
    return w if w >= 1500 else w // 2

# real vendor-researched copy for the few high-power new models (more accurate
# than the template); from scripts/audit_results/lea.json
_audit = json.load(open(os.path.join(REPO, "scripts", "audit_results", "lea.json")))
AUDIT = {p["slug"]: p for p in _audit.get("new_products", [])}

def pure_front(name):
    n = name.lower().replace("front-and-back", "X").replace("frontback", "X").replace("front-_-back", "X")
    return "front" in n and "back" not in n

def thumb_of(rels):
    fronts = [r for r in rels if pure_front(os.path.basename(r))]
    return (fronts or rels or [None])[0]

# ---- copy generation ----------------------------------------------------------
def series_phrase(m):
    if m["cinema"]:
        return "Cinema Digital Series"
    net = "Dante" if m["dante"] else "Network"
    if m["gov"]:
        return f"{('Dante-enabled ' if m['dante'] else '')}Government-model CONNECT Series".strip()
    return f"{net} CONNECT Series"

def sub_title(m):
    if m["dante"]:
        return f"SMART AMP WITH DANTE | {m['channels']} CH | {m['watts']} WATTS PER CH"
    return f"SMART AMP | {m['channels']} CHANNELS | {m['watts']} WATTS PER CHANNEL"

def description(m):
    w, half, ch = m["watts"], p2ohm(m["watts"]), m["channels"]
    imp = ("4&Omega;, 8&Omega;, 25V, 70V, and 100V" if m["cinema"]
           else "4&Omega;, 8&Omega;, 70V, and 100V")
    p1 = (f"The LEA Professional {m['label']} is a {ch}-channel {series_phrase(m)} smart "
          f"amplifier delivering {w} watts per channel at {imp} ({half}W at 2&Omega;).")
    if m["cinema"]:
        p1 += (" Purpose-built for cinema and immersive surround, it pairs AES67 audio-over-IP "
               "with LEA's cloud-based remote monitoring for theatrical and large-format rooms.")
    elif m["gov"]:
        p1 += (" As part of the CONNECT Series “G” (Government) line, all wireless "
               "capabilities are removed — connections are made strictly over wired LAN — "
               "for secure and government installations.")
    elif m["adsp"]:
        p1 += (" The “ADSP” designation denotes the Advanced DSP variant, upgrading the "
               "platform to an Analog Devices SHARC 96 kHz processor with linear-phase FIR "
               "crossovers, deeper IIR filtering, and extended per-channel delay.")
    elif m["dante"]:
        p1 += " It adds native Dante audio-over-IP networking on top of the CONNECT Series platform."
    else:
        p1 += (" Per-channel HiZ/LoZ selection and a network-connected design make it well suited "
               "to small and medium commercial installations.")
    if m["gov"]:
        conn = "Connectivity is wired-only via FAST Ethernet/LAN, with no onboard wireless."
    elif m["dante"]:
        conn = ("Three ways to connect — built-in Wi-Fi access point, existing Wi-Fi, or FAST "
                "Ethernet — are joined by native Dante for audio transport.")
    else:
        conn = ("Three ways to connect — built-in Wi-Fi access point, existing Wi-Fi, or FAST "
                "Ethernet — simplify network setup.")
    ctx = ("cinema and immersive surround systems" if m["cinema"]
           else "high-density distributed-audio systems" if ch >= 8
           else "compact, space-constrained racks" if m["half"]
           else "zoned commercial audio")
    p2 = (f"Every channel has onboard DSP with input/output processing, parametric EQ, high- and "
          f"low-pass crossovers, limiting, and delay. {conn} Power-over-network control, cloud "
          f"monitoring through the LEA platform, and selectable 70V/100V/low-impedance operation "
          f"per channel make {m['label']} straightforward to deploy and manage across {ctx}.")
    return f"<p>{p1}</p><p>{p2}</p>"

def tech_table(m):
    w, half, ch = m["watts"], p2ohm(m["watts"]), m["channels"]
    rows = [("Channels", str(ch)),
            ("Power per Channel (2&Omega;)", f"{half}W"),
            ("Power per Channel (4&Omega;)", f"{w}W"),
            ("Power per Channel (8&Omega;)", f"{w}W")]
    if m["cinema"]:
        rows.append(("Power per Channel (25V)", f"{w}W"))
    rows += [("Power per Channel (70V)", f"{w}W"),
             ("Power per Channel (100V)", f"{w}W"),
             ("Audio Inputs", "Analog balanced + AES67" if m["cinema"]
              else "Analog balanced + Dante" if m["dante"] else "Analog balanced"),
             ("Network", "FAST Ethernet (wired LAN only)" if m["gov"]
              else "Wi-Fi AP, Wi-Fi, or FAST Ethernet" + (" + Dante" if m["dante"] else "")),
             ("DSP", "Advanced DSP — Analog Devices SHARC 96 kHz (FIR + IIR)" if m["adsp"]
              else "Onboard DSP — EQ, crossovers, limiting, delay per channel"),
             ("Output Modes", ("Low-Z, 25V, 70V, 100V" if m["cinema"] else "Low-Z, 70V, 100V")
              + " selectable per channel"),
             ("Cloud", "LEA cloud monitoring & control"),
             ("Chassis", "Half-rack" if m["half"] else "1U rack")]
    body = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    return f"<table><tbody>{body}</tbody></table>"

def new_row(m):
    th = thumb_of(MAN.get(m["slug"], []))
    a = AUDIT.get(m["slug"], {})
    desc = a.get("description") or description(m)
    tt = a.get("technical_table") or tech_table(m)
    return {
        "Slug": m["slug"], ":draft": "true", "Title": m["label"],
        "Sub Title": sub_title(m), "Product Description": desc,
        "Technical Table": tt,
        "Thumbnail": raw_url(th) if th else "",
        "Thumbnail:alt": f"{m['label']} — LEA Professional {m['channels']}-channel {m['watts']}W smart amplifier",
        "Brand": "lea", "Product Categories": "audio", "Product Tags": "amplifier",
        "Specsheet": raw_url(DSMAN[m["slug"]]) if DSMAN.get(m["slug"]) else "",
    }

def main():
    export = {r["Slug"]: r for r in csv.DictReader(open(EXPORT, newline="", encoding="utf-8"))
              if r.get("Brand") == "lea"}
    prods, imgs = [], []
    n_new = n_exist = 0
    for m in catalog():
        slug = m["slug"]
        if slug in export:                       # leave existing exactly as-is
            e = export[slug]
            row = {c: e.get(c, "") for c in PCOLS}
            if not row["Thumbnail"].strip():     # nothing to preserve -> fill from render
                th = thumb_of(MAN.get(slug, []))
                if th:
                    row["Thumbnail"] = raw_url(th)
            if not row["Specsheet"].strip() and DSMAN.get(slug):  # fill empty datasheet
                row["Specsheet"] = raw_url(DSMAN[slug])
            prods.append(row)
            desc = e.get("Product Description", "")
            n_exist += 1
        else:
            row = new_row(m)
            prods.append(row)
            desc = row["Product Description"]
            n_new += 1
        gallery = ",".join(raw_url(p) for p in MAN.get(slug, []))
        imgs.append({"Slug": slug, "Product Description": desc, "Gallery": gallery})

    for path, cols, rows in [("LEA_Products.csv", PCOLS, prods), ("LEA_Images.csv", ICOLS, imgs)]:
        with open(os.path.join(REPO, path), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
        print(f"  {path:18} {len(rows)} rows")
    no_thumb = [r["Slug"] for r in prods if not r["Thumbnail"]]
    no_gal = [r["Slug"] for r in imgs if not r["Gallery"].strip()]
    print(f"existing kept verbatim: {n_exist} | new generated: {n_new}")
    print(f"rows without thumbnail: {no_thumb or 'none'}")
    print(f"rows without gallery: {no_gal or 'none'}")

if __name__ == "__main__":
    main()
