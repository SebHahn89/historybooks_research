#!/usr/bin/env python3
"""
Bestandsgrundrisse Fachwerkhaus: Erdgeschoss (±0,00) und 1. Obergeschoss.

Digitalisiert aus zwei Fotos eines handbemaßten Bestandsplans.

Einheit: cm. Ursprung je Geschoss: äußere Gebäudeecke unten links,
x nach rechts, y nach oben ("oben" = Oberkante des Originalblatts).

Grundsatz: Eingetragene Maßzahlen sind maßgebend. Wo die Vorlage keine Maße
hat, wurden Werte aus dem perspektivisch entzerrten Foto abgegriffen
("ca.", Genauigkeit etwa ±10 cm). Widersprüche zwischen Maßketten sind in
PRUEFLISTE dokumentiert und in der Zeichnung mit * markiert.

Aufruf:  python3 grundriss.py        (benötigt ezdxf, shapely, pymupdf)
Ausgabe: plaene/*.dxf, plaene/*.pdf, plaene/*.png
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
from ezdxf.addons.drawing.config import (BackgroundPolicy, ColorPolicy, Configuration,
                                         LineweightPolicy)
from ezdxf.enums import TextEntityAlignment
from ezdxf.fonts import fonts
from ezdxf.math import BoundingBox2d
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plaene")

# ---------------------------------------------------------------- Blatt / Stil
SCALE = 50                 # 1:50
MM = SCALE / 10.0          # Modell-cm je Papier-mm (1 mm Papier = 5 cm)
SHEET_W, SHEET_H = 420, 297  # A3 quer, mm
TXT_DIM = 2.5              # Maßzahlen, mm Papier
ROW0 = 50                  # Abstand 1. Maßkette von der Fassade, cm
ROWD = 33                  # Abstand der Maßketten untereinander, cm
DATUM = "28.09.2026"

GRAY_WALL = (205, 205, 205)
GRAY_CHIM = (150, 150, 150)
LT_KELLER = 25.0           # Linientypfaktor gestrichelt (Keller)
LT_TUER = 12.0
BLUE = (30, 70, 200)
RED = (200, 30, 30)


# ---------------------------------------------------------------- Geometrie
class VBand:
    """Senkrechte Wand, deren Flächen unten (y=0) und oben (y=H) an
    unterschiedlichen x-Werten gemessen wurden (leicht schiefe Wand)."""

    def __init__(self, xl0, xr0, xl1, xr1, H):
        self.xl0, self.xr0, self.xl1, self.xr1, self.H = xl0, xr0, xl1, xr1, H

    def xl(self, y):
        return self.xl0 + (self.xl1 - self.xl0) * y / self.H

    def xr(self, y):
        return self.xr0 + (self.xr1 - self.xr0) * y / self.H

    def poly(self, y0=None, y1=None):
        y0 = 0 if y0 is None else y0
        y1 = self.H if y1 is None else y1
        return Polygon([(self.xl(y0), y0), (self.xr(y0), y0),
                        (self.xr(y1), y1), (self.xl(y1), y1)])


@dataclass
class Opening:
    kind: str            # fenster | fenster_unklar | oeffnung | haustuer
    orient: str          # 'h' (Wand waagrecht) | 'v' (Wand senkrecht)
    a0: float            # Beginn entlang der Wand (x bei h, y bei v)
    a1: float            # Ende entlang der Wand
    f0: Callable         # Wandfläche 1 als Funktion der Laufkoordinate
    f1: Callable         # Wandfläche 2
    hinge: str = ""      # Haustür: Band-Seite 'a0' | 'a1'
    swing: int = 1       # Haustür: Aufschlagrichtung (+1 = in +y bzw. +x)

    def cut(self):
        if self.orient == "h":
            lo = min(self.f0(self.a0), self.f1(self.a0)) - 1
            hi = max(self.f0(self.a0), self.f1(self.a0)) + 1
            return box(self.a0, lo, self.a1, hi)
        lo = min(self.f0(self.a0), self.f1(self.a0), self.f0(self.a1), self.f1(self.a1)) - 1
        hi = max(self.f0(self.a0), self.f1(self.a0), self.f0(self.a1), self.f1(self.a1)) + 1
        return box(lo, self.a0, hi, self.a1)

    def face_line(self, f, shift=0.0):
        if self.orient == "h":
            return [(self.a0, f(self.a0) + shift), (self.a1, f(self.a1) + shift)]
        return [(f(self.a0) + shift, self.a0), (f(self.a1) + shift, self.a1)]

    def mid(self):
        return lambda t: (self.f0(t) + self.f1(t)) / 2


def c(v):
    """Konstante Wandfläche."""
    return lambda _t: v


@dataclass
class Chimney:
    x0: float
    y0: float
    x1: float
    y1: float
    inset: float = 8.0


@dataclass
class Chain:
    axis: str                     # 'x' = waagrechte Kette, 'y' = senkrechte Kette
    pts: list                     # Messpunkte entlang der Achse
    row: float                    # Lage der Maßlinie (y bzw. x)
    toward: int                   # Richtung zum Gebäude (+1/-1) für Hilfslinien
    labels: dict = field(default_factory=dict)   # Segmentindex -> Text ('<>' = Messwert)
    skip: set = field(default_factory=set)       # Segmente ohne Maß (nur Hilfslinie)


@dataclass
class Floor:
    key: str
    title: str
    subtitle: str
    outline: Polygon
    walls: list
    openings: list
    chimneys: list
    stair: dict
    chains: list
    marks_1: list                 # handschriftliche "1" der Vorlage
    rooms: list                   # (Nr, Saatfläche, Textposition)
    extra_lines: list = field(default_factory=list)   # Zusatzlinie außen
    dashed: list = field(default_factory=list)        # gestrichelte Linien der Vorlage
    entrance: tuple | None = None
    legend_extra: list = field(default_factory=list)


# ============================================================ ERDGESCHOSS
def build_eg() -> Floor:
    H = 813
    outline = Polygon([(0, 0), (1191, 0), (1186, H), (0, H)])
    # Schiefe Wände: Maßkette oben (y=813) und unten (y=0) weichen ab.
    right = VBand(1173, 1191, 1168, 1186, H)   # Außenwand rechts (unten 18, oben 18)
    wallA = VBand(363, 385, 355, 377, H)       # Innenwand links (oben 355-377, unten 363-385)

    walls = [
        box(0, 0, 27, H),                               # Außenwand links 27
        box(-1, 0, 1300, 27).intersection(outline),     # Außenwand unten 27
        box(-1, 791, 1300, H).intersection(outline),    # Außenwand oben 22
        right.poly(),                                   # Außenwand rechts 18
        wallA.poly(),                                   # Wand A (22)
        box(20, 462, 366, 484),                         # Wand Raum 0.01/0.05 (22)
        box(372, 432, 749, 459),                        # Querwand Mitte (27)
        box(760, 429, 1180, 451),                       # Querwand rechts (22)
        box(749, 432, 771, H - 10),                     # Wand C oben (22)
        box(748, 0, 776, 451),                          # Wand C unten (28)
        box(508, 450, 528, H - 10),                     # Wand Raum 0.02/0.03 (20)
        box(460, 250, 477, 440),                        # Treppenwange/-wand senkrecht (17)
        box(460, 250, 538, 267),                        # Wand unter Treppenauge (17)
        box(523, 20, 538, 178),                         # Flurwand rechts (15)
    ]
    top_i, top_o = c(791), c(813)
    bot_i, bot_o = c(27), c(0)
    ow = [
        # Fenster Außenwand oben
        Opening("fenster", "h", 140, 225, top_i, top_o),
        Opening("fenster", "h", 396, 471, top_i, top_o),
        Opening("fenster", "h", 528, 616, top_i, top_o),
        Opening("fenster", "h", 948, 1031, top_i, top_o),
        # Außenwand unten
        Opening("fenster", "h", 135, 282, bot_i, bot_o),
        Opening("haustuer", "h", 428, 523, bot_i, bot_o, hinge="a0", swing=+1),
        Opening("fenster", "h", 593, 730, bot_i, bot_o),
        Opening("fenster", "h", 904, 1041, bot_i, bot_o),
        # Außenwand rechts (schief)
        Opening("fenster", "v", 155, 243, right.xl, right.xr),
        Opening("fenster", "v", 277, 365, right.xl, right.xr),
        Opening("fenster", "v", 528, 614, right.xl, right.xr),
        # Außenwand links: Öffnung ohne Maß (Brüstungslinien, kein Glas gezeichnet)
        Opening("fenster_unklar", "v", 505, 594, c(27), c(0)),
        # Innentüren / Durchgänge (in der Vorlage ohne Türblatt)
        Opening("oeffnung", "v", 148, 232, wallA.xl, wallA.xr),        # 0.05 -> Flur
        Opening("oeffnung", "h", 597, 685, c(432), c(459)),            # Mitte -> 0.03
        Opening("oeffnung", "v", 167, 249, c(748), c(776)),            # Mitte -> 0.08
        Opening("oeffnung", "v", 503, 587, c(749), c(771)),            # 0.03 -> 0.04 (ca.)
        Opening("oeffnung", "v", 679, 751, c(508), c(528)),            # 0.02 -> 0.03
    ]
    chimneys = [
        Chimney(wallA.xl(508) - 54, 484, wallA.xl(508), 533),   # ca. 54/49, unbemaßt
        Chimney(695, 383, 749, 432),                           # 54 x 46 (bemaßt)
    ]
    stair = dict(xl=wallA.xr, xr=460, y0=250, y1=432, n=15,
                 brk=((372,), (460, 415)), arrow_x=421, arrow_y0=258, arrow_tip=352)

    X = "x"
    Y = "y"
    top = 813 + ROW0
    bot = -(ROW0 + 62)          # Platz für Eingangspfeil
    lft = -ROW0
    rgt = 1191 + ROW0
    chains = [
        # ---- oben (von innen nach außen)
        Chain(X, [0, 27, 140, 225, 355, 377, 396, 471, 508, 528, 616, 749, 771, 948, 1031, 1168, 1186],
              top, -1),
        Chain(X, [695, 749], top + ROWD, -1),
        Chain(X, [528, 597, 685, 749], top + 2 * ROWD, -1),
        Chain(X, [0, 27, 355, 377, 508, 528, 749, 771, 1168, 1186], top + 3 * ROWD, -1),
        Chain(X, [0, 1186], top + 4 * ROWD, -1),
        # ---- unten (von innen nach außen)
        Chain(X, [0, 135, 282], bot, +1),
        Chain(X, [385, 460, 538], bot, +1),
        Chain(X, [904, 1041, 1191], bot, +1),
        Chain(X, [363, 385, 523, 538], bot - ROWD, +1),
        Chain(X, [593, 730, 1191], bot - ROWD, +1),
        Chain(X, [0, 428, 523, 1191], bot - 2 * ROWD, +1),
        Chain(X, [0, 27, 363, 385, 748, 776, 1173, 1191], bot - 3 * ROWD, +1),
        Chain(X, [0, 1191], bot - 4 * ROWD, +1),
        # ---- links (von innen nach außen)
        Chain(Y, [250, 267], lft + 25, +1),
        Chain(Y, [505, 594], lft + 25, +1, labels={0: "ca. <>"}),
        Chain(Y, [27, 178, 250, 432], lft - 5, +1),
        Chain(Y, [27, 148, 232, 432, 459, 679, 751, 791], lft - 5 - ROWD, +1,
              labels={4: "<>*"}),
        Chain(Y, [27, 432, 459, 791], lft - 5 - 2 * ROWD, +1, labels={2: "<>*"}),
        Chain(Y, [0, 27, 462, 484, 791, 813], lft - 5 - 3 * ROWD, +1),
        Chain(Y, [0, 813], lft - 5 - 4 * ROWD, +1),
        # ---- rechts (von innen nach außen)
        Chain(Y, [0, 27, 155, 243, 277, 365, 429, 451, 528, 614, 791, 813], rgt, -1),
        Chain(Y, [27, 167, 249], rgt + ROWD, -1),
        Chain(Y, [383, 429], rgt + ROWD, -1),
        Chain(Y, [0, 27, 429, 451, 791, 813], rgt + 2 * ROWD, -1),
    ]
    marks = [(178, 662), (450, 594), (648, 601), (978, 604),
             (197, 242), (437, 172), (603, 326), (971, 204)]
    rooms = [
        ("0.01", box(27, 484, 360, 791), (120, 560)),
        ("0.02", box(377, 459, 508, 791), (442, 700)),
        ("0.03", box(528, 459, 749, 791), (638, 700)),
        ("0.04", box(771, 451, 1170, 791), (975, 700)),
        ("0.05", box(27, 27, 365, 462), (195, 360)),
        ("0.06", unary_union([box(378, 27, 530.5, 250), box(378, 250, 460, 432)]), (492, 215)),
        ("0.07", unary_union([box(530.5, 27, 748, 432), box(460, 250, 530.5, 432)]), (640, 392)),
        ("0.08", box(776, 27, 1174, 429), (975, 330)),
    ]
    # Zusatzlinie außen (oben, rechts, unten) – Bedeutung unklar
    b = outline.buffer(8, join_style=2)
    tr = max((p for p in b.exterior.coords if p[1] > 400), key=lambda p: p[0])
    br = max((p for p in b.exterior.coords if p[1] < 400), key=lambda p: p[0])
    extra = [[(0, 821), tr, br, (0, -8)]]
    dashed = [
        [(622, 27), (622, 272), (862, 272), (862, 429)],
        [(654, 27), (654, 238), (900, 238), (900, 416), (right.xl(416), 416)],
    ]
    return Floor(
        key="EG", title="Grundriss Erdgeschoss ±0,00", subtitle="Erdgeschoss (EG)",
        outline=outline, walls=walls, openings=ow, chimneys=chimneys, stair=stair,
        chains=chains, marks_1=marks, rooms=rooms, extra_lines=extra, dashed=dashed,
        entrance=(475.5, -92, -14),
        legend_extra=["keller", "zusatzlinie"],
    )


# ============================================================ OBERGESCHOSS
def build_og() -> Floor:
    H = 708
    outline = Polygon([(0, 0), (1190, 0), (1190, 617), (759, 617), (759, H), (0, H)])
    wallT = VBand(365, 382, 370, 387, H)   # Treppenhauswand links (oben 370-387, unten 365-382)
    walls = [
        box(0, 0, 25, H),                      # Außenwand links 25
        box(0, 0, 1190, 17),                   # Außenwand unten 17
        box(0, 691, 759, H),                   # Außenwand oben 17
        box(742, 10, 759, H),                  # Wand 742-759 (inkl. Rücksprung)
        box(742, 600, 1190, 617),              # Außenwand oben rechts (Rücksprung 91)
        box(1172, 0, 1190, 617),               # Außenwand rechts 18
        wallT.poly(),                          # Treppenhauswand links 17
        box(20, 407, 372, 419),                # Wand 1.01/1.02 (12)
        box(375, 544, 472, 564),               # Wandstück über Podest (20)
        box(462, 162, 472, 434),               # Treppenwand rechts (10)
        box(378, 162, 472, 174),               # Abschluss Treppe unten (12)
        box(537, 249, 750, 261),               # Querwand (12)
        box(592, 10, 604, 255),                # Wand Flur/1.06 (12)
        box(750, 419, 1180, 431),              # Querwand rechts (12)
    ]
    ow = [
        Opening("fenster", "h", 557, 630, c(691), c(708)),
        Opening("oeffnung", "v", 436, 506, c(25), c(0)),
        Opening("fenster", "v", 160, 278, c(25), c(0)),
        Opening("fenster", "v", 157, 223, c(1172), c(1190)),
        Opening("fenster", "v", 246, 312, c(1172), c(1190)),
        Opening("fenster", "v", 436, 476, c(1172), c(1190)),
        Opening("fenster", "h", 537, 584, c(17), c(0)),
        Opening("fenster", "h", 615, 662, c(17), c(0)),
        Opening("oeffnung", "v", 82, 152, wallT.xl, wallT.xr),     # Flur -> 1.02
        Opening("oeffnung", "v", 469, 544, wallT.xl, wallT.xr),    # Podest -> 1.01
        Opening("oeffnung", "v", 92, 149, c(592), c(604)),         # Flur -> 1.06
        Opening("oeffnung", "v", 324, 419, c(742), c(759)),        # 1.04 -> 1.08
        Opening("oeffnung", "h", 865, 945, c(419), c(431)),        # 1.07 -> 1.08 (ca.)
    ]
    chimneys = [
        Chimney(wallT.xl(384) - 54, 361, wallT.xl(384), 407),   # ca. 54/46, unbemaßt
        Chimney(688, 261, 742, 309),                           # ca. 54/48, unbemaßt
    ]
    stair = dict(xl=wallT.xr, xr=462, y0=174, y1=434, n=None, step=12.5,
                 brk=((347,), (462, 404)), arrow_x=423, arrow_y0=181, arrow_tip=290)
    X, Y = "x", "y"
    top = H + ROW0
    bot = -ROW0
    lft = -ROW0
    rgt = 1190 + ROW0
    chains = [
        Chain(X, [370, 387, 557, 630, 742, 759], top, -1, labels={1: "<>*"}),
        Chain(X, [0, 25, 370, 387, 742, 759, 1172, 1190], top + ROWD, -1),
        Chain(X, [0, 1190], top + 2 * ROWD, -1),
        Chain(X, [365, 382, 537, 584, 592, 604, 615, 662, 742, 759], bot, +1, labels={7: "<>*"}),
        Chain(X, [25, 365, 382, 462, 472, 537, 742, 759, 1172], bot - ROWD, +1),
        Chain(X, [0, 25, 365, 382, 592, 604, 742, 759, 1172, 1190], bot - 2 * ROWD, +1),
        Chain(X, [0, 1190], bot - 3 * ROWD, +1),
        Chain(Y, [0, 17, 160, 278, 407, 419], lft, +1),
        Chain(Y, [0, 17, 162, 174, 434, 544, 564, 691, 708], lft - ROWD, +1,
              labels={4: "<>*", 6: "<>*"}),
        Chain(Y, [0, 17, 82, 152, 407, 419, 469, 544, 691, 708], lft - 2 * ROWD, +1,
              labels={3: "<>*", 5: "<>*"}),
        Chain(Y, [0, 17, 436, 506, 691, 708], lft - 3 * ROWD, +1),
        Chain(Y, [0, 708], lft - 4 * ROWD, +1),
        Chain(Y, [0, 17, 157, 223, 246, 312, 419, 431, 436, 476, 600, 617], rgt, -1),
        Chain(Y, [17, 249, 261, 324, 419, 431, 691], rgt + ROWD, -1, labels={3: "<>*"}),
        Chain(Y, [0, 17, 419, 431, 600, 617, 691, 708], rgt + 2 * ROWD, -1),
        Chain(Y, [0, 617, 708], rgt + 3 * ROWD, -1),
        # innen: Tür in Wand Flur/1.06
        Chain(Y, [17, 92, 149, 249], 650, -1, labels={0: "<>*"}),
        # innen: Tür 1.07/1.08 (unbemaßt)
        Chain(X, [865, 945], 470, -1, labels={0: "ca. <>"}),
    ]
    marks = [(165, 542), (418, 488), (565, 491), (965, 501),
             (158, 187), (501, 120), (693, 117), (968, 190)]
    rooms = [
        ("1.01", box(25, 419, 371, 691), (230, 470)),
        ("1.02", box(25, 17, 367, 407), (120, 300)),
        ("1.03", box(380, 174, 472, 544), (428, 523)),
        ("1.04", unary_union([box(472, 255, 750.5, 691), box(385, 564, 472, 691)]), (640, 420)),
        ("1.05", unary_union([box(380, 17, 598, 168), box(462, 168, 598, 255)]), (440, 60)),
        ("1.06", box(598, 17, 742, 249), (700, 210)),
        ("1.07", box(759, 425, 1172, 600), (1060, 560)),
        ("1.08", box(750.5, 17, 1172, 425), (1060, 330)),
    ]
    return Floor(
        key="OG", title="Grundriss 1. Obergeschoss (1. Stock)", subtitle="1. Obergeschoss (OG)",
        outline=outline, walls=walls, openings=ow, chimneys=chimneys, stair=stair,
        chains=chains, marks_1=marks, rooms=rooms,
    )


# ============================================================ DXF-AUSGABE
LAYERS = {
    # name: (farbe ACI, linienstärke 1/100 mm, linientyp)
    "WAND": (7, 50, "Continuous"),
    "WAND_FUELLUNG": (8, 0, "Continuous"),
    "FENSTER": (7, 25, "Continuous"),
    "FENSTER_UNKLAR": (7, 18, "Continuous"),
    "TUER": (7, 25, "Continuous"),
    "SCHORNSTEIN": (7, 35, "Continuous"),
    "TREPPE": (7, 18, "Continuous"),
    "TREPPE_LAUFLINIE": (7, 25, "Continuous"),
    "KELLER_VERMUTET": (8, 25, "DASHED"),
    "LINIE_AUSSEN_VORLAGE": (7, 18, "Continuous"),
    "BEMASSUNG": (7, 18, "Continuous"),
    "RAUMSTEMPEL": (7, 18, "Continuous"),
    "MARKIERUNG_1_VORLAGE": (5, 25, "Continuous"),
    "HINWEIS_PRUEFEN": (1, 18, "Continuous"),
    "SYMBOLE": (7, 25, "Continuous"),
    "PLANKOPF": (7, 25, "Continuous"),
    "PLANKOPF_DUENN": (7, 13, "Continuous"),
}


def new_doc():
    doc = ezdxf.new("R2013", setup=True, units=ezdxf.units.CM)
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LUNITS"] = 2
    for name, (col, lw, lt) in LAYERS.items():
        doc.layers.add(name, color=col, lineweight=lw, linetype=lt)
    doc.styles.add("PLAN", font="arial.ttf")
    doc.styles.add("PLAN_FETT", font="arialbd.ttf")
    doc.styles.add("HAND", font="ariali.ttf")
    ds = doc.dimstyles.new("BESTAND_1_50")
    ds.dxf.dimtxsty = "PLAN"
    ds.dxf.dimscale = MM          # Papier-mm -> Modell-cm
    ds.dxf.dimtxt = TXT_DIM
    ds.dxf.dimasz = 1.5
    ds.dxf.dimtsz = 1.2           # Architekturstriche statt Pfeile
    ds.dxf.dimexe = 1.2
    ds.dxf.dimexo = 0.0
    ds.dxf.dimgap = 0.6
    ds.dxf.dimtad = 1
    ds.dxf.dimtih = 0
    ds.dxf.dimtoh = 0
    ds.dxf.dimdec = 0
    ds.dxf.dimlunit = 2
    ds.dxf.dimdsep = ord(",")
    ds.dxf.dimtmove = 2
    ds.dxf.dimlwd = 18
    ds.dxf.dimlwe = 13
    ds.dxf.dimclrd = 7
    ds.dxf.dimclre = 7
    ds.dxf.dimclrt = 7
    ds.dxf.dimtofl = 1
    ds.dxf.dimatfit = 3
    return doc


def _polys(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def _clean(poly: Polygon) -> Polygon:
    return poly.simplify(0.01, preserve_topology=True)


def add_poly_outline(msp, poly, layer, off):
    ox, oy = off
    for ring in [poly.exterior, *poly.interiors]:
        pts = [(x + ox, y + oy) for x, y in ring.coords[:-1]]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})


def add_poly_fill(msp, poly, layer, rgb, off, pattern=None, pscale=1.0, pangle=0.0):
    ox, oy = off
    h = msp.add_hatch(dxfattribs={"layer": layer})
    if pattern:
        h.set_pattern_fill(pattern, scale=pscale, angle=pangle)
        h.dxf.color = 7
    else:
        h.set_solid_fill(rgb=rgb)
    h.paths.add_polyline_path([(x + ox, y + oy) for x, y in poly.exterior.coords[:-1]],
                              is_closed=True, flags=1)
    for ring in poly.interiors:
        h.paths.add_polyline_path([(x + ox, y + oy) for x, y in ring.coords[:-1]],
                                  is_closed=True, flags=0)
    return h


def text(msp, s, x, y, h, layer, off, align=TextEntityAlignment.MIDDLE_CENTER,
         style="PLAN", rot=0.0, rgb=None):
    t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": style})
    t.set_placement((x + off[0], y + off[1]), align=align)
    if rgb:
        t.rgb = rgb
    return t


_FONT_CACHE = {}


def text_width(s, h, bold=False):
    """Textbreite in Zeichnungseinheiten (Schrifthöhe = Versalhöhe wie in DXF)."""
    key = (bold, round(h, 4))
    if key not in _FONT_CACHE:
        name = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
        _FONT_CACHE[key] = fonts.make_font(name, cap_height=h)
    return _FONT_CACHE[key].text_width(s)


def draw_chain(msp, ch: Chain, off):
    """Maßkette als echte DIMENSION-Objekte; kleine Maße werden seitlich versetzt."""
    ox, oy = off
    txt = TXT_DIM * MM
    gap = 0.6 * MM
    ext = 6.0                       # Länge der Hilfslinie zum Gebäude hin (cm)
    pts = ch.pts
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    labels = []
    for i, (a, b) in enumerate(segs):
        val = f"{round(b - a):d}"
        lab = ch.labels.get(i, "<>").replace("<>", val)
        labels.append(lab)
    pad = 1.0
    # Textpositionen: Start in Segmentmitte, dann Überlappungen auseinanderschieben.
    # Passende Maßzahlen bleiben innerhalb ihres Segments, zu kleine dürfen seitlich
    # heraus (so nah wie möglich an ihrem Maß).
    widths = [text_width(l, txt) for l in labels]
    sep = 0.95 * text_width("0", txt)          # Mindestabstand zwischen Maßzahlen
    idx = [i for i in range(len(segs)) if i not in ch.skip]
    pos = {i: (segs[i][0] + segs[i][1]) / 2 for i in idx}
    lo, hi = {}, {}
    for i in idx:
        a, b = segs[i]
        w = widths[i]
        if w + 2 * pad <= b - a:
            lo[i], hi[i] = a + pad + w / 2, b - pad - w / 2
        else:
            lo[i], hi[i] = a - 4 * w, b + 4 * w
    for _ in range(400):
        moved = False
        for k in range(len(idx) - 1):
            i, j = idx[k], idx[k + 1]
            need = (widths[i] + widths[j]) / 2 + sep
            d = pos[j] - pos[i]
            if d < need - 1e-6:
                deficit = need - d
                room_i = pos[i] - lo[i]
                room_j = hi[j] - pos[j]
                mi = min(deficit / 2, room_i)
                mj = min(deficit - mi, room_j)
                mi = min(deficit - mj, room_i)
                pos[i] -= mi
                pos[j] += mj
                moved = moved or (mi + mj) > 1e-6
        if not moved:
            break
    pos = [pos.get(i) for i in range(len(segs))]

    for i, (a, b) in enumerate(segs):
        if i in ch.skip:
            continue
        if ch.axis == "x":
            p1 = (a + ox, ch.row - ch.toward * ext + oy)
            p2 = (b + ox, ch.row - ch.toward * ext + oy)
            base = ((a + b) / 2 + ox, ch.row + oy)
            loc = (pos[i] + ox, ch.row + gap + txt / 2 + oy)
            angle = 0
        else:
            p1 = (ch.row - ch.toward * ext + ox, a + oy)
            p2 = (ch.row - ch.toward * ext + ox, b + oy)
            base = (ch.row + ox, (a + b) / 2 + oy)
            loc = (ch.row - gap - txt / 2 + ox, pos[i] + oy)
            angle = 90
        lab = labels[i]
        measured = f"{round(b - a):d}"
        dtext = "<>" if lab == measured else lab
        d = msp.add_linear_dim(base=base, p1=p1, p2=p2, location=loc, angle=angle,
                               text=dtext, dimstyle="BESTAND_1_50",
                               dxfattribs={"layer": "BEMASSUNG"})
        d.render()


def draw_floor(msp, fl: Floor, off=(0.0, 0.0)):
    ox, oy = off
    # ---- Wände
    wall_all = unary_union(fl.walls).intersection(fl.outline)
    cuts = unary_union([o.cut() for o in fl.openings])
    chim_polys = [box(k.x0, k.y0, k.x1, k.y1).difference(wall_all) for k in fl.chimneys]
    wall_cut = wall_all.difference(cuts)
    for p in _polys(wall_cut):
        p = _clean(p)
        add_poly_fill(msp, p, "WAND_FUELLUNG", GRAY_WALL, off)
        add_poly_outline(msp, p, "WAND", off)

    # ---- Öffnungen
    for o in fl.openings:
        if o.kind == "fenster":
            for f in (o.f0, o.f1):
                msp.add_lwpolyline([(x + ox, y + oy) for x, y in o.face_line(f)],
                                   dxfattribs={"layer": "FENSTER"})
            mid = o.mid()
            for s in (-2.5, 2.5):
                msp.add_lwpolyline([(x + ox, y + oy) for x, y in o.face_line(mid, s)],
                                   dxfattribs={"layer": "FENSTER"})
            # Blendrahmen-Abschluss an den Laibungen
            for t in (o.a0, o.a1):
                if o.orient == "h":
                    pts = [(t, mid(t) - 2.5), (t, mid(t) + 2.5)]
                else:
                    pts = [(mid(t) - 2.5, t), (mid(t) + 2.5, t)]
                msp.add_lwpolyline([(x + ox, y + oy) for x, y in pts],
                                   dxfattribs={"layer": "FENSTER"})
        elif o.kind == "fenster_unklar":
            for f in (o.f0, o.f1):
                msp.add_lwpolyline([(x + ox, y + oy) for x, y in o.face_line(f)],
                                   dxfattribs={"layer": "FENSTER_UNKLAR"})
        elif o.kind == "haustuer":
            # Türblatt 90° geöffnet + Aufschlagbogen (Band an a0)
            inner = o.f0(o.a0)
            hx = o.a0 if o.hinge == "a0" else o.a1
            w = o.a1 - o.a0
            msp.add_lwpolyline([(hx + ox, inner + oy), (hx + ox, inner + o.swing * w + oy)],
                               dxfattribs={"layer": "TUER"})
            msp.add_lwpolyline([(hx + ox + (4 if o.hinge == 'a0' else -4), inner + oy),
                                (hx + ox + (4 if o.hinge == 'a0' else -4), inner + o.swing * w + oy),
                                (hx + ox, inner + o.swing * w + oy)],
                               dxfattribs={"layer": "TUER"})
            if o.hinge == "a0":
                msp.add_arc((hx + ox, inner + oy), w, 0, 90, dxfattribs={"layer": "TUER"})
            else:
                msp.add_arc((hx + ox, inner + oy), w, 90, 180, dxfattribs={"layer": "TUER"})
            # Schwelle / Anschlag in Wandmitte
            mid = o.mid()
            msp.add_lwpolyline([(o.a0 + ox, mid(o.a0) + oy), (o.a1 + ox, mid(o.a1) + oy)],
                               dxfattribs={"layer": "TUER", "linetype": "DASHED", "ltscale": LT_TUER})

    # ---- Schornsteine
    for k, p in zip(fl.chimneys, chim_polys):
        i = k.inset
        fx0, fy0, fx1, fy1 = k.x0 + i, k.y0 + i, k.x1 - i, k.y1 - i
        flue = box(fx0, fy0, fx1, fy1)
        for q in _polys(p):
            q = _clean(q)
            add_poly_fill(msp, q.difference(flue), "SCHORNSTEIN", GRAY_CHIM, off, pattern="ANSI31",
                          pscale=2.2, pangle=0)
            add_poly_outline(msp, q, "SCHORNSTEIN", off)
        add_poly_outline(msp, flue, "SCHORNSTEIN", off)
        tri = Polygon([(fx0, fy0), (fx1, fy1), (fx0, fy1)])
        h = msp.add_hatch(dxfattribs={"layer": "SCHORNSTEIN"})
        h.set_solid_fill(color=7)
        h.paths.add_polyline_path([(x + ox, y + oy) for x, y in tri.exterior.coords[:-1]],
                                  is_closed=True)
    # ---- Treppe
    st = fl.stair
    xl, xr, y0, y1 = st["xl"], st["xr"], st["y0"], st["y1"]
    (by0,), (bx1, by1) = st["brk"]
    bx0 = xl(by0)

    def brk_y(x):
        return by0 + (by1 - by0) * (x - bx0) / (bx1 - bx0)

    step = st.get("step") or (y1 - y0) / st["n"]
    y = y0
    while y < y1 - 0.1:
        xa = xl(y)
        # Stufe nur unterhalb der Bruchlinie
        if y < brk_y(xa) - 0.5:
            if y <= brk_y(xr):
                xe = xr
            else:
                xe = bx0 + (y - by0) * (bx1 - bx0) / (by1 - by0)
            msp.add_line((xa + ox, y + oy), (xe + ox, y + oy), dxfattribs={"layer": "TREPPE"})
        y += step
    # Bruchlinie mit Zacke
    mx = (bx0 + bx1) / 2
    my = brk_y(mx)
    zig = [(bx0, by0), (mx - 6, my - 3), (mx - 2, my + 9), (mx + 2, my - 9), (mx + 6, my + 3),
           (bx1, by1)]
    msp.add_lwpolyline([(x + ox, y + oy) for x, y in zig], dxfattribs={"layer": "TREPPE_LAUFLINIE"})
    # Lauflinie mit Antrittskreis und Pfeil
    ax, a0, tip = st["arrow_x"], st["arrow_y0"], st["arrow_tip"]
    msp.add_circle((ax + ox, a0 + oy), 4.5, dxfattribs={"layer": "TREPPE_LAUFLINIE"})
    msp.add_line((ax + ox, a0 + 4.5 + oy), (ax + ox, tip - 22 + oy),
                 dxfattribs={"layer": "TREPPE_LAUFLINIE"})
    h = msp.add_hatch(dxfattribs={"layer": "TREPPE_LAUFLINIE"})
    h.set_solid_fill(color=7)
    h.paths.add_polyline_path([(ax - 8 + ox, tip - 24 + oy), (ax + 8 + ox, tip - 24 + oy),
                               (ax + ox, tip + oy)], is_closed=True)

    # ---- gestrichelte Linien der Vorlage (EG: vermutl. Kellerumriss)
    for pl in fl.dashed:
        msp.add_lwpolyline([(x + ox, y + oy) for x, y in pl],
                           dxfattribs={"layer": "KELLER_VERMUTET", "ltscale": LT_KELLER})
    for pl in fl.extra_lines:
        msp.add_lwpolyline([(x + ox, y + oy) for x, y in pl],
                           dxfattribs={"layer": "LINIE_AUSSEN_VORLAGE"})

    # ---- Eingangspfeil
    if fl.entrance:
        ex, e0, e1 = fl.entrance
        msp.add_line((ex + ox, e0 + oy), (ex + ox, e1 - 20 + oy), dxfattribs={"layer": "SYMBOLE"})
        h = msp.add_hatch(dxfattribs={"layer": "SYMBOLE"})
        h.set_solid_fill(color=7)
        h.paths.add_polyline_path([(ex - 10 + ox, e1 - 24 + oy), (ex + 10 + ox, e1 - 24 + oy),
                                   (ex + ox, e1 + oy)], is_closed=True)

    # ---- Räume: Fläche (lichte Maße, ohne Tür-/Fensternischen)
    solid = unary_union([wall_all, *chim_polys])
    inner = fl.outline.difference(solid)
    areas = []
    for nr, seed, (tx, ty) in fl.rooms:
        part = inner.intersection(seed)
        polys = sorted(_polys(part), key=lambda p: -p.area)
        a = sum(p.area for p in polys if p.area > 2000) / 1e4
        areas.append((nr, a))
        text(msp, nr, tx, ty + 7, 3.0 * MM, "RAUMSTEMPEL", off, style="PLAN_FETT")
        text(msp, f"{a:.2f} m²".replace(".", ","), tx, ty - 9, 2.2 * MM, "RAUMSTEMPEL", off)
    # ---- handschriftliche "1" der Vorlage
    for mx1, my1 in fl.marks_1:
        text(msp, "1", mx1, my1, 5.0 * MM, "MARKIERUNG_1_VORLAGE", off, style="HAND", rgb=BLUE)
    # ---- Maßketten
    for ch in fl.chains:
        draw_chain(msp, ch, off)
    return areas


# ---------------------------------------------------------------- Planrahmen
def legend_symbol(msp, kind, x, y, off):
    ox, oy = off
    L = 9 * MM   # Symbolbreite 9 mm
    if kind == "wand":
        p = box(x, y - 1.2 * MM, x + L, y + 1.2 * MM)
        add_poly_fill(msp, p, "WAND_FUELLUNG", GRAY_WALL, off)
        add_poly_outline(msp, p, "WAND", off)
    elif kind == "fenster":
        p1 = box(x, y - 1.2 * MM, x + 2 * MM, y + 1.2 * MM)
        p2 = box(x + L - 2 * MM, y - 1.2 * MM, x + L, y + 1.2 * MM)
        for p in (p1, p2):
            add_poly_fill(msp, p, "WAND_FUELLUNG", GRAY_WALL, off)
            add_poly_outline(msp, p, "WAND", off)
        for yy in (y - 1.2 * MM, y + 1.2 * MM, y - 0.5 * MM, y + 0.5 * MM):
            msp.add_line((x + 2 * MM + ox, yy + oy), (x + L - 2 * MM + ox, yy + oy),
                         dxfattribs={"layer": "FENSTER"})
    elif kind == "oeffnung":
        p1 = box(x, y - 1.2 * MM, x + 2.5 * MM, y + 1.2 * MM)
        p2 = box(x + L - 2.5 * MM, y - 1.2 * MM, x + L, y + 1.2 * MM)
        for p in (p1, p2):
            add_poly_fill(msp, p, "WAND_FUELLUNG", GRAY_WALL, off)
            add_poly_outline(msp, p, "WAND", off)
    elif kind == "schornstein":
        p = box(x + 2 * MM, y - 2 * MM, x + 6 * MM, y + 2 * MM)
        q = box(x + 2.8 * MM, y - 1.2 * MM, x + 5.2 * MM, y + 1.2 * MM)
        add_poly_fill(msp, p.difference(q), "SCHORNSTEIN", GRAY_CHIM, off, pattern="ANSI31", pscale=2.2)
        add_poly_outline(msp, p, "SCHORNSTEIN", off)
        add_poly_outline(msp, q, "SCHORNSTEIN", off)
        h = msp.add_hatch(dxfattribs={"layer": "SCHORNSTEIN"})
        h.set_solid_fill(color=7)
        h.paths.add_polyline_path([(x + 2.8 * MM + ox, y - 1.2 * MM + oy),
                                   (x + 5.2 * MM + ox, y + 1.2 * MM + oy),
                                   (x + 2.8 * MM + ox, y + 1.2 * MM + oy)], is_closed=True)
    elif kind == "keller":
        msp.add_line((x + ox, y + oy), (x + L + ox, y + oy),
                     dxfattribs={"layer": "KELLER_VERMUTET", "ltscale": LT_KELLER})
    elif kind == "zusatzlinie":
        msp.add_line((x + ox, y + oy), (x + L + ox, y + oy), dxfattribs={"layer": "LINIE_AUSSEN_VORLAGE"})
    elif kind == "eins":
        text(msp, "1", x + L / 2, y, 4 * MM, "MARKIERUNG_1_VORLAGE", off, style="HAND", rgb=BLUE)
    elif kind == "stern":
        text(msp, "328*", x + L / 2, y, 2.5 * MM, "BEMASSUNG", off)
    elif kind == "ca":
        text(msp, "ca. 89", x + L / 2, y, 2.5 * MM, "BEMASSUNG", off)


def draw_sheet(msp, fl: Floor, areas, sheet_origin, off, page_no, n_pages):
    """A3-Rahmen mit Legende, Raumliste und Plankopf (alles im Modellbereich, 1:50)."""
    sx, sy = sheet_origin
    z = (0.0, 0.0)

    def P(xmm, ymm):
        return sx + xmm * MM, sy + ymm * MM

    def T(s, xmm, ymm, hmm, style="PLAN", align=TextEntityAlignment.LEFT, layer="PLANKOPF", rgb=None,
          maxw=None):
        x, y = P(xmm, ymm)
        if maxw is None:
            maxw = (SHEET_W - 11.5 - xmm) if align == TextEntityAlignment.LEFT else 999
        w = text_width(s, hmm, bold=(style == "PLAN_FETT"))
        if w > maxw:
            hmm = hmm * maxw / w
        text(msp, s, x, y, hmm * MM, layer, z, align=align, style=style, rgb=rgb)

    def R(x0, y0, x1, y1, layer="PLANKOPF"):
        a, b = P(x0, y0)
        cc, d = P(x1, y1)
        msp.add_lwpolyline([(a, b), (cc, b), (cc, d), (a, d)], close=True, dxfattribs={"layer": layer})

    def Lh(x0, x1, y, layer="PLANKOPF_DUENN"):
        a, b = P(x0, y)
        cc, _ = P(x1, y)
        msp.add_line((a, b), (cc, b), dxfattribs={"layer": layer})

    R(0, 0, SHEET_W, SHEET_H, "PLANKOPF_DUENN")          # Blattkante
    R(20, 10, SHEET_W - 10, SHEET_H - 10)                 # Zeichenrahmen
    px0 = SHEET_W - 10 - 72                               # rechte Spalte
    a, b = P(px0, 10)
    cc, d = P(px0, SHEET_H - 10)
    msp.add_line((a, b), (cc, d), dxfattribs={"layer": "PLANKOPF"})
    x = px0 + 4
    y = SHEET_H - 10 - 9
    T("FACHWERKHAUS – BESTAND", x, y, 3.0, style="PLAN_FETT")
    y -= 7
    T(fl.title, x, y, 2.6)
    y -= 5
    T("digitalisiert nach handbemaßtem Bestandsplan", x, y, 1.8)
    y -= 4
    Lh(px0, SHEET_W - 10, y)
    y -= 6
    T("LEGENDE", x, y, 2.2, style="PLAN_FETT")
    items = [("wand", "Wand Bestand (geschnitten)"),
             ("fenster", "Fenster"),
             ("oeffnung", "Tür/Öffnung (Anschlag lt. Vorlage offen)"),
             ("schornstein", "Schornstein mit Zug")]
    if "keller" in fl.legend_extra:
        items.append(("keller", "gestrichelt lt. Vorlage (vermutl. Kellerumriss)"))
    if "zusatzlinie" in fl.legend_extra:
        items.append(("zusatzlinie", "Zusatzlinie außen lt. Vorlage (Sockel?)"))
    items += [("eins", "handschriftl. Markierung „1“ der Vorlage"),
              ("stern", "Maß weicht vom Originaleintrag ab"),
              ("ca", "unbemaßt, aus Foto abgegriffen (±10 cm)")]
    for kind, label in items:
        y -= 6.2
        sx0, sy0 = P(x, y + 0.9)
        legend_symbol(msp, kind, sx0, sy0, z)
        T(label, x + 12, y, 1.8)
    y -= 5
    Lh(px0, SHEET_W - 10, y)
    y -= 6
    T("RAUMLISTE", x, y, 2.2, style="PLAN_FETT")
    T("lichte Fläche, ohne Tür-/Fensternischen", x + 22, y, 1.6)
    tot = 0.0
    for nr, a_ in areas:
        y -= 4.6
        T(f"Raum {nr}", x + 2, y, 1.9)
        T(f"{a_:.2f} m²".replace(".", ","), x + 60, y, 1.9, align=TextEntityAlignment.RIGHT)
        tot += a_
    y -= 2
    Lh(x + 2, x + 60, y)
    y -= 4.6
    T("Summe", x + 2, y, 1.9, style="PLAN_FETT")
    T(f"{tot:.2f} m²".replace(".", ","), x + 60, y, 1.9, style="PLAN_FETT",
      align=TextEntityAlignment.RIGHT)
    y -= 5
    Lh(px0, SHEET_W - 10, y)
    y -= 6
    T("HINWEISE", x, y, 2.2, style="PLAN_FETT")
    notes = [
        "Alle Maße in cm, Rohbau/Bestand lt. Vorlage.",
        "Eingetragene Maße der Vorlage sind maßgebend;",
        "Wände teils schief, wo Ketten oben/unten abweichen.",
        "* und ca.-Werte: siehe Prüfliste (ab Blatt 3).",
        "Vor Planung und Ausführung örtliches Aufmaß",
        "erforderlich (Fachwerk: Lot/Flucht prüfen).",
    ]
    for n_ in notes:
        y -= 4.2
        T(n_, x, y, 1.8)
    # Plankopf unten
    R(px0, 10, SHEET_W - 10, 46)
    rows = [("Projekt", "Fachwerkhaus – Ausbau"),
            ("Planinhalt", fl.subtitle + " – Bestand"),
            ("Maßstab", "1:50 (A3)      Einheit: cm"),
            ("Grundlage", "Bestandsplan (Handzeichnung, Foto)"),
            ("Stand", f"{DATUM}   Blatt {page_no}/{n_pages}")]
    yy = 46
    for k_, v_ in rows:
        yy -= 7.2
        Lh(px0, SHEET_W - 10, yy)
        T(k_, px0 + 2, yy + 2.3, 1.5)
        T(v_, px0 + 17, yy + 2.3, 1.9)
    # Nordpfeil fehlt in der Vorlage
    T("Nordrichtung in der Vorlage nicht angegeben", 24, 13, 2.0, layer="HINWEIS_PRUEFEN", rgb=RED)


# ============================================================ PRÜFLISTE
PRUEFLISTE = [
    ("Allgemein", [
        "Digitalisiert aus 2 Fotos (EG, 1. Stock). Fotos perspektivisch entzerrt; die Maßzahlen der Vorlage "
        "sind maßgebend, die Zeichnung selbst ist ca. ±10 cm ungenau gezeichnet.",
        "Ursprung je Geschoss: Außenecke unten links. EG und OG haben verschiedene Außenmaße "
        "(EG 1186/1191 × 813, OG 1190 × 708). Ob die Unterkanten übereinanderliegen, ist in der Vorlage "
        "nicht angegeben. Die Treppenlage spricht dafür (EG-Treppe endet bei y = 432, OG-Treppenraum bei y = 434); "
        "die Schornsteine liegen dann aber nicht deckungsgleich (EG y ≈ 383–533, OG y ≈ 261–407). Vor Ort prüfen.",
        "Handschriftliche blaue „1“ aus der Vorlage übernommen (Layer MARKIERUNG_1_VORLAGE), Bedeutung unbekannt.",
    ]),
    ("Erdgeschoss", [
        "Gesamtbreite oben 1186, unten 1191 (beide Ketten geschlossen). Umgesetzt als leicht schiefe rechte "
        "Außenwand (5 cm auf 8,13 m).",
        "Innenwand zwischen 0.01/0.02 bzw. 0.05/0.06: oben 355–377, unten 363–385. Umgesetzt als durchgehend "
        "schiefe Wand (8 cm auf 8,13 m).",
        "Wand C: oben 22 dick (749–771), unten 28 dick (748–776); Übergang im Bereich der Querwand.",
        "Querwand: Mitte 432–459 (27, Kette links), rechts 429–451 (22, Kette rechts). Versatz liegt in Wand C.",
        "Kette oben: gelesen als 27|113|85|130 | 19|75|37 | 88|133 | 177|83|137. „37“ und „177“ sind schwer lesbar "
        "(könnten auch 39/197 sein), gewählt, weil nur so die Kette schließt.",
        "Unteres Mittelmaß 363 (zwischen 385 und 748) ist in der Vorlage nicht eingetragen; aus der Kette errechnet.",
        "Kette links 121|84|200|27|230|72|40: von oben 40|72 stimmen mit der Zeichnung; bis zur Querwand bleiben "
        "rechnerisch nur 220 statt 230 → gezeichnet 220*.",
        "Kette links 405|27|335 ergibt mit der Außenwand 816 statt 813. Oberes Teilmaß gezeichnet als 332*.",
        "Rechte Fensterkette: „128“ unten (nicht 108) und 177|86|77 oben, gewählt, weil nur so 813 schließt.",
        "Öffnung Außenwand links in Raum 0.01 (y ≈ 505–594): nur Hilfslinien, keine Maßzahl. Nur Brüstungslinien "
        "gezeichnet, Art (Fenster/Tür/zugemauert) unklar.",
        "Tür 0.03→0.04 (y ≈ 503–587) unbemaßt, aus Foto abgegriffen.",
        "Schornstein in 0.01 (ca. 54 × 49) unbemaßt; Schornstein bei 0.07 bemaßt (54 breit, 46 ab Querwand).",
        "Gestrichelte Doppellinie (ca. 32–38 breit) in 0.07/0.08: in der Vorlage ohne Erklärung, vermutlich "
        "Kellerumriss/Kellerwände unter dem EG. Lage aus Foto abgegriffen.",
        "Dünne Zusatzlinie ca. 8 cm außerhalb der Außenwand oben/rechts/unten (nicht links): unbemaßt, "
        "vermutlich Sockel oder Verkleidung.",
        "Haustür 95 breit: Anschlag innen, Band links; Türblatt im Original 45° geöffnet, hier 90° (Norm).",
        "Innentüren: in der Vorlage nur als Öffnung ohne Türblatt/Aufschlag gezeichnet, so übernommen.",
        "Treppe: 75 breit (Kette 75|78), Lauf 250 → 432, 15 Auftritte zu je ca. 12 cm gezeichnet (steile Treppe); "
        "Steigungsmaße sind in der Vorlage nicht angegeben.",
    ]),
    ("1. Obergeschoss", [
        "Umriss mit Rücksprung oben rechts: 91 tief (Kette rechts 91|617), Wand 742–759.",
        "Treppenhauswand links: oben 370–387, unten 365–382, umgesetzt als schiefe Wand (5 cm).",
        "Wand zwischen 1.01/1.02: Außenwand-Kette links (143|118|129|12) legt sie auf 407–419; die Kette der "
        "Treppenhauswand (…|52|12|253|…) ergäbe 405–417 → dort 255*/50* statt 253/52.",
        "Widerspruch am Podest: Kette 145|12|260|85|20|152 setzt das Wandstück über dem Podest auf 519–539, "
        "die Kette der Treppenhauswand (…|75|147) und die Zeichnung auf 544–564. Gewählt: 544–564 (Tür 75 "
        "bleibt erhalten), dadurch 127* statt 152 und Podesttiefe 110* statt 85.",
        "Kette oben innen 17|185|73|112|17 ist um 15 zu lang. Fenster wie gezeichnet 112 von Wand 742 gesetzt, "
        "damit 170* statt 185.",
        "Kette rechts 260|80|63|12|232 schließt um 15 nicht; Öffnung 1.04→1.08 nach Zeichnung 95* statt 80.",
        "Kette unten innen: gelesen als 17|155|47|8|12|11|47|81|17 (8 und 11 unter der Linie notiert); "
        "rechnerisch 80* statt 81.",
        "Kette rechts innen „35|57|100“ (Tür Flur→1.06): unterstes Maß als 75* gelesen, weil nur so die Kette "
        "bis zur Querwand schließt (Zeichnung ca. 75).",
        "Kette rechts: „12,40 / 5“ gelesen als …|124|40|5|12|107|… (schließt auf 617).",
        "Tür 1.07→1.08 (x ≈ 865–945) unbemaßt, aus Foto abgegriffen.",
        "Schornsteine im OG unbemaßt (ca. 54 × 46/48), aus Foto abgegriffen.",
        "Öffnung Außenwand links in 1.01 (70, y = 436–506): ohne Fensterzeichen in der Vorlage → als Öffnung gezeichnet.",
        "Fenster im OG sind in der Vorlage nur als schmale Rahmen an der Außenseite gezeichnet; hier Normsymbol.",
        "Treppe OG: 80 breit (Kette 80|10|65), Treppenraum 174 → 434, Abschluss unten 12 dick (so gezeichnet).",
    ]),
]


# ============================================================ RENDERN
def render_pdf_page(doc, bbox_min, page_w=SHEET_W, page_h=SHEET_H):
    msp = doc.modelspace()
    ctx = RenderContext(doc)
    backend = pymupdf.PyMuPdfBackend()
    cfg = Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE, min_lineweight=0.13,
                        background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR)
    Frontend(ctx, backend, config=cfg).draw_layout(msp, finalize=True)
    page = layout.Page(page_w, page_h, layout.Units.mm)
    settings = layout.Settings(fit_page=False, scale=10.0 / SCALE)
    x0, y0 = bbox_min
    rb = BoundingBox2d([(x0, y0), (x0 + page_w * MM, y0 + page_h * MM)])
    pdf = backend.get_pdf_bytes(page, settings=settings, render_box=rb)
    import pymupdf as fitz
    src = fitz.open("pdf", pdf)
    png = src[0].get_pixmap(dpi=150).tobytes("png")
    return pdf, png


def pruefliste_pdf(path_pdf, first_page=3, total=None):
    import pymupdf as fitz
    d = fitz.open()
    W, Hh = fitz.paper_size("a4")
    pg = d.new_page(width=W, height=Hh)
    y = 56
    font = fitz.Font("helv")
    fontb = fitz.Font("hebo")

    def put(s, size, bold=False, indent=0):
        nonlocal y, pg
        f = fontb if bold else font
        maxw = W - 2 * 56 - indent
        words = s.split(" ")
        line = ""
        lines = []
        for w in words:
            t = (line + " " + w).strip()
            if f.text_length(t, fontsize=size) > maxw:
                lines.append(line)
                line = w
            else:
                line = t
        lines.append(line)
        for ln in lines:
            if y > Hh - 56:
                pg = d.new_page(width=W, height=Hh)
                y = 56
            tw = fitz.TextWriter(pg.rect)
            tw.append((56 + indent, y), ln, font=f, fontsize=size)
            tw.write_text(pg)
            y += size * 1.35

    put("Fachwerkhaus – Bestandspläne EG / 1. OG", 15, True)
    y += 2
    put("Prüfliste: Lesarten, Annahmen und Widersprüche der Vorlage", 11)
    put(f"Stand {DATUM}. Maße in cm. Mit * markierte Maße weichen vom Originaleintrag ab; "
        "„ca.“-Werte sind unbemaßt und aus dem entzerrten Foto abgegriffen (±10 cm).", 9)
    y += 6
    for head, items in PRUEFLISTE:
        y += 4
        put(head, 11.5, True)
        y += 1
        for it in items:
            put("•", 9, indent=0)
            y -= 9 * 1.35
            put(it, 9, indent=12)
            y += 2
    n = len(d)
    for k, p in enumerate(d):
        tw = fitz.TextWriter(p.rect)
        tw.append((56, Hh - 30), f"Fachwerkhaus – Bestand EG/OG · Prüfliste · Blatt {first_page + k}/"
                  f"{total or first_page + n - 1}", font=font, fontsize=8)
        tw.write_text(p)
    d.save(path_pdf)
    return n


def main():
    os.makedirs(OUT, exist_ok=True)
    floors = [build_eg(), build_og()]
    import pymupdf as fitz
    book = fitz.open()
    combined = new_doc()
    cmsp = combined.modelspace()
    tmp = os.path.join(OUT, "_pruefliste.pdf")
    n_pages = 2 + pruefliste_pdf(tmp)
    all_areas = {}
    for i, fl in enumerate(floors):
        doc = new_doc()
        msp = doc.modelspace()
        areas = draw_floor(msp, fl)
        all_areas[fl.key] = areas
        # Blatt so legen, dass die Zeichnung links im Rahmen sitzt
        from ezdxf import bbox as _bb
        ext = _bb.extents(msp, fast=True)
        draw_w = ext.size.x
        draw_h = ext.size.y
        avail_w = (SHEET_W - 10 - 72 - 20) * MM
        sx = ext.extmin.x - 20 * MM - (avail_w - draw_w) / 2
        sy = ext.extmin.y - (SHEET_H * MM - draw_h) / 2
        draw_sheet(msp, fl, areas, (sx, sy), (0, 0), i + 1, n_pages)
        print(f"{fl.key}: Zeichnung {draw_w / MM:.0f} x {draw_h / MM:.0f} mm, verfügbar "
              f"{avail_w / MM:.0f} x {SHEET_H - 20} mm")
        dxf_path = os.path.join(OUT, f"{fl.key}_Bestand.dxf")
        doc.saveas(dxf_path)
        # Gesamt-DXF: OG unter das EG (gleiches x, Abstand 3 m)
        dy = 0 if fl.key == "EG" else -(813 + 1000)
        draw_floor(cmsp, fl, (0, dy))
        h_fl = fl.outline.bounds[3]
        text(cmsp, fl.title.upper(), 0, dy + h_fl + 330, 6 * MM, "PLANKOPF", (0, 0),
             align=TextEntityAlignment.LEFT, style="PLAN_FETT")
        # Rendern: Schrift auf metrisch gleiche Liberation-Fonts umstellen
        doc.styles.get("PLAN").dxf.font = "LiberationSans-Regular.ttf"
        doc.styles.get("PLAN_FETT").dxf.font = "LiberationSans-Bold.ttf"
        doc.styles.get("HAND").dxf.font = "LiberationSans-Italic.ttf"
        pdf, png = render_pdf_page(doc, (sx, sy))
        with open(os.path.join(OUT, f"{fl.key}_Bestand_1-50_A3.png"), "wb") as f:
            f.write(png)
        src = fitz.open("pdf", pdf)
        book.insert_pdf(src)
    combined.saveas(os.path.join(OUT, "Fachwerkhaus_Bestand_EG_OG.dxf"))
    pruefliste_pdf(tmp, first_page=3, total=n_pages)
    book.insert_pdf(fitz.open(tmp))
    os.remove(tmp)
    book.set_metadata({"title": "Fachwerkhaus – Bestandsgrundrisse EG/OG 1:50",
                       "subject": "Digitalisierter Bestandsplan", "creator": "grundriss.py"})
    book.save(os.path.join(OUT, "Fachwerkhaus_Bestand_1-50_A3.pdf"))
    for k, v in all_areas.items():
        print(k, ", ".join(f"{n}: {a:.2f}" for n, a in v), f"= {sum(a for _, a in v):.2f} m²")


if __name__ == "__main__":
    main()
