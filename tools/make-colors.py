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
    "Gaming": dict(
        title="NebulaOS Gaming", bg="#121022", base="#0d0b1a", alt="#161330", surface="#1d1838",
        header="#100e1e", text="#ece9ff", muted="#9a94c2", accent="#8b5cf6", accent2="#06b6d4",
        negative="#f43f5e", neutral="#f59e0b", positive="#22c55e",
        ansi=["#1d1838", "#f43f5e", "#22c55e", "#f59e0b", "#3b82f6", "#a855f7", "#06b6d4", "#d4d0f0",
              "#3a3360", "#fb7185", "#4ade80", "#fbbf24", "#60a5fa", "#c084fc", "#22d3ee", "#ffffff"]),
    "Hacking": dict(  # Catppuccin Mocha
        title="NebulaOS Hacking", bg="#1e1e2e", base="#181825", alt="#232334", surface="#313244",
        header="#181825", text="#cdd6f4", muted="#a6adc8", accent="#cba6f7", accent2="#f5c2e7",
        negative="#f38ba8", neutral="#f9e2af", positive="#a6e3a1",
        ansi=["#45475a", "#f38ba8", "#a6e3a1", "#f9e2af", "#89b4fa", "#f5c2e7", "#94e2d5", "#bac2de",
              "#585b70", "#f38ba8", "#a6e3a1", "#f9e2af", "#89b4fa", "#f5c2e7", "#94e2d5", "#a6adc8"]),
    "Server": dict(  # Ubuntu-like
        title="NebulaOS Server", bg="#2a0f22", base="#21091b", alt="#30122a", surface="#3d1733",
        header="#22091b", text="#f7f2f5", muted="#c7b3c0", accent="#e95420", accent2="#f6a03d",
        negative="#e01b24", neutral="#f6a03d", positive="#4e9a06",
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
