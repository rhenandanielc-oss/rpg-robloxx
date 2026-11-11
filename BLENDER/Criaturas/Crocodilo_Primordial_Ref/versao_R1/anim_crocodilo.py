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
RECUO_DIAN = 0.30
def marcha(T, L, apoio, alt, flex_col, amp_cauda, bob):
    def f(t):
        u = t / T; r = {}; pes = {}
        for k, (par, sx, fase) in PATAS.items():
            d, arf = passo(u + fase, L, apoio, alt)
            # dianteiras: passo centrado 0,3 mais para tras (sob o ombro). Pousar no ponto mais a frente com a pata quase
            # esticada fazia o IK girar o antebraco 26,7 graus num quadro (retorno do laco da Corrida); mesma passada e velocidade
            if par == "dian": d = d + V((0, RECUO_DIAN, 0))
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

# ================================================================== Lote 2: locomocao, transicoes e agua
from mathutils import Matrix as _M
def _interp(x, pts):
    if x <= pts[0][0]: return pts[0][1]
    for (a, b), (c, d) in zip(pts, pts[1:]):
        if x <= c: return b + (d - b) * (x - a) / (c - a)
    return pts[-1][1]
GAIT_F = [(0.0, 0.0), (0.4, 0.40), (1.85, 1 / 1.5), (8.75, 30 / 16)]       # ciclos/s (Andar e Corrida atuais nos extremos)
GAIT_DUTY = [(0.0, 0.70), (1.85, 0.65), (8.75, 0.45)]
GAIT_ALT = [(0.0, 0.35), (1.85, 0.42), (8.75, 0.55)]
GAIT_FLEX = [(0.0, 0.0), (1.85, 7.0), (8.75, 11.0)]            # parado: coluna e cauda voltam ao neutro (emenda com o Repouso)
GAIT_CAUDA = [(0.0, 0.0), (1.85, 12.0), (8.75, 18.0)]
PIVO = V((0, (REPOUSO["MaoE"].y + REPOUSO["PeE"].y + REPOUSO["MaoD"].y + REPOUSO["PeD"].y) / 4, 0))   # centro entre as patas
R_GIRO = 4.0                                                     # raio efetivo (pe-pivo) para cadencia no giro
LIM_APOIO = {"dian": 1.10, "tras": 1.15}                         # pe apoiado levanta ao passar disto atras do neutro (alcance)
LIM_FRENTE = {"dian": 0.80, "tras": 1.00}                        # pouso no maximo isto a frente do neutro
def NEUTRO(k):
    return REPOUSO[k] + (V((0, RECUO_DIAN, 0)) if PATAS[k][0] == "dian" else V((0, 0, 0)))
def _arf(u, dobra=22.0, lev=0.3):
    if u < 0.6: return min(dobra * math.sin(math.pi * min(1.0, u / 0.6)), 0.85 * math.degrees(math.asin(min(1.0, lev / 1.3))))
    return -0.45 * dobra * math.sin(math.pi * min(1.0, (u - 0.6) / 0.3))
def corpo_gait(r, t, fase_mae, u_eq, freq, sinal_curva=0.0):
    """coluna/cabeca/cauda acompanhando a marcha (mesma linguagem do Andar/Corrida) + curva constante opcional"""
    ang = math.radians(_interp(u_eq, GAIT_FLEX)) * math.sin(2 * math.pi * fase_mae)
    cv = math.radians(9.0) * sinal_curva
    r["Pelve"] = [(V((0, 0, 1)), -ang * 0.6 - cv * 0.3)]
    r["Coluna1"] = [(V((0, 0, 1)), ang * 0.7 + cv * 0.5)]; r["Coluna2"] = [(V((0, 0, 1)), ang * 0.6 + cv * 0.5)]
    r["Pescoco"] = [(V((0, 0, 1)), -ang * 0.8 + cv * 0.8)]; r["Cabeca"] = [(V((0, 0, 1)), -ang * 0.5 + cv * 0.6)]
    amp = _interp(u_eq, GAIT_CAUDA)
    for i, nm in enumerate(CAUDA):
        a = math.radians(amp * (0.5 + 0.5 * i / 7)) * math.sin(2 * math.pi * (fase_mae - 0.09 * i) - 0.6)
        r[nm] = [(V((0, 0, 1)), a - cv * 0.35 * (i / 7))]
    r["Mandibula"] = [(V((1, 0, 0)), FECHADA)]

# ---- viradas no lugar (laco): o jogo gira o modelo em torno do PIVO; o pe apoiado gira ao contrario no espaco do modelo
def virada(sentido, T=1.5, theta=13.0, apoio=0.65, alt=0.40):      # 24 e 16 graus/apoio passavam do alcance das dianteiras
    th = math.radians(theta); w = sentido * th / (apoio * T)          # rad/s de sincronizacao
    def f(t):
        u = t / T; r = {}; pes = {}; apoiados = set()
        for k, (par, sx, fase) in PATAS.items():
            fk = (u + fase) % 1.0; N = REPOUSO[k]          # viradas: pe no repouso (o recuo das dianteiras e da Corrida)
            if par == "dian": N = N + V((-0.25 * sx, 0, 0))   # dianteiras 0,25 para dentro: o fim do apoio passava do alcance (MaoE q29)
            if fk < apoio:
                a = sentido * (th / 2 - th * fk / apoio); lev = 0.0; arf = 0.0; apoiados.add(k)
            else:
                v_ = (fk - apoio) / (1 - apoio); a = sentido * (-th / 2 + th * suave(v_)); lev = alt * math.sin(math.pi * v_); arf = _arf(v_, lev=lev)
            Pm = PIVO + _M.Rotation(a, 3, "Z") @ (N - PIVO) + V((0, 0, lev))
            pes[k] = (Pm - REPOUSO[k], arf, a)                 # guinada do pe = mesmo angulo: a sola fica parada no mundo
        corpo_gait(r, t, u, 1.0, 1 / T, sentido)
        Tm = _M.Translation(PIVO) @ _M.Rotation(w * t, 4, "Z") @ _M.Translation(-PIVO)
        return r, V((0, 0, 0.03 * math.cos(4 * math.pi * u))), pes, {"T": Tm, "apoio": apoiados}
    return f, math.degrees(w)

