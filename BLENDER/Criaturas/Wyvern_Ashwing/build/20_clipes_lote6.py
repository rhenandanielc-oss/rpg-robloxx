# Lote 6 de clipes da Wyvern: realismo 2 (pedido do usuario em 12/11/2026), sobre Wyvern_E7_clipes_L5.blend (preservado).
# So ACRESCENTA actions. Clipes visuais: angulos e tempos sao PROPOSTA (nada de regra de jogo).
#   AsasEscudo         6 s  encolhe, recolhe a cabeca e cruza as asas dobradas a frente do peito (capa); treme; volta
#   SecarAsas          6 s  abre as asas ao sol (como corvo-marinho), duas batidas lentas, sacode a membrana, fecha
#   AgarrarPresa       6 s  pisa 2,5 studs a frente com a pata direita (prende a presa) e entra na postura do Comer
#                           (aprovado): morde/puxa a presa a ~11 studs a frente; solta e volta. Presa nao modelada.
#   AndarQuatroApoios  1,6 s loop  anda apoiando o pulso/polegar das asas no chao (como morcego/pterossauro): pernas do
#                           walk_loop em camera lenta (6,7 st/s), corpo inclinado 24 graus na pelve, asas por IK com a
#                           parte mais baixa da asa no chao durante o apoio (curva de altura calibrada por lado).
# Os de 6 s comecam e terminam no quadro 0 do idle. O andar e um loop na esteira (pes e pulsos apoiados recuam juntos).
# Uso: blender -b Wyvern_E7_clipes_L5.blend -P 20_clipes_lote6.py -- <08_base.py> <saida.blend> <manifesto.json> [clipes|lab:<pasta>]
import bpy, sys, math, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
I0, FI0 = amostra("idle_loop", 0.0)
T_IDLE = DUR["idle_loop"]; T_FLY = DUR["fly_loop"]; T_WALK = DUR["walk_loop"]
def I(t): return amostra("idle_loop", t % T_IDLE)
ASAS = ASA["L"] + ASA["R"]
LOG = {}
def sx_(s): return 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
def env(t, a, b, c, d):
    return suave((t - a) / max(b - a, 1e-6)) * (1 - suave((t - c) / max(d - c, 1e-6)))
def lerp_k(t, marcas):
    if t <= marcas[0][0]: return marcas[0][1]
    for (ta, va), (tb, vb) in zip(marcas, marcas[1:]):
        if t <= tb: return va + (vb - va) * suave((t - ta) / (tb - ta))
    return marcas[-1][1]
JAW_FECHADA = Q(V((1, 0, 0)), R(18))                                # boca do modelo fica entreaberta no repouso (L5)
def fechar_boca(P, w):
    if w > 0: P.update(misturar(P, {**P, "jaw": (P["jaw"][0], JAW_FECHADA, P["jaw"][2])}, w, ["jaw"]))
# ---------------------------------------------------------------- pernas (como no L5)
LEG0 = {s: ponta(fk(I0, PERNA[s]), "calf_" + s) for s in "LR"}
FK0 = fk(I0)
def plantar(P, s, alvo, R_pe, toe=None, guarda=False):
    """jarrete (ponta da canela) no alvo; pe com a orientacao R_pe (espaco do armature); dedo do idle ou o dado"""
    ini = {b: P[b] for b in ("thigh_" + s, "calf_" + s)}
    e0 = (ponta(fk(P, ["calf_" + s]), "calf_" + s) - alvo).length
    ik_perna(P, s, [(lambda M, s=s: ponta(M, "calf_" + s), alvo, 1.0)],
             eixos=[("thigh_" + s, X), ("thigh_" + s, FRENTE), ("calf_" + s, X)], it=60)
    err = (ponta(fk(P, ["calf_" + s]), "calf_" + s) - alvo).length
    giro = max(math.degrees(ini[b][1].rotation_difference(P[b][1]).angle) for b in ini)
    if guarda and (err > e0 or giro > 40):                           # IK divergiu/torceu: fica a pose de partida
        P.update(ini); err = e0; LOG["ik_perna_revertido"] = LOG.get("ik_perna_revertido", 0) + 1
    Mc = fk(P, ["calf_" + s])["calf_" + s]
    q_ = ((Mc @ REL["foot_" + s]).to_3x3().inverted() @ R_pe).to_quaternion()
    l, _, e = P["foot_" + s]; P["foot_" + s] = (l, q_, e)
    P["toe_" + s] = tuple(x.copy() for x in (toe or I0["toe_" + s]))
    return err
