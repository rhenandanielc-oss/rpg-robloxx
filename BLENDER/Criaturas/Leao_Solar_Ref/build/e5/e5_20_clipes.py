"""E5: gerador dos clipes do Leao Solar (Fase A). Tudo e gravado em CHAVES (quaternions por osso + posicao da Raiz):
nenhuma restricao/solver precisa existir no Roblox.
Como funciona, por quadro:
1. trajetoria da raiz (posicao e rumo) integrada da velocidade/rumo do clipe (com deslocamento real, para ver o
   escorregamento; a versao "no lugar" para o jogo e a mesma com a translacao da Raiz zerada);
2. postura do tronco (quadril, coluna, peito, pescoco) por funcoes da fase da marcha + parametros do clipe;
3. planejador de passos por pata: no APOIO a pata fica PARADA no mundo; ao decolar, calcula o pouso a partir da posicao
   prevista da raiz no instante do pouso (metade do arco de apoio a frente do ponto neutro) e faz o balanco em arco;
4. IK analitico de 2 ossos (umero+antebraco ate o punho; coxa+canela ate o jarrete), com o metacarpo/metatarso
   orientado por regra (extensao no fim do apoio, flexao no balanco) e a escapula rolando com o umero;
5. cabeca estabilizada no mundo (so segue o rumo e o olhar do clipe);
6. secundarios gravados: auxiliares de volume = metade do filho; cauda em onda atrasada; tufo e juba por mola amortecida
   sobre a velocidade angular do osso pai (atraso e retorno, sem fisica no jogo).
QA por clipe: erro do IK, escorregamento das patas em apoio (vertices da sola), altura minima da malha, emenda do loop.
Uso: blender -b E5_rig.blend -P e5_20_clipes.py -- <saida_dir> <clipe1,clipe2|todos> [render=1] [res=540]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
SO = A[1].split(","); REND = (A[2] != "0") if len(A) > 2 else True; RES = int(A[3]) if len(A) > 3 else 540
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS; DT = 1.0 / FPS
arm = bpy.data.objects["Leao_Solar_Rig"]; ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]
PB = arm.pose.bones; BD = arm.data.bones; MOD = ob.modifiers["Armature"]
for pb in PB: pb.rotation_mode = "QUATERNION"
R = math.radians
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def janela(t, a, b, sub=0.25, des=0.25): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
def upd(): bpy.context.view_layer.update()
# ------------------------------------------------------------------ geometria do rig
PERNAS = {"DD": ("dian", ["Escapula_DD", "Umero_DD", "Antebraco_DD", "Mao_DD", "Dedos_DD"]),
          "DE": ("dian", ["Escapula_DE", "Umero_DE", "Antebraco_DE", "Mao_DE", "Dedos_DE"]),
          "TD": ("tras", ["Coxa_TD", "Canela_TD", "Metatarso_TD", "Dedos_TD"]),
          "TE": ("tras", ["Coxa_TE", "Canela_TE", "Metatarso_TE", "Dedos_TE"])}
LEN = {b.name: b.length for b in BD}
def pt(b, tail=False): return (BD[b].tail_local if tail else BD[b].head_local).copy()
# pontos neutros das patas (local da raiz, frente = -Y): dianteiras como no repouso, traseiras centradas sob o quadril
OMBRO = {"DD": V((1.5, -9.3, 0)), "DE": V((-1.5, -9.3, 0)), "TD": V((1.5, 6.2, 0)), "TE": V((-1.5, 6.2, 0))}   # projecao no chao (local da raiz)
ALC_PADRAO = ((2.7, 3.3), (3.5, 3.7))   # alcance horizontal (frente, tras) das dianteiras e traseiras em relacao ao ombro|quadril (studs)
def alcance(g, tipo): return g.get("alc", ALC_PADRAO)[0 if tipo == "dian" else 1]
NEUTRO = {"DD": V((1.75, -9.3, 0.6)), "DE": V((-1.75, -9.3, 0.6)), "TD": V((1.85, 6.15, 0.7)), "TE": V((-1.85, 6.15, 0.7))}
REP_PATA = {k: pt(PERNAS[k][1][-1]) for k in PERNAS}                       # ponto "pata" (cabeca do osso Dedos) no repouso
VEC_DEDOS = {k: pt(PERNAS[k][1][-1], True) - pt(PERNAS[k][1][-1]) for k in PERNAS}
VEC_META = {k: pt(PERNAS[k][1][-2], True) - pt(PERNAS[k][1][-2]) for k in PERNAS}   # punho->pata / jarrete->pata
QUAD_PATA = {k: REP_PATA[k] - pt(PERNAS[k][1][0]) for k in ("TD", "TE")}   # quadril (cabeca da coxa) -> pata, no repouso
AUX = {"Cotovelo_Aux_DD": "Antebraco_DD", "Cotovelo_Aux_DE": "Antebraco_DE", "Punho_Aux_DD": "Mao_DD", "Punho_Aux_DE": "Mao_DE"}
SEC = [b.name for b in BD if b.name.startswith(("Juba_", "Tufo"))]
CAUDA = ["Cauda%d" % i for i in range(1, 7)]
def rot_local(nome, q_mundo):
    """rotacao dada em eixos do mundo (repouso) -> quaternion local do osso"""
    r = BD[nome].matrix_local.to_3x3(); return (r.inverted() @ q_mundo.to_matrix() @ r).to_quaternion()
def qx(a): return Quaternion(X, a)
def qy(a): return Quaternion(Y, a)
def qz(a): return Quaternion(Z, a)
def zerar():
    for pb in PB: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
def mirar(nome, alvo):
    """gira o osso (a partir da orientacao herdada) pelo menor arco ate a ponta apontar para 'alvo' (espaco da armadura)"""
    pb = PB[nome]; pb.rotation_quaternion = (1, 0, 0, 0); upd()
    M = pb.matrix.copy(); y = M.col[1].xyz.normalized(); d = (alvo - M.translation)
    if d.length < 1e-6: return
    Rm = y.rotation_difference(d.normalized()).to_matrix()
    pb.matrix = Matrix.LocRotScale(M.translation, (Rm @ M.to_3x3().normalized()).to_quaternion(), None); upd()
def orientar(nome, q_mundo_rel):
    """poe o osso com a orientacao do repouso girada por q_mundo_rel (mundo), mantendo a posicao herdada"""
    pb = PB[nome]; pb.rotation_quaternion = (1, 0, 0, 0); upd(); M = pb.matrix.copy()
    pb.matrix = Matrix.LocRotScale(M.translation, (q_mundo_rel.to_matrix() @ BD[nome].matrix_local.to_3x3()).to_quaternion(), None); upd()
def _sinal_flexao(nome, eixo_mundo, sentido):
    """+1 se girar o osso em +X local leva a ponta no 'sentido' (mundo) dado; mede no repouso, sem supor espelhamento de eixos"""
    zerar(); upd(); t0 = PB[nome].tail.copy(); PB[nome].rotation_quaternion = Quaternion(X, 0.3); upd()
    d = (PB[nome].tail - t0).dot(sentido); zerar(); upd(); return 1 if d > 0 else -1
SG_PUNHO = {p_: _sinal_flexao("Mao_" + p_, None, V((0, 1, 0))) for p_ in ("DD", "DE")}      # flexao palmar: ponta do metacarpo para tras
SG_DEDOS = {p_: _sinal_flexao("Dedos_" + p_, None, V((0, 0, -1))) for p_ in ("DD", "DE")}   # dedos fecham: ponta para baixo
SG_JARRETE = {p_: _sinal_flexao("Metatarso_" + p_, None, V((0, 1, 0))) for p_ in ("TD", "TE")}   # + = jarrete abre (ponta do metatarso para tras)
SG_DEDOS.update({p_: _sinal_flexao("Dedos_" + p_, None, V((0, 0, -1))) for p_ in ("TD", "TE")})
print("SINAIS punho", SG_PUNHO, "dedos", SG_DEDOS)
def ik2(S, W, l1, l2, polo):
    d = (W - S).length; d = min(d, (l1 + l2) * 0.999); u = (W - S).normalized(); W2 = S + u * d
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d); h = math.sqrt(max(l1 * l1 - a * a, 0.0)); v = polo - u * polo.dot(u)
    v = v.normalized() if v.length > 1e-6 else Z; return S + u * a + v * h, W2
# ------------------------------------------------------------------ marchas (fases de pouso de cada pata)
MARCHA = {
    # f = passadas/s, beta = fracao de apoio, off = fase de cada pata, h = altura do balanco (dian, tras), S = passada (studs)
    "parado": dict(f=0.0, beta=1.0, off={"TE": 0.0, "DE": 0.25, "TD": 0.5, "DD": 0.75}, h=(0.0, 0.0)),
    "andar": dict(f=60 / 73, beta=0.64, off={"TE": 0.0, "DE": 0.24, "TD": 0.5, "DD": 0.74}, h=(1.25, 0.95)),
    "trote": dict(f=60 / 46, beta=0.46, off={"TE": 0.0, "DD": 0.04, "TD": 0.5, "DE": 0.54}, h=(1.7, 1.3)),
    # galope rotatorio felino: traseiras (TE, TD) -> dianteiras (DD, DE) -> voo recolhido; apoio curto e passada longa
    "corrida": dict(f=60 / 38, beta=0.26, off={"TE": 0.0, "TD": 0.13, "DD": 0.42, "DE": 0.56}, h=(2.3, 1.3), alc=((4.0, 3.9), (2.6, 4.3))),
}
def mistura(g1, g2, w):
    a, b = MARCHA[g1], MARCHA[g2]
    off = {}
    for k in a["off"]:
        d = (b["off"][k] - a["off"][k] + 0.5) % 1.0 - 0.5; off[k] = (a["off"][k] + w * d) % 1.0
    f = a["f"] + w * (b["f"] - a["f"]) if a["f"] > 0 and b["f"] > 0 else (b["f"] if w > 0.5 else a["f"])
    ca, cb = a.get("alc", ALC_PADRAO), b.get("alc", ALC_PADRAO)
    alc = tuple(tuple(ca[i][j] + w * (cb[i][j] - ca[i][j]) for j in range(2)) for i in range(2))
    return dict(f=f, beta=a["beta"] + w * (b["beta"] - a["beta"]), off=off, h=tuple(a["h"][i] + w * (b["h"][i] - a["h"][i]) for i in range(2)), alc=alc)
# ------------------------------------------------------------------ clipes: parametros em funcao do tempo
# cada clipe: dur, loop, marcha(t)->dict, vel(t) studs/s, rumo_vel(t) rad/s, corpo(t, fase)->dict de angulos/alturas
def corpo_base():
    return dict(labio=0.0, lingua=0.0, y=0.0, col1=0.0, col2=0.0, z=0.0, x=0.0, pitch=0.0, roll=0.0, col_pitch=0.0, col_yaw=0.0, peito_roll=0.0, pesc=0.0, pesc_yaw=0.0, cab_pitch=0.0, cab_yaw=0.0,
                cab_roll=0.0, mand=0.0, orelha=(0.0, 0.0), palp=0.0, cauda_base=0.0, cauda_amp=0.0, cauda_f=0.0, cauda_yaw=0.0, resp=0.0)
def mist(c1, c2, w):
    out = {}
    for k in c1:
        a, b = c1[k], c2[k]
        out[k] = tuple(x + w * (y - x) for x, y in zip(a, b)) if isinstance(a, tuple) else a + w * (b - a)
    return out
def resp(t, T=3.6): return math.sin(2 * math.pi * t / T)
def piscar(t, ts, d=0.16): return max((math.sin(math.pi * min(max((t - a) / d, 0), 1)) for a in ts), default=0.0)
def c_repouso_vigilante(t, fase):
    c = corpo_base(); b = resp(t, 3.4)
    c.update(resp=b, z=0.035 * b, col_pitch=R(0.7) * b, pesc=R(-1.0) * b, cab_pitch=R(0.6) * b)
    c["cab_yaw"] = R(9) * janela(t, 0.8, 2.6, 0.5, 0.5) - R(7) * janela(t, 3.6, 5.4, 0.5, 0.5)   # olha para um lado, depois o outro
    c["orelha"] = (R(-14) * janela(t, 1.0, 1.5, 0.08, 0.15), R(-12) * janela(t, 4.0, 4.5, 0.08, 0.15))  # orelhas giram para o som
    c["palp"] = R(-42) * piscar(t, (2.2, 5.1))
    c["cauda_base"] = R(4); c["cauda_amp"] = R(5); c["cauda_f"] = 1 / 6.8
    c["x"] = 0.06 * math.sin(2 * math.pi * t / 6.8)                                            # peso passa de um lado ao outro
    return c
def c_repouso_relaxado(t, fase):
    c = corpo_base(); b = resp(t, 4.4)
    c.update(resp=b, z=-0.12 + 0.045 * b, col_pitch=R(1.0) * b + R(1.5), pesc=R(10) + R(-1.2) * b, cab_pitch=R(-6) + R(0.8) * b)
    c["cab_yaw"] = R(4) * math.sin(2 * math.pi * t / 8.8)
    c["palp"] = R(-18) + R(-24) * piscar(t, (3.0, 7.2), 0.22)                                   # olhos meio fechados, piscada lenta
    c["orelha"] = (R(8), R(8)); c["cauda_base"] = R(10); c["cauda_amp"] = R(9); c["cauda_f"] = 1 / 4.4
    c["x"] = 0.05 * math.sin(2 * math.pi * t / 8.8)
    return c
def c_observar(t, fase):
    """fica alerta: levanta a cabeca, fixa um ponto a esquerda, fareja (focinho sobe em pulsos), volta"""
    c = corpo_base(); b = resp(t, 3.0); foco = janela(t, 0.4, 4.6, 0.6, 0.7)
    fare = sum(janela(t, a, a + 0.22, 0.07, 0.1) for a in (2.0, 2.35, 2.7))
    c.update(resp=b, z=0.03 * b + 0.06 * foco, col_pitch=R(0.7) * b, pesc=R(-12) * foco, cab_pitch=R(4) * foco + R(-5) * fare, cab_yaw=R(24) * foco,
             pesc_yaw=R(10) * foco, orelha=(R(-16) * foco, R(-16) * foco), palp=R(6) * foco + R(-42) * piscar(t, (4.9,)))
    c["cauda_base"] = R(2); c["cauda_amp"] = R(3) + R(6) * janela(t, 3.0, 4.2, 0.3, 0.4); c["cauda_f"] = 0.6
    return c
def c_locomocao(nome):
    def f(t, fase):
        c = corpo_base(); p = 2 * math.pi * fase
        if nome == "andar":
            c.update(z=-0.28 + 0.07 * math.cos(2 * p), x=0.10 * math.sin(p), roll=R(1.2) * math.sin(p), col_yaw=R(2.5) * math.sin(p + 0.6),
                     peito_roll=R(-2.0) * math.sin(p + 0.3), pesc=R(14), cab_pitch=R(-10), cauda_base=R(6), cauda_amp=R(6), cauda_f=0.82, cauda_yaw=0)
        elif nome == "trote":
            c.update(z=-0.25 + 0.14 * math.cos(2 * p), col_pitch=R(1.5) * math.cos(2 * p), x=0.04 * math.sin(p), col_yaw=R(1.5) * math.sin(p),
                     pesc=R(10), cab_pitch=R(-7), cauda_base=R(10), cauda_amp=R(7), cauda_f=1.3)
        else:   # corrida (galope rotatorio)
            fl = math.cos(p - 2 * math.pi * 0.88)                      # +1 = coluna fechada (voo recolhido), -1 = aberta (traseiras empurram, dianteiras alcancam)
            c.update(z=-0.75 + 0.40 * math.cos(p - 2 * math.pi * 0.86), pitch=R(4.5) * math.cos(p - 2 * math.pi * 0.62),
                     col1=R(9) * fl, col2=R(-11) * fl, peito_roll=0.0, pesc=R(5) + R(5) * fl, cab_pitch=R(-3),
                     x=0.05 * math.sin(p), cauda_base=R(14) - R(5) * fl, cauda_amp=R(7), cauda_f=MARCHA["corrida"]["f"], orelha=(R(16), R(16)), palp=R(-6))
        c["resp"] = math.sin(p)
        return c
    return f
def rampa(t, a, b): return suave((t - a) / max(b - a, 1e-6))
def marcha_rampa(g, t, a, b, fmin=0.55):
    """marcha g com frequencia subindo de fmin*f ate f entre a e b (passos curtos no comeco)"""
    m = dict(MARCHA[g]); m["f"] = m["f"] * (fmin + (1 - fmin) * rampa(t, a, b)); m["h"] = tuple(h * (0.6 + 0.4 * rampa(t, a, b)) for h in m["h"]); return m
V_ANDAR, V_TROTE, V_CORRIDA = MARCHA["andar"]["f"] * 9.5, MARCHA["trote"]["f"] * 13.0, MARCHA["corrida"]["f"] * 22.0
LOC = {k: c_locomocao(k) for k in ("andar", "trote", "corrida")}
def c_trans(g1, g2, a, b):
    def f(t, fase): return mist(LOC[g1](t, fase), LOC[g2](t, fase), rampa(t, a, b))
    return f
def c_inicio(g, a, b):
    def f(t, fase): return mist(c_repouso_vigilante(t, fase), LOC[g](t, fase), rampa(t, a, b))
    return f
def c_fim(g, a, b, final=None):
    def f(t, fase): return mist(LOC[g](t, fase), (final or c_repouso_vigilante)(t, fase), rampa(t, a, b))
    return f
T_ARR = 0.48   # instante da explosao
def c_arrancada(t, fase):
    """antecipacao (agacha fundo, peso para tras, coluna fecha, cabeca baixa e olhar fixo a frente, orelhas para a frente, cauda baixa)
    -> explosao (dianteiras saem primeiro, coluna abre, peito sobe e vai a frente, traseiras empurram) -> galope acelerando"""
    c = c_repouso_vigilante(t, fase); ag = janela(t, 0.0, T_ARR + 0.06, 0.38, 0.10)
    c.update(z=-1.8 * ag, pitch=0.0, col1=R(7) * ag, col2=R(-8) * ag, pesc=R(27) * ag, cab_pitch=R(9) * ag, cab_yaw=0.0, pesc_yaw=0.0,
             orelha=(R(-14) * ag, R(-14) * ag), palp=R(-10) * ag, cauda_base=R(26) * ag, cauda_amp=R(1.5), cauda_f=0.4, x=0.0)
    ex = janela(t, T_ARR + 0.06, T_ARR + 0.40, 0.08, 0.16)                  # explosao: peito sobe, coluna abre
    c["pitch"] += R(-7) * ex; c["col1"] += R(-9) * ex; c["col2"] += R(10) * ex; c["z"] += 1.4 * ex; c["cauda_base"] += R(10) * ex
    return mist(c, LOC["corrida"](t, fase), rampa(t, T_ARR + 0.15, T_ARR + 0.75))
def c_frenagem(t, fase):
    """corrida -> frenagem: dianteiras seguram, peito baixa, cabeca estabiliza, cauda equilibra -> parado"""
    c = mist(LOC["corrida"](t, fase), LOC["trote"](t, fase), rampa(t, 0.2, 0.7)); c = mist(c, LOC["andar"](t, fase), rampa(t, 0.7, 1.2))
    fr = janela(t, 0.25, 1.4, 0.3, 0.5)
    c["pitch"] += R(-3.5) * fr; c["z"] += -0.25 * fr; c["pesc"] += R(-8) * fr; c["cauda_base"] += R(12) * fr
    return mist(c, c_repouso_vigilante(t, fase), rampa(t, 1.3, 2.0))
def c_virar(lado):
    def f(t, fase):
        c = c_repouso_vigilante(t, fase); v = janela(t, 0.0, 2.4, 0.35, 0.6); sg = 1 if lado == "E" else -1
        c.update(cab_yaw=sg * R(26) * janela(t, -0.1, 2.0, 0.25, 0.6), pesc_yaw=sg * R(12) * v, col_yaw=sg * R(6) * v, cauda_yaw=-sg * R(14) * v,
                 cauda_amp=R(4), z=-0.15 * v, palp=0.0)
        return c
    return f
CLIPES = {
    "Repouso_Vigilante": dict(dur=6.8, loop=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_repouso_vigilante, pose_repouso=True),
    "Repouso_Relaxado": dict(dur=8.8, loop=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_repouso_relaxado, pose_repouso=True),
    "Observar_Farejar": dict(dur=5.2, loop=False, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_observar, pose_repouso=True),
    "Andar": dict(dur=73 / 30, loop=True, marcha=lambda t: MARCHA["andar"], vel=lambda t: V_ANDAR, rumo=lambda t: 0.0, corpo=c_locomocao("andar")),
    "Trote": dict(dur=46 / 30, loop=True, marcha=lambda t: MARCHA["trote"], vel=lambda t: V_TROTE, rumo=lambda t: 0.0, corpo=c_locomocao("trote")),
    "Repouso_para_Andar": dict(dur=2.4, loop=False, inicio_repouso=True, fase0=0.70, marcha=lambda t: marcha_rampa("andar", t, 0.0, 1.4),
                               vel=lambda t: V_ANDAR * rampa(t, 0.05, 1.6), rumo=lambda t: 0.0, corpo=c_inicio("andar", 0.0, 1.2)),
    "Andar_para_Repouso": dict(dur=2.6, loop=False, parar_em=0.9, parar_repouso=True, marcha=lambda t: MARCHA["andar"],
                               vel=lambda t: V_ANDAR * (1 - rampa(t, 0.0, 1.3)), rumo=lambda t: 0.0, corpo=c_fim("andar", 0.6, 1.9)),
    "Andar_para_Trote": dict(dur=2.4, loop=False, marcha=lambda t: mistura("andar", "trote", rampa(t, 0.3, 1.5)),
                             vel=lambda t: V_ANDAR + (V_TROTE - V_ANDAR) * rampa(t, 0.3, 1.7), rumo=lambda t: 0.0, corpo=c_trans("andar", "trote", 0.3, 1.5)),
    "Trote_para_Andar": dict(dur=2.4, loop=False, marcha=lambda t: mistura("trote", "andar", rampa(t, 0.3, 1.5)),
                             vel=lambda t: V_TROTE + (V_ANDAR - V_TROTE) * rampa(t, 0.2, 1.6), rumo=lambda t: 0.0, corpo=c_trans("trote", "andar", 0.3, 1.5)),
    "Trote_para_Corrida": dict(dur=2.0, loop=False, marcha=lambda t: mistura("trote", "corrida", rampa(t, 0.2, 1.0)),
                               vel=lambda t: V_TROTE + (V_CORRIDA - V_TROTE) * rampa(t, 0.2, 1.3), rumo=lambda t: 0.0, corpo=c_trans("trote", "corrida", 0.2, 1.0)),
    "Corrida_para_Trote": dict(dur=2.0, loop=False, marcha=lambda t: mistura("corrida", "trote", rampa(t, 0.2, 1.0)),
                               vel=lambda t: V_CORRIDA + (V_TROTE - V_CORRIDA) * rampa(t, 0.1, 1.2), rumo=lambda t: 0.0, corpo=c_trans("corrida", "trote", 0.2, 1.0)),
    "Arrancada": dict(dur=2.3, loop=False, inicio_repouso=True, marcha=lambda t: MARCHA["parado"] if t < T_ARR else marcha_rampa("corrida", t, T_ARR, T_ARR + 0.9, 0.8),
                      primeiros={"DD": 0.0, "DE": 0.08, "TD": 0.20, "TE": 0.27},      # 1o balanco de cada pata (s apos a explosao): dianteiras, depois o impulso traseiro
                      vel=lambda t: V_CORRIDA * (1 - (1 - min(max((t - T_ARR - 0.05) / 1.1, 0.0), 1.0)) ** 2), rumo=lambda t: 0.0, corpo=c_arrancada),
    "Frenagem": dict(dur=2.4, loop=False, parar_em=1.15, parar_repouso=True,
                     marcha=lambda t: mistura("trote", "andar", rampa(t, 0.7, 1.1)) if t > 0.7 else mistura("corrida", "trote", rampa(t, 0.2, 0.7)),
                     vel=lambda t: V_CORRIDA * (1 - rampa(t, 0.1, 1.3)), rumo=lambda t: 0.0, corpo=c_frenagem),
    "Virar_E": dict(dur=2.9, loop=False, inicio_repouso=True, parar_em=1.95, parar_repouso=True, fase0=0.70, pivo=V((0, -1.6, 0)),
                    marcha=lambda t: dict(MARCHA["andar"], f=1.25, beta=0.55), vel=lambda t: 0.0,
                    rumo=lambda t: R(90) / 1.525 * janela(t, 0.15, 1.95, 0.25, 0.3), corpo=c_virar("E")),
    "Virar_D": dict(dur=2.9, loop=False, inicio_repouso=True, parar_em=1.95, parar_repouso=True, fase0=0.20, pivo=V((0, -1.6, 0)),
                    marcha=lambda t: dict(MARCHA["andar"], f=1.25, beta=0.55), vel=lambda t: 0.0,
                    rumo=lambda t: -R(90) / 1.525 * janela(t, 0.15, 1.95, 0.25, 0.3), corpo=c_virar("D")),
    "Corrida": dict(dur=38 / 30, loop=True, marcha=lambda t: MARCHA["corrida"], vel=lambda t: V_CORRIDA, rumo=lambda t: 0.0, corpo=c_locomocao("corrida")),
}
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "e5_21_faseB.py"), encoding="utf-8").read())   # clipes da Fase B
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "e5_22_montaria.py"), encoding="utf-8").read())   # S2: montaria
# ------------------------------------------------------------------ simulacao de um clipe
PRE = 3.0   # segundos de pre-rolagem (o ciclo entra ja estabilizado)
def catmull(P, k, s_):
    p0, p1, p2, p3 = P[max(k - 1, 0)], P[k], P[k + 1], P[min(k + 2, len(P) - 1)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * s_ + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s_ ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s_ ** 3)
def hermite_nu(us, P, u, para=None):
    """spline de Hermite com nos nao uniformes (tangentes Catmull-Rom ponderadas pelo tempo de cada trecho); tangente zero nas pontas
    e nos indices em 'para' (pausa/impacto). Velocidade continua mesmo com trechos de duracoes muito diferentes."""
    n = len(us); para = para or set(); m = []
    for i in range(n):
        if i == 0 or i == n - 1 or i in para: m.append(P[i] * 0.0); continue
        h0, h1 = us[i] - us[i - 1], us[i + 1] - us[i]
        m.append(((P[i + 1] - P[i]) / h1 * h0 + (P[i] - P[i - 1]) / h0 * h1) / (h0 + h1))
    k = max(i for i in range(n - 1) if us[i] <= u) if u < us[-1] else n - 2; h = us[k + 1] - us[k]; x = min(max((u - us[k]) / h, 0.0), 1.0)
    return ((2 * x ** 3 - 3 * x ** 2 + 1) * P[k] + (x ** 3 - 2 * x ** 2 + x) * h * m[k] + (-2 * x ** 3 + 3 * x ** 2) * P[k + 1] + (x ** 3 - x ** 2) * h * m[k + 1])
def agenda_pata(cl, p_, t, rp, ry, estado, raiz):
    """acoes (bote, patada, mordida, esquiva): cada balanco = dict(t0, t1, alvo=V local (soma ao ponto de repouso da pata na pose da raiz
    em t1), h=altura do arco, via=[(u, V local relativo a raiz no instante, angulo_metacarpo|None)]). Fora dos balancos a pata fica apoiada."""
    e = estado.get(p_)
    if e is None: e = estado[p_] = dict(apoio=True, w=rp + qz(ry) @ REP_PATA[p_], yaw=ry, u=0.0, prog=0.0, dph=0.0, ang=None)
    lst = cl["agenda"].get(p_, []); sw = next((x for x in lst if x["t0"] <= t < x["t1"]), None)
    if sw is None:
        if not e["apoio"]: e.update(apoio=True, w=e["alvo"].copy(), yaw=e["yaw_alvo"], u=0.0, ang=None, sw=None, rel=None)
        nx = next((x for x in lst if x["t0"] > t), None); prox = nx["t0"] if nx else None; te = nx.get("t_emp", 0.18) if nx else 0.18
        e["prog"] = 0.55 + 0.45 * suave((t - (prox - te)) / te) if (prox is not None and prox - t < te) else 0.0   # calcanhar sobe antes de decolar
        e["a_emp"] = R(nx["empurra"]) if (nx and nx.get("empurra")) else None   # bote: impulso na ponta dos dedos (calcanhar bem alto)
        return
    if e.get("sw") is not sw:                                               # comeca o balanco: planeja pouso e passagem
        e["a_ini"] = e.get("a_emp"); e["a_emp"] = None                      # o balanco parte do angulo do impulso (sem salto)
        lp, ly = raiz(sw["t1"]); alvo = lp + qz(ly) @ (REP_PATA[p_] + sw.get("alvo", V((0, 0, 0))))
        pts, us, angs = [e["w"].copy()], [0.0], [None]
        for x_ in sw.get("via", []) if not sw.get("rel") else sw["rel"]["via"]:
            u_, off = x_[0], x_[1]; ang = x_[2] if (len(x_) > 2 and not sw.get("rel")) else None; tv = sw["t0"] + u_ * (sw["t1"] - sw["t0"])
            vp, vy = raiz(tv)
            pts.append(vp + qz(vy) @ (REP_PATA[p_] + off)); us.append(u_); angs.append(ang)
        pts.append(alvo); us.append(1.0); angs.append(0.0 if any(x is not None for x in angs) else None)   # pousa com a pata plana
        e.update(sw=sw, apoio=False, ini=e["w"].copy(), alvo=alvo, yaw_ini=e["yaw"], yaw_alvo=ly, pts=pts, us=us, angs=angs)
    uu = (t - sw["t0"]) / (sw["t1"] - sw["t0"]); pts, us = e["pts"], e["us"]
    vq = sw.get("via_quadril")
    jt = sw.get("jarrete")
    e["rq"] = dict(u=uu, via=vq, b=suave(uu / sw.get("solta_q", 0.10)) * (1 - suave((uu - 0.70) / 0.30)),
                   jarrete=R(hermite_nu([x[0] for x in jt], [x[1] for x in jt], uu)) if jt else None,
                   k=suave(uu / 0.12) * (1 - suave((uu - 0.88) / 0.12))) if vq else None
    if sw.get("rel"):                                                       # golpe: caminho Hermite + punho/dedos relativos (sem angulo no mundo)
        r_ = sw["rel"]; para_ = {i + 1 for i, x in enumerate(r_["via"]) if len(x) > 2 and x[2]}
        w = V(hermite_nu(us, [V(tuple(x)) for x in pts], uu, para_))
        ang_ = lambda tab: hermite_nu([x[0] for x in tab], [x[1] for x in tab], uu)
        k = suave(uu / 0.12) * (1 - suave((uu - 0.88) / 0.12))           # mistura com a pata apoiada (regra do apoio) na decolagem e no pouso
        e.update(w=w, yaw=e["yaw_ini"] + (e["yaw_alvo"] - e["yaw_ini"]) * suave(uu), u=uu, ang=None,
                 rel=dict(punho=R(ang_(r_["punho"])), dedos=R(ang_(r_["dedos"])), k=k, esc=r_.get("escapula", 0.32), a_regra=R(22) if uu < 0.5 else 0.0,
                          alcance_suave=r_.get("alcance_suave", False), u=uu, via_ombro=r_.get("via_ombro"),
                          b_ombro=suave(uu / 0.18) * (1 - suave((uu - 0.66) / 0.34)) if r_.get("via_ombro") else 0.0))
        return
    if len(pts) == 2:
        s_ = suave(uu); w = e["ini"].lerp(e["alvo"], s_); w.z = e["ini"].z + (e["alvo"].z - e["ini"].z) * s_ + sw.get("h", 1.2) * math.sin(math.pi * uu) ** 0.7; ang = None
    else:
        k = max(i for i in range(len(us) - 1) if us[i] <= uu); s_ = (uu - us[k]) / max(us[k + 1] - us[k], 1e-6); w = catmull(pts, k, s_)
        a0, a1 = e["angs"][k], e["angs"][k + 1]
        ang = None if (a0 is None and a1 is None) else ((a0 if a0 is not None else a1) * (1 - suave(s_)) + (a1 if a1 is not None else a0) * suave(s_))
    e.update(w=w, yaw=e["yaw_ini"] + (e["yaw_alvo"] - e["yaw_ini"]) * suave(uu), u=uu, ang=ang)
def simular(cl):
    dur = cl["dur"]; N = int(round(dur * FPS)); t0 = 0.0 if (cl.get("pose_repouso") or cl.get("inicio_repouso")) else -PRE   # pre-rolagem: a marcha entra estabilizada
    ts = np.arange(t0, dur + 2.0, DT)
    pos = [V((0, 0, 0))]; yaw = [0.0]
    for t in ts[1:]:
        y = yaw[-1] + cl["rumo"](t) * DT; yaw.append(y)
        pos.append(pos[-1] + qz(y) @ V((0, -1, 0)) * cl["vel"](t) * DT + qz(y) @ V((1, 0, 0)) * cl.get("vel_lat", lambda t: 0.0)(t) * DT)   # frente = -Y girada pelo rumo
    i0 = int(round(-t0 * FPS)); base = pos[i0].copy(); pos = [p - base for p in pos]
    def raiz(t):
        k = min(max(int(round((t - t0) * FPS)), 0), len(ts) - 1); pv = cl.get("pivo", V((0, 0, 0)))
        return pos[k] + (pv - qz(yaw[k]) @ pv), yaw[k]                                 # gira em torno do pivo (centro do corpo)
    fase = cl.get("fase0", 0.0); estado = {}; quadros = []; travada = set(); f_ant = None
    for k, t in enumerate(ts):
        g = cl["marcha"](t); fase += g["f"] * DT; rp, ry = raiz(t)
        if cl.get("primeiros") and f_ant == 0.0 and g["f"] > 0:       # a marcha comeca agora: cada pata decola no instante pedido
            for p_, Ti in cl["primeiros"].items():
                estado[p_]["dph"] = (g["beta"] - fase - g["f"] * max(Ti, DT) - g["off"][p_]) % 1.0; estado[p_]["relaxa"] = True
                estado[p_]["espera"] = (fase + g["off"][p_] + estado[p_]["dph"]) % 1.0 >= g["beta"] + 1e-3   # falta mais que um apoio: espera a volta
        f_ant = g["f"]
        for p_, (tipo, _) in PERNAS.items():
            if cl.get("agenda") is not None:
                agenda_pata(cl, p_, t, rp, ry, estado, raiz); continue
            h = g["h"][0 if tipo == "dian" else 1]; e = estado.get(p_)
            ph = (fase + g["off"][p_] + (e["dph"] if e else 0.0)) % 1.0
            pnt = REP_PATA[p_] if (cl.get("pose_repouso") or (cl.get("parar_em") is not None and t >= cl["parar_em"] and cl.get("parar_repouso"))) else NEUTRO[p_]
            neutro = (lambda rp_, ry_, pnt=pnt: rp_ + qz(ry_) @ pnt)
            if e is None:
                # primeira vez: pata apoiada no ponto coerente com a fase (no apoio: recua de +S*beta/2 a -S*beta/2)
                if g["f"] > 0 and not cl.get("inicio_repouso"):
                    S = cl["vel"](t) / g["f"]; pr = min(ph / g["beta"], 1.0)
                    w = neutro(rp, ry) + qz(ry) @ V((0, -1, 0)) * (S * g["beta"] * (0.5 - pr))
                elif cl.get("inicio_repouso"): w = rp + qz(ry) @ REP_PATA[p_]
                else: w = neutro(rp, ry)
                e = estado[p_] = dict(apoio=True, w=w, yaw=ry, ini=w, alvo=w, yaw_ini=ry, yaw_alvo=ry, u=0.0, prog=0.0, dph=0.0, espera=False,
                                      relaxa=cl["loop"])          # loops: qualquer desvio de fase da pre-rolagem volta ao padrao da marcha
            # maquina de estados por pata: APOIO (parada no mundo) -> BALANCO (duracao em tempo) -> pouso
            if os.environ.get("E5_DEBUG") and e.get("_dph_ant") is not None and abs(e["dph"] - e["_dph_ant"]) > 0.02: print("DPH t=%.2f %s %.3f -> %.3f" % (t, p_, e["_dph_ant"], e["dph"]))
            e["_dph_ant"] = e["dph"]
            if e["apoio"]:
                if e["espera"] and ph < g["beta"]: e["espera"] = False                  # a fase deu a volta depois de um pouso atrasado
                livre = g["f"] > 0 and p_ not in travada
                decola = livre and not e["espera"] and ph >= g["beta"]
                if livre and not decola:                                                # limite de alcance: longe demais atras -> decola ja
                    sh = rp + qz(ry) @ OMBRO[p_]; decola = (e["w"] - sh).dot(qz(ry) @ V((0, 1, 0))) > alcance(g, tipo)[1]
                    if decola and os.environ.get("E5_DEBUG"): print("ALCANCE t=%.2f %s ph %.2f" % (t, p_, ph))
                if decola:
                    Tsw = (1 - g["beta"]) / g["f"]; e.update(apoio=False, t_dec=t, Tsw=Tsw, ini=e["w"].copy(), yaw_ini=e["yaw"])
                    # pouso: ponto neutro na pose prevista da raiz no MEIO do proximo apoio (centra o apoio em translacao e giro)
                    t_l = t + Tsw; gl = cl["marcha"](t_l); t_m = t_l + (gl["beta"] / max(gl["f"], 1e-6)) * 0.5
                    if cl.get("parar_em") is not None and t_l >= cl["parar_em"]: t_m = t_l + 2.0      # vai travar: pouso no ponto final
                    mp, my = raiz(t_m); alvo = neutro(mp, my); lp_, ly_ = raiz(t_l); sh = lp_ + qz(ly_) @ OMBRO[p_]; fw = qz(ly_) @ V((0, -1, 0))
                    frente = (alvo - sh).dot(fw)
                    if frente > alcance(gl, tipo)[0]: alvo = alvo - fw * (frente - alcance(gl, tipo)[0])     # nao pousa alem do alcance
                    e["alvo"] = alvo; e["yaw_alvo"] = my
                else:
                    e["prog"] = (ph / g["beta"] if not e["espera"] else 0.0) if g["f"] > 0 else 0.0; e["u"] = 0.0
                    if e.get("relaxa") and g["f"] > 0 and t > cl.get("relaxa_depois", 1.0 if not cl["loop"] else -99):   # volta devagar ao padrao da marcha (so no apoio)
                        d_ = (e["dph"] + 0.5) % 1.0 - 0.5; e["dph"] = d_ * (1 - DT / 0.5)
            if not e["apoio"]:
                uu = min((t - e["t_dec"]) / e["Tsw"], 1.0)
                if uu >= 1.0 - 1e-6:                                                    # pousou
                    esp = False
                    if g["f"] > 0 and g["beta"] <= ph < 0.85: e["dph"] -= ph               # pouso claramente fora de fase: o apoio comeca agora
                    elif g["f"] > 0 and ph >= 0.85: esp = True                             # pousou um instante antes da virada da fase
                    e.update(apoio=True, w=e["alvo"].copy(), yaw=e["yaw_alvo"], u=0.0, prog=0.0, espera=esp)
                    if cl.get("parar_em") is not None and t >= cl["parar_em"]: travada.add(p_)  # parando: fica apoiada
                else:
                    s_ = suave(uu); w = e["ini"].lerp(e["alvo"], s_); w.z = e["ini"].z + (e["alvo"].z - e["ini"].z) * s_ + h * math.sin(math.pi * uu) ** 0.7
                    e.update(w=w, yaw=e["yaw_ini"] + (e["yaw_alvo"] - e["yaw_ini"]) * s_, u=uu)
        if t >= -1e-9 and len(quadros) < N + 1:
            quadros.append(dict(t=t, raiz=rp.copy(), yaw=ry, fase=fase, corpo=cl["corpo"](t, fase), dmin=(cl.get("dmin_dian", 0.70), cl.get("dmin_tras", 0.76)),
                                pes={p_: dict(w=e["w"].copy(), yaw=e["yaw"], apoio=e["apoio"], u=e["u"], prog=e["prog"], ang=e.get("ang"), rel=e.get("rel"), a_emp=e.get("a_emp"), a_ini=e.get("a_ini") if not e["apoio"] else None,
                                         rq=e.get("rq") if not e["apoio"] else None) for p_, e in estado.items()}))
    DPH_FINAL.clear(); DPH_FINAL.update({p_: e["dph"] for p_, e in estado.items()})
    return quadros
DPH_FINAL = {}
SOLA_LOC = {}
for p_, (tipo, ossos) in PERNAS.items():
    SOLA_LOC[p_] = {b: [] for b in ossos[-2:]}; gi = {ob.vertex_groups[b].index: b for b in ossos[-2:] if b in ob.vertex_groups}
    for v in ob.data.vertices:
        if v.co.z > 0.45: continue
        w_ = [(g.weight, gi[g.group]) for g in v.groups if g.group in gi]
        if w_ and max(w_)[0] > 0.6: SOLA_LOC[p_][max(w_)[1]].append(v.co.copy())
    print("SOLA", p_, {b: len(v) for b, v in SOLA_LOC[p_].items()})
# ------------------------------------------------------------------ pose de um quadro
SOBRA = [0.0]; ERRO_GOLPE = [0.0]   # ERRO_GOLPE: pata de golpe longe do caminho planejado (alcance), studs
def posar(q):
    zerar(); c = q["corpo"]; ry = q["yaw"]; SOBRA[0] = 0.0
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ (q["raiz"] + qz(ry) @ V((c["x"], -c["y"], c["z"])))   # Raiz: sem pai
    PB["Raiz"].rotation_quaternion = rot_local("Raiz", qz(ry))
    PB["Quadril"].rotation_quaternion = rot_local("Quadril", qy(c["roll"]) @ qx(c["pitch"]))
    PB["Coluna1"].rotation_quaternion = rot_local("Coluna1", qz(c["col_yaw"]) @ qx(-c["col_pitch"] * 0.5 + c["col1"]))
    PB["Coluna2"].rotation_quaternion = rot_local("Coluna2", qz(c["col_yaw"]) @ qx(-c["col_pitch"] * 0.5 + c["col2"]))
    PB["Peito"].rotation_quaternion = rot_local("Peito", qy(c["peito_roll"]) @ qx(c["col_pitch"] * 0.4))
    PB["Pescoco1"].rotation_quaternion = rot_local("Pescoco1", qz(c["pesc_yaw"] * 0.6) @ qx(-c["pesc"] * 0.6))
    PB["Pescoco2"].rotation_quaternion = rot_local("Pescoco2", qz(c["pesc_yaw"] * 0.4) @ qx(-c["pesc"] * 0.4))
    upd()
    # cabeca estabilizada: orientacao no mundo = rumo + olhar do clipe
    orientar("Cabeca", qz(ry + c["cab_yaw"] + c["pesc_yaw"]) @ qx(-c["cab_pitch"] - c["pitch"] * 0.3) @ qy(c["cab_roll"]))
    PB["Mandibula"].rotation_quaternion = rot_local("Mandibula", qx(c["mand"]))
    if "Lingua1" in PB:
        PB["Lingua1"].rotation_quaternion = rot_local("Lingua1", qx(c["lingua"])); PB["Lingua2"].rotation_quaternion = rot_local("Lingua2", qx(-c["lingua"] * 0.6))
    for k in ("D", "E"):                                                     # labio superior sobe (rosnado): translacao para cima e um pouco para tras
        if "Labio_" + k in PB: PB["Labio_" + k].location = BD["Labio_" + k].matrix_local.to_3x3().inverted() @ V((0, 0.13 * c["labio"], c["labio"]))
    for k, a in zip(("D", "E"), c["orelha"]):
        PB["Orelha_" + k].rotation_quaternion = rot_local("Orelha_" + k, qx(a))
        PB["Palpebra_" + k].rotation_quaternion = rot_local("Palpebra_" + k, qx(c["palp"]))
    # cauda: postura + onda atrasada (base -> ponta)
    for i, b in enumerate(CAUDA):
        lag = i * 0.11; w = math.sin(2 * math.pi * (c["cauda_f"] * q["t"] - lag)) if c["cauda_f"] else 0.0
        PB[b].rotation_quaternion = rot_local(b, qz(c["cauda_amp"] * w * (0.5 + 0.12 * i) + c["cauda_yaw"]) @ qx(c["cauda_base"] * (1 if i < 3 else -0.6)))
    upd()
    erro = 0.0
    for p_, (tipo, ossos) in PERNAS.items():
        pe = q["pes"][p_]; P = pe["w"]; fy = pe["yaw"]
        lat = qz(fy) @ X
        # metacarpo/metatarso: repouso girado por regra (apoio: estende no fim; balanco: flexiona e volta)
        if pe["apoio"]: a = (pe.get("a_emp") or R(22 if tipo == "dian" else 16)) * suave((pe["prog"] - 0.55) / 0.45)   # sola plana ate ~55% do apoio; depois o calcanhar sobe
        else:
            # positivo = ponta da pata vai para tras (dobra). Dianteira: dobra moderada no inicio do balanco e ja esticada quando a perna
            # vai a frente (a 105 graus e ate u=0,55 a pata virava a sola para cima = "contorcida"); traseira: jarrete flexiona pouco
            u = pe["u"]; dob = R(58 if tipo == "dian" else 35)
            a = (pe.get("a_ini") or R(22 if tipo == "dian" else 16)) * (1 - suave(u / 0.2)) + dob * janela(u, 0.0, 0.72, 0.28, 0.34) + R(-6) * suave((u - 0.6) / 0.4) * (1 - suave((u - 0.95) / 0.05))
        if not pe["apoio"] and pe.get("ang") is not None: a = pe["ang"]
        if tipo == "dian" and not pe["apoio"] and pe.get("rel"):
            ee = posar_golpe(p_, ossos, P, fy, ry, pe["rel"]); ERRO_GOLPE[0] = max(ERRO_GOLPE[0], ee)
            if ee > 0.2 and os.environ.get("E5_DEBUG"): print("GOLPE_ALCANCE t=%.2f %s u %.2f erro %.2f pata-ombro %.2f" % (q["t"], p_, pe["u"], ee, (P - PB[ossos[1]].head).length), "P", [round(x, 2) for x in P], "ombro", [round(x, 2) for x in PB[ossos[1]].head], "raiz", [round(x, 2) for x in q["raiz"]])
            continue
        if tipo == "tras" and not pe["apoio"] and pe.get("rq"):
            # bote: no voo o quadril sobe ~7 studs; o meio do caminho e relativo ao quadril POSADO (pontas no mundo = chao)
            vq = pe["rq"]["via"]; uc = min(max(pe["rq"]["u"], vq[0][0]), vq[-1][0])
            Po = PB[ossos[0]].head + qz(ry) @ (QUAD_PATA[p_] + V(hermite_nu([x[0] for x in vq], [V(x[1]) for x in vq], uc))); P = P.lerp(Po, pe["rq"]["b"])
        meta = (qz(fy) @ (Quaternion(X, a) @ VEC_META[p_]))
        dv = qz(fy) @ VEC_DEDOS[p_]
        if not pe["apoio"]:                                                  # balanco: dedos pendem (dianteira: seguem o metacarpo dobrado;
            dob = janela(pe["u"], 0.05, 0.75, 0.28, 0.3) * (0.55 if tipo == "dian" else 1.0)   # traseira: para a frente e para baixo)
            dsw = (Quaternion(lat, R(0 if tipo == "dian" else -40)) @ meta.normalized()) * VEC_DEDOS[p_].length
            dv = dv.lerp(dsw, dob)
            folga = min((P + dv).z, (P + meta * 0.0).z - 0.45) - (0.35 + (REP_PATA[p_].z - 0.6))
            if folga < 0: P = P + V((0, 0, -folga))                          # dedos nunca abaixo do chao: sobe a pata
        if not pe["apoio"]:
            # no balanco a perna nao fecha alem do anatomico: distancia minima ombro|quadril -> punho|jarrete (senao a canela
            # atravessa a coxa/flanco e o joelho entra na barriga)
            b0 = ossos[1] if tipo == "dian" else ossos[0]; l12 = LEN[ossos[1]] + LEN[ossos[2]] if tipo == "dian" else LEN[ossos[0]] + LEN[ossos[1]]
            if tipo == "dian": PB[ossos[0]].rotation_quaternion = Quaternion(); upd()
            S0 = PB[b0].head.copy(); J0 = P - meta; dmin = q.get("dmin", (0.70, 0.76))[0 if tipo == "dian" else 1] * l12
            if (J0 - S0).length < dmin: P = S0 + (J0 - S0).normalized() * dmin + meta
        for passada in range(5 if pe.get("rq") else 3):                    # bote: passadas extras (metatarso relativo + sola)
            J_ = P - meta                                                   # punho (dianteira) / jarrete (traseira)
            if pe["apoio"] and passada == 0:                                # quanto falta de perna (corpo alto demais para a pata apoiada)
                s0 = PB[ossos[1] if tipo == "dian" else ossos[0]].head; l12 = LEN[ossos[1]] + LEN[ossos[2]] if tipo == "dian" else LEN[ossos[0]] + LEN[ossos[1]]
                SOBRA[0] = max(SOBRA[0], (J_ - s0).length - 0.985 * l12)
            if tipo == "dian":
                esc, um, ant, mao, ded = ossos
                PB[esc].rotation_quaternion = Quaternion(); upd()
                Sr = PB[um].head.copy(); swing = math.atan2(-(J_ - Sr).dot(qz(ry) @ V((0, -1, 0))), -(J_ - Sr).z)
                PB[esc].rotation_quaternion = rot_local(esc, Quaternion(qz(ry) @ X, swing * 0.32)); upd()
                S = PB[um].head.copy(); E, W2 = ik2(S, J_, LEN[um], LEN[ant], qz(ry) @ V((0, 1, 0)) + V((0, 0, 0.15)))
                mirar(um, E); mirar(ant, W2); orientar(mao, qz(fy) @ Quaternion(X, a)); ee = (PB[mao].tail - P).length
            else:
                cx, cn, mt, ded = ossos
                S = PB[cx].head.copy()
                if pe.get("rq"):                                                 # bote: a perna satura macio perto do alcance (sem travar esticada)
                    Lt = LEN[cx] + LEN[cn]; d = (J_ - S).length; d0 = 0.90 * Lt
                    if d > d0: J_ = S + (J_ - S).normalized() * (d0 + 0.08 * Lt * math.tanh((d - d0) / (0.08 * Lt)))
                E, W2 = ik2(S, J_, LEN[cx], LEN[cn], qz(ry) @ V((0, -1, 0)))
                mirar(cx, E); mirar(cn, W2); orientar(mt, qz(fy) @ Quaternion(X, a))
                rq_ = pe.get("rq")
                if rq_ and rq_.get("jarrete") is not None:
                    # bote: metatarso so em flexao/extensao do jarrete em relacao a canela (o angulo no mundo torcia ~40 graus ao recolher),
                    # misturado com a regra do mundo nas pontas do balanco; o metatarso real realimenta o alvo do jarrete
                    q_reg = PB[mt].matrix.to_quaternion(); PB[mt].rotation_quaternion = Quaternion(X, SG_JARRETE[p_] * rq_["jarrete"]); upd()
                    PB[mt].matrix = Matrix.LocRotScale(PB[mt].head.copy(), q_reg.slerp(PB[mt].matrix.to_quaternion(), rq_["k"]), None); upd()
                    novo = PB[mt].tail - PB[mt].head
                    if (novo - meta).length > 0.02 and passada < 3: meta = novo; continue
                ee = (PB[mt].tail - P).length
            if pe["apoio"]: orientar(ded, qz(fy))                           # sola plana, sem rolar
            elif tipo == "tras" and pe.get("rq") and pe["rq"].get("jarrete") is not None:
                # bote: dedos seguem o metatarso com leve curvatura (relativos), misturados com a sola plana nas pontas
                orientar(ded, qz(fy)); q_reg = PB[ded].matrix.to_quaternion(); PB[ded].rotation_quaternion = Quaternion(X, SG_DEDOS[p_] * R(12) * (1 - suave((pe["rq"]["u"] - 0.55) / 0.30))); upd()
                PB[ded].matrix = Matrix.LocRotScale(PB[ded].head.copy(), q_reg.slerp(PB[ded].matrix.to_quaternion(), pe["rq"]["k"]), None); upd()
            else: mirar(ded, P + dv)
            if os.environ.get("E5_DBGT") and abs(q["t"] - float(os.environ["E5_DBGT"])) < 0.017 and p_ == "TE":
                zs_ = min(min((PB[b].matrix @ BD[b].matrix_local.inverted() @ v).z for v in SOLA_LOC[p_][b]) for b in SOLA_LOC[p_] if SOLA_LOC[p_][b])
                print("DBG", p_, "apoio", pe["apoio"], "u %.2f" % pe["u"], "P", [round(x, 2) for x in P], "ded_head", [round(x, 2) for x in PB[ossos[-1]].head], "sola_min %.3f" % zs_, "ee %.3f" % ee)
            if pe["apoio"] or not SOLA_LOC[p_]: break
            # balanco: menor altura da sola real (vertices dos dedos/metacarpo levados pelos ossos) -> sobe a pata se tocar o chao
            zs = min(min((PB[b].matrix @ BD[b].matrix_local.inverted() @ v).z for v in SOLA_LOC[p_][b]) for b in SOLA_LOC[p_] if SOLA_LOC[p_][b])
            if zs >= 0.06: break
            P = P + V((0, 0, 0.06 - zs))
        if pe["apoio"]:
            erro = max(erro, ee)
            if ee > 0.1 and os.environ.get("E5_DEBUG"):
                fw_ = qz(ry) @ V((0, -1, 0)); print("IKERRO t=%.2f %s %.2f prog %.2f frente_do_ombro %.2f alt_ombro %.2f" % (q["t"], p_, ee, pe["prog"], (P - S).dot(fw_), S.z))
    # auxiliares de volume: metade do filho
    for a_, f_ in AUX.items(): PB[a_].rotation_quaternion = Quaternion().slerp(PB[f_].rotation_quaternion, 0.5)
    upd(); return erro
_SOLA_G = {}
def sola_golpe(p_):
    """vertices baixos da pata (z < 0,4 no repouso) com peso somado >= 0,5 em Mao/Dedos/Punho_Aux, cada um pelo osso dominante
    (inclui a almofada do carpo, que o SOLA_LOC nao pega)"""
    if p_ not in _SOLA_G:
        alvo = {"Mao_" + p_, "Dedos_" + p_, "Punho_Aux_" + p_}; gi = {g.index: g.name for g in ob.vertex_groups}; out = []
        for v in ob.data.vertices:
            if v.co.z >= 0.4: continue
            w = [(g.weight, gi[g.group]) for g in v.groups if gi[g.group] in alvo]
            if w and sum(x for x, _ in w) >= 0.5: out.append((max(w)[1], v.co.copy()))
        _SOLA_G[p_] = out
    return _SOLA_G[p_]
def posar_golpe(p_, ossos, P, fy, ry, rl):
    """dianteira no golpe (Patada). Causa da torcao antiga: o metacarpo era orientado por um angulo no MUNDO (orientar), sem levar em
    conta o antebraco; com a pata erguida o punho chegava a ~155 graus de flexao (quase antiparalelo) e a torcao residual trocava de
    lado entre quadros; o polo fixo (para tras) do IK ainda deixava o cotovelo acima da linha ombro-punho. Aqui:
    - o polo do cotovelo e o 'para tras' girado pela flexao do ombro (menor arco de 'para baixo' ate ombro->punho): dobradica estavel;
    - punho e dedos = rotacao local SO em X (flexao/extensao, zero torcao e zero desvio), misturada com a regra do apoio nas pontas;
    - o metacarpo real (cauda - cabeca do osso) realimenta o alvo do punho (3 passadas) para a pata cair no caminho planejado."""
    esc, um, ant, mao, ded = ossos; meta = qz(fy) @ VEC_META[p_]; tras, baixo = qz(ry) @ V((0, 1, 0)), V((0, 0, -1)); ee = 0.0
    Pw = P.copy()
    for _ in range(4):
        if rl.get("via_ombro"):
            # bote: no voo o ombro sobe ~4,8 studs (pitch e coluna) e anda 15; o meio do caminho e dado em relacao ao ombro posado
            # (escapula em repouso) e misturado com o caminho no mundo, que segura a decolagem e o pouso no chao
            PB[esc].rotation_quaternion = Quaternion(); upd(); S0 = PB[um].head.copy(); vo = rl["via_ombro"]
            uc = min(max(rl["u"], vo[0][0]), vo[-1][0]); Po = S0 + qz(ry) @ V(hermite_nu([x[0] for x in vo], [V(x[1]) for x in vo], uc))
            P = Pw.lerp(Po, rl["b_ombro"])
        J_ = P - meta
        PB[esc].rotation_quaternion = Quaternion(); upd()
        Sr = PB[um].head.copy(); swing = math.atan2(-(J_ - Sr).dot(qz(ry) @ V((0, -1, 0))), -(J_ - Sr).z)
        PB[esc].rotation_quaternion = rot_local(esc, Quaternion(qz(ry) @ X, swing * rl["esc"])); upd()
        S = PB[um].head.copy(); u = (J_ - S).normalized(); polo = baixo.rotation_difference(u) @ tras
        if rl["alcance_suave"]:                                              # bote: a perna satura macio perto do alcance (sem "travar" esticada)
            Lt = LEN[um] + LEN[ant]; d = (J_ - S).length; d0 = 0.90 * Lt
            if d > d0: J_ = S + u * (d0 + 0.08 * Lt * math.tanh((d - d0) / (0.08 * Lt)))
        E, W2 = ik2(S, J_, LEN[um], LEN[ant], polo); mirar(um, E); mirar(ant, W2)
        PB[mao].rotation_quaternion = Quaternion(X, SG_PUNHO[p_] * rl["punho"]); upd(); q_rel = PB[mao].matrix.to_quaternion()
        orientar(mao, qz(fy) @ Quaternion(X, rl["a_regra"])); q_reg = PB[mao].matrix.to_quaternion()
        PB[mao].matrix = Matrix.LocRotScale(PB[mao].head.copy(), q_reg.slerp(q_rel, rl["k"]), None); upd()
        meta = PB[mao].tail - PB[mao].head; ee = (PB[mao].tail - P).length
        if rl["alcance_suave"]:                                              # bote: a sola real (com a almofada do carpo) nao entra no chao
            zs = min((PB[b].matrix @ BD[b].matrix_local.inverted() @ v).z for b, v in sola_golpe(p_))
            if zs < 0.04: Pw = Pw + V((0, 0, 0.04 - zs)); P = P + V((0, 0, 0.04 - zs)); continue
        if ee < 0.005: break
    PB[ded].rotation_quaternion = Quaternion(X, SG_DEDOS[p_] * rl["dedos"]); upd(); q_rel = PB[ded].matrix.to_quaternion()
    orientar(ded, qz(fy)); q_reg = PB[ded].matrix.to_quaternion()
    PB[ded].matrix = Matrix.LocRotScale(PB[ded].head.copy(), q_reg.slerp(q_rel, rl["k"]), None); upd()
    return ee
# ------------------------------------------------------------------ secundarios (mola) gravados depois dos principais
def molas(nq):
    K, D_ = (2 * math.pi * 1.5) ** 2, 2 * 0.45 * (2 * math.pi * 1.5)
    est = {b: np.zeros(4) for b in SEC}; ant = {}
    for f in range(1, nq + 1):
        sc.frame_set(f)
        for b in SEC:
            pb = PB[b]; pai = pb.parent.name; q = (arm.matrix_world @ PB[pai].matrix).to_quaternion()
            if b in ant: dq = ant[b].inverted() @ q; ax_, an = dq.to_axis_angle(); om = V(ax_) * an / DT
            else: om = V((0, 0, 0))
            ant[b] = q; st = est[b]; alvo = np.array([-0.05 * om.x, -0.05 * om.z])
            acc = K * (alvo - st[:2]) - D_ * st[2:]; st[2:] += acc * DT; st[:2] += st[2:] * DT; st[:2] = np.clip(st[:2], -0.3, 0.3)
            g = 1.0 if b.endswith(("_1", "Tufo1")) else 1.4
            base = PB["Cauda5" if b == "Tufo1" else "Cauda6"].rotation_quaternion.copy() if b.startswith("Tufo") else Quaternion()
            pb.rotation_quaternion = base @ Quaternion(X, st[0] * g) @ Quaternion(Z, st[1] * g); pb.keyframe_insert("rotation_quaternion", frame=f)
# ------------------------------------------------------------------ QA e render
SOLA = {}
for p_, (tipo, ossos) in PERNAS.items():
    gi = {ob.vertex_groups[n].index for n in ossos[-1:] if n in ob.vertex_groups}   # almofadas dos dedos
    SOLA[p_] = [v.index for v in ob.data.vertices if v.co.z < 0.35 and any(g.group in gi and g.weight > 0.75 for g in v.groups)]
# QA "perna dentro do corpo": vertices da canela/metatarso/antebraco/mao contra a pele do tronco (faces do quadril, coluna e peito)
from mathutils.bvhtree import BVHTree
_GI = {g.index: g.name for g in ob.vertex_groups}
def _dom(v):
    w = sorted(((g.weight, _GI[g.group]) for g in v.groups), reverse=True); return w[0] if w else (0, "")
_DOMV = [_dom(v) for v in ob.data.vertices]
_CASCA = None
PERNA_V, POLIS_P = {}, {}
for i, (w, b) in enumerate(_DOMV):
    if w > 0.7 and b.split("_")[0] in ("Canela", "Metatarso", "Antebraco", "Mao"): PERNA_V.setdefault(b.split("_")[-1], []).append(i)
for pe_ in PERNA_V:   # pele do corpo para esta pata: tudo menos a propria canela/antebraco para baixo (a coxa/flanco/peito ficam)
    proprio = {b for b in (x + "_" + pe_ for x in ("Canela", "Metatarso", "Antebraco", "Mao", "Dedos", "Punho_Aux", "Cotovelo_Aux"))}
    POLIS_P[pe_] = [list(p.vertices) for p in ob.data.polygons if p.material_index == 0 and not any(_DOMV[i][1] in proprio for i in p.vertices)]
def perna_no_corpo(P):
    """maior profundidade (studs) de um vertice da canela/antebraco para baixo dentro da pele do resto do corpo, por pata"""
    out = {}
    for pe_, ids in PERNA_V.items():
        bvh = BVHTree.FromPolygons([tuple(x) for x in P], POLIS_P[pe_]); pior = 0.0
        for i in ids[::2]:
            loc, nrm, fi, dist = bvh.find_nearest(V(P[i]), 2.5)
            if loc is None: continue
            d = (V(P[i]) - loc).dot(nrm)
            if d < -pior: pior = -d
        out[pe_] = round(pior, 3)
    return out
def malha():
    dg = bpy.context.evaluated_depsgraph_get(); m = ob.evaluated_get(dg).to_mesh(); P = np.array([v.co for v in m.vertices]); ob.evaluated_get(dg).to_mesh_clear()
    Mw = np.array(ob.matrix_world); return P @ Mw[:3, :3].T + Mw[:3, 3]
def preparar_cena():
    if "_chao" in bpy.data.objects: return
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); ch = bpy.context.active_object; ch.name = "_chao"
    mc = bpy.data.materials.new("_chao"); mc.use_nodes = True; nt = mc.node_tree; bs = nt.nodes["Principled BSDF"]
    ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 100; ck.inputs["Color1"].default_value = (0.47, 0.43, 0.36, 1); ck.inputs["Color2"].default_value = (0.38, 0.35, 0.29, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["UV"], ck.inputs["Vector"]); nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.95
    ch.data.materials.append(mc)
    w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.64, 0.66, 1)
    sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.6; sol.angle = math.radians(8)
    so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
    sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = False; sc.view_settings.view_transform = "Standard"
    cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 45
def render_clipe(nome, nq, raizes, vistas):
    cam = sc.camera; pasta = os.path.join(OUT, nome); os.makedirs(pasta, exist_ok=True)
    sc.render.resolution_x, sc.render.resolution_y = int(RES * 16 / 9) // 2 * 2, RES; sc.render.image_settings.file_format = "PNG"
    for vista, (az, el, dist, alt_) in vistas.items():
        sel = [int(x) for x in os.environ["E5_QUADROS"].split(",")] if os.environ.get("E5_QUADROS") else range(1, nq + 1)
        for f in sel:
            if f > nq: continue
            sc.frame_set(f); r = raizes[f - 1]; alvo = V((r.x, r.y + 0.5, 7.5 + alt_))
            if vista.startswith("rosto"): alvo = arm.matrix_world @ ((PB["Cabeca"].head + PB["Cabeca"].tail) * 0.5 + V((0, -0.6, -0.9)))   # close que segue a cabeca
            cam.location = alvo + V((-math.sin(R(az)) * math.cos(R(el)), -math.cos(R(az)) * math.cos(R(el)), math.sin(R(el)))) * dist
            cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.join(pasta, "%s_%04d.png" % (vista, f)); bpy.ops.render.render(write_still=True)
def video(pasta, prefixo, nq, saida, fps):
    """PNG -> MP4 pelo editor de video do Blender (sem ffmpeg no sistema)"""
    s2 = bpy.data.scenes.new("_v"); s2.sequence_editor_create(); s2.render.fps = fps; s2.frame_start = 1; s2.frame_end = nq
    st = s2.sequence_editor.strips.new_image("img", os.path.join(pasta, "%s_%04d.png" % (prefixo, 1)), channel=1, frame_start=1)
    for f in range(2, nq + 1): st.elements.append("%s_%04d.png" % (prefixo, f))
    s2.render.resolution_x, s2.render.resolution_y = sc.render.resolution_x, sc.render.resolution_y
    im = s2.render.image_settings
    try: im.media_type = "VIDEO"
    except Exception: pass
    im.file_format = "FFMPEG"; s2.render.ffmpeg.format = "MPEG4"; s2.render.ffmpeg.codec = "H264"; s2.render.ffmpeg.constant_rate_factor = "HIGH"
    s2.render.filepath = saida; bpy.ops.render.render(animation=True, scene=s2.name); bpy.data.scenes.remove(s2)
# ------------------------------------------------------------------ principal
rel = {}
nomes = list(CLIPES) if SO == ["todos"] else SO
for nome in nomes:
    cl = CLIPES[nome]; quadros = simular(cl); nq = len(quadros) - (1 if cl["loop"] else 0)   # loop: o ultimo quadro = primeiro (nao gravado)
    MOD.show_viewport = False
    act = bpy.data.actions.new("Leao_" + nome); act.use_fake_user = True; arm.animation_data_create(); arm.animation_data.action = act   # fake user: todas as acoes ficam no .blend
    # o corpo se apoia nas pernas: onde a pata apoiada nao alcanca, a raiz desce (passada previa, suavizada no tempo)
    lista = quadros[:nq + 1] if cl["loop"] else quadros[:nq]; desce = np.zeros(len(lista))
    for it in range(3):
        for i, q in enumerate(lista):
            q["corpo"]["z"] -= desce[i] if it else 0.0
        extra = np.zeros(len(lista))
        for i, q in enumerate(lista):
            posar(q); extra[i] = max(SOBRA[0], 0.0) * 1.15
        if extra.max() < 0.01: break
        w_ = 4; modo = "wrap" if cl["loop"] else "edge"; base_ = extra[:nq] if cl["loop"] else extra   # loop: suavizacao circular
        pad = np.pad(base_, w_, mode=modo); ex = np.array([pad[i:i + 2 * w_ + 1].max() for i in range(len(base_))])
        ex = np.convolve(np.pad(ex, w_, mode=modo), np.hanning(2 * w_ + 1) / np.hanning(2 * w_ + 1).sum(), mode="valid")
        if cl["loop"]: ex = np.append(ex, ex[0])
        desce = ex; print("APOIO_CORPO", nome, "passada", it, "maior descida %.2f" % ex.max(), np.round(ex, 2).tolist() if os.environ.get("E5_DEBUG") else "")
    erro_max = 0.0; poses = []; ERRO_GOLPE[0] = 0.0
    for q in quadros[:nq + 1] if cl["loop"] else quadros[:nq]:
        erro_max = max(erro_max, posar(q)); poses.append(({pb.name: pb.rotation_quaternion.copy() for pb in PB if pb.name not in SEC}, PB["Raiz"].location.copy(),
                                                          {b: PB[b].location.copy() for b in ("Labio_D", "Labio_E") if b in PB}))
    if cl["loop"]:
        bruta = max((math.degrees(poses[0][0][b].rotation_difference(poses[nq][0][b]).angle), b) for b in poses[0][0] if b != "Raiz")
        print("EMENDA_BRUTA", nome, round(bruta[0], 2), bruta[1], "dph", {p_: round(e_, 3) for p_, e_ in DPH_FINAL.items()})
    if cl["loop"]:   # distribui a diferenca entre o quadro N+1 e o 1 ao longo do ciclo (emenda sem salto)
        for b in poses[0][0]:
            d = poses[0][0][b] @ poses[nq][0][b].inverted()
            for f in range(nq): poses[f][0][b] = Quaternion().slerp(d, f / nq) @ poses[f][0][b]
    for f in range(1, nq + 1):
        rots, loc, locs = poses[f - 1]
        for b, l_ in locs.items(): PB[b].location = l_; PB[b].keyframe_insert("location", frame=f)
        for b, q_ in rots.items(): PB[b].rotation_quaternion = q_; PB[b].keyframe_insert("rotation_quaternion", frame=f)
        PB["Raiz"].location = loc; PB["Raiz"].keyframe_insert("location", frame=f)
    sc.frame_start, sc.frame_end = 1, nq
    molas(nq)
    MOD.show_viewport = True
    # QA: escorregamento das solas em apoio, altura minima, emenda do loop
    esc = {p_: 0.0 for p_ in PERNAS}; zmin = 9.0; ant = None; raizes = []; no_corpo = {p_: 0.0 for p_ in PERNAS}; no_corpo_q = {}
    for f in range(1, nq + 1):
        sc.frame_set(f); P = malha()
        if float(P[:, 2].min()) < zmin: zmin = float(P[:, 2].min()); iv = int(np.argmin(P[:, 2])); zmin_onde = (f, [round(float(x), 2) for x in P[iv]], sorted(((round(g.weight, 2), ob.vertex_groups[g.group].name) for g in ob.data.vertices[iv].groups), reverse=True)[:3], [round(x, 2) for x in ob.data.vertices[iv].co])
        raizes.append(V(quadros[f - 1]["raiz"]))
        if f % 2 == 1:
            for p_, d_ in perna_no_corpo(P).items():
                if d_ > no_corpo[p_]: no_corpo[p_] = d_; no_corpo_q[p_] = f
        if ant is not None:
            for p_ in PERNAS:
                if quadros[f - 1]["pes"][p_]["apoio"] and quadros[f - 2]["pes"][p_]["apoio"] and SOLA[p_]:
                    d = np.linalg.norm((P[SOLA[p_], :2] - ant[SOLA[p_], :2]), axis=1); esc[p_] = max(esc[p_], float(np.percentile(d, 90)))
        ant = P
    emenda = None
    if cl["loop"]:   # salto do ultimo quadro para o primeiro, comparado ao maior salto entre quadros vizinhos dentro do clipe
        pior = (0.0, None, 0.0)
        for b in poses[0][0]:
            qs = [poses[f][0][b] for f in range(nq)]
            dentro = max(math.degrees(qs[f].rotation_difference(qs[f + 1]).angle) for f in range(nq - 1))
            volta = math.degrees(qs[-1].rotation_difference(qs[0]).angle)
            if volta - dentro > pior[0] - pior[2]: pior = (volta, b, dentro)
        emenda = {"osso": pior[1], "salto_volta_graus": round(pior[0], 2), "maior_salto_interno_graus": round(pior[2], 2)}
    contatos = {p_: [f for f in range(2, nq + 1) if quadros[f - 1]["pes"][p_]["apoio"] and not quadros[f - 2]["pes"][p_]["apoio"]] for p_ in PERNAS}
    decol = {p_: [f for f in range(2, nq + 1) if not quadros[f - 1]["pes"][p_]["apoio"] and quadros[f - 2]["pes"][p_]["apoio"]] for p_ in PERNAS}
    desl = quadros[nq - 1]["raiz"] - quadros[0]["raiz"]
    rel[nome] = dict(quadros=nq, fps=FPS, duracao_s=round(nq / FPS, 3), loop=cl["loop"], velocidade_studs_s=round(cl["vel"](0.0), 2),
                     deslocamento_raiz=[round(x, 2) for x in desl], erro_ik_max=round(erro_max, 4), erro_golpe_max=round(ERRO_GOLPE[0], 3), escorregamento_apoio_p90=esc and {k: round(v, 4) for k, v in esc.items()},
                     altura_min_malha=round(zmin, 3), altura_min_onde=zmin_onde, perna_dentro_do_corpo=no_corpo, perna_dentro_quadro=no_corpo_q, emenda_loop_graus=emenda, pousos=contatos, decolagens=decol)
    print("CLIPE", nome, json.dumps(rel[nome]), flush=True)
    if REND:
        preparar_cena()
        vistas = {"perfil": (-90, 5, 50, 0.0), "34": (-40, 13, 52, 0.0)}
        if os.environ.get("E5_VISTAS") == "rosto": vistas = {"rosto_frente": (0, 4, 9, 0.0), "rosto_34": (-40, 8, 10, 0.0)}
        if os.environ.get("E5_VISTAS") == "todas": vistas = {"perfil": (-90, 5, 50, 0.0), "34": (-40, 13, 52, 0.0), "rosto_frente": (0, 4, 9, 0.0), "rosto_34": (-40, 8, 10, 0.0)}
        if os.environ.get("E5_VISTAS") == "esq": vistas = {"esq_perto": (90, 4, 24, -2.0), "dir_perto": (-90, 4, 24, -2.0)}   # revisao das traseiras
        render_clipe(nome, nq, raizes, vistas)
        for vista in ([] if os.environ.get("E5_QUADROS") else vistas):
            pasta = os.path.join(OUT, nome)
            video(pasta, vista, nq, os.path.join(OUT, "%s_%s.mp4" % (nome, vista)), FPS)
            video(pasta, vista, nq, os.path.join(OUT, "%s_%s_lento.mp4" % (nome, vista)), 10)
json.dump(rel, open(os.path.join(OUT, "clipes_%s.json" % "_".join(nomes)[:60]), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Leao_Solar_E5_clipes_%s.blend" % "_".join(nomes)[:60]))
print("CLIPES_OK")
