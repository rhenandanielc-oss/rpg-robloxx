"""v46 (20/11/2026, pedido "mudar de direcao caminhando em curva"): ANDAR EM CURVA, em COPIA (anim_v45r3 so lida; saida <dir>).
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
       "cauda": [-1.5, -2.3, -3.1, -4.0], "rolamento": 1.5, "baixar": 0.10}
if os.environ.get("AJUSTE_V46"): PAR.update(json.loads(os.environ["AJUSTE_V46"]))
CLIPES = {"AndarCurvaEsquerda": 30.0, "AndarCurvaDireita": -30.0, "AndarCurvaFechadaEsquerda": 50.0, "AndarCurvaFechadaDireita": -50.0}
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
        g["pata"][k] = {"S": S, "C": C, "dob": b, "xs": P[sup].matrix.col[0].to_3d().copy(), "xi": P[inf].matrix.col[0].to_3d().copy(),
                        "Mpe": P[pe].matrix.copy(), "Mdedo": P[dedo].matrix.copy(), "MCP": P[pe].tail.copy()}
    AND.append(g)
ARM.animation_data.action = None
def u_de(k, t): return ((t / T_) - FASE[k]) % 1.0
MEIO = {}                                                    # MCP no meio do apoio (referencial do corpo, Andar reto)
for k in PATAS:
    tm = ((FASE[k] + BETA / 2) % 1.0) * T_; q = tm * FPS; i = int(q) % NQ; f = q - int(q)
    MEIO[k] = AND[i]["pata"][k]["MCP"].lerp(AND[i + 1]["pata"][k]["MCP"], f)
def arco(M, tau, om):
    if abs(om) < 1e-9: return M + V((0, VEL * tau, 0))
    th = om * tau; Pp = V(((VEL / om) * (1 - math.cos(th)), -(VEL / om) * math.sin(th), 0.0))
    return Matrix.Rotation(-th, 3, Z) @ (M - Pp)
def delta(k, tau, om):
    M = MEIO[k]; d = arco(M, tau, om) - (M + V((0, VEL * tau, 0))); return V((d.x, d.y, 0.0)), -om * tau
def pata_curva(k, t, om):
    u = u_de(k, t)
    if u < BETA: return delta(k, (u / BETA - 0.5) * TS, om) + (True,)
    w = mj((u - BETA) / (1 - BETA)); d0, y0 = delta(k, TS / 2, om); d1, y1 = delta(k, -TS / 2, om)
    return d0.lerp(d1, w), y0 + (y1 - y0) * w, False
def pose_ik(k, g, G):
    sup, inf, pe, dedo = PATAS[k]; a, b = B[sup].length, B[inf].length; S = P[sup].head.copy()
    Mpe = G @ g["Mpe"]; Ct = Mpe.translation.copy()                       # carpo novo = cabeca do Metacarpo levado por G
    dv = Ct - S; d = min(dv.length, (a + b) * 0.9995); dn = dv.normalized()
    al = (a * a - b * b + d * d) / (2 * d); h = math.sqrt(max(a * a - al * al, 0.0))
    dob = G.to_3x3() @ g["dob"]; perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0, xr in ((sup, S, K, G.to_3x3() @ g["xs"]), (inf, K, S + dn * d, G.to_3x3() @ g["xi"])):
        yv = (t0 - h0).normalized(); xv = (xr - yv * xr.dot(yv)).normalized()
        Mm = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); Mm.translation = h0; P[nome].matrix = Mm; bpy.context.view_layer.update()
    Mm = Mpe.copy(); Mm.translation = P[inf].tail.copy(); P[pe].matrix = Mm; bpy.context.view_layer.update()
    Mm = G @ g["Mdedo"]; Mm.translation = P[pe].tail.copy(); P[dedo].matrix = Mm; bpy.context.view_layer.update()
    return (S + dn * d - Ct).length, d / (a + b)
REL = {"metodo": __doc__.split("Uso:")[0], "parametros": PAR, "andar": CJ, "fps": FPS, "acoes": {}}
for nome, om_g in CLIPES.items():
    om = math.radians(om_g); s = 1 if om_g > 0 else -1; k_ = abs(om_g) / PAR["omega_ref"]
    VAL, ERR, EXT, APO, PIOR = [], 0.0, {}, {k: [] for k in PATAS}, {}
    for q in range(NQ + 1):
        t = q / FPS; g = AND[q]
        for pb in P: pb.matrix_basis.identity()
        for nm, (qq, ll) in g["basis"].items(): P[nm].rotation_quaternion = qq; P[nm].location = ll
        for nm in ("Pescoco1", "Pescoco2", "Cabeca", "Coluna1", "Coluna2", "Coluna3"):
            if nm in P: P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(s * k_ * PAR[nm]), 3, Z)) @ P[nm].rotation_quaternion
        for i, nm in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):
            if nm in P: P[nm].rotation_quaternion = q_global(nm, Matrix.Rotation(math.radians(s * k_ * PAR["cauda"][i]), 3, Z)) @ P[nm].rotation_quaternion
        P["Quadril"].location = P["Quadril"].location + REST["Quadril"].to_3x3().inverted() @ V((0, 0, -PAR["baixar"] * k_ * k_))
        P["Quadril"].rotation_quaternion = q_global("Quadril", Matrix.Rotation(math.radians(-s * k_ * PAR["rolamento"]), 3, Y)) @ P["Quadril"].rotation_quaternion
        bpy.context.view_layer.update()
        e_ = 0.0
        for k in PATAS:
            d, yaw, apoiada = pata_curva(k, t, om); APO[k].append(apoiada)
            M0 = g["pata"][k]["MCP"]; G = Matrix.Translation(V((M0.x + d.x, M0.y + d.y, 0))) @ Matrix.Rotation(yaw, 4, Z) @ Matrix.Translation(V((-M0.x, -M0.y, 0)))
            e, x = pose_ik(k, g["pata"][k], G); e_ = max(e_, e); EXT[k] = max(EXT.get(k, 0.0), x)
            if e > PIOR.get(k, (0,))[0]: PIOR[k] = (round(e, 4), q, apoiada, round(d.x, 3), round(d.y, 3), round(math.degrees(yaw), 1))
        ERR = max(ERR, e_)
        VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); ARM.animation_data.action = acn
    for qi, vals in enumerate(VAL):
        for pb in P:
            pb.rotation_quaternion, pb.location = vals[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=qi, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=qi, group=pb.name)
    acn.use_fake_user = True; acn.frame_range = (0, NQ); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    ext = []                                                   # curva externa (pivo) por quadro, do quadro 0 do ciclo
    for q in range(NQ + 1):
        th = om * q / FPS; ext.append([round((VEL / om) * (1 - math.cos(th)), 5), round(-(VEL / om) * math.sin(th), 5), round(math.degrees(th), 5)])
    lq = max((VAL[0][n][0].rotation_difference(VAL[NQ][n][0])).angle for n in VAL[0])
    REL["acoes"][nome] = {"quadros": NQ, "duracao_s": NQ / FPS, "laco": True, "omega_graus_s": om_g, "raio_pivo_studs": round(VEL / abs(om), 3),
                          "v_studs_s": VEL, "giro_por_ciclo_graus": round(om_g * T_, 3), "externa_por_quadro_xy_psi": ext,
                          "apoio_por_quadro": APO, "erro_ik_max": round(ERR, 6), "extensao_max_perna": {k: round(x, 3) for k, x in EXT.items()},
                          "laco_q0_x_qfim_graus": round(math.degrees(lq), 4), "pior_ik_por_pata": PIOR}
    print("V46", nome, "omega", om_g, "raio", round(VEL / abs(om), 2), "erro_ik", round(ERR, 5), "ext", {k: round(x, 3) for k, x in EXT.items()},
          "laco", round(math.degrees(lq), 4), "pior(erro,q,apoio,dx,dy,guin)", PIOR, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "curvas_v46.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("CURVAS_V46_OK", flush=True)
