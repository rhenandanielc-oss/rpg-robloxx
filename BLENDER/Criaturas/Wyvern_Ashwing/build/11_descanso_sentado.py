# Descanso "sentado sobre os jarretes" (alternativa 1 aprovada pelo usuario em 05/11/2026): SO Deitar / Deitado / Levantar.
# Parte de Wyvern_E7_clipes_L2b.blend (as outras 19 actions ficam intactas) e usa 08_base.py sem alterar.
# Mantem do L2b (09_descanso_v2.py): pes plantados (o corpo recua sobre os pes), perna aberta, angulos interpolados,
# emendas exatas e respiracao que so ergue. Muda: o quadril fica mais ALTO (QUEDA menor) e o peito desce (coluna
# inclinada a frente) ate o peito/barriga dianteira tocar o chao; a perna dobra menos. Como a pose mudou, pescoco/cabeca,
# antebraco, ombro e cauda sao RECALIBRADOS aqui na malha (cabeca apoiada, garra e cauda sem afundar).
# Uso: blender -b Wyvern_E7_clipes_L2b.blend -P 11_descanso_sentado.py -- <08_base.py> <manifesto_L2.json> <saida.blend> <manifesto_saida.json>
#      [busca | KX RECUO JY HX QUEDA HJ [DZ_DEI DZ_LEV]]
import bpy, sys, math, json, itertools
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
CAL = json.load(open(argv[1], encoding="utf-8"))["_calibracao"]["deitado_param_graus"]
OUT, MANI = argv[2], argv[3]; BUSCA = len(argv) > 4 and argv[4] == "busca"
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
I0, FI0 = amostra("idle_loop", 0.0)
T_IDLE = DUR["idle_loop"]
def I(t): return amostra("idle_loop", t)
PARAM = {k: R(v) for k, v in CAL.items()}
LOG = {}
QUEDA = 4.25                     # queda da raiz (v1: 4,25); HJ = jarrete acima da altura da v1; PEITO = coluna a frente
HJ = 0.0; PEITO = 0.0; HX = 0.0                       # HX = jarrete para fora do quadril (canela ao lado da coxa)
def _juntas(M, s): return (ponta(M, "calf_" + s), ponta(M, "foot_" + s), ponta(M, "toe_" + s))   # jarrete, bola, ponta
def _joelho(M, s): return cabeca(M, "calf_" + s)
LEG0 = {s: _juntas(fk(I0, PERNA[s]), s) for s in "LR"}
SX = {s: (1.0 if BD["thigh_" + s].head_local.x > 0 else -1.0) for s in "LR"}
EIXOS = {s: [("thigh_" + s, X), ("thigh_" + s, FRENTE), ("calf_" + s, X), ("foot_" + s, X), ("foot_" + s, FRENTE), ("toe_" + s, X)] for s in "LR"}
# ---------------------------------------------------------------- pose deitada das pernas (parametrizada)
def pernas_deitadas(Pc, kx, dz, jy):
    """IK com a raiz ja baixada/recuada: ponta do dedo FIXA no ponto do idle; bola e jarrete no chao; joelho alto e a kx
    para fora do quadril; jarrete jy atras da bola"""
    res = {}
    for s in "LR":
        tip, ball0 = LEG0[s][2], LEG0[s][1]; Mh = fk(Pc, ["thigh_" + s]); hip = cabeca(Mh, "thigh_" + s)
        alvos = [(lambda M, s=s: ponta(M, "toe_" + s), V((tip.x, tip.y, tip.z + dz[s])), V((1, 1, 1))),
                 (lambda M, s=s: ponta(M, "foot_" + s), V((ball0.x + 0.15 * SX[s], 0, 0.40 + dz[s])), V((0.6, 0, 1))),
                 (lambda M, s=s: ponta(M, "calf_" + s), V((hip.x + HX * SX[s], 0, 0.55 + HJ + dz[s])), V((0.6 if HX else 0, 0, 0.7))),
                 (lambda M, s=s: cabeca(M, "calf_" + s), V((hip.x + kx * SX[s], 0, 1.45 + dz[s])), V((0.6, 0, 0.6))),
                 (lambda M, s=s: ponta(M, "foot_" + s) - ponta(M, "calf_" + s), V((0, -jy, 0)), V((0, 0.5, 0)))]
        res[s] = round(ik_perna(Pc, s, alvos, eixos=EIXOS[s], it=80), 3)
    return res
