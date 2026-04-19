# CRAM — Handbuch

Dieses Handbuch beschreibt den Betrieb von CRAM — dem Crisis Role Availability Manager. Es ist in zwei Teile gegliedert: der **Anwenderteil** richtet sich an alle Mitglieder eines Krisenstabs, die mit dem Tool während eines Ereignisses arbeiten. Der **Administrationsteil** richtet sich an diejenigen, die die Konfiguration pflegen, neue Versionen verteilen und für den Betrieb zuständig sind.

---

# Teil 1: Anwenderteil

## Das Tool zum ersten Mal öffnen

CRAM ist eine einzelne HTML-Datei. Ein Doppelklick genügt — die Datei öffnet sich im Standard-Browser. Es wird kein Server benötigt, keine Installation, keine Internetverbindung.

Beim ersten Start ist eine Beispiel-Konfiguration geladen, die einen kleinen Krisenstab für Cybersicherheitsvorfälle zeigt. Diese Konfiguration kann bearbeitet oder komplett ersetzt werden.

Wer CRAM regelmäßig nutzt, installiert sich das Tool als Progressive Web App (PWA):

- **Chrome/Edge Desktop**: Installations-Symbol rechts in der Adressleiste
- **Chrome Android**: Menü → „Zum Startbildschirm hinzufügen"
- **Safari iOS**: Teilen-Menü → „Zum Home-Bildschirm"

Nach der Installation startet CRAM in einem eigenen Fenster ohne Browser-Leiste. Der Zustand bleibt zwischen Sitzungen erhalten.

## Die Benutzeroberfläche auf einen Blick

Nach dem Start sieht man drei Hauptbereiche:

- **Kopfleiste**: Versionsanzeige, Statistik-Pills (Primär, Vertretung aktiv, Unbesetzt, Abwesend), Sprachauswahl, Aktions-Buttons (Sync, Daten, Drucken, Edit-Modus-Toggle, Theme-Umschalter)
- **Hauptbereich**: Organigramm mit Ebenen und Rollen. Jede Rolle wird als Karte dargestellt.
- **Seitenleiste rechts**: Drei Tabs — **Roster** (aktuelle Besetzung und Abwesenheitsliste), **People** (alle Personen nach Namen), **Log** (Audit-Protokoll)

## Rollenkarten verstehen

Jede Rollenkarte zeigt folgende Informationen:

