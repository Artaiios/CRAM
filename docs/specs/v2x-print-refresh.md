# Print-Layout-Refresh — Diagnose und Vorschläge (V2.x)

Status: Diagnose, nicht implementiert. Geplant als V2.x-Polish-Task (siehe
ROADMAP). Hintergrund: Feedback aus der V2.0-GA-Vorbereitung — Patrick
beschreibt die drei Print-Templates als "unübersichtlich und chaotisch".

Dieses Dokument seziert den Status quo (Code in `crisis-role-manager.html`
Zeilen ~3633–3921 CSS und ~15357–15601 JS), nennt konkrete Probleme und
skizziert eine Richtung. Es ist bewusst Diagnose, nicht Lösungs-Design im
Detail — das gehört in eine eigene Session, idealerweise zusammen mit dem
V2.1 Team-Pool-Konzept.

---

## Aktueller Stand

CRAM bietet drei Druckvarianten, ausgewählt im Print-Modal:

| Variante | Funktion | Default-Format |
|---|---|---|
| `overview` | Ein-Seiten-Wandchart mit allen Rollen und aktuell Besetzenden | A4 quer / A3 quer |
| `detail` | Mehrseitige Rollen-Liste mit vollständiger Substitution-Kette + Kontakt | A4 hoch |
| `persons` | Alphabetische Personen-Übersicht, "absent" oben, "available" unten | A4 hoch |

Gemeinsame Header-Zeile: Drucktitel + Organisationsname links,
Druckdatum + Config-Fingerprint rechts, getrennt durch 2pt-Linie.

Skalierung: `--print-scale` wird aus der kurzen Papierseite gegen A4
(210mm) berechnet, gedeckelt auf `0.85`–`1.6`. Alle Schriftgrößen
multiplizieren mit diesem Faktor. Funktional sauber, aber führt zu sehr
kleinen Größen bei vielen Spalten in `overview` und sehr großen Headlines
auf A3.

### Overview

- **Zweck:** Wand-Chart im Krisenraum. Was sieht man auf 3–5m Abstand?
- **Status quo:** Grid mit `--p-cols` Spalten (`computeOverviewColumns`,
  Ziel 62mm pro Spalte, gedeckelt auf 6). Ein Spalten-Block pro Level. In
  jedem Block: Level-Name in Uppercase mit Unterstrich, darunter pro
  Rolle ein Karten-Element mit eigenem Rahmen, linker Akzentlinie und
  bei `critical` zusätzlich rotem Hintergrund + rotem `CRITICAL`-Badge.
  Rollen-Name ist sekundär (grau, 9pt-Skala), Personenname dominant (fett,
  12pt-Skala), Telefonnummer in Monospace 11pt, optional ein kursiver
  Sub-Hinweis "unavailable — substitute active".
- **Probleme:**
  1. **Visuelle Geräusche.** Jede Karte hat einen eigenen Rahmen plus
     einen 2.5pt-Akzent links, plus bei critical noch Hintergrundfarbe
     plus den Badge "CRITICAL". Drei Codierungen für ein Konzept. Wenn
     viele Rollen kritisch sind (häufig im Vorstand-Level), ertrinkt die
     Seite in Rot.
  2. **Hierarchie kippt.** Der Rollenname (das, wonach man im Krisenfall
     sucht) ist grau und klein. Der Personenname ist dominant. Für die
     Wandchart-Lesung "wer ist gerade Chief Information Security
     Officer?" ist das falsch herum — man scannt nach Rolle und liest
     dann die Person.
  3. **Spalten brechen Namen.** Bei sechs Spalten auf A4 quer sind die
     Spalten ~37mm breit. "Stellvertretender Vorsitz Krisenstab" wird zu
     "Stellvertretender / Vorsitz / Krisenstab" — drei Zeilen für einen
     Rollennamen, der dann mehr Platz braucht als der Personenname.
  4. **Substitution-Hinweis ist schwach.** Der kursive 7.5pt-Mini-Text
     "Sebastian Köhler unavailable — substitute active" ist auf
     Wandchart-Distanz unlesbar. Information über aktive Substitution
     verschwindet genau dort, wo man sie braucht.
  5. **Doppelter Critical-Marker.** Roter Balken + roter Badge + roter
     Hintergrund. Eine Codierung reicht — vermutlich der Balken.
  6. **Telefonnummer in Monospace.** Korrekt zur Lesbarkeit, aber 11pt
     Monospace neben 12pt Fett-Sans wirkt wie ein Bug, nicht wie eine
     bewusste Hierarchie. Konsistente Behandlung von Kontaktdaten fehlt.

### Role detail

