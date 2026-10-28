#!/usr/bin/env python3
"""Локальный сервер для «Лукошка».

Зачем: игра — это набор статических файлов (HTML/PNG/JSON). Чтобы работали
установка на телефон (PWA), офлайн-режим и корректные MIME-типы, её нужно
отдавать по http, а не открывать как file://.

Запуск:
    python3 serve.py            # http://localhost:8000
    python3 serve.py 8080       # другой порт
    python3 serve.py 8080 0.0.0.0   # слушать все интерфейсы (для доступа в сети)

Дальше: откройте http://localhost:8000 — и играйте. Телефон в той же Wi-Fi:
http://<IP-компьютера>:8000
"""
import http.server
import socketserver
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
HOST = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".webmanifest": "application/manifest+json",
        ".js": "application/javascript",
        ".svg": "image/svg+xml",
        ".md": "text/markdown; charset=utf-8",
        ".csv": "text/csv; charset=utf-8",
    }

    def end_headers(self):
        # чтобы правки уровней подхватывались сразу после обновления страницы
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # тихий режим


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as httpd:
        print(f"Лукошко → http://localhost:{PORT}  (host {HOST})")
        print("Ctrl+C — остановить")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nПока!")
