# Сервер рекомендаций Gemini

В Vercel подключите этот репозиторий, Root Directory: `server`, Framework: Other.
Секрет `GEMINI_API_KEY` хранится только в Environment Variables для Production.
Адрес обработчика после публикации: `https://<production-domain>/api/advice`.
До запуска необходимо настроить квоту Google и распределённый лимит запросов:
локальный лимит в функции сбрасывается при перезапуске и не ограничивает суммарные расходы.
Origin по умолчанию: https://valentinsmolyakoff-cmyk.github.io.
CORS не заменяет защиту от ботов. Имена и история действий ребёнка не передаются.
Проверка без ключа: `node test.cjs` (внешний API подменяется в тестах).
