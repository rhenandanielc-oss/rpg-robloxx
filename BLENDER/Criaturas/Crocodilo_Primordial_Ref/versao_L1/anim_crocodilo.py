"""Clipes do Crocodilo Primordial (procedurais, no lugar; o jogo move o modelo). Cada quadro: alvos IK dos pes, coluna,
cauda, cabeca e mandibula; o IK resolve as patas e a pose final de cada osso e gravada em FK (acao 'Croc_<clipe>'),
pronta para o JSON do Studio. Principios do padrao de movimento do projeto: cauda em onda base->ponta com atraso,
corpo ondulando lateralmente, antecipacao -> golpe -> recuperacao nos ataques; pe apoiado nao escorrega na velocidade
informada (v = passo / tempo de apoio).
Uso: blender -b CR_Crocodilo_Rig.blend -P anim_crocodilo.py -- <saida_dir> [clipes,separados]"""
import bpy, sys, os, math, json
from mathutils import Vector as V, Matrix, Quaternion
A = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["CR_Croc_Rig"]; PB = arm.pose.bones; BD = arm.data.bones
ANG_BOCA = math.radians(arm["ang_boca"])            # o Meshy veio com a boca aberta ~14 graus (repouso do rig)
FECHADA = -1.00 * ANG_BOCA                           # Lote 1 (rig v2: arcadas separadas pela topologia): fecha 100%
ABRE_MAX = 12.0                                      # graus alem da boca do Meshy (~14 = a da referencia); conferido sem fios
PATAS = {"MaoE": ("dian", 1, 0.0), "PeD": ("tras", -1, 0.0), "MaoD": ("dian", -1, 0.5), "PeE": ("tras", 1, 0.5)}  # pares diagonais
ALVO = {k: bpy.data.objects["IK_" + k] for k in PATAS}
REPOUSO = {k: o.location.copy() for k, o in ALVO.items()}
# a traseira direita do Meshy esta aberta para o lado (x -3,6 contra 2,7 da esquerda) e quase esticada: a base dela vai
# 0,6 para dentro em todos os clipes (mais alcance e mais simetria; a malha nao e reposicionada)
BASE = {"PeD": V((0.6, 0.0, 0.0))}
for k, d in BASE.items(): REPOUSO[k] = REPOUSO[k] + d
ROT0 = {k: o.rotation_quaternion.copy() for k, o in ALVO.items()}
CAUDA = ["Cauda%d" % i for i in range(1, 9)]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def rot_mundo(nome, eixos):
    """rotacao em eixos do MUNDO (X = arfagem, Z = guinada, Y = rolagem) convertida para o espaco local do osso"""
    r = BD[nome].matrix_local.to_3x3(); q = Matrix.Identity(3)
    for eixo, ang in eixos:
        q = Matrix.Rotation(ang, 3, eixo) @ q
    return (r.inverted() @ q @ r).to_quaternion()
def zerar():
    for pb in PB:
        pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for k, o in ALVO.items(): o.location = REPOUSO[k].copy(); o.rotation_quaternion = ROT0[k].copy()
def passo(fase, L, apoio, alt, dobra=22.0):
    """deslocamento do pe no ciclo (0..1): apoio = recua de -L/2 a +L/2 (frente = -Y); balanco = sobe e avanca.
    Arfagem do pe: dedos descem na saida (calcanhar sobe) e sobem antes de pousar; plano no apoio."""
    f = fase % 1.0
    if f < apoio:
        return V((0, -L / 2 + L * f / apoio, 0)), 0.0
    u = (f - apoio) / (1 - apoio); s = suave(u)
    lev = alt * math.sin(math.pi * u)
    if u < 0.6:   # dedos descem so o que a elevacao permite (ponta nunca abaixo do chao; pe ~1,3 de comprimento)
        arf = min(dobra * math.sin(math.pi * min(1.0, u / 0.6)), 0.85 * math.degrees(math.asin(min(1.0, lev / 1.3))))
    else:         # dedos sobem antes de pousar e voltam a zero aos 90% (laco fecha sem salto, inclusive na corrida de 16 quadros)
        arf = -0.45 * dobra * math.sin(math.pi * min(1.0, (u - 0.6) / 0.3))
    return V((0, L / 2 - L * s, lev)), arf
