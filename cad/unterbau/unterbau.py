# -*- coding: utf-8 -*-
"""
Unterbau unter der Wanne: Geräteboden mit Plasmagerät und Schaltschrank, darüber
ein Tropfboden, der Wasser von der Wanne nach hinten ableitet, und der Kabelweg
von der Y-Energiekette zum Schaltschrank.

- Geräteboden: Siebdruckplatte 9 mm auf den unteren Längsrohren (vom ersten
  Mittelquerrohr bis vorn), 6x M6 in Nietmuttern. Darauf rechts das Plasmagerät
  (Front nach vorn, 250 mm hinter der Schrankfront: Platz für Schlauchpaket und
  Stecker), links vorn der Schaltschrank 400 x 500 x 200.
- Tropfboden: Alu-Blech 1,5 mm unter dem Wannenkäfig, Gefälle nach hinten, Ränder
  seitlich und vorn hochgekantet, hinten über den Rahmen hinaus mit Tropfkante.
  Der Wannenablauf geht durch eine Hülse.
- Kabelweg: Der Kabelkanal auf dem Y-Kettenträger reicht bis hinter das vordere
  Bein; dort außen rechts an der vorderen Kettenstütze senkrecht hinunter, dann
  quer direkt hinter dem Bein in die obere rechte Ecke des Schaltschranks.

Koordinaten wie Grundrahmen: Ursprung = Außenecke am Boden, X quer (klein = rechts,
von vorn gesehen), Y längs (vorn = groß), Z oben.

Aufruf:
  python3 cad/live.py cad/unterbau/unterbau.py
"""
import math
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
    mittelquer_y=1516.0 / 3 - 20.0,       # Hinterkante erstes Mittelquerrohr (Geräteboden liegt darauf)
    max_breite=800.0,
    # Wannenkäfig: Unterkante unterer Rahmen, Ablauf
    kaefig_uk=710.0,            # Rahmen-OK 850 - 120 (Wannenboden) - 20 (Rohr)
    kaefig_y=(238.4, 1473.6),
    ablauf=(360.0, 856.0),      # Rahmen x, y (Wannenmitte)
    ablauf_d=32.0,
    # Geräteboden
    boden_t=9.0,                # Siebdruckplatte 9
    boden_loch_y=[560.0, 1050.0, 1420.0],   # = grundrahmen geraeteboden_y
    # Plasmagerät SPARTUS XPro CUT 70CNC: 515 lang x 215 breit x 370 hoch (Herstellerangabe)
    geraet=(215.0, 515.0, 370.0),
    geraet_x0=45.0,             # rechts (Kettenseite), Front nach vorn
    front_y=1500.0,             # Front des Schranks
    geraet_zurueck=250.0,       # Gerätefront hinter front_y: Schlauchpaket mit langem Stecker
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
    # Kabelkanäle senkrecht und quer: derselbe Typ PVC 25 x 60 mit Deckel, Wand 2
    kanal_y=(1416.0, 1476.0),   # direkt hinter dem vorderen Bein (Rückseite 1476)
    kanal_x=(-65.0, -40.0),     # senkrecht außen auf der vorderen Kettenstütze (40 x 40, x -40 bis 0), Deckel außen
    kanal_oben=1073.0,          # Oberkante Kabelkanal 40 x 40 auf dem Y-Kettenträger
    traeger_ok=1033.0,          # Oberkante Y-Kettenträger (= Unterkante Kanal darauf)
    traeger_x=(-34.0, 6.0),     # Y-Kettenträger und Kanal darauf
    traeger_h=20.0,
    # Kanalknoten (Druck) über der vorderen Kettenstütze
    stuetze_ok=900.0,           # Oberkante vordere Kettenstütze (= energiekette stuetze_vorn_ok)
    knoten_muffe=25.0,          # Träger und Kanal Y stecken so tief im Knoten (enden bei y 1437,25)
    knoten_boden=15.0,          # unter dem Träger innen (über dem Umlenkhalter Y, OK 947)
    knoten_schuerze=30.0,       # Vorderwand reicht so weit über die Stütze
    knoten_stuetze=[(-28.0, 885.0), (-12.0, 885.0)],   # M5 von vorn in die Stütze (= energiekette stuetze_knoten)
    knoten_traeger_y=[1419.0, 1431.0],                 # M5 von innen in den Träger (= energiekette traeger_knoten_y)
    quer_z=(615.0, 640.0),      # Querkanal flach (Deckel unten), oben bündig unter der Schrankdecke
    kanal_t=2.0,
    # Übergangsteile (Druck): Muffen 15 tief über den Kanalenden, Wand 3,2, Spiel 0,25 je Seite
    ue_wand=3.2,
    ue_spiel=0.25,
    ue_muffe=15.0,
    bogen_ri=10.0,              # Bogen unten: Innenradius (Außenradius = + 25)
    ue_m3_tiefe=5.0,            # Deckelschrauben M3: Mutter so tief unter der Deckelauflage
    # Befestigung ohne Distanzstücke: je 2x M5 von innen aus dem Kanal in Nietmuttern
    # senkrecht: in der vorderen Kettenstütze (= energiekette stuetze_kanal_*, Rahmen-z = 850 + z)
    stuetze_y0=1436.0,
    stuetze_uk=680.0,           # über der Muffe des unteren Bogens
    stuetze_kanal_y=[10.0, 30.0],
    stuetze_kanal_z=[720.0, 860.0],
    # Durchgriffe in der Rückwand des senkrechten Kanals (Deckel offen) zu den M6 der Stütze
    # am Rahmen (Zugang Ø13, = energiekette, Rahmen-y, -z)
    durchgriff=[(13.0, y, z) for y in (1446.0, 1466.0) for z in (790.0, 830.0)],
    # quer: in der Rückseite des vorderen Beins (= grundrahmen kanal_bein)
    kanal_bein=[(12.0, 627.5), (28.0, 627.5)],
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


