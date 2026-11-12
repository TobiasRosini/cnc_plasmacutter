# -*- coding: utf-8 -*-
"""
Y-Energiekette, liegend, rechts (Kastenseite).

Kette igus E2/000 2400.03 (38 x 25 innen, 54 x 35 außen), R125. Die feste Hälfte liegt in einer Rinne
auf einem Träger über dem rechten Y-Winkel (höher als alles, was dort am Portal
hochsteht). Der Träger liegt auf zwei Stützen (hinten am Rahmenende, vorn hinter dem Bein), außen am
Längsträger. Das bewegte Ende sitzt oben auf der Schlaufe; ein Ausleger aus
Alu-Flachmaterial geht von der Kettenlasche des rechten Winkels außen an der Rinne
vorbei nach oben.

Lage: x ab Mitte rechte Y-Schiene (negativ = außen), y = Rahmen-y (feste Teile)
bzw. ab Portalmitte (Ausleger), z = Rahmenoberkante.

Aufruf:
  python3 cad/live.py cad/energiekette/energiekette.py
"""
import os
import sys
import math
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))
import fc_dok  # noqa: E402
import kaufteile as kt  # noqa: E402

P = dict(
    # Maschine (aus Grundrahmen / Y-Winkel)
    rahmen_laenge=1556.0,       # Oberrahmen (vorn 40 über den Untertisch)
    rohr=40.0,
    portal_y=(160.0, 1280.0),   # Portalmitte von hinten bis vorn
    # Kette
    # igus E2/000 Serie 2400.03: innen 38 x 25, außen 54 x 35, Teilung 46 mm/Glied,
    # Radien 55/75/100/125/150/...; R bis Kettenmitte (Bauhöhe H = 2R + 35).
    # Länge nach igus: S/2 + K (K = pi R + Zuschlag, Katalog 5.102)
    kette_h=35.0,
    kette_b=54.0,
    teilung=46.0,
    radius=125.0,               # 2400.03.125.0
    glieder=23,                 # 1058 mm, igus: S/2 + K = 560 + 496 = 1056
    reserve=40.0,               # Schlaufe bei Portal hinten reserve/2 hinter der Mitte des Anschlussteils (mind. end_laenge)
                                # (bleibt hinter der X-Ablage); der Festpunkt folgt aus der Kettenlänge
    kette_innen_x=-7.0,         # Innenkante der Kette (Mitte wie bei 56 breit) (Z-Schlitten fährt bei X rechts bis 2 mm vor die Schienenmitte)
    # Träger (Stahl 40x20x2, flach) und Rinne (Blech 2 mm)
    traeger_uk=163.0,           # über X-Schalterblock (161)
    traeger_b=40.0,
    traeger_h=20.0,
    # Rinnen Y und X: Alu-U-Profil 20 x 60 x 20 x 2 (Handel, ungekantet), innen 56
    rinne_t=2.0,
    rinne_rand=20.0,
    kanal_ende_y=1437.25,       # Kabelkanal auf dem Träger vom festen Kettenende bis hier; Kanal und
    traeger_ende_y=1437.25,     # Träger stecken vorn gemeinsam im Kanalknoten (Unterbau, Muffe 25 tief)
    traeger_knoten_y=[1419.0, 1431.0],  # M5-Nietmuttern in der Innenseite des Trägers (Knoten, = Unterbau)
    kanal_h=40.0,               # Kabelkanal 40 x 40 (PVC, Wand 2) auf dem Träger
    kanal_t=2.0,
    kanal_schraub_y=[950.0, 1150.0, 1350.0],   # M4 durch den Kanalboden in Nietmuttern im Träger
    rinne_luft=1.0,             # Kette 54, festes Anschlussteil 51 (bewegte Enden liegen nicht in der Rinne)
    # Anschlussteile igus 2030.12PZ (Kunststoff, verriegelt): Platte 7 dick, Ba + 1 = 55
    # breit, 40 lang, 2 Bohrungen Ø6,1 im Abstand A = 25 quer zur Kette, 10 mm vom äußeren Ende
    end_D=55.0,
    end_C=25.0,
    end_F=6.1,
    end_laenge=40.0,
    end_flansch=7.0,
    end_loch=10.0,
    # Stützen: je ein Rechteckrohr außen am Längsträger, hinten 20x40x2 (40 entlang y) am
    # Rahmenende mit Druckkopf unter dem Träger, vorn 40x40x2 hinter dem Bein unter dem
    # Kanalknoten (Unterbau), in dem Träger und Kanäle zusammenlaufen.
    # Rohr an den Längsträger: 2x M6 durch die Innenwand in Nietmuttern (Grundrahmen
    # ek_stuetze_y/z), außen Zugangslöcher. Kopf ins Rohr: 2x M5 in eingepresste Muttern.
    # Träger auf den Kopf: 2x M6 von unten in Nietmuttern in der Trägerunterseite.
    stuetze=(20.0, 40.0),
    stuetze_wand=2.0,
    stuetze_m6_y=[10.0, 30.0],      # = Grundrahmen ek_stuetze_y
    stuetze_m6_z=-20.0,             # = Grundrahmen ek_stuetze_z
    # Vorn: Rechteckrohr 40 x 40 x 2 direkt hinter dem vorderen Bein, nach unten verlängert
    # (trägt den senkrechten Kabelkanal). M6 in Längsträger Oberrahmen und Längsrohr Untertisch.
    stuetze_vorn=(40.0, 40.0),
    stuetze_vorn_y0=1436.0,         # bis Rückseite Bein (1476) = Grundrahmen ek_stuetze_vorn_y
    stuetze_vorn_m6_z=[-20.0, -60.0],   # = Grundrahmen ek_stuetze_vorn_z
    stuetze_vorn_uk=-170.0,         # Rahmen-z 680, über der Muffe des Kanalbogens (Unterbau)
    stuetze_vorn_ok=50.0,           # Rahmen-z 900: darauf sitzt der Kanalknoten (statt Stützkopf)
    stuetze_knoten=[(-48.0, 35.0), (-32.0, 35.0)],  # M5-Nietmuttern in der Vorderwand (x, z; = Unterbau)
    stuetze_kanal_z=[-130.0, 10.0],     # M5-Nietmuttern außen für den senkrechten Kanal (= Unterbau)
    stuetze_kanal_y=[10.0, 30.0],
    zugang_m6_d=13.0,
    kopf_h=15.0,
    kopf_zapfen=25.0,
    kopf_y=60.0,                    # Kopf ragt über das Rohr hinaus: Trägerschrauben von unten zugänglich
    kopf_m5_y=[12.0, 28.0],
    kopf_m5_unter_ok=12.0,
    traeger_m6_y=50.0,              # ab Rahmenende
    nietmutter_m6_d=9.0,
    nietmutter_m5_d=7.0,
    # Kettenturm (Alu-Flachmaterial 40x8) an der Stirn der rechts verlängerten Brücke.
    # In der Brücke steckt ein Einsteckteil (Druck), das von den M6 des Sattels
    # mit gehalten wird; der Turm ist mit 4x M6 in dessen Stirnseite geschraubt.
    ausleger_b=40.0,
    ausleger_t=8.0,
    ausleger_y=(-20.0, 20.0),   # ab Portalmitte (= Brückentiefe)
    ausleger_luft=4.5,          # zur Rinne (Turm bleibt an seiner Stelle)
    bruecke_z=(57.0, 137.0),    # Brücke über Rahmen-OK
    bruecke_wand=4.0,
    bruecke_tiefe=40.0,
    m6_x=[-11.5, 11.5],         # M6 des Sattels (ab Schienenmitte)
    m6_z=[75.0, 95.0],
    einsteck_innen=38.0,        # Einsteckteil reicht bis hier (über die zweite M6)
    turm_loecher=[(-8.0, 80.0), (8.0, 80.0), (-8.0, 118.0), (8.0, 118.0)],  # (y, z)
    # links liegt die Sattelschraube M6 (z 75) nur 8,5 mm hinter der Stirn: die
    # unteren Einsätze würden sie schneiden, deshalb beide Reihen über den Sattel-M6
    turm_loecher_links=[(-8.0, 106.0), (8.0, 106.0), (-8.0, 124.0), (8.0, 124.0)],

    # X-Energiekette über der Brücke: igus 2400.03, R75, liegend auf einer Ablage,
    # die an der Kettenseite am Kettenturm und an der Gegenseite an einer Platte an der
    # Brückenstirn sitzt (Einsteckteil wie am Turm). Festpunkt so weit zur Kettenseite,
    # wie es die Kettenlänge erlaubt (kurzer Rücklauf der Leitungen in der Rinne hinten),
    # Schlaufe zur
    # Kettenseite, bewegtes Ende am Halter auf dem Z-Kopf. Die Leitungen treten dort zur
    # Gegenseite aus und kehren über einen Bogen zum Brenner zurück: an der Kettenseite
    # wäre dafür bei X am Ende kein Platz (Turm, Y-Kettenende). Steht der Wagen an der
    # Gegenseite, trägt sich das obere Trum über den Festpunkt hinaus frei.
    xk_radius=75.0,             # 2400.03.075.0 (R65 gibt es nicht; Adern innen in der Kehre > R60)
    xk_glieder=14,              # 644 mm, igus: S/2 + K = 283 + 346 = 629
    xk_y_vorn=13.5,             # Vorderkante Kette; hinteres M5 des festen Endes mit 3 mm Wand hinter dem Träger             # Vorderkante Kette, Anschlussstück bleibt 1 mm vor dem Halter am Z-Kopf
    xk_traeger_uk=225.0,        # über Y-Kette (unteres Trum bis 220) und X-Motor
    xk_halter_dicke=15.0,       # Ablagehalter X: Platte innen am Turm (M5-Mutter 8 tief), dahinter beginnt die Ablage
    xk_zapfen=25.0,             # Zapfen des Ablagehalters in der Ablage
    xk_halter_dx=-10.0,         # bewegtes Ende neben der Wagenmitte (am Z-Kopf)
    xk_wagen_x=(78.0, 644.0),   # X-Weg Wagenmitte (Rahmen-x)
    xk_reserve=40.0,            # Schlaufe bei X rechts xk_reserve/2 neben der Mitte des Anschlussteils (mind. end_laenge)
    xk_bruecke_links_x=720.0,  # Brückenstirn Gegenseite (Rahmen-x)
    # Druckteile am Kettenturm (Turm bleibt ein gerades Alu-Flachmaterial 40 x 8):
    # oben Halter für das bewegte Y-Kettenende, auf Höhe der X-Ablage der Ablagehalter
    # (Zapfen für die Ablage, darauf liegt die Schlaufe bei X am Ende)
    hy_dicke=20.0,              # Halter Y über dem Anschlussstück
    hy_y=(-20.0, 32.0),         # nach vorn verlängert: Kabelbinder an der Leitungsbiegung
    turm_x_y=[-14.0, 12.0],     # M5 Turm -> Ablagehalter (innerhalb der 40 mm Turmbreite)
    # Leitungen ohne Schutzschlauch (Adern des Brennerpakets + Motor- und Schalterkabel),
    # Biegeradius mindestens 60 (Stromkabel Ø6,3); Hüllkurven als Rundrohr
    leitung_r=60.0,
    # zwei Pfade wie die Fächer der Ketten (Trennsteg): Brenner (Nr. 1-4) und Steuerung (Nr. 5-9),
    # flach nebeneinander, Mitte = Trennsteg; Steuerung in Laufrichtung links (in der Y-Kette innen)
    fach_b=(17.5, 16.0),        # Breite Brenner, Steuerung (unten 3 bzw. 2 Leitungen nebeneinander)
    fach_h=13.0,                # Höhe beider Pfade (zwei Lagen)
    fach_steg=3.0,              # Abstand der Pfade (Trennsteg, Mittelsteg der Schellen)
    brenner_leitung_d=16.0,     # Adern des Brennerpakets zwischen X-Kette und Brenner
    leitung_hinten_y=-143.0,    # Lauf hinter der Ablage (Kehre R60 in den Festpunkt)
    leitung_oben_z=580.0,       # Bogen über das Y-Kettenende nach hinten
    leitung_ab_x=16.0,          # dort hinter der Ablage senkrecht nach unten (Pfade nebeneinander in x)
    leitung_s_y=(-6.0, -51.0),  # oben zwischen Bogen und Umlenkkopf seitlich versetzt (neben die Y-Kette)
    leitung_r_s=70.0,           # Versatz liegt in der Ebene der Pfade: innerer Pfad R60
    leitung_dreh_x=270.0,       # in der Ablage hinten bis hier um 90° verdrillt (Pfade danach nebeneinander in y)
    # Führungen (Druck): Leitungsbogen auf dem Halter Y (180°-Kehre R60), Umlenkkopf auf einem
    # Mast (Alu 30 x 4) an der Rinne hinten (90° nach unten)
    fuehrung_b=40.0,            # Breite zwischen den Wangen
    wange_t=3.0,
    wange_r=75.0,               # Wangen bis zu diesem Radius um die Bogenmitte
    mast=(40.0, 8.0),           # Alu-Flachstange 40 x 8 (wie Kettenturm)
    mast_dx=5.0,                # Mastmitte neben der Leitung (Abstand zur Y-Kette)
    mast_oben=591.5,            # = Oberkante Umlenkkopf (leitung_oben_z + fach_h / 2 + 5)
    mast_m4_dx=10.0,            # M4 unten in Gewinde in der Stirn der Ablage hinten
    rh_t=8.0,                   # Ablage hinten: Alu-Flachstange 40 x 8 (statt Winkel)
    kopf_m4_z=[470.0, 560.0],   # M4 Kopf an den Mast
    kopf_m4_dx=10.0,            # M4 Kopf an den Mast, x ab leitung_ab_x
    kopf_breit_z=478.0,         # Kopf ab hier nach rechts verbreitert (Schelle), darunter läuft die Y-Kette
    schelle_senk_z=495.0,       # Schelle am senkrechten Lauf (Mitte)
    dist_z=(350.0, 430.0),      # Distanzstück am Mast unter dem Kopf (Auflage der Leitungen)
    dist_kb_z=[362.0, 418.0],   # Kabelbinder quer durch das Distanzstück
    dist_m4_z=[380.0, 400.0],   # M4 von hinten durch den Mast in Muttern im Distanzstück
    # Versteifungswinkel (Druck) außen an der Ecke Mast / Ablage hinten: Schenkel hinter dem Mast,
    # Bodenplatte unter der Ablage, zwei Rippen hinten
    mw_t=6.0,                   # Wandstärke Schenkel und Bodenplatte
    mw_h=100.0,                 # Höhe des Schenkels ab Unterkante Ablage
    mw_tief=40.0,               # Rippen nach hinten
    mw_rippe=5.0,
    mw_x=(1.0, 39.0),           # Breite (links vor dem Rinnenhalter)
    mw_m4_oben_z=85.0,          # M4 oben in Gewinde im Mast, z ab Unterkante Ablage
    mw_m4_ablage_y=[-156.0, -129.5],   # M4 von unten in Gewinde in der Ablage (neben den Leitungen)
    # Verbindungsplatte (Druck) unter dem freien Leitungsstück zwischen Bogen und Kopf:
    # liegt in Aussparungen oben in beiden, je 2x M4 von oben (gesenkt) in Muttern
    vp_t=15.0,
    vp_y=(-60.0, 0.0),
    vp_m4_bogen=[(-10.0, -10.0), (10.0, -10.0)],   # (x ab Kettenmitte, y)
    vp_m4_kopf=[(-10.0, -52.0), (10.0, -52.0)],    # (x ab leitung_ab_x, y)
    # Leitungsschellen (Druck, 5 gleiche): zwei Tunnel mit Mittelsteg über den Pfaden, je 1x M3 durch
    # die Schenkel in Muttern der Unterlage; oben auf Bogen, Verbindungsplatte und Kopf, in der
    # Ablage hinten auf Sockeln (heben die Pfade auf Kettenhöhe, 2x M3 von unten durch die Ablage)
    bg_spiel=1.0,               # Tunnel breiter als die Pfade (Schellen auch im Bogen der Pfade)
    bg_steg=2.0,                # Mittelsteg der Schellen (Abstand der Pfade fach_steg)
    bg_schenkel=9.4,            # Schenkel mit M3 (Wand 3)
    bg_l=15.0,
    bg_dach=3.0,
    bg_oben_y=[12.5, -30.0, -72.0],             # Bogen, Verbindungsplatte, Kopf (y der Mitte)
    bg_rinne_x=[300.0, 420.0],
    sockel_l=32.0,
    sockel_m3_dy=11.0,
    brenner_oben_z=555.0,       # Bogen über dem Brenner (X-Wagen-z), Z unten
    brenner_stummel_z=475.0,    # Oberkante Tülle + Stummel am Brenner (X-Wagen-z), Z unten
    brenner_y=136.0,
    # Rinne hinten (Alu-Winkel 40 x 20 x 2) auf Haltern (Druck) an der Ablage
    rh_halter_x=[40.0, 250.0],  # dazu ein dritter unter dem festen Kettenende (hinteres M5)
    rh_halter_b=20.0,
    zkopf_hinten_y=28.0,        # Rückseite Z-Kopf-Sockel (X-Wagen-y)
    zkopf_uk=270.0,             # Unterkante Z-Kopf-Sockel (X-Wagen-z)
    xk_halter_loecher=[-28.0, 2.0],     # x der M5-Muttern in der Z-Kopf-Rückseite (= z_achse xk_halter_x)
    hx_platte=14.0,             # Platte über dem Anschlussstück (Muttern oben)
    bruecke_uk_x_wagen=57.0,    # Brückenunterkante über Rahmen-OK (X-Wagen z = 0)
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def geo():
    k_x1 = P["kette_innen_x"]
    k_x0 = k_x1 - P["kette_b"]
    t, rl = P["rinne_t"], P["rinne_luft"]
    r_x0, r_x1 = k_x0 - rl - t, k_x1 + rl + t
    z_rinne = P["traeger_uk"] + P["traeger_h"]
    z_ku = z_rinne + t                                  # Unterkante unteres Trum
    z_mitte_u = z_ku + P["kette_h"] / 2
    z_mitte_o = z_mitte_u + 2 * P["radius"]
    ym0 = P["portal_y"][0] + sum(P["ausleger_y"]) / 2
    ym1 = P["portal_y"][1] + sum(P["ausleger_y"]) / 2
    laenge = P["glieder"] * P["teilung"] + P["end_laenge"]        # Anschlussteile je zur Hälfte
    l_eff = laenge - math.pi * P["radius"]
    y_fest = ym0 - P["reserve"] + l_eff                 # Schlaufe bei Portal hinten reserve/2 hinter dem Ende
    if ym1 - y_fest > l_eff:
        raise ValueError("Y-Kette zu kurz")
    a_x1 = r_x0 - P["ausleger_luft"]
    y_hinten = ym0 - P["reserve"] / 2 - P["radius"] - P["kette_h"] / 2 - 5   # Rinne/Träger hinten
    return dict(y_hinten=y_hinten, k_x0=k_x0, k_x1=k_x1, r_x0=r_x0, r_x1=r_x1, z_rinne=z_rinne, z_ku=z_ku,
                z_mu=z_mitte_u, z_mo=z_mitte_o, ym0=ym0, ym1=ym1, y_fest=y_fest, l_eff=l_eff,
                laenge=laenge, a_x1=a_x1, a_x0=a_x1 - P["ausleger_t"])


# ---------------------------------------------------------------- feste Teile
def traeger_rinne():
    g = geo()
    xm = (g["r_x0"] + g["r_x1"]) / 2
    tb, th = P["traeger_b"], P["traeger_h"]
    yh = g["y_hinten"]
    L = P["traeger_ende_y"]                              # vorn im Kanalknoten (Unterbau)
    tr = box(xm - tb / 2, xm + tb / 2, yh, L, P["traeger_uk"], P["traeger_uk"] + th)
    tr = tr.cut(box(xm - tb / 2 + 2, xm + tb / 2 - 2, yh - 1, L + 1, P["traeger_uk"] + 2,
                    P["traeger_uk"] + th - 2))
    for ya, ri, _, _, _, _, kopf in stuetzen_lagen():   # M6-Nietmuttern zu den Stützköpfen
        for dx in (-10.0, 10.0):
            if kopf:
                tr = tr.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, 4,
                                              V(xm + dx, ya + ri * P["traeger_m6_y"], P["traeger_uk"] - 1)))
    for y in P["traeger_knoten_y"]:                      # M5-Nietmuttern innen: Träger im Kanalknoten
        tr = tr.cut(Part.makeCylinder(P["nietmutter_m5_d"] / 2, 4, V(xm + tb / 2 + 1, y, P["traeger_uk"] + th / 2),
                                      V(-1, 0, 0)))
    xc = (g["k_x0"] + g["k_x1"]) / 2
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):                  # Nietmuttern M5 für das feste Kettenende
        tr = tr.cut(Part.makeCylinder(3.5, 4, V(xc + dx, g["y_fest"] + loch_versatz(),
                                                P["traeger_uk"] + th - 3)))
    for y in P["kanal_schraub_y"]:                       # Nietmuttern M4 für den Kabelkanal
        tr = tr.cut(Part.makeCylinder(3.0, 4, V(xm, y, P["traeger_uk"] + th - 3)))
    t = P["rinne_t"]
    y0 = yh                                              # Rinne hinten bis hinter das feste Kettenende
    y1 = rinne_ende_y()
    ri = box(g["r_x0"], g["r_x1"], y0, y1, g["z_rinne"], g["z_rinne"] + t)
    xc = (g["k_x0"] + g["k_x1"]) / 2
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):                  # festes Kettenende, M5
        ri = ri.cut(Part.makeCylinder(2.75, t + 2, V(xc + dx, g["y_fest"] + loch_versatz(), g["z_rinne"] - 1)))
    for x0 in (g["r_x0"], g["r_x1"] - t):
        ri = ri.fuse(box(x0, x0 + t, y0, y1, g["z_rinne"], g["z_rinne"] + P["rinne_rand"]))
    return tr, ri.removeSplitter()


