// Server — Ubuntu-like: a top bar with the clock in the middle + a vertical dock on the left
// with the app grid at the bottom.
var bar = topBar(1.4);
look(bar, "opaque");                       // flat solid bar, square edges
var act = bar.addWidget("org.kde.plasma.kickoff");
act.currentConfigGroup = ["General"];
act.writeConfig("icon", "nebulaos");
bar.addWidget("org.kde.plasma.panelspacer");
addClock(bar, true);
bar.addWidget("org.kde.plasma.panelspacer");
addControlButton(bar);
bar.addWidget("org.kde.plasma.systemtray");

var dock = dockPanel("left", 2.7, true, false);
look(dock, "opaque");                      // attached full-height dock
addTasks(dock, launchers(["applications:nebula-serverpanel.desktop", "applications:org.kde.plasma-systemmonitor.desktop", "applications:nebula-ai.desktop"]), false);
dock.addWidget("org.kde.plasma.panelspacer");
dock.addWidget("org.kde.plasma.trash");
var grid = dock.addWidget("org.kde.plasma.kickoff");
grid.currentConfigGroup = ["General"];
grid.writeConfig("icon", "view-app-grid-symbolic");

desktopWidgets([["org.kde.plasma.systemmonitor.cpu", 180], ["org.kde.plasma.systemmonitor.memory", 180], ["org.kde.plasma.systemmonitor.diskusage", 180], ["org.kde.plasma.systemmonitor.net", 160]]);

// Lock the layout again: users cannot edit panels (NebulaOS can, through scripting).
panels().forEach(function (p) { safe(function () { p.locked = true; }); });
// Lock the whole layout (panels and widgets). Files can still be dropped on the desktop
// and added with “Add to desktop” — that is file handling, not editing.
safe(function () { locked = true; });
