# DEMONSTRACAO (nao e a animacao final do jogador): cavaleiro de teste em caixas, proporcoes de R15 (~5,5 studs), subindo e
# descendo da Wyvern pelos dois lados e sentado nos clipes montados. Usa Wyvern_E7_clipes_L4.blend SEM alterar (nada e salvo
# no .blend; o manequim so existe na execucao). Sela, lado oficial de entrada e regras de montaria NAO sao definidos aqui.
#   assento: preso ao osso da sela (spine_02); posicao (atras das asas), altura sobre a pele (0,6-0,9: espaco de uma
#            futura sela) e abertura das coxas escolhidas pela maior folga do manequim sentado no RideIdle
#   Montar_E / Montar_D (com o clipe Mount): em pe ao lado do flanco -> agacha -> salta ate o assento com a Wyvern agachada
#            -> fica preso ao osso enquanto ela levanta
#   Desmontar_E / Desmontar_D (com o Dismount): preso ao osso -> salta para o lado -> aterrissa agachado -> em pe
#   Sentado: RideIdle, RideWalk, RideRun, RideVirarEsquerda, RideVirarDireita
# Folga (stud) = distancia de pontos das caixas a pele, negativa se o ponto esta DENTRO (voto de 6 raios); asas (membrana fina) por distancia
# sem sinal. Separada em CORPO (tronco, cabeca, coxas, canelas) e APOIO (maos e pes, que podem tocar).
# Uso: blender -b Wyvern_E7_clipes_L4.blend -P 17_demo_cavaleiro.py -- <saida_dir> <medir|render> [vistas] [passo]
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix, Quaternion as Q, Euler
from mathutils.bvhtree import BVHTree
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]; MODO = argv[1]; VISTAS_ = argv[2].split(",") if len(argv) > 2 else ["lado", "tres4", "frente"]
PASSO = float(argv[3]) if len(argv) > 3 else 1.6
os.makedirs(OUT, exist_ok=True)
scn = bpy.context.scene; FPS = scn.render.fps
arm = bpy.data.objects["Wyvern_Rig"]; mesh = bpy.data.objects["Wyvern"]; key = mesh.data.shape_keys
R = math.radians
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def usar(nome):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        if ob.animation_data is None: ob.animation_data_create()
        ob.animation_data.action = a; ob.animation_data.action_slot = [s for s in a.slots if s.target_id_type == tipo][0]
    return a
def ir(nome, t):
    usar(nome); f = t * FPS; scn.frame_set(int(f), subframe=f - int(f)); bpy.context.view_layer.update()
