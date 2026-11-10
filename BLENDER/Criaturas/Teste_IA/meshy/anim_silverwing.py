"""Animacoes PROPRIAS do Silverwing ("Dragao Glacial", TESTE) — substituem as do molde Mesh2Motion.
Causas corrigidas (diag_anatomia.py): pes dianteiros convergiam para a linha media (+-3,5 cm vs ombros +-6,8 cm);
pes traseiros suspensos 7-11 cm (perna curta p/ a altura do quadril do molde); base da cauda dobrava 20 graus no
Idle/Walk do molde; no voo as pernas pendiam esticadas e juntas.
Como: pose calculada osso a osso (FK) sobre o REPOUSO atual (malha/esqueleto intactos); patas por IK de 2 ossos +
metacarpo/metatarso + dedos com o chao (z=0) travado; cauda segmentada com atraso e apoio no chao; asas amostradas das
acoes validadas (dobra propria, Fly_Flap, Fly_Glide) e misturadas por slerp.
Eixos: frente = -Y, cima = +Z, esquerda do dragao = +X (sufixo _l). Unidades do GLB (modelo no Roblox: escala 17,5).
Uso: blender -b Silverwing_M2M.blend -P anim_silverwing.py -- [clipes,separados|todos] """
import bpy, sys, math
from mathutils import Vector, Matrix, Quaternion
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PEDIDOS = None if not args or args[0] == "todos" else set(args[0].split(","))
FPS = 30
import os
NECK_BASE = float(os.environ.get("NECK_BASE", "1"))      # pescoco ja erguido no repouso (modelo neutro): 0
PESC_VOO = float(os.environ.get("PESC_VOO", "0"))        # graus para deitar o pescoco no voo (negativo = baixa)
PERNA_VOO_REL = os.environ.get("PERNA_VOO_REL") == "1"  # patas de voo a partir da pose do proprio modelo
ANG_QUADRIL_VOO = float(os.environ.get("ANG_QUADRIL_VOO", "30"))  # giro da perna inteira no quadril/ombro em voo (graus)
# AMPLITUDE DO CORPO (referencia: video do usuario jogando Dragon Adventures, quadros a cada 0,125 s): o corpo inteiro
# sobe/desce e arfa a cada batida, o pescoco reage com atraso, patas balancam como pendulo, cauda chicoteia. Com os
# valores antigos (~0,3 stud / 2 graus) o dragao parecia ESTATICO no jogo. 0 = clipes antigos.
PENDULO = float(os.environ.get("PENDULO", "1"))
# AMP: multiplica corpo/cabeca/patas (o usuario, jogando, via so asas e cauda se mexendo: medido no cliente, cabeca
# ~0,8 stud e tronco +-2 graus = parado na escala do dragao). AC = versao no chao (passos nao podem patinar).
AMP = float(os.environ.get("AMP", "2.5")); AC = 1 + (AMP - 1) * 0.55
# ENCOLHE: fracao da distancia ombro/quadril -> punho/tornozelo nas patas de voo (1 = pendurada reta)
ENCOLHE = float(os.environ.get("ENCOLHE", "0.62")); ENCOLHE_EXTRA = {"v": 1.0}
# giro das patas no voo (graus, para TRAS): traseiras / dianteiras; 0 = usa ANG_QUADRIL_VOO nas duas
ANG_VOO_TRAS = float(os.environ.get("ANG_VOO_TRAS", "0")); ANG_VOO_FRENTE = float(os.environ.get("ANG_VOO_FRENTE", "0"))
ENCOLHE_FRENTE = float(os.environ.get("ENCOLHE_FRENTE", str(ENCOLHE)))   # dianteiras: menos encolhidas, deitadas para tras
PLANEIO_ABAIXA = float(os.environ.get("PLANEIO_ABAIXA", "0"))   # graus: baixa as pontas das asas no planeio
# fator da queda da base da cauda (1 = Silverwing). Caudas que ja descem no repouso (CR_Dragao) usam ~0: senao a
# cauda encosta no chao e o apoio a dobra para cima em gancho
CAUDA_BASE_K = float(os.environ.get("CAUDA_BASE_K", "1"))
# PASSO_PESADO=1 (CR_Dragao, usuario 31/10, referencia "quadrupede pesado"): tronco inclinado a frente, dianteira sobe
# mais com os dedos curvados, quique quase zero trocado por ABSORCAO nos ombros quando a dianteira pisa e IMPULSO do
# quadril quando a traseira empurra. Passada, apoio e ciclo nao mudam (velocidades calibradas da montaria/IA).
PASSO_PESADO = os.environ.get("PASSO_PESADO") == "1"
# PERSONALIDADE (sistema universal 01/11): batidas por clipe no voo e no pairar. Glacial = menos batidas, mais amplas e
# cadenciadas (o controlador da montaria segue com as mesmas velocidades: so a cadencia da asa muda)
NB_VOO = int(os.environ.get("NB_VOO", "4")); NB_PAIRAR = int(os.environ.get("NB_PAIRAR", "4"))
# CERTIFICACAO (02/11, Glacial): batida PROFUNDA e com golpe forte. AMP_ASA amplia o giro do ombro/umero/antebraco em
# torno da pose media do Fly_Flap (1 = fonte intacta); ASA_GOLPE (0..0,5) acelera a descida da asa e alonga a subida no
# MESMO periodo (laco e reacoes do corpo continuam casados: ponta() usa a mesma fase). T_VOO/T_PAIRAR = duracao dos
# clipes (cadencia = duracao / batidas). AG_DEITADO = agachamento do deitado/dormindo (barriga no chao). Sem as
# variaveis tudo fica como antes (CR/Silverwing inalterados).
AMP_ASA = float(os.environ.get("AMP_ASA", "1")); ASA_GOLPE = float(os.environ.get("ASA_GOLPE", "0"))
T_VOO = float(os.environ.get("T_VOO", "3.2")); T_PAIRAR = float(os.environ.get("T_PAIRAR", "4.0"))
AG_DEITADO = float(os.environ.get("AG_DEITADO", "0.09"))
sc = bpy.context.scene; sc.render.fps = FPS
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for m in M.modifiers: m.show_viewport = False

# ---------------------------------------------------------------- esqueleto
REST = {b.name: b.matrix_local.copy() for b in A.data.bones}
PAI = {b.name: (b.parent.name if b.parent else None) for b in A.data.bones}
ORD = []
def _v(b):
    ORD.append(b.name)
    for c in b.children: _v(c)
for b in [b for b in A.data.bones if b.parent is None]: _v(b)
REL = {n: (REST[PAI[n]].inverted() @ REST[n]) if PAI[n] else REST[n].copy() for n in ORD}
def rot(m): return m.to_3x3().normalized()
def H(n): return REST[n].translation.copy()
def T(n): return A.data.bones[n].tail_local.copy()
# linha media e centro do corpo tirados do REPOUSO (servem para qualquer malha encaixada no esqueleto)
XM = REST["hips"].translation.x
C = (REST["hips"].translation + REST["spine_2"].translation) / 2 + Vector((0, 0, 0.03))
ASA = [n for n in ORD if n.startswith(("wing_", "shoulder_"))]
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
def Rax(eixo, graus): return Matrix.Rotation(math.radians(graus), 3, eixo)
def smooth(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, t): return a + (b - a) * t

# pernas: nomes e comprimentos
def perna(lado, tras):
    if tras:
        n = dict(J="back_leg_" + lado, E="back_ankle_" + lado, P="back_foot_" + lado, K="back_toes_" + lado, D="back_toes_tip_" + lado)
    else:
        n = dict(J="front_leg_" + lado, E="front_ankle_" + lado, P="front_foot_" + lado, K="front_toes_" + lado, D="front_toes_tip_" + lado)
    n["L1"] = (H(n["E"]) - H(n["J"])).length; n["L2"] = (H(n["P"]) - H(n["E"])).length
    n["L3"] = (H(n["K"]) - H(n["P"])).length; n["L4"] = (H(n["D"]) - H(n["K"])).length; n["L5"] = A.data.bones[n["D"]].length
    n["s"] = 1 if lado == "l" else -1; n["tras"] = tras
    return n
PERNAS = {"PD_E": perna("l", False), "PD_D": perna("r", False), "PT_E": perna("l", True), "PT_D": perna("r", True)}
CAUDA = ["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"]
PESCOCO = ["spine_2", "spine_3", "spine_4"]

# ---------------------------------------------------------------- fontes de asas (acoes validadas)
CACHE = {}
def fonte(nome):
    if nome in CACHE: return CACHE[nome]
    ant = A.animation_data.action if A.animation_data else None
    act = bpy.data.actions[nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); quadros = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); quadros.append({n: A.pose.bones[n].matrix_basis.copy() for n in ASA})
    A.animation_data.action = ant                 # restaura a acao sendo gravada
    if nome == "Silverwing_Fly_Flap" and AMP_ASA != 1.0: _ampliar_batida(quadros)
    CACHE[nome] = quadros; return quadros
def _ampliar_batida(quadros):
    """batida mais PROFUNDA: o giro de cada osso em torno da sua pose media no ciclo e multiplicado (ombro e umero
    inteiro, antebraco 60%, dedos/membrana intactos = a membrana acompanha sem torcer)"""
    for b in ASA:
        k = AMP_ASA if b.startswith(("shoulder_", "wing_1_")) else (1 + (AMP_ASA - 1) * 0.6 if b.startswith("wing_2_") else 1.0)
        if k == 1.0: continue
        qs = [f[b].to_quaternion() for f in quadros]; s = Quaternion((0, 0, 0, 0))
        for q in qs: s = s + (q if q.dot(qs[0]) >= 0 else -q)
        med = s.normalized()
        for f, q in zip(quadros, qs):
            d = med.rotation_difference(q); eixo, ang = d.to_axis_angle()
            if ang > math.pi: ang -= 2 * math.pi
            f[b] = Matrix.Translation(f[b].translation) @ (med @ Quaternion(eixo, ang * k)).to_matrix().to_4x4()
_XC = {"v": None}
def _fase(u):
    """tempo do clipe -> fase da fonte Fly_Flap (ASA_GOLPE: descida mais rapida, subida mais lenta; g(0)=0, g(1)=1)"""
    if ASA_GOLPE == 0: return u
    if _XC["v"] is None:
        n_ = len(PONTA) - 1; it = max(range(n_ + 1), key=lambda i: PONTA[i]) / n_; ib = min(range(n_ + 1), key=lambda i: PONTA[i]) / n_
        _XC["v"] = (it + ((ib - it) % 1.0) / 2) % 1.0                 # meio do golpe descendente (alto -> baixo)
    x = u % 1.0; xc = _XC["v"]; k = ASA_GOLPE / (2 * math.pi)
    return (u - x) + x + k * (math.sin(2 * math.pi * (x - xc)) - math.sin(-2 * math.pi * xc))
def asas(nome, u):
    """basis das asas na fase u (0..1, ciclo: ultimo quadro = primeiro)"""
    if nome == "Silverwing_Fly_Flap": u = _fase(u)
    q = fonte(nome); n = len(q) - 1; x = (u % 1.0) * n; i = int(x); t = x - i; j = min(i + 1, n)
    out = {}
    for b in ASA:
        a, c = q[i][b], q[j][b]
        out[b] = Matrix.Translation(a.translation.lerp(c.translation, t)) @ a.to_quaternion().slerp(c.to_quaternion(), t).to_matrix().to_4x4()
    return out
def mistura(a, b, t):
    return {n: Matrix.Translation(a[n].translation.lerp(b[n].translation, t)) @ a[n].to_quaternion().slerp(b[n].to_quaternion(), t).to_matrix().to_4x4() for n in a}

# DOBRA PROPRIA das asas no chao (asas 1,5x, 29/10): a dobra do molde (Idle) deixava o punho no chao ao lado do corpo e
# os dedos abertos para cima = "tenda" enorme com as asas maiores. Aqui, estilo morcego/wyvern: umero para tras e um
# pouco acima, antebraco dobrado para FRENTE (punho perto do ombro), dedos deitados para tras ao longo do flanco,
# quase paralelos (membrana recolhida em pregas), pontas acima do chao. Direcoes no corpo em repouso (frente = -Y,
# esquerda = +X, cima = +Z); o lado direito e o espelho em X. Substitui as amostras do "Silverwing_Idle" no CACHE:
# todos os clipes de chao e as misturas Idle<->Glide (abrir/fechar) usam a dobra nova.
DOBRA = os.environ.get("DOBRA_PROPRIA", "1") == "1"
DIR_DOBRA = {
    "wing_1": (0.35, 0.85, 0.30), "wing_2": (0.10, -0.97, -0.20),
    "wing_3": (0.02, 0.985, -0.12), "wing_4": (-0.03, 0.98, -0.14), "wing_5": (-0.06, 0.97, -0.16), "wing_tip": (-0.08, 0.96, -0.18),
    "wing_feather_5_0": (-0.02, 0.96, -0.24), "wing_feather_5_1": (-0.05, 0.95, -0.26), "wing_feather_5_tip": (-0.07, 0.94, -0.28),
    "wing_feather_4_0": (-0.03, 0.94, -0.30), "wing_feather_4_1": (-0.06, 0.93, -0.31), "wing_feather_4_tip": (-0.08, 0.92, -0.32),
    "wing_feather_3_0": (-0.03, 0.93, -0.31), "wing_feather_3_1": (-0.06, 0.92, -0.32), "wing_feather_3_tip": (-0.08, 0.91, -0.33),
    "wing_feather_2_0": (-0.02, 0.84, -0.48), "wing_feather_2_1": (-0.04, 0.86, -0.46), "wing_feather_2_tip": (-0.06, 0.87, -0.44),
    "wing_feather_1_0": (0.10, 0.75, 0.05), "wing_feather_1_1": (0.08, 0.80, 0.0), "wing_feather_1_tip": (0.06, 0.82, -0.05),
}
if os.environ.get("DOBRA_JSON"):                      # dobra propria de outro dragao (mesmo esqueleto, asas diferentes)
    import json
    DIR_DOBRA.update({k: tuple(v) for k, v in json.load(open(os.environ["DOBRA_JSON"], encoding="utf-8")).items()})
def _basis_dobra(resp=0.0, dirs=None):
    """basis (local) de cada osso de asa para a dobra; resp (-1..1) = pequena variacao (respiracao/ajuste)"""
    W = {}; out = {}; dirs = dirs or DIR_DOBRA
    for n in ORD:
        pai = PAI[n]; Mc = (W[pai] @ REL[n]) if pai else REL[n].copy()
        base = n[:-2] if n.endswith(("_l", "_r")) else n
        if n in ASA and base in dirs:
            d = Vector(dirs[base])
            if base == "wing_1": d = d + Vector((0, 0, 0.03 * resp))                 # cotovelo sobe/desce de leve
            if base.startswith("wing_feather"): d = d + Vector((-0.015 * resp, 0, 0))   # dedos encostam/afastam
            if n.endswith("_r"): d.x = -d.x
            y = rot(Mc) @ Y
            Md = Matrix.Translation(Mc.translation) @ (y.rotation_difference(d.normalized()).to_matrix() @ rot(Mc)).to_4x4()
        else:
            Md = Mc
        W[n] = Md
        if n in ASA: out[n] = Mc.inverted() @ Md
    return out
if DOBRA:
    CACHE["Silverwing_Idle"] = [_basis_dobra(math.sin(2 * math.pi * k / 30)) for k in range(31)]

# ASAS ARMADAS no chao (usuario 31/10: "nao quero ver as asas dobradas de novo"): no lugar da dobra, asas meio abertas
# e um pouco erguidas (referencia do dragao marrom andando): umero para fora/tras/cima, punho alto, dedos em leque para
# tras e para baixo, membrana aberta. ERGUIDA = asas acima do corpo (referencia do dragao verde sentado). Entre as duas,
# mistura das direcoes (ergue 0..1). Substitui o "Silverwing_Idle" do CACHE: todos os clipes de chao e as misturas com
# o voo passam a partir das asas armadas.
ASAS_ARMADAS = os.environ.get("ASAS_ARMADAS") == "1"
DIR_ARMADA = {
    "wing_1": (0.55, 0.35, 0.75), "wing_2": (0.45, -0.25, 0.85),
    "wing_3": (0.60, 0.10, 0.55), "wing_4": (0.70, 0.30, 0.10), "wing_5": (0.60, 0.50, -0.30), "wing_tip": (0.50, 0.60, -0.50),
    "wing_feather_5_0": (0.55, 0.55, -0.20), "wing_feather_5_1": (0.52, 0.58, -0.25), "wing_feather_5_tip": (0.50, 0.60, -0.30),
    "wing_feather_4_0": (0.40, 0.75, -0.40), "wing_feather_4_1": (0.38, 0.76, -0.42), "wing_feather_4_tip": (0.36, 0.77, -0.45),
    "wing_feather_3_0": (0.25, 0.85, -0.50), "wing_feather_3_1": (0.24, 0.85, -0.52), "wing_feather_3_tip": (0.22, 0.85, -0.54),
    "wing_feather_2_0": (0.15, 0.90, -0.45), "wing_feather_2_1": (0.14, 0.90, -0.46), "wing_feather_2_tip": (0.13, 0.90, -0.47),
    "wing_feather_1_0": (0.10, 0.97, -0.20), "wing_feather_1_1": (0.10, 0.97, -0.22), "wing_feather_1_tip": (0.10, 0.96, -0.24),
}
DIR_ERGUIDA = {
    "wing_1": (0.35, 0.35, 0.87), "wing_2": (0.25, -0.10, 0.96),
    "wing_3": (0.30, 0.35, 0.88), "wing_4": (0.30, 0.60, 0.60), "wing_5": (0.30, 0.80, 0.30), "wing_tip": (0.25, 0.90, 0.10),
    "wing_feather_5_0": (0.30, 0.85, 0.30), "wing_feather_5_1": (0.30, 0.86, 0.25), "wing_feather_5_tip": (0.30, 0.87, 0.20),
    "wing_feather_4_0": (0.30, 0.90, 0.00), "wing_feather_4_1": (0.30, 0.90, -0.05), "wing_feather_4_tip": (0.30, 0.90, -0.10),
    "wing_feather_3_0": (0.25, 0.90, -0.30), "wing_feather_3_1": (0.25, 0.90, -0.33), "wing_feather_3_tip": (0.24, 0.90, -0.36),
    "wing_feather_2_0": (0.20, 0.85, -0.50), "wing_feather_2_1": (0.20, 0.85, -0.52), "wing_feather_2_tip": (0.19, 0.85, -0.54),
    "wing_feather_1_0": (0.10, 0.90, -0.40), "wing_feather_1_1": (0.10, 0.90, -0.42), "wing_feather_1_tip": (0.10, 0.89, -0.44),
}
def _sub(raiz):
    """osso + descendentes"""
    out = {raiz}; mudou = True
    while mudou:
        mudou = False
        for n in ORD:
            if n not in out and PAI[n] in out: out.add(n); mudou = True
    return out
def _giro_em(p, R): return Matrix.Translation(p) @ R.to_4x4() @ Matrix.Translation(-p)
# parametros (graus): ergue = sobe a asa inteira no ombro; recua = varre para tras; cotovelo/punho = meia dobra
# (antebraco para frente, dedos para tras), fecha os dedos em leque. ARMADA (andar/parado) e ERGUIDA (sentado)
# usuario 31/10: no andar as asas estavam altas e perto do montador -> mais baixas e abertas para os lados
P_ARMADA = dict(ergue=18, recua=14, cotovelo=-8, punho=24, leque=0.2)
# (usuario 06/11: "nao quero a asa do dragao dobrada em nenhuma animacao"; andando/correndo = meio termo entre baixas
# quase no chao e abertas para os lados; sentado um pouco para cima) -> a pose de chao vem por env sem mexer no padrao
if os.environ.get("P_ARMADA"):
    import json as _js0; P_ARMADA.update(_js0.loads(os.environ["P_ARMADA"]))
# sentado (usuario 31/10: de frente parecia borboleta): menos vertical, mais para tras e com leve dobra para o lado
P_ERGUIDA = dict(ergue=58, recua=48, cotovelo=-34, punho=58, leque=0.5)
if os.environ.get("P_ERGUIDA"):                       # outro dragao (ex.: Glacial) ajusta o sentado sem mudar o CR
    import json as _js; P_ERGUIDA.update(_js.loads(os.environ["P_ERGUIDA"]))
# ASAS DE DESCANSO (usuario 02/11, Glacial: "deitado ou descansando, asas mais baixas, quase no chao com uma leve dobra
# para encostar no chao"): mesma montagem rigida das armadas com outros angulos (umero baixo, leve dobra no cotovelo e
# no punho) e depois o ombro rola a asa ate a ponta ficar rente ao piso (asas_rente_chao). Sem P_DESCANSO: como antes.
P_DESCANSO = None
if os.environ.get("P_DESCANSO"):
    import json as _js2; P_DESCANSO = dict(P_ARMADA); P_DESCANSO.update(_js2.loads(os.environ["P_DESCANSO"]))
ALVO_DESCANSO = float(os.environ.get("ALVO_DESCANSO", "0.062"))     # altura da ponta da asa no descanso (unid. do rig)
def asas_armadas(ergue=0.0, resp=0.0, Pfix=None, Plado=None):
    """Asas ARMADAS a partir do PLANEIO (pose validada, membrana sem lascas): giros RIGIDOS de subarvores (punho,
    cotovelo, ombro) em vez de direcoes osso a osso -> a membrana entre os dedos nao torce. ergue 0 = armada,
    1 = erguida acima do corpo (sentado); resp = respiracao (pequena variacao); Plado = {"l"/"r": P} pose propria de
    um lado (06/11: asa em rampa para montar)"""
    P0 = Pfix or {k: lerp(P_ARMADA[k], P_ERGUIDA[k], ergue) for k in P_ARMADA}; P = P0
    G = asas("Silverwing_Fly_Glide", 0.2); W = {}
    for n in ORD:                                                   # planeio com o corpo em repouso
        pai = PAI[n]; Mc = (W[pai] @ REL[n]) if pai else REL[n].copy()
        W[n] = Mc @ G[n] if n in G else Mc
    Wt = dict(W)
    for s_, sg in (("l", 1), ("r", -1)):
        P = (Plado or {}).get(s_, P0)
        def gira(raiz, piv_osso, R, extra=()):
            pv = Wt[piv_osso].translation.copy(); Mg = _giro_em(pv, R)
            for n in _sub(raiz) | set(extra): Wt[n] = Mg @ Wt[n]
        # leque: dedos 3/4/5 se aproximam do dedo de ataque (wing_3) girando para frente no plano da asa
        for k, f in (("3", 1.0), ("4", 0.7), ("5", 0.35)):
            raiz = "wing_feather_%s_0_%s" % (k, s_)
            gira(raiz, raiz, Rax(Z, -sg * 40 * P["leque"] * f))
        gira("wing_3_" + s_, "wing_3_" + s_, Rax(Z, sg * P["punho"]))                       # dedos para tras
        gira("wing_2_" + s_, "wing_2_" + s_, Rax(Z, sg * P["cotovelo"]))                    # antebraco a frente
        R = Rax(Z, sg * (P["recua"] + 1.5 * resp)) @ Rax(Y, -sg * (P["ergue"] + 2.0 * resp))
        gira("wing_1_" + s_, "wing_1_" + s_, R, extra=_sub("wing_feather_1_0_" + s_))      # asa inteira sobe
    out = {}
    for n in ASA:
        pai = PAI[n]; Mc = (Wt[pai] @ REL[n]) if pai else REL[n].copy()
        out[n] = Mc.inverted() @ Wt[n]
    return out
if ASAS_ARMADAS:
    CACHE["Silverwing_Idle"] = [asas_armadas(0.0, math.sin(2 * math.pi * k / 30)) for k in range(31)]
# fase da batida: altura da ponta da asa no Fly_Flap (para o corpo reagir a batida)
def _alt_ponta():
    act = bpy.data.actions["Silverwing_Fly_Flap"]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); zs = []
    for f in range(f0, f1 + 1): sc.frame_set(f); zs.append(A.pose.bones["wing_tip_l"].tail.z)
    A.animation_data.action = None
    m = sum(zs) / len(zs); r = max(zs) - min(zs); return [(z - m) / r for z in zs]
PONTA = _alt_ponta()
def ponta(u):
    n = len(PONTA) - 1; x = (_fase(u) % 1.0) * n; i = int(x); return lerp(PONTA[i], PONTA[min(i + 1, n)], x - i)
def fase_alta():
    """tempo do clipe em que a asa esta no alto (com ASA_GOLPE a fase muda; sem ele = indice do maximo do PONTA)"""
    return max((k / 400 for k in range(400)), key=ponta)

# ---------------------------------------------------------------- IK
def ik2(J, P, a, b, polo):
    d = P - J; L = d.length; u = d.normalized()
    L = min(max(L, abs(a - b) + 1e-4), (a + b) * 0.995)
    ca = (a * a + L * L - b * b) / (2 * a * L); sa = math.sqrt(max(0.0, 1 - ca * ca))
    w = polo - u * polo.dot(u)
    w = w.normalized() if w.length > 1e-6 else u.orthogonal().normalized()
    E = J + (u * ca + w * sa) * a
    return E, J + u * L, (P - J).length / (a + b)

