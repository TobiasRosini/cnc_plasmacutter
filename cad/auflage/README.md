# Auflage (Kammträger und Auflageleisten)

```
python3 cad/live.py cad/auflage/auflage.py
```

Lose gesteckt, ohne Schrauben im Wasser. Koordinaten wie Wannenkäfig (Wannenmitte, Rahmenoberkante = 0). Prüfwerte in `pruefung.txt`.

- **Kammträger:** 3 Stück Stahlblech 3 mm, 1080 lang, 87 hoch, längs (Y) bei x −200 / 0 / +200 auf dem Wannenboden. Sie kreuzen alle Querrohre des Wannenkäfigs, die Last geht durch den PE-Boden direkt in die Rohre. Oben Schlitze 3,5 × 20 im **Raster 25 mm** (43 Positionen). Unten Aussparungen 60 × 15 zwischen den Querrohren für Wasser und Schlamm, beim mittleren Träger auch über dem Ablauf. Enden unten gefast (Rundung Boden/Wand).
- **Auflageleisten:** Flachstahl 50 × 3, 530 lang, quer (X). Normal **jede zweite Position (Teilung 50, 22 Stück)**, für kleine Teile dichter (bis 43 Stück). Oberkante = Rahmenoberkante = Blechunterseite, 1 mm über dem Bördel. Bis auf die obersten 15 mm im Wasser.
- Einbau von oben durch die Bördelöffnung 540 × 1137 (Leisten 5 mm Luft je Seite, Kammträger 28 mm je Ende). Die Leisten halten die Kammträger aufrecht, seitlich begrenzt der Bördel.
- Erster Satz: Leisten aus Flachstahl 50 × 3 (Handel), Kammträger extern lasern oder von Hand schlitzen. Danach schneidet die Maschine ihre Ersatzteile selbst (`kammtraeger.step`, `auflageleiste.step`).
- Wasser 15 mm unter der Blechunterseite (üblich 0–25 mm).
