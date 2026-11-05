"""Grade 4 estados x 3 cameras. Uso: python grade_estados.py <dir> <prefixo> <saida> [titulo]"""
import sys
from PIL import Image, ImageDraw, ImageFont
d, pre, out = sys.argv[1:4]; tit = sys.argv[4] if len(sys.argv) > 4 else pre
f = ImageFont.truetype("arial.ttf", 20); W, H = 560, 315
g = Image.new("RGB", (3 * W, 4 * H + 36), (30, 30, 32)); dr = ImageDraw.Draw(g); dr.text((8, 8), tit, fill=(255, 220, 120), font=f)
for i, e in enumerate(("fechada", "meia", "repouso", "aberta")):
    for j, c in enumerate(("E", "D", "frente")):
        im = Image.open("%s/%s_%s_%s.png" % (d, pre, e, c)).convert("RGB").resize((W, H)); g.paste(im, (j * W, 36 + i * H))
        dr.text((j * W + 6, 36 + i * H + 4), "%s - %s" % (e, c), fill=(255, 220, 120), font=f)
g.save(out); print("GRADE", out)