# ---------------------------------------------------------------- montagem da pose
class Pose:
    """corpo: off (Vector), arfagem (graus, + nariz p/ cima), rolagem (graus, + esquerda p/ baixo), guinada (graus, + esquerda)
    curva[osso] = (cima_graus, esquerda_graus) em torno dos eixos do corpo; asas = basis por osso;
    pata[nome] = dict(modo='chao', K=Vector, beta=graus, dedos=graus) | dict(modo='livre', P=, meta=Vector, dedos=Vector)
    extra[osso] = Matrix3 de giro em mundo aplicado sobre o basis (ex.: ombro da asa)"""
    def __init__(s):
        s.off = Vector(); s.arf = s.rol = s.gui = 0.0; s.curva = {}; s.asas = {}; s.pata = {}; s.extra = {}
    def Rb(s): return Rax(Z, s.gui) @ Rax(X, -s.arf) @ Rax(Y, s.rol)

ESTIC = {}
# OMBRO FIXO (usuario 02/11, Glacial: "a asa deve se juntar ao corpo, nao ficar separada"): a batida e as correcoes de
# voo giravam o osso shoulder_*, que arrasta a RAIZ da asa (pele presa ao flanco) para fora do tronco (costura afastada
# ate 1,3 stud no Voo e 4,2 no Pairar). Com OMBRO_FIXO=1 o shoulder volta a pose de repouso (raiz presa ao corpo) e o
# MESMO giro passa para o umero (wing_1), entao o resto da asa faz exatamente o mesmo movimento; giros extras de ombro
# (plano da batida no pairar, curvas, mergulho...) tambem passam para o umero. Idempotente. Sem a variavel: como antes.
OMBRO_FIXO = os.environ.get("OMBRO_FIXO") == "1"
def _fixar_ombro(p):
    if not OMBRO_FIXO or not p.asas: return
    if any(sp.get("modo") == "chao" for sp in p.pata.values()): return   # so no ar (no chao a asa armada ja assenta melhor)
    novo = dict(p.asas)
    for s_ in ("l", "r"):
        sh, w1 = "shoulder_" + s_, "wing_1_" + s_
        if sh in novo and w1 in novo:
            Bs = rot(novo[sh]); Rr = rot(REL[w1])
            corr = Rr.inverted() @ Bs @ Rr                         # (repouso)^-1 @ Bs: giro do ombro levado ao umero
            Bw = novo[w1]
            novo[w1] = Matrix.Translation(Bw.translation) @ (corr @ rot(Bw)).to_4x4()
            novo[sh] = Matrix.Translation(novo[sh].translation)
        if sh in p.extra:
            e = p.extra.pop(sh); p.extra[w1] = e @ p.extra[w1] if w1 in p.extra else e
    p.asas = novo
# SINAL_FIXO (10/11, Sombrio: so com a variavel): o sinal do giro de cada osso vinha da direcao JA POSADA (dirb . ey); com
# o corpo muito erguido (Pairar, arf ~55) a cabeca cruzava 90 graus do eixo do corpo, o sinal invertia e a cabeca dava um
# tranco de ~60 graus para baixo a cada batida (medido: head -9 -> -71 -> -9 em 0,2 s). Fixo pelo osso em REPOUSO.
SINAL_FIXO = os.environ.get("SINAL_FIXO") == "1"
_SINAL = {}
def _sinal_repouso(n):
    if n not in _SINAL: _SINAL[n] = 1 if (A.data.bones[n].matrix_local.to_3x3() @ Y).dot(Y) > 0 else -1
    return _SINAL[n]
def resolver(p):
    _fixar_ombro(p)
    Rb = p.Rb(); ex, ey, ez = Rb @ X, Rb @ Y, Rb @ Z
    W, B, dirs = {}, {}, {}
    for n in ORD:
        pai = PAI[n]; Mc = (W[pai] @ REL[n]) if pai else REL[n].copy()
        _ik_pata(p, n, Mc, dirs, ex, ey)
        if n == "hips":
            Md = Matrix.Translation(C + p.off) @ Rb.to_4x4() @ Matrix.Translation(-C) @ Mc
        elif n in p.asas:
            Md = Mc @ p.asas[n]
            if n in p.extra: Md = Matrix.Translation(Md.translation) @ (p.extra[n] @ rot(Md)).to_4x4()
        elif n in dirs:
            y = rot(Mc) @ Y; Md = Matrix.Translation(Mc.translation) @ (y.rotation_difference(dirs[n]).to_matrix() @ rot(Mc)).to_4x4()
        elif n in p.curva:
            cima, esq = p.curva[n]
            dirb = rot(Mc) @ Y
            sinal = 1 if dirb.dot(ey) > 0 else -1             # osso para tras (cauda) ou para frente (pescoco)
            if SINAL_FIXO: sinal = _sinal_repouso(n)          # (10/11) sem inverter no meio do clipe
            R = Rax(ez, esq * (-sinal)) @ Rax(ex, cima * sinal)
            if n in p.extra: R = p.extra[n] @ R                  # giro extra em mundo (ex.: cabeca inclinada de lado)
            Md = Matrix.Translation(Mc.translation) @ (R @ rot(Mc)).to_4x4()
        else:
            Md = Mc
        W[n] = Md; B[n] = Mc.inverted() @ Md
    return W, B

def _ik_pata(p, n, Mc, dirs, ex, ey):
        # IK: ao chegar no osso superior da pata (ANTES de posiciona-lo), define as direcoes da cadeia
        for chave, pg in PERNAS.items():
            if n != pg["J"] or chave not in p.pata: continue
            sp = p.pata[chave]; J = Mc.translation
            fora = ex * pg["s"]
            polo = (ey * (1 if not pg["tras"] else -1) + fora * 0.25)          # cotovelo p/ tras, joelho p/ frente
            if sp["modo"] == "chao":
                K = sp["K"]; bet = math.radians(sp["beta"])
                tr = Vector((ey.x, ey.y, 0)).normalized()                         # 'tras' no plano do chao
                P = K + (tr * math.cos(bet) + Z * math.sin(bet)) * pg["L3"]
                dedos = Rax(Vector((tr.y, -tr.x, 0)).normalized() * -1, sp.get("dedos", 0)) @ (-tr)
                dponta = Rax(Vector((tr.y, -tr.x, 0)).normalized() * -1, sp.get("dedos", 0) * 1.6) @ (-tr)
            else:
                P = J + sp["P"]; K = P + sp["meta"].normalized() * pg["L3"]; dedos = sp["dedos"].normalized(); dponta = sp.get("ponta", dedos).normalized()
            E, Pr, est = ik2(J, P, pg["L1"], pg["L2"], polo)
            ESTIC[chave] = max(ESTIC.get(chave, 0), est)
            if (Pr - P).length > 1e-4: K = K + (Pr - P)                                # alcance limitado: o pe acompanha
            dirs[pg["J"]] = (E - J).normalized(); dirs[pg["E"]] = (Pr - E).normalized(); dirs[pg["P"]] = (K - Pr).normalized()
            dirs[pg["K"]] = dedos; dirs[pg["D"]] = dponta

def chave(act, f, B):
    for n, m in B.items():
        pb = A.pose.bones[n]; pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
        pb.keyframe_insert("rotation_quaternion", frame=f, group=n); pb.keyframe_insert("location", frame=f, group=n)

def gerar(nome, n_quadros, fn, loop=True):
    if PEDIDOS and nome not in PEDIDOS: return
    an = "Silverwing_" + nome
    for f_ in ("Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide"): fonte(f_)
    if an in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[an])
    act = bpy.data.actions.new(an); act.use_fake_user = True
    A.animation_data_create(); A.animation_data.action = act
    ESTIC.clear(); zmin = 9
    for k in range(n_quadros + 1):
        u = k / n_quadros
        p = fn(u)
        # certificacao 02/11: em clipe de chao (alguma pata apoiada) nenhuma ponta de asa entra no piso (asas dobradas
        # com o tronco inclinado / meia abertura de exibicao passando por baixo): sobe so o necessario
        if p.asas and not getattr(p, "descanso", False) and any(sp.get("modo") == "chao" for sp in p.pata.values()):
            asas_acima_do_chao(p, asas("Silverwing_Fly_Flap", FA))
        W, B = resolver(p)
        chave(act, k + 1, B)
        if "chao" in nome or True:
            zmin = min(zmin, min(W[PERNAS[c]["K"]].translation.z for c in PERNAS))
    nk = 0
    for lay in act.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"; nk += 1
    if nk == 0: raise RuntimeError("sem chaves em %s (acao atual=%s)" % (an, A.animation_data.action and A.animation_data.action.name))
    act["loop"] = loop
    A.animation_data.action = None
    print("CLIPE", an, n_quadros + 1, "quadros", "%.2fs" % (n_quadros / FPS), "loop", loop,
          "estic", {c: round(v, 2) for c, v in ESTIC.items()}, "zmin_dedos", round(zmin, 3))

# ---------------------------------------------------------------- posturas base
def pescoco_alto(p, cima=0.0, esq=0.0, cab=0.0):
    """pescoco erguido (dragao em pe) com a cabeca nivelada; cima/esq extras distribuidos"""
    base = {k: v * NECK_BASE for k, v in {"spine_2": 14, "spine_3": 10, "spine_4": 4}.items()}
    tot = 0
    for i, n in enumerate(PESCOCO):
        c = base[n] + cima * (0.3 + 0.2 * i); e = esq * (0.25 + 0.1 * i); p.curva[n] = (c, e); tot += c
    p.curva["head"] = (-tot + 2 + cab - p.arf, esq * 0.3)       # cabeca nivelada no mundo (compensa pescoco e tronco)

def cauda(p, base_cima, curv, lat, chao=True, onda=None):
    """base_cima: graus no 1o segmento; curv: graus somados por segmento (curva continua);
    lat: lista de desvios laterais (+esquerda) por segmento; chao: a cauda deita no chao (z>=0.035)"""
    W, _ = resolver(p)
    base_cima *= CAUDA_BASE_K
    # curva CONTINUA: a queda da base se distribui nos 4 primeiros segmentos (antes vinha toda no 1o = "quebra" no
    # quadril) e a subida de apoio comeca so no meio da cauda
    DIST = [0.34, 0.28, 0.22, 0.16, 0, 0, 0]; SUB = [0, 0, 0, 0.5, 1, 1, 0.8]
    ang_cima = [base_cima * DIST[i] * 1.5 + curv * SUB[i] + (onda[i] if onda else 0.0) for i in range(len(CAUDA))]
    for i, n in enumerate(CAUDA):
        p.curva[n] = (ang_cima[i], lat[i] if i < len(lat) else 0)
    if chao:                                             # apoio: segmento que entraria no chao sobe so o necessario
        for it in range(3):
            W, _ = resolver(p)
            for i, n in enumerate(CAUDA):
                tz = (W[n] @ Vector((0, A.data.bones[n].length, 0))).z if False else (W[n].translation + rot(W[n]) @ Vector((0, A.data.bones[n].length, 0))).z
                if tz < 0.035:
                    L = A.data.bones[n].length; falta = 0.035 - tz
                    c, e = p.curva[n]; p.curva[n] = (c + math.degrees(math.asin(min(1, falta / L))), e)
                    if i + 1 < len(CAUDA):
                        c2, e2 = p.curva[CAUDA[i + 1]]; p.curva[CAUDA[i + 1]] = (c2 - math.degrees(math.asin(min(1, falta / L))) * 0.5, e2)

# CAUDA VIVA: cada componente e uma onda que NASCE na base e corre para a ponta (atraso por segmento), com peso
# crescente para a ponta (a base quase nao vira: nao bate nas coxas). Atraso ~0,8-1,1 rad por segmento = curva em S
# ao longo dos 7 segmentos; varios harmonicos inteiros do clipe (laco perfeito) com fases diferentes = sem vai-e-vem
# mecanico; 'env' modula a amplitude (momentos quase parados). Graus por segmento (giro local), +esquerda / +cima.
PESO_CAUDA = [0.22, 0.42, 0.62, 0.8, 0.93, 1.0, 1.0]
def onda_cauda(u, comps, env=1.0):
    """comps: (amp_graus, harmonico_inteiro, fase0_rad, atraso_rad_por_segmento)"""
    return [env * PESO_CAUDA[k] * sum(a * math.sin(2 * math.pi * h * u + f0 - at * k) for a, h, f0, at in comps)
            for k in range(len(CAUDA))]
def somar(a, b): return [x + y for x, y in zip(a, b)]

# posicoes de apoio (repouso do esqueleto: J dianteiro x=+-0.068, traseiro +-0.10)
# apoio dos pes: abaixo da junta superior de cada pata (largura do ombro/quadril + 15%) e a frente/atras como no
# repouso; z do dedo no chao
def _apoio(c):
    pg = PERNAS[c]; J = H(pg["J"]); K = H(pg["K"])
    x = XM + (J.x - XM) * 1.15
    return Vector((x, K.y, 0.022 if not pg["tras"] else 0.016))
PE = {c: _apoio(c) for c in PERNAS}
print("APOIO", {c: tuple(round(v, 3) for v in p) for c, p in PE.items()})
BETA = {"PD_E": 52, "PD_D": 52, "PT_E": 60, "PT_D": 60}

def em_pe(p, agach=0.0):
    p.off = Vector((0, 0, -0.035 - agach)); p.arf = 5 - agach * 40
    for c in PERNAS: p.pata[c] = dict(modo="chao", K=PE[c].copy(), beta=BETA[c] + agach * 60, dedos=0)

# ---------------------------------------------------------------- clipes de solo
def f_parado(u):
    """Parado de 8 s: 3 respiracoes, olhar que varre o ambiente (ida e volta + desvio rapido), troca de apoio entre as
    patas e cauda viva: curva lenta em S para o lado OPOSTO ao olhar (contrapeso), ponta com pequenos toques e
    momentos quase parados (env)."""
    p = Pose(); em_pe(p)
    r = math.sin(2 * math.pi * 3 * u)                                              # respiracao (3 por clipe)
    olhar = math.sin(2 * math.pi * u) * 0.75 + 0.25 * math.sin(2 * math.pi * 3 * u + 0.8)
    apoio = math.sin(2 * math.pi * u + 0.6)
    p.off += Vector((0.006 * apoio * AC, 0, 0.003 * r * AC * 1.5))
    p.rol = 1.4 * apoio * AC; p.arf += 0.6 * r * AC
    p.curva["spine_1"] = (0.8 * r * AC * 1.5, 0); p.curva["spine_0"] = (-0.4 * r * AC, -2.0 * olhar * AC)
    pescoco_alto(p, cima=-14 * PENDULO + 3 * AC * 1.5 * math.sin(2 * math.pi * 2 * u + 1.1), esq=14 * olhar * AC,
                 cab=-4 * AC * math.sin(2 * math.pi * 3 * u + 0.4))
    p.asas = asas("Silverwing_Idle", (u * 3) % 1.0)
    env = 0.45 + 0.55 * (0.5 - 0.5 * math.cos(2 * math.pi * 2 * u + 0.4)) ** 1.5
    lat = onda_cauda(u, [(-13.0, 1, 0.9, 0.95), (5.5, 2, 2.1, 1.2), (2.2, 5, 0.3, 1.6)], env)
    vert = onda_cauda(u, [(2.2, 1, 1.7, 0.8), (1.2, 3, 0.2, 1.1)], env)
    cauda(p, -16, 5.0, lat, onda=vert)
    return p

# asas no chao: DOBRADAS rentes ao corpo (referencia) — o Walk do molde deixava as asas meio abertas e assimetricas
def andadura(T_ciclo, duty, S, fases, alt_pd, alt_pt, bob, rol, guin, arf_osc=0.0, flex=0.0, nome_asa="Silverwing_Idle", corrida=False):
    def fn(u):
        p = Pose(); em_pe(p)
        bob_ = bob * (0.35 if PASSO_PESADO else 1.0)                    # sem quicar: o peso aparece nos apoios
        if PASSO_PESADO: p.arf -= 6 if corrida else 4                    # tronco inclinado para frente
        p.off += Vector((0, 0, -bob_ * math.cos(4 * math.pi * u) - 0.014 - (0.01 if corrida else 0)))   # em marcha o corpo baixa (alcance da traseira)
        p.rol = rol * math.sin(2 * math.pi * u); p.gui = 0
        p.arf += arf_osc * math.sin(2 * math.pi * u + 1.2)
        p.curva["spine_0"] = (flex * math.sin(2 * math.pi * u + 1.2), guin * math.sin(2 * math.pi * u))
        p.curva["spine_1"] = (flex * 0.5 * math.sin(2 * math.pi * u + 1.6), guin * 0.6 * math.sin(2 * math.pi * u - 0.4))
        for c, pg in PERNAS.items():
            # traseira: passada 15% menor (perna mais curta) com apoio proporcionalmente menor = MESMA velocidade do
            # pe no chao que a dianteira (sem patinar); o centro do apoio fica no mesmo ponto do ciclo
            k_ = 0.85 if pg["tras"] else 1.0; Sp, dp = S * k_, duty * k_
            fase = (u - fases[c] - (duty - dp) / 2) % 1.0
            K = PE[c].copy(); bet = BETA[c]; dedos = 0
            if fase < dp:                                      # apoio: o pe recua com o chao (anim no lugar)
                v = fase / dp; K.y += Sp * (v - 0.5)
                if v > 0.8: bet += (v - 0.8) / 0.2 * 18; dedos = -(v - 0.8) / 0.2 * 10   # impulso: calcanhar sobe
            else:                                              # balanco: avanca e levanta
                v = (fase - dp) / (1 - dp); K.y = PE[c].y + Sp * (0.5 - smooth(v))
                K.z += (alt_pd if not pg["tras"] else alt_pt) * math.sin(math.pi * v)
                bet += 22 * math.sin(math.pi * v); dedos = -32 * math.sin(math.pi * v)
            if PASSO_PESADO:
                if fase < dp:
                    v = fase / dp
                    amort = math.exp(-((v - 0.06) / 0.09) ** 2)               # logo apos pisar
                    if not pg["tras"]:                                     # dianteira recebe o peso: ombro cede
                        p.off.z -= 0.010 * amort * (1.3 if corrida else 1.0); p.arf -= 1.6 * amort
                    elif v > 0.7:                                          # traseira empurra: quadril sobe e avanca
                        emp = math.sin(math.pi * (v - 0.7) / 0.3)
                        p.off.z += 0.006 * emp; p.arf -= 1.2 * emp
                else:
                    v = (fase - dp) / (1 - dp)
                    if not pg["tras"]:                                     # dianteira alta e dedos curvados (referencia)
                        K.z += 0.030 * math.sin(math.pi * v); dedos -= 16 * math.sin(math.pi * v); bet += 8 * math.sin(math.pi * v)
            p.pata[c] = dict(modo="chao", K=K, beta=bet, dedos=dedos)
        # referencia: andando o pescoco vai para FRENTE e mais baixo (nao ereto), balanca a cada passo com atraso e a
        # cabeca acompanha o olhar; correndo estica ainda mais
        if corrida:
            # corrida: pescoco esticado a frente balancando pouco e com atraso; a cabeca COMPENSA 75% (olhar estavel)
            osc = 3.0 * math.cos(4 * math.pi * u - 0.7)
            pescoco_alto(p, cima=(-50 if PASSO_PESADO else -44) * PENDULO + osc, esq=-guin * 0.8 * math.sin(2 * math.pi * u - 0.3), cab=-0.75 * osc)
        else:
            pescoco_alto(p, cima=(-38 if PASSO_PESADO else -30) * PENDULO + 3 * AC * 1.6 * math.cos(4 * math.pi * u - 0.7),
                         esq=-guin * 1.2 * math.sin(2 * math.pi * u - 0.3), cab=-2.5 * AC * math.cos(4 * math.pi * u - 1.2))
        if ASAS_ARMADAS:                       # asas armadas balancam com o passo (2 por ciclo), com atraso do tronco
            ergue = (0.12 if corrida else 0.08) + (0.30 if corrida else 0.22) * math.cos(4 * math.pi * u - 1.3)
            p.asas = asas_armadas(ergue, 1.0 * math.sin(4 * math.pi * u - 1.9))
        else:
            p.asas = asas(nome_asa, u)
        # cauda: onda lateral que nasce no quadril (contrapeso do passo) e cresce com atraso para a ponta; na corrida
        # menor e mais rigida (contrapeso, nao chicote)
        # (+ 2o harmonico: a curva muda de forma entre as passadas em vez de so trocar de lado)
        k_c = 0.45 if corrida else 1.0
        lat = onda_cauda(u, [(15.0 * k_c, 1, -0.4, 0.8), (3.2 * k_c, 2, 1.0, 1.15)])
        vert = onda_cauda(u, [((1.4 if corrida else 1.6), 2, 0.0, 0.6), (0.8, 1, 1.3, 0.9)])
        cauda(p, -6 if corrida else -12, 4.0 if corrida else 4.5, lat, chao=True, onda=vert)
        return p
    return fn

# andar: sequencia lateral (TE, DE, TD, DD); v = S/(duty*T)
# andar mais vivo (referencia: trote agil, nao arrastado): passada maior e ciclo mais curto = ~8 studs/s no ritmo 1
T_ANDAR, D_ANDAR, S_ANDAR = 0.9, 0.64, 0.26
# (bob, rolagem, guinada do tronco maiores: ombros e quadril trabalham a cada passo; mesma passada = sem patinar)
f_andar = andadura(T_ANDAR, D_ANDAR, S_ANDAR, {"PT_E": 0.0, "PD_E": 0.25, "PT_D": 0.5, "PD_D": 0.75}, 0.055, 0.05,
                   (0.005 + 0.007 * PENDULO) * AC, (1.5 + 1.8 * PENDULO) * AC, (2.5 + 2.0 * PENDULO) * AC, arf_osc=1.5 * PENDULO * AC)
# corrida PESADA (usuario 29/10: a anterior quicava/saltitava): mesma velocidade (1,0823 u/s = 18,94 studs/s, o
# servidor escala o ritmo por RitmoCorrerBase), apoio maior (0,42 -> 0,48: quase sempre um pe no chao, sem fase
# aerea) e passada mais longa; quique, arfagem, flexao, rolagem e balanco do pescoco ~1/3 dos anteriores
T_CORRER, D_CORRER = 0.66, 0.48; S_CORRER = round(0.30 / (0.42 * 0.66) * D_CORRER * T_CORRER, 4)
f_correr = andadura(T_CORRER, D_CORRER, S_CORRER, {"PT_E": 0.0, "PT_D": 0.12, "PD_D": 0.5, "PD_E": 0.62}, 0.07, 0.06,
                    0.010, 2.0, 2.4, arf_osc=2.5, flex=4.0, corrida=True)

def f_parada(u):                       # frenagem curta: dianteiras firmam a frente, corpo recua e assenta
    p = Pose(); em_pe(p)
    k = math.sin(math.pi * min(1, u * 1.4)); p.arf += 5 * k; p.off += Vector((0, 0.02 * k, -0.02 * k))
    # (certificacao 02/11: o pe dianteiro deslizava 0,6 stud apoiado; agora fica plantado e so o corpo recua)
    pescoco_alto(p, cima=-6 * k)
    p.asas = asas("Silverwing_Idle", u * 0.3)
    # frenagem: a cauda sobe (contrapeso do corpo que recua) e a ponta chicoteia para cima com atraso
    cauda(p, -12 + 6 * k, 4.5, onda_cauda(u, [(3.0, 1, 0.5, 0.9)]),
          onda=[(5 + 4 * k_) * math.sin(math.pi * min(1, max(0, u * 1.5 - 0.08 * k_))) for k_ in range(7)])
    return p

