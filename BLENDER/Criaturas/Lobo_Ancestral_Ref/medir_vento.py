"""Quanto o pelo se move com o vento ao longo de um clipe (so leitura): deslocamento maximo (pico a pico) dos vertices
de cada grupo Pelo* em relacao ao osso pai, e o salto entre o ultimo e o primeiro quadro (fechamento do loop).
Uso: blender -b <Anim.blend> -P medir_vento.py -- Clipe[,Clipe]"""
import bpy, sys
import numpy as np
LISTA = sys.argv[sys.argv.index("--") + 1].split(",")
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
dono = np.array([gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in LO.data.vertices])
pelo = np.array([any(gi[g.group].startswith("Pelo") and g.weight > 0.3 for g in v.groups) for v in LO.data.vertices])
for nome in LISTA:
    act = bpy.data.actions["Lobo_" + nome]; arm.animation_data_create(); arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = [int(x) for x in act.frame_range]
    seq = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh()
        co = np.array([v.co[:] for v in m.vertices])[pelo]; ev.to_mesh_clear()
        M = (arm.matrix_world @ arm.pose.bones["Peito"].matrix).inverted()          # no referencial do peito
        co = (np.c_[co, np.ones(len(co))] @ np.array(M).T)[:, :3]; seq.append(co)
    seq = np.array(seq); amp = np.linalg.norm(seq.max(axis=0) - seq.min(axis=0), axis=1)
    salto = np.linalg.norm(seq[-1] - seq[0], axis=1).max(); dd = np.linalg.norm(np.diff(seq, axis=0), axis=2); passo = dd.max()
    qf, vi = np.unravel_index(dd.argmax(), dd.shape); vg = np.nonzero(pelo)[0][vi]
    print("   pior passo: quadro %d->%d, vertice %d (%s) em %s" % (qf + f0, qf + f0 + 1, vg, dono[vg], np.round(LO.data.vertices[vg].co[:], 2)))
    print("VENTO %-10s quadros %3d | pelo solto: %d verts | balanco pico-a-pico mediana %.3f p90 %.3f max %.3f | salto loop %.3f | passo max/quadro %.3f"
          % (nome, len(seq), pelo.sum(), np.median(amp), np.percentile(amp, 90), amp.max(), salto, passo))
