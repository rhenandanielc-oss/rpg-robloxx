# Ajuste LOCAL de pesos nas pregas das pernas (joelho, jarrete, quadril/flanco), so na selecao documentada.
# Selecao (reproduzivel): vertices com intersecao real >= PMIN no M0 (10a_m0_prega.py, Deitar/Deitado/Levantar do L2b),
#   soldados pelas costuras (duplicatas de UV recebem o mesmo peso), dilatados ANEIS aneis no grafo soldado,
#   restritos a vertices cujos pesos ja usam so ossos de PERNA_OK (perna do lado + pelvis/spine_01/spine_02).
# Operacao: suavizacao laplaciana dos pesos DENTRO da selecao (borda da selecao e o resto da malha fixos), com mascara
#   1 no nucleo -> 0 na borda, intensidade ALFA e K iteracoes; depois mantem os 4 maiores e normaliza (limite do asset: 4).
# Avaliacao rapida: skinning linear proprio em numpy (conferido contra o Blender), intersecoes reais com perna nos clipes.
# Uso: blender -b <L2b.blend> -P 10b_pesos_prega.py -- <m0.json> <saida.json> busca
#      blender -b <L2b.blend> -P 10b_pesos_prega.py -- <m0.json> <saida.json> aplicar <ALFA> <K> <ANEIS> <FLANCO 0/1> <saida.blend>
import bpy, sys, json, math, itertools, time
import numpy as np
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_ray_tri
argv = sys.argv[sys.argv.index("--") + 1:]
M0, OUT, MODO = argv[0], argv[1], argv[2]
scn = bpy.context.scene; FPS = scn.render.fps
arm = bpy.data.objects["Wyvern_Rig"]; obj = bpy.data.objects["Wyvern"]; me = obj.data; key = me.shape_keys
NV = len(me.vertices); GR = {g.index: g.name for g in obj.vertex_groups}; GI = {v: k for k, v in GR.items()}
BONES = [b.name for b in arm.data.bones]; BI = {b: i for i, b in enumerate(BONES)}
# ---------------------------------------------------------------- pesos como matriz densa (NV x ossos)
W0 = np.zeros((NV, len(BONES)))
for v in me.vertices:
    for g in v.groups: W0[v.index, BI[GR[g.group]]] = g.weight
# ---------------------------------------------------------------- solda e adjacencia
rest = np.array([v.co[:] for v in me.vertices])
kd = KDTree(NV)
for i, p in enumerate(rest): kd.insert(p, i)
kd.balance(); S = np.arange(NV)
for i in range(NV):
    if S[i] != i: continue
    for _, j, _ in kd.find_range(Vector(rest[i]), 1e-3):
        if j > i: S[j] = i
RAIZ = sorted(set(S.tolist())); RI = {r: k for k, r in enumerate(RAIZ)}
VIZ = defaultdict(set)
for e in me.edges:
    a, b = S[e.vertices[0]], S[e.vertices[1]]
    if a != b: VIZ[a].add(b); VIZ[b].add(a)
me.calc_loop_triangles(); TRI = np.array([t.vertices[:] for t in me.loop_triangles]); TRIL = [tuple(t) for t in TRI.tolist()]
SOLD = [{int(S[i]) for i in t} for t in TRIL]
DOM = [BONES[int(np.argmax(W0[i]))] for i in range(NV)]
OT = [Counter(DOM[i] for i in t).most_common(1)[0][0] for t in TRIL]
EP = [o.startswith(("thigh", "calf", "foot", "toe")) for o in OT]
# ---------------------------------------------------------------- selecao
m0 = json.load(open(M0, encoding="utf-8"))["vertices"]
def selecao(pmin, aneis, flanco):
    ok = {s: {BI[b] for b in ("thigh_" + s, "calf_" + s, "foot_" + s, "toe_" + s) + (("pelvis", "spine_01", "spine_02") if flanco else ())} for s in "LR"}
    lado = lambda r: "L" if rest[r][0] > 0 else "R"
    def permitido(r): return set(np.nonzero(W0[r] > 1e-6)[0].tolist()) <= ok[lado(r)]
    nucleo = {int(S[int(i)]) for i, v in m0.items() if v["prof_max"] >= pmin}
    nucleo = {r for r in nucleo if permitido(r)}
    anel = {r: 0 for r in nucleo}; fronteira = set(nucleo)
    for k in range(1, aneis + 1):
        nova = set()
        for r in fronteira:
            for n in VIZ[r]:
                if n not in anel and permitido(n): anel[n] = k; nova.add(n)
        fronteira = nova
    return anel, ok
