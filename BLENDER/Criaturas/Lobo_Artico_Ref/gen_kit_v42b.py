"""Kit v42b (17/11/2026) = gen_kit_v42 com o SINAL DA MANDIBULA corrigido: no rig, girar("Mandibula","X",+g) ABRE
(convencao do gen_bloco4_v41; achado na mordida v43). Na v42 a boca do CometaPouso (4), AvalancheOnda (24) e
AvalancheCorrida (7) FECHAVA para dentro do cranio. So isso muda. Uso: ... -P gen_kit_v42b.py -- anim_v42b
Kit (v42): clipes proprios do Cometa Glacial e da Avalanche sobre a anim_v41 (as 34 acoes ficam intactas).
Documento de poderes §5.4/§5.5: Cometa = preparacao 0,25 s (agacha), voo (casca de gelo no corpo), pouso/explosao;
Avalanche = corrida teleguiada coberta de neve, termina em onda conica a frente.
Acoes novas (30 q/s):
- CometaPreparar (8 q, uma vez): agacha com as patas plantadas, peso para tras, cabeca baixa mirando, orelhas para tras.
- CometaVoo (24 q, laco): corpo esticado (dianteiras para a frente, traseiras para tras), pescoco na linha das costas,
  cauda reta para tras; leve ondulacao no laco. Sem altura no clipe: a trajetoria e do servidor.
- CometaPouso (24 q, uma vez): toque (q0) -> amortece fundo (q5) -> volta ao Repouso (q24). Marcador Impacto = 0 s.
- AvalancheCorrida (= quadros da Corrida, laco): Corrida com cabeca e pescoco baixos de investida, orelhas coladas,
  boca entreaberta e cauda reta para tras (so ossos que nao tocam o chao: as patas ficam iguais a Corrida aprovada).
- AvalancheOnda (30 q, uma vez): finca as dianteiras e empurra peito e cabeca para baixo e para a frente com a boca aberta
  (onda em q6), segura ate q12 e volta ao Repouso em q30.
Construtor igual ao gen_bloco4_v41 (Repouso q0, tronco com pivo no quadril, patas por IK com alvo fixo no mundo).
Uso: blender -b anim_v41/CR_LoboArtico_Anim.blend -P gen_kit_v42.py -- <dir_saida>"""
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
ARM = M.ARM; P = M.P; sc = bpy.context.scene
for pb in P: pb.rotation_mode = "QUATERNION"
PATAS = ("DE", "DD", "TE", "TD")
PERNAS = [n for c in M.PATAS.values() for n in c]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * x * (10 - 15 * x + 6 * x * x)
def janela(q, a, b): return suave((q - a) / max(1e-9, b - a))
def girar(osso, eixo, graus, piv=None):
    if not graus: return
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def mover(osso, d):
    pb = P[osso]; m = pb.matrix.copy(); m.translation = m.translation + d; pb.matrix = m; bpy.context.view_layer.update()
def da_acao(nome, q):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); ARM.animation_data.action = None
def repouso_q0(): da_acao("Repouso", 0)
repouso_q0(); S = {pb.name: pb.matrix.copy() for pb in P}; SLOC = {pb.name: pb.rotation_quaternion.copy() for pb in P}
MCP_S = {k: P[c[2]].tail.copy() for k, c in M.PATAS.items()}
def ang_cabeca():
    yc = P["Cabeca"].matrix.col[1].xyz; return math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))
CAB0 = ang_cabeca()
# ---- poses (girar "X" no espaco do rig: + = frente desce / perna vai para tras / cauda sobe; orelha - = para tras)
POSES = {
    "preparar": {"desce_quadril": 0.95, "y_quadril": 0.35, "pitch": 5.0, "pescoco": (8.0, 6.0), "cabeca": CAB0 + 4.0, "boca": 0.0,
                 "orelhas": -28.0, "cauda": (8.0, 6.0, 0.0)},
    "voo": {"desce_quadril": 0.0, "y_quadril": 0.0, "pitch": -3.0, "pescoco": (16.0, 10.0), "cabeca": CAB0 + 2.0, "boca": 0.0,
            "orelhas": -34.0, "cauda": (34.0, 14.0, 8.0),
            "pernas": {"Umero_E": -72, "Antebraco_E": -14, "Metacarpo_E": 30, "Dedos_E": 18, "Umero_D": -68, "Antebraco_D": -16, "Metacarpo_D": 30, "Dedos_D": 18,
                       "Coxa_E": 50, "Tibia_E": 28, "Metatarso_E": 18, "DedosPe_E": 12, "Coxa_D": 54, "Tibia_D": 26, "Metatarso_D": 18, "DedosPe_D": 12}},
    "pouso": {"desce_quadril": 1.15, "y_quadril": 0.1, "pitch": 7.0, "pescoco": (10.0, 6.0), "cabeca": CAB0 + 6.0, "boca": 4.0,
              "orelhas": -24.0, "cauda": (12.0, 6.0, 0.0)},
    "onda": {"desce_quadril": 0.55, "y_quadril": -0.35, "pitch": 9.0, "pescoco": (16.0, 10.0), "cabeca": CAB0 + 10.0, "boca": 24.0,
             "orelhas": -36.0, "cauda": (22.0, 8.0, 0.0)},
}
def corpo(pz, s, c):
    mover("Quadril", V((0, pz["y_quadril"] * s, -pz["desce_quadril"] * s))); girar("Quadril", "X", pz["pitch"] * s)
    girar("Pescoco1", "X", pz["pescoco"][0] * c); girar("Pescoco2", "X", pz["pescoco"][1] * c)
    girar("Cabeca", "X", (pz["cabeca"] - ang_cabeca()) * c)
    girar("Mandibula", "X", pz["boca"] * c)                      # v42b: + abre
    girar("Orelha_E", "X", pz["orelhas"] * c); girar("Orelha_D", "X", pz["orelhas"] * c)
    for n, g in zip(("Cauda1", "Cauda2", "Cauda3"), pz["cauda"]): girar(n, "X", g * c)
