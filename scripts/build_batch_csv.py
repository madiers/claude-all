#!/usr/bin/env python3
"""Build a single Framer-import batch CSV for products NOT yet in the Framer CMS.

This file appends to the CMS (Framer doesn't replace on import), so the rule is:
include ONLY products that are missing from the existing brand CSVs / Framer.

Today's batch:
- 7 StormAudio main products (merged from StormAudio_Draft_Additions.csv)
- 2 StormAudio accessories
- 35 Krix new products
= 44 rows total in one file the user can upload once.
"""
import csv, os, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_BRANCH = "madiers/claude-all/claude/blissful-cori-JY3Gi"
RAW = f"https://raw.githubusercontent.com/{REPO_BRANCH}"

def raw_url(relpath: str) -> str:
    return f"{RAW}/{urllib.parse.quote(relpath)}"

def tt(rows):
    body = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)
    return ("<figure><table><tbody>"
            "<tr><th>Specification</th><th>Value</th></tr>"
            f"{body}</tbody></table></figure>")

def desc(*paragraphs, heading="Description"):
    p = "".join(f"<p>{x}</p>" for x in paragraphs)
    return f"<h3>{heading}</h3>{p}"

# ============================================================
# Helper: simple product factory
# ============================================================
def P(slug, title, sub, paragraphs, specs, thumb, gallery,
      brand, tag, specsheet, draft="true", category="audio"):
    return {
        "Slug": slug,
        ":draft": draft,
        "Title": title,
        "Sub Title": sub,
        "Product Description": desc(*paragraphs),
        "Technical Table": tt(specs),
        "Thumbnail": thumb,
        "Thumbnail:alt": title,
        "Brand": brand,
        "Product Categories": category,
        "Product Tags": tag,
        "Specsheet": specsheet,
        "Gallery": ", ".join(gallery),
    }

products = []

# ============================================================
# StormAudio accessories (2)
# ============================================================
products.append(P(
    slug="calibration-kit",
    title="Calibration Kit",
    sub="DIRAC LIVE ROOM-CALIBRATION KIT",
    paragraphs=[
        "StormAudio's Calibration Kit is the full-fat tool every StormAudio integrator brings on site. "
        "Built around a calibrated USB measurement microphone and supplied in a custom flight case, it "
        "contains everything required to run a complete Dirac Live Room Correction, Bass Control, and "
        "Active Room Treatment session on any StormAudio ISP or ISR processor.",
        "The kit ships with a microphone stand and boom, USB and USB-over-CAT5 cabling, and a powered "
        "USB/CAT5 extender so the mic can reach the prime listening position from anywhere in the room. "
        "The flight case has empty space for additional small equipment so installers can carry a single, "
        "organized rig between projects.",
        "Designed to be used with the StormAudio-licensed build of Dirac Live, it produces the "
        "measurement data StormAudio's Pro Remote Assisted Calibration (PRAC) service expects — making "
        "it the only calibration hardware StormAudio formally endorses for field use.",
    ],
    specs=[
        ("Microphone", "Calibrated omnidirectional USB measurement microphone"),
        ("Calibration File", "Individual calibration file supplied"),
        ("Connection", "USB + USB-over-CAT5 extender"),
        ("Stand", "Microphone stand with boom included"),
        ("Cables", "USB cables and USB/CAT5 cable & extender included"),
        ("Carrying", "Custom flight case with space for additional gear"),
        ("Compatible Software", "Dirac Live 2.x (StormAudio licensed build)"),
        ("Supports", "Dirac Live, Multi-Subwoofer Bass Control, Active Room Treatment (ART)"),
        ("Compatible Processors", "ISP Elite MK3, ISP Core 16, ISP Evo, ISR Fusion 20 (and legacy ISPs)"),
        ("Max Channels", "Up to 32 channels of calibration"),
        ("Net Weight", "9 kg (19.8 lb)"),
        ("Gross Weight", "12 kg (22 lb)"),
        ("Box Dimensions", "61 x 50 x 25 cm (24 x 19.7 x 9.8 in)"),
    ],
    thumb="",
    gallery=[],
    brand="stormaudio", tag="accessory",
    specsheet="https://nintronics.co.uk/products/storm-audio-calibration-kit",
))

products.append(P(
    slug="microphone-mini-kit",
    title="Microphone Mini-Kit",
    sub="COMPACT CALIBRATION & MONITORING MIC KIT",
    paragraphs=[
        "The Microphone Mini-Kit is StormAudio's permanent in-room microphone solution, supplied with "
        "every new StormAudio processor and available as a spare or replacement SKU. It pairs a "
        "calibrated USB measurement microphone with a discreet pod and a USB-over-CAT5 extender, so the "
        "mic can live permanently at the prime listening position and feed back into the processor "
        "whenever calibration or RTA is needed.",
        "Beyond Dirac Live calibration, the Mini-Kit unlocks StormAudio's remote monitoring and "
        "Real-Time Analysis features, letting the integrator audit speaker behaviour and re-run "
        "calibration from anywhere without ever bringing a flight case back on site. It is the "
        "recommended companion to every ISP Elite MK3, ISP Core 16, ISP Evo, and ISR Fusion 20 install.",
    ],
    specs=[
        ("Microphone", "Calibrated USB measurement microphone"),
        ("Calibration File", "Individual calibration file supplied"),
        ("Mounting", "Microphone pod (permanent in-room placement)"),
        ("Connection", "USB + USB-over-CAT5 cable and extender"),
        ("Compatible Software", "Dirac Live 2.x (StormAudio licensed build)"),
        ("Supports", "Dirac Live, Bass Control, Active Room Treatment, Remote Monitoring, RTA"),
        ("Compatible Processors", "ISP Elite MK3, ISP Core 16, ISP Evo, ISR Fusion 20"),
        ("Max Channels", "Up to 32 channels of calibration"),
        ("Net Weight", "0.5 kg (1.1 lb)"),
        ("Box Dimensions", "35 x 28 x 8 cm (13.8 x 11 x 3.1 in)"),
    ],
    thumb="",
    gallery=[],
    brand="stormaudio", tag="accessory",
    specsheet="https://nintronics.co.uk/products/storm-audio-microphone-mini-kit",
))

# ============================================================
# Krix new products (35) — image URLs from Krix's own CDN
# ============================================================

