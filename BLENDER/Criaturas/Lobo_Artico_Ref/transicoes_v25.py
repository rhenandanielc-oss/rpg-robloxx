"""L2b, 1o bloco (v25): ARRANCADA (Repouso -> Corrida) e FRENAGEM (Corrida -> Repouso), acoes de uma vez (nao lacos), sobre
uma copia da anim_v24 (so lida; saida <dir>). Repouso, Andar, Trote e Corrida ficam INTACTOS.
CONTRATO (projeto): clipe NO LUGAR (Raiz fixa, frente -Y; o jogo move o modelo); IK analitico de 2 ossos gravado em FK nos
ossos (marcha_v21.py; rolamento da v24 = pivo a 0,8 do osso dos dedos, descido 0,25 traseiras / 0,20 dianteiras, dedos para a
almofada); sem constraints/drivers. O DESLOCAMENTO de apresentacao e uma CURVA (nao uniforme), gravada em transicoes_v25.json
(X, v por quadro): X(t) = -integral de v; a auditoria e o render usam essa curva (nunca v constante).
- Arrancada: Repouso q0 -> antecipacao (agacha, peso para tras nas traseiras, v = 0) -> impulso (v sobe rapido no comeco e
  suaviza ate v_corrida) -> galope que converge para a Corrida v24 -> termina IGUAL ao quadro 0 da Corrida (entrada: Corrida q0).
- Frenagem: comeca IGUAL ao quadro 0 da Corrida (saida da Corrida no fim de um ciclo, q14 = q0) -> desaceleracao progressiva
  (passos encurtando, cadencia caindo, mais tempo de apoio, peso para tras: traseiras sob o corpo, dianteiras firmes) -> cada
  pata da um ultimo passo de acomodacao que POUSA onde, quando o corpo parar, ela estara na posicao de repouso -> estabiliza ->
  termina IGUAL ao Repouso q0.
Gerador: relogio de fase do galope (ordem TE -> TD -> DD -> DE, fases da Corrida) com ciclo T(r) e fracao de apoio beta(r)
dependentes de r = v / v_corrida; pata no APOIO recua no referencial do corpo exatamente integral(v) (sem deslize por
construcao); toque planejado para centrar o apoio em c(r); balanco min-jerk do ponto de saida ao proximo toque; alturas,
dobras e rolamento escalados por r; corpo = mistura (slerp) da pose do Repouso q0 com o corpo da Corrida (fase do relogio), com
atraso leve em pescoco/cabeca/cauda (inercia) e postura de impulso/freio proporcional a aceleracao. No ultimo ciclo da
Arrancada e no 1o da Frenagem os parametros sao EXATAMENTE os da Corrida (mesmas formulas): emenda sem salto.
Uso: blender -b anim_v24/CR_LoboArtico_Anim.blend -P transicoes_v25.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix, Quaternion
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
COR = CJ["marchas"]["Corrida"]; T_C = COR["T"]; V_C = COR["v_studs_s"]; FPS = M.FPS; NQC = int(round(T_C * FPS)); ARM = M.ARM; P = M.P
PAR = {"ant_s": 0.30, "acel_s": 1.25, "freio_s": 1.15, "acomoda_s": 0.45, "T_lento": 0.62, "beta_lento": 0.60, "teta0": 0.52, "h_min": 0.35,
       "agacha_z": -0.10, "agacha_graus": -3.0, "impulso_graus": 2.5, "freio_graus": -3.5, "freio_z": -0.06, "cabeca_freio_graus": -4.0,
       "atraso_cabeca_s": 0.07, "atraso_cauda_s": 0.12, "r_congela": 0.30}
if os.environ.get("AJUSTE_V25"): PAR.update(json.loads(os.environ["AJUSTE_V25"]))
LEG = {n for c in M.PATAS.values() for n in c}; CABECA = {"Pescoco1", "Pescoco2", "Cabeca"}; CAUDA = {"Cauda1", "Cauda2", "Cauda3", "Cauda4"}
# ---------------------------------------------------------------- rolamento da v24 (igual a clipes_v24.py, padrao)
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
# ---------------------------------------------------------------- corpo da Corrida (copia de clipes_v21.corpo_corrida, mesmos parametros)
def escapulas(add, G, t, A):
    for lado in ("E", "D"):
        u = ((t / G["T"]) - G["fases"]["D" + lado]) % 1.0; add("Escapula_" + lado, M.X, -A * math.cos(2 * math.pi * (u - G["apoio"] / 2)))
def corpo_corrida(t):
    G = COR; T = G["T"]; u = (t / T) % 1.0; R = {}; X = M.X; Y = M.Y; Z = M.Z; onda = M.onda
    def add(n, e, g): R.setdefault(n, []).append((e, g))
    flex = math.cos(2 * math.pi * (u - G["suspensao_centro"]))
    q = V((0.03 * onda(t, T, 0.1), 0.0, G["quadril_z"] + G["subida"] * math.cos(2 * math.pi * (u - G["suspensao_centro"]))))
    soma = G["coluna_graus"] * 2.7
    add("Quadril", X, G["arfagem_graus"] * 0.5 * (1 + math.cos(2 * math.pi * (u - 0.48))) - G["compensa_coluna"] * soma * min(flex, 0.0))
    add("Quadril", Y, 1.5 * onda(t, T, 0.2))
    for n, f in (("Coluna1", 1.0), ("Coluna2", 1.0), ("Coluna3", 0.7)): add(n, X, G["coluna_graus"] * f * flex)
    pesc = -(G["arfagem_graus"] * 0.5 * (1 + math.cos(2 * math.pi * (u - 0.48))) + soma * flex - G["compensa_coluna"] * soma * min(flex, 0.0))
    add("Pescoco1", X, 9.0 + 0.6 * pesc); add("Pescoco2", X, 0.25 * pesc); add("Cabeca", X, -7.0 + 0.15 * pesc)
    add("Pescoco1", Z, 0.8 * onda(t, T, 0.3))
    for i, n in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):
        add(n, X, (-14.0 if i == 0 else -3.0) - (3.0 + 1.5 * i) * flex); add(n, Z, (1.5 + 1.0 * i) * onda(t, T, 0.2 + 0.1 * i))
    for n in ("Orelha_E", "Orelha_D"): add(n, X, -14.0 - 2.0 * flex)
    escapulas(add, G, t, 14.0)
    return R, q
def pose_de(R, q):
    M.aplicar_corpo(R, q); return {pb.name: pb.rotation_quaternion.copy() for pb in P if pb.name not in LEG}, P["Quadril"].location.copy()
ac = bpy.data.actions["Repouso"]; ARM.animation_data.action = ac
if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
bpy.context.scene.frame_set(0); REP = ({pb.name: pb.rotation_quaternion.copy() for pb in P if pb.name not in LEG}, P["Quadril"].location.copy())
ARM.animation_data.action = None
# ---------------------------------------------------------------- curvas tecnicas
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def T_de(r): return T_C + (PAR["T_lento"] - T_C) * (1 - r) ** 1.5
def beta_de(r): return COR["apoio"] + (PAR["beta_lento"] - COR["apoio"]) * (1 - r) ** 1.2
DT = 1.0 / 600
def v_arranca(t):
    x = (t - PAR["ant_s"]) / PAR["acel_s"]
    if x <= 0: return 0.0
    if x >= 1: return V_C
    return V_C * (1 - (1 - x) ** 2.2) * suave(x / 0.12)
def v_freia(t):
    x = t / PAR["freio_s"]
    if x <= 0: return V_C
    if x >= 1: return 0.0
    return V_C * (1 - suave(x)) ** 1.15
def plano(v_fn, dur, teta_ini, modo):
    """amostra fina: tempo, v, X (=-integral v), relogio de fase; apoios por pata (inicio/fim/toque) com congelamento no fim (Frenagem)"""
    N = int(round(dur / DT)); ts = [i * DT for i in range(N + 1)]; vs = [v_fn(t) for t in ts]; Xs = [0.0]; th = [teta_ini]
    for i in range(1, N + 1):
        Xs.append(Xs[-1] - 0.5 * (vs[i] + vs[i - 1]) * DT)
        rr = 0.5 * (vs[i] + vs[i - 1]) / V_C; rel = (ts[i] >= PAR["ant_s"]) if modo == "arranca" else True
        th.append(th[-1] + (DT / T_de(rr) if rel else 0.0))
    def Xi(p):                                                       # X interpolado em posicao fracionaria de amostra
        p = max(0.0, min(float(N), p)); i0 = int(math.floor(p)); i1 = min(N, i0 + 1); return Xs[i0] + (p - i0) * (Xs[i1] - Xs[i0])
    D = lambda p0, p1: -(Xi(p1) - Xi(p0))                           # distancia percorrida pelo corpo entre dois instantes
    ap = {}
    for k in M.PATAS:
        f = COR["fases"][k]; est = []
        for i in range(N + 1):
            r = vs[i] / V_C
            if modo == "arranca" and ts[i] < PAR["ant_s"]: est.append(True); continue
            est.append(((th[i] - f) % 1.0) < beta_de(r))
        if modo == "arranca":                                        # comeca com as 4 patas plantadas: so sai no 1o fim de apoio
            i = 0
            while i <= N and est[i]: i += 1
        segs = []; i = 0
        while i <= N:
            if est[i]:
                j = i
                while j + 1 <= N and est[j + 1]: j += 1
                segs.append([i, j]); i = j + 1
            else: i += 1
        for s in segs:                                               # limites EXATOS (interpolados): inicio = relogio cruza fase+m; fim = fracao cruza beta(r)
            i, j = s
            if i > 0 and not (modo == "arranca" and ts[i] <= PAR["ant_s"]):
                m = math.floor(th[i] - f); s[0] = (i - 1) + (f + m - th[i - 1]) / max(1e-12, th[i] - th[i - 1])
            if j < N:
                m = math.floor(th[j] - f); h0 = th[j] - f - m - beta_de(vs[j] / V_C); h1 = th[j + 1] - f - m - beta_de(vs[j + 1] / V_C)
                s[1] = j + (-h0) / max(1e-12, h1 - h0)
        if modo == "freia":                                          # congela: depois do 1o toque com r < r_congela a pata fica plantada
            for s in segs:
                if vs[int(s[0])] / V_C < PAR["r_congela"] and s[0] > 0: s[1] = N; segs = segs[:segs.index(s) + 1]; break
            else: segs[-1][1] = N
        ap[k] = segs
    return {"t": ts, "v": vs, "X": Xs, "teta": th, "apoios": ap, "D": D, "N": N}
def pata_em(PL, k, i):
    """dy, dz, rolo, dobra da pata k na amostra i (referencial do corpo)"""
    segs = PL["apoios"][k]; v = PL["v"]; D = PL["D"]
    def c_de(ii): return (v[ii] / V_C) * COR["centro"][k]
    def toque(s, idx):
        if PL["modo"] == "arranca" and idx == 0: return 0.0           # 1o apoio da Arrancada = posicao do repouso
        if PL["modo"] == "freia" and idx == len(segs) - 1: return -D(s[0], PL["N"])          # ultimo: termina na posicao de repouso
        if PL["modo"] == "freia" and idx == 0 and s[0] == 0:          # apoio em curso no quadro 0 = apoio da Corrida
            return PL["y0"][k]
        mid = int((s[0] + s[1]) // 2); return c_de(min(mid, PL["N"])) - D(s[0], s[1]) / 2
    for idx, s in enumerate(segs):
        if s[0] <= i <= s[1]:
            y = toque(s, idx) + D(s[0], i); r = v[int(s[0])] / V_C
            sp = (i - s[0]) / max(1, s[1] - s[0]); roll = math.radians(COR["rolamento_graus"]) * min(1.0, r)
            final_parado = (PL["modo"] == "freia" and idx == len(segs) - 1) or (PL["modo"] == "arranca" and idx == 0 and False)
            rolo = 0.0 if final_parado else roll * suave((sp - COR["rolo_ini"]) / (1 - COR["rolo_ini"]))
            if PL["modo"] == "arranca" and idx == 0: rolo = roll * suave((sp - 0.75) / 0.25)
            return y, 0.0, rolo, 0.0
        if idx + 1 < len(segs) and s[1] < i < segs[idx + 1][0]:
            a0, a1 = s[1], segs[idx + 1][0]; w = (i - a0) / (a1 - a0); mj = w * w * w * (10 - 15 * w + 6 * w * w)
            y0 = toque(s, idx) + D(s[0], s[1]); y1 = toque(segs[idx + 1], idx + 1); r = max(v[int(a0)], v[int(a1)]) / V_C
            h = COR["altura"][k[0]] * (PAR["h_min"] + (1 - PAR["h_min"]) * r); dob = math.radians(COR["dobra_graus"][k[0]]) * (PAR["h_min"] + (1 - PAR["h_min"]) * r)
            roll = math.radians(COR["rolamento_graus"]) * min(1.0, v[int(a0)] / V_C)
            return y0 + (y1 - y0) * mj, M.altura_balanco(h, w), roll * (1 - suave((w - 0.2) / 0.4)), dob * math.sin(math.pi * w) ** 1.5 * (1 - suave((w - 0.7) / 0.3))
    if PL["modo"] == "freia" and i < segs[0][0]:                      # balanco em curso no quadro 0 (Corrida) ate o 1o toque
        u0 = (PL["teta"][0] - COR["fases"][k]) % 1.0; s0 = segs[0][0]
        w0 = (u0 - COR["apoio"]) / (1 - COR["apoio"]); dur = (s0 - 0) * DT; wq = w0 + (1 - w0) * (i / s0)
        yc0 = M.pata_marcha(COR, k, 0.0)[0]; y1 = toque(segs[0], 0)
        mj0 = w0 ** 3 * (10 - 15 * w0 + 6 * w0 * w0); mj = wq ** 3 * (10 - 15 * wq + 6 * wq * wq)
        ys = yc0 + (y1 - yc0) * (mj - mj0) / max(1e-6, 1 - mj0)
        r = 1.0; h = COR["altura"][k[0]]; dob = math.radians(COR["dobra_graus"][k[0]]); roll = math.radians(COR["rolamento_graus"])
        return ys, M.altura_balanco(h, wq), roll * (1 - suave((wq - 0.2) / 0.4)), dob * math.sin(math.pi * wq) ** 1.5 * (1 - suave((wq - 0.7) / 0.3))
    raise RuntimeError("pata %s sem fase na amostra %d" % (k, i))
def a_de(PL, t):
    i = max(0, min(PL["N"], int(round(t / DT)))); return PL["v"][i] / V_C
def acel_de(PL, i):
    j0, j1 = max(0, i - 3), min(PL["N"], i + 3); return (PL["v"][j1] - PL["v"][j0]) / ((j1 - j0) * DT) / (V_C / 0.6)
def montar_pose(PL, i):
    t = PL["t"][i]; th = PL["teta"][i]; rc = pose_de(*corpo_corrida(th * T_C))
    ac_ = acel_de(PL, i); ant = 0.0
    if PL["modo"] == "arranca": ant = math.sin(math.pi * min(1.0, t / (PAR["ant_s"] + 0.15))) ** 2 if t < PAR["ant_s"] + 0.15 else 0.0
    if PL["modo"] == "freia": ant = 0.0
    def a_osso(n):
        lag = PAR["atraso_cabeca_s"] if n in CABECA else (PAR["atraso_cauda_s"] if n in CAUDA else 0.0)
        tt = t - lag if PL["modo"] == "arranca" else t - lag
        return suave(a_de(PL, max(0.0, tt)) ** 0.8) if PL["modo"] == "arranca" else suave(a_de(PL, max(0.0, tt)))
    # postura extra: agachar/peso atras (antecipacao), inclinar para frente no impulso, sentar as traseiras no freio
    Rx = {}
    def add(n, e, g): Rx.setdefault(n, []).append((e, g))
    freio = max(0.0, -ac_) * suave(t / 0.12) if PL["modo"] == "freia" else 0.0      # entra do zero: Frenagem q0 = Corrida q0
    imp = max(0.0, ac_) if PL["modo"] == "arranca" else 0.0
    add("Quadril", M.X, PAR["agacha_graus"] * ant + PAR["impulso_graus"] * min(1.0, imp) + PAR["freio_graus"] * min(1.0, freio))
    add("Pescoco1", M.X, -2.0 * ant + 2.0 * min(1.0, imp) + PAR["cabeca_freio_graus"] * min(1.0, freio))
    add("Cauda1", M.X, 4.0 * min(1.0, freio) - 3.0 * ant)
    qx = V((0, 0, PAR["agacha_z"] * ant + PAR["freio_z"] * min(1.0, freio)))
    ex = pose_de(Rx, qx)
    Q = {}
    for n in REP[0]:
        a = a_osso(n); qb = REP[0][n].slerp(rc[0][n], a); Q[n] = ex[0][n] @ qb
    loc = REP[1].lerp(rc[1], a_osso("Quadril")) + (ex[1] - M.REST["Quadril"].to_3x3().inverted() @ V())
    for pb in P: pb.matrix_basis.identity()
    for n, q in Q.items(): P[n].rotation_quaternion = q
    P["Quadril"].location = loc; bpy.context.view_layer.update()
    err = 0.0; ext = {}
    for k in M.PATAS:
        dy, dz, rolo, dobra = pata_em(PL, k, i); m_ef, phi, phd = alvo(k, dy, dz, rolo, dobra); e, x = M.ik(k, m_ef, phi, phd); err = max(err, e); ext[k] = x
    for c in M.PATAS.values():
        for n in c: P[n].location = (0, 0, 0)
    bpy.context.view_layer.update(); return err, ext
def quadros_de(PL, nq):
    return [int(round(q / FPS / DT)) for q in range(nq + 1)]
REL = {"parametros": PAR, "v_corrida": V_C, "T_corrida": T_C, "fps": FPS, "acoes": {}}
def gerar(nome, PL, nq):
    idx = quadros_de(PL, nq); VAL = []; ERR = 0.0; EXT = {}
    for pb in P: pb.rotation_mode = "QUATERNION"
    for i in idx:
        e, ext = montar_pose(PL, i); ERR = max(ERR, e)
        for k, x in ext.items(): EXT[k] = max(EXT.get(k, 0), x)
        VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); ARM.animation_data.action = acn
    for qi, vals in enumerate(VAL):
        for pb in P:
            pb.rotation_quaternion, pb.location = vals[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=qi, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=qi, group=pb.name)
    acn.use_fake_user = True; acn.frame_range = (0, nq); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    fim = idx[-1]; apo = {k: [[round(s[0] * DT * FPS, 3), round(min(s[1], fim) * DT * FPS, 3)] for s in segs if s[0] <= fim] for k, segs in PL["apoios"].items()}
    est = {k: [any(s[0] <= i <= s[1] for s in PL["apoios"][k]) for i in idx] for k in M.PATAS}
    REL["acoes"][nome] = {"quadros": nq, "duracao_s": round(nq / FPS, 4), "laco": False, "X_por_quadro": [round(PL["X"][i], 5) for i in idx],
                          "v_por_quadro": [round(PL["v"][i], 4) for i in idx], "direcao": [0, -1, 0], "teta_por_quadro": [round(PL["teta"][i], 5) for i in idx],
                          "apoio_por_quadro": est, "apoios_quadros_continuos": apo, "erro_ik_max": round(ERR, 5), "extensao_max_perna": {k: round(x, 3) for k, x in EXT.items()},
                          "distancia_total": round(-PL["X"][idx[-1]], 3)}
    print("V25", nome, nq, "erro_ik", round(ERR, 5), "ext", {k: round(x, 3) for k, x in EXT.items()}, "dist", round(-PL["X"][idx[-1]], 3), flush=True)
# ---------------------------------------------------------------- ARRANCADA: relogio alinhado para terminar num inteiro (= Corrida q0)
def plano_arranca(teta0):
    dur = PAR["ant_s"] + PAR["acel_s"] + 5.0 * T_C; PL = plano(v_arranca, dur, teta0, "arranca"); PL["modo"] = "arranca"; return PL
PL = plano_arranca(PAR["teta0"]); i_full = int(round((PAR["ant_s"] + PAR["acel_s"]) / DT))
ql = (math.floor(PL["teta"][i_full]) + 2 - PL["teta"][i_full]) * T_C        # tempo ate o 2o inteiro depois da velocidade cheia
t_end = PL["t"][i_full] + ql; nq_a = int(math.ceil(t_end * FPS - 1e-9)); d_teta = (nq_a / FPS - t_end) / T_C
PL = plano_arranca(PAR["teta0"] - d_teta)                                      # desloca o relogio para cair no inteiro num quadro inteiro
ia = int(round(nq_a / FPS / DT)); REL["arranca_teta_fim"] = PL["teta"][ia]       # o plano segue alem do fim (apoios em curso usam o toque planejado)
if os.environ.get("DBG_V25"):
    for k in M.PATAS:
        segs = PL["apoios"][k]; print("DBG", k, "pata_em", [round(x, 4) for x in pata_em(PL, k, ia)], "corrida", [round(x, 4) for x in M.pata_marcha(COR, k, 0.0)],
              "segs_perto", [(round(a_ * DT * FPS, 2), round(b_ * DT * FPS, 2)) for a_, b_ in segs if abs(a_ - ia) < 400 or abs(b_ - ia) < 400], "ia", ia * DT * FPS, flush=True)
gerar("Arrancada", PL, nq_a)
# ---------------------------------------------------------------- FRENAGEM: comeca em Corrida q0 (teta = 0)
dur_f = PAR["freio_s"] + PAR["acomoda_s"]; nq_f = int(round(dur_f * FPS)); PF = plano(v_freia, nq_f / FPS, 0.0, "freia"); PF["modo"] = "freia"
PF["y0"] = {k: M.pata_marcha(COR, k, 0.0)[0] for k in M.PATAS}
gerar("Frenagem", PF, nq_f)
REL["entrada_saida"] = {"Arrancada": {"inicio": "Repouso q0", "fim": "Corrida q0 (continua a Corrida a partir do q1)", "teta_fim": round(REL["arranca_teta_fim"], 6)},
                        "Frenagem": {"inicio": "Corrida q0 (sair da Corrida no fim de um ciclo: q14 = q0)", "fim": "Repouso q0"}}
ARM.animation_data.action = bpy.data.actions["Corrida"]
json.dump(REL, open(os.path.join(OUT, "transicoes_v25.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("TRANSICOES_V25_OK", flush=True)
