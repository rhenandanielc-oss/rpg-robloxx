"""v52 (27/11/2026, usuario: "Sim, corrigir o laco"): CORRECAO DO APOIO nas curvas do Andar compartilhadas (as 16 da v46b/v46c).
Mesmo erro achado na partida (v51): a pata apoiada = Andar levado por G = T(MCP_andar + delta) Rz(guinada) T(-MCP_andar), e o MCP do
Andar no quadro = meio do apoio + recuo + RESIDUO (rolamento do pe do Andar, em eixos do CORPO) -> o residuo girava junto com o corpo e
arrastava a sola (|residuo| x giro no apoio: DD 0,0396, TE 0,0335 a 30 graus/s). v52: delta += Rz(guinada) r - r, com r = MCP_andar(t) -
(meio + recuo), no apoio e nas pontas dos balancos (saida/pouso), para o residuo ficar no rumo em que a pata pousou. Em linha reta nada
muda. Saida curvas_v46b.json (mesmo nome, em <dir> novo; campo "versao": "v52").
Uso: blender -b anim_v51/CR_LoboArtico_Anim.blend -P gerar_curvas_v52.py -- anim_v52
--- texto da v46b ---
v46b (20/11): MESMO metodo de "dobrar" o Andar aprovado, mas com TRAJETORIA GENERICA: o pivo segue um perfil omega(t) qualquer
(integrado); cada pata apoiada fica fixa no mundo no ponto do MEIO do seu apoio naquela trajetoria; balanco min-jerk entre a saida e o
proximo toque. Lacos de omega constante (1 ciclo) + TRANSICOES de 2 ciclos (rampa suave de 1 ciclo no inicio; o 2o ciclo ja e o laco)
que comecam e terminam EXATAMENTE na pose dos lacos (Andar, Curva 30, Fechada 50): o jogo troca de clipe so na virada do ciclo.
Motivo: misturar Andar e Curva por PESO fazia a pata escorregar (0,07 com peso fixo de 50%, 0,13-0,41 nas rampas; auditoria v46).
Uso: blender -b anim_v45r3/CR_LoboArtico_Anim.blend -P gerar_curvas_v46b.py -- anim_v46b
--- texto da v46: ---
v46 (20/11/2026, pedido "mudar de direcao caminhando em curva"): ANDAR EM CURVA, em COPIA (anim_v45r3 so lida; saida <dir>).
Acoes novas (lacos de 36 quadros = 1 ciclo do Andar, MESMA fase do Andar para o jogo misturar reto <-> curva pelo peso):
  AndarCurvaEsquerda / AndarCurvaDireita             omega = 30 graus/s  (raio do pivo = v/omega = 5,7 studs)  [PROPOSTA][A TESTAR]
  AndarCurvaFechadaEsquerda / AndarCurvaFechadaDireita omega = 50 graus/s  (raio 3,4 studs)                    [PROPOSTA][A TESTAR]
Metodo = "dobrar" o Andar APROVADO quadro a quadro (o Andar v41/v45r3 ja tem as correcoes v31 pernas retas, v33 patas sem virar no
ar, v34 convergencia): ossos do corpo = os do Andar + curvatura; cada pata = a MESMA pata do Andar levada por uma transformacao
rigida no plano do chao G = T(MCP + delta) Rz(guinada) T(-MCP):
  APOIO: o ponto da pata fica PARADO NO MUNDO enquanto o pivo do jogo avanca v = 3,0 studs/s (frente -Y) e gira omega em volta de
    si mesmo. No referencial do corpo, o MCP que no meio do apoio estava em M fica em Rz(-th) (M - P(tau)), th = omega tau,
    P(tau) = ((v/omega)(1 - cos th), -(v/omega) sin th); delta = isso - (M + (0, v tau)) (o que o Andar reto ja faz); guinada = -th.
    -> pata interna percorre arco menor, externa arco maior (a diferenca sai da propria geometria do giro).
  BALANCO: delta e guinada vao, em min-jerk, do valor da saida (tau = +Ts/2) ao do proximo toque (tau = -Ts/2): a pata pousa ja
    virada para dentro da curva.
  Perna: IK de 2 ossos ate o carpo novo, com o PLANO DE DOBRA do proprio quadro do Andar (cotovelo/joelho no mesmo lado; mantem a
    perna reta da v31) e a torcao do osso do Andar; Metacarpo/Dedos = os do Andar levados por G (sola inteira, rolamento preservado).
Corpo (graus no omega de referencia 30 graus/s, escala linear com omega; + = esquerda): cabeca/pescoco antecipam (Pescoco1 5,
  Pescoco2 2,5, Cabeca 3,5), coluna em arco (Coluna1 1,5, Coluna2 2,5, Coluna3 2), cauda compensa para fora (-1,5 .. -4) e o corpo
  inclina para dentro (Quadril, rolamento 1,5). Valores = [PROPOSTA][A TESTAR].
Saida: <dir>/CR_LoboArtico_Anim.blend + curvas_v46.json (omega, raio, curva externa por quadro, apoio por quadro, erros de IK).
Contrato de animacao igual (clipe no lugar); o jogo aplica a curva externa: por quadro, avanca v*dt na frente e gira omega*dt (pivo).
Uso: blender -b anim_v45r3/CR_LoboArtico_Anim.blend -P gerar_curvas_v46.py -- anim_v46"""
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
PAR = {"omega_ref": 30.0, "Pescoco1": 5.0, "Pescoco2": 2.5, "Cabeca": 3.5, "Coluna1": 1.5, "Coluna2": 2.5, "Coluna3": 2.0,
       "cauda": [-1.5, -2.3, -3.1, -4.0], "rolamento": 1.5, "baixar": 0.12}
