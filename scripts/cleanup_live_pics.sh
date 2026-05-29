#!/usr/bin/env bash
# Removes the 68 already-live product folders from "NEW Product Pics".
# Live = the product slug already exists in Products_Framer_29_may.csv.
# Run from repo root:  bash scripts/cleanup_live_pics.sh
set -euo pipefail
cd "$(dirname "$0")/.."

targets=(
  # MAG AIR series mainline (already live)
  "NEW Product Pics/AIR series/AIR-122"
  "NEW Product Pics/AIR series/AIR-152"
  "NEW Product Pics/AIR series/AIR-62"
  "NEW Product Pics/AIR series/AIR-82"
  "NEW Product Pics/AIR series/AIR-S12 (S12-IP)"
  "NEW Product Pics/AIR series/AIR-S15 (S15-IP)"
  "NEW Product Pics/AIR series/AIR-S18 (S18-IP)"

  # MAG AIR-C series (already live)
  "NEW Product Pics/AIR-C series/AIR-C24"
  "NEW Product Pics/AIR-C series/AIR-C4"
  "NEW Product Pics/AIR-C series/AIR-C5"
  "NEW Product Pics/AIR-C series/AIR-C6"
  "NEW Product Pics/AIR-C series/AIR-C8"
  "NEW Product Pics/AIR-C series/AIR-CX-10"
  "NEW Product Pics/AIR-C series/AIR-CX-12"
  "NEW Product Pics/AIR-C series/AIR-CX-15"
  "NEW Product Pics/AIR-C series/AIR-S26"
  "NEW Product Pics/AIR-C series/AIR-S26A"

  # MAG Amplification (io-16000 is live)
  "NEW Product Pics/Amplification/Amplifiers/IO-16000"

  # MAG PD-PowerDistributor (all 6 live)
  "NEW Product Pics/PD-PowerDistributor/PD - 1x8"
  "NEW Product Pics/PD-PowerDistributor/PD - 2T604"
  "NEW Product Pics/PD-PowerDistributor/PD - 2x4"
  "NEW Product Pics/PD-PowerDistributor/PD - 2x8"
  "NEW Product Pics/PD-PowerDistributor/PD - 3x4"
  "NEW Product Pics/PD-PowerDistributor/PD - 4x4"

  # Krix Dedicated Home Cinema (live)
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Freestanding/Cinematix"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Freestanding/Flix"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Freestanding/Pix"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Freestanding/Theatrix"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/In-wall/Megaphonix Centre In-Wall"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/In-wall/Scenix"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Linear LCR - Soundbar"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/AS-200"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/AS-325"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-10"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-20"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-30"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-40"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Modular/MX-5"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/Hyperphonix 45"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/Megaphonix Centre"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/On-wall/Megaphonix Flat"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Subwoofer/Cyclonix 11"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Subwoofer/Cyclonix 12"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Subwoofer/Cyclonix 12 Active Compact"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Subwoofer/Cyclonix 15"
  "NEW Product Pics/KRIX Dedicated Home Cinema Product Images/Subwoofer/Cyclonix 18"

  # Krix Home Entertainment (live)
  "NEW Product Pics/KRIX Home Entertainment Product Images/Bookshelf/Acoustix Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Bookshelf/Esoterix Altum"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Centre Channel/Epicentrix Mk2"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Centre Channel/Graphix Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Centre Channel/Vortex Mk2"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Evara range/Acoustix Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Evara range/Graphix Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Evara range/Phoenix Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Evara range/Seismix 3D Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Floorstanding/Harmonix Mk2"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Floorstanding/Neuphonix Mk2"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Floorstanding/Phoenix Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Floorstanding/Phoenix Mk2"
  "NEW Product Pics/KRIX Home Entertainment Product Images/In-Ceiling/Hemispherix SPS"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Outdoor/Hemispherix SPS"
  "NEW Product Pics/KRIX Home Entertainment Product Images/In-Wall/Epix"
  "NEW Product Pics/KRIX Home Entertainment Product Images/In-Wall/IW-30"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Subwoofer/Seismix 1 Mk7"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Subwoofer/Seismix 3 Mk8"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Subwoofer/Seismix 3D Evara"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Subwoofer/Seismix 3D Mk3"
  "NEW Product Pics/KRIX Home Entertainment Product Images/Subwoofer/Seismix 5"
)

before=$(du -sk "NEW Product Pics" 2>/dev/null | awk '{print $1}')
for t in "${targets[@]}"; do
  if [[ -d "$t" ]]; then
    rm -rf "$t" && echo "deleted: $t"
  fi
done
after=$(du -sk "NEW Product Pics" 2>/dev/null | awk '{print $1}')
echo
echo "NEW Product Pics: $((before-after)) KB reclaimed"
echo "Remaining size:"
du -sh "NEW Product Pics"
