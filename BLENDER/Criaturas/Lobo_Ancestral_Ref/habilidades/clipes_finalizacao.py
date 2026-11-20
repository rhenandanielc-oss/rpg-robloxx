# Finalizacao PROPRIA do Lobo Ancestral (20/11/2026): mordida no FLANCO/barriga do inimigo caido + sacudidas da CABECA.
# Carregado por exec() em anim_lobo.py com LOBO_FINAL=1 (clipes aprovados intactos). Substitui a v81 (morder o pescoco,
# puxar o alvo e "estrangular" com o Comer congelado), recusada pelo usuario: "ir ate o meio do corpo do inimigo caido,
# na regiao lateral da barriga, morder e sacudir a propria cabeca/boca; nao puxar, nao estrangular, nao sacudir o corpo dele".
# Principios de lobo real (so principios): aproxima de lado, abaixa o peito com as dianteiras um pouco abertas e firmes,
# o pescoco desce e a boca abre; fecha e SEGURA; sacode com a cabeca/pescoco (torcao curta, 2-3 vezes), os ombros
# absorvem e as patas ficam plantadas; orelhas para tras, cauda baixa reagindo pouco.
# Clipe NO LUGAR (o jogo posiciona o lobo ao lado do caido). Alvo: focinho na altura do flanco de um lobo deitado.
FIN_ALTURA = float(os.environ.get("LOBO_FIN_ALT", "0.55"))      # r2: queixo na faixa da barriga de um lobo deitado de lado (flanco z 0,05-1,28)
FIN_ROLL = float(os.environ.get("LOBO_FIN_ROLL", "12"))         # r2: torcao da cabeca no eixo do focinho (graus) - a ponta fica presa
def _pose_flanco(alt=None, dz=None, pit=None, nome="mordida_flanco"):
    """peito baixo e um pouco a frente, dianteiras abertas e firmes, traseiras carregadas; pescoco desce ate o flanco"""
    # r2: agacha a frente (como o Comer aprovado) para o pescoco descer ~60-80 graus, nao dobrar ao maximo (r1: 120 graus)
    dz = float(os.environ.get("LOBO_FIN_DZ", "1.25")) if dz is None else dz
    pit = float(os.environ.get("LOBO_FIN_PIT", "18")) if pit is None else pit
    p = P(raiz=(0, -0.05, -dz, pit),
          ossos={"OrelhaE": {"X": -24, "Y": 6}, "OrelhaD": {"X": -24, "Y": -6}, "JubaPeito": {"X": 4},
                 **{nm: {"X": -10 if i == 0 else -3} for i, nm in enumerate(CAUDA)}},
          pes={"MaoE": ((0.32, -0.42, 0), -8, 0), "MaoD": ((-0.32, -0.42, 0), -8, 0),
               "MetatarsoE": ((0, 0.08, 0), -10, 0), "MetatarsoD": ((0, 0.08, 0), -10, 0)})
    return cara_no_chao(p, alvo=FIN_ALTURA if alt is None else alt, nome=nome)
def _com(base, extra, raiz_d=None):
    q = {"raiz": list(base["raiz"]), "ossos": {k: dict(v) for k, v in base["ossos"].items()}, "pes": dict(base["pes"])}
    somar_ossos(q["ossos"], extra)
    if raiz_d:
        for i, d in enumerate(raiz_d): q["raiz"][i] += d
    return q
