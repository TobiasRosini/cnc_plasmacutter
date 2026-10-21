# -*- coding: utf-8 -*-
"""
Y-Portalwinkel: verbindet die Portalbrücke (Alu-Rechteckrohr 80x40x4, 80 hoch) mit
zwei HGH15-Wagen einer Y-Schiene.

Aufbau (von unten nach oben):
  HGR15-Schiene -> 2x HGH15CA-Wagen -> Alu-Flachstange 40x15 (gesenkte
  ISO-4762-Schrauben M4) -> 3D-gedruckter Winkel (M5 in Gewinde der
  Flachstange) -> Brücke im Sattel (2x M6 quer durch).
  Riemen HTD5M/15 genau über der Schienenmitte: Obertrum (Zähne unten) an
  zwei Türmen an den Enden geklemmt, -Y Zahnprofil fest, +Y Spannschlitten
  in Schwalbenschwanznut; Rücktrum läuft durch einen Tunnel unten im
  Winkel über die Flachstange. Kein seitlicher Riemenflansch mehr.
  Zwei Varianten (vorn = +Y, dort zeigen die Y-Spannschrauben hin):
  - "fest" (rechts, wie modelliert, +X außen)
  - "kasten" (links, gespiegelt): Lasche Y-Energiekette außen, Anschluss
    X-Energiekette hinten. Der Anschlusskasten ist noch offen.
  X-Antrieb als Omega auf dem X-Wagen: Der X-Riemen (hochkant, Zähne zur
  Brücke) ist hinten an beiden Sätteln geklemmt (Zahnprofil in der
  Sattelrückwand, flache Klemmplatte mit 4x M4 in Gewindeeinsätze).

Koordinaten: Ursprung = Mitte Flachstange, Unterseite (= Oberkante Wagen).
  Y = Schienenrichtung, +X = außen (vom Tisch weg), Z = oben.

Aufruf:
  python3 cad/live.py cad/y_portalwinkel/y_portalwinkel.py
Erzeugt im selben Ordner: FCStd, STEP, STL, Bohrschablone (SVG).
"""
import os
import sys
import math
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
ABSTAND = 300.0     # Darstellung im Teile-Dokument: linker Winkel (kasten) bei x = -ABSTAND
sys.path.insert(0, os.path.dirname(OUT))
import fc_dok  # noqa: E402

