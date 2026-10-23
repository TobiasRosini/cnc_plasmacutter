# CNC-Plasmatisch – Projektstand 19.10.2026

## 1. Projektziel und Grundkonzept

Kompakter, möglichst rollbarer CNC-Plasmaschneidtisch für die Werkstatt. Größere Werkstücke können bei Bedarf von Hand geschnitten werden.

| Eigenschaft | Festlegung |
|---|---|
| Verfahrbereich Düse | **1100 × 550 mm** (= Bodenfläche der Wanne innen), Y × X |
| Y-Achse (lange Achse) | Beidseitig angetriebenes Portal auf zwei parallelen Führungen; zwei getrennte Motoren |
| X-Achse (kurze Achse) | Brennerwagen auf dem Portal; ein Motor |
| Portalbrücke | Alu-Rechteckrohr **80 × 40 × 4 mm** (80 hoch, 40 tief), X-Schienen oben und unten |
| Z-Achse | Spindelantrieb mit automatischer Brennerhöhenregelung (THC) |
| Rahmen | Geschweißtes Stahl-Rechteckrohr 40 × 40 × 3, nur gerade Schnitte (keine Gehrungen) |
| **Maximale Gesamtbreite** | **800 mm** über alles (Tür Werkstatt–Garage 820 mm lichte Weite) |
| Aufstellung | Einstellfüße und Rollen: Zum Betrieb wird der Rahmen mit den Füßen über die Rollen angehoben und steht fest; zum Verfahren Füße hochdrehen |
| CAD | **FreeCAD** (statt Fusion 360) |
| Steuerung | LinuxCNC mit QtPlasmaC |
| Motion-Controller | Mesa 7i96S über Ethernet |
| Rechner | Vorhandener Lenovo ThinkCentre M929q (Intel Core i7, 8. Generation) |
| Verfügbare Versorgung | 3 × 400 V, 43 A |

**Achszuordnung festgelegt:** Y ist die lange Portal-Fahrachse (beidseitig angetrieben), X die kurze Querachse des Brennerwagens.

### Verfügbare Fertigungsmöglichkeiten

| Verfahren | Möglichkeit |
|---|---|
| 3D-Druck | Bauraum 200 × 200 × 150 mm |
| Papierdruck | A4, farbig (z. B. Bohr- und Anreißschablonen 1:1) |
| Drehen | Konventionelle Drehmaschine |

Teile sind so zu konstruieren, dass sie mit diesen Mitteln (plus Schweißen des Stahlrahmens) herstellbar sind; größere Druckteile ggf. teilen.

## 2. Plasmaschneidgerät

**Festgelegtes Modell:** SPARTUS XPro CUT 70CNC, vorgesehen mit geradem Maschinenbrenner SP80M. Das Gerät soll auch für manuelle Schnitte genutzt werden können; die Brennervarianten bzw. Lieferumfang sind vor Bestellung zu prüfen.

- 400-V-Gerät mit HF-freier Pilotlichtbogenzündung laut Händlerbeschreibung.
- CNC-Steueranschluss laut zuvor besprochener Handbuchabbildung:
  - Pins 3/4: Start/Stop
  - Pins 5 (−) / 6 (+): geteilte Lichtbogenspannung
  - Pins 12/14: Transfer / Arc OK
- Einstellbarer Spannungsteiler: 20:1, 30:1, 40:1 oder 50:1.
- Geplanter Einsatz: unlegierter Stahl von ca. 2 bis 25 mm. Die tatsächlich erreichbare Schnittqualität und zulässigen Parameter bei 25 mm sind noch anhand der Schneidtabellen zu prüfen.
- **Status:** Modell ausgewählt; Kauf noch nicht bestätigt.

Herstellerseite: <http://spartus.pl/en/produkt/plasma-cutter-xpro-cut-70cnc/>

Handbuch: <http://spartus.pl/wp-content/uploads/2026/05/spartus_xprocut70cnc_eng.pdf>

