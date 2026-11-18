# Halbzeuge: Einkauf und Zuschnitt

Erzeugt von `cad/halbzeuge.py` aus der Stückliste (dort ändern, nicht hier). Lagerlängen und Tafelformate sind Annahmen für den Transport im Auto und beim Händler zu prüfen; viele Händler sägen auch direkt nach dem Schnittplan. Rahmen: **Oberrahmen 40 × 40 × 3, Untertisch 40 × 40 × 2**.

## Einkaufsliste

| Halbzeug | Bedarf netto | Bestellen | Masse netto |
|---|---:|---|---:|
| Stahl-Rechteckrohr 40 × 40 × 3 | 3.75 m | 2 × 3000 mm | 13.1 kg |
| Stahl-Rechteckrohr 40 × 40 × 2 | 12.64 m | 5 × 3000 mm | 30.2 kg |
| Stahl-Rechteckrohr 80 × 40 × 4 | 0.64 m | 1 × 1000 mm | 4.5 kg |
| Stahl-Rechteckrohr 40 × 20 × 2 | 1.63 m | 1 × 3000 mm | 2.9 kg |
| Stahl-Vierkantrohr 20 × 20 × 2 | 11.30 m | 5 × 3000 mm | 12.8 kg |
| Flachstahl 50 × 3 | 14.71 m | 6 × 3000 mm | 17.3 kg |
| Gewindestange M16 | 0.80 m | 1 × 1000 mm | 1.0 kg |
| Alu-Rechteckrohr 80 × 40 × 4 | 0.90 m | 1 × 1000 mm | 2.2 kg |
| Alu-Rechteckrohr 40 × 20 × 2 | 0.75 m | 1 × 1000 mm | 0.5 kg |
| Alu-Flachstange 40 × 15 | 0.36 m | 1 × 500 mm | 0.6 kg |
| Alu-Flachstange 40 × 8 | 1.45 m | 1 × 2000 mm | 1.3 kg |
| Alu-Vierkant 20 × 20 | 0.44 m | 1 × 500 mm | 0.5 kg |
| Alu-U-Profil 20 × 60 × 20 × 2 | 1.39 m | 1 × 2000 mm | 0.7 kg |
| PVC-Kabelkanal 40 × 40 | 0.58 m | 1 × 2000 mm | – |
| PVC-Kabelkanal 25 × 60 | 0.56 m | 1 × 2000 mm | – |
| Stahlblech 3 | 0.53 m² | 1 × 1250 × 625 mm | 12.6 kg |
| Stahlblech 1 | 0.00 m² | 1 × 100 × 100 mm | 0.0 kg |
| Stahlplatte 10 | 0.12 m² | 1 × 400 × 400 mm | 9.6 kg |
| Alu-Platte 12 | 0.04 m² | 1 × 500 × 150 mm | 1.4 kg |
| Alu-Blech 0,5 | 1.82 m² | 1 × 2000 × 1250 mm | 2.5 kg |
| Siebdruckplatte 9 | 0.74 m² | Zuschnitt auf Maß | 4.5 kg |

Masse netto: Stahl 104 kg, Alu 10 kg.

## Zuschnitt

### Stahl-Rechteckrohr 40 × 40 × 3

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| OR_Laengstraeger_L | 1556 | 1 |  |
| OR_Laengstraeger_R | 1556 | 1 |  |
| OR_Quertraeger_V | 640 | 1 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 1556 + 640, Rest 798
- Stange 2: 1556, Rest 1441

### Stahl-Rechteckrohr 40 × 40 × 2

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| UT_Laengsrohr_oben_L | 1436 | 1 |  |
| UT_Laengsrohr_unten | 1436 | 2 |  |
| UT_Laengsrohr_oben_R | 1436 | 1 |  |
| UT_Bein | 710 | 2 |  |
| UT_Bein_3 | 710 | 1 |  |
| UT_Bein_4 | 710 | 1 |  |
| UT_Querrohr_oben_H | 640 | 1 |  |
| UT_Querrohr_unten | 640 | 4 |  |
| UT_Querrohr_oben_V | 640 | 1 |  |
| ek_stuetzen_220 | 220 | 1 | vordere Kettenstütze |

Schnittplan (Schnitt 3 mm):

- Stange 1: 1436 + 1436, Rest 122
- Stange 2: 1436 + 1436, Rest 122
- Stange 3: 710 + 710 + 710 + 710, Rest 148
- Stange 4: 640 + 640 + 640 + 640 + 220, Rest 205
- Stange 5: 640 + 640, Rest 1714

### Stahl-Rechteckrohr 80 × 40 × 4

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| OR_Quertraeger_H | 640 | 1 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 640, Rest 357

### Stahl-Rechteckrohr 40 × 20 × 2

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| ek_traeger_40x20 | 1445 | 1 |  |
| ek_stuetzen_188 | 188 | 1 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 1445 + 188, Rest 1361

