#!/usr/bin/env python3
"""Генерирует графику NebulaOS (только стандартная библиотека Python).

    python tools/make-art.py            # логотип, иконки, загрузчик, Plymouth
    python tools/make-art.py --all      # плюс обои режимов (дольше)

Стиль: глубокий космос, многослойная туманность (фрактальный шум), звёздное поле,
виньетка и лёгкое зерно. Логотип «Орбита»: планета с мягкой светотенью,
тонкое кольцо с зазором над планетой и четырёхлучевая искра.
"""
import math
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARE = ROOT / "desktop/usr/share"
MODES = SHARE / "nebulaos/modes"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# ---------- PNG ----------
def write_png(path, w, h, rows, alpha=False):
    """rows: итератор строк; каждая строка — список пикселей (r, g, b[, a]) в 0..255."""
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for p in row:
            raw += bytes(max(0, min(255, int(c + 0.5))) for c in p[:4 if alpha else 3])

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6 if alpha else 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
    print(f"{path.relative_to(ROOT)}  {w}x{h}  {len(png) // 1024} KB")


def grid_rows(w, h, fn):
    for y in range(h):
        yield [fn(x, y) for x in range(w)]


# ---------- Логотип ----------
VIOLET, PINK, CYAN, LILAC = rgb("#8b5cf6"), rgb("#ec4899"), rgb("#5eead4"), rgb("#a78bfa")
TILT = math.radians(-20)
PLANET_R = 0.43
RING_A, RING_B, RING_W = 0.88, 0.235, 0.032
GAP = 0.016          # зазор между передней частью кольца и планетой


def logo_sample(x, y):
    """(r, g, b, a) логотипа в точке [-1, 1]²."""
    xr = x * math.cos(TILT) + y * math.sin(TILT)
    yr = -x * math.sin(TILT) + y * math.cos(TILT)
    d = math.hypot(xr / RING_A, yr / RING_B)
    ring_dist = abs(d - 1) * RING_B          # приблизительное расстояние до оси кольца
    r = math.hypot(x, y)
    front = yr > 0
    out = (0, 0, 0, 0)

    def ring_color():
        t = (xr + RING_A) / (2 * RING_A)
        c = mix(CYAN, LILAC, t)
        return mix(c, (255, 255, 255), 0.18 * (1 - abs(2 * t - 1)))

    # Задняя часть кольца — за планетой.
    if ring_dist < RING_W and not front:
        out = ring_color() + (235,)
    if r < PLANET_R:
        # Градиент + светотень: свет сверху слева, мягкий терминатор, тонкий ободок.
        u = (x + PLANET_R) / (2 * PLANET_R)
        v = (y + PLANET_R) / (2 * PLANET_R)
        col = mix(VIOLET, PINK, 0.65 * u + 0.35 * v)
        nz = math.sqrt(max(0.0, 1 - (r / PLANET_R) ** 2))
        light = max(0.0, (-x * 0.55 - y * 0.70) / PLANET_R * 0.6 + nz * 0.55)
        col = mix((58, 22, 98), col, 0.35 + 0.65 * smooth(0.0, 0.6, light))
        col = mix(col, (255, 240, 255), 0.22 * smooth(0.75, 1.0, light))
        rim = smooth(PLANET_R - 0.035, PLANET_R, r)
        col = mix(col, LILAC, 0.35 * rim * smooth(0.0, 0.3, x * 0.5 - y * 0.5 + 0.2))
        out = col + (255,)
    if front:
        if ring_dist < RING_W:
            out = ring_color() + (255,)
        elif ring_dist < RING_W + GAP and r < PLANET_R + 0.01:
            out = (0, 0, 0, 0)       # «вырез» в планете — кольцо читается чётко
    # Искра: четыре тонких луча + маленькое ядро.
    sx, sy = x - 0.70, y + 0.66
    ax, ay = abs(sx), abs(sy)
    ray = max(math.exp(-(ay / 0.012) ** 2) * smooth(0.16, 0.0, ax),
              math.exp(-(ax / 0.012) ** 2) * smooth(0.16, 0.0, ay))
    core = math.exp(-(sx * sx + sy * sy) / 0.0009)
    s = min(1.0, ray + core)
    if s > 0.02:
        a = out[3] / 255
        c = mix(out[:3] if a else (255, 255, 255), (255, 255, 255), s)
        out = c + (255 * max(a, s),)
    return out


