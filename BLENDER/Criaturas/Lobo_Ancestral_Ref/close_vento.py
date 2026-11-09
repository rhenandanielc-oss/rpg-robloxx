"""Close 3/4 da juba/peito ao longo de um clipe (quadros PNG) para ver o pelo balancar ao vento. So leitura.
Uso: blender -b <Anim.blend> -P close_vento.py -- <saida_dir> <Clipe> <passo>"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); CL = A[1]; PASSO = int(A[2]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
act = bpy.data.actions["Lobo_" + CL]; arm.animation_data_create(); arm.animation_data.action = act
try: arm.animation_data.action_slot = act.slots[0]
except Exception: pass
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8; sc.render.resolution_x, sc.render.resolution_y = 640, 640
cam = sc.camera; cam.data.type = "PERSP"; cam.data.lens = 60
alvo = V((0, -3.6, 5.6)); cam.location = V((9.5, -11.5, 8.0)); cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
f0, f1 = [int(x) for x in act.frame_range]
for f in range(f0, f1 + 1, PASSO):
    sc.frame_set(f); sc.render.filepath = os.path.join(OUT, "%s_%04d.png" % (CL, f)); bpy.ops.render.render(write_still=True)
