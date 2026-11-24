"""Simulacao (Python puro) da REGRA DE DECISAO da proposta Controle r11: a cada fim de clipe escolhe o proximo pelo rumo que
falta ate o alvo (mesma tabela de proximoAndar do Luau) e o pivo segue a curva externa exata de cada clipe (curvas_v46b.json).
Alvo = ponto fixo a distancia D e angulo inicial theta (+ = esquerda). Mede: clipes usados, erro final de rumo ao alvo,
maior passagem do rumo (overshoot), distancia percorrida ate ficar com |erro| < 9 graus, e menor distancia ao alvo.
Uso: python sim_controle_r11.py [anim_v46b/curvas_v46b.json]"""
import json, math, sys
VJ = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "anim_v46b/curvas_v46b.json"))["acoes"]
NIVEL = {"Andar": 0}
for l, s in (("Esquerda", 1), ("Direita", -1)):
    for n in ("CurvaBreve", "CurvaCurta", "CurvaParaAndar"): NIVEL[n + l] = 0
    for n in ("AndarParaCurva", "AndarCurva", "FechadaParaCurva"): NIVEL[n + l] = s
    for n in ("CurvaParaFechada", "AndarCurvaFechada"): NIVEL[n + l] = 2 * s
def proximo(atual, a):
    n = NIVEL[atual]; g = abs(math.degrees(a)); lado = "Esquerda" if a > 0 else "Direita"
    if n == 0:
        if g < 9: return "Andar"
        if g < 27: return "CurvaBreve" + lado
        if g < 54: return "CurvaCurta" + lado
        return "AndarParaCurva" + lado
    ln = "Esquerda" if n > 0 else "Direita"; mesmo = (a > 0) == (n > 0)
    if abs(n) == 1:
        if not mesmo or g <= 27: return "CurvaParaAndar" + ln
        if g > 140: return "CurvaParaFechada" + ln
        return "AndarCurva" + ln
    if not mesmo or g <= 108: return "FechadaParaCurva" + ln
    return "AndarCurvaFechada" + ln
def ext(nome):
    if nome == "Andar": return [(0.0, -3.0 * q / 30, 0.0) for q in range(37)]
    return [(e[0], e[1], math.radians(e[2])) for e in VJ[nome]["externa_por_quadro_xy_psi"]]
def comp(base, e):
    x, y, p = base; c, s = math.cos(p), math.sin(p); return (x + c * e[0] - s * e[1], y + s * e[0] + c * e[1], p + e[2])
def erro(pose, alvo):
    x, y, p = pose; dx, dy = alvo[0] - x, alvo[1] - y; f = (math.sin(p), -math.cos(p))     # frente = Rz(p) (0,-1)
    return math.atan2(f[0] * dy - f[1] * dx, f[0] * dx + f[1] * dy), math.hypot(dx, dy)
def rodar(theta_g, D, max_clipes=14):
    th = math.radians(theta_g); alvo = (D * math.sin(th) * -1 * -1, -D * math.cos(th)); alvo = (-D * math.sin(th) * -1, -D * math.cos(th))
    # frente inicial (0,-1); esquerda do lobo = +X  -> alvo a theta para a esquerda = (D sin th, -D cos th)
    alvo = (D * math.sin(th), -D * math.cos(th))
    pose = (0.0, 0.0, 0.0); atual = "Andar"; seq = []; dmin = D; over = 0.0; s0 = 1 if th > 0 else -1; dist_ok = None; anda = 0.0
    a, d = erro(pose, alvo)
    for _ in range(max_clipes):
        a, d = erro(pose, alvo)
        if d < 3.0: break
        nxt = proximo(atual, a); seq.append(nxt); E = ext(nxt)
        for e in E[1:]:
            p2 = comp(pose, e); anda_ = 0
            a2, d2 = erro(p2, alvo); dmin = min(dmin, d2)
            if a2 * s0 < 0: over = max(over, abs(math.degrees(a2)))
        prev = pose; pose = comp(pose, E[-1]); anda += sum(math.hypot(E[i][0] - E[i - 1][0], E[i][1] - E[i - 1][1]) for i in range(1, len(E)))
        a, d = erro(pose, alvo)
        if dist_ok is None and abs(math.degrees(a)) < 9: dist_ok = round(anda, 1)
        atual = nxt
    return {"theta": theta_g, "D": D, "clipes": seq, "erro_final_graus": round(math.degrees(a), 1), "dist_final": round(d, 1),
            "passou_do_rumo_graus": round(over, 1), "andou_ate_alinhar": dist_ok, "menor_dist": round(dmin, 1)}
if __name__ == "__main__":
    R = []
    for th in (15, 25, 40, 60, 90, 135, 180, -45, -120):
        for D in (40.0, 15.0):
            r = rodar(th, D); R.append(r)
            print("SIM th=%4d D=%4.0f erro=%6.1f passou=%5.1f alinhou_em=%s studs  clipes=%s" % (th, D, r["erro_final_graus"], r["passou_do_rumo_graus"], r["andou_ate_alinhar"], " ".join(c.replace("Esquerda", "E").replace("Direita", "D") for c in r["clipes"][:8])))
    json.dump(R, open("review/v46_curvas/sim_controle_r11.json", "w"), indent=1)