- **Zweck:** A4-Telefonliste mit voller Substitution-Kette pro Rolle.
- **Status quo:** Pro Level eine `p-h2`-Überschrift mit Border-Bottom.
  Darunter pro Rolle ein Block mit hellgrauem Rahmen, optional rotem
  Links-Akzent + rosa Hintergrund bei critical. Pro Rolle eine
  Ketten-Liste, jedes Element: Rang-Label (50pt fix), Name + optionaler
  ABSENT-Tag, Telefon rechts. Aktiver Eintrag bekommt gelben Hintergrund.
- **Probleme:**
  1. **Drei-Spalten-Zeile in der Kette ist eng.** 50pt für "Substitute 3"
     fix reserviert, plus Name plus Telefon — bei langem Namen + langer
     Telefonnummer + Absent-Tag wird's krampfig. Auf A4 hoch geht das
     gerade so, aber die Verteilung wirkt nicht entworfen, sondern
     gewachsen.
  2. **Manual-Note steht über der Kette.** Wenn jemand manuell zugewiesen
     ist, erscheint ein gelber Kasten "🔒 MANUAL: Person — Telefon" ÜBER
     der Kette. Das ist die korrekte Stelle, aber die Beziehung zwischen
     "manueller Override" und "diese Kette ist deshalb gerade nicht
     aktiv" wird nicht visualisiert. Der Leser muss selber kombinieren.
  3. **Active-Highlighting subtil.** Der aktive Ketten-Eintrag bekommt
     `#fff3c0` Hintergrund + Fett. Bei voller Kette mit primary anwesend
     ist das in Ordnung. Bei Cascade (rank > 0 aktiv) verliert sich der
     Hinweis "warum dieser und nicht der davor" — die Abwesenheits-Tags
     der durchgestrichenen Vorgänger müsste man als Geschichte lesen.
     Das funktioniert für trainierte Augen, ist aber kein klares Signal.
  4. **Rollen-Beschreibung lebt zwischen Head und Manual-Note.** Wenn
     vorhanden, kommt sie als `p-small` direkt unter dem Rollennamen.
     Mehrzeilige Beschreibungen brechen das saubere Karten-Format.
  5. **Kein Page-Header-Repeat bei Level-Wechsel.** Wenn ein Level über
     mehrere Seiten geht, fehlt auf den Folgeseiten der Level-Kontext.
     `running()` für den Footer ist da, aber Level-Crumbs nicht.
  6. **`break-inside: avoid` auf Level-Section** kann bei großen Levels
     zu erzwungenen Seitenwechseln mit halbleeren Vorgänger-Seiten
     führen. Sollte auf Rollen-Ebene reichen.

### People list

- **Zweck:** Alphabetische Personen-Übersicht, schnelles Nachschlagen.
- **Status quo:** Zwei Sektionen ("Abwesend" + "Verfügbar"), jeweils
  pro Person eine Zeile mit Zwei-Spalten-Grid: links Name + Kontakt,
  rechts Rollen-Chips. Absente Personen mit rosa Hintergrund und
  hinten ergänztem " — ABSENT" via CSS-`::after`.
- **Probleme:**
  1. **Zwei-Spalten ist starr.** Bei Personen mit vielen Rollen quillt
     die rechte Spalte über; bei Personen mit langem Namen + Email
     bricht die linke unschön. Keine adaptive Verteilung.
  2. **"— ABSENT" via `::after`** ist ein Anti-Pattern für Druck.
     Inhalt im CSS, nicht steuerbar über Sprache (steht hardcoded
     "ABSENT" in der `.p-person-name[data-absent="true"]::after`-Regel,
     Zeile ~3899). Das ignoriert die i18n-Logik des Rests.
  3. **Rollen-Chips ohne Rang-Priorität.** Chips sind gleichwertig
     gerendert ("Role-Name · Primary" oder "Role-Name · Substitute 2"),
     keine visuelle Unterscheidung zwischen "ist Hauptverantwortlicher"
     und "ist Backup #5". Wenn Person 7 Rollen hat, ist nicht erkennbar,
     wo sie primary ist.
  4. **Sektion-Reihenfolge counter-intuitiv.** "Absent oben" ist im
     Krisen-Briefing sinnvoll ("wer fehlt heute?"), aber wenn die Liste
     als Telefonbuch eingesetzt wird, will man verfügbare Personen oben.
     Sollte konfigurierbar oder klar dokumentiert sein.
  5. **Keine Buchstaben-Trenner.** Bei >40 Personen ist alphabetisch
     ohne A/B/C/...-Anker mühsam zu durchblättern.
  6. **Absente Personen bleiben in der Rollen-Auflistung ihrer Chips.**
     Person ist `data-absent="true"`, aber Chips zeigen weiterhin
     "Primary in Role X" — kein Hinweis, dass Role X aktuell vermutlich
     in Substitution ist. Querverweis fehlt.