# SENTADO (usuario 31/10, referencia do dragao verde): traseiras dobradas sob o corpo com o metatarso no chao, quadril
# baixo, peito e pescoco erguidos, cabeca altiva e nivelada, dianteiras retas apoiando, asas recolhidas, cauda em
# curva suave pelo lado no chao. a = 0 (em pe) .. 1 (sentado); r = respiracao; olhar = giro da cabeca
def pose_sentado(p, a, r=0.0, olhar=0.0, ponta=None, passo=None):
    """passo (transicoes): progresso 0..1 de cada pata reposicionada EM PASSO (levanta, avanca, pousa); sem ele o
    pe acompanha 'a' (antes deslizava apoiado ate 1,2 stud no Sentar)"""
    em_pe(p)
    p.arf += 30 * a                                                     # peito sobe, quadril desce (giro no centro)
    p.off += Vector((0, 0.03 * a, -0.105 * a + 0.004 * r * a))          # ombros quase na altura de pe
    def ap(c): return passo[c] if passo else a
    for c in ("PT_E", "PT_D"):                                          # traseiras sob o corpo, pe deitado no chao
        p.pata[c]["K"].y -= 0.07 * ap(c); p.pata[c]["beta"] = lerp(BETA[c], 6, a)
    for c in ("PD_E", "PD_D"):                                          # dianteiras retas, um pouco a frente
        p.pata[c]["K"].y -= 0.03 * ap(c); p.pata[c]["beta"] = lerp(BETA[c], 64, a)
    if passo:
        for c in PERNAS: p.pata[c]["K"].z += (0.03 if c.startswith("PD") else 0.04) * math.sin(math.pi * passo[c])
    p.curva["spine_1"] = (1.2 * r * a, 0); p.curva["spine_0"] = (-0.6 * r * a, -2.0 * olhar * a)
    pescoco_alto(p, cima=-14 * (1 - a) - 8 * a + 1.5 * r, esq=12 * olhar, cab=4 * a)
    lado = -1                                                           # cauda curva para a direita do dragao
    lat = [lado * (1.0 + 1.4 * k) * a for k in range(7)]                # curva suave (~35 graus no total)
    if ponta: lat = somar(lat, ponta)
    # tronco inclinado 30 graus: o apoio automatico da cauda no chao empilhava angulos para CIMA (cauda no ar).
    # Sentado: curva definida por segmento -- a base desce ate o chao, o meio fica rente ao piso e a curva e lateral;
    # nas transicoes mistura com a cauda de em pe
    cauda(p, -14, 3.0, [0] * 7, chao=True)
    CIMA_SENTADO = [16, 9, 5, 2, 1, 0.5, 0]                            # graus locais (compensam os 30 do tronco)
    for k, n in enumerate(CAUDA):
        c, e = p.curva[n]
        p.curva[n] = (lerp(c, CIMA_SENTADO[k], a), lat[k] if k < len(lat) else 0)
    # deita a cauda NO chao: cada segmento (a partir do 2o) corrige o angulo para a ponta ficar logo acima do piso
    # (sobe ou desce), entao a curva lateral fica rente ao chao em vez de subir ou atravessar
    for it in range(6):
        W, _ = resolver(p)
        for k, n in enumerate(CAUDA):
            if k == 0: continue
            Lb = A.data.bones[n].length
            tz = (W[n].translation + rot(W[n]) @ Vector((0, Lb, 0))).z
            alvo = 0.03 + 0.004 * k
            corr = math.degrees(math.asin(max(-1, min(1, (alvo - tz) / Lb)))) * 0.9 * a
            c, e = p.curva[n]; p.curva[n] = (c + corr, e)
    p.asas = asas_armadas(a, r) if ASAS_ARMADAS else asas("Silverwing_Idle", 0.0)    # sentado: asas acima do corpo
    if not ASAS_ARMADAS:
        # asas DOBRADAS (certificacao 02/11): com o tronco erguido 30 graus a dobra apontava para o chao (pontas ~5 studs
        # dentro do piso); o ombro devolve a inclinacao do tronco e a dobra fica deitada ao longo do flanco
        Rb = p.Rb()
        for n_ in ("shoulder_l", "shoulder_r"): p.extra[n_] = Rax(Rb @ X, 26 * a)
    if passo: cauda_sobre_chao(p)              # transicao: a cauda nao atravessa o piso no meio do caminho (era -2,9 studs)
    return p
def f_sentar(u):
    """em pe -> sentado 1,6 s: para, REPOSICIONA as dianteiras (um passo curto cada), flexiona joelhos/quadris e baixa a
    garupa enquanto as traseiras vem para baixo do corpo em passo, peito sobe, pescoco e asas acomodam, cauda curva"""
    passo = {"PD_E": janela(u, 0.02, 0.17), "PD_D": janela(u, 0.12, 0.27), "PT_E": janela(u, 0.32, 0.52), "PT_D": janela(u, 0.46, 0.66)}
    return pose_sentado(Pose(), smooth(u), passo=passo)
def f_levantar_sentado(u):
    """sentado -> em pe 1,2 s: o peso passa para as dianteiras (corpo vai a frente), as traseiras empurram e erguem a
    garupa voltando em passo para tras, o peito desce para a postura quadrupede e as dianteiras se ajustam"""
    passo = {"PT_E": 1 - janela(u, 0.22, 0.44), "PT_D": 1 - janela(u, 0.36, 0.58), "PD_E": 1 - janela(u, 0.62, 0.78), "PD_D": 1 - janela(u, 0.74, 0.92)}
    a = 1 - smooth(min(1.0, u * 1.1))
    p = pose_sentado(Pose(), a, passo=passo)
    p.off += Vector((0, -0.018 * pulso(u, 0.0, 0.3, 0.55, 0.9), 0)); p.arf -= 4 * pulso(u, 0.0, 0.3, 0.55, 0.9)
    return p
def f_sentado(u):
    """8 s: 3 respiracoes, olhar lento (ida e volta + desvio), ajustes de cauda com momentos quase parados"""
    r = math.sin(2 * math.pi * 3 * u)
    olhar = 0.75 * math.sin(2 * math.pi * u) + 0.25 * math.sin(2 * math.pi * 3 * u + 0.8)
    env = 0.4 + 0.6 * (0.5 - 0.5 * math.cos(2 * math.pi * 2 * u + 0.4)) ** 1.5
    ponta = onda_cauda(u, [(4.0, 1, 0.6, 0.9), (2.0, 3, 1.4, 1.3)], env)
    return pose_sentado(Pose(), 1.0, r, olhar, ponta)

def asas_descanso(a=1.0, resp=0.0):
    """basis das asas de descanso misturadas com as armadas (a = 0 armadas .. 1 descanso)"""
    if not P_DESCANSO: return asas("Silverwing_Idle", 0.0)
    return asas_armadas(0.0, resp, {k: lerp(P_ARMADA[k], P_DESCANSO[k], a) for k in P_ARMADA})
def _min_lado(p, lado):
    W, _ = resolver(p)
    return min((W[n].translation + rot(W[n]) @ Vector((0, A.data.bones[n].length, 0))).z for n in ASA if n.endswith("_" + lado))
def asas_rente_chao(p, a=1.0):
    """rola cada asa no ombro (eixo frente-tras do corpo) ate a ponta ficar em ALVO_DESCANSO; peso a (transicoes)"""
    if not P_DESCANSO or a <= 0.001: return
    # (06/11) com as asas abertas do descanso novo, o rolamento ate o chao empurrava as pontas ~4 studs para dentro do
    # piso nas transicoes; DESCANSO_RENTE=0 deixa o limite padrao do gerar() manter as pontas acima do chao
    if os.environ.get("DESCANSO_RENTE") == "0": return
    p.descanso = True                      # gerar() nao ergue estas asas (a ponta encosta no chao de proposito)
    Rb = p.Rb()
    for lado, sg in (("l", 1), ("r", -1)):
        n = "shoulder_" + lado; base = p.extra.get(n)
        def poe(ang): p.extra[n] = Rax(Rb @ Y, sg * ang) @ base if base is not None else Rax(Rb @ Y, sg * ang)
        # MENOR giro a partir da pose de descanso: descobre o sentido que SOBE a ponta (derivada local) e busca entre 0 e
        # o limite nesse sentido (subir, se a ponta esta abaixo do alvo) ou no oposto (descer, se esta acima)
        poe(0.0); z0 = _min_lado(p, lado)
        poe(6.0); sobe = 1.0 if _min_lado(p, lado) > z0 else -1.0
        lim = sobe * 22.0 if z0 < ALVO_DESCANSO else -sobe * 35.0
        poe(lim)
        if (z0 < ALVO_DESCANSO) == (_min_lado(p, lado) < ALVO_DESCANSO): ang = lim      # nao cruza o alvo: vai ao limite
        else:
            lo, hi = 0.0, lim                                                  # lo do lado de z0
            for _ in range(12):
                mid = (lo + hi) / 2; poe(mid)
                if (_min_lado(p, lado) < ALVO_DESCANSO) == (z0 < ALVO_DESCANSO): lo = mid
                else: hi = mid
            ang = (lo + hi) / 2
        poe(ang * a)
        if os.environ.get("DBG_DESC"): print("DESC", lado, "z0=%.3f lim=%.0f ang=%.1f zf=%.3f" % (z0, lim, ang, _min_lado(p, lado)))

# ASA EM RAMPA para montar (usuario 06/11: "para o jogador montar, a animacao deve abrir a asa ao montar (como uma
# rampa)"): a asa do lado do cavaleiro abre esticada e desce ate o chao (sem dobra no cotovelo/punho, dedos juntos);
# a ponta encosta no chao pelo asas_rente_chao. Lado "l" = esquerda do dragao (+X). Clipes *_Rampa_E / *_Rampa_D.
P_RAMPA = dict(ergue=-48, recua=-6, cotovelo=0, punho=6, leque=0.35)
if os.environ.get("P_RAMPA"):
    import json as _js3; P_RAMPA.update(_js3.loads(os.environ["P_RAMPA"]))
def f_agachar(ini, fim, ag=0.09, rampa=None):
    def fn(u):
        a = lerp(ini, fim, smooth(u)) if ini != fim else ini
        p = Pose(); em_pe(p, agach=ag * a)
        r = math.sin(2 * math.pi * u) if ini == fim else 0
        p.off += Vector((0, 0, 0.003 * r))
        pescoco_alto(p, cima=-8 * a + 2 * r)
        p.asas = asas_descanso(a, r) if P_DESCANSO else asas("Silverwing_Idle", u)
        if rampa:                                                            # a asa do lado do cavaleiro vira rampa
            base = {k: lerp(P_ARMADA[k], P_DESCANSO[k], a) for k in P_ARMADA} if P_DESCANSO else dict(P_ARMADA)
            p.asas = asas_armadas(0.0, 0.3 * r, base, Plado={rampa: {k: lerp(base[k], P_RAMPA[k], a) for k in base}})
        # deitado: cauda enrola devagar para um lado (descanso) e a ponta mexe pouco; transicoes levam a curva junto
        enrola = [6.0 * a * PESO_CAUDA[k_] for k_ in range(7)]
        viva = onda_cauda(u, [(2.5, 1, 0.3, 0.9), (1.0, 2, 1.7, 1.3)]) if ini == fim else [0] * 7
        cauda(p, -16, 5.0, somar(enrola, viva))
        asas_rente_chao(p, a)
        return p
    return fn

# ---------------------------------------------------------------- comportamento natural (IA selvagem)
# Nomes = os logicos do EstadosDragao (Observar, Beber, Comer, Idle_Alerta_Mantido, Ninho_Ameaca, Dormir...): o
# "Silverwing_<nome>" e achado direto (antes caiam no apelido "*" = Parado). Duracoes casadas com as esperas do
# IA_Dragao.Cerebro (Beber 9,5 s, Comer 8,5 s, AmeacaNinho 4,6 s).
def ponta_boca(W):
    m = W["mouth_lower"]; return m.translation + rot(m) @ Vector((0, A.data.bones["mouth_lower"].length, 0))
def pescoco_ao_chao(p, z_alvo, esq=0.0, cab_extra=0.0):
    """abaixa o pescoco (mais na base, menos perto da cabeca) ate a boca chegar a altura z_alvo; a cabeca gira de
    volta 55% para o focinho ficar apontado para baixo/frente (nao dobrado para tras)"""
    def aplicar(k):
        for i, n_ in enumerate(PESCOCO): p.curva[n_] = (-k * (1.0, 0.7, 0.3)[i], esq * (0.25 + 0.1 * i))
        p.curva["head"] = (0.55 * k + cab_extra, esq * 0.3)
    lo, hi = 0.0, 75.0
    for _ in range(14):
        k = (lo + hi) / 2; aplicar(k)
        W, _ = resolver(p)
        if ponta_boca(W).z > z_alvo: lo = k
        else: hi = k
    aplicar((lo + hi) / 2)

def base_pe(p, frente_baixa=0.0):
    """em pe; frente_baixa (0..1): tronco inclina para frente e as patas dianteiras flexionam (apoio para beber/comer)"""
    em_pe(p)
    p.arf += -6 * frente_baixa; p.off += Vector((0, -0.01 * frente_baixa, -0.012 * frente_baixa))
    for c in ("PD_E", "PD_D"): p.pata[c]["beta"] += 10 * frente_baixa; p.pata[c]["K"].x += PERNAS[c]["s"] * 0.012 * frente_baixa

def f_beber(u):
    """Beber 9 s: aproxima a boca da agua (0-15%), 5 lambidas com pausas (mandibula + cabeca mergulham pouco), ergue
    a cabeca no meio para vigiar, volta a beber, ergue (85-100%)."""
    desce = janela(u, 0.02, 0.15) * (1 - janela(u, 0.86, 1.0)) * (1 - pulso(u, 0.47, 0.52, 0.58, 0.63))
    p = Pose(); base_pe(p, desce)
    r = math.sin(2 * math.pi * 4 * u)
    p.off += Vector((0, 0, 0.003 * r))
    lam = max(0.0, math.sin(2 * math.pi * 10 * u)) ** 2 * desce                   # lambidas (10 no clipe, so a metade baixa)
    z = lerp(0.40, 0.035, desce) - 0.012 * lam
    olhar = 18 * pulso(u, 0.48, 0.52, 0.58, 0.62) * math.sin(2 * math.pi * 2 * u)
    pescoco_ao_chao(p, z, esq=olhar)
    boca_abre(p, 0.18 * lam)
    p.asas = asas("Silverwing_Idle", (u * 3) % 1.0)
    cauda(p, -14, 5.0, onda_cauda(u, [(-8.0, 1, 0.6, 0.95), (3.0, 2, 1.8, 1.25)]),
          onda=onda_cauda(u, [(1.5, 2, 0.3, 0.8)]))
    return p

def f_comer(u):
    """Comer 8,5 s: abaixa ate a presa no chao a frente, 3 ciclos de morder-puxar-rasgar (tranco para tras e para
    cima) e mastigar com a cabeca erguida, olhada rapida em volta, termina erguendo."""
    p = Pose()
    ciclo = (u * 3) % 1.0; n_c = min(2, int(u * 3))
    abaixo = pulso(ciclo, 0.0, 0.22, 0.42, 0.55) * (1 - janela(u, 0.93, 1.0))
    puxa = pulso(ciclo, 0.36, 0.45, 0.5, 0.62)
    mastiga = janela(ciclo, 0.55, 0.65) * (1 - janela(ciclo, 0.92, 1.0))
    base_pe(p, abaixo)
    p.off += Vector((0, 0.012 * puxa, 0.004 * puxa))
    z = lerp(0.33, 0.05, abaixo) + 0.05 * puxa
    olhar = (20 if n_c == 1 else -12) * mastiga * math.sin(math.pi * janela(ciclo, 0.6, 0.9))
    pescoco_ao_chao(p, z, esq=olhar, cab_extra=-10 * puxa + 6 * mastiga)
    boca_abre(p, 0.75 * pulso(ciclo, 0.12, 0.22, 0.3, 0.38) + 0.28 * mastiga * (0.5 + 0.5 * math.sin(2 * math.pi * 14 * u)))
    p.curva["spine_1"] = (-3 * puxa, 0)
    p.asas = asas("Silverwing_Idle", (u * 2) % 1.0)
    cauda(p, -14, 5.0, onda_cauda(u, [(-7.0, 1, 0.2, 0.95), (2.5, 3, 1.1, 1.2)]),
          onda=[2.5 * puxa * PESO_CAUDA[k] for k in range(7)])
    return p

def segura(u, alvos, giro=0.35):
    """olhar em etapas: vira, SEGURA, vira (nao seno continuo). alvos = lista de graus, um por trecho; giro = fracao
    do trecho gasta virando"""
    n_ = len(alvos); x = (u % 1.0) * n_; i = int(x); t = x - i
    return lerp(alvos[i - 1], alvos[i], smooth(t / giro))          # alvos[-1] = ultimo (laco fecha)

def f_observar(u):
    """Observar 7 s: corpo parado e firme, cabeca/pescoco varrem o ambiente em etapas (vira, segura, vira), ergue o
    pescoco para olhar longe, respiracao, troca de apoio, cauda em S lento."""
    p = Pose(); em_pe(p)
    r = math.sin(2 * math.pi * 3 * u)
    # usuario 31/10 ("cabeca igual louco"): viradas mais lentas e menores (pico 263 -> ~100 graus/s)
    esq = segura(u, [0, 24, 24, -18, -18, 6, 0], 0.65)
    cima = segura(u, [0, 5, 8, 2, 6, 0, 0], 0.65)
    p.off += Vector((0, 0, 0.003 * r)); p.arf += 0.8 * r
    p.curva["spine_0"] = (0, -0.12 * esq)
    pescoco_alto(p, cima=-10 + cima, esq=esq, cab=-2 * r)
    p.asas = asas("Silverwing_Idle", (u * 3) % 1.0)
    cauda(p, -15, 5.0, somar([-0.25 * esq * PESO_CAUDA[k] for k in range(7)], onda_cauda(u, [(5.0, 1, 0.9, 0.95), (2.0, 3, 0.3, 1.3)])),
          onda=onda_cauda(u, [(1.6, 2, 0.4, 0.8)]))
    return p

def f_farejar(u):
    """Farejar 2,5 s: abaixa a cabeca a frente, 5 farejadas curtas (trancos), ergue."""
    p = Pose(); em_pe(p)
    desce = pulso(u, 0.0, 0.25, 0.75, 1.0)
    tr = max(0.0, math.sin(2 * math.pi * 10 * u)) * desce
    pescoco_ao_chao(p, lerp(0.40, 0.14, desce) + 0.008 * tr, esq=6 * math.sin(2 * math.pi * u))
    p.asas = asas("Silverwing_Idle", u)
    cauda(p, -15, 5.0, onda_cauda(u, [(3.0, 1, 0.5, 1.0)]))
    return p

def f_reagir(u):
    """Reagir a estimulo 1,2 s: cabeca sobe e encara de repente, corpo recua um pouco, asas se mexem (meia abertura
    curta), cauda tensiona."""
    s_ = pulso(u, 0.0, 0.18, 0.6, 1.0); seg = janela(u, 0.1, 0.35)
    p = Pose(); em_pe(p)
    p.off += Vector((0, 0.015 * s_, 0.006 * s_)); p.arf += 4 * s_
    pescoco_alto(p, cima=-10 + 16 * seg, cab=-6 * seg)
    p.asas = asas_ameaca(0.22 * s_)
    cauda(p, -15 + 8 * s_, 5.0, onda_cauda(u, [(3.0, 1, 0.0, 1.0)]), onda=[5 * s_ * PESO_CAUDA[k] for k in range(7)])
    return p

def f_alerta(u):
    """Alerta mantido 4 s (laco): pescoco ereto, cabeca alta encarando, asas meio abertas (parecer maior), cauda
    erguida e tensa balancando devagar, respiracao rapida, rosnado leve."""
    p = Pose(); em_pe(p)
    r = math.sin(2 * math.pi * 4 * u)
    p.off += Vector((0, 0.006, 0.006 + 0.003 * r)); p.arf += 3 + 0.8 * r
    pescoco_alto(p, cima=6 + 2 * math.sin(2 * math.pi * u + 0.4), esq=5 * math.sin(2 * math.pi * u), cab=-5)
    boca_abre(p, 0.12 * max(0.0, math.sin(2 * math.pi * 2 * u)))
    p.asas = asas_ameaca(0.3 + 0.03 * math.sin(2 * math.pi * 2 * u))
    cauda(p, -6, 5.0, onda_cauda(u, [(6.0, 1, 0.0, 0.9), (2.0, 2, 1.3, 1.2)]), onda=[4 * PESO_CAUDA[k] for k in range(7)])
    return p

def f_ameaca(u):
    """Ameaca do ninho 4,6 s: abaixa a frente (postura de bote), abre as asas bem (intimidacao), recolhe o pescoco
    e RUGE projetando a cabeca, sacode, segura a postura ofensiva.
    CABECA_RUGIDO (03/11): a boca fica fechada (labios entreabertos) ate o som e abre/fecha JUNTO com ele (som em 0,34,
    forte ate ~0,62 e cauda ate ~0,75); a cabeca vigia o ninho de um lado ao outro antes e ataca em blefe no rugido."""
    if CABECA_RUGIDO: return f_ameaca_v2(u)
    pre = janela(u, 0.0, 0.2); insp = pulso(u, 0.18, 0.3, 0.32, 0.4); rug = pulso(u, 0.33, 0.4, 0.62, 0.75)
    p = Pose(); base_pe(p, 0.55 * pre)
    for c in PERNAS: p.pata[c]["beta"] += 6 * pre
    p.off += Vector((0, 0.02 * insp - 0.025 * rug, -0.01 * pre))
    pescoco_alto(p, cima=-22 * pre + 10 * insp - 4 * rug, esq=3 * math.sin(2 * math.pi * 8 * u) * rug, cab=4 * pre - 8 * rug)
    boca_abre(p, 0.2 * pre + 1.0 * rug)
    abre = 0.62 * pre + 0.08 * rug
    p.asas = asas_ameaca(abre)
    lat = onda_cauda(u, [(9.0, 2, 0.0, 0.9), (3.0, 4, 1.0, 1.2)])
    cauda(p, -10 + 6 * pre, 5.0, lat, onda=[6 * pre * PESO_CAUDA[k] for k in range(7)])
    return p

def f_ameaca_v2(u):
    gelo = CABECA_RUGIDO == "gelo"
    pre = janela(u, 0.0, 0.2); insp = pulso(u, 0.18, 0.28, 0.30, 0.36); rug = pulso(u, 0.34, 0.41, 0.66, 0.76)
    vigia = pre * (1 - janela(u, 0.28, 0.36))                                  # antes do rugido: vigia o ninho
    p = Pose(); base_pe(p, 0.55 * pre)
    for c in PERNAS: p.pata[c]["beta"] += 6 * pre
    if gelo:
        bote = pulso(u, 0.36, 0.44, 0.60, 0.70)                                # UM avanco longo e firme
        p.off += Vector((0, 0.02 * insp - 0.03 * bote, -0.01 * pre))
        olhar = 9 * math.sin(2 * math.pi * 0.9 * u - 0.6) * vigia            # varredura lenta e unica
        pescoco_alto(p, cima=-22 * pre + 8 * insp - 6 * bote, esq=olhar, cab=4 * pre - 9 * bote)
        cabeca_extra(p, cima=-3 * bote, esq=0.3 * olhar, inclina=-0.25 * olhar)
        boca_abre(p, 0.05 * pre + 1.0 * rug, tranco=0.4 * math.sin(2 * math.pi * 6 * u) * rug)
    else:
        bote = pulso(u, 0.38, 0.43, 0.46, 0.51) + pulso(u, 0.52, 0.57, 0.60, 0.66)   # dois botes de blefe
        p.off += Vector((0, 0.02 * insp - 0.022 * rug - 0.018 * bote, -0.01 * pre))
        olhar = 12 * math.sin(2 * math.pi * 1.6 * u) * vigia                  # vigia rapido de um lado ao outro
        tr = tremor_voz(rug, 24, 2.4, u)
        pescoco_alto(p, cima=-22 * pre + 10 * insp - 4 * rug - 5 * bote, esq=olhar + 0.4 * tr, cab=4 * pre - 8 * rug)
        cabeca_extra(p, cima=-5 * bote, esq=0.35 * olhar + sacode(u, 0.64, 0.80, 3.0, 8),
                     inclina=-0.4 * olhar + 7 * math.sin(2 * math.pi * 2.0 * u) * rug)
        garganta(p, tr)
        boca_abre(p, 0.05 * pre + 1.0 * rug, tranco=tr)
    p.asas = asas_ameaca(0.62 * pre + 0.08 * rug)
    lat = onda_cauda(u, [(9.0, 2, 0.0, 0.9), (3.0, 4, 1.0, 1.2)])
    cauda(p, -10 + 6 * pre, 5.0, lat, onda=[6 * pre * PESO_CAUDA[k] for k in range(7)])
    return p

def f_preparar_combate(u):
    """Postura de combate 3 s (laco): frente baixa, asas meio abertas, cabeca baixa e a frente balancando de lado a
    lado (procura brecha), rosnado, cauda chicoteando devagar."""
    p = Pose(); base_pe(p, 0.55)
    lado = math.sin(2 * math.pi * u)
    p.gui = 3 * lado; p.rol = 1.5 * math.sin(2 * math.pi * u + 0.8)
    p.off += Vector((0.005 * lado, 0, -0.006 + 0.003 * math.sin(2 * math.pi * 3 * u)))
    pescoco_alto(p, cima=-22 + 3 * math.sin(2 * math.pi * 2 * u), esq=-9 * lado, cab=4)
    boca_abre(p, 0.15 + 0.1 * max(0.0, math.sin(2 * math.pi * 3 * u)))
    p.asas = asas_ameaca(0.48)
    cauda(p, -8, 5.0, somar([-4 * lado * PESO_CAUDA[k] * 1.6 for k in range(7)], onda_cauda(u, [(7.0, 1, 0.7, 1.0)])),
          onda=[3 * PESO_CAUDA[k] for k in range(7)])
    return p

def asas_ameaca(abre):
    """meia abertura de EXIBICAO (intimidacao/esforco): as asas sobem e abrem para os lados (alto da batida + planeio),
    em vez de cair ate o chao como a mistura dobra->planeio fazia com as asas 1,5x"""
    alto = mistura(asas("Silverwing_Fly_Flap", FA), asas("Silverwing_Fly_Glide", 0.2), 0.35)
    return mistura(asas("Silverwing_Idle", 0.0), alto, abre)

def pose_dormir(u, a=1.0):
    """deitado (agach 1), pescoco curvado para o lado com a cabeca apoiada no chao junto as patas, cauda enrolada"""
    p = Pose(); em_pe(p, agach=AG_DEITADO)
    r = math.sin(2 * math.pi * 2 * u)                                                # respiracao LENTA (2 em 8 s)
    p.off += Vector((0, 0, 0.004 * r * a))
    p.curva["spine_1"] = (1.2 * r * a, 0)
    tique = 3 * pulso(u, 0.62, 0.64, 0.66, 0.7) * a                                  # pequeno movimento ocasional
    pescoco_ao_chao(p, lerp(0.26, 0.045, a) + 0.003 * r * a, esq=34 * a, cab_extra=tique)
    p.asas = asas_descanso(1.0, r * a)
    enrola = [(6.0 + 6.0 * a) * PESO_CAUDA[k_] for k_ in range(7)]
    cauda(p, -16, 5.0, somar(enrola, onda_cauda(u, [(1.2 * a, 1, 0.3, 0.9)])))
    asas_rente_chao(p, 1.0)
    return p
