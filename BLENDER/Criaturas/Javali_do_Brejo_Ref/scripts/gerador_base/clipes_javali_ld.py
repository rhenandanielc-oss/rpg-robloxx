# ================================================================== LOTE D do Javali Silvestre (13/11/2026): defesa e derrota.
# ESTUDO DE ANIMACAO: comportamento defensivo ("territorial, investe quando acuado") e [PROPOSTA] da especie; NAO ha dano,
# alcance, hitbox, duracao de estado, loot nem regra de coleta aqui. Carregado com JAVALI_LD=1 (liga tambem B e C).
# Ameaca (pateia e firma), Investida (arranca de cabeca baixa ate o galope de investida), RecuperacaoInvestida (freia, ergue o
# focinho, termina no fim do Alerta), ReacaoImpacto (encolhe e recupera o apoio), Derrota (perde a sustentacao, dobra as
# pernas e cai de lado, corpo e cabeca apoiados) e Derrotado (pose final mantida). Numeros sao [PROPOSTA].
# Recursos do gerador usados: pes com apoio=False (patear/recuar), ext["fk_pernas"] (pernas soltas em FK sobre a pose do
# Repouso q0), ext["assentar"] (ponto mais baixo encosta no chao) e ext["cabeca_chao"] (cabeca desce ate apoiar).
def pata_no_ar(k_, t, t0, dur, dy, alt):
    """casco sai do chao, vai dy (u, +Y = para tras) num arco de altura alt e pousa; (deslocamento, apoiado?)"""
    u = (t - t0) / dur
    if u <= 0: return V((0, 0, 0)), True
    if u >= 1: return V((0, dy, 0)), True
    return V((0, dy * suave(u), alt * math.sin(math.pi * u) ** 0.8)), False
# ---------------------------------------------------------------- AMEACA: pateia 2x, firma os apoios, peso a frente, cabeca baixa
DUR_AM = 1.8
def pose_ameaca(r, k):
    soma(r, "Pescoco", [(X, R(9) * k)]); soma(r, "Pescoco2", [(X, R(3) * k)]); soma(r, "Cabeca", [(X, R(5) * k)])   # presas a frente
    soma(r, "Coluna3", [(X, R(2.5) * k)]); soma(r, "Pelve", [(X, R(-2.5) * k)])          # peso nas dianteiras, garupa firme
    soma(r, "OrelhaE", [(X, R(-22) * k)]); soma(r, "OrelhaD", [(X, R(-22) * k)])          # orelhas para tras
    soma(r, "Cauda1", [(X, R(-28) * k)]); soma(r, "Cauda2", [(X, R(-10) * k)])           # cauda erguida e dura
def c_ameaca(t):
    r = base_rep(); k = suave(t / 0.5); pose_ameaca(r, k); pes = {}; ext = {"apoio": {}}
    tr = 0.0
    for t0 in (0.55, 0.95):                                       # pateia: a dianteira D raspa o chao para tras duas vezes
        d1, a1 = pata_no_ar("QuartelaD", t, t0, 0.18, 0.06, 0.045); d2, a2 = pata_no_ar("QuartelaD", t, t0 + 0.18, 0.16, -0.06, 0.02)
        if not a1: pes["QuartelaD"] = d1; ext["apoio"]["QuartelaD"] = False
        elif not a2: pes["QuartelaD"] = V((0, 0.06, 0)) + d2; ext["apoio"]["QuartelaD"] = False
        tr += janela(t, t0 - 0.05, t0 + 0.40, 0.08, 0.1)
    soma(r, "Coluna3", [(Y, R(-1.5) * tr)])                         # peso sai da pata que pateia
    return r, REP0[1] + V((0.004 * tr, -0.012 * k, -0.010 * k)), pes, ext
# ---------------------------------------------------------------- INVESTIDA: empurra com as traseiras, galope de cabeca baixa
def corpo_investida(r, u, k=1.0):
    corpo_galope(r, u, k)
    soma(r, "Pescoco", [(X, R(7) * k)]); soma(r, "Cabeca", [(X, R(6) * k)])             # cabeca BAIXA, presas a frente
    soma(r, "OrelhaE", [(X, R(-10) * k)]); soma(r, "OrelhaD", [(X, R(-10) * k)])
    soma(r, "Cauda1", [(X, R(-12) * k)])
