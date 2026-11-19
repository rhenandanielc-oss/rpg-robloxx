"""Clipes do Cerbero Sombrio (procedurais, NO LUGAR: o jogo move o modelo). Adaptado de Urso_Silvestre_Ref/v2/rig/anim_urso.py.
Cada quadro define alvos IK das 4 patas (mundo), rotacoes de coluna/pescocos/cabecas/mandibulas/cauda e deslocamento da Raiz;
o IK resolve as patas e a pose final de cada osso e gravada em FK (acao 'Cerbero_<clipe>') e em JSON (mesmo formato dos
clipes do Urso/Crocodilo, para a ponte JSON -> KeyframeSequence do Studio).
Ritmo dos lobos (Lobo Artico anim_v41: Andar 36 q, Corrida 15 q) com peso de cao grande: peito largo e pesado (o tronco
dianteiro afunda no apoio das dianteiras), escapulas acompanhando a pata; as tres cabecas oscilam com ATRASOS diferentes.
PILOTO (17/11): Repouso, Andar, Corrida, Mordida (um ataque basico: so a cabeca C morde; E e D reagem pouco).
QA por clipe: erro do IK, escorregao da pata apoiada (relativo ao chao que corre), altura minima das patas e do resto da malha.
Velocidades sao PARAMETROS TECNICOS / PROPOSTA (RPG_02 15.3 propoe terra 39 studs/s, nao aprovado). Clipes nao definem mecanicas.
Uso: blender -b -t 4 CR_Cerbero_Rig.blend -P anim_cerbero.py -- <saida_dir> [clipe1,clipe2]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["Cerbero_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
MALHAS = [bpy.data.objects[n] for n in ("Cerbero_Cabecas", "Cerbero_Corpo", "Cerbero_Bocas")]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def onda(t, T, fase=0.0): return math.sin(2 * math.pi * (t / T + fase))
def janela(t, a, b, sub=0.2, des=0.2): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
R = math.radians
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
CABS = "CED"
S = {}                                                       # eixo lateral de cada cabeca (girar em S com angulo NEGATIVO = abaixa/abre)
for k in CABS:
    b = BD["Cabeca" + k]; f = b.tail_local - b.head_local; f.z = 0; f.normalize(); S[k] = f.cross(Z).normalized()

# ------------------------------------------------------------------ IK das patas (alvos = Empties no mundo)
PATAS = {"MaoE": ("dian", "AntebracoE", "BracoE"), "MaoD": ("dian", "AntebracoD", "BracoD"),
         "PeE": ("tras", "CanelaE", "CoxaE"), "PeD": ("tras", "CanelaD", "CoxaD")}
ALVO, POLO, REP = {}, {}, {}
for pe, (par, meio, topo) in PATAS.items():
    a_ = bpy.data.objects.new("IK_" + pe, None); sc.collection.objects.link(a_); a_.location = BD[pe].head_local.copy()
    a_.rotation_mode = "QUATERNION"; a_.rotation_quaternion = BD[pe].matrix_local.to_quaternion()
    j = BD[meio].head_local; p_ = bpy.data.objects.new("Polo_" + pe, None); sc.collection.objects.link(p_)
    p_.location = j + V((0, 5.0 if par == "dian" else -5.0, 0))                   # cotovelo para tras, joelho para a frente
    c = PB[meio].constraints.new("IK"); c.target = a_; c.pole_target = p_; c.chain_count = 2; c.use_stretch = False
    cr = PB[pe].constraints.new("COPY_ROTATION"); cr.target = a_
    ALVO[pe], POLO[pe], REP[pe] = a_, p_, a_.location.copy()
ROT0 = {k: o.rotation_quaternion.copy() for k, o in ALVO.items()}
POLO_REP = {k: o.location.copy() for k, o in POLO.items()}
bpy.context.view_layer.update()
for pe, (par, meio, topo) in PATAS.items():
    c = PB[meio].constraints["IK"]; alvo_j = BD[meio].head_local.copy()
    def erro(a_):
        c.pole_angle = a_; bpy.context.view_layer.update(); return (PB[meio].head - alvo_j).length + (PB[meio].tail - BD[meio].tail_local).length
    melhor = min((erro(R(g)), R(g)) for g in range(-180, 180, 5))[1]
    for passo_ in (2.5, 1.0, 0.25):
        melhor = min((erro(melhor + R(d)), melhor + R(d)) for d in (-passo_, 0, passo_))[1]
    c.pole_angle = melhor; print("POLO", pe, round(math.degrees(melhor), 2), "erro", round(erro(melhor), 4))
def rot_mundo(nome, eixos):
    r = BD[nome].matrix_local.to_3x3(); q = Matrix.Identity(3)
    for eixo, ang in eixos: q = Matrix.Rotation(ang, 3, eixo) @ q
    return (r.inverted() @ q @ r).to_quaternion()
def zerar():
    for pb in PB: pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for k, o in ALVO.items(): o.location = REP[k].copy(); o.rotation_quaternion = ROT0[k].copy()
    for k, o in POLO.items(): o.location = POLO_REP[k].copy()
    for pe_, (par_, meio_, topo_) in PATAS.items(): PB[meio_].constraints["IK"].mute = False; PB[pe_].constraints["Copy Rotation"].mute = False   # L3

# ------------------------------------------------------------------ locomocao: apoio amarrado ao deslocamento integrado S(t)
class Perfil:
    def __init__(self, vfun, t0=-3.0, t1=8.0, dt=1 / 600):
        self.t0, self.dt = t0, dt; n = int((t1 - t0) / dt) + 1; acc = 0.0; self.S = []
        for i in range(n): self.S.append(acc); acc += vfun(t0 + i * dt) * dt
    def s(self, t):
        x = (t - self.t0) / self.dt; i = max(0, min(len(self.S) - 2, int(x))); return self.S[i] + (self.S[i + 1] - self.S[i]) * (x - i)
ALT_UL = {}
def passo_var(t, fase, T, apoio, alt, Lf, perf, eixo=V((0, 1, 0))):
    phi = t / T + fase; n_ = math.floor(phi); f = phi - n_; tc = (n_ - fase) * T
    if f < apoio: return eixo * (-Lf(tc) / 2 + perf.s(t) - perf.s(tc)), 0.0
    tl = tc + apoio * T; y0 = -Lf(tc) / 2 + perf.s(tl) - perf.s(tc); y1 = -Lf(tc + T) / 2
    u = (f - apoio) / (1 - apoio); s = suave(u)
    mundo_ = abs((y1 - y0) - (perf.s(tc + T) - perf.s(tl)))                     # 2A: quanto a pata anda NO MUNDO neste balanco
    alt = max(alt, 0.6 * min(1.0, mundo_ / 1.0))                                # 2A: pata que se move sempre sai do chao
    return eixo * (y0 + (y1 - y0) * s) + V((0, 0, alt * math.sin(math.pi * u))), u
BASE_Z = -0.45                                              # altura comum (pernas levemente dobradas)
T_AND, L_AND, AP_AND, ALT_AND = 36 / 30, 3.6, 0.62, 0.95    # r2: 4,2 passava do alcance (erro IK 0,10)
    # ritmo do lobo (36 q); passada de cao de ~14 studs de ombro
T_GAL, L_GAL, AP_GAL, ALT_GAL = 16 / 30, 4.4, 0.37, 1.45    # r2: 5,4 passava do alcance (erro IK 0,39)
    # galope: 16 q (lobo 15 q; o Cerbero e mais pesado)
FASE_ANDAR = {"PeE": 0.0, "MaoE": 0.25, "PeD": 0.5, "MaoD": 0.75}                      # sequencia lateral
FASE_GALOPE = {"PeE": 0.0, "PeD": 0.12, "MaoD": 0.46, "MaoE": 0.58}                    # galope rotatorio
V_AND = L_AND / (AP_AND * T_AND); V_GAL = L_GAL / (AP_GAL * T_GAL)
PERF_AND = Perfil(lambda t: V_AND); PERF_GAL = Perfil(lambda t: V_GAL)
ATRASO = {"C": 0.0, "E": 0.07, "D": -0.06}                  # cabecas desencontradas (fracao do ciclo)
AMP = {"C": 1.0, "E": 0.85, "D": 0.9}
def cabecas_osc(r, u, amp_pitch, amp_yaw, mand=0.0):
    """oscilacao controlada: cada cabeca acompanha o passo com seu atraso; laterais um pouco menos"""
    for k in CABS:
        uu = u + ATRASO[k]; c2 = math.cos(4 * math.pi * uu); s1 = math.sin(2 * math.pi * uu)
        r["Pescoco%s1" % k] = [(S[k], -R(amp_pitch) * c2 * AMP[k]), (Z, R(amp_yaw) * s1 * AMP[k])]
        r["Pescoco%s2" % k] = [(S[k], R(amp_pitch * 0.5) * c2 * AMP[k])]
        r["Cabeca" + k] = [(S[k], R(amp_pitch * 0.6) * c2 * AMP[k])]                  # cabeca compensa: o olhar fica estavel
        if mand: r["Mandibula" + k] = [(S[k], -R(mand) * (0.5 + 0.5 * math.sin(2 * math.pi * (uu + 0.2))))]
def rot_sola(ext, k_, u, lim=22):
    ext["rot_pe"][k_] = -R(lim) * math.sin(math.pi * u) if u > 0 else 0.0
def c_andar(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_AND
    for k_, fase in FASE_ANDAR.items():
        pes[k_], uu = passo_var(t, fase, T_AND, AP_AND, ALT_AND, lambda tt: L_AND, PERF_AND); rot_sola(ext, k_, uu); ext["apoio"][k_] = uu == 0
    sw = math.sin(2 * math.pi * u)
    # peso dianteiro: o peito afunda quando uma dianteira recebe o peso (2x por ciclo, logo apos cada pouso dianteiro)
    peito = math.cos(4 * math.pi * (u - FASE_ANDAR["MaoE"] - 0.05))
    r["Pelve"] = [(Y, R(2.5) * sw), (Z, R(1.8) * sw)]
    r["Coluna2"] = [(Y, R(-2.0) * sw), (Z, R(-1.5) * sw)]
    r["Coluna3"] = [(Y, R(1.6) * math.sin(2 * math.pi * (u + 0.25))), (X, R(1.6) * peito)]
    for p_ in ("MaoE", "MaoD"): r["Escapula" + p_[-1]] = [(X, R(6) * math.cos(2 * math.pi * ((u + FASE_ANDAR[p_]) % 1.0)))]
    cabecas_osc(r, u, 2.6, 2.0)
    r["Cauda1"] = [(Z, R(6) * sw), (X, R(-4))]; r["Cauda2"] = [(Z, R(5) * math.sin(2 * math.pi * (u - 0.1)))]
    r["Cauda3"] = [(Z, R(4) * math.sin(2 * math.pi * (u - 0.2)))]
    return r, V((0.12 * sw, 0, BASE_Z - 0.05 + 0.08 * math.cos(4 * math.pi * u) - 0.05 * (peito + 1) / 2)), pes, ext
def c_corrida(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_GAL
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(t, fase, T_GAL, AP_GAL, ALT_GAL, lambda tt: L_GAL, PERF_GAL); rot_sola(ext, k_, uu, 32); ext["apoio"][k_] = uu == 0
    corpo_galope(r, u, 1.0)
    return r, V((0, 0, Z_GAL + 0.30 * math.sin(2 * math.pi * (u - 0.05)))), pes, ext
Z_GAL = -1.25
def corpo_galope(r, u, k):
    """tronco, escapulas, cabecas e cauda do galope; k = intensidade (1 = Corrida; Partida/Freada crescem ou somem)"""
    fl = math.sin(2 * math.pi * (u - 0.15)); flex = 8 * k
    r["Pelve"] = [(X, R(flex) * fl)]; r["Coluna1"] = [(X, R(-flex * 0.6) * fl)]; r["Coluna2"] = [(X, R(-flex * 0.5) * fl)]
    r["Coluna3"] = [(X, R(flex * 0.35) * fl)]
    for p_ in ("MaoE", "MaoD"): r["Escapula" + p_[-1]] = [(X, R(10) * k * math.cos(2 * math.pi * ((u + FASE_GALOPE[p_]) % 1.0)))]
    cabecas_osc(r, u * 0.5, 3.5 * k, 0.0)                      # aceno: 1 por passada (cabecas mais baixas e firmes)
    for kk in CABS:                                             # 2A: guinada e boca entreaberta com periodo da PASSADA (antes u*0,5
        uu = u + ATRASO[kk]                                     # nao fechava o loop: salto de ate ~7 graus na mandibula)
        r["Pescoco%s1" % kk] += [(Z, R(1.2 * k) * math.sin(2 * math.pi * uu) * AMP[kk])]
        r["Mandibula" + kk] = [(S[kk], -R(7 * k) * (0.5 + 0.5 * math.sin(2 * math.pi * (uu + 0.2))))]
    for kk in CABS:
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], -R(10) * k)]; r["Cabeca" + kk] = r["Cabeca" + kk] + [(S[kk], R(6) * k)]
    r["Cauda1"] = [(X, R(-10) * k + R(6) * fl * k), (Z, R(3) * k * math.sin(2 * math.pi * u))]
    r["Cauda2"] = [(X, R(5) * k * math.sin(2 * math.pi * (u - 0.15)))]

# ------------------------------------------------------------------ LOTE 2A (17/11): Trote, Partida, Freada, Viradas, Salto
class PerfDesloc:
    def __init__(self, p, d): self.p, self.d = p, d
    def s(self, t): return self.p.s(t + self.d)
T_TRO, L_TRO, AP_TRO, ALT_TRO = 18 / 30, 3.2, 0.45, 1.0       # r2: 3,8 passava do alcance       # trote diagonal no ritmo do lobo (18 q)
FASE_TROTE = {"PeE": 0.0, "MaoD": 0.0, "PeD": 0.5, "MaoE": 0.5}
V_TRO = L_TRO / (AP_TRO * T_TRO); PERF_TRO = Perfil(lambda t: V_TRO)
def c_trote(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_TRO
    for k_, fase in FASE_TROTE.items():
        pes[k_], uu = passo_var(t, fase, T_TRO, AP_TRO, ALT_TRO, lambda tt: L_TRO, PERF_TRO); rot_sola(ext, k_, uu, 28); ext["apoio"][k_] = uu == 0
    c2 = math.cos(4 * math.pi * u); s1 = math.sin(2 * math.pi * u)
    r["Pelve"] = [(Y, R(2.0) * s1)]; r["Coluna2"] = [(Y, R(-1.6) * s1)]; r["Coluna3"] = [(Y, R(1.2) * s1), (X, R(1.4) * c2)]
    for p_ in ("MaoE", "MaoD"): r["Escapula" + p_[-1]] = [(X, R(8) * math.cos(2 * math.pi * ((u + FASE_TROTE[p_]) % 1.0)))]
    cabecas_osc(r, u, 2.2, 1.0)
    for kk in CABS: r["Pescoco%s1" % kk] += [(S[kk], -R(5))]
    r["Cauda1"] = [(X, R(-6)), (Z, R(4) * s1)]; r["Cauda2"] = [(Z, R(4) * math.sin(2 * math.pi * (u - 0.12)))]
    return r, V((0, 0, BASE_Z - 0.35 + 0.14 * c2)), pes, ext          # duas batidas por ciclo (cada par diagonal)
# Partida: agacha 11 q, depois 3 ciclos de galope crescendo; o ultimo quadro = quadro 0 da Corrida (fase inteira)
T0_ARR = 11 / 30; DUR_ARR = T0_ARR + 3 * T_GAL
def k_arr(t): return suave((t - T0_ARR) / (2 * T_GAL))
PERF_ARR = Perfil(lambda t: V_GAL * k_arr(t)); PERF_ARR_G = PerfDesloc(PERF_ARR, T0_ARR)
def c_partida(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}, "v": V_GAL * k_arr(t)}; k = k_arr(t)
    ag = janela(t, 0.0, T0_ARR + 0.10, 0.22, 0.16); tt = t - T0_ARR
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(tt, fase, T_GAL, AP_GAL, ALT_GAL * k, lambda x: L_GAL * k_arr(x + T0_ARR), PERF_ARR_G)
        rot_sola(ext, k_, uu if k > 0.02 else 0.0, 32); ext["apoio"][k_] = uu == 0
    corpo_galope(r, tt / T_GAL, k)
    r["Pelve"] = r["Pelve"] + [(X, R(6) * ag)]                  # agachar: garupa desce, cabecas abaixam juntas (mira)
    for kk in CABS: r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], -R(8) * ag)]
    z = BASE_Z + (Z_GAL - BASE_Z) * k + 0.30 * k * math.sin(2 * math.pi * (tt / T_GAL - 0.05)) - 0.55 * ag
    return r, V((0, 0.35 * ag, z)), pes, ext
# Freada: comeca no quadro 0 da Corrida; a passada encolhe ate parar; o peso senta nas traseiras e volta a pose de Repouso
DUR_FRE = 1.5
def k_fre(t): return 1 - suave(t / 0.95)
PERF_FRE = Perfil(lambda t: V_GAL * k_fre(t))
def c_freada(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}, "v": V_GAL * k_fre(t)}; k = k_fre(t); s = janela(t, 0.35, DUR_FRE, 0.25, 0.55)
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(t, fase, T_GAL, AP_GAL, ALT_GAL * max(k, 0.0) ** 0.7, lambda x: L_GAL * k_fre(x), PERF_FRE)
        rot_sola(ext, k_, uu if k > 0.02 else 0.0, 32); ext["apoio"][k_] = uu == 0
    corpo_galope(r, t / T_GAL, k)
    r["Pelve"] = r["Pelve"] + [(X, R(-7) * s)]; r["Coluna2"] = r["Coluna2"] + [(X, R(4) * s)]
    for kk, at in (("C", 0.0), ("E", 0.06), ("D", 0.10)):        # cabecas sobem em sequencia ao frear (inercia desencontrada)
        sk = janela(t, 0.35 + at, DUR_FRE, 0.25, 0.55)
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], R(9) * sk)]; r["Cabeca" + kk] = r["Cabeca" + kk] + [(S[kk], -R(5) * sk)]
    z = BASE_Z + (Z_GAL - BASE_Z) * k + 0.30 * k * math.sin(2 * math.pi * (t / T_GAL - 0.05)) - 0.40 * s
    return r, V((0, 0.45 * s, z)), pes, ext
GIRO = math.radians(30)                                       # virar no lugar: 30 graus/s (PARAMETRO; 60 passava do alcance: as dianteiras ficam a ~6,5 do pivo)
PIVO = BD["Raiz"].head_local.copy()
def c_virar(sinal):
    """virar no lugar: o jogo gira o modelo a sinal*GIRO em torno da Raiz (+1 = esquerda, anti-horario). Pata apoiada =
    ponto fixo no mundo visto do corpo (gira -omega em torno do pivo); balanco: arco ate o proximo pouso."""
    w = GIRO * sinal; T = T_AND; ap = AP_AND
    def girado(k_, ang):
        rr = REP[k_] - PIVO; c_, s_ = math.cos(ang), math.sin(ang)
        return V((PIVO.x + rr.x * c_ - rr.y * s_, PIVO.y + rr.x * s_ + rr.y * c_, REP[k_].z)) - REP[k_]
    def f(t):
        r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}, "w": w, "giro_pe": {}}; u = t / T; meia = w * ap * T / 2
        for k_, fase in FASE_ANDAR.items():
            phi = t / T + fase; n_ = math.floor(phi); fr = phi - n_; tc = (n_ - fase) * T; tm = tc + ap * T / 2
            if fr < ap:
                pes[k_] = girado(k_, -w * (t - tm)); uu = 0.0; ext["giro_pe"][k_] = -w * (t - tm)
            else:
                uu = (fr - ap) / (1 - ap); p0, p1 = girado(k_, -meia), girado(k_, meia)
                ext["giro_pe"][k_] = -meia + 2 * meia * suave(uu)
                pes[k_] = p0.lerp(p1, suave(uu)) + V((0, 0, 0.6 * math.sin(math.pi * uu)))
            rot_sola(ext, k_, uu, 16); ext["apoio"][k_] = uu == 0
        sw = math.sin(2 * math.pi * u)
        r["Pelve"] = [(Y, R(1.5) * sw), (Z, R(-5) * sinal)]; r["Coluna2"] = [(Z, R(6) * sinal)]; r["Coluna3"] = [(Z, R(4) * sinal)]
        cabecas_osc(r, u, 1.6, 0.0)
        for kk, at in (("C", 1.0), ("E", 0.8 if sinal > 0 else 1.2), ("D", 1.2 if sinal > 0 else 0.8)):   # cabeca do lado da curva lidera
            r["Pescoco%s1" % kk] += [(Z, R(12) * sinal * at)]; r["Cabeca" + kk] = r["Cabeca" + kk] + [(Z, R(6) * sinal * at)]
        r["Cauda1"] = [(Z, R(-10) * sinal + R(3) * sw), (X, R(-3))]
        return r, V((0.06 * sw, 0, BASE_Z - 0.04 + 0.04 * math.cos(4 * math.pi * u))), pes, ext
    return f
# Salto: agacha -> impulso -> voo (dianteiras a frente, traseiras recolhidas) -> pouso das dianteiras -> recuperacao.
# A subida da Raiz no clipe e VISUAL (arco de 2,6 studs); a altura real do salto e da fisica do jogo (eventos marcam as fases).
EV_SALTO = {"agachar": 0.0, "decolagem": 0.42, "apice": 0.70, "pouso": 0.98, "recuperacao": 1.10, "fim": 1.5}
def c_salto(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    ag = suave(t / 0.36) * (1 - suave((t - 0.36) / 0.08))       # agachamento
    imp = janela(t, 0.36, 0.55, 0.06, 0.12)                    # extensao no impulso
    tv = (t - 0.42) / (0.98 - 0.42); ar = 0.0 < tv < 1.0
    arco = 2.6 * 4 * tv * (1 - tv) if ar else 0.0
    am = janela(t, 0.98, 1.5, 0.05, 0.40)                       # amortecimento do pouso
    zr = BASE_Z - 0.95 * ag + 0.35 * imp + arco - 0.80 * am
    sobe = max(0.0, zr - (BASE_Z + 0.25))                       # acima disto as patas deixam o chao (pernas ja esticadas)
    vo = suave(tv / 0.25) * (1 - suave((tv - 0.7) / 0.3)) if ar else 0.0
    for k_ in PATAS:
        dian = k_.startswith("Mao")
        tuck = V((0, -1.4 if dian else 1.1, 0.9 if dian else 1.3)) * vo   # dianteiras estendem a frente, traseiras recolhem
        pes[k_] = V((0, 0, sobe)) + tuck; ext["apoio"][k_] = sobe < 1e-4 and vo < 1e-4; ext.setdefault("no_ar", {})[k_] = sobe > 1e-4 or vo > 1e-4   # r2: recolher ja e voo
        ext["rot_pe"][k_] = (-R(30) if dian else -R(40)) * vo
    inc = R(-6) * imp * (1 - am) + R(8) * vo * (tv - 0.5) * 2 + R(6) * am * (1 - suave((t - 1.2) / 0.3))   # nariz sobe na decolagem, desce no pouso
    r["Pelve"] = [(X, inc * 0.6 + R(8) * ag)]; r["Coluna2"] = [(X, inc * 0.4)]; r["Coluna3"] = [(X, inc * 0.5 - R(4) * ag)]
    for kk, at in (("C", 0.0), ("E", 0.03), ("D", 0.05)):
        tt_ = t - at; agk = suave(tt_ / 0.36) * (1 - suave((tt_ - 0.36) / 0.08)); amk = janela(tt_, 0.98, 1.5, 0.06, 0.40)
        r["Pescoco%s1" % kk] = [(S[kk], -R(10) * agk + R(6) * vo - R(10) * amk)]; r["Cabeca" + kk] = [(S[kk], R(4) * agk + R(5) * amk)]
        r["Mandibula" + kk] = [(S[kk], -R(5) * vo)]
    r["Cauda1"] = [(X, R(-15) * vo + R(10) * ag), (Z, 0.0)]; r["Cauda2"] = [(X, R(-8) * vo)]
    return r, V((0, 0, zr)), pes, ext
# ------------------------------------------------------------------ LOTE 2B (17/11): Alerta, Observar, ReacaoGolpe, Deitar, Descanso, Levantar
def c_alerta(t):
    """algo chamou a atencao: as tres cabecas sobem e miram em sequencia (C, depois D, depois E), peso a frente, cauda alta;
    segura e volta ao Repouso no fim (encaixa nos dois lados)"""
    r = {}; DUR = 2.4
    for kk, at, yaw in (("C", 0.00, 0.0), ("D", 0.10, -6.0), ("E", 0.18, 8.0)):
        k = janela(t, 0.05 + at, DUR - 0.05, 0.22, 0.55)
        tremor = R(0.6) * math.sin(2 * math.pi * 7 * t) * janela(t, 0.5, 1.6, 0.1, 0.2)
        r["Pescoco%s1" % kk] = [(S[kk], R(14) * k), (Z, R(yaw) * k)]; r["Pescoco%s2" % kk] = [(S[kk], R(4) * k)]
        r["Cabeca" + kk] = [(S[kk], -R(6) * k + tremor)]
        r["Mandibula" + kk] = [(S[kk], -R(5) * janela(t, 0.9 + at, 1.5 + at, 0.12, 0.25))]          # farejo curto de boca entreaberta
    k = janela(t, 0.05, DUR - 0.05, 0.25, 0.55)
    r["Coluna3"] = [(X, R(-3) * k)]; r["Coluna2"] = [(X, R(-1.5) * k)]; r["Pelve"] = [(X, R(2) * k)]
    r["Cauda1"] = [(X, R(18) * k)]; r["Cauda2"] = [(X, R(6) * k)]
    return r, V((0, -0.25 * k, 0.12 * k)), {}, {}
def c_observar(t):
    """Vigilia (orienta o olhar): cada cabeca varre um setor diferente com tempos desencontrados; a C fareja no meio"""
    r = {}
    e1 = janela(t, 0.3, 2.3, 0.5, 0.5); e2 = janela(t, 2.4, 4.2, 0.5, 0.5)
    d1 = janela(t, 0.6, 2.6, 0.5, 0.5); d2 = janela(t, 2.7, 4.2, 0.5, 0.45)
    c1 = janela(t, 1.2, 3.0, 0.45, 0.45); sniff = janela(t, 1.6, 2.6, 0.15, 0.2) * math.sin(2 * math.pi * t * 4)
    r["PescocoE1"] = [(Z, R(28) * e1 + R(8) * e2), (S["E"], R(4) * e1 - R(6) * e2)]; r["CabecaE"] = [(Z, R(10) * e1), (S["E"], -R(5) * e2)]
    r["PescocoD1"] = [(Z, -R(26) * d1 - R(6) * d2), (S["D"], R(5) * d2)]; r["CabecaD"] = [(Z, -R(10) * d1), (S["D"], R(4) * d2)]
    r["PescocoC1"] = [(S["C"], -R(10) * c1)]; r["CabecaC"] = [(S["C"], -R(6) * c1 + R(1.5) * sniff)]
    r["MandibulaC"] = [(S["C"], -R(3) * c1)]
    r["Coluna3"] = [(Z, R(3) * (e1 - d1))]
    r["Cauda1"] = [(Z, R(5) * math.sin(2 * math.pi * t / 4.4)), (X, R(4) * janela(t, 0.2, 4.2, 0.5, 0.5))]
    return r, V((0, 0, 0.04 * onda(t, 2.2))), {}, {}
def c_reacao(t):
    """golpe pela frente-esquerda: tronco recua e torce, as cabecas sacodem com atrasos (a E, mais perto, mais forte),
    rosnado curto e assentada; volta ao Repouso"""
    r = {}; i = suave(t / 0.07) * (1 - suave((t - 0.12) / 0.55)); rec = janela(t, 0.22, 1.0, 0.2, 0.35)
    for kk, at, f in (("E", 0.00, 1.0), ("C", 0.03, 0.8), ("D", 0.06, 0.6)):
        ii = suave((t - at) / 0.07) * (1 - suave((t - at - 0.12) / 0.55))
        r["Pescoco%s1" % kk] = [(Z, -R(16) * f * ii), (S[kk], R(8) * f * ii)]; r["Cabeca" + kk] = [(Z, -R(10) * f * ii), (S[kk], R(6) * f * ii)]
        r["Mandibula" + kk] = [(S[kk], -R(14) * f * janela(t, 0.10 + at, 0.7 + at, 0.08, 0.3))]
    r["Coluna2"] = [(Z, -R(6) * i), (Y, R(5) * i)]; r["Coluna3"] = [(Z, -R(6) * i)]; r["Cauda1"] = [(X, -R(12) * i)]
    return r, V((-0.25 * i, 0.55 * i, -0.30 * i - 0.25 * rec)), {}, {}
# --- deitar (esternal): a pata gira em torno do PROPRIO ponto de apoio (nao escorrega); dianteiras dao um passo a frente
# antes de deitar; traseiras: o metatarso deita para tras ate o jarrete tocar o chao; corpo desce ate o peito tocar o chao.
FLAT = R(66)                                               # r2: osso Mao/Pe inclinado (84 enterrava o antebraco grosso desta malha)
PASSO_DIAN = 1.6                                            # passo das dianteiras a frente (studs; PARAMETRO)
DEITADO = {"z": -5.6}                                        # descida da Raiz; CALIBRADA pela malha antes dos clipes
def pata_dobra(k_, k, passo=0.0, alt=0.0):
    """k = 0 em pe -> 1 deitada; gira o osso Mao/Pe em torno da ponta (apoio) ate FLAT"""
    b = BD[k_]; W0, P0 = b.head_local.copy(), b.tail_local.copy(); d0 = W0 - P0
    phi0 = math.atan2(d0.y, d0.z); L = math.hypot(d0.y, d0.z); phi = phi0 + (FLAT - phi0) * k   # r3: L no plano YZ (x mantido)
    P = P0 + V((0, -passo, alt + 0.20 * k))                    # r2: apoio sobe um pouco ao deitar (malha grossa da pata)
    W = P + V((d0.x, L * math.sin(phi), L * math.cos(phi)))
    dir_n = (P - W).normalized(); q = (P0 - W0).normalized().rotation_difference(dir_n)
    return W - W0, q
def pose_deitada(r, pes, ext, kd, kt, kf, passo, alt=0.0):
    """kd = descida do corpo; kt/kf = dobra das traseiras/dianteiras; passo = fracao do passo a frente das dianteiras"""
    for k_ in PATAS:
        dian = k_.startswith("Mao")
        d, q = pata_dobra(k_, kf if dian else kt, PASSO_DIAN * passo if dian else 0.0, alt if dian else 0.0)
        pes[k_] = d; ext.setdefault("rot_q", {})[k_] = q
        eixo_, ang_ = q.to_axis_angle()                          # r2: dedos giram ao contrario (ficam planos no chao)
        dd = ("Dedos" + k_[-1]) if dian else ("DedosPe" + k_[-1])
        r[dd] = r.get(dd, []) + [(V(eixo_), -ang_)]
    r["Pelve"] = r.get("Pelve", []) + [(X, R(-4) * kd)]; r["Coluna3"] = r.get("Coluna3", []) + [(X, R(3) * kd)]
    for kk, at in (("C", 0.0), ("E", 0.08), ("D", 0.04)):
        r["Pescoco%s1" % kk] = r.get("Pescoco%s1" % kk, []) + [(S[kk], R(10) * kd)]       # pescocos compensam a descida (cabecas ficam erguidas)
    r["Cauda1"] = r.get("Cauda1", []) + [(X, R(-14) * kd)]; r["Cauda2"] = r.get("Cauda2", []) + [(X, R(8) * kd), (Z, R(18) * kd)]
    return DEITADO["z"] * kd
def degrau(t, a, b, alt=0.7):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return suave(x), alt * math.sin(math.pi * x)
DUR_DEITAR, DUR_LEVANTAR = 2.6, 2.2
def c_deitar(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    passo, alt = degrau(t, 0.15, 0.75)                         # dianteiras: passo a frente (sai do chao, nao arrasta)
    kt = suave((t - 0.55) / 1.25); kd = suave((t - 0.70) / 1.55); kf = suave((t - 1.05) / 1.25)
    z = pose_deitada(r, pes, ext, kd, kt, kf, passo, alt)
    for k_ in PATAS: ext["apoio"][k_] = not (k_.startswith("Mao") and 0.15 < t < 0.75)
    for kk, at in (("C", 0.0), ("E", 0.12), ("D", 0.22)):        # cabecas acompanham a descida desencontradas
        b_ = janela(t, 0.3 + at, 1.6 + at, 0.4, 0.5)
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], -R(8) * b_)]
    cabecas_descanso(r, suave((t - 1.6) / 0.9))                # r3: termina na pose do Descanso
    return r, V((0, 0.35 * kd, BASE_Z + z * 1.0 + 0.25 * kd)), pes, ext
def cabecas_descanso(r, k):
    """r3: pose das cabecas no inicio do Descanso (E de queixo apoiado, D cochilando), na intensidade k: Deitar termina e
    Levantar comeca exatamente nela"""
    for kk in CABS: r["Pescoco%s1" % kk] = r.get("Pescoco%s1" % kk, []) + [(S[kk], -R(1.0) * onda(0.0, 3.0, ATRASO[kk]) * k)]
    r["PescocoE1"] = r["PescocoE1"] + [(S["E"], -R(22) * k), (Z, R(6) * k)]; r["CabecaE"] = r.get("CabecaE", []) + [(S["E"], -R(10) * k)]
    r["PescocoD1"] = r["PescocoD1"] + [(S["D"], -R(14) * k)]; r["CabecaD"] = r.get("CabecaD", []) + [(S["D"], -R(8) * k)]
def c_descanso(t):
    """deitado, em loop: respiracao profunda (4 s) e cabecas desencontradas: C erguida vigia, E apoia o queixo, D cochila e
    levanta a cada tanto; uma lambida curta da E"""
    T = 6.0; r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {k_: True for k_ in PATAS}}
    z = pose_deitada(r, pes, ext, 1.0, 1.0, 1.0, 1.0)
    b = onda(t, 3.0)
    r["Coluna1"] = [(X, R(1.0) * b)]; r["Coluna2"] = [(X, R(-1.2) * b)]
    for kk in CABS: r["Pescoco%s1" % kk] += [(S[kk], -R(1.0) * onda(t, 3.0, ATRASO[kk]))]
    r["PescocoE1"] += [(S["E"], -R(22)), (Z, R(6))]; r["CabecaE"] = [(S["E"], -R(10))]                 # queixo apoiado (baixo)
    acorda = janela(t, 2.4, 4.4, 0.5, 0.6)
    r["PescocoD1"] += [(S["D"], -R(14) * (1 - acorda))]; r["CabecaD"] = [(S["D"], -R(8) * (1 - acorda)), (Z, -R(10) * acorda)]
    r["PescocoC1"] += [(Z, R(6) * janela(t, 0.6, 2.2, 0.5, 0.5) - R(6) * janela(t, 3.6, 5.4, 0.5, 0.5))]
    r["MandibulaE"] = [(S["E"], -R(8) * janela(t, 4.6, 5.3, 0.15, 0.25))]
    r["Cauda3"] = [(Z, R(5) * onda(t, T))]
    return r, V((0, 0.35, BASE_Z + z + 0.25 + 0.04 * b)), pes, ext
def c_levantar(t):
    """dianteiras empurram primeiro (peito sobe), traseiras depois; dianteiras voltam com um passo (sai do chao)"""
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    kf = 1 - suave(t / 0.85); kd = 1 - suave((t - 0.25) / 1.15); kt = 1 - suave((t - 0.55) / 1.05)
    passo, alt = degrau(t, 1.25, 1.85); passo = 1 - passo
    z = pose_deitada(r, pes, ext, kd, kt, kf, passo, alt)
    for k_ in PATAS: ext["apoio"][k_] = not (k_.startswith("Mao") and 1.25 < t < 1.85)
    for kk, at in (("C", 0.0), ("E", 0.08), ("D", 0.14)):
        b_ = janela(t, 0.1 + at, 1.4 + at, 0.3, 0.5)
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], R(8) * b_)]          # cabecas puxam para cima ao levantar
    r["Coluna3"] = r["Coluna3"] + [(X, -R(5) * janela(t, 0.0, 1.2, 0.3, 0.5))]
    cabecas_descanso(r, 1 - suave(t / 0.6))                    # r3: comeca na pose do Descanso
    return r, V((0, 0.35 * kd, BASE_Z + z + 0.25 * kd)), pes, ext
EVENTOS_LOTE2B = {"Deitar": {"passo_dianteiras": 0.15, "traseiras_dobram": 0.55, "peito_no_chao": 2.25, "fim_deitado": DUR_DEITAR},
                  "Levantar": {"dianteiras_empurram": 0.0, "traseiras_sobem": 0.55, "passo_dianteiras": 1.25, "fim_em_pe": DUR_LEVANTAR},
                  "ReacaoGolpe": {"impacto": 0.0, "recuperacao": 0.22, "fim": 1.0}, "Alerta": {"mira": 0.05, "segura": 0.6, "volta": 1.85, "fim": 2.4}}
EVENTOS_LOTE2 = {**EVENTOS_LOTE2B, "Salto": EV_SALTO, "Partida": {"agachar": 0.0, "primeira_passada": round(T0_ARR, 3), "encaixa_corrida": round(DUR_ARR, 3)},
                 "Freada": {"inicio_na_corrida": 0.0, "parada": 0.95, "fim_em_repouso": DUR_FRE}}
def c_repouso(t):
    """respiracao + pequenas reacoes desencontradas: C vira de leve, E olha para fora, D fareja para baixo, E boceja curto"""
    T = 6.0; r = {}; b = onda(t, 3.0)
    r["Coluna1"] = [(X, R(0.6) * b)]; r["Coluna2"] = [(X, R(-0.8) * b)]; r["Coluna3"] = [(X, R(0.5) * b)]
    c_ = janela(t, 0.8, 2.4, 0.45, 0.5); e_ = janela(t, 2.2, 3.9, 0.45, 0.5); d_ = janela(t, 3.8, 5.6, 0.5, 0.5)
    sniff = janela(t, 4.3, 5.2, 0.15, 0.2) * math.sin(2 * math.pi * t * 3.5)
    for k in CABS:
        resp = R(0.8) * onda(t, 3.0, ATRASO[k])
        r["Pescoco%s1" % k] = [(S[k], -resp)]; r["Cabeca" + k] = [(S[k], resp * 0.6)]
    r["PescocoC1"] += [(Z, R(10) * c_)]; r["CabecaC"] += [(Z, R(6) * c_)]
    r["PescocoE1"] += [(Z, R(12) * e_), (S["E"], R(5) * e_)]; r["CabecaE"] += [(S["E"], R(4) * e_)]
    r["PescocoD1"] += [(S["D"], -R(9) * d_)]; r["CabecaD"] += [(S["D"], -R(7) * d_ + R(1.5) * sniff)]
    r["MandibulaD"] = [(S["D"], -R(2) * janela(t, 4.4, 5.0, 0.1, 0.15))]
    r["MandibulaE"] = [(S["E"], -R(14) * janela(t, 0.2, 0.9, 0.2, 0.3))]                        # bocejo curto
    r["Cauda1"] = [(Z, R(4) * onda(t, T)), (X, R(-3))]; r["Cauda2"] = [(Z, R(3) * onda(t, T, -0.1))]
    return r, V((0, 0, 0.05 * b)), {}, {}
EV_MORD = {"antecipacao": 0.0, "bote": 0.30, "contato": 0.42, "recuperacao": 0.55, "fim": 1.1}
def c_mordida(t):
    """mordida basica da cabeca C: recolhe e abre -> bote com estalo da mandibula -> recuperacao; E e D abrem espaco"""
    r = {}; a = suave(t / 0.30); b = suave((t - 0.30) / 0.12); c = suave((t - 0.55) / 0.55)
    boca = -R(36) * a * (1 - b) - R(4) * b * (1 - c)
    r["MandibulaC"] = [(S["C"], boca)]
    r["PescocoC1"] = [(S["C"], R(9) * a * (1 - b) - R(14) * b * (1 - c))]; r["PescocoC2"] = [(S["C"], R(5) * a * (1 - b) - R(6) * b * (1 - c))]
    r["CabecaC"] = [(S["C"], R(8) * a * (1 - b) - R(4) * b * (1 - c))]
    for k, sg in (("E", 1), ("D", -1)):                      # laterais se afastam um pouco (sem colisao de mandibulas) e reagem atrasadas
        lad = suave((t - 0.10) / 0.3) * (1 - suave((t - 0.6) / 0.45))
        r["Pescoco%s1" % k] = [(Z, R(7) * sg * lad), (S[k], R(3) * lad)]; r["Mandibula" + k] = [(S[k], -R(6) * janela(t, 0.35, 0.8, 0.1, 0.2))]
    r["Coluna3"] = [(X, R(-2) * a * (1 - b) + R(4) * b * (1 - c))]; r["Coluna2"] = [(X, R(2) * b * (1 - c))]
    r["Cauda1"] = [(X, R(-8) * a * (1 - c))]
    return r, V((0, 0.40 * a * (1 - b) - 0.9 * b * (1 - c), -0.18 * b * (1 - c))), {}, {}
CLIPES = {  # nome: (funcao, duracao s, loop, velocidade de simulacao [PARAMETRO TECNICO])
    "Repouso": (c_repouso, 6.0, True, 0.0),
    "Andar": (c_andar, T_AND, True, V_AND),
    "Corrida": (c_corrida, T_GAL, True, V_GAL),
    "Mordida": (c_mordida, 1.1, False, 0.0),
    # lote 2A (17/11)
    "Trote": (c_trote, T_TRO, True, V_TRO),
    "Partida": (c_partida, DUR_ARR, False, 0.0),
    "Freada": (c_freada, DUR_FRE, False, 0.0),
    "VirarE": (c_virar(1), T_AND, True, 0.0),
    "VirarD": (c_virar(-1), T_AND, True, 0.0),
    "Salto": (c_salto, 1.5, False, 0.0),
    # lote 2B (17/11)
    "Alerta": (c_alerta, 2.4, False, 0.0),
    "Observar": (c_observar, 4.4, False, 0.0),
    "ReacaoGolpe": (c_reacao, 1.0, False, 0.0),
    "Deitar": (c_deitar, DUR_DEITAR, False, 0.0),
    "Descanso": (c_descanso, 6.0, True, 0.0),
    "Levantar": (c_levantar, DUR_LEVANTAR, False, 0.0),
}
# ------------------------------------------------------------------ LOTE 3 (18/11): ataques em CAMADA (atacar andando) + poderes v6.2
# Pedido do usuario: morder e dar garrada andando/correndo (PvP sem ficar parado). Solucao: clipes de CAMADA que so tocam os ossos
# do ataque (mascara); no jogo tocam com prioridade Action por cima de Andar/Trote/Corrida, que continuam nas outras partes.
# Poderes (REFERENCIAS_PODERES_E_EFEITOS v6.2 §4h, kit e elemento unico PENDENTES de confirmacao): Chamas Triplices e Furia (com
# Rugido Infernal) em camada das 3 cabecas; Investida Sombria de corpo inteiro (locomocao). Valores de tempo = [A TESTAR].
CADEIA = {kk: ["Pescoco%s1" % kk, "Pescoco%s2" % kk, "Cabeca" + kk, "Mandibula" + kk] for kk in CABS}
PERNA_D = {sd: ["Escapula" + sd, "Braco" + sd, "Antebraco" + sd, "Mao" + sd, "Dedos" + sd] for sd in "ED"}
CABECAS3 = CADEIA["C"] + CADEIA["E"] + CADEIA["D"]
NEUTRO = {}                                                  # pose local das pernas dianteiras no Repouso (calculada antes dos clipes)
def o_mordida(kk):
    """mordida rapida de UMA cabeca (ataque basico em movimento): recolhe/abre -> bote -> volta; contato em 0,30 s"""
    def f(t):
        r = {}; a = suave(t / 0.20); b = suave((t - 0.20) / 0.10); c = suave((t - 0.38) / 0.42)
        r["Pescoco%s1" % kk] = [(S[kk], R(8) * a * (1 - b) - R(14) * b * (1 - c))]
        r["Pescoco%s2" % kk] = [(S[kk], R(4) * a * (1 - b) - R(6) * b * (1 - c))]
        r["Cabeca" + kk] = [(S[kk], R(7) * a * (1 - b) - R(4) * b * (1 - c))]
        r["Mandibula" + kk] = [(S[kk], -R(38) * a * (1 - b) - R(3) * b * (1 - c))]
        return r, {}
    return f
def o_garra(sd):
    """garrada da dianteira 'sd' (ataque basico em movimento): ergue e dobra -> golpe a frente e para dentro -> volta ao apoio
    do Repouso; contato em 0,32 s. A perna sai do IK so durante o clipe."""
    s_in = 1 if sd == "E" else -1                           # para dentro (E = -X)
    def f(t):
        r = {}; a = suave(t / 0.18) * (1 - suave((t - 0.18) / 0.14)); b = suave((t - 0.18) / 0.14) * (1 - suave((t - 0.34) / 0.41))
        # r2: pata sempre um pouco erguida (o corpo desce no Trote/Corrida) e golpe sem enterrar as garras
        r["Escapula" + sd] = [(X, R(8) * (a + b) + R(3))]
        r["Braco" + sd] = [(X, R(38) * a + R(48) * b + R(6)), (Z, -R(12) * s_in * b)]
        r["Antebraco" + sd] = [(X, -R(70) * a - R(18) * b - R(22))]
        r["Mao" + sd] = [(X, -R(30) * a + R(6) * b - R(10))]
        r["Dedos" + sd] = [(X, R(4) * b)]
        return r, {"ik_off": ["Mao" + sd], "neutro": {nm: NEUTRO[nm] for nm in PERNA_D[sd]}}
    return f
EV_CHAMAS = {"preparo": 0.0, "disparo_E": 0.45, "disparo_C": 0.70, "disparo_D": 0.95, "recuperacao": 1.10, "fim": 1.6}
def o_chamas(t):
    """Chamas Triplices: as tres cabecas miram (laterais giram para a frente), abrem em sequencia E -> C -> D (0,25 s [A TESTAR])
    com bote curto e recuo; uma cabeca por vez fica de boca bem aberta no seu disparo"""
    r = {}; mira = janela(t, 0.0, 1.6, 0.30, 0.45)
    for kk, yaw in (("E", 14.0), ("C", 0.0), ("D", -18.0)):
        td = EV_CHAMAS["disparo_" + kk]
        abre = suave((t - (td - 0.12)) / 0.10) * (1 - suave((t - (td + 0.08)) / 0.22))
        bote = suave((t - (td - 0.03)) / 0.05) * (1 - suave((t - (td + 0.05)) / 0.20)); recuo = janela(t, td + 0.05, td + 0.35, 0.06, 0.2)
        r["Pescoco%s1" % kk] = [(S[kk], R(6) * mira - R(9) * bote + R(4) * recuo), (Z, R(yaw) * mira)]
        r["Pescoco%s2" % kk] = [(S[kk], R(3) * mira)]
        r["Cabeca" + kk] = [(S[kk], -R(3) * mira + R(6) * bote)]
        r["Mandibula" + kk] = [(S[kk], -R(5) * mira - R(34) * abre)]
    return r, {}
FURIA_T = 2.0
EV_FURIA_LOOP = {"contato_C": 0.30, "contato_E": 0.95, "contato_D": 1.55}
def furia_pose(t, r=None):
    """postura de furia (loop 2,0 s): cabecas baixas e a frente, rosnando; cada uma morde no seu tempo (ataques desencontrados)"""
    r = {} if r is None else r; t = t % FURIA_T
    for kk, yaw in (("C", 0.0), ("E", 8.0), ("D", -10.0)):
        tb = EV_FURIA_LOOP["contato_" + kk]
        a = janela(t, tb - 0.16, tb + 0.02, 0.10, 0.04); b = janela(t, tb - 0.02, tb + 0.28, 0.04, 0.24)
        tremor = R(1.2) * math.sin(2 * math.pi * 6 * t + {"C": 0, "E": 2, "D": 4}[kk])     # 12 ciclos em 2 s: fecha o loop
        r["Pescoco%s1" % kk] = [(S[kk], -R(8) + R(7) * a - R(12) * b), (Z, R(yaw))]
        r["Pescoco%s2" % kk] = [(S[kk], -R(3) + R(3) * a - R(4) * b)]
        r["Cabeca" + kk] = [(S[kk], R(4) + R(5) * a - R(3) * b + tremor)]
        r["Mandibula" + kk] = [(S[kk], -R(8) - R(28) * a + R(5) * b)]
    return r
def o_furia_loop(t): return furia_pose(t), {}
EV_RUGIDO = {"rugido_C": 0.15, "rugido_E": 0.40, "rugido_D": 0.65, "entra_furia": 1.6}
def o_rugido(t):
    """Rugido Infernal (ativacao da Furia): cada cabeca ergue e ruge de boca escancarada, uma por vez (C -> E -> D), e todas
    terminam na postura de furia (quadro 0 do FuriaLoop)"""
    kf = suave((t - 1.05) / 0.55); base = furia_pose(0.0); r = {}
    for kk in CABS:
        s0 = EV_RUGIDO["rugido_" + kk]; env = janela(t, s0, s0 + 0.75, 0.12, 0.30)
        sacode = R(2.5) * math.sin(2 * math.pi * 9 * (t - s0)) * env
        def mistura(nm, extra):
            r[nm] = [(e, ang * kf) for e, ang in base[nm]] + extra
        mistura("Pescoco%s1" % kk, [(S[kk], R(14) * env)]); mistura("Pescoco%s2" % kk, [(S[kk], R(4) * env)])
        mistura("Cabeca" + kk, [(S[kk], -R(10) * env), (Z, sacode)]); mistura("Mandibula" + kk, [(S[kk], -R(42) * env)])
    return r, {}
def o_furia_saida(t):
    k = 1 - suave(t / 0.8); base = furia_pose(0.0)
    return {nm: [(e, ang * k) for e, ang in eixos] for nm, eixos in base.items()}, {}
def camada_sobre(o_fn, mascara, base_fn, base_T=None, t0=0.0, dur_o=None, base_com_altura=True, extras=()):
    """amostra de previa: base (Andar/Corrida/Repouso) + camada (substitui SO os ossos da mascara, como a prioridade Action do
    Roblox). extras = [(o_fn, mascara, t0, dur)] para encadear camadas (Rugido -> Loop -> Saida)."""
    def f(t):
        tb = t % base_T if base_T else t
        r, raiz, pes, ext = base_fn(tb)
        if not base_com_altura: raiz = raiz + V((0, 0, BASE_Z))
        for fo, msk, t_0, du in [(o_fn, mascara, t0, dur_o)] + list(extras):
            if t_0 <= t <= t_0 + du:
                ro, eo = fo(t - t_0)
                for nm in msk: r[nm] = ro.get(nm, [])
                for k_ in eo.get("ik_off", []):
                    ext.setdefault("ik_off", []).append(k_); ext.setdefault("apoio", {})[k_] = False
                ext.setdefault("neutro", {}).update(eo.get("neutro", {}))
        return r, raiz, pes, ext
    return f
def so_camada(o_fn, mascara):
    """clipe de camada exportado: Repouso parado + camada (o JSON leva so os ossos da mascara)"""
    return camada_sobre(o_fn, mascara, lambda t: c_repouso(0.0), None, 0.0, 99.0, False)
# Investida Sombria: compressao nos apoios -> impulso (~0,5 s, ~11 studs na velocidade do galope) -> encaixe no quadro 0 da Corrida.
# NO LUGAR: o deslocamento (impulso e +40% de velocidade por 4 s) e do jogo; o clipe so atua.
T0_INV = 0.30; DUR_INV = T0_INV + 2 * T_GAL
def k_inv(t): return suave((t - T0_INV) / 0.22)        # r2: rampa um pouco mais longa (escorregao 0,5)
PERF_INV = Perfil(lambda t: V_GAL * k_inv(t)); PERF_INV_G = PerfDesloc(PERF_INV, T0_INV)
EV_INVESTIDA = {"compressao": 0.0, "impulso": T0_INV, "fim_impulso": round(T0_INV + 0.5, 3), "passa_corrida": round(T0_INV + 0.5, 3), "encaixa_corrida": round(DUR_INV, 3)}
def c_investida(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}, "v": V_GAL * k_inv(t)}; k = k_inv(t); tt = t - T0_INV
    comp = suave(t / 0.22) * (1 - suave((t - 0.26) / 0.10))          # compressao: corpo desce sobre as quatro patas
    imp = janela(t, T0_INV - 0.04, T0_INV + 0.5, 0.08, 0.25)          # impulso: corpo estica e as cabecas avancam baixas
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(tt, fase, T_GAL, AP_GAL, ALT_GAL * k, lambda x: L_GAL * k_inv(x + T0_INV), PERF_INV_G)
        rot_sola(ext, k_, uu if k > 0.02 else 0.0, 32); ext["apoio"][k_] = uu == 0
    corpo_galope(r, tt / T_GAL, k)
    r["Pelve"] = r["Pelve"] + [(X, R(7) * comp - R(4) * imp)]; r["Coluna2"] = r["Coluna2"] + [(X, -R(3) * imp)]
    r["Coluna3"] = r["Coluna3"] + [(X, -R(5) * comp + R(3) * imp)]
    for kk, at in (("C", 0.0), ("E", 0.03), ("D", 0.05)):
        ik_ = janela(t - at, T0_INV - 0.04, T0_INV + 0.5, 0.08, 0.25)
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], -R(10) * comp - R(10) * ik_)]; r["Cabeca" + kk] = r["Cabeca" + kk] + [(S[kk], R(8) * ik_)]
    r["Cauda1"] = r["Cauda1"] + [(X, R(8) * imp)]
    z = BASE_Z + (Z_GAL - BASE_Z) * k + 0.30 * k * math.sin(2 * math.pi * (tt / T_GAL - 0.05)) - 0.70 * comp - 0.25 * imp
    return r, V((0, 0.30 * comp, z)), pes, ext
CAMADA = {}                                                  # nome -> mascara (JSON so com estes ossos)
for kk in CABS: CAMADA["Mordida" + kk] = CADEIA[kk]
for sd in "ED": CAMADA["Garra" + sd] = PERNA_D[sd]
CAMADA.update({"ChamasTriplices": CABECAS3, "FuriaRugido": CABECAS3, "FuriaLoop": CABECAS3, "FuriaSaida": CABECAS3})
O_FN = {**{"Mordida" + kk: o_mordida(kk) for kk in CABS}, **{"Garra" + sd: o_garra(sd) for sd in "ED"},
        "ChamasTriplices": o_chamas, "FuriaRugido": o_rugido, "FuriaLoop": o_furia_loop, "FuriaSaida": o_furia_saida}
DUR_O = {**{"Mordida" + kk: 0.8 for kk in CABS}, **{"Garra" + sd: 0.75 for sd in "ED"},
         "ChamasTriplices": 1.6, "FuriaRugido": 1.6, "FuriaLoop": FURIA_T, "FuriaSaida": 0.8}
for nm_, msk in CAMADA.items():
    CLIPES[nm_] = (so_camada(O_FN[nm_], msk), DUR_O[nm_], nm_ == "FuriaLoop", 0.0)
CLIPES["Investida"] = (c_investida, DUR_INV, False, 0.0)
# Investida r3 (18/11, pedido "revisao das tres habilidades"): MAIS ACAO, versao NOVA (a Investida aceita fica intacta).
# Patas fincando (dedos agarram o chao), peito comprimindo fundo entre as dianteiras, cabecas baixando com atraso, extensao
# marcada no impulso (coluna estica, garupa empurra, cabecas e cauda em linha) e recuperacao da passada ao entrar no galope.
# NO LUGAR: o deslocamento do jogo continua separado do clipe.
T0_R3 = 0.40; DUR_R3 = T0_R3 + 2 * T_GAL                    # 44 quadros exatos: o fim cai na fase da Corrida (0,38 dava 7 graus de salto)
def k_inv3(t): return suave((t - T0_R3) / 0.20)
PERF_R3 = Perfil(lambda t: V_GAL * k_inv3(t)); PERF_R3_G = PerfDesloc(PERF_R3, T0_R3)
EV_INVESTIDA_R3 = {"compressao": 0.0, "patas_fincadas": 0.18, "impulso": T0_R3, "extensao_max": round(T0_R3 + 0.18, 3),
                   "fim_impulso": round(T0_R3 + 0.5, 3), "passa_corrida": round(T0_R3 + 0.5, 3), "encaixa_corrida": round(DUR_R3, 3)}
def c_investida_r3(t):
    r = {}; pes = {}; ext_ = {"rot_pe": {}, "apoio": {}, "v": V_GAL * k_inv3(t)}; k = k_inv3(t); tt = t - T0_R3
    comp = suave(t / 0.30) * (1 - suave((t - (T0_R3 - 0.04)) / 0.09))        # compressao funda
    estica = janela(t, T0_R3 - 0.04, T0_R3 + 0.50, 0.10, 0.30)                  # extensao do impulso
    finca = janela(t, 0.08, T0_R3 + 0.02, 0.10, 0.06)                           # dedos agarram o chao
    for k_, fase in FASE_GALOPE.items():
        pes[k_], uu = passo_var(tt, fase, T_GAL, AP_GAL, ALT_GAL * k, lambda x: L_GAL * k_inv3(x + T0_R3), PERF_R3_G)
        rot_sola(ext_, k_, uu if k > 0.02 else 0.0, 32); ext_["apoio"][k_] = uu == 0
    corpo_galope(r, tt / T_GAL, k)
    r["Pelve"] = r["Pelve"] + [(X, R(11) * comp - R(6) * estica)]          # r2: extensao mais contida (alcance)
    r["Coluna1"] = r["Coluna1"] + [(X, -R(3) * comp + R(2) * estica)]    # r3: extensao pela garupa (girar a coluna erguia a frente)
    r["Coluna2"] = r["Coluna2"] + [(X, -R(2) * comp + R(1) * estica)]
    r["Coluna3"] = r["Coluna3"] + [(X, -R(7) * comp + R(2) * estica)]      # peito afunda entre as dianteiras (r2: sobe pouco na extensao)
    for sd in "ED":
                r["Dedos" + sd] = [(X, -R(6) * finca)]; r["DedosPe" + sd] = [(X, -R(5) * finca)]       # r2: flexao leve (14 graus enterrava)
    for kk, at in (("C", 0.0), ("E", 0.05), ("D", 0.09)):                      # cabecas baixam com atraso entre si
        cmp_k = suave((t - at) / 0.30) * (1 - suave((t - (T0_R3 - 0.04 + at)) / 0.09))
        est_k = janela(t - at, T0_R3 - 0.04, T0_R3 + 0.50, 0.10, 0.30)
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], -R(13) * cmp_k - R(15) * est_k)]
        r["Pescoco%s2" % kk] = r.get("Pescoco%s2" % kk, []) + [(S[kk], -R(4) * est_k)]
        r["Cabeca" + kk] = r["Cabeca" + kk] + [(S[kk], R(6) * cmp_k + R(10) * est_k)]
        r["Mandibula" + kk] = r.get("Mandibula" + kk, []) + [(S[kk], -R(10) * est_k)]     # soma a boca do galope (substituir quebrava o encaixe)
    r["Cauda1"] = r["Cauda1"] + [(X, -R(8) * comp + R(14) * estica)]; r["Cauda2"] = r["Cauda2"] + [(X, R(6) * estica)]
    z = BASE_Z + (Z_GAL - BASE_Z) * k + 0.30 * k * math.sin(2 * math.pi * (tt / T_GAL - 0.05)) - 1.05 * comp - 0.25 * estica
    return r, V((0, 0.25 * comp - 0.10 * estica, z)), pes, ext_
CLIPES["InvestidaR3"] = (c_investida_r3, DUR_R3, False, 0.0)
# Rugido Infernal r4 (18/11, pedido "r4 do Rugido Infernal"): ATIVACAO separada das mordidas (o FuriaRugido aceito fica intacto).
# Cada cabeca, uma por vez (C -> E -> D, sem sobrepor as aberturas): pescoco e focinho ERGUEM (sem bote para a frente), a
# mandibula ABRE devagar, SUSTENTA aberta e FECHA com controle; depois a cabeca baixa para a postura de furia (quadro 0 do
# FuriaLoop). Corpo inteiro: apoios firmes (patas paradas), peito expande (inspira antes de cada rugido), peso um pouco para
# tras, cauda erguida; o corpo termina no Repouso q0. As mordidas desencontradas so comecam no FuriaLoop, depois do fim.
RUG4_INI = {"C": 0.10, "E": 0.80, "D": 1.50}                 # inicio de cada cabeca (s) [A TESTAR]
RUG4_ERGUE, RUG4_ABRE0, RUG4_ABRE1, RUG4_FECHA0, RUG4_FECHA1, RUG4_ASSENTA = 0.32, 0.16, 0.42, 0.80, 1.08, 1.30
DUR_RUG4 = round(RUG4_INI["D"] + RUG4_ASSENTA + 0.10, 4)     # 2,90 s = 87 quadros
EV_RUGIDO_R4 = {"inspira": 0.0}
for kk in CABS:
    s0 = RUG4_INI[kk]
    EV_RUGIDO_R4.update({"ergue_" + kk: s0, "rugido_" + kk: round(s0 + RUG4_ABRE0, 3), "boca_max_" + kk: round(s0 + RUG4_ABRE1, 3),
                         "fecha_" + kk: round(s0 + RUG4_FECHA0, 3), "fechada_" + kk: round(s0 + RUG4_FECHA1, 3)})
EV_RUGIDO_R4["entra_furia"] = DUR_RUG4
def o_rugido_r4(t):
    base = furia_pose(0.0); r = {}
    for kk in CABS:
        u = t - RUG4_INI[kk]
        antecip = janela(u, -0.35, 0.05, 0.25, 0.10) * suave(t / 0.20)            # recolhe de leve (inspira); parte do Repouso q0
        ergue = suave(u / RUG4_ERGUE) * (1 - suave((u - RUG4_FECHA0) / (RUG4_ASSENTA - RUG4_FECHA0)))
        abre = suave((u - RUG4_ABRE0) / (RUG4_ABRE1 - RUG4_ABRE0)) * (1 - suave((u - RUG4_FECHA0) / (RUG4_FECHA1 - RUG4_FECHA0)))
        kf = suave((u - (RUG4_FECHA0 + 0.05)) / (RUG4_ASSENTA - RUG4_FECHA0 - 0.05))   # assenta na postura de furia
        sust = janela(u, RUG4_ABRE1 - 0.05, RUG4_FECHA0 + 0.05, 0.08, 0.10)
        vibra = R(1.3) * math.sin(2 * math.pi * 8 * u) * sust                        # vibracao curta do rugido (sem chicote)
        def mistura(nm, extra):
            r[nm] = [(e, ang * kf) for e, ang in base[nm]] + extra
        gira = {"C": 0.0, "E": 12.0, "D": -14.0}[kk]                                  # laterais viram um pouco para a frente (boca legivel)
        mistura("Pescoco%s1" % kk, [(S[kk], R(20) * ergue + R(3) * antecip), (Z, R(gira) * ergue)])
        mistura("Pescoco%s2" % kk, [(S[kk], R(9) * ergue)])
        mistura("Cabeca" + kk, [(S[kk], -R(18) * ergue - R(4) * abre + vibra)])
        mistura("Mandibula" + kk, [(S[kk], -R(56) * abre)])                       # r4b: abertura mais larga (46 lia pouco)
    return r, {}
def c_rugido_r4(t):
    """corpo inteiro: Repouso q0 + peito expandindo + apoios firmes + cabecas do o_rugido_r4"""
    r, raiz, pes, ext = c_repouso(0.0)
    env = janela(t, 0.0, DUR_RUG4, 0.40, 0.55)
    pulso = sum(janela(t - RUG4_INI[kk], -0.30, RUG4_FECHA1, 0.30, 0.35) for kk in CABS)   # inspira e sustenta em cada rugido
    pulso = min(pulso, 1.0) * suave(t / 0.30)                                  # parte do Repouso q0
    r["Coluna3"] = r["Coluna3"] + [(X, R(4) * env + R(3) * pulso)]                 # peito sobe e expande
    r["Coluna2"] = r["Coluna2"] + [(X, R(1.5) * env + R(1.0) * pulso)]
    r["Coluna1"] = r["Coluna1"] + [(X, -R(1.0) * env)]
    r["Pelve"] = [(X, -R(2.0) * env)]                                                # garupa assenta (peso para tras)
    r["Cauda1"] = r["Cauda1"] + [(X, R(10) * env)]; r["Cauda2"] = r["Cauda2"] + [(X, R(4) * env)]
    ro, _ = o_rugido_r4(t)
    r.update(ro)
    return r, raiz + V((0, 0.22 * env, 0.12 * env + 0.06 * pulso)), {}, {}
CLIPES["FuriaRugidoR4"] = (c_rugido_r4, DUR_RUG4, False, 0.0)
CAMADA["FuriaRugidoR4Camada"] = CABECAS3                       # variante em CAMADA (cabecas) para usar andando [PROPOSTA]
CLIPES["FuriaRugidoR4Camada"] = (so_camada(o_rugido_r4, CABECAS3), DUR_RUG4, False, 0.0)
# Bola Infernal (18/11, ideia do usuario; SUBSTITUI as Chamas Triplices; nome PROVISORIO): as tres cabecas CONVERGEM para um
# ponto a frente, abrem as bocas e alimentam UMA bola de fogo gigante (carga), dao um bote juntas no lancamento e recuam.
# CAMADA das cabecas (usa andando/correndo). A bola segue o alvo no jogo (teleguiada, valores [A TESTAR]).
DUR_BOLA = 2.2
EV_BOLA = {"converge": 0.0, "carga_inicio": 0.35, "carga_max": 1.20, "disparo": 1.30, "recuperacao": 1.55, "fim": DUR_BOLA}
def o_bola(t):
    r = {}; conv = janela(t, 0.0, DUR_BOLA, 0.35, 0.55)
    abre = suave((t - 0.30) / 0.35) * (1 - suave((t - 1.32) / 0.28))
    treme = janela(t, 0.50, 1.30, 0.20, 0.05)
    bote = suave((t - 1.22) / 0.08) * (1 - suave((t - 1.36) / 0.30)); recuo = janela(t, 1.34, 1.95, 0.08, 0.45)
    for kk, yaw, at in (("C", 0.0, 0.0), ("E", 22.0, 0.04), ("D", -24.0, 0.08)):
        vib = R(1.4) * math.sin(2 * math.pi * 7 * (t + at)) * treme              # esforco de sustentar a bola
        r["Pescoco%s1" % kk] = [(S[kk], -R(4) * conv - R(10) * bote + R(6) * recuo), (Z, R(yaw) * conv)]
        r["Pescoco%s2" % kk] = [(S[kk], R(2) * conv)]
        r["Cabeca" + kk] = [(S[kk], -R(2) * conv + R(5) * bote + vib), (Z, R(yaw * 0.35) * conv)]
        r["Mandibula" + kk] = [(S[kk], -R(6) * conv - R(38) * abre)]
    return r, {}
CAMADA["BolaInfernal"] = CABECAS3
CLIPES["BolaInfernal"] = (so_camada(o_bola, CABECAS3), DUR_BOLA, False, 0.0)
# Bola Infernal r2 (18/11, pedido "mais brilhante, maior ... as tres cabecas abrem a boca rugindo e forma uma bola gigante"):
# as tres cabecas ERGUEM e olham para CIMA, abrem a boca RUGINDO e sustentam (carga longa); a bola gigante forma ACIMA e a
# frente delas; no fim erguem mais um pouco (preparo) e ARREMESSAM juntas para baixo/frente; boca fecha com controle.
# Corpo inteiro (apoios firmes, peito expandindo) + variante em CAMADA para usar andando [PROPOSTA].
DUR_BOLA2 = 4.3
EV_BOLA2 = {"ergue": 0.0, "rugido": 0.40, "carga_inicio": 0.50, "carga_max": 3.00, "preparo": 3.00, "disparo": 3.35,
            "recuperacao": 3.55, "fim": DUR_BOLA2}
def o_bola2(t):
    r = {}
    for kk, yaw, at in (("C", 0.0, 0.0), ("E", 9.0, 0.06), ("D", -10.0, 0.10)):
        u = t - at
        ergue = suave(u / 0.55) * (1 - suave((u - 3.28) / 0.22))                   # sobe e olha para a bola
        prep = janela(u, 2.95, 3.32, 0.30, 0.06)                                     # erguem mais (preparo)
        arr = suave((u - 3.26) / 0.10) * (1 - suave((u - 3.42) / 0.75))             # arremesso para baixo/frente
        abre = suave((u - 0.32) / 0.40) * (1 - suave((u - 3.46) / 0.45))             # abre rugindo, fecha com controle
        sust = janela(u, 0.70, 3.30, 0.15, 0.10)
        vib = R(1.8) * math.sin(2 * math.pi * 9 * u) * sust * (0.6 + 0.4 * math.sin(2 * math.pi * 0.7 * u))   # rugido sustentado
        r["Pescoco%s1" % kk] = [(S[kk], R(32) * ergue + R(6) * prep - R(18) * arr), (Z, R(yaw) * (ergue + arr))]
        r["Pescoco%s2" % kk] = [(S[kk], R(8) * ergue + R(3) * prep - R(6) * arr)]
        r["Cabeca" + kk] = [(S[kk], -R(30) * ergue - R(6) * prep + R(16) * arr + vib), (Z, R(yaw * 0.4) * ergue)]
        r["Mandibula" + kk] = [(S[kk], -R(58) * abre)]
    return r, {}
def c_bola2(t):
    """corpo inteiro: Repouso q0 + peito expandindo (inspira e sustenta) + apoios firmes + arremesso leve do tronco"""
    r, raiz, pes, ext = c_repouso(0.0)
    env = janela(t, 0.0, DUR_BOLA2, 0.45, 0.70)
    arr = suave((t - 3.28) / 0.10) * (1 - suave((t - 3.45) / 0.70))
    r["Coluna3"] = r["Coluna3"] + [(X, R(5) * env - R(4) * arr)]
    r["Coluna2"] = r["Coluna2"] + [(X, R(1.5) * env - R(1.5) * arr)]
    r["Coluna1"] = r["Coluna1"] + [(X, -R(1.0) * env)]
    r["Pelve"] = [(X, -R(2.5) * env)]
    r["Cauda1"] = r["Cauda1"] + [(X, R(12) * env)]; r["Cauda2"] = r["Cauda2"] + [(X, R(5) * env)]
    ro, _ = o_bola2(t)
    r.update(ro)
    return r, raiz + V((0, 0.20 * env - 0.25 * arr, 0.14 * env - 0.10 * arr)), {}, {}
CLIPES["BolaInfernalR2"] = (c_bola2, DUR_BOLA2, False, 0.0)
CAMADA["BolaInfernalR2Camada"] = CABECAS3
CLIPES["BolaInfernalR2Camada"] = (so_camada(o_bola2, CABECAS3), DUR_BOLA2, False, 0.0)
def _base_bola2(t):
    r, raiz, pes, ext = c_bola2(min(t, DUR_BOLA2)); return r, raiz + V((0, 0, BASE_Z)), pes, ext
def _base_rug4(t):
    r, raiz, pes, ext = c_rugido_r4(min(t, DUR_RUG4)); return r, raiz + V((0, 0, BASE_Z)), pes, ext
PREVIA = {  # nome: (funcao, duracao) -- so para render/QA (acao assada, sem JSON)
    "Prev_Bola_Repouso": (camada_sobre(o_bola, CABECAS3, c_repouso, 6.0, 0.2, DUR_BOLA, False), 3.0),
    "Prev_Bola_Andar": (camada_sobre(o_bola, CABECAS3, c_andar, T_AND, 0.2, DUR_BOLA), 3 * T_AND),
    "Prev_Bola2": (camada_sobre(o_bola2, CABECAS3, _base_bola2, None, 0.0, DUR_BOLA2), DUR_BOLA2 + 0.7),
    "Prev_Bola2_Andar": (camada_sobre(o_bola2, CABECAS3, c_andar, T_AND, 0.2, DUR_BOLA2), 5 * T_AND),
    "Prev_FuriaR4": (camada_sobre(o_furia_loop, CABECAS3, _base_rug4, None, DUR_RUG4, 2 * FURIA_T, True,
                                  [(o_furia_saida, CABECAS3, DUR_RUG4 + 2 * FURIA_T, 0.8)]), DUR_RUG4 + 2 * FURIA_T + 0.8),
    "Prev_MordidaC_Andar": (camada_sobre(O_FN["MordidaC"], CADEIA["C"], c_andar, T_AND, 0.6, 0.8), 2 * T_AND),
    "Prev_MordidaE_Corrida": (camada_sobre(O_FN["MordidaE"], CADEIA["E"], c_corrida, T_GAL, 0.2, 0.8), 3 * T_GAL),
    "Prev_GarraE_Andar": (camada_sobre(O_FN["GarraE"], PERNA_D["E"], c_andar, T_AND, 0.5, 0.75), 2 * T_AND),
    "Prev_GarraD_Trote": (camada_sobre(O_FN["GarraD"], PERNA_D["D"], c_trote, T_TRO, 0.3, 0.75), 3 * T_TRO),
    "Prev_Chamas_Repouso": (camada_sobre(O_FN["ChamasTriplices"], CABECAS3, c_repouso, 6.0, 0.2, 1.6, False), 2.0),
    "Prev_Chamas_Andar": (camada_sobre(O_FN["ChamasTriplices"], CABECAS3, c_andar, T_AND, 0.2, 1.6), 2 * T_AND),
    "Prev_Furia_Andar": (camada_sobre(O_FN["FuriaRugido"], CABECAS3, c_andar, T_AND, 0.0, 1.6, True,
                                      [(o_furia_loop, CABECAS3, 1.6, FURIA_T), (o_furia_saida, CABECAS3, 1.6 + FURIA_T, 0.8)]), 4 * T_AND),
}
V_PREV = {"Prev_MordidaC_Andar": V_AND, "Prev_MordidaE_Corrida": V_GAL, "Prev_GarraE_Andar": V_AND, "Prev_GarraD_Trote": V_TRO,
          "Prev_Chamas_Repouso": 0.0, "Prev_Chamas_Andar": V_AND, "Prev_Furia_Andar": V_AND, "Prev_FuriaR4": 0.0, "Prev_Bola_Repouso": 0.0, "Prev_Bola_Andar": V_AND, "Prev_Bola2": 0.0, "Prev_Bola2_Andar": V_AND}      # r2: QA de escorregao com o chao da base
for nm_, (fn_, du_) in PREVIA.items(): CLIPES[nm_] = (fn_, du_, False, V_PREV[nm_])
EVENTOS_L3 = {**{"Mordida" + kk: {"contato": 0.30, "fim": 0.8} for kk in CABS}, **{"Garra" + sd: {"contato": 0.32, "fim": 0.75} for sd in "ED"},
              "ChamasTriplices": EV_CHAMAS, "FuriaRugido": EV_RUGIDO, "FuriaLoop": EV_FURIA_LOOP, "FuriaSaida": {"fim": 0.8},
              "Investida": EV_INVESTIDA, "InvestidaR3": EV_INVESTIDA_R3, "Prev_Furia_Andar": {"rugido": 0.0, "loop": 1.6, "saida": 3.6},
              "FuriaRugidoR4": EV_RUGIDO_R4, "FuriaRugidoR4Camada": EV_RUGIDO_R4,
              "BolaInfernal": EV_BOLA, "BolaInfernalR2": EV_BOLA2, "BolaInfernalR2Camada": EV_BOLA2, "Prev_FuriaR4": {"rugido": 0.0, "loop": DUR_RUG4, "saida": round(DUR_RUG4 + 2 * FURIA_T, 3)}}
INFO_EVENTOS = {"ChamasTriplices": {"disparo_E": {"cabeca": "E", "osso_boca": "CabecaE", "mandibula": "MandibulaE"},
                                    "disparo_C": {"cabeca": "C", "osso_boca": "CabecaC", "mandibula": "MandibulaC"},
                                    "disparo_D": {"cabeca": "D", "osso_boca": "CabecaD", "mandibula": "MandibulaD"}},
                "FuriaLoop": {"contato_" + kk: {"cabeca": kk} for kk in CABS}, "FuriaRugido": {"rugido_" + kk: {"cabeca": kk} for kk in CABS},
                "FuriaRugidoR4": {"rugido_" + kk: {"cabeca": kk, "som": "rugido", "vfx": "violeta"} for kk in CABS},
                "BolaInfernal": {"carga_inicio": {"bocas": "CED", "osso_boca": ["CabecaC", "CabecaE", "CabecaD"]}, "disparo": {"origem": "bola a frente das tres bocas"}},
                "BolaInfernalR2": {"carga_inicio": {"bocas": "CED", "osso_boca": ["CabecaC", "CabecaE", "CabecaD"]}, "disparo": {"origem": "bola gigante acima e a frente das tres bocas"}},
                "BolaInfernalR2Camada": {"carga_inicio": {"bocas": "CED"}, "disparo": {"origem": "bola gigante acima e a frente das tres bocas"}},
                "FuriaRugidoR4Camada": {"rugido_" + kk: {"cabeca": kk, "som": "rugido", "vfx": "violeta"} for kk in CABS}}
PONTO_BOCA = {}                                              # ponto da boca no espaco LOCAL do osso Cabeca{K} (para o projetil/VFX)
for kk in CABS:
    p_ = (BD["Cabeca" + kk].tail_local * 0.6 + BD["Mandibula" + kk].tail_local * 0.4)
    PONTO_BOCA[kk] = [round(c_, 4) for c_ in (BD["Cabeca" + kk].matrix_local.inverted() @ p_)]
EVENTOS_CLIPE = {"Mordida": EV_MORD, **EVENTOS_LOTE2, **EVENTOS_L3}
COM_ALTURA_PROPRIA = {"Andar", "Corrida", "Trote", "Partida", "Freada", "VirarE", "VirarD", "Salto", "Deitar", "Descanso", "Levantar", "Investida", "InvestidaR3"} | set(CAMADA) | set(PREVIA)
QUAIS = ARGS[1].split(",") if len(ARGS) > 1 else list(CLIPES)

# ------------------------------------------------------------------ amostragem -> FK -> acao + JSON + QA
REG_IDX = {}
for o in MALHAS[:2]:
    nomes = {g.index: g.name for g in o.vertex_groups}; pat, out_ = [], []
    for v in o.data.vertices:
        if not v.groups: continue
        nm = nomes[max(v.groups, key=lambda g: g.weight).group]
        (pat if nm.startswith(("Mao", "Dedos", "Pe", "DedosPe")) and not nm.startswith(("Pelve", "Pescoco")) else out_).append(v.index)
    REG_IDX[o.name] = {"pata": np.array(pat, dtype=np.int64), "resto": np.array(out_, dtype=np.int64)}
def regioes_zmin():
    dg = bpy.context.evaluated_depsgraph_get(); zm = {"pata": 99.0, "resto": 99.0}
    for o in MALHAS[:2]:
        ev = o.evaluated_get(dg); m = ev.to_mesh(); c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); c = c.reshape(-1, 3)
        for k, idx in REG_IDX[o.name].items():
            if len(idx): zm[k] = min(zm[k], float(c[idx, 2].min()))
        ev.to_mesh_clear()
    return zm
def aplicar(nome, fn, t):
    zerar(); rots, raiz, pes, ext = fn(t)
    if nome not in COM_ALTURA_PROPRIA: raiz = raiz + V((0, 0, BASE_Z))
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
    for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
    for k, d in pes.items(): ALVO[k].location = REP[k] + d
    for k, a_ in ext.get("rot_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
    for k, g_ in ext.get("giro_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(Z, g_) @ ALVO[k].rotation_quaternion   # virar: guinada da pata apoiada
    for k, q_ in ext.get("rot_q", {}).items(): ALVO[k].rotation_quaternion = q_ @ ROT0[k]           # 2B: osso Mao/Pe deitado (gira na ponta)
    for k in ext.get("ik_off", []): PB[PATAS[k][1]].constraints["IK"].mute = True; PB[k].constraints["Copy Rotation"].mute = True   # L3: garra
    for nm, N in ext.get("neutro", {}).items(): PB[nm].rotation_quaternion = PB[nm].rotation_quaternion @ N   # L3: sobre a perna do Repouso
    bpy.context.view_layer.update()
    return rots, raiz, pes, ext
def calibrar_deitado():
    """2B: acha a descida da Raiz em que o corpo deitado (fora das patas) toca o chao: z min entre -0,10 e 0"""
    lo_, hi_ = -9.0, 0.0
    for _ in range(14):
        m_ = (lo_ + hi_) / 2; DEITADO["z"] = m_; aplicar("Descanso", lambda t: c_descanso(0.75), 0.0)   # t com respiracao ~0
        zr = regioes_zmin()
        if zr["resto"] < -0.10: lo_ = m_                          # abaixo do chao: sobe (patas sao conferidas a parte)
        else: hi_ = m_                                              # ainda acima: desce
    lo_ = hi_; DEITADO["z"] = hi_; aplicar("Descanso", lambda t: c_descanso(0.75), 0.0)
    print("DEITADO_Z calibrado", round(lo_, 3), {k: round(v, 3) for k, v in regioes_zmin().items()}, flush=True)
if any(n in QUAIS for n in ("Deitar", "Descanso", "Levantar")): calibrar_deitado()
aplicar("Repouso", c_repouso, 0.0)                           # L3: pose local das dianteiras no Repouso (neutro da garra)
for sd in "ED":
    for nm in PERNA_D[sd]: NEUTRO[nm] = arm.convert_space(pose_bone=PB[nm], matrix=PB[nm].matrix, from_space="POSE", to_space="LOCAL").to_quaternion()
def folga_cabecas():
    """L3: menor distancia entre pontos das cabecas/mandibulas/pescocos de cabecas diferentes (colisao de dentes, labios, pescocos)"""
    pts = {}
    for kk in CABS:
        h, tl, mt = PB["Cabeca" + kk].head, PB["Cabeca" + kk].tail, PB["Mandibula" + kk].tail
        pts[kk] = [h.lerp(tl, i / 4) for i in range(5)] + [PB["Mandibula" + kk].head.lerp(mt, i / 2) for i in range(3)] + \
                  [PB["Pescoco%s2" % kk].head.lerp(PB["Pescoco%s2" % kk].tail, i / 2) for i in range(3)]
    return min((p - q).length for a_, b_ in (("C", "E"), ("C", "D"), ("E", "D")) for p in pts[a_] for q in pts[b_])
manifesto = {}; QUADROS = {}
for nome in QUAIS:
    fn, dur, loop, vel = CLIPES[nome]
    nq = int(round(dur * FPS)) + (0 if loop else 1)
    quadros = []; folga = 99.0; erro_ik = 0.0; erro_ar = 0.0; pior_ik = None; pior_desl = None; zr_min = {"pata": 99.0, "resto": 99.0}; PATA_PT = {k: [] for k in PATAS}
    for qi in range(nq):
        t = qi / FPS
        rots, raiz, pes, ext = aplicar(nome, fn, t)
        pose = {pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in PB}
        folga = min(folga, folga_cabecas())
        for k in PATAS:
            if k in ext.get("ik_off", []): PATA_PT[k].append((PB[k].tail.copy(), False, 0.0, 0.0)); continue
            e_ = (PB[k].head - ALVO[k].location).length
            if ext.get("no_ar", {}).get(k): erro_ar = max(erro_ar, e_); continue
            if e_ > erro_ik: erro_ik = e_; pior_ik = (k, qi)
            PATA_PT[k].append((PB[k].tail.copy(), ext.get("apoio", {}).get(k, False), ext.get("v", vel), ext.get("w", 0.0)))   # ponto de apoio = fim do osso Mao/Pe
        zr = regioes_zmin(); zr_min = {k: min(zr_min[k], zr[k]) for k in zr}
        quadros.append(pose)
    # escorregao: no apoio a pata deve correr para tras exatamente com o chao (+Y a v studs/s); medido entre quadros de apoio seguidos
    desl = 0.0
    # 2A: chao com velocidade variavel (v do quadro) e giro (w): o ponto apoiado gira -w/FPS em torno do pivo da Raiz
    PIVO_QA = BD["Raiz"].head_local.copy()
    for k, seq in PATA_PT.items():
        for i_, ((p0, a0, v0, w0), (p1, a1, v1, w1)) in enumerate(zip(seq, seq[1:])):
            if a0 and a1:
                vm, wm = (v0 + v1) / 2, (w0 + w1) / 2; rr = p0 - PIVO_QA
                esp = V((0, vm / FPS, 0)) + (Matrix.Rotation(-wm / FPS, 3, Z) @ rr - rr)
                d_ = ((p1 - p0) - esp).length * FPS
                if d_ > desl: desl = d_; pior_desl = (k, i_)
    manifesto[nome] = {"duracao_s": round(dur, 4), "loop": loop, "quadros": nq, "fps": FPS, "velocidade_studs_s_PARAMETRO": round(vel, 2),
                       "erro_ik_max": round(erro_ik, 4), "pior_ik_pata_quadro": pior_ik, "erro_ik_no_ar": round(erro_ar, 3), "desliza_pata_max_studs_s": round(desl, 3), "pior_desliza_pata_quadro": pior_desl,
                       "pata_min_z": round(zr_min["pata"], 3), "malha_min_z_fora_das_patas": round(zr_min["resto"], 3), "folga_cabecas_min": round(folga, 3)}
    if nome in CAMADA: manifesto[nome].update({"camada": True, "mascara": CAMADA[nome], "prioridade_sugerida": "Action"})
    if nome in PREVIA: manifesto[nome]["previa_so_render"] = True
    if nome in INFO_EVENTOS: manifesto[nome]["eventos_info"] = INFO_EVENTOS[nome]
    if nome in ("ChamasTriplices", "BolaInfernal", "BolaInfernalR2", "BolaInfernalR2Camada"): manifesto[nome]["ponto_boca_local_Cabeca"] = PONTO_BOCA
    if nome in EVENTOS_CLIPE: manifesto[nome]["eventos_s"] = EVENTOS_CLIPE[nome]
    print("CLIPE", nome, manifesto[nome], flush=True)
    dado = {"nome": "Cerbero_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel, 3), "ossos": {}}
    if nome in EVENTOS_CLIPE: dado["eventos"] = EVENTOS_CLIPE[nome]
    if nome in CAMADA:                                       # L3: so a mascara + pais com peso 0 (montar a arvore de Poses)
        dado.update({"camada": True, "prioridade_sugerida": "Action", "mascara": CAMADA[nome]})
        pais = []
        for nm in CAMADA[nome]:
            b_ = BD[nm].parent
            while b_ is not None and b_.name not in CAMADA[nome]:
                if b_.name not in pais: pais.append(b_.name)
                b_ = b_.parent
        dado["pais_peso0"] = pais
    if nome in INFO_EVENTOS: dado["eventos_info"] = INFO_EVENTOS[nome]
    if nome in ("ChamasTriplices", "BolaInfernal", "BolaInfernalR2", "BolaInfernalR2Camada"): dado["ponto_boca_local_Cabeca"] = PONTO_BOCA
    for pb in PB:
        if nome in CAMADA and pb.name not in CAMADA[nome]: continue
        seq = []
        for pose in quadros:
            m = pose[pb.name]; q = m.to_quaternion(); tt = m.translation
            seq += [round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(tt.x, 5), round(tt.y, 5), round(tt.z, 5)]
        dado["ossos"][pb.name] = seq
    if nome not in PREVIA:
        with open(os.path.join(OUT, "Cerbero_%s.json" % nome), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    QUADROS[nome] = quadros
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
for nome, quadros in QUADROS.items():
    act = bpy.data.actions.get("Cerbero_" + nome) or bpy.data.actions.new("Cerbero_" + nome); arm.animation_data.action = act
    act["loop"] = CLIPES[nome][2]; act["velocidade_PARAMETRO"] = CLIPES[nome][3]
    for qi, pose in enumerate(quadros):
        for pb in PB:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    if nome in EVENTOS_CLIPE:
        for ev, ts in EVENTOS_CLIPE[nome].items(): act.pose_markers.new(ev).frame = int(round(ts * FPS)) + 1
    act.use_fake_user = True
arm.animation_data.action = None; zerar()
for pb in PB:
    for c in pb.constraints: c.mute = False
ant = {}
mp = os.path.join(OUT, "manifesto_clipes.json")
if os.path.exists(mp) and len(QUAIS) < len(CLIPES): ant = json.load(open(mp, encoding="utf-8"))
ant.update(manifesto); json.dump(ant, open(mp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Anim.blend"))
print("ANIM_OK", list(QUADROS))