if os.environ.get("AJUSTE_V46"): PAR.update(json.loads(os.environ["AJUSTE_V46"]))
CLIPES = {}; FE = float(os.environ.get("FECHADA_V46", "45"))   # graus/s da curva fechada [A TESTAR]
for lado, sg in (("Esquerda", 1), ("Direita", -1)):
    CLIPES["AndarCurva" + lado] = (30.0 * sg, 30.0 * sg, 1); CLIPES["AndarCurvaFechada" + lado] = (FE * sg, FE * sg, 1)
    CLIPES["AndarParaCurva" + lado] = (0.0, 30.0 * sg, 2); CLIPES["CurvaParaAndar" + lado] = (30.0 * sg, 0.0, 2)
    CLIPES["CurvaParaFechada" + lado] = (30.0 * sg, FE * sg, 2); CLIPES["FechadaParaCurva" + lado] = (FE * sg, 30.0 * sg, 2)
    # v46b r5: curvas CURTAS que comecam e terminam retas (correcoes de rumo pequenas): omega = pico * sen^2 (pi t / D)
    CLIPES["CurvaBreve" + lado] = (0.0, 0.0, 1, 30.0 * sg)       # 18 graus em 1 ciclo [PROPOSTA][A TESTAR]
    CLIPES["CurvaCurta" + lado] = (0.0, 0.0, 2, 30.0 * sg)       # 36 graus em 2 ciclos [PROPOSTA][A TESTAR]
if os.environ.get("CLIPES_V46"): CLIPES = {k: v for k, v in CLIPES.items() if k in os.environ["CLIPES_V46"].split(",")}
def mj(w): w = max(0.0, min(1.0, w)); return w * w * w * (10 - 15 * w + 6 * w * w)
def q_global(n, R): Bm = REST[n].to_3x3(); return (Bm.inverted() @ R @ Bm).to_quaternion()
def usar(nome):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    return ac
for pb in P: pb.rotation_mode = "QUATERNION"
# Andar aprovado: pose de cada quadro (basis) e geometria das patas
ac = usar("Andar"); F0 = int(ac.frame_range[0]); NQ = int(ac.frame_range[1]) - F0
assert NQ == round(T_ * FPS), (NQ, T_)
AND = []
for q in range(NQ + 1):
    sc.frame_set(F0 + q)
    g = {"basis": {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P}, "pata": {}}
    for k, (sup, inf, pe, dedo) in PATAS.items():
        S, K, C = P[sup].head.copy(), P[sup].tail.copy(), P[inf].tail.copy(); dn = (C - S).normalized(); b = (K - S) - dn * (K - S).dot(dn)
        g["pata"][k] = {"S": S, "C": C, "dob": b, "ext": (C - S).length / (B[sup].length + B[inf].length), "xs": P[sup].matrix.col[0].to_3d().copy(), "xi": P[inf].matrix.col[0].to_3d().copy(),
                        "Mpe": P[pe].matrix.copy(), "Mdedo": P[dedo].matrix.copy(), "MCP": P[pe].tail.copy()}
    AND.append(g)
