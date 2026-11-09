"""S1: QA da sela deformada pelo rig nos clipes oficiais do Leao Solar (so leitura). Por clipe e por peca (material):
 - pele: menor distancia com sinal (negativa = a sela entra na pele, sem os fios da juba) e vertices-quadro abaixo de -0,05;
 - juba: fios da juba que entram na sela (pontos dos fios dentro do volume da sela; a juba balanca por mola).
Dentro/fora por paridade de raios (manequim_r15.dentro, do Crocodilo, so importado).
Uso: blender -b <com_sela.blend> -P s1_03_qa_sela.py -- <saida.json> [passo=2] [clipes]"""
import bpy, sys, os, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import s1_01_sela_leao as sl
A = sys.argv[sys.argv.index("--") + 1:]; PASSO = int(A[1]) if len(A) > 1 else 2
sc = bpy.context.scene; arm = bpy.data.objects["Leao_Solar_Rig"]; lo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]
sela = bpy.data.objects[sl.NOME]
PL = list(sela["pecas"]); at = sela.data.attributes["peca"]; vpeca = {i: PL[d.value] for i, d in enumerate(at.data)}
REP = [v.co.copy() for v in sela.data.vertices]
GI = {g.index: g.name for g in lo.vertex_groups}
juba = np.array([any(GI[g.group].startswith("Juba") and g.weight > 0.5 for g in v.groups) for v in lo.data.vertices])
OFICIAIS = [a for a in bpy.data.actions if a.name.startswith("Leao_") and not a.name.endswith(("_v1", "_r2", "_r3"))]
if len(A) > 2: OFICIAIS = [bpy.data.actions["Leao_" + n] for n in A[2].split(",")]
res = {}
for act in sorted(OFICIAIS, key=lambda a: a.name):
    arm.animation_data.action = act
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); pior = {}; n_ruim = 0; juba_dentro = (0, None); jmin = 9.0
    for f in range(f0, f1 + 1, PASSO):
        sc.frame_set(f); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
        el = lo.evaluated_get(dg); ml = el.to_mesh(); Wl = lo.matrix_world; P = [Wl @ v.co for v in ml.vertices]
        fs = [tuple(p.vertices) for p in ml.polygons]; el.to_mesh_clear()
        bvh = BVHTree.FromPolygons(P, [f_ for f_ in fs if not any(juba[i] for i in f_)])
        es = sela.evaluated_get(dg); ms = es.to_mesh(); Ws = sela.matrix_world; S = [Ws @ v.co for v in ms.vertices]
        bvh_s = BVHTree.FromPolygons(S, [tuple(p.vertices) for p in ms.polygons]); es.to_mesh_clear()
        for i, w in enumerate(S):
            loc, _, _, d = bvh.find_nearest(w, 0.6)
            if loc is None: continue
            if d < 0.25 and mq.dentro(bvh, w):
                pc = vpeca[i]
                if -d < pior.get(pc, (9, 0))[0]: pior[pc] = (round(-d, 3), f - f0 + 1, [round(c, 2) for c in REP[i]])
                if d > 0.05: n_ruim += 1
        # fios da juba perto da sela: distancia minima e quantos entram no volume
        nj = 0
        for i in np.nonzero(juba)[0]:
            loc, _, _, d = bvh_s.find_nearest(P[i], 1.0)
            if loc is None: continue
            jmin = min(jmin, d)
            if d < 0.3 and mq.dentro(bvh_s, P[i]): nj += 1
        if nj > juba_dentro[0]: juba_dentro = (nj, f - f0 + 1)
    nome = act.name[5:]
    res[nome] = {"pele_pior_por_peca": pior, "vertices_quadro_abaixo_-0,05": n_ruim, "juba_dist_min": round(jmin, 3), "juba_vertices_dentro_max": juba_dentro}
    print("QA_SELA %-24s %s | >0,05: %d | juba min %.2f dentro %d(q%s)" % (nome, " ".join("%s %.3f(q%d @%s)" % (k, v[0], v[1], v[2]) for k, v in sorted(pior.items())) or "sem contato",
                                                                        n_ruim, jmin, juba_dentro[0], juba_dentro[1]), flush=True)
json.dump(res, open(A[0], "w"), indent=1)
print("QA_SELA_OK")
