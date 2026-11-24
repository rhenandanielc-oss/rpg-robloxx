"""Simulacao LOCAL (modelo 2D, NAO e o Roblox) da r3 da IA do Lobo Artico: Atencao -> Ameaca -> Defesa -> Desengajar.
Espelha o coordenador (coordenar) e os comportamentos por papel (atencao/ameacar/defender) de IA_LoboArtico.server.luau r3,
com a cinematica e o contato de simular_contato_r2.py (Lobo, geometria, estacao, decisao_r2 = defender r2).
Simplificacoes: toca aberta (ancora = abrigo na origem), visao = flag por cenario (parede), 3 lobos (Lider/Membro Adulto,
Guardiao Pre-adulto 0,85), tick 0,3 s, jogador = ponto de raio 1. Uso: python simular_ameaca_r3.py -> tabela + json."""
import math, json, os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "simular_contato_r2.py"), encoding="utf-8").read()
exec(src.split("def cenario")[0])                                   # Lobo, geometria, estacao, decisao_r2, vetores

A = dict(raioAtencao=48, raioAviso=34, raioCritico=20, histerese=6, atencaoLobo=30, avisoLobo=16, encostar=2.5,
         atencaoMin=1.0, avisoMin=2.0, avisoCritico=3.0, insistencia=5, recuo=3, calma=4, memoria=8, memoriaDefesa=20,
         defesaSai=8, foraSeg=3, distConfronto=11, postoFracao=0.45, postoMax=16, flanco=7, flancoAtras=2,
         guardiaoPosto=4, guardiaoDefende=26)
COLEIRA = 75
NIVEL = {"Calmo": 0, "Atencao": 1, "Ameaca": 2, "Defesa": 3}
ABR = (0.0, 0.0)

class Coord:
    def __init__(s): s.tensao, s.desde, s.gat, s.dref, s.dmin, s.crit, s.fora = "Calmo", 0, 0, None, None, None, None; s.alvo = None; s.alvoAte = 0; s.motivo = ""; s.aviso = None; s.log = []
    def mudar(s, n, t, motivo):
        if s.tensao == n: return
        s.log.append((round(t, 1), s.tensao, n, motivo)); s.tensao, s.desde, s.motivo = n, t, motivo
        if n == "Ameaca": s.aviso, s.dref, s.crit = t, None, None
        if NIVEL[n] < 2: s.aviso = None
    def definir(s, uid, motivo, t): s.alvo, s.alvoAte = uid, t + A["memoriaDefesa"]; s.mudar("Defesa", t, motivo)
    def limpar(s, motivo, t): s.alvo = None; s.fora = None; s.gat = t; s.mudar("Atencao", t, motivo)

def dist_bando(lobos, p):
    return min(min(norm(sub(p, l.focinho())), norm(sub(p, l.p))) - 1.0 for l in lobos) / 1.0

