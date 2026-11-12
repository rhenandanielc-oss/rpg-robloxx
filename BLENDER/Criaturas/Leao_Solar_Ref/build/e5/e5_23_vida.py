# Fase C (11/11): clipes de VIDA do leao (so movimento). Lote C1 = em pe: Beber, Comer, Bocejar, Lamber_Pata, Espreguicar,
# Reacao_Golpe_E/D. Carregado por exec() dentro de e5_20_clipes.py depois da montaria (usa base_foco, janela, pulso, rampa, R, V,
# MARCHA, CLIPES, T...). Convencoes (medidas): pitch + = nariz desce; pesc - = pescoco DESCE (+ ergue para tras); cab_pitch - = focinho
# desce; cab_yaw + = olha
# para x+ (lado D); roll - = lado D sobe; x+ = lado D; corpo "y" + = tronco para a frente.
def oscila(t, f, a=1.0, fase_=0.0): return a * math.sin(2 * math.pi * f * t + fase_)
# ------------------------------------------------------------------ C1.1 beber (agacha na frente, cabeca ao chao, lambe a agua)
def c_beber(t, fase):
    c = base_foco(t, fase); d = janela(t, 0.4, 5.6, 0.9, 0.9); lam = janela(t, 1.5, 4.9, 0.3, 0.3)
    # r3: agachar fundo enterrava a juba do peito; agacha pouco (1,4) e o pescoco desce ~85 graus (boca a ~1 stud do chao, medido)
    c.update(z=-1.4 * d, y=0.4 * d, pitch=R(7.5) * d, col1=R(2) * d, col2=R(-3) * d, pesc=R(-85) * d, cab_pitch=R(-48) * d,
             mand=R(5) * lam + R(4) * lam * (0.5 + 0.5 * oscila(t, 2.6)), lingua=R(14) * lam * (0.5 + 0.5 * oscila(t, 2.6, 1.0, 0.6)),
             orelha=(R(6) * d, R(6) * d), palp=R(-8) * d, cauda_base=R(2), cauda_amp=R(3), cauda_f=1 / 3.0)
    c["cab_pitch"] += R(2.0) * lam * oscila(t, 2.6, 1.0, 1.2); c["pesc"] -= R(1.5) * lam * oscila(t, 2.6, 1.0, 1.2)   # a cabeca acompanha cada lambida
    return c
# ------------------------------------------------------------------ C1.2 comer em pe (cabeca ao chao, morde e puxa 3 vezes, mastiga)
def c_comer(t, fase):
    c = base_foco(t, fase); d = janela(t, 0.4, 6.6, 0.9, 0.9)
    puxa = sum(janela(t, a, a + 0.7, 0.12, 0.45) for a in (1.6, 3.1, 4.6))                                  # morde e puxa para tras/cima
    masca = sum(janela(t, a, a + 0.75, 0.1, 0.2) for a in (2.3, 3.8, 5.3))                                   # mastiga com a cabeca um pouco erguida
    c.update(z=-1.4 * d + 0.25 * puxa, y=0.4 * d - 0.35 * puxa, pitch=R(7.5) * d - R(3) * puxa, col1=R(2) * d, col2=R(-3) * d,
             pesc=R(-87) * d + R(22) * puxa + R(26) * masca, cab_pitch=R(-48) * d + R(12) * puxa + R(16) * masca,
             cab_roll=R(9) * puxa * oscila(t, 1.4), cab_yaw=R(7) * puxa * oscila(t, 1.4, 1.0, 0.7),
             mand=R(16) * janela(t, 1.35, 1.75, 0.12, 0.1) + R(16) * janela(t, 2.85, 3.25, 0.12, 0.1) + R(16) * janela(t, 4.35, 4.75, 0.12, 0.1)
                  + R(8) * masca * (0.5 + 0.5 * oscila(t, 3.2)), labio=0.14 * puxa,
             orelha=(R(10) * d, R(10) * d), palp=R(-10) * d, cauda_base=R(3), cauda_amp=R(5), cauda_f=1 / 2.4)
    return c
