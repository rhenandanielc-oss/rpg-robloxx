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
def marcha(T, L, apoio, alt, fases, ginga, bob, flex=0.0, cab_estab=1.0, lado=V((0, 1, 0)), giro=0.0):
    def f(t):
        u = t / T; r = {}; pes = {}; ext = {"rot_pe": {}}
        for k, fase in fases.items():
            d, s = passo(u + fase, L, apoio, alt, lado if giro == 0 else giro_lado(k))
            pes[k] = d; ext["rot_pe"][k] = R(-25) * math.sin(math.pi * s) if s > 0 else 0.0      # sola rola no balanco
        sw = math.sin(2 * math.pi * u)
        if flex == 0:                                                       # andar: rolamento lateral e ginga
            r["Pelve"] = [(Y, R(ginga) * sw), (Z, R(ginga * 0.6) * sw)]
            r["Coluna2"] = [(Y, R(-ginga * 0.8) * sw), (Z, R(-ginga * 0.5) * sw)]
            r["Coluna3"] = [(Y, R(ginga * 0.6) * math.sin(2 * math.pi * (u + 0.25)))]
            r["Pescoco"] = [(Z, R(-ginga * 0.5) * sw), (X, R(2.5) * math.cos(4 * math.pi * u))]
            r["Cabeca"] = [(X, R(-2.5) * math.cos(4 * math.pi * u) * cab_estab)]
            for k in ("MaoE", "MaoD"):                                     # escapula acompanha a pata dianteira
                fs = (u + fases[k]) % 1.0
                r["Escapula" + k[-1]] = [(X, R(6) * math.cos(2 * math.pi * fs))]
            raiz = V((0.10 * sw, 0, -0.36 + bob * math.cos(4 * math.pi * u)))
        else:                                                               # galope: coluna flexiona/estende
            fl = math.sin(2 * math.pi * (u - 0.15))
            r["Pelve"] = [(X, R(flex) * fl)]; r["Coluna1"] = [(X, R(-flex * 0.6) * fl)]; r["Coluna2"] = [(X, R(-flex * 0.5) * fl)]
            r["Coluna3"] = [(X, R(flex * 0.3) * fl)]; r["Pescoco"] = [(X, R(flex * 0.5) * fl)]; r["Cabeca"] = [(X, R(flex * 0.25) * fl)]
            for k in ("MaoE", "MaoD"):
                fs = (u + fases[k]) % 1.0; r["Escapula" + k[-1]] = [(X, R(10) * math.cos(2 * math.pi * fs))]
            r["OrelhaE"] = [(X, R(-20))]; r["OrelhaD"] = [(X, R(-20))]
            raiz = V((0, 0, -0.55 + bob * math.sin(2 * math.pi * (u - 0.05))))
        r["Cauda1"] = [(Z, R(5) * sw)]
        return r, raiz, pes, ext
    return f
GIRO_W = {}
def giro_lado(k):
    """virar no lugar: o pe apoiado desliza tangente ao centro do corpo (o jogo gira o modelo)"""
    p = REP[k]; tg = V((-p.y, p.x, 0)).normalized(); return tg * GIRO_W["sinal"]
def c_virar(sinal):
    def f(t):
        GIRO_W["sinal"] = sinal
        r, raiz, pes, ext = marcha(1.2, 1.3, 0.62, 0.30, FASE_ANDAR, 2.0, 0.03, giro=1)(t)
        r["Pescoco"] = r.get("Pescoco", []) + [(Z, R(14) * sinal)]; r["Cabeca"] = r.get("Cabeca", []) + [(Z, R(8) * sinal)]
        r["Coluna2"] = r.get("Coluna2", []) + [(Z, R(6) * sinal)]; r["Pelve"] = r.get("Pelve", []) + [(Z, R(-5) * sinal)]
        return r, raiz, pes, ext
    return f
