# QA numerico de clipes (mesmo metodo para os novos e para os originais do Ashwing, como linha de base).
# Por clipe, em TODAS as amostras de 30 Hz:
#   emenda do laco (graus: maior diferenca de rotacao local entre o primeiro e o ultimo quadro);
#   salto (graus/amostra: maior variacao de rotacao local de um osso entre amostras vizinhas);
#   z minimo da malha (chao em z = 0 no repouso do idle);
#   pes (clipes no lugar): velocidade horizontal do dedo apoiado (media e desvio) -> velocidade aparente e escorregao;
#   autointersecoes REAIS da malha inteira (solda difusa; profundidade >= 0,02 stud; segmento >= 0,01).
# Uso: blender -b <v.blend> -P 07c_qa_clipes.py -- <saida.json> <clipe1,clipe2,...>
import bpy, sys, json, math, itertools
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_ray_tri
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, CLIPES = argv[0], argv[1].split(",")
scn = bpy.context.scene; FPS = scn.render.fps
arm = bpy.data.objects["Wyvern_Rig"]; obj = bpy.data.objects["Wyvern"]; me = obj.data; key = me.shape_keys
me.calc_loop_triangles(); TRI = [t.vertices[:] for t in me.loop_triangles]
rest = [obj.matrix_world @ v.co for v in me.vertices]
kd = KDTree(len(rest))
for i, p in enumerate(rest): kd.insert(p, i)
kd.balance(); S = {}
for i in range(len(rest)):
    if i in S: continue
    for _, j, _ in kd.find_range(rest[i], 1e-3): S.setdefault(j, i)
SOLD = [{S[i] for i in t} for t in TRI]
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
    return max(((a - b).length for a, b in itertools.combinations(pts, 2)), default=0.0)
def intersecoes(P):
    bvh = BVHTree.FromPolygons(P, TRI, all_triangles=True); reais = []
    for a, b in bvh.overlap(bvh):
        if a >= b or SOLD[a] & SOLD[b]: continue
        L = seg(P, TRI[a], TRI[b])
        if L < 0.01: continue
        d = max(prof(P, TRI[a], TRI[b]), prof(P, TRI[b], TRI[a]))
        if d >= 0.02:
            c = sum((P[i] for i in TRI[a]), Vector()) / 3
            reais.append((a, b, round(d, 3), [round(x, 2) for x in c]))
    return reais
grupos = {g.index: g.name for g in obj.vertex_groups}
def regiao(i):
    gs = me.vertices[i].groups
    return grupos[max(gs, key=lambda g: g.weight).group] if len(gs) else "?"
R = {}
for nome in CLIPES:
    a = usar(nome); f1 = a.frame_range[1]; loop = bool(a.get("loop", nome.endswith("_loop")))
    passo = 0.8; fs = []; f = 0.0
    while f <= f1 + 1e-6: fs.append(f); f += passo
    rots = []; zmin = []; toes = []; inter = []; pior_inter = []
    for f in fs:
        ir(f)
        rots.append({pb.name: pb.matrix_basis.to_quaternion() for pb in arm.pose.bones})
        P = malha(); zmin.append(min(p.z for p in P))
        toes.append([arm.matrix_world @ arm.pose.bones[t].tail for t in ("toe_L", "toe_R")])
        rr = intersecoes(P); inter.append(len(rr))
        if len(rr) > len(pior_inter): pior_inter = [(round(f, 1),) + x for x in rr]
    def dang(q1, q2): return math.degrees(q1.rotation_difference(q2).angle)
    salto = max(((dang(rots[k][b], rots[k + 1][b]), b, round(fs[k], 1)) for k in range(len(fs) - 1) for b in rots[0]), default=(0, "", 0))
    emenda = max((dang(rots[0][b], rots[-1][b]), b) for b in rots[0]) if loop else None
    # pes: apoio = dedo a menos de 0,35 do menor z do dedo no clipe
    pes = {}
    for k_, lado in enumerate("LR"):
        zs = [t[k_].z for t in toes]; zb = min(zs); vel = []
        for k in range(len(fs) - 1):
            if zs[k] < zb + 0.35 and zs[k + 1] < zb + 0.35:
                d = toes[k + 1][k_] - toes[k][k_]; vel.append(math.hypot(d.x, d.y) / (passo / FPS))
        if vel:
            m = sum(vel) / len(vel); sd = (sum((v - m) ** 2 for v in vel) / len(vel)) ** 0.5
            pes[lado] = {"amostras_apoio": len(vel), "vel_media_studs_s": round(m, 2), "desvio": round(sd, 2), "z_dedo_min": round(zb, 2)}
    reg_inter = sorted({regiao(TRI[x[1]][0]) + "|" + regiao(TRI[x[2]][0]) for x in pior_inter})
    R[nome] = {"amostras": len(fs), "loop": loop, "emenda_graus": None if emenda is None else [round(emenda[0], 2), emenda[1]],
               "salto_max_graus_amostra": [round(salto[0], 2), salto[1], salto[2]],
               "z_malha_min": round(min(zmin), 3), "z_malha_max_dos_minimos": round(max(zmin), 3),
               "pes": pes, "intersecoes_reais_max": max(inter), "intersecoes_reais_media": round(sum(inter) / len(inter), 2),
               "pior_quadro_intersecoes": pior_inter[:12], "regioes_pior": reg_inter[:12]}
    print("QA", nome, json.dumps({k: v for k, v in R[nome].items() if k != "pior_quadro_intersecoes"}), flush=True)
json.dump(R, open(OUT, "w"), indent=1, ensure_ascii=False)
print("OK")
