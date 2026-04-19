# CRAM — Handbook

This handbook describes the operation of CRAM — the Crisis Role Availability Manager. It is split into two parts. The **user section** is for any member of a crisis committee who works with the tool during an incident. The **administration section** is for those who maintain the configuration, distribute new versions, and are responsible for operations.

---

# Part 1: User Section

## Opening the tool for the first time

CRAM is a single HTML file. A double-click is enough — the file opens in the default browser. No server is required, no installation, no internet connection.

On first start, a sample configuration is loaded that shows a small crisis committee for cybersecurity incidents. This configuration can be edited or replaced entirely.

Anyone using CRAM regularly should install it as a Progressive Web App (PWA):

- **Chrome/Edge desktop**: Install icon on the right side of the address bar
- **Chrome Android**: Menu → "Add to Home screen"
- **Safari iOS**: Share menu → "Add to Home Screen"

After installation, CRAM launches in its own window without browser chrome. State persists between sessions.

## The interface at a glance

After starting, you see three main areas:

- **Header**: Version display, statistic pills (Primary, Substitute active, Unoccupied, Absent), language selector, action buttons (Sync, Data, Print, Edit-mode toggle, theme switcher)
- **Main area**: Organisation chart with levels and roles. Each role is displayed as a card.
- **Right sidebar**: Three tabs — **Roster** (current occupancy and absence list), **People** (all persons by name), **Log** (audit trail)

## Understanding role cards

Each role card shows the following information:

- **Role name** at the top (e.g. "Crisis Manager")
- A **lightning symbol** if the role is marked as critical
- The **current occupant** with their rank — `PRIMARY` for the planned person, `SUB1`/`SUB2` when a substitute has taken over
- A **replacing note** if someone other than the primary is covering — the person being replaced is shown with strikethrough
- At the bottom, the complete **substitution chain** (`CHAIN`): Primary → Sub1 → Sub2 → … with struck-through entries for people who are currently unavailable

A **lock symbol** in the top right indicates that this role has been manually assigned and does not follow the automatic logic.

## Marking a person unavailable

In normal operation — that is, outside edit mode — a single click on a person's name within a role card opens the unavailability dialog.

Pick a **reason**:

- **On leave**
- **Sick**
- **Business trip**
- **Active in other role** — useful when the person is tied up in a different context
- **Other**

An optional **note** can be added — for instance an expected return time or a handover instruction.

After confirmation, the person counts as unavailable. All roles in which they are assigned are automatically re-resolved — if they were primary, the first available substitute takes over. The chain is visibly updated.

## Understanding the substitution cascade

As the number of absences grows, cascades form: A role loses its primary, the substitute steps in — but is itself primary in another role, triggering a further shift there.

CRAM visualises such cascades with **red dashed arrows** between the affected role cards. This makes it immediately visible which substitution chains are currently under stress — an important piece of information for the committee lead when assessing how robust the current lineup is.

If no person is available anywhere in a chain, the role is flagged as **Unoccupied**. The corresponding pill in the header shows the count of unoccupied roles; it turns red when a critical role is affected.

## Manual assignment

Sometimes a specific person should hold a role — regardless of the automatic substitution logic. Examples: The planned primary is technically available but tied up with another topic; or the committee lead has decided operationally that a specific substitute should step in.

For these cases there is **manual assignment**. In edit mode, or via the pin button on a role card, a dialog opens in which a person can be picked from the overall list. The assignment remains until explicitly released ("Release manual assignment").

Manually assigned roles are marked with a 🔒 symbol on the role card and flagged as such in the Roster tab. They are included in sync transfers (both code sync and QR transfer).

## Transferring data to another device

CRAM offers three ways to transfer data between devices. Which one to use depends on the situation.

### Sync code (telephone)

Designed for quick **status updates over the phone**. A sync code is a short alphanumeric string (typically 20–40 characters) that encodes the current absence state and manual assignments. It is formatted in groups of four for easy telephone dictation.