def osso_mundo(b): return arm.matrix_world @ arm.pose.bones[b].matrix
# ---------------------------------------------------------------- malha da Wyvern: BVH e faces de asa
GR = {g.index: g.name for g in mesh.vertex_groups}
DOM = [GR[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "?" for v in mesh.data.vertices]
EH_ASA = lambda o: any(k in o for k in ("shoulder", "upperarm", "forearm", "hand", "finger", "strut", "thumb"))
mesh.data.calc_loop_triangles(); TRI = [tuple(t.vertices) for t in mesh.data.loop_triangles]
from collections import Counter
TRI_ASA = [EH_ASA(Counter(DOM[i] for i in t).most_common(1)[0][0]) for t in TRI]
def bvhs():
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data; P = [mesh.matrix_world @ v.co for v in ev.vertices]
    corpo = [t for t, a in zip(TRI, TRI_ASA) if not a]; asa = [t for t, a in zip(TRI, TRI_ASA) if a]
    return BVHTree.FromPolygons(P, corpo, all_triangles=True), BVHTree.FromPolygons(P, asa, all_triangles=True)
# ---------------------------------------------------------------- manequim (FK simples; frente = -Y, cima = +Z, esquerda = +X)
E = 0.9                                                              # escala para ~5,5 studs de altura
SEG = {  # nome: (tamanho x, y, z)
    "Cabeca": (1.2, 1.2, 1.2), "TroncoSup": (2.0, 1.0, 1.6), "TroncoInf": (2.0, 1.0, 0.5),
    "BracoSup_E": (0.8, 0.8, 1.2), "BracoInf_E": (0.7, 0.7, 1.1), "Mao_E": (0.7, 0.7, 0.45),
    "BracoSup_D": (0.8, 0.8, 1.2), "BracoInf_D": (0.7, 0.7, 1.1), "Mao_D": (0.7, 0.7, 0.45),
    "Coxa_E": (0.9, 0.9, 1.35), "Canela_E": (0.85, 0.85, 1.25), "Pe_E": (0.85, 1.1, 0.4),
    "Coxa_D": (0.9, 0.9, 1.35), "Canela_D": (0.85, 0.85, 1.25), "Pe_D": (0.85, 1.1, 0.4)}
SEG = {k: tuple(x * E for x in v) for k, v in SEG.items()}
APOIO = {"Mao_E", "Mao_D", "Pe_E", "Pe_D"}
def Rx(a): return Matrix.Rotation(a, 4, "X")
def Ry(a): return Matrix.Rotation(a, 4, "Y")
def Rz(a): return Matrix.Rotation(a, 4, "Z")
def T(x, y, z): return Matrix.Translation(V((x, y, z)))
# pose = angulos em graus: tronco (inclina a frente), quadril flex (perna a frente), abd (perna para fora), joelho,
# ombro flex (braco a frente), ombro abd, cotovelo; R+ = sentido positivo como descrito
POSES = {
    "EmPe":     {"tronco": 0, "qflex": 0, "abd": 4, "joelho": 0, "oflex": 5, "oabd": 6, "cot": 10},
    "Agachado": {"tronco": 30, "qflex": 75, "abd": 10, "joelho": 115, "oflex": 35, "oabd": 10, "cot": 30},
    "Salto":    {"tronco": 20, "qflex": 85, "abd": 25, "joelho": 110, "oflex": 70, "oabd": 20, "cot": 40},
    "Montado":  {"tronco": 12, "qflex": 80, "abd": 40, "joelho": 75, "oflex": 45, "oabd": 12, "cot": 55}}
def misturar_pose(a, b, w): return {k: a.get(k, 0) * (1 - w) + b.get(k, 0) * w for k in set(a) | set(b)}
def partes(pose, W):
    """matrizes de mundo de cada caixa; W = matriz de mundo da pelve (centro do quadril)"""
    s = SEG; out = {}
    tron = W @ Ry(R(pose.get("rolar", 0))) @ Rx(R(pose["tronco"]))     # + inclina a frente (-Y); rolar + = para a esquerda (+X)
    out["TroncoInf"] = tron @ T(0, 0, s["TroncoInf"][2] / 2)
    sup = tron @ T(0, 0, s["TroncoInf"][2]); out["TroncoSup"] = sup @ T(0, 0, s["TroncoSup"][2] / 2)
    pesc = sup @ T(0, 0, s["TroncoSup"][2]) @ Rx(-R(pose.get("cabeca", 0))) @ Ry(-R(pose.get("cab_rolar", 0)))   # cabeca ergue (+) e rola
    out["Cabeca"] = pesc @ T(0, 0, s["Cabeca"][2] / 2 + 0.05)
    for lado, sx in (("E", 1), ("D", -1)):
        omb = sup @ T(sx * (s["TroncoSup"][0] / 2 + s["BracoSup_E"][0] / 2), 0, s["TroncoSup"][2] - 0.15)
        omb = omb @ Rx(-R(pose["oflex"])) @ Ry(-sx * R(pose["oabd"]))   # braco a frente e para fora
        out["BracoSup_" + lado] = omb @ T(0, 0, -s["BracoSup_E"][2] / 2)
        cot = omb @ T(0, 0, -s["BracoSup_E"][2]) @ Rx(-R(pose["cot"]))
        out["BracoInf_" + lado] = cot @ T(0, 0, -s["BracoInf_E"][2] / 2)
        out["Mao_" + lado] = cot @ T(0, 0, -s["BracoInf_E"][2] - s["Mao_E"][2] / 2)
        qua = W @ T(sx * 0.5 * E, 0, 0) @ Rx(-R(pose["qflex"])) @ Ry(-sx * R(pose["abd"]))
        out["Coxa_" + lado] = qua @ T(0, 0, -s["Coxa_E"][2] / 2)
        joe = qua @ T(0, 0, -s["Coxa_E"][2]) @ Rx(R(pose["joelho"]))     # canela para tras
        out["Canela_" + lado] = joe @ T(0, 0, -s["Canela_E"][2] / 2)
        tor = joe @ T(0, 0, -s["Canela_E"][2]) @ Rx(-R(pose["joelho"] - pose["qflex"]))   # pe nivelado com o chao/sela
        out["Pe_" + lado] = tor @ T(0, -0.2 * E, -s["Pe_E"][2] / 2)
    return out
def altura_pelve(pose):
    """altura da pelve acima da sola, em pe nessa pose (pes no chao)"""
    o = partes(pose, Matrix.Identity(4)); sola = min((o["Pe_E"] @ V((0, 0, -SEG["Pe_E"][2] / 2))).z, (o["Pe_D"] @ V((0, 0, -SEG["Pe_D"][2] / 2))).z)
    return -sola
def amostras(nome, M):
    sx, sy, sz = SEG[nome]; pts = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for k in (-1, 0, 1):
                if (i, j, k) != (0, 0, 0): pts.append(M @ V((i * sx / 2, j * sy / 2, k * sz / 2)))
    return pts
DIR6 = [V((1, 0, 0)), V((-1, 0, 0)), V((0, 1, 0)), V((0, -1, 0)), V((0, 0, 1)), V((0, 0, -1))]
def dentro(bvh, p):
    """dentro do corpo se a maioria dos 6 raios sai pela face (1o impacto com a normal no mesmo sentido do raio)"""
    v = 0
    for d in DIR6:
        loc, n, _, _ = bvh.ray_cast(p, d)
        if loc is not None and n.dot(d) > 0: v += 1
    return v >= 4
def amostras_alca(nome, M):
    sx, sy, sz = ALCA[nome][1]
    return [M @ V((i * sx / 2, j * sy / 2, k * sz / 2)) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)]
