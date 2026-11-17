# Auflage (Kammträger und Auflageleisten)

```
python3 cad/live.py cad/auflage/auflage.py
```

Lose gesteckt, ohne Schrauben im Wasser. Koordinaten wie Wannenkäfig (Wannenmitte, Rahmenoberkante = 0). Prüfwerte in `pruefung.txt`.

- **Kammträger:** 3 Stück Stahlblech 3 mm, 1080 lang, 87 hoch, längs (Y) bei x −200 / 0 / +200 auf dem Wannenboden. Sie kreuzen alle Querrohre des Wannenkäfigs, die Last geht durch den PE-Boden direkt in die Rohre. Oben Schlitze 3,5 × 20 im **Raster 25 mm** (43 Positionen). Unten Aussparungen 60 × 15 zwischen den Querrohren für Wasser und Schlamm, beim mittleren Träger auch über dem Ablauf. Enden unten gefast (Rundung Boden/Wand).
- **Schutzleisten** (Stand 17.11.2026): 2 Stück Stahlblech 3 mm, 1080 lang, 115 hoch, längs (Y) innen vor dem Bördel der Längswände (Außenfläche x ±268, Bördel innen ±270), lose auf dem Wannenboden, seitlich gehalten von Bördel und Leistenenden. Unten 4 Aussparungen 60 × 15 für Wasser und Schlamm, Enden unten gefast. Grund: Der PE-Bördel liegt über dem Wasser und nur 1 mm unter dem Blech; am Rand treffen Strahl und Schlacke so Stahl statt PE.
- **Softlimit Schneidbereich X: Düse ±260 um die Wannenmitte (520 breit statt 550).** Direkt über dem Bördel darf nie geschnitten werden; die Schutzleisten fangen nur Spritzer. Y bleibt ±550 (Bördel 18 mm entfernt, an den Stirnseiten kein Schutz).
- **Auflageleisten:** Flachstahl 50 × 3, 524 lang, quer (X), 3 mm Luft zu den Schutzleisten. Normal **jede zweite Position (Teilung 50, 22 Stück)**, für kleine Teile dichter (bis 43 Stück). Oberkante = Rahmenoberkante = Blechunterseite, 1 mm über dem Bördel. Bis auf die obersten 15 mm im Wasser.
- Einbau von oben durch die Bördelöffnung 540 × 1137: erst Kammträger und Schutzleisten, dann die Leisten (Kammträger 28 mm Luft je Ende). Die Leisten halten die Kammträger aufrecht, seitlich begrenzt der Bördel.
- Erster Satz: Leisten aus Flachstahl 50 × 3 (Handel), Kammträger extern lasern oder von Hand schlitzen. Danach schneidet die Maschine ihre Ersatzteile selbst (`kammtraeger.step`, `auflageleiste.step`).
- Wasser 15 mm unter der Blechunterseite (üblich 0–25 mm).
