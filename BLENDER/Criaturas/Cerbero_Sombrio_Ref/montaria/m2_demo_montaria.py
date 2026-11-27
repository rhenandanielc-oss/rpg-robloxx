"""Montaria M2 r2 (27/11/2026; r1 em montaria/r1/): DEMONSTRACAO da subida e da descida da sela reforcada do Cerbero Sombrio pelos dois lados, com o
manequim de TESTE (proporcoes aproximadas do R15; modulo manequim_r15.py do Crocodilo, so importado; nao e rig R15 validado nem
animacao publicada). Adaptado do demo "deitado" do Lobo Ancestral (montaria/v1_deitado/), que veio do Urso Silvestre.
O Cerbero toca Cerbero_MontarE/D e Cerbero_DesmontarE/D (montaria/clipes_montaria.py: ele DEITA); o manequim e animado por alvos
(quadril, maos, pes) com IK e assado em FK. Apoios medidos no Cerbero deitado: alca lateral de subida da sela, borda da sela,
cotovelo (degrau 1) e ombro (degrau 2); os pes sentados vao aos apoios de pe da sela.
Lados como no rig do Cerbero: E = x-, D = x+ (s = -1 / +1).
Subida: chega ao lado; agarra a alca lateral e a borda da sela; pe da frente no cotovelo, o corpo sobe; pe de tras no ombro,
sobe de novo; se puxa por cima da borda, a perna de tras passa pela garupa e cai no outro apoio; senta; o Cerbero levanta.
Descida: deitado; a perna de fora volta pela garupa e ele vira para o Cerbero; desce pelo ombro e pelo cotovelo segurando a
alca; pula o ultimo trecho e se afasta.
Uso: blender -b -t 1 montaria/CB_M1_sela.blend -P montaria/m2_demo_montaria.py -- <clipes_m2/CR_Cerbero_Anim.blend> <saida.blend> <saida_qa.json>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix as M, Quaternion as Q
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import m1_sela_cerbero as sl
DZ_EXTRA = 0.30                                   # r2: pose sentada da busca (m2_sentado_busca.json): quadril +0,25 e 0,3 para tras
DY_SENTA, AX_PE, AZ_PE = 0.30, 0.45, 0.15         # r2: pes 0,45 mais abertos e 0,15 mais altos nos apoios
A = sys.argv[sys.argv.index("--") + 1:]
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["Cerbero_Rig"]; sela = bpy.data.objects[sl.NOME]
CORPO = [bpy.data.objects["Cerbero_Corpo"], bpy.data.objects["Cerbero_Cabecas"]]
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"
    for c in pb.constraints: c.mute = True
SENT = {tuple(k.split("|")): tuple(v) for k, v in json.loads(sela["sentado"]).items()}
mq.SENTADO = dict(SENT)
for lado_ in ("LeftFoot", "RightFoot"):
    x_, y_, z_ = SENT[("IK", lado_)]; sx_ = 1 if lado_ == "LeftFoot" else -1; mq.SENTADO[("IK", lado_)] = (x_ + sx_ * AX_PE, y_, z_ + AZ_PE - DZ_EXTRA)
NOMES = ("Cerbero_MontarE", "Cerbero_MontarD", "Cerbero_DesmontarE", "Cerbero_DesmontarD")
for n_ in NOMES:
    if n_ in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[n_])
with bpy.data.libraries.load(os.path.abspath(A[0])) as (src, dst): dst.actions = [n for n in src.actions if n in NOMES]
for a_ in dst.actions: a_.use_fake_user = True
XC = sl.XC
if not arm.animation_data: arm.animation_data_create()
def leao_quadro(nome, t):
    arm.animation_data.action = bpy.data.actions["Cerbero_" + nome]
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
OSSO = "Coluna2"; BL = arm.data.bones[OSSO].matrix_local; Q_REP = V((XC, sl.ASSENTO_Y + DY_SENTA, Z_Q))
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
# ------------------------------------------------------------------ apoios medidos no Cerbero DEITADO, por lado
T_BAIXO = 4.0
AP = {}; XS = {}; YS = {}
INFO_SELA = json.load(open(os.path.join(RAIZ, "m1_sela.json")))
def rest_para_pose(p, osso):
    """ponto de repouso levado pela pose atual do osso"""
    b = arm.data.bones[osso]; pb = arm.pose.bones[osso]
    return arm.matrix_world @ pb.matrix @ b.matrix_local.inverted() @ arm.matrix_world.inverted() @ V(p)
for lado_l, s in (("E", -1), ("D", 1)):
    leao_quadro("Montar" + lado_l, T_BAIXO); q_ = assento().translation
    lado_r = "Left" if s > 0 else "Right"                                     # alca do lado x+ = "Left" na sela
    alca_rest = INFO_SELA["alca_subida"][lado_r]
    alca = rest_para_pose(alca_rest, OSSO)
    # r2: a alca vem da malha REAL da sela deformada (pecas "alca_subida" do lado s): ponto mais baixo do aro de ferro
    dg_ = bpy.context.evaluated_depsgraph_get(); ev_ = sela.evaluated_get(dg_); me_ = ev_.to_mesh(); W_ = sela.matrix_world
    pl_ = list(sela["pecas"]); ia_ = pl_.index("alca_subida"); at_ = me_.attributes["peca"].data
    pts_ = [W_ @ v.co for v, a_ in zip(me_.vertices, at_) if a_.value == ia_ and (W_ @ v.co).x * s > XC * s]
    ev_.to_mesh_clear()
    if pts_:
        zmin_ = min(p_.z for p_ in pts_); baixo_ = [p_ for p_ in pts_ if p_.z < zmin_ + 0.35]
        alca = sum(baixo_, V()) / len(baixo_)
    cot = arm.matrix_world @ arm.pose.bones["Antebraco" + lado_l].head          # cotovelo
    BVc = bvh_obj(lo)
    h1 = BVc.ray_cast(V((cot.x + s * 0.4, cot.y, cot.z + 6.0)), V((0, 0, -1)))
    deg1 = h1[0] if h1[0] else cot
    ys_ = alca.y - 0.9                                                         # o cavaleiro fica entre o cotovelo e a alca
    # r2: degrau 2 = o trecho mais PLANO do ombro (normal mais para cima) perto de 1,7 abaixo da alca (um ponto fixo caia sob
    # a placa do ombro no lado E e o pe entrava 0,45)
    cand = []
    for dy_ in (-0.4, -0.2, 0.0, 0.2, 0.4, 0.6):
        for dz_ in (-2.2, -1.9, -1.7, -1.5):
            h_ = BVc.ray_cast(V((XC + s * 12.0, ys_ + dy_, alca.z + dz_)), V((-s, 0, 0)))
            if h_[0] is not None: cand.append((h_[1].z - 0.15 * abs(dz_ + 1.7) - 0.1 * abs(dy_), h_[0]))
    deg2 = max(cand, key=lambda c: c[0])[1] if cand else V((XC + s * 4.0, ys_, alca.z - 1.7))
    fl = [flanco(s, y, z) for y in np.linspace(ys_ - 0.8, ys_ + 0.8, 5) for z in np.linspace(0.4, 2.6, 6)]
    XS[lado_l] = max(abs(x - XC) for x in fl) + 1.05                         # quadril do cavaleiro em pe: fora do flanco
    YS[lado_l] = ys_
    AP[lado_l] = {
        "alca": apoio(sela, alca, OSSO),
        "borda": apoio(sela, q_ + V((s * 1.5, 0.5, -0.5)), OSSO),
        "borda_f": apoio(sela, q_ + V((s * 1.5, -0.6, -0.5)), OSSO),
        "degrau1": apoio(lo, deg1, "Antebraco" + lado_l),
        "degrau2": apoio(lo, deg2, "Escapula" + lado_l),
        "degrau2f": apoio(lo, BVc.ray_cast(V((XC + s * 12.0, ys_ - 0.6, deg2.z)), V((-s, 0, 0)))[0] or deg2, "Escapula" + lado_l),
        # r2: pegadas baixas no corpo (alcancaveis do chao): ombro e flanco, a ~5,5-6 de altura
        "flanco_f": apoio(lo, V((XC + s * 12.0, ys_ - 0.5, 5.6)) if not BVc.ray_cast(V((XC + s * 12.0, ys_ - 0.5, 5.6)), V((-s, 0, 0)))[0] else BVc.ray_cast(V((XC + s * 12.0, ys_ - 0.5, 5.6)), V((-s, 0, 0)))[0], "Escapula" + lado_l),
        "flanco_t": apoio(lo, V((XC + s * 12.0, ys_ + 0.7, 6.0)) if not BVc.ray_cast(V((XC + s * 12.0, ys_ + 0.7, 6.0)), V((-s, 0, 0)))[0] else BVc.ray_cast(V((XC + s * 12.0, ys_ + 0.7, 6.0)), V((-s, 0, 0)))[0], "Coluna2"),
    }
    print("APOIOS", lado_l, "quadril", [round(c, 2) for c in q_], "XS %.2f YS %.2f" % (XS[lado_l], ys_),
          {k: [round(c, 2) for c in no_osso(v)] for k, v in AP[lado_l].items()}, flush=True)
def afasta(P, s, folga=0.95):
    """r2: o quadril fica fora do flanco na altura do tronco (o flanco deitado faz barriga acima dos degraus)"""
    fx = [flanco(s, P.y + dy, P.z + dz) for dy in (-0.4, 0.0, 0.4) for dz in (-0.6, 0.4, 1.4, 2.4)]
    f_ = max(fx) if s > 0 else min(fx)
    return V((max(P.x, f_ + folga), P.y, P.z)) if s > 0 else V((min(P.x, f_ - folga), P.y, P.z))
PE_DEG = Q()                                       # r2: no degrau, o pe fica de lado (ponta para -Y, ao longo do corpo)
def estribo(S, lado):
    return S["alvos"][("IK", lado + "Foot")]
# ------------------------------------------------------------------ MONTAR (8,7 s; deitado de 2,9 a 6,5)
def _montar_base(t, lado_l):
    s = -1 if lado_l == "E" else 1; ap = AP[lado_l]; Xs = XS[lado_l]; y0 = YS[lado_l]
    psi0 = -90.0 * s
    frente, tras = ("Left", "Right") if s > 0 else ("Right", "Left")
    def L(x, y, z): return V((XC + s * x, y, z))
    S = mq.estado_sentado(assento()); Ms = S["pelve"]; Pq = Ms.translation
    d1 = no_osso(ap["degrau1"], TORN + 0.15); d2 = no_osso(ap["degrau2"], TORN + 0.15)   # r2: pe de caixa nao afunda na curva
    f2 = abs(d2.x - XC)                                                        # x do ombro (distancia do centro)
    P = herm(t, [(0.0, L(Xs + 3.5, y0 + 0.6, 2.0)), (2.2, L(Xs, y0, 2.0)), (3.1, L(Xs, y0, 2.0)), (3.25, L(Xs + 0.05, y0, 1.85)),
                 (3.7, V((d1.x + s * 0.75, y0, d1.z + 1.35))), (4.0, V((d1.x + s * 0.65, y0, d1.z + 1.55))),
                 (4.55, L(f2 + 0.85, y0 + 0.1, d2.z + 1.25)), (4.75, L(f2 + 0.75, y0 + 0.1, d2.z + 1.45)),
                 (5.1, Pq + V((s * 1.55, 0.0, 0.55))), (5.4, Pq + V((s * 0.7, 0.05, 0.55))), (5.7, Pq + V((0, 0, 0.12))), (5.9, Pq)])
    if 2.9 < t < 5.05: P = P.lerp(afasta(P, s, 1.35), s_((t - 2.9) / 0.4) * (1 - s_((t - 4.6) / 0.45)))   # r2: rampas mais longas; quadril 1,35 fora do flanco (bracos livres)
    psi = herm(t, [(0.0, psi0), (5.05, psi0), (5.4, psi0 * 0.45), (5.75, 0.0)])
    tronco = herm(t, [(0.0, 0.0), (2.2, 4.0), (3.2, 10.0), (3.7, 14.0), (4.0, 10.0), (4.55, 14.0), (4.8, 24.0), (5.1, 38.0),
                      (5.4, 24.0), (5.7, 12.0), (5.9, 8.0)])
    cab = herm(t, [(0.0, 0.0), (2.6, -18.0), (4.5, -12.0), (5.9, -5.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    def mao(lado_m, seq):
        """r2: seq = [(t_pega, apoio), ...]: cada pegada so quando o apoio esta ao alcance; entre elas a mao sobe por fora"""
        sl_ = 1 if lado_m == "Left" else -1; cima = Mp @ V((0.9 * sl_, -0.6, 2.1)); t0 = seq[0][0]
        if t < t0 - 0.35: return (solto(Mp, lado_m), R)
        ch = [(t0 - 0.35, solto(Mp, lado_m)), (t0 - 0.12, no_osso(seq[0][1], MAO) + V((s * 0.4, 0, 0.3))), (t0, seq[0][1])]
        for (ta_, ap1), (tb_, ap2) in zip(seq, seq[1:]):
            ch += [(tb_ - 0.25, ap1), (tb_ - 0.12, no_osso(ap2, MAO) + V((s * 0.9, 0, 0.35))), (tb_, ap2)]   # r2: a mao troca de pegada por fora
        ch += [(5.8, seq[-1][1])]
        return trilha(t, ch, R, MAO)
    mF = mao(frente, [(2.95, ap["flanco_f"]), (3.75, ap["alca"]), (4.75, ap["borda_f"])])
    mT = mao(tras, [(3.05, ap["flanco_t"]), (4.05, ap["alca"]), (4.6, ap["borda"])])
    gF = L(Xs - 0.1, y0 - 0.6, TORN); gT = L(Xs - 0.05, y0 + 0.6, TORN)
    pF = (passo(t, 1.0, 1.7, L(Xs + 3.5, y0, TORN), gF), R); pT = (passo(t, 0.3, 1.0, L(Xs + 3.5, y0 + 1.2, TORN), gT), R)
    if t >= 3.2:       # pe da frente: sobe no cotovelo (degrau 1) e fica nele ate passar para o apoio de pe
        u = s_((t - 3.2) / 0.35)
        pF = (herm(u, [(0.0, gF), (0.5, gF.lerp(d1, 0.5) + V((s * 0.4, 0, 0.6))), (1.0, d1)]), R.slerp(PE_DEG, u))                                     # r2: pe de lado no degrau (ponta para a frente do Cerbero)
        d2f = no_osso(ap["degrau2f"], TORN + 0.15)                                # r2: ponto real do ombro (antes d2 - 0,6 em y entrava na barriga)
        if t >= 4.4:   # sobe tambem para o ombro (os dois pes no degrau 2)
            u2 = s_((t - 4.4) / 0.35); pF = (herm(u2, [(0.0, d1), (0.5, d1.lerp(d2f, 0.5) + V((s * 0.95, 0, 0.5))), (1.0, d2f)]), PE_DEG)
        if t >= 4.95:
            eF = estribo(S, frente); u2 = s_((t - 4.95) / 0.45)
            pF = (herm(u2, [(0.0, d2f), (0.5, d2f.lerp(eF[0], 0.5) + V((s * 0.6, 0, 0.5))), (1.0, eF[0])]), R.slerp(eF[1], u2))
    if t >= 3.95:      # pe de tras: sobe no ombro (degrau 2)
        u = s_((t - 3.95) / 0.4)
        pT = (herm(u, [(0.0, gT), (0.5, gT.lerp(d2, 0.5) + V((s * 0.95, 0, 0.6))), (1.0, d2)]), R.slerp(PE_DEG, u))
    if t >= 4.95:      # perna de tras: sai do ombro, passa dobrada pela garupa e cai no apoio do outro lado
        so_ = 1 if tras == "Left" else -1
        Lc = herm(t, [(4.95, Mp.inverted() @ d2), (5.15, V((0.6 * so_, 0.6, -0.9))), (5.32, V((1.0 * so_, 1.3, -0.2))),
                      (5.5, V((1.6 * so_, 1.2, 0.25))), (5.65, V((1.8 * so_, 0.3, -0.4)))])
        if t < 5.65: pT = (Mp @ Lc, R.slerp(R @ Rx(20), s_((t - 4.95) / 0.4)))
        else:
            eT = estribo(S, tras); u = s_((t - 5.65) / 0.25); pT = ((Mp @ Lc).lerp(eT[0], u), (R @ Rx(20)).slerp(eT[1], u))
    E = livre(P, psi, tronco, cab, {("IK", frente + "Hand"): mF, ("IK", tras + "Hand"): mT, ("IK", frente + "Foot"): pF, ("IK", tras + "Foot"): pT})
    sf = 1 if frente == "Left" else -1; st = -sf
    E["alvos"][("Polo", frente + "Foot")] = (Mp @ (V((1.0 * sf, -2.5, 1.2)) if 3.2 < t < 5.4 else V((0.6 * sf, -3.0, 0.8))), R)
    E["alvos"][("Polo", tras + "Foot")] = (Mp @ (V((1.0 * st, -2.5, 1.2)) if 3.95 < t < 5.0 else V((2.0 * st, -1.0, 2.0)) if t >= 5.0 else V((0.6 * st, -3.0, 0.8))), R)
    return mq.mistura(E, S, s_((t - 5.6) / 0.3))
# ------------------------------------------------------------------ DESMONTAR r2 (8,8 s): deitado de 2,9 a 6,6
# r2 (27/11): o ultimo trecho virou um PULO com fisica legivel: agacha no cotovelo segurando a alca (4,35-4,6), solta e empurra
# para fora e para tras; voo balistico com g = 28 studs/s^2 (9,81 m/s^2 com 1 stud ~ 0,35 m do R15); os pes tocam o chao com
# a perna quase estendida; absorve dobrando os joelhos com desaceleracao constante (sem parada seca); fica agachado 0,15 s,
# levanta em 0,5 s e se afasta dois passos ANTES de o Cerbero levantar (6,6).
G_PULO = 28.0; V_PULO = (2.4, 2.2)                               # empurrao: para fora (studs/s), para cima
T_SOLTA = 4.6; Z_CONTATO = 1.95; Z_AGACHA = 0.95                 # r2: absorve 1,0 stud (4 quadros), sem parada seca
def _pulo(d1, s, y0):
    P0 = afasta(V((d1.x + s * 0.8, y0, d1.z + 1.2)), s, 1.35); vx, vz = s * V_PULO[0], V_PULO[1]   # r2: parte de onde o quadril ja esta (sem salto na soltura)
    a, b, c = -0.5 * G_PULO, vz, P0.z - Z_CONTATO; tc = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)   # tempo de voo ate o contato
    vzc = vz - G_PULO * tc; Pc = V((P0.x + vx * tc, y0, Z_CONTATO))
    ta = 2 * (Z_CONTATO - Z_AGACHA) / abs(vzc)                                                            # desaceleracao constante ate Z_AGACHA
    return P0, vx, vz, tc, vzc, Pc, ta
def _desmontar_base(t, lado_l):
    s = -1 if lado_l == "E" else 1; ap = AP[lado_l]; Xs = XS[lado_l]; y0 = YS[lado_l]
    psi0 = -90.0 * s
    perto, longe = ("Left", "Right") if s > 0 else ("Right", "Left")
    def L(x, y, z): return V((XC + s * x, y, z))
    S = mq.estado_sentado(assento()); Ms = S["pelve"]; Pq = Ms.translation
    if t < 3.0: return S
    d1 = no_osso(ap["degrau1"], TORN + 0.15); d2 = no_osso(ap["degrau2"], TORN + 0.15); f2 = abs(d2.x - XC)   # r2: pe de caixa nao afunda na curva
    P0, vx, vz, tc, vzc, Pc, ta = _pulo(d1, s, y0)
    t_c = T_SOLTA + tc; t_a = t_c + ta; t_lev = t_a + 0.15; t_em_pe = t_lev + 0.5
    Pa = V((Pc.x + vx * ta / 2, y0, Z_AGACHA))                                         # fim da absorcao (horizontal tambem desacelera)
    if t < T_SOLTA:
        P = herm(t, [(3.0, Pq), (3.2, Pq + V((0, 0.1, 0.4))), (3.5, Pq + V((s * 0.9, 0.05, 0.5))), (3.85, L(f2 + 0.8, y0 + 0.1, d2.z + 1.5)),
                     (4.05, L(f2 + 0.85, y0 + 0.1, d2.z + 1.25)), (4.35, V((d1.x + s * 0.7, y0, d1.z + 1.45))), (T_SOLTA, P0)])
        if 3.4 < t: P = P.lerp(afasta(P, s, 1.35), s_((t - 3.4) / 0.5))                 # r2: rampa de 0,5 s (0,2 dava pico de velocidade)
    elif t < t_c: u = t - T_SOLTA; P = V((P0.x + vx * u, y0, P0.z + vz * u - 0.5 * G_PULO * u * u))
    elif t < t_a:
        u = (t - t_c) / ta; P = V((Pc.x + vx * ta * (u - u * u / 2), y0, Pc.z + vzc * ta * (u - u * u / 2)))   # v cai linearmente a zero
    elif t < t_lev: P = Pa.copy()
    elif t < t_em_pe: P = Pa.lerp(V((Pa.x, y0, 2.0)), s_((t - t_lev) / 0.5))
    else:
        Pf = V((Pa.x, y0, 2.0)); P = herm(t, [(t_em_pe, Pf), (t_em_pe + 0.5, Pf + V((s * 1.2, 0, 0))), (t_em_pe + 1.0, Pf + V((s * 2.6, 0, 0)))])
    psi = herm(t, [(3.0, 0.0), (3.2, 0.0), (3.5, psi0 * 0.85), (3.75, psi0)])
    tronco = herm(t, [(3.0, 8.0), (3.2, 22.0), (3.5, 30.0), (3.75, 18.0), (3.95, 12.0), (4.35, 12.0), (T_SOLTA, 20.0), (T_SOLTA + 0.15, 6.0),
                      (t_c, 4.0), (t_a, 26.0), (t_lev, 24.0), (t_em_pe, 4.0), (t_em_pe + 1.0, 2.0)])
    cab = herm(t, [(3.0, -5.0), (3.4, -14.0), (4.5, -16.0), (t_c, -8.0), (t_a, -18.0), (t_em_pe + 0.6, 0.0)])
    Mp = M.Translation(P) @ Rz(psi).to_matrix().to_4x4(); R = Rz(psi)
    sH = {k: S["alvos"][("IK", k + "Hand")] for k in ("Left", "Right")}
    def mao(lado_m, apoio_, t_ag, t_solta):
        if t < t_ag: return sH[lado_m]
        sl_ = 1 if lado_m == "Left" else -1
        if t < t_solta:
            return trilha(t, [(t_ag, sH[lado_m][0]), (t_ag + 0.12, no_osso(apoio_, MAO) + V((0, 0, 0.4))), (t_ag + 0.24, apoio_), (t_solta, apoio_)], R, MAO)
        a_ = no_osso(apoio_, MAO)
        if t < t_c:                                                                # bracos abrem para equilibrar no voo
            return trilha(t, [(t_solta, a_), (t_solta + 0.12, a_ + V((s * 0.5, 0, 0.1))), (t_c, Mp @ V((1.9 * sl_, -0.3, 0.9)))], R, MAO)
        return trilha(t, [(t_c, Mp @ V((1.9 * sl_, -0.3, 0.9))), (t_a, Mp @ V((1.4 * sl_, -0.9, 0.3))), (t_em_pe, solto(Mp, lado_m))], R, MAO)
    mP = mao(perto, ap["alca"], 3.05, T_SOLTA)
    if t < 4.3: mL = mao(longe, ap["borda"], 3.25, 4.3)
    elif t < T_SOLTA:                                                              # a mao de longe tambem desce para a alca (as duas seguram)
        mL = trilha(t, [(4.3, no_osso(ap["borda"], MAO)), (4.45, no_osso(ap["alca"], MAO) + V((0, 0.35, 0.3))), (4.55, ap["alca"]), (T_SOLTA, ap["alca"])], R, MAO)
    else: mL = mao(longe, ap["alca"], 3.25, T_SOLTA)
    sP = 1 if perto == "Left" else -1; sL = -sP
    pS = {k: S["alvos"][("IK", k + "Foot")] for k in ("Left", "Right")}
    def pe_voo(sl_):                                                               # pes sob o quadril, prontos para tocar
        return Mp @ V((0.5 * sl_, -0.15, -(Z_CONTATO - TORN) + 0.02))
    Mc = M.Translation(Pc) @ Rz(psi0).to_matrix().to_4x4()
    def pe_chao(sl_):
        p_ = Mc @ V((0.5 * sl_, -0.15, 0)); return V((p_.x, p_.y, TORN))
    def pe_fase(lado_m, pe_antes):
        sl_ = 1 if lado_m == "Left" else -1
        if t < T_SOLTA: return pe_antes
        if t < T_SOLTA + 0.15: return (pe_antes[0].lerp(pe_voo(sl_), s_((t - T_SOLTA) / 0.15)), R)
        if t < t_c: return (pe_voo(sl_), R)
        ch = pe_chao(sl_); alvo_ = ch + V((s * 2.6, 0, 0)); t0_ = t_em_pe + (0.05 if lado_m == perto else 0.5)
        if t < t0_: return (ch, R)
        if t < t0_ + 0.45: return (passo(t, t0_, t0_ + 0.45, ch, alvo_, 0.35), R)
        return (alvo_, R)
    # perna de fora: volta pela garupa (3,1-3,6) e pisa no ombro (degrau 2); depois no cotovelo
    if t < 3.1: pL = pS[longe]
    elif t < 3.6:
        Lc = herm(t, [(3.1, Ms.inverted() @ pS[longe][0]), (3.28, V((1.6 * sL, 1.2, 0.35))), (3.45, V((0.6 * sL, 1.5, 0.4)))])
        pL = (Ms @ Lc if t < 3.45 else (Ms @ Lc).lerp(d2, s_((t - 3.45) / 0.15)), R.slerp(R @ Rx(20), s_((t - 3.1) / 0.3)))
    elif t < 4.1: pL = (d2, PE_DEG)
    else: u = s_((t - 4.1) / 0.3); pL = (d2.lerp(d1 + V((0, 0.5, 0)), u) + V((s * 0.95 * math.sin(math.pi * u), 0, 0)), PE_DEG)
    pL = pe_fase(longe, pL)
    # perna de perto: sai do apoio de pe e desce para o ombro e o cotovelo
    if t < 3.55: pP = pS[perto]
    elif t < 3.9: u = s_((t - 3.55) / 0.3); pP = (herm(u, [(0.0, pS[perto][0]), (0.5, pS[perto][0].lerp(d2, 0.5) + V((s * 0.5, 0, 0.3))), (1.0, d2 + V((0, -0.5, 0)))]), R)
    else: u = s_((t - 3.95) / 0.3); pP = ((d2 + V((0, -0.5, 0))).lerp(d1, u) + V((s * 0.95 * math.sin(math.pi * u), 0, 0)), PE_DEG)
    pP = pe_fase(perto, pP)
    E = livre(P, psi, tronco, cab, {("IK", perto + "Hand"): mP, ("IK", longe + "Hand"): mL, ("IK", perto + "Foot"): pP, ("IK", longe + "Foot"): pL})
    E["alvos"][("Polo", perto + "Foot")] = (Mp @ (V((1.0 * sP, -2.5, 1.2)) if 3.55 < t < T_SOLTA else V((0.6 * sP, -3.0, 0.8))), R)
    E["alvos"][("Polo", longe + "Foot")] = (Mp @ (V((2.0 * sL, -1.0, 2.0)) if t < 3.45 else V((1.0 * sL, -2.5, 1.2)) if t < T_SOLTA else V((0.6 * sL, -3.0, 0.8))), R)
    return mq.mistura(S, E, s_((t - 3.0) / 0.3))
# r2: mais tempo nos trechos rapidos (sem mexer nas poses): subida por cima da borda (4,75-5,95 -> 4,75-6,35) e saida da sela
# ate o cotovelo na descida (3,2-4,45 -> 3,2-4,825); o resto so desloca
def _tw(t, a, b, f):
    if t <= a: return t
    if t <= a + (b - a) * f: return a + (t - a) / f
    return t - (b - a) * (f - 1)
TW_M = (4.75, 5.95, 4.0 / 3.0); TW_D = (3.2, 4.45, 1.3)
def montar(t, lado_l): return _montar_base(_tw(t, *TW_M), lado_l)
def desmontar(t, lado_l): return _desmontar_base(_tw(t, *TW_D), lado_l)
for lado_l in ("E", "D"):
    s_l = -1 if lado_l == "E" else 1; leao_quadro("Montar" + lado_l, T_BAIXO)
    d1_ = no_osso(AP[lado_l]["degrau1"], TORN + 0.15); _p = _pulo(d1_, s_l, YS[lado_l])
    dsl = (TW_D[1] - TW_D[0]) * (TW_D[2] - 1)
    print("PULO", lado_l, "solta %.3f contato %.3f absorve %.3f vel_contato %.2f" % (T_SOLTA + dsl, T_SOLTA + dsl + _p[3], _p[6], math.hypot(_p[1], _p[4])), flush=True)
# ------------------------------------------------------------------ assar em FK + medicoes
amo = mq.amostras_partes(0.2)
DOBRA_JOELHO = float(os.environ.get("S2_DOBRA", "15"))
col = bpy.data.collections.new("TESTE_Montaria_M2"); sc.collection.children.link(col)
ra, ob, alvos = mq.criar(col)
# ------------------------------------------------------------------ r2 (27/11): corretor de folgas do cavaleiro
# Para cada quadro: aplica o estado, mede a penetracao de cada parte do manequim no corpo do Cerbero (pele + cabecas) e na sela;
# a parte que entra empurra o alvo que a controla para fora, pela normal da superficie mais proxima (mao/antebraco -> alvo da
# mao; pe/canela -> alvo do pe; coxa/tronco/cabeca -> quadril). Passe 1 acha os empurroes quadro a quadro; eles sao suavizados
# no tempo (maximo +-4 quadros e media +-4 quadros, sem tremer) e o passe 2 aplica e mede de novo.
FOLGA_ALVO = {"Hand": 0.02, "default": 0.04}       # a mao encosta (pegada); o resto fica um pouco afastado
AMO_S = mq.amostras_partes(0.3)
def _penetracao(ra, bvh, nm):
    """(sinal, empurrao) da parte nm: sinal < 0 = dentro; empurrao = vetor que leva o ponto mais fundo ate a superficie"""
    Mb = ra.matrix_world @ ra.pose.bones[nm].matrix @ ra.data.bones[nm].matrix_local.inverted()
    pior, emp = 9.0, None
    c0 = Mb @ V(AMO_S[nm].mean(0))
    if bvh.find_nearest(c0, 2.6)[0] is None: return 9.0, None          # longe: nada a corrigir
    for p in AMO_S[nm]:
        w = Mb @ V(p); loc, nor, _, d = bvh.find_nearest(w, 3.0)
        if loc is None: continue
        if mq.dentro(bvh, w):
            if -d < pior: pior, emp = -d, (loc - w)
        elif d < pior: pior, emp = d, None
    return pior, emp
def _alvo_de(nm):
    lado = "Left" if nm.startswith("Left") else "Right" if nm.startswith("Right") else None
    if lado and nm.endswith(("Hand", "LowerArm")): return ("IK", lado + "Hand")             # r2: braco (ombro) empurra o quadril
    if lado and nm.endswith(("Foot", "LowerLeg")): return ("IK", lado + "Foot")
    return "pelve"
def _aplicar_off(est, off):
    if not off: return est
    e = {"pelve": est["pelve"].copy(), "tronco": est["tronco"], "cabeca": est["cabeca"], "alvos": dict(est["alvos"])}
    for k, v in off.items():
        if k == "pelve": e["pelve"] = M.Translation(v) @ e["pelve"]
        elif k in e["alvos"]: p_, q_ = e["alvos"][k]; e["alvos"][k] = (p_ + v, q_)
    return e
def _pose(est):
    for pb in ra.pose.bones:
        for c in pb.constraints: c.mute = False
    mq.aplicar(ra, alvos, est)
    for lado_ in ("Left", "Right"):
        ra.pose.bones[lado_ + "LowerLeg"].rotation_quaternion = Q(V((1, 0, 0)), math.radians(DOBRA_JOELHO))
    bpy.context.view_layer.update()
def _resolver(est, bvhs, iters=4):
    off = {}
    for _ in range(iters):
        _pose(_aplicar_off(est, off)); mudou = False; emp_alvo = {}
        for nm in AMO_S:
            for bvh in bvhs:
                sg, emp = _penetracao(ra, bvh, nm)
                lim = FOLGA_ALVO["Hand"] if nm.endswith("Hand") else FOLGA_ALVO["default"]
                if emp is not None:
                    v = emp + emp.normalized() * lim
                    k = _alvo_de(nm)
                    if k not in emp_alvo or v.length > emp_alvo[k].length: emp_alvo[k] = v
        for k, v in emp_alvo.items():
            off[k] = off.get(k, V()) + v; mudou = True
        if not mudou: break
    return off
def _suavizar(offs, r=6):
    chaves = set(k for o in offs for k in o); n = len(offs); out = [dict() for _ in range(n)]
    for k in chaves:
        seq = [o.get(k, V()) for o in offs]
        mx = [max(seq[max(0, i - r):i + r + 1], key=lambda v: v.length) for i in range(n)]
        for i in range(n):
            jan = mx[max(0, i - r):i + r + 1]; out[i][k] = sum(jan, V()) / len(jan)
    return out
CORRIGIR = os.environ.get("CERB_CORRIGIR", "1") == "1"
OFFS = {}
def assar(nome_acao, clipe, fn, dur, ativo=lambda t: False):
    nq = int(round(dur * FPS)) + 1; poses = []; med = []; prev = None
    offs = [dict() for _ in range(nq)]
    if CORRIGIR:                                                  # r2: passe 1 (empurroes por quadro) + suavizacao
        for qi in range(nq):
            t = qi / FPS
            if clipe: leao_quadro(clipe, t)
            else: zerar_leao()
            offs[qi] = _resolver(fn(t), [bvh_obj(lo), bvh_obj(sela)]) if ativo(t) else {}   # sentado: pose fixa (sem corretor, sem tremor)
        offs = _suavizar(offs)
        print("CORRIGIDO", nome_acao, "max empurrao %.2f" % max((v.length for o in offs for v in o.values()), default=0.0), flush=True)
    OFFS[nome_acao] = [{(k if isinstance(k, str) else "|".join(k)): [round(c, 3) for c in v] for k, v in o.items()} for o in offs]
    for qi in range(nq):
        t = qi / FPS
        if clipe: leao_quadro(clipe, t)
        else: zerar_leao()
        est = _aplicar_off(fn(t), offs[qi])
        _pose(est)
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
DUR_M = bpy.data.actions["Cerbero_MontarE"].frame_range[1] / FPS; DUR_DM = bpy.data.actions["Cerbero_DesmontarE"].frame_range[1] / FPS
for lado_l in [l_ for l_ in ("E", "D") if l_ in os.environ.get("CERB_LADOS", "ED")]:
    QA["Montar" + lado_l] = assar("DEMO_Cav_Montar" + lado_l, "Montar" + lado_l, lambda t, l=lado_l: montar(t, l), round(DUR_M - 1.0 / FPS, 3), lambda t: t < 6.15)
    QA["Desmontar" + lado_l] = assar("DEMO_Cav_Desmontar" + lado_l, "Desmontar" + lado_l, lambda t, l=lado_l: desmontar(t, l), round(DUR_DM - 1.0 / FPS, 3), lambda t: t > 3.05)
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
sc["m2"] = "cena de TESTE: Cerbero + sela M1 + manequim R15 aproximado; acoes DEMO_Cav_* = demonstracao"
json.dump({"resumo": resumo, "quadros": QA, "assento_quadril": list(Q_REP), "empurroes_r2": OFFS}, open(A[2], "w"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[1])); print("DEMO_OK")