def raiz_deitada(P, w_z, w_y, recuo):
    mover(P, "root", V((0, recuo * w_y, -QUEDA * w_z)))
def lying_legs(kx, recuo, jy, it=4):
    """calibra os alvos de altura pela malha (pe/dedo 0,04 acima do chao); devolve juntas deitadas no mundo"""
    dz = {"L": 0.0, "R": 0.0}
    for _ in range(it):
        Pc = copia(I0); raiz_deitada(Pc, 1, 1, recuo); res = pernas_deitadas(Pc, kx, dz, jy)
        zr = zmin_reg(Pc, FI0)
        for s in "LR": dz[s] += 0.04 - zr["perna" + s]
    return Pc, {s: _juntas(fk(Pc, PERNA[s]), s) + (_joelho(fk(Pc, PERNA[s]), s),) for s in "LR"}, res, {s: zr["perna" + s] for s in "LR"}
# ---------------------------------------------------------------- resto do corpo deitado (angulos da v1)
def inclinacao_cabeca(P):
    M = fk(P, ["head"]); d = ponta(M, "head") - cabeca(M, "head")
    h = math.hypot(d.x, d.y) * (1.0 if -d.y >= 0 else -1.0)
    return math.degrees(math.atan2(d.z, h))
DIST_PESC = [0.40, 0.28, 0.18, 0.10, 0.04]
def baixar_pescoco(P, A):
    for b, k in zip(PESCOCO, DIST_PESC): girar(P, b, X, A * k)
def corpo_resto(P, w):
    girar(P, "spine_01", X, R(3) * w + PEITO * w)
    for s in "LR":
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P, "shoulder_" + s, Y, -PARAM["asa_" + s] * sx * w)
        girar(P, "forearm_" + s, X, PARAM["ante_" + s] * w)
    for b in CAUDA[:2]: girar(P, b, X, -PARAM["cauda"] * w / 2)
    for i, b in enumerate(CAUDA[3:]): girar(P, b, Z, R(3.5) * w * ESQ)
def deitado_cabeca(P, w):
    baixar_pescoco(P, PARAM["pescoco"] * w)
    girar(P, "head", X, PARAM["cab_dei"] * w)
# ---------------------------------------------------------------- contagem de intersecoes reais envolvendo perna
obj.data.calc_loop_triangles(); TRI = [tuple(t.vertices) for t in obj.data.loop_triangles]
from mathutils.kdtree import KDTree
_rest = [v.co.copy() for v in obj.data.vertices]; _kd = KDTree(len(_rest))
for i, p in enumerate(_rest): _kd.insert(p, i)
_kd.balance(); SOL = {}
for i in range(len(_rest)):
    if i in SOL: continue
    for _, j, _ in _kd.find_range(_rest[i], 1e-3): SOL.setdefault(j, i)
