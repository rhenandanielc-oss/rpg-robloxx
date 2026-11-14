# ================================================================== LOTE B do Javali Silvestre (13/11/2026): aceleracao e corrida.
# Carregado por exec() em clipes_javali.py com JAVALI_LB=1; NAO altera os clipes do lote A (so acrescenta clipes).
# Mecanismo adaptado do lote 2 do Cervo-do-Bosque (clipes_cervo_l2.py: passo com passada variavel, Transicao com fase PHI e
# pouso calculado, alcance so no fim do balanco - licao da corrida r2 do cervo). Poses e numeros sao do javali.
# Parametros tecnicos [PROPOSTA] (nao sao regras do jogo): velocidades, passadas, duracoes. Fuga/defesa sao [PROPOSTA] da especie.
# Javali: galope COMPACTO (pernas curtas, passos rapidos, fase aerea curta), cabeca BAIXA e a frente (massa no pescoco/ombros),
# tronco flexiona pouco; cauda meio erguida na corrida.
def janela(t, a, b, sub=0.2, des=0.2): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
class PerfDesloc:
    def __init__(self, p, d): self.p, self.d = p, d
    def s(self, t): return self.p.s(t + self.d)
T_TRO, L_TRO, AP_TRO, ALT_TRO = 14 / 30, 0.26, 0.42, 0.06          # trote: pares diagonais, ~1,35 u/s (curso curto: perna curta)
V_TRO = L_TRO / (AP_TRO * T_TRO); PERF_TRO = Perfil(lambda t: V_TRO)
FASE_TROTE = {"QuartelaTrasE": 0.0, "QuartelaD": 0.0, "QuartelaTrasD": 0.5, "QuartelaE": 0.5}
T_GAL, L_GAL, AP_GAL, ALT_GAL = 10 / 30, 0.28, 0.30, 0.08        # corrida: galope compacto, 10 quadros por ciclo, ~2,8 u/s
# (curso de apoio limitado pela perna curta: com 0,36-0,40 a dianteira saia do alcance no fim do apoio)
V_GAL = L_GAL / (AP_GAL * T_GAL); PERF_GAL = Perfil(lambda t: V_GAL)
FASE_GALOPE = {"QuartelaTrasE": 0.0, "QuartelaTrasD": 0.09, "QuartelaD": 0.42, "QuartelaE": 0.51}   # galope rotatorio: traseiras empurram, dianteiras recebem
Z_GAL = -0.025                                                    # corpo mais baixo no galope (alcance da dianteira)
# centro do apoio no galope [PROPOSTA]: a dianteira deixava o chao esticada alem do alcance (1,04x a perna) -> apoio mais a frente
CENTRO_GAL = {"QuartelaE": -0.045, "QuartelaD": -0.045, "QuartelaTrasE": -0.01, "QuartelaTrasD": -0.01}
ALCANCE = {"QuartelaE": 0.06, "QuartelaD": 0.06, "QuartelaTrasE": 0.05, "QuartelaTrasD": 0.05}
def alcance(k_, uu, kk=1.0):
    """avanco extra da pata so no FIM do balanco (pata sobe dobrada para tras e so estende a frente antes do pouso)"""
    if uu <= 0: return V((0, 0, 0))
    return V((0, -ALCANCE[k_] * kk * 2.6 * math.sin(math.pi * uu) * uu ** 2.2, 0))
def rola_rapido(u):
    """marchas rapidas: o boleto dobra mais no inicio do balanco (casco recolhido) e volta plano no pouso"""
    return R(45) * math.sin(math.pi * min(1.0, u * 1.2)) ** 1.6 if u > 0 else 0.0
def pernas_g(t, fases, T, ap, alt, L, perf, ext, pes, k_alt=1.0, kc=None, reach=False):
    Lf = L if callable(L) else (lambda _t: L); CEN = CENTRO_GAL if reach else CENTRO
    for k_, fase in fases.items():
        d, uu, fa = passo(t, fase, T, ap, alt * k_alt, Lf, perf); c_ = 1.0
        if kc:
            phi = t / T + fase; tc = (math.floor(phi) - fase) * T; c_ = kc(tc) if uu == 0 else kc(tc) + (kc(tc + T) - kc(tc)) * suave(uu)
        pes[k_] = d + V((0, CEN[k_] * c_, 0)) + (alcance(k_, uu, k_alt) if reach else V((0, 0, 0)))
        ext["rot_pe"][k_] = rola_rapido(uu) * min(1.0, k_alt * 1.5) * fa; ext["apoio"][k_] = uu == 0
