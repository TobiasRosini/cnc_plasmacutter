# -*- coding: utf-8 -*-
"""
Z-Achse mit Kugelumlaufspindel SFU1204 und Schwimmkopf.

Aufbau (vorn an der Frontplatte des X-Wagens):
  - Z-Grundplatte (Alu 12) mit 4x M5 an die Frontplatte.
  - Zwei Distanzleisten Alu 20x20, darauf HGR15. Die Leisten schaffen Platz
    für den Mutterflansch (Ø42) zwischen Grundplatte und Z-Schlitten; die
    Schienenschrauben M4 gehen durch die Leiste in die Grundplatte.
  - Z-Schlitten (Alu 10) auf zwei HGH15CA, Mutterblock (Druck) hinten.
  - Z-Kopf (Druck) oben: Festlager FK10, Kupplung, NEMA23 kompakt.
  - Schwimmkopf: Halter (Druck) am Schlitten mit zwei Stäben Ø8, darauf
    gleitet der Brennerträger (Druck); beim Antasten hebt er sich und betätigt
    den Schalter.

Alles oberhalb von z = 50 (über der Brückenunterkante) darf breit sein; darunter
nur der schmale Brennerträger und der Brenner, weil dort an den Wegenden die
Türme der Y-Winkel stehen.

Koordinaten wie X-Wagen: x = Wagenmitte, y = Brückenmitte (+Y vorn),
z = Unterseite Brücke.

Aufruf:
  python3 cad/live.py cad/z_achse/z_achse.py
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
    y_front=36.0,               # Vorderfläche Frontplatte X-Wagen
    z_unten=50.0,               # breite Teile nur oberhalb
    hub=100.0,
    z_lage=0.0,                 # Darstellung (und Prüfung im Zusammenbau): 0 = ganz unten, 1 = ganz oben
    # Grundplatte
    gp_dicke=12.0,
    gp_x=52.0,
    gp_oben=270.0,
    gp_loecher=[(-20.0, 62.0), (20.0, 62.0), (-20.0, 88.0), (20.0, 88.0)],   # = X-Wagen z_loecher
    # Distanzleisten + Schienen
    leiste=20.0,
    schiene_x=40.0,
    # Schlitten
    sl_dicke=10.0,
    sl_x=60.0,
    sl_hoehe=100.0,
    # Mutterblock (am Schlitten hinten)
    mb_x=20.0,
    mb_platte=10.0,
    mb_steg=10.0,               # Auflage für den Mutterflansch
    mb_z=40.0,                  # Unterkante Steg über Schlitten-UK (Mutter hängt darunter)
    spindel_unten=40.0,         # freies Spindelende (schmal, darf unter z = 50)
    # Z-Kopf
    kopf_basis=20.0,
    kopf_saeule=12.0,
    kopf_platte=8.0,
    kupplung_l=30.0,
    fk_loch=18.0,               # FK10-Flansch: Lochbild ±18 (Datenblatt prüfen)
    # Schwimmkopf
    stab_d=8.0,
    stab_x=17.0,
    stab_y=115.5,
    halter_x=36.0,
    halter_h=20.0,
    traeger_x=25.0,
    traeger_h=50.0,
    schwimmweg=5.0,
    brenner_y=136.0,
    brenner_d=32.0,
    brenner_unter_traeger=60.0,  # Düse unter Unterkante Brennerträger
    m5_durchgang=5.5,
    m5_kern=4.2,
    m5_senk_d=9.5,
    m5_senk_tiefe=5.5,
    m5_mutter_sw=8.2,
    m5_mutter_tiefe=4.5,
    m4_durchgang=4.5,
    m4_kern=3.3,
    einsatz_m4_d=5.6,
    einsatz_m4_tiefe=8.0,
    einsatz_m5_d=6.4,
    einsatz_m5_tiefe=10.0,
)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def zyl(d, h, x, y, z, richtung=V(0, 0, 1)):
    return Part.makeCylinder(d / 2.0, h, V(x, y, z), richtung)


def sechskant(sw, h, x, y, z):
    r = sw / math.sqrt(3)
    pts = [V(x + r * math.cos(math.radians(30 + 60 * i)),
             y + r * math.sin(math.radians(30 + 60 * i)), z) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def geo(lage=None):
    lage = P["z_lage"] if lage is None else lage
    y0 = P["y_front"]
    y_gp = y0 + P["gp_dicke"]                    # Vorderfläche Grundplatte
    y_sch = y_gp + P["leiste"]                   # Schienenunterseite
    y_wa = y_sch + 28.0                          # Montagefläche Wagen = Schlitten hinten
    y_sp = (y_gp + y_wa) / 2                     # Spindelachse
    s0 = P["z_unten"] + lage * P["hub"]          # Schlitten-Unterkante
    z_kb = P["gp_oben"]                          # Z-Kopf Basis unten
    z_fk = z_kb + P["kopf_basis"] + 10.0         # FK10-Flansch oben
    z_mp = z_fk + 5.0 + P["kupplung_l"]          # Motorplatte unten
    c0 = s0 - P["schwimmweg"] - P["traeger_h"]   # Brennerträger unten
    return dict(y0=y0, y_gp=y_gp, y_sch=y_sch, y_wa=y_wa, y_sp=y_sp, s0=s0, z_kb=z_kb,
                z_fk=z_fk, z_mp=z_mp, c0=c0, y_sl=y_wa + P["sl_dicke"])


def mutter_loecher(g):
    """6 Flanschbohrungen der SFU1204-Mutter, um 30° gedreht (passen in den schmalen Steg)."""
    return [(16 * math.cos(math.radians(30 + 60 * i)),
             g["y_sp"] + 16 * math.sin(math.radians(30 + 60 * i))) for i in range(6)]


# ---------------------------------------------------------------- Alu
def grundplatte():
    g = geo()
    gx = P["gp_x"]
    s = box(-gx, gx, g["y0"], g["y_gp"], P["z_unten"], P["gp_oben"])
    for x, z in P["gp_loecher"]:
        s = s.cut(zyl(P["m5_durchgang"], P["gp_dicke"] + 2, x, g["y0"] - 1, z, V(0, 1, 0)))
        s = s.cut(zyl(P["m5_senk_d"], P["m5_senk_tiefe"] + 1, x, g["y_gp"] - P["m5_senk_tiefe"], z,
                      V(0, 1, 0)))
    for x in (-P["schiene_x"], P["schiene_x"]):            # M4 für Schiene + Leiste
        for z in schienen_loecher():
            s = s.cut(zyl(P["m4_kern"], 11, x, g["y_gp"] + 1, z, V(0, -1, 0)))
    for x, y in kopf_schrauben(g):                         # M5 in die Oberkante
        if y < g["y_gp"]:
            s = s.cut(zyl(P["m5_kern"], 13, x, y, P["gp_oben"] - 12))
    return s


def schienen_loecher():
    return [P["gp_oben"] - 20 - 60 * i for i in range(4)]


def leisten():
    g = geo()
    h = P["leiste"] / 2
    res = []
    for x in (-P["schiene_x"], P["schiene_x"]):
        s = box(x - h, x + h, g["y_gp"], g["y_sch"], P["z_unten"], P["gp_oben"])
        for z in schienen_loecher():
            s = s.cut(zyl(P["m4_durchgang"], P["leiste"] + 2, x, g["y_gp"] - 1, z, V(0, 1, 0)))
        s = s.cut(zyl(P["m5_kern"], 13, x, (g["y_gp"] + g["y_sch"]) / 2, P["gp_oben"] - 12))
        res.append(s)
    return res[0].fuse(res[1])


def schlitten(g):
    sx = P["sl_x"]
    s0 = g["s0"]
    s = box(-sx, sx, g["y_wa"], g["y_sl"], s0, s0 + P["sl_hoehe"])
    zw = s0 + P["sl_hoehe"] / 2
    for x0 in (-P["schiene_x"], P["schiene_x"]):          # Wagen: 4x M4 gesenkt von vorn
        for dx in (-13, 13):
            for dz in (-13, 13):
                s = s.cut(zyl(P["m4_durchgang"], P["sl_dicke"] + 2, x0 + dx, g["y_wa"] - 1, zw + dz,
                              V(0, 1, 0)))
                s = s.cut(zyl(8.0, 5, x0 + dx, g["y_sl"] - 4.5, zw + dz, V(0, 1, 0)))
    for x, z in mutterblock_schrauben(g):                 # Mutterblock: M4 gesenkt von vorn
        s = s.cut(zyl(P["m4_durchgang"], P["sl_dicke"] + 2, x, g["y_wa"] - 1, z, V(0, 1, 0)))
        s = s.cut(zyl(8.0, 5, x, g["y_sl"] - 4.5, z, V(0, 1, 0)))
    for x in (-26.0, 26.0):                               # Schwimmkopf-Halter: M5-Gewinde
        s = s.cut(zyl(P["m5_kern"], P["sl_dicke"] + 2, x, g["y_wa"] - 1, s0 + P["halter_h"] / 2,
                      V(0, 1, 0)))
    return s


# ---------------------------------------------------------------- Druck
def mutterblock_schrauben(g):
    s0 = g["s0"]
    zs = s0 + P["mb_z"] + P["mb_steg"]
    return [(-12.0, zs + 12), (12.0, zs + 12), (-12.0, zs + 36), (12.0, zs + 36)]


def mutterblock(g):
    bx = P["mb_x"]
    s0 = g["s0"]
    zs = s0 + P["mb_z"]
    s = box(-bx, bx, g["y_wa"] - P["mb_platte"], g["y_wa"], zs, zs + P["mb_steg"] + 44)
    s = s.fuse(box(-bx, bx, g["y_gp"] + 2, g["y_wa"], zs, zs + P["mb_steg"]))
    s = s.cut(zyl(14.0, P["mb_steg"] + 2, 0, g["y_sp"], zs - 1))
    for x, y in mutter_loecher(g):
        s = s.cut(zyl(P["m4_durchgang"], P["mb_steg"] + 2, x, y, zs - 1))
        s = s.cut(sechskant(7.2, 3.5, x, y, zs + P["mb_steg"] - 3.5))
    for x, z in mutterblock_schrauben(g):
        s = s.cut(zyl(P["einsatz_m4_d"], P["einsatz_m4_tiefe"] + 1, x, g["y_wa"] + 1, z,
                      V(0, -1, 0)))
    return s.removeSplitter()


def kopf_schrauben(g):
    return [(-15.0, g["y0"] + P["gp_dicke"] / 2), (15.0, g["y0"] + P["gp_dicke"] / 2),
            (-P["schiene_x"], (g["y_gp"] + g["y_sch"]) / 2),
            (P["schiene_x"], (g["y_gp"] + g["y_sch"]) / 2)]


def zkopf(g):
    gx = P["gp_x"]
    zb = g["z_kb"]
    zb1 = zb + P["kopf_basis"]
    yv = g["y_sp"] + 28.2 + 3
    s = box(-gx, gx, g["y0"] - 8, yv, zb, zb1)                             # Basis
    sx = P["kopf_saeule"]
    ys0, ys1 = g["y_sp"] - 12, g["y_sp"] + 12
    for x0 in (-42.0, 42.0 - sx):                                          # zwei Säulen
        s = s.fuse(box(x0, x0 + sx, ys0, ys1, zb1 - 0.01, g["z_mp"]))
    s = s.fuse(box(-42.0, 42.0, g["y_sp"] - 32, g["y_sp"] + 32, g["z_mp"],
                   g["z_mp"] + P["kopf_platte"]))                          # Motorplatte
    # FK10 im Sockel, Flansch oben aufliegend, 4x M4 in Einsätze
    s = s.cut(zyl(35.0, P["kopf_basis"] + 2, 0, g["y_sp"], zb - 1))
    for dx in (-P["fk_loch"], P["fk_loch"]):
        for dy in (-P["fk_loch"], P["fk_loch"]):
            s = s.cut(zyl(P["einsatz_m4_d"], P["einsatz_m4_tiefe"] + 1, dx, g["y_sp"] + dy,
                          zb1 - P["einsatz_m4_tiefe"]))
    # Motor: Zentrierung, 4x M5 mit Muttertaschen unten
    zp = g["z_mp"]
    s = s.cut(zyl(39.1, P["kopf_platte"] + 2, 0, g["y_sp"], zp - 1))
    a = 47.14 / 2
    for dx in (-a, a):
        for dy in (-a, a):
            s = s.cut(zyl(P["m5_durchgang"], P["kopf_platte"] + 2, dx, g["y_sp"] + dy, zp - 1))
            s = s.cut(sechskant(P["m5_mutter_sw"], P["m5_mutter_tiefe"] + 1, dx, g["y_sp"] + dy,
                                zp - 1))
    # Befestigung auf Grundplatte und Leisten: M5 gesenkt
    for x, y in kopf_schrauben(g):
        s = s.cut(zyl(P["m5_durchgang"], P["kopf_basis"] + 2, x, y, zb - 1))
        s = s.cut(zyl(P["m5_senk_d"], P["m5_senk_tiefe"] + 1, x, y, zb1 - P["m5_senk_tiefe"]))
    return s.removeSplitter()


def halter(g):
    """Schwimmkopf-Halter am Schlitten (unten), mit Aussparung für den Brenner."""
    hx, s0 = P["halter_x"], g["s0"]
    y0, y1 = g["y_sl"], P["stab_y"] + 10.5
    s = box(-hx, hx, y0, y1, s0, s0 + P["halter_h"])
    s = s.cut(zyl(P["brenner_d"] + 4, P["halter_h"] + 2, 0, P["brenner_y"], s0 - 1))
    for x in (-P["stab_x"], P["stab_x"]):
        s = s.cut(zyl(P["stab_d"] - 0.1, P["halter_h"] + 2, x, P["stab_y"], s0 - 1))
    for x in (-26.0, 26.0):
        s = s.cut(zyl(P["m5_durchgang"], y1 - y0 + 2, x, y0 - 1, s0 + P["halter_h"] / 2, V(0, 1, 0)))
        s = s.cut(zyl(P["m5_senk_d"], 6, x, y1 - 5, s0 + P["halter_h"] / 2, V(0, 1, 0)))
    return s.removeSplitter()


def traeger(g):
    """Brennerträger: gleitet auf den Stäben, klemmt den Brenner mit 2x M5 seitlich."""
    tx, c0 = P["traeger_x"], g["c0"]
    y0 = g["y_sl"] + 2
    y1 = P["brenner_y"] + P["brenner_d"] / 2 + 4
    s = box(-tx, tx, y0, y1, c0, c0 + P["traeger_h"])
    s = s.cut(zyl(P["brenner_d"], P["traeger_h"] + 2, 0, P["brenner_y"], c0 - 1))
    for x in (-P["stab_x"], P["stab_x"]):
        s = s.cut(zyl(P["stab_d"] + 0.5, P["traeger_h"] + 2, x, P["stab_y"], c0 - 1))
    for z in (c0 + 12, c0 + P["traeger_h"] - 12):
        s = s.cut(zyl(P["m5_kern"], tx + 1, tx + 1, P["brenner_y"], z, V(-1, 0, 0)))
    return s.removeSplitter()


# ---------------------------------------------------------------- Kaufteile
def kaufteile(g):
    d = {}
    sch = None
    for x in (-P["schiene_x"], P["schiene_x"]):
        r = kt.hgr15(P["gp_oben"] - P["z_unten"])
        r.rotate(V(0, 0, 0), V(1, 0, 0), -90)
        r.translate(V(x, g["y_sch"], P["gp_oben"]))
        sch = r if sch is None else sch.fuse(r)
    d["Z_Schienen_HGR15"] = fc_dok.fest(sch)
    wa = None
    for x in (-P["schiene_x"], P["schiene_x"]):
        w = kt.hgh15ca()
        w.rotate(V(0, 0, 0), V(1, 0, 0), -90)
        w.translate(V(x, g["y_sch"], g["s0"] + P["sl_hoehe"] / 2))
        wa = w if wa is None else wa.fuse(w)
    d["Z_Wagen_HGH15CA"] = fc_dok.fest(wa)
    zs = g["s0"] + P["mb_z"]
    m = kt.sfu1204_mutter()
    m.translate(V(0, g["y_sp"], zs))
    d["Z_Mutter_SFU1204"] = fc_dok.fest(m)
    sp = kt.sfu1204(g["z_fk"] - P["spindel_unten"])
    sp.translate(V(0, g["y_sp"], P["spindel_unten"]))
    sp = sp.fuse(zyl(8.0, 18.0, 0, g["y_sp"], g["z_fk"]))      # Wellenende Ø8 in die Kupplung
    d["Z_Spindel_SFU1204"] = fc_dok.fest(sp)
    f = kt.fk10(P["fk_loch"])
    f.translate(V(0, g["y_sp"], g["z_fk"]))
    d["Z_Festlager_FK10"] = fc_dok.fest(f)
    k = kt.kupplung(25.0, P["kupplung_l"])
    k.translate(V(0, g["y_sp"], g["z_fk"] + 2.5))
    d["Z_Kupplung"] = fc_dok.fest(k)
    mo, _ = kt.nema23(56.0, 8.0, kabel_winkel=270.0)
    mo.translate(V(0, g["y_sp"], g["z_mp"] + P["kopf_platte"]))
    d["Z_Motor_NEMA23"] = fc_dok.fest(mo)
    st = None
    for x in (-P["stab_x"], P["stab_x"]):
        z_unten = g["c0"] - 8
        s = zyl(P["stab_d"], g["s0"] + P["halter_h"] - z_unten, x, P["stab_y"], z_unten)
        s = s.fuse(zyl(14.0, 4.0, x, P["stab_y"], z_unten - 4))           # Anschlag unten
        st = s if st is None else st.fuse(s)
    d["Z_Stäbe_D8"] = st
    d["Z_Schalter"] = box(22.0, 34.0, g["y_sl"] + 3, g["y_sl"] + 9,
                          g["s0"] - P["schwimmweg"] + 2, g["s0"])
    b = kt.brenner_sp80m(P["brenner_d"])
    b.translate(V(0, P["brenner_y"], g["c0"] - P["brenner_unter_traeger"]))
    d["Brenner_SP80M"] = fc_dok.fest(b)
    return d


def teile(lage=None):
    g = geo(lage)
    eigen = {"z_grundplatte": (grundplatte(), "alu"), "z_leisten_20x20": (leisten(), "alu"),
             "z_schlitten": (schlitten(g), "alu"), "z_mutterblock": (mutterblock(g), "druck"),
             "z_kopf": (zkopf(g), "druck"), "z_halter": (halter(g), "druck"),
             "z_traeger": (traeger(g), "druck")}
    kauf = {n: (s, "zukauf") for n, s in kaufteile(g).items()}
    return g, eigen, kauf


GEWOLLT = [{"Z_Spindel_SFU1204", "Z_Kupplung"}, {"Z_Motor_NEMA23", "Z_Kupplung"},
           {"Z_Stäbe_D8", "z_halter"}]          # Presssitz / Welle in Bohrung


def main():
    g, eigen, kauf = teile()
    pfad = os.path.join(OUT, "z_achse.FCStd")
    doc, offen = fc_dok.dokument(pfad)
    for n, (shp, farbe) in list(eigen.items()) + list(kauf.items()):
        fc_dok.teil(doc, n, shp, farbe)
    fc_dok.speichern(doc, pfad, offen)

    import Mesh
    for n, (shp, farbe) in eigen.items():
        shp.exportStep(os.path.join(OUT, n + ".step"))
        if farbe == "druck":
            Mesh.Mesh(shp.tessellate(0.05)).write(os.path.join(OUT, n + ".stl"))

    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        for n, (shp, _) in eigen.items():
            bb = shp.BoundBox
            f.write("%-16s gültig: %s, %.1f x %.1f x %.1f mm\n"
                    % (n, shp.isValid(), bb.XLength, bb.YLength, bb.ZLength))
        for n, (shp, _) in eigen.items():
            fc_dok.schreibe_waende(f, n, shp)
        for lage in (0.0, 1.0):
            gl, el, kl = teile(lage)
            alle = list(el.items()) + list(kl.items())
            k = 0
            for i, (na, (a, _)) in enumerate(alle):
                for nb, (b, _) in alle[i + 1:]:
                    if {na, nb} in GEWOLLT or not a.BoundBox.intersect(b.BoundBox):
                        continue
                    v = a.common(b).Volume
                    if v > 1e-2:
                        f.write("Lage %.0f: Kollision %s / %s: %.1f mm³\n" % (lage, na, nb, v))
                        k += 1
            dz = kl["Brenner_SP80M"][0].BoundBox.ZMin
            f.write("Lage %.0f (%s): %d Kollisionen, Düse z = %.1f (Brücken-UK = 0, "
                    "Rahmen-OK ≈ -57)\n" % (lage, "unten" if lage == 0 else "oben", k, dz))
        f.write("Brennerachse %.0f mm vor Brückenmitte; Spindel y %.1f\n"
                % (P["brenner_y"], g["y_sp"]))


main()
