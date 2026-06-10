#!/usr/bin/env bash
set -euo pipefail

PROJECT="wallpaper-changer"
SERVICE="wallpaper-changer.service"
WALLPAPER_DIR="$HOME/.local/share/$PROJECT"
BIN="$HOME/.local/bin/$PROJECT"
THEME="${1:-mixed}"

echo "==> Installing $PROJECT (theme: $THEME)..."

# 1. Install Python package via pipx (isolated, stable)
if ! command -v pipx &>/dev/null; then
    echo "Error: pipx not found. Install pipx first (apt install pipx)."
    exit 1
fi

pipx install "$(dirname "$0")/.." --force

# 2. Copy wallpapers to stable location
echo "==> Copying wallpapers to $WALLPAPER_DIR"
mkdir -p "$WALLPAPER_DIR"
cp -r "$(dirname "$0")/../wallpapers"/* "$WALLPAPER_DIR"/

# 3. Install systemd user service
mkdir -p "$HOME/.config/systemd/user"
sed -e "s|{{BIN}}|$BIN|" \
    -e "s|{{WALLPAPER_DIR}}|$WALLPAPER_DIR|" \
    -e "s|{{THEME}}|$THEME|" \
    "$(dirname "$0")/../systemd/$SERVICE" \
    > "$HOME/.config/systemd/user/$SERVICE"

systemctl --user daemon-reload
systemctl --user enable "$SERVICE"
systemctl --user start "$SERVICE"

echo ""
echo "==> Done! $PROJECT is now running."
echo "    Status:  systemctl --user status $SERVICE"
echo "    Logs:    journalctl --user -u $SERVICE -f"
echo "    Stop:    systemctl --user stop $SERVICE"
echo "    Uninstall: make service-remove && pipx uninstall $PROJECT && rm -rf $WALLPAPER_DIR"
