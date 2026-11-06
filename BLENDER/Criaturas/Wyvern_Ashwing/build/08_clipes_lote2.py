# Lote 2 de clipes da Wyvern (combate, reacoes e vida em terra), sobre o lote 1 (Wyvern_E7_clipes_L1.blend).
# Derivados do idle_loop/roar do proprio Ashwing + camadas procedurais. Clipes visuais: angulos e tempos sao PROPOSTA,
# nao definem dano, alcance, janelas ou mecanicas.
#   FerraoAtaque  cauda arma em arco sobre o dorso (estilo escorpiao) e ferroa a frente, ao lado da cabeca; volta ao idle
#   Alerta        (= "Observar, ferrao erguido") postura alta, cabeca varrendo os lados, ferrao meio armado, loop
#   Ameaca        roar do Ashwing + ferrao armado e tremendo na ponta
#   ReacaoGolpe   tranco curto: peito para tras, cabeca sacode, asas se abrem um pouco, volta ao idle
#   Morte         tranco -> pernas cedem -> cai de barriga, asas abertas caidas no chao, pescoco de lado; pose final parada
#   Comer         em pe, cabeca no chao: morde e arranca (2 puxoes por ciclo), loop
#   Deitar / Deitado / Levantar   conjunto do Descanso: deita de barriga (pernas dobradas por IK, pes fixos no chao),
#                 cabeca apoiada a frente; Deitado respira em loop; Levantar ergue a cabeca primeiro
# Uso: blender -b Wyvern_E7_clipes_L1.blend -P 08_clipes_lote2.py -- <08_base.py> <saida.blend> <manifesto.json>
import bpy, sys, math, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
I0, FI0 = amostra("idle_loop", 0.0)
def I(t): return amostra("idle_loop", t)
LOG = {}
# ---------------------------------------------------------------- ferrao: arco sobre o dorso e golpe
ARCO = [35, 35, 20, 20, 20, 15, 15, 15, 20, 20]          # graus em X (+ = ergue) por segmento: 215 no total
GOLPE = [24, 18, 2, -6, -12, -12, -6, 2, 10, 14]        # somado ao arco no golpe: o arco se lanca a frente e a ponta
                                                         # desce adiante da cabeca (passa ~2 studs acima dos chifres)
LADO_ARCO = [3, 3, 2, 0, 0, 0, 0, 0, 0, 0]               # graus em Z: desloca o arco para o lado L (passa ao lado da cabeca)
def cauda_ferrao(P, k_arco, k_golpe=0.0):
    s = ESQ
    for i, b in enumerate(CAUDA):
        girar(P, b, X, R(ARCO[i] * k_arco + GOLPE[i] * k_golpe))
        girar(P, b, Z, R(LADO_ARCO[i] * (k_arco + 1.5 * k_golpe)) * s)
PRONTO = [5, 5, 4, 4, 5, 8, 14, 20, 26, 30]            # ferrao "pronto": cauda sobe atras do corpo e a ponta curva a frente
def cauda_pronto(P, k):
    for i, b in enumerate(CAUDA): girar(P, b, X, R(PRONTO[i] * k))
T_FER = 1.5
def c_ferrao(t):
    P, fold = I(t)
    a = suave(t / 0.40)                                    # arma (0-0,40 s)
    g = suave((t - 0.40) / 0.16)                           # golpe rapido (0,40-0,56 s)
    r = suave((t - 0.78) / 0.72)                           # volta (0,78-1,5 s)
    ka = a * (1 - r); kg = g * (1 - r)
    cauda_ferrao(P, ka, kg)
    girar(P, "spine_01", X, R(-4 * ka + 9 * kg))           # peito sobe ao armar, avanca no golpe
    for b in PESCOCO: girar(P, b, X, R(-2.5 * ka + 1.5 * kg))
    for b in PESCOCO[2:]: girar(P, b, Z, R(-4) * kg * ESQ) # cabeca sai para o lado oposto ao ferrao
    girar(P, "head", X, R(4 * ka - 4 * kg))
    girar(P, "jaw", X, R(10) * ka * (1 - kg))              # boca entreaberta enquanto mira
    return P, fold
