# -*- coding: utf-8 -*-
"""
Zusammenbau des Plasmatisches aus den Einzelteil-Dokumenten.

Die Teile werden als Verknüpfungen (App::Link) eingebunden, nicht kopiert:
Ändert sich ein Einzelteil, zieht der Zusammenbau automatisch nach.
Lage und Maße werden aus der Geometrie der Einzelteile abgeleitet
(Schienen im Rahmen, Schiene/Brücke im Portalwinkel-Dokument).

Neu in diesem Dokument erzeugt: Portalbrücke 80x40x4 in voller Länge.

Koordinaten wie Grundrahmen: Ursprung = Außenecke am Boden, X quer, Y längs.

Aufruf:
  python3 cad/live.py cad/zusammenbau/zusammenbau.py
"""
import os
import sys
import FreeCAD as App
import Part

V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(OUT)
sys.path.insert(0, CAD)
import fc_dok  # noqa: E402

P = dict(
    portal_y=None,              # Mitte Portal in Y; None = Rahmenmitte
    bruecke_wand=4.0,
    bruecke_verl_links=47.0,    # Brücke links verlängert: Stirn trägt den Kettenturm
    wagen_x=None,               # Lage X-Wagen; None = Rahmenmitte
    x_schiene=15.0,
    x_riemen_dicke=3.8,
    x_riemen_breite=15.0,
    max_breite=800.0,
)

RAHMEN = os.path.join(CAD, "grundrahmen", "grundrahmen.FCStd")
WANNE = os.path.join(CAD, "wanne", "wanne.FCStd")
WINKEL = os.path.join(CAD, "y_portalwinkel", "y_portalwinkel.FCStd")
XWAGEN = os.path.join(CAD, "x_wagen", "x_wagen.FCStd")
YANTRIEB = os.path.join(CAD, "y_antrieb", "y_antrieb.FCStd")
ZACHSE = os.path.join(CAD, "z_achse", "z_achse.FCStd")
KAEFIG = os.path.join(CAD, "wannenkaefig", "wannenkaefig.FCStd")
EKETTE = os.path.join(CAD, "energiekette", "energiekette.FCStd")
XWAGEN_TEILE = ["x_deckplatte", "x_frontplatte", "x_bodenplatte", "x_motorbock",
                "Wagen_X_oben", "Wagen_X_unten", "Riemenscheibe_X", "Umlenkrollen_X",
                "Motor_X_NEMA23", "x_ref_fahne"]

# aus den Einzelteilen übernommen
RAHMEN_TEILE_AUS = {"Dummy_Wanne"}
GEMEINSAM = ["Flachstange_40x15", "spannschlitten", "klemmplatte_fest",
             "klemmplatte_schlitten", "Wagen_HGH15CA"]
# rechts einfache Seite, links Kastenseite (Energieketten)
SEITEN_TEILE = {"rechts": ["winkel_fest", "x_klemmplatte", "y_ref_fahne"],
                "links": ["winkel_kasten", "x_klemmplatte_links", "y_ref_fahne_links",
                          "Referenzschalter_X"]}


def gruppe(doc, name):
    g = fc_dok.objekt(doc, "App::DocumentObjectGroup", name)
    return g


def link(doc, name, ziel, placement, grp):
    o = fc_dok.objekt(doc, "App::Link", name)
    o.setLink(ziel)
    o.LinkPlacement = placement
    if o not in grp.Group:
        grp.addObject(o)
    return o


def bbox(shape):
    bb = App.BoundBox()
    for pt in shape.tessellate(1.0)[0]:
        bb.add(pt)
    return bb