def coordenar(C, t, jogs, lobos, visto):
    if C.alvo is not None:
        j = jogs.get(C.alvo)
        if not j or not j["vivo"] or t > C.alvoAte:
            C.limpar("alvo morto/desconectado/expirou", t); return
        dA = norm(j["p"])
        if dA > COLEIRA + A["defesaSai"]:
            C.fora = C.fora if C.fora is not None else t
            if t - C.fora >= A["foraSeg"]: C.limpar("saiu do territorio", t); return
        else:
            C.fora = None
            if visto.get(C.alvo) or (C.motivo == "coleta" and t - C.desde < A["memoriaDefesa"]): C.alvoAte = t + A["memoriaDefesa"]
        return
    if C.tensao == "Defesa": C.limpar("sem alvo", t); return
    cand = [(norm(v["p"]), u) for u, v in visto.items() if v and t - v["t"] <= A["memoria"]]
    if not cand:
        if C.tensao != "Calmo" and t - C.gat >= A["calma"]:
            C.mudar("Atencao" if NIVEL[C.tensao] >= 2 else "Calmo", t, "sem intruso: acalma"); C.gat = t
        return
    dA, uid = min(cand); p = visto[uid]["p"]
    n = C.tensao; dL = dist_bando(lobos, p)
    rAv = A["raioAviso"] + (A["histerese"] if n == "Ameaca" else 0); rAt = A["raioAtencao"] + (A["histerese"] if n != "Calmo" else 0)
    lAv = A["avisoLobo"] + (A["histerese"] if n == "Ameaca" else 0); lAt = A["atencaoLobo"] + (A["histerese"] if n != "Calmo" else 0)
    quer = "Ameaca" if (dA <= rAv or dL <= lAv) else ("Atencao" if (dA <= rAt or dL <= lAt) else "Calmo")
    if NIVEL[quer] >= NIVEL[n]: C.gat = t
    if NIVEL[quer] > NIVEL[n]:
        espera = quer == "Ameaca" and n == "Atencao" and t - C.desde < A["atencaoMin"] and dA > A["raioCritico"]
        if quer == "Ameaca" and n == "Calmo" and dA > A["raioCritico"]: C.mudar("Atencao", t, "intruso a vista")
        elif not espera: C.mudar(quer, t, "aviso" if quer == "Ameaca" else "intruso a vista")
    elif NIVEL[quer] < NIVEL[n] and t - C.gat >= A["calma"]:
        C.mudar("Atencao" if n == "Ameaca" else "Calmo", t, "recuou: acalma"); C.gat = t
    if C.tensao == "Ameaca":
        tAv = t - C.aviso
        C.dref = dA if tAv < A["avisoMin"] else max(C.dref if C.dref is not None else dA, dA)
        rec = dA > (C.dmin if C.dmin is not None else dA) + A["recuo"]
        C.dmin = min(C.dmin if C.dmin is not None else dA, dA)
        if rec: C.dmin = dA; C.crit = None
        C.crit = (C.crit if C.crit is not None else t) if dA <= A["raioCritico"] else None
        if tAv >= A["avisoMin"]:
            if C.dref - dA >= A["insistencia"] and not rec and dA <= A["raioAviso"]: C.definir(uid, "insistiu", t)
            elif dL <= A["encostar"]: C.definir(uid, "encostou", t)
            elif C.crit is not None and t - C.crit >= A["avisoCritico"]: C.definir(uid, "zona critica", t)
    else:
        C.dmin = None

def posto(papel, l, intr, lado):
    e = l.e
    if papel == "Guardiao":
        d = unit(intr); return mul(d, A["guardiaoPosto"]) if norm(intr) > 0.1 else (0, A["guardiaoPosto"])
    dist = norm(intr); d = unit(intr) if dist > 0.1 else (0, 1)
    k = min(min(dist * A["postoFracao"], A["postoMax"]), max(0, dist - ((A["distConfronto"] + FOC) * e + 1.0)))
    P = mul(d, k)
    if papel != "Lider": P = add(add(P, mul((-d[1], d[0]), A["flanco"] * e * lado)), mul(d, -A["flancoAtras"] * e))
    return P

