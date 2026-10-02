# Fachwerkhaus: Bestandsgrundrisse EG und 1. OG (CAD)

Digitalisierung von zwei Fotos eines handbemaßten Bestandsplans („Erdgeschoß ±0,0“ und „1. Stock“)
als CAD-Zeichnung, gedacht als Grundlage für den Ausbau.

## Dateien

| Datei | Inhalt |
|---|---|
| `plaene/Fachwerkhaus_Bestand_1-50_A3.pdf` | Druckfertig: Blatt 1 EG, Blatt 2 OG (je A3 quer, **1:50**), Blatt 3–4 Prüfliste |
| `plaene/EG_Bestand.dxf` | Erdgeschoss als CAD-Datei (DXF R2013, Einheit **cm**) |
| `plaene/OG_Bestand.dxf` | 1. Obergeschoss als CAD-Datei |
| `plaene/Fachwerkhaus_Bestand_EG_OG.dxf` | Beide Geschosse in einer Datei (OG unter dem EG, gleiche x-Achse) |
| `plaene/*_1-50_A3.png` | Vorschaubilder |
| `plaene/EG_3D.glb` | 3D-Modell EG (glTF, Meter), öffnet z. B. mit Windows 3D-Viewer, Blender, SketchUp |
| `plaene/EG_3D.obj` + `.mtl` | 3D-Modell EG für ältere Programme |
| `plaene/EG_3D_Viewer.html` | 3D-Modell im Browser: drehen, Schnitthöhe, Ebenen, Räume anfliegen |
| `plaene/EG_Wandabwicklungen_1-50_A3.pdf` | Wandabwicklungen aller EG-Räume (Übersicht + 1 Blatt je Raum, A3, 1:50) |
| `plaene/EG_Wandabwicklungen.dxf` | dieselben Abwicklungen als CAD-Datei (cm) |
| `grundriss.py` | Generator: alle Maße stehen hier als Daten und lassen sich einzeln korrigieren |
| `hoehen.py` | Höhen für 3D und Abwicklungen (Raumhöhe 235 gemessen, übrige Höhen angenommen) |
| `modell3d.py`, `abwicklung.py` | erzeugen 3D-Modell bzw. Wandabwicklungen aus Grundriss + Höhen |

## Arbeits-Prompt (vor Beginn selbst formuliert)

> Du bist Bauzeichner/CAD-Techniker. Übertrage zwei eingescannte, handbemaßte Grundrisse (EG ±0,0 und
> 1. OG) eines Fachwerkhauses maßgetreu in eine echte CAD-Zeichnung.
> 1. **Maße vor Optik:** Die eingetragenen Maßzahlen (cm) gelten, nicht die Pixel. Lies jede Maßkette
>    einzeln aus (Ausschnitte vergrößern), prüfe, ob ihre Teilmaße die Gesamtmaße ergeben
>    (z. B. 27+328+22+131+20+221+22+397+18 = 1186), und markiere Widersprüche, statt sie zu verstecken.
> 2. **Koordinatensystem:** Nullpunkt an der Außenecke unten links, x nach rechts, y nach oben, Einheit cm.
>    Wandachsen und Wandstärken kommen aus den Maßketten, die Wandpositionen aus den Summen.
> 3. **Inhalt:** Außen- und Innenwände (geschnitten, gefüllt), Fenster (mit Brüstungsmarkierung), Türen mit
>    Aufschlag, Treppe mit Laufrichtungspfeil, Kamine/Schornsteine, Eingang. Dazu vollständige Maßketten wie
>    im Original und eine Raumnummerierung.
> 4. **Ausgabe:** DXF (Layer: Wände, Fenster, Türen, Treppe, Kamin, Bemaßung, Text, Achsen), dazu PDF/PNG im
>    Maßstab 1:100 mit Plankopf. Geschrieben als Python-Skript (ezdxf + matplotlib), damit sich jedes Maß
>    später an einer einzigen Stelle korrigieren lässt.
> 5. **Ehrlichkeit:** Unsichere oder unlesbare Werte kommen in eine Liste „Zu prüfen vor Ort“. Der Plan ist
>    Grundlage für einen Fachwerkausbau, also muss klar sein, was gemessen und was abgeleitet ist.

Abweichend vom Prompt: Die Pläne sind in **1:50** statt 1:100 ausgegeben, weil das der übliche Maßstab
für Ausbauplanung ist. Gerendert wird mit dem Zeichnungs-Add-on von ezdxf (PyMuPDF) statt mit
matplotlib, damit PDF und DXF aus denselben Objekten entstehen. Eine Achsen-Layer gibt es nicht,
da die Vorlage keine Achsen enthält.

## Vorgehen

1. Alle Maßketten beider Geschosse vergrößert und Zahl für Zahl ausgelesen. Jede Kette auf ihre
   Summe geprüft (EG oben 1186, unten 1191, links/rechts 813; OG 1190 × 708, Rücksprung 91).
