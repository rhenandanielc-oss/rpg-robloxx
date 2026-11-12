# Fase C extra (11/11): realismo pedido pelo usuario ("siga com o 2"). Carregado por exec() dentro de e5_20_clipes.py depois de
# e5_23_vida.py (usa c_descanso, c_dormir, PES_DEIT, PES_DORM, YAW_DORM, CAUDA_DORM, deitado, oscila, janela, rampa, R, V...).
# 1. Transicoes Deitado_para_Dormir / Dormir_para_Deitado: mistura do Descanso_Deitado (esfinge) com o Dormir r3 (quadril tombado),
#    traseiras escorregam para o lado da barriga (e voltam), cauda passa da postura uniforme para a deitada.
def misturar(a, b, k):
    """mistura dois dicionarios de corpo (numeros e tuplas); a cauda deitada de b entra por cauda_mix"""
    out = dict(a)
    for key, vb in b.items():
        if key in ("cauda_seg", "cauda_mix"): continue
        va = a.get(key, 0.0)
        if isinstance(vb, tuple): out[key] = tuple(x + (y - x) * k for x, y in zip(va, vb))
        elif isinstance(vb, (int, float)): out[key] = va + (vb - va) * k
    out["cauda_seg"] = b.get("cauda_seg"); out["cauda_mix"] = k; out["cauda_chao"] = True   # a cauda nao entra no chao no meio do tombo
    return out
T_DEP = 4.0
def c_deitado_dormir(t, fase):
    # comeca = Descanso_Deitado(0); termina = Dormir(8) = Dormir(0) (loops emendam)
    k = rampa(t, 0.4, 3.3)
    return misturar(c_descanso(t, fase), c_dormir(t + 8.0 - T_DEP, fase), k)
def c_dormir_deitado(t, fase):
    # acorda: comeca = Dormir(0); termina = Descanso_Deitado(6) = Descanso_Deitado(0)
    k = 1 - rampa(t, 0.5, 3.2)
    c = misturar(c_descanso(t + 6.0 - T_DEP, fase), c_dormir(t, fase), k)
    c["palp"] = c["palp"] if t > 0.9 else R(-42)                                   # abre os olhos so depois de mexer a cabeca
    return c
# traseiras: o quadril tomba e as patas escorregam rente ao chao para o lado da barriga (D); a de baixo (TE) passa sob o corpo
AG_DEP_DORM = {"TD": [dict(t0=1.0, t1=2.3, alvo=PES_DORM["TD"], yaw=YAW_DORM["TD"], h=0.35)],
               "TE": [dict(t0=1.5, t1=3.0, alvo=PES_DORM["TE"], yaw=YAW_DORM["TE"], h=0.25)]}
AG_DORM_DEP = {"TE": [dict(t0=0.7, t1=2.1, alvo=PES_DEIT["TE"], h=0.3)],
               "TD": [dict(t0=1.2, t1=2.6, alvo=PES_DEIT["TD"], h=0.4)]}
CLIPES.update({
    "Deitado_para_Dormir": dict(dur=T_DEP, loop=False, inicio_repouso=True, escapula_loc=True, agenda=AG_DEP_DORM, pes_ini=PES_DEIT, marcha=_P, vel=_0, rumo=_0, corpo=c_deitado_dormir),
    "Dormir_para_Deitado": dict(dur=T_DEP, loop=False, inicio_repouso=True, escapula_loc=True, agenda=AG_DORM_DEP, pes_ini=PES_DORM, pes_yaw=YAW_DORM, marcha=_P, vel=_0, rumo=_0, corpo=c_dormir_deitado),
})
# ------------------------------------------------------------------ 2. Pular_Obstaculo: o mesmo impulso/voo/pouso do Bote (aprovado), mais curto e mais
# alto, sem cara de ataque (boca fechada, orelhas para a frente), agachamento menor; aterrissa dianteiras primeiro e segue em pe.
PULO_DIST, PULO_ALT = 16.0, 6.5
def c_pulo(t, fase):
    c = base_foco(t, fase); ag = janela(t, 0.05, 0.80, 0.42, 0.26); emp = pulso(t, 0.52, 0.95)
    s_ = min(max((t - T_DEC) / (T_POUSO - T_DEC), 0.0), 1.0); voo = 4 * s_ * (1 - s_) if T_DEC < t < T_POUSO else 0.0
    ate = janela(t, T_POUSO - 0.04, 2.5, 0.14, 0.6)
    c.update(z=-1.9 * ag + PULO_ALT * voo - 1.0 * ate, y=-1.0 * ag + 0.3 * emp,
             pitch=R(-2.0) * ag - R(14) * pulso(t, 0.55, 1.10) + R(10) * pulso(t, 1.25, 1.85),     # nariz sobe na subida, desce para o pouso
             col1=R(7) * ag - R(9) * emp + R(5) * ate, col2=R(-8) * ag + R(10) * emp - R(6) * ate,
             pesc=R(14) * ag + R(10) * voo + R(8) * ate, cab_pitch=R(6) * ag + R(-6) * pulso(t, 1.2, 1.8),   # olha o ponto de pouso
             orelha=(R(14) * voo, R(14) * voo), palp=R(-6), mand=R(3) * ate, labio=0.0,
             cauda_base=R(14) * ag + R(10) * emp + R(20) * voo + R(12) * ate, cauda_amp=R(4) * ag + R(2), cauda_f=1.0)
    return c
