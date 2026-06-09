#!/usr/bin/env bash
set -euo pipefail

PROJECT="wallpaper-changer"
SERVICE="wallpaper-changer.service"

echo "==> Installing $PROJECT..."

# 1. Install Python package
if ! command -v pip3 &>/dev/null; then
    echo "Error: pip3 not found. Install python3-pip first."
    exit 1
fi

pip3 install --user -e "$(dirname "$0")/.."

# 2. Locate installed binary
BIN="$(python3 -m site --user-base)/bin/wallpaper-changer"
if [ ! -f "$BIN" ]; then
    echo "Error: binary not found at $BIN"
    exit 1
fi

# 3. Symlink into PATH
if [ ! -f /usr/local/bin/wallpaper-changer ]; then
    sudo ln -sf "$BIN" /usr/local/bin/wallpaper-changer
fi

# 4. Install systemd user service
mkdir -p "$HOME/.config/systemd/user"
sed "s|/usr/local/bin/wallpaper-changer|$BIN|" \
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
echo "    Uninstall: make service-remove && pip3 uninstall $PROJECT -y"
