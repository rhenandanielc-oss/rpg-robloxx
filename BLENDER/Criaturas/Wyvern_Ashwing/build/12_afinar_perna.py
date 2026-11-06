# Afinamento LOCAL da malha das pernas (escolhido pelo usuario em 05/11/2026) para o descanso do L2b: a canela deixa de
# entrar na coxa e o par perna x flanco se separa. So a perna afina (o flanco/corpo NAO se move).
# Metodo (repetido ITER vezes): em todos os quadros (30 Hz) de Deitar/Deitado/Levantar, deformacao por skinning linear
# proprio; para cada intersecao REAL com perna (solda difusa, segmento >= 0,01), o vertice de perna que esta dentro da
# outra superficie recebe o recuo necessario (profundidade + MARGEM) ao longo da normal dessa superficie; se o vertice de
# dentro e do corpo, recua o triangulo de perna (para dentro da propria perna). O recuo e levado ao espaco de repouso pela
# inversa da matriz de skinning do vertice, fica o maior por vertice entre os quadros, e e suavizado (laplaciano) so
# entre vertices de perna, com teto TETO por iteracao e TETO_TOTAL acumulado. Duplicatas de costura recebem o mesmo valor.
# Grava: posicoes da malha, Basis e as 2 shape keys (mesmo delta: os deltas das correctives nao mudam), normais
# customizadas recalculadas SO nos vertices movidos (as demais mantidas). Topologia/UV/pesos/ossos/actions intactos.
# Uso: blender -b Wyvern_E7_clipes_L2b.blend -P 12_afinar_perna.py -- <saida.blend> <relatorio.json> 0 0 0 0 <busca | aplicar K ALC>
# (o metodo valido e o RADIAL abaixo; os 4 numeros eram da v1 descartada e sao ignorados)
import bpy, sys, json, itertools, math
import numpy as np
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_ray_tri
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, REL = argv[0], argv[1]
ITER, MARGEM, TETO, TETO_TOTAL = (int(argv[2]), float(argv[3]), float(argv[4]), float(argv[5])) if len(argv) > 5 else (6, 0.04, 0.25, 0.6)
scn = bpy.context.scene
arm = bpy.data.objects["Wyvern_Rig"]; obj = bpy.data.objects["Wyvern"]; me = obj.data; key = me.shape_keys
NV = len(me.vertices); GR = {g.index: g.name for g in obj.vertex_groups}
BONES = [b.name for b in arm.data.bones]; BI = {b: i for i, b in enumerate(BONES)}
W = np.zeros((NV, len(BONES)))
for v in me.vertices:
    for g in v.groups: W[v.index, BI[GR[g.group]]] = g.weight
rest0 = np.array([v.co[:] for v in me.vertices])
kd = KDTree(NV)
for i, p in enumerate(rest0): kd.insert(p, i)
kd.balance(); S = np.arange(NV)
for i in range(NV):
    if S[i] != i: continue
    for _, j, _ in kd.find_range(Vector(rest0[i]), 1e-3):
        if j > i: S[j] = i
VIZ = defaultdict(set)
for e in me.edges:
    a, b = S[e.vertices[0]], S[e.vertices[1]]
    if a != b: VIZ[a].add(b); VIZ[b].add(a)
me.calc_loop_triangles(); TRIL = [tuple(t.vertices) for t in me.loop_triangles]
SOLD = [{int(S[i]) for i in t} for t in TRIL]
DOM = [BONES[int(np.argmax(W[i]))] for i in range(NV)]
EPV = np.array([d.startswith(("thigh", "calf", "foot", "toe")) for d in DOM])
OT = [Counter(DOM[i] for i in t).most_common(1)[0][0] for t in TRIL]
EP = [o.startswith(("thigh", "calf", "foot", "toe")) for o in OT]
KB = {k.name: np.array([v.co[:] for v in k.data]) for k in key.key_blocks}
DK = {n: KB[n] - KB["Basis"] for n in KB}
MLI = [np.array(b.matrix_local.inverted()) for b in arm.data.bones]
MWo = np.array(obj.matrix_world); MWa = np.array(arm.matrix_world); MWoi = np.linalg.inv(MWo); MWai = np.linalg.inv(MWa)
def usar(nome):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        if ob.animation_data is None: ob.animation_data_create()
        ob.animation_data.action = a
        sl = [s for s in a.slots if s.target_id_type == tipo]
        if sl: ob.animation_data.action_slot = sl[0]
    return a
