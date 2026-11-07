"""Desenha os cortes de corte_sela.py. Uso: python sela/desenhar_cortes.py <cortes.json> <saida.png> [titulo]"""
import json, sys
from PIL import Image, ImageDraw
D = json.load(open(sys.argv[1])); W, H = 520, 400; n = len(D["cortes"])
img = Image.new("RGB", (W * n, H + 40), (28, 28, 30)); d = ImageDraw.Draw(img)
COR = {"M_Sela_couro": (205, 130, 75), "M_Sela_metal": (110, 170, 255), "M_Sela_madeira": (235, 205, 95), "M_Sela_adorno": (220, 90, 255)}
for k, c in enumerate(D["cortes"]):
    topo = [max(z1, z2) for x1, z1, x2, z2, t in c["corpo"] if t == 0 and abs(x1) < 0.03]
    zc = max(topo) if topo else 0.45
    esc = W / 0.40; ox = k * W + W / 2
    tx = lambda x, z: (ox + x * esc, H * 0.30 - (z - zc) * esc)
    for x1, z1, x2, z2, t in c["corpo"]: d.line([tx(x1, z1), tx(x2, z2)], fill=(160, 160, 165) if t == 0 else (255, 140, 40), width=2)
    for x1, z1, x2, z2, t in c["sela"]: d.line([tx(x1, z1), tx(x2, z2)], fill=COR.get(D["mats"][t], (255, 255, 255)), width=2)
    d.text((k * W + 8, H + 6), "y %+.3f do centro da sela" % (c["y"] - D["y0"]), fill=(255, 255, 255))
d.text((8, H + 22), (sys.argv[3] if len(sys.argv) > 3 else "") + "  cinza = corpo | laranja = outras ilhas (asa, espinhos) | marrom = couro | amarelo = madeira | azul = metal", fill=(200, 200, 200))
img.save(sys.argv[2]); print("PNG_OK", sys.argv[2])
