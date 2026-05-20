# CRAM — Crisis Role Availability Manager

A single-file web application for managing crisis committee roles and substitution chains. Built for IT security teams, business continuity managers, and anyone who needs to know at a glance who is currently available for a given role when a real incident hits.

Runs entirely in the browser. No server, no database, no external dependencies at runtime. Works offline after the first page load and can be installed as a progressive web app.

![Main view — Enterprise demo configuration, chart of all roles across levels with the right-hand sidebar](docs/screenshots/01-main-chart-overview.png)

> Screenshots show the included Enterprise demo configuration (`cram-demo-enterprise-en.json`) with placeholder names. Real organisational data is never shown.

## What it does

- Define a **hierarchy of roles** organised in levels (for example: strategic committee → department leads → team leads → operational experts)
- Assign **multiple substitutes per role** in a clear order of succession
- Mark people as **unavailable** (holiday, sick, business trip, active elsewhere, other) and see the substitution chain take over automatically
- Visualise the flow with **cascade lines** that show where a substitute is actively covering for someone else on a different level
- **Override** an automatic assignment when a specific person must hold a role regardless of availability
- **Print paper versions** of the roster — in three different layouts, sized for A4, A3 or Letter, portrait or landscape
- **Transfer state between devices** via four independent channels, each for a different realistic situation:
  - A short code read over the phone for quick status updates
  - QR codes for full configuration transfer between nearby devices
  - JSON export/import for archival or e-mail distribution
  - Online sync against a shared HTTP backend or a local sync folder — manual (V1.2) or automatic in the background (V2.0)
- Define **team pools** under any lead role (V2.1) — a fourth tier for on-call rotations, specialist teams, or extended response groups, with per-member availability tracking
- Tag people with **free-form keywords** (V2.1) — "SOC Tier 2", "macOS forensics", "cloud reverse engineering" — and search across the directory by name, keyword, phone, or e-mail
- Keep a **30-day audit log** of every change that the committee can review after an incident

## Why it exists

Most crisis management tools are either heavyweight enterprise platforms (SAP, ServiceNow modules, dedicated BCM suites) or simple spreadsheets. The former take months to roll out and require IT ownership; the latter fall apart the moment two people edit them at the same time.

CRAM sits between those extremes. It is deliberately small, opinionated about the data model (hierarchical roles with ordered substitutes), and designed to work in the conditions where crisis tools tend to fail: on whatever device you happen to have with you, possibly offline, possibly under stress, possibly with network infrastructure that is itself part of the incident.

## Installation

