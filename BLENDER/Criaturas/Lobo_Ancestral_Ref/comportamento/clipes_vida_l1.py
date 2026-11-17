# Comportamentos de vida - LOTE 1 (11/11/2026). Pedido do usuario: "animacoes realistas, ele vivera naturalmente na floresta
# ancestral: beber, comer, descansar, uivar, entre todas as outras de um lobo da vida real... o mais proximo da realidade".
# Carregado por exec() dentro de anim_lobo.py com LOBO_VIDA=1 (os clipes aprovados e a execucao padrao nao mudam).
# Todos NO LUGAR, sobre as poses e ajustes ja aprovados (cara_no_chao do dormir, agachado do salto, respiracao).
# Referencia de comportamento (lobos reais, so principios): bebe em pe com as dianteiras um pouco abertas e o peito baixo,
# lambendo em rajadas de ~3/s e erguendo a cabeca para olhar em volta; come prendendo com as patas/boca e puxando com o pescoco
# para cima e para tras, mastigando de lado; fareja com o nariz rente ao chao em varreduras curtas; sacode o corpo da cabeca
# para a cauda (~4,5 Hz, amortecido); espreguica em "reverencia" (frente estica e desce, traseira alta) e depois estica a
# traseira; boceja com a boca bem aberta, cabeca erguida e olhos fechando.
def _pose_beber():
    """em pe, dianteiras um pouco abertas e a frente, peito mais baixo; o focinho desce ate a agua (z 0,10)"""
    p = P(raiz=(0, -0.10, -float(os.environ.get("LOBO_VIDA_DZ", "1.5")), float(os.environ.get("LOBO_VIDA_PIT", "24"))), ossos={"OrelhaE": {"X": 6}, "OrelhaD": {"X": 6}, **{nm: {"X": -6} for nm in CAUDA}},
          pes={"MaoE": ((0.30, -0.45, 0), -6, 0), "MaoD": ((-0.30, -0.45, 0), -6, 0), "MetatarsoE": ((0, 0, 0), -4, 0), "MetatarsoD": ((0, 0, 0), -4, 0)})
    return cara_no_chao(p, alvo=0.10, nome="beber")
def _pose_cabeca_alta_bebendo():
    """intervalo: ergue a cabeca para olhar em volta, ainda na postura de beber"""
    return P(raiz=(0, -0.10, -0.55, 6.0), ossos={"Pescoco1": {"X": 6}, "OrelhaE": {"X": -4}, "OrelhaD": {"X": -4}, **{nm: {"X": -6} for nm in CAUDA}},
             pes={"MaoE": ((0.30, -0.45, 0), -6, 0), "MaoD": ((-0.30, -0.45, 0), -6, 0), "MetatarsoE": ((0, 0, 0), -4, 0), "MetatarsoD": ((0, 0, 0), -4, 0)})
POSE_BEBER = _pose_beber(); POSE_BEBER_ALTA = _pose_cabeca_alta_bebendo()
def clipe_beber(t):
    """7,0 s: desce (0-1,0) -> lambe 2,2 s -> ergue e olha (3,2-4,4) -> desce e lambe (4,4-6,0) -> ergue ao repouso (6,0-7,0)"""
    p = chaves([(0.0, NEUTRO, {"MaoE": 0.12, "MaoD": 0.12}), (1.0, POSE_BEBER, None), (3.2, POSE_BEBER, None), (3.6, POSE_BEBER_ALTA, None),
                (4.1, POSE_BEBER_ALTA, None), (4.5, POSE_BEBER, None), (6.0, POSE_BEBER, None), (7.0, NEUTRO, {"MaoE": 0.12, "MaoD": 0.12})])(t)
    lambe = (1.0 < t < 3.2) or (4.5 < t < 6.0)
    if lambe:                                                          # rajadas de lambidas: boca abre/fecha e a cabeca sobe/desce um pouco
        f = 3.0; w = math.sin(2 * math.pi * f * t)
        somar_ossos(p["ossos"], {"Mandibula": {"X": 7 + 6 * w}, "Cabeca": {"X": -2.5 * max(0.0, w)}, "Pescoco2": {"X": 1.2 * w}})
    if 3.6 <= t <= 4.1:                                                # olha para um lado e para o outro
        y = 18 * math.sin(math.pi * (t - 3.6) / 0.5 * 2)
        somar_ossos(p["ossos"], {"Pescoco2": {"Z": 0.5 * y}, "Cabeca": {"Z": 0.5 * y}})
    return p