# ---- planejador de passos para transicoes (nao laco): perfil(t) -> (v studs/s para a frente, w rad/s)
def planejado(dur, perfil, extra=None, inicio=None):
    """inicio = (L, apoio, alt, T) do laco de origem: os pes comecam no estado da fase 0 desse laco (emenda sem salto)"""
    nq = int(round(dur * FPS)) + 1; dt = 1.0 / FPS
    poses = []; pos = V((0, 0, 0)); psi = 0.0; s_ = 0.0
    for i in range(nq + 40):                                      # +40 quadros para prever pousos no fim
        t = i * dt; v, w = perfil(min(t, dur)); poses.append((pos.copy(), psi, v, w, s_))
        pos = pos + _M.Rotation(psi, 3, "Z") @ V((0, -v, 0)) * dt; psi += w * dt; s_ += v * dt
    def Tm(i):
        p_, ps, _, _, _ = poses[max(0, min(len(poses) - 1, i))]; return _M.Translation(p_) @ _M.Rotation(ps, 4, "Z")
    trilha = {}                                                   # pe -> lista por quadro (pos_modelo, arfagem, apoiado)
    fase_mae = []
    i_parado = next((i for i in range(nq) if abs(poses[i][2]) < 0.05 and abs(poses[i][3]) < 0.01 and i > 0), None)
    for k, (par, sx, fase) in PATAS.items():
        N = NEUTRO(k); fi = fase; Pw = Tm(0) @ N; sw = None; out = []; acomodou = False
        if inicio:                                                # estado do laco de origem na fase 0
            L0, ap0, alt0, T0 = inicio; d0, _ = passo(fase, L0, ap0, alt0)
            if fase % 1.0 < ap0: Pw = Tm(0) @ (N + d0)
            else:
                n_sw = (1 - ap0) * T0 * FPS; u0 = (fase % 1.0 - ap0) / (1 - ap0); i0 = -int(round(u0 * n_sw)); i1 = i0 + max(4, int(round(n_sw)))
                sw = [i0, i1, Tm(0) @ (N + V((0, L0 / 2, 0))), Tm(i1) @ (N + V((0, -L0 / 2, 0))), alt0]
        for i in range(nq):
            v, w = poses[i][2], poses[i][3]; u_eq = max(abs(v), abs(w) * R_GIRO)
            fq = _interp(u_eq, GAIT_F); duty = _interp(u_eq, GAIT_DUTY); alt = _interp(u_eq, GAIT_ALT)
            if sw is None:
                exc = (Tm(min(i + 1, nq - 1)).inverted() @ Pw - N).y   # quanto o pe apoiado estara para tras do neutro no proximo quadro
                forcar = exc > (1.00 if k == "PeD" else LIM_APOIO[par])   # PeD: menos alcance (aberta no Meshy)
                if fq > 0.05 or forcar:
                    fi += fq * dt
                    if fi % 1.0 >= duty or forcar:                # entra no balanco
                        # pousa meio passo a frente do neutro NO INSTANTE do pouso (testado: mirar o meio do proximo apoio com a
                        # cadencia atual jogava o pe 3,3 a frente durante a aceleracao)
                        dur_sw = min(0.5, max(0.12, (1 - duty) / max(fq, 0.8))); i_land = i + max(4, int(round(dur_sw * FPS)))
                        v_l, w_l = poses[i_land][2], poses[i_land][3]; u_l = max(abs(v_l), abs(w_l) * R_GIRO)
                        f_l = _interp(u_l, GAIT_F); d_l = _interp(u_l, GAIT_DUTY)
                        meio = min(LIM_FRENTE[par], (v_l * d_l / (2 * f_l)) if f_l > 0.05 else 0.0)   # desacelerando: nao pousa alem do alcance
                        sw = [i, i_land, Pw.copy(), Tm(i_land) @ (N + V((0, -meio, 0))), alt]
                else:
                    fi = math.floor(fi) + min(fi % 1.0, duty * 0.999)   # parado: nao comeca balanco novo
                    # acomodacao: parado, o pe fora do neutro da um passo curto ate ele (pares diagonais em tempos diferentes)
                    Pm_ = Tm(i).inverted() @ Pw
                    if (not acomodou and i_parado is not None and i >= i_parado + int(round((0.0 if fase < 0.25 else 0.40) * FPS))
                            and (Pm_ - N).length > 0.25):
                        acomodou = True; sw = [i, i + int(round(0.35 * FPS)), Pw.copy(), Tm(i + int(round(0.35 * FPS))) @ N, 0.30]
                if sw is None:
                    out.append((Tm(i).inverted() @ Pw, 0.0, True)); continue
            i0, i1, P0, P1, alt_ = sw
            uu = min(1.0, (i - i0) / max(1, i1 - i0)); lev = alt_ * math.sin(math.pi * uu)
            Pw_i = P0.lerp(P1, suave(uu)) + V((0, 0, lev))
            out.append((Tm(i).inverted() @ Pw_i, _arf(uu, lev=lev), False))
            if uu >= 1.0:
                Pw = P1.copy(); sw = None; fi = math.ceil(fi - 1e-6) + 1e-6
        trilha[k] = out
    fm = 0.0
    for i in range(nq):
        v, w = poses[i][2], poses[i][3]; u_eq = max(abs(v), abs(w) * R_GIRO); fm += _interp(u_eq, GAIT_F) * dt; fase_mae.append(fm)
    desloc = [round(poses[i][4], 4) for i in range(nq)]
    def f(t):
        i = min(nq - 1, int(round(t * FPS))); r = {}; pes = {}; apoiados = set()
        v, w = poses[i][2], poses[i][3]; u_eq = max(abs(v), abs(w) * R_GIRO)
        for k in PATAS:
            Pm, arf, ap = trilha[k][i]; pes[k] = (Pm - REPOUSO[k], arf)
            if ap: apoiados.add(k)
        corpo_gait(r, t, fase_mae[i], u_eq, 0)
        acel = (poses[min(i + 1, nq - 1)][2] - poses[max(i - 1, 0)][2]) * FPS / 2
        # acelerando: peito baixa (ate 6 graus); freando: sobe so 2 (mais que isso levanta o ombro e tira o alcance das dianteiras)
        r["Pelve"] = r["Pelve"] + [(V((1, 0, 0)), math.radians(max(-2, min(4, 0.9 * acel))))]
        bob = 0.03 + 0.05 * min(1.0, u_eq / 8.75)
        raiz = V((0, 0, bob * math.cos(4 * math.pi * fase_mae[i])))
        info = {"T": Tm(i), "apoio": apoiados, "desloc": desloc}
        if extra: r, raiz, pes = extra(t, r, raiz, pes)
        return r, raiz, pes, info
    return f, desloc

def p_rampa(v0, v1, t0, t1):
    return lambda t: (v0 + (v1 - v0) * suave((t - t0) / (t1 - t0)), 0.0)

# ---- agua: patas recolhidas (mesma pose do Nado), pernas abertas para boiar
def pes_recolhidos():
    return {k: ((V((-0.55 * sx, 2.10, 1.35)) if par == "dian" else V((-0.30 * sx, 2.00, 1.20))), 140.0) for k, (par, sx, f_) in PATAS.items()}
def nado_corpo(r, t, T, amp_b, amp_p, curva=0.0, flex=5.0):
    u = t / T
    r.update(onda_cauda(t, T, amp_b, amp_p, 0.12))
    cv = math.radians(8.0) * curva
    for nm in CAUDA: r[nm] = [(r[nm][0][0], r[nm][0][1] - cv * 0.5)]
    ang = math.radians(flex) * math.sin(2 * math.pi * u + 0.9)
    r["Pelve"] = [(V((0, 0, 1)), -ang * 0.8 - cv * 0.3)]
    r["Coluna1"] = [(V((0, 0, 1)), ang * 0.6 + cv * 0.5)]; r["Coluna2"] = [(V((0, 0, 1)), ang * 0.3 + cv * 0.5)]
    r["Pescoco"] = [(V((0, 0, 1)), -ang * 0.6 + cv * 0.7)]; r["Cabeca"] = [(V((0, 0, 1)), -ang * 0.3 + cv * 0.5), (V((1, 0, 0)), math.radians(-2))]
    r["Mandibula"] = [(V((1, 0, 0)), FECHADA)]
