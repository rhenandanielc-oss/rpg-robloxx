# ================================================================== LOTE E do Javali Silvestre (17/11/2026): CHIFRADA.
# Pedido do usuario (17/11): "na investida ele deve levantar a cabeca como se desse uma chifrada, ao acertar o alvo".
# Carregado depois do lote D r2 com JAVALI_LD=1 JAVALI_LD_R2=1 JAVALI_LE=1. Saida em rig/clipes_LE/. ESTUDO: sem dano/hitbox.
# Chifrada = 2 ciclos do galope da Corrida (entra e sai no quadro 0 da Corrida) + gancho das presas: abaixa um pouco o
# focinho (entra por baixo do alvo), ergue pescoco e cabeca num golpe rapido para cima e um pouco para o lado, segura um
# instante e volta. So o pescoco, a cabeca e as orelhas mudam em relacao a Corrida: no jogo o clipe e PARCIAL (so esses
# ossos, prioridade Action2) por cima da Corrida ou da RecuperacaoInvestida; as pernas continuam as do clipe de baixo.
CH_OSSOS = ("Pescoco", "Pescoco2", "Cabeca", "OrelhaE", "OrelhaD")
DUR_CH = 2 * T_GAL
# (t em s, flexao em graus (+ = abaixa), torcao lateral em graus) - o golpe sobe em ~0,12 s e volta devagar
GANCHO = [(0.0, 0.0, 0.0), (0.09, 7.0, -1.5), (0.21, -32.0, 9.0), (0.31, -27.0, 7.0), (0.52, -8.0, 2.0), (DUR_CH, 0.0, 0.0)]
def c_chifrada(t):
    r, raiz, pes, ext = c_corrida(t)
    g, z = hermite(GANCHO, t)
    soma(r, "Pescoco", [(X, R(g) * 0.50), (Z, R(z) * 0.55)])
    soma(r, "Pescoco2", [(X, R(g) * 0.22), (Z, R(z) * 0.25)])
    soma(r, "Cabeca", [(X, R(g) * 0.40), (Z, R(z) * 0.30)])       # o focinho termina mais erguido que o pescoco (presas para cima)
    orl = janela(t, 0.05, 0.50, 0.06, 0.20)
    soma(r, "OrelhaE", [(X, R(-14) * orl)]); soma(r, "OrelhaD", [(X, R(-14) * orl)])   # orelhas coladas no golpe
    return r, raiz, pes, ext
CLIPES.update({"Chifrada": (c_chifrada, DUR_CH, False, 0.0, lambda t: V_GAL, 0.0, "Corrida q0", "Corrida q0")})
print("LOTE_E", {"Chifrada": round(DUR_CH, 3), "ossos_parciais": CH_OSSOS})