def _pose_comer():
    p = P(raiz=(0, 0.05, -float(os.environ.get("LOBO_VIDA_DZ", "1.5")), float(os.environ.get("LOBO_VIDA_PIT", "24"))), ossos={"OrelhaE": {"X": -8}, "OrelhaD": {"X": -8}, **{nm: {"X": -8} for nm in CAUDA}},
          pes={"MaoE": ((0.18, -0.35, 0), -8, 0), "MaoD": ((-0.10, -0.15, 0), -8, 0), "MetatarsoE": ((0, 0.05, 0), -10, 0), "MetatarsoD": ((0, 0.05, 0), -10, 0)})
    return cara_no_chao(p, alvo=0.18, nome="comer")
POSE_COMER = _pose_comer()
def _puxa():
    """puxa o pedaco: peso para tras, pescoco ergue e torce, boca fechada"""
    q = {"raiz": list(POSE_COMER["raiz"]), "ossos": {k: dict(v) for k, v in POSE_COMER["ossos"].items()}, "pes": dict(POSE_COMER["pes"])}
    q["raiz"][1] += 0.30; q["raiz"][3] -= 4.0
    somar_ossos(q["ossos"], {"Pescoco1": {"X": -14}, "Pescoco2": {"X": -8, "Z": 10}, "Cabeca": {"X": 6, "Z": 8, "Y": 10}, "Mandibula": {"X": 2}})
    return q
POSE_PUXA = _puxa()
def _mastiga():
    q = P(raiz=(0, 0.10, -0.25, 3.0), ossos={"Pescoco1": {"X": 8}, "Cabeca": {"X": 6, "Z": -8, "Y": -8}, "OrelhaE": {"X": -4}, "OrelhaD": {"X": -4}, **{nm: {"X": -6} for nm in CAUDA}},
          pes={"MaoE": ((0.18, -0.35, 0), -6, 0), "MaoD": ((-0.10, -0.15, 0), -6, 0), "MetatarsoE": ((0, 0.05, 0), -8, 0), "MetatarsoD": ((0, 0.05, 0), -8, 0)})
    return q
POSE_MASTIGA = _mastiga()
def clipe_comer(t):
    """8,0 s: desce (0-1,0) -> morde (1,0-1,4) -> puxa (1,4-1,9) -> volta (1,9-2,3) -> morde/puxa de novo (2,3-3,6)
    -> ergue um pouco e mastiga de lado (3,6-6,4) -> desce de novo (6,4-7,0) -> volta ao repouso (7,0-8,0)"""
    p = chaves([(0.0, NEUTRO, {"MaoE": 0.15}), (1.0, POSE_COMER, None), (1.4, POSE_COMER, None), (1.9, POSE_PUXA, None), (2.3, POSE_COMER, None),
                (2.7, POSE_COMER, None), (3.2, POSE_PUXA, None), (3.6, POSE_MASTIGA, None), (6.4, POSE_MASTIGA, None),
                (7.0, POSE_COMER, None), (8.0, NEUTRO, {"MaoE": 0.15})])(t)
    if 1.0 < t < 1.4 or 2.3 < t < 2.7:                                   # morde: abre e fecha forte
        u = ((t - 1.0) if t < 1.4 else (t - 2.3)) / 0.4; somar_ossos(p["ossos"], {"Mandibula": {"X": 24 * math.sin(math.pi * u)}})
    if 1.4 < t < 1.9 or 2.7 < t < 3.2:                                   # tranco do puxao (sacode a cabeca)
        u = ((t - 1.4) if t < 1.9 else (t - 2.7)) / 0.5; somar_ossos(p["ossos"], {"Cabeca": {"Z": 9 * math.sin(4 * math.pi * u) * (1 - u)}})
    if 3.6 < t < 6.4:                                                  # mastiga de lado, com pausas
        w = math.sin(2 * math.pi * 2.2 * t); pausa = 0.0 if 4.9 < t < 5.2 else 1.0
        somar_ossos(p["ossos"], {"Mandibula": {"X": (9 + 8 * w) * pausa}, "Cabeca": {"Y": 3 * w * pausa}})
    return p
