"""CPU AM5 (sustrato + IHS con faldón de 8 muescas y meseta) y pasta térmica (ThermalPaste)."""
import math
import random

import bmesh
import bpy

import layout as L
import lib
from lib import boolean_cut, join, set_origin
from build_motherboard import mb, W

H_SUB0, H_SUB1 = 2.0, 3.2       # sustrato
H_SKIRT = 4.35                   # faldón del IHS (lo pisa el ILM)
H_IHS = 7.2                      # cara superior de la meseta
PLAT = 17.0                      # semilado de la meseta (34 x 34 mm)
PASTE_MAX = 0.24                 # mm


def _uv_top(o, cu, cv, half):
    me = o.data
    uvl = me.uv_layers.active or me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            u = (L.MB_Y0 - co.y) * 1000
            v = (L.MB_Z0 - co.z) * 1000
            uvl.data[li].uv = ((u - (cu - half)) / (2 * half), 1 - (v - (cv - half)) / (2 * half))


def paste_mesh(M, coll, cu, cv):
    """Pasta tras levantar el disipador: contorno orgánico suave y relieve de "helecho"."""
    rng = random.Random(11)
    NA, NR = 120, 22
    ph = [rng.uniform(0, 6.28) for _ in range(6)]

    def edge(a):
        return (14.6 + 1.3 * math.sin(a * 4 + ph[0]) + 1.0 * math.sin(a * 7 + ph[1]) + 0.55 * math.sin(a * 13 + ph[2])
                + 0.3 * math.sin(a * 23 + ph[3]))

    def hgt(x, y, s):
        # s = r/edge en [0,1]
        base = PASTE_MAX * (1 - s ** 4) ** 1.2
        # patrón de "levantado": crestas ramificadas que salen radiales del centro
        r = math.hypot(x, y) + 1e-6
        a = math.atan2(y, x)
        f1 = math.sin(a * 9 + 0.35 * r + 1.2 * math.sin(r * 0.7 + ph[4]))
        f2 = math.sin(a * 23 + 0.9 * math.sin(r * 1.3 + ph[5]))
        f3 = math.sin(x * 2.9 + y * 1.7) * math.sin(y * 3.1 - x * 0.9)
        k = min(1.0, r / 7.0) ** 2          # sin pellizco radial en el centro
        ridge = 0.5 + 0.5 * max(-1.0, min(1.0, k * (0.6 * f1 + 0.25 * f2) + 0.45 * f3))
        return base * (0.25 + 0.75 * ridge ** 1.5) + 0.01

    bm = bmesh.new()
    center = bm.verts.new(W(cu, cv, H_IHS + hgt(0, 0, 0)))
    rings = []
    for i in range(1, NR + 1):
        s = i / NR
        ring = []
        for j in range(NA):
            a = 2 * math.pi * j / NA
            r = edge(a) * s
            x, y = r * math.cos(a), r * math.sin(a)
            h = hgt(x, y, s) if i < NR else 0.005
            ring.append(bm.verts.new(W(cu + x, cv + y, H_IHS + h)))
        rings.append(ring)
    for j in range(NA):
        bm.faces.new((center, rings[0][j], rings[0][(j + 1) % NA]))
    for i in range(NR - 1):
        for j in range(NA):
            a, b = rings[i][j], rings[i][(j + 1) % NA]
            c, d = rings[i + 1][(j + 1) % NA], rings[i + 1][j]
            bm.faces.new((a, d, c, b))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if sum(f.normal.x for f in bm.faces) > 0:
        for f in bm.faces:
            f.normal_flip()
    lib.box_uv(bm, 0.02)
    o = lib._obj_from_bm("ThermalPaste", bm, M["paste"], coll)
    lib.shade(o, 89)
    return o


def build(M, coll):
    lib.clear_collection(coll.name)
    cu, cv = L.SOCKET_C
    P = []
    P.append(mb("cpu_sub", cu - 20, cv - 20, cu + 20, cv + 20, H_SUB0, H_SUB1, M, M["ram_pcb"], coll, bevel=0.3, seg=1))
    P.append(mb("cpu_pads", cu - 18, cv - 18, cu + 18, cv + 18, H_SUB0 - 0.05, H_SUB0, M, M["gold"], coll))
    # faldón con 8 muescas
    skirt = mb("cpu_skirt", cu - 19, cv - 19, cu + 19, cv + 19, H_SUB1, H_SKIRT, M, M["nickel"], coll, bevel=0.4, seg=1)
    cuts = []
    for s in (-1, 1):
        for off in (-9.5, 9.5):
            cuts.append(mb("cut", cu + s * 19 - 4.5, cv + off - 3.5, cu + s * 19 + 4.5, cv + off + 3.5, H_SUB1 - 1, H_SKIRT + 1, M, None, coll))
            cuts.append(mb("cut", cu + off - 3.5, cv + s * 19 - 4.5, cu + off + 3.5, cv + s * 19 + 4.5, H_SUB1 - 1, H_SKIRT + 1, M, None, coll))
    boolean_cut(skirt, cuts)
    P.append(skirt)
    plat = mb("cpu_ihs", cu - PLAT, cv - PLAT, cu + PLAT, cv + PLAT, H_SKIRT - 0.1, H_IHS, M, M["ihs"], coll, bevel=1.6, seg=3)
    _uv_top(plat, cu, cv, PLAT)
    P.append(plat)
    # SMD visibles en las muescas
    for s in (-1, 1):
        for off in (-9.5, 9.5):
            for (du, dv) in ((s * 17.2, off), (off, s * 17.2)):
                for k in range(3):
                    if abs(du) > abs(dv):
                        a, b = cu + du - 0.5, cv + dv - 2.4 + k * 1.8
                        P.append(mb("cpu_smd", a, b, a + 1.0, b + 0.6, H_SUB1, H_SUB1 + 0.5, M, M["pcb_edge"], coll))
                    else:
                        a, b = cu + du - 2.4 + k * 1.8, cv + dv - 0.5
                        P.append(mb("cpu_smd", a, b, a + 0.6, b + 1.0, H_SUB1, H_SUB1 + 0.5, M, M["pcb_edge"], coll))
    cpu = join(P, "CPU")
    set_origin(cpu, W(cu, cv, H_SUB0))

    paste = paste_mesh(M, coll, cu, cv)
    set_origin(paste, W(cu, cv, H_IHS))
    return cpu, paste
