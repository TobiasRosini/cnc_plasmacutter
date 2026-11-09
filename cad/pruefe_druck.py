#!/usr/bin/env python3
"""
Druckbarkeit aller Druckteile (STL im Repository), ohne FreeCAD, ohne numpy.

Jedes Teil wird in den 6 Lagen auf seinen Hauptachsen geprüft. Kritisch ist jede nach
unten zeigende Fläche, die flacher als 45° ist (Normale z < -cos 45°) und nicht auf dem
Bett liegt. Zusammenhängende kritische Facetten bilden eine Stelle; Stellen mit kleiner
Spannweite (bis KLEIN mm, z. B. Oberseite von Querbohrungen) und waagerechte bis BRUECKE mm
(Decke über Muttertasche oder Senkung, kurze Brücke) gelten als druckbar. Die beste Lage hat die kleinste größte Spannweite, dann die kleinste Fläche an
größeren Stellen.

  grün: in der besten Lage keine größeren Stellen
  gelb: größere Stellen vorhanden (Brücke oder freier Überhang, von Hand ansehen)

Aufruf:
  python3 cad/pruefe_druck.py            -> cad/druckbarkeit.txt
"""
import math
import os
import struct
import subprocess

CAD = os.path.dirname(os.path.abspath(__file__))
GRENZ_NZ = -math.cos(math.radians(45.0))
KLEIN = 6.0         # mm Spannweite, darunter überbrückbar (Oberseite von Querbohrungen)
BRUECKE = 10.0      # mm Spannweite waagerechter Stellen: kurze Brücke (Decke über Muttertasche, Senkung)
BETT_TOL = 0.05
MIN_BETT = 50.0     # mm² Auflage, sonst Lage verworfen

# Lage: Modellachse, die beim Druck nach oben zeigt -> Drehung (nur echte Drehungen)
LAGEN = {
    "+Z oben": lambda x, y, z: (x, y, z),
    "-Z oben": lambda x, y, z: (x, -y, -z),
    "+X oben": lambda x, y, z: (y, z, x),
    "-X oben": lambda x, y, z: (y, -z, -x),
    "+Y oben": lambda x, y, z: (z, x, y),
    "-Y oben": lambda x, y, z: (z, -x, -y),
}


def lies_stl(pfad):
    with open(pfad, "rb") as f:
        daten = f.read()
    if daten[:5] == b"solid" and b"facet" in daten[:300]:
        tri, akt = [], []
        for z in daten.decode(errors="ignore").splitlines():
            z = z.strip()
            if z.startswith("vertex"):
                akt.append(tuple(float(v) for v in z.split()[1:4]))
                if len(akt) == 3:
                    tri.append(akt)
                    akt = []
        return tri
    n = struct.unpack("<I", daten[80:84])[0]
    tri = []
    for i in range(n):
        o = 84 + 50 * i
        w = struct.unpack("<12f", daten[o:o + 48])
        tri.append([w[3:6], w[6:9], w[9:12]])
    return tri


def normale(a, b, c):
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    l = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    if l == 0:
        return (0.0, 0.0, 0.0), 0.0
    return (n[0] / l, n[1] / l, n[2] / l), l / 2


