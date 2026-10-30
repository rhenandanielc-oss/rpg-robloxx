"""Polimento final de pesos guiado por TODAS as animacoes: vertices de arestas esticadas (>1.7x) ou comprimidas (<0.4x)
em qualquer quadro recebem a media dos pesos dos vizinhos (1 anel). A cada passada mede estiramento, cruzamento
asa-asa e asa-dentro-do-corpo; desfaz a passada se cruzamento/penetracao piorar.
Uso: blender -b Silverwing_M2M.blend -P polir_pesos.py -- [passadas]"""
import bpy, sys
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}   # fontes de asa (nao exportadas)
from mathutils.bvhtree import BVHTree
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
NP = int(args[0]) if args else 6
SO_CORPO = len(args) > 1 and args[1] == "corpo"          # so suaviza pele do tronco/patas/cauda (nao mexe nas asas)
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
polys = [tuple(p.vertices) for p in M.data.polygons]
E = [tuple(e.vertices) for e in M.data.edges]
R0 = [v.co.copy() for v in M.data.vertices]; L0 = [(R0[a] - R0[b]).length for a, b in E]
viz = [[] for _ in M.data.vertices]
for a, b in E: viz[a].append(b); viz[b].append(a)
acoes = sorted([a for a in bpy.data.actions if a.name.startswith("Silverwing_") and a.name not in ANTIGAS], key=lambda a: a.name)
def pesos():
    gi = {g.index: g.name for g in M.vertex_groups}
    return [{gi[g.group]: g.weight for g in v.groups if g.weight > 1e-4} for v in M.data.vertices]
def aplicar(W, idx):
    for i in idx:
        v = M.data.vertices[i]
        for g in list(v.groups): M.vertex_groups[g.group].remove([i])
        for n, w in W[i].items(): M.vertex_groups[n].add([i], w, "REPLACE")
def medir():
    W = pesos()
    def lado(i):
        if not W[i]: return ""
        n = max(W[i].items(), key=lambda x: x[1])[0]; return n[-1] if n.startswith(("wing_", "shoulder_")) else ""
    LADO = [lado(i) for i in range(len(W))]
    il = [k for k, p in enumerate(polys) if LADO[p[0]] == "l"]; ir = [k for k, p in enumerate(polys) if LADO[p[0]] == "r"]
    ic = [k for k, p in enumerate(polys) if LADO[p[0]] == ""]
    raiz = lambda i: W[i] and max(W[i].items(), key=lambda x: x[1])[0].startswith(("shoulder_", "wing_1_", "wing_feather_1_"))
    asa_v = [i for i in range(len(W)) if LADO[i] and not raiz(i)]          # mesma regra do qa_silverwing (raiz encosta de proposito)
    ruins, n_est, cruz, pen = set(), 0, 0, 0
    for act in acoes:
        A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
        f0, f1 = map(int, act.frame_range)
        for f in range(f0, f1 + 1, 2):
            sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
            P = [v.co.copy() for v in me.vertices]; M.evaluated_get(dg).to_mesh_clear()
            for k, (a, b) in enumerate(E):
                if L0[k] < 1e-6: continue
                r = (P[a] - P[b]).length / L0[k]
                if r > 1.7 or r < 0.4:
                    n_est += 1
                    for v_ in (a, b):
                        if not (SO_CORPO and LADO[v_]): ruins.add(v_)
            tl = BVHTree.FromPolygons(P, [polys[k] for k in il]); tr = BVHTree.FromPolygons(P, [polys[k] for k in ir])
            cruz += len(tl.overlap(tr))
            tc = BVHTree.FromPolygons(P, [polys[k] for k in ic])
            for i in asa_v:
                loc, nrm, fi, d = tc.find_nearest(P[i], 0.05)
                if loc is not None and -(P[i] - loc).dot(nrm) > 0.004: pen += 1
    A.animation_data.action = None
    return ruins, n_est, cruz, pen
ruins, n_est, cruz, pen = medir()
print("INICIO arestas_ruins_somadas", n_est, "vertices", len(ruins), "cruz", cruz, "penetracao", pen)
for k in range(NP):
    W = pesos(); antes = {i: dict(W[i]) for i in ruins}
    novos = {}
    for i in ruins:
        acc = {}
        for j in viz[i] + [i]:
            for n, w in W[j].items(): acc[n] = acc.get(n, 0) + w
        top = sorted(acc.items(), key=lambda x: -x[1])[:4]; s = sum(w for _, w in top)
        novos[i] = {n: w / s for n, w in top}
    for i, d in novos.items(): W[i] = d
    aplicar(W, novos.keys())
    r2, e2, c2, p2 = medir()
    print("PASSADA", k, "arestas_ruins", e2, "vertices", len(r2), "cruz", c2, "penetracao", p2)
    if c2 > cruz or p2 > pen + 5:
        for i, d in antes.items(): W[i] = d
        aplicar(W, antes.keys()); print("DESFEITA", k); break
    ruins, n_est, cruz, pen = r2, e2, c2, p2
for pb in A.pose.bones: pb.matrix_basis.identity()
bpy.ops.wm.save_mainfile()
print("POLIR_OK")


