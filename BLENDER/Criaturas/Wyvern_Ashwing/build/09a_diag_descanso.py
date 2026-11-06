# Diagnostico (somente leitura) do conjunto Deitar -> Deitado -> Levantar, com o idle como linha de base.
# Por quadro (passo 0,8 = 30 Hz), na malha inteira com solda difusa (como 07c/05a):
#   intersecoes classificadas: adjacente | rasante (segmento < 0,01 ou profundidade < 0,003) | real_oculta | real_visivel
#   visivel = o ponto medio do segmento de intersecao e o 1o impacto de algum raio externo VINDO DE CIMA DO CHAO
#   (das 26 direcoes, so as com componente z >= 0: o chao tapa as de baixo); par de ossos dominantes de cada triangulo
#   pes: jarrete/bola/ponta do dedo (z e velocidade horizontal) -> apoio carregado que desliza
#   emendas: diferenca de pose (graus por osso e deslocamento maximo de vertice) entre fim/inicio de clipes vizinhos
# Uso: blender -b <v.blend> -P 09a_diag_descanso.py -- <saida.json> [clipes=idle_loop,Deitar,Deitado,Levantar]
import bpy, sys, json, math, itertools
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_ray_tri
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]; CLIPES = argv[1].split(",") if len(argv) > 1 else ["idle_loop", "Deitar", "Deitado", "Levantar"]
scn = bpy.context.scene; FPS = scn.render.fps
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
DOM = [GR[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "?" for v in me.vertices]
def osso_tri(t): return Counter(DOM[i] for i in t).most_common(1)[0][0]
DIRS = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]
DIRS_CIMA = [d for d in DIRS if d.z >= 0]
def usar(nome):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        if ob.animation_data is None: ob.animation_data_create()
        ob.animation_data.action = a
        sl = [s for s in a.slots if s.target_id_type == tipo]
        if sl: ob.animation_data.action_slot = sl[0]
    return a
def ir(f): scn.frame_set(int(f), subframe=f - int(f))
def malha():
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    return [obj.matrix_world @ v.co for v in ev.vertices]
def normal(P, t):
    a, b, c = (P[i] for i in t); return (b - a).cross(c - a)
def bari_dentro(p, tv, tol=0.02):
    a, b, c = tv; v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14: return False
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    return v >= -tol and w >= -tol and v + w <= 1 + tol
def prof(P, A, B):
    nb = normal(P, B)
    if nb.length < 1e-12: return 0.0
    nb.normalize(); tv = [P[i] for i in B]; d_ = 0.0
    for i in A:
        d = (P[i] - tv[0]).dot(nb)
        if d < 0 and bari_dentro(P[i] - nb * d, tv): d_ = max(d_, -d)
    return d_
def seg(P, A, B):
    pts = []
    for X_, Y_ in ((A, B), (B, A)):
        tv = [P[i] for i in Y_]
        for u, v in ((X_[0], X_[1]), (X_[1], X_[2]), (X_[2], X_[0])):
            q = intersect_ray_tri(*tv, P[v] - P[u], P[u], True)
            if q is not None and (q - P[u]).dot(q - P[v]) <= 1e-12: pts.append(q)
    if len(pts) < 2: return None
    return max(itertools.combinations(pts, 2), key=lambda ab: (ab[0] - ab[1]).length)
def visivel(bvh, p):
    k = 0
    for d in DIRS_CIMA:
        o = p + d * 200; h = bvh.ray_cast(o, -d)
        if h[0] is not None and (h[0] - p).length < 2e-3: k += 1
    return k
def casos(P):
    bvh = BVHTree.FromPolygons(P, TRI, all_triangles=True); out = []
    for a, b in bvh.overlap(bvh):
        if a >= b or SOLD[a] & SOLD[b]: continue
        sg = seg(P, TRI[a], TRI[b])
        if sg is None: continue
        L = (sg[0] - sg[1]).length; d = max(prof(P, TRI[a], TRI[b]), prof(P, TRI[b], TRI[a]))
        if L < 0.01 or d < 0.003: continue
        m = (sg[0] + sg[1]) / 2
        par = "|".join(sorted((osso_tri(TRI[a]), osso_tri(TRI[b]))))
        out.append({"par": par, "prof": round(d, 3), "seg": round(L, 3), "pos": [round(x, 2) for x in m],
                    "vis": visivel(bvh, m), "tri": [a, b]})
    return out
