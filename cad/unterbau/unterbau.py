# -*- coding: utf-8 -*-
"""
Unterbau unter der Wanne: Geräteboden mit Plasmagerät und Schaltschrank, darüber
eine Haube, die Wasser von der Wanne nach hinten ableitet, und der Kabelweg
von der Y-Energiekette zum Schaltschrank.

- Geräteboden: Siebdruckplatte 9 mm auf den unteren Längsrohren (vom ersten
  Mittelquerrohr bis vorn), 6x M6 in Nietmuttern. Darauf rechts das Plasmagerät
  (Front nach vorn, 250 mm hinter der Schrankfront: Platz für Schlauchpaket und
  Stecker), links vorn der Schaltschrank 400 x 500 x 200.
- Haube: U auf dem Kopf aus Alu 0,5 über dem Geräteraum, so lang wie der Geräteboden,
  Dach mit Gefälle nach hinten und Tropfkante. Der Querkanal geht durch die rechte Wand
  (Rosette). Der Wannenablauf (Tankdurchführung, HDPE-Rohr, Winkel-Kugelhahn, Schlauch
  nach hinten) liegt hinter der Haube.
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
    ablauf=(360.0, 416.0),      # Rahmen x, y: Wannenmitte quer, hinter der Haube (440 hinter der
                                # Wannenmitte, zwischen den Käfig-Querrohren, unter einer Aussparung
                                # des mittleren Kammträgers = auflage aussparung_y)
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
    # Haube über dem Geräteraum: U auf dem Kopf aus Alu 0,5, so lang wie der Geräteboden,
    # Dach mit Gefälle nach hinten (Tropfkante), Wände auf dem Geräteboden (Flansch nach
    # außen, Spax), vorn an den Beinen (M5 in Nietmuttern), oben mit Abstandshaltern (Druck)
    # am unteren Rahmen des Wannenkäfigs (M5 in Nietmuttern)
    haube_t=0.5,
    haube_x=(40.0, 680.0),      # Außenseiten der Wände = Innenseiten der Beine
    dach_z=(665.0, 700.0),      # Oberseite Dach hinten / vorn
    haube_kante=10.0,           # Tropfkante hinten nach unten
    haube_flansch=12.0,         # unten nach außen auf den Geräteboden
    haube_spax_y=[520.0, 810.0, 1150.0, 1450.0],    # Spax 3,5 x 8 durch den Flansch (zwischen den M6 des Bodens)
    haube_bein=[(-20.0, 300.0), (-20.0, 560.0)],    # M5 in die Beine (= grundrahmen haube_bein)
    haube_kaefig_y=[600.0, 1350.0],                 # Abstandshalter unter den Käfig-Längsrohren (= wannenkaefig haube_y)
    kaefig_rohr_x=(50.0, 670.0),                    # Mitte der unteren Käfig-Längsrohre (20 x 20)
    abstand=(20.0, 30.0),       # Abstandshalter x, y
    # Rosette (Druck) innen um den Querkanal in der rechten Haubenwand: Flansch 5 dick,
    # 8 breit, 3x M3 von außen durch das Blech in eingepresste Muttern
    rosette_rand=8.0,
    rosette_t=5.0,
    rosette_spiel=0.3,
    # Ablauf hinter der Haube: Messing-Tankdurchführung 3/4" im Wannenboden, darunter
    # PE-Klemmwinkel 90° 25 x 3/4", gerades HDPE-Rohr d25 waagerecht nach hinten, am Ende
    # Kugelhahn (Klemm 25 x 3/4") und Schlauchtülle 3/4" bis an die Rahmenrückseite.
    # Gehalten von einem Halter (Druck) am hinteren oberen Querrohr des Untertischs.
    # Maße Platzhalter bis zum Kauf.
    wanne_boden=730.0,          # Unterseite Wannenboden (Wand 3)
    ablauf_klemm=44.0,          # Ø Klemmverschraubungen
    rohr_z=660.0,               # Achse des waagerechten Rohrs
    hahn=45.0,                  # Gehäuse Kugelhahn (Würfel)
    hahn_y=60.0,                # Gehäuse hinten (dahinter Abgang 3/4" und Tülle bis y 0)
    schlauch=(27.0, -80.0),     # Außen-Ø, Ende (Schlauch hängt hinten herunter)
    # Halter: Platte an der Innenseite des Querrohrs (y 40, z 770-810), Arm über den Hahn,
    # Schelle ums Rohr, Deckel unten mit 2x M4 in eingepresste Muttern
    ablauf_halter_m5=[(345.0, 790.0), (375.0, 790.0)],   # = grundrahmen ablauf_halter_m5
    halter_b=50.0,              # Breite (x)
    halter_t=12.0,              # Platte (y) und Arm (z)
    halter_schelle=(165.0, 195.0),    # Schelle y von, bis
    halter_spalt=1.0,           # Klemmspalt zwischen Schelle und Deckel
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
    (hx0, hx1), f = P["haube_x"], P["haube_flansch"]
    for x in (hx0 - f / 2, hx1 + f / 2):                 # Vorbohrung Spax der Haube
        for y in P["haube_spax_y"]:
            b = b.cut(Part.makeCylinder(1.25, 7.0, V(x, y, z0 + P["boden_t"] - 7.0)))
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


def dach_z(y):
    """Oberseite des Haubendachs bei y (Gefälle nach hinten)."""
    (z0, z1), y0, y1 = P["dach_z"], P["mittelquer_y"], P["aussen_y"]
    return z0 + (z1 - z0) * (y - y0) / (y1 - y0)


def dach(x0, x1, dz0, dz1, y0=None, y1=None):
    """Körper zwischen dach_z + dz0 und dach_z + dz1 über x0..x1 (y0..y1, sonst Haubenlänge)."""
    y0 = P["mittelquer_y"] if y0 is None else y0
    y1 = P["aussen_y"] if y1 is None else y1
    pts = [V(x0, y0, dach_z(y0) + dz0), V(x0, y1, dach_z(y1) + dz0),
           V(x0, y1, dach_z(y1) + dz1), V(x0, y0, dach_z(y0) + dz1)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(x1 - x0, 0, 0))


def kanal_loch():
    """Ausschnitt für den Querkanal in der rechten Haubenwand (y0, y1, z0, z1)."""
    (ky0, ky1), (zq0, zq1), s = P["kanal_y"], P["quer_z"], 0.5
    return ky0 - s, ky1 + s, zq0 - s, zq1 + s


def rosette_kanal_m3():
    """M3 der Kanal-Rosette (y, z): hinten, oben, unten (vorn steht außen das Bein)."""
    y0, y1, z0, z1 = kanal_loch()
    rd = P["rosette_rand"] / 2
    return [(y0 - rd, (z0 + z1) / 2), ((y0 + y1) / 2, z1 + rd), ((y0 + y1) / 2, z0 - rd)]


def abstand_m5():
    """M5 der Abstandshalter (x, y) unter den Käfig-Längsrohren."""
    return [(x, y) for x in P["kaefig_rohr_x"] for y in P["haube_kaefig_y"]]


def ablauf_teile():
    """Lagen des Ablaufstrangs: (y Bogen, y Rohrende im Hahn, y Hahn vorn, y Hahn hinten)."""
    ya = P["ablauf"][1]
    yh1 = P["hahn_y"]
    yh0 = yh1 + P["hahn"]
    return ya, yh0 + 45.0, yh0, yh1


def haube():
    """U auf dem Kopf aus Alu 0,5: Dach mit Gefälle nach hinten und Tropfkante, Wände auf
    dem Geräteboden mit Flansch nach außen, vorn an den Beinen."""
    t, (x0, x1) = P["haube_t"], P["haube_x"]
    y0, y1 = P["mittelquer_y"], P["aussen_y"]
    zb = boden_ok()
    h = dach(x0, x1, -t, 0)                                              # Dach
    h = h.fuse(box(x0, x1, y0, y0 + t, dach_z(y0) - P["haube_kante"], dach_z(y0)))   # Tropfkante
    for xa, xb in ((x0, x0 + t), (x1 - t, x1)):                         # Wände
        w = box(xa, xb, y0, y1, zb, P["dach_z"][1]).common(dach(xa - 1, xb + 1, -100.0 - 700.0, 0))
        h = h.fuse(w)
    f = P["haube_flansch"]
    yb = y1 - P["rohr"]                                                  # vorn stehen die Beine
    h = h.fuse([box(x0 - f, x0, y0, yb, zb, zb + t), box(x1, x1 + f, y0, yb, zb, zb + t)])
    for y in P["haube_spax_y"]:                                          # Spax in den Boden
        for x in (x0 - f / 2, x1 + f / 2):
            h = h.cut(Part.makeCylinder(2.0, t + 2, V(x, y, zb - 1)))
    for dy, z in P["haube_bein"]:                                        # M5 in die Beine
        for x in (x0, x1 - t):
            h = h.cut(Part.makeCylinder(2.75, t + 2, V(x - 1, y1 + dy, z), V(1, 0, 0)))
    ly0, ly1, lz0, lz1 = kanal_loch()                                    # Querkanal, rechte Wand
    h = h.cut(box(x0 - 1, x0 + t + 1, ly0, ly1, lz0, lz1))
    for y, z in rosette_kanal_m3():
        h = h.cut(Part.makeCylinder(1.7, t + 2, V(x0 - 1, y, z), V(1, 0, 0)))
    for x, y in abstand_m5():                                            # Abstandshalter
        h = h.cut(Part.makeCylinder(2.75, 20, V(x, y, dach_z(y) - 10)))
    return h.removeSplitter()


def rosette_kanal():
    """Rosette (Druck) innen an der rechten Haubenwand um den Querkanal: Flansch um den
    Ausschnitt, 3x M3 von außen durch das Blech in eingepresste Muttern (vorn steht außen
    das Bein, dort keine Schraube). Druck auf der Blechseite liegend."""
    x = P["haube_x"][0] + P["haube_t"]
    rt, rr, sp = P["rosette_t"], P["rosette_rand"], P["rosette_spiel"]
    (ky0, ky1), (zq0, zq1) = P["kanal_y"], P["quer_z"]
    y0, y1, z0, z1 = kanal_loch()
    r = box(x, x + rt, y0 - rr, y1 + rr, z0 - rr, z1 + rr)
    r = r.cut(box(x - 1, x + rt + 1, ky0 - sp, ky1 + sp, zq0 - sp, zq1 + sp))
    for y, z in rosette_kanal_m3():
        r = r.cut(Part.makeCylinder(1.7, rt + 2, V(x - 1, y, z), V(1, 0, 0)))
        r = r.cut(fc_dok.mutter(3, V(x + rt - 1.2, y, z), V(1, 0, 0)))
    return r.removeSplitter()


def abstandshalter():
    """Abstandshalter (Druck) zwischen Haubendach und Käfig-Längsrohr: unten mit dem Gefälle
    des Dachs, oben eben am Rohr, M5 von unten durch Blech und Halter in die Nietmutter.
    Gibt [(Form hinten), (Form vorn)] je für links und rechts zurück (gleiche Teile)."""
    bx, by = P["abstand"]
    zk = P["kaefig_uk"]
    res = []
    for y in P["haube_kaefig_y"]:
        teile = []
        for x in P["kaefig_rohr_x"]:
            a = dach(x - bx / 2, x + bx / 2, 0, zk - dach_z(y) + 5.0, y - by / 2, y + by / 2)
            a = a.common(box(x - bx / 2, x + bx / 2, y - by / 2, y + by / 2, 0, zk))
            a = a.cut(Part.makeCylinder(2.75, 100, V(x, y, dach_z(y) - 10)))
            teile.append(a.removeSplitter())
        res.append(teile)
    return res


def ablauf():
    """Ablaufstrang als ein Kaufteil-Platzhalter: Tankdurchführung, Klemmwinkel 90°, gerades
    HDPE-Rohr nach hinten, Kugelhahn (Hebel nach links), Schlauchtülle, Schlauch."""
    xa, ya = P["ablauf"]
    zw, zr, kd = P["wanne_boden"], P["rohr_z"], P["ablauf_klemm"]
    s = Part.makeCylinder(24.0, 5.0, V(xa, ya, zw + 3))                  # Flansch innen
    s = s.fuse(Part.makeCylinder(13.2, 38.0, V(xa, ya, zw - 30)))       # Gewinde durch den Boden
    s = s.fuse(Part.makeCylinder(20.0, 12.0, V(xa, ya, zw - 12)))       # Gegenmutter
    s = s.fuse(Part.makeCylinder(kd / 2, zw - 30 - zr, V(xa, ya, zr)))  # Klemmwinkel: senkrecht
    s = s.fuse(Part.makeSphere(kd / 2, V(xa, ya, zr)))
    s = s.fuse(Part.makeCylinder(kd / 2, 55.0, V(xa, ya, zr), V(0, -1, 0)))   # waagerecht
    _, ye, yh0, yh1 = ablauf_teile()
    s = s.fuse(Part.makeCylinder(12.5, ya - 45.0 - ye, V(xa, ye, zr), V(0, 1, 0)))   # HDPE-Rohr d25
    s = s.fuse(Part.makeCylinder(kd / 2, 50.0, V(xa, yh0 - 5.0, zr), V(0, 1, 0)))     # Klemm am Hahn
    hw = P["hahn"]
    s = s.fuse(box(xa - hw / 2, xa + hw / 2, yh1, yh0, zr - hw / 2, zr + hw / 2))
    s = s.fuse(box(xa + hw / 2, xa + hw / 2 + 100, (yh0 + yh1) / 2 - 5, (yh0 + yh1) / 2 + 5,
                   zr - 2.5, zr + 2.5))                                 # Hebel nach links
    s = s.fuse(Part.makeCylinder(15.0, 15.0, V(xa, yh1, zr), V(0, -1, 0)))     # Abgang 3/4"
    s = s.fuse(Part.makeCylinder(11.0, yh1 - 15.0, V(xa, yh1 - 15.0, zr), V(0, -1, 0)))   # Tülle bis y 0
    sd, se = P["schlauch"]
    s = s.fuse(Part.makeCylinder(sd / 2, 20.0 - se, V(xa, 20.0, zr), V(0, -1, 0)))
    return s.removeSplitter()


def ablauf_halter():
    """Halter (Druck) des Ablaufrohrs: Platte an der Innenseite des hinteren oberen Querrohrs
    (2x M5 in Nietmuttern), Arm über den Kugelhahn nach vorn, dort die obere
    Hälfte der Schelle ums Rohr; Deckel (untere Hälfte) mit 2x M4 von unten in Muttern, die
    seitlich in den Halter geschoben werden. Profil in y-z, gedruckt auf der Seite liegend.
    Gibt (Halter, Deckel) zurück."""
    xa = P["ablauf"][0]
    b, t, zr = P["halter_b"], P["halter_t"], P["rohr_z"]
    x0, x1 = xa - b / 2, xa + b / 2
    ys0, ys1 = P["halter_schelle"]
    yq = P["rohr"]                                       # Innenseite Querrohr (y 40)
    zq0, zq1 = P["unten_ok"] + 630.0, P["unten_ok"] + 670.0    # Querrohr oben z 770..810
    za = zr + P["hahn"] / 2 + 2.5                        # Arm über dem Hahn
    rr = 12.5 + 0.1
    sp = P["halter_spalt"] / 2
    h = box(x0, x1, yq, yq + t, za, zq1 - 2.0)          # Platte
    h = h.fuse(box(x0, x1, yq, ys1, za, za + t))        # Arm
    h = h.fuse(box(x0, x1, ys0, ys1, zr + sp, za))      # obere Schellenhälfte
    h = h.cut(Part.makeCylinder(rr, ys1 - ys0 + 2, V(xa, ys0 - 1, zr), V(0, 1, 0)))
    # Tropfendach 45° zur Druckoberseite (-x): gedruckt auf +x liegend, Bohrung waagerecht
    c = rr / math.sqrt(2)
    pts = [V(xa - c, ys0 - 1, zr + c), V(xa - rr * math.sqrt(2), ys0 - 1, zr), V(xa - c, ys0 - 1, zr - c),
           V(xa, ys0 - 1, zr)]
    h = h.cut(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, ys1 - ys0 + 2, 0)))
    for x, z in P["ablauf_halter_m5"]:                   # M5 in die Nietmuttern
        h = h.cut(Part.makeCylinder(2.75, t + 2, V(x, yq - 1, z), V(0, 1, 0)))
    d = box(x0, x1, ys0, ys1, zr - rr - 6.0, zr - sp)   # Deckel
    d = d.cut(Part.makeCylinder(rr, ys1 - ys0 + 2, V(xa, ys0 - 1, zr), V(0, 1, 0)))
    ym = (ys0 + ys1) / 2
    for dx in (-19.0, 19.0):                             # M4 von unten, Mutter seitlich im Halter
        p = V(xa + dx, ym, 0)
        d = d.cut(Part.makeCylinder(2.25, 40, V(p.x, p.y, zr - 30)))
        h = h.cut(Part.makeCylinder(2.25, 22, V(p.x, p.y, zr)))
        h = h.cut(fc_dok.mutter(4, V(p.x, p.y, zr + 9.0), V(0, 0, 1), V(1 if dx > 0 else -1, 0, 0), 12.0))
    return h.removeSplitter(), d.removeSplitter()


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
    hb = haube()
    ab = ablauf()
    senk, quer = kanaele()
    pfad = os.path.join(OUT, "unterbau.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "ub_geraeteboden", bo, "zukauf")
    fc_dok.teil(doc, "ub_haube", hb, "alu", 60)
    fc_dok.teil(doc, "Ablauf_Kugelhahn_Schlauch", ab, "zukauf")
    fc_dok.teil(doc, "Plasmageraet_XPro_CUT_70CNC", ge, "dummy")
    fc_dok.teil(doc, "Druckluft_Einheit", dl, "dummy")
    fc_dok.teil(doc, "Schaltschrank_400x500x200", sc, "dummy")
    fc_dok.teil(doc, "ub_kabelkanal_senkrecht", senk, "zukauf")
    fc_dok.teil(doc, "ub_kabelkanal_quer", quer, "zukauf")
    uu, uud = uebergang_unten()
    (ah0, ah1), (av0, av1) = abstandshalter()
    ahl, ade = ablauf_halter()
    druck = {"ub_uebergang_unten": uu, "ub_uebergang_unten_deckel": uud, "ub_kanalknoten": knoten(),
             "ub_rosette_kanal": rosette_kanal(),
             "ub_abstand_hinten": ah0, "ub_abstand_vorn": av0,     # Abstandshalter je 2 Stück
             "ub_ablauf_halter": ahl, "ub_ablauf_deckel": ade}
    log = []                                            # Radien und Fasen an den Druckteilen
    druck = fc_dok.sexy(druck, pfad, log)
    dx = P["kaefig_rohr_x"][1] - P["kaefig_rohr_x"][0]
    def paar(s):
        c = s.copy()
        c.translate(V(dx, 0, 0))
        return Part.makeCompound([s, c])
    for n, sh in druck.items():
        fc_dok.teil(doc, n, paar(sh) if n.startswith("ub_abstand") else sh, "druck")
    fc_dok.speichern(doc, pfad, offen)
    for alt in ("ub_tropfboden.step", "ub_rosette_ablauf.step", "ub_rosette_ablauf.stl"):  # entfallen
        if os.path.exists(os.path.join(OUT, alt)):
            os.remove(os.path.join(OUT, alt))
    for n, s in (("ub_geraeteboden", bo), ("ub_haube", hb)):
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
        (dz0, dz1), (hx0, hx1) = P["dach_z"], P["haube_x"]
        f.write("Haube (Alu %.1f): x %.0f bis %.0f, y %.0f bis %.0f, Dach oben hinten %.0f, vorn %.0f "
                "(Gefälle %.1f %%), unter dem Käfig vorn %.1f mm Luft; Abwicklung ca. %.0f x %.0f mm; "
                "Gewicht ca. %.1f kg\n"
                % (P["haube_t"], hx0, hx1, P["mittelquer_y"], P["aussen_y"], dz0, dz1,
                   100 * (dz1 - dz0) / (P["aussen_y"] - P["mittelquer_y"]),
                   P["kaefig_uk"] - dach_z(P["kaefig_y"][1]),
                   (hx1 - hx0) + 2 * (dz1 - ok) + 2 * P["haube_flansch"], P["aussen_y"] - P["mittelquer_y"],
                   hb.Volume * 2.7e-6))
        for y in P["haube_kaefig_y"]:
            f.write("Abstandshalter bei y %.0f: %.1f mm hoch (M5 x %.0f)\n"
                    % (y, P["kaefig_uk"] - dach_z(y), math.ceil((P["kaefig_uk"] - dach_z(y) + 10) / 5) * 5))
        h_rueck = dach_z(y_hinten) - P["haube_t"] - ok
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
        f.write("Schaltschrank: x %.0f bis %.0f, Oberkante %.0f, Haubendach darüber ab %.0f; "
                "Abstand zum Gerät %.0f mm\n"
                % (P["schrank_x1"] - sb, P["schrank_x1"], ok + sh,
                   dach_z(P["front_y"] - st) - P["haube_t"],
                   P["schrank_x1"] - sb - P["geraet_x0"] - gx))
        xa, ya = P["ablauf"]
        _, ye, yh0, yh1 = ablauf_teile()
        f.write("Ablauf: y %.0f (%.0f hinter der Wannenmitte, %.0f hinter der Tropfkante der Haube), "
                "Klemmwinkel 90° auf Rohrachse z %.0f, HDPE-Rohr d25 y %.0f bis %.0f (%.0f lang), "
                "Kugelhahn y %.0f bis %.0f (Hebel nach links), Tülle bis y 0 (Rahmenrückseite); "
                "Halter am hinteren Querrohr oben, Schelle y %.0f bis %.0f\n"
                % (ya, P["kaefig_y"][0] + (P["kaefig_y"][1] - P["kaefig_y"][0]) / 2 - ya,
                   P["mittelquer_y"] - ya - P["ablauf_klemm"] / 2, P["rohr_z"], ye, ya - 45.0,
                   ya - 45.0 - ye + 2 * 20.0, yh1, yh0, *P["halter_schelle"]))
        kol = [("Haube", hb), ("Gerät", ge), ("Druckluft", dl), ("Schrank", sc), ("Querkanal", quer),
               ("Rosette Kanal", druck["ub_rosette_kanal"]), ("Ablauf", ab),
               ("Ablaufhalter", druck["ub_ablauf_halter"]), ("Schellendeckel", druck["ub_ablauf_deckel"])]
        for i, (na, a) in enumerate(kol):
            for nb_, b in kol[i + 1:]:
                v = a.common(b).Volume
                if v > 1e-3:
                    f.write("Kollision %s / %s: %.1f mm³\n" % (na, nb_, v))
        f.write("\n".join(log) + "\n")
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
