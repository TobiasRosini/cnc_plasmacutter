# CAD

FreeCAD-Modelle des Plasmatisches (Rahmen, Portal, Brennerwagen, Z-Achse).

## Teilenummern

`python3 cad/live.py cad/teilenummern.py` (nach dem Zusammenbau) nummeriert alle Teile:
gleiche Teile gleiche Nummer, Spiegelteile eigene Nummer, Kaufteile nach Bezeichnung und
Außenmaßen. Ergebnis in `cad/stueckliste.md`, die Nummer steht außerdem vorn in der
Beschriftung im Zusammenbau. Vergebene Nummern bleiben in `cad/teilenummern.json` fest.

## Radien an Druckteilen

`fc_dok.verrunden(form, nachbarn, bett)` gibt den freien Außenkanten eines Druckteils eine Formsprache nach der Druckrichtung: senkrechte Kanten (in Druckrichtung) R2 wie Eckradien eines Frästeils, waagerechte Kanten (Oberseite, Überhänge) 1-mm-Fase, die stützenfrei druckt; Kanten am Druckbett bleiben scharf. Bearbeitet wird je Kantenzug mit einem Maß (sonst halbes Maß, dann tangentiale Teilzüge, zuletzt einzeln), damit Rundungen und Fasen durchlaufen statt an Ecken stumpf zu enden. Scharf bleiben Kanten an Flächen, die an einem Nachbarteil anliegen (saubere Fugen im Zusammenbau), Innenkanten und Ränder von Bohrungen, Muttertaschen und Schlitzen bis 8 mm lichter Weite; keine Rundung darf eine Wand an einer Bohrung unter 3 mm bringen. Bisher angewendet: Druckteile der Energiekette (`sexy()` in `energiekette.py`, Ergebnis je Teil in `pruefung.txt`).
