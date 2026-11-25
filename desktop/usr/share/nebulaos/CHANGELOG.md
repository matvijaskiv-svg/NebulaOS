# NebulaOS changelog

## 0.7.8
- New look without purple: graphite and blue for Hacking, black and red for Gaming, grey and orange for Server; calm new wallpapers

## 0.7.7
- New apps: Game Center, Toolkit and Server Panel; each mode styles the NebulaOS apps its own way

## 0.7.6
- Each mode has its own window style, buttons, icons, cursor and font: macOS for Hacking, Garuda neon for Gaming, Ubuntu for Server

## 0.7.5
- New macOS-style login screen, clean startup sound, plain app names and texts

## 0.7.4
- Nebula Store installs apps right in the window with a progress bar; 100+ apps

## 0.7.3
- Fixed: wallpaper and panels change again, keyboard layouts are kept, languages work, Nebula Chat reconnects, the assistant knows NebulaOS

## 0.7.2
- Panels change shape and style with the mode: glass macOS dock, solid Garuda taskbar, Ubuntu side dock

## 0.7.1
- Each mode now has its own panels: Hacking like macOS, Gaming like Garuda, Server like Ubuntu

## 0.7.0
- Fix: the update address is now part of the package, so updating no longer removes it.
- Updates and the signed channel come from the public repository NebulaOS-updates;
  the source repository can be private (tools/push-updates.sh).

## 0.6.1
- First release of the NebulaOS update channel

## 0.6.0
- Nebula Chat 2: groups with owner/moderators/mute/kick/pin, photos and files, avatars and status,
  "typing…", delivered/seen ticks, a feed of posts with likes, polls, official community groups.
- Signed channel: news, polls, ban list, wallpaper of the week and update holds are trusted only
  with the maintainer signature (Ed25519). The admin panel is no longer part of the system.
- Nebula Chat: private P2P messenger between NebulaOS users (Tox, end-to-end encrypted, no server),
  with a built-in "Message NebulaOS Support" button.
- NebulaOS news: announcements and new-version notices from the NebulaOS GitHub channel.
- Updates come from GitHub (release "repo"); `tools/release.sh` publishes one in a single command.
- Design lock for real: KDE appearance pages (themes, colors, icons, fonts, window decorations)
  are not installed at all and stay out after updates. Only wallpaper and dock can change.
- System check (`nebula doctor`): internet, DNS, drivers, sound, disk, services, with a fix for each.
- Clean up (`nebula clean`): package cache, unused packages, old logs, thumbnails; shows freed space.
- Battery care: charge only to 80% on laptops that support it (Settings → Power).
- Daily notifications: updates available, disk almost full.
- Dolphin: right-click a file → "Ask Nebula AI about this file".
- Shortcuts fixed for Plasma 6 (Super+M, Super+H, Super+A…); new: Super+Shift+S area screenshot,
  Super+Shift+R screen recording, Super+/ list of all shortcuts.
- Each Settings section has its own icon color.
- One settings app: KDE System Settings is hidden; detailed KDE modules open from NebulaOS Settings.
- Each mode has its own panel: Hacking — Mac-like floating dock, Gaming — full-width bottom panel
  like Garuda, Server — vertical dock on the left like Ubuntu.
- Boot menu entry "Install NebulaOS" that opens the installer right away.
- Wallpaper gallery: 9 nebula wallpapers.

## 0.5.0
- New desktop: KDE Plasma instead of Hyprland — every window has close/minimize buttons,
  a real apps menu, a slim top bar with the app menu, tray and clock, a centered floating dock.
- Three modes now recolor the whole desktop (KDE color schemes NebulaGaming, NebulaHacking
  — Catppuccin Mocha — and NebulaServer), the terminal, the accent color and the wallpaper.
- The look is locked (KDE Kiosk): theme, colors, icons, fonts, window style and panels
  can't be changed; wallpaper and mode can.
- "NebulaOS Settings" (Super+H) with a gear icon; About shows NebulaOS.
- Shortcuts: Super — apps menu, Super+Enter — terminal, Super+Q — close window,
  Super+M — mode, Super+A — assistant, Super+L — lock.
- NebulaOS apps rebuilt natively for Plasma (Qt): Settings with mode cards and wallpaper previews,
  Store with real app icons in a card grid, Welcome tour, AI assistant chat, graphical installer.
  Every window fits the screen; spacing, fonts and alignment polished screen by screen.
- Boot splash with the NebulaOS logo, top-left hot corner opens the overview, Magic Lamp minimize,
  soft startup sound, fastfetch with the NebulaOS logo in the terminal.
- AI assistant works out of the box: the qwen2.5:1.5b model ships on the ISO.
- Printers (CUPS + KDE printer settings); the welcome tour offers the NVIDIA driver when it finds one.

## 0.4.0
- Languages: English, Русский, Українська, Italiano — in the welcome tour, Nebula Hub and the installer.
  The keyboard layout follows the language; Alt+Shift switches layouts.
- Polished look: new Orbit logo with soft shading and a crisp ring, layered nebula wallpapers
  with stars and fine grain, calmer bar and dock, Spotlight-style launcher, refined lock screen,
  notifications in the mode's colors, smoother window animations.
- Boot menu: "Safe graphics" entry for VMs and GPUs that hang on a black screen.
- Fixed: the desktop did not start (Hyprland 0.57 emergency mode) — NebulaOS now generates the new
  Lua config (hyprland.lua); all three modes are verified with Hyprland 0.57.2.
- AI assistant can now act on the system: it proposes commands, you press Run, it sees the output
  and continues. sudo and risky commands open in a terminal; nothing runs without your confirmation.
- Fixed: autologin session name, login-screen background path, invisible cursor in VMs.

## 0.3.0
- English by default; the system language (English or Russian) is chosen in the installer.
- Nebula Center (Super+C, click the clock): Wi-Fi, Bluetooth, Do Not Disturb, night light, volume, brightness,
  power profiles, modes, media player, calendar, system load, weather.
- Welcome tour on first login: mode, drivers, AI model, automatic mode switching.
- Nebula Store (Super+Shift+A): curated apps and search across Arch and Flathub (Heroic for Epic/GOG, Discord, Spotify…).
- Automatic mode: a game opens → Gaming, Wireshark/Ghidra → Hacking, back again when it closes.
- Graphical installer (whole disk or next to Windows).
- Animated wallpapers (GIF) and smooth transitions on mode switch; mode-styled lock screen.
- Hacking: practice labs DVWA / Juice Shop / WebGoat (127.0.0.1 only), private browser, VPN/Tor indicator.
- Server: ready-made Docker servers — file sharing, Jellyfin, Minecraft.
- Home folder backups (manual and daily).
- File search (Super+Shift+F), `fix` and `… | ai` to explain terminal errors.

## 0.2.0
- Own nebulaos-desktop package and repository: NebulaOS updates via `nebula update`.
- Nebula Hub (Super+H): modes, wallpaper, dock, updates, drivers, snapshots, mode features.
- Disk installer: Btrfs, Snapper snapshots, rollback from the GRUB menu, dual boot with Windows.
- Orbit logo, GRUB / Plymouth / SDDM themes, app windows in the mode's colors.
- Papirus icons, Capitaine cursor, macOS-style window buttons.
- AI assistant window (Super+A).
- Gaming: MangoHud for all games, linux-zen kernel, turbo mode.
- Hacking: Tor, random MAC address. Server: enable services together with the firewall.
- Clipboard history (Super+V), night light (Super+Shift+N), screen recording (Super+Shift+R).

## 0.1.0
- Three modes (gaming, hacking, server) in a macOS-like style, switchable on the fly.