ESTADOS = []
for nome in ("Deitar", "Deitado", "Levantar"):
    a = usar(nome); f1 = a.frame_range[1]
    for k in range(int(f1 / 0.8 + 1e-6) + 1):
        f = k * 0.8; scn.frame_set(int(f), subframe=f - int(f))
        Ms = np.stack([MWoi @ MWa @ np.array(pb.matrix) @ MLI[i] @ MWai @ MWo for i, pb in enumerate(arm.pose.bones)])
        ESTADOS.append((nome, round(f, 1), Ms, key.key_blocks["fold_corrective_L"].value, key.key_blocks["fold_corrective_R"].value))
def blend_mats(Ms):
    return np.einsum("vb,bij->vij", W, Ms)            # matriz de skinning por vertice (espaco do objeto)
def deformar(rest, Ms, fl, fr):
    co = rest + fl * DK["fold_corrective_L"] + fr * DK["fold_corrective_R"]
    Bv = blend_mats(Ms); out = np.einsum("vij,vj->vi", Bv[:, :3, :3], co) + Bv[:, :3, 3]
    return out @ MWo[:3, :3].T + MWo[:3, 3], Bv
def bari(p, tv, tol=0.02):
    a, b, c = tv; v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14: return False
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    return v >= -tol and w >= -tol and v + w <= 1 + tol
DIRS = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (0, 1) if (x, y, z) != (0, 0, 0)]
def analisar(co, coletar=True):
    """devolve (pedidos {vertice: vetor no mundo}, metricas)"""
    P = [Vector(c) for c in co]; bvh = BVHTree.FromPolygons(P, TRIL, all_triangles=True)
    ped = {}; n = nv = 0; dmax = dvis = 0.0; pares = defaultdict(float)
    def pedir(i, vec):
        if i not in ped or vec.length > ped[i].length: ped[i] = vec
    for a, b in bvh.overlap(bvh):
        if a >= b or not (EP[a] or EP[b]) or SOLD[a] & SOLD[b]: continue
        A, B = TRIL[a], TRIL[b]; pts = []
        for X_, Y_ in ((A, B), (B, A)):
            tv = [P[i] for i in Y_]
            for u, v in ((X_[0], X_[1]), (X_[1], X_[2]), (X_[2], X_[0])):
                q = intersect_ray_tri(*tv, P[v] - P[u], P[u], True)
                if q is not None and (q - P[u]).dot(q - P[v]) <= 1e-12: pts.append(q)
        if len(pts) < 2: continue
        p1, p2 = max(itertools.combinations(pts, 2), key=lambda ab: (ab[0] - ab[1]).length)
        if (p1 - p2).length < 0.01: continue
        dpar = 0.0
        for A_, B_, ia, ib in ((A, B, a, b), (B, A, b, a)):
            nb = (P[B_[1]] - P[B_[0]]).cross(P[B_[2]] - P[B_[0]])
            if nb.length < 1e-12: continue
            nb.normalize(); tv = [P[i] for i in B_]
            for i in A_:
                d = (P[i] - tv[0]).dot(nb)
                if d < 0 and bari(P[i] - nb * d, tv):
                    dpar = max(dpar, -d)
                    if not coletar: continue
                    if EPV[i]: pedir(i, nb * (-d + MARGEM))                 # vertice de perna sai de dentro da superficie
                    elif EP[ib]:                                            # vertice do corpo dentro da perna: a perna recua
                        for j in B_:
                            if EPV[j]: pedir(j, -nb * (-d + MARGEM))
        if dpar < 0.003: continue
        n += 1; dmax = max(dmax, dpar); m = (p1 + p2) / 2; vis = 0
        for dd in DIRS:
            h = bvh.ray_cast(m + dd * 200, -dd)
            if h[0] is not None and (h[0] - m).length < 2e-3: vis = 1; break
        if vis:
            nv += 1; dvis = max(dvis, dpar); par = "|".join(sorted((OT[a], OT[b]))); pares[par] = max(pares[par], dpar)
    return ped, {"reais": n, "visiveis": nv, "prof_max": round(dmax, 3), "prof_vis": round(dvis, 3),
                 "pares_vis": {k: round(v, 3) for k, v in sorted(pares.items(), key=lambda kv: -kv[1])[:6]}}
