"""E5 Patada: deformacao da pele do punho por quadro (so leitura). Arestas da zona do punho (vertices com peso em Mao/Punho_Aux)
comparadas ao repouso: compressao (p2 do comprimento/repouso) e dobra (maior mudanca do angulo entre faces vizinhas, graus).
Uso: blender -b <arquivo.blend> -P e5_46_pele_punho.py -- <Acao:pata,Acao:pata,...>"""
import bpy, sys, math
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; PED = [x.split(":") for x in A[0].split(",")]
arm = bpy.data.objects["Leao_Solar_Rig"]; ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; sc = bpy.context.scene
me = ob.data; GI = {g.index: g.name for g in ob.vertex_groups}
def zona(p_):
    alvo = {"Mao_" + p_, "Punho_Aux_" + p_}
    return {v.index for v in me.vertices if sum(g.weight for g in v.groups if GI[g.group] in alvo) > 0.25}
def malha():
    dg = bpy.context.evaluated_depsgraph_get(); m = ob.evaluated_get(dg).to_mesh(); P = np.array([v.co for v in m.vertices]); ob.evaluated_get(dg).to_mesh_clear(); return P
def normais(P, F):
    a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]; n = np.cross(b - a, c - a); return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
me.calc_loop_triangles(); TRI = np.array([t.vertices[:] for t in me.loop_triangles])
arm.animation_data_create(); arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
sc.frame_set(1); P0 = malha()
for nome, p_ in PED:
    Z = zona(p_); E = np.array([e.vertices[:] for e in me.edges if e.vertices[0] in Z and e.vertices[1] in Z])
    T = TRI[np.isin(TRI, list(Z)).all(axis=1)]
    # pares de triangulos vizinhos (aresta comum)
    viz = {}
    for i, t in enumerate(T):
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): viz.setdefault((min(a, b), max(a, b)), []).append(i)
    PAR = np.array([v for v in viz.values() if len(v) == 2])
    L0 = np.linalg.norm(P0[E[:, 0]] - P0[E[:, 1]], axis=1); N0 = normais(P0, T); D0 = np.degrees(np.arccos(np.clip((N0[PAR[:, 0]] * N0[PAR[:, 1]]).sum(1), -1, 1)))
    act = bpy.data.actions[nome]; arm.animation_data.action = act; nq = int(act.frame_range[1]); pior = (0, 1.0, 0.0, 0)
    linhas = []
    for f in range(1, nq + 1):
        sc.frame_set(f); P = malha(); L = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1) / np.maximum(L0, 1e-6)
        N = normais(P, T); D = np.degrees(np.arccos(np.clip((N[PAR[:, 0]] * N[PAR[:, 1]]).sum(1), -1, 1)))
        comp = float(np.percentile(L, 2)); dob = float(np.percentile(np.abs(D - D0), 99.5)); linhas.append((f, comp, dob))
    c_min = min(linhas, key=lambda x: x[1]); d_max = max(linhas, key=lambda x: x[2])
    print("PELE %-22s %s arestas %d | compressao p2 min %.2f (q%d) | dobra p99.5 max %.1f graus (q%d)" % (nome, p_, len(E), c_min[1], c_min[0], d_max[2], d_max[0]))
    print("  por quadro (q:compr/dobra):", " ".join("%d:%.2f/%.0f" % x for x in linhas if x[0] % 2 == 0))
