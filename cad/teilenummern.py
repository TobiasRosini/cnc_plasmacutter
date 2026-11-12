# -*- coding: utf-8 -*-
"""
Teilenummern für alle Teile des Zusammenbaus.

Jeder Körper (Solid) im Zusammenbau ist ein Teil. Gleiche Teile bekommen die
gleiche Nummer: gleich heißt deckungsgleich (Volumen, Oberfläche, Trägheits-
momente gleich und nach Drehen/Verschieben zur Deckung zu bringen). Spiegelteile
sind nicht gleich und bekommen eine eigene Nummer.

Die Nummern bleiben stabil: cad/teilenummern.json hält Name -> Nummer fest, neue
Teile bekommen die nächste freie Nummer, Nummern weggefallener Teile werden nicht
neu vergeben. Namen kommen aus den exportierten STEP-Dateien (gleiche Geometrie),
sonst aus dem Quellobjekt.

Ergebnis: cad/stueckliste.md, Nummern vorn in den Beschriftungen der Objekte im
Zusammenbau (Baumansicht).

Aufruf (nach dem Zusammenbau):
  python3 cad/live.py cad/teilenummern.py
"""
import glob
import json
import os
import re
import sys
import FreeCAD as App
import Part

V = App.Vector
CAD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CAD)
import fc_dok  # noqa: E402

ZUSAMMENBAU = os.path.join(CAD, "zusammenbau", "zusammenbau.FCStd")
NUMMERN = os.path.join(CAD, "teilenummern.json")
LISTE = os.path.join(CAD, "stueckliste.md")

# keine Teile: Leitungen sind Hüllrohre für die Kabel
AUSLASSEN = ("Leitung",)
# Kaufteile, die in den Teile-Dokumenten je nach Achse anders heißen
KAUFNAMEN = [(r"Referenzschalter.*|Schalter_Schwimmkopf", "Naeherungsschalter_LJ12A3"),
             (r"Motor.*", "Motor_NEMA23"),
             (r"Riemenscheibe.*", "Riemenscheibe_HTD5M"),
             (r"(Dummy_)?Schienen?_HGR15", "Schiene_HGR15"),
             (r"Wagen_HGH15CA|Wagen_X_.*", "Wagen_HGH15CA"),
             (r"Riemen_.*", "Riemen_HTD5M_15"),
             (r"Umlenkrollen?.*", "Umlenkrolle")]
ART = {"stahl": "Stahl", "alu": "Alu", "druck": "Druck", "zukauf": "Kaufteil",
       "riemen": "Kaufteil (Riemen)", "wanne": "Stahl (Wanne)"}
BAUGRUPPE = {"Untertisch": "Untertisch", "Oberrahmen": "Oberrahmen", "Portal": "Portal",
             "X_Achse": "X-Achse", "Z_Achse": "Z-Achse", "Y_Antrieb": "Y-Antrieb",
             "Energiekette_Y": "Energieketten", "Unterbau": "Unterbau"}


def kennung(s):
    """Lageunabhängige Kennwerte eines Körpers."""
    m = s.PrincipalProperties["Moments"]
    return (round(s.Volume, 1), round(s.Area, 1)) + tuple(round(x / s.Volume, 1) for x in sorted(m))


def gleich_kennung(a, b, tol=1e-4):
    return all(abs(x - y) <= tol * max(abs(x), abs(y), 1.0) for x, y in zip(a, b))


def rahmen(s):
    """Schwerpunkt, Hauptachsen und Hauptmomente, nach Moment aufsteigend."""
    pp = s.PrincipalProperties
    ax = [V(pp[k + "AxisOfInertia"]).normalize() for k in ("First", "Second", "Third")]
    paare = sorted(zip(pp["Moments"], range(3)))
    return s.CenterOfMass, [ax[i] for _, i in paare], [m for m, _ in paare]


def deckungsgleich(a, b):
    """True: durch Drehen/Verschieben deckungsgleich, False: nicht (z. B. gespiegelt).
    Bei gleichen Hauptmomenten (rotationssymmetrisch, quadratisch) lässt sich die Lage
    nicht eindeutig bestimmen; dann reichen die gleichen Kennwerte (None)."""
    ca, aa, ma = rahmen(a)
    cb, ab, _ = rahmen(b)
    aa = [aa[0], aa[1], aa[0].cross(aa[1])]             # rechtshändig
    if min(abs(ma[i] - ma[i + 1]) / ma[i + 1] for i in range(2)) < 1e-3:
        return None

    def matrix(ax, c):
        return App.Matrix(ax[0].x, ax[1].x, ax[2].x, c.x, ax[0].y, ax[1].y, ax[2].y, c.y,
                          ax[0].z, ax[1].z, ax[2].z, c.z, 0, 0, 0, 1)
    ma_inv = matrix(aa, ca).inverse()
    for s1 in (1, -1):
        for s2 in (1, -1):
            s3 = s1 * s2                                   # nur echte Drehungen
            ax = [ab[0] * s1, ab[1] * s2, ab[0].cross(ab[1]) * s3]
            t = matrix(ax, cb).multiply(ma_inv)
            if abs(t.determinant() - 1) > 1e-3:
                continue
            k = a.copy()
            k.transformShape(t)
            try:
                if k.common(b).Volume > 0.999 * a.Volume:
                    return True
            except Exception:
                pass
    return False


