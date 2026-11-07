"""Utilidades de modelado procedural para Blender 5.x (bpy + bmesh)."""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEX = os.path.join(ROOT, "assets-src", "textures")


# ------------------------------------------------------------------ colecciones
def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def clear_collection(name):
    c = bpy.data.collections.get(name)
    if not c:
        return
    for o in list(c.objects):
        me = o.data if o.type == "MESH" else None
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)


def link(obj, coll):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


# ------------------------------------------------------------------ materiales
def _img(path, non_color=False):
    name = os.path.basename(path)
    im = bpy.data.images.get(name)
    if im is None:
        im = bpy.data.images.load(path, check_existing=True)
    if non_color:
        im.colorspace_settings.name = "Non-Color"
    return im


def mat(name, color=(0.5, 0.5, 0.5), metal=0.0, rough=0.5, *, emission=None, emission_strength=0.0,
        alpha=1.0, transmission=0.0, ior=1.5, coat=0.0, coat_rough=0.03, albedo_tex=None, mr_tex=None,
        normal_tex=None, normal_strength=1.0, emission_tex=None, alpha_clip_tex=None, specular=0.5):
    """Material Principled compatible con glTF. Si existe se reconstruye."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs[0], out.inputs[0])
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["IOR"].default_value = ior
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = specular
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    if transmission > 0:
        b.inputs["Transmission Weight"].default_value = transmission
    if coat > 0:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = coat_rough
    if emission is not None:
        b.inputs["Emission Color"].default_value = (*emission, 1.0)
        b.inputs["Emission Strength"].default_value = emission_strength
    y = 300
    if albedo_tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(os.path.join(TEX, albedo_tex))
        t.location = (-600, y); y -= 300
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    if mr_tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(os.path.join(TEX, mr_tex), True)
        t.location = (-800, y); y -= 300
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        sep.location = (-400, y + 300)
        nt.links.new(t.outputs["Color"], sep.inputs[0])
        nt.links.new(sep.outputs[1], b.inputs["Roughness"])
        nt.links.new(sep.outputs[2], b.inputs["Metallic"])
    if normal_tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(os.path.join(TEX, normal_tex), True)
        t.location = (-800, y); y -= 300
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.location = (-300, y + 300)
        nm.inputs["Strength"].default_value = normal_strength
        nt.links.new(t.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs[0], b.inputs["Normal"])
    if emission_tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(os.path.join(TEX, emission_tex))
        t.location = (-600, y); y -= 300
        nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emission_strength or 1.0
    if alpha_clip_tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(os.path.join(TEX, alpha_clip_tex))
        t.location = (-600, y); y -= 300
        r = nt.nodes.new("ShaderNodeMath")
        r.operation = "ROUND"
        nt.links.new(t.outputs["Alpha"], r.inputs[0])
        nt.links.new(r.outputs[0], b.inputs["Alpha"])
        try:
            m.surface_render_method = "DITHERED"
        except Exception:
            pass
    m.diffuse_color = (*color, alpha)
    return m


# ------------------------------------------------------------------ mallas
def _obj_from_bm(name, bm, mat_=None, coll=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    if mat_ is not None:
        me.materials.append(mat_)
    return o


def box_uv(bm, scale=1.0, origin=(0, 0, 0)):
    """Proyección cúbica en coordenadas de mundo (metros/escala) para texturas que se repiten."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            co = l.vert.co
            if ax == 0:
                u_, v_ = co.y, co.z
            elif ax == 1:
                u_, v_ = co.x, co.z
            else:
                u_, v_ = co.x, co.y
            l[uv].uv = (u_ / scale, v_ / scale)


def bevel_bm(bm, width, segments=2, edges=None):
    if width <= 0:
        return
    es = edges if edges is not None else list(bm.edges)
    bmesh.ops.bevel(bm, geom=es, offset=width, offset_type="OFFSET", segments=segments,
                    profile=0.5, affect="EDGES", clamp_overlap=True)


