# ================================================================== LOTE 2 (12/11/2026): trote, corrida de fuga, arrancada,
# frenagem e transicoes de marcha. Carregado por exec() em clipes_cervo.py; NAO altera os clipes aprovados do lote 1 (so
# acrescenta clipes novos). Adaptado do Bufalo (60_clipes.py lote 2 + lote6_transicoes_nado.py), escala do cervo.
# Parametros tecnicos [PROPOSTA] (nao sao regras do jogo): velocidades, passadas, duracoes. Comportamento de fuga da fauna
# segue PROPOSTA ("cervideos fogem"); a regra oficial so diz que cada especie pode fugir, defender-se ou atacar.
def janela(t, a, b, sub=0.2, des=0.2): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
class PerfDesloc:
    def __init__(self, p, d): self.p, self.d = p, d
    def s(self, t): return self.p.s(t + self.d)
def passo_l(t, fase, T, apoio, alt, Lf, perf):
    """passo_var com comprimento de passada variavel no tempo (arrancada/frenagem)"""
    phi = t / T + fase; n_ = math.floor(phi); f = phi - n_; tc = (n_ - fase) * T
    if f < apoio: return Y * (-Lf(tc) / 2 + perf.s(t) - perf.s(tc)), 0.0
    tl = tc + apoio * T; y0 = -Lf(tc) / 2 + perf.s(tl) - perf.s(tc); y1 = -Lf(tc + T) / 2
    u = (f - apoio) / (1 - apoio); s = suave(u)
    return Y * (y0 + (y1 - y0) * s) + V((0, 0, alt * math.sin(math.pi * u) ** 0.8)), u
T_TRO, L_TRO, AP_TRO, ALT_TRO = 0.60, 0.50, 0.45, 0.12          # trote: pares diagonais, ~1,85 u/s
V_TRO = L_TRO / (AP_TRO * T_TRO); PERF_TRO = Perfil(lambda t: V_TRO)
FASE_TROTE = {"QuartelaTrasE": 0.0, "QuartelaD": 0.0, "QuartelaTrasD": 0.5, "QuartelaE": 0.5}
T_GAL, L_GAL, AP_GAL, ALT_GAL = 0.40, 0.62, 0.32, 0.17          # corrida de fuga: 12 quadros por ciclo, ~4,8 u/s
if os.environ.get("CERVO_CORRIDA_R1"):            # r1: passada sincronizada com a velocidade (pata varria so 0,62 u a 4,84 u/s)
    T_GAL, L_GAL, AP_GAL = 14 / 30, 0.80, 0.80 / (4.84375 * 14 / 30)   # mesma velocidade, 14 quadros, apoio ~35%
V_GAL = L_GAL / (AP_GAL * T_GAL); PERF_GAL = Perfil(lambda t: V_GAL)
FASE_GALOPE = {"QuartelaTrasE": 0.0, "QuartelaTrasD": 0.10, "QuartelaD": 0.45, "QuartelaE": 0.55}   # galope rotatorio (saltos)
Z_GAL = -0.035 if not os.environ.get("CERVO_CORRIDA_R1") else -0.05   # corpo mais baixo no galope (alcance da dianteira)
CENTRO = {"QuartelaE": -0.03, "QuartelaD": -0.03, "QuartelaTrasE": 0.0, "QuartelaTrasD": 0.0}
# CORRIDA r1 (12/11, "parece correr no lugar"): diagnostico com camera fixa mostrou deslocamento correto (1,94 u/ciclo, casco sem
# deriva) mas pata varrendo so 0,62 u sob o corpo e tronco quase sem suspensao. Correcao: ALCANCE no balanco (a pata passa do
# ponto de pouso e volta: dianteira estende a frente, traseira chega sob a barriga) + suspensao/balanço do tronco. Apoio, fases,
# fase aerea e velocidade nao mudam. So com CERVO_CORRIDA_R1=1 (sem a variavel = entrega L2 identica).
R1 = bool(os.environ.get("CERVO_CORRIDA_R1"))
ALCANCE = {"QuartelaE": 0.18, "QuartelaD": 0.18, "QuartelaTrasE": 0.16, "QuartelaTrasD": 0.16} if R1 else {k: 0.0 for k in PATAS}
R2 = bool(os.environ.get("CERVO_CORRIDA_R2"))     # r2 (12/11, "pernas dobram pra frente e pra tras"): alcance so no FIM do
if R2:                                                # balanco (pata sobe dobrada para tras e so estende a frente antes do pouso)
    ALCANCE = {"QuartelaE": 0.11, "QuartelaD": 0.11, "QuartelaTrasE": 0.09, "QuartelaTrasD": 0.09}
