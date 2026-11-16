"""v36 (pedido 11/11: antes de dormir ele deve descansar, deitado porem de cabeca erguida): DEITAR (termina de cabeca erguida),
DESCANSO (laco, deitado de cabeca erguida, olhando em volta), ADORMECER (cabeca desce entre as patas e os olhos fecham), DORMINDO (laco,
olhos fechados, respiracao mais lenta), DESPERTAR (abre os olhos e ergue a cabeca, volta ao Descanso q0) e LEVANTARDEITADO (a partir do
Descanso). Substitui o Deitado da v35 (= Dormindo). Mesmo construtor da v35 (copia adaptada), sobre a anim_v34.
Uso: blender -b anim_v34/CR_LoboArtico_Anim.blend -P gen_deitar_v36.py -- <dir_saida>   (env C_DESC_V36 = altura da cabeca no descanso)
-------------------------------------------------------------------------------------------------------------------------------
v35: Lote de vida, bloco 1: DEITAR, DEITADO (laco) e LEVANTARDEITADO, sobre a anim_v34 (as 12 acoes antigas ficam intactas).
Pose final = Deitado (esfinge) aprovado em 11/11 (pose_deitado_v35.py, t8). Pose inicial/final das transicoes = Repouso q0 EXATO.
Construtor parametrico por quadro (a partir do Repouso q0): tronco desce (frente af, tras ah, pivo no quadril), patas por IK (marcha_v21.ik)
com alvo fixo no mundo enquanto plantadas e arco quando dao o passo, pe/dedos aplainam (f), pescoco/cabeca (c), cauda (t).
Deitar (3,1 s, em fases como no lobo real/Ancestral): dianteiras avancam em passos alternados enquanto a FRENTE desce ate os cotovelos;
depois tronco e quadril baixam e as traseiras se recolhem; por ultimo a cabeca desce entre as patas.
Levantar (2,4 s): ergue a cabeca, recolhe as dianteiras para baixo dos ombros e levanta a frente; depois as traseiras empurram e o
quadril sobe; acomoda no Repouso q0. Deitado (4 s, laco): respiracao discreta no peito e leve movimento de orelhas e ponta da cauda.
Plantas (janelas em que cada pata nao se move no mundo) gravadas no JSON para a auditoria de deslize.
Uso: blender -b anim_v34/CR_LoboArtico_Anim.blend -P gen_deitar_v35.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V, Quaternion
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
POSE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "review", "v35_vida", "pose", "deitado_t8.json")))
PZ = POSE["parametros"]; ANG_PESC = POSE["pescoco_graus"]
PAR_C_DESC = float(os.environ.get("C_DESC_V36", "0.12")); PAR_OLHO_FENDA = 0.006
ARM = M.ARM; P = M.P; sc = bpy.context.scene; FPS = 30
for pb in P: pb.rotation_mode = "QUATERNION"
def suave(x): x = max(0.0, min(1.0, x)); return x * x * x * (10 - 15 * x + 6 * x * x)
def janela(q, a, b): return suave((q - a) / max(1e-9, b - a))
def girar(osso, eixo, graus, piv=None):
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def mover(osso, d):
    pb = P[osso]; m = pb.matrix.copy(); m.translation = m.translation + d; pb.matrix = m; bpy.context.view_layer.update()
def plano_graus(vec): return -math.degrees(math.atan2(-vec.z, -vec.y))
def repouso_q0():
    ac = bpy.data.actions["Repouso"]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(0); bpy.context.view_layer.update(); ARM.animation_data.action = None
repouso_q0(); S = {pb.name: pb.matrix.copy() for pb in P}
MCP_S = {k: P[c[2]].tail.copy() for k, c in M.PATAS.items()}
qh = P["Quadril"].head.copy(); c3 = P["Coluna3"].head.copy(); LC = qh.y - c3.y
def tronco(af, ah):
    dq = PZ["desce_quadril"] * ah; dp = PZ["desce_peito"] * af
    pitch = math.degrees(math.atan2(dp - dq, LC)); mover("Quadril", V((0, 0, -dq))); girar("Quadril", "X", pitch)
# alvos finais das patas (no mundo), com o tronco todo baixado
repouso_q0(); tronco(1.0, 1.0)
FIM = {}
for k, (sup, inf, pe, dedo) in M.PATAS.items():
    sg = 1 if k[1] == "E" else -1; fr = k[0]
    FIM[k] = {"mcp": V((M.MCP0[k].x + sg * PZ["pata_%s_x" % fr], P[sup].head.y + PZ["pata_%s_y" % fr], PZ["pata_%s_z" % fr])),
              "phi": plano_graus(M.MCP0[k] - M.CAR0[k]), "phd": plano_graus(M.TIP0[k] - M.TIP0[k] + (M.TIP0[k] - M.MCP0[k]))}
def pose(af, ah, u, f, c, t, arco, resp=0.0, orelha=0.0, ponta=0.0, olhos=0.0, olhar=0.0):
    """u[k], f[k]: progresso do passo e do aplainar de cada pata; arco[k]: altura do arco atual"""
    repouso_q0(); tronco(af, ah); err = 0.0
    if resp: girar("Coluna3", "X", -resp); girar("Pescoco1", "X", resp)    # respiracao ANTES do IK (o peito move os ombros)
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        w = suave(min(1.0, 6.0 * max(u[k], f[k], af, ah)))             # pata presa pelo IK assim que o tronco ou ela se mexe
        if w <= 1e-6:
            for n in (sup, inf, pe, dedo): P[n].matrix = S[n]
            bpy.context.view_layer.update(); continue
        alvo = MCP_S[k].lerp(FIM[k]["mcp"], u[k]) + V((0, 0, arco[k]))
        e, x = M.ik(k, alvo, math.radians(FIM[k]["phi"] * f[k]), math.radians(FIM[k]["phd"] * f[k])); err = max(err, e)
        if e > 0.01 and os.environ.get("DBG_V35"): print("DBG_IK", k, round(e, 3), "af", round(af, 2), "ah", round(ah, 2), "u", round(u[k], 2), "f", round(f[k], 2), flush=True)
        for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
        bpy.context.view_layer.update()
        if w < 1.0:
            ik = {n: P[n].matrix.copy() for n in (sup, inf, pe, dedo)}
            for n in (sup, inf, pe, dedo):
                rot = S[n].to_quaternion().slerp(ik[n].to_quaternion(), w).to_matrix().to_4x4(); rot.translation = P[n].matrix.translation; P[n].matrix = rot; bpy.context.view_layer.update()
    d1, d2 = PZ["pescoco_divisao"]
    if c > 1e-6:
        girar("Pescoco1", "X", ANG_PESC * c * d1); girar("Pescoco2", "X", ANG_PESC * c * d2)
        yc = P["Cabeca"].matrix.col[1].xyz; atual = math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))
        yr = S["Cabeca"].col[1].xyz; rep = math.degrees(math.atan2(-yr.z, math.hypot(yr.x, yr.y)))
        girar("Cabeca", "X", (rep + (PZ["cabeca_alvo_graus"] - rep) * c) - atual)
    t = max(t, ah)                                                     # cauda erguida enquanto o quadril esta baixo (nao enterra)
    if t > 1e-6:
        for n, g in zip(("Cauda1", "Cauda2", "Cauda3", "Cauda4"), PZ["cauda"]): girar(n, "X", g * t)
        girar("Cauda1", "Z", PZ["cauda_lado"] * t)
    if olhar: girar("Pescoco2", "Z", olhar * 0.45); girar("Cabeca", "Z", olhar * 0.55)
    if olhos > 1e-6:
        for nm, g in PALP.items():
            P[nm].rotation_quaternion = P[nm].rotation_quaternion @ Quaternion((1, 0, 0), math.radians(g * olhos))
        bpy.context.view_layer.update()
    if orelha: girar("Orelha_E", "Y", orelha); girar("Orelha_D", "Y", -orelha * 0.6)
    if ponta: girar("Cauda4", "Z", ponta)
    return err
def gravar(nome, n, fn):
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); ERR = 0.0; VAL = []
    for q in range(n + 1):
        ERR = max(ERR, fn(q)); VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    ARM.animation_data.action = acn
    prev = {}
    for q, vals in enumerate(VAL):
        for pb in P:
            rq, lc = vals[pb.name]
            if pb.name in prev and rq.dot(prev[pb.name]) < 0: rq = -rq
            prev[pb.name] = rq; pb.rotation_quaternion = rq; pb.location = lc
            pb.keyframe_insert("rotation_quaternion", frame=q, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=q, group=pb.name)
    acn.use_fake_user = True; acn.frame_range = (0, n); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    return ERR
PATAS = ("DE", "DD", "TE", "TD")
# ---------------- palpebras: angulo (X local) que fecha cada olho, medido na malha LOW_Cabeca no Repouso q0
CAB = bpy.data.objects["LOW_Cabeca"]; GI = {g.name: g.index for g in CAB.vertex_groups}
def centro(nome):
    dg = bpy.context.evaluated_depsgraph_get(); m = CAB.evaluated_get(dg).to_mesh(); gi = GI[nome]; s_ = V(); w = 0
    for v, vb in zip(CAB.data.vertices, m.vertices):
        for g in v.groups:
            if g.group == gi and g.weight > 0.5: s_ += CAB.matrix_world @ vb.co; w += 1
    CAB.evaluated_get(dg).to_mesh_clear(); return s_ / max(1, w)
PALP = {}
for lado in "ED":
    sup, inf = "Palpebra_Sup_" + lado, "Palpebra_Inf_" + lado
    def fenda(a_):
        repouso_q0()
        P[sup].rotation_quaternion = P[sup].rotation_quaternion @ Quaternion((1, 0, 0), math.radians(-a_))
        P[inf].rotation_quaternion = P[inf].rotation_quaternion @ Quaternion((1, 0, 0), math.radians(a_ * 0.85))
        bpy.context.view_layer.update(); return centro(sup).z - centro(inf).z
    lo, hi = 0.0, 40.0
    for _ in range(16):
        md = 0.5 * (lo + hi)
        if fenda(md) > PAR_OLHO_FENDA: lo = md
        else: hi = md
    PALP[sup] = -hi; PALP[inf] = hi * 0.85
print("V36 palpebras", {k: round(v, 1) for k, v in PALP.items()}, flush=True)
C_DESC = PAR_C_DESC                                                     # cabeca erguida no deitado (0 = cabeca do Repouso, 1 = dormindo)
REL = {"pose_deitado": POSE, "palpebras_graus": PALP, "c_descanso": C_DESC, "acoes": {}}
TODAS1 = {k: 1 for k in PATAS}; ZERO = {k: 0 for k in PATAS}
# ---------------- Deitar: 80 quadros (2,67 s), termina de cabeca erguida (= Descanso q0)
JD = {"DE": (8, 34), "DD": (16, 42), "TE": (44, 66), "TD": (50, 72)}
def deitar(q):
    af = janela(q, 6, 48) * 0.85 + janela(q, 44, 72) * 0.15; ah = janela(q, 20, 48) * 0.25 + janela(q, 44, 74) * 0.75
    u = {k: janela(q, *JD[k]) for k in PATAS}; f = dict(u)
    arco = {k: (0.45 if k[0] == "D" else 0.25) * math.sin(math.pi * u[k]) for k in PATAS}
    c = janela(q, 8, 40) * 0.3 - janela(q, 46, 76) * (0.3 - C_DESC); t = janela(q, 50, 78)
    return pose(af, ah, u, f, c, t, arco)
REL["acoes"]["Deitar"] = {"quadros": 80, "erro_ik": round(gravar("Deitar", 80, deitar), 5), "plantas": {k: [[0, JD[k][0]], [JD[k][1], 80]] for k in PATAS}, "marcadores_s": {"Cotovelos": 1.6, "Deitado": 2.47}}
# ---------------- Descanso: laco 150 quadros (5 s): cabeca erguida olhando em volta, respiracao, orelhas, uma piscada
def descanso(q):
    w = 2 * math.pi * q / 150
    olhar = 9.0 * math.sin(w) * (0.6 + 0.4 * math.sin(2 * w) ** 2); pisca = max(0.0, 1 - abs(q - 100) / 4.0) if 96 <= q <= 104 else 0.0
    return pose(1, 1, TODAS1, TODAS1, C_DESC, 1, ZERO, resp=0.6 * math.sin(2 * w), orelha=4.0 * math.sin(3 * w) ** 6, ponta=4.0 * math.sin(w), olhos=pisca, olhar=olhar)
REL["acoes"]["Descanso"] = {"quadros": 150, "laco": True, "erro_ik": round(gravar("Descanso", 150, descanso), 5), "plantas": {k: [[0, 150]] for k in PATAS}}
# ---------------- Adormecer: 66 quadros (2,2 s): cabeca desce entre as patas, olhos fecham no fim
def adormecer(q):
    c = C_DESC + (1 - C_DESC) * janela(q, 4, 52); olhos = janela(q, 34, 64)
    return pose(1, 1, TODAS1, TODAS1, c, 1, ZERO, olhos=olhos)
REL["acoes"]["Adormecer"] = {"quadros": 66, "erro_ik": round(gravar("Adormecer", 66, adormecer), 5), "plantas": {k: [[0, 66]] for k in PATAS}, "marcadores_s": {"CaraNoChao": 1.73, "OlhosFechados": 2.13}}
# ---------------- Dormindo: laco 180 quadros (6 s): olhos fechados, respiracao lenta e mais funda, orelha rara
def dormindo(q):
    w = 2 * math.pi * q / 180
    return pose(1, 1, TODAS1, TODAS1, 1, 1, ZERO, resp=0.9 * math.sin(2 * w), orelha=3.0 * max(0.0, math.sin(w)) ** 12, ponta=2.0 * math.sin(w), olhos=1.0)
REL["acoes"]["Dormindo"] = {"quadros": 180, "laco": True, "erro_ik": round(gravar("Dormindo", 180, dormindo), 5), "plantas": {k: [[0, 180]] for k in PATAS}}
# ---------------- Despertar: 45 quadros (1,5 s): abre os olhos e ergue a cabeca ate o Descanso q0
def despertar(q):
    olhos = 1 - janela(q, 0, 12); c = 1 - (1 - C_DESC) * janela(q, 8, 42)
    return pose(1, 1, TODAS1, TODAS1, c, 1, ZERO, olhos=olhos, orelha=5.0 * math.sin(math.pi * janela(q, 6, 20)))
REL["acoes"]["Despertar"] = {"quadros": 45, "erro_ik": round(gravar("Despertar", 45, despertar), 5), "plantas": {k: [[0, 45]] for k in PATAS}, "marcadores_s": {"OlhosAbertos": 0.4, "CabecaErguida": 1.4}}
# ---------------- LevantarDeitado: 66 quadros (2,2 s) a partir do Descanso (cabeca ja erguida)
JL = {"DE": (6, 22), "DD": (12, 28), "TE": (22, 38), "TD": (26, 42)}
def levantar(q):
    c = C_DESC * (1 - janela(q, 30, 56)); af = 1 - (janela(q, 8, 20) * 0.25 + janela(q, 20, 42) * 0.75); ah = 1 - janela(q, 16, 50)
    u = {k: 1 - janela(q, *JL[k]) for k in PATAS}; f = dict(u)
    arco = {k: (0.4 if k[0] == "D" else 0.25) * math.sin(math.pi * u[k]) for k in PATAS}
    t = 1 - janela(q, 18, 52)
    return pose(af, ah, u, f, c, t, arco)
REL["acoes"]["LevantarDeitado"] = {"quadros": 66, "erro_ik": round(gravar("LevantarDeitado", 66, levantar), 5), "plantas": {k: [[0, JL[k][0]], [JL[k][1], 66]] for k in PATAS}, "marcadores_s": {"FrenteDePe": 1.4, "DePe": 1.87}}
for _a in [x for x in bpy.data.actions if x.name == "Deitado"]: bpy.data.actions.remove(_a)
print("V36", {k: (v["quadros"], v["erro_ik"]) for k, v in REL["acoes"].items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "vida_v36.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_DEITAR_V36_OK", flush=True)