def folga(P, bc, ba):
    """{'corpo': min, 'apoio': min, 'asa': min dist sem sinal, 'pior': (parte, valor)}"""
    r = {"corpo": 9e9, "apoio": 9e9, "asa": 9e9, "pior": None}
    for nome, M in P.items():
        g = "apoio" if nome in APOIO else "corpo"
        for p in amostras(nome, M):
            loc, n, _, d = bc.find_nearest(p)
            if loc is not None:
                sd = -d if dentro(bc, p) else d
                if sd < r[g]: r[g] = sd
                if g == "corpo" and (r["pior"] is None or sd < r["pior"][1]): r["pior"] = (nome, sd)
            loc, n, _, d = ba.find_nearest(p)
            if loc is not None and d < r["asa"]: r["asa"] = d
    return {k: (round(v, 3) if isinstance(v, float) else (v[0], round(v[1], 3)) if v else None) for k, v in r.items()}
# ---------------------------------------------------------------- assento: posicao ao longo do dorso e abertura das coxas
ir("RideIdle", 0.0); bc, ba = bvhs()
SELA = "spine_02"
def topo_dorso(y):
    loc, n, _, d = bc.ray_cast(V((0, y, 40)), V((0, 0, -1)))
    return loc
def assento_W(y, sobe=0.25):
    top = topo_dorso(y); return T(top.x, top.y, top.z + sobe)          # cavaleiro olhando -Y (mesma frente da Wyvern)
# busca: assento atras das asas (y -1..1,5), altura acima da pele 0,6-1,2 (espaco de uma futura sela), abertura das
# coxas 45-70 e dobra do joelho 55-115 (115 = estilo joquei); avaliada no RideIdle e em TODOS os quadros (passo 1,6) do
# RideWalk e do RideRun (o assento segue o
# osso da sela); nota = min(folga do corpo, folga das asas - 0,3) no pior quadro; empate -> assento baixo, coxas fechadas
AMOSTRAS_CAL = [("RideIdle", 0.0)] + [("RideWalk", k * 1.6 / FPS) for k in range(17)] + [("RideRun", k * 1.6 / FPS) for k in range(11)]
ESTADOS_CAL = []
for c_, t_ in AMOSTRAS_CAL:
    ir(c_, t_); b1, b2 = bvhs(); ESTADOS_CAL.append((osso_mundo("spine_02"), b1, b2))
ir("RideIdle", 0.0); bc, ba = bvhs(); W_SEL_IDLE = osso_mundo("spine_02")
melhor = None
for k in range(-4, 7):
    y = k * 0.25
    if topo_dorso(y) is None: continue
    for sobe in (0.6, 0.9, 1.2):
        off = W_SEL_IDLE.inverted() @ assento_W(y, sobe)
        for abd in range(45, 71, 5):
            for jo in (55, 75, 95, 115):
                POSES["Montado"]["abd"] = abd; POSES["Montado"]["joelho"] = jo; pior = 9e9; pa = 9e9
                for Wsel, b1, b2 in ESTADOS_CAL:
                    f = folga(partes(POSES["Montado"], Wsel @ off), b1, b2); pior = min(pior, f["corpo"]); pa = min(pa, f["asa"])
                    if min(pior, pa - 0.3) < (melhor[0][0] if melhor else -9e9): break
                nota = (round(min(pior, pa - 0.3), 2), -sobe, -abd)
                if melhor is None or nota > melhor[0]: melhor = (nota, y, sobe, abd, jo)
