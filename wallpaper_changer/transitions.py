"""Visual transition effects between wallpapers — 6 fast effects."""

import math
import os
import random
import subprocess
import tempfile
import time

FRAME_DELAY = 0.4
NUM_FRAMES = 5
FRAME_SIZE = '1280x720'


def _has_magick():
    try:
        subprocess.run(['convert', '--version'], capture_output=True, timeout=3)
        return True
    except Exception:
        return False


def _identify(path, fmt='%w %h'):
    try:
        r = subprocess.run(
            ['identify', '-format', fmt, path],
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout.strip()
    except Exception:
        return None


def _convert(*args):
    try:
        subprocess.run(['convert'] + list(args), check=True, capture_output=True, timeout=15)
        return True
    except Exception:
        return False


_HAS_MAGICK = _has_magick()


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ── Helper: mask & composite ─────────────────────────────────────────

def _make_mask(path, w, h, *shape_args):
    return _convert('-size', f'{w}x{h}', 'xc:black',
                    '-fill', 'white', *shape_args,
                    '-alpha', 'off', path)


def _composite_with_mask(bg, fg, mask, out):
    return _convert(bg, fg, mask, '-composite', out)


def _frames_from_masks(old, new, masks):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new)
    frames = []
    for mask in masks:
        fd, out = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        if not _composite_with_mask(old, new, mask, out):
            os.unlink(out)
            break
        frames.append(out)
    return frames


# ── Transition generators ────────────────────────────────────────────

def _crossfade_frames(old, new, num=NUM_FRAMES):
    frames = []
    for i in range(1, num + 1):
        pct = _clamp(int(i * 100 / num), 1, 100)
        fd, path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        if not _convert(old, new, '-define', f'compose:args={pct}',
                        '-compose', 'dissolve', '-composite', path):
            os.unlink(path)
            break
        frames.append(path)
    return frames