---

## Verbesserungs-Vorschläge

### Allgemein (alle Templates)

- **Eine konsistente Critical-Codierung.** Ein einziges Element pro
  Karte/Zeile (vermutlich linker 2.5pt-Balken). Badge und
  Hintergrundtinte weg, außer einem dezenten Aufdruck oben rechts.
- **Header schlanker.** Den Fingerprint reduzieren auf 6–8 Zeichen,
  Label kürzen oder als Fußzeile verlegen. Header-Region nimmt jetzt
  ~30mm der ersten Seite ein.
- **Footer auf jeder Seite** (Drucktitel, Seitennummer, Fingerprint).
  Aktuell ist `position: running(pageFooter)` deklariert (Zeile ~3694),
  aber kein Element nutzt es. Toter Code — entweder aktivieren oder
  entfernen.
- **Schrift-Hierarchie auf 3 Größen reduzieren.** Aktuell sieben
  Größen-Stufen (`6.5pt`, `7pt`, `7.5pt`, `8pt`, `8.5pt`, `9pt`, `10pt`,
  `11pt`, `12pt`, `14pt`, `18pt`). Das ist zu viel und entsteht aus
  organischem Wachstum. Reduktion auf z.B. {Body 9pt, Lead 11pt fett,
  Section 14pt fett, Page-Title 18pt fett}, plus eine Small-Variante 7pt
  für Metadaten.
- **Cascade-Information sichtbar machen, aber nicht überall.** Aktuell
  sind Cascades nur in `overview` per Mini-Sub-Hinweis angedeutet. Eine
  klare Konvention treffen: zeigen wir in jeder Variante an, dass eine
  Rolle gerade per Substitution besetzt ist, und wenn ja, wie?
  Vorschlag: dezenter Tag rechts neben dem Personennamen wie "Substitute
  rank 2" oder ein →-Symbol, niemals nur kursiver Mini-Text.
- **Print-Vorschau-Pflicht.** Aktuell springt das Modal direkt in den
  Browser-Druckdialog. Für die drei Templates wäre eine On-Screen-
  Vorschau-Seite (das gleiche HTML, screen-rendered) eine geringere
  Hürde als jedes Mal über den Browser-Print-Dialog zu iterieren. Würde
  auch Testen erleichtern.

### Overview-spezifisch

- **Hierarchie umdrehen.** Rollenname groß und fett oben, Personenname
  als zweite Zeile, Kontaktdaten klein und unauffällig darunter. Wer
  scannt sucht die Rolle, nicht die Person.
- **Spaltenzahl pro Format begrenzen.** Auf A4 max. 3 Spalten, A3 quer
  max. 5. Lieber zweite Seite als unleserliche 6-spaltige Wand.
- **Level-Blöcke nicht als Spalten.** Aktuell ist die Spalte = das Level.
  Alternative: Level als horizontale Bänder über die volle Seitenbreite
  (Levels gestapelt, Rollen innerhalb des Bands floaten). Macht
  unterschiedlich viele Rollen pro Level natürlicher.
- **Substitution-Status klar.** Statt "Sebastian Köhler unavailable —
  substitute active" als Mini-Text: ein Tag "↑ Substitute" am
  Personennamen, in dezentem Gelb. Auch auf 3m Abstand erkennbar.

### Role detail-spezifisch

- **Ketten-Layout als Tabelle, nicht als 3-Spalten-Flex.** Konsistente
  Spaltenbreiten über alle Rollen hinweg, sauberer Rhythmus auf der
  Seite. Tabular Numbers für Telefonnummern.
- **Aktiv-Indikator außerhalb der Zeile.** Statt gelber Hintergrund:
  ein deutlicher Marker links der Zeile ("▶ aktuell aktiv"). Macht auch
  bei S/W-Druck (Krisenraum hat oft nur Laser) erkennbar, welcher Eintrag
  gerade besetzt.
- **Manual-Note als Inline-Eintrag in die Kette.** Mit Marker, der
  visualisiert "die Kette ist gerade übergangen worden". Erspart das
  geistige Verknüpfen.
- **Page-Header pro Level.** Auf Folgeseiten eines Levels eine kleine
  Crumb-Zeile "Level X — Name (continued)".
- **Rollen-Beschreibung optional ausblendbar** über eine Checkbox im
  Modal. Für reine Telefonliste oft nicht gewünscht, für
  Schulungsdrucke schon.

### People list-spezifisch

- **Buchstaben-Trenner.** Erste Person mit "A" → Section-Anker "A"
  links neben der Zeile. Nicht aufwendig, deutlich bessere Scanbarkeit.