# ------------------------------------------------------------------ 3. Nadar / Nadar_Parado: "nado de cachorro" do leao real: cabeca alta e nariz
# acima da agua, dorso rente a superficie, dianteiras em remada alternada (alcanca a frente com o punho dobrado, puxa para baixo e para tras com a
# pata aberta), traseiras chutam em diagonal com a dianteira oposta; cauda boiando atras. Sem chao: todas as patas sempre em balanco.
T_NADO, T_NADO_P = 1.25, 1.6
def ag_nado(T, dur, esc=1.0):
    """balancos encadeados (fim de um = inicio do outro), caminho relativo ao ponto de repouso da pata (frente = -Y)"""
    # r2: remada mais ampla (a 1a parecia andar debaixo d'agua): a dianteira sobe dobrada ate sob o queixo, estica bem a frente e puxa
    # para baixo e para tras com a pata aberta; a traseira recolhe a frente e chuta esticando para tras
    A_D, A_T = V((0, 1.2 * esc, 3.6)), V((0, 0.3 * esc, 3.6))
    via_d = [(0.25, V((0, -1.6 * esc, 6.0))), (0.5, V((0, -4.6 * esc, 5.4))), (0.75, V((0, -1.4 * esc, 2.4)))]
    punho = [(0.0, 40), (0.25, 75), (0.5, 10), (0.75, -6), (1.0, 40)]; dedos = [(0.0, 8), (0.25, 18), (0.5, -8), (0.75, -6), (1.0, 8)]
    via_t = [(0.3, V((0, -1.8 * esc, 4.2)), R(30)), (0.58, V((0, 2.0 * esc, 2.8)), R(-10)), (0.82, V((0, 2.8 * esc, 3.6)), R(-25))]
    off = {"DD": 0.0, "TE": 0.08, "DE": 0.5, "TD": 0.58}; ag = {}
    for p_, o in off.items():
        lst = []
        for k in range(-3, int(dur / T) + 4):
            t0 = (o + k) * T
            if p_[0] == "D": lst.append(dict(t0=t0, t1=t0 + T, alvo=A_D, rel=dict(via=via_d, punho=punho, dedos=dedos, escapula=0.36)))
            else: lst.append(dict(t0=t0, t1=t0 + T, alvo=A_T, via=via_t))
        ag[p_] = lst
    return ag, {"DD": A_D, "DE": A_D, "TD": A_T, "TE": A_T}
def c_nado(T, parado=False):
    def f(t, fase):
        c = corpo_base(); s = math.sin(2 * math.pi * t / T)
        c.update(z=0.12 * math.sin(4 * math.pi * t / T), pitch=R(-7 if not parado else -4), roll=R(2.5) * s, peito_roll=R(-1.5) * s,
                 pesc=R(26) + R(2) * math.sin(4 * math.pi * t / T), cab_pitch=R(10), cab_roll=R(-2) * s, orelha=(R(4), R(4)), palp=R(-4),
                 mand=R(2) + R(3) * max(0.0, math.sin(2 * math.pi * t / (2 * T))),                # boca entreaberta, bufando no ritmo
                 col_yaw=R(1.5) * s, cauda_base=R(-2), cauda_amp=R(5), cauda_f=1 / T, resp=0.0)
        return c
    return f
_AG_N, _PI_N = ag_nado(T_NADO, 2 * T_NADO); _AG_NP, _PI_NP = ag_nado(T_NADO_P, 2 * T_NADO_P, esc=0.55)
V_NADO = 4.5
# ------------------------------------------------------------------ 4. Subir_Encosta / Descer_Encosta: andar em rampa de 20 graus. O chao e a raiz sobem
# pela inclinacao (chao_z); o tronco inclina junto (nariz para cima na subida), a cabeca olha um pouco ao longo da rampa; passada mais curta.
INCL = 20.0
def c_encosta(a):
    base = c_locomocao("andar")
    def f(t, fase):
        c = base(t, fase); c["pitch"] += -R(a) * 1.0; c["cab_pitch"] += R(a) * 0.45; c["pesc"] += R(a) * (0.25 if a > 0 else 0.1)
        c["cauda_base"] += R(a) * 0.3
        return c
    return f
_AND = lambda t: MARCHA["andar"]
CLIPES.update({
    "Pular_Obstaculo": dict(dur=2.8, loop=False, inicio_repouso=True, dmin_tras=0.55, agenda=AG_BOTE, marcha=_P, vel=lambda t: vel_bote(t, PULO_DIST), rumo=_0, corpo=c_pulo),
    "Nadar": dict(dur=2 * T_NADO, loop=True, agenda=_AG_N, pes_ini=_PI_N, marcha=_P, vel=lambda t: V_NADO, rumo=_0, corpo=c_nado(T_NADO), piscar_auto=True),
    "Nadar_Parado": dict(dur=2 * T_NADO_P, loop=True, agenda=_AG_NP, pes_ini=_PI_NP, marcha=_P, vel=_0, rumo=_0, corpo=c_nado(T_NADO_P, True)),
    "Subir_Encosta": dict(dur=73 / 30, loop=True, marcha=_AND, vel=lambda t: V_ANDAR * 0.82, rumo=_0, corpo=c_encosta(INCL), inclinacao=INCL),
    "Descer_Encosta": dict(dur=73 / 30, loop=True, marcha=_AND, vel=lambda t: V_ANDAR * 0.82, rumo=_0, corpo=c_encosta(-INCL), inclinacao=-INCL),
})
