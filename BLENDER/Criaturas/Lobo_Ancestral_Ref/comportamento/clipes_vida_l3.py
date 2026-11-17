# Comportamentos de vida - LOTE 3 (11/11/2026): alerta e caca. Lotes 1 e 2 aprovados pelo usuario ("Aprovado, siga").
# Carregado por exec() dentro de anim_lobo.py com LOBO_VIDA=3 (lotes 1 e 2 tambem carregam, intactos) DEPOIS da marcha v30
# (LOBO_MARCHA30=1): a espreita e o farejar andando usam marcha29 (a mesma do Andar aprovado) com outro corpo e outra passada.
# Principios de lobos reais (so principios):
# - ALERTA: congela, cabeca alta, orelhas eretas para a frente e girando para o som, cauda na horizontal, fareja o ar com o
#   focinho erguido em fungadas curtas;
# - ESPREITA: corpo baixo (pernas dobradas), cabeca na linha do dorso olhando a presa, orelhas para a frente, cauda baixa e
#   reta, passos lentos e deliberados (cada pata pousa com cuidado, passada curta, mais tempo apoiada);
# - BOTE (salto de rato): fixa a presa agachado, ajeita as traseiras, salta ALTO em arco e cai com as DIANTEIRAS juntas
#   prendendo a presa, focinho logo atras, depois as traseiras;
# - FAREJAR ANDANDO (rastro): passo lento, focinho baixo varrendo para os lados, fungadas em rajadas;
# - OLHAR PARA TRAS: pescoco e peito giram por cima do ombro, as patas ficam plantadas.
def _cp3(p): return {"raiz": list(p["raiz"]), "ossos": {k: dict(v) for k, v in p["ossos"].items()}, "pes": dict(p["pes"])}
def _janela(t, a, b, r=0.2):
    """1 dentro de [a, b], com entrada/saida suaves de r s"""
    return suave((t - a) / r) * (1.0 - suave((t - (b - r)) / r))
# ------------------------------------------------------------------ ALERTA (4,0 s, em pe, no lugar)
POSE_ALERTA = P(raiz=(0, 0.06, 0.08, -3.0),
                ossos={"Pescoco1": {"X": -14}, "Pescoco2": {"X": -8}, "Cabeca": {"X": 8}, "Peito": {"X": -2},
                       "OrelhaE": {"X": 8}, "OrelhaD": {"X": 8}, "JubaPeito": {"X": -4},
                       **{nm: {"X": (6 if i == 0 else 1.5)} for i, nm in enumerate(CAUDA)}},
                pes={"MaoE": ((0, 0, 0), 0, 0), "MaoD": ((0, 0, 0), 0, 0), "MetatarsoE": ((0, 0, 0), 0, 0), "MetatarsoD": ((0, 0, 0), 0, 0)})
def clipe_alerta(t):
    """4,0 s: congela e ergue a cabeca (0-0,35) -> vira para o som a esquerda (0,6-1,0) e fica parado -> fareja o ar com o
    focinho erguido (1,6-2,6) -> orelhas giram para o outro lado -> relaxa (3,3-4,0)"""
    p = chaves([(0.0, NEUTRO, None), (0.35, POSE_ALERTA, None), (3.3, POSE_ALERTA, None), (4.0, NEUTRO, None)])(t)
    yaw = 16.0 * _janela(t, 0.6, 3.3, 0.4) - 10.0 * _janela(t, 2.7, 3.3, 0.25)
    somar_ossos(p["ossos"], {"Pescoco2": {"Z": 0.45 * yaw}, "Cabeca": {"Z": 0.55 * yaw}, "Peito": {"Z": 0.08 * yaw}})
    ar = _janela(t, 1.6, 2.6, 0.25)                                     # fareja o ar: focinho sobe, fungadas (~5/s)
    w = max(0.0, math.sin(2 * math.pi * 5.0 * t))
    somar_ossos(p["ossos"], {"Cabeca": {"X": -7 * ar - 1.2 * w * ar}, "Pescoco1": {"X": -3 * ar}, "Mandibula": {"X": 1.0 * w * ar}})
    gira = 18.0 * _janela(t, 0.5, 2.6, 0.2) - 14.0 * _janela(t, 2.6, 3.3, 0.15)   # orelhas para o som (esquerda), depois para o outro lado
    somar_ossos(p["ossos"], {"OrelhaE": {"Z": gira}, "OrelhaD": {"Z": 0.6 * gira}})
    r = 2 * math.pi * t / 2.0                                           # respiracao contida
    somar_ossos(p["ossos"], {"Peito": {"X": -0.5 * math.sin(r)}})
    return p
