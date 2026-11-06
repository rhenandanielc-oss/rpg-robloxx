# M0 (somente leitura) da prega da perna: em todos os quadros (30 Hz) dos clipes pedidos, acha as intersecoes REAIS
# (solda difusa; segmento >= 0,01; profundidade >= 0,003) que envolvem perna, e registra por vertice: lado, superficie
# (osso dominante), quantos quadros, profundidade maxima, visibilidade (raio vindo de cima do chao), posicao de repouso
# e pesos atuais. Tambem resume por par de superficies e por quadro.
# Uso: blender -b <v.blend> -P 10a_m0_prega.py -- <saida.json> <clipe1,clipe2,...>
import bpy, sys, json, itertools
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_ray_tri
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, CLIPES = argv[0], argv[1].split(",")
scn = bpy.context.scene
arm = bpy.data.objects["Wyvern_Rig"]; obj = bpy.data.objects["Wyvern"]; me = obj.data; key = me.shape_keys
me.calc_loop_triangles(); TRI = [tuple(t.vertices) for t in me.loop_triangles]
rest = [obj.matrix_world @ v.co for v in me.vertices]
kd = KDTree(len(rest))
for i, p in enumerate(rest): kd.insert(p, i)
kd.balance(); S = {}
for i in range(len(rest)):
    if i in S: continue
    for _, j, _ in kd.find_range(rest[i], 1e-3): S.setdefault(j, i)
SOLD = [{S[i] for i in t} for t in TRI]
GR = {g.index: g.name for g in obj.vertex_groups}
def pesos(i): return sorted(((GR[g.group], round(g.weight, 4)) for g in me.vertices[i].groups if g.weight > 1e-6), key=lambda x: -x[1])
DOM = [pesos(i)[0][0] if pesos(i) else "?" for i in range(len(me.vertices))]
OT = [Counter(DOM[i] for i in t).most_common(1)[0][0] for t in TRI]
EP = [o.startswith(("thigh", "calf", "foot", "toe")) for o in OT]
DIRS = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (0, 1) if (x, y, z) != (0, 0, 0)]
def usar(nome):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        if ob.animation_data is None: ob.animation_data_create()
        ob.animation_data.action = a
        sl = [s for s in a.slots if s.target_id_type == tipo]
        if sl: ob.animation_data.action_slot = sl[0]
    return a
def bari(p, tv, tol=0.02):
    a, b, c = tv; v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14: return False
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    return v >= -tol and w >= -tol and v + w <= 1 + tol
def prof_v(P, A, B):
    """profundidade por vertice de A atras de B"""
    nb = (P[B[1]] - P[B[0]]).cross(P[B[2]] - P[B[0]])
    if nb.length < 1e-12: return {}
    nb.normalize(); tv = [P[i] for i in B]; r = {}
    for i in A:
        d = (P[i] - tv[0]).dot(nb)
        if d < 0 and bari(P[i] - nb * d, tv): r[i] = -d
    return r
def casos(P):
    bvh = BVHTree.FromPolygons(P, TRI, all_triangles=True); out = []
    for a, b in bvh.overlap(bvh):
        if a >= b or not (EP[a] or EP[b]) or SOLD[a] & SOLD[b]: continue
        A, B = TRI[a], TRI[b]; pts = []
        for X_, Y_ in ((A, B), (B, A)):
            tv = [P[i] for i in Y_]
            for u, v in ((X_[0], X_[1]), (X_[1], X_[2]), (X_[2], X_[0])):
                q = intersect_ray_tri(*tv, P[v] - P[u], P[u], True)
                if q is not None and (q - P[u]).dot(q - P[v]) <= 1e-12: pts.append(q)
        if len(pts) < 2: continue
        p1, p2 = max(itertools.combinations(pts, 2), key=lambda ab: (ab[0] - ab[1]).length)
        if (p1 - p2).length < 0.01: continue
        pa, pb = prof_v(P, A, B), prof_v(P, B, A)
        d = max(list(pa.values()) + list(pb.values()) + [0])
        if d < 0.003: continue
        m = (p1 + p2) / 2; vis = 0
        for dd in DIRS:
            h = bvh.ray_cast(m + dd * 200, -dd)
            if h[0] is not None and (h[0] - m).length < 2e-3: vis += 1
        out.append((a, b, d, vis, pa, pb))
    return out
VERT = defaultdict(lambda: {"quadros": 0, "prof_max": 0.0, "visivel": 0}); PAR = defaultdict(lambda: {"casos": 0, "prof_max": 0.0, "vis_max": 0.0, "quadro_pior": None})
QUAD = {}
for nome in CLIPES:
    a = usar(nome); f1 = a.frame_range[1]; fs = [k * 0.8 for k in range(int(f1 / 0.8 + 1e-6) + 1)]; QUAD[nome] = []
    for f in fs:
        scn.frame_set(int(f), subframe=f - int(f))
        ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data; P = [obj.matrix_world @ v.co for v in ev.vertices]
        cs = casos(P); vistos = set(); dvmax = 0.0
        for a_, b_, d, vis, pa, pb in cs:
            par = "|".join(sorted((OT[a_], OT[b_]))); pr = PAR[par]; pr["casos"] += 1
            if d > pr["prof_max"]: pr["prof_max"] = round(d, 3)
            if vis and d > pr["vis_max"]: pr["vis_max"] = round(d, 3); pr["quadro_pior"] = [nome, round(f, 1)]
            if vis: dvmax = max(dvmax, d)
            for i in set(TRI[a_]) | set(TRI[b_]):
                dv = max(pa.get(i, 0), pb.get(i, 0))
                rec = VERT[i]
                if (nome, f, i) not in vistos: rec["quadros"] += 1; vistos.add((nome, f, i))
                rec["prof_max"] = max(rec["prof_max"], round(dv, 3))
                if vis: rec["visivel"] += 1
        QUAD[nome].append([round(f, 1), len(cs), sum(1 for c in cs if c[3]), round(max([c[2] for c in cs], default=0), 3), round(dvmax, 3)])
        print("Q", nome, round(f, 1), len(cs), flush=True)
lado = lambda i: "L" if rest[i].x > 0 else "R"
V = {}
for i, r in VERT.items():
    V[i] = dict(r, lado=lado(i), dom=DOM[i], rest=[round(x, 3) for x in rest[i]], pesos=pesos(i))
res = {"pares": dict(sorted(PAR.items(), key=lambda kv: -kv[1]["vis_max"])), "quadros": QUAD,
       "vertices_por_dom": {s: dict(Counter(v["dom"] for v in V.values() if v["lado"] == s)) for s in "LR"},
       "vertices": V}
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=0, ensure_ascii=False)
print("PARES", json.dumps(dict(list(res["pares"].items())[:14])))
print("DOM", json.dumps(res["vertices_por_dom"]))
print("OK")
