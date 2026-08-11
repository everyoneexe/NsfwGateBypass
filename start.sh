#!/bin/bash
# Discord NSFW Gate Bypass
# Mevcut Firefox profilinde, sadece Discord icin proxy

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROFILE_DIR="$HOME/.mozilla/firefox/5x519f11.default-release"

echo ""
echo -e "${GREEN}  Discord NSFW Gate Bypass${NC}"
echo -e "  ────────────────────────"
echo ""

# mitmproxy
if pgrep -f "mitmdump.*8888" > /dev/null 2>&1; then
    echo -e "${CYAN}  [✓] mitmproxy zaten calisiyor${NC}"
else
    fuser -k 8888/tcp 2>/dev/null
    sleep 0.5
    nohup mitmdump --mode regular -p 8888 -s "$SCRIPT_DIR/mitm_bypass.py" --set block_global=false > /tmp/mitm.log 2>&1 &
    sleep 2
    if pgrep -f "mitmdump.*8888" > /dev/null 2>&1; then
        echo -e "${GREEN}  [✓] mitmproxy baslatildi${NC}"
    else
        echo -e "${RED}  [✗] mitmproxy baslatilamadi!${NC}"
        cat /tmp/mitm.log
        exit 1
    fi
fi

# PAC server
PAC_PORT=8889
if ! pgrep -f "python3.*$PAC_PORT" > /dev/null 2>&1; then
    fuser -k $PAC_PORT/tcp 2>/dev/null
    sleep 0.3
    nohup python3 -c "
import http.server, socketserver, os
os.chdir('$SCRIPT_DIR')
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Content-Type', 'application/x-ns-proxy-autoconfig')
        super().end_headers()
    def log_message(self, *a): pass
socketserver.TCPServer(('127.0.0.1', $PAC_PORT), H).serve_forever()
" > /dev/null 2>&1 &
    sleep 1
    echo -e "${GREEN}  [✓] PAC server baslatildi${NC}"
fi

# Firefox acik mi?
if pgrep -f firefox > /dev/null 2>&1; then
    echo ""
    echo -e "${YELLOW}  Firefox acik! Su adimlari yap:${NC}"
    echo ""
    echo -e "  1. Firefox'ta ${CYAN}about:preferences#general${NC} ac"
    echo -e "  2. En alta scroll et → ${CYAN}Network Settings${NC} → ${CYAN}Settings...${NC}"
    echo -e "  3. ${CYAN}Automatic proxy configuration URL${NC} sec"
    echo -e "  4. URL'ye yaz: ${GREEN}http://127.0.0.1:${PAC_PORT}/proxy.pac${NC}"
    echo -e "  5. ${CYAN}OK${NC} tikla"
    echo -e "  6. Discord'da ${CYAN}F5${NC} bas"
    echo ""
    echo -e "  ${CYAN}Sadece Discord proxy'den gecer, diger siteler direkt.${NC}"
    echo ""
    echo -e "  ${YELLOW}Ilk seferde sertifika uyarisi gelirse:${NC}"
    echo -e "  ${YELLOW}  Advanced > Accept the Risk and Continue${NC}"
    echo ""
    echo -e "  Kapatmak icin: ${CYAN}./stop.sh${NC}"
else
    echo -e "${GREEN}  [*] Firefox aciliyor...${NC}"
    firefox -P "default-release" "https://discord.com/channels/@me" 2>/dev/null &
fi
