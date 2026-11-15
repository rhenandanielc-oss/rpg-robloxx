# ================================================================== LOTE C do Javali Silvestre (13/11/2026): vida selvagem.
# Carregado por exec() em clipes_javali.py com JAVALI_LC=1; NAO altera os lotes A/B (so acrescenta clipes).
# Farejar, Fucar, Alerta, AlertaParaRepouso. Cascos plantados (sem deslocamento); entram e saem no quadro 0 do Repouso,
# exceto AlertaParaRepouso (entra no ultimo quadro do Alerta). Duracoes e amplitudes sao [PROPOSTA].
# Focinho ao chao: ext["focinho"] = (altura alvo do ponto mais baixo da cabeca, fator 0..1) -> o gerador abaixa o pescoco por
# bissecao ate o focinho/presas ficarem exatamente nessa altura (nunca abaixo do chao). Pescoco curto: o javali alcanca o chao
# so com o pescoco (o cervo precisava abrir as dianteiras).
REP0 = c_repouso(0.0)                                # pose do quadro 0 do Repouso (entrada/saida)
def base_rep(): return {k: list(v) for k, v in REP0[0].items()}
def soma(r, nome, eixos): r[nome] = r.get(nome, []) + eixos
def orelhas_frente(r, k, lado_e=0.0, lado_d=0.0):
    """orelhas viradas para o estimulo (+X = para a frente nesta montagem; Z abre/fecha)"""
    soma(r, "OrelhaE", [(X, R(14) * k), (Z, R(lado_e) * k)]); soma(r, "OrelhaD", [(X, R(14) * k), (Z, R(lado_d) * k)])
# ---------------------------------------------------------------- FAREJAR: focinho perto do chao, 3 buscas curtas, volta
DUR_FAR = 4.4
def c_farejar(t):
    r = base_rep(); desce = suave(t / 0.85) * (1 - suave((t - 3.45) / 0.85))
    # 3 buscas: o focinho vai para um lado/outro e da toques curtos (sobe 2 cm e desce de novo)
    buscas = [(1.05, -9), (1.85, 7), (2.65, -3)]; giro = 0.0; toque = 0.0
    for t0, ang in buscas:
        j = janela(t, t0 - 0.25, t0 + 0.55, 0.22, 0.25); giro += ang * j
        toque += pulso(t, 100.0, t0, 0.22) + 0.6 * pulso(t, 100.0, t0 + 0.24, 0.18)    # duas fungadas por busca
    soma(r, "Pescoco", [(Z, R(giro) * 0.6)]); soma(r, "Pescoco2", [(Z, R(giro) * 0.4)]); soma(r, "Cabeca", [(Z, R(giro) * 0.3), (X, R(3) * toque)])
    soma(r, "Coluna3", [(X, R(2.0) * desce)]); soma(r, "Coluna2", [(X, R(-0.8) * desce)])   # peso vai um pouco para a frente
    orelhas_frente(r, 0.6 * desce)
    zt = 0.045 + 0.02 * min(1.0, toque) * 0.0 - 0.015 * min(1.0, toque)                    # fungada: focinho desce 1,5 cm
    return r, REP0[1] + V((0, -0.004 * desce, -0.006 * desce)), {}, {"focinho": (zt, desce)}
