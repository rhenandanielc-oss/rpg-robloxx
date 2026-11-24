"""Prancha LOCAL da simulacao r3 (vista de cima + faixa do nivel da alcateia) para 4 cenarios. NAO e captura do Roblox.
Uso: python prancha_ameaca_r3.py -> review/rpg_ia_r3/prancha_simulacao_r3.png"""
import os, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
aqui = os.path.dirname(os.path.abspath(__file__))
g = {"__name__": "prancha", "__file__": os.path.join(aqui, "simular_ameaca_r3.py")}
try: exec(open(g["__file__"], encoding="utf-8").read(), g)
except SystemExit: pass
CEN = {c[0]: c for c in g["CEN_EXPORT"]}
escolha = ["3 recua antes do ataque", "4 insiste depois do aviso", "2 para na zona de aviso (25) 30 s", "7 dois jogadores: so B agride"]
COR = {"Calmo": "#9aa5b1", "Atencao": "#e0b341", "Ameaca": "#e07b29", "Defesa": "#c8372d"}
fig, eixos = plt.subplots(2, 4, figsize=(20, 9), gridspec_kw={"height_ratios": [4, 1]})
for k, nome in enumerate(escolha):
    c = CEN[nome]; tr = []
    T = c[2] if len(c) > 2 else 40
    r = g["cenario"](nome, c[1], T, c[3] if len(c) > 3 else (lambda t, u: True), trace=tr)
    ax = eixos[0][k]; A = g["A"]
    for raio, rot, cor in ((A["raioAtencao"], "Atencao 48", "#e0b341"), (A["raioAviso"], "Aviso 34", "#e07b29"), (A["raioCritico"], "Critica 20", "#c8372d")):
        ax.add_patch(Circle((0, 0), raio, fill=False, ls="--", lw=1, color=cor)); ax.text(0, raio + 1, rot, ha="center", fontsize=8, color=cor)
    ax.plot(0, 0, marker="*", ms=14, color="#5aa0d8"); ax.text(1.5, -2.5, "ovo/abrigo", fontsize=8)
    for i, cor in enumerate(("#1f4e79", "#2e7d32", "#6a1b9a")):
        xs = [x[2][i][0][0] for x in tr]; ys = [x[2][i][0][1] for x in tr]
        ax.plot(xs, ys, color=cor, lw=1.6, label=("Lider", "Membro", "Guardiao 0,85")[i])
        p, fr, e = tr[-1][2][i]
        ax.annotate("", xy=(p[0] + fr[0] * 6.2 * e, p[1] + fr[1] * 6.2 * e), xytext=p, arrowprops=dict(arrowstyle="->", color=cor, lw=2))
    for u, cor in (("A", "#111111"), ("B", "#888888")):
        pts = [(x[0], x[1], x[3][u]) for x in tr if u in x[3]]
        if not pts: continue
        for (t0, n0, p0), (t1, n1, p1) in zip(pts, pts[1:]):
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=COR[n1], lw=3 if u == "A" else 2, solid_capstyle="round")
        ax.plot(*pts[0][2], "o", color=cor); ax.text(pts[0][2][0] + 1, pts[0][2][1], "jogador " + u, fontsize=8)
    ax.set_xlim(-45, 45); ax.set_ylim(-20, 75); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title(nome + "\n(cor do trajeto do jogador = nivel da alcateia)", fontsize=10)
    if k == 0: ax.legend(fontsize=8, loc="lower left")
    b = eixos[1][k]
    for (t0, n0, *_), (t1, *_r) in zip(tr, tr[1:]): b.axvspan(t0, t1, color=COR[n0], lw=0)
    b.set_yticks([]); b.set_xlabel("s"); b.set_xlim(0, tr[-1][0])
    b.set_title("aviso antes da defesa: %s s | menor focinho->jogador antes da defesa: %s | acertos: %d" % (
        r["aviso_antes_da_defesa_s"], r["dF_min_antes_defesa"], r["acertos"]), fontsize=8)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=v, label=k) for k, v in COR.items()], loc="lower center", ncol=4, fontsize=9)
fig.suptitle("IA Lobo Artico r3 - SIMULACAO LOCAL 2D (nao e o Roblox): Atencao -> Ameaca -> Defesa/Desengajar  [numeros PROPOSTA, A TESTAR]", fontsize=13)
saida = os.path.normpath(os.path.join(aqui, "..", "..", "review", "rpg_ia_r3")); os.makedirs(saida, exist_ok=True)
fig.tight_layout(rect=(0, 0.04, 1, 0.95)); fig.savefig(os.path.join(saida, "prancha_simulacao_r3.png"), dpi=90)
print(os.path.join(saida, "prancha_simulacao_r3.png"))
