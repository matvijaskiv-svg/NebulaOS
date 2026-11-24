#!/usr/bin/env bash
# Publish a NebulaOS update to GitHub — every installed NebulaOS gets it via `nebula update`.
#
#   bash tools/release.sh 0.6.1 "What is new in one line"
#
# Needs: Arch (NebulaOS, WSL or a VM), base-devel, git, github-cli (`gh auth login` once)
# and your signing key (~/.config/nebulaos/admin.key or NEBULA_ADMIN_KEY).
# What it does:
#   1. sets the version (pkg/PKGBUILD, channel/channel.json, CHANGELOG);
#   2. builds the nebulaos-desktop package and the pacman repository (tools/publish-repo.sh);
#   3. uploads the repository to the GitHub release "repo" (pacman reads it from there);
#   4. adds a news item and pushes the code + channel to GitHub (users get a notification).
set -euo pipefail
src=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$src"
ver=${1:?usage: release.sh <version> "<what is new>"}
note=${2:-"NebulaOS $ver"}
[[ $ver =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "version must look like 0.6.1" >&2; exit 1; }
for c in git gh makepkg repo-add python3; do
  command -v "$c" >/dev/null || { echo "missing: $c (sudo pacman -S --needed base-devel git github-cli python)" >&2; exit 1; }
done
gh auth status >/dev/null 2>&1 || { echo "first run: gh auth login" >&2; exit 1; }

echo "==> Version $ver"
sed -i "s/^pkgver=.*/pkgver=$ver/; s/^pkgrel=.*/pkgrel=1/" pkg/PKGBUILD
python3 - "$ver" "$note" <<'PY'
import json, sys, time
from pathlib import Path
ver, note = sys.argv[1:3]
p = Path("channel/channel.json")
data = json.loads(p.read_text(encoding="utf-8"))
data["latest"] = ver
data.setdefault("news", []).append({"id": f"release-{ver}", "level": "info", "action": "update",
                                    "title": f"NebulaOS {ver}", "text": note})
data["news"] = data["news"][-20:]
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
log = Path("desktop/usr/share/nebulaos/CHANGELOG.md")
text = log.read_text(encoding="utf-8")
head, _, rest = text.partition("\n## ")
if f"## {ver}\n" not in text:
    log.write_text(f"{head}\n## {ver}\n- {note}\n\n## {rest}", encoding="utf-8")
PY

echo "==> Sign the channel"
python3 tools/admin/sign-channel.py

echo "==> Package and repository"
rm -rf out/repo
bash tools/publish-repo.sh

echo "==> Upload to GitHub release \"repo\""
gh release view repo >/dev/null 2>&1 || gh release create repo --title "NebulaOS update repository" \
  --notes "pacman repository used by nebula update. Do not delete." --latest=false
gh release upload repo out/repo/* --clobber

echo "==> Push code and news"
git add -A pkg desktop channel
git commit -m "NebulaOS $ver: $note" || true
git push
echo "Done: NebulaOS $ver is published. Installed systems get it with nebula update."
