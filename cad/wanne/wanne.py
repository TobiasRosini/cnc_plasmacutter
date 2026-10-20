# -*- coding: utf-8 -*-
"""
Wasserwanne (PE-Auffangwanne Schäfer Shop), nach Aufmaß vom 20.10.2026.

Aufmaß:
  - außen über Bördelrand 597 x 1194 x 119
  - Bördel Ø25 (Messschieber), kein voller Halbkreis, in Z gestaucht;
    Unterkante Bördel 110 über Standfläche, lichte Breite innen am Bördel 540
  - Boden innen 1100 x 550, Übergang Boden/Wand ca. R8
  - Winkel Boden/Wand ca. 97°, Wandstärke ca. 3
  - senkrechte Kanten außen R13

Annahmen (offen, siehe README):
  - 97° gilt für die Längswände. Der Bördel steht ringsum gleich weit über,
    der Neigungswinkel der Stirnwände ergibt sich daraus.
  - Bördel als Ring 110 bis 119 mit gerundeten Kanten, ringsum gleich breit
    (aus 597 - 540); er steht nach innen über die Innenwand.

Koordinaten: Ursprung = Mitte Standfläche. X = quer (597), Y = längs (1194).

Aufruf:
  flatpak run --command=FreeCADCmd org.freecad.FreeCAD $PWD/wanne.py
"""
import os
import sys
import math
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))
import fc_dok  # noqa: E402

P = dict(
    aussen_x=597.0,
    aussen_y=1194.0,
    hoehe=119.0,
    rand_uk=110.0,
    rand_innen_x=540.0,         # lichte Breite am Bördel, gemessen
    boden_innen_x=550.0,
    boden_innen_y=1100.0,
    wand=3.0,
    winkel_laengswand=97.0,     # Boden/Wand, gemessen
    radius_boden=8.0,
    radius_ecke=13.0,           # senkrechte Kanten außen
    wasserstand=95.0,           # über Standfläche (Planungswert)
)


def rechteck(bx, by, z):
    pts = [V(-bx / 2, -by / 2, z), V(bx / 2, -by / 2, z), V(bx / 2, by / 2, z),
           V(-bx / 2, by / 2, z), V(-bx / 2, -by / 2, z)]
    return Part.makePolygon(pts)


def rrechteck(bx, by, r, z):
    """Rechteck mit Eckradius r als geschlossener Draht."""
    f = Part.Face(rechteck(bx - 2 * r, by - 2 * r, z))
    return f.makeOffset2D(r).OuterWire


def geometrie():
    t, zr = P["wand"], P["rand_uk"]
    hw = zr - t                                    # Höhe der Innenwand bis Bördel
    nx = math.tan(math.radians(P["winkel_laengswand"] - 90))
    ix_oben = P["boden_innen_x"] + 2 * hw * nx
    ueberstand = (P["aussen_x"] - ix_oben - 2 * t) / 2
    iy_oben = P["aussen_y"] - 2 * ueberstand - 2 * t
    ny = (iy_oben - P["boden_innen_y"]) / 2 / hw
    return dict(nx=nx, ny=ny, ix_oben=ix_oben, iy_oben=iy_oben,
                ueberstand=ueberstand,
                winkel_stirn=90 + math.degrees(math.atan(ny)))


