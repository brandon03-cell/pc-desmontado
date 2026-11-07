"""Punto de entrada: reconstruye piezas del PC en el Blender abierto.

Desde el MCP / consola de Blender:
    exec(open(r".../blender/scripts/run.py").read()); build(["case", "fans", ...])
"""
import importlib
import os
import sys

import bpy

SCRIPTS = os.path.join(os.path.dirname(bpy.data.filepath), "scripts") if bpy.data.filepath else \
    r"C:\Users\Brandon David\Projects\pc-desmontado\blender\scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import lib, layout, materials  # noqa: E401,E402

MODULES = {
    "case": "build_case",
    "fans": "build_fans",
    "motherboard": "build_motherboard",
    "cpu": "build_cpu",
    "cooler": "build_cooler",
    "ram": "build_ram",
    "ssd": "build_ssd",
    "gpu": "build_gpu",
    "psu": "build_psu",
    "cables": "build_cables",
}


def build(which=None):
    for m in (lib, layout, materials):
        importlib.reload(m)
    M = materials.build()
    out = {}
    for key in which or MODULES:
        mod = importlib.import_module(MODULES[key])
        importlib.reload(mod)
        coll = lib.collection("PC_" + key)
        out[key] = mod.build(M, coll)
        print("built", key, lib.tri_count(coll.objects), "tris")
    return out
