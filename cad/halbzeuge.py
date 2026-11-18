#!/usr/bin/env python3
"""
Zuschnitt- und Einkaufsliste der Halbzeuge über alle Baugruppen. Liest die Teile aus
cad/stueckliste.md (vorher cad/teilenummern.py laufen lassen), den Wannenkäfig aus
cad/wannenkaefig/zuschnitt.txt und die Abwicklung der Haube aus cad/unterbau/pruefung.txt.
Ein Stahl- oder Aluteil ohne Zuordnung in TEILE bricht den Lauf ab, damit nichts fehlt.

Aufruf (ohne FreeCAD):
  python3 cad/halbzeuge.py            -> cad/halbzeuge.md
"""
import math
import os
import re

CAD = os.path.dirname(os.path.abspath(__file__))
KERF = 3.0                  # Sägeschnitt, mm
RHO = {"Stahl": 7.85e-6, "Alu": 2.7e-6, "PVC": None, "Holz": 0.68e-6}   # kg/mm³


def rohr(a, b, t):
    return a * b - (a - 2 * t) * (b - 2 * t)


# Stangenware: Name -> (Werkstoff, Querschnitt mm², Lagerlänge mm)
STANGEN = {
    "Stahl-Rechteckrohr 40 × 40 × 3": ("Stahl", rohr(40, 40, 3), 3000.0),
    "Stahl-Rechteckrohr 40 × 40 × 2": ("Stahl", rohr(40, 40, 2), 3000.0),
    "Stahl-Rechteckrohr 80 × 40 × 4": ("Stahl", rohr(80, 40, 4), 1000.0),
    "Stahl-Rechteckrohr 40 × 20 × 2": ("Stahl", rohr(40, 20, 2), 3000.0),
    "Stahl-Vierkantrohr 20 × 20 × 2": ("Stahl", rohr(20, 20, 2), 3000.0),
    "Flachstahl 50 × 3": ("Stahl", 150.0, 3000.0),
    "Gewindestange M16": ("Stahl", 157.0, 1000.0),
    "Alu-Rechteckrohr 80 × 40 × 4": ("Alu", rohr(80, 40, 4), 1000.0),
    "Alu-Rechteckrohr 40 × 20 × 2": ("Alu", rohr(40, 20, 2), 1000.0),
    "Alu-Flachstange 40 × 15": ("Alu", 600.0, 500.0),
    "Alu-Flachstange 40 × 8": ("Alu", 320.0, 2000.0),
    "Alu-Vierkant 20 × 20": ("Alu", 400.0, 500.0),
    "Alu-U-Profil 20 × 60 × 20 × 2": ("Alu", 2 * 20 * 2 + 56 * 2, 2000.0),
    "PVC-Kabelkanal 40 × 40": ("PVC", 0.0, 2000.0),
    "PVC-Kabelkanal 25 × 60": ("PVC", 0.0, 2000.0),
}
# Tafeln: Name -> (Werkstoff, Dicke mm, Format l × b mm, None = Zuschnitt auf Maß)
TAFELN = {
    "Stahlblech 3": ("Stahl", 3.0, (1250.0, 625.0)),
    "Stahlblech 1": ("Stahl", 1.0, (100.0, 100.0)),
    "Stahlplatte 10": ("Stahl", 10.0, (400.0, 400.0)),
    "Alu-Platte 12": ("Alu", 12.0, (500.0, 150.0)),
    "Alu-Blech 0,5": ("Alu", 0.5, (2000.0, 1250.0)),
    "Siebdruckplatte 9": ("Holz", 9.0, None),
}
# Teil (regulärer Ausdruck) -> (Halbzeug, Länge fest oder None, Zuschnitt l × b oder None, Bemerkung)
TEILE = [
    (r"OR_Laengstraeger.*|OR_Quertraeger_V", "Stahl-Rechteckrohr 40 × 40 × 3", None, None, ""),
    (r"OR_Quertraeger_H", "Stahl-Rechteckrohr 80 × 40 × 4", None, None, ""),
    (r"UT_(Bein|Laengsrohr|Querrohr).*", "Stahl-Rechteckrohr 40 × 40 × 2", None, None, ""),
    (r"ek_stuetzen_220", "Stahl-Rechteckrohr 40 × 40 × 2", None, None, "vordere Kettenstütze"),
    (r"ek_traeger_40x20|ek_stuetzen_188", "Stahl-Rechteckrohr 40 × 20 × 2", None, None, ""),
    (r"OR_Spritzschutz|x_schutzstreifen|auflageleiste", "Flachstahl 50 × 3", None, None, ""),
    (r"UT_Stellfuss_M16", "Gewindestange M16", 200.0, None, "unten Mutter M16 aufschweißen"),
    (r"kammtraeger|schutzleiste", "Stahlblech 3", None, None, "lasern oder von Hand schneiden"),
    (r"y_ref_fahne(_rechts)?", "Stahlblech 3", None, (61.0, 32.0), "abgekantet, Zuschnitt ungefähr"),
    (r"z_ref_fahne", "Stahlblech 3", None, None, ""),
    (r"x_spritzschutz", "Stahlblech 1", None, None, ""),
    (r"UT_Eckplatte", "Stahlplatte 10", None, None, ""),
    (r"Portalbruecke_80x40x4", "Alu-Rechteckrohr 80 × 40 × 4", None, None, ""),
    (r"x_schutz_halter", "Alu-Rechteckrohr 80 × 40 × 4", None, None, "aus der Wand des Reststücks"),
    (r"ekx_traeger_40x20", "Alu-Rechteckrohr 40 × 20 × 2", None, None, ""),
    (r"flachstange_40x15", "Alu-Flachstange 40 × 15", None, None, ""),
    (r"ek_ausleger|ekx_stuetze_links|ekx_rinne_hinten|ekx_mast", "Alu-Flachstange 40 × 8", None, None, ""),
    (r"z_leisten_20x20", "Alu-Vierkant 20 × 20", None, None, ""),
    (r"ek_rinne|ekx_rinne", "Alu-U-Profil 20 × 60 × 20 × 2", None, None, ""),
    (r"z_grundplatte|z_schlitten", "Alu-Platte 12", None, None, ""),
    (r"ek_kabelkanal", "PVC-Kabelkanal 40 × 40", None, None, "mit Deckel"),
    (r"ub_kabelkanal_(senkrecht|quer)", "PVC-Kabelkanal 25 × 60", None, None, "mit Deckel"),
    (r"ub_geraeteboden", "Siebdruckplatte 9", None, None, ""),
]
# Stahl/Alu in der Stückliste, die kein Halbzeug brauchen
OHNE = (r"Wanne", r"UT_Schweissmutter_M16", r"x_ref_stift")
# werden aus eigenen Dateien gelesen
EIGENE = (r"wannenkaefig", r"ub_haube")