# 1. Acoustix Evara
products.append(P(
    slug="acoustix-evara", title="Acoustix Evara", sub="BOOKSHELF SPEAKER",
    paragraphs=[
        "The Acoustix Evara delivers rich, detailed performance that exceeds expectations for its size, "
        "enabling music and movies to thrive in compact spaces.",
        "Its dual front-vent design allows versatile placement on stands, within shelving, or in custom "
        "joinery. Ideal for stereo systems, gaming setups, or as surround speakers in home cinema "
        "configurations.",
        "Available in five Evara finishes: Studio White, Black, Charcoal, Navy, and Green.",
    ],
    specs=[
        ("Frequency Range", "45 Hz – 40 kHz in-room response"),
        ("Power Handling", "20–160 W RMS"),
        ("Sensitivity", "89 dB (2.83 V / 1 m)"),
        ("Impedance", "6 Ω nominal (4.3 Ω min)"),
        ("Configuration", "D'Appolito, 2-way"),
        ("Enclosure", "Bass reflex, front vented"),
        ("LF Drivers", "2 x 130 mm fibre-reinforced polymer, 25 mm voice coil"),
        ("HF Driver", "26 mm dual concentric, neodymium magnet"),
        ("Input Terminals", "Gold-plated binding posts"),
        ("Dimensions (H x W x D)", "450 x 180 x 300 mm"),
        ("Weight", "10 kg each"),
        ("Finishes", "Studio White, Black, Charcoal, Navy, Green"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72fb6dcd1a1de7206a4e3_Acoustix_Evara_product_NoGrille_StudioWhite.png",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72fb6dcd1a1de7206a4e3_Acoustix_Evara_product_NoGrille_StudioWhite.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72f9aaa7c177793bfbac0_Acoustix_Evara_product_NoGrille_StudioBlack.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72fca69d690dfc950f36e_Acoustix_Evara_product_NoGrille_StudioGreen.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72fcfa48887f450771b81_Acoustix_Evara_product_NoGrille_StudioNavy.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72fd548cdd7d0213933a8_Acoustix_Evara_product_NoGrille_StudioCharcoal.png",
    ],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69e06eb637a92f7d1d43c96d_Acoustix%20Evara%20Specifications%20Sheet_001.pdf",
))

# 2. Cyclonix 12 Active Compact
products.append(P(
    slug="cyclonix-12ac", title="Cyclonix 12 Active Compact", sub="ACTIVE SUBWOOFER",
    paragraphs=[
        "A high-performance active subwoofer designed for home cinema environments where impact must be "
        "matched by flexibility. Suitable for both behind-screen and in-room installations, adapting to "
        "open-plan living areas and dedicated cinema spaces.",
        "Incorporates a 305 mm long-throw woofer and Class D amplifier with dual down-firing ports.",
    ],
    specs=[
        ("Frequency Range", "15 Hz – 200 Hz in-room response"),
        ("Amplifier Power", "400 W RMS"),
        ("Maximum Output", "125 dB SPL in-room"),
        ("Input Connections", "High-current spring terminals (10 AWG)"),
        ("USB-C", "5 V / 1 A (optional wireless receiver)"),
        ("Enclosure", "Bass reflex, dual down-firing vents"),
        ("Power Management", "Signal sensing, 15-min standby"),
        ("Driver", '305 mm (12") paper cone, 50 mm long-throw voice coil'),
        ("Phase Select", "50 Hz – 200 Hz or bypass"),
        ("Distortion", "&lt; 0.1% @ 400 W RMS"),
        ("Dimensions (H x W x D)", "630 x 500 x 295 mm (317 mm with grille)"),
        ("Weight", "26 kg"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69ead3b135286ecf84d6b57d_12AC_Preorder_NoGrille.png",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69ead3a96eb562a1928da7e7_12AC_Preorder_Grille.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69ead3b135286ecf84d6b57d_12AC_Preorder_NoGrille.png",
    ],
    brand="krix", tag="subwoofer",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69fbfb5300907bb11dfeccf5_Cyclonic%2012%20Active%20Compact%20Specifications%20Sheet%20001.pdf",
))

# 3. Cyclonix 15
products.append(P(
    slug="cyclonix-15", title="Cyclonix 15", sub="PASSIVE SUBWOOFER",
    paragraphs=[
        "A low-profile passive subwoofer that delivers high-output low-frequency performance for "
        "dedicated home cinema installations. Can function as a supporting unit for an MX-20 system or "
        "operate independently in a Series SX configuration.",
        "Its shallow depth enables discreet placement against walls. Features a large 380 mm driver with "
        "100 mm edge-wound copper voice coil for maximum output in high-drive applications.",
    ],
    specs=[
        ("Frequency Range", "25 Hz – 200 Hz in-room response"),
        ("Amplifier Power", "200–1400 W RMS recommended"),
        ("High Pass Filter", "25 Hz, 24 dB/oct Butterworth"),
        ("Limiter", "1000 W (8 Ω)"),
        ("Input Type", "High-current spring terminals (10 AWG)"),
        ("Enclosure", "Bass reflex, front vented"),
        ("Impedance", "8 Ω"),
        ("Driver", '380 mm (15") paper cone'),
        ("Voice Coil", '100 mm (4") edge-wound copper'),
        ("Sensitivity", "96 dB SPL (2.83 V / 1 m)"),
        ("Dimensions (H x W x D)", "1015 x 550 x 270 mm (290 mm with grille)"),
        ("Weight", "38 kg each"),
        ("Finish", "Cinema Black"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a61866b6354a347144c337_Cyclonix15_CinemaBlack_NoGrille.jpg",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a61866b6354a347144c337_Cyclonix15_CinemaBlack_NoGrille.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a618690a0445c0a81efea1_Cyclonix15_CinemaBlack_Grille.jpg",
    ],
    brand="krix", tag="subwoofer",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a618d40a0445c0a81f6829_Cyclonix%2015%20Specifications%20Sheet%20002.pdf",
))

# 4. Flix
products.append(P(
    slug="flix", title="Flix", sub="FREESTANDING CINEMA SPEAKER",
    paragraphs=[
        "Serious main front speakers for a serious dedicated home cinema. Delivers exceptionally high "
        "acoustic power across a wide frequency range with minimal harmonic distortion.",
        "Dual 380 mm drivers with 75 mm voice coils provide increased linear excursion, while a "
        "patented 90° x 40° short-throw horn optimizes sound dispersion to the listening position. "
        "Mounting brackets allow vertical and horizontal tilt.",
    ],
    specs=[
        ("Frequency Range", "38 Hz – 16 kHz in-room response"),
        ("Power Handling", "1000 W RMS max recommended"),
        ("Sensitivity", "101 dB (2.83 V / 1 m)"),
        ("Impedance", "4 Ω nominal"),
        ("Configuration", "2-way"),
        ("Crossover", "1400 Hz passive"),
        ("Enclosure", "Bass reflex, front vented"),
        ("LF Drivers", 'Dual 380 mm (15") high-stiffness paper cone'),
        ("LF Voice Coil", '75 mm (3") on apical former'),
        ("HF Driver", "90° x 40° short-throw horn"),
        ("Compression Throat", '25 mm (1")'),
        ("HF Voice Coil", '44 mm (1¾") edge-wound aluminium'),
        ("Input Terminals", "Krix proprietary binding posts (8 mm hole)"),
        ("Dimensions (H x W x D)", "1470 x 660 x 460 mm"),
        ("Weight", "57 kg each"),
        ("Finish", "Cinema Black"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a622870a0445c0a82aa677_Flix_CinemaBlack_Angle.jpg",
    gallery=["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a622870a0445c0a82aa677_Flix_CinemaBlack_Angle.jpg"],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a622dd24111bab229583a6_Flix%20Rev1.0%20Specification%20Sheet%20001.pdf",
))

# 5. Graphix Evara
products.append(P(
    slug="graphix-evara", title="Graphix Evara", sub="CENTRE CHANNEL SPEAKER",
    paragraphs=[
        "Centre channel that prioritizes vocal clarity and dialogue reproduction, positioning voices "
        "prominently within the soundstage.",
        "Compact dimensions and dual front-firing vents allow installation flexibility whether "
        "displayed openly or concealed in cabinetry. Available in all five Evara finishes.",
    ],
    specs=[
        ("Frequency Range", "45 Hz – 40 kHz in-room response"),
        ("Power Handling", "20–160 W RMS"),
        ("Sensitivity", "89 dB (2.83 V / 1 m)"),
        ("Impedance", "6 Ω nominal (4.3 Ω min)"),
        ("Configuration", "D'Appolito, 2-way"),
        ("Enclosure", "Bass reflex, front vented"),
        ("LF Drivers", '2 x 130 mm (5") doped paper cones, 25 mm voice coils'),
        ("HF Driver", '26 mm (1") dual concentric diaphragm, neodymium magnet'),
        ("Input Terminals", "Gold-plated binding posts"),
        ("Dimensions (H x W x D)", "180 x 450 x 300 mm"),
        ("Weight", "10 kg each"),
        ("Finishes", "Studio White, Black, Charcoal, Navy, Green"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69eea3b8d0ac624c9d19d6be_Graphix_Evara_NoGrille_Product_StudioWhite.png",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69eea3b17fa3608702019cdb_Graphix_Evara_NoGrille_Product_StudioBlack.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69eea3badadbd942be91bf82_Graphix_Evara_NoGrille_Product_StudioCharcoal.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69eea3b94c8bd774305fe7c2_Graphix_Evara_NoGrille_Product_StudioGreen.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69eea3b9916800bc2c321f00_Graphix_Evara_NoGrille_Product_StudioNavy.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69eea3b8d0ac624c9d19d6be_Graphix_Evara_NoGrille_Product_StudioWhite.png",
    ],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d73442d92505bbfe25cef6_Graphix%20Evara%20Specifications%20Sheet_001.pdf",
))

# 6. Harmonix Mk2
products.append(P(
    slug="harmonix-mk2", title="Harmonix Mk2", sub="3-WAY FLOORSTANDING SPEAKER",
    paragraphs=[
        "Delivers a truly natural, all-encompassing sound through its 3-way configuration: two 165 mm "
        "bass drivers for deep, tight bass, a dedicated 130 mm midrange, and a 25 mm tweeter extending "
        "to 40 kHz.",
        "Front-facing ports enable placement near walls without compromise. Timbre-matched across the "
        "Krix lineup for surround integration.",
    ],
    specs=[
        ("Frequency Range", "35 Hz – 40 kHz in-room response"),
        ("Power Handling", "50–250 W RMS"),
        ("Sensitivity", "90 dB (2.83 V / 1 m)"),
        ("Impedance", "6 Ω nominal (3.1 Ω min)"),
        ("Configuration", "3-way"),
        ("Enclosure", "Dual chambers — sealed midrange, bass reflex main"),
        ("Bass Drivers", "2 x 165 mm polypropylene, 33 mm voice coil"),
        ("Midrange", "130 mm coated paper, 26 mm voice coil"),
        ("Tweeter", "25 mm dual concentric diaphragm"),
        ("Terminals", "Dual gold-plated bi-wire binding posts"),
        ("Dimensions (H x W x D)", "1040 x 220 x 350 mm"),
        ("Weight", "28 kg each"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/649b938ff5ffed205fc77c1e_Harmonix_BlackWoodgrain.jpg",
    gallery=["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/649b938ff5ffed205fc77c1e_Harmonix_BlackWoodgrain.jpg"],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4c7e354c793677dbffff4_Harmonix%20Mk2%20Specifications%20Sheet-003.pdf",
))

# 7. IC-10 (Holographix current slug)
products.append(P(
    slug="ic-10", title="IC-10 (Holographix)", sub="IN-CEILING SPEAKER",
    paragraphs=[
        "Downlight-sized in-ceiling speakers that hide in the ceiling to distribute music seamlessly "
        "and invisibly. Water-resistant, semi-enclosed construction protects against dust and ceiling "
        "debris and makes them suitable for bathrooms.",
        "Multiple pairs can be wired together for even sound across large areas. Paintable to match "
        "decor with a simple twist-and-lock mounting system.",
    ],
    specs=[
        ("Frequency Range", "90 Hz – 20 kHz in-room"),
        ("Power Handling", "10–80 W RMS"),
        ("Sensitivity", "87 dB (2.83 V / 1 m)"),
        ("Impedance", "8 Ω nominal (7.5 Ω min)"),
        ("Configuration", "Full range"),
        ("Enclosure", "Acoustically treated infinite baffle"),
        ("Driver", "75 mm polypropylene cone, 20 mm voice coil"),
        ("Input", "Spring terminals"),
        ("Cut-out Diameter", "82–88 mm"),
        ("Dimensions", "95 mm diameter x 108 mm mounting depth"),
        ("Weight", "0.5 kg each"),
        ("Finish", "Paintable white"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4e70468551aa9ff6e28af_Holographix_WhiteGrille.jpg",
    gallery=["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4e70468551aa9ff6e28af_Holographix_WhiteGrille.jpg"],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4e8136ba779243fb06e6e_Holographix%20Specifications%20sheet-002.pdf",
))

# 8. IC-35S (Hemispherix SPS current slug)
products.append(P(
    slug="ic-35s", title="IC-35S (Hemispherix SPS)", sub="SINGLE-POINT STEREO IN-CEILING SPEAKER",
    paragraphs=[
        "Single-point stereo speaker for spaces where only one in-ceiling speaker is desired. Accepts "
        "both left and right audio channels — ideal for hallways, bathrooms, eaves, and tight spaces.",
        "125 mm mid-bass driver with polypropylene cone and dual 20 mm ring radiator tweeters mounted "
        "at opposing 20° angles. Rust-resistant stainless steel grille suitable for interior or "
        "alfresco installation.",
    ],
    specs=[
        ("Frequency Range", "70 Hz – 40 kHz in-room"),
        ("Power Handling", "5–50 W RMS"),
        ("Sensitivity", "85 dB (2.83 V / 1 m)"),
        ("Impedance", "2 x 8 Ω nominal (6.3 Ω min)"),
        ("Configuration", "Dual 2-way"),
        ("Enclosure", "Semi-open back"),
        ("LF Driver", '1 x 125 mm (5") polypropylene cone, 35 mm dual voice coil'),
        ("HF Drivers", '2 x 20 mm (¾") ring radiator'),
        ("Input Terminals", "4 x push-type connectors"),
        ("Cut-out Diameter", "207 mm"),
        ("Dimensions", "254 mm diameter x 90 mm mounting depth"),
        ("Weight", "2 kg each"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4f7406ba779243fbf8e21_HemispherixSPS_WhiteGrille_Angle.jpg".replace("64a4f7406ba779243fbf8e21","64a4f73a6ba779243fbf8e21"),
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4f732e7da97f717eba16b_HemispherixSPS_NoGrille_Angle.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4f73a6ba779243fbf8e21_HemispherixSPS_WhiteGrille_Angle.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4f73ed9f21f12fbc45508_HemispherixSPS_NoGrille.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4f7405fab23fac7a487e2_HemispherixSPS_Side.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4f7433744c6efbbf2cae7_HemispherixSPS_Back.jpg",
    ],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/684f74f60f6e64c09dc0e080_IC-35S%20Specifications%20Sheet.pdf",
))

# 9. LX-7
products.append(P(
    slug="lx-7", title="LX-7", sub="LINEAR LCR SOUNDBAR",
    paragraphs=[
        "Custom-built Australian passive LCR soundbar designed for screen sizes of 75 inches and "
        "larger. Three separate channels (L, C, R) pair with surround speakers and an AVR/processor to "
        "deliver immersive cinema audio without virtual processing.",
        "Sleek design minimizes space above or below displays. Includes an adjustable tilting bracket "
        "supporting up to 15° angles. Integrates three 90 x 90 Krix waveguides for enhanced "
        "dispersion. Tonally matched across all Krix surround and overhead offerings.",
    ],
    specs=[
        ("Frequency Range", "60 Hz – 20 kHz in-room"),
        ("Power Handling", "50–250 W RMS"),
        ("Sensitivity", "92 dB (2.83 V / 1 m)"),
        ("Impedance", "8 Ω"),
        ("Configuration", "2-way per channel (LCR)"),
        ("Enclosure", "Bass reflex, front vented, 12 mm braced MDF"),
        ("LF Driver", "165 mm paper cone, 50 mm voice coil"),
        ("HF Driver", "26 mm doped fabric dome with waveguide"),
        ("Crossover", "1.9 kHz"),
        ("Input Terminals", "High-current, accepts 10 AWG cable"),
        ("Mounting", "Adjustable tilt bracket (up to 15°) included"),
        ("Designed For", '75"+ displays'),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/653884beecc6d48bfb7acd5b_LX-7Without%20Grille.jpg",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/653884beecc6d48bfb7acd5b_LX-7Without%20Grille.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/653884c30785ff4bb34b0033_LX-7WithGrille.jpg",
    ],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65388588e1c2a86a53df32ac_LX-7%20Spec%20sheet%201.pdf",
))

# 10. MX-30
products.append(P(
    slug="mx-30", title="MX-30", sub="MODULAR HOME CINEMA SPEAKER SYSTEM",
    paragraphs=[
        "Designed for larger dedicated home cinemas with an acoustically transparent screen, the MX-30 "
        "delivers movie soundtracks with definition and accuracy. Incorporates commercial cinema "
        "components engineered for 5–14 m rooms.",
        "Five modular units maintain consistent height and shallow depth for installation into a single "
        "cavity. Acoustic absorbent front baffles minimize screen and room reflections.",
    ],
    specs=[
        ("LCR Frequency Range", "38 Hz – 16 kHz in-room"),
        ("LCR Power Handling", "100–700 W RMS"),
        ("LCR Sensitivity", "98 dB (2.83 V / 1 m)"),
        ("LCR Impedance", "8 Ω"),
        ("LCR LF Driver", '380 mm (15") high-stiffness paper cone'),
        ("LCR HF Driver", "90°x40° short-throw horn, 25 mm throat, 35 mm compression driver"),
        ("LCR Dimensions (H x W x D)", "1220 x 450 x 335 mm"),
        ("LCR Weight", "48 kg each"),
        ("SUB Frequency Range", "25 Hz – 200 Hz in-room"),
        ("SUB Power Handling", "200–1400 W RMS"),
        ("SUB Sensitivity", "100 dB (2.83 V / 1 m)"),
        ("SUB Driver", '455 mm (18") paper cone, 100 mm voice coil'),
        ("SUB Dimensions (H x W x D)", "1220 x 750 x 335 mm"),
        ("SUB Weight", "65 kg each"),
        ("Recommended Room Depth", "5–14 m"),
        ("Min Screen (16:9)", '135"'),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a61cf0c48a84d80bad783d_MX30_CinemaBlack_Angle.jpg",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a61ceeb9aca5c9b0be6029_MX30_CinemaBlack_Front.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a61cf0c48a84d80bad783d_MX30_CinemaBlack_Angle.jpg",
    ],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/660f7e2a2b757b243fb349f2_MX30%20Specifications%20Sheet_005.pdf",
))

# 11. MX-40
products.append(P(
    slug="mx-40", title="MX-40", sub="FLAGSHIP MODULAR HOME CINEMA SYSTEM",
    paragraphs=[
        "Flagship of the Series MX range. A three-way design with a dedicated high-frequency "
        "compression driver and a newly engineered 152 mm midrange, both integrated into a dual-horn "
        "system refined over three years.",
        "Bass drivers use high-stiffness paper cones with 75 mm voice coils. Two subwoofers each "
        "contain 455 mm drivers with 100 mm voice coils and dual spider assemblies. First Series MX "
        "system offering bi-amplification with two pairs of binding posts per LCR module.",
    ],
    specs=[
        ("LCR Frequency Range", "38 Hz – 16 kHz in-room"),
        ("LCR Power Handling LF / HF", "100–700 W / 100–400 W RMS"),
        ("LCR Sensitivity LF / HF", "98 dB / 101 dB (2.83 V / 1 m)"),
        ("LCR Impedance", "8 Ω (both)"),
        ("LCR Configuration", "3-way bi-amp"),
        ("LCR Crossover", "400 Hz (active required)"),
        ("LCR LF Driver", '380 mm (15") high-stiffness paper cone, 75 mm VC'),
        ("LCR MF Driver", '152 mm (6") on dual horn, 38 mm VC'),
        ("LCR HF Driver", "Dual horn, 25 mm throat, 35 mm compression driver, titanium diaphragm"),
        ("LCR Dimensions (H x W x D)", "1220 x 550 x 335 mm"),
        ("LCR Weight", "65 kg each"),
        ("SUB Frequency", "25 Hz – 200 Hz"),
        ("SUB Power", "200–1400 W RMS"),
        ("SUB Sensitivity", "100 dB / 8 Ω"),
        ("SUB Driver", '455 mm (18") paper cone, 100 mm VC, dual spider'),
        ("SUB Dimensions (H x W x D)", "1220 x 750 x 335 mm"),
        ("SUB Weight", "65 kg each"),
        ("Recommended Room Depth", "5–14 m"),
        ("Min Screen (16:9)", '145"'),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65a60ae35d8db6610fb0c095_MX40_CinemaBlack_Front.jpg",
    gallery=["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65a60ae35d8db6610fb0c095_MX40_CinemaBlack_Front.jpg"],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/660f7e11e4033fcd3279c6a2_MX40%20Specifications%20Sheet_006.pdf",
))

# 12. Phoenix Evara
products.append(P(
    slug="phoenix-evara", title="Phoenix Evara", sub="FLOORSTANDING SPEAKER",
    paragraphs=[
        "Slim, stylish floorstanding speaker for contemporary living spaces. Delivers powerful, "
        "dynamic sound for both music and movies, from everyday listening to immersive home cinema.",
        "Refined, space-conscious form factor complements modern interiors while maintaining "
        "performance in compact footprints.",
    ],
    specs=[
        ("Frequency Range", "35 Hz – 40 kHz in-room"),
        ("Power Handling", "50–200 W RMS"),
        ("Sensitivity", "91 dB (2.83 V / 1 m)"),
        ("Impedance", "6 Ω nominal (3.5 Ω min)"),
        ("Configuration", "D'Appolito, 2-way"),
        ("Enclosure", "Bass reflex, rear vented with X bracing"),
        ("LF Drivers", "Dual 165 mm laminated polypropylene cones"),
        ("Voice Coil", "33 mm on aluminum former"),
        ("HF Driver", "26 mm dual concentric diaphragm"),
        ("Input Terminals", "Dual gold-plated bi-wire binding posts"),
        ("Dimensions (H x W x D)", "950 x 195 x 295 mm"),
        ("Weight", "18 kg each"),
        ("Finishes", "Studio White, Black, Charcoal, Navy, Green"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69fd68b7604992735e211c22_Phoenix%20Evara_product_%20No_grille_StudioWhite.png",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69fd68ae2716fe8617161746_Phoenix%20Evara_product_%20No_grille_StudioBlack.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69fd68b8b2f751bf8d05c82e_Phoenix%20Evara_product_%20No_grille_StudioGreen.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69fd68b8dd75b887b11224f3_Phoenix%20Evara_product_%20No_grille_StudioNavy.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69fd68b7604992735e211c22_Phoenix%20Evara_product_%20No_grille_StudioWhite.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69fd68b729cf808c6877a8a8_Phoenix%20Evara_product_%20No_grille_StudioCharcoal.png",
    ],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72a421e9d564367a62c37_Phoneix%20Evara%20Specifications%20Sheet_001.pdf",
))

# 13. Phoenix Mk2
products.append(P(
    slug="phoenix-mk2", title="Phoenix Mk2", sub="D'APPOLITO FLOORSTANDING SPEAKER",
    paragraphs=[
        "Ideal home entertainment speaker for multi-channel or stereo listening. Compact (95 cm tall, "
        "under 20 cm wide) yet delivers strong performance through dual 165 mm drivers paired with a "
        "26 mm ring radiator tweeter.",
        "Award-winning model combining stylish aesthetics with powerful sound. Available in multiple "
        "wood and finish options.",
    ],
    specs=[
        ("Frequency Range", "35 Hz – 40 kHz in-room"),
        ("Power Handling", "50–200 W RMS"),
        ("Sensitivity", "91 dB (2.83 V / 1 m)"),
        ("Impedance", "6 Ω nominal (3.5 Ω min)"),
        ("Configuration", "D'Appolito, 2-way"),
        ("Enclosure", "Bass reflex, rear vented with X bracing"),
        ("LF Drivers", "Dual 165 mm laminated polypropylene cone"),
        ("Voice Coil", "33 mm on aluminium former"),
        ("HF Driver", "26 mm dual concentric diaphragm with waveguide"),
        ("Input Terminals", "Dual gold-plated bi-wire binding posts"),
        ("Dimensions (H x W x D)", "950 x 195 x 295 mm"),
        ("Weight", "18 kg each"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/649b920d7baf9ff35d363141_Phoenix_Blackwood.jpg",
    gallery=["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/649b920d7baf9ff35d363141_Phoenix_Blackwood.jpg"],
    brand="krix", tag="speaker",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a49c386254432bea52f769_Phoenix%20Mk2%20Specifications%20Sheet-003.pdf",
))

# 14. Seismix 3D Mk3 (current)
products.append(P(
    slug="seismix-3d", title="Seismix 3D Mk3", sub="ACTIVE DOWN-FIRING SUBWOOFER",
    paragraphs=[
        "Combines a 275 mm long-throw woofer with a high-efficiency Class D amplifier to deliver "
        "controlled, deep bass for music and movies.",
        "Down-firing design enables flexible placement near walls, corners, or within cabinetry, "
        "making it ideal for living spaces and media rooms.",
    ],
    specs=[
        ("Frequency Range", "22 Hz – 200 Hz in-room"),
        ("Amplifier Power", "350 W RMS / 700 W max instantaneous"),
        ("Maximum SPL", "122 dB in-room"),
        ("Inputs", "Stereo line RCA, wireless receiver"),
        ("USB-C", "5 V / 1 A (wireless receiver)"),
        ("Enclosure", "Down-firing"),
        ("Driver", "275 mm doped paper cone, 50 mm voice coil"),
        ("Power Mode", "Signal sensing, 15-min standby"),
        ("Phase Control", "0°–180° continuously variable"),
        ("Low Pass Filter", "50 Hz – 200 Hz or bypass"),
        ("Dimensions (H x W x D)", "450 x 360 x 410 mm"),
        ("Weight", "18 kg"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/660cd7c99c6f4f418d5208b4_Seismix3-DF_Front.jpg",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/660cd7c99c6f4f418d5208b4_Seismix3-DF_Front.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/660cd7cf12a89f13018486f3_Seismix3-DF_Angle.jpg",
    ],
    brand="krix", tag="subwoofer",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69e1be82ef49a149ee44e199_Seismix%203D%20Mk3%20Specifications%20Sheet%20001.pdf",
))

# 15. Seismix 3D Evara
products.append(P(
    slug="seismix-3d-evara", title="Seismix 3D Evara", sub="ACTIVE DOWN-FIRING SUBWOOFER",
    paragraphs=[
        "Bring low-frequency effects to life with this tight yet powerful down-firing subwoofer. "
        "Incorporates a custom 275 mm long-throw bass driver engineered for high-output reinforcement "
        "and a built-in Class D amplifier.",
        "Feel the rumble of bass with supreme clarity without sacrificing musicality.",
    ],
    specs=[
        ("Frequency Range", "22 Hz – 200 Hz in-room"),
        ("Amplifier Power", "350 W RMS / 700 W max instantaneous"),
        ("Maximum Output", "122 dB SPL in-room"),
        ("Inputs", "Stereo RCA line level, wireless audio receiver"),
        ("Enclosure", "Down-firing"),
        ("Driver", "275 mm doped paper cone, 50 mm voice coil on Kapton former"),
        ("Phase Select", "0°–180° continuously variable"),
        ("Low Pass Filter", "50 Hz – 200 Hz or bypass"),
        ("Dimensions (H x W x D)", "450 x 360 x 410 mm"),
        ("Weight", "18 kg"),
        ("Finishes", "Studio White, Black, Charcoal, Navy, Green"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d7339cb73d342036418557_Seismix%203D%20Evara_Product_StudioWhite.png",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d733a998187465229d19cd_Seismix%203D%20Evara_Product_StudioNavy.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d73397fc58814c27095e3a_Seismix%203D%20Evara_Product_StudioBlack.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d7339cb73d342036418557_Seismix%203D%20Evara_Product_StudioWhite.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d733a21d7f54431893f10e_Seismix%203D%20Evara_Product_StudioCharcoal.png",
    ],
    brand="krix", tag="subwoofer",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69d72c3d8f22a42b07dc197f_Seismix%203D%20Evara%20Specifications%20Sheet_001.pdf",
))

# 16. Seismix 5
products.append(P(
    slug="seismix-5", title="Seismix 5", sub="ACTIVE SUBWOOFER",
    paragraphs=[
        "Engineered to deliver uncompromising low-frequency performance for serious home cinema "
        "systems. Features a robust 305 mm long-throw woofer paired with a Class D amplifier, "
        "producing commanding bass with exceptional control.",
        "Transforms movies and music into immersive cinematic experiences with added realism, "
        "intensity, and emotion.",
    ],
    specs=[
        ("Frequency Range", "15 Hz – 200 Hz in-room"),
        ("Amplifier Power", "450 W RMS"),
        ("Maximum Output", "125 dB SPL in-room"),
        ("Inputs", "Stereo line-level RCA, balanced XLR"),
        ("USB-C", "5 V / 1 A (optional wireless receiver)"),
        ("Enclosure", "Bass reflex, front vented"),
        ("Driver", "305 mm paper cone, 50 mm voice coil"),
        ("Power Control", "Signal sensing with 15-min standby"),
        ("Phase Select", "0°–180° continuously variable"),
        ("Low Pass Filter", "50 Hz – 200 Hz or bypass"),
        ("Dimensions (H x W x D)", "506 x 400 x 470 mm"),
        ("Weight", "23 kg"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69ea9f2212342c2083cf56ed_Seismix5_Preorder_NoGrille.png",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69ea9f2212342c2083cf56ed_Seismix5_Preorder_NoGrille.png",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69ea9f3ae9a654e10f8118f9_Seismix5_Preorder_Grille.png",
    ],
    brand="krix", tag="subwoofer",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69e9db78512c3e6952fb5ca3_Seismix%205%20Specifications%20Sheet%20001.pdf",
))

# 17. Seismix 1 Mk7
products.append(P(
    slug="seismix1", title="Seismix 1 Mk7", sub="COMPACT ACTIVE SUBWOOFER",
    paragraphs=[
        "Compact subwoofer delivering big bass performance for everyday entertainment spaces — living "
        "rooms, apartments, gaming areas.",
        "Powered by a 200 mm woofer and Class D amplifier providing confident, controlled bass that "
        "adds warmth to music and depth to movie soundtracks. Compact, down-firing design enables "
        "flexible placement.",
    ],
    specs=[
        ("Frequency Range", "25 Hz – 200 Hz in-room"),
        ("Amplifier Power", "350 W RMS / 700 W max instantaneous"),
        ("Maximum Output", "116 dB SPL in-room"),
        ("Inputs", "Stereo line-level RCA"),
        ("USB-C", "5 V / 1 A (optional wireless receiver)"),
        ("Enclosure", "Bass reflex, down-firing vent"),
        ("LF Driver", '200 mm (8") doped paper cone, 38 mm voice coil'),
        ("Power Control", "Signal sensing, 15-min standby"),
        ("Phase Select", "0°–180° continuously variable"),
        ("Low Pass Filter", "50 Hz – 200 Hz or bypass"),
        ("Dimensions (H x W x D)", "375 x 295 x 320 mm"),
        ("Weight", "11 kg"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4deb1adad23f0f1c96541_Seismix1_BlackWoodgrain.jpg",
    gallery=["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4deb1adad23f0f1c96541_Seismix1_BlackWoodgrain.jpg"],
    brand="krix", tag="subwoofer",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69e1983fba4a1586c5288ae2_Seismix1MK7SpecificationSheet.pdf",
))

# 18. Seismix 3 Mk8
products.append(P(
    slug="seismix3", title="Seismix 3 Mk8", sub="ACTIVE SUBWOOFER",
    paragraphs=[
        "Engineered to deliver powerful, controlled bass for home theatre and high-performance audio "
        "systems. Features a 275 mm long-throw woofer and Class D amplifier, producing powerful, "
        "room-filling bass with clarity, control, and authority for both music and cinema.",
        "Australian-made.",
    ],
    specs=[
        ("Frequency Range", "22 Hz – 200 Hz in-room"),
        ("Amplifier Power", "350 W RMS / 700 W max instantaneous"),
        ("Maximum Output", "122 dB SPL in-room"),
        ("Inputs", "Stereo RCA line level, wireless audio receiver"),
        ("USB-C", "5 V / 1 A (wireless receiver power)"),
        ("Enclosure", "Bass reflex, front vented"),
        ("Driver", "275 mm doped paper cone, 50 mm voice coil"),
        ("Power Control", "Signal sensing, 15-min standby"),
        ("Phase Select", "0°–180° continuously variable"),
        ("Low Pass Filter", "50 Hz – 200 Hz or bypass"),
        ("Dimensions (H x W x D)", "450 x 360 x 410 mm"),
        ("Weight", "18 kg"),
    ],
    thumb="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4e2b9e7da97f717d7240e_Seismix3_BlackWoodgrain.jpg",
    gallery=[
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4e2b9e7da97f717d7240e_Seismix3_BlackWoodgrain.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64a4e2bccba4950b2511157d_Seismix3_BlackWoodgrainGrille.jpg",
    ],
    brand="krix", tag="subwoofer",
    specsheet="https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69e19a39d95e714c894d92b6_Seismix%203%20Mk8%20Specifications%20Sheet%20001.pdf",
))

# Commercial cinema speakers — same pattern, shorter copy where the spec PDF carries detail
KX_PRODUCTS = [
    # (slug, title, sub, paragraphs, specs, thumb, gallery, specsheet)
    ("kx-5974", "KX-5974", "4-WAY COMMERCIAL CINEMA SPEAKER", [
        "Enhances the performance of Krix patented horn arrays with the addition of an ultra-high-frequency "
        "horn, allowing all drivers to operate within optimal ranges and delivering enhanced dialogue "
        "clarity across vocal frequencies.",
        "Patented constant directivity horn technology ensures consistent frequency response throughout "
        "the venue. Features a mitred bass enclosure with proprietary X Bracing."
     ], [
        ("Configuration", "4-way with ultra-high-frequency horn"),
        ("Recommended Max Depth", "40 metres"),
        ("Bass Driver", "Engineered Krix with large ferrite magnet, dual aluminium shorting rings, symmetrical gap geometry"),
        ("Enclosure", "Mitred bass with X Bracing"),
        ("Horn Technology", "Patented Krix constant directivity"),
        ("UHF Horn", "Yes — separate ultra-high frequency horn for extended top end"),
        ("Finish", "Cinema Black"),
        ("Full Electrical / Dimensional Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65249ed8ae6722e722328a15_KX-5974.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65249ed8ae6722e722328a15_KX-5974.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/69f800ff4de8d3c6c8884ab9_KX-5974%20Cinema%20Specification%20Sheet-004.pdf"),

    ("kx-5972", "KX-5972", "4-WAY COMMERCIAL CINEMA SPEAKER", [
        "A 4-way cinema speaker that enhances performance through the addition of an ultra-high-frequency "
        "horn. Sophisticated loudspeaker modeling and Krix's patented constant directivity horn technology "
        "achieve industry-leading low distortion and smooth directivity. Mitred bass enclosure with "
        "proprietary X Bracing."
     ], [
        ("Configuration", "4-way with ultra-high-frequency horn"),
        ("Recommended Max Depth", "28 metres"),
        ("Bass Driver", "Large ferrite magnet, dual aluminium shorting rings, symmetrical gap geometry"),
        ("Enclosure", "Mitred bass with X Bracing"),
        ("Horn", "Patented Krix constant directivity"),
        ("UHF Horn", "Yes"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/652490a57a60b9e1097bf98e_KX-5972.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/652490a57a60b9e1097bf98e_KX-5972.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/64b8b1892fd64bfc7cfb4c55_KX-5972-Cinema-Specification-Sheet-005.pdf"),

    ("kx-5954", "KX-5954", "3-WAY COMMERCIAL CINEMA SPEAKER", [
        "Professional 3-way cinema loudspeaker featuring a dedicated midrange horn with dual 6\" "
        "neodymium drivers for superior dialogue clarity. Patented constant directivity horn technology "
        "achieves industry-leading low distortion and smooth directivity. Mitred bass enclosure with "
        "proprietary X Bracing."
     ], [
        ("Configuration", "3-way"),
        ("Midrange Drivers", '2 x 6" neodymium'),
        ("Midrange", "Dedicated midrange horn"),
        ("Bass Driver", "Engineered Krix with ferrite magnet structure"),
        ("Enclosure", "Mitred bass with X Bracing"),
        ("Horn Technology", "Krix patented constant directivity"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524df6e90d1ff17accf0c78_KX-5954.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524df6e90d1ff17accf0c78_KX-5954.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6673ba8e5f4402e78a9750f1_KX-5954%20Cinema%20Specification%20Sheet-001.pdf"),

    ("kx-5946", "KX-5946", "3-WAY COMMERCIAL CINEMA SPEAKER", [
        "Commercial cinema loudspeaker featuring a dedicated midrange horn with a 6\" neodymium driver for "
        "superior dialogue intelligence. Patented constant directivity horn technology delivers precision "
        "coverage and extremely uniform frequency response throughout cinema seating areas.",
        "Proprietary X Bracing in the enclosure suppresses standing waves."
     ], [
        ("Configuration", "3-way"),
        ("Recommended Max Depth", "40 metres"),
        ("Midrange Driver", '6" neodymium'),
        ("Midrange", "Dedicated midrange horn"),
        ("Bass Driver", "Large ferrite magnet, dual aluminium shorting rings, symmetrical gap geometry"),
        ("Enclosure", "Mitred bass with X Bracing"),
        ("Horn Technology", "Krix patented constant directivity"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524df2b3e26d57acc00557f_KX-5946.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524df2b3e26d57acc00557f_KX-5946.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524df4bbbe3e266fe733a7f_KX-5946%20Cinema%20Specification%20Sheet-003.pdf"),

    ("kx-5620", "KX-5620", "3-WAY COMMERCIAL CINEMA SPEAKER", [
        "3-way cinema loudspeaker incorporating a dedicated midrange horn that enhances vocal "
        "reproduction and intelligibility. Advanced acoustic engineering ensures low distortion and "
        "smooth directivity characteristics through sophisticated loudspeaker modeling.",
        "Every speaker is comprehensively tested in an advanced acoustic measurement chamber."
     ], [
        ("Configuration", "3-way"),
        ("Recommended Max Depth", "18 metres"),
        ("Midrange", "Dedicated midrange horn"),
        ("Acoustic Testing", "Advanced acoustic measurement chamber"),
        ("Enclosure", "Krix bass enclosure with X Bracing"),
        ("Horn Technology", "Krix patented constant directivity"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524a9232e8a473af83ef8ca_KX-5620.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524a9232e8a473af83ef8ca_KX-5620.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6615f7b099c14d6da548be06_KX-5620%20Cinema%20Specification%20Sheet-002.pdf"),

    ("kx-5275", "KX-5275", "2-WAY COMMERCIAL CINEMA SPEAKER", [
        "2-way cinema loudspeaker featuring dual 15\" bass drivers and a high-power 4\" diameter voice "
        "coil compression driver coupled with a Krix proprietary 90 x 40 degree horn.",
        "Patented constant directivity horn technology delivers precision coverage and extremely uniform "
        "frequency response. Mitred bass enclosure with X Bracing."
     ], [
        ("Configuration", "2-way"),
        ("Recommended Max Depth", "23 metres"),
        ("LF Drivers", '2 x 15" bass drivers'),
        ("HF Driver", '4" voice coil compression driver'),
        ("Horn", "Krix proprietary 90° x 40°"),
        ("Bass Driver", "Large ferrite magnet, dual aluminium shorting rings, symmetrical gap geometry"),
        ("Enclosure", "Mitred bass with X Bracing"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e1803b1c38af16dac36c_KX-5275.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e1803b1c38af16dac36c_KX-5275.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e1ac69e4b2ff1e3c6ed7_KX-5275%20Cinema%20Specification%20Sheet-004.pdf"),

    ("kx-5255", "KX-5255", "2-WAY COMMERCIAL CINEMA SPEAKER", [
        "Commercial cinema 2-way featuring dual 15\" bass drivers and an extended response 1¾\" diameter "
        "compression driver coupled with a Krix proprietary 90 x 40 degree horn.",
        "Achieves industry-leading low distortion and smooth directivity. Krix proprietary X Bracing in "
        "the enclosure."
     ], [
        ("Configuration", "2-way"),
        ("Recommended Max Depth", "23 metres"),
        ("LF Drivers", '2 x 15" bass drivers'),
        ("HF Driver", '1¾" extended-response compression driver'),
        ("Horn", "Krix proprietary 90° x 40°"),
        ("Bass Driver", "Large ferrite magnet, dual aluminium shorting rings, symmetrical gap geometry"),
        ("Enclosure", "X Bracing"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e1404229608fd3deb1aa_KX-5255.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e1404229608fd3deb1aa_KX-5255.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e161a13a09ca1cc4ad1e_KX-5255%20Cinema%20Specification%20Sheet-005.pdf"),

    ("kx-5205", "KX-5205", "2-WAY COMMERCIAL CINEMA SPEAKER", [
        "Professional cinema 2-way featuring a 15\" bass driver and extended response 1¾\" diameter "
        "compression driver coupled with a Krix proprietary 90 x 40 degree horn.",
        "Industry-leading low distortion and smooth directivity. X Bracing enclosure with mitred "
        "construction."
     ], [
        ("Configuration", "2-way"),
        ("Recommended Max Depth", "11 metres"),
        ("LF Driver", 'Single 15" bass driver'),
        ("HF Driver", '1¾" extended-response compression driver'),
        ("Horn", "Krix proprietary 90° x 40°"),
        ("Bass Driver", "Large ferrite magnet, dual aluminium shorting rings, symmetrical gap geometry"),
        ("Enclosure", "Mitred bass with X Bracing"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e106a13a09ca1cc4571a_KX-5205.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e106a13a09ca1cc4571a_KX-5205.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6524e126c6f60bf199dc6fa4_KX-5205%20Cinema%20Specification%20Sheet-004.pdf"),

    ("kx-4205", "KX-4205", "ATMOS SURROUND/LFE CINEMA SUBWOOFER", [
        "A passive high-performance cinema subwoofer with a single 15-inch driver. Engineered "
        "specifically for Dolby Atmos cinema installations, featuring high maximum SPL capabilities "
        "developed to satisfy Dolby Atmos surround requirements.",
        "Krix-engineered bass driver technology."
     ], [
        ("Type", "Passive surround subwoofer"),
        ("LF Driver", 'Single 15" Krix-engineered bass driver'),
        ("Use Case", "Dolby Atmos surround / LFE"),
        ("Maximum SPL", "Engineered to satisfy Dolby Atmos requirements"),
        ("Finish", "Cinema Black"),
        ("Full Electrical / Dimensional Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/652610031084758d8ce24189_KX-4205.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/652610031084758d8ce24189_KX-4205.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6526103b74270a9342d3dbc5_KX-4205%20Cinema%20Specification%20Sheet-004.pdf"),

    ("kx-1062", "KX-1062", "ATMOS CEILING SURROUND", [
        "A high-power compact cinema surround loudspeaker specially designed for ceiling surround use "
        "in Dolby Atmos and 3D surround sound applications.",
        "Shallow profile combined with pan- and tilt-adjustable bracket allows minimal clearance to the "
        "ceiling, avoiding projector beam interference. Features four neodymium 6½\" drivers for high SPL."
     ], [
        ("Configuration", "Cinema ceiling surround (4-driver)"),
        ("Drivers", '4 x neodymium 6½"'),
        ("Profile", "Shallow / low ceiling clearance"),
        ("Mounting", "Pan and tilt adjustable bracket"),
        ("Use Case", "Dolby Atmos & 3D surround sound"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e8eafc226b18d30deed1_KX-1062.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e8eafc226b18d30deed1_KX-1062.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e90cacddf2d3dcd2b503_KX-1062%20Cinema%20Specification%20Sheet-003.pdf"),

    ("kx-1061", "KX-1061", "ATMOS CEILING SURROUND", [
        "A high-power compact cinema surround loudspeaker specially designed for ceiling surround use "
        "in Dolby Atmos and 3D surround sound applications.",
        "Shallow profile combined with tilt-adjustable bracket allows minimal ceiling clearance, "
        "avoiding projector beam interference. Dual neodymium drivers achieve high SPL engineered for "
        "Dolby Atmos."
     ], [
        ("Configuration", "Cinema ceiling surround"),
        ("Drivers", "Dual neodymium drivers"),
        ("Profile", "Shallow / low ceiling clearance"),
        ("Mounting", "Tilt-adjustable bracket"),
        ("Use Case", "Dolby Atmos & 3D surround"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e7e86e85dc3a98682720_KX-1061.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e7e86e85dc3a98682720_KX-1061.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e8b7bd538012ca680738_KX-1061%20Cinema%20Specification%20Sheet-003.pdf"),

    ("kx-1570f", "KX-1570F", "FLAT CEILING ATMOS SURROUND", [
        "A low-profile flat version of the KX-1570, specifically designed for flush mounting on "
        "ceilings to meet Dolby Atmos surround sound requirements.",
        "Uses a dual-concentric driver configuration to eliminate crossover-region phasing problems. "
        "Titanium dome HF driver with 1¾\" voice coil and 90° symmetrical dispersion, plus 12\" paper "
        "cone bass driver."
     ], [
        ("Configuration", "Dual concentric, flush mount"),
        ("HF Driver", '1¾" titanium dome'),
        ("HF Dispersion", "90° symmetrical"),
        ("LF Driver", '12" paper cone'),
        ("LF Voice Coil", '2½"'),
        ("Profile", "Low / flat, ceiling-mountable"),
        ("Use Case", "Dolby Atmos surround"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65b1cfd7ded15890eb67a460_KX-1570F-500x500.jpg",
     [
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65b1cff67db9b0f4510f5071_KX-1507F.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65b1cffa72125d04c819d04c_KX-1507F%20BACK.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65b1cffe4c6d54525af6f1d9_KX-1507F%20GRILLE.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/65b1cfd7ded15890eb67a460_KX-1570F-500x500.jpg",
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e2368c508e0a3751d2a7_KX-1570%20Cinema%20Specification%20Sheet-008.pdf"),

    ("kx-1570", "KX-1570", "ATMOS CINEMA SURROUND", [
        "Engineered as a cinema surround speaker for Dolby Atmos facilities and large auditoriums. "
        "Braced, critically damped cabinet with a 15° angled front baffle optimizes auditorium coverage "
        "while preventing ceiling reflections.",
        "Dual concentric drivers eliminate crossover phasing issues. Titanium dome tweeter with 1¾\" "
        "voice coil for 90° symmetrical dispersion, plus 12\" paper cone woofer with 2½\" voice coil."
     ], [
        ("Configuration", "Dual concentric, 2-way"),
        ("Recommended Max Room Width", "43 m"),
        ("HF Driver", '1¾" titanium dome voice coil'),
        ("HF Dispersion", "90° symmetrical"),
        ("LF Driver", '12" paper cone, 2½" voice coil'),
        ("Baffle", "15° angled front baffle"),
        ("Enclosure", "Braced, critically damped"),
        ("Use Case", "Dolby Atmos surround"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e1ed091706ef3995ed3e_KX-1570.jpg",
     [
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e1ed091706ef3995ed3e_KX-1570.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e1f1091706ef3995f0f0_KX-1570%20GRILLE.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e1f3bb7bcb93cc47a149_KX-1570%20BACK.jpg",
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e2368c508e0a3751d2a7_KX-1570%20Cinema%20Specification%20Sheet-008.pdf"),

    ("kx-1875", "KX-1875", "CINEMA SURROUND LOUDSPEAKER", [
        "A cinema surround loudspeaker engineered for high power handling and high sensitivity with a "
        "low-profile design for auditoriums with limited width.",
        "Braced cabinet with critical damping and a 15° angled front baffle. Specially damped 1\" fabric "
        "dome tweeter with proprietary waveguide. Single 10\" bass driver with 2\" vented voice coil and "
        "copper shorting ring for superior surround resolution."
     ], [
        ("Configuration", "2-way"),
        ("HF Driver", '1" fabric dome with proprietary waveguide'),
        ("LF Driver", '10" bass driver'),
        ("LF Voice Coil", '2" vented with copper shorting ring'),
        ("Baffle", "15° angled front baffle"),
        ("Profile", "Low / shallow for width-constrained rooms"),
        ("Enclosure", "Braced, critically damped"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e171040afbb97f983028_KX-1875.jpg",
     [
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e171040afbb97f983028_KX-1875.jpg",
        "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e179ac64c9a72c5bf02a_KX-1875%20GRILLE.jpg",
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e0b66b667d45c122feed_KX-1870%20KX-1875%20Cinema%20Specification%20Sheet-006.pdf"),

    ("kx-1870f", "KX-1870F", "FLAT CEILING CINEMA SURROUND", [
        "Cinema surround loudspeaker engineered for high power handling and high sensitivity, with a "
        "low, flat profile specifically designed to be flush-mounted on ceilings to support Dolby Atmos "
        "surround requirements.",
        "Braced critically damped cabinet, 15° angled baffle. 1\" fabric dome tweeter with proprietary "
        "waveguide, single 10\" bass driver with 2\" vented voice coil and copper shorting ring."
     ], [
        ("Configuration", "2-way, flush-mount / flat"),
        ("HF Driver", '1" fabric dome with proprietary waveguide'),
        ("LF Driver", '10" bass driver'),
        ("LF Voice Coil", '2" vented with copper shorting ring'),
        ("Baffle", "15° angled"),
        ("Profile", "Low / flat, flush-mountable"),
        ("Use Case", "Dolby Atmos ceiling surround"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e0f3051fa172aa62de85_KX-1870F.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e0f3051fa172aa62de85_KX-1870F.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e0b66b667d45c122feed_KX-1870%20KX-1875%20Cinema%20Specification%20Sheet-006.pdf"),

    ("kx-1870", "KX-1870", "CINEMA SURROUND LOUDSPEAKER", [
        "Cinema surround loudspeaker engineered for high power handling and high sensitivity in a "
        "package suiting a wide range of cinema sound applications.",
        "Braced cabinet with a 15° angled baffle for optimized auditorium coverage and minimized "
        "ceiling reflections. 1\" fabric dome tweeter with proprietary waveguide paired with a single "
        "10\" bass driver with 2\" vented voice coil and copper shorting ring."
     ], [
        ("Configuration", "2-way"),
        ("Recommended Max Room Width", "27 m"),
        ("HF Driver", '1" fabric dome with proprietary waveguide'),
        ("LF Driver", '10" bass driver'),
        ("LF Voice Coil", '2" vented with copper shorting ring'),
        ("Baffle", "15° angled"),
        ("Enclosure", "Braced, critically damped"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e08aa26c484eeb22109a_KX-1870.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e08aa26c484eeb22109a_KX-1870.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e0b66b667d45c122feed_KX-1870%20KX-1875%20Cinema%20Specification%20Sheet-006.pdf"),

    ("kx-1840", "KX-1840", "COMPACT CINEMA SURROUND", [
        "A compact cinema surround loudspeaker designed for installations where high-quality sound is "
        "required but space is limited.",
        "15° angled front baffle with inverted driver setup, positioning the tweeter beneath the bass "
        "driver for smooth high-frequency response. Suits corner mounting in low-ceiling rooms or under "
        "balcony projection areas where overhead structures limit speaker placement."
     ], [
        ("Configuration", "Cinema surround, compact"),
        ("Baffle", "15° angled, inverted driver setup"),
        ("Tweeter Position", "Beneath bass driver"),
        ("Use Case", "Corner mount / low-ceiling / under-balcony"),
        ("Finish", "Cinema Black"),
        ("Full Specs", "See linked specification sheet PDF"),
     ],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525de9cbb7bcb93cc4357d7_KX-1840.jpg",
     ["https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525de9cbb7bcb93cc4357d7_KX-1840.jpg"],
     "https://cdn.prod.website-files.com/63e33686b480b80aa505edc2/6525e008f54e751c3ae9d75b_KX-1840%20Cinema%20Specification%20Sheet-003.pdf"),
]

for slug, title, sub, paragraphs, specs, thumb, gallery, sheet in KX_PRODUCTS:
    products.append(P(
        slug=slug, title=title, sub=sub, paragraphs=paragraphs, specs=specs,
        thumb=thumb, gallery=gallery, brand="krix", tag="speaker", specsheet=sheet,
    ))

# ============================================================
# Write
# ============================================================
OUT = os.path.join(ROOT, "batch_2026-05-26.csv")
HEADER = ["Slug", ":draft", "Title", "Sub Title", "Product Description",
          "Technical Table", "Thumbnail", "Thumbnail:alt", "Brand",
          "Product Categories", "Product Tags", "Specsheet", "Gallery"]

# Merge in the 7 StormAudio main products already authored in StormAudio_Draft_Additions.csv
# (kept in their own file so the asset-tree CSV is reproducible; pulled in here so the user
# uploads only one batch file).
STORM_MAIN = os.path.join(ROOT, "StormAudio_Draft_Additions.csv")
storm_rows = []
if os.path.exists(STORM_MAIN):
    with open(STORM_MAIN, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            storm_rows.append({h: row.get(h, "") for h in HEADER})

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(HEADER)
    for row in storm_rows:
        w.writerow([row[h] for h in HEADER])
    for p in products:
        w.writerow([p[h] for h in HEADER])

print(f"Merged {len(storm_rows)} rows from StormAudio_Draft_Additions.csv")

print(f"Wrote {OUT}")
print(f"Products: {len(products)}")
by_brand = {}
for p in products:
    by_brand.setdefault(p["Brand"], []).append(p["Slug"])
for b, s in sorted(by_brand.items()):
    print(f"  {b}: {len(s)} — {', '.join(s)}")