def box(name, size, loc=(0, 0, 0), bevel=0.0, seg=2, mat_=None, coll=None, uv_scale=0.1, rot=None):
    """Caja centrada en loc con tamaño (sx, sy, sz) en metros."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bevel_bm(bm, min(bevel, min(size) * 0.49), seg)
    if rot is not None:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=rot)
    for v in bm.verts:
        v.co += Vector(loc)
    box_uv(bm, uv_scale)
    o = _obj_from_bm(name, bm, mat_, coll)
    shade(o, 35)
    return o


def box_minmax(name, mn, mx, **kw):
    size = tuple(mx[i] - mn[i] for i in range(3))
    loc = tuple((mx[i] + mn[i]) / 2 for i in range(3))
    return box(name, size, loc, **kw)


def cyl(name, r, depth, loc=(0, 0, 0), axis="Z", verts=32, bevel=0.0, seg=2, mat_=None, coll=None, r2=None,
        uv_scale=0.1, cap=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=depth)
    if bevel > 0:
        cap_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-7]
        bevel_bm(bm, bevel, seg, cap_edges)
    if axis == "X":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
    elif axis == "Y":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
    for v in bm.verts:
        v.co += Vector(loc)
    box_uv(bm, uv_scale)
    o = _obj_from_bm(name, bm, mat_, coll)
    shade(o, 40)
    return o


def plane(name, w, h, loc, normal="X-", mat_=None, coll=None, uv=(0, 0, 1, 1), rot90=False):
    """Plano rectangular (decal) con UV 0..1. normal: hacia dónde mira la cara.
    rot90: el eje u de la textura corre a lo largo del lado h (texto girado 90°)."""
    bm = bmesh.new()
    hw, hh = w / 2, h / 2
    # plano local en XY mirando +Z, u a lo largo de X, v a lo largo de Y
    vs = [bm.verts.new(c) for c in ((-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0))]
    f = bm.faces.new(vs)
    uvl = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv
    corners = ((u0, v1), (u0, v0), (u1, v0), (u1, v1)) if rot90 else ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
    for l, c in zip(f.loops, corners):
        l[uvl].uv = c
    rots = {
        "Z+": Matrix.Identity(3),
        "Z-": Matrix.Rotation(math.pi, 3, "X"),
        # Mirando -X: u -> -Y (hacia el frente de la caja visto desde el cristal => izquierda->derecha), v -> +Z
        "X-": Matrix(((0, 0, -1), (-1, 0, 0), (0, 1, 0))),
        "X+": Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0))),
        "Y-": Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0))),
        "Y+": Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0))),
    }
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=rots[normal])
    for v in bm.verts:
        v.co += Vector(loc)
    return _obj_from_bm(name, bm, mat_, coll)


def shade(o, angle_deg=35):
    me = o.data
    for p in me.polygons:
        p.use_smooth = True
    try:
        me.set_sharp_from_angle(angle=math.radians(angle_deg))
    except Exception:
        pass


def flat(o):
    for p in o.data.polygons:
        p.use_smooth = False


def apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    old = o.data
    o.modifiers.clear()
    o.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return o


def boolean_cut(o, cutters, solver="EXACT"):
    for c in cutters:
        md = o.modifiers.new("cut", "BOOLEAN")
        md.operation = "DIFFERENCE"
        md.object = c
        try:
            md.solver = solver
        except TypeError:
            pass
    apply_mods(o)
    for c in cutters:
        me = c.data
        bpy.data.objects.remove(c, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    shade(o, 30)
    return o


def join(objs, name):
    objs = [o for o in objs if o is not None]
    base = objs[0]
    for o in objs:
        if o.modifiers:
            apply_mods(o)
    with bpy.context.temp_override(active_object=base, selected_editable_objects=objs, selected_objects=objs,
                                   object=base):
        bpy.ops.object.join()
    base.name = name
    base.data.name = name
    return base


def set_origin(o, world_pt):
    """Mueve el origen del objeto a world_pt sin mover la geometría."""
    p = Vector(world_pt)
    local = o.matrix_world.inverted() @ p
    o.data.transform(Matrix.Translation(-local))
    o.matrix_world = o.matrix_world @ Matrix.Translation(local)
    return o


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = mw


def bezier_tube(name, pts, radius, mat_=None, coll=None, res=6, bevel_res=3, handles="AUTO"):
    """Tubo (cable/heatpipe) por una spline Bézier que pasa por pts. Devuelve malla."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = res
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p)
        bp.handle_left_type = handles
        bp.handle_right_type = handles
    o = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(o)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
    bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.curves.remove(cu)
    mo = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(mo)
    if mat_ is not None:
        me.materials.clear()
        me.materials.append(mat_)
    shade(mo, 60)
    return mo


def poly_tube(name, pts, radius, mat_=None, coll=None, bend_r=0.006, res=6, bevel_res=3):
    """Tubo por una polilínea con codos redondeados (radio bend_r) usando Bézier con handles calculados."""
    P = [Vector(p) for p in pts]
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = res
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    pts2 = [P[0]]
    for i in range(1, len(P) - 1):
        a = (P[i - 1] - P[i]).normalized()
        b = (P[i + 1] - P[i]).normalized()
        la = min(bend_r, (P[i - 1] - P[i]).length * 0.45)
        lb = min(bend_r, (P[i + 1] - P[i]).length * 0.45)
        pts2 += [P[i] + a * la, ("C", P[i]), P[i] + b * lb]
    pts2.append(P[-1])
    # construir: segmentos rectos con puntos VECTOR y codos con handle en la esquina
    sp = cu.splines.new("BEZIER")
    plain = [p for p in pts2 if not isinstance(p, tuple)]
    sp.bezier_points.add(len(plain) - 1)
    corners = [p[1] for p in pts2 if isinstance(p, tuple)]
    k = 0
    for i, bp in enumerate(sp.bezier_points):
        bp.co = plain[i]
        bp.handle_left_type = "FREE"
        bp.handle_right_type = "FREE"
    # handles: por defecto en línea recta
    bps = sp.bezier_points
    for i, bp in enumerate(bps):
        prev = bps[i - 1].co if i > 0 else bp.co - (bps[i + 1].co - bp.co)
        nxt = bps[i + 1].co if i < len(bps) - 1 else bp.co + (bp.co - bps[i - 1].co)
        bp.handle_left = bp.co + (prev - bp.co) / 3
        bp.handle_right = bp.co + (nxt - bp.co) / 3
    # codos: entre plain[1+2j] y plain[2+2j]
    for j, c in enumerate(corners):
        p0 = bps[1 + 2 * j]
        p1 = bps[2 + 2 * j]
        p0.handle_right = p0.co + (c - p0.co) * 0.552
        p1.handle_left = p1.co + (c - p1.co) * 0.552
    o = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(o)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
    bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.curves.remove(cu)
    mo = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(mo)
    if mat_ is not None:
        me.materials.clear()
        me.materials.append(mat_)
    shade(mo, 60)
    return mo


def array_copy(src, offsets, name=None):
    """Duplica la malla de src en varios offsets y lo une todo en un objeto."""
    out = [src]
    for i, off in enumerate(offsets):
        o = src.copy()
        o.data = src.data.copy()
        o.location = src.location + Vector(off)
        for c in src.users_collection:
            c.objects.link(o)
        out.append(o)
    return join(out, name or src.name)


def tri_count(objs=None):
    dg = bpy.context.evaluated_depsgraph_get()
    t = 0
    for o in objs or bpy.context.scene.objects:
        if o.type == "MESH":
            t += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return t
