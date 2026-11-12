# Lote 5 de clipes da Wyvern: realismo / vida parada (pedido do usuario em 12/11/2026), sobre Wyvern_E7_clipes_L4.blend
# (preservado). So ACRESCENTA actions. Clipes visuais: angulos e tempos sao PROPOSTA (nada de regra de jogo).
#   SacudirCorpo        3 s  sacode como cao molhado: onda cabeca -> tronco -> cauda, asas tremem por ultimo
#   AlisarAsaEsquerda   6 s  estende meio a asa E e passa o focinho na membrana (mordiscadas), volta ao idle
#   AlisarAsaDireita    6 s  espelho
#   Espreguicar         6 s  abre as asas devagar, alonga o pescoco a frente, arqueia, cauda sobe, boceja
#   Farejar             6 s  abaixa o focinho ate perto do chao e cheira em 3 pontos (pausas + fungadas)
#   OlharVolta          6 s  corpo parado; so pescoco/cabeca viram a E, pausa (inclina a cabeca), a D, volta
#   DecolagemPenhasco   2,4 s agacha na borda, lanca-se de bico para baixo, abre as asas e termina no quadro 0 do Planeio
# Todos (menos a decolagem) comecam e terminam EXATAMENTE no quadro 0 do idle (duracao multipla do idle de 3 s).
# Pescoco/cabeca guiados por IK numerico do focinho (breath_socket) com regularizacao (curva distribuida).
# Clipes no lugar (como os de voo): a queda/deslocamento da decolagem e do jogo.
# Uso: blender -b Wyvern_E7_clipes_L4.blend -P 19_clipes_lote5.py -- <08_base.py> <saida.blend> <manifesto.json> [clipes]
import bpy, sys, math, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
FONTE["Planeio"] = curvas(bpy.data.actions["Planeio"]); DUR["Planeio"] = bpy.data.actions["Planeio"].frame_range[1] / FPS_CENA
I0, FI0 = amostra("idle_loop", 0.0)
T_IDLE = DUR["idle_loop"]; T_FLY = DUR["fly_loop"]; T_PLA = DUR["Planeio"]
def I(t): return amostra("idle_loop", t % T_IDLE)
ASAS = ASA["L"] + ASA["R"]
LOG = {}
def sx_(s): return 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
def env(t, a, b, c, d):
    """0 ate a, sobe ate b, 1 ate c, desce ate d"""
    return suave((t - a) / max(b - a, 1e-6)) * (1 - suave((t - c) / max(d - c, 1e-6)))
# ---------------------------------------------------------------- agachar com pe identico ao idle (lote 3 / Comer)
LEG0 = {s: ponta(fk(I0, PERNA[s]), "calf_" + s) for s in "LR"}
FK0 = fk(I0)
def agachar(P, q):
    if q <= 1e-4: return
    mover(P, "root", V((0, 0, -q)))
    for s in "LR":
        ik_perna(P, s, [(lambda M, s=s: ponta(M, "calf_" + s), LEG0[s], 1.0)],
                 eixos=[("thigh_" + s, X), ("thigh_" + s, FRENTE), ("calf_" + s, X)], it=60)
        Mc = fk(P, ["calf_" + s])["calf_" + s]
        q_ = ((Mc @ REL["foot_" + s]).to_3x3().inverted() @ FK0["foot_" + s].to_3x3()).to_quaternion()
        l, _, e = P["foot_" + s]; P["foot_" + s] = (l, q_, e)
        P["toe_" + s] = tuple(x.copy() for x in I0["toe_" + s])
def inclinar(P, graus):
    """+ = nariz para baixo; pivo na pelve"""
    p0 = cabeca(fk(P, ["pelvis"]), "pelvis"); girar(P, "root", X, R(graus)); mover(P, "root", p0 - cabeca(fk(P, ["pelvis"]), "pelvis"))
# ---------------------------------------------------------------- asa aberta (pose do fly_loop com maior envergadura)
def pose_asa_aberta():
    best = None
    for k in range(96):
        tt = T_FLY * k / 96; Pf, _ = amostra("fly_loop", tt); M = fk(Pf)
        pl, pr = ponta(M, "strut_b_02_L"), ponta(M, "strut_b_02_R")
        om = (cabeca(M, "upperarm_L") + cabeca(M, "upperarm_R")) / 2
        sc_ = (pl - pr).length - (abs(pl.z - om.z) + abs(pr.z - om.z))
        if best is None or sc_ > best[0]: best = (sc_, tt)
    return amostra("fly_loop", best[1])[0]
