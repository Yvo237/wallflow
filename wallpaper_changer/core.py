"""Core module — wallpaper rotation logic."""

import os
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


def _set_gnome(path, dark):
    uri = 'file://' + path
    ok = _run(f'gsettings set org.gnome.desktop.background picture-uri {shlex.quote(uri)}')
    if dark:
        _run(f'gsettings set org.gnome.desktop.background picture-uri-dark {shlex.quote(uri)}')
    return ok


def _set_kde(path, dark):
    script = (
        f'var allDesktops = desktops();'
        f'for (var i=0; i<allDesktops.length; i++) {{'
        f'  allDesktops[i].wallpaperPlugin = "org.kde.image";'
        f'  allDesktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];'
        f'  allDesktops[i].writeConfig("Image", {shlex.quote(path)});'
        f'}}'
    )
    return _run(
        f'qdbus org.kde.PlasmaShell /PlasmaShell org.kde.PlasmaShell.evaluateScript {shlex.quote(script)}'
    )


def _set_sway(path, dark):
    return _run(f'swaymsg output "*" bg {shlex.quote(path)} fill')


def _set_i3(path, dark):
    return _run(f'feh --bg-fill {shlex.quote(path)}')


def _set_xfce(path, dark):
    props = [
        '/backdrop/screen0/monitor0/workspace0/last-image',
        '/backdrop/screen0/monitor0/workspace0/image-style',
    ]
    ok = True
    for prop in props:
        ok &= _run(f'xfconf-query -c xfce4-desktop -p {prop} -s {shlex.quote(path)}')
    return ok


def _set_cinnamon(path, dark):
    uri = 'file://' + path
    ok = _run(f'gsettings set org.cinnamon.desktop.background picture-uri {shlex.quote(uri)}')
    if dark:
        _run(f'gsettings set org.cinnamon.desktop.background picture-uri-dark {shlex.quote(uri)}')
    return ok


def _set_mate(path, dark):
    return _run(f'gsettings set org.mate.background picture-filename {shlex.quote(path)}')


def _set_hyprland(path, dark):
    return _run(f'hyprctl hyprpaper wallpaper ",{shlex.quote(path)}"')


def discover_images(directory):
    """Return sorted list of image paths in *directory*."""
    images = []
    for f in sorted(os.listdir(directory)):
        if f.lower().endswith(IMAGE_EXTENSIONS):
            images.append(os.path.join(directory, f))
    return images


def set_wallpaper(path, dark=True):
    """Set wallpaper using auto-detected desktop environment."""
    backends = _backends()
    de = backends['_active']
    fn = backends[de]
    print(f'  [desktop: {de}]')
    return fn(path, dark)
