#!/usr/bin/env python3
"""Generate StormAudio_Draft_Additions.csv with full Framer-import rows."""
import csv, os, urllib.parse

REPO_BRANCH = "madiers/claude-all/claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/{REPO_BRANCH}"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def raw_url(relpath: str) -> str:
    return f"{RAW}/{urllib.parse.quote(relpath)}"

def files_in(folder: str, exts=(".png", ".jpg", ".jpeg", ".tif", ".mp4")):
    abs_folder = os.path.join(ROOT, folder)
    if not os.path.isdir(abs_folder):
        return []
    out = []
    for name in sorted(os.listdir(abs_folder)):
        if name.startswith("."):
            continue
        full = os.path.join(abs_folder, name)
        if os.path.isdir(full):
            continue
        if name.lower().endswith(exts):
            out.append(f"{folder}/{name}")
    return out

def pick(folder, *needles):
    """Return first file in folder whose name contains all needles (case-insensitive)."""
    for f in files_in(folder):
        base = os.path.basename(f).lower()
        if all(n.lower() in base for n in needles):
            return f
    return None

def gallery(*folders, exclude_tif=True):
    out = []
    for f in folders:
        for p in files_in(f):
            if exclude_tif and p.lower().endswith(".tif"):
                continue
            out.append(p)
    return out

def tech_table(rows):
    body = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)
    return (
        "<figure><table><tbody>"
        "<tr><th>Specification</th><th>Value</th></tr>"
        f"{body}</tbody></table></figure>"
    )

# -------- Product definitions --------
products = []

# 1) ISP Evo
products.append({
    "slug": "isp-evo",
    "draft": "true",
    "title": "ISP Evo",
    "sub": "FULLY DIGITAL IMMERSIVE SOUND PROCESSOR",
    "desc": (
        "<h3>Description</h3>"
        "<p>The ISP Evo is the first purely digital immersive sound processor on the home cinema market. "
        "Built on a fully digital signal path with AES/EBU and AoIP (AES67/Dante) interfaces, it is the only "
        "processor capable of interfacing directly with Digital Cinema Processors playing DCP content and "
        "delivering up to 32 channels in digital format over the network.</p>"
        "<p>Up to 32 channels of decoding and upmixing handle every major immersive format — Dolby Atmos, "
        "DTS:X Pro, Auro-3D, IMAX Enhanced, MPEG-H and Sony 360 Reality Audio — with up to 32 channels of "
        "post-processing. HDMI 2.1 with HDCP 2.3 supports 8K/40 Gbps, HDR10+, Dolby Vision and HLG "
        "pass-through across all seven inputs and two eARC outputs.</p>"
        "<p>Dirac Live Room Correction, Dirac Live Bass Control and Dirac Live Active Room Treatment all "
        "ship as standard, paired with StormAudio's Expert Bass Management for full-range reference "
        "performance in the most demanding installations.</p>"
    ),
    "table": tech_table([
        ("Decoding & Upmixing", "Up to 32 channels"),
        ("Post-Processing", "Up to 32 channels"),
        ("Supported Codecs", "Dolby Atmos, DTS:X Pro, Auro-3D, IMAX Enhanced, MPEG-H, Sony 360RA"),
        ("HDMI Inputs", "7 (HDMI 2.1 / HDCP 2.3 / 40 Gbps)"),
        ("HDMI Outputs", "2 (ARC/eARC matrix)"),
        ("Video Pass-Through", "8K, 4K UHD, HDR10+, Dolby Vision, HLG"),
        ("Room Correction", "Dirac Live + Dirac Live Bass Control + Dirac Live Active Room Treatment"),
        ("Digital Outputs", "Up to 32ch AES/EBU; up to 32ch AoIP (AES67/Dante)"),
        ("Digital Inputs", "Up to 16ch AES/EBU; up to 32ch AoIP"),
        ("Analog Inputs", "4x RCA (7.1 or stereo); 1x XLR stereo"),
        ("S/PDIF Inputs", "3x optical Toslink, 3x coaxial"),
        ("Bass Management", "StormAudio Expert Bass Management"),
        ("Dimensions (with ears)", "420 x 479 x 155 mm (16.53 x 18.86 x 5.91 in)"),
        ("Weight", "8.3 kg (17.6 lbs)"),
    ]),
    "thumb": "StormAudio/ISP-Evo/packshot/ISP_EVO_NoBackground_FRONT (1).png",
    "thumb_alt": "ISP Evo",
    "brand": "stormaudio",
    "cat": "processor",
    "tags": "immersive,processor,dolby-atmos,dts-x,dirac-live,aoip,dante",
    "specsheet": "https://www.stormaudio.com/wp-content/uploads/2024/04/StormAudio-CI-ISP-EVO-Specification-sheet-2025.03.25.pdf",
    "gallery_folders": ["StormAudio/ISP-Evo/packshot", "StormAudio/ISP-Evo/pictures"],
})

