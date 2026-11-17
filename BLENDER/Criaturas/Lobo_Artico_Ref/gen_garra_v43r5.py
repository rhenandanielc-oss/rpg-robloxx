"""Garras v43 r5 (17/11/2026) - rodada sobre COPIA da v43 r4 (anim_v43r4 -> anim_v43r5). SO GarraE/GarraD e as variantes
_Corrida mudam; Mordida1/2 (+_Corrida), Piscar e a locomocao sao copiados intactos. A r4 das garras fica como R4_<acao>.
Pedido do usuario (roteiro "Corrigir as patadas"): golpe baixo, curto e distinto da passada; preparo discreto,
aceleracao ao alvo, contato claro, recolhimento; sem afundar (r4: ate 0,15 no Trote e 0,17 na Corrida, em entrada/saida e
no contato), sem arrasto no puxao, sem torcao visivel; Contato em q7 (0,233 s) e 0,5 s mantidos.
Medido na r4 (qa_r4.json): Trote afunda em q1/q14 (o clipe forca a perna ao repouso com o corpo mais baixo); Corrida afunda
no contato/puxao (q6-7, q11-12) e o puxao pelo chao arrasta (o corpo anda ate 0,68 por quadro na Corrida).
r5 (adaptacao de jogo): a pata ACERTA O ALVO a frente numa altura baixa (nao crava no chao) e recolhe pelo ar:
  q0 entrada (o jogo faz fade de 0,06 s) -> q1,5 ja descolou (sobe 0,24, carpo dobrando) -> q3,5 preparo (pata recolhida sob
  o peito, carpo dobrado 55) -> q5,5 acelera para frente (dedos abrindo) -> q7 CONTATO no alvo (1,30 a frente, 0,42 acima
  do apoio, perna estendida, dedos abertos) -> q8,5 garras fecham no impacto (rebote curto) -> q11 recolhe (carpo dobra)
  -> q13,5 desce -> q15 quase no apoio (0,10 acima; o jogo volta para a passada).
  Sem translacao lateral para dentro (a r4 levava 0,10 para dentro: parte da virada do carpo). Variante _Corrida: +0,90 no
  clipe todo (galope com o corpo 0,39-1,07 mais baixo).
Uso: blender -b anim_v43r4/CR_LoboArtico_Anim.blend -P gen_garra_v43r5.py -- anim_v43r5"""
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
for pb in P: pb.rotation_mode = "QUATERNION"
def suave(x): x = max(0.0, min(1.0, x)); return x * x * x * (10 - 15 * x + 6 * x * x)
def girar(osso, eixo, graus, piv=None):
    if not graus: return
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def da_acao(nome, q):
    for pb in P: pb.location = (0, 0, 0)
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); ARM.animation_data.action = None
def repouso_q0(): da_acao("Repouso", 0)
def chaves(q, ks):
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
# r4 das garras guardada para comparar (R4_*); o resto do .blend (mordidas, Piscar, R3_*, locomocao) fica como esta
for n in ("GarraE", "GarraD", "GarraE_Corrida", "GarraD_Corrida"):
    velho = bpy.data.actions.get("R4_" + n)
    if velho: bpy.data.actions.remove(velho)
    c = bpy.data.actions[n].copy(); c.name = "R4_" + n; c.use_fake_user = True
PALP = ["Palpebra_Sup_E", "Palpebra_Inf_E", "Palpebra_Sup_D", "Palpebra_Inf_D"]
CABECA = ["Pescoco1", "Pescoco2", "Cabeca", "Mandibula", "Orelha_E", "Orelha_D"] + PALP
PATA = {"E": list(M.PATAS["DE"]), "D": list(M.PATAS["DD"])}
N = 15; CONTATO_G = 7
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
def olhos(f_sup, f_inf):
    for lado, ol in PIV["olhos"].items():
        P["Palpebra_Sup_" + lado].rotation_quaternion = Quaternion((1, 0, 0), math.radians(ol["fechar_sup_graus"] * f_sup))
        P["Palpebra_Inf_" + lado].rotation_quaternion = Quaternion((1, 0, 0), math.radians(ol["fechar_inf_graus"] * f_inf))
    bpy.context.view_layer.update()
