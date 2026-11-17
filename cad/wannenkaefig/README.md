# Wannenkäfig

```
python3 cad/live.py cad/wannenkaefig/wannenkaefig.py
```

Stahl-Rechteckrohr 20 × 20 × 2, nur gerade Schnitte, stumpf verschweißt (`zuschnitt.txt`, ca. 11,5 m, 13 kg).

- Oberer Ring 640 × 1235, Oberkante 40 mm unter Rahmenoberkante, liegt innen am oberen Rahmen des Untertischs an; 3× M8 je Seite quer durch Ring und Längsrohr. Käfig und Wanne gehören damit zum Untertisch.
- Unterer Rahmen gleicher Größe, sechs Querrohre unter dem Wannenboden (y ±110, ±330, ±550 ab Wannenmitte), sechs Pfosten.
- Ablauf 440 mm hinter der Wannenmitte, zwischen den Querrohren bei −330 und −550 (Unterbau: hinter der Haube über dem Geräteraum).
- Höhe: Wanne steht 120 mm unter Rahmenoberkante. Opferleisten 1 mm über dem Bördel (Blechunterseite = Rahmenoberkante), Wasser bis 105 mm über Boden = 15 mm unter dem Blech. Die Kammträger der Auflage laufen längs und kreuzen alle Querrohre (`cad/auflage/`).
- Hinweis: Z ganz unten liegt die Düse 8 mm unter dem Blech und damit tiefer als der Bördel. An den X-Enden würde der Brenner dort den Bördel treffen; Z-Untergrenze in LinuxCNC auf etwa 3 mm unter Blechunterseite begrenzen. Mit dem Softlimit X ±260 (Schutzleisten, `cad/auflage/README.md`) bleibt die Düse ohnehin innerhalb des Bördels.
