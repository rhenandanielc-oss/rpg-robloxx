# Queda LATERAL do Lobo Ancestral (20/11/2026) - o lobo derrubado tomba DE LADO (decubito lateral), flanco e barriga
# expostos, para a finalizacao no flanco. Carregado por exec() em anim_lobo.py com LOBO_QUEDA=1. Clipes NOVOS, proprios
# (Deitar/Deitado/LevantarDeitado do descanso ficam intactos). Para cada lado (E = cai sobre o lado esquerdo, D = direito):
#   QuedaLado*    1,1 s  tropeco -> perde o equilibrio (tronco rola, patas de baixo cedem) -> ombro/quadril tocam o chao
#                        -> cabeca e cauda assentam por ultimo, com um pequeno quique de peso
#   CaidoLado*    4,0 s  laco: de lado, patas relaxadas para o lado da barriga, cabeca e cauda pousadas, respiracao discreta
#   LevantarLado* 1,9 s  recolhe as patas sob o corpo, rola para o peito, apoia as 4 patas e fica de pe (sem salto de pose)
# Coerencia de canideo (so principios): na queda o tronco rola sobre o ombro/quadril do lado de baixo; deitado de lado as
# patas ficam paralelas, as de cima repousando sobre as de baixo; a cabeca toca o chao pela bochecha; para levantar o
# animal primeiro traz as patas para baixo do corpo (fica "de peito") e so depois ergue a frente e a traseira.
QL_ROLL = _ev_env("LOBO_Q_ROLL", "80")            # rolagem final do tronco (graus): ~decubito lateral
QL_BAIXO_Z = _ev_env("LOBO_Q_PE_BAIXO", "0.14")   # patas do lado de baixo, rentes ao chao
QL_CIMA_Z = _ev_env("LOBO_Q_PE_CIMA", "0.62")     # patas de cima repousando sobre as de baixo
QL_RECOLHE = _ev_env("LOBO_Q_RECOLHE", "0.78")    # perna relaxada: o pe fica 14% mais perto do ombro/quadril que esticada
QL_ABRE_Y = _ev_env("LOBO_Q_ABRE_Y", "0.80")      # r4 (pedido 20/11 "separe mais as patas"): maos para a frente, pes para tras
QL_TESOURA = _ev_env("LOBO_Q_TESOURA", "0.60")    # r4: o par de cima vai ainda mais longe (frente/tras) que o de baixo
QL_TRAS = _ev_env("LOBO_Q_TRAS", "0.55")          # r4c: as traseiras abrem menos (o jarrete limita; com 1,0 o IK errava 0,15)
QL_CIMA_Z_ABERTO = _ev_env("LOBO_Q_PE_CIMA_AB", "0.42")  # r4: separado, a pata de cima desce um pouco (nao fica empilhada)
JUNTA = {"MaoE": "EscapulaE", "MaoD": "EscapulaD", "MetatarsoE": "CoxaE", "MetatarsoD": "CoxaD"}
def _lado_de_baixo(sinal):
    q = P(raiz=(0, 0, -2.5, 0, sinal * 60.0, 0)); aplicar(q)
    return "E" if PB["EscapulaE"].head.z < PB["EscapulaD"].head.z else "D"
def _pes_laterais(r, baixo, recolhe=QL_RECOLHE, zb=QL_BAIXO_Z, zc=QL_CIMA_Z):
    """pernas acompanham o tronco rolado (relaxadas, um pouco dobradas) e deitam: as de baixo rentes ao chao, as de cima
    sobre elas"""
    M = pose_raiz(r); pes = {}
    for k in PES:
        j = M @ BD[JUNTA[k]].head_local; a = M @ B0[k]
        h = j + (a - j) * recolhe
        cima = k[-1] != baixo
        z = zb if not cima else (QL_CIMA_Z_ABERTO if zc == QL_CIMA_Z else zc)
        dy = (QL_ABRE_Y + (QL_TESOURA if cima else 0.0)) * (-1.0 if k.startswith("Mao") else QL_TRAS)   # o lobo olha para -Y
        alc = (h - j).length; t = V((h.x, h.y + dy, z))
        if (t - j).length > alc:                                         # r4b: abre girando a perna (mesmo alcance), sem esticar
            dyz = (t.y - j.y) ** 2 + (t.z - j.z) ** 2
            t.x = j.x + math.copysign(math.sqrt(max(0.0, alc * alc - dyz)), h.x - j.x)
        pes[k] = (t - B0[k], PLANO[k] * 0.4, 4)
    return pes
