# -*- coding: utf-8 -*-
"""
X-Wagen mit Omega-Antrieb.

Aufbau:
  - Brücke 80x40x4 (80 hoch), HGR15 oben und unten, je ein HGH15CA-Wagen.
  - Wagenkörper (Druck, ASA, seitlich liegend gedruckt): Deck über dem oberen Wagen,
    Front vorn senkrecht, Boden unter dem unteren Wagen in einem C-Profil. Die
    Z-Grundplatte (Alu 12) reicht bis unten und ist oben und unten verschraubt.
  - Spritzschutz (Blech 1 mm) unter Boden und Z-Grundplatte.
  - Motorbock (3D-Druck) von hinten an das Deck geflanscht: Motorplatte mit
    NEMA23 senkrecht, darunter
    Riemenscheibe 24 Z und zwei Umlenkrollen (je 2x 608) auf festen Achsen in
    der unteren Platte. Gespannt wird, indem der Motor in seinen Langlöchern
    nach hinten geschoben wird.
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
    # Wagenkörper (Druck, ASA): Deck, Front und Boden in einem Teil
    front_dicke=14.0,
    deck_dicke=26.0,            # dick: hinten Flanschfläche für den Motorbock
    deck_senk=12.0,             # Wagenschrauben M4 x 20
    boden_dicke=10.0,           # Unterseite bleibt bei z -38 (Abstand zum Blech)
    koerper_x=30.0,             # halbe Breite, durchgehend (an den X-Enden dicht an den Sätteln)
    front_spalt=2.0,            # Front vor der Brücke
    deck_hinten=-33.0,          # Hinterkante Deck = Flanschfläche Motorbock (y)
    boden_hinten=-21.0,
    m4_senk_scheibe=10.0,       # Senkung für Kopf + Scheibe (Kunststoff kriecht sonst)
    m4_senk_tiefe_druck=6.0,
    einsatz_m5_d=6.4,
    einsatz_m5_tiefe=10.0,
    einsatz_m3_d=4.0,
    einsatz_m3_tiefe=6.0,
    # Spritzschutz (Blech 1 mm) unter Boden und Z-Grundplatte
    schutz_dicke=1.0,
    schutz_vorn=48.0,           # bis Vorderfläche Z-Grundplatte
    schutz_loecher=[(-24.0, -14.0), (24.0, -14.0), (-24.0, 28.0), (24.0, 28.0)],
    # Referenz X: Schalter am linken Y-Winkel (Sattelrückwand), Achse quer, z 94,
    # y -24,75, Sensorfläche bei Wagen x 78 - 20. Ziel ist ein Zylinderstift 6x10
    # (Stahl, eingepresst) in der linken Fläche des nach unten gezogenen Blocks.
    hinten_block=(-20.0, 30.0, None, -20.5, 72.0),   # x0, x1, (y0 = Deck hinten), y1, z unten
    ref_stift_d=6.0,
    ref_stift_l=10.0,
    ref_stift_lage=(-20.0, -26.75, 94.0),             # Stirn bündig mit der Blockfläche
    z_loecher=[(-20.0, -15.0), (20.0, -15.0), (-20.0, 62.0), (20.0, 62.0),
               (-20.0, 88.0), (20.0, 88.0)],   # M5 für die Z-Grundplatte (Einsätze)
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
    scheibe_abstand=44.0,       # Scheibenmitte hinter den Rollenmitten: auch ganz vorn bleiben
                                # zwischen Motor und Flanschwand gut 10 mm für einen Hebel
    achse_d=8.4,
    spann_motor=8.0,            # Spannweg: Motor in Langlöchern nach hinten
    bock_platte_unten=9.0,      # untere Platte trägt die Rollenachsen allein (darunter bleibt
                                # 0,5 mm über dem Y-Motorhalter, wenn das Portal hinten steht)
    m8_kopf_sw=13.2,
    m8_kopf_tiefe=5.5,
    # Motor NEMA23 kompakt
    motor_kante=57.0,
    motor_laenge=56.0,
    motor_welle_d=8.0,
    motor_kabel=270.0,          # Kabelaustritt nach hinten
    motor_lochabstand=47.14,
    motor_zentrier_d=38.1,
    m5_mutter_sw=8.2,
    m5_mutter_tiefe=4.5,
    # Motorbock (Druck)
    bock_x=42.0,                # halbe Breite hinten (begrenzt den X-Weg an den Sätteln)
    bock_seite=4.0,             # Seitenwände (außen an den Rollen vorbei)
    bock_hinten=-100.0,         # Hinterkante Seitenwände / untere Platte
    bock_steg=9.0,              # halbe Breite Mittelsteg zwischen den Platten
    bock_schraege_x=31.5,       # ab hier außen vorn 45° schräg
    steg_x=(6.5, 30.0),         # Stege (|x|), innen 13 mm frei für den Hebel
    steg_ende_y=-53.5,          # Motor ganz vorn gespannt: Vorderkante bei -54,7
    bock_platte=8.0,
    flansch_dicke=10.0,
    # (x, z); die unteren weiter innen: links lässt der Block dort Platz für den
    # Referenzschalter, darunter sitzt der Stahlstift
    flansch_loecher=[(-14.0, 104.0), (14.0, 104.0), (-22.0, 127.0), (22.0, 127.0)],
    flansch_tiefe=8.0,          # Mutter M4 so tief hinter der Flanschfläche (vor dem Block bleibt Wand)
    m3_durchgang=3.4,
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
    """NEMA23 gerade (nicht gedreht): Löcher auf den Diagonalen. So liegen die
    Langlöcher zum Spannen (in y) neben der Zentrierung und nicht in einer Linie."""
    a = P["motor_lochabstand"] / 2
    ys = g["y_scheibe"]
    return [(sx * a, ys + sy * a) for sx in (-1, 1) for sy in (-1, 1)]


def wagen_loecher(yc=0.0):
    a = P["wagen_loch"] / 2
    return [(sx * a, yc + sy * a) for sx in (-1, 1) for sy in (-1, 1)]


# ---------------------------------------------------------------- Wagenkörper (Druck)
def koerper():
    """Deck, Front und Boden in einem Druckteil (C-Profil, durchgehend 60 breit,
    seitlich liegend gedruckt: das Profil liegt in den Schichten). Die Z-Grundplatte
    (Alu) reicht vorn bis unten und trägt die Biegung zwischen den beiden Wagen.
    Hinten am Deck ist die Flanschfläche für den Motorbock (4x M4 in Einsätze)."""
    g = geo()
    bx = P["koerper_x"]
    zd0, zd1 = g["z_wo"], g["z_wo"] + P["deck_dicke"]
    zb0, zb1 = g["z_wu"] - P["boden_dicke"], g["z_wu"]
    yf0, yf1 = g["y_f0"], g["y_f1"]
    s = box(-bx, bx, P["deck_hinten"], yf1, zd0, zd1)                     # Deck
    s = s.fuse(box(-bx, bx, yf0, yf1, zb0, zd1))                         # Front
    s = s.fuse(box(-bx, bx, P["boden_hinten"], yf1, zb0, zb1))           # Boden
    # Wagenschrauben M4, gesenkt (Kopf mit Scheibe)
    for x, y in wagen_loecher():
        s = s.cut(zyl(P["m4_durchgang"], zd1 - zd0 + 2, x, y, zd0 - 1))
        s = s.cut(zyl(P["m4_senk_scheibe"], P["deck_senk"] + 1, x, y, zd1 - P["deck_senk"]))
        s = s.cut(zyl(P["m4_durchgang"], zb1 - zb0 + 2, x, y, zb0 - 1))
        s = s.cut(zyl(P["m4_senk_scheibe"], P["m4_senk_tiefe_druck"] + 1, x, y, zb0 - 1))
    # hinter der Brücke nach unten gezogen (bis über den Riemen); links bleibt Platz
    # für den Referenzschalter am Sattel, dort sitzt der Stahlstift in der Seitenfläche
    x0, x1, y0, y1, z0 = P["hinten_block"]
    s = s.fuse(box(x0, x1, P["deck_hinten"], y1, z0, zd0 + 0.01))
    xs, ys_, zs = P["ref_stift_lage"]
    s = s.cut(zyl(P["ref_stift_d"], P["ref_stift_l"] + 0.5, xs - 0.01, ys_, zs, V(1, 0, 0)))
    # Muttern eingepresst, jeweils seitlich in einen Schlitz geschoben (Seite x)
    yh = P["deck_hinten"]
    for x, z in P["flansch_loecher"]:                                     # Motorbock, M4
        s = s.cut(zyl(P["m4_durchgang"], P["flansch_tiefe"] + 4, x, yh - 1, z, V(0, 1, 0)))
        xs = x0 if x < 0 and z < zd0 else (-bx if x < 0 else bx)          # nächste Seitenfläche
        s = s.cut(fc_dok.mutter(4, V(x, yh + P["flansch_tiefe"] - 2.5, z), V(0, 1, 0),
                                V(1 if xs > x else -1, 0, 0), abs(xs - x) + 1))
    for x, z in P["z_loecher"]:                                           # Z-Grundplatte, M5
        s = s.cut(zyl(P["m5_durchgang"], 12, x, yf1 + 1, z, V(0, -1, 0)))
        s = s.cut(fc_dok.mutter(5, V(x, yf1 - 7, z), V(0, 1, 0), V(1 if x > 0 else -1, 0, 0),
                                bx - abs(x) + 1))
    for x, y in P["schutz_loecher"]:                                      # Spritzschutz, M3
        s = s.cut(zyl(P["m3_durchgang"], 7, x, y, zb0 - 1))
        s = s.cut(fc_dok.mutter(3, V(x, y, zb0 + 5), V(0, 0, 1), V(1 if x > 0 else -1, 0, 0),
                                bx - abs(x) + 1))
    return s.removeSplitter()


def ref_stift():
    """Zylinderstift Stahl (eingepresst) in der linken Seitenfläche: Ziel für den
    Referenzschalter X am linken Sattel (an Stelle der Blechfahne)."""
    xs, ys_, zs = P["ref_stift_lage"]
    return zyl(P["ref_stift_d"], P["ref_stift_l"], xs, ys_, zs, V(1, 0, 0))


def spritzschutz():
    """Blech 1 mm unter dem Boden und der Z-Grundplatte (Spritzer beim Einstechen).
    Löcher unter den Wagenschrauben, 4x M3 in den Boden."""
    g = geo()
    bx, t = P["koerper_x"], P["schutz_dicke"]
    z1 = g["z_wu"] - P["boden_dicke"]
    s = box(-bx, bx, P["boden_hinten"], P["schutz_vorn"], z1 - t, z1)
    for x, y in wagen_loecher():
        s = s.cut(zyl(P["m4_senk_scheibe"], t + 2, x, y, z1 - t - 1))
    for x, y in P["schutz_loecher"]:
        s = s.cut(zyl(3.4, t + 2, x, y, z1 - t - 1))
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


def langloch_z(d, y0, y1, z, h, x=0.0):
    """Langloch senkrecht (Achse z), in y von y0 bis y1 (Mitten)."""
    r = d / 2
    return zyl(d, h, x, y0, z).fuse([zyl(d, h, x, y1, z), box(x - r, x + r, y0, y1, z, z + h)])


def motorbock():
    """C-Profil von der Seite: vorn die Flanschwand (4x M4 in die Rückseite des Decks),
    nach hinten Motorplatte und untere Platte, außen zwei Seitenwände. Zwischen den
    Platten ist die Flanschwand nur in der Mitte und an den Seitenwänden, dort läuft
    der Riemen um die Rollen."""
    g = geo()
    tp = P["bock_platte"]
    yv = P["deck_hinten"]                            # Flanschfläche
    yw = yv - P["flansch_dicke"]
    zo = g["z_wo"] + P["deck_dicke"]                 # oben bündig mit dem Deck
    zm0, zm1 = g["z_mp"], g["z_mp"] + tp             # Motorplatte
    zb = g["z_up"] - tp                              # untere Platte
    ys, yro = g["y_scheibe"], g["y_rolle"]
    bx, sw = P["bock_x"], P["bock_seite"]
    yh = P["bock_hinten"]
    rand = 3.5
    s = box(-P["koerper_x"], P["koerper_x"], yw, yv, zm0, zo)              # Flanschwand oben
    vorn = [(-bx, yv), (bx, yv), (-bx, yh), (bx, yh)]
    sp = P["spann_motor"] / 2                         # Motor verschiebbar in y (±sp)
    tu = P["bock_platte_unten"]
    zb = g["z_up"] - tu
    rollen = []
    for sx in (-1, 1):
        rollen += kreis(sx * P["rolle_x"], yro, P["m8_kopf_sw"] / 3 ** 0.5 + rand)
    motor = []
    for dy in (-sp, sp):
        motor += kreis(0, ys + dy, P["motor_zentrier_d"] / 2 + 0.5 + rand)
        for x, y in motor_loecher(g):
            motor += kreis(x, y + dy, P["m5_mutter_sw"] / 3 ** 0.5 + rand)
    s = s.fuse(platte(vorn + motor, zm0, tp))                              # Motorplatte
    unten = platte(vorn + rollen, zb, tu)                                  # untere Platte
    unten = unten.cut(langloch_z(36.0, ys - sp, ys + sp, zb - 1, tu + 2))  # Fenster unter der Scheibe
    s = s.fuse(unten)
    s = s.fuse(box(-P["bock_steg"], P["bock_steg"], yw, yv, zb, zm0 + 0.01))   # Mittelsteg bis unten
    for sx in (-1, 1):                                                       # Seitenwände bis unten
        x0 = sx * bx if sx < 0 else bx - sw
        s = s.fuse(box(x0, x0 + sw, yh, yv, zb, zm1))
    s = s.cut(box(-bx - 5, bx + 5, yv, yv + 20, zb - 1, zo + 1))   # nichts vor der Flanschfläche
    # außen vorn 45° schräg frei (an den X-Enden stehen dort die Riemenklemmplatten);
    # schräg statt abgesetzt: gedruckt wird auf der Flanschfläche liegend
    c0, c1 = P["bock_schraege_x"], bx + 2
    for sx in (-1, 1):
        pts = [V(sx * c0, yv + 1, zb - 1), V(sx * c0, yv, zb - 1), V(sx * c1, yv - (c1 - c0), zb - 1),
               V(sx * c1, yv + 1, zb - 1), V(sx * c0, yv + 1, zb - 1)]
        s = s.cut(Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, zm1 - zb + 2)))
    # Stege links und rechts: versteifen den Winkel Flanschwand/Motorplatte, reichen
    # bis zur Oberkante und bis knapp vor den Motor (ganz vorn gespannt); in der
    # Mitte bleibt Platz für den Hebel
    ye = P["steg_ende_y"]
    for sx in (-1, 1):
        xa, xb_ = sorted((sx * P["steg_x"][0], sx * P["steg_x"][1]))
        pts = [V(xa, yw + 0.01, zm1 - 0.01), V(xa, yw + 0.01, zo), V(xa, ye, zm1 - 0.01),
               V(xa, yw + 0.01, zm1 - 0.01)]
        s = s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(xb_ - xa, 0, 0)))
    # Motor (45° gedreht) in Langlöchern: zum Spannen nach hinten schieben (Hebel
    # zwischen Motor und Flanschwand), dann festziehen. Muttern in Langnuten unten.
    s = s.cut(langloch_z(P["motor_zentrier_d"] + 1, ys - sp, ys + sp, zm0 - 1, tp + 2))
    for x, y in motor_loecher(g):
        s = s.cut(langloch_z(P["m5_durchgang"], y - sp, y + sp, zm0 - 1, tp + 2, x))
        for dy in (-sp, sp):
            s = s.cut(sechskant(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 1, x, y + dy, zm0 - 1))
        s = s.cut(box(x - P["m5_mutter_sw"] / 2, x + P["m5_mutter_sw"] / 2, y - sp, y + sp,
                      zm0 - 1, zm0 + P["m5_mutter_tiefe"]))
    # Umlenkrollen auf festen Achsen, nur unten: M8 von unten, Kopf verdrehsicher in
    # der Sechskanttasche, oben Mutter + Scheibe, darüber die Rolle
    for sx in (-1, 1):
        x = sx * P["rolle_x"]
        s = s.cut(zyl(P["achse_d"], tu + 2, x, yro, zb - 1))
        s = s.cut(sechskant(P["m8_kopf_sw"], P["m8_kopf_tiefe"] + 1, x, yro, zb - 1))
    # Flansch: 4x M4 durch Wand und Steg, Senkung in der Schräge des Stegs
    def schraege_y(z):
        return yw - (zo - z) / (zo - zm1) * (yw - ye)
    for x, z in P["flansch_loecher"]:
        s = s.cut(zyl(P["m4_durchgang"], yv - ye + 2, x, yv + 1, z, V(0, -1, 0)))
        y_sitz = schraege_y(z + P["m4_senk_d"] / 2 + 0.5)
        s = s.cut(zyl(P["m4_senk_d"], y_sitz - ye + 10, x, y_sitz, z, V(0, -1, 0)))
    return s.removeSplitter()


# ---------------------------------------------------------------- Kaufteile (Dummies)
def kaufteile():
    g = geo()
    d = {}
    wb, wl, s = P["wagen_breite"] / 2, P["wagen_laenge"] / 2, P["schiene"] / 2
    ob = kt.hgh15ca()                                   # Länge entlang Y -> entlang X drehen
    ob.rotate(V(0, 0, 0), V(0, 0, 1), 90)
    ob.translate(V(0, 0, P["br_hoehe"]))
    ob = fc_dok.fest(ob)
    un = kt.hgh15ca()
    un.rotate(V(0, 0, 0), V(0, 0, 1), 90)
    un.rotate(V(0, 0, 0), V(1, 0, 0), 180)              # unten, kopfüber
    un = fc_dok.fest(un)
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
    mo.translate(V(0, g["y_scheibe"], g["z_mp"] + P["bock_platte"]))
    d["Motor_X_NEMA23"] = fc_dok.fest(mo)
    return d


def main():
    teile = {"x_wagenkoerper": (koerper(), "druck"), "x_spritzschutz": (spritzschutz(), "stahl"),
             "x_motorbock": (motorbock(), "druck"),
             "x_ref_stift": (ref_stift(), "stahl")}
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
    for n in ("x_motorbock", "x_wagenkoerper"):
        Mesh.Mesh(teile[n][0].tessellate(0.05)).write(os.path.join(OUT, n + ".stl"))

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