# ---------------------------------------------------------------- alerta (observar, ferrao erguido)
T_ALE = DUR["idle_loop"]
def c_alerta(t):
    P, fold = I(t)
    u = 2 * math.pi * t / T_ALE
    girar(P, "spine_01", X, R(-6)); girar(P, "spine_02", X, R(-2))
    for b in PESCOCO[:3]: girar(P, b, X, R(-4))
    girar(P, "head", X, R(10))
    varre = math.sin(u) * 0.85 + 0.15 * math.sin(3 * u)    # varre esquerda/direita com pausas
    for b in PESCOCO: girar(P, b, Z, R(5) * varre)
    girar(P, "head", Z, R(9) * varre)
    cauda_pronto(P, 1.0)
    for i, b in enumerate(CAUDA[6:]): girar(P, b, X, R(2.5) * math.sin(u * 2 - 0.6 * i))   # ponta inquieta
    return P, fold
# ---------------------------------------------------------------- ameaca (roar + ferrao armado tremendo)
T_AME = DUR["roar"]
def c_ameaca(t):
    P, fold = amostra("roar", t, loop=False)
    k = suave(t / 0.35) * (1 - suave((t - (T_AME - 0.45)) / 0.45))
    cauda_pronto(P, 0.7 * k)
    trem = math.sin(2 * math.pi * 9 * t) * k
    for b in CAUDA[8:]: girar(P, b, Z, R(3.0) * trem)
    girar(P, "spine_01", X, R(-3) * k)
    return P, fold
# ---------------------------------------------------------------- reacao a golpe
T_REA = 0.75
def tranco(t, pico=0.07, fim=0.75):
    return suave(t / pico) * (1 - suave((t - pico) / (fim - pico)))
def aplicar_tranco(P, e, lado=1.0):
    girar(P, "spine_01", X, R(-9) * e); girar(P, "spine_02", X, R(-3) * e)
    for b in PESCOCO: girar(P, b, X, R(-3) * e)
    for b in PESCOCO[2:]: girar(P, b, Z, R(5) * e * lado * ESQ)
    girar(P, "head", X, R(10) * e); girar(P, "head", Z, R(8) * e * lado * ESQ)
    girar(P, "jaw", X, R(16) * e)
    for s in "LR":
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P, "shoulder_" + s, Y, R(-10) * sx * e)     # asas sobem/abrem um pouco (susto)
    for b in CAUDA[:4]: girar(P, b, X, R(3) * e)
def c_reacao(t):
    P, fold = I(t)
    e = tranco(t)
    tremor = math.sin(2 * math.pi * 6 * t) * 0.25 * suave((t - 0.07) / 0.1) * (1 - suave((t - 0.25) / 0.35))
    aplicar_tranco(P, e + tremor * e)
    return P, fold
# ---------------------------------------------------------------- deitado de barriga (base do Descanso e da Morte)
QUEDA = 4.25                                                       # barriga do idle fica 4,58 acima do chao
def _juntas(M, s): return (ponta(M, "calf_" + s), ponta(M, "foot_" + s), ponta(M, "toe_" + s))   # jarrete, bola, ponta
LEG0 = {s: _juntas(fk(I0, PERNA[s]), s) for s in "LR"}             # em pe (idle)
LEGD = {}                                                          # deitado (calibrado abaixo)
def _alvos(s, alv, pesos):
    return [(lambda M, s=s, k=k: _juntas(M, s)[k], alv[k], pesos[k]) for k in range(3)]
def pernas(P, w):
    """dobra as pernas por IK entre a pose em pe e a deitada (peso w). Deitada: joelho a frente e alto, jarrete no
    chao sob o quadril, pe e dedos chapados a frente (os dedos avancam ~2,5 studs: o pe se acomoda ao deitar)"""
    res = {}
    for s in "LR":
        alv = [LEG0[s][k].lerp(LEGD[s][k], w) for k in range(3)]
        res[s] = round(ik_perna(P, s, _alvos(s, alv, (0.5, 1.0, 1.0))), 3)
    return res
def agachar(P):
    """mantem bola e ponta do pe do idle (jarrete livre) depois de baixar a raiz"""
    for s in "LR": ik_perna(P, s, _alvos(s, LEG0[s], (1e-3, 1.0, 1.0)))