V_OMBRO_QUADRIL = _idx(("EscapulaE", "EscapulaD", "BracoE", "BracoD", "CoxaE", "CoxaD"))
def _assentar_lateral(q, baixo, nome=""):
    """desce/sobe a raiz ate o tronco encostar no chao: nucleo a 0,03 e ombro/braco/coxa do lado de baixo no maximo
    0,10 abaixo (pelo comprimido) - r1 so olhava o nucleo e o ombro de baixo afundava 0,42"""
    for _ in range(8):
        q["pes"] = {k: (B0[k] + V(d), i, de) for k, (d, i, de) in _pes_laterais(q["raiz"], baixo).items()}
        aplicar(q); ev = _ev()
        falta = max(0.03 - min(ev[i].co.z for i in V_NUCLEO), -0.10 - min(ev[i].co.z for i in V_OMBRO_QUADRIL))
        q["raiz"][2] += falta
        if abs(falta) < 0.01: break
    q["pes"] = {k: (B0[k] + V(d), i, de) for k, (d, i, de) in _pes_laterais(q["raiz"], baixo).items()}
    aplicar(q); ev = _ev(); print("ASSENTAR_LATERAL", nome, "dz %.2f nucleo z %.3f" % (q["raiz"][2], min(ev[i].co.z for i in V_NUCLEO)))
    return q
def _pousar(q, ossos_fn, faixa, alvo, grupo_v, nome):
    """procura o angulo (graus) que leva a parte (cabeca ou cauda) a encostar no chao a 'alvo', sem afundar"""
    melhor = None
    for a_ in faixa:
        qq = {"raiz": list(q["raiz"]), "ossos": {k: dict(v) for k, v in q["ossos"].items()}, "pes": dict(q["pes"])}
        somar_ossos(qq["ossos"], ossos_fn(a_)); aplicar(qq); ev = _ev(); z = min(ev[i].co.z for i in grupo_v)
        custo = abs(z - alvo) + (3.0 * (alvo - z) if z < alvo else 0.0)
        if melhor is None or custo < melhor[0]: melhor = (custo, a_, qq, z)
    print("POUSAR", nome, "angulo %d z %.3f" % (melhor[1], melhor[3])); return melhor[2], melhor[1]
def _cauda_lateral(p, nome="", ini=None, quieto=False):
    """r3: cauda pesada com o tronco rolado. Com 80 graus de rolagem o eixo X (sobe/desce em pe) vira lateral e o Z vira
    vertical, por isso a busca e osso a osso nos DOIS eixos: cada ponta desce ate ~0,5 (raio do pelo) e segue rente ao
    chao para tras; depois o pelo de cada osso sobe ate nao afundar mais que 0,05."""
    q = {"raiz": list(p["raiz"]), "ossos": {k: dict(v) for k, v in p["ossos"].items()}, "pes": dict(p["pes"])}
    for nm in CAUDA: q["ossos"][nm] = dict(ini[nm]) if ini else {"X": 0.0, "Z": 0.0}
    extras = [0.0] * NC
    for passada in range(4):
        ant = (0.0, 0.0)
        for i, nm in enumerate(CAUDA):
            def custo(ax, az):
                q["ossos"][nm]["X"] = ax; q["ossos"][nm]["Z"] = az; aplicar(q); h, t = PB[nm].head, PB[nm].tail; L = (t - h).length
                alvo = max(0.5, h.z - 0.95 * L) + extras[i]
                frente = max(0.0, (h.y - t.y) + 0.2 * L)                    # o lobo olha para -Y: a cauda nao vem para a frente
                return (t.z - alvo) ** 2 + 0.6 * frente ** 2 + 0.003 * (((ax - ant[0]) ** 2 + (az - ant[1]) ** 2) / 100.0)
            b0 = (q["ossos"][nm]["X"], q["ossos"][nm]["Z"]); passo0 = 12 if (passada == 0 and not ini) else 4
            R_ = 5 if not ini else 3                                       # com ini (quadro anterior): busca curta = cauda continua
            melhor = min(((b0[0] + a * passo0, b0[1] + b * passo0) for a in range(-R_, R_ + 1) for b in range(-R_, R_ + 1)), key=lambda c: custo(*c))
            for passo in (4, 2, 1):
                melhor = min(((melhor[0] + a * passo, melhor[1] + b * passo) for a in (-1, 0, 1) for b in (-1, 0, 1)), key=lambda c: custo(*c))
            q["ossos"][nm]["X"], q["ossos"][nm]["Z"] = float(melhor[0]), float(melhor[1]); ant = melhor
        aplicar(q); ev = _ev()
        fundo = [min([ev[v].co.z for v, d in DONO_CAUDA.items() if d == i] or [1.0]) for i in range(NC)]
        if min(fundo) > -0.05: break
        for i in range(NC): extras[i] += max(0.0, -0.02 - fundo[i])
    if not quieto: print("CAUDA_LATERAL", nome, " ".join("%.0f/%.0f" % (q["ossos"][nm]["X"], q["ossos"][nm]["Z"]) for nm in CAUDA),
          "| pelo min", " ".join("%.2f" % f for f in fundo))
    return q
