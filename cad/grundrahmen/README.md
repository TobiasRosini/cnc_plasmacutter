# Grundrahmen

Stahl-Rechteckrohr, nur gerade Schnitte (keine Gehrungen), alles stumpf verschweißt: **Oberrahmen 40×40×3** (trägt Schienen und Portal), **Untertisch komplett 40×40×2** (Stand 18.11.2026).
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
- **Beine:** 4 Eckbeine stumpf unter die Längsträger, unten auf Rahmenunterkante gekürzt (Bein 710).
- **Eckplatten mit Rolle und Stellfuß** (Stand 17.11.2026): je Ecke ein Flachstahl 175 × 175 × 10, außen bündig unter Bein, Längs- und Querrohr geschweißt. Im Betrieb heben die Füße die Rollen vom Boden, zum Verfahren werden sie eingedreht.
  - **Lenkrolle Ø125 mit Bremse** (160 kg, Bauhöhe 150, Rad 36 breit, Platte 100 × 80, Lochbild 80 × 60, Langlöcher 9 × 14; Ausladung 45 angenommen): 4× M8 direkt in die Eckplatte. Lenkachse 122 mm von beiden Außenkanten, also diagonal vom Fuß weg: Der Schwenkkreis (R 109) bleibt 13 mm innerhalb der Außenkanten und 10 mm vom Fußteller entfernt. Radstand 476 × 1272.
  - **Stellfuß (Eigenbau):** Gewindestange M16 × 200 unter der Beinmitte (äußerste Ecke), Gewinde in einer **Schweißmutter M16** oben auf der Eckplatte, also im Bein (vor dem Bein anschweißen). Eingedreht taucht die Stange ins Bein. Unten eine aufgeschweißte Mutter M16 zum Drehen, darunter die Lagerung/der Teller (**offen**, Tobi entscheidet an der Drehmaschine; im Modell Platzhalter Ø50 × 15). Kontermutter M16 flach unter der Platte. Im Betrieb sind 126 mm Stange frei, daher M16.
  - **Höhen:** z = 0 bleibt die Bezugsebene der Koordinaten (100 unter der Rahmenunterkante). Rad unten bei z −60. Betrieb: Boden bei z −72, Räder 12 mm frei, Rahmen-OK **922 mm über Boden**. Verfahren: Füße 22 mm eingedreht, Teller 10 mm frei, Rahmenunterkante 160 über Boden. Alle „über Boden“-Angaben der übrigen Baugruppen meinen z = 0 (+72 im Betrieb).
  - Tragkraft: Maschine im Betrieb grob 240 kg (mit Wasser), verfahren wird ohne Wasser (ca. 160 kg) → 4 × 160 kg reicht reichlich.
- **Spritzschutz Y-Schienen:** Flachstahl 50 × 3 innen an beiden Längsträgern (y 80–1360, zwischen den Y-Haltern), 25 mm über die Rahmenoberkante, je 6 Blindnieten Ø4. Bleche dürfen damit höchstens 634 mm breit sein.
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

## Zwei Baugruppen (Stand 23.10.2026)

- **Oberrahmen:** 2 Längsträger 1556 (mit den Gewinden für die Y-Schienen), Querträger hinten 40 × 40 × 3, **vorn 80 × 40 × 4 flach** (Stand 03.11.2026). Der Oberrahmen steht vorn 40 mm über den Untertisch: Unter dem Überstand greifen Schraubzwingen, so lassen sich Flachstangen auf Querträger und Auflageleisten (gleiche Höhe) zum Schneiden einspannen. Trägt das ganze Portal samt Antrieben, Schaltern und Energieketten.
- **Untertisch:** 4 Beine, Fußplatten, unterer Rahmen mit Mittelquerrohren und ein eigener oberer Rahmen direkt unter dem Oberrahmen. Daran hängt der Wannenkäfig (M8 quer), die Wanne steht darin.
- **Verschraubung:** 6× M8 × 90 senkrecht durch die aufeinanderliegenden Querrohre (je Ende 3 bei x 120 / 360 / 600). Dort liegen weder Schienen noch Halter.
- Zuschnittliste getrennt nach Baugruppe in `zuschnitt.txt`.
