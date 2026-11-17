"""Prancha de revisao do kit v42: uma linha por acao (perfil E e 3/4), quadros de review/v42_kit/quadros.
Uso: python prancha_kit_v42.py (nesta pasta)"""
import os, re
from PIL import Image, ImageDraw
Q = "review/v42_kit/quadros"; O = "review/v42_kit/revisao"; os.makedirs(O, exist_ok=True)
ACS = ["CometaPreparar", "CometaVoo", "CometaPouso", "AvalancheCorrida", "AvalancheOnda"]
w, h = 240, 180
for vista in ("perfil_E", "34_E", "frente"):
    lin = []
    for ac in ACS:
        qs = sorted(int(m.group(1)) for f in os.listdir(Q) for m in [re.match(r"LOW_%s_%s_q(\d+)\.png" % (ac, vista), f)] if m); lin.append((ac, qs))
    nc = max(len(q) for _, q in lin); img = Image.new("RGB", (120 + nc * (w + 3), len(lin) * (h + 3) + 22), (40, 40, 40)); d = ImageDraw.Draw(img)
    d.text((6, 4), "Kit v42 - %s (30 q/s)" % vista, fill=(255, 235, 120))
    for r, (ac, qs) in enumerate(lin):
        y = 22 + r * (h + 3); d.text((4, y + h // 2), ac, fill=(255, 235, 120))
        for c, q in enumerate(qs):
            s = Image.open(os.path.join(Q, "LOW_%s_%s_q%04d.png" % (ac, vista, q))).convert("RGB"); s.thumbnail((w, h)); img.paste(s, (120 + c * (w + 3), y))
            d.text((122 + c * (w + 3), y + 2), "q%d %.2fs" % (q, q / 30), fill=(255, 255, 255))
    img.save(os.path.join(O, "kit_v42_%s.png" % vista))
print("PRANCHA_KIT_V42_OK")
