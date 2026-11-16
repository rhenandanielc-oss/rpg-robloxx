"""v22, diagnostico SO LEITURA do flanco direito / ventre na locomocao (Trote q6, Corrida q6/q10/q12 e o pior quadro de cada
acao), com o rig real e as acoes atuais. Regiao: pele do corpo com x < 0,4 (lado D e linha media), -2,5 < y < 3,0, z < 4,2.
Para cada quadro e LOD:
- faces viradas (normal posada x normal do repouso levada pelo osso dominante) e arestas esticadas (> 1,8x e > 2,5x), com area,
  agrupadas por COMPOSICAO de pesos (ossos com peso > 0,15) e por posicao;
- PONTE: arestas cujos 2 vertices tem ossos dominantes de 'membros' diferentes (coxa D x coluna/quadril) e diferenca de peso
  da coxa D > 0,5 numa aresta curta (< 0,12): degrau de peso entre vizinhos quase coincidentes;
- INTERPENETRACAO: vertices da pele do ventre/flanco que ficam do lado de dentro de faces da coxa D (raio a partir do vertice
  pela normal da coxa) e distancia minima entre pele da coxa e pele do ventre;
Uso: blender -b <anim.blend> -P diag_flanco_v22.py -- <saida_json> [LOW,LOD1,LOD2]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from collections import Counter, defaultdict
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; OSS = {b.name for b in ARM.data.bones}
QUADROS = {"Trote": [6, 4, 8], "Corrida": [6, 10, 12, 8, 4], "Andar": [14]}
COXA_D = {"Coxa_D", "Tibia_D"}
def usar(n):
    ac = bpy.data.actions[n]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
def regiao(p): return p.x < 0.4 and -2.5 < p.y < 3.0 and p.z < 4.2
def posado(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); P = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return P
R = {}
for L in NIV:
    C = bpy.data.objects[L + "_Corpo"]; me = C.data; ARM.animation_data.action = None
    for pb in ARM.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update(); P0 = [v.co.copy() for v in me.vertices]
    gn = {g.index: g.name for g in C.vertex_groups}; W = [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS and e.weight > 1e-4} for v in me.vertices]
    F = [list(p.vertices) for p in me.polygons]; N0 = [p.normal.copy() for p in me.polygons]; A0 = [p.area for p in me.polygons]
    cen0 = [sum((P0[i] for i in f), V()) / len(f) for f in F]; FR = [fi for fi in range(len(F)) if regiao(cen0[fi])]; FRs = set(FR)
    VR = sorted({i for fi in FR for i in F[fi]})
    ares = {}
    for fi in FR:
        f = F[fi]
        for k in range(len(f)):
            e = tuple(sorted((f[k], f[(k + 1) % len(f)]))); ares[e] = (P0[e[0]] - P0[e[1]]).length
    def comp(ids):
        w = {}
        for i in ids:
            for k, x in W[i].items(): w[k] = w.get(k, 0) + x / len(ids)
        return "+".join(sorted(k for k, x in w.items() if x > 0.15))
    # degraus de peso (repouso): coxa D entre vizinhos proximos
    deg = []
    for (i, j), l in ares.items():
        if l < 0.12:
            d = abs(sum(W[i].get(k, 0) for k in COXA_D) - sum(W[j].get(k, 0) for k in COXA_D))
            if d > 0.5: deg.append((round(d, 2), round(l, 3)))
    RL = R[L] = {"faces_regiao": len(FR), "vertices_regiao": len(VR), "degraus_peso_coxaD_>0,5_em_arestas_<0,12": len(deg), "degraus_exemplo": deg[:8], "quadros": {}}
    coxa_f = [fi for fi in FR if max(W[F[fi][0]], key=W[F[fi][0]].get, default="") in COXA_D]
    for acao, qs in QUADROS.items():
        usar(acao)
        for q in qs:
            sc.frame_set(q); Pc = posado(C); vir = Counter(); avir = Counter(); est = Counter(); est25 = 0; pos_v = defaultdict(list)
            for fi in FR:
                f = F[fi]; w = {}
                for vi in f:
                    for k, x in W[vi].items(): w[k] = w.get(k, 0) + x
                if not w or A0[fi] < 2e-4: continue
                pb = ARM.pose.bones[max(w, key=w.get)]; Rm = (pb.matrix @ pb.bone.matrix_local.inverted()).to_3x3()
                n1 = (Pc[f[1]] - Pc[f[0]]).cross(Pc[f[2]] - Pc[f[0]])
                if n1.length > 1e-12 and n1.normalized().dot(Rm @ N0[fi]) < 0:
                    c = comp(f); vir[c] += 1; avir[c] += A0[fi]; pos_v[c].append(cen0[fi])
            for (i, j), l in ares.items():
                if l < 1e-3: continue
                r = (Pc[i] - Pc[j]).length / l
                if r > 1.8: est[comp([i, j])] += 1
                if r > 2.5: est25 += 1
            # interpenetracao: vertices da regiao que nao sao coxa D, dentro da pele da coxa D posada
            bv = BVHTree.FromPolygons(Pc, [F[fi] for fi in coxa_f]) if coxa_f else None; dentro = 0; dmin = 9.0
            if bv:
                for i in VR:
                    if sum(W[i].get(k, 0) for k in COXA_D) > 0.3: continue
                    loc, nr, idx, d = bv.find_nearest(Pc[i])
                    if loc is None: continue
                    dmin = min(dmin, d)
                    if d < 0.25 and (Pc[i] - loc).dot(nr) < -0.01: dentro += 1
            RL["quadros"]["%s_q%d" % (acao, q)] = {
                "viradas": sum(vir.values()), "area_viradas": round(sum(avir.values()), 3),
                "viradas_por_composicao": {k: [v, round(avir[k], 3), [round(x, 2) for x in (sum(pos_v[k], V()) / len(pos_v[k]))]] for k, v in vir.most_common(8)},
                "arestas_>1,8x": sum(est.values()), "arestas_>2,5x": est25, "esticadas_por_composicao": dict(est.most_common(8)),
                "vertices_dentro_da_coxaD": dentro, "dist_min_pele_a_coxaD": round(dmin, 3)}
            print("DIAG", L, acao, q, json.dumps(RL["quadros"]["%s_q%d" % (acao, q)]), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("DIAG_FLANCO_OK", flush=True)
