# listener.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)
        decoded = ""
        try:
            decoded = base64.b64decode(post_data).decode(errors="ignore")
        except Exception:
            decoded = post_data.decode(errors="ignore")

        print(f"\n=== {self.path} ===\n")
        print(decoded)
        self.send_response(200)
        self.end_headers()

server = HTTPServer(('0.0.0.0', 8000), Handler)
print("[*] Listening on port 8000...")
server.serve_forever()
