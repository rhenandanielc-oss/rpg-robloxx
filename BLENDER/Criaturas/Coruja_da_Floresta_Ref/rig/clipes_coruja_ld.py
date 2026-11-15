# ================================================================== LOTE D da Coruja-da-Floresta (15/11/2026): defesa e derrota, ESTUDO.
# Carregado com CORUJA_LD=1 (traz os lotes B e C; rig r4 com palpebras: CORUJA_R3=1, CORUJA_DOBRA=rig/r3/dobra_asas.json,
# CORUJA_PALPEBRAS=rig/r4/palpebras.json). Sem dano, hitbox ou regra de jogo: como a coruja e derrotada, onde cai o corpo e
# se ela foge ou ameaca sao [PENDENTE]/[PROPOSTA] (DOCS/fauna/floresta-ancestral.md secao 4).
# Ameaca, ReacaoImpacto, ReacaoImpactoVoo, FugaDecolando, Derrota, DerrotaEmVoo, Derrotada (laco parado = DerrotaFim).
# ---------------------------------------------------------------- AMEACA: asas em capa (arco a frente), corpo ericado, cabeca baixa balancando
CAPA_E = quats_de({"BracoAsa": [(Y, R(-20)), (Z, R(-38))], "AntebracoAsa": [(Z, R(-30)), (Y, R(10))], "MaoAsa": [(Z, R(-24)), (Y, R(12))], "Primarias": [(Z, R(-10)), (Y, R(8))]})
CAPA = {"E": CAPA_E, "D": espelha(CAPA_E)}
DUR_AME = 3.0
def c_ameaca(t):
    r, raiz = base_rep(); k = suave(t / 0.70) * (1 - suave((t - 2.25) / 0.7))   # (r2: abrindo em 0,45 s a asa girava 52 graus por quadro)
    soma(r, "Coluna1", [(X, R(6) * k)]); soma(r, "Coluna2", [(X, R(10) * k)])          # inclina para o intruso
    sw = math.sin(2 * math.pi * (t - 0.4) / 0.9) * suave((t - 0.4) / 0.3) * k            # cabeca baixa balancando de lado
    sib = pulso(t, 0.95, 0.35) + pulso(t, 1.75, 0.35)                                     # dois avancos de cabeca (silvo)
    soma(r, "Pescoco", [(X, R(14) * k + R(10) * sib)]); soma(r, "Pescoco2", [(Z, R(10) * sw), (X, R(-4) * k)])
    soma(r, "Cabeca", [(X, R(-10) * k - R(6) * sib), (Z, R(8) * sw), (Y, R(-10) * sw)])
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-28) * k)])                                # tufos deitados (raiva)
    soma(r, "Cauda", [(X, R(12) * k)]); soma(r, "CaudaLequeE", [(Y, R(-16) * k)]); soma(r, "CaudaLequeD", [(Y, R(16) * k)])   # cauda em leque
    def asa_t(l, nm):
        f1 = suave(k * 2); f2 = suave(k * 2 - 1)                    # abre pela horizontal e so entao forma o arco (mesmo caminho de volta)
        return sq(sq(FECHADA[nm + l], Quaternion(), f1), CAPA[l][nm], f2)
    return r, raiz + V((0, -0.006 * k, 0.012 * k)), {}, {"asa_q": asas_q(asa_t)}
# ---------------------------------------------------------------- REACAO AO IMPACTO pousada (golpe de frente)
DUR_REA = 0.9
def golpe(t, t0=0.0):
    """envelope de impacto: sobe em 0,06 s e amortece"""
    u = t - t0
    return 0.0 if u <= 0 else (u / 0.06 if u < 0.06 else math.exp(-(u - 0.06) / 0.18))
def c_reacao(t):
    r, raiz = base_rep(); g = golpe(t) * (1 - suave((t - 0.55) / 0.35))
    soma(r, "Coluna2", [(X, R(-10) * g)]); soma(r, "Coluna1", [(X, R(-5) * g)])          # tronco joga para tras
    soma(r, "Pescoco", [(X, R(-10) * g)]); soma(r, "Cabeca", [(X, R(-12) * g), (Z, R(9) * g)])
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-22) * g)])
    soma(r, "Cauda", [(X, R(8) * g)])
    palpebras(r, piscada(t, 0.02, 0.20))                                                 # pisca no golpe
    def asa_t(l, nm): return sq(FECHADA[nm + l], MEIO_ABERTA_E[nm] if l == "E" else ASA_D(MEIO_ABERTA_E)[nm], 0.9 * g)   # asas saltam do corpo
    return r, raiz + V((0, 0.018 * g, -0.008 * g)), {}, {"asa_q": asas_q(asa_t)}
