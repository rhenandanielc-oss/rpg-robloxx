"""E5: teste visual de palpebras (piscar/semicerrar) e orelhas (para tras / para a frente) e boca 0-32 no rig de producao.
Uso: blender -b E5_rig.blend -P e5_12_teste_rosto.py -- <saida_dir>"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
for pb in arm.pose.bones: pb.rotation_mode = "XYZ"
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.4; so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
def vista(nome, alvo, az, el, dist, res=420):
    alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = res; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
def pose(d):
    for pb in arm.pose.bones: pb.rotation_euler = (0, 0, 0)
    for k, v in d.items(): arm.pose.bones[k].rotation_euler = tuple(math.radians(x) for x in v)
    bpy.context.view_layer.update()
TESTES = [("neutro", {}), ("palp_pos25", {"Palpebra_D": (25, 0, 0), "Palpebra_E": (25, 0, 0)}), ("palp_neg25", {"Palpebra_D": (-25, 0, 0), "Palpebra_E": (-25, 0, 0)}),
          ("palp_neg40", {"Palpebra_D": (-40, 0, 0), "Palpebra_E": (-40, 0, 0)}), ("palp_pos40", {"Palpebra_D": (40, 0, 0), "Palpebra_E": (40, 0, 0)}),
          ("orelha_x35", {"Orelha_D": (35, 0, 0), "Orelha_E": (35, 0, 0)}), ("orelha_x-35", {"Orelha_D": (-35, 0, 0), "Orelha_E": (-35, 0, 0)}),
          ("orelha_z30", {"Orelha_D": (0, 0, 30), "Orelha_E": (0, 0, -30)})]
for nome, d in TESTES:
    pose(d); vista(nome + "_frente", (-0.2, -14.0, 14.6), 0, 6, 6.5); vista(nome + "_34", (-0.2, -13.6, 14.8), -45, 15, 8)
print("OK")
