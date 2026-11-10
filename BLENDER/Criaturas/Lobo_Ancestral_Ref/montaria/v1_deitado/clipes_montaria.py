# Montaria M2 (10/11/2026): clipes do LOBO ANCESTRAL para montar/desmontar (so movimento). Pedido do usuario: "a animacao de
# subida e de descida" (sela leve M1 aprovada 10/11). Como no Urso (aprovado 09/11): o lobo DEITA (poses do clipe Deitar ja
# aprovado: NEUTRO -> COTOV -> DEIT, cabeca erguida) para o cavaleiro subir e LEVANTA com ele (poses do LevantarDeitado
# aprovado: DEIT -> APOIO -> agachado -> NEUTRO). Dois lados. Carregado por exec() dentro de anim_lobo.py quando
# LOBO_MONTARIA=1 (os clipes aprovados e a execucao padrao nao mudam).
# Lado E = x+ (patas MaoE/MetatarsoE), lado D = x-. Pescoco2/Cabeca em Z positivo olham para x+.
# Tempos alinhados com o cavaleiro de teste (montaria/m2_demo_montaria.py):
#   Montar (6,2 s): 0,15 olha para o cavaleiro; 0,3-2,2 deita; 2,3-4,0 o cavaleiro sobe (maos na pegada e no assento, a
#   perna de fora passa pela garupa; o lobo absorve o peso); 4,1-6,2 levanta com ele e termina no repouso.
#   Desmontar (6,0 s): 0,3-2,2 deita com o cavaleiro; 2,3-3,7 ele desce pelo lado; 3,9-6,0 levanta.
def _janela(t, a, b, sa, sb):
    """0 antes de a, sobe em sa s, fica 1, desce em sb s ate b"""
    return suave((t - a) / sa) * (1 - suave((t - (b - sb)) / sb))
_LEV_PES = {"MaoE": 0.18, "MaoD": 0.18, "MetatarsoE": 0.18, "MetatarsoD": 0.18}
_AGACH = agachado_pose()
def _deita_levanta(t0d, t_lev):
    """deita de t0d a t0d+1,9 (Deitar aprovado ate DEIT) e levanta a partir de t_lev (LevantarDeitado aprovado a partir de DEIT)"""
    return chaves([(0.0, NEUTRO, None), (t0d, NEUTRO, None), (t0d + 0.9, COTOV, {"MaoE": 0.30, "MaoD": 0.30}),
                   (t0d + 1.9, DEIT, {"MetatarsoE": 0.22, "MetatarsoD": 0.22}), (t_lev, DEIT, None),
                   (t_lev + 0.6, APOIO_P, _LEV_PES), (t_lev + 1.3, _AGACH, {"MaoE": 0.25, "MaoD": 0.25}), (t_lev + 1.8, NEUTRO, None)])
def c_montar(sg):
    base = _deita_levanta(0.3, 4.1)
    def f(t):
        p = base(t)
        olha = _janela(t, 0.15, 5.4, 0.45, 0.7); pisa = _janela(t, 2.5, 3.2, 0.1, 0.3); senta = _janela(t, 3.3, 4.0, 0.1, 0.35)
        somar_ossos(p["ossos"], {"Pescoco2": {"Z": sg * 18 * olha}, "Cabeca": {"Z": sg * 14 * olha, "X": -4 * olha},
                                 "OrelhaE": {"X": -10 * olha}, "OrelhaD": {"X": -10 * olha},
                                 "Coluna2": {"Y": -sg * 2.0 * pisa}})                  # rola um pouco para o lado do peso
        p["raiz"][2] -= 0.04 * pisa + 0.06 * senta                                     # absorve o peso
        return p
    return f
def c_desmontar(sg):
    base = _deita_levanta(0.3, 3.9)
    def f(t):
        p = base(t)
        olha = _janela(t, 2.3, 5.2, 0.45, 0.7); perna = _janela(t, 2.3, 2.9, 0.1, 0.25); sai = _janela(t, 2.9, 3.6, 0.1, 0.35)
        somar_ossos(p["ossos"], {"Pescoco2": {"Z": sg * 16 * olha}, "Cabeca": {"Z": sg * 12 * olha},
                                 "OrelhaE": {"X": -10 * olha}, "OrelhaD": {"X": -10 * olha},
                                 "Coluna2": {"Y": -sg * 2.0 * sai}})
        p["raiz"][2] += -0.03 * perna + 0.04 * sai
        return p
    return f
CLIPES.update({
    "Montar_E": (c_montar(1), 6.2, False, 0.0, {"Deitado": 2.2, "Sentado": 4.0, "EmPe": 5.9}),
    "Montar_D": (c_montar(-1), 6.2, False, 0.0, {"Deitado": 2.2, "Sentado": 4.0, "EmPe": 5.9}),
    "Desmontar_E": (c_desmontar(1), 6.0, False, 0.0, {"Deitado": 2.2, "NoChao": 3.6, "EmPe": 5.7}),
    "Desmontar_D": (c_desmontar(-1), 6.0, False, 0.0, {"Deitado": 2.2, "NoChao": 3.6, "EmPe": 5.7}),
})
