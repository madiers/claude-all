# claude-all — Framer CMS product pipeline

Staging area for product asset (images + datasheets) and the import CSVs that load them into the **Framer Products CMS** at madiers.framer.website. Framer fetches all assets directly from this repo over `raw.githubusercontent.com`, so anything not pushed here doesn't reach Framer.

Brands handled here: Krix, BassBoss, MAG Audio, StormAudio, Nice, Gefen, Stealth Acoustics, Garvan Acoustics, Fasttel, Netvio, LEA, Advatek, Cornered Audio, Pulse-Eight, Innovo, Flat Panel Audio, Gallo Acoustics, Furman, Lukh-ee, Kordz, Micro-Nova, Bond.

---

## The pattern, end-to-end

```
new vendor assets  →  diff vs live CSV  →  research on vendor site  →
mirror PDFs+images into repo  →  build batch CSV  →  commit + push  →
import to Framer  →  re-export + diff to catch silent drops
```

### 1. Take inventory of what's new

A dump of vendor assets lands in a folder like `NEW Product Pics/<Series>/<Product>/...`. To find which products are NEW (vs. already in Framer):

```bash
python3 -c "
import csv
with open('Products_Framer_<date>.csv') as f: rows=list(csv.reader(f))
live = set(r[0] for r in rows[1:] if len(r)>8 and r[8]=='<brand-slug>')
print('\n'.join(sorted(live)))
"
```

Then map each `NEW Product Pics/<Series>/<Product>` folder to a candidate slug and check against `live`. Anything missing needs a new row in the next batch CSV.

The latest live export of the Framer Products collection lives at [Products_Framer_29_may.csv](Products_Framer_29_may.csv) (rename + commit a new one whenever you re-export).

### 2. Research each new product on the vendor's site

Browse the vendor's product page (e.g. `https://krix.com.au/<product>`, `https://mag-audio.com/<series>/<product>`, `https://www.bassboss.com/<product>`) and capture for each:

| Field | Where it comes from |
|---|---|
| Title | The product's commercial name as the vendor uses it |
| Sub Title | One-line tagline (≤80 chars), vendor's marketing voice |
| Product Description | Rich HTML: `<h3>` intro line + `<p>` paragraph + `<ul><li>` highlights + closing `<p>` (~120-180 words) |
| Technical Table | `<table><tbody><tr><th>Specification</th><th>Value</th></tr>...</tbody></table>` — real specs from the vendor's datasheet |
| Specsheet | Find the datasheet PDF on the vendor site, download URL |

Skip-or-flag products the vendor doesn't actually sell ("Arts" was marketing renders, not a SKU — folder was dropped, not imported).

Don't make up specs. If the vendor's page is thin, copy what's there and leave the rest empty; don't invent numbers.

### 3. Mirror vendor PDFs into the repo

**Framer's Specsheet field silently drops external vendor URLs.** Only `raw.githubusercontent.com/madiers/claude-all/<branch>/...` and `framerusercontent.com/assets/...` URLs survive on import. So every datasheet has to live in this repo.

Download each PDF into the same folder as the product's images:

```
NEW Product Pics/<Series>/<Product>/<slug>_datasheet.pdf
```

[scripts/download_pdfs.py](scripts/download_pdfs.py) is the canonical fetcher — reads `scripts/research_<brand>.json` and writes each PDF into the right folder. Pattern for downloading:

```python
req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
with urllib.request.urlopen(req, timeout=30) as r:
    data = r.read()
assert data[:4] == b"%PDF"   # reject error pages
with open(f"<folder>/{slug}_datasheet.pdf", "wb") as f:
    f.write(data)
```

Images are usually delivered as zips; unzip them under `NEW Product Pics/<Series>/<Product>/` with the original filenames. The CSV refers to specific files by name.

### 4. Build the batch CSV

**13 columns, exactly:**

```
Slug,:draft,Title,Sub Title,Product Description,Technical Table,
Thumbnail,Thumbnail:alt,Brand,Product Categories,Product Tags,
Specsheet,Gallery
```

(`Gallery` exists in `Products_Import.csv`; the brand-specific Site_Enrichment / Draft_Additions CSVs omit it.)