_, Y_ASSENTO, SOBE, ABD, JO = melhor
POSES["Montado"]["abd"] = ABD; POSES["Montado"]["joelho"] = JO
_assento_W = assento_W
def assento_W(y, sobe=None): return _assento_W(y, SOBE if sobe is None else sobe)
W_SEL0 = osso_mundo(SELA); W_ASSENTO = assento_W(Y_ASSENTO)
OFF = W_SEL0.inverted() @ W_ASSENTO                                  # assento no espaco do osso da sela
CAL = {"alca_provisoria": None, "erro_pegada_maos": None,
       "bracos_graus": None, "y_assento": Y_ASSENTO, "altura_sobre_pele": SOBE, "abertura_coxas_graus": POSES["Montado"]["abd"], "joelho_graus": JO,
       "nota_pior_quadro": melhor[0][0], "folga_RideIdle0": folga(partes(POSES["Montado"], W_ASSENTO), bc, ba),
       "assento_mundo_RideIdle0": [round(x, 2) for x in W_ASSENTO.translation]}
print("CAL", json.dumps(CAL), flush=True)
def W_sentado(): return osso_mundo(SELA) @ OFF
# ---------------------------------------------------------------- PEGADA NO DRAGAO (pedido do usuario, 09/11/2026; substitui a
# alca provisoria): o cavaleiro se debruca para a frente (meio deitado) e segura com as duas maos no dorso da Wyvern, a frente
# do assento. Alvos das maos: pontos da pele do dorso (raio de cima no RideIdle) a +-0,7 do eixo e a uma distancia a frente
# escolhida pela busca; mao 0,25 acima da pele (meia espessura da mao). Os alvos ficam no espaco do assento (osso da sela).
ALCA = {}
def alca(W): return {}
ir("RideIdle", 0.0); bc, ba = bvhs()
def alvos_mao(yl):
    out = {}
    for m, x in (("Mao_E", 0.7), ("Mao_D", -0.7)):
        q = W_ASSENTO @ V((x, yl, 0)); loc, n, _, _ = bc.ray_cast(V((q.x, q.y, q.z + 6)), V((0, 0, -1)))
        if loc is None: return None
        if n.z < 0: n = -n
        out[m] = W_ASSENTO.inverted() @ (loc + n * 0.25)
    return out
cands = []
for tr in range(30, 75, 5):                                          # inclinacao do tronco a frente
    melhor_t = None
    for yl in (-2.2, -2.6, -3.0, -3.4, -3.8):
        A = alvos_mao(yl)
        if A is None: continue
        for of in range(30, 125, 5):
            for oa in range(-30, 35, 5):
                for co in range(0, 65, 5):
                    pz = dict(POSES["Montado"], tronco=tr, oflex=of, oabd=oa, cot=co); P_ = partes(pz, Matrix.Identity(4))
                    e = max((P_[m].translation - A[m]).length for m in A)
                    if melhor_t is None or e < melhor_t[0]: melhor_t = (e, tr, of, oa, co, yl)
    pz = dict(POSES["Montado"], tronco=melhor_t[1], oflex=melhor_t[2], oabd=melhor_t[3], cot=melhor_t[4])
    Pm_ = {k: v for k, v in partes(pz, W_ASSENTO).items() if k not in APOIO}
    f = folga(Pm_, bc, ba); cands.append((melhor_t, f["corpo"], f["pior"]))
    print("CAND_PEGA tronco", tr, "erro_mao", round(melhor_t[0], 3), "y_alvo", melhor_t[5], "folga_corpo", f["corpo"], f["pior"], flush=True)
# escolha: o tronco mais deitado com o corpo do cavaleiro >= 0,08 fora da pele e erro da mao <= 0,12
ok = [c for c in cands if c[1] >= 0.08 and c[0][0] <= 0.12] or sorted(cands, key=lambda c: (c[0][0] > 0.12, -c[1]))[:1]
esc = max(ok, key=lambda c: c[0][1])
_, POSES["Montado"]["tronco"], POSES["Montado"]["oflex"], POSES["Montado"]["oabd"], POSES["Montado"]["cot"], Y_PEGA = esc[0]
ALVOS_MAO = alvos_mao(Y_PEGA)
# os pontos de pegada acompanham a PELE: guarda o triangulo da pele sob cada mao e as coordenadas baricentricas do ponto
# (no RideIdle); a cada quadro a mao mira o mesmo ponto da malha deformada, 0,25 acima dela na normal do triangulo
from mathutils.geometry import barycentric_transform
TRI_CORPO = [t for t, a in zip(TRI, TRI_ASA) if not a]
PELE_MAO = {}
_ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data; _P0 = [mesh.matrix_world @ v.co for v in _ev.vertices]
for m, a_ in ALVOS_MAO.items():
    pw = W_ASSENTO @ a_; loc, n, fi, _ = bc.find_nearest(pw); PELE_MAO[m] = (TRI_CORPO[fi], loc.copy(), [_P0[i].copy() for i in TRI_CORPO[fi]])
