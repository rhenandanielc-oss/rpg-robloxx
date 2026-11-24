"""v47 (24/11/2026, pedido "virada de combate"; decisoes do usuario: PIVO NAS TRASEIRAS, 90 graus ~1,0 s, so em ameaca/defesa,
mordida emenda). VirarCombate90Esquerda/Direita e VirarCombate180Esquerda/Direita, em COPIA (base anim_v46c, so lida; saida <dir>).
Mesmo gerador aprovado das viradas v27/v44 (texto abaixo), com: centro do giro = MEIO DAS PATAS TRASEIRAS (as traseiras dao passinhos
quase no lugar e a frente varre o arco), passos rapidos (mais ciclos), cabeca/pescoco liderando mais forte, coluna e cauda mais
marcadas. Parametros = [PROPOSTA][A TESTAR]. Saida: viradas_combate_v47.json. Uso: blender -b anim_v46c/CR_LoboArtico_Anim.blend -P
gerar_virada_combate_v47.py -- anim_v47
--- texto da v44: ---
v44 (20/11/2026, pedido "viradas naturais" do lobo solitario): VIRADA CURTA com passos, em COPIA (anim_v44/; a biblioteca e
as acoes existentes ficam intactas). Mesmo gerador aprovado das viradas v27 (copia integral abaixo), so com outros parametros e
nomes: VirarCurtoEsquerda / VirarCurtoDireita = 45 graus em ~1,5 s (2 ciclos de passo), para o controlador trocar a rotacao
direta do pivo (shift lock) por passos nos desvios medios. Parametros = [PROPOSTA][A TESTAR]. Saida: viradas_curtas_v44.json.
Uso: blender -b anim_v43r5/CR_LoboArtico_Anim.blend -P viradas_curtas_v44.py -- anim_v44
--- texto original da v27: ---
v27 = v26 com CORRECAO DAS PERNAS QUE ENTRAVAM PARA DENTRO (pedido do usuario 10/11): na v26 a planta de cada apoio era o
repouso no rumo do MEIO do apoio; como o corpo gira sobre a pata plantada, no referencial do corpo a pata varre de lado
(~1 stud por apoio nas patas a 2,8 do pivo) e metade da varredura ia para DENTRO (ate 0,56; a perna cruzava o meio e chegava
a 0,21 da outra). v27: a POSICAO de cada planta e escolhida (bisseccao no rumo da planta) para que o alvo do MCP nunca entre mais
que dentro_max em relacao ao repouso durante o apoio (a varredura fica para FORA, abducao); a ORIENTACAO da pata plantada continua
no rumo do meio do apoio. Mais ciclos de passo (passos mais curtos) reduzem a varredura. Resto igual a v26.
L2b, 2o bloco (v26): VIRAR ESQUERDA e VIRAR DIREITA (giro no lugar com passos), acoes de uma vez, sobre copia da anim_v25 (so lida;
saida <dir>). As 6 acoes anteriores ficam intactas.
EIXOS: frente -Y, cima +Z, lado ESQUERDO do lobo = +X. Rumo externo psi em torno de +Z (anti-horario visto de cima). VirarEsquerda:
psi 0 -> +90 graus (a frente vai de -Y para +X); VirarDireita: psi 0 -> -90 graus. 90 graus = parametro tecnico (ANGULO), nao regra.
CONTRATO: Raiz FIXA nos ossos (clipe no lugar). Transformacao EXTERNA (apresentacao/jogo), gravada em viradas_v26.json por quadro:
rumo psi(t) e translacao T(t) = P - Rz(psi) P (pivo P = centro das 4 patas no repouso, fica parado no mundo); posicao mundial = T +
Rz(psi) * posicao deformada local. No fim os ossos estao no Repouso q0 (continua o Repouso no rumo novo).
Gerador: psi(t) com aceleracao e frenagem suaves (perfil trapezoidal de velocidade angular); passos por ciclos de marcha (n ciclos,
fracao de apoio beta, ordem das patas por lado: Esquerda DE -> TD -> DD -> TE, Direita DD -> TE -> DE -> TD); cada pata plantada
guarda POSICAO e ORIENTACAO no mundo (a pata gira em relacao ao corpo com uma guinada propria no metacarpo/dedos: a sola nao
pivota contra o chao); pouso = posicao do repouso no rumo do MEIO do proximo apoio (apoio centrado); ultimo pouso = repouso no
rumo final; balanco min-jerk no mundo com altura e dobra de passo; rolamento da v24 so antes de levantar. Corpo = Repouso q0 +
cabeca/pescoco que antecipam o giro, coluna em curva para o lado do giro, cauda em contrapeso com atraso, e transferencia de peso
(quadril desloca para longe da pata no ar). IK analitico de 2 ossos gravado em FK (mesmo de marcha_v21, com guinada da pata).
Uso: blender -b anim_v26/CR_LoboArtico_Anim.blend -P viradas_v27.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix
import marcha_v21 as M
DOC_V = "v27"
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); FPS = M.FPS; ARM = M.ARM; P = M.P; B = M.B; X, Y, Z = M.X, M.Y, M.Z
PAR = {"angulo": 90.0, "ant_s": 0.15, "giro_s": 1.10, "acomoda_s": 0.30, "ciclos": 2, "beta": 0.55, "rampa": 0.25, "h": 0.30, "dobra_D": 70.0, "dobra_T": 55.0,
       "rolo_graus": 12.0, "cabeca_graus": 10.0, "cabeca2_graus": 4.0, "cabeca3_graus": 7.0, "coluna_graus": 3.5, "cauda_graus": 7.0,
       "lider_cabeca_s": 0.15, "atraso_cauda_s": 0.12, "peso_x": 0.05, "dentro_max": 0.10}
COMBATE = json.loads(os.environ["COMBATE_V47"]) if os.environ.get("COMBATE_V47") else None
COMBATE = {int(k): v for k, v in COMBATE.items()} if COMBATE else {45: {"ant_s": 0.06, "giro_s": 0.46, "acomoda_s": 0.12, "ciclos": 2, "beta": 0.45, "h": 0.26, "rampa": 0.25},
           90: {"ant_s": 0.08, "giro_s": 0.78, "acomoda_s": 0.14, "ciclos": 4, "beta": 0.45, "h": 0.28, "rampa": 0.22},
           180: {"ant_s": 0.08, "giro_s": 1.36, "acomoda_s": 0.16, "ciclos": 7, "beta": 0.45, "h": 0.28, "rampa": 0.18}}
ANGS = [int(a) for a in os.environ.get("ANGS_V47", "45,90,180").split(",")]   # v47b r2: + 45 graus (~0,6 s) para nao passar do ponto
PAR.update({"baixar": float(os.environ.get("BAIXAR_V47", "0.18")), "cabeca_graus": 18.0, "cabeca2_graus": 8.0, "cabeca3_graus": 12.0, "coluna_graus": 6.0, "cauda_graus": 12.0, "lider_cabeca_s": 0.08, "atraso_cauda_s": 0.08})
if os.environ.get("AJUSTE_V47"): PAR.update(json.loads(os.environ["AJUSTE_V47"]))
LEG = {n for c in M.PATAS.values() for n in c}; SIDE = {"DE": 1, "TE": 1, "DD": -1, "TD": -1}
_YT = (M.MCP0["TE"].y + M.MCP0["TD"].y) / 2; _YF = (M.MCP0["DE"].y + M.MCP0["DD"].y) / 2
PIVO_FRAC = float(os.environ.get("PIVO_FRAC_V47", "0.25"))                   # 0 = meio das traseiras; 1 = meio das dianteiras
PIVO = V((0.0, _YT + PIVO_FRAC * (_YF - _YT), 0))                          # v47: centro do giro nas TRASEIRAS (ou um pouco a frente)
# rolamento v24 + guinada da pata
ARM.animation_data.action = None
for pb in P: pb.matrix_basis.identity()
bpy.context.view_layer.update()
C_ = bpy.data.objects["LOW_Corpo"]; me = C_.data; gn = {g.index: g.name for g in C_.vertex_groups}; SOLA = {}
for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"]):
    ids = [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8]; zs = min(me.vertices[i].co.z for i in ids)
    pad = [me.vertices[i].co for i in ids if me.vertices[i].co.z < zs + 0.03 and max(((gn[g.group], g.weight) for g in me.vertices[i].groups), key=lambda t: t[1])[0] == M.PATAS[k][3]]
    pc = sum(pad, V()) / len(pad); SOLA[k] = {"z_sola": zs, "almofada": V((pc.x, pc.y, zs))}
def alvo(k, p, dz, rolo, dobra, yaw):
    Rz = Matrix.Rotation(yaw, 3, Z); tv = Rz @ (M.TIP0[k] - M.MCP0[k]); Cf = p + 0.8 * tv; lp = 0.20 if k[0] == "D" else 0.25
    Cg = Cf - V((0, 0, lp * (Cf.z - (SOLA[k]["z_sola"] + dz)))); m_ef = Cg + Matrix.Rotation(rolo, 3, Rz @ X) @ (p - Cg)
    pl = SOLA[k]["almofada"] - M.MCP0[k]; nd = Rz.inverted() @ ((p + Rz @ pl) - m_ef)
    return m_ef, rolo + dobra, math.atan2(nd.z, nd.y) - math.atan2(pl.z, pl.y) + 0.45 * dobra, yaw
def ik(k, mcp, phi, phi_dedo, yaw):
    """= marcha_v21.ik com GUINADA yaw (em torno de +Z do armature) aplicada ao metacarpo/metatarso e aos dedos"""
    sup, inf, pe, dedo = M.PATAS[k]; bs, bi = B[sup], B[inf]; a, b = bs.length, bi.length
    Rz = Matrix.Rotation(yaw, 3, Z); Rp = Rz @ Matrix.Rotation(phi, 3, X); T = mcp + Rp @ (M.CAR0[k] - M.MCP0[k])
    S = P[sup].head.copy(); Mpai = P[sup].parent.matrix @ B[sup].parent.matrix_local.inverted()
    K0, S0 = bs.tail_local, bs.head_local; d0 = (bi.tail_local - S0).normalized()
    dob = Mpai.to_3x3() @ ((K0 - S0) - d0 * (K0 - S0).dot(d0))
    dv = T - S; d = min(dv.length, (a + b) * 0.9995); dn = dv.normalized()
    al = (a * a - b * b + d * d) / (2 * d); h = math.sqrt(max(a * a - al * al, 0.0)); perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0 in ((sup, S, K), (inf, K, S + dn * d)):
        yv = (t0 - h0).normalized(); xr = Mpai.to_3x3() @ M.REST[nome].col[0].to_3d(); xv = (xr - yv * xr.dot(yv)).normalized()
        Mm = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); Mm.translation = h0; P[nome].matrix = Mm; bpy.context.view_layer.update()
    Mm = (Rp.to_4x4() @ Matrix.Translation(-M.MCP0[k]) @ M.REST[pe]); Mm.translation = P[inf].tail.copy(); P[pe].matrix = Mm; bpy.context.view_layer.update()
    Mm = (Rz.to_4x4() @ Matrix.Rotation(phi_dedo, 4, X)) @ Matrix.Translation(-M.MCP0[k]) @ M.REST[dedo]; Mm.translation = P[pe].tail.copy(); P[dedo].matrix = Mm
    bpy.context.view_layer.update()
    return (S + dn * d - T).length, d / (a + b)
ac = bpy.data.actions["Repouso"]; ARM.animation_data.action = ac
if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
bpy.context.scene.frame_set(0); REP = ({pb.name: pb.rotation_quaternion.copy() for pb in P if pb.name not in LEG}, P["Quadril"].location.copy())
ARM.animation_data.action = None
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def mj(w): w = max(0.0, min(1.0, w)); return w * w * w * (10 - 15 * w + 6 * w * w)
REL = {"parametros": PAR, "eixos": {"frente": "-Y", "cima": "+Z", "esquerda_do_lobo": "+X", "rumo": "psi em torno de +Z, anti-horario visto de cima"},
       "pivo": [round(x, 4) for x in PIVO], "fps": FPS, "acoes": {}}
def gerar(nome, s):
    A_ = math.radians(PAR["angulo"]) * s; t0, D_ = PAR["ant_s"], PAR["giro_s"]; nq = int(round((t0 + D_ + PAR["acomoda_s"]) * FPS)); dur = nq / FPS; r = PAR["rampa"]
    def omega_n(t):                                                # velocidade angular normalizada (trapezio suavizado), integral = 1 em [t0, t0+D]
        x = (t - t0) / D_
        if x <= 0 or x >= 1: return 0.0
        return (suave(x / r) if x < r else (suave((1 - x) / r) if x > 1 - r else 1.0)) / (1 - r) / D_
    NS = 4000; tg = [dur * i / NS for i in range(NS + 1)]; ps = [0.0]
    for i in range(1, NS + 1): ps.append(ps[-1] + 0.5 * (omega_n(tg[i]) + omega_n(tg[i - 1])) * (tg[i] - tg[i - 1]))
    k_ = 1.0 / ps[-1]
    def psi(t):
        if t <= 0: return 0.0
        if t >= dur: return A_
        i = min(NS - 1, int(t / dur * NS)); f = (t - tg[i]) / (tg[i + 1] - tg[i]); return A_ * k_ * (ps[i] + f * (ps[i + 1] - ps[i]))
    def Tw(ps_): return PIVO - Matrix.Rotation(ps_, 3, Z) @ PIVO
    def mundo(k, ps_):                                             # posicao (x, y) mundial do MCP de repouso da pata k com o corpo no rumo ps_
        w = Tw(ps_) + Matrix.Rotation(ps_, 3, Z) @ V((M.MCP0[k].x, M.MCP0[k].y, 0)); return V((w.x, w.y, 0))
    fase = ({"DE": 0.0, "TD": 0.25, "DD": 0.50, "TE": 0.75} if s > 0 else {"DD": 0.0, "TE": 0.25, "DE": 0.50, "TD": 0.75})
    n, beta = PAR["ciclos"], PAR["beta"]; th2t = lambda th: t0 + th / n * D_
    plano = {}
    for k in M.PATAS:
        sw = [(th2t(j + fase[k]), th2t(j + fase[k] + 1 - beta)) for j in range(n)]
        est = []; ini = 0.0
        for j, (a0, a1) in enumerate(sw): est.append([ini, a0]); ini = a1
        est.append([ini, dur])
        pl = [(mundo(k, 0.0), 0.0)]; sg = 1 if k[1] == "E" else -1
        def dentro(W, a0, a1):                                     # maior entrada (para o meio) do alvo do MCP no apoio, em relacao ao repouso
            mx = -9.0
            for i in range(41):
                t = a0 + (a1 - a0) * i / 40; ps_ = psi(t); p = Matrix.Rotation(-ps_, 3, Z) @ (W - Tw(ps_)); mx = max(mx, sg * (M.MCP0[k].x - p.x))
            return mx
        for j in range(1, len(est)):
            a0, a1 = est[j]
            if j == len(est) - 1: pl.append((mundo(k, A_), A_)); continue
            hm = psi(0.5 * (a0 + a1)); hs = abs(psi(a1) - psi(a0)) * 1.5 + 1e-4
            if dentro(mundo(k, hm), a0, a1) <= PAR["dentro_max"]: pl.append((mundo(k, hm), hm)); continue
            dr = 1 if dentro(mundo(k, hm + 0.01), a0, a1) < dentro(mundo(k, hm), a0, a1) else -1; lo, hi = hm, hm + dr * hs
            for _ in range(40):
                md = 0.5 * (lo + hi)
                if dentro(mundo(k, md), a0, a1) > PAR["dentro_max"]: lo = md
                else: hi = md
            pl.append((mundo(k, hi), hm))                             # posicao deslocada para fora; orientacao no rumo do meio
        plano[k] = {"apoios": est, "balancos": sw, "plantas": pl}
    def pata(k, t):
        Pk = plano[k]; ps_ = psi(t); Rinv = Matrix.Rotation(-ps_, 3, Z); Tt = Tw(ps_)
        for j, (a0, a1) in enumerate(Pk["apoios"]):
            if a0 <= t <= a1:
                W, hd = Pk["plantas"][j]; p = Rinv @ (W - Tt); sp = (t - a0) / max(1e-6, a1 - a0)
                ultimo = j == len(Pk["apoios"]) - 1; rolo = 0.0 if ultimo else math.radians(PAR["rolo_graus"]) * suave((sp - 0.72) / 0.28)
                return V((p.x, p.y, M.MCP0[k].z)), 0.0, rolo, 0.0, hd - ps_, True, 0.0
        for j, (a0, a1) in enumerate(Pk["balancos"]):
            if a0 < t < a1:
                w = (t - a0) / (a1 - a0); m = mj(w); W0, h0 = Pk["plantas"][j]; W1, h1 = Pk["plantas"][j + 1]
                W = W0 + (W1 - W0) * m; hd = h0 + (h1 - h0) * m; p = Rinv @ (W - Tt); dz = M.altura_balanco(PAR["h"], w)
                sg = 1 if k[1] == "E" else -1; ex_ = sg * (M.MCP0[k].x - p.x) - PAR["dentro_max"]   # no AR: a corda do giro nao puxa a pata para dentro
                if ex_ > 0: p = p + V((sg * ex_ * suave(min(w, 1 - w) / 0.15), 0, 0))
                dob = math.radians(PAR["dobra_" + k[0]]) * math.sin(math.pi * w) ** 1.5 * (1 - suave((w - 0.7) / 0.3))
                rolo = math.radians(PAR["rolo_graus"]) * (1 - suave((w - 0.2) / 0.4))
                return V((p.x, p.y, M.MCP0[k].z + dz)), dz, rolo, dob, hd - ps_, False, math.sin(math.pi * w)
        raise RuntimeError((k, t))
    def om(t): return omega_n(t) * D_ * (1 - r)                       # 0..1
    LAT = {}; VAL = []; ERR = 0.0; EXT = {}; LOG = {"psi_graus": [], "T": [], "apoio": {k: [] for k in M.PATAS}, "omega_graus_s": []}
    for pb in P: pb.rotation_mode = "QUATERNION"
    for q in range(nq + 1):
        t = q / FPS; Rx = {}
        def add(nm, e, g): Rx.setdefault(nm, []).append((e, g))
        lid = om(t + PAR["lider_cabeca_s"]); cor = om(t); cau = om(t - PAR["atraso_cauda_s"])
        add("Pescoco1", Z, s * PAR["cabeca_graus"] * lid); add("Pescoco2", Z, s * PAR["cabeca2_graus"] * lid); add("Cabeca", Z, s * PAR["cabeca3_graus"] * lid)
        for nm, f in (("Coluna1", 0.8), ("Coluna2", 1.0), ("Coluna3", 0.8)): add(nm, Z, s * PAR["coluna_graus"] * f * cor)
        for i, nm in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")): add(nm, Z, s * PAR["cauda_graus"] * (0.7 + 0.3 * i) * cau)
        pes = {k: pata(k, t) for k in M.PATAS}
        qx = V((-PAR["peso_x"] * sum(SIDE[k] * pes[k][6] for k in M.PATAS), 0, -0.02 * sum(pes[k][6] for k in M.PATAS) - PAR.get("baixar", 0.0) * suave(min(t, dur - t) / 0.18)))   # v47: agacha na briga
        M.aplicar_corpo(Rx, qx); ex = ({pb.name: pb.rotation_quaternion.copy() for pb in P if pb.name not in LEG}, P["Quadril"].location.copy())
        for pb in P: pb.matrix_basis.identity()
        for nm, qq in REP[0].items(): P[nm].rotation_quaternion = ex[0][nm] @ qq
        P["Quadril"].location = REP[1] + ex[1]; bpy.context.view_layer.update()
        e_ = 0.0
        for k in M.PATAS:
            p, dz, rolo, dob, yaw, ap, _ = pes[k]; m_ef, phi, phd, yw = alvo(k, p, dz, rolo, dob, yaw); e, x = ik(k, m_ef, phi, phd, yw); e_ = max(e_, e); EXT[k] = max(EXT.get(k, 0), x)
            LOG["apoio"][k].append(ap); sg_ = 1 if k[1] == "E" else -1; LAT.setdefault(k, []).append(sg_ * (p.x - M.MCP0[k].x))
        for c in M.PATAS.values():
            for nm in c: P[nm].location = (0, 0, 0)
        bpy.context.view_layer.update(); ERR = max(ERR, e_)
        ps_ = psi(t); Tt = Tw(ps_); LOG["psi_graus"].append(round(math.degrees(ps_), 5)); LOG["T"].append([round(Tt.x, 5), round(Tt.y, 5)])
        LOG["omega_graus_s"].append(round(math.degrees(A_) * omega_n(t), 4))
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
    REL["acoes"][nome] = {"parametros_desta": dict(PAR), "quadros": nq, "duracao_s": round(nq / FPS, 4), "laco": False, "angulo_final_graus": round(math.degrees(A_), 3), "sinal": s,
                          "psi_graus_por_quadro": LOG["psi_graus"], "T_por_quadro": LOG["T"], "omega_graus_s_por_quadro": LOG["omega_graus_s"],
                          "apoio_por_quadro": LOG["apoio"], "ordem_patas": fase,
                          "apoios_s": {k: [[round(a, 4), round(b, 4)] for a, b in plano[k]["apoios"]] for k in plano},
                          "plantas_mundo": {k: [[round(W.x, 4), round(W.y, 4), round(math.degrees(h), 3)] for W, h in plano[k]["plantas"]] for k in plano},
                          "erro_ik_max": round(ERR, 6), "extensao_max_perna": {k: round(x, 3) for k, x in EXT.items()},
                          "T_final": LOG["T"][-1], "alvo_mcp_lateral": {k: {"dentro_max": round(-min(v), 4), "fora_max": round(max(v), 4)} for k, v in LAT.items()}}
    print("V47", nome, nq, "erro_ik", round(ERR, 6), "ext", {k: round(x, 3) for k, x in EXT.items()}, "T_fim", LOG["T"][-1], "lateral", {k: (round(-min(v), 3), round(max(v), 3)) for k, v in LAT.items()}, flush=True)
for ang in ANGS:
    PAR.update(COMBATE[ang]); PAR["angulo"] = float(ang)
    gerar("VirarCombate%dEsquerda" % ang, +1); gerar("VirarCombate%dDireita" % ang, -1)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "viradas_combate_v47.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("VIRADAS_COMBATE_V47_OK", flush=True)
