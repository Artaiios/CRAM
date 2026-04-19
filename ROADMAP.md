# CRAM — Roadmap

Stand: 19. April 2026, nach Release v1.0.0-rc1.2.

Dies ist eine lebende Liste. Prioritäten können sich durch Praxis-Feedback verschieben. Das Dokument liegt im Repo, damit Mitbenutzer nachvollziehen können, woran wir denken.

## Aktuelle Phase: RC-Erprobung

Ziel: Aus v1.0.0-rc1.2 wird entweder eine Final-Version v1.0.0, oder — falls Findings auftauchen — eine Serie von rc1.3, rc1.4, bevor das 1.0-Tag gesetzt wird.

Empfohlene Testdauer: 2 bis 3 Wochen aktiver Nutzung mit realistischen Daten und auf mindestens zwei verschiedenen Geräten.

---

## Vor v1.0.0 — Security-Nacharbeit (zwingend)

### S-01: Content Security Policy einbauen

**Priorität:** hoch. Blockt das 1.0-Release.

**Umsetzung:**
Ein Meta-Tag im `<head>` des Tools:

```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'none';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: blob:;
  font-src 'self' data:;
  connect-src 'self' blob: data:;
  manifest-src 'self' blob:;
  media-src 'self' blob: data:;
  base-uri 'none';
  form-action 'none';
  frame-ancestors 'none';
">
```

**Begründung der Kompromisse:**

- `script-src 'unsafe-inline'` ist unvermeidlich, weil CRAM bewusst als Single-File-Anwendung mit Inline-JavaScript gebaut ist. Das ist Architektur, nicht Schlamperei.
- `'unsafe-eval'` wird **nicht** zugelassen — das Tool nutzt kein `eval()` oder `new Function()` (Stichprobe geprüft).
- `data:` und `blob:` in `img-src`, `manifest-src`, `connect-src` sind für die PWA-Funktionalität nötig (Icon als Data-URI, Manifest als Blob-URL, QR-Codes werden als SVG inline gerendert).
- `frame-ancestors 'none'` verhindert Clickjacking.
- `base-uri 'none'`, `form-action 'none'` schließen weitere Angriffsvektoren.

**Test vor Release:**
Alle drei Transferkanäle durchgehen, QR-Scanner aktivieren, Kamera-Zugriff prüfen, PWA-Installation testen, Drucken testen. Wenn alles weiterhin funktioniert, CSP-Header committen.

**Zeitaufwand:** 2–3 Stunden inkl. Test. Ein Release-Commit.

---

### S-02: Systematische Verifikation von Nutzer-Input-Escaping

**Priorität:** hoch. Blockt das 1.0-Release.

**Ausgangslage:**
Der Code nutzt heute bereits `escapeHTML()` an 308 Stellen — das ist diszipliniert. Aber es gibt 55 `innerHTML=`-Zuweisungen mit Template-Literals, und bei dieser Menge ist nicht bewiesen, dass in **jeder** davon jeder Nutzer-Input durch `escapeHTML()` läuft.

**Konkrete Maßnahmen:**

1. **Audit mit Penetration-Test-Payload.** Eine Enterprise-Demo-Config mit bewusst bösartigen Strings in jedem Feld (Rollenname, Beschreibung, Personenname, Telefon, E-Mail, Notiz, Ebenen-Name, Organisations-Name, Drucktitel) bauen. Payload-Beispiele:
   - `<img src=x onerror=alert(1)>`
   - `"><script>alert(1)</script>`
   - `javascript:alert(1)`
   - `</div><iframe src=javascript:alert(1)>`
   - Unicode-Varianten mit Tricks wie `&#60;script&#62;`
   
   Diese Config in CRAM importieren. Alle Views durchklicken: Organigramm, alle Modals, alle drei Druckvarianten, Sidebar-Tabs, Audit-Log, Sync-Modal. Ergebnis: Wenn **irgendwo** ein Alert aufgeht oder eine Konsolen-Warnung erscheint, haben wir eine Lücke.

2. **Automatisierter Regressions-Test.** Die Payload-Config in die bestehenden Testsuiten aufnehmen. Das Test-Framework prüft, dass nach Rendering keine `<script>`, keine `onerror=`, keine `javascript:`-URLs im DOM auftauchen, die nicht aus dem Tool selbst kommen.

