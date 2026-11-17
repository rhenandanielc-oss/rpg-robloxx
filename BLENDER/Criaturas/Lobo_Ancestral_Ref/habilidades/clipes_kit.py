# Kit do Lobo Ancestral (10/11/2026): clipes das 3 ATIVAS (so movimento). v28: Investida sobre a Corrida v28 (versao anterior em clipes_kit_v27.py). Pedido do usuario em
# DOCS/pedidos/2026-11-10-lobo-ancestral-habilidades-passivas.md (elemento Natureza; Salto Predatorio, Uivo Ancestral, Investida).
# Carregado por exec() dentro de anim_lobo.py quando LOBO_KIT=1 (os 24 clipes aprovados e a execucao padrao nao mudam).
# Todos NO LUGAR (como os demais clipes): o jogo move o modelo (arco do salto, avanco da investida) pelo servidor/fisica.
# Marcadores sincronizam som, contato (dano) e VFX no Studio.
def _mistura(a, b, s):
    """interpolacao de duas poses (mesma regra de chaves())"""
    s = max(0.0, min(1.0, s))
    p = {"raiz": [lerp(x, y, s) for x, y in zip(a["raiz"], b["raiz"])], "ossos": {}, "pes": {}}
    for nm in set(a["ossos"]) | set(b["ossos"]):
        ea, eb = a["ossos"].get(nm, {}), b["ossos"].get(nm, {})
        p["ossos"][nm] = {e: lerp(ea.get(e, 0.0), eb.get(e, 0.0), s) for e in set(ea) | set(eb)}
    for k in PES:
        (ba, ia, da), (bb, ib, db) = a["pes"][k], b["pes"][k]
        p["pes"][k] = (ba.lerp(bb, s), lerp(ia, ib, s), lerp(da, db, s))
    return p
# ------------------------------------------------------------------ SALTO PREDATORIO (1,35 s)
# agacha mirando o alvo (cabeca baixa, orelhas para tras) -> impulso -> no ar com as dianteiras estendidas para a frente e a
# boca aberta -> aterrissa sobre o alvo fechando a mandibula (Golpe = Aterrissagem) -> amortece -> repouso.
def clipe_salto_predatorio(t):
    mira = P(raiz=(0, 0.25, -0.45, 4.0), ossos={"Pescoco1": {"X": 10}, "Pescoco2": {"X": 4}, "Cabeca": {"X": -10}, "Mandibula": {"X": 4},
                                               "OrelhaE": {"X": -30}, "OrelhaD": {"X": -30}, **{nm: {"X": -6} for nm in CAUDA}},
             pes={"MaoE": ((0, -0.05, 0), -14, 0), "MaoD": ((0, -0.05, 0), -14, 0), "MetatarsoE": ((0, 0.05, 0), -24, 0), "MetatarsoD": ((0, 0.05, 0), -24, 0)})
    imp = P(raiz=(0, 0.0, 0.30, -12.0), ossos={"Pescoco1": {"X": -6}, "Cabeca": {"X": -6}, "Mandibula": {"X": 10}, "OrelhaE": {"X": -30}, "OrelhaD": {"X": -30}},
            pes={"MaoE": ((0, -0.3, 0.55), 30, 20), "MaoD": ((0, -0.3, 0.55), 30, 20), "MetatarsoE": ((0, 0.15, 0.25), 30, 10), "MetatarsoD": ((0, 0.15, 0.25), 30, 10)})
    ar_r = (0, -0.4, 1.4, -4.0); M_ar = pose_raiz(list(ar_r) + [0, 0])
    ar = P(raiz=ar_r, ossos={"Pescoco1": {"X": 4}, "Pescoco2": {"X": 2}, "Cabeca": {"X": 2}, "Mandibula": {"X": 26}, "OrelhaE": {"X": -34}, "OrelhaD": {"X": -34},
                             "Escapula" + "E": {"X": -14}, "EscapulaD": {"X": -14}, **{nm: {"X": 4} for nm in CAUDA}})
    for k, ext, inc in (("MaoE", V((0.12, -1.9, 0.95)), 20), ("MaoD", V((-0.12, -1.9, 0.95)), 20),
                        ("MetatarsoE", V((0, 1.25, 0.6)), 95), ("MetatarsoD", V((0, 1.25, 0.6)), 95)):
        ar["pes"][k] = (mundo_pe(M_ar, k, ext), inc, 30)
    golpe = P(raiz=(0, -0.55, -0.20, 9.0), ossos={"Pescoco1": {"X": 14}, "Pescoco2": {"X": 6}, "Cabeca": {"X": 6}, "Mandibula": {"X": 0},
                                                 "OrelhaE": {"X": -30}, "OrelhaD": {"X": -30}},
              pes={"MaoE": ((0.08, -0.8, 0), -10, 0), "MaoD": ((-0.08, -0.8, 0), -10, 0), "MetatarsoE": ((0, -0.3, 0.45), 30, 10), "MetatarsoD": ((0, -0.3, 0.45), 30, 10)})
    amort = P(raiz=(0, -0.55, -0.50, 3.0), ossos={"Pescoco1": {"X": 10}, "Cabeca": {"X": 4}, "OrelhaE": {"X": -20}, "OrelhaD": {"X": -20}},
              pes={"MaoE": ((0.08, -0.8, 0), -12, 0), "MaoD": ((-0.08, -0.8, 0), -12, 0), "MetatarsoE": ((0, -0.55, 0), -20, 0), "MetatarsoD": ((0, -0.55, 0), -20, 0)})
    fim = P(raiz=(0, -0.55, 0, 0), pes={k: ((0, -0.55, 0), 0, 0) for k in PES})
    return chaves([(0.0, NEUTRO, None), (0.30, mira, None), (0.42, imp, None), (0.64, ar, None), (0.80, ar, None),
                   (0.86, golpe, None), (1.02, amort, None), (1.35, fim, None)])(t)
