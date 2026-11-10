# Montaria M2 r3 (10/11/2026): clipes do LOBO ANCESTRAL para montar/desmontar COM PULO (so movimento). Pedido do usuario:
# "em vez do lobo subir assim e descer assim, faca com que o jogador pule". O lobo NAO deita mais (versao anterior em
# montaria/v1_deitado/): fica em pe (NEUTRO), olha para o cavaleiro, se firma antes do pulo e absorve o impacto.
# Carregado por exec() dentro de anim_lobo.py quando LOBO_MONTARIA=1 (os clipes aprovados e a execucao padrao nao mudam).
# Lado E = x+ (patas MaoE/MetatarsoE), lado D = x-. Pescoco2/Cabeca em Z positivo olham para x+.
# r3 (10/11): "quero que ele encene que esta segurando no lobo para pular" -> o cavaleiro se agarra na borda da sela.
# Tempos alinhados com o cavaleiro de teste (montaria/m2_demo_montaria.py):
#   Montar (3,0 s): 0-1,1 chega; 1,32 agarra a borda da aba; 1,35-1,6 agacha segurando (o lobo rola para o lado do puxao);
#   1,6 pula se puxando, pe no estribo; 2,0-2,3 a perna de fora passa pela garupa; 2,4 sentado.
#   Desmontar (3,2 s): 0,55 maos na aba; 0,6-1,15 a perna de fora passa pela garupa; 1,25-1,55 pendurado no flanco (o lobo
#   cede para o lado); 1,55 solta; 1,85 no chao agachado; se afasta.
def _janela(t, a, b, sa, sb):
    """0 antes de a, sobe em sa s, fica 1, desce em sb s ate b"""
    return suave((t - a) / sa) * (1 - suave((t - (b - sb)) / sb))
def _em_pe():
    return chaves([(0.0, NEUTRO, None), (1.0, NEUTRO, None)])
def c_montar(sg):
    base = _em_pe()
    def f(t):
        p = base(t)
        olha = _janela(t, 0.1, 2.8, 0.45, 0.6)
        puxa = _janela(t, 1.3, 2.25, 0.25, 0.3)                                        # cavaleiro agarrado na borda, puxando o lado
        imp = _janela(t, 2.36, 2.95, 0.08, 0.45)                                       # assenta na sela
        somar_ossos(p["ossos"], {"Pescoco2": {"Z": sg * 18 * olha}, "Cabeca": {"Z": sg * 14 * olha, "X": -4 * olha - 2 * imp},
                                 "OrelhaE": {"X": -10 * olha}, "OrelhaD": {"X": -10 * olha},
                                 "Coluna2": {"Y": -sg * 2.5 * puxa + sg * 1.0 * imp}, "Coluna1": {"Y": -sg * 1.2 * puxa}})
        p["raiz"][2] -= 0.05 * puxa + 0.08 * imp
        return p
    return f
def c_desmontar(sg):
    base = _em_pe()
    def f(t):
        p = base(t)
        olha = _janela(t, 0.4, 3.0, 0.45, 0.6)
        pend = _janela(t, 0.9, 1.75, 0.3, 0.2)                                         # cavaleiro pendurado no flanco
        solta = _janela(t, 1.6, 2.2, 0.08, 0.45)                                       # alivio quando ele solta
        somar_ossos(p["ossos"], {"Pescoco2": {"Z": sg * 16 * olha}, "Cabeca": {"Z": sg * 12 * olha},
                                 "OrelhaE": {"X": -10 * olha}, "OrelhaD": {"X": -10 * olha},
                                 "Coluna2": {"Y": -sg * 2.5 * pend + sg * 0.8 * solta}, "Coluna1": {"Y": -sg * 1.2 * pend}})
        p["raiz"][2] += -0.05 * pend + 0.02 * solta
        return p
    return f
CLIPES.update({
    "Montar_E": (c_montar(1), 3.0, False, 0.0, {"Agarra": 1.32, "Pulo": 1.6, "Sentado": 2.4}),
    "Montar_D": (c_montar(-1), 3.0, False, 0.0, {"Agarra": 1.32, "Pulo": 1.6, "Sentado": 2.4}),
    "Desmontar_E": (c_desmontar(1), 3.2, False, 0.0, {"Pendurado": 1.25, "Solta": 1.55, "NoChao": 1.85}),
    "Desmontar_D": (c_desmontar(-1), 3.2, False, 0.0, {"Pendurado": 1.25, "Solta": 1.55, "NoChao": 1.85}),
})
