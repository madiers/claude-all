# LEA Connect Series — Dante Amps · Instagram carousel

Dark, minimal, motion-design carousel for **LEA Professional 4- & 8-channel Dante amplifiers**, posted by Galtech Trading.

## Post order (upload the numbered files in this sequence)
| # | File | Type | Content |
|---|------|------|---------|
| 1 | `1_hero.mp4` | **video** (Higgsfield) | 8-ch amp cinematic push-in — "Networked Dante Amplification" |
| 2 | `2_four_channel.mp4` | static + text motion | "04 Channel Dante Amps" — CS84D/CS164D/CS354D/CS704D/CS1504D |
| 3 | `3_eight_channel.mp4` | static + text motion | "08 Channel Dante Amps" — CS88D/CS168D |
| 4 | `4_network.mp4` | **video** (Higgsfield) | 4-ch amp macro dolly — "Every channel, on the network" |
| 5 | `5_features.mp4` | static + text motion | Dante / DSP / browser control / 70-100V / IoT cloud |
| 6 | `6_become_a_dealer.mp4` | static + text motion | Dealer CTA — galtechtrading.com · sales@galtechtrading.com |

- **Format:** 1080 × 1350 (4:5), H.264, 24 fps, ~5 s each, silent audio track (IG-safe).
- `_preview_reel.mp4` — all six stitched for quick review (do **not** post this; upload the 6 files as a carousel).
- `_cover.jpg` — feed cover still. `_contact_sheet.png` — all six at a glance.
- `caption.txt` — ready-to-paste caption + hashtags.

## How it was made
- **Product motion (slides 1 & 4):** Higgsfield `seedance_2_0` image-to-video from dark-studio composites of the real LEA renders (`Assets/lea/_renders/`), so the hardware stays photoreal and undistorted.
- **Text & static slides:** local HTML/CSS motion design → headless-Chrome frame capture → ffmpeg. Text animates in/out; product stays pixel-perfect.
- Source project (regenerate/edit): session scratchpad `lea-carousel/` — `render.html` (design system + copy), `studio_*.html` (studio composites), `cap.js`, `build_video.sh`, `assemble.sh`.

## Specs shown (verified)
CS164D = 4 ch / 160 W·ch / Dante · CS168D = 8 ch / 160 W·ch / Dante. All models are LEA Connect Series "D" (Dante) smart amps. No prices or stock quoted (B2B).
