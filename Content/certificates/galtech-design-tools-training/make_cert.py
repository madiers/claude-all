#!/usr/bin/env python3
"""Galtech Design Tools Training - certificate generator (web + PDF)."""
import os, html, subprocess, sys

REPO="/Users/madiyarismagulov/Library/CloudStorage/GoogleDrive-info@verstack.design/My Drive/Verstack Projects/Marketing/Galtech/claude-all-1"
OUT=os.path.join(REPO,"Content/certificates/galtech-design-tools-training")
os.makedirs(os.path.join(OUT,"pdf"),exist_ok=True)
os.makedirs(os.path.join(OUT,"html"),exist_ok=True)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOGO_B64=open("/tmp/logo_ink_b64.txt").read().strip()

TEMPLATE=r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Galtech Certificate __NAME__</title>
<style>
  @page {{ size: 297mm 210mm; margin: 0; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  :root {{
    --ink:#0e1730; --ink2:#1b2745; --blue:#2f6bff; --blue2:#7fb0ff;
    --muted:#6b7284; --line:#d7deec; --paper:#fbfcff;
  }}
  html,body {{ width:297mm; height:209.6mm; }}
  body {{
    font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; color:var(--ink);
    background:var(--paper); -webkit-print-color-adjust:exact; print-color-adjust:exact;
    position:relative; overflow:hidden;
  }}
  .bg {{ position:absolute; inset:0; z-index:0; overflow:hidden; }}
  .bg .glow {{ position:absolute; left:50%; top:-14mm; width:180mm; height:120mm;
    transform:translateX(-50%);
    background:radial-gradient(ellipse at center, rgba(47,107,255,.10), rgba(47,107,255,0) 62%); }}
  .bg .wm {{ position:absolute; left:50%; top:53%; transform:translate(-50%,-50%);
    font-family:"Didot","Baskerville",Georgia,serif; font-size:150mm; font-weight:700;
    color:rgba(14,23,48,.028); letter-spacing:-6px; }}
  /* frame */
  .frame {{ position:absolute; inset:9mm; border:1.6px solid var(--ink);
    z-index:1; }}
  .frame:before {{ content:""; position:absolute; inset:2.6mm; border:0.7px solid rgba(47,107,255,.55); }}
  .corner {{ position:absolute; width:15mm; height:15mm; z-index:2; }}
  .corner svg {{ width:100%; height:100%; }}
  .corner.tl {{ top:6.4mm; left:6.4mm; }}
  .corner.tr {{ top:6.4mm; right:6.4mm; transform:scaleX(-1); }}
  .corner.bl {{ bottom:6.4mm; left:6.4mm; transform:scaleY(-1); }}
  .corner.br {{ bottom:6.4mm; right:6.4mm; transform:scale(-1,-1); }}
  /* content */
  .wrap {{ position:absolute; inset:9mm; z-index:3; display:flex; flex-direction:column;
    align-items:center; text-align:center; padding:15mm 26mm 12mm; }}
  .logo {{ height:12mm; margin-bottom:2.5mm; }}
  .tag {{ font-size:8.5px; letter-spacing:4.5px; color:var(--muted); text-transform:uppercase; }}
  .seal {{ margin:6.5mm 0 5mm; }}
  .kicker {{ font-size:11px; letter-spacing:8px; color:var(--blue); text-transform:uppercase;
    font-weight:600; }}
  h1 {{ font-family:"Didot","Baskerville",Georgia,serif; font-weight:700; font-size:33px;
    letter-spacing:5px; text-transform:uppercase; color:var(--ink); margin-top:3mm; }}
  .divider {{ width:34mm; height:2px; margin:5mm 0 6mm;
    background:linear-gradient(90deg,transparent,var(--blue),transparent); }}
  .pre {{ font-size:12.5px; color:var(--muted); letter-spacing:.6px; }}
  .name {{ font-family:"Snell Roundhand","Didot",Georgia,serif; font-size:58px; font-weight:600;
    color:var(--ink); line-height:1.05; margin:3.5mm 0 1.5mm;
    background:linear-gradient(180deg,var(--ink),var(--ink2)); -webkit-background-clip:text;
    -webkit-text-fill-color:transparent; }}
  .name-rule {{ width:96mm; height:1px; background:var(--line); margin:0 0 2mm; }}
  .company {{ font-size:13px; color:var(--blue); font-weight:600; letter-spacing:.4px;
    text-transform:uppercase; }}
  .body {{ max-width:190mm; font-size:14px; line-height:1.7; color:#31384a; margin-top:6mm; }}
  .body b {{ color:var(--ink); }}
  .meta {{ display:flex; gap:9mm; align-items:center; margin-top:7mm;
    font-size:11px; letter-spacing:2px; text-transform:uppercase; color:var(--ink); }}
  .meta .dot {{ width:4px; height:4px; border-radius:50%; background:var(--blue); }}
  .foot {{ position:absolute; left:34mm; right:34mm; bottom:20mm; z-index:3;
    display:flex; justify-content:center; align-items:flex-end; }}
  .sig {{ width:82mm; text-align:center; }}
  .sig .mark {{ height:11mm; }}
  .sig .sline {{ height:1px; background:var(--ink); opacity:.5; margin:1.5mm 0; }}
  .sig .sname {{ font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; font-size:13px;
    font-weight:600; color:var(--ink); letter-spacing:.4px; }}
  .sig .slabel {{ font-size:9px; letter-spacing:2.5px; text-transform:uppercase; color:var(--muted);
    margin-top:.8mm; }}
</style></head>
<body>
  <div class="bg">
    <div class="glow"></div>
    <div class="wm">G</div>
  </div>
  <div class="frame"></div>
  <div class="corner tl">__CORNER__</div>
  <div class="corner tr">__CORNER__</div>
  <div class="corner bl">__CORNER__</div>
  <div class="corner br">__CORNER__</div>

  <div class="wrap">
    <img class="logo" src="data:image/png;base64,__LOGO__" alt="Galtech">

    <div class="seal">__SEAL__</div>

    <div class="kicker">Certificate of Completion</div>
    <h1>Design Tools Training</h1>
    <div class="divider"></div>

    <div class="pre">This certificate is proudly presented to</div>
    <div class="name">__NAME__</div>
    <div class="name-rule"></div>
    <div class="company">__COMPANY__</div>

    <div class="body">
      for successfully completing the <b>Galtech Design Tools: Live Dealer Training</b>, a hands-on
      session covering Galtech&rsquo;s product configuration workflow and design toolset for AV and
      smart-control system integrators.
    </div>

    <div class="meta">
      <span>22 July 2026</span><span class="dot"></span>
      <span>Dubai, United Arab Emirates</span>
    </div>
  </div>

  <div class="foot">
    <div class="sig">
      <div class="mark"></div>
      <div class="sline"></div>
      <div class="sname">Nabil El Rayes</div>
      <div class="slabel">Galtech Trading &middot; Managing Director</div>
    </div>
  </div>
</body></html>"""

SEAL=r"""<svg width="66" height="66" viewBox="0 0 66 66" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#2f6bff"/><stop offset="1" stop-color="#0e1730"/></linearGradient></defs>
  <g fill="none">
    <circle cx="33" cy="33" r="31" stroke="url(#g)" stroke-width="2"/>
    <circle cx="33" cy="33" r="25.5" stroke="#7fb0ff" stroke-width="1" stroke-dasharray="1 3"/>
    <circle cx="33" cy="33" r="18.5" fill="url(#g)"/>
    <path d="M25.5 33.5l5 5 10-11" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
  </g></svg>"""

CORNER=r"""<svg viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg" fill="none"
  stroke="#2f6bff" stroke-width="1.4" stroke-linecap="round">
  <path d="M4 34 V10 a6 6 0 0 1 6-6 H34"/>
  <path d="M4 22 V14 a4 4 0 0 1 4-4 H22" stroke="#0e1730" stroke-width="1"/>
  <circle cx="9" cy="9" r="1.6" fill="#2f6bff" stroke="none"/>
</svg>"""

TEMPLATE=TEMPLATE.replace("{{","{").replace("}}","}")  # written with .format-style braces; we use .replace()

def build(name, company, cid):
    doc=(TEMPLATE
         .replace("__LOGO__",LOGO_B64)
         .replace("__SEAL__",SEAL)
         .replace("__CORNER__",CORNER)
         .replace("__NAME__",html.escape(name))
         .replace("__COMPANY__",html.escape(company) if company else "")
         .replace("__CID__",cid))
    if not company:
        doc=doc.replace('<div class="company"></div>','')
    slug="".join(c if c.isalnum() else "_" for c in name).strip("_")
    hp=os.path.join(OUT,"html",f"{slug}.html")
    open(hp,"w",encoding="utf-8").write(doc)
    pp=os.path.join(OUT,"pdf",f"{slug}.pdf")
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-pdf-header-footer",
        "--no-margins",f"--print-to-pdf={pp}",f"file://{hp}"],
        capture_output=True,timeout=90)
    return hp,pp,slug

# 15 approved guests (guest_id, name, company). company="" -> line omitted.
GUESTS=[
 ("gst-BMNp0ulLgNOOcuz","Sikander Khan","Future Way Technical Services LLC"),
 ("gst-yfgqtkl0oC4PHo7","Ahmed Nabil","Symphony"),
 ("gst-X5Cwlnhre1CktQH","Tarek Choueiry","Housync Technology Services"),
 ("gst-oBd9VjuaocKACrM","Mohamed Riad","Morph Collective"),
 ("gst-dFAcjvwMMKyS78f","Sajo Chacko","Nano Pixel Technologies LLC"),
 ("gst-7DKfbRvGl4ALGAA","Bala","Ultimate Solutions LLC"),
 ("gst-6nU2jvi36p5AlHI","Mani","Ultimate Solutions"),
 ("gst-ybwZ37JGxn5ZZk7","Nidhin Gopi",""),               # company field was a job title -> omit
 ("gst-jnHovoBzSc2SZ5f","Danil","Butler Company"),
 ("gst-CsefchwqhrMPxV1","Zain Ul Abideen","Neom Connections"),
 ("gst-FS9fNhnw152brUh","Marcel Zaatar","Al Rostamani Communications"),
 ("gst-72ZrWrOp73pDf1h","Rajkumar","Triangle Power Solutions Electricals Trading LLC"),
 ("gst-UnApy3oS7C7ArYO","Omar Deen","Smart Astra"),
 ("gst-5QsCrz4Zr6O7Ay8","Dr. Duney D Sam","Euro Systems LLC"),
 ("gst-1kqgyrFQoByxhF9","Akash Kumar","NTI Audio Visual Technologies"),
]
def cid_of(gid):
    return "GDT-26-"+"".join(c for c in gid.replace("gst-","") if c.isalnum())[:6].upper()

def preview(hp, slug):
    png=os.path.join("/tmp",f"cert_{slug}.png")
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--force-device-scale-factor=2",
        "--hide-scrollbars","--window-size=1123,794",
        f"--screenshot={png}",f"file://{hp}"],capture_output=True,timeout=90)
    return png

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "sample"
    if mode=="batch":
        rows=[]
        for gid,name,comp in GUESTS:
            hp,pp,slug=build(name,comp,cid_of(gid))
            rows.append((name,comp,cid_of(gid),os.path.basename(pp)))
            print(f"  {name:22s} {cid_of(gid):14s} -> {os.path.basename(pp)}")
        print(f"generated {len(rows)} certificates")
    else:
        hp,pp,slug=build("Sajo Chacko","Nano Pixel Technologies LLC","GDT-26-DFACJV")
        print("HTML:",hp); print("PDF :",pp)
        print("PNG :",preview(hp,slug))