def f_dormir(u): return pose_dormir(u, 1.0)
def f_adormecer(u): return pose_dormir(u, smooth(u))
def f_acordar(u):
    """Acordar 2 s: abre/ergue a cabeca do chao (0-40%), depois levanta o corpo (Levantar)"""
    if u < 0.4: return pose_dormir(0.0, 1 - smooth(u / 0.4))
    return f_agachar(1, 0, AG_DEITADO)((u - 0.4) / 0.6)
def f_ninho_alerta(u):
    """Ninho_Alerta 1,2 s: do deitado direto para alerta (levanta ja de cabeca erguida e asas meio abertas)"""
    p = f_agachar(1, 0)(smooth(min(1, u * 1.25)))
    for n_ in ("shoulder_l", "shoulder_r"): p.extra.pop(n_, None)        # asas vao para a exibicao (sem o rolamento do descanso)
    s_ = janela(u, 0.0, 0.5)
    pescoco_alto(p, cima=-8 + 14 * s_, cab=-5 * s_)
    p.asas = asas_ameaca(0.25 * s_)
    return p

# ---------------------------------------------------------------- voo
def recolhidas(p, fase_batida=0.0, forte=1.0, pender=0.0):
    """patas em postura aerodinamica, SEPARADAS: dianteiras dobradas junto ao peito, traseiras estendidas p/ tras
    sob a cauda; reagem a batida (sobem no golpe descendente); pender (0..1) = pairar/preparacao de pouso"""
    Rb = p.Rb(); ex, ey, ez = Rb @ X, Rb @ Y, Rb @ Z
    b = ponta(fase_batida)              # + asa alta (subida da asa) / - golpe descendente
    for c, pg in PERNAS.items():
        s = pg["s"]
        if not pg["tras"]:
            # dianteiras dobradas contra o peito: punho para tras e para cima, mao voltada para tras
            Prel = ex * s * 0.05 + ey * lerp(0.11, -0.02, pender) + ez * lerp(-0.085, -0.20, pender) + ez * 0.012 * b * forte
            meta = ey * lerp(0.75, 0.2, pender) - ez * lerp(0.65, 1.0, pender) + ex * s * 0.12
            dedos = ey * lerp(0.9, -0.2, pender) - ez * lerp(0.5, 1.0, pender)
        else:
            Prel = ex * s * 0.03 + ey * lerp(0.16, 0.05, pender) + ez * lerp(-0.12, -0.21, pender) + ez * 0.010 * b * forte
            meta = ey * lerp(1.0, 0.25, pender) - ez * lerp(0.3, 1.0, pender) + ex * s * 0.1
            dedos = ey * lerp(1.0, 0.0, pender) - ez * lerp(0.2, 1.0, pender)
        if PERNA_VOO_REL:
            # a partir da pose do PROPRIO modelo (pernas retas): gira a perna inteira para tras em torno do ombro/quadril
            # (dianteiras 40, traseiras 60 graus; menos ao pairar) e dobra um pouco o pe; quase sem esticar a pele
            # quadril/ombro giram POUCO (a coxa encosta no flanco: giro grande rasga a pele em lascas); a dobra fica no
            # joelho/tornozelo
            # pendulo: as patas balancam com ATRASO em relacao a batida (inercia), mais no tornozelo que no quadril
            bl = ponta(fase_batida - (0.22 if not pg["tras"] else 0.28))
            # (usuario 29/10) patas CONTRAIDAS PARA TRAS no voo, rente a barriga (traseiras rumo a cauda, dianteiras contra
            # o peito), mexendo de leve — nao penduradas para baixo; no hover (pender) voltam a ficar mais abaixo
            base = (ANG_VOO_TRAS if pg["tras"] else ANG_VOO_FRENTE) if ANG_VOO_TRAS > 0 else ANG_QUADRIL_VOO
            ang = math.radians(base * (1 - 0.6 * pender) + (2 + 4 * PENDULO) * AMP * 0.6 * bl * forte)
            # giro em torno de +X do corpo (esquerda): baixo -> +Y = TRAS. (Antes era -X: o "para tras" levava a pata
            # para FRENTE — dianteiras pareciam agarrar o ar)
            R = Matrix.Rotation(ang, 3, ex)                 # topo da perna fixo, pe vai para tras
            Jr = H(pg["J"])
            def d(n): return (Rb @ (H(n) - Jr))
            Prel = R @ d(pg["P"]); Krel = R @ d(pg["K"]); Drel = R @ d(pg["D"])
            meta = (Krel - Prel); dedos = (Drel - Krel)
            # RECOLHER (referencia): o alvo do punho/tornozelo vem para perto do corpo -> a IK dobra cotovelo e joelho
            # (antes a pata pendia quase reta); no hover recolhe menos, no mergulho mais (ENCOLHE_EXTRA)
            enc = ENCOLHE if pg["tras"] else ENCOLHE_FRENTE
            k_enc = lerp(enc, 1 - (1 - enc) * 0.45, pender) * ENCOLHE_EXTRA.get("v", 1.0)
            # recolhe puxando para TRAS (antes a dianteira ia para frente = parecia "agarrando" o ar)
            Prel = Prel * k_enc + (Rb @ Y) * 0.015 * (1 - k_enc) * 4
            meta = (Matrix.Rotation(math.radians(25 + 15 * (1 - pender) + 12 * PENDULO * AMP * bl * forte), 3, ex) @ meta)
            dedos = (Matrix.Rotation(math.radians(20 * (1 - pender) + 14 * PENDULO * AMP * ponta(fase_batida - 0.35)), 3, ex) @ dedos)
            p.pata[c] = dict(modo="livre", P=Prel, meta=meta, dedos=dedos)
        else:
            p.pata[c] = dict(modo="livre", P=Prel, meta=meta, dedos=dedos)

FASE_PATA = {"PD_E": 0.0, "PD_D": 2.1, "PT_E": 4.0, "PT_D": 1.2}
def patas_vivas(p, ut, intens=1.0, h=1):
    """voo: pequenos reposicionamentos das patas recolhidas (fases diferentes por pata, sem simetria) e dedos que
    abrem/fecham devagar; ut = tempo lento do clipe (0..1), h = harmonico (inteiro: laco perfeito)"""
    Rb = p.Rb(); ex, ey, ez = Rb @ X, Rb @ Y, Rb @ Z
    for c, sp in p.pata.items():
        if sp.get("modo") != "livre": continue
        f = 2 * math.pi * h * ut + FASE_PATA[c]
        # + abertura lateral lenta e independente (pernas nao ficam coladas uma na outra nem em espelho)
        abre = PERNAS[c]["s"] * 0.004 * intens * (0.6 + 0.4 * math.sin(f + 1.9))
        sp["P"] = sp["P"] + ez * (0.007 * intens * math.sin(f)) + ey * (0.005 * intens * math.sin(2 * f + 0.7)) + ex * abre
        sp["dedos"] = Rax(ex, 12 * intens * math.sin(2 * f + 1.3)) @ sp["dedos"]
        sp["meta"] = Rax(ex, 5 * intens * math.sin(f + 0.4)) @ sp["meta"]

def cauda_ar(p, cima_base, lat, onda_cima=None):
    for i, n in enumerate(CAUDA):
        c = (cima_base if i == 0 else 0.0) + (onda_cima[i] if onda_cima else 0.0)
        p.curva[n] = (c, lat[i] if i < len(lat) else 0.0)

def pescoco_voo(p, cima=0.0, esq=0.0, cab=0.0, onda=None, onda_lat=None):
    # PESC_VOO: graus somados para deitar um pescoco que no repouso esta erguido (modelo em pose neutra); a cabeca
    # compensa 80% para continuar olhando a frente
    # onda/onda_lat: graus extras POR VERTEBRA (movimento secundario com atraso: cada vertebra vira num tempo, nao
    # todas no mesmo angulo); a cabeca desfaz 70% da onda vertical (olhar estabilizado)
    cima = cima + PESC_VOO / 1.05
    ov = onda or [0.0] * len(PESCOCO); ol = onda_lat or [0.0] * len(PESCOCO)
    for i, n in enumerate(PESCOCO): p.curva[n] = (2 + cima * (0.25 + 0.1 * i) + ov[i], esq * (0.25 + 0.1 * i) + ol[i])
    p.curva["head"] = (cab - 2 - cima * 0.2 - PESC_VOO * 0.8 - 0.7 * sum(ov), esq * 0.3 - 0.4 * sum(ol))

def onda_pescoco(w, amp, atraso=0.07, base=0.16):
    """onda vertical da batida subindo pelo pescoco (base -> cabeca), cada vertebra com atraso"""
    return [amp * (0.8 + 0.2 * i) * ponta(w - base - atraso * i) for i in range(len(PESCOCO))]

def f_voo(u, nb=1, ut=None):
    """nb batidas por clipe; ut = tempo lento (cauda/patas). Sem ut (transicoes/mordida) = comportamento antigo."""
    w = u * nb; p = Pose(); b = ponta(w)
    p.off = Vector((0, 0, -0.016 * b)); p.arf = 1.5 * b
    p.curva["spine_1"] = (1.5 * b, 0)                                    # torax reage ao esforco da batida
    p.asas = asas("Silverwing_Fly_Flap", w)
    recolhidas(p, w)
    pescoco_voo(p, cima=2.5 * b, cab=-2.5 * b)                         # cabeca estavel: compensa o balanco
    if ut is None:
        cauda_ar(p, 2, [(0.6 + 1.0 * k) * math.sin(2 * math.pi * w - 0.55 * k) for k in range(7)],
                 [5 * (0.5 + 0.12 * k) * ponta(w - 0.09 * k) for k in range(7)])
        return p
    # CORPO VIVO (referencia): a batida descendente ERGUE o corpo (atraso ~0,12 ciclo), o tronco arfa e flexiona,
    # ombros/quadril rolam um pouco de um lado ao outro ao longo do clipe, o pescoco segue o tronco com atraso e a
    # cabeca estabiliza so em parte (acompanha o movimento, nao fica 'pregada')
    bc = ponta(w - 0.12); bp = ponta(w - 0.22)
    p.off = Vector((0, 0.012 * bp * AMP, -0.05 * bc * AMP)); p.arf = 5 * bc * AMP
    p.rol = (4.5 * math.sin(2 * math.pi * ut + 0.4) + 1.5 * math.sin(2 * math.pi * 3 * ut)) * AMP
    p.gui = 2.5 * math.sin(2 * math.pi * ut - 0.6) * AMP
    p.curva["spine_1"] = (5 * b * AMP, 1.5 * math.sin(2 * math.pi * ut) * AMP); p.curva["spine_0"] = (-3 * bc * AMP, -1.5 * math.sin(2 * math.pi * ut) * AMP)
    # pescoco: onda da batida sobe vertebra por vertebra (atraso) + olhar lento que varre os lados; a cabeca
    # estabiliza a onda e faz pequenos ajustes proprios (nao oscilacao mecanica: harmonicos lentos do clipe)
    olhar = (-5 * math.sin(2 * math.pi * ut + 0.4) + 3 * math.sin(2 * math.pi * 2 * ut + 1.0)) * AMP
    pescoco_voo(p, cima=6 * bp * AMP, esq=olhar, cab=-5 * bp * AMP * 0.6 + 3 * math.sin(2 * math.pi * 2 * ut + 2.1),
                onda=onda_pescoco(w, 2.2 * AMP), onda_lat=[-0.12 * olhar * k for k in (0.2, 0.5, 0.8)])
    recolhidas(p, w, forte=1.4)
    patas_vivas(p, ut, 1.9 * AMP * 0.7)
    # cauda: S lateral lento (contrapeso do rolamento) + chicote vertical de cada batida, maior para a ponta
    lat = onda_cauda(ut, [(13.0, 1, 0.0, 0.95), (5.0, 2, 1.4, 1.25), (2.0, nb, 0.6, 0.7)])
    vert = somar([9 * (0.45 + 0.12 * k) * ponta(w - 0.16 - 0.07 * k) for k in range(7)], onda_cauda(ut, [(2.5, 1, 2.2, 0.8)]))
    cauda_ar(p, 2, lat, vert)
    return p

def f_voo_rapido(u, nb=5, ut=None):
    """VOO RAPIDO (estado Voo_Rapido): corpo alongado (pescoco esticado a frente e mais baixo), patas mais recolhidas,
    movimento secundario reduzido, cauda alinhada; batidas mais frequentes (5 por clipe em vez de 4)"""
    ut = u if ut is None else ut
    w = u * nb; p = Pose(); b = ponta(w); bc = ponta(w - 0.12); bp = ponta(w - 0.22)
    G = AMP * 0.5
    p.off = Vector((0, 0.008 * bp * G, -0.04 * bc * G)); p.arf = -3 + 4 * bc * G
    p.rol = 2.5 * math.sin(2 * math.pi * ut + 0.4) * G; p.gui = 1.2 * math.sin(2 * math.pi * ut - 0.6) * G
    p.curva["spine_1"] = (4 * b * G, 0); p.curva["spine_0"] = (-2 * bc * G, 0)
    p.asas = asas("Silverwing_Fly_Flap", w)
    ENCOLHE_EXTRA["v"] = 0.92
    recolhidas(p, w, forte=0.9)
    ENCOLHE_EXTRA["v"] = 1.0
    patas_vivas(p, ut, 0.9)
    pescoco_voo(p, cima=-10 + 3 * bp * G, esq=-2.5 * math.sin(2 * math.pi * ut + 0.4) * G, cab=6,
                onda=onda_pescoco(w, 1.0 * G))
    lat = onda_cauda(ut, [(5.0, 1, 0.0, 0.9), (2.0, 2, 1.4, 1.2)])
    vert = [4 * (0.45 + 0.12 * k) * ponta(w - 0.16 - 0.07 * k) for k in range(7)]
    cauda_ar(p, 1, lat, vert)
    return p

def f_pairar(u, nb=1, ut=None):        # voo estacionario: corpo inclinado, batidas de sustentacao, correcoes
    w = u * nb; p = Pose(); b = ponta(w)
    p.arf = 32 + 3 * b; p.off = Vector((0, 0.02, -0.03 * b + 0.02))
    p.curva["spine_1"] = (2.5 * b, 0); p.curva["spine_0"] = (-1.5 * b, 0)  # torax/quadril compensam o esforco
    p.asas = asas("Silverwing_Fly_Flap", w)
    for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): p.extra[n] = Rax(p.Rb() @ X, 22)   # plano da batida mais horizontal
    recolhidas(p, w, forte=1.6, pender=0.75)
    uu = w if ut is None else ut
    pescoco_voo(p, cima=-30 - 3 * b, esq=3 * math.sin(2 * math.pi * uu), cab=-p.arf * 0.2)
    if ut is None:
        lat = [(0.8 + 1.2 * k) * (math.sin(2 * math.pi * w - 0.5 * k) * 0.7 + 0.4 * math.sin(6 * math.pi * w + 0.9 - 0.4 * k)) for k in range(7)]
        cauda_ar(p, -14, lat, [3 * b * (0.4 + 0.15 * k) for k in range(7)])
        return p
    # HOVER (referencia): corpo bem mais vertical, batidas num plano quase horizontal (ombros giram junto), o corpo
    # sobe a cada golpe, patas penduradas balancando, cauda caida fazendo S lento; cabeca olha para frente
    bc = ponta(w - 0.12); bp = ponta(w - 0.24)
    p.arf = 30 + 20 * PENDULO + 4 * bc * AMP
    p.off = Vector((0, 0.03, -0.06 * bc * AMP + 0.03))
    p.rol = 3.5 * math.sin(2 * math.pi * ut + 1.0) * AMP; p.gui = 3 * math.sin(2 * math.pi * ut - 0.3) * AMP
    p.curva["spine_1"] = (5 * b * AMP, 0); p.curva["spine_0"] = (-3 * bc * AMP, 2 * math.sin(2 * math.pi * ut) * AMP)
    for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): p.extra[n] = Rax(p.Rb() @ X, 22 + 14 * PENDULO)
    recolhidas(p, w, forte=1.8, pender=0.75 + 0.25 * PENDULO)
    patas_vivas(p, ut, 2.0 * AMP * 0.7)
    pescoco_voo(p, cima=-30 - 18 * PENDULO + 4 * bp * AMP,
                esq=(6 * math.sin(2 * math.pi * ut) + 3 * math.sin(2 * math.pi * 3 * ut + 0.5)) * AMP,
                cab=-p.arf * (0.2 + 0.25 * PENDULO) - 4 * bp * AMP * 0.6, onda=onda_pescoco(w, 1.6 * AMP))
    lat = onda_cauda(ut, [(12.0, 1, 0.5, 1.0), (5.5, 2, 2.0, 1.3), (2.2, 3, 0.9, 1.6)])
    vert = somar([6 * (0.45 + 0.12 * k) * ponta(w - 0.16 - 0.07 * k) for k in range(7)], onda_cauda(ut, [(3.0, 1, 1.0, 0.9)]))
    # (10/11, Sombrio: CAUDA_PAIRAR) com os clipes na convencao certa a cauda do hover caia a prumo (~85 graus, 18,5 studs
    # abaixo do quadril) e entrava no chao no Eclipse (corpo a 24 do chao) e no voo parado baixo; CAUDA_PAIRAR = base da
    # cauda (graus) -> segue mais a linha do corpo inclinado. Sem a variavel: como antes.
    cauda_ar(p, CAUDA_PAIRAR if CAUDA_PAIRAR is not None else -14 - 14 * PENDULO, lat, vert)
    return p
CAUDA_PAIRAR = float(os.environ["CAUDA_PAIRAR"]) if os.environ.get("CAUDA_PAIRAR") else None

def f_subida(u, nb=1, ut=None):
    w = u * nb; p = Pose(); b = ponta(w)
    p.off = Vector((0, 0, -0.02 * b)); p.arf = 2 * b
    p.asas = asas("Silverwing_Fly_Flap", w)
    for n in ("shoulder_l", "shoulder_r"): p.extra[n] = Rax(p.Rb() @ X, 10)     # ombros puxam a batida para frente
    p.curva["spine_0"] = (4, 0); p.curva["spine_1"] = (6 + 2 * b, 0)             # torax se eleva e reage a batida
    recolhidas(p, w, forte=1.3); [p.pata[c].update(P=p.pata[c]["P"] + Vector((0, 0.02, 0.01))) for c in p.pata]
    pescoco_voo(p, cima=26 + 3 * b, cab=6)
    uu = w if ut is None else ut
    if ut is not None:
        # subida com esforco: golpes fortes erguem o tronco, pescoco estica para cima e reage com atraso
        bc = ponta(w - 0.12); bp = ponta(w - 0.22)
        p.off = Vector((0, 0.01 * bp, -0.055 * bc)); p.arf = 6 + 6 * bc
        p.rol = 3 * math.sin(2 * math.pi * ut + 0.4)
        p.curva["spine_1"] = (8 + 5 * b, 0); p.curva["spine_0"] = (4 - 3 * bc, 0)
        recolhidas(p, w, forte=1.6); [p.pata[c].update(P=p.pata[c]["P"] + (p.Rb() @ Y) * 0.02) for c in p.pata]
        pescoco_voo(p, cima=30 + 6 * bp, esq=4 * math.sin(2 * math.pi * ut), cab=4 - 5 * bp, onda=onda_pescoco(w, 3.0))
        patas_vivas(p, ut, 1.6)
    # subindo: a cauda abaixa (estabiliza a inclinacao) e ondula pouco
    lat = onda_cauda(uu, [(7.0, 1, 0.3, 0.9), (3.0, 2, 1.6, 1.2)]) if ut is not None else [(0.5 + 0.8 * k) * math.sin(2 * math.pi * w - 0.6 * k) for k in range(7)]
    cauda_ar(p, -5, lat, [3.5 * ponta(w - 0.1 * k) - 1.5 - (2.0 * PESO_CAUDA[k] if ut is not None else 0) for k in range(7)])
    return p

def f_descida(u):                     # descida suave: asas semi-abertas planando, cabeca/pescoco para baixo
    p = Pose()
    p.asas = mistura(asas("Silverwing_Fly_Glide", u), asas("Silverwing_Fly_Flap", 0.35), 0.25)
    p.curva["spine_1"] = (-3, 0); p.arf = -10                                   # tronco inclina para a descida
    p.rol = 5 * math.sin(2 * math.pi * u + 0.3); p.gui = 3 * math.sin(2 * math.pi * u - 0.8)   # pequenas correcoes de rumo
    p.off = Vector((0, 0, 0.012 * math.sin(2 * math.pi * 2 * u)))
    recolhidas(p, 0.35); patas_vivas(p, u, 1.4)
    pescoco_voo(p, cima=-26 + 4 * math.sin(2 * math.pi * 2 * u + 0.6), esq=-4 * math.sin(2 * math.pi * u + 0.3), cab=-8)
    # descendo: a cauda SOBE um pouco em relacao ao corpo (alinha com a trajetoria) e corrige devagar
    cauda_ar(p, 4, onda_cauda(u, [(8.0, 1, 0.0, 0.95), (3.5, 2, 1.2, 1.3)]),
             somar([2.0 * PESO_CAUDA[k] for k in range(7)], onda_cauda(u, [(1.8, 2, 0.4, 0.8)])))
    return p

def f_planeio(u):
    p = Pose()
    r = math.sin(2 * math.pi * 2 * u)                                            # respiracao no planeio (2 por clipe)
    # planeio vivo: corpo flutua na corrente (sobe/desce, rola e corrige o rumo devagar), torax respira, cabeca olha
    p.off = Vector((0, 0, 0.02 * math.sin(2 * math.pi * u) + 0.008 * math.sin(2 * math.pi * 3 * u + 1.0)))
    p.rol = 6 * math.sin(2 * math.pi * u + 0.5) + 2 * math.sin(2 * math.pi * 3 * u)
    p.gui = 3 * math.sin(2 * math.pi * u - 0.4); p.arf = 2 * math.sin(2 * math.pi * 2 * u + 0.9)
    p.curva["spine_1"] = (2.5 * r, 0); p.curva["spine_0"] = (0, -2 * math.sin(2 * math.pi * u + 0.5))
    p.asas = asas("Silverwing_Fly_Glide", u)
    # pequenas correcoes alares (cada asa no seu tempo) + PLANEIO_ABAIXA: baixa as duas pontas (asas estendidas para
    # os lados, nao apontadas para cima)
    Rb = p.Rb()
    p.extra["shoulder_l"] = Rax(Rb @ Y, PLANEIO_ABAIXA + 2.0 * math.sin(2 * math.pi * 2 * u + 0.3))
    p.extra["shoulder_r"] = Rax(Rb @ Y, -(PLANEIO_ABAIXA + 2.0 * math.sin(2 * math.pi * 2 * u + 1.9)))
    recolhidas(p, 0.3); patas_vivas(p, u, 1.6)
    pescoco_voo(p, cima=4 + 5 * math.sin(2 * math.pi * u + 0.8), esq=-7 * math.sin(2 * math.pi * u + 0.5) + 3 * math.sin(2 * math.pi * 2 * u))
    cauda_ar(p, 1, onda_cauda(u, [(9.0, 1, 0.0, 0.9), (3.5, 2, 1.0, 1.2), (1.3, 3, 2.3, 1.5)]),
             onda_cauda(u, [(1.8, 2, 0.0, 0.7), (1.0, 1, 1.5, 0.9)]))
    return p

def f_curva(lado):
    sg = 1 if lado == "E" else -1
    def fn(u):
        p = Pose()
        p.asas = asas("Silverwing_Fly_Glide", u)
        Rb = p.Rb()
        p.extra["shoulder_l"] = Rax(Rb @ Y, (9 + 3 * (sg > 0)) * sg); p.extra["shoulder_r"] = Rax(Rb @ Y, (9 + 3 * (sg < 0)) * sg)  # asa interna desce mais
        p.rol = 4 * sg; p.curva["spine_0"] = (0, 4 * sg)                         # quadril acompanha a inclinacao
        recolhidas(p, 0.3)
        for c in p.pata:                                                         # correcoes assimetricas das patas
            interna = (PERNAS[c]["s"] == sg)
            p.pata[c]["P"] = p.pata[c]["P"] + (Rb @ X) * 0.012 * sg + (Rb @ Z) * (0.012 if interna else -0.004)
        patas_vivas(p, u, 0.8)
        pescoco_voo(p, cima=3, esq=22 * sg, cab=4)
        p.curva["spine_1"] = (0, 5 * sg)
        # cauda compensa a curva: base segue o tronco, meio acompanha, ponta abre para fora com atraso + correcoes
        base = [-sg * (3 + 3.0 * k) for k in range(7)]          # constante: a rampa antiga quebrava o laco (10,5 graus)
        cauda_ar(p, 1, somar(base, onda_cauda(u, [(2.5, 2, 0.0, 1.1), (1.2, 3, 1.4, 1.4)])), onda_cauda(u, [(1.5, 1, 0.6, 0.9)]))
        return p
    return fn

