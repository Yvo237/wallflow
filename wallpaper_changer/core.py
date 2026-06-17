"""Core module — wallpaper rotation logic."""

import os
import random
import shlex
import subprocess

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

_DESKTOPS = {}


def _detect_desktop():
    env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    if 'gnome' in env or 'budgie' in env:
        return 'gnome'
    if 'kde' in env:
        return 'kde'
    if 'sway' in env:
        return 'sway'
    if 'i3' in env:
        return 'i3'
    if 'xfce' in env:
        return 'xfce'
    if 'cinnamon' in env:
        return 'cinnamon'
    if 'mate' in env:
        return 'mate'
    if 'hyprland' in env:
        return 'hyprland'
    return 'gnome'


def _backends():
    if _DESKTOPS:
        return _DESKTOPS

    de = _detect_desktop()

    _DESKTOPS.update(
        {
            'gnome': _set_gnome,
            'kde': _set_kde,
            'sway': _set_sway,
            'i3': _set_i3,
            'xfce': _set_xfce,
            'cinnamon': _set_cinnamon,
            'mate': _set_mate,
            'hyprland': _set_hyprland,
        }
    )

    if de not in _DESKTOPS:
        print(f"Warning: unknown desktop '{de}', falling back to GNOME")
        de = 'gnome'

    _DESKTOPS['_active'] = de
    return _DESKTOPS


def _run(cmd):
    try:
        subprocess.run(shlex.split(cmd), check=True, capture_output=True, timeout=10)
        return True
    except Exception:
        return False


def _set_gnome(path, dark, fit_mode=True):
    uri = 'file://' + path
    ok = _run(f'gsettings set org.gnome.desktop.background picture-uri {shlex.quote(uri)}')
    if dark:
        _run(f'gsettings set org.gnome.desktop.background picture-uri-dark {shlex.quote(uri)}')
    option = 'scaled' if fit_mode else 'zoom'
    _run(f'gsettings set org.gnome.desktop.background picture-options {option}')
    return ok


def _set_kde(path, dark, fit_mode=True):
    fill_mode = '3' if fit_mode else '2'
    script = (
        f'var allDesktops = desktops();'
        f'for (var i=0; i<allDesktops.length; i++) {{'
        f'  allDesktops[i].wallpaperPlugin = "org.kde.image";'
        f'  allDesktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];'
        f'  allDesktops[i].writeConfig("Image", {shlex.quote(path)});'
        f'  allDesktops[i].writeConfig("FillMode", "{fill_mode}");'
        f'}}'
    )
    return _run(
        f'qdbus org.kde.PlasmaShell /PlasmaShell org.kde.PlasmaShell.evaluateScript {shlex.quote(script)}'
    )


def _set_sway(path, dark, fit_mode=True):
    mode = 'fit' if fit_mode else 'fill'
    return _run(f'swaymsg output "*" bg {shlex.quote(path)} {mode}')


def _set_i3(path, dark, fit_mode=True):
    flag = '--bg-max' if fit_mode else '--bg-fill'
    return _run(f'feh {flag} {shlex.quote(path)}')


def _set_xfce(path, dark, fit_mode=True):
    style = '2' if fit_mode else '3'
    ok = _run(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -s {shlex.quote(path)}')
    ok &= _run(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/image-style -s {style}')
    return ok


def _set_cinnamon(path, dark, fit_mode=True):
    uri = 'file://' + path
    ok = _run(f'gsettings set org.cinnamon.desktop.background picture-uri {shlex.quote(uri)}')
    if dark:
        _run(f'gsettings set org.cinnamon.desktop.background picture-uri-dark {shlex.quote(uri)}')
    option = 'scaled' if fit_mode else 'zoom'
    _run(f'gsettings set org.cinnamon.desktop.background picture-options {option}')
    return ok


def _set_mate(path, dark, fit_mode=True):
    ok = _run(f'gsettings set org.mate.background picture-filename {shlex.quote(path)}')
    option = 'scaled' if fit_mode else 'zoom'
    _run(f'gsettings set org.mate.background picture-options {option}')
    return ok


def _set_hyprland(path, dark, fit_mode=True):
    return _run(f'hyprctl hyprpaper wallpaper ",{shlex.quote(path)}"')


def discover_images(directory):
    """Return sorted list of image paths in *directory*."""
    images = []
    for f in sorted(os.listdir(directory)):
        if f.lower().endswith(IMAGE_EXTENSIONS):
            images.append(os.path.join(directory, f))
    return images


def set_wallpaper(path, dark=True, fit_mode=True):
    """Set wallpaper using auto-detected desktop environment."""
    backends = _backends()
    de = backends['_active']
    fn = backends[de]
    print(f'  [desktop: {de}]')
    return fn(path, dark, fit_mode=fit_mode)


def discover_mixed_images(themes_dir, exclude='mixed'):
    """Build an interleaved playlist from all themes so no two
    consecutive images come from the same theme directory."""
    theme_images = {}
    for entry in sorted(os.listdir(themes_dir)):
        td = os.path.join(themes_dir, entry)
        if entry == exclude or not os.path.isdir(td):
            continue
        imgs = discover_images(td)
        if imgs:
            random.shuffle(imgs)
            theme_images[entry] = imgs

    if not theme_images:
        return []

    theme_names = list(theme_images.keys())
    pending = {t: list(imgs) for t, imgs in theme_images.items()}
    playlist = []
    last_theme = None

    while any(pending.values()):
        available = [t for t in theme_names if pending[t] and t != last_theme]
        if not available:
            available = [t for t in theme_names if pending[t]]
        theme = max(available, key=lambda t: len(pending[t]))
        playlist.append(pending[theme].pop(0))
        last_theme = theme

    return playlist
