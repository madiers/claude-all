# LEA × Galtech — LinkedIn film

Single minimal brand film for LinkedIn. **`lea_linkedin.mp4`** — post this.

- **1080 × 1080** (square, LinkedIn-native), **13.5 s**, H.264, 24 fps, silent audio.
- Three beats, cross-dissolved, opens/closes on black:
  **① InfoComm 2026 Best of Show badge → ② product push-in ("Networked Dante amplification · 4- & 8-channel · DSP · web control") → ③ award + "Now at Galtech Trading" + dealer CTA.**
- `_poster.jpg` — feed thumbnail. `caption.txt` — ready-to-paste caption + hashtags.

## Made with Higgsfield (this version)
- **Backdrop:** AI-generated (Higgsfield → **Nano Banana 2**, "GPT-image"-class) — a premium dark studio environment with a soft blue light pool + bokeh floor. Two options were generated; option B is used. Both saved in `_refs/`.
- **Product motion:** the real CS168D render composited onto that backdrop, then animated with **Higgsfield → Kling 3.0** (image-to-video, slow cinematic push-in + light sweep). Hardware stays photoreal/undistorted. *(Seedance was tried first but hit a false-positive content flag, so Kling was used — a nice case for keeping multiple video models.)*
- **Type, badge, intro/outro:** rendered locally (headless Chrome + ffmpeg) for crisp text; official `2026_InfoComm.png` badge.
- `_refs/` — `backdrop-option-A.png`, `backdrop-option-B-used.png`, `product-base-still.png`.

Rebuild: session scratchpad `ln/` — `render_seg.html`, `compose_hero.html`, `cap.js`, `build_seg.sh`.
