# Lote 3 de clipes da Wyvern (transicoes de locomocao, voo e ninho), sobre a base aprovada Wyvern_E7_clipes_L2c.blend.
# Fontes: clipes do Ashwing (idle_loop, fly_loop) e a Corrida do lote 1. Clipes visuais: angulos/tempos sao PROPOSTA.
#   Arrancada     idle -> Corrida: impulso (agacha e inclina), termina EXATAMENTE no quadro 0 da Corrida
#   Frenagem      Corrida -> idle: freia jogando o peso para tras, asas abrem um pouco; termina no quadro 0 do idle
#   VooBatido     fly_loop mais rapido (x1,18) e mais amplo nas asas, corpo levemente a frente, loop
#   PairarCurto   batidas do fly_loop com o corpo empinado ~30 graus, pernas a frente, cauda baixa, loop
#   Empoleirado   em pe agachado, equilibrio: corpo balanca de lado, asas meio abertas compensam, cauda contrapeso, loop
#   GuardaNinho   agachado sobre o ninho, asas abertas e baixas cobrindo, cabeca baixa varrendo, sibilo, ferrao meio
#                 armado, loop
# Pes no chao: agachamentos com o jarrete no ponto do idle e o pe na orientacao do idle (como o Comer aprovado).
# Uso: blender -b Wyvern_E7_clipes_L2c.blend -P 14_clipes_lote3.py -- <08_base.py> <saida.blend> <manifesto.json> [clipes]
import bpy, sys, math, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
for n in ("Corrida",):                                              # fonte extra: a Corrida aprovada do lote 1
    FONTE[n] = curvas(bpy.data.actions[n]); DUR[n] = bpy.data.actions[n].frame_range[1] / FPS_CENA
I0, FI0 = amostra("idle_loop", 0.0)
T_IDLE = DUR["idle_loop"]; T_COR = DUR["Corrida"]; T_FLY = DUR["fly_loop"]
def I(t): return amostra("idle_loop", t)
def C(t): return amostra("Corrida", t)
LOG = {}
def media(clipe, n=32):
    acc = {b: [V(), Q((0, 0, 0, 0)), V()] for b in OSSOS}
    for k in range(n):
        P, _ = amostra(clipe, DUR[clipe] * k / n)
        for b in OSSOS:
            l, q, e = P[b]; a = acc[b]; a[0] += l / n; a[2] += e / n
            if a[1].dot(q) < 0: q = -q
            a[1] = Q([a[1][i] + q[i] / n for i in range(4)])
    return {b: (a[0], a[1].normalized(), a[2]) for b, a in acc.items()}
def ampliar(P, M, k, ossos):
    for b in ossos:
        l, q, e = P[b]; lm, qm, em = M[b]
        if qm.dot(q) < 0: q = -q
        d = qm.inverted() @ q; ang = d.angle; ax = d.axis
        P[b] = (lm + (l - lm) * k, qm @ Q(ax, ang * k) if ang > 1e-6 else q, e)
# ---------------------------------------------------------------- agachar com pe identico ao idle (do Comer aprovado)
def _juntas(M, s): return (ponta(M, "calf_" + s), ponta(M, "foot_" + s), ponta(M, "toe_" + s))
LEG0 = {s: _juntas(fk(I0, PERNA[s]), s) for s in "LR"}
FK0 = fk(I0)
def agachar(P, q):
    mover(P, "root", V((0, 0, -q)))
    for s in "LR":
        ik_perna(P, s, [(lambda M, s=s: ponta(M, "calf_" + s), LEG0[s][0], 1.0)],
                 eixos=[("thigh_" + s, X), ("thigh_" + s, FRENTE), ("calf_" + s, X)], it=60)
        Mc = fk(P, ["calf_" + s])["calf_" + s]
        q_ = ((Mc @ REL["foot_" + s]).to_3x3().inverted() @ FK0["foot_" + s].to_3x3()).to_quaternion()
        l, _, e = P["foot_" + s]; P["foot_" + s] = (l, q_, e)
        P["toe_" + s] = tuple(x.copy() for x in I0["toe_" + s])
