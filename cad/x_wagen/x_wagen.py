# -*- coding: utf-8 -*-
"""
X-Wagen mit Omega-Antrieb.

Aufbau:
  - Brücke 80x40x4 (80 hoch), HGR15 oben und unten, je ein HGH15CA-Wagen.
  - Alu-Platten 10 mm: Deckplatte (über dem oberen Wagen, von hinten bis vorn),
    Frontplatte (vorn senkrecht, trägt später Z-Achse und Brenner),
    Bodenplatte (unter dem unteren Wagen, an die Frontplatte geschraubt).
  - Motorbock (3D-Druck) hinten unter der Deckplatte: Motorplatte mit
    NEMA23 senkrecht (Körper ragt durch die Deckplatte), darunter
    Riemenscheibe 24 Z und zwei Umlenkrollen (je 2x 608) zwischen Motorplatte
    und unterer Platte. Eine Rolle sitzt im Langloch: damit wird der Riemen
    gespannt.
  - X-Riemen HTD5M/15 hochkant hinter der Brücke, Zähne zur Brücke, Enden an
    den Sätteln der Y-Winkel geklemmt.

Koordinaten: x = Wagenmitte (entlang der Brücke), y = Brückenmitte (+Y vorn),
z = Unterseite Brücke.

Aufruf:
  python3 cad/live.py cad/x_wagen/x_wagen.py
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
    # Brücke
    br_hoehe=80.0,
    br_tiefe=40.0,
    # HGR15 / HGH15CA
    schiene=15.0,
    wagen_breite=34.0,
    wagen_laenge=61.4,
    wagen_hoehe=28.0,
    wagen_h1=4.3,
    wagen_loch=26.0,
    m4_durchgang=4.5,
    m4_senk_d=8.0,
    m4_senk_tiefe=4.5,
    # Platten (Alu)
    platte=10.0,
    front_dicke=12.0,           # Frontplatte (M5 in die Stirnkanten)
    deck_x=46.0,                # halbe Länge Deckplatte in X
    front_x=30.0,               # halbe Länge Front- und Bodenplatte (<= halbe Wagenlänge)
    front_spalt=4.0,            # Frontplatte vor der Brücke
    deck_hinten=-136.0,         # Hinterkante Deckplatte (y)
    # Referenzfahne X (Stahl 3 mm) unter der Deckplatte, links hinten; Schalter am
    # linken Y-Winkel (Sattelrückwand), Achse z 94, y -25
    xf=(-20.0, 3.0, -34.0, -19.0, 86.0),      # x0, x1, y0, y1, z unten
    xf_loecher=[(-12.0, -26.5), (-3.0, -26.5)],
    deck_vor=0.0,               # Deckplatte bündig mit der Frontplatte (vorn sitzt die Z-Grundplatte)
    boden_vor=3.0,              # Bodenplatte steht vorn über die Frontplatte
    z_loecher=[(-20.0, 62.0), (20.0, 62.0), (-20.0, 88.0), (20.0, 88.0)],  # M5 für die Z-Grundplatte
    m5_durchgang=5.5,
    m5_kern=4.2,
    m5_senk_d=9.5,
    m5_senk_tiefe=5.5,
    # X-Riemen (aus y_portalwinkel: Rücken bei y = -31.9, Mitte z = 61 über Brücke UK)
    riemen_rueck_y=-31.9,
    riemen_z=61.0,
    riemen_breite=15.0,
    riemen_dicke=3.8,
    # Omega
    rolle_d=22.0,               # 608
    rolle_h=17.0,               # 2x 608 + Bordscheiben
    rolle_x=26.0,
    scheibe_abstand=33.1,       # Scheibenmitte hinter den Rollenmitten (Scheibe bei y = -76)
    achse_d=8.4,
    spann_langloch=8.0,         # Rolle +X verschiebbar nach hinten
    # Motor NEMA23 kompakt
    motor_kante=57.0,
    motor_laenge=56.0,
    motor_welle_d=8.0,
    motor_kabel=180.0,          # Kabelaustritt im Motor-System; mit 45° Drehung -> hinten links
    motor_lochabstand=47.14,
    motor_zentrier_d=38.1,
    m5_mutter_sw=8.2,
    m5_mutter_tiefe=4.5,
    # Motorbock (Druck)
    bock_x=42.0,                # halbe Breite hinten
    bock_rueck=14.0,            # Rückwand
    bock_seite=12.0,            # Seitenwände
    bock_seite_bis=-90.0,       # Seitenwangen enden vor dem Motor
    bock_platte=8.0,
    bock_schrauben=[(-33.0, -125.0), (33.0, -125.0), (-36.0, -100.0), (36.0, -100.0)],
    einsatz_m4_d=5.6,
    einsatz_m4_tiefe=10.0,
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def zyl(d, h, x, y, z, richtung=V(0, 0, 1)):
    return Part.makeCylinder(d / 2.0, h, V(x, y, z), richtung)


def sechskant(sw, h, x, y, z):
    import math
    r = sw / math.sqrt(3)
    pts = [V(x + r * math.cos(math.radians(30 + 60 * i)),
             y + r * math.sin(math.radians(30 + 60 * i)), z) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def geo():
    bt = P["br_tiefe"] / 2
    z_wo = P["br_hoehe"] + P["wagen_hoehe"]           # Montagefläche oberer Wagen
    z_wu = -P["wagen_hoehe"]                           # Montagefläche unterer Wagen
    y_rolle = P["riemen_rueck_y"] - P["rolle_d"] / 2
    y_scheibe = y_rolle - P["scheibe_abstand"]
    # Riemenscheibe (Kaufteil): Zahnbereich mittig auf dem Riemen, Nabe oben
    _, sd = kt.riemenscheibe_htd5m(24, bohrung=P["motor_welle_d"])
    z_s0 = P["riemen_z"] - sum(sd["zahnbereich"]) / 2
    z_mp = z_s0 + sd["hoehe"] + 1                      # Unterseite Motorplatte
    z_up = min(z_s0, P["riemen_z"] - P["rolle_h"] / 2) - 2    # Oberseite untere Platte
    return dict(bt=bt, z_wo=z_wo, z_wu=z_wu, y_rolle=y_rolle, y_scheibe=y_scheibe,
                z_mp=z_mp, z_up=z_up, z_s0=z_s0, y_f0=bt + P["front_spalt"],
                y_f1=bt + P["front_spalt"] + P["front_dicke"])


def motor_loecher(g):
    """NEMA23 um 45° gedreht: Löcher vorn/hinten/links/rechts."""
    a = P["motor_lochabstand"] / 2 * 2 ** 0.5
    ys = g["y_scheibe"]
    return [(0.0, ys + a), (0.0, ys - a), (a, ys), (-a, ys)]


def motor_raute(g, zu, h, luft=1.0):
    """Grundriss des um 45° gedrehten Motors als Prisma."""
    r = P["motor_kante"] / 2 * 2 ** 0.5 + luft
    ys = g["y_scheibe"]
    pts = [V(0, ys + r, zu), V(r, ys, zu), V(0, ys - r, zu), V(-r, ys, zu), V(0, ys + r, zu)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def wagen_loecher(yc=0.0):
    a = P["wagen_loch"] / 2
    return [(sx * a, yc + sy * a) for sx in (-1, 1) for sy in (-1, 1)]


# ---------------------------------------------------------------- Alu-Platten
def deckplatte():
    g = geo()
    t = P["platte"]
    z0 = g["z_wo"]
    s = box(-P["deck_x"], P["deck_x"], P["deck_hinten"], g["y_f1"] + P["deck_vor"], z0, z0 + t)
    for x, y in wagen_loecher():
        s = s.cut(zyl(P["m4_durchgang"], t + 2, x, y, z0 - 1))
        s = s.cut(zyl(P["m4_senk_d"], P["m4_senk_tiefe"] + 1, x, y, z0 + t - P["m4_senk_tiefe"]))
    # Ausschnitt für den Motorkörper (Motor um 45° gedreht)
    s = s.cut(motor_raute(g, z0 - 1, t + 2))
    # M5 zur Frontplatte (in deren Oberkante), Kopf oben aufliegend
    yf = (g["y_f0"] + g["y_f1"]) / 2
    for x in (-20, 0, 20):
        s = s.cut(zyl(P["m5_durchgang"], t + 2, x, yf, z0 - 1))
    # M4-Gewinde für die Referenzfahne X
    for x, y in P["xf_loecher"]:
        s = s.cut(zyl(3.3, 9, x, y, z0 - 1))
    # M4 in den Motorbock (Gewindeeinsätze), gesenkt
    for x, y in P["bock_schrauben"]:
        s = s.cut(zyl(P["m4_durchgang"], t + 2, x, y, z0 - 1))
        s = s.cut(zyl(P["m4_senk_d"], P["m4_senk_tiefe"] + 1, x, y, z0 + t - P["m4_senk_tiefe"]))
    return s


def frontplatte():
    g = geo()
    fx = P["front_x"]
    z0, z1 = g["z_wu"], g["z_wo"]
    s = box(-fx, fx, g["y_f0"], g["y_f1"], z0, z1)
    yf = (g["y_f0"] + g["y_f1"]) / 2
    for x in (-20, 0, 20):
        s = s.cut(zyl(P["m5_kern"], 15, x, yf, z1 - 14))      # oben, Gewinde M5
        s = s.cut(zyl(P["m5_kern"], 15, x, yf, z0 - 1))       # unten, Gewinde M5
    for x, z in P["z_loecher"]:                                 # vorn, Gewinde M5 für Z
        s = s.cut(zyl(P["m5_kern"], 11, x, g["y_f1"] + 1, z, V(0, -1, 0)))
    return s


def bodenplatte():
    g = geo()
    fx, t = P["front_x"], P["platte"]
    z1 = g["z_wu"]
    s = box(-fx, fx, -P["wagen_breite"] / 2 - 4, g["y_f1"] + P["boden_vor"], z1 - t, z1)
    for x, y in wagen_loecher():
        s = s.cut(zyl(P["m4_durchgang"], t + 2, x, y, z1 - t - 1))
        s = s.cut(zyl(P["m4_senk_d"], P["m4_senk_tiefe"] + 1, x, y, z1 - t - 1))
    # M5 in die Unterkante der Frontplatte
    yf = (g["y_f0"] + g["y_f1"]) / 2
    for x in (-20, 0, 20):
        s = s.cut(zyl(P["m5_durchgang"], t + 2, x, yf, z1 - t - 1))
    return s


# ---------------------------------------------------------------- Motorbock
def huelle(punkte):
    """Konvexe Hülle (monotone Kette) einer Punktliste [(x, y)]."""
    p = sorted(set((round(x, 4), round(y, 4)) for x, y in punkte))
    def kreuz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    unten, oben = [], []
    for q in p:
        while len(unten) >= 2 and kreuz(unten[-2], unten[-1], q) <= 0:
            unten.pop()
        unten.append(q)
    for q in reversed(p):
        while len(oben) >= 2 and kreuz(oben[-2], oben[-1], q) <= 0:
            oben.pop()
        oben.append(q)
    return unten[:-1] + oben[:-1]


def kreis(x, y, r, n=24):
    import math
    return [(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def platte(punkte, z0, h):
    pts = [V(x, y, z0) for x, y in huelle(punkte)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, h))


def motorbock():
    """Rückwand + zwei schräge Seitenwangen + zwei Platten, deren Umriss nur
    die Befestigungen umschließt (konvexe Hülle mit 3,5 mm Rand)."""
    g = geo()
    bx, tp = P["bock_x"], P["bock_platte"]
    yh = P["deck_hinten"] + 4                        # Deckplatte steht hinten 4 mm über
    yr = yh + P["bock_rueck"]
    zo = g["z_wo"]                                   # unter der Deckplatte
    zb = g["z_up"] - tp
    ys, yro = g["y_scheibe"], g["y_rolle"]
    rand = 3.5
    s = box(-bx, bx, yh, yr, zb, zo)                                       # Rückwand
    # Seitenwangen: oben bis hinter die Deckplattenschrauben, dann schräg zur Motorplatte
    w = P["bock_seite"]
    yb = P["bock_seite_bis"]
    y_sch = max(y for _, y in P["bock_schrauben"] if y > yr) + P["einsatz_m4_d"] / 2 + 3
    for sx in (-1, 1):
        x0 = sx * bx if sx < 0 else bx - w
        pts = [V(x0, yh, zb), V(x0, yh, zo), V(x0, y_sch, zo),
               V(x0, yb, g["z_mp"] + tp), V(x0, yb, zb), V(x0, yh, zb)]
        s = s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(w, 0, 0)))
    # Grundfläche hinten (Rückwand und Wangen) für beide Platten
    hinten = [(-bx, yh), (bx, yh), (-bx, yb), (bx, yb)]
    rollen = []
    for sx in (-1, 1):
        lang = P["spann_langloch"] if sx > 0 else 0.0
        rollen += kreis(sx * P["rolle_x"], yro, P["achse_d"] / 2 + rand)
        rollen += kreis(sx * P["rolle_x"], yro - lang, P["achse_d"] / 2 + rand)
    motor = kreis(0, ys, P["motor_zentrier_d"] / 2 + 0.5 + rand)
    for x, y in motor_loecher(g):
        motor += kreis(x, y, P["m5_mutter_sw"] / 3 ** 0.5 + rand)
    s = s.fuse(platte(hinten + rollen + motor, g["z_mp"], tp))           # Motorplatte
    unten = platte(hinten + rollen, zb, tp)                               # untere Platte
    unten = unten.cut(zyl(36.0, tp + 2, 0, ys, zb - 1))                  # Fenster unter der Scheibe
    s = s.fuse(unten)
    # Motor (45° gedreht): Zentrierung, 4x M5 mit Muttertaschen unten
    s = s.cut(zyl(P["motor_zentrier_d"] + 1, tp + 2, 0, ys, g["z_mp"] - 1))
    for x, y in motor_loecher(g):
        s = s.cut(zyl(P["m5_durchgang"], tp + 2, x, y, g["z_mp"] - 1))
        s = s.cut(sechskant(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 1, x, y, g["z_mp"] - 1))
    # Achsen der Umlenkrollen: -X fest, +X im Langloch nach hinten (Riemen spannen)
    for sx in (-1, 1):
        x = sx * P["rolle_x"]
        lang = P["spann_langloch"] if sx > 0 else 0.0
        for z0, h in ((g["z_mp"] - 1, tp + 2), (zb - 1, tp + 2)):
            s = s.cut(zyl(P["achse_d"], h, x, yro, z0))
            if lang:
                s = s.cut(zyl(P["achse_d"], h, x, yro - lang, z0))
                s = s.cut(box(x - P["achse_d"] / 2, x + P["achse_d"] / 2, yro - lang, yro, z0, z0 + h))
    # Gewindeeinsätze M4 oben für die Deckplatte
    for x, y in P["bock_schrauben"]:
        s = s.cut(zyl(P["einsatz_m4_d"], P["einsatz_m4_tiefe"] + 1, x, y,
                      zo - P["einsatz_m4_tiefe"]))
    return s.removeSplitter()


def ref_fahne():
    g = geo()
    x0, x1, y0, y1, zu = P["xf"]
    zo = g["z_wo"]
    s = box(x0, x1, y0, y1, zo - 3, zo).fuse(box(x0, x0 + 3, y0, y1, zu, zo - 2.99))
    for x, y in P["xf_loecher"]:
        s = s.cut(zyl(4.5, 5, x, y, zo - 4))
    return s.removeSplitter()


# ---------------------------------------------------------------- Kaufteile (Dummies)
def kaufteile():
    g = geo()
    d = {}
    wb, wl, s = P["wagen_breite"] / 2, P["wagen_laenge"] / 2, P["schiene"] / 2
    ob = box(-wl, wl, -wb, wb, P["br_hoehe"] + P["wagen_h1"], g["z_wo"])
    ob = ob.cut(box(-wl - 1, wl + 1, -s - 0.5, s + 0.5, P["br_hoehe"], P["br_hoehe"] + P["schiene"]))
    un = box(-wl, wl, -wb, wb, g["z_wu"], -P["wagen_h1"])
    un = un.cut(box(-wl - 1, wl + 1, -s - 0.5, s + 0.5, -P["schiene"], 0))
    d["Wagen_X_oben"] = ob
    d["Wagen_X_unten"] = un
    sch, _ = kt.riemenscheibe_htd5m(24, bohrung=P["motor_welle_d"])
    sch.translate(V(0, g["y_scheibe"], g["z_s0"]))
    d["Riemenscheibe_X"] = fc_dok.fest(sch)
    hr = P["rolle_h"] / 2
    d["Umlenkrollen_X"] = zyl(P["rolle_d"], 2 * hr, -P["rolle_x"], g["y_rolle"],
                              P["riemen_z"] - hr).fuse(
        zyl(P["rolle_d"], 2 * hr, P["rolle_x"], g["y_rolle"], P["riemen_z"] - hr))
    mo, _ = kt.nema23(P["motor_laenge"], P["motor_welle_d"], kabel_winkel=P["motor_kabel"])
    mo.rotate(V(0, 0, 0), V(0, 0, 1), 45)
    mo.translate(V(0, g["y_scheibe"], g["z_mp"] + P["bock_platte"]))
    d["Motor_X_NEMA23"] = fc_dok.fest(mo)
    return d


def main():
    teile = {"x_deckplatte": (deckplatte(), "alu"), "x_frontplatte": (frontplatte(), "alu"),
             "x_bodenplatte": (bodenplatte(), "alu"), "x_motorbock": (motorbock(), "druck"),
             "x_ref_fahne": (ref_fahne(), "stahl")}
    kauf = kaufteile()
    pfad = os.path.join(OUT, "x_wagen.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    for n, (shp, farbe) in teile.items():
        fc_dok.teil(doc, n, shp, farbe)
    farben = {}
    for n, shp in kauf.items():
        fc_dok.teil(doc, n, shp, farben.get(n, "dummy"))
    fc_dok.speichern(doc, pfad, offen)

    import Mesh
    for n, (shp, _) in teile.items():
        shp.exportStep(os.path.join(OUT, n + ".step"))
    Mesh.Mesh(teile["x_motorbock"][0].tessellate(0.05)).write(os.path.join(OUT, "x_motorbock.stl"))

    g = geo()
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        for n, (shp, _) in teile.items():
            bb = shp.BoundBox
            f.write("%-14s gültig: %s, %.1f x %.1f x %.1f mm\n"
                    % (n, shp.isValid(), bb.XLength, bb.YLength, bb.ZLength))
        alle = list(teile.items()) + [(n, (s, "")) for n, s in kauf.items()]
        n = 0
        for i, (na, (a, _)) in enumerate(alle):
            for nb, (b, _) in alle[i + 1:]:
                v = a.common(b).Volume
                if v > 1e-2:
                    f.write("Kollision %s / %s: %.1f mm³\n" % (na, nb, v))
                    n += 1
        f.write("Kollisionen: %d\n" % n)
        for nm, (shp, _) in teile.items():
            fc_dok.schreibe_waende(f, nm, shp)
        f.write("Riemenscheibe Mitte y %.1f, Rollen y %.1f, Motorplatte UK z %.1f\n"
                % (g["y_scheibe"], g["y_rolle"], g["z_mp"]))
        f.write("Größte halbe Breite hinter der Brücke (begrenzt den X-Weg an den Sätteln): %.1f mm\n"
                % max(P["rolle_x"] + P["rolle_d"] / 2, P["bock_x"]))


main()
