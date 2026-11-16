"""Lote de vida, bloco 4 (v41): UIVAR (Uivar / Uivando laco / PararUivar) e SACUDIR (acao unica Repouso -> Repouso) sobre a anim_v40
(as 30 acoes ficam intactas). Poses aprovadas em 12/11 (review/v41_bloco4/pose/<pose>.json, pose_bloco4_v41.py).
Mesmo construtor do bloco 3 (gen_bloco3_v40): Repouso q0; tronco baixa/gira com pivo no quadril; patas por IK com alvo fixo no mundo
(as patas NAO saem do lugar nestes clipes: o Sacudir usa a base do Repouso, sem o passo de abrir as patas da pose estatica); pescoco,
cabeca, boca, orelhas e Cauda1 interpolados em rotacao local.
Uivando (5 s, laco): uma nota longa (q0-110: boca abre mais em 'O' e o focinho sobe de leve) e a inspiracao (q110-150: boca quase fecha,
cabeca desce um pouco, peito enche). Sacudir (2 s): prepara (agacha, q0-12), torcao em onda alternando os lados ~4,5x/s com a cabeca
na frente e o peito, o quadril e a cauda atrasados (q10-50, envelope sobe e desce), assenta no Repouso (q46-60).
Uso: blender -b anim_v40/CR_LoboArtico_Anim.blend -P gen_bloco4_v41.py -- <dir_saida>"""
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
DPOSE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review", "v41_bloco4", "pose")
POSES = {p: json.load(open(os.path.join(DPOSE, p + ".json"))) for p in ("uivar", "sacudir")}
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
LOCAIS = ("Pescoco1", "Pescoco2", "Cabeca", "Mandibula", "Orelha_E", "Orelha_D", "Cauda1")
def eixo_osso(n): return (P[n].tail - P[n].head).normalized()
def ang_cabeca():
    yc = P["Cabeca"].matrix.col[1].xyz; return math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))
def tronco(pz, s):
    mover("Quadril", V((0, pz["y_quadril"] * s, -pz["desce_quadril"] * s))); girar("Quadril", "X", pz["pitch_graus"] * s)
LFIM = {}
for nome, R in POSES.items():
    pz = R["parametros"]; repouso_q0(); tronco(pz, 1.0)
    d1, d2 = pz["pescoco_divisao"]; girar("Pescoco1", "X", pz["pescoco_graus"] * d1); girar("Pescoco2", "X", pz["pescoco_graus"] * d2)
    girar("Cabeca", "X", pz["cabeca_graus"] - ang_cabeca())
    if pz["boca_graus"]: girar("Mandibula", "X", pz["boca_graus"])
    if pz["orelhas_graus"]: girar("Orelha_E", "X", -pz["orelhas_graus"]); girar("Orelha_D", "X", -pz["orelhas_graus"])
    if pz["cauda_ergue"]: girar("Cauda1", "X", pz["cauda_ergue"])
    LFIM[nome] = {n: P[n].rotation_quaternion.copy() for n in LOCAIS}       # (rolos, rolo da cabeca e cauda para o lado sao dinamicos)
