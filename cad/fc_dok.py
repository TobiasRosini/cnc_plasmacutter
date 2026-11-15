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
    """Offenes Dokument zu pfad. Hat FreeCAD es nur teilweise geladen (beim Öffnen eines
    Zusammenbaus nur die verlinkten Objekte), wird es vollständig nachgeladen; sonst
    fehlen neue Teile im Zusammenbau."""
    pfad = os.path.abspath(pfad)
    for d in App.listDocuments().values():
        if d.FileName and os.path.abspath(d.FileName) == pfad:
            if getattr(d, "Partial", False):
                d = App.openDocument(pfad)
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
        if o.TypeId in ("App::Origin", "App::Line", "App::Plane", "App::Point"):
            continue                    # Ursprung eines App::Part (wird mit ihm angelegt)
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


def _kontaktflaechen(shape, nachbarn, tol=0.05):
    """Indizes der Flächen, die an einem Nachbarteil anliegen (Stichproben im Flächeninneren)."""
    res = set()
    for i, f in enumerate(shape.Faces):
        bb = f.BoundBox
        bb.enlarge(0.5)
        nb = [n for n in nachbarn if n.BoundBox.intersect(bb)]
        if not nb:
            continue
        u0, u1, v0, v1 = f.ParameterRange
        pts = []
        for a, b in ((0.5, 0.5), (0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)):
            u, v = u0 + a * (u1 - u0), v0 + b * (v1 - v0)
            p = f.valueAt(u, v)
            if f.isInside(p, 1e-4, True):
                pts.append(p)
        if not pts:
            pts = [f.CenterOfMass]
        for p in pts:
            vx = Part.Vertex(p)
            if any(vx.distToShape(n)[0] < tol for n in nb):
                res.add(i)
                break
    return res


def _konvex(e, f1, f2):
    """True, wenn die Kante zwischen f1 und f2 eine Außenkante ist."""
    p = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
    t = e.tangentAt((e.FirstParameter + e.LastParameter) / 2)
    n1 = f1.normalAt(*f1.Surface.parameter(p))
    n2 = f2.normalAt(*f2.Surface.parameter(p))
    w = n1.cross(t)
    if w.Length < 1e-9:
        return False
    w.normalize()
    if f1.distToShape(Part.Vertex(p + w * 0.05))[0] > 1e-3:
        w = -w
    return n2.dot(w) < -1e-3


def _innen(shape, f, weite=8.0):
    """True, wenn vor der Fläche f innerhalb von weite mm wieder Material liegt (Wand eines
    Schlitzes, Tunnels, einer Tasche). Geprüft an Punkten, die wirklich auf der Fläche liegen
    (bei Ringflächen liegt der Schwerpunkt im Loch); innen nur, wenn alle Material sehen."""
    u0, u1, v0, v1 = f.ParameterRange
    pts = [f.CenterOfMass] + [f.valueAt(u0 + a * (u1 - u0), v0 + b * (v1 - v0))
                              for a in (0.1, 0.3, 0.5, 0.7, 0.9) for b in (0.1, 0.3, 0.5, 0.7, 0.9)]
    pts = [p for p in pts if f.isInside(p, 1e-4, True)][:3]
    if not pts:
        return False
    for p in pts:
        n = f.normalAt(*f.Surface.parameter(p))
        strahl = Part.LineSegment(p + n * 0.05, p + n * weite).toShape()
        try:
            if strahl.common(shape).Length <= 1e-3:
                return False
        except Exception:
            return False
    return True


def _duenn(shape, grenze=3.0):
    return {(round(x), round(y), round(z)) for d, x, y, z, _ in duenne_waende(shape, grenze)}


def _bohrung(f):
    """True für die Wand einer Bohrung (Zylinder mit Material außen), False für eine
    gerundete Außenecke (konvexer Zylinder)."""
    su = f.Surface
    p = f.CenterOfMass
    if not f.isInside(p, 1e-4, True):
        u0, u1, v0, v1 = f.ParameterRange
        p = f.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    r = p - su.Center
    r = r - su.Axis * r.dot(su.Axis)
    return f.normalAt(*su.parameter(p)).dot(r) < 0


