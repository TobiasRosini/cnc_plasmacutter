# -*- coding: utf-8 -*-
"""
Grundrahmen des Plasmatisches aus Stahl-Rechteckrohr 40x40x3.

Konzept (nur gerade Schnitte, keine Gehrungen, alles stumpf verschweißt):
  - Oben: 2 Längsträger (Y) über die volle Länge, tragen die HGR15-Schienen;
    M4-Gewinde direkt in die Rohroberseite geschnitten.
    2 Querträger (X) stumpf zwischen die Längsträger.
  - 4 Eckbeine stumpf unter die Längsträger bis zur Rahmenunterkante, darunter
    je eine Eckplatte mit Lenkrolle und Stellfuß.
  - Unten: Längs- und Querrohre stumpf zwischen die Beine, dazu
    2 Mittelquerrohre als Auflage für den Wannenträger (folgt später).
  - Die Wanne (HDPE, ca. 600 x 1200 x 150) liegt innen zwischen den Beinen
    und kann zum Reinigen an der Stirnseite herausgezogen werden.

Koordinaten: Ursprung = Außenecke am Boden. X = quer (kurz), Y = längs
(Portal-Fahrachse), Z = oben.

Aufruf (Flatpak-FreeCAD, headless):
  flatpak run --command=FreeCADCmd org.freecad.FreeCAD $PWD/grundrahmen.py
Erzeugt: grundrahmen.FCStd, grundrahmen.step, zuschnitt.txt, pruefung.txt
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

# ---------------------------------------------------------------- Parameter
P = dict(
    rohr=40.0,                  # Rechteckrohr 40 x 40
    wand=3.0,
    dichte=7.85e-6,             # kg/mm³ Stahl

    # Wanne (grob, genaue Maße folgen)
    wanne_x=600.0,
    wanne_y=1200.0,
    wanne_h=150.0,
    wanne_spiel=20.0,           # je Seite zwischen Wanne und Rohr
    # Längsaufteilung: Der Brenner sitzt 136 mm vor der Brückenmitte. Die Schienen
    # liegen deshalb um diesen Betrag hinter der Wannenmitte, damit die Düse den
    # ganzen Wannenboden erreicht. Hinter dem Schienenanfang Platz für die
    # Y-Motoren, vor dem Schienenende für die Umlenkrollen.
    brenner_versatz=136.0,
    winkel_halb=90.0,           # halbe Länge Y-Winkel (Flachstange)
    platz_hinten=70.0,          # Rahmenende bis Schienenanfang (Y-Motoren)
    platz_vorn=70.0,            # Schienenende bis Rahmenende mindestens (Umlenkung)

    # Höhe
    hoehe_ok=850.0,             # Oberkante oberer Rahmen = Auflage der Schienen
    unten_uk=100.0,             # Unterkante unterer Rahmen = Unterkante Beine über z = 0

    # Eckplatten mit Lenkrolle und Stellfuß (Stand 17.11.2026). Die Beine enden an der
    # Rahmenunterkante, darunter je Ecke eine Platte unter Bein, Längs- und Querrohr.
    # z = 0 bleibt Bezugsebene der Koordinaten (100 unter der Rahmenunterkante); der Boden
    # liegt im Betrieb tiefer (siehe pruefung.txt). Im Betrieb heben die Füße die Rollen um
    # rad_luft vom Boden, zum Verfahren werden sie eingedreht.
    eckplatte=(175.0, 175.0, 10.0),              # x, y, Dicke; außen bündig
    # Lenkrolle mit Bremse Ø125 (Datenblatt Tobi 17.11.2026): 160 kg, Bauhöhe 150, Rad 36
    # breit, Platte 100 x 80, Lochbild 80 x 60, Langlöcher 9 x 14; Ausladung angenommen.
    # 4x M8 direkt in die Eckplatte.
    rolle=dict(rad_d=125.0, rad_b=36.0, bauhoehe=150.0, ausladung=45.0,
               platte=(80.0, 100.0), lochbild=(60.0, 80.0), loch_d=9.0),
    m8_kern=6.8,
    rolle_xy=122.0,             # Lenkachse ab beiden Außenkanten (diagonal vom Fuß weg)
    rad_luft=12.0,              # Rad über Boden im Betrieb
    # Stellfuß (Eigenbau): Gewindestange M16 unter der Beinmitte, Schweißmutter oben auf
    # der Eckplatte (im Bein), Kontermutter darunter, unten eine aufgeschweißte Mutter zum
    # Drehen und die Lagerung/der Teller (Platzhalter, wird an der Drehmaschine entschieden).
    # Eingedreht taucht die Stange ins Bein.
    fuss_loch=17.0,
    fuss_mutter=(24.0, 13.0),                    # M16 DIN 934: SW x Höhe
    fuss_konter=(24.0, 8.0),                     # M16 DIN 439
    fuss_teller=(50.0, 15.0),                    # Ø x Höhe, Platzhalter
    fuss_stange=200.0,
    fuss_luft=10.0,             # Teller über Boden beim Verfahren

    # Mittelquerrohre unten (Auflage Wannenträger), Lage als Anteil der Länge
    mitte_quer=[1 / 3, 2 / 3],

    # HGR15
    schiene_laenge=1300.0,
    schiene_breite=15.0,
    schiene_hoehe=15.0,
    schiene_teilung=60.0,
    schiene_e=20.0,             # Abstand erstes Loch vom Schienenende
    m4_kern=3.3,
    # Trennung Untertisch / Oberrahmen
    # Verbindungen ohne lange Bolzen: Schraube nur durch die nahe Wand, gegenüber ein
    # Zugangsloch, Gewinde in einer Nietmutter im anderen Rohr
    trenn_schrauben_x=[120.0, 360.0, 600.0],    # M8 x 16: Querrohr oben in Nietmutter Querrohr unten
    kaefig_schrauben_y=[-450.0, 0.0, 450.0],    # M6: Wannenkäfig in Nietmutter Längsrohr Untertisch
    m8_durchgang=9.0,
    nietmutter_m8_d=11.0,
    zugang_m8_d=16.0,           # Zugangsloch für Stecknuss/Inbus mit Scheibe
    # Befestigungen am Oberrahmen
    halter_loecher=[(-10.0, 52.0), (10.0, 52.0), (-10.0, 14.0), (10.0, 14.0)],  # (x ab Schiene, Abstand vor/hinter Schienenende)
    nietmutter_m6_d=9.0,        # M6-Nietmutter: 3 mm Wand trägt kein gutes M6-Gewinde
    ek_stuetze_y=[10.0, 30.0],                   # M6-Nietmuttern außen (Kettenstütze hinten rechts), ab Rahmenende
    ek_stuetze_z=-20.0,                          # ab Rahmen-OK
    ek_stuetze_vorn_y=[1446.0, 1466.0],          # Kettenstütze vorn (hinter dem Bein): Längsträger oben
    ek_stuetze_vorn_z=[-20.0, -60.0],            # und Längsrohr Untertisch oben (= energiekette stuetze_vorn_*)
    # Vorderer Querträger 80 x 40 x 4 flach: steht 40 mm vor den Untertisch über, darunter
    # greifen Schraubzwingen (Flachstangen zum Schneiden einspannen); Oberrahmen 40 länger
    qv_tiefe=80.0,
    qv_wand=4.0,
    or_ueberstand=40.0,
    # Querkanal (Unterbau): 2x M5 aus dem Kanal durch die Vorderwand in Nietmuttern im vorderen Bein rechts
    kanal_bein=[(12.0, 627.5), (28.0, 627.5)],   # Rückseite (x, z)
    nietmutter_m5_d=7.0,
    # Haube über dem Geräteraum (Unterbau): Seitenwände je 2x M5 in Nietmuttern in der
    # Innenseite der vorderen Beine (y ab Rahmenvorderkante, z) (= unterbau haube_bein)
    haube_bein=[(-20.0, 300.0), (-20.0, 560.0)],
    # Halter des Wannenablaufs: 2x M5 in Nietmuttern in der Innenseite des hinteren oberen
    # Querrohrs des Untertischs (x, z) (= unterbau ablauf_halter_m5)
    ablauf_halter_m5=[(345.0, 790.0), (375.0, 790.0)],
    geraeteboden_y=[560.0, 1050.0, 1420.0],      # M6-Nietmuttern oben in den unteren Längsrohren (= unterbau boden_loch_y)
    # Spritzschutz Y-Schienen: Flachstahl 50 x 3 innen an den Längsträgern, steht über die
    # Rahmenoberkante (Bleche dann höchstens 634 breit); zwischen den Y-Motor- und Umlenkhaltern
    schutz_t=3.0,
    schutz_ueber=25.0,
    schutz_unter=25.0,
    schutz_y=(80.0, 1360.0),
    schutz_niet_y=[120.0, 340.0, 560.0, 780.0, 1000.0, 1220.0],
    schutz_niet_z=-12.5,                         # ab Rahmen-OK, Blindniet Ø4
    niet_d=4.1,
)


def ableiten():
    r, s = P["rohr"], P["wanne_spiel"]
    P["innen_x"] = P["wanne_x"] + 2 * s
    P["aussen_x"] = P["innen_x"] + 2 * r
    # Wannenmitte so, dass Schienenanfang = platz_hinten
    wm = P["platz_hinten"] + P["schiene_laenge"] / 2 + P["brenner_versatz"]
    P["wanne_mitte_y"] = wm
    P["schiene_y0"] = P["platz_hinten"]
    vorn = max(P["schiene_y0"] + P["schiene_laenge"] + P["platz_vorn"],
               wm + P["wanne_y"] / 2 + s + r)
    P["aussen_y"] = vorn
    P["innen_y"] = vorn - 2 * r
    P["schiene_x"] = [r / 2, P["aussen_x"] - r / 2]   # Schienenmitte = Rohrmitte


# ---------------------------------------------------------------- Helfer
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


ZUSCHNITT = []
GRUPPE = ["Oberrahmen"]


def rohr(name, x0, y0, z0, laenge, achse):
    """Hohlprofil r x r x wand, Länge entlang 'x', 'y' oder 'z' ab (x0, y0, z0)."""
    r, t = P["rohr"], P["wand"]
    d = {"x": (laenge, r, r), "y": (r, laenge, r), "z": (r, r, laenge)}[achse]
    aussen = box(x0, x0 + d[0], y0, y0 + d[1], z0, z0 + d[2])
    o = [t if d[i] == r else -1 for i in range(3)]
    innen = box(x0 + o[0], x0 + d[0] - o[0], y0 + o[1], y0 + d[1] - o[1],
                z0 + o[2], z0 + d[2] - o[2])
    ZUSCHNITT.append((GRUPPE[0], name, laenge))
    return aussen.cut(innen)


# ---------------------------------------------------------------- Rahmen
def rahmen():
    """Zwei verschraubte Baugruppen:
    - Oberrahmen (OR_): Längsträger mit den Y-Schienen und Querträger, trägt das
      ganze Portal.
    - Untertisch (UT_): Beine, Eckplatten, unterer Rahmen, Mittelquerrohre und ein
      eigener oberer Rahmen direkt unter dem Oberrahmen; daran hängt der Wannenkäfig.
    Verschraubt mit M8 senkrecht durch die aufeinanderliegenden Querrohre an beiden
    Enden (dort liegen keine Schienen und keine Halter)."""
    r = P["rohr"]
    ax, ay = P["aussen_x"], P["aussen_y"]
    z_ok = P["hoehe_ok"]
    z_oben = z_ok - r                    # Unterkante Oberrahmen = Oberkante Untertisch
    z_u = P["unten_uk"]
    teile = {}

    # ----- Oberrahmen
    GRUPPE[0] = "Oberrahmen"
    for i, x0 in enumerate((0.0, ax - r)):
        ayo = ay + P["or_ueberstand"]                    # Oberrahmen vorn länger
        lt = rohr("Längsträger oben", x0, 0, z_oben, ayo, "y")
        for y in schienen_loecher():
            lt = lt.cut(Part.makeCylinder(P["m4_kern"] / 2, P["wand"] + 2,
                                          V(x0 + r / 2, y, z_ok - P["wand"] - 1)))
        # M6-Nietmuttern für Y-Motorhalter (hinten) und Umlenkhalter (vorn)
        y_a, y_e = P["schiene_y0"], P["schiene_y0"] + P["schiene_laenge"]
        for dx, dy in P["halter_loecher"]:
            for y in (y_a - dy, y_e + dy):
                lt = lt.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                              V(x0 + r / 2 + dx, y, z_ok - P["wand"] - 1)))
        # M6 quer für die Stützen der Y-Energiekette (nur rechts): hinten am Rahmenende,
        # vorn hinter dem Bein
        if i == 0:
            for y in P["ek_stuetze_y"] + P["ek_stuetze_vorn_y"]:
                lt = lt.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                              V(-1, y, z_ok + P["ek_stuetze_z"]), V(1, 0, 0)))
        xi = x0 + r - P["wand"] - 1 if i == 0 else x0 - 1      # Innenwand (Spritzschutz)
        for y in P["schutz_niet_y"]:
            lt = lt.cut(Part.makeCylinder(P["niet_d"] / 2, P["wand"] + 2,
                                          V(xi, y, z_ok + P["schutz_niet_z"]), V(1, 0, 0)))
        teile["OR_Laengstraeger_%s" % "LR"[i]] = lt
    for i, y0 in enumerate((0.0, ay - r)):
        if i == 1:                                       # vorn 80 x 40 x 4 flach, steht über
            tq, qw = P["qv_tiefe"], P["qv_wand"]
            q = box(r, ax - r, y0, y0 + tq, z_oben, z_ok).cut(
                box(r - 1, ax - r + 1, y0 + qw, y0 + tq - qw, z_oben + qw, z_ok - qw))
            ZUSCHNITT.append(("80x40x4", "Querträger vorn (Oberrahmen)", ax - 2 * r))
        else:
            q = rohr("Querträger oben", r, y0, z_oben, ax - 2 * r, "x")
        for x in P["trenn_schrauben_x"]:                 # unten Durchgang, oben Zugang
            q = q.cut(Part.makeCylinder(P["m8_durchgang"] / 2, P["wand"] + 2, V(x, y0 + r / 2, z_oben - 1)))
            q = q.cut(Part.makeCylinder(P["zugang_m8_d"] / 2, P["wand"] + 2,
                                        V(x, y0 + r / 2, z_ok - P["wand"] - 1)))
        teile["OR_Quertraeger_%s" % "VH"[i]] = q

    # ----- Untertisch
    GRUPPE[0] = "Untertisch"
    z_ut = z_oben - r                    # Unterkante oberer Rahmen Untertisch
    z_u = P["unten_uk"]
    bein_l = z_oben - z_u
    for i, (x0, y0) in enumerate([(0, 0), (ax - r, 0), (0, ay - r), (ax - r, ay - r)]):
        bein = rohr("Bein", x0, y0, z_u, bein_l, "z")
        if i == 2:                                       # vorn rechts: Querkanal (Rückseite)
            for x, z in P["kanal_bein"]:
                bein = bein.cut(Part.makeCylinder(P["nietmutter_m5_d"] / 2, P["wand"] + 2,
                                                  V(x0 + x, y0 - 1, z), V(0, 1, 0)))
        if i >= 2:                                       # vorn: Haube (Innenseite)
            xi = x0 + r - P["wand"] - 1 if x0 == 0 else x0 - 1
            for dy, z in P["haube_bein"]:
                bein = bein.cut(Part.makeCylinder(P["nietmutter_m5_d"] / 2, P["wand"] + 2,
                                                  V(xi, ay + dy, z), V(1, 0, 0)))
        teile["UT_Bein_%d" % (i + 1)] = bein
    for i, x0 in enumerate((0.0, ax - r)):
        lo = rohr("Längsrohr Untertisch oben", x0, r, z_ut, ay - 2 * r, "y")
        xi = x0 + r - P["wand"] - 1 if i == 0 else x0 - 1      # Innenwand (zum Käfig)
        for y in P["kaefig_schrauben_y"]:
            lo = lo.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                          V(xi, P["wanne_mitte_y"] + y, z_ut + r - 10.0),
                                          V(1, 0, 0)))
        if i == 0:                                       # Kettenstütze vorn
            z = z_ok + P["ek_stuetze_vorn_z"][1]
            for y in P["ek_stuetze_vorn_y"]:
                lo = lo.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                              V(-1, y, z), V(1, 0, 0)))
        teile["UT_Laengsrohr_oben_%s" % "LR"[i]] = lo
        lu = rohr("Längsrohr unten", x0, r, z_u, ay - 2 * r, "y")
        for y in P["geraeteboden_y"]:                    # Geräteboden: M6 von oben in Nietmuttern
            lu = lu.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                          V(x0 + r / 2, y, z_u + r - P["wand"] - 1)))
        teile["UT_Laengsrohr_unten_%s" % "LR"[i]] = lu
    for i, y0 in enumerate((0.0, ay - r)):
        q = rohr("Querrohr Untertisch oben", r, y0, z_ut, ax - 2 * r, "x")
        for x in P["trenn_schrauben_x"]:                 # Nietmutter M8 in der Oberseite
            q = q.cut(Part.makeCylinder(P["nietmutter_m8_d"] / 2, P["wand"] + 2,
                                        V(x, y0 + r / 2, z_oben - P["wand"] - 1)))
        if y0 == 0.0:                                    # hinten: Halter des Wannenablaufs (Innenseite)
            for x, z in P["ablauf_halter_m5"]:
                q = q.cut(Part.makeCylinder(P["nietmutter_m5_d"] / 2, P["wand"] + 2,
                                            V(x, r - P["wand"] - 1, z), V(0, 1, 0)))
        teile["UT_Querrohr_oben_%s" % "VH"[i]] = q
        teile["UT_Querrohr_unten_%s" % "VH"[i]] = rohr(
            "Querrohr unten", r, y0, z_u, ax - 2 * r, "x")
    for i, a in enumerate(P["mitte_quer"]):
        y0 = ay * a - r / 2
        teile["UT_Querrohr_mitte_%d" % (i + 1)] = rohr(
            "Querrohr Mitte (unten)", r, y0, z_u, ax - 2 * r, "x")
    return teile


def spritzschutz():
    """Flachstahl 50 x 3 innen an den Längsträgern, Blindnieten Ø4."""
    r, t, ax = P["rohr"], P["schutz_t"], P["aussen_x"]
    z0, z1 = P["hoehe_ok"] - P["schutz_unter"], P["hoehe_ok"] + P["schutz_ueber"]
    y0, y1 = P["schutz_y"]
    res = {}
    for name, x0, rich in (("R", r, 1), ("L", ax - r - t, -1)):
        s = box(x0, x0 + t, y0, y1, z0, z1)
        for y in P["schutz_niet_y"]:
            s = s.cut(Part.makeCylinder(P["niet_d"] / 2, t + 2,
                                        V(x0 - 1 if rich > 0 else x0 + t + 1, y,
                                          P["hoehe_ok"] + P["schutz_niet_z"]), V(rich, 0, 0)))
        res["OR_Spritzschutz_%s" % name] = s
    return res


def fuesse_rollen():
    """Eckplatten mit Schweißmutter, Stellfüße (Betriebsstellung) und Lenkrollen.
    Gibt (stahl, kauf, info) zurück."""
    r = P["rohr"]
    ax, ay = P["aussen_x"], P["aussen_y"]
    ex, ey, et = P["eckplatte"]
    z_pl = P["unten_uk"] - et
    form, d = kt.lenkrolle(**P["rolle"])
    z_rad = z_pl - d["bauhoehe"]
    boden = z_rad - P["rad_luft"]                    # Boden im Betrieb
    sw, mh = P["fuss_mutter"]
    kw, kh = P["fuss_konter"]
    td, th = P["fuss_teller"]
    z_stange = boden + th                            # Unterkante Stange = Unterkante Fußmutter
    stahl, kauf = {}, {}
    for i, (x0, y0) in enumerate([(0, 0), (ax - r, 0), (0, ay - r), (ax - r, ay - r)]):
        links, hinten = x0 == 0, y0 == 0
        c = V(x0 + r / 2, y0 + r / 2, 0)
        xp = 0.0 if links else ax - ex
        yp = 0.0 if hinten else ay - ey
        xa = P["rolle_xy"] if links else ax - P["rolle_xy"]
        ya = P["rolle_xy"] if hinten else ay - P["rolle_xy"]
        pl = box(xp, xp + ex, yp, yp + ey, z_pl, P["unten_uk"])
        pl = pl.cut(Part.makeCylinder(P["fuss_loch"] / 2, et + 2, V(c.x, c.y, z_pl - 1)))
        lx, ly = P["rolle"]["lochbild"]
        for sx in (-1, 1):
            for sy in (-1, 1):
                pl = pl.cut(Part.makeCylinder(P["m8_kern"] / 2, et + 2,
                                              V(xa + sx * lx / 2, ya + sy * ly / 2, z_pl - 1)))
        stahl["UT_Eckplatte_%d" % (i + 1)] = pl
        m = kt.sechskant(sw, mh, P["unten_uk"]).cut(
            Part.makeCylinder(8.0, mh + 2, V(0, 0, P["unten_uk"] - 1)))
        m.translate(V(c.x, c.y, 0))
        stahl["UT_Schweissmutter_M16_%d" % (i + 1)] = fc_dok.fest(m)
        f = Part.makeCylinder(8.0, P["fuss_stange"], V(0, 0, z_stange))
        f = f.fuse([kt.sechskant(sw, mh, z_stange),                 # aufgeschweißt, zum Drehen
                    Part.makeCylinder(td / 2, th, V(0, 0, boden)),  # Lagerung/Teller (Platzhalter)
                    kt.sechskant(kw, kh, z_pl - kh)]).removeSplitter()   # Kontermutter
        f.translate(V(c.x, c.y, 0))
        stahl["UT_Stellfuss_M16_%d" % (i + 1)] = fc_dok.fest(f)
        ro = form.copy()
        if not hinten:                               # Rad läuft zur Rahmenmitte nach
            ro.rotate(V(0, 0, 0), V(0, 0, 1), 180)
        ro.translate(V(xa, ya, z_pl))
        kauf["UT_Lenkrolle_%d" % (i + 1)] = fc_dok.fest(ro)
    hub = P["rad_luft"] + P["fuss_luft"]
    info = dict(z_rad=z_rad, boden=boden, huell_r=d["huell_r"],
                z_kranz=z_pl - 4.0 - 12.0, hub=hub,
                stange_oben=z_stange + P["fuss_stange"],
                ueber=z_pl - kh - (z_stange + mh))   # freie Stange zwischen Fußmutter und Kontermutter
    return stahl, kauf, info


def schienen_loecher():
    ay, L = P["aussen_y"], P["schiene_laenge"]
    y0 = P["schiene_y0"]
    n = int((L - 2 * P["schiene_e"]) // P["schiene_teilung"]) + 1
    return [y0 + P["schiene_e"] + i * P["schiene_teilung"] for i in range(n)]


# ---------------------------------------------------------------- Dummies
def dummies():
    d = {}
    ay, L, sb = P["aussen_y"], P["schiene_laenge"], P["schiene_breite"]
    z = P["hoehe_ok"]
    y0 = P["schiene_y0"]
    s = None
    for xc in P["schiene_x"]:
        k = kt.hgr15(L, P["schiene_teilung"], P["schiene_e"])
        k.translate(V(xc, y0, z))
        k = fc_dok.fest(k)
        s = k if s is None else s.fuse(k)
    d["Dummy_Schienen_HGR15"] = s
    # Wanne: Höhe hängt am Wannenträger, hier Oberkante 20 mm unter dem oberen Rahmen
    r, sp = P["rohr"], P["wanne_spiel"]
    zt = P["hoehe_ok"] - r - 20
    y0 = P["wanne_mitte_y"] - P["wanne_y"] / 2
    d["Dummy_Wanne"] = box(r + sp, r + sp + P["wanne_x"], y0, y0 + P["wanne_y"],
                           zt - P["wanne_h"], zt)
    return d


# ---------------------------------------------------------------- Hauptteil
def main():
    ableiten()
    teile = rahmen()
    dm = dummies()
    fr_stahl, fr_kauf, fr = fuesse_rollen()

    pfad = os.path.join(OUT, "grundrahmen.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    for name, shp in teile.items():
        fc_dok.teil(doc, name, shp, "stahl")
    for name, shp in spritzschutz().items():
        fc_dok.teil(doc, name, shp, "stahl")
    for name, shp in fr_stahl.items():
        fc_dok.teil(doc, name, shp, "stahl")
    for name, shp in fr_kauf.items():
        fc_dok.teil(doc, name, shp, "zukauf")
    fc_dok.teil(doc, "Dummy_Schienen_HGR15", dm["Dummy_Schienen_HGR15"], "dummy")
    fc_dok.teil(doc, "Dummy_Wanne", dm["Dummy_Wanne"], "wanne", 60)
    fc_dok.speichern(doc, pfad, offen)
    Part.makeCompound(list(teile.values()) + list(fr_stahl.values())).exportStep(
        os.path.join(OUT, "grundrahmen.step"))

    # Zuschnittliste je Baugruppe
    r, t = P["rohr"], P["wand"]
    kg_m = (r * r - (r - 2 * t) ** 2) * 1000 * P["dichte"]
    with open(os.path.join(OUT, "zuschnitt.txt"), "w") as f:
        f.write("Zuschnitt Rechteckrohr %gx%gx%g Stahl, alle Schnitte gerade (90°)\n" % (r, r, t))
        for gruppe in ("Untertisch", "Oberrahmen"):
            zus = {}
            for g_, name, l in ZUSCHNITT:
                if g_ == gruppe:
                    zus[(name, round(l, 1))] = zus.get((name, round(l, 1)), 0) + 1
            gesamt = sum(l * n for (_, l), n in zus.items())
            f.write("\n%s\n%-28s %10s %6s\n" % (gruppe, "Teil", "Länge mm", "Stk"))
            for (name, l), n in sorted(zus.items(), key=lambda e: -e[0][1]):
                f.write("%-28s %10.1f %6d\n" % (name, l, n))
            f.write("Summe: %.2f m (%.1f kg)\n" % (gesamt / 1000, gesamt / 1000 * kg_m))
        for g_, name, l in ZUSCHNITT:
            if g_ == "80x40x4":
                f.write("\nRechteckrohr 80x40x4 Stahl: %s %.1f mm, 1 Stk\n" % (name, l))
        f.write("\nEckplatten: 4x Flachstahl %gx%gx%g unter Bein, Längs- und Querrohr, außen "
                "bündig; Bohrung Ø%g unter der Beinmitte, 4x M8 (Kernloch Ø%g) im Lochbild %gx%g "
                "für die Lenkrolle (Lenkachse %g von beiden Außenkanten)\n"
                % (*P["eckplatte"], P["fuss_loch"], P["m8_kern"], *P["rolle"]["lochbild"],
                   P["rolle_xy"]))
        f.write("Schweißmuttern M16: 4 Stk oben auf die Eckplatten über die Bohrung (vor dem Bein "
                "anschweißen)\n")
        f.write("Stellfüße: 4x Gewindestange M16 x %g, unten Mutter M16 aufgeschweißt, "
                "Kontermutter M16 flach, Lagerung/Teller offen\n" % P["fuss_stange"])
        f.write("Verschraubung Untertisch/Oberrahmen: %d x M8 senkrecht (je Ende %d), "
                "M8x16 durch die Unterseite des oberen Querrohrs (Zugang Ø16 von oben) "
                "in Nietmuttern M8 im unteren Querrohr\n"
                % (2 * len(P["trenn_schrauben_x"]), len(P["trenn_schrauben_x"])))
        f.write("Schienengewinde: 2x %d x M4 (Kernloch Ø%.1f), Teilung %g, "
                "erstes Loch %g mm vom Schienenende\n"
                % (len(schienen_loecher()), P["m4_kern"], P["schiene_teilung"], P["schiene_e"]))

    alle = Part.makeCompound(list(teile.values())
                             + [v for k, v in fr_stahl.items() if "Eckplatte" in k])
    bb = Part.makeCompound(list(teile.values())).BoundBox
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Außenmaß Rahmen: %.0f x %.0f x %.0f mm (X x Y x Z)\n"
                % (bb.XLength, bb.YLength, bb.ZLength))
        f.write("Lichtes Innenmaß zwischen den Rohren: %.0f x %.0f mm (Wanne %g x %g)\n"
                % (P["innen_x"], P["innen_y"], P["wanne_x"], P["wanne_y"]))
        f.write("Schienenabstand Mitte-Mitte: %.0f mm\n"
                % (P["schiene_x"][1] - P["schiene_x"][0]))
        f.write("Masse Stahl (Rohre + Eckplatten): %.1f kg\n"
                % (alle.Volume * P["dichte"]))
        f.write("Stirnöffnung zum Herausziehen der Wanne: %.0f breit x %.0f hoch\n"
                % (P["innen_x"], P["hoehe_ok"] - r - (P["unten_uk"] + r)))
        # Überschneidungen zwischen Rohren (soll 0 sein, nur Stoßflächen)
        namen = list(teile)
        ueber = 0.0
        for i in range(len(namen)):
            for j in range(i + 1, len(namen)):
                a, b = teile[namen[i]], teile[namen[j]]
                if a.BoundBox.intersect(b.BoundBox):
                    v = a.common(b).Volume
                    if v > 1e-3:
                        f.write("Überschneidung %s / %s: %.1f mm³\n"
                                % (namen[i], namen[j], v))
                        ueber += v
        f.write("Überschneidungen gesamt: %.3f mm³\n" % ueber)
        f.write("Wanne / Rahmen: %.3f mm³\n" % alle.common(dm["Dummy_Wanne"]).Volume)
        # Stellfüße und Rollen
        f.write("\nStellfüße und Rollen (z = 0: Bezugsebene, %g unter der Rahmenunterkante)\n"
                % P["unten_uk"])
        f.write("Betrieb: Boden bei z = %.0f, Rahmen-OK %.0f mm über Boden, Räder %.0f mm frei, "
                "Stange zwischen Fußmutter und Kontermutter %.0f mm frei, Stange oben bei z = %.0f\n"
                % (fr["boden"], P["hoehe_ok"] - fr["boden"], P["rad_luft"], fr["ueber"],
                   fr["stange_oben"]))
        f.write("Verfahren: Rad unten bei z = %.0f, Rahmenunterkante %.0f über Boden, Füße %.0f mm "
                "eingedreht (Teller %.0f mm frei), Stange oben bei z = %.0f (im Bein)\n"
                % (fr["z_rad"], P["unten_uk"] - fr["z_rad"], fr["hub"], P["fuss_luft"],
                   fr["stange_oben"] + fr["hub"]))
        ax_, ay_ = P["aussen_x"], P["aussen_y"]
        f.write("Schwenkkreis Rolle R %.1f: %.1f mm innerhalb der Außenkanten\n"
                % (fr["huell_r"], P["rolle_xy"] - fr["huell_r"]))
        f.write("Radstand Verfahren: %.0f (X) x %.0f (Y) mm, Füße %.0f x %.0f\n"
                % (ax_ - 2 * P["rolle_xy"], ay_ - 2 * P["rolle_xy"], ax_ - r, ay_ - r))
        hinder_c = Part.makeCompound(list(teile.values()) + list(fr_stahl.values()))
        v_schw = 0.0
        for xa in (P["rolle_xy"], ax_ - P["rolle_xy"]):
            for ya in (P["rolle_xy"], ay_ - P["rolle_xy"]):
                zyl = Part.makeCylinder(fr["huell_r"], fr["z_kranz"] - fr["z_rad"],
                                        V(xa, ya, fr["z_rad"]))
                v_schw += zyl.common(hinder_c).Volume
        f.write("Schwenkkreis gegen Rahmen/Füße: %.1f mm³\n" % v_schw)
        v_k = sum(k.common(hinder_c).Volume for k in fr_kauf.values())
        stahl_c = Part.makeCompound(list(teile.values()))
        v_k += sum(k.common(stahl_c).Volume for n, k in fr_stahl.items())
        for n, k in fr_stahl.items():
            for n2, k2 in fr_stahl.items():
                if n < n2 and k.BoundBox.intersect(k2.BoundBox):
                    v_k += k.common(k2).Volume
        f.write("Füße/Rollen/Eckplatten gegen Rahmen und untereinander: %.3f mm³\n" % v_k)
        f.write("Durchbiegung Längsträger (Spannweite %.0f mm, 200 N mittig): %.3f mm\n"
                % ((P["aussen_y"] - r), durchbiegung(200.0, P["aussen_y"] - r)))


def durchbiegung(F, L):
    r, t = P["rohr"], P["wand"]
    I = (r ** 4 - (r - 2 * t) ** 4) / 12
    return F * L ** 3 / (48 * 210000 * I)


main()