def cenario(nome, roteiro, T=40.0, ver=lambda t, u: True, trace=None):
    lobos = [Lobo((0, 3), (0, 1), 1.0), Lobo((5, -2), (0, 1), 1.0), Lobo((-3, -4), (0, 1), 0.85)]
    papeis = ["Lider", "Membro", "Guardiao"]; lados = [1, -1, 1]
    C = Coord(); jogs = {}; visto = {}; est = [{} for _ in lobos]
    t, nt, cmds = 0.0, 0.0, [("parar",)] * 3
    mins = {"dF_min_antes_defesa": 99.0, "dentro_corpo_s": 0.0, "acertos": 0, "dano_fora_alcance": 0, "mudancas": 0, "aglomerou_s": 0.0}
    pend = []; ult = [-9] * 3; ameaca_t = None; defesa_t = None
    while t < T:
        roteiro(t, jogs, C)
        if t >= nt:
            nt += TICK
            for u, j in jogs.items():
                if j["vivo"] and ver(t, u) and (norm(j["p"]) <= A["raioAtencao"] + 26): visto[u] = {"p": j["p"], "t": t}
            for u in list(visto):
                if t - visto[u]["t"] > A["memoria"] or u not in jogs or not jogs[u]["vivo"]: visto.pop(u)
            coordenar(C, t, jogs, lobos, visto)
            if trace is not None: trace.append((round(t, 2), C.tensao, [(l.p, l.fr, l.e) for l in lobos], {u: j["p"] for u, j in jogs.items()}))
            if C.tensao == "Ameaca" and ameaca_t is None: ameaca_t = t
            if C.tensao == "Defesa" and defesa_t is None: defesa_t = t
            for i, l in enumerate(lobos):
                cmd = ("parar",); intr = None
                if C.tensao in ("Atencao", "Ameaca") and visto:
                    u = min(visto, key=lambda k: norm(visto[k]["p"])); intr = visto[u]["p"]
                if C.tensao == "Defesa" and C.alvo in jogs:
                    a = jogs[C.alvo]["p"]
                    if papeis[i] == "Guardiao" and norm(a) > A["guardiaoDefende"]:
                        P = mul(unit(a), A["guardiaoPosto"]); cmd = ("mover", sub(P, l.p), "trote") if norm(sub(P, l.p)) > 5 else ("olhar", sub(a, l.p))
                    else:
                        est[i]["t"] = t; cmd, pode = decisao_r2(l, a, est[i], 0.0)
                        dF, ang_, *_ = geometria(l, a)
                        if pode and dF <= ALC * l.e + FOLGA and ang_ <= 30 and t - ult[i] >= 0.5: ult[i] = t; pend.append((t + 0.2, i, C.alvo))
                elif C.tensao == "Ameaca" and intr:
                    dF = norm(sub(intr, l.focinho())) - 1.0
                    if dF < A["distConfronto"] * l.e: cmd = ("olhar", sub(intr, l.p))
                    else:
                        P = posto(papeis[i], l, intr, lados[i])
                        cmd = ("mover", sub(P, l.p), "andar") if norm(sub(P, l.p)) > 5 else ("olhar", sub(intr, l.p))
                elif C.tensao == "Atencao" and intr:
                    cmd = ("olhar", sub(intr, l.p))
                cmds[i] = cmd
        for i, l in enumerate(lobos): l.passo(cmds[i])
        for tp, i, u in list(pend):
            if t >= tp:
                pend.remove((tp, i, u)); j = jogs.get(u)
                if j:
                    dF, a, *_ = geometria(lobos[i], j["p"])
                    if dF <= ALC * lobos[i].e + FOLGA and a <= CONE_KIT: mins["acertos"] += 1
                    elif dF > ALC * lobos[i].e + FOLGA + 0.01: mins["dano_fora_alcance"] += 0     # o Kit recusa: nunca ha dano a distancia
        for j in jogs.values():
            for l in lobos:
                rel = sub(j["p"], l.p); al = dot(rel, l.fr); la = abs(dot(rel, (-l.fr[1], l.fr[0])))
                if -0.8 * l.e < al < 6.0 * l.e and la < 1.3 * l.e: mins["dentro_corpo_s"] += DT
            if C.tensao != "Defesa" and defesa_t is None:
                mins["dF_min_antes_defesa"] = min(mins["dF_min_antes_defesa"], min(norm(sub(j["p"], l.focinho())) - 1.0 for l in lobos))
        if C.tensao == "Ameaca" and min(norm(sub(lobos[a].p, lobos[b].p)) for a in range(3) for b in range(a + 1, 3)) < 2.5: mins["aglomerou_s"] += DT   # defesa: sim sem separar()
        t += DT
    mins["dF_min_antes_defesa"] = round(mins["dF_min_antes_defesa"], 1); mins["dentro_corpo_s"] = round(mins["dentro_corpo_s"], 2)
    mins["aglomerou_s"] = round(mins["aglomerou_s"], 2); mins["mudancas"] = len(C.log)
    aviso = round(defesa_t - ameaca_t, 1) if (ameaca_t is not None and defesa_t is not None) else None
    return {"cenario": nome, "niveis": [f"{x[0]}s {x[1]}->{x[2]} ({x[3]})" for x in C.log], "final": C.tensao,
            "aviso_antes_da_defesa_s": aviso, **mins}

