"""Prancha em grade com rotulo em cada quadro (Lote 5).
Uso: python grade.py <saida.png> <colunas> "<titulo>" <imagem>=<rotulo> [<imagem>=<rotulo> ...]"""
import sys
from PIL import Image, ImageDraw, ImageFont
out, cols, titulo = sys.argv[1], int(sys.argv[2]), sys.argv[3]
itens = [a.split("=", 1) for a in sys.argv[4:]]
W, H = 640, 400
try: fonte = ImageFont.truetype("arial.ttf", 20); ft = ImageFont.truetype("arial.ttf", 24)
except Exception: fonte = ft = ImageFont.load_default()
lin = (len(itens) + cols - 1) // cols
pr = Image.new("RGB", (cols * W + (cols - 1) * 8, 44 + lin * (H + 8)), (30, 30, 32)); d = ImageDraw.Draw(pr)
d.text((10, 9), titulo, fill=(240, 240, 240), font=ft)
for k, (p, rot) in enumerate(itens):
    im = Image.open(p).convert("RGB"); im.thumbnail((W, H)); q = Image.new("RGB", (W, H), (80, 80, 82))
    q.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    dq = ImageDraw.Draw(q); dq.rectangle((0, 0, 8 + 11 * len(rot), 28), fill=(20, 20, 22)); dq.text((5, 3), rot, fill=(255, 230, 150), font=fonte)
    pr.paste(q, ((k % cols) * (W + 8), 44 + (k // cols) * (H + 8)))
pr.save(out); print("GRADE_OK", out, pr.size)
