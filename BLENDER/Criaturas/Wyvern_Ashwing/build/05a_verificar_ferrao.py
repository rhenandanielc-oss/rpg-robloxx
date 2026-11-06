# M0 (somente leitura) - verificacao CASO A CASO da regiao do ferrao, em TODOS os frames dos 3 ciclos.
# Uso: blender -b <v.blend> -P 05a_verificar_ferrao.py -- <saida.json>
# Para cada par de triangulos que o BVH acusa como sobrepostos:
#   - vizinhanca por solda DIFUSA (KDTree, 1e-3): pares que tocam num vertice/aresta soldada = falso positivo
#     (costura UV / adjacente);
#   - segmento de intersecao (arestas de A contra B e de B contra A), comprimento e profundidade de
#     penetracao (quanto um triangulo passa para tras do outro dentro da area dele);
#   - visibilidade: o ponto medio do segmento e o primeiro impacto de algum dos 26 raios externos?
#   classe: "adjacente" | "rasante" (segmento < 0,01 ou profundidade < 0,003) | "real_oculta" | "real_visivel"
# Faces dobradas (normal da face contra a normal lisa soldada): area, posicao, e se o VERSO aparece de fora.
# Bordas abertas: posicao, comprimento, fresta ate a borda mais proxima e se a abertura aparece de fora.
import bpy, sys, json, math, itertools
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_ray_tri
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
scn = bpy.context.scene
obj = bpy.data.objects["Wyvern"]; arm = bpy.data.objects["Wyvern_Rig"]; me = obj.data
YR = 22.3
me.calc_loop_triangles()
rest = [obj.matrix_world @ v.co for v in me.vertices]
reg = {v.index for v in me.vertices if v.co.y >= YR}
TRI = [t.vertices[:] for t in me.loop_triangles if all(i in reg for i in t.vertices)]
TODOS = [t.vertices[:] for t in me.loop_triangles]          # oclusao usa a malha inteira
# solda difusa
kd = KDTree(len(rest))
for i, p in enumerate(rest): kd.insert(p, i)
kd.balance()
solda = {}
for i in range(len(rest)):
    if i in solda: continue
    for _, j, _ in kd.find_range(rest[i], 1e-3): solda.setdefault(j, i)
S = lambda i: solda[i]
DIRS = [Vector(d).normalized() for d in itertools.product((-1, 0, 1), repeat=3) if any(d)]
def usar(clipe):
    a = bpy.data.actions[clipe]; arm.animation_data.action = a; _k = bpy.data.objects["Wyvern"].data.shape_keys; _sk = [s for s in a.slots if s.target_id_type == "KEY"]
    if _sk and _k.animation_data: _k.animation_data.action = a; _k.animation_data.action_slot = _sk[0]   # shape keys do clipe (slot KEY)
    try: arm.animation_data.action_slot = a.slots[0]
    except Exception: pass
    return a
def avaliar():
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    return [obj.matrix_world @ v.co for v in ev.vertices]
def visivel(bvh_all, p, n_ok=None):
    """quantas das 26 direcoes enxergam p (primeiro impacto a < 2e-3 de p)"""
    k = 0
    for d in DIRS:
        o = p + d * 200; h = bvh_all.ray_cast(o, -d)
        if h[0] is not None and (h[0] - p).length < 2e-3: k += 1
    return k
def normal(P, t):
    a, b, c = (P[i] for i in t); return (b - a).cross(c - a)
def inter_seg(P, A, B):
    pts = []
    for X, Y in ((A, B), (B, A)):
        tv = [P[i] for i in Y]
        for u, v in ((X[0], X[1]), (X[1], X[2]), (X[2], X[0])):
            q = intersect_ray_tri(*tv, P[v] - P[u], P[u], True)
            if q is not None and (q - P[u]).dot(q - P[v]) <= 1e-12: pts.append(q)
    if len(pts) < 2: return None
    a, b = max(itertools.combinations(pts, 2), key=lambda ab: (ab[0] - ab[1]).length)
    return a, b
def bari_dentro(p, tv, tol=0.02):
    a, b, c = tv; v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14: return False
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    return v >= -tol and w >= -tol and v + w <= 1 + tol
def penetracao(P, A, B):
    """maior distancia de um vertice de A para TRAS de B (pelo lado de dentro), projetando dentro de B"""
    nb = normal(P, B)
    if nb.length < 1e-12: return 0.0
    nb.normalize(); tv = [P[i] for i in B]; prof = 0.0
    for i in A:
        d = (P[i] - tv[0]).dot(nb)
        if d < 0 and bari_dentro(P[i] - nb * d, tv): prof = max(prof, -d)
    return prof
