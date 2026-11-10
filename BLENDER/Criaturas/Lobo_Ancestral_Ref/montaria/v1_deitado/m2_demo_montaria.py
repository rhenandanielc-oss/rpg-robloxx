"""Montaria M2 (10/11/2026): DEMONSTRACAO da subida e da descida da sela leve do Lobo Ancestral pelos dois lados, com o
manequim de TESTE (proporcoes aproximadas do R15; modulo manequim_r15.py do Crocodilo, so importado; nao e rig R15 validado
nem animacao publicada). Adaptado do m2_demo_montaria.py do Urso Silvestre (aprovado 09/11). O lobo toca Lobo_Montar_E/D e
Lobo_Desmontar_E/D (montaria/clipes_montaria.py: ele DEITA); o manequim e animado por alvos (quadril, maos, pes) com IK e
assado em FK. Apoios (pegada, aba) sao pontos medidos na sela do lobo deitado e acompanham o osso; os estribos sao os alvos
dos pes sentados.
Lado E = x+ do lobo, lado D = x-.
Subida: dois passos ate o lado; o lobo deita (dorso baixo); maos na pegada e na aba; o pe da frente entra no ESTRIBO, o
corpo sobe sobre ele, a perna de tras passa pela garupa e cai no outro estribo; senta; o lobo levanta com ele.
Descida: o lobo deita; a perna de fora passa pela garupa, o corpo vira para o lobo e desce pelo flanco segurando a aba;
pousa e se afasta dois passos.
Uso: blender -b montaria/LA_M1_sela.blend -P montaria/m2_demo_montaria.py -- <Anim_Montaria.blend> <saida.blend> <saida_qa.json>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix as M, Quaternion as Q
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import m1_sela_lobo as sl
DZ_EXTRA = 0.05
A = sys.argv[sys.argv.index("--") + 1:]
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; sela = bpy.data.objects[sl.NOME]
CORPO = [bpy.data.objects["Lobo_Ancestral_LOW"]]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
SENT = {tuple(k.split("|")): tuple(v) for k, v in json.loads(sela["sentado"]).items()}
mq.SENTADO = dict(SENT)
for lado_ in ("LeftFoot", "RightFoot"):
    x_, y_, z_ = SENT[("IK", lado_)]; mq.SENTADO[("IK", lado_)] = (x_, y_, z_ - DZ_EXTRA)
NOMES = ("Lobo_Montar_E", "Lobo_Montar_D", "Lobo_Desmontar_E", "Lobo_Desmontar_D")
for n_ in NOMES:
    if n_ in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[n_])
with bpy.data.libraries.load(os.path.abspath(A[0])) as (src, dst): dst.actions = [n for n in src.actions if n in NOMES]
for a_ in dst.actions: a_.use_fake_user = True
XC = sl.XC
def leao_quadro(nome, t):
    arm.animation_data.action = bpy.data.actions["Lobo_" + nome]
    try: arm.animation_data.action_slot = arm.animation_data.action.slots[0]
    except Exception: pass
    sc.frame_set(1 + int(round(t * FPS))); bpy.context.view_layer.update()
def zerar_leao():
    arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
zerar_leao()
def bvh_obj(o):
    dg = bpy.context.evaluated_depsgraph_get(); vs, fs = [], []
    for o_ in (o if isinstance(o, (list, tuple)) else [o]):
        ev = o_.evaluated_get(dg); m = ev.to_mesh(); W = o_.matrix_world; k = len(vs)
        vs += [W @ v.co for v in m.vertices]; fs += [tuple(i + k for i in p.vertices) for p in m.polygons]; ev.to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs)
lo = CORPO
hit = bvh_obj(sela).ray_cast(V((XC, sl.ASSENTO_Y, 20)), V((0, 0, -1))); Z_Q = hit[0].z + sl.DZ_QUADRIL + DZ_EXTRA
OSSO = "Coluna2"; BL = arm.data.bones[OSSO].matrix_local; Q_REP = V((XC, sl.ASSENTO_Y, Z_Q))
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
# ------------------------------------------------------------------ apoios medidos no lobo DEITADO (t = 3,0 s), por lado
T_BAIXO = 3.0
AP = {}; XS = {}
for lado_l, s in (("E", 1), ("D", -1)):
    leao_quadro("Montar_" + lado_l, T_BAIXO); q_ = assento().translation
    fl = [flanco(s, y, z) for y in np.linspace(-2.0, 1.0, 7) for z in np.linspace(0.4, 2.6, 6)]
    XS[lado_l] = (max(fl) if s > 0 else -min(fl)) + 1.05                    # quadril do cavaleiro em pe: fora do flanco
    AP[lado_l] = {
        "pegada": apoio(sela, q_ + V((s * 0.16, -1.05, 0.0)), OSSO),
        "aba": apoio(sela, q_ + V((s * 0.85, 0.45, -0.45)), OSSO),
        "aba_f": apoio(sela, q_ + V((s * 0.85, -0.35, -0.45)), OSSO),
    }
    print("APOIOS", lado_l, "quadril", [round(c, 2) for c in q_], "XS %.2f" % XS[lado_l], {k: [round(c, 2) for c in no_osso(v)] for k, v in AP[lado_l].items()})
def estribo(S, lado):
    return S["alvos"][("IK", lado + "Foot")]
# ------------------------------------------------------------------ MONTAR (6,2 s; o lobo esta deitado de 2,2 a 4,1)
def montar(t, lado_l):
    s = 1 if lado_l == "E" else -1; ap = AP[lado_l]; Xs = XS[lado_l]
    psi0 = -90.0 * s
    frente, tras = ("Left", "Right") if s > 0 else ("Right", "Left")
    def L(x, y, z): return V((XC + s * x, y, z))
    S = mq.estado_sentado(assento()); Ms = S["pelve"]; Pq = Ms.translation
    eF = estribo(S, frente)
    P = herm(t, [(0.0, L(Xs + 3.2, 0.3, 2.0)), (1.5, L(Xs, 0.0, 2.0)), (2.3, L(Xs, 0.0, 2.0)), (2.5, L(Xs + 0.05, -0.05, 1.85)),
                 (2.8, L(Xs - 0.15, -0.05, 2.15)), (3.05, Pq + V((s * 1.05, 0.05, 0.75))), (3.3, Pq + V((s * 0.55, 0.1, 0.6))),
                 (3.55, Pq + V((0, 0, 0.12))), (3.75, Pq)])
    psi = herm(t, [(0.0, psi0), (2.95, psi0), (3.3, psi0 * 0.45), (3.6, 0.0)])
    tronco = herm(t, [(0.0, 0.0), (1.5, 4.0), (2.5, 14.0), (2.8, 22.0), (3.05, 30.0), (3.3, 22.0), (3.55, 12.0), (3.75, 8.0)])
    cab = herm(t, [(0.0, 0.0), (2.0, -14.0), (3.1, -10.0), (3.75, -5.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    def mao(lado_m, agarre, atraso):
        sl_ = 1 if lado_m == "Left" else -1; cima = Mp @ V((0.9 * sl_, -0.6, 1.9))
        if t < 2.15 + atraso: return (solto(Mp, lado_m), R)
        if t < 2.4 + atraso:
            u = s_((t - 2.15 - atraso) / 0.25); return (solto(Mp, lado_m).lerp(cima, u), R)
        g_ = no_osso(agarre, MAO)
        return trilha(t, [(2.4 + atraso, cima), (2.5 + atraso, g_ + V((s * 0.35, 0, 0.35))), (2.58 + atraso, agarre), (3.6, agarre)], R, MAO)
    mF, mT = mao(frente, ap["pegada"], 0.0), mao(tras, ap["aba"], 0.05)
    gF = L(Xs, -0.6, TORN); gT = L(Xs + 0.05, 0.6, TORN)
    pF = (passo(t, 0.75, 1.35, L(Xs + 3.2, -0.3, TORN), gF), R); pT = (passo(t, 0.1, 0.7, L(Xs + 3.2, 0.9, TORN), gT), R)
    if t >= 2.45:      # pe da frente: entra no ESTRIBO (vindo por fora) e fica nele; o corpo sobe sobre ele
        u = s_((t - 2.45) / 0.3)
        pF = (herm(u, [(0.0, gF), (0.5, gF.lerp(eF[0], 0.5) + V((s * 0.55, 0, 0.35))), (1.0, eF[0])]), R.slerp(eF[1], u))
    if t >= 2.85:      # perna de tras: sai do chao, sobe dobrada, passa pela garupa e cai no outro estribo
        so_ = 1 if tras == "Left" else -1
        Lc = herm(t, [(2.85, Mp.inverted() @ gT), (3.02, V((0.5 * so_, 0.5, -1.2))), (3.2, V((0.9 * so_, 1.2, -0.45))),
                      (3.38, V((1.5 * so_, 1.15, 0.15))), (3.55, V((1.7 * so_, 0.3, -0.45)))])
        if t < 3.55: pT = (Mp @ Lc, R.slerp(R @ Rx(20), s_((t - 2.85) / 0.4)))
        else:
            eT = estribo(S, tras); u = s_((t - 3.55) / 0.25); pT = ((Mp @ Lc).lerp(eT[0], u), (R @ Rx(20)).slerp(eT[1], u))
    E = livre(P, psi, tronco, cab, {("IK", frente + "Hand"): mF, ("IK", tras + "Hand"): mT, ("IK", frente + "Foot"): pF, ("IK", tras + "Foot"): pT})
    sf = 1 if frente == "Left" else -1; st = -sf
    E["alvos"][("Polo", frente + "Foot")] = (Mp @ (V((1.4 * sf, 2.5, 1.2)) if 2.45 < t < 3.5 else V((0.6 * sf, -3.0, 0.8))), R)
    E["alvos"][("Polo", tras + "Foot")] = (Mp @ (V((2.0 * st, -1.0, 2.0)) if t > 2.95 else V((0.6 * st, -3.0, 0.8))), R)
    return mq.mistura(E, S, s_((t - 3.5) / 0.3))
# ------------------------------------------------------------------ DESMONTAR (6,0 s): o lobo deita com o cavaleiro (0,3-2,2); a perna de
# fora passa pela garupa, o corpo vira para o lobo e desce pelo flanco segurando a aba; pousa e se afasta dois passos
def desmontar(t, lado_l):
    s = 1 if lado_l == "E" else -1; ap = AP[lado_l]; Xs = XS[lado_l]
    psi0 = -90.0 * s
    perto, longe = ("Left", "Right") if s > 0 else ("Right", "Left")
    def L(x, y, z): return V((XC + s * x, y, z))
    S = mq.estado_sentado(assento()); Ms = S["pelve"]; Pq = Ms.translation
    if t < 2.3: return S
    P = herm(t, [(2.3, Pq), (2.55, Pq + V((0, 0.1, 0.4))), (2.85, Pq + V((s * 0.7, 0.2, 0.45))), (3.05, L(Xs - 0.55, 0.4, Pq.z - 0.05)),
                 (3.25, L(Xs - 0.15, 0.45, 2.3)), (3.4, L(Xs, 0.45, 1.85)), (3.6, L(Xs + 0.05, 0.45, 2.0)), (4.0, L(Xs + 1.0, 0.45, 2.0)), (4.4, L(Xs + 2.1, 0.45, 2.0))])
    psi = herm(t, [(2.3, 0.0), (2.5, 0.0), (2.85, psi0 * 0.85), (3.05, psi0)])
    tronco = herm(t, [(2.3, 8.0), (2.55, 22.0), (2.85, 22.0), (3.05, 14.0), (3.25, 10.0), (3.4, 16.0), (3.7, 6.0), (4.4, 2.0)])
    cab = herm(t, [(2.3, -5.0), (2.7, -12.0), (3.4, -14.0), (4.2, 0.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    sH = {k: S["alvos"][("IK", k + "Hand")] for k in ("Left", "Right")}
    def mao(lado_m, apoio_, t_ag):
        if t < t_ag: return sH[lado_m]
        if t < 3.12:
            return trilha(t, [(t_ag, sH[lado_m][0]), (t_ag + 0.12, no_osso(apoio_, MAO) + V((0, 0, 0.4))), (t_ag + 0.24, apoio_), (3.12, apoio_)], R, MAO)
        a_ = no_osso(apoio_, MAO); sl_ = 1 if lado_m == "Left" else -1
        return trilha(t, [(3.12, a_), (3.22, a_ + V((s * 0.7, 0, 0.3))), (3.4, Mp @ V((1.3 * sl_, 0.45, 1.1))), (3.7, solto(Mp, lado_m))], R, MAO)
    mP, mL = mao(perto, ap["aba_f"], 2.35), mao(longe, ap["aba"], 2.55)
    sP = 1 if perto == "Left" else -1; sL = -sP
    pS = {k: S["alvos"][("IK", k + "Foot")] for k in ("Left", "Right")}
    gP = L(Xs - 0.1, -0.15, TORN); gL = L(Xs, 1.15, TORN)
    def pendurado(lado_m):
        sl_ = 1 if lado_m == "Left" else -1; return fora(Mp @ V((0.55 * sl_, 0.9, -1.1)), s, 0.8)
    if t < 2.4: pL = pS[longe]
    elif t < 2.95:
        Lc = herm(t, [(2.4, Ms.inverted() @ pS[longe][0]), (2.58, V((1.5 * sL, 1.2, 0.45))), (2.76, V((0.4 * sL, 1.6, 0.5))), (2.95, Mp.inverted() @ pendurado(longe))])
        pL = (Mp @ Lc if t >= 2.76 else Ms @ Lc, R.slerp(R @ Rx(20), s_((t - 2.4) / 0.3)))
    elif t < 3.4: pL = (pendurado(longe), R @ Rx(20))
    else: pL = (passo(t, 3.95, 4.35, gL, L(Xs + 2.1, 1.15, TORN), 0.4) if t > 3.95 else gL, R)
    if t < 2.85: pP = pS[perto]
    elif t < 3.4:
        u = s_((t - 2.85) / 0.2); a_, b_ = pS[perto][0], pendurado(perto)
        pP = (herm(u, [(0.0, a_), (0.5, a_.lerp(b_, 0.5) + V((s * 0.5, 0, 0.3))), (1.0, b_)]), pS[perto][1].slerp(R @ Rx(20), u))
    else: pP = (passo(t, 3.75, 4.15, gP, L(Xs + 2.0, -0.15, TORN), 0.4) if t > 3.75 else gP, R)
    if 3.28 <= t < 3.4:
        u = s_((t - 3.28) / 0.12); pL = (pendurado(longe).lerp(gL, u), R); pP = (pendurado(perto).lerp(gP, u), R)
    E = livre(P, psi, tronco, cab, {("IK", perto + "Hand"): mP, ("IK", longe + "Hand"): mL, ("IK", perto + "Foot"): pP, ("IK", longe + "Foot"): pL})
    E["alvos"][("Polo", perto + "Foot")] = (Mp @ V((1.4 * sP, 2.5, 1.2)) if t < 3.4 else Mp @ V((0.6 * sP, -3.0, 0.8)), R)
    E["alvos"][("Polo", longe + "Foot")] = (Mp @ V((2.0 * sL, -1.0, 2.0)) if t < 2.9 else Mp @ V((1.4 * sL, 2.5, 1.2)) if t < 3.4 else Mp @ V((0.6 * sL, -3.0, 0.8)), R)
    return mq.mistura(S, E, s_((t - 2.3) / 0.3))
# ------------------------------------------------------------------ assar em FK + medicoes
amo = mq.amostras_partes(0.2)
DOBRA_JOELHO = float(os.environ.get("S2_DOBRA", "15"))
col = bpy.data.collections.new("TESTE_Montaria_M2"); sc.collection.children.link(col)
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
    QA["Montar_" + lado_l] = assar("DEMO_Cav_Montar_" + lado_l, "Montar_" + lado_l, lambda t, l=lado_l: montar(t, l), 6.2)
    QA["Desmontar_" + lado_l] = assar("DEMO_Cav_Desmontar_" + lado_l, "Desmontar_" + lado_l, lambda t, l=lado_l: desmontar(t, l), 6.0)
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
sc["m2"] = "cena de TESTE: lobo + sela M1 + manequim R15 aproximado; acoes DEMO_Cav_* = demonstracao"
json.dump({"resumo": resumo, "quadros": QA, "assento_quadril": list(Q_REP)}, open(A[2], "w"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[1])); print("DEMO_OK")