ARM.animation_data.action = None
def u_de(k, t): return ((t / T_) - FASE[k]) % 1.0
MEIO = {}                                                    # MCP no meio do apoio (referencial do corpo, Andar reto)
for k in PATAS:
    tm = ((FASE[k] + BETA / 2) % 1.0) * T_; q = tm * FPS; i = int(q) % NQ; f = q - int(q)
    MEIO[k] = AND[i]["pata"][k]["MCP"].lerp(AND[i + 1]["pata"][k]["MCP"], f)
RAMPA_S = T_                                                  # rampa de omega das transicoes (1 ciclo) [PROPOSTA][A TESTAR]
CENTRO = V((0.0, float(os.environ.get("CENTRO_Y_V46", "-0.95")), 0.0))   # v46b r3: ponto do corpo que percorre o arco (giro em volta dele) [A TESTAR]
class Traj:
    """trajetoria do pivo para um perfil omega(t) (rad/s; t em s, definido em toda a reta: antes/depois = constante), v constante.
    Integra de -6 s a +12 s a 600 Hz; pose(t) = (posicao xy, rumo psi)."""
    def __init__(self, omf):
        self.omf = omf; self.dt = 1.0 / 600; self.t0 = -6.0; n = int(18.0 / self.dt) + 1; self.P = [None] * n; self.S = [0.0] * n
        i0 = int(round(-self.t0 / self.dt)); self.P[i0] = CENTRO.copy(); self.S[i0] = 0.0      # integra o CENTRO de giro (no corpo)
        for d in (1, -1):
            i = i0
            while 0 <= i + d < n:
                t = self.t0 + i * self.dt; h = d * self.dt; pm = self.S[i] + omf(t + h / 2) * h / 2
                self.P[i + d] = self.P[i] + V((math.sin(pm), -math.cos(pm), 0.0)) * VEL * h; self.S[i + d] = self.S[i] + omf(t + h / 2) * h; i += d
    def pose(self, t):
        x = (t - self.t0) / self.dt; i = int(math.floor(x)); f = x - i
        sv = self.S[i] + (self.S[i + 1] - self.S[i]) * f; c = self.P[i].lerp(self.P[i + 1], f)
        return c - Matrix.Rotation(sv, 3, Z) @ CENTRO, sv                                  # posicao do PIVO (origem do rig)
    def corpo_de(self, t, tm, Mloc):
        """ponto do corpo Mloc no instante tm (fixo no mundo) visto do referencial do corpo no instante t; + guinada relativa"""
        p1, s1 = self.pose(tm); p0, s0 = self.pose(t); w = p1 + Matrix.Rotation(s1, 3, Z) @ Mloc
        return Matrix.Rotation(-s0, 3, Z) @ (w - p0), s1 - s0
def janela_apoio(k, t):
    """(apoiada, meio do apoio atual/ultimo, fim do apoio) no tempo global t, pelo cronograma do Andar"""
    u = u_de(k, t); ini = t - u * T_
    return u < BETA, ini + TS / 2, ini + TS
DENTRO_MAX = float(os.environ.get("DENTRO_MAX_V46", "99"))   # v46b r2: no apoio a pata nao entra mais que isso para o meio (stud) [A TESTAR]
IK_SUAVE = float(os.environ.get("IK_SUAVE_V46", "0.97"))    # v46b r4: acima disso (ou da extensao do proprio Andar) a perna estica suave
FORA_MAX = float(os.environ.get("FORA_MAX_V46", "99"))      # v46b r4: nem mais que isso para FORA (perna de fora no limite do alcance) [A TESTAR]
SIDE = {"DE": 1, "TE": 1, "DD": -1, "TD": -1}; _OX = {}
def plantio(tr, k, tm):
    """ponto plantado (referencial do corpo no meio do apoio): o do Andar, deslocado PARA FORA se, no giro, a pata entraria mais que
    DENTRO_MAX para o meio durante o apoio (como a v27 das viradas). Andar reto: deslocamento 0 (Andar aprovado intacto)."""
    ch = (id(tr), k, round(tm, 5))
    if ch not in _OX:
        M = MEIO[k]; sg = SIDE[k]; xs = [tr.corpo_de(tm + TS * (i / 12 - 0.5), tm, M)[0].x for i in range(13)]
        e = max(sg * (M.x - x) for x in xs); f = max(sg * (x - M.x) for x in xs)
        _OX[ch] = V((sg * max(0.0, e - DENTRO_MAX) - sg * max(0.0, f - FORA_MAX), 0.0, 0.0))
    return MEIO[k] + _OX[ch]
