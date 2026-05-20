#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Patrick Zeller
#
# run-pen-test.sh — wrapper around tests/pen-test-s02.js
#
# Starts a tiny static file server in the repo root, runs the Node-based
# S-02 pen-test against http://127.0.0.1:8765, and shuts the server down
# regardless of outcome.
#
# Prerequisites:
#   - node (>= 18)
#   - npx playwright install chromium     (one-time, locally)
#
# Exit codes are propagated from pen-test-s02.js:
#   0  = all surfaces clean
#   1  = at least one XSS finding (release blocker)
#   2  = tooling missing or environmental failure (skip with reason)

set -u

PORT="${PORT:-8765}"
HOST="${HOST:-127.0.0.1}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if ! command -v node >/dev/null 2>&1; then
  echo "[skip] node not on PATH — install Node 18+ to run S-02."
  exit 2
fi

# Start a minimal static server (vanilla Node, no npm deps) serving
# the repo root so crisis-role-manager.html is reachable at the URL
# the test expects.
SERVER_LOG="$(mktemp -t cram-pen-test-server.XXXXXX)"
node - <<'NODESERVER' >"${SERVER_LOG}" 2>&1 &
const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = process.env.CRAM_REPO_ROOT;
const PORT = parseInt(process.env.PORT || '8765', 10);
const HOST = process.env.HOST || '127.0.0.1';
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.png':  'image/png',
  '.svg':  'image/svg+xml',
};
const srv = http.createServer((req, res) => {
  let url = decodeURIComponent((req.url || '/').split('?')[0]);
  if (url.endsWith('/')) url += 'index.html';
  const p = path.normalize(path.join(ROOT, url));
  if (!p.startsWith(ROOT)) { res.writeHead(403); return res.end('forbidden'); }
  fs.readFile(p, (err, data) => {
    if (err) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
    res.end(data);
  });
});
srv.listen(PORT, HOST, () => console.log('static server listening on http://' + HOST + ':' + PORT));
NODESERVER

SERVER_PID=$!
export CRAM_REPO_ROOT="${REPO_ROOT}"
export PORT HOST

cleanup() {
  if kill -0 "${SERVER_PID}" 2>/dev/null; then
    kill "${SERVER_PID}" 2>/dev/null || true
    wait "${SERVER_PID}" 2>/dev/null || true
  fi
  rm -f "${SERVER_LOG}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait briefly for the server to bind.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if curl -sf "http://${HOST}:${PORT}/crisis-role-manager.html" -o /dev/null; then
    break
  fi
  sleep 0.2
done

BASE_URL="http://${HOST}:${PORT}" node "${SCRIPT_DIR}/pen-test-s02.js"
RC=$?

exit "${RC}"
