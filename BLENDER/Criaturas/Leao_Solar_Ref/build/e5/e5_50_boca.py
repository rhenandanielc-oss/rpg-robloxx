"""Fase C: mede, por quadro, a boca do leao (so leitura): menor altura dos vertices da cabeca/mandibula (beber/comer: a boca chega ao
chao?) e a distancia da boca (ponta da mandibula) ate a pata dianteira D (lamber). Uso: blender -b <clipes.blend> -P e5_50_boca.py -- <Acao1,Acao2>"""
import bpy, sys
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
sc = bpy.context.scene; arm = bpy.data.objects["Leao_Solar_Rig"]; ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]
GI = {g.index: g.name for g in ob.vertex_groups}
cab = np.array([max(((g.weight, GI[g.group]) for g in v.groups), default=(0, ""))[1] in ("Cabeca", "Mandibula", "Lingua1", "Lingua2", "Labio_D", "Labio_E") for v in ob.data.vertices])
for nome in A[0].split(","):
    act = bpy.data.actions[nome]; arm.animation_data.action = act; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); lin = []
    for f in range(f0, f1 + 1, 3):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); m = ob.evaluated_get(dg).to_mesh()
        P = np.array([v.co for v in m.vertices]); ob.evaluated_get(dg).to_mesh_clear(); W = np.array(ob.matrix_world); P = P @ W[:3, :3].T + W[:3, 3]
        boca = arm.matrix_world @ arm.pose.bones["Mandibula"].tail; pata = arm.matrix_world @ arm.pose.bones["Dedos_DD"].head
        lin.append((f, float(P[cab][:, 2].min()), (boca - pata).length, float(P[:, 2].min())))
    zmin = min(lin, key=lambda x: x[1]); dmin = min(lin, key=lambda x: x[2])
    print("BOCA %-16s cabeca z min %.2f (q%d) | boca-pata min %.2f (q%d) | malha z min %.2f" % (nome, zmin[1], zmin[0], dmin[2], dmin[0], min(x[3] for x in lin)))
