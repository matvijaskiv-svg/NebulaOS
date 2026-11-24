# NebulaOS: translations for shell scripts (sourced by nebula and nebula-install).
# Language: $NEBULA_LANG, then ~/.config/nebulaos/lang, then $LANG. Catalogs are
# /usr/share/nebulaos/i18n/<lang>.tsv: "English<TAB>Translation" per line.
declare -A NEBULA_TR=()

nebula_lang() {
  local l=${NEBULA_LANG:-} home f
  if [[ -z $l ]]; then
    home=$HOME; [[ -n ${SUDO_USER:-} ]] && home=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    f=${XDG_CONFIG_HOME:-$home/.config}/nebulaos/lang
    [[ -r $f ]] && read -r l < "$f"
  fi
  [[ -z $l ]] && l=${LANG%%_*}
  case $l in ru|uk|it) printf '%s' "$l" ;; *) printf 'en' ;; esac
}

nebula_load_tr() {
  local f k v
  f=/usr/share/nebulaos/i18n/$(nebula_lang).tsv
  [[ -r $f ]] || return 0
  while IFS=$'\t' read -r k v; do
    [[ -n $k && -n $v && $k != \#* ]] && NEBULA_TR[$k]=$v
  done < "$f"
}

# t 'English text' -> translated text (or the original).
t() { printf '%s' "${NEBULA_TR[$1]:-$1}"; }

nebula_load_tr
