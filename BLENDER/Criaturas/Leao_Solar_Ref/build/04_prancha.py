"""Prancha referencia x modelo: por vista (perfil, frente, traseira) a referencia, o render do modelo na mesma escala
e a sobreposicao das silhuetas (cinza = ambos, vermelho = so referencia, azul = so modelo) com IoU; mais o 3/4.
Uso: python 04_prancha.py <ref.png> <ref_dir> <render_dir> <saida.png> [titulo]"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
REF, RDIR, VDIR, SAIDA = sys.argv[1:5]; TIT = sys.argv[5] if len(sys.argv) > 5 else ""
ref = Image.open(REF).convert("RGB"); FUNDO = (220, 213, 207)
CORTES = {"lado": (0, 0, 1217, 594), "frente": (0, 610, 608, 1293), "tras": (609, 610, 1217, 1293)}
MASC = {"lado": "lado", "frente": "frente", "tras": "tras"}
try: fonte = ImageFont.truetype("arial.ttf", 22); fp = ImageFont.truetype("arial.ttf", 17)
except OSError: fonte = fp = ImageFont.load_default()
linhas, metricas = [], {}
for v, (x0, y0, x1, y1) in CORTES.items():
    r = ref.crop((x0, y0, x1, y1))
    mod = Image.open(os.path.join(VDIR, v + ".png")).convert("RGBA")
    m_mod = np.asarray(mod)[..., 3] > 127
    m_ref = np.load(os.path.join(RDIR, MASC[v] + ".npy"))[y0:y1, x0:x1] if v == "lado" else \
        (np.asarray(Image.open(os.path.join(RDIR, "mascara_total.png")))[y0:y1, x0:x1] > 127)
    inter = (m_mod & m_ref).sum(); uni = (m_mod | m_ref).sum(); iou = inter / max(uni, 1); metricas[v] = round(float(iou), 3)
    fundo = Image.new("RGBA", mod.size, FUNDO + (255,)); fundo.alpha_composite(mod)
    sob = np.zeros(m_mod.shape + (3,), np.uint8) + 40
    sob[m_mod & m_ref] = (150, 150, 150); sob[m_ref & ~m_mod] = (220, 60, 60); sob[m_mod & ~m_ref] = (60, 110, 230)
    linhas.append((v, r, fundo.convert("RGB"), Image.fromarray(sob), iou))
tq = Image.open(os.path.join(VDIR, "tres_quartos.png")).convert("RGBA")
f3 = Image.new("RGBA", tq.size, FUNDO + (255,)); f3.alpha_composite(tq)
NOMES = {"lado": "Perfil", "frente": "Frente", "tras": "Traseira"}
LW = 1217 * 3 + 80; topo = 60
alt = topo + sum(l[1].height + 50 for l in linhas) + f3.height + 60
P = Image.new("RGB", (LW, alt), (30, 30, 34)); d = ImageDraw.Draw(P)
d.text((20, 15), TIT, fill=(240, 220, 160), font=fonte)
y = topo
for v, r, m, s, iou in linhas:
    d.text((20, y), f"{NOMES[v]} - referencia | modelo (mesma escala) | silhuetas: cinza=ambos, vermelho=so ref, azul=so modelo   IoU {iou:.3f}",
           fill=(230, 230, 230), font=fp)
    y += 28
    for i, im in enumerate((r, m, s)): P.paste(im, (20 + i * (1217 + 20), y))
    y += r.height + 22
d.text((20, y), "3/4 frontal (perspectiva, luz neutra de estudio)", fill=(230, 230, 230), font=fp); y += 28
P.paste(f3.convert("RGB"), (20, y))
P.save(SAIDA)
json.dump(metricas, open(os.path.splitext(SAIDA)[0] + "_iou.json", "w"))
print("PRANCHA", SAIDA, metricas)
