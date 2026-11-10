"""Clipes do Urso Silvestre v2 (procedurais, NO LUGAR: o jogo move o modelo). Cada quadro define alvos IK das 4 patas
(mundo), rotacoes de coluna/pescoco/cabeca/mandibula/orelhas/cauda e deslocamento da Raiz; o IK resolve as patas e a pose
final de cada osso e gravada em FK (acao 'Urso_<clipe>') e em JSON (mesmo formato dos clipes do Crocodilo, para a ponte
JSON -> KeyframeSequence do Studio).
Peso de urso: plantigrado (sola inteira apoiada), passo em sequencia lateral no andar com rolamento de massa e escapulas
acompanhando a pata; galope rotatorio na corrida com flexao da coluna; antecipacao -> acao -> recuperacao nos ataques.
QA por clipe: erro do IK, escorregao do pe apoiado (2 quadros seguidos em apoio), altura minima da malha (garras/chao).
Velocidades sao PROPOSTA (RPG_02 Etapa 24.2: terra 18 studs/s nao aprovado). Clipes visuais: nao definem mecanicas.
Uso: blender -b CR_Urso_v2_Rig.blend -P anim_urso.py -- <saida_dir> [clipe1,clipe2]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["Urso_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
MALHAS = [bpy.data.objects[n] for n in ("Urso_Cabeca", "Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Boca")]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def onda(t, T, fase=0.0): return math.sin(2 * math.pi * (t / T + fase))
def janela(t, a, b, sub=0.2, des=0.2):
    """0 -> 1 entre a e a+sub, 1 -> 0 entre b-des e b"""
    return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
R = math.radians

# ------------------------------------------------------------------ IK das patas (alvos = Empties no mundo)
PATAS = {"MaoE": ("dian", "AntebracoE", "BracoE"), "MaoD": ("dian", "AntebracoD", "BracoD"),
         "PeE": ("tras", "CanelaE", "CoxaE"), "PeD": ("tras", "CanelaD", "CoxaD")}
ALVO, POLO, REP = {}, {}, {}
for pe, (par, meio, topo) in PATAS.items():
    a_ = bpy.data.objects.new("IK_" + pe, None); sc.collection.objects.link(a_); a_.location = BD[pe].head_local.copy()
    a_.rotation_mode = "QUATERNION"; a_.rotation_quaternion = BD[pe].matrix_local.to_quaternion()
    j = BD[meio].head_local; p_ = bpy.data.objects.new("Polo_" + pe, None); sc.collection.objects.link(p_)
    p_.location = j + V((0, 3.0 if par == "dian" else -3.0, 0))                   # cotovelo para tras, joelho para a frente
    c = PB[meio].constraints.new("IK"); c.target = a_; c.pole_target = p_; c.chain_count = 2; c.use_stretch = False
    cr = PB[pe].constraints.new("COPY_ROTATION"); cr.target = a_                     # sola segue o alvo (fica apoiada)
    ALVO[pe], POLO[pe], REP[pe] = a_, p_, a_.location.copy()
ROT0 = {k: o.rotation_quaternion.copy() for k, o in ALVO.items()}
POLO_REP = {k: o.location.copy() for k, o in POLO.items()}
bpy.context.view_layer.update()
for pe, (par, meio, topo) in PATAS.items():                                         # angulo de polo: joelho/cotovelo no repouso
    c = PB[meio].constraints["IK"]; alvo_j = BD[meio].head_local.copy()
    def erro(a_):
        c.pole_angle = a_; bpy.context.view_layer.update(); return (PB[meio].head - alvo_j).length + (PB[meio].tail - BD[meio].tail_local).length
    melhor = min((erro(R(g)), R(g)) for g in range(-180, 180, 5))[1]
    for passo_ in (2.5, 1.0, 0.25):
        melhor = min((erro(melhor + R(d)), melhor + R(d)) for d in (-passo_, 0, passo_))[1]
    c.pole_angle = melhor; print("POLO", pe, round(math.degrees(melhor), 2), "erro", round(erro(melhor), 4))
def rot_mundo(nome, eixos):
    """rotacao em eixos do MUNDO (X arfagem, Y rolagem, Z guinada) convertida para o espaco local do osso"""
    r = BD[nome].matrix_local.to_3x3(); q = Matrix.Identity(3)
    for eixo, ang in eixos: q = Matrix.Rotation(ang, 3, eixo) @ q
    return (r.inverted() @ q @ r).to_quaternion()
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
def zerar():
    for pb in PB: pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for k, o in ALVO.items(): o.location = REP[k].copy(); o.rotation_quaternion = ROT0[k].copy()
    for k, o in POLO.items(): o.location = POLO_REP[k].copy()
    for pe, (par, meio, topo) in PATAS.items(): PB[meio].constraints["IK"].influence = 1.0; PB[pe].constraints["Copy Rotation"].influence = 1.0
def passo(fase, L, apoio, alt, lado=V((0, 1, 0))):
    """pe no ciclo: apoio = recua de -L/2 a +L/2 ao longo de 'lado' (frente = -Y); balanco sobe e avanca"""
    f = fase % 1.0
    if f < apoio: return lado * (-L / 2 + L * f / apoio), 0.0
    u = (f - apoio) / (1 - apoio); s = suave(u)
    return lado * (L / 2 - L * s) + V((0, 0, alt * math.sin(math.pi * u))), u
FASE_ANDAR = {"PeE": 0.0, "MaoE": 0.25, "PeD": 0.5, "MaoD": 0.75}                      # sequencia lateral
FASE_GALOPE = {"PeE": 0.0, "PeD": 0.12, "MaoD": 0.46, "MaoE": 0.58}                    # galope rotatorio

# ------------------------------------------------------------------ clipes: t -> (rots, raiz, pes, extras)
def base_pose(r, cab=0.0):
    r.setdefault("Mandibula", [(X, 0.0)])
def c_repouso(t):
    T = 4.0; r = {}; b = onda(t, T)
    r["Coluna1"] = [(X, R(0.6) * b)]; r["Coluna2"] = [(X, R(-0.8) * b)]                  # respiracao: torax sobe e desce
    r["Pescoco"] = [(X, R(-1.0) * b)]; r["Cabeca"] = [(X, R(1.2) * b), (Z, R(3) * onda(t, T, 0.3))]
    r["OrelhaE"] = [(X, R(-8) * janela(t, 1.2, 1.6, 0.08, 0.15))]; r["OrelhaD"] = [(X, R(-6) * janela(t, 3.0, 3.4, 0.08, 0.15))]
    r["Cauda1"] = [(Z, R(3) * onda(t, T))]
    return r, V((0, 0, 0.04 * b)), {}, {}
def c_observar(t):
    """olha para a esquerda, fareja (focinho sobe), olha para a direita, volta"""
    r = {}; e = janela(t, 0.3, 2.0, 0.45, 0.4); d = janela(t, 2.3, 4.0, 0.45, 0.45); f = janela(t, 1.0, 1.7, 0.15, 0.15)
    guin = R(38) * e - R(34) * d
    r["Pescoco"] = [(Z, guin * 0.45), (X, R(-6) * (e + d))]; r["Pescoco2"] = [(Z, guin * 0.35)]
    r["Cabeca"] = [(Z, guin * 0.2), (X, R(-10) * f + R(1.5) * math.sin(2 * math.pi * t * 4) * f)]
    r["Coluna3"] = [(Z, guin * 0.12)]
    r["OrelhaE"] = [(Z, R(18) * e)]; r["OrelhaD"] = [(Z, R(-18) * d)]
    r["Mandibula"] = [(X, R(3) * f)]
    return r, V((0, 0, 0.03 * onda(t, 2.2))), {}, {}
# ------------------------------------------------------------------ REVISAO 03/11: locomocao com apoio amarrado ao deslocamento
# Medido na linha de base: (1) a sola andava no apoio por peso do antebraco (corrigido no rig); (2) Virar deslizava as patas
# no sentido contrario e sem relacao com o raio; (3) Sentar/Deitar/Frenagem/Arrancada arrastavam as patas; (4) Arrancada e
# Frenagem nao encaixavam na fase da Corrida; (5) galope esticava a pata dianteira ate a singularidade do IK.
# Agora: pe apoiado = posicao de pouso + deslocamento INTEGRADO do corpo (S(t) = integral de v), entao fica parado no mundo
# mesmo com velocidade variavel; balanco = arco ate o proximo pouso. v(t) e o giro sao PARAMETROS TECNICOS (nao regras).
BASE_Z = -0.30                                              # altura comum dos clipes em pe (pernas levemente dobradas)
PIVO = BD["Raiz"].head_local.copy()                         # pivo de giro/deslocamento do modelo (Raiz)
T_GAL, L_GAL, AP_GAL = 14 / 30, 2.9, 0.37                   # galope: passada menor (sem esticar a dianteira) e cadencia maior
T_AND, L_AND, AP_AND = 1.2, 2.4, 0.62
GIRO = math.radians(60)                                     # virar: 60 graus/s (parametro tecnico desta revisao)
ALT_UL = {}
class Perfil:
    """v(t) e S(t) = integral de v, amostrados finos (tambem antes de 0 e depois do fim, por extrapolacao)"""
    def __init__(self, vfun, t0=-3.0, t1=6.0, dt=1 / 600):
        self.t0, self.dt = t0, dt; n = int((t1 - t0) / dt) + 1; acc = 0.0; self.S = []
        for i in range(n): self.S.append(acc); acc += vfun(t0 + i * dt) * dt
    def s(self, t):
        x = (t - self.t0) / self.dt; i = max(0, min(len(self.S) - 2, int(x))); return self.S[i] + (self.S[i + 1] - self.S[i]) * (x - i)
class PerfDesloc:
    """perfil com tempo deslocado (o galope da arrancada comeca depois do agachamento)"""
    def __init__(self, p, d): self.p, self.d = p, d
    def s(self, t): return self.p.s(t + self.d)
def passo_var(t, fase, T, apoio, alt, Lf, perf, eixo=V((0, 1, 0))):
    """pe ao longo de 'eixo' (corpo): apoio = pouso + S(t) - S(t_pouso); balanco = smoothstep ate o proximo pouso"""
    ALT_UL['_ultimo'] = alt
    phi = t / T + fase; n_ = math.floor(phi); f = phi - n_; tc = (n_ - fase) * T
    if f < apoio:
        return eixo * (-Lf(tc) / 2 + perf.s(t) - perf.s(tc)), 0.0
    tl = tc + apoio * T; y0 = -Lf(tc) / 2 + perf.s(tl) - perf.s(tc); y1 = -Lf(tc + T) / 2
    u = (f - apoio) / (1 - apoio); s = suave(u)
    mundo_ = abs((y1 - y0) - (perf.s(tc + T) - perf.s(tl)))                     # quanto a pata anda NO MUNDO neste balanco
    alt = max(alt, 0.25 * min(1.0, mundo_ / 0.3))                              # REVISAO: pata que se move (no mundo) sempre sai do chao
    ALT_UL['_ultimo'] = alt
    return eixo * (y0 + (y1 - y0) * s) + V((0, 0, alt * math.sin(math.pi * u))), u
def corpo_andar(r, u, fases, ginga, k=1.0):
    sw = math.sin(2 * math.pi * u)
    r["Pelve"] = [(Y, R(ginga) * sw * k), (Z, R(ginga * 0.6) * sw * k)]
    r["Coluna2"] = [(Y, R(-ginga * 0.8) * sw * k), (Z, R(-ginga * 0.5) * sw * k)]
    r["Coluna3"] = [(Y, R(ginga * 0.6) * math.sin(2 * math.pi * (u + 0.25)) * k)]
    r["Pescoco"] = [(Z, R(-ginga * 0.5) * sw * k), (X, R(2.5) * math.cos(4 * math.pi * u) * k)]
    r["Cabeca"] = [(X, R(-2.5) * math.cos(4 * math.pi * u) * k)]
    for p_ in ("MaoE", "MaoD"):
        r["Escapula" + p_[-1]] = [(X, R(6) * math.cos(2 * math.pi * ((u + fases[p_]) % 1.0)) * k)]
    r["Cauda1"] = [(Z, R(5) * sw * k)]
    return sw
def corpo_galope(r, u, fases, flex):
    fl = math.sin(2 * math.pi * (u - 0.15))
    r["Pelve"] = [(X, R(flex) * fl)]; r["Coluna1"] = [(X, R(-flex * 0.6) * fl)]; r["Coluna2"] = [(X, R(-flex * 0.5) * fl)]
    r["Coluna3"] = [(X, R(flex * 0.3) * fl)]; r["Pescoco"] = [(X, R(flex * 0.5) * fl)]; r["Cabeca"] = [(X, R(flex * 0.25) * fl)]
    for p_ in ("MaoE", "MaoD"): r["Escapula" + p_[-1]] = [(X, R(10) * math.cos(2 * math.pi * ((u + fases[p_]) % 1.0)) * flex / 9)]
    r["OrelhaE"] = [(X, R(-20) * flex / 9)]; r["OrelhaD"] = [(X, R(-20) * flex / 9)]
def rot_sola(ext, k_, u):
    """sola rola no balanco, limitada pela altura do balanco (dedos nao riscam o chao em passos baixos)"""
    alt = ALT_UL.get(k_, 0.48); lim = math.asin(min(0.9, 0.85 * alt / 1.3))
    ext["rot_pe"][k_] = -min(R(25), lim) * math.sin(math.pi * u) if u > 0 else 0.0
V_AND = L_AND / (AP_AND * T_AND); V_GAL = L_GAL / (AP_GAL * T_GAL)
PERF_AND = Perfil(lambda t: V_AND); PERF_GAL = Perfil(lambda t: V_GAL)
def c_andar(t):
    r = {}; pes = {}; ext = {"rot_pe": {}}; u = t / T_AND
    for k_, fase in FASE_ANDAR.items():
        pes[k_], uu = passo_var(t, fase, T_AND, AP_AND, 0.48, lambda tt: L_AND, PERF_AND); ALT_UL[k_] = ALT_UL.get('_ultimo', 0.48); rot_sola(ext, k_, uu)
    sw = corpo_andar(r, u, FASE_ANDAR, 3.0)
    return r, V((0.10 * sw, 0, BASE_Z - 0.06 + 0.05 * math.cos(4 * math.pi * u))), pes, ext
def c_corrida(t):
    r = {}; pes = {}; ext = {"rot_pe": {}}; u = t / T_GAL
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(t, fase, T_GAL, AP_GAL, 0.70, lambda tt: L_GAL, PERF_GAL); ALT_UL[k_] = ALT_UL.get('_ultimo', 0.48); rot_sola(ext, k_, uu)
    corpo_galope(r, u, FASE_GALOPE, 9); r["Cauda1"] = [(Z, R(4) * math.sin(2 * math.pi * u))]
    return r, V((0, 0, -0.65 + 0.20 * math.sin(2 * math.pi * (u - 0.05)))), pes, ext
# arrancada: agacha 11 quadros, depois 3 ciclos de galope crescendo; o ultimo quadro = quadro 0 da Corrida (fase inteira)
T0_ARR = 11 / 30; DUR_ARR = T0_ARR + 3 * T_GAL
def k_arr(t): return suave((t - T0_ARR) / (2 * T_GAL))
PERF_ARR = Perfil(lambda t: V_GAL * k_arr(t)); PERF_ARR_G = PerfDesloc(PERF_ARR, T0_ARR)
def c_arrancada(t):
    r = {}; pes = {}; ext = {"rot_pe": {}}; k = k_arr(t); ag = janela(t, 0.0, T0_ARR + 0.10, 0.22, 0.16)
    tt = t - T0_ARR
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(tt, fase, T_GAL, AP_GAL, 0.70 * k, lambda x: L_GAL * k_arr(x + T0_ARR), PERF_ARR_G)
        ALT_UL[k_] = ALT_UL.get('_ultimo', 0.48); rot_sola(ext, k_, uu if k > 0.02 else 0.0)
    corpo_galope(r, tt / T_GAL, FASE_GALOPE, 9 * k)
    r["Pelve"] = r["Pelve"] + [(X, R(6) * ag)]; r["Pescoco"] = r["Pescoco"] + [(X, R(8) * ag)]
    z = BASE_Z + (-0.65 - BASE_Z) * k + 0.20 * k * math.sin(2 * math.pi * (tt / T_GAL - 0.05)) - 0.25 * ag
    return r, V((0, 0.20 * ag, z)), pes, ext
# frenagem: comeca no quadro 0 da Corrida e a passada encolhe ate parar; o peso senta nas traseiras e volta ao repouso
DUR_FRE = 1.5
def k_fre(t): return 1 - suave(t / 0.95)
PERF_FRE = Perfil(lambda t: V_GAL * k_fre(t))
def c_frenagem(t):
    r = {}; pes = {}; ext = {"rot_pe": {}}; k = k_fre(t); s = janela(t, 0.35, DUR_FRE, 0.25, 0.55)
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(t, fase, T_GAL, AP_GAL, 0.70 * max(k, 0.0) ** 0.7, lambda x: L_GAL * k_fre(x), PERF_FRE)
        ALT_UL[k_] = ALT_UL.get('_ultimo', 0.48); rot_sola(ext, k_, uu if k > 0.02 else 0.0)
    corpo_galope(r, t / T_GAL, FASE_GALOPE, 9 * k)
    r["Pelve"] = r["Pelve"] + [(X, R(-7) * s)]; r["Coluna2"] = r.get("Coluna2", []) + [(X, R(4) * s)]
    r["Pescoco"] = r["Pescoco"] + [(X, R(-8) * s)]; r["Cabeca"] = r["Cabeca"] + [(X, R(-5) * s)]
    z = BASE_Z + (-0.65 - BASE_Z) * k + 0.20 * k * math.sin(2 * math.pi * (t / T_GAL - 0.05)) - 0.30 * s
    return r, V((0, 0.35 * s, z)), pes, ext
def c_virar(sinal):
    """virar no lugar: o jogo gira o modelo a sinal * GIRO em torno da Raiz (sinal +1 = esquerda, anti-horario).
    Pe apoiado = ponto fixo no mundo visto do corpo: gira -omega em torno do pivo (ARCO, nao corda). Balanco: do ponto de
    saida ao proximo pouso, com arco de altura."""
    w = GIRO * sinal; T = T_AND; ap = AP_AND
    def girado(k_, ang):
        rr = REP[k_] - PIVO; c_, s_ = math.cos(ang), math.sin(ang)
        return V((PIVO.x + rr.x * c_ - rr.y * s_, PIVO.y + rr.x * s_ + rr.y * c_, REP[k_].z)) - REP[k_]
    def f(t):
        r = {}; pes = {}; ext = {"rot_pe": {}}; u = t / T; meia = w * ap * T / 2
        for k_, fase in FASE_ANDAR.items():
            phi = t / T + fase; n_ = math.floor(phi); fr = phi - n_; tc = (n_ - fase) * T; tm = tc + ap * T / 2
            if fr < ap:
                pes[k_] = girado(k_, -w * (t - tm)); uu = 0.0; ext.setdefault("giro_pe", {})[k_] = -w * (t - tm)
            else:
                uu = (fr - ap) / (1 - ap); p0, p1 = girado(k_, -meia), girado(k_, meia)
                ext.setdefault("giro_pe", {})[k_] = -meia + 2 * meia * suave(uu)               # no balanco volta a orientacao de pouso
                pes[k_] = p0.lerp(p1, suave(uu)) + V((0, 0, max(0.30, 0.25 * min(1.0, (p1 - p0).length / 0.3)) * math.sin(math.pi * uu)))
            ALT_UL[k_] = 0.30; rot_sola(ext, k_, uu)
        sw = corpo_andar(r, u, FASE_ANDAR, 2.0)
        r["Pescoco"] = r.get("Pescoco", []) + [(Z, R(14) * sinal)]; r["Cabeca"] = r.get("Cabeca", []) + [(Z, R(8) * sinal)]
        r["Coluna2"] = r.get("Coluna2", []) + [(Z, R(6) * sinal)]; r["Pelve"] = r.get("Pelve", []) + [(Z, R(-5) * sinal)]
        return r, V((0.05 * sw, 0, BASE_Z - 0.04 + 0.03 * math.cos(4 * math.pi * u))), pes, ext
    return f
def degrau(t, a, b, alt=0.35):
    """passo de reposicionamento: 0 -> 1 entre a e b com arco de altura alt (a pata sai do chao, nao arrasta)"""
    x = max(0.0, min(1.0, (t - a) / (b - a))); return suave(x), alt * math.sin(math.pi * x)
# 04/11 (pedido do usuario: "mais sentado no chao"): garupa e coxas apoiadas, tronco mais ereto, traseiras dao um
# passo a frente (as coxas deitam), dianteiras recuam para baixo do peito. Valores ajustaveis por SENTADO_TESTE (json).
# Antes (ate 04/11): raiz=(0, 0.9, -1.78), pelve=-24, col1=5, col2=9, col3=0, recuo=1.3, sem passo atras, cauda=-25,
# passos das dianteiras em 0.10-0.50 / 0.40-0.80 (garupa 0.09 acima do chao, coxa 1.41, tronco 35 graus).
# 04/11 r1: raiz z -2.48, pelve -43, coluna 13/15/7, calcanhar levantado (garupa so encostava; "encoste mais a bunda").
# r2: garupa mais baixa (-0.16), pelve menos girada (a traseira desce), pe traseiro quase plano (fecha o vao sob a
# garupa sem afundar a sola) e cauda menos dobrada (nao entra no chao).
SENTADO = dict(raiz=(0.0, 1.4, -2.64), pelve=-40.0, col1=12.0, col2=14.0, col3=7.0, pesc=10.0, cab=4.0,
               recuo=1.6, passo_tras=0.9, calc_z=0.16, calc_ang=-4.0, cauda=-15.0,
               passoE=(0.38, 0.72), passoD=(0.62, 0.94))   # dianteiras recuam depois que o corpo ja desceu (IK sem erro)
if os.environ.get("SENTADO_TESTE"): SENTADO.update(json.loads(os.environ["SENTADO_TESTE"]))
DUR_SEN = 1.4
def pose_sentado(t, k, r, pes):
    S = SENTADO
    r["Pelve"] = [(X, R(S["pelve"]) * k)]; r["Coluna1"] = [(X, R(S["col1"]) * k)]; r["Coluna2"] = [(X, R(S["col2"]) * k)]
    if S["col3"]: r["Coluna3"] = [(X, R(S["col3"]) * k)]
    r["Pescoco"] = [(X, R(S["pesc"]) * k)]; r["Cabeca"] = [(X, R(S["cab"]) * k)]
    for p_, (a, b), sx in (("MaoE", S.get("passoE", (0.10, 0.50)), 1), ("MaoD", S.get("passoD", (0.40, 0.80)), -1)):   # dianteiras recuam (passo)
        s, h = degrau(t, a, b, 0.32); pes[p_] = V((0.1 * sx, S["recuo"], 0)) * s + V((0, 0, h))
    hz = CALC_Z if S["calc_z"] is None else S["calc_z"]; ang = CALC_ANG if S["calc_ang"] is None else S["calc_ang"]
    for p_, (a, b) in (("PeE", (0.30, 0.70)), ("PeD", (0.50, 0.90))):              # traseiras: passo a frente (coxas deitam)
        s, h = degrau(t, a, b, 0.30) if S["passo_tras"] else (0.0, 0.0)
        pes[p_] = V((0, -S["passo_tras"] * s, hz * k + h)); EXT_POSTURA.setdefault("rot_pe", {})[p_] = R(ang) * k
    return V(S["raiz"]) * k
EXT_POSTURA = {}
CALC_Z, CALC_ANG = 0.22, -12.0                         # calcanhar sobe 0,22 e o pe gira 12 graus (dedos apoiados); testado 0,15/-20 a 0,30/+30
def c_sentar(t):
    r = {}; pes = {}; k = suave((t - 0.30) / (DUR_SEN - 0.30)); EXT_POSTURA.clear()
    raiz = pose_sentado(t, k, r, pes); r["Cauda1"] = [(X, R(SENTADO["cauda"]) * k)]
    return r, raiz + V((0, 0, 0.10 * math.sin(math.pi * k))), pes, {"rot_pe": dict(EXT_POSTURA.get("rot_pe", {}))}
def c_levantar_sentado(t):
    return c_sentar(DUR_SEN - t)
DEITADO_Z = -2.3                                     # recalibrado antes de amostrar (ver calibrar_deitado)
DUR_DEI = 2.0
def pose_deitado(t, k, r, pes, ext):
    r["Pelve"] = [(X, R(-3) * k)]; r["Coluna3"] = [(X, R(-4) * k)]; r["Pescoco"] = [(X, R(-10) * k)]; r["Cabeca"] = [(X, R(14) * k)]
    for p_, (a, b), sx in (("MaoE", (0.05, 0.50), 1), ("MaoD", (0.35, 0.80), -1)):   # bracos vao a frente em passos
        s, h = degrau(t, a, b, 0.40); pes[p_] = V((0.15 * sx, -2.2, 0)) * s + V((0, 0, h))
    ext["rot_pe"] = {"PeE": R(CALC_ANG) * k, "PeD": R(CALC_ANG) * k}                 # REVISAO: calcanhar sobe, dedos apoiados
    for p_ in ("PeE", "PeD"): pes[p_] = V((0, 0, CALC_Z * k))
    ext["polo"] = {"MaoE": V((3.5, 1.0, 0)) * k, "MaoD": V((-3.5, 1.0, 0)) * k, "PeE": V((2.5, 0, 0)) * k, "PeD": V((-2.5, 0, 0)) * k}
    return V((0, 0.3 * k, DEITADO_Z * k))
def c_deitar(t):
    r = {}; pes = {}; ext = {}; k = suave((t - 0.55) / (DUR_DEI - 0.55)); raiz = pose_deitado(t, k, r, pes, ext)
    return r, raiz, pes, ext
def c_levantar_deitado(t):
    return c_deitar(DUR_DEI - t)
def c_comer(t):
    """cabeca ao chao, mastiga (mandibula abre/fecha), puxa com a cabeca; pata dianteira esquerda segura o alimento"""
    T = 2.4; r = {}; pes = {}; d = 1.0                      # loop ja com a cabeca baixa (a descida e a mistura do jogo)
    mast = 0.5 + 0.5 * math.sin(2 * math.pi * t * 2.5)
    r["Coluna3"] = [(X, R(6) * d)]; r["Pescoco"] = [(X, R(30) * d)]; r["Pescoco2"] = [(X, R(18) * d)]
    r["Cabeca"] = [(X, R(12) * d + R(4) * math.sin(2 * math.pi * t / 1.2)), (Z, R(5) * math.sin(2 * math.pi * t / 2.4))]
    r["Mandibula"] = [(X, R(16) * mast * d)]
    pes["MaoE"] = V((0, -0.6 * d, 0)); r["OrelhaE"] = [(X, R(-10) * mast)]; r["OrelhaD"] = [(X, R(-10) * mast)]
    return r, V((0, 0.15 * d, -0.25 * d)), pes, {}
def c_rugir(t):
    """antecipacao (inspira, abaixa) -> ergue a cabeca e abre a boca ao maximo -> sustenta com tremor -> fecha"""
    r = {}; a = janela(t, 0.0, 0.45, 0.35, 0.1); k = janela(t, 0.35, 2.3, 0.3, 0.5); tre = R(1.2) * math.sin(2 * math.pi * t * 11) * k
    r["Coluna2"] = [(X, R(3) * a - R(2) * k)]; r["Coluna3"] = [(X, R(-3) * k)]
    r["Pescoco"] = [(X, R(8) * a - R(24) * k + tre)]; r["Pescoco2"] = [(X, R(-12) * k)]; r["Cabeca"] = [(X, R(-12) * k + tre)]
    r["Mandibula"] = [(X, R(38) * k + R(2) * a + tre * 2)]
    r["OrelhaE"] = [(X, R(-22) * k)]; r["OrelhaD"] = [(X, R(-22) * k)]
    return r, V((0, 0.1 * a - 0.05 * k, -0.15 * a - 0.22 * k)), {}, {}
def c_ameaca(t):
    """ergue-se nas patas traseiras rugindo, segura e volta ao apoio (cai pesado nas dianteiras)"""
    r = {}; pes = {}; ext = {"ik": {}}
    sobe = suave((t - 0.25) / 0.65); desce = suave((t - 2.0) / 0.55); k = sobe * (1 - desce)
    ant = janela(t, 0.0, 0.75, 0.30, 0.45)                                    # antecipacao longa e suave (pernas quase retas amplificam)
    r["Pelve"] = [(X, R(-52) * k + R(3) * ant)]
    for l_ in "ED":                                                            # traseiras: compensa a pelve (fica de pe)
        r["Coxa" + l_] = [(X, R(52) * k)]
    ext["alvo_fk"] = {}
    for l_, s_ in (("E", 1), ("D", 0.85)):                                     # dianteiras sobem soltas: o alvo do IK segue a pata (FK)
        ext["alvo_fk"]["Mao" + l_] = suave((k - 0.05) / 0.20) if t < 1.5 else suave(k / 0.05)   # REVISAO: decola so depois do corpo subir (sem arrastar); pousa travando no toque
        kb = k * k                                                              # REVISAO: bracos voltam ao repouso antes do toque (pouso sem deslizar)
        r["Braco" + l_] = [(X, R(35 * s_) * kb), (Y, R(-12 if l_ == "E" else 12) * kb)]
        r["Antebraco" + l_] = [(X, R(-55 * s_) * kb)]; r["Mao" + l_] = [(X, R(-25) * kb)]
    ro = janela(t, 0.7, 2.0, 0.25, 0.3)
    r["Pescoco"] = [(X, R(22) * k - R(14) * ro)]; r["Cabeca"] = [(X, R(12) * k - R(10) * ro)]
    r["Mandibula"] = [(X, R(36) * ro + R(1.5) * math.sin(2 * math.pi * t * 10) * ro)]
    r["OrelhaE"] = [(X, R(-22) * ro)]; r["OrelhaD"] = [(X, R(-22) * ro)]
    impacto = janela(t, 2.5, 2.9, 0.06, 0.3)                                   # peso cai nas dianteiras
    return r, V((0, 0, -0.30 * impacto - 0.12 * ant)), pes, ext
def c_golpe_pata(t):
    """antecipacao (peso para a direita, pata esquerda recua e sobe) -> golpe em arco para a frente/dentro -> recuperacao"""
    r = {}; pes = {}; ant = janela(t, 0.0, 0.55, 0.35, 0.15); gol = janela(t, 0.40, 0.75, 0.12, 0.15); rec = suave((t - 0.75) / 0.45)
    lev = suave(t / 0.35) * (1 - rec)
    arco = suave((t - 0.40) / 0.18)
    pes["MaoE"] = (V((0.5, 0.6, 2.4)) * (1 - arco) + V((-0.9, -2.0, 0.9)) * arco) * lev
    r["Pelve"] = [(Y, R(-6) * lev)]; r["Coluna2"] = [(Z, R(10) * ant - R(14) * gol), (Y, R(-8) * lev)]
    r["Coluna3"] = [(Z, R(8) * ant - R(12) * gol)]; r["Pescoco"] = [(Z, R(-8) * gol), (X, R(-6) * ant)]
    r["Mandibula"] = [(X, R(14) * gol)]; r["OrelhaE"] = [(X, R(-30) * lev)]; r["OrelhaD"] = [(X, R(-30) * lev)]
    return r, V((-0.35 * lev, 0.15 * ant - 0.25 * gol, -0.1 * lev)), pes, {"rot_pe": {"MaoE": R(-40) * lev}}
def c_mordida(t):
    """recolhe e abre a boca -> bote com a cabeca e estalo da mandibula -> recuperacao"""
    r = {}; a = suave(t / 0.30); b = suave((t - 0.30) / 0.12); c = suave((t - 0.55) / 0.45)
    boca = R(34) * a * (1 - b) + R(-0.0) * b
    r["Mandibula"] = [(X, boca)]
    r["Pescoco"] = [(X, R(-10) * a * (1 - b) + R(10) * b * (1 - c))]; r["Cabeca"] = [(X, R(-8) * a * (1 - b) + R(6) * b * (1 - c))]
    r["Coluna3"] = [(X, R(4) * b * (1 - c))]
    r["OrelhaE"] = [(X, R(-30) * a * (1 - c))]; r["OrelhaD"] = [(X, R(-30) * a * (1 - c))]
    return r, V((0, 0.35 * a * (1 - b) - 0.6 * b * (1 - c), -0.15 * b * (1 - c))), {}, {}
def c_reacao(t):
    """impacto pela frente-esquerda: cabeca e tronco recuam e torcem, orelhas baixam, recupera com assentada"""
    r = {}; i = suave(t / 0.08) * (1 - suave((t - 0.12) / 0.55)); rec = janela(t, 0.25, 0.9, 0.2, 0.3)
    r["Pescoco"] = [(Z, R(-18) * i), (X, R(-10) * i)]; r["Cabeca"] = [(Z, R(-12) * i), (Y, R(8) * i)]
    r["Coluna2"] = [(Z, R(-6) * i), (Y, R(5) * i)]; r["Coluna3"] = [(Z, R(-6) * i)]
    r["OrelhaE"] = [(X, R(-35) * i)]; r["OrelhaD"] = [(X, R(-35) * i)]; r["Mandibula"] = [(X, R(10) * i)]
    return r, V((-0.15 * i, 0.30 * i, -0.22 * i - 0.18 * rec)), {}, {}
CLIPES = {  # nome: (funcao, duracao s, loop, velocidade de simulacao [PARAMETRO TECNICO], perfil v(t) p/ QA ou None)
    "Repouso": (c_repouso, 4.0, True, 0.0, None),
    "Observar": (c_observar, 4.4, False, 0.0, None),
    "Andar": (c_andar, T_AND, True, V_AND, None),
    "Corrida": (c_corrida, T_GAL, True, V_GAL, None),
    "Arrancada": (c_arrancada, DUR_ARR, False, 0.0, lambda t: V_GAL * k_arr(t)),
    "Frenagem": (c_frenagem, DUR_FRE, False, 0.0, lambda t: V_GAL * k_fre(t)),
    "VirarE": (c_virar(1), T_AND, True, 0.0, None),
    "VirarD": (c_virar(-1), T_AND, True, 0.0, None),
    "Sentar": (c_sentar, DUR_SEN, False, 0.0, None),
    "LevantarSentado": (c_levantar_sentado, DUR_SEN, False, 0.0, None),
    "Deitar": (c_deitar, DUR_DEI, False, 0.0, None),
    "LevantarDeitado": (c_levantar_deitado, DUR_DEI, False, 0.0, None),
    "Comer": (c_comer, 2.4, True, 0.0, None),
    "Rugir": (c_rugir, 2.4, False, 0.0, None),
    "Ameaca": (c_ameaca, 3.2, False, 0.0, None),
    "GolpePata": (c_golpe_pata, 1.3, False, 0.0, None),
    "Mordida": (c_mordida, 1.0, False, 0.0, None),
    "ReacaoImpacto": (c_reacao, 1.0, False, 0.0, None),
}
COM_ALTURA_PROPRIA = {"Andar", "Corrida", "Arrancada", "Frenagem", "VirarE", "VirarD"}      # os demais recebem BASE_Z
GIRO_SIM = {"VirarE": 60.0, "VirarD": -60.0}
# poderes (04/11): clipes PROPRIOS dos poderes ficam em poderes/clipes_poderes.py e so entram com URSO_PODERES=1
# (os 18 clipes aprovados e a execucao padrao nao mudam). EVENTOS_CLIPE: instantes marcados (ex.: impacto no chao).
EVENTOS_CLIPE = {}
if os.environ.get("URSO_PODERES"):
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "poderes", "clipes_poderes.py"), encoding="utf-8").read(), globals())
if os.environ.get("URSO_MONTARIA"):                    # montaria (09/11): clipes Montar_E/D e Desmontar_E/D (montaria/clipes_montaria.py)
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "montaria", "clipes_montaria.py"), encoding="utf-8").read(), globals())
QUAIS = ARGS[1].split(",") if len(ARGS) > 1 else list(CLIPES)

# ------------------------------------------------------------------ amostragem -> FK -> acao + JSON + QA
def malha_zmin():
    dg = bpy.context.evaluated_depsgraph_get(); zm = 9.0
    for o in MALHAS:
        ev = o.evaluated_get(dg); m = ev.to_mesh(); c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c)
        zm = min(zm, float(c.reshape(-1, 3)[:, 2].min()) + o.matrix_world.translation.z); ev.to_mesh_clear()
    return zm
REG_IDX = {}
for o in MALHAS[:3]:                                                       # regioes por osso dominante: patas, membros, tronco
    nomes = {g.index: g.name for g in o.vertex_groups}; pat, mem, tro = [], [], []
    for v in o.data.vertices:
        if not v.groups: continue
        nm = nomes[max(v.groups, key=lambda g: g.weight).group]
        if nm.startswith("Pelo") and nm in BD: nm = BD[nm].parent.name      # rig com pelo ao vento (04/11): regiao do pai
        if nm.startswith(("Mao", "Dedos")) or (nm.startswith("Pe") and not nm.startswith(("Pelve", "Pescoco"))): pat.append(v.index)
        elif nm.startswith(("Braco", "Antebraco", "Coxa", "Canela")): mem.append(v.index)
        else: tro.append(v.index)
    REG_IDX[o.name] = {k: np.array(v_, dtype=np.int64) for k, v_ in (("pata", pat), ("membro", mem), ("tronco", tro))}
def regioes_zmin():
    dg = bpy.context.evaluated_depsgraph_get(); zm = {"pata": 9.0, "membro": 9.0, "tronco": 9.0}
    for o in MALHAS[:3]:
        ev = o.evaluated_get(dg); m = ev.to_mesh(); c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); c = c.reshape(-1, 3)
        for k, idx in REG_IDX[o.name].items():
            if len(idx): zm[k] = min(zm[k], float(c[idx, 2].min()))
        ev.to_mesh_clear()
    return zm
def tronco_zmin(): return min(regioes_zmin().values())
def calibrar_deitado():
    """acha a descida da Raiz em que a parte mais baixa da malha toca o chao (z = 0) na pose deitada final"""
    global DEITADO_Z
    lo_, hi_ = -4.5, -0.3
    for _ in range(14):
        m_ = (lo_ + hi_) / 2; DEITADO_Z = m_; zerar(); rots, raiz, pes, ext = c_deitar(DUR_DEI)
        PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ (raiz + V((0, 0, BASE_Z)))
        for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
        for k, d in pes.items(): ALVO[k].location = REP[k] + d
        for k, a_ in ext.get("rot_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
        for k, d_ in ext.get("polo", {}).items(): POLO[k].location = POLO_REP[k] + d_
        bpy.context.view_layer.update(); zr = regioes_zmin()
        if zr["tronco"] < -0.10 or zr["membro"] < -0.05 or zr["pata"] < -0.03: lo_ = m_   # REVISAO: tolerancias por regiao
        else: hi_ = m_
    DEITADO_Z = hi_; print("DEITADO_Z calibrado", round(DEITADO_Z, 3), "z_min por regiao", {k: round(v_, 3) for k, v_ in regioes_zmin().items()})
if os.environ.get("DEITADO_FIXO"): DEITADO_Z = float(os.environ["DEITADO_FIXO"]); print("DEITADO_Z fixo (teste)", DEITADO_Z)
elif any(n in QUAIS for n in ("Deitar", "LevantarDeitado")) or any(n.startswith(("Montar_", "Desmontar_")) for n in QUAIS): calibrar_deitado()   # montaria usa a pose deitada
manifesto = {}; QUADROS = {}
for nome in QUAIS:
    fn, dur, loop, vel, apoio_info = CLIPES[nome]
    nq = int(round(dur * FPS)) + (0 if loop else 1)
    quadros = []; erro_ik = 0.0; desliza = 0.0; zmin = 9.0; prev = None; TOQUE = {}; ERRO_PATA = {}
    for qi in range(nq):
        t = qi / FPS
        zerar(); rots, raiz, pes, ext = fn(t)
        if nome not in COM_ALTURA_PROPRIA: raiz = raiz + V((0, 0, BASE_Z))
        PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
        for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
        for k, d in pes.items(): ALVO[k].location = REP[k] + d
        for k, a_ in ext.get("rot_pe", {}).items():
            ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
        for k, g_ in ext.get("giro_pe", {}).items():                         # REVISAO: guinada da sola (virar no lugar)
            ALVO[k].rotation_quaternion = Quaternion(Z, g_) @ ALVO[k].rotation_quaternion
        for k, d_ in ext.get("polo", {}).items(): POLO[k].location = POLO_REP[k] + d_
        for k, w_ in ext.get("ik", {}).items():
            meio = PATAS[k][1]; PB[meio].constraints["IK"].influence = w_; PB[k].constraints["Copy Rotation"].influence = w_
        for k in TOQUE:
            if k not in ext.get("alvo_fk", {}): ALVO[k].location = TOQUE[k].copy()
        if ext.get("alvo_fk"):                                              # alvo = mistura repouso -> posicao da pata em FK
            for k in ext["alvo_fk"]: PB[PATAS[k][1]].constraints["IK"].mute = True; PB[k].constraints["Copy Rotation"].mute = True
            bpy.context.view_layer.update(); fk = {k: (PB[k].head.copy(), PB[k].matrix.to_quaternion()) for k in ext["alvo_fk"]}
            for k, w_ in ext["alvo_fk"].items():
                PB[PATAS[k][1]].constraints["IK"].mute = False; PB[k].constraints["Copy Rotation"].mute = False
                ALVO[k].location = ALVO[k].location.lerp(fk[k][0], w_); ALVO[k].rotation_quaternion = ALVO[k].rotation_quaternion.slerp(fk[k][1], w_)
                if ALVO[k].location.z < REP[k].z: ALVO[k].location.z = REP[k].z               # REVISAO: alvo nunca abaixo do chao (pouso)
                if k in TOQUE: ALVO[k].location = TOQUE[k].copy()                              # REVISAO: depois do toque a pata fica onde pousou
                elif t > 1.0 and ALVO[k].location.z <= REP[k].z + 0.01: TOQUE[k] = ALVO[k].location.copy()
        bpy.context.view_layer.update()
        pose = {pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in PB}
        for k in PATAS:
            if ext.get("ik", {}).get(k, 1.0) > 0.99 and ext.get("alvo_fk", {}).get(k, 0.0) < 0.01:
                e_ = (PB[k].head - ALVO[k].location).length; erro_ik = max(erro_ik, e_)
                if e_ > ERRO_PATA.get(k, (0, 0))[0]: ERRO_PATA[k] = (round(e_, 4), qi)
        if qi % 3 == 0: zmin = min(zmin, malha_zmin())
        quadros.append(pose)
    manifesto[nome] = {"duracao": dur, "loop": loop, "quadros": nq, "velocidade_studs_s_PROPOSTA": round(vel, 2),
                       "erro_ik_max": round(erro_ik, 4), "erro_ik_por_pata": ERRO_PATA, "malha_z_min": round(zmin, 3)}
    if nome in GIRO_SIM: manifesto[nome]["giro_graus_s_PROPOSTA"] = GIRO_SIM[nome]
    if callable(apoio_info): manifesto[nome]["v_perfil_PARAMETRO"] = [round(apoio_info(q_ / FPS), 4) for q_ in range(nq)]
    print("CLIPE", nome, manifesto[nome], flush=True)
    dado = {"nome": "Urso_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel, 3), "ossos": {}}
    if nome in EVENTOS_CLIPE: dado["eventos"] = EVENTOS_CLIPE[nome]; manifesto[nome]["eventos"] = EVENTOS_CLIPE[nome]
    for pb in PB:
        seq = []
        for pose in quadros:
            m = pose[pb.name]; q = m.to_quaternion(); tt = m.translation
            seq += [round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(tt.x, 5), round(tt.y, 5), round(tt.z, 5)]
        dado["ossos"][pb.name] = seq
    with open(os.path.join(OUT, "Urso_%s.json" % nome), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    QUADROS[nome] = quadros
# acoes FK assadas (restricoes desligadas para tocar a acao)
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
for nome, quadros in QUADROS.items():
    act = bpy.data.actions.get("Urso_" + nome) or bpy.data.actions.new("Urso_" + nome); arm.animation_data.action = act
    act["loop"] = CLIPES[nome][2]; act["velocidade_PROPOSTA"] = CLIPES[nome][3]
    for qi, pose in enumerate(quadros):
        for pb in PB:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    act.use_fake_user = True
arm.animation_data.action = None; zerar()
for pb in PB:
    for c in pb.constraints: c.mute = False
ant = {}
mp = os.path.join(OUT, "manifesto_clipes.json")
if os.path.exists(mp) and len(QUAIS) < len(CLIPES): ant = json.load(open(mp, encoding="utf-8"))
ant.update(manifesto); json.dump(ant, open(mp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.environ.get("URSO_ANIM_SAIDA") or os.path.join(os.path.dirname(bpy.data.filepath), "CR_Urso_v2_Anim.blend"))   # URSO_ANIM_SAIDA: poderes salvam a parte
print("ANIM_OK", list(QUADROS))