def geraet_front_y():
    return P["front_y"] - P["geraet_zurueck"]


def plasmageraet():
    bx, by, bz = P["geraet"]
    x0, y1, z0 = P["geraet_x0"], geraet_front_y(), boden_ok()
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


def bogen_mitte():
    """Mittelpunkt des unteren Bogens (x, z): Innenkante senkrecht / Oberkante quer + Innenradius."""
    return P["kanal_x"][1] + P["bogen_ri"], P["quer_z"][1] + P["bogen_ri"]


def kanaele():
    (kx0, kx1), (ky0, ky1) = P["kanal_x"], P["kanal_y"]
    zq0, zq1 = P["quer_z"]
    xc, zc = bogen_mitte()
    senk = rohr_kanal(kx0, kx1, ky0, ky1, zc, P["stuetze_ok"], "z")
    xs = P["schrank_x1"] - P["schrank"][0]
    quer = rohr_kanal(xc, xs, ky0, ky1, zq0, zq1, "x")
    t = P["kanal_t"]
    for dy in P["stuetze_kanal_y"]:                      # M5 durch die Rückwand in die Kettenstütze
        for z in P["stuetze_kanal_z"]:
            senk = senk.cut(Part.makeCylinder(2.75, t + 2, V(kx1 - t - 1, P["stuetze_y0"] + dy, z),
                                              V(1, 0, 0)))
    for d, y, z in P["durchgriff"]:
        senk = senk.cut(Part.makeCylinder(d / 2, t + 2, V(kx1 - t - 1, y, z), V(1, 0, 0)))
    for x, z in P["kanal_bein"]:                         # M5 durch die Vorderwand ins Bein
        quer = quer.cut(Part.makeCylinder(2.75, t + 2, V(x, ky1 - t - 1, z), V(0, 1, 0)))
    return senk, quer