def onda_cauda(t, T, amp_base, amp_ponta, atraso=0.10, eixo="Z", fase0=0.0):
    out = {}
    for i, nm in enumerate(CAUDA):
        k = i / 7; a = amp_base + (amp_ponta - amp_base) * k
        out[nm] = [(V((0, 0, 1)) if eixo == "Z" else V((1, 0, 0)), math.radians(a) * math.sin(2 * math.pi * (t / T - atraso * i) + fase0))]
    return out

# ------------------------------------------------------------------ definicao dos clipes: t (s) -> pose
def clipe_repouso(t):
    T = 4.0; r = {}
    r.update(onda_cauda(t, T, 0.6, 2.2, 0.06))                     # Lote 1: cauda mais calma (sem oscilacao constante exagerada)
    r["Coluna1"] = [(V((0, 0, 1)), math.radians(0.5) * math.sin(2 * math.pi * t / T))]
    r["Cabeca"] = [(V((1, 0, 0)), math.radians(-1.0) * math.sin(2 * math.pi * t / T)), (V((0, 0, 1)), math.radians(2.0) * math.sin(2 * math.pi * t / T + 1))]
    r["Mandibula"] = [(V((1, 0, 0)), FECHADA + math.radians(0.6) * (0.5 + 0.5 * math.sin(2 * math.pi * t / T)))]
    return r, V((0, 0, 0.035 * math.sin(2 * math.pi * t / T))), {}
def marcha(T, L, apoio, alt, flex_col, amp_cauda, bob):
    def f(t):
        u = t / T; r = {}; pes = {}
        for k, (par, sx, fase) in PATAS.items():
            d, arf = passo(u + fase, L, apoio, alt)
            pes[k] = (d, arf)
        ang = math.radians(flex_col) * math.sin(2 * math.pi * u)
        r["Pelve"] = [(V((0, 0, 1)), -ang * 0.6)]
        r["Coluna1"] = [(V((0, 0, 1)), ang * 0.7)]; r["Coluna2"] = [(V((0, 0, 1)), ang * 0.6)]
        r["Pescoco"] = [(V((0, 0, 1)), -ang * 0.8)]; r["Cabeca"] = [(V((0, 0, 1)), -ang * 0.5)]
        r.update(onda_cauda(t, T, amp_cauda * 0.5, amp_cauda, 0.09, fase0=-0.6))
        r["Mandibula"] = [(V((1, 0, 0)), FECHADA)]
        raiz = V((0, 0, bob * math.cos(4 * math.pi * u)))
        return r, raiz, pes
    return f
def clipe_nado(t):
    """crocodilo nadando: patas encostadas nos flancos apontando para tras (dedos para tras), propulsao so pela cauda em
    onda base->ponta com atraso; a ondulacao comeca no meio do tronco; pescoco/cabeca cancelam a guinada (olhar estavel)"""
    T = 2.0; u = t / T; r = {}; pes = {}
    for k, (par, sx, fase) in PATAS.items():
        if par == "dian": pes[k] = (V((-0.55 * sx, 2.10, 1.35)), 140.0)      # dedos para tras, sola para cima e para fora
        else: pes[k] = (V((-0.30 * sx, 2.00, 1.20)), 140.0)
    r.update(onda_cauda(t, T, 10.0, 24.0, 0.12))
    ang = math.radians(5.0) * math.sin(2 * math.pi * u + 0.9)
    r["Pelve"] = [(V((0, 0, 1)), -ang * 0.8)]
    r["Coluna1"] = [(V((0, 0, 1)), ang * 0.6)]; r["Coluna2"] = [(V((0, 0, 1)), ang * 0.3)]
    r["Pescoco"] = [(V((0, 0, 1)), -ang * 0.6)]; r["Cabeca"] = [(V((0, 0, 1)), -ang * 0.3), (V((1, 0, 0)), math.radians(-2))]
    r["Mandibula"] = [(V((1, 0, 0)), FECHADA)]
    return r, V((0, 0, 0.03 * math.sin(4 * math.pi * u))), pes