# ------------------------------------------------------------------ C1.3 bocejo (cabeca sobe e recua, boca bem aberta, lingua, olhos fecham)
def c_bocejar(t, fase):
    c = base_foco(t, fase); a = janela(t, 0.5, 3.0, 0.7, 0.6); b = janela(t, 0.9, 2.6, 0.45, 0.5)
    c.update(z=0.08 * a, y=-0.15 * a, pesc=R(-10) * a, cab_pitch=R(14) * a + R(4) * b, mand=R(32) * b, lingua=R(16) * b,
             labio=0.10 * b, palp=R(-35) * b, orelha=(R(18) * b, R(18) * b), col_pitch=R(1.5) * a, cauda_base=R(3), cauda_amp=R(3), cauda_f=1 / 3.4)
    c["cab_roll"] = R(4) * janela(t, 2.6, 3.3, 0.15, 0.3) * oscila(t, 4.0)                                    # sacudidinha no fim
    return c
# ------------------------------------------------------------------ C1.4 lamber a pata dianteira D DEITADO (r2 11/11, referencia do usuario):
# deitado como o Descanso; o cotovelo fica no chao, o antebraco ergue a pata ate a frente do queixo (sola virada para a boca) e a cabeca
# desce e vira para a pata; 4 lambidas; volta a pose deitada (encadeia com Descanso_Deitado / Dormir / Levantar).
def c_lamber(t, fase):
    c = deitado(base_foco(t, fase, T=4.0)); d = janela(t, 0.5, 4.9, 0.8, 0.8); lam = janela(t, 1.5, 4.2, 0.2, 0.2)
    golpe = 0.5 + 0.5 * oscila(t, 1.3, 1.0, -1.2)
    c.update(pesc=R(-8) + R(-32) * d - R(5) * lam * golpe, cab_pitch=R(4) + R(-34) * d - R(8) * lam * golpe, cab_yaw=R(20) * d, pesc_yaw=R(10) * d,
             cab_roll=R(-6) * d, mand=R(9) * lam, lingua=R(18) * lam * golpe, palp=R(-14) * d, orelha=(R(-4) * d, R(-4) * d),
             cauda_base=CB_D, cauda_yaw=CY_D, cauda_amp=R(3), cauda_f=1 / 3.6)
    return c
def ag_lamber():
    via = [(0.15, V((0.0, -6.3, 1.8))), (0.32, V((0.1, -5.9, 3.0)), True), (0.75, V((0.1, -5.9, 3.05)), True), (0.9, V((0.0, -6.4, 1.3)))]
    punho = [(0.0, 10), (0.15, 40), (0.32, 75), (0.75, 75), (0.9, 30), (1.0, 0)]
    dedos = [(0.0, 0), (0.32, 14), (0.75, 14), (1.0, 0)]
    return {"DD": [dict(t0=0.6, t1=4.7, alvo=PES_DEIT["DD"], rel=dict(via=via, punho=punho, dedos=dedos, escapula=0.38))]}
# ------------------------------------------------------------------ C1.5 espreguicar (dianteiras estendem a frente, peito desce, quadril alto)
def c_espreguicar(t, fase):
    c = base_foco(t, fase); e = janela(t, 0.5, 4.7, 1.0, 1.0); boc = janela(t, 1.9, 3.5, 0.4, 0.5)   # r2: corpo desce junto com o passo (perna reta nao estica alem do alcance)
    # r2 (11/11, usuario: "a pata dianteira estique a frente, nao dobre"): dianteiras RETAS a frente (cotovelo ~174 graus), peito baixo, quadril alto
    c.update(z=-0.5 * e, pitch=R(15) * e, meta_dian=R(-45) * e, esc_sobe=-1.0 * e, pesc=R(-10) * e, cab_pitch=R(10) * e,
             mand=R(20) * boc, lingua=R(8) * boc, palp=R(-30) * boc, orelha=(R(14) * e, R(14) * e), cauda_base=R(18) * e, cauda_amp=R(4), cauda_f=1 / 2.0)
    return c
