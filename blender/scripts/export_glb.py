"""Exporta las piezas del PC a GLB (sin comprimir; la compresión la hace tools/optimize-glb.mjs).

Uso en Blender: exec(open(r".../export_glb.py").read()); export()
"""
import os

import bpy

ROOT = r"C:\Users\Brandon David\Projects\pc-desmontado"
OUT = os.path.join(ROOT, "assets-src", "pc_raw.glb")

TOP = ["Case", "GlassPanel", "FanFront1", "FanFront2", "FanFront3", "FanRear", "GPU", "CablePCIe",
       "CPUCooler", "CPU", "ThermalPaste", "RAM1", "RAM2", "RAM3", "RAM4", "SSD", "SSDHeatsink",
       "PSU", "Cable24Pin", "CableEPS", "Motherboard"]


def export(path=OUT):
    for o in bpy.context.view_layer.objects:
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
    bpy.context.view_layer.objects.active = sel[0]
    # Solo la escena del PC: el archivo puede contener otras escenas ajenas al proyecto
    pc_scene = bpy.data.scenes["Scene"]
    if bpy.context.window is not None and bpy.context.window.scene != pc_scene:
        bpy.context.window.scene = pc_scene
    kw = dict(filepath=path, export_format="GLB", use_selection=True, use_active_scene=True, export_apply=True, export_yup=True,
              export_texcoords=True, export_normals=True, export_tangents=False, export_materials="EXPORT",
              export_image_format="AUTO", export_cameras=False, export_lights=False, export_extras=False,
              export_animations=False, export_draco_mesh_compression_enable=False)
    props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    kw = {k: v for k, v in kw.items() if k in props}
    bpy.ops.export_scene.gltf(**kw)
    print("exported", path, os.path.getsize(path) // 1024, "KB")
    return path
