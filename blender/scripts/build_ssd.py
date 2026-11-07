"""SSD NVMe M.2 2280 (SSD) y disipador M.2 de la placa (SSDHeatsink)."""
import layout as L
import lib
from lib import join, set_origin
from build_motherboard import mb, mbcyl, W

H0 = 2.8


def build(M, coll):
    lib.clear_collection(coll.name)
    u0, v0, u1, v1 = L.M2_SSD
    vc = (v0 + v1) / 2
    P = []
    pcb = mb("s_pcb", u0 - 3, v0, u1, v1, H0, H0 + 0.8, M, M["pcb"], coll, bevel=0.3, seg=1)
    P.append(pcb)
    # dedos dorados (entran en el conector)
    for k in range(10):
        P.append(mb("s_gold", u0 - 3, v0 + 1.5 + k * 1.9, u0 + 0.5, v0 + 2.6 + k * 1.9, H0 - 0.01, H0 + 0.81, M, M["gold"], coll))
    # media luna del tornillo
    P.append(mbcyl("s_notch", u1, vc, 2.0, H0 + 0.79, H0 + 0.82, M["gold"], coll, 16))
    # chips: controlador, DRAM, 2 NAND
    P.append(mb("s_ctrl", u0 + 4, vc - 7, u0 + 18, vc + 7, H0 + 0.8, H0 + 1.9, M, M["nickel"], coll, bevel=0.3))
    P.append(mb("s_dram", u0 + 22, vc - 5.5, u0 + 33, vc + 5.5, H0 + 0.8, H0 + 1.8, M, M["chip"], coll, bevel=0.2))
    for k in range(2):
        P.append(mb("s_nand", u0 + 37 + k * 20, vc - 7, u0 + 55 + k * 20, vc + 7, H0 + 0.8, H0 + 2.0, M, M["chip"], coll, bevel=0.2))
    # etiqueta (cubre los chips como en los SSD reales)
    lbl = lib.plane("s_label", 0.072, 0.0216, W((u0 + u1) / 2 + 1.5, vc, H0 + 2.06), "X-", M["ssd_label"], coll)
    lbl.data.transform(__import__("mathutils").Matrix.Rotation(3.14159265, 4, "X"))
    lbl.location = W((u0 + u1) / 2 + 1.5, vc, H0 + 2.06)
    lib.apply_mods(lbl)
    lbl.data.transform(lbl.matrix_basis)
    lbl.matrix_basis.identity()
    P.append(lbl)
    ssd = join(P, "SSD")
    set_origin(ssd, W(u0, vc, H0))

    # disipador
    a0, b0, a1, b1 = L.M2_HEATSINK
    H = []
    H.append(mb("h_body", a0, b0, a1, b1, 4.6, 10.5, M, M["alu_dark"], coll, bevel=1.0, seg=2))
    for k in range(9):
        H.append(mb("h_groove", a0 + 10 + k * 8.5, b0 + 2, a0 + 11.5 + k * 8.5, b1 - 2, 10.5, 10.9, M, M["alu_black"], coll))
    H.append(mb("h_pad", u0 + 1, v0 + 0.5, u1 - 1, v1 - 0.5, 3.8, 4.6, M, M["plastic_grey"], coll))
    for u in (a0 + 3.5, a1 - 3.5):
        H.append(mbcyl("h_screw", u, (b0 + b1) / 2, 2.6, 10.5, 12.0, M["screw_silver"], coll, 16, 0.5))
    H.append(mb("h_stripe", a0 + 4, b1 - 3, a1 - 4, b1 - 1.8, 10.5, 10.7, M, M["rgb"], coll))
    hs = join(H, "SSDHeatsink")
    set_origin(hs, W((a0 + a1) / 2, (b0 + b1) / 2, 4.6))
    return ssd, hs
