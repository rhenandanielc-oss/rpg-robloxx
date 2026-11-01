"""Renders de apresentacao do GL_Dragao rigado (GL_Dragao_M2M.blend): pose de exibicao (clipe Sentado, asas erguidas,
como a referencia), rugido com a boca aberta no quadro de maior abertura, andar e voo; mesma luz do master.
Uso: blender -b GL_Dragao_M2M.blend -P render_exibicao.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
for o in sc.objects:
    if o.type == "LIGHT": o.hide_render = True
w = bpy.data.worlds.new("Ceu_Exib"); sc.world = w
if w.node_tree is None: w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.72, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.35
for nome, en, cor, rot in (("Sol", 4.0, (1.0, 0.97, 0.94), (math.radians(50), 0, math.radians(30))),
                           ("Contra", 3.0, (0.85, 0.92, 1.0), (math.radians(115), 0, math.radians(200))),
                           ("Preench", 1.2, (0.88, 0.94, 1.0), (math.radians(60), 0, math.radians(-120)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.view_settings.view_transform = "AgX"
cam = sc.camera
def foto(nome, pos, alvo, lente):
    cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
def acao(nome):
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    return [int(x) for x in act.frame_range]
f0, f1 = acao("Sentado"); sc.frame_set((f0 + f1) // 2)
foto("exibicao_ref", V((1.75, -2.75, 1.10)), (0, -0.30, 0.45), 40)
foto("exibicao_lado", V((-3.3, -0.30, 0.65)), (0, -0.25, 0.45), 40)
foto("exibicao_frente", V((0.0, -3.2, 0.75)), (0, -0.30, 0.50), 40)
f0, f1 = acao("Rugido_Combate")
ml = A.pose.bones["mouth_lower"]; melhor = (0, f0)
for f in range(f0, f1 + 1):
    sc.frame_set(f); a = ml.matrix_basis.to_quaternion().angle
    if a > melhor[0]: melhor = (a, f)
sc.frame_set(melhor[1]); print("EXIB boca max %.1f graus no quadro %d" % (math.degrees(melhor[0]), melhor[1]))
cab = A.matrix_world @ A.pose.bones["head"].head
foto("rugido_cabeca", cab + V((-0.55, -0.55, 0.10)), cab + V((0, -0.10, -0.02)), 50)
foto("rugido_corpo", V((1.75, -2.75, 1.10)), (0, -0.30, 0.50), 40)
f0, f1 = acao("Andar"); sc.frame_set(f0 + (f1 - f0) // 4); foto("andar", V((-3.3, -0.4, 0.75)), (0, -0.10, 0.45), 40)
f0, f1 = acao("Voo"); sc.frame_set(f0 + (f1 - f0) // 3); foto("voo", V((2.2, -3.0, 1.6)), (0, -0.10, 0.55), 36)
A.animation_data.action = None
print("EXIB_OK")