AG_ESPREG = {"DD": [dict(t0=0.6, t1=1.5, alvo=V((0, -7.0, 0)), h=1.0), dict(t0=3.6, t1=4.4, alvo=V((0, 0, 0)), h=0.8)],
             "DE": [dict(t0=0.75, t1=1.65, alvo=V((0, -7.0, 0)), h=1.0), dict(t0=3.75, t1=4.55, alvo=V((0, 0, 0)), h=0.8)]}
# ------------------------------------------------------------------ C1.6 reacao a golpe pelo lado (recua, cabeca vira, orelhas para tras)
def c_reacao(lado):
    sg = -1 if lado == "E" else 1                                                 # lado de onde vem o golpe
    def f(t, fase):
        c = base_foco(t, fase); g = janela(t, 0.12, 1.3, 0.06, 0.6); s_ = janela(t, 0.12, 0.55, 0.04, 0.25)
        c.update(x=-sg * 0.55 * g, y=-0.25 * g, z=-0.35 * g, roll=sg * R(5) * s_, col_yaw=-sg * R(7) * s_, pesc=R(8) * s_, pesc_yaw=-sg * R(10) * s_,
                 cab_yaw=sg * R(18) * g, cab_pitch=R(6) * s_, cab_roll=-sg * R(6) * s_, palp=R(-30) * s_ - R(8) * g, orelha=(R(26) * g, R(26) * g),
                 labio=0.22 * g, mand=R(10) * s_, cauda_base=R(8) * g, cauda_yaw=sg * R(16) * s_, cauda_amp=R(6) * g, cauda_f=1.4)
        return c
    return f
CLIPES.update({
    "Beber": dict(dur=6.2, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_beber),
    "Comer": dict(dur=7.2, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_comer),
    "Bocejar": dict(dur=3.6, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_bocejar),
    "Espreguicar": dict(dur=5.4, loop=False, inicio_repouso=True, escapula_loc=True, agenda=AG_ESPREG, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_espreguicar),
    "Reacao_Golpe_E": dict(dur=1.6, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_reacao("E")),
    "Reacao_Golpe_D": dict(dur=1.6, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_reacao("D")),
})
# ------------------------------------------------------------------ Lote C2 = no chao: Deitar, Descanso_Deitado, Dormir, Levantar, Sentar, Sentado,
# Levantar_Sentado, Morte. Deitado = esfinge: barriga perto do chao, antebracos deitados (metacarpo -25 graus; -80 enterrava punho/mao 1,7), patas da
# frente 3 studs a frente, traseiras dobradas sob o corpo e um pouco para fora. Sentado = quadril no chao, nariz para cima (pitch -20).
DEIT = dict(z=-5.7, pitch=R(-7.5), meta_dian=R(-50), meta_tras=R(-64), esc_sobe=-1.0)   # r2 (11/11): antebracos DEITADOS no chao (ref. do usuario)
# cauda deitada no chao, curvada para o lado (varredura 11/11: cauda_base -4 enterrava o tufo 5 studs; 12/+35 = tufo ~0,5 acima do chao)
CB_D, CY_D = R(20), R(35)   # r2: corpo mais baixo -> cauda mais alta (varredura: 12 = -2,4; 25 = +1,2)
PES_DEIT = {"DD": V((0, -6.5, 0.3)), "DE": V((0, -6.5, 0.3)), "TD": V((1.4, -4.0, 0)), "TE": V((-1.4, -4.0, 0))}
PES_DORM = dict(PES_DEIT, TD=V((4.5, -4.0, 0.3)), TE=V((6.0, -1.0, 0.3)))   # r3: traseiras soltas para o lado D (quadril tombado)
YAW_DORM = {"TD": R(70), "TE": R(70)}
# cauda deitada (busca gulosa por segmento, busca_cauda 11/11): sai do quadril, desce ao chao e contorna o lado D ate as patas
CAUDA_DORM = [(R(p), R(y)) for p, y in ((8, 86), (-80, -4), (-24, 32), (-8, 14), (8, 23), (24, -4))]
SENT = dict(z=-7.4, pitch=R(-28), meta_tras=R(-64), esc_sobe=-1.4)   # r2 (11/11): bunda NO chao, metatarso deitado com a pata a frente
CB_S, CY_S = R(40), R(28)
PES_SENT = {"TD": V((1.4, -3.5, 0)), "TE": V((-1.4, -3.5, 0))}
def deitado(c, k=1.0):
    c.update(z=c["z"] + DEIT["z"] * k, meta_dian=DEIT["meta_dian"] * k, meta_tras=DEIT["meta_tras"] * k, esc_sobe=DEIT.get("esc_sobe", 0.0) * k, pitch=c["pitch"] + DEIT.get("pitch", 0.0) * k); return c