def _circle_reveal_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    cx, cy = w // 2, h // 2
    max_r = int((w * w + h * h) ** 0.5 * 0.6) + 1

    frames = []
    for i in range(1, num + 1):
        radius = int(max_r * i / num)
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _make_mask(mask, w, h, '-draw', f'circle {cx},{cy} {cx},{cy + radius}')
            and _composite_with_mask(old, new, mask, out)
        )
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _diamond_reveal_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        s = int(min(w, h) * 0.7 * pct)
        cx, cy = w // 2, h // 2
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _make_mask(mask, w, h, '-draw',
                       f'polygon {cx},{cy - s} {cx + s},{cy} {cx},{cy + s} {cx - s},{cy}')
            and _composite_with_mask(old, new, mask, out)
        )
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _slide_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    direction = random.choice(['left', 'right', 'up', 'down'])
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        dx, dy = 0, 0
        if direction == 'left':
            dx = int(w * (1 - pct))
        elif direction == 'right':
            dx = int(-w * (1 - pct))
        elif direction == 'up':
            dy = int(h * (1 - pct))
        elif direction == 'down':
            dy = int(-h * (1 - pct))
        fd1, rolled = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _convert(new, '-roll', f'+{-dx}+{-dy}', rolled)
            and _convert(old, rolled, '-geometry', f'+{dx}+{dy}', '-composite', out)
        )
        os.unlink(rolled)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _wipe_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    horizon = random.choice(['left', 'right', 'up', 'down'])
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        x1, y1, x2, y2 = 0, 0, w, h
        if horizon == 'left':
            x2 = int(w * pct)
        elif horizon == 'right':
            x1 = int(w * (1 - pct))
        elif horizon == 'up':
            y2 = int(h * pct)
        elif horizon == 'down':
            y1 = int(h * (1 - pct))
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _make_mask(mask, w, h, '-draw', f'rectangle {x1},{y1} {x2},{y2}')
            and _composite_with_mask(old, new, mask, out)
        )
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _radial_wipe_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    max_r = int((w * w + h * h) ** 0.5 * 0.6) + 1
    frames = []
    for i in range(1, num + 1):
        r = int(max_r * i / num)
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _convert('-size', f'{w}x{h}', 'radial-gradient:white-black',
                     '-negate', '-gamma', f'{i / num}', '-alpha', 'off', mask)
            and _composite_with_mask(old, new, mask, out)
        )
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _blur_fade_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    max_blur = 8
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        blur_old = max_blur * (1 - pct) if pct < 0.5 else max_blur * (pct - 0.5) * 2
        blur_new = max_blur * (0.5 - pct) if pct < 0.5 else max_blur * (pct - 0.5)
        dissolve = int(abs(pct - 0.5) * 200)
        fd1, old_b = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, new_b = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        fd3, out = tempfile.mkstemp(suffix='.png')
        os.close(fd3)
        ok = (
            _convert(old, '-blur', f'0x{blur_old:.1f}', old_b)
            and _convert(new, '-blur', f'0x{blur_new:.1f}', new_b)
            and _convert(old_b, new_b, '-define', f'compose:args={_clamp(dissolve,1,99)}',
                         '-compose', 'dissolve', '-composite', out)
        )
        os.unlink(old_b)
        os.unlink(new_b)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _pixelate_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        scale = max(2, int(100 * (1 - 2 * abs(pct - 0.5))))
        fd1, old_p = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, new_p = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        fd3, out = tempfile.mkstemp(suffix='.png')
        os.close(fd3)
        dissolve = _clamp(int(abs(pct - 0.5) * 200), 1, 99)
        sw = max(1, int(w * scale // 100))
        sh = max(1, int(h * scale // 100))
        ok = (
            _convert(old, '-scale', f'{sw}x{sh}!', '-scale', f'{w}x{h}!', old_p)
            and _convert(new, '-scale', f'{sw}x{sh}!', '-scale', f'{w}x{h}!', new_p)
            and _convert(old_p, new_p, '-define', f'compose:args={dissolve}',
                         '-compose', 'dissolve', '-composite', out)
        )
        os.unlink(old_p)
        os.unlink(new_p)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _swirl_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        angle = int(180 * (1 - pct))
        dissolve = _clamp(int(pct * 100), 1, 100)
        fd1, swirled = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _convert(old, '-swirl', str(angle), swirled)
            and _convert(swirled, new, '-define', f'compose:args={dissolve}',
                         '-compose', 'dissolve', '-composite', out)
        )
        os.unlink(swirled)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _ripple_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    frames = []
    for i in range(num, 0, -1):
        pct = i / num
        amp = max(1, int(15 * pct))
        dissolve = _clamp(int(100 * (1 - pct)), 0, 100)
        fd1, wave_img = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _convert(new, '-wave', f'{amp}x{amp * 2}', wave_img)
            and _convert(old, wave_img, '-define', f'compose:args={dissolve}',
                         '-compose', 'dissolve', '-composite', out)
        )
        os.unlink(wave_img)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _implode_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        amount = 0.5 * (1 - pct)
        dissolve = _clamp(int(pct * 100), 1, 100)
        fd1, imp = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _convert(old, '-implode', f'{amount:.1f}', imp)
            and _convert(imp, new, '-define', f'compose:args={dissolve}',
                         '-compose', 'dissolve', '-composite', out)
        )
        os.unlink(imp)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _zoom_blur_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    cx, cy = w // 2, h // 2
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        scale = 0.5 + pct
        dissolve = _clamp(int(pct * 100), 1, 100)
        fd1, zoomed = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _convert(old, '-distort', 'SRT', f'{scale},{cx},{cy}', zoomed)
            and _convert(zoomed, new, '-define', f'compose:args={dissolve}',
                         '-compose', 'dissolve', '-composite', out)
        )
        os.unlink(zoomed)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _fade_through_black_frames(old, new, num=NUM_FRAMES):
    frames = []
    half = num // 2
    for i in range(1, num + 1):
        pct = i / num
        fd, out = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        if i <= half:
            fade = int(100 * (1 - (i - 1) / half))
            _convert(old, '-evaluate', f'multiply {fade}%', out)
        else:
            fade = int(100 * (i - half - 1) / half)
            _convert(new, '-evaluate', f'multiply {fade}%', out)
        frames.append(out)
    return frames


