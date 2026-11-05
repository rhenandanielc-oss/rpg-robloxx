"""Renderiza os clipes assados (acoes Croc_*) do CR_Crocodilo_Anim.blend: N quadros por clipe em duas cameras, para
pranchas e GIFs de revisao. Nao salva o .blend.
Uso: blender -b CR_Crocodilo_Anim.blend -P render_clipes.py -- <saida_dir> [clipes] [quadros_por_clipe]"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
QUAIS = A[1].split(",") if len(A) > 1 and A[1] else None; NQ = int(A[2]) if len(A) > 2 else 12
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; cam = sc.camera; cd = cam.data
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in sc.objects:
    if o.type == "EMPTY": o.hide_render = True
    if o.type == "ARMATURE": o.hide_render = True
sc.render.resolution_x, sc.render.resolution_y = 960, 540; sc.eevee.taa_render_samples = 24
CAMS_TODAS = {"34": (V((24.0, -20.0, 7.5)), V((0.5, -2.5, 2.4)), 30, None), "lado": (V((40, -2, 2.8)), V((0, -2, 2.8)), 0, 36),
              "cabeca": (V((8.0, -21.0, 5.5)), V((0, -12.5, 3.4)), 38, None), "patas": (V((16.0, -12.0, 2.2)), V((1.5, -4.0, 1.2)), 30, None),
              "topo": (V((0, 1.0, 45)), V((0, 1.01, 0)), 0, 38)}
CAMS = {k: CAMS_TODAS[k] for k in (A[3].split(",") if len(A) > 3 else ("34", "lado"))}
if not arm.animation_data: arm.animation_data_create()
for act in bpy.data.actions:
    if not act.name.startswith("Croc_"): continue
    nome = act.name[5:]
    if QUAIS and nome not in QUAIS: continue
    arm.animation_data.action = act
    if act.slots: arm.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range; total = int(f1 - f0) + 1
    for cn, (p, a, lente, orto) in CAMS.items():
        cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler()
        if orto: cd.type = "ORTHO"; cd.ortho_scale = orto
        else: cd.type = "PERSP"; cd.lens = lente
        for i in range(NQ):
            f = int(f0 + i * (total - (0 if act.get("loop", True) else 1)) / NQ) if NQ > 1 else int(f0)
            sc.frame_set(f)
            sc.render.filepath = os.path.join(OUT, "%s_%s_%02d.png" % (nome, cn, i)); bpy.ops.render.render(write_still=True)
    print("RENDER_CLIPE", nome, total, "quadros")
print("RENDER_CLIPES_OK")