# ------------------------------------------------------------------ UIVO ANCESTRAL (2,6 s)
# mais curto que o Uivo de vida (4 s): firma as patas, estufa o peito, ergue a cabeca, uiva (BuffInicio no inicio do som);
# no fim sacode de leve a juba e volta ao repouso com a cauda alta (pronto para correr).
def clipe_uivo_ancestral(t):
    cab = {"Pescoco1": {"X": -24}, "Pescoco2": {"X": -18}, "Cabeca": {"X": -16}, "Peito": {"X": -2},
           "OrelhaE": {"X": -12, "Y": 6}, "OrelhaD": {"X": -12, "Y": -6}, "JubaPeito": {"X": -8}, "JubaE": {"X": 4}, "JubaD": {"X": 4},
           **{nm: {"X": 6} for nm in CAUDA}}
    firme = {k: ((0, 0.12 if k.startswith("Mao") else 0.0, 0), -4, 0) for k in PES}
    prep = P(raiz=(0, 0.06, 0.02, -2.0), ossos=dict(cab), pes=firme)
    abre = P(raiz=(0, 0.06, 0.04, -3.0), ossos={**cab, **boca_aberta(22)}, pes=firme)
    sus = P(raiz=(0, 0.06, 0.05, -3.5), ossos={**{k: {e: g * 1.08 for e, g in v.items()} for k, v in cab.items()}, **boca_aberta(25)}, pes=firme)
    fecha = P(raiz=(0, 0.04, 0.02, -1.5), ossos={**cab, **boca_aberta(2)}, pes=firme)
    pronto = P(raiz=(0, 0.0, -0.05, 2.0), ossos={"Pescoco1": {"X": 4}, "OrelhaE": {"X": -6}, "OrelhaD": {"X": -6}, **{nm: {"X": 10} for nm in CAUDA}})
    p = chaves([(0.0, NEUTRO, None), (0.35, prep, None), (0.55, abre, None), (1.85, sus, None), (2.1, fecha, None), (2.6, pronto, None)])(t)
    if 0.55 < t < 1.85: somar_ossos(p["ossos"], {"Mandibula": {"X": 1.5 * math.sin(2 * math.pi * t * 1.6)}, "Cabeca": {"X": -0.8 * math.sin(2 * math.pi * t * 0.9)}})
    if 2.0 < t < 2.5:                                                  # sacode a juba
        a = math.sin(math.pi * (t - 2.0) / 0.5) * math.sin(2 * math.pi * (t - 2.0) * 6)
        somar_ossos(p["ossos"], {"Pescoco2": {"Z": 6 * a}, "Cabeca": {"Z": 8 * a}, "JubaE": {"Z": 6 * a}, "JubaD": {"Z": 6 * a}})
    return p
