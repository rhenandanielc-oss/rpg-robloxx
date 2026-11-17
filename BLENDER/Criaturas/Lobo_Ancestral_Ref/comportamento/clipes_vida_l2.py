# Comportamentos de vida - LOTE 2 (11/11/2026): conforto e higiene. Lote 1 aprovado pelo usuario ("Aprovado, siga").
# Carregado por exec() dentro de anim_lobo.py com LOBO_VIDA=2 (depois do lote 1; os clipes aprovados nao mudam).
# Sobre as poses aprovadas: SENT (sentado), DEIT/DEIT_B (deitado em esfinge), respira(). Principios de lobos reais:
# coca sentado, com a pata traseira levantada ate o pescoco/orelha em batidas rapidas (~7/s), cabeca inclinada para a pata e
# olhos semicerrados; lambe a pata dianteira deitado, cabeca virada para ela, lambidas ritmadas; cava com as dianteiras
# alternadas (puxa a terra para tras, sob o peito), cabeca baixa olhando o buraco; dorme ENROLADO com o corpo em arco, o focinho
# perto da garupa e a cauda cobrindo o focinho.
def _cp(p): return {"raiz": list(p["raiz"]), "ossos": {k: dict(v) for k, v in p["ossos"].items()}, "pes": dict(p["pes"])}
# COCAR: RETIRADO 11/11 a pedido do usuario ("retire a animacao de cocar"); nunca foi commitado - a versao r2 esta descrita na ficha (secao 6al).
# ------------------------------------------------------------------ LAMBER A PATA (5,0 s, deitado em esfinge)
# 11/11 r3 (usuario: "nao deixe a cabeca entrar dentro da perna"): o focinho afundava no antebraco E (1003 vertices a < 0,45
# do osso) -> pata 0,35 para fora; r4 ("encoste a cabeca"): queixo a 0,55 ENCOSTA na pata (62 vertices a < 0,45, 0 a < 0,30).
def _pose_lambe():
    q = _cp(DEIT); b, i_, d_ = q["pes"]["MaoE"]
    q["pes"]["MaoE"] = (b + V((float(os.environ.get("LOBO_LAMBE_PX", "0.35")), float(os.environ.get("LOBO_LAMBE_PY", "0.10")), 0.12)), i_ + 10, d_)
    somar_ossos(q["ossos"], {"Pescoco2": {"Z": 14}, "Cabeca": {"Z": 10, "Y": 8}, "OrelhaE": {"X": -4}, "OrelhaD": {"X": -4}})
    return cara_no_chao(q, alvo=float(os.environ.get("LOBO_LAMBE_Z", "0.55")), nome="lamber")
POSE_LAMBE = _pose_lambe()
def clipe_lamber_pata(t):
    """5,0 s: deitado -> baixa a cabeca sobre a pata dianteira E (0-0,8) -> lambidas (~3/s, cabeca sobe e desce ao longo da
    pata) com uma pausa -> volta (4,3-5,0)"""
    p = chaves([(0.0, DEIT, None), (0.8, POSE_LAMBE, None), (4.3, POSE_LAMBE, None), (5.0, DEIT, None)])(t)
    if 0.8 < t < 4.3 and not (2.5 < t < 2.9):
        w = math.sin(2 * math.pi * 3.0 * t); s = math.sin(2 * math.pi * 1.0 * t)
        somar_ossos(p["ossos"], {"Mandibula": {"X": 6 + 6 * w}, "Cabeca": {"X": -3 * max(0.0, w)}, "Pescoco1": {"X": 2.5 * s}})
    olhos(p, curva_olhos(t, [(0.0, 0.0), (0.8, 0.45), (4.3, 0.45), (5.0, 0.0)]))
    return p
# ------------------------------------------------------------------ CAVAR (4,0 s, em pe, dianteiras alternadas)
def _pose_cava():
    p = P(raiz=(0, 0.15, -0.95, 15.0), ossos={"OrelhaE": {"X": 8}, "OrelhaD": {"X": 8}, **{nm: {"X": 6} for nm in CAUDA}},
          pes={"MaoE": ((0.05, -0.30, 0), -4, 0), "MaoD": ((-0.05, -0.30, 0), -4, 0), "MetatarsoE": ((0.12, 0.10, 0), -8, 0), "MetatarsoD": ((-0.12, 0.10, 0), -8, 0)})
    return cara_no_chao(p, alvo=1.1, nome="cavar")
POSE_CAVA = _pose_cava()
def clipe_cavar(t):
    """4,0 s: baixa a frente e olha o buraco (0-0,5) -> cava 3 s: cada dianteira sobe, avanca e puxa a terra para tras sob o
    peito (raspando o chao), alternadas (~2 batidas/s por pata) -> volta (3,5-4,0)"""
    p = chaves([(0.0, NEUTRO, None), (0.5, POSE_CAVA, None), (3.5, POSE_CAVA, None), (4.0, NEUTRO, {"MaoE": 0.12, "MaoD": 0.12})])(t)
    if 0.5 < t < 3.5:
        a = suave((t - 0.5) / 0.25) * (1 - suave((t - 3.25) / 0.25))
        for k, fase in (("MaoE", 0.0), ("MaoD", 0.5)):
            u = (t * 2.0 + fase) % 1.0; b, i_, d_ = p["pes"][k]
            if u < 0.45:                                                 # sobe e avanca
                s = u / 0.45; dy = -0.55 * suave(s); dz = 0.40 * math.sin(math.pi * s); inc = 35 * math.sin(math.pi * s)
            else:                                                        # finca e puxa para tras raspando
                s = (u - 0.45) / 0.55; dy = -0.55 + 1.15 * suave(s); dz = 0.0; inc = -10 + 6 * s
            p["pes"][k] = (b + V((0, dy * a, dz * a)), i_ + inc * a, d_ + 10 * a)
        p["raiz"][2] += 0.03 * math.sin(2 * math.pi * 4.0 * t) * a
        somar_ossos(p["ossos"], {"Peito": {"Z": 3 * math.sin(2 * math.pi * 2.0 * t) * a}})
    return p
