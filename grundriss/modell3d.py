#!/usr/bin/env python3
"""
3D-Modell Erdgeschoss aus den Grundrissdaten (grundriss.py) und den
Höhenannahmen (hoehen.py).

Ausgabe:
  plaene/EG_3D.glb        glTF-Binär (Windows 3D-Viewer, Blender, SketchUp, Browser)
  plaene/EG_3D.obj/.mtl   OBJ für ältere Programme
  plaene/EG_3D_info.json  Raumdaten für den Browser-Viewer
Einheit im Modell: Meter (glTF-Norm), y = oben.
"""
from __future__ import annotations

import json
import os

import numpy as np
import trimesh
from shapely.geometry import LineString, box
from shapely.ops import unary_union

import grundriss as G
import hoehen as Hh
from raeume import flaeche, geschoss

OUT = G.OUT

# Farben (RGBA 0-1)
MAT = {
    "Waende": ([0.93, 0.92, 0.89, 1.0], 0.95),
    "Boden": ([0.72, 0.58, 0.42, 1.0], 0.8),
    "Schornsteine": ([0.62, 0.38, 0.30, 1.0], 0.9),
    "Fenster": ([0.55, 0.75, 0.90, 0.35], 0.1),
    "Haustuer": ([0.40, 0.27, 0.17, 1.0], 0.7),
    "Treppe": ([0.60, 0.45, 0.30, 1.0], 0.75),
    "Kellerumriss": ([0.35, 0.35, 0.40, 1.0], 0.9),
}

# Z-oben (cm) -> glTF y-oben (m): (x, y, z) -> (x, z, -y)
TO_GLTF = np.array([[0.01, 0, 0, 0], [0, 0, 0.01, 0], [0, -0.01, 0, 0], [0, 0, 0, 1]], dtype=float)


def extrude(geom, z0, z1):
    meshes = []
    for p in G._polys(geom):
        p = p.buffer(0)
        if p.is_empty or p.area < 0.5 or z1 <= z0:
            continue
        for q in G._polys(p):
            m = trimesh.creation.extrude_polygon(q, height=z1 - z0)
            m.apply_translation([0, 0, z0])
            meshes.append(m)
    return meshes


def material(group):
    rgba, rough = MAT[group]
    return trimesh.visual.material.PBRMaterial(
        name=group, baseColorFactor=[int(c * 255) for c in rgba], metallicFactor=0.0,
        roughnessFactor=rough, alphaMode="BLEND" if rgba[3] < 1 else "OPAQUE", doubleSided=True)


def main():
    fl = G.build_eg()
    g = geschoss(fl)
    H = Hh.RAUMHOEHE
    parts = {k: [] for k in MAT}

    # Wände: in Höhenscheiben zerlegt, jede Scheibe ohne die Öffnungen, die sie schneiden
    zs = sorted({0, H, *[z for o in fl.openings for z in Hh.z_range(o.kind)]})
    for za, zb in zip(zs[:-1], zs[1:]):
        cuts = [o.cut() for o in fl.openings
                if Hh.z_range(o.kind)[0] <= za and Hh.z_range(o.kind)[1] >= zb]
        geom = g["walls"].difference(unary_union(cuts)) if cuts else g["walls"]
        parts["Waende"] += extrude(geom, za, zb)

    # Fußböden je Raum (2 cm), Schornsteine
    for nr, (poly, _) in g["rooms"].items():
        parts["Boden"] += extrude(poly, -2, 0)
    for c in g["chims"]:
        parts["Schornsteine"] += extrude(c, 0, H)

    # Fenster: Glasscheibe in Wandmitte
    for o in fl.openings:
        if o.kind not in ("fenster", "fenster_unklar"):
            continue
        z0, z1 = Hh.z_range(o.kind)
        mid = LineString(o.face_line(o.mid())).buffer(1.5, cap_style=2)
        parts["Fenster"] += extrude(mid, z0, z1)

    # Haustür: Türblatt 90° geöffnet (Band links, schlägt nach innen)
    ht = next(o for o in fl.openings if o.kind == "haustuer")
    w = ht.a1 - ht.a0
    inner_face = ht.f0(ht.a0)
    parts["Haustuer"] += extrude(box(ht.a0, inner_face, ht.a0 + 4, inner_face + w), 0, Hh.TUER_HOEHE)

    # Treppe: Blockstufen auf dem Lauf lt. Grundriss
    st = fl.stair
    n_auf = st["n"]
    rise = (H + Hh.DECKE) / Hh.TREPPE_STEIGUNGEN
    run = (st["y1"] - st["y0"]) / n_auf
    for k in range(n_auf):
        ya, yb = st["y0"] + k * run, st["y0"] + (k + 1) * run
        tread = box(330, ya, st["xr"], yb).difference(g["walls"])
        parts["Treppe"] += extrude(tread, 0, (k + 1) * rise)

    # Vermuteter Kellerumriss als flache Linien auf dem Boden
    for pl in fl.dashed:
        parts["Kellerumriss"] += extrude(LineString(pl).buffer(2.5, cap_style=2), 0, 0.4)

    scene = trimesh.Scene()
    allm = []
    for grp, ms in parts.items():
        if not ms:
            continue
        m = trimesh.util.concatenate(ms)
        m.merge_vertices()
        m.apply_transform(TO_GLTF)
        m.visual = trimesh.visual.TextureVisuals(material=material(grp))
        scene.add_geometry(m, node_name=grp, geom_name=grp)
        allm.append((grp, m))
    glb = os.path.join(OUT, "EG_3D.glb")
    scene.export(glb)
    obj, files = trimesh.exchange.obj.export_obj(scene, include_texture=True, return_texture=True,
                                                 mtl_name="EG_3D.mtl")
    with open(os.path.join(OUT, "EG_3D.obj"), "w") as f:
        f.write(obj)
    for name, data in files.items():
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(data)

    info = dict(
        hoehen=dict(raumhoehe=H, bruestung=Hh.FENSTER_BRUESTUNG, sturz=Hh.FENSTER_STURZ,
                    tuer=Hh.TUER_HOEHE, decke=Hh.DECKE),
        raeume=[dict(nr=nr, flaeche=round(flaeche(p), 2),
                     x=round(p.representative_point().x / 100, 3),
                     z=round(-p.representative_point().y / 100, 3),
                     bbox=[round(v / 100, 3) for v in p.bounds])
                for nr, (p, _) in g["rooms"].items()],
        groesse=[round(v / 100, 3) for v in fl.outline.bounds],
    )
    with open(os.path.join(OUT, "EG_3D_info.json"), "w") as f:
        json.dump(info, f, indent=1, ensure_ascii=False)
    # Browser-Viewer mit eingebettetem Modell
    import base64
    tpl = open(os.path.join(G.HERE, "viewer_template.html"), encoding="utf-8").read()
    html = (tpl.replace("__GLB__", base64.b64encode(open(glb, "rb").read()).decode())
               .replace("__INFO__", json.dumps(info, ensure_ascii=False))
               .replace("__H__", str(H)).replace("__BR__", str(Hh.FENSTER_BRUESTUNG))
               .replace("__ST__", str(Hh.FENSTER_STURZ)).replace("__T__", str(Hh.TUER_HOEHE)))
    with open(os.path.join(OUT, "EG_3D_Viewer.html"), "w", encoding="utf-8") as f:
        f.write(html)
    for grp, m in allm:
        print(f"{grp:14s} {len(m.faces):6d} Dreiecke, wasserdicht={m.is_watertight}")
    print("GLB", os.path.getsize(glb) // 1024, "KB")


if __name__ == "__main__":
    main()