Image / PDF URLs all use the same prefix:

```
https://raw.githubusercontent.com/madiers/claude-all/<branch>/<percent-encoded-repo-path>
```

For new products, set `:draft=true`. Re-importing an existing slug **UPDATES** that entry — Framer upserts by `Slug` — so it's safe (and useful) to include refreshes of already-live products in the same batch.

**One combined batch CSV per session** — `batch_YYYY-MM-DD.csv` — covering every new product across every brand. One file, one upload.

See [batch_2026-05-29.csv](batch_2026-05-29.csv) for the most recent example, and [scripts/merge_batch_2026-05-29.py](scripts/merge_batch_2026-05-29.py) for the skeleton → final-CSV merger.

#### Per-brand split CSVs (Garvan + Fasttel, 2026-06-08)

For Garvan and Fasttel the import is split into **two files per brand**, both keyed by `Slug`, so product copy and images can be imported (and re-imported) independently:

- `<Brand>_Products.csv` — `Slug, :draft, Title, Sub Title, Product Description, Technical Table, Brand, Product Categories, Product Tags, Specsheet` (no image columns).
- `<Brand>_Images.csv` — `Slug, Thumbnail, Thumbnail:alt, Gallery`.

Built by [scripts/build_csvs.py](scripts/build_csvs.py) from the live export, `scripts/garvan_manifest.json`, and `scripts/research_fasttel.json` + `scripts/fasttel_manifest.json`. Categories/Tags are restricted to values already present in the live export (no new collection slugs). Assets live in `Assets/<brand>/<slug>/`; the FT600 family datasheet is shared at `Assets/fasttel/_shared/`.

### 5. Commit + push in chunks under 2 GB

GitHub's per-push pack limit is around 2 GB. Anything bigger gets `remote end hung up unexpectedly` somewhere past 2.3 GB. To keep pushes reliable:

1. `git config http.postBuffer 524288000` (one-time)
2. Split large work across multiple commits — each top-level `NEW Product Pics/<Series>` folder is a reasonable unit, none has been larger than ~900 MB
3. Push after each commit; if `Connection reset by peer`, retry the same `git push` — transient

A clean sequence for a large batch:

```bash
# small commit first (cleanup + small assets + CSV + scripts)
git add -u  # picks up deletions
git add scripts/ batch_*.csv "NEW Product Pics/<small-folder>" ...
git commit -m "..."
git push

# then one commit per large series
git add "NEW Product Pics/AIR series"      && git commit -m "Add AIR series" && git push
git add "NEW Product Pics/AIR-C series"    && git commit -m "Add AIR-C series" && git push
git add "NEW Product Pics/VerA"            && git commit -m "Add VerA"          && git push
```

### 6. Cleanup as products go live

Once a product's images are in Framer (visible as `framerusercontent.com/...` URLs in the next export), the source folder under `NEW Product Pics/<Series>/<Product>` is functionally redundant — Framer's CDN now serves the assets. To save space:

- Re-export Framer to `Products_Framer_<date>.csv`
- Identify which slugs in `NEW Product Pics` are now live
- Delete those subfolders (`scripts/cleanup_live_pics.sh` is the pattern)
- Commit the deletions

What stays in the repo: brand asset folders are reduced to the *new draft* set only, so future audits know exactly what's outstanding.

### 7. Verify the import — silent drops are real

Framer accepts rows with bad data and silently empties the cell. Always after import:

1. Re-export the Products collection.
2. Diff submitted batch vs. export per slug.
3. Any row where Brand/Categories/Tags/Specsheet/Thumbnail differs is a silent drop. Patch the offending field and re-import only the affected rows — Framer upserts by slug.

---

## The three silent-drop gotchas