def f_mergulho(u):
    p = Pose()
    # MERGULHO (referencia): asas bem mais fechadas e varridas para tras (menos arrasto), sem atravessar o corpo;
    # patas ainda mais compactas
    p.asas = mistura(asas("Silverwing_Fly_Glide", u), asas("Silverwing_Idle", 0.0), 0.66)
    Rb = p.Rb(); p.arf = -6
    for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): p.extra[n] = Rax(Rb @ Z, -18 * s_)
    ENCOLHE_EXTRA["v"] = 0.95
    recolhidas(p, 0.3); [p.pata[c].update(P=p.pata[c]["P"] + (Rb @ Y) * 0.03 + (Rb @ Z) * 0.02) for c in p.pata]
    ENCOLHE_EXTRA["v"] = 1.0
    patas_vivas(p, u, 0.5, h=2)
    pescoco_voo(p, cima=-4, cab=-3)
    # mergulho rapido: cauda alinhada (aerodinamica), so pequenas correcoes rapidas na ponta
    cauda_ar(p, 0, onda_cauda(u, [(2.0, 2, 0.0, 0.8), (1.0, 4, 1.0, 1.2)]), [1.5 * PESO_CAUDA[k] for k in range(7)])
    return p


# ---------------------------------------------------------------- sistema universal de animacoes (01/11): comportamento
# Toda forma regional usa as MESMAS funcoes (proporcoes vem do esqueleto encaixado; personalidade por variaveis de
# ambiente). Antecipacao -> acao -> reacao do corpo -> movimento secundario (cauda/asas) -> recuperacao.
# ---------------------------------------------------------------- CABECA DOS RUGIDOS (usuario 03/11)
# "diferencie o movimento da cabeca dos dragoes em cada rugido, conforme o tipo de rugido e a situacao": cada rugido
# ganha uma linguagem de cabeca PROPRIA (giro/inclinacao/sacudida sobre o pescoco) e por forma: fogo = agressivo,
# sacode e da trancos; gelo = frio, movimentos lentos, longos e estaveis. CABECA_RUGIDO vazio (Sombrio, por ora) =
# clipes exatamente como antes.
CABECA_RUGIDO = os.environ.get("CABECA_RUGIDO", "")
def _lim(x): return max(0.0, min(1.0, x))
def cabeca_extra(p, cima=0.0, esq=0.0, inclina=0.0):
    """giro proprio da CABECA (chamar depois de pescoco_alto/voo/ao_chao): cima/esq somam na curva da cabeca;
    inclina = rolagem em torno do focinho (+ = orelha esquerda desce)"""
    c, e = p.curva.get("head", (0.0, 0.0)); p.curva["head"] = (c + cima, e + esq)
    if abs(inclina) > 0.01:
        frente_, _, _ = eixos(p); R = Rax(frente_, inclina)
        p.extra["head"] = R @ p.extra["head"] if "head" in p.extra else R
def sacode(u, a, b, ciclos, amp):
    """sacudida amortecida de a a b (ciclos dentro da janela): comeca forte e morre suave"""
    if u <= a or u >= b: return 0.0
    t = (u - a) / (b - a)
    return amp * math.sin(2 * math.pi * ciclos * t) * (1 - t) ** 1.6 * smooth(min(1.0, t * 5))

def f_rugido_territorial(u):
    """Rugido territorial 4,2 s: firma as patas, ergue o pescoco ao alto, enche o peito, abre as asas pela metade e
    solta um rugido LONGO para o ceu (cabeca sobe), tremor da garganta, cauda erguida varrendo; recupera devagar."""
    firma = janela(u, 0.0, 0.15); insp = pulso(u, 0.08, 0.28, 0.30, 0.38); rug = pulso(u, 0.30, 0.40, 0.82, 0.95)
    p = Pose(); em_pe(p)
    for c in PERNAS: p.pata[c]["beta"] += 4 * firma
    trem = math.sin(2 * math.pi * 22 * u) * rug
    p.off += Vector((0, 0.012 * insp - 0.006 * rug, 0.010 * insp + 0.004 * rug)); p.arf += 4 * insp + 6 * rug
    p.curva["spine_1"] = (6 * insp + 3 * rug, 0); p.curva["spine_0"] = (-2 * insp, 0)
    pescoco_alto(p, cima=14 * firma + 6 * insp + 4 * rug, esq=2 * trem, cab=4 * insp + 14 * rug + 1.5 * trem)
    boca_abre(p, 0.10 * insp + 1.0 * rug, tranco=trem)
    p.asas = asas_ameaca(0.5 * firma + 0.1 * rug)
    lat = onda_cauda(u, [(8.0, 1, 0.3, 0.9), (3.0, 3, 1.1, 1.2)])
    cauda(p, -12 + 8 * rug, 5.0, lat, onda=[6 * rug * PESO_CAUDA[k] for k in range(7)])
    if CABECA_RUGIDO == "fogo":
        # proclama o territorio: varre o horizonte de um lado ao outro durante o rugido longo (cabeca ao alto),
        # inclina para o lado da varredura e fecha com uma sacudida forte de cabeca
        varre = 13 * math.sin(2 * math.pi * 0.9 * (u - 0.40)) * rug
        cabeca_extra(p, cima=3 * rug, esq=varre + sacode(u, 0.80, 0.97, 3.5, 7), inclina=0.35 * varre)
    elif CABECA_RUGIDO == "gelo":
        # majestoso: UM arco lento e continuo pelo horizonte (sem sacudir), cabeca subindo devagar ate o fim do folego
        arco = 9 * (2 * smooth(_lim((u - 0.36) / 0.52)) - 1) * rug
        cabeca_extra(p, cima=5 * smooth(_lim((u - 0.36) / 0.5)) * rug, esq=arco, inclina=-0.12 * arco)
    return p

def f_intimidar(u):
    """Intimidacao 3,6 s (laco): encara o adversario de cabeca BAIXA, mostra os dentes (labio entreaberto), dois
    grunhidos curtos, asas tensas meio abertas tremendo, peso a frente, cauda chicoteando de lado."""
    p = Pose(); base_pe(p, 0.35)
    gr = max(0.0, math.sin(2 * math.pi * 2 * u)) ** 3                         # 2 grunhidos por ciclo
    lado = math.sin(2 * math.pi * u)
    p.off += Vector((0.004 * lado, -0.006 * gr, -0.004 + 0.003 * math.sin(2 * math.pi * 4 * u)))
    p.arf += 1.5 * gr; p.rol = 1.2 * lado
    pescoco_alto(p, cima=-20 - 3 * gr, esq=-4 * lado, cab=6 + 2 * gr)
    boca_abre(p, 0.16 + 0.22 * gr, tranco=gr)
    p.asas = asas_ameaca(0.40 + 0.03 * math.sin(2 * math.pi * 6 * u))
    lat = onda_cauda(u, [(12.0, 1, 0.0, 0.9), (4.0, 3, 0.7, 1.2)])
    cauda(p, -8, 5.0, lat, onda=[3 * PESO_CAUDA[k] for k in range(7)])
    return p

def f_curiosidade(u):
    """Curiosidade 5 s: nota algo (vira e ergue a cabeca), INCLINA a cabeca de lado, aproxima o focinho baixo
    farejando, inclina para o outro lado, recua e volta a postura."""
    nota = pulso(u, 0.0, 0.12, 0.85, 1.0); inc1 = pulso(u, 0.15, 0.25, 0.32, 0.4); aprox = pulso(u, 0.38, 0.5, 0.62, 0.72)
    inc2 = pulso(u, 0.68, 0.76, 0.84, 0.9)
    fare = max(0.0, math.sin(2 * math.pi * 14 * u)) * aprox
    p = Pose(); em_pe(p)
    p.off += Vector((0, -0.02 * aprox, -0.006 * aprox)); p.arf += -3 * aprox
    pescoco_alto(p, cima=-10 + 6 * nota - 16 * aprox + 0.6 * fare, esq=14 * nota - 6 * inc2, cab=-2 * nota + 8 * aprox)
    frente_, _, _ = eixos(p)
    p.extra["head"] = Rax(frente_, 22 * inc1 - 18 * inc2)                  # inclina a cabeca (eixo do focinho)
    boca_abre(p, 0.06 * fare)
    p.asas = asas("Silverwing_Idle", u)
    cauda(p, -14, 5.0, onda_cauda(u, [(5.0, 1, 0.4, 0.95), (2.5, 3, 0.9, 1.3)]), onda=[3 * nota * PESO_CAUDA[k] for k in range(7)])
    return p

def f_dano(forte=False, ar=False):
    """Reacao a dano (leve 0,6 s / forte 1,1 s): tranco proporcional (corpo recua e rola para o lado do golpe), pescoco
    encolhe, olhos/boca reagem, asas dao um espasmo, cauda contrai; recupera sem travar o controle."""
    k = 1.0 if forte else 0.45
    def fn(u):
        hit = pulso(u, 0.0, 0.10, 0.18, 0.75 if forte else 0.6)
        if ar:
            p = f_pairar(u * 2 % 1.0)
            pescoco_voo(p, cima=-30 + 10 * k * hit, cab=-p.arf * 0.2 - 8 * k * hit)
            p.arf += 8 * k * hit
        else:
            p = Pose(); em_pe(p)
            p.off += Vector((0.010 * k * hit, 0.025 * k * hit, -0.008 * k * hit)); p.arf += 6 * k * hit; p.rol = -6 * k * hit
            pescoco_alto(p, cima=-10 + 12 * k * hit, esq=-8 * k * hit, cab=-10 * k * hit)
            p.asas = asas_ameaca(0.25 * k * hit)
            cauda(p, -15 + 10 * k * hit, 5.0, onda_cauda(u, [(3.0, 1, 0.0, 1.0)]), onda=[8 * k * hit * PESO_CAUDA[i] for i in range(7)])
        p.curva["spine_1"] = (p.curva.get("spine_1", (0, 0))[0] - 5 * k * hit, 0)
        boca_abre(p, 0.35 * k * hit)
        return p
    return fn

# MERGULHO PICADO (usuario 09/11: "no mergulho o dragao va rapidamente ao chao, que junte as asas e desca com tudo"):
# excecao pedida a regra de 06/11 (asas nunca dobradas) SO para este clipe: asas JUNTAS ao corpo, varridas para tras,
# cotovelo e punho fechados e dedos em leque fechado (giros rigidos das asas armadas: a membrana nao torce); pescoco e
# cabeca esticados a frente, patas bem recolhidas, cauda reta com tremor rapido. A inclinacao de bico para baixo vem do
# motor de voo (pitch do corpo), nao do clipe. P_PICADO por env ajusta a pose.
P_PICADO = dict(ergue=-14, recua=88, cotovelo=-86, punho=118, leque=1.0)  # (v3 09/11, usuario: "de cabeca para baixo, com as asas
# fechadas" = bico para o chao) variante F1: asas FECHADAS coladas ao corpo, sem tremor
# (v2 E3 enrolada: ergue -6, recua 88, cotovelo -98, punho 132 com EMBOLA=1)
# (variante A anterior: ergue -18, recua 85, cotovelo -80, punho 110 = coladas, varridas para tras)
if os.environ.get("P_PICADO"):
    import json as _js3; P_PICADO.update(_js3.loads(os.environ["P_PICADO"]))
# (v2, usuario 09/11: "eu quero que ele va rapidamente de cabeca, meio embolado com as asas, e quando tiver se aproximando
# do chao volte a bater as asas"): EMBOLA (0..1) = asas ENROLADAS em volta do corpo (nao varridas para tras), um pouco
# assimetricas e tremendo no vento (lado direito defasado), cauda curvada, pescoco esticado de cabeca para a queda.
# A frenagem batendo asas perto do chao e do motor de voo (troca para o Pairar/Subida), nao deste clipe.
EMBOLA = float(os.environ.get("EMBOLA", "0"))                  # (v3) padrao = asas fechadas e paradas; 1 = embolado (v2)
def f_mergulho_picado(u):
    p = Pose()
    trem = math.sin(2 * math.pi * 4 * u)                              # vibracao do ar nas asas fechadas
    if EMBOLA > 0:
        tr2 = math.sin(2 * math.pi * 4 * u + 1.7)
        def var(t, s):                                                # asa enrolada que tremula (cotovelo/punho batem no vento)
            return {k: v + {"ergue": 3.0 * t + s * 5 * EMBOLA, "cotovelo": 6.0 * t * EMBOLA, "punho": -5.0 * t * EMBOLA}.get(k, 0.0)
                    for k, v in P_PICADO.items()}
        p.asas = asas_armadas(0.0, 0.0, Pfix=var(trem, 0), Plado={"l": var(trem, 0), "r": var(tr2, 1)})
    else:
        p.asas = asas_armadas(0.0, 0.0, Pfix={k: v + (1.5 * trem if k == "ergue" else 0.0) for k, v in P_PICADO.items()})
    p.arf = -8
    ENCOLHE_EXTRA["v"] = 0.85 - 0.15 * EMBOLA
    recolhidas(p, 0.3)
    ENCOLHE_EXTRA["v"] = 1.0
    patas_vivas(p, u, 0.25, h=2)
    pescoco_voo(p, cima=-10 - 6 * EMBOLA, cab=-6 - 4 * EMBOLA)
    cauda_ar(p, 2 - 16 * EMBOLA, onda_cauda(u, [(3.0, 4, 0.0, 0.5 + 0.6 * EMBOLA)]), [(0.8 + 1.2 * EMBOLA) * PESO_CAUDA[k] for k in range(7)])
    return p

def f_mergulho_saida(u):
    """Recuperacao do mergulho 1,2 s: abre as asas (frenagem do ar), ergue o peito e o pescoco e passa a bater asas
    (Voo); patas descem um pouco com a desaceleracao."""
    t = smooth(u); flare = pulso(u, 0.1, 0.35, 0.55, 0.95)
    p = mistura_pose(f_mergulho(u), f_voo(u, 1, u), t)
    p.arf += 14 * flare
    return p

# MERGULHO V2 (10/11, SO o Sombrio liga com MERGULHO_V2=1; sem a variavel nada muda): "o rabo pra cima a cabeca pra cima
# e o corpo pra baixo" (usuario). Causa medida no Studio: os JSON tocavam ESPELHADOS (osso do jogo = osso do Blender
# girado 180 no Y) -> o exportador converte com CONVENCAO_ROBLOX=giro180y. Clipes proprios da manobra, pensados para o
# pitch da RAIZ vindo do motor (entrada ~0 -> -80, queda -84, freio volta a 0 em curva continua):
#  Mergulho_Entrada: antecipacao curta (a asa sobe meia batida, sem empinar) e recolhe em SEQUENCIA ombro -> cotovelo ->
#    punho -> dedos ate a pose do picado; patas encolhem; pescoco alonga na linha do corpo.
#  Mergulho_Picado (V2): silhueta longitudinal focinho-pescoco-peito-quadril-cauda; patas traseiras coladas ao ventre.
#  Mergulho_Freio: abre as asas em sequencia, 2 batidas fortes de frenagem e termina na pose do Pairar (corpo erguido,
#    cauda caida atras/abaixo); pescoco e cauda seguem com atraso amortecido (sem chicote).
MERG_V2 = os.environ.get("MERGULHO_V2") == "1"
PIC2 = dict(arf=-6, cima=-22, cab=4, enc=0.62, cauda=0.0, peito=-3)
if os.environ.get("PIC2"):
    import json as _js4; PIC2.update(_js4.loads(os.environ["PIC2"]))
GRUPOS_ASA = (("shoulder", "wing_1"), ("wing_2",), ("wing_3",), ("wing_4", "wing_5", "wing_tip", "wing_feather"))
def _grupo_asa(n):
    for i, g in enumerate(GRUPOS_ASA):
        if n.startswith(g) or (n[:-2] in g): return i
    return 3
def _mistura_asas_escalonada(a, b, ts):
    """mistura por grupo (ombro, cotovelo, punho, dedos) com tempos proprios: recolhe/abre em sequencia"""
    out = {}
    for n in a:
        t = ts[_grupo_asa(n)]
        out[n] = Matrix.Translation(a[n].translation.lerp(b[n].translation, t)) @ a[n].to_quaternion().slerp(b[n].to_quaternion(), t).to_matrix().to_4x4()
    return out
def _lerp_curvas(p, a, b, nomes, t):
    for n_ in nomes:
        ca, cb = a.curva.get(n_, (0, 0)), b.curva.get(n_, (0, 0)); p.curva[n_] = (lerp(ca[0], cb[0], t), lerp(ca[1], cb[1], t))
def f_picado_v2(u):
    p = Pose()
    trem = math.sin(2 * math.pi * 4 * u)
    p.asas = asas_armadas(0.0, 0.0, Pfix={k: v + (1.0 * trem if k == "ergue" else 0.0) for k, v in P_PICADO.items()})
    p.arf = PIC2["arf"]
    p.curva["spine_1"] = (PIC2["peito"], 0); p.curva["spine_0"] = (PIC2["peito"] * 0.6, 0)
    ENCOLHE_EXTRA["v"] = PIC2["enc"]
    recolhidas(p, 0.3)
    ENCOLHE_EXTRA["v"] = 1.0
    patas_vivas(p, u, 0.12, h=2)
    pescoco_voo(p, cima=PIC2["cima"], cab=PIC2["cab"])
    cauda_ar(p, PIC2["cauda"], onda_cauda(u, [(1.2, 4, 0.0, 0.5)]), [0.5 * PESO_CAUDA[k] for k in range(7)])
    return p
def f_mergulho_entrada(u):
    """0,55 s: asa sobe meia batida (antecipacao) e recolhe em sequencia ate o picado"""
    fb = (FA + 0.5) % 1.0; sobe = (FA - fb) % 1.0
    a = f_voo(fb + sobe * min(1.0, u / 0.35), 1, u * 0.2)
    b = f_picado_v2(u)
    p = mistura_pose(a, b, janela(u, 0.12, 0.85))
    p.asas = _mistura_asas_escalonada(a.asas, b.asas, [janela(u, 0.22, 0.62), janela(u, 0.30, 0.72), janela(u, 0.38, 0.84), janela(u, 0.46, 0.96)])
    _lerp_curvas(p, a, b, PESCOCO + ["head"], janela(u, 0.05, 0.70))
    _lerp_curvas(p, a, b, CAUDA, janela(u, 0.25, 1.0))
    return p
def f_mergulho_freio(u):
    """1,2 s: abre em sequencia (0-0,32), batidas fortes (2) e chega no Pairar; corpo ergue com o freio"""
    a = f_picado_v2(u)
    w = FA + max(0.0, u - 0.30) / 0.70 * 2.0                      # 1o golpe comeca com a asa no alto
    b = f_pairar(w, 1, u)
    p = mistura_pose(a, b, janela(u, 0.04, 0.78))
    p.asas = _mistura_asas_escalonada(a.asas, b.asas, [janela(u, 0.0, 0.24), janela(u, 0.05, 0.28), janela(u, 0.09, 0.31), janela(u, 0.13, 0.34)])
    _lerp_curvas(p, a, b, PESCOCO + ["head"], janela(u, 0.10, 0.75))
    tc = janela(u, 0.22, 0.95)                                    # cauda: atraso amortecido, sem chicote
    for k_, n_ in enumerate(CAUDA):
        ca, cb = a.curva.get(n_, (0, 0)), b.curva.get(n_, (0, 0)); p.curva[n_] = (lerp(ca[0], cb[0], tc), lerp(ca[1], cb[1] * 0.6, tc))
    return p

# ---------------------------------------------------------------- transicoes
def mistura_pose(a, b, t):
    """mistura duas Poses (corpo, curvas, asas, patas)"""
    p = Pose(); p.off = a.off.lerp(b.off, t); p.arf = lerp(a.arf, b.arf, t); p.rol = lerp(a.rol, b.rol, t); p.gui = lerp(a.gui, b.gui, t)
    for n in set(a.curva) | set(b.curva):
        ca, cb = a.curva.get(n, (0, 0)), b.curva.get(n, (0, 0)); p.curva[n] = (lerp(ca[0], cb[0], t), lerp(ca[1], cb[1], t))
    p.asas = mistura(a.asas, b.asas, t) if a.asas and b.asas else (a.asas or b.asas)
    for n in set(a.extra) | set(b.extra):
        ea = a.extra.get(n, Matrix.Identity(3)).to_quaternion(); eb = b.extra.get(n, Matrix.Identity(3)).to_quaternion()
        p.extra[n] = ea.slerp(eb, t).to_matrix()
    # patas: posicoes absolutas resolvidas nas duas poses e interpoladas
    Wa, _ = resolver(a); Wb, _ = resolver(b)
    for c, pg in PERNAS.items():
        J = None
        def alvo(W):
            P = W[pg["P"]].translation; K = W[pg["K"]].translation; D = W[pg["D"]].translation
            return P, K, D, (W[pg["D"]].translation + rot(W[pg["D"]]) @ Vector((0, pg["L5"], 0)))
        Pa, Ka, Da, Ea = alvo(Wa); Pb, Kb, Db, Eb = alvo(Wb)
        Jt = (Wa[pg["J"]].translation).lerp(Wb[pg["J"]].translation, t)
        P = Pa.lerp(Pb, t); K = Ka.lerp(Kb, t); D = Da.lerp(Db, t); Ep = Ea.lerp(Eb, t)
        p.pata[c] = dict(modo="abs", P=P, K=K, D=D, E=Ep)
    return p

_resolver_base = resolver
def resolver(p):                                      # suporte a patas em posicao absoluta (transicoes)
    abs_ = {c: s for c, s in p.pata.items() if s.get("modo") == "abs"}
    if not abs_: return _resolver_base(p)
    for c in abs_: p.pata[c] = dict(modo="livre", P=Vector(), meta=Y, dedos=Y)
    W, _ = _resolver_base(p)                          # 1a passada: posicao dos ombros/quadris
    for c, s in abs_.items():
        J = W[PERNAS[c]["J"]].translation
        p.pata[c] = dict(modo="livre", P=s["P"] - J, meta=(s["K"] - s["P"]), dedos=(s["D"] - s["K"]), ponta=(s["E"] - s["D"]))
    return _resolver_base(p)

def _min_asa(p):
    W, _ = resolver(p)
    return min((W[n].translation + rot(W[n]) @ Vector((0, A.data.bones[n].length, 0))).z for n in ASA)
def asas_acima_do_chao(p, alto, piso=0.06):
    """se alguma ponta de osso da asa fica abaixo do piso (unidades do rig; 0,06 = ~1 stud), mistura as asas com a
    pose 'alto' so o necessario (busca binaria)"""
    if _min_asa(p) >= piso: return
    orig = p.asas; lo, hi = 0.0, 1.0
    for _ in range(9):
        t = (lo + hi) / 2; p.asas = mistura(orig, alto, t)
        if _min_asa(p) >= piso: hi = t
        else: lo = t
    p.asas = mistura(orig, alto, hi)
def cauda_sobre_chao(p, piso=0.035):
    """segmento da cauda cuja ponta entraria no chao sobe so o necessario (transicoes ar <-> chao)"""
    for it in range(12):
        W, _ = resolver(p); mudou = False
        for i, n in enumerate(CAUDA):
            L = A.data.bones[n].length; tz = (W[n].translation + rot(W[n]) @ Vector((0, L, 0))).z
            if tz < piso:
                c, e = p.curva.get(n, (0.0, 0.0)); p.curva[n] = (c + math.degrees(math.asin(min(1, (piso - tz) / L))), e); mudou = True
                break
        if not mudou: break

def f_decolagem(u):
    # 0-0.35 agacha e ergue as asas; 0.35-0.55 impulso (pernas estendem, batida forte); 0.55-1 recolhe e bate
    chao = Pose(); em_pe(chao)
    ag = smooth(u / 0.35) if u < 0.35 else max(0.0, 1 - smooth((u - 0.35) / 0.15))
    chao.off = Vector((0, 0, -0.035 - 0.05 * ag + (0.07 * smooth((u - 0.4) / 0.2) if u > 0.4 else 0)))
    chao.arf = 5 + 6 * ag
    for c in chao.pata: chao.pata[c]["beta"] = BETA[c] + 28 * ag; chao.pata[c]["dedos"] = 6 * ag   # garras nao entram no chao
    pescoco_alto(chao, cima=-10 * ag + (16 * smooth((u - 0.35) / 0.25) if u > 0.35 else 0))
    cauda(chao, -10 + 14 * ag, 4.5, [0] * 7, chao=True)
    # asas: dobradas -> erguidas (fase alta do Flap) -> ciclo de batidas
    fa = fase_alta()
    if u < 0.35: chao.asas = mistura(asas("Silverwing_Idle", u), asas("Silverwing_Fly_Flap", fa), smooth(u / 0.35))
    else: chao.asas = asas("Silverwing_Fly_Flap", fa + (u - 0.35) / 0.65 * 1.5)
    ar = f_voo(fa + (u - 0.35) / 0.65 * 1.5 if u > 0.35 else fa)
    w = smooth((u - 0.45) / 0.35)
    p = chao if w <= 0 else mistura_pose(chao, ar, w)
    # CERTIFICACAO 02/11: com as patas ainda perto do chao a batida completa enfiava as pontas ~7 studs no solo (o
    # servidor so ergue o corpo depois de 40% do clipe; a IA nao ergue). A batida e limitada para as pontas ficarem
    # acima do piso (golpe raso enquanto o corpo sobe) e a cauda nao atravessa o chao
    asas_acima_do_chao(p, asas("Silverwing_Fly_Flap", fa)); cauda_sobre_chao(p)
    return p

