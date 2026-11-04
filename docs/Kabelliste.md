# Kabelliste

Stand 03.11.2026. Seiten von vorn gesehen. Schaltschrank und Plasmagerät stehen unter der Wanne vorn (`cad/unterbau/`). Ketten: igus 2400.03 (innen 38 × 25), Y R125, X R75, siehe `cad/energiekette/README.md`.

## Bewegte Leitungen (durch die Ketten)

| Nr. | Leitung | Von | Nach | Typ | Ø ca. | Y-Kette | X-Kette | Länge ca. |
|---|---|---|---|---|---|---|---|---|
| 1 | Brenner: Luftschlauch | Plasmagerät | Brenner SP80M | PU 8 (im Schlauchpaket) | 8 | ✓ | ✓ | 5,0 m ab Gerät |
| 2 | Brenner: Stromkabel | Plasmagerät | Brenner | im Schlauchpaket, min. R60 | 6,3 | ✓ | ✓ | 5,0 m ab Gerät |
| 3 | Brenner: Pilot | Plasmagerät | Brenner | im Schlauchpaket | 3 | ✓ | ✓ | 5,0 m ab Gerät |
| 4 | Brenner: Start/Stopp (2 Adern) | Plasmagerät | Brenner | im Schlauchpaket; bei CNC-Start ungenutzt, im Paket lassen | 2 × 2 | ✓ | ✓ | 5,0 m ab Gerät |
| 5 | Motor X | Schaltschrank (Treiber) | X-Motor auf dem Wagen | igus CF10.07.05, (5 G 0,75)C: 4 Phasen + PE ans Motorgehäuse, Schirm | 7,5 | ✓ | ✓ | 5,0 m |
| 6 | Motor Z | Schaltschrank (Treiber) | Z-Motor auf dem Z-Kopf | igus CF10.07.05 | 7,5 | ✓ | ✓ | 5,0 m |
| 7 | Referenzschalter X | Schaltschrank (24 V, Eingang) | LJ12A3 am rechten Y-Winkel | igus CF9.02.03.INI, 3 × 0,25 | 4,5 | ✓ | – | 3,1 m |
| 8 | Referenzschalter Z | Schaltschrank | LJ12A3 im Z-Kopf | igus CF9.02.03.INI | 4,5 | ✓ | ✓ | 5,0 m |
| 9 | Schalter Schwimmkopf | Schaltschrank (24 V, Eingang) | LJ12A3-4-Z/AY im oberen Steg des Schwimmkopf-Halters (fährt mit Z) | igus CF9.02.03.INI, 3 × 0,25 | 4,5 | ✓ | ✓ | 5,3 m |
| (10) | Ohmsche Antastung (falls gewählt) | Schaltschrank | Brennerkappe | 1 Ader, hochspannungsfest isoliert | ~3 | ✓ | ✓ | 5,0 m |

Längen bis zu den Klemmen im Schaltschrank (bzw. bis zum Brenneranschluss vorn am Plasmagerät), aus dem Modell, ohne Reserve:
Schaltschrank bis festes Y-Kettenende ca. 1,75 m (Querkanal über dem Gerät 0,35, senkrecht außen rechts 0,5, Kanal auf dem Y-Träger 0,6, im Schrank 0,3), Y-Kette 1,06 m, Y-Ende bis X-Festpunkt 1,28 m, X-Kette 0,64 m, X-Ende bis Verbraucher 0,3–0,5 m. Plasmagerät bis festes Y-Kettenende ca. 1,6 m.

**Schlauchpaket SP80M:** muss mindestens 5,0 m lang sein (Länge noch messen).

Kabelweg: `cad/unterbau/README.md`.

Die LJ12A3 haben ein fest angespritztes PVC-Kabel, das nicht für Schleppketten gedacht ist. Es wird kurz vor der Kette (X: am Turm, Z und Schwimmkopf: am X-Wagen) auf die Kettenleitung verlötet und mit Schrumpfschlauch isoliert.

## Bestellung igus (chainflex, auf Länge geschnitten)