def c_deitar(t, fase):
    c = base_foco(t, fase); tr = rampa(t, 0.35, 1.5); fr = rampa(t, 1.4, 3.2)
    c.update(z=-1.6 * tr * (1 - fr) + DEIT["z"] * fr, pitch=R(-9) * tr * (1 - fr) + DEIT["pitch"] * fr, meta_dian=DEIT["meta_dian"] * rampa(t, 2.0, 3.1), esc_sobe=DEIT["esc_sobe"] * rampa(t, 1.9, 3.1),
             meta_tras=DEIT["meta_tras"] * rampa(t, 1.0, 2.6), pesc=R(-8) * fr, cab_pitch=R(4) * fr, orelha=(R(-6) * fr, R(-6) * fr),
             cauda_base=CB_D * rampa(t, 0.3, 1.2), cauda_yaw=CY_D * fr, cauda_amp=R(3), cauda_f=1 / 3.6)      # cauda sobe ja no agachar (o tufo tocava o chao)
    return c
AG_DEITAR = {"TD": [dict(t0=0.5, t1=0.95, alvo=PES_DEIT["TD"], h=0.6)], "TE": [dict(t0=0.6, t1=1.05, alvo=PES_DEIT["TE"], h=0.6)],
             "DD": [dict(t0=1.55, t1=2.05, alvo=PES_DEIT["DD"], h=0.7)], "DE": [dict(t0=1.7, t1=2.2, alvo=PES_DEIT["DE"], h=0.7)]}
def c_descanso(t, fase):
    c = deitado(base_foco(t, fase, T=4.0)); olha = oscila(t, 1 / 6.0)
    c.update(pesc=R(-8), cab_pitch=R(4) + R(3) * oscila(t, 1 / 6.0, 1.0, 1.0), cab_yaw=R(14) * olha, pesc_yaw=R(6) * olha,
             orelha=(R(-6) + R(10) * janela(t, 2.2, 2.6, 0.08, 0.15), R(-6)), palp=R(-6), cauda_base=CB_D, cauda_yaw=CY_D, cauda_amp=R(4), cauda_f=1 / 3.0)
    return c
def c_dormir(t, fase):
    c = deitado(base_foco(t, fase, T=8.0 / 2)); b = oscila(t, 1 / 4.0)
    # r2 (11/11, ref. do usuario): cabeca DEITADA entre as patas, olhos fechados de verdade.
    # r2b: pescoco -55 + focinho -30 (era -90/+5): a dobra pescoco/cabeca de ~95 graus esticava a pele da palpebra (pesos do Pescoco2) e o olho ficava aberto
    # r3 (11/11, usuario: "pernas relaxem... corpo todo no chao"): quadril TOMBADO para o lado E (roll -55; o peito volta 30 e fica de esfinge),
    # traseiras soltas e deitadas para o lado D (PES_DORM), cauda curvada junto das patas. Pose estatica medida em teste_dorm (r5).
    c.update(z=c["z"] - 0.75, roll=R(-55), peito_roll=R(30), pesc=R(-55) + R(1.0) * b, cab_pitch=R(-30), cab_yaw=R(6), cab_roll=R(6), palp=R(-42), orelha=(R(6), R(6)),
             col_pitch=R(1.2) * b, mand=R(0.5), cauda_base=R(-20), cauda_yaw=R(50), cauda_amp=R(1.5), cauda_f=1 / 8.0)
    c["orelha"] = (R(6) + R(14) * janela(t, 5.0, 5.35, 0.06, 0.15), R(6))                                   # a orelha tremula uma vez
    c["cauda_chao"] = True; c["cauda_seg"] = CAUDA_DORM                                                                                # cauda DEITADA no chao, curvada ate as patas
    return c
