// Gaming — Garuda-like: one floating full-width taskbar at the bottom, everything in it,
// big icons, live CPU/GPU load next to the tray. No top bar: more room for games.
var bar = dockPanel("bottom", 2.6, true, true);
look(bar, "opaque");                       // solid floating bar with rounded ends
addMenu(bar, "nebulaos");
bar.addWidget("org.kde.plasma.marginsseparator");
addTasks(bar, launchers(["applications:nebula-games.desktop", "applications:com.valvesoftware.Steam.desktop", "applications:steam.desktop", "applications:net.lutris.Lutris.desktop",
                         "applications:discord.desktop", "applications:nebula-store.desktop"]), true);
bar.addWidget("org.kde.plasma.panelspacer");
safe(function () {
    var cpu = bar.addWidget("org.kde.plasma.systemmonitor.cpu");
});
bar.addWidget("org.kde.plasma.systemtray");
addClock(bar, true);
bar.addWidget("org.kde.plasma.showdesktop");

// Lock the layout again: users cannot edit panels (NebulaOS can, through scripting).
safe(function () { locked = true; });
