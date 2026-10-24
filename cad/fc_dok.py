# -*- coding: utf-8 -*-
"""
Gemeinsame Helfer für die CAD-Skripte: Dokument holen/neu anlegen,
Teile mit Farbe einfügen, speichern.

Läuft das Skript im offenen FreeCAD (über cad/live.py), wird ein bereits
geöffnetes Dokument derselben Datei wiederverwendet: Inhalt ersetzen,
Darstellung setzen, speichern. Ohne Oberfläche (FreeCADCmd) entsteht die
Datei neu, die Teile werden dann zumindest sichtbar gesetzt.

Vorhandene Objekte werden über ihren Namen aktualisiert (nicht gelöscht und
neu angelegt), damit Verknüpfungen aus dem Zusammenbau erhalten bleiben.

Achtung: Die Dokumente sind generiert. Was von Hand darin geändert wird,
geht beim nächsten Lauf verloren; Änderungen gehören ins Skript.
"""
import os
import FreeCAD as App
import Part

# Farbkonzept (festgelegt 20.10.2026): Stahl grau, Alu hellblau, 3D-Druck gelb,
# Zukaufteile grün (wenn nicht anders festgelegt), Riemen lila, Wanne wie sie ist
_STAHL = (0.55, 0.57, 0.60)
_ALU = (0.62, 0.80, 0.95)
_DRUCK = (0.98, 0.84, 0.18)
_ZUKAUF = (0.30, 0.68, 0.36)
_RIEMEN = (0.56, 0.32, 0.78)
FARBEN = {
    "stahl": _STAHL,
    "alu": _ALU,
    "druck": _DRUCK,
    "druck_hell": _DRUCK,
    "zukauf": _ZUKAUF,
    "wagen": _ZUKAUF,
    "dummy": _ZUKAUF,
    "riemen": _RIEMEN,
    "wanne": (0.20, 0.20, 0.22),
}


_BERUEHRT = {}


def offenes(pfad):
    pfad = os.path.abspath(pfad)
    for d in App.listDocuments().values():
        if d.FileName and os.path.abspath(d.FileName) == pfad:
            return d
    return None


def dokument(pfad):
    """Gibt (doc, war_offen) zurück. Ein offenes Dokument wird weiterverwendet."""
    d = offenes(pfad)
    if d is None and os.path.exists(pfad):
        d = App.openDocument(os.path.abspath(pfad))
    if d is not None:
        _BERUEHRT[d.Name] = set()
        return d, True
    name = os.path.splitext(os.path.basename(pfad))[0]
    d = App.newDocument(name)
    d.saveAs(os.path.abspath(pfad))     # nötig für Verknüpfungen in andere Dateien
    _BERUEHRT[d.Name] = set()
    return d, False


def quelle(pfad):
    """Dokument eines Einzelteils für Verknüpfungen (öffnet es bei Bedarf)."""
    return offenes(pfad) or App.openDocument(os.path.abspath(pfad))


def objekt(doc, typ, name):
    o = doc.getObject(name)
    if o is None or o.TypeId != typ:
        if o is not None:
            doc.removeObject(name)
        o = doc.addObject(typ, name)
    _BERUEHRT.setdefault(doc.Name, set()).add(o.Name)
    return o


def teil(doc, name, shape, farbe=None, transparenz=0):
    o = objekt(doc, "Part::Feature", name)
    o.Shape = shape
    o.Visibility = True
    if App.GuiUp and farbe:
        rgb = FARBEN.get(farbe, farbe)
        o.ViewObject.ShapeColor = rgb
        o.ViewObject.Transparency = transparenz
    return o


def speichern(doc, pfad, war_offen):
    # Objekte, die das Skript nicht mehr erzeugt, entfernen
    for o in list(doc.Objects):
        if o.Name not in _BERUEHRT.get(doc.Name, set()):
            doc.removeObject(o.Name)
    doc.recompute()
    # Immer mit saveAs schreiben und prüfen, dass die Datei wirklich neu ist:
    # doc.save() hat im laufenden FreeCAD teils stillschweigend nichts geschrieben,
    # dann fehlen nach einem Neustart Teile ("link not restored").
    import time
    vorher = os.path.getmtime(pfad) if os.path.exists(pfad) else 0.0
    start = time.time()
    doc.saveAs(os.path.abspath(pfad))
    if os.path.getmtime(pfad) < start - 1 and os.path.getmtime(pfad) <= vorher:
        # Rückfall: Kopie schreiben und an die Stelle der Datei setzen
        tmp = os.path.abspath(pfad) + ".neu.FCStd"
        doc.saveCopy(tmp)
        os.replace(tmp, os.path.abspath(pfad))
    if os.path.getmtime(pfad) < start - 1:
        raise RuntimeError("Datei wurde nicht gespeichert: %s" % pfad)
    if App.GuiUp and not war_offen:
        import FreeCADGui
        FreeCADGui.getDocument(doc.Name).activeView().viewIsometric()
        FreeCADGui.SendMsgToActiveView("ViewFit")