def clipe_mordida(t):
    """antecipacao (recolhe e abre) -> bote com estalo da mandibula -> recuperacao"""
    r = {}; abre, fecha_ = 0.0, 0.0
    a = suave(t / 0.30); b = suave((t - 0.30) / 0.12); c = suave((t - 0.55) / 0.45)
    boca = (1 - b) * (math.radians(ABRE_MAX) * a) + b * FECHADA             # estalo ate 80% (100% atravessa o focinho)
    if t < 0.30: boca = FECHADA * (1 - a) + math.radians(ABRE_MAX) * a
    r["Mandibula"] = [(V((1, 0, 0)), boca)]
    erg = math.radians(-9) * a * (1 - b) + math.radians(4) * b * (1 - c)        # cabeca sobe na antecipacao, baixa no bote
    r["Cabeca"] = [(V((1, 0, 0)), erg)]; r["Pescoco"] = [(V((1, 0, 0)), erg * 0.5)]
    avanco = -0.25 * a * (1 - b) * -1 + (-0.9) * b * (1 - c)                      # recua 0,25 e da o bote 0,9 para a frente
    r.update({nm: [(V((0, 0, 1)), math.radians(3) * (i / 7) * math.sin(2 * math.pi * t))] for i, nm in enumerate(CAUDA)})
    return r, V((0, avanco, -0.05 * a * (1 - b))), {}
def clipe_ameaca(t):
    """ergue o corpo e a cabeca, abre muito a boca e segura (sibilo), tremor leve, fecha no fim"""
    r = {}; a = suave(t / 0.45); f = 1 - suave((t - 1.65) / 0.35)
    k = a * f
    boca = FECHADA * (1 - k) + math.radians(ABRE_MAX) * k + math.radians(0.6) * k * math.sin(2 * math.pi * t * 9)
    r["Mandibula"] = [(V((1, 0, 0)), boca)]
    r["Cabeca"] = [(V((1, 0, 0)), math.radians(-12) * k)]; r["Pescoco"] = [(V((1, 0, 0)), math.radians(-6) * k)]
    r["Coluna2"] = [(V((1, 0, 0)), math.radians(-3) * k)]
    r.update(onda_cauda(t, 0.9, 3.0 * k, 12.0 * k, 0.1))
    return r, V((0, 0, 0.35 * k)), {}
CLIPES = {  # nome: (funcao, duracao s, loop, velocidade de deslocamento em studs/s para o jogo)
    "Repouso": (clipe_repouso, 4.0, True, 0.0),
    "Andar": (marcha(1.5, 1.8, 0.65, 0.42, 7.0, 12.0, 0.05), 1.5, True, 1.8 / (0.65 * 1.5)),
    "Corrida": (marcha(16 / 30, 2.1, 0.45, 0.55, 11.0, 18.0, 0.08), 16 / 30, True, 2.1 / (0.45 * 16 / 30)),   # ciclo = 16 quadros inteiros
    "Nado": (clipe_nado, 2.0, True, 0.0),
    "Mordida": (clipe_mordida, 1.0, False, 0.0),
    "Ameaca": (clipe_ameaca, 2.0, False, 0.0),
}
QUAIS = A[1].split(",") if len(A) > 1 else list(CLIPES)

