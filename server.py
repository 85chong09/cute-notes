#!/usr/bin/env python3
"""
简单的HTTP服务器，用于Tauri开发模式
"""
import http.server
import socketserver
import os
import sys

PORT = 1420

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'src'), **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run_server():
    os.chdir(os.path.dirname(__file__))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🍀 可爱便签开发服务器已启动")
        print(f"📍 地址: http://localhost:{PORT}")
        print(f"📁 目录: {os.path.join(os.path.dirname(__file__), 'src')}")
        print(f"🚀 现在可以运行: cargo tauri dev")
        print(f"=" * 50)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n👋 服务器已停止")
            sys.exit(0)

if __name__ == "__main__":
    run_server()
