"""Revisao da DOBRA das asas: clipe Parado (quadro 1) em 6 vistas. Uso: blender -b X.blend -P render_dobra.py -- <saida> <prefixo>"""
import bpy, sys, os
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; out, pre = os.path.abspath(a[0]), a[1]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; cam = bpy.data.objects["cam_rev"]; sc.camera = cam
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 700, 500; sc.eevee.taa_render_samples = 32
act = bpy.data.actions["Silverwing_Parado"]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]; sc.frame_set(1)
c = V((0, 0.05, 0.38)); cam.data.lens = 45
for nome, d, r in (("lado", (-1, 0.05, 0.12), 2.6), ("34_frente", (-0.8, -0.75, 0.45), 2.6), ("34_tras", (-0.75, 0.8, 0.55), 2.6),
                   ("frente", (0, -1, 0.15), 2.6), ("cima", (0.001, 0.02, 1), 2.8), ("tras", (0, 1, 0.3), 2.6)):
    cam.location = c + V(d).normalized() * r; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (pre, nome)); bpy.ops.render.render(write_still=True)
print("DOBRA_OK")
