# Montage (Stand 24.10.2026)

Alle Schraubverbindungen mit Ausführung und offenen Kandidaten: `cad/VERBINDUNGEN.md`.

Prüfung: `python3 cad/live.py cad/pruefe_montage.py` → `cad/zusammenbau/montage.txt`. Jede Schraubenbohrung wird bis 3 mm über ihr Ende hinaus verfolgt; trifft sie ein anliegendes Teil, muss dort eine Bohrung oder ein Gewinde sein. Aktuell: **0 offen**, 54 bekannte, gewollte Fälle, keine sich schneidenden Bohrungen (Schraubenköpfe unter Deckteilen, Muttertaschen, Klemmschrauben auf den Brenner, Schalter in Bohrungen).

## Reihenfolge Portal

Vorher in alle Druckteile die Muttern einpressen bzw. seitlich in ihre Schlitze schieben (Taschen liegen jeweils auf der Seite, zu der die Schraube die Mutter zieht; Schlitze werden vom Nachbarteil verschlossen).

1. Y-Wagen auf die Schienen, **Flachstange** mit 8× M4×12 von oben (Köpfe gesenkt).
2. **Y-Winkel** aufsetzen, 4× M4×18 im Sattelboden (vor der Brücke!).
3. X-Schienen oben und unten an die **Brücke** (M4-Gewinde in der Brückenwand), Einsteckteile rechts und links einschieben (M6-Muttern vorher seitlich in die Schlitze).
4. Brücke in die Sättel legen, 4× M6×60 je Sattel quer (auch durch die Einsteckteile), Muttern vorn eingepresst, Köpfe hinten. **Vor der festen Riemenklemme:** die oberen beiden Köpfe liegen danach unter Klemmplatte und Fahne.
5. Feste Riemenklemme: Fahne + Klemmplatte, 4× M5×65 durch Turm und Basis in die Flachstange.
6. Kettenturm (gerades Alu-Flachmaterial 40 × 8) an die Brückenstirn (4× M6 in die Muttern des Einsteckteils). Innen am Turm, alles M5 von außen durch den Turm in Muttern der Druckteile: **Ablagehalter X** (2×), **Halter Y** oben (2×).
7. X-Wagen: Wagenkörper (Druck) mit 4× M4 oben und 4× M4 unten an die Wagen, je mit Scheibe. Motorbock mit den Umlenkrollen (M8 von unten) von hinten an die Rückseite des Decks (4× M4 in Muttern, Köpfe in den Schrägen der Stege gesenkt), **erst danach** Motor mit Scheibe einsetzen: die Senkungen liegen dicht vor der Motorfront. Riemen spannen: Hebel zwischen Motor und Flanschwand, Motor nach hinten drücken, M5 festziehen. Spritzschutz erst nach dem unteren Wagen (4× M3×6 in Muttern im Boden).
8. Platte an die linke Brückenstirn (4× M6 in die Muttern des linken Einsteckteils). X-Ablage rechts auf den Zapfen des Ablagehalters schieben (2× M5 von unten durch die untere Rohrwand), links Stopfen im Rohr, 2× M5 durch die Platte. Drei Rinnenhalter unter die Ablage (je 2× M5 von unten in Nietmuttern; in den dritten, unter dem festen Kettenende, vorher die M5-Mutter seitlich einschieben), Ablage hinten darauf (je 1× M4 in Mutter).
9. Festes Ende der X-Kette (Anschlussteil igus 2030.12PZ) bei Rahmen-x 476 in die Rinne (2× M5 durch den Rinnenboden: vorn in die Nietmutter der Ablage, hinten in die Mutter im Rinnenhalter), bewegtes Ende der Y-Kette von unten an den Halter Y (2× M5 in Muttern). Leitungsbogen auf den Halter Y (die beiden M5 des Kettenendes länger, Muttern seitlich in den Bogen). Mast (Alu 40 × 8) mit dem **Versteifungswinkel** (Druck) an die Ablage hinten: Winkel von hinten unten an Mast und Ablage, 2× M4 × 25 durch Winkel und Mast in Gewinde in der hinteren Stirn der Ablage, oben 2× M4 durch den Winkel in Gewinde im Mast, unten 2× M4 von unten durch den Winkel in Gewinde in der Ablage, Umlenkkopf oben auf den Mast (2× M4), Distanzstück darunter (2× M4 von hinten durch den Mast), Verbindungsplatte in die Aussparungen von Bogen und Kopf (je 2× M4 von oben). Leitungen vom Y-Ende nach vorn (Kabelbinder durch die zwei Schlitze im Halter Y), um den Leitungsbogen nach hinten, über den Umlenkkopf hinter der Ablage hinunter, in der Ablage hinten nach links und mit der Kehre von links in das feste X-Ende. Die Leitungen bleiben dabei in zwei Pfaden wie in den Kettenfächern (Brenner / Steuerung, Lage siehe `cad/energiekette/README.md`): oben links und rechts des Trennstegs im Bogen bzw. des Mittelstegs der Schellen am Kopf, auf den ersten 200 mm der Ablage hinten um 90° verdrillt, danach Steuerung vorn. Vorher 2 Leitungssockel auf die Ablage hinten (je 2× M3 von unten in eingepresste Muttern). Zuletzt die 6 Leitungsschellen mit dem Mittelsteg zwischen den Pfaden auflegen (je 2× M3 × 25 durch die Schenkel: auf Bogen, Platte, Kopf oben, Kopf am senkrechten Lauf und die beiden Sockel), Kabelbinder an Bogen und Kopf sowie zwei durch das Distanzstück. Überall mindestens R60 (Steuerung innen in Kehre und Bogen unten R50).
10. Z-Achse: Grundplatte an die Front des Wagenkörpers (6× M5 in Muttern, davon 2 unten), Leisten + Schienen (M4 durch die Leiste in die Grundplatte), Z-Kopf-Sockel (4× M5), FK10 mit Spindel (4× M4 in Muttern unten im Sockel), Kupplung, dann Motorhalter mit Motor (4× M4 durch die Säulen in Muttern unten im Sockel). Schwimmkopf: Halter unten an den Schlitten (3× M5), Stäbe Ø8 × 100 in die Sacklöcher einpressen, Träger (Bohrungen auf 8 aufgerieben, Schmiernippel M6) aufschieben, Halter oben auf die Stäbe und 2× M5 von oben in die Schlitten-Oberkante, Schalter LJ12A3 in den oberen Steg (eingepresste Mutter, Kontermutter), Brenner einlegen, Klemmdeckel mit Zielstift spannen.
11. Halter der X-Kette (Druck) an die Rückseite des Z-Kopf-Sockels (2× M5 in Muttern), bewegtes Ende von unten an den Halter (2× M5 in Muttern). Adern des Brennerpakets links aus dem Kettenende, im Bogen (R60) hoch und nach vorn, von oben in die Tülle; Motor- und Schalterkabel zweigen hier ab.
12. Spritzschutz X: Halter (Alu 4 mm, aus dem Reststück der Brücke) an die vordere Stirn beider Flachstangen (je 2× M4 in Gewinde), Schutzstreifen (Flachstahl 50 × 3) innen an die Laschen (je 2× M4 mit Mutter). Der Streifen läuft zwischen Z-Grundplatte und Brenner.

