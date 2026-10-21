# Wannenkäfig

```
python3 cad/live.py cad/wannenkaefig/wannenkaefig.py
```

Stahl-Rechteckrohr 20 × 20 × 2, nur gerade Schnitte, stumpf verschweißt (`zuschnitt.txt`, ca. 11,5 m, 13 kg).

- Oberer Ring 640 × 1235, Oberkante = Rahmenoberkante, liegt innen an den Längsträgern an; 3× M8 je Seite quer durch Ring und Längsträger.
- Unterer Rahmen gleicher Größe, sechs Querrohre unter dem Wannenboden (y ±110, ±330, ±550 ab Wannenmitte), sechs Pfosten.
- Mitte frei für den Ablauf (zwischen den Querrohren bei ±110).
- Höhe: Wanne steht 120 mm unter Rahmenoberkante. Opferleisten 1 mm über dem Bördel (Blechunterseite = Rahmenoberkante), Wasser bis 105 mm über Boden = 15 mm unter dem Blech. Die Leistenträger stehen im Wasser auf dem Wannenboden direkt über den Querrohren.
- Hinweis: Z ganz unten liegt die Düse 8 mm unter dem Blech und damit tiefer als der Bördel. An den X-Enden würde der Brenner dort den Bördel treffen; Z-Untergrenze in LinuxCNC auf etwa 3 mm unter Blechunterseite begrenzen.