def aussenmasse(s):
    """Größte Außenmaße, absteigend: kleinere Hülle aus achsparalleler Lage und
    Lage entlang der Hauptachsen."""
    c, ax, _ = rahmen(s)
    ax = [ax[0], ax[1], ax[0].cross(ax[1])]
    m = App.Matrix(ax[0].x, ax[1].x, ax[2].x, c.x, ax[0].y, ax[1].y, ax[2].y, c.y,
                   ax[0].z, ax[1].z, ax[2].z, c.z, 0, 0, 0, 1)
    k = s.copy()
    k.transformShape(m.inverse())
    huellen = []
    for h in (s, k):
        try:
            bb = h.optimalBoundingBox()
        except Exception:
            bb = h.BoundBox
        huellen.append((bb.XLength * bb.YLength * bb.ZLength, (bb.XLength, bb.YLength, bb.ZLength)))
    return sorted(min(huellen)[1], reverse=True)


def art(o):
    if not App.GuiUp:
        return ""
    try:
        f = o.ViewObject.ShapeColor[:3]
    except Exception:
        return ""
    beste, d = "", 1e9
    for k, rgb in fc_dok.FARBEN.items():
        e = sum((x - y) ** 2 for x, y in zip(f, rgb))
        if e < d:
            beste, d = k, e
    return ART.get(beste, "Kaufteil") if d < 0.01 else ""


def step_namen():
    """Kennwerte der Körper aller exportierten STEP-Dateien -> (Kennung, Name, Pfad).
    Enthält eine Datei wenige verschiedene Körper, werden sie durchnummeriert; Dateien
    mit ganzen Baugruppen (Grundrahmen) bleiben außen vor."""
    res = []
    for p in sorted(glob.glob(os.path.join(CAD, "*", "*.step"))):
        try:
            sol = Part.read(p).Solids
        except Exception:
            continue
        n = os.path.splitext(os.path.basename(p))[0]
        kn = []
        for s in sol:
            k = kennung(s)
            if not any(gleich_kennung(k, x) for x in kn):
                kn.append(k)
        if len(kn) > 3:
            continue
        for i, k in enumerate(kn):
            res.append((k, n if len(kn) == 1 else "%s_%d" % (n, i + 1), os.path.relpath(p, CAD)))
    return res


def basisname(n):
    """Objektname ohne die Vorsilben des Zusammenbaus."""
    return re.sub(r"^(R|W|P|X|Z|Y|EK|U)_(links_|rechts_|h[lr]_|v[lr]_)?", "", n)


def kaufname(n):
    for muster, name in KAUFNAMEN:
        if re.fullmatch(muster, n):
            return name
    return n