# chaves da pata: (dy [- = frente], dz [acima do apoio], dobra do carpo em graus, dedos em graus [- abre, + fecha])
K = [(0, (0.00, 0.00, 0.0, 0.0)), (1.5, (0.05, 0.24, 40.0, 6.0)), (3.5, (-0.20, 0.44, 55.0, 10.0)),
     (5.5, (-0.85, 0.46, 15.0, -22.0)), (CONTATO_G, (-1.30, 0.42, 0.0, -14.0)), (8.5, (-1.15, 0.48, 12.0, 22.0)),
     (11, (-0.50, 0.46, 45.0, 12.0)), (13.5, (-0.08, 0.24, 22.0, 4.0)), (15, (0.00, 0.10, 6.0, 0.0))]
VAR = {"corrida": False}; ERR = []
def garra(q, lado):
    repouso_q0(); s = "E" if lado > 0 else "D"; k = "D" + s; sg = 1 if lado > 0 else -1
    dy, dz, dobra, dedo = chaves(q, K); dobra = max(0.0, dobra)
    if VAR["corrida"]: dz += 0.90
    dz = max(0.0, dz)
    mcp, phi, phid = M.alvo_pata(k, dy, dz, 0.0, math.radians(dobra))
    e, ext = M.ik(k, mcp, phi, phid + math.radians(dedo)); ERR.append(e)
    cab = chaves(q, [(0, 0.0), (3, 1.0), (10, 1.0), (15, 0.0)])
    girar("Pescoco1", "X", 6 * cab); girar("Pescoco2", "X", 4 * cab); girar("Pescoco1", "Z", 7 * sg * cab); girar("Cabeca", "X", 4 * cab)
    girar("Mandibula", "X", 16 * chaves(q, [(0, 0.0), (3, 1.0), (9, 1.0), (13, 0.0)]))
    for o in ("Orelha_E", "Orelha_D"): girar(o, "X", -26 * cab)
    mira = chaves(q, [(0, 0.0), (2, 0.40), (11, 0.40), (15, 0.0)])
    reflexo = chaves(q, [(0, 0.0), (CONTATO_G - 0.5, 0.0), (CONTATO_G, 0.6), (CONTATO_G + 1.5, 0.0), (15, 0.0)])
    olhos(max(mira, reflexo), max(0.8 * mira, 0.8 * reflexo))
def gravar_parcial(nome, n, fn, ossos):
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); VAL = []
    for q in range(n + 1):
        fn(q); VAL.append({o: P[o].rotation_quaternion.copy() for o in ossos})
    ARM.animation_data.action = acn; prev = {}
    for q, vals in enumerate(VAL):
        for o in ossos:
            rq = vals[o]
            if o in prev and rq.dot(prev[o]) < 0: rq = -rq
            prev[o] = rq; P[o].rotation_quaternion = rq; P[o].keyframe_insert("rotation_quaternion", frame=q, group=o)
    acn.use_fake_user = True; acn.frame_range = (0, n); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
REL = json.load(open(os.path.join(SRC, "ataque_v43.json"))); REL["versao"] = "v43 r5 (garras); mordidas = r4"
for corr in (False,):          # r5b: _Corrida passa a ser sincronizada por fase (abaixo)
    VAR["corrida"] = corr; suf = "_Corrida" if corr else ""
    for nome, lado in (("GarraE", 1), ("GarraD", -1)):
        ossos = CABECA + PATA["E" if lado > 0 else "D"]
        gravar_parcial(nome + suf, N, lambda q, l=lado: garra(q, l), ossos)
        REL["acoes"][nome + suf] = {"quadros": N, "parcial": True, "ossos": ossos, "marcadores_s": {"Contato": round(CONTATO_G / 30, 3)},
                                    **({"variante": "Corrida (servidor escolhe pela marcha)"} if corr else {})}