SOLD = [{SOL[i] for i in t} for t in TRI]
from collections import Counter
def osso_tri(t): return Counter(DOM[i] for i in t).most_common(1)[0][0]
OT = [osso_tri(t) for t in TRI]
EPERNA = [o.startswith(("thigh", "calf", "foot", "toe")) for o in OT]
DIRS = [V((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (0, 1) if (x, y, z) != (0, 0, 0)]
def bari_dentro(p, tv, tol=0.02):
    a, b, c = tv; v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14: return False
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    return v >= -tol and w >= -tol and v + w <= 1 + tol
def inter_perna(P, fold):
    co = malha_np(P, fold); Pv = [V(c) for c in co]
    bvh = BVHTree.FromPolygons(Pv, TRI, all_triangles=True); n = 0; nv = 0; dmax = 0.0; dvis = 0.0; casos = []
    for a, b in bvh.overlap(bvh):
        if a >= b or not (EPERNA[a] or EPERNA[b]) or SOLD[a] & SOLD[b]: continue
        A, B = TRI[a], TRI[b]; pts = []
        for X_, Y_ in ((A, B), (B, A)):
            tv = [Pv[i] for i in Y_]
            for u, v in ((X_[0], X_[1]), (X_[1], X_[2]), (X_[2], X_[0])):
                q = intersect_ray_tri(*tv, Pv[v] - Pv[u], Pv[u], True)
                if q is not None and (q - Pv[u]).dot(q - Pv[v]) <= 1e-12: pts.append(q)
        if len(pts) < 2: continue
        p1, p2 = max(itertools.combinations(pts, 2), key=lambda ab: (ab[0] - ab[1]).length)
        if (p1 - p2).length < 0.01: continue
        def prof(A_, B_):
            nb = (Pv[B_[1]] - Pv[B_[0]]).cross(Pv[B_[2]] - Pv[B_[0]])
            if nb.length < 1e-12: return 0.0
            nb.normalize(); d_ = 0.0; tv = [Pv[i] for i in B_]
            for i in A_:
                d = (Pv[i] - tv[0]).dot(nb)
                if d < 0 and bari_dentro(Pv[i] - nb * d, tv): d_ = max(d_, -d)
            return d_
        d = max(prof(A, B), prof(B, A))
        if d < 0.003: continue
        m = (p1 + p2) / 2; vis = 0
        for dd in DIRS:
            h = bvh.ray_cast(m + dd * 200, -dd)
            if h[0] is not None and (h[0] - m).length < 2e-3: vis += 1
        n += 1; dmax = max(dmax, d)
        if vis: nv += 1; dvis = max(dvis, d); casos.append((round(d, 3), "|".join(sorted((OT[a], OT[b]))), [round(x, 2) for x in m]))
    return {"reais": n, "visiveis": nv, "prof_max": round(dmax, 3), "prof_max_visivel": round(dvis, 3), "piores_visiveis": sorted(casos, reverse=True)[:5]}
FRENTE_CORPO = ["spine_02", "spine_03"]
PEITO_FIXO = None                        # None = peito desce ate o chao; numero = inclinacao fixa (barriga pode ficar no ar)
def corrigir_cabeca(P, alvo):
    tot = 0.0
    for _ in range(4):
        d = R(inclinacao_cabeca(P) - alvo); girar(P, "head", X, d); tot += d
    return tot
def calibrar_corpo(Pleg):
    """com as pernas ja na pose sentada: peito ate o chao, cauda, pescoco/cabeca e asas, nessa ordem (malha)"""
    global PEITO
    for k in ("asa_L", "asa_R", "ante_L", "ante_R", "pescoco", "cab_dei", "cauda"): PARAM[k] = 0.0
    PEITO = 0.0
    def pose(wcab=1.0):
        Pt = copia(Pleg); corpo_resto(Pt, 1.0); deitado_cabeca(Pt, wcab); return Pt
    def zfr(a):
        global PEITO
        PEITO = a; return zmin_ossos(pose(0.0), FI0, FRENTE_CORPO)
    PEITO = PEITO_FIXO if PEITO_FIXO is not None else bissecao(zfr, R(-10), R(30), 0.06); zfr(PEITO)
    def zcau(a):
        PARAM["cauda"] = a; return zmin_reg(pose(0.0), FI0)["cauda"]
    PARAM["cauda"] = bissecao(zcau, R(-15), R(12), 0.12)
    def zcab(a):
        PARAM["pescoco"] = a; PARAM["cab_dei"] = 0.0; Pt = pose(1.0)
        PARAM["cab_dei"] = corrigir_cabeca(Pt, -8.0)
        return zmin_reg(pose(1.0), FI0)["cabeca"]
    PARAM["pescoco"] = bissecao(lambda a: -zcab(a), 0.0, R(130), -0.22); zcab(PARAM["pescoco"])
    for s in "LR":
        def zante(a, s=s):
            PARAM["ante_" + s] = a; return zmin_reg(pose(1.0), FI0)["asa" + s]
        def zasa(a, s=s):
            PARAM["asa_" + s] = a; return zmin_reg(pose(1.0), FI0)["asa" + s]
        PARAM["ante_" + s] = bissecao(zante, 0.0, R(-40), 0.14, it=14) if zante(0.0) < 0.14 else 0.0; zante(PARAM["ante_" + s])
        PARAM["asa_" + s] = bissecao(lambda a: -zasa(a), 0.0, R(30), -0.05, it=14) if zasa(0.0) < 0.05 else 0.0; zasa(PARAM["asa_" + s])
    Pd = pose(1.0)
    return Pd, {"PEITO": round(math.degrees(PEITO), 2), **{k: round(math.degrees(v), 2) for k, v in PARAM.items()}}, zmin_reg(Pd, FI0)
def pose_deitada(kx, recuo, jy):
    Pc, LD, res, zr = lying_legs(kx, recuo, jy)
    Pd, cal, zr_corpo = calibrar_corpo(Pc)
    return Pd, LD, res, zr, cal, zr_corpo
if BUSCA:
    print("BASE_IDLE", inter_perna(copia(I0), FI0), flush=True)
    for q, pe, kx, hx in itertools.product((3.6, 3.2), (0.0, 8.0), (1.5, 2.4), (1.4, 3.2)):
        QUEDA, HX, HJ, PEITO_FIXO = q, hx, 0.0, R(pe)
        Pc, LD, res, zr, cal, zc = pose_deitada(kx, 2.6, 2.0)
        ip = inter_perna(Pc, FI0); pv = ip.pop("piores_visiveis")
        print("BUSCA2 q=%.2f peito=%d kx=%.1f hx=%.1f" % (q, pe, kx, hx), "zmin", {k: float(v) for k, v in zc.items()}, ip, pv[:2], flush=True)
    raise SystemExit
# ---------------------------------------------------------------- escolha (da busca, ver LEIA-ME) e clipes
_a = [float(x) for x in argv[4:10]] if len(argv) > 9 else [1.5, 2.6, 2.0, 2.8, 3.2, 0.0]   # escolha: ver LEIA-ME
KX, RECUO, JY, HX, QUEDA, HJ = _a
PEITO_FIXO = None if len(argv) <= 12 or argv[12] == "auto" else R(float(argv[12]))
PDEIT, LEGD, RES_IK, ZR, CALC, ZCORPO = pose_deitada(KX, RECUO, JY)
LOG.update({"KX": KX, "RECUO": RECUO, "JY": JY, "HX": HX, "QUEDA": QUEDA, "HJ": HJ, "calibracao_corpo_graus": CALC, "zmin_regioes": ZCORPO,
            "ik_res": RES_IK, "zmin_perna": ZR, "inter_perna_deitado": inter_perna(PDEIT, FI0),
            "juntas_deitado": {s: [[round(x, 2) for x in j] for j in LEGD[s]] for s in "LR"}})
LEGQ = {b: PDEIT[b] for s in "LR" for b in PERNA[s]}               # rotacoes da perna na pose deitada calibrada
def pernas_transicao(P, wz):
    """interpola os ANGULOS da perna (em pe -> deitada, dobra natural, joelho nao atravessa o corpo) e corrige so o
    necessario por IK: ponta do dedo plantada (no chao do idle ate a deitada) e bola de leve. Em wz = 1: pose calibrada"""
    for s in "LR":
        for b in PERNA[s]:
            l, q, e = P[b]; ld, qd, ed = LEGQ[b]
            if q.dot(qd) < 0: qd = -qd
            P[b] = (l.lerp(ld, wz), q.slerp(qd, wz), e.lerp(ed, wz))
        alvos = [(lambda M, s=s: ponta(M, "toe_" + s), LEG0[s][2].lerp(LEGD[s][2], wz), 1.0),
                 (lambda M, s=s: ponta(M, "foot_" + s), LEG0[s][1].lerp(LEGD[s][1], wz), 0.15)]
        ik_perna(P, s, alvos, eixos=EIXOS[s], it=30)
def corpo(P, wz, wy, wr, wn):
    raiz_deitada(P, wz, wy, RECUO); pernas_transicao(P, wz); corpo_resto(P, wr); deitado_cabeca(P, wn)
T_DEI, T_DLOOP, T_LEV = 2.4, 4.0, 2.0
DZ_DEI = float(argv[10]) if len(argv) > 10 else 0.3; DZ_LEV = float(argv[11]) if len(argv) > 11 else 0.3
def respirar(P, t, T):
    """inspira = dorso e cabeca SOBEM (nunca descem abaixo da pose calibrada); vale zero em t = 0 e fecha o laco em T"""
    u = 2 * math.pi * t / T
    sobe = (1 - math.cos(u)) / 2                                  # 0 -> 1 -> 0
    girar(P, "spine_02", X, -R(0.9) * sobe); girar(P, "spine_03", X, -R(0.5) * sobe)
    girar(P, "head", X, -R(0.6) * sobe)
    for i, b in enumerate(CAUDA[6:]): girar(P, b, Z, R(1.0) * (math.sin(u - 0.5 * i) - math.sin(-0.5 * i)))
def c_deitar(t):
    wy = suave(t / 1.6)                        # recua sobre os pes (senta para tras)...
    wz = suave((t - DZ_DEI) / 1.75)            # ...e desce junto, um pouco atras: a perna nao comprime
    wr = suave(t / 1.9); wn = suave((t - 0.6) / 1.7)
    Pi, fi = I(t); P = misturar(Pi, I0, wr); fold = fi * (1 - wr) + FI0 * wr
    corpo(P, wz, wy, wr, wn)
    return P, fold
def c_deitado(t):
    P = copia(I0); corpo(P, 1, 1, 1, 1); respirar(P, t, T_DLOOP)
    return P, FI0
def c_levantar(t):
    wn = 1 - suave(t / 0.8)                    # cabeca sobe primeiro
    wz = 1 - suave((t - 0.30) / 1.35)          # empurra para cima...
    wy = 1 - suave((t - 0.30 - DZ_LEV) / 1.35) # ...e passa o peso a frente sobre os pes, um pouco depois
    wr = 1 - suave((t - 0.3) / 1.5)
    Pi, fi = I((t - T_LEV) % T_IDLE)           # termina exatamente no quadro 0 do idle
    P = misturar(Pi, I0, wr); fold = fi * (1 - wr) + FI0 * wr
    corpo(P, wz, wy, wr, wn)
    return P, fold
CLIPES = {"Deitar": (c_deitar, T_DEI, False), "Deitado": (c_deitado, T_DLOOP, True), "Levantar": (c_levantar, T_LEV, False)}
mani = {"_fonte": "Wyvern_E7_clipes_L2b.blend; so Deitar/Deitado/Levantar regravados (11_descanso_sentado.py)", "_hz": HZ, "_calibracao": LOG}
print("CALIB", json.dumps(LOG, default=str), flush=True)
for nome, (fn, dur, loop) in CLIPES.items():
    mani[nome] = gravar_clipe(nome, fn, dur, loop); print("CLIPE", nome, mani[nome], flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
print("OK")