def stueckliste():
    res = []
    with open(os.path.join(CAD, "stueckliste.md"), encoding="utf-8") as f:
        for z in f:
            t = [x.strip() for x in z.strip().strip("|").split("|")]
            if len(t) >= 5 and t[0].isdigit():
                res.append((t[1], int(t[2]), t[3], [float(x) for x in t[4].split("×")]))
    return res


def sammeln():
    stangen, tafeln = {}, {}
    for name, n, art, m in stueckliste():
        if any(re.fullmatch(o, name) for o in OHNE + EIGENE):
            continue
        treffer = [e for e in TEILE if re.fullmatch(e[0], name)]
        if not treffer:
            if art.startswith(("Stahl", "Alu")):
                raise SystemExit("Keine Zuordnung in TEILE: %s (%s)" % (name, art))
            continue
        _, hz, laenge, format_, bem = treffer[0]
        if hz in STANGEN:
            stangen.setdefault(hz, []).append((name, laenge or m[0], n, bem))
        else:
            tafeln.setdefault(hz, []).append((name, format_ or (m[0], m[1]), n, bem))
    with open(os.path.join(CAD, "wannenkaefig", "zuschnitt.txt"), encoding="utf-8") as f:
        for z in f:
            t = re.match(r"(\S.*?)\s{2,}([\d.]+)\s+(\d+)$", z.rstrip())
            if t:
                stangen.setdefault("Stahl-Vierkantrohr 20 × 20 × 2", []).append(
                    ("Wannenkäfig: " + t.group(1), float(t.group(2)), int(t.group(3)), ""))
    with open(os.path.join(CAD, "unterbau", "pruefung.txt"), encoding="utf-8") as f:
        t = re.search(r"Abwicklung ca\. (\d+) x (\d+)", f.read())
    tafeln.setdefault("Alu-Blech 0,5", []).append(
        ("ub_haube", (float(t.group(1)), float(t.group(2))), 1, "Abwicklung, gekantet"))
    return stangen, tafeln


def stangenplan(teile, lager):
    """First-Fit absteigend: Liste der Stangen mit ihren Schnitten."""
    stuecke = sorted((l for _, l, n, _ in teile for _ in range(n)), reverse=True)
    plan = []
    for l in stuecke:
        if l > lager:
            raise SystemExit("Teil %.0f länger als die Lagerlänge %.0f" % (l, lager))
        for s in plan:
            if sum(s) + (len(s) + 1) * KERF + l <= lager:
                s.append(l)
                break
        else:
            plan.append([l])
    return plan


