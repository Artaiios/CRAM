# CRAM — Management Summary

**Crisis Role Availability Manager** — Werkzeug für die Verwaltung von Krisenstabs-Rollen und Vertretungsketten in IT-Sicherheits- und Incident-Response-Teams.

---

## Das Problem

Wenn der Krisenfall eintritt, muss innerhalb von Minuten klar sein:

- **Wer hat aktuell welche Rolle?**
- **Wer vertritt wen, wenn die Bereitschaft ausfällt?**
- **Wer kann ein bestimmtes Fachthema sofort abdecken?**

In den meisten Organisationen wird das mit Excel, SharePoint-Listen oder einem Wiki abgebildet. Diese Werkzeuge sind im Ernstfall **nicht krisenstabil**: kein Netz, gesperrte Accounts, veraltete Stände, kein Vertretungs-Logik.

CRAM löst diese Anforderung als eigenständiges Werkzeug, das im Krisenfall garantiert funktioniert.

---

## Was CRAM macht

### Kern-Funktionen

- **Krisenstabs-Strukturen abbilden** — beliebig viele Ebenen (z. B. Strategischer Krisenstab, Management, Topic-Leads, Mitarbeiter-Pools)
- **Vertretungsketten** pro Rolle definieren — primär plus mehrere Substituten in fester Reihenfolge
- **Verfügbarkeit live tracken** — wer ist da, wer ist im Urlaub, wer auf Schicht
- **Automatische Cascade-Auflösung** — wenn die primäre Bereitschaft ausfällt, zeigt das Tool sofort die nächste verfügbare Vertretung
- **Mitarbeiter-Pools** mit freien Schwerpunktthemen (Keywords) — z. B. „SOC-Tier-2", „Forensik macOS", „Cloud-Reverse-Engineering"
- **Live-Suche** — „wer kann jetzt Cloud-Forensik?" filtert über Namen, Keywords und Verfügbarkeit

### Synchronisation ohne Backend

CRAM braucht **keine Server-Infrastruktur**. Daten leben lokal im Browser. Für den Stand-Abgleich zwischen Geräten und Mitgliedern gibt es fünf Wege:

| Methode | Eignung |
|---|---|
| **Sync-Code** (Text per Phone/Chat) | Schnellster Weg, funktioniert auch über Telefon |
| **QR-Code** | Camera-basiert, Initial-Verteilung |
| **JSON-Datei** (Mail/USB/Share) | Air-gapped Stäbe, formelle Übergabe |
| **HTTP-Backend** (eigener Server, WebDAV) | Automatische Synchronisation zwischen Geräten |
| **Lokales Verzeichnis** | Shared-Drive im Stabsraum |

### Automatischer Hintergrund-Sync

Seit V2.0 läuft die Synchronisation **opt-in pro Sync-Source** automatisch im Hintergrund:

- Polling-Intervall einstellbar (30–300 Sekunden)
- Pausiert automatisch bei Offline, im Hintergrund-Tab, bei Auth-Verlust
- Erkennt Konfliktsituationen (Drift) und zeigt sie sichtbar im Header an
- Recovery nach Crash, abgelaufener Authentifizierung oder Verbindungsabbruch

---

## Warum CRAM krisenstabil ist

### Funktioniert ohne Netzwerk

- Single-HTML-File (~750 KB), komplett offline lauffähig
- Keine externen Abhängigkeiten, keine CDN-Calls, keine API-Aufrufe nach außen
- Funktioniert auf USB-Stick, im air-gapped Stabsraum, ohne Internet
- Installierbar als Progressive Web App auf iPhone und Desktop

### Datenschutz by design

- **Keine Telemetrie**, keine Analytics, kein Phone-Home — niemals
- Daten werden ausschließlich lokal gespeichert (Browser-Storage)
- Optional Ende-zu-Ende-Verschlüsselung für Sync-Daten (AES-256-GCM, PBKDF2 mit 250.000 Iterationen, WebCrypto)
- Open Source (Apache 2.0), Code vollständig prüfbar

### Krisenstabs-tauglich entworfen

