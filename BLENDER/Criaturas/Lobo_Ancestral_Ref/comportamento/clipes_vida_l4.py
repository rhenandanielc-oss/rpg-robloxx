# Comportamentos de vida - LOTE 4 (12/11/2026): vocal e social. Lotes 1, 2 e 3 aprovados pelo usuario ("Aprovado, siga").
# Carregado por exec() dentro de anim_lobo.py com LOBO_VIDA=4 (lotes 1 e 2 tambem carregam, intactos; o 3 nao e necessario).
# Os clipes da base "Uivo" e "Rosnar" (aprovados) ficam INTACTOS; aqui entram versoes novas, mais proximas do lobo real.
# Principios de lobos reais (so principios):
# - UIVO: inspira (peito enche), ergue o focinho bem alto, boca em "O" (pouco aberta, labios arredondados - nao escancarada),
#   orelhas um pouco para tras, olhos semicerrados; a nota sobe, sustenta e cai no fim; sentado ou em pe, cauda relaxada;
# - LATIDO DE AVISO: lobos latem pouco - um "uf" curto e grave de alarme: postura alta e rigida, orelhas eretas para a frente,
#   cauda na horizontal, cada latido e um tranco do peito com a boca abrindo e fechando rapido;
# - GANIDO: corpo um pouco encolhido, orelhas para tras e para os lados, cabeca baixa e inclinada, cauda baixa abanando
#   curto, boca quase fechada tremendo, levanta uma pata dianteira, olhar suplicante;
# - ROSNADO DE AMEACA (ofensivo): cabeca baixa na linha do dorso, olhar fixo, orelhas eretas para a frente, PELOS da nuca,
#   juba e dorso ERICADOS, cauda alta e rigida, peso para a frente, boca entreaberta mostrando os dentes, vibracao no peito;
#   (o rig nao tem osso de labio: o franzir do labio nao e possivel sem um osso/forma nova - ver ficha)
# - SAUDACAO (social, ao lider/companheiro): corpo baixo, orelhas coladas para tras, cabeca baixa olhando para cima,
#   cauda baixa abanando largo com o quadril rebolando, focinho que "lambe" o ar.
# - CAUDA CONFORME O ESTADO: relaxada/pendente (uivo), horizontal (alarme), baixa abanando curto (ganido), alta e rigida
#   (ameaca), baixa abanando largo (saudacao).
def _cp4(p): return {"raiz": list(p["raiz"]), "ossos": {k: dict(v) for k, v in p["ossos"].items()}, "pes": dict(p["pes"])}
def _jan(t, a, b, r=0.2):
    """1 dentro de [a, b], com entrada/saida suaves de r s"""
    return suave((t - a) / r) * (1.0 - suave((t - (b - r)) / r))
def _mais(base, ossos=None, raiz=None):
    q = _cp4(base)
    if ossos: somar_ossos(q["ossos"], ossos)
    if raiz:
        for i, d in enumerate(raiz): q["raiz"][i] += d
    return q
def _cauda(ang_base, ang_resto, z=0.0):
    return {nm: {"X": (ang_base if i == 0 else ang_resto), "Z": z * (i + 1) / NC} for i, nm in enumerate(CAUDA)}
# ------------------------------------------------------------------ UIVO (comum aos dois)
UIV_P1 = float(os.environ.get("LOBO_UIV_P1", "-32")); UIV_P2 = float(os.environ.get("LOBO_UIV_P2", "-24")); UIV_CAB = float(os.environ.get("LOBO_UIV_CAB", "-36"))   # medido: focinho 61 graus acima da horizontal (+4 na nota)
UIV_BOCA = float(os.environ.get("LOBO_UIV_BOCA", "11"))
def _uivo_cabeca(f):
    """f 0..1: quanto da cabeca de uivo (focinho para o alto)"""
    return {"Pescoco1": {"X": UIV_P1 * f}, "Pescoco2": {"X": UIV_P2 * f}, "Cabeca": {"X": UIV_CAB * f},
            "OrelhaE": {"X": -8 * f, "Y": 6 * f}, "OrelhaD": {"X": -8 * f, "Y": -6 * f}, "JubaPeito": {"X": -4 * f}}