def calibrar_pernas():
    """IK deitado; os alvos sobem ate a malha do pe/dedo ficar 0,04 acima do chao (a malha e mais grossa que o osso)"""
    res = {}; dz = {"L": 0.0, "R": 0.0}
    for it in range(5):
        Pc = copia(I0); mover(Pc, "root", V((0, 0, -QUEDA)))
        for s in "LR":
            h0 = LEG0[s][1]; d = dz[s]
            alvos = [(lambda M, s=s: cabeca(M, "calf_" + s), V((0, 0, 1.45 + d)), V((0, 0, 1))),          # joelho alto
                     (lambda M, s=s: ponta(M, "calf_" + s), V((0, h0.y + 0.2, 0.55 + d)), V((0, 1, 1))),
                     (lambda M, s=s: ponta(M, "foot_" + s), V((0, 0, 0.40 + d)), V((0, 0, 1))),
                     (lambda M, s=s: ponta(M, "toe_" + s), V((0, 0, 0.06 + d)), V((0, 0, 1)))]
            res[s] = round(ik_perna(Pc, s, alvos, it=80), 3)
            M = fk(Pc, PERNA[s]); LEGD[s] = _juntas(M, s)
        zr = zmin_reg(Pc, FI0)
        for s in "LR": dz[s] += 0.04 - zr["perna" + s]
        res["zmin_it%d" % it] = {s: zr["perna" + s] for s in "LR"}
    for s in "LR":
        res[s + "_juntas"] = [[round(x, 2) for x in j] for j in LEGD[s]]
    LOG["pernas_deitado"] = res
calibrar_pernas()
PARAM = {}
def inclinacao_cabeca(P):
    M = fk(P, ["head"]); d = ponta(M, "head") - cabeca(M, "head")
    h = math.hypot(d.x, d.y) * (1.0 if -d.y >= 0 else -1.0)      # horizontal com sinal: a frente e -Y
    return math.degrees(math.atan2(d.z, h))
DIST_PESC = [0.40, 0.28, 0.18, 0.10, 0.04]                         # pescoco baixa estendido (mais na base), sem virar U
def baixar_pescoco(P, A):
    for b, k in zip(PESCOCO, DIST_PESC): girar(P, b, X, A * k)
def corrigir_cabeca(P, alvo):
    """gira a cabeca em X ate o osso apontar alvo graus (negativo = focinho para baixo); devolve o angulo usado"""
    tot = 0.0
    for _ in range(4):
        d = R(inclinacao_cabeca(P) - alvo); girar(P, "head", X, d); tot += d
    return tot
def deitado_corpo(P, w):
    mover(P, "root", V((0, 0, -QUEDA * w)))
    pernas(P, w)
    girar(P, "spine_01", X, R(3) * w)
    for s in "LR":
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P, "shoulder_" + s, Y, -PARAM["asa_" + s] * sx * w)
        girar(P, "forearm_" + s, X, PARAM["ante_" + s] * w)           # antebraco mais dobrado: a garra do polegar nao afunda
    for b in CAUDA[:2]: girar(P, b, X, -PARAM["cauda"] * w / 2)
    for i, b in enumerate(CAUDA[3:]): girar(P, b, Z, R(3.5) * w * ESQ)
def deitado_cabeca(P, w):
    baixar_pescoco(P, PARAM["pescoco"] * w)
    girar(P, "head", X, PARAM["cab_dei"] * w)                     # cabeca nivelada: queixo apoiado
