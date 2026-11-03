# -*- coding: utf-8 -*-
"""
Unterbau unter der Wanne: Geräteboden mit Plasmagerät und Schaltschrank, darüber
ein Tropfboden, der Wasser von der Wanne nach hinten ableitet, und der Kabelweg
von der Y-Energiekette zum Schaltschrank.

- Geräteboden: Alu-Platte 4 mm auf den unteren Längsrohren (vorn bis zum zweiten
  Mittelquerrohr), 4x M6 in Nietmuttern. Darauf vorn rechts das Plasmagerät
  (Front nach vorn), links daneben der Schaltschrank 400 x 500 x 200.
- Tropfboden: Alu-Blech 1,5 mm unter dem Wannenkäfig, Gefälle nach hinten, Ränder
  seitlich und vorn hochgekantet, hinten über den Rahmen hinaus mit Tropfkante.
  Der Wannenablauf geht durch eine Hülse.
- Kabelweg: Der Kabelkanal auf dem Y-Kettenträger endet vor der vordersten
  Portalstellung; dort außen rechts senkrecht hinunter, dann quer unter dem
  Tropfboden über das Plasmagerät in die rechte Seitenwand des Schaltschranks.

Koordinaten wie Grundrahmen: Ursprung = Außenecke am Boden, X quer (klein = rechts,
von vorn gesehen), Y längs (vorn = groß), Z oben.

Aufruf:
  python3 cad/live.py cad/unterbau/unterbau.py
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
    # Grundrahmen (aus grundrahmen.py)
    aussen_x=720.0,
    aussen_y=1516.0,
    rohr=40.0,
    unten_ok=140.0,             # Oberkante unterer Rahmen (unten_uk 100 + 40)
    mittelquer_y=1516.0 * 2 / 3 - 20.0,   # Hinterkante zweites Mittelquerrohr (Geräteboden liegt darauf)
    max_breite=800.0,
    # Wannenkäfig: Unterkante unterer Rahmen, Ablauf
    kaefig_uk=710.0,            # Rahmen-OK 850 - 120 (Wannenboden) - 20 (Rohr)
    kaefig_y=(238.4, 1473.6),
    ablauf=(360.0, 856.0),      # Rahmen x, y (Wannenmitte)
    ablauf_d=32.0,
    # Geräteboden
    boden_t=4.0,
    boden_loch_y=[1050.0, 1420.0],      # = grundrahmen geraeteboden_y
    # Plasmagerät SPARTUS XPro CUT 70CNC: 515 lang x 215 breit x 370 hoch (Herstellerangabe)
    geraet=(215.0, 515.0, 370.0),
    geraet_x0=45.0,             # rechts (Kettenseite), Front nach vorn
    front_y=1500.0,             # Fronten von Gerät und Schrank
    luft_ueber_geraet=500.0,    # Höhe über dem Geräteboden: Hand an die Druckluft-Einheit
    # Druckluft-Einheit (Filter/Regler) hinten am Gerät, Platzhalter
    druckluft=(80.0, 60.0, 180.0),
    # Schaltschrank links neben dem Gerät
    schrank=(400.0, 200.0, 500.0),      # Breite (x), Tiefe (y), Höhe
    schrank_x1=675.0,
    # Tropfboden
    tropf_t=1.5,
    tropf_z=(640.0, 690.0),     # Oberseite hinten (Tropfkante) / vorn
    tropf_y=(-20.0, 1476.0),    # hinten 20 über den Rahmen hinaus, vorn bis an die Beine
    tropf_rand=15.0,
    tropf_kante=10.0,           # hinten nach unten gekantet
    huelse=(40.0, 44.0, 20.0),  # Durchführung Ablauf: innen, außen, Höhe über dem Blech
    # Kabelkanäle (PVC mit Deckel, Wand 2)
    kanal_y=(1390.0, 1450.0),   # vor der vordersten Portalstellung (1408), hinter dem Bein (1476)
    kanal_x=(-65.0, -40.0),     # außen rechts neben dem Y-Kettenträger (-34)
    kanal_oben=1073.0,          # Oberkante Kabelkanal auf dem Y-Kettenträger
    quer_z=(560.0, 600.0),      # Querkanal unter dem Tropfboden, über dem Plasmagerät
    kanal_t=2.0,
    # Distanzstücke (Druck) zwischen Kanal und Rahmen, je 2x M5 von innen aus dem Kanal in
    # Nietmuttern im Rohr (= grundrahmen kanal_*)
    halter_y=1420.0,
    halter_z_or=[820.0, 840.0],
    halter_z_ut=[780.0, 800.0],
    halter_bein=[(12.0, 580.0), (28.0, 580.0)],
    bein_hinten_y=1476.0,
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def geraeteboden():
    r, ax = P["rohr"], P["aussen_x"]
    y0, y1 = P["mittelquer_y"], P["aussen_y"]
    z0 = P["unten_ok"]
    b = box(0, ax, y0, y1, z0, z0 + P["boden_t"])
    for x in (0.0, ax - r):                              # Aussparungen an den vorderen Beinen
        b = b.cut(box(x - 1, x + r, y1 - r, y1 + 1, z0 - 1, z0 + P["boden_t"] + 1))
    for x in (r / 2, ax - r / 2):
        for y in P["boden_loch_y"]:
            b = b.cut(Part.makeCylinder(3.3, P["boden_t"] + 2, V(x, y, z0 - 1)))
    return b


def boden_ok():
    return P["unten_ok"] + P["boden_t"]


def plasmageraet():
    bx, by, bz = P["geraet"]
    x0, y1, z0 = P["geraet_x0"], P["front_y"], boden_ok()
    g = box(x0, x0 + bx, y1 - by, y1, z0, z0 + bz)
    dx, dy, dz = P["druckluft"]
    xm = x0 + bx / 2
    return g, box(xm - dx / 2, xm + dx / 2, y1 - by - dy, y1 - by, z0 + 100.0, z0 + 100.0 + dz)


def schaltschrank():
    sb, st, sh = P["schrank"]
    x1, y1, z0 = P["schrank_x1"], P["front_y"], boden_ok()
    return box(x1 - sb, x1, y1 - st, y1, z0, z0 + sh)


def tropf_z(y):
    (y0, y1), (z0, z1) = P["tropf_y"], P["tropf_z"]
    return z0 + (z1 - z0) * (y - y0) / (y1 - y0)


def schraege(x0, x1, y0, y1, dz0, dz1):
    """Körper zwischen den Flächen tropf_z + dz0 und tropf_z + dz1 über x0..x1, y0..y1."""
    pts = [V(x0, y0, tropf_z(y0) + dz0), V(x0, y1, tropf_z(y1) + dz0),
           V(x0, y1, tropf_z(y1) + dz1), V(x0, y0, tropf_z(y0) + dz1)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(V(x1 - x0, 0, 0))


def tropfboden():
    r, ax = P["rohr"], P["aussen_x"]
    t, rd = P["tropf_t"], P["tropf_rand"]
    x0, x1 = r, ax - r
    y0, y1 = P["tropf_y"]
    s = schraege(x0, x1, y0, y1, -t, 0)                  # Boden (Oberseite = tropf_z)
    s = s.fuse(schraege(x0, x0 + t, y0, y1, 0, rd))      # Rand rechts
    s = s.fuse(schraege(x1 - t, x1, y0, y1, 0, rd))      # Rand links
    zf = tropf_z(y1)
    s = s.fuse(box(x0, x1, y1 - t, y1, zf - t, zf + rd))  # Rand vorn
    zh = tropf_z(y0)
    s = s.fuse(box(x0, x1, y0, y0 + t, zh - t - P["tropf_kante"], zh))   # Tropfkante hinten
    xa, ya = P["ablauf"]
    di, da, hh = P["huelse"]
    za = tropf_z(ya)
    s = s.cut(Part.makeCylinder(di / 2, 60, V(xa, ya, za - 30)))
    hu = Part.makeCylinder(da / 2, hh + t, V(xa, ya, za - t)).cut(
        Part.makeCylinder(di / 2, hh + t + 2, V(xa, ya, za - t - 1)))
    return s.fuse(hu).removeSplitter()


def rohr_kanal(x0, x1, y0, y1, z0, z1, achse):
    """Kabelkanal als Rechteckrohr (Wand kanal_t), offen in Richtung achse."""
    t = P["kanal_t"]
    k = box(x0, x1, y0, y1, z0, z1)
    o = {"x": (-1, t, t), "y": (t, -1, t), "z": (t, t, -1)}[achse]
    return k.cut(box(x0 + o[0], x1 - o[0], y0 + o[1], y1 - o[1], z0 + o[2], z1 - o[2]))


def kanaele():
    (kx0, kx1), (ky0, ky1) = P["kanal_x"], P["kanal_y"]
    zq0, zq1 = P["quer_z"]
    senk = rohr_kanal(kx0, kx1, ky0, ky1, zq0, P["kanal_oben"], "z")
    xs = P["schrank_x1"] - P["schrank"][0]
    quer = rohr_kanal(kx1, xs, ky0, ky1, zq0, zq1, "x")
    t = P["kanal_t"]
    for z in P["halter_z_or"] + P["halter_z_ut"]:        # M5 durch die Rückwand
        senk = senk.cut(Part.makeCylinder(2.75, t + 2, V(kx1 - t - 1, P["halter_y"], z), V(1, 0, 0)))
    for x, z in P["halter_bein"]:                        # M5 durch die Vorderwand
        quer = quer.cut(Part.makeCylinder(2.75, t + 2, V(x, ky1 - t - 1, z), V(0, 1, 0)))
    return senk, quer


def kanalhalter():
    """Distanzstücke (Druck): senkrechter Kanal an Längsträger und Längsrohr (rechts außen),
    Querkanal an der Rückseite des vorderen Beins."""
    kx1 = P["kanal_x"][1]
    ky1 = P["kanal_y"][1]
    y = P["halter_y"]
    res = []
    for zs in (P["halter_z_or"], P["halter_z_ut"]):
        zm = sum(zs) / 2
        s = box(kx1, 0.0, y - 20.0, y + 20.0, zm - 20.0, zm + 20.0)   # so hoch wie das Rohr
        for z in zs:
            s = s.cut(Part.makeCylinder(2.75, -kx1 + 2, V(kx1 - 1, y, z), V(1, 0, 0)))
        res.append(s)
    xs = [x for x, _ in P["halter_bein"]]
    zm = P["halter_bein"][0][1]
    s = box(min(xs) - 10.0, max(xs) + 10.0, ky1, P["bein_hinten_y"], zm - 15.0, zm + 15.0)
    for x, z in P["halter_bein"]:
        s = s.cut(Part.makeCylinder(2.75, P["bein_hinten_y"] - ky1 + 2, V(x, ky1 - 1, z), V(0, 1, 0)))
    res.append(s)
    return res


def main():
    bo = geraeteboden()
    ge, dl = plasmageraet()
    sc = schaltschrank()
    tr = tropfboden()
    senk, quer = kanaele()
    pfad = os.path.join(OUT, "unterbau.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "ub_geraeteboden", bo, "alu")
    fc_dok.teil(doc, "ub_tropfboden", tr, "alu")
    fc_dok.teil(doc, "Plasmageraet_XPro_CUT_70CNC", ge, "dummy")
    fc_dok.teil(doc, "Druckluft_Einheit", dl, "dummy")
    fc_dok.teil(doc, "Schaltschrank_400x500x200", sc, "dummy")
    fc_dok.teil(doc, "ub_kabelkanal_senkrecht", senk, "zukauf")
    fc_dok.teil(doc, "ub_kabelkanal_quer", quer, "zukauf")
    kh = kanalhalter()
    fc_dok.teil(doc, "ub_kanalhalter", Part.makeCompound(kh), "druck")
    fc_dok.speichern(doc, pfad, offen)
    for n, s in (("ub_geraeteboden", bo), ("ub_tropfboden", tr)):
        s.exportStep(os.path.join(OUT, n + ".step"))
    import Mesh
    for n, s in (("ub_kanalhalter_rahmen", kh[0]), ("ub_kanalhalter_bein", kh[2])):
        s.exportStep(os.path.join(OUT, n + ".step"))
        Mesh.Mesh(s.tessellate(0.05)).write(os.path.join(OUT, n + ".stl"))

    gx, gy, gz = P["geraet"]
    ok = boden_ok()
    y_hinten = P["front_y"] - gy
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Geräteboden: Oberkante %.0f über Boden, y %.0f bis %.0f\n"
                % (ok, P["mittelquer_y"], P["aussen_y"]))
        f.write("Tropfboden: Oberseite hinten %.0f, vorn %.0f (Gefälle %.1f %%), "
                "Ränder %.0f; unter dem Käfig mind. %.0f mm Luft\n"
                % (P["tropf_z"][0], P["tropf_z"][1],
                   100 * (P["tropf_z"][1] - P["tropf_z"][0]) / (P["tropf_y"][1] - P["tropf_y"][0]),
                   P["tropf_rand"], P["kaefig_uk"] - (tropf_z(P["kaefig_y"][1]) + P["tropf_rand"])))
        h_rueck = tropf_z(y_hinten) - P["tropf_t"] - ok
        f.write("Höhe über dem Geräteboden an der Geräterückseite (Druckluft-Einheit): %.0f mm "
                "(gefordert %.0f): %s\n" % (h_rueck, P["luft_ueber_geraet"],
                                            "ok" if h_rueck >= P["luft_ueber_geraet"] else "ZU NIEDRIG"))
        f.write("Plasmagerät: x %.0f bis %.0f, y %.0f bis %.0f, Oberkante %.0f; Querkanal darüber ab %.0f\n"
                % (P["geraet_x0"], P["geraet_x0"] + gx, y_hinten, P["front_y"], ok + gz, P["quer_z"][0]))
        sb, st, sh = P["schrank"]
        f.write("Schaltschrank: x %.0f bis %.0f, Oberkante %.0f, Tropfboden darüber ab %.0f; "
                "Abstand zum Gerät %.0f mm\n"
                % (P["schrank_x1"] - sb, P["schrank_x1"], ok + sh,
                   tropf_z(P["front_y"] - st) - P["tropf_t"],
                   P["schrank_x1"] - sb - P["geraet_x0"] - gx))
        xa, ya = P["ablauf"]
        f.write("Ablauf: durch den Tropfboden bei z %.0f, Hülse Ø%.0f bis %.0f\n"
                % (tropf_z(ya), P["huelse"][1], tropf_z(ya) + P["huelse"][2]))
        for n, sh in (("ub_kanalhalter_rahmen", kh[0]), ("ub_kanalhalter_bein", kh[2])):
            fc_dok.schreibe_waende(f, n, sh)
        f.write("Kabelkanal senkrecht außen rechts: x %.0f bis %.0f -> Maschinenbreite höchstens %.0f "
                "(Grenze %.0f, Portal links bis x 727,5)\n"
                % (P["kanal_x"][0], P["kanal_x"][1], 727.5 - P["kanal_x"][0], P["max_breite"]))


if __name__ == "__main__":
    main()