## 3. Steuerung und Brennerhöhenregelung

- **Mesa 7i96S:** Ethernet-Motion-Controller mit fünf Step/Dir-Kanälen; vier werden benötigt.
- **LinuxCNC + QtPlasmaC:** Bewegungssteuerung, Referenzfahrt mit automatischer Portal-Rechtwinkligstellung, Plasmaschneidablauf und THC.
- **Mesa THCAD:** Vorgesehen zur Erfassung der geteilten Lichtbogenspannung des SPARTUS. Die konkrete THCAD-Ausführung und Skalierung sind noch zu bestimmen.
- Geplante Signale: Torch On, Arc OK, Arc Voltage, Referenzschalter, Endschalter und Sicherheitsstatus.
- **Mesa 7i96S ist bereits geliefert** und soll direkt per Ethernet mit dem ThinkCentre verbunden werden.

Die THC korrigiert während des Schnitts die Brennerhöhe anhand der Lichtbogenspannung. Die initiale Blechoberfläche wird über Floating Head oder ohmsche Antastung ermittelt; die endgültige Lösung ist offen.

## 4. Antriebe – aktualisierte Festlegung

**Neue Entscheidung: NEMA23-Schrittmotoren, Open Loop (offener Regelkreis), 3 Nm.** Die zuvor diskutierten Closed-Loop-Motoren mit integriertem Treiber entfallen.

| Achse | Anzahl | Motor |
|---|---:|---|
| Y-Achse links | 1 | NEMA23, 3 Nm, Open Loop |
| Y-Achse rechts | 1 | NEMA23, 3 Nm, Open Loop |
| X-Achse | 1 | NEMA23 kompakt, ca. 1,2 Nm, 56 mm (fährt auf dem X-Wagen mit), Open Loop |
| Z-Achse | 1 | NEMA23 kompakt, ca. 1,2 Nm, 56 mm, direkt über Kupplung auf SFU1204, Open Loop |
| **Gesamt** | **4** | **4 × NEMA23, 3 Nm** |

- **4 separate digitale Step/Dir-Schrittmotortreiber** statt integrierter Closed-Loop-Treiber.
- Treiber müssen hinsichtlich Phasenstrom, Versorgungsspannung und Step/Dir-Eingangspegel zu den konkret gewählten Motoren und zur Mesa 7i96S passen.
- **48 V DC** als vorgesehene Motor-/Treiber-Versorgung; Netzteil-Leistung erst nach Treiberauswahl festlegen.
- **24 V DC** für geeignete Sensorik und Steuerungs-I/O vorgesehen; Versorgung der Mesa gemäß Datenblatt auslegen.
- Bei Open Loop gibt es keine automatische Rückmeldung über Schrittverluste. Deshalb Beschleunigung und Maximalgeschwindigkeit mit Reserve einstellen und die Mechanik leichtgängig ausführen.
- Die bisher geplante Bestellung eines 2-Nm-Closed-Loop-Testmotors ist **hinfällig**.

## 5. Linearführungen und Mechanik

**Festgelegt: HGR15-Profilschienen auf allen Achsen.** Vorläufige Dimensionierung:

| Achse | Schienen | Wagen | Grobe Schienenlänge |
|---|---|---|---|
| Y-Achse (lang) | 2 × HGR15 | 4 × HGH15 (2 Wagen je Schiene) | 1200–1400 mm |
| X-Achse (kurz) | 2 × HGR15 | 4 × HGH15 | 800–900 mm |
| Z-Achse | 2 × HGR15 | 2–4 × HGH15 | 300–350 mm |

**Lagerung Y festgelegt:** je Schiene 2 Wagen, insgesamt 4 Wagen für das Portal.

### Portalbrücke

