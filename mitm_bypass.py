"""
Discord NSFW Age Gate Bypass - mitmproxy addon
WebSocket READY event'indeki nsfw_allowed'i patch'ler

Kullanim:
  mitmdump --mode regular -p 8888 -s mitm_bypass.py
"""

import zlib
from mitmproxy import http


class NsfwBypass:
    def __init__(self):
        self.inflator = None

    # HTTP API response'lari
    def response(self, flow: http.HTTPFlow):
        if "discord.com/api" not in flow.request.pretty_url:
            return
        ct = flow.response.headers.get("content-type", "")
        if "json" not in ct:
            return
        try:
            body = flow.response.get_text()
            if body and "nsfw_allowed" in body and '"nsfw_allowed":false' in body:
                body = body.replace('"nsfw_allowed":false', '"nsfw_allowed":true')
                body = body.replace('"age_verification_status":1', '"age_verification_status":2')
                flow.response.set_text(body)
                print(f"\033[32m[HTTP PATCHED]\033[0m {flow.request.path.split('?')[0]}")
        except:
            pass

    # WebSocket mesajlari (READY event burada geliyor)
    def websocket_message(self, flow):
        msg = flow.websocket.messages[-1]
        if msg.from_client:
            return

        data = msg.content

        if self.inflator is None:
            self.inflator = zlib.decompressobj()

        # zlib-stream: Z_SYNC_FLUSH ile biten mesajlar
        is_complete = len(data) >= 4 and data[-4:] == b'\x00\x00\xff\xff'

        try:
            decompressed = self.inflator.decompress(data)
        except:
            self.inflator = zlib.decompressobj()
            try:
                decompressed = self.inflator.decompress(data)
            except:
                return

        if not is_complete:
            return

        try:
            text = decompressed.decode('utf-8')
        except:
            return

        if '"nsfw_allowed":false' not in text and '"nsfw_allowed": false' not in text:
            return

        # PATCH
        patched = text.replace('"nsfw_allowed":false', '"nsfw_allowed":true')
        patched = patched.replace('"nsfw_allowed": false', '"nsfw_allowed": true')
        patched = patched.replace('"age_verification_status":1', '"age_verification_status":2')

        # Recompress: yeni zlib stream baslat
        try:
            deflator = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
            compressed = deflator.compress(patched.encode('utf-8'))
            compressed += deflator.flush(zlib.Z_SYNC_FLUSH)
            msg.content = compressed

            # Inflator'u resetle — stream artik uyumsuz
            self.inflator = zlib.decompressobj()

            print(f"\033[35m[WS PATCHED]\033[0m nsfw_allowed: false -> true (READY event)")
        except Exception as e:
            print(f"\033[31m[WS PATCH FAIL]\033[0m {e}")


addons = [NsfwBypass()]
