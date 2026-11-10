# Clipes PROPRIOS dos poderes do Urso Silvestre v2 (04/11/2026). Executado dentro do anim_urso.py (exec em globals())
# so quando URSO_PODERES=1: usa os mesmos auxiliares (suave, janela, degrau, R, X/Y/Z, V) e acrescenta clipes novos ao
# CLIPES sem alterar os 18 aprovados. Numeros de tempo/angulo = PARAMETROS DE LABORATORIO, nao regra do jogo.
# Uso: URSO_PODERES=1 URSO_ANIM_SAIDA=poderes/CR_Urso_v2_Anim_Poderes.blend \
#      blender -b CR_Urso_v2_Rig.blend -P anim_urso.py -- poderes/clipes GolpeColossal

# v2 (04/11, pedido do usuario: "antes de bater no chao ele deve dar um rugido ... levantar e descer com tudo"):
# ergue mais alto (pelve -40), RUGE la em cima (boca aberta, cabeca para cima, tremor) e so entao desaba com forca.
# v1 (contato em 1,10 s, sem rugido, pelve -26) ficou registrada no LEIA-ME.
T_RUG_GC = 1.00                      # inicio do rugido (som do rugido)
T_IMP_GC = 58 / 30                   # contato das patas com o chao (s) -> dano, rachaduras, tremor e som do impacto
DUR_GC = 3.2
def c_golpe_colossal(t):
    """preparacao (peso para tras, agacha) -> ergue bem o tronco e as duas patas dianteiras -> RUGE no alto (boca
    aberta, cabeca e pescoco para cima, tremor) -> desaba com tudo e bate as duas patas juntas no chao (T_IMP_GC) ->
    o corpo absorve o impacto (afunda, coluna cede, cabeca baixa) -> recupera, patas voltam com um passo cada"""
    r = {}; pes = {}
    ant = janela(t, 0.0, 0.55, 0.40, 0.20)                                  # preparacao
    sobe = suave((t - 0.40) / 0.60)
    t_q = T_IMP_GC - 0.20                                                   # comeca a desabar
    queda = max(0.0, min(1.0, (t - t_q) / 0.20)) ** 2                       # descida acelerada ate o contato
    up = sobe * (1 - queda)
    rug = janela(t, T_RUG_GC - 0.10, t_q + 0.10, 0.22, 0.20)                # rugido no alto
    tre = R(1.3) * math.sin(2 * math.pi * t * 11) * rug
    imp = janela(t, T_IMP_GC - 0.02, T_IMP_GC + 0.75, 0.16, 0.45)           # absorcao do impacto
    r["Pelve"] = [(X, R(-40) * up + R(3) * ant)]
    for l_ in "ED": r["Coxa" + l_] = [(X, R(40) * up)]
    r["Coluna1"] = [(X, R(4) * imp)]; r["Coluna2"] = [(X, R(-6) * up - R(3) * rug + R(8) * imp)]; r["Coluna3"] = [(X, R(-4) * up + R(6) * imp)]
    # tronco quase em pe: o pescoco traz a cabeca para a FRENTE (o rugido le de frente, nao para o ceu)
    r["Pescoco"] = [(X, R(10) * ant + R(16) * up - R(6) * rug + tre + R(14) * imp)]
    r["Pescoco2"] = [(X, R(6) * up - R(4) * rug)]
    r["Cabeca"] = [(X, R(6) * ant + R(8) * up - R(4) * rug + tre + R(9) * imp)]
    r["Mandibula"] = [(X, R(40) * rug + R(14) * imp + tre * 2)]
    r["OrelhaE"] = [(X, R(-30) * max(up, imp))]; r["OrelhaD"] = [(X, R(-30) * max(up, imp))]
    # dianteiras: sobem com o tronco, descem para um ponto um pouco a frente e ficam pregadas; recuperacao em passos
    frente = suave((t - t_q) / 0.20)
    for p_, (a, b), sx in (("MaoE", (T_IMP_GC + 0.40, T_IMP_GC + 0.75), 1), ("MaoD", (T_IMP_GC + 0.60, T_IMP_GC + 0.95), -1)):
        s, h = degrau(t, a, b, 0.30)
        y = -0.95 * frente * (1 - s); z = ALT_PATA_GC * up + h
        pes[p_] = V((0.08 * sx * up, y + 1.30 * up, z))
    raiz = V((0, 0.25 * ant + 0.55 * up - 0.15 * imp, -0.22 * ant - 0.42 * imp))
    return r, raiz, pes, {}