Download the latest release from the [Releases page](https://github.com/Artaiios/CRAM/releases), open `crisis-role-manager.html` in any modern browser, and you're running.

For a better experience, install it as a progressive web app:
- **Chrome/Edge Desktop**: Click the install icon in the address bar
- **Chrome/Android**: Menu → "Add to Home screen"
- **Safari/iOS**: Share → "Add to Home Screen"

After installation, CRAM launches in its own window, without the browser chrome, and retains its state between sessions on the same device.

## Quick start

1. Open `crisis-role-manager.html`. The default configuration contains a small example committee.
2. Click the edit icon (✎) in the header to enter edit mode.
3. Click ⚙ **Settings** to set your organisation name and the title that should appear on printouts.
4. Add or modify roles, persons, and assignments. The organisation chart updates in real time.
5. Leave edit mode and click on any person in the chart to mark them as unavailable. Watch the substitution chain take effect.
6. Click 🖨 **Print** to generate a paper copy — choose the layout variant and paper size.
7. Use ⇄ **Sync** to transfer state to another instance of CRAM running on another device.

A comprehensive user and administrator handbook is available in [English](docs/handbook-en.md) and [German](docs/handbook-de.md).

## Demo configurations

Two large sample configurations are included for testing and demonstration. Each has 100 persons, 40 roles across 7 levels, and realistic crisis committee structures for a multinational enterprise:

- [`demo/cram-demo-enterprise-en.json`](demo/cram-demo-enterprise-en.json) — English role names and descriptions
- [`demo/cram-demo-enterprise-de.json`](demo/cram-demo-enterprise-de.json) — German role names and descriptions

Both contain the same 100 people with international names from all continents (Europe, the Americas, Africa, China, India, the rest of Asia, the Middle East, Oceania). Import via the Data (⇵) → Import panel.

## Core concepts

### Role hierarchy

Roles live inside **levels**. A level is a conceptual grouping — "Executive Board", "Department Heads", "Technical Experts". Each role has a name, a description, a **critical** flag, and a list of **assignments**.

### Assignments and the substitution chain

An assignment ties a person to a role at a given rank. Rank 0 is the primary; ranks 1, 2, 3... are substitutes in order of succession.

When the app resolves who is currently holding a role, it walks the chain:
- If the primary is available, the role is filled by the primary.
- If the primary is unavailable, the first available substitute takes over.
- If no one in the chain is available, the role is flagged as uncovered.

Each role card shows its complete chain at the bottom, with struck-through names indicating who is currently unavailable. When a substitute has actually taken over, the card is annotated with `Replacing: <original primary>`.

![Main view with people sidebar — primary occupants and chains visible per role](docs/screenshots/03-main-view-with-people-sidebar.png)

### Cascade visualisation

When one person covers for another on a different level, CRAM draws an animated dashed arrow between the affected role cards. This makes it immediately visible which chains are actively being exercised — useful when the committee is briefing and needs to know at a glance which positions are under substitution stress.

![Cascade visualisation — yellow arrows trace where substitutes are actively covering for absent primaries](docs/screenshots/06-cascade-visualization.png)

### Visual legend

CRAM uses colour and animation to convey the current state of every role and cascade. The full legend:

**Role card left border — the role's current state:**

| Colour | State | Meaning |
|---|---|---|
| Green | Primary | The planned primary occupant is active |
| Yellow | Substitute (Sub1) | The first substitute has taken over |
| Dark orange | Substitute (Sub2 or deeper) | A second-tier or later substitute is active |
| Red | Unoccupied | No one in the chain is available |
| Red + pulsing | Unoccupied + critical | No one available for a critical role — needs attention |

**Role card border and surroundings — special conditions:**

| Signal | Meaning |
|---|---|
| Purple solid border + 🔒 badge | Role currently has a manual assignment in effect |
| Purple dashed border + struck-through name | Role was manually assigned to someone who has since become unavailable |
| Yellow outline around card | Card is part of a non-critical cascade (either source or target) |
| Yellow outline + glow | Cascade target that is non-critical — this is where the substitute is actively standing in |
| Red outline around card | Card is part of a cascade into a critical role |
| Red outline + glow | Cascade target on a critical role |
| Dimmed (50% opacity) | Cascade view is active and this card is not involved in any cascade |

**Cascade arrows (only visible while cascade view is enabled):**

| Colour | Animation | Meaning |
|---|---|---|
| Yellow dashed | Slow flow | Substitution into a non-critical role |
| Red dashed, thicker | Faster pulse with red glow | Substitution into a **critical** role — watch this carefully |

The arrow colour is determined by the **target role** (where the person is standing in), not the person's home role. A green-sub-filling-a-red role produces a red arrow; a red-primary-covering-a-green role produces a yellow arrow.

**Header status pills — system-wide state:**

| Colour | Meaning |
|---|---|
| Grey (neutral) | Informational count, no action required |
| Yellow outline | Active but non-critical condition — substitutes have stepped in |
| Red + pulsing | At least one critical role is unoccupied — attention required |

**Sidebar accents:**

| Element | Colour | Meaning |
|---|---|---|
| Roster entry, left border | Green | Role held by primary |
| Roster entry, left border | Yellow | Role held by substitute |
| Roster entry, left border | Dark orange | Role held by deeper substitute |
| Roster entry, left border | Red | Role unoccupied |
| People list entry, left border | Yellow | Person is currently unavailable |

### Manual assignments

Sometimes the automatic rule isn't what you want. A manual assignment pins a specific person to a role regardless of availability — useful during an actual incident when the primary might be available but unfit for this particular task, or when a substitute has been specifically drafted in.

![Manual assignment in effect — role card carries the lock badge and the pinned person's name](docs/screenshots/08-manual-assignment-active.png)

Manual assignments are marked with a 🔒 badge on the role card and persist until cleared. They are included in sync transfers.

### Team pools, keywords, and search (V2.1)

Below the classic three-tier hierarchy (Krisenstab → Management → Topic-Lead) CRAM supports a fourth tier: **team pools**. A pool is a group of employees attached to a lead role — useful for on-call rotations, specialist teams, or extended response groups that report into a lead but are not formal substitutes themselves.

- A pool member can simultaneously appear in the lead's substitution chain. A `[SUB]` badge in the chart surfaces that overlap.
- Pools render directly under their lead role on desktop (≥ 1024 px, V2.1.1 layout) and as collapsible level-end blocks on tablet and mobile.
- Pools are created and edited from the chart in edit mode (`+ Pool` button per column, `✎`/`×` on the pool header). A bulk-edit list also exists under Settings → Pools.
- If the lead role is deleted, the pool is preserved as **orphaned** in a dedicated section at the end of the chart — no cascade delete.

Each person carries a free-form list of **keywords** (max 32 per person, 64 characters each). Keywords are stored as chips with autocomplete and surface in the new **sidebar Search tab** (between People and Log; fifth nav button on mobile). Search matches name, keyword, phone, and e-mail; filters cover availability and keyword cloud (AND logic). Hit cards show roles (primary/sub), pool membership, and keyword chips, and click through to the person-edit modal.

**Sync note:** pool and keyword changes belong to the **configuration**, not the status. The status-mode fingerprint deliberately ignores them — distribute pool/keyword updates via a data-mode sync (JSON, QR, or Online-Data).

> Current screenshots show the V2.0 UI without pools. A screenshot refresh from a demo configuration is planned for a follow-up release; the text descriptions above reflect the V2.1.1 behaviour.

### Status vs configuration

CRAM makes a clear distinction:

- **Configuration** is the static structure — who is in the directory, what roles exist, who substitutes whom. Changes infrequently, typically a few times a year.
- **Status** is the dynamic state — who is currently unavailable, which manual assignments are active. Changes constantly during an incident.

This separation matters because the two types of data have different transfer channels. A 30-second phone call can synchronise status across a dozen devices. Configuration needs a QR scan or a file exchange.

## Transfer channels

| Channel | What | Offline? | Typical use |
|---|---|---|---|
| Sync code | Status only | Yes | Phone call, chat, radio |
| QR transfer | Configuration, status, or both | Yes | Same room, no network |
| JSON export / import | Configuration, status, or both | Yes | E-mail, file share, archive |
| Online (V1.2+) | Configuration + status, encrypted | No | Distributed team, regular reconciliation |

### Sync code

A short alphanumeric code — typically 20 to 40 characters — that encodes the current availability of all persons plus any manual assignments. The sending instance generates the code; the receiving instance enters it. Both instances must share the same base configuration (verified by a 4-character fingerprint).

![Sync code send view with fingerprint and people statistics](docs/screenshots/16-sync-code-send.png)

### QR transfer

For transferring full configurations, the sender generates one or several QR codes (compressed and encoded in fragments). The receiver activates their camera, holds it up to the sender's screen, and the fragments are collected and reassembled automatically.

![QR transfer send view — scope picker and generated QR code](docs/screenshots/17-sync-qr-send-options.png)

Works offline, device to device. Requires a modern browser with the native barcode detection API (Chrome, Edge, Safari); Firefox users need to fall back to JSON file import.

### JSON export

A conventional JSON file with the full configuration and optionally the current runtime state. Useful for:
- Archiving the committee structure as of a specific date
- Sharing configuration with a colleague via e-mail
- Version-controlling the crisis committee definition in your documentation system
- Seeding a fresh CRAM instance on a new device

![Data export dialog with scope and runtime-state toggle](docs/screenshots/19-data-export.png)

### Online sync (V1.2+)

For ongoing reconciliation across a distributed team. Unlike the channels above, online sync does not require live contact between sender and receiver — everyone pushes their state to a shared endpoint and pulls the combined state from there.

Two backend types are supported:

- **HTTP endpoint** — a self-hosted location (nginx with `dav_methods`, Caddy + WebDAV plugin, SharePoint WebDAV, MinIO, Synology NAS). Server-side setup snippets in [`docs/server-setup.md`](docs/server-setup.md).
- **Local directory** — typically a folder synchronised by OneDrive / Dropbox / Google Drive. CRAM writes the file; the vendor's desktop client handles distribution. No new server required.

End-to-end encryption is enabled by default (AES-256-GCM with PBKDF2). The passphrase is never persisted — recipients re-enter it after a browser restart. Sources can be onboarded onto other devices by sharing a **sync bundle**: a JSON object that carries URL or filename, auth data, salt, and passphrase. Distribute the bundle over a secure channel (Signal, password manager, in-person) — never in plain email or chat.

**Manual sync (V1.2/V1.3):** two buttons in the Sync modal — Pull and Push. Status-only by default; structural changes go through Data → Online with an explicit confirmation.

**Automatic sync (V2.0, opt-in):** per source, the user can switch on a background poller with one of four modes — `off`, `pull` (poll only), `push` (push on local edits only), or `bidirectional`. Polling interval is configurable between 30 and 300 seconds. The header indicator shows a live countdown to the next tick. ETag-based If-Match guards against lost updates on HTTP backends; conflicts get one Pull-Merge-Push retry. Tab visibility, offline events, auth errors, missing passphrase, and lost file-system permission each have their own pause/resume behaviour — the poller does not retry blindly. Config drift (server has a different committee structure) surfaces as a separate error class and routes the user to Data → Online for an explicit decision.

![Settings → Sync sources — per-source Auto-Sync mode, polling interval, encryption status](docs/screenshots/14-settings-sync-sources-tab.png)

For end-user step-by-step instructions, see [docs/handbook-en.md](docs/handbook-en.md#online-sync-since-v12).

## Print / PDF

Three variants, each sensibly sized for the chosen paper:

- **Overview** — a one-page wall chart. Roles grouped by level, each showing its primary occupant and phone number in large type. Critical roles are marked in red.
- **Role detail** — multi-page structured listing. One section per level; each role shows the current occupant, the complete substitution chain with phone numbers, and any manual assignment.
- **People list** — alphabetical phone directory. Absent people are called out in a separate section.

![Print dialog — template chooser with paper size and orientation](docs/screenshots/22-print-template-chooser.png)

![Overview print template rendered for the Enterprise demo committee](docs/screenshots/23-print-overview-output.png)

All three variants support A4, A3, and Letter in both portrait and landscape. The layout scales to fill the selected page.

## Languages

The user interface is available in:
- German (Deutsch)
- English
- Spanish (Español)
- French (Français)
- Chinese (中文)

![Language switcher in the header](docs/screenshots/12-language-switcher.png)

The language switcher is in the header. The selection persists between sessions.

## Editing the committee

Edit mode is activated with the ✎ icon in the header. While in edit mode you can add or rearrange levels, roles, and persons, and manage the substitution chain for each role.

![Edit mode active — role cards show pencil and pin handles for editing](docs/screenshots/10-edit-mode-active.png)

![Role editor with ordered substitution chain](docs/screenshots/11-edit-role-modal.png)

The Settings dialog exposes the organisation name and the print title — both are empty by default and are shown on every printed page if filled in.

![Settings dialog — General tab](docs/screenshots/13-settings-general-tab.png)

## Tracking absence

Clicking a person in the main view (when not in edit mode) opens a dialog to mark them unavailable. A reason category and an optional note can be recorded. Once marked, the person's availability is reflected across all roles they are assigned to, and the substitution chain takes over automatically.

![Manual assignment modal — pick the person who should hold this role regardless of availability](docs/screenshots/09-manual-assignment-modal.png)

The sidebar has three tabs:

- **Roster** — shows who is currently absent at the top, followed by the active occupants with their contact details grouped by role.
- **People** — alphabetical list of all persons with their availability status and quick filter.
- **Log** — the 30-day audit trail.

![People tab — alphabetical directory with availability state](docs/screenshots/04-sidebar-people-tab.png)

![Log tab — recent absence changes, manual assignments, sync events](docs/screenshots/05-sidebar-audit-log.png)

## Privacy and data handling

Everything stays in the browser. There is no backend, no analytics, no telemetry. The three storage keys (`cram.config`, `cram.runtime`, `cram.audit`) live in the browser's localStorage and never leave the device unless *you* export them.

This does mean there is no cloud sync, no cross-device login, no backup unless you make one yourself. The transfer channels above are the only way data moves between instances.

## Browser compatibility

| Feature | Chrome/Edge | Safari (desktop) | Safari (iOS 15+) | Firefox |
|---|---|---|---|---|
| Core functionality | ✓ | ✓ | ✓ | ✓ |
| QR code generation | ✓ | ✓ | ✓ | ✓ |
| QR code scanning | ✓ | ✓ | ✓ | — (missing BarcodeDetector API) |
| PWA installation | ✓ | ✓ | ✓ (caveat below) | partial |
| Camera over `file://` | ✓ | ✓ | n/a | ✓ |
| Camera on mobile over `file://` | — | — | — (needs HTTPS) | — (needs HTTPS) |
| **Online sync — HTTP backend (V1.2+)** | ✓ | ✓ | ✓ | ✓ |
| **Online sync — Local directory (V1.2+)** | ✓ | partial (re-permission per session) | — (no File System Access API) | — (no File System Access API) |
| **End-to-end encryption (V1.2+)** | ✓ | ✓ | ✓ | ✓ |
| **Auto-Sync polling (V2.0)** | ✓ | ✓ | ✓ (caveat below) | ✓ |

Firefox users can still use every feature except QR scanning and the Local-directory sync source. HTTP-based online sync works in every browser. When a feature is unavailable, CRAM shows an explanatory banner in the Sync sources tab.

For mobile camera access, the tool needs to be served over HTTPS, localhost, or loaded from `file://` with appropriate permissions.

**iOS PWA caveat:** Safari clears Web App data after roughly 7 days of inactivity (Apple platform policy). For users who install CRAM as a PWA on iPhone and only open it during incidents, sources, the audit log, and the local configuration can disappear unexpectedly. Mitigation: export a JSON backup regularly, or keep the sync source configured against an HTTP backend so a re-import after data loss is one Pull away.

## Known limitations

- QR scanning is not available on Firefox. We chose not to ship a 130 KB polyfill for a minority-browser edge case. Firefox users on desktop can transfer configurations via JSON export instead.
- The tool is deliberately single-device and offline. There is no central server, no account system, no cross-device sync. Configuration changes must be propagated explicitly through one of the three transfer channels.
- localStorage is tied to the browser origin. Opening the same HTML file from two different paths counts as two separate installations with independent state.
- At very large committee sizes (100+ persons, 40+ roles), the overview print variant may overflow A4 landscape. A3 handles this comfortably.

## Licence

Apache License 2.0. See [LICENSE](LICENSE) for the project licence and [NOTICE](NOTICE) for third-party attributions including the full MIT licence texts of embedded libraries.

A CycloneDX 1.5 Software Bill of Materials is produced with each release (see `cram-sbom.cdx.json` in the release assets). It lists every embedded component with purl, SHA-256 hash, and licence identifier, suitable for ingestion into dependency-tracking tools.

## Acknowledgements

CRAM embeds two third-party libraries, both inlined for the single-file architecture. Full licence texts are reproduced in [NOTICE](NOTICE) and as comment blocks directly above each library's code inside `crisis-role-manager.html`.

- **fflate** 0.8.2 by Arjun Barrett — MIT License. Compression for QR transfer payloads.
- **qrcode-generator** 1.4.4 by Kazuhiko Arase — MIT License. QR matrix generation.

## Contributing

Bug reports, feature requests, and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to file an issue or submit a change.

## Disclaimer

CRAM is a tool, not a plan. It assists with tracking and communicating role assignments; it does not substitute for a tested crisis management process, trained personnel, or the judgment of whoever is responsible for committee leadership during an actual incident. Test it under realistic conditions before relying on it.
