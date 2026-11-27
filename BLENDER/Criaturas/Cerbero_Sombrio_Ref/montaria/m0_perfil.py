"""M0: perfil lateral (topo e barriga no meio) em pe e deitado, com a zona proposta da sela e um cavaleiro R15 de 5 studs."""
import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d = json.load(open("m0_dorso.json"))
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
for a, k, tit in ((ax[0], "repouso_rest", "Em pe (repouso)"), (ax[1], "deitado_fim", "Deitado (fim do Deitar)")):
    r = d[k]; ys = [p["y"] for p in r["perfil"] if p["topo_x+0.0"]]
    a.plot(ys, [p["topo_x+0.0"] for p in r["perfil"] if p["topo_x+0.0"]], "k-", lw=2, label="topo (meio)")
    yb = [p["y"] for p in r["perfil"] if p["barriga"]]; a.plot(yb, [p["barriga"] for p in r["perfil"] if p["barriga"]], "k--", lw=1, label="barriga")
    a.axvspan(-3.5, 1.0, color="#b03020", alpha=0.18, label="sela (proposta)")
    for n, c in r["ossos"].items():
        if n in ("Coluna3", "PescocoC1", "EscapulaE", "BracoE", "CoxaE"): a.plot(c[1], c[2], "o", ms=4); a.annotate(n, (c[1], c[2]), fontsize=7)
    a.add_patch(plt.Rectangle((-14.5, 0), 1.2, 5, color="#3070c0", alpha=0.6)); a.annotate("cavaleiro 5", (-15, 5.3), fontsize=8)
    a.axhline(0, color="#777", lw=0.8); a.set_title(tit); a.set_xlabel("y (frente = direita)"); a.invert_xaxis(); a.grid(alpha=0.3)
    a.set_xlim(13, -16)
ax[0].set_ylabel("altura (studs)"); ax[0].legend(fontsize=8, loc="lower left")
plt.tight_layout(); plt.savefig("review_m0/m0_perfil.png", dpi=110)
