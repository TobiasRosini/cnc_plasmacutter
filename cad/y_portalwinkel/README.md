# Y-Portalwinkel

Verbindet die Portalbrücke (Alu-Rechteckrohr 80×40×4, 80 hoch, 40 tief) mit den zwei HGH15-Wagen einer Y-Schiene.
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
- Brücke 80×40×4 hochkant im Sattel, 4× **M6×60** quer (Kopf-Senkung −Y, Muttertasche +Y).
- Wagenabstand 110 mm Mitte–Mitte, Flachstange 180 mm lang.
- Flachstange: 8× Ø4,5 mit Senkung Ø8×7,5 für ISO 4762 **M4×12** (4,5 mm Einschraubtiefe, steht nicht über), 8× M5-Gewinde 12 tief.
- Winkel: Basis 14 mm, Türme 48 mm breit (je 4 mm über die Flachstange), Kettenlasche außen; gesamt 52 mm quer. Zugangslöcher Ø9 über den M4-Schrauben.

## Riemen HTD5M/15 über der Schienenmitte

- **Obertrum** mit Zähnen nach unten, Kanal 15,6 × 1,0 mm auf zwei Türmen an den Enden (Kanalboden 57 mm über Unterseite Flachstange = Rücktrum + Teilkreis der 24er-Scheibe). Der Riemenrücken steht 0,7 mm über, die Klemmplatten pressen ihn.
- **Rücktrum** läuft durch einen Tunnel 16,4 × 9 mm unten im Winkel, 2 mm über der Flachstange.
- **Festes Ende (−Y):** HTD5M-Zahnlücken eingeprägt, Klemmplatte mit 4× **M5×60** durch Turm und Basis direkt in die Flachstange.
- **Spannende (+Y):** Schwalbenschwanznut 60°, 30,6 mm oben, 7 mm tief, nach außen offen. Reicht der Spannweg nicht, den Schlitten zahnweise versetzt neu einschieben. Spannschlitten 30 mm lang mit Zahnlücken, Klemmplatte mit 4× **M4×12** (Muttern unten im Schlitten). Spannschraube **M5×45 Sechskant (DIN 933)** auf Zug: Der Kopf liegt verdrehsicher in einer Tasche im Widerlager direkt am Sattel (von oben eingelegt), gespannt wird mit der Mutter vor der Lasche der Klemmplatte. Spannweg 20 mm.
- Zahnlückenform vereinfacht (Breite 3,3, Tiefe 2,2, runder Grund). Vor dem Druck mit einem Riemenstück abgleichen.
- Basis zur Flachstange: 2× M5×18 auf der festen Seite (gesenkt), 2× **M5×55** von der Turmoberkante auf der Spannseite.

## Varianten und X-Riemen

- **winkel_fest** (rechts) und **winkel_kasten** (links, gespiegelt gedruckt). Beide Y-Spannseiten zeigen nach vorn (+Y).
- X-Riemen (Omega auf dem X-Wagen) hinten an beiden Sätteln: Zahnprofil in der Sattelrückwand, flache **x_klemmplatte** mit 4× M4 in Gewindeeinsätze (je Seite eine, links gespiegelt).
- Kastenseite: Lasche für die Y-Energiekette außen, 2× M4-Einsätze hinten für die X-Energiekette. Der Anschlusskasten selbst ist noch offen.

## Energiekette

- Senkrechter Befestigungsflansch außen an der Basis (8 mm dick, 30 mm über Basis, y −45…−5) mit 4× M5 waagerecht (Lochbild 20 × 12 mm), Muttertaschen innen. Der Kettenhalter wird ein eigenes Teil.
- Der Flansch sitzt an jedem Winkel, damit links und rechts dasselbe Teil passt (um 180° gedreht). Abschaltbar mit `ek_flansch=False`.

## Stand 20.10.2026 abends

- Basis zur Flachstange: 4× **M4×18** im Sattelboden (Senkung Ø7,5), Gewinde M4 in der Flachstange. Keine Zugangslöcher mehr zu den Wagenschrauben: erst Flachstange auf die Wagen, dann den Winkel aufsetzen.
- Türme 52 mm breit, Schwalbenschwanz 36 mm oben; Klemmplatte des Spannschlittens mit 4× **M3** (Muttern unten im Schlitten).
- X-Riemenklemme: 4 Zahnlücken mittig in der Sattelrückwand, Klemmplatte 40 × 36 mit 4× **M3** in Gewindeeinsätze.
- M6 durch Sattel und Brücke bei x ±11,5; Mittelrippe 5 mm.
- Alle Druckteile werden auf Wandstärke an Bohrungen geprüft (mindestens 3 mm, `pruefung.txt`).
