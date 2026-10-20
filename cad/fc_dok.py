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

FARBEN = {
    "stahl": (0.55, 0.57, 0.60),
    "alu": (0.80, 0.81, 0.84),
    "druck": (0.88, 0.48, 0.22),
    "druck_hell": (0.95, 0.65, 0.35),
    "wagen": (0.29, 0.44, 0.65),
    "riemen": (0.15, 0.15, 0.15),
    "wanne": (0.20, 0.20, 0.22),
    "dummy": (0.70, 0.72, 0.75),
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
    if war_offen:
        doc.save()
    else:
        doc.saveAs(os.path.abspath(pfad))
    if App.GuiUp and not war_offen:
        import FreeCADGui
        FreeCADGui.getDocument(doc.Name).activeView().viewIsometric()
        FreeCADGui.SendMsgToActiveView("ViewFit")
