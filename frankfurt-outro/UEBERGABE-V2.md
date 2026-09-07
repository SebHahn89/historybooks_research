# Übergabe an Claude Code: Frankfurt-Outro für „Damals in Farbe" — **V2**

Stand: 7. September 2026. Diese Fassung ersetzt die Übergabe vom selben Tag.
Sie ersetzt außerdem alle früheren Entwürfe mit ausgeschriebenem „DAMALS IN
FARBE", zweizeiligem „FRANK / FURT", Bembel oder Brezel. Zunächst
ausschließlich Frankfurt umsetzen.

## Was sich gegenüber V1 geändert hat

Drei Vorgaben von Sebastian, alle drei sind verbindlich:

1. **Es müssen keine 3D-Objekte sein.** Der Abbinder darf stattdessen im
   **Paper-Cutout-Stil** entstehen. Damit entfällt die Beschaffung
   lizenzgeprüfter 3D-Modelle als Voraussetzung. Die 3D-Fassung bleibt als
   Vergleichsvariante bestehen, ist aber nicht mehr gesetzt.
2. **Vor der Produktion steht eine gestalterische Prüfung.** V2
   (Paper-Cutout) wird gegen die reguläre Variante (3D-Objekte) geprüft.
   Prüfformat: **18 Frames in drei Abschnitten, je Abschnitt 3×2 Frames als
   ein Paket.** Dieses Format hat sich bereits bewährt.
3. **Orange ersetzt Gold.** Der Gold-Ton aus dem Corporate Design wird im
   Abbinder durch das CI-Orange ersetzt. Die Buchstabenwechsel laufen
   entsprechend zwischen CI-Blau und Orange, nicht mehr zwischen Blau und
   Gold.

Alles Übrige aus V1 bleibt gültig und ist unten vollständig enthalten.

---

## 1. Auftrag

Entwickle einen hochwertigen, wenige Sekunden langen, wiederverwendbaren
Reel-Abbinder für Sebastian und seine Marke „Damals in Farbe". Übertrage die
Motion-Design-Sprache des beigefügten Referenzvideos auf Frankfurt und das
vorhandene Corporate Design. Nicht bloß einen generischen Text-Zoom oder eine
animierte Präsentationsfolie bauen.

Die Reihenfolge ist jetzt: **erst gestalterisch entscheiden, dann
produzieren.** Zuerst beide Varianten als Frameboards zeigen, Entscheidung
einholen, danach animieren. Nicht mit der Produktion beginnen, solange die
Stilfrage offen ist.

Für die Umsetzung soll weiterhin raylight.app über dessen MCP-Anbindung
geprüft werden. Prüfe die tatsächlichen Fähigkeiten der verbundenen Werkzeuge,
bevor du eine technische Umsetzung versprichst. Eine HTML/WebGL-Fassung
existiert als erster technischer Entwurf, ist aber nicht die verbindliche
Qualitätsreferenz.

## 2. Zielverständnis — Interpretation, nicht zusätzliche Nutzervorgabe

Ich verstehe das Ziel als einen kurzen, eigenständigen Markenmoment am Ende
historischer Stadt-Reels: Frankfurt wird durch Schrift und vertraute
Stadtobjekte unmittelbar erkennbar; das originale Logo sorgt für die Zuordnung
zur Marke. Der Abbinder soll trotz häufiger Wiederholung interessant bleiben,
hochwertig und materiell wirken und sich ohne neue Bearbeitung an weitere
Frankfurt-Reels anhängen lassen.

Die Referenz gefällt vermutlich wegen ihrer Kombination aus typografischer
Wucht, überraschenden Größenwechseln, räumlich bewegten Alltagsobjekten, leicht
federnder Schrift und einer asymmetrischen, dennoch präzisen Komposition.
Dieses Zusammenwirken ist wichtiger als eine möglichst lange Liste von
Effekten. Das ist meine Interpretation. Sebastian hat keine finalen
Easing-Kurven, exakte Laufzeit, Musik oder bestimmte Rotationswinkel
freigegeben.

## 3. Verbindliche Vorgaben des Nutzers

- Hochkant-Reel: 9:16. Arbeits- und Exportziel: 1080 × 1920 Pixel.
- „Damals in Farbe" NICHT als neu gesetzten Text ausschreiben. Das gelieferte
  Logo verwenden.
- Unterhalb des Logos den Stadtnamen in drei Zeilen anordnen: erste Zeile
  **FRA**, zweite Zeile nach rechts eingerückt **NK**, dritte Zeile wieder
  linksbündig **FURT**.
- Einstieg eng auf „FRA" gezoomt. Anschließend herauszoomen und die
  dreizeilige Gesamtkomposition zeigen.
- Die Spitze des Frankfurter Messeturms ersetzt das **A**.
- Links neben dem **N** steht eine **Nilgans**. Sie ersetzt ausdrücklich keinen
  Buchstaben.
