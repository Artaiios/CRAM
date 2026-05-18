# Changelog

All notable changes to CRAM are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [semantic versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0-rc1] — 2026-05-18

Auto-Sync as a release candidate. V2.0 turns the V1.2/1.3 manual pull-push channel into a background poller that survives offline, hidden tabs, lost auth, lost permission, missing passphrase, and crash-mid-push — without ever silently replacing a stab configuration (V1.3 status/data split holds). Opt-in per source; default off.

### Added — Auto-Sync (V2.0 core)

- **SyncPoller (IIFE).** Per-source tick loop with `_register`/`_unregisterSource`. Visibility multiplier ×4 when the tab is hidden (D3). `online`/`offline` listeners suspend and resume the loop.
- **3-class error model.** `transient` → exponential backoff up to 16× `baseInterval`. `auth` (401/403) → flips `autoMode=off` and surfaces a persistent badge. `permission` (`NotAllowedError`, S5) → hard-pause.
- **Console classes.** `passphrase-required` (WP-16) and `concurrent` (412 retry cap) are tracked separately from the backoff variable so they cannot starve the recovery path.
- **Auto-push hook.** `Sync.markDirty()` schedules a push 2 s after the last edit (debounce); early-returns while `_needsRecovery` or `_waitingForPassphrase` is set so the UI spinner stays consistent.
- **`pendingPush` sentinel.** SHA-256 hash of the payload is persisted before the actual `PUT`. On boot, if the sentinel is still present, the recovery modal offers Retry or Discard (H3). The hash never appears in the UI and never leaves localStorage in plaintext form (WP-4).
- **If-Match ETag header (S1).** Lost-update protection on the HTTP backend; pre-read fetches the current ETag, push sends `If-Match: <etag>`, 412 triggers a fingerprint-aware retry with a hard cap.
- **Settings UI — Auto-Sync accordion.** Per-source: mode toggle (off / pull / push / bidirectional), polling-interval slider (30–300 s), live stats, four badges (`authError`, `permissionRequired`, `pendingPush`, `passphrase-required`).
- **Toast system with dedup.** Catch-up on tab focus after a 401, recovery modal on boot, transient-error coalescing.
- **Migration banner V1.3 → V2.** Opt-in per source, dismissible, idempotent (dual trigger: `schemaVersion < 2 || !state.auto`).

### Added — Mobile (iPhone gate)

- **iPhone Safari is a release-blocker platform.** Acceptance criteria M1–M3 in `docs/specs/v2.0-auto-sync.md`. New role `cram-mobile-qa-engineer`.
- **PWA installable.** Manifest now ships 192×192 and 512×512 PNG icons (Lighthouse green).
- **`env(safe-area-inset-top)` on `.app-header`** for Dynamic Island in PWA standalone mode.
- **44×44 pt tap targets** on migration-banner buttons, settings accordion controls, toast actions, source-row actions, header buttons (across all three breakpoints).

### Added — Spec & docs

- `docs/specs/v2.0-auto-sync.md` extended with resilience acceptance criteria H1–H5 (crisis gate) and mobile M1–M3 (iPhone gate).
- Structural consequences captured: 3-class error model, two independent backoff variables, hard-pause vs. soft-pause distinction.

### Changed

- `cram.sync.v1` schema bumped to version 2 (idempotent migration; dual-trigger on `schemaVersion < 2 || !state.auto`).
- `POLL_INTERVAL_MIN_SEC` defensive floor raised from 15 s to 30 s (Security Watch-Point 3).
- `Sync.addSource` / `Sync.removeSource` now call `SyncPoller._register` / `_unregisterSource` centrally — previously the wiring lived in UI wrappers and could be bypassed.
- Browser-compat matrix (local CLAUDE.md) extended with a Safari iOS 15+ column.

### Fixed

- **V1.3 regression — docs(en).** `stab` → `committee` consistency in the Online-Sync chapter.
- **Mobile F1 — Migration-banner buttons.** Raised from 23 px to 44 px on ≤600 px (HIG violation).
- **Mobile F2 — Settings modal source-card.** Horizontal overflow on iPhone SE (470 px content in a 373 px viewport) eliminated.
- **Mobile F3 — Header buttons.** 32/34/36 px → 44 px across all three breakpoints.
- **Mobile F4 — Source-row action buttons.** Share / Edit / Delete raised from 25 px to 44 px.
- **Step 4 polish — `scheduleAutoPush`.** Early-return on `_needsRecovery` and `_waitingForPassphrase` so the UI spinner does not flicker.
- **F2 — `Sync.pull()`.** `lastEtag` is now persisted only *after* `applyEnvelopeForSource` succeeds. Previous order opened a cache-poisoning vector: a malformed envelope could update the ETag and then bail.
- **F2b — `Sync.push()` pre-read.** Same pattern: persist `lastEtag` from the pre-read only after the local-vs-server fingerprint check passes.

### Security