# ------------------------------------------------------------------ INVESTIDA (1,2 s)
# carga curta (abaixa, orelhas para tras) -> arranque em galope baixo e rapido (passada do Corrida aprovado, mais baixa e com a
# cabeca estendida) -> boca abre e fecha no primeiro alvo (Contato) -> freia e recupera.
_GAL = marcha(**GALOPE)
VEL_INV = vel(GALOPE)                                                  # 21,4 studs/s (mesma velocidade do galope aprovado)
def vel_investida(t):
    """v28: curva de velocidade do AVANCO que o jogo aplica ao modelo (o clipe fica no lugar): parado na carga, rampa no
    Arranque (0,22-0,36), galope ate 0,78, desacelera ate o Freia (0,96), parado depois. As patas apoiadas recuam nessa
    velocidade (planta no chao) - antes (v27) as misturas arrastavam as patas apoiadas (deslize ate 34 studs/s)."""
    if t < 0.22: return 0.0
    if t < 0.36: return VEL_INV * suave((t - 0.22) / 0.14)
    if t < 0.78: return VEL_INV
    if t < 0.96: return VEL_INV * (1 - suave((t - 0.78) / 0.18))
    return 0.0
def _investida_base(t):
    carga = P(raiz=(0, 0.30, -0.40, 6.0), ossos={"Pescoco1": {"X": 12}, "Pescoco2": {"X": 6}, "Cabeca": {"X": -8}, "OrelhaE": {"X": -34}, "OrelhaD": {"X": -34},
                                                **{nm: {"X": -4} for nm in CAUDA}},
              pes={"MaoE": ((0, 0, 0), -14, 0), "MaoD": ((0, 0, 0), -14, 0), "MetatarsoE": ((0, 0, 0), -26, 0), "MetatarsoD": ((0, 0, 0), -26, 0)})   # v28: so o corpo abaixa
    morde = P(raiz=(0, -0.35, -0.35, 10.0), ossos={"Pescoco1": {"X": 18}, "Pescoco2": {"X": 10}, "Cabeca": {"X": 8}, "Mandibula": {"X": 0},
                                                  "OrelhaE": {"X": -26}, "OrelhaD": {"X": -26}},
              pes={"MaoE": ((0, -0.55, 0), -14, 0), "MaoD": ((0, -0.45, 0), -14, 0), "MetatarsoE": ((0, -0.1, 0), 16, 0), "MetatarsoD": ((0, -0.1, 0), 16, 0)})
    fim = P(raiz=(0, 0, 0, 0))
    if t <= 0.22: return chaves([(0.0, NEUTRO, None), (0.22, carga, None)])(t)
    g = _GAL(t - 0.22); g["raiz"][2] -= 0.10                            # galope um pouco mais baixo
    somar_ossos(g["ossos"], {"Pescoco1": {"X": 8}, "Cabeca": {"X": -6}, "OrelhaE": {"X": -16}, "OrelhaD": {"X": -16},
                             "Mandibula": {"X": 26 * suave((t - 0.62) / 0.16)}, "Pescoco2": {"X": 6 * suave((t - 0.62) / 0.16)}})
    if t < 0.36: return _mistura(carga, g, suave((t - 0.22) / 0.14))
    if t < 0.78: return g
    if t < 0.86: return _mistura(g, morde, suave((t - 0.78) / 0.08))
    return chaves([(0.86, morde, None), (0.96, morde, None), (1.2, fim, None)])(t)