# ------------------------------------------------------------------ amostragem -> FK -> acao + JSON + QA
pes_ponta = {k: BD[k] for k in PATAS}
manifesto = {}
for nome in QUAIS:
    fn, dur, loop, vel = CLIPES[nome]
    nq = int(round(dur * FPS)) + (0 if loop else 1)
    quadros = []; erro_ik = 0.0; desliza = 0.0; chao_min = 9.0; prev = None
    for qi in range(nq):
        t = qi / FPS
        zerar(); rots, raiz, pes = fn(t)
        PB["Raiz"].location = (rot_mundo("Raiz", []) .to_matrix().inverted() @ BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz)
        for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
        for k, d in pes.items():
            ang_p = 0.0
            if isinstance(d, tuple): d, ang_p = d
            ALVO[k].location = REPOUSO[k] + d
            if ang_p: ALVO[k].rotation_quaternion = Quaternion((1, 0, 0), math.radians(ang_p)) @ ROT0[k]
        bpy.context.view_layer.update()
        pose = {}
        for pb in PB:
            m = arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL")
            pose[pb.name] = m.copy()
        for k in PATAS:                                           # QA: punho no alvo; ponta do pe no chao
            e_ = (PB[k].head - ALVO[k].location).length
            if e_ > erro_ik: erro_ik = e_; pior = (k, round((t / dur + PATAS[k][2]) % 1.0, 2), tuple(round(c, 2) for c in (ALVO[k].location - REPOUSO[k])))
            chao_min = min(chao_min, PB[k].tail.z)
        if vel > 0:                                               # pe apoiado: velocidade = -v no jogo (anda para -Y)
            for k, (par, sx, fase) in PATAS.items():
                f = (t / dur + fase) % 1.0; apoio = 0.65 if nome == "Andar" else 0.45
                fp = ((t - 1 / FPS) / dur + fase) % 1.0
                if f < apoio and fp < apoio and fp < f and prev is not None:          # dois quadros seguidos em apoio
                    vy = (PB[k].head.y - prev[k]) * FPS
                    desliza = max(desliza, abs(vy - vel))
        prev = {k: PB[k].head.y for k in PATAS}
        quadros.append(pose)
    # grava acao FK (sem restricoes) para revisao no Blender
    act = bpy.data.actions.get("Croc_" + nome) or bpy.data.actions.new("Croc_" + nome)
    act["loop"] = loop; act["velocidade"] = vel
    manifesto[nome] = {"duracao": dur, "loop": loop, "quadros": nq, "velocidade_studs_s": round(vel, 2),
                       "erro_ik_max": round(erro_ik, 4), "desliza_pe_max_studs_s": round(desliza, 3), "ponta_pe_min_z": round(chao_min, 3)}
    print("CLIPE", nome, manifesto[nome], flush=True)
    if erro_ik > 0.02: print("   pior IK:", pior)
    dado = {"nome": "Crocodilo_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel, 3), "ossos": {}}
    for pb in PB:
        seq = []
        for pose in quadros:
            m = pose[pb.name]; q = m.to_quaternion(); tt = m.translation
            seq += [round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(tt.x, 5), round(tt.y, 5), round(tt.z, 5)]
        dado["ossos"][pb.name] = seq
    with open(os.path.join(OUT, "Crocodilo_%s.json" % nome), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
    globals().setdefault("QUADROS", {})[nome] = quadros
# acoes FK assadas (as restricoes ficam desligadas para tocar a acao)
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
for nome, quadros in QUADROS.items():
    act = bpy.data.actions["Croc_" + nome]; arm.animation_data.action = act
    for qi, pose in enumerate(quadros):
        for pb in PB:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    act.use_fake_user = True
arm.animation_data.action = None; zerar()
for pb in PB:
    for c in pb.constraints: c.mute = False
json.dump(manifesto, open(os.path.join(OUT, "manifesto_clipes.json"), "w"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "CR_Crocodilo_Anim.blend"))
print("ANIM_OK", list(QUADROS))
