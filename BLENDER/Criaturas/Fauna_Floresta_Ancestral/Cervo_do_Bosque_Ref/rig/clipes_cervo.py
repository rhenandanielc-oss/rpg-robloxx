"""Clipes do Cervo-do-Bosque (rig de 30 ossos, rig/CR_Cervo_Rig.blend). Adaptado do gerador aprovado do Bufalo
(Bufalo_Colossal_Ref/build/60_clipes.py), escala do cervo (ombro ~1,2 u). NO LUGAR (o jogo move o modelo).
Cada quadro define alvos IK das 4 patas (no boleto), rotacoes de coluna/pescoco/cabeca/orelhas/cauda e o deslocamento da
Raiz; o IK resolve as patas e a pose final vai para uma acao FK 'Cervo_<clipe>' e para JSON (mesmo formato do Bufalo/Urso,
ponte JSON -> KeyframeSequence no Studio).
Ungulado: cadeia de 3 ossos por pata (dianteira Braco-Antebraco-Canela, carpo dobra para a frente; traseira
Coxa-Perna-CanelaTras, jarrete para tras); a Quartela copia a orientacao do alvo (casco plano no apoio, rola no balanco).
Lote 1: Repouso, Andar, VirarE, VirarD. Velocidades, passadas e giro sao PROPOSTA/parametro tecnico (nao regra do jogo).
QA: erro do IK, escorregao do casco apoiado no mundo, altura minima dos cascos, emenda do laco.
Uso: blender -b rig/CR_Cervo_Rig.blend -P rig/clipes_cervo.py -- <saida_dir> [Repouso,Andar,VirarE,VirarD]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
for o in [o for o in sc.objects if o.type in ("CAMERA", "LIGHT")]: bpy.data.objects.remove(o)
arm = bpy.data.objects["Cervo_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
CORPO = bpy.data.objects["Cervo_Corpo"]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def onda(t, T, fase=0.0): return math.sin(2 * math.pi * (t / T + fase))
def pulso(t, T, t0, dur):
    """pulso suave 0->1->0 de duracao dur a cada T segundos (orelha que gira, cauda que sacode)"""
    f = ((t - t0) % T) / dur
    return math.sin(math.pi * f) ** 2 if f < 1 else 0.0
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
    p_.location = j + V((0, -0.4 if par == "dian" else 0.4, 0))          # carpo para a frente; jarrete para tras
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
DOBRA_HOOK = None                                    # lote 3 bloco B: patas dobradas em FK (deitar/levantar)
def zerar():
    for pb in PB: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for pb in PB:
        for c_ in pb.constraints: c_.influence = 1.0
    for k, o in ALVO.items(): o.location = REP[k].copy(); o.rotation_quaternion = ROT0[k].copy()
    for k, o in POLO.items(): o.location = POLO_REP[k].copy()
# ------------------------------------------------------------------ locomocao (apoio amarrado a S(t): casco nao escorrega)
class Perfil:
    def __init__(self, vfun, t0=-3.0, t1=12.0, dt=1 / 600):
        self.t0, self.dt = t0, dt; n = int((t1 - t0) / dt) + 1; acc = 0.0; self.S = []
        for i in range(n): self.S.append(acc); acc += vfun(t0 + i * dt) * dt
    def s(self, t):
        x = (t - self.t0) / self.dt; i = max(0, min(len(self.S) - 2, int(x))); return self.S[i] + (self.S[i + 1] - self.S[i]) * (x - i)
def passo_var(t, fase, T, apoio, alt, L, perf, eixo=Y):
    phi = t / T + fase; n_ = math.floor(phi); f = phi - n_; tc = (n_ - fase) * T
    if f < apoio: return eixo * (-L / 2 + perf.s(t) - perf.s(tc)), 0.0
    tl = tc + apoio * T; y0 = -L / 2 + perf.s(tl) - perf.s(tc); y1 = -L / 2
    u = (f - apoio) / (1 - apoio); s = suave(u)
    return eixo * (y0 + (y1 - y0) * s) + V((0, 0, alt * math.sin(math.pi * u) ** 0.8)), u
BASE_Z = -0.012                                   # corpo levemente baixo nos clipes em pe (folga da dianteira)
# andar de cervo [PROPOSTA]: ciclo 1,1 s, passada 0,50 u, apoio 64%, casco sobe alto (passo "pisado" de cervideo)
T_AND, L_AND, AP_AND, ALT_AND = 1.1, 0.50, 0.64, 0.085
V_AND = L_AND / (AP_AND * T_AND); PERF_AND = Perfil(lambda t: V_AND)
FASE_ANDAR = {"QuartelaTrasE": 0.0, "QuartelaE": 0.25, "QuartelaTrasD": 0.5, "QuartelaD": 0.75}   # sequencia lateral
def rola_casco(u):
    """casco: no balanco a pinca dobra (boleto flexiona) e volta plana antes do pouso"""
    return R(40) * math.sin(math.pi * min(1.0, u * 1.15)) if u > 0 else 0.0
def orelhas(r, t, T, base=0.0):
    """orelhas vivas: giros rapidos e independentes (escutam), nao periodicos entre si"""
    e = pulso(t, T, 0.6, 0.55) - 0.6 * pulso(t, T, 3.4, 0.4) + 0.8 * pulso(t, T, 7.1, 0.5)
    d = pulso(t, T, 2.2, 0.5) + 0.7 * pulso(t, T, 5.3, 0.45) - 0.5 * pulso(t, T, 8.4, 0.4)
    r["OrelhaE"] = [(Z, R(-20) * e), (X, R(5) * e + base)]; r["OrelhaD"] = [(Z, R(20) * d), (X, R(5) * d + base)]   # 20 graus: ponta da E encosta na galhada
# ------------------------------------------------------------------ clipes: t -> (rots, raiz, pes, ext)
def c_repouso(t):
    T = 10.0; r = {}; b = onda(t, 3.333); b2 = onda(t, 3.333, 0.35); peso = onda(t, T)       # 3 respiracoes por laco de 10 s
    r["Coluna1"] = [(X, R(0.6) * b)]; r["Coluna2"] = [(X, R(-0.8) * b)]; r["Coluna3"] = [(X, R(0.5) * b2)]
    r["Pelve"] = [(Y, R(1.0) * peso)]                                                          # peso troca de traseira
    olha = onda(t, T, 0.1); vig = pulso(t, T, 4.2, 1.6)                                        # olha em volta; ergue a cabeca 1x
    r["Pescoco"] = [(X, R(-0.8) * b - R(4) * vig), (Z, R(5) * olha)]
    r["Pescoco2"] = [(Z, R(3) * onda(t, T, 0.18)), (X, R(-2) * vig)]
    r["Cabeca"] = [(X, R(1.2) * b2 + R(2) * vig), (Z, R(4) * onda(t, T, 0.25))]
    orelhas(r, t, T)
    sac = pulso(t, T, 6.2, 0.5)                                                                # cauda: sacode 1x (moscas)
    r["Cauda1"] = [(X, R(3) * b2 - R(18) * sac), (Z, R(14) * sac * math.sin(6 * math.pi * ((t - 6.2) % T) / 0.5))]
    r["Cauda2"] = [(Z, R(10) * sac * math.sin(6 * math.pi * ((t - 6.25) % T) / 0.5))]
    return r, V((0.004 * peso, 0, 0.003 * b)), {}, {}
def c_andar(t):
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}; u = t / T_AND
    for k_, fase in FASE_ANDAR.items():
        d, uu = passo_var(t, fase, T_AND, AP_AND, ALT_AND, L_AND, PERF_AND)
        pes[k_] = d; ext["rot_pe"][k_] = rola_casco(uu); ext["apoio"][k_] = uu == 0
    sw = math.sin(2 * math.pi * u); bob = math.cos(4 * math.pi * u)
    r["Pelve"] = [(Y, R(2.2) * sw), (Z, R(1.4) * sw)]
    r["Coluna1"] = [(Y, R(-1.0) * sw)]
    r["Coluna2"] = [(Y, R(-0.8) * sw), (Z, R(-1.0) * sw)]
    r["Coluna3"] = [(Y, R(1.5) * math.sin(2 * math.pi * (u + 0.25))), (X, R(0.6) * bob)]
    # cabeca acena com cada dianteira (2x por ciclo), pescoco compensa o rolar da cernelha; cabeca fica estavel (olhar)
    acen = math.cos(4 * math.pi * (u - 0.25 - 0.06))
    r["Pescoco"] = [(X, R(2.0) + R(2.4) * acen), (Z, R(-1.5) * math.sin(2 * math.pi * (u + 0.25)))]
    r["Pescoco2"] = [(X, R(1.0) * acen)]
    r["Cabeca"] = [(X, R(-2.2) * acen), (Z, R(-0.8) * math.sin(2 * math.pi * (u + 0.3)))]
    for lado in "ED":                                                                       # escapula acompanha a dianteira
        r["Escapula" + lado] = [(X, R(5) * math.cos(2 * math.pi * ((u + FASE_ANDAR["Quartela" + lado]) % 1.0)))]
    r["Cauda1"] = [(Z, R(4) * math.sin(2 * math.pi * (u - 0.15)))]; r["Cauda2"] = [(Z, R(6) * math.sin(2 * math.pi * (u - 0.3)))]
    orelhas(r, t % (10 * T_AND), 10 * T_AND)                                                # orelhas no laco de 10 ciclos
    return r, V((0.004 * sw, 0, -0.004 + 0.006 * bob)), pes, ext
GIRO_GS = 25.0; GIRO = R(GIRO_GS)               # curva: 25 graus/s a ~0,71 u/s = raio ~1,6 u (PROPOSTA)
PIVO = BD["Raiz"].head_local.copy()
def c_virar(sinal):
    """andando em curva: o jogo gira o modelo a sinal*GIRO em torno da Raiz e o desloca a V_AND. Casco apoiado = ponto fixo
    no mundo visto do corpo: arco em torno do centro instantaneo de rotacao. Corpo inclina para dentro, cabeca entra antes."""
    w = GIRO * sinal; T, ap = T_AND, AP_AND
    ICR = PIVO + V((V_AND / w, 0, 0))
    def no_arco(k_, ang):
        p_ = REP[k_] - ICR; c_, s_ = math.cos(ang), math.sin(ang)
        return V((ICR.x + p_.x * c_ - p_.y * s_, ICR.y + p_.x * s_ + p_.y * c_, REP[k_].z)) - REP[k_]
    def f(t):
        r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}, "giro_pe": {}}
        for k_, fase in FASE_ANDAR.items():
            phi = t / T + fase; n_ = math.floor(phi); fr = phi - n_; tc = (n_ - fase) * T; tm = tc + ap * T / 2
            meia = w * ap * T / 2
            if fr < ap:
                pes[k_] = no_arco(k_, -w * (t - tm)); uu = 0.0; ext["giro_pe"][k_] = -w * (t - tm)
            else:
                uu = (fr - ap) / (1 - ap); p0 = no_arco(k_, -meia); p1 = no_arco(k_, meia)
                ext["giro_pe"][k_] = -meia + 2 * meia * suave(uu)
                pes[k_] = p0.lerp(p1, suave(uu)) + V((0, 0, ALT_AND * math.sin(math.pi * uu) ** 0.8))
            ext["rot_pe"][k_] = rola_casco(uu); ext["apoio"][k_] = uu == 0
        rr, raiz, _p, _e = c_andar(t); raiz = raiz + V((0, 0, -0.006))
        for k_, v_ in rr.items(): r[k_] = list(v_)
        r["Pescoco"] = r.get("Pescoco", []) + [(Z, R(12) * sinal)]; r["Pescoco2"] = r.get("Pescoco2", []) + [(Z, R(6) * sinal)]
        r["Cabeca"] = r.get("Cabeca", []) + [(Z, R(8) * sinal)]
        r["Coluna2"] = r.get("Coluna2", []) + [(Z, R(3) * sinal)]; r["Pelve"] = r.get("Pelve", []) + [(Z, R(-4) * sinal), (Y, R(3) * sinal)]
        r["Coluna3"] = r.get("Coluna3", []) + [(Y, R(3) * sinal)]                   # inclina para dentro da curva
        r["Cauda1"] = r.get("Cauda1", []) + [(Z, R(-8) * sinal)]                   # cauda segue a trajetoria
        return r, raiz, pes, ext
    return f
# nome: (funcao, duracao, loop, velocidade [PROPOSTA], v(t) para QA, giro graus/s [PROPOSTA])
CLIPES = {"Repouso": (c_repouso, 10.0, True, 0.0, None, 0.0), "Andar": (c_andar, 10 * T_AND, True, V_AND, None, 0.0),
          "VirarE": (c_virar(1), 10 * T_AND, True, V_AND, None, GIRO_GS), "VirarD": (c_virar(-1), 10 * T_AND, True, V_AND, None, -GIRO_GS)}
if os.environ.get("CERVO_L2"):                     # lote 2: so com a variavel; sem ela o lote 1 aprovado nao muda
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_cervo_l2.py"), encoding="utf-8").read())
if os.environ.get("CERVO_L4"):                     # lote 4 (reacao e derrota): so com a variavel
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_cervo_l4.py"), encoding="utf-8").read())
if os.environ.get("CERVO_L3B"):                    # lote 3 bloco B (deitar/deitado/levantar): so com a variavel
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_cervo_l3b.py"), encoding="utf-8").read())
if os.environ.get("CERVO_L3"):                     # lote 3 (vida no habitat): so com a variavel
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipes_cervo_l3.py"), encoding="utf-8").read())
QUAIS = ARGS[1].split(",") if len(ARGS) > 1 else list(CLIPES)
# ------------------------------------------------------------------ QA: cascos = vertices da pele com Quartela dominante e baixos
gr = {g.index: g.name for g in CORPO.vertex_groups}; CASCO_V = {k: [] for k in PATAS}
for v in CORPO.data.vertices:
    if v.co.z > 0.07: continue
    for g in v.groups:
        if gr[g.group] in CASCO_V and g.weight > 0.5: CASCO_V[gr[g.group]].append(v.index)
print("CASCOS vertices", {k: len(v) for k, v in CASCO_V.items()})
def cascos():
    dg = bpy.context.evaluated_depsgraph_get(); ev = CORPO.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); c = c.reshape(-1, 3); ev.to_mesh_clear()
    return {k: c[idx] for k, idx in CASCO_V.items()}
# alcance maximo da pata (fracao do comprimento Braco+Antebraco+Canela / Coxa+Perna+CanelaTras). So com a variavel: os
# lotes aprovados nao mudam. Corrida r2 (12/11, "pernas dobram para frente e para tras"): 0 = desligado.
ALC_MAX = float(os.environ.get("CERVO_ALCANCE_MAX", "0"))
CADEIA_L = {k: BD[f].length + BD[m].length + BD[BD[m].parent.name].length for k, (_p, f, m) in PATAS.items()}
CLAMP_N = [0]
manifesto = {}; QUADROS = {}; APOIOS = {}
for nome in QUAIS:
    fn, dur, loop, vel, vfun, giro = CLIPES[nome]; nq = int(round(dur * FPS)) + (0 if loop else 1)
    APO = []; quadros = []; erro_ik = 0.0; zmin = {k: 9.0 for k in PATAS}; desl = {k: 0.0 for k in PATAS}; prev = None; ERRO_PATA = {}; ap_prev = {}
    for qi in range(nq + (1 if loop else 0)):                       # loop: quadro extra em t = duracao so para medir a emenda
        t = qi / FPS; zerar(); rots, raiz, pes, ext = fn(t); raiz = raiz + V((0, 0, BASE_Z))
        PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
        for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
        for k, d in pes.items(): ALVO[k].location = REP[k] + d
        for k, a_ in ext.get("rot_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
        for k, g_ in ext.get("giro_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(Z, g_) @ ALVO[k].rotation_quaternion
        bpy.context.view_layer.update()
        if ALC_MAX:                                                  # alvo alem do alcance: a pata estica toda e o IK inverte a dobra
            for k in PATAS:                                          # (carpo/cotovelo dobrando para o lado errado). Traz o alvo para
                fim = PATAS[k][1]; meio = PATAS[k][2]; topo = BD[meio].parent.name   # dentro de ALC_MAX do comprimento da cadeia
                raiz_ = PB[topo].head; d_ = ALVO[k].location - raiz_; Lc = CADEIA_L[k] * ALC_MAX
                if d_.length > Lc: ALVO[k].location = raiz_ + d_.normalized() * Lc; CLAMP_N[0] += 1
            bpy.context.view_layer.update()
        if DOBRA_HOOK and (ext.get("dobra") or ext.get("solta")): DOBRA_HOOK(ext)   # patas em dobra/soltas: FK (sem IK)
        for _it in range(2):                                         # casco em balanco nunca abaixo do chao
            cs0 = cascos(); mexeu = False
            for k in PATAS:
                if ext.get("apoio", {}).get(k, True) or len(cs0[k]) == 0 or k in ext.get("dobra", {}) or k in ext.get("solta", {}): continue
                zb = float(cs0[k][:, 2].min())
                if zb < 0.0: ALVO[k].location.z += -zb + 0.002; mexeu = True
            if not mexeu: break
            bpy.context.view_layer.update()
        pose = {pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in PB}
        if loop and qi == nq: pose_fim = pose; break
        for k in PATAS:
            if k in ext.get("dobra", {}) or k in ext.get("solta", {}): continue   # pata em FK: sem alvo de IK a medir
            e_ = (PB[k].head - ALVO[k].location).length; erro_ik = max(erro_ik, e_)
            if e_ > ERRO_PATA.get(k, (0, 0))[0]: ERRO_PATA[k] = (round(e_, 4), qi)
        cs = cascos()
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
    emenda = 0.0
    if loop:
        a0 = quadros[0]
        emenda = max((a0[n].to_quaternion().rotation_difference(pose_fim[n].to_quaternion()).angle) for n in a0)
    manifesto[nome] = {"duracao": dur, "loop": loop, "quadros": nq, "velocidade_u_s_PROPOSTA": round(vel, 3), "erro_ik_max": round(erro_ik, 4),
                       "erro_ik_por_pata": ERRO_PATA, "casco_z_min": {k: round(v, 4) for k, v in zmin.items()},
                       "escorregao_casco_apoiado_max": {k: round(v, 4) for k, v in desl.items()}, "emenda_loop_graus": round(math.degrees(emenda), 2),
                       "giro_graus_s_PROPOSTA": giro, "alvos_limitados": CLAMP_N[0]}
    print("CLIPE", nome, json.dumps(manifesto[nome]), flush=True); CLAMP_N[0] = 0
    dado = {"nome": "Cervo_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel, 4), "ossos": {}}
    dado["apoio"] = {k: [int(x[k]) for x in APO] for k in PATAS}; APOIOS[nome] = dado["apoio"]
    for pb in PB:
        seq = []
        for pose in quadros:
            m = pose[pb.name]; q = m.to_quaternion(); tt = m.translation
            seq += [round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(tt.x, 5), round(tt.y, 5), round(tt.z, 5)]
        dado["ossos"][pb.name] = seq
    with open(os.path.join(OUT, "Cervo_%s.json" % nome), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    QUADROS[nome] = quadros
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
for nome, quadros in QUADROS.items():
    act = bpy.data.actions.get("Cervo_" + nome) or bpy.data.actions.new("Cervo_" + nome); arm.animation_data.action = act
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, os.environ.get("CERVO_ANIM_ARQ", "Cervo_Clipes_L1.blend"))); print("ANIM_OK", list(QUADROS))