def logo_pixel_fn(size, ss=3, scale=1.0):
    def pixel(px, py):
        acc = [0.0, 0.0, 0.0, 0.0]
        for i in range(ss):
            for j in range(ss):
                x = ((px + (i + 0.5) / ss) / size * 2 - 1) * scale
                y = ((py + (j + 0.5) / ss) / size * 2 - 1) * scale
                r, g, b, a = logo_sample(x, y)
                acc[0] += r * a
                acc[1] += g * a
                acc[2] += b * a
                acc[3] += a
        if acc[3] == 0:
            return (0, 0, 0, 0)
        return (acc[0] / acc[3], acc[1] / acc[3], acc[2] / acc[3], acc[3] / (ss * ss))
    return pixel


# ---------- Туманность ----------
class Noise:
    def __init__(self, seed):
        rnd = random.Random(seed)
        self.p = list(range(256))
        rnd.shuffle(self.p)
        self.p += self.p
        self.v = [rnd.random() for _ in range(256)]

    def value(self, x, y):
        xi, yi = int(math.floor(x)), int(math.floor(y))
        xf, yf = x - xi, y - yi
        u, w = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
        p, v = self.p, self.v
        a = v[p[(xi & 255) + p[yi & 255]]]
        b = v[p[((xi + 1) & 255) + p[yi & 255]]]
        c = v[p[(xi & 255) + p[(yi + 1) & 255]]]
        d = v[p[((xi + 1) & 255) + p[(yi + 1) & 255]]]
        return (a + (b - a) * u) + ((c + (d - c) * u) - (a + (b - a) * u)) * w

    def fbm(self, x, y, octaves=5):
        s, amp, f, norm = 0.0, 0.5, 1.0, 0.0
        for _ in range(octaves):
            s += amp * self.value(x * f, y * f)
            norm += amp
            amp *= 0.5
            f *= 2.03
        return s / norm


