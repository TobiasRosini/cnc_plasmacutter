#!/usr/bin/env python3
"""
Normteile (Schrauben, Muttern, Nietmuttern, Scheiben, Niete) je Verbindung und als
Gesamtliste. Anzahl und Klemmlängen sind aus den Bohrungen des Zusammenbaus ermittelt
und stehen hier von Hand: Kommt eine Verschraubung dazu, hier eintragen.

Aufruf (ohne FreeCAD):
  python3 cad/normteile.py            -> cad/normteile.md
"""
import math
import os
import re

CAD = os.path.dirname(os.path.abspath(__file__))

ZS = "ISO 4762 M%s"          # Zylinderschraube Innensechskant
SK = "DIN 933 M%s"           # Sechskantschraube, Vollgewinde
SE = "DIN 7991 M%s"          # Senkschraube Innensechskant
MU = "ISO 4032 M%d"          # Sechskantmutter
NM = "Nietmutter M%d"        # Stahl, Flachrundkopf
SB = "ISO 7089 M%d"          # Scheibe

# Baugruppe, Verbindung, [(Artikel, Stück)], Bemerkung
V = [
    ("Rahmen", "Oberrahmen auf Untertisch", [(ZS % "8 × 16", 6), (NM % 8, 6)], ""),
    ("Rahmen", "Wannenkäfig am Untertisch", [(ZS % "6 × 12", 6), (NM % 6, 6)], "Kopf durch das Zugangsloch Ø12"),
    ("Rahmen", "Y-Schienen HGR15", [(ZS % "4 × 16", 44)], "Gewinde in der 3-mm-Wand"),
    ("Rahmen", "Y-Motor- und Umlenkhalter", [(ZS % "6 × 12", 16), (NM % 6, 16)], ""),
    ("Rahmen", "Y-Motoren", [(ZS % "5 × 16", 8), (MU % 5, 8)], ""),
    ("Rahmen", "Y-Umlenkrollen (Achse)", [(SK % "8 × 30", 2), (MU % 8, 2), (SB % 8, 2)],
     "Spalt 2,5 zwischen Halter und Rolle mit Scheibe ausgleichen"),
    ("Rahmen", "Spritzschutz Y an den Längsträgern", [("Blindniet Ø4 × 8 Stahl", 12)], ""),
    ("Rahmen", "Geräteboden auf untere Längsrohre", [(ZS % "6 × 16", 6), (NM % 6, 6)], ""),
    ("Rahmen", "Lenkrollen an den Eckplatten", [(SK % "8 × 16", 16)], "Länge an der Rollenplatte prüfen"),
    ("Rahmen", "Stellfüße (Kontermutter)", [("DIN 439 M16", 4)], "Gewindestange und Schweißmutter: Stückliste 130, 131"),

    ("Portal", "Flachstange auf Y-Wagen", [(ZS % "4 × 12", 16)], ""),
    ("Portal", "Winkel auf Flachstange", [(ZS % "4 × 18", 8)], ""),
    ("Portal", "Feste Y-Riemenklemme", [(ZS % "5 × 60", 8)], "nicht länger: Gewinde nur 12 tief"),
    ("Portal", "Y-Spannschlitten, Klemmplatte", [(ZS % "3 × 12", 8), (MU % 3, 8)], ""),
    ("Portal", "Y-Spannschraube", [(SK % "5 × 45", 2), (MU % 5, 2)], ""),
    ("Portal", "X-Riemenklemme am Sattel", [(ZS % "3 × 16", 8), (MU % 3, 8)], "nicht länger: dahinter liegt die Brücke"),
    ("Portal", "Sattel an Brücke", [(ZS % "6 × 60", 8), (MU % 6, 8)], ""),
    ("Portal", "Kettenturm rechts an Einsteckteil", [(ZS % "6 × 20", 4), (MU % 6, 4)], ""),
    ("Portal", "Platte links an Einsteckteil", [(ZS % "6 × 25", 4), (MU % 6, 4)], ""),
    ("Portal", "X-Schienen HGR15", [(ZS % "4 × 16", 22)], "Gewinde in der 4-mm-Wand"),
    ("Portal", "Halter Spritzschutz X an Flachstange", [(ZS % "4 × 10", 4)], ""),
    ("Portal", "Schutzstreifen X an Halter", [(ZS % "4 × 12", 4), (MU % 4, 4)], ""),

    ("X-Wagen", "Wagenkörper auf X-Wagen, oben", [(ZS % "4 × 20", 4), (SB % 4, 4)], ""),
    ("X-Wagen", "Wagenkörper auf X-Wagen, unten", [(ZS % "4 × 10", 4), (SB % 4, 4)], ""),
    ("X-Wagen", "Spritzschutz", [(ZS % "3 × 6", 4), (MU % 3, 4)], ""),
    ("X-Wagen", "Motorbock an Wagenkörper", [(ZS % "4 × 20", 2), (ZS % "4 × 25", 2), (MU % 4, 4)], ""),
    ("X-Wagen", "Z-Grundplatte an Wagenkörper", [(ZS % "5 × 16", 6), (MU % 5, 6)], ""),
    ("X-Wagen", "X-Motor", [(ZS % "5 × 12", 4), (MU % 5, 4)], ""),
    ("X-Wagen", "X-Umlenkrollen (Achse)", [(SK % "8 × 30", 2), (MU % 8, 2), (SB % 8, 4), ("Rillenkugellager 608-2RS", 4)],
     "je 2 Scheiben unter der Rolle (Spalt 3)"),

    ("Z-Achse", "Z-Schienen durch die Leisten", [(ZS % "4 × 35", 8)], ""),
    ("Z-Achse", "Schlitten auf Z-Wagen", [(ZS % "4 × 12", 8)], ""),
    ("Z-Achse", "Mutterblock am Schlitten", [(ZS % "4 × 18", 4), (MU % 4, 4)], ""),
    ("Z-Achse", "Spindelmutter SFU1204 am Mutterblock", [(ZS % "4 × 18", 6), (MU % 4, 6)], ""),
    ("Z-Achse", "Z-Kopf auf Grundplatte und Leisten", [(ZS % "5 × 25", 4)], ""),
    ("Z-Achse", "Festlager FK10", [(ZS % "4 × 30", 4), (MU % 4, 4)], "Lochbild bei Lieferung prüfen"),
    ("Z-Achse", "Motorhalter durch die Säulen", [(ZS % "4 × 75", 4), (MU % 4, 4)],
     "**auf 73 mm kürzen**, sonst stößt die Spitze auf die Z-Schiene"),
    ("Z-Achse", "Z-Motor", [(ZS % "5 × 12", 4), (MU % 5, 4)], ""),
    ("Z-Achse", "Schwimmkopf-Halter unten am Schlitten", [(ZS % "5 × 10", 3)], ""),
    ("Z-Achse", "Schwimmkopf-Halter oben am Schlitten", [(ZS % "5 × 16", 2)], ""),
    ("Z-Achse", "Referenzfahne Z", [(ZS % "4 × 8", 2)], ""),
    ("Z-Achse", "Klemmdeckel am Brennerträger", [(ZS % "4 × 30", 4), (MU % 4, 4)], ""),

    ("Energieketten", "Kettenstützen am Rahmen", [(ZS % "6 × 12", 6), (NM % 6, 6)], ""),
    ("Energieketten", "Stützkopf im Rohr", [(ZS % "5 × 12", 2), (MU % 5, 2)], ""),
    ("Energieketten", "Y-Träger auf Stützkopf", [(ZS % "6 × 25", 2), (NM % 6, 2)], ""),
    ("Energieketten", "Kanalknoten auf vorderer Stütze", [(ZS % "5 × 10", 2), (NM % 5, 2)], ""),
    ("Energieketten", "Y-Träger im Kanalknoten", [(ZS % "5 × 10", 2), (NM % 5, 2)], ""),
    ("Energieketten", "Rinnen Y und X", [(SE % "3 × 6", 4)], "Gewinde in der Oberwand"),
    ("Energieketten", "Kabelkanal auf Y-Träger", [(ZS % "4 × 8", 3), (NM % 4, 3)], ""),
    ("Energieketten", "Festes Ende Y-Kette", [(ZS % "5 × 16", 2), (NM % 5, 2)], ""),
    ("Energieketten", "Festes Ende X-Kette, vorn", [(ZS % "5 × 16", 1), (NM % 5, 1)], ""),
    ("Energieketten", "Festes Ende X-Kette, hinten", [(ZS % "5 × 20", 1), (MU % 5, 1)], ""),
    ("Energieketten", "Bewegtes Ende Y-Kette, Halter Y, Leitungsbogen", [(ZS % "5 × 45", 2), (MU % 5, 2)], ""),
    ("Energieketten", "Bewegtes Ende X-Kette am Halter X", [(ZS % "5 × 20", 2), (MU % 5, 2)], ""),
    ("Energieketten", "Halter X am Z-Kopf", [(ZS % "5 × 20", 2), (MU % 5, 2)], ""),
    ("Energieketten", "Halter Y am Kettenturm", [(ZS % "5 × 20", 2), (MU % 5, 2)], ""),
    ("Energieketten", "Ablagehalter am Kettenturm", [(ZS % "5 × 20", 2), (MU % 5, 2)], ""),
    ("Energieketten", "X-Ablage auf dem Zapfen", [(ZS % "5 × 12", 2), (MU % 5, 2)], ""),
    ("Energieketten", "Stopfen an der Platte links", [(ZS % "5 × 20", 2), (MU % 5, 2)], ""),
    ("Energieketten", "Stopfen in der X-Ablage (Sicherung)", [(ZS % "4 × 18", 1), (MU % 4, 1), (SB % 4, 1)], ""),
    ("Energieketten", "Rinnenhalter unter der Ablage", [(ZS % "5 × 16", 6), (NM % 5, 6)], ""),
    ("Energieketten", "Ablage hinten auf Rinnenhalter", [(ZS % "4 × 16", 3), (MU % 4, 3)], ""),
    ("Energieketten", "Anschlussdose auf Rinnenhalter", [(ZS % "4 × 25", 2), (MU % 4, 2)], ""),
    ("Energieketten", "Deckel Anschlussdose", [(ZS % "3 × 12", 2), (MU % 3, 2)], ""),
    ("Energieketten", "Leitungsbogen quer (a, Steg, b)", [(ZS % "3 × 60", 2), (MU % 3, 2)], "**auf 57 mm kürzen**"),
    ("Energieketten", "Verbindungsplatte am Leitungsbogen", [(ZS % "4 × 20", 2), (MU % 4, 2)], ""),
    ("Energieketten", "Verbindungsplatte am Umlenkkopf", [(ZS % "4 × 25", 2), (MU % 4, 2)], ""),
    ("Energieketten", "Mast am Umlenkkopf", [(ZS % "4 × 16", 2), (MU % 4, 2)], ""),
    ("Energieketten", "Mastwinkel durch den Mast in die Ablagestirn", [(ZS % "4 × 20", 2)], "nicht länger: Gewinde nur 10 tief"),
    ("Energieketten", "Mastwinkel oben in den Mast", [(ZS % "4 × 12", 2)], ""),
    ("Energieketten", "Mastwinkel unten in die Ablage hinten", [(ZS % "4 × 12", 2)], ""),
    ("Energieketten", "Distanzstück am Mast", [(ZS % "4 × 20", 2), (MU % 4, 2)], ""),
    ("Energieketten", "Leitungsschellen auf Bogen, Kopf und Sockeln", [(ZS % "3 × 30", 8), (MU % 3, 8)],
     "Spitze darf unten nicht vorstehen, sonst kürzen"),
    ("Energieketten", "Leitungsschelle auf Verbindungsplatte", [(ZS % "3 × 35", 2), (MU % 3, 2)], "**auf 32 mm kürzen**"),
    ("Energieketten", "Spezialschelle am Umlenkkopf", [(ZS % "3 × 25", 1), (MU % 3, 1)], ""),
    ("Energieketten", "Leitungssockel auf Ablage hinten", [(ZS % "3 × 12", 4), (MU % 3, 4)], ""),

    ("Unterbau", "Kabelkanal senkrecht an der Stütze", [(ZS % "5 × 10", 4), (NM % 5, 4)], ""),
    ("Unterbau", "Kabelkanal quer am Bein", [(ZS % "5 × 10", 2), (NM % 5, 2)], ""),
    ("Unterbau", "Deckel Übergang unten", [(ZS % "3 × 10", 2), (MU % 3, 2)], ""),
    ("Unterbau", "Haube am Geräteboden", [("Spax 3,5 × 8", 8)], "vorbohren Ø2,5"),
    ("Unterbau", "Haube an den vorderen Beinen", [(ZS % "5 × 8", 4), (NM % 5, 4)], ""),
    ("Unterbau", "Haube am Wannenkäfig, hinten", [(ZS % "5 × 55", 2), (NM % 5, 2)], ""),
    ("Unterbau", "Haube am Wannenkäfig, vorn", [(ZS % "5 × 30", 2), (NM % 5, 2)], ""),
    ("Unterbau", "Rosette Querkanal", [(ZS % "3 × 6", 3), (MU % 3, 3)], ""),
    ("Unterbau", "Ablaufhalter am Querrohr", [(ZS % "5 × 20", 2), (NM % 5, 2)], ""),
    ("Unterbau", "Deckel Ablaufhalter", [(ZS % "4 × 30", 2), (MU % 4, 2)], ""),
]