def f_pouso(u):
    # contato rapido: patas estendidas p/ o chao, toque, amortecimento, asas fecham
    ar = f_pairar(0.6); chao = Pose(); em_pe(chao)
    ar.off += Vector((0, 0, 0.11))                   # o clipe comeca com o modelo ja no chao: patas penduradas acima dele
    absorve = math.sin(math.pi * smooth((u - 0.2) / 0.6)) if u > 0.2 else 0
    chao.off += Vector((0, 0, -0.05 * absorve)); chao.arf += 4 * absorve
    for c in chao.pata: chao.pata[c]["beta"] = BETA[c] + 30 * absorve
    pescoco_alto(chao, cima=-8 * absorve)
    cauda(chao, -14, 5.0, [0] * 7)
    chao.asas = mistura(asas("Silverwing_Fly_Glide", 0.2), asas("Silverwing_Idle", u), smooth((u - 0.15) / 0.85))
    w = smooth(u / 0.25)
    p = mistura_pose(ar, chao, w)
    asas_acima_do_chao(p, asas("Silverwing_Fly_Glide", 0.2)); cauda_sobre_chao(p)       # certificacao 02/11
    return p

def f_mordida(u):
    """Mordida Aerea (1,0 s, no lugar: o servidor faz o avanco). 0-0.28 preparo (pescoco recolhe em S, cabeca baixa,
    asas sobem, patas encolhem, cauda alinha); 0.28-0.55 disparo (pescoco projeta, corpo alonga, asas varrem para
    tras, garras dianteiras a frente, boca abre); 0.55-0.66 mordida (fecha com forca, cabeca da 'tranco');
    0.66-1 recuperacao ate o Voo."""
    prep = smooth(u / 0.28) * (1 - smooth((u - 0.28) / 0.12))
    disp = smooth((u - 0.26) / 0.22) * (1 - smooth((u - 0.7) / 0.3))
    boca = smooth((u - 0.38) / 0.14) * (1 - smooth((u - 0.55) / 0.06))
    tranco = math.sin(math.pi * min(1, max(0, (u - 0.55) / 0.12)))
    p = Pose()
    p.arf = 6 * prep - 10 * disp                       # agacha no ar e mergulha o nariz no bote
    p.off = Vector((0, -0.03 * prep + 0.06 * disp, 0.015 * prep))
    p.curva["spine_0"] = (5 * prep - 4 * disp, 0); p.curva["spine_1"] = (7 * prep - 5 * disp, 0)
    # pescoco: S recolhido (preparo) -> reto e projetado (disparo); cabeca compensa
    for i, n in enumerate(PESCOCO):
        p.curva[n] = (lerp(0, [22, 4, -20][i], prep) + 2 - 3 * disp + 6 * tranco * (i == 2), 0)
    p.curva["head"] = (-8 * prep + 4 * disp - 10 * tranco, 0)
    p.curva["mouth_lower"] = (-38 * boca + 3 * tranco, 0)          # mandibula abre / fecha
    # asas: sobem (preparo) -> varrem para tras recolhidas (disparo) -> voltam a bater
    fa = max(range(len(PONTA)), key=lambda i: PONTA[i]) / (len(PONTA) - 1)
    alto = asas("Silverwing_Fly_Flap", fa); var = mistura(asas("Silverwing_Fly_Glide", 0.2), asas("Silverwing_Idle", 0.0), 0.55)
    base = asas("Silverwing_Fly_Flap", fa + u * 1.4)
    p.asas = mistura(mistura(base, alto, prep), var, disp)
    Rb = p.Rb()
    for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): p.extra[n] = Rax(Rb @ Z, -14 * s_ * disp)
    recolhidas(p, fa + u * 1.4, pender=0.0)
    for c, pg in PERNAS.items():                                     # garras dianteiras a frente no bote
        if not pg["tras"]:
            sp = p.pata[c]
            sp["P"] = sp["P"].lerp((Rb @ X) * pg["s"] * 0.06 + (Rb @ Y) * -0.10 + (Rb @ Z) * -0.10, disp * 0.8)
            sp["meta"] = sp["meta"].lerp(-(Rb @ Y) - (Rb @ Z) * 0.3, disp); sp["dedos"] = sp["dedos"].lerp(-(Rb @ Y), disp)
        else:
            p.pata[c]["P"] = p.pata[c]["P"] + (Rb @ Z) * 0.02 * prep
    lat = [0.6 * math.sin(2 * math.pi * u * 2 - 0.5 * k) * k * (1 - disp) for k in range(7)]
    cauda_ar(p, 3 * prep - 2 * disp, lat, [(-2 * prep + 1.5 * disp) * (0.5 + 0.1 * k) for k in range(7)])
    rec = smooth((u - 0.7) / 0.3)
    if rec > 0: return mistura_pose(p, f_voo((fa + u * 1.4) % 1.0), rec)
    return p

# ---------------------------------------------------------------- combate (clipes proprios)
# Tempos casados com os marcadores de reserva do Combate_Dragao.Nucleo (o KeyframeSequence importado nao traz
# marcadores): Mordida Impacto 0,74 s; Garra 0,72 s; Cauda 0,92 s; Rugido 0,95 s; Sopro emissao 1,05 s;
# Arremetida preparo 0,7 + avanco 0,7; Tempestade Impulso 1,1 / Batida 1,75 / Pouso 2,95; Tempestade aerea Batida
# 1,0; Ruptura Impacto 1,4 / Erupcao 1,65 / Fim 3,4. Cada golpe: antecipacao -> preparo -> execucao -> contato ->
# reacao -> recuperacao, com corpo, pescoco, cauda (contrapeso com atraso) e patas participando.
FA = fase_alta()                                                                 # asa no alto (fase do Fly_Flap)
FB = min(range(len(PONTA)), key=lambda i: PONTA[i]) / (len(PONTA) - 1)       # asa embaixo
def janela(u, a, b): return smooth((u - a) / (b - a)) if b > a else float(u >= a)
def pulso(u, a, b, c, d): return janela(u, a, b) * (1 - janela(u, c, d))      # sobe a-b, fica, desce c-d
def ref_pata(p, c):
    W, _ = resolver(p); pg = PERNAS[c]
    J = W[pg["J"]].translation; P = W[pg["P"]].translation; K = W[pg["K"]].translation
    return P - J, K - P, rot(W[pg["K"]]) @ Y
def eixos(p): Rb = p.Rb(); return -(Rb @ Y), Rb @ X, Rb @ Z                   # frente, esquerda, cima
def boca_abre(p, a, tranco=0.0): p.curva["mouth_lower"] = (-40 * a + 3 * tranco, 0)
def cauda_contrapeso(fn_g, u, ganho=0.5, atraso=0.035):
    """lateral da cauda = giro do corpo com sinal trocado, propagado com atraso (a base reage primeiro)"""
    return [-ganho * fn_g(u - atraso * k) * PESO_CAUDA[k] * 1.6 for k in range(7)]

def f_ataque_mordida(u):
    """Mordida terrestre 1,4 s (contato 0,53): recolhe o pescoco em S e abre a boca, avanca ombros/torax e projeta
    a cabeca, fecha com forca no contato (tranco), segura e volta."""
    prep = pulso(u, 0.0, 0.33, 0.36, 0.46)
    bote = pulso(u, 0.36, 0.53, 0.62, 1.0)
    abre = pulso(u, 0.28, 0.45, 0.51, 0.55)
    tr = math.sin(math.pi * min(1, max(0, (u - 0.53) / 0.12)))
    p = Pose(); em_pe(p)
    p.off += Vector((0, 0.025 * prep - 0.05 * bote, 0.008 * prep - 0.014 * bote))
    p.arf += 3 * prep - 7 * bote
    p.curva["spine_1"] = (3 * prep - 4 * bote, 0); p.curva["spine_0"] = (-1.5 * prep + 1.5 * bote, 0)
    # pescoco ereto no repouso: o bote precisa levar a cabeca para FRENTE e para BAIXO (base do pescoco gira forte)
    pescoco_alto(p, cima=8 * prep - 30 * bote, cab=4 * prep - 6 * bote - 8 * tr)
    for i, n_ in enumerate(PESCOCO):                                            # S de recolhimento (soma 0) + bote
        c_, e_ = p.curva[n_]; p.curva[n_] = (c_ + [14, 0, -14][i] * prep + [-26, -8, 10][i] * bote, e_)
    c_, e_ = p.curva["head"]; p.curva["head"] = (c_ + 18 * bote, e_)           # focinho aponta para a frente no bote
    # BOTE BAIXO (teste da IA 30/10: no contato a boca ficava ~17 studs acima de um alvo do tamanho de um jogador e a
    # mordida errava): no bote o pescoco desce ate a boca ficar na altura do alvo (~0,2 = 3,5 studs), misturado pelo
    # peso do bote (preparo em S intacto)
    if bote > 0.01:
        antes = {n_: p.curva[n_] for n_ in PESCOCO + ["head"]}
        pescoco_ao_chao(p, lerp(0.42, 0.20, bote), cab_extra=-8 * tr)
        for n_, (ca, ea) in antes.items():
            cb, eb = p.curva[n_]; p.curva[n_] = (lerp(ca, cb, bote), lerp(ea, eb, bote))
    boca_abre(p, abre, tr)
    p.asas = asas_ameaca(0.15 * bote)
    for c in ("PD_E", "PD_D"): p.pata[c]["beta"] += 8 * bote                    # punhos firmam no avanco
    vert = [(5 * prep - 3 * bote + 6 * math.sin(math.pi * min(1, max(0, (u - 0.5 - 0.03 * k) / 0.3)))) * PESO_CAUDA[k] for k in range(7)]
    cauda(p, -14 + 6 * prep, 5.0, onda_cauda(u, [(2.0, 1, 0.4, 1.0)]), onda=vert)
    return p

def f_ataque_garra(lado):
    """Garra 1,5 s (contato 0,48): peso nas outras 3 patas, tronco gira para armar, ombro/cotovelo/punho levantam e
    abrem as garras; o golpe descreve um arco para frente e para dentro raspando para baixo; a pata volta ao apoio."""
    c = "PD_E" if lado == "E" else "PD_D"; s = PERNAS[c]["s"]
    def giro(t): return (-s * 5 * janela(t, 0, 0.30) + s * 12 * janela(t, 0.32, 0.48)) * (1 - janela(t, 0.6, 1.0))
    def fn(u):
        prep = janela(u, 0.0, 0.30); golpe = janela(u, 0.32, 0.48); rec = janela(u, 0.60, 1.0)
        p = Pose(); em_pe(p)
        Prel0, meta0, ded0 = ref_pata(p, c)
        p.rol = -s * 3.5 * prep * (1 - rec); p.gui = giro(u)
        p.off += Vector((-s * 0.008 * prep, -0.02 * golpe, -0.006 * prep)) * (1 - rec)
        p.arf += (3 * prep - 4 * golpe) * (1 - rec)
        p.curva["spine_1"] = (0, (s * 4 * golpe - s * 2 * prep) * (1 - rec))
        pescoco_alto(p, cima=(-4 * prep - 6 * golpe) * (1 - rec), esq=-0.6 * giro(u), cab=-4 * golpe * (1 - rec))
        boca_abre(p, 0.25 * pulso(u, 0.3, 0.45, 0.55, 0.75))                     # rosna no esforco
        p.asas = asas_ameaca(0.18 * pulso(u, 0.1, 0.4, 0.55, 0.9))
        fr, es, ci = eixos(p); fora = es * s
        armado = Prel0 + ci * 0.12 - fr * 0.015 + fora * 0.03
        fim = Prel0 + ci * 0.03 + fr * 0.11 - fora * 0.045
        if u < 0.32: P = Prel0.lerp(armado, prep)
        else: P = armado.lerp(fim, golpe) + ci * 0.04 * math.sin(math.pi * golpe) + fora * 0.02 * math.sin(math.pi * golpe)
        mt_arm = (fr * 0.5 - ci * 0.8); mt_fim = (fr - ci * 0.5)
        dd_arm = (fr * 0.4 + ci * 0.9); dd_fim = (fr * 0.3 - ci * 1.0)
        if u < 0.32: mt = meta0.normalized().lerp(mt_arm.normalized(), prep); dd = ded0.lerp(dd_arm.normalized(), prep)
        else: mt = mt_arm.normalized().lerp(mt_fim.normalized(), golpe); dd = dd_arm.normalized().lerp(dd_fim.normalized(), golpe)
        if rec > 0: P = P.lerp(Prel0, rec); mt = mt.lerp(meta0.normalized(), rec); dd = dd.lerp(ded0, rec)
        if rec < 0.999: p.pata[c] = dict(modo="livre", P=P, meta=mt, dedos=dd)
        outra = "PD_D" if c == "PD_E" else "PD_E"; p.pata[outra]["beta"] += 6 * prep * (1 - rec)   # apoio firma
        vert = [(3 * golpe * (1 - rec)) * PESO_CAUDA[k] for k in range(7)]
        cauda(p, -14, 5.0, somar(cauda_contrapeso(giro, u), onda_cauda(u, [(1.5, 1, 0.2, 1.0)])), onda=vert)
        return p
    return fn

def f_ataque_cauda(u):
    """Golpe de cauda 1,8 s (contato 0,51): enrola para um lado, chicoteia para o outro (onda da base a ponta), volta."""
    def h(t): return 10 * janela(t, 0.0, 0.38) - 20 * janela(t, 0.42, 0.54) + 10 * janela(t, 0.62, 1.0)
    p = Pose(); em_pe(p)
    p.gui = -0.35 * h(u); p.rol = 0.12 * h(u)
    pescoco_alto(p, esq=-0.9 * h(u), cima=-3 * pulso(u, 0.3, 0.45, 0.6, 0.9))
    p.asas = asas_ameaca(0.12 * pulso(u, 0.3, 0.45, 0.6, 0.9))
    lat = [h(u - 0.028 * k) * PESO_CAUDA[k] * 1.1 for k in range(7)]
    cauda(p, -10, 5.0, lat, onda=[4 * pulso(u, 0.3, 0.45, 0.6, 0.9) * PESO_CAUDA[k] for k in range(7)])
    return p

ROAR_ESTILO = os.environ.get("ROAR_ESTILO", "fogo")       # personalidade do rugido: fogo (energico) | gelo (frio)
def f_rugido(base_ar=False):
    """RUGIDO PADRAO v2 (01/11, todos os dragoes; personalidade por ROAR_ESTILO), 2,6 s, emissao em 0,365 (marcador
    RugidoInicio do Nucleo): ANTECIPACAO (peso para tras, pescoco recolhe e sobe, peito enche, boca entreabre) ->
    INVESTIDA curta em direcao ao alvo (patas dianteiras firmam, corpo avanca, pescoco projeta, cabeca desce e a boca
    abre ao maximo no quadro da emissao) -> SUSTENTACAO com tensao no pescoco/garganta, varredura lenta da cabeca,
    asas em exibicao, cauda em contrapeso -> RECUPERACAO. A direcao do alvo vem do corpo (a IA vira antes) e do foco
    AlvoOlhar (MovimentoVivo). 'gelo': frio e controlado (pouco tremor, cabeca baixa e estavel, asas amplas)."""
    gelo = ROAR_ESTILO == "gelo"
    trem_f, trem_a = (7, 1.0) if gelo else (20, 3.0)
    def fn(u):
        ant = pulso(u, 0.0, 0.28, 0.30, 0.38)
        inv = pulso(u, 0.30, 0.37, 0.80, 0.97)
        sus = pulso(u, 0.37, 0.45, 0.78, 0.92)
        trem = math.sin(2 * math.pi * trem_f * u) * sus * trem_a
        varre = math.sin(2 * math.pi * (u - 0.4)) * sus * (3 if gelo else 5)
        if base_ar:
            p = f_pairar(u * 3 % 1.0)
            pescoco_voo(p, cima=-30 + 12 * ant - 8 * inv, esq=0.5 * varre + 0.3 * trem, cab=-p.arf * 0.2 - 8 * inv)
        else:
            p = Pose(); em_pe(p)
            for c in PERNAS: p.pata[c]["beta"] += (6 if c.startswith("PD") else 3) * inv
            avan = 0.022 if gelo else 0.032
            p.off += Vector((0, 0.016 * ant - avan * inv, 0.008 * ant - 0.006 * inv))
            p.arf += 4 * ant - (5 if gelo else 4) * inv
            pescoco_alto(p, cima=12 * ant - (16 if gelo else 12) * inv + 0.4 * trem, esq=varre + 0.5 * trem,
                         cab=6 * ant - (12 if gelo else 8) * inv)
            p.asas = asas_ameaca(0.25 * ant + (0.62 if gelo else 0.5) * inv)
            lat = somar(onda_cauda(u, [(4.0, 1, 0.0, 1.0), (2.0, 3, 1.0, 1.3)]), [-0.4 * varre * PESO_CAUDA[k] for k in range(7)])
            cauda(p, -14 - 4 * ant + 10 * inv, 5.0, lat, onda=[7 * inv * PESO_CAUDA[k] for k in range(7)])
        p.curva["spine_1"] = (p.curva.get("spine_1", (0, 0))[0] + 7 * ant + 3 * inv, 0)
        p.curva["spine_0"] = (p.curva.get("spine_0", (0, 0))[0] - 2 * ant, p.curva.get("spine_0", (0, 0))[1])
        boca_abre(p, 0.18 * ant + 1.12 * inv, tranco=0.3 * trem)
        if CABECA_RUGIDO == "gelo":
            # frio e calculado: recua e inclina a cabeca medindo o alvo, depois UMA virada lenta e deliberada de um
            # lado ao outro com o queixo recolhido (sem tranco nem sacudida) e volta a encarar
            vira = 8 * math.sin(2 * math.pi * (u - 0.40) / 0.9) * sus
            cabeca_extra(p, cima=4 * ant - 5 * sus, esq=vira, inclina=6 * ant - 0.3 * vira)
        return p
    return fn

# ---------------------------------------------------------------- RUGIDOS DO FOGO (02/11, Dragao das Montanhas)
# Agressivo, dominante e expressivo (o Glacial e frio e controlado). Cada um: preparo -> emissao (tempo = fase do som no
# SonsDragao_Cliente / marcador do Nucleo) -> reacao do corpo (garganta treme, peito, coluna) -> recuperacao.
def tremor_voz(rug, freq, amp, u): return math.sin(2 * math.pi * freq * u) * rug * amp
def garganta(p, t):
    """tremor da garganta/pescoco durante a vocalizacao (vibracao gutural); chamar DEPOIS de pescoco_alto/voo"""
    for i, n_ in enumerate(PESCOCO):
        c_, e_ = p.curva[n_]; p.curva[n_] = (c_ + t * (0.3 + 0.25 * i), e_ + 0.2 * t)
    return t

def f_rugido_ameaca(u):
    """Rugido de AMEACA 3,0 s (emissao do rugido em 0,56; rosnado desde 0,25): encara o alvo (o MovimentoVivo vira
    pescoco/cabeca pelo AlvoOlhar), focinho BAIXO e a frente, dentes a mostra, ombros e asas tensos, patas se
    reposicionam; o rosnado cresce e EXPLODE num rugido curto PROJETANDO a cabeca para frente (nunca para o ceu);
    mantem a atencao no alvo."""
    if CABECA_RUGIDO: return f_rugido_ameaca_v2(u)
    enc = janela(u, 0.0, 0.22); rosn = pulso(u, 0.25, 0.42, 0.52, 0.58); rug = pulso(u, 0.55, 0.60, 0.74, 0.86)
    fica = janela(u, 0.80, 1.0)
    p = Pose(); base_pe(p, 0.45 * enc)
    for c in PERNAS: p.pata[c]["beta"] += (7 if c.startswith("PD") else 4) * enc
    p.off += Vector((0, 0.008 * rosn - 0.03 * rug, -0.006 * enc + 0.004 * rosn))
    p.arf += 2 * rosn - 5 * rug
    p.curva["spine_1"] = (2 * rosn + 4 * rug, 0); p.curva["spine_0"] = (-2 * rosn, 0)
    tr = tremor_voz(max(rosn * 0.5, rug), 26, 2.6, u)
    pescoco_alto(p, cima=-16 * enc - 4 * rosn - 10 * rug + 3 * fica, esq=0.4 * tr, cab=5 * enc + 2 * rosn - 7 * rug)
    # FOCINHO BAIXO e a frente (revisao 02/11: so com pescoco_alto o pescoco subia no rugido): mistura com a pose de
    # boca na altura do alvo (0,42 = ~7 studs), mais forte no rosnado/rugido
    w = min(1.0, 0.45 * enc + 0.35 * rosn + 0.6 * rug)
    if w > 0.01:
        antes = {n_: p.curva[n_] for n_ in PESCOCO + ["head"]}
        pescoco_ao_chao(p, lerp(0.42, 0.30, rug), cab_extra=8 * rug)            # focinho a frente: a mandibula abre para frente
        for n_, (ca, ea) in antes.items():
            cb, eb = p.curva[n_]; p.curva[n_] = (lerp(ca, cb, w), lerp(ea, eb, w))
    garganta(p, tr)
    boca_abre(p, 0.14 * enc + 0.16 * rosn + 0.95 * rug + 0.06 * fica, tranco=tr)
    p.asas = asas_ameaca(0.35 * enc + 0.25 * rug + 0.03 * math.sin(2 * math.pi * 7 * u) * enc)
    cauda(p, -9 + 4 * rug, 5.0, onda_cauda(u, [(9.0, 1, 0.0, 0.9), (3.0, 3, 1.0, 1.2)]),
          onda=[(2.5 * enc + 2.5 * rug) * PESO_CAUDA[k] for k in range(7)])
    return p

def f_rugido_ameaca_v2(u):
    """Rugido de AMEACA v2 (03/11) 3,0 s: o som comeca em 0,30 e dura ate ~0,88 -> a boca fica FECHADA (labio
    entreaberto) ate 0,30, abre com o som, fica aberta no trecho forte e fecha quando ele morre (antes abria num rosnado
    mudo 0,8 s antes e o rugido era mais curto que a boca aberta). Cabeca: encara baixo, oscila como cobra e inclina
    medindo o alvo; no rugido projeta e da dois trancos para frente, contra-inclina e volta a encarar."""
    enc = janela(u, 0.0, 0.22); rug = pulso(u, 0.30, 0.40, 0.76, 0.88); fica = janela(u, 0.84, 1.0)
    cobra = enc * (1 - janela(u, 0.26, 0.34))
    tranco = pulso(u, 0.44, 0.48, 0.51, 0.56) + pulso(u, 0.60, 0.64, 0.67, 0.72)
    p = Pose(); base_pe(p, 0.45 * enc)
    for c in PERNAS: p.pata[c]["beta"] += (7 if c.startswith("PD") else 4) * enc
    p.off += Vector((0, -0.026 * rug - 0.012 * tranco, -0.006 * enc))
    p.arf += -4 * rug
    p.curva["spine_1"] = (4 * rug, 0); p.curva["spine_0"] = (-1.5 * rug, 0)
    tr = tremor_voz(rug, 26, 2.6, u)
    ond = 7 * math.sin(2 * math.pi * 1.7 * u) * cobra                      # cobra: vai e volta lento, encarando
    pescoco_alto(p, cima=-16 * enc - 10 * rug - 4 * tranco + 3 * fica, esq=ond + 0.4 * tr, cab=5 * enc - 7 * rug)
    w = min(1.0, 0.45 * enc + 0.6 * rug)
    if w > 0.01:
        antes = {n_: p.curva[n_] for n_ in PESCOCO + ["head"]}
        pescoco_ao_chao(p, lerp(0.42, 0.30, rug), esq=ond, cab_extra=8 * rug)
        for n_, (ca, ea) in antes.items():
            cb, eb = p.curva[n_]; p.curva[n_] = (lerp(ca, cb, w), lerp(ea, eb, w))
    garganta(p, tr)
    cabeca_extra(p, cima=-6 * tranco + 2 * cobra, esq=0.4 * ond, inclina=10 * cobra - 6 * rug + 4 * fica)
    boca_abre(p, 0.05 * enc + 0.97 * rug + 0.04 * fica, tranco=tr)
    p.asas = asas_ameaca(0.35 * enc + 0.25 * rug + 0.03 * math.sin(2 * math.pi * 7 * u) * enc)
    cauda(p, -9 + 4 * rug, 5.0, onda_cauda(u, [(9.0, 1, 0.0, 0.9), (3.0, 3, 1.0, 1.2)]),
          onda=[(2.5 * enc + 2.5 * rug) * PESO_CAUDA[k] for k in range(7)])
    return p

