"""S2: DEMONSTRACAO da subida na sela do Leao Solar pelos dois lados, com o manequim de TESTE (proporcoes aproximadas do R15;
modulo manequim_r15.py do Crocodilo, so importado; nao e rig R15 validado nem animacao publicada). Metodo do Lote 4/5 do
Crocodilo (aprovado): o leao toca Leao_Montar_E / Leao_Montar_D; o manequim e animado por alvos (quadril, maos, pes) com IK e
assado em FK nas acoes DEMO_Cav_Montar_E / DEMO_Cav_Montar_D / DEMO_Cav_Sentado. Apoios (cotovelo, ombro, aba, alca) sao
pontos medidos na pele/sela do leao agachado e acompanham o osso.
Lado E = x- do leao (patas DE), lado D = x+; caminhos livres definidos no referencial do lado (X para fora, a partir de XC).
Subida em salto apoiado atras da juba: pe da frente empurra no flanco, maos na aba e na alca, a perna de tras passa pela garupa.
Uso: blender -b <S1 com sela.blend> -P s2_02_demo_montaria.py -- <clipes_montar.blend> <saida.blend> <saida_qa.json>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix as M, Quaternion as Q
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(RAIZ, "..", "s1"))
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import s1_01_sela_leao as sl
DZ_EXTRA = 0.10                                         # quadril 0,1 mais alto que o projeto da sela (coxas do R15 nao entram na aba)
mq.SENTADO = dict(sl.SENTADO_LEAO)
for lado_, sx in (("LeftFoot", 1), ("RightFoot", -1)):  # pes no mesmo lugar absoluto dos apoios (quadril 0,1 mais alto)
    x_, y_, z_ = sl.SENTADO_LEAO[("IK", lado_)]; mq.SENTADO[("IK", lado_)] = (x_, y_, z_ - DZ_EXTRA)
A = sys.argv[sys.argv.index("--") + 1:]
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["Leao_Solar_Rig"]; lo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; sela = bpy.data.objects[sl.NOME]
with bpy.data.libraries.load(os.path.abspath(A[0])) as (src, dst): dst.actions = [n for n in src.actions if n in ("Leao_Montar_E", "Leao_Montar_D", "Leao_Desmontar_E", "Leao_Desmontar_D")]
for a_ in dst.actions: a_.use_fake_user = True
XC = sl.XC
def leao_quadro(nome, t):
    arm.animation_data.action = bpy.data.actions["Leao_" + nome]; sc.frame_set(1 + int(round(t * FPS))); bpy.context.view_layer.update()
def zerar_leao():
    arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
# ------------------------------------------------------------------ assento: topo da sela no repouso (depois da folga) + 0,55
zerar_leao()
def bvh_obj(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh(); W = o.matrix_world
    vs = [W @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]; ev.to_mesh_clear(); return BVHTree.FromPolygons(vs, fs)
hit = bvh_obj(sela).ray_cast(V((XC, sl.ASSENTO_Y, 20)), V((0, 0, -1))); Z_Q = hit[0].z + sl.DZ_QUADRIL + DZ_EXTRA
OSSO = "Coluna1"; BL = arm.data.bones[OSSO].matrix_local; Q_REP = V((XC, sl.ASSENTO_Y, Z_Q))
def assento():
    return arm.matrix_world @ arm.pose.bones[OSSO].matrix @ BL.inverted() @ M.Translation(Q_REP)
print("ASSENTO quadril", [round(c, 3) for c in Q_REP])
# ------------------------------------------------------------------ curvas e utilitarios (como no demo do Crocodilo)
def herm(t, pts):
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
    u = s_((t - t0) / (t1 - t0)); p = a.lerp(b, u); p.z += alt * math.sin(math.pi * u); return p
def apoio(o_alvo, p_mundo, osso):
    """ponto e normal da superficie (pele ou sela) mais proximos de p_mundo na pose atual, guardados no espaco do osso"""
    bvh = bvh_obj(o_alvo); loc, nor, _, _ = bvh.find_nearest(p_mundo)
    pb = arm.pose.bones[osso]; Mb = arm.matrix_world @ pb.matrix
    return (osso, Mb.inverted() @ loc, (Mb.inverted().to_3x3() @ nor).normalized())
def no_osso(ap, d=0.0):
    osso, p, n = ap; Mb = arm.matrix_world @ arm.pose.bones[osso].matrix
    return Mb @ p + (Mb.to_3x3() @ n).normalized() * d
def q_apoio(ap, R):
    osso, p, n = ap; Mb = arm.matrix_world @ arm.pose.bones[osso].matrix
    return V((0, 0, 1)).rotation_difference((Mb.to_3x3() @ n).normalized()) @ R
def trilha(t, chaves, R, d):
    ps = [(tk, (no_osso(v, d) if isinstance(v, tuple) else v)) for tk, v in chaves]
    qs = [(q_apoio(v, R) if isinstance(v, tuple) else R) for _, v in chaves]
    p = herm(t, ps)
    if t <= chaves[0][0]: return p, qs[0]
    for i in range(len(chaves) - 1):
        if t <= chaves[i + 1][0]: return p, qs[i].slerp(qs[i + 1], s_((t - chaves[i][0]) / (chaves[i + 1][0] - chaves[i][0])))
    return p, qs[-1]
MAO = 0.33; TORN = 0.33
BV = {"q": None, "bvh": None}
def flanco(s, y, z):
    """x da pele do lado s (+1 = x+, -1 = x-) na altura z (raio de fora para dentro)"""
    q = (sc.frame_current, arm.animation_data.action.name if arm.animation_data.action else "")
    if BV["q"] != q: BV["bvh"] = bvh_obj(lo); BV["q"] = q
    hit = BV["bvh"].ray_cast(V((XC + s * 9.0, y, z)), V((-s, 0, 0))); return hit[0].x if hit[0] else XC
def fora(p, s, folga=0.62):
    """empurra o tornozelo/mao para fora do flanco do lado s (desliza encostado, nao atravessa)"""
    fx = [flanco(s, p.y + d, p.z + dz) for d in (-0.45, 0.0, 0.45) for dz in (-0.25, 0.1)]
    f_ = max(fx) if s > 0 else min(fx)
    return V((max(p.x, f_ + folga), p.y, p.z)) if s > 0 else V((min(p.x, f_ - folga), p.y, p.z))
def livre(P, psi, tronco, cabeca, alvos_):
    R = Rz(psi); Mp = M.Translation(P) @ R.to_matrix().to_4x4()
    est = {"pelve": Mp, "tronco": tronco, "cabeca": cabeca, "alvos": {}}
    for lado, s in (("Left", 1), ("Right", -1)):
        est["alvos"][("Polo", lado + "Foot")] = (Mp @ V((0.6 * s, -3.0, 0.8)), R)
        est["alvos"][("Polo", lado + "Hand")] = (Mp @ V((2.2 * s, 2.0, 1.5)), R)
    for k, v in alvos_.items(): est["alvos"][k] = v
    return est
def solto(Mp, lado): s = 1 if lado == "Left" else -1; return Mp @ V((1.55 * s, 0.05, 0.1))
# ------------------------------------------------------------------ apoios medidos no leao agachado (t = 1,5 s), por lado
# subida em salto apoiado ATRAS DA JUBA (a juba cobre os lados ate y -3 e e larga): pe no flanco, maos na aba e na alca
T_BAIXO = 1.5
AP = {}
for lado_l, s in (("E", -1), ("D", 1)):
    leao_quadro("Montar_" + lado_l, T_BAIXO); q_ = assento().translation                   # quadril sentado na pose baixa
    AP[lado_l] = {
        "flanco": apoio(lo, V((XC + s * 5.0, 0.15, 6.3)), "Coluna1"),                      # parte mais larga do flanco (pe empurra; mais baixo a canela batia na barriga do flanco)
        "aba": apoio(sela, q_ + V((s * 1.2, 0.65, -0.4)), "Coluna1"),                      # borda da aba do lado da subida (mao de tras)
        "aba_f": apoio(sela, q_ + V((s * 1.2, -0.35, -0.4)), "Coluna1"),                   # borda da aba, frente (1o agarre da mao da frente)
        "alca": apoio(sela, q_ + V((s * 0.18, -1.15, 0.25)), "Coluna1"),                   # alca de couro (mao da frente)
    }
    print("APOIOS", lado_l, {k: [round(c, 2) for c in no_osso(v)] for k, v in AP[lado_l].items()})
# ------------------------------------------------------------------ MONTAR (4,6 s)
def montar(t, lado_l):
    s = -1 if lado_l == "E" else 1; ap = AP[lado_l]
    psi0 = 90.0 if s < 0 else -90.0                                          # de frente para o leao
    frente, tras = ("Right", "Left") if s < 0 else ("Left", "Right")         # lado do cavaleiro voltado para a cabeca / a garupa do leao
    def L(x, y, z): return V((XC + s * x, y, z))                             # ponto no referencial do lado (x para fora)
    S = mq.estado_sentado(assento()); Ms = S["pelve"]
    P = herm(t, [(0.0, L(7.4, 0.6, 2.0)), (0.9, L(4.3, 0.5, 2.0)), (1.2, L(4.25, 0.5, 1.9)), (1.42, L(4.2, 0.5, 1.72)),
                 (1.62, L(3.95, 0.45, 4.4)), (1.86, L(3.35, 0.35, 7.4)), (2.08, L(2.45, 0.3, 9.5)), (2.32, Ms.translation + V((s * 0.8, 0.15, 0.6))),
                 (2.56, Ms.translation + V((0, 0, 0.12))), (2.75, Ms.translation)])
    psi = herm(t, [(0.0, psi0), (1.95, psi0), (2.3, psi0 * 0.4), (2.58, 0.0)])
    tronco = herm(t, [(0.0, 0.0), (0.9, 4.0), (1.42, 16.0), (1.62, 12.0), (1.86, 24.0), (2.08, 40.0), (2.32, 26.0), (2.56, 12.0), (2.75, 8.0)])
    cab = herm(t, [(0.0, 0.0), (1.1, -16.0), (2.1, -10.0), (2.75, -5.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    # maos: penduradas -> sobem (antecipacao) -> mao da frente na alca, mao de tras na aba -> mistura final (alca)
    def mao(lado_m, agarre, alvo_, atraso):
        """salto e agarre: penduradas -> sobem por FORA junto com o corpo (sem segurar nada baixo) -> agarram a borda da aba
        quando o corpo ja esta alto -> a mao da frente passa para a alca (a de tras fica na aba)"""
        sl_ = 1 if lado_m == "Left" else -1; cima = Mp @ V((1.05 * sl_, -0.35, 2.3)); alto = Mp @ V((0.95 * sl_, -0.6, 2.65))   # mao sobe rente ao corpo, longe do flanco
        if t < 1.1 + atraso: return (solto(Mp, lado_m), R)
        if t < 1.45 + atraso:
            u = s_((t - 1.1 - atraso) / 0.35); return (solto(Mp, lado_m).lerp(cima, u), R)
        if t < 1.74 + atraso:
            u = s_((t - 1.45 - atraso) / 0.29); return (cima.lerp(alto, u), R)
        g_ = no_osso(agarre, MAO)
        if t < 2.0 + atraso: return trilha(t, [(1.74 + atraso, alto), (1.84 + atraso, g_ + V((s * 0.45, 0, 0.55))), (1.92 + atraso, agarre), (2.0 + atraso, agarre)], R, MAO)
        if alvo_ is agarre: return trilha(t, [(2.0 + atraso, agarre), (2.1 + atraso, agarre)], R, MAO)
        a_ = no_osso(alvo_, MAO)
        return trilha(t, [(2.0 + atraso, agarre), (2.08 + atraso, g_.lerp(a_, 0.5) + V((0, 0, 0.45))), (2.16 + atraso, alvo_)], R, MAO)
    mF, mT = mao(frente, ap["aba_f"], ap["alca"], 0.0), mao(tras, ap["aba"], ap["aba"], 0.04)
    # pes: dois passos -> agacha -> salta (pe da frente empurra no flanco) -> perna de tras passa pela garupa -> sentado
    gF = L(4.35, -0.15, TORN); gT = L(4.45, 1.15, TORN)
    pF = (passo(t, 0.4, 0.8, L(7.4, 0.0, TORN), gF), R); pT = (passo(t, 0.05, 0.45, L(7.4, 1.2, TORN), gT), R)
    if t >= 1.45:     # pe da frente: sai do chao e apoia no flanco (empurra), depois sobe para o apoio de pe
        if t < 1.85: pF = trilha(t, [(1.45, gF), (1.6, L(4.0, 0.0, 3.6)), (1.72, ap["flanco"]), (1.85, ap["flanco"])], R, TORN + 0.4)
        else:
            u = s_((t - 1.85) / 0.7); a_ = no_osso(ap["flanco"], TORN + 0.4); fim = S["alvos"][("IK", frente + "Foot")][0]
            pF = (fora(herm(u, [(0.0, a_), (0.4, a_.lerp(fim, 0.4) + V((s * 1.3, 0, 0.6))), (1.0, fim)]), s, 0.85) if u < 0.9 else fim,
                  q_apoio(ap["flanco"], R).slerp(S["alvos"][("IK", frente + "Foot")][1], u))
    if t >= 1.5:      # perna de tras: sobe dobrada por tras, passa pela garupa no referencial do quadril e desce do outro lado
        so_ = 1 if tras == "Left" else -1
        Lc = herm(t, [(1.5, Mp.inverted() @ gT), (1.75, V((0.7 * so_, 0.5, -1.2))), (2.05, V((0.9 * so_, 1.3, -0.5))),
                      (2.3, V((1.6 * so_, 1.2, 0.2))), (2.52, V((1.9 * so_, 0.3, -0.4))), (2.75, V((1.9 * so_, -0.55, -0.85)))])
        pT = (Mp @ Lc, R.slerp(R @ Rx(20), s_((t - 1.5) / 0.4)))
    E = livre(P, psi, tronco, cab, {("IK", frente + "Hand"): mF, ("IK", tras + "Hand"): mT, ("IK", frente + "Foot"): pF, ("IK", tras + "Foot"): pT})
    sf = 1 if frente == "Left" else -1; st = -sf
    E["alvos"][("Polo", frente + "Foot")] = (Mp @ (V((1.4 * sf, 2.5, 1.2)) if 1.4 < t < 2.4 else V((0.6 * sf, -3.0, 0.8))), R)   # pe no flanco: joelho dobra para FORA do leao
    E["alvos"][("Polo", tras + "Foot")] = (Mp @ (V((2.0 * st, -1.0, 2.0)) if t > 2.0 else V((0.6 * st, -3.0, 0.8))), R)
    return mq.mistura(E, S, s_((t - 2.5) / 0.35))
# ------------------------------------------------------------------ DESMONTAR (3,8 s): o leao agacha com o cavaleiro sentado; a perna de fora
# passa pela garupa, o corpo vira para o leao e desliza pelo flanco segurando a aba; pousa amortecendo e se afasta dois passos
def desmontar(t, lado_l):
    s = -1 if lado_l == "E" else 1; ap = AP[lado_l]
    psi0 = 90.0 if s < 0 else -90.0                                          # no fim de frente para o leao
    perto, longe = ("Right", "Left") if s < 0 else ("Left", "Right")        # perna do lado da descida / perna que passa pela garupa
    def L(x, y, z): return V((XC + s * x, y, z))
    S = mq.estado_sentado(assento()); Ms = S["pelve"]
    if t < 1.15: return S
    P = herm(t, [(1.15, Ms.translation), (1.45, Ms.translation + V((0, 0.1, 0.45))), (1.75, Ms.translation + V((s * 0.8, 0.2, 0.4))),
                 (1.92, L(2.55, 0.35, 8.6)), (2.06, L(3.4, 0.4, 6.7)), (2.19, L(4.05, 0.45, 4.4)), (2.3, L(4.35, 0.5, 2.3)), (2.42, L(4.45, 0.5, 1.75)),
                 (2.62, L(4.5, 0.5, 2.0)), (3.0, L(5.4, 0.5, 2.0)), (3.4, L(6.5, 0.5, 2.0))])
    psi = herm(t, [(1.15, 0.0), (1.4, 0.0), (1.75, psi0 * 0.85), (1.95, psi0)])
    tronco = herm(t, [(1.15, 8.0), (1.45, 24.0), (1.75, 24.0), (2.06, 14.0), (2.3, 10.0), (2.42, 16.0), (2.7, 6.0), (3.4, 2.0)])
    cab = herm(t, [(1.15, -5.0), (1.6, -12.0), (2.4, -14.0), (3.2, 0.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    sH = {k: S["alvos"][("IK", k + "Hand")] for k in ("Left", "Right")}
    # maos: alca/coxas -> mao do lado da descida na borda da aba (frente), a outra na aba (tras) -> soltam por fora e descem
    def mao(lado_m, apoio_, t_ag):
        if t < t_ag: return sH[lado_m]
        if t < 2.02:
            p_, q_ = trilha(t, [(t_ag, sH[lado_m][0]), (t_ag + 0.12, no_osso(apoio_, MAO) + V((0, 0, 0.5))), (t_ag + 0.24, apoio_), (2.02, apoio_)], R, MAO)
            return (p_, q_)
        a_ = no_osso(apoio_, MAO); sl_ = 1 if lado_m == "Left" else -1
        return trilha(t, [(2.02, a_), (2.12, a_ + V((s * 0.9, 0, 0.4))), (2.3, Mp @ V((1.3 * sl_, 0.45, 1.1))), (2.6, solto(Mp, lado_m))], R, MAO)   # solta para longe do leao
    mP, mL = mao(perto, ap["aba_f"], 1.25), mao(longe, ap["aba"], 1.45)
    # pes: perna de fora passa por tras (garupa) no referencial do quadril; as duas pendem do lado da descida, fora do flanco;
    # pousam no chao (2,3) e dao dois passos para tras
    sP = 1 if perto == "Left" else -1; sL = -sP
    pS = {k: S["alvos"][("IK", k + "Foot")] for k in ("Left", "Right")}
    gP = L(4.35, -0.15, TORN); gL = L(4.45, 1.15, TORN)
    def pendurado(lado_m):
        sl_ = 1 if lado_m == "Left" else -1; return fora(Mp @ V((0.55 * sl_, 0.9, -1.5)), s, 0.9)
    if t < 1.3: pL = pS[longe]
    elif t < 1.85:
        Lc = herm(t, [(1.3, Ms.inverted() @ pS[longe][0]), (1.48, V((1.6 * sL, 1.3, 0.45))), (1.66, V((0.4 * sL, 1.75, 0.5))), (1.85, Mp.inverted() @ pendurado(longe))])
        pL = (Mp @ Lc if t >= 1.66 else Ms @ Lc, R.slerp(R @ Rx(20), s_((t - 1.3) / 0.3)))
    elif t < 2.3: pL = (pendurado(longe), R @ Rx(20))
    else: pL = (passo(t, 2.85, 3.25, gL, L(6.65, 1.15, TORN), 0.4) if t > 2.85 else gL.lerp(gL, 1.0), R)
    if t < 1.75: pP = pS[perto]
    elif t < 2.3:
        u = s_((t - 1.75) / 0.2); a_, b_ = pS[perto][0], pendurado(perto)          # sai do apoio de pe por FORA e por cima (passava no bloco)
        pP = (herm(u, [(0.0, a_), (0.5, a_.lerp(b_, 0.5) + V((s * 0.7, 0, 0.45))), (1.0, b_)]), pS[perto][1].slerp(R @ Rx(20), u))
    else: pP = (passo(t, 2.65, 3.05, gP, L(6.55, -0.15, TORN), 0.4) if t > 2.65 else gP, R)
    if 2.18 <= t < 2.3:      # chega ao chao: os pes descem do pendurado para o ponto de pouso
        u = s_((t - 2.18) / 0.12); pL = (pendurado(longe).lerp(gL, u), R); pP = (pendurado(perto).lerp(gP, u), R)
    E = livre(P, psi, tronco, cab, {("IK", perto + "Hand"): mP, ("IK", longe + "Hand"): mL, ("IK", perto + "Foot"): pP, ("IK", longe + "Foot"): pL})
    E["alvos"][("Polo", perto + "Foot")] = (Mp @ V((1.4 * sP, 2.5, 1.2)) if t < 2.3 else Mp @ V((0.6 * sP, -3.0, 0.8)), R)
    E["alvos"][("Polo", longe + "Foot")] = (Mp @ V((2.0 * sL, -1.0, 2.0)) if t < 1.8 else Mp @ V((1.4 * sL, 2.5, 1.2)) if t < 2.3 else Mp @ V((0.6 * sL, -3.0, 0.8)), R)
    return mq.mistura(S, E, s_((t - 1.15) / 0.3))
# ------------------------------------------------------------------ assar em FK + medicoes
amo = mq.amostras_partes(0.2)
DOBRA_JOELHO = float(os.environ.get("S2_DOBRA", "15"))
col = bpy.data.collections.new("TESTE_Montaria_S2"); sc.collection.children.link(col)
ra, ob, alvos = mq.criar(col)
def assar(nome_acao, clipe, fn, dur):
    nq = int(round(dur * FPS)) + 1; poses = []; med = []; prev = None
    for qi in range(nq):
        t = qi / FPS
        if clipe: leao_quadro(clipe, t)
        else: zerar_leao()
        for pb in ra.pose.bones:
            for c in pb.constraints: c.mute = False
        mq.aplicar(ra, alvos, fn(t))
        for lado_ in ("Left", "Right"):   # dobra inicial dos joelhos: com a perna reta o IK nao sabe para onde dobrar (agachar afundava o pe)
            ra.pose.bones[lado_ + "LowerLeg"].rotation_quaternion = Q(V((1, 0, 0)), math.radians(DOBRA_JOELHO))
        bpy.context.view_layer.update()
        poses.append({pb.name: ra.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in ra.pose.bones})
        bvh = bvh_obj(lo); fo = mq.folgas(ra, amo, bvh)
        bs = BVHTree.FromObject(sela, bpy.context.evaluated_depsgraph_get()); fs = mq.folgas(ra, amo, bs, Minv=sela.matrix_world.inverted(), raio=3.0, passo=2)
        pel = ra.matrix_world @ ra.pose.bones["LowerTorso"].head
        sola = min((ra.matrix_world @ ra.pose.bones[f].matrix @ ra.data.bones[f].matrix_local.inverted() @ V(p)).z for f in ("LeftFoot", "RightFoot") for p in amo[f])
        vel = (pel - prev).length * FPS if prev is not None else 0.0; prev = pel.copy()
        med.append({"q": qi + 1, "t": round(t, 3), "folga_leao": fo, "folga_sela": fs, "quadril": [round(c, 3) for c in pel], "vel_quadril": round(vel, 2), "sola_min_z": round(sola, 3)})
    for pb in ra.pose.bones:
        for c in pb.constraints: c.mute = True
    if not ra.animation_data: ra.animation_data_create()
    act = bpy.data.actions.get(nome_acao) or bpy.data.actions.new(nome_acao); ra.animation_data.action = act
    for qi, pose in enumerate(poses):
        for pb in ra.pose.bones:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    act.use_fake_user = True; act["demonstracao"] = "manequim R15 aproximado, nao publicado"; act["clipe_leao"] = clipe or "(repouso)"
    ra.animation_data.action = None
    return med
QA = {}
QA["Sentado"] = assar("DEMO_Cav_Sentado", None, lambda t: mq.estado_sentado(assento()), 0.0)
for lado_l in ("E", "D"):
    QA["Montar_" + lado_l] = assar("DEMO_Cav_Montar_" + lado_l, "Montar_" + lado_l, lambda t, l=lado_l: montar(t, l), 4.6)
    QA["Desmontar_" + lado_l] = assar("DEMO_Cav_Desmontar_" + lado_l, "Desmontar_" + lado_l, lambda t, l=lado_l: desmontar(t, l), 3.8)
resumo = {}
for k, med in QA.items():
    r = {"folga_leao_min": {}, "folga_sela_min": {}}
    for m in med:
        for nm, v in m["folga_leao"].items():
            if nm not in r["folga_leao_min"] or v < r["folga_leao_min"][nm][0]: r["folga_leao_min"][nm] = (v, m["q"])
        for nm, v in m["folga_sela"].items():
            if nm not in r["folga_sela_min"] or v < r["folga_sela_min"][nm][0]: r["folga_sela_min"][nm] = (v, m["q"])
    r["vel_quadril_max"] = max(m["vel_quadril"] for m in med); r["sola_min_z"] = min(m["sola_min_z"] for m in med)
    resumo[k] = r; print("QA_DEMO", k, json.dumps(r), flush=True)
zerar_leao(); ra.animation_data.action = bpy.data.actions["DEMO_Cav_Sentado"]
sc["s2"] = "cena de TESTE: leao + sela S1 + manequim R15 aproximado; acoes DEMO_Cav_* = demonstracao"
json.dump({"resumo": resumo, "quadros": QA, "assento_quadril": list(Q_REP)}, open(A[2], "w"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[1])); print("DEMO_OK")
