"""Quadros do rugido (antecipacao, investida/emissao, sustentacao, recuperacao) + closes da boca fechada/aberta do
GL_Dragao rigado. Uso: blender -b GL_Dragao_M2M.blend -P render_rugido.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
for o in sc.objects:
    if o.type == "LIGHT": o.hide_render = True
w = bpy.data.worlds.new("C"); sc.world = w
if w.node_tree is None: w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.72, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.4
for en, rot in ((4.0, (0.87, 0, 0.52)), (2.5, (2.0, 0, 3.5)), (1.2, (1.05, 0, -2.1))):
    l = bpy.data.lights.new("s", "SUN"); l.energy = en; o = bpy.data.objects.new("s", l); sc.collection.objects.link(o); o.rotation_euler = rot
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 960, 540; sc.view_settings.view_transform = "AgX"
cam = sc.camera
def foto(nome, pos, alvo, lente):
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
def acao(nome):
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    return [int(x) for x in act.frame_range]
f0, f1 = acao("Rugido_Combate")
for i, (u, rot) in enumerate(((0.0, "0_inicio"), (0.24, "1_antecipacao"), (0.37, "2_investida"), (0.60, "3_sustentacao"), (0.93, "4_recuperacao"))):
    sc.frame_set(int(f0 + (f1 - f0) * u))
    foto("rugido_" + rot, V((-1.9, -1.55, 0.95)), (0, -0.35, 0.55), 40)
sc.frame_set(int(f0 + (f1 - f0) * 0.5)); cab = A.matrix_world @ A.pose.bones["head"].head
foto("boca_aberta_34", cab + V((-0.45, -0.55, 0.08)), cab + V((0, -0.12, -0.03)), 55)
foto("boca_aberta_lado", cab + V((-0.62, -0.12, 0.0)), cab + V((0, -0.12, -0.03)), 55)
f0, f1 = acao("Parado"); sc.frame_set(f0); cab = A.matrix_world @ A.pose.bones["head"].head
foto("boca_fechada_34", cab + V((-0.45, -0.55, 0.08)), cab + V((0, -0.12, -0.02)), 55)
foto("boca_fechada_frente", cab + V((0.0, -0.75, 0.05)), cab + V((0, -0.12, -0.02)), 55)
A.animation_data.action = None
print("RUGIDO_OK")
