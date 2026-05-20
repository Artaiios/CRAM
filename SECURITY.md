# Security Policy

CRAM (Crisis Role Availability Manager) is a single-file HTML application used by
IT security teams and crisis committees. This document describes the threat model,
how to report vulnerabilities, and recommended hardening for enterprise deployments.

---

## 1. Threat Model

CRAM is a client-side tool. All data lives in `localStorage`. There is no backend
owned by the project. Cross-device sync is explicit (sync code, QR, JSON file) or —
since V2.0 — through user-configured backends (S1 HTTP, S5 custom endpoint).

### In scope

- **XSS via user input.** Role names, person names, notes and other free-text fields
  are user-controlled. Mitigation: every `innerHTML` interpolation runs through
  `escapeHTML()` (308+ call sites at time of writing).
- **Data exfiltration following XSS.** Even if a `escapeHTML()` site were missed,
  the Content Security Policy in the HTML `<meta http-equiv>` blocks most
  exfiltration paths. `default-src 'none'`, no `'unsafe-eval'`, no remote scripts.
- **V2.0 auto-sync attack surface (new).**
  - Untrusted HTTP backend: a malicious S1/S5 endpoint can serve crafted ETags,
    crafted bodies, or non-2xx status. CRAM treats every response body as
    untrusted; it is validated (`SyncCryptoDetect`, JSON parsing, schema checks)
    before any `localStorage` write.
  - ETag tampering: ETags are opaque strings used for `If-None-Match` polling.
    An attacker controlling the backend can force unnecessary pulls but cannot
    forge state without also producing a valid encrypted bundle.
  - Backoff-DoS via 5xx storms: client-side backoff (jitter + cap) is RAM-only
    and resets on reload; a misbehaving backend cannot persistently disable
    sync. Visibility-driven polling stops when the tab is hidden.

### Out of scope

- **Physical device theft.** Disk encryption (FileVault, BitLocker, LUKS) is the
  customer's responsibility.
- **Compromised browser extension.** Any extension running in the same origin
  has full DOM access. CRAM cannot defend against this and does not try.
- **Compromised browser / OS.** Same reasoning.

---

## 2. Reporting Vulnerabilities

Report security issues by email to **patrick.zeller.ger@gmail.com**.

Please include:

- A description of the issue and the impact you observed.
- Reproduction steps (config snippet, click path, payload).
- Affected version (the `APP_VERSION` constant near the top of the main script
  block, or the GitHub release tag).
- Whether the issue is already publicly known.

### Response expectations

CRAM is maintained by a single developer in his spare time. Best-effort response
within **one week**. Critical issues (RCE, persistent XSS, crypto break) are
triaged ahead of feature work; lower-severity issues are scheduled.

There is **no bug bounty**. Researchers who report responsibly are credited in
the CHANGELOG and release notes if they wish.

### Coordinated disclosure

Default disclosure window: **90 days** from initial report to public disclosure,
matching industry norm. Shorter windows are negotiable for trivial fixes;
longer windows are negotiable for complex fixes. Public disclosure before a fix
is available is strongly discouraged but not prohibited.

---

## 3. CSP Hardening for Enterprise Deployments

The CSP shipped in `crisis-role-manager.html` is set via `<meta http-equiv>`. This
covers the air-gapped / file-system deployment path. When CRAM is hosted behind
a web server (intranet portal, S3+CloudFront, nginx, IIS, etc.), the same
policy should additionally be sent as an HTTP response header. HTTP headers
have stronger effect than meta tags (they apply earlier and cover directives
that meta tags cannot set).

### Directives that require an HTTP header

- **`frame-ancestors 'none'`** — cannot be set in a meta tag at all; browsers
  ignore it there. Required to prevent clickjacking via iframe embedding.
- **`X-Frame-Options: DENY`** — fallback for older browsers that pre-date
  `frame-ancestors`.

### Tighter `connect-src` for enterprise

The shipped policy is intentionally permissive on `connect-src` so users can
configure arbitrary S1/S5 backends without rebuilding the file:

```
connect-src 'self' blob: data: https: http://localhost:* http://127.0.0.1:*;
```

In an enterprise deployment where the backend URL is known and fixed,
restrict it:

```
connect-src 'self' https://sync.internal.example.com;
```

This removes the "any HTTPS" allowance and reduces the blast radius of a
compromised dependency or a misconfigured sync target.