## Rahmen

- Oberrahmen auf den Untertisch: 6× M8×16 durch die Unterseite der oberen Querrohre (Zugang Ø16 von oben) in Nietmuttern M8 in den unteren Querrohren.
- Y-Motor- und Umlenkhalter: **M6-Nietmuttern** im Längsträger (Ø9), die 3-mm-Wand trägt kein gutes M6-Gewinde.
- Y-Schienen: M4 direkt in die 3-mm-Wand (gut 4 Gänge).
- Spritzschutz Y: Flachstahl 50 × 3 innen an die Längsträger, je 6 Blindnieten Ø4.
- Auflage: Kammträger in die Wanne stellen (x −200 / 0 / +200), Auflageleisten in jede zweite Schlitzposition stecken (`cad/auflage/README.md`).
- Wannenkäfig: 3× M6 je Seite durch die Außenwand des Rings (Zugang Ø12 innen, Wanne vorher heraus) in Nietmuttern M6 im Längsrohr des Untertischs.
- Geräteboden (Siebdruckplatte 9 mm) auf die unteren Längsrohre: 6× M6 von oben in Nietmuttern. Darauf Plasmagerät rechts (250 mm hinter der Schrankfront) und Schaltschrank vorn links (`cad/unterbau/README.md`).
- Tropfboden unter dem Wannenkäfig (Gefälle nach hinten), Ablauf durch die Hülse; Befestigung noch offen.
- Stützen der Y-Kette: hinten Rohr 20×40×2 (2× M6), vorn Rohr 40×40×2 hinter dem Bein (4× M6, in Längsträger und Längsrohr des Untertischs), jeweils durch die Innenwand (Zugang Ø13 außen) in Nietmuttern. Hinten Druckkopf mit 2× M5-Muttern (von unten in die Schlitze) einstecken und durch die Rohrwand verschrauben.
- Kabelkanäle und Träger: senkrechter Kanal 25 × 60 außen auf die vordere Stütze (4× M5 in Nietmuttern), Querkanal 25 × 60 hinter dem Bein (2× M5 in Nietmuttern im Bein) in die obere rechte Ecke des Schaltschranks, Bogen unten (Druck) auf beide Enden stecken. Kanalknoten (Druck) von oben auf die vordere Stütze und den senkrechten Kanal setzen, 2× M5 von vorn in die Stütze. Y-Träger hinten auf den Stützkopf legen und vorn in die Muffe des Knotens schieben: hinten 2× M6 von unten, vorn 2× M5 von innen durch den Knoten in Nietmuttern im Träger. Kanal 40 × 40 auf dem Träger vom festen Kettenende bis in den Knoten (3× M4 in Nietmuttern). Leitungen durch den Knoten fädeln, sonst über die Kanaldeckel einlegen; Deckel des Bogens mit 2× M3 schließen (Muttern vorher seitlich einschieben).

## Noch offen

- Rinnen (Y und X) und Kabelkanal auf den Trägern: Blindnieten Ø4 bzw. Schrauben, Lage beim Bau festlegen.
- Befestigung Tropfboden.
- Ketten igus 2400.03 (Y: 2400.03.125.0, 23 Glieder; X: 2400.03.075.0, 14 Glieder), Anschlussteile igus 2030.12PZ: 2 Bohrungen Ø6,1 im Abstand 25, 10 mm vom äußeren Ende, mit M5 verschrauben. Feste Enden: 2× M5 durch den Rinnenboden in Nietmuttern M5 im Y-Träger bzw. in der X-Ablage (X: hinteres M5 in eine Mutter im Rinnenhalter).
- Stopfen links in der X-Ablage sichern (kleben oder Querstift).
- Leitungen sind als Hüllrohre vereinfacht (Ø20 / Ø16). Führung des Bogens über dem Y-Ende und am Abgang hinter der Ablage (Clips) noch offen; Adern am Brenner gegen Funken schützen (Gewebe- oder Silikonschlauch).
- Anschlusskasten noch nicht gezeichnet.
- Stellfüße und Rollen an den Fußplatten.
