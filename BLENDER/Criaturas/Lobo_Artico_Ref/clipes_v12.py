"""Lote 1 de clipes do Lobo Artico sobre o rig v11 (rig_v11/ so e lido): 'Repouso' e 'Andar'. Clipes PROCEDURAIS, NO LUGAR
(contrato do pipeline, como o Urso v2: o jogo move o modelo; a Raiz NAO translada e fica no chao, entre as patas; frente = -Y
do Blender, para onde o lobo olha). Cada quadro: giros de coluna/pescoco/cabeca/escapulas/cauda/orelhas/palpebras em eixos
globais do repouso, deslocamento do Quadril, alvos das 4 patas (articulacao dos dedos MCP/MTP + inclinacao da pata) -> IK
analitico de 2 ossos (Umero+Antebraco ate o carpo; Coxa+Tibia ate o jarrete, dobra no plano do repouso levado pelo pai),
Metacarpo/Metatarso pela inclinacao da pata, dedos planos no chao no apoio; o resultado e gravado em FK (quaternions) em
TODOS os quadros: nada de constraints/drivers no export.
Andar (parametros TECNICOS ajustaveis, nao regras de jogo): ciclo T, comprimento por ciclo D (velocidade v = D/T), sequencia
lateral TE 0 -> DE 0,25 -> TD 0,5 -> DD 0,75, fator de apoio 0,62; apoio: a pata recua em relacao ao corpo exatamente a v
(parada no chao na apresentacao com deslocamento); balanco: ergue e avanca (trajetoria suave), dobra o carpo/jarrete e volta
plana antes do toque; rolamento no fim do apoio em torno do CONTATO DOS DEDOS no chao (dedos presos onde tocaram). Tudo periodico em T -> laco continuo em pose e velocidade.
Repouso: 8 s (2 respiracoes de 4 s), peso lateral/frontal lento, patas plantadas pelo IK, 1 piscada (5,3 s), contracao das
orelhas, cauda lenta; boca fechada.
Tambem grava (NAO exportados): 'Teste_Transicao' (Repouso -> Andar -> Repouso, rampa de amplitude da passada, apoios
passo a passo: cada pata guarda o toque).
Uso: blender -b rig_v11/CR_LoboArtico_Rig.blend -P clipes_v12.py -- <saida_dir>"""
import bpy, sys, os, json, math, shutil
from mathutils import Vector as V, Matrix, Quaternion
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
for f in ("rig_pivos.json", "acao_v10.json", "rig_v11.json"): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; B = ARM.data.bones
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def onda(t, T, f=0.0): return math.sin(2 * math.pi * (t / T + f))
REST = {b.name: b.matrix_local.copy() for b in B}
def q_global(n, R): Bm = REST[n].to_3x3(); return (Bm.inverted() @ R @ Bm).to_quaternion()
PATAS = {"DE": ("Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D"),
         "TE": ("Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"), "TD": ("Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D")}
