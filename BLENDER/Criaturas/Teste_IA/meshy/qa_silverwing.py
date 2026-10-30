"""QA de deformacao do Silverwing_M2M.blend em TODOS os quadros de todas as acoes (e no descanso):
- estiramento/compressao de arestas vs descanso (por par de regioes);
- asa atravessando o corpo (vertice de asa do lado de dentro da superficie do corpo, prof. > 0.004);
- asa esquerda x direita e auto-intersecao de cada asa (faces nao adjacentes que se cruzam);
- patas abaixo do chao no Walk/Idle.
Grava qa.json com os piores quadros. Uso: blender -b arq.blend -P qa_silverwing.py -- saida.json"""
import bpy, sys, json, math
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}   # fontes de asa (nao exportadas)
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter, defaultdict
saida = sys.argv[sys.argv.index("--") + 1:][0]
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
def regiao(n):
    if n.startswith(("wing_", "shoulder_")): return "asa_" + n[-1]
    if n.startswith("tail_"): return "cauda"
    if n.startswith(("front_", "collar_")): return "pd_" + n[-1]
    if n.startswith(("back_", "hips_anchor_")): return "pt_" + n[-1]
    return "tronco"
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "tronco"
REG = [regiao(dom(v)) for v in M.data.vertices]
# faces: regiao por maioria; membrana = faces de asa sem 'shoulder' dominante (raiz encosta no corpo de proposito)
FREG = []
for p in M.data.polygons:
    c = Counter(REG[i] for i in p.vertices); FREG.append(c.most_common(1)[0][0])
RAIZ = set(i for i, v in enumerate(M.data.vertices) if dom(v).startswith(("shoulder_", "wing_1_", "wing_feather_1_")))
E = [tuple(e.vertices) for e in M.data.edges]
R0 = [v.co.copy() for v in M.data.vertices]
L0 = [(R0[a] - R0[b]).length for a, b in E]
polys = [tuple(p.vertices) for p in M.data.polygons]
corpo_idx = [i for i, r in enumerate(FREG) if not r.startswith("asa")]
asa_idx = {s: [i for i, r in enumerate(FREG) if r == "asa_" + s] for s in "lr"}
asa_vs = {s: [i for i, r in enumerate(REG) if r == "asa_" + s and i not in RAIZ] for s in "lr"}

def bvh(P, idx):
    return BVHTree.FromPolygons([P[i] for i in range(len(P))], [polys[i] for i in idx], all_triangles=False), idx
def cruzamentos(tA, iA, tB, iB, mesmo=False):
    n = 0
    for a, b in tA.overlap(tB):
        fa, fb = polys[iA[a]], polys[iB[b]]
        if mesmo and (iA[a] == iB[b] or set(fa) & set(fb)): continue
        n += 1
    return n // (2 if mesmo else 1)

def avaliar(nome, f):
    dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
    P = [v.co.copy() for v in me.vertices]; M.evaluated_get(dg).to_mesh_clear()
    est = Counter(); comp = 0; mx = 0
    for k, (a, b) in enumerate(E):
        if L0[k] < 1e-6: continue
        r = (P[a] - P[b]).length / L0[k]; mx = max(mx, r)
        if r > 1.6: est[tuple(sorted((REG[a], REG[b])))] += 1
        if r < 0.35: comp += 1
    tc, ic = bvh(P, corpo_idx)
    dentro = defaultdict(int); prof_max = 0
    for s in "lr":
        for i in asa_vs[s]:
            loc, nrm, fi, d = tc.find_nearest(P[i], 0.05)
            if loc is None: continue
            pr = -(P[i] - loc).dot(nrm)
            if pr > 0.004 and d < 0.05:
                dentro[s] += 1; prof_max = max(prof_max, pr)
    tl, il = bvh(P, asa_idx["l"]); tr, ir = bvh(P, asa_idx["r"])
    lxr = cruzamentos(tl, il, tr, ir)
    autol = cruzamentos(tl, il, tl, il, True); autor = cruzamentos(tr, ir, tr, ir, True)
    zmin_pes = min(P[i].z for i, r in enumerate(REG) if r.startswith(("pd", "pt")))
    return dict(acao=nome, quadro=f, est_max=round(mx, 2), arestas_esticadas=sum(est.values()),
                pares=est.most_common(4), comprimidas=comp, asa_no_corpo=dict(dentro), prof_max=round(prof_max, 4),
                asa_l_x_r=lxr, auto_asa_l=autol, auto_asa_r=autor, zmin_pes=round(zmin_pes, 3))
res = []
A.animation_data_create(); A.animation_data.action = None
for t in A.animation_data.nla_tracks: t.mute = True
for pb in A.pose.bones: pb.matrix_basis.identity()
bpy.context.scene.frame_set(1); res.append(avaliar("DESCANSO", 0))
for act in sorted([a for a in bpy.data.actions if a.name.startswith("Silverwing_")], key=lambda a: a.name):
    A.animation_data.action = act
    if len(act.slots): A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    for f in range(f0, f1 + 1):
        bpy.context.scene.frame_set(f); res.append(avaliar(act.name, f))
A.animation_data.action = None
for r in res:
    print("QA %-22s %3d est%.2f n%-4d comp%-3d corpo%s prof%.3f LxR%d autoL%d autoR%d pes%.3f %s" % (
        r["acao"], r["quadro"], r["est_max"], r["arestas_esticadas"], r["comprimidas"], r["asa_no_corpo"], r["prof_max"],
        r["asa_l_x_r"], r["auto_asa_l"], r["auto_asa_r"], r["zmin_pes"], r["pares"][:2]))
json.dump(res, open(saida, "w"), indent=1)
print("QA_OK")