T0_INV = 0.20; DUR_INV = T0_INV + 3 * T_GAL                    # empurrao 0,2 s; 2 ciclos acelerando; 1 ciclo cheio
def k_inv(t): return suave((t - T0_INV * 0.5) / (2 * T_GAL))
PERF_INV = Perfil(lambda t: V_GAL * k_inv(t)); PERF_INV_G = PerfDesloc(PERF_INV, T0_INV)
def c_investida(t):
    r_ = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; k = k_inv(t); tt = t - T0_INV
    pernas_g(tt, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, lambda x: L_GAL * k_inv(x + T0_INV), PERF_INV_G, ext, pes, k_alt=k,
             kc=lambda x: k_inv(x + T0_INV), reach=True)
    corpo_investida(r_, tt / T_GAL, k)
    rA, zA, _p, _e = c_ameaca(DUR_AM); w = suave(t / (T0_INV + 0.6 * T_GAL)); r = mistura(rA, r_, w)
    emp = janela(t, 0.0, T0_INV + 0.15, 0.10, 0.12)                # empurra: garupa desce e projeta o corpo
    soma(r, "Pelve", [(X, R(-5) * emp)]); soma(r, "Coluna1", [(X, R(5) * emp)])
    z = Z_GAL * k + 0.015 * k * math.sin(2 * math.pi * (tt / T_GAL - 0.05)) + SUSP * k * math.cos(2 * math.pi * (tt / T_GAL - 0.93)) - 0.01 * emp
    return r, zA.lerp(V((0, 0, 0)), w) + V((0, 0, z)), pes, ext
# ---------------------------------------------------------------- RECUPERACAO: freia, levanta o focinho, reassenta (fim = AlertaFim)
T_ESP_R = T_GAL; T_DES_R = 0.75; DUR_RI = T_ESP_R + T_DES_R + 3 * T_GAL + 0.35
def k_ri(t): return 1 - suave((t - T_ESP_R) / T_DES_R)
PERF_RI = Perfil(lambda t: V_GAL * k_ri(t))
def c_recuperacao(t):
    r_ = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; k = k_ri(t)
    pernas_g(t, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, lambda x: L_GAL * k_ri(x), PERF_RI, ext, pes, k_alt=max(k, 0.0) ** 0.6, kc=k_ri, reach=True)
    corpo_investida(r_, t / T_GAL, k)
    ab = janela(t, T_ESP_R + 0.05, T_ESP_R + T_DES_R + 2 * T_GAL, 0.22, 0.45)   # absorve nas dianteiras
    soma(r_, "Pelve", [(X, R(2.5) * ab)]); soma(r_, "Coluna3", [(X, R(-1.5) * ab)])   # (mais forte afundava o boleto dianteiro 3 mm)
    rB, zB, _p, _e = c_alerta(DUR_AL); w = suave((t - T_ESP_R - 0.35 * T_DES_R) / (DUR_RI - T_ESP_R - 0.35 * T_DES_R - 0.05))
    r = mistura(r_, rB, w)
    z = Z_GAL * k + 0.015 * k * math.sin(2 * math.pi * (t / T_GAL - 0.05)) + SUSP * k * math.cos(2 * math.pi * (t / T_GAL - 0.93)) - 0.004 * ab
    return r, V((0, -0.006 * ab, z)).lerp(zB, w), pes, ext
# ---------------------------------------------------------------- REACAO AO IMPACTO: encolhe, recua uma dianteira, recupera
DUR_RE = 1.2
def c_reacao(t):
    r = base_rep(); pes = {}; ext = {"apoio": {}}
    g = suave(t / 0.08) if t < 0.08 else math.exp(-(t - 0.08) / 0.16) * math.cos(9.0 * (t - 0.08))   # golpe rapido + amortece (comeca em 0)
    g = g * (1 - suave((t - 0.75) / 0.4))
    soma(r, "Coluna2", [(X, R(-5) * g)]); soma(r, "Coluna3", [(X, R(-3) * g)]); soma(r, "Pelve", [(X, R(2) * g)])   # tronco contrai
    soma(r, "Pescoco", [(X, R(-9) * g), (Z, R(6) * g)]); soma(r, "Cabeca", [(X, R(-4) * g), (Z, R(4) * g)])       # pescoco recua e vira
    orl = janela(t, 0.05, 0.9, 0.08, 0.3)
    soma(r, "OrelhaE", [(X, R(-25) * orl)]); soma(r, "OrelhaD", [(X, R(-25) * orl)]); soma(r, "Cauda1", [(X, R(12) * orl)])
    d1, a1 = pata_no_ar("QuartelaE", t, 0.14, 0.20, 0.045, 0.03)     # recupera o apoio: a dianteira E da um passo curto para tras
    d2, a2 = pata_no_ar("QuartelaE", t, 0.62, 0.24, -0.045, 0.025)   # e volta ao lugar (pose estavel = Repouso q0)
    if not a1: pes["QuartelaE"] = d1; ext["apoio"]["QuartelaE"] = False
    elif 0.34 <= t < 0.62: pes["QuartelaE"] = V((0, 0.045, 0))
    elif not a2: pes["QuartelaE"] = V((0, 0.045, 0)) + d2; ext["apoio"]["QuartelaE"] = False
    return r, REP0[1] + V((0.006 * g, 0.022 * g, -0.008 * abs(g))), pes, ext
