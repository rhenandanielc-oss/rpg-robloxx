# Lote 1 de clipes da Wyvern (locomocao e voo), derivados dos 6 clipes do proprio Ashwing (mesmo estilo/rig) com
# camadas procedurais. Clipes visuais: velocidades/angulos sao PROPOSTA, nao definem mecanicas do jogo.
#   Corrida              walk_loop acelerado e ampliado (desvio da pose media x1,35), corpo inclinado a frente, loop
#   VirarEsquerda/Direita walk_loop com o corpo em arco (coluna/pescoco/cabeca/cauda) e inclinacao para dentro, loop
#   Planeio              pose de asa mais aberta do fly_loop sustentada, oscilacao lenta de asa/cauda/pescoco, loop
#   CurvaAereaE/D        Planeio com rolagem para dentro, cabeca na curva e cauda como leme, loop
#   Pouso                takeoff invertido (desce com deslocamento de raiz) + asas: batidas do fly_loop perdendo
#                        amplitude ate a frenagem (flare) no toque; depois o recolhimento invertido do takeoff e o idle
# Chaves a 30 Hz (como os clipes originais: 0,8 quadro em cena de 24 fps); shape keys fold_corrective no slot KEY.
# Uso: blender -b Wyvern_E6.blend -P 07_clipes_lote1.py -- <saida.blend> <manifesto.json>
import bpy, sys, math, json
from mathutils import Vector as V, Quaternion as Q, Matrix
from bpy_extras import anim_utils
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, MANI = argv[0], argv[1]
sc = bpy.context.scene; FPS_CENA = sc.render.fps; HZ = 30
arm = bpy.data.objects["Wyvern_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
key = bpy.data.objects["Wyvern"].data.shape_keys
R = math.radians
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
# ---------------------------------------------------------------- leitura das acoes originais (fcurves avaliadas)
def curvas(act):
    m = {}
    for L in act.layers:
        for s in L.strips:
            for cb in s.channelbags:
                for f in cb.fcurves: m[(f.data_path, f.array_index)] = f
    return m
FONTE = {n: curvas(bpy.data.actions[n]) for n in ("idle_loop", "walk_loop", "fly_loop", "takeoff", "roar", "bite")}
DUR = {n: bpy.data.actions[n].frame_range[1] / FPS_CENA for n in FONTE}
OSSOS = [b.name for b in BD]
def amostra(clipe, t, loop=True):
    """pose do clipe original no tempo t (s): {osso: (loc, quat, esc)}, fold"""
    T = DUR[clipe]; t = (t % T) if loop else min(max(t, 0.0), T); fr = t * FPS_CENA; m = FONTE[clipe]; P = {}
    for b in OSSOS:
        pb = 'pose.bones["%s"].' % b
        loc = V([m[(pb + "location", i)].evaluate(fr) if (pb + "location", i) in m else 0.0 for i in range(3)])
        q = Q([m[(pb + "rotation_quaternion", i)].evaluate(fr) if (pb + "rotation_quaternion", i) in m else (1.0 if i == 0 else 0.0) for i in range(4)])
        esc = V([m[(pb + "scale", i)].evaluate(fr) if (pb + "scale", i) in m else 1.0 for i in range(3)])
        P[b] = (loc, q.normalized(), esc)
    fk = 'key_blocks["fold_corrective_L"].value'
    fold = m[(fk, 0)].evaluate(fr) if (fk, 0) in m else 0.0
    return P, fold
def misturar(A, B, w):
    return {b: (A[b][0].lerp(B[b][0], w), A[b][1].slerp(B[b][1], w) if A[b][1].dot(B[b][1]) >= 0 else A[b][1].slerp(-B[b][1], w), A[b][2].lerp(B[b][2], w)) for b in A}
def rot_mundo(osso, eixo, ang):
    """rotacao em eixo do MUNDO (repouso) convertida para o espaco local do osso"""
    r = BD[osso].matrix_local.to_3x3()
    return (r.inverted() @ Matrix.Rotation(ang, 3, eixo) @ r).to_quaternion()
def mover(P, osso, desl):
    """desloca o osso por um vetor no MUNDO (a pose.location e no espaco local do osso; o Z local da raiz nao e o Z do mundo)"""
    l, q, e = P[osso]; P[osso] = (l + BD[osso].matrix_local.to_3x3().inverted() @ desl, q, e)
def girar(P, osso, eixo, ang):
    l, q, e = P[osso]; P[osso] = (l, rot_mundo(osso, eixo, ang) @ q, e)
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
FRENTE = -Y                                   # a cabeca esta em -Y
ESQ = 1.0 if BD["upperarm_L"].head_local.x > 0 else -1.0   # lado L em +X ?
ASA = {s: [b for b in OSSOS if b.endswith("_" + s) and any(k in b for k in ("shoulder", "upperarm", "forearm", "hand", "finger", "strut", "thumb"))] for s in "LR"}
PERNA = [b for b in OSSOS if any(b.startswith(k) for k in ("thigh", "calf", "foot", "toe"))]
COLUNA = ["spine_01", "spine_02", "spine_03"]; PESCOCO = ["neck_01", "neck_02", "neck_03", "neck_04", "neck_05"]
CAUDA = ["tail_%02d" % i for i in range(1, 11)]
# pose media de um ciclo (para ampliar o desvio em torno dela)
def media(clipe, n=32):
    acc = {b: [V(), Q((0, 0, 0, 0)), V()] for b in OSSOS}
    for k in range(n):
        P, _ = amostra(clipe, DUR[clipe] * k / n)
        for b in OSSOS:
            l, q, e = P[b]; a = acc[b]; a[0] += l / n; a[2] += e / n
            if a[1].dot(q) < 0: q = -q
            a[1] = Q([a[1][i] + q[i] / n for i in range(4)])
    return {b: (a[0], a[1].normalized(), a[2]) for b, a in acc.items()}
MED_WALK = media("walk_loop")
def ampliar(P, M, k, ossos):
    for b in ossos:
        l, q, e = P[b]; lm, qm, em = M[b]
        if qm.dot(q) < 0: q = -q
        d = qm.inverted() @ q; ang = d.angle; ax = d.axis
        P[b] = (lm + (l - lm) * k, qm @ Q(ax, ang * k) if ang > 1e-6 else q, e)
# ---------------------------------------------------------------- clipes
T_CORR = 0.72
# o balanco da perna no walk do Ashwing ocupa ~40% do ciclo (medido: amostras 19-31 de 32 na perna L), mas com
# ritmo irregular: pausa de ~4 graus/amostra e depois 66 e 54 graus/amostra. Acelerado por igual isso vira saltos
# > 100 graus. Na corrida cada perna tem o proprio mapa de fase: no balanco o tempo e reparametrizado pela
# distancia angular percorrida (thigh+calf+foot), 70% uniforme; o apoio segue em tempo linear.
BAL = {"L": (0.59, 0.41), "R": (0.09, 0.41)}                              # (inicio, duracao) do balanco, fracao do ciclo
def _acumulado(lado, n=256):
    a, Ls = BAL[lado]; ac = [0.0]
    for k in range(n):
        s1 = (a + Ls * k / n) * DUR["walk_loop"]; s2 = (a + Ls * (k + 1) / n) * DUR["walk_loop"]
        P1_, P2_ = amostra("walk_loop", s1)[0], amostra("walk_loop", s2)[0]
        ac.append(ac[-1] + sum(math.degrees(P1_[b + lado][1].rotation_difference(P2_[b + lado][1]).angle) for b in ("thigh_", "calf_", "foot_")))
    return [c / ac[-1] for c in ac]
ACUM = {l: _acumulado(l) for l in "LR"}
def fase_perna(u, lado):
    a, Ls = BAL[lado]; x = (u - a) % 1.0
    if x >= Ls: return u % 1.0                                            # apoio: tempo linear
    alvo = x / Ls; ac = ACUM[lado]; n = len(ac) - 1                       # fracao de distancia angular desejada
    k = next((i for i in range(n) if ac[i + 1] >= alvo), n - 1)
    f = (alvo - ac[k]) / max(ac[k + 1] - ac[k], 1e-9); unif = (k + f) / n
    return (a + Ls * (0.3 * (x / Ls) + 0.7 * unif)) % 1.0
def c_corrida(t):
    u = t / T_CORR
    P, fold = amostra("walk_loop", u * DUR["walk_loop"])
    for lado in "LR":
        PL, _ = amostra("walk_loop", fase_perna(u, lado) * DUR["walk_loop"])
        for b in ("thigh_", "calf_", "foot_", "toe_"): P[b + lado] = PL[b + lado]
    ampliar(P, MED_WALK, 1.15, PERNA + ["pelvis", "root"] + COLUNA)
    girar(P, "spine_01", X, R(4)); girar(P, "pelvis", X, R(5))             # corpo inclinado a frente (+X = nariz para baixo)
    for i, b in enumerate(PESCOCO): girar(P, b, X, R(2.5))                  # pescoco esticado a frente
    girar(P, "head", X, R(-6))
    mover(P, "root", V((0, 0, 0.10 + 0.12 * math.sin(4 * math.pi * u))))   # quique 2x por ciclo; +0,10: dedo apoiado na altura do walk
    for i, b in enumerate(CAUDA):                                         # cauda reta com onda atrasada
        girar(P, b, Z, R(1.6) * math.sin(2 * math.pi * (u - 0.08 * i)))
    return P, fold
T_VIR = DUR["walk_loop"]
def c_virar(sinal):
    def f(t):
        P, fold = amostra("walk_loop", t)
        s = sinal * ESQ                                                   # + = para a esquerda da criatura
        for b, a in zip(COLUNA, (3, 4, 4)): girar(P, b, Z, R(a) * s)
        for b in PESCOCO: girar(P, b, Z, R(4) * s)
        girar(P, "head", Z, R(6) * s)
        for i, b in enumerate(CAUDA): girar(P, b, Z, R(-2.2) * s)         # corpo inteiro em arco (C): cauda curva para o mesmo lado
        girar(P, "spine_01", Y, R(5) * s)                                 # tronco inclina para dentro (raiz/pernas nao: o pe nao afunda)
        return P, fold
    return f
# planeio: quadro do fly_loop com as asas HORIZONTAIS e abertas: maior envergadura com as pontas na altura do ombro
# (o criterio antigo pegava o fim da subida, asas em V)
def envergadura(t):
    P, _ = amostra("fly_loop", t)
    for b in OSSOS:
        l, q, e = P[b]; PB[b].location = l; PB[b].rotation_quaternion = q; PB[b].scale = e
    bpy.context.view_layer.update()
    pl = arm.matrix_world @ PB["strut_b_02_L"].tail; pr = arm.matrix_world @ PB["strut_b_02_R"].tail
    om = (arm.matrix_world @ PB["upperarm_L"].head + arm.matrix_world @ PB["upperarm_R"].head) / 2
    return (pl - pr).length - 2.0 * (abs(pl.z - om.z) + abs(pr.z - om.z)) / 2
for pb in PB: pb.rotation_mode = "QUATERNION"
cand = [(envergadura(DUR["fly_loop"] * k / 96), DUR["fly_loop"] * k / 96) for k in range(96)]
T_PLANA_SRC = max(cand)[1]
BASE_PLANA, _ = amostra("fly_loop", T_PLANA_SRC)
T_PLAN = 2.4
def c_planeio(t, roll=0.0):
    P = {b: (l.copy(), q.copy(), e.copy()) for b, (l, q, e) in BASE_PLANA.items()}
    u = t / T_PLAN; w = math.sin(2 * math.pi * u)
    for s, sg in (("L", 1), ("R", -1)):
        girar(P, "upperarm_" + s, FRENTE, R(2.0) * w * sg * ESQ)          # asas sobem/descem de leve (ar)
        for b in ("strut_a_02_", "strut_b_02_", "strut_c_02_", "strut_d_02_"): girar(P, b + s, FRENTE, R(1.5) * math.sin(2 * math.pi * (u - 0.1)) * sg * ESQ)
    for i, b in enumerate(CAUDA): girar(P, b, Z, R(1.2) * math.sin(2 * math.pi * (u - 0.07 * i)))
    for b in PESCOCO: girar(P, b, X, R(0.8) * math.sin(2 * math.pi * (u + 0.25)))
    mover(P, "root", V((0, 0, 0.25 * w)))
    return P, 0.0
def c_curva(sinal):
    def f(t):
        P, fold = c_planeio(t)
        s = sinal * ESQ; ent = 1.0
        girar(P, "root", Y, R(24) * s * ent)                              # rolagem para dentro da curva
        for b in PESCOCO: girar(P, b, Z, R(3) * s)
        girar(P, "head", Z, R(5) * s); girar(P, "head", Y, R(-10) * s)     # cabeca nivelada olhando a curva
        for i, b in enumerate(CAUDA): girar(P, b, Z, R(-2.5) * s)         # cauda como leme, seguindo o arco
        girar(P, "upperarm_" + ("L" if s * ESQ > 0 else "R"), FRENTE, R(-4) * (1 if s * ESQ > 0 else -1) * ESQ)  # asa de dentro um pouco baixa
        return P, fold
    return f
# pouso: takeoff invertido; detecta o quadro em que os pes deixam o chao no takeoff
def pes_z(t):
    P, _ = amostra("takeoff", t, loop=False)
    for b in OSSOS:
        l, q, e = P[b]; PB[b].location = l; PB[b].rotation_quaternion = q; PB[b].scale = e
    bpy.context.view_layer.update()
    return min((arm.matrix_world @ PB[p].tail).z for p in ("toe_L", "toe_R"))
T_TK = DUR["takeoff"]; z0 = pes_z(0.0)
T_SOLTA = next(T_TK * k / 120 for k in range(120) if pes_z(T_TK * k / 120) > z0 + 0.6)
FLARE = {b: (l.copy(), q.copy(), e.copy()) for b, (l, q, e) in BASE_PLANA.items()}
for s in "LR":   # asas para cima e para a frente (freio): erguer = rot. em Y, avancar = rot. em Z, sinal pelo lado
    sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
    girar(FLARE, "shoulder_" + s, Y, R(-12) * sx); girar(FLARE, "shoulder_" + s, Z, R(-18) * sx)
ACEL = 1.15                                                               # pouso um pouco mais rapido que o takeoff
T_POU = T_TK / ACEL + 0.45
T_TOQUE = (T_TK - T_SOLTA) / ACEL                                         # instante do toque no chao (s)
I0, FI0 = amostra("idle_loop", 0.0)
def c_pouso(t):
    ts = max(T_TK - t * ACEL, 0.0)                                        # tempo no takeoff (invertido)
    P, fold = amostra("takeoff", ts, loop=False)
    if t < T_TOQUE:                                                       # no ar: batidas do fly_loop perdendo amplitude -> flare
        k = suave(t / T_TOQUE)
        V_, _ = amostra("fly_loop", t * 1.1)
        asa_ar = misturar(V_, FLARE, k)
        for b in ASA["L"] + ASA["R"]: P[b] = asa_ar[b]
        girar(P, "root", X, R(-6) * k)                                    # empina pouco no flare (-X = nariz para cima)
    else:                                                                 # depois do toque: flare -> asas dobradas do idle
        k = suave((t - T_TOQUE) / 0.9)
        for b in ASA["L"] + ASA["R"]: P[b] = misturar({b: FLARE[b]}, {b: I0[b]}, k)[b]
        girar(P, "root", X, R(-6) * (1 - suave((t - T_TOQUE) / 0.4)))
        fold = FI0 * k                                                    # correctives acompanham o recolhimento
    if t < T_TOQUE: fold = 0.0
    lev = suave((t - (T_TOQUE - 0.7)) / 0.4) * (1 - suave((t - (T_TOQUE + 0.3)) / 0.5))
    for b in CAUDA[:6]: girar(P, b, X, R(2.5) * lev)                      # cauda erguida no toque (nao bate no chao)
    if t > T_POU - 0.6:                                                   # assenta na pose do idle
        w = suave((t - (T_POU - 0.6)) / 0.6)
        P = misturar(P, I0, w); fold = fold * (1 - w) + FI0 * w
    return P, fold
CLIPES = {  # nome: (funcao, duracao, loop)
    "Corrida": (c_corrida, T_CORR, True),
    "VirarEsquerda": (c_virar(+1), T_VIR, True), "VirarDireita": (c_virar(-1), T_VIR, True),
    "Planeio": (c_planeio, T_PLAN, True),
    "CurvaAereaEsquerda": (c_curva(+1), T_PLAN, True), "CurvaAereaDireita": (c_curva(-1), T_PLAN, True),
    "Pouso": (c_pouso, T_POU, False),
}
# ---------------------------------------------------------------- gravacao (acao com slot OBJECT + slot KEY, 30 Hz)
mani = {"_balanco_walk_fase_frac": {l: [round(a, 3), round(b, 3)] for l, (a, b) in BAL.items()}, "_fonte": "Wyvern_E6.blend (6 clipes do Ashwing)", "_hz": HZ, "_lado_L_em_X": ESQ,
        "_planeio_quadro_fly_s": round(T_PLANA_SRC, 3), "_pouso_toque_s": round(T_TOQUE, 3)}
for nome, (fn, dur, loop) in CLIPES.items():
    n = int(round(dur * HZ)) + 1
    ts = [dur * k / (n - 1) for k in range(n)]
    poses = [fn(t) for t in ts]
    if loop:                                                              # fecha o laco: ultimo quadro = primeiro
        poses[-1] = poses[0]
    if nome in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[nome])
    act = bpy.data.actions.new(nome); act.use_fake_user = True
    so = act.slots.new(id_type="OBJECT", name=arm.name); sk = act.slots.new(id_type="KEY", name=key.name)
    cbo = anim_utils.action_ensure_channelbag_for_slot(act, so); cbk = anim_utils.action_ensure_channelbag_for_slot(act, sk)
    frs = [t * FPS_CENA for t in ts]
    def gravar(cb, path, idx, vals, grupo=None):
        fc = cb.fcurves.new(path, index=idx, group_name=grupo) if grupo else cb.fcurves.new(path, index=idx)
        fc.keyframe_points.add(len(vals)); co = []
        for f, v in zip(frs, vals): co += [f, v]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
        fc.update()
    for b in OSSOS:
        pb = 'pose.bones["%s"].' % b; prev = None; qs = []
        for P, _ in poses:                                                # continuidade de sinal dos quaternions
            q = P[b][1]
            if prev is not None and prev.dot(q) < 0: q = -q
            qs.append(q); prev = q
        for i in range(3): gravar(cbo, pb + "location", i, [P[b][0][i] for P, _ in poses], b)
        for i in range(4): gravar(cbo, pb + "rotation_quaternion", i, [q[i] for q in qs], b)
        for i in range(3): gravar(cbo, pb + "scale", i, [P[b][2][i] for P, _ in poses], b)
    for lado in "LR": gravar(cbk, 'key_blocks["fold_corrective_%s"].value' % lado, 0, [f for _, f in poses])
    act["loop"] = loop
    mani[nome] = {"duracao_s": round(dur, 3), "loop": loop, "amostras": n, "quadros_cena": round(dur * FPS_CENA, 2)}
    print("CLIPE", nome, mani[nome], flush=True)
for pb in PB: pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.scale = (1, 1, 1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w"), indent=1, ensure_ascii=False)
print("OK")
