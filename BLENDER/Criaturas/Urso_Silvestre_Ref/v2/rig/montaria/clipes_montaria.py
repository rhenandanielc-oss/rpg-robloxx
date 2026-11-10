# Montaria M2 (09/11/2026): clipes do URSO para montar/desmontar (so movimento). Pedido do usuario: "animacao de subida, a
# montaria no urso e animacao de descida". Decisao proposta e aprovada ("Aprovar e seguir"): o urso DEITA (pose do clipe
# Deitar, ja aprovada) para o cavaleiro subir e levanta com ele; dois lados. Carregado por exec() dentro de anim_urso.py
# quando URSO_MONTARIA=1 (os 18 clipes aprovados e a execucao padrao nao mudam).
# Lado E = x+ (patas MaoE/PeE), lado D = x-. Pescoco/cabeca giram em Z positivo para olhar para x+.
# Tempos alinhados com o cavaleiro de teste (montaria/m2_demo_montaria.py):
#   Montar (6,4 s): 0,15 olha para o cavaleiro; 0,3-2,3 deita; 2,3-4,4 o cavaleiro sobe (pe no antebraco, maos na aba e na
#   alca, perna passa pela garupa; o urso absorve o peso); 4,4-6,4 levanta com ele e termina no repouso.
#   Desmontar (6,2 s): 0,3-2,3 deita com o cavaleiro; 2,4-3,9 ele desce pelo lado; 4,2-6,2 levanta.
T_DEITA0 = 0.30                                        # inicio da descida (c_deitar comeca em t = 0)
def _deitar_em(t):
    return c_deitar(max(0.0, min(DUR_DEI, t)))
def c_montar(sg):
    def f(t):
        if t < 4.4: rots, raiz, pes, ext = _deitar_em(t - T_DEITA0)
        else: rots, raiz, pes, ext = _deitar_em(DUR_DEI - (t - 4.4))                 # levantar = deitar ao contrario (clipe aprovado)
        olha = janela(t, 0.15, 5.6, 0.45, 0.7); pisa = janela(t, 2.45, 3.1, 0.08, 0.3); puxa = janela(t, 2.9, 3.5, 0.1, 0.3)
        senta = janela(t, 3.5, 4.2, 0.08, 0.35)
        rots["Pescoco"] = rots.get("Pescoco", []) + [(Z, sg * R(20) * olha)]; rots["Cabeca"] = rots.get("Cabeca", []) + [(Z, sg * R(16) * olha)]
        rots["OrelhaE"] = [(X, R(-10) * olha)]; rots["OrelhaD"] = [(X, R(-10) * olha)]
        rots["Coluna2"] = rots.get("Coluna2", []) + [(Y, -sg * R(1.5) * pisa)]           # rola um pouco para o lado do peso
        return rots, raiz + V((0, 0, -0.05 * pisa - 0.05 * puxa - 0.07 * senta)), pes, ext
    return f
def c_desmontar(sg):
    def f(t):
        if t < 4.2: rots, raiz, pes, ext = _deitar_em(t - T_DEITA0)
        else: rots, raiz, pes, ext = _deitar_em(DUR_DEI - (t - 4.2))
        olha = janela(t, 2.6, 5.4, 0.45, 0.7); perna = janela(t, 2.4, 2.95, 0.1, 0.25); sai = janela(t, 2.95, 3.6, 0.1, 0.35)
        rots["Pescoco"] = rots.get("Pescoco", []) + [(Z, sg * R(18) * olha)]; rots["Cabeca"] = rots.get("Cabeca", []) + [(Z, sg * R(14) * olha)]
        rots["OrelhaE"] = [(X, R(-10) * olha)]; rots["OrelhaD"] = [(X, R(-10) * olha)]
        rots["Coluna2"] = rots.get("Coluna2", []) + [(Y, -sg * R(1.5) * sai)]
        return rots, raiz + V((0, 0, -0.04 * perna + 0.05 * sai)), pes, ext
    return f
CLIPES.update({
    "Montar_E": (c_montar(1), 6.4, False, 0.0, None), "Montar_D": (c_montar(-1), 6.4, False, 0.0, None),
    "Desmontar_E": (c_desmontar(1), 6.2, False, 0.0, None), "Desmontar_D": (c_desmontar(-1), 6.2, False, 0.0, None),
})
