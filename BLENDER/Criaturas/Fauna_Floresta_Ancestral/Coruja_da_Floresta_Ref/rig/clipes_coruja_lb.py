# ================================================================== LOTE B da Coruja-da-Floresta (14/11/2026): voo.
# Carregado por exec() em clipes_coruja.py com CORUJA_LB=1 (rig r3: CORUJA_R3=1, CORUJA_DOBRA=rig/r3/dobra_asas.json).
# Asas partem da pose ABERTA do modelo (identidade) e batem por deltas (alto/baixo, pulso dobrando na subida);
# corpo inclina para a frente (Raiz em X); cabeca compensa e fica nivelada; pes PRESOS AO CORPO (recolhidos sob a cauda) pelo
# mesmo IK do chao -> decolar/pousar trocam o alvo dos pes (chao <-> corpo) sem estalo.
# NO LUGAR na horizontal (velocidade gravada; v_perfil em decolar/pousar); a ALTURA de voo fica no clipe (centro do corpo a
# H_VOO). Batidas, velocidades, inclinacoes e duracoes sao [PROPOSTA]. Comportamento da especie (voa/recua) e [PROPOSTA].
ABERTA = {nm: Quaternion() for nm in ASA_OSSOS}
def mistura(rA, rB, w):
    r = {}
    for n_ in set(rA) | set(rB): r[n_] = [(e, a * (1 - w)) for e, a in rA.get(n_, [])] + [(e, a * w) for e, a in rB.get(n_, [])]
    return r
def asa_aberta(f): return {l: (ABERTA, f) for l in PES}
def asa_rots(r, l, braco=(), ante=(), mao=(), prim=(), ombro=()):
    """deltas da asa E em eixos do mundo de repouso; a D espelha (Y e Z trocam de sinal)"""
    s = 1 if l == "E" else -1
    for nm, e in (("OmbroAsa", ombro), ("BracoAsa", braco), ("AntebracoAsa", ante), ("MaoAsa", mao), ("Primarias", prim)):
        if e: soma(r, nm + l, [(ax, ang * (s if ax != X else 1)) for ax, ang in e])
H_VOO = 0.55                                     # altura do centro do corpo em voo (no clipe)
PIVO_RAIZ = BD["Raiz"].head_local.copy(); CENTRO = V((0, -0.02, 0.32))      # centro aproximado do corpo em repouso
def raiz_para(pitch, bank, alvo):
    """translacao da Raiz para que o centro do corpo fique em 'alvo' depois de inclinar (pitch em X, bank em Y)"""
    Rm = (Matrix.Rotation(bank, 3, Y) @ Matrix.Rotation(pitch, 3, X))
    c_ = PIVO_RAIZ + Rm @ (CENTRO - PIVO_RAIZ); return V(alvo) - c_
PE_RECOLHIDO = {"E": (0.050, 0.095, 0.150), "D": (-0.050, 0.095, 0.150)}      # pes sob a cauda (pontos do repouso)
def pes_no_corpo(f, enrola=R(70)): return {l: (PE_RECOLHIDO[l], f, enrola) for l in PES}
# perna RECOLHIDA (FK, eixos do repouso): coxa e tibia para tras, tarso dobrado, dedos fechados - pes sob a cauda
RECOLHIDA = {"Coxa": [(X, R(30))], "Tibia": [(X, R(55))], "Tarso": [(X, R(-35))], "Dedos": [(X, R(-60))]}
def pernas_no_ar(f): return (RECOLHIDA, f)
# ---------------------------------------------------------------- corpo de voo (batida e planeio compartilham)
T_BAT = 0.40; V_BAT = 3.0; V_PLA = 3.6; PITCH = R(52)
def batida(r, l, u, amp):
    """asa no ciclo de batida (u em ciclos): descida rapida com a asa estendida, subida com o pulso dobrado"""
    c = math.cos(2 * math.pi * u); sobe = max(0.0, math.sin(2 * math.pi * u))   # c=+1 no alto, -1 embaixo
    asa_rots(r, l, ombro=[(Y, R(-10) * c * amp)], braco=[(Y, R(-42) * c * amp), (Z, R(6) * c * amp)],
             ante=[(Y, R(-8) * c * amp), (Z, R(14) * sobe * amp)], mao=[(Z, R(-22) * sobe * amp), (Y, R(10) * c * amp)],
             prim=[(Z, R(-10) * sobe * amp), (Y, R(6) * c * amp)])
def planeio(r, l, t, k=1.0):
    """asa aberta planando: diedro leve, primarias ajustando devagar"""
    asa_rots(r, l, braco=[(Y, R(-8) * k)], mao=[(Y, R(3) * math.sin(2 * math.pi * t / (T_PLA / 2)) * k)], prim=[(Z, R(-4) * k), (Y, R(-4) * math.sin(2 * math.pi * t / (T_PLA / 3) + 1) * k)])   # periodos que dividem o laco