def sx_(s): return 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
Z_CHAO = -0.022                                                    # z minimo do idle (o pe parado ja fica assim)
def nao_afundar(P, fold):
    """se a malha de uma perna passa abaixo de Z_CHAO (mistura apoio x balanco), ergue ponta e bola do pe so o deficit"""
    for _ in range(3):
        z = zmin_reg(P, fold); ok = True
        for s in "LR":
            d = Z_CHAO - z["perna" + s]
            if d > 0.003:
                ok = False; M = fk(P, PERNA[s]); up = V((0, 0, d + 0.005))
                alvos = [(lambda M, s=s: ponta(M, "toe_" + s), ponta(M, "toe_" + s) + up, 1.0),
                         (lambda M, s=s: ponta(M, "foot_" + s), ponta(M, "foot_" + s) + up, 1.0)]
                ik_perna(P, s, alvos, it=30)
        if ok: break
    return P
# ---------------------------------------------------------------- Arrancada / Frenagem
T_ARR = T_COR
def c_arrancada(t):
    u = t / T_ARR; w = suave(min(u / 0.85, 1.0)); imp = math.sin(math.pi * u)
    Pi, fi = I(t); Pc, fc = C(t)
    P = misturar(Pi, Pc, w); fold = fi * (1 - w) + fc * w
    girar(P, "spine_01", X, R(6) * imp)                                # mergulha o peito no impulso
    for b in PESCOCO[:3]: girar(P, b, X, R(2) * imp)
    girar(P, "head", X, R(-5) * imp)
    for b in CAUDA[:4]: girar(P, b, X, R(1.5) * imp)                   # cauda sobe como contrapeso
    if 0 < w < 1: nao_afundar(P, fold)                                  # inicio/fim intactos (emendas exatas)
    return P, fold
T_FRE = 0.9
def c_frenagem(t):
    u = t / T_FRE; w = suave(min(u / 0.8, 1.0)); fr = math.sin(math.pi * min(u / 0.75, 1.0))
    Pc, fc = C(t % T_COR); Pi, fi = I((t - T_FRE) % T_IDLE)           # termina no quadro 0 do idle
    P = misturar(Pc, Pi, w); fold = fc * (1 - w) + fi * w
    girar(P, "spine_01", X, R(-8) * fr)                                # peso para tras
    for b in PESCOCO[:3]: girar(P, b, X, R(-2.5) * fr)
    girar(P, "head", X, R(7) * fr)
    for b in CAUDA[:4]: girar(P, b, X, R(2.5) * fr)
    for s in "LR": girar(P, "shoulder_" + s, Y, R(-9) * sx_(s) * fr)   # asas abrem um pouco (equilibrio)
    if 0 < w < 1: nao_afundar(P, fold)
    return P, fold
# ---------------------------------------------------------------- voo
MED_FLY = media("fly_loop")
ASAS = ASA["L"] + ASA["R"]
T_VB = T_FLY / 1.18
def c_voo_batido(t):
    P, fold = amostra("fly_loop", t * 1.18)
    ampliar(P, MED_FLY, 1.15, ASAS)
    girar(P, "root", X, R(5))                                         # corpo um pouco a frente (cruzeiro rapido)
    for b in PESCOCO: girar(P, b, X, R(-1))
    u = 2 * math.pi * t / T_VB
    for i, b in enumerate(CAUDA): girar(P, b, X, R(0.8) * math.sin(u - 0.3 * i))
    return P, 0.0
T_PAI = 1.0
def c_pairar(t):
    P, fold = amostra("fly_loop", t * T_FLY / T_PAI)
    ampliar(P, MED_FLY, 1.1, ASAS)
    u = 2 * math.pi * t / T_PAI
    pel0 = cabeca(fk(P, ["pelvis"]), "pelvis")
    girar(P, "root", X, R(-30))                                       # empinado (-X = nariz para cima)...
    mover(P, "root", pel0 - cabeca(fk(P, ["pelvis"]), "pelvis"))      # ...com pivo na pelve (o corpo nao desloca)
    for b in PESCOCO: girar(P, b, X, R(5))                            # pescoco devolve a cabeca para a frente
    girar(P, "head", X, R(5))
    for s in "LR":
        girar(P, "thigh_" + s, X, R(-22)); girar(P, "calf_" + s, X, R(10))   # pernas penduradas a frente
        girar(P, "toe_" + s, X, R(18))
    for b in CAUDA[:3]: girar(P, b, X, R(6))                          # cauda volta para quase horizontal (leme)
    for i, b in enumerate(CAUDA[3:]): girar(P, b, X, R(1.0) * math.sin(u - 0.4 * i))
    mover(P, "root", V((0, 0, 0.18 * math.sin(u + 0.6))))              # sobe a cada batida
    return P, 0.0
