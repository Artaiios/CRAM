# CRAM — Roadmap

Stand: 8. Mai 2026, nach Brainstorming-Konvergenz für V1.2/V2.0.

Lebende Liste. Prioritäten verschieben sich durch Praxis-Feedback. Liegt im Repo, damit Mitbenutzer nachvollziehen können, woran wir denken.

## Aktuelle Phase: V1.0 finalisieren

Der RC ist mit rc1.3 in Praxis-Erprobung gewesen. Feedback der Tester eindeutig:

> "Robust, alle grundlegenden Funktionen vorhanden und nutzbar. Aber dadurch komplex jeden Status aktuell zu halten, vor allem in verteilten Teams. Air-Gap-Sync wichtig für Extremfälle, im Regelfall ist Netzwerk vorhanden — daher mittelfristig eine Option, die alle Mitglieder pro-aktiv synchron hält."

Konsequenz: V1.0 wird wie geplant als stabile Single-Device-Variante released, **S-02 ist der einzige verbleibende Release-Blocker.** Online-Sync ist V2-Material — V1.2 dient als manueller Zwischenschritt, der die Sync-Source-Architektur einführt, ohne schon Auto-Magie zu bringen.

---

## Vor V1.0 — Security

### S-01: Content Security Policy ✓ erledigt mit rc1.3

Inline-CSP-Meta-Tag im `<head>`, blockt externe Scripts/Styles, erlaubt nur Inline (Single-File-Architektur-Zwang). Kein `unsafe-eval`. Ausgeliefert.

### S-02: Systematische Verifikation von Nutzer-Input-Escaping

**Status:** einziger verbleibender Release-Blocker für V1.0.

**Ausgangslage:** Code nutzt heute 308 `escapeHTML()`-Aufrufe an 55 `innerHTML=`-Stellen. Diszipliniert, aber nicht bewiesen lückenlos.

**Konkrete Maßnahmen:**

1. **Pen-Test-Konfiguration bauen** — Demo-Config mit XSS-Payloads in jedem Feld. Bleibt **dauerhaft lokal**, kommt nie ins Repo (auch nicht in Branches).
   - `<img src=x onerror=alert(1)>`
   - `"><script>alert(1)</script>`
   - `javascript:alert(1)`
   - `</div><iframe src=javascript:alert(1)>`
   - HTML-Entity- und Unicode-Tricks: `&#60;script&#62;`

2. **Vollständiger View-Walkthrough** — Pen-Test-Config importieren, alle Views durchklicken: Organigramm, alle Modals, alle drei Druckvarianten, Sidebar-Tabs (Roster/People/Log), Audit-Log, Sync-Modal. Jedes ausgelöste Alert oder im DOM auftauchende `<script>`/`onerror=`/`javascript:` ohne Tool-Herkunft = Lücke.

3. **Automatisierter Regressions-Test** — unter `tests/` festschreiben (Playwright + Headless-Chromium). Lädt CRAM mit Payload-Config, scannt DOM nach unerwünschten Tags/Attributen, schlägt fehl wenn welche gefunden werden.

4. **Punktuelle Umstellung auf `textContent`** — wo nur Text angezeigt wird (Personen-Name, Telefonnummer, Rollen-Name in Card), `innerHTML` durch `textContent` ersetzen. Eliminiert Stellen dauerhaft als Angriffsfläche.

**Aufwand:** 1-3 Tage je nach Findings. Branch: `s-02-input-audit`.

### S-03 (optional): SHA-256 für Release-Assets

Zurückgestellt. Nice-to-have, nicht blockierend. Wird umgesetzt, sobald ein Customer es anfragt.

---

## Vor V1.0 — Lizenz-Compliance ✓ vollständig erledigt mit rc1.3

- **L-01** ✓ MIT-Lizenztexte für fflate und qrcode-generator inline + NOTICE-Datei
- **L-02** ✓ qrcode-generator-Versions-Pin auf 1.4.4 mit Begründungs-Kommentar
- **L-03** ✓ SPDX-Header in `crisis-role-manager.html`
- **L-04** ✓ CycloneDX 1.5 SBOM als Release-Asset (`cram-sbom.cdx.json`)

---

## Vor V1.0 — Praxistest

### T-01: RC-Feedback eingearbeitet ✓

Praxistest mit rc1.2/rc1.3 hat keine Bugs oder strukturellen Probleme aufgezeigt. Tool gilt als robust und funktional vollständig. Das größte Feedback-Item ist nicht V1-relevant, sondern Design-Driver für V2: pro-aktive Synchronisation für verteilte Teams. Siehe V1.2/V2.0.

---

## V1.2 — Manueller Online-Sync mit Awareness

**Ziel:** Sync-Source-Architektur etablieren, ohne Auto-Magie. User behält volle Kontrolle. Proof-of-Concept und Vertrauensaufbau für V2.