- Ein **Geripptes**, gefüllt mit Apfelwein, ersetzt das **U**.
- Die drei Objekte müssen sich sichtbar im Raum bewegen. **Ob das über echte
  3D-Modelle oder über gestaffelte Papierebenen geschieht, entscheidet die
  gestalterische Prüfung in Abschnitt 5.** Was in beiden Fällen gilt: ein
  flaches Bild in der Bildebene zu drehen ist keine räumliche Bewegung.
- Beim Auftauchen wechseln die Buchstaben EINZELN zwischen **Blau und Orange**
  aus dem Corporate Design.
- Die Bewegungssprache des Referenzvideos aufnehmen: markante Zooms, räumliche
  Objektbewegung, subtile Sprünge und versetzter Aufbau der Typografie.
- Zunächst Frankfurt, nicht gleichzeitig München ausarbeiten.

### Exakte Zuordnung

| Zeile | Schrift | Objekt | Rolle |
|---|---|---|---|
| 1 | FRA | Messeturmspitze | ersetzt A |
| 2 | NK, nach rechts versetzt | Nilgans | steht links neben N |
| 3 | FURT, wieder links | Geripptes mit Apfelwein | ersetzt U |

Die Animation darf A und U zunächst zeigen und dann ersetzen. Ob sie am Ende
als Objekte stehen bleiben oder zurückgetauscht werden, ist noch nicht
ausdrücklich entschieden. Mein Vorschlag ist, sie im Schlussbild als Objekte
stehen zu lassen, weil das die Typografie-Objekt-Idee der Referenz erhält.
Nicht wieder auf die frühere Idee „Bembel statt B" zurückfallen.

---

## 4. Materialien und Designgrundlage

### Design-System

Sebastian hat das Design-System als gebündelte HTML-Datei geliefert
(`Damals_in_Farbe_Carousel.html`). Sie ist auspackbar: Farbtokens, Typo-Tokens,
Slide-Geometrie, fünf München-Fotos und die Montserrat-Schriftdateien liegen
darin. Übernommen ins Projekt:

```
frankfurt-outro/assets/fonts/montserrat-latin.woff2       Montserrat variabel, 100-900
frankfurt-outro/assets/fonts/montserrat-latin-ext.woff2   dito, erweitertes Latein
frankfurt-outro/assets/images/muenchen-*.png              5 München-Fotos, je 1080 px breit
```