def agachar(P, q, lados="LR"):
    if q <= 1e-4: return
    mover(P, "root", V((0, 0, -q)))
    for s in lados: LOG["erro_perna"] = round(max(LOG.get("erro_perna", 0.0), plantar(P, s, LEG0[s], FK0["foot_" + s].to_3x3())), 3)
def inclinar(P, graus):
    p0 = cabeca(fk(P, ["pelvis"]), "pelvis"); girar(P, "root", X, R(graus)); mover(P, "root", p0 - cabeca(fk(P, ["pelvis"]), "pelvis"))
def pose_asa_aberta():
    best = None
    for k in range(96):
        tt = T_FLY * k / 96; Pf, _ = amostra("fly_loop", tt); M = fk(Pf)
        pl, pr = ponta(M, "strut_b_02_L"), ponta(M, "strut_b_02_R")
        om = (cabeca(M, "upperarm_L") + cabeca(M, "upperarm_R")) / 2
        sc_ = (pl - pr).length - (abs(pl.z - om.z) + abs(pr.z - om.z))
        if best is None or sc_ > best[0]: best = (sc_, tt)
    return amostra("fly_loop", best[1])[0]
ASA_ABERTA = pose_asa_aberta()
# ---------------------------------------------------------------- IK por modos (L5) com ossos extras na FK
FOC = "breath_socket"
def ik_geral(P0, params, alvos, reg, x0=None, it=25, extra=()):
    n = len(params); x = np.array(x0 if x0 is not None else np.zeros(n), dtype=float)
    ossos_fk = sorted({FOC, "head", "jaw"} | set(extra) | {b for modo in params for b, ax, k in modo})
    def pose(xv):
        Pp = dict(P0)
        for modo, a in zip(params, xv):
            for b, ax, k in modo: girar(Pp, b, ax, float(a) * k)
        return Pp
    def resid(xv):
        M = fk(pose(xv), ossos_fk); r = []
        for f, alvo, w in alvos:
            d = f(M) - alvo; r += [d.x * w, d.y * w, d.z * w]
        return np.concatenate([np.array(r), np.asarray(reg) * xv])
    for _ in range(it):
        r0 = resid(x)
        J = np.zeros((len(r0), n)); h = 1e-4
        for j in range(n):
            xx = x.copy(); xx[j] += h; J[:, j] = (resid(xx) - r0) / h
        dx = np.linalg.solve(J.T @ J + 1e-3 * np.eye(n), -J.T @ r0)
        dx = np.clip(dx, -0.15, 0.15); x = x + dx
        if np.abs(dx).max() < 1e-5: break
    P = pose(x); M = fk(P, ossos_fk)
    err = max((f(M) - alvo).length for f, alvo, w in alvos)
    return P, x, err
KP = (0.16, 0.2, 0.22, 0.22, 0.2)
PESC_XZ = [[("spine_03", X, 1.0)], [(b, X, k) for b, k in zip(PESCOCO, KP)],
           [(b, X, k) for b, k in zip(PESCOCO, (0.35, 0.3, 0.15, -0.1, -0.3))],
           [(b, Z, k) for b, k in zip(PESCOCO, KP)] + [("spine_03", Z, 0.15)],
           [("head", X, 1.0)], [("head", Z, 1.0)]]
REG_XZ = [0.8, 0.05, 0.25, 0.05, 0.3, 0.4]
ESTADO = {}
def ik_chave(chave, P, params, alvos, reg, extra=()):
    P2, x, err = ik_geral(P, params, alvos, reg, ESTADO.get(chave), extra=extra)
    xa = ESTADO.get(chave)
    if xa is not None:
        d = math.degrees(float(np.abs(x - xa).max())); k = "salto_ik_" + chave
        if d > LOG.get(k, [0])[0]: LOG[k] = [round(d, 2), int(np.abs(x - xa).argmax())]
    ESTADO[chave] = x
    LOG["erro_ik_" + chave] = round(max(LOG.get("erro_ik_" + chave, 0.0), err), 3)
    return P2
