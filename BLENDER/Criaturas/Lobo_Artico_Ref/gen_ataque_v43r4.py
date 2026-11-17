"""Ataque basico v43 r4 (17/11/2026) - rodada sobre COPIA da v43 r3 (anim_v43 -> anim_v43r4; a r3 fica intacta e tambem
e copiada para dentro do .blend novo como R3_<acao> so para comparar lado a lado).
Pedido do usuario: "agora nem se parecem com patadas" + roteiro: bote que AVANCA ate o contato com boca legivel; garra em
ARCO BAIXO e CURTO, preparo discreto, aceleracao ao contato, recolhimento claro, distinguivel de um passo.
Medido na r3 (medir_r3): Mordida1 no contato = focinho 0,43 para TRAS e 1,94 para BAIXO (despenca); GarraE = pata vai 2,0 a
frente e 0,93 para cima e no contato volta 0,86 ATRAS do repouso (= desenho de uma passada). Passo: Andar sobe 0,13,
Trote 0,29, Corrida 0,72.
Base real (pesquisa 17/11): lobos quase nao agarram com as patas (sem garras retrateis nem antebraco que gira; dependem da
boca) -> a GARRA e adaptacao de jogo: o gesto e o de "pisar/prender" a presa com a dianteira (carpo dobrado no preparo,
bate para frente-baixo com os dedos abertos, crava e puxa para tras pelo chao, recolhe dobrando o carpo).
r4:
- Mordida1/2: trajetoria-alvo do FOCINHO (ponta do osso Cabeca) resolvida a cada quadro (busca nos angulos de Pescoco1/
  Pescoco2; Cabeca da o angulo de mira): recua (q0-3: +0,30 atras/+0,22 acima) -> bote (q3-6: 0,95 a frente, 0,45 abaixo;
  Mordida2 tambem 0,60 para o lado, focinho virado para o lado do bote) -> contato q6 (fecha de estalo) -> puxa (q6-8:
  0,20 de volta, Mordida2 rasga girando) -> volta (q8-15). Boca: abre no recuo (+40), segura aberta na aproximacao, fecha
  q5,3 -> q6, segura fechada (mordendo) ate q9, solta +10 e fecha.
- GarraE/D: pata por IK (marcha_v21.ik + alvo_pata) com chaves: q0 repouso; q2,5 preparo (sobe 0,30, recua 0,10, carpo
  dobrado 75 graus); q5 alcance (0,80 a frente, 0,42 acima, dedos abertos); q7 CONTATO (1,15 a frente, no chao, um pouco
  para dentro sem cruzar, dedos cravando); q9 puxa (0,85 a frente, no chao); q12 recolhe (0,30 a frente, 0,22 acima,
  carpo dobrado 45); q15 repouso. Altura maxima 0,42 (Andar 0,13 / Trote 0,29): o que distingue do passo e o carpo dobrado,
  os dedos abertos/cravando e o puxao para tras pelo chao.
- Olhos: estreitam mirando (0,40) e piscam forte so 1-2 quadros no contato (0,75) -> olhar legivel na mira.
Marcadores Contato iguais a r3 (Mordida q6 = 0,2 s; Garra q7 = 0,233 s): o servidor (CFG.basico.contato) NAO muda.
Uso: blender -b anim_v43/CR_LoboArtico_Anim.blend -P gen_ataque_v43r4.py -- anim_v43r4"""
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
ARM = M.ARM; P = M.P; sc = bpy.context.scene
# r4b: Pescoco1 e "conectado" ao pai no Blender (osso conectado ignora location) -> desconecta SO no .blend de trabalho
# (repouso identico; no Roblox os Bones aceitam translacao e o export JSON ja leva matrix_basis.translation)
CONECTADO = ARM.data.bones["Pescoco1"].use_connect
if CONECTADO:
    bpy.context.view_layer.objects.active = ARM; ARM.select_set(True); bpy.ops.object.mode_set(mode="EDIT")
    ARM.data.edit_bones["Pescoco1"].use_connect = False; bpy.ops.object.mode_set(mode="POSE"); bpy.ops.object.mode_set(mode="OBJECT")
