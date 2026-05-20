# CRAM — Roadmap

Stand: 19. Mai 2026 — V1.0, V1.2.0, V1.2.1, V1.3.0 released. V2.0.0-rc1 als Release-Candidate getaggt (`v2-auto-sync`-Branch); Promotion auf stable V2.0.0 nach RC-Phase.

Lebende Liste. Prioritäten verschieben sich durch Praxis-Feedback. Liegt im Repo, damit Mitbenutzer nachvollziehen können, woran wir denken.

---

## Released

### V1.0 — Single-Device-Baseline ✓

Stabile Single-Device-Variante. Sync per Code/QR/JSON. Kernfunktionen produktiv erprobt.

**Security (vor V1.0 abgeschlossen):**
- **S-01** ✓ Content Security Policy (Inline-Meta-Tag, kein `unsafe-eval`)
- **S-02** ✓ Systematische Verifikation von Nutzer-Input-Escaping — Pen-Test-Config + DOM-Scan-Regression, `textContent`-Umstellung an reinen Text-Stellen
- **S-03** (optional, zurückgestellt) SHA-256 für Release-Assets — nice-to-have, nicht blockierend

**Lizenz-Compliance (vor V1.0 abgeschlossen):**
- **L-01** ✓ MIT-Lizenztexte für fflate und qrcode-generator inline + NOTICE-Datei
- **L-02** ✓ qrcode-generator-Versions-Pin auf 1.4.4 mit Begründungs-Kommentar
- **L-03** ✓ SPDX-Header in `crisis-role-manager.html`
- **L-04** ✓ CycloneDX 1.5 SBOM als Release-Asset (`cram-sbom.cdx.json`)

**Praxistest:** T-01 ✓ RC-Feedback eingearbeitet. Größtes Feedback-Item (pro-aktive Sync) wurde zum Design-Driver für V1.2/V2.0.

### V1.2 — Manueller Online-Sync mit Awareness ✓

Sync-Source-Architektur etabliert, ohne Auto-Magie. User behält volle Kontrolle.

- Sync-Source-Abstraktion (`read()`, `write()`, `version`)
- Backend S1 (HTTP PUT/GET) und S5 (File System Access API)
- Setup über Sync-Bundle (URL + Auth-Token + Passphrase + Config-Fingerprint), distribuiert als QR-Code, Magic-Link oder JSON-Datei
- Encryption Default ON via WebCrypto (AES-GCM, PBKDF2)
- Zwei explizite Buttons im Sync-Modal: "Stand vom Server holen" + "Stand auf Server schicken"
- Awareness-Indikator im Header: synced / syncing / out-of-sync / disabled
- Browser-Warnung bei eingeschränktem Funktionsumfang (Firefox: keine S5-Persistierung)

**Detail-Spec:** [`docs/specs/v1.2-manual-sync.md`](docs/specs/v1.2-manual-sync.md).

### V1.3 — Sync/Data-Split (Status vs. Konfiguration) ✓

Sicherheitsproblem aus V1.2 gelöst — Sync-Aktionen können nicht mehr versehentlich strukturelle Konfigurationen überschreiben.

- **⇄ Sync** ist ausschließlich Status-Sync (Abwesenheiten + manuelle Zuweisungen), nur bei identischem Fingerprint zwischen Server und lokal
- **⇵ Data** mit neuem Online-Tab für vollständige Konfigurations-Synchronisation (config + runtime), mit explizitem Bestätigungs-Dialog
- Backend `Sync.push`/`Sync.pull` mode-aware (`'status'` | `'full'`), neue Error-Klasse `ConfigDriftError`
- `Sync.probeMeta` und `Sync.previewDiff` für Server-Stand-Inspektion ohne Apply
- Awareness-Indikator neuer Zustand `config-drift` (⚠, rot, klickbar)
- Onboarding-Auto-Pull nach Bundle-Import
- Vorbereitung für V2.0: Auto-Polling kann nur Status berühren

---

## V2.0 — Automatischer Online-Sync (rc1 released)

**Ziel:** "Set-and-forget"-UX. Sync läuft transparent im Hintergrund, im Krisenfall kein manueller Aufwand.

**Architektur:** identisch zu V1.3 (gleiche Sync-Source-Abstraktion, gleiche Backends). V2.0 ergänzt eine Automatisierungs-Schicht.