def m3_deckel(teil, deckel, p, achse, schlitz):
    """Deckelschraube M3: Loch im Deckel, Loch und seitlich eingeschobene Mutter im Teil.
    p = Lochmitte in der Deckelauflage, achse = vom Deckel in das Teil."""
    a = V(achse)
    teil = teil.cut(Part.makeCylinder(1.7, 14.0, p - a * 1.0, a))
    teil = teil.cut(fc_dok.mutter(3, p + a * P["ue_m3_tiefe"], a, schlitz, 12.0))
    deckel = deckel.cut(Part.makeCylinder(1.7, 10.0, p - a * 6.0, a))
    return teil, deckel


def uebergang_unten():
    """Bogen vom senkrechten Kanal in den Querkanal (Druck): Viertelring um die
    Bogenmitte (Querschnitt wie die Kanäle), Muffen über beide Kanalenden, offen nach
    hinten (-y) mit flachem Deckel. Druck auf der Vorderseite (+y), alle Wände senkrecht."""
    w, sp, lm = P["ue_wand"], P["ue_spiel"], P["ue_muffe"]
    xc, zc = bogen_mitte()
    ri = P["bogen_ri"]
    ra = ri + (P["kanal_x"][1] - P["kanal_x"][0])
    ky0, ky1 = P["kanal_y"]
    yo, yv = ky0 - sp, ky1 + sp + w                      # offene Seite, Vorderseite (Druckbett)
    yd = yo - w                                          # Deckel yd..yo

    def ring(r0, r1, y0, y1):
        c = Part.makeCylinder(r1, y1 - y0, V(xc, y0, zc), V(0, 1, 0))
        if r0 > 0:
            c = c.cut(Part.makeCylinder(r0, y1 - y0 + 2, V(xc, y0 - 1, zc), V(0, 1, 0)))
        return c.common(box(xc - r1 - 1, xc, y0 - 1, y1 + 1, zc - r1 - 1, zc))

    def umriss(y0, y1):
        u = ring(ri - sp - w, ra + sp + w, y0, y1)
        u = u.fuse(box(P["kanal_x"][0] - sp - w, P["kanal_x"][1] + sp + w, y0, y1, zc, zc + lm))
        u = u.fuse(box(xc, xc + lm, y0, y1, P["quer_z"][0] - sp - w, P["quer_z"][1] + sp + w))
        return u

    d = 42.0 / math.sqrt(2)
    bosse = [((xc, zc), ri - sp - w, (1, 0, 1)),        # in der Innenecke, Mutter von rechts oben
             ((xc - d, zc - d), 5.0, (-1, 0, -1))]     # außen an der Ecke
    k = umriss(yo, yv)
    for (bx, bz), r, _ in bosse:
        k = k.fuse(Part.makeCylinder(r, yv - yo, V(bx, yo, bz), V(0, 1, 0)))
    yi = ky1 + sp                                        # Innenraum bis zur Vorderwand
    k = k.cut(ring(ri - sp, ra + sp, yo - 1, yi))
    k = k.cut(box(P["kanal_x"][0] - sp, P["kanal_x"][1] + sp, yo - 1, yi, zc, zc + lm + 1))
    k = k.cut(box(xc, xc + lm + 1, yo - 1, yi, P["quer_z"][0] - sp, P["quer_z"][1] + sp))
    de = umriss(yd, yo)
    for (bx, bz), r, _ in bosse:
        de = de.fuse(Part.makeCylinder(r, w, V(bx, yd, bz), V(0, 1, 0)))
    for (bx, bz), _, sl in bosse:
        k, de = m3_deckel(k, de, V(bx, yo, bz), (0, 1, 0), sl)
    return k.removeSplitter(), de.removeSplitter()


