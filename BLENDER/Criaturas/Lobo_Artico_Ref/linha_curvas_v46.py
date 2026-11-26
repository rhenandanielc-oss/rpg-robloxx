"""v46: linha do tempo dos CENARIOS de curva (importado por auditar_curvas_v46.py e vistas_curvas_v46.py). Emula o que o
controlador proposto faz no jogo: os lacos Andar / AndarCurva* / AndarCurvaFechada* tocam na MESMA fase (quadro = tempo de marcha
mod 36) e sao misturados por PESO conforme a taxa de giro omega(t) pedida; o pivo avanca v = 3,0 studs/s na frente e gira omega(t)
(mesmo contrato das curvas: rotacao em volta do proprio pivo). omega -> pesos: |omega| <= 30: Andar (1-a) + Curva (a), a = |omega|/30;
30..50: Curva (1-b) + Fechada (b), b = (|omega|-30)/20. Sinal + = esquerda. Repouso entra so na partida parada (fade como o Controle).
Cada quadro: lista de (acao, quadro, peso) + matriz externa 4x4 (pivo no mundo) + omega + velocidade + apoio por pata.
CENARIOS (parametros = [PROPOSTA][A TESTAR]):
  aberta_E / aberta_D   Andar 1,2 s -> rampa 0,8 s ate 30 graus/s -> 3 ciclos -> rampa 0,8 s -> Andar 1,2 s (~87 graus)
  fechada_E / fechada_D idem ate 50 graus/s (~135 graus)
  inverte_EparaD        30 E -> rampa 1,2 s -> 30 D (curva em S, inverter a curva)
  meia_E                15 graus/s (mistura 50% Andar + 50% Curva) por 4 ciclos: curva bem aberta
  volta_180_E           destino ATRAS: rampa ate 50 E, segura ate somar 180 graus no rumo, rampa de saida (curvas concatenadas)
  parado_para_curva_E   Repouso -> (fade 0,25 s do Controle, sem clipe de partida) Andar ja em curva fechada E [mostra o limite atual]"""
import math, json, os
from mathutils import Vector as V, Matrix
FPS = 30; NQ = 36; VEL = 3.0; BETA = 0.62; FASE = {"TE": 0.0, "DE": 0.25, "TD": 0.5, "DD": 0.75}; T_ = 1.2
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def pesos(om, lado_neutro="E"):
    a = abs(om); s = "Esquerda" if om > 0 else "Direita"
    if a < 1e-6: return [("Andar", 1.0)]
    if a <= 30: return [("Andar", 1 - a / 30), ("AndarCurva" + s, a / 30)]
    b = min(1.0, (a - 30) / 20); return [("AndarCurva" + s, 1 - b), ("AndarCurvaFechada" + s, b)]