def remada(t, T, sentido=0.0):
    """Lote R1 (referencia real): devagar o crocodilo abre as patas para se equilibrar e guiar; as TRASEIRAS remam (puxada
    para tras com o pe aberto, volta recolhida e de lado); as dianteiras ficam abertas, so corrigindo. Na curva lenta a
    traseira de FORA rema mais forte e a dianteira de DENTRO segura (pivo)."""
    pes = {}
    for k, (par, sx, fase) in PATAS.items():
        fora = 1.0 + 0.8 * sentido * sx if sentido else 1.0          # sentido +1 (esquerda): pata direita (sx -1) e a de fora
        if par == "dian":
            seg = 1.0 - 0.6 * max(0.0, -sentido * sx) if sentido else 1.0
            c_ = 0.06 * seg * math.sin(2 * math.pi * (t / T + fase))
            pes[k] = (V((0.45 * sx, 0.6 + c_, 0.9)), 55.0)
        else:
            u = (t / T + (0.0 if sx > 0 else 0.5)) % 1.0              # traseiras alternadas
            if u < 0.45:                                              # puxada: pe aberto vai para tras
                v = suave(u / 0.45); y = -0.25 + 0.75 * v; x = 0.45; z = 0.75 - 0.10 * math.sin(math.pi * v); ang = 55.0
            else:                                                     # volta: recolhida rente ao corpo
                v = suave((u - 0.45) / 0.55); y = 0.5 - 0.75 * v; x = 0.45 - 0.20 * math.sin(math.pi * v); z = 0.75 + 0.15 * math.sin(math.pi * v); ang = 55.0 + 60.0 * math.sin(math.pi * v)
            amp = min(1.25, fora)
            pes[k] = (V((x * sx, 0.7 + (y - 0.125) * amp, z)), ang)
    return pes
def clipe_nado_parado(t):
    """boiando: patas abertas para os lados, as traseiras remam devagar (alternadas) para manter a posicao; cauda so corrige
    (onda lenta e curta), cabeca parada"""
    T = 3.0; r = {}
    nado_corpo(r, t, T, 3.0, 9.0, 0.0, 2.0)
    return r, V((0, 0, 0.03 * math.sin(2 * math.pi * t / T))), remada(t, T)
def curva_lenta(sentido, T=3.0):
    """curva devagar (referencia real): patas abertas guiando, traseira de fora rema forte, cauda varre de leve para o lado"""
    def f(t):
        r = {}; nado_corpo(r, t, T, 4.0, 12.0, 0.6 * sentido, 2.5)
        return r, V((0, 0, 0.03 * math.sin(2 * math.pi * t / T))), remada(t, T, sentido)
    return f
def curva_aquatica(sentido, T=2.0):
    def f(t):
        r = {}; nado_corpo(r, t, T, 10.0, 24.0, sentido, 4.0)
        return r, V((0, 0, 0.03 * math.sin(4 * math.pi * t / T))), pes_recolhidos()
    return f
def mergulho(subindo):
    """superficie -> submerso (ou o contrario). Corpo arfa (nariz desce/sobe) pela Raiz; a profundidade e do jogo"""
    dur = 1.5
    def f(t):
        k = suave(t / dur); r = {}
        nado_corpo(r, t, 1.2, 12.0, 28.0, 0.0, 4.0)                    # cauda forte (impulso)
        arf_c = 18.0 * suave(t / 0.8) if not subindo else -14.0 * math.sin(math.pi * min(1.0, t / dur))   # nariz desce / sobe
        r["Raiz"] = [(V((1, 0, 0)), math.radians(arf_c))]
        r["Cabeca"] = r["Cabeca"] + [(V((1, 0, 0)), math.radians(6.0 if not subindo else -8.0) * math.sin(math.pi * min(1.0, t / dur)))]
        return r, V((0, 0, (-0.35 * k) if not subindo else (-0.35 * (1 - k)))), pes_recolhidos()
    return f, dur
def entrada_agua(t_ref=None):
    """anda devagar ate a agua, desacelera, recolhe as patas e passa a propulsao para a cauda"""
    dur = 2.2
    # testado na cena de margem (review/L2b): desacelerar ate 0 parava o corpo em cima da rampa (cauda e quadril entravam na
    # margem). Mantem a passada do Andar ate as patas sairem do chao; depois disso a velocidade e do jogo (nado).
    fp, desloc = planejado(dur, lambda t: (1.85, 0.0), inicio=(1.8, 0.65, 0.42, 1.5))
    rec = pes_recolhidos()
    def f(t):
        r, raiz, pes, info = fp(t); b = suave((t - 1.0) / 0.8)
        for k in PATAS:
            d0, a0 = pes[k]; d1, a1 = rec[k]; pes[k] = (d0.lerp(d1, b), a0 + (a1 - a0) * b)
        rn = {}; nado_corpo(rn, t, 2.0, 10.0 * b, 24.0 * b, 0.0, 5.0 * b)
        for nm in CAUDA: r[nm] = [(V((0, 0, 1)), r[nm][0][1] * (1 - b) + rn[nm][0][1])]
        # sem arfagem propria: a inclinacao do corpo vem do alinhamento ao fundo (jogo); testado na cena de margem, a arfagem
        # do clipe brigava com a rampa (IK 0,12 com as patas no chao)
        info["pes_corpo"] = b
        return r, raiz, pes, info          # sem baixar 0,35 no clipe: subir/descer a raiz para boiar e do jogo (emenda com Nado)
    return f, dur, desloc
def saida_agua():
    """nadando -> estende as patas ate o chao, apoia o peso (corpo sobe) e sai andando"""
    dur = 2.4
    fp, desloc = planejado(dur, lambda t: (1.85 * suave((t - 1.2) / 1.0), 0.0))
    rec = pes_recolhidos()
    def f(t):
        r, raiz, pes, info = fp(t); b = suave((t - 0.3) / 0.8)            # 0 recolhida -> 1 no chao
        for k, (par, sx, fase) in PATAS.items():
            d1, a1 = pes[k]; d0, a0 = rec[k]
            atraso = 0.0 if par == "dian" else 0.15                        # dianteiras alcancam o chao antes
            bk = suave((t - 0.3 - atraso) / 0.8)
            lev = 0.35 * math.sin(math.pi * bk) if 0 < bk < 1 else 0.0
            pes[k] = (d0.lerp(d1, bk) + V((0, 0, lev)), a0 + (a1 - a0) * bk)
            if bk < 1.0: info["apoio"].discard(k)
        rn = {}; nado_corpo(rn, t, 2.0, 10.0 * (1 - b), 24.0 * (1 - b), 0.0, 5.0 * (1 - b))
        for nm in CAUDA: r[nm] = [(V((0, 0, 1)), r[nm][0][1] * b + rn[nm][0][1])]
        # sem arfagem propria (testado: nariz para cima empurrava a cauda 1,25 para dentro da rampa); inclinacao = alinhamento ao fundo
        info["pes_corpo"] = 1.0 - b
        return r, raiz, pes, info          # idem: a raiz do jogo desce da altura de boiar ate o fundo
    return f, dur, desloc