Das früher genannte Claude-Design-Projekt
(<https://claude.ai/design/p/90e16a7e-6569-4789-a96b-e6a70b26a5fe>) ist aus
einer Claude-Code-Sitzung heraus weiterhin nicht lesbar (HTTP 403). Es wird
nicht mehr gebraucht — die HTML-Datei enthält dieselben Tokens.

### ⚠️ Offener Punkt: Es gibt kein Orange im Corporate Design

Das gelieferte Design-System definiert genau **sechs Markenfarben** (Figma
Variable Collection „Damals in Farbe · Farben"):

| Token | Hexwert | Verwendung laut System |
|---|---|---|
| navy | `#16325C` | Headline auf hellem Foto |
| night | `#0D2547` | dunkelblaue Fläche |
| paper | `#F1F1EF` | heller Papier-Hintergrund |
| ink | `#1E1E1E` | Schrift auf Papier |
| **gold** | **`#E9C993`** | **Akzent Outro** |
| white | `#FFFFFF` | Weiß |

Ein Orange ist darin **nicht enthalten** — auch nicht in den
Dokumentationsfarben (dort nur `--gold-deep #A8853D` und `--green #296B47`).
Die Anweisung „statt dem Gold in der CI das Orange" führt also keine
vorhandene CI-Farbe ein, sondern **ersetzt die einzige Akzentfarbe des Systems
durch eine neue**. Das ist eine Markenentscheidung, keine Umsetzungsdetail —
und sie sollte bewusst getroffen werden, weil `gold` im System ausdrücklich als
„Akzent Outro" geführt wird, also genau für diesen Anwendungsfall.

Der in den Frameboards verwendete Wert `#F0A32A` stammt **nicht** aus dem
Design-System. Er ist aus den Badges und dem Button des gelieferten
München-Frameboards abgeleitet und damit eine Schätzung. Vor der Produktion
ist zu klären:

1. Wo kommt das Orange her — gibt es eine Quelle, die ich noch nicht kenne?
2. Wird `gold` im Design-System ersetzt, oder bekommt der Abbinder eine
   Sonderfarbe, die im übrigen Kit weiter Gold bleibt?
3. Der exakte Hexwert.

Bis dahin steht `#F0A32A` in allen Dateien als CSS-Variable `--orange` und ist
an einer Stelle austauschbar. **Nicht als CI-Farbe ausgeben, solange das nicht
bestätigt ist.**

### Typografie

Montserrat liegt jetzt als echte Schriftdatei vor, nicht mehr als Ersatz. Die
Tokens des Systems, soweit für den Abbinder relevant:

| Token | Wert |
|---|---|
| Schnitte | 300 Light, 500 Medium, 600 SemiBold, 700 Bold, 800 ExtraBold |
| Outro/Headline | 66 px, ExtraBold, Zeilenhöhe 1,19, Tracking 0,01 em |
| Cover/Headline | 72 px, ExtraBold, Zeilenhöhe 1,13, Tracking 0,005 em |
| Stack/Heavy | 82 px, ExtraBold, Zeilenhöhe 1,114, Tracking 0,02 em |
| Satzspiegel | Slide 1080 × 1350, Rand 84 px, Spalte 912 px |

Die Frameboards setzen FRA / NK / FURT in Montserrat ExtraBold bei 280 px auf
1080 px Breite, linker Rand 84 px wie im System. Die Buchstabenpositionen
werden zur Laufzeit **gemessen**, nicht fest eingetragen — sonst bricht das
Layout bei jedem Schriftwechsel.

Zu beachten: Das Kit ist auf **1080 × 1350** ausgelegt (Carousel), der Abbinder
auf **1080 × 1920** (Reel). Die Schriftgrößen des Kits sind daher nicht direkt
übertragbar, die Proportionen und der Rand schon.

### Bildmaterial

Die fünf Fotos aus dem Bundle sind **München**: `bau1893`, `blaueStunde`,
`gruenHeute`, `isarHeute`, `muenchen1925`. Sie liegen im Projekt und sind
einsetzbar — aber nicht für Frankfurt. Für einen Frankfurt-Abbinder werden
Frankfurt-Motive gebraucht. Zwei Wege:

- Frankfurt-Fotos aus dem Bestand nachliefern, oder
- den Abbinder ohne Fotos bauen. Der Paper-Cutout-Stil trägt auch ohne
  Fotomaterial; die Copenhagen-Referenz nutzt Fotos als Collagenebene, das ist
  für Frankfurt bisher nicht verlangt.

Der Figma-Link auf `History-Books--Copy`, Node `656:15283`, ist über die
Figma-Anbindung lesbar. Der Knoten ist allerdings ein **Buchsatz-Board**
(Doppelseiten, Bildunterschriften, Kapitelmarken, 41 000 × 50 500 px), kein
Storyboard und keine Farbquelle. Falls dort ein bestimmter Frame gemeint war,
brauche ich den Node dieses Frames.

### Logo

Originaldatei: `Group 77.svg`, im Übergabepaket zusätzlich unter
`assets/logo.svg`. SVG-Abmessungen: 1924 × 1983. Eine geschwungene, schräg
ansteigende Wortmarke mit Unterstreichung, als Vektorpfade angelegt. Sichtbare
Füllfarbe: `#FFE395`.

Das Original nicht neu zeichnen, nicht als Montserrat-Text nachsetzen und nicht
eigenmächtig verzerren. In den Frameboards steht an seiner Stelle ein
erkennbarer **Platzhalter** — der ist als solcher beschriftet und ersetzt das
Logo nicht.

### Figma-Kit

[Damals in Farbe – Social Media Kit](https://www.figma.com/design/0L2ofgcrTLaMcAnbGacyv4/Damals-in-Farbe-%E2%80%93-Social-Media-Kit?node-id=1-3)

Das Kit bleibt als Referenz relevant; die konkreten Werte stehen inzwischen
oben unter „Typografie" und stammen direkt aus dem gelieferten Design-System.

Papierstruktur und Materialität passen zur bisherigen Marke — im
Paper-Cutout-Stil werden sie zum tragenden Prinzip statt zur Dekoration. Auf
Nachtblau bleibt CI-Blau kontrastarm: blaue Typografie vorzugsweise auf
Papiergrund zeigen.

---

## 5. Gestalterische Prüfung vor der Produktion

### Prüfformat

Beide Varianten werden im selben Format gezeigt, damit sie vergleichbar sind:

- **18 Frames** über die gesamte Laufzeit
- **drei Abschnitte** zu je sechs Frames
- je Abschnitt **ein Board mit 3×2 Frames** im Hochformat 9:16
- je Frame: Nummer, Zeitfenster, Zoomstufe und eine Beschreibung getrennt nach
  **Kamera**, **Bewegung** und **Farbe**
- je Board eine Zeitleiste mit den sechs Übergängen

Dieses Format hat bei München funktioniert und wird beibehalten. Es ist bewusst
kein Animatic: Es zeigt Komposition, Ausschnitt und Rhythmus, nicht das
Timing-Gefühl. Über Easing entscheidet erst die bewegte Vorschau.

### Stand der Boards

Der Satz für **V2 / Paper-Cutout** liegt vor:

```
frankfurt-outro/storyboard/
  storyboard.html      Generator (alle Frames als Daten, ein Aufruf pro Board)
  frameboard-1.png     01 / Typografischer Auftakt      0,00-1,80 s
  frameboard-2.png     02 / Objekte übernehmen          1,80-4,00 s
  frameboard-3.png     03 / Beruhigung und Schluss      4,00-6,50 s
```

`storyboard.html` im Browser öffnen zeigt alle drei Boards untereinander;
`?board=2` zeigt eines einzeln. Die Frames sind keine Renderframes, sondern
Mockups aus derselben SVG-Szene mit 18 verschiedenen Kameraausschnitten. Die
Kamerawerte sind damit direkt in die Produktion übernehmbar.

**Offen:** Der Satz für die **reguläre Variante (3D)** fehlt noch. Für einen
echten Vergleich muss er in genau demselben Raster und mit denselben 18
Zeitfenstern entstehen — gleiche Choreografie, anderer Materialeindruck.

### Entscheidungsfrage an Sebastian

Die 18 Beats, Kameraausschnitte und Farbwechsel sind in beiden Varianten
identisch. Zu entscheiden ist allein der Materialeindruck:

| | V2 / Paper-Cutout | Regulär / 3D |
|---|---|---|
| Objekte | geschnittene Papierebenen | Modelle mit Material und Licht |
| Räumlichkeit | Lagenversatz, wandernder Schlagschatten, wechselnde Silhouette | echte Rotation mit Rückseite |
| Nähe zur Marke | hoch — Papier ist bereits Markenmaterial | mittel — neuer Materialauftritt |
| Asset-Bedarf | keine externen Assets, alles vektorbasiert | drei lizenzgeprüfte Modelle nötig |
| Risiko | Objekte wirken zu flach, wenn der Lagenversatz zu klein ist | Modelle wirken wie Stock-Ware, Stilbruch zur Papiermarke |
| Raylight-Eignung | gut — entspricht dem, was das Werkzeug nachweislich kann | offen — Mesh-Import erst zu prüfen |
| Aufwand | gering, in einem Durchgang produzierbar | hoch, Beschaffung plus Rendering |

Meine Empfehlung ist V2. Sie trifft die Papier-Materialität der Marke, kommt
ohne Asset-Beschaffung aus und passt zu den belegten Fähigkeiten von Raylight.
Der 3D-Weg bleibt möglich, kostet aber Beschaffung, Lizenzprüfung und einen
zweiten Rendering-Pfad. Die Entscheidung liegt bei Sebastian.

---

## 6. Variante V2 — Paper-Cutout

### Prinzip

Jedes Element ist eine ausgeschnittene Papierform auf Papiergrund: die
Buchstaben, die drei Objekte, die Akzentflächen. Tiefe entsteht durch
Übereinanderliegen und einen weichen, versetzten Schlagschatten — nicht durch
perspektivische Verkürzung.

### Wie „räumliche Bewegung" ohne 3D funktioniert

Das ist die zentrale Frage bei diesem Stil, und sie ist ausdrücklich **keine
Erlaubnis, ein flaches Bild zu kippen und das 3D zu nennen.** Räumlichkeit
entsteht hier aus vier Mitteln:

1. **Lagenversatz.** Jedes Objekt besteht aus drei bis fünf getrennten
   Papierebenen. Bewegen sich diese Ebenen unterschiedlich schnell, entsteht
   Parallaxe. Beispiel Messeturmspitze: Vorderfläche, Schattenflanke und
   Antenne sind eigene Ebenen und verschieben sich gegeneinander.
2. **Wechselnde Silhouette.** Die Umrissform verändert sich während der
   Bewegung. Die Nilgans zeigt nacheinander Profil, Dreiviertelansicht und
   verkürzten Hals — als Formwechsel, nicht als Skalierung.
3. **Wandernder Schlagschatten.** Der Schatten bewegt sich relativ zum Objekt.
   Das allein erzeugt bereits den Eindruck, dass sich etwas über der Fläche
   hebt.
4. **Innenzeichnung.** Reliefs bewegen sich mit: das Rautenmuster des
   Gerippten, die Fensterbänder der Turmspitze, die Flügeldeckfeder der Gans.

Wenn nur ein einziges Bild gedreht wird und weder Silhouette noch Schatten noch
Innenzeichnung reagieren, ist die Regel verletzt. In dem Fall die Grenze offen
benennen statt sie zu kaschieren.

### Objekte im Cutout-Stil

- **Messeturmspitze** — pyramidenförmige Spitze mit hellerer und dunklerer
  Flanke, kurzer Turmschaft mit ausgesparten Fensterbändern, orangefarbener
  Punkt an der Antenne. Keine beliebige Hochhausspitze: das Verhältnis von
  Pyramide zu Schaft muss stimmen.
- **Nilgans** — Körper in warmem Braunton, dunklere Flügeldecke als eigene
  Ebene, langer aufrechter Hals, kleiner Kopf, **Augenfleck** als klar
  erkennbare dunkle Scheibe, Schnabel und Beine in Orange. Keine weiße
  Hausgans, keine Ente. Der lange Hals ist das wichtigste Erkennungsmerkmal.
- **Geripptes** — nach unten verjüngtes Glas, Rand und Boden als eigene
  Papierstreifen, Rautenrelief als Innenzeichnung, Apfelwein als orange Fläche
  mit waagerechter Oberkante. Die Oberkante bleibt beim Kippen des Glases
  waagerecht — daran wird die Drehung lesbar. Keine Bierkrone.

### Was diese Variante ausschließt

Keine Verläufe, keine Weichzeichnung außerhalb des Schlagschattens, keine
Glasbrechung, kein Bloom. Die Wirkung kommt aus Form, Farbfläche und
Bewegung. Wenn eine Stelle nur mit einem Effekt funktioniert, stimmt die Form
noch nicht.

---

## 7. Referenzvideo: Quelle und Methode

[Instagram-Original von kinisi.tv](https://www.instagram.com/reels/DbIaKQTuOji/)

Upload: `All in a days work. 🌞Like a lot of freelancers, after months of
back-to-back projects, Id bee.mp4`.

Technisch ausgelesen: 1280 × 720 Pixel, 16:9 quer, 30 Bilder pro Sekunde,
H.264-Bildspur und AAC-Tonspur, Gesamtdauer rund 21,12 Sekunden. Der erste
gestalterische Durchlauf dauert ungefähr 10,5 Sekunden; danach wiederholt sich
die Bildfolge weitgehend. Die Referenz daher neu für Hochkant komponieren,
nicht einfach mittig beschneiden.

Das beigefügte **CopenhagenFramebookRhythmus_2.pdf** enthält 48 ausgewählte
Einzelbilder in fünf Abschnitten aus dem ersten Durchlauf, verteilt auf 14
Seiten zu je vier Frames. Es zeigt ausschließlich das Copenhagen-Original,
keinen Frankfurt-Entwurf. Die Zeitstempel und nullbasierten Frame-Nummern
beziehen sich auf den Upload. Easing-Kurven, Rotationsachsen und die
ursprüngliche Produktionssoftware wurden nicht rekonstruiert. Audio-Impulse
wurden als Transienten aus dem Signal ermittelt, aber nicht mit einer
gesicherten musikalischen Takt- oder BPM-Bestimmung gleichgesetzt.

Sebastians Präzisierung: **Der Takt des Copenhagen-Videos ist besonders; die
Bildfolgen folgen diesem Rhythmus.** Daher nicht nur schöne Einzelbilder
übernehmen, sondern den zeitlichen Zusammenhang von Ton, Bildwechsel,
Farbwechsel und Objektbewegung untersuchen. Große visuelle Umschaltungen bei
4,50 / 5,50 / 6,50 Sekunden liegen jeweils eine Sekunde auseinander. Weitere
Objekt- und Zeilenakzente folgen in ungefähr halben Sekunden. Die kleineren
Bewegungen zwischen diesen Ereignissen sind ebenso wichtig. Für die
musikalische Interpretation unbedingt das Original mit Ton ansehen.

## 8. Detaillierte Erklärung der Referenz

### Abschnitt 1: Typografischer Anker und Aufklappen der Collage, ca. 0,0–1,5 s

Im ersten Frame steht zunächst ein rotes H auf sehr hellem Grund. Daraus
entwickelt sich rasch eine kompakte Komposition: oben die kräftige Grotesk
„CPH", darunter ein kleines hochkant geschnittenes Schwarzweißfoto einer
Häuserfront und im weiteren Aufbau „MAN". Die Buchstaben wechseln während des
Aufbaus zwischen Rot und Schwarz. Sehr kleine Metadaten, feine Linien und
Markierungen erzeugen eine redaktionelle, beinahe kartografische Ebene.

Um etwa 1,25 bis 1,5 Sekunden öffnet sich die Fotokomposition seitlich. Aus dem
einzelnen Bild wird ein breiterer Streifen verschiedener architektonischer
Ausschnitte.

Übertragen auf Frankfurt: erst FRA als klaren Ausschnitt zeigen; die komplette
Wortkomposition soll als überraschende räumliche Erweiterung erscheinen.

### Abschnitt 2: Von der Bildcollage zum Raster, ca. 1,65–3,0 s

Die schmalen und breiten Fotoausschnitte verteilen sich über die Fläche.
Rechteckige Felder unterschiedlicher Größe, Weißraum, Schwarzweißbilder und
rote Akzente wechseln sich ab. Um etwa 3 Sekunden steht ein freigestellter
Holzstuhl im zentralen roten Feld. Der Übergang fühlt sich nicht wie eine
weiche Überblendung an, sondern wie ein gezielter Wechsel des Ausschnitts
innerhalb eines größeren Layouts.

Für Frankfurt kann diese Logik ohne die komplette Fotocollage übernommen
werden. Zusätzliche Frankfurt-Fotos sind bisher nicht verlangt und sollten
nicht ungefragt die Hauptrolle übernehmen — im Paper-Cutout-Stil übernehmen die
geschnittenen Farbflächen diese ordnende Rolle.

### Abschnitt 3: Räumliche Objektinszenierung, ca. 3,15–5,1 s

Der Holzstuhl verändert sichtbar seine Ansicht. Beine, Sitzfläche und
Rückenlehne verschieben sich perspektivisch gegeneinander. Anschließend rückt
ein goldbraunes, freigestelltes Gebäck in den Vordergrund; weiße und schwarze
„m"-Zeichen liegen teilweise darüber, sodass die Schrift um das Objekt herum zu
spielen scheint.

Wirkung: Reale Materialität trifft auf strenge Typografie. Die Gegenstände sind
keine angehängten Sticker, sondern tragen einen eigenen Bewegungsakzent. Genau
das ist der Abschnitt, an dem sich V2 beweisen muss.

### Abschnitt 4: Riesige Buchstaben und schneller Zoom-out, ca. 5,25–6,75 s

Die Bildsprache wechselt zu sehr großen typografischen Formen. Bei etwa 5,5
Sekunden dominieren ein rotes C und ein schwarzes O die Fläche. Bis etwa 6,5
Sekunden zieht sich die Typografie deutlich zurück, der Wortanfang „COP" wird
als kleinerer Textblock lesbar.

Das ist der wichtigste Referenzabschnitt für Frankfurt: nicht ein endlos
langsamer Ken-Burns-Effekt, sondern ein ausgeprägter Wechsel von enger
typografischer Nähe zu einer lesbaren Gesamtanordnung. Bewegung zügig beginnen
und präzise abbremsen.

### Abschnitt 5: Versetzter Stadtname mit integrierten Objekten, ca. 7,0–10,1 s

Ein Fahrrad schiebt sich in den Textblock, das Gebäck erscheint im oberen
Schriftbereich, der Stuhl wird im unteren Wortbereich integriert. Die einzelnen
Elemente kommen nicht gleichzeitig an. Auch in der fast fertigen Komposition
bleibt Bewegung vorhanden.

Genau dieses Prinzip soll Frankfurt tragen: FRA / NK / FURT mit
Messeturmspitze, Nilgans und Geripptem. Nicht die konkrete
Kopenhagen-Gestaltung kopieren; ihr Verhältnis von Buchstaben, Objekten,
Ausschnitten und Bewegungsrhythmus übertragen.

## 9. Motion-Regeln für die Übertragung

- Große Maßstabswechsel gezielt einsetzen. Nicht Kamera, jedes Objekt und jede
  Zeile dauerhaft gleich stark bewegen.
- Den Blick führen: FRA → erste räumliche Irritation → Gesamtwort → Objekte →
  Logo und lesbares Ende.
- Buchstaben einzeln animieren; kein bloßer Farbwechsel des gesamten
  Textcontainers.
- Kurze blau-orange Farbstufen dürfen knackig sein. Kein dauerhaftes hektisches
  Blinken. Höchstens zwei Zeichen gleichzeitig orange.
- Subtile Sprünge bedeuten kleine Positions- oder Skalierungsüberschwinger mit
  kurzer Beruhigung. Keine dauernd hüpfenden Gummibuchstaben.
- Die drei Objekte bekommen eigene Startzeitpunkte und leicht unterschiedliche
  Bewegungen. Nicht synchron wie Produkte auf drei identischen Drehtellern.
- Räumlichkeit muss an wechselnden Silhouetten, Lagenversatz und wandernden
  Schatten erkennbar sein — siehe Abschnitt 6.
- Schatten, Glanz und Schärfe konsistent halten. Starke Unschärfe, Bloom und
  Lens-Flare sind kein Ersatz für gute Bewegung.
- Im Schlussbild genügend Ruhe lassen, um Frankfurt und das Logo zu erkennen.

## 10. Ablauf: die 18 Frames

Arbeitsstand etwa 6,5 Sekunden bei 30 Bildern/s. Die Sekundenwerte stammen aus
dem Entwurf und sind noch nicht freigegeben. Die vollständigen Beschreibungen
zu Kamera, Bewegung und Farbe stehen auf den Frameboards; hier die Übersicht.

### Abschnitt 01 — Typografischer Auftakt, 0,00–1,80 s

| # | Zeit | Zoom | Frame |
|---|---|---|---|
| 1 | 0,00–0,20 | 360 % | Anschnitt F, nur ein Zeichen im Bild |
| 2 | 0,20–0,45 | 300 % | R und A setzen versetzt ein, erster Orange-Akzent |
| 3 | 0,45–0,70 | 250 % | Größte Nahaufnahme, kurzer Halt |
| 4 | 0,70–1,10 | 250→150 % | Schneller Zoom-out, NK tritt eingerückt ein |
| 5 | 1,10–1,45 | 130 % | FURT läuft ein und federt nach |
| 6 | 1,45–1,80 | 100 % | Wortkomposition steht, bewusste Farbpause |

### Abschnitt 02 — Objekte übernehmen, 1,80–4,00 s

| # | Zeit | Zoom | Frame |
|---|---|---|---|
| 7 | 1,80–2,05 | 108 % | Messeturmspitze legt sich vor das A |
| 8 | 2,05–2,35 | 108 % | A ist ersetzt, Spitze kippt, Flanken tauschen |
| 9 | 2,35–2,60 | 104 % | Nilgans läuft von links ein, neben das N |
| 10 | 2,60–2,95 | 104 % | Gans dreht sich, Turmspitze läuft gegenläufig |
| 11 | 2,95–3,30 | 100 % | Geripptes übernimmt das U, Apfelwein steigt |
| 12 | 3,30–4,00 | 98 % | Alle Objekte gesetzt, Gegen-Impuls |

### Abschnitt 03 — Beruhigung und Schluss, 4,00–6,50 s

| # | Zeit | Zoom | Frame |
|---|---|---|---|
| 13 | 4,00–4,30 | 98 % | Restbewegung unter 3° |
| 14 | 4,30–4,70 | 94 % | Langsamer Pull-back, Cutout-Kanten treten hervor |
| 15 | 4,70–5,10 | 94 % | Logo blendet oben ein |
| 16 | 5,10–5,50 | 94 % | Letzte Farbstufe auf einzelnen Zeichen |
| 17 | 5,50–6,10 | 94 % | Schlussbild, längste Standzeit |
| 18 | 6,10–6,50 | 94 % | Halt, Puffer für Reel-Bedienflächen und Loop |

Diese Tabelle nicht mechanisch abhaken. Die visuelle Referenz und das Gefühl
der Bewegung haben Vorrang vor den Zahlen.

## 11. Raylight über MCP: zuerst prüfen, dann umsetzen

Raylight beschreibt eine MCP-Verbindung für Claude Code mit Zugriff auf
Projekte, Shots, Animationen und gerenderte Frames. Der Server ist
`https://api.raylight.app/mcp`; das betreffende Projekt soll während der Arbeit
im Raylight-Editor geöffnet sein. Quelle:
[offizielle MCP-Anleitung](https://www.raylight.app/mcp), geprüft am
7. September 2026.

```sh
claude mcp add --transport http raylight https://api.raylight.app/mcp
```

Authentifizierung ausschließlich über die vorgesehene Anmeldung. Keine Tokens
in Projektdateien oder in diese Übergabe schreiben.

Danach:

1. Verfügbare MCP-Werkzeuge und deren Eingabeschemata auslesen. Keine
   ausgedachten Tool-Namen verwenden.
2. Projekte und aktuelle Editor-Verbindung prüfen. Nur das richtige Projekt
   bearbeiten; bei Mehrdeutigkeit Sebastian fragen.
3. SVG-Import, Einzellayer, Farben, Shot- und Timeline-Steuerung, Kamera und
   Export anhand tatsächlicher Fähigkeiten prüfen.
4. **Für V2 ist das die entscheidende Prüfung**, denn der Paper-Cutout-Stil
   braucht genau das, was Raylight beschreibt: SVG mit erhaltenen Einzelebenen,
   Ebenen-Transformationen und Schatten. Ob Mesh-Import unterstützt wird, ist
   für V2 nicht mehr kritisch — nur für die reguläre 3D-Variante.
5. Wenn V2 in Raylight umsetzbar ist: Szene aus `storyboard.html` als
   Ebenen-SVG exportieren und dort aufbauen.
6. Wenn nicht: die konkrete Grenze benennen und eine Entscheidung für einen
   anderen Renderer einholen. Raylight nicht nur dem Namen nach verwenden,
   während das Ergebnis heimlich woanders entsteht.

## 12. Assets und Qualität

Für **V2** sind keine externen Assets nötig — außer Logo und Schrift. Alle
Objekte sind Vektorformen und liegen bereits in `storyboard.html`.

Für die **reguläre 3D-Variante** gilt weiterhin: Es wurden bisher keine
hochwertigen, extern bezogenen und lizenzgeprüften 3D-Assets beschafft. Im
früheren HTML-Entwurf existieren lediglich prozedural erzeugte, stilisierte
Geometrien. Für jedes neue Asset Quelle, Lizenz, kommerzielle Nutzbarkeit und
Attribution dokumentieren. Bezahlte Modelle oder Renderkosten nicht ohne
Zustimmung auslösen.

## 13. Bisheriger Arbeitsstand und Grenzen

### Frameboards V2 — vorhanden

Drei Boards mit 18 Frames, erzeugt aus `storyboard.html` und als PNG gerendert.
Es sind **Storyboard-Mockups, keine Renderframes** einer laufenden Animation.
Schrift ist echtes Montserrat ExtraBold aus dem Design-System, die Farben navy /
night / paper / ink sind die bestätigten Tokens. Offen bleiben: das Logo (noch
Platzhalter) und das Orange (`#F0A32A`, ungeprüft — siehe oben). Zoomwerte,
Bildausschnitte und Objektpositionen sind belastbar und direkt übernehmbar.

### Frameboards 3D — fehlen

Für den Vergleich noch zu erstellen, im identischen Raster.

### Figma

Zwei frühere Figma-Outros auf „Reel-Bibliothek" verwenden noch ausgeschriebenes
DAMALS IN FARBE und andere Stadtobjekte. Inhaltlich überholt, nicht als Vorlage
übernehmen. Das Figma-Kit bleibt als CI-Quelle relevant.

### HTML/WebGL-Entwurf

[Private Vorschau](https://frankfurt-outro.roybera.chatgpt.site) — enthält
Logo, drei Textzeilen, Montserrat-Glyphen als SVG-Pfade,
Einzelbuchstaben-Farbwechsel, einfachen Kamerazoom und prozedurale Objekte. Der
Code wurde auf Syntax und vorhandene Assets geprüft; eine vollständige visuelle
Browser- und Exportprüfung fand nicht statt. Der Entwurf ist **keine
abgenommene Endanimation**. Deployment-Erfolg ist keine visuelle Abnahme.
Ursprünglicher Code-Ort: `/workspace/sites/frankfurt-outro/`. Diese Pfade
existieren nicht automatisch auf Sebastians Rechner. Den alten Code nicht als
Voraussetzung für den Neuansatz behandeln.

## 14. Gewünschte Ergebnisse und Abnahmekriterien

### Stufe 1 — gestalterische Entscheidung

1. Frameboards beider Varianten, 18 Frames, drei Abschnitte, je 3×2. ✅ für V2,
   ⬜ für 3D
2. Entscheidung von Sebastian für eine Variante.
3. Klärung der Orange-Frage (siehe Abschnitt 4) und die Logodatei
   `Group 77.svg`. Die Schrift ist beschafft.

### Stufe 2 — Produktion

4. Bearbeitbares Raylight-Projekt oder klar dokumentierte technische Grenze
   samt abgestimmter Alternative.
5. Abspielbare Vorschau der tatsächlichen Animation, nicht nur ein statisches
   Layout.
6. Geprüfter MP4-Export in 1080 × 1920, vorzugsweise 30 Bilder/s, ohne schwarze
   Ränder und ohne Bedienoberfläche.
7. Kurze Dokumentation: Dauer, verwendete Assets und Lizenzen, Export und
   spätere Wiederverwendung.

### Prüfliste vor der Übergabe

- FRA / NK / FURT korrekt, NK sichtbar eingerückt, Gesamtwort gut lesbar?
- Logo original, nicht als neuer Text nachgebaut, nicht umgefärbt?
- A durch Messeturmspitze ersetzt, Nilgans links neben N, U durch gefülltes
  Geripptes ersetzt?
- Bewegen sich die Objekte erkennbar räumlich — bei V2 über Lagenversatz,
  wechselnde Silhouette und wandernden Schatten, nicht durch bloßes Kippen
  eines flachen Bildes?
- Individuelle Blau-Orange-Wechsel statt kollektivem Effekt, nie mehr als zwei
  Zeichen gleichzeitig?
- Gold nirgends mehr als Akzentfarbe im Einsatz?
- Wirkt der Zoom wie der Referenzabschnitt ab ca. 5,5 s, nicht wie eine
  beliebige Slideshow?
- Kein Abschneiden wichtiger Elemente durch Formatwechsel oder typische
  Reel-Bedienflächen?
- Schlussbild ausreichend lange lesbar und mit gutem Kontrast?
- Start, größte Nahaufnahme, Zoommitte, jeder Objekteintritt und Schlussbild
  als echte Renderframes geprüft?
- MP4 vollständig abgespielt, Auflösung, Laufzeit und Bildrate kontrolliert,
  kein falsches Exportversprechen?

## 15. Einstiegsprompt für Claude Code

Du übernimmst die Fertigstellung meines Frankfurt-Abbinders für „Damals in
Farbe". Lies dieses Briefing und das Framebook vollständig; sie enthalten meine
verbindlichen Vorgaben und die Analyse der Videoreferenz. Analysiere den
Abschnitt von ungefähr 5,5 bis 10,1 Sekunden der Referenz selbst in Bewegung.

Beginne **nicht** mit der Produktion, sondern mit der gestalterischen Prüfung:
Es gibt zwei Varianten — V2 im Paper-Cutout-Stil und die reguläre Variante mit
3D-Objekten. Für V2 liegen die drei Frameboards mit 18 Frames bereits vor. Baue
den Vergleichssatz für die 3D-Variante im identischen Raster und hole meine
Entscheidung ein.

Es müssen ausdrücklich keine 3D-Objekte sein. Wenn du V2 umsetzt, muss die
Räumlichkeit trotzdem echt sein: Lagenversatz, wechselnde Silhouette und
wandernder Schatten. Ein flaches Bild zu kippen und es 3D zu nennen ist nicht
zulässig.

Verbindlich bleiben: enger Einstieg auf FRA, Zoom-out auf FRA / eingerücktes NK
/ FURT, einzeln zwischen CI-Blau und **Orange** wechselnde Buchstaben — Gold
wird nicht mehr verwendet. Das A wird zur Messeturmspitze, links neben N steht
eine Nilgans, das U wird zu einem mit Apfelwein gefüllten Gerippten. Verwende
mein originales Logo darüber, unverändert. Kläre vorher, woher das Orange kommt — mein Design-System kennt
nur Gold — und hol dir die Logodatei.

Prüfe echte Renderframes und liefere anschließend einen tatsächlich getesteten
Videoexport. Erfinde keine Raylight-Fähigkeiten.
