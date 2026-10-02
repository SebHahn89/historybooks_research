#!/usr/bin/env python3
"""
Wandabwicklungen aller Räume im Erdgeschoss (Blick jeweils von innen).

Grundlage: Grundrissdaten aus grundriss.py, Höhen aus hoehen.py (Annahmen!).
Die Wände jedes Raums werden im Uhrzeigersinn abgewickelt, beginnend mit der
oberen Wand (Planoben). Jede Wandfläche zeigt Fenster, Türen/Öffnungen,
Schornsteinflächen und offene Raumübergänge mit Maßketten.

Ausgabe:
  plaene/EG_Wandabwicklungen_1-50_A3.pdf   Übersicht + 1 Blatt je Raum (A3 quer, 1:50)
  plaene/EG_Wandabwicklungen.dxf           alle Blätter nebeneinander (Einheit cm)
"""
from __future__ import annotations

import math
import os

from ezdxf.enums import TextEntityAlignment
from shapely.geometry import LineString, Point, box
from shapely.geometry.polygon import orient

import grundriss as G
import hoehen as Hh
from raeume import flaeche, geschoss

MM = G.MM
G.DATUM = "02.10.2026"
LEFT = TextEntityAlignment.LEFT
RIGHT = TextEntityAlignment.RIGHT
CENTER = TextEntityAlignment.MIDDLE_CENTER
SEITE = {"oben": (0, 1), "rechts": (1, 0), "unten": (0, -1), "links": (-1, 0)}

ABW_LAYERS = {
    "ABW_WAND": (7, 35, "Continuous"),
    "ABW_BODEN": (7, 50, "Continuous"),
    "ABW_OFFEN": (8, 18, "DASHED"),
    "ABW_OEFFNUNG": (7, 25, "Continuous"),
    "ABW_TREPPE": (7, 25, "Continuous"),
    "ABW_TEXT": (7, 18, "Continuous"),
}