ASA_ABERTA = pose_asa_aberta()
# ---------------------------------------------------------------- IK do focinho (pescoco/cabeca), partida a quente
FOC = "breath_socket"
def ik_geral(P0, params, alvos, reg, x0=None, it=25):
    """params: MODOS = [[(osso, eixo_mundo, peso), ...], ...] (um angulo por modo, distribuido pelos ossos com o peso:
    curva unica e suave, sem zigue-zague); alvos: [(fn(M)->V, alvo V, peso)]; reg: regularizacao por modo.
    Resolve os angulos totais (a partir de P0) por Gauss-Newton amortecido. Devolve (P, x, erro)."""
    n = len(params); x = np.array(x0 if x0 is not None else np.zeros(n), dtype=float)
    ossos_fk = sorted({FOC, "head", "jaw"} | {b for modo in params for b, ax, k in modo})
    def pose(xv):
        Pp = dict(P0)
        for modo, a in zip(params, xv):
            for b, ax, k in modo: girar(Pp, b, ax, float(a) * k)
        return Pp
    def resid(xv):
        M = fk(pose(xv), ossos_fk); r = []
        for f, alvo, w in alvos:
            d = f(M) - alvo; r += [d.x * w, d.y * w, d.z * w]
        return np.concatenate([np.array(r), np.asarray(reg) * xv])
    for _ in range(it):
        r0 = resid(x)
        J = np.zeros((len(r0), n)); h = 1e-4
        for j in range(n):
            xx = x.copy(); xx[j] += h; J[:, j] = (resid(xx) - r0) / h
        dx = np.linalg.solve(J.T @ J + 1e-3 * np.eye(n), -J.T @ r0)
        dx = np.clip(dx, -0.15, 0.15); x = x + dx
        if np.abs(dx).max() < 1e-5: break
    P = pose(x); M = fk(P, ossos_fk)
    err = max((f(M) - alvo).length for f, alvo, w in alvos)
    return P, x, err
KP = (0.16, 0.2, 0.22, 0.22, 0.2)                                   # distribuicao ao longo do pescoco (soma ~1)
PESC_XZ = [[("spine_03", X, 1.0)],                                  # peito
           [(b, X, k) for b, k in zip(PESCOCO, KP)],                # curvar o pescoco (frente/tras)
           [(b, X, k) for b, k in zip(PESCOCO, (0.35, 0.3, 0.15, -0.1, -0.3))],   # curva em S (base x ponta)
           [(b, Z, k) for b, k in zip(PESCOCO, KP)] + [("spine_03", Z, 0.15)],    # virar
           [("head", X, 1.0)], [("head", Z, 1.0)]]                  # cabeca
REG_XZ = [0.8, 0.05, 0.25, 0.05, 0.3, 0.4]
ESTADO = {}
def ik_focinho(chave, P, alvos, params=PESC_XZ, reg=REG_XZ):
    P2, x, err = ik_geral(P, params, alvos, reg, ESTADO.get(chave))
    xa = ESTADO.get(chave)
    if xa is not None:
        d = float(np.abs(x - xa).max()); k = "salto_ik_" + chave
        if math.degrees(d) > LOG.get(k, [0])[0]: LOG[k] = [round(math.degrees(d), 2), int(np.abs(x - xa).argmax())]
    ESTADO[chave] = x; LOG.setdefault("erro_ik_" + chave, 0.0)
    LOG["erro_ik_" + chave] = round(max(LOG["erro_ik_" + chave], err), 3)
    return P2
def foco(M): return cabeca(M, FOC)
def cab(M): return cabeca(M, "head")
# ---------------------------------------------------------------- SacudirCorpo
T_SAC = T_IDLE
def c_sacudir(t):
    P, fold = I(t)
    w = 2 * math.pi * 4.2 * t                                          # ~4 Hz (animal medio)
    e_pesc = env(t, 0.45, 0.75, 1.55, 1.95); e_tronco = env(t, 0.65, 0.95, 1.75, 2.15)
    e_cauda = env(t, 0.85, 1.2, 1.95, 2.4); e_asa = env(t, 1.15, 1.45, 2.15, 2.6)
    agachar(P, 0.35 * env(t, 0.2, 0.6, 2.2, 2.75))                      # firma as pernas
    for i, b in enumerate(PESCOCO): girar(P, b, Z, R(7) * e_pesc * math.sin(w - 0.5 * i))
    girar(P, "head", Z, R(9) * e_pesc * math.sin(w - 2.8)); girar(P, "head", FRENTE, R(12) * e_pesc * math.sin(w - 2.8))
    girar(P, "jaw", X, R(-6) * e_pesc)                                  # boca entreaberta
    girar(P, "spine_01", FRENTE, R(7) * e_tronco * math.sin(w - 0.9))   # tronco rola (pivo no quadril)
    girar(P, "spine_02", FRENTE, R(4) * e_tronco * math.sin(w - 1.4))
    for i, b in enumerate(CAUDA): girar(P, b, Z, R(3.0) * e_cauda * math.sin(w - 1.6 - 0.45 * i))
    for b in CAUDA[:4]: girar(P, b, X, R(1.5) * max(e_cauda, e_tronco))   # cauda sobe um pouco (nao varre o chao)
    for s in "LR":
        girar(P, "shoulder_" + s, Y, R(-10) * sx_(s) * e_asa)            # asas afastam um pouco do corpo
        girar(P, "upperarm_" + s, FRENTE, R(6) * e_asa * math.sin(1.6 * w) * sx_(s))   # e tremem
        girar(P, "forearm_" + s, X, R(5) * e_asa * math.sin(1.6 * w + 0.8))
    return P, fold
