# CAD

FreeCAD-Modelle des Plasmatisches (Rahmen, Portal, Brennerwagen, Z-Achse).

## Teilenummern

`python3 cad/live.py cad/teilenummern.py` (nach dem Zusammenbau) nummeriert alle Teile:
gleiche Teile gleiche Nummer, Spiegelteile eigene Nummer, Kaufteile nach Bezeichnung und
Außenmaßen. Ergebnis in `cad/stueckliste.md`, die Nummer steht außerdem vorn in der
Beschriftung im Zusammenbau. Vergebene Nummern bleiben in `cad/teilenummern.json` fest.

## Radien an Druckteilen

`fc_dok.verrunden(form, nachbarn, bett)` rundet die freien Außenkanten eines Druckteils (R2, wo nötig R1 oder R0,5). Scharf bleiben Kanten an Flächen, die an einem Nachbarteil anliegen (saubere Fugen im Zusammenbau), an der Druckbett-Seite, Innenkanten und Ränder von Bohrungen, Muttertaschen, Schlitzen und Tunneln; keine Rundung darf eine Wand an einer Bohrung unter 3 mm bringen. Bisher angewendet: Druckteile der Energiekette (`sexy()` in `energiekette.py`, Ergebnis je Teil in `pruefung.txt`).