# ---------------------------------------------------------------- REACAO AO IMPACTO em voo: BaterAsas q0 -> BaterAsas q0 (2 batidas)
DUR_RV = 2 * T_BAT
def c_reacao_voo(t):
    g = golpe(t) * (1 - suave((t - 0.45) / 0.3))
    amp = 1.0 - 0.65 * g                                            # batida desorganiza
    r, raiz = corpo_voo(t, t / T_BAT, amp, 0.0, bank=R(-22) * g, giro_cab=R(10) * g)
    soma(r, "Raiz", [(X, R(-14) * g)])                               # golpe levanta o peito (perde sustentacao)
    for l in PES: asa_rots(r, l, braco=[(Y, R(-28) * g)], mao=[(Z, R(18) * g)])        # asas se debatem para cima
    soma(r, "Cabeca", [(X, R(-10) * g)])
    palpebras(r, piscada(t, 0.02, 0.20))
    cai = -0.05 * pulso(t, 0.05, 0.7)                                # perde altura e recupera
    return r, raiz + V((0, 0.02 * g, cai)), {}, ext_voo()
def v_reacao_voo(t): return V_BAT * (1 - 0.45 * pulso(t, 0.0, DUR_RV))
# ---------------------------------------------------------------- FUGA DECOLANDO: Repouso q0 -> BaterAsas q0 (sobressalto + decolagem mais rapida)
A_FUGA = 0.5; DT_FUGA = DUR_DEC - round((DUR_DEC - T_SAI * (1 - A_FUGA)) * FPS) / FPS; L_FUGA = A_FUGA * T_SAI + 0.25
def tau_fuga(t): return t + DT_FUGA * suave(t / L_FUGA)                 # chao comprimido, voo no tempo normal (sem estalo de velocidade)
DUR_FUG = round((DUR_DEC - DT_FUGA) * FPS) / FPS        # quadro final cai exatamente no fim do Decolar (fase inteira da batida)
def c_fuga(t):
    r, raiz, pes, ext = c_decolar(tau_fuga(t))
    al = pulso(t, 0.0, 0.40)                                         # sobressalto: corpo afina, tufos sobem, cabeca da um tranco
    soma(r, "Cabeca", [(X, R(-8) * al), (Z, R(-12) * al)])
    for l in "ED": soma(r, "Tufo" + l, [(X, R(14) * al)])
    return r, raiz, pes, ext
def v_fuga(t): return v_decolar(tau_fuga(t))
# ---------------------------------------------------------------- DERROTA (pose final comum): deitada sobre o lado E
TH_LADO = R(84); Z_LADO = float(os.environ.get("CORUJA_Z_LADO", "0.219")); X_LADO = 0.10
PIVO_PE = V((float(os.environ.get("CORUJA_PIVO_X", "0.13")), 0.0, 0.0))     # borda de fora do pe E (eixo do tombo)
MORTA = {"Coxa": [(X, R(-25))], "Tibia": [(X, R(35))], "Tarso": [(X, R(-20))], "Dedos": [(X, R(-75))]}   # pernas soltas, garras fechadas
def fk_mix(A_, B_, w): return {k: [(e, a * (1 - w)) for e, a in A_.get(k, [])] + [(e, a * w) for e, a in B_.get(k, [])] for k in set(A_) | set(B_)}
ASA_SUP = {nm: FECHADA[nm + "D"].slerp(Quaternion(), float(os.environ.get("CORUJA_ASA_SUP", "0.12"))) for nm in ASA_OSSOS}   # asa de cima solta sobre o corpo (r2: 0,38 ficava em pe como vela)
def pose_caida(cab=1.0, solta=1.0):
    """cab: cabeca apoiada (0..1); solta: asa de cima solta (0..1)"""
    r = {"Raiz": [(Y, TH_LADO)]}
    soma(r, "Pescoco", [(Y, R(14) * cab), (X, R(10) * cab)]); soma(r, "Pescoco2", [(Y, R(10) * cab)]); soma(r, "Cabeca", [(Y, R(12) * cab), (Z, R(-8) * cab)])
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-20))])
    soma(r, "Cauda", [(X, R(4))]); soma(r, "CaudaLequeE", [(Y, R(-6))]); soma(r, "CaudaLequeD", [(Y, R(6))])
    raiz = raiz_para(0.0, TH_LADO, (X_LADO, CENTRO.y, Z_LADO))
    asa = {"E": {nm: FECHADA[nm + "E"] for nm in ASA_OSSOS}, "D": {nm: sq(FECHADA[nm + "D"], ASA_SUP[nm], solta) for nm in ASA_OSSOS}}
    return r, raiz, asa
