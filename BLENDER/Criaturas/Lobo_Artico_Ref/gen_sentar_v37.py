"""Lote de vida, bloco 2 (v37): SENTAR, SENTADO (laco) e LEVANTARSENTADO, sobre a anim_v36 (as 18 acoes ficam intactas).
Pose final = Sentado aprovado em 11/11 (pose_sentado_v37.py, cB: tronco 34 graus, garupa no chao, dianteiras retas, metatarsos
traseiros deitados para a frente, cabeca nivelada, cauda EM PE ao longo do corpo, levemente curvada).
Mesmo construtor do bloco 1 (gen_deitar_v36): a partir do Repouso q0; tronco sobe a frente e desce o quadril (s); patas por IK com alvo
fixo no mundo enquanto plantadas e arco no passo, pe aplaina no ar; pescoco/cabeca e cauda interpolados (rotacao local) entre o
Repouso q0 e a pose final.
Sentar (1,9 s): o peso vai para tras e o quadril desce enquanto as traseiras dao um passo curto para a frente e dobram; as dianteiras
se ajustam sob o peito; a cabeca nivela e a cauda sobe por ultimo. Sentado (5 s, laco): respiracao, olhar em volta, orelhas, piscada,
leve balanco da ponta da cauda. LevantarSentado (1,6 s): as traseiras recuam e empurram, o quadril sobe e a frente desce; acomoda no
Repouso q0. Uso: blender -b anim_v36/CR_LoboArtico_Anim.blend -P gen_sentar_v37.py -- <dir_saida>"""
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
POSE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "review", "v37_sentado", "pose", "sentado_cB.json"))); PZ = POSE["parametros"]
VID = json.load(open(os.path.join(SRC, "vida_v36.json"))); PALP = VID["palpebras_graus"]
ARM = M.ARM; P = M.P; sc = bpy.context.scene
for pb in P: pb.rotation_mode = "QUATERNION"
PATAS = ("DE", "DD", "TE", "TD")
def suave(x): x = max(0.0, min(1.0, x)); return x * x * x * (10 - 15 * x + 6 * x * x)
def janela(q, a, b): return suave((q - a) / max(1e-9, b - a))
def girar(osso, eixo, graus, piv=None):
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def mover(osso, d):
    pb = P[osso]; m = pb.matrix.copy(); m.translation = m.translation + d; pb.matrix = m; bpy.context.view_layer.update()
def plano_graus(vec): return -math.degrees(math.atan2(-vec.z, -vec.y))
def apontar(osso, d):
    pb = P[osso]; y = pb.matrix.col[1].xyz.normalized(); d = d.normalized(); ax = y.cross(d)
    if ax.length > 1e-8: girar(osso, ax.normalized(), math.degrees(math.acos(max(-1.0, min(1.0, y.dot(d))))))
def repouso_q0():
    ac = bpy.data.actions["Repouso"]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(0); bpy.context.view_layer.update(); ARM.animation_data.action = None
repouso_q0(); S = {pb.name: pb.matrix.copy() for pb in P}; SLOC = {pb.name: pb.rotation_quaternion.copy() for pb in P}
MCP_S = {k: P[c[2]].tail.copy() for k, c in M.PATAS.items()}
def tronco(s):
    mover("Quadril", V((0, PZ["y_quadril"] * s, -PZ["desce_quadril"] * s))); girar("Quadril", "X", -PZ["pitch_graus"] * s)
# pose final: alvos das patas, rotacoes locais de pescoco/cabeca/cauda
repouso_q0(); tronco(1.0)
FIM = {}
for k, (sup, inf, pe, dedo) in M.PATAS.items():
    sg = 1 if k[1] == "E" else -1; fr = k[0]
    phi = PZ["pe_%s_graus" % fr]; phd = PZ["dedo_%s_graus" % fr]
    phi = plano_graus(M.MCP0[k] - M.CAR0[k]) if phi is None else phi; phd = plano_graus(M.TIP0[k] - M.MCP0[k]) if phd is None else phd
    FIM[k] = {"mcp": V((M.MCP0[k].x + sg * PZ["pata_%s_x" % fr], P[sup].head.y + PZ["pata_%s_y" % fr], PZ["pata_%s_z" % fr])), "phi": phi, "phd": phd}
d1, d2 = PZ["pescoco_divisao"]; girar("Pescoco1", "X", PZ["pescoco_graus"] * d1); girar("Pescoco2", "X", PZ["pescoco_graus"] * d2)
yc = P["Cabeca"].matrix.col[1].xyz; atual = math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y))); girar("Cabeca", "X", PZ["cabeca_alvo_graus"] - atual)
eixo = (P["Quadril"].head - P["Coluna3"].head).normalized(); base = -eixo; apontar("Cauda1", base); d_ = base.copy()
for n, cv in zip(("Cauda2", "Cauda3", "Cauda4"), PZ["cauda_curva"]):
    d_ = (Matrix.Rotation(math.radians(cv), 3, V((1, 0, 0))) @ d_).normalized(); apontar(n, d_)