MCP0 = {k: B[c[2]].tail_local.copy() for k, c in PATAS.items()}; CAR0 = {k: B[c[2]].head_local.copy() for k, c in PATAS.items()}
def ik(k, mcp, phi, phi_dedo):
    """pata k: articulacao dos dedos em 'mcp' (espaco do armature), inclinacao da pata phi (rad, em X: >0 calcanhar sobe /
    pata dobra para tras), dedos com phi_dedo em relacao ao chao"""
    sup, inf, pe, dedo = PATAS[k]; bs, bi = B[sup], B[inf]; a, b = bs.length, bi.length
    Rp = Matrix.Rotation(phi, 3, X); T = mcp + Rp @ (CAR0[k] - MCP0[k])           # carpo / jarrete
    S = P[sup].head.copy(); Mpai = P[sup].parent.matrix @ B[sup].parent.matrix_local.inverted()
    K0, S0 = bs.tail_local, bs.head_local; d0 = (bi.tail_local - S0).normalized()
    dob = Mpai.to_3x3() @ ((K0 - S0) - d0 * (K0 - S0).dot(d0))
    dv = T - S; d = min(dv.length, (a + b) * 0.9995); dn = dv.normalized()
    al = (a * a - b * b + d * d) / (2 * d); h = math.sqrt(max(a * a - al * al, 0.0)); perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0 in ((sup, S, K), (inf, K, S + dn * d)):
        yv = (t0 - h0).normalized(); xr = Mpai.to_3x3() @ REST[nome].col[0].to_3d(); xv = (xr - yv * xr.dot(yv)).normalized()
        M = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); M.translation = h0; P[nome].matrix = M; bpy.context.view_layer.update()
    M = (Rp.to_4x4() @ Matrix.Translation(-MCP0[k]) @ REST[pe]); M.translation = P[inf].tail.copy(); P[pe].matrix = M; bpy.context.view_layer.update()
    M = Matrix.Rotation(phi_dedo, 4, X) @ Matrix.Translation(-MCP0[k]) @ REST[dedo]; M.translation = P[pe].tail.copy(); P[dedo].matrix = M
    bpy.context.view_layer.update()
    return (S + dn * d - T).length                                     # erro do IK (alcance)
# ------------------------------------------------------------------ parametros (TECNICOS, ajustaveis)
ANDAR = {"T": 1.2, "D": 3.6, "apoio": 0.62, "fases": {"TE": 0.0, "DE": 0.25, "TD": 0.5, "DD": 0.75}, "altura_dianteira": 0.42, "altura_traseira": 0.36,
         "rolamento_graus": 28.0, "dobra_balanco_dianteira_graus": 95.0, "dobra_balanco_traseira_graus": 70.0}
ANDAR["v_studs_s"] = ANDAR["D"] / ANDAR["T"]
REPOUSO = {"T": 8.0, "respiracao_s": 4.0, "piscada_s": 5.3}
def pata_andar(k, t, amp=1.0):
    """deslocamento da MCP (dy, dz) e angulos (phi, phi_dedo) da pata k no tempo t (amp = escala da passada, transicao)"""
    T, beta = ANDAR["T"], ANDAR["apoio"]; S = ANDAR["D"] * beta * amp; u = ((t / T) - ANDAR["fases"][k]) % 1.0
    h = (ANDAR["altura_dianteira"] if k[0] == "D" else ANDAR["altura_traseira"]) * amp
    roll = math.radians(ANDAR["rolamento_graus"]) * amp; dob = math.radians(ANDAR["dobra_balanco_dianteira_graus" if k[0] == "D" else "dobra_balanco_traseira_graus"]) * amp
    if u < beta:                                                        # apoio: recua a v (frente = -y)
        s = u / beta; dy = -S / 2 + S * s; dz = 0.0; rolo = roll * suave((s - 0.72) / 0.28); dobra = 0.0
    else:                                                               # balanco
        w = (u - beta) / (1 - beta); m = w * w * w * (10 - 15 * w + 6 * w * w)       # min-jerk
        dy = S / 2 - S * m; dz = altura_balanco(h, w)
        rolo = roll * (1 - suave((w - 0.2) / 0.4)); dobra = dob * math.sin(math.pi * w) ** 1.5 * (1 - suave((w - 0.7) / 0.3))
    return dy, dz, rolo, dobra
TIP0 = {k: B[c[3]].tail_local.copy() for k, c in PATAS.items()}
def altura_balanco(h, w):
    """sobe logo na saida e so chega a zero NO toque (a versao anterior zerava em 87% do balanco e a pata encostava ainda
    avancando: ~0,13 stud de escorregao no pouso)"""
    return h * math.sin(math.pi * w ** 0.8) ** 1.15
