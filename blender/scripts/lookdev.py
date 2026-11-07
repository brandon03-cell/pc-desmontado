"""Entorno de revisión: HDRI de estudio, cámara, suelo y ajustes de render."""
import math
import os

import bpy
from mathutils import Vector

ROOT = r"C:\Users\Brandon David\Projects\pc-desmontado"


def setup(engine="CYCLES"):
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(ROOT, "assets-src", "hdri", "studio_small_09_2k.hdr"), check_existing=True)
    mp = nt.nodes.new("ShaderNodeMapping")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], env.inputs[0])
    mp.inputs["Rotation"].default_value[2] = math.radians(110)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    # Fondo de cámara oscuro, la luz sigue viniendo del HDRI
    lp = nt.nodes.new("ShaderNodeLightPath")
    dark = nt.nodes.new("ShaderNodeBackground")
    dark.inputs["Color"].default_value = (0.012, 0.013, 0.016, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(env.outputs[0], bg.inputs[0])
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(dark.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])

    try:
        sc.render.engine = engine
    except TypeError as e:
        print(e)
    if sc.render.engine == "CYCLES":
        sc.cycles.samples = 96
        sc.cycles.use_denoising = True
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for t in ("OPTIX", "CUDA"):
                try:
                    prefs.compute_device_type = t
                    prefs.get_devices()
                    for d in prefs.devices:
                        d.use = True
                    sc.cycles.device = "GPU"
                    break
                except Exception:
                    continue
        except Exception as e:
            print("gpu", e)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception as e:
        print(e)

    # Suelo oscuro con reflejo suave
    fl = bpy.data.objects.get("LD_Floor")
    if fl is None:
        me = bpy.data.meshes.new("LD_Floor")
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3)
        bm.to_mesh(me)
        fl = bpy.data.objects.new("LD_Floor", me)
        sc.collection.objects.link(fl)
        m = bpy.data.materials.new("LD_FloorMat")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (0.02, 0.021, 0.025, 1)
        b.inputs["Roughness"].default_value = 0.35
        me.materials.append(m)
    cam = bpy.data.objects.get("LD_Cam")
    if cam is None:
        cd = bpy.data.cameras.new("LD_Cam")
        cam = bpy.data.objects.new("LD_Cam", cd)
        sc.collection.objects.link(cam)
    cam.data.lens = 50
    cam.data.clip_start = 0.01
    sc.camera = cam
    return cam


def aim(cam, eye, target, lens=50):
    cam.location = Vector(eye)
    d = Vector(target) - Vector(eye)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens


def render(path, samples=96, res=(1600, 1000)):
    sc = bpy.context.scene
    if sc.render.engine == "CYCLES":
        sc.cycles.samples = samples
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path