- Tragende Struktur der Brücke: **Alu-Rechteckrohr 80 × 40 × 4 mm**, 80 hoch stehend (gewählt 20.10.2026 statt 20 × 40 × 4: ca. 10× steifer gegen Biegung und Verdrehung, 1,7 kg bei 720 mm).
- X-Achse: HGR15 oben und unten auf der Brücke, Wagen aus Alu-Platten greift von vorn um die Brücke; vorn Z-Achse und Schneiddüse. **Omega-Antrieb** (20.10.2026, statt Motor am Brückenende, wegen 800 mm Gesamtbreite): X-Riemen hochkant hinter der Brücke, Enden an den Sätteln der Y-Winkel geklemmt; Motor hinten auf dem Wagen (gleicht Brenner und Z-Achse teilweise aus). X-Energiekette hinter der Brücke, Anschlusskasten auf der linken Portalseite.
- Trägt die X-Schienen und den Brennerwagen mit Z-Achse; Durchbiegung und Torsion in der FreeCAD-Konstruktion prüfen.
- Anbindung an die Y-Wagen beidseitig über Portalwangen.

Die tatsächlichen Schienenlängen folgen aus der FreeCAD-Konstruktion, Wagenabständen, Endanschlägen und dem nutzbaren Hub.

### Zahnriemenantrieb

- **HTD5M**, **15 mm breit**, für beide horizontalen Achsen.
- **Festgelegt: 24 Zähne** je Antriebsriemenscheibe (Teilkreis 38,2 mm, 120 mm Weg pro Umdrehung), Direktantrieb ohne Untersetzung, Bohrung passend zur Motorwelle.
- Riemen über der Schienenmitte: Obertrum mit Zähnen nach unten an den Enden des Y-Winkels geklemmt, Rücktrum läuft durch einen Tunnel im Winkel über den Wagen zurück (Abstand der Trume = Teilkreis).

### Fahrwerte (Richtwerte, mit den SPARTUS-Schneidtabellen abgleichen)

| Größe | Richtwert |
|---|---|
| Schnittgeschwindigkeit 1–2 mm | bis 6–8 m/min |
| 3 mm / 6 mm / 10 mm / 20 mm | ca. 3–4 / 1,5–2 / 1 / 0,3–0,4 m/min |
| Eilgang | 10–15 m/min |
| Beschleunigung | 1–3 m/s² |

- Mit 24 Zähnen entsprechen 15 m/min nur 125 U/min; dort hat der NEMA23 mit 3 Nm nahezu sein volles Moment (> 100 N Vorschubkraft je Seite bei ca. 12–15 kg bewegter Portalmasse).
- Auflösung 0,075 mm (1/8-Mikroschritt) bzw. ca. 0,04 mm (1/16).
- Wegen der niedrigen Drehzahl Treiber mit Mikroschritt und Resonanzdämpfung wählen.
- Auf der Y-Achse (lang) je Seite ein eigener Motor, Treiber und Riemenantrieb.
- Motoren möglichst stationär am Tisch; Riemen parallel und möglichst nahe an der Führungsebene.
- Riemenlängen, Umlenkrollen und Spannvorrichtungen sind noch zu konstruieren.

### Referenzschalter (bestellt 23.10.2026)

- 4× induktiver Näherungsschalter **LJ12A3-4-Z/AY** (M12, PNP, Öffner, 6–36 V, 4 mm auf Stahl), betrieben an 24 V.
- **Y links/rechts:** hinten über der Y-Riemenscheibe, genau über der Schiene, Achse längs (Halter am Y-Motorhalter); Stahlfahne abgekantet auf der Klemmplatte am festen Ende des Y-Winkels. Über das M12-Gewinde fein einstellbar (Portal rechtwinklig).
- **X:** am linken Y-Winkel (Kastenseite) auf der Sattelrückwand, Achse quer; Stahlfahne unter der Deckplatte des X-Wagens. Schaltet ab ca. 82 mm Wagenmitte.
- **Z:** oben, senkrecht durch den Z-Kopf; Stahlfahne auf dem Z-Schlitten.
- Andere Achsenden über Software-Endlagen in LinuxCNC.