def tombado_pose(sinal):
    baixo = _lado_de_baixo(sinal)
    q = P(raiz=(0, 0.0, -3.0, 0.0, sinal * QL_ROLL, 0.0),
          ossos={"OrelhaE": {"X": -10}, "OrelhaD": {"X": -10}, "Mandibula": {"X": 4}})
    q = _assentar_lateral(q, baixo, "tombado_" + baixo)
    # cabeca: o pescoco dobra para o lado de baixo ate a bochecha encostar no chao (busca o sinal e o angulo)
    q, _ = _pousar(q, lambda a: {"Pescoco1": {"Z": 0.45 * a, "X": 4}, "Pescoco2": {"Z": 0.35 * a}, "Cabeca": {"Z": 0.25 * a, "Y": 0.2 * a}},
                   range(-70, 71, 5), 0.04, V_CABECA, "cabeca_" + baixo)
    q = _cauda_lateral(q, "tombado_" + baixo)
    for l_ in PALP_FECHA: q["ossos"]["Palpebra" + l_] = {"F": 0.55}      # olhos semicerrados (atordoado)
    aplicar(q); ev = _ev()
    print("TOMBADO", baixo, "raiz", [round(x, 2) for x in q["raiz"]], "nucleo z %.3f cabeca z %.3f" % (min(ev[i].co.z for i in V_NUCLEO), min(ev[i].co.z for i in V_CABECA)),
          " ".join("%s:(%.2f,%.2f,%.2f)" % (k, *PB[k].tail) for k in PES))
    return q, baixo
def _mistura(a, b, u, zmin_pe=0.10, recolher=None):
    """pose intermediaria (para as chaves de transicao): mistura raiz/ossos/patas; patas nunca abaixo de zmin_pe;
    recolher = {pe: fracao} puxa a pata para baixo do corpo (perde o apoio / prepara para levantar)"""
    p = {"raiz": [lerp(x, y, u) for x, y in zip(a["raiz"], b["raiz"])], "ossos": {}, "pes": {}}
    for nm in set(a["ossos"]) | set(b["ossos"]):
        ea, eb = a["ossos"].get(nm, {}), b["ossos"].get(nm, {})
        p["ossos"][nm] = {e: lerp(ea.get(e, 0.0), eb.get(e, 0.0), u) for e in set(ea) | set(eb)}
    M = pose_raiz(p["raiz"])
    for k in PES:
        (ba, ia, da), (bb, ib, db) = a["pes"][k], b["pes"][k]
        bola = ba.lerp(bb, u)
        if recolher and k in recolher:
            sob = M @ (BD[JUNTA[k]].head_local + (B0[k] - BD[JUNTA[k]].head_local) * 0.55)
            bola = bola.lerp(V((sob.x, sob.y, bola.z)), recolher[k])
        bola = V((bola.x, bola.y, max(zmin_pe, bola.z)))
        p["pes"][k] = (bola, lerp(ia, ib, u), lerp(da, db, u))
    return p