3. **Umstellung einzelner Stellen auf `textContent`.** Wo nur reiner Text angezeigt wird (Personen-Name in Sidebar, Telefonnummer, Rollenname in einer Karte), auf `textContent` umstellen. Das ist der systematisch sicherste Weg und eliminiert diese Stellen als Angriffsfläche permanent. `innerHTML` bleibt nur, wo tatsächlich HTML-Struktur aufgebaut wird.

**Priorisierung innerhalb S-02:**
- Schritt 1 (Pen-Test) zuerst — dauert 2–3 Stunden und schafft Klarheit über den Ist-Zustand
- Schritt 2 (Regressions-Test) nur wenn Schritt 1 Probleme aufdeckt, sonst optional für später
- Schritt 3 (textContent-Umstellung) sinnvoll für Hot-Paths, aber kein Blocker

**Zeitaufwand gesamt:** 1 Tag wenn alles sauber, 2–3 Tage wenn Lücken gefunden werden.

---

### S-03 (optional): Subresource Integrity für inline Libraries

**Priorität:** niedrig.

Die beiden eingebetteten Libraries (fflate, qrcode-generator) liegen inline als Code im HTML. Wenn jemand die Datei zwischen Release-Asset-Upload und Download manipulieren würde, wäre das nicht erkennbar. Im Moment ist das Risiko theoretisch, weil GitHub-Release-Assets per HTTPS ausgeliefert werden, aber für sehr defensive Szenarien (Air-Gap-Transfer, interner Mirror) wäre eine SHA-256-Signatur der Release-Assets sinnvoll.

Konkret: Neben jedem Asset auf der Release-Seite eine `.sha256`-Datei bereitstellen. Admin prüft vor Verteilung `sha256sum -c`.

**Aufwand:** eine Stunde pro Release.

---

## Vor v1.0.0 — Lizenz-Compliance (zwingend)

### L-01: MIT-Lizenztext für eingebettete Libraries einfügen

**Priorität:** hoch. Blockt das 1.0-Release.

**Problem:** CRAM bettet zwei MIT-lizenzierte Libraries inline ein (fflate 0.8.2 von Arjun Barrett; qrcode-generator 1.4.4 von Kazuhiko Arase). Die MIT-Lizenz verlangt ausdrücklich, dass der vollständige Lizenztext in allen Distributionsartefakten mitgeführt wird:

> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

Im aktuellen Code steht nur eine Kurzattribution (Autor + Version). Die geforderte Permission Notice fehlt. Das ist keine Kosmetik, sondern eine echte Lizenzverletzung.

**Umsetzung:**
- In der HTML-Datei direkt vor jedem Library-Code-Block einen `/*! … */`-Kommentarblock einfügen, der den kompletten MIT-Lizenztext der jeweiligen Library enthält (inkl. Copyright-Zeile des Urhebers).
- Zusätzlich in der `NOTICE`-Datei im Repo die beiden Lizenztexte aufnehmen (eine NOTICE-Datei existiert bisher nicht und wird neu angelegt — Apache-2.0 erlaubt beides ausdrücklich: die dritte-Party-Attributionen gehören in NOTICE, der Projekt-Lizenztext in LICENSE).
- Im `README` einen kurzen Abschnitt „Third-Party-Software" ergänzen, der auf NOTICE verweist.

Der `/*! … */`-Syntax wird verwendet (statt `/* … */`), weil viele JS-Minifier lizenzrechtlich relevante Kommentare mit `/*!` am Anfang standardmäßig erhalten — auch wenn wir aktuell nicht minifizieren, ist das die korrekte Konvention.

**Zeitaufwand:** 1 Stunde.

---

### L-02: qrcode-generator-Version dokumentieren

**Priorität:** mittel. Nicht blockierend, aber begründungspflichtig.

**Ausgangslage:** CRAM verwendet qrcode-generator 1.4.4. Die aktuelle Version ist 2.0.4.