### Energiekette Y (Stand 23.10.2026)

- Liegend links, über dem linken Y-Winkel auf einem Träger mit Rinne (Stützen an den Rahmenenden), Ausleger vom Portal außen an der Rinne vorbei. Kette 20 × 38 innen, R125, ca. 1,01 m (`cad/energiekette/`).
- Die geteilte Lichtbogenspannung kommt an der CNC-Buchse des Geräts heraus (Anleitung S. 13), läuft also nicht in der Kette; im Schlauchpaket des SP80M nur Luft/Strom und Start-Stopp, Pilot, Düse.
- Kettenturm an der Stirn der links verlängerten Brücke (Einsteckteil, mit den Sattel-M6 verschraubt).
- **X-Kette** 20 × 38, R65, liegend hinter der Brücke auf einer Ablage über dem X-Wagen; Festpunkt links am Kettenturm, bewegtes Ende am Pfosten auf der Deckplatte. Z ohne Kette (lose Schlaufe).
- Gesamtbreite mit beiden Ketten: 789 mm.

### Gantry Squaring

- Zwei unabhängige Referenzschalter für die Y-Achse.
- Eine Schalterposition fein einstellbar, um das Portal rechtwinklig auszurichten.
- LinuxCNC referenziert beide Seiten getrennt und bewegt sie anschließend synchron.

### Z-Achse

- Kugelumlaufspindel, voraussichtlich **SFU1204**.
- Zielwert ca. **100 mm nutzbarer Hub**.
- Floating Head oder ohmsche Antastung; genaue Konstruktion offen.
- Automatische Brennerhöhenregelung (THC) vorgesehen.

## 6. Wasserbett

**Geliefert:** stapelbare PE-Auffangwanne für Kleingebinde von Schäfer Shop, flacher Boden. Modell: `cad/wanne/`.

Produkt: <https://www.schaefer-shop.de/p/auffangwanne-fuer-kleingebinde-stapelbar-polyethylen-schwarz-diverse-varianten?selectedItem=665409>

Aufmaß vom 20.10.2026:

| Maß | Wert |
|---|---|
| Außen über Bördelrand | 597 × 1194 × 119 mm |
| Bördelrand | Ø25 (Messschieber), flach gestaucht, Unterkante 110 mm über Standfläche |
| Lichte Öffnung am Bördel | 540 mm breit (längs ca. 1142 mm gemessen); Wanne ist verformbar, maßgeblich sind Außenmaße und Bodenfläche |
| Boden innen | 1100 × 550 mm, Übergang Boden/Wand ca. R8 |
| Winkel Boden/Wand | ca. 97° |
| Wandstärke | ca. 3 mm |
| Spiel im Grundrahmen (lichte Weite 640 × 1240) | 21,5 mm quer / 23 mm längs je Seite |

Vorläufige Planungswerte:

| Parameter | Wert |
|---|---|
| Wasserstand | ca. 105 mm über Wannenboden (knapp unter dem Bördel) |
| Abstand Wasseroberfläche zur Blechunterseite | ca. 15 mm (Blech liegt 1 mm über dem Bördel, sonst trägt der Bördel breite Bleche) |
| Opferleisten (Slats) | ca. 35 × 3 mm Flachstahl |
| Opferleisten-Abstand | ca. 50 mm |
| Wasserinhalt | aus dem Modell ca. 58 l bei 95 mm Wasserstand über Standfläche (ca. 68 l bis Unterkante Bördel) |

