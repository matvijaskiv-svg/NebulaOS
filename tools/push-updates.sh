#!/usr/bin/env bash
# Publish what installed NebulaOS systems download to the PUBLIC updates repository.
# The source repository (NebulaOS: code, build, admin panel) can then stay private.
#
#   bash tools/push-updates.sh channel   signed channel (news, polls, groups, bans, wallpapers) → main branch
#   bash tools/push-updates.sh repo      pacman repository out/repo/* → release "repo"
#   bash tools/push-updates.sh all       both
#
# Public repository: $NEBULA_UPDATES_REPO (default matvijaskiv-svg/NebulaOS-updates),
# local copy: $NEBULA_UPDATES_DIR (default: NebulaOS-updates next to this repository).
# The first run creates the public repository (needs `gh auth login`).
set -euo pipefail
src=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
UPDATES=${NEBULA_UPDATES_REPO:-matvijaskiv-svg/NebulaOS-updates}
dir=${NEBULA_UPDATES_DIR:-$(dirname "$src")/NebulaOS-updates}
what=${1:-all}
command -v gh >/dev/null || { echo "missing: gh (sudo pacman -S github-cli)" >&2; exit 1; }

if ! gh repo view "$UPDATES" >/dev/null 2>&1; then
  echo "==> Creating the public repository $UPDATES"
  gh repo create "$UPDATES" --public --description "NebulaOS updates: signed channel and package repository" \
    --add-readme
fi

if [[ $what == channel || $what == all ]]; then
  echo "==> Channel → github.com/$UPDATES"
  [[ -d $dir/.git ]] || gh repo clone "$UPDATES" "$dir"
  git -C "$dir" pull -q --ff-only || true
  python3 "$src/tools/admin/sign-channel.py" --check
  rm -rf "$dir/channel"
  cp -a "$src/channel" "$dir/channel"
  cat > "$dir/README.md" <<'EOF'
# NebulaOS updates

What installed NebulaOS systems download. Nothing to edit here by hand.

- `channel/channel.json` + `channel.sig` — news, polls, official groups, ban list, wallpaper of the week.
  Every NebulaOS accepts it only with the maintainer's Ed25519 signature.
- Release `repo` — the pacman repository `[nebulaos]` used by `nebula update`.
EOF
  git -C "$dir" add -A
  if git -C "$dir" diff --cached --quiet; then
    echo "    (no changes)"
  else
    git -C "$dir" commit -qm "Channel update $(date -u +%Y-%m-%dT%H:%MZ)"
    git -C "$dir" push -q
  fi
fi

if [[ $what == repo || $what == all ]]; then
  echo "==> Package repository → release \"repo\" of $UPDATES"
  ls "$src"/out/repo/nebulaos.db >/dev/null
  gh release view repo --repo "$UPDATES" >/dev/null 2>&1 || gh release create repo --repo "$UPDATES" \
    --title "NebulaOS update repository" --notes "pacman repository used by nebula update. Do not delete." --latest=false
  gh release upload repo "$src"/out/repo/* --clobber --repo "$UPDATES"
fi
echo "Published to github.com/$UPDATES"