def casos_inter(P, frame_tag):
    bvh = BVHTree.FromPolygons(P, TRI, all_triangles=True)
    bvh_all = None; out = []
    for a, b in bvh.overlap(bvh):
        if a >= b: continue
        A, B = TRI[a], TRI[b]
        sa, sb = {S(i) for i in A}, {S(i) for i in B}
        if sa & sb: out.append({"classe": "adjacente"}); continue
        seg = inter_seg(P, A, B)
        if seg is None: out.append({"classe": "rasante", "seg": 0}); continue
        L = (seg[0] - seg[1]).length; prof = max(penetracao(P, A, B), penetracao(P, B, A))
        m = (seg[0] + seg[1]) / 2
        if bvh_all is None: bvh_all = BVHTree.FromPolygons(P, TODOS, all_triangles=True)
        vis = visivel(bvh_all, m)
        cl = "rasante" if (L < 0.01 or prof < 0.003) else ("real_visivel" if vis else "real_oculta")
        out.append({"classe": cl, "tri": [a, b], "seg": round(L, 4), "prof": round(prof, 4), "vis_dirs": vis,
                    "pos": [round(c, 3) for c in m], "y_rep": round(sum(rest[i].y for i in A + B) / 6, 2), "quadro": frame_tag})
    return out
R = {}
# ---- repouso
bvh_all_rest = BVHTree.FromPolygons(rest, TODOS, all_triangles=True)
R["repouso_intersecoes"] = [c for c in casos_inter(rest, "repouso") if c["classe"] != "adjacente"]
# ---- faces dobradas (repouso), soldadas
ac = {}
for t in TRI:
    n = normal(rest, t)
    for i in t: ac[S(i)] = ac.get(S(i), Vector()) + n
dob = []
for k, t in enumerate(TRI):
    n = normal(rest, t); m = sum((ac[S(i)] for i in t), Vector())
    if n.length > 1e-12 and m.length > 1e-12 and n.normalized().dot(m.normalized()) < 0:
        c = sum((rest[i] for i in t), Vector()) / 3
        # o VERSO aparece? raios externos cujo primeiro impacto e esta face e chegam pelo lado do verso
        verso = 0; frente = 0
        for d in DIRS:
            h = bvh_all_rest.ray_cast(c + d * 200, -d)
            if h[0] is not None and (h[0] - c).length < 2e-3:
                if d.dot(n) < 0: verso += 1
                else: frente += 1
        ang = math.degrees(n.normalized().angle(m.normalized()))
        dob.append({"tri": k, "area": round(n.length / 2, 6), "pos": [round(x, 3) for x in c], "angulo_vs_lisa": round(ang, 1),
                    "verso_visivel_dirs": verso, "frente_visivel_dirs": frente})
R["faces_dobradas"] = dob
# ---- bordas abertas reais (solda difusa)
from collections import Counter
arestas = Counter()
for t in TRI:
    for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): arestas[frozenset((S(u), S(v)))] += 1
bord = [tuple(e) for e, n in arestas.items() if n == 1]
bm_ = []
for u, v in bord:
    m = (rest[u] + rest[v]) / 2; L = (rest[u] - rest[v]).length
    fres = min(((rest[a] + rest[b]) / 2 - m).length for a, b in bord if {a, b} != {u, v}) if len(bord) > 1 else 0
    bm_.append({"vertices": [u, v], "pos": [round(x, 3) for x in m], "comp": round(L, 4), "fresta_borda_vizinha": round(fres, 4),
                "vis_dirs": visivel(bvh_all_rest, m)})
R["bordas_abertas"] = sorted(bm_, key=lambda b: b["pos"][1])
# laços de borda (abertura fechada?) : componentes ligados das bordas
adj = {}
for u, v in bord: adj.setdefault(u, set()).add(v); adj.setdefault(v, set()).add(u)
vis_, lacos = set(), []
for s in adj:
    if s in vis_: continue
    pilha, comp = [s], []
    while pilha:
        x = pilha.pop()
        if x in vis_: continue
        vis_.add(x); comp.append(x); pilha += list(adj[x])
    lacos.append({"vertices": len(comp), "fechado": all(len(adj[x]) == 2 for x in comp),
                  "centro": [round(c, 3) for c in sum((rest[x] for x in comp), Vector()) / len(comp)],
                  "diametro": round(max((rest[a] - rest[b]).length for a in comp for b in comp), 4)})
R["bordas_lacos"] = lacos
# ---- ciclos: TODOS os frames
cic = {}
for clipe in ("idle_loop", "walk_loop", "fly_loop"):
    a = usar(clipe); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1])
    por_frame = {}; casos = []
    for f in range(f0, f1 + 1):
        scn.frame_set(f); P = avaliar()
        cs = casos_inter(P, f)
        cont = Counter(c["classe"] for c in cs); por_frame[f] = dict(cont)
        casos += [c for c in cs if c["classe"] in ("real_visivel", "real_oculta")]
    cic[clipe] = {"frames": [f0, f1], "por_frame": por_frame, "casos_reais": casos,
                  "max_por_classe": {k: max(pf.get(k, 0) for pf in por_frame.values()) for k in ("adjacente", "rasante", "real_oculta", "real_visivel")}}
R["ciclos"] = cic
json.dump(R, open(OUT, "w"), indent=1, ensure_ascii=False)
print("OK")
