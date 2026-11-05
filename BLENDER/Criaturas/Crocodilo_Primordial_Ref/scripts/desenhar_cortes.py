"""Desenha o JSON de cortes_boca.py. Uso: python desenhar_cortes.py <base> (le <base>.json, grava <base>)"""
import sys, json
from PIL import Image, ImageDraw, ImageFont
base = sys.argv[1]; d = json.load(open(base + ".json")); f = ImageFont.truetype("arial.ttf", 20)
W, H, S = 520, 420, 150
ks = list(d); g = Image.new("RGB", (W * min(4, len(ks)), H * ((len(ks) + 3) // 4)), (250, 250, 250)); dr = ImageDraw.Draw(g)
for i, k in enumerate(ks):
    ox, oy = (i % 4) * W, (i // 4) * H
    dr.rectangle([ox, oy, ox + W - 2, oy + H - 2], outline=(180, 180, 180)); dr.text((ox + 8, oy + 6), "y = %s" % k, fill=(0, 0, 0), font=f)
    for (x1, z1, w1), (x2, z2, w2) in d[k]:
        wm = (w1 + w2) / 2; cor = (int(255 * wm), 40, int(255 * (1 - wm)))
        dr.line([ox + W / 2 + x1 * S, oy + H - 20 - (z1 - 1.6) * S, ox + W / 2 + x2 * S, oy + H - 20 - (z2 - 1.6) * S], fill=cor, width=2)
g.save(base); print("OK", base)