**Was V2.0-rc1 enthält:**
- **SyncPoller** mit per-source Tick-Loop, Visibility-Multiplier ×4 bei Hidden-Tab, `online`/`offline`-Listener
- **3-Klassen-Fehler-Modell:** `transient` (Backoff), `auth` (AutoMode-OFF + Badge), `permission` (Hard-Pause + Action-Required) — plus separate Klassen für `passphrase-required`, `concurrent` (412), `config-drift`
- **Auto-Push** mit 2 s-Debounce via `Sync.markDirty()`
- **Pull-before-push** mit `If-Match`-ETag für Lost-Update-Schutz (S1)
- **`pendingPush`-Sentinel** für Crash-Recovery mid-push (SHA-256-Payload-Hash)
- **Vier Auto-Modi pro Source:** `off`, `pull`, `push`, `bidirectional`, Polling-Intervall 30–300 s
- **Tab-Visibility-Sync** — sofortiger Pull bei Tab-Fokus, Reset des Visibility-Multipliers
- **Silent auto-apply** eingehender Updates, Toast statt Dialog
- **Config-drift** als eigene Fehlerklasse + modaler Resolve-Dialog
- **Live-Countdown** im Header-Indikator (Auto-Mode: „Synced vor 12s · nächster in 18s")
- **PWA-Manifest** mit 192/512 PNG-Icons (Lighthouse-installable)
- **Mobile-Akzeptanzkriterien M1–M3** (iPhone Safari iOS 15+)

**Was in rc1 NICHT enthalten ist (deferred → rc2/GA):**
- S5-Auto-Push (kein ETag-Equivalent in File System Access API)
- iPad-Smoke
- Realer iPhone-Smoke gegen physisches Gerät
- WP-16 ZH-native Review der Passphrase-i18n-Strings
- Dev-Backend `If-Match`-Validation

**Detail-Spec:** [`docs/specs/v2.0-auto-sync.md`](docs/specs/v2.0-auto-sync.md).

**Branch:** `v2-auto-sync`. **Tag:** `v2.0.0-rc1`.

### V2.0-GA-Gate

Promotion auf stable V2.0.0:
1. Realer iPhone-Smoke gegen physisches Gerät (M1–M3 plus H1/H3 im Standalone-Mode)
2. Dev-Backend `If-Match`-Validation (für Two-Tab-Konflikt-Smoke im CI)
3. RC-Phase mind. zwei Wochen ohne neue Showstopper
4. WP-16 ZH-Native-Review

---

## V2.0-Plateau (ab GA)

V2.0 ist als stabiles Plateau gedacht, kein Sprungbrett zu V3. Krisen-Tooling, das sich quartalsweise verändert, ist gefährlich — Muscle Memory der User ist ein Sicherheits-Feature. Maßstab für jede neue Funktion: macht das den Krisenstabs-Alltag einfacher oder nur reichhaltiger?

Wartungslinie: V2.0.x für Bugfixes und Sicherheits-Patches. Maximal zwei begründete V2.x-Erweiterungen pro Jahr.

---

## V2.0.x — Quick-Wins (nach GA, inkrementell)

Aus interner UX-Review nach RC1:
- **Q1:** Tooltip-Konsistenz-Pass (`title=` + `aria-label` synchronisieren) — A11y
- **Q2:** „Was passiert jetzt"-Texte in destruktiven Dialogen (Vorher/Nachher statt „Sicher?") — Krisen-Fehlertoleranz
- **Q3:** Print-Vorschau-Modal vor tatsächlichem Drucken — Discoverability, Papier-Spar

Aus Audit-Findings:
- **F-S2:** Toast-Stack-Cap (MAX_TOASTS=10, FIFO)
- **F-S3:** `_setSyncing` Refcount statt Bool (UI-Flackern bei Pull+Push parallel)
- **F-B:** `_stripUrlsAndTokens` Basic-Auth + Cookie-Header (low risk bei aktuellen Backends)
- **R1-Lücke:** Combo-State Offline + OutOfSync im Header
- **dev-sync-backend.py** um If-Match-Validierung erweitern (für lokale 2-Tab-Smoke-Tests)
- **ZH-Native-Speaker-Review** für i18n-Strings (Inline-TODOs im Code)

---

## V2.1 — Team-Pools (geplant)

Vierte Ebene unter Krisenstab / Management / Topic-Lead: Mitarbeiter-Pools.

**Zweck:**
- Mitarbeiter erfassen, die nicht in den drei Krisen-Rollen-Ebenen stecken
- Verfügbarkeit festhalten (gleiche Logik wie bestehende Person-Verfügbarkeit)
- Keywords/Schwerpunktthemen pro Mitarbeiter (z.B. „SOC-Analyst Tier 2", „Cloud-Forensik")

**Visuelle Differenzierung:**
- Flacher als Rollen-Karten (kleinere Höhe, ggf. Listen-Layout)
- Optisch klar abgesetzt — Pool und Rolle dürfen nicht verwechselbar sein

**Use-Case-Beispiel:** Krisenstab sucht „wer kann Cloud-Forensik in der nächsten Stunde?" → filterbar nach Keyword + Verfügbarkeit.

**Komplexität:** moderat. Schema-Migration auf v3, neuer Render-Layer, Such-/Filter-Funktion, Print-Template-Erweiterung, i18n × 5.

---

## V2.2 — Bereitschafts-Kalender (geplant)

