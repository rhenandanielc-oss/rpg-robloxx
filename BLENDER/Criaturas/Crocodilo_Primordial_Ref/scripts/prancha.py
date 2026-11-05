"""Prancha de revisao: referencia x render na camera equivalente (linha 1) + vistas extras (linha 2).
Uso: python prancha.py <referencia.png> <render_ref.png> <saida.png> [extra1.png extra2.png ...] [--titulo "texto"]"""
import sys
from PIL import Image, ImageDraw, ImageFont
a = sys.argv[1:]
titulo = ""
if "--titulo" in a:
    i = a.index("--titulo"); titulo = a[i + 1]; a = a[:i] + a[i + 2:]
ref, ren, out, extras = a[0], a[1], a[2], a[3:]
W = 1672 // 2; H = 941 // 2
def abre(p, w, h):
    im = Image.open(p).convert("RGB"); im.thumbnail((w, h)); fundo = Image.new("RGB", (w, h), (90, 90, 92))
    fundo.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return fundo
try: fonte = ImageFont.truetype("arial.ttf", 22)
except Exception: fonte = ImageFont.load_default()
linhas2 = (len(extras) + 2) // 3
alt = 40 + H + linhas2 * (H * 2 // 3 + 10)
pr = Image.new("RGB", (W * 2 + 10, alt), (30, 30, 32)); d = ImageDraw.Draw(pr)
d.text((10, 8), titulo, fill=(235, 235, 235), font=fonte)
pr.paste(abre(ref, W, H), (0, 40)); pr.paste(abre(ren, W, H), (W + 10, 40))
d.text((10, 44), "REFERENCIA", fill=(255, 220, 120), font=fonte); d.text((W + 20, 44), "MODELO", fill=(255, 220, 120), font=fonte)
w3 = (W * 2 + 10 - 20) // 3; h3 = H * 2 // 3
for k, p in enumerate(extras):
    x = (k % 3) * (w3 + 10); y = 40 + H + 10 + (k // 3) * (h3 + 10)
    pr.paste(abre(p, w3, h3), (x, y))
    d.text((x + 6, y + 4), p.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0], fill=(255, 220, 120), font=fonte)
pr.save(out); print("PRANCHA", out, pr.size)