def rinne_ende_y():
    return geo()["y_fest"] + P["end_laenge"] / 2 + 10.0


def kabelkanal_y():
    """Kabelkanal 40 x 40 (mit Deckel) auf dem Träger vor der Rinne: nimmt die Leitungen
    vom festen Kettenende nach vorn auf; an seinem Ende gehen sie seitlich in den
    senkrechten Kanal (Unterbau)."""
    g = geo()
    xm = (g["r_x0"] + g["r_x1"]) / 2
    b, h, t = P["traeger_b"], P["kanal_h"], P["kanal_t"]
    y0, y1, z0 = rinne_ende_y(), P["kanal_ende_y"], g["z_rinne"]
    k = box(xm - b / 2, xm + b / 2, y0, y1, z0, z0 + h)
    k = k.cut(box(xm - b / 2 + t, xm + b / 2 - t, y0 - 1, y1 + 1, z0 + t, z0 + h - t))
    for y in P["kanal_schraub_y"]:
        k = k.cut(Part.makeCylinder(2.25, t + 2, V(xm, y, z0 - 1)))
    return k


def stuetzen_lagen():
    """Je Stütze: (y0, Richtung, Rohr (x, y), Unterkante, M6-z, Oberkante, Stützkopf). Rohr von
    y0 bis y0 + richt * Rohr-y; hinten am Rahmenende mit Druckkopf unter dem Träger, vorn
    hinter dem vorderen Bein bis unter den Kanalknoten (Unterbau), der den Träger aufnimmt."""
    return [(0.0, 1, P["stuetze"], -P["rohr"], [P["stuetze_m6_z"]], P["traeger_uk"] - P["kopf_h"], True),
            (P["stuetze_vorn_y0"], 1, P["stuetze_vorn"], P["stuetze_vorn_uk"], P["stuetze_vorn_m6_z"],
             P["stuetze_vorn_ok"], False)]


