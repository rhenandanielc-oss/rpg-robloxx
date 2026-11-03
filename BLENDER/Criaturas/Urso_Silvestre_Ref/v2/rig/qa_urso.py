"""QA de apoio, contato e deformacao dos clipes do Urso v2 (acoes FK de um CR_Urso_v2_Anim.blend). Mede:
 1) CONTATO NA SOLA no MUNDO: cada pata tem um conjunto fixo de vertices da sola (repouso z < 0,15, osso dominante da
    propria pata). O modelo e deslocado/girado como no jogo (SIMULACAO: v e omega sao parametros tecnicos desta revisao,
    nao regras). Apoio = sola a menos de 0,06 do chao. Deriva = maior distancia horizontal da sola desde o inicio do
    apoio, por intervalo inteiro de apoio (loops avaliados em 2 ciclos seguidos).
 2) CHAO: vertices abaixo de z = 0 por regiao (garra, dedo/sola, cotovelo, joelho, perna, tronco, cabeca) e profundidade.
 3) BOCA: arestas da cabeca esticadas > 3x, separadas em interior da boca (cavidade) e exterior.
 4) ESTALOS: velocidade e aceleracao angular por osso (quaternions com sinal continuo, 30 qps); picos isolados de
    aceleracao (>= 4x a mediana do osso no clipe e >= 9000 graus/s2) listados para conferencia visual.
 5) TRANSICOES: pares de clipes com mistura de 0,25 s (slerp), medindo chao e salto de pose entre fim e inicio.
Uso: blender -b <Anim.blend> -P qa_urso.py -- <saida.json> [clipes]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = os.path.abspath(A[0]); QUAIS = A[1].split(",") if len(A) > 1 else None
sc = bpy.context.scene; FPS = 30; arm = bpy.data.objects["Urso_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
for pb in PB:
    for c in pb.constraints: c.mute = True
MALHAS = [bpy.data.objects[n] for n in ("Urso_Cabeca", "Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Boca")]
PIVO = BD["Raiz"].head_local.copy()
# simulacao de deslocamento (parametros tecnicos desta revisao, NAO oficiais)
SIM = {"Andar": (3.23, 0.0), "Corrida": (17.23, 0.0), "VirarE": (0.0, 60.0), "VirarD": (0.0, -60.0)}
try:
    man = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "manifesto_clipes.json"), encoding="utf-8"))
    for k, v in man.items():
        if k in ("Andar", "Corrida") and v.get("velocidade_studs_s_PROPOSTA"): SIM[k] = (v["velocidade_studs_s_PROPOSTA"], 0.0)
        if k in ("VirarE", "VirarD") and "giro_graus_s_PROPOSTA" in v: SIM[k] = (0.0, v["giro_graus_s_PROPOSTA"])
except Exception: man = {}
VPERF = {k: v["v_perfil_PARAMETRO"] for k, v in man.items() if "v_perfil_PARAMETRO" in v}       # arrancada/frenagem: v(t) por quadro
def regiao(nome, z0, y0):
    if nome.startswith(("Dedos",)): return "garra/dedo"
    if nome.startswith(("Mao", "Pe")) and not nome.startswith("Pelve") and not nome.startswith("Pesc"): return "sola"
    if nome.startswith("Antebraco"): return "cotovelo/antebraco" if z0 > 1.2 else "punho"
    if nome.startswith("Braco"): return "cotovelo/braco"
    if nome.startswith("Canela"): return "joelho/canela" if z0 > 1.2 else "calcanhar"
    if nome.startswith("Coxa"): return "joelho/coxa"
    if nome.startswith(("Cabeca", "Mandibula", "Orelha", "Pescoco")): return "cabeca/pescoco"
    return "tronco"
INFO = {}
for o in MALHAS:
    nomes = {g.index: g.name for g in o.vertex_groups}; n = len(o.data.vertices)
    c0 = np.empty(n * 3); o.data.vertices.foreach_get("co", c0); c0 = c0.reshape(-1, 3)
    dom = []
    for v in o.data.vertices:
        g = max(v.groups, key=lambda g: g.weight) if v.groups else None; dom.append(nomes[g.group] if g else "?")
    reg = np.array([regiao(dom[i], c0[i, 2], c0[i, 1]) for i in range(n)])
    e = np.empty(len(o.data.edges) * 2, dtype=np.int64); o.data.edges.foreach_get("vertices", e); e = e.reshape(-1, 2)
    INFO[o.name] = dict(c0=c0, dom=np.array(dom), reg=reg, e=e, l0=np.linalg.norm(c0[e[:, 0]] - c0[e[:, 1]], axis=1))
cab = INFO["Urso_Cabeca"]; c0 = cab["c0"]
meio = (c0[cab["e"][:, 0]] + c0[cab["e"][:, 1]]) / 2
cab["boca_int"] = (meio[:, 1] < -4.55) & (meio[:, 1] > -6.0) & (np.abs(meio[:, 0]) < 0.32) & (meio[:, 2] > 5.85) & (meio[:, 2] < 6.45)
SOLAS = {}
for k, lado, frente in (("MaoE", "E", True), ("MaoD", "D", True), ("PeE", "E", False), ("PeD", "D", False)):
    ids = []
    for o in MALHAS[1:3]:
        I = INFO[o.name]; d = I["dom"]
        ok = (I["c0"][:, 2] < 0.15) & np.array([nm.endswith(lado) and ((nm.startswith(("Mao", "DedosE", "DedosD")) and frente) or (nm.startswith(("Pe", "DedosPe")) and not nm.startswith("Pelve") and not frente)) for nm in d])
        ids.append((o.name, np.nonzero(ok)[0]))
    SOLAS[k] = ids
def avaliar():
    """posicoes deformadas (mundo do modelo) de todas as malhas"""
    dg = bpy.context.evaluated_depsgraph_get(); P = {}
    for o in MALHAS:
        ev = o.evaluated_get(dg); m = ev.to_mesh(); c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); P[o.name] = c.reshape(-1, 3).copy(); ev.to_mesh_clear()
    return P
DESLOC = {}
def mundo(p, t, v, w):
    """aplica o deslocamento simulado do jogo: anda -Y (v studs/s ou o perfil v(t) do clipe) e gira w graus/s no pivo (Raiz)"""
    ang = math.radians(w) * t; ca, sa = math.cos(ang), math.sin(ang)
    q = p - np.array(PIVO); q[:, 1] -= DESLOC["s"](t) if "s" in DESLOC else v * t
    x = q[:, 0] * ca - q[:, 1] * sa; y = q[:, 0] * sa + q[:, 1] * ca
    return np.stack([x + PIVO.x, y + PIVO.y, q[:, 2] + PIVO.z], axis=1)
def quats_do_quadro():
    return {pb.name: pb.rotation_quaternion.copy() for pb in PB}
def pose_aplicar(act, f):
    arm.animation_data.action = act; sc.frame_set(int(f))
res = {"simulacao_parametros_tecnicos": {k: {"v_studs_s": v, "giro_graus_s": w} for k, (v, w) in SIM.items()}, "clipes": {}, "transicoes": {}}
if not arm.animation_data: arm.animation_data_create()
ACOES = {a.name[5:]: a for a in bpy.data.actions if a.name.startswith("Urso_")}
for nome, act in ACOES.items():
    if QUAIS and nome not in QUAIS: continue
    f0, f1 = [int(x) for x in act.frame_range]; loop = bool(act.get("loop", False)); nq = f1 - f0 + 1
    v, w = SIM.get(nome, (0.0, 0.0)); DESLOC.clear()
    if nome in VPERF:                                                        # integra o perfil v(t) (quadro a quadro)
        vp = VPERF[nome]; acum = [0.0]
        for q_ in range(1, len(vp)): acum.append(acum[-1] + 0.5 * (vp[q_] + vp[q_ - 1]) / FPS)
        DESLOC["s"] = lambda tt, acum=acum: acum[min(len(acum) - 1, int(round(tt * FPS)))]
    seq = list(range(f0, f1 + 1)) * (2 if loop else 1)
    sola_pos = {k: [] for k in SOLAS}; chao = {}; boca_max = (0, 0); quats = []
    cache = {}
    for i, f in enumerate(seq):
        if f not in cache:
            pose_aplicar(act, f); P = avaliar(); cache[f] = (P, quats_do_quadro(), {k: np.array(PB[k].head[:]) for k in SOLAS})
        P, qd, cab_ossos = cache[f]; t = i / FPS
        if i < nq:
            quats.append(qd)
            for o in MALHAS:
                z = P[o.name][:, 2]; abaixo = z < 0
                for r_ in np.unique(INFO[o.name]["reg"][abaixo]):
                    s = abaixo & (INFO[o.name]["reg"] == r_); prof = float(-z[s].min())
                    a_ = chao.setdefault(r_, [0.0, 0, None]);
                    if prof > a_[0]: a_[0] = prof; a_[2] = int(f)
                    a_[1] = max(a_[1], int(s.sum()))
            I = INFO["Urso_Cabeca"]; c = P["Urso_Cabeca"]; l1 = np.linalg.norm(c[I["e"][:, 0]] - c[I["e"][:, 1]], axis=1); r = l1 / np.maximum(I["l0"], 1e-6)
            ruim = r > 3; boca_max = (max(boca_max[0], int((ruim & I["boca_int"]).sum())), max(boca_max[1], int((ruim & ~I["boca_int"]).sum())))
        for k, ids in SOLAS.items():
            pts = np.concatenate([P[o][idx] for o, idx in ids]); W_ = mundo(pts, t, v, w)
            osso = mundo(np.array([cab_ossos[k]]), t, v, w)[0]                  # cabeca do osso da pata (punho/calcanhar)
            sola_pos[k].append((float(pts[:, 2].min()), W_.mean(axis=0), osso))
    if os.environ.get("QA_SERIE") == nome:                                 # depuracao: serie quadro a quadro
        json.dump({k: [(round(z_, 3), [round(float(c_), 3) for c_ in w_[:2]], [round(float(c_), 3) for c_ in o_[:2]]) for z_, w_, o_ in s] for k, s in sola_pos.items()},
                  open(SAIDA.replace(".json", "_serie_%s.json" % nome), "w"))
    # deriva por intervalo de apoio (sola < 0,06 do chao)
    deriva = {}
    for k, s in sola_pos.items():
        pior = 0.0; pior_o = 0.0; ini = None; ini_o = None; apoios = 0
        for i, (zmin, wpos, opos) in enumerate(s):
            if zmin < 0.02:                                               # contato: sola a ate 0,02 do chao
                if ini is None: ini = wpos; ini_o = opos; apoios += 1
                else:
                    pior = max(pior, float(np.hypot(*(wpos[:2] - ini[:2])))); pior_o = max(pior_o, float(np.hypot(*(opos[:2] - ini_o[:2]))))
            else: ini = None
        deriva[k] = {"deriva_max_studs": round(pior, 3), "deriva_osso_studs": round(pior_o, 3), "apoios": apoios}
    # estalos: velocidade/aceleracao angular por osso
    picos = []; vel_max = {}
    for b in [pb.name for pb in PB]:
        qs = [q[b] for q in quats]
        for j in range(1, len(qs)):
            if qs[j].dot(qs[j - 1]) < 0: qs[j] = -qs[j]
        ws = [math.degrees(qs[j - 1].rotation_difference(qs[j]).angle) * FPS for j in range(1, len(qs))]
        if loop and len(qs) > 2: ws.append(math.degrees(qs[-1].rotation_difference(qs[0] if qs[-1].dot(qs[0]) >= 0 else -qs[0]).angle) * FPS)
        if not ws: continue
        vel_max[b] = round(max(ws), 1)
        acs = [abs(ws[j] - ws[j - 1]) * FPS for j in range(1, len(ws))]
        if not acs: continue
        med = float(np.median(acs)) + 1e-6
        for j, a_ in enumerate(acs):
            if a_ >= 9000 and a_ >= 4 * med: picos.append((b, f0 + j + 1, round(a_), round(ws[j], 1), round(ws[j + 1] if j + 1 < len(ws) else 0, 1)))
    picos.sort(key=lambda x: -x[2])
    res["clipes"][nome] = {"loop": loop, "quadros": nq, "sim_v": v, "sim_giro": w, "sola_mundo": deriva,
                           "chao_por_regiao": {r_: {"prof_max": round(a_[0], 3), "verts_max": a_[1], "quadro": a_[2]} for r_, a_ in sorted(chao.items())},
                           "boca_arestas_3x": {"interior": boca_max[0], "exterior": boca_max[1]}, "picos_aceleracao": picos[:12],
                           "vel_angular_max_graus_s": dict(sorted(vel_max.items(), key=lambda x: -x[1])[:6])}
    print("QA", nome, json.dumps({"sola": {k: (v_["deriva_max_studs"], v_["deriva_osso_studs"]) for k, v_ in deriva.items()}, "chao": {r_: round(a_[0], 3) for r_, a_ in chao.items()},
          "boca": boca_max, "picos": len(picos)}, ensure_ascii=False), flush=True)
# ------------------------------------------------------------------ transicoes (mistura 0,25 s por slerp, como um fade do Animator)
PARES = [("Repouso", "Andar"), ("Andar", "Repouso"), ("Andar", "Corrida"), ("Corrida", "Andar"), ("Corrida", "Frenagem"), ("Frenagem", "Repouso"),
         ("Repouso", "Arrancada"), ("Arrancada", "Corrida"), ("Repouso", "VirarE"), ("VirarE", "Repouso"), ("Repouso", "VirarD"), ("VirarD", "Repouso"),
         ("Andar", "VirarE"), ("Repouso", "Sentar"), ("Sentar", "LevantarSentado"), ("LevantarSentado", "Repouso"),
         ("Repouso", "Deitar"), ("Deitar", "LevantarDeitado"), ("LevantarDeitado", "Repouso")]
def pose_de(act, f):
    pose_aplicar(act, f); return {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in PB}
for a_n, b_n in PARES:
    if a_n not in ACOES or b_n not in ACOES: continue
    if QUAIS and not (a_n in QUAIS or b_n in QUAIS): continue
    a, b = ACOES[a_n], ACOES[b_n]; fa = int(a.frame_range[1]); fb = int(b.frame_range[0])
    pa, pb_ = pose_de(a, fa), pose_de(b, fb)
    salto = max(math.degrees(pa[k][0].rotation_difference(pb_[k][0]).angle) for k in pa)
    salto_raiz = (pa["Raiz"][1] - pb_["Raiz"][1]).length
    pior_chao = {}; arm.animation_data.action = None
    for i in range(9):                                            # 0,25 s de mistura em 9 amostras
        s = i / 8
        for pb in PB:
            q0, l0 = pa[pb.name]; q1, l1 = pb_[pb.name]; pb.rotation_quaternion = q0.slerp(q1, s); pb.location = l0.lerp(l1, s)
        bpy.context.view_layer.update(); P = avaliar()
        for o in MALHAS:
            z = P[o.name][:, 2]; ab = z < 0
            for r_ in np.unique(INFO[o.name]["reg"][ab]):
                pior_chao[r_] = max(pior_chao.get(r_, 0.0), float(-z[ab & (INFO[o.name]["reg"] == r_)].min()))
    res["transicoes"]["%s->%s" % (a_n, b_n)] = {"salto_pose_graus": round(salto, 1), "salto_raiz_studs": round(salto_raiz, 3), "chao_por_regiao": {k: round(v_, 3) for k, v_ in sorted(pior_chao.items())}}
    print("TRANS", a_n, "->", b_n, res["transicoes"]["%s->%s" % (a_n, b_n)], flush=True)
# transicoes com fase sincronizada (mesmo periodo e mesmas fases: Andar <-> VirarE/D): mistura no MESMO tempo normalizado
for a_n, b_n in (("Andar", "VirarE"), ("Andar", "VirarD"), ("VirarE", "Andar")):
    if a_n not in ACOES or b_n not in ACOES: continue
    a, b = ACOES[a_n], ACOES[b_n]; pior = 0.0
    for f_ in range(int(a.frame_range[0]), int(a.frame_range[1]) + 1, 2):
        pa, pb_ = pose_de(a, f_), pose_de(b, f_); arm.animation_data.action = None
        for pb in PB: q0, l0 = pa[pb.name]; q1, l1 = pb_[pb.name]; pb.rotation_quaternion = q0.slerp(q1, 0.5); pb.location = l0.lerp(l1, 0.5)
        bpy.context.view_layer.update(); P = avaliar()
        for o in MALHAS: pior = max(pior, float(-P[o.name][:, 2].min()))
    res["transicoes"]["%s->%s (fase sincronizada, meio da mistura)" % (a_n, b_n)] = {"chao_max": round(pior, 3)}
    print("TRANS_SINC", a_n, "->", b_n, round(pior, 3), flush=True)
json.dump(res, open(SAIDA, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("QA_OK", SAIDA)