def _pose_fareja(lado):
    p = P(raiz=(0, -0.05, -1.25, 19.0), ossos={"OrelhaE": {"X": 10}, "OrelhaD": {"X": 10}, **{nm: {"X": 2} for nm in CAUDA}},
          pes={"MaoE": ((0.05, -0.10, 0), -4, 0), "MaoD": ((-0.05, -0.10, 0), -4, 0), "MetatarsoE": ((0, 0, 0), -2, 0), "MetatarsoD": ((0, 0, 0), -2, 0)})
    q = cara_no_chao(p, alvo=0.35, nome="farejar")
    somar_ossos(q["ossos"], {"Pescoco1": {"Z": 12 * lado}, "Pescoco2": {"Z": 10 * lado}, "Cabeca": {"Z": 6 * lado}})
    return q
POSE_FAREJA_E, POSE_FAREJA_D = _pose_fareja(1), _pose_fareja(-1)
def clipe_farejar(t):
    """4,0 s em laco: nariz rente ao chao varrendo E -> D -> E, com fungadas rapidas (6/s) e orelhas para a frente"""
    u = (t / 4.0) % 1.0
    p = chaves([(0.0, POSE_FAREJA_E, None), (0.5, POSE_FAREJA_D, None), (1.0, POSE_FAREJA_E, None)])(u)
    f = math.sin(2 * math.pi * 6.0 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * u * 2))
    somar_ossos(p["ossos"], {"Cabeca": {"X": 1.5 * f}, "Mandibula": {"X": 1.0 + 0.8 * f}})
    return p
def clipe_sacudir(t):
    """1,8 s: firma as patas e sacode da cabeca para a cauda (~4,5 Hz, onda que atrasa ao longo da coluna, amortecida)"""
    firme = P(raiz=(0, 0.0, -0.10, 0.0), pes={"MaoE": ((0.12, 0, 0), -4, 0), "MaoD": ((-0.12, 0, 0), -4, 0), "MetatarsoE": ((0.12, 0, 0), -4, 0), "MetatarsoD": ((-0.12, 0, 0), -4, 0)})
    p = chaves([(0.0, NEUTRO, {"MaoE": 0.1, "MaoD": 0.1, "MetatarsoE": 0.1, "MetatarsoD": 0.1}), (0.3, firme, None), (1.5, firme, None), (1.8, NEUTRO, None)])(t)
    if 0.25 < t < 1.6:
        e = math.sin(math.pi * (t - 0.25) / 1.35) * math.exp(-1.2 * (t - 0.25))
        cadeia = [("Cabeca", 0.0, 22), ("Pescoco2", 0.06, 16), ("Pescoco1", 0.10, 12), ("Peito", 0.14, 9), ("Coluna2", 0.18, 10), ("Coluna1", 0.22, 10), ("Pelve", 0.26, 8)]
        for nm, atraso, a in cadeia:
            somar_ossos(p["ossos"], {nm: {"Y": a * e * math.sin(2 * math.pi * 4.5 * (t - atraso))}})
        for i, nm in enumerate(CAUDA):
            somar_ossos(p["ossos"], {nm: {"Z": (10 + 4 * i) * e * math.sin(2 * math.pi * 4.5 * (t - 0.3 - 0.04 * i))}})
        for nm in ("OrelhaE", "OrelhaD"): somar_ossos(p["ossos"], {nm: {"X": -18 * e * abs(math.sin(2 * math.pi * 4.5 * t))}})
        for nm in ("JubaE", "JubaD", "JubaPeito"): somar_ossos(p["ossos"], {nm: {"Z": 12 * e * math.sin(2 * math.pi * 4.5 * (t - 0.05))}})
        p["raiz"][4] += 4.0 * e * math.sin(2 * math.pi * 4.5 * (t - 0.15))
    return p
