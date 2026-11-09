"""Folha de quadros de um clipe (para revisao sem player): N quadros igualmente espacados da pasta videos/_q_<clipe>,
vistas escolhidas (0 lateral, 1 frontal, 2 tres_quartos), com o numero do quadro. Uso: python folha.py <clipe> [N] [vistas] [ciclo_quadros]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
nome = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 8; vistas = [int(c) for c in (sys.argv[3] if len(sys.argv) > 3 else "02")]
ciclo = int(sys.argv[4]) if len(sys.argv) > 4 else None
pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos", "_q_" + nome)
arq = sorted(f for f in os.listdir(pasta) if f.startswith("m_"))
if ciclo: arq = arq[:ciclo]
idx = [round(i * (len(arq) - 1) / max(1, N - 1)) for i in range(N)] if not ciclo else [round(i * len(arq) / N) for i in range(N)]
try: fonte = ImageFont.truetype("arial.ttf", 20)
except Exception: fonte = ImageFont.load_default()
tiles = []
for i in idx:
    im = Image.open(os.path.join(pasta, arq[i])); w = im.width // 3
    for v in vistas:
        t = im.crop((v * w, 0, (v + 1) * w, im.height)); d = ImageDraw.Draw(t); d.text((8, 6), "%s q%d" % (nome, i), fill=(255, 255, 255), font=fonte); tiles.append(t)
cols = len(vistas) * 2 if len(vistas) <= 2 else len(vistas)
rows = (len(tiles) + cols - 1) // cols
out = Image.new("RGB", (cols * tiles[0].width, rows * tiles[0].height))
for k, t in enumerate(tiles): out.paste(t, ((k % cols) * t.width, (k // cols) * t.height))
dest = os.path.join(os.path.dirname(pasta), "Folha_%s.png" % nome); out.save(dest); print(dest)
