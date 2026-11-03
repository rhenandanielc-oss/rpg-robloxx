"""Desenha os ossos (ossos_2d.json do diagrama_ossos.py) sobre os renders. Uso: python desenhar_ossos.py <dir>"""
import sys, os, json
from PIL import Image, ImageDraw
d_ = sys.argv[1]; dados = json.load(open(os.path.join(d_, "ossos_2d.json")))
for nome, ossos in dados.items():
    p = os.path.join(d_, nome + ".png"); im = Image.open(p).convert("RGB"); d = ImageDraw.Draw(im)
    for bn, h, t in ossos:
        cor = (255, 200, 40) if bn.endswith("E") else ((80, 200, 255) if bn.endswith("D") else (255, 90, 90))
        d.line([tuple(h), tuple(t)], fill=cor, width=4); d.ellipse((h[0] - 5, h[1] - 5, h[0] + 5, h[1] + 5), fill=cor)
        if (nome == "ossos_perfil" and not bn.endswith("D")) or (nome == "ossos_frente" and not bn.endswith("E")):
            d.text(((h[0] + t[0]) / 2 + 6, (h[1] + t[1]) / 2 - 6), bn, fill=(255, 255, 255))
    im.save(p)
print("OK")
