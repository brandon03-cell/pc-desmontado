"""Fuente ATX 850 W modular (PSU + hijo PSU_Fan_Rotor)."""
import bpy
from mathutils import Matrix

import lib
from lib import box_minmax as B, cyl, plane, boolean_cut, join, set_origin
import build_fans

X0, X1 = -0.075, 0.075
Y0, Y1 = 0.066, 0.2235
Z0, Z1 = 0.0165, 0.1025
FAN_C = (0.0, 0.142, Z0)


def build(M, coll):
    lib.clear_collection(coll.name)
    P = []
    body = B("p_body", (X0, Y0, Z0), (X1, Y1, Z1), bevel=0.0025, seg=3, mat_=M["steel"], coll=coll)
    boolean_cut(body, [
        cyl("cut", 0.064, 0.02, (FAN_C[0], FAN_C[1], Z0), "Z", 72, coll=coll),                     # alojamiento ventilador
        B("cut", (-0.068, Y1 - 0.002, 0.024), (0.022, Y1 + 0.01, 0.095), bevel=0.003, coll=coll),   # rejilla trasera
        B("cut", (-0.068, Y0 - 0.01, 0.022), (0.068, Y0 + 0.003, 0.097), bevel=0.003, coll=coll),   # panel modular
    ])
    P.append(body)
    # rejilla del ventilador (anillos + radios)
    for r in (0.021, 0.034, 0.047, 0.06):
        ring = cyl("p_grill", r + 0.0008, 0.0016, (FAN_C[0], FAN_C[1], Z0 + 0.0012), "Z", 72, mat_=M["screw"], coll=coll)
        boolean_cut(ring, [cyl("cut", r - 0.0008, 0.01, (FAN_C[0], FAN_C[1], Z0), "Z", 72, coll=coll)])
        P.append(ring)
    for k in range(4):
        sp = B("p_spoke", (-0.064, -0.0008, Z0 + 0.0004), (0.064, 0.0008, Z0 + 0.002), mat_=M["screw"], coll=coll)
        sp.data.transform(Matrix.Translation((-0, 0, 0)))
        sp.data.transform(Matrix.Rotation(0.785398 * k, 4, "Z"))
        sp.data.transform(Matrix.Translation((FAN_C[0], FAN_C[1], 0)))
        P.append(sp)
    P.append(cyl("p_badge", 0.016, 0.0008, (FAN_C[0], FAN_C[1], Z0 + 0.0008), "Z", 40, mat_=M["alu_dark"], coll=coll))
    # trasera: panal, toma C14 e interruptor
    P.append(plane("p_rear_mesh", 0.09, 0.071, (-0.023, Y1 - 0.0015, 0.0595), "Y+", M["mesh"], coll, uv=(0, 0, 4, 3.2)))
    P.append(B("p_rear_back", (-0.068, Y1 - 0.012, 0.024), (0.022, Y1 - 0.01, 0.095), mat_=M["chip"], coll=coll))
    P.append(B("p_c14", (0.032, Y1 - 0.003, 0.058), (0.06, Y1 + 0.0005, 0.084), bevel=0.002, mat_=M["plastic"], coll=coll))
    for dx in (-0.006, 0.0, 0.006):
        P.append(B("p_c14pin", (0.046 + dx - 0.0008, Y1 - 0.003, 0.068), (0.046 + dx + 0.0008, Y1 + 0.001, 0.074), mat_=M["tin"], coll=coll))
    P.append(B("p_switch", (0.036, Y1 - 0.001, 0.03), (0.054, Y1 + 0.002, 0.046), bevel=0.0015, mat_=M["plastic_gloss"], coll=coll))
    # panel modular delantero
    P.append(B("p_modpanel", (-0.068, Y0 + 0.002, 0.022), (0.068, Y0 + 0.004, 0.097), mat_=M["plastic"], coll=coll))
    sockets = [(-0.062, 0.06, -0.034, 0.092, 2, 9), (-0.03, 0.074, -0.014, 0.092, 2, 5),
               (-0.008, 0.075, 0.012, 0.092, 2, 4), (0.016, 0.075, 0.036, 0.092, 2, 4), (0.04, 0.075, 0.062, 0.092, 2, 6),
               (-0.008, 0.052, 0.012, 0.069, 2, 4), (0.016, 0.052, 0.036, 0.069, 2, 4),
               (-0.062, 0.028, -0.04, 0.04, 1, 6), (-0.036, 0.028, -0.014, 0.04, 1, 6), (0.016, 0.028, 0.04, 0.04, 1, 6)]
    for (a, b, c, d, rows, cols) in sockets:
        P.append(B("p_sock", (a, Y0 + 0.0005, b), (c, Y0 + 0.003, d), bevel=0.0005, mat_=M["connector"], coll=coll))
        for i in range(cols):
            for j in range(rows):
                cx = a + (i + 0.5) * (c - a) / cols
                cz = b + (j + 0.5) * (d - b) / rows
                P.append(B("p_hole", (cx - 0.0011, Y0 + 0.0002, cz - 0.0011), (cx + 0.0011, Y0 + 0.0008, cz + 0.0011), mat_=M["chip"], coll=coll))
    # etiqueta lateral (lado cristal)
    P.append(plane("p_label", 0.118, 0.0636, (X0 - 0.0002, (Y0 + Y1) / 2 - 0.008, (Z0 + Z1) / 2), "X-", M["psu_label"], coll))
    # tornillos traseros
    for (x, z) in ((-0.07, 0.021), (0.07, 0.021), (-0.07, 0.098), (0.07, 0.098)):
        P.append(cyl("p_screw", 0.003, 0.002, (x, Y1 + 0.007, z), "Y", 16, bevel=0.0006, mat_=M["screw"], coll=coll))
    psu = join(P, "PSU")
    set_origin(psu, ((X0 + X1) / 2, (Y0 + Y1) / 2, (Z0 + Z1) / 2))

    blades = build_fans.blades_mesh("p_blades", 7, 0.021, 0.0605, 0.012, M["fan_blade_black"], coll, sweep=0.75, skew=0.3, axis="Z")
    hub = cyl("p_hub", 0.021, 0.012, (0, 0, 0), "Z", 40, bevel=0.0015, mat_=M["fan_frame"], coll=coll)
    rot = join([blades, hub], "PSU_Fan_Rotor")
    rot.location = (FAN_C[0], FAN_C[1], Z0 + 0.0105)
    lib.parent_keep(rot, psu)
    return psu
