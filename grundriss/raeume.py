"""Gemeinsame Geometrie für 3D-Modell und Wandabwicklungen (aus grundriss.py)."""
from __future__ import annotations

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import grundriss as G


def geschoss(fl: G.Floor):
    """Wandmasse (ungeschnitten), Schornsteine, Innenraum und Räume eines Geschosses."""
    wall_all = unary_union(fl.walls).intersection(fl.outline)
    chims = [box(k.x0, k.y0, k.x1, k.y1).difference(wall_all) for k in fl.chimneys]
    chim_all = unary_union(chims)
    inner = fl.outline.difference(unary_union([wall_all, chim_all]))
    rooms = {}
    for nr, seed, pos in fl.rooms:
        polys = sorted(G._polys(inner.intersection(seed)), key=lambda p: -p.area)
        rooms[nr] = (polys[0], pos)
    return dict(walls=wall_all, chims=chims, chim_all=chim_all, inner=inner, rooms=rooms)


def flaeche(poly: Polygon) -> float:
    return poly.area / 1e4
