# -*- coding: utf-8 -*-
"""
Y-Energiekette, liegend, links (Kastenseite).

Kette 20 x 38 innen, 35 x 56 außen, R125. Die feste Hälfte liegt in einer Rinne
auf einem Träger über dem linken Y-Winkel (höher als alles, was dort am Portal
hochsteht). Der Träger liegt auf zwei Stützen an den Rahmenenden, außen am
Längsträger. Das bewegte Ende sitzt oben auf der Schlaufe; ein Ausleger aus
Alu-Flachstahl geht von der Kettenlasche des linken Winkels außen an der Rinne
vorbei nach oben.

Lage: x ab Mitte linke Y-Schiene (negativ = außen), y = Rahmen-y (feste Teile)
bzw. ab Portalmitte (Ausleger), z = Rahmenoberkante.

Aufruf:
  python3 cad/live.py cad/energiekette/energiekette.py
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
    # Maschine (aus Grundrahmen / Y-Winkel)
    rahmen_laenge=1516.0,
    rohr=40.0,
    portal_y=(160.0, 1280.0),   # Portalmitte von hinten bis vorn
    # Kette
    kette_h=35.0,
    kette_b=56.0,
    radius=125.0,               # bis Kettenmitte
    reserve=60.0,               # Zusatzlänge
    kette_innen_x=-6.0,         # Innenkante der Kette (Z-Schlitten fährt bei X links bis 2 mm vor die Schienenmitte)
    # Träger (Stahl 40x20x2, flach) und Rinne (Blech 2 mm)
    traeger_uk=163.0,           # über X-Schalterblock (161)
    traeger_b=40.0,
    traeger_h=20.0,
    rinne_t=2.0,
    rinne_rand=12.0,
    rinne_luft=1.0,
    # Stützen (Stahl 20x20x2) außen am Längsträger, an den Rahmenenden
    stuetze=20.0,
    # Ausleger (Alu-Flachstahl 40x8), am Kettenflansch des linken Winkels
    ausleger_b=40.0,
    ausleger_t=8.0,
    ausleger_y=(-45.0, -5.0),   # ab Portalmitte (= Lasche am Winkel)
    lasche_aussen=-28.0,        # Außenfläche der Lasche am Winkel (x)
    lasche_z=(43.0, 87.0),      # Lasche über Rahmen-OK
    lasche_loecher=[(-35.0, 67.0), (-15.0, 67.0), (-35.0, 79.0), (-15.0, 79.0)],  # (y, z)
    ausleger_luft=2.0,          # zur Rinne
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def geo():
    k_x1 = P["kette_innen_x"]
    k_x0 = k_x1 - P["kette_b"]
    t, rl = P["rinne_t"], P["rinne_luft"]
    r_x0, r_x1 = k_x0 - rl - t, k_x1 + rl + t
    z_rinne = P["traeger_uk"] + P["traeger_h"]
    z_ku = z_rinne + t                                  # Unterkante unteres Trum
    z_mitte_u = z_ku + P["kette_h"] / 2
    z_mitte_o = z_mitte_u + 2 * P["radius"]
    ym0 = P["portal_y"][0] + sum(P["ausleger_y"]) / 2
    ym1 = P["portal_y"][1] + sum(P["ausleger_y"]) / 2
    y_fest = (ym0 + ym1) / 2
    l_eff = (ym1 - ym0) / 2 + P["reserve"]
    a_x1 = r_x0 - P["ausleger_luft"]
    return dict(k_x0=k_x0, k_x1=k_x1, r_x0=r_x0, r_x1=r_x1, z_rinne=z_rinne, z_ku=z_ku,
                z_mu=z_mitte_u, z_mo=z_mitte_o, ym0=ym0, ym1=ym1, y_fest=y_fest, l_eff=l_eff,
                laenge=l_eff + math.pi * P["radius"], a_x1=a_x1, a_x0=a_x1 - P["ausleger_t"])


# ---------------------------------------------------------------- feste Teile
def traeger_rinne():
    g = geo()
    L = P["rahmen_laenge"]
    xm = (g["r_x0"] + g["r_x1"]) / 2
    tb, th = P["traeger_b"], P["traeger_h"]
    tr = box(xm - tb / 2, xm + tb / 2, 0, L, P["traeger_uk"], P["traeger_uk"] + th)
    tr = tr.cut(box(xm - tb / 2 + 2, xm + tb / 2 - 2, -1, L + 1, P["traeger_uk"] + 2,
                    P["traeger_uk"] + th - 2))
    t = P["rinne_t"]
    y0 = g["y_fest"] - 60
    ri = box(g["r_x0"], g["r_x1"], y0, L, g["z_rinne"], g["z_rinne"] + t)
    for x0 in (g["r_x0"], g["r_x1"] - t):
        ri = ri.fuse(box(x0, x0 + t, y0, L, g["z_rinne"], g["z_rinne"] + P["rinne_rand"]))
    return tr, ri.removeSplitter()


def stuetzen():
    s = P["stuetze"]
    g = geo()
    xm = (g["r_x0"] + g["r_x1"]) / 2
    x_aussen = -P["rohr"] / 2                          # Außenfläche Längsträger
    res = None
    for y0 in (0.0, P["rahmen_laenge"] - s):
        # senkrechtes Rohr außen am Längsträger, oben ein Querstück unter den Träger
        st = box(x_aussen - s, x_aussen, y0, y0 + s, -P["rohr"], P["traeger_uk"])
        st = st.cut(box(x_aussen - s + 2, x_aussen - 2, y0 + 2, y0 + s - 2, -P["rohr"] - 1,
                        P["traeger_uk"] + 1))
        q0 = min(xm - P["traeger_b"] / 2, x_aussen - s)
        q1 = max(xm + P["traeger_b"] / 2, x_aussen)
        qu = box(q0, q1, y0, y0 + s, P["traeger_uk"] - s, P["traeger_uk"])
        qu = qu.cut(box(q0 - 1, q1 + 1, y0 + 2, y0 + s - 2, P["traeger_uk"] - s + 2,
                        P["traeger_uk"] - 2))
        st = st.fuse(qu)
        res = st if res is None else res.fuse(st)
    return res.removeSplitter()


# ---------------------------------------------------------------- Ausleger (am Portal)
def ausleger():
    """Drei Alu-Flachstähle 40x8: Fuß an der Lasche, waagerecht nach außen unter der
    Rinne, senkrecht an der Rinne vorbei, oben Platte über dem Kettenende."""
    g = geo()
    y0, y1 = P["ausleger_y"]
    t = P["ausleger_t"]
    la = P["lasche_aussen"]
    z0, z1 = P["lasche_z"]
    fuss = box(la - t, la, y0, y1, z0, z1)
    waag = box(g["a_x0"], la - t + 0.01, y0, y1, z1 - t, z1)
    z_top = g["z_mo"] + P["kette_h"] / 2
    senk = box(g["a_x0"], g["a_x1"], y0, y1, z1 - t + 0.01, z_top + t)
    oben = box(g["a_x1"] - 0.01, g["k_x1"], y0, y1, z_top, z_top + t)
    s = fuss.fuse([waag, senk, oben])
    for y, z in P["lasche_loecher"]:
        s = s.cut(Part.makeCylinder(2.75, t + 2, V(la - t - 1, y, z), V(1, 0, 0)))
    return s.removeSplitter()


# ---------------------------------------------------------------- Kette (je Portallage)
def kette(portal_y):
    """Kette als Körper: unteres Trum (fest) ab Festpunkt, Schlaufe vorn, oberes Trum
    zurück bis zum Ausleger. portal_y = Portalmitte (Rahmen-y)."""
    g = geo()
    ym = portal_y + sum(P["ausleger_y"]) / 2
    y_l = (g["y_fest"] + ym + g["l_eff"]) / 2           # Mitte der Schlaufe
    x0, x1 = g["k_x0"], g["k_x1"]
    h, R = P["kette_h"], P["radius"]
    unten = box(x0, x1, g["y_fest"], y_l, g["z_ku"], g["z_ku"] + h)
    oben = box(x0, x1, ym, y_l, g["z_mo"] - h / 2, g["z_mo"] + h / 2)
    zc = (g["z_mu"] + g["z_mo"]) / 2
    ring = Part.makeCylinder(R + h / 2, x1 - x0, V(x0, y_l, zc), V(1, 0, 0)).cut(
        Part.makeCylinder(R - h / 2, x1 - x0 + 2, V(x0 - 1, y_l, zc), V(1, 0, 0)))
    ring = ring.common(box(x0 - 1, x1 + 1, y_l, y_l + R + h, zc - R - h, zc + R + h))
    return unten.fuse([oben, ring]).removeSplitter()


def main():
    tr, ri = traeger_rinne()
    st = stuetzen()
    au = ausleger()
    pfad = os.path.join(OUT, "energiekette.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "ek_traeger_40x20", tr, "stahl")
    fc_dok.teil(doc, "ek_rinne", ri, "stahl")
    fc_dok.teil(doc, "ek_stuetzen", st, "stahl")
    o = fc_dok.teil(doc, "ek_ausleger", au, "alu")
    o.Placement = App.Placement(V(0, 700, 0), App.Rotation())     # Darstellung in Portalmitte
    k = fc_dok.teil(doc, "Kette_20x38_R125", kette(700.0), "zukauf")
    fc_dok.speichern(doc, pfad, offen)
    for n, s in (("ek_ausleger", au), ("ek_rinne", ri)):
        s.exportStep(os.path.join(OUT, n + ".step"))

    g = geo()
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Kettenlänge ca. %.0f mm (Festpunkt y %.0f, Hub %.0f, R%.0f)\n"
                % (g["laenge"], g["y_fest"], g["ym1"] - g["ym0"], P["radius"]))
        f.write("Rinne x %.1f bis %.1f, Ausleger außen bis x %.1f (ab Schienenmitte links)\n"
                % (g["r_x0"], g["r_x1"], g["a_x0"]))
        f.write("Kette oben bis %.0f mm über Rahmen-OK, Träger-UK %.0f\n"
                % (g["z_mo"] + P["kette_h"] / 2 + P["ausleger_t"], P["traeger_uk"]))


if __name__ == "__main__":
    main()
