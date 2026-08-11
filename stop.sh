#!/bin/bash
# Bypass'i kapat ve proxy ayarini geri al

pkill -f "mitmdump.*8888" 2>/dev/null
pkill -f "python3.*8889" 2>/dev/null

echo ""
echo "  [✓] mitmproxy kapatildi"
echo "  [✓] PAC server kapatildi"
echo ""
echo "  Firefox'ta proxy'yi kapat:"
echo "    about:preferences#general > Network Settings > No proxy"
echo ""