# ---------------------------------------------------------------- FUCAR: focinho no chao, empurroes curtos, contrapeso
DUR_FUC = 5.4
def c_fucar(t):
    r = base_rep(); desce = suave(t / 0.95) * (1 - suave((t - 4.35) / 0.95))
    emp = [1.25, 2.05, 2.85, 3.6]; e = 0.0; vol = 0.0
    for t0 in emp:
        f = (t - t0) / 0.6
        if 0 <= f <= 1:
            e += math.sin(math.pi * f) ** 2                     # empurra (focinho levanta a terra para a frente)
            vol += math.sin(2 * math.pi * f) * math.sin(math.pi * f)   # e recua
    lado = math.sin(2 * math.pi * (t - 1.2) / 1.6) * janela(t, 1.0, 4.2, 0.4, 0.4)
    # empurrao: tronco vai para a frente (cascos fixos), cabeca gira o disco do focinho para cima; pescoco empurra
    soma(r, "Cabeca", [(X, R(-9) * e), (Z, R(4) * lado)]); soma(r, "Pescoco", [(Z, R(5) * lado)])
    soma(r, "Coluna3", [(X, R(2.5) * desce + R(1.5) * e)]); soma(r, "Coluna1", [(X, R(-1.5) * e)])
    soma(r, "Pelve", [(X, R(-1.5) * e)])                        # contrapeso: garupa firma para tras
    orelhas_frente(r, 0.3 * desce)
    soma(r, "Cauda1", [(Z, R(10) * math.sin(2 * math.pi * t / 0.7) * janela(t, 1.2, 3.9, 0.3, 0.3))])   # cauda abana enquanto fuca
    zt = 0.004 + 0.012 * max(0.0, vol)                          # focinho encosta no chao (4 mm) e sobe um pouco ao recuar
    raiz = REP0[1] + V((0, -0.006 * desce - 0.010 * e + 0.004 * max(0.0, vol), -0.008 * desce))
    return r, raiz, {}, {"focinho": (zt, desce)}
# ---------------------------------------------------------------- ALERTA: interrompe, ergue a cabeca, orelhas no estimulo
DUR_AL = 1.4
def pose_alerta(r, k):
    soma(r, "Pescoco", [(X, R(-11) * k)]); soma(r, "Pescoco2", [(X, R(-4) * k)]); soma(r, "Cabeca", [(X, R(4) * k)])   # focinho nivelado
    soma(r, "Coluna3", [(X, R(-1.2) * k)]); soma(r, "Pelve", [(X, R(0.8) * k)])
    orelhas_frente(r, k, -6, 6)
    soma(r, "Cauda1", [(X, R(-10) * k)])                       # cauda sobe um pouco (tensao)
def k_alerta(t):
    """sobe rapido (0,35 s), passa um pouco e assenta numa pose sustentavel"""
    return suave(t / 0.35) * (1 + 0.12 * math.sin(math.pi * min(1.0, max(0.0, (t - 0.25) / 0.6))))
def c_alerta(t):
    r = base_rep(); k = k_alerta(t); pose_alerta(r, k)
    return r, REP0[1] + V((0, 0.003 * suave(t / 0.35), 0.004 * suave(t / 0.35))), {}, {}
def c_alerta_para_repouso(t):
    w = suave(t / DUR_AR); rA, zA, _p, _e = c_alerta(DUR_AL); rB = base_rep()
    r = mistura(rA, rB, w)
    sopro = janela(t, 0.15, 0.95, 0.3, 0.4)                     # solta o ar: costelas descem, pescoco relaxa
    soma(r, "Coluna2", [(X, R(1.2) * sopro)]); soma(r, "Pescoco", [(X, R(2.5) * sopro)])
    return r, zA.lerp(REP0[1], w), {}, {}
DUR_AR = 1.6
REF_EXTRA = {"AlertaFim": (c_alerta, DUR_AL)}
FOCINHO_SUAVE = ("Farejar", "Fucar")                 # angulo do pescoco em 2 passadas (sem salto quando o ponto mais baixo troca)
CLIPES.update({"Farejar": (c_farejar, DUR_FAR, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "Fucar": (c_fucar, DUR_FUC, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "Alerta": (c_alerta, DUR_AL, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "AlertaFim (pose sustentavel)"),
               "AlertaParaRepouso": (c_alerta_para_repouso, DUR_AR, False, 0.0, lambda t: 0.0, 0.0, "AlertaFim", "Repouso q0")})
print("LOTE_C", {k: CLIPES[k][1] for k in ("Farejar", "Fucar", "Alerta", "AlertaParaRepouso")})