Prerequisite: Sender and receiver share the same base configuration. The first four characters are a fingerprint of the configuration — if they match on both sides, the schema is compatible and the code is accepted.

**Operation:**

1. Open sync modal (⇄ button in header)
2. Select channel "📟 Code sync (phone)" — this is the default
3. The "↗ Send" tab is pre-selected — the code appears immediately
4. Read the code over the phone or paste it into chat
5. Receiver opens their sync modal, switches to "↙ Receive", enters the code and confirms

Entered codes are validated live: A mistyped character leads to a fingerprint mismatch and is detected before anything is applied.

**Limits:** The sync code transfers **only status**, no configuration. For initial setup or changes to roles/people, use the other channels.

### QR transfer (camera)

For the **initial distribution of a configuration** or when configurations differ between devices. Data appears as a QR code on the sender's device and is read by the receiver with the camera.

**Sender operation:**

1. Open sync modal, select channel "📷 QR transfer (camera)"
2. "↗ Send" tab, then pick scope:
   - **Configuration only** — roles, levels, people (no status)
   - **Status only** — absences and manual assignments
   - **Configuration + status** — everything
3. Click "Generate QR code(s)"
4. Small configurations show a single QR code; larger ones produce a series of fragments
5. With multiple fragments, activate "▶ Auto-advance" — every 2.5 seconds the next QR is shown automatically

**Receiver operation:**

1. Open sync modal, channel "📷 QR transfer (camera)", tab "↙ Receive"
2. Click "Start camera" — grant permission
3. Point camera at the sender's screen. Fragments are detected automatically; the progress dots show which ones have arrived (green) and which are still missing (grey).
4. Once all fragments are in, the preview appears — with statistics on configuration and status.
5. Click "Apply" — the data is applied; an entry in the audit log documents the import.

**Prerequisites:**
- Modern browser with `BarcodeDetector` API: Chrome, Edge, Safari. Firefox does not currently have this API.
- For camera access on mobile: HTTPS, localhost, or `file://` — HTTP does not work.

### JSON export/import

For **archival, email distribution, or version control**. The configuration (and optionally the status) is downloaded as a JSON file and can be imported on another device.

**Export:**

1. Open data modal (⇵ button)
2. Tab "↑ Export"
3. If needed, tick "Include runtime state" to include status as well
4. Click "Download" — a file `cram-export-YYYY-MM-DD-HH-MM-SS.json` is saved

**Import:**

1. Open data modal, tab "↓ Import"
2. Pick file — contents are validated
3. Review preview (number of levels, roles, people)
4. Click "Import" — existing data is overwritten

## Printing

CRAM has three print templates for paper copies, and all three work with A4, A3 or Letter in portrait or landscape.

**Overview**: A single-page wall chart. All roles grouped by level, each showing its current primary occupant and phone number in large type. Critical roles are highlighted red.

**Role detail**: Multi-page structured listing. One section per level; each role shows the current occupant, the complete substitution chain with phone numbers, and any manual assignment.

**People list**: Alphabetical phone directory with current status. Absent people are called out in a separate section.

**Operation:**

1. Print button (🖨) in header
2. Pick template
3. Pick paper size and orientation
4. "Open print dialog" — in the browser's print dialog, choose "Save as PDF" as destination if needed

The organisation and print titles set in Settings appear in the header of every printout. If empty, a language-dependent default title is used.

## Switching language

The language selector is in the header. Currently available: German, English, Spanish, French, Chinese. The selection persists between sessions.

## Display

The ☀/☾ symbol in the header toggles between light and dark theme.

The **S/M/L/XL** size steps adjust the display density of the organisation chart to screen size. On mobile devices there is a dedicated layout variant with bottom navigation.

## Reading the audit log

The Log tab shows all changes over the past 30 days:

- Configuration edits (which role, what changed)
- Absence notifications (who, with which reason, when)
- Manual assignments (which person, which role, set/released)
- Sync events (incoming and outgoing codes, imports)

