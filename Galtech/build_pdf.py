#!/usr/bin/env python3
"""
Build the ELAN Certified Dealer Agreement PDFs.

Two layouts share the same content and asset pipeline:

    agreement_print.html   -> ELAN_Certified_Dealer_Agreement.pdf   (compact)
    agreement_studio.html  -> ELAN_Dealer_Agreement_Studio.pdf      (editorial)

Usage:
    pip install pymupdf weasyprint pillow
    python3 build_pdf.py [--only print|studio] [path/to/original_agreement.pdf]

Passing the original agreement PDF re-extracts the ELAN partner badges and the
Galtech wordmark from it (they are not redistributed in this repo).

Fonts: Inter for both layouts, plus Chakra Petch for the studio display type.
    curl -sA "Mozilla/4.0" "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700" -o inter.css
    curl -sA "Mozilla/4.0" "https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700" -o chakra.css
    # download each .ttf into /usr/share/fonts/truetype/... then: fc-cache -f
On macOS install Inter (https://rsms.me/inter/) and Chakra Petch from Google Fonts.

Why the checkbox post-processing exists
---------------------------------------
WeasyPrint emits <input type="radio"> as a radio group whose widgets carry an
inverted /Rect and an /AP dictionary holding only the on-state, keyed through
/Opt by index. Several viewers - macOS Preview among them - will not hit-test
that, so the control renders but cannot be clicked. Instead the HTML draws a
plain anchor box in a near-paper fill, and PyMuPDF replaces each one with a
standard checkbox widget: normalised /Rect and /AP carrying both /Off and /Yes.
Those are independent checkboxes, so "tick one" is a stated rule rather than one
the file enforces; that is the deliberate trade for a control that works
everywhere.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

LAYOUTS = {
    "print":  ("agreement_print.html",  "ELAN_Certified_Dealer_Agreement.pdf"),
    "studio": ("agreement_studio.html", "ELAN_Dealer_Agreement_Studio.pdf"),
}

# xref -> (soft-mask xref, output name) in the original source PDF
SOURCE_IMAGES = {
    36: (37, "badge_selected"),
    49: (50, "badge_preferred"),
    55: (56, "badge_prestige"),
    3:  (4,  "logo_galtech"),
}
BADGE_HEIGHT_PX = 450          # drawn ~24mm tall => ~475 dpi, ample for print
ANCHOR_FILL = (0xFD / 255, 0xFD / 255, 0xFE / 255)   # near-paper marker fill
TIER_FIELDS = ["partner_selected", "partner_preferred", "partner_prestige"]


def extract_assets(source_pdf):
    """Pull the badges + wordmark out of the source PDF, preserving transparency."""
    import fitz
    from PIL import Image

    os.makedirs(ASSETS, exist_ok=True)
    doc = fitz.open(source_pdf)
    for xref, (smask, name) in SOURCE_IMAGES.items():
        path = os.path.join(ASSETS, f"{name}.png")
        # combine the base image with its soft mask to recover the alpha channel
        fitz.Pixmap(fitz.Pixmap(doc, xref), fitz.Pixmap(doc, smask)).save(path)

        im = Image.open(path).convert("RGBA")
        if name == "logo_galtech":
            # the source lockup carries an empty bar under the wordmark; keep the wordmark
            alpha = im.split()[3]
            rows = [max(alpha.crop((0, y, im.width, y + 1)).getdata()) for y in range(im.height)]
            bands, start = [], None
            for y, v in enumerate(rows):
                if v > 8 and start is None:
                    start = y
                elif v <= 8 and start is not None:
                    bands.append((start, y))
                    start = None
            if start is not None:
                bands.append((start, im.height))
            if bands:
                y0, y1 = bands[0]
                im = im.crop((0, max(0, y0 - 2), im.width, min(im.height, y1 + 2)))
            im.save(path, optimize=True)
            # the wordmark ships white for dark grounds; ink a copy for light paper
            a = im.split()[3]
            flat = Image.new("L", im.size, 16)
            Image.merge("RGBA", (flat, flat, Image.new("L", im.size, 18), a)).save(
                os.path.join(ASSETS, "logo_galtech_dark.png"), optimize=True)
        else:
            w = round(im.width * BADGE_HEIGHT_PX / im.height)
            im.resize((w, BADGE_HEIGHT_PX), Image.LANCZOS).save(path, optimize=True)
        print(f"  {name:18} ok")


def add_tier_checkboxes(pdf_path):
    """Replace the drawn anchor boxes with real, clickable checkbox widgets."""
    import fitz

    doc = fitz.open(pdf_path)
    added = 0
    for page in doc:
        anchors = []
        for drawing in page.get_drawings():
            fill = drawing.get("fill")
            if not fill or not all(abs(fill[i] - ANCHOR_FILL[i]) < 0.006 for i in range(3)):
                continue
            rect = drawing["rect"]
            if 12 < rect.width < 17 and 12 < rect.height < 17:
                anchors.append(rect)
        for name, rect in zip(TIER_FIELDS, sorted(anchors, key=lambda r: r.x0)):
            widget = fitz.Widget()
            widget.field_name = name
            widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
            widget.rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
            widget.field_value = False
            widget.border_width = 0
            widget.text_color = (0.06, 0.06, 0.07)
            page.add_widget(widget)
            added += 1
    doc.saveIncr()
    return added


def build(key):
    from weasyprint import HTML
    import fitz

    src, out_name = LAYOUTS[key]
    out = os.path.join(HERE, out_name)
    HTML(os.path.join(HERE, src)).write_pdf(
        out, pdf_forms=True, optimize_images=True, full_fonts=False)
    boxes = add_tier_checkboxes(out)

    doc = fitz.open(out)
    kinds = {}
    for page in doc:
        for w in page.widgets():
            kinds[w.field_type_string] = kinds.get(w.field_type_string, 0) + 1
    print(f"{out_name}: {len(doc)} pages, {kinds}, "
          f"{boxes} tier boxes, {os.path.getsize(out)/1e6:.2f} MB")


def main():
    args = [a for a in sys.argv[1:]]
    only = None
    if "--only" in args:
        i = args.index("--only")
        only = args[i + 1]
        del args[i:i + 2]
    if args:
        print("Extracting assets from", args[0])
        extract_assets(args[0])
    elif not os.path.isdir(ASSETS):
        sys.exit("assets/ is missing - pass the path to the original agreement PDF.")

    for key in ([only] if only else list(LAYOUTS)):
        build(key)


if __name__ == "__main__":
    main()