def pose(nome, s, c, ergue=0.0, boca=0.0, peito=0.0, torcao=None, orelha=0.0):
    """s: tronco; c: pescoco/cabeca/boca/orelhas/Cauda1. ergue: focinho sobe (graus); boca: >0 fecha; peito: inspiracao (graus).
    torcao: {'Quadril','Coluna2','Coluna3','Cabeca','Cauda'} -> fator assinado (-1..1) dos rolos da pose sacudir."""
    pz = POSES[nome]["parametros"]; repouso_q0(); tronco(pz, s); err = 0.0
    if peito: girar("Coluna3", "X", -peito); girar("Pescoco1", "X", peito)
    if torcao:
        for n, g in pz["rolos"].items(): girar(n, -eixo_osso("Coluna1") if n == "Quadril" else eixo_osso(n), g * torcao.get(n, 0.0))
    w = suave(min(1.0, 6.0 * s))                                           # perto do Repouso: mistura FK do Repouso -> IK (emenda exata)
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        if w <= 1e-6:
            for n in (sup, inf, pe, dedo): P[n].matrix = S[n]
            bpy.context.view_layer.update(); continue
        e, x = M.ik(k, MCP_S[k], 0.0, 0.0); err = max(err, e)
        for n in (sup, inf, pe, dedo): P[n].location = (0, 0, 0)
        bpy.context.view_layer.update()
        if w < 1.0:
            ik = {n: P[n].matrix.copy() for n in (sup, inf, pe, dedo)}
            for n in (sup, inf, pe, dedo):
                rot = S[n].to_quaternion().slerp(ik[n].to_quaternion(), w).to_matrix().to_4x4(); rot.translation = P[n].matrix.translation; P[n].matrix = rot; bpy.context.view_layer.update()
    for n in LOCAIS: P[n].rotation_quaternion = SLOC[n].slerp(LFIM[nome][n], c)
    bpy.context.view_layer.update()
    if ergue: girar("Cabeca", "X", -ergue)
    if boca: girar("Mandibula", "X", -boca)
    if torcao:
        if torcao.get("Cabeca"): girar("Cabeca", eixo_osso("Cabeca"), pz["cabeca_rolo"] * torcao["Cabeca"])
        if torcao.get("Cauda"):
            for n, f in (("Cauda1", 0.4), ("Cauda2", 0.3), ("Cauda3", 0.3)): girar(n, "Z", pz["cauda_lado"] * f * torcao["Cauda"])
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
REL = {"poses": {k: {"parametros": v["parametros"]} for k, v in POSES.items()}, "acoes": {}}
def todas(n): return {k: [[0, n]] for k in PATAS}
def registrar(nome, n, fn, laco=False, marc=None):
    REL["acoes"][nome] = {"quadros": n, "erro_ik": round(gravar(nome, n, fn), 5), "plantas": todas(n)}
    if laco: REL["acoes"][nome]["laco"] = True
    if marc: REL["acoes"][nome]["marcadores_s"] = marc
# ================= UIVAR =================
registrar("Uivar", 36, lambda q: pose("uivar", janela(q, 0, 30), janela(q, 2, 34)), marc={"BocaAberta": 1.13})
def uivando(q):
    if q <= 110: x = math.sin(math.pi * q / 110) ** 2; return pose("uivar", 1, 1, ergue=5.0 * x, boca=-6.0 * x, orelha=0.0)
    y = math.sin(math.pi * (q - 110) / 40) ** 2; return pose("uivar", 1, 1, ergue=-4.0 * y, boca=12.0 * y, peito=2.5 * y)
registrar("Uivando", 150, uivando, laco=True, marc={"FimDaNota": 3.67})
registrar("PararUivar", 36, lambda q: pose("uivar", 1 - janela(q, 6, 36), 1 - janela(q, 0, 32)), marc={"Repouso": 1.2})
# ================= SACUDIR (60 q, 2 s) =================
F = 4.5 / 30.0                                                             # ciclos por quadro (~4,5 por segundo)
ATRASO = {"Cabeca": 0.0, "Coluna3": 1.0, "Coluna2": 1.6, "Quadril": 2.4, "Cauda": 3.2}
def sacudir(q):
    s = janela(q, 0, 12) - janela(q, 46, 60)
    tor = {}
    for n, d in ATRASO.items():
        qq = q - d; env = janela(qq, 10, 18) * (1 - janela(qq, 38, 50))
        tor[n] = env * math.sin(2 * math.pi * F * (qq - 10))
    return pose("sacudir", s, s, torcao=tor)
registrar("Sacudir", 60, sacudir, marc={"Pico": 0.9})
print("V41", {k: (v["quadros"], v["erro_ik"]) for k, v in REL["acoes"].items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "vida_v41.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_BLOCO4_V41_OK", flush=True)
