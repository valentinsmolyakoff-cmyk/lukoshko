#!/usr/bin/env bash
# Публикация «Лукошка» одной командой.
#
#   ./deploy.sh netlify            — Netlify (нужен токен: export NETLIFY_AUTH_TOKEN=...)
#   ./deploy.sh netlify новая      — создать новый сайт (иначе обновит существующий)
#   ./deploy.sh vercel             — Vercel (нужен токен: export VERCEL_TOKEN=...)
#   ./deploy.sh gh <логин> <репо>  — GitHub Pages (нужен git + gh auth login или SSH-ключ)
#   ./deploy.sh zip                — просто собрать lukoshko-site.zip для drag-and-drop
#
# Токены бесплатно берутся здесь:
#   Netlify → User settings → Applications → Personal access tokens
#   Vercel  → Account settings → Tokens
set -euo pipefail
cd "$(dirname "$0")"

SITE_FILES=(index.html manifest.webmanifest sw.js icon.svg icon-192.png icon-512.png
            apple-touch-icon.png favicon-32.png netlify.toml _headers vercel.json)

make_zip() {
  rm -f lukoshko-site.zip
  zip -q -r lukoshko-site.zip "${SITE_FILES[@]}" 404.html 2>/dev/null || \
  zip -q -r lukoshko-site.zip "${SITE_FILES[@]}"
  echo "✔ Готово: lukoshko-site.zip ($(du -h lukoshko-site.zip | cut -f1))"
  echo "  Перетащите архив на https://app.netlify.com/drop — сайт появится за ~20 секунд."
}

cmd="${1:-zip}"

case "$cmd" in
  zip)
    make_zip
    ;;

  netlify)
    command -v netlify >/dev/null || { echo "Ставлю Netlify CLI…"; npm i -g netlify-cli; }
    : "${NETLIFY_AUTH_TOKEN:?Нужен export NETLIFY_AUTH_TOKEN=... (User settings → Applications)}"
    if [ "${2:-}" = "новая" ] || [ "${2:-}" = "new" ]; then
      netlify sites:create --manual --name "lukoshko-$RANDOM"
    fi
    netlify deploy --prod --dir . --site "${NETLIFY_SITE_ID:-}" 
    echo "✔ Опубликовано. Адрес смотрите в выводе выше (Deploy log → Website URL)."
    ;;

  vercel)
    command -v vercel >/dev/null || { echo "Ставлю Vercel CLI…"; npm i -g vercel; }
    : "${VERCEL_TOKEN:?Нужен export VERCEL_TOKEN=... (Account settings → Tokens)}"
    vercel deploy --prod --yes --token "$VERCEL_TOKEN"
    ;;

  gh)
    : "${2:?Укажите логин GitHub: ./deploy.sh gh <логин> <репозиторий>}"
    repo="${3:-lukoshko}"
    git init -q 2>/dev/null || true
    git add -A
    git commit -qm "Лукошко: игра для детей 5+" || true
    git branch -M main
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://github.com/$2/$repo.git"
    git push -u origin main
    echo "✔ Код на GitHub. Теперь: Settings → Pages → Source: GitHub Actions."
    echo "  Адрес: https://$2.github.io/$repo/"
    ;;

  *)
    echo "Неизвестная команда: $cmd"; grep '^#' "$0" | head -12; exit 1
    ;;
esac
