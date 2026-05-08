#!/usr/bin/env python3
"""
CRAM dev sync backend — minimal HTTP server for testing V1.2 sync locally.

Listens on 127.0.0.1:8765. Stores state at scripts/dev-sync-state.json next
to this script. Pure Python stdlib, no install required.

Endpoints:
  GET     /cram/state.json     -> 200 with stored JSON, or 404 if empty
  PUT     /cram/state.json     -> 204, stores request body (JSON-validated)
  HEAD    /cram/state.json     -> 200 with Last-Modified + ETag, or 404
  OPTIONS /cram/state.json     -> 204 CORS preflight

CORS: Access-Control-Allow-Origin: * (any origin), Allow-Methods: GET, HEAD,
PUT, OPTIONS, Allow-Headers: Authorization, Content-Type, If-Match,
If-None-Match. Suitable for testing CRAM loaded from file:// or any origin.

NOT FOR PRODUCTION. No auth, no encryption, no rate limiting, no TLS. The
state file is overwritten on every PUT; nothing is durable beyond the file.

Usage:
  python3 scripts/dev-sync-backend.py
  python3 scripts/dev-sync-backend.py --port 9000
  python3 scripts/dev-sync-backend.py --reset

Stop with Ctrl+C.
"""

import argparse
import hashlib
import json
import sys
from email.utils import formatdate
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DEFAULT_PORT = 8765
ENDPOINT_PATH = '/cram/state.json'
STATE_FILE = Path(__file__).parent / 'dev-sync-state.json'

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, HEAD, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type, If-Match, If-None-Match',
    'Access-Control-Expose-Headers': 'ETag, Last-Modified',
    'Access-Control-Max-Age': '86400',
}


def compute_etag(body):
    return '"' + hashlib.sha256(body).hexdigest()[:16] + '"'


class CRAMSyncHandler(BaseHTTPRequestHandler):
    def _send_cors(self):
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)

    def _send_simple(self, status, body=b'', content_type=None):
        self.send_response(status)
        self._send_cors()
        if content_type:
            self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _state_metadata(self):
        if not STATE_FILE.exists():
            return None
        body = STATE_FILE.read_bytes()
        return {
            'body': body,
            'last_modified': formatdate(STATE_FILE.stat().st_mtime, usegmt=True),
            'etag': compute_etag(body),
        }

    def do_OPTIONS(self):
        if self.path != ENDPOINT_PATH:
            self._send_simple(404)
            return
        self._send_simple(204)

    def do_HEAD(self):
        if self.path != ENDPOINT_PATH:
            self._send_simple(404)
            return
        meta = self._state_metadata()
        if meta is None:
            self._send_simple(404)
            return
        self.send_response(200)
        self._send_cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(meta['body'])))
        self.send_header('Last-Modified', meta['last_modified'])
        self.send_header('ETag', meta['etag'])
        self.end_headers()

    def do_GET(self):
        if self.path != ENDPOINT_PATH:
            self._send_simple(404, b'Not found\n', 'text/plain')
            return
        meta = self._state_metadata()
        if meta is None:
            self._send_simple(404, b'State empty\n', 'text/plain')
            return
        self.send_response(200)
        self._send_cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(meta['body'])))
        self.send_header('Last-Modified', meta['last_modified'])
        self.send_header('ETag', meta['etag'])
        self.end_headers()
        self.wfile.write(meta['body'])

    def do_PUT(self):
        if self.path != ENDPOINT_PATH:
            self._send_simple(404, b'Not found\n', 'text/plain')
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            self._send_simple(400, b'Invalid Content-Length\n', 'text/plain')
            return
        if length <= 0:
            self._send_simple(400, b'Empty body\n', 'text/plain')
            return
        body = self.rfile.read(length)
        try:
            json.loads(body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            self._send_simple(400, f'Invalid JSON: {e}\n'.encode(), 'text/plain')
            return
        STATE_FILE.write_bytes(body)
        self._send_simple(204)

    def log_message(self, fmt, *args):
        sys.stderr.write(f'[{self.log_date_time_string()}] {fmt % args}\n')


def main():
    parser = argparse.ArgumentParser(description='CRAM V1.2 dev sync backend (testing only).')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'TCP port (default: {DEFAULT_PORT})')
    parser.add_argument('--reset', action='store_true', help='Clear stored state and exit')
    args = parser.parse_args()

    if args.reset:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
            print(f'Reset: removed {STATE_FILE}')
        else:
            print(f'Reset: nothing to remove ({STATE_FILE} did not exist)')
        return

    server = HTTPServer(('127.0.0.1', args.port), CRAMSyncHandler)
    print(f'CRAM dev sync backend listening on http://127.0.0.1:{args.port}{ENDPOINT_PATH}')
    print(f'State file: {STATE_FILE}')
    print('Ctrl+C to stop, --reset to clear state.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopping.')
        server.server_close()


if __name__ == '__main__':
    main()