- **Rang-Priorität sichtbar.** Primary-Rollen mit anderem Chip-Style
  (gefüllt) als Substitute-Rollen (Outline). Oder: Rollen nach Rang
  sortiert, primary zuerst.
- **Sortier-Option im Modal.** "Alle (absent oben) / Alle (alphabetisch)
  / Nur verfügbar". Drei Klicks, deckt alle Use-Cases.
- **"ABSENT" aus CSS in JS.** Übersetzbarer String, nicht hardcoded im
  `::after`-Selektor. Konsistent mit dem Rest der i18n-Architektur.
- **Cross-Reference bei absenten Personen.** "Vertretung aktiv in:
  Role X (gerade Substitute Y)" als eigene Sub-Zeile. Macht aus der
  Personen-Liste eine Awareness-Übersicht.

---

## Abhängigkeiten

### V2.1 Team-Pools

V2.1 wird Team-Pools einführen (Rollen, die nicht 1 Person, sondern
einen Pool von n Personen haben — z.B. SOC-Schicht). Das beeinflusst
alle drei Templates:

- **Overview:** Pool-Rolle muss anzeigen, wer aktuell aktiv ist UND
  wer im Pool wartet. Eine "Person pro Karte" reicht nicht.
- **Role detail:** Substitution-Kette wird zu Pool-Liste. Reihenfolge
  wird zur Rotation, "primary" wird zu "aktuell dran".
- **People list:** Pool-Mitgliedschaft als eigene Chip-Variante neben
  Role-Chips, oder als eigene Sub-Sektion.

**Empfehlung:** Print-Refresh NACH V2.1-Pool-Design starten. Sonst
wird der Refresh zweimal gebaut — einmal jetzt, einmal nach Pool-
Einführung. Wenn Pool-Design schon klar ist (Datenmodell mit
`assignments[]` plus optionalem `poolMembers[]` z.B.), kann der
Refresh parallel laufen.

### V2.0 Auto-Sync

Keine direkte Abhängigkeit. Sync-Fingerprint ist im Header schon drin
und bleibt unverändert. Auto-Sync ändert nichts am Druck-Output.

---

## Aufwandsschätzung

**Moderat.** Konkret:

- CSS-Refactor `@media print`-Block (~290 Zeilen): 1 Tag
- Drei `buildPrint*`-Funktionen umbauen (~200 Zeilen): 1–2 Tage
- Print-Modal um Sortier-/Filter-Optionen erweitern: 0.5 Tage
- On-Screen-Vorschau (separate Route oder Modal-Tab): 1 Tag
- Übersetzungen aller neuen Strings (5 Sprachen): 0.5 Tage
- QA auf A4 hoch/quer + A3 quer + Letter, je drei Templates,
  je mit demo-DE/demo-EN-Config: 1 Tag

**Summe: ~5–6 Tage** Solo-Entwicklung, ohne Pool-Awareness. Mit Pools
+1–2 Tage zusätzlich.

---

## Akzeptanzkriterien

Konkret prüfbar nach dem Refresh:

- **Wand-Chart A3 quer:** Rollennamen auf 3m Abstand lesbar (mind. 14pt
  Body bei A3-Scale 1.41 → ~20pt Effektiv). Personennamen auf 5m
  identifizierbar.
- **Telefonliste A4 hoch:** Eine Rolle = ein klar abgegrenzter Block.
  Kein Block über Seitenumbruch gerissen. Bei 30 Rollen / 6 Level: 4–6
  Seiten, durchgängig konsistentes Layout.
- **Personen-Liste A4 hoch:** Bei 50 Personen scrollt der Druck auf
  max. 3 Seiten. Alphabet-Anker erkennbar. Absente Personen visuell
  klar getrennt, ohne dass die Liste in "ungenutzten Platz" zerfällt.
- **Critical-Codierung:** Genau eine visuelle Codierung pro Element.
  Keine doppelte Kombination von Rot-Badge + Rot-Rahmen +
  Rot-Hintergrund.
- **Substitution sichtbar in allen Varianten:** In Overview als
  scanbarer Tag, in Detail als Inline-Marker in der Kette, in Persons
  als Cross-Reference bei der absenten Person.
- **S/W-Druck-Test:** Komplette Konvention bei reinem Laser-Schwarzweiß
  noch lesbar (keine Information geht verloren, wenn die Tinte fehlt).
- **Print-CSS hat einen Stil, nicht drei.** Token-Konsolidierung: drei
  Schriftgrößen, drei Border-Stärken, zwei Akzentfarben (Schwarz, Rot).
  Vorbei mit `0.25pt`, `0.5pt`, `1pt`, `2.5pt` durcheinander.
