"""Command-line interface."""

import argparse
import os
import signal
import sys
import time
from pathlib import Path

import tomllib

from . import __version__
from .core import discover_images, set_wallpaper

DEFAULT_DIR = os.path.expanduser('~/Pictures/Wallpapers')
DEFAULT_INTERVAL = 45

_PKG_DIR = Path(__file__).resolve().parent.parent
THEMES_DIR = _PKG_DIR / 'wallpapers'
AVAILABLE_THEMES = ['anime', 'ai', 'cybersec', 'dev', 'science', 'music', 'data', 'mixed']
CONFIG_PATH = Path('~/.config/wallpaper-changer.toml').expanduser()


def load_config():
    """Load settings from TOML config file, return dict of overrides."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, 'rb') as f:
            return tomllib.load(f)
    except Exception as e:
        print(f'Warning: could not load config: {e}')
        return {}


def build_parser():
    parser = argparse.ArgumentParser(
        prog='wallpaper-changer',
        description='Rotate your desktop wallpaper automatically.',
        epilog='Config file: ~/.config/wallpaper-changer.toml',
    )
    parser.add_argument(
        '-d', '--dir', default=None, help='Image directory (overrides config / --theme)'
    )
    parser.add_argument(
        '-t', '--theme', choices=AVAILABLE_THEMES, help=f'Theme: {", ".join(AVAILABLE_THEMES)}'
    )
    parser.add_argument('--list-themes', action='store_true', help='List available themes and exit')
    parser.add_argument('-i', '--interval', type=int, default=None, help='Seconds between changes')
    parser.add_argument(
        '--no-dark', action='store_true', default=None, help='Skip dark-mode variant'
    )
    parser.add_argument(
        '-V', '--version', action='version', version=f'wallpaper-changer v{__version__}'
    )
    return parser


def merge_args_with_config(args):
    """CLI args override config file which overrides defaults."""
    cfg = load_config()

    resolved = argparse.Namespace()
    resolved.dir = args.dir or cfg.get('dir')
    resolved.theme = args.theme or cfg.get('theme')
    resolved.interval = (
        args.interval if args.interval is not None else cfg.get('interval', DEFAULT_INTERVAL)
    )
    resolved.no_dark = args.no_dark if args.no_dark is not None else cfg.get('no_dark', False)
    resolved.list_themes = args.list_themes
    return resolved


def resolve_dir(namespace):
    if namespace.list_themes:
        print('Available themes:')
        for t in AVAILABLE_THEMES:
            td = THEMES_DIR / t
            count = (
                len([f for f in os.listdir(td) if f.endswith(('.jpg', '.png'))])
                if td.is_dir()
                else 0
            )
            marker = ' ★' if t == 'mixed' else ''
            print(f'  {t:12s}  ({count} images){marker}')
        sys.exit(0)
    if namespace.dir:
        return namespace.dir
    if namespace.theme:
        td = THEMES_DIR / namespace.theme
        if td.is_dir():
            return str(td)
        print(f"Theme '{namespace.theme}' not found at {td}")
        sys.exit(1)
    return DEFAULT_DIR


def main():
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    args = merge_args_with_config(build_parser().parse_args())
    img_dir = resolve_dir(args)
    images = discover_images(img_dir)

    if not images:
        print(f'No images found in {img_dir}')
        sys.exit(1)

    print(f'wallpaper-changer v{__version__}')
    print(f'Interval: {args.interval}s  |  Images: {len(images)}')
    print(f'Dir: {img_dir}')
    print('Press Ctrl+C to stop.\n')

    while True:
        for img in images:
            name = os.path.basename(img)
            print(f'Wallpaper: {name}')
            set_wallpaper(img, dark=not args.no_dark)
            time.sleep(args.interval)
