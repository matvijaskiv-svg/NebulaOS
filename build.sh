#!/usr/bin/env bash
# Собирает NebulaOS ISO: берёт releng из установленного archiso, собирает пакет
# nebulaos-desktop в локальный репозиторий, накладывает профиль NebulaOS и
# запускает mkarchiso. Запускать на Arch Linux (ВМ, WSL с Arch, Docker) от root.
#
#   bash build.sh              — собрать ISO в ./out
#   bash build.sh --prepare    — всё, кроме mkarchiso (быстрая проверка)
#
# Нужны пакеты: archiso grub base-devel
# Переменные: OUT_DIR (./out), WORK_DIR (/tmp/nebulaos-work),
#             PROFILE_DIR (/tmp/nebulaos-profile), RELENG (/usr/share/archiso/configs/releng),
#             NEBULA_REPO_URL — адрес репозитория обновлений (см. tools/publish-repo.sh)
set -euo pipefail

src=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
releng=${RELENG:-/usr/share/archiso/configs/releng}
profile=${PROFILE_DIR:-/tmp/nebulaos-profile}
work=${WORK_DIR:-/tmp/nebulaos-work}
out=${OUT_DIR:-$src/out}
repo=/tmp/nebulaos-repo
prepare_only=0
[[ ${1:-} == --prepare ]] && prepare_only=1

die() { printf 'build.sh: %s\n' "$*" >&2; exit 1; }
clean() { sed -e 's/\r$//' -e 's/#.*//' -e 's/[[:space:]]//g' | awk 'NF'; }

[[ $EUID -eq 0 ]] || die 'нужны права root: sudo bash build.sh'
[[ -d $releng ]] || die "нет $releng — установите archiso: pacman -S archiso"
command -v makepkg >/dev/null && command -v fakeroot >/dev/null || die 'нужны makepkg и fakeroot: pacman -S --needed base-devel'
(( prepare_only )) || command -v mkarchiso >/dev/null || die 'mkarchiso не найден'
(( prepare_only )) || command -v grub-install >/dev/null || die 'нужен grub для UEFI-загрузки: pacman -S grub'

