# CRAM — Handbuch

Dieses Handbuch beschreibt den Betrieb von CRAM — dem Crisis Role Availability Manager. Es ist in zwei Teile gegliedert: der **Anwenderteil** richtet sich an alle Mitglieder eines Krisenstabs, die mit dem Tool während eines Ereignisses arbeiten. Der **Administrationsteil** richtet sich an diejenigen, die die Konfiguration pflegen, neue Versionen verteilen und für den Betrieb zuständig sind.

![Übersicht des Organigramms mit geladener Enterprise-Demo-Konfiguration](screenshots/01-main-chart-overview.png)

> Screenshots zeigen die enthaltene Enterprise-Demo-Konfiguration (`cram-demo-enterprise-en.json`) auf englischer UI-Sprache. Echte Organisationsdaten werden nie gezeigt.

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

![Roster-Sidebar mit höherer Dichte — Abwesenheiten oben, aktive Besetzungen nach Rolle gruppiert](screenshots/02-roster-density-overview.png)

![Hauptansicht mit geöffnetem People-Tab — Organigramm und Personenverzeichnis nebeneinander](screenshots/03-main-view-with-people-sidebar.png)

## Rollenkarten verstehen

Jede Rollenkarte zeigt folgende Informationen:

- **Rollenname** oben (beispielsweise „Crisis Manager")
- Ein **Blitz-Symbol**, wenn die Rolle als kritisch markiert ist
- Der **aktuelle Besetzer** mit seiner Rangstufe — `PRIMARY` bei der planmäßigen Person, `SUB1`/`SUB2` wenn eine Vertretung eingesprungen ist
- Ein **Replacing-Hinweis**, falls jemand anders als der Primärbesetzer vertritt — die vertretene Person wird durchgestrichen angezeigt
- Unten die vollständige **Vertretungskette** (`CHAIN`): Primär → Sub1 → Sub2 → … mit durchgestrichenen Einträgen für abwesende Personen

Ein **Schloss-Symbol** oben rechts zeigt an, dass diese Rolle manuell zugewiesen wurde und nicht der automatischen Logik folgt.

![Rollenkarte mit aktiver manueller Zuordnung — Schloss-Badge und gepinnte Person sichtbar](screenshots/08-manual-assignment-active.png)

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

CRAM visualisiert solche Kaskaden mit animierten gestrichelten Pfeilen zwischen den betroffenen Rollenkarten. Das macht auf einen Blick sichtbar, welche Vertretungsketten aktuell unter Druck stehen — eine wichtige Information für die Krisenstabsleitung, wenn es darum geht abzuschätzen, wie robust die aktuelle Aufstellung ist.

![Kaskaden-Visualisierung mit Pfeilen von Heim- zu Ziel-Rollen](screenshots/06-cascade-visualization.png)

![Mehrstufige Kaskade — mehrere Vertretungen gleichzeitig, kritische Ziele mit roten Pfeilen](screenshots/07-cascade-multi-level.png)

Gibt es keine verfügbare Person mehr in einer Kette, wird die Rolle als **Unoccupied** markiert. Das entsprechende Pill in der Kopfleiste zeigt die Anzahl unbesetzter Rollen an; bei kritischen Rollen wird das Pill rot eingefärbt.

## Legende: Was die Farben und Symbole bedeuten

CRAM nutzt Farben und Animationen, um den aktuellen Zustand jeder Rolle und jeder Kaskade zu signalisieren. Die vollständige Legende:

### Linker Rand einer Rollenkarte — Zustand der Rolle

| Farbe | Zustand | Bedeutung |
|---|---|---|
| Grün | Primary | Der planmäßige Primär-Besetzer ist aktiv |
| Gelb | Substitute (Sub1) | Der erste Vertreter ist eingesprungen |
| Dunkel-Orange | Substitute (Sub2 oder tiefer) | Ein Vertreter zweiter oder späterer Stufe ist aktiv |
| Rot | Unoccupied | Niemand in der Kette verfügbar |
| Rot + pulsierend | Unoccupied + kritisch | Kritische Rolle unbesetzt — Aufmerksamkeit erforderlich |

### Rahmen und Umgebung der Karte — Sonderzustände

| Signal | Bedeutung |
|---|---|
| Violetter Rahmen + 🔒-Symbol | Rolle hat eine aktive manuelle Zuordnung |
| Violetter gestrichelter Rahmen + durchgestrichener Name | Manuell zugeordnete Person ist abwesend geworden |
| Gelbe Umrandung | Karte ist Teil einer Kaskade (nicht kritisch) |
| Gelbe Umrandung + Glow | Kaskaden-Ziel, nicht kritisch — hier springt gerade jemand ein |
| Rote Umrandung | Karte ist Teil einer kritischen Kaskade |
| Rote Umrandung + Glow | Kaskaden-Ziel auf einer kritischen Rolle |
| Abgedunkelt (50% Deckkraft) | Kaskaden-Ansicht ist aktiv und diese Karte ist nicht beteiligt |

### Kaskaden-Pfeile (nur sichtbar bei aktivierter Kaskaden-Ansicht)

| Farbe | Animation | Bedeutung |
|---|---|---|
| Gelb gestrichelt | langsamer Fluss | Vertretung in einer nicht-kritischen Rolle |
| Rot gestrichelt, dicker | schnellere Pulsation mit rotem Glow | Vertretung in einer **kritischen** Rolle — besonders beobachten |

Die Pfeilfarbe richtet sich nach der **Ziel-Rolle** (wohin vertreten wird), nicht nach der Heim-Rolle der Person. Ein grüner Vertreter, der eine rote Rolle auffängt, erzeugt einen roten Pfeil; ein Primär aus einer kritischen Rolle, der in eine unkritische Rolle einspringt, erzeugt einen gelben.

### Statuspills in der Kopfleiste — Gesamtzustand

| Farbe | Bedeutung |
|---|---|
| Grau (neutral) | Reine Info-Zählung, keine Aktion nötig |
| Gelber Rahmen | Aktiv, aber nicht kritisch — Vertreter sind eingesprungen |
| Rot + pulsierend | Mindestens eine kritische Rolle ist unbesetzt |

### Akzente in der Seitenleiste

| Element | Farbe | Bedeutung |
|---|---|---|
| Roster-Eintrag, linker Rand | Grün | Rolle durch Primär besetzt |
| Roster-Eintrag, linker Rand | Gelb | Rolle durch Vertreter besetzt |
| Roster-Eintrag, linker Rand | Dunkel-Orange | Rolle durch tieferen Vertreter besetzt |
| Roster-Eintrag, linker Rand | Rot | Rolle unbesetzt |
| People-Eintrag, linker Rand | Gelb | Person ist aktuell abwesend |

## Manuelle Zuordnung

Manchmal soll eine bestimmte Person eine Rolle halten — unabhängig von der automatischen Vertretungslogik. Beispiele: Der planmäßige Primär ist zwar verfügbar, aber mit einem anderen Thema ausgelastet; oder die Krisenstabsleitung hat operativ entschieden, dass eine bestimmte Vertretung einspringen soll.

Für diesen Fall gibt es die **manuelle Zuordnung**. Im Edit-Modus oder über den Pin-Button auf einer Rollenkarte öffnet sich ein Dialog, in dem eine Person aus der Gesamtliste ausgewählt werden kann. Die Zuordnung bleibt bestehen, bis sie explizit wieder aufgehoben wird („Release manual assignment").

![Dialog für manuelle Zuordnung — Suche und Auswahl der Person, die diese Rolle halten soll](screenshots/09-manual-assignment-modal.png)

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

![Sync-Code Sendeansicht mit Fingerprint, Zeichenzahl und Personenstatistik](screenshots/16-sync-code-send.png)

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

![QR-Transfer Sendeansicht — Scope-Auswahl, erzeugter QR-Code, Fragment-Fortschritt](screenshots/17-sync-qr-send-options.png)

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

![Daten → Export — Scope-Auswahl mit Runtime-State-Toggle](screenshots/19-data-export.png)

**Bedienung Import:**

1. Daten-Modal öffnen, Tab „↓ Import"
2. Datei auswählen — die Inhalte werden validiert
3. Vorschau prüfen (Anzahl Ebenen, Rollen, Personen)
4. „Import" klicken — bestehende Daten werden überschrieben

![Daten → Import — Vorschau mit Ebenen-/Rollen-/Personenzahl vor dem Anwenden](screenshots/20-data-import.png)

### Online-Sync (ab V1.2)

Für die **regelmäßige Statusabgleichung verteilter Teams** über das Netzwerk. Im Gegensatz zu Code/QR/Datei ist hier **kein Live-Kontakt** zwischen Sender und Empfänger nötig — jeder schickt seinen Stand an einen geteilten Server und holt sich von dort den aktuellen Gesamtstand.

In V1.2/V1.3 sind beide Aktionen **manuell** (zwei Buttons im Sync-Modal). Ab V2.0 gibt es zusätzlich einen **automatischen Modus pro Source** — opt-in, Default OFF (siehe Abschnitt „Auto-Sync (ab V2.0)" weiter unten).

**Zwei Backend-Typen werden unterstützt:**

- **HTTP-Server** — ein selbst gehosteter Endpunkt (nginx mit `dav_methods`, Caddy + WebDAV-Plugin, SharePoint-WebDAV, MinIO, Synology-NAS). Der Server hostet eine einzige Datei `state.json`. Setup-Hinweise siehe [`docs/server-setup.md`](server-setup.md).
- **Lokales Verzeichnis** — typisch ein Ordner, der von OneDrive / Dropbox / Google Drive zwischen Geräten synchronisiert wird. CRAM schreibt nur die Datei in den Ordner, der Cloud-Sync-Client des Anbieters macht die Verteilung. Kein eigener Server nötig.

**Eine Sync-Source einrichten:**

1. Edit-Modus aktivieren (✎ in der Kopfleiste)
2. Im Edit-Banner ⚙ **Einstellungen** klicken
3. Auf den Tab **Sync-Sources** wechseln
4. Wähle:
   - **+ Neue HTTP-Source** — Bezeichnung (frei wählbar, z.B. „Hauptserver intern"), URL des Endpunkts, Authentifizierung (None / Basic / Bearer)
   - **+ Lokales Verzeichnis** — Bezeichnung, dann „Verzeichnis wählen…" klicken; der Browser fragt nach einem Ordner; danach noch optional den Dateinamen anpassen (Default `cram-sync.json`)
5. **Verschlüsselung** ist standardmäßig aktiviert (Ende-zu-Ende, AES-256-GCM mit PBKDF2 aus deiner Passphrase). Vergib eine Passphrase und bestätige sie. **Notiere sie in einem Passwort-Manager** — CRAM speichert sie nur im Arbeitsspeicher und vergisst sie bei jedem Tab-Schließen.
6. Speichern.

Sobald die Source angelegt ist, erscheint links der Status-Pills in der Kopfleiste ein kleiner **Sync-Indikator** mit aktuellem Zustand: ✓ Synchron, ↑ Änderungen (lokale ungepushte Edits), ↻ Sync läuft, ✗ Fehler.

![Sync → Online — Pull/Push-Buttons pro Source mit aktuellem Zustand](screenshots/18-sync-online-status.png)

**Manuell synchronisieren:**

1. ⇄ **Sync** in der Kopfleiste öffnen
2. Kanal **🌐 Online (Server)** wählen
3. Pro Source siehst du zwei Buttons:
   - **↓ Vom Server holen** — lädt den Server-Stand und überschreibt deinen lokalen
   - **↑ Zum Server schicken** — sendet deinen lokalen Stand und überschreibt den Server-Stand
4. Bei verschlüsselten Sources fragt CRAM bei Bedarf nach der Passphrase (z.B. nach einem Tab-Neustart). Die Passphrase wird nicht gespeichert.

**Eine Source mit dem Team teilen — Sync-Bundle:**

Damit Kollegen gegen dieselbe Source synchronisieren können, exportierst du ein **Sync-Bundle**: ein JSON-Objekt mit allen nötigen Informationen (URL bzw. Dateiname, Auth-Daten, Salt, Passphrase).

1. In **Settings → Sync-Sources** auf der jeweiligen Source „Teilen" klicken
2. Modal zeigt das Bundle-JSON + einen Warnhinweis: **Bundle ist vertraulich**, enthält Passphrase und Anmeldedaten im Klartext
3. Über einen sicheren Kanal verteilen: Signal/Threema, Passwort-Manager-Eintrag, persönliche Übergabe. **NICHT per E-Mail oder normalem Chat schicken.**
4. Kollegin öffnet CRAM, Settings → Sync-Sources → **⇩ Bundle importieren**, fügt das JSON ein oder lädt es aus der Datei
5. CRAM zeigt eine Vorschau mit Source-Typ, URL/Dateiname, Verschlüsselungs-Status und einem Fingerprint-Vergleich. Wenn die Fingerprints nicht übereinstimmen, würdet ihr gegen unterschiedliche Stabs-Konfigurationen syncen — CRAM warnt deutlich.
6. „Übernehmen" — bei lokalen Verzeichnis-Bundles fragt CRAM jetzt nach dem lokalen Ordner (der Empfänger wählt seinen eigenen Pfad).

**Was beim Online-Sync versehentlich passieren kann:**

- **Server unerreichbar** — z.B. VPN aus, falsche URL: Sync-Indikator wird rot ✗ mit Fehlertext, lokale Daten bleiben unverändert
- **Wrong Passphrase** — beim Pull schlägt die Entschlüsselung fehl: „Decryption failed — wrong passphrase?". Über das Modal kannst du sie erneut eingeben
- **Versehentlich Klartext-Bundle teilen** — vor jedem Save wird mit `confirm()` nachgefragt, ob du Bundle ohne Verschlüsselung anlegen willst. Standard ist immer Encryption=ON
- **Falscher Fingerprint beim Import** — wirst gewarnt, kannst trotzdem importieren wenn du sicher bist (z.B. neuer Stab)

**Browser-Hinweis:** Firefox unterstützt den „Lokales Verzeichnis"-Typ nicht, weil Mozilla die File-System-Access-API ablehnt. HTTP-Sources funktionieren in jedem Browser. Wenn Firefox erkannt wird, blendet CRAM einen entsprechenden Hinweis-Banner im Sync-Sources-Tab ein.

### Sync vs. Data — was wann nutzen (V1.3)

Ab V1.3 ist der Online-Sync in zwei klar getrennte Werkzeuge aufgeteilt:

- **⇄ Sync → Online**: nur Status (Abwesenheiten + manuelle Zuweisungen) — die Daten, die sich im Krisenfall mehrfach pro Stunde ändern. Funktioniert **nur** bei identischer Stab-Konfiguration zwischen Server und lokal. Bei Mismatch sperrt die Sync-Action und verweist auf Data.
- **⇵ Data → Online**: komplette Konfiguration + Status — die strukturellen Änderungen, die selten passieren (neue Rolle, umstrukturierter Stab, neue Person). Funktioniert immer, mit explizitem Bestätigungs-Dialog.

Die Trennung ist Sicherheit: Status-Sync kann nicht versehentlich die Stab-Struktur überschreiben.

**Praxisflows:**

- *Routine im Krisenfall (Abwesenheiten ändern):* ⇄ Sync → Online → „Status holen" oder „Status schicken". Schnell, zwei Klicks.
- *Strukturelle Stab-Änderung:* Im Edit-Mode die Konfiguration anpassen, dann ⇵ Data → Online → „Lokalen Stand auf Server schicken". Server-Stand wird mit Bestätigung überschrieben.
- *Erstes Mal Bundle importieren:* Nach dem Import fragt CRAM: „Server hat bereits einen Stand — jetzt übernehmen?" → Ja drücken, fertig.

**Awareness-Indikator (im Header):** Wenn nach einem Server-Probe (Sync- oder Data-Modal geöffnet) festgestellt wird, dass die Konfigurationen abweichen, wechselt der Indikator auf rotes „⚠ Konfig-Drift" — anklickbar, springt direkt zu Data → Online.

![Daten → Online — Voll-Konfig + Status mit explizitem Bestätigungsdialog](screenshots/21-data-online-full-config.png)

### Auto-Sync (ab V2.0)

V2.0 ergänzt einen **Hintergrund-Poller pro Source**, damit Status-Updates ohne manuellen Klick zwischen Geräten verteilt werden. Der Modus wird **pro Source einzeln** aktiviert. Default nach Update von V1.x ist **OFF** — die manuellen Buttons funktionieren weiter wie vorher.

![Einstellungs-Modal, Tab Sync-Sources — Auto-Sync-Modus und Polling-Intervall pro Source](screenshots/14-settings-sync-sources-tab.png)

Nach dem Update von V1.3 zeigt CRAM beim ersten Öffnen des Sync-Tabs einmalig ein Migrations-Banner. Es erklärt das neue Modus-Feld und den Default-OFF-Zustand.

**Auto-Sync aktivieren:**

1. Edit-Modus → ⚙ Einstellungen → Tab **Sync-Sources**
2. Pro Source erscheint ein **Auto-Sync-Akkordeon** mit folgenden Optionen:
   - **Modus** (Toggle):
     - `off` — kein Auto-Sync (Default)
     - `pull` — nur regelmäßig vom Server holen (passiv konsumieren)
     - `push` — bei lokalen Änderungen sofort schicken (aktiv publizieren, kein Polling)
     - `bidirectional` — beides
   - **Polling-Intervall:** Slider 30 / 60 / 90 / 120 / 180 / 300 Sekunden
3. Sobald Auto-Sync aktiv ist, zeigt der Header-Indikator im Auto-Modus zusätzlich eine **Live-Countdown** zur nächsten Aktion: „Synced vor 12s · nächster in 18s".

**Verhalten bei besonderen Zuständen:**

- **Tab im Hintergrund:** Polling-Intervall wird ×4 gedehnt. Beim Zurückwechseln des Tabs holt CRAM sofort den aktuellen Stand, unabhängig vom Polling-Cycle.
- **Browser offline (`navigator.onLine = false`):** Polling pausiert komplett, keine Retries im Leerlauf. Sidebar zeigt „Offline seit HH:MM". Sobald Browser wieder online ist, ein sofortiger Resume-Tick.
- **Auth-Verlust (401/403):** Auto-Mode wird automatisch auf OFF gesetzt. Ein persistentes Badge im Sync-Tab und im Settings-Akkordeon zeigt „Authentifizierung abgelaufen — neu anmelden". Beim nächsten Tab-Fokus erscheint einmalig ein Catch-Up-Toast mit dem Zeitpunkt des Auth-Verlusts.
- **Passphrase fehlt** (z.B. nach Tab-Neustart bei verschlüsselter Source): Auto-Sync pausiert, Badge „Passphrase erforderlich" am Akkordeon. User-Aktion: Passphrase nachreichen.
- **Datei-Zugriff verloren** (S5, lokales Verzeichnis — nach Reboot oder Drittprozess): Hard-Pause, keine Retries. Sidebar zeigt „Dateizugriff erneut bestätigen" mit Button „Zugriff gewähren".
- **Konflikt beim Push** (jemand anderes hat zwischenzeitlich geschrieben, ETag-Mismatch → HTTP 412): CRAM macht automatisch einen Pull, mergt lokal, pusht erneut. Wenn das nach 3 Versuchen nicht klappt, Toast „Sync-Konflikt — bitte prüfen".
- **Konfigurations-Drift** (Server hat eine andere Stab-Struktur): wird als eigene Fehlerklasse behandelt — Auto-Push pausiert für diese Source, Indikator wird rot „⚠ Konfig-Drift", modaler Dialog listet betroffene Sources mit den Optionen „Konfiguration vom Server übernehmen" (löst einen Voll-Pull über Data → Online aus) oder „Später".

**Crash-Recovery (Crash mitten im Push):**

Wenn der Tab während eines Pushes geschlossen wird, erkennt CRAM beim nächsten Start einen Sentinel und zeigt einen modalen Dialog: „Letzter Sync-Vorgang wurde unterbrochen — bitte manuell prüfen". Zwei Optionen: „Erneut pushen (mit Conflict-Check)" oder „Verwerfen". Bis zur Entscheidung wird Auto-Sync für diese Source pausiert.

**Toast-Benachrichtigungen:**

- *Stand aktualisiert von [User] um [Zeit]* — wenn ein eingehender Pull sichtbare Daten verändert hat
- *Dein Edit wurde durch eine neuere Version ersetzt — siehe Log* — wenn ein lokaler Edit im Sync-Konflikt verloren ging (dezent rot, 8 Sek)
- *Sync-Konflikt aufgelöst* — nach erfolgreichem Pull-Merge-Push-Retry

**Was Auto-Sync NIE tut:**

- Auto-Sync berührt **nur Status** (Abwesenheiten + manuelle Zuweisungen). Strukturelle Konfigurationsänderungen (neue Rolle, Person hinzugefügt, Stab umstrukturiert) gehen **immer** über Data → Online mit explizitem Bestätigungs-Dialog. Eine automatische Konfigurations-Übernahme ohne User-Klick ist baulich ausgeschlossen.
- Auto-Sync löst keinen modalen Dialog für eingehende Updates aus — nur Toasts. Die UX-Entscheidung dahinter: im Krisenfall darf kein Dialog die Aufmerksamkeit binden.

**Hinweis S5 (lokales Verzeichnis):** Die File-System-Access-API kennt kein ETag/If-Match. Bei zwei parallelen Schreibvorgängen auf einer S5-Source kann eine Version verloren gehen, ohne dass CRAM den Konflikt bemerkt. Wird im Settings-Akkordeon einer S5-Source mit einem Hinweis kenntlich gemacht. Auto-Pull auf S5 funktioniert, Auto-Push auf S5 ist in V2.0-rc1 deaktiviert.

**iPhone-Hinweis (PWA-Standalone-Mode):** Apple löscht PWA-Daten nach ca. 7 Tagen Inaktivität. Wer CRAM als PWA auf iOS installiert und nur sporadisch öffnet, riskiert Verlust der lokalen Sources, des Audit-Logs und der Konfiguration. Mitigation: regelmäßig JSON exportieren, **oder** sicherstellen dass eine HTTP-Sync-Source eingerichtet ist — nach Datenverlust ist ein einmaliger Pull genug, um wieder auf Stand zu sein. Der iPhone-Smoke-Test ist in V2.0-rc1 noch nicht gegen ein physisches Gerät verifiziert worden (siehe CHANGELOG „Deferred").

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

![Druck-Modal — Template-Auswahl mit Papiergröße und Ausrichtung](screenshots/22-print-template-chooser.png)

![Übersichts-Druckvorlage, gerendert für den Enterprise-Demo-Krisenstab](screenshots/23-print-overview-output.png)

Die Organisations- und Drucktitel, die in den Einstellungen gesetzt sind, erscheinen in der Kopfzeile jedes Ausdrucks. Sind sie leer, wird ein sprachabhängiger Standardtitel eingesetzt.

## Sprache wechseln

Die Sprachauswahl ist in der Kopfleiste. Aktuell verfügbar: Deutsch, Englisch, Spanisch, Französisch, Chinesisch. Die Auswahl bleibt zwischen Sitzungen bestehen.

![Sprachumschalter in der Kopfleiste — Deutsch, Englisch, Spanisch, Französisch, Chinesisch](screenshots/12-language-switcher.png)

## Darstellung

Das ☀/☾-Symbol in der Kopfleiste wechselt zwischen hellem und dunklem Theme.

Die Größenstufen **S/M/L/XL** passen die Darstellungsdichte des Organigramms an die Bildschirmgröße an. Bei Mobilgeräten gibt es eine eigene Layout-Variante mit Bottom-Navigation.

## Audit-Log lesen

![Audit-Log-Tab mit jüngsten Konfigurations-, Abwesenheits- und Sync-Ereignissen](screenshots/05-sidebar-audit-log.png)

![People-Tab — alphabetisches Verzeichnis mit Verfügbarkeitsstatus](screenshots/04-sidebar-people-tab.png)

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

Der Einstellungsdialog (⚙ im Edit-Modus) ist der Einstiegspunkt für Organisationsname, Drucktitel, Sprache, Dichte und den Sync-Sources-Tab.

![Einstellungen → Allgemein — Organisationsname, Drucktitel, Sprache, Dichte](screenshots/13-settings-general-tab.png)

Der About-Tab in den Einstellungen führt Version, Build-Hash und die Liste der eingebetteten Bibliotheken.

![Einstellungen → About — Version, Build-Hash, eingebettete Bibliotheken](screenshots/15-settings-about-tab.png)

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

Der Edit-Modus wird über das ✎-Symbol in der Kopfleiste aktiviert. In ihm werden auf den Rollenkarten Stift- und Pin-Handles eingeblendet, und die Sidebar-Tabs werden zu Editoren für Personen und Ebenen.

![Edit-Modus aktiv — Rollenkarten zeigen Inline-Edit-Handles](screenshots/10-edit-mode-active.png)

Eine Rolle besteht aus:

- **Name** (Pflicht) — sollte die Funktion beschreiben, nicht die aktuelle Person
- **Beschreibung** (optional, aber sehr empfohlen) — ein Satz, der die Aufgaben klar macht. Im Stress greift keiner mehr auf externe Dokumente zu.
- **Critical-Flag** — markiert die Rolle als kritisch; im Druck und in der Statistik wird sie hervorgehoben
- **Assignments** — Primär plus Vertreter in einer definierten Reihenfolge

![Rolle-bearbeiten-Modal — Name, Beschreibung, Critical-Flag, geordnete Vertretungskette](screenshots/11-edit-role-modal.png)

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
