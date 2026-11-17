"""Prancha do ataque basico v43: uma prancha por vista; linhas = ataque x base (Repouso/Andar/Corrida), colunas = quadros.
Uso: python prancha_ataque_v43.py (nesta pasta)"""
import os, re
from PIL import Image, ImageDraw
Q = "review/v43_ataque/quadros"; O = "review/v43_ataque/revisao"; os.makedirs(O, exist_ok=True)
ATS = ["Mordida1", "Mordida2", "GarraE", "GarraD"]; BASES = ["Repouso", "Andar", "Corrida"]
CONT = {"Mordida1": 6, "Mordida2": 6, "GarraE": 7, "GarraD": 7}
w, h = 230, 158
for vista in ("perfil_E", "34_E"):
    fs = os.listdir(Q)
    if not any(vista in f for f in fs): continue
    for at in ATS:
        lin = []
        for b in BASES:
            qs = sorted(int(m.group(1)) for f in fs for m in [re.match(r"%s_%s_%s_q(\d+)\.png" % (at, b, vista), f)] if m); lin.append((b, qs))
        nc = max(len(q) for _, q in lin); img = Image.new("RGB", (90 + nc * (w + 3), len(lin) * (h + 3) + 22), (40, 40, 40)); d = ImageDraw.Draw(img)
        d.text((6, 4), "Ataque basico v43 - %s sobre a locomocao - %s (30 q/s; CONTATO em q%d)" % (at, vista, CONT[at]), fill=(255, 235, 120))
        for r, (b, qs) in enumerate(lin):
            y = 22 + r * (h + 3); d.text((4, y + h // 2), b, fill=(255, 235, 120))
            for c, q in enumerate(qs):
                s = Image.open(os.path.join(Q, "%s_%s_%s_q%02d.png" % (at, b, vista, q))).convert("RGB"); s.thumbnail((w, h)); x = 90 + c * (w + 3); img.paste(s, (x, y))
                d.text((x + 2, y + 2), "q%d %.2fs" % (q, q / 30), fill=(255, 80, 80) if q == CONT[at] else (255, 255, 255))
        img.save(os.path.join(O, "ataque_v43_%s_%s.jpg" % (at, vista)), quality=88)
print("PRANCHA_ATAQUE_V43_OK")