**Bewertung der 2.0.x-Serie (Stand April 2026):** Die 2.0.x-Releases (2.0.1, 2.0.2, 2.0.4) drehen sich laut GitHub-Releases primär um TypeScript-Typings (Issue #120) und einen Bugfix für Issue #121. Für vanilla-JavaScript-Konsumenten wie CRAM ist der Unterschied funktional minimal. Wir nutzen drei API-Methoden: `qrcode(typeNumber, ecLevel)`, `addData()`, `make()`, `createSvgTag()`. Keine dieser API-Signaturen hat sich geändert.

**Entscheidung:** **Bei 1.4.4 bleiben.**

Die 2.0-Serie bringt für CRAMs Use-Case keinen funktionalen Mehrwert — wir profitieren weder von TypeScript-Typings noch von dem einen Bugfix für ein Szenario, das wir nicht nutzen. Jede Versionsänderung an einer Library, die QR-Codes korrekt generiert, hat dagegen ein nicht-null Regressionsrisiko. Das ist das klassische „never change a running system"-Szenario: Stabilität ist wichtiger als Aktualität.

**Umsetzung:** Im Code-Kommentar vor der Library explizit vermerken, dass die Version bewusst bei 1.4.4 gehalten wird, mit Begründung und dem Hinweis, dass bei einer bekannten Sicherheitslücke in 1.4.4 oder einer funktionalen Notwendigkeit das Upgrade auf 2.0.x (oder höher) durchgeführt würde.

**Wiedervorlage:** Einmal pro Jahr prüfen: Gibt es in der 1.4.x- oder 2.0.x-Serie einen Security-Advisory (npm audit, GitHub Security Advisory)? Wenn ja, Upgrade einplanen. Wenn nein, weiterhin bleiben.

**Zeitaufwand:** 15 Minuten (nur Kommentar).

---

### L-03: SPDX-Header in der HTML-Datei

**Priorität:** niedrig. Nicht blockierend, aber billig und sinnvoll.

**Umsetzung:** Direkt nach `<!DOCTYPE html>` zwei HTML-Kommentarzeilen einfügen:

```html
<!DOCTYPE html>
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Patrick Zeller -->
<html lang="de">
```

**Nutzen:** Automatisierte Compliance-Tools (scancode, reuse.software, SBOM-Generatoren) erkennen die Lizenz ohne dass ein Mensch den Header manuell interpretieren muss. Macht CRAM für Enterprise-Integration leichter freigabefähig.

**Zeitaufwand:** 5 Minuten.

---

### L-04: SBOM (Software Bill of Materials) als Release-Asset

**Priorität:** mittel. Nicht blockierend für 1.0, aber stark gewünscht für Enterprise-Integration.

**Format-Entscheidung:** **CycloneDX 1.5 JSON**.

Begründung: Es gibt zwei etablierte Formate — SPDX und CycloneDX. Beide sind für unseren Zweck geeignet, aber CycloneDX ist in der Industrie-Security-Welt (OWASP, Dependency-Track, DefectDojo, Snyk, Dependabot) das verbreitetere Format und lässt sich mit weniger Mühe maschinell konsumieren. SPDX ist in der Open-Source-Lizenz-Welt dominant, aber aufwendiger im Handling. Für eine Projekt-Größe wie CRAM reicht CycloneDX vollkommen.

**Inhalt der SBOM:** Minimaler, aber vollständiger Eintrag pro Komponente:

- CRAM selbst (Apache-2.0, Patrick Zeller, Version aus Release-Tag)
- fflate 0.8.2 (MIT, Arjun Barrett, mit PURL und Repository-URL)
- qrcode-generator 1.4.4 (MIT, Kazuhiko Arase, mit PURL und Repository-URL)

Dazu Hash-Angaben (SHA-256) für jede Komponente, damit Downstream-Consumer die Integrität verifizieren können.

**Umsetzung:**

1. Python-Script `/scripts/generate_sbom.py` im Repo, das aus einer kleinen Template-Struktur und den Hash-Werten der Library-Blöcke eine gültige CycloneDX-1.5-JSON erzeugt.
2. Script wird manuell vor jedem Release ausgeführt; Output `cram-sbom.cdx.json` (die Endung `.cdx.json` ist CycloneDX-Konvention).
3. Die SBOM wird als zusätzliches Release-Asset mit hochgeladen.
4. Im README-Abschnitt „Third-Party-Software" kommt ein kurzer Verweis auf die SBOM.

**Zeitaufwand:** 1–1,5 Stunden (Script schreiben, einmalig; danach 2 Minuten pro Release).

**Alternative zu SBOM-Skript:** Tools wie `cyclonedx-npm` oder `cyclonedx-python-lib` können das automatisieren, aber sie erwarten eine `package.json` oder ein Python-Projekt. CRAM hat bewusst keines von beiden. Ein 50-Zeilen-Python-Script, das die drei Komponenten hart kodiert, ist pragmatischer und hat keine Build-Ketten-Abhängigkeit.

---

## Vor v1.0.0 — funktionale Nacharbeit (soweit Praxis zeigt)

### T-01: Praxis-Test-Ergebnisse einarbeiten

Alles was aus 2–3 Wochen Tests in den nächsten Tagen kommt. Vermutliche Kategorien:
- UI-Polish (manche Dialoge sind enger oder weiter als erwartet)
- Browser-spezifische Quirks (insbesondere Safari iOS)
- Fehlende oder irreführende Hinweistexte
- Erkannte Edge-Cases bei Kaskaden-Berechnung mit tiefen Hierarchien

Jedes Finding wird als GitHub-Issue erfasst. Kleinere Issues werden in einem Sammel-Release (rc1.3) gefixt. Wirklich kritische Findings (Datenverlust, falsche Kaskaden) bekommen eigene Bugfix-Releases.

---

## Nach v1.0.0 — 1.x Feature-Set

Die folgenden Punkte wurden in früheren Sessions diskutiert aber zurückgestellt. Sie sind nicht zwingend, würden CRAM aber in konkreten Situationen verbessern.

### F-01: Suche über Rollen und Personen

Strg+K öffnet ein Suchfeld. Eingabe „CISO" findet die Rolle. Eingabe „Martinez" findet die Person. Klick auf ein Ergebnis scrollt zur Rollenkarte oder öffnet den Personen-Detail-Dialog. Bei großen Stäben (40+ Rollen, 100+ Personen) eine echte Zeitersparnis.

**Aufwand:** 1–2 Sessions.

### F-02: Audit-Log-Filter und CSV-Export

Der Log-Tab bekommt oben einen Filter (nach Zeitraum, nach Typ, nach Person). Export als CSV für Nachbesprechungen und Compliance-Dokumentation. Heute muss man dazu Screenshots machen — nicht praxistauglich bei echten Incidents.

**Aufwand:** 1 Session.

### F-03: Tags für Personen

Personen bekommen Freitext-Tags (z. B. „Nachtschicht", „Remote verfügbar", „Sprecht Englisch"). Tags werden in der People-Liste angezeigt und als Filter nutzbar. Basis für F-04.

**Aufwand:** 1 Session.

### F-04: Bulk-Operationen

Mehrere Personen gleichzeitig als abwesend markieren (z. B. „alle mit Tag 'Standort-München' als 'Dienstreise' markieren"). Nützlich bei geplanten Events wie Firmenveranstaltungen oder Weiterbildungen. Braucht F-03.

**Aufwand:** 1 Session.

### F-05: Dunkel-/Hellmodus automatisch nach Systemeinstellung

`prefers-color-scheme`-Media-Query respektieren als Default, weiterhin manuelle Überschreibung möglich. Kleiner, aber spürbarer Polish für Nutzer, die System-weite Theme-Einstellungen pflegen.

**Aufwand:** 1–2 Stunden.

### F-06: Drucklayout „Kontakt-Karte"

Vierte Druckvorlage: eine A5/A6-Karte pro Stabsmitglied mit den eigenen Rollen, direkten Vertretern und deren Telefonnummern — so dass jeder eine persönliche Karte hat, die er in die Tasche steckt. Aus dem heutigen Role-Detail-Template ableitbar.

**Aufwand:** 0.5–1 Session.

### F-07: Drilldown von Statuspill zu betroffener Liste

Klick auf „Sub. active 12" öffnet eine Liste der 12 aktiven Vertretungen. Klick auf „Unoccupied 1" zeigt die eine unbesetzte Rolle. Reine Navigation, keine neue Semantik.

**Aufwand:** 1 Session.

---

## Größerer Sprung — 2.x, optional

### V-01: Optionaler Online-Sync

Der größte konzeptionelle Schritt. Würde bedeuten:
- Optionales Backend (selbst-hostbar, Referenz-Implementierung Node.js / Express / SQLite)
- Client bekommt ein Settings-Feld „Sync-Server-URL"
- OIDC-Auth gegen Entra ID, Google Workspace, Keycloak
- Differenz-Sync statt Voll-Replacement
- Konflikt-Auflösung bei gleichzeitiger Bearbeitung

**Erhebliche Konsequenzen:**
- Single-File-Charakter für den Client bleibt, aber das Gesamt-System ist kein Single-File mehr
- Server-Betrieb und Pflege wird zum laufenden Aufwand
- Für Enterprise-Einsatz mit 50+ Stabsmitgliedern ein Gewinn, für kleine Stäbe Overkill

**Sinnvoll nur, wenn Praxis-Einsatz zeigt, dass der aktuelle Offline-Ansatz nicht reicht.** Nicht aus der Hand schießen.

**Aufwand:** 5–10 Sessions für Spec, Referenz-Backend, Client-Integration, Tests.

### V-02: Historische Ansicht

Über den 30-Tage-Audit-Log hinausgehend: Snapshots einer Konfiguration zu bestimmten Zeitpunkten (quartalsweise, nach größeren Änderungen) speichern und rückwärts einsehen können. Sinnvoll für Audit-Szenarien nach echten Vorfällen, um nachzuweisen „so sah der Stab zum Zeitpunkt X aus".

Aufwand vs. Nutzen ist bei den meisten Organisationen wahrscheinlich nicht günstig. Erstmal als Idee parken.

**Aufwand:** 2–3 Sessions.

---

## Prozess-Roadmap — nicht technisch

### P-01: Beta-Feedback kanalisieren

Nach den 2–3 Wochen Testphase ein strukturiertes Feedback-Gespräch mit den Testern. Templatisierte Issue-Form auf GitHub ist da (feature_request.md, bug_report.md), aber Menschen füllen oft lieber ein Gespräch aus. Nach dem Gespräch die Findings in Issues überführen.

### P-02: Versions-Kommunikation

Mit dem 1.0-Release eine kurze Kommunikations-Kampagne: eine Ankündigung (Blog-Post, LinkedIn-Beitrag, interner Newsletter je nach Zielgruppe). Ziel nicht Marketing, sondern dass potenzielle Nutzer das Tool überhaupt finden. Wenn's nur drei Leute im eigenen Unternehmen benutzen, ist das völlig in Ordnung — dann braucht's keine Kampagne.

### P-03: License-Kompatibilitäts-Scan

Für Enterprise-Einsätze wichtig: Apache-2.0 ist kompatibel mit typischen Unternehmens-Lizenzen, aber eine schnelle Zertifikats-Prüfung mit Tools wie `scancode` oder `license-checker` auf das gesamte Projekt stellt sicher, dass kein versehentlich eingebauter GPL-Schnipsel darin ist.

---

## Anti-Roadmap — was wir bewusst NICHT tun

Dinge, die in Diskussionen gerne vorgeschlagen werden, aber nicht zum Projekt passen:

- **npm-Package-Publishing.** CRAM ist eine Anwendung, keine Library. Ein `npm install cram` würde den Zweck verzerren.
- **Docker-Image.** Overkill für eine Single-File-HTML-Anwendung. Wer einen Webserver hat, kann die Datei ausliefern. Wer keinen hat, nimmt `file://`.
- **TypeScript-Refactoring.** Der Code ist bewusst vanilla JavaScript, damit jeder Admin mit Basis-Webkenntnissen ihn lesen und modifizieren kann. TypeScript würde eine Build-Kette erzwingen und das Single-File-Prinzip brechen.
- **Build-Tools / Bundler.** Aus demselben Grund.
- **Eigene Icons-Library / CSS-Framework.** Wir halten die CSS-Variablen-basierte Minimal-Implementierung bei. Tailwind etc. würde die Datei massiv vergrößern ohne erkennbaren Gewinn.
- **Plugin-System.** CRAM ist ein Tool mit klarem Scope. Erweiterbarkeit über Plugins hätte einen enormen Design-Aufwand und würde die Oberfläche zerfasern. Wer es anpassen will, forkt und editiert — das ist die vorgesehene Extension-Methode.

---

## Reihenfolge-Vorschlag

1. **Jetzt:** Test-Phase mit rc1.2 starten (2–3 Wochen).
2. **Parallel dazu (ein Batch-Release rc1.3):** L-01 (MIT-Lizenztexte + NOTICE-Datei), L-02 (qrcode-generator-Begründung im Code), L-03 (SPDX-Header), L-04 (SBOM als Release-Asset), S-01 (CSP). Das sind alles rein textuelle oder deklarative Änderungen ohne Funktionsauswirkung, lassen sich in einer Session umsetzen und landen als rc1.3.
3. **Nach Test-Phase:** S-02 (Input-Audit) mit Pen-Test-Config, plus alle Findings aus der Praxis. Landet als rc1.4.
4. **Danach:** 1.0-Release, wenn alles sauber.
5. **Nach 1.0:** Feature-Set 1.x in Priorität F-07 (Drilldown, günstig) → F-01 (Suche) → F-02 (Audit-Export) → F-05 (Auto-Theme) → F-03/F-04 (Tags + Bulk) → F-06 (Kontakt-Karte).
6. **V-01 (Online-Sync) nur, wenn Praxis das Bedürfnis zeigt.** Nicht aus Prinzip.
