# -*- coding: utf-8 -*-
"""
Grundrahmen des Plasmatisches aus Stahl-Rechteckrohr 40x40x3.

Konzept (nur gerade Schnitte, keine Gehrungen, alles stumpf verschweißt):
  - Oben: 2 Längsträger (Y) über die volle Länge, tragen die HGR15-Schienen;
    M4-Gewinde direkt in die Rohroberseite geschnitten.
    2 Querträger (X) stumpf zwischen die Längsträger.
  - 4 Eckbeine stumpf unter die Längsträger, unten Fußplatten.
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
    fuss_dicke=8.0,             # Fußplatte unter jedem Bein
    fuss_kante=100.0,
    fuss_loch=13.0,             # z. B. Stellfuß M12 oder Lenkrolle
    unten_uk=100.0,             # Unterkante unterer Rahmen über Boden

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
    ek_stuetze_y=[10.0, 30.0],                   # M6-Nietmuttern außen (Kettenstützen links), ab Rahmenende
    ek_stuetze_z=-20.0,                          # ab Rahmen-OK
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
    - Untertisch (UT_): Beine, Fußplatten, unterer Rahmen, Mittelquerrohre und ein
      eigener oberer Rahmen direkt unter dem Oberrahmen; daran hängt der Wannenkäfig.
    Verschraubt mit M8 senkrecht durch die aufeinanderliegenden Querrohre an beiden
    Enden (dort liegen keine Schienen und keine Halter)."""
    r = P["rohr"]
    ax, ay = P["aussen_x"], P["aussen_y"]
    z_ok = P["hoehe_ok"]
    z_oben = z_ok - r                    # Unterkante Oberrahmen = Oberkante Untertisch
    z_fuss = P["fuss_dicke"]
    z_u = P["unten_uk"]
    teile = {}

    # ----- Oberrahmen
    GRUPPE[0] = "Oberrahmen"
    for i, x0 in enumerate((0.0, ax - r)):
        lt = rohr("Längsträger oben", x0, 0, z_oben, ay, "y")
        for y in schienen_loecher():
            lt = lt.cut(Part.makeCylinder(P["m4_kern"] / 2, P["wand"] + 2,
                                          V(x0 + r / 2, y, z_ok - P["wand"] - 1)))
        # M6-Nietmuttern für Y-Motorhalter (hinten) und Umlenkhalter (vorn)
        y_a, y_e = P["schiene_y0"], P["schiene_y0"] + P["schiene_laenge"]
        for dx, dy in P["halter_loecher"]:
            for y in (y_a - dy, y_e + dy):
                lt = lt.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                              V(x0 + r / 2 + dx, y, z_ok - P["wand"] - 1)))
        # M8 quer für die Stützen der Y-Energiekette (nur links, an beiden Enden)
        if i == 0:
            for dy in P["ek_stuetze_y"]:
                for y in (dy, ay - dy):
                    lt = lt.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                                  V(-1, y, z_ok + P["ek_stuetze_z"]), V(1, 0, 0)))
        teile["OR_Laengstraeger_%s" % "LR"[i]] = lt
    for i, y0 in enumerate((0.0, ay - r)):
        q = rohr("Querträger oben", r, y0, z_oben, ax - 2 * r, "x")
        for x in P["trenn_schrauben_x"]:                 # unten Durchgang, oben Zugang
            q = q.cut(Part.makeCylinder(P["m8_durchgang"] / 2, P["wand"] + 2, V(x, y0 + r / 2, z_oben - 1)))
            q = q.cut(Part.makeCylinder(P["zugang_m8_d"] / 2, P["wand"] + 2,
                                        V(x, y0 + r / 2, z_ok - P["wand"] - 1)))
        teile["OR_Quertraeger_%s" % "VH"[i]] = q

    # ----- Untertisch
    GRUPPE[0] = "Untertisch"
    z_ut = z_oben - r                    # Unterkante oberer Rahmen Untertisch
    bein_l = z_oben - z_fuss
    for i, (x0, y0) in enumerate([(0, 0), (ax - r, 0), (0, ay - r), (ax - r, ay - r)]):
        teile["UT_Bein_%d" % (i + 1)] = rohr("Bein", x0, y0, z_fuss, bein_l, "z")
        fk = P["fuss_kante"]
        fx = min(max(x0 + r / 2 - fk / 2, 0), ax - fk)
        fy = min(max(y0 + r / 2 - fk / 2, 0), ay - fk)
        fp = box(fx, fx + fk, fy, fy + fk, 0, z_fuss)
        fp = fp.cut(Part.makeCylinder(P["fuss_loch"] / 2, z_fuss + 2,
                                      V(x0 + r / 2, y0 + r / 2, -1)))
        teile["UT_Fussplatte_%d" % (i + 1)] = fp
    for i, x0 in enumerate((0.0, ax - r)):
        lo = rohr("Längsrohr Untertisch oben", x0, r, z_ut, ay - 2 * r, "y")
        xi = x0 + r - P["wand"] - 1 if i == 0 else x0 - 1      # Innenwand (zum Käfig)
        for y in P["kaefig_schrauben_y"]:
            lo = lo.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, P["wand"] + 2,
                                          V(xi, P["wanne_mitte_y"] + y, z_ut + r - 10.0),
                                          V(1, 0, 0)))
        teile["UT_Laengsrohr_oben_%s" % "LR"[i]] = lo
        teile["UT_Laengsrohr_unten_%s" % "LR"[i]] = rohr(
            "Längsrohr unten", x0, r, z_u, ay - 2 * r, "y")
    for i, y0 in enumerate((0.0, ay - r)):
        q = rohr("Querrohr Untertisch oben", r, y0, z_ut, ax - 2 * r, "x")
        for x in P["trenn_schrauben_x"]:                 # Nietmutter M8 in der Oberseite
            q = q.cut(Part.makeCylinder(P["nietmutter_m8_d"] / 2, P["wand"] + 2,
                                        V(x, y0 + r / 2, z_oben - P["wand"] - 1)))
        teile["UT_Querrohr_oben_%s" % "VH"[i]] = q
        teile["UT_Querrohr_unten_%s" % "VH"[i]] = rohr(
            "Querrohr unten", r, y0, z_u, ax - 2 * r, "x")
    for i, a in enumerate(P["mitte_quer"]):
        y0 = ay * a - r / 2
        teile["UT_Querrohr_mitte_%d" % (i + 1)] = rohr(
            "Querrohr Mitte (unten)", r, y0, z_u, ax - 2 * r, "x")
    return teile


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

    pfad = os.path.join(OUT, "grundrahmen.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    for name, shp in teile.items():
        fc_dok.teil(doc, name, shp, "stahl")
    fc_dok.teil(doc, "Dummy_Schienen_HGR15", dm["Dummy_Schienen_HGR15"], "dummy")
    fc_dok.teil(doc, "Dummy_Wanne", dm["Dummy_Wanne"], "wanne", 60)
    fc_dok.speichern(doc, pfad, offen)
    Part.makeCompound(list(teile.values())).exportStep(
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
        f.write("\nFußplatten: 4x %gx%gx%g mm, Bohrung Ø%g\n"
                % (P["fuss_kante"], P["fuss_kante"], P["fuss_dicke"], P["fuss_loch"]))
        f.write("Verschraubung Untertisch/Oberrahmen: %d x M8 senkrecht (je Ende %d), "
                "M8x16 durch die Unterseite des oberen Querrohrs (Zugang Ø16 von oben) "
                "in Nietmuttern M8 im unteren Querrohr\n"
                % (2 * len(P["trenn_schrauben_x"]), len(P["trenn_schrauben_x"])))
        f.write("Schienengewinde: 2x %d x M4 (Kernloch Ø%.1f), Teilung %g, "
                "erstes Loch %g mm vom Schienenende\n"
                % (len(schienen_loecher()), P["m4_kern"], P["schiene_teilung"], P["schiene_e"]))

    alle = Part.makeCompound(list(teile.values()))
    bb = alle.BoundBox
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Außenmaß Rahmen: %.0f x %.0f x %.0f mm (X x Y x Z)\n"
                % (bb.XLength, bb.YLength, bb.ZLength))
        f.write("Lichtes Innenmaß zwischen den Rohren: %.0f x %.0f mm (Wanne %g x %g)\n"
                % (P["innen_x"], P["innen_y"], P["wanne_x"], P["wanne_y"]))
        f.write("Schienenabstand Mitte-Mitte: %.0f mm\n"
                % (P["schiene_x"][1] - P["schiene_x"][0]))
        f.write("Masse Stahl (Rohre + Fußplatten): %.1f kg\n"
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
        f.write("Durchbiegung Längsträger (Spannweite %.0f mm, 200 N mittig): %.3f mm\n"
                % ((P["aussen_y"] - r), durchbiegung(200.0, P["aussen_y"] - r)))


def durchbiegung(F, L):
    r, t = P["rohr"], P["wand"]
    I = (r ** 4 - (r - 2 * t) ** 4) / 12
    return F * L ** 3 / (48 * 210000 * I)


main()
