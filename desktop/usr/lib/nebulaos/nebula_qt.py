"""NebulaOS: shared Qt helpers so all NebulaOS apps look native in KDE Plasma.

Apps get the system style (Breeze + the mode's color scheme) automatically. This
module adds the common pieces: pages with grouped rows (like System Settings),
background tasks, running commands, fitting windows to the screen and translations.
"""
import shlex
import subprocess
import sys
import threading

sys.path.insert(0, "/usr/lib/nebulaos")
from nebula_i18n import _  # noqa: E402  (translations, shared with shell tools)

from PySide6.QtCore import QObject, Qt, Signal  # noqa: E402
from PySide6.QtGui import QFont, QGuiApplication, QIcon  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

__all__ = ["Meter", "Thumb", "Toggle", "tile", "_", "app", "fit", "run", "run_cmd", "in_terminal", "background", "Page", "Group", "QIcon", "Qt"]


def app(desktop_id, icon="nebulaos"):
    """QApplication tied to its .desktop file (correct icon and grouping in the dock)."""
    a = QApplication.instance() or QApplication(sys.argv)
    a.setDesktopFileName(desktop_id)
    # NebulaOS uses Papirus-Dark everywhere (locked in kdeglobals); set it explicitly so
    # our apps never fall back to missing-icon placeholders.
    import os
    paths = QIcon.themeSearchPaths()
    for extra in ("/usr/share/icons", os.path.expanduser("~/.local/share/icons")):
        if extra not in paths:
            paths.append(extra)
    QIcon.setThemeSearchPaths(paths)
    if os.path.isdir("/usr/share/icons/Papirus-Dark"):
        QIcon.setThemeName("Papirus-Dark")
    a.setWindowIcon(QIcon.fromTheme(icon))
    a.setApplicationDisplayName("")
    a.setStyleSheet(STYLE)
    _mode_shapes()
    return a


def radius(px):
    """Corner radius in the mode's shape: Steam is square, Ubuntu small, macOS soft."""
    return {"gaming": min(px, 2), "server": min(px, 6)}.get(MODE, px)


def _mode_shapes():
    """Every app's own style sheets get the mode's corner radius, so no app keeps a foreign shape."""
    import re
    from PySide6.QtWidgets import QWidget
    if getattr(QWidget, "_nebula_shaped", False) or MODE == "hacking":
        return
    orig = QWidget.setStyleSheet
    pat = re.compile(r"border-radius:\s*(\d+)px")

    def shaped(self, sheet):
        orig(self, pat.sub(lambda m: f"border-radius: {radius(int(m.group(1)))}px", sheet or ""))
    QWidget.setStyleSheet = shaped
    QWidget._nebula_shaped = True


# Look of NebulaOS apps — each mode imitates a real program family, not a template:
#   Gaming  — Steam client: square corners, uppercase headers, accent bar on the selected item.
#   Hacking — macOS Finder: grey sidebar, soft grey selection, plain lists with thin dividers.
#   Server  — Ubuntu Settings (Yaru): framed lists, small radius, orange only on the main button.
_COMMON = """
QScrollBar:vertical {{ width: 8px; background: transparent; margin: 2px; }}
QScrollBar::handle:vertical {{ background: palette(midlight); border-radius: 3px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QStatusBar {{ border: none; }}
QScrollArea {{ background: transparent; }}
QPushButton:disabled {{ color: palette(placeholder-text); }}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {{ border: 1px solid palette(highlight); }}
QProgressBar::chunk {{ background: palette(highlight); }}
"""

