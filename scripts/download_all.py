#!/usr/bin/env python3
"""Download exactly 18 wallpapers per theme from picsum.photos."""

import os
import shutil
import sys
import time
import urllib.request

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wallpapers')
NEED = 18

THEMES = {
    'anime': [
        'japan',
        'manga',
        'artistic',
        'sketch',
        'colorful',
        'vibrant',
        'drawing',
        'paint',
        'fantasy',
        'dreamy',
        'illustration',
        'comic',
        'cartoon',
        'creative',
        'gallery',
        'portrait',
        'digital-art',
        'watercolor',
    ],
    'ai': [
        'neural',
        'digital-brain',
        'machine',
        'algorithm',
        'robot',
        'cyborg',
        'future',
        'automation',
        'deep-learning',
        'smart',
        'innovation',
        'intelligence',
        'processor',
        'chip',
        'circuit',
        'server',
        'compute',
        'cognition',
    ],
    'cybersec': [
        'cyber',
        'security',
        'firewall',
        'encrypt',
        'shield',
        'lock',
        'privacy',
        'anonymous',
        'dark-web',
        'scan',
        'defense',
        'protocol',
        'auth',
        'secure',
        'hacker',
        'matrix',
        'binary',
        'cipher',
    ],
    'dev': [
        'code',
        'programming',
        'developer',
        'terminal',
        'syntax',
        'algorithm',
        'software',
        'database',
        'framework',
        'python',
        'javascript',
        'coding',
        'debug',
        'compile',
        'version',
        'commit',
        'deploy',
        'stack',
    ],
    'science': [
        'math',
        'physics',
        'equation',
        'formula',
        'calculus',
        'quantum',
        'space',
        'cosmos',
        'gravity',
        'molecule',
        'atom',
        'particle',
        'geometry',
        'fractal',
        'nebula',
        'galaxy',
        'telescope',
        'experiment',
    ],
    'music': [
        'piano',
        'guitar',
        'melody',
        'orchestra',
        'concert',
        'notes',
        'sound',
        'acoustic',
        'vinyl',
        'headphone',
        'rhythm',
        'symphony',
        'jazz',
        'classical',
        'studio',
        'beat',
        'waveform',
        'instrument',
    ],
    'data': [
        'analytics',
        'bigdata',
        'dashboard',
        'chart',
        'statistics',
        'database',
        'network',
        'cloud',
        'visualization',
        'insight',
        'prediction',
        'pipeline',
        'warehouse',
        'mining',
        'pattern',
        'report',
        'metrics',
        'graph',
    ],
}


def download(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if len(data) < 5000:
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception:
        return False


total_ok = 0
for theme, seeds in THEMES.items():
    theme_dir = os.path.join(BASE, theme)
    os.makedirs(theme_dir, exist_ok=True)

    print(f'[{theme}] downloading {NEED} images...')
    count = 0
    for i, seed in enumerate(seeds):
        if count >= NEED:
            break
        fname = f'{theme}_{i + 1:02d}.jpg'
        dest = os.path.join(theme_dir, fname)
        url = f'https://picsum.photos/seed/{seed}/1920/1080'
        sys.stdout.write(f'  {fname} ({seed})... ')
        sys.stdout.flush()
        ok = download(url, dest)
        if ok:
            sz = os.path.getsize(dest)
            sys.stdout.write(f'OK ({sz // 1024}KB)\n')
            count += 1
            total_ok += 1
        else:
            sys.stdout.write('FAIL\n')
        time.sleep(0.5)
    print(f'  -> {theme}: {count} images\n')

# Mixed: copy from all themes
mixed_dir = os.path.join(BASE, 'mixed')
os.makedirs(mixed_dir, exist_ok=True)
idx = 1
for theme in THEMES:
    src_dir = os.path.join(BASE, theme)
    for f in sorted(os.listdir(src_dir)):
        if f.endswith('.jpg'):
            shutil.copy2(os.path.join(src_dir, f), os.path.join(mixed_dir, f'mixed_{idx:03d}.jpg'))
            idx += 1

mixed_count = len([f for f in os.listdir(mixed_dir) if f.endswith('.jpg')])
print(f'=== Done: {total_ok} images downloaded ===')
print(f'Mixed theme: {mixed_count} images')
