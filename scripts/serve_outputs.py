#!/usr/bin/env python3
"""Serve a folder on localhost with HTTP Range support, so review pages with
<video> tags play and seek in a browser pane.

Why this exists: a review board opened as a file (file://...) in an embedded
browser pane often cannot load its relative video files, and a page handed over
as a sandboxed snapshot cannot either. `python3 -m http.server` answers every
video request with the whole file and no Range support, and Chromium's player
needs ranges (206 Partial Content) to start and seek an mp4. This server
answers Range requests with 206 and byte slices, and everything else exactly
like the standard library server.

Usage:
  python3 scripts/serve_outputs.py                     serves ./outputs on 4200
  python3 scripts/serve_outputs.py --root outputs --port 4200
  python3 scripts/serve_outputs.py 4300                port as a bare number
  python3 scripts/serve_outputs.py --selftest          offline proof of the 206

Then open http://localhost:4200/<path under the root>. It binds to 127.0.0.1
only, so nothing on your network can reach it. Note that a hidden browser pane
usually pauses media, so "the video loaded" is the check you can automate and
"the video plays" is the one you watch.
"""
import argparse
import os
import re
import sys
import tempfile
import threading
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        rng = self.headers.get("Range")
        if not rng or os.path.isdir(path) or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        size = os.path.getsize(path)
        if not m or (m.group(1) == "" and m.group(2) == ""):
            return super().send_head()
        a, b = m.group(1), m.group(2)
        if a == "":
            start, end = max(0, size - int(b)), size - 1
        else:
            start, end = int(a), min(int(b) if b else size - 1, size - 1)
        if start >= size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return None
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        n = getattr(self, "_remaining", None)
        if n is None:
            try:
                return super().copyfile(source, outputfile)
            except (BrokenPipeError, ConnectionResetError):
                return None
        try:
            while n > 0:
                buf = source.read(min(1 << 20, n))
                if not buf:
                    break
                outputfile.write(buf)
                n -= len(buf)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the player cancels ranges it no longer needs
        finally:
            self._remaining = None

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


def make_server(root, port):
    return ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=root))


def selftest():
    with tempfile.TemporaryDirectory() as td:
        data = bytes(range(256)) * 40          # 10240 bytes
        with open(os.path.join(td, "clip.mp4"), "wb") as fh:
            fh.write(data)
        srv = make_server(td, 0)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{port}/clip.mp4"
        ok = True

        def get(rng=None):
            req = urllib.request.Request(base, headers={"Range": rng} if rng else {})
            try:
                with urllib.request.urlopen(req) as r:
                    return r.status, r.headers, r.read()
            except urllib.error.HTTPError as e:
                return e.code, e.headers, b""

        cases = [
            (None, 200, data),
            ("bytes=0-99", 206, data[:100]),
            ("bytes=10000-", 206, data[10000:]),
            ("bytes=-50", 206, data[-50:]),
            ("bytes=99999-", 416, b""),
        ]
        for rng, want_status, want_body in cases:
            status, headers, body = get(rng)
            good = status == want_status and body == want_body
            if rng and want_status == 206:
                good = good and headers.get("Content-Range", "").startswith("bytes ")
            print(f"{'PASS' if good else 'FAIL'}  Range {rng or 'none'}: {status}, {len(body)} bytes")
            ok = ok and good
        srv.shutdown()
        srv.server_close()
    print("\nselftest:", "all pass" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Serve a folder with HTTP Range support.")
    ap.add_argument("port_pos", nargs="?", type=int, help=argparse.SUPPRESS)
    ap.add_argument("--root", default="outputs", help="folder to serve (default ./outputs)")
    ap.add_argument("--port", type=int, default=4200, help="port (default 4200)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    port = args.port_pos or args.port
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"no such folder: {root}")
        return 1
    print(f"serving {root} at http://localhost:{port}/  (Ctrl-C stops it)")
    try:
        make_server(root, port).serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