def c_levantar(t, fase):
    c = base_foco(t, fase); fr = 1 - rampa(t, 0.4, 1.7); tr = 1 - rampa(t, 1.5, 2.6)
    c.update(z=DEIT["z"] * fr + (-1.6) * (1 - fr) * tr, pitch=R(-9) * (1 - fr) * tr + DEIT["pitch"] * fr, meta_dian=DEIT["meta_dian"] * (1 - rampa(t, 0.3, 1.0)), esc_sobe=DEIT["esc_sobe"] * (1 - rampa(t, 0.3, 1.2)),
             meta_tras=DEIT["meta_tras"] * (1 - rampa(t, 1.4, 2.2)), pesc=R(-8) * fr, orelha=(R(-6) * fr, R(-6) * fr), cauda_base=CB_D * tr, cauda_yaw=CY_D * fr, cauda_amp=R(3), cauda_f=1 / 3.6)
    return c
AG_LEVANTAR = {"DD": [dict(t0=0.55, t1=1.05, alvo=V((0, 0, 0)), h=0.7)], "DE": [dict(t0=0.7, t1=1.2, alvo=V((0, 0, 0)), h=0.7)],
               "TD": [dict(t0=1.55, t1=2.0, alvo=V((0, 0, 0)), h=0.6)], "TE": [dict(t0=1.65, t1=2.1, alvo=V((0, 0, 0)), h=0.6)]}
def c_sentar(t, fase):
    c = base_foco(t, fase); s_ = rampa(t, 0.5, 2.0)
    c.update(z=SENT["z"] * s_, pitch=SENT["pitch"] * s_, esc_sobe=SENT.get("esc_sobe", 0.0) * s_, meta_tras=SENT["meta_tras"] * rampa(t, 0.8, 2.0), pesc=R(10) * s_, cab_pitch=R(-12) * s_,
             cauda_base=CB_S * s_, cauda_yaw=CY_S * s_, cauda_amp=R(3), cauda_f=1 / 3.4)
    return c
AG_SENTAR = {"TD": [dict(t0=0.35, t1=0.8, alvo=PES_SENT["TD"], h=0.5)], "TE": [dict(t0=0.45, t1=0.9, alvo=PES_SENT["TE"], h=0.5)]}
def c_sentado(t, fase):
    c = base_foco(t, fase, T=5.0 / 1.5); olha = oscila(t, 1 / 5.0)
    c.update(z=c["z"] + SENT["z"], pitch=SENT["pitch"], esc_sobe=SENT.get("esc_sobe", 0.0), meta_tras=SENT["meta_tras"], pesc=R(10), cab_pitch=R(-12) + R(3) * oscila(t, 0.4, 1.0, 0.5),
             cab_yaw=R(16) * olha, pesc_yaw=R(6) * olha, orelha=(R(-8), R(-8)), cauda_base=CB_S, cauda_yaw=CY_S, cauda_amp=R(4), cauda_f=1 / 2.5)
    return c
def c_levantar_sentado(t, fase):
    c = base_foco(t, fase); s_ = 1 - rampa(t, 0.4, 1.5)
    c.update(z=SENT["z"] * s_, pitch=SENT["pitch"] * s_, esc_sobe=SENT.get("esc_sobe", 0.0) * s_, meta_tras=SENT["meta_tras"] * (1 - rampa(t, 0.3, 1.2)), pesc=R(10) * s_, cab_pitch=R(-12) * s_,
             cauda_base=CB_S * s_, cauda_yaw=CY_S * s_, cauda_amp=R(3), cauda_f=1 / 3.4)
    return c
