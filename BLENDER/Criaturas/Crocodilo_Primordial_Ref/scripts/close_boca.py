"""Somente leitura: closes da boca num quadro de um clipe assado. Uso: blender -b CR_Crocodilo_Anim.blend -P close_boca.py -- <saida_dir> <clipe> <quadro>"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT, CL, Q = os.path.abspath(A[0]), A[1], int(A[2]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; cam = sc.camera; cd = cam.data
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in sc.objects:
    if o.type in ("EMPTY", "ARMATURE"): o.hide_render = True
act = bpy.data.actions["Croc_" + CL]; arm.animation_data.action = act
if act.slots: arm.animation_data.action_slot = act.slots[0]
sc.frame_set(Q); sc.render.resolution_x, sc.render.resolution_y = 1280, 720
for nome, p, a, l in (("lado", V((6.5, -12.8, 4.0)), V((0, -12.8, 3.8)), 40), ("frente_baixo", V((2.5, -20.5, 2.2)), V((0, -14.0, 3.2)), 50),
                      ("dentro", V((1.6, -18.5, 5.4)), V((0, -12.0, 3.6)), 35)):
    cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler(); cd.type = "PERSP"; cd.lens = l
    sc.render.filepath = os.path.join(OUT, "%s_%d_%s.png" % (CL, Q, nome)); bpy.ops.render.render(write_still=True)