### Stahl-Vierkantrohr 20 × 20 × 2

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| Wannenkäfig: Ring oben längs | 1235 | 2 |  |
| Wannenkäfig: Rahmen unten längs | 1235 | 2 |  |
| Wannenkäfig: Ring oben quer | 600 | 2 |  |
| Wannenkäfig: Rahmen unten quer | 600 | 2 |  |
| Wannenkäfig: Querrohr Boden | 600 | 6 |  |
| Wannenkäfig: Pfosten | 60 | 6 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 1235 + 1235 + 60 + 60 + 60 + 60 + 60 + 60, Rest 146
- Stange 2: 1235 + 1235, Rest 524
- Stange 3: 600 + 600 + 600 + 600, Rest 588
- Stange 4: 600 + 600 + 600 + 600, Rest 588
- Stange 5: 600 + 600, Rest 1794

### Flachstahl 50 × 3

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| OR_Spritzschutz | 1280 | 2 |  |
| x_schutzstreifen | 620 | 1 |  |
| auflageleiste | 524 | 22 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 1280 + 1280, Rest 434
- Stange 2: 620 + 524 + 524 + 524 + 524, Rest 269
- Stange 3: 524 + 524 + 524 + 524 + 524, Rest 365
- Stange 4: 524 + 524 + 524 + 524 + 524, Rest 365
- Stange 5: 524 + 524 + 524 + 524 + 524, Rest 365
- Stange 6: 524 + 524 + 524, Rest 1419

### Gewindestange M16

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| UT_Stellfuss_M16 | 200 | 4 | unten Mutter M16 aufschweißen |

Schnittplan (Schnitt 3 mm):

- Stange 1: 200 + 200 + 200 + 200, Rest 188

### Alu-Rechteckrohr 80 × 40 × 4

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| Portalbruecke_80x40x4 | 769 | 1 |  |
| x_schutz_halter | 65 | 2 | aus der Wand des Reststücks |

Schnittplan (Schnitt 3 mm):

- Stange 1: 769 + 65 + 65, Rest 92

### Alu-Rechteckrohr 40 × 20 × 2

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| ekx_traeger_40x20 | 754 | 1 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 754, Rest 243

### Alu-Flachstange 40 × 15

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| flachstange_40x15 | 180 | 2 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 180 + 180, Rest 134

### Alu-Flachstange 40 × 8

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| ekx_rinne_hinten | 477 | 1 |  |
| ek_ausleger | 433 | 1 |  |
| ekx_mast | 356 | 1 |  |
| ekx_stuetze_links | 188 | 1 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 477 + 433 + 356 + 188, Rest 534

### Alu-Vierkant 20 × 20

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| z_leisten_20x20 | 220 | 2 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 220 + 220, Rest 54

### Alu-U-Profil 20 × 60 × 20 × 2

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| ek_rinne | 863 | 1 |  |
| ekx_rinne | 530 | 1 |  |

Schnittplan (Schnitt 3 mm):

- Stange 1: 863 + 530, Rest 601

### PVC-Kabelkanal 40 × 40

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| ek_kabelkanal | 582 | 1 | mit Deckel |

Schnittplan (Schnitt 3 mm):

- Stange 1: 582, Rest 1415

### PVC-Kabelkanal 25 × 60

| Teil | Länge mm | Stk | Bemerkung |
|---|---:|---:|---|
| ub_kabelkanal_quer | 305 | 1 | mit Deckel |
| ub_kabelkanal_senkrecht | 250 | 1 | mit Deckel |

Schnittplan (Schnitt 3 mm):

- Stange 1: 305 + 250, Rest 1439

### Stahlblech 3

| Teil | Zuschnitt mm | Stk | Bemerkung |
|---|---:|---:|---|
| kammtraeger | 1080 × 87 | 3 | lasern oder von Hand schneiden |
| schutzleiste | 1080 × 115 | 2 | lasern oder von Hand schneiden |
| y_ref_fahne | 61 × 32 | 1 | abgekantet, Zuschnitt ungefähr |
| y_ref_fahne_rechts | 61 × 32 | 1 | abgekantet, Zuschnitt ungefähr |
| z_ref_fahne | 24 × 20 | 1 |  |

### Stahlblech 1

| Teil | Zuschnitt mm | Stk | Bemerkung |
|---|---:|---:|---|
| x_spritzschutz | 69 × 60 | 1 |  |

### Stahlplatte 10

| Teil | Zuschnitt mm | Stk | Bemerkung |
|---|---:|---:|---|
| UT_Eckplatte | 175 × 175 | 4 |  |

### Alu-Platte 12

| Teil | Zuschnitt mm | Stk | Bemerkung |
|---|---:|---:|---|
| z_grundplatte | 308 × 104 | 1 |  |
| z_schlitten | 120 × 100 | 1 |  |

### Alu-Blech 0,5

| Teil | Zuschnitt mm | Stk | Bemerkung |
|---|---:|---:|---|
| ub_haube | 1766 × 1031 | 1 | Abwicklung, gekantet |

### Siebdruckplatte 9

| Teil | Zuschnitt mm | Stk | Bemerkung |
|---|---:|---:|---|
| ub_geraeteboden | 1031 × 720 | 1 |  |