CLIPES = {  # nome: (funcao, duracao s, loop, velocidade de deslocamento em studs/s para o jogo)
    "Repouso": (clipe_repouso, 4.0, True, 0.0),
    "Andar": (marcha(1.5, 1.8, 0.65, 0.42, 7.0, 12.0, 0.05), 1.5, True, 1.8 / (0.65 * 1.5)),
    "Corrida": (marcha(16 / 30, 2.1, 0.45, 0.55, 11.0, 18.0, 0.08), 16 / 30, True, 2.1 / (0.45 * 16 / 30)),   # ciclo = 16 quadros inteiros
    "Nado": (clipe_nado, 2.0, True, 0.0),
    "Mordida": (clipe_mordida, 1.0, False, 0.0),
    "Ameaca": (clipe_ameaca, 2.0, False, 0.0),
}
EXTRA = {}            # nome -> dados de sincronizacao para o jogo (giro, perfil de deslocamento)
PES_CORPO = {"Nado": 1.0, "NadoParado": 1.0, "CurvaAquaticaEsquerda": 1.0, "CurvaAquaticaDireita": 1.0, "Mergulho": 1.0, "Emersao": 1.0,
             "CurvaLentaEsquerda": 1.0, "CurvaLentaDireita": 1.0}
_vE, _wE = virada(+1); _vD, _wD = virada(-1)
CLIPES["VirarEsquerda"] = (_vE, 1.5, True, 0.0); EXTRA["VirarEsquerda"] = {"giro_graus_s": round(_wE, 2), "pivo_y": round(PIVO.y, 3)}
CLIPES["VirarDireita"] = (_vD, 1.5, True, 0.0); EXTRA["VirarDireita"] = {"giro_graus_s": round(_wD, 2), "pivo_y": round(PIVO.y, 3)}
INI_ANDAR = (1.8, 0.65, 0.42, 1.5); INI_CORRIDA = (2.1, 0.45, 0.55, 16 / 30)   # parametros dos lacos Andar/Corrida
for nome_, dur_, perf_, ini_ in (("Arrancada", 1.4, p_rampa(0.0, 8.75, 0.15, 1.15), None), ("Frenagem", 1.6, p_rampa(8.75, 0.0, 0.0, 0.9), INI_CORRIDA),
                           ("RepousoParaAndar", 1.4, p_rampa(0.0, 1.85, 0.1, 1.0), None), ("AndarParaRepouso", 1.8, p_rampa(1.85, 0.0, 0.0, 1.0), INI_ANDAR),
                           ("AndarParaCorrida", 1.1, p_rampa(1.85, 8.75, 0.0, 0.8), INI_ANDAR), ("CorridaParaAndar", 1.1, p_rampa(8.75, 1.85, 0.0, 0.8), INI_CORRIDA)):
    _f, _d = planejado(dur_, perf_, inicio=ini_)
    if nome_ == "Arrancada":                                       # antecipacao: agacha e baixa a cabeca antes do arranque
        _f0 = _f
        def _f(t, _f0=_f0):
            r, raiz, pes, info = _f0(t); k = math.sin(math.pi * min(1.0, t / 0.35)) if t < 0.35 else 0.0
            r["Cabeca"] = r["Cabeca"] + [(V((1, 0, 0)), math.radians(5) * k)]
            return r, raiz + V((0, 0, -0.12 * k)), pes, info
    if nome_ == "Frenagem":                                        # freia: peito sobe, cabeca e cauda compensam
        _f1 = _f
        def _f(t, _f1=_f1):
            r, raiz, pes, info = _f1(t); k = math.sin(math.pi * min(1.0, t / 1.0)) if t < 1.0 else 0.0
            r["Cabeca"] = r["Cabeca"] + [(V((1, 0, 0)), math.radians(-6) * k)]
            for i, nm in enumerate(CAUDA): r[nm] = r[nm] + [(V((1, 0, 0)), math.radians(2.5) * k)]
            return r, raiz, pes, info
    CLIPES[nome_] = (_f, dur_, False, 0.0); EXTRA[nome_] = {"deslocamento_studs": _d, "v_inicio": round(perf_(0)[0], 2), "v_fim": round(perf_(dur_)[0], 2)}
CLIPES["NadoParado"] = (clipe_nado_parado, 3.0, True, 0.0)
CLIPES["CurvaLentaEsquerda"] = (curva_lenta(+1), 3.0, True, 0.0); EXTRA["CurvaLentaEsquerda"] = {"giro_graus_s_proposto": 12.0, "obs": "nado lento: patas guiando (referencia real)"}
CLIPES["CurvaLentaDireita"] = (curva_lenta(-1), 3.0, True, 0.0); EXTRA["CurvaLentaDireita"] = {"giro_graus_s_proposto": -12.0, "obs": "nado lento: patas guiando (referencia real)"}
CLIPES["CurvaAquaticaEsquerda"] = (curva_aquatica(+1), 2.0, True, 0.0); EXTRA["CurvaAquaticaEsquerda"] = {"giro_graus_s_proposto": 25.0}
CLIPES["CurvaAquaticaDireita"] = (curva_aquatica(-1), 2.0, True, 0.0); EXTRA["CurvaAquaticaDireita"] = {"giro_graus_s_proposto": -25.0}
_m, _md = mergulho(False); CLIPES["Mergulho"] = (_m, _md, False, 0.0)
_e, _ed = mergulho(True); CLIPES["Emersao"] = (_e, _ed, False, 0.0)
_ea, _ead, _eadl = entrada_agua(); CLIPES["EntradaAgua"] = (_ea, _ead, False, 0.0); EXTRA["EntradaAgua"] = {"deslocamento_studs": _eadl}
_sa, _sad, _sadl = saida_agua(); CLIPES["SaidaAgua"] = (_sa, _sad, False, 0.0); EXTRA["SaidaAgua"] = {"deslocamento_studs": _sadl}

# ================================================================== Lote 3: reacoes e vida (pes plantados; so visual, sem regra)
X_, Y_, Z_ = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
def kf(t, pts):
    """curva por chaves (t, valor) com interpolacao suave entre elas"""
    if t <= pts[0][0]: return pts[0][1]
    for (a, b), (c, d) in zip(pts, pts[1:]):
        if t <= c: return b + (d - b) * suave((t - a) / (c - a))
    return pts[-1][1]
def mix(ra, rb, k):
    """mistura de poses: angulos de A escalados por (1-k) + os de B por k (k=0 e A exato, k=1 e B exato)"""
    return {nm: [(ax, a * (1 - k)) for ax, a in ra.get(nm, [])] + [(ax, a * k) for ax, a in rb.get(nm, [])] for nm in set(ra) | set(rb)}