def _venetian_blinds_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    num_slats = 12
    slat_h = h // num_slats
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        _convert('-size', f'{w}x{h}', 'xc:black', mask)
        reveal_h = int(slat_h * pct)
        for s in range(num_slats):
            y1 = s * slat_h
            if s % 2 == 0:
                _convert(mask, '-fill', 'white', '-draw',
                         f'rectangle 0,{y1} {w},{y1 + reveal_h}', mask)
            else:
                _convert(mask, '-fill', 'white', '-draw',
                         f'rectangle 0,{y1 + slat_h - reveal_h} {w},{y1 + slat_h}', mask)
        ok = _composite_with_mask(old, new, mask, out)
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _shutter_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    num_blades = 16
    blade_w = w // num_blades
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        _convert('-size', f'{w}x{h}', 'xc:black', mask)
        reveal_w = int(blade_w * pct)
        for b in range(num_blades):
            x1 = b * blade_w
            if b % 2 == 0:
                _convert(mask, '-fill', 'white', '-draw',
                         f'rectangle {x1},0 {x1 + reveal_w},{h}', mask)
            else:
                _convert(mask, '-fill', 'white', '-draw',
                         f'rectangle {x1 + blade_w - reveal_w},0 {x1 + blade_w},{h}', mask)
        ok = _composite_with_mask(old, new, mask, out)
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _random_bars_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    random.seed(42)
    bars = sorted(random.sample(range(0, w, 4), 40))
    widths = [random.randint(20, 80) for _ in bars]
    random.seed()
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        _convert('-size', f'{w}x{h}', 'xc:black', mask)
        count = int(len(bars) * pct)
        for j in range(count):
            _convert(mask, '-fill', 'white', '-draw',
                     f'rectangle {bars[j]},0 {bars[j] + widths[j]},{h}', mask)
        ok = _composite_with_mask(old, new, mask, out)
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _ken_burns_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    direction = random.choice([(1, 1), (1, -1), (-1, 1), (-1, -1)])
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        scale = 1.0 + 0.15 * pct
        dx = int(direction[0] * w * 0.08 * pct)
        dy = int(direction[1] * h * 0.08 * pct)
        dissolve = _clamp(int(pct * 100), 1, 100)
        fd1, panned = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        ok = (
            _convert(old, '-distort', 'SRT',
                     f'{scale},{dx},{dy}', panned)
            and _convert(panned, new, '-define', f'compose:args={dissolve}',
                         '-compose', 'dissolve', '-composite', out)
        )
        os.unlink(panned)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


def _page_curl_frames(old, new, num=NUM_FRAMES):
    dims = _identify(old)
    if not dims:
        return _crossfade_frames(old, new, num)
    w, h = map(int, dims.split())
    frames = []
    for i in range(1, num + 1):
        pct = i / num
        fd1, mask = tempfile.mkstemp(suffix='.png')
        os.close(fd1)
        fd2, out = tempfile.mkstemp(suffix='.png')
        os.close(fd2)
        x_curl = int(w * (1 - pct))
        _convert('-size', f'{w}x{h}', 'xc:black',
                 '-fill', 'white',
                 '-draw', f'polygon {x_curl},0 {w},0 {w},{h} {x_curl},{h}',
                 '-alpha', 'off', mask)
        ok = _composite_with_mask(old, new, mask, out)
        os.unlink(mask)
        if not ok:
            os.unlink(out)
            break
        frames.append(out)
    return frames


# ── Registry ─────────────────────────────────────────────────────────

_TRANSITIONS = [
    ('Crossfade',       _crossfade_frames),
    ('Circle reveal',   _circle_reveal_frames),
    ('Diamond reveal',  _diamond_reveal_frames),
    ('Slide',           _slide_frames),
    ('Wipe',            _wipe_frames),
    ('Fade to black',   _fade_through_black_frames),
]


# ── Public API ───────────────────────────────────────────────────────

_last_transition = None


def apply_transition(old_path, new_path, dark=True, fit_mode=True):
    """Apply a random visual transition between two wallpapers."""
    global _last_transition

    if not _HAS_MAGICK:
        from .core import set_wallpaper as sw
        sw(new_path, dark=dark, fit_mode=fit_mode)
        return

    candidates = [t for t in _TRANSITIONS if t[0] != _last_transition]
    if not candidates:
        candidates = _TRANSITIONS
    name, func = random.choice(candidates)
    _last_transition = name
    print(f'  Transition: {name}')

    old_resized = _resize_for_transition(old_path)
    new_resized = _resize_for_transition(new_path)

    frames = func(old_resized, new_resized)
    for f in [old_resized, new_resized]:
        try:
            os.unlink(f)
        except Exception:
            pass

    if not frames:
        from .core import set_wallpaper as sw
        sw(new_path, dark=dark, fit_mode=fit_mode)
        return

    for i, fp in enumerate(frames):
        _set_any_wallpaper(fp, dark, fit_mode)
        time.sleep(FRAME_DELAY)
        try:
            os.unlink(fp)
        except Exception:
            pass

    from .core import set_wallpaper as sw
    sw(new_path, dark=dark, fit_mode=fit_mode)
    time.sleep(FRAME_DELAY)


def _resize_for_transition(path):
    """Create a temporary resized copy of the image for fast transitions."""
    fd, tmp = tempfile.mkstemp(suffix='.jpg')
    os.close(fd)
    try:
        subprocess.run(
            ['convert', path, '-resize', FRAME_SIZE, '-quality', '85', tmp],
            check=True, capture_output=True, timeout=15,
        )
        return tmp
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        return path


def _set_any_wallpaper(path, dark=False, fit_mode=True):
    """Set wallpaper without printing desktop info."""
    from .core import _backends
    backends = _backends()
    de = backends['_active']
    fn = backends[de]
    fn(path, dark=dark, fit_mode=fit_mode)