# ------------------------------------------------------------------ ESPREITA (laco, andar agachado lento)
# r1: corpo 1,7 mais baixo; r2 (usuario: "a perna traseira parece se mover mais do que pode"): medido - a 1,7 o joelho dobrava
# 130-155 graus e o jarrete ate 112 (Andar: 63-98 e 73) -> corpo 1,3 com a frente 5 graus mais baixa e passo traseiro curto
# (altura 0,18, dobra 10, rolamento 4, apoio centrado 0,35): joelho ~110-127, jarrete ate ~92, faixa do jarrete 57 -> ~36.
ESP_Z = float(os.environ.get("LOBO_ESP_Z", "1.3")); ESP_PIT = float(os.environ.get("LOBO_ESP_PIT", "5"))
def corpo_espreita(t, u, pes):
    """corpo baixo e nivelado; quase sem balanco; cabeca na linha do dorso, olhos na presa; orelhas a frente; cauda baixa"""
    z = -ESP_Z - 0.012 * math.cos(4 * math.pi * u); rol = 0.6 * _ondas(u, 0.25); yaw = 0.6 * _ondas(u, 0.0)
    o = {"Pelve": {"Z": -0.8 * _ondas(u, 0.25)}, "Coluna1": {"Z": 0.5 * _ondas(u, 0.30)}, "Coluna2": {"Z": 0.5 * _ondas(u, 0.35)},
         "Peito": {"Z": 0.4 * _ondas(u, 0.40)},
         "Pescoco1": {"X": 14.0}, "Pescoco2": {"X": 4.0}, "Cabeca": {"X": -14.0 + 0.6 * math.cos(4 * math.pi * u + 0.9)},  # cabeca estavel
         "Mandibula": {"X": 0.0}, "OrelhaE": {"X": 9.0}, "OrelhaD": {"X": 9.0}, "JubaPeito": {"X": -4.0}}
    for i, nm in enumerate(CAUDA):
        k = (i + 1) / NC; o[nm] = {"X": (-10.0 if i == 0 else 1.0), "Z": 1.0 * k * _ondas(u, 0.1 + 0.25 * k)}
    for lado in ("E", "D"): o["Escapula" + lado] = {"X": 6.0 * (pes["Mao" + lado][0].y - B0["Mao" + lado].y)}
    return [0, 0, z, ESP_PIT, rol, yaw], o
ESPREITA = dict(T=64 / FPS, L=1.40, apoio=0.76, fases={"MetatarsoE": 0.0, "MaoE": 0.25, "MetatarsoD": 0.5, "MaoD": 0.75},
                alt={"D": 0.42, "T": 0.18}, flex={"D": 10.0, "T": 10.0},
                cfg=dict(rolamento={"D": 8.0, "T": 4.0}, rolo_ini=0.75, dedo_curl=14.0,
                         centro={"MaoE": -0.15, "MaoD": -0.15, "MetatarsoE": 0.35, "MetatarsoD": 0.35}, corpo=corpo_espreita))