# ---------------------------------------------------------------- Analyse
def wandflaechen(fl, g, nr):
    """Wandflächen eines Raums im Uhrzeigersinn, Start: obere Wand ganz links."""
    poly = orient(g["rooms"][nr][0].simplify(0.4), sign=-1.0)       # im Uhrzeigersinn
    pts = list(poly.exterior.coords)[:-1]
    edges = []
    for i in range(len(pts)):
        p0, p1 = pts[i], pts[(i + 1) % len(pts)]
        L = math.dist(p0, p1)
        if L < 10:                      # Reste aus Wandanschlüssen/Raumgrenzen
            continue
        d = ((p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L)
        n = (-d[1], d[0])               # nach außen (links der Laufrichtung)
        m = ((p0[0] + p1[0]) / 2 + 3 * n[0], (p0[1] + p1[1]) / 2 + 3 * n[1])
        if g["chim_all"].buffer(0.5).contains(Point(m)):
            art = "schornstein"
        elif g["walls"].buffer(0.5).contains(Point(m)):
            art = "wand"
        else:
            art = "offen"
        seite = max(SEITE, key=lambda k: SEITE[k][0] * n[0] + SEITE[k][1] * n[1])
        seg = LineString([p0, p1])
        ops = []
        if art == "wand":
            for o in fl.openings:
                c = o.cut()
                if seg.distance(c) > 0.5:
                    continue
                part = c.intersection(seg.buffer(2.0))
                ts = [(x - p0[0]) * d[0] + (y - p0[1]) * d[1] for x, y in part.exterior.coords]
                t0, t1 = max(0.0, min(ts)), min(L, max(ts))
                if t1 - t0 > 5:
                    z0, z1 = Hh.z_range(o.kind)
                    ops.append(dict(kind=o.kind, t0=t0, t1=t1, z0=z0, z1=z1))
            ops.sort(key=lambda o: o["t0"])
        edges.append(dict(p0=p0, p1=p1, L=L, d=d, n=n, art=art, seite=seite, ops=ops))
    # Start: obere Wand, die am weitesten links beginnt
    top = [i for i, e in enumerate(edges) if e["seite"] == "oben"]
    s = min(top, key=lambda i: min(edges[i]["p0"][0], edges[i]["p1"][0])) if top else 0
    edges = edges[s:] + edges[:s]
    for k, e in enumerate(edges):
        e["id"] = chr(ord("A") + k)
        H = Hh.RAUMHOEHE
        e["brutto"] = e["L"] * H / 1e4
        e["oeff"] = sum((o["t1"] - o["t0"]) * (o["z1"] - o["z0"]) for o in e["ops"]) / 1e4
        e["netto"] = e["brutto"] - e["oeff"] if e["art"] == "wand" else 0.0
    return edges


def treppenprofil(fl, e):
    """Stufenlinie, wenn die Wandfläche seitlich an der Treppe liegt (Raum 0.06)."""
    st = fl.stair
    if abs(e["d"][0]) > 0.05:                      # nur Wände parallel zum Lauf (senkrecht im Plan)
        return None
    xm = (e["p0"][0] + e["p1"][0]) / 2
    if not (abs(xm - st["xr"]) < 3 or abs(xm - st["xl"]((st["y0"] + st["y1"]) / 2)) < 3):
        return None
    rise = (Hh.RAUMHOEHE + Hh.DECKE) / Hh.TREPPE_STEIGUNGEN
    run = (st["y1"] - st["y0"]) / st["n"]

    def t_of(y):
        return (xm - e["p0"][0]) * e["d"][0] + (y - e["p0"][1]) * e["d"][1]

    prof = [(t_of(st["y0"]), 0.0)]
    for k in range(st["n"]):
        z = (k + 1) * rise
        prof += [(t_of(st["y0"] + k * run), z), (t_of(st["y0"] + (k + 1) * run), z)]
    prof.append((t_of(st["y1"]), 0.0))
    return [(max(0, min(e["L"], t)), z) for t, z in prof]


# ---------------------------------------------------------------- Zeichnen
def zeichne_wand(msp, fl, e, ox, oy):
    H = Hh.RAUMHOEHE
    L = e["L"]
    off = (ox, oy)
    lay = "ABW_OFFEN" if e["art"] == "offen" else "ABW_WAND"
    rect = box(0, 0, L, H)
    if e["art"] == "schornstein":
        G.add_poly_fill(msp, rect, "SCHORNSTEIN", G.GRAY_CHIM, off, pattern="ANSI31", pscale=2.2)
    G.add_poly_outline(msp, rect, lay, off)
    msp.add_line((ox - 12, oy), (ox + L + 12, oy), dxfattribs={"layer": "ABW_BODEN"})
    for o in e["ops"]:
        r = box(o["t0"], o["z0"], o["t1"], o["z1"])
        G.add_poly_fill(msp, r, "ABW_OEFFNUNG", (255, 255, 255), off)
        G.add_poly_outline(msp, r, "ABW_OEFFNUNG", off)
        cx, cz = (o["t0"] + o["t1"]) / 2, (o["z0"] + o["z1"]) / 2
        if o["kind"] in ("fenster", "fenster_unklar"):
            inner = box(o["t0"] + 5, o["z0"] + 5, o["t1"] - 5, o["z1"] - 5)
            G.add_poly_outline(msp, inner, "FENSTER", off)
            lab = "Fenster?" if o["kind"] == "fenster_unklar" else "Fenster"
        else:
            lab = "Haustür" if o["kind"] == "haustuer" else "Tür"
        G.text(msp, lab, cx, cz, 2.0 * MM, "ABW_TEXT", off)
    if e["art"] == "offen":
        G.text(msp, "offen (Raumübergang)", L / 2, H / 2, 2.0 * MM, "ABW_TEXT", off,
               rot=90 if L < 120 else 0)
    if e["art"] == "schornstein":
        G.text(msp, "Schornstein", L / 2, H / 2, 2.0 * MM, "ABW_TEXT", off, rot=90 if L < 120 else 0)
    prof = treppenprofil(fl, e) if e["art"] == "wand" else None
    if prof:
        prof = [(t, min(z, H)) for t, z in prof]
        msp.add_lwpolyline([(t + ox, z + oy) for t, z in prof], dxfattribs={"layer": "ABW_TREPPE"})
        G.text(msp, "Treppe", sum(t for t, _ in prof) / len(prof), 40, 2.0 * MM, "ABW_TEXT", off)
    # Kopfzeile
    G.text(msp, f"{e['id']}", 0, H + 34, 3.5 * MM, "ABW_TEXT", off, align=LEFT, style="PLAN_FETT")
    l1, l2 = kopf(e)
    G.text(msp, l1, 4.5 * MM, H + 34, 2.2 * MM, "ABW_TEXT", off, align=LEFT)
    G.text(msp, l2, 0, H + 14, 2.0 * MM, "ABW_TEXT", off, align=LEFT)
    # Maßketten
    tpts = sorted({0.0, L, *[v for o in e["ops"] for v in (o["t0"], o["t1"])]})
    G.draw_chain(msp, G.Chain("x", tpts, -32, +1), off)
    if len(tpts) > 2:
        G.draw_chain(msp, G.Chain("x", [0.0, L], -65, +1), off)
    zpts = sorted({0, H, *[v for o in e["ops"] for v in (o["z0"], o["z1"])]})
    G.draw_chain(msp, G.Chain("y", zpts, L + 32, -1), off)


def kopf(e):
    l1 = {"wand": f"Wand {e['seite']}", "offen": f"offen, Seite {e['seite']}",
          "schornstein": f"Schornstein, Seite {e['seite']}"}[e["art"]]
    l2 = {"wand": f"netto {e['netto']:.2f} m²".replace(".", ","), "offen": "keine Wandfläche",
          "schornstein": f"{e['brutto']:.2f} m²".replace(".", ",")}[e["art"]]
    return l1, l2


def kopf_breite(e):
    l1, l2 = kopf(e)
    return max(4.5 * MM + G.text_width(l1, 2.2 * MM), G.text_width(l2, 2.0 * MM))


def layout(edges, width):
    """Wände zeilenweise anordnen; liefert [(edge, x, zeile)]."""
    out, x, row = [], 0.0, 0
    for e in edges:
        w = max(e["L"] + 85, kopf_breite(e) + 25)
        if x > 0 and x + max(e["L"] + 45, kopf_breite(e)) > width:
            x, row = 0.0, row + 1
        out.append((e, x, row))
        x += w
    return out, row + 1


def schluesselplan(msp, fl, g, nr, edges, x0, y0, k=0.25):
    """Kleiner Grundriss 1:200 mit markiertem Raum und Wandbuchstaben."""
    from shapely import affinity
    T = lambda geom: affinity.translate(affinity.scale(geom, k, k, origin=(0, 0)), x0, y0)
    G.add_poly_fill(msp, T(fl.outline), "WAND_FUELLUNG", (160, 160, 160), (0, 0))
    for r_nr, (r_poly, _) in g["rooms"].items():
        q = T(r_poly)
        G.add_poly_fill(msp, q, "WAND_FUELLUNG", (240, 200, 190) if r_nr == nr else (255, 255, 255), (0, 0))
        G.add_poly_outline(msp, q, "PLANKOPF_DUENN", (0, 0))
    G.add_poly_outline(msp, T(fl.outline), "PLANKOPF_DUENN", (0, 0))
    for e in edges:
        mx = (e["p0"][0] + e["p1"][0]) / 2 - 16 * e["n"][0]
        my = (e["p0"][1] + e["p1"][1]) / 2 - 16 * e["n"][1]
        G.text(msp, e["id"], x0 + mx * k, y0 + my * k, 2.0 * MM, "PLANKOPF", (0, 0), style="PLAN_FETT",
               rgb=G.RED)


def blatt(msp, fl, g, nr, edges, sx, sy, page_no, n_pages):
    def P(xmm, ymm):
        return sx + xmm * MM, sy + ymm * MM

    def T(s, xmm, ymm, hmm, style="PLAN", align=LEFT):
        x, y = P(xmm, ymm)
        G.text(msp, s, x, y, hmm * MM, "PLANKOPF", (0, 0), align=align, style=style)

    def R(x0, y0, x1, y1, layer="PLANKOPF"):
        a, b = P(x0, y0)
        c, d = P(x1, y1)
        msp.add_lwpolyline([(a, b), (c, b), (c, d), (a, d)], close=True, dxfattribs={"layer": layer})

    def Lh(x0, x1, y):
        a, b = P(x0, y)
        c, _ = P(x1, y)
        msp.add_line((a, b), (c, b), dxfattribs={"layer": "PLANKOPF_DUENN"})

    W, Hs = G.SHEET_W, G.SHEET_H
    R(0, 0, W, Hs, "PLANKOPF_DUENN")
    R(20, 10, W - 10, Hs - 10)
    px0 = W - 10 - 72
    a, b = P(px0, 10)
    c, d = P(px0, Hs - 10)
    msp.add_line((a, b), (c, d), dxfattribs={"layer": "PLANKOPF"})
    x = px0 + 4
    y = Hs - 19
    T("FACHWERKHAUS – BESTAND", x, y, 3.0, style="PLAN_FETT")
    y -= 7
    T(f"Wandabwicklung Raum {nr}", x, y, 2.6)
    y -= 5
    T("Erdgeschoss · Blick jeweils von innen", x, y, 1.8)
    y -= 4
    Lh(px0, W - 10, y)
    # Schlüsselplan
    y -= 4
    kx, ky = P(x + 2, y - 44)
    schluesselplan(msp, fl, g, nr, edges, kx, ky)
    y -= 48
    T("Lageplan 1:200, Wandbuchstaben rot", x, y, 1.6)
    y -= 4
    Lh(px0, W - 10, y)
    # Tabelle
    y -= 6
    T("WANDFLÄCHEN", x, y, 2.2, style="PLAN_FETT")
    y -= 5
    for col, txt_, al in ((x + 1, "Wand", LEFT), (x + 30, "Länge", RIGHT), (x + 46, "Öffn.", RIGHT),
                          (x + 64, "netto", RIGHT)):
        T(txt_, col, y, 1.6, align=al)
    y -= 1.5
    Lh(x, x + 65, y)
    sum_n = sum_o = 0.0
    for e in edges:
        y -= 4.0
        art = {"wand": e["seite"], "offen": "offen", "schornstein": "Schornstein"}[e["art"]]
        T(f"{e['id']}  {art}", x + 1, y, 1.7)
        T(f"{e['L']:.0f} cm", x + 30, y, 1.7, align=RIGHT)
        if e["art"] == "wand":
            T(f"{e['oeff']:.2f}".replace(".", ","), x + 46, y, 1.7, align=RIGHT)
            T(f"{e['netto']:.2f} m²".replace(".", ","), x + 64, y, 1.7, align=RIGHT)
            sum_n += e["netto"]
            sum_o += e["oeff"]
        elif e["art"] == "schornstein":
            T(f"{e['brutto']:.2f} m²".replace(".", ","), x + 64, y, 1.7, align=RIGHT)
    y -= 1.5
    Lh(x, x + 65, y)
    y -= 4.2
    T("Summe Wand netto", x + 1, y, 1.8, style="PLAN_FETT")
    T(f"{sum_n:.2f} m²".replace(".", ","), x + 64, y, 1.8, style="PLAN_FETT", align=RIGHT)
    room = g["rooms"][nr][0]
    y -= 6
    for k_, v_ in (("Grundfläche = Deckenfläche", f"{flaeche(room):.2f} m²"),
                   ("Umfang", f"{room.exterior.length / 100:.2f} m".replace(".", ",")),
                   ("Raumhöhe (gemessen)", f"{Hh.RAUMHOEHE} cm")):
        T(k_, x + 1, y, 1.7)
        T(v_.replace(".", ","), x + 64, y, 1.7, align=RIGHT)
        y -= 4
    y -= 2
    Lh(px0, W - 10, y)
    y -= 5
    T("HINWEISE", x, y, 2.0, style="PLAN_FETT")
    for n_ in ("Längen aus dem Grundriss (lichte Maße).",
               f"Raumhöhe {Hh.RAUMHOEHE} cm gemessen. Angenommen:",
               f"Brüstung {Hh.FENSTER_BRUESTUNG}, Sturz {Hh.FENSTER_STURZ}, Türen {Hh.TUER_HOEHE} cm.",
               "Netto = Wandfläche ohne Öffnungen,",
               "Schornsteinseiten getrennt ausgewiesen."):
        y -= 3.8
        T(n_, x, y, 1.65)
    R(px0, 10, W - 10, 39)
    yy = 39
    for k_, v_ in (("Projekt", "Fachwerkhaus – Ausbau"), ("Planinhalt", f"Wandabwicklung Raum {nr} (EG)"),
                   ("Maßstab", "1:50 (A3)      Einheit: cm"), ("Stand", f"{G.DATUM}   Blatt {page_no}/{n_pages}")):
        yy -= 7.2
        Lh(px0, W - 10, yy)
        T(k_, px0 + 2, yy + 2.3, 1.5)
        T(v_, px0 + 17, yy + 2.3, 1.9)
    return P(20, 10), P(px0, Hs - 10)


def uebersicht_pdf(path, daten):
    import pymupdf as fitz
    d = fitz.open()
    W, Hh_ = fitz.paper_size("a4")
    pg = d.new_page(width=W, height=Hh_)
    f, fb = fitz.Font("helv"), fitz.Font("hebo")

    def put(x, y, s, size=9.5, bold=False, right=False):
        font = fb if bold else f
        if right:
            x -= font.text_length(s, fontsize=size)
        tw = fitz.TextWriter(pg.rect)
        tw.append((x, y), s, font=font, fontsize=size)
        tw.write_text(pg)

    y = 60
    put(56, y, "Fachwerkhaus – Wandabwicklungen Erdgeschoss", 15, True)
    y += 20
    put(56, y, f"Übersicht Wandflächen je Raum · Stand {G.DATUM} · Blatt 1/{len(daten) + 1}", 10)
    y += 14
    put(56, y, f"Raumhöhe {Hh.RAUMHOEHE} cm (gemessen). Angenommen: Brüstung {Hh.FENSTER_BRUESTUNG}, "
               f"Sturz {Hh.FENSTER_STURZ}, Türen {Hh.TUER_HOEHE} cm. Längen aus dem Grundriss.", 8.5)
    y += 26
    cols = [(56, "Raum", False), (165, "Grundfläche", True), (240, "Umfang", True), (320, "Wand brutto", True),
            (395, "Öffnungen", True), (470, "Wand netto", True), (540, "Wandflächen", True)]
    for x, s, r in cols:
        put(x, y, s, 9, True, r)
    y += 5
    pg.draw_line((56, y), (540, y), width=0.6)
    tot = [0.0] * 5
    for nr, room, edges in daten:
        y += 16
        br = sum(e["brutto"] for e in edges if e["art"] == "wand")
        oe = sum(e["oeff"] for e in edges if e["art"] == "wand")
        ne = sum(e["netto"] for e in edges)
        vals = [flaeche(room), room.exterior.length / 100, br, oe, ne]
        tot = [a + b for a, b in zip(tot, vals)]
        put(56, y, f"Raum {nr}")
        for (x, _, _), v, u in zip(cols[1:6], vals, ("m²", "m", "m²", "m²", "m²")):
            put(x, y, f"{v:.2f} {u}".replace(".", ","), right=True)
        put(540, y, f"{sum(1 for e in edges if e['art'] == 'wand')}", right=True)
    y += 6
    pg.draw_line((56, y), (540, y), width=0.6)
    y += 14
    put(56, y, "Summe", bold=True)
    for (x, _, _), v, u in zip(cols[1:6], tot, ("m²", "m", "m²", "m²", "m²")):
        put(x, y, f"{v:.2f} {u}".replace(".", ","), bold=True, right=True)
    y += 34
    for line in ("Lesart: Jede Wand wird von innen betrachtet; Reihenfolge im Uhrzeigersinn ab der oberen Wand (Planoben).",
                 "„Öffnungen“ = Fenster + Türen in Wandflächen; offene Raumübergänge zählen nicht als Wand.",
                 "Schornsteinseiten sind auf den Raumblättern getrennt ausgewiesen und hier nicht in „Wand“ enthalten.",
                 "Treppe in Raum 0.06: Stufenlinie auf den seitlichen Wänden eingezeichnet.",
                 "Für Material (Putz, Dämmung, Farbe) Wand netto verwenden; Laibungen sind nicht enthalten."):
        put(56, y, line, 8.5)
        y += 13
    d.save(path)


def main():
    import pymupdf as fitz
    fl = G.build_eg()
    g = geschoss(fl)
    doc = G.new_doc()
    for name, (col, lw, lt) in ABW_LAYERS.items():
        doc.layers.add(name, color=col, lineweight=lw, linetype=lt)
    msp = doc.modelspace()
    nrs = [nr for nr, _, _ in fl.rooms]
    n_pages = len(nrs) + 1
    sheets, daten = [], []
    for i, nr in enumerate(nrs):
        edges = wandflaechen(fl, g, nr)
        daten.append((nr, g["rooms"][nr][0], edges))
        sx, sy = i * 2300.0, 0.0
        (ax, ay), (bx, by) = blatt(msp, fl, g, nr, edges, sx, sy, i + 2, n_pages)
        width = (bx - ax) - 2 * 10 * MM
        placed, rows = layout(edges, width)
        row_h = Hh.RAUMHOEHE + 150
        total_h = rows * row_h
        top = by - ((by - ay) - total_h) / 2 - 45
        widest = max(x + e["L"] + 45 for e, x, _ in placed)
        left = ax + ((bx - ax) - widest) / 2
        for e, x, row in placed:
            zeichne_wand(msp, fl, e, left + x, top - (row + 1) * row_h + 95)
        sheets.append((sx, sy))
        print(f"{nr}: {len(edges)} Flächen, {rows} Zeile(n): "
              + " ".join(f"{e['id']}={e['art'][0]}{e['L']:.0f}({len(e['ops'])})" for e in edges))
    doc.saveas(os.path.join(G.OUT, "EG_Wandabwicklungen.dxf"))
    doc.styles.get("PLAN").dxf.font = "LiberationSans-Regular.ttf"
    doc.styles.get("PLAN_FETT").dxf.font = "LiberationSans-Bold.ttf"
    doc.styles.get("HAND").dxf.font = "LiberationSans-Italic.ttf"
    book = fitz.open()
    tmp = os.path.join(G.OUT, "_uebersicht.pdf")
    uebersicht_pdf(tmp, daten)
    book.insert_pdf(fitz.open(tmp))
    os.remove(tmp)
    for i, (sx, sy) in enumerate(sheets):
        pdf, png = G.render_pdf_page(doc, (sx, sy))
        book.insert_pdf(fitz.open("pdf", pdf))
        if nrs[i] in ("0.05", "0.06"):
            with open(os.path.join(G.OUT, f"EG_Wandabwicklung_{nrs[i]}.png"), "wb") as f:
                f.write(png)
    book.set_metadata({"title": "Fachwerkhaus – Wandabwicklungen EG 1:50", "creator": "abwicklung.py"})
    book.save(os.path.join(G.OUT, "EG_Wandabwicklungen_1-50_A3.pdf"))


if __name__ == "__main__":
    main()