def knoten():
    """Kanalknoten (Druck) vorn rechts: hier laufen Y-Träger mit Kanal, senkrechter Kanal und
    vordere Kettenstütze zusammen. Träger und Kanal darauf stecken gemeinsam von hinten in
    einer Muffe (2x M5 von innen in Nietmuttern im Träger), der senkrechte Kanal von unten.
    Der Knoten sitzt auf der Stütze, eine Schürze der Vorderwand greift über sie (2x M5 von
    vorn in Nietmuttern). Innen laufen die Leitungen vom Y-Kanal seitlich in den senkrechten
    Kanal. Geschlossen, kein Deckel. Druck auf der Vorderseite liegend (Brücken bis 40 mm)."""
    w, sp, lm = P["ue_wand"], P["ue_spiel"], P["ue_muffe"]
    (kx0, kx1), (ky0, ky1) = P["kanal_x"], P["kanal_y"]
    (tx0, tx1), zt = P["traeger_x"], P["traeger_ok"]
    ztu = zt - P["traeger_h"]                            # Unterkante Träger = Auflage im Knoten
    zk = P["kanal_oben"] + sp
    zs = P["stuetze_ok"]
    xa, xi = kx0 - sp - w, tx1 + sp + w
    yh, yv = ky0 - sp - w, ky1 + sp + w
    ys = yh + P["knoten_muffe"]                          # Grund der Muffe für Träger und Kanal Y
    k = box(xa, 0.0, yh, yv, zs, zk + w)                 # über der Stütze und dem senkrechten Kanal
    k = k.fuse(box(0.0, xi, yh, yv, ztu - P["knoten_boden"], zk + w))   # unter dem Träger, über dem Umlenkhalter
    k = k.fuse(box(xa, 0.0, ky1 + sp, yv, zs - P["knoten_schuerze"], zs))  # Schürze vorn über die Stütze
    k = k.fuse(box(xa, kx0 - sp, yh, yv, zs - lm, zs))   # Muffe senkrecht: außen
    k = k.fuse(box(xa, kx1, yh, ky0 - sp, zs - lm, zs))  # hinten (innen liegt der Kanal an der Stütze)
    k = k.cut(box(kx0 - sp, kx1 + sp, ky0 - sp, ky1 + sp, zs - lm - 1, zk))       # senkrecht
    k = k.cut(box(tx0 - sp, tx1 + sp, yh - 1, ys, ztu, zk))                       # Muffe Träger + Kanal Y
    k = k.cut(box(tx0 - sp, tx1 + sp, ys - 1, ky1 + sp, zt, zk))                  # Leitungen über dem Träger
    k = k.cut(box(kx1 + sp - 1, tx0 - sp + 1, ys, ky1 + sp, zt, zk))              # Übergang zur Seite
    for x, z in P["knoten_stuetze"]:                     # M5 von vorn in die Stütze
        k = k.cut(Part.makeCylinder(2.75, w + 2, V(x, yv + 1, z), V(0, -1, 0)))
    for y in P["knoten_traeger_y"]:                      # M5 von innen in den Träger
        k = k.cut(Part.makeCylinder(2.75, w + 2, V(xi + 1, y, ztu + P["traeger_h"] / 2), V(-1, 0, 0)))
    return k.removeSplitter()