def f_rugido_combate_fogo(u):
    """Rugido de COMBATE do Fogo 1,6 s (emissao em 0,30): contrai o pescoco em S, PROJETA a cabeca de uma vez, boca
    escancarada, vocalizacao curta e feroz; ombros/peito/coluna acusam o esforco, cauda compensa, recupera rapido."""
    con = pulso(u, 0.0, 0.22, 0.24, 0.32); proj = pulso(u, 0.28, 0.34, 0.58, 0.82)
    p = Pose(); em_pe(p)
    for c in PERNAS: p.pata[c]["beta"] += (5 if c.startswith("PD") else 2) * proj
    p.off += Vector((0, 0.014 * con - 0.028 * proj, 0.004 * con - 0.006 * proj))
    p.arf += 3 * con - 6 * proj
    p.curva["spine_1"] = (4 * con + 5 * proj, 0); p.curva["spine_0"] = (-2 * con + 1.5 * proj, 0)
    pescoco_alto(p, cima=6 * con - 14 * proj, cab=5 * con - 6 * proj)
    for i, n_ in enumerate(PESCOCO):                                            # S de recolhimento -> projecao
        c_, e_ = p.curva[n_]; p.curva[n_] = (c_ + [12, 0, -12][i] * con + [-10, -4, 6][i] * proj, e_)
    tr = tremor_voz(proj, 24, 3.2, u); garganta(p, tr)
    boca_abre(p, 0.2 * con + 1.0 * proj, tranco=tr)
    p.asas = asas_ameaca(0.12 * con + 0.32 * proj)
    vert = [(5 * proj - 3 * con) * PESO_CAUDA[k] for k in range(7)]
    cauda(p, -14 + 5 * proj, 5.0, onda_cauda(u, [(2.5, 1, 0.3, 1.0)]), onda=vert)
    if CABECA_RUGIDO == "fogo":
        # combate: arma a cabeca para tras inclinada, ESTALA para frente/baixo no grito e sacode de raiva no fim
        estala = pulso(u, 0.28, 0.33, 0.38, 0.48)
        cabeca_extra(p, cima=6 * con - 9 * estala, esq=sacode(u, 0.48, 0.84, 3.0, 9),
                     inclina=7 * con - 5 * estala + 0.5 * sacode(u, 0.50, 0.86, 3.0, 9))
    return p

def f_rugido_aereo(u):
    """Rugido AEREO 2,4 s (emissao em 0,35): no Studio vira clipe PARCIAL (_Sup: so pescoco/cabeca/mandibula/peito),
    entao asas, patas e cauda seguem o voo. Peito expande, pescoco projeta discretamente para frente, boca abre."""
    ins = pulso(u, 0.0, 0.25, 0.28, 0.36); rug = pulso(u, 0.33, 0.40, 0.72, 0.9)
    p = f_pairar(u * 2 % 1.0)
    tr = math.sin(2 * math.pi * 20 * u) * rug * 2.5
    p.arf += 3 * ins - 2 * rug
    p.curva["spine_1"] = (p.curva.get("spine_1", (0, 0))[0] + 6 * ins + 3 * rug, 0)
    pescoco_voo(p, cima=-30 + 8 * ins - 4 * rug, esq=0.3 * tr, cab=-p.arf * 0.2 + 4 * ins - 6 * rug)
    boca_abre(p, 0.15 * ins + 1.0 * rug, tranco=tr)
    if CABECA_RUGIDO == "fogo":
        # no ar: cabeca estica para frente, da um tranco PARA CIMA no pico do grito e inclina de um lado ao outro como
        # se cortasse o vento (o corpo segue o voo; so pescoco/cabeca no clipe parcial)
        joga = pulso(u, 0.44, 0.50, 0.56, 0.66)
        cabeca_extra(p, cima=-3 * rug + 9 * joga, esq=5 * math.sin(2 * math.pi * 1.2 * (u - 0.4)) * rug,
                     inclina=8 * math.sin(2 * math.pi * 1.2 * (u - 0.4)) * rug)
    return p

def f_rugido_vitoria(u):
    """Rugido de VITORIA 3,6 s (emissao em 0,36): ergue a cabeca, enche o peito, abre as asas pela metade, rugido medio
    e imponente (cabeca alta mas nao ao ceu), cauda balancando; recupera devagar."""
    sobe = pulso(u, 0.0, 0.25, 0.80, 1.0); ins = pulso(u, 0.18, 0.30, 0.32, 0.38); rug = pulso(u, 0.35, 0.42, 0.66, 0.80)
    p = Pose(); em_pe(p)
    p.off += Vector((0, 0.006 * ins, 0.002 * sobe + 0.001 * ins))           # peito enche sem esticar as patas
    p.arf += 1.5 * sobe + 1.5 * ins                                             # peito sobe pela coluna, nao pelas patas
    p.curva["spine_1"] = (3 * sobe + 3 * ins + 2 * rug, 0)
    tr = tremor_voz(rug, 18, 2.2, u)
    pescoco_alto(p, cima=10 * sobe + 4 * ins + 2 * rug, esq=0.4 * tr + 3 * math.sin(2 * math.pi * u) * sobe, cab=3 * ins + 8 * rug)
    garganta(p, tr)
    boca_abre(p, 0.12 * ins + 0.95 * rug, tranco=tr)
    p.asas = asas_ameaca(0.45 * sobe + 0.08 * rug)
    cauda(p, -12 + 8 * sobe, 5.0, onda_cauda(u, [(5.0, 1, 0.2, 0.9), (2.0, 3, 1.0, 1.2)]),
          onda=[5 * sobe * PESO_CAUDA[k] for k in range(7)])
    if CABECA_RUGIDO == "fogo":
        # triunfo: no pico JOGA a cabeca para tras (queixo ao alto), depois vira devagar olhando o derrotado de cima e
        # termina com dois acenos curtos de dominio
        joga = pulso(u, 0.44, 0.50, 0.56, 0.64)
        olha = 12 * math.sin(math.pi * _lim((u - 0.58) / 0.30)) * janela(u, 0.56, 0.64) * (1 - janela(u, 0.86, 0.98))
        acena = pulso(u, 0.84, 0.87, 0.88, 0.91) + pulso(u, 0.92, 0.95, 0.96, 0.99)
        cabeca_extra(p, cima=11 * joga - 5 * acena - 4 * (olha / 12), esq=olha, inclina=-0.3 * olha + 3 * joga)
    return p

def _sopro(p, ar, recolhe, mira, abre, tremor, u):
    """pescoco/cabeca/boca do sopro sobre a pose base (solo ou pairando)"""
    if ar:
        pescoco_voo(p, cima=-30 + 14 * recolhe - 6 * mira, esq=1.5 * tremor, cab=-p.arf * 0.2 - 4 * mira)
    else:
        pescoco_alto(p, cima=12 * recolhe - 14 * mira, esq=1.5 * tremor, cab=-5 * mira)
        for i, n_ in enumerate(PESCOCO):
            c_, e_ = p.curva[n_]; p.curva[n_] = (c_ + [10, 0, -10][i] * recolhe, e_)
    p.curva["spine_1"] = (p.curva.get("spine_1", (0, 0))[0] + 6 * recolhe - 2 * mira, 0)   # torax expande e empurra
    boca_abre(p, abre * (0.85 + 0.05 * tremor))
def f_sopro(fase, ar=False):
    def fn(u):
        if fase == "Inicio":     # 1,2 s: recolhe e enche o peito (0-0,7), aponta e abre a boca ate a emissao (0,875)
            recolhe = pulso(u, 0.0, 0.6, 0.7, 0.9); mira = janela(u, 0.68, 0.9); abre = janela(u, 0.7, 0.88); tremor = 0
        elif fase == "Loop":     # 0,9 s em laco: boca aberta, pescoco firme na mira, pequeno tremor do jato
            recolhe = 0; mira = 1; abre = 1; tremor = math.sin(2 * math.pi * 3 * u)
        else:                    # Fim 0,8 s: fecha a boca, sacode a cabeca e volta
            recolhe = 0; mira = 1 - janela(u, 0.1, 0.8); abre = 1 - janela(u, 0.0, 0.35); tremor = math.sin(2 * math.pi * 2 * u) * (1 - u)
        if ar:
            p = f_pairar(u if fase == "Loop" else (u * (1.2 if fase == "Inicio" else 0.8)) % 1.0)
        else:
            p = Pose(); em_pe(p)
            p.off += Vector((0, 0.012 * recolhe - 0.02 * mira, 0.004 * recolhe))
            p.arf += 2 * recolhe - 2 * mira
            p.asas = asas_ameaca(0.25 * mira + 0.1 * recolhe)
            for c in ("PD_E", "PD_D"): p.pata[c]["beta"] += 6 * mira               # patas firmam contra o recuo
            cauda(p, -12 + 4 * mira, 5.0, onda_cauda(u, [(2.0, 1, 0.3, 1.0)]), onda=[3 * mira * PESO_CAUDA[k] for k in range(7)])
        _sopro(p, ar, recolhe, mira, abre, tremor, u)
        return p
    return fn

def f_arremetida(ar=False):
    """Arremetida 2,1 s: preparo 0-0,33 (agacha, asas armam, pescoco recua), avanco 0,33-0,67 (o servidor desloca o
    corpo: aqui o bote - patas a frente/atras, asas varridas, pescoco reto, boca abre e fecha no contato), recuperacao."""
    def fn(u):
        prep = pulso(u, 0.0, 0.3, 0.33, 0.42); av = pulso(u, 0.33, 0.42, 0.62, 0.8)
        abre = pulso(u, 0.42, 0.5, 0.58, 0.62)
        if ar:
            p = f_voo((FA * (1 - prep) + u * 2) % 1.0)
            p.asas = mistura(mistura(p.asas, asas("Silverwing_Fly_Flap", FA), prep),
                             mistura(asas("Silverwing_Fly_Glide", 0.2), asas("Silverwing_Idle", 0.0), 0.6), av)
            Rb = p.Rb()
            for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): p.extra[n] = Rax(Rb @ Z, -14 * s_ * av)
            p.arf += 4 * prep - 6 * av
            pescoco_voo(p, cima=10 * prep - 6 * av, cab=-4 * av)
            cauda_ar(p, 3 * prep - 2 * av, onda_cauda(u, [(2.5, 2, 0.0, 0.9)]), [(-1.5 * prep + 1.5 * av) * PESO_CAUDA[k] for k in range(7)])
        else:
            base = Pose(); em_pe(base, agach=0.06 * prep)
            base.arf -= 4 * prep
            pescoco_alto(base, cima=6 * prep)
            base.asas = mistura(asas("Silverwing_Idle", u), asas("Silverwing_Fly_Flap", FA), prep)
            cauda(base, -14, 5.0, onda_cauda(u, [(2.0, 1, 0.0, 1.0)]))
            if av <= 0: p = base
            else:
                bote = Pose(); em_pe(bote)
                bote.off += Vector((0, -0.03, 0.03)); bote.arf = -2
                fr, es, ci = eixos(bote)
                for c, pg in PERNAS.items():
                    Prel0, meta0, ded0 = ref_pata(bote, c)
                    if pg["tras"]: bote.pata[c] = dict(modo="livre", P=Prel0 - fr * 0.07 + ci * 0.05, meta=(-fr - ci * 0.3), dedos=-fr)
                    else: bote.pata[c] = dict(modo="livre", P=Prel0 + fr * 0.09 + ci * 0.07, meta=(fr - ci * 0.6), dedos=(fr * 0.5 - ci))
                pescoco_alto(bote, cima=-16, cab=-4)
                bote.asas = mistura(asas("Silverwing_Fly_Glide", 0.2), asas("Silverwing_Idle", 0.0), 0.45)
                cauda(bote, -4, 2.0, onda_cauda(u, [(1.5, 2, 0.0, 0.8)]), chao=False)
                p = mistura_pose(base, bote, av)
                asas_acima_do_chao(p, asas("Silverwing_Fly_Flap", FA))      # certificacao 02/11
        boca_abre(p, abre)
        return p
    return fn

def f_tempestade(u):
    """Tempestade de Asas terrestre 3,4 s: agacha e ergue as asas (0-0,32), IMPULSO (0,324: o servidor eleva o
    corpo), asas no maximo e torax arqueado, BATIDA devastadora (0,515), batidas de sustentacao, prepara o pouso e
    toca o chao (0,868), amortece e fecha as asas."""
    agach = janela(u, 0.0, 0.3) * (1 - janela(u, 0.3, 0.34))
    ar_w = janela(u, 0.31, 0.37) * (1 - janela(u, 0.82, 0.868))
    absorve = math.sin(math.pi * min(1, max(0, (u - 0.868) / 0.13)))
    # asas: dobradas -> alto -> segura -> golpe -> sustentacao -> planeio -> dobradas
    if u < 0.30: wa = mistura(asas("Silverwing_Idle", 0.0), asas("Silverwing_Fly_Flap", FA), smooth(u / 0.30))
    elif u < 0.47: wa = asas("Silverwing_Fly_Flap", FA + 0.03 * math.sin(2 * math.pi * 4 * u))
    elif u < 0.53: wa = asas("Silverwing_Fly_Flap", FA + 0.5 * smooth((u - 0.47) / 0.06))
    elif u < 0.80: wa = asas("Silverwing_Fly_Flap", FA + 0.5 + (u - 0.53) / 0.27 * 2.5)
    elif u < 0.90: wa = mistura(asas("Silverwing_Fly_Flap", FA + 0.5 + 2.5), asas("Silverwing_Fly_Glide", 0.2), smooth((u - 0.8) / 0.1))
    else: wa = mistura(asas("Silverwing_Fly_Glide", 0.2), asas("Silverwing_Idle", 0.0), smooth((u - 0.9) / 0.1))
    golpe = pulso(u, 0.47, 0.515, 0.54, 0.62)
    arco = pulso(u, 0.37, 0.46, 0.48, 0.52)
    chao = Pose(); em_pe(chao, agach=0.10 * agach)
    chao.off += Vector((0, 0, -0.05 * absorve)); chao.arf += 4 * absorve
    for c in chao.pata: chao.pata[c]["beta"] += 30 * absorve
    pescoco_alto(chao, cima=-12 * agach - 8 * absorve)
    cauda(chao, -14 + 8 * agach, 5.0, onda_cauda(u, [(2.0, 1, 0.0, 1.0)]))
    chao.asas = wa
    if ar_w <= 0: return chao
    ar = Pose(); ar.arf = 10 + 12 * arco - 10 * golpe
    ar.off = Vector((0, 0, 0.02 * arco - 0.03 * golpe))
    ar.curva["spine_1"] = (8 * arco - 6 * golpe, 0); ar.curva["spine_0"] = (-4 * golpe, 0)
    ar.asas = wa
    Rb = ar.Rb()
    for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): ar.extra[n] = Rax(Rb @ X, 14 * golpe - 6 * arco)
    recolhidas(ar, (u - 0.53) / 0.27 * 2.5 if u > 0.53 else 0.3, forte=1.4, pender=0.9 * janela(u, 0.75, 0.86))
    patas_vivas(ar, u, 1.2)
    pescoco_voo(ar, cima=-18 + 10 * arco - 14 * golpe, cab=-ar.arf * 0.2 - 4 * golpe)
    vert = [(6 * arco - 10 * math.sin(math.pi * min(1, max(0, (u - 0.5 - 0.02 * k) / 0.2)))) * PESO_CAUDA[k] for k in range(7)]
    cauda_ar(ar, -8, onda_cauda(u, [(5.0, 1, 0.5, 1.0), (2.0, 3, 1.1, 1.3)]), vert)
    boca_abre(ar, 0.5 * golpe)
    return mistura_pose(chao, ar, ar_w)

def f_tempestade_ar(u):
    """versao aerea 2,4 s (batida 0,417): pairando, ergue as asas ao maximo e arqueia (0-0,36), golpe (0,38-0,44),
    reacao do torax e da cauda, volta as batidas de sustentacao."""
    base = f_pairar((u * 2.4) % 1.0)
    arco = pulso(u, 0.0, 0.33, 0.38, 0.42); golpe = pulso(u, 0.38, 0.417, 0.45, 0.6)
    if u < 0.36: wa = mistura(base.asas, asas("Silverwing_Fly_Flap", FA), smooth(u / 0.33))
    elif u < 0.44: wa = asas("Silverwing_Fly_Flap", FA + 0.5 * smooth((u - 0.36) / 0.06))
    else: wa = mistura(asas("Silverwing_Fly_Flap", FA + 0.5 + (u - 0.44) * 3), base.asas, smooth((u - 0.6) / 0.4))
    base.asas = wa; base.arf += 8 * arco - 8 * golpe
    base.curva["spine_1"] = (8 * arco - 6 * golpe, 0)
    Rb = base.Rb()
    for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): base.extra[n] = Rax(Rb @ X, 22 + 14 * golpe - 6 * arco)
    pescoco_voo(base, cima=-30 + 10 * arco - 12 * golpe, cab=-base.arf * 0.2 - 4 * golpe)
    vert = [(6 * arco - 9 * math.sin(math.pi * min(1, max(0, (u - 0.41 - 0.02 * k) / 0.2)))) * PESO_CAUDA[k] for k in range(7)]
    cauda_ar(base, -12, onda_cauda(u, [(5.0, 1, 0.0, 1.0)]), vert)
    boca_abre(base, 0.5 * golpe)
    return base

# CORACAO INFERNAL (oficial 30/10; substitui a Ruptura no Montanhas). 4,2 s, casado com ConfigCombate.Coracao:
# carga 0-1,1 s (peito sobe e expande, pescoco recua e ergue, boca entreaberta) | expele 1,1-1,5 (pescoco projeta a
# cabeca, mandibula abre ao maximo, corpo empurra a frente) | giro 1,5-3,2 (a cabeca ACOMPANHA a lamina que gira ao
# redor do corpo: vira para o lado em que ela esta, ida e volta; tronco torce junto, cauda faz contrapeso) |
# dissipa 3,2-3,8 | recupera ate 4,2. Giro: 1,25 volta anti-horaria (sentido 1) com a mesma suavizacao do servidor.
CI_T = 4.2; CI_CARGA, CI_EXPELE, CI_GIRO, CI_VOLTAS = 1.1, 0.4, 1.7, 1.25
def _ci_ang(t):
    if t <= CI_CARGA + CI_EXPELE: return 0.0
    k = min(1.0, (t - CI_CARGA - CI_EXPELE) / CI_GIRO)
    return 2 * math.pi * CI_VOLTAS * (k * k * (3 - 2 * k))
def f_coracao(base_ar=False):
    def fn(u):
        t = u * CI_T
        carga = pulso(u, 0.0, 0.24, 0.255, 0.30)
        expele = pulso(u, 0.255, 0.30, 0.36, 0.46)
        giro = janela(u, 0.34, 0.40) * (1 - janela(u, 0.74, 0.86))
        rec = janela(u, 0.86, 1.0)
        ang = _ci_ang(t)
        segue = 46 * math.sin(ang) * giro                      # cabeca acompanha o lado em que a lamina esta
        boca = 0.18 * carga + 1.05 * expele + 0.45 * giro * (1 - janela(u, 0.62, 0.78))
        if base_ar:
            p = f_pairar(u * 3 % 1.0)
            p.arf += 6 * carga - 5 * expele
            pescoco_voo(p, cima=-30 + 14 * carga - 10 * expele, esq=segue, cab=-p.arf * 0.2 + 6 * carga - 10 * expele)
            p.curva["spine_0"] = (p.curva.get("spine_0", (0, 0))[0], -0.25 * segue)
        else:
            p = Pose(); em_pe(p, agach=0.03 * carga + 0.02 * expele)
            p.off += Vector((0, 0.015 * carga - 0.03 * expele, 0.008 * carga))
            p.arf += 7 * carga - 5 * expele
            pescoco_alto(p, cima=14 * carga - 12 * expele - 4 * giro, esq=segue, cab=6 * carga - 10 * expele)
            p.curva["spine_0"] = (-2 * expele, -0.3 * segue)
            if ASAS_ARMADAS: p.asas = asas_armadas(0.25 * carga + 0.15 * giro, math.sin(2 * math.pi * 3 * u))
            else: p.asas = asas_ameaca(0.4 * carga + 0.3 * giro)
            lat = [(-0.45 * segue) * PESO_CAUDA[k] for k in range(7)]
            cauda(p, -14 + 5 * carga, 5.0, somar(lat, onda_cauda(u, [(3.0, 1, 0.0, 1.0)])),
                  onda=[(4 * carga - 3 * expele) * PESO_CAUDA[k] for k in range(7)])
        p.curva["spine_1"] = (p.curva.get("spine_1", (0, 0))[0] + 7 * carga - 3 * expele, 0)   # peito expande na carga
        boca_abre(p, boca)
        return p
    return fn

def f_ruptura(u):
    """Ruptura Vulcanica 3,6 s: firma as traseiras, EMPINA (dianteiras sobem recolhidas, asas meio abertas, rugido),
    GOLPEIA o chao (contato 0,389), fica baixo enquanto a erupcao sobe (0,458) com as asas abertas, recupera."""
    empina = pulso(u, 0.10, 0.32, 0.33, 0.39)
    golpe = pulso(u, 0.36, 0.39, 0.70, 0.95)
    abre_asa = pulso(u, 0.12, 0.3, 0.7, 0.95)
    tr = math.sin(math.pi * min(1, max(0, (u - 0.389) / 0.1)))
    chao = Pose(); em_pe(chao, agach=0.03 * janela(u, 0, 0.1) * (1 - empina) + 0.06 * golpe)
    chao.arf += -5 * golpe - 2 * tr
    fr, es, ci = eixos(chao)
    for c in ("PD_E", "PD_D"): chao.pata[c]["K"] = chao.pata[c]["K"] + Vector((0, -0.03 * golpe, 0))   # dianteiras batem a frente
    pescoco_alto(chao, cima=-14 * golpe, cab=-6 * golpe)
    chao.asas = asas_ameaca(0.55 * abre_asa)
    cauda(chao, -14 + 6 * golpe, 5.0, onda_cauda(u, [(3.0, 1, 0.0, 1.0)]),
          onda=[(8 * empina - 6 * tr) * PESO_CAUDA[k] for k in range(7)])
    if empina <= 0: p = chao
    else:
        ref = Pose(); em_pe(ref); Rref = ref.Rb()
        alto = Pose(); em_pe(alto)
        alto.arf = 30; alto.off = Vector((0, 0.03, 0.05))
        fr, es, ci = eixos(alto); Ralto = alto.Rb()
        for c in ("PD_E", "PD_D"):
            # pata de apoio do repouso levada junto com o tronco empinado (no corpo), depois recolhida ao peito
            Prel0, meta0, ded0 = ref_pata(ref, c)
            Pc = Ralto @ (Rref.inverted() @ Prel0)
            alto.pata[c] = dict(modo="livre", P=Pc * 0.8 + ci * 0.03 + fr * 0.03, meta=(fr * 0.3 - ci), dedos=(fr * 0.6 - ci * 0.6))
        pescoco_alto(alto, cima=10, cab=4)
        alto.asas = chao.asas
        # tronco empinado 30 graus: a cauda sobe em relacao ao corpo para continuar rente ao chao (apoio/contrapeso)
        cauda(alto, 20, 2.0, onda_cauda(u, [(3.0, 1, 0.0, 1.0)]))
        p = mistura_pose(chao, alto, empina)
    boca_abre(p, pulso(u, 0.15, 0.3, 0.4, 0.5) * 0.9)
    return p

# ---------------------------------------------------------------- certificacao (02/11): clipes que a IA pedia e caiam em
# apelidos (Deitar/Deitado_Acordado -> Abaixar/Abaixado, Beber_Loop/Comer_Mastigar/Espreguicar -> Parado, Giro -> Andar)
# e animacoes GENERICAS de habilidade (Hab_*): so movimento, sem poder, dano, recarga ou efeito (kit de gelo pendente).
def pose_deitado(u, a=1.0, olhar=0.0, cima=0.0):
    """deitado ACORDADO: quatro patas flexionadas sob o corpo (AG_DEITADO), barriga no chao, pescoco erguido baixo
    (esfinge), cabeca nivelada, asas dobradas, cauda curvada ao lado"""
    p = Pose(); em_pe(p, agach=AG_DEITADO * a)
    r = math.sin(2 * math.pi * 2 * u)
    p.off += Vector((0, 0, 0.003 * r * a)); p.curva["spine_1"] = (1.0 * r * a, 0)
    pescoco_alto(p, cima=-14 * (1 - a) - 26 * a + cima + 1.2 * r, esq=olhar, cab=3 * a)
    p.asas = asas_descanso(a, r * a)
    enrola = [(8.0 * a) * PESO_CAUDA[k_] for k_ in range(7)]
    cauda(p, -16, 5.0, somar(enrola, onda_cauda(u, [(1.6 * a, 1, 0.3, 0.9), (0.8 * a, 3, 1.2, 1.2)])))
    asas_rente_chao(p, a)
    return p
def f_deitar(u):
    """em pe -> deitado 2,2 s: dianteiras flexionam primeiro e o torax desce, depois o quadril acomoda, a cauda curva
    e a cabeca baixa ate a posicao de descanso"""
    p = pose_deitado(u, smooth(u))
    frente = pulso(u, 0.0, 0.35, 0.55, 0.95)                    # a frente desce antes (nariz para baixo), o quadril segue
    p.arf -= 7 * frente; p.off += Vector((0, -0.006 * frente, 0))
    return p
def f_deitado_acordado(u):
    """8 s em laco: respiracao lenta, olhar em etapas (vira, segura), cabeca sobe as vezes, ponta da cauda viva"""
    esq = segura(u, [0, 20, 20, -14, -14, 4, 0], 0.6); cima = segura(u, [0, 4, 7, 2, 5, 0, 0], 0.6)
    return pose_deitado(u, 1.0, esq, cima)
def f_beber_loop(u):
    """Beber em laco 3 s (estado BebendoLongo): boca na agua, 6 lambidas com a mandibula, cabeca corrige de leve"""
    p = Pose(); base_pe(p, 1.0)
    lam = max(0.0, math.sin(2 * math.pi * 6 * u)) ** 2
    pescoco_ao_chao(p, 0.035 - 0.012 * lam, esq=3 * math.sin(2 * math.pi * u))
    boca_abre(p, 0.18 * lam)
    p.asas = asas("Silverwing_Idle", u)
    cauda(p, -14, 5.0, onda_cauda(u, [(-6.0, 1, 0.6, 0.95)]), onda=onda_cauda(u, [(1.2, 2, 0.3, 0.8)]))
    return p