### Example nginx snippet

```nginx
location /cram/ {
  add_header Content-Security-Policy "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' https://sync.internal.example.com; manifest-src 'self' blob:; media-src 'self' blob: data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none';" always;
  add_header X-Frame-Options "DENY" always;
  add_header Referrer-Policy "no-referrer" always;
  add_header X-Content-Type-Options "nosniff" always;
}
```

`'unsafe-inline'` for `script-src` and `style-src` remains. This is an
architectural constraint — the entire tool is one inline HTML file. Removing
it would require breaking the single-file principle.

---

## 4. Known Sanitization Limitations

CRAM stores network errors in the audit log to help diagnose sync failures.
Before storage, error messages pass through `_stripUrlsAndTokens()` (main
script block) which redacts:

- URLs (`https?://...` → `[url]`)
- Bearer tokens (`Bearer <value>` → `Bearer [token]`)
- Common query-string secrets (`?token=`, `?password=`, `?passphrase=`,
  `?secret=`, `?key=`, `?auth=` → `?[redacted]`)

### Not redacted (low risk today, documented for completeness)

- **HTTP Basic-Auth credentials** in URLs (`https://user:pass@host/...`).
  Today no CRAM code path constructs such URLs and no supported backend
  format requires them. If a future backend introduces Basic-Auth, extend the
  regex in `_stripUrlsAndTokens` before merging.
- **Cookie headers** in error messages. Modern `fetch()` errors do not
  expose `Cookie` or `Set-Cookie` content in `error.message`; this is
  documented prophylactically.
- **Custom proprietary headers** (`X-Api-Key`, `X-Auth-Token`, etc.) if a
  backend echoes them in an error body. CRAM only stores `error.message`,
  not response bodies, so the risk is low — but a misbehaving backend could
  put the header value into the error string.

### Mitigation if a new backend changes the risk profile

Extend `_stripUrlsAndTokens` to cover the additional pattern. Keep the regex
list short and commented; over-redaction makes audit logs useless for
debugging.

---

## 5. Cryptographic Discipline

V2.0 sync supports end-to-end encryption of the sync payload (default ON for
new sync sources). The implementation lives in the `SyncCrypto` IIFE inside
`crisis-role-manager.html`.

- **WebCrypto only.** No third-party crypto library, no hand-rolled primitives.
- **Key derivation:** PBKDF2-HMAC-SHA256, 250 000 iterations, 16-byte salt
  per sync source (generated on first encrypt, persisted in source config).
- **Encryption:** AES-256-GCM with a fresh 12-byte IV per message.
- **Passphrase lifecycle:** never written to disk. Held in a RAM-only
  `_passphraseCache` Map keyed by source ID. Cleared on reload.
- **Derived-key cache:** RAM-only `_keyCache`. Also cleared on reload.
- **Tokens (for HTTP-Basic / Bearer backends):** stored in the source config
  in `localStorage`. This is an accepted residual risk, mitigated by the CSP
  preventing exfiltration after XSS. Users who consider this unacceptable
  should not use the auto-sync feature and should rely on manual sync code /
  QR / JSON.

If a user forgets the passphrase, the encrypted payload on the backend is
unrecoverable by design. There is no recovery path and no backdoor.

---

## 6. Audit Status

V2.0 went through six independent internal audit passes before GA:

1. Security review (this domain).
2. Stability review (sync state machine, race conditions).
3. Mobile compatibility (iPhone Safari, iPad best-effort).
4. Resilience (offline / partial-connectivity behaviour).
5. Regression vs V1.3.0.
6. Documentation consistency (README, handbooks, PDFs, NOTICE, SBOM).

Twenty-five watch-points were recorded across the audits. All are either
already resolved or classified as nice-to-have for post-GA. None are
release blockers.

The systematic input-escaping verification described in CLAUDE.md as **S-02**
is the primary remaining structured security exercise. A penetration-test
configuration with deliberately malicious strings (`<img src=x onerror=...>`,
`"><script>...`, `javascript:`, Unicode-escaped variants) should be imported
into CRAM and every view exercised. Any future regression test for this lives
under the `tests/` directory once formalised.

---

## 7. Version Coverage

Security fixes are issued only for the latest released minor version. Older
versions are not patched; users on older releases should upgrade. The single
HTML file makes upgrades a download-and-replace operation with no migration
cost beyond opening the new file in the same origin.