def c_arrancada(t):
    """parado -> agacha (antecipacao) -> impulso das traseiras -> 2 passadas de galope crescendo (no lugar)"""
    r = {}; pes = {}; ext = {"rot_pe": {}}
    ag = janela(t, 0.0, 0.42, 0.22, 0.12)
    if t < 0.36:
        r["Pelve"] = [(X, R(6) * ag)]; r["Coluna2"] = [(X, R(-4) * ag)]; r["Pescoco"] = [(X, R(8) * ag)]
        r["OrelhaE"] = [(X, R(-25) * ag)]; r["OrelhaD"] = [(X, R(-25) * ag)]
        return r, V((0, 0.25 * ag, -0.55 * ag)), pes, ext
    k = suave((t - 0.36) / 0.5)
    g = marcha(16 / 30, 3.4 * k, 0.40, 0.75 * k, FASE_GALOPE, 0, 0.22 * k, flex=9 * k)(t - 0.36)
    rr, raiz, pes, ext = g
    raiz = raiz + V((0, 0.25 * (1 - k), (0.55 - 0.55 * (1 - k) * (1 - suave((t - 0.36) / 0.15))) * 0 ))
    return rr, raiz, pes, ext
def c_frenagem(t):
    """galope -> patas dianteiras fincam a frente, corpo recua e senta o peso nas traseiras -> parado"""
    r = {}; pes = {}; k = suave(t / 0.35); s = janela(t, 0.25, 1.1, 0.2, 0.45)
    pes["MaoE"] = V((0, -0.9 * k, 0)) * (1 - suave((t - 0.75) / 0.3)); pes["MaoD"] = V((0, -0.75 * k, 0)) * (1 - suave((t - 0.8) / 0.3))
    pes["PeE"] = V((0, -0.8 * s, 0)); pes["PeD"] = V((0, -0.6 * s, 0))
    r["Pelve"] = [(X, R(-8) * s)]; r["Coluna2"] = [(X, R(4) * s)]; r["Pescoco"] = [(X, R(-8) * s)]; r["Cabeca"] = [(X, R(-6) * s)]
    r["OrelhaE"] = [(X, R(-15) * s)]; r["OrelhaD"] = [(X, R(-15) * s)]
    return r, V((0, 0.45 * s, -0.75 * s - 0.3 * k * (1 - s))), pes, {}
SENTADO = dict(raiz=V((0, 0.9, -2.2)), pelve=R(-24))
def pose_sentado(k, r, pes):
    r["Pelve"] = [(X, SENTADO["pelve"] * k)]; r["Coluna1"] = [(X, R(5) * k)]; r["Coluna2"] = [(X, R(9) * k)]
    r["Pescoco"] = [(X, R(10) * k)]; r["Cabeca"] = [(X, R(4) * k)]
    pes["MaoE"] = V((0.1 * k, 1.3 * k, 0)); pes["MaoD"] = V((-0.1 * k, 1.3 * k, 0))     # patas dianteiras recuam (apoio vertical)
    pes["PeE"] = V((0.15 * k, -1.1 * k, 0)); pes["PeD"] = V((-0.15 * k, -1.1 * k, 0))   # traseiras vao para a frente
    return SENTADO["raiz"] * k
def c_sentar(t):
    r = {}; pes = {}; k = suave(t / 1.3)
    raiz = pose_sentado(k, r, pes); r["Cauda1"] = [(X, R(-25) * k)]
    return r, raiz + V((0, 0, 0.12 * math.sin(math.pi * k))), pes, {}
def c_levantar_sentado(t):
    r, raiz, pes, ext = c_sentar(1.3 - t); return r, raiz, pes, ext
DEITADO_Z = -3.05                                    # recalibrado antes de amostrar (ver calibrar_deitado)
def pose_deitado(k, r, pes, ext):
    r["Pelve"] = [(X, R(-3) * k)]; r["Coluna3"] = [(X, R(-4) * k)]; r["Pescoco"] = [(X, R(-10) * k)]; r["Cabeca"] = [(X, R(14) * k)]
    pes["MaoE"] = V((0.15 * k, -2.2 * k, 0.0)); pes["MaoD"] = V((-0.15 * k, -2.2 * k, 0.0))           # bracos estendidos a frente
    pes["PeE"] = V((0.55 * k, -1.2 * k, 0.0)); pes["PeD"] = V((-0.55 * k, -1.2 * k, 0.0))             # traseiras dobradas por baixo
    ext["rot_pe"] = {}                                                        # solas ficam apoiadas (girar furava o chao)
    return V((0, 0.3 * k, DEITADO_Z * k))
def c_deitar(t):
    r = {}; pes = {}; ext = {}
    k = suave(t / 1.8); raiz = pose_deitado(k, r, pes, ext)
    return r, raiz, pes, ext
