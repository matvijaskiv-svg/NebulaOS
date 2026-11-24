// NebulaOS layout: a slim top bar (menu, window menu, tray, clock) and a centered dock.
// Panels and the desktop are locked; NebulaOS Kiosk settings keep them locked.

var wallpaper = "file:///usr/share/nebulaos/modes/gaming/wallpaper.png";

// ---------- Desktop ----------
desktopsArray = desktopsForActivity(currentActivity());
for (var i = 0; i < desktopsArray.length; i++) {
    var d = desktopsArray[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", wallpaper);
    d.currentConfigGroup = [];
}

// ---------- Top bar ----------
var top = new Panel;
top.location = "top";
top.height = Math.round(gridUnit * 1.5);
top.floating = false;

var menu = top.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "nebulaos");
menu.writeConfig("favoritesPortedToKAstats", true);

top.addWidget("org.kde.plasma.appmenu");
top.addWidget("org.kde.plasma.panelspacer");
var tray = top.addWidget("org.kde.plasma.systemtray");
var clock = top.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateFormat", "shortDate");

// ---------- Dock ----------
var dock = new Panel;
dock.location = "bottom";
dock.height = Math.round(gridUnit * 2.7);
dock.lengthMode = "fit";
dock.alignment = "center";
dock.floating = true;
dock.hiding = "dodgewindows";

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:nebula-hub.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:firefox.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:org.kde.kate.desktop",
    "applications:libreoffice-startcenter.desktop",
    "applications:org.kde.elisa.desktop",
    "applications:nebula-store.desktop",
    "applications:nebula-ai.desktop"
]);
tasks.writeConfig("showOnlyCurrentDesktop", false);
tasks.writeConfig("groupingStrategy", 1);
dock.addWidget("org.kde.plasma.marginsseparator");
dock.addWidget("org.kde.plasma.trash");

// ---------- Lock everything ----------
top.locked = true;
dock.locked = true;
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].locked = true;
}
