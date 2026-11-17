# Comportamentos de vida - LOTE 5 (12/11/2026): revisao dos clipes existentes. Lotes 1-4 aprovados pelo usuario.
# Carregado por exec() dentro de anim_lobo.py com LOBO_VIDA=5. SUBSTITUI, so neste lote, os clipes de mesmo nome
# (Repouso, Observar, Sentado, Uivo, Adormecer, Despertar); a base aprovada (v31: rig18/Lobo_Ancestral_Anim_v31.blend,
# clipes30/) fica INTACTA para comparacao. Os outros clipes da base nao mudam (auditoria sem defeito medido).
# Auditoria 12/11 (cabeca a < 0,30 do eixo do antebraco/pata, erro de IK) dos 24 clipes da base:
# - Adormecer: 225 vertices da cabeca DENTRO do antebraco direito (1,3-2,0 s) - a cabeca atravessa a perna na transicao;
# - Despertar: 264 (0,1-0,5 s), o mesmo na volta;
# - Uivo: IK 0,074 (o corpo subia 0,10 com as patas plantadas) e boca escancarada (lobo uiva com a boca em "O");
# - Descanso: 12-17 (a cabeca ENCOSTA na pata direita - pose da foto aprovada; mantida);
# - demais: 0.
# Naturalidade (principios de lobos reais): parado o lobo troca o peso entre as patas, as orelhas giram de forma
# independente para sons, pisca, fareja o ar de vez em quando; ao olhar para os lados as orelhas giram ANTES da cabeca
# e o corpo acompanha um pouco.
def _jan5(t, a, pico, b):
    """0 fora de (a, b), sobe suave ate 1 no pico e desce"""
    if t <= a or t >= b: return 0.0
    return suave((t - a) / (pico - a)) if t < pico else 1.0 - suave((t - pico) / (b - pico))
def _pisca(t, ts, d=0.18):
    """fracao fechada das palpebras: piscadas curtas em ts"""
    f = 0.0
    for t0 in ts:
        u = (t - t0) / d
        if 0.0 <= u <= 1.0: f = max(f, math.sin(math.pi * u))
    return f
def _orelha(t, t0, d=0.45):
    """giro rapido de uma orelha para um som e volta (0..1)"""
    return _jan5(t, t0, t0 + 0.12, t0 + d)
def _fungadas(t, a, b, hz=5.0):
    w = _jan5(t, a, a + 0.15, b) if b - a > 0.3 else 0.0
    return w * max(0.0, math.sin(2 * math.pi * hz * t))
# ------------------------------------------------------------------ REPOUSO r5 (laco 8 s)
REP_T = 8.0
def clipe_repouso5(t):
    """laco 8 s sobre o Repouso aprovado (respiracao 4 s): troca de peso E/D, cabeca olha devagar, orelhas giram
    sozinhas (E 1,3 s; D 4,6 s; as duas para a frente 6,2 s), piscadas (2,2 e 5,8 s), fareja o ar (3,2-3,8 s)"""
    p = clipe_repouso(t % 4.0)
    w = 2 * math.pi * t / REP_T
    p["raiz"][0] += 0.05 * math.sin(w); p["raiz"][4] += 1.0 * math.sin(w)              # peso passa de uma pata para a outra
    somar_ossos(p["ossos"], {"Pelve": {"Z": 1.2 * math.sin(w)}, "Pescoco2": {"Z": 3.0 * math.sin(w + 1.0)}, "Cabeca": {"Z": 2.5 * math.sin(w + 1.3)}})
    oe, od, of = _orelha(t, 1.3), _orelha(t, 4.6), _jan5(t, 6.0, 6.3, 7.0)
    somar_ossos(p["ossos"], {"OrelhaE": {"Z": 20 * oe, "X": 3 * oe + 6 * of}, "OrelhaD": {"Z": -20 * od, "X": 3 * od + 6 * of}})
    fu = _fungadas(t, 3.2, 3.8); ar = _jan5(t, 3.0, 3.3, 4.0)
    somar_ossos(p["ossos"], {"Cabeca": {"X": -4 * ar - 1.0 * fu}, "Mandibula": {"X": 0.8 * fu}})
    olhos(p, _pisca(t, (2.2, 5.8)))
    return p
