# -*- coding: utf-8 -*-
"""
Montageprüfung im Zusammenbau: Für jede Schraubenbohrung (Zylinder Ø2,8 bis
Ø13, kein Sackloch-Gewindeauslauf) wird die Achse über die Bohrung hinaus
verlängert. Trifft sie dort auf Material eines anderen Teils, muss dieses Teil
eine Bohrung oder ein Gewinde auf derselben Achse haben. Fehlt das, steht es in
cad/zusammenbau/montage.txt.
Geprüft wird nur das direkt anliegende Teil (bis 3 mm hinter dem Bohrungsende).

Aufruf (Zusammenbau muss offen sein):
  python3 cad/live.py cad/pruefe_montage.py
"""
import os
import FreeCAD as App

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zusammenbau")
V = App.Vector

# Teile, die nicht verschraubt werden oder deren Bohrungen keine Schrauben sind
OHNE = ("Riemen", "Kette_", "Leitung", "Wanne", "Brenner", "Spindel", "Kupplung", "Ablauf",
        "Schienen_HGR15\0")
R_MIN, R_MAX = 1.4, 6.6
VERL = 25.0


def bohrungen(shape):
    """Zylinderflächen, die Löcher sind (Achse außerhalb des Materials)."""
    res = []
    for f in shape.Faces:
        su = f.Surface
        if "Cylinder" not in su.TypeId or not R_MIN <= su.Radius <= R_MAX:
            continue
        a, c = su.Axis, su.Center
        ts = [(v.Point - c).dot(a) for v in f.Vertexes]
        if not ts:
            continue
        t0, t1 = min(ts), max(ts)
        mitte = c + a * ((t0 + t1) / 2)
        if shape.isInside(mitte, 0.01, True):
            continue                                   # Zapfen, kein Loch
        res.append((c, a, t0, t1, su.Radius))
    return res


def koaxial(shape, c, a, tol=0.4):
    for f in shape.Faces:
        su = f.Surface
        if "Cylinder" not in su.TypeId:
            continue
        if abs(abs(su.Axis.dot(a)) - 1) > 1e-3:
            continue
        w = su.Center - c
        if (w - a * w.dot(a)).Length < tol:
            return True
    return False


def GEWOLLT_GRUND(e):
    """Bekannte Fälle, in denen das Nachbarteil keine Bohrung braucht."""
    na, nb, x, y, z, d = e
    if "Flachstange" in na and "winkel" in nb:
        return "Senkung der Wagenschraube, wird vom Winkel überdeckt (erst Flachstange montieren)"
    if "winkel" in na and "Portalbruecke" in nb:
        return "Senkschraube M4 im Sattelboden, liegt unter der Brücke (vor der Brücke montieren)"
    if "spannschlitten" in na:
        return "Muttertasche/Schraube endet im Schlitten"
    if "z_traeger" in na and "Brenner" in nb:
        return "Klemmschraube drückt auf den Brennerschaft"
    if "Referenzschalter" in nb:
        return "Bohrung für den Schalter (Schalter steckt darin)"
    return ""


def main():
    doc = App.getDocument("zusammenbau")
    teile = []
    for o in doc.Objects:
        if o.TypeId not in ("App::Link", "Part::Feature"):
            continue
        sh = o.Shape
        if sh.isNull() or sh.Volume <= 0:
            continue
        teile.append((o.Name, sh))
    funde = []
    for na, sa in teile:
        if any(k in na for k in OHNE):
            continue
        for c, a, t0, t1, r in bohrungen(sa):
            for ende, vz in ((t1, 1), (t0, -1)):
                # nur das anliegende Nachbarteil (bis 3 mm hinter dem Bohrungsende)
                pts = [c + a * (ende + vz * d) for d in (0.3, 1.0, 2.0, 3.0)]
                for nb, sb in teile:
                    if nb == na or any(k in nb for k in ("Riemen", "Kette_", "Leitung", "Wanne", "Ablauf")):
                        continue
                    bb = sb.BoundBox
                    if not any(bb.isInside(p) for p in pts):
                        continue
                    if not any(sb.isInside(p, 0.01, False) for p in pts):
                        continue
                    if koaxial(sb, c, a):
                        continue
                    p = c + a * ((t0 + t1) / 2)
                    funde.append((na, nb, round(p.x, 1), round(p.y, 1), round(p.z, 1), round(2 * r, 1)))
    # doppelte (beide Seiten einer Bohrung) zusammenfassen
    eindeutig = sorted(set(funde))
    offen, gewollt = [], []
    for e in eindeutig:
        grund = GEWOLLT_GRUND(e)
        (gewollt if grund else offen).append((e, grund))
    with open(os.path.join(OUT, "montage.txt"), "w") as f:
        f.write("Bohrungen ohne Gegenstück im Nachbarteil: %d offen, %d gewollt\n"
                % (len(offen), len(gewollt)))
        for (na, nb, x, y, z, d), _ in offen:
            f.write("OFFEN %s (Ø%.1f bei %.1f, %.1f, %.1f) trifft %s ohne Bohrung/Gewinde\n"
                    % (na, d, x, y, z, nb))
        for (na, nb, x, y, z, d), grund in gewollt:
            f.write("gewollt %s -> %s (Ø%.1f bei %.1f, %.1f, %.1f): %s\n"
                    % (na, nb, d, x, y, z, grund))


main()
