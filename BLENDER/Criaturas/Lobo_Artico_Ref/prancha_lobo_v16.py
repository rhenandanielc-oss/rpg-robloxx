"""Prancha do diagnostico v16 (lobo da cauda do lado da perna). Uso: python prancha_lobo_v16.py review/v16_lobo"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.abspath(sys.argv[1]); W, H = 640, 480
try: F = ImageFont.truetype("arial.ttf", 22)
except OSError: F = ImageFont.load_default()
def cel(p, t):
    im = Image.open(os.path.join(D, p)).convert("RGB"); im.thumbnail((W, H)); c = Image.new("RGB", (W, H), (20, 20, 22)); c.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    d = ImageDraw.Draw(c); d.rectangle((0, 0, W, 32), fill=(0, 0, 0)); d.text((8, 5), t, font=F, fill=(255, 255, 255)); return c
L = [[cel("print_usuario.png", "1. print do usuario (v15)"), cel("classe_fresta_E_q0030.png", "2. corte da v10: azul = lado PERNA"), cel("lobo_1.0_E.png", "3. roxo = LOBO DA CAUDA no lado perna")],
     [cel("v15/real_fresta_E_q0033.png", "4. v15 q33: lobo vai com a perna"), cel("v16/cores_fresta_E_q0033.png", "5. v16 (so pesos): lobo segue a cauda..."), cel("v16/real_fresta_E_q0033.png", "6. ...mas a pele do vinco estica (membrana)")]]
o = Image.new("RGB", (3 * W + 8, 2 * H + 4), (40, 40, 40))
for r, l in enumerate(L):
    for c, im in enumerate(l): o.paste(im, (c * (W + 4), r * (H + 4)))
o.save(os.path.join(D, "diagnostico_lobo_v16.png")); print("PRANCHA_LOBO_OK")