def soma(r, nm, ax, graus): r.setdefault(nm, []).append((ax, math.radians(graus)))
def soma_cab(r, ax, graus):
    """gira a cabeca e a mandibula juntas (a Mandibula e filha do Pescoco2, nao da Cabeca: girar so a Cabeca abria/cruzava a
    boca; visto no render da pose deitada, dentes de cima passando da arcada de baixo)"""
    soma(r, "Cabeca", ax, graus); soma(r, "_cab", ax, graus)
def boca_acompanha(fn):
    """correcao 04/11: a mandibula agora segue a cabeca em TODOS os clipes (mandibula_segue_cabeca na amostragem); o '_cab'
    so marcava o giro e e descartado para nao somar duas vezes"""
    def f(t):
        r, raiz, pes = fn(t); r.pop("_cab", None)
        return r, raiz, pes
    return f
REP0 = clipe_repouso(0.0)[0]                                       # transicoes do Lote 3 saem/chegam no quadro 0 do Repouso
DESCE = 0.62                                                       # barriga (z 0,71) ~0,09 do chao; 0,66 empurrava o cotovelo D 0,05 para dentro do chao
def deitado(t, T=6.0):
    """deitado de barriga: queixo no chao, cauda relaxada em curva leve; respira (corpo so sobe a partir do apoio)"""
    r = {}; u = 2 * math.pi * t / T; resp = 0.5 - 0.5 * math.cos(u)
    soma(r, "Pescoco", X_, 8.0); soma(r, "Pescoco2", X_, 8.0); soma_cab(r, X_, 10.0)
    soma_cab(r, Z_, 1.2 * math.sin(u))
    for i, nm in enumerate(CAUDA):
        soma(r, nm, Z_, 2.5 + 0.8 * i / 7 + (1.5 * (i / 7) * math.sin(u - 0.5 * i / 7) - 1.5 * (i / 7) * math.sin(-0.5 * i / 7)))
        if i >= 3: soma(r, nm, X_, -0.6)                            # ponta encosta no chao
    soma(r, "Coluna1", X_, -0.5 * resp)
    r["Mandibula"] = [(X_, FECHADA)]
    return r, V((0, 0, -DESCE + 0.02 * resp))
DEIT0 = deitado(0.0)
ABRE_DEIT = 0.35                                                   # dianteiras abertas deitado (passo curto no Deitar/Levantar)
def pes_deitado(k_):
    """k_ (0..1) por pata: desloca as dianteiras para fora (cotovelo nao afunda com o corpo baixo)"""
    return {k: (V((ABRE_DEIT * sx * k_.get(k, 0.0), 0, 0)), 0.0) for k, (par, sx, f_) in PATAS.items() if par == "dian"}
def passo_lado(t, t0, dur=0.45, alt=0.25):
    """passo curto: 0 -> 1 com elevacao (o pe nao arrasta)"""
    u = max(0.0, min(1.0, (t - t0) / dur)); return suave(u), alt * math.sin(math.pi * u)
def clipe_descanso_deitado(t): r, raiz = deitado(t); return r, raiz, pes_deitado({"MaoE": 1.0, "MaoD": 1.0})
GAPE = math.degrees(ANG_BOCA) + ABRE_MAX                          # cranio sobe = abertura total aprovada: a mandibula fica parada no chao
def clipe_deitado_boca_aberta(t):
    """Lote R1 (referencia real, 'gaping'): deitado ao sol/calor de boca aberta. A mandibula fica apoiada no chao e quem sobe e
    o CRANIO (cabeca); a abertura total e a maxima aprovada da boca. Respira devagar; laco de 6 s. Emenda com
    DescansoDeitado por cruzamento de ~0,6 s (so cabeca e boca mudam)."""
    r, raiz = deitado(t)
    soma(r, "Cabeca", X_, -GAPE)                                   # so o cranio (a mandibula nao recebe este giro)
    soma(r, "Pescoco2", X_, -0.6)                                  # o pivo da cabeca fica atras da dobradica: sem isto o queixo entrava 0,05 no chao
    r["Mandibula"] = [(X_, math.radians(ABRE_MAX) + math.radians(0.8) * math.sin(2 * math.pi * t / 6.0))]
    return r, raiz, pes_deitado({"MaoE": 1.0, "MaoD": 1.0})
def clipe_deitar(t):
    """frente desce primeiro (pelve inclina), depois o quadril; cabeca acompanha e o queixo pousa por ultimo"""
    rz = 0.20 * suave(t / 0.9) + (DESCE - 0.20) * suave((t - 0.7) / 1.0)
    p = 4.3 * suave(t / 0.9) * (1 - suave((t - 0.7) / 1.0))
    r = mix(REP0, DEIT0[0], suave((t - 0.5) / 1.5))
    soma(r, "Pelve", X_, p); soma(r, "Cauda1", X_, -p)                # a cauda nao levanta com a pelve
    pes = {}
    for k, t0 in (("MaoD", 0.0), ("MaoE", 0.2)):
        u, lev = passo_lado(t, t0); sx = PATAS[k][1]; pes[k] = (V((ABRE_DEIT * sx * u, 0, lev)), 0.0)
    return r, V((0, 0, -rz)), pes
def clipe_levantar(t):
    """empurra a frente primeiro (cabeca antecipa), depois o quadril; termina no quadro 0 do Repouso"""
    sobe = 0.20 * suave((t - 0.1) / 0.7) + (DESCE - 0.20) * suave((t - 0.6) / 0.9)
    p = -4.3 * suave((t - 0.1) / 0.7) * (1 - suave((t - 0.6) / 0.9))
    r = mix(DEIT0[0], REP0, suave(t / 1.6))
    soma_cab(r, X_, -5.0 * math.sin(math.pi * min(1.0, t / 1.2)))   # cabeca sobe antes do corpo
    soma(r, "Pelve", X_, p); soma(r, "Cauda1", X_, -p)
    pes = {}
    for k, t0 in (("MaoE", 1.0), ("MaoD", 1.2)):                    # com o corpo ja alto, as dianteiras voltam sob o ombro
        u, lev = passo_lado(t, t0, 0.4); sx = PATAS[k][1]; pes[k] = (V((ABRE_DEIT * sx * (1 - u), 0, lev)), 0.0)
    return r, V((0, 0, -DESCE + sobe)), pes
def clipe_reacao_golpe(t):
    """golpe de frente: tranco para tras e para cima, cabeca recua e desvia, boca abre um pouco, cauda chicoteia; volta ao Repouso"""
    k = suave(t / 0.10) * (1 - suave((t - 0.13) / 0.55)); e = math.exp(-5 * t) * math.sin(2 * math.pi * t / 0.35)
    r = mix(REP0, {}, 0.0)
    soma(r, "Pelve", X_, -1.5 * k); soma(r, "Pescoco", X_, -5.0 * k); soma_cab(r, X_, -10.0 * k)
    soma(r, "Pescoco", Z_, 5.0 * k); soma_cab(r, Z_, 7.0 * k)
    r["Mandibula"] = [(X_, FECHADA + math.radians(8.0) * k)]
    for i, nm in enumerate(CAUDA): soma(r, nm, Z_, 5.0 * (0.3 + i / 7) * e * (1 - suave((t - 0.5) / 0.3)))
    return r, V((0, 0.15 * k, 0.05 * k)), {}   # 0,30 para tras esticava a dianteira E (antebraco 28 graus num quadro)
