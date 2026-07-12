# Netvio — AV distribution (animated IG carousel)

Dark **animated** carousel: product fades in from black over a moving dark background, NETVIO wordmark top-left, "Galtech Trading" top-right, feature checklist, GALTECH logo bottom-left. Style per Figma nodes 5694-2 / 5694-15 + `2.mp4` (fade in / fade out). Upload the 6 MP4s in order.

1. `1_cover.mp4` — "Netvio" (JP4 AVoIP rack)
2. `2_avoip.mp4` — "JP4 · AV-over-IP" (encoder)
3. `3_matrix.mp4` — "HDMI & HDBaseT Matrix"
4. `4_connections.mp4` — "Every I/O, on board" (rear panel)
5. `5_control.mp4` — "One app. Total control." (touch panel)
6. `6_become_a_dealer.mp4` — CTA · Middle East

- **1080 × 1350** (4:5), H.264, 24 fps, ~5 s each, silent audio. Each fades from/to black (loop-friendly).
- `_preview_reel.mp4` = all six stitched (review only). `_cover.jpg`, `_contact_sheet.png`, `caption.txt`.
- **Made with Higgsfield** — animated dark background = Seedance 2.0 (text-to-video); real Netvio product photos cut out locally (colorkey/lumakey) + text/logos/animation rendered locally (Chrome + ffmpeg).

Rebuild: session scratchpad `nv2/` — `render_nv2.html`, `cap.js`, `build_nv2.sh`.