print("PESCOCO1_CONECTADO_ANTES", CONECTADO, flush=True)
for pb in P: pb.rotation_mode = "QUATERNION"
def suave(x): x = max(0.0, min(1.0, x)); return x * x * x * (10 - 15 * x + 6 * x * x)
def janela(q, a, b): return suave((q - a) / max(1e-9, b - a))
def girar(osso, eixo, graus, piv=None):
    if not graus: return
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def da_acao(nome, q):
    for pb in P: pb.location = (0, 0, 0)          # r4b: zera translacoes que a acao nao tem (avanco do pescoco acumulava)
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); ARM.animation_data.action = None
def repouso_q0(): da_acao("Repouso", 0)
def chaves(q, ks):
    """spline Catmull-Rom (nao uniforme) pelas chaves [(q, valor), ...]: o movimento NAO para em cada chave (o golpe
    acelera continuamente ate o contato); velocidade zero so na primeira e na ultima chave."""
    tup = isinstance(ks[0][1], tuple)
    vals = [list(v) if tup else [v] for _, v in ks]; ts = [t for t, _ in ks]
    if q <= ts[0]: r = vals[0]
    elif q >= ts[-1]: r = vals[-1]
    else:
        i = max(j for j in range(len(ts) - 1) if ts[j] <= q)
        t0, t1 = ts[i], ts[i + 1]; p0, p1 = vals[i], vals[i + 1]; h = t1 - t0; s = (q - t0) / h
        def tang(j):
            if j == 0 or j == len(ts) - 1: return [0.0] * len(p0)
            return [(vals[j + 1][c] - vals[j - 1][c]) / (ts[j + 1] - ts[j - 1]) for c in range(len(p0))]
        m0, m1 = tang(i), tang(i + 1)
        h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
        r = [h00 * p0[c] + h10 * h * m0[c] + h01 * p1[c] + h11 * h * m1[c] for c in range(len(p0))]
    return tuple(r) if tup else r[0]

# ---- copia da r3 para comparar ----
for n in ("Mordida1", "Mordida2", "GarraE", "GarraD", "Piscar"):
    if n in bpy.data.actions:
        c = bpy.data.actions[n].copy(); c.name = "R3_" + n; c.use_fake_user = True

PALP = ["Palpebra_Sup_E", "Palpebra_Inf_E", "Palpebra_Sup_D", "Palpebra_Inf_D"]
CABECA = ["Pescoco1", "Pescoco2", "Cabeca", "Mandibula", "Orelha_E", "Orelha_D"] + PALP
PATA = {"E": list(M.PATAS["DE"]), "D": list(M.PATAS["DD"])}
N = 15; CONTATO_M = 6; CONTATO_G = 7
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
def olhos(f_sup, f_inf):
    for lado, ol in PIV["olhos"].items():
        P["Palpebra_Sup_" + lado].rotation_quaternion = Quaternion((1, 0, 0), math.radians(ol["fechar_sup_graus"] * f_sup))
        P["Palpebra_Inf_" + lado].rotation_quaternion = Quaternion((1, 0, 0), math.radians(ol["fechar_inf_graus"] * f_inf))
    bpy.context.view_layer.update()
def focinho(): return ARM.matrix_world @ P["Cabeca"].tail
def ang_cabeca():
    yc = (ARM.matrix_world.to_3x3() @ P["Cabeca"].matrix.col[1].xyz); return math.degrees(math.atan2(-yc.z, math.hypot(yc.x, yc.y)))
repouso_q0(); S0 = focinho().copy(); CAB0 = ang_cabeca()
MCP_S = {k: P[c[2]].tail.copy() for k, c in M.PATAS.items()}

# ================= MORDIDA =================
NECK_T = [V((0, 0, 0))]
def pose_pescoco(a1, a2, yaw, pitch_cab, roll):
    repouso_q0()
    # r4b: avanco do pescoco (translacao da base do Pescoco1 no mundo = empurrao dos ombros no bote; o tronco segue a
    # locomocao no clipe parcial). Medido na r4a: so com rotacao o focinho avancava 0,11 (ele ja fica na altura da base).
    if NECK_T[0].length > 1e-6:
        mt = P["Pescoco1"].matrix.copy(); mt.translation = mt.translation + NECK_T[0]; P["Pescoco1"].matrix = mt; bpy.context.view_layer.update()
    if yaw: girar("Pescoco1", "Z", 0.55 * yaw); girar("Pescoco2", "Z", 0.30 * yaw)
    girar("Pescoco1", "X", a1); girar("Pescoco2", "X", a2)
    if yaw: girar("Cabeca", "Z", 0.15 * yaw)
    girar("Cabeca", "X", pitch_cab - ang_cabeca())
    if roll: girar("Cabeca", "Y", roll)
SOL = {}
def resolver(alvo, yaw, pitch_cab, roll, chute):
    def custo(a1, a2):
        pose_pescoco(a1, a2, yaw, pitch_cab, roll); return (focinho() - alvo).length
    best = (chute, custo(*chute))
    for passo in (6.0, 3.0, 1.5, 0.75):
        melhorou = True
        while melhorou:
            melhorou = False
            for d1, d2 in ((passo, 0), (-passo, 0), (0, passo), (0, -passo), (passo, -passo), (-passo, passo)):
                c = (max(-25, min(40, best[0][0] + d1)), max(-25, min(35, best[0][1] + d2)))
                e = custo(*c)
                if e < best[1] - 1e-4: best = (c, e); melhorou = True
    pose_pescoco(*best[0], yaw, pitch_cab, roll); return best