_STYLES = {
    "gaming": """
QFrame#group {{ background: palette(base); border: none; border-radius: 2px; }}
QFrame#card {{ background: palette(base); border: none; border-radius: 2px; }}
QFrame#card[active="true"] {{ border: 1px solid palette(highlight); }}
QLabel#badge {{ color: palette(highlighted-text); background: palette(highlight); border-radius: 2px; padding: 1px 6px; }}
QLabel#pagetitle {{ letter-spacing: 1px; }}
QLabel#grouptitle {{ color: palette(placeholder-text); letter-spacing: 1px; }}
QListWidget#nav {{ background: palette(base); border: none; padding: 8px 0; outline: none; }}
QListWidget#nav::item {{ min-height: 32px; padding-left: 12px; margin: 0; border: none; border-left: 3px solid transparent; }}
QListWidget#nav::item:hover {{ background: palette(alternate-base); }}
QListWidget#nav::item:selected {{ background: palette(alternate-base); color: palette(text); border-left: 3px solid palette(highlight); }}
QPushButton {{ padding: 6px 18px; border-radius: 2px; border: none; background: palette(midlight); }}
QPushButton:hover {{ background: palette(alternate-base); }}
QPushButton:default {{ background: palette(highlight); color: palette(highlighted-text); }}
QPushButton:checked {{ background: palette(highlight); color: palette(highlighted-text); }}
QPushButton:flat {{ background: transparent; }}
QLineEdit, QComboBox, QPlainTextEdit {{ border: 1px solid transparent; border-radius: 2px; padding: 5px 8px; background: palette(alternate-base); }}
QProgressBar {{ border: none; border-radius: 0; background: palette(alternate-base); height: 6px; text-align: center; }}
""",
    "hacking": """
QFrame#group {{ background: transparent; border: none; }}
QFrame#card {{ background: palette(base); border: 1px solid palette(midlight); border-radius: 8px; }}
QFrame#card[active="true"] {{ border: 2px solid palette(highlight); }}
QLabel#badge {{ color: palette(text); background: palette(midlight); border-radius: 4px; padding: 1px 6px; }}
QLabel#grouptitle {{ color: palette(placeholder-text); }}
QListWidget#nav {{ background: palette(alternate-base); border: none; border-right: 1px solid palette(midlight); padding: 8px 0; outline: none; }}
QListWidget#nav::item {{ min-height: 26px; padding-left: 6px; margin: 1px 8px; border-radius: 5px; border: none; }}
QListWidget#nav::item:selected {{ background: palette(midlight); color: palette(text); }}
QPushButton {{ padding: 3px 12px; border-radius: 5px; border: 1px solid palette(midlight); background: palette(button); }}
QPushButton:hover {{ background: palette(midlight); }}
QPushButton:default {{ background: palette(highlight); color: palette(highlighted-text); border: none; }}
QPushButton:checked {{ background: palette(midlight); border: none; }}
QPushButton:flat {{ background: transparent; border: none; }}
QLineEdit, QComboBox, QPlainTextEdit {{ border: 1px solid palette(midlight); border-radius: 5px; padding: 3px 7px; background: palette(base); }}
QProgressBar {{ border: none; border-radius: 3px; background: palette(midlight); height: 6px; text-align: center; }}
QProgressBar::chunk {{ border-radius: 3px; }}
""",
    "server": """
QFrame#group {{ background: palette(base); border: 1px solid palette(midlight); border-radius: 6px; }}
QFrame#card {{ background: palette(base); border: 1px solid palette(midlight); border-radius: 6px; }}
QFrame#card[active="true"] {{ border: 2px solid palette(highlight); }}
QLabel#badge {{ color: palette(highlighted-text); background: palette(highlight); border-radius: 3px; padding: 1px 6px; }}
QLabel#grouptitle {{ font-weight: bold; }}
QListWidget#nav {{ background: palette(window); border: none; border-right: 1px solid palette(midlight); padding: 6px 0; outline: none; }}
QListWidget#nav::item {{ min-height: 36px; padding-left: 8px; margin: 1px 6px; border-radius: 6px; border: none; }}
QListWidget#nav::item:hover {{ background: palette(alternate-base); }}
QListWidget#nav::item:selected {{ background: palette(midlight); color: palette(text); }}
QPushButton {{ padding: 5px 14px; border-radius: 5px; border: none; background: palette(midlight); }}
QPushButton:hover {{ background: palette(alternate-base); }}
QPushButton:default {{ background: palette(highlight); color: palette(highlighted-text); font-weight: bold; }}
QPushButton:checked {{ background: palette(highlight); color: palette(highlighted-text); }}
QPushButton:flat {{ background: transparent; }}
QLineEdit, QComboBox, QPlainTextEdit {{ border: 1px solid palette(midlight); border-radius: 5px; padding: 5px 8px; background: palette(base); }}
QProgressBar {{ border: none; border-radius: 3px; background: palette(midlight); height: 8px; text-align: center; }}
QProgressBar::chunk {{ border-radius: 3px; }}
""",
}


def current_mode():
    import os
    for path in (os.path.expanduser("~/.config/nebulaos/mode"), "/etc/nebulaos/default-mode"):
        try:
            m = open(path).read().strip()
            if m in ("gaming", "hacking", "server"):
                return m
        except OSError:
            pass
    return "gaming"


def build_style(mode=None):
    return (_STYLES[mode or current_mode()] + _COMMON).replace("{{", "{").replace("}}", "}")


MODE = current_mode()
STYLE = build_style()