def ik_focinho(chave, P, alvos): return ik_chave(chave, P, PESC_XZ, alvos, REG_XZ)
def foco(M): return cabeca(M, FOC)
def cab(M): return cabeca(M, "head")
# ---------------------------------------------------------------- AsasEscudo
T_ESC = 2 * T_IDLE
PAR = dict(esc_z=-65, esc_y=-35, esc_up=40, esc_fa=0, esc_mix=0.0, esc_dentro=0, esc_cab=(0, 2.2, -3.4))
def c_escudo(t):
    P, fold = I(t)
    ea = env(t, 0.25, 1.15, 4.5, 5.6)                                   # asas
    ec = env(t, 0.15, 0.95, 4.7, 5.8)                                   # corpo/cabeca
    agachar(P, 0.7 * ec)
    P = misturar(P, ASA_ABERTA, PAR["esc_mix"] * ea, ASAS)
    tr = math.sin(2 * math.pi * 2.6 * t) * env(t, 1.3, 1.6, 4.2, 4.5)   # tensao: asas tremem pouco
    for s in "LR":
        k = sx_(s)
        girar(P, "shoulder_" + s, Z, R(PAR["esc_z"]) * k * ea)           # asas a frente do peito
        girar(P, "shoulder_" + s, Y, (R(PAR["esc_y"]) + R(1.2) * tr) * k * ea)   # erguidas (cobrem a cabeca)
        girar(P, "upperarm_" + s, FRENTE, R(PAR["esc_up"]) * k * ea)
        girar(P, "forearm_" + s, X, R(PAR["esc_fa"]) * ea)
        girar(P, "upperarm_" + s, Z, R(PAR["esc_dentro"]) * k * ea)    # cotovelos para dentro (asas se cruzam a frente)
    f0 = foco(fk(P, [FOC]))
    if ec > 1e-3:
        alvo = f0 + V(PAR["esc_cab"]) * ec                              # cabeca recolhida para tras e para baixo
        Pik = ik_focinho("esc", P, [(foco, alvo, 1.0)])
        P = misturar(P, Pik, 1.0, ["spine_03"] + PESCOCO + ["head"])
    else:
        ESTADO.pop("esc", None)
    for b in CAUDA[:6]: girar(P, b, Z, R(2.0) * ESQ * ec)               # cauda encosta de lado no corpo
    fechar_boca(P, ec)
    return P, fold
# ---------------------------------------------------------------- SecarAsas
T_SEC = 2 * T_IDLE
def c_secar(t):
    P, fold = I(t)
    ea = env(t, 0.3, 1.4, 4.6, 5.7)
    P = misturar(P, ASA_ABERTA, 0.85 * ea, ASAS)
    bat = env(t, 1.9, 2.2, 3.6, 3.9) * math.sin(2 * math.pi * 1.2 * (t - 1.9))   # duas batidas lentas
    tre = env(t, 4.0, 4.15, 4.45, 4.6) * math.sin(2 * math.pi * 9 * t)          # sacudida rapida da membrana
    for s in "LR":
        k = sx_(s)
        girar(P, "shoulder_" + s, Y, (R(-14) + R(16) * bat) * k * ea)    # meio erguidas, batendo devagar
        girar(P, "shoulder_" + s, Z, R(8) * k * ea)                      # um pouco para tras (peito ao sol)
        girar(P, "forearm_" + s, X, R(5) * tre)
        girar(P, "upperarm_" + s, FRENTE, R(4) * tre * k)
    eh = env(t, 0.6, 1.6, 4.4, 5.5)
    for b in PESCOCO[1:4]: girar(P, b, X, R(-3) * eh)                  # pescoco ergue
    girar(P, "head", X, R(-10) * eh)                                     # focinho ao alto
    fechar_boca(P, eh)
    return P, fold