def pontos_pele():
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data; out = {}
    for m, (tri, loc0, v0) in PELE_MAO.items():
        v1 = [mesh.matrix_world @ ev.vertices[i].co for i in tri]
        p = barycentric_transform(loc0, v0[0], v0[1], v0[2], v1[0], v1[1], v1[2])
        n = (v1[1] - v1[0]).cross(v1[2] - v1[0]).normalized()
        if n.z < 0: n = -n
        out[m] = p + n * 0.25
    return out
BASE_BRACO = {k: POSES["Montado"][k] for k in ("oflex", "oabd", "cot")}
ERRO_POR_QUADRO = []
def pose_montada(base=None):
    """bracos reajustados em duas etapas (grossa +-30, fina +-4; tronco +-3) ate as maos chegarem aos pontos de pegada que
    acompanham a pele; tronco/rolagem/cabeca vem da pose base (fisica)"""
    base = base or POSES["Montado"]
    Ws = W_sentado(); alvo = {m: Ws.inverted() @ q for m, q in pontos_pele().items()}
    def erro(pz):
        P_ = partes(pz, Matrix.Identity(4)); return max((P_[m].translation - alvo[m]).length for m in alvo)
    melhor_ = None
    for dt in (-3, 0, 3):
        for d1 in range(-30, 31, 6):
            for d2 in range(-20, 21, 10):
                for d3 in range(-30, 31, 6):
                    pz = dict(base, tronco=base["tronco"] + dt, oflex=BASE_BRACO["oflex"] + d1,
                              oabd=BASE_BRACO["oabd"] + d2, cot=max(0, BASE_BRACO["cot"] + d3))
                    e = erro(pz)
                    if melhor_ is None or e < melhor_[0]: melhor_ = (e, pz)
    b0 = melhor_[1]
    for d1 in range(-4, 5, 1):
        for d2 in range(-5, 6, 5):
            for d3 in range(-4, 5, 1):
                pz = dict(b0, oflex=b0["oflex"] + d1, oabd=b0["oabd"] + d2, cot=max(0, b0["cot"] + d3))
                e = erro(pz)
                if e < melhor_[0]: melhor_ = (e, pz)
    ERRO_POR_QUADRO.append(melhor_[0])
    return melhor_[1]
ERRO_PEGA = round(esc[0][0], 3)
CAB_BASE = POSES["Montado"]["tronco"] - 8                            # cabeca erguida: olha a frente (8 graus abaixo do horizonte)
POSES["Montado"]["cabeca"] = CAB_BASE
CAL["erro_pegada_maos"] = ERRO_PEGA
CAL["pegada_no_dragao"] = {"y_alvo_local": Y_PEGA, "x_maos": 0.7, "mao_acima_da_pele": 0.25}
CAL["alca_provisoria"] = "removida (09/11): pegada no dorso"
CAL["bracos_graus"] = {k: POSES["Montado"][k] for k in ("tronco", "oflex", "oabd", "cot")}
CAL["pegada_no_dragao"]["acompanha"] = "triangulo da pele sob cada mao (baricentrico)"
print("PEGADA", json.dumps({"erro": ERRO_PEGA, "y_alvo": Y_PEGA, **CAL["bracos_graus"]}), flush=True)
# ---------------------------------------------------------------- sequencias
LARG = 4.6                                                           # distancia lateral do flanco onde o cavaleiro espera
def pe_lado(sx):
    """pelve em pe ao lado do flanco, olhando para a Wyvern (+X do lado E olha para -X)"""
    yaw = R(-90) if sx > 0 else R(90)                                 # -Y girado para -X (lado E) / +X (lado D)
    return T(sx * LARG, Y_ASSENTO + 0.3, altura_pelve(POSES["EmPe"])) @ Rz(yaw), yaw
def interp_W(A, B, w, ctrl=None):
    """posicao em curva de Bezier quadratica (ctrl = ponto de controle acima do flanco); rotacao por slerp"""
    la, ra, _ = A.decompose(); lb, rb, _ = B.decompose()
    if ra.dot(rb) < 0: rb = -rb
    l = la.lerp(lb, w) if ctrl is None else la * (1 - w) ** 2 + ctrl * 2 * (1 - w) * w + lb * w * w
    return Matrix.LocRotScale(l, ra.slerp(rb, w), None)
def ctrl_flanco(sx, W_assento):
    """acima do flanco do lado de subida: 1,8 para fora do assento e 3 acima dele"""
    p = W_assento.translation; return V((p.x + sx * 1.8, p.y, p.z + 3.0))
