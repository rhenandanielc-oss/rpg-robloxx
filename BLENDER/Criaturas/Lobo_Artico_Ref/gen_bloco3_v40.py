"""Lote de vida, bloco 3 (v40): FAREJAR, COMER e BEBER sobre a anim_v39 (as 21 acoes ficam intactas). Cada comportamento tem
entrada (verbo), laco (gerundio) e saida (Parar...): Farejar/Farejando/PararFarejar, Comer/Comendo/PararComer, Beber/Bebendo/PararBeber.
Poses finais = poses aprovadas em 12/11 (review/v40_bloco3/pose/<pose>.json, pose_bloco3_v40.py): mesmo construtor (Repouso q0; frente do
tronco desce com pivo no quadril; patas por IK com alvo fixo no mundo; pescoco/cabeca/boca/orelhas interpolados em rotacao local).
Lacos: Farejando 4 s (varre o chao de um lado a outro, fungadas rapidas com o focinho subindo, orelhas); Comendo 5 s (mastiga 3x/s,
3 puxoes do pescoco para tras/cima); Bebendo 3 s (lambidas 3x/s: boca abre e fecha, focinho sobe de leve). Os desvios do laco valem 0 no
q0 (emenda exata com a entrada e a saida) e so levantam o focinho (nao enterram).
Uso: blender -b anim_v39/CR_LoboArtico_Anim.blend -P gen_bloco3_v40.py -- <dir_saida>"""
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
DPOSE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review", "v40_bloco3", "pose")
POSES = {p: json.load(open(os.path.join(DPOSE, p + ".json"))) for p in ("farejar", "comer", "beber")}
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
def repouso_q0():
    ac = bpy.data.actions["Repouso"]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(0); bpy.context.view_layer.update(); ARM.animation_data.action = None
repouso_q0(); S = {pb.name: pb.matrix.copy() for pb in P}; SLOC = {pb.name: pb.rotation_quaternion.copy() for pb in P}
MCP_S = {k: P[c[2]].tail.copy() for k, c in M.PATAS.items()}
LOCAIS = ("Pescoco1", "Pescoco2", "Cabeca", "Mandibula", "Orelha_E", "Orelha_D")
def ang_cabeca():
    yc = P["Cabeca"].matrix.col[1].xyz; return math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))
def tronco(pz, s):
    mover("Quadril", V((0, pz["y_quadril"] * s, -pz["desce_quadril"] * s))); girar("Quadril", "X", pz["pitch_graus"] * s)
ALVO = {}; LFIM = {}
for nome, R in POSES.items():
    pz = R["parametros"]; repouso_q0(); tronco(pz, 1.0)
    ALVO[nome] = {k: MCP_S[k] + V(((1 if k[1] == "E" else -1) * pz["pata_%s_x" % k[0]], pz["pata_%s_y" % k[0]], 0)) for k in PATAS}
    d1, d2 = pz["pescoco_divisao"]; girar("Pescoco1", "X", R["pescoco_graus"] * d1); girar("Pescoco2", "X", R["pescoco_graus"] * d2)
    girar("Cabeca", "X", pz["cabeca_graus"] - ang_cabeca())
    if pz["boca_graus"]: girar("Mandibula", "X", pz["boca_graus"])
    if pz["orelhas_graus"]: girar("Orelha_E", "X", -pz["orelhas_graus"]); girar("Orelha_D", "X", -pz["orelhas_graus"])
    LFIM[nome] = {n: P[n].rotation_quaternion.copy() for n in LOCAIS}
def pose(nome, s, u, c, arco, olhar=0.0, ergue=0.0, boca=0.0, puxa=0.0, orelha=0.0):
    """s: tronco (0 Repouso, 1 pose); u: patas (0 no lugar do Repouso, 1 no alvo da pose); c: pescoco/cabeca/boca/orelhas.
    Desvios do laco: olhar (graus, Z), ergue (graus, focinho sobe), boca (graus, fecha), puxa (graus, pescoco sobe/recua), orelha."""
    pz = POSES[nome]["parametros"]; repouso_q0(); tronco(pz, s); err = 0.0
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        w = suave(min(1.0, 6.0 * max(u[k], s)))
        if w <= 1e-6:
            for n in (sup, inf, pe, dedo): P[n].matrix = S[n]
            bpy.context.view_layer.update(); continue
        alvo = MCP_S[k].lerp(ALVO[nome][k], u[k]) + V((0, 0, arco[k]))
        e, x = M.ik(k, alvo, 0.0, 0.0); err = max(err, e)
        for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
        bpy.context.view_layer.update()
        if w < 1.0:
            ik = {n: P[n].matrix.copy() for n in (sup, inf, pe, dedo)}
            for n in (sup, inf, pe, dedo):
                rot = S[n].to_quaternion().slerp(ik[n].to_quaternion(), w).to_matrix().to_4x4(); rot.translation = P[n].matrix.translation; P[n].matrix = rot; bpy.context.view_layer.update()
    for n in LOCAIS: P[n].rotation_quaternion = SLOC[n].slerp(LFIM[nome][n], c)
    bpy.context.view_layer.update()
    if puxa: girar("Pescoco1", "X", -puxa * 0.6); girar("Pescoco2", "X", -puxa * 0.4)
    if olhar: girar("Pescoco2", "Z", olhar * 0.5); girar("Cabeca", "Z", olhar * 0.5)
    if ergue: girar("Cabeca", "X", -ergue)
    if boca: girar("Mandibula", "X", -boca)
    if orelha: girar("Orelha_E", "Y", orelha); girar("Orelha_D", "Y", -orelha * 0.7)
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
REL = {"poses": {k: {"parametros": v["parametros"], "pescoco_graus": v["pescoco_graus"]} for k, v in POSES.items()}, "acoes": {}}
T1 = {k: 1 for k in PATAS}; Z0 = {k: 0 for k in PATAS}
def onda(q, n, ciclos): return 0.5 - 0.5 * math.cos(2 * math.pi * ciclos * q / n)      # 0 no q0, periodica no laco
def registrar(nome, n, fn, plantas, laco=False, marc=None):
    REL["acoes"][nome] = {"quadros": n, "erro_ik": round(gravar(nome, n, fn), 5), "plantas": plantas}
    if laco: REL["acoes"][nome]["laco"] = True
    if marc: REL["acoes"][nome]["marcadores_s"] = marc