def mcp_andar(k, t):
    q = (t * FPS) % NQ; i = int(q); f = q - i
    m = AND[i]["pata"][k]["MCP"].lerp(AND[min(i + 1, NQ)]["pata"][k]["MCP"], f); return V((m.x, m.y, 0.0))
def delta_g(tr, k, t, tm):
    M = MEIO[k]; p, yaw = tr.corpo_de(t, tm, plantio(tr, k, tm)); d = p - (M + V((0, VEL * (t - tm), 0))); d = V((d.x, d.y, 0.0))
    r = mcp_andar(k, t) - V((M.x, M.y + VEL * (t - tm), 0.0))                 # v52: residuo do Andar (eixos do corpo)
    return d + (Matrix.Rotation(yaw, 3, Z) @ r - r), yaw                      # v52: residuo no rumo em que a pata pousou
def pata_curva(k, t, tr):
    ap, tm, fim = janela_apoio(k, t)
    if ap: return delta_g(tr, k, t, tm) + (True,)
    w = mj((t - fim) / (T_ - TS)); d0, y0 = delta_g(tr, k, fim, tm); tm2 = tm + T_; d1, y1 = delta_g(tr, k, tm2 - TS / 2, tm2)
    return d0.lerp(d1, w), y0 + (y1 - y0) * w, False
def pose_ik(k, g, G):
    sup, inf, pe, dedo = PATAS[k]; a, b = B[sup].length, B[inf].length; S = P[sup].head.copy()
    Mpe = G @ g["Mpe"]; Ct = Mpe.translation.copy()                       # carpo novo = cabeca do Metacarpo levado por G
    dv = Ct - S; dn = dv.normalized(); Lm = (a + b) * 0.9995; ds = min(Lm - 1e-4, max(IK_SUAVE * (a + b), g["ext"] * (a + b)))
    d = dv.length if dv.length <= ds else ds + (Lm - ds) * (1 - math.exp(-(dv.length - ds) / (Lm - ds)))   # v46b r4: IK suave
    al = (a * a - b * b + d * d) / (2 * d); h = math.sqrt(max(a * a - al * al, 0.0))
    dob = G.to_3x3() @ g["dob"]; perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0, xr in ((sup, S, K, G.to_3x3() @ g["xs"]), (inf, K, S + dn * d, G.to_3x3() @ g["xi"])):
        yv = (t0 - h0).normalized(); xv = (xr - yv * xr.dot(yv)).normalized()
        Mm = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); Mm.translation = h0; P[nome].matrix = Mm; bpy.context.view_layer.update()
    Mm = Mpe.copy(); Mm.translation = P[inf].tail.copy(); P[pe].matrix = Mm; bpy.context.view_layer.update()
    Mm = G @ g["Mdedo"]; Mm.translation = P[pe].tail.copy(); P[dedo].matrix = Mm; bpy.context.view_layer.update()
    return (S + dn * d - Ct).length, d / (a + b)