def wanne(g):
    t, zr, h = P["wand"], P["rand_uk"], P["hoehe"]
    bx, by = P["boden_innen_x"], P["boden_innen_y"]
    # Innenraum: Pyramidenstumpf vom Boden (z = t) bis über den Rand
    z_top = zr + 0.01
    k = (z_top - t)
    re_a = P["radius_ecke"]
    re_i = re_a - t
    innen = Part.makeLoft([rrechteck(bx, by, re_i, t),
                           rrechteck(bx + 2 * k * g["nx"], by + 2 * k * g["ny"], re_i, z_top)],
                          True)
    unten = [e for e in innen.Edges
             if abs(e.BoundBox.ZMax - t) < 1e-6 and abs(e.BoundBox.ZMin - t) < 1e-6]
    innen = innen.makeFillet(P["radius_boden"], unten)
    # Außenkörper: um Wandstärke größer, unten auf z = 0
    ax0, ay0 = bx + 2 * t - 2 * t * g["nx"], by + 2 * t - 2 * t * g["ny"]
    aussen = Part.makeLoft([rrechteck(ax0, ay0, re_a, 0),
                            rrechteck(ax0 + 2 * zr * g["nx"], ay0 + 2 * zr * g["ny"], re_a, zr)],
                           True)
    # Bördelrand: Ring mit lichter Öffnung, ringsum gleich breit
    rb = (P["aussen_x"] - P["rand_innen_x"]) / 2
    ox, oy = P["aussen_x"] - 2 * rb, P["aussen_y"] - 2 * rb
    # Ecken konzentrisch zur Außenwand
    r_aus = re_a + g["ueberstand"]
    r_in = max(re_i - (g["ix_oben"] - P["rand_innen_x"]) / 2, 2.0)
    ring = Part.Face(rrechteck(P["aussen_x"], P["aussen_y"], r_aus, zr)).cut(
        Part.Face(rrechteck(ox, oy, r_in, zr)))
    rand = ring.extrude(V(0, 0, h - zr))
    waag = [e for e in rand.Edges
            if abs(e.BoundBox.ZMax - e.BoundBox.ZMin) < 1e-6]
    rand = rand.makeFillet((h - zr) / 2 - 0.05, waag)
    return aussen.cut(innen).fuse(rand).removeSplitter(), innen


def main():
    g = geometrie()
    w, innen = wanne(g)

    pfad = os.path.join(OUT, "wanne.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "Wanne", w, "wanne", 30)
    fc_dok.speichern(doc, pfad, offen)
    w.exportStep(os.path.join(OUT, "wanne.step"))

    def inhalt(z):
        b = Part.makeBox(2000, 2000, z, V(-1000, -1000, 0))
        return innen.common(b).Volume / 1e6

    bb = App.BoundBox()   # aus Tessellierung, BoundBox ist bei Verrundungen zu grob
    for pt in w.tessellate(0.5)[0]:
        bb.add(pt)
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Wanne gültig: %s, Außenmaß %.1f x %.1f x %.1f mm\n"
                % (w.isValid(), bb.XLength, bb.YLength, bb.ZLength))
        f.write("Bördelüberstand über Außenwand (abgeleitet): %.1f mm\n" % g["ueberstand"])
        f.write("Innenmaß oben unter dem Bördel: %.1f x %.1f mm\n"
                % (g["ix_oben"], g["iy_oben"]))
        rb = (P["aussen_x"] - P["rand_innen_x"]) / 2
        f.write("Lichte Öffnung am Bördel: %.1f x %.1f mm (Bördel %.1f breit, "
                "%.1f nach innen über die Wand)\n"
                % (P["rand_innen_x"], P["aussen_y"] - 2 * rb, rb,
                   (g["ix_oben"] - P["rand_innen_x"]) / 2))
        f.write("Winkel Längswand %.1f° (gemessen), Stirnwand %.1f° (abgeleitet)\n"
                % (P["winkel_laengswand"], g["winkel_stirn"]))
        for z in (P["wasserstand"], 100.0, P["rand_uk"]):
            f.write("Wasserinhalt bis %.0f mm über Standfläche: %.1f l\n" % (z, inhalt(z)))
        rx, ry = 640.0, 1240.0
        f.write("Spiel im Grundrahmen (lichte Weite %.0f x %.0f): %.1f / %.1f mm je Seite\n"
                % (rx, ry, (rx - P["aussen_x"]) / 2, (ry - P["aussen_y"]) / 2))


main()