def f_comer_mastigar(u):
    """Mastigar em laco 3 s: cabeca meio baixa, mandibula mastiga (rapido), pequenos trancos de engolir e correcoes"""
    p = Pose(); base_pe(p, 0.5)
    eng = pulso(u, 0.45, 0.52, 0.56, 0.66)
    pescoco_ao_chao(p, 0.22 + 0.02 * eng, esq=4 * math.sin(2 * math.pi * u + 0.5), cab_extra=4 * eng)
    boca_abre(p, 0.22 * (0.5 + 0.5 * math.sin(2 * math.pi * 9 * u)) * (1 - eng))
    p.asas = asas("Silverwing_Idle", u)
    cauda(p, -14, 5.0, onda_cauda(u, [(-5.0, 1, 0.2, 0.95), (2.0, 2, 1.1, 1.2)]))
    return p
def f_espreguicar(u):
    """Espreguicar 4 s: dianteiras avancam em passo, peito desce e quadril sobe (dorso arqueado), pescoco estica, asas
    abrem e tremem, bocejo; recolhe tudo e volta"""
    est = pulso(u, 0.12, 0.38, 0.62, 0.86)
    p = Pose(); em_pe(p)
    passo = {"PD_E": pulso(u, 0.02, 0.14, 0.86, 0.96), "PD_D": pulso(u, 0.08, 0.2, 0.9, 1.0)}
    for c, k in passo.items():
        p.pata[c]["K"].y -= 0.11 * k
        if 0 < k < 1: p.pata[c]["K"].z += 0.035 * math.sin(math.pi * k)
        p.pata[c]["beta"] += 24 * est
    # (teste no Studio 02/11: com -12 graus parecia so exibicao de asas) peito bem baixo, garupa alta, dorso arqueado
    p.arf -= 19 * est; p.off += Vector((0, -0.012 * est, -0.028 * est))
    p.curva["spine_1"] = (-9 * est, 0); p.curva["spine_0"] = (7 * est, 0)
    boce = pulso(u, 0.36, 0.46, 0.56, 0.66)
    pescoco_alto(p, cima=-12 + 22 * est - 10 * boce, cab=-6 * est + 10 * boce)
    boca_abre(p, 0.95 * boce)
    p.asas = asas_ameaca(0.7 * est + 0.03 * est * math.sin(2 * math.pi * 9 * u))
    cauda(p, -12 + 10 * est, 5.0, onda_cauda(u, [(3.0, 1, 0.3, 1.0)]), onda=[6 * est * PESO_CAUDA[k] for k in range(7)])
    return p
def f_giro(lado):
    """girar no lugar (o Locomotor gira o modelo): passos SEM avanco (pe nao desliza), cabeca guia a curva, tronco e
    cauda acompanham com atraso para o lado de fora"""
    sg = 1 if lado == "E" else -1
    base = andadura(T_ANDAR, D_ANDAR, 0.0001, {"PT_E": 0.0, "PD_E": 0.25, "PT_D": 0.5, "PD_D": 0.75}, 0.045, 0.04,
                    0.004, 1.5, 0.0)
    def fn(u):
        p = base(u)
        p.curva["spine_0"] = (p.curva["spine_0"][0], 4 * sg); p.curva["spine_1"] = (p.curva["spine_1"][0], 3 * sg)
        pescoco_alto(p, cima=-22 + 2 * math.cos(4 * math.pi * u), esq=20 * sg, cab=0)
        cauda(p, -12, 4.5, somar([-sg * 2.5 * k for k in range(7)], onda_cauda(u, [(4.0, 1, -0.4, 0.8)])), onda=onda_cauda(u, [(1.2, 2, 0.0, 0.6)]))
        return p
    return fn
def f_hab_concentracao(u):
    """Concentracao elemental 3 s (laco): frente baixa e firme, cabeca recolhida e baixa, asas meio erguidas com
    tremor fino, respiracao profunda (2 por clipe), boca entreaberta, cauda tensa quase parada"""
    r = math.sin(2 * math.pi * 2 * u)
    p = Pose(); base_pe(p, 0.35)
    for c in PERNAS: p.pata[c]["beta"] += 5
    p.off += Vector((0, 0.006, -0.008 + 0.003 * r)); p.arf += 1.5 * r
    p.curva["spine_1"] = (4 + 3 * r, 0)
    pescoco_alto(p, cima=-20 + 3 * r, esq=1.5 * math.sin(2 * math.pi * 7 * u), cab=8)
    for i, n_ in enumerate(PESCOCO):
        c_, e_ = p.curva[n_]; p.curva[n_] = (c_ + [8, 0, -8][i], e_)
    boca_abre(p, 0.10 + 0.05 * max(0.0, r))
    p.asas = asas_ameaca(0.38 + 0.025 * math.sin(2 * math.pi * 11 * u))
    cauda(p, -10, 5.0, onda_cauda(u, [(1.5, 1, 0.3, 1.0), (0.6, 5, 0.0, 1.4)]), onda=[3 * PESO_CAUDA[k] for k in range(7)])
    return p
def f_hab_golpe_garras(u):
    """Golpe com garras 2,2 s: garra esquerda (contato 0,24) e direita (contato 0,74) em sequencia"""
    return f_ataque_garra("E")(u * 2) if u < 0.5 else f_ataque_garra("D")((u - 0.5) * 2)
def f_hab_recuperacao(u):
    """Recuperacao pos-habilidade 1,6 s: sacode a cabeca (amortecido), solta o ar (peito baixa), fecha a boca,
    recolhe as asas e assenta o corpo"""
    sac = math.sin(2 * math.pi * 3 * u) * (1 - janela(u, 0.1, 0.7)) * janela(u, 0.0, 0.08)
    sol = pulso(u, 0.05, 0.3, 0.45, 0.9)
    p = Pose(); em_pe(p)
    p.arf -= 3 * sol; p.off += Vector((0, 0, -0.008 * sol))
    p.curva["spine_1"] = (-3 * sol, 0)
    pescoco_alto(p, cima=-16 * sol, esq=14 * sac, cab=4 * sol)
    boca_abre(p, 0.25 * (1 - janela(u, 0.0, 0.5)))
    p.asas = asas_ameaca(0.35 * (1 - janela(u, 0.1, 0.8)))
    cauda(p, -14, 5.0, onda_cauda(u, [(3.0, 1, 0.0, 1.0)]), onda=[3 * (1 - u) * PESO_CAUDA[k] for k in range(7)])
    return p

# ---------------------------------------------------------------- KIT DO GELO (oficial 02/11, Dragao Glacial)
# Sopro Glacial (Sopro_Glacial_*), Rajadas de Gelo, Zero Absoluto e Nevasca Ancestral. Tempos casados com
# ConfigCombate (Glacial): Rajadas 2,4 s com disparos em 0,72/1,08/1,44/1,80 s; Zero Absoluto 2,8 s com a descarga
# em 1,06 s; Nevasca 5,6 s (salto 0,5 s, rugido 1,75 s, ondas 2,2-4,3 s, pouso 4,7-5,4 s no solo). "_Camada" = no ar.
RAJ_TIROS = [0.30, 0.45, 0.60, 0.75]
def f_rajadas(ar=False):
    """Rajadas de Gelo 2,4 s: pescoco recolhe em S e a cabeca MIRA (preparo), 4 disparos ritmados: a boca estala
    aberta, a cabeca recua e o peito da um tranco a cada tiro; asas meio armadas estabilizam; recupera."""
    def fn(u):
        prep = janela(u, 0.0, 0.25) * (1 - janela(u, 0.82, 1.0))
        rec = sum(math.exp(-((u - t - 0.03) / 0.04) ** 2) for t in RAJ_TIROS)
        abre = min(1.0, sum(pulso(u, t - 0.045, t - 0.005, t + 0.03, t + 0.085) for t in RAJ_TIROS))
        if ar:
            p = f_pairar((u * 2.0) % 1.0)
            p.arf += 3 * rec
            pescoco_voo(p, cima=-30 + 6 * prep - 5 * rec, cab=-p.arf * 0.2 - 4 * prep + 6 * rec)
        else:
            p = Pose(); base_pe(p, 0.3 * prep)
            for c in PERNAS: p.pata[c]["beta"] += 5 * prep
            p.off += Vector((0, 0.010 * prep + 0.012 * rec, 0.004 * rec))
            p.arf += 2 * prep + 2.5 * rec
            pescoco_alto(p, cima=-10 * prep + 4 * rec, cab=-6 * prep + 7 * rec)
            for i, n_ in enumerate(PESCOCO):                                     # S de mira (soma 0)
                c_, e_ = p.curva[n_]; p.curva[n_] = (c_ + [7, 0, -7][i] * prep, e_)
            p.asas = asas_ameaca(0.28 * prep + 0.04 * rec)
            cauda(p, -10 + 3 * prep, 5.0, onda_cauda(u, [(1.6, 1, 0.3, 1.0)]), onda=[(2 * prep + 3 * rec) * PESO_CAUDA[k] for k in range(7)])
        p.curva["spine_1"] = (p.curva.get("spine_1", (0, 0))[0] + 3 * prep - 3 * rec, 0)
        boca_abre(p, 0.12 * prep + 0.75 * abre)
        return p
    return fn

def f_zero_absoluto(ar=False):
    """Zero Absoluto 2,8 s: tensao (abaixa, asas sobem tremendo, peito enche, pescoco recolhe) -> DESCARGA em 0,38
    (corpo cai sobre as patas, asas abrem ao maximo, cabeca baixa e a frente com a boca aberta, cauda bate) ->
    sustenta com tremor fino -> recupera."""
    def fn(u):
        prep = janela(u, 0.0, 0.34) * (1 - janela(u, 0.36, 0.40))
        desc = pulso(u, 0.36, 0.40, 0.62, 0.86)
        choque = math.exp(-((u - 0.39) / 0.03) ** 2)
        trem = math.sin(2 * math.pi * 26 * u) * (prep * 0.6 + desc * 0.4)
        if ar:
            p = f_pairar((u * 2.2) % 1.0)
            p.arf += -6 * prep + 10 * desc
            Rb = p.Rb()
            for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): p.extra[n] = Rax(Rb @ X, 22 + 14 * desc - 8 * prep)
            p.asas = mistura(p.asas, asas("Silverwing_Fly_Glide", 0.2), 0.7 * desc)
            pescoco_voo(p, cima=-34 - 10 * desc + 0.5 * trem, cab=-p.arf * 0.2 - 6 * desc)
        else:
            p = Pose(); em_pe(p, agach=0.035 * prep + 0.07 * desc)
            for c in PERNAS: p.pata[c]["beta"] += 6 * desc
            p.off += Vector((0, 0, -0.012 * choque))
            p.arf += 3 * prep - 4 * desc
            pescoco_alto(p, cima=-12 * prep - 20 * desc + 0.6 * trem, esq=0.4 * trem, cab=6 * prep - 4 * desc)
            p.asas = asas_ameaca(0.45 * prep + 0.95 * desc + 0.03 * trem * prep)
            vert = [(-6 * choque + 7 * desc * math.sin(math.pi * min(1, max(0, (u - 0.40 - 0.02 * k) / 0.25)))) * PESO_CAUDA[k] for k in range(7)]
            cauda(p, -12 - 4 * prep + 8 * desc, 5.0, onda_cauda(u, [(2.0, 1, 0.0, 1.0), (1.0, 7, 0.4, 1.3)]), onda=vert)
        p.curva["spine_1"] = (p.curva.get("spine_1", (0, 0))[0] + 6 * prep - 4 * desc + 0.5 * trem, 0)
        boca_abre(p, 0.15 * prep + 0.85 * desc, tranco=0.3 * trem)
        return p
    return fn

def f_nevasca(ar=False):
    """Nevasca Ancestral 5,6 s (ultimate): solo = agacha e SALTA (o servidor ergue o corpo), ar = batidas fortes; o
    corpo se ergue com o peito ao alto, RUGE para o ceu, asas abrem e sustentam a descarga (tremor de esforco no corpo
    todo, cauda baixa), recupera; no solo desce, estende as patas e amortece o pouso."""
    def fn(u):
        ag = janela(u, 0.0, 0.08) * (1 - janela(u, 0.08, 0.12))
        ergue = pulso(u, 0.22, 0.31, 0.78, 0.9)
        rug = pulso(u, 0.30, 0.34, 0.50, 0.58)
        desc = pulso(u, 0.35, 0.42, 0.76, 0.86)
        trem = math.sin(2 * math.pi * 30 * u) * desc
        ar_ = f_pairar((u * 4.0) % 1.0)
        ar_.arf += 14 * ergue
        aberta = mistura(asas("Silverwing_Fly_Glide", 0.2), asas("Silverwing_Fly_Flap", FA), 0.35)
        ar_.asas = mistura(ar_.asas, aberta, 0.85 * desc)
        Rb = ar_.Rb()
        for s_, n in ((1, "shoulder_l"), (-1, "shoulder_r")): ar_.extra[n] = Rax(Rb @ X, 22 + 14 * PENDULO - 18 * desc)
        pescoco_voo(ar_, cima=-30 - 18 * PENDULO + 40 * ergue + 18 * rug + 0.8 * trem, esq=0.6 * trem, cab=-ar_.arf * 0.3 + 14 * rug)
        ar_.curva["spine_1"] = (ar_.curva.get("spine_1", (0, 0))[0] + 8 * ergue + 1.2 * trem, 0)
        boca_abre(ar_, 0.2 * ergue + 1.05 * rug + 0.35 * desc * (1 - rug), tranco=0.4 * trem)
        vert = [(-8 * desc + 3 * math.sin(2 * math.pi * 3 * u - 0.5 * k)) * PESO_CAUDA[k] for k in range(7)]
        cauda_ar(ar_, -14 - 10 * desc, onda_cauda(u, [(6.0, 2, 0.3, 1.0), (2.0, 5, 1.1, 1.3)]), vert)
        if ar: return ar_
        chao = Pose(); em_pe(chao, agach=0.07 * ag)
        absorve = math.sin(math.pi * min(1, max(0, (u - 0.93) / 0.07)))
        chao.off += Vector((0, 0, -0.04 * absorve)); chao.arf += 6 * ag + 4 * absorve
        for c in chao.pata: chao.pata[c]["beta"] += 28 * ag + 28 * absorve
        pescoco_alto(chao, cima=-10 * ag + 10 * janela(u, 0.06, 0.12) - 8 * absorve)
        chao.asas = (mistura(asas("Silverwing_Idle", 0.0), asas("Silverwing_Fly_Flap", FA), janela(u, 0.0, 0.09)) if u < 0.5
                     else mistura(asas("Silverwing_Fly_Glide", 0.2), asas("Silverwing_Idle", 0.0), janela(u, 0.92, 1.0)))
        cauda(chao, -12 + 8 * ag, 5.0, onda_cauda(u, [(2.0, 1, 0.0, 1.0)]))
        w = janela(u, 0.08, 0.16) * (1 - janela(u, 0.86, 0.95))
        p = chao if w <= 0 else (ar_ if w >= 1 else mistura_pose(chao, ar_, w))
        if u < 0.22 or u > 0.84:                       # perto do chao (antes do corpo subir / no pouso): asas e cauda acima
            asas_acima_do_chao(p, asas("Silverwing_Fly_Flap", FA)); cauda_sobre_chao(p)
        return p
    return fn

# ---------------------------------------------------------------- gerar
if PEDIDOS == {"DEBUG"}:
    p = f_parado(0.0); W, B = resolver(p)
    act = bpy.data.actions["Silverwing_Parado"]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    sc.frame_set(1)
    for n_ in ["hips", "spine_0", "spine_1", "collar_anchor_l", "front_leg_collar_l", "front_leg_l", "front_ankle_l", "front_foot_l", "front_toes_l"]:
        pb = A.pose.bones[n_]; bo = A.data.bones[n_]
        print("DBG", n_, "calc", tuple(round(c, 4) for c in W[n_].translation), "blender", tuple(round(c, 4) for c in pb.head),
              "inhRot", bo.use_inherit_rotation, "inhScale", bo.inherit_scale, "localLoc", bo.use_local_location, "constr", len(pb.constraints), "rotmode", pb.rotation_mode)
    raise SystemExit
def n(seg): return max(2, int(round(seg * FPS)))
gerar("Parado", n(8.0), f_parado)
gerar("Andar", n(T_ANDAR), f_andar)
gerar("Correr", n(T_CORRER), f_correr)
gerar("Parada", n(0.6), f_parada, loop=False)
gerar("Abaixar", n(0.7), f_agachar(0, 1), loop=False)
gerar("Abaixado", n(3.0), f_agachar(1, 1))
gerar("Sentar", n(1.6), f_sentar, loop=False)
gerar("Sentado", n(8.0), f_sentado)
gerar("Levantar_Sentado", n(1.2), f_levantar_sentado, loop=False)
gerar("Levantar", n(0.7), f_agachar(1, 0), loop=False)
for lado_, suf_ in (("l", "E"), ("r", "D")):                         # (06/11) montar: asa do lado do cavaleiro em rampa
    gerar("Abaixar_Rampa_" + suf_, n(1.0), f_agachar(0, 1, rampa=lado_), loop=False)
    gerar("Abaixado_Rampa_" + suf_, n(3.0), f_agachar(1, 1, rampa=lado_))
    gerar("Levantar_Rampa_" + suf_, n(1.0), f_agachar(1, 0, rampa=lado_), loop=False)
# voo: 4 batidas por clipe (mesmo ritmo de antes) para a cauda/patas terem movimento LENTO e nao repetitivo
gerar("Voo", n(T_VOO), lambda u: f_voo(u, NB_VOO, u))
gerar("Voo_Rapido", n(3.2), lambda u: f_voo_rapido(u, 5, u))
gerar("Pairar", n(T_PAIRAR), lambda u: f_pairar(u, NB_PAIRAR, u))
gerar("Subida", n(2.8), lambda u: f_subida(u, 4, u))
gerar("Descida", n(4.0), f_descida)
gerar("Planeio", n(4.0), f_planeio)
gerar("Curva_E", n(4.0), f_curva("E"))
gerar("Curva_D", n(4.0), f_curva("D"))
gerar("Mergulho", n(2.0), f_mergulho)
gerar("Decolagem", n(1.0), f_decolagem, loop=False)
gerar("Pouso", n(0.5), f_pouso, loop=False)
gerar("Mordida_Aerea", n(1.0), f_mordida, loop=False)
# combate (nomes = os que o Nucleo pede; "_Camada" = versao no ar)
gerar("Ataque_Mordida", n(1.4), f_ataque_mordida, loop=False)
gerar("Ataque_Garra_E", n(1.5), f_ataque_garra("E"), loop=False)
gerar("Ataque_Garra_D", n(1.5), f_ataque_garra("D"), loop=False)
gerar("Ataque_Cauda", n(1.8), f_ataque_cauda, loop=False)
if ROAR_ESTILO == "fogo":                     # rugidos proprios do Fogo (02/11); o Gelo segue com o padrao v2
    gerar("Rugido_Combate", n(1.6), f_rugido_combate_fogo, loop=False)
    gerar("Rugido_Ameaca", n(3.0), f_rugido_ameaca, loop=False)
    gerar("Rugido_Aereo", n(2.4), f_rugido_aereo, loop=False)
    gerar("Rugido_Vitoria", n(3.6), f_rugido_vitoria, loop=False)
else:
    gerar("Rugido_Combate", n(2.6), f_rugido(False), loop=False)
gerar("Rugido_Combate_Camada", n(2.6), f_rugido(True), loop=False)
for ar_, suf in ((False, ""), (True, "_Camada")):
    gerar("Sopro_Inicio" + suf, n(1.2), f_sopro("Inicio", ar_), loop=False)
    gerar("Sopro_Loop" + suf, n(0.9), f_sopro("Loop", ar_))
    gerar("Sopro_Fim" + suf, n(0.8), f_sopro("Fim", ar_), loop=False)
    gerar("Arremetida" + suf, n(2.1), f_arremetida(ar_), loop=False)
gerar("Tempestade_Asas", n(3.4), f_tempestade, loop=False)
gerar("Tempestade_Asas_Ar", n(2.4), f_tempestade_ar, loop=False)
gerar("Ruptura_Vulcanica", n(3.6), f_ruptura, loop=False)
gerar("Coracao_Infernal", n(CI_T), f_coracao(False), loop=False)
gerar("Coracao_Infernal_Camada", n(CI_T), f_coracao(True), loop=False)
# comportamento natural da IA selvagem (nomes logicos do EstadosDragao)
gerar("Beber", n(9.0), f_beber, loop=False)
gerar("Comer", n(8.5), f_comer, loop=False)
gerar("Observar", n(7.0), f_observar)
gerar("Observar_Farejar", n(2.5), f_farejar, loop=False)
gerar("Reagir_Estimulo", n(1.2), f_reagir, loop=False)
gerar("Idle_Alerta_Mantido", n(4.0), f_alerta)
gerar("Ninho_Ameaca", n(4.6), f_ameaca, loop=False)
gerar("Preparar_Combate", n(3.0), f_preparar_combate)
gerar("Adormecer", n(2.5), f_adormecer, loop=False)
gerar("Dormir", n(8.0), f_dormir)
gerar("Acordar", n(2.0), f_acordar, loop=False)
gerar("Ninho_Alerta", n(1.2), f_ninho_alerta, loop=False)
# sistema universal (01/11): comportamento, dano e recuperacao do mergulho
gerar("Rugido_Territorial", n(4.2), f_rugido_territorial, loop=False)
gerar("Intimidar", n(3.6), f_intimidar)
gerar("Curiosidade", n(5.0), f_curiosidade, loop=False)
gerar("Dano_Leve", n(0.6), f_dano(False), loop=False)
gerar("Dano_Forte", n(1.1), f_dano(True), loop=False)
gerar("Dano_Leve_Ar", n(0.6), f_dano(False, True), loop=False)
gerar("Dano_Forte_Ar", n(1.1), f_dano(True, True), loop=False)
gerar("Mergulho_Saida", n(1.2), f_mergulho_saida, loop=False)
gerar("Mergulho_Picado", n(1.0), f_picado_v2 if MERG_V2 else f_mergulho_picado)
if MERG_V2:                                                          # (10/11) so o Sombrio: clipes proprios da manobra
    gerar("Mergulho_Entrada", n(0.55), f_mergulho_entrada, loop=False)
    gerar("Mergulho_Freio", n(1.2), f_mergulho_freio, loop=False)
# certificacao 02/11: estados da IA sem clipe proprio + animacoes genericas de habilidade (nenhum poder ligado)
gerar("Deitar", n(2.2), f_deitar, loop=False)
gerar("Deitado_Acordado", n(8.0), f_deitado_acordado)
gerar("Beber_Loop", n(3.0), f_beber_loop)
gerar("Comer_Mastigar", n(3.0), f_comer_mastigar)
gerar("Espreguicar", n(4.0), f_espreguicar, loop=False)
gerar("Giro_E", n(T_ANDAR), f_giro("E"))
gerar("Giro_D", n(T_ANDAR), f_giro("D"))
gerar("Hab_Concentracao", n(3.0), f_hab_concentracao)
for ar_, suf in ((False, ""), (True, "_Ar")):
    gerar("Hab_Preparo_Respiratorio" + suf, n(1.2), f_sopro("Inicio", ar_), loop=False)
    gerar("Hab_Emissao_Loop" + suf, n(0.9), f_sopro("Loop", ar_))
    gerar("Hab_Emissao_Fim" + suf, n(0.8), f_sopro("Fim", ar_), loop=False)
    gerar("Hab_Investida" + suf, n(2.1), f_arremetida(ar_), loop=False)
gerar("Hab_Golpe_Garras", n(2.2), f_hab_golpe_garras, loop=False)
gerar("Hab_Area", n(3.4), f_tempestade, loop=False)
gerar("Hab_Area_Ar", n(2.4), f_tempestade_ar, loop=False)
gerar("Hab_Recuperacao", n(1.6), f_hab_recuperacao, loop=False)
# kit do gelo (oficial 02/11)
for ar_, suf in ((False, ""), (True, "_Camada")):
    gerar("Sopro_Glacial_Inicio" + suf, n(1.2), f_sopro("Inicio", ar_), loop=False)
    gerar("Sopro_Glacial_Loop" + suf, n(0.9), f_sopro("Loop", ar_))
    gerar("Sopro_Glacial_Fim" + suf, n(0.8), f_sopro("Fim", ar_), loop=False)
    gerar("Rajadas_Gelo" + suf, n(2.4), f_rajadas(ar_), loop=False)
    gerar("Zero_Absoluto" + suf, n(2.8), f_zero_absoluto(ar_), loop=False)
    gerar("Nevasca_Ancestral" + suf, n(5.6), f_nevasca(ar_), loop=False)
print("VEL_ANDAR studs/s", round(S_ANDAR / (D_ANDAR * T_ANDAR) * 17.5, 2), "VEL_CORRER", round(S_CORRER / (D_CORRER * T_CORRER) * 17.5, 2))
for m in M.modifiers: m.show_viewport = True
bpy.ops.wm.save_mainfile()
print("ANIM_OK")
