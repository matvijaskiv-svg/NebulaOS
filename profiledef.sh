#!/usr/bin/env bash
# shellcheck disable=SC2034
# NebulaOS — профиль archiso. Накладывается поверх releng скриптом build.sh.

iso_name="nebulaos"
iso_label="NEBULA_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="NebulaOS"
iso_application="NebulaOS Live/Rescue Environment"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="arch"
buildmodes=('iso')
# Актуальные режимы archiso: bios.syslinux, uefi.grub, uefi.systemd-boot.
# GRUB для UEFI (x64 и ia32) берётся из каталога grub/ профиля releng.
bootmodes=('bios.syslinux'
           'uefi.grub')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
  ["/etc/sudoers.d"]="0:0:750"
  ["/etc/sudoers.d/10-wheel"]="0:0:440"
  ["/home/nebula"]="1000:1000:750"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/usr/local/bin/nebula-install"]="0:0:755"
  ["/usr/local/bin/nebula-install-gui"]="0:0:755"
)