ARTEN = (("Zylinderschrauben ISO 4762", "ISO 4762"), ("Sechskantschrauben DIN 933", "DIN 933"),
         ("Senkschrauben DIN 7991", "DIN 7991"), ("Muttern", ("ISO 4032", "DIN 439")),
         ("Nietmuttern", "Nietmutter"), ("Scheiben ISO 7089", "ISO 7089"),
         ("Sonstiges", ("Blindniet", "Spax", "Rillenkugellager")))


def sortkey(artikel):
    return [int(z) if z.isdigit() else z for z in re.split(r"(\d+)", artikel)]


def bestellen(n):
    """Bedarf + 10 %, mindestens 2 Stück Reserve."""
    return n + max(2, math.ceil(n * 0.1))


def main():
    summe = {}
    for _, _, teile, _ in V:
        for artikel, n in teile:
            summe[artikel] = summe.get(artikel, 0) + n
    z = ["# Normteile", "",
         "Erzeugt von `cad/normteile.py` (dort ändern, nicht hier). Anzahl und Längen sind aus den Bohrungen "
         "des Zusammenbaus ermittelt. Die Teile aus `cad/stueckliste.md` (Wellen Ø8, Zylinderstifte, "
         "Schmiernippel, Gewindestangen M16) stehen nur dort. Muttern M12 liegen den Schaltern LJ12A3 bei. "
         "Kabelbinder und Kabelverschraubungen: `docs/AUFGABEN.md`, Punkt 16.", "",
         "## Gesamtliste", "", "„Bestellen“ ist der Bedarf plus 10 %, mindestens 2 Stück Reserve.", ""]
    for titel, kennung in ARTEN:
        zeilen = sorted((a for a in summe if a.startswith(kennung)), key=sortkey)
        z += ["### " + titel, "", "| Artikel | Bedarf | Bestellen |", "|---|---:|---:|"]
        z += ["| %s | %d | %d |" % (a, summe[a], bestellen(summe[a])) for a in zeilen]
        z += ["", "Summe %d Stück." % sum(summe[a] for a in zeilen), ""]
    z += ["## Je Verbindung", ""]
    gruppe = None
    for g, verbindung, teile, bem in V:
        if g != gruppe:
            z += ["", "### " + g, "", "| Verbindung | Normteile | Bemerkung |", "|---|---|---|"]
            gruppe = g
        z.append("| %s | %s | %s |" % (verbindung, ", ".join("%d× %s" % (n, a) for a, n in teile), bem))
    with open(os.path.join(CAD, "normteile.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(z) + "\n")
    print("%d Verbindungen, %d Artikel, %d Stück -> cad/normteile.md" % (len(V), len(summe), sum(summe.values())))


if __name__ == "__main__":
    main()