# 11/11 r2 (usuario: "ao se espreguicar suas patas dobram muito"): as dianteiras iam so 1,3 a frente e o antebraco dobrava
# sob o peito (malha do antebraco 0,63 dentro do chao, pata -60). Agora esticam 2,8 a frente como na reverencia real, com o
# cotovelo perto do chao e a pata apoiada (-38).
# 11/11 r3 (usuario: "arrume as patas que estao dobradas ao espreguicar e nao deixe a cabeca entrar dentro da perna"):
# medido no modelo de patas retas - a -38 a sola rolava 8 graus e os dedos ficavam curvados (ponta para baixo); a -53 (plano
# da perna) a pata fica chapada, reta para a frente, na linha do antebraco. O pescoco erguia pouco (-10) e o focinho entrava
# no antebraco (196 vertices a < 0,45 do osso) -> pescoco -28/-12 e cabeca +4: 0 vertices, focinho a 0,92 do chao.
# 11/11 r4 (usuario: "encoste a cabeca no chao ou na perna, e arrume a perna que agora vira e fica torta"): medido - o polo do
# cotovelo (feito para a marcha) deixava o plano de dobra do cotovelo 85 graus fora do plano da perna: o cotovelo entrava sob o
# peito e o antebraco torcia. Agora o polo fica no plano VERTICAL ombro->pata (`polo_frente_vert`, peso conforme a reverencia):
# plano 10 graus; as patas vao 0,3 para fora (alinhadas aos ombros, pernas paralelas) e giram 3 graus para fora (`yaw_pe`;
# apontavam 3 para dentro). A cabeca desce ate o QUEIXO encostar no chao entre as patas (cara_no_chao), sem entrar nas pernas.
REV_DY = float(os.environ.get("LOBO_REV_DY", "2.8")); REV_INC = float(os.environ.get("LOBO_REV_INC", "-53"))
REV_PX = float(os.environ.get("LOBO_REV_PX", "0.3")); REV_YAW = float(os.environ.get("LOBO_REV_YAW", "3"))
_REV = {}
def _rever():
    if "p" not in _REV:
        col = float(os.environ.get("LOBO_REV_COL", "12"))
        r = P(raiz=(0, -0.45, -float(os.environ.get("LOBO_REV_Z", "0.3")), float(os.environ.get("LOBO_REV_PIT", "12"))),
              ossos={"Coluna1": {"X": col}, "Coluna2": {"X": col * 1.3}, "Peito": {"X": col * 1.3}, "Pescoco1": {"X": -10}, "Cabeca": {"X": -6},
                     "OrelhaE": {"X": -10}, "OrelhaD": {"X": -10}, **{nm: {"X": 8} for nm in CAUDA}},
              pes={"MaoE": ((REV_PX, -REV_DY, 0.0), REV_INC, 0), "MaoD": ((-REV_PX, -REV_DY, 0.0), REV_INC, 0), "MetatarsoE": ((0, 0.10, 0), -6, 0), "MetatarsoD": ((0, 0.10, 0), -6, 0)})
        r = cara_no_chao(r, float(os.environ.get("LOBO_REV_QUEIXO", "0.05")), "espreguicar", amin=-60)
        somar_ossos(r["ossos"], {"Mandibula": {"X": 6}}); _REV["p"] = r
    return _REV["p"]
