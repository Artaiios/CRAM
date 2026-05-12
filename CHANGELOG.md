# Changelog

All notable changes to CRAM are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [semantic versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] — 2026-05-12

Two bug fixes against the V1.2.0 surface, found in first practical use.

### Fixed

- **Online sync now correctly applies full configurations, not just status.** The leftover fingerprint-mismatch check in `applyEnvelopeForSource` (inherited from the sync-code channel, which is status-only) refused any pull where the server config differed from the local one — exactly the case the online-sync feature exists to handle. The check is removed for the online path; the receiver now accepts the server's full `config` and `runtime` as authoritative. A `sync_config_replaced` audit-log entry records every config-changing pull with the old and new fingerprints so the change stays traceable. The sync-code channel still enforces fingerprint match (status-only semantics).
- **Cascade arrows no longer clip when the org chart scrolls.** `.cascade-overlay` was sized with `width: 100%; height: 100%` in CSS, which resolves to the containing block (the relatively-positioned `#org-chart`'s padding-box) rather than the scroll-content box. Paths drawn beyond that area were rendered but visually cut off. The CSS sizing rules are removed; the SVG now uses the `width` and `height` attributes set by `renderCascadeLines()` to `chart.scrollWidth` and `chart.scrollHeight`, which include the full scrollable content. The bug pre-dated V1.2 — first reported and fixed now.

### Changed

- `APP_VERSION` bumped to `1.2.1`.

## [1.2.0] — 2026-05-12

Online synchronisation as a new transfer channel, manual mode. The previous three channels (sync code, QR transfer, JSON export/import) remain unchanged and continue to work as before. V1.2 adds a fourth: a server-or-folder-backed pull/push pair driven by two explicit buttons. V2.0 will automate it; V1.2 deliberately keeps the user in control of every operation.

### Added

- **Sync source abstraction.** A `Sync` module manages a list of configured sources with CRUD operations, version tracking, dirty flag, and a callback hook for the UI. Each source has a type, label, backend-specific config, and encryption settings. Stored under `cram.sync.v1` in localStorage.
- **Backend S1 — HTTP(S) endpoint.** Talks `GET` / `HEAD` / `PUT` / `OPTIONS` against any HTTPS server that supports those (nginx with `dav_methods`, Caddy + WebDAV plugin, Apache + `mod_dav`, MinIO, Synology NAS, SharePoint WebDAV). Auth types: `none`, `basic`, `bearer`. Reference configurations in [`docs/server-setup.md`](docs/server-setup.md).
- **Backend S5 — local directory (File System Access API).** User picks a folder once via the native browser picker; CRAM persists the directory handle in IndexedDB and writes the state file there on every push. Typical use: a OneDrive / Dropbox / Google Drive sync folder, where the vendor's desktop client distributes the file between devices without any server involved.
- **End-to-end encryption.** Default ON for new sources. PBKDF2-HMAC-SHA256 with 250 000 iterations derives an AES-256-GCM key from a user passphrase + 16-byte per-source salt. Each write uses a fresh 12-byte IV. Pure WebCrypto, no external library. Passphrase lives in RAM only and is discarded when the tab closes.
- **Sync-bundle share / import.** Onboards a second device against the same source. A `SyncBundle` JSON object carries source type, label, config, encryption salt, and passphrase. Distributed via JSON text or file (QR channel deferred). Receivers see a preview with a fingerprint comparison before confirming.
- **Settings tab "Sync sources"** with CRUD UI: add HTTP source, add local-directory source, edit, share, delete. Form validates URL prefix, filename pattern, passphrase length (≥ 8) and match-confirm on creation.
- **Sync modal: new "Online" channel** next to Code and QR. Lists every configured source with a Pull and a Push button, plus a last-synced line (version + timestamp) for the most recently used source. Empty state offers a direct shortcut to Settings → Sync sources.
- **Awareness indicator in the header.** A compact pill left of the existing stab-status metrics, showing one of: ✓ synced, ↻ syncing, ↑ out-of-sync (local changes pending push), ✗ error. Hidden when no sources are configured. Reactive via a `Sync.onChange` subscription; tooltip carries source label, version, and a relative timestamp via `Intl.RelativeTimeFormat`.
- **Browser support banner** in the Sync sources tab, automatically shown when the current browser is missing one of the V1.2 APIs (File System Access, BarcodeDetector). Adapts its lead sentence to Firefox / Safari / generic.
- **Dev sync backend** (`scripts/dev-sync-backend.py`): a minimal stdlib-only Python HTTP server on `127.0.0.1:8765` that simulates a real backend (GET / HEAD / PUT / OPTIONS with full CORS) for local testing. Not for production.
- **Server-setup documentation** (`docs/server-setup.md`): reference configurations for nginx with `dav_methods`, Caddy with the webdav community plugin, Apache with `mod_dav`, MinIO with presigned URLs, plus CORS requirements, auth options, TLS notes, and scaling expectations.
- **Handbook chapters** in DE and EN covering the user-side flow: add a source, manual pull / push, share a bundle, common failure modes.
- **CSP relaxation.** `connect-src` extended from `'self' blob: data:` to additionally allow `https:` (for production HTTPS endpoints) and `http://localhost:* http://127.0.0.1:*` (for local development). Documented as a deliberate second-layer trade-off; `escapeHTML` remains the first line of XSS defence and the URL of each source is matched against the configured-sources list before any fetch.

### Changed

- `APP_VERSION` bumped to `1.2.0`.
- `Storage.set()` now calls `Sync.markDirty()` when `cram.config.v1` or `cram.runtime.v1` is written, so the awareness indicator switches to "out of sync" on every local edit without touching the callers.

### Compatibility

The new "Local directory" source type and the QR scanner both require browser APIs that Firefox does not implement. HTTP-based online sync, encryption, and bundle import work in every modern browser. Safari requires re-granting file-system permission per session; Chrome and Edge persist it.

### Deferred

- **QR channel for sync bundles** (rendered as scannable QR codes). The existing JSON-text and file channels cover the practical need for V1.2. QR will be added in a follow-up commit reusing the existing fragmentation pipeline if practice demands it.
- **S2 backend — S3-style presigned URLs.** Originally planned for V2.1 because URL rotation (7-day max for AWS sigv4) does not fit the "set and forget" promise of the awareness indicator. Customers needing this today can use the HTTP backend against MinIO with manually refreshed presigned URLs.
- **PDF user manuals** for V1.2 were not rebuilt in this release. The Markdown handbooks under `docs/` are the source of truth and have been updated; the previously bundled PDFs still reflect rc1.3 content. PDFs will be regenerated in a follow-up release.

### Security model unchanged

The S-02 audit conducted before v1.0.0 remains valid for the V1.2 surface — the new modals all flow through the same `escapeHTML()` discipline, and `innerHTML` is not introduced in any new code path that takes raw user input without escaping. Encryption is layered on top of the existing input-escaping defence, not as a replacement.

## [1.0.0] — 2026-05-08

First stable release. Functionally identical to `1.0.0-rc1.3`; the rc cycle (rc1 → rc1.3) added compliance, security, and documentation polish without changing user-visible behaviour. After several weeks of practice testing, the tool is considered ready for production use.

### Security audit completed (S-02)

A penetration-test configuration with deliberately malicious payloads — `<img onerror>`, `<script>`, `<iframe javascript:>`, `<svg onload>`, HTML-entity-encoded scripts, `javascript:` URLs in href, CSS-injection attempts, and special characters — was imported and rendered through every user-facing view: organisation chart, all sidebar tabs (Roster, People, Log), person detail, mark-unavailable modal, manual-assignment modal, edit-mode CRUD for both persons and roles, all three print variants (Overview, Role detail, People list), all three sync channels (Code, QR, JSON), and the Settings modal. **No payloads executed in any rendering location.** The 308 `escapeHTML()` calls across 55 `innerHTML=` sites are confirmed consistent. The pen-test configuration itself is kept locally and is not part of the repository.

`tel:` and `mailto:` href attributes were specifically reviewed: the protocol prefix is hardcoded, so user-controlled values cannot redirect the protocol to `javascript:`. The browser sandboxes both protocols against script execution.

### Changed

- `APP_VERSION` bumped to `1.0.0`.

### What is next

The next development phase is documented in [`ROADMAP.md`](ROADMAP.md):

- **V1.2** introduces a sync-source abstraction with HTTP and File System Access API backends, optional E2E encryption, and explicit pull/push operations. Detailed spec in [`docs/specs/v1.2-manual-sync.md`](docs/specs/v1.2-manual-sync.md).
- **V2.0** adds the automation layer (auto-polling, auto-push, conflict resolution) on top of the V1.2 architecture. Spec in [`docs/specs/v2.0-auto-sync.md`](docs/specs/v2.0-auto-sync.md).

## [1.0.0-rc1.3] — 2026-04-19

Security and compliance release. No functional feature changes; the tool behaves identically to rc1.2.

### Added

- **Content Security Policy** (S-01) as a `<meta http-equiv>` tag in the HTML head. Allows only inline scripts (required for the single-file architecture) and inline styles, plus `data:` / `blob:` URIs for images, fonts, manifest, and media. Blocks all external script, style, font, and connection sources. Note: `frame-ancestors` cannot be set via meta — servers hosting CRAM should additionally set `X-Frame-Options: DENY` or `Content-Security-Policy: frame-ancestors 'none'` as an HTTP header.
- **Full MIT licence texts** for the two embedded libraries (L-01). Previously only short attribution comments were present; this violated the MIT licence's requirement to reproduce the licence text in all distributions. Licence texts now appear both as `/*! ... */` comment blocks directly above each library's code in `crisis-role-manager.html` and in the `NOTICE` file.
- **SPDX headers** in `crisis-role-manager.html` (L-03): `SPDX-License-Identifier: Apache-2.0` and `SPDX-FileCopyrightText: 2026 Patrick Zeller` as HTML comments directly after `<!DOCTYPE html>`. Enables automated compliance tools (scancode, reuse, SBOM generators) to detect the licence without human interpretation.
- **CycloneDX 1.5 SBOM** (L-04) as a release asset (`cram-sbom.cdx.json`). Lists CRAM itself plus both embedded libraries with purl, SHA-256 hash, and SPDX licence identifiers. Ready for ingestion into tools like OWASP Dependency-Track or DefectDojo.
- **Version-pin rationale** for qrcode-generator (L-02): explicit code comment explaining why CRAM stays on 1.4.4 rather than upgrading to 2.0.x. Summary: the 2.0 series adds TypeScript typings that do not apply to our vanilla-JS use case; the runtime API is unchanged; stability over novelty.

### Removed

- **External Google Fonts dependency.** Previously `crisis-role-manager.html` pulled IBM Plex Sans and IBM Plex Mono from `fonts.googleapis.com` on every load. This contradicted the offline-first architecture and would have forced the CSP to whitelist external style sources. The CSS font-family stacks now fall back through `-apple-system`, `Segoe UI`, `system-ui`, and generic families — robust on every platform.

### Changed

- `APP_VERSION` bumped to `1.0.0-rc1.3`.

### Security impact summary

With rc1.3, a successful XSS injection that somehow bypassed CRAM's input escaping would still be contained: the browser would refuse to load external scripts, exfiltrate data to third-party URLs, or execute `eval()`-based payloads. CSP is the second defence layer behind the existing `escapeHTML()` routine. The third layer — systematic verification of every `innerHTML` site — is tracked as S-02 and is the primary remaining security item before v1.0.

## [1.0.0-rc1.2] — 2026-04-19

Documentation release. No functional changes to the tool itself beyond the version string.

### Added

- Complete **visual legend** in README, both Markdown handbooks, and both PDFs. Covers every colour-coded signal the tool uses: role card states (primary green, substitute yellow, deeper substitute dark orange, unoccupied red, critical pulsing), manual assignment markers (purple solid border with lock icon, purple dashed for manually-assigned-but-absent), cascade arrow colours and why the target role determines the colour, header status pills, and sidebar accents.

### Changed

- `APP_VERSION` bumped to `1.0.0-rc1.2`.
- Cascade description in documentation was previously misleading — said "red dashed arrows" while in reality arrows are yellow for non-critical and red for critical cascades. Now accurate.

## [1.0.0-rc1.1] — 2026-04-19

Documentation release. No functional changes to the tool itself beyond the version string.

### Fixed

- Screenshot filenames in `docs/screenshots/` now match what each image actually depicts. The original filenames were guessed from upload timestamps; several did not match their content, causing the README to show the wrong dialog for several sections.

### Added

- German user manual PDF (`CRAM-Anwenderhandbuch.pdf`) as a release asset. Same structure and layout as the English version, translated to German.

### Changed

- `APP_VERSION` bumped to `1.0.0-rc1.1` so the Settings → About value matches the release tag.

## [1.0.0-rc1] — 2026-04-19

First release candidate. Feature-complete, pending field validation before a final 1.0 tag.

### Added

- **Role and substitution management** — hierarchical levels, roles with ordered substitution chains, a critical-role flag, and descriptive metadata for each role.
- **Availability tracking** — mark individuals as unavailable with a reason category (holiday, sick, travel, unreachable, other) and an optional note. The cascade re-resolves automatically.
- **Manual assignments** — pin a specific person to a role, overriding the automatic substitution logic. Marked with a 🔒 badge.
- **Five-language interface** — German, English, Spanish, French, Chinese. The selected language persists between sessions.
- **Print and PDF output** — three layout variants (Overview, Role detail, People list), three paper sizes (A4, A3, Letter), both portrait and landscape. Typography scales with paper size.
- **Sync code** — telephone-transferrable alphanumeric code for exchanging runtime state (absences and manual assignments) between two CRAM instances with identical base configuration. Protocol version 2, backward-compatible with v1 codes.
- **QR transfer** — send configuration and/or runtime state across nearby devices. The sender generates one or more QR codes (data is compressed with gzip before fragmentation); the receiver scans them with the camera. Works offline.
- **JSON export / import** — full configuration export with optional runtime state, structured validation on import, diff preview before applying.
- **30-day audit log** — ring-buffer log of all configuration edits, availability changes, sync operations, and imports. Accessible via the side panel.
- **Customisable titles** — organisation name and print title can be overridden in Settings. Defaults fall back to a localised crisis committee title per language.
- **Organisation chart visualisation** — SVG-rendered roles with Bezier-curve cascade lines showing current substitution flow when a role is held by someone other than the primary.
- **Responsive layout** — dedicated mobile layout with bottom navigation for phones, adaptive behaviour for tablets and narrow desktops, four size steps (S, M, L, XL) for scaling the main view.
- **PWA support** — inline Web App Manifest, installable on Android, iOS, and desktop browsers. Runs standalone after installation.
- **Dark and light themes** — manual toggle in the header, preference persists.

### Known limitations

- QR scanning requires a browser with the native `BarcodeDetector` API (Chrome, Edge, Safari). Firefox users can still generate QR codes but cannot scan them; use JSON import as an alternative.
- Camera access from mobile browsers requires HTTPS; `file://` does not work on mobile Safari or Chrome Android.
- Configuration changes must be propagated explicitly. There is no cloud sync or server component.
- The overview print variant may overflow A4 landscape for configurations with 30+ roles. A3 accommodates this without issue.

### Third-party components

- [fflate](https://github.com/101arrowz/fflate) 0.8.2 (MIT, Arjun Barrett) — gzip compression for QR transfer.
- [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) 1.4.4 (MIT, Kazuhiko Arase) — QR code matrix generation.

Both libraries are inlined in the HTML file. No external resources are loaded at runtime.

---

## Pre-1.0 history

Versions 0.1 through 0.15.1 were internal development builds and are not tagged as releases. Highlights of that period, for context:

- **0.15** — QR-based configuration transfer with multi-fragment support and camera scanning.
- **0.14** — QR send UI with scope picker (config, status, or both) and fragment navigation.
- **0.13** — Sync code V2 extended to carry manual assignments alongside absences.
- **0.12** — Customisable organisation name and print title.
- **0.11** — Print and PDF output in three layout variants.
- **0.10** — Mobile layout with dedicated bottom navigation.
- **0.9** — PWA packaging with inline manifest and icon.
- **0.8** — Five-language interface.
- **0.7** — Event delegation refactor, data import/export with validation.
- **0.6** — Audit log with ring buffer.
- **0.5** — Sync code V1 for telephone-based status exchange.
- **0.4** — Cascade visualisation with SVG Bezier curves.
- **0.3** — Edit mode with full CRUD for levels, roles, and persons.
- **0.2** — Priority-based occupancy resolution with strict-higher-priority rule.
- **0.1** — Initial prototype.
