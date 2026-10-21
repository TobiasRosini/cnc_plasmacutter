# -*- coding: utf-8 -*-
"""
Wannenkäfig aus Stahl-Rechteckrohr 20x20x2 (nur gerade Schnitte, stumpf
verschweißt). Trägt die Wanne am Boden, hält die Wände und hängt mit dem
oberen Ring innen am Grundrahmen (an die Längsträger geschraubt).

Höhe: Bleche, die breiter als die Wannenöffnung (540) sind, liegen sonst auf
dem Bördel. Die Opferleisten stehen deshalb 1 mm über dem Bördel (Wannenboden
+ 120), und zwar auf Trägern im Wasser direkt über den Querrohren des Käfigs
(die Last geht durch den Wannenboden ins Rohr, nicht in die Wände). Wasser bis
knapp unter den Bördel (105 über Boden) -> 15 mm unter dem Blech.
Blechunterseite = Rahmenoberkante (die Düse kommt bis 8 mm darunter).
Oberer Ring: Oberkante = Rahmenoberkante, außen neben dem Bördel.

In der Mitte bleibt der Boden zwischen zwei Querrohren frei für den Ablauf.

Koordinaten: x/y = Wannenmitte, z = Rahmenoberkante.

Aufruf:
  python3 cad/live.py cad/wannenkaefig/wannenkaefig.py
"""
import os
import sys
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))
import fc_dok  # noqa: E402

