# -*- coding: utf-8 -*-
"""
Y-Portalwinkel: verbindet die Portalbrücke (Alu-Rechteckrohr 20x40x4) mit
zwei HGH15-Wagen einer Y-Schiene.

Aufbau (von unten nach oben):
  HGR15-Schiene -> 2x HGH15CA-Wagen -> Alu-Flachstange 40x15 (gesenkte
  ISO-4762-Schrauben M4) -> 3D-gedruckter Winkel (M5 in Gewinde der
  Flachstange) -> Brücke im Sattel (2x M6 quer durch).
  Außen am Winkel: Flansch mit Riemennut und Klemmbohrungen für HTD5M/15, Befestigungsflansch Energiekette.

Koordinaten: Ursprung = Mitte Flachstange, Unterseite (= Oberkante Wagen).
  Y = Schienenrichtung, +X = außen (vom Tisch weg), Z = oben.

Aufruf (Flatpak-FreeCAD, headless):
  flatpak run --command=FreeCADCmd org.freecad.FreeCAD $PWD/y_portalwinkel.py
Erzeugt im selben Ordner: FCStd, STEP, STL, Bohrschablone (SVG).
"""
import os
import math
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))

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
    zugang_d=9.0,               # Zugang zu den M4-Wagenschrauben
    loecher_m5=[(10, 27), (12, 82)],   # (x, y), gespiegelt in x und y

    # Brücke 20 x 40 x 4, 40 hoch stehend
    br_breite=20.0,
    br_hoehe=40.0,
    br_wand=4.0,
    br_spiel=0.4,               # Spiel im Sattel (Druckteil)
    sattel_wand=10.0,
    m6_durchgang=6.4,
    m6_senk_d=11.0,
    m6_senk_tiefe=4.0,
    m6_mutter_sw=10.2,          # SW10 + Druckspiel
    m6_mutter_tiefe=5.0,
    m6_x=[-10.0, 10.0],

    rippe_dicke=8.0,
    rippe_ende_y=85.0,

    # Riemen HTD5M / 15 mm, flach, Zähne nach unten, Rücktrum unter dem Wagen
    fla_breite=50.0,            # Flansch ab Außenkante Flachstange
    riemen_breite=15.0,
    riemen_dicke=3.8,
    riemen_teilung=5.0,
    zahn_hoehe=2.1,             # -> Riemenrücken 1,7 mm
    zahn_breite=3.3,            # Lückenbreite inkl. Spiel
    nut_breite=15.6,            # Riemenkanal
    nut_tiefe=1.0,              # Riemenrücken steht 0,7 mm über -> Klemmplatte presst
    scheibe_zaehne=24,          # Antriebsscheibe, bestimmt Lage des Rücktrums

    # Festes Ende (-Y): eingeprägtes Zahnprofil + Klemmplatte M5
    fest_y=(-90.0, -54.0),
    klemm_abstand_x=26.0,
    klemm_y=[-82.0, -64.0],
    m5_mutter_sw=8.2,
    m5_mutter_tiefe=4.5,
    klemm_platte_dicke=6.0,

    # Spannende (+Y): Schwalbenschwanznut 60°, nach außen offen (Schlitten von
    # außen einschieben). Spannschraube M5 auf Zug: Kopf am Widerlager innen,
    # Mutter in der Lasche der Schlitten-Klemmplatte.
    sw_oeffnung=32.0,           # Breite oben
    sw_tiefe=7.0,
    sw_winkel=60.0,             # Flankenwinkel zur Waagerechten
    spiel=0.3,
    schl_laenge=36.0,
    spannweg=20.0,              # 4 Zähne; reicht er nicht, Schlitten zahnweise versetzt neu einschieben
    schl_lage=0.5,              # Lage im Modell: 0 = ganz außen (entspannt), 1 = ganz innen
    schl_m4_x=11.5,
    schl_m4_y=9.0,
    m4_mutter_sw=7.2,
    m4_mutter_tiefe=3.2,
    schl_platte_dicke=5.0,
    lasche_dicke=8.0,           # Lasche an der Schlitten-Klemmplatte
    lasche_hoehe=18.0,          # über Flanschoberkante
    spann_z=12.0,               # Achse Spannschraube über Flanschoberkante
    widerlager_dicke=10.0,
    widerlager_breite=24.0,
    widerlager_spalt=2.0,       # Lasche/Widerlager bei voll gespanntem Schlitten

    # Befestigungsflansch Energiekette (Halter folgt als eigenes Teil).
    # Sitzt außen auf jedem Winkel, damit links und rechts dasselbe Teil passt.
    ek_flansch=True,
    ek_dicke=8.0,
    ek_hoehe=30.0,              # über Flanschoberkante
    ek_y=(-45.0, -5.0),
    ek_loecher=[(-35.0, 10.0), (-15.0, 10.0), (-35.0, 22.0), (-15.0, 22.0)],  # (y, z über OK)
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


