# Z-Achse

```
python3 cad/live.py cad/z_achse/z_achse.py
```

- Kugelumlaufspindel **SFU1204**, Festlager FK10 oben, unteres Ende frei. Motor NEMA23 kompakt (1,2 Nm) oben über Kupplung Ø25 × 30.
- Z-Grundplatte Alu 12 mm, oben 104 breit, unterhalb z 50 nur 60 breit (läuft an den Sätteln vorbei), reicht bis zur Unterkante des X-Wagenkörpers. 6× M5 in Muttern der Front, damit trägt sie die Biegung zwischen oberem und unterem Wagen.
- Zwei Distanzleisten Alu 20 × 20 × 220, darauf HGR15 (Abstand 80). Die Leisten schaffen Platz für den Mutterflansch Ø42 zwischen Grundplatte und Schlitten; die Schienenschrauben M4 gehen durch die Leisten in die Grundplatte.
- Z-Schlitten Alu 120 × 100 × 12 (gleiche Platte wie die Grundplatte; Rückenplatte des Schwimmkopf-Halters dafür 6 statt 8) auf zwei HGH15CA. Mutterblock (Druck) hinten, die Mutter hängt unter dem Steg.
- Z-Kopf (Druck) auf Grundplatte und Leisten: Sockel mit FK10, zwei Säulen, Motorplatte; die Kupplung ist von vorn und hinten zugänglich.
- Brenner SP80M aufgemessen (02.11.2026, `kaufteile.brenner_sp80m`): 510 lang; Überwurfmutter 38 (Ø19–30,5), Kunststoffabdeckung Ø34,6 bis 135, **Verbundrohr Ø35 von 135 bis 375 (nur hier spannen)**, Knickschutztülle bis 510 (größte Stelle SW36), Schlauchpaket Ø20 / flach 35 × 10, Biegeradius gut 120, minimal 100. Angenommen: Düsenform, Lage des Sechskants an der Tülle.
- Schwimmkopf **vor dem Schlitten**, Halter zweiteilig (Druck):
  - **Halter unten** (seitlich liegend gedruckt, Rücken unten): Rückenplatte (3× M5 gesenkt in den Schlitten, die mittlere durch bis in eine Freibohrung im Mutterblock) und unterer Steg mit zwei Sacklöchern 13 tief (Ø7,9, Stäbe eingepresst).
  - **Halter oben** (flach, Oberseite unten gedruckt): oberer Steg, liegt auf der Rückenplatte, nach hinten über die Schlitten-Oberkante verlängert und dort mit 2× M5 gesenkt von oben in Gewinde im Schlitten (9 tief). Zwei Sacklöcher Ø8 13 tief: Die Stäbe werden beim Aufschrauben eingefangen.
  - Stäbe: Präzisionswelle Ø8 h6 × 100, 1 mm Längsspiel in den Sacklöchern.
- Dazwischen gleitet der Brennerträger (70 hoch, hintere Klemmschale) mit Klemmdeckel, 4× M4 in Muttern (von oben/unten eingeschoben), 0,5 mm Klemmspalt. Der Träger klemmt 140–210 mm über der Düse auf dem Rohr, liegt auf dem unteren Steg und hat 5 mm Weg bis zum oberen Steg. Stabbohrungen im Träger Ø7,8 gedruckt, **auf 8 aufreiben**. Seitlich je ein Butzen (7 mm, unten 45°) mit **Kegelschmiernippel M6 (DIN 71412, SW7)** auf halber Trägerhöhe: Kernloch Ø5 bis in die Stabbohrung, M6 durchschneiden.
- **Schalter Schwimmkopf:** induktiv **LJ12A3-4-Z/AY** (wie die Referenzschalter: M12, PNP, Öffner, 4 mm auf Stahl), senkrecht im oberen Steg bei x 25 / y 151 (rechts vorn neben dem Brenner). Mutter M12 oben im Steg eingepresst, Kontermutter darauf; Sensorfläche 0,5 mm über der Unterseite des Stegs (über das Gewinde einstellbar). Ziel: Zylinderstift 6 × 10 (Stahl) oben im Klemmdeckel. Der Schalter öffnet nach etwa 1–2 mm Hub, der Rest bis zum Anschlag (5 mm) bleibt als Überweg.
- Montage: Halter unten an den Schlitten, Stäbe in die Sacklöcher einpressen, Träger aufschieben (Bohrungen vorher aufgerieben, Nippel eingeschraubt), Halter oben auf die Stäbe setzen und mit 2× M5 in die Schlitten-Oberkante schrauben, Schalter mit Muttern einsetzen, Brenner einlegen, Deckel spannen.
- Hub 100 mm. Düse von 65 mm unter bis 35 mm über der Brückenunterkante (Rahmenoberkante = 57 mm unter der Brücke). Brennerachse 136 mm vor der Brückenmitte.
- Breite Teile liegen alle über der Brückenunterkante + 50 mm; darunter nur der Brenner (an den X-Enden stehen dort die Türme der Y-Winkel).

- Die X-Wagen HGH15CA mit Metallabstreifer bestellen (HIWIN-Dichtungsoption, Kennung im Katalog prüfen).

Offen: genaue Maße FK10 (Lochbild). Schaltabstand auf den Stift 6 mm am Gerät prüfen (Nennwert gilt für 12 × 12 Stahl).
