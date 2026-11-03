"""Monta os GIFs da simulacao de deslocamento (render_deslocamento.py) com rotulo obrigatorio e o grafico das patas no mundo.
Normal (30 qps) e lento (1/3) lado a lado. Grafico: trajeto visto de cima e deriva de cada apoio (pata parada no chao).
Uso: python gif_deslocamento.py <dir_render> <saida_dir> [rotulo_extra]"""
import sys, os, glob, csv, math
from PIL import Image, ImageDraw
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d, out = sys.argv[1], sys.argv[2]; extra = sys.argv[3] if len(sys.argv) > 3 else ""; os.makedirs(out, exist_ok=True)
ROT = "SIMULACAO no Blender - v e giro sao parametros tecnicos desta revisao, nao regras do jogo; Roblox pendente"
CORES = {"MaoE": "#d93636", "MaoD": "#e0b01a", "PeE": "#3a6fe0", "PeD": "#36b05a"}
for pasta in sorted(glob.glob(os.path.join(d, "video", "*"))):
    nome = os.path.basename(pasta); qs = [Image.open(p).convert("RGB") for p in sorted(glob.glob(os.path.join(pasta, "*.png")))]
    if not qs: continue
    W, H = qs[0].size; n = len(qs); quadros = []
    for k in range(n * 3):
        o = Image.new("RGB", (W * 2, H + 36), (20, 20, 20)); o.paste(qs[k % n], (0, 36)); o.paste(qs[(k // 3) % n], (W, 36))
        dr = ImageDraw.Draw(o); dr.text((6, 3), ROT, fill=(255, 220, 80))
        dr.text((6, 20), "%s %s - normal" % (nome, extra), fill=(255, 255, 255)); dr.text((W + 6, 20), "%s %s - lento (1/3)" % (nome, extra), fill=(255, 255, 255))
        quadros.append(o.quantize(colors=128))
    quadros[0].save(os.path.join(out, "Desloc_%s%s.gif" % (nome, ("_" + extra) if extra else "")), save_all=True, append_images=quadros[1:], duration=33, loop=0, optimize=True)
    # grafico
    f = os.path.join(d, nome + "_patas.csv")
    if not os.path.exists(f): continue
    linhas = list(csv.DictReader(open(f, encoding="utf-8")))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
    for pata, cor in CORES.items():
        L = [r for r in linhas if r["pata"] == pata]
        xs = [float(r["x"]) for r in L]; ys = [float(r["y"]) for r in L]
        a1.plot(xs, ys, color=cor, lw=0.8, alpha=0.5)
        a1.scatter([float(r["x"]) for r in L if r["apoio"] == "1"], [float(r["y"]) for r in L if r["apoio"] == "1"], s=6, color=cor, label=pata)
        ini = None; tt = []; dd = []
        for r in L:
            if r["apoio"] == "1":
                p = (float(r["x"]), float(r["y"]))
                if ini is None: ini = p
                tt.append(float(r["t"])); dd.append(math.hypot(p[0] - ini[0], p[1] - ini[1]))
            else:
                if tt: a2.plot(tt, dd, color=cor, lw=1.6); tt, dd = [], []
                ini = None
        if tt: a2.plot(tt, dd, color=cor, lw=1.6)
    a1.set_aspect("equal"); a1.set_title("Patas no mundo (vista de cima); pontos = apoio"); a1.set_xlabel("x (studs)"); a1.set_ylabel("y (studs)"); a1.legend(fontsize=8)
    a2.axhline(0.05, color="#888", ls="--", lw=0.8); a2.text(0, 0.052, "tolerancia proposta 0,05 (Andar/Virar)", fontsize=7, color="#666")
    a2.set_title("Deriva do osso da pata durante cada apoio"); a2.set_xlabel("tempo (s)"); a2.set_ylabel("deriva (studs)"); a2.set_ylim(0, max(0.12, a2.get_ylim()[1]))
    fig.suptitle("%s %s - %s" % (nome, extra, ROT), fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(out, "Grafico_%s%s.png" % (nome, ("_" + extra) if extra else "")), dpi=110); plt.close(fig)
    print("GIF_DESLOC", nome, n)