# ---------------------------------------------------------------- Parameter
P = dict(
    # HGH15CA-Wagen (HIWIN-Katalog / gängige Nachbauten)
    wagen_breite=34.0,
    wagen_laenge=61.4,
    wagen_lochbild_x=26.0,      # quer
    wagen_lochbild_y=26.0,      # längs
    wagen_gewinde_tiefe=5.0,    # M4 x 5
    wagen_hoehe=28.0,           # Schienenunterkante bis Wagenoberkante
    wagen_h1=4.3,               # Schienenunterkante bis Wagenunterkante
    schiene_breite=15.0,
    schiene_hoehe=15.0,
    wagen_abstand=110.0,        # Mitte-Mitte der beiden Wagen

    # Alu-Flachstange 40 x 15
    fl_breite=40.0,
    fl_dicke=15.0,
    fl_laenge=180.0,
    m4_durchgang=4.5,
    m4_senk_d=8.0,              # Kopf ISO 4762 M4 = 7 mm
    m4_senk_tiefe=7.5,          # -> M4x12: 7,5 Klemmlänge + 4,5 Einschraubtiefe
    m5_kern=4.2,
    m5_gewinde_tiefe=12.0,

    # Druckteil
    basis_dicke=14.0,
    m5_durchgang=5.5,
    m5_senk_d=9.5,
    m5_senk_tiefe=5.0,          # -> M5x18 (9 Druckteil + 9 im Alu)
    basis_m4=[(13.25, 10.0)],   # Basis zur Flachstange im Sattelboden, M4 (x, y), gespiegelt
    m4_kern=3.3,
    m4_basis_senk_tiefe=4.0,    # Senkung in der 14er-Basis, Boden über dem Tunnel
    m4_basis_senk_d=7.5,        # Kopf ISO 4762 M4 = 7 mm

    # Brücke 80 x 40 x 4, 80 hoch, 40 tief (Y)
    br_breite=40.0,
    br_hoehe=80.0,
    br_wand=4.0,
    br_spiel=0.4,               # Spiel im Sattel (Druckteil)
    sattel_wand=10.0,
    m6_durchgang=6.4,
    m6_senk_d=11.0,
    m6_senk_tiefe=4.0,
    m6_mutter_sw=10.2,          # SW10 + Druckspiel
    m6_mutter_tiefe=5.0,
    m6_x=[-11.5, 11.5],
    m6_z=[18.0, 38.0],          # über Basisoberkante (oben frei für X-Riemenklemme)

    rippe_dicke=5.0,

    # Riemen HTD5M / 15 mm über der Schienenmitte
    riemen_breite=15.0,
    riemen_dicke=3.8,
    riemen_teilung=5.0,
    zahn_hoehe=2.1,             # -> Riemenrücken 1,7 mm
    zahn_breite=3.3,            # Lückenbreite inkl. Spiel
    nut_breite=15.6,            # Riemenkanal
    nut_tiefe=1.0,              # Riemenrücken steht 0,7 mm über -> Klemmplatte presst
    scheibe_zaehne=24,          # Teilkreis = Abstand Obertrum/Rücktrum
    tunnel_breite=16.0,         # Rücktrum durch die Basis
    tunnel_hoehe=9.0,
    ruecktrum_luft=2.0,         # Riemen über Flachstange
    turm_breite=52.0,           # Türme an den Enden (steht 6 mm über die Flachstange)

    # Festes Ende (-Y): eingeprägtes Zahnprofil, Klemmplatte mit 4x M5x60
    # durch Turm und Basis in die Flachstange
    fest_y=(-90.0, -50.0),
    klemm_x=13.5,
    klemm_y=[-84.0, -56.0],
    klemm_platte_dicke=6.0,
    m5_mutter_sw=8.2,
    m5_mutter_tiefe=4.5,

    # Spannende (+Y): Schwalbenschwanznut 60°, nach außen offen. Spannschraube
    # M5 (Sechskant) auf Zug: Kopf liegt verdrehsicher im Widerlager am Sattel,
    # gespannt wird mit der Mutter hinter der Lasche der Schlitten-Klemmplatte.
    sw_oeffnung=36.0,           # Breite oben
    sw_tiefe=7.0,
    sw_winkel=60.0,             # Flankenwinkel zur Waagerechten
    spiel=0.3,
    schl_laenge=24.0,
    spannweg=20.0,              # reicht er nicht, Schlitten zahnweise versetzt neu einschieben
    schl_lage=0.5,              # Lage im Modell: 0 = ganz außen (entspannt), 1 = ganz innen
    schl_schraube_x=12.5,       # 4x M3 Klemmplatte auf dem Schlitten
    schl_schraube_y=5.0,
    m3_durchgang=3.4,
    m3_mutter_sw=5.7,
    m3_mutter_tiefe=2.6,
    schl_platte_dicke=5.0,
    lasche_dicke=6.0,           # Lasche an der Schlitten-Klemmplatte
    lasche_hoehe=18.0,          # über Turmoberkante
    spann_z=11.0,               # Achse Spannschraube über Turmoberkante
    widerlager_dicke=8.0,
    widerlager_breite=18.0,
    widerlager_spalt=1.0,       # Lasche/Widerlager bei voll gespanntem Schlitten
    m5_kopf_sw=8.2,             # Sechskantschraube M5 (SW8)
    m5_kopf_hoehe=3.8,

    # Befestigungsflansch Energiekette (Halter folgt als eigenes Teil).
    # Sitzt außen auf jedem Winkel, damit links und rechts dasselbe Teil passt.
    ek_flansch=True,            # nur Variante "kasten"
    ek_dicke=8.0,
    ek_hoehe=30.0,              # über Basisoberkante
    ek_y=(-45.0, -5.0),
    ek_loecher=[(-35.0, 10.0), (-15.0, 10.0), (-35.0, 22.0), (-15.0, 22.0)],  # (y, z über OK)

    # X-Riemen (Omega auf dem X-Wagen): Enden hinten an den Sätteln geklemmt
    x_riemen_z=61.0,            # Mitte X-Riemen (hochkant) über Basisoberkante
    xk_hoehe=36.0,              # Klemmplatte senkrecht
    xk_dicke=6.0,
    xk_einsatz_x=15.0,          # 4x M3-Gewindeeinsatz in der Sattelrückwand
    xk_einsatz_dz=13.0,         # über/unter Riemenmitte
    xk_zaehne=4,                # Zahnlücken in der Rückwand (mittig, zwischen den Einsätzen)
    einsatz_m3_d=4.0,
    einsatz_m3_tiefe=6.0,
    einsatz_m4_d=5.6,
    einsatz_m4_tiefe=8.0,
    # X-Energiekette hinten an der Sattelrückwand (nur kasten): 2x M5 unten
    xek_loecher=[(-10.0, 4.0), (10.0, 4.0)],   # (x, z über Basis), unter den M6-Senkungen
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def zyl(d, h, x, y, z, richtung=V(0, 0, 1)):
    return Part.makeCylinder(d / 2.0, h, V(x, y, z), richtung)


def sechskant(sw, h, x, y, z, richtung=V(0, 0, 1)):
    """Sechskanttasche, Schlüsselweite sw, Achse in 'richtung'."""
    r = sw / math.sqrt(3)
    pts = [V(r * math.cos(math.radians(30 + 60 * i)),
             r * math.sin(math.radians(30 + 60 * i)), 0) for i in range(7)]
    prisma = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))
    rot = App.Rotation(V(0, 0, 1), richtung)
    prisma.Placement = App.Placement(V(x, y, z), rot)
    return prisma


def gespiegelt(xy):
    x, y = xy
    return {(sx * x, sy * y) for sx in (-1, 1) for sy in (-1, 1)}


def wagen_mitten():
    a = P["wagen_abstand"] / 2.0
    return [-a, a]


