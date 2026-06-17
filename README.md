# Wallpaper Changer

> Rotate your desktop wallpapers automatically.

![Python](https://img.shields.io/badge/python-3.8+-blue)
![Desktop](https://img.shields.io/badge/desktop-GNOME|KDE|Sway|i3|XFCE|Cinnamon|MATE|Hyprland-green)
![systemd](https://img.shields.io/badge/service-systemd-orange)
![CI](https://github.com/YOUR_USER/wallpaper-changer/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

**Wallpaper Changer** is a lightweight Python tool that cycles through a directory of images and applies them as your desktop background at a configurable interval. It ships with a systemd user service for seamless autostart.

```
wallpaper-changer v1.0.0
Interval: 45s  |  Images: 125
Dir: /home/user/wallpaper-changer/wallpapers/mixed
Press Ctrl+C to stop.

Wallpaper: mixed_001.jpg
  [desktop: gnome]
```

---

## Quick Start

```bash
git clone https://github.com/<your-user>/wallpaper-changer.git
cd wallpaper-changer
make install          # pip install --user -e .
make service-install  # enable & start systemd service
```

That's it. Your wallpaper will start rotating every 45 seconds using the 4 sample images included in the repo.

> **Add your own images**: just drop `.jpg` or `.png` files into the `wallpapers/` folder and they'll be picked up automatically on the next cycle.

---

## Usage

### CLI

```bash
# Run manually
wallpaper-changer

# Use a theme (8 available)
wallpaper-changer --theme mixed

# Custom interval & directory
wallpaper-changer --dir ~/Images --interval 60

# List available themes
wallpaper-changer --list-themes

# Pass through python -m
python3 -m wallpaper_changer --interval 30
```

| Argument | Default | Description |
|----------|---------|-------------|
| `-d, --dir` | `~/Pictures/Wallpapers` | Image directory |
| `-t, --theme` | — | Theme: `abstract`, `ai`, `animals`, `anime`, `cyberpunk`, `cybersec`, `fantasy`, `nature`, `mixed` |
| `--list-themes` | — | Show available themes and exit |
| `-i, --interval` | `45` | Seconds between changes |
| `--no-dark` | `false` | Skip dark-mode variant |
| `-V, --version` | | Show version |

#### Visual transitions (v1.1.0+)

When changing wallpapers, a random visual effect is applied (requires ImageMagick). **6 transitions** available (fast enough for real-time use):

| # | Transition | Description |
|---|-----------|-------------|
| 1 | **Crossfade** | Smooth dissolve between images |
| 2 | **Circle reveal** | Growing circle uncovers the new wallpaper |
| 3 | **Diamond reveal** | Diamond shape grows from center |
| 4 | **Slide** | New image slides in from a random direction |
| 5 | **Wipe** | Progressive reveal from one edge |
| 6 | **Fade to black** | Cinematic fade through black |

Without ImageMagick, wallpapers change instantly as before.

#### Smart mixed mode (v1.1.0+)

When using `--theme mixed`, the images are sourced **directly** from all other theme directories (no duplicate copies — the `wallpapers/mixed/` directory is no longer needed). The playlist is interleaved so no two consecutive images come from the same theme, ensuring maximum variety without wasted disk space.

#### New themes (v1.1.0+)

The project now includes **8 themes** (24 images each):

`abstract` · `ai` · `animals` · `anime` · `cyberpunk` · `cybersec` · `fantasy` · `nature`

Plus the virtual **`mixed`** theme that interleaves all of them.

### Service

```bash
make service-start     # systemctl --user start
make service-stop      # systemctl --user stop
make service-restart   # systemctl --user restart
make service-logs      # journalctl -f
make service-remove    # remove service
```

---

## Installation (for end users)

### One-liner (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/<user>/wallpaper-changer/main/scripts/install.sh | bash
```

### Manual

```bash
git clone https://github.com/<your-user>/wallpaper-changer.git
cd wallpaper-changer
./scripts/install.sh
```

### Uninstall

```bash
./scripts/uninstall.sh
# or
make service-remove && pip3 uninstall wallpaper-changer -y
```

---

## How it works

1. Discovers all images (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`) in the target directory.
2. Loops through them indefinitely, applying each via the appropriate tool for your desktop environment.
3. Supports **8 desktop environments** out of the box: GNOME, KDE, Sway, i3, XFCE, Cinnamon, MATE, Hyprland.
4. Handles both light and dark variants on supported desktops (GNOME, Cinnamon).
5. A systemd user service (`--user`) keeps the process alive across sessions.

### Configuration file

Settings can be persisted in `~/.config/wallpaper-changer.toml`:

```toml
theme = "mixed"
interval = 45
```

CLI flags always override config values. See the [sample config](systemd/wallpaper-changer.service) for all options.

---

## Project structure

```
wallpaper-changer/
├── wallpaper_changer/          # Python package
│   ├── __init__.py             # Version info
│   ├── __main__.py             # python -m entry point
│   ├── core.py                 # Image discovery & wallpaper logic
│   ├── transitions.py          # Visual transition effects
│   └── cli.py                  # Argument parser & main loop
├── wallpapers/                 # Themes (24 images each)
│   ├── abstract/               #   Abstrait
│   ├── ai/                     #   Intelligence artificielle
│   ├── animals/                #   Animaux
│   ├── anime/                  #   Anime, manga
│   ├── architecture/           #   Architecture
│   ├── cyberpunk/              #   Cyberpunk
│   ├── cybersec/               #   Cybersécurité
│   ├── data/                   #   Data science
│   ├── dev/                    #   Développement
│   ├── fantasy/                #   Fantastique
│   ├── minimal/                #   Minimaliste
│   ├── music/                  #   Musique
│   ├── nature/                 #   Nature
│   ├── retro/                  #   Rétro / Synthwave
│   └── science/                #   Sciences
├── systemd/
│   └── wallpaper-changer.service  # systemd unit template
├── scripts/
│   ├── download_all.py         # Download sample wallpapers
│   ├── install.sh              # Automated install
│   └── uninstall.sh            # Clean removal
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions CI
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pyproject.toml              # Package metadata, CLI, ruff config
├── Makefile                    # Convenience commands
├── CHANGELOG.md
├── README.md
├── LICENSE
└── .gitignore
```

---

## Requirements

- **Python 3.8+**
- **systemd** (optional — for service mode)
- **pip3** (for installation)
- One of: GNOME, KDE, Sway, i3 (feh), XFCE, Cinnamon, MATE, or Hyprland

---

## License

[MIT](LICENSE)
