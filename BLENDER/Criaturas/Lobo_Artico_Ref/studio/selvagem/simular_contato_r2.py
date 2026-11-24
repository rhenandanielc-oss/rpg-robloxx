"""r2b: estacao de menor custo + aproxima em trote se o alvo se move. Simulacao LOCAL (modelo 2D, NAO e o Roblox) do contato de ataque do lobo selvagem: r1e x r2 (19/11/2026).
Espelha a decisao de IA_LoboArtico.defender (r1e e r2) e uma cinematica simplificada do Controle_Servidor:
velocidades dos clipes (Andar 3,0 / Trote 6,667 / Corrida 20,357 x Escala), giro andando 60/70/45 graus/s, parado: clipe
Virar (90 graus em 3,1 s) acima de 60 graus e giro de 60 graus/s abaixo (r7 IA_Olhar), aceleracao limitada a 12 studs/s2
(as transicoes reais sao clipes), tick da IA 0,3 s, pacote velho 0,6 s. Mordida do Kit: acerta se, 0,2 s depois do pedido,
o alvo esta a <= 3,5e+1,5 do focinho e a <= 37,5 graus da frente; o Kit recusa pedidos a menos de 0,5 s.
Corpo: alvo "dentro" se estiver entre -0,8 e 6,0 x e ao longo do lobo (pivo nas ancas) e a < 1,3 x e de lado.
Cenarios: alvo parado, andando de lado, correndo para longe, recuando devagar, colado sob o tronco, e Pre-adulto (0,85).
Uso: python simular_contato_r2.py  -> tabela + simular_contato_r2.json"""
import math, json
DT = 1 / 30; TICK = 0.3
VEL = {"andar": 3.0, "trote": 6.667, "correr": 20.357}
GIRO = {"andar": 60, "trote": 70, "correr": 45}
FOC, ALC, FOLGA, CONE_KIT = 6.2, 3.5, 1.5, 37.5

def rot(v, a): c, s = math.cos(a), math.sin(a); return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def norm(a): return math.hypot(a[0], a[1])
def unit(a): m = norm(a); return (a[0] / m, a[1] / m) if m > 1e-6 else (0.0, 0.0)
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def ang(a, b): return math.atan2(a[0] * b[1] - a[1] * b[0], dot(a, b))

class Lobo:
    def __init__(s, p, fr, e): s.p, s.fr, s.e, s.v, s.virando = p, unit(fr), e, 0.0, 0.0
    def passo(s, cmd):
        tipo = cmd[0]
        if tipo == "mover" and norm(cmd[1]) > 0.1:
            d, marcha = unit(cmd[1]), cmd[2]
            a = ang(s.fr, d)
            if s.v < 0.3 and abs(a) > math.radians(60):          # parado: clipe de virada (lento)
                s.fr = unit(rot(s.fr, max(-1, min(1, a)) * math.radians(29) * DT)); s.v = 0; return
            lim = math.radians(GIRO[marcha]) * DT
            s.fr = unit(rot(s.fr, max(-lim, min(lim, a))))
            alvo_v = VEL[marcha] * s.e
        elif tipo == "olhar":
            alvo_v = 0.0
            if s.v < 0.3:
                a = ang(s.fr, unit(cmd[1]))
                if abs(a) > math.radians(60): s.fr = unit(rot(s.fr, math.copysign(math.radians(29) * DT, a)))
                elif abs(a) > math.radians(4): lim = math.radians(60) * DT; s.fr = unit(rot(s.fr, max(-lim, min(lim, a))))
        else:
            alvo_v = 0.0
        dv = alvo_v - s.v; s.v += max(-12 * DT, min(12 * DT, dv))
        s.p = add(s.p, mul(s.fr, s.v * DT))
    def focinho(s): return add(s.p, mul(s.fr, FOC * s.e))

def geometria(l, alvo):
    rel = sub(alvo, l.p); fr = l.fr
    dF = norm(sub(alvo, l.focinho()))
    along = dot(rel, fr); lado = abs(dot(rel, (-fr[1], fr[0])))
    a = math.degrees(math.acos(max(-1, min(1, dot(unit(rel), fr))))) if norm(rel) > 0.05 else 180
    sob = (-1.0 * l.e < along < (FOC - 0.8) * l.e and lado < 1.8 * l.e) or (along >= (FOC - 0.8) * l.e and dF < 0.7 * l.e)
    return dF, a, sob, rel, along, lado

def decisao_r1e(l, alvo, est):
    d = norm(sub(alvo, l.p))
    if d > 9.5: return ("mover", sub(alvo, l.p), "correr" if d > 25 else "trote"), True
    return ("mover", sub(alvo, l.p), "andar"), True                     # anda para o alvo e morde (a falha)

def estacao(l, alvo):
    """r2b: entre 8 pontos a D do alvo, o de menor custo: virar agora + andar + virar no fim para o alvo."""
    e = l.e; D = FOC * e + 1.0 + 0.8 * e; melhor, cm = None, 1e9
    for k in range(8):
        u = rot((0, 1), k * math.pi / 4); S = add(alvo, mul(u, D)); ida = sub(S, l.p)
        if norm(ida) < 0.5: return S
        c = abs(ang(l.fr, unit(ida))) / math.radians(45) + norm(ida) / (3.0 * e) + abs(ang(unit(ida), mul(u, -1))) / math.radians(45)
        # r2c: rota que passa por cima do alvo (segmento pivo->S a < 2 x e do alvo, fora o comeco) e penalizada
        w = sub(alvo, l.p); tt = max(0.0, min(1.0, dot(w, ida) / max(dot(ida, ida), 1e-6)))
        if tt > 0.15 and norm(sub(alvo, add(l.p, mul(ida, tt)))) < 2.0 * e: c += 6
        if c < cm: melhor, cm = S, c
    return melhor

