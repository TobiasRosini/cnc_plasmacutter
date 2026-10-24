# X-Wagen (Omega-Antrieb)

```
python3 cad/live.py cad/x_wagen/x_wagen.py
```

- Brücke 80×40×4, HGR15 oben und unten, je ein HGH15CA.
- Wagenkörper (Druck, ASA) statt drei Alu-Platten: C-Profil durchgehend 60 breit, seitlich liegend ohne Stützen zu drucken. Deck 26 dick (über dem oberen Wagen, endet 33 mm hinter der Brückenmitte; die Rückseite ist die Flanschfläche für den Motorbock, 4× M4-Muttern, seitlich eingeschoben). Hinter der Brücke ist das Deck bis knapp über den Riemen nach unten gezogen (z 72); links bleibt dort Platz für den Referenzschalter, in der Seitenfläche steckt ein Zylinderstift 6 × 10 (Stahl, eingepresst) als Ziel. Gedruckt auf der rechten Seite liegend. Front 14, Boden 10 (Unterseite wie bisher z −38). Die Z-Grundplatte reicht bis unten und trägt die Biegung. Wagenschrauben M4 mit Scheibe.
- Spritzschutz Stahlblech 1 mm unter Boden und Z-Grundplatte, 4× M3×6 in Muttern (seitlich eingeschoben).
- Motorbock (Druck, auf der Flanschfläche liegend gedruckt), von hinten an das Deck geflanscht (4× M4, Senkungen in der Schräge der Stege): von der Seite ein C, vorn die Flanschwand, links und rechts Stege bis zur Oberkante und bis knapp vor den Motor (Mitte frei für den Hebel), außen vorn 45° schräg (Riemenklemmplatten an den Sätteln), nach hinten Motorplatte und untere Platte, außen zwei Seitenwände. Zwischen den Platten bleibt von der Flanschwand nur ein Mittelsteg, links und rechts davon läuft der Riemen um die Rollen. NEMA23 kompakt senkrecht (nicht mehr gedreht), Riemenscheibe 24 Z 44 mm hinter den Rollen. **Gespannt wird über den Motor:** er sitzt in Langlöchern (8 mm Weg in y), die M5-Muttern liegen unten in Langnuten. Zum Spannen einen Hebel zwischen Motor und Flanschwand ansetzen (dort bleiben mindestens 10 mm), dann festziehen. Zwei Umlenkrollen (je 2× 608) auf festen Achsen, nur unten befestigt: M8 von unten, Kopf in der Sechskanttasche, oben Mutter und Scheibe, darüber die Rolle.
- X-Riemen HTD5M/15 hochkant 10 mm hinter der Brücke, Zähne zur Brücke, Enden an den Sätteln der Y-Winkel geklemmt.
- X-Weg (Zusammenbau): Wagenmitte 76 bis 644 mm = 568 mm, gefordert 550 (Wannenboden 85 bis 635).

Offen: Z-Achse an der Frontplatte, Anbindung X-Energiekette, Bohrungen der X-Schienen in der Brücke.

- Motor und Riemenscheibe sind als Kaufteile mit Flansch, Zentrierbund, Welle Ø8 mit Abflachung, Befestigungsbohrungen und Kabelaustritt (hinten links) modelliert (`cad/kaufteile.py`).
- Motorbock: Platten nur so groß wie die Befestigungen brauchen (Hülle mit 3,5 mm Rand), schräge Seitenwangen, Fenster in der unteren Platte unter der Riemenscheibe.

Alle Teile werden auf Wandstärke an Bohrungen geprüft (mindestens 3 mm, `pruefung.txt`).