PASSO_LIM = 0.75                                                        # v28: recuo maximo da pata plantada antes de um passo
PASSOS_FIM = {"MaoE": 0.96, "MetatarsoD": 1.0, "MaoD": 1.04, "MetatarsoE": 1.08}   # v28: na freada cada pata da um passo de volta ao repouso
def _tabela_investida():
    """integra as patas quadro a quadro (30 fps): apoiada = plantada (recua a vel_investida); no balanco segue a pose e o erro
    acumulado no apoio some ate o proximo pouso; na freada, passos alternados (levanta 0,25) ate o repouso."""
    dt = 1.0 / FPS; n = int(round(1.2 * FPS)) + 1; tab = []; est = {}
    for i in range(n):
        t = i * dt; p = _investida_base(t); novo = {}
        for k in PES:
            bola, incl, dedo = p["pes"][k]; chao = (bola.z - B0[k].z) < 0.03
            e = est.get(k)
            if t >= 0.96:
                s0 = PASSOS_FIM[k]; ini = e["ini"] if e and "ini" in e else (e["pos"] if e else bola.copy())
                u = max(0.0, min(1.0, (t - s0) / 0.12)); pos = ini.lerp(B0[k], suave(u)); pos.z = B0[k].z + 0.25 * math.sin(math.pi * u)
                novo[k] = {"pos": pos, "ini": ini, "apoio": u in (0.0, 1.0)}
                p["pes"][k] = (pos, incl * (1 - u) if u < 1 else 0.0, dedo); continue
            if e is not None and e.get("passo"):                             # passo curto em andamento (freando)
                t0p, de = e["passo"]; u = (t - t0p) / 0.12
                if u < 1.0:
                    pos = de.lerp(bola, suave(u)); pos.z = bola.z + 0.25 * math.sin(math.pi * u)
                    novo[k] = {"pos": pos, "err": V((0, 0, 0)), "apoio": False, "passo": (t0p, de)}; p["pes"][k] = (pos, incl, dedo); continue
                e = {"pos": bola.copy(), "err": V((0, 0, 0)), "apoio": True}
            if e is None: pos = bola.copy(); err = V((0, 0, 0)); ap = chao
            elif chao and e["apoio"]:
                pos = e["pos"] + V((bola.x - e["pos"].x, 0.5 * (vel_investida(t) + vel_investida(t - dt)) * dt, 0)); pos.z = bola.z; err = pos - bola; ap = True
                if abs(pos.y - bola.y) > PASSO_LIM:                          # recuou demais (alem do alcance): da um passo curto
                    novo[k] = {"pos": pos, "err": V((0, 0, 0)), "apoio": False, "passo": (t, pos.copy())}; p["pes"][k] = (pos, incl, dedo); continue
            elif chao:                                                       # pouso: comeca plantada onde a pata chegou
                pos = e["pos"].copy(); pos.z = bola.z; err = pos - bola; ap = True
            else:                                                            # balanco: o erro do apoio some ao longo do voo
                err = e["err"] * 0.82; pos = bola + err; ap = False
            novo[k] = {"pos": pos, "err": err, "apoio": ap}
            p["pes"][k] = (pos, incl, dedo)
        est = novo; p["eixo_perna"] = True                                # v28: a regra da marcha vale em todas as fases
        tab.append(p)
    return tab
_TAB_INV = []
def clipe_investida(t):
    global _TAB_INV
    if not _TAB_INV: _TAB_INV = _tabela_investida()
    i = max(0, min(len(_TAB_INV) - 1, int(round(t * FPS))))
    q = _TAB_INV[i]
    return {"raiz": list(q["raiz"]), "ossos": {k: dict(v) for k, v in q["ossos"].items()}, "pes": dict(q["pes"]), "eixo_perna": True}
CLIPES.update({
    "Hab_SaltoPredatorio": (clipe_salto_predatorio, 1.35, False, 0.0,
                            {"Mira": 0.30, "Impulso": 0.36, "Decolagem": 0.42, "Golpe": 0.86, "Aterrissagem": 0.86, "Recuperado": 1.35}),
    "Hab_UivoAncestral": (clipe_uivo_ancestral, 2.6, False, 0.0, {"UivoInicio": 0.55, "BuffInicio": 0.6, "UivoFim": 1.85, "Fim": 2.6}),
    "Hab_Investida": (clipe_investida, 1.2, False, 0.0, {"Carga": 0.0, "Arranque": 0.22, "Contato": 0.86, "Freia": 0.96, "Fim": 1.2}),
})
