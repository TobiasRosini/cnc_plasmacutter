# Energieketten

Beide Ketten: **igus E2/000 Serie 2400.03** (innen 38 × 25, außen 54 × 35, Teilung 46 mm/Glied, im Innenradius aufklappbar), Anschlussteile **igus 2030.12PZ** (Kunststoff, verriegelt, Satz für beide Enden): Platte 7 mm, 55 breit, 40 lang, je 2 Bohrungen Ø6,1 im Abstand 25 quer zur Kette, 10 mm vom äußeren Ende; befestigt mit M5. Radius R bis Kettenmitte (igus: Bauhöhe H = 2R + 35). Länge nach igus S/2 + K (Katalog 5.102).

| | Artikel | Glieder | Länge |
|---|---|---|---|
| Y-Kette | 2400.03.125.0 | 23 | 1058 mm (igus-Formel 1056) |
| X-Kette | 2400.03.075.0 | 14 | 644 mm (igus-Formel 629) |
| Anschlussteile | 2030.12PZ.A1 (vormontiert, Einbaulage A1) | 2 Sätze | |
| Trennstege | 211, jedes 2. Glied | Y 11, X 7 | |

Belegung und Leitungen: `docs/Kabelliste.md`.

## Y-Energiekette (rechts, liegend)

```
python3 cad/live.py cad/energiekette/energiekette.py
```

- R125, 23 Glieder, Festpunkt bei Rahmen-y 825 (105 mm vor der Mitte des Y-Wegs, so dass die längere igus-Kette hinten nicht weiter übersteht), **Schlaufe hinten**, die Kabel verlassen den Festpunkt nach vorn (Schaltschrank und Plasmagerät stehen vorn). Seit die X-Ablage über der Brücke liegt, reicht die Schlaufe nur noch knapp 10 mm hinter den Rahmen.
- Träger Stahl 40 × 20 × 2 flach über die ganze Rahmenlänge, Unterkante 163 mm über Rahmen-OK (über dem X-Schalterblock), darauf hinten eine Rinne aus 2-mm-Blech bis hinter das feste Kettenende, davor ein Kabelkanal 40 × 40 bis y 1450 (weiter siehe `cad/unterbau/README.md`). Zwei Stützen außen am Längsträger an den Rahmenenden: je ein Rohr 20 × 40 × 2 (M6 in Nietmuttern), oben ein Druckkopf unter dem Träger (kopfüber druckbar, M5-Muttern in Schlitzen).
- Kettenturm aus Alu-Flachmaterial 40 × 8 an der Stirn der rechts um 47 mm verlängerten Brücke: 4× M6 in Muttern eines Einsteckteils (Druck, Muttern seitlich eingeschoben), das in der Brücke steckt und von den beiden M6 des Sattels mit gehalten wird. Ohne Laschen: Druckteile mit eingepressten M5-Muttern sitzen innen am Turm (Halter Y oben, Ablagehalter X unten).
- Kette innen 7 mm außerhalb der Schienenmitte: Der Z-Schlitten fährt bei X ganz rechts bis knapp davor. Der Z-Kopf ist rechts schmaler (52 statt 58 mm).
- Gesamtbreite mit Kette: 781 mm.
- Im Zusammenbau wird die Kette für die jeweilige Portallage neu berechnet.

## X-Energiekette

Seiten von vorn gesehen (vorn = +Y): die Y-Kette liegt rechts (kleines x).

- R75 (R65 gibt es bei igus nicht; die Adern liegen innen in der Kehre damit noch über R60), 14 Glieder, liegend auf einer Ablage (Alu 40 × 20 × 2 + Rinne) über der Brücke, direkt hinter dem Z-Kopf, Unterkante 225 mm über Rahmen-OK, oben bis 432.
- **Festpunkt bei Rahmen-x 476** (2× M5 durch den Rinnenboden in Nietmuttern der Ablage), **Schlaufe nach rechts** zum Kettenturm. Der Festpunkt liegt so weit rechts, wie es die Kette mit igus-Länge zulässt: Bei X ganz rechts beginnt der Bogen direkt am Anschlussteil, die Schlaufe bleibt 4 mm vor dem Turm. Steht der Wagen links, trägt sich das obere Trum etwa 160 mm frei über den Festpunkt hinaus (igus: freitragend bis etwa 2 m). Bewegtes Ende am Halter (Druck) an der Rückseite des Z-Kopf-Sockels (2× M5 in Muttern), 10 mm rechts der Wagenmitte. Die Leitungen treten dort nach links aus.
- Warum nicht ganz links: kürzere Kette und kürzerer Rücklauf der Leitungen in der Rinne hinten (vorher Festpunkt links, 0,80 m Kette, 1,42 m Leitung bis zum Festpunkt). Ganz in die Mitte geht mit der igus-Länge nicht, dann stieße die Schlaufe an den Turm.
- Warum Schlaufe rechts: Die Adern müssen am bewegten Ende zum Brenner umkehren (Kehre R60, etwa 70 mm). Rechts stehen bei X am Ende Kettenturm und Y-Kettenende; links ist der Platz frei. Bei X ganz links reichen die Adern 4 mm über die Brückenstirn (Rahmen-x 724, oberhalb der Platte, innerhalb der Gesamtbreite).
- Ablage rechts auf dem Zapfen des Ablagehalters am Turm (darauf liegt bei X ganz rechts die Schlaufe), links an der Platte an der linken Brückenstirn (Stopfen mit 2× M5). Die Rinne endet hinter dem Festpunkt; links davon liegt nichts mehr auf der Ablage.

## Leitungen (ohne Schutzschlauch)

Der Mantel des Brennerpakets wird bis zur Knickschutztülle aufgeschnitten; die Adern (PU-Luftschlauch 8, Stromkabel 6,3, Pilot ~3, 2× ~2) laufen lose mit den Motor- und Schalterkabeln durch beide Ketten. Kleinster Biegeradius 60 (Stromkabel). Im Modell als Hüllrohre: Ø20 für alle Leitungen, Ø16 für die Adern zum Brenner.

- **Y-Ende → X-Festpunkt** (ca. 1,28 m): am Y-Ende nach vorn (Kabelbinder im Halter Y), hoch, im Bogen über das Y-Kettenende nach hinten, hinter der Ablage hinunter, in einer **Rinne hinten** (Alu-Winkel 40 × 20 × 2 auf drei Haltern aus Druck, je 2× M5 von unten in Nietmuttern der Ablage) nach links und mit einer Kehre R60 in den Festpunkt.
- **X-Ende → Brenner** (ca. 0,40 m): nach links aus dem Kettenende, hoch, im Bogen nach vorn und von oben in die Tülle. Höchster Punkt bei Z unten ca. 1,47 m über Boden; bei Z oben wird die Schlaufe 100 mm länger und wölbt sich etwas höher.
- Motor- und Schalterkabel zweigen am X-Ende ab.
- Gesamtbreite: 784 mm.
