"""Clipes da Coruja-da-Floresta (rig piloto de ave aprovado 14/11, rig/CR_Coruja_Rig.blend). LOTE A: pousada.
Mecanismo inspirado no gerador do javali (Javali_Silvestre_Ref/rig/clipes_javali.py): pose por quadro -> acao FK 'Coruja_<clipe>'
+ JSON por clipe (ponte JSON -> KeyframeSequence) + manifesto com QA. Especifico da ave:
  - pes: IK de 2 ossos (Tibia + Tarso; o calcanhar dobra para TRAS), alvo na base dos Dedos; Dedos copiam o alvo (apoio plano);
  - asas: base = ASA FECHADA resolvida por alvos (rig/dobra_asas.json); variacoes por slerp para outras poses de asa;
  - demais ossos: rotacoes em eixos do mundo de repouso (rot_mundo), somadas a base.
NO LUGAR: o jogo move o modelo (velocidade/giro gravados quando houver). Numeros e duracoes sao [PROPOSTA].
Clipes: Repouso, OlharE, OlharD, InclinarCabeca, AjeitarPenas, EsticarAsaE, EsticarAsaD, VirarNoLugarE, VirarNoLugarD, Saltitar.
Uso: blender -b rig/CR_Coruja_Rig.blend -P rig/clipes_coruja.py -- <saida_dir> [lista,de,clipes]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
ARGS = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(ARGS[0]); os.makedirs(os.path.join(OUT, "json"), exist_ok=True)
AQUI = os.path.dirname(os.path.abspath(__file__))
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
for im in bpy.data.images:
    if im.filepath and "low_voxel" in im.filepath: im.filepath = im.filepath.replace("low_voxel", "low_v1"); im.reload()
arm = bpy.data.objects["Coruja_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
CORPO, CAB = bpy.data.objects["Coruja_Corpo"], bpy.data.objects["Coruja_Cabeca"]; MALHAS = [CORPO, CAB]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def janela(t, a, b, sub=0.2, des=0.2): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
def onda(t, T, fase=0.0): return math.sin(2 * math.pi * (t / T + fase))
def pulso(t, t0, dur):
    f = (t - t0) / dur; return math.sin(math.pi * f) ** 2 if 0 < f < 1 else 0.0
R = math.radians; X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
for pb in PB: pb.rotation_mode = "QUATERNION"
def rot_mundo(nome, eixos):
    r = BD[nome].matrix_local.to_3x3(); q = Matrix.Identity(3)
    for eixo, ang in eixos: q = Matrix.Rotation(ang, 3, eixo) @ q
    return (r.inverted() @ q @ r).to_quaternion()
# ------------------------------------------------------------------ base: asa fechada
FECHADA = {k: Quaternion(v) for k, v in json.load(open(os.environ.get("CORUJA_DOBRA", os.path.join(AQUI, "dobra_asas.json"))))["ossos"].items()}
ASA_OSSOS = ["BracoAsa", "AntebracoAsa", "MaoAsa", "Primarias"]
# ------------------------------------------------------------------ IK dos pes
PES = {"E": "DedosE", "D": "DedosD"}; ALVO, POLO, REP = {}, {}, {}
for l, pe in PES.items():
    a_ = bpy.data.objects.new("IK_" + pe, None); sc.collection.objects.link(a_); a_.location = BD[pe].head_local.copy()
    a_.rotation_mode = "QUATERNION"; a_.rotation_quaternion = BD[pe].matrix_local.to_quaternion()
    p_ = bpy.data.objects.new("Polo_" + pe, None); sc.collection.objects.link(p_); p_.location = BD["Tarso" + l].head_local + V((0, 0.25, 0))   # calcanhar para tras
    c = PB["Tarso" + l].constraints.new("IK"); c.target = a_; c.pole_target = p_; c.chain_count = 2; c.use_stretch = False
    cr = PB[pe].constraints.new("COPY_ROTATION"); cr.target = a_
    ALVO[l], POLO[l], REP[l] = a_, p_, a_.location.copy()
ROT0 = {l: o.rotation_quaternion.copy() for l, o in ALVO.items()}; POLO_REP = {l: o.location.copy() for l, o in POLO.items()}
bpy.context.view_layer.update()
for l in PES:                                                       # angulo de polo que reproduz o repouso
    c = PB["Tarso" + l].constraints["IK"]; alvo_j = BD["Tibia" + l].tail_local.copy()
    def erro(a_): c.pole_angle = a_; bpy.context.view_layer.update(); return (PB["Tibia" + l].tail - alvo_j).length
    m_ = min((erro(R(g)), R(g)) for g in range(-180, 180, 5))[1]
    for p_ in (2.5, 1.0, 0.25): m_ = min((erro(m_ + R(d)), m_ + R(d)) for d in (-p_, 0, p_))[1]
    c.pole_angle = m_; print("POLO", l, round(math.degrees(m_), 1), "erro", round(erro(m_), 4))
CADEIA = {l: BD["Tibia" + l].length + BD["Tarso" + l].length for l in PES}
# ------------------------------------------------------------------ pose de um quadro
def zerar():
    for pb in PB:
        pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
        for c_ in pb.constraints: c_.influence = 1.0
    for l in PES: ALVO[l].location = REP[l].copy(); ALVO[l].rotation_quaternion = ROT0[l].copy(); POLO[l].location = POLO_REP[l].copy()
def asa_q(l, nm, ext):
    """asa: FECHADA, ou slerp para outra pose (ext['asa'][l] = (dict nome->quat, fator)); ext['asa_q'][l][nm] = quat explicito"""
    if nm in ext.get("asa_q", {}).get(l, {}): return ext["asa_q"][l][nm]
    base = FECHADA[nm + l]; a = ext.get("asa", {}).get(l)
    if not (a and nm in a[0]): return base
    alvo = a[0][nm]
    if base.dot(alvo) < 0: alvo = -alvo                               # caminho curto (o sinal invertido dava salto de 355 graus)
    return base.slerp(alvo, a[1])
def pose_de(fn, t):
    zerar(); rots, raiz, pes, ext = fn(t); raiz = raiz + V((0, 0, BASE_Z))
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
    if ext.get("giro_raiz"): PB["Raiz"].rotation_quaternion = rot_mundo("Raiz", [(Z, ext["giro_raiz"])])
    for l in PES:
        for nm in ASA_OSSOS: PB[nm + l].rotation_quaternion = asa_q(l, nm, ext)
    for nm, eixos in rots.items():
        base = PB[nm].rotation_quaternion.copy() if any(nm == a + l for a in ASA_OSSOS for l in PES) else Quaternion()
        PB[nm].rotation_quaternion = base @ rot_mundo(nm, eixos)
    for l, d in pes.items(): ALVO[l].location = REP[l] + d
    for l, g in ext.get("giro_pe", {}).items(): ALVO[l].rotation_quaternion = Quaternion(Z, g) @ ROT0[l]
    for l, a in ext.get("rola_pe", {}).items(): ALVO[l].rotation_quaternion = Quaternion(X, a) @ ALVO[l].rotation_quaternion
    bpy.context.view_layer.update()
    if ext.get("pes_corpo"):                                         # lote B: pes presos ao CORPO (recolhidos em voo) ou ao chao
        Mr = PB["Raiz"].matrix @ BD["Raiz"].matrix_local.inverted()  # leva pontos do repouso para onde a Raiz levou o corpo
        for l, (ponto, f, enrola) in ext["pes_corpo"].items():
            if f <= 1e-4: continue
            alvo_c = Mr @ V(ponto); ALVO[l].location = ALVO[l].location.lerp(alvo_c, f)
        bpy.context.view_layer.update()
    for l in PES:                                                    # alvo alem do alcance: perna esticada e IK estala
        raiz_ = PB["Tibia" + l].head; d_ = ALVO[l].location - raiz_
        if d_.length > CADEIA[l] * 0.97: ALVO[l].location = raiz_ + d_.normalized() * CADEIA[l] * 0.97; LIMITE[0] += 1
    bpy.context.view_layer.update()
    if ext.get("pernas_fk"):                                         # lote B: perna recolhida em FK, interpolada com a solucao do IK
        alvo_fk, f = ext["pernas_fk"]                               # (sem IK no ar: o IK com pe preso ao corpo virava a tibia)
        if f > 1e-4:
            for l in PES:
                cad = ["Coxa" + l, "Tibia" + l, "Tarso" + l, "Dedos" + l]
                loc = {n: arm.convert_space(pose_bone=PB[n], matrix=PB[n].matrix, from_space="POSE", to_space="LOCAL").to_quaternion() for n in cad}
                for c_ in list(PB["Tarso" + l].constraints) + list(PB["Dedos" + l].constraints): c_.influence = 0.0
                for n in cad:
                    q_fk = rot_mundo(n, alvo_fk.get(n[:-1], []))
                    if loc[n].dot(q_fk) < 0: q_fk = -q_fk
                    PB[n].rotation_quaternion = loc[n].slerp(q_fk, f)
            bpy.context.view_layer.update()
    return ext, {pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in PB}
LIMITE = [0]
BASE_Z = -0.010        # leve flexao de base: em pe a perna da coruja fica quase reta e qualquer subida do corpo passava do alcance
# ------------------------------------------------------------------ poses de asa usadas no lote A
def quats_de(rots_rest):
    """quats locais de uma pose de asa definida a partir do REPOUSO (asas abertas) em eixos do mundo"""
    return {nm: rot_mundo(nm + "E", e) for nm, e in rots_rest.items()}
def espelha(qs): return {k: Quaternion((q.w, q.x, -q.y, -q.z)) for k, q in qs.items()}   # D = espelho do E (validado na dobra)
MEIO_ABERTA_E = {nm: FECHADA[nm + "E"].slerp(Quaternion(), 0.30) for nm in ASA_OSSOS}      # asa solta do corpo (sacudir/saltar)
ESTICADA_E = quats_de({"BracoAsa": [(X, R(-35)), (Z, R(45)), (Y, R(45))], "AntebracoAsa": [(Z, R(-12))], "MaoAsa": [(Z, R(8))], "Primarias": [(Z, R(6))]})
ASA_D = lambda qs: espelha(qs)
# ------------------------------------------------------------------ clipes
T_REP = 8.0
def base_respira(r, t, T=T_REP, k=1.0):
    b = onda(t, T / 4)                                                # 4 respiracoes por laco
    r.setdefault("Coluna1", []).append((X, R(0.8) * b * k)); r.setdefault("Coluna2", []).append((X, R(-0.6) * b * k))
    return b
def c_repouso(t):
    r = {}; b = base_respira(r, t); peso = onda(t, T_REP, 0.15)
    r["Pelve"] = [(Y, R(1.2) * peso)]
    # olhares rapidos de coruja: vira em ~0,15 s, segura, volta (pequenos, sem sair do laco)
    g = 18 * (suave((t - 1.6) / 0.15) - suave((t - 3.0) / 0.2)) - 14 * (suave((t - 5.0) / 0.15) - suave((t - 6.4) / 0.2))
    r["Pescoco2"] = [(Z, R(g * 0.5))]; r["Cabeca"] = [(Z, R(g * 0.5)), (Y, R(4) * onda(t, T_REP, 0.4))]
    for l, s, t0 in (("E", 1, 2.2), ("D", -1, 4.4)):
        r["Tufo" + l] = [(X, R(-12) * pulso(t, t0, 0.5)), (Y, R(6 * s) * pulso(t, t0 + 3.2, 0.4))]
    r["Cauda"] = [(X, R(5) + R(2) * onda(t, T_REP / 2, 0.3))]       # cauda um pouco erguida (com a flexao de base a ponta tocava o chao)
    return r, V((0.003 * peso, 0, 0.0015 * b)), {}, {}
REP0 = None
def base_rep():
    r, raiz, _p, _e = c_repouso(0.0); return {k: list(v) for k, v in r.items()}, raiz
def soma(r, nm, e): r[nm] = r.get(nm, []) + e
DUR_OL = 2.4
def k_olhar_r3(t):
    """r3: giro DECIDIDO (sai rapido, desacelera curto em 0,30 s), passa 3% e assenta (0,15 s), pausa, retorno suave (0,5 s)"""
    if t < 0.30: u = (t / 0.30) ** 1.4; k = 1 - (1 - u) ** 3            # parte do repouso (sem tranco no 1o quadro) e desacelera curto
    elif t < 0.45: u = (t - 0.30) / 0.15; k = 1 + 0.03 * math.sin(math.pi * u)
    else: k = 1.0
    return k * (1 - suave((t - 1.80) / 0.50))
def c_olhar(s):
    if os.environ.get("CORUJA_R3"):
        def f3(t):
            r, raiz = base_rep(); k = k_olhar_r3(t); tot = float(os.environ.get("CORUJA_OLHAR_GRAUS", "150")) * s
            pa, pb_, pc = [float(x) for x in os.environ.get("CORUJA_OLHAR_PARTES", "0.10,0.25,0.65").split(",")]
            sacada = 6 * s * pulso(t, 0.95, 0.30)                                        # pequeno ajuste no meio da pausa (fixa o alvo)
            soma(r, "Pescoco", [(Z, R(tot * pa + sacada * 0.2) * k)]); soma(r, "Pescoco2", [(Z, R(tot * pb_ + sacada * 0.3) * k)])
            soma(r, "Cabeca", [(Z, R(tot * pc + sacada * 0.5) * k), (Y, R(-5 * s) * k)])
            ct = float(os.environ.get("CORUJA_OLHAR_TRONCO", "-3"))                     # tronco: compensa (-) ou acompanha (+) o giro
            soma(r, "Coluna2", [(Z, R(ct * s) * k)]); soma(r, "Coluna1", [(Z, R(ct * 0.5 * s) * k)])
            for l in "ED": soma(r, "Tufo" + l, [(X, R(-7) * pulso(t, 0.26, 0.30) - R(5) * pulso(t, 1.95, 0.35))])   # tufos reagem discretos
            return r, raiz, {}, {}
        return f3
    def f(t):
        r, raiz = base_rep(); k = suave(t / 0.32) * (1 - suave((t - 1.85) / 0.45))     # giro rapido, segura, volta mais calmo
        tot = 150 * s; sacada = 8 * s * pulso(t, 0.9, 0.35)                            # pequeno ajuste no meio (fixa o alvo)
        soma(r, "Pescoco", [(Z, R(tot * 0.25 + sacada * 0.3) * k)]); soma(r, "Pescoco2", [(Z, R(tot * 0.35 + sacada * 0.3) * k)])
        soma(r, "Cabeca", [(Z, R(tot * 0.40 + sacada * 0.4) * k), (Y, R(-6 * s) * k)])
        soma(r, "Coluna2", [(Z, R(-4 * s) * k)])                                       # tronco compensa um pouco
        return r, raiz, {}, {}
    return f
DUR_INC = 2.4
def c_inclinar(t):
    r, raiz = base_rep()
    a = 24 * (suave((t - 0.15) / 0.25) - suave((t - 0.95) / 0.25)) - 18 * (suave((t - 1.15) / 0.22) - suave((t - 1.85) / 0.3))
    soma(r, "Cabeca", [(Y, R(a))]); soma(r, "Pescoco2", [(Y, R(a * 0.25)), (X, R(4) * janela(t, 0.1, 2.2, 0.3, 0.3))])   # escuta: inclina e avanca
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-10) * janela(t, 0.1, 2.2, 0.2, 0.3))])
    return r, raiz, {}, {}
DUR_AJ = 2.2
def c_ajeitar(t):
    r, raiz = base_rep(); prep = janela(t, 0.0, 1.9, 0.30, 0.35)
    sac = math.exp(-max(0.0, t - 0.45) / 0.22) * math.sin(2 * math.pi * 7.0 * (t - 0.45)) if t > 0.45 else 0.0
    sac *= suave((t - 0.4) / 0.08)
    soma(r, "Coluna1", [(Z, R(7) * sac)]); soma(r, "Coluna2", [(Z, R(9) * sac), (X, R(-3) * prep)])
    soma(r, "Pescoco", [(Z, R(-6) * sac)]); soma(r, "Cabeca", [(Z, R(14) * math.sin(2 * math.pi * 7.0 * (t - 0.50)) * math.exp(-max(0.0, t - 0.5) / 0.2) if t > 0.5 else 0.0)])
    soma(r, "Cauda", [(Z, R(10) * sac)])
    asa = {l: (MEIO_ABERTA_E if l == "E" else ASA_D(MEIO_ABERTA_E), 0.55 * janela(t, 0.25, 1.1, 0.15, 0.3)) for l in "ED"}
    return r, raiz + V((0, 0, -0.004 * prep)), {}, {"asa": asa}           # (subir esticava as pernas alem do alcance)
DUR_EST = 3.2
def c_esticar(l):
    s = 1 if l == "E" else -1; outro = "D" if l == "E" else "E"
    def f(t):
        r, raiz = base_rep(); k = suave((t - 0.35) / 0.7) * (1 - suave((t - 2.15) / 0.75))
        pk = janela(t, 0.15, 2.95, 0.3, 0.3)                                            # peso vai para a outra perna antes
        soma(r, "Coluna2", [(Y, R(-5 * s) * pk), (X, R(4) * k)]); soma(r, "Coluna1", [(Y, R(-3 * s) * pk)])
        soma(r, "Cabeca", [(Z, R(10 * s) * k)])                                         # olha um pouco para o lado da asa
        asa = {l: (ESTICADA_E if l == "E" else ASA_D(ESTICADA_E), k)}
        pe_k = suave((t - 0.55) / 0.5) * (1 - suave((t - 1.95) / 0.55))                 # a perna do mesmo lado estica para tras
        pes = {l: V((0.012 * s * pe_k, 0.075 * pe_k, 0.05 * pe_k))}; ext = {"asa": asa, "apoio": {l: pe_k < 1e-3}, "rola_pe": {l: R(-30) * pe_k}}   # dedos para cima (r2: +35 enfiava os dedos no chao)
        return r, raiz + V((-0.006 * s * pk, 0, -0.004 * pk)), pes, ext
    return f
# virar no lugar: o jogo gira o modelo; cada pe da passinhos em arco em torno do centro (apoio = ponto fixo no mundo)
GIRO_GS = 60.0; T_PASSO = 0.5; DUR_VIR = 2 * T_PASSO * 2
PIVO = BD["Raiz"].head_local.copy()
def c_virar(sinal):
    w = R(GIRO_GS) * sinal
    def no_arco(l, ang):
        p_ = REP[l] - PIVO; c_, s_ = math.cos(ang), math.sin(ang)
        return V((PIVO.x + p_.x * c_ - p_.y * s_, PIVO.y + p_.x * s_ + p_.y * c_, REP[l].z)) - REP[l]
    def f(t):
        r, raiz = base_rep(); pes = {}; ext = {"apoio": {}, "giro_pe": {}}; T = 2 * T_PASSO; ap = 0.6
        for l, fase in (("E", 0.0), ("D", 0.5)):
            phi = t / T + fase; n_ = math.floor(phi); fr = phi - n_; tc = (n_ - fase) * T; tm = tc + ap * T / 2; meia = w * ap * T / 2
            if fr < ap: pes[l] = no_arco(l, -w * (t - tm)); ext["giro_pe"][l] = -w * (t - tm); ext["apoio"][l] = True
            else:
                u = (fr - ap) / (1 - ap); p0, p1 = no_arco(l, -meia), no_arco(l, meia)
                pes[l] = p0.lerp(p1, suave(u)) + V((0, 0, 0.022 * math.sin(math.pi * u))); ext["giro_pe"][l] = -meia + 2 * meia * suave(u); ext["apoio"][l] = False
        bal = math.sin(2 * math.pi * t / T)
        soma(r, "Coluna2", [(Y, R(3) * bal)]); soma(r, "Pelve", [(Y, R(3) * bal)])     # balanca de um pe para o outro
        soma(r, "Cabeca", [(Z, R(12) * sinal)]); soma(r, "Pescoco2", [(Z, R(8) * sinal)])   # a cabeca ja olha para onde vira
        return r, raiz + V((0.003 * bal, 0, -0.004 - 0.003 * abs(bal))), pes, ext
    return f
# saltitar: pulinhos com os dois pes juntos; o jogo move o modelo a V_SAL; pes presos ao chao no apoio
T_SAL, L_SAL, AP_SAL = 0.5, 0.09, 0.5; V_SAL = L_SAL / T_SAL; DUR_SAL = 2 * T_SAL
def c_saltitar(t):
    r, raiz = base_rep(); u = (t % T_SAL) / T_SAL; pes = {}; ext = {"apoio": {}, "rola_pe": {}}
    no_ar = u >= AP_SAL; ua = (u - AP_SAL) / (1 - AP_SAL) if no_ar else 0.0
    for l in "ED":
        if not no_ar: dy = -L_SAL / 2 + V_SAL * (u * T_SAL)                               # apoio: pe recua com o deslocamento
        else: dy = L_SAL / 2 - L_SAL * suave(ua)                                          # no ar: pe volta para a frente
        pes[l] = V((0, dy, 0.045 * math.sin(math.pi * ua) if no_ar else 0.0)); ext["apoio"][l] = not no_ar   # pes sobem com o corpo
        ext["rola_pe"][l] = R(25) * math.sin(math.pi * ua) if no_ar else 0.0
    agacha = math.sin(math.pi * min(1.0, u / AP_SAL)) if not no_ar else 0.0               # agacha no apoio, estica no salto
    alto = 0.035 * math.sin(math.pi * ua) if no_ar else 0.0
    soma(r, "Coluna2", [(X, R(6) * agacha - R(4) * math.sin(math.pi * ua))]); soma(r, "Cauda", [(X, R(10) * agacha - R(8) * math.sin(math.pi * ua))])   # (r2: no agachamento a ponta da cauda raspava o chao)
    asa = {l: (MEIO_ABERTA_E if l == "E" else ASA_D(MEIO_ABERTA_E), 0.35 * math.sin(math.pi * ua) if no_ar else 0.0) for l in "ED"}
    ext["asa"] = asa
    return r, raiz + V((0, 0, alto - 0.018 * agacha)), pes, ext
# nome: (funcao, duracao, laco, velocidade [PROPOSTA], giro graus/s [PROPOSTA], entrada, saida)
CLIPES = {"Repouso": (c_repouso, T_REP, True, 0.0, 0.0, "laco", "laco"),
          "OlharE": (c_olhar(1), DUR_OL, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
          "OlharD": (c_olhar(-1), DUR_OL, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
          "InclinarCabeca": (c_inclinar, DUR_INC, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
          "AjeitarPenas": (c_ajeitar, DUR_AJ, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
          "EsticarAsaE": (c_esticar("E"), DUR_EST, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
          "EsticarAsaD": (c_esticar("D"), DUR_EST, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
          "VirarNoLugarE": (c_virar(1), DUR_VIR, True, 0.0, GIRO_GS, "laco", "laco"),
          "VirarNoLugarD": (c_virar(-1), DUR_VIR, True, 0.0, -GIRO_GS, "laco", "laco"),
          "Saltitar": (c_saltitar, DUR_SAL, True, V_SAL, 0.0, "laco", "laco")}
if os.environ.get("CORUJA_LB"):                     # lote B (voo): so com a variavel; sem ela o lote A nao muda
    exec(open(os.path.join(AQUI, "clipes_coruja_lb.py"), encoding="utf-8").read())
if os.environ.get("CORUJA_LC"):                     # lote C (vida e caca): usa o voo do lote B
    if not os.environ.get("CORUJA_LB"): exec(open(os.path.join(AQUI, "clipes_coruja_lb.py"), encoding="utf-8").read())
    exec(open(os.path.join(AQUI, "clipes_coruja_lc.py"), encoding="utf-8").read())
if os.environ.get("CORUJA_LD"):                     # lote D (defesa/derrota, ESTUDO): usa os lotes B e C
    if not os.environ.get("CORUJA_LB") and not os.environ.get("CORUJA_LC"): exec(open(os.path.join(AQUI, "clipes_coruja_lb.py"), encoding="utf-8").read())
    if not os.environ.get("CORUJA_LC"): exec(open(os.path.join(AQUI, "clipes_coruja_lc.py"), encoding="utf-8").read())
    exec(open(os.path.join(AQUI, "clipes_coruja_ld.py"), encoding="utf-8").read())
QUAIS = ARGS[1].split(",") if len(ARGS) > 1 else list(CLIPES)
# ------------------------------------------------------------------ QA
gr = {g.index: g.name for g in CORPO.vertex_groups}; PE_V = {l: [] for l in PES}
for v in CORPO.data.vertices:
    if v.co.z > 0.03: continue
    for g in v.groups:
        for l, pe in PES.items():
            if gr[g.group] == pe and g.weight > 0.5: PE_V[l].append(v.index)
print("PES vertices", {l: len(v) for l, v in PE_V.items()})
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
def ang_q(qa, qb):
    g = math.degrees(qa.rotation_difference(qb).angle); return min(g, 360 - g)   # q e -q sao a mesma orientacao
def dif_pose(a, b):
    return max(ang_q(a[n].to_quaternion(), b[n].to_quaternion()) for n in a), max((a[n].translation - b[n].translation).length for n in a)
def pior_osso(a, b): return max(((ang_q(a[n].to_quaternion(), b[n].to_quaternion()), n) for n in a))
REF_REP = pose_de(c_repouso, 0.0)[1]
manifesto = {}; QUADROS = {}; APOIOS = {}; VPERS = {}
for nome in QUAIS:
    fn, dur, laco, vel, giro, ent, sai = CLIPES[nome][:7]; VF = CLIPES[nome][7] if len(CLIPES[nome]) > 7 else None; nq = int(round(dur * FPS)) + (0 if laco else 1); LIMITE[0] = 0
    quadros = []; APO = []; erro_ik = 0.0; zmin = 9.0; desl = {l: 0.0 for l in PES}; prev = None; ap_prev = {}
    for qi in range(nq + (1 if laco else 0)):
        t = qi / FPS; ext, pose = pose_de(fn, t)
        if laco and qi == nq: pose_fim = pose; break
        for l in PES: erro_ik = max(erro_ik, (PB["Tarso" + l].tail - ALVO[l].location).length)
        cs = malha(CORPO); zmin = min(zmin, float(cs[:, 2].min()), float(malha(CAB)[:, 2].min()))
        if prev is not None:
            for l in PES:
                apo = ext.get("apoio", {}).get(l, True)
                if apo and ap_prev.get(l, True) and PE_V[l]:
                    c_ = cs[PE_V[l]]; ang = math.radians(giro) / FPS; cw = c_ - np.array(PIVO)
                    cw = np.stack([cw[:, 0] * math.cos(ang) - cw[:, 1] * math.sin(ang), cw[:, 0] * math.sin(ang) + cw[:, 1] * math.cos(ang), cw[:, 2]], 1) + np.array(PIVO)
                    mov = cw - prev[PE_V[l]]; mov[:, 1] -= (VF(t - 0.5 / FPS) if VF else vel) / FPS; baixo = c_[:, 2] < 0.012
                    if baixo.any(): desl[l] = max(desl[l], float(np.abs(mov[baixo][:, :2]).max()))
        prev = cs; ap_prev = dict(ext.get("apoio", {})); quadros.append(pose); APO.append({l: bool(ext.get("apoio", {}).get(l, True)) for l in PES})
    salto = (0.0, "", 0); seq = quadros + ([pose_fim] if laco else [])
    for i_ in range(len(seq) - 1):
        for n_ in seq[i_]:
            a_ = ang_q(seq[i_][n_].to_quaternion(), seq[i_ + 1][n_].to_quaternion())
            if a_ > salto[0]: salto = (round(a_, 2), n_, i_)
    m_ = {"duracao_s": round(dur, 4), "quadros": nq, "laco": laco, "velocidade_u_s_PROPOSTA": round(vel, 4), "giro_graus_s_PROPOSTA": giro,
          "entrada": ent, "saida": sai, "erro_ik_max": round(erro_ik, 4), "pele_z_min_cm": round(zmin * 100, 2),
          "escorregao_pe_apoiado_max": {l: round(v, 4) for l, v in desl.items()}, "alvos_limitados": LIMITE[0], "maior_giro_entre_quadros_graus_osso_quadro": salto}
    if laco: m_["emenda_laco_graus_transl"] = [round(x, 3) for x in dif_pose(quadros[0], pose_fim)]
    else:
        def ref_de(txt):
            n0 = txt.split()[0]
            if n0 in globals().get("REF_EXTRA_C", {}): fn_, t_ = REF_EXTRA_C[n0]; return pose_de(fn_, t_)[1]
            return REF_REP if n0 not in CLIPES else pose_de(CLIPES[n0][0], 0.0)[1]
        RE, RS = ref_de(ent), ref_de(sai)
        m_["emenda_entrada_graus_transl"] = [round(x, 3) for x in dif_pose(RE, quadros[0])]
        m_["emenda_saida_graus_transl"] = [round(x, 3) for x in dif_pose(RS, quadros[-1])]
        m_["emenda_entrada_pior_osso"] = [round(pior_osso(RE, quadros[0])[0], 2), pior_osso(RE, quadros[0])[1]]
        m_["emenda_saida_pior_osso"] = [round(pior_osso(RS, quadros[-1])[0], 2), pior_osso(RS, quadros[-1])[1]]
    manifesto[nome] = m_; print("CLIPE", nome, json.dumps(m_), flush=True)
    ANT = {}
    for pose in quadros:                                             # mesmo hemisferio quadro a quadro (q e -q iguais; interpolacao nao)
        for n_, m in pose.items():
            q = m.to_quaternion()
            if n_ in ANT and ANT[n_].dot(q) < 0: q = -q
            ANT[n_] = q; pose[n_] = Matrix.Translation(m.translation) @ q.to_matrix().to_4x4()
    VPER = [round(VF(q_ / FPS), 4) for q_ in range(nq)] if VF else None
    dado = {"nome": "Coruja_" + nome, "fps": FPS, "loop": laco, "quadros": nq, "duracao": dur, "velocidade": round(vel, 4), "giro_graus_s": giro, "ossos": {},
            "apoio": {PES[l]: [int(x[l]) for x in APO] for l in PES}}
    if VPER: dado["v_perfil"] = VPER
    for pb in PB:
        s_ = []
        for pose in quadros:
            m = pose[pb.name]; q = m.to_quaternion(); tt = m.translation
            s_ += [round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(tt.x, 5), round(tt.y, 5), round(tt.z, 5)]
        dado["ossos"][pb.name] = s_
    json.dump(dado, open(os.path.join(OUT, "json", "Coruja_%s.json" % nome), "w"), separators=(",", ":"))
    QUADROS[nome] = quadros; APOIOS[nome] = dado["apoio"]; VPERS[nome] = VPER
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
for nome, quadros in QUADROS.items():
    act = bpy.data.actions.get("Coruja_" + nome) or bpy.data.actions.new("Coruja_" + nome); arm.animation_data.action = act
    act["apoio_json"] = json.dumps(APOIOS[nome]); act["loop"] = CLIPES[nome][2]; act["velocidade_PROPOSTA"] = CLIPES[nome][3]; act["giro_graus_s_PROPOSTA"] = CLIPES[nome][4]
    for qi, pose in enumerate(quadros):
        for pb in PB:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    if VPERS.get(nome): act["v_perfil"] = VPERS[nome]
    act.use_fake_user = True
arm.animation_data.action = None; zerar()
for o in list(ALVO.values()) + list(POLO.values()): bpy.data.objects.remove(o)
for pb in PB:
    for c in list(pb.constraints): pb.constraints.remove(c)
json.dump(manifesto, open(os.path.join(OUT, "manifesto_clipes.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, os.environ.get("CORUJA_ANIM_ARQ", "Coruja_Clipes_LA.blend"))); print("ANIM_OK", list(QUADROS))
