# -*- coding: utf-8 -*-
"""
Y-Energiekette, liegend, links (Kastenseite).

Kette 20 x 38 innen, 35 x 56 außen, R125. Die feste Hälfte liegt in einer Rinne
auf einem Träger über dem linken Y-Winkel (höher als alles, was dort am Portal
hochsteht). Der Träger liegt auf zwei Stützen an den Rahmenenden, außen am
Längsträger. Das bewegte Ende sitzt oben auf der Schlaufe; ein Ausleger aus
Alu-Flachmaterial geht von der Kettenlasche des linken Winkels außen an der Rinne
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
import kaufteile as kt  # noqa: E402

P = dict(
    # Maschine (aus Grundrahmen / Y-Winkel)
    rahmen_laenge=1516.0,
    rohr=40.0,
    portal_y=(160.0, 1280.0),   # Portalmitte von hinten bis vorn
    # Kette
    kette_h=35.0,
    kette_b=56.0,
    radius=125.0,               # bis Kettenmitte
    reserve=40.0,               # Zusatzlänge: Schlaufe bleibt hinter der X-Ablage
                                # (dort liegt die X-Ablage), auch wenn das Portal ganz hinten steht
    kette_innen_x=-6.0,         # Innenkante der Kette (Z-Schlitten fährt bei X links bis 2 mm vor die Schienenmitte)
    # Träger (Stahl 40x20x2, flach) und Rinne (Blech 2 mm)
    traeger_uk=163.0,           # über X-Schalterblock (161)
    traeger_b=40.0,
    traeger_h=20.0,
    rinne_t=2.0,
    rinne_rand=12.0,
    rinne_luft=2.5,             # Anschlussstücke sind 60 breit (Kette 56)
    # Anschlussstücke 20x38 (Herstellertabelle): Flansch D = 60, Bohrungen Ø6 im Abstand C = 51
    end_D=60.0,
    end_C=51.0,
    end_F=6.0,
    end_laenge=30.0,
    end_flansch=4.0,
    # Stützen (Stahl 20x20x2) außen am Längsträger, an den Rahmenenden
    stuetze=20.0,
    stuetze_m8_z=[-30.0, -10.0],    # = Grundrahmen ek_stuetze_z
    # Kettenturm (Alu-Flachmaterial 40x8) an der Stirn der links verlängerten Brücke.
    # In der Brücke steckt ein Einsteckteil (Druck), das von den M6 des Sattels
    # mit gehalten wird; der Turm ist mit 4x M6 in dessen Stirnseite geschraubt.
    ausleger_b=40.0,
    ausleger_t=8.0,
    ausleger_y=(-20.0, 20.0),   # ab Portalmitte (= Brückentiefe)
    ausleger_luft=2.0,          # zur Rinne
    bruecke_z=(57.0, 137.0),    # Brücke über Rahmen-OK
    bruecke_wand=4.0,
    bruecke_tiefe=40.0,
    m6_x=[-11.5, 11.5],         # M6 des Sattels (ab Schienenmitte)
    m6_z=[75.0, 95.0],
    einsteck_innen=38.0,        # Einsteckteil reicht bis hier (über die zweite M6)
    turm_loecher=[(-8.0, 80.0), (8.0, 80.0), (-8.0, 118.0), (8.0, 118.0)],  # (y, z)
    einsatz_m6_d=8.0,
    einsatz_m6_tiefe=12.0,

    # X-Energiekette über der Brücke: 20x38 (35x56), R65, liegend auf einer Ablage,
    # die links am Kettenturm und rechts an einer Platte an der rechten Brückenstirn
    # sitzt (Einsteckteil wie links). Bewegtes Ende am Halter auf dem Z-Kopf.
    xk_radius=65.0,
    xk_y_vorn=17.0,             # Vorderkante Kette, Anschlussstück bleibt 1 mm vor dem Halter am Z-Kopf
    xk_traeger_uk=225.0,        # über Y-Kette (unteres Trum bis 220) und X-Motor
    xk_fest_x=20.0,             # Festpunkt links (Rahmen-x)
    xk_halter_dx=-35.0,         # bewegtes Ende links von der Wagenmitte (am Z-Kopf)
    xk_wagen_x=(78.0, 644.0),   # X-Weg Wagenmitte (Rahmen-x)
    xk_reserve=40.0,
    xk_bruecke_rechts_x=720.0,  # rechte Brückenstirn (Rahmen-x)
    # Druckteile am Kettenturm (Turm bleibt ein gerades Alu-Flachmaterial 40 x 8):
    # oben Halter für das bewegte Y-Kettenende, auf Höhe der X-Ablage der Festhalter
    # (festes X-Kettenende + Zapfen für die Ablage), dazwischen Clips für die Leitungen
    hy_dicke=20.0,              # Halter Y über dem Anschlussstück
    hy_y=(-20.0, 32.0),         # nach vorn verlängert: Kabelbinder an der Leitungsbiegung
    einsatz_m5_d=6.4,           # Gewindeeinsatz M5 (Bohrung im Druckteil)
    einsatz_m5_tiefe=10.0,
    turm_x_y=[-14.0, 12.0],     # M5 Turm -> Festhalter (innerhalb der 40 mm Turmbreite)
    leitung_d=16.0,             # Leitungsbündel (Brennerschlauch + Kabel), vereinfacht
    clip_z=[345.0, 380.0],      # Leitungsclips am Turm
    zkopf_hinten_y=28.0,        # Rückseite Z-Kopf-Sockel (X-Wagen-y)
    zkopf_uk=270.0,             # Unterkante Z-Kopf-Sockel (X-Wagen-z)
    xk_halter_loecher=[-45.0, -25.0],   # x der M5-Einsätze in der Z-Kopf-Rückseite
    # Halter X (Druck) mit Bogenkanal: Leitungen treten nach oben aus
    hx_platte=14.0,             # Platte über dem Anschlussstück (Einsätze von unten)
    hx_bogen_r=20.0,            # Kanalmitte
    hx_kanal_h=20.0,            # lichte Höhe = Innenhöhe der Kette
    hx_kanal_b=38.0,            # lichte Breite = Innenbreite der Kette
    hx_wand=4.0,
    hx_strebe=5.0,              # Strebe zwischen Rückwand und Kanalkörper
    m4_einsatz_d=5.6,           # Gewindeeinsatz M4 (Tülle am Austritt)
    m4_einsatz_tiefe=8.0,
    bruecke_uk_x_wagen=57.0,    # Brückenunterkante über Rahmen-OK (X-Wagen z = 0)
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
    y_hinten = ym0 - P["reserve"] / 2 - P["radius"] - P["kette_h"] / 2 - 5   # Rinne/Träger hinten
    return dict(y_hinten=y_hinten, k_x0=k_x0, k_x1=k_x1, r_x0=r_x0, r_x1=r_x1, z_rinne=z_rinne, z_ku=z_ku,
                z_mu=z_mitte_u, z_mo=z_mitte_o, ym0=ym0, ym1=ym1, y_fest=y_fest, l_eff=l_eff,
                laenge=l_eff + math.pi * P["radius"], a_x1=a_x1, a_x0=a_x1 - P["ausleger_t"])


# ---------------------------------------------------------------- feste Teile
def traeger_rinne():
    g = geo()
    L = P["rahmen_laenge"]
    xm = (g["r_x0"] + g["r_x1"]) / 2
    tb, th = P["traeger_b"], P["traeger_h"]
    yh = g["y_hinten"]
    tr = box(xm - tb / 2, xm + tb / 2, yh, L, P["traeger_uk"], P["traeger_uk"] + th)
    tr = tr.cut(box(xm - tb / 2 + 2, xm + tb / 2 - 2, yh - 1, L + 1, P["traeger_uk"] + 2,
                    P["traeger_uk"] + th - 2))
    for y in (P["stuetze"] / 2, L - P["stuetze"] / 2):            # M6 zu den Stützen
        for dx in (-10.0, 10.0):
            tr = tr.cut(Part.makeCylinder(3.3, 4, V(xm + dx, y, P["traeger_uk"] - 1)))   # nur untere Wand
    t = P["rinne_t"]
    y0 = yh                                              # Rinne ganz durch: hinten Schlaufe, vorn Kabel
    ri = box(g["r_x0"], g["r_x1"], y0, L, g["z_rinne"], g["z_rinne"] + t)
    xc = (g["k_x0"] + g["k_x1"]) / 2
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):                  # festes Kettenende, M5
        ri = ri.cut(Part.makeCylinder(2.75, t + 2, V(xc + dx, g["y_fest"], g["z_rinne"] - 1)))
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
        for z in P["stuetze_m8_z"]:                       # M8 quer in den Längsträger
            st = st.cut(Part.makeCylinder(4.5, s + 2, V(x_aussen - s - 1, y0 + s / 2, z), V(1, 0, 0)))
        for dx in (-10.0, 10.0):                           # M6 senkrecht in den Träger
            st = st.cut(Part.makeCylinder(3.3, s + 2, V(xm + dx, y0 + s / 2, P["traeger_uk"] - s - 1)))
        res = st if res is None else res.fuse(st)
    return res.removeSplitter()


# ---------------------------------------------------------------- Kettenturm (am Portal)
def bruecke_ende():
    """x-Lage der verlängerten Brückenstirn (ab Schienenmitte links)."""
    return geo()["a_x1"]


def ausleger():
    """Kettenturm: gerades Alu-Flachmaterial 40 x 8 an der Brückenstirn, ohne Laschen.
    Alles Weitere sitzt an Druckteilen, die mit M5 durch den Turm geschraubt werden."""
    g = geo()
    y0, y1 = P["ausleger_y"]
    t = P["ausleger_t"]
    z_top = g["z_mo"] + P["kette_h"] / 2
    s = box(g["a_x0"], g["a_x1"], y0, y1, P["bruecke_z"][0], z_top + P["hy_dicke"])
    for y, z in P["turm_loecher"]:
        s = s.cut(Part.makeCylinder(3.3, t + 2, V(g["a_x0"] - 1, y, z), V(1, 0, 0)))
    for y, z in turm_m5():
        s = s.cut(Part.makeCylinder(2.75, t + 2, V(g["a_x0"] - 1, y, z), V(1, 0, 0)))
    return s.removeSplitter()


def turm_m5():
    """Alle M5-Durchgänge im Turm (y, z): Halter Y, Clips, Festhalter X."""
    g, gx = geo(), geo_x()
    z_top = g["z_mo"] + P["kette_h"] / 2
    res = [(y, z_top + P["hy_dicke"] / 2) for y in (-10.0, 10.0)]
    res += [(y, z) for z in P["clip_z"] for y in (-8.0, 8.0)]
    res += [(y, festhalter_zm()) for y in P["turm_x_y"]]
    return res


def einsatz_x(x, y, z, richt=1):
    """Bohrung für einen M5-Gewindeeinsatz, quer (x)."""
    d, l = P["einsatz_m5_d"], P["einsatz_m5_tiefe"]
    return Part.makeCylinder(d / 2, l + 1, V(x - richt, y, z), V(richt, 0, 0))


def einsatz_z(x, y, z, richt=1):
    d, l = P["einsatz_m5_d"], P["einsatz_m5_tiefe"]
    return Part.makeCylinder(d / 2, l + 1, V(x, y, z - richt), V(0, 0, richt))


def halter_y():
    """Druckteil oben am Turm: das bewegte Ende der Y-Kette ist von unten mit 2x M5
    in Einsätze geschraubt; seitlich 2x M5 durch den Turm. Vorn zwei Schlitze für
    einen Kabelbinder, der die Leitung an der Biegung nach unten hält."""
    g = geo()
    z0 = g["z_mo"] + P["kette_h"] / 2
    x0, x1 = g["a_x1"], g["k_x1"] + 5
    s = box(x0, x1, P["hy_y"][0], P["hy_y"][1], z0, z0 + P["hy_dicke"])
    xc = (g["k_x0"] + g["k_x1"]) / 2
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):
        s = s.cut(einsatz_z(xc + dx, sum(P["ausleger_y"]) / 2, z0))
    for y in (-10.0, 10.0):
        s = s.cut(einsatz_x(x0, y, z0 + P["hy_dicke"] / 2))
    lx, _ = leitung_bei_y(26.0)
    for dx in (-12.0, 12.0):                                      # Kabelbinder 3,6 breit
        s = s.cut(box(lx + dx - 1.5, lx + dx + 1.5, 23.5, 28.5, z0 - 1, z0 + P["hy_dicke"] + 1))
    return s.removeSplitter()


def festhalter_zm():
    return geo_x()["z_t0"] + (P["traeger_h"] + P["rinne_t"]) / 2


def festhalter_x():
    """Druckteil auf Höhe der X-Ablage, innen am Turm (2x M5 durch den Turm). Trägt
    oben das feste Ende der X-Kette (2x M5 von oben in Einsätze) und hat rechts
    einen Zapfen, auf den die Ablage geschoben wird (2x M5 von unten durch die
    untere Wand). Er ist so breit wie die Rinne und gleicht damit den Versatz
    zwischen Turm (y +-20) und Ablage aus."""
    g, gx = geo(), geo_x()
    x0, x1 = g["a_x1"], ablage_x0()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    z0, h = gx["z_t0"], P["traeger_h"]
    s = box(x0, x1, gx["r_y0"], gx["r_y1"], z0, gx["z_ku"])
    s = s.fuse(box(x1 - 0.01, x1 + 25, ym - 17.8, ym + 17.8, z0 + 2.2, z0 + h - 2.2))
    yc = (gx["y0"] + gx["y1"]) / 2
    for dy in (-P["end_C"] / 2, P["end_C"] / 2):
        s = s.cut(einsatz_z(gx["xf"], yc + dy, gx["z_ku"], -1))
    for y in P["turm_x_y"]:
        s = s.cut(einsatz_x(x0, y, festhalter_zm()))
    for x, y in zapfen_loecher():
        s = s.cut(Part.makeCylinder(P["einsatz_m5_d"] / 2, 9, V(x, y, z0 + 1)))
    return s.removeSplitter()


def ablage_x0():
    """Linkes Ende von X-Ablage und Rinne: hinter dem festen Kettenende."""
    gx = geo_x()
    return gx["xf"] + P["end_laenge"] / 2


def zapfen_loecher():
    gx = geo_x()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    return [(ablage_x0() + 12.5, ym - 10.0), (ablage_x0() + 12.5, ym + 10.0)]


def leitung_weg():
    """Mittellinie des Leitungsbündels vom bewegten Y-Ende (tritt nach vorn aus)
    zum festen X-Ende (tritt nach links ein), ab Schienenmitte links / Portalmitte:
    Geraden mit Bögen, senkrecht durch die Clips vor dem Turm."""
    g, gx = geo(), geo_x()
    xc = (g["k_x0"] + g["k_x1"]) / 2
    e = P["end_laenge"] / 2
    yc = (gx["y0"] + gx["y1"]) / 2
    z_ein = gx["z_ku"] + P["kette_h"] / 2
    xl, yl = -50.0, 34.0                                 # senkrechtes Stück (Clips)
    pts = [V(xc, e + 0.5, g["z_mo"]), V(xc, yl, g["z_mo"]), V(xl, yl, 410.0),
           V(xl, yl, 300.0), V(xl, yc, z_ein), V(gx["xf"] - e - 0.5, yc, z_ein)]
    radien = [16.0, 30.0, 30.0, 20.0]
    kanten, start = [], pts[0]
    for i in range(1, len(pts) - 1):
        a, p, b = pts[i - 1], pts[i], pts[i + 1]
        u = (a - p).normalize()
        w = (b - p).normalize()
        th = math.acos(max(-1.0, min(1.0, u.dot(w))))
        r = radien[i - 1]
        d = r / math.tan(th / 2)
        t1, t2 = p + u * d, p + w * d
        bi = (u + w).normalize()
        c = p + bi * (r / math.sin(th / 2))
        kanten.append(Part.LineSegment(start, t1).toShape())
        kanten.append(Part.Arc(t1, c - bi * r, t2).toShape())
        start = t2
    kanten.append(Part.LineSegment(start, pts[-1]).toShape())
    return Part.Wire(kanten)


def leitung_abtasten(n=200):
    return leitung_weg().discretize(Number=n)


def leitung_bei_y(y):
    pts = leitung_abtasten()
    p = min(pts[:len(pts) // 3], key=lambda q: abs(q.y - y))
    return p.x, p.z


def leitung_bei_z(z):
    pts = [q for q in leitung_abtasten() if 300 < q.z < 410]
    p = min(pts, key=lambda q: abs(q.z - z))
    return p.x, p.y


def leitung():
    """Leitungsbündel als Rohr entlang der Mittellinie (nur Darstellung und Kollision)."""
    w = leitung_weg()
    e0 = w.OrderedEdges[0]
    p0 = e0.valueAt(e0.FirstParameter)
    t0 = e0.tangentAt(e0.FirstParameter)
    kreis = Part.Wire([Part.makeCircle(P["leitung_d"] / 2, p0, t0)])
    return w.makePipeShell([kreis], True, True)


def clips():
    """Leitungsclips (Druck) innen am Turm, je 2x M5 durch den Turm; die Leitung
    wird von vorn eingeklipst."""
    g = geo()
    x0 = g["a_x1"]
    r = P["leitung_d"] / 2 + 0.5
    res = None
    for zc in P["clip_z"]:
        cx, cy = leitung_bei_z(zc)
        c = box(x0, cx + r + 3.5, -16.0, cy + r + 1.5, zc - 8, zc + 8)
        c = c.cut(Part.makeCylinder(r, 18, V(cx, cy, zc - 9)))
        c = c.cut(box(cx - 6.0, cx + 6.0, cy, cy + r + 3, zc - 9, zc + 9))
        for y in (-8.0, 8.0):
            c = c.cut(einsatz_x(x0, y, zc))
        res = c if res is None else res.fuse(c)
    return res


def einsteckteil():
    """Steckt in der Brücke (links), gehalten von den beiden M6 des Sattels;
    Stirnseite mit 4x M6-Einsatz für den Kettenturm."""
    g = geo()
    w, tb = P["bruecke_wand"], P["bruecke_tiefe"]
    za, zb = P["bruecke_z"]
    sp = 0.2
    x0, x1 = g["a_x1"], P["einsteck_innen"]
    s = box(x0, x1, -tb / 2 + w + sp, tb / 2 - w - sp, za + w + sp, zb - w - sp)
    for x in P["m6_x"]:
        for z in P["m6_z"]:
            s = s.cut(Part.makeCylinder(3.3, tb, V(x, -tb / 2, z), V(0, 1, 0)))
    for y, z in P["turm_loecher"]:
        s = s.cut(Part.makeCylinder(P["einsatz_m6_d"] / 2, P["einsatz_m6_tiefe"] + 1,
                                    V(x0 - 1, y, z), V(1, 0, 0)))
    return s.removeSplitter()


# ---------------------------------------------------------------- X-Kette
def geo_x():
    h, b, R = P["kette_h"], P["kette_b"], P["xk_radius"]
    y1 = P["xk_y_vorn"]
    y0 = y1 - b
    t, rl = P["rinne_t"], P["rinne_luft"]
    z_t0 = P["xk_traeger_uk"]
    z_ri = z_t0 + P["traeger_h"]
    z_ku = z_ri + t
    z_mu = z_ku + h / 2
    z_mo = z_mu + 2 * R
    xs = -20.0                                           # Rahmen-x -> x ab Schienenmitte links
    m0 = P["xk_wagen_x"][0] + P["xk_halter_dx"] + xs
    m1 = P["xk_wagen_x"][1] + P["xk_halter_dx"] + xs
    xf = P["xk_fest_x"] + xs
    l_eff = m1 - xf + P["xk_reserve"]
    return dict(y0=y0, y1=y1, z_t0=z_t0, z_ri=z_ri, z_ku=z_ku, z_mu=z_mu, z_mo=z_mo,
                m0=m0, m1=m1, xf=xf, l_eff=l_eff, laenge=l_eff + math.pi * R, xs=xs,
                r_y0=y0 - rl - t, r_y1=y1 + rl + t, x_re=P["xk_bruecke_rechts_x"] + xs)


def stopfen_loecher():
    gx = geo_x()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    zm = gx["z_t0"] + P["traeger_h"] / 2
    return [(-14.0, zm), (0.0, zm)]          # innerhalb der Plattenbreite (y +-20)


def ablage_x():
    """Alu 40x20x2 flach (in y 40 breit) + Rinne, links auf dem Zapfen des Festhalters,
    rechts stumpf an der Platte (Stopfen mit M5-Einsätzen)."""
    gx = geo_x()
    x0 = ablage_x0()
    x1 = gx["x_re"]
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    z0 = gx["z_t0"]
    tr = box(x0, x1, ym - 20, ym + 20, z0, z0 + P["traeger_h"])
    tr = tr.cut(box(x0 - 1, x1 + 1, ym - 18, ym + 18, z0 + 2, z0 + P["traeger_h"] - 2))
    for x, y in zapfen_loecher():                                  # M5 von unten in den Zapfen
        tr = tr.cut(Part.makeCylinder(2.75, 4, V(x, y, z0 - 1)))
    t = P["rinne_t"]
    ri = box(x0, x1, gx["r_y0"], gx["r_y1"], gx["z_ri"], gx["z_ri"] + t)
    for y0 in (gx["r_y0"], gx["r_y1"] - t):
        ri = ri.fuse(box(x0, x1, y0, y0 + t, gx["z_ri"], gx["z_ri"] + P["rinne_rand"]))
    return tr, ri.removeSplitter()


def stopfen_x():
    """Stopfen (Druck) im rechten Ende der X-Ablage, 2x M5-Einsatz längs."""
    gx = geo_x()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    z0 = gx["z_t0"]
    L = 25.0
    res = None
    for xa, richt in ((gx["x_re"], -1),):
        xs0, xs1 = (xa, xa + L) if richt > 0 else (xa - L, xa)
        st = box(xs0, xs1, ym - 17.8, ym + 17.8, z0 + 2.2, z0 + P["traeger_h"] - 2.2)
        for y, z in stopfen_loecher():
            st = st.cut(Part.makeCylinder(3.2, 11, V(xa - richt * 1, y, z), V(richt, 0, 0)))
        res = st if res is None else res.fuse(st)
    return res


def stuetze_x_rechts():
    """Platte (Alu 8 mm) an der rechten Brückenstirn: 4x M6 in das rechte Einsteckteil,
    oben stößt die X-Ablage dagegen (2x M5 in den Stopfen)."""
    gx = geo_x()
    x0 = gx["x_re"]
    t = P["ausleger_t"]
    py0, py1 = P["ausleger_y"]
    s = box(x0, x0 + t, py0, py1, P["bruecke_z"][0], gx["z_t0"] + P["traeger_h"] + 5)
    for y, z in P["turm_loecher"]:
        s = s.cut(Part.makeCylinder(3.3, t + 2, V(x0 - 1, y, z), V(1, 0, 0)))
    for y, z in stopfen_loecher():
        s = s.cut(Part.makeCylinder(2.75, t + 2, V(x0 - 1, y, z), V(1, 0, 0)))
    return s


def einsteckteil_rechts():
    """Wie links, in der rechten Brückenstirn (x ab Schienenmitte links)."""
    gx = geo_x()
    w, tb = P["bruecke_wand"], P["bruecke_tiefe"]
    za, zb = P["bruecke_z"]
    sp = 0.2
    xr = gx["x_re"]
    xm = xr - 20.0                                       # rechte Schienenmitte
    x0 = xm - P["einsteck_innen"]
    s = box(x0, xr, -tb / 2 + w + sp, tb / 2 - w - sp, za + w + sp, zb - w - sp)
    for x in P["m6_x"]:
        for z in P["m6_z"]:
            s = s.cut(Part.makeCylinder(3.3, tb, V(xm + x, -tb / 2, z), V(0, 1, 0)))
    for y, z in P["turm_loecher"]:
        s = s.cut(Part.makeCylinder(P["einsatz_m6_d"] / 2, P["einsatz_m6_tiefe"] + 1,
                                    V(xr + 1, y, z), V(-1, 0, 0)))
    return s.removeSplitter()


def halter_x():
    """Halter für das bewegte Ende der X-Kette (Druck, X-Wagen-Koordinaten):
    Rückwand an der Rückseite des Z-Kopf-Sockels (2x M5 in dessen Einsätze), oben
    eine Platte über dem Anschlussstück (2x M5 von unten in Einsätze). Links ein
    Bogenkanal: die Leitungen treten waagerecht aus dem Anschlussstück aus und
    werden nach oben umgelenkt."""
    gx = geo_x()
    zb = P["bruecke_uk_x_wagen"]
    t = P["ausleger_t"]
    dx = P["xk_halter_dx"]
    yk = P["zkopf_hinten_y"]
    h = P["kette_h"]
    e = P["end_laenge"] / 2
    z_es = gx["z_mo"] - h / 2 - zb                       # Unterkante Anschlussstück
    z_top = z_es + h                                     # Oberkante (Flansch)
    dp = P["hx_platte"]
    xb = dx - e                                          # Austrittsseite des Anschlussstücks
    senk = box(dx - 20, dx + 20, yk - t, yk, P["zkopf_uk"], z_top + dp)
    oben = box(xb - 2, dx + 20, gx["y0"] - 6, yk, z_top, z_top + dp)
    yc = (gx["y0"] + gx["y1"]) / 2
    s = senk.fuse(oben)
    # Bogenkanal: Achse quer (y), Mitte über der Austrittsmitte
    R, kh, kb, w = P["hx_bogen_r"], P["hx_kanal_h"], P["hx_kanal_b"], P["hx_wand"]
    zm = z_es + h / 2
    zc = zm + R
    ky0, ky1 = yc - kb / 2, yc + kb / 2
    ra, ri = R + kh / 2 + w, R - kh / 2 - w
    # Druck kopfüber: Oberseite durchgehend eben (Druckbett), Rückseite (-y) bündig
    # mit der Platte, kein Spalt zwischen Kanal und Platte
    by0, by1 = gx["y0"] - 6, yk
    z_ob = z_top + dp
    quadrant = box(xb - ra - 1, xb, by0 - 1, by1 + 1, zc - ra - 1, zc)
    koerper = Part.makeCylinder(ra, by1 - by0, V(xb, by0, zc), V(0, 1, 0)).common(quadrant)
    koerper = koerper.fuse(box(xb - ra, xb - 2 + 0.01, by0, by1, zc - 0.01, z_ob))
    s = s.fuse(koerper)
    ring = Part.makeCylinder(R + kh / 2, kb, V(xb, ky0, zc), V(0, 1, 0)).cut(
        Part.makeCylinder(R - kh / 2, kb + 2, V(xb, ky0 - 1, zc), V(0, 1, 0)))
    q2 = box(xb - R - kh, xb + 0.5, ky0 - 1, ky1 + 1, zc - R - kh, zc + 0.01)
    s = s.cut(ring.common(q2))
    s = s.cut(box(xb - R - kh / 2, xb - R + kh / 2, ky0, ky1, zc, z_ob + 1))
    for dy in (-P["end_C"] / 2, P["end_C"] / 2):        # Einsatz von unten, oben M5 durch
        s = s.cut(einsatz_z(dx, yc + dy, z_top))
        s = s.cut(Part.makeCylinder(2.75, dp + 2, V(dx, yc + dy, z_top)))
    # Strebe links neben dem Anschlussstück: von der Rückwand unten schräg unter den
    # Kanalkörper, versteift den Winkel zwischen Rückwand und Platte
    rb = P["hx_strebe"]
    zs = zc - math.sqrt(ra ** 2 - (rb / 2) ** 2) + 6      # sicher im Kanalkörper
    pts = [V(xb - rb, yk - t, P["zkopf_uk"] + 2), V(xb - rb, yk - t, zs),
           V(xb - rb, gx["y0"] - 1, zs), V(xb - rb, yk - t, P["zkopf_uk"] + 2)]
    s = s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(rb, 0, 0)))
    s = s.cut(ring.common(q2))                          # Kanal frei halten
    # zwei Gewindeeinsätze M4 neben der Austrittsöffnung (für eine Tülle)
    for y in (ky0 - 8.0, ky1 + 8.0):
        s = s.cut(Part.makeCylinder(P["m4_einsatz_d"] / 2, P["m4_einsatz_tiefe"] + 1,
                                    V(xb - R, y, z_ob - P["m4_einsatz_tiefe"])))
    for x in P["xk_halter_loecher"]:
        s = s.cut(Part.makeCylinder(2.75, t + 2, V(x, yk - t - 1, P["zkopf_uk"] + 10), V(0, 1, 0)))
    return s.removeSplitter()


def endstueck(unten):
    return kt.kette_endstueck(P["kette_h"], P["kette_b"], P["end_D"], P["end_C"], P["end_F"],
                              P["end_laenge"], P["end_flansch"], unten)


def kette_x(wagen_x):
    """X-Kette je Wagenlage (Rahmen-x der Wagenmitte), x ab Schienenmitte links."""
    gx = geo_x()
    xm = wagen_x + P["xk_halter_dx"] + gx["xs"]
    x_l = (gx["xf"] + xm + gx["l_eff"]) / 2
    y0, y1 = gx["y0"], gx["y1"]
    h, R = P["kette_h"], P["xk_radius"]
    e = P["end_laenge"] / 2
    unten = box(gx["xf"] + e, x_l, y0, y1, gx["z_ku"], gx["z_ku"] + h)
    oben = box(xm + e, x_l, y0, y1, gx["z_mo"] - h / 2, gx["z_mo"] + h / 2)
    yc = (y0 + y1) / 2
    for unt, x, z in ((True, gx["xf"], gx["z_ku"]), (False, xm, gx["z_mo"] - h / 2)):
        es = endstueck(unt)
        es.rotate(V(0, 0, 0), V(0, 0, 1), 90)              # Länge entlang X, Breite entlang Y
        es.translate(V(x, yc, z))
        unten = unten.fuse(fc_dok.fest(es))
    zc = (gx["z_mu"] + gx["z_mo"]) / 2
    ring = Part.makeCylinder(R + h / 2, y1 - y0, V(x_l, y0, zc), V(0, 1, 0)).cut(
        Part.makeCylinder(R - h / 2, y1 - y0 + 2, V(x_l, y0 - 1, zc), V(0, 1, 0)))
    ring = ring.common(box(x_l, x_l + R + h, y0 - 1, y1 + 1, zc - R - h, zc + R + h))
    return unten.fuse([oben, ring]).removeSplitter()


# ---------------------------------------------------------------- Kette (je Portallage)
def kette(portal_y):
    """Kette als Körper: unteres Trum (fest) ab Festpunkt nach hinten, Schlaufe hinten,
    oberes Trum nach vorn bis zum Ausleger. Die Kabel verlassen den Festpunkt nach vorn
    (Schaltschrank und Plasmagerät stehen vorn). portal_y = Portalmitte (Rahmen-y)."""
    g = geo()
    ym = portal_y + sum(P["ausleger_y"]) / 2
    y_l = (g["y_fest"] + ym - g["l_eff"]) / 2           # Mitte der Schlaufe (hinten)
    x0, x1 = g["k_x0"], g["k_x1"]
    h, R = P["kette_h"], P["radius"]
    e = P["end_laenge"] / 2
    unten = box(x0, x1, y_l, g["y_fest"] - e, g["z_ku"], g["z_ku"] + h)
    oben = box(x0, x1, y_l, ym - e, g["z_mo"] - h / 2, g["z_mo"] + h / 2)
    xc = (x0 + x1) / 2
    for unt, y, z in ((True, g["y_fest"], g["z_ku"]), (False, ym, g["z_mo"] - h / 2)):
        es = endstueck(unt)
        es.translate(V(xc, y, z))
        unten = unten.fuse(fc_dok.fest(es))
    zc = (g["z_mu"] + g["z_mo"]) / 2
    ring = Part.makeCylinder(R + h / 2, x1 - x0, V(x0, y_l, zc), V(1, 0, 0)).cut(
        Part.makeCylinder(R - h / 2, x1 - x0 + 2, V(x0 - 1, y_l, zc), V(1, 0, 0)))
    ring = ring.common(box(x0 - 1, x1 + 1, y_l - R - h, y_l, zc - R - h, zc + R + h))
    return unten.fuse([oben, ring]).removeSplitter()


def main():
    tr, ri = traeger_rinne()
    st = stuetzen()
    au = ausleger()
    ei = einsteckteil()
    xtr, xri = ablage_x()
    xst = stuetze_x_rechts()
    xpf = halter_x()
    pfad = os.path.join(OUT, "energiekette.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "ek_traeger_40x20", tr, "stahl")
    fc_dok.teil(doc, "ek_rinne", ri, "stahl")
    fc_dok.teil(doc, "ek_stuetzen", st, "stahl")
    portal = {"ek_ausleger": (au, "alu"), "ek_einsteckteil": (ei, "druck"),
              "ek_halter_y": (halter_y(), "druck"), "ekx_festhalter": (festhalter_x(), "druck"),
              "ek_leitungsclips": (clips(), "druck"), "ek_Leitung": (leitung(), "zukauf"),
              "ekx_traeger_40x20": (xtr, "alu"), "ekx_rinne": (xri, "alu"),
              "ekx_stuetze_rechts": (xst, "alu"), "ekx_stopfen": (stopfen_x(), "druck"),
              "ek_einsteckteil_rechts": (einsteckteil_rechts(), "druck")}
    for n, (shp, farbe) in portal.items():
        o = fc_dok.teil(doc, n, shp, farbe)
        o.Placement = App.Placement(V(0, 700, 0), App.Rotation())  # Darstellung in Portalmitte
    o = fc_dok.teil(doc, "ekx_halter", xpf, "druck")
    o.Placement = App.Placement(V(340, 700, 57), App.Rotation())
    fc_dok.teil(doc, "Kette_20x38_R125", kette(700.0), "zukauf")
    k = fc_dok.teil(doc, "Kette_X_20x38_R65", kette_x(360.0), "zukauf")
    k.Placement = App.Placement(V(0, 700, 0), App.Rotation())
    fc_dok.speichern(doc, pfad, offen)
    import Mesh
    for n, s in (("ek_ausleger", au), ("ek_rinne", ri), ("ek_einsteckteil", ei), ("ekx_halter", xpf)):
        s.exportStep(os.path.join(OUT, n + ".step"))
    druck = {"ek_einsteckteil": ei, "ek_einsteckteil_rechts": einsteckteil_rechts(),
             "ek_halter_y": halter_y(), "ekx_festhalter": festhalter_x(),
             "ek_leitungsclips": clips(), "ekx_stopfen": stopfen_x(), "ekx_halter": xpf}
    for n, s in druck.items():
        s.exportStep(os.path.join(OUT, n + ".step"))
        Mesh.Mesh(s.tessellate(0.05)).write(os.path.join(OUT, n + ".stl"))

    g, gx = geo(), geo_x()
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Y-Kette: Länge ca. %.0f mm (Festpunkt y %.0f, Hub %.0f, R%.0f)\n"
                % (g["laenge"], g["y_fest"], g["ym1"] - g["ym0"], P["radius"]))
        f.write("Y-Rinne x %.1f bis %.1f, Kettenturm außen bis x %.1f (ab Schienenmitte links)\n"
                % (g["r_x0"], g["r_x1"], g["a_x0"]))
        f.write("X-Kette: Länge ca. %.0f mm (R%.0f), Ablage-UK %.0f, oben bis %.0f über Rahmen-OK\n"
                % (gx["laenge"], P["xk_radius"], gx["z_t0"], gx["z_mo"] + P["kette_h"] / 2))
        sl = kette_x(P["xk_wagen_x"][1]).BoundBox
        f.write("X-Kette Schlaufe bei X ganz rechts bis Rahmen-x %.1f\n" % (sl.XMax - gx["xs"]))
        fc_dok.schreibe_waende(f, "ek_einsteckteil", ei)
        fc_dok.schreibe_waende(f, "ek_einsteckteil_rechts", einsteckteil_rechts())
        for n, sh in druck.items():
            if n not in ("ek_einsteckteil", "ek_einsteckteil_rechts"):
                fc_dok.schreibe_waende(f, n, sh)
        le = leitung()
        for n, sh in (("Turm", au), ("Clips", clips()), ("Halter Y", halter_y()),
                      ("Festhalter X", festhalter_x()), ("X-Kette", kette_x(P["xk_wagen_x"][0])),
                      ):
            f.write("Leitung / %s: %.2f mm³\n" % (n, le.common(sh).Volume))
        f.write("Leitung: Länge ca. %.0f mm (Mittellinie)\n" % leitung_weg().Length)


if __name__ == "__main__":
    main()
