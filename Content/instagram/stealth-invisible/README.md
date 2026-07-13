# Stealth Acoustics — invisible speakers (animated IG carousel)

Black-ground animated carousel (KRIX house style). Each slide: product fades in from black, STEALTH / ACOUSTICS wordmark top-left, "Galtech Trading" top-right, feature checklist, GALTECH logo bottom-left.

Upload the 5 MP4s in order:
1. `1_cover_invisible.mp4` — "Sound you can't see" (LRX-85 paintable panel)
2. `2_driver_reveal.mp4` — "The speaker behind the wall" (LRX-85 dual-driver, HTA 2022 award)
3. `3_stingray_outdoor.mp4` — "StingRay · Invisible outdoors" (weatherproof)
4. `4_sa2400_amp.mp4` — SA2400 MK II amplifier
5. `5_become_a_dealer.mp4` — CTA · Middle East

- **1080 × 1350** (4:5), H.264, 24 fps, ~5 s each, silent audio. Fades from/to black (loop-friendly).
- `_preview_reel.mp4`, `_cover.jpg`, `_contact_sheet.png`, `caption.txt`.
- Products cut from Stealth composite/packshot images (crop + colorkey white + alpha-trim). The white LR panels are white-on-white and uncuttable, so the grey LRX-85 panel/driver and dark StingRay are used. Text, logos and animation rendered locally (Chrome + ffmpeg).

Rebuild: session scratchpad `brands/` — `render_brand.html?brand=stealth`, `cut_stealth.sh`, `build_stealth.sh`.
