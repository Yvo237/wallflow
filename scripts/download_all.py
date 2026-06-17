#!/usr/bin/env python3
"""Download themed wallpapers from picsum.photos — 24 per theme."""

import os
import sys
import time
import urllib.request

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wallpapers')
NEED = 24

THEME_SEEDS = {
    'ai':           ['neural', 'circuit', 'processor', 'chip', 'server', 'robot',
                     'algorithm', 'matrix', 'digital', 'compute', 'machine', 'core',
                     'quantum', 'tech', 'brain', 'cognition', 'automation', 'data',
                     'node', 'vector', 'cloud', 'network', 'system', 'logic'],
    'anime':        ['japan', 'tokyo', 'temple', 'garden', 'cherry', 'lantern',
                     'calligraphy', 'pagoda', 'kimono', 'bamboo', 'origami', 'zen',
                     'mountain-fuji', 'japan-street', 'shrine', 'samurai', 'geisha',
                     'osaka', 'kyoto', 'nara', 'hokkaido', 'japan-art', 'dojo', 'bonsai'],
    'cybersec':     ['cyber', 'lock', 'shield', 'secure', 'privacy', 'encrypt',
                     'firewall', 'anonymous', 'defense', 'protocol', 'vault',
                     'guard', 'safe', 'protect', 'cipher', 'key', 'secure-line',
                     'identity', 'scan', 'monitor', 'gate', 'access', 'stealth', 'armor'],
    'dev':          ['code', 'terminal', 'keyboard', 'monitor', 'laptop', 'workspace',
                     'developer', 'software', 'database', 'stack', 'debug', 'compile',
                     'python', 'javascript', 'server', 'cloud', 'docker', 'linux',
                     'git', 'desk-setup', 'coding', 'office', 'tech-desk', 'minimal-desk'],
    'science':      ['microscope', 'laboratory', 'experiment', 'chemistry', 'biology',
                     'physics', 'molecule', 'dna', 'telescope', 'space', 'galaxy',
                     'nebula', 'planet', 'atom', 'crystal', 'fractal', 'math',
                     'formula', 'gravity', 'particle', 'quantum', 'stellar', 'cosmos', 'satellite'],
    'music':        ['piano', 'guitar', 'concert', 'studio', 'headphone', 'microphone',
                     'vinyl', 'orchestra', 'instrument', 'speaker', 'dj', 'live-music',
                     'acoustic', 'singer', 'band', 'drum', 'saxophone', 'trumpet',
                     'violin', 'cello', 'harp', 'flute', 'organ', 'amplifier'],
    'data':         ['analytics', 'dashboard', 'chart', 'graph', 'statistics',
                     'network', 'cloud', 'database', 'server', 'visualization',
                     'insight', 'predict', 'pipeline', 'cluster', 'warehouse',
                     'metrics', 'report', 'mining', 'pattern', 'diagram',
                     'infographic', 'map', 'flow', 'grid'],
    'nature':       ['forest', 'mountain', 'ocean', 'river', 'waterfall', 'lake',
                     'sunset', 'aurora', 'beach', 'valley', 'canyon', 'glacier',
                     'desert', 'island', 'reef', 'volcano', 'meadow', 'alpine',
                     'coast', 'cliff', 'cave', 'star', 'moon', 'rainbow'],
    'retro':        ['vintage', 'retro-car', 'old-city', 'cassette', 'polaroid',
                     'arcade', 'neon-sign', 'synthwave', 'eighties', 'retro-gaming',
                     'old-school', 'classic-car', 'vintage-camera', 'retro-tv',
                     'analog', 'record-player', 'typewriter', 'old-phone',
                     'vintage-clock', 'retro-bike', 'old-radio', 'vintage-poster',
                     'retro-train', 'classic-watch'],
    'fantasy':      ['castle', 'dragon', 'knight', 'sword', 'magic', 'crystal',
                     'crown', 'throne', 'shield', 'armor', 'tower', 'bridge',
                     'stone', 'ruins', 'cathedral', 'chapel', 'monastery', 'gothic',
                     'medieval', 'viking', 'celtic', 'mythical', 'enchanted', 'mystic'],
    'cyberpunk':    ['neon', 'city-night', 'rain-night', 'street-lamp', 'cityscape',
                     'skyline', 'night-city', 'bridge-night', 'highway-night',
                     'china-town', 'shibuya', 'times-square', 'las-vegas',
                     'tokyo-night', 'hong-kong', 'neon-light', 'city-rain',
                     'downtown', 'urban-night', 'skyscraper', 'metropolis', 'futuristic',
                     'night-market', 'cyber-city'],
    'minimal':      ['minimal', 'simple', 'clean', 'geometry', 'pattern', 'white',
                     'architecture-minimal', 'interior', 'space', 'light',
                     'shadow', 'line', 'shape', 'form', 'texture', 'surface',
                     'glass', 'steel', 'concrete', 'wood', 'paper', 'fabric',
                     'monochrome', 'pastel'],
    'abstract':     ['abstract', 'colorful', 'vibrant', 'pattern', 'texture',
                     'gradient', 'geometric', 'fluid', 'wave', 'spiral',
                     'mosaic', 'kaleidoscope', 'fractal', 'blur', 'bokeh',
                     'light-paint', 'neon-abstract', 'liquid', 'smoke', 'ink',
                     'paint-splash', 'graffiti', 'mandala', 'symmetry'],
    'animals':      ['cat', 'dog', 'horse', 'bird', 'eagle', 'owl', 'wolf',
                     'fox', 'deer', 'bear', 'lion', 'tiger', 'elephant',
                     'giraffe', 'zebra', 'monkey', 'panda', 'koala', 'penguin',
                     'dolphin', 'whale', 'butterfly', 'swan', 'parrot'],
    'architecture': ['architecture', 'building', 'bridge', 'tower', 'facade',
                     'interior', 'staircase', 'window', 'door', 'column',
                     'modern-house', 'skyscraper', 'cathedral', 'museum',
                     'library', 'stadium', 'theater', 'office', 'apartment',
                     'hotel', 'shrine', 'temple', 'church', 'mosque'],
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
for theme, seeds in sorted(THEME_SEEDS.items()):
    theme_dir = os.path.join(BASE, theme)
    os.makedirs(theme_dir, exist_ok=True)

    existing = {f for f in os.listdir(theme_dir) if f.endswith('.jpg')}
    count = len(existing)
    print(f'[{theme}] {count} existing, need {NEED}...')

    for i, seed in enumerate(seeds):
        if count >= NEED:
            break
        fname = f'{theme}_{count + 1:02d}.jpg'
        dest = os.path.join(theme_dir, fname)
        if os.path.exists(dest):
            count += 1
            continue
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
        time.sleep(0.4)
    print(f'  -> {theme}: {count} images\n')

print(f'=== Done: {total_ok} new images downloaded ===')