ALT_PATA_GC = float(os.environ.get("ALT_PATA_GC", "6.2"))
CLIPES["GolpeColossal"] = (c_golpe_colossal, DUR_GC, False, 0.0, None)
EVENTOS_CLIPE["GolpeColossal"] = {"rugido_s": T_RUG_GC, "impacto_s": round(T_IMP_GC, 4), "impacto_quadro": int(round(T_IMP_GC * FPS))}

# ------------------------------------------------------------------ Rugido Protetor (Etapa 2, 04/11)
# Rugido de urso pesado (nao reaproveita o de dragao nem o Rugir aprovado): inspira e EXPANDE o peito (coluna sobe,
# tronco cresce para tras e para cima, orelhas para tras) -> projeta a cabeca para a FRENTE e ruge com a boca bem
# aberta, varrendo devagar de um lado para o outro (cobre a area do treinador) -> recupera. Patas plantadas.
T_RUG_RP = 0.70                      # inicio do rugido (som)
T_EFEITO_RP = 1.00                   # pico do rugido -> o servidor aplica os bonus
DUR_RP = 3.0
def c_rugido_protetor(t):
    r = {}
    insp = janela(t, 0.0, 0.85, 0.55, 0.25)                                 # inspira: peito expande
    rug = janela(t, T_RUG_RP - 0.10, 2.35, 0.20, 0.45)                       # rugido
    rec = janela(t, 2.2, DUR_RP, 0.35, 0.45)                                 # recuperacao (assenta)
    tre = R(1.4) * math.sin(2 * math.pi * t * 10) * rug
    varre = R(14) * math.sin(math.pi * (t - T_RUG_RP) / 1.6) * rug          # varredura lateral lenta
    r["Pelve"] = [(X, R(-2) * insp)]
    r["Coluna1"] = [(X, R(-1.5) * insp)]
    r["Coluna2"] = [(X, R(-3) * insp - R(1) * rug + R(2) * rec)]
    r["Coluna3"] = [(X, R(2.5) * insp + R(3) * rug)]   # compensa: ombros ficam sobre as patas plantadas
    r["Pescoco"] = [(X, R(-10) * insp - R(8) * rug + tre), (Z, varre * 0.6)]   # pescoco estica para a frente e um pouco para cima
    r["Pescoco2"] = [(X, R(-4) * insp + R(2) * rug), (Z, varre * 0.4)]
    r["Cabeca"] = [(X, R(-6) * insp - R(10) * rug + tre), (Z, varre * 0.3)]   # focinho para cima: boca a vista de frente
    r["Mandibula"] = [(X, R(4) * insp + R(46) * rug + tre * 2)]
    r["OrelhaE"] = [(X, R(-30) * max(insp, rug))]; r["OrelhaD"] = [(X, R(-30) * max(insp, rug))]
    r["Cauda1"] = [(X, R(-10) * rug)]
    raiz = V((0, 0.0, -0.14 * insp - 0.10 * rug - 0.10 * rec))   # o peito expande pela COLUNA; a raiz quase nao sobe (patas plantadas)
    return r, raiz, {}, {}
CLIPES["RugidoProtetor"] = (c_rugido_protetor, DUR_RP, False, 0.0, None)
EVENTOS_CLIPE["RugidoProtetor"] = {"rugido_s": T_RUG_RP, "efeito_s": T_EFEITO_RP}

