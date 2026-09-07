# Frankfurt SW-Archivbilder

Quelle: Google Drive, Geteilte Ablage FreeFlowCode_Home →
`2026_History Books / 01_HistoryBooks_Allgemein / Shortlist und SW-Bilder -
Bilder History Book Frankfurt (nicht im Buch enthalten)`
Ordner-ID `1UoRiGL8lrPa7zTUDQLpkXFJDi49rWr32` — 41 Dateien.

Der Ordner enthält benannte Archivaufnahmen, überwiegend von **Gottfried
Vömel** (ca. 1905–1930), dazu **Ria Schönberger** (ca. 1937), **Heinrich
Stürtz** (1910/1935), ein Lichtdruck von **Carl Hertel** (1896) und eine
Lithografie von **S. Prout** (1826). Auflösung der geprüften Dateien:
1512 × 2016 px, Hochformat — passt zu 9:16 ohne Hochskalieren.

Motive u. a.: Paulskirche, Römerberg, Alte Brücke, Rententurm, Hauptwache,
Konstablerwache, Goetheplatz, Große Bockenheimer Straße, Uhrtürmchen,
Haus zum Rebstock, Mainpanorama, Mainufer, Fünffingerplätzchen,
Christkindchesmarkt, Katharinenkirche, St. Leonhard, Junghof, Nizza am Main.

## Bisher geholt

| Datei | Motiv | Jahr |
|---|---|---|
| `1_gottfried-voemel-frankfurt-die-paulskirche-...jpg` | Paulskirche | ca. 1905 |
| `1_gottfried-voemel-frankfurt-roemerberg-...jpg` | Römerberg | ca. 1930 |

## Wie die restlichen zu holen sind

`drive.google.com` ist aus der Sitzung heraus **nicht direkt erreichbar**
(Egress-Proxy blockt, HTTP 000). Der funktionierende Weg:

1. `mcp__Google_Drive__download_file_content` mit der Datei-ID aufrufen.
2. Das Ergebnis ist zu groß für den Kontext und wird automatisch als JSON
   nach `~/.claude/projects/<projekt>/<session>/tool-results/` geschrieben.
3. Aus dieser Datei das Feld `content` base64-dekodieren — siehe
   `grab.py`-Muster in der Sitzung. Kostet praktisch keinen Kontext.

Ein Aufruf pro Datei. Die Datei-IDs stehen in der Drive-Suche über
`parentId = '1UoRiGL8lrPa7zTUDQLpkXFJDi49rWr32'`.

## Rechte

Vor der Veröffentlichung klären: Die Aufnahmen stammen aus Archivbeständen
und sind laut Ordnername **nicht im Buch enthalten**. Nutzungsrechte für
Social Media sind damit nicht automatisch gegeben und noch zu prüfen.