# 2) ISR Fusion 20
products.append({
    "slug": "isr-fusion-20",
    "draft": "true",
    "title": "ISR Fusion 20",
    "sub": "20-CHANNEL IMMERSIVE SOUND RECEIVER",
    "desc": (
        "<h3>Description</h3>"
        "<p>The ISR Fusion 20 is the first 20-channel immersive sound receiver on the market, integrating "
        "StormAudio's reference processing platform with 16 channels of the latest ICEpower Edge "
        "amplification developed in Denmark. It pairs the DSP horsepower to decode up to 11.1.8 immersive "
        "layouts with the muscle to drive a full Atmos array out of a single chassis.</p>"
        "<p>Designed for serious home cinemas where space, simplicity and performance must coexist, the "
        "Fusion 20 supports Dolby Atmos, DTS:X Pro, Auro-3D and IMAX Enhanced, with HDMI 2.1a / HDCP 2.3 "
        "inputs handling 8K and 4K120 plus HDR10+, HLG and Dolby Vision.</p>"
        "<p>The most advanced implementation of Dirac Live Active Room Treatment ensures accurate "
        "calibration, while up to 20 PEQs per channel, four-way active crossovers and unlimited subwoofer "
        "support give integrators full control over even the most ambitious systems.</p>"
    ),
    "table": tech_table([
        ("Total Channels", "20 (16 amplified + 4 pre-out)"),
        ("Amplification", "ICEpower Edge Class D"),
        ("Power Output (SE, 8 ohm)", "150 W per channel"),
        ("Power Output (BTL, 8 ohm)", "500 W per channel"),
        ("Channel Modes", "16ch SE, or up to 10ch SE + 3ch BTL"),
        ("Continuous / Peak Power", "2000 W continuous / 2500 W peak"),
        ("Supported Codecs", "Dolby Atmos, DTS:X Pro, Auro-3D, IMAX Enhanced"),
        ("Max Immersive Layout", "11.1.8"),
        ("HDMI", "7 in / 2 out (HDMI 2.1a / HDCP 2.3)"),
        ("Video Pass-Through", "8K, 4K120, HDR10+, HLG, Dolby Vision"),
        ("Room Correction", "Dirac Live + DLBC + DLBM + DLART"),
        ("PEQ", "Up to 20 per channel"),
        ("Crossovers", "Up to four-way active"),
        ("Subwoofer Support", "Unlimited"),
        ("Control", "Web UI, iOS/Android app, IR, home-automation drivers"),
    ]),
    "thumb": "StormAudio/ISR-Fusion/packshot/ISR_FUSION_FRONT_NOBG_SUPERHQ_05_0022.png",
    "thumb_alt": "ISR Fusion 20",
    "brand": "stormaudio",
    "cat": "receiver",
    "tags": "immersive,receiver,dolby-atmos,dts-x,dirac-live,icepower-edge",
    "specsheet": "https://www.stormaudio.com/receiver/isr-fusion-20/",
    "gallery_folders": ["StormAudio/ISR-Fusion/packshot", "StormAudio/ISR-Fusion/pictures"],
})