def stuetzen():
    """Rechteckrohre senkrecht außen am Längsträger: hinten 20 x 40 x 2, vorn 40 x 40 x 2
    (nach unten verlängert, außen Nietmuttern M5 für den senkrechten Kabelkanal)."""
    t = P["stuetze_wand"]
    x1 = -P["rohr"] / 2                                # Außenfläche Längsträger
    res = []
    for ya, ri, (sx, sy), z0, m6_z, z1, kopf in stuetzen_lagen():
        x0 = x1 - sx
        y0, y1 = sorted((ya, ya + ri * sy))
        st = box(x0, x1, y0, y1, z0, z1).cut(box(x0 + t, x1 - t, y0 + t, y1 - t, z0 - 1, z1 + 1))
        for dy in P["stuetze_m6_y"]:                       # M6 innen, Zugang außen
            y = ya + ri * dy
            for z in m6_z:
                st = st.cut(Part.makeCylinder(3.3, t + 2, V(x1 - t - 1, y, z), V(1, 0, 0)))
                st = st.cut(Part.makeCylinder(P["zugang_m6_d"] / 2, t + 2, V(x0 - 1, y, z), V(1, 0, 0)))
        if kopf:
            for dy in P["kopf_m5_y"]:                      # M5 außen in den Kopfzapfen
                st = st.cut(Part.makeCylinder(2.75, t + 2, V(x0 - 1, ya + ri * dy, z1 - P["kopf_m5_unter_ok"]),
                                              V(1, 0, 0)))
        else:                                              # Nietmuttern M5: Kabelkanal außen, Knoten vorn
            for dy in P["stuetze_kanal_y"]:
                for z in P["stuetze_kanal_z"]:
                    st = st.cut(Part.makeCylinder(P["nietmutter_m5_d"] / 2, t + 2, V(x0 - 1, ya + ri * dy, z),
                                                  V(1, 0, 0)))
            for x, z in P["stuetze_knoten"]:
                st = st.cut(Part.makeCylinder(P["nietmutter_m5_d"] / 2, t + 2, V(x, ya + ri * sy + 1, z),
                                              V(0, -1, 0)))
        res.append(st)
    return res


def stuetzen_kopf():
    """Druckkopf auf jedem Stützrohr: Zapfen im Rohr (2x M5-Mutter, von unten in
    Schlitze geschoben), Platte unter dem Träger (2x M6 von unten). Kopfüber druckbar."""
    g = geo()
    t, sp = P["stuetze_wand"], 0.2
    x1 = -P["rohr"] / 2
    xm = (g["r_x0"] + g["r_x1"]) / 2
    zo = P["traeger_uk"]
    zu = zo - P["kopf_h"]
    res = None
    for ya, ri, (sx, sy), _, _, _, kopf in stuetzen_lagen():
        if not kopf:
            continue
        x0 = x1 - sx
        y0, y1 = sorted((ya, ya + ri * P["kopf_y"]))
        k = box(min(xm - P["traeger_b"] / 2, x0), max(xm + P["traeger_b"] / 2, x1), y0, y1, zu, zo)
        r0, r1 = sorted((ya + ri * (t + sp), ya + ri * (sy - t - sp)))
        k = k.fuse(box(x0 + t + sp, x1 - t - sp, r0, r1, zu - P["kopf_zapfen"], zu + 0.01))
        zs = zu - P["kopf_m5_unter_ok"]
        xn = (x0 + x1) / 2                                   # Mutter in Zapfenmitte
        for dy in P["kopf_m5_y"]:
            y = ya + ri * dy
            k = k.cut(Part.makeCylinder(2.75, xn - x0 + 6, V(x0, y, zs), V(1, 0, 0)))
            k = k.cut(box(xn - 2.4, xn + 2.4, y - 4.15, y + 4.15, zu - P["kopf_zapfen"] - 1, zs + 4.8))
        for dx in (-10.0, 10.0):                              # M6 in den Träger
            k = k.cut(Part.makeCylinder(3.3, P["kopf_h"] + 2, V(xm + dx, ya + ri * P["traeger_m6_y"], zu - 1)))
        res = k if res is None else res.fuse(k)
    return res.removeSplitter()


# ---------------------------------------------------------------- Kettenturm (am Portal)
def bruecke_ende():
    """x-Lage der verlängerten Brückenstirn (ab Schienenmitte rechts)."""
    return geo()["a_x1"]


def ausleger():
    """Kettenturm: gerades Alu-Flachmaterial 40 x 8 an der Brückenstirn, ohne Laschen.
    Alles Weitere sitzt an Druckteilen, die mit M5 durch den Turm geschraubt werden."""
    g = geo()
    y0, y1 = P["ausleger_y"]
    t = P["ausleger_t"]
    z_top = g["z_mo"] + P["kette_h"] / 2
    s = box(g["a_x0"], g["a_x1"], y0, y1, P["bruecke_z"][0], z_top + P["hy_dicke"])
    for y, z in P["turm_loecher"]:
        s = s.cut(Part.makeCylinder(3.3, t + 2, V(g["a_x0"] - 1, y, z), V(1, 0, 0)))
    for y, z in turm_m5():
        s = s.cut(Part.makeCylinder(2.75, t + 2, V(g["a_x0"] - 1, y, z), V(1, 0, 0)))
    return s.removeSplitter()


def turm_m5():
    """Alle M5-Durchgänge im Turm (y, z): Halter Y, Ablagehalter X."""
    g = geo()
    z_top = g["z_mo"] + P["kette_h"] / 2
    res = [(y, z_top + P["hy_dicke"] / 2) for y in (-10.0, 10.0)]
    res += [(y, festhalter_zm()) for y in P["turm_x_y"]]
    return res


def m5_quer(x, y, z, richt, schlitz, laenge, tiefe=8.0):
    """M5 quer (x) ab der Fläche x in Richtung richt; Mutter tiefe dahinter,
    durch einen Schlitz in Richtung schlitz (Länge laenge) eingeschoben."""
    s = Part.makeCylinder(2.75, tiefe + 6, V(x - richt, y, z), V(richt, 0, 0))
    return s.fuse(fc_dok.mutter(5, V(x + richt * tiefe, y, z), V(1, 0, 0), schlitz, laenge))


def m5_senkrecht(x, y, z0, z1, z_mutter):
    """M5 senkrecht durch (z0..z1), Mutter an der Fläche bei z_mutter eingepresst."""
    s = Part.makeCylinder(2.75, z1 - z0 + 2, V(x, y, z0 - 1))
    return s.fuse(fc_dok.mutter(5, V(x, y, z_mutter), V(0, 0, 1)))


def halter_y():
    """Druckteil oben am Turm: das bewegte Ende der Y-Kette ist von unten mit 2x M5
    in eingepresste Muttern geschraubt; seitlich 2x M5 durch den Turm. Vorn zwei Schlitze für
    einen Kabelbinder, der die Leitung an der Biegung nach unten hält."""
    g = geo()
    z0 = g["z_mo"] + P["kette_h"] / 2
    x0, x1 = g["a_x1"], g["k_x1"] + 5
    s = box(x0, x1, P["hy_y"][0], P["hy_y"][1], z0, z0 + P["hy_dicke"])
    xc = (g["k_x0"] + g["k_x1"]) / 2
    hd = P["hy_dicke"]
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):                  # M5 von unten, Mutter oben
        s = s.cut(m5_senkrecht(xc + dx, sum(P["ausleger_y"]) / 2 + loch_versatz(), z0, z0 + hd, z0 + hd - 1.5))
    for y in (-10.0, 10.0):                                        # Turm: Mutter von oben
        s = s.cut(m5_quer(x0, y, z0 + hd / 2, 1, V(0, 0, 1), hd / 2 + 1))
    lx, _ = leitung_bei_y(26.0)
    for dx in (-12.0, 12.0):                                      # Kabelbinder 3,6 breit
        s = s.cut(box(lx + dx - 1.5, lx + dx + 1.5, 23.5, 28.5, z0 - 1, z0 + P["hy_dicke"] + 1))
    return s.removeSplitter()


def festhalter_zm():
    return geo_x()["z_t0"] + (P["traeger_h"] + P["rinne_t"]) / 2


def ablagehalter_x():
    """Druckteil auf Höhe der X-Ablage: Platte innen am Turm (2x M5 durch den Turm) mit
    einem Zapfen, auf den die Ablage geschoben wird (2x M5 von unten durch die untere
    Wand). Ablage und Rinne reichen bis an die Platte."""
    g, gx = geo(), geo_x()
    x0, x1 = g["a_x1"], ablage_x0()
    ymt = ym_traeger()
    z0, h = gx["z_t0"], P["traeger_h"]
    s = box(x0, x1, min(gx["r_y0"], P["ausleger_y"][0]), max(gx["r_y1"], P["ausleger_y"][1]), z0, gx["z_ku"])
    s = s.fuse(box(x1 - 0.01, x1 + P["xk_zapfen"], ymt - 17.8, ymt + 17.8, z0 + 2.2, z0 + h - 2.2))
    zm = festhalter_zm()
    for y in P["turm_x_y"]:                                        # Turm: Mutter von unten
        s = s.cut(m5_quer(x0, y, zm, 1, V(0, 0, -1), zm - z0 + 1))
    for x, y in zapfen_loecher():                                  # Zapfen: Mutter von der Seite
        s = s.cut(Part.makeCylinder(2.75, 15, V(x, y, z0 + 1)))
        sy = -1 if y < ymt else 1
        s = s.cut(fc_dok.mutter(5, V(x, y, z0 + 10), V(0, 0, 1), V(0, sy, 0), 9))
    return s.removeSplitter()


def ablage_x0():
    """Ende von X-Ablage und Rinne an der Kettenseite: direkt hinter der Platte des
    Ablagehalters am Turm (Ablage auf dessen Zapfen)."""
    return geo()["a_x1"] + P["xk_halter_dicke"]


def zapfen_loecher():
    gx = geo_x()
    ym = ym_traeger()
    x = ablage_x0() + P["xk_zapfen"] / 2
    return [(x, ym - 10.0), (x, ym + 10.0)]


def weg(pts, r):
    """Mittellinie aus Geraden mit Bögen an den Ecken (Radius r, oder je Ecke eine Liste
    mit einem Wert pro Punkt). Prüft, dass jede Gerade für die Bögen an ihren Enden lang
    genug ist."""
    n = len(pts)
    rs = list(r) if isinstance(r, (list, tuple)) else [r] * n
    d = [0.0] * n
    for i in range(1, n - 1):
        u = (pts[i - 1] - pts[i]).normalize()
        w = (pts[i + 1] - pts[i]).normalize()
        th = math.pi - math.acos(max(-1.0, min(1.0, u.dot(w))))   # Richtungsänderung
        d[i] = rs[i] * math.tan(th / 2)
    for i in range(n - 1):
        if d[i] + d[i + 1] > (pts[i + 1] - pts[i]).Length + 1e-6:
            raise ValueError("Leitungsweg: Gerade %d zu kurz (%.1f < %.1f)"
                             % (i, (pts[i + 1] - pts[i]).Length, d[i] + d[i + 1]))
    kanten, start = [], pts[0]
    for i in range(1, n - 1):
        a, p, b = pts[i - 1], pts[i], pts[i + 1]
        u = (a - p).normalize()
        w = (b - p).normalize()
        t1, t2 = p + u * d[i], p + w * d[i]
        bi = (u + w).normalize()
        th = math.acos(max(-1.0, min(1.0, u.dot(w))))
        c = p + bi * (rs[i] / math.sin(th / 2))
        if (t1 - start).Length > 1e-6:
            kanten.append(Part.LineSegment(start, t1).toShape())
        kanten.append(Part.Arc(t1, c - bi * rs[i], t2).toShape())
        start = t2
    if (pts[-1] - start).Length > 1e-6:
        kanten.append(Part.LineSegment(start, pts[-1]).toShape())
    return Part.Wire(kanten)


def leitung_ecken():
    """Eckpunkte und Radien der Bündelmitte (= Trennsteg zwischen den Pfaden) vom bewegten
    Y-Ende (Leitungen treten nach vorn aus) zum Festpunkt der X-Kette (treten dort zur
    Kettenseite ein): nach vorn, hoch, in einem Bogen über das Y-Kettenende nach hinten,
    seitlich versetzt, hinter der Ablage hinunter, in der Ablage hinten zur Gegenseite und
    mit einer Kehre in den Festpunkt."""
    g, gx = geo(), geo_x()
    r, rs = P["leitung_r"], P["leitung_r_s"]
    xc = (g["k_x0"] + g["k_x1"]) / 2
    e = P["end_laenge"] / 2
    yc = (gx["y0"] + gx["y1"]) / 2
    z_ein = gx["z_ku"] + P["kette_h"] / 2
    yh, zo, xa = P["leitung_hinten_y"], P["leitung_oben_z"], P["leitung_ab_x"]
    x_ein = gx["xf"] + e + 0.5
    x_kehre = x_ein + r + 2.0
    y_vor = bogen_y_vor()                                # Bogen nach oben direkt hinter dem Anschlussteil
    ys0, ys1 = P["leitung_s_y"]
    pts = [V(xc, e + 0.5, g["z_mo"]), V(xc, y_vor, g["z_mo"]), V(xc, y_vor, zo),
           V(xc, ys0, zo), V(xa, ys1, zo),
           V(xa, yh, zo), V(xa, yh, z_ein), V(x_kehre, yh, z_ein), V(x_kehre, yc, z_ein),
           V(x_ein, yc, z_ein)]
    return pts, [r, r, r, rs, rs, r, r, r, r, r]