def main():
    bo = geraeteboden()
    ge, dl = plasmageraet()
    sc = schaltschrank()
    tr = tropfboden()
    senk, quer = kanaele()
    pfad = os.path.join(OUT, "unterbau.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "ub_geraeteboden", bo, "zukauf")
    fc_dok.teil(doc, "ub_tropfboden", tr, "alu")
    fc_dok.teil(doc, "Plasmageraet_XPro_CUT_70CNC", ge, "dummy")
    fc_dok.teil(doc, "Druckluft_Einheit", dl, "dummy")
    fc_dok.teil(doc, "Schaltschrank_400x500x200", sc, "dummy")
    fc_dok.teil(doc, "ub_kabelkanal_senkrecht", senk, "zukauf")
    fc_dok.teil(doc, "ub_kabelkanal_quer", quer, "zukauf")
    uu, uud = uebergang_unten()
    druck = {"ub_uebergang_unten": uu, "ub_uebergang_unten_deckel": uud, "ub_kanalknoten": knoten()}
    for n, sh in druck.items():
        fc_dok.teil(doc, n, sh, "druck")
    fc_dok.speichern(doc, pfad, offen)
    for n, s in (("ub_geraeteboden", bo), ("ub_tropfboden", tr)):
        s.exportStep(os.path.join(OUT, n + ".step"))
    import Mesh
    for n, s in druck.items():
        s.exportStep(os.path.join(OUT, n + ".step"))
        Mesh.Mesh(s.tessellate(0.05)).write(os.path.join(OUT, n + ".stl"))

    gx, gy, gz = P["geraet"]
    ok = boden_ok()
    yf = geraet_front_y()
    y_hinten = yf - gy
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
        f.write("Plasmagerät: x %.0f bis %.0f, y %.0f bis %.0f, Oberkante %.0f; vor der Front %.0f mm "
                "bis zum Querkanal, %.0f mm bis zur Schrankfront\n"
                % (P["geraet_x0"], P["geraet_x0"] + gx, y_hinten, yf, ok + gz,
                   P["kanal_y"][0] - yf, P["front_y"] - yf))
        f.write("Geräteboden liegt auf: Mittelquerrohr 1 (%.0f-%.0f), Mittelquerrohr 2 (%.0f-%.0f), "
                "Querrohr vorn (%.0f-%.0f); größte freie Spannweite in y %.0f mm\n"
                % (P["mittelquer_y"], P["mittelquer_y"] + 40, P["aussen_y"] * 2 / 3 - 20,
                   P["aussen_y"] * 2 / 3 + 20, P["aussen_y"] - 40, P["aussen_y"],
                   P["aussen_y"] * 2 / 3 - 20 - (P["mittelquer_y"] + 40)))
        sb, st, sh = P["schrank"]
        f.write("Querkanal z %.0f bis %.0f, Einführung in die rechte Seitenwand des Schranks %.0f mm unter "
                "der Oberkante; Muffe des Bogens bis zur Kettenstütze vorn %.0f mm frei\n"
                % (P["quer_z"][0], P["quer_z"][1], ok + sh - P["quer_z"][1],
                   P["stuetze_uk"] - bogen_mitte()[1] - P["ue_muffe"]))
        f.write("Schaltschrank: x %.0f bis %.0f, Oberkante %.0f, Tropfboden darüber ab %.0f; "
                "Abstand zum Gerät %.0f mm\n"
                % (P["schrank_x1"] - sb, P["schrank_x1"], ok + sh,
                   tropf_z(P["front_y"] - st) - P["tropf_t"],
                   P["schrank_x1"] - sb - P["geraet_x0"] - gx))
        xa, ya = P["ablauf"]
        f.write("Ablauf: durch den Tropfboden bei z %.0f, Hülse Ø%.0f bis %.0f\n"
                % (tropf_z(ya), P["huelse"][1], tropf_z(ya) + P["huelse"][2]))
        for n, sh in druck.items():
            fc_dok.schreibe_waende(f, n, sh)
        xc, zc = bogen_mitte()
        f.write("Bogen unten: Mitte x %.0f z %.0f, R%.0f bis R%.0f; senkrechter Kanal z %.0f bis %.0f, "
                "Querkanal ab x %.0f\n" % (xc, zc, P["bogen_ri"], P["bogen_ri"] + 25, zc, P["stuetze_ok"], xc))
        kb = knoten().BoundBox
        f.write("Kanalknoten: x %.2f bis %.2f, y %.2f bis %.2f, z %.0f bis %.2f (Druckhöhe %.1f auf der "
                "Vorderseite); Träger und Kanal Y enden bei y %.2f\n"
                % (kb.XMin, kb.XMax, kb.YMin, kb.YMax, kb.ZMin, kb.ZMax, kb.YLength,
                   P["kanal_y"][0] - P["ue_spiel"] - P["ue_wand"] + P["knoten_muffe"] - P["ue_spiel"]))
        xa = P["kanal_x"][0] - P["ue_spiel"] - P["ue_wand"]
        f.write("Kabelkanal senkrecht außen rechts: x %.0f bis %.0f, Übergangsteile bis x %.2f -> "
                "Maschinenbreite höchstens %.0f (Grenze %.0f, Portal links bis x 727,5)\n"
                % (P["kanal_x"][0], P["kanal_x"][1], xa, 727.5 - xa, P["max_breite"]))


if __name__ == "__main__":
    main()