# 3) ISP Core 16
products.append({
    "slug": "isp-core-16",
    "draft": "true",
    "title": "ISP Core 16",
    "sub": "16-CHANNEL IMMERSIVE SOUND PROCESSOR",
    "desc": (
        "<h3>Description</h3>"
        "<p>The ISP Core 16 is StormAudio's gateway into reference-grade immersive processing — a "
        "French-engineered 16-channel preamp/processor that brings the same Dirac Live calibration toolkit "
        "and bass-management philosophy as the flagship Elite into a more streamlined chassis. It decodes "
        "and upmixes Dolby Atmos, DTS:X Pro, Auro-3D and IMAX Enhanced, with legacy codec support up to "
        "192 kHz.</p>"
        "<p>Seven HDMI inputs and two HDMI outputs with eARC handle 4K UHD with HDR10, Dolby Vision and "
        "HLG (HDMI 2.0b / HDCP 2.2 stock, with an HDMI 2.1 upgrade board available for 8K and 48 Gbps).</p>"
        "<p>Dirac Live, Dirac Live Bass Control and Dirac Live Active Room Treatment ship as standard, "
        "with up to 20 PEQs per channel, four-way active crossovers and unlimited subwoofers — giving "
        "custom installers a complete platform for sophisticated cinema layouts.</p>"
    ),
    "table": tech_table([
        ("Processing Channels", "Up to 18 (16 outputs)"),
        ("Supported Codecs", "Dolby Atmos, DTS:X Pro, Auro-3D, IMAX Enhanced"),
        ("Legacy Codecs", "Up to 192 kHz"),
        ("HDMI Inputs", "7"),
        ("HDMI Outputs", "2 (with eARC)"),
        ("HDMI Version", "2.0b / HDCP 2.2 / 18 Gbps (2.1 upgrade board: 48 Gbps, 8K, VRR, ALLM, QFT, QMS)"),
        ("HDR Support", "HDR10, Dolby Vision, HLG"),
        ("Room Correction", "Dirac Live + DLBC + DLART"),
        ("PEQ", "Up to 20 per channel"),
        ("Active Crossovers", "Up to four-way"),
        ("Subwoofer Support", "Unlimited"),
        ("Analog Outputs", "16ch XLR"),
        ("Analog Inputs", "4x RCA (7.1 or stereo); 1x XLR stereo"),
        ("Digital Inputs", "3x coax S/PDIF, 3x optical Toslink"),
        ("Digital Output", "1x optical Toslink (Zone 2 stereo downmix)"),
        ("Display", "5-inch full-color front panel"),
        ("Control", "Web UI, IR remote, iOS/Android app; Roon Ready"),
        ("Form Factor", "3U"),
        ("Dimensions", "402.2 x 442 x 132.7 mm (ears +4 cm, feet +2 cm)"),
        ("Weight", "9 kg"),
    ]),
    "thumb": "StormAudio/ISP-Core/Pictures/ISP_CORE_FRONT_BG_03.png",
    "thumb_alt": "ISP Core 16",
    "brand": "stormaudio",
    "cat": "processor",
    "tags": "immersive,processor,dolby-atmos,dts-x,dirac-live,roon-ready",
    "specsheet": "https://www.stormaudio.com/wp-content/uploads/2024/04/StormAudio-CI-ISP-CORE-16-Specification-sheet-2025.06.24-1.pdf",
    "gallery_folders": ["StormAudio/ISP-Core/Pictures"],
})

# 4) ISP Elite MK3
products.append({
    "slug": "isp-elite-mk3",
    "draft": "true",
    "title": "ISP Elite MK3",
    "sub": "REFERENCE IMMERSIVE SOUND PROCESSOR",
    "desc": (
        "<h3>Description</h3>"
        "<p>The ISP Elite MK3 is StormAudio's reference immersive sound processor — a modular, "
        "future-proof platform that took 'Best New Home Cinema Sound Processor of 2022' and continues to "
        "set the bar. Engineered around a software-defined hardware strategy, every major subsystem "
        "(HDMI, audio outputs, processing) is upgradeable, so the chassis you install today keeps pace "
        "with format and connectivity changes for years.</p>"
        "<p>Up to 24 channels of decoding and upmixing — and up to 32 channels of post-processing — "
        "handle Dolby Atmos, DTS:X Pro, Auro-3D and IMAX Enhanced. Seven HDMI inputs with HDMI 2.1a / "
        "HDCP 2.3 support 8K at 40 Gbps and full HDR10+, Dolby Vision and HLG pass-through.</p>"
        "<p>The full Dirac Live suite — Live, Bass Control, Bass Management and Active Room Treatment "
        "(DLART) — comes standard, with model variants delivering 16, 24 or 32 analog XLR channels, or "
        "32 digital AES/EBU or AoIP (AES67/Dante) outputs for the most ambitious installations.</p>"
    ),
    "table": tech_table([
        ("Variants", "Elite 16/24/32 Analog MK3; Elite 32 Digital AES MK3; Elite 32 Digital AoIP MK3"),
        ("Decoding & Upmixing", "Up to 24 channels"),
        ("Post-Processing", "Up to 32 channels"),
        ("Supported Codecs", "Dolby Atmos, DTS:X Pro, Auro-3D, IMAX Enhanced Ready, legacy up to 192 kHz"),
        ("HDMI", "7 in / 2 out (ARC/eARC)"),
        ("HDMI Version", "2.1a / HDCP 2.3 (upgradable board)"),
        ("Video Pass-Through", "8K, 4K UHD, HDR10+, Dolby Vision, HLG"),
        ("Room Correction", "Dirac Live + DLBC + DLBM + DLART"),
        ("Analog Outputs", "16ch / 24ch / 32ch XLR (by model)"),
        ("Digital Outputs", "Optional 32ch AES/EBU; 32ch AoIP AES67/Ravenna; Dante compatible"),
        ("Analog Inputs", "4x RCA (7.1 or stereo); 1x XLR stereo"),
        ("Digital Inputs", "3x optical Toslink, 3x coaxial S/PDIF"),
        ("Bass Management", "Standard + Expert modes"),
        ("Multi-Sub / Multi-Way", "Yes"),
        ("Multi-Theater / Multi-Room", "Yes"),
        ("Control", "Web UI, IR remote, iOS/Android apps, control-system drivers"),
        ("Dimensions", "465.8 x 442 x 176 mm (ears +4 cm, feet +2 cm)"),
        ("Weight", "11 kg"),
    ]),
    "thumb": "StormAudio/ISP-Elite-MK3/Packshots/MK3_FRONT_SHADOW.png",
    "thumb_alt": "ISP Elite MK3",
    "brand": "stormaudio",
    "cat": "processor",
    "tags": "immersive,processor,reference,dolby-atmos,dts-x,dirac-live,modular",
    "specsheet": "https://www.stormaudio.com/processors/isp-elite-mk3/",
    "gallery_folders": ["StormAudio/ISP-Elite-MK3/Packshots", "StormAudio/ISP-Elite-MK3/Pictures",
                         "StormAudio/Piled-MK3/Pictures"],
})