def clipe_morte(t):
    """incapacitacao visual: tranco, patas cedem, barriga cai com leve rolagem, cabeca tomba de lado, cauda amolece"""
    tr = math.sin(math.pi * min(1.0, t / 0.25)) if t < 0.25 else 0.0
    c = suave((t - 0.25) / 0.5); q = math.exp(-8 * max(0.0, t - 0.75)) * math.sin(2 * math.pi * max(0.0, t - 0.75) / 0.3) if t > 0.75 else 0.0
    h = suave((t - 0.4) / 0.8); s = suave((t - 0.6) / 1.0)
    r = mix(REP0, {}, 0.0)
    r["Raiz"] = [(Y_, math.radians(7.0 * c))]                             # rola um pouco para o lado +X
    soma_cab(r, X_, -8.0 * tr)
    soma(r, "Pescoco", X_, 8.0 * h); soma(r, "Pescoco2", X_, 6.0 * h); soma_cab(r, X_, 2.0 * h)   # mais que isso o focinho tombado entra 0,2 no chao
    soma(r, "Pescoco", Z_, 9.0 * h); soma_cab(r, Z_, 9.0 * h); soma_cab(r, Y_, 8.0 * h)
    r["Mandibula"] = [(X_, FECHADA + math.radians(5.0) * h)]
    for i, nm in enumerate(CAUDA):
        soma(r, nm, Z_, (3.5 + 1.5 * i / 7) * s)
        if i >= 3: soma(r, nm, X_, -1.2 * s)
    return r, V((0, 0, 0.05 * tr - MORTE_DESCE * c + 0.04 * q)), {}
MORTE_DESCE = 0.58
def clipe_comer(t):
    """abaixa a cabeca ate a comida, abre, abocanha; joga a cabeca para cima para engolir (2 vezes); volta ao Repouso"""
    r = mix(REP0, {}, 0.0)
    pesc = kf(t, [(0, 0), (0.45, 6), (0.65, 6), (1.0, -6), (1.25, -9), (1.5, -3), (1.85, -7), (2.1, -2), (2.6, 0)])
    cab = kf(t, [(0, 0), (0.45, 3), (0.65, 2.5), (1.0, -10), (1.25, -15), (1.5, -5), (1.85, -11), (2.1, -3), (2.6, 0)])
    boca = kf(t, [(0, 0), (0.3, 0), (0.5, ABRE_MAX), (0.58, ABRE_MAX), (0.64, 0), (1.05, 0), (1.18, 7), (1.3, 0), (1.75, 0), (1.88, 5), (2.0, 0)])
    guin = 5.0 * math.sin(2 * math.pi * (t - 0.65) / 0.45) * (suave((t - 0.65) / 0.15) * (1 - suave((t - 1.2) / 0.3))) if t > 0.65 else 0.0
    soma(r, "Pescoco", X_, pesc); soma_cab(r, X_, cab); soma_cab(r, Z_, guin)
    soma(r, "Pelve", X_, 1.0 * kf(t, [(0, 0), (0.45, 1), (0.65, 1), (1.0, 0)]))
    r["Mandibula"] = [(X_, FECHADA + (math.radians(ABRE_MAX) - FECHADA) * boca / ABRE_MAX)]   # 0 = fechada 100%, ABRE_MAX = +12
    e = suave(t / 0.4) * (1 - suave((t - 2.4) / 0.6))
    for i, nm in enumerate(CAUDA): soma(r, nm, Z_, 2.5 * e * (i / 7) * math.sin(2 * math.pi * t / 1.5))
    return r, V((0, 0, 0)), {}
def clipe_observar(t):
    """ergue um pouco a cabeca e varre o ambiente: esquerda, segura, direita, segura, volta"""
    r = mix(REP0, {}, 0.0)
    g = kf(t, [(0, 0), (0.7, 1), (1.4, 1), (2.3, -1), (3.0, -1), (3.8, 0)])
    ergue = kf(t, [(0, 0), (0.5, 1), (3.3, 1), (3.9, 0)])
    soma(r, "Coluna2", Z_, 3.0 * g); soma(r, "Pescoco", Z_, 9.0 * g); soma(r, "Pescoco2", Z_, 6.0 * g); soma_cab(r, Z_, 9.0 * g)
    soma(r, "Pescoco", X_, -3.0 * ergue); soma_cab(r, X_, -4.0 * ergue)
    for i, nm in enumerate(CAUDA): soma(r, nm, Z_, -2.0 * g * (i / 7))
    return r, V((0, 0, 0)), {}
def clipe_alerta(t):
    """estimulo de lado: cabeca vira rapido, corpo se ergue nas patas, cauda firme; segura e relaxa de volta"""
    r = mix(REP0, {}, 0.0)
    a = kf(t, [(0, 0), (0.25, 1), (1.8, 1), (2.5, 0)]); g = kf(t, [(0, 0), (0.18, 1), (1.9, 1), (2.5, 0)])
    soma(r, "Pescoco", Z_, 10.0 * g); soma_cab(r, Z_, 12.0 * g); soma(r, "Coluna2", Z_, 3.0 * g)
    soma(r, "Pescoco", X_, -5.0 * a); soma_cab(r, X_, -6.0 * a); soma(r, "Coluna2", X_, -2.0 * a)
    for i, nm in enumerate(CAUDA): soma(r, nm, X_, (2.0 if i == 0 else 0.0) * a); soma(r, nm, Z_, -3.0 * g * (i / 7))
    tremor = 0.4 * a * math.sin(2 * math.pi * t * 7) if 0.3 < t < 1.8 else 0.0
    soma_cab(r, X_, tremor)
    return r, V((0, 0, 0.28 * a)), {}
for nome_, fn_, dur_, loop_, ext_ in (
        ("ReacaoGolpe", clipe_reacao_golpe, 0.8, False, {"eventos": {"impacto": 0.0}, "de": "Repouso", "para": "Repouso"}),
        ("Morte", clipe_morte, 2.4, False, {"eventos": {"patas_cedem": 0.25, "impacto_chao": 0.75}, "de": "Repouso", "para": "(fica no ultimo quadro)"}),
        ("Comer", clipe_comer, 3.0, False, {"eventos": {"abocanha": 0.62, "engole": 1.25, "engole2": 1.95}, "de": "Repouso", "para": "Repouso"}),
        ("Deitar", clipe_deitar, 2.0, False, {"eventos": {"barriga_no_chao": 1.7}, "de": "Repouso", "para": "DescansoDeitado"}),
        ("DescansoDeitado", clipe_descanso_deitado, 6.0, True, {}),
        ("DeitadoBocaAberta", clipe_deitado_boca_aberta, 6.0, True, {"de": "DescansoDeitado (cruzar ~0,6 s)", "para": "DescansoDeitado", "obs": "gaping: sol/calor (referencia real)"}),
        ("Levantar", clipe_levantar, 1.8, False, {"de": "DescansoDeitado", "para": "Repouso"}),
        ("Observar", clipe_observar, 4.0, False, {"de": "Repouso", "para": "Repouso"}),
        ("Alerta", clipe_alerta, 2.5, False, {"eventos": {"vira_para_estimulo": 0.18}, "de": "Repouso", "para": "Repouso"})):
    CLIPES[nome_] = (boca_acompanha(fn_), dur_, loop_, 0.0)
    if ext_: EXTRA[nome_] = ext_