def alvo_pata(k, dy, dz, rolo, dobra):
    """rolamento em torno do CONTATO DOS DEDOS no chao (nao da articulacao, 0,3 acima: arrastava as almofadas): a MCP sobe
    girando em torno de C e os dedos apontam para a ponta, que fica onde tocou; a dobra do balanco gira na MCP"""
    mcp = MCP0[k] + V((0, dy, dz)); tv = TIP0[k] - MCP0[k]; C = mcp + 0.7 * tv
    m_ef = C + Matrix.Rotation(rolo, 3, X) @ (mcp - C); nd = (mcp + tv) - m_ef
    phi_dedo_rolo = math.atan2(nd.z, nd.y) - math.atan2(tv.z, tv.y)
    return m_ef, rolo + dobra, phi_dedo_rolo + 0.45 * dobra
def pose_corpo(t, amp=1.0, resp=0.0):
    """giros (osso: [(eixo, graus)]) e deslocamento do Quadril no Andar (amp) somados a respiracao/repouso"""
    T = ANDAR["T"]; R = {}; q = V((0, 0, 0))
    def add(n, e, g): R.setdefault(n, []).append((e, g))
    if amp > 0:
        q += V((0.035 * onda(t, T, 0.0) * amp, 0.0, (-0.03 * math.cos(4 * math.pi * t / T) - 0.012) * amp))
        add("Quadril", Y, 2.2 * onda(t, T, 0.0) * amp); add("Quadril", Z, 3.0 * onda(t, T, 0.25) * amp)
        add("Coluna1", Z, -1.2 * onda(t, T, 0.25) * amp); add("Coluna2", Z, -1.5 * onda(t, T, 0.30) * amp); add("Coluna3", Z, -1.8 * onda(t, T, 0.35) * amp)
        add("Coluna3", Y, -1.6 * onda(t, T, 0.25) * amp)
        add("Pescoco1", Z, 1.4 * onda(t, T, 0.4) * amp); add("Cabeca", Z, 1.0 * onda(t, T, 0.45) * amp)
        add("Pescoco1", X, 1.3 * math.cos(4 * math.pi * t / T + 0.6) * amp); add("Cabeca", X, -1.6 * math.cos(4 * math.pi * t / T + 0.9) * amp)   # cabeca estabilizada
        for i, n in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):
            add(n, Z, (2.0 + 1.6 * i) * onda(t, T, 0.1 + 0.08 * i) * amp); add(n, X, 1.2 * math.cos(4 * math.pi * t / T + 0.5 * i) * amp)
        for n, s in (("Orelha_E", 1), ("Orelha_D", -1)): add(n, X, 2.5 * math.cos(4 * math.pi * t / T + 1.2) * amp)
        for lado, f in (("E", 0.25), ("D", 0.75)):                       # escapula acompanha a pata (frente/tras)
            u = ((t / T) - f) % 1.0; add("Escapula_" + lado, X, -5.0 * math.cos(2 * math.pi * (u - 0.31)) * amp)
    if resp:
        TR = REPOUSO["respiracao_s"]; b = onda(t, TR, 0.0) * resp
        add("Coluna2", X, -0.8 * b); add("Coluna3", X, -0.6 * b); add("Pescoco1", X, 0.9 * b); add("Pescoco2", X, 0.35 * b)
        q += V((0.022 * onda(t, REPOUSO["T"], 0.0) * resp, 0.015 * onda(t, REPOUSO["T"], 0.25) * resp, 0.006 * b))
        add("Quadril", Y, -0.8 * onda(t, REPOUSO["T"], 0.0) * resp)
        add("Cabeca", Z, 1.2 * onda(t, REPOUSO["T"], 0.6) * resp); add("Cabeca", X, 0.6 * onda(t, REPOUSO["T"] / 2, 0.3) * resp)
        for i, n in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):
            add(n, Z, (1.0 + 0.8 * i) * onda(t, REPOUSO["T"], 0.1 * i) * resp); add(n, X, 0.6 * onda(t, TR, 0.2 + 0.1 * i) * resp)
        tw = lambda c, d: math.sin(math.pi * suave((t - c) / d)) if c <= t <= c + d else 0.0
        add("Orelha_E", X, -9.0 * tw(2.1, 0.35) * resp); add("Orelha_E", Z, 5.0 * tw(2.1, 0.35) * resp); add("Orelha_D", X, -6.0 * tw(6.4, 0.4) * resp)
    return R, q