def m5_punkte():
    s = set()
    for xy in P["loecher_m5"]:
        s |= gespiegelt(xy)
    return sorted(s)


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
    return s


# ---------------------------------------------------------------- Druckteil
def winkel():
    b, l = P["fl_breite"], P["fl_laenge"]
    z0 = P["fl_dicke"]
    z1 = z0 + P["basis_dicke"]
    xa = b / 2 + P["fla_breite"]

    # Basis + Flansch in einem Stück, flache Unterseite = Druckbett
    s = box(-b / 2, xa, -l / 2, l / 2, z0, z1)

    # Sattel
    ci = P["br_breite"] / 2 + P["br_spiel"] / 2
    co = ci + P["sattel_wand"]
    zt = z1 + P["br_hoehe"]
    s = s.fuse(box(-b / 2, b / 2, -co, -ci, z1, zt))
    s = s.fuse(box(-b / 2, b / 2, ci, co, z1, zt))

    # Mittelrippe beidseitig (Winkel-Steife in Fahrtrichtung)
    rd = P["rippe_dicke"]
    for sy in (-1, 1):
        pts = [V(-rd / 2, sy * co, z1), V(-rd / 2, sy * co, zt),
               V(-rd / 2, sy * P["rippe_ende_y"], z1), V(-rd / 2, sy * co, z1)]
        s = s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(rd, 0, 0)))

    # M5 zur Flachstange, von oben gesenkt
    for x, y in m5_punkte():
        s = s.cut(zyl(P["m5_durchgang"], P["basis_dicke"] + 2, x, y, z0 - 1))
        s = s.cut(zyl(P["m5_senk_d"], P["m5_senk_tiefe"] + 1,
                      x, y, z1 - P["m5_senk_tiefe"]))

    # Zugang zu den M4-Wagenschrauben
    for x, y in wagen_schrauben():
        s = s.cut(zyl(P["zugang_d"], P["basis_dicke"] + 2, x, y, z0 - 1))

    # M6 quer durch Sattel und Brücke: Kopf bei -Y, Mutter bei +Y
    zm = z1 + P["br_hoehe"] / 2
    for x in P["m6_x"]:
        s = s.cut(zyl(P["m6_durchgang"], 2 * co + 2, x, -co - 1, zm, V(0, 1, 0)))
        s = s.cut(zyl(P["m6_senk_d"], P["m6_senk_tiefe"] + 1,
                      x, -co - 1, zm, V(0, 1, 0)))
        s = s.cut(sechskant(P["m6_mutter_sw"], P["m6_mutter_tiefe"] + 1,
                            x, co + 1, zm, V(0, -1, 0)))

    # Riemenflansch: Riemenkanal über die ganze Länge
    xr = riemen_x()
    s = s.cut(box(xr - P["nut_breite"] / 2, xr + P["nut_breite"] / 2,
                  -l / 2 - 1, l / 2 + 1, z1 - P["nut_tiefe"], z1 + 1))

    # Festes Ende (-Y): Zahnprofil eingeprägt, Klemmplatte mit M5 + Muttertaschen
    s = s.cut(zahnluecken(xr, P["fest_y"][0] - 1, P["fest_y"][1],
                          z1 - P["nut_tiefe"]))
    for x, y in klemm_punkte():
        s = s.cut(zyl(P["m5_durchgang"], P["basis_dicke"] + 2, x, y, z0 - 1))
        s = s.cut(sechskant(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 1,
                            x, y, z0 - 1))

    # Spannende (+Y): Schwalbenschwanznut, nach außen offen
    t = P["sw_tiefe"]
    yw0, yw1 = widerlager_y()
    s = s.cut(schwalbe(xr, P["sw_oeffnung"], t + 1, yw1 - 3, l / 2 + 1, z1 - t))

    # Widerlager für die Spannschraube (Kopf innen, Seite -Y)
    wb = P["widerlager_breite"]
    s = s.fuse(box(xr - wb / 2, xr + wb / 2, yw0, yw1, z1 - P["nut_tiefe"],
                   z1 + P["lasche_hoehe"]))
    s = s.cut(zyl(P["m5_durchgang"], yw1 - yw0 + 2, xr, yw0 - 1,
                  z1 + P["spann_z"], V(0, 1, 0)))

    # Befestigungsflansch Energiekette: senkrechte Lasche an der Außenkante,
    # M5 waagerecht, Muttertaschen innen
    if P["ek_flansch"]:
        xa = b / 2 + P["fla_breite"]
        xi = xa - P["ek_dicke"]
        ya, yb = P["ek_y"]
        s = s.fuse(box(xi, xa, ya, yb, z1 - 0.01, z1 + P["ek_hoehe"]))
        for y, z in P["ek_loecher"]:
            s = s.cut(zyl(P["m5_durchgang"], P["ek_dicke"] + 2, xi - 1, y, z1 + z,
                          V(1, 0, 0)))
            s = s.cut(sechskant(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 1,
                                xi - 1, y, z1 + z, V(1, 0, 0)))
    return s.removeSplitter()