def leitung_weg():
    return weg(*leitung_ecken())


def fach_mitten():
    """Lage der Pfadmitten (Brenner, Steuerung) quer zum Bündel ab dem Trennsteg."""
    st = P["fach_steg"] / 2
    return -(st + P["fach_b"][0] / 2), st + P["fach_b"][1] / 2


def _schnitt(p1, d1, p2, d2):
    """Mitte der kürzesten Verbindung zweier Geraden (Schnittpunkt, wenn sie sich schneiden)."""
    w0 = p1 - p2
    a, b, c = d1.dot(d1), d1.dot(d2), d2.dot(d2)
    dd, ee = d1.dot(w0), d2.dot(w0)
    n = a * c - b * b
    if abs(n) < 1e-12:
        return p1
    s, t = (b * ee - c * dd) / n, (a * ee - b * dd) / n
    return (p1 + d1 * s + p2 + d2 * t) * 0.5


def pfad_ecken(o):
    """Eckpunkte und Radien des Pfads im Abstand o (quer, Steuerung positiv) von der
    Bündelmitte, vor und nach dem Verdrillen. Die Querrichtung wandert mit dem Bündel:
    oben liegt die Steuerung zur Maschinenmitte, nach dem Bogen unten am Mast oben; in der
    Ablage hinten verdrillt das Bündel bis leitung_dreh_x um 90°, danach liegt die
    Steuerung vorn (innen in der Kehre). Bögen in der Ebene der Pfade: Radius um o
    kleiner bzw. größer."""
    pts, rad = leitung_ecken()
    i_dreh = 6                                           # Ecke unten am Mast, danach verdrillt
    n = len(pts)
    dirs = [(pts[j + 1] - pts[j]).normalize() for j in range(n - 1)]
    seite = [V(1, 0, 0)]                                 # am Y-Ende: Steuerung innen (+x)
    for j in range(1, n - 1):
        seite.append(App.Rotation(dirs[j - 1], dirs[j]).multVec(seite[-1]))
    t = dirs[i_dreh]
    s_vor = seite[i_dreh]
    s_nach = V(-t.y, t.x, 0).normalize()                 # nach dem Verdrillen: links der Laufrichtung
    seite[i_dreh] = s_nach
    for j in range(i_dreh + 1, n - 1):
        seite[j] = App.Rotation(dirs[j - 1], dirs[j]).multVec(seite[j - 1])

    def ecke(i):
        sn = s_vor if i == i_dreh else seite[i]
        q = _schnitt(pts[i - 1] + seite[i - 1] * o, dirs[i - 1], pts[i] + sn * o, dirs[i])
        u, w = -dirs[i - 1], dirs[i]
        bi = (u + w).normalize()
        ni = bi - w * bi.dot(w)
        return q, rad[i] - o * sn.dot(ni.normalize())

    a = pts[i_dreh] + t * rad[i_dreh]                    # Ende des Bogens unten (Bündelmitte)
    e = V(P["leitung_dreh_x"], a.y, a.z)
    vor = [pts[0] + seite[0] * o] + [ecke(i)[0] for i in range(1, i_dreh + 1)] + [a + s_vor * o]
    r_vor = [0.0] + [ecke(i)[1] for i in range(1, i_dreh + 1)] + [0.0]
    nach = [e + s_nach * o] + [ecke(i)[0] for i in range(i_dreh + 1, n - 1)] + [pts[-1] + seite[-1] * o]
    r_nach = [0.0] + [ecke(i)[1] for i in range(i_dreh + 1, n - 1)] + [0.0]
    return (vor, r_vor), (nach, r_nach), (a, e, s_vor, s_nach), seite[0]


def _rechteck(c, t, s, b, h):
    hv = t.cross(s).normalize()
    s = s.normalize()
    ps = [c + s * (b / 2) + hv * (h / 2), c - s * (b / 2) + hv * (h / 2),
          c - s * (b / 2) - hv * (h / 2), c + s * (b / 2) - hv * (h / 2)]
    return Part.makePolygon(ps + [ps[0]])


def _quer_zu(s, t):
    s = s - t * s.dot(t)
    return s.normalize()


def pfad(k):
    """Hüllkörper eines Pfads (k = 0 Brenner, 1 Steuerung): Rechteck fach_b x fach_h,
    entlang des Pfads geführt, im Verdrillstück als Loft um die Bündelmitte."""
    o = fach_mitten()[k]
    b, h = P["fach_b"][k], P["fach_h"]
    (vor, r_vor), (nach, r_nach), (a, e, sa, se), s0 = pfad_ecken(o)
    t0 = (vor[1] - vor[0]).normalize()
    p1 = weg(vor, r_vor).makePipeShell([_rechteck(vor[0], t0, s0, b, h)], True, False)
    t = (e - a).normalize()
    win = math.atan2(sa.cross(se).dot(t), sa.dot(se))
    profile = []
    for i in range(9):
        f = i / 8.0
        s = App.Rotation(t, math.degrees(win * f)).multVec(sa)
        profile.append(_rechteck(a + (e - a) * f + s * o, t, s, b, h))
    p2 = Part.makeLoft(profile, True, False)
    t2 = (nach[1] - nach[0]).normalize()
    p3 = weg(nach, r_nach).makePipeShell([_rechteck(nach[0], t2, se, b, h)], True, False)
    return Part.makeCompound([p1, p2, p3])


def leitung_punkt(y=None, x=None, z_min=None, z_max=None):
    """Punkt der Leitungsmittellinie und Richtung (waagerecht) an der Stelle y bzw. x."""
    pts = leitung_weg().discretize(Number=1500)
    kand = [i for i, q in enumerate(pts) if (z_min is None or q.z > z_min)
            and (z_max is None or q.z < z_max)]
    i = min(kand, key=lambda k: abs(pts[k].y - y) if y is not None else abs(pts[k].x - x))
    a, b = pts[max(i - 2, 0)], pts[min(i + 2, len(pts) - 1)]
    d = V(b.x - a.x, b.y - a.y, 0)
    return pts[i], d.normalize()


def buegel_lagen():
    """(Punkt auf der Unterlage unter dem Trennsteg, Richtung längs) aller Leitungsschellen.
    Die Steuerung liegt an allen Schellen links der Richtung."""
    zo, rd = P["leitung_oben_z"], P["fach_h"] / 2
    res = []
    for y in P["bg_oben_y"]:
        q, d = leitung_punkt(y=y, z_min=zo - 1)
        res.append((V(q.x, q.y, q.z - rd), d))
    z_ein = geo_x()["z_ku"] + P["kette_h"] / 2
    for x in P["bg_rinne_x"]:
        q, d = leitung_punkt(x=x, z_max=z_ein + 1)
        res.append((V(q.x, q.y, q.z - rd), d))
    return res


def _quer(p, d, dx, dy=0.0, dz=0.0):
    """Punkt p + dx quer zum Bündel (links von d) + dy längs + dz."""
    q = V(-d.y, d.x, 0)
    return V(p.x + q.x * dx + d.x * dy, p.y + q.y * dx + d.y * dy, p.z + dz)


def schelle_mass():
    """Quermaße der Schelle ab dem Trennsteg (links = Steuerung positiv)."""
    st, sp, sk = P["fach_steg"] / 2, P["bg_spiel"], P["bg_schenkel"]
    xb, xs = -(st + P["fach_b"][0] + sp), st + P["fach_b"][1] + sp
    return dict(xb=xb, xs=xs, x0=xb - sk, x1=xs + sk, m3=(xb - sk / 2, xs + sk / 2),
                h=P["fach_h"] + sp)


def _platziert(s, p, d):
    """Lokal x quer (links von d), y längs, z ab der Unterlage -> Lage der Schelle."""
    s.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(math.atan2(d.y, d.x)) + 90.0)
    s.translate(p)
    return s


def leitungsschellen():
    """Zwei Tunnel mit Mittelsteg über den Pfaden, je 1x M3 durch die Schenkel."""
    m, l, t = schelle_mass(), P["bg_l"] / 2, P["bg_dach"]
    st = P["bg_steg"] / 2
    res = []
    for p, d in buegel_lagen():
        s = box(m["x0"], m["x1"], -l, l, 0, m["h"] + t)
        s = s.cut(box(m["xb"], -st, -l - 1, l + 1, -1, m["h"]))
        s = s.cut(box(st, m["xs"], -l - 1, l + 1, -1, m["h"]))
        for x in m["m3"]:
            s = s.cut(Part.makeCylinder(1.7, m["h"] + t + 2, V(x, 0, -1)))
        res.append(_platziert(s, p, d))
    s = res[0].copy()                                   # am senkrechten Lauf (Umlenkkopf)
    p, d = buegel_lagen()[0]
    s.translate(-p)
    s.rotate(V(0, 0, 0), V(0, 0, 1), -(math.degrees(math.atan2(d.y, d.x)) + 90.0))
    s.transformShape(schelle_senkrecht())             # starr, bleibt deckungsgleich
    res.append(s)
    return res


def schelle_fuss(i, h, l=None):
    """Unterlage unter der Schelle i (Fläche der Schelle, Höhe h nach unten)."""
    p, d = buegel_lagen()[i]
    m = schelle_mass()
    l = (P["bg_l"] / 2 + 1.0) if l is None else l
    return _platziert(box(m["x0"], m["x1"], -l, l, -h, 0), p, d)


def buegel_bohrungen(teil, art, nur):
    """M3 der Schellen in die Unterlage: Muttern 8 mm unter der Auflage, seitlich nach außen
    eingeschoben ("seite") oder von unten eingepresst ("unten", Verbindungsplatte)."""
    m = schelle_mass()
    lagen = buegel_lagen()
    for i in nur:
        p, d = lagen[i]
        q = V(-d.y, d.x, 0)
        for x in m["m3"]:
            c = _quer(p, d, x)
            teil = teil.cut(Part.makeCylinder(1.7, 14, V(c.x, c.y, p.z - 13)))
            if art == "seite":
                sx = 1 if x > 0 else -1
                teil = teil.cut(fc_dok.mutter(3, V(c.x, c.y, p.z - 8.0), V(0, 0, 1), q * sx,
                                              P["bg_schenkel"] / 2 + 2.0))
            elif art == "unten":
                teil = teil.cut(fc_dok.mutter(3, V(c.x, c.y, p.z - P["vp_t"] + 1.3), V(0, 0, 1)))
    return teil


def schelle_einzeln():
    """Eine Schelle in Druckbett-Lage (Dach unten)."""
    s = leitungsschellen()[0].copy()
    p, d = buegel_lagen()[0]
    s.translate(-p)
    s.rotate(V(0, 0, 0), V(0, 0, 1), -(math.degrees(math.atan2(d.y, d.x)) + 90.0))
    s.rotate(V(0, 0, 0), V(1, 0, 0), 180.0)
    return s


def leitungssockel():
    """Druckteile in der Ablage hinten unter den beiden Schellen: heben die Pfade auf die
    Höhe der X-Kette; 2x M3 von unten durch die Ablage in Muttern (von unten eingepresst)."""
    lagen = buegel_lagen()
    z_r = rinne_hinten_z() + P["rh_t"]
    res = []
    for i in range(len(P["bg_oben_y"]), len(lagen)):
        p, d = lagen[i]
        s = schelle_fuss(i, p.z - z_r, P["sockel_l"] / 2)
        s = buegel_bohrungen(s, "seite", [i])
        for dy in (-P["sockel_m3_dy"], P["sockel_m3_dy"]):
            c = _quer(p, d, 0.0, dy)
            s = s.cut(Part.makeCylinder(1.7, 10, V(c.x, c.y, z_r - 1)))
            s = s.cut(fc_dok.mutter(3, V(c.x, c.y, z_r + 1.3), V(0, 0, 1)))
        res.append(s)
    return res