AG_LEV_SENT = {"TD": [dict(t0=1.0, t1=1.45, alvo=V((0, 0, 0)), h=0.5)], "TE": [dict(t0=1.1, t1=1.55, alvo=V((0, 0, 0)), h=0.5)]}
MORTE = dict(z=-3.2, meta_dian=R(-25), meta_tras=R(-50))     # a queda de lado guarda a pose da 1a versao (so os olhos mudaram)
def c_morte(t, fase):
    c = base_foco(t, fase); cai = rampa(t, 0.25, 1.35); lado_ = rampa(t, 1.2, 2.2); cab = rampa(t, 1.0, 2.0)
    c.update(z=MORTE["z"] * cai - 0.25 * lado_, pitch=R(-4) * janela(t, 0.25, 1.6, 0.35, 0.5), meta_dian=MORTE["meta_dian"] * rampa(t, 0.3, 1.1),
             meta_tras=MORTE["meta_tras"] * rampa(t, 0.5, 1.4), roll=R(-22) * lado_, x=0.7 * lado_,
             pesc=R(-70) * cab, cab_pitch=R(-22) * cab, cab_roll=R(26) * cab, palp=R(-45) * rampa(t, 0.6, 1.6), mand=R(7) * cab,
             orelha=(R(10) * cab, R(10) * cab), cauda_base=R(24) * rampa(t, 0.1, 1.0), cauda_yaw=CY_D * cai, cauda_amp=R(2) * (1 - cai), cauda_f=1 / 4.0)
    c["resp"] = 0.0
    return c
AG_MORTE = {"DD": [dict(t0=0.55, t1=1.05, alvo=V((0, -2.2, 0)), h=0.4)], "DE": [dict(t0=0.6, t1=1.1, alvo=V((0, -2.0, 0)), h=0.4)],
            "TD": [dict(t0=0.8, t1=1.25, alvo=V((0.6, -1.0, 0)), h=0.4)], "TE": [dict(t0=0.85, t1=1.3, alvo=V((-0.4, -1.0, 0)), h=0.4)]}
_P = lambda t: MARCHA["parado"]; _0 = lambda t: 0.0
CLIPES.update({
    "Lamber_Pata": dict(dur=5.4, loop=False, inicio_repouso=True, escapula_loc=True, agenda=ag_lamber(), pes_ini=PES_DEIT, marcha=_P, vel=_0, rumo=_0, corpo=c_lamber),
    "Deitar": dict(dur=4.0, loop=False, inicio_repouso=True, escapula_loc=True, agenda=AG_DEITAR, marcha=_P, vel=_0, rumo=_0, corpo=c_deitar),
    "Descanso_Deitado": dict(dur=6.0, loop=True, inicio_repouso=True, escapula_loc=True, agenda={}, pes_ini=PES_DEIT, marcha=_P, vel=_0, rumo=_0, corpo=c_descanso),
    "Dormir": dict(dur=8.0, loop=True, inicio_repouso=True, escapula_loc=True, agenda={}, pes_ini=PES_DORM, pes_yaw=YAW_DORM, marcha=_P, vel=_0, rumo=_0, corpo=c_dormir),
    "Levantar": dict(dur=3.0, loop=False, inicio_repouso=True, escapula_loc=True, agenda=AG_LEVANTAR, pes_ini=PES_DEIT, marcha=_P, vel=_0, rumo=_0, corpo=c_levantar),
    "Sentar": dict(dur=2.6, loop=False, inicio_repouso=True, escapula_loc=True, agenda=AG_SENTAR, marcha=_P, vel=_0, rumo=_0, corpo=c_sentar),
    "Sentado": dict(dur=5.0, loop=True, inicio_repouso=True, escapula_loc=True, agenda={}, pes_ini=PES_SENT, marcha=_P, vel=_0, rumo=_0, corpo=c_sentado),
    "Levantar_Sentado": dict(dur=2.0, loop=False, inicio_repouso=True, escapula_loc=True, agenda=AG_LEV_SENT, pes_ini=PES_SENT, marcha=_P, vel=_0, rumo=_0, corpo=c_levantar_sentado),
    "Morte": dict(dur=3.4, loop=False, inicio_repouso=True, agenda=AG_MORTE, marcha=_P, vel=_0, rumo=_0, corpo=c_morte),
})