def _uivo(t, base, dur, sobe_z=0.03):
    """linha do tempo (dur ~7 s): orelhas atentas (0-0,6) -> inspira, peito enche (0,6-1,2) -> focinho sobe (1,0-1,8) ->
    nota sobe (1,8-2,6) e sustenta ate dur-1,4 com tremor leve -> nota cai (cabeca desce um pouco, boca fecha) -> volta"""
    p = _cp4(base); fim = dur - 1.4
    f = suave((t - 1.0) / 0.8) * (1 - suave((t - (fim + 0.5)) / 0.8))
    somar_ossos(p["ossos"], _uivo_cabeca(f))
    somar_ossos(p["ossos"], {"OrelhaE": {"X": 5 * _jan(t, 0.0, 1.1, 0.3)}, "OrelhaD": {"X": 5 * _jan(t, 0.0, 1.1, 0.3)}})
    ins = _jan(t, 0.6, 1.9, 0.5)                                         # inspiracao: peito enche e o corpo sobe um fio
    exp = suave((t - 1.8) / (fim - 1.8)) * (1 - suave((t - fim) / 0.6))  # expira devagar durante o uivo
    somar_ossos(p["ossos"], {"Peito": {"X": -3.0 * ins + 1.5 * exp}, "JubaPeito": {"X": 2.0 * ins}})
    p["raiz"][2] += sobe_z * ins
    nota = _jan(t, 1.8, fim, 0.5)                                        # nota: sobe (cabeca mais alta) e cai no fim
    sobe = _jan(t, 1.9, 2.8, 0.35)
    cai = suave((t - (fim - 0.5)) / 0.6) * (1 - suave((t - (fim + 0.4)) / 0.5))
    somar_ossos(p["ossos"], {"Cabeca": {"X": -4 * sobe + 6 * cai}, "Pescoco2": {"X": 3 * cai}})
    trem = 0.6 * math.sin(2 * math.pi * 5.0 * t) * nota                  # vibrato da voz
    somar_ossos(p["ossos"], {"Mandibula": {"X": (UIV_BOCA + 2.0 * sobe - 4.0 * cai) * nota + trem},
                             "Cabeca": {"X": -0.5 * math.sin(2 * math.pi * 0.6 * t) * nota}})
    olhos(p, 0.35 * nota)                                                # olhos semicerrados
    return p
UIVO_SENT_D = 7.0
def clipe_uivo_sentado(t):
    """7,0 s, comeca e termina no Sentado (encaixa entre Sentar/Sentado/LevantarSentado); cauda continua no chao"""
    return _uivo(t, SENT, UIVO_SENT_D)
UIVO_PE_D = 6.4
POSE_UIVO_PE = P(raiz=(0, 0.06, 0.0, -4.0), ossos={"Peito": {"X": -2}, **_cauda(-6, 1.0)})   # em pe: peso um pouco atras, cauda pendente
def clipe_uivo_em_pe(t):
    """6,4 s, em pe no lugar: assenta o peso (0-0,6) e uiva como o sentado; cauda pendente relaxada"""
    base = chaves([(0.0, NEUTRO, None), (0.6, POSE_UIVO_PE, None), (UIVO_PE_D - 0.6, POSE_UIVO_PE, None), (UIVO_PE_D, NEUTRO, None)])(t)
    return _uivo(t, base, UIVO_PE_D, 0.0)          # em pe o corpo nao sobe (esticava as patas: IK 0,10)
