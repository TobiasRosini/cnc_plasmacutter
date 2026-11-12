# CAD

FreeCAD-Modelle des Plasmatisches (Rahmen, Portal, Brennerwagen, Z-Achse).

## Teilenummern

`python3 cad/live.py cad/teilenummern.py` (nach dem Zusammenbau) nummeriert alle Teile:
gleiche Teile gleiche Nummer, Spiegelteile eigene Nummer, Kaufteile nach Bezeichnung und
Außenmaßen. Ergebnis in `cad/stueckliste.md`, die Nummer steht außerdem vorn in der
Beschriftung im Zusammenbau. Vergebene Nummern bleiben in `cad/teilenummern.json` fest.