- **Wannenkäfig** aus Stahl-Rechteckrohr 20 × 20 × 2 (`cad/wannenkaefig/`): hängt mit dem oberen Ring im Grundrahmen, trägt den Wannenboden auf Querrohren und hält die Wände. Wanne steht 120 mm unter Rahmenoberkante, Blechunterseite = Rahmenoberkante.
- Austauschbare Opferleisten auf Trägern, die im Wasser auf dem Wannenboden direkt über den Querrohren des Käfigs stehen; die Last geht durch den Boden ins Stahlrohr, die PE-Wände tragen nichts.
- **Ablauf** mittig im Wannenboden, Ø25–32 mm, der Käfigboden ist dort frei.
- Wanne wird zum Reinigen **nach oben herausgehoben** (Portal ganz hinten); der Käfig bleibt fest im Rahmen.
- Wanne zum Reinigen möglichst herausnehmbar; flacher Boden erleichtert das Entfernen von Schlamm.
- **Sicherheitsrelevant:** PE kann durch direkten Plasmastrahl und heiße Schlacke beschädigt werden. Wannenboden und Seiten sind konstruktiv zu schützen; Wasserstand und Schnittbereich müssen das Risiko berücksichtigen. Wasserbett ersetzt keine geeignete Lüftung/Absaugung.

## 7. Druckluft

- Druckluft muss ausreichend trocken, sauber und ölfrei sein.
- Vorgesehen: Wasserabscheider, Fein-/Koaleszenzfilter, Druckregler; bei Bedarf Kältetrockner.
- Betriebsdruck und Luftverbrauch werden anhand des SPARTUS-Handbuchs festgelegt; vorhandenen Kompressor darauf prüfen.
- Druckverlust in Schlauch und Anschlüssen unter Last berücksichtigen.

## 8. Beschaffungsstand

| Komponente | Status |
|---|---|
| Rahmenstahl | Vorhanden |
| Lenovo ThinkCentre M929q | Vorhanden |
| Mesa 7i96S | Geliefert |
| PE-Wasserwanne 597 × 1194 × 119 | Geliefert, vermessen |
| SPARTUS XPro CUT 70CNC | Modell festgelegt; Maschinenbrenner SP80M gekauft (22.10.2026), Maße Düsenkopf und Schlauchpaket folgen |
| Mesa THCAD | Vorgesehen, Variante offen |
| 4 × NEMA23, 3 Nm, Open Loop | Neu festgelegt, noch auszuwählen/zu bestellen |
| 4 × separate Step/Dir-Treiber | Noch auszuwählen |
| 48-V- und 24-V-Netzteile | Vorgesehen, noch zu dimensionieren |
| HGR15-Schienen und Wagen | Bauart festgelegt, Längen offen |
| HTD5M/15-mm-Riemen und Pulleys | Bauart festgelegt, Mengen/Längen offen |
| Z-Spindel | SFU1204 vorgesehen, Details offen |
| Endschalter, Schütz, Not-Aus, Verkabelung | Noch auszulegen |

## 9. Nächste Schritte

1. ~~Gelieferte Wanne vermessen~~ (erledigt 20.10.2026, siehe Abschnitt 6).
2. Rahmen und Portal in **FreeCAD** konstruieren.
3. Verfahrwege, Schienenlängen und Befestigungsebenen festlegen.
4. HTD5M-Riemenführung mit zwei Antrieben auf der langen Achse ausarbeiten.
5. Passende **3-Nm-NEMA23-Open-Loop-Motoren** und separate Step/Dir-Treiber auswählen; Strom, Induktivität, Drehmoment-Drehzahl-Kennlinie und Versorgung prüfen.
6. Motoransteuerung über die bereits vorhandene Mesa 7i96S testen.
7. Z-Achse, Antastung und THCAD-Anbindung planen.
8. Schaltschrank, Erdung/EMV, Not-Aus und Sicherheitskreis auslegen.

---

**Leitlinie:** Solide, wartungsfreundliche und möglichst kompakte Eigenbau-Maschine. Festgelegte Komponenten nicht unnötig neu aufrollen; offene Maße und elektrische Detaildaten vor Bestellung anhand von Konstruktion und Herstellerunterlagen verifizieren.