# ------------------------------------------------------------------ LATIDO DE AVISO (2,4 s, em pe)
LAT_PELO = float(os.environ.get("LOBO_LAT_PELO", "0"))   # r2 16/11: 0 (aprovado 12/11 = 8; a nuca girada abre a aba atras da juba)
POSE_ALARME = P(raiz=(0, 0.05, 0.08, -3.0),
                ossos={"Pescoco1": {"X": -12}, "Pescoco2": {"X": -6}, "Cabeca": {"X": 6}, "Peito": {"X": -2},
                       "OrelhaE": {"X": 10}, "OrelhaD": {"X": 10}, "PeloNuca1": {"X": LAT_PELO}, "PeloNuca2": {"X": LAT_PELO}, **_cauda(10, 1.5)})
LATIDOS = (0.75, 1.30)
def clipe_latido(t):
    """2,4 s: postura alta de alarme (0-0,4) -> dois latidos curtos (0,75 e 1,30): tranco do peito, cabeca para a frente,
    boca abre e fecha rapido -> fica atento -> relaxa (1,9-2,4)"""
    p = chaves([(0.0, NEUTRO, None), (0.4, POSE_ALARME, None), (1.9, POSE_ALARME, None), (2.4, NEUTRO, None)])(t)
    for t0 in LATIDOS:
        u = (t - t0) / 0.24
        if 0.0 <= u <= 1.0:
            b = math.sin(math.pi * u) ** 0.6                                 # golpe rapido
            g = math.sin(math.pi * min(1.0, u / 0.55)) if u < 0.55 else 0.0  # boca: abre rapido, fecha
            somar_ossos(p["ossos"], {"Peito": {"X": 3.5 * b}, "Coluna2": {"X": 1.5 * b}, "Pescoco1": {"X": 5 * b}, "Cabeca": {"X": 3 * b},
                                     "Mandibula": {"X": 16 * g}, "JubaPeito": {"X": 4 * b}})
            p["raiz"][1] -= 0.07 * b; p["raiz"][2] -= 0.03 * b
    return p
# ------------------------------------------------------------------ GANIDO (3,6 s, em pe)
POSE_GANIDO = P(raiz=(0, 0.10, -0.22, 2.0),
                ossos={"Pescoco1": {"X": 10}, "Pescoco2": {"X": 2}, "Cabeca": {"X": -12, "Y": 7}, "Peito": {"X": 1},
                       "OrelhaE": {"X": -20, "Y": 12}, "OrelhaD": {"X": -20, "Y": -12}, **_cauda(-16, 1.0)},
                pes={"MaoE": ((0, 0, 0), -6, 0), "MaoD": ((0, 0, 0), -6, 0), "MetatarsoE": ((0, 0, 0), -10, 0), "MetatarsoD": ((0, 0, 0), -10, 0)})
def clipe_ganido(t):
    """3,6 s: encolhe com as orelhas para tras (0-0,5) -> gane com a boca quase fechada tremendo, cabeca inclinada que troca
    de lado (2,0), cauda baixa abanando curto -> levanta a pata dianteira esquerda (1,0-1,7) -> volta (3,0-3,6)"""
    p = chaves([(0.0, NEUTRO, None), (0.5, POSE_GANIDO, None), (3.0, POSE_GANIDO, None), (3.6, NEUTRO, None)])(t)
    w = _jan(t, 0.5, 3.0, 0.3)
    som = _jan(t, 0.6, 1.5, 0.15) + _jan(t, 1.9, 2.8, 0.15)               # dois ganidos
    somar_ossos(p["ossos"], {"Mandibula": {"X": (1.5 + 1.0 * math.sin(2 * math.pi * 9.0 * t)) * som},
                             "Cabeca": {"X": -2.5 * som, "Y": -14 * suave((t - 1.8) / 0.4) * w},   # focinho sobe no ganido; inclinacao troca de lado
                             "Pescoco2": {"X": -2 * som}})
    for i, nm in enumerate(CAUDA):                                        # abana curto e rapido, baixa
        k = (i + 1) / NC; somar_ossos(p["ossos"], {nm: {"Z": 9 * k * math.sin(2 * math.pi * 3.2 * t - 1.2 * k) * w}})
    pa = _jan(t, 1.0, 1.7, 0.2)                                           # pata dianteira esquerda se ergue (suplica)
    if pa > 0:
        b, inc, dd = p["pes"]["MaoE"]
        p["pes"]["MaoE"] = (b + V((0, -0.12 * pa, 0.45 * pa)), inc + 45 * pa, dd + 18 * pa)
        p["raiz"][0] -= 0.10 * pa                                       # peso passa para a direita
    olhos(p, 0.12 * w)
    return p
