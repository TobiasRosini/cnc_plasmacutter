# -*- coding: utf-8 -*-
"""
Y-Antrieb: Motorhalter (hinten) und Umlenkhalter (vorn) auf den Rahmen-
Längsträgern, je links und rechts. Motor NEMA23 (3 Nm) innen, Achse quer (X),
Riemenscheibe 24 Z genau über der Schienenmitte.

Lage (Konvention "hinten links"): x = Schienenmitte, +x nach innen,
y = Schienenende, +y entlang der Schiene in den Tisch, z = Oberkante Rahmen.
Die rechten Teile sind gespiegelt; vorn werden sie im Zusammenbau um 180°
gedreht eingesetzt.

Aufruf:
  python3 cad/live.py cad/y_antrieb/y_antrieb.py
"""
import os
import sys
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))
import fc_dok  # noqa: E402
import kaufteile as kt  # noqa: E402

P = dict(
    # Riemenlage aus y_portalwinkel: Wagenhöhe 28 + Rücktrum-UK 17 + Rücken 1,7
    # + halber Teilkreis 19,1 = Achse über Rahmenoberkante
    z_achse=28.0 + 17.0 + 1.7 + 24 * 5.0 / 3.141592653589793 / 2,
    y_achse=-32.0,              # hinter dem Schienenende (Winkel fährt bis y = 0)
    rohr=40.0,
    rahmen_ende=-70.0,          # Rahmenende (Verlängerung 60 + 10 Schiene)
    # Halter (3D-Druck)
    basis_dicke=10.0,
    platte_dicke=10.0,
    platte_rand=3.0,            # über dem Motorflansch
    rippe=6.0,
    y_vorn=-2.0,                # Halter endet vor dem Schienenanfang
    m6_durchgang=6.6,
    m6_senk_d=11.0,
    m6_senk_tiefe=4.0,
    basis_loecher=[(-10.0, -52.0), (10.0, -52.0), (-10.0, -14.0), (10.0, -14.0)],
    m5_durchgang=5.5,
    m5_mutter_sw=8.2,
    m5_mutter_tiefe=4.5,
    achse_d=8.4,
    m8_mutter_sw=13.2,
    m8_mutter_tiefe=6.5,
    # Motor
    motor_laenge=76.0,          # NEMA23 ca. 1,9 Nm (statt 3 Nm, 112 mm)
    # Referenzschalter Y (nur Motorhalter, hinten): über der Riemenscheibe, genau
    # über der Schiene, Achse längs. Fahne auf der Klemmplatte am festen Ende des
    # Y-Winkels. Der Block bleibt innen unter 14 mm (dort fährt der X-Motorbock
    # nur 1 mm darüber), der Steg zur Platte bleibt unter 97 mm.
    ref_x=0.0,
    ref_z=98.0,
    ref_block=(-12.0, 14.0, -30.0, -14.0, 88.5, 107.5),  # x0, x1, y0, y1, z0, z1
    ref_steg_oben=97.0,
    ref_luft=6.0,               # Sensorfläche hinter dem Schienenende (Fahne steht 3 mm über)
    motor_welle_d=8.0,
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def zyl_x(d, l, x, y, z):
    return Part.makeCylinder(d / 2, l, V(x, y, z), V(1, 0, 0))


def sechskant_x(sw, h, x, y, z):
    import math
    r = sw / math.sqrt(3)
    pts = [V(x, y + r * math.cos(math.radians(30 + 60 * i)),
             z + r * math.sin(math.radians(30 + 60 * i))) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(h, 0, 0))


def scheibe(mit_nabe=True):
    s, d = kt.riemenscheibe_htd5m(24, bohrung=P["motor_welle_d"],
                                  nabe_l=8.0 if mit_nabe else 0.01)
    mitte = sum(d["zahnbereich"]) / 2
    s.translate(V(0, 0, -mitte))
    s.rotate(V(0, 0, 0), V(0, 1, 0), 90)               # Achse Z -> X, Nabe nach +x (innen)
    s.translate(V(0, P["y_achse"], P["z_achse"]))
    return fc_dok.fest(s), d["hoehe"] - mitte


def geo():
    _, x_nabe = scheibe()
    x0 = x_nabe + 1                                     # Außenseite Platte
    return dict(x0=x0, x1=x0 + P["platte_dicke"])


def halter(variante):
    g = geo()
    r = P["rohr"] / 2
    ya, yv = P["rahmen_ende"] + 4, P["y_vorn"]
    za, ya_ = P["z_achse"], P["y_achse"]
    k = 56.4 / 2 + P["platte_rand"]
    s = box(-r, g["x1"], ya, yv, 0, P["basis_dicke"])                     # Basis
    s = s.fuse(box(g["x0"], g["x1"], ya, yv, 0, za + k))                  # Platte
    rp = P["rippe"]                                                         # Rippe hinten
    pts = [V(-r, ya, P["basis_dicke"]), V(g["x0"] + 0.01, ya, P["basis_dicke"]),
           V(g["x0"] + 0.01, ya, za + k - 5), V(-r, ya, P["basis_dicke"])]
    s = s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(0, rp, 0)))
    # Befestigung auf dem Längsträger: 4x M6, gesenkt
    for x, y in P["basis_loecher"]:
        s = s.cut(Part.makeCylinder(P["m6_durchgang"] / 2, P["basis_dicke"] + 2, V(x, y, -1)))
        s = s.cut(Part.makeCylinder(P["m6_senk_d"] / 2, P["m6_senk_tiefe"] + 1,
                                    V(x, y, P["basis_dicke"] - P["m6_senk_tiefe"])))
    t = P["platte_dicke"]
    if variante == "motor":                                                 # Schalterblock außen
        x0, x1, y0, y1, z0, z1 = P["ref_block"]
        s = s.fuse(box(x0, x1, y0, y1, z0, z1))
        s = s.fuse(box(x1 - 0.01, g["x0"] + 0.01, y0, y1, z0, P["ref_steg_oben"]))   # Steg zur Platte
        s = s.cut(Part.makeCylinder(6.1, y1 - y0 + 2, V(P["ref_x"], y0 - 1, P["ref_z"]), V(0, 1, 0)))
        s = s.cut(zyl_x(38.1 + 1, t + 2, g["x0"] - 1, ya_, za))
        a = 47.14 / 2
        for dy in (-a, a):
            for dz in (-a, a):
                s = s.cut(zyl_x(P["m5_durchgang"], t + 2, g["x0"] - 1, ya_ + dy, za + dz))
                s = s.cut(sechskant_x(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 1, g["x0"] - 1,
                                      ya_ + dy, za + dz))
    else:
        s = s.cut(zyl_x(P["achse_d"], t + 2, g["x0"] - 1, ya_, za))
        s = s.cut(sechskant_x(P["m8_mutter_sw"], P["m8_mutter_tiefe"] + 1,
                              g["x1"] - P["m8_mutter_tiefe"], ya_, za))
    return s.removeSplitter()


