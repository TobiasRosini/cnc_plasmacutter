# -*- coding: utf-8 -*-
"""
Y-Energiekette, liegend, rechts (Kastenseite).

Kette igus E2/000 2400.03 (38 x 25 innen, 54 x 35 außen), R125. Die feste Hälfte liegt in einer Rinne
auf einem Träger über dem rechten Y-Winkel (höher als alles, was dort am Portal
hochsteht). Der Träger liegt auf zwei Stützen an den Rahmenenden, außen am
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
    rahmen_laenge=1516.0,
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
    rinne_t=2.0,
    rinne_rand=12.0,
    rinne_luft=3.5,             # Anschlussstücke sind 55 breit (Kette 54); Rinne und Turm wie vorher
    # Anschlussteile igus 2030.12PZ (Kunststoff, verriegelt): Platte 7 dick, Ba + 1 = 55
    # breit, 40 lang, 2 Bohrungen Ø6,1 im Abstand A = 25 quer zur Kette, 10 mm vom äußeren Ende
    end_D=55.0,
    end_C=25.0,
    end_F=6.1,
    end_laenge=40.0,
    end_flansch=7.0,
    end_loch=10.0,
    # Stützen: je ein Rechteckrohr 20x40x2 (40 entlang y) außen am Längsträger, an den
    # Rahmenenden, oben ein Druckkopf unter dem Träger (statt angeschweißtem Querrohr).
    # Rohr an den Längsträger: 2x M6 durch die Innenwand in Nietmuttern (Grundrahmen
    # ek_stuetze_y/z), außen Zugangslöcher. Kopf ins Rohr: 2x M5 in eingepresste Muttern.
    # Träger auf den Kopf: 2x M6 von unten in Nietmuttern in der Trägerunterseite.
    stuetze=(20.0, 40.0),
    stuetze_wand=2.0,
    stuetze_m6_y=[10.0, 30.0],      # = Grundrahmen ek_stuetze_y
    stuetze_m6_z=-20.0,             # = Grundrahmen ek_stuetze_z
    zugang_m6_d=13.0,
    kopf_h=15.0,
    kopf_zapfen=25.0,
    kopf_y=60.0,                    # Kopf ragt über das Rohr hinaus: Trägerschrauben von unten zugänglich
    kopf_m5_y=[12.0, 28.0],
    kopf_m5_unter_ok=12.0,
    traeger_m6_y=50.0,              # ab Rahmenende
    nietmutter_m6_d=9.0,
    # Kettenturm (Alu-Flachmaterial 40x8) an der Stirn der rechts verlängerten Brücke.
    # In der Brücke steckt ein Einsteckteil (Druck), das von den M6 des Sattels
    # mit gehalten wird; der Turm ist mit 4x M6 in dessen Stirnseite geschraubt.
    ausleger_b=40.0,
    ausleger_t=8.0,
    ausleger_y=(-20.0, 20.0),   # ab Portalmitte (= Brückentiefe)
    ausleger_luft=2.0,          # zur Rinne
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
    xk_y_vorn=17.0,             # Vorderkante Kette, Anschlussstück bleibt 1 mm vor dem Halter am Z-Kopf
    xk_traeger_uk=225.0,        # über Y-Kette (unteres Trum bis 220) und X-Motor
    xk_ablage_x0=15.0,          # Ablage beginnt hier (x ab Schienenmitte Kettenseite)
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
    leitung_d=20.0,             # alle Leitungen zwischen Y-Kette und X-Kette
    brenner_leitung_d=16.0,     # Adern des Brennerpakets zwischen X-Kette und Brenner
    leitung_hinten_y=-131.0,    # Lauf hinter der Ablage (Kehre R60 in den Festpunkt)
    leitung_oben_z=580.0,       # Bogen über das Y-Kettenende nach hinten
    leitung_ab_x=10.0,          # dort hinter der Ablage senkrecht nach unten
    brenner_oben_z=555.0,       # Bogen über dem Brenner (X-Wagen-z), Z unten
    brenner_stummel_z=475.0,    # Oberkante Tülle + Stummel am Brenner (X-Wagen-z), Z unten
    brenner_y=136.0,
    # Rinne hinten (Alu-Winkel 40 x 20 x 2) auf Haltern (Druck) an der Ablage
    rh_halter_x=[40.0, 250.0, 440.0],
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
    L = P["rahmen_laenge"]
    xm = (g["r_x0"] + g["r_x1"]) / 2
    tb, th = P["traeger_b"], P["traeger_h"]
    yh = g["y_hinten"]
    tr = box(xm - tb / 2, xm + tb / 2, yh, L, P["traeger_uk"], P["traeger_uk"] + th)
    tr = tr.cut(box(xm - tb / 2 + 2, xm + tb / 2 - 2, yh - 1, L + 1, P["traeger_uk"] + 2,
                    P["traeger_uk"] + th - 2))
    for y in (P["traeger_m6_y"], L - P["traeger_m6_y"]):          # M6-Nietmuttern zu den Stützköpfen
        for dx in (-10.0, 10.0):
            tr = tr.cut(Part.makeCylinder(P["nietmutter_m6_d"] / 2, 4, V(xm + dx, y, P["traeger_uk"] - 1)))
    xc = (g["k_x0"] + g["k_x1"]) / 2
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):                  # Nietmuttern M5 für das feste Kettenende
        tr = tr.cut(Part.makeCylinder(3.5, 4, V(xc + dx, g["y_fest"] + loch_versatz(),
                                                P["traeger_uk"] + th - 3)))
    t = P["rinne_t"]
    y0 = yh                                              # Rinne ganz durch: hinten Schlaufe, vorn Kabel
    ri = box(g["r_x0"], g["r_x1"], y0, L, g["z_rinne"], g["z_rinne"] + t)
    xc = (g["k_x0"] + g["k_x1"]) / 2
    for dx in (-P["end_C"] / 2, P["end_C"] / 2):                  # festes Kettenende, M5
        ri = ri.cut(Part.makeCylinder(2.75, t + 2, V(xc + dx, g["y_fest"] + loch_versatz(), g["z_rinne"] - 1)))
    for x0 in (g["r_x0"], g["r_x1"] - t):
        ri = ri.fuse(box(x0, x0 + t, y0, L, g["z_rinne"], g["z_rinne"] + P["rinne_rand"]))
    return tr, ri.removeSplitter()


def stuetzen_lagen():
    """(y0, Richtung) je Rahmenende: Rohr von y0 bis y0 + richt * 40."""
    return [(0.0, 1), (P["rahmen_laenge"], -1)]


def stuetzen():
    """Je ein Rechteckrohr 20 x 40 x 2 senkrecht außen am Längsträger."""
    sx, sy = P["stuetze"]
    t = P["stuetze_wand"]
    x1 = -P["rohr"] / 2                                # Außenfläche Längsträger
    x0 = x1 - sx
    z0, z1 = -P["rohr"], P["traeger_uk"] - P["kopf_h"]
    res = None
    for ya, ri in stuetzen_lagen():
        y0, y1 = sorted((ya, ya + ri * sy))
        st = box(x0, x1, y0, y1, z0, z1).cut(box(x0 + t, x1 - t, y0 + t, y1 - t, z0 - 1, z1 + 1))
        for dy in P["stuetze_m6_y"]:                       # M6 innen, Zugang außen
            y = ya + ri * dy
            st = st.cut(Part.makeCylinder(3.3, t + 2, V(x1 - t - 1, y, P["stuetze_m6_z"]), V(1, 0, 0)))
            st = st.cut(Part.makeCylinder(P["zugang_m6_d"] / 2, t + 2, V(x0 - 1, y, P["stuetze_m6_z"]),
                                          V(1, 0, 0)))
        for dy in P["kopf_m5_y"]:                          # M5 außen in den Kopfzapfen
            st = st.cut(Part.makeCylinder(2.75, t + 2, V(x0 - 1, ya + ri * dy, z1 - P["kopf_m5_unter_ok"]),
                                          V(1, 0, 0)))
        res = st if res is None else res.fuse(st)
    return res.removeSplitter()


def stuetzen_kopf():
    """Druckkopf auf jedem Stützrohr: Zapfen im Rohr (2x M5-Mutter, von unten in
    Schlitze geschoben), Platte unter dem Träger (2x M6 von unten). Kopfüber druckbar."""
    g = geo()
    sx, sy = P["stuetze"]
    t, sp = P["stuetze_wand"], 0.2
    x1 = -P["rohr"] / 2
    x0 = x1 - sx
    xm = (g["r_x0"] + g["r_x1"]) / 2
    zo = P["traeger_uk"]
    zu = zo - P["kopf_h"]
    res = None
    for ya, ri in stuetzen_lagen():
        y0, y1 = sorted((ya, ya + ri * P["kopf_y"]))
        k = box(min(xm - P["traeger_b"] / 2, x0), max(xm + P["traeger_b"] / 2, x1), y0, y1, zu, zo)
        r0, r1 = sorted((ya + ri * (t + sp), ya + ri * (sy - t - sp)))
        k = k.fuse(box(x0 + t + sp, x1 - t - sp, r0, r1, zu - P["kopf_zapfen"], zu + 0.01))
        zs = zu - P["kopf_m5_unter_ok"]
        xn = (x0 + x1) / 2                                   # Mutter in Zapfenmitte
        for dy in P["kopf_m5_y"]:
            y = ya + ri * dy
            k = k.cut(Part.makeCylinder(2.75, sx, V(x0, y, zs), V(1, 0, 0)))
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
    """Druckteil auf Höhe der X-Ablage, innen am Turm (2x M5 durch den Turm), mit
    einem Zapfen, auf den die Ablage geschoben wird (2x M5 von unten durch die
    untere Wand). Er ist so breit wie die Rinne und gleicht damit den Versatz
    zwischen Turm (y +-20) und Ablage aus; oben liegt bei X am Ende die Schlaufe auf."""
    g, gx = geo(), geo_x()
    x0, x1 = g["a_x1"], ablage_x0()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    z0, h = gx["z_t0"], P["traeger_h"]
    s = box(x0, x1, gx["r_y0"], gx["r_y1"], z0, gx["z_ku"])
    s = s.fuse(box(x1 - 0.01, x1 + 25, ym - 17.8, ym + 17.8, z0 + 2.2, z0 + h - 2.2))
    zm = festhalter_zm()
    for y in P["turm_x_y"]:                                        # Turm: Mutter von unten
        s = s.cut(m5_quer(x0, y, zm, 1, V(0, 0, -1), zm - z0 + 1))
    for x, y in zapfen_loecher():                                  # Zapfen: Mutter von der Seite
        s = s.cut(Part.makeCylinder(2.75, 15, V(x, y, z0 + 1)))
        sy = -1 if y < ym else 1
        s = s.cut(fc_dok.mutter(5, V(x, y, z0 + 10), V(0, 0, 1), V(0, sy, 0), 9))
    return s.removeSplitter()


def ablage_x0():
    """Ende von X-Ablage und Rinne an der Kettenseite (auf dem Zapfen des Ablagehalters)."""
    return P["xk_ablage_x0"]


def zapfen_loecher():
    gx = geo_x()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    return [(ablage_x0() + 12.5, ym - 10.0), (ablage_x0() + 12.5, ym + 10.0)]


def weg(pts, r):
    """Mittellinie aus Geraden mit Bögen (Radius r) an den Ecken. Prüft, dass jede
    Gerade für die Bögen an ihren Enden lang genug ist."""
    n = len(pts)
    d = [0.0] * n
    for i in range(1, n - 1):
        u = (pts[i - 1] - pts[i]).normalize()
        w = (pts[i + 1] - pts[i]).normalize()
        th = math.pi - math.acos(max(-1.0, min(1.0, u.dot(w))))   # Richtungsänderung
        d[i] = r * math.tan(th / 2)
    for i in range(n - 1):
        if d[i] + d[i + 1] > (pts[i + 1] - pts[i]).Length + 1e-6:
            raise ValueError("Leitungsweg: Gerade %d zu kurz für R%.0f" % (i, r))
    kanten, start = [], pts[0]
    for i in range(1, n - 1):
        a, p, b = pts[i - 1], pts[i], pts[i + 1]
        u = (a - p).normalize()
        w = (b - p).normalize()
        t1, t2 = p + u * d[i], p + w * d[i]
        bi = (u + w).normalize()
        th = math.acos(max(-1.0, min(1.0, u.dot(w))))
        c = p + bi * (r / math.sin(th / 2))
        if (t1 - start).Length > 1e-6:
            kanten.append(Part.LineSegment(start, t1).toShape())
        kanten.append(Part.Arc(t1, c - bi * r, t2).toShape())
        start = t2
    if (pts[-1] - start).Length > 1e-6:
        kanten.append(Part.LineSegment(start, pts[-1]).toShape())
    return Part.Wire(kanten)


def leitung_weg():
    """Alle Leitungen vom bewegten Y-Ende (treten nach vorn aus) zum Festpunkt der
    X-Kette in der Mitte (treten dort zur Kettenseite ein): nach vorn, hoch, in einem
    Bogen über das Y-Kettenende nach hinten, hinter der Ablage hinunter, in der Rinne
    hinten zur Gegenseite und mit einer Kehre R60 in den Festpunkt."""
    g, gx = geo(), geo_x()
    r = P["leitung_r"]
    xc = (g["k_x0"] + g["k_x1"]) / 2
    e = P["end_laenge"] / 2
    yc = (gx["y0"] + gx["y1"]) / 2
    z_ein = gx["z_ku"] + P["kette_h"] / 2
    yh, zo, xa = P["leitung_hinten_y"], P["leitung_oben_z"], P["leitung_ab_x"]
    x_ein = gx["xf"] + e + 0.5
    x_kehre = x_ein + r + 2.0
    y_vor = e + 0.5 + r + 2.0                            # Bogen nach oben direkt hinter dem Anschlussteil
    pts = [V(xc, e + 0.5, g["z_mo"]), V(xc, y_vor, g["z_mo"]), V(xc, y_vor, zo),
           V(xa, yh, zo), V(xa, yh, z_ein), V(x_kehre, yh, z_ein), V(x_kehre, yc, z_ein),
           V(x_ein, yc, z_ein)]
    return weg(pts, r)


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
    return rohr(leitung_weg(), P["leitung_d"])


def brenner_leitung():
    return rohr(brenner_weg(), P["brenner_leitung_d"])


def rinne_hinten():
    """Alu-Winkel 40 x 20 x 2 hinter der Ablage: waagerechter Schenkel unter den
    Leitungen, senkrechter Schenkel hinten; von der Kettenseite bis vor die Kehre."""
    gx = geo_x()
    yh = P["leitung_hinten_y"]
    z0 = gx["z_ku"] + P["kette_h"] / 2 - P["leitung_d"] / 2 - 2.0
    x0 = P["leitung_ab_x"] - 15.0
    x1 = gx["xf"] + P["end_laenge"] / 2 + 2.0
    s = box(x0, x1, yh - 20.0, yh + 20.0, z0, z0 + 2.0)
    s = s.fuse(box(x0, x1, yh - 22.0, yh - 20.0, z0, z0 + 20.0)).removeSplitter()
    for x in P["rh_halter_x"]:                           # M4 in die Rinnenhalter
        s = s.cut(Part.makeCylinder(2.25, 4, V(x + P["rh_halter_b"] / 2, yh, z0 - 1)))
    return s


def rinnenhalter():
    """Druckteile unter der Ablage: tragen die Rinne hinten (je 2x M5 von unten in
    Nietmuttern der Ablage, Rinne mit 1x M4 in eine Mutter, seitlich eingeschoben)."""
    gx = geo_x()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    yh = P["leitung_hinten_y"]
    z_r = gx["z_ku"] + P["kette_h"] / 2 - P["leitung_d"] / 2 - 2.0
    z0 = gx["z_t0"] - 8.0
    res = None
    for x in P["rh_halter_x"]:
        b = P["rh_halter_b"]
        s = box(x, x + b, yh - 22.0, ym + 20.0, z0, gx["z_t0"])           # unter der Ablage
        s = s.fuse(box(x, x + b, yh - 22.0, gx["r_y0"] - 1.0, gx["z_t0"] - 0.01, z_r))  # hinten hoch zur Rinne
        for y in (ym - 10.0, ym + 10.0):                               # M5 von unten, Nietmutter in der Ablage
            s = s.cut(Part.makeCylinder(2.75, 10, V(x + b / 2, y, z0 - 1)))
        s = s.cut(Part.makeCylinder(2.25, 12, V(x + b / 2, yh, z_r - 11)))
        s = s.cut(fc_dok.mutter(4, V(x + b / 2, yh, z_r - 6), V(0, 0, 1), V(1, 0, 0), b))
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


def stopfen_loecher():
    gx = geo_x()
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    zm = gx["z_t0"] + P["traeger_h"] / 2
    return [(-14.0, zm), (0.0, zm)]          # innerhalb der Plattenbreite (y +-20)


def ablage_x():
    """Alu 40x20x2 flach (in y 40 breit) + Rinne, an der Kettenseite auf dem Zapfen des
    Ablagehalters, an der Gegenseite stumpf an der Platte (Stopfen mit M5-Muttern). Die
    Rinne endet hinter dem festen Kettenende (2x M5 durch den Rinnenboden, neben der
    Ablage); dahinter liegt die Kehre der Leitungen."""
    gx = geo_x()
    x0 = ablage_x0()
    x1 = gx["x_re"]
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
    z0 = gx["z_t0"]
    tr = box(x0, x1, ym - 20, ym + 20, z0, z0 + P["traeger_h"])
    tr = tr.cut(box(x0 - 1, x1 + 1, ym - 18, ym + 18, z0 + 2, z0 + P["traeger_h"] - 2))
    for x, y in zapfen_loecher():                                  # M5 von unten in den Zapfen
        tr = tr.cut(Part.makeCylinder(2.75, 4, V(x, y, z0 - 1)))
    for x in P["rh_halter_x"]:                                     # Nietmuttern M5 für die Rinnenhalter
        for y in (ym - 10.0, ym + 10.0):
            tr = tr.cut(Part.makeCylinder(3.5, 4, V(x + P["rh_halter_b"] / 2, y, z0 - 1)))
    yc = (gx["y0"] + gx["y1"]) / 2
    for dy in (-P["end_C"] / 2, P["end_C"] / 2):                  # Nietmuttern M5 für das feste Kettenende
        tr = tr.cut(Part.makeCylinder(3.5, 4, V(gx["xf"] + loch_versatz(), yc + dy, z0 + P["traeger_h"] - 3)))
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
    ym = (gx["r_y0"] + gx["r_y1"]) / 2
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
    s = box(x0, x0 + t, py0, py1, P["bruecke_z"][0], gx["z_t0"] + P["traeger_h"] + 5)
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


def main():
    tr, ri = traeger_rinne()
    st = stuetzen()
    au = ausleger()
    ei = einsteckteil()
    xtr, xri = ablage_x()
    xst = stuetze_x_links()
    xpf = halter_x()
    pfad = os.path.join(OUT, "energiekette.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    for alt in ("ekx_festhalter", "ek_leitungsclips", "Kette_20x38_R125", "Kette_X_20x38_R65"):  # ersetzt
        if doc.getObject(alt):
            doc.removeObject(alt)
    fc_dok.teil(doc, "ek_traeger_40x20", tr, "stahl")
    fc_dok.teil(doc, "ek_rinne", ri, "stahl")
    fc_dok.teil(doc, "ek_stuetzen", st, "stahl")
    fc_dok.teil(doc, "ek_stuetzen_kopf", stuetzen_kopf(), "druck")
    portal = {"ek_ausleger": (au, "alu"), "ek_einsteckteil": (ei, "druck"),
              "ek_halter_y": (halter_y(), "druck"), "ekx_ablagehalter": (ablagehalter_x(), "druck"),
              "ek_Leitung": (leitung(), "zukauf"),
              "ekx_traeger_40x20": (xtr, "alu"), "ekx_rinne": (xri, "alu"),
              "ekx_rinne_hinten": (rinne_hinten(), "alu"), "ekx_rinnenhalter": (rinnenhalter(), "druck"),
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
             "ek_stuetzen_kopf": stuetzen_kopf()}
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
                      ("Rinnenhalter", rinnenhalter())):
            f.write("Leitung / %s: %.2f mm³\n" % (n, le.common(sh).Volume))
        for wx in P["xk_wagen_x"]:
            f.write("Leitung / X-Kette bei Wagen %.0f: %.2f mm³\n" % (wx, le.common(kette_x(wx)).Volume))
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
