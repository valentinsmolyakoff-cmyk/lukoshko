#!/usr/bin/env bash
# Публикация «Лукошка» на GitHub Pages одной командой.
#
#   export GITHUB_TOKEN=ghp_...      # токен: GitHub → Settings → Developer settings →
#                                   #   Personal access tokens (classic) → scope: repo + workflow
#   ./publish-github.sh <логин> [репозиторий]
#
# Что делает:
#   1) создаёт публичный репозиторий (если его ещё нет);
#   2) пушит ветку main (токен НЕ сохраняется в .git/config — передаётся заголовком);
#   3) включает GitHub Pages в режиме «GitHub Actions»;
#   4) печатает адрес сайта вида https://<логин>.github.io/<репозиторий>/
set -euo pipefail
cd "$(dirname "$0")"

USER_="${1:?Укажите логин GitHub: ./publish-github.sh <логин> [репозиторий]}"
REPO="${2:-lukoshko}"
: "${GITHUB_TOKEN:?Нужен export GITHUB_TOKEN=... (scope: repo + workflow)}"

API="https://api.github.com"
AUTH=(-H "Authorization: Bearer ${GITHUB_TOKEN}" -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28")

say() { printf '\033[1;32m✔\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m•\033[0m %s\n' "$*"; }

# --- 1. репозиторий -----------------------------------------------------------
if curl -sf "${AUTH[@]}" "$API/repos/$USER_/$REPO" >/dev/null; then
  warn "Репозиторий $USER_/$REPO уже есть — обновляю содержимое."
else
  warn "Создаю репозиторий $USER_/$REPO…"
  curl -sS "${AUTH[@]}" -X POST "$API/user/repos" \
    -d "{\"name\":\"$REPO\",\"private\":false,\"has_issues\":true,\"has_wiki\":false,
         \"description\":\"Лукошко — развивающая онлайн-игра для детей 5+: 100 уровней, PWA, офлайн\"}" \
    > /tmp/gh_repo.json
  grep -q '"full_name"' /tmp/gh_repo.json || { cat /tmp/gh_repo.json; exit 1; }
fi
say "Репозиторий: https://github.com/$USER_/$REPO"

# --- 2. пуш ------------------------------------------------------------------
if [ ! -d .git ]; then
  git init -q -b main
fi
git add -A
git -c user.name="Лукошко" -c user.email="lukoshko@example.com" \
    commit -q -m "Лукошко: развивающая игра для детей 5+ (100 уровней, PWA, офлайн)" || true
git branch -M main

# токен передаём одноразовым заголовком, в конфиг он не попадает
BASIC="$(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 | tr -d '\n')"
git -c http.extraheader="AUTHORIZATION: Basic ${BASIC}" \
    push --quiet --force-with-lease "https://github.com/$USER_/$REPO.git" main:main \
  || git -c http.extraheader="AUTHORIZATION: Basic ${BASIC}" \
    push --quiet --set-upstream "https://github.com/$USER_/$REPO.git" main:main
say "Код отправлен в ветку main"

# --- 3. GitHub Pages ---------------------------------------------------------
warn "Включаю GitHub Pages (источник: GitHub Actions)…"
curl -sS "${AUTH[@]}" -X POST "$API/repos/$USER_/$REPO/pages" \
  -d '{"build_type":"workflow"}' > /tmp/gh_pages.json 2>/dev/null || true
if ! grep -q '"html_url"\|"build_type"' /tmp/gh_pages.json 2>/dev/null; then
  curl -sS "${AUTH[@]}" -X PUT "$API/repos/$USER_/$REPO/pages" \
    -d '{"build_type":"workflow"}' > /tmp/gh_pages.json 2>/dev/null || true
fi

# --- 4. адрес ----------------------------------------------------------------
URL="https://$USER_.github.io/$REPO/"
say "Готово. Сайт: $URL"
echo "   Первая сборка занимает 30–90 секунд."
echo "   Статус: https://github.com/$USER_/$REPO/actions"
echo "   Проверить готовность:  until curl -sf $URL >/dev/null; do sleep 5; done; echo OK"