def _fabrica(POSE_FLANCO):
    POSE_FLANCO_ABRE = _com(POSE_FLANCO, {"Mandibula": {"X": 26}, "Cabeca": {"X": -4}})
    POSE_FLANCO_MORDE = _com(POSE_FLANCO, {"Mandibula": {"X": 3}, "Pescoco1": {"X": 2}}, (0, -0.06, -0.04, 1.0))
    POSE_FLANCO_PUXA = _com(POSE_FLANCO_MORDE, {"Pescoco1": {"X": -3}, "Pescoco2": {"X": -2}, "Cabeca": {"X": 4}}, (0, 0.10, 0, -1.0))
    def clipe_mordida_flanco(t):
        """2,6 s: entrada com peso (0-0,45, boca abre) -> CONTATO 0,50 (fecha) -> segura e sacode 3x a CABECA (0,62-1,80; torcao
        no eixo do focinho + pescoco, ombros absorvem, patas plantadas) -> solta (1,85-2,05) -> volta ao repouso (2,6)"""
        p = chaves([(0.0, NEUTRO, {"MaoE": 0.10, "MaoD": 0.10}), (0.42, POSE_FLANCO_ABRE, None), (0.50, POSE_FLANCO_MORDE, None),
                    (0.62, POSE_FLANCO_MORDE, None), (1.10, POSE_FLANCO_PUXA, None), (1.80, POSE_FLANCO_MORDE, None),
                    (2.0, _com(POSE_FLANCO, {"Mandibula": {"X": 16}}), None), (2.6, NEUTRO, {"MaoE": 0.10, "MaoD": 0.10})])(t)
        if 0.62 < t < 1.80:                                               # 3 sacudidas curtas, amortecidas, da cabeca/pescoco
            u = (t - 0.62) / 1.18
            env = math.sin(math.pi * min(1.0, u * 1.6)) if u < 0.62 else (1.0 - (u - 0.62) / 0.38) * 0.9
            w = math.sin(2 * math.pi * 2.55 * (t - 0.62)) * max(0.0, env)
            somar_ossos(p["ossos"], {"Cabeca": {"Y": FIN_ROLL * w, "Z": -1.0 * w}, "Pescoco2": {"Y": 0.40 * FIN_ROLL * w, "Z": 1.5 * w},
                                     "Pescoco1": {"Z": 1.0 * w}, "Peito": {"Z": -1.5 * w}, "Coluna2": {"Z": -0.8 * w},
                                     "OrelhaE": {"Y": 4 * w}, "OrelhaD": {"Y": 4 * w},
                                     **{nm: {"Z": -4.0 * w * (i + 1) / NC} for i, nm in enumerate(CAUDA)}})
            p["raiz"][4] = p["raiz"][4] + 0.8 * w if len(p["raiz"]) > 4 else p["raiz"]
        return p
    return clipe_mordida_flanco
POSE_FLANCO = _pose_flanco()
clipe_mordida_flanco = _fabrica(POSE_FLANCO)
CLIPES["Hab_MordidaFlanco"] = (clipe_mordida_flanco, 2.6, False, 0.0,
                               {"Antecipacao": 0.30, "Contato": 0.50, "Sacudida": 0.62, "Solta": 1.85, "Fim": 2.6})
# 20/11 r3 (queda lateral): o alvo agora cai DE LADO e a barriga exposta e uma parede vertical (z ~0,9-2,2 no meio do
# tronco); o clipe aprovado fecha a boca a 0,48 (barriga de lobo deitado sobre o peito) e ficava abaixo dela, junto as
# pernas. Variante propria com o queixo no meio da barriga lateral e menos agachamento; mesmo ritmo e marcadores.
FIN_LADO_ALT = float(os.environ.get("LOBO_FIN_LADO_ALT", "1.30"))
FIN_LADO_DZ = float(os.environ.get("LOBO_FIN_LADO_DZ", "0.55"))
FIN_LADO_PIT = float(os.environ.get("LOBO_FIN_LADO_PIT", "8"))
CLIPES["Hab_MordidaFlancoLado"] = (_fabrica(_pose_flanco(FIN_LADO_ALT, FIN_LADO_DZ, FIN_LADO_PIT, "mordida_flanco_lado")), 2.6, False, 0.0,
                                   {"Antecipacao": 0.30, "Contato": 0.50, "Sacudida": 0.62, "Solta": 1.85, "Fim": 2.6})
