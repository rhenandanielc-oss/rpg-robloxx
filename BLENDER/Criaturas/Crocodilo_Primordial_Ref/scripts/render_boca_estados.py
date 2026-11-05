"""Boca em estados (fechada 100%, meia, repouso do Meshy, aberta +12 graus) x (lado esquerdo, lado direito, frente),
posando so a Mandibula no rig. Uso: blender -b CR_Crocodilo_Rig.blend -P render_boca_estados.py -- <saida_dir> <prefixo> [graus_abre]"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT, PRE = os.path.abspath(A[0]), A[1]; ABRE = float(A[2]) if len(A) > 2 else 12.0
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; cam = sc.camera; cd = cam.data
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
    pb.matrix_basis.identity()
if arm.animation_data: arm.animation_data.action = None
for o in sc.objects:
    if o.type in ("EMPTY", "ARMATURE"): o.hide_render = True
ang = arm["ang_boca"]
EST = (("fechada", -ang), ("meia", -ang / 2), ("repouso", 0.0), ("aberta", ABRE))
CAM = (("E", V((7.0, -15.5, 4.2)), V((0.5, -13.2, 3.7)), 42), ("D", V((-7.0, -15.5, 4.2)), V((-0.5, -13.2, 3.7)), 42),
       ("frente", V((0.0, -22.5, 4.0)), V((0, -13.0, 3.6)), 50))
sc.render.resolution_x, sc.render.resolution_y = 800, 450
pb = arm.pose.bones["Mandibula"]; pb.rotation_mode = "XYZ"
for en, a in EST:
    pb.rotation_euler = (math.radians(a), 0, 0); bpy.context.view_layer.update()
    for cn, p, alvo, l in CAM:
        cam.location = p; cam.rotation_euler = (alvo - p).to_track_quat("-Z", "Y").to_euler(); cd.type = "PERSP"; cd.lens = l
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s.png" % (PRE, en, cn)); bpy.ops.render.render(write_still=True)
print("ESTADOS_OK", [(e, round(a, 1)) for e, a in EST])