def sockel_loecher():
    lagen = buegel_lagen()
    return [_quer(p, d, 0.0, dy) for p, d in lagen[len(P["bg_oben_y"]):]
            for dy in (-P["sockel_m3_dy"], P["sockel_m3_dy"])]


def bogen_y_vor():
    return P["end_laenge"] / 2 + 0.5 + P["leitung_r"] + 5.0


def zyl_x(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def leitungsbogen():
    """Druckteil auf dem Halter Y: die Leitungen treten am bewegten Kettenende nach vorn
    aus und laufen innen um diesen Bogen (R60 Mittellinie) hoch und zurück nach hinten.
    Wangen links und rechts halten das Bündel, Kabelbinder durch zwei Schlitze. Befestigt
    mit den beiden M5 des Kettenendes (länger, von unten durch Anschlussteil, Halter und
    Bogen, Muttern seitlich eingeschoben)."""
    g = geo()
    r = P["leitung_r"]
    xc = (g["k_x0"] + g["k_x1"]) / 2
    yv = bogen_y_vor()
    cy, z1, z2 = yv - r, g["z_mo"] + r, P["leitung_oben_z"] - r
    ri = r - P["fach_h"] / 2
    b, wt, wr = P["fuehrung_b"] / 2, P["wange_t"], P["wange_r"]
    z_h = g["z_mo"] + P["kette_h"] / 2 + P["hy_dicke"]   # Oberkante Halter Y
    yb = P["hy_y"][0]
    xa0, xa1 = xc - b - wt, xc + b + wt

    def stadion(rad, x0, x1):
        s = zyl_x(rad, x0, x1, cy, z1).fuse(zyl_x(rad, x0, x1, cy, z2))
        s = s.fuse(box(x0, x1, cy - rad, cy + rad, z1, z2))
        return s.common(box(x0 - 1, x1 + 1, cy, cy + rad + 1, z1 - rad - 1, z2 + rad + 1))

    kern = stadion(ri, xc - b, xc + b).fuse(box(xc - b, xc + b, yb, cy, z_h, z2 + ri))
    st = P["fach_steg"] / 2
    kern = kern.fuse([stadion(ri + 8.0, xc - st, xc + st),         # Trennsteg zwischen den Pfaden
                      schelle_fuss(0, 12.0)])                       # Auflage der Schelle
    # Wangen = ganze Seitenplatten (Bogen und Kern), außen bündig mit der Schellenauflage:
    # die Hälften werden auf der Wange liegend gedruckt
    fb = kern.BoundBox
    xa0, xa1 = min(xa0, fb.XMin), max(xa1, fb.XMax)
    w = stadion(wr, xa0, xa1).fuse(box(xa0, xa1, yb, cy, z_h, z2 + ri))
    w = w.cut(box(xc - b, xc + b, yb - 1, cy + wr + 1, z1 - wr - 1, z2 + wr + 1))
    s = kern.fuse(w)
    s = s.cut(box(xa0 - 1, xa1 + 1, yb - 1, P["hy_y"][1] + 0.5, z1 - wr - 1, z_h))   # Halter Y
    zv = z2 + ri - P["vp_t"]                                            # Verbindungsplatte
    s = s.cut(box(xc - b - 1, xa1 + 1, yb - 1, P["vp_y"][1], zv, z2 + ri + 1))
    for dx, y in P["vp_m4_bogen"]:
        s = s.cut(Part.makeCylinder(2.25, 16, V(xc + dx, y, zv - 15)))
        s = s.cut(fc_dok.mutter(4, V(xc + dx, y, zv - 8.0), V(0, 0, 1), V(0, -1, 0), y - yb + 1))
    s = buegel_bohrungen(s, "seite", [0])
    lx, _ = leitung_bei_y(26.0)
    s = s.cut(box(lx - 15, lx + 15, 22.0, 30.0, z_h - 1, z_h + 2.5))   # Kabelbinder im Halter Y
    for z in (z1 - 15.0, z2 + 15.0):                                    # Kabelbinder um das Bündel
        s = s.cut(box(xa0 - 1, xa1 + 1, cy + ri - 15.0, cy + ri - 12.0, z - 2.5, z + 2.5))
    yl = sum(P["ausleger_y"]) / 2 + loch_versatz()
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):                        # M5 des Kettenendes
        x = xc + dx
        s = s.cut(Part.makeCylinder(2.75, 25, V(x, yl, z_h - 1)))
        sx = 1 if dx > 0 else -1
        s = s.cut(fc_dok.mutter(5, V(x, yl, z_h + 15), V(0, 0, 1), V(sx, 0, 0), max(xa1 - x, x - xa0) + 2))
    yq = cy + 20.0                                                      # M3 quer durch alle drei Teile
    for z in (z1 - 17.5, z2 + 20.0):
        s = m3_quer_durch(s, xa0, xa1, yq, z)
    return s.removeSplitter()


def m3_quer_durch(s, x0, x1, y, z):
    """M3 quer (x) durch dreiteilige Führung: Kopf gesenkt bei x0, Mutter in Tasche bei x1."""
    s = s.cut(Part.makeCylinder(1.7, x1 - x0 + 2, V(x0 - 1, y, z), V(1, 0, 0)))
    s = s.cut(Part.makeCylinder(3.2, 3.5, V(x0 - 1, y, z), V(1, 0, 0)))           # Zylinderkopf
    return s.cut(fc_dok.mutter(3, V(x1 - 1.0, y, z), V(1, 0, 0)))                 # Mutter außen


def dreiteilig(s, xm):
    """Teilt eine Führung am Trennsteg (xm +- fach_steg/2): zwei Hälften mit je einer Wange
    (auf der Wange liegend gedruckt) und der Trennsteg als flache Scheibe dazwischen."""
    st = P["fach_steg"] / 2
    bb = s.BoundBox
    def teil(x0, x1):
        return s.common(box(x0, x1, bb.YMin - 1, bb.YMax + 1, bb.ZMin - 1, bb.ZMax + 1)).removeSplitter()
    return [teil(bb.XMin - 1, xm - st), teil(xm - st, xm + st), teil(xm + st, bb.XMax + 1)]


def mast():
    """Alu-Flachstange 40 x 8 hinter der Ablage hinten: unten 2x M4 in Gewinde in deren
    hinterer Stirn, oben der Umlenkkopf (2x M4), darunter das Distanzstück (2x M4)."""
    yh, xa = P["leitung_hinten_y"], P["leitung_ab_x"]
    mb, mt = P["mast"]
    xm = xa + P["mast_dx"]
    z0 = rinne_hinten_z()
    y1 = yh - 20.0
    s = box(xm - mb / 2, xm + mb / 2, y1 - mt, y1, z0, P["mast_oben"])
    for dx in (-P["mast_m4_dx"], P["mast_m4_dx"]):
        s = s.cut(Part.makeCylinder(2.25, mt + 2, V(xm + dx, y1 - mt - 1, z0 + P["rh_t"] / 2), V(0, 1, 0)))
    for z in P["kopf_m4_z"]:
        s = s.cut(Part.makeCylinder(2.25, mt + 2, V(xa + P["kopf_m4_dx"], y1 - mt - 1, z), V(0, 1, 0)))
    for z in P["dist_m4_z"]:                      # Distanzstück
        s = s.cut(Part.makeCylinder(2.25, mt + 2, V(xa + P["kopf_m4_dx"], y1 - mt - 1, z), V(0, 1, 0)))
    for dx in (-P["mast_m4_dx"], P["mast_m4_dx"]):          # Versteifungswinkel oben: Gewinde M4
        s = s.cut(Part.makeCylinder(1.65, mt + 2, V(xm + dx, y1 - mt - 1, z0 + P["mw_m4_oben_z"]),
                                    V(0, 1, 0)))
    return s


def mastwinkel():
    """Versteifungswinkel (Druck) außen an der Ecke Mast / Ablage hinten: Schenkel hinter
    dem Mast, Bodenplatte unter Mast und Ablage, zwei Rippen nach hinten. Die beiden M4 des
    Masts in die Ablagestirn gehen länger auch durch den Schenkel, oben 2x M4 in Gewinde im
    Mast, unten 2x M4 von unten in Gewinde in der Ablage. Auf der Bodenplatte stehend
    stützenfrei druckbar."""
    yh, xa = P["leitung_hinten_y"], P["leitung_ab_x"]
    mt = P["mast"][1]
    t, h, tief, rb = P["mw_t"], P["mw_h"], P["mw_tief"], P["mw_rippe"]
    x0, x1 = P["mw_x"]
    z0 = rinne_hinten_z()
    yr = yh - 20.0 - mt                                     # Rückseite Mast
    yv = yh + 20.0                                          # Vorderkante Ablage
    s = box(x0, x1, yr - t - tief, yv, z0 - t, z0)          # Bodenplatte
    s = s.fuse(box(x0, x1, yr - t, yr, z0 - t, z0 + h))     # Schenkel
    for xr in (x0, x1 - rb):                                # Rippen
        tri = Part.Face(Part.makePolygon([V(xr, yr - t, z0 + h), V(xr, yr - t, z0),
                                          V(xr, yr - t - tief, z0), V(xr, yr - t, z0 + h)]))
        s = s.fuse(tri.extrude(V(rb, 0, 0)))
    xm = xa + P["mast_dx"]
    for dx in (-P["mast_m4_dx"], P["mast_m4_dx"]):
        for z in (z0 + P["rh_t"] / 2, z0 + P["mw_m4_oben_z"]):
            s = s.cut(Part.makeCylinder(2.25, t + 2, V(xm + dx, yr - t - 1, z), V(0, 1, 0)))
    for y in P["mw_m4_ablage_y"]:
        s = s.cut(Part.makeCylinder(2.25, t + 2, V(xm, y, z0 - t - 1)))
    return s.removeSplitter()


def distanzstueck():
    """Druckteil auf dem Mast unter dem Umlenkkopf: füllt den Abstand vom Mast bis hinter die
    Leitungen (Auflage wie die Rückwand des Kopfs), zwei Kanäle quer für Kabelbinder um das
    Bündel. Rechts nicht breiter als die Leitungen (Y-Kette). 2x M4 von hinten durch den Mast,
    Muttern von links eingeschoben."""
    xa, yh = P["leitung_ab_x"], P["leitung_hinten_y"]
    mb, mt = P["mast"]
    y1 = yh - 20.0                                # Vorderseite Mast
    y2 = yh - P["fach_h"] / 2                     # Rückseite der Leitungen
    x0 = xa - P["fach_steg"] / 2 - P["fach_b"][0]
    x1 = xa + P["mast_dx"] + mb / 2
    z0, z1 = P["dist_z"]
    s = box(x0, x1, y1, y2, z0, z1)
    for z in P["dist_kb_z"]:
        s = s.cut(box(x0 - 1, x1 + 1, y1 + 3.0, y1 + 6.0, z - 2.5, z + 2.5))
    xm4 = xa + P["kopf_m4_dx"]
    for z in P["dist_m4_z"]:
        s = s.cut(Part.makeCylinder(2.25, y2 - y1 - 1.5, V(xm4, y1 - 0.01, z), V(0, 1, 0)))
        s = s.cut(fc_dok.mutter(4, V(xm4, y1 + 6.5, z), V(0, 1, 0), V(1, 0, 0), x1 - xm4 + 1))
    return s


def schelle_senkrecht():
    """Lage der Schelle am senkrechten Lauf vor der Rückwand des Umlenkkopfs: Matrix
    lokal (x quer, Steuerung positiv; y längs; z ab der Unterlage) -> Modell."""
    xa, yh = P["leitung_ab_x"], P["leitung_hinten_y"]
    p = V(xa, yh - P["fach_h"] / 2, P["schelle_senk_z"])
    return App.Matrix(1, 0, 0, p.x, 0, 0, 1, p.y, 0, -1, 0, p.z, 0, 0, 0, 1)


