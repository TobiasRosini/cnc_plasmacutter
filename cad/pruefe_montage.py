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
import Part

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zusammenbau")
V = App.Vector

# Teile, die nicht verschraubt werden oder deren Bohrungen keine Schrauben sind
OHNE = ("Riemen", "Kette_", "Leitung", "W_Wanne\0", "Brenner", "Spindel", "Kupplung", "Ablauf",
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
    if "winkel" in na and "Portalbruecke" in nb and d < 4.0:
        return "M3 der X-Riemenklemme endet in der Mutter innen an der Sattelrückwand (Schraube nicht länger als Klemmplatte + Wand)"
    if "winkel" in na and "Portalbruecke" in nb:
        return "Senkschraube M4 im Sattelboden, liegt unter der Brücke (vor der Brücke montieren)"
    if "spannschlitten" in na:
        return "Muttertasche/Schraube endet im Schlitten"
    if "z_traeger" in na and "Brenner" in nb:
        return "Klemmschraube drückt auf den Brennerschaft"
    if "motorbock" in na and "Motor_X" in nb:
        return "Langloch zum Spannen: der Motor wird darin verschoben"
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
        if any(k in na + "\0" for k in OHNE):
            continue
        for c, a, t0, t1, r in bohrungen(sa):
            for ende, vz in ((t1, 1), (t0, -1)):
                # nur das anliegende Nachbarteil (bis 3 mm hinter dem Bohrungsende)
                pts = [c + a * (ende + vz * d) for d in (0.3, 1.0, 2.0, 3.0)]
                for nb, sb in teile:
                    if nb == na or any(k in nb + "\0" for k in ("Riemen", "Kette_", "Leitung", "W_Wanne\0", "Ablauf")):
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
    # Bohrungen, die sich innerhalb eines Teils schneiden (z. B. Einsatz quer durch
    # eine Schraubenbohrung)
    schnitte = []
    for na, sa in teile:
        if any(k in na + "\0" for k in OHNE):
            continue
        zyl = []
        for c, a, t0, t1, r in bohrungen(sa):
            zyl.append((a, r, Part.makeCylinder(r, max(t1 - t0, 0.1), c + a * t0, a)))
        for i in range(len(zyl)):
            for j in range(i + 1, len(zyl)):
                if abs(zyl[i][0].dot(zyl[j][0])) > 0.99:
                    continue
                if not zyl[i][2].BoundBox.intersect(zyl[j][2].BoundBox):
                    continue
                v = zyl[i][2].common(zyl[j][2])
                if v.Volume > 0.05:
                    m = v.BoundBox.Center
                    schnitte.append((na, round(2 * zyl[i][1], 1), round(2 * zyl[j][1], 1),
                                     round(m.x), round(m.y), round(m.z)))
    # doppelte (beide Seiten einer Bohrung) zusammenfassen
    eindeutig = sorted(set(funde))
    offen, gewollt = [], []
    for e in eindeutig:
        grund = GEWOLLT_GRUND(e)
        (gewollt if grund else offen).append((e, grund))
    with open(os.path.join(OUT, "montage.txt"), "w") as f:
        f.write("Bohrungen ohne Gegenstück im Nachbarteil: %d offen, %d gewollt\n"
                % (len(offen), len(gewollt)))
        f.write("Bohrungen, die sich im selben Teil schneiden: %d\n" % len(set(schnitte)))
        for na, d1, d2, x, y, z in sorted(set(schnitte)):
            f.write("SCHNITT %s: Ø%.1f und Ø%.1f bei (%d, %d, %d)\n" % (na, d1, d2, x, y, z))
        for (na, nb, x, y, z, d), _ in offen:
            f.write("OFFEN %s (Ø%.1f bei %.1f, %.1f, %.1f) trifft %s ohne Bohrung/Gewinde\n"
                    % (na, d, x, y, z, nb))
        for (na, nb, x, y, z, d), grund in gewollt:
            f.write("gewollt %s -> %s (Ø%.1f bei %.1f, %.1f, %.1f): %s\n"
                    % (na, nb, d, x, y, z, grund))


main()