# ------------------------------------------------------------------ Carga Selvagem (Etapa 3, 04/11; proposta aprovada)
# 3 clipes NO LUGAR (o servidor move o urso): CargaInicio (antecipacao + aceleracao) -> CargaCorrida (loop, corrida
# pesada) -> CargaImpacto (ombrada + freada curta + recuperacao). Sem acerto: o jogo usa a Frenagem aprovada.
# Corrida pesada: galope de cadencia maior (0,34 s) e menos tempo de apoio; cabeca baixa, ombros a frente, mais baixa.
# V_CAR (~29 studs/s) e a velocidade em que as patas nao escorregam = PARAMETRO TECNICO, nao regra do jogo.
T_CAR, L_CAR, AP_CAR = 0.34, 3.0, 0.30
V_CAR = L_CAR / (AP_CAR * T_CAR); PERF_CAR = Perfil(lambda t: V_CAR)
# v3 (05/11, pedido do usuario: "na corrida abaixe a cabeca e deixe o ombro mais exposto na direcao do alvo"): a corrida
# ja vem com o tronco TORCIDO, ombro direito apontado ao alvo (Coluna3/Coluna2 em Z), e a cabeca BAIXA e recolhida para o
# lado oposto (o pescoco contra-gira), deixando o ombro na frente. v2 (so cabeca baixa 12/4) registrada no LEIA-ME.
TORS_CAR = float(os.environ.get("TORS_CAR", "12")); CAB_BAIXA = float(os.environ.get("CAB_BAIXA", "30")); TORS_C2 = float(os.environ.get("TORS_C2", "0.5"))
LEV_PESC = float(os.environ.get("LEV_PESC", "4")); LEV_CAB = float(os.environ.get("LEV_CAB", "0"))
PA_A = float(os.environ.get("PA_A", "0.12")); PA_B = float(os.environ.get("PA_B", "0.12")); PA_2 = float(os.environ.get("PA_2", "0.34"))
MD_H = float(os.environ.get("MD_H", "1.6")); ME_H = float(os.environ.get("ME_H", "0.7")); ME_X = float(os.environ.get("ME_X", "0.35")); ME_T = float(os.environ.get("ME_T", "0.55"))
LEV_Z = float(os.environ.get("LEV_Z", "0.12")); LEV_P = float(os.environ.get("LEV_P", "5"))
OMB_Z = float(os.environ.get("OMB_Z", "12")); LEV_RZ = float(os.environ.get("LEV_RZ", "6")); LEV_C3 = float(os.environ.get("LEV_C3", "10"))
def corpo_carga(r, u, k):
    corpo_galope(r, u, FASE_GALOPE, 11 * k)
    r["Coluna3"] = r["Coluna3"] + [(X, R(6) * k), (Z, R(TORS_CAR) * k)]   # ombros a frente, ombro direito lidera
    r["Coluna2"] = r.get("Coluna2", []) + [(Z, R(TORS_CAR * TORS_C2) * k)]
    r["Pescoco"] = r["Pescoco"] + [(X, R(CAB_BAIXA) * k), (Z, R(-TORS_CAR * 1.4) * k)]; r["Cabeca"] = r["Cabeca"] + [(X, R(10) * k), (Z, R(-4) * k)]   # cabeca baixa, recolhida
    r["OrelhaE"] = [(X, R(-34) * k)]; r["OrelhaD"] = [(X, R(-34) * k)]
    r["Cauda1"] = [(X, R(-8) * k), (Z, R(3) * math.sin(2 * math.pi * u))]
def z_carga(u, k): return BASE_Z + (-0.85 - BASE_Z) * k + 0.18 * k * math.sin(2 * math.pi * (u - 0.05))
def c_carga_corrida(t):
    r = {}; pes = {}; ext = {"rot_pe": {}}; u = t / T_CAR
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(t, fase, T_CAR, AP_CAR, 0.75, lambda tt: L_CAR, PERF_CAR); ALT_UL[k_] = ALT_UL.get('_ultimo', 0.48); rot_sola(ext, k_, uu)
    corpo_carga(r, u, 1.0)
    return r, V((0, 0, z_carga(u, 1.0))), pes, ext