def umlenkkopf():
    """Druckteil oben am Mast, aus einem Stück: die Leitungen kommen oben von vorn und
    laufen innen um diesen Bogen (R60) senkrecht hinunter in die Rinne hinten. Rückwand am
    Mast (2x M4, Muttern seitlich eingeschoben), Wange auf der Gegenseite, zur Kettenseite
    offen (Leitungen von der Seite einlegen). Am senkrechten Lauf hält eine Leitungsschelle
    die Pfade an der Rückwand, die dafür oberhalb der Y-Kette nach rechts verbreitert ist;
    darunter ein Kabelbinder. Unten vorn im Bogen ausgeschnitten. Auf der Wange liegend
    stützenfrei druckbar."""
    r, hh = P["leitung_r"], P["fach_h"] / 2
    yh, xa, zo = P["leitung_hinten_y"], P["leitung_ab_x"], P["leitung_oben_z"]
    ri = r - hh
    b, wt = P["fuehrung_b"] / 2, P["wange_t"]
    cy, cz = yh + r, zo - r
    ys1 = P["leitung_s_y"][1]
    y_rw = yh - 20.0                                     # Rückseite = Vorderseite Mast
    z_u = min(P["kopf_m4_z"]) - 30.0
    m = schelle_mass()
    kern = zyl_x(ri, xa - b, xa + b, cy, cz).common(box(xa - b, xa + b, cy - ri, cy, cz, cz + ri))
    kern = kern.fuse(box(xa - b, xa + b, cy, ys1 + 5.0, cz, cz + ri))
    rw = box(xa - 15.0, xa + b, y_rw, yh - hh, z_u, P["mast_oben"])
    rw = rw.fuse(box(xa + m["x0"] - 1.0, xa - 14.0, y_rw, yh - hh, P["kopf_breit_z"], P["mast_oben"]))
    fu = schelle_fuss(2, 12.0).BoundBox
    xw = max(xa + b + wt + 2.0, fu.XMax, xa + m["x1"] + 1.0)            # außen bündig mit den Schellen
    wa = box(xa + b, xw, y_rw, cy, z_u, zo + hh + 5.0)                  # Wange = ganze Seitenplatte,
    wa = wa.fuse(box(xa + b, xw, cy, ys1 + 5.0, z_u, cz + ri))          # vorn nur bis unter die Schelle
    s = kern.fuse([rw, wa, schelle_fuss(2, 12.0)]).removeSplitter()
    # unten vorn unter dem Bogen weg: Viertelkreis um die vordere untere Ecke, endet vorn an
    # der Unterseite des Kerns und unten 10 mm vor den Leitungen
    rb = cz - z_u
    s = s.cut(Part.makeCylinder(rb, xw - xa + b + 2, V(xa - b - 1, ys1 + 5.0, z_u), V(1, 0, 0)))
    zv = cz + ri - P["vp_t"]                                            # Verbindungsplatte
    s = s.cut(box(xa - b - 1, xa + b, P["vp_y"][0], ys1 + 6.0, zv, cz + ri + 1))
    for dx, y in P["vp_m4_kopf"]:
        s = s.cut(Part.makeCylinder(2.25, 16, V(xa + dx, y, zv - 15)))
        s = s.cut(fc_dok.mutter(4, V(xa + dx, y, zv - 8.0), V(0, 0, 1), V(0, 1, 0), ys1 + 5.0 - y + 1))
    xm4 = xa + P["kopf_m4_dx"]
    for z in P["kopf_m4_z"]:
        s = s.cut(Part.makeCylinder(2.25, 12, V(xm4, y_rw - 1, z), V(0, 1, 0)))
        s = s.cut(fc_dok.mutter(4, V(xm4, y_rw + 6.0, z), V(0, 1, 0), V(1, 0, 0), xw - xm4 + 1))
    s = buegel_bohrungen(s, "seite", [2])
    # Schelle am senkrechten Lauf: Platz in der Wange, M3 in die Rückwand, Muttern seitlich
    t = schelle_senkrecht()
    l = P["bg_l"] / 2 + 0.3
    tasche = box(m["x0"] - 0.3, m["x1"] + 0.3, -l, l, 0, m["h"] + P["bg_dach"] + 1)
    tasche.transformShape(t)
    s = s.cut(tasche)
    for x in m["m3"]:
        sx = 1 if x > 0 else -1
        s = s.cut(Part.makeCylinder(1.7, 14, V(x, 0, -13)).transformGeometry(t))
        s = s.cut(fc_dok.mutter(3, t.multiply(V(x, 0, -8.0)), t.multiply(V(0, 0, 1)) - t.multiply(V(0, 0, 0)),
                                V(sx, 0, 0), P["bg_schenkel"] / 2 + 6.0))
    z = z_u + 15.0                                                      # Kabelbinder um das Bündel
    s = s.cut(box(xa - 16, xw + 1, y_rw + 3.0, y_rw + 6.0, z - 2.5, z + 2.5))
    return s.removeSplitter()


def verbindungsplatte():
    """Druckteil zwischen Leitungsbogen und Umlenkkopf: Oberseite = Unterseite der
    Leitungen, liegt an beiden Enden in einer Aussparung, je 2x M4 (Zylinderkopf versenkt)."""
    g = geo()
    xc = (g["k_x0"] + g["k_x1"]) / 2
    xa = P["leitung_ab_x"]
    b = P["fuehrung_b"] / 2
    z1 = P["leitung_oben_z"] - P["fach_h"] / 2
    z0 = z1 - P["vp_t"]
    s = box(xc - b, xa + b, P["vp_y"][0], P["vp_y"][1], z0, z1)
    for x0, pts in ((xc, P["vp_m4_bogen"]), (xa, P["vp_m4_kopf"])):
        for dx, y in pts:
            s = s.cut(Part.makeCylinder(2.25, P["vp_t"] + 2, V(x0 + dx, y, z0 - 1)))
            s = s.cut(Part.makeCylinder(4.0, 5.5, V(x0 + dx, y, z1 - 4.5)))   # Zylinderkopf M4 versenkt
    return buegel_bohrungen(s, "unten", [1])


def rinne_hinten_z():
    """Unterkante der Ablage hinten. Oberseite unter dem Brennerpfad, der nach dem Bogen am
    Mast unten liegt (Pfade übereinander) und beim Verdrillen mit der Kante tiefer kommt."""
    gx = geo_x()
    rk = math.hypot(P["fach_steg"] / 2 + P["fach_b"][0], P["fach_h"] / 2)
    return gx["z_ku"] + P["kette_h"] / 2 - rk - P["bg_spiel"] - P["rh_t"]


def brenner_weg():
    """Adern des Brennerpakets vom bewegten X-Ende (treten zur Gegenseite aus) zum
    Brenner, X-Wagen-Koordinaten, Z unten: hoch, über einen Bogen nach vorn und von
    oben in die Tülle. Bei Z oben wird die Schlaufe 100 mm länger und wölbt sich."""
    gx = geo_x()
    r = P["leitung_r"]
    zb = P["bruecke_uk_x_wagen"]
    yc = (gx["y0"] + gx["y1"]) / 2
    z_aus = gx["z_mo"] - zb
    x_aus = P["xk_halter_dx"] + P["end_laenge"] / 2 + 0.5
    xa = x_aus + r + 2.0
    zo, yb = P["brenner_oben_z"], P["brenner_y"]
    pts = [V(x_aus, yc, z_aus), V(xa, yc, z_aus), V(xa, 30.0, zo), V(0, yb, zo),
           V(0, yb, P["brenner_stummel_z"])]
    return weg(pts, r)


def leitung_abtasten(n=200):
    return leitung_weg().discretize(Number=n)


