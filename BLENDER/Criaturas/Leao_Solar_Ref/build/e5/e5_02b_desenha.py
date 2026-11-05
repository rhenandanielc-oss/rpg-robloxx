"""desenha os cortes de e5_02 (python do sistema): python e5_02b_desenha.py <saida.png> <a.json> [b.json]"""
import sys, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = [json.load(open(f)) for f in sys.argv[2:]]; zs = list(D[0]["cortes"].keys())
fig, axs = plt.subplots(len(D), len(zs), figsize=(4 * len(zs), 4.6 * len(D)), squeeze=False)
for r, d in enumerate(D):
    for c, z in enumerate(zs):
        ax = axs[r][c]
        for a, b in d["cortes"][z]: ax.plot([a[0], b[0]], [a[1], b[1]], "k-", lw=0.5)
        ax.set_title(f"{d['obj']}  {"xyz"[d.get("eixo", 2)]}={z}", fontsize=9); ax.set_aspect("equal"); (ax.set_xlim(-4.5, 4.5), ax.set_ylim(-3.5, -13)) if d.get("eixo", 2) == 2 else (ax.set_xlim(-12, -4), ax.set_ylim(0, 9)); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=60)