# ================================================================== Lote 4: montaria (so apresentacao; o cavaleiro e demonstracao separada)
BAIXA_MONT = 0.20                                                  # baixa a postura para receber o peso (patas plantadas)
def montaria(t, baixa, rola, olha, amortece, lado=1.0):
    """corpo estavel: baixa nas patas, rola de leve para o lado do apoio (lado = +1: esquerdo/+X; -1: direito/-X), cabeca
    acompanha o cavaleiro; cauda parada (contrapeso); termina no quadro 0 do Repouso"""
    r = mix(REP0, {}, 0.0)
    soma(r, "Pescoco", Z_, 4.0 * olha * lado); soma_cab(r, Z_, 6.0 * olha * lado); soma(r, "Pescoco", X_, 1.5 * olha)
    for i, nm in enumerate(CAUDA): soma(r, nm, Z_, -1.0 * olha * lado * (i / 7))
    r["Raiz"] = [(Y_, math.radians(1.5 * rola * lado))]
    soma(r, "Coluna1", X_, -0.5 * amortece)                       # dorso cede atras (frente nao afunda o cotovelo)
    return r, V((0, 0, -BAIXA_MONT * baixa - 0.03 * amortece)), {}
def clipe_montar(t, lado=1.0):
    baixa = kf(t, [(0, 0), (0.7, 1), (3.0, 1), (3.75, 0)]); rola = kf(t, [(1.0, 0), (1.5, 1), (2.4, 1), (2.8, 0)])
    olha = kf(t, [(0.1, 0), (0.7, 1), (1.9, 1), (2.9, 0)]); amort = kf(t, [(2.75, 0), (2.95, 1), (3.3, 0)])
    return montaria(t, baixa, rola, olha, amort, lado)
def clipe_desmontar(t, lado=1.0):
    baixa = kf(t, [(0, 0), (0.6, 1), (2.8, 1), (3.5, 0)]); rola = kf(t, [(0.8, 0), (1.4, 1), (2.3, 1), (2.7, 0)])
    olha = kf(t, [(0.3, 0), (1.0, 1), (2.5, 1), (3.2, 0)]); amort = kf(t, [(2.3, 0), (2.5, -0.5), (2.8, 0)])   # alivio do peso ao soltar
    return montaria(t, baixa, rola, olha, amort, lado)
# Lote 5: subida e descida pelos DOIS lados (decisao do usuario 05/11). Montar/Desmontar = lado esquerdo (+X), sem mudanca.
def clipe_montar_d(t): return clipe_montar(t, -1.0)
def clipe_desmontar_d(t): return clipe_desmontar(t, -1.0)
for nome_, fn_, dur_, ext_ in (
        ("Montar", clipe_montar, 4.0, {"eventos": {"maos_no_ombro": 1.0, "pe_no_cotovelo_E": 1.4, "pe_atras_do_cotovelo_D": 1.85, "perna_sobre_o_dorso": 2.4, "sentado": 3.1},
                                       "de": "Repouso", "para": "Repouso (montado)", "lado_do_teste": "esquerdo (+X)", "obs": "eventos = demonstracao do cavaleiro de teste; sem regra de jogo"}),
        ("Desmontar", clipe_desmontar, 3.6, {"eventos": {"maos_na_sela": 0.7, "perna_sobre_o_dorso": 1.1, "solta": 2.15, "pes_no_chao": 2.5},
                                             "de": "Repouso (montado)", "para": "Repouso", "lado_do_teste": "esquerdo (+X)", "obs": "eventos = demonstracao do cavaleiro de teste; sem regra de jogo"}),
        ("MontarDireita", clipe_montar_d, 4.0, {"eventos": {"maos_no_ombro": 1.0, "pe_no_cotovelo_D": 1.4, "pe_atras_do_cotovelo_E": 1.85, "perna_sobre_o_dorso": 2.4, "sentado": 3.1},
                                                "de": "Repouso", "para": "Repouso (montado)", "lado": "direito (-X)", "espelho_de": "Montar", "obs": "eventos = demonstracao do cavaleiro de teste"}),
        ("DesmontarDireita", clipe_desmontar_d, 3.6, {"eventos": {"maos_na_sela": 0.7, "perna_sobre_o_dorso": 1.1, "solta": 2.15, "pes_no_chao": 2.5},
                                                      "de": "Repouso (montado)", "para": "Repouso", "lado": "direito (-X)", "espelho_de": "Desmontar", "obs": "eventos = demonstracao do cavaleiro de teste"})):
    CLIPES[nome_] = (boca_acompanha(fn_), dur_, False, 0.0); EXTRA[nome_] = ext_
QUAIS = A[1].split(",") if len(A) > 1 else list(CLIPES)

# ------------------------------------------------------------------ mordida rigida (correcao 04/11)
RH, RJ = BD["Cabeca"].matrix_local.copy(), BD["Mandibula"].matrix_local.copy()
def mandibula_segue_cabeca(rots):
    """a Mandibula e filha do Pescoco2: o giro da Cabeca e aplicado tambem a ela, em torno do pivo da CABECA (mordida rigida,
    os dentes nao deslizam nem cruzam com a cabeca girando). A rotacao propria da mandibula (abrir/fechar) vale em relacao a
    cabeca e nunca fecha alem do fechado (FECHADA): antes, em VirarE/D os dentes raspavam 7,3 graus de lado e o queixo
    deslizava 0,65 stud; Arrancada/Mergulho/Mordida fechavam ate 5 graus alem (arcadas cruzando)."""
    ang = sum(a for ax, a in rots.get("Mandibula", [(X_, FECHADA)]) if abs(ax.x) > 0.99)
    if ang < FECHADA:
        PB["Mandibula"].rotation_quaternion = rot_mundo("Mandibula", rots.get("Mandibula", []) + [(X_, FECHADA - ang)])
    Lh = PB["Cabeca"].rotation_quaternion.to_matrix().to_4x4()
    Lj = PB["Mandibula"].rotation_quaternion.to_matrix().to_4x4()
    Gh = RH @ Lh @ RH.inverted(); Lj2 = RJ.inverted() @ Gh @ RJ @ Lj
    PB["Mandibula"].rotation_quaternion = Lj2.to_quaternion(); PB["Mandibula"].location = Lj2.translation