def leitung_bei_y(y):
    pts = leitung_abtasten()
    p = min(pts[:len(pts) // 6], key=lambda q: abs(q.y - y))
    return p.x, p.z


def rohr(w, d):
    """Hüllkurve der Leitungen als Rohr entlang der Mittellinie (Darstellung, Kollision)."""
    e0 = w.OrderedEdges[0]
    p0 = e0.valueAt(e0.FirstParameter)
    t0 = e0.tangentAt(e0.FirstParameter)
    kreis = Part.Wire([Part.makeCircle(d / 2, p0, t0)])
    return w.makePipeShell([kreis], True, True)


def leitung():
    return Part.makeCompound([pfad(0), pfad(1)])


def brenner_leitung():
    return rohr(brenner_weg(), P["brenner_leitung_d"])


def rinne_hinten():
    """Alu-Winkel 40 x 20 x 2 hinter der Ablage: waagerechter Schenkel unter den
    Leitungen, senkrechter Schenkel hinten; von der Kettenseite bis vor die Kehre."""
    gx = geo_x()
    yh = P["leitung_hinten_y"]
    z0, t = rinne_hinten_z(), P["rh_t"]
    x0 = P["leitung_ab_x"] - 15.0
    x1 = gx["xf"] + P["end_laenge"] / 2 + 2.0
    s = box(x0, x1, yh - 20.0, yh + 20.0, z0, z0 + t)
    for x in rh_halter_xs():                             # M4 in die Rinnenhalter
        s = s.cut(Part.makeCylinder(2.25, t + 2, V(x + P["rh_halter_b"] / 2, yh, z0 - 1)))
    for c in sockel_loecher():                           # M3 von unten in die Leitungssockel
        s = s.cut(Part.makeCylinder(1.7, t + 2, V(c.x, c.y, z0 - 1)))
    xm = P["leitung_ab_x"] + P["mast_dx"]
    for dx in (-P["mast_m4_dx"], P["mast_m4_dx"]):       # M4 Mast: Gewinde in der hinteren Stirn
        s = s.cut(Part.makeCylinder(1.65, 11, V(xm + dx, yh - 21.0, z0 + t / 2), V(0, 1, 0)))
    for y in P["mw_m4_ablage_y"]:                         # M4 Versteifungswinkel von unten
        s = s.cut(Part.makeCylinder(1.65, t + 2, V(xm, y, z0 - 1)))
    return s


def rinnenhalter():
    """Druckteile unter der Ablage: tragen die Ablage hinten (je 2x M5 von unten in
    Nietmuttern der Ablage, Ablage hinten mit 1x M4 in eine Mutter, seitlich eingeschoben).
    L-Profil: Platte unter der Ablage, dahinter hoch bis zur Ablage hinten. Der letzte
    sitzt unter dem festen Kettenende und reicht hinter der Ablage bis unter die Rinne
    (hinteres M5 des Kettenendes in eine seitlich eingeschobene Mutter)."""
    gx = geo_x()
    ym = ym_traeger()
    yh = P["leitung_hinten_y"]
    z_r = rinne_hinten_z()
    z0 = gx["z_t0"] - 8.0
    b = P["rh_halter_b"]
    y_tr = ym - 20.0                                     # Rückseite der Ablage
    yc = (gx["y0"] + gx["y1"]) / 2
    y_fest = [yc + dy for dy in (-P["end_C"] / 2, P["end_C"] / 2) if abs(yc + dy - ym) >= 18.0]
    res = None
    for i, x in enumerate(rh_halter_xs()):
        s = box(x, x + b, yh - 20.0, ym + 20.0, z0, gx["z_t0"])            # unter der Ablage
        s = s.fuse(box(x, x + b, yh - 20.0, y_tr, gx["z_t0"] - 0.01, z_r))  # hoch zur Ablage hinten
        if i == len(rh_halter_xs()) - 1:
            s = s.fuse(box(x, x + b, gx["r_y0"], y_tr, gx["z_t0"] - 0.01, gx["z_ri"]))   # unter der Rinne
            for y in y_fest:
                s = s.cut(Part.makeCylinder(2.75, 16, V(x + b / 2, y, gx["z_ri"] - 15)))
                s = s.cut(fc_dok.mutter(5, V(x + b / 2, y, gx["z_ri"] - 8), V(0, 0, 1), V(1, 0, 0), b / 2 + 1))
        for y in (ym - 10.0, ym + 10.0):                               # M5 von unten, Nietmutter in der Ablage
            s = s.cut(Part.makeCylinder(2.75, 10, V(x + b / 2, y, z0 - 1)))
        s = s.cut(Part.makeCylinder(2.25, 12, V(x + b / 2, yh, z_r - 11)))
        s = s.cut(fc_dok.mutter(4, V(x + b / 2, yh, z_r - 6), V(0, 0, 1), V(1, 0, 0), b / 2 + 1))
        res = s if res is None else res.fuse(s)
    return res.removeSplitter()


def einsteckteil():
    """Steckt in der Brücke (rechts), gehalten von den beiden M6 des Sattels;
    Stirnseite mit 4x M6 für den Kettenturm (Muttern seitlich eingeschoben)."""
    g = geo()
    w, tb = P["bruecke_wand"], P["bruecke_tiefe"]
    za, zb = P["bruecke_z"]
    sp = 0.2
    x0, x1 = g["a_x1"], P["einsteck_innen"]
    s = box(x0, x1, -tb / 2 + w + sp, tb / 2 - w - sp, za + w + sp, zb - w - sp)
    for x in P["m6_x"]:
        for z in P["m6_z"]:
            s = s.cut(Part.makeCylinder(3.3, tb, V(x, -tb / 2, z), V(0, 1, 0)))
    for y, z in P["turm_loecher"]:                     # M6, Mutter seitlich eingeschoben
        s = s.cut(Part.makeCylinder(3.3, 20, V(x0 - 1, y, z), V(1, 0, 0)))
        s = s.cut(fc_dok.mutter(6, V(x0 + 10, y, z), V(1, 0, 0), V(0, 1 if y > 0 else -1, 0), 9))
    return s.removeSplitter()


# ---------------------------------------------------------------- X-Kette
def geo_x():
    h, b, R = P["kette_h"], P["kette_b"], P["xk_radius"]
    y1 = P["xk_y_vorn"]
    y0 = y1 - b
    t, rl = P["rinne_t"], P["rinne_luft"]
    z_t0 = P["xk_traeger_uk"]
    z_ri = z_t0 + P["traeger_h"]
    z_ku = z_ri + t
    z_mu = z_ku + h / 2
    z_mo = z_mu + 2 * R
    xs = -20.0                                           # Rahmen-x -> x ab Schienenmitte rechts
    m0 = P["xk_wagen_x"][0] + P["xk_halter_dx"] + xs
    m1 = P["xk_wagen_x"][1] + P["xk_halter_dx"] + xs
    laenge = P["xk_glieder"] * P["teilung"] + P["end_laenge"]
    l_eff = laenge - math.pi * R
    xf = m0 - P["xk_reserve"] + l_eff                    # Schlaufe bei X rechts xk_reserve/2 neben dem Ende
    if m1 - xf > l_eff:
        raise ValueError("X-Kette zu kurz")
    return dict(y0=y0, y1=y1, z_t0=z_t0, z_ri=z_ri, z_ku=z_ku, z_mu=z_mu, z_mo=z_mo,
                m0=m0, m1=m1, xf=xf, l_eff=l_eff, laenge=laenge, xs=xs,
                r_y0=y0 - rl - t, r_y1=y1 + rl + t, x_re=P["xk_bruecke_links_x"] + xs)


def ym_traeger():
    """Mitte der X-Ablage in y: bündig mit Platte und Turm (Brückentiefe)."""
    return sum(P["ausleger_y"]) / 2


def x_fest_loch():
    """x der Bohrungen des festen X-Kettenendes."""
    return geo_x()["xf"] + loch_versatz()


def rh_halter_xs():
    """Rinnenhalter (x der linken Kante); der letzte unter dem festen Kettenende."""
    return P["rh_halter_x"] + [x_fest_loch() - P["rh_halter_b"] / 2]


def stopfen_loecher():
    gx = geo_x()
    zm = gx["z_t0"] + P["traeger_h"] / 2
    return [(ym_traeger() - 10.0, zm), (ym_traeger() + 10.0, zm)]


def ablage_x():
    """Alu 40x20x2 flach (in y 40 breit, bündig mit Platte und Turm) + Rinne, an der
    Kettenseite auf dem Zapfen des Ablagehalters, an der Gegenseite stumpf an der Platte
    (Stopfen mit M5-Muttern). Die Rinne steht hinten über die Ablage über und endet
    hinter dem festen Kettenende (2x M5 durch den Rinnenboden: vorn in eine Nietmutter
    der Ablage, hinten in den Rinnenhalter); dahinter liegt die Kehre der Leitungen."""
    gx = geo_x()
    x0 = ablage_x0()
    x1 = gx["x_re"]
    ym = ym_traeger()
    z0 = gx["z_t0"]
    tr = box(x0, x1, ym - 20, ym + 20, z0, z0 + P["traeger_h"])
    tr = tr.cut(box(x0 - 1, x1 + 1, ym - 18, ym + 18, z0 + 2, z0 + P["traeger_h"] - 2))
    for x, y in zapfen_loecher():                                  # M5 von unten in den Zapfen
        tr = tr.cut(Part.makeCylinder(2.75, 4, V(x, y, z0 - 1)))
    for x in rh_halter_xs():                                       # Nietmuttern M5 für die Rinnenhalter
        for y in (ym - 10.0, ym + 10.0):
            tr = tr.cut(Part.makeCylinder(3.5, 4, V(x + P["rh_halter_b"] / 2, y, z0 - 1)))
    yc = (gx["y0"] + gx["y1"]) / 2
    for dy in (-P["end_C"] / 2, P["end_C"] / 2):                  # Nietmutter M5 für das feste Kettenende
        if abs(yc + dy - ym) < 18.0:                               # (das hintere M5 geht in den Rinnenhalter)
            tr = tr.cut(Part.makeCylinder(3.5, 4, V(x_fest_loch(), yc + dy, z0 + P["traeger_h"] - 3)))
    t = P["rinne_t"]
    xr = gx["xf"] + P["end_laenge"] / 2
    ri = box(x0, xr, gx["r_y0"], gx["r_y1"], gx["z_ri"], gx["z_ri"] + t)
    for y0 in (gx["r_y0"], gx["r_y1"] - t):
        ri = ri.fuse(box(x0, xr, y0, y0 + t, gx["z_ri"], gx["z_ri"] + P["rinne_rand"]))
    yc = (gx["y0"] + gx["y1"]) / 2
    for dy in (-P["end_C"] / 2, P["end_C"] / 2):                  # festes Kettenende
        ri = ri.cut(Part.makeCylinder(2.75, t + 2, V(gx["xf"] + loch_versatz(), yc + dy, gx["z_ri"] - 1)))
    return tr, ri.removeSplitter()


def stopfen_x():
    """Stopfen (Druck) im linken Ende der X-Ablage, 2x M5 längs in Muttern."""
    gx = geo_x()
    ym = ym_traeger()
    z0 = gx["z_t0"]
    L = 25.0
    res = None
    for xa, richt in ((gx["x_re"], -1),):
        xs0, xs1 = (xa, xa + L) if richt > 0 else (xa - L, xa)
        st = box(xs0, xs1, ym - 17.8, ym + 17.8, z0 + 2.2, z0 + P["traeger_h"] - 2.2)
        for y, z in stopfen_loecher():                  # Mutter seitlich eingeschoben
            st = st.cut(Part.makeCylinder(2.75, 14, V(xa - richt * 1, y, z), V(richt, 0, 0)))
            sy = -1 if y < ym else 1
            st = st.cut(fc_dok.mutter(5, V(xa + richt * 8, y, z), V(1, 0, 0), V(0, sy, 0),
                                      abs(ym + sy * 17.8 - y) + 1))
        res = st if res is None else res.fuse(st)
    return res


def stuetze_x_links():
    """Platte (Alu 8 mm) an der linken Brückenstirn: 4x M6 in das linke Einsteckteil,
    oben stößt die X-Ablage dagegen (2x M5 in den Stopfen)."""
    gx = geo_x()
    x0 = gx["x_re"]
    t = P["ausleger_t"]
    py0, py1 = P["ausleger_y"]
    s = box(x0, x0 + t, py0, py1, P["bruecke_z"][0], gx["z_t0"] + P["traeger_h"])   # oben bündig mit der Ablage
    for y, z in P["turm_loecher_links"]:
        s = s.cut(Part.makeCylinder(3.3, t + 2, V(x0 - 1, y, z), V(1, 0, 0)))
    for y, z in stopfen_loecher():
        s = s.cut(Part.makeCylinder(2.75, t + 2, V(x0 - 1, y, z), V(1, 0, 0)))
    return s


def einsteckteil_links():
    """Wie rechts, in der linken Brückenstirn (x ab Schienenmitte rechts)."""
    gx = geo_x()
    w, tb = P["bruecke_wand"], P["bruecke_tiefe"]
    za, zb = P["bruecke_z"]
    sp = 0.2
    xr = gx["x_re"]
    xm = xr - 20.0                                       # linke Schienenmitte
    x0 = xm - P["einsteck_innen"]
    s = box(x0, xr, -tb / 2 + w + sp, tb / 2 - w - sp, za + w + sp, zb - w - sp)
    for x in P["m6_x"]:
        for z in P["m6_z"]:
            s = s.cut(Part.makeCylinder(3.3, tb, V(xm + x, -tb / 2, z), V(0, 1, 0)))
    for y, z in P["turm_loecher_links"]:              # Mutter hinter der Sattelschraube
        s = s.cut(Part.makeCylinder(3.3, 24, V(xr + 1, y, z), V(-1, 0, 0)))
        s = s.cut(fc_dok.mutter(6, V(xr - 14, y, z), V(1, 0, 0), V(0, 1 if y > 0 else -1, 0), 9))
    return s.removeSplitter()


def halter_x():
    """Halter für das bewegte Ende der X-Kette (Druck, X-Wagen-Koordinaten):
    Rückwand an der Rückseite des Z-Kopf-Sockels (2x M5 in Muttern im Sockel), oben
    eine Platte über dem Anschlussstück (2x M5 von unten, Muttern oben eingepresst),
    ohne Streben (darunter laufen Kette und Adern, darüber sitzt der Z-Motor). Die
    Leitungen treten frei zur Gegenseite aus. Kopfüber (Platte unten) druckbar."""
    gx = geo_x()
    zb = P["bruecke_uk_x_wagen"]
    t = P["ausleger_t"]
    dx = P["xk_halter_dx"]
    yk = P["zkopf_hinten_y"]
    h = P["kette_h"]
    z_es = gx["z_mo"] - h / 2 - zb                       # Unterkante Anschlussstück
    z_top = z_es + h                                     # Oberkante (Flansch)
    dp = P["hx_platte"]
    z_ob = z_top + dp
    lo = P["xk_halter_loecher"]
    xa, xb = min(lo) - 7.0, max(lo) + 7.0
    yc = (gx["y0"] + gx["y1"]) / 2
    s = box(xa, xb, yk - t, yk, P["zkopf_uk"], z_ob)
    s = s.fuse(box(xa, xb, gx["y0"] - 6, yk, z_top, z_ob))
    # keine Streben: darunter laufen Kette und Adern, darüber sitzt der Z-Motor
    for dy in (-P["end_C"] / 2, P["end_C"] / 2):        # Mutter oben, M5 von unten
        s = s.cut(m5_senkrecht(dx + loch_versatz(), yc + dy, z_top, z_ob, z_ob - 1.5))
    for x in lo:
        s = s.cut(Part.makeCylinder(2.75, t + 2, V(x, yk - t - 1, P["zkopf_uk"] + 10), V(0, 1, 0)))
    return s.removeSplitter()


def loch_versatz():
    """Bohrungen der Anschlussteile ab Mitte Anschlussteil zum äußeren Ende (beide Ketten:
    +x bzw. +y, die Schlaufen liegen an der Kettenseite bzw. hinten)."""
    return P["end_laenge"] / 2 - P["end_loch"]


def endstueck(unten, loch):
    return kt.kette_endstueck(P["kette_h"], P["kette_b"], P["end_D"], P["end_C"], P["end_F"],
                              P["end_laenge"], P["end_flansch"], unten, loch)


def kette_x(wagen_x):
    """X-Kette je Wagenlage (Rahmen-x der Wagenmitte), x ab Schienenmitte Kettenseite.
    Festpunkt in der Mitte, Schlaufe zur Kettenseite; an der Gegenseite läuft das
    obere Trum frei über den Festpunkt hinaus."""
    gx = geo_x()
    xm = wagen_x + P["xk_halter_dx"] + gx["xs"]
    x_l = (gx["xf"] + xm - gx["l_eff"]) / 2
    y0, y1 = gx["y0"], gx["y1"]
    h, R = P["kette_h"], P["xk_radius"]
    e = P["end_laenge"] / 2
    unten = box(x_l, gx["xf"] - e, y0, y1, gx["z_ku"], gx["z_ku"] + h)
    oben = box(x_l - 0.01, max(xm - e, x_l + 0.01), y0, y1, gx["z_mo"] - h / 2, gx["z_mo"] + h / 2)  # Bogen ab Anschlussteil
    yc = (y0 + y1) / 2
    for unt, x, z in ((True, gx["xf"], gx["z_ku"]), (False, xm, gx["z_mo"] - h / 2)):
        es = endstueck(unt, -loch_versatz())                # nach der Drehung: Bohrungen bei +x
        es.rotate(V(0, 0, 0), V(0, 0, 1), 90)              # Länge entlang X, Breite entlang Y
        es.translate(V(x, yc, z))
        unten = unten.fuse(fc_dok.fest(es))
    zc = (gx["z_mu"] + gx["z_mo"]) / 2
    ring = Part.makeCylinder(R + h / 2, y1 - y0, V(x_l, y0, zc), V(0, 1, 0)).cut(
        Part.makeCylinder(R - h / 2, y1 - y0 + 2, V(x_l, y0 - 1, zc), V(0, 1, 0)))
    ring = ring.common(box(x_l - R - h, x_l, y0 - 1, y1 + 1, zc - R - h, zc + R + h))
    return unten.fuse([oben, ring]).removeSplitter()


# ---------------------------------------------------------------- Kette (je Portallage)
def kette(portal_y):
    """Kette als Körper: unteres Trum (fest) ab Festpunkt nach hinten, Schlaufe hinten,
    oberes Trum nach vorn bis zum Ausleger. Die Kabel verlassen den Festpunkt nach vorn
    (Schaltschrank und Plasmagerät stehen vorn). portal_y = Portalmitte (Rahmen-y)."""
    g = geo()
    ym = portal_y + sum(P["ausleger_y"]) / 2
    y_l = (g["y_fest"] + ym - g["l_eff"]) / 2           # Mitte der Schlaufe (hinten)
    x0, x1 = g["k_x0"], g["k_x1"]
    h, R = P["kette_h"], P["radius"]
    e = P["end_laenge"] / 2
    unten = box(x0, x1, y_l, g["y_fest"] - e, g["z_ku"], g["z_ku"] + h)
    oben = box(x0, x1, y_l - 0.01, max(ym - e, y_l + 0.01), g["z_mo"] - h / 2, g["z_mo"] + h / 2)
    xc = (x0 + x1) / 2
    for unt, y, z in ((True, g["y_fest"], g["z_ku"]), (False, ym, g["z_mo"] - h / 2)):
        es = endstueck(unt, loch_versatz())
        es.translate(V(xc, y, z))
        unten = unten.fuse(fc_dok.fest(es))
    zc = (g["z_mu"] + g["z_mo"]) / 2
    ring = Part.makeCylinder(R + h / 2, x1 - x0, V(x0, y_l, zc), V(1, 0, 0)).cut(
        Part.makeCylinder(R - h / 2, x1 - x0 + 2, V(x0 - 1, y_l, zc), V(1, 0, 0)))
    ring = ring.common(box(x0 - 1, x1 + 1, y_l - R - h, y_l, zc - R - h, zc + R + h))
    return unten.fuse([oben, ring]).removeSplitter()


def fuehrungen():
    """Leitungsbogen dreiteilig (Hälfte, Trennsteg, Hälfte), Umlenkkopf aus einem Stück."""
    g = geo()
    lb = dreiteilig(leitungsbogen(), (g["k_x0"] + g["k_x1"]) / 2)
    return lb, umlenkkopf()


def main():
    tr, ri = traeger_rinne()
    lb, uk = fuehrungen()
    st = stuetzen()
    au = ausleger()
    ei = einsteckteil()
    xtr, xri = ablage_x()
    xst = stuetze_x_links()
    xpf = halter_x()
    pfad = os.path.join(OUT, "energiekette.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    for alt in ("ekx_festhalter", "ek_leitungsclips", "Kette_20x38_R125", "Kette_X_20x38_R65",
                "ek_leitungsbuegel"):  # ersetzt
        if doc.getObject(alt):
            doc.removeObject(alt)
    fc_dok.teil(doc, "ek_traeger_40x20", tr, "stahl")
    fc_dok.teil(doc, "ek_rinne", ri, "alu")
    fc_dok.teil(doc, "ek_kabelkanal", kabelkanal_y(), "zukauf")
    fc_dok.teil(doc, "ek_stuetzen", Part.makeCompound(st), "stahl")
    fc_dok.teil(doc, "ek_stuetzen_kopf", stuetzen_kopf(), "druck")
    portal = {"ek_ausleger": (au, "alu"), "ek_einsteckteil": (ei, "druck"),
              "ek_halter_y": (halter_y(), "druck"), "ekx_ablagehalter": (ablagehalter_x(), "druck"),
              "ek_Leitung": (leitung(), "zukauf"),
              "ekx_traeger_40x20": (xtr, "alu"), "ekx_rinne": (xri, "alu"),
              "ekx_rinne_hinten": (rinne_hinten(), "alu"), "ekx_rinnenhalter": (rinnenhalter(), "druck"),
              "ek_leitungsbogen": (Part.makeCompound(lb), "druck"), "ekx_mast": (mast(), "alu"), "ekx_distanzstueck": (distanzstueck(), "druck"),
              "ekx_mastwinkel": (mastwinkel(), "druck"),
              "ekx_umlenkkopf": (uk, "druck"), "ek_verbindungsplatte": (verbindungsplatte(), "druck"),
              "ek_leitungsschellen": (Part.makeCompound(leitungsschellen()), "druck"),
              "ekx_leitungssockel": (Part.makeCompound(leitungssockel()), "druck"),
              "ekx_stuetze_links": (xst, "alu"), "ekx_stopfen": (stopfen_x(), "druck"),
              "ek_einsteckteil_links": (einsteckteil_links(), "druck")}
    for n, (shp, farbe) in portal.items():
        o = fc_dok.teil(doc, n, shp, farbe)
        o.Placement = App.Placement(V(0, 700, 0), App.Rotation())  # Darstellung in Portalmitte
    for n, shp, farbe in (("ekx_halter", xpf, "druck"), ("ekx_Leitung_Brenner", brenner_leitung(), "zukauf")):
        o = fc_dok.teil(doc, n, shp, farbe)
        o.Placement = App.Placement(V(340, 700, 57), App.Rotation())
    fc_dok.teil(doc, "Kette_igus_2400_03_R125", kette(700.0), "zukauf")
    k = fc_dok.teil(doc, "Kette_X_igus_2400_03_R75", kette_x(360.0), "zukauf")
    k.Placement = App.Placement(V(0, 700, 0), App.Rotation())
    fc_dok.speichern(doc, pfad, offen)
    import Mesh
    for n, s in (("ek_ausleger", au), ("ek_rinne", ri), ("ek_einsteckteil", ei), ("ekx_halter", xpf),
                 ("ekx_rinne_hinten", rinne_hinten())):
        s.exportStep(os.path.join(OUT, n + ".step"))
    druck = {"ek_einsteckteil": ei, "ek_einsteckteil_links": einsteckteil_links(),
             "ek_halter_y": halter_y(), "ekx_ablagehalter": ablagehalter_x(),
             "ekx_rinnenhalter": rinnenhalter(), "ekx_stopfen": stopfen_x(), "ekx_halter": xpf,
             "ek_stuetzen_kopf": stuetzen_kopf(),
             "ek_leitungsbogen_a": lb[0], "ek_leitungsbogen_steg": lb[1], "ek_leitungsbogen_b": lb[2],
             "ekx_umlenkkopf": uk, "ekx_distanzstueck": distanzstueck(), "ekx_mastwinkel": mastwinkel(),
             "ek_verbindungsplatte": verbindungsplatte(),
             "ek_leitungsschelle": schelle_einzeln(),             # 6 Stück
             "ekx_leitungssockel": leitungssockel()[0]}           # 2 Stück
    mast().exportStep(os.path.join(OUT, "ekx_mast.step"))
    for n, s in druck.items():
        s.exportStep(os.path.join(OUT, n + ".step"))
        Mesh.Mesh(s.tessellate(0.05)).write(os.path.join(OUT, n + ".stl"))

    g, gx = geo(), geo_x()
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Y-Kette igus 2400.03.%03.0f.0: %d Glieder = %.0f mm (Modell mit Anschlussteilen %.0f), "
                "Festpunkt y %.0f, Hub %.0f\n"
                % (P["radius"], P["glieder"], P["glieder"] * P["teilung"], g["laenge"], g["y_fest"],
                   g["ym1"] - g["ym0"]))
        f.write("Y-Rinne x %.1f bis %.1f, Kettenturm außen bis x %.1f (ab Schienenmitte Kettenseite)\n"
                % (g["r_x0"], g["r_x1"], g["a_x0"]))
        f.write("X-Kette igus 2400.03.%03.0f.0: %d Glieder = %.0f mm, Festpunkt Rahmen-x %.0f, Ablage-UK %.0f, "
                "oben bis %.0f über Rahmen-OK\n"
                % (P["xk_radius"], P["xk_glieder"], P["xk_glieder"] * P["teilung"], gx["xf"] - gx["xs"],
                   gx["z_t0"], gx["z_mo"] + P["kette_h"] / 2))
        f.write("X-Kette oberes Trum bei X an der Gegenseite ca. %.0f mm frei über den Festpunkt hinaus "
                "(freitragende Länge der Kette prüfen)\n" % (gx["m1"] - gx["xf"]))
        sl = kette_x(P["xk_wagen_x"][0]).BoundBox
        f.write("X-Kette Schlaufe bei X an der Kettenseite bis x %.1f (Turm innen %.1f)\n"
                % (sl.XMin, g["a_x1"]))
        fc_dok.schreibe_waende(f, "ek_einsteckteil", ei)
        fc_dok.schreibe_waende(f, "ek_einsteckteil_links", einsteckteil_links())
        for n, sh in druck.items():
            if n not in ("ek_einsteckteil", "ek_einsteckteil_links"):
                fc_dok.schreibe_waende(f, n, sh)
        le = leitung()
        for n, sh in (("Turm", au), ("Halter Y", halter_y()), ("Ablagehalter X", ablagehalter_x()),
                      ("Ablage", xtr), ("Rinne X", xri), ("Rinne hinten", rinne_hinten()),
                      ("Rinnenhalter", rinnenhalter()), ("Leitungsbogen", Part.makeCompound(lb)),
                      ("Mast", mast()), ("Umlenkkopf", uk), ("Distanzstück", distanzstueck()), ("Mastwinkel", mastwinkel()),
                      ("Verbindungsplatte", verbindungsplatte()),
                      ("Schellen", Part.makeCompound(leitungsschellen())),
                      ("Sockel", Part.makeCompound(leitungssockel()))):
            f.write("Leitung / %s: %.2f mm³\n" % (n, le.common(sh).Volume))
        for wx in P["xk_wagen_x"]:
            f.write("Leitung / X-Kette bei Wagen %.0f: %.2f mm³\n" % (wx, le.common(kette_x(wx)).Volume))
        p0, p1 = le.Solids[:3], le.Solids[3:]
        p0, p1 = Part.makeCompound(p0), Part.makeCompound(p1)
        f.write("Pfade Brenner / Steuerung: %.2f mm³\n" % p0.common(p1).Volume)
        for k, n in ((0, "Brenner"), (1, "Steuerung")):
            (_, r1), (_, r2), _, _ = pfad_ecken(fach_mitten()[k])
            f.write("Pfad %s: kleinster Biegeradius (Mitte) R%.1f\n" % (n, min(r1[1:-1] + r2[1:-1])))
        bw = brenner_weg()
        f.write("Leitungen Y-Ende -> X-Festpunkt: ca. %.0f mm, Adern X-Ende -> Brenner: ca. %.0f mm (R%.0f)\n"
                % (leitung_weg().Length, bw.Length, P["leitung_r"]))
        x_max = max(v.x for v in bw.discretize(Number=100)) + P["brenner_leitung_d"] / 2
        f.write("Adern bei X an der Gegenseite bis Rahmen-x %.0f (Brückenstirn %.0f)\n"
                % (P["xk_wagen_x"][1] + x_max, P["xk_bruecke_links_x"]))
        z_max = max(v.z for v in bw.discretize(Number=100)) + P["brenner_leitung_d"] / 2
        f.write("Adern oben bis %.0f über Brücken-UK (Z unten), ca. %.0f mm über Boden; bei Z oben "
                "100 mm Schlaufe mehr\n" % (z_max, z_max + 907.0))


if __name__ == "__main__":
    main()