def corpo_voo(t, u, amp_bat, k_pla, bank=0.0, giro_cab=0.0):
    """pose de voo: amp_bat = intensidade da batida (fase u); k_pla = peso do planeio; bank = inclinacao lateral (rad)"""
    r = {}; c = math.cos(2 * math.pi * u)
    for l in PES:
        if amp_bat > 0: batida(r, l, u, amp_bat)
        if k_pla > 0: planeio(r, l, t, k_pla)
    sobe_corpo = -0.012 * c * amp_bat                                              # corpo sobe na descida da asa
    r["Raiz"] = [(X, PITCH + R(3) * c * amp_bat), (Y, bank)]
    # cabeca nivelada e olhando a frente (compensa o pitch do corpo), estavel na batida
    soma(r, "Pescoco", [(X, -PITCH * 0.30)]); soma(r, "Pescoco2", [(X, -PITCH * 0.30)]); soma(r, "Cabeca", [(X, -PITCH * 0.35 - R(3) * c * amp_bat), (Z, giro_cab), (Y, -bank * 0.6)])
    soma(r, "Cauda", [(X, R(-10) + R(4) * c * amp_bat)]); soma(r, "CaudaLequeE", [(Y, R(-12) * k_pla)]); soma(r, "CaudaLequeD", [(Y, R(12) * k_pla)])
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-25))])                              # tufos deitados em voo
    raiz = raiz_para(PITCH, bank, (0, 0, H_VOO)) + V((0, 0, sobe_corpo))
    return r, raiz
def ext_voo(f_asa=1.0): return {"asa": asa_aberta(f_asa), "pernas_fk": pernas_no_ar(1.0), "apoio": {l: False for l in PES}}
def c_bater(t):
    r, raiz = corpo_voo(t, t / T_BAT, 1.0, 0.0); return r, raiz, {}, ext_voo()
T_PLA = 2.6
def c_planar(t):
    r, raiz = corpo_voo(t, 0.0, 0.0, 1.0); return r, raiz + V((0, 0, 0.006 * math.sin(2 * math.pi * t / T_PLA))), {}, ext_voo()
GIRO_CURVA = 40.0; BANK = R(24)
def c_curva(s):
    def f(t):
        r, raiz = corpo_voo(t, 0.0, 0.0, 1.0, bank=BANK * s, giro_cab=R(14) * s)
        for l, sx in (("E", 1), ("D", -1)): asa_rots(r, l, braco=[(Y, R(5) * s * sx)])   # asa de dentro um pouco mais baixa
        return r, raiz + V((0, 0, 0.006 * math.sin(2 * math.pi * t / T_PLA))), {}, ext_voo()
    return f
# ---------------------------------------------------------------- transicoes batida <-> planeio (terminam no q0 do destino)
DUR_BP = 4 * T_BAT * 0.5 + 0.2                                    # 1,0 s
def c_bater_para_planar(t):
    w = suave(t / DUR_BP)                                          # amplitude da batida morre, planeio entra (fim = Planar q0)
    r, raiz = corpo_voo(t - DUR_BP, t / T_BAT, 1 - w, w); return r, raiz, {}, ext_voo()
DUR_PB = 3 * T_BAT                                                 # 1,2 s: entra batendo e termina na fase inteira (q0 do BaterAsas)
def c_planar_para_bater(t):
    w = suave(t / (2 * T_BAT)); r, raiz = corpo_voo(t * (1 - w), t / T_BAT, w, 1 - w)
    return r, raiz, {}, ext_voo()
# ---------------------------------------------------------------- decolar: Repouso q0 -> BaterAsas q0
T_AG, T_SAI = 0.28, 0.44; N_BAT_DEC = 3; DUR_DEC = T_SAI + N_BAT_DEC * T_BAT
def c_decolar(t):
    r0, raiz0 = base_rep(); tb = t - T_SAI                       # tb: tempo de voo (fase da batida)
    ag = suave(t / T_AG) * (1 - suave((t - T_AG) / (T_SAI - T_AG)))  # agacha e explode
    ar = suave((t - T_SAI + 0.06) / 0.5)                           # entra no voo
    asa_f = suave((t - 0.12) / 0.38)                               # asas abrem antes de sair do chao
    amp = suave((t - 0.30) / 0.45) * (1.0 + 0.25 * (1 - suave((t - 0.9) / 0.5)))   # primeiras batidas mais amplas
    rv, raizv = corpo_voo(t, max(0.0, tb) / T_BAT if tb > 0 else (t - T_SAI) / T_BAT, min(1.25, amp), 0.0)
    r = mistura(r0, rv, ar)
    if ar < 1:                                                     # no chao: asas abrindo (sem batida antes da hora)
        for l in PES:
            for nm in ASA_OSSOS:
                if nm + l in r: r[nm + l] = [(e, a * min(1.0, amp + ar)) for e, a in r[nm + l]]
    soma(r, "Coluna2", [(X, R(14) * ag)]); soma(r, "Pescoco", [(X, R(8) * ag)])  # agacha inclinando o corpo para a frente
    soma(r, "Cauda", [(X, R(14) * ag)])                                           # (r2: a ponta da cauda raspava no agachamento)
    raiz = raiz0.lerp(raizv, ar) + V((0, -0.02 * ag, -0.035 * ag))
    pes_f = ar                                                     # pes acompanham a subida do corpo (r2: atrasados, a perna esticava e a tibia virava)
    return r, raiz, {}, {"asa": asa_aberta(asa_f), "pernas_fk": pernas_no_ar(pes_f), "apoio": {l: t < T_SAI for l in PES}}