# ------------------------------------------------------------------ ROSNADO DE AMEACA (3,4 s, em pe, ofensivo)
ROS_PELO = float(os.environ.get("LOBO_ROS_PELO", "0"))   # r2 16/11: 0 (aprovado 12/11 = 22). Medido: nuca 5-10 graus ja abre a aba escura
# atras da juba (renders review/pelo_r2); a malha de cartoes nao suporta girar os ossos Pelo*. A ameaca fica nas orelhas, boca, cauda e corpo.
# 16/11 (usuario: "ao rugir, seu pelo se divide"): no pico a placa do dorso subia como uma aba e descolava da juba.
# Fatores so para o dorso e a juba lateral (padrao 1 = clipe aprovado de 12/11, reproduzivel).
ROS_DORSO = float(os.environ.get("LOBO_ROS_DORSO", "1"))
ROS_JUBA = float(os.environ.get("LOBO_ROS_JUBA", "1"))
POSE_AMEACA = P(raiz=(0, -0.12, -0.28, 5.0),
                ossos={"Pescoco1": {"X": 16}, "Pescoco2": {"X": 2}, "Cabeca": {"X": -12}, "Peito": {"X": 1},
                       "OrelhaE": {"X": 9}, "OrelhaD": {"X": 9}, "Mandibula": {"X": 7},
                       "PeloNuca1": {"X": ROS_PELO}, "PeloNuca2": {"X": ROS_PELO}, "PeloDorso1": {"X": 0.8 * ROS_PELO * ROS_DORSO}, "PeloDorso2": {"X": 0.6 * ROS_PELO * ROS_DORSO},
                       "JubaE": {"X": -0.5 * ROS_PELO * ROS_JUBA}, "JubaD": {"X": -0.5 * ROS_PELO * ROS_JUBA}   # (medido: nuca/dorso X+ erica; juba lateral X-)
                      , "JubaPeito": {"X": 4},
                       **_cauda(18, 1.0)},
                pes={"MaoE": ((0, 0, 0), -8, 0), "MaoD": ((0, 0, 0), -8, 0), "MetatarsoE": ((0, 0, 0), -6, 0), "MetatarsoD": ((0, 0, 0), -6, 0)})
def clipe_rosnado_ameaca(t):
    """3,4 s: pelos ericam e o corpo se projeta para a frente (0-0,5) -> rosna fixo, peito vibrando, boca entreaberta
    (dentes a mostra) -> ameaca mais forte (1,7-2,3: boca abre mais, avanca um fio) -> volta (2,8-3,4)"""
    p = chaves([(0.0, NEUTRO, None), (0.5, POSE_AMEACA, None), (2.8, POSE_AMEACA, None), (3.4, NEUTRO, None)])(t)
    w = _jan(t, 0.4, 2.9, 0.2)
    somar_ossos(p["ossos"], {"Mandibula": {"X": 1.0 * math.sin(2 * math.pi * 11 * t) * w}, "Peito": {"X": 0.6 * math.sin(2 * math.pi * 10 * t) * w},
                             "Cabeca": {"X": 0.4 * math.sin(2 * math.pi * 9 * t) * w}})
    forte = _jan(t, 1.7, 2.3, 0.15)
    somar_ossos(p["ossos"], {"Mandibula": {"X": 7 * forte}, "Pescoco1": {"X": 3 * forte}, "Cabeca": {"X": -3 * forte}})
    p["raiz"][1] -= 0.06 * forte
    for i, nm in enumerate(CAUDA[-3:]):                                  # ponta da cauda alta treme (rigida)
        somar_ossos(p["ossos"], {nm: {"Z": 2.5 * math.sin(2 * math.pi * 7 * t + i) * w}})
    return p
