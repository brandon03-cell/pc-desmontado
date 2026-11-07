"""Cables mallados individualmente: ATX 24 pines, EPS 8 pines y 12V-2x6 de la GPU.
Cada cable es un nodo: Cable24Pin, CableEPS, CablePCIe (origen en el conector)."""
import layout as L
import lib
from lib import box_minmax as B, join, set_origin, poly_tube
from build_motherboard import mb, W
import build_gpu as G

R_WIRE = 0.00155


def comb(name, pts, M, coll, pad=0.0022):
    xs, ys, zs = zip(*pts)
    return B(name, (min(xs) - pad, min(ys) - pad, min(zs) - pad), (max(xs) + pad, max(ys) + pad, max(zs) + pad), bevel=0.001, mat_=M["connector"], coll=coll)


def cable_24(M, coll):
    a = L.ATX24
    P = [mb("c24_plug", a[0] - 0.8, a[1] - 0.7, a[2] + 0.8, a[3] + 0.7, 12, 27, M, M["connector"], coll, bevel=0.8)]
    P.append(mb("c24_latch", a[0] - 3.2, (a[1] + a[3]) / 2 - 2.5, a[0] - 0.8, (a[1] + a[3]) / 2 + 2.5, 6, 25, M, M["connector"], coll, bevel=0.5))
    mid, mid2 = [], []
    for r, ur in enumerate((231.0, 237.0)):
        hh = 37.5 + (1 - r) * 3.4
        ug = 268.0 + (1 - r) * 3.4
        for c in range(12):
            vc = 86.2 + c * 4.3
            vg = 108 + (vc - 110) * 0.68 + r * 1.4      # segunda fila desfasada
            pts = [W(ur, vc, 26), W(ur, vc, hh), W(250, vc, hh), W(ug, vg, hh), W(ug, vg, -16), W(ug, 300, -16)]
            P.append(poly_tube("c24w", pts, R_WIRE, M["sleeve"], coll, bend_r=0.008 + r * 0.0025, res=5, bevel_res=2))
            mid.append(W(246, vc, hh))
            mid2.append(W(ug, vg, 12))
    P.append(comb("c24_comb", mid, M, coll))
    P.append(comb("c24_comb2", mid2, M, coll))
    o = join(P, "Cable24Pin")
    set_origin(o, W((a[0] + a[2]) / 2, (a[1] + a[3]) / 2, 12))
    return o


def cable_eps(M, coll):
    a = L.EPS[0]
    P = [mb("ceps_plug", a[0] - 0.7, a[1] - 0.6, a[2] + 0.7, a[3] + 0.6, 12, 26, M, M["connector"], coll, bevel=0.8)]
    P.append(mb("ceps_latch", (a[0] + a[2]) / 2 - 2.5, a[3] + 0.6, (a[0] + a[2]) / 2 + 2.5, a[3] + 2.6, 6, 24, M, M["connector"], coll, bevel=0.5))
    mid = []
    for r, vr in enumerate((3.5, 7.5)):
        hh = 31.0 + r * 3.4
        vg = -12.0 - r * 3.4
        for c in range(4):
            uc = 36.2 + c * 4.3
            pts = [W(uc, vr, 25), W(uc, vr, hh), W(uc, vg, hh), W(uc, vg, -16), W(uc - 40, vg, -16)]
            P.append(poly_tube("cepsw", pts, R_WIRE, M["sleeve"], coll, bend_r=0.007, res=5, bevel_res=2))
            mid.append(W(uc, -4, hh))
    P.append(comb("ceps_comb", mid, M, coll))
    o = join(P, "CableEPS")
    set_origin(o, W((a[0] + a[2]) / 2, (a[1] + a[3]) / 2, 12))
    return o


def cable_pcie(M, coll):
    x0, y0, x1, y1 = G.CONN
    zp = G.ZP + G.PCB_T / 2
    P = [B("cp_plug", (-0.0585, y0 - 0.0006, zp + 0.0002), (x0 - 0.0001, y1 + 0.0006, zp + 0.0106), bevel=0.0008, mat_=M["connector"], coll=coll)]
    P.append(B("cp_latch", (-0.054, (y0 + y1) / 2 - 0.0028, zp + 0.0106), (-0.042, (y0 + y1) / 2 + 0.0028, zp + 0.0122), bevel=0.0005, mat_=M["connector"], coll=coll))
    mid = []
    for r in range(2):
        z = zp + 0.0039 + r * 0.0034
        xb = -0.077 - r * 0.0034
        for c in range(6):
            y = y0 + 0.0029 + c * 0.003
            pts = [(-0.058, y, z), (xb, y, z), (xb, y, 0.105), (xb, y, 0.085)]
            P.append(poly_tube("cpw", pts, 0.00142, M["sleeve"], coll, bend_r=0.008, res=5, bevel_res=2))
            mid.append((xb, y, 0.205))
    # 4 cables de señal (sense)
    for c in range(2):
        y = y0 + 0.006 + c * 0.0076
        z = zp + 0.0098
        xb = -0.0845 - c * 0.0012
        P.append(poly_tube("cps", [(-0.058, y, z), (xb, y, z), (xb, y, 0.1), (xb, y, 0.085)], 0.0006, M["sleeve"], coll, bend_r=0.008, res=5, bevel_res=1))
    P.append(comb("cp_comb", mid, M, coll))
    P.append(comb("cp_comb2", [(p[0], p[1], 0.15) for p in mid], M, coll))
    o = join(P, "CablePCIe")
    set_origin(o, (x0, (y0 + y1) / 2, zp))
    return o


def build(M, coll):
    lib.clear_collection(coll.name)
    return cable_24(M, coll), cable_eps(M, coll), cable_pcie(M, coll)
