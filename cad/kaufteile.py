# -*- coding: utf-8 -*-
"""
Kaufteile mit den für die Konstruktion relevanten Merkmalen.

Alle Teile in eigener Lage; der Aufrufer dreht und verschiebt sie.
"""
import math
import FreeCAD as App
import Part

V = App.Vector


def nema23(laenge=56.0, welle_d=8.0, welle_l=21.0, kabel_winkel=225.0):
    """Schrittmotor NEMA23 (Maße nach gängigem Datenblatt, z. B. 23HS22).

    Lage: Flanschfläche (Anlage) in z = 0, Welle zeigt nach -Z, Körper nach +Z,
    Achse = Z. Die Befestigungsbohrungen liegen auf den Diagonalen des
    Quadrats (x/y = ±23,57).
    kabel_winkel: Richtung des Kabelaustritts in der XY-Ebene (Grad, 0 = +X).
    Gibt (form, daten) zurück; daten enthält Lochabstand, Zentrier-Ø usw.
    """
    kante = 56.4
    fase = 4.0                        # Eckfase von Flansch und Körper
    flansch_t = 5.0
    lochabstand = 47.14
    loch_d = 5.1
    zentrier_d, zentrier_h = 38.1, 1.6
    kappe_t = 8.0                     # hintere Kappe (Kunststoff/Alu)
    koerper_kante = 56.0

    def quadrat(k, f, z0, h):
        a = k / 2
        pts = [V(a - f, -a, 0), V(a, -a + f, 0), V(a, a - f, 0), V(a - f, a, 0),
               V(-a + f, a, 0), V(-a, a - f, 0), V(-a, -a + f, 0), V(-a + f, -a, 0)]
        pts = [p + V(0, 0, z0) for p in pts] + [pts[0] + V(0, 0, z0)]
        return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))

    flansch = quadrat(kante, fase, 0, flansch_t)
    for sx in (-1, 1):
        for sy in (-1, 1):
            flansch = flansch.cut(Part.makeCylinder(loch_d / 2, flansch_t + 2,
                                                    V(sx * lochabstand / 2, sy * lochabstand / 2, -1)))
    koerper = quadrat(koerper_kante, fase + 1.5, flansch_t, laenge - flansch_t - kappe_t)
    kappe = quadrat(kante, fase, laenge - kappe_t, kappe_t)
    zentrier = Part.makeCylinder(zentrier_d / 2, zentrier_h, V(0, 0, -zentrier_h))
    welle = Part.makeCylinder(welle_d / 2, welle_l, V(0, 0, -zentrier_h - welle_l))
    # Abflachung an der Welle (0,5 mm tief, 15 mm lang ab Wellenende)
    welle = welle.cut(Part.makeBox(welle_d, welle_d, 15,
                                   V(welle_d / 2 - 0.5, -welle_d / 2, -zentrier_h - welle_l)))
    # Kabelaustritt seitlich an der Kappe: Tülle + Kabelstück
    w = math.radians(kabel_winkel)
    r = kante / 2
    tuelle = Part.makeBox(16, 8, 7, V(r - 1, -8, laenge - kappe_t + 0.5))
    tuelle.rotate(V(0, 0, 0), V(0, 0, 1), kabel_winkel)
    kabel = Part.makeCylinder(3, 25, V(0, 0, 0), V(1, 0, 0))
    kabel.translate(V(r + 7, -4, laenge - kappe_t / 2))
    kabel.rotate(V(0, 0, 0), V(0, 0, 1), kabel_winkel)
    form = flansch.fuse([koerper, kappe, zentrier, welle, tuelle, kabel]).removeSplitter()
    daten = dict(kante=kante, lochabstand=lochabstand, loch_d=loch_d, zentrier_d=zentrier_d,
                 zentrier_h=zentrier_h, welle_d=welle_d, welle_l=welle_l, laenge=laenge,
                 kabel_richtung=V(math.cos(w), math.sin(w), 0))
    return form, daten


def riemenscheibe_htd5m(zaehne=24, breite=15.0, bohrung=8.0, nabe_d=28.0, nabe_l=8.0,
                        bord_d=None):
    """HTD5M-Riemenscheibe mit Bordscheiben und Nabe (vereinfacht, ohne Zähne).

    Lage: Achse Z, Unterkante Bordscheibe in z = 0, Nabe oben."""
    teil_d = zaehne * 5.0 / math.pi
    aussen_d = teil_d - 1.14
    bord_d = bord_d or aussen_d + 7
    b = 1.5
    s = Part.makeCylinder(bord_d / 2, b)
    s = s.fuse(Part.makeCylinder(aussen_d / 2, breite + 1, V(0, 0, b)))
    s = s.fuse(Part.makeCylinder(bord_d / 2, b, V(0, 0, b + breite + 1)))
    h = 2 * b + breite + 1
    s = s.fuse(Part.makeCylinder(nabe_d / 2, nabe_l, V(0, 0, h)))
    s = s.cut(Part.makeCylinder(bohrung / 2, h + nabe_l + 2, V(0, 0, -1)))
    return s.removeSplitter(), dict(teil_d=teil_d, hoehe=h + nabe_l, zahnbereich=(b, b + breite + 1))


