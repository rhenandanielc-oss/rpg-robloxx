# Marcha v30 (10/11/2026; copia corrigida da v29 - marcha_v29.py fica intacto): Andar e Corrida do Lobo Ancestral inspirados no movimento do Lobo Artico v29 (anim_v29; scripts
# Lobo_Artico_Ref/clipes_v12.py e clipes_v21.py, so lidos). Carregado por exec() dentro de anim_lobo.py com LOBO_MARCHA29=1:
# substitui SO "Andar" e "Corrida" (Trote, Partida, Freada, transicoes e habilidades seguem a marcha v28).
# O que vem do Artico (principios, nao curvas copiadas): balanco min-jerk com a altura zerando so no toque; rolamento da sola
# so no fim do apoio; dobra do carpo/jarrete forte no meio do balanco e desfeita antes do pouso; corpo nivelado no Andar
# (quadril quase sem sobe-desce, sem arfagem); galope ROTATORIO (TE -> TD -> DD -> DE) com suspensao recolhida, a frente subindo
# e descendo junto com a traseira, coluna que recolhe e estende, cabeca estabilizada, cauda de contrapeso, orelhas para tras.
# Adaptado ao Ancestral: pernas mais longas (L 4,7/4,95 contra 3,9/4,4), dedos retos para a frente (o Artico abre 3-15 graus),
# dobra do carpo limitada (carpo auxiliar da v28; acima de ~90 graus a malha volta a formar o "toco"), passada pela cernelha.
def marcha29(T, L, apoio, fases, alt, flex, cfg):
    """alt = {"D": , "T": } altura do balanco; flex = {"D": , "T": } dobra maxima (graus) do carpo/jarrete no balanco;
    cfg: rolamento, rolo_ini, centro {pe: dy do centro do apoio}, dedo_curl, corpo(...)."""
    def f(t):
        u = (t / T) % 1.0; p = pose_base(); pes = {}
        for k in PES:
            uk = (u - fases[k]) % 1.0; d_ = "D" if k.startswith("Mao") else "T"; c = cfg["centro"][k]
            roll = cfg["rolamento"][d_]; ri = cfg.get("rolo_ini", 0.72)
            if uk < apoio:
                s = uk / apoio; dy = c - L / 2 + L * s; dz = 0.0
                incl = lerp(-INCL_POUSO, roll, suave((s - ri) / (1 - ri))); dedo = 0.0
            else:
                w = (uk - apoio) / (1 - apoio); m = w * w * w * (10 - 15 * w + 6 * w * w)       # min-jerk
                dy = c + L / 2 - L * m; dz = alt[d_] * math.sin(math.pi * w ** 0.8) ** 1.15        # altura so zera no toque
                dob = math.sin(math.pi * w) ** 1.5 * (1 - suave((w - 0.7) / 0.3))
                incl = roll * (1 - suave((w - 0.2) / 0.4)) + flex[d_] * dob - INCL_POUSO * suave((w - 0.85) / 0.15)
                dedo = cfg.get("dedo_curl", 20.0) * dob
            dx = 0.0
            if uk >= apoio and d_ == "T":                                # v30: traseira abre um pouco no balanco (como a v28; o polo segue)
                dx = cfg.get("abre_tras", 0.0) * (1 if k.endswith("E") else -1) * math.sin(math.pi * (uk - apoio) / (1 - apoio))
            pes[k] = (B0[k] + V((dx, dy, dz)), incl, dedo)
        p["pes"] = pes; p["eixo_perna"] = True; p["polo_corpo"] = POLO_CORPO30; p["polo_plano"] = POLO_PLANO30
        p["raiz"], p["ossos"] = cfg["corpo"](t, u, pes)
        if PLANO_PE30 and not _sem_plano[0]:                             # v30: o JARRETE perto do plano de repouso da perna traseira (a
            for l_ in ("E", "D"):                                        # pata recuava em linha reta e saia do plano inclinado: o joelho
                k = "Metatarso" + l_; bola, incl, dedo = pes[k]          # girava e a coxa torcia ate 4,6-5,3 graus no galope).
                uk = (u - fases[k]) % 1.0                                # APOIO: x constante (o do meio do apoio) -> sem deslize lateral;
                dmid = _dx_meio(k)                                       # BALANCO: correcao completa, com entrada/saida suaves
                if uk < apoio: dxp = dmid
                else:
                    w = (uk - apoio) / (1 - apoio); dxp = lerp(dmid, _dx_plano(p, k), math.sin(math.pi * w) ** 0.5)
                pes[k] = (bola + V((dxp * PLANO_PE30, 0, 0)), incl, dedo)
        return p
    _sem_plano = [False]; _cache = {}
    def _dx_plano(p, k):
        l_ = k[-1]; bola, incl, dedo = p["pes"][k]; Mr = pose_raiz(p["raiz"])
        jar = bola + Matrix.Rotation(rad(incl), 3, EIXO_PATA[k]) @ (W0[k] - B0[k]); Hh = Mr @ BD["Coxa" + l_].head_local
        nn = (Mr.to_3x3() @ PLANO_TRAS[l_]).normalized(); return -((jar - Hh).dot(nn)) / nn.x
    def _dx_meio(k):
        if k not in _cache:
            _sem_plano[0] = True; tm = ((fases[k] + apoio / 2) % 1.0) * T; q = f(tm); _sem_plano[0] = False
            _cache[k] = _dx_plano(q, k)
        return _cache[k]
    return f
