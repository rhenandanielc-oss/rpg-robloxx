"""Quadros parados de clipes (lateral rente ao chao, frontal e 3/4) para revisar poses e contato com o chao. So leitura.
Uso: blender -b rig/Lobo_Ancestral_Anim.blend -P pose_still.py -- <saida_dir> Clipe:quadro,Clipe:quadro,..."""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.render.resolution_x, sc.render.resolution_y = 800, 520
cam = sc.camera; camd = cam.data; camd.type = "PERSP"
for item in A[1].split(","):
    nome, q = item.split(":"); act = bpy.data.actions["Lobo_" + nome]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(act.frame_range[0]) + int(q))
    for vn, pos, alvo in (("lado", V((22, -1.5, 1.2)), V((0, -1.5, 2.2))), ("frente", V((0, -20, 2.5)), V((0, -1, 2.2))), ("34", V((13, -14, 6)), V((0, -1, 2.0)))):
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = 40
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s.png" % (nome, q, vn)); bpy.ops.render.render(write_still=True)
print("STILL_OK")