LFIM = {n: P[n].rotation_quaternion.copy() for n in ("Pescoco1", "Pescoco2", "Cabeca", "Cauda1", "Cauda2", "Cauda3", "Cauda4")}
def pose(s, u, f, c, t, arco, resp=0.0, orelha=0.0, ponta=0.0, olhos=0.0, olhar=0.0):
    repouso_q0(); tronco(s); err = 0.0
    if resp: girar("Coluna3", "X", -resp); girar("Pescoco1", "X", resp)    # respiracao ANTES do IK
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        w = suave(min(1.0, 6.0 * max(u[k], f[k], s)))
        if w <= 1e-6:
            for n in (sup, inf, pe, dedo): P[n].matrix = S[n]
            bpy.context.view_layer.update(); continue
        alvo = MCP_S[k].lerp(FIM[k]["mcp"], u[k]) + V((0, 0, arco[k]))
        e, x = M.ik(k, alvo, math.radians(FIM[k]["phi"] * f[k]), math.radians(FIM[k]["phd"] * f[k])); err = max(err, e)
        for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
        bpy.context.view_layer.update()
        if w < 1.0:
            ik = {n: P[n].matrix.copy() for n in (sup, inf, pe, dedo)}
            for n in (sup, inf, pe, dedo):
                rot = S[n].to_quaternion().slerp(ik[n].to_quaternion(), w).to_matrix().to_4x4(); rot.translation = P[n].matrix.translation; P[n].matrix = rot; bpy.context.view_layer.update()
    for n in ("Pescoco1", "Pescoco2", "Cabeca"):
        P[n].rotation_quaternion = SLOC[n].slerp(LFIM[n], c) if not resp or n != "Pescoco1" else P[n].rotation_quaternion
    if resp: P["Pescoco1"].rotation_quaternion = SLOC["Pescoco1"].slerp(LFIM["Pescoco1"], c) @ Quaternion((1, 0, 0), math.radians(0.0))
    for n in ("Cauda1", "Cauda2", "Cauda3", "Cauda4"): P[n].rotation_quaternion = SLOC[n].slerp(LFIM[n], t)
    bpy.context.view_layer.update()
    if olhar: girar("Pescoco2", "Z", olhar * 0.45); girar("Cabeca", "Z", olhar * 0.55)
    if olhos > 1e-6:
        for nm, g in PALP.items(): P[nm].rotation_quaternion = P[nm].rotation_quaternion @ Quaternion((1, 0, 0), math.radians(g * olhos))
        bpy.context.view_layer.update()
    if orelha: girar("Orelha_E", "Y", orelha); girar("Orelha_D", "Y", -orelha * 0.6)
    if ponta: girar("Cauda4", "Z", ponta)
    return err
def gravar(nome, n, fn):
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); ERR = 0.0; VAL = []
    for q in range(n + 1):
        ERR = max(ERR, fn(q)); VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    ARM.animation_data.action = acn; prev = {}
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
REL = {"pose_sentado": POSE, "acoes": {}}; T1 = {k: 1 for k in PATAS}; Z0 = {k: 0 for k in PATAS}
# ---------------- Sentar: 57 quadros (1,9 s)
JS = {"TE": (16, 36), "TD": (22, 42), "DE": (28, 42), "DD": (34, 48)}   # traseiras assentam com o quadril quase no fim (LOD2: jarrete nao arrasta)
def sentar(q):
    s = janela(q, 4, 46); u = {k: janela(q, *JS[k]) for k in PATAS}; f = dict(u)
    arco = {k: (0.22 if k[0] == "T" else 0.3) * math.sin(math.pi * u[k]) for k in PATAS}
    return pose(s, u, f, janela(q, 10, 50), janela(q, 2, 34), arco)          # cauda sobe ANTES de o quadril baixar (nao enterra)
REL["acoes"]["Sentar"] = {"quadros": 57, "erro_ik": round(gravar("Sentar", 57, sentar), 5), "plantas": {k: [[0, JS[k][0]], [JS[k][1], 57]] for k in PATAS}, "marcadores_s": {"Sentado": 1.53, "Cauda": 1.9}}
# ---------------- Sentado: laco 150 quadros (5 s)
def sentado(q):
    w = 2 * math.pi * q / 150
    olhar = 10.0 * math.sin(w) * (0.6 + 0.4 * math.sin(2 * w) ** 2); pisca = max(0.0, 1 - abs(q - 75) / 4.0) if 71 <= q <= 79 else 0.0
    return pose(1, T1, T1, 1, 1, Z0, resp=0.5 * math.sin(2 * w), orelha=4.0 * math.sin(3 * w) ** 6, ponta=5.0 * math.sin(w), olhos=pisca, olhar=olhar)
REL["acoes"]["Sentado"] = {"quadros": 150, "laco": True, "erro_ik": round(gravar("Sentado", 150, sentado), 5), "plantas": {k: [[0, 150]] for k in PATAS}}
# ---------------- LevantarSentado: 48 quadros (1,6 s)
JLS = {"DE": (4, 16), "DD": (8, 20), "TE": (14, 32), "TD": (18, 36)}
def levantar(q):
    s = 1 - janela(q, 8, 40); u = {k: 1 - janela(q, *JLS[k]) for k in PATAS}; f = dict(u)
    arco = {k: (0.22 if k[0] == "T" else 0.3) * math.sin(math.pi * u[k]) for k in PATAS}
    return pose(s, u, f, 1 - janela(q, 4, 34), 1 - janela(q, 24, 46), arco)  # cauda so desce depois de o quadril subir
REL["acoes"]["LevantarSentado"] = {"quadros": 48, "erro_ik": round(gravar("LevantarSentado", 48, levantar), 5), "plantas": {k: [[0, JLS[k][0]], [JLS[k][1], 48]] for k in PATAS}, "marcadores_s": {"DePe": 1.33}}
print("V37", {k: (v["quadros"], v["erro_ik"]) for k, v in REL["acoes"].items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "vida_v37.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_SENTAR_V37_OK", flush=True)
