# Unterbau

```
python3 cad/live.py cad/unterbau/unterbau.py
```

Alles unter der Wanne. Koordinaten wie Grundrahmen (Seiten von vorn gesehen, vorn = großes y). Prüfwerte in `pruefung.txt`.

- **Geräteboden:** Siebdruckplatte 9 mm auf den unteren Längsrohren, vom ersten Mittelquerrohr bis vorn (y 485–1516), an den vorderen Beinen ausgespart. Liegt auf beiden Mittelquerrohren und dem vorderen Querrohr auf (größte freie Spannweite 465 mm in y). 6× M6 von oben in Nietmuttern in den unteren Längsrohren (y 560 / 1050 / 1420, `grundrahmen geraeteboden_y`). Oberkante 149 über Boden.
- **Plasmagerät** SPARTUS XPro CUT 70CNC (515 × 215 × 370) rechts, Front nach vorn, **250 mm hinter der Schrankfront** (y 735–1250): Das Schlauchpaket kommt vorn heraus und hat einen langen Stecker. Die Druckluft-Einheit hinten am Gerät ist von rechts und von oben erreichbar: über dem Geräteboden sind dort 515 mm frei (gefordert 500).
- **Schaltschrank** 400 × 500 × 200 vorn links (Front y 1500, 15 mm neben dem Gerät), Tür nach vorn. Inhalt: Mini-PC (190 × 190 × 45), Mesa 7i96S (150 × 100 × 40), 4 Schrittmotortreiber, Schaltnetzteil 48 V, 24-V-Versorgung, Reihenklemmen, Not-Aus und Schütz. Alle Leitungen kommen oben rechts durch die Seitenwand, laufen innen an der Oberkante entlang und gehen von dort auf die Reihenklemmen.
- **Tropfboden:** Alu-Blech 1,5 mm unter dem Wannenkäfig zwischen den Beinen, Gefälle 3,3 % nach hinten (Oberseite vorn 690, hinten 640), Ränder seitlich und vorn 15 hoch, hinten 20 mm über den Rahmen hinaus mit Tropfkante. Der Wannenablauf geht durch eine Hülse Ø44 (20 hoch). Unter dem Käfig bleiben vorn 5 mm Luft. Befestigung noch offen (z. B. Gewindestangen M6 an den Längsrohren des Käfigs).
- **Kabelweg:** Kabelkanal 40 × 40 auf dem Y-Kettenträger vom festen Kettenende in den **Kanalknoten** (Druck) über der vorderen Kettenstütze. Von dort in den senkrechten Kanal außen rechts (x −65 bis −40, y 1416–1476, z 650–900) auf der Stütze, über den **Bogen unten** (Druck, R10/R35) in den Querkanal (z 615–640) direkt hinter dem Bein und in die **obere rechte Ecke** des Schaltschranks (Oberkante Kanal 9 mm unter der Schrankoberkante). Senkrechter und Querkanal sind derselbe Typ: PVC 25 × 60 mit Deckel (senkrecht Deckel außen, quer Deckel unten); an alle Leitungen kommt man über die Kanaldeckel. Vor dem Gerät bleiben 250 mm bis zur Schrankfront; das Schlauchpaket verlässt den Querkanal nach unten und geht dort in den Brenneranschluss.
- **Kanalknoten** (`ub_kanalknoten`, Druck, Wand 3,2, geschlossen): Hier stoßen Y-Träger mit Kanal, senkrechter Kanal und vordere Kettenstütze zusammen.
  - Träger und Kanal 40 × 40 darauf stecken gemeinsam (40 × 60) 25 mm tief von hinten in einer Muffe; beide enden bei y 1437,25. 2× M5 von innen (x > 0, über dem Umlenkhalter Y frei zugänglich) durch die Knotenwand in Nietmuttern in der Innenseite des Trägers.
  - Der senkrechte Kanal steckt von unten 15 mm in einer dreiseitigen Muffe (innen liegt er an der Stütze).
  - Der Knoten sitzt auf der Stütze (Oberkante z 900), die Vorderwand reicht als Schürze 30 mm über die Stütze: 2× M5 von vorn in Nietmuttern in der Vorderwand der Stütze. Ersetzt den vorderen Stützkopf.
  - Innen laufen die Leitungen über dem Trägerende zur Seite und senkrecht hinunter.
  - Druck auf der Vorderseite liegend (y nach oben, Höhe 67 mm): größte Brücke 40 mm über dem Leitungsraum, keine Stützen.
- **Bogen unten** (`ub_uebergang_unten`, Druck, Wand 3,2): Viertelring wie der Kanalquerschnitt, die Kanalenden stecken 15 mm tief in Muffen (0,25 Spiel je Seite). Offen nach hinten mit flachem Deckel (`ub_uebergang_unten_deckel`, 2× M3 in seitlich eingeschobenen Muttern). Druck auf der Vorderseite liegend, alle Wände senkrecht.
- **Vordere Kettenstütze** (`cad/energiekette/`): Rechteckrohr 40 × 40 × 2 direkt hinter dem vorderen Bein (y 1436–1476), außen am Längsträger des Oberrahmens und am oberen Längsrohr des Untertischs (je 2× M6 in Nietmuttern), von z 680 (15 mm über der Muffe des Bogens) bis z 900 (darauf der Kanalknoten).
- **Befestigung der Kanäle** ohne Distanzstücke, je 2× M5 von innen aus dem Kanal in Nietmuttern M5: senkrechter Kanal auf der Stütze (z 720 und 860), Querkanal an der Rückseite des vorderen rechten Beins (z 627,5). Der Querkanal ist außerdem am Schaltschrank befestigt (Kabeleinführung). Die Rückwand des senkrechten Kanals hat 4 Durchgriffe Ø13 zu den M6 der Stütze: Bei offenem Deckel lässt sich die Stütze lösen, ohne den Kanal abzunehmen.
- Gesamtbreite: 793 mm (Portal); Kanal, Knoten und Bogen reichen bis x −68,45, also höchstens 796 mm (Grenze 800).
