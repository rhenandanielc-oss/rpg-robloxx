# Funcoes comuns dos clipes da Wyvern a partir do lote 2 (carregado com exec pelos scripts 08*).
# As mesmas convencoes do lote 1 (07_clipes_lote1.py): poses como {osso: (loc, quat, esc)} + fold (shape keys),
# rotacoes em eixo do MUNDO convertidas para o local do osso, deslocamentos da raiz no mundo, chaves a 30 Hz.
# A mais: cinematica direta propria (sem atualizar a cena), IK de perna por minimos quadrados e o z minimo da malha
# por regiao (osso dominante do vertice) para encostar partes no chao.
import bpy, math
import numpy as np
from mathutils import Vector as V, Quaternion as Q, Matrix
from bpy_extras import anim_utils
sc = bpy.context.scene; FPS_CENA = sc.render.fps; HZ = 30
arm = bpy.data.objects["Wyvern_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
obj = bpy.data.objects["Wyvern"]; key = obj.data.shape_keys
R = math.radians
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def curvas(act):
    m = {}
    for L in act.layers:
        for s in L.strips:
            for cb in s.channelbags:
                for f in cb.fcurves: m[(f.data_path, f.array_index)] = f
    return m
FONTE = {n: curvas(bpy.data.actions[n]) for n in ("idle_loop", "walk_loop", "fly_loop", "takeoff", "roar", "bite")}
DUR = {n: bpy.data.actions[n].frame_range[1] / FPS_CENA for n in FONTE}
OSSOS = [b.name for b in BD]
def amostra(clipe, t, loop=True):
    T = DUR[clipe]; t = (t % T) if loop else min(max(t, 0.0), T); fr = t * FPS_CENA; m = FONTE[clipe]; P = {}
    for b in OSSOS:
        pb = 'pose.bones["%s"].' % b
        loc = V([m[(pb + "location", i)].evaluate(fr) if (pb + "location", i) in m else 0.0 for i in range(3)])
        q = Q([m[(pb + "rotation_quaternion", i)].evaluate(fr) if (pb + "rotation_quaternion", i) in m else (1.0 if i == 0 else 0.0) for i in range(4)])
        esc = V([m[(pb + "scale", i)].evaluate(fr) if (pb + "scale", i) in m else 1.0 for i in range(3)])
        P[b] = (loc, q.normalized(), esc)
    fk = 'key_blocks["fold_corrective_L"].value'
    fold = m[(fk, 0)].evaluate(fr) if (fk, 0) in m else 0.0
    return P, fold
def copia(P): return {b: (l.copy(), q.copy(), e.copy()) for b, (l, q, e) in P.items()}
def misturar(A, B, w, ossos=None):
    C = copia(A)
    for b in (ossos or A):
        qa, qb = A[b][1], B[b][1]
        if qa.dot(qb) < 0: qb = -qb
        C[b] = (A[b][0].lerp(B[b][0], w), qa.slerp(qb, w), A[b][2].lerp(B[b][2], w))
    return C
def rot_mundo(osso, eixo, ang):
    r = BD[osso].matrix_local.to_3x3()
    return (r.inverted() @ Matrix.Rotation(ang, 3, eixo) @ r).to_quaternion()
def mover(P, osso, desl):
    l, q, e = P[osso]; P[osso] = (l + BD[osso].matrix_local.to_3x3().inverted() @ desl, q, e)
def girar(P, osso, eixo, ang):
    l, q, e = P[osso]; P[osso] = (l, rot_mundo(osso, eixo, ang) @ q, e)
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
FRENTE = -Y
ESQ = 1.0 if BD["upperarm_L"].head_local.x > 0 else -1.0
ASA = {s: [b for b in OSSOS if b.endswith("_" + s) and any(k in b for k in ("shoulder", "upperarm", "forearm", "hand", "finger", "strut", "thumb"))] for s in "LR"}
PERNA = {s: ["thigh_" + s, "calf_" + s, "foot_" + s, "toe_" + s] for s in "LR"}
COLUNA = ["spine_01", "spine_02", "spine_03"]; PESCOCO = ["neck_01", "neck_02", "neck_03", "neck_04", "neck_05"]
CAUDA = ["tail_%02d" % i for i in range(1, 11)]
for pb in PB: pb.rotation_mode = "QUATERNION"
# ---------------------------------------------------------------- cinematica direta propria (espaco do armature)
REL = {}
for b in BD:
    REL[b.name] = (b.parent.matrix_local.inverted() @ b.matrix_local) if b.parent else b.matrix_local.copy()
PAI = {b.name: (b.parent.name if b.parent else None) for b in BD}
COMP = {b.name: b.length for b in BD}
def cadeia(osso):
    c = []
    while osso: c.append(osso); osso = PAI[osso]
    return c[::-1]
def fk(P, ossos=None):
    M = {}
    for b in (ossos or OSSOS):
        if b in M: continue
        for c in cadeia(b):
            if c in M: continue
            l, q, e = P[c]
            base = Matrix.LocRotScale(l, q, e)
            M[c] = (M[PAI[c]] @ REL[c] @ base) if PAI[c] else (REL[c] @ base)
    return M
MW = arm.matrix_world.copy()
def cabeca(M, b): return MW @ M[b].translation
def ponta(M, b): return MW @ (M[b] @ V((0, COMP[b], 0)))
# ---------------------------------------------------------------- IK de perna (minimos quadrados, Gauss-Newton numerico)
def ik_perna(P, lado, alvos, eixos=None, it=40):
    """alvos: lista (funcao(M)->Vector, Vector alvo, peso). Ajusta rotacoes em X do mundo de coxa/canela/pe/dedo
    (eixos extras: lista de (osso, eixo))."""
    gl = eixos or [(b, X) for b in PERNA[lado]]
    ch = PERNA[lado]
    def resid(Pp):
        M = fk(Pp, ch); r = []
        for f, alvo, w in alvos:                                 # w: escalar ou Vector (peso por componente)
            d = f(M) - alvo; w3 = w if isinstance(w, V) else V((w, w, w)); r += [d.x * w3.x, d.y * w3.y, d.z * w3.z]
        return np.array(r)
    for _ in range(it):
        r0 = resid(P)
        if np.dot(r0, r0) < 1e-8: break
        J = np.zeros((len(r0), len(gl))); h = 1e-4
        for j, (b, ax) in enumerate(gl):
            Pp = dict(P); girar(Pp, b, ax, h); J[:, j] = (resid(Pp) - r0) / h
        lam = 1e-3
        dx = np.linalg.solve(J.T @ J + lam * np.eye(len(gl)), -J.T @ r0)
        dx = np.clip(dx, -0.3, 0.3)
        for j, (b, ax) in enumerate(gl): girar(P, b, ax, float(dx[j]))
    r = resid(P)
    return float(np.sqrt(np.dot(r, r) / max(len(r) // 3, 1)))
# ---------------------------------------------------------------- malha avaliada: z minimo por regiao
GR = {g.index: g.name for g in obj.vertex_groups}
NV = len(obj.data.vertices)
DOM = []
for v in obj.data.vertices:
    DOM.append(GR[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "?")
def regiao_de(osso):
    if osso.startswith("tail"): return "cauda"
    if osso.startswith(("neck", "head", "jaw", "breath")): return "cabeca"
    for s in "LR":
        if osso in ASA[s]: return "asa" + s
        if osso in PERNA[s]: return "perna" + s
    return "corpo"
REG = np.array([regiao_de(d) if d != "?" else "corpo" for d in DOM])
def aplicar(P, fold):
    for b in OSSOS:
        l, q, e = P[b]; PB[b].location = l; PB[b].rotation_quaternion = q; PB[b].scale = e
    for s in "LR": key.key_blocks["fold_corrective_" + s].value = fold
    bpy.context.view_layer.update()
def malha_np(P, fold):
    aplicar(P, fold)
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    co = np.empty(len(ev.vertices) * 3); ev.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    m = np.array(obj.matrix_world); return co @ m[:3, :3].T + m[:3, 3]
def zmin_reg(P, fold):
    co = malha_np(P, fold)
    return {r: round(float(co[REG == r][:, 2].min()), 3) for r in sorted(set(REG))}
DOMA = np.array(DOM)
def zmin_ossos(P, fold, ossos):
    co = malha_np(P, fold); return float(co[np.isin(DOMA, ossos)][:, 2].min())
def bissecao(fn, a, b, alvo, it=18):
    """acha x em [a,b] com fn(x)=alvo (fn monotona)"""
    fa = fn(a) - alvo
    for _ in range(it):
        m = (a + b) / 2; fm = fn(m) - alvo
        if (fm > 0) == (fa > 0): a, fa = m, fm
        else: b = m
    return (a + b) / 2
# ---------------------------------------------------------------- gravacao (slot OBJECT + slot KEY, 30 Hz, LINEAR)
def gravar_clipe(nome, fn, dur, loop):
    n = int(round(dur * HZ)) + 1
    ts = [dur * k / (n - 1) for k in range(n)]
    poses = [fn(t) for t in ts]
    if loop: poses[-1] = poses[0]
    if nome in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[nome])
    act = bpy.data.actions.new(nome); act.use_fake_user = True
    so = act.slots.new(id_type="OBJECT", name=arm.name); sk = act.slots.new(id_type="KEY", name=key.name)
    cbo = anim_utils.action_ensure_channelbag_for_slot(act, so); cbk = anim_utils.action_ensure_channelbag_for_slot(act, sk)
    frs = [t * FPS_CENA for t in ts]
    def gravar(cb, path, idx, vals, grupo=None):
        fc = cb.fcurves.new(path, index=idx, group_name=grupo) if grupo else cb.fcurves.new(path, index=idx)
        fc.keyframe_points.add(len(vals)); co = []
        for f, v in zip(frs, vals): co += [f, v]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
        fc.update()
    for b in OSSOS:
        pb = 'pose.bones["%s"].' % b; prev = None; qs = []
        for P, _ in poses:
            q = P[b][1]
            if prev is not None and prev.dot(q) < 0: q = -q
            qs.append(q); prev = q
        for i in range(3): gravar(cbo, pb + "location", i, [P[b][0][i] for P, _ in poses], b)
        for i in range(4): gravar(cbo, pb + "rotation_quaternion", i, [q[i] for q in qs], b)
        for i in range(3): gravar(cbo, pb + "scale", i, [P[b][2][i] for P, _ in poses], b)
    for lado in "LR": gravar(cbk, 'key_blocks["fold_corrective_%s"].value' % lado, 0, [f for _, f in poses])
    act["loop"] = loop
    return {"duracao_s": round(dur, 3), "loop": loop, "amostras": n, "quadros_cena": round(dur * FPS_CENA, 2)}
def zerar():
    for pb in PB: pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.scale = (1, 1, 1)