# ------------------------------------------------------------------ OBSERVAR r5 (4,5 s, mesmos marcadores)
def clipe_observar5(t):
    """como o aprovado, mais: orelhas giram 0,15 s ANTES da cabeca, piscada no inicio de cada giro, o peso vai para o
    lado do olhar, fareja em cada lado"""
    ks = [(0.0, 0), (0.6, 38), (1.6, 38), (2.4, -34), (3.4, -34), (4.2, 0), (4.5, 0)]
    def yaw_em(tt):
        tt = min(4.5, max(0.0, tt))
        for i in range(len(ks) - 1):
            if ks[i][0] <= tt <= ks[i + 1][0]: return lerp(ks[i][1], ks[i + 1][1], suave((tt - ks[i][0]) / (ks[i + 1][0] - ks[i][0])))
        return 0.0
    p = clipe_observar(t)
    ya, yo = yaw_em(t), yaw_em(t + 0.15)
    somar_ossos(p["ossos"], {"OrelhaE": {"Z": (yo - ya) * 0.5}, "OrelhaD": {"Z": (yo - ya) * 0.5}})
    p["raiz"][0] += 0.04 * ya / 38.0; p["raiz"][4] += 0.8 * ya / 38.0
    fu = _fungadas(t, 0.9, 1.5) + _fungadas(t, 2.7, 3.3)
    somar_ossos(p["ossos"], {"Cabeca": {"X": -1.0 * fu}, "Mandibula": {"X": 0.8 * fu}})
    olhos(p, _pisca(t, (0.05, 1.65, 3.45)))
    return p
# ------------------------------------------------------------------ SENTADO r5 (laco 8 s)
SENT_RESP = respira(SENT)
def clipe_sentado5(t):
    """laco 8 s sobre o Sentado aprovado (respiracao 4 s): olha devagar para os lados, orelhas sozinhas, piscadas,
    ponta da cauda (apoiada) mexe uma vez"""
    p = SENT_RESP(t % 4.0); w = 2 * math.pi * t / 8.0
    somar_ossos(p["ossos"], {"Pescoco2": {"Z": 5.0 * math.sin(w)}, "Cabeca": {"Z": 4.0 * math.sin(w + 0.4)}})
    oe, od = _orelha(t, 2.0), _orelha(t, 5.4)
    somar_ossos(p["ossos"], {"OrelhaE": {"Z": 18 * oe}, "OrelhaD": {"Z": -18 * od}})
    pc = _jan5(t, 6.2, 6.5, 7.2)
    for i, nm in enumerate(CAUDA[-3:]): somar_ossos(p["ossos"], {nm: {"Z": 8 * pc * (i + 1) / 3}})
    olhos(p, _pisca(t, (1.2, 4.4, 7.0)))
    return p
