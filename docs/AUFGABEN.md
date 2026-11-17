# Aufgabenplan bis zum Bau

Stand 15.11.2026. Gesammelt aus den READMEs, `cad/MONTAGE.md`, `cad/VERBINDUNGEN.md`, den Prüfberichten, `docs/Kabelliste.md` und dem Projektstand. Erledigtes abhaken und mit Datum versehen.

## A. Konstruktion abschließen (CAD)

1. [x] **Stellfüße und Rollen** (17.11.2026): Eckplatte 175 × 175 × 10 unter Bein, Längs- und Querrohr; Lenkrolle Ø125 (4× M8) diagonal innen, Stellfuß Gewindestange M16 in Schweißmutter unter der Beinmitte (taucht eingedreht ins Bein). Rahmen-OK im Betrieb 922 über Boden (`cad/grundrahmen/README.md`). **Offen:** Lagerung/Teller unten am Fuß (Tobi, Drehmaschine).
2. [x] **Wasserschutz über dem Geräteraum** (15.11.2026): Haube aus Alu 0,5 als U auf dem Kopf, so lang wie der Geräteboden, an Geräteboden, vorderen Beinen und Wannenkäfig; Querkanal durch eine gedruckte Rosette (`cad/unterbau/README.md`).
3. [x] **Wannenablauf** (15.11.2026): Messing-Tankdurchführung hinter der Haube (440 hinter der Wannenmitte), Klemmwinkel 90°, gerades HDPE-Rohr d25 nach hinten, Kugelhahn und Schlauchtülle an der Rahmenrückseite, Ablaufhalter (Druck) am hinteren Querrohr. Maße beim Kauf prüfen.
4. [x] **Bördelrand der Wanne schützen** (17.11.2026): Boden und Wände liegen unter Wasser und brauchen keinen Schutz, gefährdet ist nur der PE-Bördel (über dem Wasser, 1 mm unter dem Blech). Schutzleisten aus Blech 3 mm innen vor dem Bördel der Längswände, Auflageleisten auf 524 gekürzt, Softlimit X ±260 (`cad/auflage/README.md`).
5. [x] **Anschlussdose X-Referenzschalter** (17.11.2026): Druckteil auf dem rechten Rinnenhalter, CF9 aus dem Strang und PVC-Kabel des Schalters über je eine Kabelverschraubung M12, gelötet (`cad/energiekette/README.md`). Z und Schwimmkopf werden weiter am X-Wagen gelötet.
6. [x] **Leitungsführung** (17.11.2026): Bogen über dem Y-Ende und Abgang hinter der Ablage waren mit Leitungsbogen, Umlenkkopf, Distanzstück und Schellen schon erledigt. Funkenschutz: Feuerschutzschlauch innen 20 über die Brenneradern (X-Kettenende bis Tülle), innen 6 über das PVC-Kabel des Schwimmkopf-Schalters (`cad/energiekette/README.md`).
7. [x] **Stopfen links in der X-Ablage sichern** (17.11.2026): 1× M4 von unten durch die Ablage in eine Mutter im Stopfen.
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

16. [ ] **Kaufteile festlegen und bestellen**: Schienen HGR15 (Längen aus dem Modell) und Wagen HGH15CA (X mit Metallabstreifer), Riemen HTD5M/15 (Längen) und Scheiben, SFU1204 mit FK10, Motoren NEMA23 (2 × 1,9 Nm, 2 × 1,2 Nm), 4 Step/Dir-Treiber, Netzteile 48 V/24 V, Mesa THCAD (Variante), igus-Ketten und chainflex-Leitungen (Kabelliste), Referenz- und Schwimmkopfschalter LJ12A3, Präzisionswellen Ø8, 2 Kabelverschraubungen M12 × 1,5 (Kabel 3–6,5), Feuerschutzschlauch innen 20 (0,5 m) und innen 6 (0,3 m), Edelstahl-Kabelbinder, 4 Lenkrollen Ø125 mit Bremse (160 kg, Platte 100 × 80, Lochbild 80 × 60), Gewindestange M16 und Muttern für die Stellfüße.
17. [ ] Bei Lieferung prüfen: Lochbild FK10, Schaltabstand LJ12A3 auf den Stift 6 mm, Länge Schlauchpaket SP80M (mind. 5,0 m), Längen der fest verlegten Y-Leitungen.

## D. Elektrik und Steuerung

18. [ ] **Schaltschrank** 400 × 500 × 200: Stromlaufplan, Not-Aus/Sicherheitskreis, Schütz, Netzteile, Treiber, Mesa 7i96S, THCAD, Erdung/EMV (Plasma!), Belegung im Schrank, Klemmenplan.
19. [ ] **LinuxCNC/QtPlasmaC**: Konfiguration Mesa 7i96S, Gantry-Squaring mit zwei Y-Referenzschaltern, Softlimit Schneidbereich X ±260 um die Wannenmitte (Bördel), Z-Untergrenze ca. 3 mm unter Blechunterseite, Mindestwasserstand (Markierung oder Schwimmerschalter, optional), Schwimmkopf-Antastung, THC.
20. [ ] **Druckluft**: Wasserabscheider, Filter, Druckregler nach SPARTUS-Handbuch, Kompressor prüfen.
21. [ ] **Lüftung/Absaugung** der Werkstatt (das Wasserbett ersetzt sie nicht).
