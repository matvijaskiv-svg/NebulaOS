#!/usr/bin/env bash
# Собирает пакет nebulaos-desktop и репозиторий [nebulaos] для обновлений.
# Запуск на Arch (WSL/ВМ):  bash tools/publish-repo.sh
# Результат: out/repo/ (nebulaos.db, nebulaos.files и *.pkg.tar.zst).
#
# Публикация на GitHub Releases (один раз: gh auth login):
#   gh release create repo --title "NebulaOS repo" --notes "pacman repo" || true
#   gh release upload repo out/repo/* --clobber
# Адрес для NEBULA_REPO_URL: https://github.com/<вы>/<репо>/releases/download/repo
#
# Подпись (рекомендуется): создайте ключ gpg и задайте GPGKEY=<id> —
# пакет и база будут подписаны, а SigLevel можно поднять до Required.
set -euo pipefail
src=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
out=${REPO_DIR:-${OUT_DIR:-$src/out}/repo}
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT

cp -a "$src/pkg/." "$stage/"
cp -a "$src/desktop" "$stage/desktop"
find "$stage" -type f ! -name '*.png' -exec sed -i 's/\r$//' {} + 2>/dev/null || true
if [[ $EUID -eq 0 ]]; then
  chown -R nobody: "$stage"
  run() { runuser -u nobody -- env HOME="$stage" "$@"; }
else
  run() { "$@"; }
fi
sign=(); [[ -n ${GPGKEY:-} ]] && sign=(--sign --key "$GPGKEY")
(cd "$stage" && run env PKGDEST="$stage/out" BUILDDIR="$stage/build" SRCDEST="$stage/src" \
  makepkg -d -f --noconfirm "${sign[@]}" >/dev/null)

install -d "$out"
cp -f "$stage"/out/*.pkg.tar.zst* "$out/"
rsign=(); [[ -n ${GPGKEY:-} ]] && rsign=(--sign --key "$GPGKEY")
repo-add -q -R "${rsign[@]}" "$out/nebulaos.db.tar.gz" "$out"/nebulaos-desktop-*.pkg.tar.zst
# GitHub не хранит символьные ссылки: заменяем их копиями.
for f in nebulaos.db nebulaos.files; do
  [[ -L $out/$f ]] && cp --remove-destination "$(readlink -f "$out/$f")" "$out/$f"
done
ls -1 "$out"