# ===================== r5b: GARRAS SINCRONIZADAS POR FASE (Andar / Trote / Corrida) =====================
# A varredura de fases (medir_garra_r5) mostrou que um golpe parcial com pose de inicio/fim FIXA nao funciona andando:
# fim seco salta 1,7-3,7 studs (a passada esta em outro ponto), entrada/saida afundam 0,3-0,7 e arrastam ate 1,2.
# Solucao: para cada marcha e lado, o golpe comeca no quadro em que aquela pata DESCOLA na passada (q0 = locomocao),
# mistura com o golpe (preparo -> contato no alvo -> recolhimento) e devolve a pata EXATAMENTE na passada no q15.
# Requer o servidor iniciar a garra nesse instante (proposta documentada; nao alterado nesta rodada).
APOIO = {}
def sola(l): return [ARM.matrix_world @ P["Dedos_" + l].tail, ARM.matrix_world @ P["Dedos_" + l].head, ARM.matrix_world @ P["Metacarpo_" + l].tail]
for pb in P: pb.matrix_basis.identity()
da_acao("Repouso", 0); APOIO = {l: [x.z for x in sola(l)] for l in ("E", "D")}
def apoiada(l): return min(x.z - a for x, a in zip(sola(l), APOIO[l])) < 0.03
def descolamento(base, l):
    nb = int(bpy.data.actions[base].frame_range[1]); est = []
    for q in range(nb):
        for pb in P: pb.matrix_basis.identity()
        da_acao(base, q); est.append(apoiada(l))
    for q in range(nb):
        if est[q] and not est[(q + 1) % nb]: return (q + 1) % nb, nb, est
    return 0, nb, est
SINC = {}
def pouso_apos_contato(base, l, f0, nb):
    """r5d: primeiro quadro q >= 9 em que a PASSADA apoia de novo essa pata (o golpe devolve a pata ali)"""
    for q in range(9, 16):
        for pb in P: pb.matrix_basis.identity()
        da_acao(base, (f0 + q) % nb)
        if apoiada(l): return q
    return 15
