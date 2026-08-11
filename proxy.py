#!/usr/bin/env python3
"""
Discord API CORS Proxy
Tarayicidan Discord API'ye direkt istek atilamiyor (CORS),
bu proxy aradaki engeli kaldiriyor.

Kullanim:
  python3 proxy.py
  Tarayicida http://localhost:8009 ac
"""

import http.server
import json
import os
import sys
import urllib.request
import urllib.error
import ssl

PORT = 8009
DISCORD_API = "https://discord.com/api/v9"

# index.html icindeki API URL'ini proxy'ye yonlendir
INDEX_HTML = None


def load_index():
    global INDEX_HTML
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    # API URL'ini local proxy'ye yonlendir
    INDEX_HTML = content.replace(
        "const API = 'https://discord.com/api/v9';",
        f"const API = 'http://localhost:{PORT}/api/v9';"
    )


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Renkli log
        method = args[0].split()[0] if args else ""
        path = args[0].split()[1] if args and len(args[0].split()) > 1 else ""
        status = args[1] if len(args) > 1 else ""

        colors = {"GET": "\033[36m", "PATCH": "\033[35m", "POST": "\033[33m", "DELETE": "\033[31m"}
        color = colors.get(method, "\033[37m")

        status_color = "\033[32m" if str(status).startswith("2") else "\033[31m"
        print(f"  {color}{method}\033[0m {path} {status_color}{status}\033[0m")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Discord-Locale, X-Discord-Timezone, X-Super-Properties")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # index.html serve
        if self.path == "/" or self.path == "/index.html":
            if INDEX_HTML is None:
                load_index()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode("utf-8"))
            return

        # API proxy
        if self.path.startswith("/api/"):
            self.proxy_request("GET")
            return

        self.send_response(404)
        self.end_headers()

    def do_PATCH(self):
        if self.path.startswith("/api/"):
            self.proxy_request("PATCH")
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_request("POST")
            return
        self.send_response(404)
        self.end_headers()

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self.proxy_request("PUT")
            return
        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self.proxy_request("DELETE")
            return
        self.send_response(404)
        self.end_headers()

    def proxy_request(self, method):
        # /api/v9/... -> https://discord.com/api/v9/...
        target_url = f"https://discord.com{self.path}"

        # Body oku
        body = None
        content_length = self.headers.get("Content-Length")
        if content_length:
            body = self.rfile.read(int(content_length))

        # Discord'a gonderilecek headerlar
        headers = {}
        forward_headers = [
            "Authorization", "Content-Type",
            "X-Super-Properties", "X-Discord-Locale", "X-Discord-Timezone",
            "X-Installation-ID", "X-Debug-Options"
        ]
        for h in forward_headers:
            val = self.headers.get(h)
            if val:
                headers[h] = val

        # User-Agent ekle (Discord bunu kontrol eder)
        headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"

        # SSL context
        ctx = ssl.create_default_context()

        try:
            req = urllib.request.Request(target_url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                resp_body = resp.read()
                status = resp.status

                self.send_response(status)
                self.send_cors_headers()

                # Response headerlarini ilet
                ct = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", ct)

                # Rate limit headerlari
                for rl_header in ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "Retry-After"]:
                    val = resp.headers.get(rl_header)
                    if val:
                        self.send_header(rl_header, val)

                self.end_headers()

                if resp_body:
                    self.wfile.write(resp_body)

        except urllib.error.HTTPError as e:
            resp_body = e.read()
            self.send_response(e.code)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")

            # Rate limit info
            retry_after = e.headers.get("Retry-After")
            if retry_after:
                self.send_header("Retry-After", retry_after)

            self.end_headers()
            if resp_body:
                self.wfile.write(resp_body)

        except Exception as e:
            self.send_response(502)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


def main():
    load_index()

    server = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)

    print()
    print(f"\033[35m  Discord NSFW Gate Bypass Proxy\033[0m")
    print(f"\033[90m  ────────────────────────────────\033[0m")
    print(f"  \033[36mhttp://localhost:{PORT}\033[0m")
    print()
    print(f"\033[90m  Tarayicida yukardaki URL'i ac.\033[0m")
    print(f"\033[90m  Ctrl+C ile kapat.\033[0m")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[33m  Kapatiliyor...\033[0m")
        server.server_close()


if __name__ == "__main__":
    main()
