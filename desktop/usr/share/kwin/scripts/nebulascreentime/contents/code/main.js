// Report the active window's app to the NebulaOS screen time service.
function report(w) {
    callDBus("org.nebulaos.ScreenTime", "/ScreenTime", "org.nebulaos.ScreenTime", "Active",
             w ? String(w.resourceClass || "") : "");
}
workspace.windowActivated.connect(report);
report(workspace.activeWindow);
