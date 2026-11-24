"""NebulaOS: translations for the GTK apps.

`_()` translates a string. `install()` patches the GTK/libadwaita widgets used by
NebulaOS so that labels, titles and subtitles passed as plain English strings are
translated automatically. Catalogs: /usr/share/nebulaos/i18n/<lang>.tsv.
"""
import os
from pathlib import Path

I18N = Path("/usr/share/nebulaos/i18n")
LANGUAGES = [("en", "English"), ("ru", "Русский"), ("uk", "Українська"), ("it", "Italiano")]
_TR = {}


def current():
    lang = os.environ.get("NEBULA_LANG", "")
    if not lang:
        conf = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "nebulaos/lang"
        try:
            lang = conf.read_text(encoding="utf-8").strip()
        except OSError:
            lang = ""
    lang = lang or os.environ.get("LANG", "en")[:2]
    return lang if lang in {code for code, _n in LANGUAGES} else "en"


def _unescape(s):
    return s.replace("\\n", "\n").replace("\\t", "\t")


def load():
    _TR.clear()
    try:
        for line in (I18N / f"{current()}.tsv").read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#") and "\t" in line:
                src, dst = line.split("\t", 1)
                if dst:
                    _TR[_unescape(src)] = _unescape(dst)
    except OSError:
        pass


def _(text):
    return _TR.get(text, text) if isinstance(text, str) else text


TEXT_PROPS = ("label", "title", "subtitle", "placeholder_text", "tooltip_text",
              "description", "heading", "body", "text", "name")


def install(Gtk, Adw):
    """Translate English strings given to widgets, without wrapping every call site."""
    def wrap_init(cls):
        orig = cls.__init__

        def __init__(self, *args, **kwargs):
            for key in TEXT_PROPS:
                if isinstance(kwargs.get(key), str):
                    kwargs[key] = _(kwargs[key])
            orig(self, *args, **kwargs)
        cls.__init__ = __init__

    def wrap_method(cls, name, arg=0):
        orig = getattr(cls, name, None)
        if orig is None:
            return

        def method(self, *args, **kwargs):
            args = list(args)
            if len(args) > arg and isinstance(args[arg], str):
                args[arg] = _(args[arg])
            return orig(self, *args, **kwargs)
        setattr(cls, name, method)

    for cls in (Gtk.Label, Gtk.Button, Gtk.ToggleButton, Gtk.CheckButton, Gtk.Entry, Gtk.SearchEntry,
                Gtk.FileDialog, Gtk.FileFilter, Adw.ActionRow, Adw.EntryRow, Adw.PasswordEntryRow,
                Adw.ComboRow, Adw.PreferencesGroup, Adw.ApplicationWindow, Adw.ButtonContent,
                Adw.Toast, Adw.MessageDialog):
        wrap_init(cls)
    for cls, name, arg in ((Gtk.Label, "set_text", 0), (Gtk.Label, "set_label", 0), (Gtk.Button, "set_label", 0),
                           (Adw.PreferencesRow, "set_title", 0), (Adw.ActionRow, "set_subtitle", 0),
                           (Gtk.FileFilter, "set_name", 0), (Gtk.Stack, "add_titled", 2),
                           (Adw.MessageDialog, "add_response", 1), (Gtk.Entry, "set_placeholder_text", 0)):
        wrap_method(cls, name, arg)
    orig_new = Gtk.StringList.new
    Gtk.StringList.new = staticmethod(lambda items: orig_new([_(i) for i in items]))


load()


def fit(win, width, height):
    """Default window size that always fits the screen (max 80% wide, 75% tall)."""
    try:
        from gi.repository import Gdk
        monitors = Gdk.Display.get_default().get_monitors()
        geo = monitors.get_item(0).get_geometry()
        width, height = min(width, int(geo.width * 0.8)), min(height, int(geo.height * 0.75))
    except Exception:  # no display info yet — keep the requested size
        pass
    win.set_default_size(width, height)