def v_decolar(t): return V_BAT * suave((t - T_SAI + 0.1) / (N_BAT_DEC * T_BAT))
# ---------------------------------------------------------------- pousar: Planar q0 -> Repouso q0
T_TOQ = 0.95; DUR_POU = T_TOQ + 0.95
def c_pousar(t):
    rv, raizv = corpo_voo(t, (t - T_TOQ) / (T_BAT * 0.8), 0.0, 1.0)
    fl = suave(t / 0.55)                                           # flare: corpo fica em pe, asas freiam (para cima e a frente)
    for l in PES: asa_rots(rv, l, braco=[(Y, R(-30) * fl), (Z, R(-25) * fl)], ante=[(Z, R(-10) * fl)], prim=[(Y, R(-10) * fl)])
    rv["Raiz"] = [(X, PITCH * (1 - 0.85 * fl))]
    soma(rv, "Cauda", [(X, R(18) * fl)]); soma(rv, "CaudaLequeE", [(Y, R(-14) * fl)]); soma(rv, "CaudaLequeD", [(Y, R(14) * fl)])
    soma(rv, "Pescoco", [(X, PITCH * 0.30 * fl)]); soma(rv, "Pescoco2", [(X, PITCH * 0.30 * fl)]); soma(rv, "Cabeca", [(X, PITCH * 0.35 * fl)])
    desce = suave(t / T_TOQ); raiz_v = raiz_para(PITCH * (1 - 0.85 * fl), 0.0, (0, 0, H_VOO * (1 - desce) + CENTRO.z * desce))
    # depois do toque: absorve, duas batidas curtas de equilibrio e fecha as asas
    pos = t - T_TOQ; ab = janela(t, T_TOQ - 0.02, T_TOQ + 0.45, 0.10, 0.30)
    eq = math.exp(-max(0.0, pos) / 0.25) * math.sin(2 * math.pi * max(0.0, pos) / 0.28) if pos > 0 else 0.0
    if pos > 0:
        for l in PES: asa_rots(rv, l, braco=[(Y, R(-20) * eq)])
    r0, raiz0 = base_rep(); fim = suave((t - T_TOQ - 0.15) / 0.75)
    r = mistura(rv, r0, fim)
    raiz = raiz_v.lerp(raiz0, suave((t - T_TOQ + 0.1) / 0.3)) + V((0, 0, -0.03 * ab))
    asa_f = 1 - suave((t - T_TOQ - 0.1) / 0.7)                      # asas fecham depois do toque
    pes_f = 1 - suave((t - 0.25) / (T_TOQ - 0.30))                 # pes saem do corpo e vao ao chao (garras a frente antes do toque)
    pes = {l: V((0, -0.05 * (1 - suave((t - 0.6) / 0.35)), 0)) for l in PES}
    return r, raiz, pes, {"asa": asa_aberta(asa_f), "pernas_fk": pernas_no_ar(pes_f), "apoio": {l: t >= T_TOQ for l in PES}}
def v_pousar(t): return V_PLA * (1 - suave(t / T_TOQ))
CLIPES.update({"BaterAsas": (c_bater, 4 * T_BAT, True, V_BAT, 0.0, "laco", "laco"),
               "Planar": (c_planar, T_PLA, True, V_PLA, 0.0, "laco", "laco"),
               "PlanarCurvaE": (c_curva(1), T_PLA, True, V_PLA, GIRO_CURVA, "laco", "laco"),
               "PlanarCurvaD": (c_curva(-1), T_PLA, True, V_PLA, -GIRO_CURVA, "laco", "laco"),
               "BaterParaPlanar": (c_bater_para_planar, DUR_BP, False, 0.0, 0.0, "BaterAsas q0", "Planar q0", lambda t: V_BAT + (V_PLA - V_BAT) * suave(t / DUR_BP)),
               "PlanarParaBater": (c_planar_para_bater, DUR_PB, False, 0.0, 0.0, "Planar q0", "BaterAsas q0", lambda t: V_PLA + (V_BAT - V_PLA) * suave(t / (2 * T_BAT))),
               "Decolar": (c_decolar, DUR_DEC, False, 0.0, 0.0, "Repouso q0", "BaterAsas q0", v_decolar),
               "Pousar": (c_pousar, DUR_POU, False, 0.0, 0.0, "Planar q0", "Repouso q0", v_pousar)})
print("LOTE_B", {k: round(CLIPES[k][1], 3) for k in ("BaterAsas", "Planar", "Decolar", "Pousar", "BaterParaPlanar", "PlanarParaBater")})
