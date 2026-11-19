# ================================================================== LOTE F do Javali Silvestre (17/11/2026): BEBER.
# Pedido (IA de vivencia 17/11): o javali bebe numa beirada firme de lagoa; nao havia clipe de beber. Clipe MINIMO, sem
# redesenhar o rig: igual ao Fucar na estrutura (Repouso q0 -> Repouso q0, cascos plantados), mas o ponto mais baixo da
# cabeca (disco do focinho) desce ate a LINHA D'AGUA, que no jogo fica a ZT_AGUA acima do plano dos cascos (o animal para
# com as dianteiras na lamina rasa). 4 goles: o focinho mergulha 1,5 cm e sobe; a cabeca sobe um pouco ao engolir.
# Carregado com JAVALI_LC=1 JAVALI_LF=1 (usa base_rep/orelhas_frente/soma do lote C). Numeros [PROPOSTA]/[A TESTAR].
ZT_AGUA = 0.09                                       # m acima do plano dos cascos (x escala do modelo no jogo)
DUR_BEB = 5.2
def c_beber(t):
    r = base_rep(); desce = suave(t / 0.9) * (1 - suave((t - (DUR_BEB - 0.95)) / 0.95))
    goles = [1.25, 2.05, 2.85, 3.65]; g = 0.0; eng = 0.0
    for t0 in goles:
        f = (t - t0) / 0.5
        if 0 <= f <= 1: g += math.sin(math.pi * f) ** 2                   # focinho mergulha e volta
        f2 = (t - t0 - 0.35) / 0.4
        if 0 <= f2 <= 1: eng += math.sin(math.pi * f2) ** 2              # engole: garganta/cabeca sobem um pouco
    soma(r, "Cabeca", [(X, R(-4) * eng)])
    soma(r, "Coluna3", [(X, R(2.2) * desce)]); soma(r, "Coluna2", [(X, R(-0.8) * desce)])   # peso nas dianteiras
    orelhas_frente(r, 0.35 * desce)
    soma(r, "Cauda1", [(Z, R(7) * math.sin(2 * math.pi * t / 0.8) * janela(t, 1.1, 4.1, 0.3, 0.3))])
    zt = ZT_AGUA - 0.015 * g + 0.012 * eng
    return r, REP0[1] + V((0, -0.005 * desce, -0.007 * desce)), {}, {"focinho": (zt, desce)}
FOCINHO_SUAVE = tuple(FOCINHO_SUAVE) + ("Beber",)
CLIPES.update({"Beber": (c_beber, DUR_BEB, False, 0.0, lambda t: 0.0, 0.0, "Repouso q0", "Repouso q0")})
print("LOTE_F", {"Beber": DUR_BEB, "zt_agua_m": ZT_AGUA})
