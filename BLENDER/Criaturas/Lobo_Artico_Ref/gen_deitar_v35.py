"""Lote de vida, bloco 1 (v35): DEITAR, DEITADO (laco) e LEVANTARDEITADO, sobre a anim_v34 (as 12 acoes antigas ficam intactas).
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
from mathutils import Matrix, Vector as V
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
POSE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "review", "v35_vida", "pose", "deitado_t8.json")))
PZ = POSE["parametros"]; ANG_PESC = POSE["pescoco_graus"]
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
def pose(af, ah, u, f, c, t, arco, resp=0.0, orelha=0.0, ponta=0.0):
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
REL = {"pose_deitado": POSE, "acoes": {}}
# ---------------- Deitar: 93 quadros (3,1 s)
JD = {"DE": (8, 34), "DD": (16, 42), "TE": (44, 66), "TD": (50, 72)}            # passo de cada pata (inicio, fim)
def deitar(q):
    af = janela(q, 6, 48) * 0.85 + janela(q, 44, 72) * 0.15; ah = janela(q, 20, 48) * 0.25 + janela(q, 44, 74) * 0.75
    u = {k: janela(q, *JD[k]) for k in PATAS}; f = dict(u)                     # pe aplaina no ar, durante o passo
    arco = {k: (0.45 if k[0] == "D" else 0.25) * math.sin(math.pi * u[k]) for k in PATAS}
    c = janela(q, 8, 48) * 0.3 + janela(q, 70, 93) * 0.7; t = janela(q, 50, 82)
    return pose(af, ah, u, f, c, t, arco)
REL["acoes"]["Deitar"] = {"quadros": 93, "erro_ik": round(gravar("Deitar", 93, deitar), 5),
                          "plantas": {k: [[0, JD[k][0]], [JD[k][1], 93]] for k in PATAS}, "marcadores_s": {"Cotovelos": 1.6, "Deitado": 2.47, "CaraNoChao": 3.1}}
# ---------------- Deitado: laco de 120 quadros (4 s)
def deitado(q):
    w = 2 * math.pi * q / 120
    return pose(1, 1, {k: 1 for k in PATAS}, {k: 1 for k in PATAS}, 1, 1, {k: 0 for k in PATAS}, resp=0.6 * math.sin(w), orelha=3.0 * max(0.0, math.sin(2 * w)) ** 4, ponta=4.0 * math.sin(w))
REL["acoes"]["Deitado"] = {"quadros": 120, "laco": True, "erro_ik": round(gravar("Deitado", 120, deitado), 5), "plantas": {k: [[0, 120]] for k in PATAS}}
# ---------------- LevantarDeitado: 72 quadros (2,4 s)
JL = {"DE": (10, 26), "DD": (16, 32), "TE": (26, 42), "TD": (30, 46)}
def levantar(q):
    c = 1 - (janela(q, 0, 14) * 0.7 + janela(q, 38, 62) * 0.3); af = 1 - (janela(q, 12, 24) * 0.25 + janela(q, 24, 46) * 0.75); ah = 1 - janela(q, 20, 54)
    u = {k: 1 - janela(q, *JL[k]) for k in PATAS}; f = dict(u)
    arco = {k: (0.4 if k[0] == "D" else 0.25) * math.sin(math.pi * u[k]) for k in PATAS}
    t = 1 - janela(q, 22, 56)
    return pose(af, ah, u, f, c, t, arco)
REL["acoes"]["LevantarDeitado"] = {"quadros": 72, "erro_ik": round(gravar("LevantarDeitado", 72, levantar), 5),
                                   "plantas": {k: [[0, JL[k][0]], [JL[k][1], 72]] for k in PATAS}, "marcadores_s": {"CabecaErguida": 0.53, "FrenteDePe": 1.4, "DePe": 2.07}}
print("V35", {k: (v["quadros"], v["erro_ik"]) for k, v in REL["acoes"].items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "vida_v35.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_DEITAR_V35_OK", flush=True)
