import socketserver, http.server, os
os.chdir(os.path.join(os.path.dirname(__file__), "outputs"))
with socketserver.TCPServer(("", 8765), http.server.SimpleHTTPRequestHandler) as s:
    s.serve_forever()
