# -*- coding: utf-8 -*-
"""
Werkstückauflage in der Wanne: Kammträger und Auflageleisten (Opferleisten), lose
gesteckt, ohne Schrauben im Wasser.

- Kammträger: Stahlblech 3 mm hochkant, längs (Y) auf dem Wannenboden. Sie kreuzen
  alle Querrohre des Wannenkäfigs, die Last geht durch den PE-Boden direkt in die
  Rohre. Oben Schlitze im Raster 25 mm; normal steckt man jede zweite Position
  (Teilung 50), für kleine Teile alle. Unten Aussparungen für Wasser und Schlamm,
  der mittlere Träger bei -440 auch über dem Ablauf (unterbau ablauf).
- Schutzleisten: Stahlblech 3 mm hochkant, längs (Y) innen vor dem Bördel der Längs-
  wände, lose auf dem Wannenboden zwischen Bördel und Leistenenden. Der PE-Bördel liegt
  über dem Wasser und 1 mm unter dem Blech; am Rand trifft Strahl und Schlacke so Stahl.
  Dazu Softlimit X (schnitt_x): nie direkt über dem Bördel schneiden.
- Auflageleisten: Flachstahl 50 x 3, quer (X), 524 lang (zwischen den Schutzleisten).
  Oberkante 1 mm über dem Bördel = Rahmenoberkante = Blechunterseite. Bis auf die
  obersten 15 mm stehen sie im Wasser.

Koordinaten wie Wannenkäfig: x/y = Wannenmitte, z = Rahmenoberkante.

Aufruf:
  python3 cad/live.py cad/auflage/auflage.py
"""
import os
import sys
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))
import fc_dok  # noqa: E402

P = dict(
    # Wanne (wanne.py / wannenkaefig.py)
    boden_z=-117.0,             # Innenseite Wannenboden (Standfläche -120 + Wand 3)
    boden_innen=(550.0, 1100.0),
    oeffnung=(540.0, 1137.0),   # lichte Öffnung am Bördel
    wasser_z=-15.0,
    ablauf_d=32.0,
    # Kammträger
    kt_t=3.0,
    kt_x=[-200.0, 0.0, 200.0],
    kt_l=1080.0,
    kt_oben=-30.0,
    kt_fase=10.0,               # unten an den Enden (Rundung Boden/Wand R8)
    schlitz_b=3.5,
    schlitz_t=20.0,
    raster=25.0,
    n_raster=43,                # y -525 ... 525
    aussparung=(60.0, 15.0),    # Länge, Höhe unten
    aussparung_y=[0.0, -220.0, 220.0, -440.0, 440.0],   # zwischen den Käfig-Querrohren
    # Auflageleisten
    l_t=3.0,
    l_h=50.0,
    l_x=524.0,                  # 3 mm Luft zu den Schutzleisten
    l_teilung=2,                # jede zweite Rasterposition
    # Schutzleisten vor dem Bördel (Längsseiten)
    s_t=3.0,
    s_aussen=268.0,             # Außenfläche ab Wannenmitte (Bördel innen 270, Boden flach bis ca. 268)
    s_l=1080.0,
    s_oben=-2.0,                # 1 mm unter der Bördeloberkante, 2 mm unter dem Blech
    s_aussparung_y=[-330.0, -110.0, 110.0, 330.0],   # unten, Wasser/Schlamm zum Rand
    schnitt_abstand=5.0,        # Softlimit Düse: so weit innerhalb der Schutzleisten
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def raster_y():
    n = P["n_raster"]
    return [(i - (n - 1) / 2) * P["raster"] for i in range(n)]


def kammtraeger(x):
    t, l2 = P["kt_t"] / 2, P["kt_l"] / 2
    z0, z1 = P["boden_z"], P["kt_oben"]
    s = box(x - t, x + t, -l2, l2, z0, z1)
    f = P["kt_fase"]
    for sy in (-1, 1):                                   # Fasen unten an den Enden
        pts = [V(x - t - 1, sy * l2, z0 - 0.01), V(x - t - 1, sy * (l2 - f), z0 - 0.01),
               V(x - t - 1, sy * l2, z0 + f)]
        k = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(2 * t + 2, 0, 0))
        s = s.cut(k)
    for y in raster_y():
        b = P["schlitz_b"] / 2
        s = s.cut(box(x - t - 1, x + t + 1, y - b, y + b, z1 - P["schlitz_t"], z1 + 1))
    al, ah = P["aussparung"]
    for y in P["aussparung_y"]:
        s = s.cut(box(x - t - 1, x + t + 1, y - al / 2, y + al / 2, z0 - 1, z0 + ah))
    return s.removeSplitter()