RAMPA = float(os.environ.get("RAMPA_V46", "0.8"))
def perfil(nome):
    """lista de omega (graus/s) por quadro e lista de 'repouso' (peso do Repouso por quadro)"""
    q = lambda s_: int(round(s_ * FPS))
    def rampa_hold(om, hold_s):
        L = [0.0] * q(1.2) + [om * suave(i / q(RAMPA)) for i in range(q(RAMPA))] + [om] * q(hold_s) + [om * (1 - suave(i / q(RAMPA))) for i in range(q(RAMPA))] + [0.0] * q(1.2)
        return L
    if nome == "aberta_E": L = rampa_hold(30, 3 * T_)
    elif nome == "aberta_D": L = rampa_hold(-30, 3 * T_)
    elif nome == "fechada_E": L = rampa_hold(50, 2 * T_)
    elif nome == "fechada_D": L = rampa_hold(-50, 2 * T_)
    elif nome == "meia_E": L = [0.0] * q(1.2) + [15 * suave(i / q(RAMPA)) for i in range(q(RAMPA))] + [15.0] * q(4 * T_) + [15 * (1 - suave(i / q(RAMPA))) for i in range(q(RAMPA))] + [0.0] * q(1.2)
    elif nome == "inverte_EparaD":
        L = [0.0] * q(0.6) + [30 * suave(i / q(RAMPA)) for i in range(q(RAMPA))] + [30.0] * q(T_) + [30 - 60 * suave(i / q(1.2)) for i in range(q(1.2))] + [-30.0] * q(T_) + [-30 * (1 - suave(i / q(RAMPA))) for i in range(q(RAMPA))] + [0.0] * q(0.6)
    elif nome == "volta_180_E":
        L = [0.0] * q(0.6); sub = [50 * suave(i / q(RAMPA)) for i in range(q(RAMPA))]; L += sub; ac = sum(sub) / FPS
        saida = sum(50 * (1 - suave(i / q(RAMPA))) for i in range(q(RAMPA))) / FPS
        while ac + saida < 180.0: L.append(50.0); ac += 50.0 / FPS
        L += [50 * (1 - suave(i / q(RAMPA))) for i in range(q(RAMPA))] + [0.0] * q(1.2)
    elif nome == "parado_para_curva_E":
        L = [None] * q(0.5) + [50.0] * q(2 * T_) + [50 * (1 - suave(i / q(RAMPA))) for i in range(q(RAMPA))] + [0.0] * q(1.2)
    else: raise KeyError(nome)
    return L
CENARIOS = ["aberta_E", "aberta_D", "fechada_E", "fechada_D", "inverte_EparaD", "meia_E", "volta_180_E", "parado_para_curva_E"]
def linha(nome):
    L = perfil(nome); out = []; psi = 0.0; pos = V((0.0, 0.0, 0.0)); qm = 0; fade = 0.25; t_andar = None
    for i, om in enumerate(L):
        parado = om is None
        if parado:
            mix = [("Repouso", i % 240, 1.0)]; v = 0.0; omr = 0.0; ap = {k: True for k in FASE}
        else:
            if t_andar is None: t_andar = i
            mix = [(a, qm % NQ, w) for a, w in pesos(om)]
            ta = (i - t_andar) / FPS; wr = 1 - suave(ta / fade) if any(x is None for x in L[:i]) else 0.0
            if wr > 1e-6: mix = [("Repouso", i % 240, wr)] + [(a, qq, w * (1 - wr)) for a, qq, w in mix]
            v = VEL; omr = math.radians(om); u = (qm % NQ) / NQ
            ap = {k: ((u - FASE[k]) % 1.0) < BETA for k in FASE}; qm += 1
        Mx = Matrix.Translation(pos) @ Matrix.Rotation(psi, 4, "Z")
        out.append({"mix": mix, "M": Mx, "omega": 0.0 if parado else om, "v": v, "apoio": ap, "psi": math.degrees(psi), "pos": pos.copy()})
        dt = 1.0 / FPS; pm = psi + omr * dt / 2; pos = pos + V((math.sin(pm), -math.cos(pm), 0.0)) * v * dt; psi += omr * dt
    return out
def aplicar(P, ACTS, REST, mix, frame_set_cache):
    """pose = mistura por peso (slerp normalizado incremental; Quadril.location em media) das acoes nos quadros dados"""
    from mathutils import Quaternion
    poses = [(frame_set_cache(a, q), w) for a, q, w in mix if w > 1e-6]; tot = sum(w for _, w in poses)
    for pb in P:
        acc_w = 0.0; qq = None; loc = V((0, 0, 0))
        for ps, w in poses:
            qa, la = ps[pb.name]; loc += la * (w / tot)
            if qq is None: qq = qa.copy(); acc_w = w
            else:
                if qq.dot(qa) < 0: qa = -qa
                acc_w += w; qq = qq.slerp(qa, w / acc_w)
        pb.rotation_quaternion = qq; pb.location = loc
