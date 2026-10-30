"""Close-ups do rosto no rig (repouso e boca aberta do Rugido_Combate) para revisar olho, boca e cabeca.
Uso: blender -b CR_Dragao_M2M.blend -P render_rosto.py -- <saida_dir> [prefixo]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; out = os.path.abspath(a[0]); pre = a[1] if len(a) > 1 else "rosto"
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 900, 600; sc.eevee.taa_render_samples = 48
cam = bpy.data.objects["cam_rev"]; sc.camera = cam; cam.data.lens = 70
def cabeca(): return A.matrix_world @ A.pose.bones["head"].head
casos = [("repouso", "Silverwing_Parado", 1)]
act = bpy.data.actions.get("Silverwing_Rugido_Combate")
if act:                                                       # quadro de boca mais aberta
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); melhor = (0, f0)
    for f in range(f0, f1 + 1):
        sc.frame_set(f); q = A.pose.bones["mouth_lower"].matrix_basis.to_quaternion().angle
        melhor = max(melhor, (q, f))
    casos.append(("rugido", "Silverwing_Rugido_Combate", melhor[1]))
for nome, acao, f in casos:
    act = bpy.data.actions[acao]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]; sc.frame_set(f)
    c = (cabeca() + A.matrix_world @ A.pose.bones["mouth_upper_tip"].tail) / 2
    for vista, d in (("lado", (-1, -0.15, 0.05)), ("34", (-0.75, -0.8, 0.2)), ("frente", (0, -1, 0.05)), ("baixo34", (-0.6, -0.7, -0.25))):
        cam.location = c + V(d).normalized() * 0.95; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "%s_%s_%s.png" % (pre, nome, vista)); bpy.ops.render.render(write_still=True)
print("ROSTO_OK", casos)
