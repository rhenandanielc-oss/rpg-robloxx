"""v30: PATAS DIANTEIRAS que viravam demais no balanco (pedido do usuario: "as patas da frente se viram muito, parecendo bugado").
Diagnostico (diag_patas_giro_v30.py): no balanco o carpo dobrava ate 105 graus no Andar, 120 no Trote e 141 na Corrida e os dedos
ate 85-92 graus: a pata virava com a sola para cima/tras, o punho da malha estrangulava e a DE (inclinada 18,7 graus no repouso do rig)
parecia girar para fora.
Correcao = POS-PROCESSO so nos ossos das DIANTEIRAS (Umero, Antebraco, Metacarpo, Dedos), SO NO BALANCO (apoio do cronograma de cada acao = 0); as patas no
apoio e todos os outros ossos ficam IDENTICOS (deslize inalterado por construcao):
- carpo: angulo theta (Antebraco x Metacarpo) comprimido acima de theta0 com joelho suave: theta' = theta - (1-r)*rampa(theta-theta0),
  rampa(x) = 0 (x<=0), x^2/(2w) (x<w), x-w/2; rotacao do Metacarpo em torno do eixo yAntebraco x yMetacarpo (no plano da dobra, o que
  tambem tira parte do giro lateral);
- dedos: o mesmo com phi (Metacarpo x Dedos), depois do carpo;
- folga: a pata menos dobrada fica mais baixa; o PUNHO sobe (so no balanco) o necessario para a pata manter a folga da v29 na malha
  LOW (limitada a folga_alvo), com o IK de 2 ossos do braco refeito (mesmo plano/rolagem da marcha_v21) e a orientacao corrigida do
  pe; subida suavizada no tempo. Umero/Antebraco/Metacarpo/Dedos das dianteiras regravados (so quadros de balanco mudam);
- peso no balanco: entra em 'rampa_q' quadros depois da saida da pata e sai nos ultimos 'rampa_q' antes do toque (suave), 0 no apoio.
Lacos (Andar/Trote/Corrida) continuam lacos (mesma regra nos dois extremos). Uso:
blender -b anim_v29/CR_LoboArtico_Anim.blend -P patas_dianteiras_v30.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
import marchas_v29 as MV
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
PAR = {"carpo_theta0": 30.0, "carpo_r": 0.35, "carpo_w": 15.0, "dedos_phi0": 28.0, "dedos_r": 0.35, "dedos_w": 12.0, "rampa_q": 2, "folga_alvo": 0.06, "ponta_q": 6}
if os.environ.get("AJUSTE_V30"): PAR.update(json.loads(os.environ["AJUSTE_V30"]))
ARM = M.ARM; P = M.P; sc = bpy.context.scene; FPS = 30
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); G = MV.marchas(CJ)
TJ = {}
for fn in ("marchas_v29.json", "transicoes_v25.json", "viradas_v27.json"):
    for k, v in json.load(open(os.path.join(SRC, fn)))["acoes"].items(): TJ[k] = v
FRENTE = {"DE": ("Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Antebraco_D", "Metacarpo_D", "Dedos_D")}
def apoio(ac, k, q):
    if ac in TJ: return bool(TJ[ac]["apoio_por_quadro"][k][q])
    return bool(MV.apoio(G, {"acoes": {}}, ac, k, q))
def rampa(x, w): return 0.0 if x <= 0 else (x * x / (2 * w) if x < w else x - w / 2)
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def pesos(ac, k, n, laco):
    ap = [apoio(ac, k, q) for q in range(n + 1)]; w = [0.0] * (n + 1); R = PAR["rampa_q"]; L = n if laco else n + 1
    def nao_apoio(j):
        if laco: return not ap[j % n]
        return 0 <= j <= n and not ap[j]
    for i in range(L):
        if ap[i]: continue
        a = 0
        while a < L and nao_apoio(i - a - 1): a += 1
        b = 0
        while b < L and nao_apoio(i + b + 1): b += 1
        if not laco:                                            # pontas da acao sem apoio: conta como meio do balanco (continua fora)
            if i - a - 1 < 0: a = L
            if i + b + 1 > n: b = L
        w[i] = suave((a + 0.5) / (R + 0.5)) * suave((b + 0.5) / (R + 0.5)) if R > 0 else 1.0
    if laco: w[n] = w[0]
    return w, ap
def girar(osso, eixo, graus):
    pb = P[osso]; h = pb.head.copy(); Mx = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h)
    pb.matrix = Mx @ pb.matrix; bpy.context.view_layer.update()
def ang(u, w): return math.degrees(math.acos(max(-1, min(1, u.normalized().dot(w.normalized())))))
# folga na malha LOW (protecao): menor z da regiao da pata - z da sola no repouso
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); CORPO = bpy.data.objects["LOW_Corpo"]; ARM.animation_data.action = None
for pb in P: pb.matrix_basis.identity()
bpy.context.view_layer.update()
IDS = {k: [v.index for v in CORPO.data.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
CHAO = {k: min(CORPO.data.vertices[i].co.z for i in v) for k, v in IDS.items()}
def folga(k):
    dg = bpy.context.evaluated_depsgraph_get(); e = CORPO.evaluated_get(dg); m = e.to_mesh(); z = min(m.vertices[i].co.z for i in IDS[k]) - CHAO[k]; e.to_mesh_clear(); return z
REL = {"parametros": PAR, "acoes": {}}
for pb in P: pb.rotation_mode = "QUATERNION"
ACS = ["Andar", "Trote", "Corrida"] + sorted(a.name for a in bpy.data.actions if a.name in TJ)   # marchas primeiro (as transicoes copiam as pontas)
CONTEXTO = {"Arrancada": ("Repouso", "Corrida"), "Frenagem": ("Corrida", "Repouso"), "VirarEsquerda": ("Repouso", "Repouso"), "VirarDireita": ("Repouso", "Repouso")}
for _n, _a in TJ.items():
    if "origem" in _a: CONTEXTO[_n] = (_a["origem"], _a["destino"])
GFIN = {}                                                           # marcha -> (pesos, subida do punho) finais por quadro e pata
CADEIA = {"DE": ("Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D")}
def ik_braco(k, T):
    """IK de 2 ossos (Umero, Antebraco) ate o punho T, mesmo plano/rolagem da marcha_v21.ik"""
    sup, inf = CADEIA[k][:2]; bs, bi = M.B[sup], M.B[inf]; a_, b_ = bs.length, bi.length
    S = P[sup].head.copy(); Mpai = P[sup].parent.matrix @ M.B[sup].parent.matrix_local.inverted()
    K0, S0 = bs.tail_local, bs.head_local; d0 = (bi.tail_local - S0).normalized(); dob = Mpai.to_3x3() @ ((K0 - S0) - d0 * (K0 - S0).dot(d0))
    dv = T - S; d = min(dv.length, (a_ + b_) * 0.9995); dn = dv.normalized()
    al = (a_ * a_ - b_ * b_ + d * d) / (2 * d); h = math.sqrt(max(a_ * a_ - al * al, 0.0)); perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0 in ((sup, S, K), (inf, K, S + dn * d)):
        yv = (t0 - h0).normalized(); xr = Mpai.to_3x3() @ M.REST[nome].col[0].to_3d(); xv = (xr - yv * xr.dot(yv)).normalized()
        Mx = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); Mx.translation = h0; P[nome].matrix = Mx; bpy.context.view_layer.update()
    return (S + dn * d - T).length
def dobra_dobradica(pai, filho):
    """angulo assinado (graus) do osso filho em relacao ao pai em torno do eixo X do pai (dobradica do carpo/dedos), com as direcoes
    projetadas no plano perpendicular a esse eixo; devolve (angulo, eixo)"""
    # eixo = X do corpo (lateral), o mesmo da dobra do pe no IK original (marcha_v21.ik: Rotation(phi, X)); girar em torno dele
    # mantem a componente lateral do pe igual a da v29 (o eixo X do antebraco no galope e inclinado e fazia as patas cruzarem)
    x = V((1.0, 0.0, 0.0)); a_ = P[pai].matrix.col[1].xyz; b_ = P[filho].matrix.col[1].xyz
    a_ = (a_ - x * a_.dot(x)).normalized(); b_ = (b_ - x * b_.dot(x)).normalized()
    return math.degrees(math.atan2(a_.cross(b_).dot(x), a_.dot(b_))), x
def montar_pata(k, base, w, dz):
    """a partir da pose base: (1) corrige carpo/dedos com peso w; (2) sobe o punho dz e refaz o IK do braco mantendo a orientacao
    corrigida do pe e dos dedos. Devolve erro do IK"""
    sup, inf, met, ded = CADEIA[k]
    for nm in (sup, inf, met, ded):
        P[nm].matrix = base[nm]; bpy.context.view_layer.update()
    if w > 0:
        for pai, filho, nt, nr, nw in ((inf, met, "carpo_theta0", "carpo_r", "carpo_w"), (met, ded, "dedos_phi0", "dedos_r", "dedos_w")):
            th, eixo = dobra_dobradica(pai, filho)                 # angulo NA DOBRADICA (eixo X local do osso pai)
            dd_ = w * (1 - PAR[nr]) * rampa(abs(th) - PAR[nt], PAR[nw])
            if dd_ > 1e-6: girar(filho, eixo, -math.copysign(dd_, th))
    if dz <= 1e-7: return 0.0
    om, od = P[met].matrix.to_3x3().to_4x4(), P[ded].matrix.to_3x3().to_4x4(); Tp = P[inf].tail + V((0, 0, dz)); e = ik_braco(k, Tp)
    om.translation = P[inf].tail; P[met].matrix = om; bpy.context.view_layer.update(); od.translation = P[met].tail; P[ded].matrix = od; bpy.context.view_layer.update()
    return e
OSSOS4 = [nm for c in CADEIA.values() for nm in c]
for ac in ACS:
    acn = bpy.data.actions[ac]; ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
    f0, f1 = (int(x) for x in acn.frame_range); n = f1 - f0; laco = ac in ("Andar", "Trote", "Corrida")
    W = {k: pesos(ac, k, n, laco) for k in CADEIA}; BASE = []; ORIG = []
    for q in range(n + 1):
        ARM.animation_data.action = acn; sc.frame_set(f0 + q); bpy.context.view_layer.update()
        BASE.append({nm: P[nm].matrix.copy() for nm in OSSOS4}); ORIG.append({nm: P[nm].rotation_quaternion.copy() for nm in OSSOS4})
    ARM.animation_data.action = None
    est = {k: {} for k in CADEIA}; DZ = {k: [0.0] * (n + 1) for k in CADEIA}; Z0 = {k: [None] * (n + 1) for k in CADEIA}
    def pose_base(q):
        ARM.animation_data.action = acn; sc.frame_set(f0 + q); bpy.context.view_layer.update(); ARM.animation_data.action = None
    # passo 1: deficit de folga com a correcao inteira e punho parado
    for q in range(n + 1):
        if not any(W[k][0][q] > 0 for k in CADEIA): continue
        pose_base(q)
        for k in CADEIA:
            w = W[k][0][q]
            if w <= 0: continue
            montar_pata(k, BASE[q], 0.0, 0.0); z0 = folga(k); montar_pata(k, BASE[q], w, 0.0); z1 = folga(k); alvo = min(z0, PAR["folga_alvo"])
            Z0[k][q] = z0; DZ[k][q] = max(0.0, alvo - z1)
            montar_pata(k, BASE[q], 0.0, 0.0)
    # suaviza a subida do punho no tempo (max de 3 quadros e media de 3), so dentro do balanco
    for k in CADEIA:
        d = DZ[k]; m = [max(d[max(0, q - 1):q + 2]) for q in range(n + 1)]
        DZ[k] = [(sum(m[max(0, q - 1):q + 2]) / len(m[max(0, q - 1):q + 2])) * (1.0 if W[k][0][q] > 0 else 0.0) for q in range(n + 1)]
        if laco: DZ[k][n] = DZ[k][0]
    # pontas das transicoes: peso e subida do punho iguais aos da marcha vizinha ja corrigida (mesma pose no q0 / no fim) e misturados
    # com os da propria acao em 'ponta_q' quadros: a emenda fica exata; nunca no apoio da propria acao
    if not laco and ac in CONTEXTO:
        Kp = PAR["ponta_q"]; ori, dst = CONTEXTO[ac]
        for k in CADEIA:
            w_, ap_ = W[k]
            for i in range(0, Kp + 1):
                s_ = suave(i / Kp)
                for gnome, q_t, q_g in ((ori, i, None), (dst, n - i, None)):
                    if gnome not in GFIN or q_t < 0 or q_t > n: continue
                    NQg = len(GFIN[gnome][0][k]) - 1; qg = (i % NQg) if q_t == i else ((NQg - i) % NQg)
                    wg, dg = GFIN[gnome][0][k][qg], GFIN[gnome][1][k][qg]
                    if ap_[q_t]: w_[q_t] = 0.0; DZ[k][q_t] = 0.0; continue
                    w_[q_t] = wg + (w_[q_t] - wg) * s_; DZ[k][q_t] = dg + (DZ[k][q_t] - dg) * s_
    # passo 2: aplica, confere folga e completa se faltar
    NOVOS = []
    for q in range(n + 1):
        pose_base(q); r = {}
        for k in CADEIA:
            w = W[k][0][q]; e = est[k]
            th0 = ang(BASE[q][CADEIA[k][1]].col[1].xyz, BASE[q][CADEIA[k][2]].col[1].xyz); e["carpo_antes"] = max(e.get("carpo_antes", 0), th0)
            if w > 0:
                if Z0[k][q] is None: montar_pata(k, BASE[q], 0.0, 0.0); Z0[k][q] = folga(k)
                dz = DZ[k][q]; err = montar_pata(k, BASE[q], w, dz); z = folga(k); alvo = min(Z0[k][q], PAR["folga_alvo"]) - 0.002
                it = 0
                while z < alvo and it < 4:
                    dz += alvo + 0.002 - z; err = montar_pata(k, BASE[q], w, dz); z = folga(k); it += 1
                DZ[k][q] = dz; e["folga_antes"] = min(e.get("folga_antes", 9), Z0[k][q]); e["folga_depois"] = min(e.get("folga_depois", 9), z)
                e["subida_punho_max"] = max(e.get("subida_punho_max", 0), dz); e["erro_ik_max"] = max(e.get("erro_ik_max", 0), err)
            e["carpo_depois"] = max(e.get("carpo_depois", 0), ang(P[CADEIA[k][1]].matrix.col[1].xyz, P[CADEIA[k][2]].matrix.col[1].xyz))
            e["dedos_depois"] = max(e.get("dedos_depois", 0), ang(P[CADEIA[k][2]].matrix.col[1].xyz, P[CADEIA[k][3]].matrix.col[1].xyz))
            for nm in CADEIA[k]:
                qn = P[nm].rotation_quaternion.copy()
                if qn.dot(ORIG[q][nm]) < 0: qn = -qn
                r[nm] = qn
        NOVOS.append(r)
    cb = acn.layers[0].strips[0].channelbag(acn.slots[0])
    for nm in OSSOS4:
        for i in range(4):
            fc = cb.fcurves.find('pose.bones["%s"].rotation_quaternion' % nm, index=i)
            kp = {int(round(p.co.x)): p for p in fc.keyframe_points}
            for q in range(n + 1):
                p = kp[f0 + q]; p.co.y = NOVOS[q][nm][i]; p.handle_left_type = "AUTO_CLAMPED"; p.handle_right_type = "AUTO_CLAMPED"
            fc.update()
    for pb in P: pb.matrix_basis.identity()
    if laco: GFIN[ac] = ({k: list(W[k][0]) for k in CADEIA}, {k: list(DZ[k]) for k in CADEIA})
    REL["acoes"][ac] = {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in est.items()}; REL["acoes"][ac]["subida_punho_por_quadro"] = {k: [round(x, 4) for x in DZ[k]] for k in CADEIA}
    print("V30", ac, json.dumps({k: REL["acoes"][ac][k] for k in CADEIA}), flush=True)
ARM.animation_data.action = bpy.data.actions["Andar"]
json.dump(REL, open(os.path.join(OUT, "patas_dianteiras_v30.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("PATAS_DIANTEIRAS_V30_OK", flush=True)