def wagen_schrauben():
    pts = []
    for yc in wagen_mitten():
        for sx in (-1, 1):
            for sy in (-1, 1):
                pts.append((sx * P["wagen_lochbild_x"] / 2,
                            yc + sy * P["wagen_lochbild_y"] / 2))
    return pts


def m4_basis_punkte():
    s = set()
    for xy in P["basis_m4"]:
        s |= gespiegelt(xy)
    return sorted(s)


def m5_punkte():
    """M5-Gewinde in der Flachstange (Klemmschrauben festes Ende)."""
    return sorted(klemm_punkte())


# ---------------------------------------------------------------- Flachstange
def flachstange():
    b, t, l = P["fl_breite"], P["fl_dicke"], P["fl_laenge"]
    s = box(-b / 2, b / 2, -l / 2, l / 2, 0, t)
    for x, y in wagen_schrauben():
        s = s.cut(zyl(P["m4_durchgang"], t + 2, x, y, -1))
        s = s.cut(zyl(P["m4_senk_d"], P["m4_senk_tiefe"] + 1,
                      x, y, t - P["m4_senk_tiefe"]))
    for x, y in m5_punkte():
        s = s.cut(zyl(P["m5_kern"], P["m5_gewinde_tiefe"] + 1,
                      x, y, t - P["m5_gewinde_tiefe"]))
    for x, y in m4_basis_punkte():
        s = s.cut(zyl(P["m4_kern"], 11, x, y, t - 10))
    return s


# ---------------------------------------------------------------- Druckteil
def z_basis():
    return P["fl_dicke"] + P["basis_dicke"]


def z_ruecktrum():
    """Unterkante Rücktrum (Rücken unten, Zähne oben)."""
    return P["fl_dicke"] + P["ruecktrum_luft"]


def z_kanal():
    """Kanalboden Obertrum = Teilkreislinie (Riemenrücken liegt darauf)."""
    rueck = P["riemen_dicke"] - P["zahn_hoehe"]
    teilkreis = P["scheibe_zaehne"] * P["riemen_teilung"] / math.pi
    return z_ruecktrum() + rueck + teilkreis


def z_turm():
    return z_kanal() + P["nut_tiefe"]


def sattel_y():
    ci = P["br_breite"] / 2 + P["br_spiel"] / 2
    return ci, ci + P["sattel_wand"]


