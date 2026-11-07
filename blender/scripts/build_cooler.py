"""Disipador de torre: base niquelada, 6 heatpipes de cobre en U, 52 aletas de aluminio,
tapa superior y ventilador de 120 mm (CPUCooler + hijo CPUCooler_Rotor)."""
import math

import bpy
from mathutils import Matrix

import layout as L
import lib
from lib import boolean_cut, join, set_origin, cyl
from build_motherboard import mb, mbcyl, W
import build_fans

H_BASE0 = 7.62          # apoya sobre la pasta (IHS 7.2 + pasta)
H_BASE1 = 13.0
FIN0, FIN1 = 47.0, 160.0
FIN_U = 50.0            # profundidad de aletas (dirección del flujo de aire, eje u)
FIN_V = 125.0           # anchura de las aletas (eje v)
N_FINS = 52


def build(M, coll):
    lib.clear_collection(coll.name)
    cu, cv = L.SOCKET_C
    P = []
    # Base (cobre niquelado) + bloque de anclaje
    P.append(mb("cl_base", cu - 20, cv - 21, cu + 20, cv + 21, H_BASE0, H_BASE0 + 3.0, M, M["nickel"], coll, bevel=0.6))
    P.append(mb("cl_block", cu - 19, cv - 24, cu + 19, cv + 24, H_BASE0 + 3.0, H_BASE1 + 3.5, M, M["alu_black"], coll, bevel=1.2))
    # Puente de montaje y tornillos (54 x 90 mm)
    P.append(mb("cl_bridge", cu - 4.5, cv - 47, cu + 4.5, cv + 47, H_BASE1 + 3.5, H_BASE1 + 6.0, M, M["steel_bare"], coll, bevel=0.8))
    for sv in (-1, 1):
        P.append(mbcyl("cl_screw", cu, cv + sv * 45, 3.2, H_BASE1 + 6.0, H_BASE1 + 9.0, M["screw_silver"], coll, 20, 0.6))
        P.append(mbcyl("cl_spring", cu, cv + sv * 45, 2.6, H_BASE1 + 0.2, H_BASE1 + 3.6, M["steel_bare"], coll, 12))

    # Heatpipes: 6 en U. Tramo de base a lo largo de v, patas suben (h) al bloque de aletas.
    r_hp = 3.0
    legs_v = [6, 14, 22, 30, 38, 46]       # separación desde el centro (mm) para cada tubo
    order = [2, 4, 0, 5, 1, 3]
    for i in range(6):
        ub = cu + (i - 2.5) * 6.3                         # posición en la base
        row = 1 if order[i] % 2 else -1                   # tresbolillo: filas alternas
        ul = cu + row * 9.0                               # fila delantera/trasera en las aletas
        sv = legs_v[order[i]]
        for side in (-1, 1):
            pts = [
                W(ub, cv, H_BASE0 + 3.2 + r_hp),
                W(ub, cv + side * 14, H_BASE0 + 3.2 + r_hp),
                W(ub, cv + side * (14 + sv * 0.35), H_BASE1 + 14),
                W(ul, cv + side * sv, H_BASE1 + 34),
                W(ul, cv + side * sv, FIN1 + 1.8),
            ]
            P.append(lib.poly_tube(f"hp{i}_{side}", pts, r_hp / 1000, M["copper"], coll, bend_r=0.012, res=8, bevel_res=3))
            # extremo del heatpipe asomando por la tapa (cúpula baja niquelada)
            P.append(mbcyl("hp_cap", ul, cv + side * sv, r_hp + 0.1, FIN1 + 2.0, FIN1 + 3.4, M["nickel"], coll, 20, 0.65))

    # Aletas
    pitch = (FIN1 - FIN0) / (N_FINS - 1)
    fin = mb("cl_fin", cu - FIN_U / 2, cv - FIN_V / 2, cu + FIN_U / 2, cv + FIN_V / 2, 0, 0.4, M, M["fins"], coll)
    # perfil: esquinas recortadas en el borde de entrada (como aletas reales en "punta de flecha")
    boolean_cut(fin, [
        mb("cut", cu - FIN_U / 2 - 1, cv - 4, cu - FIN_U / 2 + 4, cv + 4, -1, 2, M, None, coll),
    ])
    fins = [fin]
    for k in range(1, N_FINS):
        f = fin.copy()
        f.data = fin.data
        coll.objects.link(f)
        f.location = (-(k * pitch) / 1000.0, 0, 0)
        fins.append(f)
    for f in fins:
        f.data = f.data.copy()
    fins_obj = join(fins, "cl_fins")
    fins_obj.data.transform(Matrix.Translation((-(FIN0) / 1000.0, 0, 0)))
    # aplicar location de la base
    P.append(fins_obj)
    # Tapa superior
    P.append(mb("cl_top", cu - FIN_U / 2 - 0.5, cv - FIN_V / 2 - 0.5, cu + FIN_U / 2 + 0.5, cv + FIN_V / 2 + 0.5, FIN1 + 0.4, FIN1 + 2.2, M, M["alu_black"], coll, bevel=0.8))
    # Ventilador 120 mm (sin RGB) en la cara delantera (u mayor = hacia el frente)
    cooler = join(P, "CPUCooler")
    fr, ro = build_fans.case_fan_meshes(M, coll, rgb=False)
    fu = cu + FIN_U / 2 + 12.5 + 0.5
    fan_center = W(fu, cv, (FIN0 + FIN1) / 2 + 1)
    fr.location = fan_center
    lib.apply_mods(fr)
    fr.data.transform(Matrix.Translation(fan_center))
    fr.location = (0, 0, 0)
    # clips de alambre
    clips = []
    for sv in (-1, 1):
        clips.append(lib.poly_tube("clip", [W(fu - 15, cv + sv * 58, FIN0 - 1), W(fu + 1, cv + sv * 61.5, FIN0 - 1), W(fu + 1, cv + sv * 61.5, FIN1 + 1), W(fu - 15, cv + sv * 58, FIN1 + 1)],
                                    0.0006, M["steel_bare"], coll, bend_r=0.003))
    cooler = join([cooler, fr] + clips, "CPUCooler")
    set_origin(cooler, W(cu, cv, H_BASE0))
    ro.name = "CPUCooler_Rotor"
    ro.data.name = "CoolerRotor120"
    ro.location = fan_center
    lib.parent_keep(ro, cooler)
    return cooler