# ---------------------------------------------------------------- empoleirado / guarda do ninho
T_EMP = T_IDLE
def c_empoleirado(t):
    P, fold = I(t); u = 2 * math.pi * t / T_EMP
    agachar(P, 0.6)
    bal = math.sin(u) * 0.8 + 0.2 * math.sin(2 * u)                   # balanco lateral
    girar(P, "spine_01", Y, R(4) * bal); girar(P, "spine_01", X, R(4))
    for b in PESCOCO: girar(P, b, Y, R(-1.5) * bal)                   # cabeca compensa
    for s in "LR":
        lado = 1.0 if sx_(s) * ESQ > 0 else -1.0
        girar(P, "shoulder_" + s, Y, R(-14 - 6 * bal * lado) * sx_(s))     # asas meio abertas, sobe a do lado que cai
        girar(P, "forearm_" + s, X, R(-6))
    for b in CAUDA[:5]: girar(P, b, Z, R(-1.6) * bal)                 # cauda contrapeso
    for b in CAUDA[:2]: girar(P, b, X, R(2))
    return P, fold
T_GUA = 2 * T_IDLE                                                  # 2 ciclos do idle (base): o laco fecha sem salto
ASA_ABERTA = None
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
PARAM = {"gua_asa": 0.0}
def guarda_base(P, wasa=1.0):
    agachar(P, 1.2)
    girar(P, "spine_01", X, R(6))
    P2 = misturar(P, ASA_ABERTA, 0.85 * wasa, ASAS)
    for s in "LR":
        girar(P2, "shoulder_" + s, Y, PARAM["gua_asa"] * sx_(s) * wasa)      # asas baixas cobrindo o ninho
        girar(P2, "shoulder_" + s, Z, R(-14) * sx_(s) * wasa)               # e um pouco a frente
    for b, k in zip(PESCOCO, (0.4, 0.3, 0.2, 0.1, 0.0)): girar(P2, b, X, R(40) * k)
    girar(P2, "head", X, R(-18))
    for i, b in enumerate(CAUDA[2:]): girar(P2, b, Z, R(4.0) * ESQ)      # cauda curvada em volta do ninho
    PR = [5, 5, 4, 4, 5, 8, 14, 20, 26, 30]
    for i, b in enumerate(CAUDA): girar(P2, b, X, R(PR[i] * 0.4))     # ferrao meio armado
    return P2
def zasa_gua(a):
    PARAM["gua_asa"] = a; P = guarda_base(copia(I0)); z = zmin_reg(P, 0.0); return min(z["asaL"], z["asaR"])
PARAM["gua_asa"] = bissecao(zasa_gua, 0.0, R(50), 0.75, it=14)   # folga p/ balanco do idle
LOG["guarda_asa_graus"] = round(math.degrees(PARAM["gua_asa"]), 2)
def c_guarda(t):
    Pi, fi = I(t % T_IDLE); u = 2 * math.pi * t / T_GUA
    P = guarda_base(Pi)
    varre = math.sin(u)
    for b in PESCOCO[2:]: girar(P, b, Z, R(6) * varre)
    girar(P, "head", Z, R(8) * varre)
    sib = suave((t - 2.6) / 0.25) * (1 - suave((t - 3.3) / 0.35))   # sibilo (1 por ciclo)
    girar(P, "jaw", X, R(20) * sib); girar(P, "head", X, R(-4) * sib)
    for s in "LR": girar(P, "upperarm_" + s, FRENTE, R(2.0) * math.sin(u * 2) * (1 if s == "L" else -1) * ESQ)
    return P, 0.0
CLIPES = {"Arrancada": (c_arrancada, T_ARR, False), "Frenagem": (c_frenagem, T_FRE, False),
          "VooBatido": (c_voo_batido, T_VB, True), "PairarCurto": (c_pairar, T_PAI, True),
          "Empoleirado": (c_empoleirado, T_EMP, True), "GuardaNinho": (c_guarda, T_GUA, True)}
SO = argv[3].split(",") if len(argv) > 3 else list(CLIPES)
mani = {"_fonte": "Wyvern_E7_clipes_L2c.blend (idle_loop, fly_loop, Corrida)", "_hz": HZ, "_calibracao": LOG}
print("CALIB", json.dumps(LOG), flush=True)
for nome in SO:
    fn, dur, loop = CLIPES[nome]; mani[nome] = gravar_clipe(nome, fn, dur, loop); print("CLIPE", nome, mani[nome], flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