# ---------------------------------------------------------------- AgarrarPresa
# Pata direita pisa a frente e prende a presa; o corpo entra na postura do Comer (aprovado no L2c: cabeca no chao a
# ~11 studs a frente) e morde/puxa a presa logo a frente da pata; solta e volta ao idle.
FONTE["Comer"] = curvas(bpy.data.actions["Comer"]); DUR["Comer"] = bpy.data.actions["Comer"].frame_range[1] / FPS_CENA
T_AGA = 2 * T_IDLE
PATA = "R" if ESQ > 0 else "L"                                       # pata direita da Wyvern
APAR = dict(desl_y=-2.5, desl_x=-0.3, arco=1.6, aperta=0.0)
def c_agarrar(t):
    P, fold = I(t)
    s = PATA; o = "L" if s == "R" else "R"
    wc = env(t, 1.1, 2.0, 4.2, 5.2)                                     # entra/sai da postura do Comer
    if wc > 1e-4:
        Pc, fc = amostra("Comer", (t - 1.1) % DUR["Comer"])
        P = misturar(P, Pc, wc); fold = fold * (1 - wc) + fc * wc
    plantar(P, o, LEG0[o], FK0["foot_" + o].to_3x3(), guarda=True)      # pata de apoio presa ao ponto do idle
    ida = suave((t - 0.45) / 0.75); volta = suave((t - 4.7) / 0.9)
    u = ida * (1 - volta)
    arco = math.sin(math.pi * min(1, max(0, (t - 0.45) / 0.75))) * (1 - volta) + math.sin(math.pi * min(1, max(0, (t - 4.7) / 0.9))) * volta
    desl = V((APAR["desl_x"] * ESQ, APAR["desl_y"], 0.0))
    alvo = LEG0[s] + desl * u + V((0, 0, APAR["arco"] * arco - APAR["aperta"] * env(t, 1.15, 1.35, 4.5, 4.75)))
    toe = (I0["toe_" + s][0], rot_mundo("toe_" + s, X, R(25) * arco) @ I0["toe_" + s][1], I0["toe_" + s][2])
    pernas = ("thigh_" + s, "calf_" + s)
    if "aga_perna" in ESTADO:                                          # parte da solucao do quadro anterior (sem torcer)
        for b, q_ in zip(pernas, ESTADO["aga_perna"]): P[b] = (P[b][0], q_.copy(), P[b][2])
    e = plantar(P, s, alvo, FK0["foot_" + s].to_3x3(), toe)
    ESTADO["aga_perna"] = [P[b][1].copy() for b in pernas]
    if t > 5.5:                                                        # termina exatamente no idle (sem rolagem residual da coxa)
        Pi_, _ = I(t); P = misturar(P, Pi_, suave((t - 5.5) / 0.5), PERNA[s])
    LOG["erro_perna_aga"] = round(max(LOG.get("erro_perna_aga", 0.0), e), 3)
    for s_ in "LR": girar(P, "shoulder_" + s_, Y, R(-6) * sx_(s_) * env(t, 0.3, 0.9, 5.0, 5.7))   # asas um pouco erguidas
    return P, fold
# ---------------------------------------------------------------- AndarQuatroApoios
T_QUA = 1.6
import os; DEPURAR = os.environ.get("L6_DEBUG") == "1"
Z_CHAO = -0.022
ESC_T = T_WALK / T_QUA                                              # pernas do walk_loop em camera lenta
FAT_ESTANCIA = 0.625                                                # fracao de apoio (igual a das pernas)
QPAR = dict(incl=24, desce=0.0, xw=5.6, frente=-4.6, z_k=0.0, arco=0.8, hand=0.0, fase=0.25)
def joelho_asa(s): return "thumb_" + s                              # junta do pulso/polegar = ponto de apoio
def alvo_asa(s, t):
    vel = 6.7 / (FAT_ESTANCIA * T_QUA)                             # mesma velocidade dos pes
    passo = vel * FAT_ESTANCIA * T_QUA
    fi = (t / T_QUA - QPAR["fase"] - (0.5 if s != ("L" if ESQ > 0 else "R") else 0.0)) % 1.0
    y0 = QPAR["ombro_y"] + QPAR["frente"]
    if fi < FAT_ESTANCIA:
        u = fi / FAT_ESTANCIA; y = y0 + passo * u; z = QPAR["z_k"] + corr_apoio(s, u)
    else:
        u = (fi - FAT_ESTANCIA) / (1 - FAT_ESTANCIA); y = y0 + passo * (1 - suave(u))
        z = QPAR["z_k"] + corr_apoio(s, 1.0) * (1 - suave(u)) + corr_apoio(s, 0.0) * suave(u) + QPAR["arco"] * math.sin(math.pi * u)
    return V((QPAR["xw"] * sx_(s), y, z))
