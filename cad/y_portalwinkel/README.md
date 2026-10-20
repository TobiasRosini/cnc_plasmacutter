# Y-Portalwinkel

Verbindet die Portalbrücke (Alu 20×40×4, 40 hoch stehend) mit den zwei HGH15-Wagen einer Y-Schiene.
Je Seite ein Satz: Alu-Flachstange 40×15 + 3D-gedruckter Winkel.

Alles wird parametrisch aus `y_portalwinkel.py` erzeugt (Parameter oben im Skript):

```
python3 cad/live.py cad/y_portalwinkel/y_portalwinkel.py
```

Ist FreeCAD offen (MCP-Addon, Port 9875), wird das offene Dokument live aktualisiert, sonst headless erzeugt. Die FCStd ist generiert: Änderungen gehören ins Skript.

| Datei | Inhalt |
|---|---|
| `y_portalwinkel.FCStd` | Baugruppe inkl. Dummy-Schiene, -Wagen, -Brücke, -Riemen |
| `winkel_druckteil.step/.stl` | Winkel (Druck), Unterseite aufs Bett |
| `spannschlitten.step/.stl` | Spannschlitten für die Schwalbenschwanznut, Unterseite aufs Bett |
| `klemmplatte_fest.step/.stl`, `klemmplatte_schlitten.step/.stl` | Riemenklemmplatten |
| `flachstange_40x15.step` | Alu-Flachstange |
| `flachstange_bohrschablone_1zu1.svg` | Anreißschablone A4 quer, 1:1 drucken |
| `pruefung.txt` | Gültigkeit, Bauraum, Kollisionsprüfung |

## Festlegungen und Annahmen

- Wagen **HGH15CA** (bestätigt): 34 breit, 61,4 lang, Lochbild 26×26, 4× M4, Gewindetiefe 5 mm.
- Brücke **hochkant** (bestätigt), im Sattel mit 2× **M6×40** quer (Kopf-Senkung −Y, Muttertasche +Y).
- Wagenabstand 110 mm Mitte–Mitte, Flachstange 180 mm lang.
- Flachstange: 8× Ø4,5 mit Senkung Ø8×7,5 für ISO 4762 **M4×12** (4,5 mm Einschraubtiefe, steht nicht über), 8× M5-Gewinde 12 tief.
- Winkel: Basis 14 mm, Mittelrippe beidseitig, Zugangslöcher Ø9 über den M4-Schrauben, 8× **M5×18** in die Flachstange.

## Riemen HTD5M/15 (flach, Zähne unten, Rücktrum läuft unter dem Wagen zurück)

- Riemenkanal 15,6 × 1,0 mm außen auf dem Flansch (Riemenmitte 45 mm neben Schienenmitte). Der Riemenrücken steht 0,7 mm über, die Klemmplatten pressen ihn.
- **Festes Ende (−Y):** HTD5M-Zahnlücken eingeprägt, Klemmplatte mit 4× **M5×20**, Muttern in Taschen von unten.
- **Spannende (+Y):** Schwalbenschwanznut 60°, 32 mm oben, 7 mm tief, nach außen offen. Reicht der Spannweg nicht, den Schlitten zahnweise versetzt neu einschieben. Im Spannschlitten ebenfalls Zahnlücken, Klemmplatte mit 4× **M4×12**, Muttern unten im Schlitten. Spannschraube **M5×45 auf Zug**: Kopf am Widerlager innen auf dem Flansch, Mutter in der Lasche der Schlitten-Klemmplatte. Spannweg 20 mm (Parameter `spannweg`).
- Zahnlückenform vereinfacht (Breite 3,3, Tiefe 2,2, runder Grund). Vor dem Druck mit einem Riemenstück abgleichen.

## Energiekette

- Senkrechter Befestigungsflansch außen (8 mm dick, 30 mm hoch, y −45…−5) mit 4× M5 waagerecht (Lochbild 20 × 12 mm), Muttertaschen innen. Der Kettenhalter wird ein eigenes Teil.
- Der Flansch sitzt an jedem Winkel, damit links und rechts dasselbe Teil passt (um 180° gedreht). Abschaltbar mit `ek_flansch=False`.
