"""Ventiladores de caja 120 mm ARGB (3 frontales + 1 trasero) y generador de ventiladores reutilizable.

Cada ventilador: objeto marco (nombre de la pieza) + hijo "<nombre>_Rotor" (aspas + buje) que la
web puede girar sobre su eje (eje Y en Blender = eje Z en three.js).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import lib
from lib import box_minmax as B, cyl, boolean_cut, join, set_origin


def blades_mesh(name, n, r_hub, r_tip, depth, mat_, coll, sweep=0.62, thick=0.0011, skew=0.32, tip_ring=False, axis="Y"):
    """Aspas con torsión y curvatura. Eje de giro = Y (o Z). Centro en el origen."""
    bm = bmesh.new()
    NR, NT = 9, 10
    for b in range(n):
        phi = 2 * math.pi * b / n
        grid = []
        for i in range(NR + 1):
            s = i / NR
            r = r_hub * 0.98 + (r_tip - r_hub * 0.98) * s
            sw = sweep * (1.0 - 0.25 * s)
            d = depth * (1.0 - 0.2 * s)
            row = []
            for j in range(NT + 1):
                t = j / NT
                th = phi + sw * (t - 0.5) + skew * s * s
                a = d * (t - 0.5) + 0.0025 * math.sin(math.pi * t) * (0.5 + s)
                x, z = r * math.cos(th), r * math.sin(th)
                row.append(bm.verts.new((x, a, z)))
            grid.append(row)
        for i in range(NR):
            for j in range(NT):
                bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lib.box_uv(bm, 0.05)
    o = lib._obj_from_bm(name, bm, mat_, coll)
    md = o.modifiers.new("solid", "SOLIDIFY")
    md.thickness = thick
    md.offset = 0
    lib.apply_mods(o)
    lib.shade(o, 50)
    parts = [o]
    if tip_ring:
        ring = cyl(name + "_ring", r_tip + 0.0012, depth * 0.55, (0, 0, 0), "Y", 64, mat_=mat_, coll=coll)
        inner = cyl("cut", r_tip - 0.0005, depth, (0, 0, 0), "Y", 64, coll=coll)
        boolean_cut(ring, [inner])
        parts.append(ring)
    o = join(parts, name) if len(parts) > 1 else o
    if axis == "Z":
        o.data.transform(Matrix.Rotation(-math.pi / 2, 4, "X"))
    return o


def case_fan_meshes(M, coll, size=0.12, depth=0.025, rgb=True, blade_mat=None):
    """Devuelve (marco, rotor) centrados en el origen, eje Y, lado de admisión hacia -Y."""
    h = size / 2
    frame = B("fan_frame", (-h, -depth / 2, -h), (h, depth / 2, h), bevel=0.006, seg=3, mat_=M["fan_frame"], coll=coll)
    bore = 0.0585 * size / 0.12
    cutters = [cyl("cut", bore, depth * 2, (0, 0, 0), "Y", 72, coll=coll)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            cutters.append(cyl("cut", 0.00215, depth * 2, (sx * (h - 0.0075), 0, sz * (h - 0.0075)), "Y", 12, coll=coll))
    # rebajes en las caras laterales del marco (aligera, como los reales)
    for s_ in (-1, 1):
        cutters.append(B("cut", (-h + 0.014, -depth / 2 + 0.004, s_ * h - 0.01), (h - 0.014, depth / 2 - 0.004, s_ * h + 0.01), coll=coll))
        cutters.append(B("cut", (s_ * h - 0.01, -depth / 2 + 0.004, -h + 0.014), (s_ * h + 0.01, depth / 2 - 0.004, h - 0.014), coll=coll))
    boolean_cut(frame, cutters)
    parts = [frame]
    # Soportes del motor (4 brazos) en la cara de salida (+Y)
    hub_r = 0.0205 * size / 0.12
    for k in range(4):
        a = math.radians(45 + 90 * k)
        L = bore + 0.002 - hub_r
        mid = hub_r + L / 2
        arm = B("fan_arm", (-L / 2, -0.0015, -0.0022), (L / 2, 0.0015, 0.0022), mat_=M["fan_frame"], coll=coll)
        arm.data.transform(Matrix.Rotation(-a, 4, "Y"))
        arm.data.transform(Matrix.Translation((mid * math.cos(a), depth / 2 - 0.0035, mid * math.sin(a))))
        parts.append(arm)
    parts.append(cyl("fan_motor", hub_r * 0.95, 0.004, (0, depth / 2 - 0.003, 0), "Y", 40, mat_=M["fan_frame"], coll=coll))
    # Anillos ARGB en el borde del orificio (delante y detrás)
    if rgb:
        for yy in (-depth / 2 + 0.0025, depth / 2 - 0.0025):
            ring = cyl("fan_rgb", bore + 0.0006, 0.003, (0, yy, 0), "Y", 72, mat_=M["rgb"], coll=coll)
            boolean_cut(ring, [cyl("cut", bore - 0.0009, 0.01, (0, yy, 0), "Y", 72, coll=coll)])
            # UV: u = ángulo alrededor del anillo (para el degradado RGB)
            me = ring.data
            uvl = me.uv_layers.active or me.uv_layers.new()
            for poly in me.polygons:
                for li in poly.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    ang = (math.atan2(co.z, co.x) / (2 * math.pi)) % 1.0
                    uvl.data[li].uv = (ang, 0.5)
            parts.append(ring)
    fr = join(parts, "fan_frame")

    # Rotor: buje + aspas
    bl = blades_mesh("fan_blades", 9, hub_r, bore - 0.0018, depth * 0.62, blade_mat or (M["fan_blade_rgb"] if rgb else M["fan_blade_black"]), coll)
    bl.data.transform(Matrix.Translation((0, -0.0015, 0)))
    hub = cyl("fan_hub", hub_r, depth * 0.72, (0, -0.0015, 0), "Y", 48, bevel=0.0015, mat_=M["fan_frame"], coll=coll)
    cap = cyl("fan_cap", hub_r * 0.8, 0.0006, (0, -0.0015 - depth * 0.36 - 0.0002, 0), "Y", 48, mat_=M["plastic_gloss"], coll=coll)
    rot = join([bl, hub, cap], "fan_rotor")
    return fr, rot


def place_fan(name, frame_src, rotor_src, loc, coll, rot=None):
    fr = bpy.data.objects.new(name, frame_src.data)
    coll.objects.link(fr)
    fr.location = loc
    ro = bpy.data.objects.new(name + "_Rotor", rotor_src.data)
    coll.objects.link(ro)
    ro.parent = fr
    ro.location = (0, 0, 0)
    if rot is not None:
        fr.rotation_euler = rot
    return fr


def build(M, coll):
    lib.clear_collection(coll.name)
    fr, ro = case_fan_meshes(M, coll)
    fr.data.name = "FanFrame120"
    ro.data.name = "FanRotor120"
    out = []
    for i, z in enumerate((0.14, 0.265, 0.39)):
        out.append(place_fan(f"FanFront{i + 1}", fr, ro, (-0.01, -0.2055, z), coll))
    out.append(place_fan("FanRear", fr, ro, (-0.024, 0.2115, 0.367), coll))
    # eliminar los objetos fuente (las mallas siguen vivas por los usuarios nuevos)
    bpy.data.objects.remove(fr, do_unlink=True)
    bpy.data.objects.remove(ro, do_unlink=True)
    return out