# 5) PA 8 Ultra MK3 — uses PA_FRONT / PA8_BACK / PA_SIDE + shared Pictures + Piled
products.append({
    "slug": "pa-8-ultra-mk3",
    "draft": "true",
    "title": "PA 8 Ultra MK3",
    "sub": "8-CHANNEL POWER AMPLIFIER",
    "desc": (
        "<h3>Description</h3>"
        "<p>The PA 8 Ultra MK3 is StormAudio's 8-channel reference amplifier — engineered with Pascal "
        "Audio and built around UMAC Class D modules paired with four individual UREC power supplies "
        "delivering up to 3 kW of total power capacity. It is the heart of an immersive system, pumping "
        "200 W per channel into 8 ohms or 400 W into 4 ohms across all eight channels.</p>"
        "<p>When bigger SPLs or LCR/subwoofer duty calls, four bridged BTL channels deliver up to 800 W "
        "RMS at 8 ohms with 32 dB of gain. THD+N is held below 0.005% at 1 W and signal-to-noise sits at "
        "115 dB, with frequency response extending from 10 Hz to 50 kHz (-3 dB CEM).</p>"
        "<p>Ethernet remote monitoring via StormMonitoring, USB service access and 12 V triggers tie it "
        "cleanly into any StormAudio ISP-based system.</p>"
    ),
    "table": tech_table([
        ("Channels", "8 (SE) or 4 (BTL bridged)"),
        ("Amplifier Class", "UMAC Class D (developed with Pascal Audio)"),
        ("Power Supplies", "4 x UREC, up to 3 kW total"),
        ("Power Output (SE, 8 ohm)", "200 W RMS per channel"),
        ("Power Output (SE, 4 ohm)", "400 W RMS per channel"),
        ("Power Output (BTL, 8 ohm)", "800 W RMS per channel"),
        ("Power Output (BTL, 4 ohm)", "800 W RMS per channel"),
        ("Gain (SE)", "26 dB"),
        ("Gain (BTL)", "32 dB"),
        ("THD+N (1 W)", "&lt; 0.005%"),
        ("THD (20 Hz–20 kHz)", "&lt; 0.03% (1 W to -1 dB max power)"),
        ("Signal-to-Noise Ratio", "115 dB (P-rated)"),
        ("Frequency Response", "10 Hz – 50 kHz (-3 dB CEM)"),
        ("Inputs", "8 x XLR balanced"),
        ("Control", "Ethernet (StormMonitoring), USB service, 12 V trigger in/out"),
        ("Form Factor", "3U rack"),
        ("Dimensions (W x D x H)", "490 x 441 x 130 mm"),
        ("Weight", "21 kg net (46.3 lbs)"),
    ]),
    "thumb": "StormAudio/PA-MK3/Packshots/PA_FRONT.png",
    "thumb_alt": "PA 8 Ultra MK3",
    "brand": "stormaudio",
    "cat": "amplifier",
    "tags": "amplifier,class-d,8-channel,power-amplifier,umac,pascal-audio",
    "specsheet": "https://www.stormaudio.com/wp-content/uploads/2024/04/StormAudio-CI-PA-MK3-Specification-sheet-2023.05.03.pdf",
    "gallery_folders": [],  # populated explicitly below
    "gallery_explicit": [
        "StormAudio/PA-MK3/Packshots/PA_FRONT.png",
        "StormAudio/PA-MK3/Packshots/PA8_BACK.png",
        "StormAudio/PA-MK3/Packshots/PA_SIDE.png",
    ] + [f"StormAudio/PA-MK3/Pictures/PA MK3 ({n}).jpg" for n in range(1, 9)]
      + [f"StormAudio/Piled-MK3/Pictures/MK3 piled ISP and PA ({n}).jpg" for n in range(1, 16)],
})