1. **Brand, Product Categories, Product Tags are reference fields.** Each value must exactly match an existing slug in Framer's Brands / Categories / Tags collections. Unknown values silently drop — the cell becomes blank.

   Known good slugs (as of 2026-05-29):
   - **Brands:** `storm-audio` (not `stormaudio`), `krix`, `bassboss`, `mag-audio`, `garvan-acoustics`, `nice`, `gefen`, `fasttel`, `netvio`, `stealth-acoustics`, `lea`, `advatek-lighting`, `cornered-audio`, `pulse-eight`, `innovo`, `flat-panel-audio`, `gallo-acoustics`, `furman`, `lukh-ee`, `kordz`, `micro-nova`, `bond`
   - **Categories:** `audio`, `video`, `control-system`, `automation`, `lighting`, or combos like `audio,cinema` / `cinema,audio`
   - **Tags:** `speaker`, `subwoofer`, `amplifier`, `controller`, `receiver`, `extender`, `matrix`, `outdoor`, `cinema`, `acoustic-sound-panels`, `cabling`, `door-phone`, `touch-panel`, `encoder`, `decoder`, `install-kit`, `faceplates`, `power-conditioner`, `splitter`, `video-distribution`, `remote-control`
   - **Never** use marketing tags like `dolby-atmos`, `dts-x`, `dirac-live`, `dante`, `processor`, `accessory` — they don't exist in the collection. If a genuinely new tag is needed, add it in Framer first, then reference the slug.

2. **Specsheet is a File field, not a URL field.** Only `raw.githubusercontent.com/madiers/claude-all/<branch>/...pdf` or `framerusercontent.com/assets/...pdf` URLs work. Vendor URLs (`cdn.prod.website-files.com/...`, `mag-audio.com/...`, etc.) look fine in the CSV but always drop on import.

3. **Thumbnail cannot be blank for new products.** Empty Thumbnail = product imports without an image. Source a photo before shipping, or document the gap.

---

## Repository layout

```
.
├── README.md                          # this file
├── batch_<date>.csv                   # current session's combined import CSV
├── batch_<date>_skeleton.csv          # asset-URL skeleton produced before research
├── Products_Framer_<date>.csv         # last full export of Framer Products collection
├── Products_Framer_Export.csv         # alias / latest copy
├── <Brand>_Site_Enrichment.csv        # updates to already-live entries for one brand
├── <Brand>_Draft_Additions.csv        # new draft rows for one brand
│
├── NEW Product Pics/                  # active draft set — products not yet in Framer
│   ├── AIR series/Accessories/
│   ├── AIR-C series/
│   ├── KRIX Dedicated Home Cinema Product Images/
│   ├── KRIX Home Entertainment Product Images/
│   └── VerA/
│
├── MAG/, KRIX/, BASSBOSS/,            # historical per-brand asset trees;
│   StormAudio/, Impulsion-8/,         # safe to trim once products are live + verified
│   Products/                          # (Products/ holds Nice rows + their Products_Import.csv)
│
└── scripts/
    ├── cleanup_live_pics.sh           # delete subfolders of NEW Product Pics once live
    ├── download_pdfs.py               # mirror vendor PDFs into the repo
    ├── merge_batch_<date>.py          # skeleton + research JSON → final batch CSV
    ├── research_mag.json              # per-brand research output (Title, specs, Specsheet URL)
    ├── research_krix.json
    └── pdf_paths.json                 # slug → local PDF path map used by CSV rewrite
```

`.gitignore` covers `__pycache__/`, `*.pyc`, `.DS_Store`.

---

## Quick reference

- Live export to diff against: [Products_Framer_29_may.csv](Products_Framer_29_may.csv)
- Latest batch CSV: [batch_2026-05-29.csv](batch_2026-05-29.csv)
- Krix CSVs: [Krix_Draft_Additions.csv](Krix_Draft_Additions.csv), [Krix_Site_Enrichment.csv](Krix_Site_Enrichment.csv)
- Earlier batches: [batch_2026-05-26.csv](batch_2026-05-26.csv), [batch_2026-05-26_magaudio.csv](batch_2026-05-26_magaudio.csv), etc.
- Cleanup script: [scripts/cleanup_live_pics.sh](scripts/cleanup_live_pics.sh)
- PDF mirror script: [scripts/download_pdfs.py](scripts/download_pdfs.py)
- Repo root on GitHub: https://github.com/madiers/claude-all

Branch in active use: read it from `git rev-parse --abbrev-ref HEAD`, then plug into the raw URL template above.