def alcance(k_, uu, kk=1.0):
    """avanco extra da pata no balanco (zero no levantar e no pousar: o apoio nao muda)"""
    if uu <= 0: return V((0, 0, 0))
    if R2:                                            # pico ~78% do balanco; comeca devagar (carpo/jarrete ainda dobrados)
        return V((0, -ALCANCE[k_] * kk * 2.6 * math.sin(math.pi * uu) * uu ** 2.2, 0))
    return V((0, -ALCANCE[k_] * kk * 1.6 * math.sin(math.pi * uu) * uu, 0))
SUSP, BALANCO = ((0.045, R(3)) if R2 else (0.055, R(5))) if R1 else (0.0, 0.0)   # dianteira alcanca mais a frente
def pernas(t, fases, T, ap, alt, L, perf, ext, pes, k_alt=1.0, kc=None, reach=False):
    Lf = L if callable(L) else (lambda _t: L)
    for k_, fase in fases.items():
        d, uu = passo_l(t, fase, T, ap, alt * k_alt, Lf, perf); c_ = 1.0
        if kc:
            phi = t / T + fase; tc = (math.floor(phi) - fase) * T; c_ = kc(tc) if uu == 0 else kc(tc) + (kc(tc + T) - kc(tc)) * suave(uu)
        pes[k_] = d + V((0, CENTRO[k_] * c_, 0)) + (alcance(k_, uu, k_alt) if reach else V((0, 0, 0)))
        ext["rot_pe"][k_] = rola_casco(uu) * min(1.0, k_alt * 1.5); ext["apoio"][k_] = uu == 0
if R2:
    _rola_l1 = rola_casco
    def rola_casco(u):                               # r2: boleto dobra mais no inicio do balanco (casco recolhido), volta plano no pouso
        return R(70) * math.sin(math.pi * min(1.0, u * 1.25)) ** 1.3 if u > 0 else 0.0
def cauda_bandeira(r, u, k=1.0):
    """fuga: cauda branca ERGUIDA (sinal de alarme dos cervideos) com tremor no ritmo da passada"""
    r["Cauda1"] = [(X, R(-55) * k + R(6) * math.sin(2 * math.pi * (u - 0.1)) * k)]
    r["Cauda2"] = [(X, R(-20) * k + R(8) * math.sin(2 * math.pi * (u - 0.25)) * k)]
