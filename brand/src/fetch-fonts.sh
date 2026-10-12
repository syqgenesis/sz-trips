#!/usr/bin/env bash
# Download the open-source (SIL OFL) fonts the build outlines into the logo files.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p fonts
base=https://raw.githubusercontent.com/google/fonts/main/ofl
for f in \
  "cormorantgaramond/CormorantGaramond[wght].ttf" \
  "cormorantgaramond/CormorantGaramond-Italic[wght].ttf" \
  "bodonimoda/BodoniModa[opsz,wght].ttf" \
  "hankengrotesk/HankenGrotesk[wght].ttf"; do
  out="fonts/$(basename "$f")"
  [ -f "$out" ] || curl -sSfL -o "$out" "$base/$(printf '%s' "$f" | sed 's/\[/%5B/;s/\]/%5D/')"
done
echo "fonts ready"
