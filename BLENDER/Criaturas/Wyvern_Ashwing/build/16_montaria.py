# Montaria da Wyvern (7 clipes da criatura; as animacoes do cavaleiro R15 sao separadas), sobre a base aprovada
# Wyvern_E7_clipes_L3b.blend (preservada). So acrescenta 7 actions. Clipes visuais: angulos/tempos sao PROPOSTA; regras de
# montaria, sela e encaixe do cavaleiro NAO sao definidas aqui.
#   RideIdle / RideWalk / RideRun / RideVirarEsquerda / RideVirarDireita
#       idle_loop / walk_loop / Corrida / VirarEsquerda / VirarDireita com o DORSO estabilizado: a cada quadro a rotacao
#       de mundo do osso da sela (spine_02, entre os ombros) e puxada para a media do ciclo (fica ESTAB do desvio) por
#       contra-rotacao em spine_01; pernas, raiz e pes intactos (apoio igual ao do clipe de origem); cabeca um pouco mais alta
#   Mount     idle -> agacha (pes como no idle), asas sobem e abrem para liberar os flancos (simetrico: serve dos dois lados),
#             segura, levanta e termina EXATAMENTE no quadro 0 do RideIdle
#   Dismount  RideIdle -> agacha e abre as asas -> volta ao idle; termina EXATAMENTE no quadro 0 do idle
# Uso: blender -b Wyvern_E7_clipes_L3b.blend -P 16_montaria.py -- <08_base.py> <saida.blend> <manifesto.json>
import bpy, sys, math, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
for n in ("Corrida", "VirarEsquerda", "VirarDireita"):
    FONTE[n] = curvas(bpy.data.actions[n]); DUR[n] = bpy.data.actions[n].frame_range[1] / FPS_CENA
I0, FI0 = amostra("idle_loop", 0.0)
T_IDLE = DUR["idle_loop"]
SELA = "spine_02"; ESTAB = 0.35
def rot_mundo_osso(P, b): return fk(P, [b])[b].to_quaternion()
def rot_media(clipe, n=48):
    acc = Q((0, 0, 0, 0)); ref = None
    for k in range(n):
        P, _ = amostra(clipe, DUR[clipe] * k / n); q = rot_mundo_osso(P, SELA)
        if ref is None: ref = q
        if q.dot(ref) < 0: q = -q
        acc = Q([acc[i] + q[i] / n for i in range(4)])
    return acc.normalized()
MEDIA = {c: rot_media(c) for c in ("idle_loop", "walk_loop", "Corrida", "VirarEsquerda", "VirarDireita")}
def estabilizar(P, clipe, k=1.0):
    """leva a rotacao de mundo da sela para slerp(media, atual, ESTAB) girando spine_01 (2 passadas)"""
    alvo_m = MEDIA[clipe]
    for _ in range(2):
        q = rot_mundo_osso(P, SELA); m = alvo_m if alvo_m.dot(q) >= 0 else -alvo_m
        alvo = m.slerp(q, 1 - (1 - ESTAB) * k)
        d = alvo @ q.inverted()                                       # delta no espaco do armature
        ax, ang = d.to_axis_angle()
        if ang > math.pi: ang -= 2 * math.pi
        if abs(ang) < 1e-7: break
        eixo_mundo = (arm.matrix_world.to_3x3() @ ax).normalized()
        girar(P, "spine_01", eixo_mundo, ang)
    return P
def cabeca_alta(P, k=1.0):
    for b in PESCOCO[:3]: girar(P, b, X, R(-1.5) * k)
    girar(P, "head", X, R(3) * k)
def ride(clipe):
    def f(t):
        P, fold = amostra(clipe, t); estabilizar(P, clipe); cabeca_alta(P)
        return P, fold
    return f
# ---------------------------------------------------------------- agachar (pe identico ao idle; como no Comer aprovado)
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
Q_MONT = 2.2
def montar_pose(P, k, fold):
    """k 0..1: agacha, peito baixa um pouco, asas sobem/abrem para fora (flancos livres), cabeca vira para tras de leve"""
    if k <= 1e-4: return P, fold
    agachar(P, Q_MONT * k)
    girar(P, "spine_01", X, R(5) * k)
    for s in "LR":
        girar(P, "shoulder_" + s, Y, R(-28) * sx_(s) * k)            # asa sobe/abre
        girar(P, "shoulder_" + s, Z, R(-10) * sx_(s) * k)            # e vai um pouco a frente
    for b in PESCOCO[2:]: girar(P, b, X, R(-2) * k)
    for b in CAUDA[:2]: girar(P, b, X, R(2.5) * k)                     # cauda acompanha o agachamento sem tocar o chao
    return P, fold * (1 - 0.6 * k)
T_MON, T_DES = 2.4, 2.0
RIDE_IDLE = ride("idle_loop")
def c_mount(t):
    k = suave(t / 0.7) * (1 - suave((t - 1.5) / 0.8))                 # desce 0-0,7; segura; sobe 1,5-2,3
    wr = suave((t - 1.4) / 0.9)                                       # passa do idle ao RideIdle ao levantar
    Pi, fi = amostra("idle_loop", t); Pr, fr = RIDE_IDLE((t - T_MON) % T_IDLE)   # termina no quadro 0 do RideIdle
    P = misturar(Pi, Pr, wr); fold = fi * (1 - wr) + fr * wr
    return montar_pose(P, k, fold)
def c_dismount(t):
    k = suave(t / 0.6) * (1 - suave((t - 1.2) / 0.7))
    wr = 1 - suave((t - 0.3) / 0.9)
    Pr, fr = RIDE_IDLE(t % T_IDLE); Pi, fi = amostra("idle_loop", (t - T_DES) % T_IDLE)   # termina no quadro 0 do idle
    P = misturar(Pi, Pr, wr); fold = fi * (1 - wr) + fr * wr
    return montar_pose(P, k, fold)
CLIPES = {"RideIdle": (RIDE_IDLE, T_IDLE, True), "RideWalk": (ride("walk_loop"), DUR["walk_loop"], True),
          "RideRun": (ride("Corrida"), DUR["Corrida"], True), "RideVirarEsquerda": (ride("VirarEsquerda"), DUR["VirarEsquerda"], True),
          "RideVirarDireita": (ride("VirarDireita"), DUR["VirarDireita"], True),
          "Mount": (c_mount, T_MON, False), "Dismount": (c_dismount, T_DES, False)}
mani = {"_fonte": "Wyvern_E7_clipes_L3b.blend (idle_loop, walk_loop, Corrida, Viradas)", "_hz": HZ, "_osso_sela": SELA, "_estab": ESTAB,
        "_agachar_mount": Q_MONT}
for nome, (fn, dur, loop) in CLIPES.items():
    mani[nome] = gravar_clipe(nome, fn, dur, loop); print("CLIPE", nome, mani[nome], flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
