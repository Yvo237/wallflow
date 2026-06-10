#!/usr/bin/env bash
set -euo pipefail

PROJECT="wallpaper-changer"
SERVICE="wallpaper-changer.service"
WALLPAPER_DIR="$HOME/.local/share/$PROJECT"

echo "==> Uninstalling $PROJECT..."

systemctl --user stop "$SERVICE" 2>/dev/null || true
systemctl --user disable "$SERVICE" 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/$SERVICE"
systemctl --user daemon-reload

pipx uninstall "$PROJECT" 2>/dev/null || true

rm -rf "$WALLPAPER_DIR"

echo "==> Done."
