# Grundrahmen

Stahl-Rechteckrohr 40×40×3, nur gerade Schnitte (keine Gehrungen), alles stumpf verschweißt.
Parametrisch aus `grundrahmen.py` (Parameter oben im Skript):

```
python3 cad/live.py cad/grundrahmen/grundrahmen.py
```

Ist FreeCAD offen (MCP-Addon, Port 9875), wird das offene Dokument live aktualisiert, sonst headless erzeugt. Die FCStd ist generiert: Änderungen gehören ins Skript.

| Datei | Inhalt |
|---|---|
| `grundrahmen.FCStd` | Rahmen + Dummy-Schienen HGR15 + Dummy-Wanne |
| `grundrahmen.step` | Rahmen |
| `zuschnitt.txt` | Zuschnittliste, Masse, Schienengewinde |
| `pruefung.txt` | Maße, Überschneidungen, Durchbiegung |

## Aufbau

- **Oben:** 2 Längsträger über die volle Länge (1320) tragen die HGR15-Schienen. M4-Gewinde direkt in die 3-mm-Oberwand, Teilung 60, 22 Löcher je Schiene. 2 Querträger stumpf dazwischen.
- **Beine:** 4 Eckbeine stumpf unter die Längsträger, Fußplatten 100×100×8 mit Ø13. Vorgesehen sind **Einstellfüße und Rollen**: Im Betrieb heben die Füße den Rahmen über die Rollen an, zum Verfahren werden sie hochgedreht. Die Anbindung beider an den Fußplatten ist noch zu konstruieren.
- **Unten:** Längs- und Querrohre stumpf zwischen die Beine (Unterkante 100 über Boden), dazu 2 Mittelquerrohre als Auflage für den Wannenträger.
- **Wanne:** liegt innen (lichte Weite 640 × 1240 bei Wanne 600 × 1200 und 20 mm Spiel je Seite) und lässt sich an der Stirnseite durch die Öffnung 640 × 670 herausziehen. Der Wannenträger und damit die Wannenhöhe folgen später.

## Randbedingung Breite

Die ganze Maschine darf **höchstens 800 mm breit** sein (Tür 820 mm). Stand Zusammenbau: 736 mm (Rahmen 720, Y-Portalwinkel mit Riemen über der Schiene je 8 mm über). Motoren und Energiekette müssen in den verbleibenden 64 mm bleiben.

## Annahmen (offen)

- Oberkante Rahmen 850 mm (Schienenauflage). Arbeitshöhe Blech ergibt sich später aus Wannenträger und Opferleisten.
- Schienen 1300 lang, mittig. Y-Hub mit Wagensatz 180 mm reicht für 1000 mm plus Endanschläge.
- M4 in 3 mm Wand ergibt gut 4 tragende Gänge. Für die Schienen genügt das, die Rohroberseite sollte aber vor dem Bohren auf Ebenheit geprüft werden (ggf. unterlegen oder Schiene an einer Anschlagkante ausrichten).

## Längsaufteilung (Stand 21.10.2026)

Der Brenner sitzt 136 mm vor der Brückenmitte. Damit die Düse den ganzen Wannenboden (1100 mm) erreicht, liegen die Schienen um diesen Betrag hinter der Wannenmitte: Schienenanfang 70 mm hinter dem Rahmenende (Platz für die Y-Motoren), Wanne nach vorn versetzt. Der Rahmen wird dadurch **1516 mm** lang (Parameter `brenner_versatz`, `platz_hinten`, `platz_vorn`).