def _sperre(s, nachbarn, bett, loch_r, schlitz):
    """Flächen, deren Kanten scharf bleiben: Kontakt zu Nachbarteilen, Druckbett-Seite,
    Bohrungen, Muttertaschen (kleine Freiformflächen), Wände von Schlitzen."""
    kontakt = _kontaktflaechen(s, nachbarn)
    zmax = max(v.Point.dot(bett) for v in s.Vertexes)
    def gesperrt(i, f):
        if i in kontakt:
            return True
        st = f.Surface.TypeId
        if "Plane" in st:
            n = f.normalAt(*f.Surface.parameter(f.CenterOfMass))
            if n.dot(bett) > 0.999 and abs(f.CenterOfMass.dot(bett) - zmax) < 0.05:
                return True
        elif "Cylinder" in st:
            if f.Surface.Radius < loch_r and _bohrung(f):
                return True
        elif f.Area < 200.0:
            return True
        return _innen(s, f, schlitz)
    return {i for i, f in enumerate(s.Faces) if gesperrt(i, f)}


def _zuege(s, sperre, bett, senkrecht):
    """Freie konvexe Außenkanten einer Richtungsklasse, zu Zügen verbunden (Kanten mit
    gemeinsamem Eckpunkt). senkrecht: beide Flächen parallel zur Druckrichtung."""
    kanten = []
    for e in s.Edges:
        if e.Length < 1.0 or not any(k in e.Curve.TypeId for k in ("Line", "Circle", "BSpline", "Ellipse")):
            continue
        fl = [i for i, f in enumerate(s.Faces) if any(e.isSame(x) for x in f.Edges)]
        if len(fl) != 2 or sperre & set(fl):
            continue
        f1, f2 = s.Faces[fl[0]], s.Faces[fl[1]]
        if not _konvex(e, f1, f2):
            continue
        p = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        quer = max(abs(f.normalAt(*f.Surface.parameter(p)).dot(bett)) for f in (f1, f2))
        if (quer < 0.02) != senkrecht:
            continue
        kanten.append(e)
    def schluessel(v):
        return tuple(round(c, 3) for c in v.Point)
    eltern = list(range(len(kanten)))
    def wurzel(i):
        while eltern[i] != i:
            eltern[i] = eltern[eltern[i]]
            i = eltern[i]
        return i
    an = {}
    for i, e in enumerate(kanten):
        for v in e.Vertexes:
            k = schluessel(v)
            if k in an:
                eltern[wurzel(i)] = wurzel(an[k])
            else:
                an[k] = i
    zuege = {}
    for i, e in enumerate(kanten):
        zuege.setdefault(wurzel(i), []).append(
            (e.valueAt((e.FirstParameter + e.LastParameter) / 2), e.Length))
    return list(zuege.values())


def _sicher(op):
    """op() (gibt eine Form zurück) in einem Kindprozess: Fasen und Rundungen bringen
    OpenCascade manchmal zum Absturz, der sich in Python nicht abfangen lässt; dann endet nur
    das Kind. Ergebnis über eine BREP-Datei. None bei Fehler oder Absturz."""
    import tempfile
    fd, pfad = tempfile.mkstemp(suffix=".brep")
    os.close(fd)
    try:
        pid = os.fork()
        if pid == 0:
            code = 1
            try:
                op().exportBrep(pfad)
                code = 0
            except BaseException:
                pass
            os._exit(code)
        _, st = os.waitpid(pid, 0)
        if not (os.WIFEXITED(st) and os.WEXITSTATUS(st) == 0):
            return None
        s = Part.Shape()
        s.importBrep(pfad)
        return s
    finally:
        os.remove(pfad)