def winkel(variante="fest"):
    """variante 'fest' oder 'kasten'; beide in Lage +X außen (kasten wird danach gespiegelt)."""
    b, l = P["fl_breite"], P["fl_laenge"]
    z0, z1 = P["fl_dicke"], z_basis()
    zt = z_turm()
    tb = P["turm_breite"] / 2
    ci, co = sattel_y()

    # Basis, flache Unterseite = Druckbett
    s = box(-b / 2, b / 2, -l / 2, l / 2, z0, z1)

    # Sattel
    zs = z1 + P["br_hoehe"]
    s = s.fuse(box(-b / 2, b / 2, -co, -ci, z1, zs))
    s = s.fuse(box(-b / 2, b / 2, ci, co, z1, zs))

    # Mittelrippe zur festen Seite (die Spannseite ist durchgehend Turm):
    # vom Sattel (unter der X-Riemenklemme) schräg bis an die Innenkante des
    # festen Turms, unterhalb des Riemenkanals
    rd = P["rippe_dicke"]
    yf = P["fest_y"][1]
    zr_oben = x_geo()["zr"] - P["xk_hoehe"] / 2 - 2      # unter der X-Riemenklemme
    pts = [V(-rd / 2, -co, z1), V(-rd / 2, -co, zr_oben),
           V(-rd / 2, yf, z_kanal() - 0.5), V(-rd / 2, yf, z1), V(-rd / 2, -co, z1)]
    s = s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(rd, 0, 0)))

    # Türme: fest (-Y) und Spannseite (+Y, bis an den Sattel)
    s = s.fuse(box(-tb, tb, P["fest_y"][0], P["fest_y"][1], z0, zt))
    s = s.fuse(box(-tb, tb, co - 0.01, l / 2, z0, zt))

    # Widerlager am Sattel für die Spannschraube
    wb = P["widerlager_breite"] / 2
    yw0, yw1 = widerlager_y()
    s = s.fuse(box(-wb, wb, yw0 - 0.01, yw1, zt - 0.01, zt + P["lasche_hoehe"]))

    # Riemenkanal auf beiden Türmen, Zahnprofil am festen Ende
    nb = P["nut_breite"] / 2
    s = s.cut(box(-nb, nb, -l / 2 - 1, P["fest_y"][1] + 0.01, z_kanal(), zt + 1))
    s = s.cut(box(-nb, nb, co, l / 2 + 1, z_kanal(), zt + 1))
    s = s.cut(zahnluecken(0, P["fest_y"][0] - 1, P["fest_y"][1], z_kanal()))

    # Tunnel für das Rücktrum
    tw = P["tunnel_breite"] / 2
    s = s.cut(box(-tw, tw, -l / 2 - 1, l / 2 + 1, z0 - 1, z0 + P["tunnel_hoehe"]))

    # M4 Basis zur Flachstange im Sattelboden, gesenkt (vor der Brücke montieren)
    for x, y in m4_basis_punkte():
        s = s.cut(zyl(P["m4_durchgang"], P["basis_dicke"] + 2, x, y, z0 - 1))
        s = s.cut(zyl(P["m4_basis_senk_d"], P["m4_basis_senk_tiefe"] + 1,
                      x, y, z1 - P["m4_basis_senk_tiefe"]))

    # Klemmschrauben festes Ende: durch Turm und Basis
    for x, y in klemm_punkte():
        s = s.cut(zyl(P["m5_durchgang"], zt - z0 + 2, x, y, z0 - 1))

    # Kein Zugang zu den M4-Wagenschrauben: erst Flachstange auf die Wagen,
    # dann den Winkel aufsetzen (Zugangslöcher hätten den Tunnel angeschnitten)

    # M6 quer durch Sattel und Brücke: Kopf bei -Y, Mutter bei +Y
    for x, zz in [(x, zz) for x in P["m6_x"] for zz in P["m6_z"]]:
        zm = z1 + zz
        s = s.cut(zyl(P["m6_durchgang"], 2 * co + 2, x, -co - 1, zm, V(0, 1, 0)))
        s = s.cut(zyl(P["m6_senk_d"], P["m6_senk_tiefe"] + 1,
                      x, -co - 1, zm, V(0, 1, 0)))
        s = s.cut(sechskant(P["m6_mutter_sw"], P["m6_mutter_tiefe"] + 1,
                            x, co + 1, zm, V(0, -1, 0)))

    # Spannseite: Schwalbenschwanznut, nach außen offen
    t = P["sw_tiefe"]
    s = s.cut(schwalbe(0, P["sw_oeffnung"], t + 1, sw_start_y(), l / 2 + 1, zt - t))

    # Spannschraube: Schaftschlitz + Kopftasche von oben (Kopf verdrehsicher)
    za = zt + P["spann_z"]
    s = s.cut(box(-P["m5_durchgang"] / 2, P["m5_durchgang"] / 2, yw0 - 1, yw1 + 1,
                  za, zt + P["lasche_hoehe"] + 1))
    s = s.cut(zyl(P["m5_durchgang"], yw1 - yw0 + 2, 0, yw0 - 1, za, V(0, 1, 0)))
    kh = P["m5_kopf_sw"] / 2
    s = s.cut(box(-kh, kh, yw0, yw0 + P["m5_kopf_hoehe"],
                  za - P["m5_kopf_sw"] / math.sqrt(3) - 0.2, zt + P["lasche_hoehe"] + 1))

    # Befestigungsflansch Energiekette: senkrechte Lasche außen an der Basis
    if P["ek_flansch"] and variante == "kasten":
        xi = b / 2
        xa = xi + P["ek_dicke"]
        ya, yb = P["ek_y"]
        s = s.fuse(box(xi, xa, ya, yb, z0, z1 + P["ek_hoehe"]))
        for y, z in P["ek_loecher"]:
            s = s.cut(zyl(P["m5_durchgang"], P["ek_dicke"] + 2, xi - 1, y, z1 + z,
                          V(1, 0, 0)))
            s = s.cut(sechskant(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 1,
                                xi - 1, y, z1 + z, V(1, 0, 0)))
    # X-Riemenklemme: Zahnprofil in der Sattelrückwand, Gewindeeinsätze
    s = s.cut(x_klemm_bohrungen(variante))
    return s.removeSplitter()


def x_geo():
    """X-Riemen hinten an der Brücke (lokale Koordinaten, +Y vorn)."""
    z1 = z_basis()
    yw = -sattel_y()[1]                       # Außenfläche Sattelrückwand
    rueck = P["riemen_dicke"] - P["zahn_hoehe"]
    return dict(zr=z1 + P["x_riemen_z"], yw=yw,
                y_rueck=yw - rueck,             # Riemenrücken (hinten)
                y_mitte=yw + P["zahn_hoehe"] - P["riemen_dicke"] / 2)


def x_klemm_bohrungen(variante):
    g = x_geo()
    res = []
    hb = P["riemen_breite"] / 2 + 1
    # Zahnlücken senkrecht in der Rückwand über die Sattelbreite
    w, h = P["zahn_breite"], P["zahn_hoehe"] + 0.1
    n = P["xk_zaehne"]
    for i in range(n):
        x = (i - (n - 1) / 2) * P["riemen_teilung"]
        res.append(box(x - w / 2, x + w / 2, g["yw"] - 0.01, g["yw"] + h - w / 2,
                       g["zr"] - hb, g["zr"] + hb))
        res.append(zyl(w, 2 * hb, x, g["yw"] + h - w / 2, g["zr"] - hb))
    for sx in (-1, 1):
        for sz in (-1, 1):
            res.append(zyl(P["einsatz_m3_d"], P["einsatz_m3_tiefe"] + 1,
                           sx * P["xk_einsatz_x"], g["yw"] - 1,
                           g["zr"] + sz * P["xk_einsatz_dz"], V(0, 1, 0)))
    if variante == "kasten":
        z1 = z_basis()
        for x, z in P["xek_loecher"]:
            res.append(zyl(P["einsatz_m4_d"], P["einsatz_m4_tiefe"] + 1, x, g["yw"] - 1,
                           z1 + z, V(0, 1, 0)))
    return Part.makeCompound(res)


