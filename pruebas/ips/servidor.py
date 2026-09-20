from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class AplicacionLaboratorio(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        cuerpo = b"aplicacion protegida operativa\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)


ThreadingHTTPServer(("0.0.0.0", 8080), AplicacionLaboratorio).serve_forever()