# ---------------------------------------------------------------- FISICA do cavaleiro preso ao assento (pedido do usuario)
# Aceleracao linear do assento (2a diferenca da posicao, no espaco do assento) e oscilacao da sua inclinacao/rolagem:
#   - para cima (+Z) comprime: o tronco cai a frente; arranque a frente (-Y) joga o tronco para tras; puxao lateral (X)
#     rola o tronco para fora; tudo por mola amortecida (2,2 Hz, amortecimento 0,4) -> atraso e assentamento naturais
#   - a cabeca estabiliza o olhar: compensa a inclinacao/rolagem do assento e do tronco (80%), mantendo o rosto a frente
FIS = {"freq_hz": 2.2, "amort": 0.45, "g_vert": 0.15, "g_frente": 0.15, "g_lado": 0.14, "lim_tronco": 10.0, "lim_rolar": 6.0, "estab_cabeca": 0.8}
def angulos_assento(Ws):
    fr = Ws.to_3x3() @ V((0, -1, 0)); lt = Ws.to_3x3() @ V((1, 0, 0))
    return math.degrees(math.asin(max(-1, min(1, fr.z)))), math.degrees(math.asin(max(-1, min(1, lt.z))))   # nariz acima +, esquerda acima +
def fisica(Ws_list, dt, loop, impulso=0.0):
    n = len(Ws_list); P = [W.translation.copy() for W in Ws_list]; Rm = [W.to_3x3() for W in Ws_list]
    def acc(i):
        if loop: a_ = (P[(i + 1) % n] - 2 * P[i] + P[(i - 1) % n]) / dt ** 2
        else:
            j = min(max(i, 1), n - 2); a_ = (P[j + 1] - 2 * P[j] + P[j - 1]) / dt ** 2
        return Rm[i].transposed() @ a_
    alvo = []
    for i in range(n):
        a_ = acc(i)
        alvo.append((max(-FIS["lim_tronco"], min(FIS["lim_tronco"], FIS["g_vert"] * a_.z + FIS["g_frente"] * a_.y)),
                     max(-FIS["lim_rolar"], min(FIS["lim_rolar"], -FIS["g_lado"] * a_.x))))
    w = 2 * math.pi * FIS["freq_hz"]; z = FIS["amort"]; sub = 20; h = dt / sub
    x = [0.0, 0.0]; v = [impulso, 0.0]; saida = []
    for vt in range(3 if loop else 1):
        cur = []
        for i in range(n):
            for _ in range(sub):
                for k in (0, 1):
                    ak = w * w * (alvo[i][k] - x[k]) - 2 * z * w * v[k]; v[k] += ak * h; x[k] += v[k] * h
            cur.append((x[0], x[1]))
        saida = cur
    if loop: saida[-1] = saida[0]
    ang = [angulos_assento(W) for W in Ws_list]
    mp = sum(a[0] for a in ang) / n; mr = sum(a[1] for a in ang) / n
    out = []
    for (dtr, drol), (ap, ar) in zip(saida, ang):
        # nariz do assento acima (ap > media) inclina tudo para cima: a cabeca abaixa o mesmo tanto (estabiliza)
        out.append({"tronco": POSES["Montado"]["tronco"] + dtr, "rolar": drol,
                    "cabeca": CAB_BASE + dtr - FIS["estab_cabeca"] * (ap - mp),
                    "cab_rolar": -FIS["estab_cabeca"] * (drol + (ar - mr))})
    return out, [round(max(abs(o[0]) for o in saida), 2), round(max(abs(o[1]) for o in saida), 2)]
AMPLITUDES = {}
def montar_seq(clipe, ts, livre, loop, nome, impulso=0.0):
    """livre(t) -> (pose, W) quando o cavaleiro NAO esta preso; None quando esta montado (fisica + pegada)"""
    presos = [i for i, t in enumerate(ts) if livre(t) is None]; Ws = []
    for i in presos: ir(clipe, ts[i]); Ws.append(W_sentado())
    fis, amp = fisica(Ws, PASSO / FPS, loop, impulso) if presos else ([], [0, 0])
    AMPLITUDES[nome] = amp
    fmap = dict(zip(presos, fis)); quadros = []
    for i, t in enumerate(ts):
        ir(clipe, t); lv = livre(t)
        if lv is None: pose = pose_montada(dict(POSES["Montado"], **fmap[i])); W = W_sentado()
        else: pose, W = lv
        quadros.append((round(t, 3), {k: [list(r) for r in M] for k, M in partes(pose, W).items()}))
    return quadros
