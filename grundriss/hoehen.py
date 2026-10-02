"""
Höhenannahmen für 3D-Modell und Wandabwicklungen (Erdgeschoss).

Die Vorlage ist ein reiner Grundriss ohne Höhenangaben. Die Raumhöhe ist vom
Eigentümer gemessen; alle übrigen Werte sind ANNAHMEN (übliche Maße für ein
älteres Fachwerkhaus) und müssen vor Ort gemessen werden. Nach dem Messen hier ändern und die Skripte neu ausführen:
    python3 modell3d.py && python3 abwicklung.py
Alle Maße in cm, bezogen auf Oberkante Fertigfußboden EG (±0,00).
"""

RAUMHOEHE = 235          # lichte Raumhöhe EG – gemessen (Angabe Eigentümer, 2,35 m)
DECKE = 25               # Deckenstärke EG/OG (für Treppensteigung)
FENSTER_BRUESTUNG = 85   # Oberkante Brüstung (Unterkante Fensteröffnung)
FENSTER_STURZ = 195      # Unterkante Sturz (Oberkante Fensteröffnung)
TUER_HOEHE = 200         # lichte Durchgangshöhe Türen/Öffnungen
TREPPE_STEIGUNGEN = 16   # Anzahl Steigungen EG -> OG (15 Auftritte lt. Plan)


def z_range(kind: str):
    """Höhenbereich einer Öffnung nach Art."""
    if kind in ("fenster", "fenster_unklar"):
        return FENSTER_BRUESTUNG, FENSTER_STURZ
    return 0, TUER_HOEHE
