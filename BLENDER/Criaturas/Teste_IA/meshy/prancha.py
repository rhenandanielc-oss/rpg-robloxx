"""Junta renders do render_clipes.py numa prancha (linhas = clipes/quadros, colunas = vistas).
Uso: python prancha.py pasta_renders saida.png Clipe1:0,1 Clipe2:1 ... [--vistas lado,34,frente]"""
import sys, os
from PIL import Image, ImageDraw
pasta, saida = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
vistas = ["lado", "34", "frente", "baixo", "tras"]
if "--vistas" in args:
    i = args.index("--vistas"); vistas = args[i + 1].split(","); args = args[:i] + args[i + 2:]
linhas = []
for a in args:
    nome, qs = (a.split(":") + ["0"])[:2]
    for q in qs.split(","): linhas.append((nome, int(q)))
W, H = 320, 240
img = Image.new("RGB", (W * len(vistas), H * len(linhas)), (30, 30, 30))
d = ImageDraw.Draw(img)
for r, (nome, q) in enumerate(linhas):
    for c, v in enumerate(vistas):
        f = os.path.join(pasta, "%s_%d_%s.png" % (nome, q, v))
        if os.path.exists(f): img.paste(Image.open(f).convert("RGB").resize((W, H)), (c * W, r * H))
        d.text((c * W + 4, r * H + 4), "%s q%d %s" % (nome, q, v), fill=(255, 255, 0))
img.save(saida); print("PRANCHA", saida, img.size)