def motor():
    g = geo()
    m, _ = kt.nema23(P["motor_laenge"], P["motor_welle_d"], kabel_winkel=270.0)
    m.rotate(V(0, 0, 0), V(0, 1, 0), 90)               # Welle -X, Körper +X
    m.translate(V(g["x1"], P["y_achse"], P["z_achse"]))
    return fc_dok.fest(m)


def ref_schalter():
    x0, x1, y0, y1, z0, z1 = P["ref_block"]
    m = kt.naeherungsschalter_m12(50.0, (-y1 - P["ref_luft"] - 4.0, -y0 - P["ref_luft"]))
    m.rotate(V(0, 0, 0), V(1, 0, 0), 90)                # +Z -> -Y (Körper nach hinten)
    m.translate(V(P["ref_x"], -P["ref_luft"], P["ref_z"]))
    return fc_dok.fest(m)


def gespiegelt(s):
    return s.mirror(V(0, 0, 0), V(1, 0, 0))


def main():
    teile = {
        "y_motorhalter": (halter("motor"), "druck"),
        "y_umlenkhalter": (halter("umlenk"), "druck"),
        "Motor_Y": (motor(), "zukauf"),
        "Riemenscheibe_Y": (scheibe(True)[0], "zukauf"),
        "Umlenkrolle_Y": (scheibe(False)[0], "zukauf"),
        "Referenzschalter_Y": (ref_schalter(), "zukauf"),
    }
    for n in list(teile):
        teile[n + "_r"] = (gespiegelt(teile[n][0]), teile[n][1])

    pfad = os.path.join(OUT, "y_antrieb.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    for n, (shp, farbe) in teile.items():
        o = fc_dok.teil(doc, n, shp, farbe)
        # Darstellung im Teile-Dokument nebeneinander (der Zusammenbau setzt eigene Lagen)
        dx = 200.0 if n.endswith("_r") else 0.0
        dy = 150.0 if ("umlenk" in n.lower()) else 0.0
        o.Placement = App.Placement(V(-dx, dy, 0), App.Rotation())
    fc_dok.speichern(doc, pfad, offen)

    import Mesh
    for n in ("y_motorhalter", "y_umlenkhalter", "y_motorhalter_r", "y_umlenkhalter_r"):
        shp = teile[n][0]
        shp.exportStep(os.path.join(OUT, n + ".step"))
        Mesh.Mesh(shp.tessellate(0.05)).write(os.path.join(OUT, n + ".stl"))

    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        for n in ("y_motorhalter", "y_umlenkhalter"):
            shp = teile[n][0]
            bb = shp.BoundBox
            f.write("%-16s gültig: %s, %.1f x %.1f x %.1f mm\n"
                    % (n, shp.isValid(), bb.XLength, bb.YLength, bb.ZLength))
            fc_dok.schreibe_waende(f, n, shp)
        paare = [("y_motorhalter", "Motor_Y"), ("y_motorhalter", "Riemenscheibe_Y"),
                 ("Motor_Y", "Riemenscheibe_Y"), ("y_umlenkhalter", "Umlenkrolle_Y")]
        for a, b in paare:
            f.write("Kollision %s / %s: %.3f mm³\n"
                    % (a, b, teile[a][0].common(teile[b][0]).Volume))
        f.write("Achse Riemenscheibe: z %.1f über Rahmen, y %.1f vor dem Schienenende\n"
                % (P["z_achse"], P["y_achse"]))
        f.write("Motor innen bis x %.1f ab Schienenmitte\n" % teile["Motor_Y"][0].BoundBox.XMax)


main()
