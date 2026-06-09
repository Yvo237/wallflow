#!/usr/bin/env bash
set -euo pipefail

PROJECT="wallpaper-changer"
SERVICE="wallpaper-changer.service"

echo "==> Uninstalling $PROJECT..."

systemctl --user stop "$SERVICE" 2>/dev/null || true
systemctl --user disable "$SERVICE" 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/$SERVICE"
systemctl --user daemon-reload

sudo rm -f /usr/local/bin/wallpaper-changer

pip3 uninstall "$PROJECT" -y 2>/dev/null || true

echo "==> Done."