def calibrar_deitado():
    P, f = copia(I0), FI0
    Pc = copia(P); mover(Pc, "root", V((0, 0, -QUEDA))); LOG["ik_deitado"] = pernas(Pc, 1.0)
    girar(Pc, "spine_01", X, R(3))
    for s in "LR": PARAM["asa_" + s] = 0.0; PARAM["ante_" + s] = 0.0
    PARAM["cauda"] = 0.0
    def zcau(a):
        Pt = copia(Pc)
        for b in CAUDA[:2]: girar(Pt, b, X, -a / 2)
        return zmin_reg(Pt, f)["cauda"]
    PARAM["cauda"] = bissecao(zcau, 0.0, R(12), 0.06) if zcau(0.0) > 0.06 else 0.0
    PARAM["pescoco"] = 0.0
    Pb = copia(P); deitado_corpo(Pb, 1.0)
    def zcab(a):
        Pt = copia(Pb)
        baixar_pescoco(Pt, a)
        PARAM["cab_dei"] = corrigir_cabeca(Pt, -8.0)
        return zmin_reg(Pt, f)["cabeca"]
    PARAM["pescoco"] = bissecao(lambda a: -zcab(a), 0.0, R(130), -0.22); zcab(PARAM["pescoco"])
    def zasa(a, s):
        PARAM["asa_" + s] = a; Pt = copia(P); deitado_corpo(Pt, 1.0); deitado_cabeca(Pt, 1.0)
        return zmin_reg(Pt, f)["asa" + s]
    def zante(a, s):
        PARAM["ante_" + s] = a; Pt = copia(P); deitado_corpo(Pt, 1.0); deitado_cabeca(Pt, 1.0)
        return zmin_reg(Pt, f)["asa" + s]
    for s in "LR":                                                   # 1o o antebraco; o ombro so se ainda faltar
        PARAM["ante_" + s] = bissecao(lambda a, s=s: zante(a, s), 0.0, R(-40), 0.14, it=14) if zante(0.0, s) < 0.14 else 0.0
        PARAM["asa_" + s] = bissecao(lambda a, s=s: -zasa(a, s), 0.0, R(30), -0.05, it=14) if zasa(0.0, s) < 0.05 else 0.0
    Pd = copia(P); deitado_corpo(Pd, 1.0); deitado_cabeca(Pd, 1.0)
    LOG["deitado_param_graus"] = {k: round(math.degrees(v), 2) for k, v in PARAM.items()}
    LOG["deitado_zmin"] = zmin_reg(Pd, f)
calibrar_deitado()
T_DEI, T_LEV, T_DLOOP = 2.0, 1.6, 4.0
def respirar(P, t, T):
    u = 2 * math.pi * t / T
    girar(P, "spine_02", X, R(0.9) * math.sin(u)); girar(P, "spine_03", X, R(0.6) * math.sin(u - 0.4))
    girar(P, "head", X, R(0.6) * math.sin(u - 0.8))
    for i, b in enumerate(CAUDA[6:]): girar(P, b, Z, R(1.0) * math.sin(u - 0.5 * i))
def c_deitar(t):
    wb = suave(t / 1.55); wn = suave((t - 0.45) / 1.55)
    Pi, fi = I(t); P = misturar(Pi, I0, wb); fold = fi * (1 - wb) + FI0 * wb
    deitado_corpo(P, wb); deitado_cabeca(P, wn)
    return P, fold
def c_deitado(t):
    P = copia(I0); deitado_corpo(P, 1.0); deitado_cabeca(P, 1.0); respirar(P, t, T_DLOOP)
    return P, FI0
def c_levantar(t):
    wn = 1 - suave(t / 0.85); wb = 1 - suave((t - 0.3) / 1.2)
    Pi, fi = I(t); P = misturar(Pi, I0, wb); fold = fi * (1 - wb) + FI0 * wb
    deitado_corpo(P, wb); deitado_cabeca(P, wn)
    return P, fold
# ---------------------------------------------------------------- morte
# pose final: deitado de barriga, asas abertas caidas ate o chao (pose de asa do planeio baixada), pescoco de lado
def curvas_fly():
    best = None
    for k in range(96):
        t = DUR["fly_loop"] * k / 96; Pf, _ = amostra("fly_loop", t); M = fk(Pf)
        pl, pr = ponta(M, "strut_b_02_L"), ponta(M, "strut_b_02_R")
        om = (cabeca(M, "upperarm_L") + cabeca(M, "upperarm_R")) / 2
        sc_ = (pl - pr).length - (abs(pl.z - om.z) + abs(pr.z - om.z))
        if best is None or sc_ > best[0]: best = (sc_, t)
    return amostra("fly_loop", best[1])[0]