def verrunden(shape, nachbarn, bett, radius=2.0, fase=1.0, loch_r=8.0, schlitz=8.0):
    """Gibt einem Druckteil Radien und Fasen ("make it sexy"), je nach Lage der Kante beim
    Druck (bett = Normale der Unterseite beim Druck):
      - senkrechte Kanten (in Druckrichtung): Radius, wie Eckradien eines Frästeils,
      - waagerechte Kanten (Oberseite, Überhänge): Fase, druckt stützenfrei.
    Gerundet bzw. gefast wird je Kantenzug mit einem Maß; geht es nicht, der ganze Zug mit
    dem halben Maß, sonst in tangential durchlaufenden Teilzügen, zuletzt Kante für Kante. Scharf bleiben Kanten an Flächen, die an einem
    Nachbarteil anliegen (saubere Fugen im Zusammenbau), an der Druckbett-Seite,
    Innenkanten und Ränder von Bohrungen, Muttertaschen und Schlitzen (lichte Weite bis
    schlitz). Keine Rundung darf eine Wand an einer Bohrung unter 3 mm bringen.
    Gibt (form, {"radius": (bearbeitet, kandidaten, offen), "fase": (...)}) zurück, offen =
    [(Mitte, Länge)] der Kanten, die scharf bleiben mussten."""
    bett = App.Vector(bett).normalize()
    nachbarn = list(nachbarn)
    s = shape
    v0 = s.Volume
    duenn0 = _duenn(s)

    def finde(form, m, l):
        """Kante wiederfinden; eine Nachbarbearbeitung kann sie gekürzt haben."""
        nah = [e for e in form.Edges if e.distToShape(Part.Vertex(m))[0] < 1e-3]
        for e in nah:
            if abs(e.Length - l) < 1e-3:
                return e
        return nah[0] if len(nah) == 1 else None

    def teilzuege(form, z):
        """Zug in tangential durchlaufende Teilzüge zerlegen."""
        es = [finde(form, m, l) for m, l in z]
        def tangente(e, v):
            t = e.tangentAt(e.parameterAt(v))
            return t.normalize() if t.Length > 1e-9 else t
        eltern = list(range(len(z)))
        def wurzel(i):
            while eltern[i] != i:
                i = eltern[i]
            return i
        for i in range(len(z)):
            for j in range(i + 1, len(z)):
                if es[i] is None or es[j] is None:
                    continue
                for v in es[i].Vertexes:
                    w = [x for x in es[j].Vertexes if x.Point.distanceToPoint(v.Point) < 1e-3]
                    if w and tangente(es[i], v).cross(tangente(es[j], w[0])).Length < 0.02:
                        eltern[wurzel(j)] = wurzel(i)
        res = {}
        for i in range(len(z)):
            res.setdefault(wurzel(i), []).append(z[i])
        return list(res.values())

    def gut(neu, alt):
        return (neu.isValid() and len(neu.Solids) == len(alt.Solids)
                and 0 < alt.Volume - neu.Volume < 0.05 * v0 and _duenn(neu) <= duenn0)

    def versuch(form, op, mass, kanten):
        es = [finde(form, m, l) for m, l in kanten]
        if not es or None in es:
            return None
        neu = _sicher(lambda: form.makeFillet(mass, es) if op == "radius" else form.makeChamfer(mass, es))
        return neu if neu is not None and gut(neu, form) else None

    bericht = {}
    for op, mass, senkrecht in (("radius", radius, True), ("fase", fase, False)):
        zuege = _zuege(s, _sperre(s, nachbarn, bett, loch_r, schlitz), bett, senkrecht)
        alle = [k for z in zuege for k in z]
        offen = []
        # erst alle auf einmal (nur bei wenigen Kanten: sehr viele auf einmal haben
        # OpenCascade abstürzen lassen, nicht abfangbar)
        neu = versuch(s, op, mass, alle) if 0 < len(alle) <= 20 else None
        if neu is not None:
            s, n = neu, len(alle)
        else:
            n = 0
            def zug(z, stufe):
                nonlocal s, n
                for m in (mass, mass / 2):
                    neu = versuch(s, op, m, z)
                    if neu is not None:
                        s, n = neu, n + len(z)
                        return
                if stufe == 0 and len(z) > 1:                   # tangentiale Teilzüge
                    for t in teilzuege(s, z):
                        zug(t, 1)
                elif len(z) > 1:                                # Kante für Kante
                    for k in z:
                        zug([k], 2)
                else:
                    offen.append(z[0])
            for z in zuege:
                zug(z, 0)
        bericht[op] = (n, len(alle), offen)
    return s, bericht


