"""Caja mid-tower: chasis (Case) + panel de cristal (GlassPanel)."""
import math

from mathutils import Matrix

import lib
from lib import box_minmax as B, cyl, plane, boolean_cut, join, set_origin

# Medidas exteriores
X0, X1 = -0.115, 0.115
Y0, Y1 = -0.23, 0.23
Z0, Z1 = 0.012, 0.48
T = 0.0012           # espesor chapa (visual)
TRAY_X = 0.093       # cara frontal de la bandeja de la placa
SHROUD_TOP = 0.115
SHROUD_Y0 = -0.175
SLOT_PITCH = 0.02032
GPU_Z = 0.2735


def slot_z(k):
    """Centro Z de la ranura de expansión k (0 = la de la GPU)."""
    return GPU_Z - 0.0075 - k * SLOT_PITCH


def build(M, coll):
    lib.clear_collection(coll.name)
    parts = []
    s, si = M["steel"], M["steel_in"]

    # ---------------------------------------------------------------- paneles exteriores
    # Lateral derecho (detrás de la bandeja)
    parts.append(B("c_right", (X1 - T * 2, Y0 + 0.003, Z0 + 0.003), (X1, Y1 - 0.003, Z1 - 0.003), bevel=0.0015, mat_=s, coll=coll))
    # Base
    parts.append(B("c_bottom", (X0 + 0.001, Y0 + 0.004, Z0), (X1 - 0.001, Y1 - 0.004, Z0 + 0.004), bevel=0.0015, mat_=s, coll=coll))
    # Techo con ventana de malla
    top = B("c_top", (X0, Y0 + 0.004, Z1 - 0.005), (X1, Y1 - 0.004, Z1), bevel=0.002, mat_=s, coll=coll)
    boolean_cut(top, [B("cut", (-0.09, -0.185, Z1 - 0.02), (0.085, 0.175, Z1 + 0.02), coll=coll)])
    parts.append(top)
    parts.append(plane("c_top_mesh", 0.175, 0.36, (-0.0025, -0.005, Z1 - 0.0025), "Z+", M["mesh"], coll, uv=(0, 0, 0.175 / 0.03, 0.36 / 0.03)))
    # Marco del techo: carriles para ventiladores superiores
    for y in (-0.16, 0.15):
        parts.append(B("c_toprail", (-0.1, y - 0.004, Z1 - 0.012), (0.09, y + 0.004, Z1 - 0.005), mat_=si, coll=coll))

    # Frontal: bisel de plástico con malla
    front = B("c_front", (X0, Y0, Z0), (X1, Y0 + 0.008, Z1), bevel=0.003, seg=3, mat_=M["plastic"], coll=coll)
    boolean_cut(front, [B("cut", (-0.098, Y0 - 0.01, 0.03), (0.098, Y0 + 0.02, Z1 - 0.022), bevel=0.004, coll=coll)])
    parts.append(front)
    parts.append(plane("c_front_mesh", 0.196, Z1 - 0.022 - 0.03, (0, Y0 + 0.004, (0.03 + Z1 - 0.022) / 2), "Y-", M["mesh"], coll,
                       uv=(0, 0, 0.196 / 0.03, (Z1 - 0.052) / 0.03)))
    # Placa de montaje de ventiladores frontales
    fb = B("c_fanbracket", (-0.075, -0.2215, 0.016), (0.06, -0.2185, Z1 - 0.008), mat_=si, coll=coll)
    cutters = [cyl("cut", 0.058, 0.03, (-0.01, -0.22, z), "Y", 48, coll=coll) for z in (0.14, 0.265, 0.39)]
    boolean_cut(fb, cutters)
    parts.append(fb)

    # Trasera
    rear = B("c_rear", (X0 + 0.002, Y1 - 0.006, Z0 + 0.002), (X1 - 0.002, Y1, Z1 - 0.002), bevel=0.001, mat_=s, coll=coll)
    cuts = [
        B("cut", (0.041, Y1 - 0.02, 0.281), (0.0855, Y1 + 0.02, 0.44), coll=coll),          # escudo I/O
        cyl("cut", 0.056, 0.04, (-0.024, Y1 - 0.003, 0.367), "Y", 48, coll=coll),           # ventilador trasero
        B("cut", (-0.075, Y1 - 0.02, 0.019), (0.075, Y1 + 0.02, 0.103), coll=coll),         # fuente
    ]
    for k in range(-1, 6):
        z = slot_z(k)
        cuts.append(B("cut", (-0.047, Y1 - 0.02, z - 0.0075), (0.074, Y1 + 0.02, z + 0.0075), coll=coll))
    boolean_cut(rear, cuts)
    parts.append(rear)
    parts.append(plane("c_rear_vent", 0.112, 0.112, (-0.024, Y1 - 0.003, 0.367), "Y+", M["mesh"], coll, uv=(0, 0, 4, 4)))
    # Tapas de ranuras (las de la GPU, k=0..2, quedan libres: las ocupa su soporte)
    for k in (-1, 3, 4, 5):
        z = slot_z(k)
        sc = B("c_slotcover", (-0.05, Y1 - 0.0085, z - 0.0089), (0.077, Y1 - 0.0065, z + 0.0089), bevel=0.0006, mat_=M["slot_cover"], coll=coll)
        parts.append(sc)
        for j in range(6):
            parts.append(B("c_slotvent", (-0.035 + j * 0.017, Y1 - 0.0062, z - 0.0035), (-0.024 + j * 0.017, Y1 - 0.0058, z + 0.0035), mat_=M["plastic"], coll=coll))
    # Tornillos de las tapas
    for k in range(-1, 6):
        parts.append(cyl("c_slotscrew", 0.0032, 0.003, (0.081, Y1 + 0.0015, slot_z(k)), "Y", 16, bevel=0.0008, mat_=M["screw"], coll=coll))
    # Marco de ranuras
    parts.append(B("c_slotframe", (0.077, Y1 - 0.012, slot_z(5) - 0.012), (0.09, Y1 - 0.006, slot_z(-1) + 0.012), mat_=si, coll=coll))

    # ---------------------------------------------------------------- interior
    tray = B("c_tray", (TRAY_X, -0.205, SHROUD_TOP), (TRAY_X + 0.002, Y1 - 0.006, Z1 - 0.005), mat_=si, coll=coll)
    tray_cuts = [
        B("cut", (0.08, 0.094 - 0.05, 0.367 - 0.055), (0.11, 0.094 + 0.05, 0.367 + 0.055), bevel=0.006, coll=coll),  # CPU
        B("cut", (0.08, -0.068, 0.315), (0.11, -0.046, 0.392), bevel=0.006, coll=coll),   # pasacables 24 pines
        B("cut", (0.08, -0.068, 0.17), (0.11, -0.046, 0.25), bevel=0.006, coll=coll),
        B("cut", (0.08, 0.13, 0.452), (0.11, 0.2, 0.469), bevel=0.004, coll=coll),        # EPS superior
    ]
    boolean_cut(tray, tray_cuts)
    parts.append(tray)
    # Pasacables de goma (marcos)
    for (ya, yb, za, zb) in ((-0.068, -0.046, 0.315, 0.392), (-0.068, -0.046, 0.17, 0.25), (0.13, 0.2, 0.452, 0.469)):
        g = B("c_grommet", (TRAY_X - 0.002, ya - 0.002, za - 0.002), (TRAY_X + 0.003, yb + 0.002, zb + 0.002), bevel=0.0015, mat_=M["rubber"], coll=coll)
        boolean_cut(g, [B("cut", (0.08, ya + 0.0015, za + 0.0015), (0.11, yb - 0.0015, zb - 0.0015), bevel=0.003, coll=coll)])
        parts.append(g)
        # labios de goma (rendija)
        parts.append(B("c_grom_lip", (TRAY_X + 0.0005, ya + 0.0015, za + 0.0015), (TRAY_X + 0.001, (ya + yb) / 2 - 0.0005, zb - 0.0015), mat_=M["rubber"], coll=coll))
        parts.append(B("c_grom_lip", (TRAY_X + 0.0005, (ya + yb) / 2 + 0.0005, za + 0.0015), (TRAY_X + 0.001, yb - 0.0015, zb - 0.0015), mat_=M["rubber"], coll=coll))
    # Separadores (standoffs) bajo los agujeros de la placa
    import layout as L
    for (u, v) in L.HOLES:
        x, y, z = L.mb_to_world(u, v)
        parts.append(cyl("c_standoff", 0.0027, TRAY_X - (x + L.MB_T / 1000), (x + L.MB_T / 1000 + (TRAY_X - x - L.MB_T / 1000) / 2, y, z), "X", 6, mat_=M["tin"], coll=coll))

    # Cubierta de la fuente (shroud)
    shroud_top = B("c_shroud_top", (X0 + 0.003, SHROUD_Y0, SHROUD_TOP - 0.003), (TRAY_X, Y1 - 0.006, SHROUD_TOP), bevel=0.001, mat_=s, coll=coll)
    sh_cuts = [B("cut", (-0.098, 0.03, 0.1), (-0.062, 0.075, 0.13), bevel=0.004, coll=coll)]   # paso cable PCIe
    for j in range(9):
        sh_cuts.append(B("cut", (-0.04 + j * 0.012, -0.15, 0.1), (-0.034 + j * 0.012, -0.06, 0.13), bevel=0.002, coll=coll))
    boolean_cut(shroud_top, sh_cuts)
    parts.append(shroud_top)
    side = B("c_shroud_side", (X0 + 0.003, SHROUD_Y0, Z0 + 0.004), (X0 + 0.006, Y1 - 0.006, SHROUD_TOP), bevel=0.001, mat_=s, coll=coll)
    parts.append(side)
    parts.append(B("c_shroud_front", (X0 + 0.003, SHROUD_Y0, Z0 + 0.004), (TRAY_X, SHROUD_Y0 + 0.003, SHROUD_TOP), bevel=0.001, mat_=s, coll=coll))
    # Logotipo en relieve del shroud (lado cristal)
    parts.append(B("c_shroud_badge", (X0 + 0.0025, -0.02, 0.05), (X0 + 0.003, 0.09, 0.08), bevel=0.001, mat_=M["alu_dark"], coll=coll))

    # Marco lateral izquierdo (donde apoya el cristal)
    for (ya, yb, za, zb) in ((Y0 + 0.008, Y1 - 0.006, Z0, Z0 + 0.012), (Y0 + 0.008, Y1 - 0.006, Z1 - 0.012, Z1 - 0.005)):
        parts.append(B("c_lrail", (X0, ya, za), (X0 + 0.003, yb, zb), mat_=s, coll=coll))
    for y in (Y0 + 0.008, Y1 - 0.009):
        parts.append(B("c_lpost", (X0, y, Z0), (X0 + 0.003, y + 0.003, Z1 - 0.005), mat_=s, coll=coll))
    for y in (Y1 - 0.009,):
        parts.append(B("c_rpost", (X1 - 0.003, y, Z0), (X1, y + 0.003, Z1 - 0.005), mat_=s, coll=coll))

    # Patas
    for x in (X0 + 0.02, X1 - 0.02):
        for y in (Y0 + 0.035, Y1 - 0.035):
            parts.append(B("c_foot", (x - 0.012, y - 0.022, 0.0), (x + 0.012, y + 0.022, Z0 + 0.001), bevel=0.003, mat_=M["plastic"], coll=coll))
            parts.append(B("c_footpad", (x - 0.010, y - 0.02, -0.0005), (x + 0.010, y + 0.02, 0.001), bevel=0.002, mat_=M["rubber"], coll=coll))

    # I/O frontal en el techo
    io_y = Y0 + 0.022
    parts.append(B("c_io_panel", (-0.075, io_y - 0.012, Z1 - 0.0005), (0.075, io_y + 0.012, Z1 + 0.0008), bevel=0.001, mat_=M["plastic_gloss"], coll=coll))
    parts.append(cyl("c_power", 0.0065, 0.003, (-0.055, io_y, Z1 + 0.0015), "Z", 32, bevel=0.0008, mat_=M["alu_dark"], coll=coll))
    pr = cyl("c_power_ring", 0.0075, 0.0012, (-0.055, io_y, Z1 + 0.0011), "Z", 32, mat_=M["rgb_white"], coll=coll)
    parts.append(pr)
    for i, x in enumerate((-0.03, -0.012)):
        parts.append(B("c_usb", (x - 0.0065, io_y - 0.0025, Z1 + 0.0002), (x + 0.0065, io_y + 0.0025, Z1 + 0.0009), mat_=M["plastic"], coll=coll))
        parts.append(B("c_usb_in", (x - 0.0055, io_y - 0.0005, Z1 + 0.0004), (x + 0.0055, io_y + 0.0012, Z1 + 0.001), mat_=M["tin"], coll=coll))
    parts.append(B("c_usbc", (0.006, io_y - 0.0017, Z1 + 0.0002), (0.0155, io_y + 0.0017, Z1 + 0.0009), bevel=0.0012, mat_=M["tin"], coll=coll))
    parts.append(cyl("c_jack", 0.0028, 0.0012, (0.03, io_y, Z1 + 0.0006), "Z", 16, mat_=M["plastic"], coll=coll))
    parts.append(cyl("c_reset", 0.003, 0.0016, (0.05, io_y, Z1 + 0.0008), "Z", 16, mat_=M["alu_dark"], coll=coll))

    case = join(parts, "Case")
    set_origin(case, (0, 0, 0))

    # ---------------------------------------------------------------- cristal
    g = B("GlassPanel", (X0 - 0.0045, Y0 + 0.004, Z0 + 0.003), (X0 - 0.0005, Y1 - 0.003, Z1 - 0.003), bevel=0.0015, seg=2, mat_=M["glass"], coll=coll)
    # serigrafía negra (frit) en la cara interior, borde de 14 mm
    gx = X0 - 0.0002
    w = 0.014
    frit = []
    ya, yb, za, zb = Y0 + 0.004, Y1 - 0.003, Z0 + 0.003, Z1 - 0.003
    for (a, b) in (((ya, za), (yb, za + w)), ((ya, zb - w), (yb, zb)), ((ya, za + w), (ya + w, zb - w)), ((yb - w, za + w), (yb, zb - w))):
        frit.append(B("frit", (gx - 0.0004, a[0], a[1]), (gx, b[0], b[1]), mat_=M["frit"], coll=coll))
    # bisagras / soportes de cristal
    for z in (Z0 + 0.03, Z1 - 0.03):
        frit.append(B("glass_clip", (X0 - 0.0005, Y1 - 0.012, z - 0.012), (X0 + 0.002, Y1 - 0.003, z + 0.012), bevel=0.001, mat_=M["alu_black"], coll=coll))
    gp = join([g] + frit, "GlassPanel")
    set_origin(gp, (X0 - 0.0025, 0.0, (Z0 + Z1) / 2))
    return case, gp
