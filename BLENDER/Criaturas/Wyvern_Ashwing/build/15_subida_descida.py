# Subida, Descida e Mergulho em pleno voo (pedido do usuario em 06/11/2026), sobre Wyvern_E7_clipes_L3.blend (preservado).
# So acrescenta estas 3 actions. Fontes: fly_loop (Ashwing) e Planeio (lote 1). Inclinacoes com pivo na PELVE (o corpo
# nao desloca em relacao aos outros clipes de voo, feitos no lugar). Clipes visuais: angulos e tempos sao PROPOSTA.
#   Subida    batidas do fly_loop 10% mais rapidas e 20% mais amplas, nariz para cima 22 graus, pernas recolhidas, loop
#   Descida   planeio com nariz para baixo 15 graus, asas um pouco recuadas e em V leve, cabeca olhando a frente, loop
#   Mergulho  nariz para baixo 45 graus, asas meio fechadas e recuadas junto ao corpo (tremor), cauda reta, loop
# Uso: blender -b Wyvern_E7_clipes_L3.blend -P 15_subida_descida.py -- <08_base.py> <saida.blend> <manifesto.json>
import bpy, sys, math, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
FONTE["Planeio"] = curvas(bpy.data.actions["Planeio"]); DUR["Planeio"] = bpy.data.actions["Planeio"].frame_range[1] / FPS_CENA
I0, FI0 = amostra("idle_loop", 0.0)
T_FLY = DUR["fly_loop"]; T_PLA = DUR["Planeio"]
ASAS = ASA["L"] + ASA["R"]
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
MED_FLY = media("fly_loop")
def sx_(s): return 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
def inclinar(P, graus):
    """+ = nariz para baixo; pivo na pelve"""
    p0 = cabeca(fk(P, ["pelvis"]), "pelvis"); girar(P, "root", X, R(graus)); mover(P, "root", p0 - cabeca(fk(P, ["pelvis"]), "pelvis"))
def pernas_recolhidas(P, k=1.0):
    for s in "LR":
        girar(P, "thigh_" + s, X, R(28) * k); girar(P, "calf_" + s, X, R(-25) * k); girar(P, "toe_" + s, X, R(20) * k)
T_SUB = T_FLY / 1.1
def c_subida(t):
    P, _ = amostra("fly_loop", t * 1.1); ampliar(P, MED_FLY, 1.2, ASAS)
    u = 2 * math.pi * t / T_SUB
    inclinar(P, -22)
    for b in PESCOCO: girar(P, b, X, R(1.5))                          # cabeca acompanha a subida (olha a frente/acima)
    girar(P, "head", X, R(-4))
    pernas_recolhidas(P, 0.8)
    for b in CAUDA[:3]: girar(P, b, X, R(3))                          # cauda alinhada ao corpo (leme)
    for i, b in enumerate(CAUDA[3:]): girar(P, b, X, R(1.0) * math.sin(u - 0.4 * i))
    return P, 0.0
T_DES = T_PLA
def c_descida(t):
    P, _ = amostra("Planeio", t)
    u = 2 * math.pi * t / T_DES
    inclinar(P, 15)
    for s in "LR":
        girar(P, "shoulder_" + s, Z, R(12) * sx_(s))                  # asas recuadas (menos area)
        girar(P, "shoulder_" + s, Y, R(-6) * sx_(s))                  # V leve (estabilidade)
    for b in PESCOCO: girar(P, b, X, R(-2.5))                         # olha a frente
    girar(P, "head", X, R(-3))
    pernas_recolhidas(P, 0.6)
    for b in CAUDA[:3]: girar(P, b, X, R(1.5))
    for i, b in enumerate(CAUDA[3:]): girar(P, b, Z, R(0.8) * math.sin(u - 0.3 * i))
    return P, 0.0
T_MER = 1.2
PLA0, _ = amostra("Planeio", 0.0)
W_FECHA = 0.55                                                       # mistura asa aberta (planeio) -> dobrada (idle)
def c_mergulho(t):
    P, _ = amostra("Planeio", 0.0); u = 2 * math.pi * t / T_MER
    P = misturar(P, I0, W_FECHA, ASAS)
    for s in "LR":
        girar(P, "shoulder_" + s, Z, R(16) * sx_(s))                  # recuadas junto ao corpo
        girar(P, "upperarm_" + s, FRENTE, R(1.5) * math.sin(u * 3) * sx_(s) * ESQ)   # tremor no vento
    inclinar(P, 45)
    for b in PESCOCO: girar(P, b, X, R(-6))                           # pescoco estendido na linha do corpo
    girar(P, "head", X, R(-8))
    pernas_recolhidas(P, 1.0)
    for b in CAUDA[:3]: girar(P, b, X, R(2.5))                        # cauda reta (aerodinamica)
    for i, b in enumerate(CAUDA[4:]): girar(P, b, Z, R(0.6) * math.sin(u * 2 - 0.4 * i))
    return P, FI0 * W_FECHA
CLIPES = {"Subida": (c_subida, T_SUB, True), "Descida": (c_descida, T_DES, True), "Mergulho": (c_mergulho, T_MER, True)}
mani = {"_fonte": "Wyvern_E7_clipes_L3.blend (fly_loop, Planeio, idle_loop); so Subida/Descida/Mergulho acrescentados", "_hz": HZ,
        "_inclinacao_graus": {"Subida": -22, "Descida": 15, "Mergulho": 45}, "_asa_fechada_mergulho": W_FECHA}
for nome, (fn, dur, loop) in CLIPES.items():
    mani[nome] = gravar_clipe(nome, fn, dur, loop); print("CLIPE", nome, mani[nome], flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