# ---------------------------------------------------------------- AlisarAsa (E/D)
T_ALI = 2 * T_IDLE
def alvo_membrana(M, s, u):
    a, b = cabeca(M, "upperarm_" + s), cabeca(M, "forearm_" + s)
    p = a.lerp(b, u); c = cabeca(M, "strut_a_02_" + s)
    p = p.lerp(c, 0.25)                                                 # um pouco para dentro da membrana
    n = (b - a).cross(c - b).normalized()
    if n.dot(cab(M) - p) < 0: n = -n
    return p + n * 0.55                                                 # focinho encosta por fora (sem atravessar)
def c_alisar(lado):
    s = lado
    def fn(t):
        P, fold = I(t)
        ea = env(t, 0.2, 1.3, 4.6, 5.8)                                 # asa
        ec = env(t, 0.7, 1.8, 4.3, 5.5)                                 # cabeca
        P = misturar(P, ASA_ABERTA, 0.6 * ea, ASA[s])
        girar(P, "shoulder_" + s, Z, R(-22) * sx_(s) * ea)               # asa trazida um pouco a frente
        girar(P, "shoulder_" + s, Y, R(-30) * sx_(s) * ea)               # e erguida (a mao nao toca o chao)
        girar(P, "spine_02", Z, R(5) * sx_(s) * ec)             # tronco acompanha um pouco
        Pb = P
        if ec > 1e-3:
            M = fk(P)
            u = 0.45 + 0.3 * math.sin(2 * math.pi * (t - 1.8) / 2.5)     # percorre a membrana devagar
            alvo = alvo_membrana(M, s, u)
            mord = max(0.0, math.sin(2 * math.pi * 3.2 * t))             # mordiscadas
            alvo = alvo + (cab(M) - alvo).normalized() * 0.25 * mord
            f0 = foco(fk(Pb, [FOC]))
            Pik = ik_focinho("ali" + s, Pb, [(foco, f0.lerp(alvo, ec), 1.0)])
            P = misturar(Pb, Pik, 1.0, ["spine_03"] + PESCOCO + ["head"])
            girar(P, "jaw", X, R(-10) * mord * ec)
        else:
            ESTADO.pop("ali" + s, None)
        return P, fold
    return fn
# ---------------------------------------------------------------- Espreguicar
T_ESP = 2 * T_IDLE
def c_espreguicar(t):
    P, fold = I(t)
    ea = env(t, 0.3, 2.0, 3.6, 5.4)                                     # asas
    ep = env(t, 0.8, 2.3, 3.8, 5.6)                                     # pescoco/arco
    inclinar(P, 10 * ep)                                                # peito a frente
    agachar(P, 0.5 * ep)
    P = misturar(P, ASA_ABERTA, 0.9 * ea, ASAS)
    tr = math.sin(2 * math.pi * 7 * t) * env(t, 2.0, 2.4, 3.3, 3.8)     # tremor do alongamento
    for s in "LR":
        girar(P, "shoulder_" + s, Y, (R(-12) + R(1.5) * tr) * sx_(s) * ea)   # asas acima, esticadas
        girar(P, "shoulder_" + s, Z, R(10) * sx_(s) * ea)                # e para tras
    for i, b in enumerate(CAUDA[:6]): girar(P, b, X, R(3.5) * ep)       # cauda sobe (arco)
    f0 = foco(fk(P, [FOC]))
    alvo = f0 + V((0, -1.7, -0.9)) * ep                                 # focinho longe a frente
    if ep > 1e-3:
        Pik = ik_focinho("esp", P, [(foco, alvo, 1.0)])
        P = misturar(P, Pik, 1.0, ["spine_03"] + PESCOCO + ["head"])
    else:
        ESTADO.pop("esp", None)
    boc = env(t, 2.3, 2.8, 3.4, 4.0)                                    # bocejo no auge
    girar(P, "jaw", X, R(-32) * boc); girar(P, "head", X, R(-8) * boc)
    return P, fold
