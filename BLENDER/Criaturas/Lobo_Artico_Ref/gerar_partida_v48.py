"""v48 (26/11/2026, pendencia "partir parado com passos / parar sem deslizar"): PARTIDA e PARADA do Andar, em COPIA (base anim_v47b,
so lida; saida <dir>). Mesmo metodo das curvas v46b (o Andar APROVADO "dobrado": corpo = Andar, patas = as do Andar levadas por uma
transformacao rigida no chao, IK com o plano de dobra do proprio quadro), com a trajetoria do corpo agora com VELOCIDADE variavel:
  PartidaAndar               v 0 -> 3,0 studs/s em 1,2 s (suave), omega 0                     2 ciclos (o 2o ja e o Andar)
  PartidaCurvaEsquerda/Dir.  v 0 -> 3,0 e omega 0 -> +-30 graus/s                               2 ciclos (o 2o ja e o AndarCurva)
  ParadaAndar                v 3,0 -> 0 em 1,2 s; cada pata pousa no lugar do Repouso e fica    2 ciclos (termina no Repouso q0)
Partida: cada pata fica PLANTADA onde estava no Repouso ate a sua primeira saida do cronograma do Andar (>= 0,25 s) e, nos 0,2 s antes
de sair, o pe passa da pose do Repouso para a do Andar (calcanhar sobe); depois segue o plano normal (apoio fixo no mundo no ponto do
meio do apoio da trajetoria; balanco min-jerk NO MUNDO entre os pontos plantados). Corpo: Repouso -> Andar em 0,6 s.
Parada: o ultimo pouso de cada pata entre 1,0 e 2,2 s e no lugar do Repouso (no rumo final) e a pata fica ali; o pe volta da pose do
Andar para a do Repouso em 0,2 s depois do pouso; corpo Andar -> Repouso entre 1,2 e 2,0 s.
Parametros = [PROPOSTA][A TESTAR]. Saida: partida_v48.json (curva externa por quadro, apoio por quadro, erros de IK).
Uso: blender -b anim_v47b/CR_LoboArtico_Anim.blend -P gerar_partida_v48.py -- anim_v48"""
import bpy, sys, os, json, math, shutil
from mathutils import Vector as V, Matrix, Quaternion
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; B = ARM.data.bones; sc = bpy.context.scene; FPS = 30
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1)); REST = {b.name: b.matrix_local.copy() for b in B}
PATAS = {"DE": ("Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D"),
         "TE": ("Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"), "TD": ("Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D")}
LEG = {n for c in PATAS.values() for n in c}
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json")))["andar"]
T_, BETA, FASE, VEL = CJ["T"], CJ["apoio"], CJ["fases"], CJ["v_studs_s"]; TS = BETA * T_
CENTRO = V((0.0, -0.95, 0.0)); IK_SUAVE = 0.97
PAR = {"rampa_s": float(os.environ.get("RAMPA_V48", "1.2")), "corpo_partida_s": 0.6, "saida_min_s": 0.1, "pe_troca_s": 0.2, "parada_janela": [1.6, 2.8], "corpo_parada": [2.0, 3.0], "parada_espera_s": 0.4,
       "omega_ref": 30.0, "Pescoco1": 5.0, "Pescoco2": 2.5, "Cabeca": 3.5, "Coluna1": 1.5, "Coluna2": 2.5, "Coluna3": 2.0,
       "cauda": [-1.5, -2.3, -3.1, -4.0], "rolamento": 1.5, "baixar": 0.12}
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def mj(w): w = max(0.0, min(1.0, w)); return w * w * w * (10 - 15 * w + 6 * w * w)
def q_global(n, R): Bm = REST[n].to_3x3(); return (Bm.inverted() @ R @ Bm).to_quaternion()
def usar(nome):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    return ac
for pb in P: pb.rotation_mode = "QUATERNION"
def captura():
    g = {"basis": {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P}, "pata": {}}
    for k, (sup, inf, pe, dedo) in PATAS.items():
        S, K, C = P[sup].head.copy(), P[sup].tail.copy(), P[inf].tail.copy(); dn = (C - S).normalized(); b = (K - S) - dn * (K - S).dot(dn)
        g["pata"][k] = {"dob": b, "xs": P[sup].matrix.col[0].to_3d().copy(), "xi": P[inf].matrix.col[0].to_3d().copy(),
                        "Mpe": P[pe].matrix.copy(), "Mdedo": P[dedo].matrix.copy(), "MCP": P[pe].tail.copy(), "ext": (C - S).length / (B[sup].length + B[inf].length)}
    return g