def c_derrotada(t):
    r, raiz, asa = pose_caida(); palpebras(r, 1.0)
    return r, raiz, {}, {"asa_q": asa, "pernas_fk": (MORTA, 1.0), "apoio": {l: False for l in PES}}
DUR_DER = 2.5
def c_derrota(t):
    r0, raiz0 = base_rep()
    g = golpe(t) * (1 - suave((t - 0.4) / 0.3))                       # golpe
    soma(r0, "Coluna2", [(X, R(-8) * g)]); soma(r0, "Cabeca", [(X, R(-10) * g)])
    ced = suave((t - 0.22) / 0.55)                                    # pernas cedem, corpo afunda e inclina para o lado
    soma(r0, "Cauda", [(X, R(16) * ced)])                            # (cauda subia pouco e raspava 1,1 cm no agachamento)
    soma(r0, "Coluna1", [(Y, R(8) * ced)]); soma(r0, "Pescoco", [(X, R(12) * ced)]); soma(r0, "Cabeca", [(X, R(10) * ced)])
    u = max(0.0, min(1.0, (t - 0.70) / 0.55)); tomb = u * u                 # tomba acelerando (gravidade)
    qq = pulso(t, 1.25, 0.30); tomb_q = tomb - 0.06 * qq               # quique pequeno ao bater
    rf, raizf, asaf = pose_caida(cab=suave((t - 1.35) / 0.55), solta=suave((t - 1.0) / 0.7))
    r = mistura(r0, rf, tomb_q)
    raiz_c = raiz0 + V((0, 0.012 * g, -0.015 * ced))
    # r2: tomba GIRANDO SOBRE A BORDA DO PE E (pivo no chao), pernas rigidas no corpo; so perto do fim o corpo vai para a pose
    # deitada final e as pernas soltam (antes as pernas giravam com o corpo e o pe E entrava 8,9 cm no chao)
    th = TH_LADO * tomb_q; C0 = V((0, CENTRO.y, CENTRO.z - 0.015 * ced))
    rel = C0 - PIVO_PE; rola = PIVO_PE + V((rel.x * math.cos(th) + rel.z * math.sin(th), rel.y, -rel.x * math.sin(th) + rel.z * math.cos(th)))
    b_ = suave((tomb - 0.35) / 0.65)
    alvo = rola.lerp(V((X_LADO, CENTRO.y, Z_LADO)), b_) + V((0, 0, 0.026 * math.sin(math.pi * b_)))   # (ponta da asa de baixo raspava 1,4 cm a 70 graus)
    raiz = (raiz_c + raiz_para(0.0, th, alvo) - raiz_para(0.0, 0.0, C0)).lerp(raiz_para(0.0, th, alvo), b_) + V((0, 0, 0.008 * qq))
    pre = {l: {nm: sq(FECHADA[nm + l], MEIO_ABERTA_E[nm] if l == "E" else ASA_D(MEIO_ABERTA_E)[nm], 0.6 * g + 0.35 * ced * (1 - tomb)) for nm in ASA_OSSOS} for l in PES}
    asa = {l: {nm: sq(pre[l][nm], asaf[l][nm], suave(tomb / (0.45 if l == "E" else 0.8))) for nm in ASA_OSSOS} for l in PES}   # asa de baixo cola no corpo antes de tocar o chao
    fk = suave(tomb / 0.10)                                           # pernas presas ao corpo (rigidas) ao comecar a tombar
    raiz = raiz + V((0, 0, (0.015 * ced - BASE_Z + 0.007) * suave(tomb / 0.07) * (1 - b_)))   # perna rigida = comprimento de repouso: desfaz a flexao (o pe afundava 2,5 cm)
    palpebras(r, max(piscada(t, 0.02, 0.20), suave((t - 1.45) / 0.6)))
    pes = {}
    return r, raiz, pes, {"asa_q": asa, "pernas_fk": (fk_mix({}, MORTA, b_), fk), "apoio": {"E": b_ < 0.02, "D": tomb < 0.02}}