def x_klemmplatte():
    """Flache Klemmplatte für das X-Riemenende (rechts wie modelliert)."""
    g = x_geo()
    b = P["fl_breite"] / 2
    y1 = g["y_rueck"] + 0.5                    # 0,5 mm Klemmweg
    s = box(-b, b, y1 - P["xk_dicke"], y1, g["zr"] - P["xk_hoehe"] / 2,
            g["zr"] + P["xk_hoehe"] / 2)
    for sx in (-1, 1):
        for sz in (-1, 1):
            s = s.cut(zyl(P["m3_durchgang"], P["xk_dicke"] + 2, sx * P["xk_einsatz_x"],
                          y1 - P["xk_dicke"] - 1,
                          g["zr"] + sz * P["xk_einsatz_dz"], V(0, 1, 0)))
    return s


def schl_mitte(lage=None):
    """Schlittenmitte in Y. lage 0 = ganz außen (entspannt), 1 = ganz innen."""
    lage = P["schl_lage"] if lage is None else lage
    yi = widerlager_y()[1] + P["widerlager_spalt"] + P["lasche_dicke"] \
        + platte_laenge() / 2
    return yi + (1 - lage) * P["spannweg"]


def platte_laenge():
    return P["schl_schraube_y"] * 2 + 12


def widerlager_y():
    """Widerlager direkt am Sattel (+Y)."""
    co = sattel_y()[1]
    return co, co + P["widerlager_dicke"]


def sw_start_y():
    return schl_mitte(1.0) - P["schl_laenge"] / 2 - 2


def klemm_punkte():
    return [(sx * P["klemm_x"], y) for sx in (-1, 1) for y in P["klemm_y"]]


