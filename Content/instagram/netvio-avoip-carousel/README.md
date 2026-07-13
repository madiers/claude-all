# Netvio — AV distribution & control (animated IG carousel)

Black-ground animated carousel (KRIX house style). Each slide: product fades in from black over a softly drifting spotlight, NETVIO wordmark top-left, "Galtech Trading" top-right, feature checklist, GALTECH logo bottom-left. No AI-video background (clean local render, no artifacts).

Upload the 5 MP4s in order:
1. `1_cover_distribute.mp4` — "Distribute anything" (JP4 AVoIP rack)
2. `2_avoip_jp4.mp4` — "JP4 · AV-over-IP" (encoder)
3. `3_matrix_hdbaset.mp4` — "HDMI & HDBaseT Matrix"
4. `4_control_app.mp4` — "One app. Total control." (touch panel)
5. `5_become_a_dealer.mp4` — CTA · Middle East

- **1080 × 1350** (4:5), H.264, 24 fps, ~5 s each, silent audio. Each fades from/to black (loop-friendly).
- `_preview_reel.mp4` = all five stitched (review only). `_cover.jpg`, `_contact_sheet.png`, `caption.txt`.
- Real Netvio product photos cut out locally (colorkey/lumakey); text, logos and animation rendered locally (Chrome + ffmpeg).

Rebuild: session scratchpad `brands/` — `render_brand.html?brand=netvio`, `cap.js`, `build_brands.sh`.