def nebula_wallpaper(w, h, spec, seed, logo=None):
    """Цельная туманность вдоль диагонали: искажённый фрактальный шум, цвет плавно
    меняется по палитре, яркая сердцевина, звёзды, виньетка и зерно."""
    bg_top, bg_bottom = rgb(spec["top"]), rgb(spec["bottom"])
    pal = [rgb(c) for c in spec["palette"]]
    core_col = rgb(spec["core"])
    k = spec.get("density", 0.85)
    noise = Noise(seed)
    sc = 2.6
    lw, lh = w // 3, h // 3
    aspect = w / h
    low = []
    for y in range(lh + 1):
        row = []
        for x in range(lw + 1):
            u, v = x / lw, y / lh
            px, py = u * sc * aspect, v * sc
            # Domain warping — «волокна» вместо круглых облаков.
            wx = px + 0.9 * noise.fbm(px + 5.2, py + 1.3, 3)
            wy = py + 0.9 * noise.fbm(px + 1.7, py + 9.2, 3)
            d = noise.fbm(wx, wy, 5)
            axis = spec.get("axis", (0.22, 0.55))
            band = math.exp(-((v - (axis[0] + axis[1] * u)) / 0.27) ** 2)
            dens = smooth(0.40, 0.80, d) * (0.12 + 0.88 * band)
            core = smooth(0.60, 0.92, d) * band
            hue = noise.fbm(u * 1.6 + 20.0, v * 1.6 + 7.0, 3)
            row.append((dens, core, hue))
        low.append(row)

    def palette(t):
        t = max(0.0, min(0.999, (t - 0.3) / 0.4)) * (len(pal) - 1)
        i = int(t)
        return mix(pal[i], pal[min(i + 1, len(pal) - 1)], t - i)

    rnd = random.Random(seed + 1)
    stars = {}
    for _ in range(int(w * h * spec.get("stars", 0.0008))):
        x, y = rnd.randrange(w), rnd.randrange(h)
        b = 0.25 + 0.75 * rnd.random() ** 4
        stars[(x, y)] = max(stars.get((x, y), 0), b)
        if b > 0.8:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                stars[(x + dx, y + dy)] = max(stars.get((x + dx, y + dy), 0), b * 0.35)
    grain = random.Random(seed + 2)
    lp = logo_pixel_fn(logo[2], ss=2) if logo else None

    def pixel(x, y):
        u, v = x / w, y / h
        col = mix(bg_top, bg_bottom, v * 0.85 + u * 0.15)
        fx, fy = u * lw, v * lh
        x0, y0 = int(fx), int(fy)
        tx, ty = fx - x0, fy - y0
        x1, y1 = min(x0 + 1, lw), min(y0 + 1, lh)
        a, b, c, d = low[y0][x0], low[y0][x1], low[y1][x0], low[y1][x1]
        vals = [(a[i] * (1 - tx) + b[i] * tx) * (1 - ty) + (c[i] * (1 - tx) + d[i] * tx) * ty for i in range(3)]
        dens, core, hue = vals
        col = mix(col, palette(hue), dens * k)
        col = mix(col, core_col, core * spec.get("glow", 0.35))
        s = stars.get((x, y))
        if s:
            col = mix(col, (255, 250, 255), s * (1 - 0.6 * dens))
        vig = 1 - 0.55 * ((u - 0.5) ** 2 + (v - 0.5) ** 2) * 1.8
        g = (grain.random() - 0.5) * spec.get("grain", 5)
        col = tuple(cc * vig + g for cc in col)
        if lp:
            lx, ly = x - (logo[0] - logo[2] // 2), y - (logo[1] - logo[2] // 2)
            if 0 <= lx < logo[2] and 0 <= ly < logo[2]:
                r, gg, bb, al = lp(lx, ly)
                col = mix(col, (r, gg, bb), al / 255)
        return col
    return grid_rows(w, h, pixel)


SPECS = {
    # Гейминг: чёрный космос, красно-оранжевая туманность (как акцент режима).
    "gaming": {"top": "#050506", "bottom": "#0d0809", "palette": ["#3a0a0e", "#a3121c", "#e5484d", "#ff8a3d"],
               "core": "#ffd2b0", "glow": 0.26, "density": 0.88, "stars": 0.0010, "grain": 6, "axis": (0.18, 0.62)},
    # Хакинг: графитовый космос, синяя туманность в цвете macOS.
    "hacking": {"top": "#0b0c0f", "bottom": "#080a10", "palette": ["#0c1f44", "#0a4fb0", "#0a84ff", "#64d2ff"],
                "core": "#d6efff", "glow": 0.26, "density": 0.85, "stars": 0.0008, "grain": 5, "axis": (0.20, 0.55)},
    # Сервер: нейтральный тёмно-серый космос с оранжевой туманностью Ubuntu.
    "server": {"top": "#121212", "bottom": "#1a1513", "palette": ["#3a2a22", "#8a3415", "#e95420", "#f6a03d"],
               "core": "#ffe0b8", "glow": 0.20, "density": 0.80, "stars": 0.0006, "grain": 5, "axis": (0.15, 0.65), "seed": 314},
}


# Галерея: ещё 6 туманностей в разных настроениях (Настройки → Обои).
GALLERY = {
    "nebula-aurora": {"top": "#030a0c", "bottom": "#061418", "palette": ["#0f3b44", "#0d9488", "#22d3ee", "#a7f3d0"],
                      "core": "#ecfeff", "glow": 0.22, "density": 0.85, "stars": 0.0010, "grain": 5, "axis": (0.10, 0.70), "seed": 501},
    "nebula-ember": {"top": "#0c0505", "bottom": "#1a0907", "palette": ["#3b0d0c", "#9a3412", "#f97316", "#fde68a"],
                     "core": "#fff7ed", "glow": 0.24, "density": 0.85, "stars": 0.0007, "grain": 5, "axis": (0.35, 0.40), "seed": 502},
    "nebula-rose": {"top": "#0d0510", "bottom": "#1c0a1d", "palette": ["#4a1042", "#be185d", "#f472b6", "#fbcfe8"],
                    "core": "#fdf2f8", "glow": 0.25, "density": 0.85, "stars": 0.0009, "grain": 5, "axis": (0.20, 0.55), "seed": 503},
    "nebula-deep": {"top": "#02030a", "bottom": "#050a1e", "palette": ["#0b1a4a", "#1d4ed8", "#60a5fa", "#c7d2fe"],
                    "core": "#e0e7ff", "glow": 0.25, "density": 0.80, "stars": 0.0013, "grain": 6, "axis": (0.30, 0.45), "seed": 504},
    "nebula-forest": {"top": "#040a06", "bottom": "#08140c", "palette": ["#123a24", "#15803d", "#84cc16", "#d9f99d"],
                      "core": "#f7fee7", "glow": 0.18, "density": 0.78, "stars": 0.0008, "grain": 5, "axis": (0.15, 0.65), "seed": 505},
    "nebula-mono": {"top": "#050506", "bottom": "#0d0d10", "palette": ["#1f1f25", "#3f3f46", "#a1a1aa", "#e4e4e7"],
                    "core": "#fafafa", "glow": 0.20, "density": 0.80, "stars": 0.0011, "grain": 6, "axis": (0.25, 0.50), "seed": 506},
}


def main():
    for size, path in [(512, SHARE / "nebulaos/logo.png"),
                       (256, SHARE / "icons/hicolor/256x256/apps/nebulaos.png"),
                       (64, SHARE / "nebulaos/logo-64.png"),
                       (180, SHARE / "plymouth/themes/nebulaos/logo.png")]:
        write_png(path, size, size, grid_rows(size, size, logo_pixel_fn(size)), alpha=True)

    write_png(SHARE / "plymouth/themes/nebulaos/bar.png", 280, 4,
              grid_rows(280, 4, lambda x, y: mix(VIOLET, PINK, x / 280) + (255,)), alpha=True)
    write_png(SHARE / "plymouth/themes/nebulaos/bar_bg.png", 280, 4,
              grid_rows(280, 4, lambda x, y: (255, 255, 255, 34)), alpha=True)
    write_png(SHARE / "grub/themes/nebulaos/background.png", 1920, 1080,
              nebula_wallpaper(1920, 1080, SPECS["gaming"], 11, logo=(960, 300, 200)))
    write_png(SHARE / "grub/themes/nebulaos/select_c.png", 8, 8,
              grid_rows(8, 8, lambda x, y: (139, 92, 246, 70)), alpha=True)
    write_png(ROOT / "branding/splash.png", 640, 480,
              nebula_wallpaper(640, 480, SPECS["gaming"], 12, logo=(320, 100, 120)))

    if "--gallery" in sys.argv:
        for name, spec in GALLERY.items():
            write_png(SHARE / "nebulaos/wallpapers" / f"{name}.png", 1920, 1080,
                      nebula_wallpaper(1920, 1080, spec, spec["seed"]))
        return
    only = [m for m in SPECS if m in sys.argv]
    if "--all" in sys.argv or only:
        for i, (mode, spec) in enumerate(SPECS.items()):
            if only and mode not in only:
                continue
            write_png(MODES / f"{mode}/wallpaper.png", 1920, 1080, nebula_wallpaper(1920, 1080, spec, spec.get("seed", 100 + i)))


if __name__ == "__main__":
    main()