def patas_ik(s):
    """patas plantadas no apoio do Repouso; perto do Repouso mistura FK->IK (emenda exata no q do Repouso)"""
    w = suave(min(1.0, 6.0 * s)); err = 0.0
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        if w <= 1e-6:
            for n in (sup, inf, pe, dedo): P[n].matrix = S[n]
            bpy.context.view_layer.update(); continue
        fk = {n: P[n].rotation_quaternion.copy() for n in (sup, inf, pe, dedo)}
        e, x = M.ik(k, MCP_S[k], 0.0, 0.0); err = max(err, e)
        for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
        bpy.context.view_layer.update()
        if w < 1.0:
            for n in (sup, inf, pe, dedo): P[n].rotation_quaternion = fk[n].slerp(P[n].rotation_quaternion.copy(), w); bpy.context.view_layer.update()
    return err
def pose_chao(nome, s, c, extra=None):
    repouso_q0(); corpo(POSES[nome], s, c); e = patas_ik(s)
    if extra: extra()
    return e
def pose_voo(q, n):
    repouso_q0(); pz = POSES["voo"]; corpo(pz, 1.0, 1.0); x = math.sin(2 * math.pi * q / n)
    for osso, g in pz["pernas"].items():
        osc = 3.0 * x * (1 if osso[-1] == "E" else -1) * (1 if osso.startswith(("Umero", "Coxa")) else 0.5)
        girar(osso, "X", g + osc)
    girar("Coluna2", "X", 1.2 * x); girar("Cauda2", "Z", 4.0 * math.sin(2 * math.pi * q / n + 0.8)); girar("Cauda3", "Z", 5.0 * math.sin(2 * math.pi * q / n + 1.6))
    return 0.0
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
REL = {"poses": {k: {kk: vv for kk, vv in v.items()} for k, v in POSES.items()}, "cabeca_repouso_graus": round(CAB0, 2), "acoes": {}}
def registrar(nome, n, fn, laco=False, marc=None, plantas=True):
    REL["acoes"][nome] = {"quadros": n, "erro_ik": round(gravar(nome, n, fn), 5), "plantas": ({k: [[0, n]] for k in PATAS} if plantas else {})}
    if laco: REL["acoes"][nome]["laco"] = True
    if marc: REL["acoes"][nome]["marcadores_s"] = marc
# ================= COMETA =================
registrar("CometaPreparar", 8, lambda q: pose_chao("preparar", janela(q, 0, 6), janela(q, 0, 5)), marc={"Salto": 0.27})
registrar("CometaVoo", 24, lambda q: pose_voo(q, 24), laco=True, plantas=False)
def pouso(q):
    s = (0.55 + 0.45 * janela(q, 0, 5)) * (1 - janela(q, 7, 24)); c = 1 - janela(q, 4, 22)
    return pose_chao("pouso", s, c)
registrar("CometaPouso", 24, pouso, marc={"Impacto": 0.0, "Repouso": 0.8})
# ================= AVALANCHE =================
NCOR = int(bpy.data.actions["Corrida"].frame_range[1])
AV = {"pescoco": (12.0, 8.0), "cabeca": 6.0, "boca": 7.0, "orelhas": -36.0, "cauda": (26.0, 10.0, 4.0)}
def av_corrida(q):
    da_acao("Corrida", q)
    girar("Pescoco1", "X", AV["pescoco"][0]); girar("Pescoco2", "X", AV["pescoco"][1]); girar("Cabeca", "X", AV["cabeca"])
    girar("Mandibula", "X", AV["boca"]);                          # v42b: + abre
    girar("Orelha_E", "X", AV["orelhas"]); girar("Orelha_D", "X", AV["orelhas"])
    for n, g in zip(("Cauda1", "Cauda2", "Cauda3"), AV["cauda"]): girar(n, "X", g)
    return 0.0
REL["avalanche_corrida_camadas"] = AV
registrar("AvalancheCorrida", NCOR, av_corrida, laco=True, plantas=False)
def onda(q):
    s = janela(q, 0, 6) * (1 - janela(q, 12, 30)); c = janela(q, 0, 5) * (1 - janela(q, 13, 28))
    return pose_chao("onda", s, c)
registrar("AvalancheOnda", 30, onda, marc={"Onda": 0.2, "Repouso": 1.0})
print("V42", {k: (v["quadros"], v["erro_ik"]) for k, v in REL["acoes"].items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "kit_v42.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_KIT_V42B_OK", flush=True)