2. Beide Fotos über die vier inneren Gebäudeecken perspektivisch entzerrt (1 px = 0,5 cm). So ließen
   sich Bauteile ohne Maßzahl (einige Türen, Schornsteine, Treppenstufen, gestrichelte Linien) abgreifen.
   Kontrolle: Die bemaßten Fenster liegen im entzerrten Bild innerhalb weniger Zentimeter auf ihren Maßketten.
3. Geometrie als Daten in `grundriss.py`. Wo die Kette oben und die Kette unten für dieselbe Wand
   verschiedene Werte haben, ist die Wand zwischen beiden Messpunkten schief gezeichnet. Jede Maßzahl
   gilt so an der Stelle, an der sie gemessen wurde.
4. Maßketten sind echte DXF-Bemaßungen (DIMENSION), der Wert entsteht aus der Geometrie. Weicht er vom
   Eintrag der Vorlage ab, steht ein `*` dahinter; die Gründe stehen in der Prüfliste (Blatt 3–4 im PDF).

## Was vor dem Ausbau vor Ort geprüft werden sollte

Die vollständige Liste steht im PDF. Am wichtigsten:

- **Widersprüche von 15–25 cm im OG** (Podest/Treppenhaus, Fenster oben, Öffnung 1.04→1.08). Die
  Ketten der Vorlage passen dort nicht zusammen.
- **Unbemaßte Teile** („ca.“): Öffnung links in 0.01, Türen 0.03→0.04 und 1.07→1.08, alle Schornsteine
  außer dem bei 0.07.
- **Lage OG zu EG**: Die Vorlage sagt nicht, wie die Geschosse übereinanderliegen. Die Treppe spricht für
  bündige Unterkanten, die Schornsteine liegen dann aber nicht deckungsgleich.
- **Gestrichelte Doppellinie im EG** (vermutlich Kellerumriss) und **dünne Zusatzlinie außen** (vermutlich
  Sockel oder Verkleidung): Bedeutung ist nicht beschriftet.
- Nordrichtung, Geschosshöhen, Treppensteigung, Balkenlage und Fachwerkständer sind in der Vorlage nicht enthalten.

## DXF öffnen

- Zeichnungseinheit ist **Zentimeter** (`$INSUNITS = 5`). Beim Import in Programme, die Millimeter
  erwarten, die Einheit auf cm stellen.
- Schrift: Arial (in der Zeichnung als Stil `PLAN`), Bemaßungsstil `BESTAND_1_50` für Ausgabe 1:50.
- Layer:

| Layer | Inhalt |
|---|---|
| `WAND`, `WAND_FUELLUNG` | Wandkonturen, graue Füllung |
| `FENSTER`, `FENSTER_UNKLAR` | Fenster; Öffnung links in 0.01 (Art unklar) |
| `TUER` | Haustür mit Aufschlag |
| `SCHORNSTEIN` | Schornsteine mit Zug |
| `TREPPE`, `TREPPE_LAUFLINIE` | Stufen, Bruchlinie, Lauflinie mit Pfeil |
| `KELLER_VERMUTET` | gestrichelte Linien der Vorlage (EG) |
| `LINIE_AUSSEN_VORLAGE` | Zusatzlinie außen (EG) |
| `BEMASSUNG` | Maßketten |
| `RAUMSTEMPEL` | Raumnummer und Fläche |
| `MARKIERUNG_1_VORLAGE` | handschriftliche blaue „1“ der Vorlage |
| `HINWEIS_PRUEFEN` | Hinweise in Rot |
| `PLANKOPF`, `PLANKOPF_DUENN`, `SYMBOLE` | Blattrahmen, Legende, Plankopf, Eingangspfeil |

Getestet: `ezdxf` Audit ohne Fehler. Geeignete Programme zum Weiterzeichnen sind z. B. LibreCAD, QCAD,
FreeCAD, DraftSight, AutoCAD, BricsCAD oder der DXF-Import von ArchiCAD/Vectorworks/SketchUp Pro.

## 3D-Modell und Wandabwicklungen (EG)

- Grundriss aus `grundriss.py`, Höhen aus `hoehen.py`: Raumhöhe **235 cm (gemessen)**; Brüstung 85,
  Fenstersturz 195, Türhöhe 200, Decke 25 cm sind **Annahmen**, weil der Plan keine Höhen enthält.
- Treppe: 15 Auftritte lt. Plan, 16 Steigungen bis OG-Fußboden (angenommen).
- Wandabwicklung: jede Wand von innen gesehen, im Uhrzeigersinn ab der oberen Wand (Planoben), mit
  Öffnungen, Maßketten und Netto-Wandfläche (ohne Öffnungen, ohne Laibungen). Schornsteinseiten und
  offene Raumübergänge sind getrennt gekennzeichnet; in Raum 0.06 ist die Treppenlinie eingezeichnet.

## Neu erzeugen

```bash
pip install -r requirements.txt
python3 grundriss.py && python3 modell3d.py && python3 abwicklung.py
```

Ein Maß korrigieren (z. B. nach dem Aufmaß vor Ort): Wert in `build_eg()` bzw. `build_og()` ändern und
das Skript erneut ausführen. Wände, Öffnungen, Maßketten, Flächen und PDF werden daraus neu berechnet.