def pisca(t):
    c, d = REPOUSO["piscada_s"], 0.24
    if not (c <= t <= c + d): return 0.0
    x = (t - c) / d; return suave(x / 0.4) if x < 0.4 else (1.0 if x < 0.55 else 1 - suave((x - 0.55) / 0.45))
def montar(t, amp, resp, pisc, pes=None):
    for pb in P: pb.matrix_basis.identity()
    R, q = pose_corpo(t, amp, resp)
    for n, lst in R.items():
        M = Matrix.Identity(3)
        for e, g in lst: M = Matrix.Rotation(math.radians(g), 3, e) @ M
        P[n].rotation_quaternion = q_global(n, M)
    P["Quadril"].location = REST["Quadril"].to_3x3().inverted() @ q
    for lado, ol in PIV["olhos"].items():
        for kk, ang in (("Sup", ol["fechar_sup_graus"]), ("Inf", ol["fechar_inf_graus"])):
            P["Palpebra_%s_%s" % (kk, lado)].rotation_quaternion = Quaternion(X, math.radians(ang * pisc))
    bpy.context.view_layer.update(); err = 0.0
    for k in PATAS:
        if pes is not None: dy, dz, rolo, dobra = pes[k]
        elif amp > 0: dy, dz, rolo, dobra = pata_andar(k, t, amp)
        else: dy = dz = rolo = dobra = 0.0
        m_ef, phi, phd = alvo_pata(k, dy, dz, rolo, dobra)
        err = max(err, ik(k, m_ef, phi, phd))
    for k, c in PATAS.items():
        for n in c: P[n].location = (0, 0, 0)
    return err
def gravar(nome, n_quadros, fn):
    if ARM.animation_data: ARM.animation_data.action = None              # calcula SEM acao atribuida (a avaliacao da acao
    for pb in P: pb.rotation_mode = "QUATERNION"                        # anterior sobrescrevia a pose a cada update do IK)
    VAL, ERR = [], 0.0
    for qi in range(n_quadros + 1):
        ERR = max(ERR, fn(qi / FPS)); VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    ac = bpy.data.actions.new(nome); ARM.animation_data_create(); ARM.animation_data.action = ac
    for qi, vals in enumerate(VAL):
        for pb in P:
            pb.rotation_quaternion, pb.location = vals[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=qi, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=qi, group=pb.name)
    ac.use_fake_user = True; ac.frame_range = (0, n_quadros)
    for pb in P: pb.matrix_basis.identity()
    return ac, ERR
if ARM.animation_data: ARM.animation_data.action = None
REL = {"contrato": "no lugar; Raiz fixa no chao (sem translacao); frente = -Y do Blender; deslocamento e velocidade pelo controlador do jogo",
       "fps": FPS, "andar": ANDAR, "repouso": REPOUSO, "acoes": {}}
nA = int(round(ANDAR["T"] * FPS)); acA, eA = gravar("Andar", nA, lambda t: montar(t, 1.0, 0.0, 0.0))
nR = int(round(REPOUSO["T"] * FPS)); acR, eR = gravar("Repouso", nR, lambda t: montar(t, 0.0, 1.0, pisca(t)))
# transicao tecnica (nao exportada): 2 s repouso, rampa 0,6 s, 3 ciclos, rampa 0,6 s, 2 s repouso
TT = [2.0, 0.6, 3 * ANDAR["T"], 0.6, 2.0]; c_ = [sum(TT[:i]) for i in range(len(TT) + 1)]
def amp_tr(t):
    if t < c_[1]: return 0.0
    if t < c_[2]: return suave((t - c_[1]) / TT[1])
    if t < c_[3]: return 1.0
    if t < c_[4]: return 1 - suave((t - c_[3]) / TT[3])
    return 0.0