def mordida_alvo(q, lado):
    rec = (0.0, 0.30, 0.22); bote = (0.60 * lado, -0.95, -0.45); puxa = (0.45 * lado, -0.75, -0.42)
    return chaves(q, [(0, (0.0, 0.0, 0.0)), (3, rec), (6, bote), (8, puxa), (11, (0.15 * lado, -0.25, -0.12)), (15, (0.0, 0.0, 0.0))])
# r4c: variante _Corrida (QA: no galope o corpo desce 0,39-1,07; a cabeca do golpe ficava 0,6-0,75 ACIMA da cabeca da
# locomocao e a pata da garra atravessava o chao ate 1,08) -> focinho 0,70 mais baixo / pata 0,90 mais alta o clipe todo.
VAR = {"corrida": False}
def mordida(q, lado=0):
    dx, dy, dz = mordida_alvo(q, lado)
    alvo = S0 + V((dx, dy, dz - (0.70 if VAR["corrida"] else 0.0)))
    NECK_T[0] = V((0.0, min(0.0, dy) * 0.62, min(0.0, dz) * 0.25))       # ate ~0,59 a frente e 0,11 abaixo no contato
    yaw = chaves(q, [(0, 0.0), (3, 4.0 * lado), (6, 16.0 * lado), (8, 14.0 * lado), (15, 0.0)])     # Mordida2: focinho virado ao lado do bote
    pitch = chaves(q, [(0, CAB0), (3, CAB0 - 8.0), (6, CAB0 + 6.0), (8, CAB0 + 6.0), (15, CAB0)]) + (8.0 if VAR["corrida"] else 0.0)   # mira: cabeca sobe no recuo, nivela no bote
    roll = (-24.0 * lado * janela(q, CONTATO_M, CONTATO_M + 2.5) * (1 - janela(q, 10, N))) if lado else 0.0   # rasga
    ch = SOL.get(("m", lado, q - 1), (0.0, 0.0))
    (a, b), err = resolver(alvo, yaw, pitch, roll, ch); SOL[("m", lado, q)] = (a, b); ERR_M.append(err)
    abre = janela(q, 0.5, 3) * (1 - janela(q, CONTATO_M - 0.7, CONTATO_M))
    solta = 0.25 * janela(q, 9, 11) * (1 - janela(q, 12.5, N))
    girar("Mandibula", "X", 40 * abre + 40 * solta)
    for o in ("Orelha_E", "Orelha_D"): girar(o, "X", -32 * chaves(q, [(0, 0.0), (2, 1.0), (10, 1.0), (15, 0.0)]))
    mira = chaves(q, [(0, 0.0), (2, 0.40), (11, 0.40), (15, 0.0)])
    reflexo = chaves(q, [(0, 0.0), (CONTATO_M - 0.5, 0.0), (CONTATO_M, 0.75), (CONTATO_M + 1.5, 0.0), (15, 0.0)])
    olhos(max(mira, reflexo), max(0.8 * mira, 0.8 * reflexo))
    return 0.0
ERR_M = []

# ================= GARRA =================
def garra(q, lado):
    NECK_T[0] = V((0, 0, 0)); repouso_q0(); s = "E" if lado > 0 else "D"; k = "D" + s; sg = 1 if lado > 0 else -1
    # pata: (dx para dentro, dy [- = frente], dz, dobra do carpo em graus, dedos em graus [- abre/levanta, + crava])
    # r4b: contato e puxao sobem (a r4a cravava a ponta dos dedos 0,14-0,18 no chao)
    # r4c: dobra do carpo 75 -> 55 e 45 -> 35 (a torcao medida acompanhava a dobra; Andar aprovado chega a 15-21 na mesma
    # medida) e contato/puxao +0,08 (Trote: ombro desce 0,26 e a ponta afundava 0,12-0,16)
    K = [(0, (0.0, 0.0, 0.0, 0.0, 0.0)), (2.5, (0.0, 0.10, 0.30, 55.0, 10.0)), (5, (0.04, -0.80, 0.42, 18.0, -28.0)),
         (CONTATO_G, (0.10, -1.15, 0.24, 0.0, 22.0)), (9, (0.08, -0.85, 0.26, 0.0, 26.0)), (12, (0.03, -0.30, 0.30, 35.0, 8.0)),
         (15, (0.0, 0.0, 0.0, 0.0, 0.0))]
    dx, dy, dz, dobra, dedo = chaves(q, K); dz = max(0.0, dz); dobra = max(0.0, dobra)   # spline nao pode afundar a pata
    if VAR["corrida"]: dz += 0.90
    mcp, phi, phid = M.alvo_pata(k, dy, dz, 0.0, math.radians(dobra))
    mcp = mcp + V((-sg * dx, 0, 0))                     # para dentro (E fica em +x)
    e, ext = M.ik(k, mcp, phi, phid + math.radians(dedo)); ERR_G.append(e)
    # cabeca acompanha o lado do golpe, baixa um pouco; boca em rosnado
    cab = chaves(q, [(0, 0.0), (3, 1.0), (10, 1.0), (15, 0.0)])
    girar("Pescoco1", "X", 6 * cab); girar("Pescoco2", "X", 4 * cab); girar("Pescoco1", "Z", 7 * sg * cab); girar("Cabeca", "X", 4 * cab)
    girar("Mandibula", "X", 16 * chaves(q, [(0, 0.0), (3, 1.0), (9, 1.0), (13, 0.0)]))
    for o in ("Orelha_E", "Orelha_D"): girar(o, "X", -26 * cab)
    mira = chaves(q, [(0, 0.0), (2, 0.40), (11, 0.40), (15, 0.0)])
    reflexo = chaves(q, [(0, 0.0), (CONTATO_G - 0.5, 0.0), (CONTATO_G, 0.6), (CONTATO_G + 1.5, 0.0), (15, 0.0)])
    olhos(max(mira, reflexo), max(0.8 * mira, 0.8 * reflexo))
    return 0.0
