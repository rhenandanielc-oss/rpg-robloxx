"""Conta vertices da JUBA/PEITO dentro das capsulas dos ossos das patas dianteiras (Braco/Antebraco/Mao, raio 0,25)
ao longo de clipes. So leitura. Uso: blender -b <rig.blend> -P juba_patas.py -- <blend_das_acoes|-> Clipe,Clipe"""
import bpy, sys, os
import numpy as np
from mathutils.geometry import intersect_point_line
A = sys.argv[sys.argv.index("--") + 1:]; FONTE = A[0]; CL = A[1].split(",")
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; sc = bpy.context.scene
if FONTE != "-":
    with bpy.data.libraries.load(os.path.abspath(FONTE)) as (s, d): d.actions = ["Lobo_" + c for c in CL if "Lobo_" + c not in bpy.data.actions]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
gi = {g.index: g.name for g in LO.vertex_groups}; y_omb = arm.data.bones["BracoE"].head_local.y
JUB = {"JubaE", "JubaD", "JubaPeito", "Pescoco1", "Pescoco2", "Peito"}
idx = [v.index for v in LO.data.vertices if v.groups and gi[max(v.groups, key=lambda q: q.weight).group] in JUB and v.co.y < y_omb + 0.5 and v.co.z > 3.4]
for c in CL:
    act = bpy.data.actions["Lobo_" + c]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = [int(x) for x in act.frame_range]; tot = 0; pior = 0
    for f in range(f0, f1 + 1, 2):
        sc.frame_set(f); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        segs = [(arm.pose.bones[b].head, arm.pose.bones[b].tail) for b in ("BracoE", "AntebracoE", "MaoE", "BracoD", "AntebracoD", "MaoD")]
        n_ = 0
        for i in idx:
            p = ev[i].co
            for a, b in segs:
                q, t = intersect_point_line(p, a, b)
                t = min(1, max(0, t)); q = a.lerp(b, t)
                if (p - q).length < 0.25: n_ += 1; break
        tot += n_; pior = max(pior, n_)
    print("JUBA_NAS_PATAS", c, "media por quadro %.1f" % (tot / len(range(f0, f1 + 1, 2))), "pior quadro", pior, "de", len(idx))