def main():
    doc = fc_dok.quelle(ZUSAMMENBAU)
    maschine = doc.getObject("Maschine")
    steps = step_namen()

    # --- alle Körper einsammeln (Reihenfolge wie im Baum)
    koerper = []          # (objekt, quelle, baugruppe, index, solid)
    for g in maschine.Group:
        if g.TypeId != "App::DocumentObjectGroup":
            continue
        for o in g.Group:
            ziel = o.getLinkedObject(True) if o.TypeId == "App::Link" else o
            if ziel is None or any(a in ziel.Name for a in AUSLASSEN):
                continue
            sh = Part.getShape(o)
            for i, s in enumerate(sh.Solids):
                koerper.append((o, ziel, g.Name, i, s))

    # --- gleiche Teile zusammenfassen. Kaufteile: gleiche Bezeichnung und Außenmaße
    # (Muttern, Kabelabgang usw. sitzen je nach Einbau anders)
    teile = []
    for k in koerper:
        o, ziel, bg, i, s = k
        kn = kennung(s)
        ar = art(ziel)
        kauf = ar.startswith("Kaufteil")
        km = (kaufname(basisname(ziel.Name)), tuple(round(x) for x in aussenmasse(s))) if kauf else None
        gefunden = None
        for t in teile:
            if kauf or t["kauf"]:
                if km == t["kaufkennung"]:
                    gefunden = t
                    break
                continue
            if not gleich_kennung(kn, t["kennung"]):
                continue
            if deckungsgleich(s, t["solid"]) is False:
                t["spiegel"].add(id(k))
                continue
            gefunden = t
            break
        if gefunden is None:
            gefunden = dict(kennung=kn, solid=s, glieder=[], spiegel=set(), spiegel_zu=[], art=ar,
                            kauf=kauf, kaufkennung=km)
            teile.append(gefunden)
        gefunden["glieder"].append(k)
    for t in teile:                                         # Spiegelteile gegenseitig vermerken
        for u in teile:
            if u is not t and any(id(k) in t["spiegel"] for k in u["glieder"]):
                t["spiegel_zu"].append(u)
                u["spiegel_zu"].append(t)

    # --- Namen: aus der STEP-Datei (bei mehreren passenden die des Quellobjekts),
    # sonst aus dem Objekt
    for t in teile:
        o, ziel, bg, i, s = t["glieder"][0]
        quelle = basisname(ziel.Name)
        t["masse"] = aussenmasse(t["solid"])
        t["datei"] = ""
        treffer = [(n, p) for kn, n, p in steps if not t["kauf"] and gleich_kennung(kn, t["kennung"])]
        if treffer:
            t["name"], t["datei"] = next((x for x in treffer if x[0] == quelle), treffer[0])
            continue
        if t["kauf"]:
            t["name"] = t["kaufkennung"][0]
        elif len({k[1].Name for k in t["glieder"]}) > 1:   # gleiche Teile aus mehreren Objekten
            t["name"] = re.sub(r"_(\d+|[LRlrVH]|links|rechts)$", "", quelle)
        else:
            t["name"] = quelle
    # gleiche Namen für verschiedene Teile: Länge anhängen, sonst alle Maße, sonst zählen
    for wie in (lambda u: "%.0f" % u["masse"][0], lambda u: "x".join("%.0f" % x for x in u["masse"]), None):
        for t in teile:
            gleiche = [u for u in teile if u["name"] == t["name"]]
            if len(gleiche) < 2:
                continue
            for j, u in enumerate(gleiche):
                u["name"] = "%s_%s" % (u["name"], wie(u) if wie else j + 1)
            if wie and len({u["name"] for u in gleiche}) < len(gleiche):
                for u in gleiche:                           # nicht eindeutig: zurück
                    u["name"] = u["name"].rsplit("_", 1)[0]

    # --- Nummern: gespeicherte behalten, neue anhängen
    alt = {}
    if os.path.exists(NUMMERN):
        with open(NUMMERN, encoding="utf-8") as f:
            alt = json.load(f)
    naechste = max([int(v) for v in alt.values()] + [0]) + 1
    for t in teile:
        if t["name"] in alt:
            t["nr"] = int(alt[t["name"]])
        else:
            t["nr"] = naechste
            alt[t["name"]] = naechste
            naechste += 1
    with open(NUMMERN, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(alt.items(), key=lambda x: x[1])), f, ensure_ascii=False, indent=1)
        f.write("\n")

    # --- Beschriftungen im Zusammenbau
    nr_von = {}
    for t in teile:
        for o, ziel, bg, i, s in t["glieder"]:
            nr_von.setdefault(o.Name, set()).add(t["nr"])
    for g in maschine.Group:
        if g.TypeId != "App::DocumentObjectGroup":
            continue
        for o in g.Group:
            rein = re.sub(r"^[\d+]+ ", "", o.Label)
            nrn = sorted(nr_von.get(o.Name, ()))
            o.Label = ("+".join("%03d" % n for n in nrn) + " " + rein) if nrn else rein
    doc.save()

    # --- Stückliste
    teile.sort(key=lambda t: t["nr"])
    with open(LISTE, "w", encoding="utf-8") as f:
        f.write("# Stückliste\n\n")
        f.write("Erzeugt von `cad/teilenummern.py` aus dem Zusammenbau (nicht von Hand ändern). "
                "Gleiche Teile haben die gleiche Nummer, Spiegelteile eine eigene. "
                "Nummern stehen fest in `cad/teilenummern.json`; neue Teile bekommen die nächste "
                "freie Nummer. Im Zusammenbau steht die Nummer vorn in der Beschriftung. "
                "Leitungen (Hüllrohre) sind keine Teile. Schrauben, Muttern, Nietmuttern noch nicht "
                "enthalten.\n\n")
        f.write("| Nr. | Teil | Stk. | Art | Maße (mm) | Baugruppe | Datei | Bemerkung |\n")
        f.write("|---:|---|---:|---|---|---|---|---|\n")
        for t in teile:
            masse = " × ".join("%.0f" % x for x in t["masse"])
            bgs = []
            for k in t["glieder"]:
                b = BAUGRUPPE.get(k[2], k[2])
                if b not in bgs:
                    bgs.append(b)
            bem = ", ".join("Spiegelteil zu %03d" % u["nr"] for u in t["spiegel_zu"])
            f.write("| %03d | %s | %d | %s | %s | %s | %s | %s |\n" % (
                t["nr"], t["name"], len(t["glieder"]), t["art"], masse, ", ".join(bgs),
                t["datei"], bem))
        f.write("\n%d verschiedene Teile, %d Stück.\n" % (len(teile), sum(len(t["glieder"]) for t in teile)))


main()