def hgr15(laenge, teilung=60.0, e=20.0):
    """Profilschiene HGR15. Lage: Unterseite in z = 0, Länge entlang Y ab y = 0,
    Schienenmitte x = 0. Bohrungen Ø4,5 mit Senkung Ø7,5 von oben."""
    s = Part.makeBox(15, laenge, 15, V(-7.5, 0, 0))
    y = e
    while y <= laenge - e + 1e-6:
        s = s.cut(Part.makeCylinder(2.25, 17, V(0, y, -1)))
        s = s.cut(Part.makeCylinder(3.75, 5.3, V(0, y, 15 - 5.3)))
        y += teilung
    return s


def hgh15ca():
    """Wagen HGH15CA. Lage: Schienenunterkante z = 0 (Wagen sitzt auf der
    Schiene), Montagefläche oben z = 28, Mitte x = y = 0, Länge entlang Y.
    4x M4 im Lochbild 26 x 26 von oben."""
    w, l, h, h1 = 34.0, 61.4, 28.0, 4.3
    s = Part.makeBox(w, l, h - h1, V(-w / 2, -l / 2, h1))
    s = s.cut(Part.makeBox(16, l + 2, 15 - h1 + 0.5, V(-8, -l / 2 - 1, h1 - 0.01)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            s = s.cut(Part.makeCylinder(1.65, 6, V(sx * 13, sy * 13, h - 5.9)))
    return s


def sfu1204(laenge):
    """Kugelumlaufspindel Ø12, Achse Z, von z = 0 bis laenge (ohne Gewindedarstellung)."""
    return Part.makeCylinder(6.0, laenge)


def sfu1204_mutter():
    """Mutter SFU1204: Flansch Ø42 x 8 (6x Ø4,5 auf Teilkreis 32), Körper Ø22,
    Gesamtlänge 35. Lage: Achse Z, Flanschoberseite in z = 0, Körper nach unten."""
    s = Part.makeCylinder(21.0, 8.0, V(0, 0, -8))
    s = s.fuse(Part.makeCylinder(11.0, 35.0, V(0, 0, -35)))
    for i in range(6):
        w = math.radians(60 * i)
        s = s.cut(Part.makeCylinder(2.25, 10, V(16 * math.cos(w), 16 * math.sin(w), -9)))
    s = s.cut(Part.makeCylinder(6.0, 37, V(0, 0, -36)))
    return s.removeSplitter()


def fk10(loch=18.0):
    """Festlager FK10 (vereinfacht): Flansch 42 x 42 x 10 oben, Körper Ø34 x 17
    darunter. Lage: Achse Z, Flanschoberseite z = 0."""
    s = Part.makeBox(42, 42, 10, V(-21, -21, -10))
    s = s.fuse(Part.makeCylinder(17.0, 17.0, V(0, 0, -27)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            s = s.cut(Part.makeCylinder(2.25, 12, V(sx * loch, sy * loch, -11)))
    s = s.cut(Part.makeCylinder(6.0, 30, V(0, 0, -28)))
    return s.removeSplitter()


def kupplung(d=25.0, l=30.0, bohrung=8.0):
    """Wellenkupplung (Balg/Klaue) Ø25 x 30, beidseitig Bohrung Ø8. Achse Z ab z = 0."""
    return Part.makeCylinder(d / 2, l).cut(Part.makeCylinder(bohrung / 2, l + 2, V(0, 0, -1)))


def brenner_sp80m(schaft_d=32.0, laenge=250.0):
    """Maschinenbrenner (Platzhalter für SP80M): Schaft Ø32, Kegel zur Düse.
    Lage: Achse Z, Düsenspitze in z = 0, Schaft nach oben."""
    kegel = Part.makeCone(6.0, schaft_d / 2, 35.0)
    schaft = Part.makeCylinder(schaft_d / 2, laenge - 35.0, V(0, 0, 35.0))
    schlauch = Part.makeCylinder(9.0, 40.0, V(0, 0, laenge))
    return kegel.fuse([schaft, schlauch]).removeSplitter()