# ------------------------------------------------------------------ FAREJAR ANDANDO (laco, seguindo rastro)
FAR_P1 = float(os.environ.get("LOBO_FAR_P1", "55")); FAR_P2 = float(os.environ.get("LOBO_FAR_P2", "-5"))
FAR_CAB = float(os.environ.get("LOBO_FAR_CAB", "-30")); FAR_DZ = float(os.environ.get("LOBO_FAR_DZ", "1.1")); FAR_PIT = float(os.environ.get("LOBO_FAR_PIT", "18"))
FAR_VAR = float(os.environ.get("LOBO_FAR_VAR", "16"))
def corpo_farejar(t, u, pes):
    # r2 (usuario: "cabeca mais proxima ao chao e se movendo esquerda-direita"): pescoco ESTICADO para a frente (60/10, cabeca -5)
    # e frente 1,0/18 graus: nariz de 2,06 para 1,50 e mais a frente das patas; varredura 9 -> 16 (sem bater nas pernas)
    # r3 (usuario: "rosto mais a frente virado ao chao, parece cheirar o pelo"): o pescoco 60/10 virava o focinho PARA TRAS (117 graus,
    # nariz 0,81 atras do peito). Agora pescoco 55/-5 + cabeca -30 + frente 1,1/18: focinho 72 graus para baixo, nariz 1,10 a frente do peito, z 1,51
    # (inclinacao 21 esticava as patas dianteiras: IK 0,13)
    """como o Andar aprovado, mais lento, com o focinho baixo varrendo o chao e fungadas"""
    raiz, o = corpo_andar29(t, u, pes)
    var = FAR_VAR * math.sin(2 * math.pi * u)                           # uma varredura E->D por ciclo
    somar_ossos(o, {"Pescoco1": {"X": FAR_P1, "Z": 0.4 * var}, "Pescoco2": {"X": FAR_P2, "Z": 0.4 * var}, "Cabeca": {"X": FAR_CAB, "Z": 0.3 * var},
                    "OrelhaE": {"X": 4.0}, "OrelhaD": {"X": 4.0}})
    w = max(0.0, math.sin(2 * math.pi * 6.0 * t)) * (1.0 if (u % 0.5) < 0.3 else 0.0)   # rajadas de fungadas
    somar_ossos(o, {"Mandibula": {"X": 1.2 * w}, "Cabeca": {"X": -0.8 * w}})
    for i, nm in enumerate(CAUDA): o[nm]["X"] = o[nm]["X"] - (4.0 if i == 0 else 0.0)
    raiz = list(raiz); raiz[2] -= FAR_DZ; raiz[3] += FAR_PIT                   # frente um pouco mais baixa
    return raiz, o
FAREJAR = dict(T=48 / FPS, L=1.70, apoio=0.66, fases=ANDAR29["fases"], alt={"D": 0.50, "T": 0.42}, flex={"D": 10.0, "T": 32.0},
               cfg=dict(rolamento={"D": 12.0, "T": 18.0}, rolo_ini=0.72, dedo_curl=16.0,
                        centro={"MaoE": 0.0, "MaoD": 0.0, "MetatarsoE": 0.55, "MetatarsoD": 0.55}, corpo=corpo_farejar))
# ------------------------------------------------------------------ OLHAR PARA TRAS (3,6 s, no lugar, por cima do ombro E)
def _pose_olha_tras():
    q = _cp3(NEUTRO)
    pz = float(os.environ.get("LOBO_OT_PEITO", "4"))
    somar_ossos(q["ossos"], {"Coluna2": {"Z": 0.55 * pz}, "Peito": {"Z": pz}, "Pescoco1": {"Z": 30, "X": -6}, "Pescoco2": {"Z": 28}, "Cabeca": {"Z": 22, "Y": 8},
                             "OrelhaE": {"X": 6, "Z": 12}, "OrelhaD": {"X": 6, "Z": 12}, "EscapulaD": {"X": -3}})
    for i, nm in enumerate(CAUDA): somar_ossos(q["ossos"], {nm: {"Z": 3 + 1.5 * i}})
    q["raiz"][5] = 2.0
    return q
POSE_OLHA_TRAS = _pose_olha_tras()
def clipe_olhar_tras(t):
    """3,6 s: ouve algo atras -> orelhas giram (0-0,3) -> pescoco e peito giram por cima do ombro esquerdo (0,3-1,0) ->
    olha parado (1,0-2,4) -> volta (2,4-3,2) -> repouso"""
    p = chaves([(0.0, NEUTRO, None), (0.3, NEUTRO, None), (1.0, POSE_OLHA_TRAS, None), (2.4, POSE_OLHA_TRAS, None), (3.2, NEUTRO, None), (3.6, NEUTRO, None)])(t)
    somar_ossos(p["ossos"], {"OrelhaE": {"Z": 10 * _janela(t, 0.0, 1.2, 0.25)}, "OrelhaD": {"Z": 10 * _janela(t, 0.0, 1.2, 0.25)}})
    return p
