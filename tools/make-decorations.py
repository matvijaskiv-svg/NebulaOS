#!/usr/bin/env python3
"""Window decorations (KWin Aurorae themes), one per NebulaOS mode.

    python tools/make-decorations.py      → desktop/usr/share/aurorae/themes/Nebula{Mac,Neon,Yaru}

NebulaMac  (Hacking) — macOS: traffic lights on the left, centered title, rounded top corners.
NebulaNeon (Gaming)  — Garuda dr460nized: dark bar, neon accent line, glowing symbols on the right.
NebulaYaru (Server)  — Ubuntu Yaru: grey round buttons on the right, orange close, centered title.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "desktop/usr/share/aurorae/themes"


BOX = '<rect width="16" height="16" fill="#000" fill-opacity="0"/>'   # fixes each state's size to 16×16


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f'{body}\n</svg>\n')


def frame(bar, border, radius, accent_line=None, inactive_bar=None):
    """decoration.svg: a frame with rounded top corners. The bar color fills the title area."""
    r = radius
    def block(prefix, color):
        line = (f'<rect x="0" y="{r - 2}" width="1" height="2" fill="{accent_line}"/>' if accent_line else "")
        parts = [
            # corners
            f'<path id="{prefix}-topleft" d="M0,{r} A{r},{r} 0 0 1 {r},0 L{r},{r} Z" fill="{color}"/>',
            f'<path id="{prefix}-topright" transform="translate({r + 4},0)" d="M0,0 A{r},{r} 0 0 1 {r},{r} L0,{r} Z" fill="{color}"/>',
            f'<rect id="{prefix}-top" x="{2 * r + 8}" y="0" width="4" height="{r}" fill="{color}"/>',
            f'<rect id="{prefix}-left" x="0" y="{r + 4}" width="1" height="4" fill="{border}"/>',
            f'<rect id="{prefix}-right" x="4" y="{r + 4}" width="1" height="4" fill="{border}"/>',
            f'<rect id="{prefix}-center" x="8" y="{r + 4}" width="4" height="4" fill="{color}"/>',
            f'<rect id="{prefix}-bottomleft" x="0" y="{r + 12}" width="1" height="1" fill="{border}"/>',
            f'<rect id="{prefix}-bottom" x="4" y="{r + 12}" width="4" height="1" fill="{border}"/>',
            f'<rect id="{prefix}-bottomright" x="10" y="{r + 12}" width="1" height="1" fill="{border}"/>',
        ]
        return "\n".join(parts)
    body = block("decoration", bar) + "\n" + block("decoration-inactive", inactive_bar or bar)
    if accent_line:   # a thin neon line under the title bar (drawn by the "top" piece's gradient)
        body = body.replace(f'<rect id="decoration-top" x="{2 * r + 8}" y="0" width="4" height="{r}" fill="{bar}"/>',
                            f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
                            f'<stop offset="0" stop-color="{bar}"/><stop offset="0.85" stop-color="{bar}"/>'
                            f'<stop offset="1" stop-color="{accent_line}"/></linearGradient></defs>'
                            f'<rect id="decoration-top" x="{2 * r + 8}" y="0" width="4" height="{r}" fill="{bar}"/>')
    return svg(60, 60, body)


GLYPH = {
    "close": "M5,5 L11,11 M11,5 L5,11",
    "minimize": "M4.5,8 L11.5,8",
    "maximize": "M4.5,8 L11.5,8 M8,4.5 L8,11.5",
    "restore": "M5,6 L10,11 M6,11 L10,11 L10,7",
}


def mac_button(kind):
    colors = {"close": "#ff5f57", "minimize": "#febc2e", "maximize": "#28c840", "restore": "#28c840"}
    c = colors[kind]
    states = []
    for i, state in enumerate(["active", "inactive", "hover", "pressed", "deactivated"]):
        fill = {"inactive": "#4b4b57", "deactivated": "#3a3a44"}.get(state, c)
        glyph = (f'<path d="{GLYPH[kind]}" stroke="#4d0000" stroke-opacity="0.7" stroke-width="1.4" '
                 f'stroke-linecap="round" fill="none"/>' if state in ("hover", "pressed") else "")
        dim = '<circle cx="8" cy="8" r="6" fill="#000" fill-opacity="0.2"/>' if state == "pressed" else ""
        states.append(f'<g id="{state}" transform="translate({i * 16},0)">{BOX}<circle cx="8" cy="8" r="6" fill="{fill}"/>'
                      f'{dim}{glyph}</g>')
    return svg(80, 16, "\n".join(states))


def neon_button(kind):
    colors = {"close": "#ff2e97", "minimize": "#00e5ff", "maximize": "#00e5ff", "restore": "#00e5ff"}
    c = colors[kind]
    states = []
    for i, state in enumerate(["active", "inactive", "hover", "pressed", "deactivated"]):
        stroke = {"inactive": "#6f6a8a", "deactivated": "#3c3850"}.get(state, c)
        halo = (f'<circle cx="8" cy="8" r="7.5" fill="{c}" fill-opacity="{0.18 if state == "hover" else 0.32}"/>'
                if state in ("hover", "pressed") else "")
        states.append(f'<g id="{state}" transform="translate({i * 16},0)">{BOX}{halo}'
                      f'<path d="{GLYPH[kind]}" stroke="{stroke}" stroke-width="1.8" stroke-linecap="round" fill="none"/></g>')
    return svg(80, 16, "\n".join(states))


def yaru_button(kind):
    states = []
    for i, state in enumerate(["active", "inactive", "hover", "pressed", "deactivated"]):
        if kind == "close":
            fill = {"inactive": "#4a4a4a", "hover": "#f26b3a", "pressed": "#c7431a", "deactivated": "#3a3a3a"}.get(state, "#e95420")
        else:
            fill = {"inactive": "#3c3c3c", "hover": "#5a5a5a", "pressed": "#6a6a6a", "deactivated": "#333333"}.get(state, "#4a4a4a")
        stroke = "#9a9a9a" if state in ("inactive", "deactivated") else "#ffffff"
        states.append(f'<g id="{state}" transform="translate({i * 16},0)">{BOX}<circle cx="8" cy="8" r="7.5" fill="{fill}"/>'
                      f'<path d="{GLYPH[kind]}" transform="translate(8,8) scale(0.8) translate(-8,-8)" stroke="{stroke}" '
                      f'stroke-width="1.6" stroke-linecap="round" fill="none"/></g>')
    return svg(80, 16, "\n".join(states))


THEMES = {
    "NebulaMac": dict(title="Nebula Mac", bar="#1f1f2b", inactive="#191923", border="#33334a",
                      radius=10, line=None, text="#d6d8ee", itext="#7f8299", align="AlignHCenter",
                      button=mac_button, size=16, spacing=8),
    "NebulaNeon": dict(title="Nebula Neon", bar="#0d0b17", inactive="#0b0a12", border="#2a1f4a",
                       radius=8, line="#7b2ff7", text="#eef0ff", itext="#7d7a98", align="AlignLeft",
                       button=neon_button, size=16, spacing=10),
    "NebulaYaru": dict(title="Nebula Yaru", bar="#2c2c2c", inactive="#242424", border="#3d3d3d",
                       radius=10, line=None, text="#ffffff", itext="#9a9a9a", align="AlignHCenter",
                       button=yaru_button, size=16, spacing=8),
}

for name, t in THEMES.items():
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "decoration.svg").write_text(frame(t["bar"], t["border"], t["radius"], t["line"], t["inactive"]))
    for kind in ("close", "minimize", "maximize", "restore"):
        (d / f"{kind}.svg").write_text(t["button"](kind))
    (d / "metadata.desktop").write_text(
        f"[Desktop Entry]\nName={t['title']}\nComment=NebulaOS window decoration\n"
        f"X-KDE-PluginInfo-Author=NebulaOS\nX-KDE-PluginInfo-Name={name}\n"
        f"X-KDE-PluginInfo-Version=1.0\nX-KDE-PluginInfo-License=GPL\n")
    (d / f"{name}rc").write_text(
        "[General]\n"
        f"ActiveTextColor={t['text']}\nInactiveTextColor={t['itext']}\n"
        f"TitleAlignment={t['align']}\nTitleVerticalAlignment=AlignVCenter\n"
        "Animation=150\nShadow=true\n\n"
        "[Layout]\n"
        "BorderLeft=1\nBorderRight=1\nBorderBottom=1\n"
        "TitleEdgeTop=5\nTitleEdgeBottom=5\nTitleEdgeLeft=10\nTitleEdgeRight=10\n"
        "TitleBorderLeft=8\nTitleBorderRight=8\nTitleHeight=22\n"
        f"ButtonWidth={t['size']}\nButtonHeight={t['size']}\nButtonSpacing={t['spacing']}\nButtonMarginTop=8\n"
        "ExplicitButtonSpacer=10\n"
        "PaddingTop=0\nPaddingBottom=0\nPaddingLeft=0\nPaddingRight=0\n")
    print("wrote", d)
