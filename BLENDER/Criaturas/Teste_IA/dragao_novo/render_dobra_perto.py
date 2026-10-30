"""Close da asa dobrada (Parado q1): lado, 3/4 de cima, de cima e wireframe da membrana. Uso: blender -b X.blend -P render_dobra_perto.py -- <saida> <prefixo>"""
import bpy, sys, os
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; out, pre = os.path.abspath(a[0]), a[1]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; cam = bpy.data.objects["cam_rev"]; sc.camera = cam
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 800, 560; sc.eevee.taa_render_samples = 32
act = bpy.data.actions["Silverwing_Parado"]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]; sc.frame_set(1)
c = V((-0.12, 0.0, 0.42)); cam.data.lens = 50
for nome, d, r in (("lado", (-1, 0.0, 0.15), 1.5), ("34_cima", (-0.8, 0.3, 0.6), 1.5), ("cima", (-0.1, 0.05, 1), 1.6), ("34_frente", (-0.8, -0.6, 0.35), 1.5)):
    cam.location = c + V(d).normalized() * r; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (pre, nome)); bpy.ops.render.render(write_still=True)
print("PERTO_OK")
