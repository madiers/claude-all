#!/usr/bin/env python3
"""Single source of truth for the full LEA Professional amplifier catalogue.

LEA's model number encodes the amp: watts-per-channel = int(num[:-1]) * 10,
channel-count = int(num[-1]).  e.g. 704 = 700 W x 4 ch, 168 = 160 W x 8 ch,
1504 = 1500 W x 4 ch, 34 = 30 W x 4 ch.  Power at 2 ohm is half the rated power.

Series:
  connect  base CONNECT Series (Network; analog + optional networking)
  dante    same chassis with Dante (model ends in D)
  adsp     Advanced-DSP variant (-ADSP)
  g        Government model (-G): all wireless removed, wired LAN only
  cds      Cinema Digital Series (CDS...): cinema/immersive, adds 25 V + AES67

catalog() returns one dict per model with computed channels/watts and the
render token used to fetch its studio image from leaprofessional.com.
"""

def _watts(num):
    return int(num[:-1]) * 10

def _ch(num):
    return int(num[-1])

def _render(num, dante, cinema, half):
    """Which leaprofessional.com render this model uses (the photographed box)."""
    if num == "1504":
        return ("special", ["Assets/lea/_renders/1504-front.png",
                            "Assets/lea/_renders/Front-_-Back_1504D.png"])
    if num == "3004":
        rels = (["CS3004D-Front-and-Back.png", "CS3004D-back.png"] if dante else
                ["CS3004-Front.png", "CS3004-Front-and-Back.png", "CS3004-back-panel.png"])
        return ("special", [f"Assets/lea/_renders/{r}" for r in rels])
    if half:
        return ("special", ["Assets/lea/_renders/Half-Rack-Front.png"])
    return ("token", "CS" + num + ("D" if (dante or cinema) else ""))

def catalog():
    out = []
    def add(slug, label, num, series, dante, gov=False, adsp=False, cinema=False, half=False):
        out.append({
            "slug": slug, "label": label, "num": num,
            "channels": _ch(num), "watts": _watts(num),
            "series": series, "dante": dante, "gov": gov, "adsp": adsp,
            "cinema": cinema, "half": half,
            "render": _render(num, dante, cinema, half),
        })

    # base full-rack CONNECT (Network, non-Dante)
    for n in ["352", "354", "702", "704", "1504"]:
        add(f"cs{n}", f"CS{n}", n, "connect", dante=False)
    # Dante CONNECT (full-rack + high-channel)
    for n in ["352", "354", "702", "704", "1504", "84", "88", "164", "168"]:
        add(f"cs{n}d", f"CS{n}D", n, "connect", dante=True)
    # half-rack CONNECT (Network)
    for n in ["34", "62", "64", "122", "124"]:
        add(f"cs{n}", f"CS{n}", n, "connect", dante=False, half=True)
    # half-rack Dante
    for n in ["34", "62", "64", "122", "124"]:
        add(f"cs{n}d", f"CS{n}D", n, "connect", dante=True, half=True)
    # ADSP (Network + Dante)
    for n in ["352", "354", "702", "704"]:
        add(f"cs{n}-adsp", f"CS{n}-ADSP", n, "adsp", dante=False, adsp=True)
        add(f"cs{n}d-adsp", f"CS{n}D-ADSP", n, "adsp", dante=True, adsp=True)
    # Government models (-G)
    for slug, label, num, dante in [
        ("cs354-g", "CS354-G", "354", False), ("cs354d-g", "CS354D-G", "354", True),
        ("cs702-g", "CS702-G", "702", False), ("cs704-g", "CS704-G", "704", False),
        ("cs704d-g", "CS704D-G", "704", True), ("cs1504-g", "CS1504-G", "1504", False),
        ("cs1504d-g", "CS1504D-G", "1504", True)]:
        add(slug, label, num, "g", dante=dante, gov=True)
    # Cinema Digital Series
    for n in ["352", "354", "702", "704", "1504"]:
        add(f"cds{n}", f"CDS{n}", n, "cds", dante=True, cinema=True)
    # 3004 high-power
    add("cs3004", "CS3004", "3004", "connect", dante=False)
    add("cs3004d", "CS3004D", "3004", "connect", dante=True)
    return out

if __name__ == "__main__":
    c = catalog()
    print(len(c), "models")
    for m in c:
        print(f"  {m['slug']:14} {m['label']:12} {m['channels']}ch {m['watts']}W "
              f"{m['series']:8} render={m['render'][1] if m['render'][0]=='token' else 'special'}")
