"""Exporta las piezas del PC a GLB (sin comprimir; la compresión la hace tools/optimize-glb.mjs).

Uso en Blender (con blender/pc.blend abierto): exec(open(r".../export_glb.py").read()); export()
"""
import os

import bpy

# Raíz del proyecto relativa al .blend (blender/pc.blend -> ..); ruta fija solo como respaldo
_BLEND_DIR = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else ""
ROOT = os.path.dirname(_BLEND_DIR) if _BLEND_DIR else r"C:\Users\Brandon David\Projects\pc-desmontado"
OUT = os.path.join(ROOT, "assets-src", "pc_raw.glb")
PC_SCENE = "Scene"

# Debe coincidir con ALL_NODE_NAMES de src/scene/parts.ts (lo valida tools/optimize-glb.mjs)
TOP = ["Case", "GlassPanel", "FanFront1", "FanFront2", "FanFront3", "FanRear", "GPU", "CablePCIe",
       "CPUCooler", "CPU", "ThermalPaste", "RAM1", "RAM2", "RAM3", "RAM4", "SSD", "SSDHeatsink",
       "PSU", "Cable24Pin", "CableEPS", "Motherboard"]

EXPECTED = {"Case": (0.0, 0.0, 0.0), "CPU": (0.083, 0.094, 0.367), "GPU": (0.082, 0.1255, 0.2735), "PSU": (0.0, 0.145, 0.0595)}


def check_positions(tol=0.002):
    """Evita exportar si alguien ha movido piezas a mano en la interfaz (los scripts son la fuente de verdad)."""
    bad = []
    for n, p in EXPECTED.items():
        loc = bpy.data.objects[n].location
        if any(abs(loc[i] - p[i]) > tol for i in range(3)):
            bad.append(f"{n} en {tuple(round(v, 3) for v in loc)} (esperado {p})")
    if bad:
        raise RuntimeError("Piezas movidas; ejecuta build() antes de exportar: " + "; ".join(bad))


def export(path=OUT):
    # Primero la escena del PC: el archivo puede contener otras escenas ajenas al proyecto
    pc_scene = bpy.data.scenes[PC_SCENE]
    win = bpy.context.window
    prev_scene = win.scene if win is not None else None
    if win is not None and win.scene != pc_scene:
        win.scene = pc_scene
    check_positions()
    vl = bpy.context.view_layer
    prev_sel = {o.name for o in vl.objects if o.select_get()}
    prev_hidden = {o.name for o in vl.objects if o.hide_get()}
    prev_active = vl.objects.active
    try:
        for o in vl.objects:
            o.select_set(False)
        sel = []
        for n in TOP:
            o = bpy.data.objects[n]
            o.hide_set(False)
            o.select_set(True)
            sel.append(o)
            for c in o.children_recursive:
                c.hide_set(False)
                c.select_set(True)
        vl.objects.active = sel[0]
        kw = dict(filepath=path, export_format="GLB", use_selection=True, use_active_scene=True, export_apply=True,
                  export_yup=True, export_texcoords=True, export_normals=True, export_tangents=False,
                  export_materials="EXPORT", export_image_format="AUTO", export_cameras=False, export_lights=False,
                  export_extras=False, export_animations=False, export_draco_mesh_compression_enable=False)
        props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
        kw = {k: v for k, v in kw.items() if k in props}
        bpy.ops.export_scene.gltf(**kw)
    finally:
        # Restaura selección, visibilidad, objeto activo y escena del usuario
        for o in vl.objects:
            o.select_set(o.name in prev_sel)
            o.hide_set(o.name in prev_hidden)
        vl.objects.active = prev_active
        if win is not None and prev_scene is not None and win.scene != prev_scene:
            win.scene = prev_scene
    print("exported", path, os.path.getsize(path) // 1024, "KB")
    return path