def todas(n): return {k: [[0, n]] for k in PATAS}
# ================= FAREJAR (patas no lugar) =================
registrar("Farejar", 30, lambda q: pose("farejar", janela(q, 0, 26), Z0, janela(q, 2, 30), Z0), todas(30), marc={"FocinhoNoChao": 1.0})
def farejando(q):
    n = 120; w = 2 * math.pi * q / n
    olhar = 14.0 * math.sin(w)                                                       # varre o chao de um lado a outro
    fung = 1.6 * onda(q, n, 24) * (0.4 + 0.6 * onda(q, n, 2))                        # fungadas (5 q), mais fortes no meio de cada varrida
    return pose("farejar", 1, Z0, 1, Z0, olhar=olhar, ergue=fung, orelha=4.0 * math.sin(2 * w))
registrar("Farejando", 120, farejando, todas(120), laco=True)
registrar("PararFarejar", 30, lambda q: pose("farejar", 1 - janela(q, 4, 30), Z0, 1 - janela(q, 0, 26), Z0), todas(30), marc={"CabecaErguida": 0.9})
# ================= COMER (dianteiras abrem um passo) =================
JC = {"DE": (8, 22), "DD": (14, 28)}
def comer(q):
    u = {k: (janela(q, *JC[k]) if k in JC else 0.0) for k in PATAS}
    arco = {k: 0.3 * math.sin(math.pi * u[k]) for k in PATAS}
    return pose("comer", janela(q, 4, 36), u, janela(q, 10, 44), arco)
registrar("Comer", 45, comer, {"DE": [[0, 8], [22, 45]], "DD": [[0, 14], [28, 45]], "TE": [[0, 45]], "TD": [[0, 45]]}, marc={"BocaNoAlimento": 1.47})
def comendo(q):
    n = 150
    mastiga = 11.0 * onda(q, n, 15)                                                   # 3 mastigadas/s (fecha a boca)
    puxa = 7.0 * onda(q, n, 3) ** 3                                                  # 3 puxoes: pescoco sobe/recua
    return pose("comer", 1, T1, 1, Z0, boca=mastiga, puxa=puxa, ergue=2.0 * onda(q, n, 3) ** 3, orelha=3.0 * math.sin(2 * math.pi * q / n))
registrar("Comendo", 150, comendo, todas(150), laco=True)
JCs = {"DE": (18, 32), "DD": (24, 38)}
def parar_comer(q):
    u = {k: (1 - janela(q, *JCs[k]) if k in JCs else 1.0) for k in PATAS}
    arco = {k: 0.3 * math.sin(math.pi * u[k]) for k in PATAS}
    return pose("comer", 1 - janela(q, 6, 40), u, 1 - janela(q, 0, 30), arco)
registrar("PararComer", 45, parar_comer, {"DE": [[0, 18], [32, 45]], "DD": [[0, 24], [38, 45]], "TE": [[0, 45]], "TD": [[0, 45]]}, marc={"DePe": 1.3})
# ================= BEBER (dianteiras abrem e se agacham) =================
JB = {"DE": (8, 24), "DD": (16, 32)}
def beber(q):
    u = {k: (janela(q, *JB[k]) if k in JB else 0.0) for k in PATAS}
    arco = {k: 0.3 * math.sin(math.pi * u[k]) for k in PATAS}
    return pose("beber", janela(q, 6, 46), u, janela(q, 12, 54), arco)
registrar("Beber", 54, beber, {"DE": [[0, 8], [24, 54]], "DD": [[0, 16], [32, 54]], "TE": [[0, 54]], "TD": [[0, 54]]}, marc={"FocinhoNaAgua": 1.8})
def bebendo(q):
    n = 90
    lambe = onda(q, n, 9)                                                             # 3 lambidas/s
    return pose("beber", 1, T1, 1, Z0, boca=7.0 * lambe, ergue=2.2 * lambe, orelha=2.5 * math.sin(2 * math.pi * q / n))
registrar("Bebendo", 90, bebendo, todas(90), laco=True)
JBs = {"DE": (22, 38), "DD": (28, 44)}
def parar_beber(q):
    u = {k: (1 - janela(q, *JBs[k]) if k in JBs else 1.0) for k in PATAS}
    arco = {k: 0.3 * math.sin(math.pi * u[k]) for k in PATAS}
    return pose("beber", 1 - janela(q, 8, 48), u, 1 - janela(q, 0, 34), arco)
registrar("PararBeber", 54, parar_beber, {"DE": [[0, 22], [38, 54]], "DD": [[0, 28], [44, 54]], "TE": [[0, 54]], "TD": [[0, 54]]}, marc={"DePe": 1.6})
print("V40", {k: (v["quadros"], v["erro_ik"]) for k, v in REL["acoes"].items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "vida_v40.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_BLOCO3_V40_OK", flush=True)