def _ondas(u, f): return math.sin(2 * math.pi * (u + f))
def corpo_andar29(t, u, pes):
    """corpo nivelado (Artico: quadril quase sem sobe-desce, sem arfagem), balanco lateral suave, coluna em onda, cabeca
    estabilizada, cauda e orelhas discretas; escapula acompanha a pata."""
    z = -0.10 - 0.025 * math.cos(4 * math.pi * u); rol = 1.2 * _ondas(u, 0.25); yaw = 1.4 * _ondas(u, 0.0)
    o = {"Pelve": {"Z": -1.6 * _ondas(u, 0.25), "Y": 1.4 * _ondas(u, 0.0)}, "Coluna1": {"Z": 0.9 * _ondas(u, 0.30)}, "Coluna2": {"Z": 1.1 * _ondas(u, 0.35)},
         "Peito": {"Z": 0.8 * _ondas(u, 0.40), "Y": -0.8 * _ondas(u, 0.25)},
         "Pescoco1": {"X": 1.3 * math.cos(4 * math.pi * u + 0.6), "Z": -1.2 * _ondas(u, 0.4)}, "Cabeca": {"X": -1.6 * math.cos(4 * math.pi * u + 0.9), "Z": -0.8 * _ondas(u, 0.45)},
         "Mandibula": {"X": 0.0}}
    for i, nm in enumerate(CAUDA):
        k = (i + 1) / NC; o[nm] = {"Z": 2.4 * k * _ondas(u, 0.1 + 0.25 * k), "X": 4.0 + 1.0 * k * math.cos(4 * math.pi * u + 1.5 * k)}
    for nm in ("OrelhaE", "OrelhaD"): o[nm] = {"X": 2.0 * math.cos(4 * math.pi * u + 1.2), "Y": 0.0}
    for nm in ("JubaE", "JubaD", "JubaPeito"): o[nm] = {"X": 2.5 * math.cos(4 * math.pi * u - 1.4)}
    for lado in ("E", "D"): o["Escapula" + lado] = {"X": 7.0 * (pes["Mao" + lado][0].y - B0["Mao" + lado].y)}
    return [0, 0, z, 0.0, rol, yaw], o