def riemen_x():
    return P["fl_breite"] / 2 + P["fla_breite"] / 2


def schl_mitte(lage=None):
    """Schlittenmitte in Y. lage 0 = ganz außen (bündig), 1 = ganz innen."""
    lage = P["schl_lage"] if lage is None else lage
    return P["fl_laenge"] / 2 - P["schl_laenge"] / 2 - lage * P["spannweg"]


def platte_laenge():
    return P["schl_m4_y"] * 2 + 12


def widerlager_y():
    """Widerlager-Y-Bereich: vor der Lasche bei voll gespanntem Schlitten."""
    y_lasche = schl_mitte(1.0) - platte_laenge() / 2 - P["lasche_dicke"]
    y1 = y_lasche - P["widerlager_spalt"]
    return y1 - P["widerlager_dicke"], y1


def klemm_punkte():
    xr = riemen_x()
    return [(xr + sx * P["klemm_abstand_x"] / 2, y)
            for sx in (-1, 1) for y in P["klemm_y"]]


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
    xr = riemen_x()
    z1 = P["fl_dicke"] + P["basis_dicke"]
    sp, t = P["spiel"], P["sw_tiefe"]
    k = 1 / math.tan(math.radians(P["sw_winkel"]))
    h = t - sp
    zu = z1 - h
    ob = P["sw_oeffnung"] - 2 * sp
    ub = ob + 2 * h * k
    yc, L = schl_mitte(), P["schl_laenge"]
    pts = [V(xr - ub / 2, yc - L / 2, zu), V(xr + ub / 2, yc - L / 2, zu),
           V(xr + ob / 2, yc - L / 2, z1), V(xr - ob / 2, yc - L / 2, z1),
           V(xr - ub / 2, yc - L / 2, zu)]
    s = Part.Face(Part.makePolygon(pts)).extrude(V(0, L, 0))
    s = s.cut(box(xr - P["nut_breite"] / 2, xr + P["nut_breite"] / 2,
                  yc - L, yc + L, z1 - P["nut_tiefe"], z1 + 1))
    s = s.cut(zahnluecken(xr, yc - L / 2 - 1, yc + L / 2 + 1, z1 - P["nut_tiefe"]))
    for x, y in schl_punkte():
        s = s.cut(zyl(4.5, h + 2, x, y, zu - 1))
        s = s.cut(sechskant(P["m4_mutter_sw"], P["m4_mutter_tiefe"] + 1, x, y, zu - 1))
    return s.removeSplitter()