# ---------------------------------------------------------------- Farejar
T_FAR = 2 * T_IDLE
FAR_PONTOS = [(0.0, V((0.0, -11.6, 1.85))), (1.0, V((2.6 * ESQ, -10.8, 1.75))), (2.0, V((-2.2 * ESQ, -11.2, 1.8)))]
def alvo_farejar(t):
    # desce (0,4-1,5), cheira no centro, no lado E, no lado D (pausas de ~0,9 s), sobe (4,8-5,8)
    marcas = [(1.5, 0), (2.4, 0), (2.8, 1), (3.5, 1), (3.9, 2), (4.6, 2)]
    if t <= marcas[0][0]: return FAR_PONTOS[0][1]
    for (ta, ia), (tb, ib) in zip(marcas, marcas[1:]):
        if t <= tb: return FAR_PONTOS[ia][1].lerp(FAR_PONTOS[ib][1], suave((t - ta) / (tb - ta)))
    return FAR_PONTOS[2][1]
def c_farejar(t):
    P, fold = I(t)
    ed = env(t, 0.3, 1.5, 4.6, 5.8)
    inclinar(P, 14 * ed)
    agachar(P, 0.6 * ed)
    for s_ in "LR": girar(P, "shoulder_" + s_, Y, R(-7) * sx_(s_) * ed)   # asas dobradas um pouco erguidas (pontas fora do chao)
    f0 = foco(fk(P, [FOC])); c0 = cab(fk(P, ["head"]))
    if ed > 1e-3:
        alvo = alvo_farejar(t)                                          # sem fungadas (pedido do usuario 12/11)
        alvo_f = f0.lerp(alvo, ed)
        alvo_c = c0.lerp(alvo + V((0, 1.6, 2.2)), ed)                   # cabeca atras/acima: focinho aponta para baixo
        Pik = ik_focinho("far", P, [(foco, alvo_f, 1.0), (cab, alvo_c, 0.25)])
        P = misturar(P, Pik, 1.0, ["spine_03"] + PESCOCO + ["head"])
        # balanco suave da cabeca esquerda-direita enquanto cheira (so a cabeca, ~0,9 Hz) + leve rolagem
        eb = env(t, 1.4, 1.9, 4.4, 4.9)
        bal = math.sin(2 * math.pi * 0.9 * (t - 1.4)) * eb
        girar(P, "head", Z, R(9) * bal)
        girar(P, "head", Y, R(-4) * bal)
    # boca fechada: no repouso do modelo a boca ja fica entreaberta; +18 graus em X local fecha (close 12/11, review/l5/boca)
    P = misturar(P, {**P, "jaw": (P["jaw"][0], Q(V((1, 0, 0)), R(18)), P["jaw"][2])}, env(t, 0.0, 0.5, 5.5, 6.0), ["jaw"])
    if ed <= 1e-3:
        ESTADO.pop("far", None)
    return P, fold
# ---------------------------------------------------------------- OlharVolta
T_OLH = 2 * T_IDLE
def c_olhar(t):
    P, fold = I(t)
    # angulo de giro (+ = esquerda da Wyvern): centro -> E (pausa) -> D (pausa) -> centro
    def lerp_k(marcas):
        for (ta, va), (tb, vb) in zip(marcas, marcas[1:]):
            if t <= tb: return va + (vb - va) * suave((t - ta) / (tb - ta)) if t >= ta else va
        return marcas[-1][1]
    g = lerp_k([(0.0, 0.0), (0.4, 0.0), (1.2, 1.0), (2.3, 1.0), (3.4, -1.0), (4.6, -1.0), (5.5, 0.0), (6.0, 0.0)])
    incl = lerp_k([(0.0, 0.0), (1.4, 0.0), (1.8, 1.0), (2.2, 0.0), (3.6, 0.0), (4.0, -1.0), (4.4, 0.0), (6.0, 0.0)])
    eix = lerp_k([(0.0, 0.0), (0.4, 0.0), (1.0, 1.0), (5.2, 1.0), (5.8, 0.0), (6.0, 0.0)])
    ang = R(75) * g * ESQ                                               # total da cabeca
    girar(P, "spine_03", Z, ang * 0.06)
    for b, k in zip(PESCOCO, (0.14, 0.18, 0.2, 0.2, 0.16)): girar(P, b, Z, ang * k)
    girar(P, "head", Z, ang * 0.06)
    for b in PESCOCO[1:4]: girar(P, b, X, R(-2.5) * eix)               # pescoco ergue (vigia)
    girar(P, "head", FRENTE, R(16) * incl)                              # inclina a cabeca (ouvindo)
    return P, fold