def pes_transicao():
    """passo a passo: no apoio a pata guarda o toque e recua junto com o corpo (v * amplitude); no balanco vai do ponto de
    saida ao alvo do proximo toque (-S/2 com a amplitude daquele instante); fases do Andar a partir do inicio da rampa"""
    T, beta = ANDAR["T"], ANDAR["apoio"]; n = int(round(c_[-1] * FPS)); dt = 1.0 / FPS; out = []
    est = {k: {"y": 0.0, "y_saida": 0.0, "fase": None} for k in PATAS}
    for qi in range(n + 1):
        t = qi * dt; am = amp_tr(t); tt = t - c_[1]; fr = {}
        for k in PATAS:
            e = est[k]; u = ((tt / T) - ANDAR["fases"][k]) % 1.0; ap = u < beta or am <= 1e-4
            ah = suave(am / 0.3)                                        # altura/dobra cheias logo no inicio da rampa: passos de verdade
            h = (ANDAR["altura_dianteira"] if k[0] == "D" else ANDAR["altura_traseira"]) * ah
            roll = math.radians(ANDAR["rolamento_graus"]) * ah; dob = math.radians(ANDAR["dobra_balanco_dianteira_graus" if k[0] == "D" else "dobra_balanco_traseira_graus"]) * ah
            if ap:
                if e["fase"] == "balanco": e["y"] = e["alvo"]
                e["fase"] = "apoio"; e["y"] += ANDAR["v_studs_s"] * am * dt if am > 1e-4 else 0.0
                s_ = u / beta if am > 1e-4 else 0.0; fr[k] = (e["y"], 0.0, roll * suave((s_ - 0.72) / 0.28), 0.0)
            else:
                w = (u - beta) / (1 - beta)
                if e["fase"] != "balanco": e["y_saida"] = e["y"]; e["fase"] = "balanco"
                t_toque = t + (1 - w) * (1 - beta) * T                          # alvo pela amplitude do MEIO do proximo apoio
                e["alvo"] = -ANDAR["D"] * beta * amp_tr(t_toque + beta * T / 2) / 2  # (pelo toque: a pata passava do alcance no fim)
                m = w * w * w * (10 - 15 * w + 6 * w * w); y = e["y_saida"] + (e["alvo"] - e["y_saida"]) * m; e["y"] = y
                dz = altura_balanco(h, w)
                fr[k] = (y, dz, roll * (1 - suave((w - 0.2) / 0.4)), dob * math.sin(math.pi * w) ** 1.5 * (1 - suave((w - 0.7) / 0.3)))
        out.append(fr)
    return out
PES_TR = pes_transicao()
acT, eT = gravar("Teste_Transicao", int(round(c_[-1] * FPS)), lambda t: montar(t - c_[1], amp_tr(t), 1.0 - amp_tr(t), 0.0, PES_TR[int(round(t * FPS))]))
REL["acoes"] = {"Andar": {"quadros": nA, "duracao_s": ANDAR["T"], "laco": True, "v_studs_s": round(ANDAR["v_studs_s"], 3), "erro_ik_max": round(eA, 5)},
                "Repouso": {"quadros": nR, "duracao_s": REPOUSO["T"], "laco": True, "erro_ik_max": round(eR, 5)},
                "Teste_Transicao": {"quadros": int(round(c_[-1] * FPS)), "trechos_s": TT, "exportar": False, "erro_ik_max": round(eT, 5),
                                    "nota": "rampa da amplitude da passada; v instantanea = v * amplitude"}}
ARM.animation_data.action = acA; sc.frame_start, sc.frame_end = 0, nA
json.dump(REL, open(os.path.join(OUT, "clipes_v12.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("CLIPES_V12_OK", json.dumps(REL["acoes"]), flush=True)