Geplante Abwesenheiten vorab erfassen (Zeitraum statt nur „ab jetzt"). Tool berechnet aktuelle Cascade aus Datum + Plan. Schließt die Lücke zwischen akuter Lage und Wochen-Slot-Planung.

---

## V2.x — Lessons-Learned-Export (geplant, später)

Audit-Log → strukturierter Post-Incident-Report (Markdown/PDF). Nutzt vorhandene Audit-Daten, viertes Print-Template.

---

## V2.x — Print-Layout-Refresh (Polish, eigener Task)

Aktuelle drei Print-Templates wirken unübersichtlich. UX-Reviewer + ui-engineer-Pass auf Strukturklarheit, ggf. verbunden mit V2.1 wenn Team-Pools ohnehin die Templates anfassen.

---

## Im Backlog (kein Commitment)

Praxisrelevante Ideen ohne festen Termin. Werden gezogen, wenn Bedarf aus dem Einsatz klar wird.

- **Suche über Rollen und Personen** (Strg+K) — bei großen Stäben (40+ Rollen) deutliche Zeitersparnis
- **Audit-Log-Filter und CSV-Export** — heute nur per Screenshot, nicht praxistauglich für Nachbesprechungen
- **Tags für Personen** (Freitext: „Nachtschicht", „Remote", „Englisch") — Basis für Bulk-Operationen
- **Bulk-Operationen** auf Personen-Gruppen (braucht Tags) — nützlich bei geplanten Events
- **Theme automatisch nach Systemeinstellung** (`prefers-color-scheme` als Default)
- **Drucklayout „Kontakt-Karte"** — A5/A6 pro Stabsmitglied zum Mitnehmen
- **Drilldown von Statuspill** — Klick auf „Sub. active 12" zeigt Liste
- **Historische Snapshots** über 30-Tage-Audit-Log hinaus — für Audit-Szenarien nach echten Vorfällen
- **S2-Backend (S3 presigned URLs)** — wenn Praxis zeigt dass S1+S5 nicht reichen; Presigned-URL-Rotation ist die Reibung
- **Übungs-Modus (Tabletop-Exercise)** — strategisch interessant, aber UX-Verwechslungsgefahr Übung/Ernst muss erst sauber gelöst sein
- **Tests/-Verzeichnis ausbauen** — Pen-Test ist mit GA drin, weitere Smoke-Tests folgen
- **Encryption-Default für neue Sources auf `on` umstellen** (aktuell off, nur Empfehlung in Doku)

---

## Prozess

### Versions-Kommunikation

Mit V1.0/V2.0-Release kurze Ankündigung (Blog-Post / LinkedIn / interner Newsletter, je nach Zielgruppe). Ziel ist Findbarkeit, nicht Marketing. Wenn nur drei Leute im eigenen Unternehmen das Tool nutzen, ist das völlig okay.

### License-Kompatibilitäts-Scan

Für Enterprise-Einsätze sinnvoll: Apache-2.0 ist mit typischen Unternehmens-Lizenzen kompatibel, aber eine schnelle Prüfung mit `scancode` oder `license-checker` stellt sicher, dass nichts versehentlich GPL-Schnipsel enthält.

---

## Bewusst verworfen

Diese Themen sind geprüft und bewusst nicht im Plan, weil sie das Kern-Versprechen des Tools (single-file, offline-first, krisen-stabil) verwässern würden:

- **Multi-Komitee in einer Instanz** — Browser-Profile sind der richtige Hammer
- **Browser-Notifications/Alerts** — unzuverlässig im Krisenfall, Permission-Erwartungs-Mismatch
- **Mobile-App-Wrapper (Capacitor/Tauri)** — AppStore-Pflege bricht Single-File-Prinzip
- **Voice-Input** — Genauigkeit unter Stress katastrophal, Datenschutz problematisch
- **Server-Multi-User-Locking** — bricht „No backend", ETag-Optimistic-Concurrency reicht
- **Build-Pipeline / npm-Dependencies / TypeScript / React** — architektonisch ausgeschlossen
- **Telemetrie / Analytics** — ausgeschlossen, auch nicht „nur Crash-Reports"
- **Docker-Image / eigene Server-Komponente** — Overkill für Single-File-HTML
- **Plugin-System** — Forking ist das Erweiterungsmodell
- **WebRTC P2P-Sync** — falsches Modell für asynchrone Stab-Sync
- **Git-as-Backend für Sync** — verwirrt mehr als es hilft (Commit-Floods, Rate-Limits, Audit-Log-Doppelung)
- **Eigene CRAM-Cloud / SaaS** — Customer hostet eigenes Backend oder nutzt eigene Cloud, kein Phone-Home
- **OneDrive / Drive via OAuth** — OAuth-Flow-Komplexität nicht gerechtfertigt; S5 deckt diese Use-Cases via Desktop-Sync-Folder ab
- **npm-Package-Publishing** — CRAM ist Anwendung, keine Library
- **Eigene Icons-Library / CSS-Framework** — CSS-Variablen-basiertes Minimal-CSS bleibt