CORR = {"L": [0.0] * 13, "R": [0.0] * 13}                          # altura extra da junta ao longo do apoio (calibrada)
def corr_apoio(s, u):
    tab = CORR[s]; x = min(max(u, 0.0), 1.0) * (len(tab) - 1); i = min(int(x), len(tab) - 2); f = x - i
    return tab[i] * (1 - f) + tab[i + 1] * f
def t_de(s, fi):
    return T_QUA * ((fi + QPAR["fase"] + (0.5 if s != ("L" if ESQ > 0 else "R") else 0.0)) % 1.0)
ASA_IK = {s: [[("shoulder_" + s, Y, 1.0)], [("shoulder_" + s, Z, 1.0)], [("upperarm_" + s, X, 1.0)],
              [("upperarm_" + s, Z, 1.0)], [("upperarm_" + s, FRENTE, 1.0)], [("forearm_" + s, X, 1.0)]] for s in "LR"}
REG_ASA = [0.35, 0.35, 0.12, 0.12, 0.12, 0.15]
def quad_corpo(t):
    tw = (t * ESC_T) % T_WALK
    Pw, fold = amostra("walk_loop", tw); Mw = fk(Pw)
    P = copia(Pw)
    for b in ASAS: P[b] = tuple(x.copy() for x in I0[b])              # asas dobradas como no idle (sem o tremor do walk)
    inclinar(P, QPAR["incl"]); mover(P, "root", V((0, 0, -QPAR["desce"])))
    for s in "LR":                                                   # coxa com a MESMA orientacao de mundo do walk (sem torcer no IK)
        b = "thigh_" + s; Mp = fk(P, [PAI[b]])[PAI[b]]
        l_, q_, e_ = ((Mp @ REL[b]).inverted() @ Mw[b]).decompose()
        P[b] = (P[b][0], q_, P[b][2])
    for s in "LR":
        LOG["erro_perna_qua"] = round(max(LOG.get("erro_perna_qua", 0.0), plantar(P, s, ponta(Mw, "calf_" + s), Mw["foot_" + s].to_3x3(), Pw["toe_" + s], guarda=True)), 3)
    for b in PESCOCO[:3]: girar(P, b, X, R(-4))                        # pescoco compensa a inclinacao (olha a frente)
    girar(P, "head", X, R(-8))
    for s in "LR": girar(P, "hand_" + s, X, R(QPAR["hand"]))
    return P, fold
def em_apoio(s, t):
    fi = (t / T_QUA - QPAR["fase"] - (0.5 if s != ("L" if ESQ > 0 else "R") else 0.0)) % 1.0
    return fi < FAT_ESTANCIA
def c_quatro(t, corrigir=True):
    P0, fold = quad_corpo(t)
    def resolver(alvos_):
        P = P0
        for s in "LR":
            Pik = ik_chave("qua" + s, P0, ASA_IK[s], [(lambda M, s=s: cabeca(M, joelho_asa(s)), alvos_[s], 1.0)], REG_ASA,
                           extra=[joelho_asa(s)])
            P = misturar(P, Pik, 1.0, ASA[s])
        return P
    alvos = {s: alvo_asa(s, t) for s in "LR"}
    P = resolver(alvos)
    if corrigir:                                                     # o ponto mais baixo da asa de apoio fica no chao
        z = zmin_reg(P, fold); mudou = False
        for s in "LR":
            dz = Z_CHAO - z["asa" + s]
            if em_apoio(s, t) or dz > 0:                              # no balanco so corrige se atravessar o chao
                alvos[s] = alvos[s] + V((0, 0, max(-1.0, min(1.0, dz)))); mudou = True
        if mudou:
            LOG["corr_apoio_max"] = round(max(LOG.get("corr_apoio_max", 0.0), max(abs(Z_CHAO - z["asa" + s]) for s in "LR")), 3)
            P = resolver(alvos)
    if DEPURAR:
        z2 = zmin_reg(P, fold); M = fk(P)
        print("DBG t=%.3f" % t, {s: (em_apoio(s, t), [round(v, 2) for v in alvos[s]], [round(v, 2) for v in cabeca(M, joelho_asa(s))], round(z2["asa" + s], 2)) for s in "LR"}, flush=True)
    return P, fold