def schl_punkte():
    xr, yc = riemen_x(), schl_mitte()
    return [(xr + sx * P["schl_m4_x"], yc + sy * P["schl_m4_y"])
            for sx in (-1, 1) for sy in (-1, 1)]


def klemmplatte_fest():
    xr = riemen_x()
    z = P["fl_dicke"] + P["basis_dicke"] + 0.7    # auf dem Riemenrücken
    bx = P["klemm_abstand_x"] + 12
    ya, yb = P["fest_y"][0], P["fest_y"][1] - 2
    s = box(xr - bx / 2, xr + bx / 2, ya, yb, z, z + P["klemm_platte_dicke"])
    for x, y in klemm_punkte():
        s = s.cut(zyl(P["m5_durchgang"], 20, x, y, z - 1))
    return s


def klemmplatte_schlitten():
    xr, yc = riemen_x(), schl_mitte()
    z = P["fl_dicke"] + P["basis_dicke"] + 0.7
    bx = P["sw_oeffnung"] - 2 * P["spiel"]
    L = platte_laenge()
    s = box(xr - bx / 2, xr + bx / 2, yc - L / 2, yc + L / 2, z,
            z + P["schl_platte_dicke"])
    # Lasche innen (-Y) für die Spannschraube, Mutter auf der Außenseite (+Y)
    z1 = P["fl_dicke"] + P["basis_dicke"]
    ya = yc - L / 2 - P["lasche_dicke"]
    s = s.fuse(box(xr - bx / 2, xr + bx / 2, ya, yc - L / 2 + 0.01,
                   z, z1 + P["lasche_hoehe"]))
    zs = z1 + P["spann_z"]
    s = s.cut(zyl(P["m5_durchgang"], P["lasche_dicke"] + 2, xr, ya - 1, zs, V(0, 1, 0)))
    s = s.cut(sechskant(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 0.01, xr,
                        yc - L / 2 - P["m5_mutter_tiefe"], zs, V(0, 1, 0)))
    for x, y in schl_punkte():
        s = s.cut(zyl(4.5, 20, x, y, z - 1))
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
    z1 = P["fl_dicke"] + P["basis_dicke"]
    bb, bh, bw = P["br_breite"], P["br_hoehe"], P["br_wand"]
    br = box(-250, P["fl_breite"] / 2, -bb / 2, bb / 2, z1, z1 + bh)
    br = br.cut(box(-251, P["fl_breite"] / 2 + 1, -bb / 2 + bw, bb / 2 - bw,
                    z1 + bw, z1 + bh - bw))
    d["Bruecke_20x40x4"] = br
    xr = riemen_x()
    zr = z1 - P["nut_tiefe"]
    rb = P["riemen_breite"] / 2
    rueck = P["riemen_dicke"] - P["zahn_hoehe"]
    # Obertrum: zwei Enden auf dem Winkel (nur Riemenrücken dargestellt)
    ob = box(xr - rb, xr + rb, -160, P["fest_y"][1], zr, zr + rueck)
    ob = ob.fuse(box(xr - rb, xr + rb, schl_mitte() - P["schl_laenge"] / 2,
                     160, zr, zr + rueck))
    d["Riemen_HTD5M_15"] = ob
    # Rücktrum unter dem Wagen, um den Teilkreis der Antriebsscheibe tiefer
    zu = zr - P["scheibe_zaehne"] * P["riemen_teilung"] / math.pi
    d["Riemen_Ruecktrum"] = box(xr - rb, xr + rb, -160, 160, zu, zu + P["riemen_dicke"])
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
    L.append(f'<text x="{ox}" y="{oy+b+10}" font-size="3.5" fill="blue">blau: 8x Ø4,5 durch, Senkung Ø8 x 7,5 tief (ISO 4762 M4x12) – Wagen HGH15CA</text>')
    L.append(f'<text x="{ox}" y="{oy+b+16}" font-size="3.5" fill="red">rot: 8x M5, Kernloch Ø4,2 x 12 tief, Gewinde ≥10 tief – Druckwinkel</text>')
    L.append(f'<text x="{ox}" y="{oy-3}" font-size="3">Außenseite (+X, Riemenflansch)</text>')
    L.append(f'<line x1="{ox}" y1="{oy+b+28}" x2="{ox+100}" y2="{oy+b+28}" stroke="black" stroke-width="0.4"/>')
    L.append(f'<text x="{ox}" y="{oy+b+34}" font-size="3">100 mm</text>')
    # Bemaßung als Koordinatenliste
    yy = oy + b + 44
    L.append(f'<text x="{ox}" y="{yy}" font-size="3">Koordinaten ab Stangenmitte (Länge / Breite), mm: '
             f'M4: ±{P["wagen_abstand"]/2 - P["wagen_lochbild_y"]/2:.0f} / ±{P["wagen_abstand"]/2 + P["wagen_lochbild_y"]/2:.0f} längs, ±{P["wagen_lochbild_x"]/2:.0f} quer; '
             + "; ".join(f"M5: ±{y:g} längs, ±{x:g} quer" for x, y in P["loecher_m5"]) + '</text>')
    L.append('</svg>')
    with open(os.path.join(OUT, "flachstange_bohrschablone_1zu1.svg"), "w") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------- Hauptteil
