"""Diagrama do esqueleto: renders de perfil e de frente da malha em argila semitransparente e projecao dos ossos
(linhas + nomes) gravada em ossos_2d.json e desenhada por cima com PIL fora do Blender (desenhar_ossos.py). Uso: blender -b CR_Urso_v2_Rig.blend -P diagrama_ossos.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector as V
from bpy_extras.object_utils import world_to_camera_view
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Urso_Rig"]
arg = bpy.data.materials.new("Argila"); arg.use_nodes = True; b = arg.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.75, 0.72, 0.68, 1); b.inputs["Alpha"].default_value = 0.45
if hasattr(arg, "surface_render_method"): arg.surface_render_method = "BLENDED"
for o in sc.objects:
    if o.type == "MESH":
        for i in range(len(o.data.materials)): o.data.materials[i] = arg
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.2, 0.2, 0.22, 1)
l = bpy.data.lights.new("K", "SUN"); l.energy = 3; lo = bpy.data.objects.new("K", l); sc.collection.objects.link(lo); lo.rotation_euler = (0.8, 0, -0.6)
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1400, 900; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
import json
saida = {}
for nome, pos, alvo in (("ossos_perfil", (-30, 0, 4.5), (0, 0, 4.5)), ("ossos_frente", (0, -30, 4.5), (0, 0, 4.5))):
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = 42
    p = os.path.join(OUT, nome + ".png"); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
    bpy.context.view_layer.update(); W, H = sc.render.resolution_x, sc.render.resolution_y
    def px(q):
        c = world_to_camera_view(sc, cam, A.matrix_world @ q); return (c.x * W, (1 - c.y) * H)
    saida[nome] = [(bn.name, px(bn.head_local), px(bn.tail_local)) for bn in A.data.bones]
json.dump(saida, open(os.path.join(OUT, "ossos_2d.json"), "w"))
print("DIAGRAMA_OK")
