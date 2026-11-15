# Aufgabenplan bis zum Bau

Stand 15.11.2026. Gesammelt aus den READMEs, `cad/MONTAGE.md`, `cad/VERBINDUNGEN.md`, den Prüfberichten, `docs/Kabelliste.md` und dem Projektstand. Erledigtes abhaken und mit Datum versehen.

## A. Konstruktion abschließen (CAD)

1. [ ] **Stellfüße und Rollen** an den Fußplatten (100 × 100 × 8, Ø13). Konzept laut Rahmen-README: Im Betrieb heben die Füße den Rahmen über die Rollen, zum Verfahren werden sie hochgedreht. Zu entscheiden: Fußtyp (Gelenkfuß M12?), Rollen (Lenk-/Bockrollen, Feststeller, Lochbild), Anbindung (M12 in 8 mm schneiden = gut 4 Gänge, oder Mutter aufschweißen), Lage der Rollen (eigene Laschen?). Grenze 800 mm Breite beachten (heute 793).
2. [x] **Wasserschutz über dem Geräteraum** (15.11.2026): Haube aus Alu 0,5 als U auf dem Kopf, so lang wie der Geräteboden, an Geräteboden, vorderen Beinen und Wannenkäfig; Querkanal durch eine gedruckte Rosette (`cad/unterbau/README.md`).
3. [x] **Wannenablauf** (15.11.2026): Messing-Tankdurchführung hinter der Haube (440 hinter der Wannenmitte), HDPE-Rohr d25, Winkel-Kugelhahn, Schlauchtülle, Schlauch nach hinten. Maße beim Kauf prüfen.
4. [ ] **Schutz der PE-Wanne** vor Plasmastrahl und heißer Schlacke (Projektstand Abschnitt 6, „sicherheitsrelevant“): Boden- und Wandschutz konstruktiv vorsehen oder bewusst über Wasserstand und Schnittbereich lösen. Entscheidung offen.
5. [ ] **Anschlusskasten** an der Kastenseite des rechten Y-Winkels (Übergang Y-/X-Kette, Lötstellen der LJ12A3-Leitungen).
6. [ ] **Leitungsführung**: Clips für den Bogen über dem Y-Ende und am Abgang hinter der Ablage; Funkenschutz der Adern am Brenner (Gewebe- oder Silikonschlauch).
7. [ ] **Stopfen links in der X-Ablage sichern** (kleben oder Querstift).
8. [ ] Rinnen (Y, X) und Kabelkanal auf den Trägern: Blindnieten Ø4 bzw. Schrauben, Lage festlegen (sonst beim Bau).
9. [ ] Optional: Außenkanten der Rippen am Mastwinkel ohne Fase (Rippen 1–2 mm einrücken, dann geht die Fase).

## B. Prüfen und Unterlagen fertig machen

10. [ ] **Montageprüfung** (`pruefe_montage.py`, letzter Lauf 12.11.) und Kollisionsprüfung im Zusammenbau nach allen Änderungen seit dem 12.11. (Spezialschelle, Verbindungsplatte, Radien/Fasen).
11. [ ] **7 gelbe Druckteile** in `cad/druckbarkeit.txt` ansehen: ub_kanalknoten, x_motorbock, x_wagenkoerper, y_motorhalter (+ _l), winkel_fest, winkel_kasten. Brücken/Überhänge akzeptieren oder ändern.
12. [ ] **Normteile in die Stückliste**: Schrauben, Muttern, Einpress- und Nietmuttern, Blindnieten, Stäbe (heute nicht enthalten), aus `VERBINDUNGEN.md` und dem Modell.
13. [ ] **Zuschnitt- und Einkaufsliste Halbzeuge** (Stahl, Alu, Bleche, Siebdruckplatte) über alle Baugruppen zusammengefasst.
14. [ ] **Druckliste**: alle STL mit Anzahl, Material (PETG/ASA), Drucklage, geschätztem Gewicht.
15. [ ] **Dokumente nachziehen**: veraltete „Offen“-Zeile im X-Wagen-README, Beschaffungsstand und „Nächste Schritte“ im Projektstand, Montageanleitung um die neuen Teile ergänzen.

## C. Beschaffung

16. [ ] **Kaufteile festlegen und bestellen**: Schienen HGR15 (Längen aus dem Modell) und Wagen HGH15CA (X mit Metallabstreifer), Riemen HTD5M/15 (Längen) und Scheiben, SFU1204 mit FK10, Motoren NEMA23 (2 × 1,9 Nm, 2 × 1,2 Nm), 4 Step/Dir-Treiber, Netzteile 48 V/24 V, Mesa THCAD (Variante), igus-Ketten und chainflex-Leitungen (Kabelliste), Referenz- und Schwimmkopfschalter LJ12A3, Präzisionswellen Ø8.
17. [ ] Bei Lieferung prüfen: Lochbild FK10, Schaltabstand LJ12A3 auf den Stift 6 mm, Länge Schlauchpaket SP80M (mind. 5,0 m), Längen der fest verlegten Y-Leitungen.

## D. Elektrik und Steuerung

18. [ ] **Schaltschrank** 400 × 500 × 200: Stromlaufplan, Not-Aus/Sicherheitskreis, Schütz, Netzteile, Treiber, Mesa 7i96S, THCAD, Erdung/EMV (Plasma!), Belegung im Schrank, Klemmenplan.
19. [ ] **LinuxCNC/QtPlasmaC**: Konfiguration Mesa 7i96S, Gantry-Squaring mit zwei Y-Referenzschaltern, Z-Untergrenze ca. 3 mm unter Blechunterseite (Bördel an den X-Enden), Schwimmkopf-Antastung, THC.
20. [ ] **Druckluft**: Wasserabscheider, Filter, Druckregler nach SPARTUS-Handbuch, Kompressor prüfen.
21. [ ] **Lüftung/Absaugung** der Werkstatt (das Wasserbett ersetzt sie nicht).