def c_levantar_deitado(t):
    return c_deitar(1.8 - t)
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
    r["OrelhaE"] = [(X, R(-35) * k)]; r["OrelhaD"] = [(X, R(-35) * k)]
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
        ext["alvo_fk"]["Mao" + l_] = suave(k / 0.15)                          # logo que o corpo sobe, o alvo e a propria pata em FK
        r["Braco" + l_] = [(X, R(35 * s_) * k), (Y, R(-12 if l_ == "E" else 12) * k)]
        r["Antebraco" + l_] = [(X, R(-55 * s_) * k)]; r["Mao" + l_] = [(X, R(-25) * k)]
    ro = janela(t, 0.7, 2.0, 0.25, 0.3)
    r["Pescoco"] = [(X, R(22) * k - R(14) * ro)]; r["Cabeca"] = [(X, R(12) * k - R(10) * ro)]
    r["Mandibula"] = [(X, R(36) * ro + R(1.5) * math.sin(2 * math.pi * t * 10) * ro)]
    r["OrelhaE"] = [(X, R(-35) * ro)]; r["OrelhaD"] = [(X, R(-35) * ro)]
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
CLIPES = {  # nome: (funcao, duracao s, loop, velocidade em studs/s para o jogo [PROPOSTA], fase do apoio p/ QA)
    "Repouso": (c_repouso, 4.0, True, 0.0, None),
    "Observar": (c_observar, 4.4, False, 0.0, None),
    "Andar": (marcha(1.2, 2.4, 0.62, 0.48, FASE_ANDAR, 3.0, 0.05), 1.2, True, 2.4 / (0.62 * 1.2), (FASE_ANDAR, 0.62)),
    "Corrida": (marcha(16 / 30, 3.4, 0.37, 0.75, FASE_GALOPE, 0, 0.22, flex=9), 16 / 30, True, 3.4 / (0.37 * 16 / 30), (FASE_GALOPE, 0.37)),
    "Arrancada": (c_arrancada, 1.6, False, 0.0, None),
    "Frenagem": (c_frenagem, 1.2, False, 0.0, None),
    "VirarE": (c_virar(1), 1.2, True, 0.0, None),
    "VirarD": (c_virar(-1), 1.2, True, 0.0, None),
    "Sentar": (c_sentar, 1.3, False, 0.0, None),
    "LevantarSentado": (c_levantar_sentado, 1.3, False, 0.0, None),
    "Deitar": (c_deitar, 1.8, False, 0.0, None),
    "LevantarDeitado": (c_levantar_deitado, 1.8, False, 0.0, None),
    "Comer": (c_comer, 2.4, True, 0.0, None),
    "Rugir": (c_rugir, 2.4, False, 0.0, None),
    "Ameaca": (c_ameaca, 3.2, False, 0.0, None),
    "GolpePata": (c_golpe_pata, 1.3, False, 0.0, None),
    "Mordida": (c_mordida, 1.0, False, 0.0, None),
    "ReacaoImpacto": (c_reacao, 1.0, False, 0.0, None),
}
QUAIS = ARGS[1].split(",") if len(ARGS) > 1 else list(CLIPES)

# ------------------------------------------------------------------ amostragem -> FK -> acao + JSON + QA
def malha_zmin():
    dg = bpy.context.evaluated_depsgraph_get(); zm = 9.0
    for o in MALHAS:
        ev = o.evaluated_get(dg); m = ev.to_mesh(); c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c)
        zm = min(zm, float(c.reshape(-1, 3)[:, 2].min()) + o.matrix_world.translation.z); ev.to_mesh_clear()
    return zm
TRONCO_IDX = {}
for o in MALHAS[:3]:                                                       # vertices do tronco (osso dominante fora das patas)
    nomes = {g.index: g.name for g in o.vertex_groups}; ids = []
    for v in o.data.vertices:
        if v.groups:
            g = max(v.groups, key=lambda g: g.weight)
            if not nomes[g.group].startswith(("Braco", "Antebraco", "Mao", "Dedos", "Coxa", "Canela", "Pe", "Escapula")): ids.append(v.index)
    TRONCO_IDX[o.name] = np.array(ids, dtype=np.int64)
def tronco_zmin():
    dg = bpy.context.evaluated_depsgraph_get(); zm = 9.0
    for o in MALHAS[:3]:
        ev = o.evaluated_get(dg); m = ev.to_mesh(); c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c)
        c = c.reshape(-1, 3)[TRONCO_IDX[o.name]]; zm = min(zm, float(c[:, 2].min())); ev.to_mesh_clear()
    return zm