CAD = os.path.dirname(os.path.abspath(__file__))
ZUSAMMENBAU = os.path.join(CAD, "zusammenbau", "zusammenbau.FCStd")


def drucklage(name):
    """Normale der Druckbett-Seite eines Druckteils aus cad/druckbarkeit.txt (Lage, in der
    pruefe_druck.py das Teil druckt; "+Z oben" -> Bett bei -Z)."""
    with open(os.path.join(CAD, "druckbarkeit.txt"), encoding="utf-8") as f:
        for z in f:
            t = z.split()
            if len(t) > 3 and t[1] == name and t[2] == "Lage":
                a = {"X": App.Vector(1, 0, 0), "Y": App.Vector(0, 1, 0), "Z": App.Vector(0, 0, 1)}[t[3][1]]
                return a * (-1 if t[3][0] == "+" else 1)
    raise KeyError("Drucklage von %s fehlt in druckbarkeit.txt (pruefe_druck.py laufen lassen)" % name)


def nachbarn_im_zusammenbau(dok_pfad, name, form, rand=1.0):
    """Nachbarn eines Teils (Objekt name im Dokument dok_pfad) aus dem Zusammenbau, in den
    Koordinaten des Teils, für jede Lage, in der es eingebaut ist. Nur Teile, deren
    Hüllquader den von form (um rand vergrößert) schneidet. Gibt (nachbarn, lagen) zurück."""
    zb = quelle(ZUSAMMENBAU)
    ziel = os.path.abspath(dok_pfad)
    alle, eigen = [], []
    for o in zb.Objects:
        if o.TypeId == "App::Link":
            lo = o.LinkedObject
            if lo is None or lo is o or not hasattr(lo, "Shape") or lo.Shape.isNull():
                continue
            s = lo.Shape.copy()
            s.Placement = o.LinkPlacement               # Link ersetzt die Objekt-Platzierung
            if os.path.abspath(lo.Document.FileName) == ziel and lo.Name == name:
                eigen.append(o)
                continue
        elif o.TypeId == "Part::Feature" and not o.Shape.isNull():
            s = o.Shape.copy()
        else:
            continue
        alle.append(s)
    bb = form.BoundBox
    bb.enlarge(rand)
    res = []
    for inst in eigen:
        inv = inst.LinkPlacement.inverse()
        for s in alle:
            t = s.copy()
            t.Placement = inv.multiply(t.Placement)
            if t.BoundBox.intersect(bb):
                res.append(t)
    return res, len(eigen)


def radien_zeile(name, bericht, sekunden):
    return ("Radien %s: R2 an %d von %d senkrechten Kanten, Fase an %d von %d waagerechten (%.0f s)"
            % (name, bericht["radius"][0], bericht["radius"][1], bericht["fase"][0],
               bericht["fase"][1], sekunden))


def sexy(teile, dok_pfad, log):
    """Radien und Fasen (verrunden) für die Druckteile einer Baugruppe: teile = Name ->
    Form in Teilekoordinaten (wie im Dokument dok_pfad, ohne Objekt-Platzierung). Drucklage
    aus druckbarkeit.txt, Nachbarn aus dem Zusammenbau. Gibt Name -> Form zurück."""
    import time
    res = {}
    for n, s in teile.items():
        t0 = time.time()
        try:
            bett = drucklage(n)
        except KeyError:                                # neues Teil: erst STL, dann pruefe_druck.py
            res[n] = s
            log.append("Radien %s: keine Drucklage in druckbarkeit.txt (pruefe_druck.py, dann neu)" % n)
            continue
        nb, lagen = nachbarn_im_zusammenbau(dok_pfad, n, s)
        r, b = verrunden(s, nb, bett)
        res[n] = r
        log.append(radien_zeile(n, b, time.time() - t0)
                   + ("" if lagen else " – nicht im Zusammenbau, ohne Nachbarn"))
    return res
