"""Clipes do Javali Silvestre (rig piloto de 30 ossos aprovado 13/11, rig/CR_Javali_Rig.blend). LOTE A: base de locomocao.
Mecanismo adaptado do gerador do Cervo-do-Bosque (Cervo_do_Bosque_Ref/rig/clipes_cervo.py: IK das 4 patas com alvo no boleto,
casco apoiado amarrado ao deslocamento S(t), Quartela copiando o alvo, QA de IK/escorregao/casco/emenda e JSON por clipe);
poses e parametros sao PROPRIOS do javali (massa no pescoco/ombros, pescoco curto, passos curtos, focinho estavel).
NO LUGAR: a Raiz nao avanca; o jogo move o modelo na velocidade gravada (velocidade_PROPOSTA / v_perfil).
Clipes: Repouso, Andar, VirarE, VirarD, ParadoParaAndar (entra no quadro 0 do Andar), AndarParaParado (sai do quadro 0 do
Andar e termina no quadro 0 do Repouso). Velocidades, passadas, giro e duracoes sao PROPOSTA (parametro tecnico, nao regra).
Uso: blender -b rig/CR_Javali_Rig.blend -P rig/clipes_javali.py -- <saida_dir> [lista,de,clipes]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
for o in [o for o in sc.objects if o.type in ("CAMERA", "LIGHT")]: bpy.data.objects.remove(o)
arm = bpy.data.objects["Javali_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
CORPO = bpy.data.objects["Javali_Corpo"]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def onda(t, T, fase=0.0): return math.sin(2 * math.pi * (t / T + fase))
def pulso(t, T, t0, dur):
    f = ((t - t0) % T) / dur
    return math.sin(math.pi * f) ** 2 if f < 1 else 0.0
def janela(t, a, b, sub=0.2, des=0.2): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
R = math.radians; X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
# ------------------------------------------------------------------ IK (alvo no boleto = cabeca da Quartela)
PATAS = {"QuartelaE": ("dian", "CanelaE", "AntebracoE"), "QuartelaD": ("dian", "CanelaD", "AntebracoD"),
         "QuartelaTrasE": ("tras", "CanelaTrasE", "PernaE"), "QuartelaTrasD": ("tras", "CanelaTrasD", "PernaD")}
ALVO, POLO, REP = {}, {}, {}
for pb in PB: pb.rotation_mode = "QUATERNION"
for pe, (par, fim, meio) in PATAS.items():
    a_ = bpy.data.objects.new("IK_" + pe, None); sc.collection.objects.link(a_); a_.location = BD[pe].head_local.copy()
    a_.rotation_mode = "QUATERNION"; a_.rotation_quaternion = BD[pe].matrix_local.to_quaternion()
    j = BD[meio].tail_local; p_ = bpy.data.objects.new("Polo_" + pe, None); sc.collection.objects.link(p_)
    p_.location = j + V((0, -0.25 if par == "dian" else 0.25, 0))          # carpo para a frente; jarrete para tras
    c = PB[fim].constraints.new("IK"); c.target = a_; c.pole_target = p_; c.chain_count = 3; c.use_stretch = False
    cr = PB[pe].constraints.new("COPY_ROTATION"); cr.target = a_
    ALVO[pe], POLO[pe], REP[pe] = a_, p_, a_.location.copy()
ROT0 = {k: o.rotation_quaternion.copy() for k, o in ALVO.items()}; POLO_REP = {k: o.location.copy() for k, o in POLO.items()}
bpy.context.view_layer.update()
for pe, (par, fim, meio) in PATAS.items():                            # angulo de polo que reproduz o repouso
    c = PB[fim].constraints["IK"]; topo = BD[meio].parent.name
    alvo_j = [BD[topo].tail_local.copy(), BD[meio].tail_local.copy()]
    def erro(a_):
        c.pole_angle = a_; bpy.context.view_layer.update(); return (PB[topo].tail - alvo_j[0]).length + (PB[meio].tail - alvo_j[1]).length
    melhor = min((erro(R(g)), R(g)) for g in range(-180, 180, 5))[1]
    for passo_ in (2.5, 1.0, 0.25): melhor = min((erro(melhor + R(d)), melhor + R(d)) for d in (-passo_, 0, passo_))[1]
    c.pole_angle = melhor; print("POLO", pe, round(math.degrees(melhor), 2), "erro", round(erro(melhor), 4))
def rot_mundo(nome, eixos):
    r = BD[nome].matrix_local.to_3x3(); q = Matrix.Identity(3)
    for eixo, ang in eixos: q = Matrix.Rotation(ang, 3, eixo) @ q
    return (r.inverted() @ q @ r).to_quaternion()
def zerar():
    for pb in PB:
        pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
        for c_ in pb.constraints: c_.influence = 1.0            # lote D: pernas em FK desligam o IK por quadro
    for k, o in ALVO.items(): o.location = REP[k].copy(); o.rotation_quaternion = ROT0[k].copy()
    for k, o in POLO.items(): o.location = POLO_REP[k].copy()
# ------------------------------------------------------------------ locomocao
class Perfil:
    """S(t) = integral de v: o casco apoiado recua exatamente o que o corpo avanca (nao escorrega)"""
    def __init__(self, vfun, t0=-3.0, t1=12.0, dt=1 / 600):
        self.t0, self.dt = t0, dt; n = int((t1 - t0) / dt) + 1; acc = 0.0; self.S = []
        for i in range(n): self.S.append(acc); acc += vfun(t0 + i * dt) * dt
    def s(self, t):
        x = (t - self.t0) / self.dt; i = max(0, min(len(self.S) - 2, int(x))); return self.S[i] + (self.S[i + 1] - self.S[i]) * (x - i)
def passo(t, fase, T, apoio, alt, Lf, perf):
    """casco no tempo t: apoio (preso ao chao) ou balanco (arco). Lf(tc) = passada do passo que comecou em tc (pode variar).
    Altura do balanco proporcional ao trecho a percorrer (passo minusculo = pata quase nao sobe; parada sem arrastar)."""
    phi = t / T + fase; n_ = math.floor(phi); f = phi - n_; tc = (n_ - fase) * T
    if f < apoio: return Y * (-Lf(tc) / 2 + perf.s(t) - perf.s(tc)), 0.0, 1.0
    tl = tc + apoio * T; y0 = -Lf(tc) / 2 + perf.s(tl) - perf.s(tc); y1 = -Lf(tc + T) / 2
    u = (f - apoio) / (1 - apoio); s = suave(u); fa = min(1.0, abs(y1 - y0) / 0.12)
    if abs(y1 - y0) < 0.003: return Y * (y0 + perf.s(t) - perf.s(tl)), 0.0, 1.0   # passo nulo: a pata segue plantada no chao
    return Y * (y0 + (y1 - y0) * s) + V((0, 0, alt * fa * math.sin(math.pi * u) ** 0.8)), u, fa
BASE_Z = -0.012                                    # corpo levemente baixo nos clipes em pe (folga da dianteira)
# andar de javali [PROPOSTA]: ciclo 0,9 s, passada curta 0,26 u, apoio 65%, casco sobe pouco (pata curta, perto do corpo)
T_AND, L_AND, AP_AND, ALT_AND = 0.9, 0.26, 0.65, 0.045
V_AND = L_AND / (AP_AND * T_AND); PERF_AND = Perfil(lambda t: V_AND)
FASE_ANDAR = {"QuartelaTrasE": 0.0, "QuartelaE": 0.25, "QuartelaTrasD": 0.5, "QuartelaD": 0.75}   # quatro tempos, sequencia lateral
def rola_casco(u):
    """no balanco a pinca dobra (boleto flexiona) e volta plana antes do pouso"""
    return R(35) * math.sin(math.pi * min(1.0, u * 1.15)) ** 1.6 if u > 0 else 0.0   # sai devagar do chao (sem estalo na decolagem)
def orelhas(r, t, T, base=0.0):
    """orelhas pequenas e eretas: giros curtos e independentes, pouca amplitude"""
    e = pulso(t, T, 0.6, 0.45) - 0.6 * pulso(t, T, 3.1, 0.35) + 0.8 * pulso(t, T, 5.7, 0.4)
    d = pulso(t, T, 1.9, 0.4) + 0.7 * pulso(t, T, 4.3, 0.4) - 0.5 * pulso(t, T, 6.9, 0.35)
    r["OrelhaE"] = [(Z, R(-14) * e), (X, R(4) * e + base)]; r["OrelhaD"] = [(Z, R(14) * d), (X, R(4) * d + base)]
# ------------------------------------------------------------------ clipes: t -> (rots, raiz, pes, ext)
T_REP = 8.0
def c_repouso(t):
    """quatro cascos plantados; cabeca baixa; respiracao nas costelas (4 por laco); orelhas e cauda como secundario"""
    T = T_REP; r = {}; b = onda(t, 2.0); b2 = onda(t, 2.0, 0.3); peso = onda(t, T); fare = pulso(t, T, 3.0, 1.4)
    r["Coluna1"] = [(X, R(0.5) * b)]; r["Coluna2"] = [(X, R(-0.7) * b)]; r["Coluna3"] = [(X, R(0.4) * b2)]
    r["Pelve"] = [(Y, R(0.8) * peso)]                                                          # peso troca de traseira devagar
    olha = onda(t, T, 0.1)
    r["Pescoco"] = [(X, R(7) - R(0.5) * b + R(3) * fare), (Z, R(3) * olha)]                   # cabeca baixa; baixa um pouco mais 1x (fareja o ar/chao)
    r["Pescoco2"] = [(X, R(3)), (Z, R(2) * onda(t, T, 0.2))]
    r["Cabeca"] = [(X, R(0.8) * b2 - R(1.5) * fare), (Z, R(2.5) * onda(t, T, 0.27))]
    orelhas(r, t, T)
    sac = pulso(t, T, 5.6, 0.45); osc = math.sin(6 * math.pi * ((t - 5.6) % T) / 0.45)
    r["Cauda1"] = [(X, R(2) * b2 - R(10) * sac), (Z, R(16) * sac * osc)]; r["Cauda2"] = [(Z, R(12) * sac * math.sin(6 * math.pi * ((t - 5.65) % T) / 0.45))]
    return r, V((0.003 * peso, 0, 0.002 * b)), {}, {}
def corpo_andar(t, u, k=1.0):
    """tronco do andar: pelve/ombros balancam discretos; focinho estavel (pescoco compensa a cernelha)"""
    r = {}; sw = math.sin(2 * math.pi * u); bob = math.cos(4 * math.pi * u)
    r["Pelve"] = [(Y, R(2.0) * sw * k), (Z, R(1.2) * sw * k)]
    r["Coluna1"] = [(Y, R(-0.8) * sw * k)]
    r["Coluna2"] = [(Y, R(-0.6) * sw * k), (Z, R(-0.8) * sw * k)]
    r["Coluna3"] = [(Y, R(1.6) * math.sin(2 * math.pi * (u + 0.25)) * k), (X, R(0.5) * bob * k)]
    acen = math.cos(4 * math.pi * (u - 0.25 - 0.05))
    r["Pescoco"] = [(X, R(4) + R(1.2) * acen * k), (Z, R(-1.2) * math.sin(2 * math.pi * (u + 0.25)) * k)]   # cabeca baixa de javali
    r["Pescoco2"] = [(X, R(2) + R(0.5) * acen * k)]
    r["Cabeca"] = [(X, R(-1.4) * acen * k), (Z, R(-0.6) * math.sin(2 * math.pi * (u + 0.3)) * k)]
    for lado in "ED":                                                                         # escapula acompanha a dianteira
        r["Escapula" + lado] = [(X, R(4) * math.cos(2 * math.pi * ((u + FASE_ANDAR["Quartela" + lado]) % 1.0)) * k)]
    r["Cauda1"] = [(X, R(-4) * k), (Z, R(5) * math.sin(2 * math.pi * (u - 0.15)) * k)]; r["Cauda2"] = [(Z, R(7) * math.sin(2 * math.pi * (u - 0.3)) * k)]
    orelhas(r, t % (8 * T_AND), 8 * T_AND)
    return r, V((0.003 * sw * k, 0, (-0.003 + 0.004 * bob) * k))
# centro da faixa de apoio [PROPOSTA]: dianteiras apoiam um pouco a frente do repouso (no fim do apoio a pata ficava esticada no
# limite do IK e o antebraco saltava ~40 graus num quadro ao levantar). kc(t) liga/desliga o deslocamento nas transicoes.
CENTRO = {"QuartelaE": -0.035, "QuartelaD": -0.035, "QuartelaTrasE": -0.01, "QuartelaTrasD": -0.01}
def pernas(t, ext, pes, Lf, perf, alt=ALT_AND, kc=None):
    for k_, fase in FASE_ANDAR.items():
        d, uu, fa = passo(t, fase, T_AND, AP_AND, alt, Lf, perf); c_ = 1.0
        if kc:                                       # centro do passo: fixo no apoio, migra no balanco (casco apoiado nao escorrega)
            phi = t / T_AND + fase; tc = (math.floor(phi) - fase) * T_AND; c_ = kc(tc) if uu == 0 else kc(tc) + (kc(tc + T_AND) - kc(tc)) * suave(uu)
        pes[k_] = d + V((0, CENTRO[k_] * c_, 0)); ext["rot_pe"][k_] = rola_casco(uu) * fa; ext["apoio"][k_] = uu == 0
def c_andar(t):
    pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    pernas(t, ext, pes, lambda _x: L_AND, PERF_AND); r, raiz = corpo_andar(t, t / T_AND)
    return r, raiz, pes, ext
GIRO_GS = 25.0; GIRO = R(GIRO_GS)                 # curva: 25 graus/s a ~0,44 u/s = raio ~1,0 u (PROPOSTA)
PIVO = BD["Raiz"].head_local.copy()
def c_virar(sinal):
    """andando em curva: o jogo gira o modelo a sinal*GIRO em torno da Raiz e o desloca a V_AND. Casco apoiado = ponto fixo
    no mundo (arco em torno do centro instantaneo de rotacao); os cascos em balanco se reposicionam na direcao da curva."""
    w = GIRO * sinal; T, ap = T_AND, AP_AND
    ICR = PIVO + V((V_AND / w, 0, 0))
    def no_arco(k_, ang):
        b_ = REP[k_] + V((0, CENTRO[k_], 0)); p_ = b_ - ICR; c_, s_ = math.cos(ang), math.sin(ang)
        return V((ICR.x + p_.x * c_ - p_.y * s_, ICR.y + p_.x * s_ + p_.y * c_, REP[k_].z)) - REP[k_]
    def f(t):
        pes = {}; ext = {"rot_pe": {}, "apoio": {}, "giro_pe": {}}
        for k_, fase in FASE_ANDAR.items():
            phi = t / T + fase; n_ = math.floor(phi); fr = phi - n_; tc = (n_ - fase) * T; tm = tc + ap * T / 2; meia = w * ap * T / 2
            if fr < ap:
                pes[k_] = no_arco(k_, -w * (t - tm)); uu = 0.0; ext["giro_pe"][k_] = -w * (t - tm)
            else:
                uu = (fr - ap) / (1 - ap); p0 = no_arco(k_, -meia); p1 = no_arco(k_, meia)
                ext["giro_pe"][k_] = -meia + 2 * meia * suave(uu)
                pes[k_] = p0.lerp(p1, suave(uu)) + V((0, 0, ALT_AND * math.sin(math.pi * uu) ** 0.8))
            ext["rot_pe"][k_] = rola_casco(uu); ext["apoio"][k_] = uu == 0
        r, raiz = corpo_andar(t, t / T); raiz = raiz + V((0, 0, -0.003))
        r["Pescoco"] = r["Pescoco"] + [(Z, R(9) * sinal)]; r["Pescoco2"] = r["Pescoco2"] + [(Z, R(4) * sinal)]   # cabeca entra antes
        r["Cabeca"] = r["Cabeca"] + [(Z, R(6) * sinal)]
        r["Coluna2"] = r["Coluna2"] + [(Z, R(3) * sinal)]; r["Pelve"] = r["Pelve"] + [(Z, R(-4) * sinal), (Y, R(2) * sinal)]
        r["Coluna3"] = r["Coluna3"] + [(Y, R(2.5) * sinal)]                          # inclina para dentro da curva
        r["Cauda1"] = r["Cauda1"] + [(Z, R(-8) * sinal)]
        return r, raiz, pes, ext
    return f
# ------------------------------------------------------------------ transicoes parado <-> andar
def mistura(rA, rB, w):
    r = {}
    for n_ in set(rA) | set(rB): r[n_] = [(e, a * (1 - w)) for e, a in rA.get(n_, [])] + [(e, a * w) for e, a in rB.get(n_, [])]
    return r
T0_PA = 0.40                                         # preparo: transfere o peso antes de soltar a primeira pata
DUR_PA = T0_PA + 2 * T_AND                           # rampa de 1 ciclo + 1 ciclo cheio: termina no quadro 0 do Andar
def k_pa(t): return suave((t - T0_PA) / T_AND)
PERF_PA = Perfil(lambda tt: V_AND * k_pa(tt + T0_PA))
def c_parado_para_andar(t):
    tt = t - T0_PA; pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    pernas(tt, ext, pes, lambda x: L_AND * k_pa(x + T0_PA), PERF_PA, kc=lambda x: k_pa(x + T0_PA))
    w = suave(t / (T0_PA + 0.6 * T_AND)); kb = k_pa(t)
    rA, zA, _p, _e = c_repouso(0.0); rB, zB = corpo_andar(tt - 2 * T_AND, tt / T_AND, kb)   # orelhas: fim = quadro 0 do Andar
    r = mistura(rA, rB, w)
    # preparo: o peso vai para a diagonal que fica (a 1a pata a soltar e a traseira E): pelve e raiz para a direita/frente
    pr = janela(t, 0.0, T0_PA + 0.35 * T_AND, 0.30, 0.25)
    r["Pelve"] = r.get("Pelve", []) + [(Y, R(-2.0) * pr)]; r["Coluna3"] = r.get("Coluna3", []) + [(X, R(-1.0) * pr)]
    r["Pescoco"] = r.get("Pescoco", []) + [(X, R(-2.5) * pr)]                     # ergue um pouco o focinho ao decidir sair
    return r, zA.lerp(zB, w) + V((-0.006 * pr, -0.004 * pr, 0)), pes, ext
T_DES = T_AND                                        # desacelera em 1 ciclo; depois os cascos acertam e assentam
T_ESP = 0.25 * T_AND                                 # a pata que ja esta no ar no quadro 0 do Andar pousa normal (sem salto de pose)
DUR_AP = T_ESP + 2 * T_AND + 0.5
def k_ap(t): return 1 - suave((t - T_ESP) / T_DES)
PERF_AP = Perfil(lambda t: V_AND * k_ap(t))
def c_andar_para_parado(t):
    pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    pernas(t, ext, pes, lambda x: L_AND * k_ap(x), PERF_AP, kc=k_ap)
    w = suave((t - T_ESP - 0.35 * T_AND) / (DUR_AP - T_ESP - 0.35 * T_AND - 0.05))           # tronco vai para a pose do quadro 0 do Repouso
    rA, zA = corpo_andar(t, t / T_AND, k_ap(t) ** 0.5); rB, zB, _p, _e = c_repouso(0.0)
    r = mistura(rA, rB, w)
    fr = janela(t, T_ESP + 0.25 * T_AND, T_ESP + 1.6 * T_AND, 0.3, 0.45)                         # absorve: peso vai um pouco para as dianteiras
    r["Pelve"] = r.get("Pelve", []) + [(X, R(-1.5) * fr)]; r["Pescoco"] = r.get("Pescoco", []) + [(X, R(-2) * fr)]
    return r, zA.lerp(zB, w) + V((0, -0.004 * fr, -0.003 * fr)), pes, ext
# nome: (funcao, duracao, loop, velocidade [PROPOSTA], v(t) para QA, giro graus/s [PROPOSTA], entrada, saida)
CLIPES = {"Repouso": (c_repouso, T_REP, True, 0.0, None, 0.0, "laco", "laco"),
          "Andar": (c_andar, 8 * T_AND, True, V_AND, None, 0.0, "laco", "laco"),
          "VirarE": (c_virar(1), 8 * T_AND, True, V_AND, None, GIRO_GS, "laco (troca com Andar no quadro 0)", "laco"),
          "VirarD": (c_virar(-1), 8 * T_AND, True, V_AND, None, -GIRO_GS, "laco (troca com Andar no quadro 0)", "laco"),
          "ParadoParaAndar": (c_parado_para_andar, DUR_PA, False, 0.0, lambda t: V_AND * k_pa(t), 0.0, "Repouso q0", "Andar q0"),
          "AndarParaParado": (c_andar_para_parado, DUR_AP, False, 0.0, lambda t: V_AND * k_ap(t), 0.0, "Andar q0", "Repouso q0")}
if os.environ.get("JAVALI_LD"): os.environ["JAVALI_LC"] = os.environ["JAVALI_LB"] = "1"   # D usa o Alerta do C e o galope do B
if os.environ.get("JAVALI_LC"):                    # lote C (vida selvagem): so com a variavel; sem ela os lotes A/B nao mudam
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_javali_lc.py"), encoding="utf-8").read())
if os.environ.get("JAVALI_LB"):                    # lote B (trote, corrida, transicoes): so com a variavel; sem ela o lote A nao muda
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_javali_lb.py"), encoding="utf-8").read())
if os.environ.get("JAVALI_LD"):                    # lote D (defesa/derrota, ESTUDO; sem dano/hitbox): so com a variavel
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_javali_ld.py"), encoding="utf-8").read())
    if os.environ.get("JAVALI_LD_R2"):              # refino de peso do lote D (13/11): sobrescreve so os clipes refinados
        exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_javali_ld_r2.py"), encoding="utf-8").read())
        if os.environ.get("JAVALI_LE"):             # lote E (17/11): Chifrada no impacto da investida
            exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_javali_le.py"), encoding="utf-8").read())
QUAIS = ARGS[1].split(",") if len(ARGS) > 1 else list(CLIPES)
# ------------------------------------------------------------------ QA: cascos = vertices da pele com Quartela dominante e baixos
gr = {g.index: g.name for g in CORPO.vertex_groups}; CASCO_V = {k: [] for k in PATAS}
for v in CORPO.data.vertices:
    if v.co.z > 0.05: continue
    for g in v.groups:
        if gr[g.group] in CASCO_V and g.weight > 0.5: CASCO_V[gr[g.group]].append(v.index)
print("CASCOS vertices", {k: len(v) for k, v in CASCO_V.items()})
def cascos():
    dg = bpy.context.evaluated_depsgraph_get(); ev = CORPO.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); c = c.reshape(-1, 3); ev.to_mesh_clear()
    return {k: c[idx] for k, idx in CASCO_V.items()}
ALC_MAX = 0.965                                       # fracao do comprimento da cadeia (pata nunca chega a reta)
CADEIA_L = {k: BD[f].length + BD[m].length + BD[BD[m].parent.name].length for k, (_p, f, m) in PATAS.items()}
CLAMP_N = [0]; CLAMP_AP = [0]
CAB = bpy.data.objects["Javali_Cabeca"]
def cabeca_min_z():
    dg = bpy.context.evaluated_depsgraph_get(); ev = CAB.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear()
    return float(c.reshape(-1, 3)[:, 2].min()) + float(CAB.matrix_world.translation.z)
DIVISAO_PESCOCO = (("Pescoco", 0.6), ("Pescoco2", 0.3), ("Cabeca", 0.1))
def focinho_ao_chao(rots, zt, s_, eixo=None, maximo=80):
    """lote C: abaixa o pescoco (extra sobre a pose) ate o ponto mais baixo da cabeca (focinho/presas) ficar a altura
    z0 + (zt - z0) * s_, onde z0 = altura sem o extra. Bissecao no angulo; nada da cabeca atravessa o chao (zt >= 0)."""
    if s_ < 1e-3: ANG_LOG[0] = 0.0; return
    if CUR_Q[0] in ANG_FIX:                                       # 2a passada: angulo suavizado (sem saltos no pescoco)
        for nm, f in DIVISAO_PESCOCO: PB[nm].rotation_quaternion = rot_mundo(nm, rots.get(nm, []) + [(X, ANG_FIX[CUR_Q[0]] * f)])
        bpy.context.view_layer.update(); return
    bpy.context.view_layer.update(); z0 = cabeca_min_z(); alvo = z0 + (zt - z0) * s_
    def aplica(a_):
        for nm, f in DIVISAO_PESCOCO:
            PB[nm].rotation_quaternion = rot_mundo(nm, rots.get(nm, []) + [(eixo or X, a_ * f)])
        bpy.context.view_layer.update(); return cabeca_min_z()
    lo, hi = 0.0, R(maximo)
    for _ in range(16):
        m_ = (lo + hi) / 2
        if aplica(m_) > alvo: lo = m_
        else: hi = m_
    aplica(lo); ANG_LOG[0] = lo
ANG_LOG = [0.0]; ANG_FIX = {}; CUR_Q = [-1]
def suaviza_focinho(fn, nq):
    """1a passada: angulo exato por quadro. Quando o ponto mais baixo troca (disco do focinho <-> ponta da presa) o angulo salta.
    Filtro SEGURO: minimo numa janela de +-4 quadros (cabeca mais alta) e depois media de +-2 -> nunca abaixa alem do exato."""
    ANG_FIX.clear(); a = []
    for qi in range(nq): CUR_Q[0] = qi; pose_de(fn, qi / FPS); a.append(ANG_LOG[0])
    m = [min(a[max(0, i - 4):i + 5]) for i in range(nq)]
    for i in range(nq): ANG_FIX[i] = sum(m[max(0, i - 2):i + 3]) / len(m[max(0, i - 2):i + 3])
def pose_de(fn, t):
    zerar(); rots, raiz, pes, ext = fn(t); raiz = raiz + V((0, 0, BASE_Z))
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
    for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
    if ext.get("focinho"): focinho_ao_chao(rots, *ext["focinho"])
    FK = ext.get("fk_pernas")                                     # lote D: {osso da perna: [(eixo, ang)]} sobre a pose do Repouso q0
    if FK is not None:
        if not BASE_FK: BASE_FK.update({k: v.to_quaternion() for k, v in REF0["Repouso"].items()})
        for k, (_par, fim, meio) in PATAS.items():
            for c_ in list(PB[fim].constraints) + list(PB[k].constraints): c_.influence = 0.0
            for nm in (BD[meio].parent.name, meio, fim, k):
                PB[nm].rotation_quaternion = BASE_FK[nm] @ rot_mundo(nm, FK.get(nm, []))
    for k, d in pes.items(): ALVO[k].location = REP[k] + d
    for k, a_ in ext.get("rot_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
    for k, g_ in ext.get("giro_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(Z, g_) @ ALVO[k].rotation_quaternion
    bpy.context.view_layer.update()
    for k in (PATAS if FK is None else ()):   # alvo alem do alcance: a pata estica toda e o IK estala ao voltar (licao do cervo r2)
        topo = BD[PATAS[k][2]].parent.name; raiz_ = PB[topo].head; d_ = ALVO[k].location - raiz_; Lc = CADEIA_L[k] * ALC_MAX
        if d_.length > Lc:
            ALVO[k].location = raiz_ + d_.normalized() * Lc; CLAMP_N[0] += 1
            if ext.get("apoio", {}).get(k, True):
                CLAMP_AP[0] += 1                                                  # casco APOIADO puxado = casco sai do chao (evitar)
                if os.environ.get("JAVALI_DEBUG"): print("CLAMP_APOIO", k, round(t * FPS), round(d_.length / CADEIA_L[k], 3))
    bpy.context.view_layer.update()
    for _it in range(2 if FK is None else 0):                    # casco em balanco nunca abaixo do chao
        cs0 = cascos(); mexeu = False
        for k in PATAS:
            if ext.get("apoio", {}).get(k, True) or len(cs0[k]) == 0: continue
            zb = float(cs0[k][:, 2].min())
            if zb < 0.0: ALVO[k].location.z += -zb + 0.002; mexeu = True
        if not mexeu: break
        bpy.context.view_layer.update()
    if ext.get("nivelar"):                                       # lote D: inclina o corpo (Raiz em X) ate traseiras e dianteiras tocarem juntas
        f_n = ext["nivelar"]; base_r = rots.get("Raiz", [])
        def dif(p_):
            PB["Raiz"].rotation_quaternion = rot_mundo("Raiz", [(X, p_)] + base_r); bpy.context.view_layer.update()
            c_ = malha_coords(CORPO); return float(c_[V_TRAS, 2].min() - c_[V_DIAN, 2].min())
        lo, hi = R(-40), R(15)                                    # dif(lo) < 0 (garupa baixa) ... dif(hi) > 0
        for _ in range(14):
            m_ = (lo + hi) / 2
            if dif(m_) > 0: hi = m_
            else: lo = m_
        p_ = (lo + hi) / 2 * f_n; PB["Raiz"].rotation_quaternion = rot_mundo("Raiz", [(X, p_)] + base_r); bpy.context.view_layer.update()
    if ext.get("assentar"):                                      # lote D: o ponto mais baixo do corpo encosta no chao (sem flutuar/atravessar)
        f_ = ext["assentar"]
        for _it in range(2):
            mz = min(malha_min_z(o) for o in (CORPO, CAB)); raiz = raiz + V((0, 0, -mz * f_))
            PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz; bpy.context.view_layer.update()
        if ext.get("cabeca_chao"):                                # deitado: a cabeca desce ate apoiar (giro do pescoco para o lado do chao)
            zt_, s__, eixo_ = ext["cabeca_chao"]; focinho_ao_chao(rots, zt_, s__, eixo_, 70)
    return ext, {pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in PB}
BASE_FK = {}
_rest = np.array([v.co[:] for v in CORPO.data.vertices])
V_TRAS = np.where((_rest[:, 1] > 0.3) & (_rest[:, 2] < 0.10))[0]; V_DIAN = np.where((_rest[:, 1] < -0.1) & (_rest[:, 2] < 0.10))[0]
def malha_coords(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
def malha_min_z(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return float(c.reshape(-1, 3)[:, 2].min())
def dif_pose(a, b):
    return max(math.degrees(a[n].to_quaternion().rotation_difference(b[n].to_quaternion()).angle) for n in a), \
           max((a[n].translation - b[n].translation).length for n in a)
REF0 = {}
for nm_ in ("Repouso", "Andar", "Trote", "Corrida"):
    if nm_ in CLIPES: REF0[nm_] = pose_de(CLIPES[nm_][0], 0.0)[1]
for nm_, (fn_, t_) in globals().get("REF_EXTRA", {}).items(): REF0[nm_] = pose_de(fn_, t_)[1]
CUR_Q[0] = -1
manifesto = {}; QUADROS = {}; APOIOS = {}
for nome in QUAIS:
    fn, dur, loop, vel, vfun, giro, ent, sai = CLIPES[nome]; nq = int(round(dur * FPS)) + (0 if loop else 1)
    EXTENSAO = [0.0, 0]; CAB_Z = [9.0]; APO = []; quadros = []; erro_ik = 0.0; zmin = {k: 9.0 for k in PATAS}; desl = {k: 0.0 for k in PATAS}; prev = None; ERRO_PATA = {}; ap_prev = {}
    ANG_FIX.clear()
    if nome in globals().get("FOCINHO_SUAVE", ()): suaviza_focinho(fn, nq)
    for qi in range(nq + (1 if loop else 0)):
        t = qi / FPS; CUR_Q[0] = qi; ext, pose = pose_de(fn, t)
        if loop and qi == nq: pose_fim = pose; break
        for k in (PATAS if ext.get("fk_pernas") is None else ()):
            e_ = (PB[k].head - ALVO[k].location).length; erro_ik = max(erro_ik, e_)
            if e_ > ERRO_PATA.get(k, (0, 0))[0]: ERRO_PATA[k] = (round(e_, 4), qi)
        zc_ = cabeca_min_z(); CAB_Z[0] = min(CAB_Z[0], zc_)
        cs = cascos()
        _yf = [float(cs[k][:, 1].mean()) for k in ("QuartelaE", "QuartelaD") if len(cs[k])]; _yt = [float(cs[k][:, 1].mean()) for k in ("QuartelaTrasE", "QuartelaTrasD") if len(cs[k])]
        if _yf and _yt:                                               # maior extensao: distancia casco dianteiro mais a frente -> traseiro mais atras
            ext_ = max(_yt) - min(_yf)
            if ext_ > EXTENSAO[0]: EXTENSAO[:] = [ext_, qi]
        for k, c_ in cs.items():
            if len(c_) == 0: continue
            zmin[k] = min(zmin[k], float(c_[:, 2].min()))
            if prev is not None:
                apo = ext.get("apoio", {}).get(k, True)
                if apo and ap_prev.get(k, True):                        # escorregao NO MUNDO de casco apoiado
                    vq = (vfun(t - 0.5 / FPS) if vfun else vel); ang = math.radians(giro) / FPS
                    cw = c_ - np.array(PIVO); ca, sa = math.cos(ang), math.sin(ang)
                    cw = np.stack([cw[:, 0] * ca - cw[:, 1] * sa, cw[:, 0] * sa + cw[:, 1] * ca, cw[:, 2]], 1) + np.array(PIVO)
                    baixo = c_[:, 2] < 0.012; mov = (cw[baixo] - prev[k][baixo]); mov[:, 1] -= vq / FPS
                    desl[k] = max(desl[k], float(np.abs(mov[:, :2]).max()) if len(mov) else 0.0)
        prev = cs; ap_prev = dict(ext.get("apoio", {})); quadros.append(pose)
        APO.append({k: bool(ext.get("apoio", {}).get(k, True)) for k in PATAS})
    salto = (0.0, "", 0)
    for i_ in range(len(quadros) - 1 + (1 if loop else 0)):
        b_ = quadros[(i_ + 1) % len(quadros)] if not (loop and i_ == len(quadros) - 1) else pose_fim
        for n_ in quadros[i_]:
            a_ = math.degrees(quadros[i_][n_].to_quaternion().rotation_difference(b_[n_].to_quaternion()).angle)
            if a_ > salto[0]: salto = (round(a_, 2), n_, i_)
    m_ = {"maior_extensao_cascos_u_quadro": [round(EXTENSAO[0], 3), EXTENSAO[1]], "cabeca_z_min_cm": round(CAB_Z[0] * 100, 2), "alvos_limitados_pelo_alcance": CLAMP_N[0], "apoios_limitados_pelo_alcance": CLAMP_AP[0], "maior_giro_entre_quadros_graus_osso_quadro": salto, "duracao_s": round(dur, 4), "loop": loop, "quadros": nq, "velocidade_u_s_PROPOSTA": round(vel, 4), "giro_graus_s_PROPOSTA": giro,
          "entrada": ent, "saida": sai, "erro_ik_max": round(erro_ik, 4), "erro_ik_por_pata": ERRO_PATA,
          "casco_z_min": {k: round(v, 4) for k, v in zmin.items()}, "escorregao_casco_apoiado_max": {k: round(v, 4) for k, v in desl.items()}}
    if loop:
        m_["emenda_laco_graus"], m_["emenda_laco_transl"] = [round(x, 3) for x in dif_pose(quadros[0], pose_fim)]
        if vel: m_["avanco_por_ciclo_u"] = round(vel * T_AND, 4); m_["ciclo_s"] = T_AND
    else:
        m_["deslocamento_total_u"] = round(sum(0.5 * (vfun(q / FPS) + vfun((q + 1) / FPS)) / FPS for q in range(nq - 1)), 4)
        e0 = ent.split()[0]; s0 = sai.split()[0]
        m_["emenda_entrada_graus_transl"] = [round(x, 3) for x in dif_pose(REF0[e0], quadros[0])]
        m_["emenda_saida_graus_transl"] = [round(x, 3) for x in dif_pose(REF0[s0], quadros[-1])]
    manifesto[nome] = m_; print("CLIPE", nome, json.dumps(m_), flush=True); CLAMP_N[0] = 0; CLAMP_AP[0] = 0
    dado = {"nome": "Javali_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel, 4), "ossos": {}}
    dado["apoio"] = {k: [int(x[k]) for x in APO] for k in PATAS}; APOIOS[nome] = dado["apoio"]
    if vfun: dado["v_perfil"] = [round(vfun(q_ / FPS), 4) for q_ in range(nq)]
    for pb in PB:
        seq = []
        for pose in quadros:
            m = pose[pb.name]; q = m.to_quaternion(); tt = m.translation
            seq += [round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(tt.x, 5), round(tt.y, 5), round(tt.z, 5)]
        dado["ossos"][pb.name] = seq
    os.makedirs(os.path.join(OUT, "json"), exist_ok=True)
    with open(os.path.join(OUT, "json", "Javali_%s.json" % nome), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    QUADROS[nome] = quadros
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
for nome, quadros in QUADROS.items():
    act = bpy.data.actions.get("Javali_" + nome) or bpy.data.actions.new("Javali_" + nome); arm.animation_data.action = act
    act["apoio_json"] = json.dumps(APOIOS[nome]); act["loop"] = CLIPES[nome][2]; act["velocidade_PROPOSTA"] = CLIPES[nome][3]; act["giro_graus_s_PROPOSTA"] = CLIPES[nome][5]
    if CLIPES[nome][4]: act["v_perfil"] = [round(CLIPES[nome][4](q_ / FPS), 4) for q_ in range(len(quadros))]
    for qi, pose in enumerate(quadros):
        for pb in PB:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    act.use_fake_user = True
arm.animation_data.action = None; zerar()
for o in list(ALVO.values()) + list(POLO.values()): bpy.data.objects.remove(o)
for pb in PB:
    for c in list(pb.constraints): pb.constraints.remove(c)
json.dump(manifesto, open(os.path.join(OUT, "manifesto_clipes.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, os.environ.get("JAVALI_ANIM_ARQ", "Javali_Clipes_LA.blend"))); print("ANIM_OK", list(QUADROS))