REL = {"metodo": __doc__.split("Uso:")[0], "parametros": PAR, "andar": CJ, "fps": FPS, "acoes": {}}
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
for nome, cfg in CLIPES.items():
    oa, ob, ciclos = cfg[:3]; pico = cfg[3] if len(cfg) > 3 else None
    if pico is None: omf = (lambda oa, ob: (lambda t: math.radians(oa + (ob - oa) * suave(t / RAMPA_S))))(oa, ob)
    else: omf = (lambda pk, D: (lambda t: math.radians(pk) * math.sin(math.pi * t / D) ** 2 if 0.0 <= t <= D else 0.0))(pico, ciclos * T_)
    tr = Traj(omf)
    nq = NQ * ciclos; GAP = {}; VAL, ERR, EXT, APO, PIOR, OMQ = [], 0.0, {}, {k: [] for k in PATAS}, {}, []
    for q in range(nq + 1):
        t = q / FPS; g = AND[q % NQ]; omg = math.degrees(omf(t)); oml = math.degrees(omf(t + 0.15)); OMQ.append(round(omg, 4))
        s = 1 if omg >= 0 else -1; k_ = abs(omg) / PAR["omega_ref"]; kl = oml / PAR["omega_ref"]
        for pb in P: pb.matrix_basis.identity()
        for nm, (qq, ll) in g["basis"].items(): P[nm].rotation_quaternion = qq; P[nm].location = ll
        for nm in ("Pescoco1", "Pescoco2", "Cabeca"):
            if nm in P: P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(kl * PAR[nm]), 3, Z)) @ P[nm].rotation_quaternion
        for nm in ("Coluna1", "Coluna2", "Coluna3"):
            if nm in P: P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(s * k_ * PAR[nm]), 3, Z)) @ P[nm].rotation_quaternion
        for i, nm in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):
            if nm in P: P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(s * k_ * PAR["cauda"][i]), 3, Z)) @ P[nm].rotation_quaternion
        P["Quadril"].location = P["Quadril"].location + REST["Quadril"].to_3x3().inverted() @ V((0, 0, -PAR["baixar"] * k_ * k_))
        P["Quadril"].rotation_quaternion = q_global("Quadril", Matrix.Rotation(math.radians(-s * k_ * PAR["rolamento"]), 3, Y)) @ P["Quadril"].rotation_quaternion
        bpy.context.view_layer.update()
        e_ = 0.0
        for k in PATAS:
            d, yaw, apoiada = pata_curva(k, t, tr); APO[k].append(apoiada)
            M0 = g["pata"][k]["MCP"]; G = Matrix.Translation(V((M0.x + d.x, M0.y + d.y, 0))) @ Matrix.Rotation(yaw, 4, Z) @ Matrix.Translation(V((-M0.x, -M0.y, 0)))
            e, x = pose_ik(k, g["pata"][k], G); e_ = max(e_, e); EXT[k] = max(EXT.get(k, 0.0), x)
            if e > PIOR.get(k, (0,))[0]: PIOR[k] = (round(e, 4), q, apoiada, round(d.x, 3), round(d.y, 3), round(math.degrees(yaw), 1))
        ERR = max(ERR, e_)
        gd = P["Metacarpo_E"].tail.x - P["Metacarpo_D"].tail.x; gt = P["Metatarso_E"].tail.x - P["Metatarso_D"].tail.x
        if gd < GAP.get("d", (9,))[0]: GAP["d"] = (round(gd, 3), q, APO["DE"][-1], APO["DD"][-1], round(P["Metacarpo_E"].tail.y, 2), round(P["Metacarpo_D"].tail.y, 2))
        if gt < GAP.get("t", (9,))[0]: GAP["t"] = (round(gt, 3), q, APO["TE"][-1], APO["TD"][-1])
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
    ext = []                                                   # curva externa (pivo) por quadro, relativa ao quadro 0 do clipe
    for q in range(nq + 1):
        p_, s_ = tr.pose(q / FPS); ext.append([round(p_.x, 5), round(p_.y, 5), round(math.degrees(s_), 5)])
    lq = max((VAL[0][n][0].rotation_difference(VAL[nq][n][0])).angle for n in VAL[0])
    REL["acoes"][nome] = {"quadros": nq, "duracao_s": nq / FPS, "laco": ciclos == 1 and pico is None, "omega_ini_graus_s": oa, "omega_fim_graus_s": ob, "ciclos": ciclos, "pico_graus_s": pico,
                          "rampa_s": RAMPA_S if oa != ob else 0.0, "raio_pivo_final_studs": round(VEL / abs(math.radians(ob)), 3) if ob else None,
                          "v_studs_s": VEL, "giro_total_graus": ext[-1][2], "omega_por_quadro": OMQ, "externa_por_quadro_xy_psi": ext,
                          "apoio_por_quadro": APO, "erro_ik_max": round(ERR, 6), "extensao_max_perna": {k: round(x, 3) for k, x in EXT.items()},
                          "q0_x_qfim_graus": round(math.degrees(lq), 4), "pior_ik_por_pata": PIOR, "dentro_max": DENTRO_MAX, "fora_max": FORA_MAX, "ik_suave": IK_SUAVE, "centro_giro_y": CENTRO.y, "folga_lateral_min_MCP": GAP}
    print("V46", nome, "omega", oa, "->", ob, "q", nq, "giro", ext[-1][2], "erro_ik", round(ERR, 5), "folga(gap,q,apE,apD,yE,yD)", GAP, "ext", {k: round(x, 3) for k, x in EXT.items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
REL["versao"] = "v52"; json.dump(REL, open(os.path.join(OUT, "curvas_v46b.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("CURVAS_V46B_OK", flush=True)
