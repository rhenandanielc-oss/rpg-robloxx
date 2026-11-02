"""Closes das UNIOES perna-tronco e pescoco-peito no modelo RIGADO, em pose de animacao (parado, andar, sentado,
voo, rugido), sem a sombra das asas (revisao de forma). Uso: blender -b GL_Dragao_M2M.blend -P render_unioes.py -- <saida>"""
import bpy, sys, os
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for o in sc.objects:
    if o.type == "LIGHT": o.hide_render = True
w = bpy.data.worlds.new("C"); sc.world = w
if w.node_tree is None: w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.72, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.45
for en, rot in ((3.5, (0.87, 0, 0.52)), (2.5, (2.0, 0, 3.5)), (1.4, (1.05, 0, -2.1))):
    l = bpy.data.lights.new("s", "SUN"); l.energy = en; o = bpy.data.objects.new("s", l); sc.collection.objects.link(o); o.rotation_euler = rot
M.visible_shadow = False                                       # sem a faixa de sombra das asas
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 960, 540; sc.view_settings.view_transform = "AgX"
cam = sc.camera
def osso(n): return A.matrix_world @ A.pose.bones[n].head
def foto(nome, alvo, d, lente):
    cam.location = alvo + d; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
for clipe, u in (("Parado", 0.0), ("Andar", 0.3), ("Sentado", 0.5), ("Voo", 0.3), ("Rugido_Combate", 0.5)):
    act = bpy.data.actions["Silverwing_" + clipe]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); sc.frame_set(int(f0 + (f1 - f0) * u))
    foto(clipe + "_ombro", osso("front_leg_r") + V((0, 0, -0.04)), V((-0.55, -0.50, 0.18)), 40)
    foto(clipe + "_quadril", osso("back_leg_r") + V((0, 0, -0.04)), V((-0.60, 0.45, 0.18)), 40)
    foto(clipe + "_pescoco", (osso("spine_2") + osso("spine_3")) / 2, V((-0.70, -0.55, 0.20)), 38)
A.animation_data.action = None
print("UNIOES_OK")