# ------------------------------------------------------------------ BOTE (salto de rato, 2,8 s, termina 2,4 a frente)
BOTE_D = float(os.environ.get("LOBO_BOTE_D", "2.4")); BOTE_PX = float(os.environ.get("LOBO_BOTE_PX", "0.0"))                  # distancia do salto (o clipe termina deslocado, como o Salto)
def _poses_bote():
    fixa = P(raiz=(0, 0.25, -1.6, -2.0),                               # fixa a presa: agachado, peso atras, cabeca baixa e firme
             ossos={"Pescoco1": {"X": 18}, "Pescoco2": {"X": 8}, "Cabeca": {"X": -16}, "OrelhaE": {"X": 10}, "OrelhaD": {"X": 10},
                    **{nm: {"X": (float(os.environ.get("LOBO_BOTE_CB", "25")) if i == 0 else float(os.environ.get("LOBO_BOTE_CR", "4")))} for i, nm in enumerate(CAUDA)}},
             pes={"MaoE": ((0, 0, 0), -6, 0), "MaoD": ((0, 0, 0), -6, 0), "MetatarsoE": ((0, 0.05, 0), -16, 0), "MetatarsoD": ((0, 0.05, 0), -16, 0)})
    carga = P(raiz=(0, 0.40, -1.9, -3.0), ossos=dict(fixa["ossos"]),   # carrega as traseiras
              pes={"MaoE": ((0, 0, 0), -4, 0), "MaoD": ((0, 0, 0), -4, 0), "MetatarsoE": ((0, 0.05, 0), -26, 0), "MetatarsoD": ((0, 0.05, 0), -26, 0)})
    sobe_r = (0, -0.6, 1.2, -22.0); M_s = pose_raiz(list(sobe_r) + [0, 0])   # decola: frente sobe, dianteiras recolhidas
    sobe = P(raiz=sobe_r, ossos={"Pescoco1": {"X": -2}, "Cabeca": {"X": 4}, "OrelhaE": {"X": 10}, "OrelhaD": {"X": 10}})
    for k, ext, inc in (("MaoE", V((0, 0.45, 0.85)), 75), ("MaoD", V((0, 0.45, 0.85)), 75), ("MetatarsoE", V((0, 0.35, 0.10)), 30), ("MetatarsoD", V((0, 0.35, 0.10)), 30)):
        sobe["pes"][k] = (mundo_pe(M_s, k, ext), inc, 20)
    topo_r = (0, -1.3, 2.3, 4.0); M_t = pose_raiz(list(topo_r) + [0, 0])   # alto do arco: corpo vira para baixo
    topo = P(raiz=topo_r, ossos={"Pescoco1": {"X": 10}, "Cabeca": {"X": -4}, "OrelhaE": {"X": 8}, "OrelhaD": {"X": 8},
                                 **{nm: {"X": 8} for nm in CAUDA}})
    for k, ext, inc in (("MaoE", V((0, 0.30, 0.70)), 60), ("MaoD", V((0, 0.30, 0.70)), 60), ("MetatarsoE", V((0, -0.30, 0.55)), 55), ("MetatarsoD", V((0, -0.30, 0.55)), 55)):
        topo["pes"][k] = (mundo_pe(M_t, k, ext), inc, 25)
    desce_r = (0, -BOTE_D + 0.35, 1.0, 26.0); M_d = pose_raiz(list(desce_r) + [0, 0])   # mergulha: dianteiras juntas esticadas para baixo
    desce = P(raiz=desce_r, ossos={"Pescoco1": {"X": 6}, "Cabeca": {"X": -10}, "OrelhaE": {"X": 6}, "OrelhaD": {"X": 6},
                                   **{nm: {"X": 10} for nm in CAUDA}})
    for k, ext, inc in (("MaoE", V((-0.20, -0.25, 0.10)), -10), ("MaoD", V((0.20, -0.25, 0.10)), -10), ("MetatarsoE", V((0, -0.20, 0.80)), 55), ("MetatarsoD", V((0, -0.20, 0.80)), 55)):
        desce["pes"][k] = (mundo_pe(M_d, k, ext), inc, 0)
    prende = P(raiz=(0, -BOTE_D, -1.6, 30.0),                           # r2: dianteiras prendendo, PEITO baixo e pescoco RETO para a frente
               ossos={"Pescoco1": {"X": 8}, "Pescoco2": {"X": -6}, "Cabeca": {"X": 20}, "OrelhaE": {"X": 4}, "OrelhaD": {"X": 4},
                      **{nm: {"X": 4} for nm in CAUDA}},
               pes={"MaoE": ((BOTE_PX, -BOTE_D - 0.35, 0), -8, 0), "MaoD": ((-BOTE_PX, -BOTE_D - 0.35, 0), -8, 0),
                    "MetatarsoE": ((0, -BOTE_D + 0.45, 0.30), 25, 10), "MetatarsoD": ((0, -BOTE_D + 0.45, 0.30), 25, 10)})
    # (r1 dobrava o pescoco ate o queixo no chao: o focinho afundava na juba do peito - "parece que come os proprios pelos")
    assenta = P(raiz=(0, -BOTE_D, -1.6, 30.0), ossos=dict(prende["ossos"]),
                pes={"MaoE": ((BOTE_PX, -BOTE_D - 0.35, 0), -8, 0), "MaoD": ((-BOTE_PX, -BOTE_D - 0.35, 0), -8, 0),
                     "MetatarsoE": ((0, -BOTE_D + 0.4, 0), -8, 0), "MetatarsoD": ((0, -BOTE_D + 0.4, 0), -8, 0)})
    fim = P(raiz=(0, -BOTE_D, 0, 0), pes={k: ((0, -BOTE_D, 0), 0, 0) for k in PES})
    return fixa, carga, sobe, topo, desce, prende, assenta, fim