# ------------------------------------------------------------------ UIVO r5 (4,0 s, mesmos marcadores 0,78 / 3,2)
U5_P1, U5_P2, U5_CAB, U5_BOCA = -32.0, -24.0, -36.0, 11.0                  # = UivoEmPe do lote 4 (focinho 61 graus)
def clipe_uivo5(t):
    """inspira (0,1-0,7) -> focinho sobe a 61 graus (0,3-0,75) -> uiva em "O" com vibrato e olhos semicerrados
    (0,78-3,2, a nota sobe em 1,0 e cai no fim) -> volta (3,2-4,0). Corpo nao sobe (a base subia 0,10: IK 0,074)"""
    p = chaves([(0.0, NEUTRO, None), (0.4, P(raiz=(0, 0.06, 0.0, -4.0), ossos={"Peito": {"X": -2}, **{nm: {"X": (-6 if i == 0 else 1.0)} for i, nm in enumerate(CAUDA)}}), None),
                (3.6, P(raiz=(0, 0.06, 0.0, -4.0), ossos={"Peito": {"X": -2}, **{nm: {"X": (-6 if i == 0 else 1.0)} for i, nm in enumerate(CAUDA)}}), None), (4.0, NEUTRO, None)])(t)
    f = suave((t - 0.3) / 0.45) * (1 - suave((t - 3.3) / 0.6))
    somar_ossos(p["ossos"], {"Pescoco1": {"X": U5_P1 * f}, "Pescoco2": {"X": U5_P2 * f}, "Cabeca": {"X": U5_CAB * f},
                             "OrelhaE": {"X": -8 * f, "Y": 6 * f}, "OrelhaD": {"X": -8 * f, "Y": -6 * f}, "JubaPeito": {"X": -4 * f}})
    ins = _jan5(t, 0.1, 0.55, 1.0); exp = suave((t - 0.8) / 2.4)
    somar_ossos(p["ossos"], {"Peito": {"X": -3.0 * ins + 1.5 * exp * f}, "JubaPeito": {"X": 2.0 * ins}})
    nota = _jan5(t, 0.7, 0.95, 3.35) if t < 0.95 else (1.0 if t < 3.2 else _jan5(t, 0.7, 0.95, 3.45))
    sobe = _jan5(t, 0.9, 1.3, 2.0); cai = _jan5(t, 2.7, 3.15, 3.6)
    somar_ossos(p["ossos"], {"Cabeca": {"X": -4 * sobe + 6 * cai}, "Pescoco2": {"X": 3 * cai},
                             "Mandibula": {"X": (U5_BOCA + 2.0 * sobe - 4.0 * cai) * nota + 0.6 * math.sin(2 * math.pi * 5.0 * t) * nota}})
    olhos(p, 0.35 * nota)
    return p
# ------------------------------------------------------------------ ADORMECER / DESPERTAR r5 (cabeca contorna a perna)
# medido quadro a quadro (giro do pescoco x vertices da cabeca dentro da perna): na transicao a cabeca passa pelo
# antebraco DIREITO e a pata esquerda recolhe por baixo do queixo. Correcao: o pescoco gira para a esquerda (longe da
# pata direita) durante a transicao e volta a zero no fim (a pose de dormir aprovada nao muda); no Adormecer a cabeca
# sobe um pouco e a pata esquerda passa 0,8 mais por fora ao recolher. Resultado: Adormecer 225 -> 11, Despertar
# 264 -> 12 (= o contato da pose de dormir, cabeca encostada na pata).
def adormecer5(t):
    p = adormecer(t); g = _jan5(t, 1.1, 1.7, 2.4)
    somar_ossos(p["ossos"], {"Pescoco1": {"Z": 18 * g, "X": -8 * g}, "Pescoco2": {"Z": 18 * g}})
    h = _jan5(t, 1.0, 1.55, 2.1); b, i_, d_ = p["pes"]["MaoE"]; p["pes"]["MaoE"] = (b + V((0.8 * h, 0, 0)), i_, d_)
    return p
def despertar5(t):
    p = despertar(t); g = _jan5(t, -0.01, 0.15, 1.0)
    somar_ossos(p["ossos"], {"Pescoco1": {"Z": 16 * g}, "Pescoco2": {"Z": 16 * g}})
    return p
CLIPES.update({
    "Repouso": (clipe_repouso5, REP_T, True, 0.0, {}),
    "Observar": (clipe_observar5, 4.5, False, 0.0, {"OlharEsquerda": 0.6, "OlharDireita": 2.4}),
    "Sentado": (clipe_sentado5, 8.0, True, 0.0, {}),
    "Uivo": (clipe_uivo5, 4.0, False, 0.0, {"UivoInicio": 0.78, "UivoFim": 3.2}),
    "Adormecer": (adormecer5, 2.4, False, 0.0, {"Dormindo": 2.4}),
    "Despertar": (despertar5, 3.0, False, 0.0, {"Alerta": 1.1}),
})
if os.environ.get("LOBO_SONDA5"): exec(open(os.environ["LOBO_SONDA5"], encoding="utf-8").read())   # medicao (so leitura), sai antes de gerar
