"""Prancha da proposta visual das idades (idades_v1.py). Uso: python prancha_idades_v1.py <pasta dos renders>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1]
N = [("Filhote", "escala 0,40 | cabeca grande, focinho curto, orelhas e patas grandes, cauda curta | pelagem escura (nasce cinza-acastanhado) | sem cristais nem marca"),
     ("Jovem", "escala 0,65 | pernalta e magro, cabeca e patas ainda grandes | cinza claro | cristais pequenos, marca acesa"),
     ("Pre-adulto", "escala 0,85 | quase adulto | quase branco | cristais medios"),
     ("Adulto", "escala 1,00 | base aprovada"),
     ("Anciao", "escala 1,10 | pescoco e juba mais grossos, cabeca mais baixa | marfim/prateado | cristais maiores")]
FT = ImageFont.truetype("arial.ttf", 24); FS = ImageFont.truetype("arial.ttf", 17)
w, h = 440, 314
c = Image.new("RGB", (w * 5, 70 + h * 4), (30, 32, 36)); d = ImageDraw.Draw(c)
d.text((8, 4), "Lobo Artico - proposta visual por idade (prototipo: pose dos ossos + tinta + cristais; linha 1 = tamanho real no jogo)", fill=(255, 235, 140), font=FT)
for i, (n, t) in enumerate(N):
    d.text((i * w + 8, 36), n, fill=(170, 225, 255), font=FT)
    for r, v in enumerate(("fila", "perfil", "34", "cabeca")):
        im = Image.open(os.path.join(D, "%s_%s.png" % (n, v))).convert("RGB").resize((w, h)); c.paste(im, (i * w, 70 + r * h))
    y = 70 + h * 4 - 4
c2 = Image.new("RGB", (c.width, c.height + 5 * 26 + 10), (30, 32, 36)); c2.paste(c, (0, 0)); d2 = ImageDraw.Draw(c2)
for i, (n, t) in enumerate(N): d2.text((10, c.height + 6 + i * 26), "%s: %s" % (n, t), fill=(230, 230, 230), font=FS)
c2.save(os.path.join(D, "prancha_idades.jpg"), quality=88); print("ok")