# ---------------------------------------------------------------- DecolagemPenhasco
T_DEC = 2.4
Z_CHAO = -0.022                                                    # z minimo do idle
def pernas_recolhidas(P, k=1.0):
    for s in "LR":
        girar(P, "thigh_" + s, X, R(28) * k); girar(P, "calf_" + s, X, R(-25) * k); girar(P, "toe_" + s, X, R(20) * k)
def c_decolagem(t):
    Pi, fi = I(t)
    e_ag = env(t, 0.0, 0.75, 0.82, 1.05)                                 # agacha na borda e solta
    e_inc = env(t, 0.1, 0.8, 1.15, 2.1)                                  # bico para baixo
    P = copia(Pi)
    inclinar(P, 12 * e_ag + 30 * e_inc * suave((t - 0.7) / 0.35))       # antes do agachamento: pes apoiados nao saem do lugar
    w_apoio = 1 - suave((t - 0.85) / 0.25)                               # pes soltam a borda aos poucos (0,85 -> 1,1 s)
    if w_apoio > 0:
        Pa = copia(P); agachar(Pa, max(1.3 * e_ag, 1e-3))                # jarrete/pe presos ao ponto do idle
        P = misturar(P, Pa, w_apoio)
    for s_ in "LR": girar(P, "shoulder_" + s_, Y, R(-14) * sx_(s_) * env(t, 0.0, 0.6, 0.95, 1.3))   # asas fora do chao no agachamento
    w_asa = suave((t - 0.75) / 0.9)
    P = misturar(P, ASA_ABERTA, 0.25 * env(t, 0.0, 0.7, 0.8, 1.0), ASAS)   # asas se soltam do corpo
    pul = env(t, 0.8, 1.0, 1.0, 1.6)
    for s in "LR":
        girar(P, "thigh_" + s, X, R(32) * pul); girar(P, "calf_" + s, X, R(-10) * pul)   # pernas estendidas para tras
        girar(P, "foot_" + s, X, R(30) * pul); girar(P, "toe_" + s, X, R(25) * pul)
    pernas_recolhidas(P, 0.6 * suave((t - 1.3) / 0.6))
    for b in PESCOCO: girar(P, b, X, R(-3) * e_inc)                      # olha a frente/baixo, nao para o chao
    for i, b in enumerate(CAUDA[:5]): girar(P, b, X, R(2.5) * e_inc)     # cauda alinha (leme)
    Pp, fp = amostra("Planeio", (t - T_DEC) % T_PLA)                     # termina no quadro 0 do Planeio
    w = suave((t - 0.85) / (T_DEC - 0.85))
    Pa = misturar(P, ASA_ABERTA, 1.0, ASAS)
    P = misturar(P, Pa, w_asa * (1 - w))
    P = misturar(P, Pp, w); fold = fi * (1 - w) + fp * w
    if 0.75 < t < 1.6:                                                   # impulso: o corpo sobe o que faltar (pes nao entram na borda)
        z = zmin_reg(P, fold); d = Z_CHAO - min(z["pernaL"], z["pernaR"])
        if d > 0: mover(P, "root", V((0, 0, d)))
    return P, fold
CLIPES = {"SacudirCorpo": (c_sacudir, T_SAC, False), "AlisarAsaEsquerda": (c_alisar("L" if ESQ > 0 else "R"), T_ALI, False),
          "AlisarAsaDireita": (c_alisar("R" if ESQ > 0 else "L"), T_ALI, False), "Espreguicar": (c_espreguicar, T_ESP, False),
          "Farejar": (c_farejar, T_FAR, False), "OlharVolta": (c_olhar, T_OLH, False), "DecolagemPenhasco": (c_decolagem, T_DEC, False)}
SO = argv[3].split(",") if len(argv) > 3 else list(CLIPES)
mani = {"_fonte": "Wyvern_E7_clipes_L4.blend (idle_loop, fly_loop, Planeio)", "_hz": HZ}
for nome in SO:
    fn, dur, loop = CLIPES[nome]; ESTADO.clear(); mani[nome] = gravar_clipe(nome, fn, dur, loop); print("CLIPE", nome, mani[nome], flush=True)
mani["_calibracao"] = LOG; print("CALIB", json.dumps(LOG), flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
