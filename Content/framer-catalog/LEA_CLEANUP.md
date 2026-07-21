# LEA cleanup — duplicates + wrong thumbnails/galleries

## What was wrong

1. **Duplicate products.** Every LEA amp exists twice on the live site: once with the
   correct plain slug (`cs352d`) and once with a `lea-` prefixed slug (`lea-cs352d`).
   Both are titled the same ("LEA CS352D"). The `lea-` set came from an early rough import.
2. **Wrong images.** The `lea-` set was built from portal images, several of which are the
   wrong model. Confirmed: `lea-cs352d` (and the thumbnail that leaked onto plain `cs352d`)
   actually show a **702D**, not a 352D. The portal images are unreliable, so all LEA
   thumbnails + galleries have been rebuilt from LEA's own model-exact vendor renders.

## Action 1 — delete these 25 duplicate products (keep the plain slug)

Delete the `lea-` version; the plain version stays.

| delete | keep | delete | keep |
|---|---|---|---|
| lea-cs34   | cs34   | lea-cs354  | cs354  |
| lea-cs34d  | cs34d  | lea-cs354d | cs354d |
| lea-cs64   | cs64   | lea-cs702  | cs702  |
| lea-cs64d  | cs64d  | lea-cs702d | cs702d |
| lea-cs124  | cs124  | lea-cs704  | cs704  |
| lea-cs124d | cs124d | lea-cs704d | cs704d |
| lea-cs164  | cs164  | lea-cs84d  | cs84d  |
| lea-cs164d | cs164d | lea-cs88   | cs88   |
| lea-cs168  | cs168  | lea-cs88d  | cs88d  |
| lea-cs168d | cs168d | lea-cs1504 | cs1504 |
| lea-cs352  | cs352  | lea-cs1504d| cs1504d|
| lea-cs352d | cs352d | lea-cs3004 | cs3004 |
|            |        | lea-cs3004d| cs3004d|

## Action 2 — rename 1 product

`lea-cs84` has no plain twin. **Rename its slug `lea-cs84` -> `cs84`** (don't delete it).
Its correct thumbnail/gallery are in the re-import below.

## Action 3 — keep these 4 (no change)

`lea-cs-touch-blk`, `lea-cs-touch-wht`, `lea-rcaf-2`, `lea-xlrf` are accessories with no
plain twin and correct images. Leave them as they are.

## Action 4 — re-import to fix thumbnails + galleries

`Content/framer-catalog/LEA_FIX.csv` — 50 rows, plain slugs, model-exact vendor renders
(Thumbnail + Gallery). Import it and match on **Slug**. This overwrites the wrong images on
the surviving plain-slug products and covers the 4 previously-missing non-Dante models
(cs84, cs88, cs164, cs168).

- Import into the **galleries** collection (columns already match: Slug, Title,
  Product Description, Brand, Thumbnail, Gallery, Specsheet).
- If your product-page thumbnail is driven by the **Products** collection instead, import
  the same file there too — it will update the Thumbnail column on matching slugs.

The per-brand source files are also updated: `Sources/data/LEA_Products.csv` and
`LEA_Images.csv` (now 50 rows each), and the consolidated `Galtech_Galleries.csv` LEA rows
now use the correct renders.

Notes:
- Half-rack compacts (cs34/cs62/cs64/cs122/cs124 and their `d` variants) use LEA's shared
  compact-chassis render; LEA does not publish a distinct photo per half-rack model.
- `-adsp`, `-g`, and `cds` variants share their base model's chassis render (same enclosure).
