# ================================================================== LOTE D r2 do Javali Silvestre (13/11/2026): refino de PESO.
# Carregado depois de clipes_javali_ld.py com JAVALI_LD_R2=1; sobrescreve SO os clipes refinados (a versao r1 continua
# reproduzivel sem a variavel). Saida versionada em rig/clipes_LD_r2/. ESTUDO: sem dano/hitbox; numeros [PROPOSTA].
# Diagnostico (medido no r1):
#  - RecuperacaoInvestida: mantinha 2,8 u/s por 0,33 s e so entao freava (1,21 u nos primeiros 0,4 s; 1,98 u no total, quase a
#    propria investida 2,15 u) -> lia como uma segunda corrida; depois ficava 1,3 s quase parada (giro < 1 grau/quadro).
#  - Ameaca: duas patadas identicas; levantar-raspar e voltar eram dois arcos separados com inversao seca (16 graus/quadro).
#  - ReacaoImpacto: o corpo recuava e voltava sozinho numa mola (cos) antes do passo de recuperacao (q20 ja de volta).
#  - Derrota: o tombo usava suave() (desacelera antes do chao) -> o flanco "pousava" sem peso.
#  - Investida: pico de 45 graus/quadro = dobra rapida do casco no galope, igual a Corrida aprovada -> mantida.
def hermite(pts, u):
    """curva suave por pontos (u, y, z) com tangentes por diferencas (inicio/fim parados)"""
    if u <= pts[0][0]: return pts[0][1], pts[0][2]
    if u >= pts[-1][0]: return pts[-1][1], pts[-1][2]
    i = max(j for j in range(len(pts) - 1) if pts[j][0] <= u)
    def tg(j, c):
        if j == 0 or j == len(pts) - 1: return 0.0
        return (pts[j + 1][c] - pts[j - 1][c]) / (pts[j + 1][0] - pts[j - 1][0])
    u0, u1 = pts[i][0], pts[i + 1][0]; h = u1 - u0; s_ = (u - u0) / h
    h00, h10, h01, h11 = 2 * s_ ** 3 - 3 * s_ ** 2 + 1, s_ ** 3 - 2 * s_ ** 2 + s_, -2 * s_ ** 3 + 3 * s_ ** 2, s_ ** 3 - s_ ** 2
    return tuple(h00 * pts[i][c] + h10 * h * tg(i, c) + h01 * pts[i + 1][c] + h11 * h * tg(i + 1, c) for c in (1, 2))
# patada como UM gesto: ergue e estende a frente, toca leve, RASPA para tras arrastando, ergue e volta ao lugar
PATADA = [(0.0, 0.0, 0.0), (0.16, -0.012, 0.032), (0.30, -0.016, 0.006), (0.60, 0.052, 0.004), (0.80, 0.030, 0.026), (1.0, 0.0, 0.0)]
def patada(t, t0, dur, amp):
    u = (t - t0) / dur
    if u <= 0 or u >= 1: return None
    y, z = hermite(PATADA, u); return V((0, y * amp, max(0.002, z * amp)))
DUR_AM = 1.8
def c_ameaca(t):
    r = base_rep(); k = suave(t / 0.5); pose_ameaca(r, k); pes = {}; ext = {"apoio": {}}
    # peso sai da dianteira D ANTES de cada patada e volta depois (tronco rola para a E, garupa firma)
    tr = janela(t, 0.30, 1.05, 0.20, 0.18) + 0.8 * janela(t, 1.00, 1.62, 0.16, 0.18)
    for t0, dur, amp in ((0.48, 0.52, 1.0), (1.08, 0.46, 0.75)):   # 2a patada menor e mais curta (nao e copia da 1a)
        d = patada(t, t0, dur, amp)
        if d is not None: pes["QuartelaD"] = d; ext["apoio"]["QuartelaD"] = False
    soma(r, "Coluna3", [(Y, R(-2.2) * min(1.0, tr))]); soma(r, "Pelve", [(Y, R(-1.0) * min(1.0, tr))])
    raspa = sum(janela(t, t0 + 0.30 * dur, t0 + 0.62 * dur, 0.06, 0.06) * amp for t0, dur, amp in ((0.48, 0.52, 1.0), (1.08, 0.46, 0.75)))
    soma(r, "Pescoco", [(X, R(2.0) * raspa)])                         # cabeca acompanha a raspada (empurra o peso para a frente)
    return r, REP0[1] + V((0.007 * min(1.0, tr), -0.012 * k - 0.004 * raspa, -0.010 * k)), pes, ext
