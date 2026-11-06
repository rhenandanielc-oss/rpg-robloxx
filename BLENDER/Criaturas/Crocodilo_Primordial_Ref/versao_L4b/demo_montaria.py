"""Lote 4: DEMONSTRACAO do cavaleiro de teste (manequim R15 aproximado) montando e desmontando pelo lado ESQUERDO (+X)
do crocodilo - lado escolhido so para o teste, nao e regra de jogo. O crocodilo toca as acoes Croc_Montar/Croc_Desmontar
(as mesmas dos JSON); o manequim e animado por alvos (quadril, maos, pes) com IK e assado em FK nas acoes
DEMO_Cav_Montar / DEMO_Cav_Desmontar / DEMO_Cav_Sentado. Apoios no crocodilo (maos no dorso, pe no cotovelo) sao
pontos medidos na pele na pose baixa e acompanham o osso do dorso/braco. Nao e animacao R15 publicada.
Salva CR_Crocodilo_Montaria_Teste.blend (cena de teste: crocodilo + sela PROPOSTA + manequim) ao lado do .blend aberto.
Uso: blender -b CR_Crocodilo_Anim.blend -P demo_montaria.py -- [saida_qa.json]"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix as M, Quaternion as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manequim_r15 as mq
A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
croc = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]
for pb in croc.pose.bones:
    for c in pb.constraints: c.mute = True
if not croc.animation_data: croc.animation_data_create()
def croc_quadro(nome, t):
    act = bpy.data.actions["Croc_" + nome]; croc.animation_data.action = act; croc.animation_data.action_slot = act.slots[0]
    sc.frame_set(1 + int(round(t * FPS))); bpy.context.view_layer.update()
# ------------------------------------------------------------------ cena: sela PROPOSTA presa ao osso e manequim
col = bpy.data.collections.new("TESTE_Montaria_L4"); sc.collection.children.link(col)
croc.animation_data.action = None
for pb in croc.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
sela, Z_TOPO, _, _ = mq.criar_sela(croc, lo, col)
mw = sela.matrix_world.copy(); sela.parent = croc; sela.parent_type = "BONE"; sela.parent_bone = mq.OSSO_ASSENTO
bpy.context.view_layer.update(); sela.matrix_world = mw
ra, ob, alvos = mq.criar(col)
Z_Q = Z_TOPO + 0.65                                    # quadril 0,65 acima do topo da sela (estudo de encaixe)
def assento(): return mq.assento_mundo(croc, Z_Q)
# ------------------------------------------------------------------ curvas
def herm(t, pts):
    """Hermite por chaves (t, valor) com tangentes de Catmull-Rom (zero nas pontas) - valor escalar ou Vector"""
    if t <= pts[0][0]: return pts[0][1]
    if t >= pts[-1][0]: return pts[-1][1]
    for i in range(len(pts) - 1):
        (t0, p0), (t1, p1) = pts[i], pts[i + 1]
        if t <= t1: break
    def tg(j):
        if j <= 0 or j >= len(pts) - 1: return p0 * 0
        return (pts[j + 1][1] - pts[j - 1][1]) / (pts[j + 1][0] - pts[j - 1][0])
    h = t1 - t0; u = (t - t0) / h; m0, m1 = tg(i) * h, tg(i + 1) * h
    return (2 * u ** 3 - 3 * u ** 2 + 1) * p0 + (u ** 3 - 2 * u ** 2 + u) * m0 + (-2 * u ** 3 + 3 * u ** 2) * p1 + (u ** 3 - u ** 2) * m1
def s_(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def Rz(g): return Q(V((0, 0, 1)), math.radians(g))
def Rx(g): return Q(V((1, 0, 0)), math.radians(g))
def passo(t, t0, t1, a, b, alt=0.45):
    """pe no chao de a ate b entre t0 e t1 (eleva no meio)"""
    u = s_((t - t0) / (t1 - t0)); p = a.lerp(b, u); p.z += alt * math.sin(math.pi * u); return p
# ------------------------------------------------------------------ pontos de apoio medidos na pele (pose baixa)
from mathutils.bvhtree import BVHTree
def pele(x, y, osso, alvo=None):
    """ponto e normal da pele (ou da sela) sob (x, y) na pose atual, guardados no espaco do osso (acompanham o osso)"""
    if alvo is None: bvh = mq.bvh_croc(lo); Mi = M.Identity(4)
    else: bvh = BVHTree.FromObject(alvo, bpy.context.evaluated_depsgraph_get()); Mi = alvo.matrix_world
    hit = bvh.ray_cast(Mi.inverted() @ V((x, y, 12.0)), (Mi.inverted().to_3x3() @ V((0, 0, -1))).normalized())
    if hit[0] is None: loc, nor = bvh.find_nearest(Mi.inverted() @ V((x, y, 3.0)))[:2]   # sem pele na vertical: ponto mais proximo
    else: loc, nor = hit[0], hit[1]
    loc = Mi @ loc; nor = (Mi.to_3x3() @ nor).normalized()
    if nor.z < 0: nor = -nor
    pb = croc.pose.bones[osso]; Mb = croc.matrix_world @ pb.matrix
    return (osso, Mb.inverted() @ loc, Mb.inverted().to_3x3() @ nor)
def no_osso(ap, d=0.0):
    """posicao do apoio no mundo, afastada d ao longo da normal"""
    osso, p, n = ap; Mb = croc.matrix_world @ croc.pose.bones[osso].matrix
    return Mb @ p + (Mb.to_3x3() @ n).normalized() * d
def q_apoio(ap, R):
    """orientacao da mao/pe deitada na superficie: eixo fino da caixa (Z) na normal, guinada do corpo"""
    osso, p, n = ap; Mb = croc.matrix_world @ croc.pose.bones[osso].matrix
    return V((0, 0, 1)).rotation_difference((Mb.to_3x3() @ n).normalized()) @ R
croc_quadro("Montar", 1.5)                               # pose baixa (apoios medidos nela)
# subida pela pata dianteira E: pe no cotovelo, maos no ombro/flanco e depois na borda do dorso; perna D por cima da garupa
AP = {"cotovelo": pele(4.25, -7.3, "BracoE"), "cot_tras": pele(4.1, -6.1, "BracoE"),
      "mao_ombro": pele(3.35, -7.15, "BracoE"), "mao_flanco": pele(2.78, -5.48, "Coluna2"),
      "mao_E2": pele(2.1, -6.6, "Coluna2"), "mao_D2": pele(2.0, -5.2, "Coluna1"),
      "borda_E": pele(1.8, -5.0, "Coluna1"), "borda_D": pele(1.8, -3.4, "Coluna1")}
for k, (x, y) in {"sela_E": (1.15, -5.1), "sela_D": (1.15, -3.9), "sela_D2": (-1.0, -3.9)}.items():
    AP[k] = pele(x, y, "Coluna1", sela)
print("APOIOS", {k: [round(c, 2) for c in no_osso(v)] for k, v in AP.items()})
MAO = 0.33; TORN = 0.33; FOLGA_PE = 0.62                 # punho/tornozelo sobre a superficie (caixa 0,3) / pe fora do flanco
BV = {"q": None, "bvh": None}
def flanco(y, z):
    """x da pele do lado +X na altura z (raio de fora para dentro); 0 se nao houver pele"""
    q = sc.frame_current
    if BV["q"] != q: BV["bvh"] = mq.bvh_croc(lo); BV["q"] = q
    hit = BV["bvh"].ray_cast(V((9.0, y, z)), V((-1, 0, 0))); return hit[0].x if hit[0] else 0.0
def fora(p):
    """empurra o tornozelo para fora do flanco (o pe desliza encostado, nao atravessa)"""
    fx = max(flanco(p.y + d, p.z + dz) for d in (-0.45, 0.0, 0.45) for dz in (-0.25, 0.1))
    return V((max(p.x, fx + FOLGA_PE), p.y, p.z))
def livre(P, psi, tronco, cabeca, alvos_):
    """estado com quadril no mundo: P posicao, psi guinada (0 = de frente para -Y; -90 = de frente para -X)"""
    R = Rz(psi); Mp = M.Translation(P) @ R.to_matrix().to_4x4()
    est = {"pelve": Mp, "tronco": tronco, "cabeca": cabeca, "alvos": {}}
    for lado, s in (("Left", 1), ("Right", -1)):
        est["alvos"][("Polo", lado + "Foot")] = (Mp @ V((0.6 * s, -3.0, 0.8)), R)
        est["alvos"][("Polo", lado + "Hand")] = (Mp @ V((2.2 * s, 2.0, 1.5)), R)
    for k, v in alvos_.items(): est["alvos"][k] = v
    return est
def solto(Mp, lado):         # mao pendurada ao lado do corpo
    s = 1 if lado == "Left" else -1; return Mp @ V((1.55 * s, 0.05, 0.1))
def trilha(t, chaves, R, d):
    """chaves (t, apoio | ponto) -> (posicao, orientacao). Apoio: ponto da pele afastado d na normal, mao/pe deitado nela;
    ponto livre: orientacao R. Posicao por Hermite; orientacao interpolada entre as chaves vizinhas."""
    ps = [(tk, (no_osso(v, d) if isinstance(v, tuple) else v)) for tk, v in chaves]
    qs = [(q_apoio(v, R) if isinstance(v, tuple) else R) for _, v in chaves]
    p = herm(t, ps)
    if t <= chaves[0][0]: return p, qs[0]
    for i in range(len(chaves) - 1):
        if t <= chaves[i + 1][0]: return p, qs[i].slerp(qs[i + 1], s_((t - chaves[i][0]) / (chaves[i + 1][0] - chaves[i][0])))
    return p, qs[-1]
N_FLANCO = V((0, 0, 1)).rotation_difference(V((1, 0, 0)))
def mao_no_flanco(Mp, R, lado, frente=1.25, alt=1.75):
    """mao espalmada no flanco +X a frente do ombro (empurra/apoia): ponto empurrado para fora da pele, palma na normal +X"""
    s = 1 if lado == "Left" else -1; p = Mp @ V((0.95 * s, -frente, alt))
    fx = max(flanco(p.y + d, p.z + dz) for d in (-0.55, -0.2, 0.2, 0.55) for dz in (-0.55, -0.2, 0.2, 0.55))
    return (V((max(p.x, fx + 0.36), p.y, p.z)), N_FLANCO @ R)
def meio(a, b, dz, d=MAO):
    pa = no_osso(a, d) if isinstance(a, tuple) else a; pb_ = no_osso(b, d) if isinstance(b, tuple) else b
    return pa.lerp(pb_, 0.5) + V((0, 0, dz))
# ------------------------------------------------------------------ MONTAR (4,0 s; chega pela esquerda olhando para -X e sobe pela pata dianteira E)
def montar(t):
    S = mq.estado_sentado(assento()); Ms = S["pelve"]
    P = herm(t, [(0.0, V((7.9, -6.2, 2.0))), (0.8, V((5.7, -6.2, 2.0))), (1.0, V((5.6, -6.2, 1.95))), (1.35, V((5.3, -6.3, 2.35))),
                 (1.7, V((4.75, -6.3, 3.55))), (2.05, V((4.05, -6.0, 4.75))), (2.35, V((2.75, -5.35, 5.95))),
                 (2.6, V((1.3, -4.85, 6.4))), (2.85, Ms.translation + V((0, 0, 0.15))), (3.1, Ms.translation)])
    psi = herm(t, [(0.0, -90.0), (2.1, -90.0), (2.45, -45.0), (2.85, 0.0)])
    tronco = herm(t, [(0.0, 0.0), (0.8, 4.0), (1.0, 26.0), (1.7, 30.0), (2.05, 38.0), (2.35, 36.0), (2.6, 22.0), (2.85, 12.0), (3.1, 8.0)])
    cab = herm(t, [(0.0, 0.0), (1.0, -12.0), (2.1, -14.0), (3.0, -5.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    # maos: penduradas -> ombro / flanco -> borda do dorso (empurra) -> topo da sela (a mistura final leva as maos as coxas)
    if t < 0.8: mE = (solto(Mp, "Left"), R)
    elif t < 1.75:
        u = s_((t - 0.8) / 0.2); f_ = mao_no_flanco(Mp, R, "Left"); mE = (solto(Mp, "Left").lerp(f_[0], u) + V((0.7, 0, 0.3)) * 4 * u * (1 - u), R.slerp(f_[1], u))
    elif t < 2.3: mE = trilha(t, [(1.75, mao_no_flanco(Mp, R, "Left")[0]), (1.86, mao_no_flanco(Mp, R, "Left")[0] + V((0.3, 0, 0.6))), (1.97, AP["mao_E2"])], R, MAO)
    else: mE = trilha(t, [(2.3, AP["mao_E2"]), (2.42, meio(AP["mao_E2"], AP["sela_E"], 0.5)), (2.55, AP["sela_E"])], R, MAO)
    if t < 0.85: mD = (solto(Mp, "Right"), R)
    elif t < 1.8:
        u = s_((t - 0.85) / 0.2); f_ = mao_no_flanco(Mp, R, "Right"); mD = (solto(Mp, "Right").lerp(f_[0], u) + V((0.7, 0, 0.3)) * 4 * u * (1 - u), R.slerp(f_[1], u))
    elif t < 2.35: mD = trilha(t, [(1.8, mao_no_flanco(Mp, R, "Right")[0]), (1.91, mao_no_flanco(Mp, R, "Right")[0] + V((0.3, 0, 0.6))), (2.02, AP["mao_D2"])], R, MAO)
    else: mD = trilha(t, [(2.35, AP["mao_D2"]), (2.47, meio(AP["mao_D2"], AP["sela_D"], 0.5)), (2.6, AP["sela_D"])], R, MAO)
    # pes: dois passos -> E no cotovelo (joelho para fora) -> D atras do cotovelo -> D passa pela garupa -> sentado
    gE = V((5.7, -6.7, TORN)); gD = V((5.85, -5.7, TORN))       # pe E longe dos dedos da pata dianteira (x 5,0 em y -7,3)
    pD = (passo(t, 0.05, 0.45, V((7.9, -5.7, TORN)), gD), R); pE = (passo(t, 0.4, 0.8, V((7.9, -6.7, TORN)), gE), R)
    if t >= 1.05: pE = trilha(t, [(1.05, gE), (1.25, V((5.35, -7.0, 1.85))), (1.4, AP["cotovelo"])], R, TORN + 0.22)
    if t >= 2.0:
        u = s_((t - 2.0) / 0.75); fimE = S["alvos"][("IK", "LeftFoot")][0]; c_ = no_osso(AP["cotovelo"], TORN + 0.22)
        p_ = herm(u, [(0.0, c_), (0.4, c_.lerp(fimE, 0.45) + V((0.7, 0, 0.6))), (1.0, fimE)])
        pE = (fora(p_ + V((0.25, 0, 0.15)) * math.sin(math.pi * u)), q_apoio(AP["cotovelo"], R).slerp(S["alvos"][("IK", "LeftFoot")][1], u))
    if t >= 1.55: pD = trilha(t, [(1.55, gD), (1.7, V((5.2, -5.85, 1.6))), (1.85, AP["cot_tras"])], R, TORN + 0.22)
    if t >= 2.05:   # perna D sobe por tras (garupa) no referencial do quadril
        Lc = herm(t, [(2.05, Mp.inverted() @ no_osso(AP["cot_tras"], TORN + 0.22)), (2.25, V((-1.1, 0.9, -0.9))), (2.42, V((-1.5, 1.0, -0.1))),
                      (2.62, V((-1.75, 0.2, -0.45))), (2.9, V((-1.65, -0.75, -0.75)))])
        pD = (Mp @ Lc, q_apoio(AP["cot_tras"], R).slerp(R @ Rx(20), s_((t - 2.05) / 0.3)))
    E = livre(P, psi, tronco, cab, {("IK", "LeftHand"): mE, ("IK", "RightHand"): mD, ("IK", "LeftFoot"): pE, ("IK", "RightFoot"): pD})
    # joelho E para fora/para a cabeca (nao entra no ombro); joelho D para fora/para tras
    E["alvos"][("Polo", "LeftFoot")] = (Mp @ (V((2.5, 1.2, 1.5)) if t > 1.0 else V((0.6, -3.0, 0.8))), R)
    E["alvos"][("Polo", "RightFoot")] = (Mp @ (V((-2.0, -1.0, 2.0)) if t > 2.1 else V((-2.0, -1.5, 0.8)) if t > 1.5 else V((-0.6, -3.0, 0.8))), R)
    return mq.mistura(E, S, s_((t - 2.65) / 0.4))
# ------------------------------------------------------------------ DESMONTAR (3,6 s): perna D volta pela garupa, desce encostado no flanco
def desmontar(t):
    S = mq.estado_sentado(assento()); Ms = S["pelve"]; zs = Ms.translation.z; Y_ = -3.5                  # desce entre as patas (a -4,2 a mao E batia no cotovelo)
    P = herm(t, [(0.45, Ms.translation), (0.8, Ms.translation + V((0.3, 0.1, 0.35))), (1.15, V((1.6, -4.0, zs + 0.25))),
                 (1.45, V((2.6, Y_, 5.3))), (1.8, V((3.4, Y_, 4.3))), (2.1, V((3.85, Y_, 3.2))), (2.35, V((4.2, Y_, 2.3))),
                 (2.5, V((4.45, Y_, 1.92))), (2.75, V((4.55, Y_, 2.0))), (3.3, V((5.6, Y_, 2.0)))])
    psi = herm(t, [(0.45, 0.0), (0.8, -10.0), (1.15, -55.0), (1.45, -90.0)])
    tronco = herm(t, [(0.45, 8.0), (0.8, 22.0), (1.15, 35.0), (1.45, 40.0), (1.8, 32.0), (2.1, 24.0), (2.5, 20.0), (2.75, 8.0), (3.3, 0.0)])
    cab = herm(t, [(0.45, -5.0), (1.2, -10.0), (2.0, -8.0), (3.1, 0.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    sE = S["alvos"][("IK", "LeftHand")]; sD = S["alvos"][("IK", "RightHand")]
    def de_sentado(chaves, s0):      # primeira chave = mao na coxa (estado sentado)
        p, q = trilha(t, chaves, R, MAO); u = s_((t - chaves[0][0]) / (chaves[1][0] - chaves[0][0]))
        return (s0[0].lerp(p, u), s0[1].slerp(q, u)) if t < chaves[1][0] else (p, q)
    if t < 1.2: mE = de_sentado([(0.4, sE[0]), (0.7, AP["sela_E"])], sE)
    else: mE = trilha(t, [(1.2, AP["sela_E"]), (1.32, meio(AP["sela_E"], AP["borda_E"], 0.35)), (1.45, AP["borda_E"])], R, MAO)
    if t < 0.95: mD = de_sentado([(0.45, sD[0]), (0.75, AP["sela_D2"])], sD)
    else: mD = trilha(t, [(0.95, AP["sela_D2"]), (1.15, meio(AP["sela_D2"], AP["borda_D"], 0.5)), (1.4, AP["borda_D"])], R, MAO)
    if t >= 1.55:                      # solta a borda: maos espalmadas no flanco enquanto desce (antebraco nao abraca o dorso)
        u = s_((t - 1.55) / 0.2)
        fE = mao_no_flanco(Mp, R, "Left", 0.9, 1.3); fD = mao_no_flanco(Mp, R, "Right", 0.9, 1.3)
        b_ = V((0.8, 0, 0.3)) * 4 * u * (1 - u)        # arco para fora (nao corta o dorso)
        mE = (mE[0].lerp(fE[0], u) + b_, mE[1].slerp(fE[1], u)); mD = (mD[0].lerp(fD[0], u) + b_, mD[1].slerp(fD[1], u))
    if t >= 2.0:
        u = s_((t - 2.0) / 0.3)          # solta: a mao sai para fora do flanco antes de descer
        def sai(m_, lado):
            a = m_[0]; b = solto(Mp, lado); c = a.lerp(b, 0.5) + V((0.9, 0, 0.3))
            return (herm(u, [(0.0, a), (0.5, c), (1.0, b)]), m_[1].slerp(R, u))
        mE = sai(mE, "Left"); mD = sai(mD, "Right")
    sel = {k: Ms.inverted() @ S["alvos"][("IK", k)][0] for k in ("LeftFoot", "RightFoot")}
    LE = herm(t, [(0.45, sel["LeftFoot"]), (1.0, V((1.4, -0.2, -1.1))), (1.45, V((0.6, 0.6, -1.5))), (2.0, V((0.5, 0.55, -1.55)))])
    LD = herm(t, [(0.6, sel["RightFoot"]), (0.85, V((-1.55, 0.3, -0.35))), (1.1, V((-1.35, 1.2, 0.05))), (1.35, V((-0.6, 1.4, -0.4))), (1.65, V((-0.5, 0.6, -1.5))), (2.0, V((-0.5, 0.55, -1.55)))])
    pE = Mp @ LE; pD = Mp @ LD
    if 0.6 < t < 2.4: pE = fora(pE)
    if 1.3 < t < 2.4: pD = fora(pD)
    chE = V((4.95, Y_ - 0.5, TORN)); chD = V((4.95, Y_ + 0.5, TORN))
    if t >= 2.3:
        u = s_((t - 2.3) / 0.2); pE = pE.lerp(chE, u); pD = pD.lerp(chD, u)
        if t > 2.95: pE = passo(t, 2.95, 3.3, chE, V((6.1, Y_ - 0.5, TORN)), 0.35)
        if t > 2.75: pD = passo(t, 2.75, 3.1, chD, V((6.1, Y_ + 0.5, TORN)), 0.35)
    qs = S["alvos"][("IK", "LeftFoot")][1]; qp = qs.slerp(R @ Rx(20), s_((t - 0.45) / 0.5)).slerp(R, s_((t - 2.1) / 0.25))
    E = livre(P, psi, tronco, cab, {("IK", "LeftHand"): mE, ("IK", "RightHand"): mD, ("IK", "LeftFoot"): (pE, qp), ("IK", "RightFoot"): (pD, qp)})
    E["alvos"][("Polo", "LeftFoot")] = (Mp @ V((1.6, -3.0, 1.2)), R); E["alvos"][("Polo", "RightFoot")] = (Mp @ V((-1.6, -3.0, 1.2)), R)
    if t < 0.45: return S
    return mq.mistura(S, E, s_((t - 0.45) / 0.35))
# ------------------------------------------------------------------ assar em FK + medicoes
amo = mq.amostras_partes(0.2)
def assar(nome_acao, clipe, fn, dur):
    nq = int(round(dur * FPS)) + 1; poses = []; med = []; prev = None
    for qi in range(nq):
        t = qi / FPS
        if clipe: croc_quadro(clipe, t)
        else:
            croc.animation_data.action = None
            for pb in croc.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
            bpy.context.view_layer.update()
        for pb in ra.pose.bones:
            for c in pb.constraints: c.mute = False
        mq.aplicar(ra, alvos, fn(t)); bpy.context.view_layer.update()
        poses.append({pb.name: ra.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in ra.pose.bones})
        bvh = mq.bvh_croc(lo); fo = mq.folgas(ra, amo, bvh)
        bs = BVHTree.FromObject(sela, bpy.context.evaluated_depsgraph_get())
        fs = mq.folgas(ra, amo, bs, Minv=sela.matrix_world.inverted(), raio=3.0, passo=2)
        cab_z = (ra.matrix_world @ ra.pose.bones["Head"].tail).z
        pel = (ra.matrix_world @ ra.pose.bones["LowerTorso"].head)
        # solas no chao: menor z das caixas dos pes
        sola = min((ra.matrix_world @ ra.pose.bones[f].matrix @ ra.data.bones[f].matrix_local.inverted() @ V(p)).z for f in ("LeftFoot", "RightFoot") for p in amo[f])
        vel = (pel - prev).length * FPS if prev is not None else 0.0; prev = pel.copy()
        med.append({"q": qi, "t": round(t, 3), "folga_croc": fo, "folga_sela": fs, "quadril": [round(c, 3) for c in pel], "vel_quadril": round(vel, 2), "sola_min_z": round(sola, 3)})
    for pb in ra.pose.bones:
        for c in pb.constraints: c.mute = True
    if not ra.animation_data: ra.animation_data_create()
    act = bpy.data.actions.get(nome_acao) or bpy.data.actions.new(nome_acao); ra.animation_data.action = act
    for qi, pose in enumerate(poses):
        for pb in ra.pose.bones:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    act.use_fake_user = True; act["demonstracao"] = "manequim R15 aproximado, nao publicado"; act["clipe_crocodilo"] = clipe or "(descanso)"
    ra.animation_data.action = None
    return med
QA = {}
QA["Sentado"] = assar("DEMO_Cav_Sentado", None, lambda t: mq.estado_sentado(assento()), 0.0)
QA["Montar"] = assar("DEMO_Cav_Montar", "Montar", montar, 4.0)
QA["Desmontar"] = assar("DEMO_Cav_Desmontar", "Desmontar", desmontar, 3.6)
resumo = {}
for k, med in QA.items():
    r = {"folga_croc_min": {}, "folga_sela_min": {}}
    for m in med:
        for nm, v in m["folga_croc"].items():
            if nm not in r["folga_croc_min"] or v < r["folga_croc_min"][nm][0]: r["folga_croc_min"][nm] = (v, m["q"])
        for nm, v in m["folga_sela"].items():
            if nm not in r["folga_sela_min"] or v < r["folga_sela_min"][nm][0]: r["folga_sela_min"][nm] = (v, m["q"])
    r["vel_quadril_max"] = max(m["vel_quadril"] for m in med); r["sola_min_z"] = min(m["sola_min_z"] for m in med)
    resumo[k] = r; print("QA_DEMO", k, json.dumps(r))
for pb in croc.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
croc.animation_data.action = None; ra.animation_data.action = bpy.data.actions["DEMO_Cav_Sentado"]
sc["lote4"] = "cena de TESTE: sela PROPOSTA + manequim R15 aproximado; acoes DEMO_Cav_* = demonstracao"
if A: json.dump({"resumo": resumo, "quadros": QA}, open(A[0], "w"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "CR_Crocodilo_Montaria_Teste.blend"))
print("DEMO_OK")
