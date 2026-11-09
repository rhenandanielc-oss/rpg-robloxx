"""Desenha sobre a vista frontal ortografica (orto_alinhamento, escala 9,5, centro z 4,3) a linha central medida de cada
pata e do peitoral (medir_patas_frontal.json) e a linha dos ossos. Uso: python linhas_patas.py <frente.png> <medidas.json> <saida.png> <titulo>"""
import sys, json
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); J = json.load(open(sys.argv[2])); W, H = im.size; ESC, ZC = 9.5, 4.3
def px(x, z): return ((x / ESC + 0.5) * W, (1 - ((z - ZC) / ESC + 0.5)) * H)
d = ImageDraw.Draw(im)
COR = {"dianE": (40, 230, 255), "dianD": (255, 200, 40), "peito": (80, 255, 90), "trasE": (40, 120, 255), "trasD": (255, 120, 40)}
for nome, cor in COR.items():
    pts = [px(c, z) for z, c, a, b, n in J[nome] if nome.startswith("dian") or nome == "peito" or z < 3.0]
    if len(pts) > 1: d.line(pts, fill=cor, width=3)
O = J["ossos"]
for s in ("E", "D"):
    d.line([px(O["Dedos" + s][0], O["Dedos" + s][2]), px(O["Mao" + s][0], O["Mao" + s][2]), px(O["Antebraco" + s][0], O["Antebraco" + s][2]), px(O["Braco" + s][0], O["Braco" + s][2])], fill=(255, 255, 255), width=1)
try: f = ImageFont.truetype("arial.ttf", 18)
except Exception: f = ImageFont.load_default()
d.text((10, 10), sys.argv[4], fill=(255, 255, 255), font=f)
d.text((10, H - 30), "ciano/amarelo: centro da pata dianteira E/D | verde: peitoral | branco: ossos", fill=(255, 255, 255), font=f)
im.save(sys.argv[3])
