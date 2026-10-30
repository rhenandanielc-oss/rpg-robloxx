"""Close extremo do olho (repouso) e da boca (rugido, de frente-baixo). Uso: blender -b X.blend -P render_detalhe.py -- <saida> <prefixo>"""
import bpy, sys, os
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; out, pre = os.path.abspath(a[0]), a[1]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; cam = bpy.data.objects["cam_rev"]; sc.camera = cam
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 900, 600; sc.eevee.taa_render_samples = 64
def acao(n, f): act = bpy.data.actions[n]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]; sc.frame_set(f)
def foto(nome, alvo, d, dist, lente):
    cam.location = alvo + V(d).normalized() * dist; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lente; sc.render.filepath = os.path.join(out, "%s_%s.png" % (pre, nome)); bpy.ops.render.render(write_still=True)
acao("Silverwing_Parado", 1)
olho = A.matrix_world @ (A.pose.bones["head"].matrix @ (A.pose.bones["head"].bone.matrix_local.inverted() @ V((-0.0522, -0.974, 0.590))))
foto("olho", olho, (-1, -0.35, 0.15), 0.22, 80)
acao("Silverwing_Rugido_Combate", 34)
b = (A.matrix_world @ A.pose.bones["mouth_lower"].head + A.matrix_world @ A.pose.bones["mouth_upper_tip"].tail) / 2
foto("boca_frente", b, (-0.25, -1, -0.25), 0.45, 60)
foto("boca_lado", b, (-1, -0.2, 0.0), 0.45, 60)
print("DETALHE_OK")
