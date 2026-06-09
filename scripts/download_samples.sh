#!/usr/bin/env bash
# Télécharge des exemples de fonds d'écran depuis picsum.photos (libres de droit)
set -euo pipefail

DIR="$(cd "$(dirname "$0")/../wallpapers" && pwd)"
COUNT=${1:-8}

echo "==> Downloading $COUNT sample wallpapers to $DIR"

for i in $(seq 1 "$COUNT"); do
    file="$DIR/sample_$(printf '%02d' "$i").jpg"
    if [ -f "$file" ]; then
        echo "  [skip] $file already exists"
        continue
    fi
    echo "  [dl]   sample_$(printf '%02d' "$i").jpg ..."
    curl -sSL -o "$file" "https://picsum.photos/1920/1080?random=$i"
done

echo "==> Done. $(ls -1 "$DIR"/*.jpg 2>/dev/null | wc -l) wallpapers available."