def calibrar_deitado():
    """acha a descida da Raiz em que a parte mais baixa da malha toca o chao (z = 0) na pose deitada final"""
    global DEITADO_Z
    lo_, hi_ = -4.5, -0.3
    for _ in range(14):
        m_ = (lo_ + hi_) / 2; DEITADO_Z = m_; zerar(); rots, raiz, pes, ext = c_deitar(1.8)
        PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
        for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
        for k, d in pes.items(): ALVO[k].location = REP[k] + d
        for k, a_ in ext.get("rot_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
        bpy.context.view_layer.update(); zm = tronco_zmin()
        if zm < 0.15: lo_ = m_                                 # tronco a 0,15 do chao: cotovelos/joelhos nao afundam tanto
        else: hi_ = m_
    DEITADO_Z = hi_; print("DEITADO_Z calibrado", round(DEITADO_Z, 3), "z_min tronco", round(tronco_zmin(), 3), "malha", round(malha_zmin(), 3))
if any(n in QUAIS for n in ("Deitar", "LevantarDeitado")): calibrar_deitado()
manifesto = {}; QUADROS = {}
for nome in QUAIS:
    fn, dur, loop, vel, apoio_info = CLIPES[nome]
    nq = int(round(dur * FPS)) + (0 if loop else 1)
    quadros = []; erro_ik = 0.0; desliza = 0.0; zmin = 9.0; prev = None
    for qi in range(nq):
        t = qi / FPS
        zerar(); rots, raiz, pes, ext = fn(t)
        PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
        for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
        for k, d in pes.items(): ALVO[k].location = REP[k] + d
        for k, a_ in ext.get("rot_pe", {}).items():
            ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
        for k, w_ in ext.get("ik", {}).items():
            meio = PATAS[k][1]; PB[meio].constraints["IK"].influence = w_; PB[k].constraints["Copy Rotation"].influence = w_
        if ext.get("alvo_fk"):                                              # alvo = mistura repouso -> posicao da pata em FK
            for k in ext["alvo_fk"]: PB[PATAS[k][1]].constraints["IK"].mute = True; PB[k].constraints["Copy Rotation"].mute = True
            bpy.context.view_layer.update(); fk = {k: (PB[k].head.copy(), PB[k].matrix.to_quaternion()) for k in ext["alvo_fk"]}
            for k, w_ in ext["alvo_fk"].items():
                PB[PATAS[k][1]].constraints["IK"].mute = False; PB[k].constraints["Copy Rotation"].mute = False
                ALVO[k].location = ALVO[k].location.lerp(fk[k][0], w_); ALVO[k].rotation_quaternion = ALVO[k].rotation_quaternion.slerp(fk[k][1], w_)
        bpy.context.view_layer.update()
        pose = {pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in PB}
        for k in PATAS:
            if ext.get("ik", {}).get(k, 1.0) > 0.99 and ext.get("alvo_fk", {}).get(k, 0.0) < 0.01:
                erro_ik = max(erro_ik, (PB[k].head - ALVO[k].location).length)
        if qi % 3 == 0: zmin = min(zmin, malha_zmin())
        if apoio_info:                                                      # pe apoiado: velocidade no chao = v do jogo
            fases, apoio = apoio_info
            cur = {k: PB[k].head.copy() for k in PATAS}
            if prev is not None:
                for k, fase in fases.items():
                    f = (t / dur + fase) % 1.0; fp = ((t - 1 / FPS) / dur + fase) % 1.0
                    if f < apoio and fp < apoio and fp < f:
                        vy = (cur[k].y - prev[k].y) * FPS; desliza = max(desliza, abs(vy - vel))
            prev = cur
        quadros.append(pose)
    manifesto[nome] = {"duracao": dur, "loop": loop, "quadros": nq, "velocidade_studs_s_PROPOSTA": round(vel, 2),
                       "erro_ik_max": round(erro_ik, 4), "desliza_pe_max_studs_s": round(desliza, 3), "malha_z_min": round(zmin, 3)}
    print("CLIPE", nome, manifesto[nome], flush=True)
    dado = {"nome": "Urso_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel, 3), "ossos": {}}
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "CR_Urso_v2_Anim.blend"))
print("ANIM_OK", list(QUADROS))