# ---------------------------------------------------------------- RECUPERACAO r2: freia nos primeiros apoios e assenta
T_FR2 = 0.45                                                      # desaceleracao concentrada (~1,4 ciclo de galope)
def k_r2(t): return 1 - suave(t / T_FR2)
PERF_R2 = Perfil(lambda t: V_GAL * k_r2(t))
def recolhe(t): return janela(t, 0.10, 0.85, 0.20, 0.30)          # traseiras se recolhem sob o corpo durante a freada
T_NO_AR = T_GAL * (1 - AP_GAL)                                    # pousos com x < isto sao de patas que ja estavam no ar no q0:
def k_pouso(x): return 1.0 if x < T_NO_AR else k_r2(x)            # pousam como na Investida (emenda limpa); a freada vem nos seguintes
DUR_RI = T_FR2 + 3 * T_GAL + 0.25
def c_recuperacao(t):
    r_ = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; k = k_r2(t)
    kc_ = {"QuartelaE": k_pouso, "QuartelaD": k_pouso,             # dianteiras: centro do galope -> repouso
           "QuartelaTrasE": lambda x: k_pouso(x) + 5.0 * recolhe(x), "QuartelaTrasD": lambda x: k_pouso(x) + 5.0 * recolhe(x)}   # -0,01 x 5 = 5 cm a frente
    for k_, fase in FASE_GALOPE.items():
        d, uu, fa = passo(t, fase, T_GAL, AP_GAL, ALT_GAL * max(k, 0.0) ** 0.6, lambda x: L_GAL * k_pouso(x), PERF_R2)
        phi = t / T_GAL + fase; n_ = math.floor(phi); f_ = phi - n_; tc = (n_ - fase) * T_GAL; kc = kc_[k_]
        dc = CENTRO_GAL[k_] * (kc(tc + T_GAL) - kc(tc))
        if uu == 0 and f_ >= AP_GAL and abs(dc) > 0.002:            # passo curto, mas o centro do apoio muda: a pata DA o passo
            uu = (f_ - AP_GAL) / (1 - AP_GAL); fa = 1.0                # (antes ela deslizava ate 4 cm "apoiada")
            d = d + V((0, 0, min(ALT_GAL, 0.02 + abs(dc)) * math.sin(math.pi * uu) ** 0.8))
        c_ = kc(tc) if uu == 0 else kc(tc) + (kc(tc + T_GAL) - kc(tc)) * suave(uu)
        pes[k_] = d + V((0, CENTRO_GAL[k_] * c_, 0)) + alcance(k_, uu, max(k, 0.0) ** 0.6)
        ext["rot_pe"][k_] = rola_rapido(uu) * min(1.0, max(k, 0.0) ** 0.6 * 1.5) * fa; ext["apoio"][k_] = uu == 0
    corpo_investida(r_, t / T_GAL, k)
    ab = janela(t, 0.05, 0.95, 0.18, 0.45)                         # ombros recebem o peso: frente desce, garupa sobe um pouco
    soma(r_, "Pelve", [(X, R(3) * ab)]); soma(r_, "Coluna3", [(X, R(-1.3) * ab)]); r_["Raiz"] = r_.get("Raiz", []) + [(X, R(1.0) * ab)]   # (mais forte: boleto -1,1 mm)
    rB, zB, _p, _e = c_alerta(DUR_AL); w = suave((t - 0.25) / (DUR_RI - 0.35))   # focinho sobe e o corpo vai ao Alerta
    r = mistura(r_, rB, w)
    z = Z_GAL * k + 0.015 * k * math.sin(2 * math.pi * (t / T_GAL - 0.05)) + SUSP * k * math.cos(2 * math.pi * (t / T_GAL - 0.93)) - 0.005 * ab
    return r, V((0, -0.006 * ab, z)).lerp(zB, w), pes, ext
