# Schraubverbindungen (Stand 24.10.2026)

Vorgabe: am Rahmen keine langen Bolzen mit Mutter, sondern Gewinde (direkt geschnitten oder Nietmutter / Einpressmutter im Rohr). In Druckteilen bevorzugt eingepresste Muttern, sonst eingeschmolzene Gewindeeinsätze.
Geprüft mit `python3 cad/live.py cad/pruefe_montage.py`. Die Prüfung meldet jetzt auch Bohrungen, die sich im selben Teil schneiden.

## Rahmen

| Verbindung | Ausführung | Stand |
|---|---|---|
| Oberrahmen auf Untertisch | 6× M8×16 durch die Unterseite des oberen Querrohrs (Zugang Ø16 von oben) in Nietmuttern M8 im unteren Querrohr | **neu** (vorher M8×90 mit Mutter) |
| Wannenkäfig am Untertisch | 6× M6 durch die Außenwand des Rings (innen Zugang Ø12, Wanne vorher heraus) in Nietmuttern M6 im Längsrohr | **neu** (vorher M8 quer mit Mutter, Bohrungen lagen 10 mm versetzt) |
| Y-Schienen | M4 direkt in die 3-mm-Wand geschnitten | ok |
| Y-Motor- und Umlenkhalter (Druck) | 4× M6 in Nietmuttern, Köpfe gesenkt | ok |
| Y-Kettenstützen | ein Rohr 20×40×2, 2× M6 durch die Innenwand (außen Zugang Ø13) in Nietmuttern M6 im Längsträger | **neu** (vorher 2 Rohre geschweißt, M8 durch alles) |
| Stützkopf (Druck) im Rohr | 2× M5 durch die Rohrwand in Muttern, die von unten in Schlitze im Zapfen geschoben werden | **neu** |
| Y-Kettenträger auf Stützkopf | 2× M6 von unten in Nietmuttern in der Trägerunterseite | **neu** |
| Rinnen auf den Trägern | Blindnieten Ø4 | offen (Lage beim Bau) |
| Stellfüße / Rollen | Fußplatte 8 mm mit Ø13 | offen: M12 schneiden (nur gut 4 Gänge) oder Mutter aufschweißen |

## Portal und Wagen

| Verbindung | Ausführung | Stand |
|---|---|---|
| Flachstange auf Y-Wagen | 4× M4 von oben, gesenkt | ok |
| Y-Winkel (Druck) auf Flachstange | M4 gesenkt in Gewinde in der Flachstange, Riemenklemme M5×65 durch Turm und Basis in Gewinde | ok (lange Schraube, aber in Gewinde) |
| Sattel ↔ Brücke | 4× M6×60 quer durch Sattel, Brücke und Einsteckteil, Muttern vorn eingepresst, Köpfe hinten | bleibt. Zugang geprüft: Muttern sind gefangen, die unteren Köpfe immer frei, die oberen liegen unter Y-Klemmplatte und Fahne → Brücke vor der Riemenklemme montieren |
| Kettenturm / rechte Platte an Einsteckteil | 4× M6 in Muttern, seitlich in Schlitze geschoben | rechts Löcher verlegt (schnitten die Sattel-M6) |
| X-Schienen an Brücke | M4 in die 4-mm-Alu-Wand | ok |
| X-Wagenkörper auf X-Wagen | 4× + 4× M4, gesenkt mit Scheibe | ok |
| Z-Grundplatte an Wagenkörper | 6× M5 in Muttern, von der Seite eingeschoben | ok |
| Motorbock an Wagenkörper | 4× M4 in Muttern, von der Seite eingeschoben | ok |
| Motor X | 4× M5 in Langnuten (Muttern) | ok |
| Umlenkrollen X | M8 von unten, Kopf in Sechskanttasche, oben Mutter | ok |
| Spritzschutz | 4× M3×6 in Muttern, von der Seite eingeschoben | ok |

## Muttern in Druckteilen

Keine Gewindeeinsätze mehr. Wo die Schraube die Mutter in eine Tasche an der Außenfläche zieht, ist es eine einfache Sechskanttasche; sonst ein Schlitz, durch den die Mutter seitlich eingeschoben wird (Schlüsselflächen parallel zum Schlitz, dreht nicht mit). Taschenmaße: M3 5,7 × 2,7, M4 7,2 × 3,5, M5 8,2 × 4,3, M6 10,2 × 5,3 (`fc_dok.mutter`).

| Teil | Muttern |
|---|---|
| y_portalwinkel (beide) | 4× M3 innen an der Sattelrückwand (X-Riemenklemme) |
| x_wagenkoerper | 4× M4 (Motorbock), 6× M5 (Z-Grundplatte), 4× M3 (Spritzschutz), alle seitlich |
| z_kopf | 8× M4 unten (FK10, Motorhalter), 2× M5 von unten in Schlitze (Halter X-Kette) |
| z_mutterblock | 4× M4 hinten |
| ek_einsteckteil links/rechts | je 4× M6 seitlich |
| ek_halter_y | 2× M5 oben (Kettenende), 2× M5 von oben in Schlitze (Turm) |
| ekx_festhalter | 2× M5 unten (Kettenende), 2× M5 von unten (Turm), 2× M5 seitlich im Zapfen |
| ek_leitungsclips | je 2× M5 von oben |
| ekx_halter | 2× M5 oben (Kettenende), 2× M4 von links (Tülle) |
| ekx_stopfen | 2× M5 seitlich |
| ek_stuetzen_kopf | je 2× M5 von unten |