def zahnluecken(xr, ya, yb, z_boden):
    """Zahnlücken (HTD) quer zum Riemen (Zähne zeigen nach unten), y von ya bis yb."""
    w, h = P["zahn_breite"], P["zahn_hoehe"] + 0.1
    r = w / 2
    lb = P["nut_breite"]
    res = None
    n = int((yb - ya) // P["riemen_teilung"])
    for i in range(n):
        y = ya + P["riemen_teilung"] * (i + 0.5)
        g = box(xr - lb / 2, xr + lb / 2, y - w / 2, y + w / 2,
                z_boden - h + r, z_boden + 0.01)
        g = g.fuse(zyl(w, lb, xr - lb / 2, y, z_boden - h + r, V(1, 0, 0)))
        res = g if res is None else res.fuse(g)
    return res


def schwalbe(xr, oben, tiefe, ya, yb, z_unten):
    """Schwalbenschwanz-Querschnitt (unten breiter), extrudiert in Y."""
    k = 1 / math.tan(math.radians(P["sw_winkel"]))
    tiefe_echt = min(tiefe, P["sw_tiefe"])
    ub = oben + 2 * tiefe_echt * k
    zt = z_unten + tiefe_echt
    pts = [V(xr - ub / 2, ya, z_unten), V(xr + ub / 2, ya, z_unten),
           V(xr + oben / 2, ya, zt), V(xr - oben / 2, ya, zt), V(xr - ub / 2, ya, z_unten)]
    prof = Part.Face(Part.makePolygon(pts)).extrude(V(0, yb - ya, 0))
    if tiefe > tiefe_echt:   # Überstand nach oben, damit der Schnitt sauber durchgeht
        prof = prof.fuse(box(xr - oben / 2, xr + oben / 2, ya, yb, zt - 0.01,
                             zt + tiefe - tiefe_echt))
    return prof


# ---------------------------------------------------------------- Kleinteile (Druck)
def spannschlitten():
    """In Montagelage (Mitte bei schl_mitte()). Druck: Unterseite aufs Bett."""
    zt = z_turm()
    sp, t = P["spiel"], P["sw_tiefe"]
    k = 1 / math.tan(math.radians(P["sw_winkel"]))
    h = t - sp
    zu = zt - h
    ob = P["sw_oeffnung"] - 2 * sp
    ub = ob + 2 * h * k
    yc, L = schl_mitte(), P["schl_laenge"]
    pts = [V(-ub / 2, yc - L / 2, zu), V(ub / 2, yc - L / 2, zu),
           V(ob / 2, yc - L / 2, zt), V(-ob / 2, yc - L / 2, zt),
           V(-ub / 2, yc - L / 2, zu)]
    s = Part.Face(Part.makePolygon(pts)).extrude(V(0, L, 0))
    s = s.cut(box(-P["nut_breite"] / 2, P["nut_breite"] / 2,
                  yc - L, yc + L, z_kanal(), zt + 1))
    s = s.cut(zahnluecken(0, yc - L / 2 - 1, yc + L / 2 + 1, z_kanal()))
    for x, y in schl_punkte():
        s = s.cut(zyl(P["m3_durchgang"], h + 2, x, y, zu - 1))
        s = s.cut(sechskant(P["m3_mutter_sw"], P["m3_mutter_tiefe"] + 1, x, y, zu - 1))
    return s.removeSplitter()


def schl_punkte():
    yc = schl_mitte()
    return [(sx * P["schl_schraube_x"], yc + sy * P["schl_schraube_y"])
            for sx in (-1, 1) for sy in (-1, 1)]


def klemmplatte_fest():
    z = z_turm() + 0.7    # auf dem Riemenrücken
    bx = P["turm_breite"] - 4
    ya, yb = P["fest_y"]
    s = box(-bx / 2, bx / 2, ya, yb, z, z + P["klemm_platte_dicke"])
    for x, y in klemm_punkte():
        s = s.cut(zyl(P["m5_durchgang"], 20, x, y, z - 1))
    return s


def klemmplatte_schlitten():
    yc = schl_mitte()
    zt = z_turm()
    z = zt + 0.7
    bx = P["sw_oeffnung"] - 2 * P["spiel"]
    L = platte_laenge()
    s = box(-bx / 2, bx / 2, yc - L / 2, yc + L / 2, z, z + P["schl_platte_dicke"])
    # Lasche innen (-Y), glatte Bohrung; Spannmutter sitzt außen (+Y) davor
    ya = yc - L / 2 - P["lasche_dicke"]
    s = s.fuse(box(-bx / 2, bx / 2, ya, yc - L / 2 + 0.01, z, zt + P["lasche_hoehe"]))
    s = s.cut(zyl(P["m5_durchgang"], P["lasche_dicke"] + 2, 0, ya - 1,
                  zt + P["spann_z"], V(0, 1, 0)))
    for x, y in schl_punkte():
        s = s.cut(zyl(P["m3_durchgang"], 20, x, y, z - 1))
    return s.removeSplitter()


# ---------------------------------------------------------------- Dummies
def dummies():
    d = {}
    wb, wl = P["wagen_breite"], P["wagen_laenge"]
    zw0 = -(P["wagen_hoehe"] - P["wagen_h1"])
    zs0 = -P["wagen_hoehe"]
    sb = P["schiene_breite"]
    w = None
    for yc in wagen_mitten():
        k = box(-wb / 2, wb / 2, yc - wl / 2, yc + wl / 2, zw0, 0)
        k = k.cut(box(-sb / 2 - 0.5, sb / 2 + 0.5, yc - wl, yc + wl,
                      zw0 - 1, zs0 + P["schiene_hoehe"]))
        w = k if w is None else w.fuse(k)
    d["Wagen_HGH15CA"] = w
    d["Schiene_HGR15"] = box(-sb / 2, sb / 2, -150, 150, zs0,
                             zs0 + P["schiene_hoehe"])
    z1 = z_basis()
    bb, bh, bw = P["br_breite"], P["br_hoehe"], P["br_wand"]
    xl = -ABSTAND - P["fl_breite"] / 2
    br = box(xl, P["fl_breite"] / 2, -bb / 2, bb / 2, z1, z1 + bh)
    br = br.cut(box(xl - 1, P["fl_breite"] / 2 + 1, -bb / 2 + bw, bb / 2 - bw,
                    z1 + bw, z1 + bh - bw))
    d["Bruecke_80x40x4"] = br
    rb = P["riemen_breite"] / 2
    rueck = P["riemen_dicke"] - P["zahn_hoehe"]
    zk = z_kanal()
    # Obertrum: zwei Enden auf den Türmen (nur Riemenrücken dargestellt)
    ob = box(-rb, rb, -160, P["fest_y"][1], zk, zk + rueck)
    ob = ob.fuse(box(-rb, rb, schl_mitte() - P["schl_laenge"] / 2, 160, zk, zk + rueck))
    d["Riemen_HTD5M_15"] = ob
    # Rücktrum durch den Tunnel
    zu = z_ruecktrum()
    d["Riemen_Ruecktrum"] = box(-rb, rb, -160, 160, zu, zu + P["riemen_dicke"])
    return d


# ---------------------------------------------------------------- Bohrschablone
def bohrschablone():
    """Flachstange 1:1 von oben, A4 quer. Mit 100 % / 'tatsächliche Größe' drucken."""
    b, l = P["fl_breite"], P["fl_laenge"]
    W, H = 297, 210
    ox, oy = (W - l) / 2, 70       # linke obere Ecke der Stange
    L = []
    L.append('<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" '
             'viewBox="0 0 297 210" font-family="sans-serif">')
    L.append('<rect width="297" height="210" fill="white"/>')
    L.append(f'<text x="{ox}" y="25" font-size="6">Bohrschablone Flachstange 40x15x{l:.0f} (Y-Portalwinkel) – Maßstab 1:1</text>')
    L.append(f'<text x="{ox}" y="33" font-size="3.5">Ohne Skalierung drucken. Kontrollmaß: Strich unten muss 100 mm lang sein. Ansicht von oben (Senkseite).</text>')
    L.append(f'<rect x="{ox}" y="{oy}" width="{l}" height="{b}" fill="none" stroke="black" stroke-width="0.3"/>')

    def punkt(x, y, d, farbe, txt):
        # Modell: y entlang Länge -> SVG x; Modell x (+außen) -> SVG nach oben
        sx, sy = ox + l / 2 + y, oy + b / 2 - x
        L.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{d/2:.2f}" fill="none" stroke="{farbe}" stroke-width="0.25"/>')
        L.append(f'<line x1="{sx-3:.2f}" y1="{sy:.2f}" x2="{sx+3:.2f}" y2="{sy:.2f}" stroke="black" stroke-width="0.15"/>')
        L.append(f'<line x1="{sx:.2f}" y1="{sy-3:.2f}" x2="{sx:.2f}" y2="{sy+3:.2f}" stroke="black" stroke-width="0.15"/>')
        return sx, sy

    for x, y in wagen_schrauben():
        punkt(x, y, P["m4_senk_d"], "blue", "")
    for x, y in m5_punkte():
        punkt(x, y, P["m5_kern"], "red", "")
    for x, y in m4_basis_punkte():
        punkt(x, y, P["m4_kern"], "green", "")
    L.append(f'<text x="{ox}" y="{oy+b+10}" font-size="3.5" fill="blue">blau: 8x Ø4,5 durch, Senkung Ø8 x 7,5 tief (ISO 4762 M4x12) – Wagen HGH15CA</text>')
    L.append(f'<text x="{ox}" y="{oy+b+16}" font-size="3.5" fill="red">rot: 4x M5, Kernloch Ø4,2 x 12 tief – Riemenklemmung festes Ende; grün: 4x M4, Kernloch Ø3,3 x 10 tief – Winkel</text>')
    L.append(f'<text x="{ox}" y="{oy-3}" font-size="3">Außenseite (+X, Energiekette)</text>')
    L.append(f'<line x1="{ox}" y1="{oy+b+28}" x2="{ox+100}" y2="{oy+b+28}" stroke="black" stroke-width="0.4"/>')
    L.append(f'<text x="{ox}" y="{oy+b+34}" font-size="3">100 mm</text>')
    # Bemaßung als Koordinatenliste
    yy = oy + b + 44
    L.append(f'<text x="{ox}" y="{yy}" font-size="3">Koordinaten ab Stangenmitte (Länge / Breite), mm: '
             f'M4: ±{P["wagen_abstand"]/2 - P["wagen_lochbild_y"]/2:.0f} / ±{P["wagen_abstand"]/2 + P["wagen_lochbild_y"]/2:.0f} längs, ±{P["wagen_lochbild_x"]/2:.0f} quer; '
             + "M5 (längs/quer): " + ", ".join(f"{y:g}/{x:g}" for x, y in m5_punkte())
             + "; M4: " + ", ".join(f"{y:g}/{x:g}" for x, y in m4_basis_punkte()) + '</text>')
    L.append('</svg>')
    with open(os.path.join(OUT, "flachstange_bohrschablone_1zu1.svg"), "w") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------- Hauptteil
def gespiegelt_links(shape):
    """Variante kasten in Lage links: an der YZ-Ebene gespiegelt (außen = -X)."""
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def verschoben(shape, dx):
    c = shape.copy()
    c.translate(V(dx, 0, 0))
    return c


def main():
    import Mesh
    fl = flachstange()
    wm = winkel("fest")
    wk = gespiegelt_links(winkel("kasten"))     # echte Geometrie links, Ursprung Schienenmitte
    sl = spannschlitten()
    kf = klemmplatte_fest()
    ks = klemmplatte_schlitten()
    dm = dummies()
    xk = x_klemmplatte()

    # X-Riemen hinten (Darstellung gerade zwischen den Sätteln, Omega am Wagen fehlt)
    g = x_geo()
    hb, rd = P["riemen_breite"] / 2, P["riemen_dicke"] / 2
    b = P["fl_breite"] / 2
    xr = box(-ABSTAND - b, b, g["y_rueck"], g["yw"], g["zr"] - hb, g["zr"] + hb)  # nur Rücken

    druck = {"winkel_fest": wm, "winkel_kasten": wk, "spannschlitten": sl,
             "klemmplatte_fest": kf, "klemmplatte_schlitten": ks,
             "x_klemmplatte": xk}

    pfad = os.path.join(OUT, "y_portalwinkel.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "Flachstange_40x15", fl, "alu")
    for name, shp in druck.items():
        if name == "winkel_kasten":
            shp = verschoben(shp, -ABSTAND)
        fc_dok.teil(doc, name, shp, "druck" if name.startswith("winkel") else "druck_hell")
    farbe = {"Wagen_HGH15CA": "wagen", "Schiene_HGR15": "dummy",
             "Bruecke_80x40x4": "alu", "Riemen_HTD5M_15": "riemen",
             "Riemen_Ruecktrum": "riemen"}
    for name, shp in dm.items():
        fc_dok.teil(doc, name, shp, farbe.get(name, "dummy"))
    fc_dok.teil(doc, "x_klemmplatte_links", verschoben(gespiegelt_links(xk), -ABSTAND),
                "druck_hell")
    fc_dok.teil(doc, "Riemen_X", xr, "riemen")
    fc_dok.speichern(doc, pfad, offen)

    fl.exportStep(os.path.join(OUT, "flachstange_40x15.step"))
    for name, shp in druck.items():
        shp.exportStep(os.path.join(OUT, name + ".step"))
        Mesh.Mesh(shp.tessellate(0.05)).write(os.path.join(OUT, name + ".stl"))
    for alt in ("winkel_druckteil.step", "winkel_druckteil.stl", "winkel_motor.step",
                "winkel_motor.stl"):
        if os.path.exists(os.path.join(OUT, alt)):
            os.remove(os.path.join(OUT, alt))

    def bbt(shape):
        bb = App.BoundBox()
        for pt in shape.tessellate(0.5)[0]:
            bb.add(pt)
        return bb

    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        for name, shp in druck.items():
            bb = bbt(shp)
            f.write("%-22s gültig: %s, %.1f x %.1f x %.1f mm, PETG ca. %.0f g (100 %% Füllung)\n"
                    % (name, shp.isValid(), bb.XLength, bb.YLength, bb.ZLength,
                       shp.Volume / 1000 * 1.27))
        f.write("Flachstange gültig: %s\n\n" % fl.isValid())
        for nm, shp in list(druck.items()) + [("flachstange", fl)]:
            fc_dok.schreibe_waende(f, nm, shp)
        f.write("\n")

        def koll(na, a, nb, b):
            f.write("Kollision %s / %s: %.3f mm³\n" % (na, nb, a.common(b).Volume))
        # Teile der linken Seite gegen die Darstellung verschieben
        links = lambda shp: verschoben(shp, -ABSTAND)
        for wn, w, ver in (("Fest", wm, lambda x: x), ("Kasten", links(wk), links)):
            for n, shp in dm.items():
                if n == "Bruecke_80x40x4":
                    koll("Winkel " + wn, w, n, shp)
                else:
                    koll("Winkel " + wn, w, n, ver(shp))
            koll("Winkel " + wn, w, "Flachstange", ver(fl))
            koll("Winkel " + wn, w, "Spannschlitten", ver(sl))
            koll("Winkel " + wn, w, "Klemmplatte fest", ver(kf))
            koll("Winkel " + wn, w, "Klemmplatte Schlitten", ver(ks))
            koll("Winkel " + wn, w, "Riemen X", xr)
        koll("Winkel Fest", wm, "X-Klemmplatte", xk)
        koll("Winkel Kasten", links(wk), "X-Klemmplatte", links(gespiegelt_links(xk)))
        koll("Riemen X", xr, "X-Klemmplatte", xk)
        koll("Riemen X", xr, "Spannschlitten", sl)
        koll("Riemen X", xr, "Klemmplatte Schlitten", ks)
        koll("Flachstange", fl, "Wagen", dm["Wagen_HGH15CA"])
        koll("Spannschlitten", sl, "Riemen", dm["Riemen_HTD5M_15"])
        f.write("(Klemmplatten liegen bewusst 0,7 mm auf dem Riemenrücken = Klemmweg)\n")
        f.write("Höhen über Flachstange-Unterseite: Rücktrum UK %.1f, Kanalboden Obertrum %.1f, "
                "Turm OK %.1f, Widerlager OK %.1f, X-Riemen Mitte %.1f (y %.1f)\n"
                % (z_ruecktrum(), z_kanal(), z_turm(), z_turm() + P["lasche_hoehe"],
                   g["zr"], g["y_mitte"]))
        f.write("(X-Klemmplatte liegt bewusst 0,5 mm auf dem Riemenrücken = Klemmweg)\n")
        f.write("Schlitten entspannt: Außenende y %.1f (Winkelende %.1f)\n"
                % (schl_mitte(0) + P["schl_laenge"] / 2, P["fl_laenge"] / 2))
        for wn, w in (("Fest", wm), ("Kasten", wk)):
            bbw = bbt(w)
            f.write("Winkel %s quer: x %.1f bis %.1f (Schienenmitte = 0)\n"
                    % (wn, bbw.XMin, bbw.XMax))
        yw0, yw1 = widerlager_y()
        f.write("Spannweg %.1f mm (%.0f Zähne), Widerlager y %.1f..%.1f, "
                "Lasche außen bis y %.1f (entspannt)\n"
                % (P["spannweg"], P["spannweg"] / P["riemen_teilung"], yw0, yw1,
                   schl_mitte(0) - platte_laenge() / 2))
        kp = klemmplatte_schlitten
        for lage in (0.0, 1.0):
            P["schl_lage"], alt = lage, P["schl_lage"]
            f.write("Lage %.0f: Kollision Winkel Fest/Klemmplatte+Lasche %.3f mm³, "
                    "Winkel Fest/Schlitten %.3f mm³\n"
                    % (lage, wm.common(kp()).Volume, wm.common(spannschlitten()).Volume))
            P["schl_lage"] = alt

    bohrschablone()


main()
