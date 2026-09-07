# Frankfurt SW-Archivbilder

Quelle: Google Drive, Geteilte Ablage FreeFlowCode_Home →
`2026_History Books / 01_HistoryBooks_Allgemein / Shortlist und SW-Bilder -
Bilder History Book Frankfurt (nicht im Buch enthalten)`
Ordner-ID `1UoRiGL8lrPa7zTUDQLpkXFJDi49rWr32`.

**Alle 34 benannten Archivaufnahmen sind jetzt im Projekt.** Sieben
UUID-benannte Dateien im selben Ordner (z. B. `F9996C48-...jpeg`) wurden
ausgelassen — das sind Duplikate/Screenshots ohne Bildunterschrift, die
im München-Ordner in gleicher Form vorkamen.

`_kontaktbogen.jpg` zeigt alle 34 Bilder mit laufender Nummer als Übersicht.

## Fotografen und Motive

| Kürzel | Fotograf | Zeitraum | Anzahl |
|---|---|---|---|
| GV | Gottfried Vömel | ca. 1902–1930 | 28 |
| RS | Ria Schönberger | ca. 1937 | 3 |
| HS | Heinrich Stürtz | Aufnahme 1910, Abzug ca. 1935 | 1 |
| CH | Carl Hertel (Lichtdruck) | 1896 | 1 |
| SP | S. Prout (Lithografie) | 1826 | 1 |

Motive: Alte Brücke (6 Aufnahmen, verschiedene Zustände/Jahre), Paulskirche
(2), Römerberg, Rententurm (2), Hauptwache, Konstablerwache, Goetheplatz,
Katharinenkirche, St. Leonhard, Haus zum Rebstock, Junghof, Mainpanorama,
Nizza am Main, Fünffingerplätzchen (2), Christkindchesmarkt, Große
Bockenheimer Straße, Uhrtürmchen, diverse Gasthäuser, Sachsenhausen.

## Format

22 Bilder Querformat (2016×1512), 12 Bilder Hochformat (1512×2016). Für
9:16-Frames sind die Hochformat-Aufnahmen direkt brauchbar; Querformat
braucht einen Bildausschnitt oder eine Ausrichtung quer im Layout (wie im
Copenhagen-Referenzvideo, wo Fotostreifen ebenfalls in wechselnder
Orientierung erscheinen).

Alle Abzüge zeigen ihren originalen Rand/Passepartout — teils leicht
vergilbt, mit sichtbaren Ecken und Halterungsspuren. Das passt zum
Paper-Cutout-Charakter unmittelbar: die Bilder sehen bereits wie
freigestellte "Fotoschnipsel" aus, nicht wie glatte Digitalscans.

## Wie die Dateien geholt wurden

`drive.google.com` ist aus der Sitzung heraus **nicht direkt erreichbar**
(Egress-Proxy blockt, HTTP 000). Funktionierender Weg:

1. `mcp__Google_Drive__download_file_content` mit der Datei-ID aufrufen.
2. Das Ergebnis ist zu groß für den Kontext und wird automatisch als JSON
   nach `~/.claude/projects/<projekt>/<session>/tool-results/` geschrieben.
3. Das Feld `content` (base64) dekodieren — Muster:

```python
import json, base64, glob, os, re
TR = ".../tool-results"
for f in glob.glob(TR + "/mcp-Google_Drive-download_file_content-*.txt"):
    d = json.load(open(f))
    name = re.sub(r'[^A-Za-z0-9._-]', '_', d["title"])
    open(os.path.join(OUT, name), "wb").write(base64.b64decode(d["content"]))
```

Vier parallele Downloads pro Tool-Aufrunde funktionieren zuverlässig und
kosten kaum Kontext, da das Ergebnis sofort in die Datei ausgelagert wird.

## Rechte

**Noch zu klären.** Die Aufnahmen stammen aus Archivbeständen und sind laut
Ordnername "nicht im Buch enthalten". Die meisten sind über 100 Jahre alt
(gemeinfrei nach Ablauf der Schutzfrist wäre plausibel), aber der Abzug/Scan
selbst kann eigene Rechte tragen (Institutssammlung, Wasserzeichen o. ä.).
Vor Veröffentlichung im Abbinder prüfen, woher die Scans stammen und ob eine
Nennung nötig ist.
