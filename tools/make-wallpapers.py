#!/usr/bin/env python3
"""Calm mode wallpapers (soft waves of light on a dark background, macOS-style).

    QT_QPA_PLATFORM=offscreen python tools/make-wallpapers.py   (needs PySide6)

Hacking — graphite with deep blue waves; Gaming — near-black with red/orange light;
Server — neutral grey with warm Ubuntu orange.
"""
import random
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QRadialGradient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "desktop/usr/share/nebulaos/modes"
W, H = 2560, 1440
SW, SH = 480, 270          # painted small, scaled up smoothly = soft light

SPECS = {
    "hacking": dict(bg="#0e0f12", glows=[("#0a4fb0", 0.78, 0.95, 0.70, 0.55), ("#0a84ff", 0.30, 1.10, 0.55, 0.28)],
                    waves=[("#0a84ff", "#5ac8fa", 0.55, 0.35), ("#1c3f8c", "#0a84ff", 0.75, 0.25),
                           ("#64d2ff", "#0a84ff", 0.95, 0.18)]),
    "gaming": dict(bg="#0b0b0d", glows=[("#a3121c", 0.15, 1.05, 0.75, 0.55), ("#ff8a3d", 0.05, 1.15, 0.35, 0.35)],
                   waves=[("#e5484d", "#ff8a3d", 0.62, 0.38), ("#7a0f16", "#e5484d", 0.80, 0.28),
                          ("#ff8a3d", "#ffc53d", 0.97, 0.16)]),
    "server": dict(bg="#1c1c1c", glows=[("#c5401a", 0.85, 1.05, 0.70, 0.45), ("#f6a03d", 0.95, 1.15, 0.35, 0.30)],
                   waves=[("#e95420", "#f6a03d", 0.60, 0.33), ("#5a2a17", "#e95420", 0.78, 0.25),
                          ("#3a3a3a", "#6a6a6a", 0.92, 0.20)]),
}


def wave(p, c1, c2, base_y, alpha, rnd):
    """A silky layer: the area under a smooth curve, bright at its edge and fading downwards."""
    y = base_y * SH
    amp = SH * rnd.uniform(0.10, 0.18)
    k = rnd.uniform(0.25, 0.45)
    path = QPainterPath()
    path.moveTo(-60, y + amp * 0.4)
    path.cubicTo(SW * k, y - amp * 1.8, SW * (k + 0.35), y + amp * 1.5, SW + 60, y - amp * 0.8)
    path.lineTo(SW + 60, SH + 60)
    path.lineTo(-60, SH + 60)
    path.closeSubpath()
    top = y - amp * 1.2
    g = QLinearGradient(0, top, 0, top + SH * 0.55)
    a, b, clear = QColor(c1), QColor(c2), QColor(c2)
    a.setAlphaF(alpha)
    b.setAlphaF(alpha * 0.35)
    clear.setAlphaF(0)
    g.setColorAt(0.0, a)
    g.setColorAt(0.35, b)
    g.setColorAt(1.0, clear)
    p.fillPath(path, QBrush(g))
    # thin light along the edge
    edge = QPainterPath()
    edge.moveTo(-60, y + amp * 0.4)
    edge.cubicTo(SW * k, y - amp * 1.8, SW * (k + 0.35), y + amp * 1.5, SW + 60, y - amp * 0.8)
    from PySide6.QtGui import QPen
    hl = QColor(c2)
    hl.setAlphaF(min(1.0, alpha * 0.9))
    pen = QPen(hl, 1.2)
    p.strokePath(edge, pen)


def make(mode, spec, seed):
    rnd = random.Random(seed)
    small = QImage(SW, SH, QImage.Format_ARGB32)
    small.fill(QColor(spec["bg"]))
    p = QPainter(small)
    p.setRenderHint(QPainter.Antialiasing)
    for color, x, y, r, alpha in spec["glows"]:
        g = QRadialGradient(QPointF(x * SW, y * SH), r * SW)
        c = QColor(color)
        c.setAlphaF(alpha)
        g.setColorAt(0, c)
        c2 = QColor(color)
        c2.setAlphaF(0)
        g.setColorAt(1, c2)
        p.fillRect(small.rect(), QBrush(g))
    for c1, c2, y, alpha in spec["waves"]:
        wave(p, c1, c2, y, alpha, rnd)
    # vignette
    v = QRadialGradient(QPointF(SW / 2, SH / 2), SW * 0.75)
    v.setColorAt(0.55, QColor(0, 0, 0, 0))
    v.setColorAt(1, QColor(0, 0, 0, 150))
    p.fillRect(small.rect(), QBrush(v))
    p.end()
    # two smooth upscales give soft, banding-free light
    mid = small.scaled(SW * 2, SH * 2, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    big = mid.scaled(W, H, Qt.IgnoreAspectRatio, Qt.SmoothTransformation).convertToFormat(QImage.Format_RGB32)
    out = OUT / mode / "wallpaper.png"
    big.save(str(out), "PNG", 9)
    print("wrote", out, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    app = QGuiApplication([])
    for i, (m, s) in enumerate(SPECS.items()):
        make(m, s, 7 + i)