SUSP29 = 0.84
PLANO_PE30 = float(os.environ.get("LOBO_V30_PLANO_PE", "1.0"))       # v30: fracao da correcao lateral do jarrete
POLO_PLANO30 = bool(int(os.environ.get("LOBO_V30_POLO_PLANO", "0")))   # v30: polo do joelho no plano de repouso
POLO_CORPO30 = float(os.environ.get("LOBO_V30_POLO_CORPO", "0.0"))      # 0 = como a v29; 1 = polo acompanha a raiz                                                          # centro da suspensao recolhida (fase do ciclo)
def corpo_corrida29(t, u, pes):
    """galope rotatorio: a coluna recolhe na suspensao (depois das dianteiras) e estende no impulso das traseiras; a frente
    sobe e desce junto (cernelha), o quadril menos; cabeca estabilizada; cauda de contrapeso; orelhas para tras."""
    fl = math.cos(2 * math.pi * (u - SUSP29))                            # +1 recolhido, -1 estendido
    z = -0.42 + float(os.environ.get("LOBO_V30_Z", "0.10")) * math.cos(2 * math.pi * (u - SUSP29 + 0.06))
    pit = float(os.environ.get("LOBO_V30_PIT", "4.5")) * math.cos(2 * math.pi * (u - float(os.environ.get("LOBO_V30_PIT_F", "0.48"))))                       # arfagem (frente sobe no impulso das dianteiras)
    cf = float(os.environ.get("LOBO_V30_COLUNA", "0.5"))                 # v30: escala da flexao da coluna/pelve no galope
    o = {"Pelve": {"X": -5.0 * cf * fl}, "Coluna1": {"X": 5.0 * cf * fl}, "Coluna2": {"X": 5.0 * cf * fl}, "Peito": {"X": 3.5 * cf * fl},
         "Pescoco1": {"X": 10.0 - 0.6 * (pit + 6.0 * fl)}, "Pescoco2": {"X": -0.25 * (pit + 6.0 * fl)}, "Cabeca": {"X": -6.0 - 0.15 * (pit + 6.0 * fl)},
         "Mandibula": {"X": 3.0}}
    for i, nm in enumerate(CAUDA):
        k = (i + 1) / NC; o[nm] = {"X": (14.0 if i == 0 else 3.0) * 1.0 - (3.0 + 2.0 * k) * fl, "Z": (0.6 + 0.6 * k) * _ondas(u, 0.2 + 0.2 * k)}
    for nm in ("OrelhaE", "OrelhaD"): o[nm] = {"X": -16.0 - 2.0 * fl, "Y": 0.0}
    for nm in ("JubaE", "JubaD", "JubaPeito"): o[nm] = {"X": 6.0 * fl}
    for lado in ("E", "D"): o["Escapula" + lado] = {"X": 12.0 * (pes["Mao" + lado][0].y - B0["Mao" + lado].y)}
    piv = float(os.environ.get("LOBO_V30_PIVO_QUADRIL", "1.0"))         # v30: arfagem em torno do QUADRIL (a frente sobe/desce, o quadril
    Rp = Matrix.Rotation(rad(pit), 3, "X"); H = QUADRIL                   # fica estavel, como no Artico); v29 girava no centro do tronco
    tr = (H - (C + Rp @ (H - C))) * piv
    return [0, tr.y, z + tr.z, pit, 0.6 * _ondas(u, 0.0), 0], o
ANDAR29 = dict(T=36 / FPS, L=2.25, apoio=0.62, fases={"MetatarsoE": 0.0, "MaoE": 0.25, "MetatarsoD": 0.5, "MaoD": 0.75},
               alt={"D": 0.58, "T": 0.48}, flex={"D": float(os.environ.get("LOBO_V30_FLEX_AD", "10")), "T": 34.0},
               cfg=dict(rolamento={"D": float(os.environ.get("LOBO_V30_ROL_AD", "14")), "T": 20.0}, rolo_ini=0.72, dedo_curl=18.0,
                        centro={"MaoE": 0.0, "MaoD": 0.0, "MetatarsoE": 0.55, "MetatarsoD": 0.55}, corpo=corpo_andar29))
GALOPE29 = dict(T=14 / FPS, L=2.8, apoio=0.28, fases={"MetatarsoE": 0.0, "MetatarsoD": 0.08, "MaoD": 0.30, "MaoE": 0.40},
                alt={"D": 0.95, "T": 0.85}, flex={"D": float(os.environ.get("LOBO_V30_FLEX_CD", "38")), "T": float(os.environ.get("LOBO_V30_FLEX_CT", "30"))},
                cfg=dict(rolamento={"D": 20.0, "T": float(os.environ.get("LOBO_V30_ROL_T", "12"))}, rolo_ini=0.6, dedo_curl=24.0, abre_tras=float(os.environ.get("LOBO_V30_ABRE_T", "0.0")),
                         centro={"MaoE": -0.25, "MaoD": -0.25, "MetatarsoE": float(os.environ.get("LOBO_V30_CT_C", "0.35")), "MetatarsoD": float(os.environ.get("LOBO_V30_CT_C", "0.35"))}, corpo=corpo_corrida29))
def vel29(M): return M["L"] / (M["apoio"] * M["T"])
CLIPES["Andar"] = (marcha29(**ANDAR29), ANDAR29["T"], True, vel29(ANDAR29), {})
CLIPES["Corrida"] = (marcha29(**GALOPE29), GALOPE29["T"], True, vel29(GALOPE29), {})
APOIO["Andar"] = ANDAR29; APOIO["Corrida"] = GALOPE29