# ---------------------------------------------------------------- DERROTA: perde a sustentacao, dobra as pernas e cai de lado (E)
DUR_DER = 2.6
ROLA = R(84)                                                       # deita sobre o flanco esquerdo (+X vai para o chao)
def fk_derrota(t):
    tras = suave(t / 0.55); dian = suave((t - 0.35) / 0.55); dei = suave((t - 0.95) / 0.75)
    fk = {}
    for l, sx in (("E", 1), ("D", -1)):
        # traseiras dobram primeiro (garupa cai), dianteiras depois (carpo dobra); deitado: pernas relaxam meio dobradas
        fk["Coxa" + l] = [(X, R(-26) * tras + R(8) * dei)]; fk["Perna" + l] = [(X, R(48) * tras - R(16) * dei)]
        fk["CanelaTras" + l] = [(X, R(-34) * tras + R(12) * dei)]; fk["QuartelaTras" + l] = [(X, R(15) * tras)]
        fk["Braco" + l] = [(X, R(16) * dian - R(4) * dei)]; fk["Antebraco" + l] = [(X, R(-22) * dian + R(8) * dei)]
        fk["Canela" + l] = [(X, R(62) * dian - R(22) * dei)]; fk["Quartela" + l] = [(X, R(20) * dian)]
        # deitado: as de baixo (E) quase paralelas ao chao, as de cima (D) caem sobre elas; calibrado p/ tronco, pernas e cabeca
        # apoiados juntos (13/11: -14/-24 deixava o tronco 6 cm no ar escorado nas pernas; -4/-16: tronco 0, pernas 0,24, cabeca 0,4 cm)
        for o in ("Braco" + l, "Coxa" + l): fk[o] = fk[o] + [(Y, R(-4 if l == "E" else -16) * dei)]
    return fk
def c_derrota(t):
    r = base_rep(); dei = suave((t - 0.95) / 0.75); cai = suave((t - 0.25) / 0.9)
    ass = 1.0                                                     # sempre assentado: o ponto mais baixo toca o chao
    rol = ROLA * dei + R(5) * math.sin(math.pi * min(1.0, max(0.0, (t - 1.7) / 0.35))) * dei   # pequeno quique ao bater no chao
    r["Raiz"] = [(Y, rol)]                                          # inclinacao da garupa: resolvida por quadro (ext["nivelar"])
    soma(r, "Pescoco", [(X, R(10) * cai)]); soma(r, "Pescoco2", [(X, R(4) * cai)])   # cabeca pende ao perder forca
    soma(r, "Coluna2", [(X, R(3) * cai)]); soma(r, "OrelhaE", [(X, R(-15) * cai)]); soma(r, "OrelhaD", [(X, R(-15) * cai)])
    soma(r, "Cauda1", [(X, R(15) * cai)])                             # cauda cai
    cab = suave((t - 1.55) / 0.6)                                     # cabeca termina apoiada (chega por ultimo)
    ext = {"fk_pernas": fk_derrota(t), "assentar": ass, "apoio": {k_: False for k_ in PATAS}, "cabeca_chao": (0.004, cab, Z),
           "nivelar": 1 - suave((t - 1.25) / 0.45)}                  # traseiras e dianteiras tocam juntas ate ele comecar a deitar
    return r, V((0, 0, 0)), {}, ext
def c_derrotado(t):
    r, raiz, pes, ext = c_derrota(DUR_DER); return r, raiz, pes, ext
REF_EXTRA.update({"AmeacaFim": (c_ameaca, DUR_AM), "InvestidaFim": (c_investida, DUR_INV), "DerrotaFim": (c_derrota, DUR_DER)})
CLIPES.update({"Ameaca": (c_ameaca, DUR_AM, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "AmeacaFim"),
               "Investida": (c_investida, DUR_INV, False, 0.0, lambda t: V_GAL * k_inv(t), 0.0, "AmeacaFim", "InvestidaFim"),
               "RecuperacaoInvestida": (c_recuperacao, DUR_RI, False, 0.0, lambda t: V_GAL * k_ri(t), 0.0, "InvestidaFim", "AlertaFim"),
               "ReacaoImpacto": (c_reacao, DUR_RE, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "Derrota": (c_derrota, DUR_DER, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "DerrotaFim"),
               "Derrotado": (c_derrotado, 1.0, True, 0.0, None, 0.0, "DerrotaFim", "laco (pose mantida)")})
print("LOTE_D", {k: round(CLIPES[k][1], 3) for k in ("Ameaca", "Investida", "RecuperacaoInvestida", "ReacaoImpacto", "Derrota", "Derrotado")})