def andar_reto(u, p0, v, t0=0.0, t1=99.0, cria=True):                          # jogador em linha reta com velocidade v (vetor)
    criado = [not cria]
    def f(t, jogs, C):
        if not criado[0]: criado[0] = True; jogs[u] = {"p": p0, "vivo": True}
        if u not in jogs: return
        if t0 <= t <= t1: jogs[u]["p"] = add(jogs[u]["p"], mul(v, DT))
    return f
def seq(*fs):
    def f(t, jogs, C):
        for g in fs: g(t, jogs, C)
    return f
def em(t_ev, acao):
    feito = [False]
    def f(t, jogs, C):
        if not feito[0] and t >= t_ev: feito[0] = True; acao(t, jogs, C)
    return f

CEN = []
CEN.append(("1 aproximacao lenta ate 30 e para", andar_reto("A", (0, 70), (0, -3), 0, 13.3)))
CEN.append(("2 para na zona de aviso (25) 30 s", andar_reto("A", (0, 60), (0, -4), 0, 8.75), 45))
CEN.append(("3 recua antes do ataque", seq(andar_reto("A", (0, 60), (0, -4), 0, 9), andar_reto("A", (0, 0), (0, 5), 11, 20, cria=False))))
CEN.append(("4 insiste depois do aviso", andar_reto("A", (0, 60), (0, -3), 0, 99)))
CEN.append(("5 agressao direta (dano validado) a 40", seq(andar_reto("A", (0, 40), (0, 0)), em(3, lambda t, j, C: C.definir("A", "dano", t)))))
CEN.append(("6 coleta do ovo", seq(andar_reto("A", (0, 60), (0, -10), 0, 5.5), em(5.6, lambda t, j, C: C.definir("A", "coleta", t)))))
CEN.append(("7 dois jogadores: so B agride", seq(andar_reto("A", (10, 30), (0, 0)), andar_reto("B", (-20, 40), (0, 0)), em(4, lambda t, j, C: C.definir("B", "dano", t)))))
CEN.append(("8 parede: intruso a 22 sem visao", andar_reto("A", (0, 22), (0, 0)), 30, lambda t, u: False))
def morrer(t, j, C): j["A"]["vivo"] = False
CEN.append(("9 alvo morre durante a defesa", seq(andar_reto("A", (0, 15), (0, 0)), em(1, lambda t, j, C: C.definir("A", "dano", t)), em(8, morrer))))
def sair(t, j, C): j.pop("A", None)
CEN.append(("10 alvo desconecta", seq(andar_reto("A", (0, 15), (0, 0)), em(1, lambda t, j, C: C.definir("A", "dano", t)), em(8, sair))))
CEN.append(("11 sai do territorio e volta a rotina", seq(andar_reto("A", (0, 15), (0, 0), 0, 0), em(1, lambda t, j, C: C.definir("A", "dano", t)), andar_reto("A", (0, 15), (0, 9), 3, 99, cria=False)), 45))
CEN.append(("12 alvo circulando perto do ovo (r 10, 6/s) apos dano", seq(em(0, lambda t, j, C: j.setdefault("A", {"p": (10, 0), "vivo": True})),
            lambda t, j, C: j["A"].__setitem__("p", (10 * math.cos(t * 0.6), 10 * math.sin(t * 0.6))) if "A" in j else None,
            em(0.5, lambda t, j, C: C.definir("A", "dano", t))), 25))
CEN.append(("13 colado no lobo sem aviso previo (aparece a 3)", andar_reto("A", (0, 12), (0, 0)), 20))
res = []
if __name__ != "__main__": CEN_EXPORT = CEN; raise SystemExit
for c in CEN:
    nome, roteiro_ = c[0], c[1]; T = c[2] if len(c) > 2 else 40; ver = c[3] if len(c) > 3 else (lambda t, u: True)
    res.append(cenario(nome, roteiro_, T, ver))
for r in res:
    print("\n== %s  (final: %s; aviso antes da defesa: %s s; menor focinho->intruso antes da defesa: %s; dentro do corpo: %s s; acertos: %d; aglomeracao: %s s)" % (
        r["cenario"], r["final"], r["aviso_antes_da_defesa_s"], r["dF_min_antes_defesa"], r["dentro_corpo_s"], r["acertos"], r["aglomerou_s"]))
    for x in r["niveis"]: print("   ", x)
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "simular_ameaca_r3.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