# inicio: abaixa e joga o peso para tras (0,36 s), depois 2 ciclos acelerando; o ultimo quadro = quadro 0 da CargaCorrida
T0_CAR = 0.36; DUR_CAR_INI = T0_CAR + 2 * T_CAR
def k_car(t): return suave((t - T0_CAR) / (1.6 * T_CAR))
PERF_CAR_INI = PerfDesloc(Perfil(lambda t: V_CAR * k_car(t)), T0_CAR)
def c_carga_inicio(t):
    r = {}; pes = {}; ext = {"rot_pe": {}}; k = k_car(t); ag = janela(t, 0.0, T0_CAR + 0.12, 0.26, 0.18)
    tt = t - T0_CAR
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(tt, fase, T_CAR, AP_CAR, 0.75 * k, lambda x: L_CAR * k_car(x + T0_CAR), PERF_CAR_INI)
        ALT_UL[k_] = ALT_UL.get('_ultimo', 0.48); rot_sola(ext, k_, uu if k > 0.02 else 0.0)
    corpo_carga(r, tt / T_CAR, k)
    # v3b (05/11, pedido do usuario: "ao ativar a habilidade o urso empurra o chao, fazendo-o rachar e sai correndo"):
    # agacha mais fundo nas traseiras e, em T_EMP_CAR, EMPURRA o chao (traseiras estendem, o corpo dispara para a frente
    # e um pouco para cima, a cabeca afunda) -> evento empurrao_s: o cliente racha o chao atras das patas traseiras
    emp = janela(t, T_EMP_CAR - 0.05, T_EMP_CAR + 0.22, 0.05, 0.16)
    r["Pelve"] = r["Pelve"] + [(X, R(8) * ag - R(EMP_P) * emp)]; r["Pescoco"] = r["Pescoco"] + [(X, R(14) * ag + R(6) * emp)]; r["Cabeca"] = r["Cabeca"] + [(X, R(4) * ag)]
    r["OrelhaE"] = [(X, R(-34) * max(k, ag))]; r["OrelhaD"] = [(X, R(-34) * max(k, ag))]
    return r, V((0, 0.35 * ag - EMP_Y * emp, z_carga(tt / T_CAR, k) - AG_Z * ag + EMP_Z * emp)), pes, ext