**Funktionsumfang:**
- **Sync-Source-Abstraktion** (`read()`, `write()`, `version`) als zentrale Erweiterung
- **Backend S1** (HTTP PUT/GET): self-hosted nginx, Caddy, MinIO, SharePoint-WebDAV, Synology
- **Backend S5** (File System Access API): lokales Verzeichnis, deckt OneDrive-/Dropbox-/Drive-Sync-Folder und Network-Mounts ab
- **Setup über Sync-Bundle** (URL + Auth-Token + Passphrase + Config-Fingerprint), distribuiert als QR-Code, Magic-Link oder JSON-Datei
- **Encryption Default ON** via WebCrypto (AES-GCM, PBKDF2 aus Passphrase) — auch für S1, weil Customer-IT-Logs nicht im Klartext PII enthalten sollen (DSGVO)
- **Zwei explizite Buttons** im Sync-Modal: "Stand vom Server holen" + "Stand auf Server schicken"
- **Awareness-Indikator** im Header, separat vom Verfügbarkeitsstatus: synced / syncing / out-of-sync / disabled
- **Browser-Warnung** bei eingeschränktem Funktionsumfang (Firefox: keine S5-Persistierung)

**Was nicht in V1.2 kommt:** Auto-Polling, Auto-Push, Konflikt-Auflösung, Multi-Source.

**Detail-Spec:** [`docs/specs/v1.2-manual-sync.md`](docs/specs/v1.2-manual-sync.md).

**Branch:** `v1-2-manual-sync`. **Aufwand:** geschätzt 4–6 Sessions inklusive Tests, UI-Anpassung, Doku-Update.

---

## V2.0 — Automatischer Online-Sync

**Ziel:** "Set-and-forget"-UX. Sync läuft transparent im Hintergrund, im Krisenfall kein manueller Aufwand für die Nutzer.

**Architektur:** identisch zu V1.2 (gleiche Sync-Source-Abstraktion, gleiche Backends).

**Was V2.0 dazubringt:**
- **Auto-Polling** alle 90 Sekunden (konfigurierbar 30–300 Sek)
- **Auto-Push** sofort nach jedem lokalen Save (mit Backoff bei Fehler)
- **Pull-before-push** mit HTTP-If-Match für optimistische Konkurrenz-Kontrolle (S1, S2)
- **Tab-Visibility-Sync** — sofortiger Pull bei Tab-Fokus
- **Silent auto-apply** eingehender Updates, Toast-Notification ohne Dialog
- **Konflikt-Verlust** wird ins Audit-Log geschrieben mit Recovery-Pfad
- **Multi-Source** als Advanced-Option für Failover-Szenarien

**Detail-Spec:** [`docs/specs/v2.0-auto-sync.md`](docs/specs/v2.0-auto-sync.md).

**Branch:** `v2-0-auto-sync`. **Aufwand:** geschätzt 5–8 Sessions auf Basis der V1.2-Architektur.

---

## V2.1 (optional) — S2-Backend (S3-presigned-URLs)

**Ziel:** Cloud-Storage-Backend ohne eigenen Server-Betrieb für Customer mit existierender AWS/MinIO/R2/B2-Infrastruktur.

**Reibung:** Presigned URLs expiren (max 7 Tage bei AWS sigv4). Setup muss URL-Rotation einkalkulieren — entweder über regelmäßiges manuelles Sync-Bundle-Update oder über einen kleinen URL-Refresh-Endpoint.

**Wird gebaut, wenn** die Praxis nach V2.0 zeigt, dass S1 + S5 nicht alle Customer abdecken und Cloud-Storage-Bedarf signifikant ist.

---

## 1.x Feature-Set (parallel oder nach V2)

Nicht zwingend, aber praxisrelevante Verbesserungen. Reihenfolge ist Vorschlag, kann durch Praxis-Feedback verschoben werden.

### F-01: Suche über Rollen und Personen

Strg+K öffnet Suchfeld. Eingabe "CISO" findet Rolle, "Martinez" findet Person. Klick scrollt zur Karte oder öffnet Detail-Dialog. Bei großen Stäben (40+ Rollen, 100+ Personen) deutliche Zeitersparnis. **Aufwand:** 1–2 Sessions.

### F-02: Audit-Log-Filter und CSV-Export

Log-Tab bekommt Filter (Zeitraum, Typ, Person). CSV-Export für Nachbesprechungen und Compliance. Heute nur per Screenshot — nicht praxistauglich. **Aufwand:** 1 Session.

### F-03: Tags für Personen

Personen bekommen Freitext-Tags ("Nachtschicht", "Remote verfügbar", "Englisch"). Anzeige in People-Liste, nutzbar als Filter. Basis für F-04. **Aufwand:** 1 Session.

