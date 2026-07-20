# Galtech catalogue — additions & fixes (Framer import)

Source of truth for what to change: your live **Products.csv** (745 products) + the dealer-portal export + a multi-vendor scrape. Goal: only **add missing** and **fix broken** products; the 150 already-good ones are left untouched.

## Files
- **Galtech_AddFix_Products.csv** — import into your Framer *Products* collection. Exact schema (Slug, :draft, Title, Sub Title, Product Description, Technical Table, Thumbnail, Thumbnail:alt, Brand, Product Categories, Product Tags, Specsheet). 109 rows = 97 new + 12 fixes.
  - **New (97):** full rows built from the portal data.
  - **Fixes (12):** existing rows, with ONLY the missing Thumbnail and/or Specsheet filled in (all other fields preserved).
- **Galtech_AddFix_Galleries.csv** — Slug, Title, Gallery (comma-separated image URLs) for a gallery collection.

## Assets
Hosted under `Assets/<brand>/<slug>/` and referenced by raw GitHub URLs:
- `<slug>_main.*` — the **thumbnail**: your portal's own image, background made **transparent** (never black or white bg).
- `<slug>_g1..` — gallery images from the vendor sites, also transparent.
- `<slug>_datasheet.pdf` — spec sheet from the vendor.

All backgrounds are transparent (black/white/grey solid backgrounds flood-filled out; lifestyle/busy shots left as-is). No em-dashes.

## Known gaps (small)
- A handful of accessories have no vendor spec sheet (none exists) — thumbnail only.
- ELAN/Xantech (Nice control gear) spec sheets pending the last vendor pass; thumbnails already in.
