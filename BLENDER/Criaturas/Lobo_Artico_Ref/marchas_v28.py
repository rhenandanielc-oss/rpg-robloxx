"""v28 (modulo comum, sem bpy): marchas ciclicas (G de cada marcha igual ao da clipes_v24: Andar com centro 0 e rolo_ini 0,72) e a
LINHA DO TEMPO da sequencia de troca de marchas usada pela auditoria e pelo render:
Andar x2 | AndarParaTrote | Trote x3 | TroteParaCorrida | Corrida x3 | CorridaParaTrote | Trote x2 | TroteParaAndar | Andar x2
(sem quadros duplicados: o ultimo quadro de cada clipe ciclico = q0, a transicao comeca em q0 = q0 da marcha de origem e o seu
quadro final = q0 da marcha de destino). Deslocamento por quadro: marchas -v/30; transicoes = CURVA gravada (marchas_v28.json)."""
import math
NQ = {"Andar": 36, "Trote": 18, "Corrida": 14}
TRANS = {"AndarParaTrote": ("Andar", "Trote"), "TroteParaAndar": ("Trote", "Andar"), "TroteParaCorrida": ("Trote", "Corrida"), "CorridaParaTrote": ("Corrida", "Trote")}
def marchas(CJ):
    A = CJ["marchas"]["Andar"]
    return {"Andar": {"T": A["T"], "D": A["D"], "apoio": A["apoio"], "fases": A["fases"], "centro": {k: 0.0 for k in ("DE", "DD", "TE", "TD")},
                      "altura": {"D": A["altura_dianteira"], "T": A["altura_traseira"]}, "rolamento_graus": A["rolamento_graus"], "rolo_ini": 0.72,
                      "dobra_graus": {"D": A["dobra_balanco_dianteira_graus"], "T": A["dobra_balanco_traseira_graus"]}, "v_studs_s": A["v_studs_s"]},
            "Trote": CJ["marchas"]["Trote"], "Corrida": CJ["marchas"]["Corrida"]}
def linha(TJ):
    LT = []
    def gait(n, ciclos): LT.extend((n, q) for _ in range(ciclos) for q in range(NQ[n]))
    def tr(n): LT.extend((n, q) for q in range(TJ["acoes"][n]["quadros"]))
    gait("Andar", 2); tr("AndarParaTrote"); gait("Trote", 3); tr("TroteParaCorrida"); gait("Corrida", 3); tr("CorridaParaTrote"); gait("Trote", 2); tr("TroteParaAndar"); gait("Andar", 2)
    LT.append(("Andar", 0)); return LT
def deslocamento(LT, G, TJ, FPS=30):
    Xc = []; x = 0.0
    for i, (ac_, q) in enumerate(LT):
        if i > 0:
            if ac_ in TRANS:
                Xs = TJ["acoes"][ac_]["X_por_quadro"]; x += (Xs[q] - Xs[q - 1]) if q > 0 else -G[TRANS[ac_][0]]["v_studs_s"] / FPS
            else: x += -G[ac_]["v_studs_s"] / FPS
        Xc.append(x)
    return Xc
def apoio(G, TJ, acao, k, q, FPS=30):
    if acao in TRANS: return TJ["acoes"][acao]["apoio_por_quadro"][k][q]
    g = G[acao]; u = ((q / FPS / g["T"]) - g["fases"][k]) % 1.0; return u < g["apoio"]