def medir(rest):
    pior = {}
    for nome, f, Ms, fl, fr in ESTADOS:
        co, _ = deformar(rest, Ms, fl, fr); _, m = analisar(co, False); m["f"] = f
        if nome not in pior or (m["prof_vis"], m["visiveis"]) > (pior[nome]["prof_vis"], pior[nome]["visiveis"]): pior[nome] = m
    return pior
# ---------------------------------------------------------------- afinamento RADIAL suave (v2; o empurrao por vertice da
# v1 deste script oscilava e dobrava a pele sobre ela mesma - descartado)
# Para cada vertice de coxa/canela: r = vetor radial ao eixo do osso dominante (repouso). Na pose Deitado (quadro 0), se o
# lado do vertice esta VOLTADO para a superficie vizinha (canela para a coxa; coxa para a canela; ambos para o eixo do
# corpo), recua em -r por K * f * g * |r|, f = cos do angulo (>= 0) e g = proximidade (1 a 0 em ALC studs). Depois
# suaviza o campo de deslocamento so entre vertices de perna (sem degraus na juncao coxa/canela/pe).
def segmento(M, b): return np.array(cabeca(M, b)[:]), np.array(ponta(M, b)[:])
def mais_perto(p, a, b):
    ab = b - a; t = np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-9), 0, 1); return a + t * ab
usar("Deitado"); scn.frame_set(0); bpy.context.view_layer.update()
def cabeca(M, b): return arm.matrix_world @ arm.pose.bones[b].head
def ponta(M, b): return arm.matrix_world @ arm.pose.bones[b].tail
ALVOS_DE = {}
for s_ in "LR":
    corpo = [segmento(None, b) for b in ("pelvis", "spine_01", "spine_02")]
    ALVOS_DE["thigh_" + s_] = [segmento(None, "calf_" + s_), segmento(None, "foot_" + s_)] + corpo
    ALVOS_DE["calf_" + s_] = [segmento(None, "thigh_" + s_)] + corpo
    ALVOS_DE["foot_" + s_] = [segmento(None, "calf_" + s_)] + corpo
Ms0 = ESTADOS[[k for k, e in enumerate(ESTADOS) if e[0] == "Deitado"][0]][2]
co_dei, _ = deformar(rest0, Ms0, ESTADOS[0][3], ESTADOS[0][4])
EIXO_REST = {b.name: (np.array((obj.matrix_world.inverted() @ arm.matrix_world @ b.head_local)[:]), np.array((obj.matrix_world.inverted() @ arm.matrix_world @ b.tail_local)[:])) for b in arm.data.bones}
def campo(K, ALC):
    D = np.zeros((NV, 3))
    for i in range(NV):
        b = DOM[i]
        if b not in ALVOS_DE: continue
        a0, a1 = EIXO_REST[b]; pr = mais_perto(rest0[i], a0, a1); r = rest0[i] - pr; Lr = np.linalg.norm(r)
        if Lr < 1e-4: continue
        # radial na pose deitada (mundo) e direcao a superficie vizinha mais perto
        Ms_b = Ms0[BI[b]]
        h0 = np.array(cabeca(None, b)[:]); h1 = np.array(ponta(None, b)[:]); pd = co_dei[i]; rd = pd - mais_perto(pd, h0, h1)
        if np.linalg.norm(rd) < 1e-4: continue
        rd /= np.linalg.norm(rd); fg = 0.0
        for sa, sb in ALVOS_DE[b]:                                   # cada superficie vizinha conta (vale a maior)
            q = mais_perto(pd, sa, sb); d = np.linalg.norm(q - pd)
            fg = max(fg, max(0.0, float(np.dot(rd, (q - pd) / max(d, 1e-6)))) * max(0.0, 1.0 - d / ALC))
        D[i] = -r / Lr * K * fg * Lr
    # solda + suavizacao so entre vertices de perna
    for r_ in set(S.tolist()):
        pass
    Dr = defaultdict(lambda: np.zeros(3)); cnt = Counter()
    for i in range(NV): Dr[int(S[i])] += D[i]; cnt[int(S[i])] += 1
    Dr = {r_: Dr[r_] / cnt[r_] for r_ in Dr}
    for _ in range(4):
        D2 = {}
        for r_ in RAIZ_P:
            nb = [n for n in VIZ[r_] if n in Dr and EPV[n]]
            D2[r_] = 0.5 * Dr[r_] + 0.5 * np.mean([Dr[n] for n in nb], axis=0) if nb else Dr[r_]
        Dr.update(D2)
    out = np.zeros((NV, 3))
    for i in range(NV):
        if EPV[i]: out[i] = Dr[int(S[i])]
    return out