def calibrar_quatro():
    P, _ = quad_corpo(0.0); M = fk(P)
    QPAR["ombro_y"] = cabeca(M, "upperarm_L").y; QPAR["z_k"] = 1.5
    for s in "LR": CORR[s] = [0.0] * 13
    # curva de altura: em cada ponto do apoio, o ponto mais baixo da asa toca o chao (z = Z_CHAO); 3 passadas
    for _ in range(3):
        for s in "LR":
            ESTADO.clear(); nova = []
            for k in range(13):
                u = k / 12; Pm, fm = c_quatro(t_de(s, u * FAT_ESTANCIA), corrigir=False)
                nova.append(CORR[s][k] + Z_CHAO - zmin_reg(Pm, fm)["asa" + s])
            # suaviza (media movel de 3) para a junta nao tremer
            CORR[s] = [sum(nova[max(0, k - 1):k + 2]) / len(nova[max(0, k - 1):k + 2]) for k in range(13)]
    ESTADO.clear()
    for k in list(LOG):
        if k.startswith(("erro_ik_qua", "salto_ik_qua", "corr_apoio")): LOG.pop(k)
    LOG["quatro_calib"] = {k: round(v, 3) for k, v in QPAR.items()}
    LOG["quatro_corr"] = {s: [round(v, 2) for v in CORR[s]] for s in "LR"}
CLIPES = {"AsasEscudo": (c_escudo, T_ESC, False), "SecarAsas": (c_secar, T_SEC, False),
          "AgarrarPresa": (c_agarrar, T_AGA, False), "AndarQuatroApoios": (c_quatro, T_QUA, True)}
# ---------------------------------------------------------------- modo laboratorio: renderiza quadros soltos
if len(argv) > 3 and argv[3].startswith("lab:"):
    import os
    pasta = argv[3][4:]; os.makedirs(pasta, exist_ok=True)
    pedidos = json.loads(argv[4])                                    # [[clipe, t, {par}], ...]
    scn = bpy.context.scene; scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 640; scn.render.resolution_y = 430
    scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
    bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
    mc = bpy.data.materials.new("chao"); mc.diffuse_color = (0.42, 0.45, 0.38, 1); bpy.context.object.data.materials.append(mc)
    cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); scn.collection.objects.link(cam); scn.camera = cam
    cd.type = "ORTHO"; cd.clip_end = 1000; cd.ortho_scale = 34
    for ob in (arm, key):
        if ob.animation_data: ob.animation_data.action = None
    for i, (nome, t, par) in enumerate(pedidos):
        PAR.update(par); QPAR.update(par); APAR.update(par); ESTADO.clear(); LOG.clear()
        if nome == "AndarQuatroApoios": calibrar_quatro()
        fn = CLIPES[nome][0]
        P, fold = fn(t) if nome != "AndarQuatroApoios" else fn(t)
        aplicar(P, fold)
        print("LAB", i, nome, t, par, "zmin", zmin_reg(P, fold), "log", json.dumps(LOG))
        for v, d in (("lado", V((1, 0, 0.05))), ("tres4", V((0.8, -0.7, 0.45))), ("frente", V((0, -1, 0.15)))):
            d = d.normalized(); c = V((0, -3, 6))
            cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
            scn.render.filepath = os.path.join(pasta, "%02d_%s.png" % (i, v)); bpy.ops.render.render(write_still=True)
    sys.exit(0)
SO = argv[3].split(",") if len(argv) > 3 else list(CLIPES)
mani = {"_fonte": "Wyvern_E7_clipes_L5.blend (idle_loop, walk_loop, fly_loop)", "_hz": HZ}
for nome in SO:
    fn, dur, loop = CLIPES[nome]; ESTADO.clear()
    if nome == "AndarQuatroApoios": calibrar_quatro(); fn = lambda t: c_quatro(t, corrigir=False)
    mani[nome] = gravar_clipe(nome, fn, dur, loop); print("CLIPE", nome, mani[nome], flush=True)
mani["_calibracao"] = LOG; print("CALIB", json.dumps(LOG), flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
