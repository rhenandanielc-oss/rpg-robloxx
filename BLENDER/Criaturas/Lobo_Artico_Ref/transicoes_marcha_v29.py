"""v29 = copia da v28 que REGERA SO TroteParaAndar e CorridaParaTrote (as outras 10 acoes vem intactas do blend da v28):
- TroteParaAndar: plano IGUAL ao da v28 (mesmos R, t_a; quadros 0..75 identicos aos da v28), mas a acao termina no PRIMEIRO q0 do
  Andar depois da CONVERGENCIA (pose igual ao Andar: posicao/eixo de todos os ossos <= 2e-6 stud dali ate o fim do plano gerado).
  Contrato de saida mantido (Andar q0, continua no q1); corta so o ciclo de Andar constante a mais que a v28 anexava.
- CorridaParaTrote: o APOIO nao estica alem do comprimento natural da marcha intermediaria (v*beta/cadencia no meio do apoio, folga
  'apoio_max_rel'): a mudanca de fase das patas que atrasam (TE +0,25, DE +0,35) passa a ser absorvida no BALANCO (balanco mais
  longo), nao num apoio comprido (que levava a TE a tocar muito a frente e travar a perna reta no ar). Toque continua centrado e a
  pata plantada recua exatamente integral(v). Apoio cortado: fracao do apoio (rolamento) pela distancia.
Uso: blender -b anim_v28/CR_LoboArtico_Anim.blend -P transicoes_marcha_v29.py -- <dir_saida>
-------------------------------------------------------------------------------------------------------------------------------
L2b, 3o bloco (v28): TROCAS DE MARCHA AndarParaTrote, TroteParaAndar, TroteParaCorrida, CorridaParaTrote (acoes de uma vez), sobre
copia da anim_v27 (so lida; saida <dir>). As 8 acoes anteriores ficam INTACTAS.
CONTRATO: clipe NO LUGAR (Raiz fixa, frente -Y); IK analitico de 2 ossos gravado em FK (marcha_v21; rolamento v24: pivo a 0,8 do
osso dos dedos descido 0,25/0,20, dedos para a almofada); sem constraints. Cada transicao comeca IGUAL ao q0 da marcha de origem e
termina IGUAL ao q0 da marcha de destino (entra no fim de um ciclo da origem, sai para o q1 do destino). Deslocamento = CURVA
nao uniforme gravada em marchas_v28.json (X = -integral de v por quadro).
Gerador = UMA marcha que se transforma: peso s(t) (0 = origem, 1 = destino, rampa suave de duracao R a partir de t_a); todos os
parametros sao interpolados por s: velocidade v, cadencia 1/T, fracao de apoio beta, fase de cada pata (pelo caminho mais curto:
Andar -> Trote as traseiras adiantam 0,25 de ciclo; Trote -> Corrida DD +0,4, TE +0,1, TD -0,32), centro do apoio, altura do
balanco, dobra do carpo/jarrete, rolamento. Relogio de fase theta = integral(1/T). Pata no APOIO recua no referencial do corpo
exatamente integral(v) (sem deslize por construcao), toque centrado no centro do apoio; balanco min-jerk do ponto de saida ao
proximo toque (mesmas formulas da pata_marcha: com s fixo o gerador reproduz a marcha). O plano comeca 2 ciclos ANTES do q0 (so
origem) e segue 2 ciclos depois do fim (so destino): as pontas ficam exatas. Corpo = pose dos ossos que nao sao pernas lida dos
proprios clipes de origem e destino na fase theta (quadro fracionario) e misturada por s (slerp; cabeca/pescoco e cauda com
atraso leve). Tempo extra em s = 1 escolhido (bisseccao em t_a) para theta terminar num inteiro num quadro inteiro.
Uso: blender -b anim_v27/CR_LoboArtico_Anim.blend -P transicoes_marcha_v28.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix, Quaternion
import marcha_v21 as M
import marchas_v28 as MV
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); G = MV.marchas(CJ)
FPS = M.FPS; ARM = M.ARM; P = M.P; sc = bpy.context.scene; DT = 1.0 / 600
PAR = {"AndarParaTrote": {"R": 1.2}, "TroteParaAndar": {"R": 1.3, "saida": "q0_apos_convergencia"}, "TroteParaCorrida": {"R": 1.0},
       "CorridaParaTrote": {"R": 1.1, "apoio_max_rel": 1.05},
       "atraso_cabeca_s": 0.08, "atraso_cauda_s": 0.14, "pre_ciclos": 2.0, "pos_ciclos": 2.0, "cauda_min_ciclos": 1.5,
       "tol_convergencia_stud": 2e-6, "tol_visual_stud": 1e-3}
if os.environ.get("AJUSTE_V29"): PAR.update(json.loads(os.environ["AJUSTE_V29"]))
ACOES_V29 = ("TroteParaAndar", "CorridaParaTrote"); TJ28 = json.load(open(os.path.join(SRC, "marchas_v28.json")))
ATUAL = None                                                            # acao em geracao (parametros por acao)
LEG = {n for c in M.PATAS.values() for n in c}; CABECA = {"Pescoco1", "Pescoco2", "Cabeca", "Orelha_E", "Orelha_D"}; CAUDA = {"Cauda1", "Cauda2", "Cauda3", "Cauda4"}
# ---------------------------------------------------------------- rolamento da v24 (igual a clipes_v24.alvo_v24 'grade')
ARM.animation_data.action = None
for pb in P: pb.matrix_basis.identity()
bpy.context.view_layer.update()
C_ = bpy.data.objects["LOW_Corpo"]; me = C_.data; gn = {g.index: g.name for g in C_.vertex_groups}; SOLA = {}
for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"]):
    ids = [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8]; zs = min(me.vertices[i].co.z for i in ids)
    pad = [me.vertices[i].co for i in ids if me.vertices[i].co.z < zs + 0.03 and max(((gn[g.group], g.weight) for g in me.vertices[i].groups), key=lambda t: t[1])[0] == M.PATAS[k][3]]
    pc = sum(pad, V()) / len(pad); SOLA[k] = {"z_sola": zs, "almofada": V((pc.x, pc.y, zs))}
def alvo(k, dy, dz, rolo, dobra):
    mcp = M.MCP0[k] + V((0, dy, dz)); tv = M.TIP0[k] - M.MCP0[k]; Cf = mcp + 0.8 * tv; lp = 0.20 if k[0] == "D" else 0.25
    Cg = Cf - V((0, 0, lp * (Cf.z - (SOLA[k]["z_sola"] + dz)))); m_ef = Cg + Matrix.Rotation(rolo, 3, M.X) @ (mcp - Cg)
    pv0 = SOLA[k]["almofada"] - M.MCP0[k]; nd = (mcp + pv0) - m_ef
    return m_ef, rolo + dobra, math.atan2(nd.z, nd.y) - math.atan2(pv0.z, pv0.y) + 0.45 * dobra
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def suave5(x): x = max(0.0, min(1.0, x)); return x * x * x * (10 - 15 * x + 6 * x * x)
def mj(w): return suave5(w)
def lerp(a, b, s): return a + (b - a) * s
def delta_fase(a, b): d = (b - a) % 1.0; return d - 1.0 if d > 0.5 else d
def deslocamento_global(GA, GB):
    """deslocamento global g das fases (o destino e alcancado em theta = inteiro + g): escolhe g (passo 0,05) que minimiza a maior
    mudanca de fase de uma pata (depois a soma); mudancas pequenas = apoios que nao esticam nem encurtam muito"""
    best = None
    for j in range(-10, 10):
        g = j / 20; d = {k: delta_fase(GA["fases"][k], GB["fases"][k] + g) for k in M.PATAS}
        c = (round(max(abs(x) for x in d.values()), 6), round(sum(abs(x) for x in d.values()), 6), abs(g))
        if best is None or c < best[0]: best = (c, g, d)
    return best[1], best[2]
def params(GA, GB, s):
    """parametros da marcha intermediaria com peso s"""
    vA, vB = GA["v_studs_s"], GB["v_studs_s"]; g, dl = deslocamento_global(GA, GB)
    return {"v": lerp(vA, vB, s), "cad": lerp(1 / GA["T"], 1 / GB["T"], s), "beta": lerp(GA["apoio"], GB["apoio"], s),
            "f": {k: GA["fases"][k] + dl[k] * s for k in M.PATAS}, "g": g,
            "c": {k: lerp(GA["centro"][k], GB["centro"][k], s) for k in M.PATAS},
            "h": {e: lerp(GA["altura"][e], GB["altura"][e], s) for e in "DT"}, "dob": {e: lerp(GA["dobra_graus"][e], GB["dobra_graus"][e], s) for e in "DT"},
            "roll": math.radians(lerp(GA["rolamento_graus"], GB["rolamento_graus"], s)), "ri": lerp(GA.get("rolo_ini", 0.72), GB.get("rolo_ini", 0.72), s)}
def plano(GA, GB, ta, R, dur):
    pre = PAR["pre_ciclos"] * GA["T"]; pos = PAR["pos_ciclos"] * GB["T"]; N0 = int(round(pre / DT)); N = N0 + int(round((dur + pos) / DT))
    ts = [(i - N0) * DT for i in range(N + 1)]; ss = [suave5((t - ta) / R) for t in ts]; PP = [params(GA, GB, s) for s in ss]
    th = [ts[0] / GA["T"]]; Xs = [0.0]
    for i in range(1, N + 1):
        th.append(th[-1] + 0.5 * (PP[i]["cad"] + PP[i - 1]["cad"]) * DT); Xs.append(Xs[-1] - 0.5 * (PP[i]["v"] + PP[i - 1]["v"]) * DT)
    x0 = Xs[N0]; Xs = [x - x0 for x in Xs]
    def Xi(p): p = max(0.0, min(float(N), p)); i0 = int(math.floor(p)); i1 = min(N, i0 + 1); return Xs[i0] + (p - i0) * (Xs[i1] - Xs[i0])
    D = lambda p0, p1: -(Xi(p1) - Xi(p0))
    ap = {}
    for k in M.PATAS:
        g = [th[i] - PP[i]["f"][k] for i in range(N + 1)]; est = [(g[i] % 1.0) < PP[i]["beta"] for i in range(N + 1)]
        segs = []; i = 0
        while i <= N:
            if est[i]:
                j = i
                while j + 1 <= N and est[j + 1]: j += 1
                segs.append([float(i), float(j)]); i = j + 1
            else: i += 1
        for sg in segs:                                                    # limites EXATOS (interpolados)
            i, j = int(sg[0]), int(sg[1])
            if i > 0:
                m = math.floor(g[i]); a0, a1 = g[i - 1] - m, g[i] - m; sg[0] = (i - 1) + (0 - a0) / max(1e-12, a1 - a0)
            if j < N:
                m = math.floor(g[j]); h0 = g[j] - m - PP[j]["beta"]; h1 = g[j + 1] - m - PP[j + 1]["beta"]; sg[1] = j + (-h0) / max(1e-12, h1 - h0)
        ap[k] = [sg for sg in segs if sg[0] > 0 and sg[1] < N]          # so apoios completos (as pontas do plano ficam fora do clipe)
    cortes = {k: [] for k in M.PATAS}; rel = PAR.get(ATUAL, {}).get("apoio_max_rel")
    if rel:                                                            # v29: apoio nao estica alem do natural (fase absorvida no balanco)
        for k in M.PATAS:
            for sg in ap[k]:
                if sg[0] < N0 + 1.0: continue                              # apoio em curso no q0: igual a origem
                mid = int(round(0.5 * (sg[0] + sg[1]))); pr = PP[mid]; Lmax = rel * pr["v"] * pr["beta"] / pr["cad"]; L = D(sg[0], sg[1])
                if L > Lmax:
                    lo, hi = sg[0], sg[1]
                    for _ in range(50):
                        md = 0.5 * (lo + hi)
                        if D(sg[0], md) > Lmax: hi = md
                        else: lo = md
                    cortes[k].append({"inicio": sg[0], "fim_fase": sg[1], "fim": lo, "comprimento_fase": round(L, 4), "comprimento": round(D(sg[0], lo), 4)}); sg[1] = lo
    return {"GA": GA, "t": ts, "s": ss, "P": PP, "teta": th, "X": Xs, "D": D, "N": N, "N0": N0, "apoios": ap, "cortes": cortes}
def pata_em(PL, k, i):
    segs = PL["apoios"][k]; D = PL["D"]; PP = PL["P"]
    GA = PL["GA"]
    def toque(sg):
        if sg[0] < PL["N0"] + 1.0: return GA["centro"][k] - GA["D"] * GA["apoio"] / 2   # apoio em curso no q0: toque IGUAL ao da origem
        mid = int(round(0.5 * (sg[0] + sg[1]))); return PP[mid]["c"][k] - D(sg[0], sg[1]) / 2
    for idx, sg in enumerate(segs):
        if sg[0] <= i <= sg[1]:
            pr = PP[i]; sp = max(0.0, min(1.0, ((PL["teta"][i] - pr["f"][k]) % 1.0) / pr["beta"]))   # fracao do apoio pela FASE (= pata_marcha)
            if sp > 0.999 and i - sg[0] < 0.5 * (sg[1] - sg[0]): sp = 0.0
            if any(abs(c["inicio"] - sg[0]) < 1e-9 for c in PL["cortes"][k]): sp = D(sg[0], i) / max(1e-9, D(sg[0], sg[1]))   # v29: apoio cortado
            return toque(sg) + D(sg[0], i), 0.0, pr["roll"] * suave((sp - pr["ri"]) / (1 - pr["ri"])), 0.0, True
        if idx + 1 < len(segs) and sg[1] < i < segs[idx + 1][0]:
            a0, a1 = sg[1], segs[idx + 1][0]; w = (i - a0) / (a1 - a0); y0 = toque(sg) + D(sg[0], sg[1]); y1 = toque(segs[idx + 1]); pr = PP[i]
            rl = PP[int(math.floor(a0))]["roll"]; N0 = PL["N0"]
            if a0 < N0 < a1 and i >= N0:                                   # balanco em curso no q0: continua o da ORIGEM (igual no q0)
                swA = (1 - GA["apoio"]) * GA["T"] / DT; w0 = (N0 - a0) / swA; te = a1 - N0; tau = i - N0
                cq = (1 - w0 - te / swA) / (te * te); w = w0 + tau / swA + cq * tau * tau   # mesma velocidade de w no q0 (sem tranco), chega a 1 no toque
                y1A = GA["centro"][k] - GA["D"] * GA["apoio"] / 2; yA = y0 + (y1A - y0) * mj(w)
                yy = yA + (y1 - y1A) * suave5((w - w0) / max(1e-9, 1 - w0))   # correcao do toque entra com velocidade 0 (sem tranco)
            else: yy = y0 + (y1 - y0) * mj(w)
            return (yy, M.altura_balanco(pr["h"][k[0]], w), rl * (1 - suave((w - 0.2) / 0.4)),
                    math.radians(pr["dob"][k[0]]) * math.sin(math.pi * w) ** 1.5 * (1 - suave((w - 0.7) / 0.3)), False)
    raise RuntimeError("pata %s sem fase na amostra %d" % (k, i))
# ---------------------------------------------------------------- corpo lido dos clipes (ossos que nao sao pernas)
CORPO = [pb.name for pb in P if pb.name not in LEG]
def ler_corpo(nome, fr):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    f0 = int(math.floor(fr)); sc.frame_set(f0, subframe=fr - f0)
    r = ({n: P[n].rotation_quaternion.copy().normalized() for n in CORPO}, P["Quadril"].location.copy()); return r
def montar(nA, nB, PL, i, cacheA, cacheB):
    t = PL["t"][i]; th = PL["teta"][i]; GA, GB = G[nA], G[nB]
    frA = (th % 1.0) * MV.NQ[nA]; frB = ((th - PL["P"][i]["g"]) % 1.0) * MV.NQ[nB]
    ca = cacheA.setdefault(round(frA, 6), ler_corpo(nA, frA)); cb = cacheB.setdefault(round(frB, 6), ler_corpo(nB, frB)); ARM.animation_data.action = None
    def s_osso(n):
        lag = PAR["atraso_cabeca_s"] if n in CABECA else (PAR["atraso_cauda_s"] if n in CAUDA else 0.0)
        j = max(0, i - int(round(lag / DT))); return PL["s"][j]
    for pb in P: pb.matrix_basis.identity()
    for n in CORPO:
        qa, qb = ca[0][n], cb[0][n]
        if qa.dot(qb) < 0: qb = -qb
        P[n].rotation_quaternion = qa.slerp(qb, s_osso(n))
    P["Quadril"].location = ca[1].lerp(cb[1], s_osso("Quadril")); bpy.context.view_layer.update()
    err = 0.0; ext = {}; est = {}; errs = {}
    for k in M.PATAS:
        dy, dz, rolo, dobra, ap = pata_em(PL, k, i); m_ef, phi, phd = alvo(k, dy, dz, rolo, dobra); e, x = M.ik(k, m_ef, phi, phd); err = max(err, e); ext[k] = x; est[k] = ap; errs[k] = e
        if os.environ.get("DBG_V28") and e > 0.01: print("DBG", nA, nB, k, "t", round(t, 3), "s", round(PL["s"][i], 3), "apoio", ap, "dy", round(dy, 3), "dz", round(dz, 3), "erro", round(e, 3), flush=True)
    for c in M.PATAS.values():
        for n in c: P[n].location = (0, 0, 0)
    bpy.context.view_layer.update(); return err, ext, est, errs
def teta_fim(GA, GB, ta, R, t_fim):
    """theta em t_fim (integracao analitica-numerica, igual ao plano)"""
    n = int(round(t_fim / DT)); th = 0.0; cp = params(GA, GB, suave5((0 - ta) / R))["cad"]
    for i in range(1, n + 1):
        c = params(GA, GB, suave5((i * DT - ta) / R))["cad"]; th += 0.5 * (c + cp) * DT; cp = c
    return th
REL = {"parametros": PAR, "fps": FPS, "acoes": dict(TJ28["acoes"]), "versao_por_acao": {n: ("v29" if n in ACOES_V29 else "v28") for n in MV.TRANS}}
def pose_destino(nB, fr):
    ac = bpy.data.actions[nB]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    f0 = int(math.floor(fr)); sc.frame_set(f0, subframe=fr - f0)
    r = ({pb.name: pb.rotation_quaternion.copy().normalized() for pb in P}, P["Quadril"].location.copy()); ARM.animation_data.action = None; return r
def mats_val(vals):
    ARM.animation_data.action = None
    for pb in P: pb.rotation_quaternion, pb.location = vals[pb.name]
    bpy.context.view_layer.update(); return {pb.name: pb.matrix.copy() for pb in P}
def mats_destino(nB, q):
    ac = bpy.data.actions[nB]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); r = {pb.name: pb.matrix.copy() for pb in P}; ARM.animation_data.action = None; return r
def dif_mats(A, B):                                                     # stud: posicao da cabeca do osso + eixo Y (comprimento 1)
    return max((A[n].translation - B[n].translation).length + (A[n].col[1].xyz - B[n].col[1].xyz).length for n in A)
def dif_pose(vals, ref):
    da = max(math.degrees(2 * math.acos(min(1.0, abs(vals[n][0].normalized().dot(ref[0][n]))))) for n in ref[0]); return da, (vals["Quadril"][1] - ref[1]).length
for pb in P: pb.rotation_mode = "QUATERNION"
for nome, (nA, nB) in MV.TRANS.items():
    if nome not in ACOES_V29: continue
    ATUAL = nome; GA, GB = G[nA], G[nB]; R = PAR[nome]["R"]
    # fim: theta inteiro (= q0 do destino) num quadro inteiro. Sem atraso, acha o inteiro K depois de cauda_min_ciclos em s = 1 e o
    # quadro mais proximo; o pequeno erro de fase e corrigido com o atraso t_a da rampa (bisseccao; t_a < 0,5 s)
    g_, _ = deslocamento_global(GA, GB); t1 = R + PAR["cauda_min_ciclos"] * GB["T"]; th1 = teta_fim(GA, GB, 0.0, R, t1); K = math.ceil(th1 - g_) + g_; tfx = t1 + (K - th1) * GB["T"]
    acelera = GB["T"] < GA["T"]; nq = int(math.ceil(tfx * FPS - 1e-9)) if acelera else int(math.floor(tfx * FPS + 1e-9)); tf = nq / FPS
    f0 = teta_fim(GA, GB, 0.0, R, tf); lo, hi = 0.0, 0.6
    if abs(f0 - K) < 1e-6: hi = 0.0
    else: assert (teta_fim(GA, GB, hi, R, tf) - K) * (f0 - K) <= 0, (nome, f0, K)
    for _ in range(40 if hi > 0 else 0):
        md = 0.5 * (lo + hi); fm = teta_fim(GA, GB, md, R, tf)
        if (fm - K) * (f0 - K) > 0: lo = md
        else: hi = md
    ta = 0.5 * (lo + hi); PL = plano(GA, GB, ta, R, tf)
    idx = [PL["N0"] + int(round(q / FPS / DT)) for q in range(nq + 1)]
    print("V29", nome, "nq", nq, "t_a", round(ta, 4), "teta_fim", round(PL["teta"][idx[-1]], 6), flush=True)
    VAL = []; EQ = []; XQ = []; EST = {k: [] for k in M.PATAS}; cA, cB = {}, {}
    for i in idx:
        e, ext, est, ers = montar(nA, nB, PL, i, cA, cB); EQ.append(ers); XQ.append(ext)
        for k in M.PATAS: EST[k].append(est[k])
        VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    saida_q = 0; conv_info = None
    if PAR[nome].get("saida") == "q0_apos_convergencia":               # v29: corta no 1o q0 do destino depois da convergencia (pose = destino)
        g_d = PL["P"][idx[-1]]["g"]; difs = []
        for qi, i in enumerate(idx):
            frB = ((PL["teta"][i] - g_d) % 1.0) * MV.NQ[nB]; assert abs(frB - round(frB)) < 1e-4 or PL["s"][i] < 1.0, frB
            difs.append((dif_mats(mats_val(VAL[qi]), mats_destino(nB, int(round(frB)) % MV.NQ[nB])) if PL["s"][i] >= 1.0 else 1.0, int(round(frB)) % MV.NQ[nB]))
        def conv_em(tol):
            c = nq
            for qi in range(nq, -1, -1):
                if difs[qi][0] > tol: break
                c = qi
            return c
        conv = conv_em(PAR["tol_convergencia_stud"]); conv_vis = conv_em(PAR["tol_visual_stud"])
        corte = next(qi for qi in range(conv, nq + 1) if difs[qi][1] == 0)
        conv_info = {"quadro_convergencia_exata": conv, "tol_exata_stud": PAR["tol_convergencia_stud"], "quadro_convergencia_visual": conv_vis, "tol_visual_stud": PAR["tol_visual_stud"],
                     "quadro_saida_q0": corte, "quadros_v28": nq, "dif_no_corte_stud": difs[corte][0], "dif_por_quadro_stud": [round(d[0], 7) for d in difs]}
        print("V29", nome, "convergencia", {k: v for k, v in conv_info.items() if k != "dif_por_quadro_stud"}, flush=True)
        nq = corte; idx = idx[:nq + 1]; VAL = VAL[:nq + 1]; EQ = EQ[:nq + 1]; XQ = XQ[:nq + 1]; EST = {k: v[:nq + 1] for k, v in EST.items()}
    ERR = max(max(e.values()) for e in EQ); EXT = {k: max(x[k] for x in XQ) for k in M.PATAS}
    IKP = {k: {"apoio": round(max([EQ[q][k] for q in range(nq + 1) if EST[k][q]] + [0.0]), 6), "balanco": round(max([EQ[q][k] for q in range(nq + 1) if not EST[k][q]] + [0.0]), 6)} for k in M.PATAS}
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); ARM.animation_data.action = acn
    for qi, vals in enumerate(VAL):
        for pb in P:
            pb.rotation_quaternion, pb.location = vals[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=qi, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=qi, group=pb.name)
    acn.use_fake_user = True; acn.frame_range = (0, nq); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    REL["acoes"][nome] = {"origem": nA, "destino": nB, "quadros": nq, "duracao_s": round(nq / FPS, 4), "laco": False, "t_inicio_rampa_s": round(ta, 4), "rampa_s": R,
                          "X_por_quadro": [round(PL["X"][i], 5) for i in idx], "v_por_quadro": [round(PL["P"][i]["v"], 4) for i in idx],
                          "s_por_quadro": [round(PL["s"][i], 5) for i in idx], "teta_por_quadro": [round(PL["teta"][i], 5) for i in idx],
                          "cadencia_hz_por_quadro": [round(PL["P"][i]["cad"], 4) for i in idx], "apoio_por_quadro": EST, "direcao": [0, -1, 0],
                          "fases_origem": GA["fases"], "fases_destino": GB["fases"], "deslocamento_global_fase": g_, "mudanca_fase_por_pata": deslocamento_global(GA, GB)[1], "erro_ik_max": round(ERR, 6), "extensao_max_perna": {k: round(x, 3) for k, x in EXT.items()},
                          "distancia_total": round(-PL["X"][idx[-1]], 3), "entrada": nA + " q0 (sair no fim de um ciclo)", "saida": "%s q%d (continua no q%d)" % (nB, saida_q, saida_q + 1),
                          "saida_quadro_destino": saida_q, "convergencia": conv_info, "erro_ik_por_pata": IKP, "extensao_por_quadro": {k: [round(x[k], 4) for x in XQ] for k in M.PATAS},
                          "apoios_cortados_v29": {k: [{kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in c.items()} for c in v] for k, v in PL["cortes"].items()}, "versao": "v29"}
    print("V29", nome, nq, "erro_ik", round(ERR, 6), "ext", {k: round(x, 3) for k, x in EXT.items()}, "dist", round(-PL["X"][idx[-1]], 3), flush=True)
ARM.animation_data.action = bpy.data.actions["Andar"]
json.dump(REL, open(os.path.join(OUT, "marchas_v29.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("TRANSICOES_MARCHA_V29_OK", flush=True)
