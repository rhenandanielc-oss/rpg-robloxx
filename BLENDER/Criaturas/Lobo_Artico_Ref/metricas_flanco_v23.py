"""v23: METRICAS (so leitura) do flanco D / ventre, independentes da topologia, para comparar v21 / v22 / v23.
Para cada LOD, acao e quadro (varredura de TODOS os quadros de Andar, Trote e Corrida; Repouso a cada 8):
- PELE, regiao do flanco (x < 0,4; -2,5 < y < 3,0; z < 4,2) e sub-regiao da PREGA (x -1,1..0,3; y -0,5..1,1; z 2,3..3,2):
  estiramento principal por face (gradiente de deformacao repouso -> pose; s1 = maior, s2 = menor valor singular):
  area de repouso com s1 > 1,8 e > 2,5 (estiramento relativo), s1 max, s1 medio ponderado pela area;
  compressao: area com s2 < 0,5 (colapso); aresta posada mais longa na prega (estiramento absoluto, stud);
  faces viradas (normal posada x normal de repouso levada pelo osso dominante): area (criterio do diag_flanco_v22; exagera em
  zonas de peso misturado, onde o osso dominante nao representa a face);
  DOBRAS (criterio geometrico, independe dos pesos): faces cuja normal posada se opoe a media das vizinhas (no repouso
  concordavam): area na regiao e na prega;
  penetracao: vertices fora da coxa D (Coxa_D+Tibia_D < 0,3) dentro da pele da coxa D posada (fracao dos vertices) e
  profundidade max.
- PELO (cartoes com raiz na regiao): cartoes com algum vertice > 0,03 para DENTRO da pele posada (pelo atravessando) e
  cartoes com a raiz > 0,03 mais longe da pele do que no repouso (raiz descolada).
Saida: JSON com todos os quadros e o resumo (pior quadro por metrica e os quadros pedidos: Trote q6, Corrida q6/8/10/12,
Andar q14). Uso: blender -b <anim.blend> -P metricas_flanco_v23.py -- <saida_json> [LOW,LOD1,LOD2]"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; OSS = {b.name for b in ARM.data.bones}
ACOES = {n: list(range(int(bpy.data.actions[n].frame_range[0]), int(bpy.data.actions[n].frame_range[1]) + 1)) for n in os.environ.get("ACOES_MET", "Andar,Trote,Corrida").split(",")}   # v25: ACOES_MET=Arrancada,Frenagem
ACOES["Repouso"] = list(range(0, int(bpy.data.actions["Repouso"].frame_range[1]) + 1, 8))
PEDIDOS = {k: v for k, v in {"Trote": [6], "Corrida": [6, 8, 10, 12], "Andar": [14]}.items() if k in ACOES}
COXA_D = ("Coxa_D", "Tibia_D")
def regiao(p): return p.x < 0.4 and -2.5 < p.y < 3.0 and p.z < 4.2
def prega(p): return -1.1 < p.x < 0.3 and -0.5 < p.y < 1.1 and 2.3 < p.z < 3.2
def usar(n):
    ac = bpy.data.actions[n]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
def posado(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); P = np.array([v.co[:] for v in m.vertices]); e.to_mesh_clear(); return P
def tri_frames(P, F):
    p0, p1, p2 = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]; e1, e2 = p1 - p0, p2 - p0; n = np.cross(e1, e2); ar = np.linalg.norm(n, axis=1)
    x = e1 / np.maximum(np.linalg.norm(e1, axis=1), 1e-12)[:, None]; y = np.cross(n / np.maximum(ar, 1e-12)[:, None], x)
    Q = np.stack([np.stack([np.linalg.norm(e1, axis=1), (e2 * x).sum(1)], 1), np.stack([np.zeros(len(F)), (e2 * y).sum(1)], 1)], 1)   # Q[f] = [[a, b], [0, c]]
    return e1, e2, n, ar / 2, Q
R = {"acoes": {k: [v[0], v[-1], len(v)] for k, v in ACOES.items()}}
for L in NIV:
    C = bpy.data.objects[L + "_Corpo"]; me = C.data; ARM.animation_data.action = None
    for pb in ARM.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update(); P0 = np.array([v.co[:] for v in me.vertices])
    gn = {g.index: g.name for g in C.vertex_groups}
    W = [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS and e.weight > 1e-4} for v in me.vertices]
    tri = []
    for p in me.polygons:
        vs = list(p.vertices)
        for k in range(1, len(vs) - 1): tri.append((vs[0], vs[k], vs[k + 1], p.index))
    T = np.array(tri); F = T[:, :3]; cen0 = P0[F].mean(1)
    em_reg = np.array([regiao(V(c)) for c in cen0]); em_pr = np.array([prega(V(c)) for c in cen0])
    F_r = F[em_reg]; pr_r = em_pr[em_reg]
    e1_0, e2_0, n0, A0, Q0 = tri_frames(P0, F_r); Qinv = np.linalg.inv(np.where(np.abs(np.linalg.det(Q0))[:, None, None] > 1e-14, Q0, np.eye(2)))
    ok = A0 > 1e-6
    dom = []
    for f in F_r:
        w = {}
        for vi in f:
            for k, x in W[vi].items(): w[k] = w.get(k, 0) + x
        dom.append(max(w, key=w.get) if w else "Raiz")
    ef = {}
    for k, f in enumerate(F_r):
        for i in range(3): ef.setdefault(tuple(sorted((int(f[i]), int(f[(i + 1) % 3])))), []).append(k)
    VIZ = [[] for _ in F_r]
    for fs in ef.values():
        for k in fs: VIZ[k] += [j for j in fs if j != k]
    def nrm(n): return n / np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
    nn0 = nrm(n0); base_dob = np.array([np.dot(nn0[k], nn0[VIZ[k]].mean(0)) if VIZ[k] else 1.0 for k in range(len(F_r))])
    VR = sorted({int(i) for f in F_r for i in f}); fora_coxa = [i for i in VR if sum(W[i].get(k, 0) for k in COXA_D) <= 0.3]
    coxa_t = [k for k, f in enumerate(F_r) if dom[k] in COXA_D]
    # cartoes de pelo da regiao
    po = bpy.data.objects.get(L + "_Pelagem"); cart = []
    if po:
        PP0 = np.array([v.co[:] for v in po.data.vertices]); bvh0 = BVHTree.FromPolygons([V(p) for p in P0], [list(f) for f in F])
        adj = [[] for _ in range(len(PP0))]
        for e in po.data.edges: adj[e.vertices[0]].append(e.vertices[1]); adj[e.vertices[1]].append(e.vertices[0])
        vis = np.zeros(len(PP0), bool)
        for s in range(len(PP0)):
            if vis[s]: continue
            st = [s]; cc = []; vis[s] = True
            while st:
                x = st.pop(); cc.append(x)
                for u in adj[x]:
                    if not vis[u]: vis[u] = True; st.append(u)
            ds = [bvh0.find_nearest(V(PP0[i]))[3] for i in cc]; r = cc[int(np.argmin(ds))]
            if regiao(V(PP0[r])): cart.append((cc, r, min(ds)))
    RL = R[L] = {"faces_regiao": int(ok.sum()), "faces_prega": int((ok & pr_r).sum()), "area_regiao": round(float(A0[ok].sum()), 3), "area_prega": round(float(A0[ok & pr_r].sum()), 3),
                 "cartoes_regiao": len(cart), "quadros": {}}
    for acao, qs in ACOES.items():
        usar(acao)
        for q in qs:
            sc.frame_set(q); Pc = posado(C)
            e1, e2, n1, A1, Q1 = tri_frames(Pc, F_r)
            # gradiente de deformacao em coordenadas locais: J = [e1 e2]_pose(2D na propria base) * Q0^-1 -> usar Q1 * Q0^-1
            J = Q1 @ Qinv; sv = np.linalg.svd(J, compute_uv=False); s1, s2 = sv[:, 0], sv[:, 1]
            Rm = {}
            vir = np.zeros(len(F_r), bool)
            for k in range(len(F_r)):
                if not ok[k]: continue
                d = dom[k]
                if d not in Rm: pb = ARM.pose.bones[d]; Rm[d] = np.array((pb.matrix @ pb.bone.matrix_local.inverted()).to_3x3())
                if np.dot(n1[k], Rm[d] @ n0[k]) < 0: vir[k] = True
            m = ok; nn1 = nrm(n1)
            dob = np.array([(np.dot(nn1[k], nn1[VIZ[k]].mean(0)) < 0) if VIZ[k] else False for k in range(len(F_r))]) & (base_dob > 0.3) & ok
            lp = 0.0
            for k in np.nonzero(ok & pr_r)[0]:
                f = F_r[k]; lp = max(lp, max(np.linalg.norm(Pc[f[i]] - Pc[f[(i + 1) % 3]]) for i in range(3)))
            dentro = 0; prof = 0.0
            if coxa_t:
                bv = BVHTree.FromPolygons([V(p) for p in Pc], [list(F_r[k]) for k in coxa_t])
                for i in fora_coxa:
                    loc, nr, idx, d = bv.find_nearest(V(Pc[i]))
                    if loc is not None and d < 0.25:
                        s = (V(Pc[i]) - loc).dot(nr)
                        if s < -0.01: dentro += 1; prof = max(prof, -s)
            c_atr = c_desc = 0
            if cart:
                PPc = posado(po); bvc = BVHTree.FromPolygons([V(p) for p in Pc], [list(f) for f in F])
                for cc, r, d0 in cart:
                    loc, nr, _, dr = bvc.find_nearest(V(PPc[r]))
                    if dr - d0 > 0.03: c_desc += 1
                    for i in cc:
                        loc, nr, _, d = bvc.find_nearest(V(PPc[i]))
                        if loc is not None and (V(PPc[i]) - loc).dot(nr) < -0.03: c_atr += 1; break
            mp = ok & pr_r
            RL["quadros"]["%s_q%d" % (acao, q)] = {
                "s1>1,8_area": round(float(A0[m & (s1 > 1.8)].sum()), 4), "s1>2,5_area": round(float(A0[m & (s1 > 2.5)].sum()), 4), "s1_max": round(float(s1[m].max()), 3),
                "s1_medio": round(float((s1[m] * A0[m]).sum() / A0[m].sum()), 4), "s2<0,5_area": round(float(A0[m & (s2 < 0.5)].sum()), 4),
                "prega_s1>1,8_area": round(float(A0[mp & (s1 > 1.8)].sum()), 4), "prega_s1_max": round(float(s1[mp].max()), 3), "prega_s2<0,5_area": round(float(A0[mp & (s2 < 0.5)].sum()), 4),
                "prega_aresta_max": round(float(lp), 3), "viradas_area": round(float(A0[vir].sum()), 4), "prega_viradas_area": round(float(A0[vir & mp].sum()), 4),
                "dobras_area": round(float(A0[dob].sum()), 4), "prega_dobras_area": round(float(A0[dob & pr_r].sum()), 4),
                "penetracao_frac": round(dentro / max(1, len(fora_coxa)), 4), "penetracao_prof_max": round(prof, 3),
                "pelo_atravessando": c_atr, "pelo_raiz_descolada": c_desc}
        print("MET", L, acao, flush=True)
    # resumo
    res = {}
    for k in next(iter(RL["quadros"].values())):
        if k.startswith("pen") or k.startswith("pelo") or True:
            pior = max(RL["quadros"].items(), key=lambda t: t[1][k]); res[k] = [pior[0], pior[1][k]]
    RL["pior_quadro_por_metrica"] = res
    RL["quadros_pedidos"] = {"%s_q%d" % (a_, q): RL["quadros"]["%s_q%d" % (a_, q)] for a_, qs in PEDIDOS.items() for q in qs}
json.dump(R, open(OUT, "w"), indent=1); print("METRICAS_V23_OK", flush=True)