def novos_pesos(alfa, K, aneis, flanco, pmin=0.02):
    anel, ok = selecao(pmin, aneis, flanco)
    sel = sorted(anel); mask = {r: 1.0 - anel[r] / (aneis + 1) for r in sel}
    Wr = {r: W0[r].copy() for r in RAIZ}
    for _ in range(K):
        nw = {}
        for r in sel:
            nb = list(VIZ[r]);
            if not nb: continue
            m = np.mean([Wr[n] for n in nb], axis=0)
            nw[r] = (1 - 0.5) * Wr[r] + 0.5 * m
        for r, w in nw.items(): Wr[r] = w
    W = W0.copy(); mud = {}
    for r in sel:
        lado = "L" if rest[r][0] > 0 else "R"
        w = (1 - alfa * mask[r]) * W0[r] + alfa * mask[r] * Wr[r]
        keep = np.zeros_like(w); idx = [i for i in np.argsort(-w)[:4] if w[i] > 1e-4 and i in ok[lado]]
        keep[idx] = w[idx]; keep /= keep.sum()
        for i in np.nonzero(S == r)[0]: W[i] = keep
        if np.abs(keep - W0[r]).max() > 1e-6: mud[r] = float(np.abs(keep - W0[r]).max())
    return W, sel, mud, anel
# ---------------------------------------------------------------- skinning linear proprio (numpy)
BASIS = np.array([v.co[:] for v in key.key_blocks["Basis"].data])
KL = np.array([v.co[:] for v in key.key_blocks["fold_corrective_L"].data]) - BASIS
KR = np.array([v.co[:] for v in key.key_blocks["fold_corrective_R"].data]) - BASIS
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
CACHE = {}
def estado(nome, f):
    k = (nome, round(f, 2))
    if k not in CACHE:
        usar(nome); scn.frame_set(int(f), subframe=f - int(f))
        Ms = np.stack([MWoi @ MWa @ np.array(pb.matrix) @ MLI[i] @ MWai @ MWo for i, pb in enumerate(arm.pose.bones)])
        CACHE[k] = (Ms, key.key_blocks["fold_corrective_L"].value, key.key_blocks["fold_corrective_R"].value)
    return CACHE[k]
def deformar(W, nome, f):
    Ms, fl, fr = estado(nome, f)
    co = BASIS + fl * KL + fr * KR; co4 = np.c_[co, np.ones(NV)]
    act = np.nonzero(W.sum(0) > 0)[0]
    out = np.zeros((NV, 3))
    for b in act:
        w = W[:, b]; nz = w > 0
        out[nz] += w[nz, None] * (co4[nz] @ Ms[b].T)[:, :3]
    return out @ MWo[:3, :3].T + MWo[:3, 3]
def bari(p, tv, tol=0.02):
    a, b, c = tv; v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14: return False
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    return v >= -tol and w >= -tol and v + w <= 1 + tol
DIRS = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (0, 1) if (x, y, z) != (0, 0, 0)]
def inter_perna(co, detalhe=False):
    P = [Vector(c) for c in co]; bvh = BVHTree.FromPolygons(P, TRIL, all_triangles=True)
    n = nv = 0; dmax = dvis = 0.0; pares = defaultdict(float)
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
        d = 0.0
        for A_, B_ in ((A, B), (B, A)):
            nb = (P[B_[1]] - P[B_[0]]).cross(P[B_[2]] - P[B_[0]])
            if nb.length < 1e-12: continue
            nb.normalize(); tv = [P[i] for i in B_]
            for i in A_:
                dd = (P[i] - tv[0]).dot(nb)
                if dd < 0 and bari(P[i] - nb * dd, tv): d = max(d, -dd)
        if d < 0.003: continue
        n += 1; dmax = max(dmax, d); m = (p1 + p2) / 2; vis = 0
        for dd in DIRS:
            h = bvh.ray_cast(m + dd * 200, -dd)
            if h[0] is not None and (h[0] - m).length < 2e-3: vis = 1; break
        if vis:
            nv += 1; dvis = max(dvis, d); par = "|".join(sorted((OT[a], OT[b]))); pares[par] = max(pares[par], d)
    r = {"reais": n, "visiveis": nv, "prof_max": round(dmax, 3), "prof_vis": round(dvis, 3)}
    if detalhe: r["pares_vis"] = {k: round(v, 3) for k, v in sorted(pares.items(), key=lambda kv: -kv[1])[:8]}
    return r
def quadros(nome, passo):
    f1 = bpy.data.actions[nome].frame_range[1]; return [k * passo for k in range(int(f1 / passo + 1e-6) + 1)]
DESCANSO = ["Deitar", "Deitado", "Levantar"]
OUTROS = ["walk_loop", "Corrida", "VirarEsquerda", "VirarDireita", "takeoff", "Pouso", "Comer", "Morte", "idle_loop", "fly_loop",
          "Planeio", "CurvaAereaEsquerda", "CurvaAereaDireita", "roar", "bite", "FerraoAtaque", "Alerta", "Ameaca", "ReacaoGolpe"]