def duenne_waende(shape, grenze=3.0, r_min=1.9):
    """Sucht dünne Wände an Bohrungen: Abstand jeder Bohrung (Zylinderfläche,
    Radius >= r_min), gemessen auf halber Bohrungslänge, zu allen anderen
    Flächen. Nicht als Wand zählen: angrenzende Flächen, Flächen quer zur
    Bohrung (Senkungsböden) und koaxiale Zylinder (Senkungen).
    Gibt [(abstand, x, y, z, flächentyp)] zurück, je Bohrung der kleinste Wert."""
    flaechen = shape.Faces
    kanten = [set(e.hashCode() for e in f.Edges) for f in flaechen]
    funde = {}
    for i, f in enumerate(flaechen):
        su = f.Surface
        if "Cylinder" not in su.TypeId or su.Radius < r_min:
            continue
        achse, mitte = su.Axis, su.Center
        ts = [(v.Point - mitte).dot(achse) for v in f.Vertexes]
        if not ts:
            continue
        tm = (min(ts) + max(ts)) / 2
        try:
            ring = Part.Compound(f.slice(achse, mitte.dot(achse) + tm))
        except Exception:
            continue
        if not ring.Edges:
            continue
        bb = f.BoundBox
        bb.enlarge(grenze)
        for j, g in enumerate(flaechen):
            if i == j or kanten[i] & kanten[j] or not bb.intersect(g.BoundBox):
                continue
            gs = g.Surface
            if "Plane" in gs.TypeId and abs(abs(gs.Axis.dot(achse)) - 1) < 1e-6:
                continue
            if "Cylinder" in gs.TypeId and abs(abs(gs.Axis.dot(achse)) - 1) < 1e-6:
                w = gs.Center - mitte
                if (w - achse * w.dot(achse)).Length < 1e-3:
                    continue
            tg = [(v.Point - mitte).dot(achse) for v in g.Vertexes]
            if tg and not min(tg) - 0.01 <= tm <= max(tg) + 0.01:
                continue                    # liegt nicht neben der Bohrung (z. B. Muttertasche)
            d, punkte, _ = ring.distToShape(g)
            if not 1e-4 < d < grenze:
                continue
            q = mitte + achse * tm
            schluessel = (round(q.x, 1), round(q.y, 1), round(q.z, 1))
            p = punkte[0][0]
            if schluessel not in funde or d < funde[schluessel][0]:
                funde[schluessel] = (d, p.x, p.y, p.z, gs.TypeId.split("::")[-1])
    return sorted(funde.values())


def schreibe_waende(f, name, shape, grenze=3.0):
    """Schreibt das Ergebnis von duenne_waende in die Prüfdatei."""
    funde = duenne_waende(shape, grenze)
    if not funde:
        f.write("Wand an Bohrungen %s: ok (>= %.1f mm)\n" % (name, grenze))
    for d, x, y, z, typ in funde:
        f.write("DÜNN %s: %.2f mm bei (%.1f, %.1f, %.1f) zu %s\n" % (name, d, x, y, z, typ))
    return len(funde)


def fest(shape):
    """Platzierung in die Geometrie übernehmen. Nötig für Teile, auf die der
    Zusammenbau verlinkt: App::Link übernimmt die Platzierung des Objekts nicht."""
    m = shape.Placement.toMatrix()
    s = shape.copy()
    s.Placement = App.Placement()
    return s.transformGeometry(m)


# Muttern (Schlüsselweite + Druckspiel, Höhe + Spiel) für Taschen in Druckteilen
MUTTER = {3: (5.7, 2.7), 4: (7.2, 3.5), 5: (8.2, 4.3), 6: (10.2, 5.3)}


def mutter(m, p, achse, schlitz=None, laenge=0.0):
    """Tasche für eine eingepresste Mutter M<m>: Mitte p auf der Schraubenachse,
    achse = Schraubenrichtung. Mit schlitz (Richtung quer zur Achse) und laenge
    entsteht ein Schlitz, durch den die Mutter seitlich eingeschoben wird; die
    Schlüsselflächen liegen dann parallel zum Schlitz (Mutter dreht nicht mit)."""
    import math
    sw, h = MUTTER[m]
    V = App.Vector
    z = V(achse).normalize()
    if schlitz is None:
        x = z.cross(V(0, 0, 1)) if abs(z.z) < 0.9 else z.cross(V(1, 0, 0))
    else:
        x = V(schlitz)
    x = (x - z * x.dot(z)).normalize()
    y = z.cross(x)
    r = sw / math.sqrt(3)
    pts = [V(r * math.cos(math.radians(60 * i)), r * math.sin(math.radians(60 * i)), -h / 2)
           for i in range(7)]
    s = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))
    if schlitz is not None and laenge > 0:
        s = s.fuse(Part.makeBox(laenge, sw, h, V(0, -sw / 2, -h / 2)))
    mat = App.Matrix(x.x, y.x, z.x, p.x, x.y, y.y, z.y, p.y, x.z, y.z, z.z, p.z, 0, 0, 0, 1)
    return s.transformGeometry(mat)