Entries older than 30 days are removed automatically. The log is kept purely locally — there is no cross-device synchronisation, each client has its own log.

---

# Part 2: Administration Section

## Role and responsibility

The tool administrator of a crisis committee is typically the person who:

- agrees the role hierarchy with the committee leadership
- maintains people and their substitution chains
- distributes the configuration to all committee members
- rolls out application updates and coordinates field tests
- serves as first point of contact for technical issues

Typically this is someone from IT Security, Business Continuity Management, or the crisis management office. The role is not technically demanding — the tool is deliberately kept simple — but requires an overview of the committee and its processes.

## Building the initial configuration

Starting from scratch, there are two options:

**Option A — From the default:** After first opening, a sample configuration is loaded. It can be adapted step by step in edit mode to your own organisation. Good for small committees (up to ~15 roles).

**Option B — From a demo file:** The repository ships with two enterprise demo configurations with 100 people and 40 roles across 7 levels. These can be imported and then adjusted. Faster for larger committees, since the basic structure is already in place.

**Recommendation:** First create all **levels**, then enter the **people**, finally the **roles with substitution chains**. In this order because:

- Without levels you cannot create roles
- Without people you cannot make assignments
- Roles and assignments are the most effortful part — avoids context switching

## Maintaining people

In edit mode the People tab becomes an editor. A person has:

- **Name** (mandatory)
- **Phone number** (optional but strongly recommended — this is the central contact information during an incident)
- **Email** (optional)

Recommendations:

- **Unambiguous names**: For common names like "Michael Weber", add a title or middle name to prevent confusion in the cascade view.
- **Phone numbers in international format**: `+49 170 1234567` rather than `0170 1234567`. Makes callbacks possible from any device.
- **Update at least every six months**: People change jobs, phone numbers change. A calendar reminder helps.

## Defining roles

A role consists of:

- **Name** (mandatory) — should describe the function, not the current person
- **Description** (optional, but strongly recommended) — a sentence that makes the responsibilities clear. Under stress, nobody pulls up external documents.
- **Critical flag** — marks the role as critical; it is highlighted in print and statistics
- **Assignments** — primary plus substitutes in a defined order

**Guiding principles:**

- **At least two substitutes per role**, three if the role is critical. A shallow chain falls apart in a real incident.
- **Substitutes may hold other roles** — it is explicitly intended that the same person is primary in one role and substitute in another. The cascade algorithm handles this.
- **Avoid substitutes who are structurally always absent at the same time as the primary** — if the primary is regularly at a conference and their Sub1 usually accompanies them, the substitution chain is worthless.

## Role naming

Tips for durable role names:

- **Function over title**: "IT Security Lead" rather than "Head of Information Security ABC Ltd." Titles change, functions stay.
- **No personal names in role names**: "Legal & Compliance Lead" rather than "Legal (Meier)".
- **Consistent across levels**: Either all role names in German or all in English — don't mix.
- **Unambiguous**: No two roles with the same name, not even across levels.

## Distributing the configuration

The configuration initially exists only on the device on which it was created. To get it onto the devices of committee members, there are three paths:

### Path 1: JSON file via email / internal file share

Most pragmatic for organisations with a working IT workplace and email.

1. Admin exports JSON (Data → Export → without runtime state)
2. Distribute file to all committee members
3. Each committee member opens CRAM and imports the file

**Note**: Anyone with an existing configuration will overwrite it. The import dialog shows a preview first — number of roles, people, etc.

### Path 2: QR transfer (device to device)

When devices are physically together (kickoff meeting, training) or when email is not appropriate.

1. Admin opens QR transfer, scope "Configuration + status"
2. Activate auto-advance
3. Each committee member scans sequentially with their own camera

**Advantage**: No email attachment process, no file naming, no IT policy questions. **Disadvantage**: Not parallelisable.

### Path 3: Hosting on internal web server