# ------------------------------------------------------------------ DORMIR ENROLADO (laco 6,0 s)
# 11/11 r2 (usuario: "patas todas tortas e parece que esta quebrando o pescoco"): a curva girava o PEITO (as dianteiras
# ficavam presas onde estavam e torciam) e o pescoco somava 66 graus + cabeca 16 + rolagem 6. Agora o PEITO fica parado
# (dianteiras retas aprovadas do deitado), a curva gira so a GARUPA para o lado esquerdo (a raiz gira o contrario da
# coluna) e as traseiras acompanham a garupa (posicao e direcao); o pescoco vira pouco (cabeca nivelada, sem rolar) e o
# queixo repousa no chao; a cauda contorna a garupa ate perto do focinho.
# r3: a cabeca deitada no chao entrava nas dianteiras (958 vertices); r4: queixo a 0,4 ENCOSTADO na perna, pescoco 12 graus (47 a < 0,45, 0 a < 0,30).
ENR_CURVA = float(os.environ.get("LOBO_ENR_CURVA", "12"))               # graus em Z por osso da coluna (Pelve/Coluna1/Coluna2/Peito)
ENR_PESC = float(os.environ.get("LOBO_ENR_PESC", "12"))                 # giro total do pescoco+cabeca para o lado da garupa
def _pose_enrolado():
    q = _cp(DEIT_B); aplicar(q); P0 = PB["Peito"].head.copy(); r0 = list(q["raiz"])
    ossos_c = ("Coluna1", "Coluna2", "Peito"); tot = ENR_CURVA * len(ossos_c)
    somar_ossos(q["ossos"], {nm: {"Z": ENR_CURVA} for nm in ossos_c})
    q["raiz"][5] = -tot
    for _ in range(3):                                                  # o peito volta exatamente ao lugar
        aplicar(q); d = P0 - PB["Peito"].head; q["raiz"][0] += d.x; q["raiz"][1] += d.y
    Mo, Mn = pose_raiz(r0), pose_raiz(q["raiz"]); T_ = Mn @ Mo.inverted()
    for k in ("MetatarsoE", "MetatarsoD"):
        b, i_, d_ = q["pes"][k]; nb = T_ @ b; q["pes"][k] = (V((nb.x, nb.y, b.z)), i_, d_)
    yaw_t = {k: (-tot if k.startswith("Metatarso") else 0.0) for k in PES}
    g0 = dict(GIRO_PE)
    for k in PES: GIRO_PE[k] = g0[k] + yaw_t[k]                         # durante a montagem (deitado: peso 1) = yaw_pe do clipe
    try:
        q = assentar_deitado(q, "enrolado", PITCH_DEITADO)
        for k in ("MetatarsoE", "MetatarsoD"): q = pe_rente(q, k, "enrolado")
        somar_ossos(q["ossos"], {"Pescoco1": {"Z": ENR_PESC * 0.45}, "Pescoco2": {"Z": ENR_PESC * 0.35}, "Cabeca": {"Z": ENR_PESC * 0.20},
                                 "OrelhaE": {"X": -8}, "OrelhaD": {"X": -8}})
        for i, nm in enumerate(CAUDA):                                  # cauda contorna a garupa para a frente (lado esquerdo)
            somar_ossos(q["ossos"], {nm: {"Z": 10 + 5 * i}})
        q = cara_no_chao(q, float(os.environ.get("LOBO_ENR_QUEIXO", "0.4")), "enrolado", amin=-60)
        q = cauda_no_chao(q, -13.0, "enrolado", atras=False, comprime=-0.30)
        aplicar(q); print("ENROLADO peito desvio %.3f" % (PB["Peito"].head - P0).length, "raiz", [round(x, 2) for x in q["raiz"]],
                          " ".join("%s:(%.2f,%.2f,%.2f)" % (k, *PB[k].tail) for k in PES), flush=True)
    finally:
        GIRO_PE.update(g0)
    q["yaw_pe"] = yaw_t
    return q
POSE_ENROLADO = _pose_enrolado()
def clipe_dormir_enrolado(t):
    p = respira(POSE_ENROLADO, 0.6, 6.0, "fixa")(t)
    p["yaw_pe"] = POSE_ENROLADO["yaw_pe"]
    olhos(p, 1.0)
    return p
CAUDA_NO_CHAO.update({"LamberPata", "DormirEnrolado"})
CLIPES.update({
    "LamberPata": (clipe_lamber_pata, 5.0, False, 0.0, {"NaPata": 0.8, "Pausa": 2.5, "Deitado": 5.0}),
    "Cavar": (clipe_cavar, 4.0, False, 0.0, {"Baixou": 0.5, "Cava": 0.5, "Fim": 4.0}),
    "DormirEnrolado": (clipe_dormir_enrolado, 6.0, True, 0.0, {}),
})
if os.environ.get("LOBO_SONDA"): exec(open(os.environ["LOBO_SONDA"], encoding="utf-8").read())   # medicao (so leitura), sai antes de gerar
