"""Prancha de revisao: referencia x render na mesma vista (topo) + frente, lado, tras, 3/4 e cabeca (baixo).
Uso: python prancha.py <pasta_da_rodada> [titulo]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

pasta = os.path.abspath(sys.argv[1]); titulo = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(pasta)
aqui = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(aqui, "ref", "lobo-ancestral-referencia.png")).convert("RGB")
def vista(n): return Image.open(os.path.join(pasta, "vista_%s.png" % n)).convert("RGB")
W = 2400; meia = W // 2
try: fonte = ImageFont.truetype("arial.ttf", 30)
except Exception: fonte = ImageFont.load_default()
def caber(im, w): return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
topo = [caber(ref, meia), caber(vista("referencia"), meia)]
h1 = max(i.height for i in topo)
baixo = [caber(vista(n), W // 3) for n in ("frente", "lado", "tras", "tres_quartos", "cabeca")]
h2 = baixo[0].height
out = Image.new("RGB", (W, 60 + h1 + 2 * h2), (24, 24, 24)); d = ImageDraw.Draw(out)
d.text((20, 14), "Lobo Ancestral - %s   (esq.: referencia | dir.: modelo, mesma vista aproximada)" % titulo, fill=(235, 235, 235), font=fonte)
out.paste(topo[0], (0, 60)); out.paste(topo[1], (meia, 60))
rot = ["frente", "lado", "tras", "tres quartos", "cabeca"]
for i, im in enumerate(baixo):
    x, y = (i % 3) * (W // 3), 60 + h1 + (i // 3) * h2
    out.paste(im, (x, y)); d.text((x + 14, y + 10), rot[i], fill=(255, 255, 255), font=fonte)
destino = os.path.join(pasta, "Prancha_%s.png" % os.path.basename(pasta)); out.save(destino); print(destino)