def tempos(dur): return [k * PASSO / FPS for k in range(int(dur / (PASSO / FPS) + 1e-6) + 1)]
def seq_montar(sx):
    W0, _ = pe_lado(sx); T_ATERR = 1.25
    ir("Mount", T_ATERR); Wfim = W_sentado()
    def livre(t):
        if t < 0.55: return POSES["EmPe"], W0
        if t < 0.8:
            w = suave((t - 0.55) / 0.25); pose = misturar_pose(POSES["EmPe"], POSES["Agachado"], w)
            return pose, W0 @ T(0, 0, -(altura_pelve(POSES["EmPe"]) - altura_pelve(pose)))
        if t < T_ATERR:
            w = (t - 0.8) / (T_ATERR - 0.8)
            pose = misturar_pose(POSES["Agachado"], POSES["Salto"], suave(w / 0.4)) if w < 0.4 else misturar_pose(POSES["Salto"], POSES["Montado"], suave((w - 0.4) / 0.6))
            Wa = W0 @ T(0, 0, -(altura_pelve(POSES["EmPe"]) - altura_pelve(POSES["Agachado"])))
            return pose, interp_W(Wa, Wfim, suave(w), ctrl_flanco(sx, Wfim))
        return None
    return montar_seq("Mount", tempos(2.4), livre, False, "Montar", impulso=60.0)   # impacto da aterrissagem: tronco cai a frente
def seq_desmontar(sx):
    W0, _ = pe_lado(sx); T_SAI, T_CHAO = 0.45, 0.95
    ir("Dismount", T_SAI); Wsai = W_sentado()
    Wag = W0 @ T(0, 0, -(altura_pelve(POSES["EmPe"]) - altura_pelve(POSES["Agachado"])))
    def livre(t):
        if t < T_SAI: return None
        if t < T_CHAO:
            w = (t - T_SAI) / (T_CHAO - T_SAI)
            pose = misturar_pose(POSES["Montado"], POSES["Salto"], suave(w / 0.5)) if w < 0.5 else misturar_pose(POSES["Salto"], POSES["Agachado"], suave((w - 0.5) / 0.5))
            return pose, interp_W(Wsai, Wag, suave(w), ctrl_flanco(sx, Wsai))
        if t < 1.5:
            w = suave((t - T_CHAO) / 0.55); pose = misturar_pose(POSES["Agachado"], POSES["EmPe"], w)
            return pose, W0 @ T(0, 0, -(altura_pelve(POSES["EmPe"]) - altura_pelve(pose)))
        return POSES["EmPe"], W0
    return montar_seq("Dismount", tempos(2.0), livre, False, "Desmontar")
def seq_sentado(clipe):
    a = bpy.data.actions[clipe]; dur = a.frame_range[1] / FPS
    return montar_seq(clipe, tempos(dur), lambda t: None, True, "Sentado_" + clipe)
SEQ = {"Montar_E": ("Mount", seq_montar(1)), "Montar_D": ("Mount", seq_montar(-1)),
       "Desmontar_E": ("Dismount", seq_desmontar(1)), "Desmontar_D": ("Dismount", seq_desmontar(-1))}
for c in ("RideIdle", "RideWalk", "RideRun", "RideVirarEsquerda", "RideVirarDireita"): SEQ["Sentado_" + c] = (c, seq_sentado(c))
if MODO == "medir":
    RES = {"_calibracao": CAL, "_nota": "demonstracao; manequim de caixas ~5,5 studs; nao e a animacao final do jogador"}
    for nome, (clipe, qs) in SEQ.items():
        piores = {"corpo": (9e9, None, None), "apoio": (9e9, None), "asa": (9e9, None)}; neg = 0
        for t, P in qs:
            ir(clipe, t); bc, ba = bvhs(); Pm = {k: Matrix(v) for k, v in P.items() if not k.startswith("Alca")}; f = folga(Pm, bc, ba)
            for k_ in [k for k in P if k.startswith("Alca")]:
                for p_ in amostras_alca(k_, Matrix(P[k_])):
                    loc_, n_, _, d_ = bc.find_nearest(p_)
                    if loc_ is not None:
                        sd_ = -d_ if dentro(bc, p_) else d_
                        if sd_ < piores.setdefault("alca", (9e9, None))[0]: piores["alca"] = (round(sd_, 3), t)
            for m_ in ("Mao_E", "Mao_D"):
                loc_, n_, _, d_ = bc.find_nearest(Pm[m_].translation)
                e_ = abs((-d_ if dentro(bc, Pm[m_].translation) else d_) - 0.25)   # quanto a mao se afasta da pegada na pele
                if t >= {"Montar_E": 1.25, "Montar_D": 1.25}.get(nome, 0) and (nome.startswith("Sentado") or nome.startswith("Montar") or t < 0.45):
                    piores["pega"] = max(piores.get("pega", 0), round(e_, 3))
            if f["corpo"] < piores["corpo"][0]: piores["corpo"] = (f["corpo"], t, f["pior"])
            if f["apoio"] < piores["apoio"][0]: piores["apoio"] = (f["apoio"], t)
            if f["asa"] < piores["asa"][0]: piores["asa"] = (f["asa"], t)
            if f["corpo"] < -0.05: neg += 1
        RES[nome] = {"clipe_wyvern": clipe, "quadros": len(qs), "corpo_min": piores["corpo"], "apoio_min": piores["apoio"],
                     "asa_dist_min": piores["asa"], "quadros_corpo_abaixo_-0.05": neg,
                     "mao_desvio_max_da_pele_quando_segura": piores.get("pega")}
        print("FOLGA", nome, json.dumps(RES[nome]), flush=True)
    RES["_calibracao"]["erro_ik_maos_max_montado"] = round(max(ERRO_POR_QUADRO), 3)
    RES["_calibracao"]["fisica"] = FIS; RES["_calibracao"]["fisica_amplitude_graus_tronco_rolar"] = AMPLITUDES
    print("FISICA", json.dumps(AMPLITUDES), flush=True)
    print("ERRO_IK_MAOS_MAX", round(max(ERRO_POR_QUADRO), 3), flush=True)
    json.dump(RES, open(os.path.join(OUT, "folgas_cavaleiro.json"), "w"), indent=1)
    json.dump({n: {"clipe": c, "quadros": qs} for n, (c, qs) in SEQ.items()}, open(os.path.join(OUT, "trajetorias_cavaleiro.json"), "w"))
    print("OK"); raise SystemExit