# ---------------------------------------------------------------- DERROTA EM VOO: BaterAsas q0 -> cai do ar -> DerrotaFim
DUR_DV = 2.1; T_G = 0.12; V0 = 0.6; GRAV = 9.8
def z_queda(t):
    u = max(0.0, t - T_G); return H_VOO + V0 * u - 0.5 * GRAV * u * u
T_CHAO = T_G + (V0 + math.sqrt(V0 * V0 + 2 * GRAV * (H_VOO - Z_LADO))) / GRAV          # toque no chao
def c_derrota_voo(t):
    g = golpe(t) * (1 - suave((t - 0.35) / 0.3))
    amp = 1.0 - suave(t / 0.30)                                      # para de bater
    rv, _rz = corpo_voo(t, t / T_BAT, amp, 0.0)
    for l in PES: asa_rots(rv, l, braco=[(Y, R(-25) * g)])
    w = suave(t / T_CHAO) ** 1.3                                       # corpo tomba no ar ate a pose de deitada
    qq = pulso(t, T_CHAO, 0.30)
    rf, _raizf, asaf = pose_caida(cab=suave((t - T_CHAO - 0.1) / 0.6), solta=suave((t - T_CHAO) / 0.6))
    r = mistura(rv, rf, w)
    cb = math.cos(2 * math.pi * t / T_BAT) * amp                    # mesma oscilacao do corpo_voo (emenda com BaterAsas q0)
    th_x = (PITCH + R(3) * cb) * (1 - w) + R(-10) * g; th_y = TH_LADO * w - R(8) * qq; r["Raiz"] = [(X, th_x), (Y, th_y)]
    zc = (max(Z_LADO, z_queda(t)) - 0.012 * cb * (1 - w)) if t < T_CHAO else Z_LADO + 0.012 * qq
    raiz = raiz_para(th_x - R(3) * cb * (1 - w), th_y, (X_LADO * w, CENTRO.y * w, zc))   # como no corpo_voo: a oscilacao de 3 graus nao desloca o centro
    asa = {l: {nm: sq(Quaternion(), asaf[l][nm], suave((t - 0.10) / (T_CHAO - 0.10))) for nm in ASA_OSSOS} for l in PES}
    palpebras(r, max(piscada(t, 0.02, 0.20), suave((t - T_CHAO - 0.2) / 0.6)))
    return r, raiz, {}, {"asa_q": asa, "pernas_fk": (fk_mix(RECOLHIDA, MORTA, suave(t / T_CHAO)), 1.0), "apoio": {l: False for l in PES}}
def v_derrota_voo(t): return V_BAT * (1 - suave(t / (T_CHAO + 0.35)))
REF_EXTRA_C["DerrotaFim"] = (c_derrotada, 0.0)
CLIPES.update({"Ameaca": (c_ameaca, DUR_AME, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "ReacaoImpacto": (c_reacao, DUR_REA, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "ReacaoImpactoVoo": (c_reacao_voo, DUR_RV, False, 0.0, 0.0, "BaterAsas q0", "BaterAsas q0", v_reacao_voo),
               "FugaDecolando": (c_fuga, DUR_FUG, False, 0.0, 0.0, "Repouso q0", "BaterAsas q0", v_fuga),
               "Derrota": (c_derrota, DUR_DER, False, 0.0, 0.0, "Repouso q0", "DerrotaFim"),
               "DerrotaEmVoo": (c_derrota_voo, DUR_DV, False, 0.0, 0.0, "BaterAsas q0", "DerrotaFim", v_derrota_voo),
               "Derrotada": (c_derrotada, 1.0, True, 0.0, 0.0, "laco", "laco")})
print("LOTE_D", {k: round(CLIPES[k][1], 3) for k in ("Ameaca", "ReacaoImpacto", "ReacaoImpactoVoo", "FugaDecolando", "Derrota", "DerrotaEmVoo", "Derrotada")}, "T_CHAO", round(T_CHAO, 3))