def main():
    import Mesh
    fl = flachstange()
    wi = winkel()
    sl = spannschlitten()
    kf = klemmplatte_fest()
    ks = klemmplatte_schlitten()
    dm = dummies()

    druck = {"winkel_druckteil": wi, "spannschlitten": sl,
             "klemmplatte_fest": kf, "klemmplatte_schlitten": ks}

    doc = App.newDocument("Y_Portalwinkel")
    for name, shp in ([("Flachstange_40x15", fl)] + list(druck.items())
                      + list(dm.items())):
        doc.addObject("Part::Feature", name).Shape = shp
    doc.recompute()
    doc.saveAs(os.path.join(OUT, "y_portalwinkel.FCStd"))

    fl.exportStep(os.path.join(OUT, "flachstange_40x15.step"))
    for name, shp in druck.items():
        shp.exportStep(os.path.join(OUT, name + ".step"))
        Mesh.Mesh(shp.tessellate(0.05)).write(os.path.join(OUT, name + ".stl"))

    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        for name, shp in druck.items():
            bb = shp.BoundBox
            f.write("%-22s gültig: %s, %.1f x %.1f x %.1f mm, PETG ca. %.0f g (100 %% Füllung)\n"
                    % (name, shp.isValid(), bb.XLength, bb.YLength, bb.ZLength,
                       shp.Volume / 1000 * 1.27))
        f.write("Flachstange gültig: %s\n\n" % fl.isValid())

        def koll(na, a, nb, b):
            f.write("Kollision %s / %s: %.3f mm³\n" % (na, nb, a.common(b).Volume))
        for n, shp in dm.items():
            koll("Winkel", wi, n, shp)
        koll("Winkel", wi, "Flachstange", fl)
        koll("Winkel", wi, "Spannschlitten", sl)
        koll("Flachstange", fl, "Wagen", dm["Wagen_HGH15CA"])
        koll("Spannschlitten", sl, "Riemen", dm["Riemen_HTD5M_15"])
        f.write("(Klemmplatten liegen bewusst 0,7 mm auf dem Riemenrücken = Klemmweg)\n")
        # Spannweg: Schlitten zwischen Einlegetasche und Nutende
        yw0, yw1 = widerlager_y()
        f.write("Spannweg %.1f mm (%.0f Zähne), Widerlager y %.1f..%.1f, "
                "Spannschraube M5 Kopf an y %.1f, Lasche außen bis y %.1f (entspannt)\n"
                % (P["spannweg"], P["spannweg"] / P["riemen_teilung"], yw0, yw1, yw0,
                   schl_mitte(0) - platte_laenge() / 2))
        kp = klemmplatte_schlitten
        for lage in (0.0, 1.0):
            P["schl_lage"], alt = lage, P["schl_lage"]
            f.write("Lage %.0f: Kollision Winkel/Klemmplatte+Lasche %.3f mm³, "
                    "Winkel/Schlitten %.3f mm³\n"
                    % (lage, wi.common(kp()).Volume, wi.common(spannschlitten()).Volume))
            P["schl_lage"] = alt

    bohrschablone()


main()
