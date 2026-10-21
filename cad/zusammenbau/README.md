# Zusammenbau

Rahmen, Wanne und Portal (beide Y-Portalwinkel mit Wagen, Flachstange, Druckteilen) als Verknüpfungen auf die Einzelteil-Dokumente, dazu die Portalbrücke 80×40×4 in voller Länge.

```
python3 cad/live.py cad/zusammenbau/zusammenbau.py
```

Ändert sich ein Einzelteil, zieht der Zusammenbau automatisch nach. Lage und Maße kommen aus der Geometrie der Einzelteile. Einstellbar oben im Skript: Portalposition in Y, Höhe der Wanne (bis der Wannenträger steht). Prüfwerte (Gesamtbreite gegen 800 mm, Y-Hub, Kollisionen) in `pruefung.txt`.
