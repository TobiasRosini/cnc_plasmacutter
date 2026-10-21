# X-Wagen (Omega-Antrieb)

```
python3 cad/live.py cad/x_wagen/x_wagen.py
```

- Brücke 80×40×4, HGR15 oben und unten, je ein HGH15CA.
- Alu-Platten: Deckplatte 92 × 175 × 10 (über dem oberen Wagen, hinten bis zum Motorbock), Frontplatte 60 × 136 × 12 (vorn, für Z-Achse und Brenner), Bodenplatte 60 × 60 × 10 (unter dem unteren Wagen). Deck- und Bodenplatte mit je 3× M5 in die Stirnkanten der Frontplatte.
- Motorbock (Druck, 84 × 98 × 67) hinten unter der Deckplatte, mit 4× M4 in Gewindeeinsätze an die Deckplatte: NEMA23 kompakt (1,2 Nm, 56 mm) senkrecht und um 45° gedreht, Körper ragt durch die Deckplatte. Darunter Riemenscheibe 24 Z und zwei Umlenkrollen (je 2× 608 auf M8). Die Rolle auf +X sitzt im Langloch (8 mm) und spannt den Riemen.
- X-Riemen HTD5M/15 hochkant 10 mm hinter der Brücke, Zähne zur Brücke, Enden an den Sätteln der Y-Winkel geklemmt.
- X-Weg (Zusammenbau): Wagenmitte 76 bis 644 mm = 568 mm, gefordert 550 (Wannenboden 85 bis 635).

Offen: Z-Achse an der Frontplatte, Anbindung X-Energiekette, Bohrungen der X-Schienen in der Brücke.

- Motor und Riemenscheibe sind als Kaufteile mit Flansch, Zentrierbund, Welle Ø8 mit Abflachung, Befestigungsbohrungen und Kabelaustritt (hinten links) modelliert (`cad/kaufteile.py`).
- Motorbock: Platten nur so groß wie die Befestigungen brauchen (Hülle mit 3,5 mm Rand), schräge Seitenwangen, Fenster in der unteren Platte unter der Riemenscheibe.

Alle Teile werden auf Wandstärke an Bohrungen geprüft (mindestens 3 mm, `pruefung.txt`).