# ---------------------------------------------------------------- render (mesma cena dos lotes: camera fixa, humano de escala)
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 640
scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0)); m = bpy.data.materials.new("chao"); m.diffuse_color = (0.42, 0.45, 0.38, 1); bpy.context.object.data.materials.append(m)
def mat(nome, cor):
    m_ = bpy.data.materials.new(nome); m_.use_nodes = True; m_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = cor; return m_
mc = mat("cav", (0.1, 0.3, 0.9, 1)); mp = mat("apoio", (0.95, 0.6, 0.1, 1))
CX = {}
ma = mat("alca", (0.3, 0.17, 0.08, 1))
for nome, (_, (sx, sy, sz)) in ALCA.items():
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = "DEMO_" + nome
    o.data.transform(Matrix.Diagonal((sx, sy, sz, 1))); o.data.materials.append(ma); CX[nome] = o
for nome, (sx, sy, sz) in SEG.items():
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = "DEMO_" + nome
    o.data.transform(Matrix.Diagonal((sx, sy, sz, 1))); o.data.materials.append(mp if nome in APOIO else mc); CX[nome] = o
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); scn.collection.objects.link(cam); scn.camera = cam
cd.type = "ORTHO"; cd.clip_end = 1000
tc = bpy.data.curves.new("rot", "FONT"); rot = bpy.data.objects.new("rot", tc); scn.collection.objects.link(rot)
mt = bpy.data.materials.new("rot"); mt.use_nodes = True; bt = mt.node_tree.nodes["Principled BSDF"]
bt.inputs["Base Color"].default_value = (1, 1, 0.6, 1); bt.inputs["Emission Color"].default_value = (1, 1, 0.6, 1); bt.inputs["Emission Strength"].default_value = 3
tc.materials.append(mt); rot.parent = cam
VIST = {"close": (V((0.75, -0.55, 0.45)), None, 7), "lado": (V((1, 0, 0.05)), V((0, 1, 8)), 26), "frente": (V((0, -1, 0.15)), V((0, 0, 8)), 26), "tres4": (V((0.8, -0.7, 0.45)), V((1, 1, 8)), 26),
        "tras": (V((0.1, 1, 0.3)), V((0, 2, 8)), 26)}
SO = argv[4].split(",") if len(argv) > 4 else list(SEQ)
for nome in SO:
    clipe, qs = SEQ[nome]
    for k, (t, P) in enumerate(qs):
        ir(clipe, t)
        for p, M in P.items(): CX[p].matrix_world = Matrix(M)
        for v in VISTAS_:
            d, c, esc = VIST[v]; d = d.normalized(); cd.ortho_scale = esc
            if c is None: c = Matrix(P["TroncoInf"]).translation + V((0, -0.8, 0.6))   # close: acompanha o cavaleiro
            cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
            tc.body = f"DEMO cavaleiro | {nome} ({clipe} t{t:.2f}s) | {v}"; tc.size = esc * 0.03; rot.location = (-esc / 2 * 0.96, esc * 0.667 / 2 * 0.9, -10)
            scn.render.filepath = os.path.join(OUT, f"{nome}_{v}_{k:03d}.png"); bpy.ops.render.render(write_still=True)
    print("SEQ", nome, len(qs), flush=True)
print("OK")