ac = usar("Andar"); F0 = int(ac.frame_range[0]); NQ = int(ac.frame_range[1]) - F0
AND = []
for q in range(NQ + 1): sc.frame_set(F0 + q); AND.append(captura())
ac = usar("Repouso"); sc.frame_set(int(ac.frame_range[0])); REP = captura()
ARM.animation_data.action = None
def u_de(k, t): return ((t / T_) - FASE[k]) % 1.0
MEIO = {}
for k in PATAS:
    tm = ((FASE[k] + BETA / 2) % 1.0) * T_; q = tm * FPS; i = int(q) % NQ; f = q - int(q)
    MEIO[k] = AND[i]["pata"][k]["MCP"].lerp(AND[i + 1]["pata"][k]["MCP"], f)
class Traj:
    """pivo para perfis v(t) e omega(t) (centro do giro no meio do corpo); pose(t) = (posicao xy do pivo, rumo)"""
    def __init__(self, vf, omf):
        self.dt = 1.0 / 600; self.t0 = -6.0; n = int(18.0 / self.dt) + 1; self.P = [None] * n; self.S = [0.0] * n
        i0 = int(round(-self.t0 / self.dt)); self.P[i0] = CENTRO.copy()
        for d in (1, -1):
            i = i0
            while 0 <= i + d < n:
                t = self.t0 + i * self.dt; h = d * self.dt; tm = t + h / 2; pm = self.S[i] + omf(tm) * h / 2
                self.P[i + d] = self.P[i] + V((math.sin(pm), -math.cos(pm), 0.0)) * vf(tm) * h; self.S[i + d] = self.S[i] + omf(tm) * h; i += d
    def pose(self, t):
        x = (t - self.t0) / self.dt; i = int(math.floor(x)); f = x - i
        sv = self.S[i] + (self.S[i + 1] - self.S[i]) * f; c = self.P[i].lerp(self.P[i + 1], f)
        return c - Matrix.Rotation(sv, 3, Z) @ CENTRO, sv
    def mundo(self, t, loc):
        p, s = self.pose(t); return p + Matrix.Rotation(s, 3, Z) @ loc, s
    def local(self, t, w):
        p, s = self.pose(t); return Matrix.Rotation(-s, 3, Z) @ (w - p), s
def plano_pata(k, tr, dur, modo):
    """lista de eventos da pata: [(tipo, t0, t1, W_mundo, rumo_plantado, fonte)] tipo 'apoio'/'balanco'; fonte 'rep'/'and'"""
    ev = []; j0 = math.floor(-1.0 / T_) - 1
    starts = [(FASE[k] + j) * T_ for j in range(j0, j0 + 8)]                      # inicios de apoio do Andar (tempo do clipe)
    if modo == "partida":
        Wr, sr = tr.mundo(0.0, REP["pata"][k]["MCP"])
        if u_de(k, 0.0) >= BETA:                                                   # no Andar esta NO AR em t=0: ja da o 1o passo
            lib = 0.0; ev.append(("apoio", -1.0, 0.0, Wr, sr, "rep"))
        else:
            lib = min(s + TS for s in starts if s + TS >= PAR["saida_min_s"])     # 1a saida do cronograma depois de saida_min_s
            ev.append(("apoio", -1.0, lib, Wr, sr, "rep"))
        prox = [s for s in starts if s > lib]
        ant_fim, ant_W, ant_s = lib, Wr, sr
        for s in prox:
            if s > dur + T_: break
            tm = s + TS / 2; W, sw = tr.mundo(tm, MEIO[k])
            ev.append(("balanco", ant_fim, s, (ant_W, W), (ant_s, sw), "and")); ev.append(("apoio", s, s + TS, W, sw, "and"))
            ant_fim, ant_W, ant_s = s + TS, W, sw
    else:                                                                          # parada
        a, b = PAR["parada_janela"]; ultimo = min(s for s in starts if a <= s < b)
        ant = None
        for s in starts:
            if s > ultimo: break
            if s == ultimo: W, sw = tr.mundo(dur, REP["pata"][k]["MCP"]); fim = dur + 1.0; fonte = "rep_apos"
            else: tm = s + TS / 2; W, sw = tr.mundo(tm, MEIO[k]); fim = s + TS; fonte = "and"
            if ant is not None: ev.append(("balanco", ant[0], s, (ant[1], W), (ant[2], sw), "and"))
            ev.append(("apoio", s, fim, W, sw, fonte)); ant = (fim, W, sw)
    return ev