### F-04: Bulk-Operationen

Mehrere Personen gleichzeitig als abwesend markieren ("alle mit Tag 'Standort-München' als 'Dienstreise'"). Nützlich bei geplanten Events. Braucht F-03. **Aufwand:** 1 Session.

### F-05: Theme automatisch nach Systemeinstellung

`prefers-color-scheme` als Default, manuelle Überschreibung weiterhin möglich. **Aufwand:** 1–2 Stunden.

### F-06: Drucklayout "Kontakt-Karte"

Vierte Druckvorlage: A5/A6-Karte pro Stabsmitglied mit eigenen Rollen, direkten Vertretern, Telefonnummern. Persönliche Karte zum Mitnehmen. **Aufwand:** 0,5–1 Session.

### F-07: Drilldown von Statuspill zu betroffener Liste

Klick auf "Sub. active 12" öffnet Liste der 12 aktiven Vertretungen. Klick auf "Unoccupied 1" zeigt unbesetzte Rolle. Reine Navigation, keine neue Semantik. **Aufwand:** 1 Session.

---

## V-02 (langfristig optional) — Historische Ansicht

Über 30-Tage-Audit-Log hinausgehend: Snapshots zu Zeitpunkten (quartalsweise, nach größeren Änderungen) speichern und rückwärts einsehbar machen. Nützlich bei Audit-Szenarien nach echten Vorfällen.

Aufwand vs. Nutzen für die meisten Organisationen wahrscheinlich nicht günstig. Erstmal als Idee parken.

**Aufwand:** 2–3 Sessions.

---

## Prozess-Roadmap

### P-01: Beta-Feedback kanalisieren ✓

Strukturiertes Feedback-Gespräch hat stattgefunden, Ergebnis siehe T-01 und V1.2/V2.0-Specs.

### P-02: Versions-Kommunikation

Mit V1.0-Release kurze Ankündigung (Blog-Post / LinkedIn / interner Newsletter, je nach Zielgruppe). Ziel ist Findbarkeit, nicht Marketing. Wenn nur drei Leute im eigenen Unternehmen das Tool nutzen, ist das völlig okay — dann braucht's keine Kampagne.

### P-03: License-Kompatibilitäts-Scan

Für Enterprise-Einsätze sinnvoll: Apache-2.0 ist mit typischen Unternehmens-Lizenzen kompatibel, aber eine schnelle Prüfung mit `scancode` oder `license-checker` stellt sicher, dass nichts versehentlich GPL-Schnipsel enthält.

---

## Anti-Roadmap — was wir bewusst NICHT tun

- **npm-Package-Publishing.** CRAM ist Anwendung, keine Library.
- **Docker-Image.** Overkill für Single-File-HTML.
- **TypeScript-Refactoring.** Bewusst Vanilla JS, damit jeder Admin den Code modifizieren kann.
- **Build-Tools / Bundler.** Bricht Single-File-Prinzip.
- **Eigene Icons-Library / CSS-Framework.** CSS-Variablen-basiertes Minimal-CSS bleibt.
- **Plugin-System.** Forken und editieren ist die vorgesehene Extension-Methode.
- **WebRTC P2P-Sync.** Falsches Modell für asynchrone Stab-Sync.
- **Git-as-Backend für Sync.** Verwirrt mehr als es hilft (Commit-Floods, Rate-Limits, Audit-Log-Doppelung).
- **Eigene CRAM-Cloud / SaaS.** Customer hostet eigenes Backend oder nutzt eigene Cloud — kein Phone-Home.
- **OneDrive / Drive via OAuth.** OAuth-Flow-Komplexität nicht gerechtfertigt — der File-System-Access-Pfad (S5) deckt diese Use-Cases via Desktop-Sync-Folder ab.

---

## Reihenfolge-Vorschlag

1. **Jetzt:** S-02 abschließen → V1.0 final taggen → GitHub-Release mit Assets.
2. **Danach:** V1.2 implementieren (manueller Sync, Awareness-Indikator, Sync-Source-Architektur). Praxistest.
3. **Nach V1.2-Praxistest:** V2.0 (Auto-Sync) als Switch-On auf der V1.2-Architektur.
4. **Optional V2.1:** S2-Backend, wenn Bedarf da.
5. **Parallel oder nach V2.0:** F-01..F-07 in praxis-getriebener Reihenfolge. Voraussichtlich F-07 (günstig) → F-01 (Suche, viel Wert) → F-02 (Audit-Export) → F-05 (Theme-Auto) → F-03/F-04 (Tags + Bulk) → F-06 (Kontakt-Karte).
6. **Langfristig optional:** V-02 (historische Ansicht), wenn Audit-Bedürfnisse danach rufen.