ASA_ABERTA = curvas_fly()
def morto_pose(P, w_asa, w_corpo, w_cab):
    P2 = misturar(P, ASA_ABERTA, w_asa, ASA["L"] + ASA["R"])
    deitado_corpo(P2, w_corpo)
    for s in "LR":                                                  # desfaz o erguer de asa do deitado e baixa ate o chao
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P2, "shoulder_" + s, Y, (PARAM["asa_" + s] * w_corpo + PARAM["mort_asa_" + s] * w_asa * w_corpo) * sx)
    baixar_pescoco(P2, PARAM["mort_pesc"] * w_cab)
    for s in "LR":
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P2, "thumb_" + s, Y, PARAM["mort_pol_" + s] * sx * w_asa * w_corpo)
    for b in PESCOCO: girar(P2, b, Z, R(-6) * w_cab * ESQ)         # pescoco cai para o lado R
    girar(P2, "head", X, PARAM["cab_mor"] * w_cab); girar(P2, "head", Y, R(-14) * w_cab * ESQ)
    girar(P2, "jaw", X, R(11) * w_cab)
    girar(P2, "spine_01", Y, R(-5) * w_corpo * ESQ)
    return P2
def calibrar_morte():
    for s in "LR": PARAM["mort_asa_" + s] = 0.0; PARAM["mort_pol_" + s] = 0.0
    PARAM["mort_pesc"] = 0.0; PARAM["cab_mor"] = 0.0
    PONTAS = {s: [b for b in ASA[s] if b.startswith(("strut_b_02", "strut_c_02", "strut_d_02", "finger_02"))] for s in "LR"}
    def zasa(a, s):                                                  # a ponta da asa (nao a garra) encosta no chao
        PARAM["mort_asa_" + s] = a; return zmin_ossos(morto_pose(copia(I0), 1, 1, 0), 0.0, PONTAS[s])
    for s in "LR":
        PARAM["mort_asa_" + s] = bissecao(lambda a, s=s: zasa(a, s), 0.0, R(70), 0.06, it=16) if zasa(0.0, s) > 0.06 else 0.0
    def zpol(a, s):
        PARAM["mort_pol_" + s] = a; return zmin_ossos(morto_pose(copia(I0), 1, 1, 0), 0.0, ["thumb_" + s])
    for s in "LR":
        PARAM["mort_pol_" + s] = bissecao(lambda a, s=s: -zpol(a, s), 0.0, R(110), -0.04, it=14) if zpol(0.0, s) < 0.04 else 0.0
    def zcab(a):
        PARAM["mort_pesc"] = a; PARAM["cab_mor"] = 0.0; Pt = morto_pose(copia(I0), 1, 1, 1)
        PARAM["cab_mor"] = corrigir_cabeca(Pt, -4.0)
        return zmin_reg(morto_pose(copia(I0), 1, 1, 1), 0.0)["cabeca"]
    PARAM["mort_pesc"] = bissecao(lambda a: -zcab(a), 0.0, R(130), -0.1); zcab(PARAM["mort_pesc"])
    LOG["morte_param_graus"] = {k: round(math.degrees(PARAM[k]), 2) for k in PARAM if k.startswith("mort")}
    LOG["morte_zmin"] = zmin_reg(morto_pose(copia(I0), 1, 1, 1), 0.0)
calibrar_morte()
T_MOR = 2.7
def c_morte(t):
    Pi, fold = I(t); P = misturar(Pi, I0, suave((t - 0.3) / 0.8))      # base vai para o quadro calibrado (I0)
    e = tranco(t, 0.07, 0.6)
    aplicar_tranco(P, e * (1 - suave((t - 0.3) / 0.3)), lado=-1.0)
    wc = suave((t - 0.30) / 0.85)                                   # pernas cedem e o corpo cai (0,30-1,15 s)
    wa = suave((t - 0.40) / 0.75)                                   # asas abrem e caem
    wh = suave((t - 0.55) / 0.75)                                   # pescoco desaba por ultimo
    quique = math.sin(math.pi * min(max((t - 1.32) / 0.3, 0), 1))          # cabeca quica uma vez ao bater
    P = morto_pose(P, wa, wc, wh)
    for s in "LR":                                                  # asas sobem ao abrir e so depois caem (nao varrem o chao)
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P, "shoulder_" + s, Y, -R(40) * math.sin(math.pi * wa) * (1 - wc * 0.5) * sx)
    girar(P, "neck_05", X, R(-4) * quique)
    fold = fold * (1 - wa)
    return P, fold