def residuo(k, t, tm):
    """rolamento do proprio Andar no apoio: MCP do Andar no quadro - (meio do apoio + recuo a VEL); so xy"""
    q = (t * FPS) % NQ; i = int(q); f = q - i
    m = AND[i]["pata"][k]["MCP"].lerp(AND[min(i + 1, NQ)]["pata"][k]["MCP"], f); r = m - (MEIO[k] + V((0, VEL * (t - tm), 0)))
    return V((r.x, r.y, 0.0))
def mcp_andar(k, t):
    q = (t * FPS) % NQ; i = int(q); f = q - i
    m = AND[i]["pata"][k]["MCP"].lerp(AND[min(i + 1, NQ)]["pata"][k]["MCP"], f); return V((m.x, m.y, 0.0))
def alvo_apoio(tr, k, ea, tt):
    """alvo (xy, referencial do corpo) da pata no apoio ea no instante tt, como no ramo de apoio (pe do Andar na borda)"""
    a_, _ = tr.local(tt, ea[3]); a_ = V((a_.x, a_.y, 0.0))
    return a_ + residuo(k, tt, (ea[2] - TS / 2) if ea[5] == "rep" else (ea[1] + TS / 2))
def blend_basis(ga, gb, w):
    out = {}
    for n in ga:
        qa, la = ga[n]; qb, lb = gb[n]
        if qa.dot(qb) < 0: qb = -qb
        out[n] = (qa.slerp(qb, w), la.lerp(lb, w))
    return out
def pose_ik(k, gk, G, Mpe_src):
    sup, inf, pe, dedo = PATAS[k]; a, b = B[sup].length, B[inf].length; S = P[sup].head.copy()
    Mpe = G @ Mpe_src; Ct = Mpe.translation.copy()
    dv = Ct - S; dn = dv.normalized(); Lm = (a + b) * 0.9995; ds = min(Lm - 1e-4, max(IK_SUAVE * (a + b), gk["ext"] * (a + b)))
    d = dv.length if dv.length <= ds else ds + (Lm - ds) * (1 - math.exp(-(dv.length - ds) / (Lm - ds)))
    al = (a * a - b * b + d * d) / (2 * d); h = math.sqrt(max(a * a - al * al, 0.0))
    dob = G.to_3x3() @ gk["dob"]; perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0, xr in ((sup, S, K, G.to_3x3() @ gk["xs"]), (inf, K, S + dn * d, G.to_3x3() @ gk["xi"])):
        yv = (t0 - h0).normalized(); xv = (xr - yv * xr.dot(yv)).normalized()
        Mm = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); Mm.translation = h0; P[nome].matrix = Mm; bpy.context.view_layer.update()
    Mm = Mpe.copy(); Mm.translation = P[inf].tail.copy(); P[pe].matrix = Mm; bpy.context.view_layer.update()
    return (S + dn * d - Ct).length, d / (a + b), G
def mat_blend(Ma, Mb, w):
    qa, qb = Ma.to_quaternion(), Mb.to_quaternion()
    if qa.dot(qb) < 0: qb = -qb
    M = qa.slerp(qb, w).to_matrix().to_4x4(); M.translation = Ma.translation.lerp(Mb.translation, w); return M