RAIZ_P = sorted({int(S[i]) for i in range(NV) if EPV[i]})
LOG = {"antes": medir(rest0), "busca": []}
print("ANTES", json.dumps(LOG["antes"]), flush=True)
MODO = argv[6] if len(argv) > 6 else "aplicar"
CANDS = [(0.35, 3.0), (0.5, 3.0), (0.5, 4.5), (0.65, 4.5)] if MODO == "busca" else [(float(argv[7]), float(argv[8]))]
for K, ALC in CANDS:
    Dc = campo(K, ALC); m = medir(rest0 + Dc); dl = np.linalg.norm(Dc, axis=1)
    LOG["busca"].append({"K": K, "ALC": ALC, "desl_max": round(float(dl.max()), 3), "movidos": int((dl > 1e-4).sum()), "medida": m})
    print("CAND K=%.2f ALC=%.1f" % (K, ALC), "desl_max", round(float(dl.max()), 3), "movidos", int((dl > 1e-4).sum()), json.dumps(m), flush=True)
if MODO == "busca":
    json.dump(LOG, open(REL, "w"), indent=1); print("OK"); raise SystemExit
rest = rest0 + Dc
# ---------------------------------------------------------------- gravacao
desl = np.linalg.norm(rest - rest0, axis=1); mov = np.nonzero(desl > 1e-5)[0]
delta = rest - rest0
for v in me.vertices: v.co = rest[v.index]
for k in key.key_blocks:
    arr = KB[k.name] + delta
    for i in mov: k.data[int(i)].co = arr[int(i)]
me.update()
cn = np.array([n.vector[:] for n in me.corner_normals])
# normais suaves soldadas so dos vertices movidos (soma das normais de face de todos os duplicados)
fn = defaultdict(lambda: np.zeros(3))
movs = {int(S[i]) for i in mov}
for p in me.polygons:
    rs = {int(S[v]) for v in p.vertices}
    if rs & movs:
        for r in rs & movs: fn[r] += np.array(p.normal[:]) * p.area
loops_mov = 0
for l in me.loops:
    r = int(S[l.vertex_index])
    if r in movs:
        n = fn[r]; cn[l.index] = n / (np.linalg.norm(n) + 1e-12); loops_mov += 1
me.normals_split_custom_set([tuple(x) for x in cn]); me.update()
cn2 = np.array([n.vector[:] for n in me.corner_normals])
fixos = [l.index for l in me.loops if int(S[l.vertex_index]) not in movs]
LOG["gravacao"] = {"vertices_movidos": int(len(mov)), "raizes_movidas": len(movs), "loops_normal_nova": loops_mov,
                   "desl_max": round(float(desl.max()), 3), "desl_medio_movidos": round(float(desl[mov].mean()), 3) if len(mov) else 0,
                   "por_osso": dict(Counter(DOM[int(i)] for i in mov)), "por_lado": dict(Counter("L" if rest0[int(i)][0] > 0 else "R" for i in mov)),
                   "fora_da_perna_movidos": int(sum(1 for i in mov if not EPV[int(i)])),
                   "normal_max_dif_fora": float(np.abs(cn2[fixos] - cn[fixos]).max()) if fixos else 0.0,
                   "lista_vertices": [int(i) for i in mov]}
print("GRAV", json.dumps({k: v for k, v in LOG["gravacao"].items() if k != "lista_vertices"}), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(LOG, open(REL, "w"), indent=1)
print("OK")
