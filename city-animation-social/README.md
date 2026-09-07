# City Animation Social

HTML-Outro-Animation für Videos. Eine einzige, selbstenthaltende Datei
(`index.html`) — keine Bilder, Fonts, Bibliotheken oder Build-Schritte.
Einfach im Browser öffnen.

## Was sie zeigt

Abendhimmel mit Sternen → Skyline steigt auf (zwei Parallax-Ebenen) →
Fenster gehen gestaffelt an → Logo, Titel, Untertitel, Social-Handles,
Abo-Button → Ausblendung nach Schwarz. Gesamtlänge ca. 7 Sekunden.

## Bedienung

| Taste | Funktion |
|-------|----------|
| `R` | Animation neu abspielen |
| `C` | Clean-Modus (Bedienleiste aus, für Bildschirmaufnahme) |
| `1` `2` `3` | Format 16:9 / 9:16 / 1:1 |

Alternativ über die Buttons unter der Bühne.

## URL-Parameter

Nützlich für Aufnahmen ohne Klicks:

```
index.html?format=9:16&clean&loop
```

- `format=` — `16:9` (Standard), `9:16`, `1:1`
- `clean` — startet ohne Bedienleiste
- `loop` — spielt endlos in Schleife

## Anpassen

Alle Texte stehen im `CONFIG`-Objekt am Anfang des `<script>`-Blocks:

```js
const CONFIG = {
  title:    "History Books",
  subtitle: "Geschichte, die bleibt",
  socials: [
    { icon: "yt",  label: "@historybooks" },
    { icon: "ig",  label: "@historybooks" },
    { icon: "web", label: "historybooks.de" }
  ],
  cta: "Abonnieren",
  duration: 7000,   // Gesamtlänge in ms
  fadeAt:   6.1,    // Sekunde, ab der nach Schwarz geblendet wird
  seed:     20260907 // Skyline-Zufallsmuster — andere Zahl = andere Stadt
};
```

Verfügbare Icons: `yt` (YouTube), `ig` (Instagram), `tt` (TikTok), `web`.

Farben: die CSS-Variablen unter `:root` (Nachtblau, Dämmerung, Gold, Amber).
Die Auflösung pro Format steht in `FORMATS` — `skyH` ist die Höhe der
Skyline, `cc` die vertikale Position des Textblocks.

## Als Videodatei aufnehmen

Die Animation läuft in Echtzeit im Browser. Zwei Wege:

1. **Bildschirmaufnahme** — `?clean` öffnen, Fenster auf die Zielauflösung
   ziehen, mit OBS o. ä. aufnehmen, `R` zum Starten.
2. **Frame-für-Frame rendern** — mit Playwright/Puppeteer die Seite laden,
   die Uhr per `page.clock` anhalten und Einzelbilder als PNG-Sequenz
   exportieren; danach mit `ffmpeg` zu MP4/MOV zusammensetzen. Liefert
   saubere 60 fps ohne Aufnahme-Ruckler.

Bei `prefers-reduced-motion` werden alle Animationen übersprungen — die
Endkomposition ist dann sofort sichtbar.