CLIPES = {"PartidaAndar": ("partida", 0.0), "PartidaCurvaEsquerda": ("partida", 30.0), "PartidaCurvaDireita": ("partida", -30.0), "ParadaAndar": ("parada", 0.0)}
if os.environ.get("CLIPES_V48"): CLIPES = {k: v for k, v in CLIPES.items() if k in os.environ["CLIPES_V48"].split(",")}
REL = {"metodo": __doc__.split("Uso:")[0], "parametros": PAR, "andar": CJ, "fps": FPS, "acoes": {}}
for nome, (modo, om_g) in CLIPES.items():
    R_ = PAR["rampa_s"]; NC = (2 if modo == "partida" else 3) * NQ; dur = NC / FPS   # v48 r4: parada em 3 ciclos
    if modo == "partida":
        vf = lambda t: VEL * suave(t / R_) if t > 0 else 0.0; omf = (lambda o: (lambda t: math.radians(o) * suave(t / R_) if t > 0 else 0.0))(om_g)
    else:
        E_ = PAR["parada_espera_s"]; vf = lambda t: VEL if t <= E_ else VEL * (1 - suave((t - E_) / R_)); omf = lambda t: 0.0   # freia so depois de 0,4 s
    tr = Traj(vf, omf); EV = {k: plano_pata(k, tr, dur, modo) for k in PATAS}
    VAL, ERR, APO, EXT, LOGV, PIOR = [], 0.0, {k: [] for k in PATAS}, {}, [], {}
    for q in range(NC + 1):
        t = q / FPS; ga = AND[q % NQ]
        wc = suave(t / PAR["corpo_partida_s"]) if modo == "partida" else 1 - suave((t - PAR["corpo_parada"][0]) / (PAR["corpo_parada"][1] - PAR["corpo_parada"][0]))
        bas = blend_basis(REP["basis"], ga["basis"], wc)
        for pb in P: pb.matrix_basis.identity()
        for nm, (qq, ll) in bas.items(): P[nm].rotation_quaternion = qq; P[nm].location = ll
        omg = math.degrees(omf(t)); kl = math.degrees(omf(t + 0.15)) / PAR["omega_ref"]; s_ = 1 if omg >= 0 else -1; k_ = abs(omg) / PAR["omega_ref"]
        for nm in ("Pescoco1", "Pescoco2", "Cabeca"):
            P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(kl * PAR[nm]), 3, Z)) @ P[nm].rotation_quaternion
        for nm in ("Coluna1", "Coluna2", "Coluna3"):
            P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(s_ * k_ * PAR[nm]), 3, Z)) @ P[nm].rotation_quaternion
        for i, nm in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):
            P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(s_ * k_ * PAR["cauda"][i]), 3, Z)) @ P[nm].rotation_quaternion
        P["Quadril"].location = P["Quadril"].location + REST["Quadril"].to_3x3().inverted() @ V((0, 0, -PAR["baixar"] * k_ * k_))
        P["Quadril"].rotation_quaternion = q_global("Quadril", Matrix.Rotation(math.radians(-s_ * k_ * PAR["rolamento"]), 3, Y)) @ P["Quadril"].rotation_quaternion
        bpy.context.view_layer.update()
        e_ = 0.0; pv, psi = tr.pose(t)
        for k in PATAS:
            e = next(x for x in EV[k] if x[1] <= t <= x[2] or (x is EV[k][-1]))
            gk_and = ga["pata"][k]; gk_rep = REP["pata"][k]
            if e[0] == "apoio":
                alvo, _ = tr.local(t, e[3]); yaw = e[4] - psi; apo = True
                if e[5] == "rep":                                                   # partida: plantada no Repouso; antes de sair vira a pose do Andar
                    ini = max(0.0, e[2] - PAR["pe_troca_s"]); w = suave((t - ini) / max(1e-3, e[2] - ini))   # v48 r3: em t=0 o pe ainda e o do Repouso
                    src = mat_blend(gk_rep["Mpe"], gk_and["Mpe"], w); srcd = mat_blend(gk_rep["Mdedo"], gk_and["Mdedo"], w); m0 = gk_rep["MCP"].lerp(gk_and["MCP"], w); gk = gk_and if w > 0.5 else gk_rep
                    if w > 0: alvo = alvo + residuo(k, t, e[2] - TS / 2) * w              # o calcanhar sobe como no Andar antes de sair
                elif e[5] == "rep_apos":                                            # parada: ultimo pouso; volta a pose do Repouso
                    w = suave((t - e[1]) / PAR["pe_troca_s"])
                    src = mat_blend(gk_and["Mpe"], gk_rep["Mpe"], w); srcd = mat_blend(gk_and["Mdedo"], gk_rep["Mdedo"], w); m0 = gk_and["MCP"].lerp(gk_rep["MCP"], w); gk = gk_rep if w > 0.5 else gk_and
                    if w < 1: alvo = alvo + residuo(k, t, e[1] + TS / 2) * (1 - w)
                else:
                    src = gk_and["Mpe"]; srcd = gk_and["Mdedo"]; m0 = gk_and["MCP"]; gk = gk_and
                    alvo = alvo + residuo(k, t, e[1] + TS / 2)                             # v48 r2: preserva o rolamento do pe do Andar (dedos fixos)
            else:
                (W0, W1), (s0, s1) = e[3], e[4]; w = mj((t - e[1]) / max(1e-6, e[2] - e[1]))
                # v48 r5: no ar a pata segue o caminho do PROPRIO Andar + desvio que vai do da saida ao do pouso (como as curvas v46b);
                # o caminho reto no mundo nao batia com o laco do Andar na emenda (braco 24-32 graus)
                idx = EV[k].index(e); ea = EV[k][idx - 1]; eb = EV[k][idx + 1]
                d0 = alvo_apoio(tr, k, ea, e[1]) - mcp_andar(k, e[1]); d1 = alvo_apoio(tr, k, eb, e[2]) - mcp_andar(k, e[2])
                alvo = mcp_andar(k, t) + d0.lerp(d1, w); yaw = (s0 + (s1 - s0) * w) - psi; apo = False
                if modo == "partida" and e[1] == 0.0:                                     # v48 r6: 1o passo sai do Repouso com velocidade zero
                    a0 = tr.local(t, ea[3])[0]; a0 = V((a0.x, a0.y, 0.0)); wa = suave(t / 0.35)
                    alvo = a0.lerp(alvo, wa)
                src = gk_and["Mpe"]; srcd = gk_and["Mdedo"]; m0 = gk_and["MCP"]; gk = gk_and
                if modo == "partida" and e[1] == 0.0 and t < 0.25:                         # v48 r3: 1o passo saindo do Repouso: levanta aos poucos
                    wl = suave(t / 0.25); src = mat_blend(gk_rep["Mpe"], gk_and["Mpe"], wl); srcd = mat_blend(gk_rep["Mdedo"], gk_and["Mdedo"], wl)
                    m0 = gk_rep["MCP"].lerp(gk_and["MCP"], wl); gk = gk_and if wl > 0.5 else gk_rep
            G = Matrix.Translation(V((alvo.x, alvo.y, 0))) @ Matrix.Rotation(yaw, 4, Z) @ Matrix.Translation(V((-m0.x, -m0.y, 0)))
            er, x, _ = pose_ik(k, gk, G, src); e_ = max(e_, er); EXT[k] = max(EXT.get(k, 0.0), x); APO[k].append(apo)
            if er > PIOR.get(k, (0,))[0]: PIOR[k] = (round(er, 3), q, e[0], e[5], round(e[1], 2), round(e[2], 2))
            dedo = PATAS[k][3]; Md = G @ srcd
            Md.translation = P[PATAS[k][2]].tail.copy(); P[dedo].matrix = Md; bpy.context.view_layer.update()
        ERR = max(ERR, e_); LOGV.append(round(vf(t), 4))
        VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); ARM.animation_data.action = acn
    for qi, vals in enumerate(VAL):
        for pb in P:
            pb.rotation_quaternion, pb.location = vals[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=qi, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=qi, group=pb.name)
    acn.use_fake_user = True; acn.frame_range = (0, NC); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    ext = []
    for q in range(NC + 1):
        p_, s_ = tr.pose(q / FPS); ext.append([round(p_.x, 5), round(p_.y, 5), round(math.degrees(s_), 5)])
    REL["acoes"][nome] = {"modo": modo, "omega_final_graus_s": om_g, "quadros": NC, "duracao_s": dur, "laco": False, "externa_por_quadro_xy_psi": ext,
                          "v_por_quadro": LOGV, "omega_por_quadro": [round(math.degrees(omf(q / FPS)), 4) for q in range(NC + 1)],
                          "apoio_por_quadro": APO, "erro_ik_max": round(ERR, 6), "extensao_max_perna": {k: round(x, 3) for k, x in EXT.items()},
                          "planos": {k: [[e[0], round(e[1], 3), round(e[2], 3)] for e in EV[k]] for k in PATAS}}
    print("V48", nome, "q", NC, "fim", ext[-1], "erro_ik", round(ERR, 5), "pior", PIOR, "ext", {k: round(x, 3) for k, x in EXT.items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "partida_v48.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("PARTIDA_V48_OK", flush=True)