For larger organisations with many committee members who use the app regularly.

1. Place HTML file on internal server (e.g. `https://tools.internal.example.com/cram.html`)
2. Link to all committee members
3. On opening, a tool instance is initialised locally per browser (not per device!)
4. Initial configuration distribution as in path 1 or 2

**Advantages**: Central version, camera access on mobile devices works, PWA install becomes a home-screen icon. **Prerequisite**: HTTPS endpoint available and reachable from all required networks.

## Rolling out configuration changes later

The initial distribution is a one-off. Changes (new role, personnel change, adjusted description) must be rolled out regularly.

**Recommended process:**

1. Admin changes the configuration on their device
2. Admin exports JSON and places it in an agreed location (or distributes via email, or offers QR transfer)
3. Committee members update their instance at their convenience — at the latest before the next scheduled incident test

**What does NOT happen without explicit action**: Devices do not auto-sync. This is deliberate — an unnoticed configuration change during a live incident would cause more harm than differing versions would if both are noticed.

**The config fingerprint** (four hex characters, visible in the sync modal and settings dialog) is a lightweight aid for detecting divergence: If two instances have different fingerprints, they have different configurations. This can be checked incidentally during every sync code exchange.

## Troubleshooting

### "QR scanner doesn't work"

**On Firefox**: Not supported. The browser does not have the native `BarcodeDetector` API. We deliberately don't ship a polyfill. Alternative: JSON import.

**On Chrome/Edge/Safari, but camera stays black**: Likely an HTTP origin instead of HTTPS. Solution: Open tool via HTTPS, localhost, or `file://`.

**On Chrome Android, error "permission denied"**: Browser settings → Site settings → Camera → allow for this site.

### "Sync code is rejected"

Most likely a config fingerprint mismatch. Sender and receiver have different base configurations. Solution: Align configuration — either via JSON export/import or QR transfer (scope "Configuration").

### "Everything is gone after reload"

`file://` + new file path = new origin = empty localStorage. If the HTML file has been moved, state is lost. Solution: Keep the file in a fixed location, or host via HTTPS.

In private/incognito mode, data is lost on closing — that is browser behaviour, not a bug.

### "Printer breaks the page in the middle"

Overview template on large committees (30+ roles) overflows A4 landscape. Solution: Use A3, or use the Role detail template which breaks naturally across pages.

### "Multiple team members have different lineups"

Expected if not actively synchronised. Each client has local status. Before a meeting or test, align once via sync code (quick, status only) or QR transfer (full).

## Data protection

CRAM processes personal data — name, phone number, email, absence status. This is non-trivial in terms of data protection law. Recommended steps:

1. **Document the purpose**: "Purpose of processing: Crisis committee organisation during incidents."
2. **Define legal basis**: In most cases legitimate interest (Art. 6 (1) (f) GDPR) or consent of committee members.
3. **Transparency towards data subjects**: Everyone in the tool should know they are in it and which data is held.
4. **Deletion concept**: When leaving the committee, the person must be removed from the config — on all instances.
5. **Don't use external transfer channels that third parties can inspect**: Internal email attachments OK, config upload to public file shares not OK.

For specific implementation questions, involve your organisation's data protection officer.

## Release handling

New CRAM versions are published as tags on GitHub. Every release includes the HTML file and the demo JSONs as assets.

**Process when rolling out a new version:**

1. Download new version from GitHub releases
2. Open on a test system and load it with an export JSON of the production config
3. Walk through all critical functions: editing, marking absences, sync code, QR transfer, printing
4. If everything works: distribute to committee members, replace old version on all devices
5. Check CHANGELOG for any changes — particularly breaking changes in the data format

**Backup before the switch**: Always export the current configuration with runtime state first. If the new version has an issue, you can roll back.

## Contact and feedback

Bug reports and feature requests via the GitHub issue tracker. For everything else see [CONTRIBUTING.md](../CONTRIBUTING.md).