# 6) PA 16 MK3
products.append({
    "slug": "pa-16-mk3",
    "draft": "true",
    "title": "PA 16 MK3",
    "sub": "16-CHANNEL POWER AMPLIFIER",
    "desc": (
        "<h3>Description</h3>"
        "<p><strong>Real Power for Real Immersive Systems.</strong> The PA 16 MK3 is a 16-channel "
        "high-power Class D amplifier that delivers authority and balance without strain — sixteen "
        "channels of clean output that keep blockbuster action scenes controlled while preserving every "
        "subtle detail in the mix.</p>"
        "<p>Like its 8-channel sibling, it pairs UMAC Class D modules with four UREC power supplies for "
        "up to 3 kW of headroom on tap. Each channel delivers 200 W into 8 ohms or 225 W into 4 ohms "
        "across all sixteen channels driven, with bridged BTL operation pushing up to 800 W per channel "
        "for LCRs or subwoofers.</p>"
        "<p>THD+N stays below 0.005% at 1 W, signal-to-noise hits 115 dB, and the frequency response "
        "runs 10 Hz – 50 kHz. Sixteen balanced XLR inputs, Ethernet for remote monitoring and 12 V "
        "triggers make it a drop-in match for StormAudio's ISP/ISR platforms — all in a standard 19-inch "
        "3U chassis with electronically controlled, near-silent ventilation.</p>"
    ),
    "table": tech_table([
        ("Channels", "16 (SE), or up to 4 BTL + 8 SE"),
        ("Amplifier Class", "UMAC Class D (with Pascal Audio)"),
        ("Power Supplies", "4 x UREC, up to 3 kW total"),
        ("Power Output (SE, 8 ohm)", "200 W per channel, all channels driven (20 Hz–20 kHz, 0.1% THD)"),
        ("Power Output (SE, 4 ohm)", "225 W per channel"),
        ("Power Output (BTL)", "Up to 800 W per channel"),
        ("THD+N", "&lt; 0.005% @ 1 W"),
        ("Signal-to-Noise Ratio", "~115 dB (P-rated)"),
        ("Frequency Response", "10 Hz – 50 kHz (-3 dB CEM)"),
        ("Inputs", "16 x XLR balanced"),
        ("Load Impedance", "4–8 ohm"),
        ("Control / Connectivity", "Ethernet (StormMonitoring), USB service, 12 V trigger in/out"),
        ("Cooling", "Electronic ventilation, thermal sensors, &lt; ~30 dB under load"),
        ("Form Factor", "3U, 19-inch rack"),
        ("Dimensions (W x H x D)", "435 x 150 x 490 mm"),
        ("Weight", "~21 kg"),
    ]),
    "thumb": "StormAudio/PA-MK3/Packshots/PA_FRONT.png",
    "thumb_alt": "PA 16 MK3",
    "brand": "stormaudio",
    "cat": "amplifier",
    "tags": "amplifier,class-d,16-channel,power-amplifier,umac,pascal-audio",
    "specsheet": "https://www.stormaudio.com/wp-content/uploads/2024/04/StormAudio-CI-PA-MK3-Specification-sheet-2023.05.03.pdf",
    "gallery_folders": [],
    "gallery_explicit": [
        "StormAudio/PA-MK3/Packshots/PA_FRONT.png",
        "StormAudio/PA-MK3/Packshots/PA16_BACK.png",
        "StormAudio/PA-MK3/Packshots/PA_SIDE.png",
    ] + [f"StormAudio/PA-MK3/Pictures/PA MK3 ({n}).jpg" for n in range(1, 9)]
      + [f"StormAudio/Piled-MK3/Pictures/MK3 piled ISP and PA ({n}).jpg" for n in range(1, 16)],
})