def decisao_r2(l, alvo, est, alvo_vel=0.0):
    dF, a, sob, rel, along, lado = geometria(l, alvo)
    e = l.e
    est["contato"] = (est.get("contato") and dF <= 4.6 * e) or dF <= 3.2 * e
    st = est.get("estacao")
    if st and (norm(sub(alvo, est["estacao_alvo"])) > 3 or est["estacao_ate"] < est["t"]): st = None; est["estacao"] = None
    if sob or st:
        est["contato"] = False
        if not st:
            st = estacao(l, alvo); est["estacao"], est["estacao_alvo"], est["estacao_ate"] = st, alvo, est["t"] + 8
        if norm(sub(st, l.p)) < 1.0:
            est["estacao"] = None; return ("olhar", rel), False
        return ("mover", sub(st, l.p), "andar"), False
    if est["contato"]: return ("olhar", rel), True
    if dF <= 8 * e: return ("mover", rel, "trote" if alvo_vel > 2.5 * e else "andar"), True
    return ("mover", rel, "correr" if dF > 25 * e else "trote"), False

def cenario(nome, versao, alvo0, mov, e=1.0, lobo0=(0, 0), fr0=(0, 1), T=14.0):
    l = Lobo(lobo0, fr0, e); alvo = alvo0; est = {}
    cmd, t, prox_tick, ult_pedido, pend = ("parar",), 0.0, 0.0, -9, []
    dentro_t, max_pen, mordidas, acertos, primeira = 0.0, 0.0, 0, 0, None
    while t < T:
        if t >= prox_tick:
            prox_tick += TICK
            est["t"] = t
            vel_alvo = norm(sub(mov(alvo, t), alvo)) / DT
            cmd, pode = decisao_r1e(l, alvo, est) if versao == "r1e" else decisao_r2(l, alvo, est, vel_alvo)
            dF, a, *_ = geometria(l, alvo)
            reach_ia = (dF <= ALC * e + FOLGA and a <= 30) if versao == "r2" else (norm(sub(alvo, l.p)) <= 9.5)
            if pode and reach_ia and t - ult_pedido >= 0.5:
                ult_pedido = t; mordidas += 1; pend.append(t + 0.2)
        l.passo(cmd)
        alvo = mov(alvo, t)
        for tp in list(pend):
            if t >= tp:
                pend.remove(tp); dF, a, *_ = geometria(l, alvo)
                if dF <= ALC * e + FOLGA and a <= CONE_KIT:
                    acertos += 1; primeira = primeira if primeira is not None else round(t, 2)
        _, _, _, rel, along, lado = geometria(l, alvo)
        if -0.8 * e < along < 6.0 * e and lado < 1.3 * e:
            dentro_t += DT; max_pen = max(max_pen, 1.3 * e - lado)
        t += DT
    return {"cenario": nome, "versao": versao, "escala": e, "tempo_dentro_do_corpo_s": round(dentro_t, 2),
            "max_penetracao_lateral": round(max_pen, 2), "pedidos_mordida": mordidas, "acertos": acertos, "primeiro_acerto_s": primeira}

def parado(a, t): return a
def andando_lado(a, t): return add(a, (4.0 * DT, 0.0))              # jogador andando devagar de lado
def correndo_longe(a, t): return add(a, (0.0, 16.0 * DT)) if t > 2 else a
def recuando(a, t): return add(a, (0.0, 2.0 * DT))
CEN = [("alvo parado a 20", (0.0, 20.0), parado, (0, 0), (0, 1)),
       ("alvo andando de lado", (0.0, 18.0), andando_lado, (0, 0), (0, 1)),
       ("alvo foge correndo (16/s)", (0.0, 14.0), correndo_longe, (0, 0), (0, 1)),
       ("alvo recuando devagar", (0.0, 14.0), recuando, (0, 0), (0, 1)),
       ("alvo colado sob o tronco", (0.4, 3.0), parado, (0, 0), (0, 1)),
       ("alvo atras do lobo a 4", (0.0, -4.0), parado, (0, 0), (0, 1))]
res = []
for nome, a0, mov, l0, f0 in CEN:
    for v in ("r1e", "r2"):
        res.append(cenario(nome, v, a0, mov, 1.0, l0, f0))
res.append(cenario("alvo parado a 20 (Pre-adulto 0,85)", "r1e", (0.0, 20.0), parado, 0.85))
res.append(cenario("alvo parado a 20 (Pre-adulto 0,85)", "r2", (0.0, 20.0), parado, 0.85))
print("%-36s %-4s %-6s %-9s %-7s %-7s %s" % ("cenario", "ver", "dentro", "penetr.", "pedidos", "acertos", "1o acerto"))
for r in res:
    print("%-36s %-4s %-6s %-9s %-7s %-7s %s" % (r["cenario"], r["versao"], r["tempo_dentro_do_corpo_s"], r["max_penetracao_lateral"], r["pedidos_mordida"], r["acertos"], r["primeiro_acerto_s"]))
json.dump(res, open("simular_contato_r2.json", "w"), indent=1)
