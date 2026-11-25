// NebulaOS panels: shared helpers. Each mode file is appended after this one.
// DOCK is filled in by nebula with the dock position (bottom / left / right) chosen by the user.
var DOCK = "__DOCK__";
function safe(f) { try { f(); } catch (e) { print("nebula: " + e); } }
safe(function () { locked = false; });
// Start clean: remove every panel, then build the mode's own layout.
panels().forEach(function (p) { safe(function () { p.remove(); }); });
var BASE = [
    "applications:nebula-hub.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:firefox.desktop",
    "applications:nebula-chat.desktop",
    "applications:org.kde.konsole.desktop"
];
function launchers(extra) { return BASE.concat(extra); }
function addTasks(panel, list, grouped) {
    var t = panel.addWidget("org.kde.plasma.icontasks");
    t.currentConfigGroup = ["General"];
    t.writeConfig("launchers", list);
    t.writeConfig("showOnlyCurrentDesktop", false);
    t.writeConfig("groupingStrategy", grouped ? 1 : 0);
    return t;
}
function addMenu(panel, icon) {
    var m = panel.addWidget("org.kde.plasma.kickoff");
    m.currentConfigGroup = ["General"];
    m.writeConfig("icon", icon || "nebulaos");
    m.writeConfig("favoritesPortedToKAstats", true);
    return m;
}
function addClock(panel, date) {
    var c = panel.addWidget("org.kde.plasma.digitalclock");
    c.currentConfigGroup = ["Appearance"];
    c.writeConfig("showDate", date);
    c.writeConfig("dateFormat", "shortDate");
    return c;
}
// opacity: "adaptive" (glass), "opaque" or "translucent"
function look(p, opacity) { safe(function () { p.opacity = opacity; }); }
function topBar(height) {
    var p = new Panel;
    p.location = "top";
    p.height = Math.round(gridUnit * height);
    safe(function () { p.floating = false; });
    return p;
}
function dockPanel(defaultPos, size, fill, floating) {
    var p = new Panel;
    p.location = DOCK === "default" || DOCK === "" ? defaultPos : DOCK;
    p.height = Math.round(gridUnit * size);
    p.lengthMode = fill ? "fill" : "fit";
    safe(function () { p.alignment = "center"; });
    safe(function () { p.floating = floating; });
    return p;
}