ERR_G = []

def gravar_parcial(nome, n, fn, ossos):
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); VAL = []
    for q in range(n + 1):
        fn(q); VAL.append({o: (P[o].rotation_quaternion.copy(), P[o].location.copy()) for o in ossos})
    ARM.animation_data.action = acn; prev = {}
    for q, vals in enumerate(VAL):
        for o in ossos:
            rq, lc = vals[o]
            if o in prev and rq.dot(prev[o]) < 0: rq = -rq
            prev[o] = rq; P[o].rotation_quaternion = rq; P[o].keyframe_insert("rotation_quaternion", frame=q, group=o)
            if o == "Pescoco1": P[o].location = lc; P[o].keyframe_insert("location", frame=q, group=o)   # r4b: avanco do pescoco
    acn.use_fake_user = True; acn.frame_range = (0, n); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
REL = {"versao": "v43 r4", "acoes": {}, "nota": "clipes PARCIAIS; marcadores iguais a r3 (servidor nao muda)"}
for nome, fn, ossos, cont in (
        ("Mordida1", lambda q: mordida(q, 0), CABECA, CONTATO_M),
        ("Mordida2", lambda q: mordida(q, 1), CABECA, CONTATO_M),
        ("GarraE", lambda q: garra(q, 1), CABECA + PATA["E"], CONTATO_G),
        ("GarraD", lambda q: garra(q, -1), CABECA + PATA["D"], CONTATO_G)):
    gravar_parcial(nome, N, fn, ossos)
    REL["acoes"][nome] = {"quadros": N, "parcial": True, "ossos": ossos, "marcadores_s": {"Contato": round(cont / 30, 3)}}
VAR["corrida"] = True
for nome, fn, ossos, cont in (
        ("Mordida1_Corrida", lambda q: mordida(q, 0), CABECA, CONTATO_M),
        ("Mordida2_Corrida", lambda q: mordida(q, 1), CABECA, CONTATO_M),
        ("GarraE_Corrida", lambda q: garra(q, 1), CABECA + PATA["E"], CONTATO_G),
        ("GarraD_Corrida", lambda q: garra(q, -1), CABECA + PATA["D"], CONTATO_G)):
    gravar_parcial(nome, N, fn, ossos)
    REL["acoes"][nome] = {"quadros": N, "parcial": True, "variante": "Corrida (servidor escolhe pela marcha)", "ossos": ossos, "marcadores_s": {"Contato": round(cont / 30, 3)}}
VAR["corrida"] = False
def piscar(q):
    repouso_q0(); f = janela(q, 0, 3) * (1 - janela(q, 4, 8)); olhos(f, 0.9 * f); return 0.0
gravar_parcial("Piscar", 8, piscar, PALP)
REL["acoes"]["Piscar"] = {"quadros": 8, "parcial": True, "ossos": PALP, "marcadores_s": {}}
REL["erro_focinho_max"] = round(max(ERR_M), 3); REL["erro_ik_pata_max"] = round(max(ERR_G), 4)
print("V43R4", {k: (v["quadros"], len(v["ossos"])) for k, v in REL["acoes"].items()}, "erro focinho", REL["erro_focinho_max"], "ik pata", REL["erro_ik_pata_max"], flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "ataque_v43.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_ATAQUE_V43R4_OK", flush=True)