# ------------------------------------------------------------------ SAUDACAO (3,6 s, em pe, social)
POSE_SAUDA = P(raiz=(0, 0.12, -0.40, 3.0),
               ossos={"Pescoco1": {"X": 10}, "Pescoco2": {"X": -2}, "Cabeca": {"X": -16}, "Peito": {"X": 1},
                      "OrelhaE": {"X": -26, "Y": 4}, "OrelhaD": {"X": -26, "Y": -4}, "PeloNuca1": {"X": -6}, "PeloNuca2": {"X": -6},
                      **_cauda(-10, 1.0)},
               pes={"MaoE": ((0, 0, 0), -8, 0), "MaoD": ((0, 0, 0), -8, 0), "MetatarsoE": ((0, 0, 0), -12, 0), "MetatarsoD": ((0, 0, 0), -12, 0)})
def clipe_saudacao(t):
    """3,6 s: abaixa o corpo, orelhas coladas (0-0,5) -> cauda baixa abana largo com o quadril rebolando, focinho sobe
    "lambendo" o ar em direcao ao outro (1,0-1,3 e 2,0-2,3) -> volta (3,0-3,6)"""
    p = chaves([(0.0, NEUTRO, None), (0.5, POSE_SAUDA, None), (3.0, POSE_SAUDA, None), (3.6, NEUTRO, None)])(t)
    w = _jan(t, 0.3, 3.2, 0.3)
    s = math.sin(2 * math.pi * 2.4 * t)
    for i, nm in enumerate(CAUDA):
        k = (i + 1) / NC; somar_ossos(p["ossos"], {nm: {"Z": 22 * k * math.sin(2 * math.pi * 2.4 * t - 1.0 * k) * w}})
    somar_ossos(p["ossos"], {"Pelve": {"Z": -5 * s * w}, "Coluna1": {"Z": -2.5 * s * w}, "Coluna2": {"Z": 1.5 * s * w}})
    p["raiz"][5] += 1.5 * s * w
    for t0 in (1.0, 2.0):                                                # focinho sobe e "lambe" (boca entreabre)
        g = _jan(t, t0, t0 + 0.4, 0.12)
        somar_ossos(p["ossos"], {"Pescoco1": {"X": -6 * g}, "Cabeca": {"X": -6 * g}, "Mandibula": {"X": 6 * g * (0.5 + 0.5 * math.sin(2 * math.pi * 7 * t))}})
    olhos(p, 0.15 * w)
    return p
CLIPES.update({
    "UivoSentado": (clipe_uivo_sentado, UIVO_SENT_D, False, 0.0, {"Inspira": 0.6, "UivoInicio": 1.8, "UivoFim": UIVO_SENT_D - 1.4}),
    "UivoEmPe": (clipe_uivo_em_pe, UIVO_PE_D, False, 0.0, {"Inspira": 0.6, "UivoInicio": 1.8, "UivoFim": UIVO_PE_D - 1.4}),
    "LatidoAviso": (clipe_latido, 2.4, False, 0.0, {"Latido1": LATIDOS[0], "Latido2": LATIDOS[1]}),
    "Ganido": (clipe_ganido, 3.6, False, 0.0, {"Ganido1": 0.6, "Ganido2": 1.9}),
    "RosnadoAmeaca": (clipe_rosnado_ameaca, 3.4, False, 0.0, {"RosnadoInicio": 0.5, "Ameaca": 1.7, "RosnadoFim": 2.8}),
    "Saudacao": (clipe_saudacao, 3.6, False, 0.0, {"Lambe1": 1.0, "Lambe2": 2.0}),
})
CAUDA_NO_CHAO.add("UivoSentado")                                         # sentado: cauda apoiada (como o Sentado aprovado)
if os.environ.get("LOBO_SONDA4"): exec(open(os.environ["LOBO_SONDA4"], encoding="utf-8").read())   # medicao (so leitura), sai antes de gerar