def raiz_pelos_pes(LT, dedos_fn, minimo=2):
    """MOVIMENTO DO PIVO DERIVADO DAS PATAS APOIADAS (proposta para o controlador): em cada quadro, encaixe rigido 2D (Procrustes
    com rotacao so em Z) que leva a ponta dos dedos das patas apoiadas no quadro atual (referencial do corpo, pose ja misturada) ate
    onde elas estavam no mundo no quadro anterior. Assim, mesmo com o peso/omega mudando no meio de um apoio, a pata apoiada nao
    escorrega: o corpo e que se ajusta. Com menos de 'minimo' patas apoiadas usa o passo nominal (v, omega).
    dedos_fn(mix) -> {pata: Vector (x, y) no referencial do corpo}. Reescreve M, psi e pos de cada quadro de LT."""
    psi = 0.0; pos = V((0.0, 0.0, 0.0)); prev = None
    for i, e in enumerate(LT):
        cur = dedos_fn(e["mix"])
        if prev is not None:
            ks = [k for k in cur if e["apoio"][k] and LT[i - 1]["apoio"][k]]
            if len(ks) >= minimo:
                Rp = Matrix.Rotation(psi, 3, "Z"); b = [pos + Rp @ prev[k] for k in ks]; a_ = [cur[k] for k in ks]
                ca = sum(a_, V((0, 0, 0))) / len(ks); cb = sum(b, V((0, 0, 0))) / len(ks); sx = sy = 0.0
                for p_, q_ in zip(a_, b): pa, qb = p_ - ca, q_ - cb; sx += pa.x * qb.x + pa.y * qb.y; sy += pa.x * qb.y - pa.y * qb.x
                psi = math.atan2(sy, sx); pos = cb - Matrix.Rotation(psi, 3, "Z") @ ca; pos.z = 0.0
            else:
                dt = 1.0 / FPS; omr = math.radians(LT[i - 1]["omega"]); pm = psi + omr * dt / 2
                pos = pos + V((math.sin(pm), -math.cos(pm), 0.0)) * LT[i - 1]["v"] * dt; psi += omr * dt
        e["M"] = Matrix.Translation(pos) @ Matrix.Rotation(psi, 4, "Z"); e["psi"] = math.degrees(psi); e["pos"] = pos.copy(); prev = cur
    return LT