def c_trote(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_TRO
    pernas_g(t, FASE_TROTE, T_TRO, AP_TRO, ALT_TRO, L_TRO, PERF_TRO, ext, pes)
    b2 = math.cos(4 * math.pi * u); sw = math.sin(2 * math.pi * u)
    r["Pelve"] = [(Y, R(1.4) * sw)]; r["Coluna3"] = [(Y, R(-1.2) * sw), (X, R(0.8) * b2)]       # oscilacao curta do tronco
    r["Pescoco"] = [(X, R(6) + R(1.0) * math.cos(4 * math.pi * (u - 0.15)))]; r["Pescoco2"] = [(X, R(2))]   # cabeca baixa e a frente
    r["Cabeca"] = [(X, R(-1.0) * b2)]
    for lado in "ED": r["Escapula" + lado] = [(X, R(5) * math.cos(2 * math.pi * ((u + FASE_TROTE["Quartela" + lado]) % 1.0)))]
    r["Cauda1"] = [(X, R(-12) + R(4) * b2)]; r["Cauda2"] = [(Z, R(6) * math.sin(2 * math.pi * (u - 0.3)))]
    r["OrelhaE"] = [(X, R(-6))]; r["OrelhaD"] = [(X, R(-6))]
    return r, V((0, 0, -0.014 + 0.007 * b2)), pes, ext
def corpo_galope(r, u, k=1.0):
    fl = math.sin(2 * math.pi * (u - 0.15)) * k                       # flexao/extensao curta da coluna (compacto)
    r["Pelve"] = [(X, R(5) * fl)]; r["Coluna1"] = [(X, R(-3) * fl)]; r["Coluna2"] = [(X, R(-2.5) * fl)]; r["Coluna3"] = [(X, R(2) * fl)]
    # cabeca baixa e a frente; pescoco compensa a cernelha (focinho estavel)
    r["Pescoco"] = [(X, R(9) * k - R(2) * fl)]; r["Pescoco2"] = [(X, R(3) * k)]; r["Cabeca"] = [(X, R(-3) * k + R(1.5) * fl)]
    for lado in "ED": r["Escapula" + lado] = [(X, R(8) * math.cos(2 * math.pi * ((u + FASE_GALOPE["Quartela" + lado]) % 1.0)) * k)]
    r["OrelhaE"] = [(X, R(-14) * k)]; r["OrelhaD"] = [(X, R(-14) * k)]
    r["Raiz"] = [(X, R(2.5) * k * math.sin(2 * math.pi * (u - 0.20)))]   # empina no impulso traseiro, mergulha no pouso dianteiro
    r["Cauda1"] = [(X, R(-30) * k + R(6) * math.sin(2 * math.pi * (u - 0.1)) * k)]; r["Cauda2"] = [(Z, R(7) * math.sin(2 * math.pi * (u - 0.3)) * k)]
SUSP = 0.025
def c_corrida(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_GAL
    pernas_g(t, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, L_GAL, PERF_GAL, ext, pes, reach=True); corpo_galope(r, u)
    return r, V((0, 0, Z_GAL + 0.015 * math.sin(2 * math.pi * (u - 0.05)) + SUSP * math.cos(2 * math.pi * (u - 0.93)))), pes, ext
# ---------------------------------------------------------------- ARRANCADA: de parado (Repouso q0) ate o quadro 0 da Corrida
T0_ARR = 9 / 30; DUR_ARR = T0_ARR + 4 * T_GAL                     # carrega as traseiras 0,3 s; acelera 3 ciclos; 1 ciclo cheio
def k_arr(t): return suave((t - T0_ARR) / (3 * T_GAL))
PERF_ARR = Perfil(lambda t: V_GAL * k_arr(t)); PERF_ARR_G = PerfDesloc(PERF_ARR, T0_ARR)
def c_arrancada(t):
    r_ = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; k = k_arr(t); tt = t - T0_ARR
    carga = janela(t, 0.0, T0_ARR + 0.12, 0.20, 0.14)                 # carrega: garupa desce, peso nas traseiras, cabeca baixa
    pernas_g(tt, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, lambda x: L_GAL * k_arr(x + T0_ARR), PERF_ARR_G, ext, pes, k_alt=k,
             kc=lambda x: k_arr(x + T0_ARR), reach=True)
    corpo_galope(r_, tt / T_GAL, k)
    w = suave(t / (T0_ARR + 0.5 * T_GAL)); rA, zA, _p, _e = c_repouso(0.0); r = mistura(rA, r_, w)
    r["Pelve"] = r.get("Pelve", []) + [(X, R(-6) * carga)]; r["Coluna1"] = r.get("Coluna1", []) + [(X, R(6.5) * carga)]   # garupa desce sem levantar os ombros
    r["Pescoco"] = r.get("Pescoco", []) + [(X, R(4) * carga)]
    z = Z_GAL * k + 0.015 * k * math.sin(2 * math.pi * (tt / T_GAL - 0.05)) + SUSP * k * math.cos(2 * math.pi * (tt / T_GAL - 0.93)) - 0.012 * carga
    return r, zA.lerp(V((0, 0, 0)), w) + V((0, 0, z)), pes, ext          # (recuar o corpo esticava as dianteiras alem do alcance)
# ---------------------------------------------------------------- FRENAGEM: do quadro 0 da Corrida ate o quadro 0 do Repouso
T_FRE = 0.85; T_ESP_F = T_GAL                                    # a pata no ar no quadro 0 da Corrida pousa normal
DUR_FRE = T_ESP_F + T_FRE + 3 * T_GAL + 0.35                      # desacelera; cascos acertam os ultimos passos curtos; assenta
def k_fre(t): return 1 - suave((t - T_ESP_F) / T_FRE)
PERF_FRE = Perfil(lambda t: V_GAL * k_fre(t))
def c_frenagem(t):
    r_ = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; k = k_fre(t)
    pernas_g(t, FASE_GALOPE, T_GAL, AP_GAL, ALT_GAL, lambda x: L_GAL * k_fre(x), PERF_FRE, ext, pes, k_alt=max(k, 0.0) ** 0.6, kc=k_fre, reach=True)
    corpo_galope(r_, t / T_GAL, k)
    ab = janela(t, T_ESP_F + 0.10, T_ESP_F + T_FRE + 2 * T_GAL, 0.25, 0.5)                # absorve: peso nas dianteiras, traseiras recolhem
    r_["Pelve"] = r_.get("Pelve", []) + [(X, R(4) * ab)]; r_["Coluna3"] = r_.get("Coluna3", []) + [(X, R(-3) * ab)]
    r_["Pescoco"] = r_.get("Pescoco", []) + [(X, R(-5) * ab)]
    w = suave((t - T_ESP_F - 0.45 * T_FRE) / (DUR_FRE - T_ESP_F - 0.45 * T_FRE - 0.05)); rB, zB, _p, _e = c_repouso(0.0); r = mistura(r_, rB, w)
    z = Z_GAL * k + 0.015 * k * math.sin(2 * math.pi * (t / T_GAL - 0.05)) + SUSP * k * math.cos(2 * math.pi * (t / T_GAL - 0.93)) - 0.008 * ab
    return r, V((0, -0.008 * ab, z)).lerp(zB, w), pes, ext
# ---------------------------------------------------------------- TRANSICOES (Transicao do cervo/bufalo, escala do javali)
GAITS = {"Andar": dict(cen=CENTRO, T=T_AND, ap=AP_AND, alt=ALT_AND, v=V_AND, fase=FASE_ANDAR, C=1.0, reach=0.0, rola=0.0, body=lambda ph: c_andar(ph * T_AND)),
         "Trote": dict(cen=CENTRO, T=T_TRO, ap=AP_TRO, alt=ALT_TRO, v=V_TRO, fase=FASE_TROTE, C=1.0, reach=0.0, rola=1.0, body=lambda ph: c_trote(ph * T_TRO)),
         "Corrida": dict(cen=CENTRO_GAL, T=T_GAL, ap=AP_GAL, alt=ALT_GAL, v=V_GAL, fase=FASE_GALOPE, C=1.0, reach=1.0, rola=1.0, body=lambda ph: c_corrida(ph * T_GAL))}
class Transicao:
    """muda o padrao de apoios durante o avanco: periodo, velocidade, fases e altura migram juntos; cada pouso e calculado para
    o casco cair no ponto certo da marcha de destino; a fase final e inteira (termina no quadro 0 da marcha B)"""
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
        pD = float(np.interp(s.D, s.ts, s.phi)); s.phi = s.phi * (round(pD) / pD); s.NFIM = round(pD)
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
    def C(s, k, t): ww = s.w(t); return s.A["cen"][k] + (s.B["cen"][k] - s.A["cen"][k]) * ww
    def Sx(s, t): return float(np.interp(t, s.ts, s.S))
    def pouso(s, k, tof, n):
        t_td = tof(n); t_lo = tof(n + s.par("ap", t_td)); tp = tof(n - 1); t_lp = tof(n - 1 + s.par("ap", tp))
        if t_lp < 0: return -s.A["v"] * s.A["ap"] * s.A["T"] / 2 + s.A["cen"][k], t_td, t_lo
        return -(s.Sx(t_lo) - s.Sx(t_td)) / 2 + s.C(k, t_lp), t_td, t_lo
    def pernas(s, t, pes, ext):
        for k in PATAS:
            pk = s.pk[k]; tof = lambda q: float(np.interp(q, pk, s.ts)); p = float(np.interp(t, s.ts, pk)); n = math.floor(p); fr = p - n
            y_land, t_td, t_lo = s.pouso(k, tof, n); apc = s.par("ap", t_td)
            if fr < apc:
                pes[k] = V((0, y_land + s.Sx(t) - s.Sx(t_td), 0)); ext["rot_pe"][k] = 0.0; ext["apoio"][k] = True
            else:
                y0 = y_land + s.Sx(t_lo) - s.Sx(t_td); y1 = s.pouso(k, tof, n + 1)[0]
                u = (fr - apc) / (1 - apc); alt = s.par("alt", t_lo, s.wa); rr = s.par("reach", t_lo)
                pes[k] = V((0, y0 + (y1 - y0) * suave(u), alt * math.sin(math.pi * u) ** 0.8)) + alcance(k, u, rr)
                ro = s.par("rola", t_lo); ra = rola_casco(u) * (1 - ro) + rola_rapido(u) * ro   # andar: rolar leve; trote/corrida: recolhido
                ext["rot_pe"][k] = ra; ext["apoio"][k] = u < 1e-3
    def __call__(s, t):
        pes = {}; ext = {"rot_pe": {}, "apoio": {}}; s.pernas(t, pes, ext); ph = float(np.interp(t, s.ts, s.phi)); w = s.w(t)
        rA, zA, _p, _e = s.A["body"](ph); rB, zB, _p, _e = s.B["body"](ph - s.NFIM); r = {}   # B termina no proprio quadro 0
        for n_ in set(rA) | set(rB):
            r[n_] = [(e, a * (1 - w)) for e, a in rA.get(n_, [])] + [(e, a * w) for e, a in rB.get(n_, [])]
        return r, zA.lerp(zB, w) + V((0, 0, -s.dip * 4 * w * (1 - w))), pes, ext
TRANS = {"AndarParaTrote": Transicao("Andar", "Trote", 1.0, 0.004), "TroteParaAndar": Transicao("Trote", "Andar", 1.0, 0.004),
         "TroteParaCorrida": Transicao("Trote", "Corrida", 0.8, 0.010), "CorridaParaTrote": Transicao("Corrida", "Trote", 0.8, 0.012)}
CLIPES.update({"Trote": (c_trote, T_TRO * 6, True, V_TRO, None, 0.0, "laco", "laco"),
               "Corrida": (c_corrida, T_GAL * 6, True, V_GAL, None, 0.0, "laco", "laco"),
               "Arrancada": (c_arrancada, DUR_ARR, False, 0.0, lambda t: V_GAL * k_arr(t), 0.0, "Repouso q0", "Corrida q0"),
               "Frenagem": (c_frenagem, DUR_FRE, False, 0.0, lambda t: V_GAL * k_fre(t), 0.0, "Corrida q0", "Repouso q0")})
for nm_, tr_ in TRANS.items():
    a_, b_ = {"AndarParaTrote": ("Andar", "Trote"), "TroteParaAndar": ("Trote", "Andar"), "TroteParaCorrida": ("Trote", "Corrida"),
              "CorridaParaTrote": ("Corrida", "Trote")}[nm_]
    CLIPES[nm_] = (tr_, tr_.D, False, 0.0, tr_.v, 0.0, a_ + " q0", b_ + " q0")
print("LOTE_B", {k: round(CLIPES[k][1], 3) for k in ("Trote", "Corrida", "Arrancada", "Frenagem")}, {k: round(t_.D, 3) for k, t_ in TRANS.items()},
      "V_TRO %.2f V_GAL %.2f" % (V_TRO, V_GAL))