def grupo(par):
    a, b = par.split("|")
    perna = lambda o: o.startswith(("thigh", "calf", "foot", "toe"))
    corpo = lambda o: o.startswith(("pelvis", "spine", "root", "tail_01", "tail_02"))
    if perna(a) and perna(b): return "perna-perna"
    if (perna(a) and corpo(b)) or (perna(b) and corpo(a)): return "perna-corpo"
    if perna(a) or perna(b): return "perna-outro"
    asa = lambda o: any(k in o for k in ("shoulder", "upperarm", "forearm", "hand", "finger", "strut", "thumb"))
    if asa(a) or asa(b): return "asa"
    return "outro"
R = {"clipes": {}, "emendas": {}}
POSE = {}
for nome in CLIPES:
    a = usar(nome); f1 = a.frame_range[1]
    fs = [k * 0.8 for k in range(int(f1 / 0.8 + 1e-6) + 1)]
    if nome == "idle_loop": fs = fs[::6]
    quadros = []; pes = defaultdict(list)
    for f in fs:
        ir(f); P = malha(); cs = casos(P)
        cnt = Counter(grupo(c["par"]) for c in cs)
        vis = [c for c in cs if c["vis"] > 0]
        cntv = Counter(grupo(c["par"]) for c in vis)
        quadros.append({"f": round(f, 1), "reais": len(cs), "por_grupo": dict(cnt), "visiveis": len(vis), "visiveis_por_grupo": dict(cntv),
                        "prof_max_perna": max([c["prof"] for c in cs if grupo(c["par"]).startswith("perna")], default=0),
                        "pares_perna_visiveis": Counter(c["par"] for c in vis if grupo(c["par"]).startswith("perna")).most_common(6),
                        "casos_perna_visiveis": sorted([c for c in vis if grupo(c["par"]).startswith("perna")], key=lambda c: -c["prof"])[:6],
                        "zmin": round(min(p.z for p in P), 3)})
        for s in "LR":
            M = arm.matrix_world
            pes[s].append([round(f, 1)] + [list(round(x, 3) for x in (M @ arm.pose.bones[b].tail)) for b in ("calf_" + s, "foot_" + s, "toe_" + s)])
        if f in (fs[0], fs[-1]):
            POSE[(nome, "ini" if f == fs[0] else "fim")] = ({pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}, P, key.key_blocks["fold_corrective_L"].value)
        print("Q", nome, round(f, 1), len(cs), len(vis), dict(cntv), flush=True)
    # deslize: velocidade horizontal da ponta e da bola do pe quando perto do chao (z < 0,5 da malha nao; usa osso)
    desl = {}
    for s in "LR":
        v = []
        for k in range(len(pes[s]) - 1):
            f0, f1_ = pes[s][k][0], pes[s][k + 1][0]; dt = (f1_ - f0) / FPS
            for j, nm in ((2, "bola"), (3, "ponta")):
                p0, p1 = Vector(pes[s][k][j]), Vector(pes[s][k + 1][j])
                v.append((nm, f0, round(math.hypot(p1.x - p0.x, p1.y - p0.y) / dt, 2), round(p0.z, 2)))
        desl[s] = sorted(v, key=lambda x: -x[2])[:8]
    R["clipes"][nome] = {"quadros": quadros, "pes_trajetoria": dict(pes), "maiores_velocidades_pe": desl}
def dif(a, b):
    (ma, Pa, fa), (mb, Pb, fb) = POSE[a], POSE[b]
    ang = max((math.degrees(ma[n].to_quaternion().rotation_difference(mb[n].to_quaternion()).angle), n) for n in ma)
    dv = max((Pa[i] - Pb[i]).length for i in range(len(Pa)))
    return {"graus_max": [round(ang[0], 2), ang[1]], "desloc_max_vertice": round(dv, 3), "fold": [round(fa, 3), round(fb, 3)]}
for a, b in ((("idle_loop", "ini"), ("Deitar", "ini")), (("Deitar", "fim"), ("Deitado", "ini")), (("Deitado", "fim"), ("Deitado", "ini")),
             (("Deitado", "fim"), ("Levantar", "ini")), (("Levantar", "fim"), ("idle_loop", "ini"))):
    if a in POSE and b in POSE: R["emendas"][a[0] + "." + a[1] + "->" + b[0] + "." + b[1]] = dif(a, b)
print("EMENDAS", json.dumps(R["emendas"]))
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
