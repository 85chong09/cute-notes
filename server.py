import http.server
import socketserver
import os
import sys

PORT = 1420

script_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(script_dir, 'src')

if not os.path.exists(web_dir):
    print(f"错误: 找不到目录 {web_dir}")
    sys.exit(1)

os.chdir(web_dir)

Handler = http.server.SimpleHTTPRequestHandler

class MyHTTPRequestHandler(Handler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"服务器运行在 http://localhost:{PORT}")
    print(f"静态文件目录: {web_dir}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
