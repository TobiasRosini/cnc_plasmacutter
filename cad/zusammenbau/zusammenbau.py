# -*- coding: utf-8 -*-
"""
Zusammenbau des Plasmatisches aus den Einzelteil-Dokumenten.

Die Teile werden als Verknüpfungen (App::Link) eingebunden, nicht kopiert:
Ändert sich ein Einzelteil, zieht der Zusammenbau automatisch nach.
Lage und Maße werden aus der Geometrie der Einzelteile abgeleitet
(Schienen im Rahmen, Schiene/Brücke im Portalwinkel-Dokument).

Neu in diesem Dokument erzeugt: Portalbrücke 20x40x4 in voller Länge.

Koordinaten wie Grundrahmen: Ursprung = Außenecke am Boden, X quer, Y längs.

Aufruf:
  python3 cad/live.py cad/zusammenbau/zusammenbau.py
"""
import os
import sys
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(OUT)
sys.path.insert(0, CAD)
import fc_dok  # noqa: E402

P = dict(
    portal_y=None,              # Mitte Portal in Y; None = Rahmenmitte
    wanne_ok_unter_rahmen=60.0,  # OK Wanne unter OK Rahmen (Wannenträger folgt)
    bruecke_wand=4.0,
    max_breite=800.0,
)

RAHMEN = os.path.join(CAD, "grundrahmen", "grundrahmen.FCStd")
WANNE = os.path.join(CAD, "wanne", "wanne.FCStd")
WINKEL = os.path.join(CAD, "y_portalwinkel", "y_portalwinkel.FCStd")

# aus den Einzelteilen übernommen
RAHMEN_TEILE_AUS = {"Dummy_Wanne"}
WINKEL_TEILE = ["Flachstange_40x15", "winkel_druckteil", "spannschlitten",
                "klemmplatte_fest", "klemmplatte_schlitten", "Wagen_HGH15CA"]


def gruppe(doc, name):
    g = fc_dok.objekt(doc, "App::DocumentObjectGroup", name)
    return g


def link(doc, name, ziel, placement, grp):
    o = fc_dok.objekt(doc, "App::Link", name)
    o.setLink(ziel)
    o.LinkPlacement = placement
    if o not in grp.Group:
        grp.addObject(o)
    return o


def bbox(shape):
    bb = App.BoundBox()
    for pt in shape.tessellate(1.0)[0]:
        bb.add(pt)
    return bb


