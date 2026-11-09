# Zusammenbau

Rahmen, Wanne und Portal (beide Y-Portalwinkel mit Wagen, Flachstange, Druckteilen) als Verknüpfungen auf die Einzelteil-Dokumente, dazu die Portalbrücke 80×40×4 in voller Länge.

```
python3 cad/live.py cad/zusammenbau/zusammenbau.py
```

Ändert sich ein Einzelteil, zieht der Zusammenbau automatisch nach. Lage und Maße kommen aus der Geometrie der Einzelteile. Einstellbar oben im Skript: Portalposition in Y, Höhe der Wanne (bis der Wannenträger steht). Prüfwerte (Gesamtbreite gegen 800 mm, Y-Hub, Kollisionen) in `pruefung.txt`.

**Lage in FreeCAD:** Alle Baugruppen liegen im Container `Maschine`, der die Darstellung um 180° um Z dreht. In FreeCAD ist damit die Vorderansicht (Taste 1) vorn und rechts +X. Die Einzelteil-Dokumente, die Skripte, alle Prüfungen und alle Maßangaben in der Doku bleiben in den Skript-Koordinaten (vorn = +Y, rechts = kleines x). Umrechnung beim Messen im Zusammenbau: x_FreeCAD = Rahmenbreite − x, y_FreeCAD = Rahmenlänge − y (Werte in den ersten Zeilen von `pruefung.txt`).
