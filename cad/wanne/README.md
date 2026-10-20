# Wanne

PE-Auffangwanne (Schäfer Shop), nach Aufmaß vom 20.10.2026, parametrisch aus `wanne.py`:

```
python3 cad/live.py cad/wanne/wanne.py
```

Ist FreeCAD offen (MCP-Addon, Port 9875), wird das offene Dokument live aktualisiert, sonst headless erzeugt. Die FCStd ist generiert: Änderungen gehören ins Skript.

Erzeugt `wanne.FCStd`, `wanne.step` und `pruefung.txt` (Maße, Wasserinhalt, Spiel im Grundrahmen).

## Aufmaß

- außen über Bördelrand 597 × 1194 × 119
- Bördel Ø25 (Messschieber), kein voller Halbkreis und in Z gestaucht, Unterkante 110 über Standfläche
- lichte Breite innen am Bördel 540
- Boden innen 1100 × 550, Übergang Boden/Wand ca. R8
- Winkel Boden/Wand ca. 97°, Wandstärke ca. 3
- senkrechte Kanten außen R13 (innen R10, Bördelecken konzentrisch)

## Annahmen (offen)

- **Bördel:** Ring 110–119 mit gerundeten Kanten, ringsum 28,5 mm breit (aus 597 − 540). Er steht ca. 18 mm nach innen über die Innenwand, die lichte Öffnung ist also ca. 540 × 1137. Alles, was in die Wanne greift (Opferleistenträger), muss durch diese Öffnung.
- **Stirnwände:** Mit 97° an allen Wänden passen Quer- und Längsmaß nicht zusammen. Modelliert: 97° an den Längswänden, gleicher Bördelüberstand (ca. 7 mm) ringsum, daraus ergeben sich ca. 109° an den Stirnwänden.