# ---------- 1. Пакет nebulaos-desktop и локальный репозиторий ----------
printf '==> Пакет nebulaos-desktop\n'
conf=$src/desktop/etc/pacman.d/nebulaos-repo.conf
conf_backup=$(mktemp)
cp -- "$conf" "$conf_backup"
trap 'cp -- "$conf_backup" "$conf"; rm -f -- "$conf_backup"' EXIT
NEBULA_REPO_URL=${NEBULA_REPO_URL-https://github.com/matvijaskiv-svg/NebulaOS-updates/releases/download/repo}
if [[ -n ${NEBULA_REPO_URL:-} ]]; then
  printf '[nebulaos]\nSigLevel = Optional TrustAll\nServer = %s\n' "$NEBULA_REPO_URL" > "$conf"
fi
rm -rf -- "$repo"
REPO_DIR=$repo bash "$src/tools/publish-repo.sh" >/dev/null
[[ -f $repo/nebulaos.db ]] || die 'не удалось собрать пакет nebulaos-desktop'
ls -1 "$repo"/*.pkg.tar.zst

# ---------- 2. Профиль: releng + NebulaOS ----------
printf '==> Профиль: %s (releng + NebulaOS)\n' "$profile"
rm -rf -- "$profile"
cp -a -- "$releng" "$profile"
cp -a -- "$src/airootfs/." "$profile/airootfs/"
cp -- "$src/profiledef.sh" "$src/pacman.conf" "$profile/"
while IFS= read -r -d '' f; do   # CRLF, если файлы правили в Windows
  case $f in *.png) continue ;; esac
  sed -i 's/\r$//' -- "$profile/${f#"$src"/}"
done < <(find "$src/airootfs" "$src/profiledef.sh" "$src/pacman.conf" -type f -print0)
chmod 0755 "$profile"/airootfs/usr/local/bin/nebula-install{,-gui}
# Version in the ISO name; NEBULA_ADMIN=1 builds the maintainer's personal ISO with the admin panel.
ver=$(sed -n 's/^pkgver=//p' "$src/pkg/PKGBUILD")
sed -i "s/^iso_version=.*/iso_version=\"$ver\"/" "$profile/profiledef.sh"
if [[ ${NEBULA_ADMIN:-0} == 1 ]]; then
  printf '==> Personal ISO: with the admin panel\n'
  [[ -f $src/tools/admin/nebula-admin ]] || die 'tools/admin/nebula-admin is missing (it is kept only on your computer)'
  sed -i "s/^iso_name=.*/iso_name=\"nebulaos-admin\"/" "$profile/profiledef.sh"
  install -Dm755 "$src/tools/admin/nebula-admin" "$profile/airootfs/usr/local/bin/nebula-admin"
  install -Dm644 "$src/tools/admin/nebula-admin.desktop" "$profile/airootfs/usr/local/share/applications/nebula-admin.desktop"
  sed -i '/\["\/usr\/local\/bin\/nebula-install"\]=/i\  ["/usr/local/bin/nebula-admin"]="0:0:755"' "$profile/profiledef.sh"
fi
install -d "$profile/airootfs/home/nebula" "$profile/airootfs/opt/nebulaos"
cp -a -- "$repo" "$profile/airootfs/opt/nebulaos/repo"
printf '\n[nebulaos]\nSigLevel = Optional TrustAll\nServer = file://%s\n' "$repo" >> "$profile/pacman.conf"
# Style lock: the KDE appearance pages never get into the image.
sed -i "/^\[options\]/a $(bash "$src/desktop/usr/lib/nebulaos/style-lock" --noextract)" "$profile/pacman.conf"

# AI-модель прямо в ISO (по умолчанию qwen2.5:1.5b, ~1 ГБ; NEBULA_AI_MODEL=none — без неё).
# Скачивается один раз в кэш /tmp/nebulaos-models и переиспользуется в следующих сборках.
ai_model=${NEBULA_AI_MODEL:-qwen2.5:1.5b}
if [[ $ai_model != none ]]; then
  models=/tmp/nebulaos-models
  install -d "$models"
  if [[ ! -e $models/manifests/registry.ollama.ai/library/${ai_model%%:*}/${ai_model#*:} ]]; then
    command -v ollama >/dev/null || pacman -S --noconfirm --needed ollama >/dev/null
    printf '==> AI-модель %s (скачивается один раз)
' "$ai_model"
    OLLAMA_MODELS=$models OLLAMA_HOST=127.0.0.1:11555 ollama serve >/tmp/nebulaos-ollama.log 2>&1 &
    ollama_pid=$!
    for _ in $(seq 30); do OLLAMA_HOST=127.0.0.1:11555 ollama list >/dev/null 2>&1 && break; sleep 1; done
    OLLAMA_HOST=127.0.0.1:11555 ollama pull "$ai_model" >/dev/null || die "не удалось скачать модель $ai_model"
    kill "$ollama_pid" 2>/dev/null || true
  fi
  install -d "$profile/airootfs/var/lib/ollama"
  cp -a -- "$models/." "$profile/airootfs/var/lib/ollama/"
  printf '==> AI-модель в образе: %s
' "$ai_model"
fi

# Пакеты: список releng (загрузчики, mkinitcpio-archiso, ...) + NebulaOS.
cat -- "$releng/packages.x86_64" "$src/packages.x86_64" | clean | sort -u > "$profile/packages.x86_64"

# ---------- 3. Службы ----------
# В releng сеть ведут systemd-networkd + iwd, у нас NetworkManager (конфликт).
# sshd и автовход root на tty1 для десктопного Live не нужны.
units=$profile/airootfs/etc/systemd/system
find "$units" -type l \( -name 'systemd-networkd*' -o -name 'iwd.service' -o -name 'sshd.service' \) -delete
rm -rf -- "$units/getty@tty1.service.d"
enable() { # enable <unit> <target>
  install -d "$units/$2.wants"
  ln -sfn "/usr/lib/systemd/system/$1" "$units/$2.wants/$1"
}
enable NetworkManager.service multi-user.target
enable NetworkManager-wait-online.service network-online.target
ln -sfn /usr/lib/systemd/system/NetworkManager-dispatcher.service "$units/dbus-org.freedesktop.nm-dispatcher.service"
enable ollama.service multi-user.target
enable nebula-firstboot.service multi-user.target
enable bluetooth.service bluetooth.target
enable power-profiles-daemon.service graphical.target
install -d "$units/sockets.target.wants" && ln -sfn /usr/lib/systemd/system/cups.socket "$units/sockets.target.wants/cups.socket"
ln -sfn /usr/lib/systemd/system/sddm.service "$units/display-manager.service"
ln -sfn /usr/lib/systemd/system/graphical.target "$units/default.target"

# ---------- 4. Загрузка: брендинг, заставка, Plymouth ----------
cp -- "$src/branding/splash.png" "$profile/syslinux/splash.png"
find "$profile/grub" "$profile/syslinux" "$profile/efiboot" -type f \( -name '*.cfg' -o -name '*.conf' \) -print0 \
  | xargs -0 -r sed -i \
      -e 's/Arch Linux install medium/NebulaOS Live/g' \
      -e 's/Arch Linux/NebulaOS/g' \
      -e '/archisobasedir=/{/ quiet splash/!s/$/ quiet splash/}'
grub_cfg=$profile/grub/grub.cfg
if [[ -f $grub_cfg ]] && ! grep -q 'NebulaOS colors' "$grub_cfg"; then
  { printf '# NebulaOS colors\n'
    printf 'set menu_color_normal=light-gray/black\n'
    printf 'set menu_color_highlight=white/magenta\n'
    printf 'set color_normal=light-gray/black\n'
    cat -- "$grub_cfg"; } > "$grub_cfg.new" && mv -f -- "$grub_cfg.new" "$grub_cfg"
fi
# «Safe graphics»: копия первого пункта без заставки и с nomodeset — для ВМ и
# видеокарт, на которых обычная загрузка зависает на чёрном экране.
for cfg in "$profile/grub/grub.cfg" "$profile/grub/loopback.cfg"; do
  [[ -f $cfg ]] && ! grep -q 'Safe graphics' "$cfg" || continue
  awk '
    !done && /^menuentry / { grab = 1 }
    grab { buf = buf $0 "\n" }
    { print }
    grab && /^}/ {
      grab = 0; done = 1
      gsub(/menuentry "[^"]*"/, "menuentry \"NebulaOS Live (Safe graphics)\"", buf)
      gsub(/ quiet splash/, "", buf)
      gsub(/archisobasedir=/, "nomodeset archisobasedir=", buf)
      gsub(/--id='"'"'[^'"'"']*'"'"'/, "--id='"'"'nebula-safe'"'"'", buf)
      printf "\n%s", buf
    }' "$cfg" > "$cfg.new" && mv -f -- "$cfg.new" "$cfg"
  sed -i "/Safe graphics/s/--id '[^']*'/--id 'nebula-safe'/" "$cfg"
  # «Install NebulaOS»: the same Live system that opens the installer right away.
  if ! grep -q 'Install NebulaOS' "$cfg"; then
    awk '
      !done && /^menuentry / { grab = 1 }
      grab { buf = buf $0 "
" }
      { print }
      grab && /^}/ {
        grab = 0; done = 1
        gsub(/menuentry "[^"]*"/, "menuentry \"Install NebulaOS\"", buf)
        gsub(/--id .[^ ]*./, "--id nebula-install", buf)
        gsub(/archisobasedir=/, "nebula.install=1 archisobasedir=", buf)
        printf "
%s", buf
      }' "$cfg" > "$cfg.new" && mv -f -- "$cfg.new" "$cfg"
  fi
done
sys_cfg=$profile/syslinux/archiso_sys-linux.cfg
if [[ -f $sys_cfg ]] && ! grep -q 'Safe graphics' "$sys_cfg"; then
  awk '
    !done && /^LABEL / { grab = 1 }
    grab && /^$/ && buf != "" {
      grab = 0; done = 1; print; sub(/LABEL [^\n]*/, "LABEL nebula_safe", buf)
      sub(/MENU LABEL [^\n]*/, "MENU LABEL NebulaOS Live (Safe graphics)", buf)
      gsub(/ quiet splash/, "", buf); sub(/archisobasedir=/, "nomodeset archisobasedir=", buf)
      printf "%s\n", buf; next
    }
    grab { buf = buf $0 "\n" }
    { print }' "$sys_cfg" > "$sys_cfg.new" && mv -f -- "$sys_cfg.new" "$sys_cfg"
fi
mkinit=$profile/airootfs/etc/mkinitcpio.conf.d/archiso.conf
if [[ -f $mkinit ]] && ! grep -q plymouth "$mkinit"; then
  sed -Ei 's/^(HOOKS=\([^)]*\<(udev|systemd)\>)/\1 plymouth/' "$mkinit"
fi

# ---------- 5. Проверки ----------
bash -n "$profile/profiledef.sh"
for s in nebula nebula-firstboot; do bash -n "$src/desktop/usr/bin/$s"; done
bash -n "$profile/airootfs/usr/local/bin/nebula-install"
if command -v python3 >/dev/null; then
  for s in ai nebula-hub nebula-ai-overlay nebula-welcome nebula-store nebula-automode; do
    python3 -c 'import ast,sys; ast.parse(open(sys.argv[1], encoding="utf-8").read())' "$src/desktop/usr/bin/$s"
  done
fi

# Все ли пакеты есть в репозиториях: ISO, зависимости nebulaos-desktop и наборы
# режимов. multilib включаем только для проверки (он нужен режиму gaming).
install -d "$work/checkdb"
sed -e 's/^#\[multilib\]/[multilib]/' -e '/^\[multilib\]/{n;s/^#Include/Include/}' "$profile/pacman.conf" > "$work/check.conf"
if pacman -Sy --config "$work/check.conf" --dbpath "$work/checkdb" >/dev/null; then
  missing=$( { cat "$profile/packages.x86_64" "$src"/desktop/usr/share/nebulaos/modes/*/packages
               sed -n '/^depends=(/,/^)/p' "$src/pkg/PKGBUILD" | sed '1d;$d' | tr ' ' '\n'
               printf '%s\n' os-prober ntfs-3g grub-btrfs snapper snap-pac inotify-tools linux-zen linux-lts ufw docker firejail tor
               # Arch-программы из каталога Nebula Store.
               { grep -A1 '"source": "arch"' "$src/desktop/usr/share/nebulaos/store.json" | sed -n 's/.*"id": "\([^"]*\)".*/\1/p' || true; }; } \
    | clean | sort -u | while read -r p; do
        pacman -Sp --config "$work/check.conf" --dbpath "$work/checkdb" --print-format '' "$p" >/dev/null 2>&1 || printf '%s ' "$p"
      done)
  [[ -z $missing ]] || die "пакеты не найдены в репозиториях: $missing"
  printf '==> Все пакеты найдены в репозиториях\n'
else
  printf '==> Нет доступа к репозиториям, проверка пакетов пропущена\n'
fi

(( prepare_only )) && { printf '==> Профиль готов: %s\n' "$profile"; exit 0; }

# ---------- 6. Сборка ----------
rm -rf -- "$work"
mkarchiso -v -w "$work" -o "$out" "$profile"
printf '==> Готово: %s\n' "$out"