- **30-Tage-Audit-Log** für nachträgliche Lessons-Learned-Analyse
- **Vier Druck-Templates** (V2.2): Wandtafel-Übersicht (mit Auto-Fit auf Eine-Seite), Rollendetail, Telefonliste, Team-Pools — A4/A3/Letter, Hoch- und Querformat. Kritische Rollen dual codiert (Farbe + Glyph) für Schwarzweiß-Druck.
- **Mehrsprachig** (Deutsch, Englisch, Spanisch, Französisch, Chinesisch)
- **Mobile-tauglich** — iPhone-Safari mit korrekten Tap-Targets und Safe-Area-Handling

### Software-Qualität

- Kein Build-Step, kein Package-Manager, kein Framework-Lock-in — eine HTML-Datei
- Sechs unabhängige interne Audits durchgeführt (Security, Stabilität, Mobile, Resilienz, Regression, Doku)
- Pen-Test als reproduzierbare Regression im Repository
- Vollständige Source-of-Truth-Markdown-Dokumentation (DE + EN) plus PDF-Handbücher

---

## Anwendungsfälle

### Krisenstab im IT-Security-Incident

> Cyber-Angriff um 02:47 Uhr. Der SOC-Lead ist im Urlaub. CRAM zeigt sofort, dass die Vertretung Dr. M. erreichbar ist, die nächste Vertretung Dr. K. ebenfalls. Die Bereitschaft auf Tier 2 sieht über die Suche, wer Forensik-Expertise hat — drei Mitarbeiter sind aktuell verfügbar. Während der Lead-Eintrifft, hat die erste Triage bereits begonnen.

### Konzern-weite Eskalation

> Drei Krisenstäbe (HQ + zwei Töchter) arbeiten parallel. CRAM auf Stab-Tablets, synchronisiert über internen HTTP-Server alle 30 Sekunden. Konfigurations-Änderungen werden sichtbar als Drift markiert, jeder Stab entscheidet bewusst über Übernahme.

### Tabletop-Übung

> Vor der Jahres-Übung: Demo-Konfiguration laden, Krisenfall durchspielen ohne Echtdaten zu beeinträchtigen. Nach der Übung: Audit-Log zeigt Entscheidungs-Sequenz für die Nachbesprechung.

### Bereitschafts-Wochenende

> Telefonliste mit Substitutionsketten als PDF drucken, in den Wachraum hängen. Wer in der Nacht angerufen werden muss, steht klar lesbar in der Kette — primary, sub 1, sub 2 — mit Telefonnummern.

---

## Was CRAM bewusst nicht ist

Klare Abgrenzung:

- **Kein Krisenmanagement-Komplett-System** — CRAM verwaltet Rollen und Verfügbarkeit, nicht Aufgaben, Lagebilder oder Entscheidungsprotokolle
- **Kein HR-Tool** — Stamm-Personaldaten leben anderswo, CRAM zieht nur Namen und Kontakt
- **Keine Mobile-App** — bewusst Web-App, weil App-Store-Distribution Krisenstabs-Einsatz verzögert
- **Kein Cloud-Service** — kein Vendor-Lock-in, keine SaaS-Abhängigkeit

---

## Kosten und Betrieb

| Position | Kosten |
|---|---|
| **Software-Lizenz** | 0 € (Apache 2.0) |
| **Server-Infrastruktur** | optional — eigener HTTP-Server für Sync, kann auch ohne genutzt werden |
| **Wartung** | minimal — eine HTML-Datei aktualisieren bei Release |
| **Schulung** | erfahrungsgemäß 15–30 Minuten pro Bereitschafts-Mitglied |
| **Support** | Community via GitHub, kein kommerzieller Support |

---

## Wer das Werkzeug nutzt

Primär: IT-Sicherheits-Teams, SOC- und Incident-Response-Funktionen, Krisenstabs-Strukturen in mittleren und größeren Organisationen.

Sekundär: jede Organisation mit Bereitschaftsdiensten und Vertretungslogik, die ohne Backend-Infrastruktur auskommt.

---

## Verfügbarkeit

- **Code & Releases:** https://github.com/Artaiios/CRAM
- **Lizenz:** Apache 2.0
- **Sprache:** Single-File HTML, vanilla JavaScript, keine Build-Pipeline
- **Browser-Kompatibilität:** Chrome/Edge, Safari (Desktop + iOS), Firefox (mit Einschränkungen beim QR-Scanner)

---

**Stand:** V2.2.0 — Mai 2026
**Lizenz:** Apache 2.0
**Kontakt:** Patrick Zeller · patrick.zeller.ger@gmail.com
