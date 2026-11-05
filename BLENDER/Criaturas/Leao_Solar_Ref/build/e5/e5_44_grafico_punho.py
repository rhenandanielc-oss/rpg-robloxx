"""Graficos e tabela dos angulos da pata de golpe (antes x depois) a partir dos JSON do e5_40. Uso: python e5_44_grafico_punho.py <antes.json> <depois.json> <saida.png> <saida.txt> [acao_unica, ex. Leao_Bote: DD e DE da mesma acao]"""
import sys, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
a, d = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
UNICA = sys.argv[5] if len(sys.argv) > 5 else None
def acao(lado): return UNICA or "Leao_Patada_" + lado
LIN = [("Mao", "flexao", "Punho (Mao rel. antebraco): flexao, graus"), ("Mao", "torcao", "Punho: torcao em volta do osso, graus"),
       ("Mao", "salto", "Punho: variacao entre quadros, graus"), ("Antebraco", "flexao", "Cotovelo (antebraco rel. umero): flexao, graus"),
       ("Umero", "salto", "Ombro (umero): variacao entre quadros, graus")]
fig, ax = plt.subplots(len(LIN), 2, figsize=(14, 15), sharex=True); txt = []
for j, (lado, pe) in enumerate((("D", "DD"), ("E", "DE"))):
    for i, (o, k, tit) in enumerate(LIN):
        for nome, dados, cor in (("antes (v1)", a, "#c0504d"), ("depois (r2)", d, "#1f6fb4")):
            L = dados[acao(lado)][pe]; ax[i][j].plot([x["f"] for x in L], [x["%s_%s" % (o, pe)][k] or 0 for x in L], color=cor, label=nome, lw=1.8)
        ax[i][j].set_title("%s %s - %s" % (acao(lado).replace("Leao_", ""), pe, tit), fontsize=10); ax[i][j].grid(alpha=0.3)
    ax[0][j].legend(); ax[-1][j].set_xlabel("quadro (30 qps)")
    for nome, dados in (("antes", a), ("depois", d)):
        L = dados[acao(lado)][pe]; m = lambda o, k: max(abs(x["%s_%s" % (o, pe)][k] or 0) for x in L)
        sup = [x for x in dados[acao(lado)] if x != pe]
        txt.append("%s %s %-6s | punho flexao max %5.1f | punho torcao max %5.1f | punho salto max %5.1f/q | cotovelo flexao max %5.1f | cotovelo salto max %5.1f/q | umero salto max %5.1f/q | Punho_Aux torcao max %5.1f" % (
            acao(lado).replace("Leao_", ""), pe, nome, m("Mao", "flexao"), m("Mao", "torcao"), m("Mao", "salto"), m("Antebraco", "flexao"), m("Antebraco", "salto"), m("Umero", "salto"), m("Punho_Aux", "torcao")))
fig.suptitle("Leao Solar - " + (UNICA or "Patada").replace("Leao_", "") + ": angulos da pata dianteira, antes x depois (Blender; numeros nao provam naturalidade, so continuidade)", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(sys.argv[3], dpi=90); open(sys.argv[4], "w", encoding="utf-8").write("\n".join(txt) + "\n"); print("\n".join(txt))