- **Rollenname** oben (beispielsweise „Crisis Manager")
- Ein **Blitz-Symbol**, wenn die Rolle als kritisch markiert ist
- Der **aktuelle Besetzer** mit seiner Rangstufe — `PRIMARY` bei der planmäßigen Person, `SUB1`/`SUB2` wenn eine Vertretung eingesprungen ist
- Ein **Replacing-Hinweis**, falls jemand anders als der Primärbesetzer vertritt — die vertretene Person wird durchgestrichen angezeigt
- Unten die vollständige **Vertretungskette** (`CHAIN`): Primär → Sub1 → Sub2 → … mit durchgestrichenen Einträgen für abwesende Personen

Ein **Schloss-Symbol** oben rechts zeigt an, dass diese Rolle manuell zugewiesen wurde und nicht der automatischen Logik folgt.

## Eine Person als abwesend markieren

Im normalen Betrieb, also außerhalb des Edit-Modus, genügt ein Klick auf den Namen einer Person in einer Rollenkarte, um sie als abwesend zu markieren.

Im Dialog wählt man einen **Grund**:

- **Urlaub** (on leave)
- **Krank** (sick)
- **Dienstreise** (business trip)
- **Aktiv in anderer Rolle** (active in other role) — nützlich, wenn die Person in einem anderen Kontext gebunden ist
- **Sonstiges** (other)

Optional kann eine **Notiz** hinterlegt werden — beispielsweise eine voraussichtliche Rückkehrdauer oder eine Vertretungsanweisung.

Nach dem Bestätigen gilt die Person als abwesend. Alle Rollen, in denen sie eingesetzt ist, werden automatisch neu aufgelöst — falls sie Primär war, springt der erste verfügbare Vertreter ein. Die Kette wird sichtbar nachgezogen.

## Die Vertretungskaskade verstehen

Wenn die Anzahl der Abwesenheiten zunimmt, entstehen Kaskaden: Eine Rolle verliert ihren Primärbesetzer, die Vertretung springt ein — ist aber selbst Primär in einer anderen Rolle, sodass dort eine weitere Verschiebung ausgelöst wird.

CRAM visualisiert solche Kaskaden mit **roten gestrichelten Pfeilen** zwischen den betroffenen Rollenkarten. Das macht auf einen Blick sichtbar, welche Vertretungsketten aktuell unter Druck stehen — eine wichtige Information für die Krisenstabsleitung, wenn es darum geht abzuschätzen, wie robust die aktuelle Aufstellung ist.

Gibt es keine verfügbare Person mehr in einer Kette, wird die Rolle als **Unoccupied** markiert. Das entsprechende Pill in der Kopfleiste zeigt die Anzahl unbesetzter Rollen an; bei kritischen Rollen wird das Pill rot eingefärbt.

## Manuelle Zuordnung

Manchmal soll eine bestimmte Person eine Rolle halten — unabhängig von der automatischen Vertretungslogik. Beispiele: Der planmäßige Primär ist zwar verfügbar, aber mit einem anderen Thema ausgelastet; oder die Krisenstabsleitung hat operativ entschieden, dass eine bestimmte Vertretung einspringen soll.

Für diesen Fall gibt es die **manuelle Zuordnung**. Im Edit-Modus oder über den Pin-Button auf einer Rollenkarte öffnet sich ein Dialog, in dem eine Person aus der Gesamtliste ausgewählt werden kann. Die Zuordnung bleibt bestehen, bis sie explizit wieder aufgehoben wird („Release manual assignment").

Manuelle Zuordnungen werden mit einem 🔒-Symbol auf der Rollenkarte markiert und im Roster-Tab entsprechend ausgewiesen. Sie werden bei Sync-Übertragungen (Code-Sync und QR-Transfer) mitgeschickt.

## Daten auf ein anderes Gerät übertragen

CRAM bietet drei Wege, um Daten zwischen Geräten zu übertragen. Welchen man nutzt, hängt von der Situation ab.

### Sync-Code (Telefon)

Für schnelle **Status-Aktualisierungen am Telefon** gedacht. Ein Sync-Code ist eine kurze alphanumerische Zeichenfolge (typisch 20–40 Zeichen), die den aktuellen Abwesenheitsstatus und die manuellen Zuordnungen kodiert. Er wird in 4er-Gruppen formatiert, damit er telefonisch gut durchzugeben ist.

Voraussetzung: Sender und Empfänger haben dieselbe Basiskonfiguration. Die erste vier Zeichen des Codes sind ein Fingerprint der Konfiguration — stimmen sie auf beiden Seiten überein, passt das Schema und der Code wird akzeptiert.

**Bedienung:**

1. Sync-Modal öffnen (⇄-Button in der Kopfleiste)
2. Kanal „📟 Code-Sync (Telefon)" wählen — ist der Standard
3. Tab „↗ Senden" ist vorausgewählt — der Code erscheint sofort
4. Code durchtelefonieren oder per Chat schicken
5. Empfänger öffnet sein Sync-Modal, Tab „↙ Empfangen", gibt den Code ein und bestätigt

Eingegebene Codes werden live validiert: Eine falsch getippte Ziffer führt zu einem Fingerprint-Mismatch und wird erkannt, bevor etwas angewandt wird.

**Grenzen:** Der Sync-Code überträgt **nur den Status**, keine Konfiguration. Für Ersteinrichtung oder Änderungen an Rollen/Personen sind die anderen Wege zu nutzen.

### QR-Transfer (Kamera)

Für die **Erstverteilung einer Konfiguration** oder wenn Abweichungen in den Konfigurationen bestehen. Dabei werden die Daten auf dem Sendergerät als QR-Code angezeigt und vom Empfänger mit der Kamera eingelesen.

**Bedienung Sender:**

1. Sync-Modal öffnen, Kanal „📷 QR-Transfer (Kamera)" wählen
2. Tab „↗ Senden", dann Scope auswählen:
   - **Nur Konfiguration** — Rollen, Ebenen, Personen (ohne Status)
   - **Nur Status** — Abwesenheiten und manuelle Zuordnungen
   - **Konfiguration + Status** — alles
3. „QR-Code(s) erzeugen" klicken
4. Bei kleinen Configs erscheint ein einziger QR-Code, bei größeren eine Serie von Fragmenten
5. Bei mehreren Fragmenten „▶ Automatisch durchschalten" aktivieren — alle 2,5 Sekunden wird automatisch zum nächsten QR gewechselt

**Bedienung Empfänger:**

1. Sync-Modal öffnen, Kanal „📷 QR-Transfer (Kamera)", Tab „↙ Empfangen"
2. „Kamera starten" klicken — Berechtigung gewähren
3. Kamera auf Sender-Bildschirm richten. Die Fragmente werden automatisch erkannt; die Fortschrittspunkte unten zeigen, welche schon da sind (grün) und welche noch fehlen (grau).
4. Sind alle Fragmente da, wird die Vorschau angezeigt — mit Statistik zur Konfiguration und zum Status.
5. „Übernehmen" klicken — die Daten werden angewandt; ein Eintrag im Audit-Log dokumentiert den Import.

**Voraussetzungen:**
- Moderner Browser mit `BarcodeDetector`-API: Chrome, Edge, Safari. Firefox hat die API derzeit nicht.
- Für Kamerazugriff auf Mobilgeräten: HTTPS, localhost oder `file://` — HTTP funktioniert nicht.

### JSON Export/Import

Für **Archivierung, E-Mail-Versand oder Versionskontrolle**. Die Konfiguration (und optional der Status) werden als JSON-Datei heruntergeladen und können auf einem anderen Gerät importiert werden.

**Bedienung Export:**

1. Daten-Modal öffnen (⇵-Button)
2. Tab „↑ Export"
3. Bei Bedarf Häkchen „Include runtime state" setzen, um auch Status mit einzuschließen
4. „Download" klicken — es entsteht eine Datei `cram-export-YYYY-MM-DD-HH-MM-SS.json`

**Bedienung Import:**

1. Daten-Modal öffnen, Tab „↓ Import"
2. Datei auswählen — die Inhalte werden validiert
3. Vorschau prüfen (Anzahl Ebenen, Rollen, Personen)
4. „Import" klicken — bestehende Daten werden überschrieben

## Drucken

CRAM hat drei Druckvorlagen für den Papieraushang, und alle drei funktionieren mit A4, A3 oder Letter in Hoch- und Querformat.

**Übersicht**: Eine einseitige Wandtafel. Alle Rollen gruppiert nach Ebenen, jede mit ihrer aktuellen Primär-Besetzung und Telefonnummer in großer Schrift. Kritische Rollen sind rot hervorgehoben.

**Rollendetail**: Mehrseitiges strukturiertes Verzeichnis. Eine Sektion pro Ebene; jede Rolle zeigt den aktuellen Besetzer, die vollständige Vertretungskette mit Telefonnummern, eine etwaige manuelle Zuordnung.

**Personenliste**: Alphabetisches Telefonverzeichnis mit aktuellem Status. Abwesende Personen werden in einem separaten Abschnitt aufgeführt.

**Bedienung:**

1. Druck-Button (🖨) in der Kopfleiste
2. Template wählen
3. Papierformat und Ausrichtung wählen
4. „Druckdialog öffnen" — im Browser-Druckdialog kann als Ziel „Als PDF speichern" gewählt werden

Die Organisations- und Drucktitel, die in den Einstellungen gesetzt sind, erscheinen in der Kopfzeile jedes Ausdrucks. Sind sie leer, wird ein sprachabhängiger Standardtitel eingesetzt.

## Sprache wechseln

Die Sprachauswahl ist in der Kopfleiste. Aktuell verfügbar: Deutsch, Englisch, Spanisch, Französisch, Chinesisch. Die Auswahl bleibt zwischen Sitzungen bestehen.

## Darstellung

Das ☀/☾-Symbol in der Kopfleiste wechselt zwischen hellem und dunklem Theme.

Die Größenstufen **S/M/L/XL** passen die Darstellungsdichte des Organigramms an die Bildschirmgröße an. Bei Mobilgeräten gibt es eine eigene Layout-Variante mit Bottom-Navigation.

## Audit-Log lesen

Der Log-Tab zeigt alle Änderungen der letzten 30 Tage:

- Konfigurationsänderungen (welche Rolle, was wurde geändert)
- Abwesenheitsmeldungen (wer, mit welchem Grund, wann)
- Manuelle Zuordnungen (welche Person, welche Rolle, gesetzt/aufgehoben)
- Sync-Ereignisse (eingehende und ausgehende Codes, Imports)

Einträge älter als 30 Tage werden automatisch entfernt. Das Log wird rein lokal geführt — es gibt keine Synchronisation zwischen Geräten, jeder Client hat sein eigenes Log.

---

# Teil 2: Administrationsteil

## Rollenbild und Verantwortung

Der Tool-Administrator eines Krisenstabs ist typischerweise diejenige Person, die:

- die Rollenhierarchie mit der Krisenstabsleitung abstimmt
- Personen und deren Vertretungsketten pflegt
- die Konfiguration an alle Stabsmitglieder verteilt
- Updates der Applikation einführt und Feldtests koordiniert
- bei technischen Problemen als erster Ansprechpartner fungiert

Typischerweise ist das eine Person aus IT-Security, Business Continuity Management oder dem BKM-Office. Die Rolle ist nicht technisch anspruchsvoll — das Tool ist bewusst einfach gehalten —, aber erfordert Überblick über den Krisenstab und seine Prozesse.

## Die initiale Konfiguration aufbauen

Wer aus dem Stand startet, hat zwei Optionen:

**Option A — Vom Standard aus:** Nach dem ersten Öffnen ist eine Beispiel-Konfiguration geladen. Diese kann im Edit-Modus Schritt für Schritt an die eigene Organisation angepasst werden. Gut für kleine Stäbe (bis ~15 Rollen).

**Option B — Aus einer Demo-Datei:** Im Repository liegen zwei Enterprise-Demo-Configs mit 100 Personen und 40 Rollen in 7 Ebenen. Diese können importiert und dann angepasst werden. Schneller für größere Stäbe, da die grundlegende Struktur bereits vorhanden ist.

**Empfehlung:** Erst alle **Ebenen** anlegen, dann die **Personen** einpflegen, zuletzt die **Rollen mit Vertretungsketten**. In dieser Reihenfolge weil:

- Ohne Ebenen kann man keine Rollen anlegen
- Ohne Personen kann man keine Assignments machen
- Rollen und Assignments sind der aufwändigste Teil — spart Kontextwechsel

## Personen pflegen

Im Edit-Modus wird der People-Tab zu einem Editor. Eine Person hat:

- **Name** (Pflicht)
- **Telefonnummer** (optional, aber dringend empfohlen — ist die zentrale Kontaktinformation im Krisenfall)
- **E-Mail** (optional)

Empfehlungen:

- **Eindeutige Namen**: Bei häufigen Namen wie „Michael Weber" lieber Titel oder zweiten Vornamen ergänzen, um Verwechslungen in der Kaskadenansicht zu vermeiden.
- **Telefonnummern im internationalen Format**: `+49 170 1234567` statt `0170 1234567`. Macht Rückrufe von jedem Gerät aus sofort möglich.
- **Aktualisierung mindestens halbjährlich**: Menschen wechseln Stellen, Telefonnummern ändern sich. Ein Reminder im Kalender hilft.

## Rollen definieren

Eine Rolle besteht aus:

- **Name** (Pflicht) — sollte die Funktion beschreiben, nicht die aktuelle Person
- **Beschreibung** (optional, aber sehr empfohlen) — ein Satz, der die Aufgaben klar macht. Im Stress greift keiner mehr auf externe Dokumente zu.
- **Critical-Flag** — markiert die Rolle als kritisch; im Druck und in der Statistik wird sie hervorgehoben
- **Assignments** — Primär plus Vertreter in einer definierten Reihenfolge

**Leitprinzipien:**

- **Mindestens zwei Vertreter pro Rolle**, drei wenn die Rolle kritisch ist. Eine Kette ohne Tiefe reißt im Ernstfall ab.
- **Vertreter dürfen Rollen haben** — es ist explizit vorgesehen, dass dieselbe Person Primär in einer Rolle und Vertreter in einer anderen ist. Der Kaskaden-Algorithmus bildet das ab.
- **Keine Vertreter, die strukturell immer gleichzeitig abwesend sind** — wenn der Primär auf einer Konferenz ist und sein Sub1 in der Regel auch, ist die Vertretungskette wertlos.

## Namensgebung der Rollen

Tipps für robuste Rollenbezeichnungen:

- **Funktion statt Titel**: „IT Security Lead" statt „Leiter Informationssicherheit ABC GmbH". Titel ändern sich, Funktionen bleiben.
- **Keine Personennamen in Rollennamen**: „Legal & Compliance Lead" statt „Legal (Meier)".
- **Konsistent über Ebenen hinweg**: Entweder alle Rollen mit deutschem Namen oder alle mit englischem — nicht vermischen.
- **Eindeutig**: Keine zwei Rollen mit dem gleichen Namen, auch nicht auf verschiedenen Ebenen.

## Verteilung der Konfiguration

Die Konfiguration existiert initial nur auf dem Gerät, auf dem sie erstellt wurde. Um sie auf die Geräte der Stabsmitglieder zu bekommen, gibt es drei Wege:

### Weg 1: JSON-Datei per E-Mail / interner Fileshare

Am pragmatischsten für Organisationen mit funktionierendem IT-Arbeitsplatz und E-Mail.

1. Admin exportiert JSON (Daten → Export → ohne Runtime-State)
2. Datei an alle Stabsmitglieder verteilen
3. Jedes Stabsmitglied öffnet CRAM und importiert die Datei

**Hinweis**: Wer bereits eine Konfiguration hat, überschreibt sie. Der Import-Dialog zeigt vorher eine Preview — Anzahl Rollen, Personen etc.

### Weg 2: QR-Transfer (Gerät zu Gerät)

Wenn die Geräte räumlich zusammen sind (Kick-off-Meeting, Schulung) oder wenn E-Mail nicht sinnvoll ist.

1. Admin öffnet QR-Transfer, Scope „Konfiguration + Status"
2. Auto-Cycle aktivieren
3. Jedes Stabsmitglied scannt nacheinander mit der eigenen Kamera

**Vorteil**: Kein E-Mail-Anhang-Prozess, keine Dateibenennung, keine IT-Policy-Fragen. **Nachteil**: Nicht parallelisierbar.

### Weg 3: Hosting auf internem Webserver

Für größere Organisationen mit vielen Stabsmitgliedern, die die App regelmäßig nutzen.

1. HTML-Datei auf internen Server legen (z.B. `https://tools.intern.example.com/cram.html`)
2. Link an alle Stabsmitglieder
3. Beim Öffnen wird die Tool-Instanz je Browser (nicht je Gerät!) lokal initialisiert
4. Konfigurations-Erstverteilung wie Weg 1 oder 2

**Vorteile**: Zentrale Version, Kamera-Zugriff auch auf Mobilgeräten, PWA-Installation wird zum Startbildschirm-Icon. **Voraussetzung**: HTTPS-Endpoint vorhanden und aus allen benötigten Netzen erreichbar.

## Configuration-Changes später einspielen

Die initiale Verteilung ist einmalig. Änderungen (neue Rolle, Personalwechsel, geänderte Beschreibung) müssen aber regelmäßig durchgespielt werden.

**Empfohlener Prozess:**

1. Admin ändert die Konfiguration auf seinem Gerät
2. Admin exportiert JSON und legt es an einer vereinbarten Stelle ab (oder verteilt per E-Mail, oder bietet QR-Übertragung an)
3. Stabsmitglieder aktualisieren ihre Instanz bei Gelegenheit — spätestens vor dem nächsten geplanten Incident-Test

**Was NICHT passiert ohne explizite Aktion**: Die Geräte synchronisieren sich nicht automatisch. Das ist beabsichtigt — eine unbemerkte Konfigurationsänderung in einer laufenden Krise würde mehr Schaden anrichten als unterschiedliche Stände, wenn beides auffällt.

**Der Config-Fingerprint** (vier Hex-Zeichen, zu sehen im Sync-Modal und im Settings-Dialog) ist ein leichtes Hilfsmittel zur Erkennung von Abweichungen: Wenn zwei Instanzen unterschiedliche Fingerprints haben, haben sie unterschiedliche Konfigurationen. Das lässt sich bei jedem Sync-Code-Austausch nebenbei prüfen.

## Troubleshooting

### „QR-Scanner funktioniert nicht"

**Auf Firefox**: Nicht unterstützt. Der Browser hat keine native `BarcodeDetector`-API. Wir liefern bewusst keinen Polyfill aus. Alternative: JSON-Import.

**Auf Chrome/Edge/Safari, aber Kamera bleibt schwarz**: Vermutlich HTTP-Origin statt HTTPS. Lösung: Tool über HTTPS, localhost oder `file://` öffnen.

**Auf Chrome Android, Fehler „permission denied"**: Browser-Einstellungen → Seiten-Einstellungen → Kamera → für die Seite erlauben.

### „Der Sync-Code wird abgelehnt"

Wahrscheinlich Config-Fingerprint-Mismatch. Sender und Empfänger haben unterschiedliche Basiskonfigurationen. Lösung: Konfiguration abgleichen — entweder per JSON-Export/Import oder per QR-Transfer (Scope „Konfiguration").

### „Nach Reload ist alles weg"

`file://` + neuer Datei-Pfad = neue Origin = leerer localStorage. Wenn die HTML-Datei verschoben wurde, geht der Zustand verloren. Lösung: Datei am festen Ort lassen, oder über HTTPS hosten.

Im Privaten-/Inkognito-Modus gehen Daten beim Schließen verloren — das ist Browser-Verhalten, kein Bug.

### „Der Drucker bricht die Seite mittendrin ab"

Overview-Template bei großen Stäben (30+ Rollen) überläuft A4 Querformat. Lösung: A3 verwenden oder Role-Detail-Template benutzen, das automatisch umbricht.

### „Mehrere Mitarbeiter haben unterschiedliche Aufstellungen"

Erwartet, wenn nicht aktiv synchronisiert wird. Jeder Client hat seinen lokalen Status. Vor einem Treffen oder Test einmal per Sync-Code (schnell, nur Status) oder QR-Transfer (vollständig) angleichen.

## Datenschutz

CRAM verarbeitet personenbezogene Daten — Name, Telefonnummer, E-Mail, Abwesenheitsstatus. Das ist verarbeitungsrechtlich nicht triviale. Empfohlene Schritte:

1. **Zweckbindung dokumentieren**: „Zweck der Verarbeitung: Krisenstabs-Organisation im Notfall".
2. **Rechtsgrundlage festlegen**: In den meisten Fällen berechtigtes Interesse (Art. 6 Abs. 1 lit. f DSGVO) oder Einwilligung der Stabsmitglieder.
3. **Transparenz gegenüber den Betroffenen**: Jeder, der im Tool erfasst wird, soll wissen, dass er drin ist und welche Daten dort liegen.
4. **Löschkonzept**: Bei Ausscheiden aus dem Stab muss die Person aus der Config entfernt werden — auf allen Instanzen.
5. **Keine externen Übertragungswege nutzen, die Drittanbieter einsehen können**: E-Mail-Anhänge intern OK, Konfigurations-Upload auf öffentliche Fileshares nicht.

Bei Fragen zur konkreten Ausgestaltung: Datenschutzbeauftragten der eigenen Organisation einbinden.

## Release-Handling

Neue CRAM-Versionen werden als Tag auf GitHub veröffentlicht. Jeder Release enthält die HTML-Datei und die Demo-JSONs als Assets.

**Prozess beim Einspielen einer neuen Version:**

1. Neue Version aus GitHub-Releases herunterladen
2. Auf einem Testsystem öffnen und mit einer Export-JSON der produktiven Config laden
3. Alle kritischen Funktionen durchgehen: Bearbeiten, Abwesenheiten markieren, Sync-Code, QR-Transfer, Drucken
4. Falls alles funktioniert: an Stabsmitglieder verteilen, alte Version auf allen Geräten ersetzen
5. Änderungen im CHANGELOG prüfen — insbesondere auf Breaking Changes im Datenformat

**Backup vor dem Wechsel**: Immer zuerst die aktuelle Konfiguration samt Runtime-State exportieren. Wenn die neue Version ein Problem hat, kann man zurückrollen.

## Kontakt und Feedback

Bug-Reports und Feature-Wünsche bitte über den Issue-Tracker auf GitHub. Für alles andere siehe [CONTRIBUTING.md](../CONTRIBUTING.md).