# ---------------------------------------------------------------- REACAO r2: o empurrao leva o corpo, a pata segura, ele se recompoe
DUR_RE = 1.3
def c_reacao(t):
    r = base_rep(); pes = {}; ext = {"apoio": {}}
    emp = suave(t / 0.09) * (1 - suave((t - 0.40) / 0.55))          # corpo empurrado para tras e assim fica ate se recompor
    con = suave(t / 0.07) * (1 - suave((t - 0.12) / 0.35))          # contracao rapida do tronco e do pescoco
    soma(r, "Coluna2", [(X, R(-5) * con)]); soma(r, "Coluna3", [(X, R(-3) * con)]); soma(r, "Pelve", [(X, R(2) * con)])
    soma(r, "Pescoco", [(X, R(-9) * con - R(3) * emp), (Z, R(7) * emp)]); soma(r, "Cabeca", [(X, R(-4) * con), (Z, R(4) * emp)])
    orl = janela(t, 0.03, 1.0, 0.07, 0.35)
    soma(r, "OrelhaE", [(X, R(-25) * orl)]); soma(r, "OrelhaD", [(X, R(-25) * orl)]); soma(r, "Cauda1", [(X, R(12) * orl)])
    # a dianteira E recua JUNTO com o empurrao e segura o peso; quando ele se recompoe, ela volta ao lugar
    if t < 0.70: d_, a_ = pata_no_ar("QuartelaE", t, 0.06, 0.20, 0.05, 0.03)        # (r2a: o limite t = 0,70 fazia a pata pular 5 cm)
    else: d_, a_ = pata_no_ar("QuartelaE", t, 0.70, 0.26, -0.05, 0.025); d_ = V((0, 0.05, 0)) + d_
    pes["QuartelaE"] = d_
    if not a_: ext["apoio"]["QuartelaE"] = False
    return r, REP0[1] + V((0.006 * emp, 0.026 * emp, -0.008 * emp)), pes, ext
# ---------------------------------------------------------------- DERROTA r2: o tombo ACELERA ate o flanco bater no chao
T_ROLA0, T_ROLA = 0.95, 0.62
def rolar(t):
    u = (t - T_ROLA0) / T_ROLA
    if u <= 0: return 0.0
    if u < 1: return u * u * (1.6 - 0.6 * u)                      # comeca devagar (desequilibrio) e acelera ate o impacto
    tb = t - (T_ROLA0 + T_ROLA)
    return 1.0 + 0.06 * math.exp(-tb / 0.10) * math.sin(math.pi * min(1.0, tb / 0.16)) if tb < 0.6 else 1.0   # quique curto e amortecido
_c_derrota_r1 = c_derrota
def c_derrota(t):
    r, raiz, pes, ext = _c_derrota_r1(t)
    r["Raiz"] = [(Y, ROLA * rolar(t))]
    imp = janela(t, T_ROLA0 + T_ROLA - 0.02, T_ROLA0 + T_ROLA + 0.35, 0.04, 0.25)   # impacto: cabeca e cauda sacodem com o choque
    soma(r, "Pescoco2", [(Z, R(5) * imp)]); soma(r, "Cauda1", [(Z, R(-10) * imp)])
    return r, raiz, pes, ext
def c_derrotado(t):
    r, raiz, pes, ext = c_derrota(DUR_DER); return r, raiz, pes, ext
REF_EXTRA.update({"AmeacaFim": (c_ameaca, DUR_AM), "DerrotaFim": (c_derrota, DUR_DER)})
CLIPES.update({"Ameaca": (c_ameaca, DUR_AM, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "AmeacaFim"),
               "RecuperacaoInvestida": (c_recuperacao, DUR_RI, False, 0.0, lambda t: V_GAL * k_r2(t), 0.0, "InvestidaFim", "AlertaFim"),
               "ReacaoImpacto": (c_reacao, DUR_RE, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "Derrota": (c_derrota, DUR_DER, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "DerrotaFim"),
               "Derrotado": (c_derrotado, 1.0, True, 0.0, None, 0.0, "DerrotaFim", "laco (pose mantida)")})
print("LOTE_D_R2", {k: round(CLIPES[k][1], 3) for k in ("Ameaca", "RecuperacaoInvestida", "ReacaoImpacto", "Derrota")})