| Artikel | Aufbau | Ø | Biegeradius in der Kette | Menge |
|---|---|---|---|---|
| CF10.07.05 | (5 G 0,75)C, TPE, geschirmt | 7,5 | 5 × d | X und Z je 5,5 m = 11 m; dazu Y-Motoren (fest verlegt) je etwa 3 m |
| CF9.02.03.INI | 3 × 0,25, TPE (für Initiatoren) | 4,5 | 5 × d | X 3,5 m, Z 5,5 m, Schwimmkopf 6 m = 15 m; dazu Y-Schalter (fest verlegt) je etwa 3 m |

Warum 5 G statt 4 G: Grün-gelb ist für den Schutzleiter reserviert. Bei 4 G müsste eine Phase auf Grün-gelb laufen; mit 5 G gehen die vier schwarzen nummerierten Adern auf die Phasen und Grün-gelb an das Motorgehäuse. Der Schirm wird am Treiber bzw. im Schaltschrank aufgelegt. Die Y-Motoren (fest verlegt) können dieselbe Leitung bekommen.

Mengen mit etwa 0,5 m Reserve je Leitung. Werte aus dem igus-Leitungskatalog (ältere Ausgabe); Lieferbarkeit und aktuellen Preis im igus-Shop prüfen.

## Belegung der Ketten

Ein Trennsteg igus 211 in jedem zweiten Glied (Y: 11 Stück, X: 7 Stück) teilt den Innenraum:

| Fach | Breite | Inhalt | Belegung |
|---|---|---|---|
| Brenner | ca. 19 | Nr. 1–4 (+10) | unten Luft 8, Strom 6,3, Pilot 3 nebeneinander (17,3), darüber die beiden Start/Stopp-Adern |
| Steuerung (innen) | ca. 17 | Nr. 5–9 | unten die zwei Motorleitungen (2 × 7,5 = 15), darüber die Schalterleitungen (3 × 4,5 = 13,5) |

Höhe je Fach höchstens 7,5 + 4,5 = 12 von 25 mm. Die Plasmaleitungen (Pilot, Strom) liegen so nicht direkt neben den Schalterleitungen. Im Brennerfach liegt das Stromkabel unten in der Mitte (Luft und Pilot außen), weil es im Versatz zwischen den Ketten auf der Innenseite R60 braucht.

Zwischen Y- und X-Kette bleiben die beiden Fächer als getrennte Pfade erhalten: Trennsteg in Leitungsbogen und Umlenkkopf, Leitungsschellen mit Mittelsteg (`cad/energiekette/README.md`). In der Y-Kette liegt die Steuerung innen, in der X-Kette hinten.

## Biegeradien

Leitungen, die innen in der Kehre anliegen, biegen sich enger als der Kettenradius: R_Leitung ≈ R − 12,5 + d/2.

| Kette | Leitung | Biegung innen | Anforderung |
|---|---|---|---|
| X (R75) | Stromkabel Ø6,3 | ca. 66 | min. 60 ✓ |
| X (R75) | Motorleitung CF10 Ø7,5 | ca. 66 | CF10: 5 × d = 38 ✓ |
| X (R75) | Schalterleitung Ø4,5 | ca. 65 | CF9: 5 × d = 23 ✓ |
| Y (R125) | alle | über 115 | ✓ |

## Fest verlegt (nicht in den Ketten)

| Leitung | Von | Nach | Typ |
|---|---|---|---|
| Motor Y rechts, Motor Y links | Schaltschrank | Y-Motoren hinten am Rahmen | 4 × 0,75 geschirmt |
| Referenzschalter Y rechts, Y links | Schaltschrank | LJ12A3 an den Y-Motorhaltern | 3 × 0,25 |
| CNC-Buchse Plasmagerät (Torch On, Arc OK, geteilte Lichtbogenspannung) | Plasmagerät | Schaltschrank (Mesa 7i96S, THCAD) | geschirmt, Adernzahl nach Anleitung S. 13 |

## Offen

- Längen der fest verlegten Y-Leitungen nach Verlegeweg am Rahmen.
- Entscheidung Schwimmkopf oder ohmsche Antastung (Nr. 10).