def tafel_passt(teile, fmt):
    """Streifenweise legen: gibt die belegte Breite zurück, None wenn es nicht passt."""
    stuecke = sorted((sorted(m, reverse=True) for _, m, n, _ in teile for _ in range(n)), key=lambda m: (-m[1], -m[0]))
    streifen = []
    for l, b in stuecke:
        if l > fmt[0]:
            return None
        for s in streifen:
            if s[0] + KERF + l <= fmt[0] and b <= s[1]:
                s[0] += KERF + l
                break
        else:
            streifen.append([l, b])
    breite = sum(s[1] for s in streifen) + KERF * (len(streifen) - 1)
    return breite if breite <= fmt[1] else None


def main():
    stangen, tafeln = sammeln()
    ein, ab = [], []
    gesamt = {"Stahl": 0.0, "Alu": 0.0}
    for hz, (wst, a, lager) in STANGEN.items():
        if hz not in stangen:
            raise SystemExit("Halbzeug ohne Teile: " + hz)
        teile = stangen[hz]
        plan = stangenplan(teile, lager)
        netto = sum(l * n for _, l, n, _ in teile)
        kg = netto * a * RHO[wst] if RHO[wst] else 0.0
        if wst in gesamt:
            gesamt[wst] += kg
        ein.append("| %s | %.2f m | %d × %.0f mm | %s |" % (hz, netto / 1000, len(plan), lager, "%.1f kg" % kg if kg else "–"))
        ab += ["", "### " + hz, "", "| Teil | Länge mm | Stk | Bemerkung |", "|---|---:|---:|---|"]
        for name, l, n, bem in sorted(teile, key=lambda e: -e[1]):
            ab.append("| %s | %.0f | %d | %s |" % (name, l, n, bem))
        ab += ["", "Schnittplan (Schnitt %.0f mm):" % KERF, ""]
        for i, s in enumerate(plan, 1):
            rest = lager - sum(s) - len(s) * KERF
            ab.append("- Stange %d: %s, Rest %.0f" % (i, " + ".join("%.0f" % l for l in s), max(rest, 0.0)))
    for hz, (wst, t, fmt) in TAFELN.items():
        teile = tafeln[hz]
        flaeche = sum(m[0] * m[1] * n for _, m, n, _ in teile)
        kg = flaeche * t * RHO[wst]
        if wst in gesamt:
            gesamt[wst] += kg
        if fmt:
            if tafel_passt(teile, fmt) is None:
                raise SystemExit("%s passt nicht auf %.0f × %.0f" % (hz, fmt[0], fmt[1]))
            kauf = "1 × %.0f × %.0f mm" % fmt
        else:
            kauf = "Zuschnitt auf Maß"
        ein.append("| %s | %.2f m² | %s | %.1f kg |" % (hz, flaeche / 1e6, kauf, kg))
        ab += ["", "### " + hz, "", "| Teil | Zuschnitt mm | Stk | Bemerkung |", "|---|---:|---:|---|"]
        for name, m, n, bem in sorted(teile, key=lambda e: -e[1][0]):
            ab.append("| %s | %.0f × %.0f | %d | %s |" % (name, m[0], m[1], n, bem))
    z = ["# Halbzeuge: Einkauf und Zuschnitt", "",
         "Erzeugt von `cad/halbzeuge.py` aus der Stückliste (dort ändern, nicht hier). Lagerlängen und Tafelformate sind "
         "Annahmen für den Transport im Auto und beim Händler zu prüfen; viele Händler sägen auch direkt nach dem Schnittplan. "
         "Rahmen: **Oberrahmen 40 × 40 × 3, Untertisch 40 × 40 × 2**.", "",
         "## Einkaufsliste", "", "| Halbzeug | Bedarf netto | Bestellen | Masse netto |", "|---|---:|---|---:|"] + ein
    z += ["", "Masse netto: Stahl %.0f kg, Alu %.0f kg." % (gesamt["Stahl"], gesamt["Alu"]), "", "## Zuschnitt"] + ab
    with open(os.path.join(CAD, "halbzeuge.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(z) + "\n")
    print("%d Stangenprofile, %d Tafeln, Stahl %.0f kg, Alu %.0f kg -> cad/halbzeuge.md"
          % (len(STANGEN), len(TAFELN), gesamt["Stahl"], gesamt["Alu"]))


if __name__ == "__main__":
    main()
