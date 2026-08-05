#!/usr/bin/env python3
"""
Build the ELAN Certified Dealer Agreement PDF.

Renders agreement_print.html to a 3-page, A4, fillable PDF using WeasyPrint,
after extracting the ELAN partner badges and the Galtech wordmark out of the
original agreement PDF (they are not redistributed in this repo).

    pip install pymupdf weasyprint pillow
    python3 build_pdf.py path/to/Galtech_ELAN_Certified_Dealer_Agreement_BW_Fillable.pdf

Inter must be available to the renderer. On Linux:
    curl -sA "Mozilla/4.0" \
      "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700" -o inter.css
    # download each .ttf listed in inter.css into /usr/share/fonts/truetype/inter, then:
    fc-cache -f
On macOS, install Inter from https://rsms.me/inter/ (or `brew install --cask font-inter`).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "ELAN_Certified_Dealer_Agreement.pdf")

# xref -> (soft-mask xref, output name) in the original source PDF
SOURCE_IMAGES = {
    36: (37, "badge_selected"),
    49: (50, "badge_preferred"),
    55: (56, "badge_prestige"),
    3:  (4,  "logo_galtech"),
}
BADGE_HEIGHT_PX = 450  # rendered at 24mm tall => ~475 dpi, ample for print


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
        else:
            w = round(im.width * BADGE_HEIGHT_PX / im.height)
            im = im.resize((w, BADGE_HEIGHT_PX), Image.LANCZOS)
        im.save(path, optimize=True)
        print(f"  {name:16} {im.size[0]}x{im.size[1]}")


def render():
    from weasyprint import HTML
    HTML(os.path.join(HERE, "agreement_print.html")).write_pdf(
        OUT, pdf_forms=True, optimize_images=True, full_fonts=False
    )


def main():
    if len(sys.argv) > 1:
        print("Extracting assets from", sys.argv[1])
        extract_assets(sys.argv[1])
    elif not os.path.isdir(ASSETS):
        sys.exit("assets/ is missing - pass the path to the original agreement PDF.")

    render()
    size = os.path.getsize(OUT) / 1e6
    try:
        import fitz
        doc = fitz.open(OUT)
        fields = sum(len(list(p.widgets())) for p in doc)
        print(f"Wrote {OUT} - {len(doc)} pages, {fields} form fields, {size:.2f} MB")
    except ImportError:
        print(f"Wrote {OUT} - {size:.2f} MB")


if __name__ == "__main__":
    main()
