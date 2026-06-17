#!/usr/bin/env python3
"""Download themed wallpapers from wallhaven.cc — 24 per theme."""

import os
import re
import sys
import time
import urllib.request

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wallpapers')
NEED = 24

THEMES = {
    'abstract':   'abstract',
    'ai':         'ai',
    'animals':    'animals',
    'anime':      'anime',
    'cyberpunk':  'cyberpunk',
    'cybersec':   'hacker',
    'fantasy':    'fantasy',
    'nature':     'nature',
}


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception:
        return None


def get_wallpaper_ids(query, needed):
    """Search wallhaven and return list of wallpaper IDs."""
    ids = []
    page = 1
    while len(ids) < needed and page <= 10:
        url = (
            f'https://wallhaven.cc/search?q={query}'
            f'&categories=111&purity=100&atleast=1920x1080'
            f'&sorting=random&page={page}'
        )
        html = fetch(url)
        if not html:
            break
        found = re.findall(r'href="https://wallhaven\.cc/w/([a-z0-9]+)"', html)
        if not found:
            break
        for wid in found:
            if wid not in ids:
                ids.append(wid)
        page += 1
        time.sleep(1)
    return ids[:needed]


def get_image_url(wallpaper_id):
    """Get the direct image URL for a wallpaper ID."""
    html = fetch(f'https://wallhaven.cc/w/{wallpaper_id}')
    if not html:
        return None
    m = re.search(r'id="wallpaper" src="([^"]+)"', html)
    if m:
        return m.group(1)
    return None


def download_image(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        if len(data) < 5000:
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception:
        return False


total_ok = 0
for theme, query in sorted(THEMES.items()):
    theme_dir = os.path.join(BASE, theme)
    os.makedirs(theme_dir, exist_ok=True)

    existing = {f for f in os.listdir(theme_dir) if f.endswith(('.jpg', '.png'))}
    count = len(existing)
    need = NEED - count
    if need <= 0:
        print(f'[{theme}] already has {count}, skipping')
        continue

    print(f'[{theme}] searching for {need} wallpapers (q={query})...')
    ids = get_wallpaper_ids(query, need)
    print(f'  Found {len(ids)} wallpaper IDs')

    for i, wid in enumerate(ids):
        if count >= NEED:
            break
        fname = f'{theme}_{count + 1:02d}'
        dest_jpg = os.path.join(theme_dir, f'{fname}.jpg')
        dest_png = os.path.join(theme_dir, f'{fname}.png')
        if dest_jpg in existing or dest_png in existing:
            count += 1
            continue

        sys.stdout.write(f'  getting {wid}... ')
        sys.stdout.flush()
        img_url = get_image_url(wid)
        if not img_url:
            sys.stdout.write('no URL\n')
            time.sleep(1)
            continue

        ext = img_url.rsplit('.', 1)[-1] if '.' in img_url else 'jpg'
        dest = os.path.join(theme_dir, f'{fname}.{ext}')
        ok = download_image(img_url, dest)
        if ok:
            sz = os.path.getsize(dest)
            sys.stdout.write(f'OK ({sz // 1024}KB)\n')
            count += 1
            total_ok += 1
        else:
            sys.stdout.write('FAIL\n')
        time.sleep(1.5)
    print(f'  -> {theme}: {count} images\n')

print(f'=== Done: {total_ok} images downloaded ===')