def _queda(sinal, TOMB, baixo):
    """tropeco (0,18) -> meio da queda (0,52, tronco a ~45 graus, patas de baixo cedem sob o corpo) -> contato (0,78)
    -> assenta com quique (0,90) -> final (1,1, cabeca e cauda pousadas por ultimo)"""
    lado_x = 1.0 if baixo == "E" else -1.0                              # o corpo escorrega um pouco para o lado da queda
    trop = P(raiz=(0.25 * lado_x, 0.10, -0.18, -4.0, sinal * 10.0, 0.0),
             ossos={"Pescoco1": {"X": -10, "Z": -8 * sinal}, "Cabeca": {"X": -6}, "OrelhaE": {"X": -28}, "OrelhaD": {"X": -28}, "Mandibula": {"X": 10}},
             pes={k: ((0.15 * lado_x if k[-1] == baixo else -0.12 * lado_x, -0.12 if k.startswith("Mao") else 0.12, 0.0), -10, 0) for k in PES})
    baixos = {k: 0.50 for k in PES if k[-1] == baixo}                   # r4: 0,85 -> 0,50 (patas mais separadas na queda)
    meio = _mistura(trop, TOMB, 0.45, 0.10, baixos)
    somar_ossos(meio["ossos"], {"Pescoco1": {"X": -12}, "Cabeca": {"X": -8}})        # a cabeca ainda resiste (mais alta)
    cont = _mistura(trop, TOMB, 0.86, 0.10)
    cont["raiz"][2] += 0.12
    cab_alta = {"Pescoco1": {"X": -8}, "Pescoco2": {"X": -4}}
    somar_ossos(cont["ossos"], cab_alta)                                # cabeca e cauda tocam DEPOIS do tronco
    meio = _cauda_lateral(meio, "meio_" + baixo); cont = _cauda_lateral(cont, "cont_" + baixo)       # r3
    quique = _mistura(TOMB, TOMB, 0.0); quique["raiz"][2] += 0.05; somar_ossos(quique["ossos"], {"Pescoco1": {"X": -3}})
    return chaves([(0.0, NEUTRO, None), (0.18, trop, None), (0.52, meio, {k: 0.35 for k in PES if k[-1] != baixo}),
                   (0.78, cont, None), (0.90, quique, None), (1.10, TOMB, None)])
def _levantar(sinal, TOMB, baixo):
    """recolhe as patas sob o corpo e rola para o peito (0,55-1,0) -> apoia as 4 (1,0) -> agachado (1,45) -> de pe (1,9)"""
    AP = apoios_pose(); AG = agachado_pose()
    junta = _mistura(TOMB, TOMB, 0.0, 0.10, {k: 0.7 for k in PES})        # patas vem para baixo do corpo, ainda de lado
    rola = _mistura(TOMB, AP, 0.55, 0.10, {k: 0.5 for k in PES})          # rola para o peito, cabeca ergue
    somar_ossos(rola["ossos"], {"Pescoco1": {"X": -10}, "Cabeca": {"X": -6}})
    junta = _cauda_lateral(junta, "junta_" + baixo)                        # r3: cauda sem enterrar
    for nm in CAUDA: rola["ossos"][nm] = {"X": -8.0, "Z": 0.0}             # r3: ao rolar a cauda sai reta para tras (pelve ja alta)
    return chaves([(0.0, TOMB, None), (0.45, junta, None), (0.95, rola, None), (1.25, AP, {k: 0.18 for k in PES}),
                   (1.55, AG, {"MaoE": 0.25, "MaoD": 0.25}), (1.9, NEUTRO, None)])