# ---------------------------------------------------------------- comer (em pe, cabeca no chao)
T_COM = DUR["idle_loop"]                                           # mesmo periodo do idle: o laco fecha
QC = 1.5                                                           # agacha 1,5 stud (pes fixos por IK)
def comer_base(P):
    mover(P, "root", V((0, 0, -QC))); agachar(P)
    for b in COLUNA: girar(P, b, X, R(7))
    baixar_pescoco(P, PARAM["comer_pesc"])
    girar(P, "head", X, PARAM["cab_com"])
    for s in "LR":
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P, "shoulder_" + s, Y, -PARAM["asa_com_" + s] * sx)
def calibrar_comer():
    PARAM["comer_pesc"] = 0.0; PARAM["cab_com"] = 0.0; PARAM["asa_com_L"] = PARAM["asa_com_R"] = 0.0
    def zcab(a):
        PARAM["comer_pesc"] = a; PARAM["cab_com"] = 0.0; Pt = copia(I0); comer_base(Pt)
        PARAM["cab_com"] = corrigir_cabeca(Pt, -35.0); return zmin_reg(Pt, FI0)["cabeca"]
    PARAM["comer_pesc"] = bissecao(lambda a: -zcab(a), 0.0, R(150), -0.65); zcab(PARAM["comer_pesc"])
    def zasa(a, s):
        PARAM["asa_com_" + s] = a; Pt = copia(I0); comer_base(Pt); return zmin_reg(Pt, FI0)["asa" + s]
    for s in "LR":
        PARAM["asa_com_" + s] = bissecao(lambda a, s=s: -zasa(a, s), 0.0, R(30), -0.6, it=14) if zasa(0.0, s) < 0.6 else 0.0
    Pt = copia(I0); comer_base(Pt)
    LOG["comer_param_graus"] = {k: round(math.degrees(PARAM[k]), 2) for k in ("comer_pesc", "cab_com", "asa_com_L", "asa_com_R")}; LOG["comer_zmin"] = zmin_reg(Pt, FI0)
calibrar_comer()
def c_comer(t):
    P, fold = I(t)
    comer_base(P)
    u = (t / T_COM) * 2 % 1.0                                       # 2 puxoes por ciclo
    mord = suave(u / 0.18) * (1 - suave((u - 0.22) / 0.12))         # abre e fecha a boca no chao
    puxa = suave((u - 0.30) / 0.22) * (1 - suave((u - 0.62) / 0.30))   # arranca: ergue e sacode a cabeca
    girar(P, "jaw", X, R(18) * mord + R(5) * puxa)
    for b in PESCOCO[1:]: girar(P, b, X, R(-3.5) * puxa)
    girar(P, "head", X, R(6) * puxa)
    sac = math.sin(2 * math.pi * (u - 0.30) / 0.16) * puxa * (1 if int(t / T_COM * 2) % 2 == 0 else -1)
    girar(P, "head", Z, R(9) * sac); girar(P, "neck_05", Z, R(4) * sac)
    return P, fold
# ---------------------------------------------------------------- gravacao
CLIPES = {  # nome: (funcao, duracao, loop)
    "FerraoAtaque": (c_ferrao, T_FER, False),
    "Alerta": (c_alerta, T_ALE, True),
    "Ameaca": (c_ameaca, T_AME, False),
    "ReacaoGolpe": (c_reacao, T_REA, False),
    "Morte": (c_morte, T_MOR, False),
    "Comer": (c_comer, T_COM, True),
    "Deitar": (c_deitar, T_DEI, False),
    "Deitado": (c_deitado, T_DLOOP, True),
    "Levantar": (c_levantar, T_LEV, False),
}
SO = argv[3].split(",") if len(argv) > 3 else list(CLIPES)
mani = {"_fonte": "Wyvern_E7_clipes_L1.blend (idle_loop/roar/fly_loop do Ashwing)", "_hz": HZ, "_lado_L_em_X": ESQ, "_calibracao": LOG}
print("CALIB", json.dumps(LOG, default=str), flush=True)
for nome in SO:
    fn, dur, loop = CLIPES[nome]
    mani[nome] = gravar_clipe(nome, fn, dur, loop)
    print("CLIPE", nome, mani[nome], flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
print("OK")
