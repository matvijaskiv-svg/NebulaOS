#!/usr/bin/env python3
"""Генерирует цветовые схемы KDE и Konsole для трёх режимов NebulaOS.

    python tools/make-colors.py

Результат: desktop/usr/share/color-schemes/Nebula*.colors
           desktop/usr/share/konsole/Nebula*.colorscheme
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_KDE = ROOT / "desktop/usr/share/color-schemes"
OUT_KONSOLE = ROOT / "desktop/usr/share/konsole"

# bg — окна, base — поля и списки, alt — чередование строк, surface — кнопки/заголовки,
# text, muted, accent, accent2, ansi — 16 цветов терминала.
MODES = {
    "Gaming": dict(  # Garuda-like: neutral near-black, one strong red accent (no purple, no gradients)
        title="NebulaOS Gaming", bg="#151517", base="#0f0f11", alt="#1b1b1e", surface="#232327",
        header="#111113", text="#ececef", muted="#9b9ba3", accent="#e5484d", accent2="#ff8a3d",
        negative="#ff5c63", neutral="#f5a524", positive="#30a46c",
        ansi=["#232327", "#e5484d", "#30a46c", "#f5a524", "#3e8ef7", "#c25ec4", "#2bb3c0", "#d4d4d8",
              "#3a3a40", "#ff6b70", "#4cc38a", "#ffc53d", "#5aa2ff", "#d987db", "#45cfdb", "#ffffff"]),
    "Hacking": dict(  # macOS dark: graphite greys, system blue
        title="NebulaOS Hacking", bg="#1e1e1e", base="#191919", alt="#232323", surface="#2c2c2e",
        header="#1a1a1a", text="#e8e8ea", muted="#98989d", accent="#0a84ff", accent2="#64d2ff",
        negative="#ff453a", neutral="#ffd60a", positive="#32d74b",
        ansi=["#2c2c2e", "#ff453a", "#32d74b", "#ffd60a", "#0a84ff", "#bf5af2", "#64d2ff", "#d1d1d6",
              "#48484a", "#ff6961", "#5be37a", "#ffe066", "#409cff", "#da8fff", "#8ad9ff", "#ffffff"]),
    "Server": dict(  # Ubuntu Yaru dark: neutral greys, Ubuntu orange
        title="NebulaOS Server", bg="#2c2c2c", base="#242424", alt="#303030", surface="#3a3a3a",
        header="#262626", text="#f2f2f2", muted="#ababab", accent="#e95420", accent2="#f6a03d",
        negative="#c7162b", neutral="#f99b11", positive="#0e8420",
        ansi=["#2e3436", "#cc0000", "#4e9a06", "#c4a000", "#3465a4", "#75507b", "#06989a", "#d3d7cf",
              "#555753", "#ef2929", "#8ae234", "#fce94f", "#729fcf", "#ad7fa8", "#34e2e2", "#eeeeec"]),
}


def rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#" + "".join(f"{round(int(a[i:i+2], 16) * (1 - t) + int(b[i:i+2], 16) * t):02x}" for i in (0, 2, 4))


def group(name, bg, alt, fg, m):
    return f"""[Colors:{name}]
BackgroundAlternate={rgb(alt)}
BackgroundNormal={rgb(bg)}
DecorationFocus={rgb(m['accent'])}
DecorationHover={rgb(mix(m['accent'], m['text'], 0.25))}
ForegroundActive={rgb(m['accent2'])}
ForegroundInactive={rgb(m['muted'])}
ForegroundLink={rgb(m['accent'])}
ForegroundNegative={rgb(m['negative'])}
ForegroundNeutral={rgb(m['neutral'])}
ForegroundNormal={rgb(fg)}
ForegroundPositive={rgb(m['positive'])}
ForegroundVisited={rgb(mix(m['accent'], m['accent2'], 0.5))}

"""


def kde_scheme(key, m):
    s = "".join([
        group("Window", m["bg"], m["alt"], m["text"], m),
        group("View", m["base"], m["alt"], m["text"], m),
        group("Button", m["surface"], mix(m["surface"], m["text"], 0.06), m["text"], m),
        group("Selection", m["accent"], mix(m["accent"], m["bg"], 0.2), "#ffffff", m),
        group("Tooltip", m["surface"], m["alt"], m["text"], m),
        group("Complementary", m["header"], m["alt"], m["text"], m),
        group("Header", m["header"], m["alt"], m["text"], m),
        group("Header][Inactive", m["bg"], m["alt"], m["muted"], m),
    ])
    s += f"""[General]
ColorScheme=Nebula{key}
Name={m['title']}
shadeSortColumn=true
AccentColor={rgb(m['accent'])}

[KDE]
contrast=4

[WM]
activeBackground={rgb(m['header'])}
activeBlend={rgb(m['text'])}
activeForeground={rgb(m['text'])}
inactiveBackground={rgb(m['bg'])}
inactiveBlend={rgb(m['muted'])}
inactiveForeground={rgb(m['muted'])}
"""
    return s


def konsole_scheme(key, m):
    names = ["Color0", "Color1", "Color2", "Color3", "Color4", "Color5", "Color6", "Color7"]
    out = [f"[General]\nDescription={m['title']}\nOpacity=1\nBlur=false\n\n"
           f"[Background]\nColor={rgb(m['base'])}\n\n[BackgroundIntense]\nColor={rgb(m['base'])}\n\n"
           f"[Foreground]\nColor={rgb(m['text'])}\n\n[ForegroundIntense]\nColor={rgb(m['text'])}\n\n"]
    for i, n in enumerate(names):
        out.append(f"[{n}]\nColor={rgb(m['ansi'][i])}\n\n[{n}Intense]\nColor={rgb(m['ansi'][i + 8])}\n\n")
    return "".join(out)


OUT_KDE.mkdir(parents=True, exist_ok=True)
OUT_KONSOLE.mkdir(parents=True, exist_ok=True)
for key, m in MODES.items():
    (OUT_KDE / f"Nebula{key}.colors").write_text(kde_scheme(key, m), encoding="utf-8", newline="\n")
    (OUT_KONSOLE / f"Nebula{key}.colorscheme").write_text(konsole_scheme(key, m), encoding="utf-8", newline="\n")
    print("Nebula" + key)