def main():
    dr = fc_dok.quelle(RAHMEN)
    dw = fc_dok.quelle(WANNE)
    dp = fc_dok.quelle(WINKEL)
    pfad = os.path.join(OUT, "zusammenbau.FCStd")
    doc, offen = fc_dok.dokument(pfad)

    # --- Bezugsmaße aus den Einzelteilen
    schienen = dr.getObject("Dummy_Schienen_HGR15").Shape.Solids
    sx = sorted((s.BoundBox.Center.x for s in schienen))
    s_bb = schienen[0].BoundBox
    z_schiene_rahmen = s_bb.ZMin
    rahmen_bb = App.BoundBox()
    for o in dr.Objects:
        if o.Name not in RAHMEN_TEILE_AUS and o.Name != "Dummy_Schienen_HGR15":
            rahmen_bb.add(o.Shape.BoundBox)
    w_schiene = dp.getObject("Schiene_HGR15").Shape.BoundBox
    w_bruecke = dp.getObject("Bruecke_20x40x4").Shape.BoundBox
    w_flach = dp.getObject("Flachstange_40x15").Shape.BoundBox
    dz = z_schiene_rahmen - w_schiene.ZMin
    py = P["portal_y"] if P["portal_y"] is not None else rahmen_bb.Center.y

    # --- Rahmen + Schienen
    g_r = gruppe(doc, "Rahmen")
    for o in dr.Objects:
        if o.Name in RAHMEN_TEILE_AUS:
            continue
        link(doc, "R_" + o.Name, o, App.Placement(), g_r)

    # --- Wanne, mittig im Rahmen
    g_w = gruppe(doc, "Wanne")
    wobj = dw.getObject("Wanne")
    wh = bbox(wobj.Shape).ZLength
    zw = rahmen_bb.ZMax - P["wanne_ok_unter_rahmen"] - wh
    link(doc, "W_Wanne", wobj,
         App.Placement(V(rahmen_bb.Center.x, rahmen_bb.Center.y, zw), App.Rotation()), g_w)

    # --- Portal: rechts wie modelliert (+X außen), links um 180° gedreht
    g_p = gruppe(doc, "Portal")
    seiten = {"rechts": (sx[1], App.Rotation()),
              "links": (sx[0], App.Rotation(V(0, 0, 1), 180))}
    for seite, (x, rot) in seiten.items():
        pl = App.Placement(V(x, py, dz), rot)
        for n in WINKEL_TEILE:
            link(doc, "P_%s_%s" % (seite, n), dp.getObject(n), pl, g_p)

    # Brücke über die volle Breite: Außenkante Sattel links bis rechts
    halb = w_bruecke.XMax          # Brückenende = Sattelaußenkante ab Schienenmitte
    x0, x1 = sx[0] - halb, sx[1] + halb
    y0, y1 = py + w_bruecke.YMin, py + w_bruecke.YMax
    z0, z1 = dz + w_bruecke.ZMin, dz + w_bruecke.ZMax
    t = P["bruecke_wand"]
    br = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
    br = br.cut(Part.makeBox(x1 - x0 + 2, y1 - y0 - 2 * t, z1 - z0 - 2 * t,
                             V(x0 - 1, y0 + t, z0 + t)))
    b = fc_dok.teil(doc, "Portalbruecke_20x40x4", br, "alu")
    if b not in g_p.Group:
        g_p.addObject(b)

    fc_dok.speichern(doc, pfad, offen)

    # --- Prüfung
    def form(prefix):
        return [o for o in doc.Objects if o.Name.startswith(prefix)
                and o.TypeId == "App::Link"]

    rahmen = Part.makeCompound([o.Shape for o in form("R_")
                                if "Schienen" not in o.Name])
    portal = [o for o in form("P_")] + [b]
    wanne = doc.getObject("W_Wanne").Shape
    alle = Part.makeCompound([o.Shape for o in doc.Objects
                              if o.TypeId in ("App::Link", "Part::Feature")])
    gb = bbox(alle)
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Gesamtmaß: %.0f (X) x %.0f (Y) x %.0f (Z) mm\n"
                % (gb.XLength, gb.YLength, gb.ZLength))
        f.write("Gesamtbreite %.0f mm, Grenze %.0f mm: %s\n"
                % (gb.XLength, P["max_breite"],
                   "ok" if gb.XLength <= P["max_breite"] else
                   "ZU BREIT um %.0f mm" % (gb.XLength - P["max_breite"])))
        f.write("Rahmen außen %.0f, Portal steht je Seite %.0f mm über\n"
                % (rahmen_bb.XLength, (gb.XLength - rahmen_bb.XLength) / 2))
        f.write("Portalbrücke: %.0f mm lang, OK %.0f mm über Boden\n" % (x1 - x0, z1))
        ls = s_bb.YLength
        f.write("Y-Hub (Schiene %.0f − Flachstange %.0f): %.0f mm, gefordert 1100\n"
                % (ls, w_flach.YLength, ls - w_flach.YLength))
        f.write("Wanne: Unterkante %.0f, Oberkante %.0f mm über Boden (Wannenträger offen)\n"
                % (zw, zw + wh))
        for o in portal:
            v = o.Shape.common(rahmen).Volume
            if v > 1e-3:
                f.write("Kollision %s / Rahmen: %.1f mm³\n" % (o.Name, v))
        f.write("Kollision Wanne / Rahmen: %.3f mm³\n" % wanne.common(rahmen).Volume)
        f.write("Kollision Wanne / Brücke: %.3f mm³\n" % wanne.common(br).Volume)
        f.write("Abstand Brücke UK zu Rahmen OK: %.0f mm\n" % (z0 - rahmen_bb.ZMax))


main()
