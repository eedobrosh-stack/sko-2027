#!/usr/bin/env python3
"""Local server for the sko_2027 spec form and results page. Stdlib only.

  python3 server.py [--port 7894]

GET  /                 form UI
GET  /api/spec         current spec.json (created from spec.example.json if missing)
POST /api/spec         save spec.json
GET  /api/candidates   <output_dir>/candidates.json (empty list if none yet)
POST /api/candidates   save candidates (used for the Approve checkboxes)
POST /api/launch       open Terminal running `claude "/sko_2027 run"` (macOS); else returns the command
"""
import json, os, shutil, subprocess, sys, argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "spec.json")
EXAMPLE = os.path.join(HERE, "spec.example.json")


def load_spec():
    if not os.path.exists(SPEC):
        shutil.copy(EXAMPLE, SPEC)
    with open(SPEC, encoding="utf-8") as f:
        return json.load(f)


def out_dir():
    d = os.path.expanduser(load_spec().get("output_dir") or "~/sko_2027_output")
    os.makedirs(d, exist_ok=True)
    return d


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False, indent=1)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def log_message(self, *a):
        pass

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            with open(os.path.join(HERE, "form", "index.html"), encoding="utf-8") as f:
                return self._send(200, f.read(), "text/html")
        if p == "/api/spec":
            return self._send(200, load_spec())
        if p == "/api/candidates":
            f = os.path.join(out_dir(), "candidates.json")
            data = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else []
            return self._send(200, data)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        p = self.path.split("?")[0]
        try:
            if p == "/api/spec":
                spec = self._body()
                with open(SPEC, "w", encoding="utf-8") as f:
                    json.dump(spec, f, ensure_ascii=False, indent=2)
                return self._send(200, {"ok": True, "path": SPEC})
            if p == "/api/candidates":
                data = self._body()
                f = os.path.join(out_dir(), "candidates.json")
                with open(f, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=1)
                return self._send(200, {"ok": True, "path": f})
            if p == "/api/launch":
                mode = (self._body().get("mode") or "run")
                cmd = f'claude "/sko_2027 {mode}"'
                if sys.platform == "darwin":
                    script = f'tell application "Terminal" to activate\ntell application "Terminal" to do script "cd ~ && {cmd.replace(chr(34), chr(92)+chr(34))}"'
                    subprocess.Popen(["osascript", "-e", script])
                    return self._send(200, {"ok": True, "launched": True, "command": cmd})
                return self._send(200, {"ok": True, "launched": False, "command": cmd})
        except Exception as e:  # noqa
            return self._send(500, {"error": str(e)})
        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=7894)
    a = ap.parse_args()
    load_spec()
    print(f"sko_2027 form: http://localhost:{a.port}   (spec: {SPEC})")
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