def schutzleiste(sx):
    t, l2 = P["s_t"], P["s_l"] / 2
    x1 = sx * P["s_aussen"]
    x0 = x1 - sx * t
    z0, z1 = P["boden_z"], P["s_oben"]
    s = box(min(x0, x1), max(x0, x1), -l2, l2, z0, z1)
    f = P["kt_fase"]
    for sy in (-1, 1):                                   # Fasen unten an den Enden
        pts = [V(-1, sy * l2, z0 - 0.01), V(-1, sy * (l2 - f), z0 - 0.01), V(-1, sy * l2, z0 + f)]
        k = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(t + 2, 0, 0))
        k.translate(V(min(x0, x1), 0, 0))
        s = s.cut(k)
    al, ah = P["aussparung"]
    for y in P["s_aussparung_y"]:
        s = s.cut(box(min(x0, x1) - 1, max(x0, x1) + 1, y - al / 2, y + al / 2, z0 - 1, z0 + ah))
    return s.removeSplitter()


def leisten():
    lx, lt = P["l_x"] / 2, P["l_t"] / 2
    z1 = P["kt_oben"] - P["schlitz_t"] + P["l_h"]
    res = []
    for y in raster_y()[::P["l_teilung"]]:
        res.append(box(-lx, lx, y - lt, y + lt, z1 - P["l_h"], z1))
    return Part.makeCompound(res)


def main():
    kt = [kammtraeger(x) for x in P["kt_x"]]
    le = leisten()
    sl = [schutzleiste(sx) for sx in (-1, 1)]
    pfad = os.path.join(OUT, "auflage.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    fc_dok.teil(doc, "Kammtraeger", Part.makeCompound(kt), "stahl")
    fc_dok.teil(doc, "Auflageleisten", le, "stahl")
    fc_dok.teil(doc, "Schutzleisten", Part.makeCompound(sl), "stahl")
    fc_dok.speichern(doc, pfad, offen)
    kt[1].exportStep(os.path.join(OUT, "kammtraeger.step"))
    le.Solids[0].exportStep(os.path.join(OUT, "auflageleiste.step"))
    sl[1].exportStep(os.path.join(OUT, "schutzleiste.step"))

    z_ok = P["kt_oben"] - P["schlitz_t"] + P["l_h"]
    ry = raster_y()
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Kammträger: %d Stück, %.0f lang, %.0f hoch (Stahl %.0f mm), Schlitze %.1f x %.0f im Raster %.0f "
                "(%d Positionen, y %.0f bis %.0f)\n"
                % (len(P["kt_x"]), P["kt_l"], P["kt_oben"] - P["boden_z"], P["kt_t"], P["schlitz_b"],
                   P["schlitz_t"], P["raster"], len(ry), ry[0], ry[-1]))
        f.write("Auflageleisten: %d Stück (Teilung %.0f), Flachstahl %.0f x %.0f, %.0f lang; "
                "dicht gesteckt %d Stück\n"
                % (len(le.Solids), P["raster"] * P["l_teilung"], P["l_h"], P["l_t"], P["l_x"], len(ry)))
        f.write("Oberkante Leisten %.1f (Rahmen-OK = 0), im Wasser bis %.0f mm unter der Oberkante\n"
                % (z_ok, z_ok - P["wasser_z"]))
        f.write("Durch die Bördelöffnung %.0f x %.0f: Leisten %.0f (Luft %.0f je Seite), "
                "Kammträger %.0f (Luft %.0f je Ende)\n"
                % (P["oeffnung"][0], P["oeffnung"][1], P["l_x"], (P["oeffnung"][0] - P["l_x"]) / 2,
                   P["kt_l"], (P["oeffnung"][1] - P["kt_l"]) / 2))
        si = P["s_aussen"] - P["s_t"]
        f.write("Schutzleisten: 2 Stück, Blech %.0f, %.0f lang, %.0f hoch, Außenfläche x ±%.0f "
                "(Bördel innen ±%.0f, %.0f mm Luft), Leistenenden %.0f mm Luft\n"
                % (P["s_t"], P["s_l"], P["s_oben"] - P["boden_z"], P["s_aussen"],
                   P["oeffnung"][0] / 2, P["oeffnung"][0] / 2 - P["s_aussen"],
                   si - P["l_x"] / 2))
        sx_ = si - P["schnitt_abstand"]
        f.write("Softlimit Schneidbereich X: Düse ±%.0f um die Wannenmitte (%.0f breit, "
                "Wannenboden %.0f); Y unverändert ±%.0f (Bördel %.0f mm entfernt)\n"
                % (sx_, 2 * sx_, P["boden_innen"][0], P["boden_innen"][1] / 2,
                   (P["oeffnung"][1] - P["boden_innen"][1]) / 2))


if __name__ == "__main__":
    main()
