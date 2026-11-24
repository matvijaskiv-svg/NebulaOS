// Hacking — macOS-like: a slim top bar (menu, app menu, tray, clock) + a floating centered dock.
var bar = topBar(1.5);
addMenu(bar, "nebulaos");
bar.addWidget("org.kde.plasma.appmenu");
bar.addWidget("org.kde.plasma.panelspacer");
bar.addWidget("org.kde.plasma.systemtray");
addClock(bar, true);

var dock = dockPanel("bottom", 2.8, false, true);
safe(function () { dock.hiding = "dodgewindows"; });
addTasks(dock, launchers(["applications:org.wireshark.Wireshark.desktop", "applications:nebula-ai.desktop",
                          "applications:nebula-store.desktop"]), true);
dock.addWidget("org.kde.plasma.marginsseparator");
dock.addWidget("org.kde.plasma.trash");
