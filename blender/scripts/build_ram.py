"""4 módulos DDR5 con disipador y barra ARGB (RAM1..RAM4, malla compartida)."""
import bpy

import layout as L
import lib
from lib import join, set_origin
from build_motherboard import mb, W

V0 = (L.DIMM_V[0] + L.DIMM_V[1]) / 2 - 133.35 / 2
V1 = V0 + 133.35
H0 = 2.5


def stick(M, coll, u):
    P = []
    P.append(mb("r_pcb", u - 0.6, V0, u + 0.6, V1, H0, H0 + 31.25, M, M["ram_pcb"], coll))
    # contactos dorados
    P.append(mb("r_gold", u - 0.62, V0 + 2, u + 0.62, V1 - 2, H0, H0 + 4, M, M["gold"], coll))
    # disipador (dos mitades) con perfil escalonado
    for s in (-1, 1):
        a, b = (u + 0.6, u + 3.4) if s > 0 else (u - 3.4, u - 0.6)
        P.append(mb("r_hs", a, V0 + 0.5, b, V1 - 0.5, H0 + 6.5, H0 + 38.5, M, M["alu_dark"], coll, bevel=0.5, seg=2))
        # nervio superior
        P.append(mb("r_rib", a, V0 + 0.5, b + 0.2 * s, V1 - 0.5, H0 + 33.5, H0 + 36, M, M["alu_black"], coll, bevel=0.3))
        # etiqueta en la cara
        face_u = b + 0.02 if s > 0 else a - 0.02
        lbl = lib.plane("r_label", 0.0255, 0.118, W(face_u, (V0 + V1) / 2, H0 + 20.5), "Y-" if s > 0 else "Y+", M["ram_label"], coll, rot90=True)
        P.append(lbl)
    # barra difusora ARGB
    P.append(mb("r_bar", u - 3.2, V0 + 2, u + 3.2, V1 - 2, H0 + 38.5, H0 + 41.5, M, M["rgb"], coll, bevel=0.8, seg=2))
    # UV del anillo RGB: degradado a lo largo de la barra
    bar = P[-1]
    me = bar.data
    uvl = me.uv_layers.active
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = (((L.MB_Z0 - co.z) * 1000 - V0) / 133.35 * 0.5 + 0.1, 0.5)
    P.append(mb("r_cap", u - 3.5, V0 + 0.5, u + 3.5, V1 - 0.5, H0 + 41.5, H0 + 42.5, M, M["alu_black"], coll, bevel=0.4))
    return join(P, "ram")


def build(M, coll):
    lib.clear_collection(coll.name)
    u = L.DIMM_U[0]
    src = stick(M, coll, u)
    set_origin(src, W(u, (V0 + V1) / 2, H0))
    src.data.name = "RAM_DDR5"
    outs = []
    for i, ui in enumerate(L.DIMM_U):
        o = bpy.data.objects.new(f"RAM{i + 1}", src.data)
        coll.objects.link(o)
        o.location = W(ui, (V0 + V1) / 2, H0)
        outs.append(o)
    bpy.data.objects.remove(src, do_unlink=True)
    return outs
