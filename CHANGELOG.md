# Changelog

All notable changes to CRAM are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [semantic versioning](https://semver.org/spec/v2.0.0.html).

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
