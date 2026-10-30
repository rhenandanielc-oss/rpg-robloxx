"""Costura macia entre regioes (corpo x pata dianteira/traseira x asa x cauda): as regioes geodesicas deixam a fronteira
1/0 em dente de serra, que vira lascas quando a pata/asa se move. Pega os vertices de fronteira (vizinho de outra parte,
exceto asa_l x asa_r no dorso) + ANEIS aneis e faz Laplaciano de TODOS os grupos so nessa faixa (borda externa fixa),
limite 4, normaliza. Uso: blender -b Silverwing_M2M.blend -P costura_regioes.py [-- ANEIS ITER]"""
import bpy, sys
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ANEIS = int(args[0]) if args else 5; ITER = int(args[1]) if len(args) > 1 else 30
M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
def parte(v):
    if not len(v.groups): return "corpo"
    n = gi[max(v.groups, key=lambda g: g.weight).group]
    if n.startswith(("wing_", "shoulder_")): return "asa_" + n[-1]
    if n.startswith(("front_", "collar_")): return "pd_" + n[-1]
    if n.startswith(("back_", "hips_anchor")): return "pt_" + n[-1]
    if n.startswith("tail"): return "cauda"
    return "corpo"
PV = [parte(v) for v in M.data.vertices]
viz = [set() for _ in M.data.vertices]
for e in M.data.edges:
    a, b = e.vertices; viz[a].add(b); viz[b].add(a)
# copias do mesmo ponto nas costuras de UV contam como vizinhas (mesmos vizinhos = mesmos pesos)
from mathutils.kdtree import KDTree
_kd = KDTree(len(PV))
for v in M.data.vertices: _kd.insert(v.co, v.index)
_kd.balance()
for v in M.data.vertices:
    for _, j, _ in _kd.find_range(v.co, 1e-6):
        if j != v.index: viz[v.index] |= viz[j]
for v in M.data.vertices: viz[v.index].discard(v.index)
def separa(a, b): return a != b and {a, b} != {"asa_l", "asa_r"}
borda = {v for v in range(len(PV)) if any(separa(PV[v], PV[n]) for n in viz[v])}
faixa = set(borda)
for _ in range(ANEIS): faixa |= {n for v in faixa for n in viz[v]}
W = [{g.group: g.weight for g in v.groups if g.weight > 1e-5} for v in M.data.vertices]
livres = [v for v in faixa if all(n in faixa for n in viz[v])]          # borda externa da faixa fica fixa
for _ in range(ITER):
    novo = {}
    for v in livres:
        m = {}
        for n in viz[v]:
            for g, w in W[n].items(): m[g] = m.get(g, 0.0) + w / len(viz[v])
        d = {g: 0.4 * W[v].get(g, 0.0) + 0.6 * m.get(g, 0.0) for g in set(W[v]) | set(m)}
        top = sorted(d.items(), key=lambda x: -x[1])[:4]; s = sum(w for _, w in top) or 1.0
        novo[v] = {g: w / s for g, w in top if w / s > 0.01}
    for v, d in novo.items(): W[v] = d
vgs = M.vertex_groups
for v in livres:
    for g in list(M.data.vertices[v].groups): vgs[g.group].remove([v])
    for g, w in W[v].items(): vgs[g].add([v], w, "REPLACE")
print("COSTURA fronteira", len(borda), "faixa", len(faixa), "suavizados", len(livres))
print("MAX_INFLUENCIAS", max(len(v.groups) for v in M.data.vertices), "sem_peso", sum(1 for v in M.data.vertices if not len(v.groups)))
bpy.ops.wm.save_mainfile()
print("COSTURA_OK")
