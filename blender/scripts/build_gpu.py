"""Tarjeta gráfica de 3 slots y 305 mm (GPU + hijos GPU_Fan1..3_Rotor)."""
import math

import bpy
from mathutils import Matrix, Vector

import lib
from lib import box_minmax as B, cyl, boolean_cut, join, set_origin, plane
import build_fans

ZP = 0.2735                     # plano medio del PCB (alineado con PCIEX16_1)
PCB_T = 0.0016
Y_BR, Y_END = 0.2205, -0.083    # soporte -> extremo delantero
XS0, XS1 = -0.058, 0.0745       # canto superior (cristal) -> lado placa
Z_BOT = 0.217                   # cara de los ventiladores
Z_FIN0, Z_FIN1 = 0.2305, 0.2715
Z_BP0, Z_BP1 = 0.2755, 0.2775   # backplate
FAN_Y = (0.170, 0.0715, -0.027)
FAN_X = (XS0 + XS1) / 2
FAN_R = 0.0465
CONN = (-0.0400, 0.0315, -0.0285, 0.0495)   # x0, y0, x1, y1 del 12V-2x6


def build(M, coll):
    lib.clear_collection(coll.name)
    P = []
    # ------------------------------------------------------------ PCB
    pcb = B("g_pcb", (-0.030, -0.030, ZP - PCB_T / 2), (0.0735, Y_BR - 0.001, ZP + PCB_T / 2), mat_=M["pcb"], coll=coll)
    P.append(pcb)
    P.append(B("g_fingers_pcb", (0.0735, 0.0815, ZP - PCB_T / 2), (0.082, 0.1695, ZP + PCB_T / 2), mat_=M["pcb"], coll=coll))
    for k in range(40):
        y = 0.083 + k * 0.0021
        for s in (-1, 1):
            P.append(B("g_finger", (0.0745, y, ZP + s * PCB_T / 2 - 0.00005), (0.0815, y + 0.0013, ZP + s * PCB_T / 2 + 0.00005), mat_=M["gold"], coll=coll))
    # componentes cerca del conector de alimentación
    for k in range(6):
        P.append(cyl("g_cap", 0.0028, 0.006, (-0.022 + (k % 3) * 0.0065, 0.058 + (k // 3) * 0.0065, ZP + 0.0038), "Z", 14, bevel=0.0004, mat_=M["cap_sleeve"], coll=coll))

    # ------------------------------------------------------------ disipador: aletas
    pitch = 0.0019
    n = int((Y_BR - 0.003 - (Y_END + 0.002)) / pitch)
    fin = B("g_fin", (-0.0545, -0.0002, Z_FIN0), (0.0715, 0.0002, Z_FIN1), mat_=M["fins"], coll=coll)
    fin_ft = B("g_fin_ft", (-0.050, -0.0002, Z_FIN0), (0.066, 0.0002, Z_BP0 - 0.0003), mat_=M["fins"], coll=coll)
    fins = []
    for k in range(n):
        y = Y_END + 0.002 + k * pitch
        src = fin_ft if y < -0.031 else fin
        f = src.copy()
        coll.objects.link(f)
        f.location = (0, y, 0)
        fins.append(f)
    for f in fins:
        f.data = f.data.copy()
        f.data.transform(Matrix.Translation(f.location))
        f.location = (0, 0, 0)
    bpy.data.objects.remove(fin, do_unlink=True)
    bpy.data.objects.remove(fin_ft, do_unlink=True)
    P.append(join(fins, "g_fins"))
    # placa base del disipador / cámara de vapor (bajo el PCB)
    P.append(B("g_coldplate", (-0.022, 0.06, Z_FIN1), (0.06, 0.165, ZP - PCB_T / 2), mat_=M["nickel"], coll=coll))
    # heatpipes niquelados (visibles por el canto)
    for i, z in enumerate((0.236, 0.2445, 0.253, 0.2615)):
        xh = -0.041 + (i % 2) * 0.004
        pts = [(0.03, 0.2 - i * 0.004, z), (xh, 0.2 - i * 0.004, z), (xh, -0.073 + i * 0.004, z), (0.03, -0.073 + i * 0.004, z)]
        P.append(lib.poly_tube(f"g_hp{i}", pts, 0.003, M["copper"], coll, bend_r=0.014, res=8, bevel_res=2))

    # ------------------------------------------------------------ carcasa (shroud)
    plate = B("g_plate", (XS0, Y_END, Z_BOT), (XS1, Y_BR, Z_BOT + 0.0035), bevel=0.0015, mat_=M["plastic"], coll=coll)
    boolean_cut(plate, [cyl("cut", FAN_R, 0.02, (FAN_X, y, Z_BOT), "Z", 72, coll=coll) for y in FAN_Y])
    P.append(plate)
    # aros metálicos alrededor de cada ventilador
    for y in FAN_Y:
        r = cyl("g_fanring", FAN_R + 0.003, 0.002, (FAN_X, y, Z_BOT - 0.0004), "Z", 72, mat_=M["alu_dark"], coll=coll)
        boolean_cut(r, [cyl("cut", FAN_R + 0.0002, 0.01, (FAN_X, y, Z_BOT), "Z", 72, coll=coll)])
        P.append(r)
    # acentos de aluminio entre ventiladores y en los extremos
    for y in (0.1205, 0.022):
        P.append(B("g_accent", (XS0 + 0.004, y - 0.0025, Z_BOT - 0.0012), (XS1 - 0.004, y + 0.0025, Z_BOT + 0.001), bevel=0.0008, mat_=M["alu_dark"], coll=coll))
    P.append(B("g_endcap", (XS0, Y_END, Z_BOT), (XS1, Y_END + 0.004, Z_FIN0 + 0.006), bevel=0.0015, mat_=M["plastic"], coll=coll))
    P.append(B("g_brend", (XS0, Y_BR - 0.004, Z_BOT), (XS1, Y_BR, Z_FIN1), bevel=0.001, mat_=M["plastic"], coll=coll))
    # canto superior (lado cristal): faldón con logo iluminado y tira RGB
    P.append(B("g_rim_top", (XS0, Y_END, Z_BOT), (XS0 + 0.0035, Y_BR, Z_FIN0 + 0.006), bevel=0.0012, mat_=M["alu_dark"], coll=coll))
    P.append(plane("g_logo", 0.105, 0.0118, (XS0 - 0.0003, 0.105, Z_BOT + 0.0098), "X-", M["gpu_logo"], coll))
    P.append(B("g_rgb_strip", (XS0 - 0.0006, -0.075, Z_BOT + 0.0155), (XS0 + 0.001, 0.035, Z_BOT + 0.0175), mat_=M["rgb"], coll=coll))
    P.append(B("g_rim_mb", (XS1 - 0.0035, Y_END, Z_BOT), (XS1, Y_BR, Z_FIN0 + 0.002), bevel=0.001, mat_=M["plastic"], coll=coll))

    # ------------------------------------------------------------ backplate
    bp = B("g_backplate", (XS0, Y_END, Z_BP0), (0.0735, Y_BR - 0.001, Z_BP1), bevel=0.0008, mat_=M["backplate"], coll=coll)
    boolean_cut(bp, [
        B("cut", (-0.047, -0.077, Z_BP0 - 0.01), (0.061, -0.036, Z_BP1 + 0.01), bevel=0.004, coll=coll),
        B("cut", (-0.065, CONN[1] - 0.003, Z_BP0 - 0.01), (CONN[2] + 0.004, CONN[3] + 0.003, Z_BP1 + 0.01), bevel=0.002, coll=coll),
    ])
    me = bp.data
    uvl = me.uv_layers.active
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = ((Y_BR - co.y) / (Y_BR - Y_END), (co.x - XS0) / (0.0735 - XS0))
    P.append(bp)
    for (x, y) in ((0.0, 0.085), (0.042, 0.085), (0.0, 0.14), (0.042, 0.14)):
        P.append(cyl("g_bpscrew", 0.0022, 0.0012, (x, y, Z_BP1 + 0.0006), "Z", 14, bevel=0.0004, mat_=M["screw"], coll=coll))
    # rejilla visible en el flow-through: soporte en cruz
    P.append(B("g_ft_bar", (-0.047, -0.0575, Z_BP0), (0.061, -0.0555, Z_BP1), mat_=M["alu_dark"], coll=coll))

    # ------------------------------------------------------------ conector 12V-2x6
    x0, y0, x1, y1 = CONN
    con = B("g_12v", (x0, y0, ZP + PCB_T / 2), (x1, y1, ZP + 0.0105), bevel=0.0005, mat_=M["connector"], coll=coll)
    cuts = []
    for c in range(6):
        for r in range(2):
            y = y0 + 0.0018 + c * 0.003
            z = ZP + 0.0028 + r * 0.0032
            cuts.append(B("cut", (x0 - 0.002, y, z), (x0 + 0.006, y + 0.0022, z + 0.0024), coll=coll))
    for c in range(4):
        cuts.append(B("cut", (x0 - 0.002, y0 + 0.003 + c * 0.0038, ZP + 0.0092), (x0 + 0.004, y0 + 0.0042 + c * 0.0038, ZP + 0.0101), coll=coll))
    boolean_cut(con, cuts)
    P.append(con)

    # ------------------------------------------------------------ soporte PCIe (3 slots) + salidas
    zb0, zb1 = 0.2165, 0.2749
    br = B("g_bracket", (-0.050, Y_BR + 0.001, zb0), (0.0765, Y_BR + 0.003, zb1), bevel=0.0004, mat_=M["steel_bare"], coll=coll)
    cuts = []
    for k in range(9):
        cuts.append(B("cut", (-0.044 + k * 0.0125, Y_BR, zb0 + 0.004), (-0.037 + k * 0.0125, Y_BR + 0.01, zb0 + 0.034), bevel=0.002, coll=coll))
    boolean_cut(br, cuts)
    P.append(br)
    for i, x in enumerate((-0.036, -0.014, 0.008, 0.030)):
        w = 0.0165 if i < 3 else 0.0155
        sh = B("g_port", (x - w / 2, Y_BR + 0.002, 0.2625), (x + w / 2, Y_BR + 0.0065, 0.2685), bevel=0.0006, mat_=M["tin"], coll=coll)
        P.append(sh)
        P.append(B("g_port_in", (x - w / 2 + 0.0012, Y_BR + 0.0062, 0.2637), (x + w / 2 - 0.0012, Y_BR + 0.0068, 0.2673), mat_=M["plastic"], coll=coll))

    gpu = join(P, "GPU")
    set_origin(gpu, (0.082, 0.1255, ZP))

    # ------------------------------------------------------------ ventiladores 90 mm (11 aspas con anillo)
    rot = build_fans.blades_mesh("g_blades", 11, 0.0165, FAN_R - 0.0016, 0.011, M["fan_blade_black"], coll, sweep=0.55, skew=0.4, tip_ring=True, axis="Z")
    hub = cyl("g_hub", 0.0165, 0.012, (0, 0, 0), "Z", 40, bevel=0.0015, mat_=M["fan_frame"], coll=coll)
    cap = cyl("g_hubcap", 0.0135, 0.0006, (0, 0, -0.0062), "Z", 40, mat_=M["alu_dark"], coll=coll)
    rotor = join([rot, hub, cap], "g_rotor")
    rotor.data.name = "GPUFanRotor90"
    for i, y in enumerate(FAN_Y):
        o = bpy.data.objects.new(f"GPU_Fan{i + 1}_Rotor", rotor.data)
        coll.objects.link(o)
        o.location = (FAN_X, y, Z_BOT + 0.0072)
        lib.parent_keep(o, gpu)
    # buje fijo del motor (3 brazos) en cada ventilador
    bpy.data.objects.remove(rotor, do_unlink=True)
    return gpu