# 7) Impulsion 8
products.append({
    "slug": "impulsion-8",
    "draft": "true",
    "title": "Impulsion 8",
    "sub": "8-CHANNEL AoIP AMPLIFIER",
    "desc": (
        "<h3>Description</h3>"
        "<p>The Impulsion 8 is StormAudio's intelligent amplifier for the smart-AV era — a compact 2U, "
        "8-channel Class D powerhouse that combines Pascal Audio's UMAC amplification, a UREC 3,600 W "
        "power supply and native AES67/Dante AoIP connectivity in a single chassis. It is engineered to "
        "make speaker management and system integration effortless, with built-in DSP, IP control and "
        "ESS Sabre HyperStream IV DAC technology on the analog inputs.</p>"
        "<p>Each channel delivers 200 W into 8 ohms, with bridged BTL operation pushing up to 800 W "
        "(8 ohm) or 1,200 W peak (4 ohm) per channel — plenty for full-range immersive arrays or "
        "dedicated subwoofer duties.</p>"
        "<p>Plug it into a StormAudio ISP and it self-detects; integrate it into a Dante network and it "
        "slots straight in alongside other AoIP devices. Full DSP (parametric EQs, FIR filters, "
        "limiters, per-channel gain) ships in a 2026 firmware update, with real-time status monitoring "
        "via StormMonitoring for remote diagnostics.</p>"
    ),
    "table": tech_table([
        ("Channels", "8 (SE) or 4 (BTL bridged)"),
        ("Amplifier Class", "UMAC Class D (Pascal Audio)"),
        ("Power Supply", "UREC 3,600 W"),
        ("Power Output (SE, 8 ohm)", "200 W RMS per channel"),
        ("Power Output (SE, 4 ohm)", "400 W RMS per channel"),
        ("Power Output (BTL, 8 ohm)", "Up to 800 W per channel"),
        ("Power Output (BTL, 4 ohm peak)", "Up to 1,200 W per channel"),
        ("Digital Inputs", "AES67 / Dante AoIP (native)"),
        ("Analog Inputs", "ESS Sabre HyperStream IV DAC"),
        ("DSP", "Built-in (parametric EQ, FIR filters, limiters, per-channel gain — full suite via 2026 firmware)"),
        ("Network / Control", "IP control, StormMonitoring, auto-detection with StormAudio ISP/ISR"),
        ("Cooling", "Thermally regulated, near-silent"),
        ("Form Factor", "2U compact rack"),
    ]),
    "thumb": "Impulsion-8/Packshots/Impulsion_front_01_nobg reduced.png",
    "thumb_alt": "Impulsion 8",
    "brand": "stormaudio",
    "cat": "amplifier",
    "tags": "amplifier,class-d,8-channel,aoip,dante,aes67,dsp,impulsion",
    "specsheet": "https://www.stormaudio.com/amplifiers/impulsion-8/",
    "gallery_folders": ["Impulsion-8/Packshots", "Impulsion-8/Pictures", "Impulsion-8/Videos"],
})

# -------- Build galleries (URL-encoded) --------
for p in products:
    if "gallery_explicit" in p and p["gallery_explicit"]:
        urls = [raw_url(f) for f in p["gallery_explicit"]]
    else:
        files = gallery(*p["gallery_folders"])
        urls = [raw_url(f) for f in files]
    p["gallery_urls"] = ", ".join(urls)
    p["thumb_url"] = raw_url(p["thumb"])

# -------- Write CSV --------
OUT = os.path.join(ROOT, "StormAudio_Draft_Additions.csv")
HEADER = ["Slug", ":draft", "Title", "Sub Title", "Product Description",
          "Technical Table", "Thumbnail", "Thumbnail:alt", "Brand",
          "Product Categories", "Product Tags", "Specsheet", "Gallery"]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(HEADER)
    for p in products:
        w.writerow([
            p["slug"], p["draft"], p["title"], p["sub"], p["desc"],
            p["table"], p["thumb_url"], p["thumb_alt"], p["brand"],
            p["cat"], p["tags"], p["specsheet"], p["gallery_urls"],
        ])

print(f"Wrote {OUT} with {len(products)} products")
for p in products:
    n = len(p["gallery_urls"].split(", ")) if p["gallery_urls"] else 0
    print(f"  - {p['slug']:20s}  {n:3d} gallery images")