def main():
    dr = fc_dok.quelle(RAHMEN)
    dw = fc_dok.quelle(WANNE)
    dp = fc_dok.quelle(WINKEL)
    dx = fc_dok.quelle(XWAGEN)
    pfad = os.path.join(OUT, "zusammenbau.FCStd")
    doc, offen = fc_dok.dokument(pfad)

    # --- Bezugsmaße aus den Einzelteilen
    schienen = dr.getObject("Dummy_Schienen_HGR15").Shape.Solids
    sx = sorted((s.BoundBox.Center.x for s in schienen))
    s_bb = schienen[0].BoundBox
    z_schiene_rahmen = s_bb.ZMin
    rahmen_bb = App.BoundBox()
    for o in dr.Objects:
        if o.Name not in RAHMEN_TEILE_AUS and o.Name != "Dummy_Schienen_HGR15":
            rahmen_bb.add(o.Shape.BoundBox)
    w_schiene = dp.getObject("Schiene_HGR15").Shape.BoundBox
    w_bruecke = dp.getObject("Bruecke_80x40x4").Shape.BoundBox
    w_flach = dp.getObject("Flachstange_40x15").Shape.BoundBox
    dz = z_schiene_rahmen - w_schiene.ZMin
    py = P["portal_y"] if P["portal_y"] is not None else rahmen_bb.Center.y

    # --- Rahmen: Untertisch und Oberrahmen als getrennte Baugruppen
    g_ut = gruppe(doc, "Untertisch")
    g_or = gruppe(doc, "Oberrahmen")
    for o in dr.Objects:
        if o.Name in RAHMEN_TEILE_AUS:
            continue
        link(doc, "R_" + o.Name, o, App.Placement(), g_ut if o.Name.startswith("UT_") else g_or)

    # --- Wanne, mittig im Rahmen
    g_w = g_ut
    wobj = dw.getObject("Wanne")
    wh = bbox(wobj.Shape).ZLength
    wy = dr.getObject("Dummy_Wanne").Shape.BoundBox.Center.y     # Wannenlage aus dem Rahmen
    # Wannenkäfig hängt im Rahmen (Ring-OK = Rahmen-OK), Wanne steht darin
    dk = fc_dok.quelle(KAEFIG)
    plk = App.Placement(V(rahmen_bb.Center.x, wy, rahmen_bb.ZMax), App.Rotation())
    link(doc, "W_Wannenkaefig", dk.getObject("Wannenkaefig"), plk, g_w)
    link(doc, "W_Ablauf", dk.getObject("Ablauf"), plk, g_w)
    zw = rahmen_bb.ZMax + dk.getObject("Wannenkaefig").Shape.BoundBox.ZMin + 20.0
    link(doc, "W_Wanne", wobj,
         App.Placement(V(rahmen_bb.Center.x, wy, zw), App.Rotation()), g_w)

    # --- Portal: rechts Motorseite, links Kastenseite (gespiegelt, Spannseite
    # beider Winkel vorn = +Y)
    g_p = gruppe(doc, "Portal")
    for seite, x in (("rechts", sx[1]), ("links", sx[0])):
        pl = App.Placement(V(x, py, dz), App.Rotation())
        for n in GEMEINSAM:
            link(doc, "P_%s_%s" % (seite, n), dp.getObject(n), pl, g_p)
        # Die Verknüpfung ersetzt die Platzierung des Objekts (die Versetzung
        # der Kastenseite im Teile-Dokument wirkt hier also nicht)
        for n in SEITEN_TEILE[seite]:
            link(doc, "P_%s_%s" % (seite, n), dp.getObject(n), pl, g_p)

    # Brücke über die volle Breite: Außenkante Sattel links bis rechts
    halb = w_bruecke.XMax          # Brückenende = Sattelaußenkante ab Schienenmitte
    x0, x1 = sx[0] - halb - P["bruecke_verl_links"], sx[1] + halb
    y0, y1 = py + w_bruecke.YMin, py + w_bruecke.YMax
    z0, z1 = dz + w_bruecke.ZMin, dz + w_bruecke.ZMax
    t = P["bruecke_wand"]
    br = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
    br = br.cut(Part.makeBox(x1 - x0 + 2, y1 - y0 - 2 * t, z1 - z0 - 2 * t,
                             V(x0 - 1, y0 + t, z0 + t)))
    b = fc_dok.teil(doc, "Portalbruecke_80x40x4", br, "alu")
    if b not in g_p.Group:
        g_p.addObject(b)

    # --- X-Achse: Schienen oben/unten zwischen den Sätteln, Wagen, Riemen
    g_x = gruppe(doc, "X_Achse")
    sattel = dp.getObject("Flachstange_40x15").Shape.BoundBox.XMax   # Sattel ±20 um Schienenmitte
    xs0, xs1 = sx[0] + sattel, sx[1] - sattel
    hs = P["x_schiene"] / 2
    yc = py + (w_bruecke.YMin + w_bruecke.YMax) / 2
    import kaufteile as kt
    lx = xs1 - xs0
    oben = kt.hgr15(lx)
    oben.rotate(V(0, 0, 0), V(0, 0, 1), -90)             # Länge entlang +X
    oben.translate(V(xs0, yc, z1))
    unten = kt.hgr15(lx)
    unten.rotate(V(0, 0, 0), V(0, 0, 1), -90)
    unten.rotate(V(0, 0, 0), V(1, 0, 0), 180)           # kopfüber unter der Brücke
    unten.translate(V(xs0, yc, z0))
    sch = fc_dok.fest(oben).fuse(fc_dok.fest(unten))
    # Brücke: M4-Gewinde für die X-Schienen oben/unten, Ø6,6 für die M6 der Sättel
    br_l = br
    xl = 20.0
    while xl <= lx - 20.0 + 1e-6:
        for zz in (z1 - P["bruecke_wand"] - 1, z0 - 1):
            br_l = br_l.cut(Part.makeCylinder(1.65, P["bruecke_wand"] + 2, V(xs0 + xl, yc, zz)))
        xl += 60.0
    for xs in sx:
        for ddx in (-11.5, 11.5):
            for ddz in (18.0, 38.0):
                br_l = br_l.cut(Part.makeCylinder(3.3, (y1 - y0) + 2, V(xs + ddx, y0 - 1, z0 + ddz),
                                                  V(0, 1, 0)))
    b.Shape = br_l
    br = br_l
    o = fc_dok.teil(doc, "X_Schienen_HGR15", sch, "dummy")
    if o not in g_x.Group:
        g_x.addObject(o)
    xw = P["wagen_x"] if P["wagen_x"] is not None else rahmen_bb.Center.x
    plw = App.Placement(V(xw, yc, z0), App.Rotation())
    for n in XWAGEN_TEILE:
        link(doc, "X_" + n, dx.getObject(n), plw, g_x)
    # Z-Achse am X-Wagen (gleiche Koordinaten)
    dz_ = fc_dok.quelle(ZACHSE)
    g_z = gruppe(doc, "Z_Achse")
    z_teile = [o.Name for o in dz_.Objects if o.TypeId == "Part::Feature"]
    for n in z_teile:
        link(doc, "Z_" + n if not n.startswith("Z_") else n, dz_.getObject(n), plw, g_z)
    # X-Riemen hinter der Brücke (gerade Trume bis zu den Umlenkrollen)
    rolle = dx.getObject("Umlenkrollen_X").Shape.BoundBox
    deck = dx.getObject("x_deckplatte").Shape.BoundBox
    rr = rolle.YLength / 2
    y_rueck = yc + rolle.YMax + 0.05          # Riemenrücken liegt an den Rollen an
    zr = z0 + rolle.Center.z
    hb, td = P["x_riemen_breite"] / 2, P["x_riemen_dicke"]
    xr_l = xw + rolle.XMin + rr
    xr_r = xw + rolle.XMax - rr
    riemen = Part.makeBox(xr_l - xs0, td, 2 * hb, V(xs0, y_rueck, zr - hb)).fuse(
        Part.makeBox(xs1 - xr_r, td, 2 * hb, V(xr_r, y_rueck, zr - hb)))
    o = fc_dok.teil(doc, "X_Riemen_HTD5M_15", riemen, "riemen")
    if o not in g_x.Group:
        g_x.addObject(o)

    # --- Y-Antrieb: Motoren hinten (Schienenanfang), Umlenkung vorn, innen
    dya = fc_dok.quelle(YANTRIEB)
    g_y = gruppe(doc, "Y_Antrieb")
    yb, yf = s_bb.YMin, s_bb.YMax
    dreh = App.Rotation(V(0, 0, 1), 180)
    for kurz, x, y, r, suf in (("hl", sx[0], yb, App.Rotation(), ""),
                               ("hr", sx[1], yb, App.Rotation(), "_r"),
                               ("vr", sx[1], yf, dreh, ""),
                               ("vl", sx[0], yf, dreh, "_r")):
        namen = (["y_motorhalter", "Motor_Y", "Riemenscheibe_Y", "Referenzschalter_Y"]
                 if kurz[0] == "h"
                 else ["y_umlenkhalter", "Umlenkrolle_Y"])
        for n in namen:
            link(doc, "Y_%s_%s" % (kurz, n), dya.getObject(n + suf),
                 App.Placement(V(x, y, z_schiene_rahmen), r), g_y)
    # Y-Riemen: Obertrum Scheibe -> Winkel (hinten) und Winkel -> Umlenkung (vorn),
    # Rücktrum über die ganze Länge (Lage aus der Riemenscheibe)
    sch = dya.getObject("Riemenscheibe_Y").Shape.BoundBox
    za = z_schiene_rahmen + sch.Center.z
    ya = sch.Center.y
    teil_r = 24 * 5.0 / 3.141592653589793 / 2
    hl = w_flach.YLength / 2
    yr = None
    for x in sx:
        oben = Part.makeBox(15, (py - hl) - (yb + ya), 3.8,
                            V(x - 7.5, yb + ya, za + teil_r - 2.1)).fuse(
            Part.makeBox(15, (yf - ya) - (py + hl), 3.8, V(x - 7.5, py + hl, za + teil_r - 2.1)))
        unten = Part.makeBox(15, (yf - ya) - (yb + ya), 3.8,
                             V(x - 7.5, yb + ya, za - teil_r - 1.7))
        yr = oben.fuse(unten) if yr is None else yr.fuse(oben).fuse(unten)
    o = fc_dok.teil(doc, "Y_Riemen_HTD5M_15", yr, "riemen")
    if o not in g_y.Group:
        g_y.addObject(o)

    # --- Y-Energiekette links: Träger, Rinne, Stützen fest; Ausleger am Portal;
    # Kette in der aktuellen Portallage aus dem Kettenmodul berechnet
    import importlib
    sys.path.insert(0, os.path.join(CAD, "energiekette"))
    import energiekette as ek
    importlib.reload(ek)
    dek = fc_dok.quelle(EKETTE)
    g_e = gruppe(doc, "Energiekette_Y")
    pl_fest = App.Placement(V(sx[0], 0, z_schiene_rahmen), App.Rotation())
    for n in ("ek_traeger_40x20", "ek_rinne", "ek_stuetzen"):
        link(doc, "EK_" + n, dek.getObject(n), pl_fest, g_e)
    pl_portal = App.Placement(V(sx[0], py, z_schiene_rahmen), App.Rotation())
    for n in ("ek_ausleger", "ek_einsteckteil", "ekx_traeger_40x20", "ekx_rinne",
              "ekx_stuetze_rechts", "ekx_stopfen", "ek_einsteckteil_rechts"):
        link(doc, "P_links_" + n, dek.getObject(n), pl_portal, g_e)
    link(doc, "X_ekx_halter", dek.getObject("ekx_halter"), plw, g_e)
    kx = ek.kette_x(xw)
    kx.translate(V(sx[0], py, z_schiene_rahmen))
    o = fc_dok.teil(doc, "X_Kette_20x38_R65", fc_dok.fest(kx), "zukauf")
    if o not in g_e.Group:
        g_e.addObject(o)
    kt_ = ek.kette(py)
    kt_.translate(V(sx[0], 0, z_schiene_rahmen))
    o = fc_dok.teil(doc, "EK_Kette_20x38_R125", fc_dok.fest(kt_), "zukauf")
    if o not in g_e.Group:
        g_e.addObject(o)

    fc_dok.speichern(doc, pfad, offen)

    # --- Prüfung
    def form(prefix):
        return [o for o in doc.Objects if o.Name.startswith(prefix)
                and o.TypeId == "App::Link"]

    rahmen = Part.makeCompound([o.Shape for o in form("R_")
                                if "Schienen" not in o.Name])
    portal = [o for o in form("P_")] + [b]
    wanne = doc.getObject("W_Wanne").Shape
    alle = Part.makeCompound([o.Shape for o in doc.Objects
                              if o.TypeId in ("App::Link", "Part::Feature")])
    gb = bbox(alle)
    with open(os.path.join(OUT, "pruefung.txt"), "w") as f:
        f.write("Gesamtmaß: %.0f (X) x %.0f (Y) x %.0f (Z) mm\n"
                % (gb.XLength, gb.YLength, gb.ZLength))
        f.write("Gesamtbreite %.0f mm, Grenze %.0f mm: %s\n"
                % (gb.XLength, P["max_breite"],
                   "ok" if gb.XLength <= P["max_breite"] else
                   "ZU BREIT um %.0f mm" % (gb.XLength - P["max_breite"])))
        f.write("Rahmen außen %.0f, Portal steht je Seite %.0f mm über\n"
                % (rahmen_bb.XLength, (gb.XLength - rahmen_bb.XLength) / 2))
        f.write("Portalbrücke: %.0f mm lang, OK %.0f mm über Boden\n" % (x1 - x0, z1))
        ls = s_bb.YLength
        f.write("Y-Hub (Schiene %.0f − Flachstange %.0f): %.0f mm, gefordert 1100\n"
                % (ls, w_flach.YLength, ls - w_flach.YLength))
        f.write("Wanne: Unterkante %.0f, Oberkante %.0f mm über Boden (im Wannenkäfig)\n"
                % (zw, zw + wh))
        for o in portal:
            v = o.Shape.common(rahmen).Volume
            if v > 1e-3:
                f.write("Kollision %s / Rahmen: %.1f mm³\n" % (o.Name, v))
        f.write("Kollision Wanne / Rahmen: %.3f mm³\n" % wanne.common(rahmen).Volume)
        f.write("Kollision Wanne / Brücke: %.3f mm³\n" % wanne.common(br).Volume)
        f.write("Abstand Brücke UK zu Rahmen OK: %.0f mm\n" % (z0 - rahmen_bb.ZMax))
        # Alle Teile paarweise (außer Rahmenrohre untereinander: Stoßflächen)
        teile = [o for o in doc.Objects if o.TypeId in ("App::Link", "Part::Feature")
                 and o.Shape.Volume > 0]
        n = 0
        for i, a in enumerate(teile):
            for c in teile[i + 1:]:
                if a.Name.startswith("R_") and c.Name.startswith("R_"):
                    continue
                paar = a.Name + c.Name
                if "Riemen_HTD5M" in paar and ("Riemenscheibe" in paar or "Umlenkrolle" in paar):
                    continue            # Riemen greift in die Scheibe (gewollt)
                if "Ablauf" in paar and "Wanne" in paar and "kaefig" not in paar:
                    continue            # Ablauf geht durch den Wannenboden (gewollt)
                if ("Kupplung" in paar and ("Spindel" in paar or "Motor" in paar)) \
                        or ("Stäbe" in paar and "halter" in paar):
                    continue            # Welle in Kupplung, Stäbe im Presssitz (gewollt)
                if not a.Shape.BoundBox.intersect(c.Shape.BoundBox):
                    continue
                v = a.Shape.common(c.Shape).Volume
                if v > 1e-2:
                    f.write("Kollision %s / %s: %.1f mm³\n" % (a.Name, c.Name, v))
                    n += 1
        f.write("Kollisionen zwischen allen Teilen: %d\n" % n)

        # X-Weg: Wagen an beide Enden schieben, bis er die Winkel berührt
        wagen = Part.makeCompound([dx.getObject(n).Shape for n in XWAGEN_TEILE]
                                  + [dz_.getObject(n).Shape for n in z_teile]
                                  + [dek.getObject("ekx_halter").Shape])
        winkel = Part.makeCompound([o.Shape for o in doc.Objects
                                    if (o.Name.startswith("P_") or o.Name.startswith("EK_"))
                                    and o.TypeId in ("App::Link", "Part::Feature")])

        def frei(x):
            c = wagen.copy()
            c.Placement = App.Placement(V(x, yc, z0), App.Rotation())
            return c.common(winkel).Volume < 1e-2

        def grenze(innen, aussen):
            for _ in range(20):
                m = (innen + aussen) / 2
                innen, aussen = (m, aussen) if frei(m) else (innen, m)
            return innen
        xmin = grenze(rahmen_bb.Center.x, xs0)
        xmax = grenze(rahmen_bb.Center.x, xs1)
        f.write("X-Weg Wagenmitte: %.1f bis %.1f = %.1f mm (Wannenboden %.0f bis %.0f gefordert)\n"
                % (xmin, xmax, xmax - xmin, rahmen_bb.Center.x - 275, rahmen_bb.Center.x + 275))

        # Portal in beiden Y-Endlagen (Flachstange am Schienenende) gegen Rahmen,
        # Y-Antrieb und Y-Riemen prüfen; X-Wagen dabei ganz links und ganz rechts
        fest_teile = Part.makeCompound(
            [o.Shape for o in doc.Objects if o.TypeId in ("App::Link", "Part::Feature")
             and (o.Name.startswith("R_") or o.Name.startswith("Y_")
                  or (o.Name.startswith("EK_") and "Kette" not in o.Name))
             and "Schienen" not in o.Name and o.Name != "Y_Riemen_HTD5M_15"])
        portal_teile = [o.Shape for o in doc.Objects if o.TypeId in ("App::Link", "Part::Feature")
                        and (o.Name.startswith("P_") or o.Name == "Portalbruecke_80x40x4"
                             or o.Name == "X_Schienen_HGR15")]
        for name, ylage in (("hinten", yb + hl), ("vorn", yf - hl)):
            for xl in (xmin, xmax):
                teile_l = [s.copy() for s in portal_teile]
                w = wagen.copy()
                w.Placement = App.Placement(V(xl, yc, z0), App.Rotation())
                teile_l.append(w)
                v = 0.0
                for t in teile_l:
                    t.translate(V(0, ylage - py, 0))
                    v += t.common(fest_teile).Volume
                f.write("Portal %s, X-Wagen bei %.0f: Kollision mit Rahmen/Y-Antrieb %.1f mm³\n"
                        % (name, xl, v))
        br_y = dz_.getObject("Brenner_SP80M").Shape.BoundBox.Center.y
        f.write("Düse in Y: %.0f bis %.0f, Wannenboden %.0f bis %.0f\n"
                % (yb + hl + br_y, yf - hl + br_y, wy - 550, wy + 550))
        # Y-Kette in beiden Endlagen gegen Portal (mit X-Wagen links/rechts) und Rahmen
        for name, ylage in (("hinten", yb + hl), ("vorn", yf - hl)):
            kk = ek.kette(ylage)
            kk.translate(V(sx[0], 0, z_schiene_rahmen))
            kk = fc_dok.fest(kk)
            for xl in (xmin, xmax):
                teile_l = [t_.copy() for t_ in portal_teile]
                w = wagen.copy()
                w.Placement = App.Placement(V(xl, yc, z0), App.Rotation())
                teile_l.append(w)
                kx = ek.kette_x(xl)
                kx.translate(V(sx[0], py, z_schiene_rahmen))
                teile_l.append(fc_dok.fest(kx))
                v = 0.0
                for t_ in teile_l:
                    t_.translate(V(0, ylage - py, 0))
                    v += t_.common(kk).Volume
                v += kk.common(fest_teile).Volume
                f.write("Y-Kette, Portal %s, X-Wagen bei %.0f: Kollision %.1f mm³\n" % (name, xl, v))
        mo = doc.getObject("Y_hl_Motor_Y").Shape.BoundBox
        f.write("Y-Motor hinten: Oberkante %.1f mm über Boden, innen bis x %.1f\n" % (mo.ZMax, mo.XMax))


main()