# ------------------------------------------------------------------ Lote R1: cauda arrastando no chao
# Crocodilo real na caminhada alta: a base da cauda sai do chao e a metade de tras vai ENCOSTADA, arrastando (IUCN CSG,
# San Diego Zoo, Londolozi). Antes: a cauda inteira ficava suspensa a ~0,8-1,2 do chao em todos os clipes de terra.
# Aplicado depois da pose de cada quadro: cada osso da cauda (3 a 8) gira em arfagem para levar a pele de baixo da junta
# ate a altura-alvo (Cauda3 a meio caminho, 4 a 8 no chao). k = 0 na agua; nas transicoes terra<->agua acompanha as patas.
RAIO_CAUDA = {"Cauda2": 1.43, "Cauda3": 1.32, "Cauda4": 1.11, "Cauda5": 0.92, "Cauda6": 0.77, "Cauda7": 0.56, "Cauda8": 0.22}  # junta -> pele de baixo (repouso)
PELE_ALVO = {"Cauda3": 0.40, "Cauda4": 0.04, "Cauda5": 0.04, "Cauda6": 0.04, "Cauda7": 0.04, "Cauda8": 0.04}
SEM_CHAO = ("Nado", "NadoParado", "CurvaAquaticaEsquerda", "CurvaAquaticaDireita", "Mergulho", "Emersao", "CurvaLentaEsquerda", "CurvaLentaDireita")
def k_cauda(nome, t):
    if nome in SEM_CHAO: return 0.0
    if nome == "EntradaAgua": return 1.0 - suave((t - 1.0) / 0.8)
    if nome == "SaidaAgua": return suave((t - 0.3) / 0.8)
    return 1.0
def cauda_no_chao(rots, kc):
    bpy.context.view_layer.update()                               # alturas NATURAIS de todas as juntas antes de corrigir
    natural = {nm: (arm.matrix_world @ PB[nm].tail).z - RAIO_CAUDA[nm] for nm in PELE_ALVO}
    for nm, z_pele in PELE_ALVO.items():
        par = BD[nm].parent.name
        alvo = natural[nm] + (z_pele - natural[nm]) * kc          # k sobre a pose natural (nao acumula pela cadeia)
        for _ in range(4):
            bpy.context.view_layer.update()
            h = arm.matrix_world @ PB[nm].head; tl = arm.matrix_world @ PB[nm].tail
            atual = tl.z - RAIO_CAUDA[nm]
            if abs(alvo - atual) < 0.004: break
            d = tl - h; dh = math.hypot(d.x, d.y)
            if dh < 1e-4: break
            # giro no plano vertical do proprio osso: eixo horizontal perpendicular a ele (com a cauda balancando de lado,
            # o X do mundo inclinava o osso e a ponta descia demais), levado para os eixos de repouso que rot_mundo usa
            w = V((d.x, d.y, 0)).normalized().cross(V((0, 0, 1)))
            Pp = (PB[par].matrix @ BD[par].matrix_local.inverted()).to_3x3()
            eixo = (Pp.inverted() @ w).normalized()
            fi = math.atan2(d.z, dh); zt = alvo + RAIO_CAUDA[nm] - h.z
            a = math.asin(max(-1.0, min(1.0, zt / math.hypot(dh, d.z)))) - fi
            rots[nm] = list(rots.get(nm, [])) + [(eixo, a)]
            PB[nm].rotation_quaternion = rot_mundo(nm, rots[nm])
# ------------------------------------------------------------------ amostragem -> FK -> acao + JSON + QA
pes_ponta = {k: BD[k] for k in PATAS}
manifesto = {}
for nome in QUAIS:
    fn, dur, loop, vel = CLIPES[nome]
    nq = int(round(dur * FPS)) + (0 if loop else 1)
    quadros = []; erro_ik = 0.0; desliza = 0.0; chao_min = 9.0; prev = None; prev_ap = {}
    for qi in range(nq):
        t = qi / FPS
        zerar(); _res = fn(t); rots, raiz, pes = _res[0], _res[1], _res[2]; info = _res[3] if len(_res) > 3 else None
        PB["Raiz"].location = (rot_mundo("Raiz", []) .to_matrix().inverted() @ BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz)
        for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
        mandibula_segue_cabeca(rots)
        kc = k_cauda(nome, t)
        if kc > 0: cauda_no_chao(rots, kc)
        wc = PES_CORPO.get(nome, 0.0)
        if info is not None and "pes_corpo" in info: wc = info["pes_corpo"]
        if wc > 0:                                               # agua: os alvos acompanham o corpo (Raiz arfa/afunda)
            bpy.context.view_layer.update(); Mr = PB["Raiz"].matrix @ BD["Raiz"].matrix_local.inverted()
        for k, d in pes.items():
            ang_p = 0.0; guin = 0.0
            if isinstance(d, tuple): d, ang_p, guin = (d + (0.0,))[:3] if len(d) == 2 else d
            ALVO[k].location = REPOUSO[k] + d
            if wc > 0: ALVO[k].location = ALVO[k].location.lerp(Mr @ ALVO[k].location, wc)
            if ang_p or guin: ALVO[k].rotation_quaternion = Quaternion((0, 0, 1), guin) @ Quaternion((1, 0, 0), math.radians(ang_p)) @ ROT0[k]
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
        if info is not None:                                      # pe apoiado parado no MUNDO (corpo andando/girando como no jogo)
            for k in PATAS:
                pw = info["T"] @ PB[k].head
                if k in info["apoio"] and wc == 0 and k in prev_ap and prev_ap[k] is not None:
                    desliza = max(desliza, (pw - prev_ap[k]).length * FPS)
                prev_ap[k] = pw if k in info["apoio"] else None
        quadros.append(pose)
    # grava acao FK (sem restricoes) para revisao no Blender
    act = bpy.data.actions.get("Croc_" + nome) or bpy.data.actions.new("Croc_" + nome)
    act["loop"] = loop; act["velocidade"] = vel
    manifesto[nome] = {"duracao": dur, "loop": loop, "quadros": nq, "velocidade_studs_s": round(vel, 2),
                       "erro_ik_max": round(erro_ik, 4), "desliza_pe_max_studs_s": round(desliza, 3), "ponta_pe_min_z": round(chao_min, 3)}
    print("CLIPE", nome, manifesto[nome], flush=True)
    if erro_ik > 0.02: print("   pior IK:", pior)
    dado = {"nome": "Crocodilo_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel, 3), "ossos": {}}
    if nome in EXTRA:
        dado["sincronizacao"] = {k_: v_ for k_, v_ in EXTRA[nome].items()}
        manifesto[nome]["sincronizacao"] = {k_: (v_ if not isinstance(v_, list) else "por quadro no JSON") for k_, v_ in EXTRA[nome].items()}
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
_mp = os.path.join(OUT, "manifesto_clipes.json")             # mescla: preserva definicoes e medidas extras (ex.: sola L2b)
_ant = json.load(open(_mp, encoding="utf-8")) if os.path.exists(_mp) else {}
for nome, d_ in manifesto.items():
    _ant[nome] = {**{k_: v_ for k_, v_ in _ant.get(nome, {}).items() if k_ not in d_}, **d_}
json.dump(_ant, open(_mp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "CR_Crocodilo_Anim.blend"))
print("ANIM_OK", list(QUADROS))