def clipe_espreguicar(t):
    """4,0 s: reverencia (dianteiras esticadas a frente, peito baixo, queixo no chao, traseira alta, cauda alta) -> volta ->
    estica a traseira (corpo a frente, pernas traseiras esticadas para tras) -> repouso"""
    rever = _rever()
    tras = P(raiz=(0, -0.30, -0.15, -4.0), ossos={"Pescoco1": {"X": -12}, "Cabeca": {"X": 4}, "OrelhaE": {"X": -6}, "OrelhaD": {"X": -6}, **{nm: {"X": -4} for nm in CAUDA}},
             pes={"MaoE": ((0, 0, 0), 6, 0), "MaoD": ((0, 0, 0), 6, 0), "MetatarsoE": ((0, 0.75, 0.0), 30, 0), "MetatarsoD": ((0, 0.55, 0.0), 26, 0)})
    fim = NEUTRO                                                       # (as dianteiras ficam plantadas; as traseiras voltam com passo)
    p = chaves([(0.0, NEUTRO, None), (0.9, rever, {"MaoE": 0.30, "MaoD": 0.30}), (1.7, rever, None), (2.3, NEUTRO, {"MaoE": 0.25, "MaoD": 0.25}),
                (2.9, tras, {"MetatarsoE": 0.25, "MetatarsoD": 0.25}), (3.4, tras, None), (4.0, fim, {"MetatarsoE": 0.25, "MetatarsoD": 0.25})])(t)
    p["eixo_perna"] = True        # 11/11: a pata dobra no PLANO DA PERNA (como a marcha v27)
    w = suave(t / 0.9) if t < 0.9 else (1.0 if t < 1.7 else 1.0 - suave((t - 1.7) / 0.6))
    if w > 0:
        p["polo_frente_vert"] = w; p["yaw_pe"] = {"MaoE": REV_YAW * w, "MaoD": -REV_YAW * w}
    return p
def clipe_bocejar(t):
    """2,4 s: ergue a cabeca, abre a boca bem (orelhas para tras, olhos fecham), fecha com estalo, sacode de leve a cabeca"""
    alto = P(raiz=(0, 0.05, 0.02, -2.0), ossos={"Pescoco1": {"X": -10}, "Pescoco2": {"X": -6}, "Cabeca": {"X": -12}, "OrelhaE": {"X": -24}, "OrelhaD": {"X": -24}})
    p = chaves([(0.0, NEUTRO, None), (0.5, alto, None), (1.6, alto, None), (2.4, NEUTRO, None)])(t)
    boca = suave((t - 0.4) / 0.45) * (1 - suave((t - 1.5) / 0.18))
    somar_ossos(p["ossos"], {"Mandibula": {"X": 32 * boca}})
    olhos(p, curva_olhos(t, [(0.0, 0.0), (0.5, 0.2), (0.8, 0.9), (1.5, 0.9), (1.8, 0.0)]))
    if 1.7 < t < 2.2: somar_ossos(p["ossos"], {"Cabeca": {"Y": 8 * math.sin(2 * math.pi * 5 * (t - 1.7)) * (1 - (t - 1.7) / 0.5)}})
    return p
CLIPES.update({
    "Beber": (clipe_beber, 7.0, False, 0.0, {"Desceu": 1.0, "Lambe": 1.0, "Olha": 3.6, "Lambe2": 4.5, "Ergue": 6.0, "Fim": 7.0}),
    "Comer": (clipe_comer, 8.0, False, 0.0, {"Desceu": 1.0, "Mordida": 1.2, "Puxao": 1.65, "Mordida2": 2.5, "Puxao2": 2.95, "Mastiga": 3.6, "Fim": 8.0}),
    "Farejar": (clipe_farejar, 4.0, True, 0.0, {}),
    "Sacudir": (clipe_sacudir, 1.8, False, 0.0, {"Inicio": 0.3, "Fim": 1.6}),
    "Espreguicar": (clipe_espreguicar, 4.0, False, 0.0, {"Reverencia": 0.9, "Traseira": 2.9, "Fim": 4.0}),
    "Bocejar": (clipe_bocejar, 2.4, False, 0.0, {"BocaAberta": 0.85, "Fecha": 1.6}),
})
CAUDA_NO_CHAO.add("Espreguicar")                                # reverencia: o peito desce de proposito (sem a elevacao automatica)