T_EMP_CAR = T0_CAR - 0.02
EMP_P = float(os.environ.get("EMP_P", "6")); EMP_Y = float(os.environ.get("EMP_Y", "0.35")); EMP_Z = float(os.environ.get("EMP_Z", "0.15")); AG_Z = float(os.environ.get("AG_Z", "0.42"))
# impacto: comeca no quadro 0 da CargaCorrida; OMBRADA em T_IMP_CS (o servidor derruba o alvo), a passada encolhe
# rapido, o peso senta nas traseiras, o urso sacode a cabeca e volta ao repouso
# v2 (04/11, pedido do usuario: "mais forte"): contato passa a 0,20 s para caber a ARMACAO (ombro e cabeca recuam e
# torcem para o lado oposto), o tronco DISPARA para a frente com o ombro direito na ponta (raiz -1,1, torcao 18 graus) e
# um TRANCO de recuo curto mostra que bateu em algo. v1 (contato 0,10 s, raiz -0,55, torcao 10) registrada no LEIA-ME.
T_IMP_CS = 0.20; DUR_CAR_IMP = 1.7
PASSO_OMB = float(os.environ.get("PASSO_OMB", "1.4"))
def k_imp(t): return 1 - suave((t - 0.16) / 0.42)                      # mantem a velocidade ate o contato
PERF_IMP = Perfil(lambda t: V_CAR * k_imp(t))
def c_carga_impacto(t):
    r = {}; pes = {}; ext = {"rot_pe": {}}; k = k_imp(t)
    arm_ = janela(t, 0.0, T_IMP_CS - 0.03, 0.14, 0.05)                    # armacao: recua e torce ao contrario
    omb = suave((t - (T_IMP_CS - 0.06)) / 0.06) * (1 - suave((t - (T_IMP_CS + 0.08)) / 0.40))   # disparo rapido, solta devagar
    tr = janela(t, T_IMP_CS, T_IMP_CS + 0.30, 0.05, 0.22)                 # tranco de recuo (bateu)
    s = janela(t, 0.40, DUR_CAR_IMP, 0.25, 0.55)                           # senta o peso / freia
    sac = janela(t, 0.85, 1.45, 0.12, 0.18)                                 # sacode a cabeca
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(t, fase, T_CAR, AP_CAR, 0.75 * max(k, 0.0) ** 0.7, lambda x: L_CAR * k_imp(x), PERF_IMP)
        ALT_UL[k_] = ALT_UL.get('_ultimo', 0.48); rot_sola(ext, k_, uu if k > 0.02 else 0.0)
    # a dianteira do ombro que bate (MaoD) da um passo a frente junto com a ombrada e volta no fim da freada
    s1, h1 = degrau(t, T_IMP_CS - PA_A, T_IMP_CS + PA_B, 0.45); s2, h2 = degrau(t, 0.62, 0.62 + PA_2, 0.35)
    pes["MaoD"] = pes["MaoD"] + V((0.10 * s1 * (1 - s2), -PASSO_OMB * s1 * (1 - s2), h1 + h2))
    # v3: no contato o ombro SOBE por baixo do alvo (LEVANTA): o peito empina (Pelve/Coluna em -X), o ombro rola para
    # cima e a cabeca acompanha o arranco; a dianteira DIREITA (lado do ombro) sobe junto, a esquerda segura o peso
    lev = janela(t, T_IMP_CS - 0.02, T_IMP_CS + 0.50, 0.10, 0.30); lz = LEV_Z * lev
    pes["MaoD"] = pes["MaoD"] + V((0, 0, MD_H * lev))
    sL, hL = degrau(t, T_IMP_CS - 0.02, T_IMP_CS + ME_T, ME_H)
    pes["MaoE"] = pes["MaoE"] + V((0, -ME_X * sL * (ME_H > 0), hL))
    corpo_carga(r, t / T_CAR, k)
    r["Coluna3"] = r["Coluna3"] + [(Z, R(-5) * arm_ + R(OMB_Z) * omb + R(LEV_RZ) * lev), (X, R(-3) * arm_ + R(5) * omb - R(3) * tr - R(LEV_C3) * lev)]   # ombro direito lidera e sobe
    r["Coluna2"] = r.get("Coluna2", []) + [(Z, R(-3) * arm_ + R(6) * omb), (X, R(4) * s - R(5) * lev)]
    r["Pescoco"] = r["Pescoco"] + [(Z, R(6) * arm_ - R(16) * omb), (X, R(-8) * arm_ + R(10) * omb - R(6) * tr - R(8) * s - R(LEV_PESC) * lev)]
    r["Cabeca"] = r["Cabeca"] + [(Z, R(-8) * omb), (X, R(6) * omb - R(6) * tr - R(4) * s - R(LEV_CAB) * lev), (Y, R(9) * math.sin(2 * math.pi * (t - 0.85) / 0.2) * sac)]
    r["Pelve"] = r["Pelve"] + [(X, R(-6) * s - R(4) * omb - R(LEV_P) * lev)]
    r["OrelhaE"] = [(X, R(-38) * max(k, omb, sac))]; r["OrelhaD"] = [(X, R(-38) * max(k, omb, sac))]
    r["Mandibula"] = [(X, R(12) * omb + R(6) * tr)]
    raiz = V((0.10 * omb, 0.30 * arm_ - 1.10 * omb + 0.45 * tr + 0.30 * s - 0.20 * lev * LEV_Z / 0.30, z_carga(t / T_CAR, k) - 0.10 * arm_ - 0.18 * omb + 0.10 * tr - 0.25 * s + lz))
    return r, raiz, pes, ext
CLIPES["CargaInicio"] = (c_carga_inicio, DUR_CAR_INI, False, 0.0, lambda t: V_CAR * k_car(t))
CLIPES["CargaCorrida"] = (c_carga_corrida, T_CAR, True, V_CAR, None)
CLIPES["CargaImpacto"] = (c_carga_impacto, DUR_CAR_IMP, False, 0.0, lambda t: V_CAR * k_imp(t))
COM_ALTURA_PROPRIA.update({"CargaInicio", "CargaCorrida", "CargaImpacto"})
EVENTOS_CLIPE["CargaImpacto"] = {"impacto_s": T_IMP_CS, "impacto_quadro": int(round(T_IMP_CS * FPS))}
EVENTOS_CLIPE["CargaInicio"] = {"empurrao_s": round(T_EMP_CAR, 4), "empurrao_quadro": int(round(T_EMP_CAR * FPS))}