BOTE_P = _poses_bote()
def clipe_bote(t):
    """2,8 s: fixa a presa agachado (0-0,5) e ajeita as traseiras (0,5-1,0) -> carrega (1,0-1,2) -> salta alto em arco
    (1,2-1,62) -> cai com as dianteiras juntas prendendo (1,75) -> traseiras pousam (1,95) -> segura com o focinho baixo
    (2,0-2,35) -> levanta (2,35-2,8) a 2,4 a frente"""
    fixa, carga, sobe, topo, desce, prende, assenta, fim = BOTE_P
    p = chaves([(0.0, NEUTRO, None), (0.5, fixa, None), (1.0, fixa, None), (1.2, carga, None), (1.38, sobe, None), (1.55, topo, None),
                (1.68, desce, None), (1.78, prende, None), (1.95, assenta, None), (2.35, assenta, None), (2.8, fim, {"MaoE": 0.2, "MaoD": 0.2})])(t)
    if 0.5 < t < 1.0:                                                    # ajeita as traseiras (pisadinhas alternadas) e a ponta da cauda treme
        for k, f0 in (("MetatarsoE", 0.0), ("MetatarsoD", 0.5)):
            u = ((t - 0.5) / 0.25 + f0) % 1.0; b, i_, d_ = p["pes"][k]
            p["pes"][k] = (b + V((0, 0, 0.10 * max(0.0, math.sin(2 * math.pi * u)))), i_, d_)
        for i, nm in enumerate(CAUDA[-3:]): somar_ossos(p["ossos"], {nm: {"Z": 6 * math.sin(2 * math.pi * 4.0 * t + i)}})
    if 1.95 < t < 2.35:                                                  # focinho busca a presa entre as patas
        e = math.sin(math.pi * (t - 1.95) / 0.4)                         # r2: ESTOCADA - impulso da cabeca para a frente e para baixo
        somar_ossos(p["ossos"], {"Pescoco1": {"X": 12 * e}, "Pescoco2": {"X": -4 * e}, "Cabeca": {"X": 4 * e}, "Mandibula": {"X": 14 * e}})   # (so o pescoco: girar o corpo tirava as traseiras do chao)
    return p
CLIPES.update({
    "Alerta": (clipe_alerta, 4.0, False, 0.0, {"Congela": 0.35, "FarejaAr": 1.6, "Relaxa": 3.3}),
    "Espreita": (marcha29(**ESPREITA), ESPREITA["T"], True, vel29(ESPREITA), {}),
    "FarejarAndando": (marcha29(**FAREJAR), FAREJAR["T"], True, vel29(FAREJAR), {}),
    "OlharTras": (clipe_olhar_tras, 3.6, False, 0.0, {"Olhando": 1.0, "Volta": 2.4}),
    "Bote": (clipe_bote, 2.8, False, 0.0, {"Fixa": 0.5, "Salto": 1.2, "Prende": 1.78, "Recuperado": 2.8}),
})
APOIO["Espreita"] = ESPREITA; APOIO["FarejarAndando"] = FAREJAR
# Bote r1: no agachado a cauda pendurada encostava no chao e a elevacao automatica erguia o lobo inteiro (o agachado sumia):
# a cauda vai mais alta (base 25, resto 4; menor altura 0,12). Fica FORA de CAUDA_NO_CHAO: no pouso o atraso secundario
# baixa a cauda e so o ajuste por osso do gerador a segura acima do chao (com ela dentro do conjunto entrava 0,9).
if os.environ.get("LOBO_SONDA3"): exec(open(os.environ["LOBO_SONDA3"], encoding="utf-8").read())   # medicao (so leitura), sai antes de gerar