def bewerte(tri):
    zmin = min(p[2] for t in tri for p in t)
    bett, krit = 0.0, []
    for i, t in enumerate(tri):
        n, a = normale(*t)
        if a == 0:
            continue
        zs = [p[2] for p in t]
        if max(zs) < zmin + BETT_TOL:
            if n[2] < -0.99:
                bett += a
            continue
        if n[2] < GRENZ_NZ:
            krit.append((i, n, a))
    # zusammenhängende Stellen über gemeinsame Kanten
    def key(p):
        return (round(p[0], 3), round(p[1], 3), round(p[2], 3))
    kanten = {}
    for i, _, _ in krit:
        t = tri[i]
        for k in range(3):
            e = tuple(sorted((key(t[k]), key(t[(k + 1) % 3]))))
            kanten.setdefault(e, []).append(i)
    eltern = {i: i for i, _, _ in krit}

    def wurzel(i):
        while eltern[i] != i:
            eltern[i] = eltern[eltern[i]]
            i = eltern[i]
        return i
    for fl in kanten.values():
        for j in fl[1:]:
            eltern[wurzel(j)] = wurzel(fl[0])
    gruppen = {}
    for i, n, a in krit:
        gruppen.setdefault(wurzel(i), []).append((i, n, a))
    stellen = []
    for g in gruppen.values():
        pts = [p for i, _, _ in g for p in tri[i]]
        xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
        dx, dy = max(xs) - min(xs), max(ys) - min(ys)
        flaeche = sum(a for _, _, a in g)
        waagerecht = all(n[2] < -0.99 for _, n, _ in g)
        stellen.append(dict(flaeche=flaeche, spann=min(dx, dy), laenge=max(dx, dy),
                            hoehe=min(zs) - zmin, waagerecht=waagerecht,
                            mitte=((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)))
    gross = [s for s in stellen if s["spann"] > (BRUECKE if s["waagerecht"] else KLEIN)]
    return bett, stellen, gross


def main():
    stls = subprocess.run(["git", "ls-files", "*.stl"], cwd=os.path.dirname(CAD),
                          capture_output=True, text=True).stdout.split()
    zeilen, gruen, gelb = [], [], []
    for rel in sorted(stls):
        tri0 = lies_stl(os.path.join(os.path.dirname(CAD), rel))
        beste = None
        for name, f in LAGEN.items():
            tri = [[f(*p) for p in t] for t in tri0]
            bett, stellen, gross = bewerte(tri)
            if bett < MIN_BETT:
                continue
            wert = (max([s["spann"] for s in gross] or [0.0]), sum(s["flaeche"] for s in gross), -bett)
            if beste is None or wert < beste[0]:
                beste = (wert, name, bett, stellen, gross, tri)
        teil = os.path.splitext(os.path.basename(rel))[0]
        if beste is None:
            gelb.append(teil)
            zeilen.append("GELB  %-28s keine Lage mit ebener Auflage >= %.0f mm²" % (teil, MIN_BETT))
            continue
        _, lage, bett, stellen, gross, tri = beste
        hoehe = max(p[2] for t in tri for p in t) - min(p[2] for t in tri for p in t)
        klein = len(stellen) - len(gross)
        if not gross:
            gruen.append(teil)
            zeilen.append("GRÜN  %-28s Lage %s, Auflage %.0f mm², Höhe %.0f mm, %d kleine Stellen"
                          % (teil, lage, bett, hoehe, klein))
        else:
            gelb.append(teil)
            zeilen.append("GELB  %-28s Lage %s, Auflage %.0f mm², Höhe %.0f mm, %d kleine Stellen, %d größere:"
                          % (teil, lage, bett, hoehe, klein, len(gross)))
            for s in sorted(gross, key=lambda s: -s["flaeche"]):
                zeilen.append("        %-10s %6.0f mm², Spannweite %5.1f, Länge %5.1f, %5.1f mm über dem Bett, "
                              "Mitte (%.0f, %.0f)"
                              % ("waagerecht" if s["waagerecht"] else "schräg", s["flaeche"], s["spann"],
                                 s["laenge"], s["hoehe"], s["mitte"][0], s["mitte"][1]))
    with open(os.path.join(CAD, "druckbarkeit.txt"), "w") as f:
        f.write("Druckbarkeit (Überhang flacher als 45° = kritisch; schräge Stellen bis %.0f mm und "
                "waagerechte bis %.0f mm Spannweite gelten als druckbar)\n" % (KLEIN, BRUECKE))
        f.write("Lage: Modellachse, die beim Druck nach oben zeigt (Koordinaten wie im Teileskript)\n")
        f.write("grün %d, gelb %d\n\n" % (len(gruen), len(gelb)))
        f.write("\n".join(zeilen) + "\n")
    print("grün %d, gelb %d -> cad/druckbarkeit.txt" % (len(gruen), len(gelb)))


if __name__ == "__main__":
    main()