def _sem_afundar(fn, dur, nome, peso=((0.0, 1.0), (99.0, 1.0)), sobe_de=None):
    """r3: entre as chaves a rolagem e a altura interpolam em linha e o quadril/ombro de baixo entrava 0,9 no chao
    (LevantarLado ~1,1 s). Mede a cada 1/15 s quanto o tronco (nucleo >= 0,03; ombro/coxa >= -0,10) precisa subir,
    suaviza e soma na raiz; tambem registra a cabeca (diagnostico)."""
    ts = [i / 15.0 for i in range(int(dur * 15) + 1)]; sobe = []; cab = []
    for t in ts:
        p = fn(t); aplicar(p); ev = _ev()
        sobe.append(max(0.0, 0.03 - min(ev[i].co.z for i in V_NUCLEO), -0.10 - min(ev[i].co.z for i in V_OMBRO_QUADRIL)))
        cab.append(min(ev[i].co.z for i in V_CABECA))
    mx = [max(sobe[max(0, i - 2):i + 3]) for i in range(len(sobe))]
    sm = [sum(mx[max(0, i - 2):i + 3]) / len(mx[max(0, i - 2):i + 3]) for i in range(len(mx))]
    if sobe_de is not None:                                                # r3: levantar sem "quique" - depois que o tronco
        alt = [fn(t)["raiz"][2] + sm[i] for i, t in enumerate(ts)]         # rola, a altura da raiz so sobe (antes subia 0,8 em
        for i in range(1, len(ts)):                                        # 1,1 s e descia de novo para o peito em 1,25 s)
            if ts[i] >= sobe_de and alt[i] < alt[i - 1]: sm[i] += alt[i - 1] - alt[i]; alt[i] = alt[i - 1]
    print("SEM_AFUNDAR", nome, "sobe max %.3f" % max(sm), "| cabeca min %.3f em t %.2f" % (min(cab), ts[cab.index(min(cab))]))
    def corpo(t):
        p = fn(t); u = min(len(sm) - 1.001, max(0.0, t * 15.0)); i = int(u)
        p["raiz"][2] += lerp(sm[i], sm[min(i + 1, len(sm) - 1)], u - i); return p
    # r3: trilha propria da cauda - resolvida a cada 1/7,5 s sobre o corpo ja erguido, partindo do quadro anterior
    # (interpolar angulos de chaves muito diferentes enterrava a cauda 0,6-0,95 entre elas)
    tc = [i / 7.5 for i in range(int(dur * 7.5) + 1)]
    if tc[-1] < dur: tc.append(dur)
    trilha = []; ini = None
    for t in tc:
        qq = _cauda_lateral(corpo(t), nome, ini, quieto=True); ini = {nm: dict(qq["ossos"][nm]) for nm in CAUDA}; trilha.append(ini)
    def g(t):
        p = corpo(t); k = 0
        while k < len(tc) - 2 and tc[k + 1] < t: k += 1
        w = min(1.0, max(0.0, (t - tc[k]) / (tc[k + 1] - tc[k]))); w = suave(w)
        j = 0                                                              # peso da trilha: 0 nas pontas que emendam com outro
        while j < len(peso) - 2 and peso[j + 1][0] < t: j += 1             # clipe (Caido/em pe), para nao saltar de pose
        pw = suave(min(1.0, max(0.0, (t - peso[j][0]) / max(1e-6, peso[j + 1][0] - peso[j][0]))))
        pw = lerp(peso[j][1], peso[j + 1][1], pw)
        for nm in CAUDA:
            ch = p["ossos"].get(nm, {})
            p["ossos"][nm] = {e: lerp(ch.get(e, 0.0), lerp(trilha[k][nm].get(e, 0.0), trilha[k + 1][nm].get(e, 0.0), w), pw) for e in ("X", "Z")}
        return p
    print("TRILHA_CAUDA", nome, len(tc), "amostras")
    return g
QUEDA_LATERAL = {}
for _s in (1.0, -1.0):
    _T, _b = tombado_pose(_s)
    QUEDA_LATERAL[_b] = _T
    CLIPES["QuedaLado" + _b] = (_sem_afundar(_queda(_s, _T, _b), 1.1, "QuedaLado" + _b, ((0.0, 0.0), (0.2, 1.0), (0.92, 1.0), (1.1, 0.0))), 1.1, False, 0.0, {"Desequilibrio": 0.18, "Contato": 0.78, "Caido": 1.1})
    CLIPES["CaidoLado" + _b] = (respira(_T, 0.8, 4.0, True), 4.0, True, 0.0, {})
    CLIPES["LevantarLado" + _b] = (_sem_afundar(_levantar(_s, _T, _b), 1.9, "LevantarLado" + _b, ((0.0, 0.0), (0.18, 1.0), (0.6, 1.0), (0.95, 0.0)), sobe_de=0.6), 1.9, False, 0.0, {"PatasSob": 0.45, "DePeito": 1.25, "EmPe": 1.9})
    CAUDA_NO_CHAO.add("CaidoLado" + _b)
TRANSICAO_EXTRA = set()
for _b in ("E", "D"):
    for _n in ("QuedaLado", "LevantarLado"): CAUDA_NO_CHAO.add(_n + _b); TRANSICAO_EXTRA.add(_n + _b)   # r3: pelo da cauda corrigido por quadro