OUTROS = [n for n in OUTROS if n in bpy.data.actions]
def avaliar(W, clipes, passo, detalhe=False):
    R = {}
    for nome in clipes:
        pior = None; zmin = 9e9; dsl = 0.0
        for f in quadros(nome, passo):
            co = deformar(W, nome, f); r = inter_perna(co, detalhe); zmin = min(zmin, float(co[:, 2].min()))
            if W is not W0:
                dsl = max(dsl, float(np.linalg.norm(co - deformar(W0, nome, f), axis=1).max()))
            r["f"] = round(f, 1)
            if pior is None or (r["prof_vis"], r["visiveis"]) > (pior["prof_vis"], pior["visiveis"]): pior = r
        pior["zmin"] = round(zmin, 3); pior["desloc_max_vs_antes"] = round(dsl, 3); R[nome] = pior
    return R
# conferencia do skinning proprio contra o Blender
usar("Deitado"); scn.frame_set(10); ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
cb = np.array([(obj.matrix_world @ v.co)[:] for v in ev.vertices]); ERR = float(np.abs(cb - deformar(W0, "Deitado", 10)).max())
print("LBS_ERR", ERR, flush=True)
assert ERR < 1e-3
if MODO == "busca":
    base_d = avaliar(W0, DESCANSO, 2.4)
    print("BASE", json.dumps(base_d), flush=True)
    res = {"base": base_d, "cand": {}}
    for alfa, K, aneis, flanco in [(1.0, 4, 2, 0), (1.0, 10, 2, 0), (1.0, 10, 3, 1), (1.0, 20, 3, 1), (0.7, 10, 3, 1)]:
        t0 = time.time(); W, sel, mud, anel = novos_pesos(alfa, K, aneis, flanco)
        rd = avaliar(W, DESCANSO, 2.4)
        tag = "a%.1f_k%d_r%d_f%d" % (alfa, K, aneis, flanco)
        res["cand"][tag] = {"sel_soldados": len(sel), "alterados": len(mud), "descanso": rd}
        print("CAND", tag, "sel", len(sel), "mud", len(mud), json.dumps(rd), round(time.time() - t0), flush=True)
    json.dump(res, open(OUT, "w"), indent=1)
    print("OK")
if MODO in ("aplicar", "efeitos"):
    alfa, K, aneis, flanco = float(argv[3]), int(argv[4]), int(argv[5]), int(argv[6])
    W, sel, mud, anel = novos_pesos(alfa, K, aneis, flanco)
    fora = [i for i in range(NV) if int(S[i]) not in anel]
    dif_fora = float(np.abs(W[fora] - W0[fora]).max()) if fora else 0.0
    infl = int((W > 1e-6).sum(1).max()); norm = float(np.abs(W.sum(1) - 1).max())
    info = {"alfa": alfa, "K": K, "aneis": aneis, "flanco": flanco, "selecao_soldados": len(sel),
            "vertices_alterados_soldados": len(mud), "dif_max_peso": round(max(mud.values(), default=0), 4),
            "dif_max_fora_da_selecao": dif_fora, "influencias_max": infl, "erro_normalizacao_max": norm,
            "por_lado_e_osso": {s: dict(Counter(BONES[int(np.argmax(W0[r]))] for r in mud if (rest[r][0] > 0) == (s == "L"))) for s in "LR"}}
    print("PESOS", json.dumps(info), flush=True)
    if MODO == "efeitos":
        info["descanso"] = avaliar(W, DESCANSO, 1.6, detalhe=True)
        info["outros"] = avaliar(W, OUTROS, 4.0)
        info["outros_antes"] = avaliar(W0, OUTROS, 4.0)
        for k in ("descanso",): print("DESC", json.dumps(info[k]), flush=True)
        for n in OUTROS: print("OUT", n, "antes", json.dumps(info["outros_antes"][n]), "depois", json.dumps(info["outros"][n]), flush=True)
    else:   # grava os pesos numa copia (arquivo de tentativa) para render
        for r in mud:
            for i in np.nonzero(S == r)[0]:
                v = me.vertices[int(i)]
                for g in list(v.groups): obj.vertex_groups[g.group].remove([int(i)])
                for b in np.nonzero(W[int(i)] > 0)[0]: obj.vertex_groups[BONES[b]].add([int(i)], float(W[int(i), b]), "REPLACE")
        bpy.ops.wm.save_as_mainfile(filepath=argv[7], copy=True)
    json.dump(info, open(OUT, "w"), indent=1)
    print("OK")