def fit(win, width, height):
    """Resize so the window always fits the screen (max 80% wide, 78% tall), centered."""
    screen = QGuiApplication.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        width, height = min(width, int(geo.width() * 0.8)), min(height, int(geo.height() * 0.78))
        win.resize(width, height)
        win.move(geo.x() + (geo.width() - width) // 2, geo.y() + (geo.height() - height) // 2)
    else:
        win.resize(width, height)


def run(*args, timeout=60):
    """Run `nebula <args>` without a terminal → (code, output)."""
    return run_cmd("nebula", *args, timeout=timeout)


def run_cmd(*cmd, timeout=60):
    """Run any command without a terminal → (code, output)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def in_terminal(*args):
    """Open a command in the NebulaOS terminal (for sudo and long tasks)."""
    cmd = " ".join(shlex.quote(a) for a in args)
    done = shlex.quote(_("Done. Press Enter to close."))
    subprocess.Popen(["nebula", "term", "-e", "bash", "-c", f"{cmd}; echo; printf '%s' {done}; read _"])


class _Bridge(QObject):
    done = Signal(object)


def background(func, on_done):
    """Run func() in a thread; call on_done(result) back on the UI thread."""
    bridge = _Bridge()
    bridge.done.connect(on_done)
    background._keep = getattr(background, "_keep", [])
    background._keep.append(bridge)

    def work():
        try:
            result = func()
        except Exception as e:  # report instead of crashing the app
            result = e
        try:
            bridge.done.emit(result)
        except RuntimeError:      # the window that asked is already gone
            pass
    threading.Thread(target=work, daemon=True).start()


class Thumb(QWidget):
    """Picture that fills its box (cropped, never stretched) with rounded corners."""

    def __init__(self, path, height=110, radius=10):
        super().__init__()
        from PySide6.QtGui import QPixmap
        self.pix = QPixmap(str(path))
        self.radius = radius
        self.setFixedHeight(height)
        self.setMinimumWidth(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, _event):
        from PySide6.QtCore import QRectF
        from PySide6.QtGui import QPainter, QPainterPath
        if self.pix.isNull():
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.radius, self.radius)
        p.setClipPath(path)
        scaled = self.pix.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (scaled.width() - self.width()) // 2
        y = (scaled.height() - self.height()) // 2
        p.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
        p.end()


def tile(icon_name, color=None, size=26):
    """Sidebar/list icon: a plain monochrome glyph (accent in Hacking like Finder, text color elsewhere)."""
    from PySide6.QtGui import QColor, QPainter, QPixmap
    dpr = 2
    px = int(size * dpr * (0.72 if size <= 28 else 0.62))
    glyph = QIcon.fromTheme(icon_name + "-symbolic", QIcon.fromTheme(icon_name)).pixmap(px, px)
    pm = QPixmap(size * dpr, size * dpr)
    pm.fill(Qt.transparent)
    if not glyph.isNull():
        pal = QGuiApplication.palette()
        tint = pal.highlight().color() if MODE == "hacking" else pal.text().color()
        if MODE == "gaming":
            tint.setAlphaF(0.8)
        mono = QPixmap(glyph.size())
        mono.fill(Qt.transparent)
        g = QPainter(mono)
        g.drawPixmap(0, 0, glyph)
        g.setCompositionMode(QPainter.CompositionMode_SourceIn)
        g.fillRect(mono.rect(), tint)
        g.end()
        p = QPainter(pm)
        off = (size * dpr - px) // 2
        p.drawPixmap(off, off, mono)
        p.end()
    pm.setDevicePixelRatio(dpr)
    return QIcon(pm)


class Toggle(QCheckBox):
    """On/off switch (pill with a sliding knob) instead of a square checkbox."""

    def __init__(self, checked=False):
        super().__init__()
        self.setChecked(bool(checked))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(42, 24)

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, _e):
        from PySide6.QtCore import QRectF
        from PySide6.QtGui import QColor, QPainter
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        track = self.palette().highlight().color() if self.isChecked() else self.palette().midlight().color()
        if not self.isEnabled():
            track.setAlphaF(0.5)
        p.setPen(Qt.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(r, r.height() / 2, r.height() / 2)
        d = r.height() - 4
        x = r.right() - d - 2 if self.isChecked() else r.left() + 2
        p.setBrush(QColor("white"))
        p.drawEllipse(QRectF(x, r.top() + 2, d, d))
        p.end()


class Meter(QWidget):
    """Thin usage bar (memory, disk) in the accent color."""

    def __init__(self, fraction=0.0, height=8):
        super().__init__()
        self.fraction = max(0.0, min(1.0, fraction))
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set(self, fraction):
        self.fraction = max(0.0, min(1.0, fraction))
        self.update()

    def paintEvent(self, _e):
        from PySide6.QtCore import QRectF
        from PySide6.QtGui import QPainter
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect())
        rad = r.height() / 2
        p.setPen(Qt.NoPen)
        p.setBrush(self.palette().midlight())
        p.drawRoundedRect(r, rad, rad)
        if self.fraction > 0:
            color = self.palette().highlight().color()
            if self.fraction > 0.9:
                from PySide6.QtGui import QColor
                color = QColor("#f87171")
            p.setBrush(color)
            p.drawRoundedRect(QRectF(r.x(), r.y(), max(r.height(), r.width() * self.fraction), r.height()), rad, rad)
        p.end()


def _muted(label, scale=0.92):
    f = label.font()
    f.setPointSizeF(max(7.0, f.pointSizeF() * scale))
    label.setFont(f)
    label.setStyleSheet("color: palette(placeholder-text);")
    return label


class Group(QFrame):
    """A titled box of rows — the System Settings look."""

    def __init__(self, title="", description=""):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("group")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(2)
        if MODE == "hacking":
            outer.setContentsMargins(0, 4, 0, 4)
        self.title_label = None
        if title:
            text = _(title)
            t = QLabel(text.upper() if MODE == "gaming" else text)
            t.setObjectName("grouptitle")
            f = t.font()
            f.setBold(True)
            if MODE != "server":
                f.setPointSizeF(f.pointSizeF() * 0.85)
            t.setFont(f)
            outer.addWidget(t)
            self.title_label = t
        self.rows = outer

    def _row(self, title, subtitle, icon=None):
        row = QWidget()
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 8, 0, 8)
        if icon is not None:
            ic = QLabel()
            ic.setPixmap(icon.pixmap(32, 32))
            ic.setFixedWidth(40)
            lay.addWidget(ic, 0, Qt.AlignTop)
        text = QVBoxLayout()
        text.setSpacing(1)
        t = QLabel(_(title))
        t.setWordWrap(True)
        text.addWidget(t)
        if subtitle:
            s = _muted(QLabel(_(subtitle)))
            s.setWordWrap(True)
            text.addWidget(s)
        lay.addLayout(text, 1)
        if self.rows.count() > (1 if self.title_label else 0):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("color: palette(midlight);")
            self.rows.addWidget(line)
        self.rows.addWidget(row)
        return lay

    def row(self, title, subtitle="", icon=None):
        """A row with an optional app icon; add your own buttons to the returned layout."""
        return self._row(title, subtitle, icon)

    def action(self, title, subtitle, button, callback, primary=False):
        lay = self._row(title, subtitle)
        b = QPushButton(_(button))
        b.setDefault(primary)
        b.clicked.connect(lambda: callback())
        lay.addWidget(b, 0, Qt.AlignVCenter)
        return b

    def switch(self, title, subtitle, checked, callback):
        lay = self._row(title, subtitle)
        c = Toggle(checked)
        c.toggled.connect(callback)
        lay.addWidget(c, 0, Qt.AlignVCenter)
        return c

    def combo(self, title, items, index, callback, subtitle=""):
        lay = self._row(title, subtitle)
        c = QComboBox()
        c.addItems([_(i) for i in items])
        c.setCurrentIndex(max(0, index))
        c.currentIndexChanged.connect(callback)
        c.setMinimumWidth(180)
        lay.addWidget(c, 0, Qt.AlignVCenter)
        return c

    def widget(self, w):
        self.rows.addWidget(w)
        return w


class Page(QScrollArea):
    """Scrollable page: title, optional subtitle, then groups."""

    def __init__(self, title, subtitle=""):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        self.box = QVBoxLayout(body)
        self.box.setContentsMargins(24, 18, 24, 18)
        self.box.setSpacing(14)
        text = _(title)
        t = QLabel(text.upper() if MODE == "gaming" else text)
        t.setObjectName("pagetitle")
        f = QFont(t.font())
        f.setPointSizeF(f.pointSizeF() * {"gaming": 1.35, "hacking": 1.25, "server": 1.3}[MODE])
        f.setBold(True)
        t.setFont(f)
        self.box.addWidget(t)
        self.title = t  # subtitles are not shown: the page title says enough
        self.setWidget(body)
        self._tail = None

    def add(self, w):
        if self._tail:
            self.box.removeItem(self._tail)
        self.box.addWidget(w)
        self.box.addStretch(1)
        self._tail = self.box.itemAt(self.box.count() - 1)
        return w

    def group(self, title="", description=""):
        return self.add(Group(title, description))


def expanding(w):
    w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return w