P = dict(
    rohr=20.0,
    wand=2.0,
    dichte=7.85e-6,
    # Rahmen innen (Grundrahmen: 640 breit); Käfig liegt mit dem Ring am Rahmen an
    innen_x=640.0,
    # Wanne
    wanne_x=597.0,
    wanne_y=1194.0,
    wanne_ueberstand=7.4,       # Bördel über Außenwand
    boden_aussen_y=1106.0,      # 1100 innen + 2x Wand
    wand_luft=8.0,              # Ring innen bis Wanne
    blech_unten=0.0,            # Blechunterseite über Rahmenoberkante
    wanne_hoehe=119.0,
    leiste_ueber_rand=1.0,
    wasserstand=105.0,          # über Wannenboden (Bördel-UK 110)
    # Böden: Querrohre unter dem Wannenboden (y-Lagen ab Mitte); Mitte frei für Ablauf
    querrohre_y=[110.0, 330.0, 550.0],
    pfosten_y=[0.0],            # zusätzlich zu den Ecken, an beiden Längsseiten
    ablauf_d=40.0,
    ablauf_l=120.0,
    # Befestigung am Rahmen: M8 quer durch Ring und Längsträger
    bolzen_y=[-450.0, 0.0, 450.0],
    m8_durchgang=8.5,
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


ZUSCHNITT = []


def rohr(name, x0, y0, z0, laenge, achse):
    r, t = P["rohr"], P["wand"]
    d = {"x": (laenge, r, r), "y": (r, laenge, r), "z": (r, r, laenge)}[achse]
    aussen = box(x0, x0 + d[0], y0, y0 + d[1], z0, z0 + d[2])
    o = [t if d[i] == r else -1 for i in range(3)]
    innen = box(x0 + o[0], x0 + d[0] - o[0], y0 + o[1], y0 + d[1] - o[1],
                z0 + o[2], z0 + d[2] - o[2])
    ZUSCHNITT.append((name, laenge))
    return aussen.cut(innen)


def geo():
    r = P["rohr"]
    z_boden = P["blech_unten"] - P["wanne_hoehe"] - P["leiste_ueber_rand"]   # Standfläche Wanne
    ax = P["innen_x"] / 2                                       # Ring außen = Rahmen innen
    wy = P["wanne_y"] / 2 - P["wanne_ueberstand"] + P["wand_luft"]   # Ring innen (y)
    ay = wy + r
    return dict(z_boden=z_boden, ax=ax, ay=ay, z_ring=-r)


def kaefig():
    g = geo()
    r = P["rohr"]
    ax, ay = g["ax"], g["ay"]
    teile = []
    for z0, ring in ((g["z_ring"], "Ring oben"), (g["z_boden"] - r, "Rahmen unten")):
        for sx in (-1, 1):                                       # Längsrohre, volle Länge
            x0 = ax - r if sx > 0 else -ax
            teile.append(rohr(ring + " längs", x0, -ay, z0, 2 * ay, "y"))
        for sy in (-1, 1):                                       # Stirnrohre dazwischen
            y0 = ay - r if sy > 0 else -ay
            teile.append(rohr(ring + " quer", -ax + r, y0, z0, 2 * ax - 2 * r, "x"))
    zb = g["z_boden"] - r
    for y in P["querrohre_y"]:                                   # Querrohre unter dem Boden
        for sy in (-1, 1):
            teile.append(rohr("Querrohr Boden", -ax + r, sy * y - r / 2, zb, 2 * ax - 2 * r, "x"))
    h = g["z_ring"] - g["z_boden"]                               # Pfosten zwischen den Ringen
    ys = [-ay, ay - r] + [y - r / 2 for y in P["pfosten_y"]]
    for sx in (-1, 1):
        x0 = ax - r if sx > 0 else -ax
        for y0 in ys:
            teile.append(rohr("Pfosten", x0, y0, g["z_boden"], h, "z"))
    s = teile[0].fuse(teile[1:])
    # M8 quer durch den Ring (und den Längsträger des Rahmens)
    for sx in (-1, 1):
        for y in P["bolzen_y"]:
            s = s.cut(Part.makeCylinder(P["m8_durchgang"] / 2, r + 2,
                                        V(sx * (ax + 1), y, g["z_ring"] + r / 2),
                                        V(-sx, 0, 0)))
    return s.removeSplitter()


def ablauf():
    g = geo()
    return Part.makeCylinder(P["ablauf_d"] / 2, P["ablauf_l"],
                             V(0, 0, g["z_boden"] + 3 - P["ablauf_l"]))


def main():
    k = kaefig()
    a = ablauf()
    pfad = os.path.join(OUT, "wannenkaefig.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "Wannenkaefig", k, "stahl")
    fc_dok.teil(doc, "Ablauf", a, "zukauf")
    fc_dok.speichern(doc, pfad, offen)
    k.exportStep(os.path.join(OUT, "wannenkaefig.step"))

    r, t = P["rohr"], P["wand"]
    kg_m = (r * r - (r - 2 * t) ** 2) * 1000 * P["dichte"]
    zus = {}
    for name, l in ZUSCHNITT:
        zus[(name, round(l, 1))] = zus.get((name, round(l, 1)), 0) + 1
    gesamt = sum(l * n for (_, l), n in zus.items())
    g = geo()
    with open(os.path.join(OUT, "zuschnitt.txt"), "w") as f:
        f.write("Zuschnitt Rechteckrohr %gx%gx%g Stahl, alle Schnitte gerade (90°)\n\n" % (r, r, t))
        f.write("%-22s %10s %6s\n" % ("Teil", "Länge mm", "Stk"))
        for (name, l), n in sorted(zus.items(), key=lambda e: -e[0][1]):
            f.write("%-22s %10.1f %6d\n" % (name, l, n))
        f.write("\nSumme Rohr: %.2f m (%.1f kg bei %.2f kg/m), ohne Sägeverlust\n"
                % (gesamt / 1000, gesamt / 1000 * kg_m, kg_m))
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Käfig gültig: %s, außen %.0f x %.0f, Höhe %.0f mm\n"
                % (k.isValid(), 2 * g["ax"], 2 * g["ay"], -g["z_boden"] + r))
        f.write("Wanne steht %.1f mm unter Rahmenoberkante; Bördel %.1f bis %.1f; Wasser bis %.1f; "
                "Blech (Leisten-OK) %.1f -> Wasser %.1f mm unter dem Blech; Ring-OK 0\n"
                % (-g["z_boden"], g["z_boden"] + 110, g["z_boden"] + P["wanne_hoehe"],
                   g["z_boden"] + P["wasserstand"], P["blech_unten"],
                   P["blech_unten"] - g["z_boden"] - P["wasserstand"]))
        f.write("Ablauf: Boden frei zwischen den Querrohren y ±%.0f\n"
                % (P["querrohre_y"][0] - r / 2))


main()