def c_trote(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_TRO
    pernas(t, FASE_TROTE, T_TRO, AP_TRO, ALT_TRO, L_TRO, PERF_TRO, ext, pes)
    b2 = math.cos(4 * math.pi * u); sw = math.sin(2 * math.pi * u)
    r["Pelve"] = [(Y, R(1.6) * sw)]; r["Coluna3"] = [(Y, R(-1.4) * sw), (X, R(1.0) * b2)]
    r["Pescoco"] = [(X, R(-2.0) + R(1.6) * math.cos(4 * math.pi * (u - 0.15)))]; r["Cabeca"] = [(X, R(-1.2) * b2)]   # cabeca alta, estavel
    for lado in "ED": r["Escapula" + lado] = [(X, R(6) * math.cos(2 * math.pi * ((u + FASE_TROTE["Quartela" + lado]) % 1.0)))]
    r["Cauda1"] = [(X, R(-15) + R(4) * b2)]; r["Cauda2"] = [(Z, R(5) * math.sin(2 * math.pi * (u - 0.3)))]
    r["OrelhaE"] = [(X, R(-8))]; r["OrelhaD"] = [(X, R(-8))]                               # orelhas um pouco para tras
    return r, V((0, 0, -0.024 + 0.012 * b2)), pes, ext          # mais baixo: alcance da dianteira no fim do apoio
def corpo_galope(r, u, k=1.0):
    fl = math.sin(2 * math.pi * (u - 0.15)) * k                       # flexao/extensao da coluna (salto)
    r["Pelve"] = [(X, R(8) * fl)]; r["Coluna1"] = [(X, R(-5) * fl)]; r["Coluna2"] = [(X, R(-4) * fl)]; r["Coluna3"] = [(X, R(3) * fl)]
    # fuga: cabeca ALTA e a frente, compensando a oscilacao da cernelha (olhar estavel); orelhas para tras
    r["Pescoco"] = [(X, R(-6) * k - R(3) * fl)]; r["Pescoco2"] = [(X, R(-2) * k)]; r["Cabeca"] = [(X, R(6) * k + R(2) * fl)]
    for lado in "ED": r["Escapula" + lado] = [(X, R(10) * math.cos(2 * math.pi * ((u + FASE_GALOPE["Quartela" + lado]) % 1.0)) * k)]
    r["OrelhaE"] = [(X, R(-12) * k)]; r["OrelhaD"] = [(X, R(-12) * k)]
    if BALANCO: r["Raiz"] = [(X, BALANCO * k * math.sin(2 * math.pi * (u - 0.20)))]   # empina no impulso traseiro, mergulha no pouso dianteiro
    cauda_bandeira(r, u, k)
def c_corrida(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_GAL
    pernas(t, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, L_GAL, PERF_GAL, ext, pes, reach=True); corpo_galope(r, u)
    return r, V((0, 0, Z_GAL + 0.03 * math.sin(2 * math.pi * (u - 0.05)) + SUSP * math.cos(2 * math.pi * (u - 0.93)))), pes, ext
# arrancada: firma (10 quadros: cabeca sobe, peso para tras, cauda ergue) + 3 ciclos de galope crescendo; fim = quadro 0 da Corrida
T0_ARR = 10 / 30; DUR_ARR = T0_ARR + 3 * T_GAL
def k_arr(t): return suave((t - T0_ARR) / (2 * T_GAL))
PERF_ARR = Perfil(lambda t: V_GAL * k_arr(t)); PERF_ARR_G = PerfDesloc(PERF_ARR, T0_ARR)
def c_arrancada(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; k = k_arr(t); ag = janela(t, 0.0, T0_ARR + 0.10, 0.18, 0.14); tt = t - T0_ARR
    pernas(tt, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, lambda x: L_GAL * k_arr(x + T0_ARR), PERF_ARR_G, ext, pes, k_alt=k, kc=lambda x: k_arr(x + T0_ARR), reach=True)
    corpo_galope(r, tt / T_GAL, k)
    r["Pelve"] = r["Pelve"] + [(X, R(6) * ag)]; r["Pescoco"] = r["Pescoco"] + [(X, R(-10) * ag)]      # assusta: cabeca sobe antes
    cauda_bandeira(r, tt / T_GAL, max(k, ag))
    for o in ("OrelhaE", "OrelhaD"): r[o] = [(X, R(-12) * max(k, ag))]
    z = Z_GAL * k + 0.03 * k * math.sin(2 * math.pi * (tt / T_GAL - 0.05)) + SUSP * k * math.cos(2 * math.pi * (tt / T_GAL - 0.93)) - 0.02 * ag
    return r, V((0, 0.02 * ag, z)), pes, ext
# frenagem: comeca no quadro 0 da Corrida; passada encolhe ate parar; peso senta nas traseiras; cauda desce
DUR_FRE = 1.4
def k_fre(t): return 1 - suave(t / 0.95)
PERF_FRE = Perfil(lambda t: V_GAL * k_fre(t))
def c_frenagem(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; k = k_fre(t); s = janela(t, 0.30, DUR_FRE, 0.22, 0.55)
    pernas(t, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, lambda x: L_GAL * k_fre(x), PERF_FRE, ext, pes, k_alt=max(k, 0.0) ** 0.7, kc=k_fre, reach=True)
    corpo_galope(r, t / T_GAL, k)
    r["Pelve"] = r["Pelve"] + [(X, R(-7) * s)]; r["Coluna1"] = r["Coluna1"] + [(X, R(6) * s)]
    r["Pescoco"] = r["Pescoco"] + [(X, R(-6) * s)]; r["Cabeca"] = r["Cabeca"] + [(X, R(-3) * s)]   # para e olha para tras/alerta
    kz = 1 - suave((t - 0.40) / 0.9)
    z = Z_GAL * kz + 0.03 * k * math.sin(2 * math.pi * (t / T_GAL - 0.05)) + SUSP * k * math.cos(2 * math.pi * (t / T_GAL - 0.93)) - 0.015 * s
    return r, V((0, 0.006 * s, z)), pes, ext
# ---------------------------------------------------------------- TRANSICOES (Transicao do Bufalo L6, escala do cervo)
GAITS = {"Andar": dict(T=T_AND, ap=AP_AND, alt=ALT_AND, v=V_AND, fase=FASE_ANDAR, C=0.0, reach=0.0, body=lambda ph: c_andar(ph * T_AND)),
         "Trote": dict(T=T_TRO, ap=AP_TRO, alt=ALT_TRO, v=V_TRO, fase=FASE_TROTE, C=1.0, reach=0.0, body=lambda ph: c_trote(ph * T_TRO)),
         "Corrida": dict(T=T_GAL, ap=AP_GAL, alt=ALT_GAL, v=V_GAL, fase=FASE_GALOPE, C=1.0, reach=1.0, body=lambda ph: c_corrida(ph * T_GAL))}
class Transicao:
    def __init__(s, A, B, Db, dip=0.0):
        s.dip = dip; s.A, s.B = GAITS[A], GAITS[B]; gA, gB = s.A, s.B
        hB = (2 - gB["ap"]) * gB["T"]; ss_ = np.linspace(0, 1, 2001)
        M = float(np.mean(1.0 / (gA["T"] + (gB["T"] - gA["T"]) * np.array([suave(x) for x in ss_]))))
        N = math.ceil(Db * M + hB / gB["T"]); TB = gB["T"]; s.Db = Db; s.D = None
        if abs(M - 1 / TB) < 1e-9: s.D = N * TB
        else:
            D0 = (N - hB / TB) / M + hB
            for D_ in (math.floor(D0 * FPS) / FPS, math.ceil(D0 * FPS) / FPS, math.ceil(D0 * FPS) / FPS + 1 / FPS):
                Db_ = (N - D_ / TB) / (M - 1 / TB)
                if Db_ > 0.3 and D_ - Db_ >= hB - 1e-6: s.D, s.Db = D_, Db_; break
        assert s.D and s.D - s.Db >= hB - 1e-6, (A, B, s.D, s.Db, hB)
        s.Dalt = s.Db
        s.fB = {k: gB["fase"][k] + round(gA["fase"][k] - gB["fase"][k]) for k in PATAS}
        dt = 1 / 600; s.ts = np.arange(-4.0, s.D + 4.0, dt); w = np.array([s.w(t) for t in s.ts])
        T = gA["T"] + (gB["T"] - gA["T"]) * w; v = gA["v"] + (gB["v"] - gA["v"]) * w
        i0 = int(round(4.0 / dt)); phi = np.concatenate([[0.0], np.cumsum(dt / T[:-1])]); s.phi = phi - phi[i0]
        S = np.concatenate([[0.0], np.cumsum(v[:-1] * dt)]); s.S = S - S[i0]
        pD = float(np.interp(s.D, s.ts, s.phi)); s.phi = s.phi * (round(pD) / pD)     # fase final exatamente inteira
        s.pk = {k: s.phi + gA["fase"][k] + (s.fB[k] - gA["fase"][k]) * w for k in PATAS}
    def w(s, t): return suave(t / s.Db)
    def wa(s, t): return suave(t / s.Dalt)
    def par(s, nome, t, wf=None):
        ww = (wf or s.w)(t)
        if nome == "ap":
            LA = s.A["v"] * s.A["ap"] * s.A["T"]; LB = s.B["v"] * s.B["ap"] * s.B["T"]
            return (LA + (LB - LA) * ww) / (s.par("v", t) * s.par("T", t))
        return s.A[nome] + (s.B[nome] - s.A[nome]) * ww
    def v(s, t): return s.par("v", t)
    def C(s, k, t): return CENTRO[k] * s.par("C", t)
    def Sx(s, t): return float(np.interp(t, s.ts, s.S))
    def pouso(s, k, tof, n):
        t_td = tof(n); t_lo = tof(n + s.par("ap", t_td)); tp = tof(n - 1); t_lp = tof(n - 1 + s.par("ap", tp))
        if t_lp < 0: return -s.A["v"] * s.A["ap"] * s.A["T"] / 2 + CENTRO[k] * s.A["C"], t_td, t_lo
        return -(s.Sx(t_lo) - s.Sx(t_td)) / 2 + s.C(k, t_lp), t_td, t_lo
    def pernas(s, t, pes, ext):
        for k in PATAS:
            pk = s.pk[k]; tof = lambda q: float(np.interp(q, pk, s.ts)); p = float(np.interp(t, s.ts, pk)); n = math.floor(p); fr = p - n
            y_land, t_td, t_lo = s.pouso(k, tof, n); apc = s.par("ap", t_td)
            if fr < apc:
                pes[k] = V((0, y_land + s.Sx(t) - s.Sx(t_td), 0)); ext["rot_pe"][k] = 0.0; ext["apoio"][k] = True
            else:
                y0 = y_land + s.Sx(t_lo) - s.Sx(t_td); y1 = s.pouso(k, tof, n + 1)[0]
                u = (fr - apc) / (1 - apc); alt = s.par("alt", t_lo, s.wa)
                pes[k] = V((0, y0 + (y1 - y0) * suave(u), alt * math.sin(math.pi * u) ** 0.8)) + alcance(k, u, s.par("reach", t_lo))
                ext["rot_pe"][k] = rola_casco(u) * min(1.0, alt / 0.06); ext["apoio"][k] = u < 1e-3
    def __call__(s, t):
        pes = {}; ext = {"rot_pe": {}, "apoio": {}}; s.pernas(t, pes, ext); ph = float(np.interp(t, s.ts, s.phi)); w = s.w(t)
        rA, zA, _p, _e = s.A["body"](ph); rB, zB, _p, _e = s.B["body"](ph); r = {}
        for n_ in set(rA) | set(rB):
            r[n_] = [(e, a * (1 - w)) for e, a in rA.get(n_, [])] + [(e, a * w) for e, a in rB.get(n_, [])]
        return r, zA.lerp(zB, w) + V((0, 0, -s.dip * 4 * w * (1 - w))), pes, ext
TRANS = {"AndarParaTrote": Transicao("Andar", "Trote", 1.2, 0.006), "TroteParaAndar": Transicao("Trote", "Andar", 1.2, 0.006),
         "TroteParaCorrida": Transicao("Trote", "Corrida", 0.9, 0.03 if R1 else 0.012),          # r1: corpo baixa mais no meio da troca
         "CorridaParaTrote": Transicao("Corrida", "Trote", 0.9, 0.045 if R1 else 0.012)}         # (suspensao da corrida x apoio do trote)
CLIPES.update({"Trote": (c_trote, T_TRO * 5, True, V_TRO, None, 0.0), "Corrida": (c_corrida, T_GAL * 5, True, V_GAL, None, 0.0),
               "Arrancada": (c_arrancada, DUR_ARR, False, 0.0, lambda t: V_GAL * k_arr(t), 0.0),
               "Frenagem": (c_frenagem, DUR_FRE, False, 0.0, lambda t: V_GAL * k_fre(t), 0.0)})
for nm_, tr_ in TRANS.items(): CLIPES[nm_] = (tr_, tr_.D, False, 0.0, tr_.v, 0.0)
print("LOTE2", {k: round(CLIPES[k][1], 3) for k in ("Trote", "Corrida", "Arrancada", "Frenagem")}, {k: round(t_.D, 3) for k, t_ in TRANS.items()},
      "V_TRO %.2f V_GAL %.2f" % (V_TRO, V_GAL))