- **WP-1 — `escapeHTML` discipline V1.3 → V2.** Call sites went from 485 to 530 (+45 for migration banner, accordion, toast surfaces).
- **WP-2 — `_stripUrlsAndTokens`.** URL, `Bearer <token>`, and query-string `token=`/`access_token=` stripping before `lastAutoPollError` is persisted (step 3). Same stripping applied to the `_onOnline` / `_onOffline` console.warn paths (step 7, WP-9).
- **WP-3 — `POLL_INTERVAL_MIN_SEC` defensive 30 s.** Resists tampered settings.
- **WP-4 — `pendingPush.payloadHash`.** SHA-256 hash, never plaintext, never rendered in the UI (verified in step-5 and step-6 reviews, Watch-Point 13).
- **WP-7 — `POLL_MODE='status'` constraint.** Enforced at every `Sync.pull` / `Sync.push` call inside the poller; full-mode is reachable only from the manual Data → Online tab.
- **WP-16 — Passphrase-required as its own error class.** Cannot be swallowed by the transient-error backoff.
- **25 Security Watch-Points** documented end-to-end across steps 1–7.

### Compatibility

V1.3 source configurations carry over without user action. AutoMode is **off** by default per source; users opt in explicitly. The wire envelope is unchanged. A V1.3 client running against a V2.0-pushed envelope behaves identically. V2.0 polling is status-only (V1.3 split holds) — a config drift is surfaced in the awareness indicator, never silently applied.

### Deferred — out of scope for RC1, in scope for RC2 / GA

- **S5 (File System Access) auto-push.** No ETag-equivalent API; lost-update protection there is left to user mitigation. Auto-pull on S5 works.
- **iPad smoke.** Not actively tested.
- **PDF handbooks.** Still reflect V1.0-rc1.3 content. Markdown handbooks under `docs/` are current.
- **Real iPhone smoke against a physical device.** Web-Inspector against Safari iOS is the GA gate; deferred to RC2.
- **WP-16 ZH-native review** of the passphrase-required i18n strings.
- **dev-sync-backend.py — If-Match validation.** Currently the local dev server does not enforce ETag preconditions; nice-to-have for two-tab smoke testing.

### Acceptance gates met

- Resilience H1–H5 (owner: `cram-resilience-engineer`)
- Mobile M1–M3 (owner: `cram-mobile-qa-engineer`)
- Security reviews steps 1–7 all clean

## [1.3.0] — 2026-05-13

Clean split between **Sync** (status-only, gated by configuration fingerprint match) and **Data** (full configuration + status, explicit confirm). Solves the silent-config-replacement risk that V1.2.1 worked around with an audit-log entry, and prepares the V2.0 auto-polling design so it can never accidentally overwrite a team's stab structure.

### Added

- **Sync API: mode parameter.** `Sync.push(sourceId, { mode })` and `Sync.pull(sourceId, { mode })` now accept `'status'` (default) or `'full'`. Status mode probes the server first and refuses the operation when the server's fingerprint does not match the local one (throws a typed `ConfigDriftError` so the UI can react). Status pulls apply only `inner.runtime`, leaving `State.config` alone. Full mode behaves as before and is used by the new Data-Online tab.
- **Sync.probeMeta / Sync.previewDiff.** Two new read-only methods. `probeMeta` returns the envelope metadata (version, timestamp, fingerprint, encrypted) without decrypting; `previewDiff` does the full comparison including counts per side (persons / levels / roles / absent / manual) and the lists of person IDs that exist only locally or only on the server. Both back the live preview cards.
- **Sync-Modal Online tab: preview cards.** Replaces the two flat buttons with one card per source that adapts to actual state — unreachable, empty, encryption-locked, decryption error, fingerprints match, fingerprints differ. When fingerprints match, the user sees a green pill and "Pull status" / "Push status" buttons. When they differ, status buttons are removed entirely and the card surfaces a single "Open Data → Online" button.
- **Data modal: new Online tab.** Third tab next to Export and Import. Same card layout as Sync's, but the active buttons always do a full pull or full push (`mode: 'full'`), with a `confirm()` dialog that summarises server-vs-local stats and warns the action cannot be undone. The Sync-Modal "Open Data" path lands here with the relevant source highlighted.
- **Awareness indicator: config-drift state.** Fifth visible state next to synced / syncing / out-of-sync / error. Rendered with a red ⚠ pill and made clickable — opens Data → Online directly. Detection runs off the shared previewDiff cache, so the indicator only flips after the user has actually inspected the server (no surprise polling).
- **Onboarding auto-pull after bundle import.** When a freshly imported sync bundle points at a server that already has state, the user is asked once whether to take that state immediately. Accepting runs a full pull and re-renders the chart; declining leaves the user to use Data → Online manually later.

### Changed

- `APP_VERSION` bumped to `1.3.0`.
- `Sync.push` / `Sync.pull` defaults changed to `mode: 'status'`. The wrappers `syncOnlinePull` and `syncOnlinePush` (kept for backward compatibility with any external callers) explicitly pass `mode: 'full'` to preserve V1.2 semantics; the new card UI uses `syncOnlinePullStatus` and `syncOnlinePushStatus` exclusively.
- Handbook chapters (DE + EN) extended with a "Sync vs. Data — what to use when" subsection covering typical workflows.

### Compatibility

V1.2 source configurations carry over without migration. The internal envelope wire format is unchanged (still `format: 'cram-sync-v1'`). A V1.2 client pulling from a V1.3-pushed envelope behaves identically because mode handling is receiver-side only. A V1.3 client running against a V1.2-only server simply sees status sync work when fingerprints match and bumps to Data → Online when they do not — no breaking error.

### Why this matters for V2.0

V2.0's polling-every-90-seconds was a security risk in the V1.2 design — a routine background pull could silently replace your stab configuration. With the V1.3 split, V2.0 auto-pull will only operate in status mode; a config drift surfaces as a visible indicator state, not as an automatic data loss.

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