def garra_fase(q, lado, base, f0, nb, alt_extra, td=15):
    """r5c: mistura de POSICAO (nao de rotacao): o alvo do IK vai da pata da passada L(q) ao alvo do golpe T(q) com peso w;
    na volta a pata segue o ponto onde a passada vai apoia-la e so encosta no q15, exatamente nele (sem deslizar).
    As rotacoes so voltam a ser as da passada nos 2 ultimos quadros (onde as posicoes ja coincidem)."""
    s_ = "E" if lado > 0 else "D"; k = "D" + s_; sg = 1 if lado > 0 else -1; sup, inf, pe, dedo = PATA[s_]; ossos = PATA[s_]
    for pb in P: pb.matrix_basis.identity()
    da_acao(base, (f0 + q) % nb)
    loco = {o: P[o].rotation_quaternion.copy() for o in ossos}
    L = P[pe].tail.copy()                                                       # MCP da passada neste quadro (espaco do rig)
    yl = (P[pe].matrix.to_3x3().col[1]); phi_l = math.atan2(yl.z, yl.y) - math.atan2((M.TIP0[k] - M.MCP0[k]).z, (M.TIP0[k] - M.MCP0[k]).y)
    # r5d: a pata volta ao chao no quadro em que a passada a apoia (td), nao no q15 -> sem perda de apoio causada pelo golpe
    w = max(0.0, min(1.0, chaves(q, [(0, 0.0), (3, 1.0), (max(7.8, td - 2.5), 1.0), (td, 0.0), (15, 0.0)])))
    dy, dz, dobra, dedo_g = chaves(q, K); dz = max(0.0, dz + alt_extra); dobra = max(0.0, dobra)
    T, phi_t, phid_t = M.alvo_pata(k, dy, dz, 0.0, math.radians(dobra))
    alvo = L.lerp(T, w)
    alvo.z = max(alvo.z, L.z + 0.0)                                             # nunca abaixo da passada (que nao afunda)
    phi = phi_l + (phi_t - phi_l) * w
    e, ext = M.ik(k, alvo, phi, phid_t * w + math.radians(dedo_g) * w); ERR.append(e)
    wr = max(0.0, min(1.0, (td - q) / 2.0))                                     # rotacoes da passada so no pouso (td-2 -> td)
    for o in ossos:
        r = loco[o]; g = P[o].rotation_quaternion.copy()
        if r.dot(g) < 0: g = -g
        P[o].rotation_quaternion = r.slerp(g, wr)
    bpy.context.view_layer.update()
    # cabeca/olhos iguais ao golpe parado, por cima da pose da passada (camada: ossos da cabeca ficam com chave)
    cab = chaves(q, [(0, 0.0), (3, 1.0), (10, 1.0), (15, 0.0)])
    girar("Pescoco1", "X", 6 * cab); girar("Pescoco2", "X", 4 * cab); girar("Pescoco1", "Z", 7 * sg * cab); girar("Cabeca", "X", 4 * cab)
    girar("Mandibula", "X", 16 * chaves(q, [(0, 0.0), (3, 1.0), (9, 1.0), (13, 0.0)]))
    for o in ("Orelha_E", "Orelha_D"): girar(o, "X", -26 * cab)
    mira = chaves(q, [(0, 0.0), (2, 0.40), (11, 0.40), (15, 0.0)])
    reflexo = chaves(q, [(0, 0.0), (CONTATO_G - 0.5, 0.0), (CONTATO_G, 0.6), (CONTATO_G + 1.5, 0.0), (15, 0.0)])
    olhos(max(mira, reflexo), max(0.8 * mira, 0.8 * reflexo))
for nome in [n for n in ("GarraE_Corrida", "GarraD_Corrida") if n in bpy.data.actions]: bpy.data.actions.remove(bpy.data.actions[nome]); REL["acoes"].pop(nome, None)
for base, alt in (("Andar", 0.0), ("Trote", 0.0), ("Corrida", 0.0)):
    for nome, lado in (("GarraE", 1), ("GarraD", -1)):
        l = "E" if lado > 0 else "D"; f0, nb, est = descolamento(base, l); td = pouso_apos_contato(base, l, f0, nb)
        ossos = CABECA + PATA[l]
        # pescoco/cabeca: chave so dos ossos da cabeca; a perna e a pose da passada misturada com o golpe
        gravar_parcial(nome + "_" + base, N, lambda q, lado=lado, base=base, f0=f0, nb=nb, alt=alt, td=td: garra_fase(q, lado, base, f0, nb, alt, td), ossos)
        SINC[nome + "_" + base] = {"marcha": base, "quadro_descolamento": f0, "quadros_ciclo": nb, "inicio_s": round(f0 / 30, 3), "pouso_q": td}
        REL["acoes"][nome + "_" + base] = {"quadros": N, "parcial": True, "ossos": ossos, "marcadores_s": {"Contato": round(CONTATO_G / 30, 3)},
                                           "sincronizado": SINC[nome + "_" + base]}
REL["sincronizacao_r5b"] = SINC
print("SINC", SINC, flush=True)
REL["erro_ik_garra_r5_max"] = round(max(ERR), 4)
print("V43R5", {k: (v["quadros"], len(v["ossos"])) for k, v in REL["acoes"].items()}, "ik", REL["erro_ik_garra_r5_max"], flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "ataque_v43.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_GARRA_V43R5_OK", flush=True)
