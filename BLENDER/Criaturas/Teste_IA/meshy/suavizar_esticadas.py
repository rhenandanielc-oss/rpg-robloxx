"""Remove lascas (faces esticadas) nas juncoes ombro/asa/pata e ventre: varre quadros de todas as acoes proprias, junta
os vertices de arestas esticadas (> LIM x o comprimento de descanso) + 2 aneis e suaviza os pesos ENTRE regioes so
nesses vertices (Laplaciano de todos os grupos), limite 4 e normaliza. Repete ate nao haver mais ou PASSADAS.
Uso: blender -b Silverwing_M2M.blend -P suavizar_esticadas.py [-- LIM PASSADAS]"""
import bpy, sys
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
LIM = float(args[0]) if args else 1.6; PASSADAS = int(args[1]) if len(args) > 1 else 6
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
NV = len(M.data.vertices)
viz = [set() for _ in range(NV)]
for e in M.data.edges:
    a, b = e.vertices; viz[a].add(b); viz[b].add(a)
# copias do mesmo ponto nas costuras de UV contam como vizinhas (senao a suavizacao separa as copias e a costura abre)
from mathutils.kdtree import KDTree
_kd = KDTree(NV)
for v in M.data.vertices: _kd.insert(v.co, v.index)
_kd.balance()
for v in M.data.vertices:
    for _, j, _ in _kd.find_range(v.co, 1e-6):
        if j != v.index: viz[v.index] |= viz[j]
for v in M.data.vertices: viz[v.index].discard(v.index)
ARE = [tuple(e.vertices) for e in M.data.edges]
R0 = [v.co.copy() for v in M.data.vertices]
L0 = [(R0[a] - R0[b]).length for a, b in ARE]
acoes = [a for a in bpy.data.actions if a.name.startswith("Silverwing_") and a.name not in ANTIGAS]
quadros = []
for act in acoes:
    f0, f1 = map(int, act.frame_range)
    quadros += [(act, f) for f in range(f0, f1 + 1, 3)]
def ler():
    return [{g.group: g.weight for g in v.groups if g.weight > 1e-5} for v in M.data.vertices]
def gravar(W, alvo):
    vgs = M.vertex_groups
    for v in alvo:
        for g in list(M.data.vertices[v].groups): vgs[g.group].remove([v])
        for gi, w in W[v].items(): vgs[gi].add([v], w, "REPLACE")
def esticadas():
    ruins = set(); pior = 1.0
    for act, f in quadros:
        A.animation_data.action = act
        if len(act.slots): A.animation_data.action_slot = act.slots[0]
        sc.frame_set(f)
        ev = M.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
        P = [v.co.copy() for v in me.vertices]; ev.to_mesh_clear()
        for (a, b), l0 in zip(ARE, L0):
            if l0 < 1e-6: continue
            r = (P[a] - P[b]).length / l0
            if r > LIM: ruins.add(a); ruins.add(b)
            if r > pior: pior = r
    return ruins, pior
for ps in range(PASSADAS + 1):
    ruins, pior = esticadas()
    print("PASSADA", ps, "vertices_esticados", len(ruins), "pior_razao", round(pior, 2))
    if not ruins or ps == PASSADAS: break
    alvo = set(ruins)
    for _ in range(2): alvo |= {n for v in alvo for n in viz[v]}
    W = ler()
    for _ in range(10):
        novo = {}
        for v in alvo:
            m = {}
            for n in viz[v]:
                for gi, w in W[n].items(): m[gi] = m.get(gi, 0.0) + w / len(viz[v])
            d = {gi: 0.5 * W[v].get(gi, 0.0) + 0.5 * m.get(gi, 0.0) for gi in set(W[v]) | set(m)}
            top = sorted(d.items(), key=lambda x: -x[1])[:4]; s = sum(w for _, w in top) or 1.0
            novo[v] = {gi: w / s for gi, w in top if w / s > 0.01}
        for v, d in novo.items(): W[v] = d
    gravar(W, alvo)
A.animation_data.action = None
mx = max(len(v.groups) for v in M.data.vertices)
print("MAX_INFLUENCIAS", mx, "sem_peso", sum(1 for v in M.data.vertices if not len(v.groups)))
bpy.ops.wm.save_mainfile()
print("SUAVIZAR_OK")