# ---- v46b: SEQUENCIAS DE CLIPES (sem mistura por peso): o controlador troca de clipe na virada do ciclo ----
SEQ_B = {
    "aberta_E": ["Andar", "AndarParaCurvaEsquerda", "AndarCurvaEsquerda", "CurvaParaAndarEsquerda", "Andar"],
    "aberta_D": ["Andar", "AndarParaCurvaDireita", "AndarCurvaDireita", "CurvaParaAndarDireita", "Andar"],
    "fechada_E": ["Andar", "AndarParaCurvaEsquerda", "CurvaParaFechadaEsquerda", "AndarCurvaFechadaEsquerda", "FechadaParaCurvaEsquerda", "CurvaParaAndarEsquerda", "Andar"],
    "fechada_D": ["Andar", "AndarParaCurvaDireita", "CurvaParaFechadaDireita", "AndarCurvaFechadaDireita", "FechadaParaCurvaDireita", "CurvaParaAndarDireita", "Andar"],
    "inverte_EparaD": ["Andar", "AndarParaCurvaEsquerda", "CurvaParaAndarEsquerda", "AndarParaCurvaDireita", "CurvaParaAndarDireita", "Andar"],
    "volta_180_E": ["Andar", "AndarParaCurvaEsquerda", "AndarCurvaEsquerda", "AndarCurvaEsquerda", "AndarCurvaEsquerda", "CurvaParaAndarEsquerda", "Andar"],
    "parado_para_curva_E": ["Repouso*15", "AndarParaCurvaEsquerda", "AndarCurvaEsquerda", "CurvaParaAndarEsquerda", "Andar"],
    "ajuste_breve_E": ["Andar", "CurvaBreveEsquerda", "Andar"],
    "ajuste_curto_D": ["Andar", "CurvaCurtaDireita", "Andar"],
    "zigue_zague": ["Andar", "CurvaBreveEsquerda", "CurvaBreveDireita", "CurvaCurtaEsquerda", "CurvaCurtaDireita", "Andar"],
    # v48: partida e parada com passos (sem fade)
    "partida_parada_reta": ["Repouso*15", "PartidaAndar", "Andar", "ParadaAndar", "RepousoFim*20"],
    "partida_curva_E": ["Repouso*15", "PartidaCurvaEsquerda", "AndarCurvaEsquerda", "CurvaParaAndarEsquerda", "ParadaAndar", "RepousoFim*20"],
    "partida_curva_D": ["Repouso*15", "PartidaCurvaDireita", "AndarCurvaDireita", "CurvaParaAndarDireita", "ParadaAndar", "RepousoFim*20"],
}
SEM_FADE = {"PartidaAndar", "PartidaCurvaEsquerda", "PartidaCurvaDireita"}
def linha_seq(nome, VJ, fade_s=0.25):
    """VJ = curvas_v46b.json['acoes']. Andar = reto a VEL; Repouso*N = N quadros parado; depois do Repouso, fade de fade_s (como o
    Controle) misturando o Repouso no inicio do primeiro clipe de marcha (o unico trecho com mistura)."""
    out = []; base = Matrix.Identity(4); qm = 0; t_rep = None
    for item in SEQ_B[nome]:
        if item.startswith("RepousoFim"):
            n = int(item.split("*")[1])
            for i in range(n): out.append({"mix": [("Repouso", i % 240, 1.0)], "M": base.copy(), "omega": 0.0, "v": 0.0, "apoio": {k: True for k in FASE}, "clipe": "Repouso", "q": i})
            continue
        if item.startswith("Repouso"):
            n = int(item.split("*")[1])
            for i in range(n): out.append({"mix": [("Repouso", (240 - n + i) % 240, 1.0)], "M": base.copy(), "omega": 0.0, "v": 0.0, "apoio": {k: True for k in FASE}, "clipe": "Repouso", "q": i})
            t_rep = len(out); continue
        if item in SEM_FADE: t_rep = None
        nq = NQ if item == "Andar" else VJ[item]["quadros"]
        for q in range(nq):
            if item == "Andar": ext = Matrix.Translation(V((0.0, -VEL * q / FPS, 0.0))); om = 0.0
            else:
                x, y, ps = VJ[item]["externa_por_quadro_xy_psi"][q]; ext = Matrix.Translation(V((x, y, 0.0))) @ Matrix.Rotation(math.radians(ps), 4, "Z"); om = VJ[item]["omega_por_quadro"][q]
            u = (qm % NQ) / NQ; ap = {k: ((u - FASE[k]) % 1.0) < BETA for k in FASE}
            if item != "Andar" and "apoio_por_quadro" in VJ[item] and item in SEM_FADE | {"ParadaAndar"}: ap = {k: VJ[item]["apoio_por_quadro"][k][q] for k in FASE}
            mix = [(item, q, 1.0)] if item != "Andar" else [("Andar", qm % NQ, 1.0)]
            if t_rep is not None:
                wr = 1 - suave((len(out) - t_rep) / (fade_s * FPS))
                if wr > 1e-6: mix = [("Repouso", (t_rep - 1) % 240, wr), (mix[0][0], mix[0][1], 1 - wr)]
            M = base @ ext; out.append({"mix": mix, "M": M, "omega": om, "v": VEL, "apoio": ap, "clipe": item, "q": q}); qm += 1
        if item == "Andar": base = base @ Matrix.Translation(V((0.0, -VEL * nq / FPS, 0.0)))
        else:
            x, y, ps = VJ[item]["externa_por_quadro_xy_psi"][nq]; base = base @ Matrix.Translation(V((x, y, 0.0))) @ Matrix.Rotation(math.radians(ps), 4, "Z")
    for e in out:
        f = e["M"].to_3x3() @ V((0, -1, 0)); e["psi"] = math.degrees(math.atan2(f.x, -f.y)); e["pos"] = e["M"].translation.copy()
    return out
